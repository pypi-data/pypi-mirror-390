"""Task suggestion command - recommends tasks to work on next."""

import asyncio
from typing import Any

import typer
from typing_extensions import Annotated

from cli.client.tasks import TasksAPIClient

from .helpers import console, get_workspace_or_exit, output_json


def suggest_tasks(
    limit: Annotated[
        int,
        typer.Option("--limit", help="Number of suggestions to return"),
    ] = 10,
    status: Annotated[
        str,
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = "todo,backlog",
    include_assigned: Annotated[
        bool,
        typer.Option("--include-assigned", help="Include already-assigned tasks"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Suggest tasks to work on next based on priority and dependencies.

    Uses the backend's suggestion algorithm to recommend tasks that are ready
    to work on (all dependencies complete). Results are sorted by priority.

    By default, only shows unassigned tasks. Use --include-assigned to see
    tasks that are already assigned.
    """
    ws_config = get_workspace_or_exit()
    task_client = TasksAPIClient.from_config()

    async def run_suggestions() -> None:
        try:
            # Get suggestions from backend
            response = await task_client.suggest_tasks(
                workspace_id=int(ws_config.workspace_id),
                max_suggestions=min(limit, 50),  # Backend max is 50
                status=status,
                include_assigned=include_assigned,
            )

            if json_output:
                # JSON output
                output_data: dict[str, Any] = {
                    "suggestions": [
                        {
                            "identifier": s.task.identifier,
                            "title": s.task.title,
                            "priority": s.task.priority,
                            "status": s.task.status,
                            "is_ready": s.is_ready,
                            "blocked_by": s.blocked_by,
                            "blocks": s.blocks,
                        }
                        for s in response.suggestions
                    ],
                    "total_ready": response.total_ready,
                    "total_blocked": response.total_blocked,
                }
                output_json(output_data)
            else:
                # Pretty console output
                if not response.suggestions:
                    console.print("\n[yellow]No task suggestions available.[/yellow]")
                    if response.total_blocked > 0:
                        console.print(
                            f"[dim]({response.total_blocked} task{'s are' if response.total_blocked > 1 else ' is'} blocked by dependencies)[/dim]"
                        )
                    console.print(
                        "Try adjusting filters with --status or create new tasks.\n"
                    )
                    return

                console.print(
                    f"\n[cyan bold]Top {len(response.suggestions)} Recommended Task{'s' if len(response.suggestions) > 1 else ''}:[/cyan bold]\n"
                )

                for i, s in enumerate(response.suggestions, 1):
                    task = s.task
                    priority_val = task.priority if task.priority is not None else 0

                    console.print(
                        f"{i}. [bold cyan]{task.identifier}[/bold cyan] - {task.title} [dim][Priority: {priority_val}][/dim]"
                    )

                    # Show readiness info
                    if s.is_ready:
                        console.print("   [green]✓[/green] Ready to work on")

                    # Show what this task blocks
                    if s.blocks and len(s.blocks) > 0:
                        blocks_count = len(s.blocks)
                        console.print(
                            f"   [dim]Unblocks {blocks_count} task{'s' if blocks_count > 1 else ''}[/dim]"
                        )

                    console.print(f"   Status: [yellow]{task.status}[/yellow]\n")

                # Show summary stats
                console.print(
                    f"[dim]Total ready tasks: {response.total_ready} | Blocked: {response.total_blocked}[/dim]"
                )
                console.print(
                    "[dim]Run: anyt task pick <ID> to start working on a task[/dim]\n"
                )

        except Exception as e:
            if json_output:
                output_json({"error": "SuggestError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to generate suggestions: {e}")
            raise typer.Exit(1)

    asyncio.run(run_suggestions())
