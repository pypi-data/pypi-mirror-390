"""
Context handling mixin for workflow executor.
"""

import json as json_module
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

if TYPE_CHECKING:
    from ..context import ExecutionContext
    from ..models import WorkflowStep


class ContextHandlerMixin:
    """Mixin for handling execution context and variable interpolation."""

    # Type hints for attributes that will be provided by WorkflowExecutor
    secrets_manager: Any

    def _get_cache_key(
        self, step: "WorkflowStep", ctx: "ExecutionContext"
    ) -> Optional[str]:
        """Generate cache key for a step if caching is enabled."""
        if not step.uses or "cache" not in (step.with_ or {}):
            return None

        # For now, simple key based on step and task
        task_id = ctx.task.get("id")
        task_updated = ctx.task.get("updated_at", "")
        return f"step:{step.uses}:task:{task_id}:updated:{task_updated}"

    def _build_evaluation_context(self, ctx: "ExecutionContext") -> Dict[str, Any]:
        """
        Build context dictionary for expression evaluation.

        Returns:
            Dictionary containing steps, env, task, and other variables
        """
        # Convert step outputs to nested structure
        steps = {}
        for step_id, output in ctx.outputs.items():
            steps[step_id] = {
                "outputs": output if isinstance(output, dict) else {"value": output}
            }

        return {
            "steps": steps,
            "env": ctx.env,
            "task": ctx.task,
        }

    def _interpolate_vars(self, value: Any, ctx: "ExecutionContext") -> Any:
        """Interpolate variables in strings like ${{ task.title }} and ${{ secrets.NAME }}."""
        if isinstance(value, str):
            # Simple variable replacement (TODO: implement proper expression evaluator)
            result = value

            # Replace task variables
            for key, val in ctx.task.items():
                result = result.replace(f"${{{{ task.{key} }}}}", str(val))

            # Replace step outputs
            for step_id, output in ctx.outputs.items():
                if isinstance(output, dict):
                    output_dict: dict[str, Any] = cast(dict[str, Any], output)
                    for out_key, out_val in output_dict.items():
                        # Use json.dumps for complex types (dict, list) to ensure valid JSON
                        if isinstance(out_val, (dict, list)):
                            replacement = json_module.dumps(out_val)
                        else:
                            replacement = str(out_val)
                        result = result.replace(
                            f"${{{{ steps.{step_id}.outputs.{out_key} }}}}",
                            replacement,
                        )

            # Replace secrets
            try:
                result = self.secrets_manager.interpolate_secrets(result)
            except ValueError as e:
                # Re-raise with better context
                raise ValueError(f"Secret interpolation failed: {e}") from e

            return result

        elif isinstance(value, dict):
            value_dict: dict[str, Any] = cast(dict[str, Any], value)
            return {k: self._interpolate_vars(v, ctx) for k, v in value_dict.items()}

        elif isinstance(value, list):
            value_list: list[Any] = cast(list[Any], value)  # type: ignore[redundant-cast]
            return [self._interpolate_vars(item, ctx) for item in value_list]

        return value
