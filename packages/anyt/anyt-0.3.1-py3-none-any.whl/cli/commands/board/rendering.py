"""Task rendering utilities for board visualization."""

from typing import Any

from cli.commands.task.helpers import format_relative_time, truncate_text
from cli.models.wrappers.dependency_graph import DependencyGraphResponse


def annotate_blocked_tasks_from_graph(
    tasks: list[dict[str, Any]], graph: DependencyGraphResponse
) -> None:
    """Annotate tasks with blocked status using dependency graph data.

    This function modifies tasks in-place, adding "blocked_by" field to blocked tasks.
    Uses pre-fetched dependency graph data instead of N+1 API calls.

    Args:
        tasks: List of tasks to annotate (modified in-place)
        graph: Complete dependency graph with all tasks and dependencies
    """
    # Get set of blocked task IDs from graph
    blocked_ids = graph.get_blocked_tasks()

    # Annotate each task
    for task in tasks:
        identifier = task.get("identifier", str(task.get("id")))

        if identifier in blocked_ids:
            # Task is blocked - get blocking tasks
            blocking_nodes = graph.get_blocking_tasks(identifier)

            # Convert nodes to dict format for display
            task["blocked_by"] = [
                {
                    "identifier": node.id,
                    "title": node.title,
                    "status": node.status,
                    "priority": node.priority,
                }
                for node in blocking_nodes
            ]


def render_task_card(task: dict[str, Any], compact: bool = False) -> str:
    """Render a task as a card for the board."""
    task_id = task.get("identifier", str(task.get("id", "")))
    title = task.get("title", "")
    owner_id = task.get("owner_id")
    updated_at = task.get("updated_at")
    status = task.get("status", "")
    is_blocked = "blocked_by" in task

    # Add status indicator
    status_icon = ""
    if is_blocked:
        status_icon = "⚠️ "
    elif status == "done":
        status_icon = "✅ "
    elif status in ["inprogress", "active"]:
        status_icon = "🔄 "
    elif status in ["backlog", "todo"]:
        status_icon = "⏸️ "

    if compact:
        # Compact format: "icon T-42 Title"
        return f"{status_icon}{task_id} {truncate_text(title, 30)}"
    else:
        # Multi-line card format
        lines = [f"{status_icon}{task_id} {truncate_text(title, 35)}"]

        # Owner info
        if owner_id:
            owner_display = owner_id[:10] if len(owner_id) > 10 else owner_id
            lines.append(f"     {owner_display} • {format_relative_time(updated_at)}")
        else:
            lines.append(f"     — • {format_relative_time(updated_at)}")

        # Show blocked indicator with dependency count
        if is_blocked:
            blocked_by = task.get("blocked_by", [])
            lines.append(f"     ⚠️ Blocked by {len(blocked_by)} task(s)")

        return "\n".join(lines)
