"""Preference service with business logic for user preference operations."""

from cli.client.preferences import PreferencesAPIClient
from cli.models.user import UserPreferences
from cli.services.base import BaseService


class PreferenceService(BaseService):
    """Business logic for user preference operations.

    PreferenceService encapsulates business rules and workflows for user
    preferences management, including:
    - Getting current workspace and project preferences
    - Setting current workspace
    - Setting current project
    - Clearing preferences

    Example:
        ```python
        service = PreferenceService.from_config()

        # Get user preferences
        prefs = await service.get_user_preferences()

        # Set current workspace
        prefs = await service.set_current_workspace(workspace_id=123)

        # Set current project
        prefs = await service.set_current_project(
            workspace_id=123,
            project_id=456
        )
        ```
    """

    preferences: PreferencesAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.preferences = PreferencesAPIClient.from_config()

    async def get_user_preferences(self) -> UserPreferences | None:
        """Get user preferences.

        Returns:
            UserPreferences object with current workspace and project, or None

        Raises:
            APIError: On HTTP errors
        """
        return await self.preferences.get_user_preferences()

    async def set_current_workspace(self, workspace_id: int) -> UserPreferences:
        """Set the current workspace preference.

        Args:
            workspace_id: Workspace ID to set as current

        Returns:
            Updated UserPreferences object

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        return await self.preferences.set_current_workspace(workspace_id)

    async def set_current_project(
        self, workspace_id: int, project_id: int
    ) -> UserPreferences:
        """Set the current project preference.

        Args:
            workspace_id: Workspace ID containing the project
            project_id: Project ID to set as current

        Returns:
            Updated UserPreferences object

        Raises:
            NotFoundError: If workspace or project not found
            APIError: On other HTTP errors
        """
        return await self.preferences.set_current_project(workspace_id, project_id)

    async def clear_user_preferences(self) -> None:
        """Clear user preferences.

        Raises:
            APIError: On HTTP errors
        """
        await self.preferences.clear_user_preferences()
