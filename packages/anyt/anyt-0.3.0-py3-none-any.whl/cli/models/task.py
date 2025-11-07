"""Task domain models for requests and filters.

Note: Task and TaskDependencyInfo response models have been moved to
src/cli/models/wrappers/task.py to use the wrapper pattern.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from cli.models.common import AssigneeType, Priority, Status


class TaskCreate(BaseModel):
    """Task creation payload."""

    title: str = Field(description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: Status = Field(default=Status.BACKLOG, description="Task status")
    priority: Priority = Field(default=Priority.NORMAL, description="Task priority")
    phase: Optional[str] = Field(default=None, description="Phase/milestone identifier")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    assignee_type: Optional[AssigneeType] = Field(
        default=AssigneeType.HUMAN, description="Assignee type: human or agent"
    )
    project_id: int = Field(description="Project ID")
    labels: list[str] = Field(default_factory=list, description="Task labels")
    estimate: Optional[int] = Field(default=None, description="Time estimate in hours")
    parent_id: Optional[int] = Field(default=None, description="Parent task ID")
    goal_id: Optional[int] = Field(default=None, description="Related goal ID")
    depends_on: Optional[list[str]] = Field(
        default=None, description="Task identifiers this task depends on"
    )

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API
    )


class TaskUpdate(BaseModel):
    """Task update payload."""

    title: Optional[str] = Field(default=None, description="Task title")
    description: Optional[str] = Field(default=None, description="Task description")
    status: Optional[Status] = Field(default=None, description="Task status")
    priority: Optional[Priority] = Field(default=None, description="Task priority")
    phase: Optional[str] = Field(default=None, description="Phase/milestone identifier")
    owner_id: Optional[str] = Field(default=None, description="Owner user ID")
    assignee_type: Optional[AssigneeType] = Field(
        default=None, description="Assignee type: human or agent"
    )
    project_id: Optional[int] = Field(default=None, description="Project ID")
    labels: Optional[list[str]] = Field(default=None, description="Task labels")
    estimate: Optional[int] = Field(default=None, description="Time estimate in hours")
    parent_id: Optional[int] = Field(default=None, description="Parent task ID")
    goal_id: Optional[int] = Field(default=None, description="Related goal ID")

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API
    )


class TaskFilters(BaseModel):
    """Task list query filters."""

    workspace_id: Optional[int] = Field(
        default=None, description="Filter by workspace ID"
    )
    project_id: Optional[int] = Field(default=None, description="Filter by project ID")
    status: Optional[list[Status]] = Field(
        default=None, description="Filter by status values"
    )
    phase: Optional[str] = Field(default=None, description="Filter by phase/milestone")
    owner: Optional[str] = Field(default=None, description="Filter by owner ID or 'me'")
    labels: Optional[list[str]] = Field(
        default=None, description="Filter by labels (AND logic)"
    )
    priority_gte: Optional[int] = Field(default=None, description="Minimum priority")
    priority_lte: Optional[int] = Field(default=None, description="Maximum priority")
    limit: int = Field(default=50, description="Items per page")
    offset: int = Field(default=0, description="Pagination offset")
    sort_by: str = Field(default="priority", description="Sort field")
    order: str = Field(default="desc", description="Sort order (asc/desc)")

    model_config = ConfigDict(
        use_enum_values=True  # Convert enums to values for API params
    )
