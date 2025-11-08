"""
Git-related workflow actions.
"""

import asyncio
from typing import Any, Dict

from .base import Action
from ..context import ExecutionContext


class CheckoutAction(Action):
    """Git checkout action."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Checkout a git branch."""
        branch = params.get("branch", "main")
        clean = params.get("clean", False)

        commands: list[str] = []
        if clean:
            commands.append("git reset --hard")
            commands.append("git clean -fd")
        commands.append(f"git checkout {branch}")
        commands.append("git pull origin {branch}")

        for cmd in commands:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=ctx.workspace_dir,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                raise RuntimeError(f"Git command failed: {stderr.decode()}")

        return {"branch": branch, "clean": clean}


class GitCommitAction(Action):
    """Git commit action."""

    async def execute(
        self, params: Dict[str, Any], ctx: ExecutionContext
    ) -> Dict[str, Any]:
        """Commit changes to git."""
        message = params.get("message", "Automated commit")
        add = params.get("add", "all")

        # Add files
        if add == "all":
            add_cmd = "git add -A"
        else:
            add_cmd = f"git add {add}"

        process = await asyncio.create_subprocess_shell(
            add_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        await process.communicate()

        # Commit
        commit_cmd: list[str] = ["git", "commit", "-m", message]
        process = await asyncio.create_subprocess_exec(
            *commit_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            # Check if it's just "nothing to commit"
            if b"nothing to commit" in stdout or b"nothing to commit" in stderr:
                return {"commit_hash": None, "committed": False}
            raise RuntimeError(f"Git commit failed: {stderr.decode()}")

        # Get commit hash
        process = await asyncio.create_subprocess_shell(
            "git rev-parse --short HEAD",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=ctx.workspace_dir,
        )
        stdout, _ = await process.communicate()
        commit_hash = stdout.decode().strip()

        return {"commit_hash": commit_hash, "committed": True}
