"""Update commands for tasks (edit, mark done, add note)."""

import asyncio
from datetime import datetime
from typing import Any, Optional

import typer
from rich.prompt import Prompt
from typing_extensions import Annotated

from cli.config import ActiveTaskConfig
from cli.models.common import Priority, Status
from cli.models.task import TaskUpdate
from cli.models.wrappers.task import Task
from cli.services.task_service import TaskService

from ..helpers import (
    console,
    get_active_task_id,
    get_workspace_or_exit,
    normalize_identifier,
    resolve_task_identifier,
    output_json,
)


def edit_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier (e.g., DEV-42, t_1Z for UID) or ID. Uses active task if not specified."
        ),
    ] = None,
    title: Annotated[
        Optional[str],
        typer.Option("--title", help="New title"),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="New description"),
    ] = None,
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="New status"),
    ] = None,
    priority: Annotated[
        Optional[int],
        typer.Option("-p", "--priority", help="New priority (-2 to 2)"),
    ] = None,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Comma-separated labels (replaces all labels)"),
    ] = None,
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="New owner ID"),
    ] = None,
    estimate: Annotated[
        Optional[int],
        typer.Option("--estimate", help="New time estimate in hours"),
    ] = None,
    ids: Annotated[
        Optional[str],
        typer.Option("--ids", help="Multiple task IDs to edit (comma-separated)"),
    ] = None,
    if_match: Annotated[
        Optional[int],
        typer.Option(
            "--if-match", help="Expected version for optimistic concurrency control"
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview changes without applying"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Edit a task's fields."""
    ws_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config()

    # Get workspace identifier for task ID normalization
    workspace_identifier = ws_config.workspace_identifier

    # Determine task identifiers to edit (bulk or single)
    # Store raw identifiers - they will be resolved in the async function
    task_identifiers = []
    if ids:
        # Bulk edit mode
        task_identifiers = [tid.strip() for tid in ids.split(",")]
    elif identifier:
        # Single task by identifier
        task_identifiers = [identifier]
    else:
        # Use active task
        active_id = get_active_task_id()
        if not active_id:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task edit DEV-42 --status done",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print(
                    "Specify a task: [cyan]anyt task edit DEV-42 --status done[/cyan]"
                )
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)
        task_identifiers = [active_id]

    # Validate priority if provided
    if priority is not None and (priority < -2 or priority > 2):
        if json_output:
            output_json(
                {
                    "error": "ValidationError",
                    "message": "Invalid priority value",
                    "details": "Priority must be between -2 and 2",
                },
                success=False,
            )
        else:
            console.print("[red]✗ Error:[/red] Invalid priority value")
            console.print("  Priority must be between -2 and 2")
        raise typer.Exit(1)

    async def update() -> None:
        try:
            # Parse labels
            label_list = None
            if labels is not None:
                label_list = [label.strip() for label in labels.split(",")]

            # Convert priority and status to enums if provided
            priority_enum = None
            if priority is not None:
                priority_enum = Priority(priority)

            status_enum = None
            if status is not None:
                status_enum = Status(status)

            # Track results for bulk operations
            updated_tasks: list[Task] = []
            errors: list[dict[str, Any]] = []

            # Resolve all identifiers (converts UIDs to workspace identifiers)
            resolved_ids = []
            for raw_id in task_identifiers:
                try:
                    resolved = await resolve_task_identifier(
                        raw_id, service, workspace_identifier
                    )
                    resolved_ids.append(resolved)
                except Exception as e:
                    # If resolution fails, add error and skip this task
                    error_msg = str(e)
                    if json_output:
                        errors.append(
                            {
                                "task_id": raw_id,
                                "error": "ResolutionError",
                                "message": f"Failed to resolve identifier: {error_msg}",
                            }
                        )
                    else:
                        console.print(
                            f"[red]✗ Error:[/red] Failed to resolve identifier '{raw_id}': {error_msg}"
                        )
                    continue

            # Update each task
            for task_id in resolved_ids:
                try:
                    # Fetch current task for dry-run or version checking
                    current_task = await service.get_task(task_id)

                    # Check version if --if-match provided
                    if if_match is not None:
                        if current_task.version != if_match:
                            if json_output:
                                errors.append(
                                    {
                                        "task_id": task_id,
                                        "error": "VersionConflict",
                                        "message": "Task was modified by another user",
                                        "current_version": current_task.version,
                                        "provided_version": if_match,
                                    }
                                )
                            else:
                                console.print(
                                    f"[red]✗ Error:[/red] Task {task_id} was modified by another user"
                                )
                                console.print(
                                    f"  Current version: {current_task.version}"
                                )
                                console.print(f"  Your version: {if_match}")
                                console.print()
                                console.print(
                                    f"  Fetch latest with: [cyan]anyt task show {task_id}[/cyan]"
                                )
                            continue

                    # Dry-run mode: show preview
                    if dry_run:
                        if not json_output:
                            console.print(
                                f"[yellow][Preview][/yellow] Would update {task_id}:"
                            )
                            if title is not None:
                                console.print(
                                    f"  title: {current_task.title} → {title}"
                                )
                            if description is not None:
                                console.print("  description: <updated>")
                            if status is not None:
                                console.print(
                                    f"  status: {current_task.status.value if isinstance(current_task.status, Status) else current_task.status} → {status}"
                                )
                            if priority is not None:
                                console.print(
                                    f"  priority: {current_task.priority.value if isinstance(current_task.priority, Priority) else current_task.priority} → {priority}"
                                )
                            if labels is not None:
                                console.print(
                                    f"  labels: {current_task.labels} → {label_list}"
                                )
                            if owner is not None:
                                console.print(
                                    f"  owner: {current_task.owner_id} → {owner}"
                                )
                            if estimate is not None:
                                console.print(
                                    f"  estimate: {current_task.estimate} → {estimate}"
                                )
                            console.print(
                                f"  updated_at: {current_task.updated_at} → <now>"
                            )
                            console.print()
                        continue

                    # Create update model
                    task_update = TaskUpdate(
                        title=title,
                        description=description,
                        status=status_enum,
                        priority=priority_enum,
                        owner_id=owner,
                        labels=label_list,
                        estimate=estimate,
                    )

                    # Actually update the task
                    updated_task = await service.update_task(task_id, task_update)
                    updated_tasks.append(updated_task)

                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "NotFound",
                                "message": f"Task '{task_id}' not found",
                            }
                        )
                    elif "409" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "Conflict",
                                "message": "Version conflict - task was modified by someone else",
                            }
                        )
                    else:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "UpdateError",
                                "message": str(e),
                            }
                        )

            # Output results
            if json_output:
                if dry_run:
                    changes_source: dict[str, Any] = {
                        "title": title,
                        "description": description,
                        "status": status,
                        "priority": priority,
                        "labels": label_list,
                        "owner_id": owner,
                        "estimate": estimate,
                    }
                    changes_dict: dict[str, Any] = {
                        k: v for k, v in changes_source.items() if v is not None
                    }
                    output_json(
                        {
                            "dry_run": True,
                            "task_ids": resolved_ids,
                            "changes": changes_dict,
                        }
                    )
                else:
                    output_json(
                        {
                            "updated": [
                                t.model_dump(mode="json") for t in updated_tasks
                            ],
                            "errors": errors,
                        }
                    )
            else:
                if dry_run:
                    console.print()
                    console.print("Run without --dry-run to apply changes")
                else:
                    # Show success for updated tasks
                    if len(updated_tasks) == 1:
                        console.print(
                            f"[green]✓[/green] Updated {updated_tasks[0].identifier}"
                        )
                    elif len(updated_tasks) > 1:
                        console.print(
                            f"[green]✓[/green] Updated {len(updated_tasks)} tasks"
                        )

                    # Show errors
                    if errors:
                        console.print()
                        for error in errors:
                            console.print(
                                f"[red]✗[/red] {error['task_id']}: {error['message']}"
                            )

            # Exit with error if all failed
            if not dry_run and len(updated_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to update task: {e}")
            raise typer.Exit(1)

    asyncio.run(update())


def mark_done(
    identifiers: Annotated[
        Optional[list[str]],
        typer.Argument(
            help="Task identifier(s) (e.g., DEV-42 DEV-43). Uses active task if not specified."
        ),
    ] = None,
    note: Annotated[
        Optional[str],
        typer.Option("--note", "-n", help="Add a completion note to the task"),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Mark one or more tasks as done.

    Optionally add a completion note to the task's Events section.
    """
    ws_config = get_workspace_or_exit()
    service: TaskService = TaskService.from_config()

    # Get workspace identifier for task ID normalization
    workspace_identifier = ws_config.workspace_identifier

    # Determine task IDs
    task_ids = []
    clear_active = False

    if identifiers:
        # Normalize each identifier
        task_ids = [
            normalize_identifier(tid, workspace_identifier) for tid in identifiers
        ]
    else:
        # Use active task
        active_id = get_active_task_id()
        if not active_id:
            if json_output:
                output_json(
                    {
                        "error": "ValidationError",
                        "message": "No task identifier provided and no active task set",
                        "suggestions": [
                            "Specify a task: anyt task done DEV-42",
                            "Or pick a task first: anyt task pick DEV-42",
                        ],
                    },
                    success=False,
                )
            else:
                console.print(
                    "[red]Error:[/red] No task identifier provided and no active task set"
                )
                console.print("Specify a task: [cyan]anyt task done DEV-42[/cyan]")
                console.print(
                    "Or pick a task first: [cyan]anyt task pick DEV-42[/cyan]"
                )
            raise typer.Exit(1)
        task_ids = [normalize_identifier(active_id, workspace_identifier)]
        clear_active = True

    async def update() -> None:
        try:
            updated_tasks: list[Task] = []
            errors: list[dict[str, Any]] = []

            # Mark each task as done
            for task_id in task_ids:
                try:
                    # If note is provided, fetch task to append note to description
                    description_update = None
                    if note:
                        task_data = await service.get_task(task_id)
                        current_description = task_data.description or ""
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                        note_text = f"\n### {timestamp} - Completed\n- {note}\n"

                        if "## Events" in current_description:
                            description_update = current_description + note_text
                        else:
                            description_update = (
                                current_description + f"\n## Events\n{note_text}"
                            )

                    # Update task status and description using typed model
                    if description_update:
                        task_update = TaskUpdate(
                            status=Status.DONE,
                            description=description_update,
                        )
                        task = await service.update_task(task_id, task_update)
                    else:
                        task_update = TaskUpdate(status=Status.DONE)
                        task = await service.update_task(task_id, task_update)

                    updated_tasks.append(task)
                except Exception as e:
                    error_msg = str(e)
                    if "404" in error_msg:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "NotFound",
                                "message": f"Task '{task_id}' not found",
                            }
                        )
                    else:
                        errors.append(
                            {
                                "task_id": task_id,
                                "error": "UpdateError",
                                "message": str(e),
                            }
                        )

            # Output results
            if json_output:
                output_json(
                    {
                        "updated": [t.model_dump(mode="json") for t in updated_tasks],
                        "errors": errors,
                    }
                )
            else:
                # Show success
                if len(updated_tasks) == 1:
                    console.print(
                        f"[green]✓[/green] Marked {updated_tasks[0].identifier} as done"
                    )
                elif len(updated_tasks) > 1:
                    console.print(
                        f"[green]✓[/green] Marked {len(updated_tasks)} tasks as done"
                    )

                # Clear active task if applicable
                if clear_active and len(updated_tasks) > 0:
                    ActiveTaskConfig.clear()
                    console.print("[dim]Cleared active task[/dim]")

                # Show errors
                if errors:
                    console.print()
                    for error in errors:
                        console.print(
                            f"[red]✗[/red] {error['task_id']}: {error['message']}"
                        )

            # Exit with error if all failed
            if len(updated_tasks) == 0 and len(errors) > 0:
                raise typer.Exit(1)

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to mark task(s) as done: {e}")
            raise typer.Exit(1)

    asyncio.run(update())


def add_note_to_task(
    identifier: Annotated[
        Optional[str],
        typer.Argument(help="Task identifier (e.g., DEV-42) or use active task"),
    ] = None,
    message: Annotated[
        str,
        typer.Option("--message", "-m", help="Note message to append"),
    ] = "",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Add a timestamped note/event to a task's description.

    DEPRECATED: Use 'anyt comment add' instead for better structure and timestamps.

    The note will be appended to the Events section of the task description
    with a timestamp.
    """
    # Show deprecation warning
    if not json_output:
        console.print(
            "[yellow]Warning:[/yellow] 'anyt task note' is deprecated. "
            "Use [cyan]anyt comment add[/cyan] instead."
        )
        console.print("[dim]This command will be removed in a future release.[/dim]\n")

    ws_config = get_workspace_or_exit()
    task_service: TaskService = TaskService.from_config()

    async def add_note() -> None:
        try:
            # Get task identifier
            task_id = identifier
            if not task_id:
                task_id = get_active_task_id()
                if not task_id:
                    if json_output:
                        output_json(
                            {
                                "error": "NoActiveTask",
                                "message": "No active task set",
                                "hint": "Specify task identifier or run 'anyt task pick'",
                            },
                            success=False,
                        )
                    else:
                        console.print("[red]Error:[/red] No active task set")
                        console.print(
                            "Specify task identifier or run [cyan]anyt task pick[/cyan]"
                        )
                    raise typer.Exit(1)

            # Normalize identifier
            task_id = normalize_identifier(task_id, ws_config.workspace_identifier)

            # Get current task to retrieve description
            task = await task_service.get_task(task_id)
            current_description = task.description or ""

            # Get message from parameter or prompt
            note_message = message
            if not note_message:
                if json_output:
                    console.print("[red]Error:[/red] Message is required")
                    raise typer.Exit(1)
                note_message = Prompt.ask("[cyan]Note message[/cyan]")
                if not note_message:
                    console.print("[yellow]Cancelled[/yellow]")
                    raise typer.Exit(0)

            # Create timestamped note
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            note = f"\n### {timestamp} - Note\n- {note_message}\n"

            # Append note to description
            # If description has an Events section, append there
            # Otherwise, create Events section and append
            if "## Events" in current_description:
                new_description = current_description + note
            else:
                new_description = current_description + f"\n## Events\n{note}"

            # Update task with new description
            updates = TaskUpdate(description=new_description)
            updated_task = await task_service.update_task(
                identifier=task_id,
                updates=updates,
            )

            # Display success
            if json_output:
                output_json(updated_task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green]✓[/green] Note added to [cyan]{updated_task.identifier}[/cyan]"
                )
                console.print(f"  {note_message}")

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "UpdateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to add note: {e}")
            raise typer.Exit(1)

    asyncio.run(add_note())
