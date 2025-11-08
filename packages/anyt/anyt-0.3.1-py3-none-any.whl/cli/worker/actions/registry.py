"""
Action registry for workflow actions.
"""

from typing import Dict, Optional

from .base import Action
from .cache import CacheAction
from .claude import ClaudeCodeAction, ClaudePromptAction
from .dry_run import (
    DryRunClaudeCodeAction,
    DryRunClaudePromptAction,
    DryRunGitCommitAction,
)
from .git import CheckoutAction, GitCommitAction
from .task import TaskAnalyzeAction, TaskDetailAction, TaskUpdateAction
from .testing import BuildAction, TestAction


class ActionRegistry:
    """Registry of available workflow actions."""

    def __init__(self) -> None:
        """Initialize registry with all available actions."""
        self.actions: Dict[str, Action] = {
            # Git actions
            "anyt/checkout@v1": CheckoutAction(),
            "anyt/git-commit@v1": GitCommitAction(),
            # Cache actions
            "anyt/cache@v1": CacheAction(),
            # Claude/AI actions
            "anyt/claude-prompt@v1": ClaudePromptAction(),
            "anyt/claude-code@v1": ClaudeCodeAction(),
            # Dry-run actions (for testing without external dependencies)
            "anyt/dry-run-claude-prompt@v1": DryRunClaudePromptAction(),
            "anyt/dry-run-claude-code@v1": DryRunClaudeCodeAction(),
            "anyt/dry-run-git-commit@v1": DryRunGitCommitAction(),
            # Task actions
            "anyt/task-update@v1": TaskUpdateAction(),
            "anyt/task-analyze@v1": TaskAnalyzeAction(),
            "anyt/task-detail@v1": TaskDetailAction(),
            # Testing/Build actions
            "anyt/test@v1": TestAction(),
            "anyt/build@v1": BuildAction(),
        }

    def get_action(self, action_name: str) -> Optional[Action]:
        """Get an action by name.

        Args:
            action_name: The name of the action (e.g., "anyt/checkout@v1")

        Returns:
            The action instance or None if not found
        """
        return self.actions.get(action_name)

    def register_action(self, name: str, action: Action) -> None:
        """Register a custom action.

        Args:
            name: The action name (e.g., "custom/my-action@v1")
            action: The action instance to register
        """
        self.actions[name] = action

    def list_actions(self) -> list[str]:
        """Get list of all registered action names.

        Returns:
            List of action names
        """
        return sorted(self.actions.keys())
