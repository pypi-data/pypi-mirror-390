"""
Core workflow executor implementation.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console

from ..actions.registry import ActionRegistry
from ..cache import CacheManager
from ..context import ExecutionContext
from ..models import StepStatus, Workflow, WorkflowExecution
from ..secrets import SecretsManager
from .artifacts import ArtifactGeneratorMixin
from .context import ContextHandlerMixin
from .steps import StepExecutorMixin

console = Console()


class WorkflowExecutor(StepExecutorMixin, ContextHandlerMixin, ArtifactGeneratorMixin):
    """Executes workflows with step-by-step processing."""

    def __init__(
        self,
        workspace_id: int,
        cache_manager: Optional[CacheManager] = None,
        secrets_manager: Optional[SecretsManager] = None,
        api_key: Optional[str] = None,
    ):
        self.workspace_id = workspace_id
        self.cache_manager = cache_manager or CacheManager()
        self.action_registry = ActionRegistry()
        self.secrets_manager = secrets_manager or SecretsManager()
        self.api_key = api_key

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

    async def execute_workflow(
        self,
        workflow: Workflow,
        task: Dict[str, Any],
        workspace_dir: Path,
        attempt_id: Optional[int] = None,
    ) -> WorkflowExecution:
        """Execute a complete workflow for a task."""
        execution = WorkflowExecution(
            workflow_name=workflow.name,
            task_id=str(task.get("id")),
            task_identifier=task.get("identifier", ""),
            started_at=datetime.now(),
            status="running",
            context={"task": task, "workspace": str(workspace_dir)},
            attempt_id=attempt_id,
        )

        console.print(f"\n[bold blue]Starting workflow:[/bold blue] {workflow.name}")
        console.print(
            f"[dim]Task: {task.get('identifier')} - {task.get('title')}[/dim]\n"
        )

        try:
            # Execute all jobs (currently supporting single job)
            for job_name, job in workflow.jobs.items():
                console.print(f"[bold]Job:[/bold] {job.name}")

                # Create execution context
                ctx = ExecutionContext(
                    task=task,
                    workspace_dir=workspace_dir,
                    outputs={},
                    env={},
                    workspace_id=self.workspace_id,
                    attempt_id=attempt_id,
                )

                # Execute each step
                for step in job.steps:
                    step_result = await self._execute_step(step, ctx)
                    execution.step_results.append(step_result)

                    # Update context with step outputs
                    if step.id and step_result.output:
                        ctx.outputs[step.id] = step_result.output

                    # Handle step failure
                    if step_result.status == StepStatus.FAILURE:
                        if not step.continue_on_error:
                            execution.status = "failure"
                            console.print(
                                f"\n[bold red]Workflow failed at step: {step.name}[/bold red]"
                            )

                            # Execute failure handlers if defined
                            if workflow.on_failure:
                                await self._execute_failure_handlers(
                                    workflow.on_failure.steps, ctx, step_result
                                )

                            break

            # Mark as success if all steps completed
            if execution.status == "running":
                execution.status = "success"
                console.print(
                    "\n[bold green]✓ Workflow completed successfully[/bold green]"
                )

        except Exception as e:
            execution.status = "failure"
            console.print(f"\n[bold red]✗ Workflow failed with error:[/bold red] {e}")

        finally:
            execution.completed_at = datetime.now()

            # Update attempt with token costs and artifacts (if attempt_id provided)
            if attempt_id:
                try:
                    # Update attempt with token costs
                    await self._update_attempt_with_costs(attempt_id, execution)

                    # Create workflow artifacts
                    await self._create_workflow_artifacts(execution, attempt_id)
                except Exception as e:
                    console.print(
                        f"[yellow]Warning: Failed to update attempt: {e}[/yellow]"
                    )

        return execution
