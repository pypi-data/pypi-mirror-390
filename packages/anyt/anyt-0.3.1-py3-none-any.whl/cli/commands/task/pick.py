"""Pick command for setting the active task."""

import asyncio
import json
from collections import defaultdict
from datetime import UTC, datetime
from typing import Optional

import typer
from rich.prompt import Prompt
from rich.table import Table
from typing_extensions import Annotated

from cli.config import ActiveTaskConfig
from cli.models.common import Priority, Status
from cli.models.task import TaskFilters
from cli.models.wrappers.task import Task
from cli.services.task_service import TaskService

from .helpers import console, get_workspace_or_exit, resolve_task_identifier


def display_interactive_picker(
    tasks: list[Task], group_by_status: bool = True
) -> str | None:
    """Display interactive task picker and return selected task identifier.

    Args:
        tasks: List of Task objects
        group_by_status: If True, group tasks by status

    Returns:
        Selected task identifier or None if cancelled
    """
    if not tasks:
        console.print("[yellow]No tasks available to pick[/yellow]")
        return None

    # Group tasks by status if requested
    if group_by_status:
        groups: defaultdict[str, list[Task]] = defaultdict(list)
        for task in tasks:
            status_val = (
                task.status.value if isinstance(task.status, Status) else task.status
            )
            groups[status_val].append(task)

        # Display tasks grouped by status
        task_index = 1
        task_map: dict[int, str] = {}

        for status in [
            "backlog",
            "todo",
            "inprogress",
            "blocked",
            "done",
        ]:
            if status not in groups:
                continue

            status_tasks = groups[status]
            console.print(
                f"\n[bold cyan]{status.upper()}[/bold cyan] ({len(status_tasks)} tasks)"
            )

            table = Table(show_header=True, header_style="bold magenta", box=None)
            table.add_column("#", style="cyan", width=4)
            table.add_column("ID", style="yellow", width=12)
            table.add_column("Title", style="white")
            table.add_column("Priority", style="blue", width=8)

            for task in status_tasks:
                title: str = task.title
                priority_val: int = (
                    task.priority.value
                    if isinstance(task.priority, Priority)
                    else task.priority
                )

                # Format priority display
                priority_display = {
                    2: "↑↑ (2)",
                    1: "↑ (1)",
                    0: "- (0)",
                    -1: "↓ (-1)",
                    -2: "↓↓ (-2)",
                }.get(priority_val, str(priority_val))

                # Truncate title if too long
                if len(title) > 60:
                    title = title[:57] + "..."

                table.add_row(str(task_index), task.identifier, title, priority_display)
                task_map[task_index] = task.identifier
                task_index += 1

            console.print(table)

    else:
        # Simple list without grouping
        table = Table(
            title="Available Tasks", show_header=True, header_style="bold magenta"
        )
        table.add_column("#", style="cyan", width=4)
        table.add_column("ID", style="yellow", width=12)
        table.add_column("Title", style="white")
        table.add_column("Status", style="blue", width=12)
        table.add_column("Priority", style="green", width=8)

        task_map = {}
        for idx, task in enumerate(tasks, 1):
            title = task.title
            status_val = (
                task.status.value if isinstance(task.status, Status) else task.status
            )
            priority_val = (
                task.priority.value
                if isinstance(task.priority, Priority)
                else task.priority
            )

            # Format priority display
            priority_display = {
                2: "↑↑ (2)",
                1: "↑ (1)",
                0: "- (0)",
                -1: "↓ (-1)",
                -2: "↓↓ (-2)",
            }.get(priority_val, str(priority_val))

            # Truncate title if too long
            if len(title) > 50:
                title = title[:47] + "..."

            table.add_row(
                str(idx), task.identifier, title, status_val, priority_display
            )
            task_map[idx] = task.identifier

        console.print(table)

    # Prompt user for selection
    console.print()
    choice = Prompt.ask("[bold]Select task number[/bold] (or 'q' to quit)", default="q")

    if choice.lower() == "q":
        console.print("[yellow]Selection cancelled[/yellow]")
        return None

    try:
        idx = int(choice)
        if idx in task_map:
            return str(task_map[idx])
        else:
            console.print(f"[red]Invalid selection: {idx}[/red]")
            console.print(f"Please choose a number between 1 and {len(task_map)}")
            return None
    except ValueError:
        console.print(f"[red]Invalid input: '{choice}'[/red]")
        console.print("Please enter a number or 'q' to quit")
        return None


def pick_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, t_1Z for UID) or ID. Leave empty for interactive picker."
        ),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    project: Annotated[
        Optional[int],
        typer.Option("--project", help="Filter by project ID"),
    ] = None,
    mine: Annotated[
        bool,
        typer.Option("--mine", help="Show only tasks assigned to you"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Pick a task to work on (sets as active task).

    If identifier is provided, picks that specific task.
    Otherwise, shows an interactive picker to select a task.
    """
    ws_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config()

    async def pick() -> None:
        try:
            # If identifier is provided, pick that task directly
            if identifier:
                # Resolve identifier (converts UIDs to workspace identifiers)
                resolved_identifier = await resolve_task_identifier(
                    identifier, service, ws_config.workspace_identifier
                )

                # Fetch task details
                task = await service.get_task(resolved_identifier)

                # Save as active task
                active_task = ActiveTaskConfig(
                    identifier=task.identifier,
                    title=task.title,
                    picked_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    workspace_id=task.workspace_id,
                    project_id=task.project_id,
                )
                active_task.save()

                if json_output:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "identifier": task.identifier,
                                    "title": task.title,
                                    "workspace_id": task.workspace_id,
                                    "project_id": task.project_id,
                                    "picked_at": active_task.picked_at,
                                },
                                "message": "Task picked successfully",
                            }
                        )
                    )
                else:
                    console.print(
                        f"[green]✓[/green] Picked [cyan]{task.identifier}[/cyan] ({task.title})"
                    )
                    console.print("  Saved to .anyt/active_task.json")

            else:
                # Interactive picker - fetch tasks and display
                # Build filters
                status_list = None
                if status:
                    # Convert status strings to Status enums
                    status_list = [Status(s.strip()) for s in status.split(",")]

                owner_filter = None
                if mine:
                    owner_filter = "me"

                # Create typed filters
                filters = TaskFilters(
                    workspace_id=int(ws_config.workspace_id),
                    status=status_list,
                    project_id=project,
                    owner=owner_filter,
                )

                # Fetch tasks
                tasks = await service.list_tasks(filters)

                if not tasks:
                    if json_output:
                        print(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": "No tasks available",
                                    "message": "No tasks found matching the filters",
                                }
                            )
                        )
                    else:
                        console.print("[yellow]No tasks available to pick[/yellow]")
                        console.print("Try adjusting your filters or create a new task")
                    raise typer.Exit(1)

                # Display interactive picker
                selected_identifier = display_interactive_picker(
                    tasks, group_by_status=True
                )

                if not selected_identifier:
                    # User cancelled
                    if json_output:
                        print(
                            json.dumps(
                                {
                                    "success": False,
                                    "error": "Selection cancelled",
                                    "message": "No task was picked",
                                }
                            )
                        )
                    raise typer.Exit(0)

                # Fetch the selected task details
                task = await service.get_task(selected_identifier)

                # Save as active task
                active_task = ActiveTaskConfig(
                    identifier=task.identifier,
                    title=task.title,
                    picked_at=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    workspace_id=task.workspace_id,
                    project_id=task.project_id,
                )
                active_task.save()

                if json_output:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "identifier": task.identifier,
                                    "title": task.title,
                                    "workspace_id": task.workspace_id,
                                    "project_id": task.project_id,
                                    "picked_at": active_task.picked_at,
                                },
                                "message": "Task picked successfully",
                            }
                        )
                    )
                else:
                    console.print(
                        f"[green]✓[/green] Picked [cyan]{task.identifier}[/cyan] ({task.title})"
                    )
                    console.print("  Saved to .anyt/active_task.json")

        except typer.Exit:
            raise
        except Exception as e:
            error_msg = str(e)
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Task not found"
                            if "404" in error_msg
                            else f"Failed to pick task: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(f"[red]Error:[/red] Failed to pick task: {e}")
            raise typer.Exit(1)

    asyncio.run(pick())
