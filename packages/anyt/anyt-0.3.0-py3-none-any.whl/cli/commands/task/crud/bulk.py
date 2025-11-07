"""Bulk operations for tasks (bulk update)."""

import asyncio
from typing import Any, Optional

import typer
from rich.prompt import Confirm
from typing_extensions import Annotated

from cli.models.common import Status
from cli.models.task import TaskUpdate
from cli.services.task_service import TaskService

from ..helpers import console, output_json


def bulk_update_tasks(
    task_ids: Annotated[
        str,
        typer.Argument(
            help="Comma-separated task identifiers (e.g., 'DEV-1,DEV-2,DEV-3')"
        ),
    ],
    status: Annotated[
        Optional[str],
        typer.Option("--status", "-s", help="New status for all tasks"),
    ] = None,
    priority: Annotated[
        Optional[int],
        typer.Option("--priority", "-p", help="New priority for all tasks (-2 to 2)"),
    ] = None,
    assignee: Annotated[
        Optional[str],
        typer.Option("--assignee", "-a", help="Assignee username or ID"),
    ] = None,
    project: Annotated[
        Optional[str],
        typer.Option("--project", help="Project identifier or ID"),
    ] = None,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON"),
    ] = False,
) -> None:
    """Update multiple tasks at once.

    Examples:
        anyt task bulk-update DEV-1,DEV-2,DEV-3 --status in_progress
        anyt task bulk-update DEV-4,DEV-5 --priority 2
        anyt task bulk-update DEV-6,DEV-7,DEV-8 --assignee john --yes
        anyt task bulk-update DEV-9,DEV-10 --status todo --priority 1
    """

    async def bulk_update() -> None:
        try:
            # Parse task IDs
            identifiers = [tid.strip() for tid in task_ids.split(",")]

            if not identifiers:
                if json_output:
                    output_json(
                        {"error": "ValidationError", "message": "No task IDs provided"},
                        success=False,
                    )
                else:
                    console.print("[red]Error: No task IDs provided[/red]")
                raise typer.Exit(1)

            # Build updates dictionary
            updates_dict: dict[str, Any] = {}

            if status:
                try:
                    updates_dict["status"] = Status(status)
                except ValueError:
                    valid_statuses = ", ".join([s.value for s in Status])
                    if json_output:
                        output_json(
                            {
                                "error": "ValidationError",
                                "message": f"Invalid status '{status}'. Valid statuses: {valid_statuses}",
                            },
                            success=False,
                        )
                    else:
                        console.print(f"[red]Error: Invalid status '{status}'[/red]")
                        console.print(f"Valid statuses: {valid_statuses}")
                    raise typer.Exit(1)

            if priority is not None:
                if priority < -2 or priority > 2:
                    if json_output:
                        output_json(
                            {
                                "error": "ValidationError",
                                "message": "Priority must be between -2 and 2",
                            },
                            success=False,
                        )
                    else:
                        console.print(
                            "[red]Error: Priority must be between -2 and 2[/red]"
                        )
                    raise typer.Exit(1)
                updates_dict["priority"] = priority

            if assignee:
                # For now, treat assignee as owner_id (user ID)
                # TODO: Add proper user resolution when get_user endpoint is available
                updates_dict["owner_id"] = assignee

            if project:
                # For now, treat project as project_id (integer)
                # TODO: Add proper project resolution when get_project endpoint is available
                try:
                    updates_dict["project_id"] = int(project)
                except ValueError:
                    if json_output:
                        output_json(
                            {
                                "error": "ValidationError",
                                "message": f"Project must be a numeric ID (got '{project}')",
                            },
                            success=False,
                        )
                    else:
                        console.print(
                            f"[red]Error: Project must be a numeric ID (got '{project}')[/red]"
                        )
                    raise typer.Exit(1)

            if not updates_dict:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "No updates specified. Use --status, --priority, --assignee, or --project",
                        },
                        success=False,
                    )
                else:
                    console.print(
                        "[yellow]No updates specified. Use --status, --priority, --assignee, or --project[/yellow]"
                    )
                raise typer.Exit(0)

            # Show confirmation (unless --yes is passed or --json)
            if not json_output:
                console.print(f"\n[bold]Updating {len(identifiers)} tasks:[/bold]")
                console.print(f"Tasks: {', '.join(identifiers)}")
                for key, value in updates_dict.items():
                    console.print(f"  {key}: {value}")

                if not yes and not Confirm.ask("\nProceed with bulk update?"):
                    console.print("[yellow]Cancelled[/yellow]")
                    raise typer.Exit(0)

            # Create TaskUpdate
            updates = TaskUpdate(**updates_dict)

            # Execute bulk update
            if not json_output:
                console.print("\n[dim]Updating tasks...[/dim]")

            task_service = TaskService.from_config()
            result = await task_service.bulk_update_tasks(identifiers, updates)

            # Display results
            if json_output:
                output_json(
                    {
                        "updated": result.updated,
                        "succeeded": result.succeeded,
                        "failed": result.failed,
                        "total": result.total,
                        "results": [
                            {
                                "identifier": r.identifier,
                                "task_id": r.task_id,
                                "success": r.success,
                                "message": r.message,
                                "error": r.error,
                            }
                            for r in result.results
                        ],
                    }
                )
            else:
                console.print(
                    f"\n[green]✓ Successfully updated {result.succeeded or result.updated} tasks[/green]"
                )

                if result.failed and result.failed > 0:
                    console.print(
                        f"[red]✗ Failed to update {result.failed} tasks:[/red]"
                    )
                    for r in result.results:
                        if not r.success:
                            error_msg = r.error or "Unknown error"
                            console.print(f"  - {r.identifier}: {error_msg}")
                else:
                    console.print("[dim]All tasks updated successfully[/dim]")

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(bulk_update())
