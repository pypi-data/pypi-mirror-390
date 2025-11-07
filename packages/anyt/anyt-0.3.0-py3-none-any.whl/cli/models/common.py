"""Common types and enums used across the CLI."""

from enum import Enum


class Status(str, Enum):
    """Task status values.

    Note: Values must match backend API exactly.
    Backend uses: backlog, todo, inprogress, blocked, canceled, done, archived
    """

    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "inprogress"  # Backend uses no underscore
    BLOCKED = "blocked"
    CANCELED = "canceled"  # Backend uses single 'l'
    DONE = "done"
    ARCHIVED = "archived"  # Tasks that are archived


class Priority(int, Enum):
    """Task priority values."""

    LOWEST = -2
    LOW = -1
    NORMAL = 0
    HIGH = 1
    HIGHEST = 2


class AssigneeType(str, Enum):
    """Assignee type for tasks.

    Note: Values must match backend API exactly.
    """

    HUMAN = "human"
    AGENT = "agent"


class ProjectStatus(str, Enum):
    """Project status values.

    Note: Values must match backend API exactly.
    """

    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELED = "canceled"
