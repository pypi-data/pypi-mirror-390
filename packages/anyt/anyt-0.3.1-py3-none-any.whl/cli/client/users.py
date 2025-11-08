"""API client for user operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from typing import Any, cast

import httpx

from sdk.generated.api_config import APIConfig
from sdk.generated.models.UserPreferencesResponse import UserPreferencesResponse
from sdk.generated.models.UserSetupResponse_Output import UserSetupResponse_Output
from sdk.generated.services.async_User_Preferences_service import (  # pyright: ignore[reportMissingImports]
    get_user_preferences_v1_users_me_preferences_get,
)
from sdk.generated.services.async_Users_service import (  # pyright: ignore[reportMissingImports]
    init_user_v1_users_init_post,
)
from cli.models.user import User, UserInitResponse, UserPreferences


class UsersAPIClient:
    """API client for user operations using generated OpenAPI client.

    This client uses generated service functions where available and falls back
    to direct httpx calls for endpoints not yet in the generated code.
    """

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
    def from_config(cls) -> "UsersAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            UsersAPIClient instance
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

    def _convert_user_setup_response(
        self, response: UserSetupResponse_Output
    ) -> UserInitResponse:
        """Convert generated UserSetupResponse to domain UserInitResponse model."""
        return UserInitResponse(
            user_id=response.workspace.owner_id,
            workspace_id=response.workspace.id,
            workspace_name=response.workspace.name,
            workspace_identifier=response.workspace.identifier,
            project_id=response.project.id,
            project_name=response.project.name,
            is_new_user=response.is_new_setup,
        )

    def _convert_preferences_response(
        self, response: UserPreferencesResponse
    ) -> UserPreferences:
        """Convert generated UserPreferencesResponse to domain UserPreferences model."""
        # Import datetime here to avoid circular imports
        from datetime import datetime

        return UserPreferences(
            user_id=response.user_id,
            current_workspace_id=response.current_workspace_id,
            current_project_id=response.current_project_id,
            updated_at=datetime.now(),  # API doesn't return updated_at
        )

    async def init_user(self) -> UserInitResponse:
        """Initialize user account with default workspace and project.

        This endpoint is idempotent and should be called on first login or when
        the user has no workspaces. It creates:
        - A default "Personal" workspace
        - A default project in that workspace
        - Returns user, workspace, and project information

        If the user already has been initialized, returns existing data.

        Returns:
            UserInitResponse with user_id, workspace, and project details

        Raises:
            ValueError: If auth token not configured
            APIError: On HTTP errors
        """
        # Call generated service function
        response = await init_user_v1_users_init_post(
            api_config_override=self._get_api_config(),
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_user_setup_response(cast(Any, response).data)

    async def get_current_user(self) -> User:
        """Get current authenticated user information.

        NOTE: This endpoint is not yet in the generated OpenAPI client,
        so we use httpx directly.

        Returns:
            User object with id, email, name, created_at

        Raises:
            ValueError: If auth token or base URL not configured
            APIError: On HTTP errors
        """
        if not self.base_url:
            raise ValueError("API base URL not configured")
        if not self.auth_token:
            raise ValueError(
                "Authentication token not configured. "
                "Run 'anyt auth login' to authenticate."
            )

        # Build headers
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        # Make request
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get("/v1/users/me", headers=headers)

        # Handle errors
        if response.status_code != 200:
            raise Exception(
                f"get_current_user failed with status code: {response.status_code}"
            )

        # Parse and convert response
        data = response.json()
        return User(**data)

    async def get_user_preferences(self) -> UserPreferences:
        """Get current user's preferences.

        Returns:
            UserPreferences with workspace/project preferences

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
            # Return empty preferences if none exist
            from datetime import datetime

            return UserPreferences(
                user_id="",  # Will be set by backend
                current_workspace_id=None,
                current_project_id=None,
                updated_at=datetime.now(),
            )

        # Convert generated response to domain model
        return self._convert_preferences_response(response_data)

    async def update_user_preferences(
        self, preferences: dict[str, int | None]
    ) -> UserPreferences:
        """Update current user's preferences.

        NOTE: This endpoint (PATCH /v1/users/me/preferences) is not yet in
        the generated OpenAPI client, so we use httpx directly.

        Args:
            preferences: Dictionary with preference updates
                        (e.g., {"current_workspace_id": 123})

        Returns:
            Updated UserPreferences

        Raises:
            ValueError: If auth token or base URL not configured
            ValidationError: If preferences data is invalid
            APIError: On other HTTP errors
        """
        if not self.base_url:
            raise ValueError("API base URL not configured")
        if not self.auth_token:
            raise ValueError(
                "Authentication token not configured. "
                "Run 'anyt auth login' to authenticate."
            )

        # Build headers
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        # Make request
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.patch(
                "/v1/users/me/preferences", headers=headers, json=preferences
            )

        # Handle errors
        if response.status_code != 200:
            raise Exception(
                f"update_user_preferences failed with status code: {response.status_code}"
            )

        # Parse and convert response
        data = response.json()
        return UserPreferences(**data)
