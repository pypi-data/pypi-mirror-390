"""Initialize AnyTask workspace in current directory."""

import asyncio
import os
from datetime import datetime
from pathlib import Path

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.prompt import Prompt

from cli.config import WorkspaceConfig

console = Console()


def init(
    workspace_id: Annotated[
        int | None,
        typer.Option("--workspace-id", "-w", help="Workspace ID to link to"),
    ] = None,
    workspace_name: Annotated[
        str | None,
        typer.Option("--workspace-name", "-n", help="Workspace name (optional)"),
    ] = None,
    identifier: Annotated[
        str | None,
        typer.Option(
            "--identifier", "-i", help="Workspace identifier (e.g., DEV, PROJ)"
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option("--dir", "-d", help="Directory to initialize (default: current)"),
    ] = None,
    dev: Annotated[
        bool,
        typer.Option("--dev", help="Use development API (http://localhost:8000)"),
    ] = False,
) -> None:
    """Initialize AnyTask in the current directory.

    Requires ANYT_API_KEY environment variable to be set.
    Creates .anyt/ directory structure and anyt.json configuration.

    Examples:
        export ANYT_API_KEY=anyt_agent_...
        anyt init                                    # Production API (https://api.anyt.dev)
        anyt init --dev                              # Development API (http://localhost:8000)
        anyt init --workspace-id 123 --identifier DEV  # Link to specific workspace
    """
    try:
        # Determine target directory
        target_dir = directory or Path.cwd()
        target_dir = target_dir.resolve()

        # Create .anyt directory if it doesn't exist
        anyt_dir = target_dir / ".anyt"
        if not anyt_dir.exists():
            anyt_dir.mkdir(parents=True)
            console.print("[green]✓[/green] Created .anyt/ directory")
        else:
            console.print("[dim].anyt/ directory already exists[/dim]")

        # Create subdirectories
        subdirs = ["workflows", "tasks"]
        for subdir in subdirs:
            subdir_path = anyt_dir / subdir
            if not subdir_path.exists():
                subdir_path.mkdir(parents=True)
                console.print(f"[green]✓[/green] Created .anyt/{subdir}/ directory")

        # Check if workspace config already exists
        existing_config = WorkspaceConfig.load(target_dir)
        if existing_config:
            console.print(
                f"[yellow]Warning:[/yellow] Workspace config already exists: {existing_config.name}"
            )
            console.print(f"Workspace ID: {existing_config.workspace_id}")
            if existing_config.workspace_identifier:
                console.print(f"Identifier: {existing_config.workspace_identifier}")

            reset = Prompt.ask(
                "Do you want to reset it?", choices=["y", "N"], default="N"
            )

            if reset.lower() != "y":
                console.print("[green]✓[/green] Using existing workspace configuration")
                raise typer.Exit(0)

        # Check for ANYT_API_KEY environment variable
        api_key = os.getenv("ANYT_API_KEY")

        # Check for ANYT_API_KEY environment variable first
        if not api_key:
            console.print(
                "\n[red]Error:[/red] ANYT_API_KEY environment variable not set"
            )
            console.print("\nAuthentication is required to initialize a workspace.")
            console.print("Set the environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            console.print("\nGet your API key from:")
            console.print("  [dim]https://anyt.dev/home/settings/api-keys[/dim]")
            raise typer.Exit(1)

        # Determine API URL
        # Priority: ANYT_API_URL env var > --dev flag > production default
        api_url = os.getenv("ANYT_API_URL")
        if not api_url:
            api_url = "http://localhost:8000" if dev else "https://api.anyt.dev"

        # If workspace_id is provided, create workspace config manually
        if workspace_id:
            ws_config = WorkspaceConfig(
                workspace_id=workspace_id,
                name=workspace_name or f"Workspace {workspace_id}",
                api_url=api_url,
                workspace_identifier=identifier,
                current_project_id=None,
                last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )
            ws_config.save(target_dir)

            console.print(f"[green]✓[/green] Linked to workspace ID {workspace_id}")
            console.print(
                f"[green]✓[/green] Saved config to {target_dir}/.anyt/anyt.json"
            )
        else:
            # API key is set - automatically fetch and setup workspace
            console.print(
                "[cyan]ANYT_API_KEY detected - setting up workspace...[/cyan]"
            )

            async def setup_workspace() -> None:
                try:
                    # Initialize API clients directly
                    from cli.client.workspaces import WorkspacesAPIClient
                    from cli.client.projects import ProjectsAPIClient

                    ws_client = WorkspacesAPIClient(base_url=api_url, api_key=api_key)
                    proj_client = ProjectsAPIClient(base_url=api_url, api_key=api_key)

                    # Fetch available workspaces
                    console.print("Fetching accessible workspaces...")
                    workspaces = await ws_client.list_workspaces()

                    if not workspaces:
                        console.print(
                            "[red]Error:[/red] No accessible workspaces found for this API key"
                        )
                        console.print(
                            "\nAPI keys require at least one workspace to be created first."
                        )
                        console.print(
                            "Please create a workspace using the web interface at [cyan]https://anyt.dev[/cyan]"
                        )
                        raise typer.Exit(1)

                    # Use the first available workspace
                    workspace = workspaces[0]
                    console.print(
                        f"[green]✓[/green] Using workspace: {workspace.name} ({workspace.identifier})"
                    )

                    # If multiple workspaces, show info
                    if len(workspaces) > 1:
                        console.print(
                            f"[dim]Found {len(workspaces)} workspaces. Using the first one.[/dim]"
                        )
                        console.print(
                            "[dim]Use 'anyt workspace list' to see all, or 'anyt workspace switch' to change.[/dim]"
                        )

                    # Fetch or create default project
                    console.print("Fetching current project...")
                    try:
                        # Try to get existing projects
                        projects = await proj_client.list_projects(workspace.id)

                        if projects:
                            # Use the first project
                            current_project = projects[0]
                        else:
                            # Create default project
                            from cli.models.project import ProjectCreate

                            current_project = await proj_client.create_project(
                                workspace.id,
                                ProjectCreate(
                                    name=workspace.name,
                                ),
                            )

                        current_project_id = current_project.id
                        console.print(
                            f"[green]✓[/green] Using project: {current_project.name}"
                        )
                    except Exception as e:
                        console.print(
                            f"[yellow]Warning:[/yellow] Could not fetch current project: {e}"
                        )
                        current_project_id = None

                    # Create and save workspace config (no api_key stored)
                    ws_config = WorkspaceConfig(
                        workspace_id=workspace.id,
                        name=workspace.name,
                        api_url=api_url,
                        workspace_identifier=workspace.identifier,
                        current_project_id=current_project_id,
                        last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                    ws_config.save(target_dir)

                    console.print(
                        f"[green]✓[/green] Saved config to {target_dir}/.anyt/anyt.json"
                    )

                except Exception as e:
                    if not isinstance(e, typer.Exit):
                        console.print(
                            f"[red]Error:[/red] Failed to setup workspace: {e}"
                        )
                        raise typer.Exit(1)
                    raise

            asyncio.run(setup_workspace())

        console.print("\n[green]✓[/green] Initialization complete!")

    except Exception as e:
        if not isinstance(e, typer.Exit):
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        raise  # Re-raise typer.Exit to preserve exit code
