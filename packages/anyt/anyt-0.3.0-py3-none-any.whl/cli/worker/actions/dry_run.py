"""
Dry-run workflow actions that simulate execution without making real changes.

These actions allow testing the workflow orchestration without invoking Claude Code
or making actual git commits. They return realistic dummy outputs that match the
expected data structures of their real counterparts.
"""

import asyncio
from typing import Any, Dict

from rich.console import Console

from .base import Action
from ..context import ExecutionContext

console = Console()


class DryRunClaudePromptAction(Action):
    """Simulates Claude prompt analysis with dummy output."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute dry-run Claude prompt analysis."""
        prompt = params.get("prompt", "")
        output_var = params.get("output", "result")
        model = params.get("model", "claude-haiku-4-5-20251001")

        console.print(
            f"  [dim][DRY RUN] Simulating Claude prompt with model {model}...[/dim]"
        )
        console.print(f"  [dim]Prompt: {prompt[:100]}...[/dim]")

        # Simulate some processing time
        await asyncio.sleep(0.5)

        # Generate realistic dummy analysis based on task context
        task_title = ctx.task.get("title", "Unknown task")

        analysis = f"""Analysis of task: {task_title}

Task Requirements:
- Implement the requested feature based on description
- Ensure proper error handling and validation
- Add comprehensive tests
- Update documentation if needed

Technical Approach:
- Review existing codebase structure
- Identify files that need modification
- Follow project coding standards
- Consider edge cases and error scenarios

Estimated Complexity: Medium
Recommended Implementation Steps:
1. Review related code
2. Implement core functionality
3. Add tests
4. Validate and refine

(Dry run simulation - no actual analysis performed)
"""

        console.print("  [green]✓[/green] [dim]Analysis complete (dry run)[/dim]")

        return {
            output_var: analysis,
            "completed": True,
            "summary": f"Analyzed task '{task_title}' (dry run)",
            "model": model,
        }


class DryRunClaudeCodeAction(Action):
    """Simulates Claude Code execution with dummy output."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute dry-run Claude Code implementation."""
        prompt = params.get("prompt", "")
        model = params.get("model", "claude-haiku-4-5-20251001")

        console.print(
            f"  [dim][DRY RUN] Simulating Claude Code with model {model}...[/dim]"
        )
        console.print(f"  [dim]Prompt: {prompt[:100]}...[/dim]")

        # Simulate processing time
        await asyncio.sleep(1.0)

        # Generate realistic dummy output based on task context
        task_identifier = ctx.task.get("identifier", "TASK-1")
        task_title = ctx.task.get("title", "Unknown task")

        # Simulate files being read and written
        files_read = [
            "src/cli/commands/task.py",
            "src/cli/services/task_service.py",
            "tests/cli/unit/test_task_commands.py",
        ]

        files_written = [
            "src/cli/commands/task.py",
            "tests/cli/unit/test_task_commands.py",
        ]

        # Simulate thinking process
        thinking = f"""Analyzing task {task_identifier}: {task_title}

I'll need to:
1. Understand the current codebase structure
2. Identify where the changes should be made
3. Implement the required functionality
4. Add appropriate tests
5. Ensure code quality standards are met

Let me start by examining the relevant files...

After reviewing the code, I'll implement the changes...

Implementation complete. Changes include:
- Modified core functionality in task.py
- Updated service layer logic
- Added comprehensive test coverage

All changes follow the project's coding standards and patterns.
(Dry run simulation - no actual implementation performed)
"""

        # Simulate summary
        summary = f"""Implementation completed for task {task_identifier} (dry run)

Changes made:
- Updated {len(files_written)} files
- Read {len(files_read)} files for context
- Added new functionality as requested
- Updated tests to cover new code

The implementation follows project standards and includes proper error handling.

Note: This is a dry run simulation. No actual files were modified.
"""

        console.print("  [green]✓[/green] [dim]Implementation complete (dry run)[/dim]")
        console.print(
            f"  [dim]Files read: {len(files_read)}, Files written: {len(files_written)}[/dim]"
        )

        return {
            "exit_code": 0,
            "completed": True,
            "files_read": files_read,
            "files_written": files_written,
            "thinking": thinking,
            "summary": summary,
            "analysis": f"Task {task_identifier} implementation (dry run)",
            "model": model,
            "tools_used": ["Read", "Write", "Edit", "Grep", "Glob"],
        }


class DryRunGitCommitAction(Action):
    """Simulates git commit without actually committing."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute dry-run git commit."""
        message = params.get("message", "Automated commit (dry run)")
        add = params.get("add", "all")

        console.print("  [dim][DRY RUN] Simulating git commit...[/dim]")
        console.print(f"  [dim]Message: {message}[/dim]")
        console.print(f"  [dim]Add mode: {add}[/dim]")

        # Simulate some processing time
        await asyncio.sleep(0.3)

        # Generate dummy commit SHA
        dummy_sha = "abc123def456789012345678901234567890abcd"

        # Simulate files changed
        files_changed = 3
        insertions = 45
        deletions = 12

        console.print(
            f"  [green]✓[/green] [dim]Commit simulated: {dummy_sha[:7]} (dry run)[/dim]"
        )
        console.print(
            f"  [dim]{files_changed} files changed, {insertions} insertions(+), {deletions} deletions(-)[/dim]"
        )

        return {
            "completed": True,
            "commit_sha": dummy_sha,
            "short_sha": dummy_sha[:7],
            "message": message,
            "files_changed": files_changed,
            "insertions": insertions,
            "deletions": deletions,
            "branch": "dry-run-branch",
        }
