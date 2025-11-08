"""Task view management commands for AnyTask CLI."""

import asyncio
import json
from typing import Any, Optional, cast

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm

from cli.config import get_effective_api_config, WorkspaceConfig
from cli.models.task import TaskFilters
from cli.models.view import TaskViewCreate, TaskViewUpdate
from cli.services.task_service import TaskService
from cli.services.view_service import ViewService

app = typer.Typer(help="Manage saved task views (filters)")
console = Console()


def _build_filters_dict(
    status: Optional[str] = None,
    priority_min: Optional[int] = None,
    priority_max: Optional[int] = None,
    owner: Optional[str] = None,
    labels: Optional[str] = None,
) -> dict[str, Any]:
    """Build filters dictionary from command options."""
    filters: dict[str, Any] = {}

    if status:
        filters["status"] = [s.strip() for s in status.split(",")]

    if priority_min is not None:
        filters["priority_min"] = priority_min

    if priority_max is not None:
        filters["priority_max"] = priority_max

    if owner:
        filters["owner"] = owner

    if labels:
        filters["labels"] = [label.strip() for label in labels.split(",")]

    return filters


def _format_filters_summary(filters: dict[str, Any]) -> str:
    """Format filters dictionary as a human-readable summary."""
    parts: list[str] = []

    if "status" in filters and filters["status"]:
        parts.append(f"status={','.join(filters['status'])}")

    if "priority_min" in filters:
        parts.append(f"priority≥{filters['priority_min']}")

    if "priority_max" in filters:
        parts.append(f"priority≤{filters['priority_max']}")

    if "owner" in filters:
        parts.append(f"owner={filters['owner']}")

    if "labels" in filters and filters["labels"]:
        parts.append(f"labels={','.join(filters['labels'])}")

    return ", ".join(parts) if parts else "No filters"


@app.command("create")
def create_view(
    name: Annotated[str, typer.Argument(help="View name")],
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    priority_min: Annotated[
        Optional[int], typer.Option("--priority-min", help="Minimum priority")
    ] = None,
    priority_max: Annotated[
        Optional[int], typer.Option("--priority-max", help="Maximum priority")
    ] = None,
    owner: Annotated[
        Optional[str], typer.Option("--owner", help="Filter by owner")
    ] = None,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Filter by labels (comma-separated)"),
    ] = None,
    default: Annotated[
        bool, typer.Option("--default", help="Set as default view")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """Create a new saved task view (filter)."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Build filters
        filters = _build_filters_dict(status, priority_min, priority_max, owner, labels)

        if not filters:
            console.print(
                "[yellow]Warning:[/yellow] Creating a view with no filters. "
                "Use options like --status, --priority-min, --labels to add filters."
            )

        # Initialize service
        service: ViewService = ViewService.from_config()

        # Create view
        result = asyncio.run(
            service.create_task_view(
                workspace_id=int(workspace_config.workspace_id),
                view=TaskViewCreate(
                    name=name,
                    filters=filters,
                    is_default=default,
                ),
            )
        )

        if json_output:
            console.print(json.dumps(result.model_dump(mode="json"), indent=2))
        else:
            default_marker = " [cyan](default)[/cyan]" if result.is_default else ""
            console.print(
                f"[green]✓[/green] Created view: {result.name}{default_marker}"
            )
            console.print(f"  Filters: {_format_filters_summary(result.filters or {})}")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_views(
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """List all saved task views."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for user authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize service
        service: ViewService = ViewService.from_config()

        # List views
        views = asyncio.run(
            service.list_task_views(workspace_id=int(workspace_config.workspace_id))
        )

        if json_output:
            console.print(
                json.dumps([view.model_dump(mode="json") for view in views], indent=2)
            )
        else:
            if not views:
                console.print("No saved views found")
                console.print(
                    "\nCreate a view with: [cyan]anyt view create <name> --status <status>[/cyan]"
                )
                return

            # Sort alphabetically
            views.sort(key=lambda x: x.name.lower())

            # Create table
            table = Table(title=f"Task Views in {workspace_config.name}")
            table.add_column("Name", style="cyan")
            table.add_column("Filters", style="white")
            table.add_column("Default", style="yellow")

            for view in views:
                filters_summary = _format_filters_summary(view.filters or {})
                default_marker = "⭐" if view.is_default else ""

                table.add_row(view.name, filters_summary, default_marker)

            console.print(table)
            console.print(f"\nTotal: {len(views)} view(s)")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("show")
def show_view(
    name: Annotated[str, typer.Argument(help="View name")],
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """Show details for a specific view."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for user authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize service
        service: ViewService = ViewService.from_config()

        # Get view by name
        view = asyncio.run(
            service.get_task_view_by_name(
                workspace_id=int(workspace_config.workspace_id), name=name
            )
        )

        if not view:
            console.print(f"[red]Error:[/red] View '{name}' not found")
            raise typer.Exit(1)

        if json_output:
            console.print(json.dumps(view.model_dump(mode="json"), indent=2))
        else:
            default_marker = " [cyan](default)[/cyan]" if view.is_default else ""
            console.print(f"\n[bold]{view.name}{default_marker}[/bold]\n")

            filters = view.filters or {}
            if filters:
                console.print("[bold]Filters:[/bold]")
                for key, value in filters.items():
                    if isinstance(value, list):
                        value_list: list[Any] = cast(list[Any], value)  # type: ignore[redundant-cast]
                        console.print(
                            f"  • {key}: {', '.join(str(v) for v in value_list)}"
                        )
                    else:
                        console.print(f"  • {key}: {value}")
            else:
                console.print("[dim]No filters configured[/dim]")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("apply")
def apply_view(
    name: Annotated[str, typer.Argument(help="View name")],
    limit: Annotated[int, typer.Option("--limit", help="Max tasks to show")] = 50,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """Apply a saved view and display matching tasks."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for user authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize services
        view_service: ViewService = ViewService.from_config()
        task_service: TaskService = TaskService.from_config()

        # Get view by name
        view = asyncio.run(
            view_service.get_task_view_by_name(
                workspace_id=int(workspace_config.workspace_id), name=name
            )
        )

        if not view:
            console.print(f"[red]Error:[/red] View '{name}' not found")
            raise typer.Exit(1)

        # Get filters from view
        filters_dict = view.filters or {}

        # Build query parameters for task list
        status_list = filters_dict.get("status")
        priority_min = filters_dict.get("priority_min")
        priority_max = filters_dict.get("priority_max")

        # Create TaskFilters object
        task_filters = TaskFilters(
            workspace_id=int(workspace_config.workspace_id),
            limit=limit,
        )
        if status_list:
            from cli.models.common import Status

            task_filters.status = [Status(s) for s in status_list]
        if priority_min is not None:
            task_filters.priority_gte = priority_min
        if priority_max is not None:
            task_filters.priority_lte = priority_max

        # List tasks with filters
        tasks = asyncio.run(task_service.list_tasks(task_filters))

        if json_output:
            console.print(
                json.dumps(
                    {"items": [task.model_dump(mode="json") for task in tasks]},
                    indent=2,
                )
            )
        else:
            console.print(f"\n[bold]View: {view.name}[/bold]")
            console.print(f"Filters: {_format_filters_summary(filters_dict)}\n")

            if not tasks:
                console.print("No tasks match this view")
                return

            # Create table
            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Status", style="yellow")
            table.add_column("Priority", style="magenta")

            for task in tasks:
                table.add_row(
                    task.identifier,
                    task.title,
                    task.status.value
                    if hasattr(task.status, "value")
                    else str(task.status),
                    str(
                        task.priority.value
                        if hasattr(task.priority, "value")
                        else task.priority
                    ),
                )

            console.print(table)
            console.print(f"\nShowing {len(tasks)} task(s)")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("edit")
def edit_view(
    name: Annotated[str, typer.Argument(help="View name")],
    new_name: Annotated[
        Optional[str], typer.Option("--name", help="New view name")
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Update status filter (comma-separated)"),
    ] = None,
    priority_min: Annotated[
        Optional[int], typer.Option("--priority-min", help="Update min priority")
    ] = None,
    priority_max: Annotated[
        Optional[int], typer.Option("--priority-max", help="Update max priority")
    ] = None,
    owner: Annotated[
        Optional[str], typer.Option("--owner", help="Update owner filter")
    ] = None,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Update labels filter (comma-separated)"),
    ] = None,
    default: Annotated[
        Optional[bool],
        typer.Option("--default/--no-default", help="Set/unset as default"),
    ] = None,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """Edit a saved view."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for user authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize service
        service: ViewService = ViewService.from_config()

        # Get view by name
        view = asyncio.run(
            service.get_task_view_by_name(
                workspace_id=int(workspace_config.workspace_id), name=name
            )
        )

        if not view:
            console.print(f"[red]Error:[/red] View '{name}' not found")
            raise typer.Exit(1)

        # Build update values
        update_name: Optional[str] = None
        update_filters: Optional[dict[str, Any]] = None
        update_default: Optional[bool] = None

        if new_name is not None:
            update_name = new_name

        # Update filters if any filter options provided
        if any(
            [status, priority_min is not None, priority_max is not None, owner, labels]
        ):
            # Start with existing filters
            current_filters = view.filters or {}
            new_filters = current_filters.copy()

            # Update with new values
            if status:
                new_filters["status"] = [s.strip() for s in status.split(",")]
            if priority_min is not None:
                new_filters["priority_min"] = priority_min
            if priority_max is not None:
                new_filters["priority_max"] = priority_max
            if owner:
                new_filters["owner"] = owner
            if labels:
                new_filters["labels"] = [label.strip() for label in labels.split(",")]

            update_filters = new_filters

        if default is not None:
            update_default = default

        if update_name is None and update_filters is None and update_default is None:
            console.print(
                "[yellow]No changes specified. Use --name, --status, etc.[/yellow]"
            )
            return

        # Update view
        result = asyncio.run(
            service.update_task_view(
                workspace_id=int(workspace_config.workspace_id),
                view_id=view.id,
                updates=TaskViewUpdate(
                    name=update_name,
                    filters=update_filters,
                    is_default=update_default,
                ),
            )
        )

        if json_output:
            console.print(json.dumps(result.model_dump(mode="json"), indent=2))
        else:
            console.print(f"[green]✓[/green] Updated view: {result.name}")
            console.print(f"  Filters: {_format_filters_summary(result.filters or {})}")
            if result.is_default:
                console.print("  [cyan]Default view[/cyan]")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("rm")
def delete_view(
    names: Annotated[list[str], typer.Argument(help="View name(s) to delete")],
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """Delete one or more saved views."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for user authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize service
        service: ViewService = ViewService.from_config()

        deleted: list[str] = []
        errors: list[str] = []

        for name in names:
            try:
                # Get view by name
                view = asyncio.run(
                    service.get_task_view_by_name(
                        workspace_id=int(workspace_config.workspace_id), name=name
                    )
                )

                if not view:
                    errors.append(f"{name}: not found")
                    continue

                # Confirm deletion
                if not force:
                    if view.is_default:
                        console.print(
                            f"[yellow]Warning:[/yellow] '{name}' is your default view"
                        )

                    if not Confirm.ask(f"Delete view '{name}'?"):
                        console.print(f"Skipped: {name}")
                        continue

                # Delete view
                asyncio.run(
                    service.delete_task_view(
                        workspace_id=int(workspace_config.workspace_id),
                        view_id=view.id,
                    )
                )

                deleted.append(name)

            except Exception as e:
                errors.append(f"{name}: {str(e)}")

        # Output results
        if json_output:
            console.print(json.dumps({"deleted": deleted, "errors": errors}, indent=2))
        else:
            if deleted:
                for name in deleted:
                    console.print(f"[green]✓[/green] Deleted view: {name}")

            if errors:
                console.print("\n[red]Errors:[/red]")
                for error in errors:
                    console.print(f"  • {error}")

            if not deleted and not errors:
                console.print("No views deleted")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("default")
def set_default_view(
    name: Annotated[
        Optional[str], typer.Argument(help="View name to set as default")
    ] = None,
    clear: Annotated[bool, typer.Option("--clear", help="Clear default view")] = False,
    json_output: Annotated[
        bool, typer.Option("--json", help="Output in JSON format")
    ] = False,
) -> None:
    """Set or clear the default task view."""
    try:
        # Load configs
        workspace_config = WorkspaceConfig.load()

        if not workspace_config:
            console.print(
                "[red]Error:[/red] Not in a workspace directory. Run [cyan]anyt init[/cyan] first"
            )
            raise typer.Exit(1)

        # Check for user authentication
        try:
            get_effective_api_config()

        except RuntimeError:
            console.print(
                "[red]Error:[/red] Task views require authentication. "
                "Set the ANYT_API_KEY environment variable:"
            )
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Initialize service
        service: ViewService = ViewService.from_config()

        if clear:
            # Get current default view
            current_default = asyncio.run(
                service.get_default_task_view(
                    workspace_id=int(workspace_config.workspace_id)
                )
            )

            if not current_default:
                console.print("No default view is set")
                return

            # Clear default
            asyncio.run(
                service.update_task_view(
                    workspace_id=int(workspace_config.workspace_id),
                    view_id=current_default.id,
                    updates=TaskViewUpdate(is_default=False),
                )
            )

            if json_output:
                console.print(json.dumps({"message": "Default view cleared"}, indent=2))
            else:
                console.print(
                    f"[green]✓[/green] Cleared default view (was: {current_default.name})"
                )

        elif name:
            # Set new default
            view = asyncio.run(
                service.get_task_view_by_name(
                    workspace_id=int(workspace_config.workspace_id), name=name
                )
            )

            if not view:
                console.print(f"[red]Error:[/red] View '{name}' not found")
                raise typer.Exit(1)

            # Update to default
            result = asyncio.run(
                service.update_task_view(
                    workspace_id=int(workspace_config.workspace_id),
                    view_id=view.id,
                    updates=TaskViewUpdate(is_default=True),
                )
            )

            if json_output:
                console.print(json.dumps(result.model_dump(mode="json"), indent=2))
            else:
                console.print(f"[green]✓[/green] Set '{name}' as default view")

        else:
            console.print("[yellow]Specify a view name or use --clear[/yellow]")
            console.print("Usage: anyt view default <name>")
            console.print("       anyt view default --clear")

    except Exception as e:
        if json_output:
            console.print(json.dumps({"error": str(e)}))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
