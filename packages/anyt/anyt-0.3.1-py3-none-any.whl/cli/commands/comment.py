"""CLI commands for task comments."""

import asyncio
import json
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from cli.client.comments import CommentsAPIClient
from cli.client.exceptions import APIError, NotFoundError, ValidationError
from cli.commands.task.helpers import get_active_task_id, get_workspace_or_exit
from cli.models.comment import CommentCreate
from cli.utils.errors import handle_api_error

app = typer.Typer(help="Manage task comments")
console = Console()


@app.command("add")
def add_comment(
    identifier: Optional[str] = typer.Argument(
        None, help="Task identifier (e.g., DEV-42). Uses active task if not provided."
    ),
    message: str = typer.Option(..., "--message", "-m", help="Comment content"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Add a comment to a task.

    Examples:
        # Add comment to active task
        anyt comment add -m "Completed implementation"

        # Add comment to specific task
        anyt comment add DEV-123 -m "Found edge case"
    """
    asyncio.run(_add_comment_async(identifier, message, json_output))


async def _add_comment_async(
    identifier: Optional[str], message: str, json_output: bool
) -> None:
    """Async implementation of add_comment."""
    # Get workspace config and verify authentication
    workspace_config = get_workspace_or_exit()

    # Resolve task identifier
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            console.print(
                "[red]Error:[/red] No task identifier provided and no active task set"
            )
            console.print(
                "Use [cyan]anyt task pick <task-id>[/cyan] to set active task"
            )
            raise typer.Exit(1)

    try:
        # Create API clients
        from cli.client.tasks import TasksAPIClient
        from cli.config import get_effective_api_config

        client = CommentsAPIClient.from_config()
        tasks_client = TasksAPIClient.from_config()

        # Get task to obtain numeric ID
        task = await tasks_client.get_task_by_workspace(
            workspace_config.workspace_id, identifier
        )

        # Determine author_id and author_type
        effective_config = get_effective_api_config()
        api_key = effective_config.get("api_key")

        if not api_key:
            console.print("[red]Error:[/red] Not authenticated")
            console.print("\nSet the ANYT_API_KEY environment variable:")
            console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
            raise typer.Exit(1)

        # Agent context - use api_key
        author_id = api_key
        author_type = "agent"

        # Create comment
        comment_data = CommentCreate(
            content=message,
            task_id=task.id,
            author_id=author_id,
            author_type=author_type,
        )
        comment = await client.create_comment(identifier, comment_data)

        if json_output:
            output: dict[str, Any] = {
                "success": True,
                "data": comment.model_dump(mode="json"),
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            console.print(
                f"[green]✓[/green] Comment added to task [cyan]{identifier}[/cyan]"
            )

    except NotFoundError:
        console.print(f"[red]Error:[/red] Task '{identifier}' not found")
        raise typer.Exit(1)
    except ValidationError as e:
        console.print(f"[red]Error:[/red] Invalid comment data: {e}")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        # Catch any unexpected errors
        handle_api_error(e, "adding comment")


@app.command("list")
def list_comments(
    identifier: Optional[str] = typer.Argument(
        None, help="Task identifier (e.g., DEV-42). Uses active task if not provided."
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List all comments on a task.

    Examples:
        # List comments on active task
        anyt comment list

        # List comments on specific task
        anyt comment list DEV-123

        # JSON output
        anyt comment list DEV-123 --json
    """
    asyncio.run(_list_comments_async(identifier, json_output))


async def _list_comments_async(identifier: Optional[str], json_output: bool) -> None:
    """Async implementation of list_comments."""
    # Verify workspace and authentication
    get_workspace_or_exit()

    # Resolve task identifier
    if not identifier:
        identifier = get_active_task_id()
        if not identifier:
            console.print(
                "[red]Error:[/red] No task identifier provided and no active task set"
            )
            console.print(
                "Use [cyan]anyt task pick <task-id>[/cyan] to set active task"
            )
            raise typer.Exit(1)

    try:
        # Create API client
        client = CommentsAPIClient.from_config()

        # Fetch comments
        comments = await client.list_comments(identifier)

        if json_output:
            output: dict[str, Any] = {
                "success": True,
                "data": {
                    "task_identifier": identifier,
                    "comments": [c.model_dump(mode="json") for c in comments],
                },
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            if not comments:
                console.print(f"No comments on task [cyan]{identifier}[/cyan]")
                return

            # Display comments in a table
            table = Table(title=f"Comments on {identifier}")
            table.add_column("ID", style="dim")
            table.add_column("Content", style="white")
            table.add_column("Created", style="cyan")
            table.add_column("User ID", style="dim")

            for comment in comments:
                # Format timestamp
                timestamp_str = comment.created_at.strftime("%Y-%m-%d %H:%M:%S")

                # Truncate long comments
                content = comment.content
                if len(content) > 80:
                    content = content[:77] + "..."

                table.add_row(
                    str(comment.id),
                    content,
                    timestamp_str,
                    str(comment.user_id),
                )

            console.print(table)
            console.print(f"\n[dim]Total: {len(comments)} comment(s)[/dim]")

    except NotFoundError:
        console.print(f"[red]Error:[/red] Task '{identifier}' not found")
        raise typer.Exit(1)
    except APIError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        # Catch any unexpected errors
        handle_api_error(e, "listing comments")
