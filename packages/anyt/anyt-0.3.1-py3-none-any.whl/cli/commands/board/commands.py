"""Board, timeline, summary, and graph visualization commands for AnyTask CLI."""

import asyncio
import json
from typing import Any, Optional

import typer
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table

from cli.services.task_service import TaskService
from cli.models.task import TaskFilters
from cli.models.common import Status
from cli.commands.task.helpers import (
    get_workspace_or_exit,
    format_priority,
    format_relative_time,
    truncate_text,
)
from cli.graph_renderer import render_ascii_graph, render_dot_graph, render_json_graph
from cli.client.workspaces import WorkspacesAPIClient
from cli.commands.board.grouping import (
    group_tasks_by_status,
    group_tasks_by_priority,
    group_tasks_by_owner,
    group_tasks_by_labels,
)
from cli.commands.board.rendering import (
    render_task_card,
    annotate_blocked_tasks_from_graph,
)
from cli.commands.board.graph_builder import build_workspace_dependency_graph

app = typer.Typer(help="Board and visualization commands")
console = Console()


@app.command("board")
def show_board(
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
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    group_by: Annotated[
        str,
        typer.Option("--group-by", help="Group by: status, priority, owner, labels"),
    ] = "status",
    sort: Annotated[
        str,
        typer.Option("--sort", help="Sort within groups: priority, updated_at"),
    ] = "priority",
    compact: Annotated[
        bool,
        typer.Option("--compact", help="Compact display mode"),
    ] = False,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Max tasks per lane"),
    ] = 20,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Display tasks in a Kanban board view."""
    ws_config = get_workspace_or_exit()
    task_service: TaskService = TaskService.from_config()
    workspaces_client: WorkspacesAPIClient = WorkspacesAPIClient.from_config()

    async def fetch_and_display() -> None:
        try:
            # Parse filters
            status_list = None
            if status:
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

            # Fetch all tasks
            filters = TaskFilters(
                workspace_id=int(ws_config.workspace_id),
                status=status_list,
                phase=phase,
                owner=owner_filter,
                labels=label_list,
                limit=100,  # API max is 100
                sort_by=sort,
                order="desc",
            )
            task_list = await task_service.list_tasks(filters)

            tasks = [task.model_dump() for task in task_list]

            if not tasks:
                if json_output:
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {"groups": {}, "total": 0},
                                "message": "No tasks found",
                            }
                        )
                    )
                else:
                    console.print("[yellow]No tasks found[/yellow]")
                    console.print(
                        "Create one with: [cyan]anyt task add 'Task title'[/cyan]"
                    )
                return

            # ✅ OPTIMIZED: Fetch dependency graph in single API call
            graph = await workspaces_client.get_dependency_graph(
                workspace_id=int(ws_config.workspace_id)
            )

            # Annotate tasks with blocked status using graph data (no additional API calls)
            annotate_blocked_tasks_from_graph(tasks, graph)

            # Group tasks based on group_by option
            if group_by == "status":
                groups = group_tasks_by_status(tasks)
                group_order = ["backlog", "active", "blocked", "done"]
                group_labels = {
                    "backlog": "Backlog",
                    "active": "Active",
                    "blocked": "Blocked",
                    "done": "Done",
                }
            elif group_by == "priority":
                groups = group_tasks_by_priority(tasks)
                group_order = ["highest", "high", "normal", "low", "lowest"]
                group_labels = {
                    "highest": "Highest (2)",
                    "high": "High (1)",
                    "normal": "Normal (0)",
                    "low": "Low (-1)",
                    "lowest": "Lowest (-2)",
                }
            elif group_by == "owner":
                groups = group_tasks_by_owner(tasks)
                # Sort groups: Unassigned first, then alphabetically by owner
                group_order = sorted(
                    groups.keys(), key=lambda x: (x != "Unassigned", x)
                )
                group_labels = {k: k for k in group_order}
            elif group_by == "labels":
                groups = group_tasks_by_labels(tasks)
                # Sort groups: No Labels first, then alphabetically
                group_order = sorted(groups.keys(), key=lambda x: (x != "No Labels", x))
                group_labels = {k: k for k in group_order}
            else:
                # Fallback to status grouping for unknown options
                if not json_output:
                    console.print(
                        f"[yellow]Unknown grouping '{group_by}', using status[/yellow]"
                    )
                groups = group_tasks_by_status(tasks)
                group_order = ["backlog", "active", "blocked", "done"]
                group_labels = {
                    "backlog": "Backlog",
                    "active": "Active",
                    "blocked": "Blocked",
                    "done": "Done",
                }

            # JSON output mode
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": True,
                            "data": {
                                "groups": groups,
                                "group_order": group_order,
                                "group_labels": group_labels,
                                "total": len(tasks),
                            },
                            "message": None,
                        }
                    )
                )
                return

            # Compact mode
            if compact:
                parts: list[str] = []
                for group_key in group_order:
                    group_tasks = groups.get(group_key, [])
                    count = len(group_tasks)
                    label = group_labels.get(group_key, group_key)
                    parts.append(f"{label}({count})")

                console.print(" | ".join(parts))
                return

            # Display header
            console.print()
            console.print("━" * 80)
            console.print(
                f"  [cyan bold]{ws_config.workspace_identifier} Board[/cyan bold]"
            )
            console.print("━" * 80)
            console.print()

            # Create table with columns for each lane
            table = Table(
                show_header=True, header_style="bold", box=None, padding=(0, 2)
            )

            for group_key in group_order:
                label = group_labels.get(group_key, group_key)
                group_tasks = groups.get(group_key, [])
                count = len(group_tasks)
                table.add_column(f"{label} ({count})", style="white", vertical="top")

            # Find max number of tasks in any lane
            max_tasks = max(len(groups.get(g, [])) for g in group_order)
            max_display = min(max_tasks, limit)

            # Build rows
            for i in range(max_display):
                row: list[str] = []
                for group_key in group_order:
                    group_tasks = groups.get(group_key, [])
                    if i < len(group_tasks):
                        task = group_tasks[i]
                        card_text = render_task_card(task, compact=False)
                        row.append(card_text)
                    else:
                        row.append("")

                table.add_row(*row)

            console.print(table)

            # Show totals and hints
            console.print()
            total_tasks = len(tasks)
            console.print(
                f"Showing {min(max_display, total_tasks)} of {total_tasks} tasks"
            )
            console.print()
            console.print("[dim]Commands:[/dim]")
            console.print(
                "  [cyan]anyt task pick <id>[/cyan]  - Pick a task to work on"
            )
            console.print("  [cyan]anyt task show <id>[/cyan]  - View task details")
            console.print("  [cyan]anyt board --mine[/cyan]    - Show only your tasks")
            console.print()

        except Exception as e:
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": f"Failed to load board: {str(e)}",
                            "message": str(e),
                        }
                    )
                )
            else:
                console.print(f"[red]Error:[/red] Failed to load board: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch_and_display())


@app.command("timeline")
def show_timeline(
    identifier: Annotated[
        str,
        typer.Argument(help="Task identifier (e.g., DEV-42)"),
    ],
    since: Annotated[
        Optional[str],
        typer.Option("--since", help="Show events since date (YYYY-MM-DD)"),
    ] = None,
    last: Annotated[
        Optional[str],
        typer.Option(
            "--last", help="Show events from last N hours/days (e.g., 24h, 7d)"
        ),
    ] = None,
    compact: Annotated[
        bool,
        typer.Option("--compact", help="Compact format"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Show chronological timeline of task events, attempts, and artifacts."""
    get_workspace_or_exit()  # Verify workspace and authentication
    task_service: TaskService = TaskService.from_config()

    async def fetch_and_display() -> None:
        try:
            # Fetch task details
            task = await task_service.get_task(identifier)
            task_id = task.identifier or str(task.id)
            title = task.title

            # Fetch events from API
            try:
                # Parse time filter
                since_param = None
                if since:
                    since_param = since
                elif last:
                    # Parse "24h", "7d" format
                    # For now, pass it to API as-is
                    since_param = last

                events = await task_service.tasks.get_task_events(
                    identifier=identifier,
                    event_type=None,  # Show all types unless filtered
                    since=since_param,
                    limit=100,
                )
            except Exception as e:
                # If events API not available, fall back to task metadata
                events = None
                if not json_output:
                    console.print(f"[yellow]Note:[/yellow] Could not fetch events: {e}")

            if json_output:
                # JSON output format
                if events:
                    # Use real events from API
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "task": {
                                        "identifier": task_id,
                                        "title": title,
                                    },
                                    "events": events,
                                },
                                "message": None,
                            }
                        )
                    )
                else:
                    # Fallback to task metadata
                    created_at = task.created_at
                    updated_at = task.updated_at
                    fallback_events: list[dict[str, Any]] = [
                        {
                            "type": "created",
                            "timestamp": created_at.isoformat() if created_at else None,
                            "status": task.status.value if task.status else "",
                            "priority": task.priority.value if task.priority else 0,
                            "labels": task.labels or [],
                        }
                    ]
                    if updated_at and created_at and updated_at != created_at:
                        fallback_events.append(
                            {
                                "type": "updated",
                                "timestamp": updated_at.isoformat(),
                            }
                        )
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "task": {
                                        "identifier": task_id,
                                        "title": title,
                                    },
                                    "events": fallback_events,
                                    "note": "Events API not available, showing basic task metadata",
                                },
                                "message": None,
                            }
                        )
                    )
            else:
                # Display header
                console.print()
                console.print("━" * 80)
                console.print(f"[cyan bold]{task_id}:[/cyan bold] {title} - Timeline")
                console.print("━" * 80)
                console.print()

                if events:
                    # Display events from API
                    for event in events:
                        event_type = event.get("type", "unknown")
                        timestamp = event.get("timestamp")
                        description = event.get("description", "")

                        # Format timestamp
                        time_str = format_relative_time(timestamp) if timestamp else ""
                        console.print(f"[dim]{time_str}[/dim]")

                        # Event icon and type
                        icon = {
                            "created": "📝",
                            "updated": "✏️",
                            "status_changed": "🔄",
                            "picked": "👤",
                            "dropped": "⏸️",
                            "completed": "✅",
                            "note_added": "💬",
                            "dependency_added": "🔗",
                            "dependency_removed": "❌",
                        }.get(event_type, "•")

                        console.print(
                            f"  {icon} {event_type.replace('_', ' ').title()}"
                        )

                        # Show description if available
                        if description:
                            console.print(f"     {description}")

                        # Show additional event data
                        for key, value in event.items():
                            if key not in ["type", "timestamp", "description", "id"]:
                                console.print(f"     {key}: {value}")

                        console.print()

                    console.print("━" * 80)
                    console.print(f"[dim]Total events: {len(events)}[/dim]")
                    console.print()
                else:
                    # Fallback: Show basic task metadata
                    created_at_str = (
                        task.created_at.isoformat() if task.created_at else None
                    )
                    console.print(f"[dim]{format_relative_time(created_at_str)}[/dim]")
                    console.print("  📝 Created")
                    status = task.status.value if task.status else ""
                    priority = task.priority.value if task.priority else 0
                    labels_list = task.labels or []
                    labels_str = ", ".join(labels_list) if labels_list else "none"
                    console.print(
                        f"     Status: [yellow]{status}[/yellow] • Priority: {priority} • Labels: {labels_str}"
                    )
                    console.print()

                    # Show last updated event
                    updated_at_str = (
                        task.updated_at.isoformat() if task.updated_at else None
                    )
                    if updated_at_str and updated_at_str != created_at_str:
                        console.print(
                            f"[dim]{format_relative_time(updated_at_str)}[/dim]"
                        )
                        console.print("  ✏️  Updated")
                        console.print()

                    console.print("━" * 80)
                    console.print(
                        "[dim]Events API integration ready, waiting for backend[/dim]"
                    )
                    console.print()

        except Exception as e:
            error_msg = str(e)
            if json_output:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Task not found"
                            if "404" in error_msg
                            else f"Failed to load timeline: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg:
                    console.print(f"[red]Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(f"[red]Error:[/red] Failed to load timeline: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch_and_display())


@app.command("summary")
def show_summary(
    period: Annotated[
        str,
        typer.Option("--period", help="Summary period: today, weekly, monthly"),
    ] = "today",
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    format_output: Annotated[
        str,
        typer.Option("--format", help="Output format: text, markdown, json"),
    ] = "text",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Generate workspace summary with done, active, blocked, and next priorities."""
    ws_config = get_workspace_or_exit()
    task_service: TaskService = TaskService.from_config()
    workspaces_client: WorkspacesAPIClient = WorkspacesAPIClient.from_config()

    async def fetch_and_display() -> None:
        try:
            # Fetch all tasks
            filters = TaskFilters(
                workspace_id=int(ws_config.workspace_id),
                phase=phase,
                limit=100,  # API max is 100
                sort_by="updated_at",
                order="desc",
            )
            task_list = await task_service.list_tasks(filters)

            tasks = [task.model_dump() for task in task_list]
            total = len(tasks)

            if not tasks:
                console.print("[yellow]No tasks in workspace[/yellow]")
                return

            # Group tasks by status
            done_tasks = [t for t in tasks if t.get("status") == "done"]
            active_tasks = [
                t for t in tasks if t.get("status") in ["inprogress", "active"]
            ]
            backlog_tasks = [t for t in tasks if t.get("status") in ["backlog", "todo"]]

            # ✅ OPTIMIZED: Fetch dependency graph in single API call
            graph = await workspaces_client.get_dependency_graph(
                workspace_id=int(ws_config.workspace_id)
            )

            # Annotate tasks with blocked status using graph data
            annotate_blocked_tasks_from_graph(tasks, graph)

            # Extract blocked tasks (those with blocked_by field)
            blocked_tasks = [t for t in tasks if "blocked_by" in t]

            # Check if JSON output is requested (via --json or --format json)
            use_json = json_output or format_output == "json"

            if use_json:
                # JSON output format
                high_priority_backlog = sorted(
                    backlog_tasks, key=lambda t: t.get("priority", 0), reverse=True
                )[:3]
                done_count = len(done_tasks)
                progress_pct = int((done_count / total) * 100) if total > 0 else 0
                print(
                    json.dumps(
                        {
                            "success": True,
                            "data": {
                                "period": period,
                                "done_tasks": done_tasks[:5],  # Show top 5
                                "active_tasks": active_tasks[:5],
                                "blocked_tasks": blocked_tasks,
                                "next_priorities": high_priority_backlog,
                                "summary": {
                                    "total": total,
                                    "done": len(done_tasks),
                                    "active": len(active_tasks),
                                    "backlog": len(backlog_tasks),
                                    "blocked": len(blocked_tasks),
                                    "progress_pct": progress_pct,
                                },
                            },
                            "message": None,
                        }
                    )
                )
                return

            # Display summary
            console.print()
            console.print("━" * 80)
            title_text = f"Workspace Summary - {period.capitalize()}"
            console.print(f"  [cyan bold]{title_text}[/cyan bold]")
            console.print("━" * 80)
            console.print()

            # Done section
            console.print(f"[green]✅ Done ({len(done_tasks)} tasks)[/green]")
            for task in done_tasks[:5]:  # Show top 5
                task_id = task.get("identifier", str(task.get("id", "")))
                title = truncate_text(task.get("title", ""), 60)
                console.print(f"   • {task_id} {title}")
            if len(done_tasks) > 5:
                console.print(f"   [dim]... and {len(done_tasks) - 5} more[/dim]")
            console.print()

            # Active section
            console.print(f"[yellow]🔄 Active ({len(active_tasks)} tasks)[/yellow]")
            for task in active_tasks[:5]:
                task_id = task.get("identifier", str(task.get("id", "")))
                title = truncate_text(task.get("title", ""), 50)
                owner_id = task.get("owner_id", "—")
                if owner_id:
                    owner_display = owner_id[:15] if len(owner_id) > 15 else owner_id
                else:
                    owner_display = "unassigned"
                updated = format_relative_time(task.get("updated_at"))
                console.print(f"   • {task_id} {title} ({owner_display}, {updated})")
            if len(active_tasks) > 5:
                console.print(f"   [dim]... and {len(active_tasks) - 5} more[/dim]")
            console.print()

            # Blocked section
            if blocked_tasks:
                console.print(f"[red]🚫 Blocked ({len(blocked_tasks)} tasks)[/red]")
                for task in blocked_tasks:
                    task_id = task.get("identifier", str(task.get("id", "")))
                    title = truncate_text(task.get("title", ""), 60)
                    console.print(f"   • {task_id} {title}")
                console.print()

            # Next priorities
            console.print("[bold]📅 Next Priorities[/bold]")
            # Show top priority backlog tasks
            high_priority_backlog = sorted(
                backlog_tasks, key=lambda t: t.get("priority", 0), reverse=True
            )[:3]

            for i, task in enumerate(high_priority_backlog, 1):
                task_id = task.get("identifier", str(task.get("id", "")))
                title = truncate_text(task.get("title", ""), 60)
                priority = format_priority(task.get("priority", 0))
                console.print(f"   {i}. {task_id} {title} {priority}")
            console.print()

            # Progress
            console.print("━" * 80)
            done_count = len(done_tasks)
            progress_pct = int((done_count / total) * 100) if total > 0 else 0
            console.print(
                f"Progress: {done_count}/{total} tasks complete ({progress_pct}%)"
            )
            console.print()

        except Exception as e:
            use_json = json_output or format_output == "json"
            if use_json:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": f"Failed to generate summary: {str(e)}",
                            "message": str(e),
                        }
                    )
                )
            else:
                console.print(f"[red]Error:[/red] Failed to generate summary: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch_and_display())


@app.command("graph")
def show_graph(
    identifier: Annotated[
        Optional[str],
        typer.Argument(
            help="Task identifier to show dependencies for (shows all if not specified)"
        ),
    ] = None,
    format_output: Annotated[
        str,
        typer.Option("--format", help="Output format: ascii, dot, json"),
    ] = "ascii",
    status: Annotated[
        Optional[str],
        typer.Option("--status", help="Filter by status (comma-separated)"),
    ] = None,
    priority_min: Annotated[
        Optional[int],
        typer.Option("--priority-min", help="Filter by minimum priority"),
    ] = None,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Filter by labels (comma-separated)"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Filter by phase/milestone"),
    ] = None,
    mine: Annotated[
        bool,
        typer.Option("--mine", help="Show only tasks assigned to you"),
    ] = False,
    depth: Annotated[
        Optional[int],
        typer.Option("--depth", help="Max dependency depth to show"),
    ] = None,
    compact: Annotated[
        bool,
        typer.Option("--compact", help="Compact display mode"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Visualize task dependencies as ASCII art or DOT format."""
    ws_config = get_workspace_or_exit()
    task_service: TaskService = TaskService.from_config()

    async def fetch_and_display() -> None:
        try:
            if identifier:
                # Show dependencies for specific task (existing behavior)
                task = await task_service.get_task(identifier)
                task_id = task.identifier or str(task.id)
                title = task.title

                # Fetch dependencies and dependents
                dependencies = await task_service.get_task_dependencies(identifier)
                dependents = await task_service.get_task_dependents(identifier)

                if json_output or format_output == "json":
                    # JSON output format
                    print(
                        json.dumps(
                            {
                                "success": True,
                                "data": {
                                    "task": {
                                        "identifier": task_id,
                                        "title": title,
                                        "status": task.status.value
                                        if task.status
                                        else "",
                                    },
                                    "dependencies": dependencies,
                                    "dependents": dependents,
                                },
                                "message": None,
                            }
                        )
                    )
                    return

                console.print()
                console.print("[bold]Task Dependency Graph[/bold]")
                console.print("━" * 80)
                console.print()

                # Show dependencies (what this depends on)
                if dependencies:
                    for dep in dependencies:
                        dep_id = dep.identifier or str(dep.id)
                        dep_title = truncate_text(dep.title, 40)
                        dep_status = dep.status.value if dep.status else ""
                        status_sym = "✓" if dep_status == "done" else "○"
                        console.print(f"        {dep_id} {status_sym}")
                        console.print(f"        {dep_title}")
                        console.print("          │")

                # Show current task
                console.print(f"        [cyan]{task_id}[/cyan] •")
                console.print(f"        {truncate_text(title, 40)}")
                task_status = task.status.value if task.status else ""
                console.print(f"        {task_status}")

                # Show dependents (what depends on this)
                if dependents:
                    console.print("          │")
                    for dept in dependents:
                        dept_id = dept.identifier or str(dept.id)
                        dept_title = truncate_text(dept.title, 40)
                        dept_status = dept.status.value if dept.status else ""
                        status_sym = "✓" if dept_status == "done" else "○"
                        console.print("          │")
                        console.print(f"        {dept_id} {status_sym}")
                        console.print(f"        {dept_title}")
                        console.print(f"        {dept_status}")

                console.print()
                console.print("Legend: ✓ done  • active  ○ backlog")
                console.print()

            else:
                # Full workspace dependency graph (NEW!)
                # Parse filters
                status_list = None
                if status:
                    status_list = [Status(s.strip()) for s in status.split(",")]

                label_list = None
                if labels:
                    label_list = [label.strip() for label in labels.split(",")]

                owner_filter = None
                if mine:
                    owner_filter = "me"

                # Build dependency graph
                graph = await build_workspace_dependency_graph(
                    task_service=task_service,
                    workspace_id=int(ws_config.workspace_id),
                    status_filter=status_list,
                    priority_min=priority_min,
                    labels_filter=label_list,
                    phase_filter=phase,
                    owner_filter=owner_filter,
                    max_depth=depth,
                )

                # Check if graph is empty
                if not graph.nodes:
                    if json_output or format_output == "json":
                        print(
                            json.dumps(
                                {
                                    "success": True,
                                    "data": {
                                        "nodes": [],
                                        "edges": [],
                                        "metadata": {
                                            "total_tasks": 0,
                                            "total_edges": 0,
                                        },
                                    },
                                    "message": "No tasks found in workspace",
                                }
                            )
                        )
                    else:
                        console.print("[yellow]No tasks found in workspace[/yellow]")
                        console.print(
                            "Create one with: [cyan]anyt task add 'Task title'[/cyan]"
                        )
                    return

                # Detect cycles
                cycles = graph.find_cycles()
                if cycles and not (json_output or format_output == "json"):
                    console.print(
                        f"[yellow]⚠ Warning: {len(cycles)} circular dependencies detected![/yellow]"
                    )
                    console.print()

                # Output based on format
                use_json = json_output or format_output == "json"

                if use_json:
                    # JSON output
                    data = render_json_graph(graph)
                    print(
                        json.dumps(
                            {"success": True, "data": data, "message": None}, indent=2
                        )
                    )

                elif format_output == "dot":
                    # DOT format output
                    dot_output = render_dot_graph(graph)
                    console.print(dot_output)

                else:
                    # ASCII art output (default)
                    console.print()
                    console.print("━" * 80)
                    console.print(
                        f"  [cyan bold]{ws_config.workspace_identifier} Dependency Graph[/cyan bold]"
                    )
                    console.print("━" * 80)
                    console.print()

                    ascii_graph = render_ascii_graph(graph, compact=compact)
                    console.print(ascii_graph)

                    console.print()
                    console.print("━" * 80)
                    console.print(
                        f"Total: {len(graph.nodes)} tasks, {len(graph.edges)} dependencies"
                    )
                    if cycles:
                        console.print(
                            f"[yellow]⚠ {len(cycles)} circular dependencies detected[/yellow]"
                        )
                    console.print()
                    console.print("[dim]Commands:[/dim]")
                    console.print(
                        "  [cyan]anyt graph <id>[/cyan]       - Show dependencies for specific task"
                    )
                    console.print(
                        "  [cyan]anyt graph --format dot[/cyan] - Output in DOT format for Graphviz"
                    )
                    console.print(
                        "  [cyan]anyt graph --json[/cyan]       - Output in JSON format"
                    )
                    console.print()

        except Exception as e:
            error_msg = str(e)
            use_json = json_output or format_output == "json"

            if use_json:
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": "Task not found"
                            if "404" in error_msg
                            else f"Failed to generate graph: {error_msg}",
                            "message": error_msg,
                        }
                    )
                )
            else:
                if "404" in error_msg and identifier:
                    console.print(f"[red]Error:[/red] Task '{identifier}' not found")
                else:
                    console.print(f"[red]Error:[/red] Failed to generate graph: {e}")
            raise typer.Exit(1)

    asyncio.run(fetch_and_display())
