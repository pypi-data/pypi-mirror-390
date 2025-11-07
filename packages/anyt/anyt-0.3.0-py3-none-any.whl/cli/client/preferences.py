"""API client for user preferences operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime
from typing import Any, cast

from sdk.generated.api_config import APIConfig
from sdk.generated.models.SetProjectRequest import SetProjectRequest
from sdk.generated.models.SetWorkspaceRequest import SetWorkspaceRequest
from sdk.generated.models.UserPreferencesResponse import UserPreferencesResponse
from sdk.generated.services.async_User_Preferences_service import (  # pyright: ignore[reportMissingImports]
    delete_user_preferences_v1_users_me_preferences_delete,
    get_user_preferences_v1_users_me_preferences_get,
    set_current_project_v1_users_me_preferences_project_put,
    set_current_workspace_v1_users_me_preferences_workspace_put,
)
from cli.models.user import UserPreferences


class PreferencesAPIClient:
    """API client for user preferences operations using generated OpenAPI client."""

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
    def from_config(cls) -> "PreferencesAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            PreferencesAPIClient instance
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
        if not self.auth_token:
            raise ValueError(
                "Authentication token not configured. "
                "Run 'anyt auth login' to authenticate."
            )
        return APIConfig(base_path=self.base_url, access_token=self.auth_token)

    def _convert_preferences_response(
        self, response: UserPreferencesResponse
    ) -> UserPreferences:
        """Convert generated UserPreferencesResponse to domain UserPreferences model."""
        # The generated model doesn't include updated_at, so we use current time
        # This is a limitation of the current API schema
        return UserPreferences(
            user_id=response.user_id,
            current_workspace_id=response.current_workspace_id,
            current_project_id=response.current_project_id,
            updated_at=datetime.now(),
        )

    async def get_user_preferences(self) -> UserPreferences | None:
        """Get user preferences (current workspace and project).

        Returns:
            UserPreferences object with current_workspace_id and current_project_id,
            or None if no preferences are set

        Raises:
            ValueError: If auth token not configured
            APIError: On HTTP errors
        """
        # Call generated service function
        response = await get_user_preferences_v1_users_me_preferences_get(
            api_config_override=self._get_api_config(),
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Handle None response case
        response_data = cast(Any, response).data
        if response_data is None:
            return None

        # Convert generated response to domain model
        return self._convert_preferences_response(response_data)

    async def set_current_workspace(self, workspace_id: int) -> UserPreferences:
        """Set the current workspace preference for the user.

        Args:
            workspace_id: The workspace ID to set as current

        Returns:
            Updated UserPreferences object

        Raises:
            ValueError: If auth token not configured or workspace_id is invalid
            NotFoundError: If workspace not found
            ValidationError: If workspace_id is invalid
            APIError: On other HTTP errors
        """
        # Validate workspace_id
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")

        # Convert to generated request model
        request = SetWorkspaceRequest(workspace_id=workspace_id)

        # Call generated service function
        response = await set_current_workspace_v1_users_me_preferences_workspace_put(
            api_config_override=self._get_api_config(),
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_preferences_response(cast(Any, response).data)

    async def set_current_project(
        self, workspace_id: int, project_id: int
    ) -> UserPreferences:
        """Set the current project (and workspace) preference for the user.

        Args:
            workspace_id: The workspace ID containing the project
            project_id: The project ID to set as current

        Returns:
            Updated UserPreferences object

        Raises:
            ValueError: If auth token not configured or IDs are invalid
            NotFoundError: If workspace or project not found
            ValidationError: If IDs are invalid
            APIError: On other HTTP errors
        """
        # Validate IDs
        if workspace_id <= 0:
            raise ValueError("workspace_id must be a positive integer")
        if project_id <= 0:
            raise ValueError("project_id must be a positive integer")

        # Convert to generated request model
        request = SetProjectRequest(workspace_id=workspace_id, project_id=project_id)

        # Call generated service function
        response = await set_current_project_v1_users_me_preferences_project_put(
            api_config_override=self._get_api_config(),
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_preferences_response(cast(Any, response).data)

    async def clear_user_preferences(self) -> None:
        """Clear user preferences (resets current workspace and project).

        Raises:
            ValueError: If auth token not configured
            APIError: On HTTP errors
        """
        # Call generated service function
        await delete_user_preferences_v1_users_me_preferences_delete(
            api_config_override=self._get_api_config(),
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )
