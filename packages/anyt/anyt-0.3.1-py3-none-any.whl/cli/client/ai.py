"""API client for AI-powered operations."""

# pyright: reportUnknownVariableType=false, reportUnknownMemberType=false

from typing import Any, cast
import httpx

from sdk.generated.api_config import APIConfig
from sdk.generated.models.CreateGoalRequest import CreateGoalRequest
from sdk.generated.models.DecompositionRequest import DecompositionRequest
from sdk.generated.models.OrganizeRequest import OrganizeRequest
from sdk.generated.models.AutoFillRequest import AutoFillRequest
from sdk.generated.models.SummaryRequest import SummaryRequest
from sdk.generated.models.SummaryPeriod import SummaryPeriod
from sdk.generated.services.async_Goals_service import (  # pyright: ignore[reportMissingImports]
    create_goal_v1_workspaces__workspace_id__goals__post,
    decompose_goal_v1_workspaces__workspace_id__goals__goal_id__decompose_post,
)
from sdk.generated.services.async_Organizer_service import (  # pyright: ignore[reportMissingImports]
    organize_workspace_v1_workspaces__workspace_id__organize__post,
    create_summary_v1_workspaces__workspace_id__organize_summaries_post,
)
from sdk.generated.services.async_Tasks_service import (  # pyright: ignore[reportMissingImports]
    auto_fill_task_v1_workspaces__workspace_id__tasks__task_identifier__auto_fill_post,
)
from cli.models.ai import (
    AIUsage,
    AISuggestions,
    OrganizationResult,
    TaskAutoFill,
    TaskReview,
    WorkspaceSummary,
)
from cli.models.goal import GoalDecomposition


class AIAPIClient:
    """API client for AI-powered operations using generated OpenAPI client."""

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
    def from_config(cls) -> "AIAPIClient":
        """Create client from configuration.

        Uses get_effective_api_config() to get API URL and key from
        workspace config or environment variables.

        Returns:
            AIAPIClient instance
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

    def _convert_decomposition_response(self, response: Any) -> GoalDecomposition:
        """Convert generated DecompositionResponse to domain GoalDecomposition model."""
        data = response.data
        return GoalDecomposition(
            goal_id=data.goal_id,
            tasks=data.tasks,
            dependencies=data.dependencies if hasattr(data, "dependencies") else [],
            reasoning=data.reasoning if hasattr(data, "reasoning") else "",
        )

    def _convert_organization_response(self, response: Any) -> OrganizationResult:
        """Convert generated OrganizeResponse to domain OrganizationResult model."""
        data = response.data
        return OrganizationResult(
            changes=data.changes if hasattr(data, "changes") else [],
            summary=data.summary if hasattr(data, "summary") else "",
        )

    def _convert_auto_fill_response(self, response: Any) -> TaskAutoFill:
        """Convert generated AutoFillResponse to domain TaskAutoFill model."""
        data = response.data
        return TaskAutoFill(
            identifier=data.identifier,
            filled_fields=data.filled_fields,
            reasoning=data.reasoning if hasattr(data, "reasoning") else "",
        )

    def _convert_summary_response(self, response: Any) -> WorkspaceSummary:
        """Convert generated SummaryResponse to domain WorkspaceSummary model."""
        data = response.data
        return WorkspaceSummary(
            period=data.period,
            activity_breakdown=data.activity_breakdown
            if hasattr(data, "activity_breakdown")
            else {},
            insights=data.insights if hasattr(data, "insights") else [],
            summary_text=data.summary_text if hasattr(data, "summary_text") else "",
        )

    async def decompose_goal(
        self,
        goal: str,
        workspace_id: int,
        max_tasks: int = 10,
        task_size: int = 4,
        project_id: int | None = None,
    ) -> GoalDecomposition:
        """Decompose a goal into actionable tasks using AI.

        Args:
            goal: The goal description
            workspace_id: The workspace ID
            max_tasks: Maximum number of tasks to generate
            task_size: Preferred task size in hours
            project_id: Optional project ID to associate the goal with (defaults to 1)

        Returns:
            GoalDecomposition object with tasks and dependencies

        Raises:
            ValueError: If workspace_id is not provided
            APIError: On HTTP errors
        """
        # Validate workspace_id is provided
        if not workspace_id:
            raise ValueError(
                "Workspace ID is required for goal decomposition. "
                "Ensure workspace context is set."
            )

        # First create a goal using generated service
        # Note: CreateGoalRequest requires project_id, using default of 1 if not provided
        create_request = CreateGoalRequest(
            title=goal,
            description=goal,
            project_id=project_id or 1,
        )

        goal_response = await create_goal_v1_workspaces__workspace_id__goals__post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            data=create_request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Extract goal ID from response
        goal_data = cast(Any, goal_response).data
        goal_id: int = goal_data.id

        # Then decompose it using generated service
        decompose_request = DecompositionRequest(
            max_tasks=max_tasks,
            max_depth=2,
            task_size_hours=task_size,
        )

        decompose_response = await decompose_goal_v1_workspaces__workspace_id__goals__goal_id__decompose_post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            goal_id=goal_id,
            data=decompose_request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_decomposition_response(decompose_response)

    async def organize_workspace(
        self, workspace_id: int, actions: list[str], dry_run: bool = False
    ) -> OrganizationResult:
        """Organize workspace tasks using AI.

        Args:
            workspace_id: The workspace ID
            actions: List of actions to perform (e.g., ["normalize_titles", "suggest_labels"])
            dry_run: If True, preview changes without applying them

        Returns:
            OrganizationResult with changes and suggestions

        Raises:
            ValueError: If workspace_id is not provided
            APIError: On HTTP errors
        """
        # Validate workspace_id is provided
        if not workspace_id:
            raise ValueError(
                "Workspace ID is required for workspace organization. "
                "Ensure workspace context is set."
            )

        # Convert domain model to generated API request model
        request = OrganizeRequest(
            actions=actions,
            dry_run=dry_run,
        )

        # Call generated service function
        response = await organize_workspace_v1_workspaces__workspace_id__organize__post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_organization_response(response)

    async def fill_task_details(
        self, identifier: str, workspace_id: int, fields: list[str] | None = None
    ) -> TaskAutoFill:
        """Auto-fill missing details for a task using AI.

        Args:
            identifier: Task identifier (e.g., DEV-42)
            workspace_id: Workspace ID containing the task
            fields: List of fields to fill (e.g., ["description", "acceptance", "labels"])

        Returns:
            TaskAutoFill object with generated content

        Raises:
            ValueError: If workspace_id is not provided
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Validate workspace_id is provided
        if not workspace_id:
            raise ValueError(
                "Workspace ID is required for task auto-fill. "
                "Ensure workspace context is set."
            )

        # Convert domain model to generated API request model
        request = AutoFillRequest(
            fields=fields or [],
        )

        # Call generated service function
        response = await auto_fill_task_v1_workspaces__workspace_id__tasks__task_identifier__auto_fill_post(
            api_config_override=self._get_api_config(),
            workspace_id=workspace_id,
            task_identifier=identifier,
            data=request,
            X_API_Key=self.api_key,
            X_Test_User_Id=None,
        )

        # Convert generated response to domain model
        return self._convert_auto_fill_response(response)

    async def generate_summary(
        self, workspace_id: int, period: str = "daily"
    ) -> WorkspaceSummary:
        """Generate workspace progress summary.

        Args:
            workspace_id: The workspace ID
            period: Summary period (daily, weekly, monthly)

        Returns:
            WorkspaceSummary with activity breakdown and insights

        Raises:
            ValueError: If workspace_id is not provided or period is invalid
            APIError: On HTTP errors
        """
        # Validate workspace_id is provided
        if not workspace_id:
            raise ValueError(
                "Workspace ID is required for summary generation. "
                "Ensure workspace context is set."
            )

        # Map period string to SummaryPeriod enum
        # Note: Original implementation used "today", but generated API uses "daily"
        period_mapping = {
            "today": SummaryPeriod.DAILY,
            "daily": SummaryPeriod.DAILY,
            "weekly": SummaryPeriod.WEEKLY,
            "monthly": SummaryPeriod.MONTHLY,
        }

        summary_period = period_mapping.get(period.lower())
        if not summary_period:
            raise ValueError(
                f"Invalid period: {period}. Must be one of: daily, weekly, monthly, or today (alias for daily)"
            )

        # Convert domain model to generated API request model
        request = SummaryRequest(
            period=summary_period,
            include_sections=["all"],
        )

        # Call generated service function
        response = (
            await create_summary_v1_workspaces__workspace_id__organize_summaries_post(
                api_config_override=self._get_api_config(),
                workspace_id=workspace_id,
                data=request,
                X_API_Key=self.api_key,
                X_Test_User_Id=None,
            )
        )

        # Convert generated response to domain model
        return self._convert_summary_response(response)

    # Methods below are not yet available in generated services
    # Using direct HTTP calls as a temporary solution

    async def _http_get(self, url: str) -> dict[str, Any]:
        """Make a direct HTTP GET request."""
        if not self.base_url:
            raise ValueError("API base URL not configured")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            result = response.json()
            # Unwrap the response if it has a 'data' field
            if isinstance(result, dict) and "data" in result:
                return cast(dict[str, Any], result["data"])
            return cast(dict[str, Any], result)

    async def _http_post(
        self, url: str, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a direct HTTP POST request."""
        if not self.base_url:
            raise ValueError("API base URL not configured")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(url, headers=headers, json=json)
            response.raise_for_status()
            result = response.json()
            # Unwrap the response if it has a 'data' field
            if isinstance(result, dict) and "data" in result:
                return cast(dict[str, Any], result["data"])
            return cast(dict[str, Any], result)

    async def get_ai_suggestions(self, workspace_id: int) -> AISuggestions:
        """Get AI-powered suggestions for next tasks to work on.

        NOTE: This endpoint is not yet available in generated OpenAPI services.
        Using direct HTTP call as a temporary solution.

        Args:
            workspace_id: The workspace ID

        Returns:
            AISuggestions with recommended tasks and reasoning

        Raises:
            ValueError: If workspace_id is not provided
            APIError: On HTTP errors
        """
        # Validate workspace_id is provided
        if not workspace_id:
            raise ValueError(
                "Workspace ID is required for AI suggestions. "
                "Ensure workspace context is set."
            )

        data = await self._http_get(f"/v1/workspaces/{workspace_id}/suggestions")
        return AISuggestions(**data)

    async def review_task(self, identifier: str) -> TaskReview:
        """Get AI review of a task before marking done.

        NOTE: This endpoint is not yet available in generated OpenAPI services.
        Using direct HTTP call as a temporary solution.

        Args:
            identifier: Task identifier (e.g., DEV-42)

        Returns:
            TaskReview with checks, warnings, and readiness status

        Raises:
            ValueError: If identifier is not provided
            NotFoundError: If task not found
            APIError: On other HTTP errors
        """
        # Validate identifier is provided
        if not identifier:
            raise ValueError("Task identifier is required for task review.")

        data = await self._http_post(f"/v1/tasks/{identifier}/review")
        return TaskReview(**data)

    async def get_ai_usage(self, workspace_id: int | None = None) -> AIUsage:
        """Get AI usage statistics and costs.

        NOTE: This endpoint is not yet available in generated OpenAPI services.
        Using direct HTTP call as a temporary solution.

        Args:
            workspace_id: Optional workspace ID for workspace-level stats

        Returns:
            AIUsage statistics with token counts and costs

        Raises:
            APIError: On HTTP errors
        """
        if workspace_id:
            url = f"/v1/workspaces/{workspace_id}/ai-usage"
        else:
            url = "/v1/ai-usage"

        data = await self._http_get(url)
        return AIUsage(**data)
