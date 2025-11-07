"""Goal and AI decomposition models."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Goal(BaseModel):
    """Goal model."""

    id: int = Field(description="Goal ID")
    title: str = Field(description="Goal title")
    description: str = Field(description="Goal description")
    workspace_id: int = Field(description="Workspace ID")
    created_at: datetime = Field(description="Creation timestamp")


class GoalDecomposition(BaseModel):
    """Result of goal decomposition."""

    goal_id: int = Field(description="Goal ID")
    tasks: list[dict[str, Any]] = Field(description="Decomposed tasks")
    dependencies: list[dict[str, Any]] = Field(
        default_factory=lambda: [], description="Task dependencies"
    )
    reasoning: Optional[str] = Field(default=None, description="AI reasoning")
    summary: Optional[str] = Field(default=None, description="Summary of decomposition")
    cost_tokens: Optional[int] = Field(default=None, description="Cost in tokens")
    cache_hit: Optional[bool] = Field(default=None, description="Whether cache was hit")
