"""User domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class User(BaseModel):
    """User model."""

    id: str = Field(description="User ID")
    email: str = Field(description="User email")
    name: Optional[str] = Field(default=None, description="User display name")
    created_at: datetime = Field(description="Creation timestamp")


class UserPreferences(BaseModel):
    """User preferences model."""

    user_id: str = Field(description="User ID")
    current_workspace_id: Optional[int] = Field(
        default=None, description="Current workspace ID"
    )
    current_project_id: Optional[int] = Field(
        default=None, description="Current project ID"
    )
    updated_at: datetime = Field(description="Last update timestamp")


class UserInitResponse(BaseModel):
    """Response from POST /v1/users/init endpoint.

    This endpoint initializes a new user account with a default workspace
    and project. It is idempotent - safe to call multiple times.
    """

    user_id: str = Field(description="User ID")
    workspace_id: int = Field(description="Created/existing default workspace ID")
    workspace_name: str = Field(description="Workspace name")
    workspace_identifier: str = Field(description="Workspace identifier")
    project_id: int = Field(description="Created/existing default project ID")
    project_name: str = Field(description="Project name")
    is_new_user: bool = Field(
        description="True if this was a new user initialization, False if user already existed"
    )
