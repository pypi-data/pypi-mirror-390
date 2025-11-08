"""
Attempt management commands.

Commands for viewing workflow execution attempts and their artifacts.
"""

import asyncio
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from cli.services.context import ServiceContext
from sdk.generated.services.async_Artifacts_service import (
    list_attempt_artifacts_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__get,
)
from sdk.generated.services.async_Attempts_service import (
    get_attempt_v1_workspaces__workspace_id__attempts__attempt_id__get,
    list_task_attempts_v1_workspaces__workspace_id__tasks__task_identifier__attempts__get,
)

app = typer.Typer(help="Manage workflow execution attempts")
console = Console()


def format_duration(ms: Optional[int]) -> str:
    """Format duration in milliseconds to human-readable string."""
    if ms is None:
        return "-"

    seconds = ms / 1000
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def format_tokens(tokens: Optional[int]) -> str:
    """Format token count for display."""
    if tokens is None:
        return "-"
    if tokens >= 1_000_000:
        return f"{tokens / 1_000_000:.1f}M"
    elif tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    else:
        return str(tokens)


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp to human-readable string."""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp


def format_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"


@app.command("list")
def list_attempts(
    task_id: str = typer.Argument(..., help="Task identifier"),
) -> None:
    """List all attempts for a task."""

    async def _list_attempts() -> None:
        try:
            context = ServiceContext.from_config()
            workspace_id = context.get_workspace_id()

            # List attempts for the task
            response = await list_task_attempts_v1_workspaces__workspace_id__tasks__task_identifier__attempts__get(
                workspace_id=workspace_id, task_identifier=task_id
            )

            attempts = response.data.items

            if not attempts:
                console.print(f"[yellow]No attempts found for task {task_id}[/yellow]")
                return

            # Create table
            table = Table(title=f"Attempts for {task_id}")
            table.add_column("ID", style="cyan", no_wrap=True)
            table.add_column("Status", style="white")
            table.add_column("Duration", style="yellow", justify="right")
            table.add_column("Tokens", style="magenta", justify="right")
            table.add_column("Started", style="dim")

            for attempt in attempts:
                table.add_row(
                    str(attempt.id),
                    attempt.status or "-",
                    format_duration(attempt.wall_clock_ms),
                    format_tokens(attempt.cost_tokens),
                    format_timestamp(attempt.started_at),
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(_list_attempts())


@app.command("show")
def show_attempt(
    attempt_id: int = typer.Argument(..., help="Attempt ID"),
) -> None:
    """Show attempt details and artifacts."""

    async def _show_attempt() -> None:
        try:
            context = ServiceContext.from_config()
            workspace_id = context.get_workspace_id()

            # Get attempt details
            attempt_response = await get_attempt_v1_workspaces__workspace_id__attempts__attempt_id__get(
                workspace_id=workspace_id, attempt_id=attempt_id
            )
            attempt = attempt_response.data

            # Get attempt artifacts
            artifacts_response = await list_attempt_artifacts_v1_workspaces__workspace_id__attempts__attempt_id__artifacts__get(
                workspace_id=workspace_id, attempt_id=attempt_id
            )
            artifacts = artifacts_response.data.items

            # Display attempt details
            console.print(f"\n[bold]Attempt #{attempt.id}[/bold]")
            console.print(f"Task: {attempt.task_identifier or attempt.task_id}")
            console.print(f"Status: {attempt.status or '-'}")
            console.print(f"Started: {format_timestamp(attempt.started_at)}")
            if attempt.ended_at:
                console.print(f"Ended: {format_timestamp(attempt.ended_at)}")
            console.print(f"Duration: {format_duration(attempt.wall_clock_ms)}")
            console.print(f"Tokens: {format_tokens(attempt.cost_tokens)}")

            if attempt.failure_message:
                console.print(f"\n[red]Failure:[/red] {attempt.failure_message}")
                if attempt.failure_class:
                    console.print(f"Class: {attempt.failure_class}")

            # Display artifacts
            if artifacts:
                console.print("\n[bold]Artifacts[/bold]")
                table = Table()
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Type", style="white")
                table.add_column("Name", style="yellow")
                table.add_column("Size", style="magenta", justify="right")

                for artifact in artifacts:
                    table.add_row(
                        str(artifact.id),
                        artifact.type,
                        artifact.name,
                        format_size(artifact.size_bytes or 0),
                    )

                console.print(table)
            else:
                console.print("\n[dim]No artifacts[/dim]")

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(_show_attempt())
