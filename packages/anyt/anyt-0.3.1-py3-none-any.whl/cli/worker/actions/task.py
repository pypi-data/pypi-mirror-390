"""
Task management workflow actions.
"""

import json
from typing import Any, Dict, Optional, cast

from cli.client.comments import CommentsAPIClient
from cli.models.comment import CommentCreate

from .base import Action
from ..context import ExecutionContext


class TaskUpdateAction(Action):
    """Update AnyTask task with enhanced note support and metadata storage."""

    def __init__(self) -> None:
        """Initialize TaskUpdateAction with API clients."""
        from cli.services.task_service import TaskService

        self.task_service: TaskService = TaskService.from_config()
        self.comments_client: CommentsAPIClient = CommentsAPIClient.from_config()

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Update task in AnyTask."""
        status = params.get("status")
        note = params.get("note")
        add_timestamp = params.get("timestamp", False)
        metadata = params.get("metadata")

        task_id = ctx.task.get("identifier")
        if not task_id:
            raise ValueError("Task identifier not found in context")

        # Add timestamp if requested
        if note and add_timestamp:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note = f"**{timestamp}**\n\n{note}"

        # Update status if provided
        if status:
            await self._update_status(task_id, status)

        # Add note if provided
        if note:
            await self._add_note(ctx, note)

        # Store metadata if provided
        if metadata:
            await self._store_metadata(ctx, metadata)

        return {
            "updated": True,
            "status": status,
            "note_added": bool(note),
            "metadata_stored": bool(metadata),
        }

    async def _update_status(self, task_id: str, status: str) -> None:
        """Update task status using TaskService."""
        from cli.models.common import Status

        # Convert string status to Status enum by value (values are lowercase)
        try:
            status_enum = Status(status.lower())
        except ValueError:
            raise ValueError(f"Invalid status: {status}")

        # Use service for business logic + validation
        await self.task_service.update_task_status(task_id, status_enum)

    async def _add_note(self, ctx: ExecutionContext, note: str) -> None:
        """Add comment to task using CommentsAPIClient."""

        task_identifier = ctx.task.get("identifier")
        task_numeric_id = ctx.task.get("id")

        if not task_identifier or not task_numeric_id:
            raise ValueError("Task identifier and ID required in context")

        # Get API key from config for author_id
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        api_key = api_config.get("api_key")

        if not api_key:
            # Provide detailed error message with troubleshooting steps
            raise ValueError(
                "API key not found. Required for creating task comments/notes.\n"
                "To fix this:\n"
                "  Set the ANYT_API_KEY environment variable:\n"
                "    export ANYT_API_KEY=anyt_agent_your_key_here\n"
                "  Get your API key from: https://anyt.dev/home/settings/api-keys"
            )

        comment = CommentCreate(
            content=note,
            task_id=task_numeric_id,
            author_id=api_key,
            author_type="agent",
        )
        await self.comments_client.create_comment(task_identifier, comment)

    async def _store_metadata(
        self, ctx: ExecutionContext, metadata: Dict[str, Any]
    ) -> None:
        """Store workflow execution metadata in task notes.

        Since task custom fields are not currently supported by the API,
        we store metadata as a structured note with a special marker.
        This allows for later retrieval and parsing.

        Args:
            ctx: Execution context containing task data
            metadata: Workflow execution metadata dictionary
        """
        from cli.models.workflow import WorkflowExecutionMetadata

        # Validate and convert metadata to proper format
        try:
            meta = WorkflowExecutionMetadata(**metadata)
        except Exception as e:
            raise ValueError(f"Invalid metadata format: {e}")

        # Store as structured note with HTML comment marker for easy parsing
        note = f"""<!-- workflow-metadata
{meta.model_dump_json(indent=2)}
-->"""

        # Add metadata note to task
        await self._add_note(ctx, note)


class TaskAnalyzeAction(Action):
    """Send Claude Code analysis results to task notes with formatting."""

    def __init__(self) -> None:
        """Initialize with CommentsAPIClient."""
        self.comments_client = CommentsAPIClient.from_config()

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Send formatted analysis to task."""
        analysis_raw = params.get("analysis", {})
        title = params.get("title", "Analysis Results")
        include_empty = params.get("include_empty", False)

        # Handle both dict and JSON string (from template interpolation)
        analysis: Dict[str, Any]
        if isinstance(analysis_raw, str):
            try:
                analysis = cast(Dict[str, Any], json.loads(analysis_raw))
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"analysis must be a valid JSON string or dictionary: {e}"
                )
        elif isinstance(analysis_raw, dict):
            analysis = cast(Dict[str, Any], analysis_raw)
        else:
            raise ValueError("analysis must be a dictionary or JSON string")

        # Format analysis as markdown
        note = self._format_analysis(title, analysis, include_empty)

        # Send to task via CommentsAPIClient

        task_identifier = ctx.task.get("identifier")
        task_numeric_id = ctx.task.get("id")

        if not task_identifier or not task_numeric_id:
            raise ValueError("Task identifier and ID required in context")

        # Get API key from config for author_id
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        api_key = api_config.get("api_key")

        if not api_key:
            # Provide detailed error message with troubleshooting steps
            raise ValueError(
                "API key not found. Required for creating task comments/notes.\n"
                "To fix this:\n"
                "  Set the ANYT_API_KEY environment variable:\n"
                "    export ANYT_API_KEY=anyt_agent_your_key_here\n"
                "  Get your API key from: https://anyt.dev/home/settings/api-keys"
            )

        comment = CommentCreate(
            content=note,
            task_id=task_numeric_id,
            author_id=api_key,
            author_type="agent",
        )
        created_comment = await self.comments_client.create_comment(
            task_identifier, comment
        )

        # Determine which sections were included
        sections: list[str] = []
        if analysis.get("files_read"):
            sections.append("files_read")
        if analysis.get("files_written"):
            sections.append("files_written")
        if analysis.get("tools_used"):
            sections.append("tools_used")
        if analysis.get("thinking"):
            sections.append("thinking")
        if analysis.get("summary"):
            sections.append("summary")

        return {
            "sent": True,
            "sections": sections,
            "note_length": len(note),
            "comment_id": created_comment.id,
        }

    def _format_analysis(
        self, title: str, analysis: Dict[str, Any], include_empty: bool
    ) -> str:
        """Format analysis results as markdown."""
        lines: list[str] = [f"## {title}\n"]

        # Files Read
        files_read = analysis.get("files_read", [])
        if files_read or include_empty:
            lines.append("### Files Read")
            if files_read:
                for f in files_read:
                    lines.append(f"- `{f}`")
            else:
                lines.append("_None_")
            lines.append("")

        # Files Written
        files_written = analysis.get("files_written", [])
        if files_written or include_empty:
            lines.append("### Files Written")
            if files_written:
                for f in files_written:
                    lines.append(f"- `{f}`")
            else:
                lines.append("_None_")
            lines.append("")

        # Tools Used
        tools_used = analysis.get("tools_used", [])
        if tools_used or include_empty:
            lines.append("### Tools Used")
            if tools_used:
                for tool in tools_used:
                    lines.append(f"- `{tool}`")
            else:
                lines.append("_None_")
            lines.append("")

        # Thinking (optional)
        thinking = analysis.get("thinking", "")
        if thinking:
            lines.append("### Analysis")
            # Truncate if too long
            if len(thinking) > 500:
                thinking = thinking[:500] + "..."
            lines.append(thinking)
            lines.append("")

        # Summary
        summary = analysis.get("summary", "")
        if summary or include_empty:
            lines.append("### Summary")
            if summary:
                lines.append(summary)
            else:
                lines.append("_No summary available_")
            lines.append("")

        return "\n".join(lines)


class TaskDetailAction(Action):
    """Send workflow execution details to task notes."""

    def __init__(self) -> None:
        """Initialize the action with API clients."""
        self.comments_client = CommentsAPIClient.from_config()

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Send formatted execution details to task."""
        status = params.get("status", "unknown")
        error = params.get("error")
        workflow_name = params.get("workflow_name", "unknown")
        duration = params.get("duration")  # seconds

        # Format execution details
        note = self._format_execution_details(
            ctx, status, error, workflow_name, duration
        )

        # Send to task

        task_identifier = ctx.task.get("identifier")
        task_numeric_id = ctx.task.get("id")

        if not task_identifier or not task_numeric_id:
            raise ValueError("Task identifier and ID required in context")

        # Get API key from config for author_id
        from cli.config import get_effective_api_config

        api_config = get_effective_api_config()
        api_key = api_config.get("api_key")

        if not api_key:
            # Provide detailed error message with troubleshooting steps
            raise ValueError(
                "API key not found. Required for creating task comments/notes.\n"
                "To fix this:\n"
                "  Set the ANYT_API_KEY environment variable:\n"
                "    export ANYT_API_KEY=anyt_agent_your_key_here\n"
                "  Get your API key from: https://anyt.dev/home/settings/api-keys"
            )

        # Create comment via API client
        comment_create = CommentCreate(
            content=note,
            task_id=task_numeric_id,
            author_id=api_key,
            author_type="agent",
        )
        created_comment = await self.comments_client.create_comment(
            task_identifier, comment_create
        )

        return {"sent": True, "comment_id": created_comment.id}

    def _format_execution_details(
        self,
        ctx: ExecutionContext,
        status: str,
        error: Optional[str],
        workflow_name: str,
        duration: Optional[float],
    ) -> str:
        """Format execution details as markdown."""
        from datetime import datetime

        lines: list[str] = ["## Workflow Execution Details\n"]

        # Status with emoji
        status_emoji = "✅" if status == "success" else "❌"
        lines.append(f"**Status**: {status_emoji} {status.title()}")
        lines.append("")

        # Workflow info
        lines.append(f"**Workflow**: `{workflow_name}`")

        # Worker info
        agent_id = ctx.task.get("agent_id", "unknown")
        lines.append(f"**Worker**: `{agent_id}`")

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"**Timestamp**: {timestamp}")

        # Duration if available
        if duration is not None:
            lines.append(f"**Duration**: {self._format_duration(duration)}")
        lines.append("")

        # Steps completed
        if ctx.outputs:
            lines.append("### Steps Completed")
            for step_id, output in ctx.outputs.items():
                # Determine step status from output
                step_status = "✓"
                if isinstance(output, dict):
                    output_dict: dict[str, Any] = cast(dict[str, Any], output)
                    if output_dict.get("error"):
                        step_status = "✗"
                lines.append(f"- {step_status} `{step_id}`")
            lines.append("")

        # Error details if failed
        if error and status != "success":
            lines.append("### Error Details")
            lines.append("```")
            lines.append(error)
            lines.append("```")
            lines.append("")

        return "\n".join(lines)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"
