"""Service context helpers for resolving workspace, project, and user context.

These helpers provide utilities for commands and services to resolve
context information like current workspace, project, or user preferences.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cli.config import WorkspaceConfig


class ServiceContext:
    """Context manager for service operations.

    Provides helper methods to resolve workspace, project, and other
    contextual information needed by services and commands.

    Uses the new config system that loads from:
    1. Environment variables (ANYT_API_KEY, ANYT_API_URL)
    2. Workspace config file (.anyt/anyt.json) if available

    Example:
        ```python
        context = ServiceContext.from_config()
        workspace_id = context.get_workspace_id()
        project_id = context.get_project_id()
        ```
    """

    def __init__(self) -> None:
        """Initialize ServiceContext.

        Loads workspace config (if available) for context resolution.
        """
        from cli.config import get_workspace_config_or_none

        self.workspace_config: "WorkspaceConfig | None" = get_workspace_config_or_none()

    @classmethod
    def from_config(cls) -> "ServiceContext":
        """Create context from configuration.

        The context will automatically load config from:
        1. Environment variables (ANYT_API_KEY, ANYT_API_URL)
        2. Workspace config file (.anyt/anyt.json) if available

        Returns:
            ServiceContext instance
        """
        return cls()

    def get_workspace_id(self) -> int | None:
        """Get workspace ID from config/context.

        Resolution order:
        1. Workspace config file (.anyt/anyt.json)
        2. None if not configured

        Returns:
            Workspace ID if available, None otherwise
        """
        if self.workspace_config and self.workspace_config.workspace_id:
            return self.workspace_config.workspace_id

        return None

    def get_project_id(self) -> int | None:
        """Get project ID from config/context.

        Resolution order:
        1. .anyt/anyt.json workspace config for current_project_id
        2. None if not configured

        Returns:
            Project ID if available, None otherwise
        """
        if self.workspace_config and self.workspace_config.current_project_id:
            return self.workspace_config.current_project_id

        return None

    def get_api_url(self) -> str:
        """Get API URL for current environment.

        Returns:
            API base URL from workspace config or ANYT_API_URL env var

        Raises:
            RuntimeError: If API URL is not configured
        """
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        api_url = api_config.get("api_url")
        if not api_url:
            raise RuntimeError("No API URL configured")
        return api_url

    def is_authenticated(self) -> bool:
        """Check if user is authenticated.

        Returns:
            True if ANYT_API_KEY environment variable is set
        """
        import os

        return bool(os.getenv("ANYT_API_KEY"))
