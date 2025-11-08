"""Main entry point for the AnyTask CLI."""

import asyncio
import sys
import typer
from typing_extensions import Annotated
from rich.console import Console

from cli.utils.errors import install_traceback_handler, handle_api_error
from cli.commands import workspace as workspace_commands
from cli.commands import project as project_commands
from cli.commands import task as task_commands
from cli.commands import ai as ai_commands
from cli.commands import init as init_command
from cli.commands import template as template_commands
from cli.commands import label as label_commands
from cli.commands import view as view_commands
from cli.commands import preference as preference_commands
from cli.commands import health as health_commands
from cli.commands import worker as worker_commands
from cli.commands import comment as comment_commands
from cli.commands import attempt as attempt_commands
from cli.commands import artifact as artifact_commands
from cli.commands.board.commands import (
    show_board,
    show_timeline,
    show_summary,
    show_graph,
)
from cli.config import ActiveTaskConfig, WorkspaceConfig, get_effective_api_config
from cli.client.tasks import TasksAPIClient
import os


def is_dev_environment() -> bool:
    """Check if --dev flag was passed to init or if ANYT_API_URL points to localhost."""
    api_url = os.getenv("ANYT_API_URL", "")
    return "localhost" in api_url or "127.0.0.1" in api_url


app = typer.Typer(
    name="anyt",
    help="AnyTask - AI-native task management from the command line",
    add_completion=False,
)

# Determine if experimental commands should be hidden
IS_DEV = is_dev_environment()

# Register command groups
# Core commands (always visible)
app.add_typer(workspace_commands.app, name="workspace", hidden=not IS_DEV)
app.add_typer(project_commands.app, name="project", hidden=not IS_DEV)
app.add_typer(task_commands.app, name="task")
app.add_typer(template_commands.app, name="template", hidden=not IS_DEV)
app.add_typer(label_commands.app, name="label", hidden=not IS_DEV)
app.add_typer(view_commands.app, name="view", hidden=not IS_DEV)
app.add_typer(preference_commands.app, name="preference", hidden=not IS_DEV)
app.add_typer(ai_commands.app, name="ai", hidden=not IS_DEV)
app.add_typer(health_commands.app, name="health")
app.add_typer(comment_commands.app, name="comment")

# Experimental/advanced commands (hidden in production)
app.add_typer(worker_commands.app, name="worker")
app.add_typer(attempt_commands.app, name="attempt")
app.add_typer(artifact_commands.app, name="artifact")

# Register board visualization commands as top-level commands
app.command("board")(show_board)
app.command("timeline")(show_timeline)
app.command("summary")(show_summary)
app.command("graph")(show_graph)

# Register init command as top-level command
app.command("init")(init_command.init)

console = Console()


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = False,
):
    """AnyTask CLI - Manage tasks, projects, and workflows."""
    if version:
        from cli import __version__

        typer.echo(f"anyt version {__version__}")
        raise typer.Exit()

    # If no command and no version flag, show help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@app.command("active")
def show_active():
    """Show the currently active task."""
    # Check if workspace is initialized
    ws_config = WorkspaceConfig.load()
    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt workspace init[/cyan] first")
        raise typer.Exit(1)

    # Load active task
    active_task = ActiveTaskConfig.load()
    if not active_task:
        console.print("[yellow]No active task[/yellow]")
        console.print("Pick one with: [cyan]anyt task pick[/cyan]")
        raise typer.Exit(0)

    # Check authentication
    try:
        get_effective_api_config()
    except RuntimeError:
        console.print("[red]Error:[/red] Not authenticated")
        console.print("\nSet the ANYT_API_KEY environment variable:")
        console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
        raise typer.Exit(1)

    client = TasksAPIClient.from_config()

    async def fetch_and_display():
        try:
            # Fetch full task details
            task = await client.get_task(active_task.identifier)

            # Display task details
            from cli.commands.task.helpers import (
                format_priority,
                format_relative_time,
            )

            task_id = task.identifier
            title = task.title

            console.print()
            console.print(f"[cyan bold]{task_id}:[/cyan bold] {title}")
            console.print("━" * 60)

            # Status and priority
            status = task.status.value
            priority_val = task.priority
            priority_str = format_priority(priority_val)
            console.print(
                f"Status: [yellow]{status}[/yellow]    Priority: {priority_str} ({priority_val})"
            )

            # Owner and labels
            owner_id = task.owner_id
            if owner_id:
                console.print(f"Owner: {owner_id}")
            else:
                console.print("Owner: [dim]unassigned[/dim]")

            labels_list = task.labels or []
            if labels_list:
                labels_str = ", ".join(labels_list)
                console.print(f"Labels: [blue]{labels_str}[/blue]")

            # Dependencies status (simplified)
            console.print()
            console.print("[dim]Dependencies: (use 'anyt dep list' for details)[/dim]")

            # Timestamps
            console.print()
            updated = (
                format_relative_time(task.updated_at.isoformat())
                if task.updated_at
                else "never"
            )
            console.print(f"Last updated: {updated}")

            # Show when task was picked
            picked_time = format_relative_time(active_task.picked_at)
            console.print(f"Picked: {picked_time}")

            console.print()

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                console.print(
                    f"[red]Error:[/red] Active task '{active_task.identifier}' not found"
                )
                console.print(
                    "It may have been deleted. Clear with: [cyan]rm .anyt/active_task.json[/cyan]"
                )
            else:
                console.print(f"[red]Error:[/red] Failed to fetch task: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch_and_display())


def main():
    """Entry point for the CLI."""
    # Install rich traceback handler if in debug mode
    install_traceback_handler()

    try:
        app()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        console.print("\n[yellow]Cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        # Catch any unhandled exceptions
        handle_api_error(e, "running command")


if __name__ == "__main__":
    main()
