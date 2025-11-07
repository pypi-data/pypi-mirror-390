"""List command for tasks."""

import asyncio
from typing import Optional

import typer
from rich.table import Table
from typing_extensions import Annotated

from cli.models.common import Priority, Status
from cli.models.task import TaskFilters
from cli.services.task_service import TaskService

from .helpers import (
    console,
    format_priority,
    format_relative_time,
    get_workspace_or_exit,
    output_json,
    truncate_text,
)


def list_tasks(
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    mine: Annotated[
        bool,
        typer.Option("--mine", help="Show only tasks assigned to you"),
    ] = False,
    assignee: Annotated[
        Optional[str],
        typer.Option(
            "--assignee", "-a", help="Filter by assignee (user ID or agent ID)"
        ),
    ] = None,
    me: Annotated[
        bool,
        typer.Option("--me", help="Show only my tasks (alias for --mine)"),
    ] = False,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Filter by labels (comma-separated)"),
    ] = None,
    sort: Annotated[
        str,
        typer.Option(
            "--sort", help="Sort field (priority, updated_at, created_at, status)"
        ),
    ] = "priority",
    order: Annotated[
        str,
        typer.Option("--order", help="Sort order (asc/desc)"),
    ] = "desc",
    limit: Annotated[
        int,
        typer.Option("--limit", help="Max number of tasks to show"),
    ] = 50,
    offset: Annotated[
        int,
        typer.Option("--offset", help="Pagination offset"),
    ] = 0,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """List tasks with filtering."""
    ws_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config()

    async def fetch() -> None:
        try:
            # Parse filters
            status_list = None
            if status:
                # Convert status strings to Status enums
                status_list = [Status(s.strip()) for s in status.split(",")]

            label_list = None
            if labels:
                label_list = [label.strip() for label in labels.split(",")]

            # Handle owner filtering (priority: --assignee > --me/--mine)
            owner_filter = None
            if assignee:
                owner_filter = assignee
            elif mine or me:
                owner_filter = "me"

            # Create typed filters
            filters = TaskFilters(
                workspace_id=int(ws_config.workspace_id),
                status=status_list,
                phase=phase,
                owner=owner_filter,
                labels=label_list,
                limit=limit,
                offset=offset,
                sort_by=sort,
                order=order,
            )

            # Fetch tasks using service
            tasks = await service.list_tasks(filters)

            # JSON output mode
            if json_output:
                output_json(
                    {
                        "items": [task.model_dump(mode="json") for task in tasks],
                        "count": len(tasks),
                    }
                )
                return

            # Rich console output mode
            if not tasks:
                console.print("[yellow]No tasks found[/yellow]")
                return

            # Display tasks in table
            table = Table(show_header=True, header_style="bold")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Title", style="white")
            table.add_column("Status", style="yellow", no_wrap=True)
            table.add_column("Priority", style="magenta", no_wrap=True)
            table.add_column("Updated", style="dim", no_wrap=True)

            for task in tasks:
                title = truncate_text(task.title)
                task_status = (
                    task.status.value
                    if isinstance(task.status, Status)
                    else task.status
                )
                priority_val = (
                    task.priority.value
                    if isinstance(task.priority, Priority)
                    else task.priority
                )
                priority_str = format_priority(priority_val)
                updated = format_relative_time(task.updated_at.isoformat())

                table.add_row(
                    task.identifier, title, task_status, priority_str, updated
                )

            console.print(table)

            # Show count
            count_text = "1 task" if len(tasks) == 1 else f"{len(tasks)} tasks"
            console.print(f"\n{count_text}")

        except Exception as e:
            if json_output:
                output_json({"error": "ListError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to list tasks: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch())
