"""
Task coordinator - main worker loop that polls for tasks and executes workflows.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from rich.console import Console
from rich.table import Table

from cli.client.comments import CommentsAPIClient
from cli.client.tasks import TasksAPIClient
from cli.models.common import Status
from cli.models.wrappers.task import Task
from cli.services.task_service import TaskService

from .cache import CacheManager
from .executor.core import WorkflowExecutor
from .models import Workflow

console = Console()


class TaskCoordinator:
    """
    Coordinates task polling and workflow execution.

    Similar to the bash script but with:
    - Smart polling with exponential backoff
    - Workflow-based execution
    - Better error handling
    - Structured logging
    """

    def __init__(
        self,
        workspace_dir: Path,
        workflows_dir: Optional[Path] = None,
        workflow_file: Optional[Path] = None,
        poll_interval: int = 5,
        max_backoff: int = 60,
        agent_id: str | None = None,
        project_id: int | None = None,
    ):
        """
        Initialize task coordinator.

        Args:
            workspace_dir: Working directory for task execution
            workflows_dir: Directory containing workflow definitions
            workflow_file: Specific workflow file to run (if specified, runs ONLY this workflow)
            poll_interval: Base polling interval in seconds
            max_backoff: Maximum backoff interval in seconds
            agent_id: Agent ID to filter task suggestions
            project_id: Optional project ID to scope suggestions to a specific project
        """
        self.workspace_dir = workspace_dir
        self.workflows_dir = workflows_dir or workspace_dir / ".anyt" / "workflows"
        self.workflow_file = workflow_file
        self.poll_interval = poll_interval
        self.max_backoff = max_backoff
        self.agent_id = agent_id
        self.project_id = project_id
        self.current_backoff: float = float(poll_interval)

        # Load API key and workspace_id from config if available
        self.api_key = self._load_api_key()
        self.workspace_id = self._load_workspace_id()

        # Initialize components
        self.cache_manager = CacheManager()

        # workspace_id is required for WorkflowExecutor
        if self.workspace_id is None:
            raise RuntimeError(
                "workspace_id is required for worker operation. "
                "Please ensure workspace config exists at .anyt/anyt.json"
            )

        self.executor = WorkflowExecutor(
            workspace_id=self.workspace_id,
            cache_manager=self.cache_manager,
            api_key=self.api_key,
        )
        self.task_client = TasksAPIClient.from_config()
        self.task_service: TaskService = TaskService.from_config()
        self.comments_client = CommentsAPIClient.from_config()

        # Load workflows
        self.workflows: Dict[str, Workflow] = {}
        self._load_workflows()

        # Log agent and project filter if configured
        if self.agent_id:
            console.print(f"[dim]Agent filter: {self.agent_id}[/dim]")
        if self.project_id:
            console.print(f"[dim]Project filter: {self.project_id}[/dim]")

        # Statistics
        self.stats: Dict[str, Any] = {
            "tasks_processed": 0,
            "tasks_succeeded": 0,
            "tasks_failed": 0,
            "started_at": datetime.now(),
        }

    def _fix_yaml_boolean_keys(self, data: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Fix YAML boolean key issue.

        YAML interprets 'on:' as boolean True. This function converts
        the boolean key back to the string 'on' for Pydantic model compatibility.

        Args:
            data: YAML parsed data (may contain boolean keys)

        Returns:
            Fixed data dict with string keys only
        """
        # Convert boolean keys to strings (YAML quirk: 'on:' becomes True)
        if True in data:
            data["on"] = data.pop(True)
        if False in data:
            data["off"] = data.pop(False)
        return data

    def _load_api_key(self) -> Optional[str]:
        """
        Load API key from config if available.

        Returns:
            API key string if available, None otherwise
        """
        try:
            from cli.config import get_effective_api_config

            api_config = get_effective_api_config()
            return api_config.get("api_key")
        except Exception:
            # No API key available
            return None

    def _load_workspace_id(self) -> Optional[int]:
        """
        Load workspace_id from workspace config if available.

        Returns:
            Workspace ID integer if available, None otherwise
        """
        try:
            from cli.config import WorkspaceConfig

            ws_config = WorkspaceConfig.load()
            return ws_config.workspace_id if ws_config else None
        except Exception:
            # No workspace config available
            return None

    def _get_api_config(self) -> Any:
        """
        Get APIConfig for generated API client calls.

        Returns:
            APIConfig instance with base_path set from config
        """
        try:
            from cli.config import get_effective_api_config
            from sdk.generated.api_config import APIConfig

            api_config = get_effective_api_config()
            api_url = api_config.get("api_url")

            if not api_url:
                raise RuntimeError("API URL not configured")

            return APIConfig(base_path=api_url, access_token=None)
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to load API config: {e}[/yellow]")
            # Return default config as fallback
            from sdk.generated.api_config import APIConfig

            return APIConfig()

    def _load_workflows(self) -> None:
        """
        Load workflow definitions.

        If workflow_file is specified, loads ONLY that workflow (single workflow mode).
        Otherwise, loads ALL workflows from workflows_dir (multi-workflow mode).
        """
        # Single workflow mode - load only the specified workflow
        if self.workflow_file:
            try:
                with open(self.workflow_file) as f:
                    data = yaml.safe_load(f)
                    # Fix YAML boolean key issue (on: becomes True)
                    data = self._fix_yaml_boolean_keys(data)
                    workflow = Workflow(**data)
                    self.workflows[workflow.name] = workflow
                    console.print(
                        f"[dim]✓ Loaded workflow: {workflow.name} (single workflow mode)[/dim]"
                    )
                return
            except Exception as e:
                console.print(
                    f"[red]Error: Failed to load workflow {self.workflow_file}: {e}[/red]"
                )
                return

        # Multi-workflow mode - load all workflows from directory
        if not self.workflows_dir.exists():
            console.print(
                f"[yellow]Warning: Workflows directory not found: {self.workflows_dir}[/yellow]"
            )
            return

        for workflow_file in self.workflows_dir.glob("*.yaml"):
            try:
                with open(workflow_file) as f:
                    data = yaml.safe_load(f)
                    # Fix YAML boolean key issue (on: becomes True)
                    data = self._fix_yaml_boolean_keys(data)
                    workflow = Workflow(**data)
                    self.workflows[workflow.name] = workflow
                    console.print(f"[dim]✓ Loaded workflow: {workflow.name}[/dim]")
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to load workflow {workflow_file}: {e}[/yellow]"
                )

        if not self.workflows:
            console.print(
                "[yellow]Warning: No workflows loaded. Worker will not process tasks.[/yellow]"
            )

    async def run(self) -> None:
        """Main worker loop."""
        console.print("\n[bold blue]AnyTask Claude Worker Started[/bold blue]")
        console.print(f"[dim]Workspace: {self.workspace_dir}[/dim]")
        console.print(f"[dim]Workflows: {len(self.workflows)}[/dim]")
        console.print(f"[dim]Poll interval: {self.poll_interval}s[/dim]\n")

        try:
            while True:
                await self._poll_and_process()
                await asyncio.sleep(self.current_backoff)
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down worker...[/yellow]")
            self._print_stats()

    async def _poll_and_process(self) -> None:
        """Poll for tasks and process them."""
        try:
            # Get suggested tasks
            console.print(
                f"[dim][{datetime.now().strftime('%H:%M:%S')}] Polling for tasks...[/dim]"
            )

            tasks = await self._get_suggested_tasks()

            if not tasks:
                # No tasks - increase backoff
                self.current_backoff = min(self.current_backoff * 1.5, self.max_backoff)
                console.print(
                    f"[dim]No tasks available. Next check in {int(self.current_backoff)}s[/dim]"
                )
                return

            # Reset backoff when tasks are found
            self.current_backoff = self.poll_interval

            # Process first task
            task = tasks[0]
            console.print(
                f"\n[bold green]Found task:[/bold green] {task['identifier']} - {task['title']}"
            )

            # Find matching workflow
            workflow = self._find_workflow_for_task(task)
            if not workflow:
                console.print(
                    f"[yellow]No matching workflow for task {task['identifier']}[/yellow]"
                )
                return

            # Execute workflow
            await self._process_task(task, workflow)

            # Update stats
            self.stats["tasks_processed"] += 1

        except Exception as e:
            console.print(f"[red]Error in worker loop:[/red] {e}")
            import traceback

            traceback.print_exc()

    async def _get_suggested_tasks(self) -> List[Dict[str, Any]]:
        """Get suggested tasks using backend's smart suggestion API.

        Uses the backend's suggestion algorithm to recommend tasks that are ready
        to work on (all dependencies complete). Results are automatically filtered
        by dependency status and sorted by priority.

        If project_id is set, uses project-level suggestions with agent_id filtering.
        Otherwise uses workspace-level suggestions.

        Returns:
            List of task dictionaries (ready to work on)
        """
        try:
            # Ensure workspace_id is set
            if self.workspace_id is None:
                console.print(
                    "[yellow]Warning:[/yellow] workspace_id not configured, cannot fetch suggestions"
                )
                return []

            # Call backend suggestion API
            # Use project-level suggest if project_id is available (supports agent_id filtering)
            # Otherwise use workspace-level suggest
            if self.project_id is not None:
                console.print(
                    f"  [dim]Fetching suggestions from project {self.project_id} for agent {self.agent_id}[/dim]"
                )
                response = await self.task_client.suggest_project_tasks(
                    workspace_id=self.workspace_id,
                    project_id=self.project_id,
                    max_suggestions=10,
                    task_status="todo",  # Worker focuses on TODO tasks
                    include_assigned=True,  # Include assigned tasks (filtered by agent_id)
                    agent_id=self.agent_id,  # Server-side filtering by agent
                )
            else:
                console.print(
                    f"  [dim]Fetching suggestions from workspace {self.workspace_id}[/dim]"
                )
                response = await self.task_client.suggest_tasks(
                    workspace_id=self.workspace_id,
                    max_suggestions=10,
                    status="todo",  # Worker focuses on TODO tasks
                    include_assigned=True,  # Include assigned tasks
                )

            # Log suggestion metrics
            console.print(
                f"  [dim]Suggestions: {response.total_ready} ready, "
                f"{response.total_blocked} blocked[/dim]"
            )

            # Get all suggestions
            suggestions = response.suggestions

            # Convert to dict format and filter to only ready tasks
            # (is_ready=True means all dependencies are complete)
            ready_tasks: list[dict[str, Any]] = []
            for suggestion in suggestions:
                if suggestion.is_ready:
                    ready_tasks.append(suggestion.task.model_dump())

                    # Log additional info for debugging
                    if suggestion.blocks and len(suggestion.blocks) > 0:
                        console.print(
                            f"  [dim]Task {suggestion.task.identifier} unblocks "
                            f"{len(suggestion.blocks)} other tasks[/dim]"
                        )

                    # Limit to 5 tasks as before
                    if len(ready_tasks) >= 5:
                        break

            return ready_tasks

        except Exception as e:
            console.print(f"[red]Failed to fetch suggestions:[/red] {e}")
            return []

    def _find_workflow_for_task(self, task: Dict[str, Any]) -> Optional[Workflow]:
        """Find a workflow that matches the task."""
        # Try both 'labels' (from Task model) and 'label_names' (from legacy API responses)
        task_labels = set(task.get("labels", task.get("label_names", [])))
        task_status_raw = task.get("status")

        # Convert Status enum to string value for comparison
        task_status: Optional[str]
        if isinstance(task_status_raw, Status):
            task_status = task_status_raw.value
        elif isinstance(task_status_raw, str):
            task_status = task_status_raw
        else:
            task_status = None

        console.print(f"  [dim]Task labels: {list(task_labels)}[/dim]")
        console.print(f"  [dim]Task status: {task_status}[/dim]")

        for workflow in self.workflows.values():
            console.print(f"  [dim]Checking workflow: {workflow.name}[/dim]")
            required_labels: list[str] = []
            # Check task_created trigger
            if workflow.on.task_created:  # type: ignore[reportUnknownMemberType,unused-ignore]
                task_created_dict: dict[str, Any] = workflow.on.task_created

                required_labels.extend(task_created_dict.get("labels", []))
                console.print(
                    f"    [dim]task_created trigger requires labels: {required_labels}[/dim]"
                )
                if required_labels:
                    matches = any(label in task_labels for label in required_labels)
                    console.print(f"    [dim]Matches: {matches}[/dim]")
                    if not matches:
                        continue
                return workflow

            # Check task_updated trigger
            if workflow.on.task_updated:  # type: ignore[reportUnknownMemberType,unused-ignore]
                task_updated_dict: dict[str, Any] = workflow.on.task_updated

                required_statuses: list[str] = task_updated_dict.get("status", [])
                required_labels.extend(task_updated_dict.get("labels", []))

                console.print(
                    f"    [dim]task_updated trigger requires status: {required_statuses}, labels: {required_labels}[/dim]"
                )

                if required_statuses and task_status not in required_statuses:
                    console.print("    [dim]Status mismatch[/dim]")
                    continue
                if required_labels and not any(
                    label in task_labels for label in required_labels
                ):
                    console.print("    [dim]Labels mismatch[/dim]")
                    continue

                return workflow

        return None

    async def _process_task(self, task: Dict[str, Any], workflow: Workflow) -> None:
        """Process a task using a workflow."""
        # Start attempt
        attempt = await self._start_attempt(
            task["identifier"], workflow.name, self.workspace_id
        )
        attempt_id = attempt.id if attempt else None

        try:
            # Update task to in-progress
            await self._update_task_status(task["identifier"], Status.IN_PROGRESS)

            # Execute workflow with attempt_id
            execution = await self.executor.execute_workflow(
                workflow, task, self.workspace_dir, attempt_id=attempt_id
            )

            # Finish attempt based on execution result
            if execution.status == "success":
                await self._finish_attempt(
                    attempt_id,
                    status="success",
                    execution=execution,
                    workspace_id=self.workspace_id,
                )
                assert isinstance(self.stats["tasks_succeeded"], int)
                self.stats["tasks_succeeded"] += 1
            else:
                # Workflow failed
                await self._finish_attempt(
                    attempt_id,
                    status="failed",
                    execution=execution,
                    workspace_id=self.workspace_id,
                )
                assert isinstance(self.stats["tasks_failed"], int)
                self.stats["tasks_failed"] += 1
                await self._update_task_status(task["identifier"], Status.BLOCKED)
                console.print(
                    f"[yellow]Task {task['identifier']} marked as BLOCKED due to workflow failure[/yellow]"
                )

        except Exception as e:
            # Finish attempt with failure
            await self._finish_attempt(
                attempt_id,
                status="failed",
                failure_class=type(e).__name__,
                failure_message=str(e),
                workspace_id=self.workspace_id,
            )

            console.print(f"\n[red]Failed to process task:[/red] {e}")
            assert isinstance(self.stats["tasks_failed"], int)
            self.stats["tasks_failed"] += 1

            # Update task to BLOCKED on exception
            try:
                await self._update_task_status(task["identifier"], Status.BLOCKED)
                console.print(
                    f"[yellow]Task {task['identifier']} marked as BLOCKED due to exception[/yellow]"
                )
            except Exception as status_error:
                console.print(
                    f"[red]Failed to update task status to blocked: {status_error}[/red]"
                )

            import traceback

            traceback.print_exc()

    async def _update_task_status(self, task_id: str, status: Status) -> Task:
        """Update task status using TaskService."""
        try:
            return await self.task_service.update_task_status(task_id, status)
        except Exception as e:
            console.print(
                f"[yellow]Warning: Failed to update task status: {e}[/yellow]"
            )
            raise

    async def _start_attempt(
        self,
        task_identifier: str,
        workflow_name: str,
        workspace_id: Optional[int] = None,
    ) -> Optional[Any]:
        """
        Start an attempt for a task workflow execution.

        Args:
            task_identifier: Task identifier (e.g., "DEV-123")
            workflow_name: Name of the workflow being executed
            workspace_id: Optional workspace ID for the request

        Returns:
            AttemptResponse if successful, None if failed
        """
        try:
            from sdk.generated.models.StartAttemptRequest import StartAttemptRequest
            from sdk.generated.services.async_Attempts_service import (
                start_attempt_v1_workspaces__workspace_id__tasks__task_identifier__attempts_start_post,
            )

            # Create attempt input
            attempt_input = StartAttemptRequest(notes=f"Workflow: {workflow_name}")

            # Get API config with correct base URL
            api_config = self._get_api_config()

            # Build kwargs for API call
            api_kwargs: Dict[str, Any] = {
                "api_config_override": api_config,
                "task_identifier": task_identifier,
                "data": attempt_input,
                "workspace_id": workspace_id,
            }
            # Only pass X_API_Key if api_key is available (not None)
            if self.api_key is not None:
                api_kwargs["X_API_Key"] = self.api_key

            # Call API to start attempt
            response = await start_attempt_v1_workspaces__workspace_id__tasks__task_identifier__attempts_start_post(
                **api_kwargs
            )

            # Extract attempt from response
            attempt = response.data
            console.print(f"[dim]✓ Started attempt #{attempt.id}[/dim]")
            return attempt

        except Exception as e:
            # Log warning but don't fail workflow
            console.print(f"[yellow]Warning: Failed to start attempt: {e}[/yellow]")
            return None

    async def _finish_attempt(
        self,
        attempt_id: Optional[int],
        status: str,
        execution: Optional[Any] = None,
        failure_class: Optional[str] = None,
        failure_message: Optional[str] = None,
        workspace_id: Optional[int] = None,
    ) -> None:
        """
        Finish an attempt with execution results.

        Args:
            attempt_id: ID of the attempt to finish
            status: "success" or "failed"
            execution: WorkflowExecution object with results
            failure_class: Exception class name if failed
            failure_message: Exception message if failed
            workspace_id: Optional workspace ID for the request
        """
        if attempt_id is None:
            # No attempt was created, skip
            return

        try:
            import json

            from sdk.generated.models.AttemptMetadata import AttemptMetadata
            from sdk.generated.models.FinishAttemptRequest import FinishAttemptRequest
            from sdk.generated.services.async_Attempts_service import (
                finish_attempt_v1_workspaces__workspace_id__attempts__attempt_id__finish_post,
            )

            # Calculate duration if execution provided
            wall_clock_ms = None
            extra_metadata: Optional[AttemptMetadata] = None

            if execution:
                if execution.started_at and execution.completed_at:
                    duration = execution.completed_at - execution.started_at
                    wall_clock_ms = int(duration.total_seconds() * 1000)

                # Build metadata from execution
                workflow_metadata: Dict[str, Union[str, int]] = {
                    "workflow_name": execution.workflow_name,
                    "steps_executed": len(execution.step_results),
                    "steps_succeeded": sum(
                        1 for s in execution.step_results if s.status.value == "success"
                    ),
                    "steps_failed": sum(
                        1 for s in execution.step_results if s.status.value == "failure"
                    ),
                    "steps_skipped": sum(
                        1 for s in execution.step_results if s.status.value == "skipped"
                    ),
                }

                # Create AttemptMetadata with workflow info in notes field
                extra_metadata = AttemptMetadata(notes=json.dumps(workflow_metadata))

            # Create finish input
            finish_input = FinishAttemptRequest(
                status=status,
                failure_class=failure_class,
                failure_message=failure_message,
                wall_clock_ms=wall_clock_ms,
                extra_metadata=extra_metadata,
            )

            # Get API config with correct base URL
            api_config = self._get_api_config()

            # Build kwargs for API call
            api_kwargs: Dict[str, Any] = {
                "api_config_override": api_config,
                "attempt_id": attempt_id,
                "data": finish_input,
                "workspace_id": workspace_id,
            }
            # Only pass X_API_Key if api_key is available (not None)
            if self.api_key is not None:
                api_kwargs["X_API_Key"] = self.api_key

            # Call API to finish attempt
            await finish_attempt_v1_workspaces__workspace_id__attempts__attempt_id__finish_post(
                **api_kwargs
            )

            console.print(f"[dim]✓ Finished attempt #{attempt_id} ({status})[/dim]")

        except Exception as e:
            # Log error but don't fail workflow
            console.print(f"[yellow]Warning: Failed to finish attempt: {e}[/yellow]")

    def _print_stats(self) -> None:
        """Print worker statistics."""
        started_at = self.stats["started_at"]
        assert isinstance(started_at, datetime)
        uptime = datetime.now() - started_at
        hours = uptime.total_seconds() / 3600

        table = Table(title="Worker Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Uptime", f"{hours:.2f} hours")
        table.add_row("Tasks Processed", str(self.stats["tasks_processed"]))
        table.add_row("Tasks Succeeded", str(self.stats["tasks_succeeded"]))
        table.add_row("Tasks Failed", str(self.stats["tasks_failed"]))

        tasks_processed = self.stats["tasks_processed"]
        assert isinstance(tasks_processed, int)
        if tasks_processed > 0:
            tasks_succeeded = self.stats["tasks_succeeded"]
            assert isinstance(tasks_succeeded, int)
            success_rate = tasks_succeeded / tasks_processed * 100
            table.add_row("Success Rate", f"{success_rate:.1f}%")

        console.print()
        console.print(table)


async def main() -> None:
    """Entry point for the worker."""
    coordinator = TaskCoordinator(workspace_dir=Path.cwd())
    await coordinator.run()


if __name__ == "__main__":
    asyncio.run(main())
