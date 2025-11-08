"""Read commands for tasks (show, share)."""

import asyncio
from typing import Optional

import pyperclip  # type: ignore[import-untyped]
import typer
from rich.markdown import Markdown
from typing_extensions import Annotated

from cli.config import get_effective_api_config
from cli.models.common import Priority, Status
from cli.services.task_service import TaskService
from cli.services.workspace_service import WorkspaceService

from ..helpers import (
    console,
    find_similar_tasks,
    format_priority,
    format_relative_time,
    get_active_task_id,
    normalize_identifier,
    output_json,
    resolve_workspace_context,
    truncate_text,
)


def show_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, t_1Z for UID). Uses active task if not specified."
        ),
    ] = None,
    workspace: Annotated[
        Optional[str],
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace identifier or ID (uses current workspace if not specified)",
        ),
    ] = None,
    show_metadata: Annotated[
        bool,
        typer.Option("--show-metadata", help="Display workflow execution metadata"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Show detailed information about a task.

    Supports both workspace-scoped identifiers (DEV-42) and UIDs (t_1Z).
    """
    # Check authentication
    try:
        get_effective_api_config()
    except RuntimeError:
        console.print("[red]Error:[/red] Not authenticated")
        console.print("\nSet the ANYT_API_KEY environment variable:")
        console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
        raise typer.Exit(1)

    service: TaskService = TaskService.from_config()
    workspace_service: WorkspaceService = WorkspaceService.from_config()

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task show DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task show DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)

    async def fetch() -> None:
        # Initialize normalized_id with the original identifier
        # (will be updated if we go through workspace-scoped path)
        normalized_id = identifier

        try:
            # Check if identifier is a UID (starts with 't_')
            if identifier.startswith("t_"):
                # Use UID endpoint (no workspace context needed)
                task = await service.get_task_by_uid(identifier)
            else:
                # Resolve workspace context for workspace-scoped identifiers
                workspace_id, workspace_identifier = await resolve_workspace_context(
                    workspace, workspace_service
                )

                # Normalize identifier for fuzzy matching with workspace prefix
                normalized_id = normalize_identifier(identifier, workspace_identifier)

                # Fetch task using service
                task = await service.get_task(normalized_id)

            # JSON output mode
            if json_output:
                output_json(task.model_dump(mode="json"))
                return

            # Rich console output mode
            console.print()
            console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
            console.print(f"[dim]UID: {task.uid}[/dim]")
            console.print("━" * 60)

            # Status and priority line
            priority_str = format_priority(
                task.priority.value
                if isinstance(task.priority, Priority)
                else task.priority
            )
            console.print(
                f"Status: [yellow]{task.status.value if isinstance(task.status, Status) else task.status}[/yellow]    "
                f"Priority: {priority_str} ({task.priority.value if isinstance(task.priority, Priority) else task.priority})"
            )

            # Owner and labels
            if task.owner_id:
                console.print(f"Owner: {task.owner_id}")
            else:
                console.print("Owner: [dim]unassigned[/dim]")

            if task.labels:
                labels_str = ", ".join(task.labels)
                console.print(f"Labels: [blue]{labels_str}[/blue]")

            # Project
            console.print(f"Project: {task.project_id}")

            # Estimate
            if task.estimate:
                console.print(f"Estimate: {task.estimate}h")

            # Description
            if task.description:
                console.print()
                console.print("[bold]Description:[/bold]")
                console.print()
                # Render description as markdown
                markdown = Markdown(task.description)
                console.print(markdown)

            # Workflow Execution Metadata (if requested)
            if show_metadata:
                workflow_metadata = await service.get_workflow_metadata(task.identifier)
                if workflow_metadata:
                    console.print()
                    console.print("[bold]Workflow Executions:[/bold]")
                    console.print()
                    for exec_meta in workflow_metadata:
                        # Status with emoji
                        status_emoji = {
                            "success": "✅",
                            "running": "🔄",
                            "failure": "❌",
                            "cancelled": "⏹️",
                        }.get(exec_meta.status, "❓")

                        console.print(
                            f"  {status_emoji} [bold]{exec_meta.workflow_execution_id}[/bold]"
                        )
                        console.print(
                            f"      Workflow: [cyan]{exec_meta.workflow_name}[/cyan]"
                        )
                        console.print(f"      Agent: [dim]{exec_meta.agent_id}[/dim]")
                        console.print(f"      Status: {exec_meta.status}")
                        console.print(f"      Started: {exec_meta.started_at}")

                        if exec_meta.completed_at:
                            console.print(f"      Completed: {exec_meta.completed_at}")

                        if exec_meta.duration_seconds is not None:
                            # Format duration nicely
                            duration = exec_meta.duration_seconds
                            if duration < 60:
                                duration_str = f"{duration:.1f}s"
                            elif duration < 3600:
                                duration_str = f"{duration / 60:.1f}m"
                            else:
                                duration_str = f"{duration / 3600:.1f}h"
                            console.print(f"      Duration: {duration_str}")

                        console.print()

            # Metadata
            console.print()
            created = format_relative_time(task.created_at.isoformat())
            updated = format_relative_time(task.updated_at.isoformat())
            console.print(f"Created: {created}")
            console.print(f"Updated: {updated}")
            console.print(f"Version: {task.version}")
            console.print()

        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg:
                # Resolve workspace for error messages
                try:
                    workspace_id, _ = await resolve_workspace_context(
                        workspace, workspace_service
                    )
                except Exception:
                    workspace_id = None

                # Try to find similar tasks for suggestions
                similar_tasks = []
                if workspace_id:
                    similar_tasks = await find_similar_tasks(
                        service, workspace_id, normalized_id
                    )

                if json_output:
                    output_json(
                        {
                            "error": "NotFoundError",
                            "message": f"Task '{normalized_id}' not found"
                            + (f" in workspace {workspace_id}" if workspace_id else ""),
                            "suggestions": [
                                {
                                    "identifier": t.get("identifier"),
                                    "title": t.get("title"),
                                }
                                for t in similar_tasks
                            ],
                        },
                        success=False,
                    )
                else:
                    workspace_info = (
                        f" in workspace {workspace_id}" if workspace_id else ""
                    )
                    console.print(
                        f"[red]✗ Error:[/red] Task '{normalized_id}' not found{workspace_info}"
                    )

                    if similar_tasks:
                        console.print()
                        console.print("  Did you mean:")
                        for task_dict in similar_tasks:
                            task_id = task_dict.get(
                                "identifier", str(task_dict.get("id", ""))
                            )
                            title = truncate_text(task_dict.get("title", ""), 40)
                            console.print(f"    [cyan]{task_id}[/cyan]  {title}")

                    console.print()
                    console.print("  List all tasks: [cyan]anyt task list[/cyan]")
            else:
                if json_output:
                    output_json(
                        {"error": "FetchError", "message": str(e)}, success=False
                    )
                else:
                    console.print(f"[red]Error:[/red] Failed to fetch task: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch())


def share_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, t_1Z for UID). Uses active task if not specified."
        ),
    ] = None,
    copy: Annotated[
        bool,
        typer.Option("--copy", "-c", help="Copy link to clipboard"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Generate a shareable link for a task.

    Creates a public URL that can be shared with anyone who has access to the task.
    The link uses the task's UID for global accessibility.
    """
    # Check authentication
    try:
        get_effective_api_config()
    except RuntimeError:
        console.print("[red]Error:[/red] Not authenticated")
        console.print("\nSet the ANYT_API_KEY environment variable:")
        console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
        raise typer.Exit(1)

    service: TaskService = TaskService.from_config()
    workspace_service: WorkspaceService = WorkspaceService.from_config()

    # Use active task if no identifier provided
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task share DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task share DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)

    async def share() -> None:
        try:
            # Check if identifier is a UID (starts with 't_')
            if identifier.startswith("t_"):
                # Use UID endpoint (no workspace context needed)
                task = await service.get_task_by_uid(identifier)
            else:
                # Resolve workspace context for workspace-scoped identifiers
                workspace_id, workspace_identifier = await resolve_workspace_context(
                    None, workspace_service
                )

                # Normalize identifier for fuzzy matching with workspace prefix
                normalized_id = normalize_identifier(identifier, workspace_identifier)

                # Fetch task using service
                task = await service.get_task(normalized_id)

            # Generate shareable URL using uid
            share_url = f"https://anyt.dev/t/{task.uid}"

            # Copy to clipboard if requested
            if copy:
                try:
                    pyperclip.copy(share_url)
                    copied = True
                except Exception:
                    # Clipboard may not be available in all environments
                    copied = False

            # Output result
            if json_output:
                output_json(
                    {
                        "task_id": task.identifier,
                        "uid": task.uid,
                        "share_url": share_url,
                        "copied": copied if copy else False,
                    }
                )
            else:
                console.print()
                console.print(f"[cyan bold]{task.identifier}:[/cyan bold] {task.title}")
                console.print()
                console.print(f"[green]Shareable link:[/green] {share_url}")
                if copy:
                    if copied:
                        console.print("[green]✓[/green] Link copied to clipboard")
                    else:
                        console.print(
                            "[yellow]⚠[/yellow] Could not copy to clipboard (not available in this environment)"
                        )
                console.print()

        except Exception as e:
            error_msg = str(e)
            if json_output:
                output_json(
                    {"error": "ShareError", "message": error_msg}, success=False
                )
            else:
                console.print(f"[red]Error:[/red] Failed to generate share link: {e}")
            raise typer.Exit(1)

    asyncio.run(share())
