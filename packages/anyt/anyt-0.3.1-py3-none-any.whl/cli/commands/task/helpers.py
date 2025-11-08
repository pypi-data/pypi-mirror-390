"""Helper functions for task commands."""

from datetime import datetime, timedelta
from typing import Any, Optional

from cli.config import ActiveTaskConfig, WorkspaceConfig, get_effective_api_config
from cli.services.workspace_service import WorkspaceService
from cli.services.task_service import TaskService
from cli.models.task import TaskFilters
from rich.console import Console

import typer

console = Console()

# Workspace resolution cache
# Maps (workspace_identifier_or_id) -> (workspace_id, workspace_identifier, timestamp)
_workspace_cache: dict[str, tuple[int, str, datetime]] = {}
_CACHE_TTL = timedelta(minutes=5)


def clear_workspace_cache() -> None:
    """Clear the workspace resolution cache.

    Call this when switching workspaces or when you want to force
    a fresh lookup from the API.
    """
    global _workspace_cache
    _workspace_cache.clear()


def get_workspace_or_exit() -> WorkspaceConfig:
    """Load workspace config or exit with error.

    Returns:
        WorkspaceConfig

    Raises:
        typer.Exit: If workspace is not initialized or config cannot be loaded
    """
    # Check if workspace is initialized
    ws_config = WorkspaceConfig.load()
    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt workspace init[/cyan] first")
        raise typer.Exit(1)

    # Check authentication
    try:
        get_effective_api_config()
    except RuntimeError:
        console.print("[red]Error:[/red] Not authenticated")
        console.print("\nSet the ANYT_API_KEY environment variable:")
        console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
        raise typer.Exit(1)

    return ws_config


async def resolve_workspace_context(
    workspace_arg: Optional[str],
    workspace_service: WorkspaceService,
) -> tuple[int, str]:
    """Resolve workspace context from --workspace flag or local workspace.

    Uses a cache to avoid repeated API calls for workspace resolution.
    Cache expires after 5 minutes.

    Priority order:
    1. --workspace flag (if provided)
    2. Local .anyt/anyt.json workspace

    Args:
        workspace_arg: Workspace identifier or ID from --workspace flag
        workspace_service: WorkspaceService for fetching workspace details

    Returns:
        Tuple of (workspace_id, workspace_identifier)

    Raises:
        typer.Exit: If workspace cannot be resolved or is invalid
    """
    # Priority 1: Explicit --workspace flag
    if workspace_arg:
        # Check cache first
        cache_key = workspace_arg.upper()
        if cache_key in _workspace_cache:
            cached_id, cached_identifier, cached_time = _workspace_cache[cache_key]
            if datetime.now() - cached_time < _CACHE_TTL:
                return cached_id, cached_identifier

        # Fetch all workspaces to resolve identifier or ID
        workspaces = await workspace_service.list_workspaces()
        for ws in workspaces:
            if str(ws.id) == workspace_arg or ws.identifier == workspace_arg.upper():
                # Update cache
                _workspace_cache[cache_key] = (
                    ws.id,
                    ws.identifier,
                    datetime.now(),
                )
                return ws.id, ws.identifier

        console.print(f"[red]Error:[/red] Workspace '{workspace_arg}' not found")
        console.print("\nAvailable workspaces:")
        for ws in workspaces:
            console.print(f"  {ws.identifier} - {ws.name} (ID: {ws.id})")
        raise typer.Exit(1)

    # Priority 2: Local .anyt/anyt.json workspace
    ws_config = WorkspaceConfig.load()
    if ws_config:
        workspace_id = int(ws_config.workspace_id)
        workspace_identifier = ws_config.workspace_identifier or "UNKNOWN"
        return workspace_id, workspace_identifier

    # No workspace found
    console.print("[red]Error:[/red] No workspace context available")
    console.print("\nOptions:")
    console.print("  1. Initialize workspace: [cyan]anyt workspace init[/cyan]")
    console.print("  2. Use --workspace flag: [cyan]--workspace DEV[/cyan]")
    raise typer.Exit(1)


def format_priority(priority: int) -> str:
    """Format priority as visual dots.

    Priority scale: -2 (lowest) to 2 (highest)
    """
    if priority >= 2:
        return "●●●"
    elif priority == 1:
        return "●●○"
    elif priority == 0:
        return "●○○"
    elif priority == -1:
        return "○○○"
    else:  # -2 or lower
        return "○○○"


def format_relative_time(dt_str: Optional[str]) -> str:
    """Format datetime string as relative time (e.g., '2h ago')."""
    if not dt_str:
        return "—"

    try:
        # Parse ISO format datetime
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        now = datetime.now(dt.tzinfo)
        delta = now - dt

        seconds = int(delta.total_seconds())

        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = seconds // 3600
            return f"{hours}h ago"
        elif seconds < 604800:
            days = seconds // 86400
            return f"{days}d ago"
        else:
            weeks = seconds // 604800
            return f"{weeks}w ago"
    except Exception:
        return dt_str


def truncate_text(text: str, max_length: int = 40) -> str:
    """Truncate text to max_length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 1] + "…"


def get_active_task_id() -> Optional[str]:
    """Get the active task identifier from .anyt/active_task.json.

    Returns:
        Task identifier if an active task is set, None otherwise.
    """
    active_task = ActiveTaskConfig.load()
    return active_task.identifier if active_task else None


async def resolve_task_identifier(
    identifier: str, task_service: TaskService, workspace_prefix: Optional[str] = None
) -> str:
    """Resolve task identifier, converting UIDs to workspace-scoped identifiers.

    This function enables commands to accept both UIDs (t_xxx) and workspace identifiers (DEV-42).
    UIDs are converted to workspace identifiers by fetching the task.

    Handles:
    - UIDs (t_xxx) → Fetches task and returns workspace identifier (DEV-42)
    - Workspace identifiers (DEV-42) → Normalizes and returns
    - Numeric IDs (42) → Normalizes with workspace prefix

    Args:
        identifier: Task identifier (UID, workspace identifier, or numeric ID)
        task_service: TaskService for fetching task details
        workspace_prefix: Workspace prefix (e.g., "DEV") to use if identifier is just a number

    Returns:
        Workspace-scoped task identifier (e.g., DEV-42)

    Raises:
        Exception: If task not found or UID is invalid
    """
    identifier = identifier.strip()

    # Check if it's a UID (starts with 't_')
    if identifier.startswith("t_"):
        # Fetch task by UID to get workspace identifier
        task = await task_service.get_task_by_uid(identifier)
        # Type annotation: identifier is a string attribute from the generated model
        return str(task.identifier)

    # Otherwise, normalize the identifier
    return normalize_identifier(identifier, workspace_prefix)


def normalize_identifier(task_id: str, workspace_prefix: Optional[str] = None) -> str:
    """Normalize task identifier for fuzzy matching.

    Handles variations like:
    - DEV-42 → DEV-42 (full identifier)
    - dev42 → DEV-42 (case insensitive, no dash)
    - 42 → 42 (just number)
    - DEV 42 → DEV-42 (with space)

    Args:
        task_id: The task identifier to normalize
        workspace_prefix: Workspace prefix (e.g., "DEV") to use if identifier is just a number

    Returns:
        Normalized task identifier
    """
    task_id = task_id.strip()

    # If it's just a number, prepend workspace prefix if provided
    if task_id.isdigit():
        if workspace_prefix:
            return f"{workspace_prefix}-{task_id}"
        return task_id

    # If it contains a dash already (DEV-42), normalize case
    if "-" in task_id:
        parts = task_id.split("-", 1)
        return f"{parts[0].upper()}-{parts[1]}"

    # If it contains a space (DEV 42), replace with dash
    if " " in task_id:
        parts = task_id.split(" ", 1)
        return f"{parts[0].upper()}-{parts[1]}"

    # Try to split alphanumeric (dev42 → DEV-42)
    # Find where digits start
    for i, char in enumerate(task_id):
        if char.isdigit():
            if i > 0:
                prefix = task_id[:i].upper()
                number = task_id[i:]
                return f"{prefix}-{number}"
            break

    # If nothing matched, return as uppercase
    return task_id.upper()


def output_json(data: dict[str, Any], success: bool = True) -> None:
    """Output data as JSON to stdout.

    Args:
        data: The data to output as JSON
        success: Whether this is a success response (affects structure)
    """
    import json

    output: dict[str, Any]
    if success:
        output = {"success": True, "data": data}
    else:
        output = {"success": False, **data}

    print(json.dumps(output, indent=2))


async def find_similar_tasks(
    task_service: TaskService, workspace_id: int, identifier: str, limit: int = 3
) -> list[dict[str, Any]]:
    """Find tasks with similar identifiers using fuzzy matching.

    Args:
        task_service: TaskService for fetching tasks
        workspace_id: Workspace ID to search in
        identifier: The identifier that wasn't found
        limit: Maximum number of suggestions to return

    Returns:
        List of similar tasks (as dicts for backward compatibility)
    """
    import difflib

    try:
        # Fetch recent tasks from workspace
        filters = TaskFilters(
            workspace_id=workspace_id, limit=50, sort_by="updated_at", order="desc"
        )
        tasks = await task_service.list_tasks(filters)

        if not tasks:
            return []

        # Get all task identifiers
        identifiers = [task.identifier or str(task.id) for task in tasks]

        # Use difflib to find similar matches
        matches = difflib.get_close_matches(
            identifier.upper(),
            [id.upper() for id in identifiers],
            n=limit,
            cutoff=0.4,  # Lower cutoff for more suggestions
        )

        # Return the corresponding tasks as dicts
        similar_tasks: list[dict[str, Any]] = []
        for match in matches:
            for task in tasks:
                task_id = task.identifier or str(task.id)
                if task_id.upper() == match:
                    # Convert Task model to dict for backward compatibility
                    similar_tasks.append(task.model_dump())
                    break

        return similar_tasks

    except Exception:
        return []
