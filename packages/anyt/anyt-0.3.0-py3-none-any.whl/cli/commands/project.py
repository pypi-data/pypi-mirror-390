"""Project commands for AnyTask CLI."""

import asyncio
from pathlib import Path

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

from cli.config import WorkspaceConfig
from cli.models.project import Project, ProjectCreate
from cli.models.workspace import Workspace
from cli.services.workspace_service import WorkspaceService
from cli.services.project_service import ProjectService
from cli.services.preference_service import PreferenceService

app = typer.Typer(help="Manage projects")
console = Console()


@app.command()
def create(
    name: Annotated[str, typer.Option("--name", "-n", help="Project name")],
    description: Annotated[
        str | None,
        typer.Option("--description", "-d", help="Project description"),
    ] = None,
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """Create a new project in a workspace.

    Creates a project with the given name.
    By default, uses the workspace from the current directory's anyt.json.
    """
    try:
        from cli.config import get_effective_api_config

        # Check authentication
        try:
            get_effective_api_config()
        except RuntimeError:
            console.print("[red]Error:[/red] Not authenticated")
            console.print("\nSet the ANYT_API_KEY environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize services
        workspace_service: WorkspaceService = WorkspaceService.from_config()
        project_service: ProjectService = ProjectService.from_config()

        async def create_project() -> None:
            # Determine workspace
            target_workspace: Workspace

            if workspace:
                # Fetch workspace by ID or identifier
                console.print(f"Fetching workspace '{workspace}'...")
                workspaces = await workspace_service.list_workspaces()

                found_ws: Workspace | None = None
                for ws in workspaces:
                    if str(ws.id) == workspace or ws.identifier == workspace.upper():
                        found_ws = ws
                        break

                if not found_ws:
                    console.print(
                        f"[red]Error:[/red] Workspace '{workspace}' not found"
                    )
                    raise typer.Exit(1)

                target_workspace = found_ws
            else:
                # Use workspace from anyt.json
                target_dir = directory or Path.cwd()
                ws_config = WorkspaceConfig.load(target_dir)

                if not ws_config:
                    console.print(
                        "[red]Error:[/red] No workspace configured in current directory"
                    )
                    console.print(
                        "Run [cyan]anyt workspace init[/cyan] first or specify --workspace"
                    )
                    raise typer.Exit(1)

                target_workspace = await workspace_service.get_workspace(
                    ws_config.workspace_id
                )

            # Create project
            console.print(
                f"Creating project: [cyan]{name}[/cyan] in workspace [yellow]{target_workspace.name}[/yellow]..."
            )

            try:
                project = await project_service.create_project(
                    workspace_id=target_workspace.id,
                    project=ProjectCreate(
                        name=name,
                        description=description,
                    ),
                )

                console.print(f"[green]✓[/green] Created project: {project.name}")
                console.print(f"Project ID: {project.id}")

                if description:
                    console.print(f"Description: {description}")

            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to create project: {e}")
                raise typer.Exit(1)

        asyncio.run(create_project())

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def list(
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """List all projects in a workspace.

    By default, lists projects in the workspace from the current directory's anyt.json.
    """
    try:
        from cli.config import get_effective_api_config

        # Check authentication
        try:
            get_effective_api_config()
        except RuntimeError:
            console.print("[red]Error:[/red] Not authenticated")
            console.print("\nSet the ANYT_API_KEY environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize services
        workspace_service: WorkspaceService = WorkspaceService.from_config()
        project_service: ProjectService = ProjectService.from_config()
        preference_service: PreferenceService = PreferenceService.from_config()

        async def list_projects() -> None:
            # Determine workspace
            target_workspace: Workspace

            if workspace:
                # Fetch workspace by ID or identifier
                console.print(f"Fetching workspace '{workspace}'...")
                workspaces = await workspace_service.list_workspaces()

                found_ws: Workspace | None = None
                for ws in workspaces:
                    if str(ws.id) == workspace or ws.identifier == workspace.upper():
                        found_ws = ws
                        break

                if not found_ws:
                    console.print(
                        f"[red]Error:[/red] Workspace '{workspace}' not found"
                    )
                    raise typer.Exit(1)

                target_workspace = found_ws
            else:
                # Use workspace from anyt.json
                target_dir = directory or Path.cwd()
                ws_config = WorkspaceConfig.load(target_dir)

                if not ws_config:
                    console.print(
                        "[red]Error:[/red] No workspace configured in current directory"
                    )
                    console.print(
                        "Run [cyan]anyt workspace init[/cyan] first or specify --workspace"
                    )
                    raise typer.Exit(1)

                target_workspace = await workspace_service.get_workspace(
                    ws_config.workspace_id
                )

            # Fetch projects
            try:
                console.print(
                    f"Fetching projects in [yellow]{target_workspace.name}[/yellow]..."
                )
                projects = await project_service.list_projects(target_workspace.id)

                if not projects:
                    console.print("[yellow]No projects found[/yellow]")
                    console.print(
                        "\nCreate one with: [cyan]anyt project create --name 'Project Name'[/cyan]"
                    )
                    return

                # Get current project from user preferences
                try:
                    prefs = await preference_service.get_user_preferences()
                    current_project_id = prefs.current_project_id if prefs else None
                except Exception:
                    current_project_id = None

                # Display projects as a table
                table = Table(title=f"Projects in {target_workspace.name}")
                table.add_column("Name", style="green")
                table.add_column("ID", style="dim")
                table.add_column("Status", style="cyan")

                for proj in projects:
                    is_current = current_project_id and current_project_id == proj.id

                    status = "● current" if is_current else ""

                    table.add_row(
                        proj.name,
                        str(proj.id),
                        status,
                    )

                console.print(table)
                console.print(f"\nTotal: {len(projects)} projects")

            except Exception as e:
                console.print(f"[red]Error:[/red] Failed to fetch projects: {e}")
                raise typer.Exit(1)

        asyncio.run(list_projects())

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def use(
    project: Annotated[str, typer.Argument(help="Project ID to set as current")],
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """Set the current project for a workspace.

    Updates user preferences to make this the default project.
    """
    try:
        from cli.config import get_effective_api_config

        # Check authentication
        try:
            get_effective_api_config()
        except RuntimeError:
            console.print("[red]Error:[/red] Not authenticated")
            console.print("\nSet the ANYT_API_KEY environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize services
        workspace_service: WorkspaceService = WorkspaceService.from_config()
        project_service: ProjectService = ProjectService.from_config()
        preference_service: PreferenceService = PreferenceService.from_config()

        async def set_current_project() -> None:
            # Determine workspace
            target_workspace: Workspace

            if workspace:
                # Fetch workspace by ID or identifier
                console.print(f"Fetching workspace '{workspace}'...")
                workspaces = await workspace_service.list_workspaces()

                found_ws: Workspace | None = None
                for ws in workspaces:
                    if str(ws.id) == workspace or ws.identifier == workspace.upper():
                        found_ws = ws
                        break

                if not found_ws:
                    console.print(
                        f"[red]Error:[/red] Workspace '{workspace}' not found"
                    )
                    raise typer.Exit(1)

                target_workspace = found_ws
            else:
                # Use workspace from anyt.json
                target_dir = directory or Path.cwd()
                ws_config = WorkspaceConfig.load(target_dir)

                if not ws_config:
                    console.print(
                        "[red]Error:[/red] No workspace configured in current directory"
                    )
                    console.print(
                        "Run [cyan]anyt workspace init[/cyan] first or specify --workspace"
                    )
                    raise typer.Exit(1)

                target_workspace = await workspace_service.get_workspace(
                    ws_config.workspace_id
                )

            # Find the target project
            try:
                projects = await project_service.list_projects(target_workspace.id)

                target_proj: Project | None = None
                for proj in projects:
                    if str(proj.id) == project:
                        target_proj = proj
                        break

                if not target_proj:
                    console.print(f"[red]Error:[/red] Project '{project}' not found")
                    console.print("\nAvailable projects:")
                    for proj in projects:
                        console.print(f"  {proj.name} (ID: {proj.id})")
                    raise typer.Exit(1)

                # Set current project via user preferences
                await preference_service.set_current_project(
                    target_workspace.id, target_proj.id
                )

                console.print(
                    f"[green]✓[/green] Set current project to: {target_proj.name}"
                )
                console.print(f"[dim]Workspace: {target_workspace.name}[/dim]")

            except typer.Exit:
                raise
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

        asyncio.run(set_current_project())

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def current(
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """Show the current project for a workspace.

    Displays the current project based on user preferences.
    """
    try:
        from cli.config import get_effective_api_config

        # Check authentication
        try:
            get_effective_api_config()
        except RuntimeError:
            console.print("[red]Error:[/red] Not authenticated")
            console.print("\nSet the ANYT_API_KEY environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize services
        workspace_service: WorkspaceService = WorkspaceService.from_config()
        project_service: ProjectService = ProjectService.from_config()
        preference_service: PreferenceService = PreferenceService.from_config()

        async def show_current_project() -> None:
            # Determine workspace
            target_workspace: Workspace

            if workspace:
                # Fetch workspace by ID or identifier
                workspaces = await workspace_service.list_workspaces()

                found_ws: Workspace | None = None
                for ws in workspaces:
                    if str(ws.id) == workspace or ws.identifier == workspace.upper():
                        found_ws = ws
                        break

                if not found_ws:
                    console.print(
                        f"[red]Error:[/red] Workspace '{workspace}' not found"
                    )
                    raise typer.Exit(1)

                target_workspace = found_ws
            else:
                # Use workspace from anyt.json
                target_dir = directory or Path.cwd()
                ws_config = WorkspaceConfig.load(target_dir)

                if not ws_config:
                    console.print(
                        "[red]Error:[/red] No workspace configured in current directory"
                    )
                    console.print(
                        "Run [cyan]anyt workspace init[/cyan] first or specify --workspace"
                    )
                    raise typer.Exit(1)

                target_workspace = await workspace_service.get_workspace(
                    ws_config.workspace_id
                )

            # Get current project
            try:
                prefs = await preference_service.get_user_preferences()

                if not prefs or not prefs.current_project_id:
                    console.print(
                        f"Workspace: [yellow]{target_workspace.name}[/yellow]"
                    )
                    console.print("[dim]No current project set[/dim]")
                    console.print(
                        "\nSet a project with: [cyan]anyt project use PROJECT[/cyan]"
                    )
                    return

                current_project_id = prefs.current_project_id

                # Fetch project details
                projects = await project_service.list_projects(target_workspace.id)
                current_proj: Project | None = None

                for proj in projects:
                    if proj.id == current_project_id:
                        current_proj = proj
                        break

                if current_proj:
                    console.print(
                        f"Workspace: [yellow]{target_workspace.name}[/yellow]"
                    )
                    console.print(
                        f"Current project: [green]{current_proj.name}[/green]"
                    )
                    console.print(f"Project ID: {current_proj.id}")
                else:
                    console.print(
                        f"Workspace: [yellow]{target_workspace.name}[/yellow]"
                    )
                    console.print(
                        f"[yellow]Warning:[/yellow] Current project (ID: {current_project_id}) not found"
                    )

            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

        asyncio.run(show_current_project())

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def switch(
    workspace: Annotated[
        str | None,
        typer.Option(
            "--workspace",
            "-w",
            help="Workspace ID or identifier (default: current workspace)",
        ),
    ] = None,
    directory: Annotated[
        Path | None,
        typer.Option(
            "--dir", help="Directory with workspace config (default: current)"
        ),
    ] = None,
) -> None:
    """Interactively switch the current project.

    Displays a list of projects and allows you to select one.
    """
    try:
        from cli.config import get_effective_api_config

        # Check authentication
        try:
            get_effective_api_config()
        except RuntimeError:
            console.print("[red]Error:[/red] Not authenticated")
            console.print("\nSet the ANYT_API_KEY environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize services
        workspace_service: WorkspaceService = WorkspaceService.from_config()
        project_service: ProjectService = ProjectService.from_config()
        preference_service: PreferenceService = PreferenceService.from_config()

        async def switch_project() -> None:
            # Determine workspace
            target_workspace: Workspace

            if workspace:
                # Fetch workspace by ID or identifier
                workspaces = await workspace_service.list_workspaces()

                found_ws: Workspace | None = None
                for ws in workspaces:
                    if str(ws.id) == workspace or ws.identifier == workspace.upper():
                        found_ws = ws
                        break

                if not found_ws:
                    console.print(
                        f"[red]Error:[/red] Workspace '{workspace}' not found"
                    )
                    raise typer.Exit(1)

                target_workspace = found_ws
            else:
                # Use workspace from anyt.json
                target_dir = directory or Path.cwd()
                ws_config = WorkspaceConfig.load(target_dir)

                if not ws_config:
                    console.print(
                        "[red]Error:[/red] No workspace configured in current directory"
                    )
                    console.print(
                        "Run [cyan]anyt workspace init[/cyan] first or specify --workspace"
                    )
                    raise typer.Exit(1)

                target_workspace = await workspace_service.get_workspace(
                    ws_config.workspace_id
                )

            # Fetch projects
            try:
                console.print(
                    f"Fetching projects in [yellow]{target_workspace.name}[/yellow]..."
                )
                projects = await project_service.list_projects(target_workspace.id)

                if not projects:
                    console.print("[yellow]No projects found[/yellow]")
                    console.print(
                        "\nCreate one with: [cyan]anyt project create --name 'Project Name'[/cyan]"
                    )
                    raise typer.Exit(0)

                # Get current project
                try:
                    prefs = await preference_service.get_user_preferences()
                    current_project_id = prefs.current_project_id if prefs else None
                except Exception:
                    current_project_id = None

                # Show selection prompt
                table = Table(title=f"Projects in {target_workspace.name}")
                table.add_column("#", style="cyan", no_wrap=True)
                table.add_column("Name", style="green")
                table.add_column("ID", style="dim")
                table.add_column("Current", style="dim")

                for idx, proj in enumerate(projects, 1):
                    is_current = current_project_id and current_project_id == proj.id

                    table.add_row(
                        str(idx),
                        proj.name,
                        str(proj.id),
                        "●" if is_current else "",
                    )

                console.print(table)

                choice = Prompt.ask(
                    "Select project",
                    choices=[str(i) for i in range(1, len(projects) + 1)],
                    default="1",
                )

                target_proj = projects[int(choice) - 1]

                # Set current project
                await preference_service.set_current_project(
                    target_workspace.id, target_proj.id
                )

                console.print(
                    f"[green]✓[/green] Switched to project: {target_proj.name}"
                )

            except typer.Exit:
                raise
            except Exception as e:
                console.print(f"[red]Error:[/red] {e}")
                raise typer.Exit(1)

        asyncio.run(switch_project())

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
