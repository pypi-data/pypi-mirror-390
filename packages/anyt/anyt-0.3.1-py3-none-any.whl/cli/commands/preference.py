"""User preference management commands."""

import asyncio
import typer
from rich.console import Console
from rich.table import Table

from cli.services.preference_service import PreferenceService
from cli.services.workspace_service import WorkspaceService

app = typer.Typer(help="Manage user preferences for workspace and project")
console = Console()


@app.command("show")
def show() -> None:
    """Show current user preferences (workspace and project)."""
    asyncio.run(_show())


async def _show() -> None:
    """Show current user preferences."""
    try:
        from cli.config import get_effective_api_config  # Check authentication

        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] This command requires authentication.",
                style="bold",
            )
            console.print(
                "Set the ANYT_API_KEY environment variable:",
                style="dim",
            )
            console.print("  export ANYT_API_KEY=anyt_agent_...", style="cyan")
            raise typer.Exit(1)

        # Initialize services
        pref_service: PreferenceService = PreferenceService.from_config()
        workspace_service: WorkspaceService = WorkspaceService.from_config()

        # Get user preferences
        prefs = await pref_service.get_user_preferences()

        if not prefs:
            console.print("[yellow]No preferences set[/yellow]", style="bold")
            console.print(
                "\nSet your current workspace with: [cyan]anyt preference set-workspace <workspace_id>[/cyan]"
            )
            console.print(
                "Set your current project with: [cyan]anyt preference set-project <workspace_id> <project_id>[/cyan]"
            )
            return

        # Create table for preferences
        table = Table(title="User Preferences", show_header=True)
        table.add_column("Setting", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")

        # Add workspace preference
        workspace_id = prefs.current_workspace_id
        if workspace_id:
            try:
                workspace = await workspace_service.get_workspace(workspace_id)
                table.add_row(
                    "Current Workspace",
                    f"[{workspace_id}] {workspace.name}",
                )
            except Exception:
                table.add_row("Current Workspace", f"[{workspace_id}]")
        else:
            table.add_row("Current Workspace", "[dim]Not set[/dim]")

        # Add project preference
        project_id = prefs.current_project_id
        if project_id and workspace_id:
            # Note: We'd need a get_project method in the client to show project name
            # For now, just show the ID
            table.add_row("Current Project", f"[{project_id}]")
        else:
            table.add_row("Current Project", "[dim]Not set[/dim]")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)


@app.command("set-workspace")
def set_workspace(
    workspace_id: int = typer.Argument(..., help="Workspace ID to set as current"),
) -> None:
    """Set the current workspace preference."""
    asyncio.run(_set_workspace(workspace_id))


async def _set_workspace(workspace_id: int) -> None:
    """Set the current workspace preference."""
    try:
        from cli.config import get_effective_api_config  # Check authentication

        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] This command requires authentication.",
                style="bold",
            )
            console.print(
                "Set the ANYT_API_KEY environment variable:",
                style="dim",
            )
            console.print("  export ANYT_API_KEY=anyt_agent_...", style="cyan")
            raise typer.Exit(1)

        # Initialize services
        pref_service: PreferenceService = PreferenceService.from_config()
        workspace_service: WorkspaceService = WorkspaceService.from_config()

        # Set workspace preference
        prefs = await pref_service.set_current_workspace(workspace_id)

        # Get workspace details for display
        try:
            workspace = await workspace_service.get_workspace(workspace_id)
            console.print(
                f"[green]✓[/green] Current workspace updated to [{workspace_id}] {workspace.name}",
                style="bold",
            )
        except Exception:
            console.print(
                f"[green]✓[/green] Current workspace updated to [{workspace_id}]",
                style="bold",
            )

        # Check if project was cleared
        if prefs.current_project_id is None:
            console.print(
                "[yellow]Note:[/yellow] Current project was cleared (not in this workspace)",
                style="dim",
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)


@app.command("set-project")
def set_project(
    workspace_id: int = typer.Argument(..., help="Workspace ID containing the project"),
    project_id: int = typer.Argument(..., help="Project ID to set as current"),
) -> None:
    """Set the current project (and workspace) preference."""
    asyncio.run(_set_project(workspace_id, project_id))


async def _set_project(workspace_id: int, project_id: int) -> None:
    """Set the current project preference."""
    try:
        from cli.config import get_effective_api_config  # Check authentication

        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] This command requires authentication.",
                style="bold",
            )
            console.print(
                "Set the ANYT_API_KEY environment variable:",
                style="dim",
            )
            console.print("  export ANYT_API_KEY=anyt_agent_...", style="cyan")
            raise typer.Exit(1)

        # Initialize services
        pref_service: PreferenceService = PreferenceService.from_config()
        workspace_service: WorkspaceService = WorkspaceService.from_config()

        # Set project preference
        await pref_service.set_current_project(workspace_id, project_id)

        # Get workspace details for display
        try:
            workspace = await workspace_service.get_workspace(workspace_id)
            console.print(
                f"[green]✓[/green] Current workspace updated to [{workspace_id}] {workspace.name}",
                style="bold",
            )
        except Exception:
            console.print(
                f"[green]✓[/green] Current workspace updated to [{workspace_id}]",
                style="bold",
            )

        console.print(
            f"[green]✓[/green] Current project updated to [{project_id}]",
            style="bold",
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)


@app.command("clear")
def clear() -> None:
    """Clear user preferences (reset workspace and project)."""
    asyncio.run(_clear())


async def _clear() -> None:
    """Clear user preferences."""
    try:
        from cli.config import get_effective_api_config  # Check authentication

        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] This command requires authentication.",
                style="bold",
            )
            console.print(
                "Set the ANYT_API_KEY environment variable:",
                style="dim",
            )
            console.print("  export ANYT_API_KEY=anyt_agent_...", style="cyan")
            raise typer.Exit(1)

        # Initialize service
        pref_service: PreferenceService = PreferenceService.from_config()

        # Clear preferences
        await pref_service.clear_user_preferences()

        console.print(
            "[green]✓[/green] User preferences cleared",
            style="bold",
        )
        console.print(
            "[dim]Your workspace and project selections have been reset[/dim]"
        )

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}", style="bold")
        raise typer.Exit(1)
