"""View service with business logic for task view operations."""

from cli.client.views import ViewsAPIClient
from cli.models.view import TaskView, TaskViewCreate, TaskViewUpdate
from cli.services.base import BaseService


class ViewService(BaseService):
    """Business logic for task view operations.

    ViewService encapsulates business rules and workflows for task view
    management, including:
    - Listing task views in a workspace
    - Creating, updating, and deleting views
    - Managing default views
    - View filter validation

    Example:
        ```python
        service = ViewService.from_config()

        # List views in workspace
        views = await service.list_task_views(workspace_id=123)

        # Create a new view
        view = await service.create_task_view(
            workspace_id=123,
            view=TaskViewCreate(
                name="My Tasks",
                filters={"status": ["todo", "inprogress"]},
                is_default=True
            )
        )

        # Get default view
        default_view = await service.get_default_task_view(workspace_id=123)
        ```
    """

    views: ViewsAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.views = ViewsAPIClient.from_config()

    async def list_task_views(self, workspace_id: int) -> list[TaskView]:
        """List task views in a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            List of TaskView objects

        Raises:
            APIError: On HTTP errors
        """
        return await self.views.list_task_views(workspace_id)

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
            ValidationError: If view data is invalid
            ConflictError: If view name already exists
            APIError: On other HTTP errors
        """
        return await self.views.create_task_view(workspace_id, view)

    async def get_task_view(self, workspace_id: int, view_id: int) -> TaskView:
        """Get a specific task view by ID.

        Args:
            workspace_id: Workspace ID
            view_id: View ID

        Returns:
            TaskView object

        Raises:
            NotFoundError: If view not found
            APIError: On other HTTP errors
        """
        return await self.views.get_task_view(workspace_id, view_id)

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
            APIError: On HTTP errors
        """
        return await self.views.get_task_view_by_name(workspace_id, name)

    async def get_default_task_view(self, workspace_id: int) -> TaskView | None:
        """Get the default task view for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Default TaskView object if found, None otherwise

        Raises:
            APIError: On HTTP errors
        """
        return await self.views.get_default_task_view(workspace_id)

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
            NotFoundError: If view not found
            ValidationError: If update data is invalid
            ConflictError: If name already exists
            APIError: On other HTTP errors
        """
        return await self.views.update_task_view(workspace_id, view_id, updates)

    async def delete_task_view(self, workspace_id: int, view_id: int) -> None:
        """Delete a task view.

        Args:
            workspace_id: Workspace ID
            view_id: View ID

        Raises:
            NotFoundError: If view not found
            APIError: On other HTTP errors
        """
        await self.views.delete_task_view(workspace_id, view_id)
