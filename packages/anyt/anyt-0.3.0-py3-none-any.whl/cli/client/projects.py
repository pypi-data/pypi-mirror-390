"""API client for project operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from datetime import datetime
from typing import Any, cast

from sdk.generated.api_config import APIConfig
from sdk.generated.models.CreateProjectRequest import CreateProjectRequest
from sdk.generated.models.Project import Project as GeneratedProject
from sdk.generated.models.ProjectStatus import ProjectStatus as GeneratedProjectStatus
from sdk.generated.services.async_Projects_service import (  # pyright: ignore[reportMissingImports]
    create_project_v1_workspaces__workspace_id__projects__post,
    get_current_project_v1_workspaces__workspace_id__projects_current_get,
    list_projects_v1_workspaces__workspace_id__projects__get,
)
from cli.models.common import ProjectStatus
from cli.models.project import Project, ProjectCreate


class ProjectsAPIClient:
    """API client for project operations using generated OpenAPI client."""

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
    def from_config(cls) -> "ProjectsAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            ProjectsAPIClient instance
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

    def _convert_project_status_to_generated(
        self, status: ProjectStatus | str
    ) -> GeneratedProjectStatus:
        """Convert domain ProjectStatus enum or string to generated ProjectStatus."""
        if isinstance(status, ProjectStatus):
            return GeneratedProjectStatus(status.value)
        return GeneratedProjectStatus(status)

    def _convert_project_status_to_domain(
        self, status: str | None
    ) -> ProjectStatus | None:
        """Convert generated project_status string to domain ProjectStatus enum."""
        if not status:
            return None
        status_map = {
            "active": ProjectStatus.ACTIVE,
            "paused": ProjectStatus.PAUSED,
            "completed": ProjectStatus.COMPLETED,
            "canceled": ProjectStatus.CANCELED,
        }
        return status_map.get(status.lower(), ProjectStatus.ACTIVE)

    def _convert_project_response(self, response: GeneratedProject) -> Project:
        """Convert generated Project to domain Project model."""
        return Project(
            id=response.id,
            name=response.name,
            description=response.description,
            status=self._convert_project_status_to_domain(response.status),
            lead_id=response.lead_id,
            start_date=datetime.fromisoformat(
                response.start_date.replace("Z", "+00:00")
            )
            if response.start_date
            else None,
            target_date=datetime.fromisoformat(
                response.target_date.replace("Z", "+00:00")
            )
            if response.target_date
            else None,
            color=response.color,
            icon=response.icon,
            workspace_id=response.workspace_id,
            created_at=datetime.fromisoformat(
                response.created_at.replace("Z", "+00:00")
            ),
            updated_at=datetime.fromisoformat(
                response.updated_at.replace("Z", "+00:00")
            ),
            deleted_at=datetime.fromisoformat(
                response.deleted_at.replace("Z", "+00:00")
            )
            if response.deleted_at
            else None,
        )

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
        # Call generated service function
        response = await list_projects_v1_workspaces__workspace_id__projects__get(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            status=None,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated responses to domain models
        response_data = cast(Any, response).data
        projects = response_data.items if response_data else []
        return [self._convert_project_response(p) for p in projects]

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
        # Validate required fields
        if not project.name:
            raise ValueError("Project name is required")

        # Convert domain model to generated API request model
        request = CreateProjectRequest(
            name=project.name,
            description=project.description,
            status=self._convert_project_status_to_generated(project.status)
            if project.status
            else None,
            lead_id=project.lead_id,
            start_date=project.start_date,
            target_date=project.target_date,
            color=project.color,
            icon=project.icon,
        )

        # Call generated service function
        response = await create_project_v1_workspaces__workspace_id__projects__post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_project_response(cast(Any, response).data)

    async def get_current_project(self, workspace_id: int) -> Project:
        """Get the current/default project for a workspace.

        Returns the user's preferred project from preferences (if it belongs to the workspace),
        or first project by creation date if no preference is set.

        Args:
            workspace_id: The workspace ID

        Returns:
            Project object

        Raises:
            NotFoundError: If workspace has no projects or workspace not found
            APIError: On other HTTP errors
        """
        # Call generated service function
        response = (
            await get_current_project_v1_workspaces__workspace_id__projects_current_get(
                api_config_override=self._get_api_config(),
                workspace_id=workspace_id,
                X_API_Key=self.api_key,
                X_Test_User_Id=None,
            )
        )

        # Convert generated response to domain model
        return self._convert_project_response(cast(Any, response).data)
