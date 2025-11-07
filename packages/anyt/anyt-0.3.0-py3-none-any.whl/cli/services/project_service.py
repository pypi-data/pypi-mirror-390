"""Project service with business logic for project operations."""

from cli.client.exceptions import NotFoundError
from cli.client.projects import ProjectsAPIClient
from cli.models.project import Project, ProjectCreate
from cli.services.base import BaseService


class ProjectService(BaseService):
    """Business logic for project operations.

    ProjectService encapsulates business rules and workflows for project
    management, including:
    - Listing projects in a workspace
    - Creating new projects
    - Getting or creating default project
    - Project validation and context resolution

    Example:
        ```python
        service = ProjectService.from_config()

        # List projects in workspace
        projects = await service.list_projects(workspace_id=123)

        # Get or create default project
        project = await service.get_or_create_default_project(workspace_id=123)

        # Create a new project
        project = await service.create_project(
            workspace_id=123,
            project=ProjectCreate(name="API")
        )
        ```
    """

    projects: ProjectsAPIClient

    def _init_clients(self) -> None:
        """Initialize API clients."""
        self.projects = ProjectsAPIClient.from_config()

    async def list_projects(self, workspace_id: int) -> list[Project]:
        """List all projects in a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            List of Project objects

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        return await self.projects.list_projects(workspace_id)

    async def create_project(
        self, workspace_id: int, project: ProjectCreate
    ) -> Project:
        """Create a new project in a workspace.

        Args:
            workspace_id: The workspace ID
            project: Project creation data

        Returns:
            Created Project object

        Raises:
            NotFoundError: If workspace not found
            ValidationError: If project data is invalid
            ConflictError: If identifier already exists
            APIError: On other HTTP errors
        """
        return await self.projects.create_project(workspace_id, project)

    async def get_current_project(self, workspace_id: int) -> Project:
        """Get the current/default project for a workspace.

        Args:
            workspace_id: The workspace ID

        Returns:
            Project object

        Raises:
            NotFoundError: If workspace not found
            APIError: On other HTTP errors
        """
        return await self.projects.get_current_project(workspace_id)

    async def get_or_create_default_project(
        self, workspace_id: int, workspace_name: str = "Default"
    ) -> Project:
        """Get current project or create a default one if none exists.

        Business logic:
        1. Try to get current project
        2. If not found, create a default project named after the workspace
        3. Return the project

        Args:
            workspace_id: The workspace ID
            workspace_name: Workspace name for default project naming

        Returns:
            Current or newly created Project object

        Raises:
            APIError: If creation fails
        """
        try:
            return await self.projects.get_current_project(workspace_id)
        except NotFoundError:
            # Create default project
            default_project = ProjectCreate(
                name=f"{workspace_name} Project",
                description="Default project",
            )
            return await self.projects.create_project(workspace_id, default_project)
