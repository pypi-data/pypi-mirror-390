"""Label domain models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Label(BaseModel):
    """Full label model."""

    id: int = Field(description="Label ID")
    name: str = Field(description="Label name")
    color: Optional[str] = Field(
        default=None, description="Hex color code (e.g., #FF0000)"
    )
    description: Optional[str] = Field(default=None, description="Label description")
    workspace_id: int = Field(description="Workspace ID")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")


class LabelCreate(BaseModel):
    """Label creation payload."""

    name: str = Field(description="Label name")
    color: Optional[str] = Field(default=None, description="Hex color code")
    description: Optional[str] = Field(default=None, description="Label description")


class LabelUpdate(BaseModel):
    """Label update payload."""

    name: Optional[str] = Field(default=None, description="Label name")
    color: Optional[str] = Field(default=None, description="Hex color code")
    description: Optional[str] = Field(default=None, description="Label description")
