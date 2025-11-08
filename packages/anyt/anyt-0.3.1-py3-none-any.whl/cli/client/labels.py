"""API client for label operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime
from typing import Any, cast

from sdk.generated.api_config import APIConfig
from sdk.generated.models.Label import Label as GeneratedLabel
from sdk.generated.models.LabelCreate import LabelCreate as GeneratedLabelCreate
from sdk.generated.models.LabelUpdate import LabelUpdate as GeneratedLabelUpdate
from sdk.generated.services.async_Labels_service import (  # pyright: ignore[reportMissingImports]
    create_label_v1_workspaces__workspace_id__labels__post,
    delete_label_v1_workspaces__workspace_id__labels__label_id__delete,
    get_label_v1_workspaces__workspace_id__labels__label_id__get,
    list_labels_v1_workspaces__workspace_id__labels__get,
    update_label_v1_workspaces__workspace_id__labels__label_id__patch,
)
from cli.models.label import Label, LabelCreate, LabelUpdate


class LabelsAPIClient:
    """API client for label operations using generated OpenAPI client."""

    def __init__(
        self,
        base_url: str | None = None,
        auth_token: str | None = None,
        api_key: str | None = None,
    ):
        """Initialize with API configuration.

        Args:
            base_url: Base URL for the API
            auth_token: Optional JWT auth token
            api_key: Optional API key
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.api_key = api_key

    @classmethod
    def from_config(cls) -> "LabelsAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            LabelsAPIClient instance
        """
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        return cls(
            base_url=api_config.get("api_url"),
            auth_token=api_config.get("auth_token"),
            api_key=api_config.get("api_key"),
        )

    def _get_api_config(self) -> APIConfig:
        """Get APIConfig for generated client calls."""
        if not self.base_url:
            raise ValueError("API base URL not configured")
        return APIConfig(base_path=self.base_url, access_token=self.auth_token)

    def _convert_label_response(self, response: GeneratedLabel) -> Label:
        """Convert generated Label to domain Label model."""
        return Label(
            id=response.id,
            name=response.name,
            color=response.color,
            description=response.description,
            workspace_id=response.workspace_id,
            created_at=datetime.fromisoformat(
                response.created_at.replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                response.updated_at.replace("Z", "+00:00")
            )
            if response.updated_at
            else datetime.fromisoformat(response.created_at.replace("Z", "+00:00")),
        )

    async def list_labels(self, workspace_id: int) -> list[Label]:
        """List labels in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of Label objects

        Raises:
            ValueError: If workspace_id is invalid or api_key is not configured
            APIError: On HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")

        if not self.api_key:
            raise ValueError(
                "API key not configured. "
                "Set ANYT_API_KEY environment variable to configure API authentication."
            )

        # Call generated service function
        response = await list_labels_v1_workspaces__workspace_id__labels__get(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated responses to domain models
        response_data = cast(Any, response).data
        labels = response_data if response_data else []
        return [self._convert_label_response(label) for label in labels]

    async def create_label(self, workspace_id: int, label: LabelCreate) -> Label:
        """Create a new label in a workspace.

        Args:
            workspace_id: Workspace ID
            label: Label creation data

        Returns:
            Created Label object

        Raises:
            ValueError: If workspace_id is invalid or api_key is not configured
            ValidationError: If label data is invalid
            ConflictError: If label name already exists
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")

        if not self.api_key:
            raise ValueError(
                "API key not configured. "
                "Set ANYT_API_KEY environment variable to configure API authentication."
            )

        # Convert domain model to generated API request model
        request = GeneratedLabelCreate(
            name=label.name,
            color=label.color,
            description=label.description,
            workspace_id=workspace_id,
        )

        # Call generated service function
        response = await create_label_v1_workspaces__workspace_id__labels__post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_label_response(cast(Any, response).data)

    async def get_label(self, workspace_id: int, label_id: int) -> Label:
        """Get a specific label by ID.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID

        Returns:
            Label object

        Raises:
            ValueError: If workspace_id or label_id is invalid or api_key is not configured
            NotFoundError: If label not found
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")

        if label_id <= 0:
            raise ValueError("label_id must be a positive integer")

        if not self.api_key:
            raise ValueError(
                "API key not configured. "
                "Set ANYT_API_KEY environment variable to configure API authentication."
            )

        # Call generated service function
        response = await get_label_v1_workspaces__workspace_id__labels__label_id__get(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            label_id=label_id,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_label_response(cast(Any, response).data)

    async def update_label(
        self, workspace_id: int, label_id: int, updates: LabelUpdate
    ) -> Label:
        """Update a label.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID
            updates: Label update data

        Returns:
            Updated Label object

        Raises:
            ValueError: If workspace_id or label_id is invalid or api_key is not configured
            NotFoundError: If label not found
            ValidationError: If update data is invalid
            ConflictError: If name already exists
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")

        if label_id <= 0:
            raise ValueError("label_id must be a positive integer")

        if not self.api_key:
            raise ValueError(
                "API key not configured. "
                "Set ANYT_API_KEY environment variable to configure API authentication."
            )

        # Convert domain model to generated API request model
        request = GeneratedLabelUpdate(
            name=updates.name,
            color=updates.color,
            description=updates.description,
        )

        # Call generated service function
        response = (
            await update_label_v1_workspaces__workspace_id__labels__label_id__patch(
                api_config_override=self._get_api_config(),
                workspace_id=workspace_id,
                label_id=label_id,
                data=request,
                X_API_Key=self.api_key,
                X_Test_User_Id=None,
            )
        )

        # Convert generated response to domain model
        return self._convert_label_response(cast(Any, response).data)

    async def delete_label(self, workspace_id: int, label_id: int) -> None:
        """Delete a label.

        Args:
            workspace_id: Workspace ID
            label_id: Label ID

        Raises:
            ValueError: If workspace_id or label_id is invalid or api_key is not configured
            NotFoundError: If label not found
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")

        if label_id <= 0:
            raise ValueError("label_id must be a positive integer")

        if not self.api_key:
            raise ValueError(
                "API key not configured. "
                "Set ANYT_API_KEY environment variable to configure API authentication."
            )

        # Call generated service function
        await delete_label_v1_workspaces__workspace_id__labels__label_id__delete(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            label_id=label_id,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )
