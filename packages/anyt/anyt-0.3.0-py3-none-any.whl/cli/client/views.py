"""API client for task view operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime
from typing import Any, cast

from sdk.generated.api_config import APIConfig
from sdk.generated.models.TaskView import TaskView as GeneratedTaskView
from sdk.generated.models.TaskViewCreate import (
    TaskViewCreate as GeneratedTaskViewCreate,
)
from sdk.generated.models.TaskViewUpdate import (
    TaskViewUpdate as GeneratedTaskViewUpdate,
)
from sdk.generated.services.async_Task_Views_service import (  # pyright: ignore[reportMissingImports]
    create_task_view_v1_workspaces__workspace_id__task_views__post,
    delete_task_view_v1_workspaces__workspace_id__task_views__view_id__delete,
    get_default_task_view_v1_workspaces__workspace_id__task_views_default_get,
    get_task_view_v1_workspaces__workspace_id__task_views__view_id__get,
    list_task_views_v1_workspaces__workspace_id__task_views__get,
    update_task_view_v1_workspaces__workspace_id__task_views__view_id__patch,
)
from cli.models.view import TaskView, TaskViewCreate, TaskViewUpdate


class ViewsAPIClient:
    """API client for task view operations using generated OpenAPI client."""

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
    def from_config(cls) -> "ViewsAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            ViewsAPIClient instance
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

    def _convert_task_view_response(self, response: GeneratedTaskView) -> TaskView:
        """Convert generated TaskView to domain TaskView model."""
        return TaskView(
            id=response.id,
            name=response.name,
            workspace_id=response.workspace_id,
            user_id=response.user_id,
            filters=response.filters or {},
            is_default=response.is_default or False,
            created_at=datetime.fromisoformat(
                response.created_at.replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                response.updated_at.replace("Z", "+00:00")
            ),
        )

    async def list_task_views(self, workspace_id: int) -> list[TaskView]:
        """List task views in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of TaskView objects

        Raises:
            ValueError: If workspace_id is invalid
            APIError: On HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")

        # Call generated service function
        response = await list_task_views_v1_workspaces__workspace_id__task_views__get(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated responses to domain models
        response_data = cast(Any, response).data
        views = response_data if response_data else []
        return [self._convert_task_view_response(v) for v in views]

    async def create_task_view(
        self, workspace_id: int, view: TaskViewCreate
    ) -> TaskView:
        """Create a new task view in a workspace.

        Args:
            workspace_id: Workspace ID
            view: Task view creation data

        Returns:
            Created TaskView object

        Raises:
            ValueError: If workspace_id is invalid
            ValidationError: If view data is invalid
            ConflictError: If view name already exists
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")

        # Convert domain model to generated API request model
        # Note: workspace_id and user_id are required by generated model
        # but will be derived from URL path and auth token by backend
        request = GeneratedTaskViewCreate(
            name=view.name,
            filters=view.filters,
            is_default=view.is_default,
            workspace_id=workspace_id,
            user_id="",  # Will be derived from auth token by backend
        )

        # Call generated service function
        response = await create_task_view_v1_workspaces__workspace_id__task_views__post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_task_view_response(cast(Any, response).data)

    async def get_task_view(self, workspace_id: int, view_id: int) -> TaskView:
        """Get a specific task view by ID.

        Args:
            workspace_id: Workspace ID
            view_id: View ID

        Returns:
            TaskView object

        Raises:
            ValueError: If workspace_id or view_id is invalid
            NotFoundError: If view not found
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")
        if view_id <= 0:
            raise ValueError(f"Invalid view_id: {view_id}")

        # Call generated service function
        response = (
            await get_task_view_v1_workspaces__workspace_id__task_views__view_id__get(
                api_config_override=self._get_api_config(),
                workspace_id=workspace_id,
                view_id=view_id,
                X_API_Key=self.api_key,
                X_Test_User_Id=None,
            )
        )

        # Convert generated response to domain model
        return self._convert_task_view_response(cast(Any, response).data)

    async def get_task_view_by_name(
        self, workspace_id: int, name: str
    ) -> TaskView | None:
        """Get a task view by name.

        Args:
            workspace_id: Workspace ID
            name: View name

        Returns:
            TaskView object if found, None otherwise

        Raises:
            ValueError: If workspace_id is invalid
            APIError: On HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")

        try:
            # List all views and filter by name
            views = await self.list_task_views(workspace_id)
            for view in views:
                if view.name == name:
                    return view
            return None
        except Exception:
            return None

    async def get_default_task_view(self, workspace_id: int) -> TaskView | None:
        """Get the default task view for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Default TaskView object if found, None otherwise

        Raises:
            ValueError: If workspace_id is invalid
            APIError: On HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")

        try:
            # Call generated service function
            response = await get_default_task_view_v1_workspaces__workspace_id__task_views_default_get(
                api_config_override=self._get_api_config(),
                workspace_id=workspace_id,
                X_API_Key=self.api_key,
                X_Test_User_Id=None,
            )

            # Convert generated response to domain model
            return self._convert_task_view_response(cast(Any, response).data)
        except Exception:
            return None

    async def update_task_view(
        self, workspace_id: int, view_id: int, updates: TaskViewUpdate
    ) -> TaskView:
        """Update a task view.

        Args:
            workspace_id: Workspace ID
            view_id: View ID
            updates: Task view update data

        Returns:
            Updated TaskView object

        Raises:
            ValueError: If workspace_id or view_id is invalid
            NotFoundError: If view not found
            ValidationError: If update data is invalid
            ConflictError: If name already exists
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")
        if view_id <= 0:
            raise ValueError(f"Invalid view_id: {view_id}")

        # Convert domain model to generated API request model
        request = GeneratedTaskViewUpdate(
            name=updates.name,
            filters=updates.filters,
            is_default=updates.is_default,
        )

        # Call generated service function
        response = await update_task_view_v1_workspaces__workspace_id__task_views__view_id__patch(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            view_id=view_id,
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_task_view_response(cast(Any, response).data)

    async def delete_task_view(self, workspace_id: int, view_id: int) -> None:
        """Delete a task view.

        Args:
            workspace_id: Workspace ID
            view_id: View ID

        Raises:
            ValueError: If workspace_id or view_id is invalid
            NotFoundError: If view not found
            APIError: On other HTTP errors
        """
        if workspace_id <= 0:
            raise ValueError(f"Invalid workspace_id: {workspace_id}")
        if view_id <= 0:
            raise ValueError(f"Invalid view_id: {view_id}")

        # Call generated service function
        await delete_task_view_v1_workspaces__workspace_id__task_views__view_id__delete(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            view_id=view_id,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )
