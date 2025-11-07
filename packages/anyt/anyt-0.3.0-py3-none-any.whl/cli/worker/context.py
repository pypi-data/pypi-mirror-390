"""
Execution context for workflow steps.
"""

from pathlib import Path
from typing import Any, Dict, Optional

from sdk.generated.models.CreateArtifactRequest import CreateArtifactRequest
from sdk.generated.services.async_Artifacts_service import (
    create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post,
)


class ExecutionContext:
    """Context passed to workflow steps during execution."""

    def __init__(
        self,
        task: Dict[str, Any],
        workspace_dir: Path,
        outputs: Dict[str, Any],
        env: Dict[str, str],
        workspace_id: int,
        attempt_id: Optional[int] = None,
    ):
        """
        Initialize execution context.

        Args:
            task: Task data (id, identifier, title, description, etc.)
            workspace_dir: Path to workspace directory
            outputs: Outputs from previous steps (keyed by step ID)
            env: Environment variables
            workspace_id: Workspace ID for API calls (required)
            attempt_id: Optional attempt ID for artifact creation
        """
        self.task = task
        self.workspace_dir = workspace_dir
        self.outputs = outputs
        self.env = env
        self.workspace_id = workspace_id
        self.attempt_id = attempt_id

    def get_task_field(self, field: str, default: Any = None) -> Any:
        """Get a field from the task data."""
        return self.task.get(field, default)

    def get_step_output(self, step_id: str, key: str, default: Any = None) -> Any:
        """Get an output value from a previous step."""
        step_outputs = self.outputs.get(step_id, {})
        return step_outputs.get(key, default)

    def set_output(self, step_id: str, key: str, value: Any) -> None:
        """Set an output value for the current step."""
        if step_id not in self.outputs:
            self.outputs[step_id] = {}
        self.outputs[step_id][key] = value

    async def create_artifact(
        self,
        type: str,
        name: str,
        content: str,
        mime_type: str = "text/plain",
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create an artifact for the current attempt.

        This is a helper method for workflow actions to create artifacts
        during execution. Only creates the artifact if attempt_id is set.

        Args:
            type: Artifact type (e.g., "code_diff", "test_results", "build_output")
            name: Artifact filename
            content: Artifact content
            mime_type: MIME type of the content (default: "text/plain")
            extra_metadata: Additional metadata to store with the artifact

        """
        if not self.attempt_id:
            return

        artifact_input = CreateArtifactRequest(
            type=type,
            name=name,
            content=content,
            mime_type=mime_type,
            extra_metadata=extra_metadata,
        )

        await create_artifact_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__post(
            workspace_id=self.workspace_id,
            attempt_id=self.attempt_id,
            data=artifact_input,
        )
