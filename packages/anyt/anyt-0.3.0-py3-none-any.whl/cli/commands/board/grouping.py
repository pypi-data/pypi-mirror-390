"""Task grouping utilities for board visualization."""

from collections import defaultdict
from typing import Any


def group_tasks_by_status(
    tasks: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group tasks by status into Kanban lanes.

    Returns dict with keys: backlog, active, blocked, done
    """
    groups: dict[str, list[dict[str, Any]]] = {
        "backlog": [],
        "active": [],
        "blocked": [],
        "done": [],
    }

    for task in tasks:
        status = task.get("status", "backlog")

        # Map various statuses to our 4 lanes
        if status in ["backlog", "todo"]:
            groups["backlog"].append(task)
        elif status in ["inprogress", "active"]:
            groups["active"].append(task)
        elif status == "done":
            groups["done"].append(task)
        else:
            # Check if task has unmet dependencies (blocked)
            # For now, put other statuses in backlog
            groups["backlog"].append(task)

    return groups


def group_tasks_by_priority(
    tasks: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group tasks by priority level.

    Returns dict with keys: highest, high, normal, low, lowest
    """
    groups: dict[str, list[dict[str, Any]]] = {
        "highest": [],
        "high": [],
        "normal": [],
        "low": [],
        "lowest": [],
    }

    for task in tasks:
        priority = task.get("priority", 0)

        if priority >= 2:
            groups["highest"].append(task)
        elif priority == 1:
            groups["high"].append(task)
        elif priority == 0:
            groups["normal"].append(task)
        elif priority == -1:
            groups["low"].append(task)
        else:  # priority <= -2
            groups["lowest"].append(task)

    return groups


def group_tasks_by_owner(
    tasks: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group tasks by owner.

    Returns dict with owner IDs as keys, plus "Unassigned" for tasks without owners.
    """
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    for task in tasks:
        owner_id = task.get("owner_id")
        if owner_id:
            groups[str(owner_id)].append(task)
        else:
            groups["Unassigned"].append(task)

    return dict(groups)


def group_tasks_by_labels(
    tasks: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    """Group tasks by labels.

    A task can appear in multiple groups if it has multiple labels.
    Returns dict with label names as keys, plus "No Labels" for unlabeled tasks.
    """
    groups: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)

    for task in tasks:
        labels = task.get("labels", [])
        if labels:
            for label in labels:
                groups[str(label)].append(task)
        else:
            groups["No Labels"].append(task)

    return dict(groups)
