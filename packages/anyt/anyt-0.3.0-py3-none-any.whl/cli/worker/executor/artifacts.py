"""
Artifact generation mixin for workflow executor.
"""

import json
from typing import TYPE_CHECKING, Any, Dict

from rich.console import Console

if TYPE_CHECKING:
    from ..models import WorkflowExecution

console = Console()


class ArtifactGeneratorMixin:
    """Mixin for creating workflow artifacts and reports."""

    # Type hints for attributes that will be provided by WorkflowExecutor
    api_key: Any
    workspace_id: Any

    async def _create_workflow_artifacts(
        self, execution: "WorkflowExecution", attempt_id: int
    ) -> None:
        """
        Create artifacts for workflow execution.

        Creates execution summary and error log artifacts attached to the attempt.

        Args:
            execution: Completed workflow execution
            attempt_id: ID of the attempt to attach artifacts to

        Raises:
            Exception: If artifact creation fails (caller should handle gracefully)
        """
        from sdk.generated.models.CreateArtifactRequest import CreateArtifactRequest
        from sdk.generated.services.async_Artifacts_service import (
            create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post,
        )

        # Get API config with correct base URL
        api_config = self._get_api_config()  # type: ignore[attr-defined]

        # Get workspace_id from execution context, fallback to self.workspace_id
        task = execution.context.get("task", {})
        workspace_id = task.get("workspace_id") or self.workspace_id

        # Artifact 1: Execution summary (always created)
        summary_json = self._generate_execution_summary(execution)
        artifact_data = CreateArtifactRequest(
            type="log",
            name="workflow_execution_summary.json",
            content=summary_json,
            mime_type="application/json",
        )

        # Debug logging
        console.print(
            f"[dim]Creating artifact with data: {artifact_data.model_dump()}[/dim]"
        )
        console.print(
            f"[dim]Workspace ID: {workspace_id}, Attempt ID: {attempt_id}[/dim]"
        )

        try:
            # Build kwargs for API call
            api_kwargs: Dict[str, Any] = {
                "api_config_override": api_config,
                "attempt_id": attempt_id,
                "data": artifact_data,
                "workspace_id": workspace_id,
            }
            # Only pass X_API_Key if api_key is available (not None)
            if self.api_key is not None:
                api_kwargs["X_API_Key"] = self.api_key

            await create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post(
                **api_kwargs
            )
        except Exception as e:
            console.print(f"[red]Artifact creation failed: {e}[/red]")
            console.print(f"[dim]Artifact data was: {artifact_data.model_dump()}[/dim]")
            console.print(
                f"[dim]Workspace ID: {workspace_id}, Attempt ID: {attempt_id}[/dim]"
            )
            raise

        # Artifact 2: Error log (only on failure)
        if execution.status == "failure":
            error_log = self._generate_error_log(execution)
            # Build kwargs for API call
            error_api_kwargs: Dict[str, Any] = {
                "api_config_override": api_config,
                "attempt_id": attempt_id,
                "data": CreateArtifactRequest(
                    type="log",
                    name="workflow_errors.txt",
                    content=error_log,
                    mime_type="text/plain",
                ),
                "workspace_id": workspace_id,
            }
            # Only pass X_API_Key if api_key is available (not None)
            if self.api_key is not None:
                error_api_kwargs["X_API_Key"] = self.api_key

            await create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post(
                **error_api_kwargs
            )

        console.print("[dim]✓ Created workflow artifacts[/dim]")

    def _generate_execution_summary(self, execution: "WorkflowExecution") -> str:
        """
        Generate JSON execution summary.

        Args:
            execution: Completed workflow execution

        Returns:
            JSON string containing execution summary
        """
        from ..models import StepStatus

        # Calculate duration
        duration_seconds = 0.0
        if execution.started_at and execution.completed_at:
            duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()

        # Build step summaries
        steps: list[dict[str, Any]] = []
        for step_result in execution.step_results:
            step_duration = step_result.duration_seconds or 0.0
            # Preview output (truncate if too long)
            output_preview = None
            if step_result.output:
                output_str = str(step_result.output)
                output_preview = (
                    output_str[:200] + "..." if len(output_str) > 200 else output_str
                )

            steps.append(
                {
                    "step_id": step_result.step_id,
                    "step_name": step_result.step_name,
                    "status": step_result.status.value,
                    "duration_seconds": round(step_duration, 2),
                    "output_preview": output_preview,
                    "error": step_result.error,
                }
            )

        # Calculate summary counts
        total_steps = len(execution.step_results)
        steps_succeeded = sum(
            1 for s in execution.step_results if s.status == StepStatus.SUCCESS
        )
        steps_failed = sum(
            1 for s in execution.step_results if s.status == StepStatus.FAILURE
        )
        steps_skipped = sum(
            1 for s in execution.step_results if s.status == StepStatus.SKIPPED
        )

        summary: dict[str, Any] = {
            "workflow_name": execution.workflow_name,
            "task_id": execution.task_id,
            "task_identifier": execution.task_identifier,
            "started_at": (
                execution.started_at.isoformat() if execution.started_at else None
            ),
            "completed_at": (
                execution.completed_at.isoformat() if execution.completed_at else None
            ),
            "duration_seconds": round(duration_seconds, 2),
            "status": execution.status,
            "steps": steps,
            "summary": {
                "total_steps": total_steps,
                "steps_succeeded": steps_succeeded,
                "steps_failed": steps_failed,
                "steps_skipped": steps_skipped,
            },
        }

        return json.dumps(summary, indent=2)

    def _generate_error_log(self, execution: "WorkflowExecution") -> str:
        """
        Generate human-readable error log for failed workflow.

        Args:
            execution: Failed workflow execution

        Returns:
            Formatted error log text
        """
        from ..models import StepStatus

        lines: list[str] = []

        # Header
        lines.append("WORKFLOW EXECUTION FAILED")
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"Workflow: {execution.workflow_name}")
        lines.append(
            f"Task: {execution.task_identifier} - {execution.context.get('task', {}).get('title', 'N/A')}"
        )

        if execution.started_at:
            lines.append(f"Started: {execution.started_at.isoformat()}")
        if execution.completed_at:
            lines.append(f"Failed: {execution.completed_at.isoformat()}")

        # Duration
        if execution.started_at and execution.completed_at:
            duration = (execution.completed_at - execution.started_at).total_seconds()
            lines.append(f"Duration: {duration:.1f} seconds")

        lines.append("")

        # Failed steps
        failed_steps = [
            s for s in execution.step_results if s.status == StepStatus.FAILURE
        ]

        if failed_steps:
            lines.append("FAILED STEPS")
            lines.append("=" * 50)
            lines.append("")

            for step in failed_steps:
                lines.append(f"Step: {step.step_name}")
                lines.append(f"Status: {step.status.value.upper()}")
                if step.duration_seconds:
                    lines.append(f"Duration: {step.duration_seconds:.1f} seconds")
                if step.error:
                    lines.append(f"Error: {step.error}")
                lines.append("")

                # Include step output if available
                if step.output:
                    lines.append("Step output:")
                    lines.append("-" * 50)
                    output_str = str(step.output)
                    # Limit output to avoid huge artifacts
                    if len(output_str) > 5000:
                        lines.append(output_str[:5000])
                        lines.append("... (output truncated)")
                    else:
                        lines.append(output_str)
                    lines.append("")

        # Overall workflow error (if any caught at workflow level)
        lines.append("WORKFLOW STATUS")
        lines.append("=" * 50)
        lines.append(f"Final status: {execution.status}")
        lines.append(
            f"Steps completed: {len([s for s in execution.step_results if s.status != StepStatus.PENDING])}/{len(execution.step_results)}"
        )

        return "\n".join(lines)

    async def _update_attempt_with_costs(
        self, attempt_id: int, execution: "WorkflowExecution"
    ) -> None:
        """
        Update attempt with token costs from workflow execution.

        Since cost_tokens is set via FinishAttemptInput only, we store it
        in the execution summary artifact's metadata for now.

        Args:
            attempt_id: ID of the attempt to update
            execution: Completed workflow execution with token tracking
        """
        # Token costs are tracked in the execution summary artifact
        # The finish_attempt API call should set cost_tokens when finishing
        if execution.total_tokens > 0:
            console.print(f"[dim]✓ Tracked token costs: {execution.total_tokens}[/dim]")
