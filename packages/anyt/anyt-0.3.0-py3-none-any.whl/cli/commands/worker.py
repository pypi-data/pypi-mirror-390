"""
Worker commands for running automated task processing.
"""

import asyncio
import tempfile
from importlib import resources
from pathlib import Path
from typing import Optional

import typer
from keyring.errors import KeyringError
from rich.console import Console
from rich.table import Table

from cli.worker.coordinator import TaskCoordinator
from cli.worker.secrets import SecretsManager
from cli.worker.workflows import BUILT_IN_WORKFLOWS

app = typer.Typer(help="Automated task worker commands")
secret_app = typer.Typer(help="Manage workflow secrets")
app.add_typer(secret_app, name="secret")
console = Console()


def resolve_workflow_file(
    workflow_name: str,
    workspace: Path,
    custom_dir: Optional[Path] = None,
) -> Path:
    """
    Resolve workflow file with priority:
    1. Custom directory (if specified)
    2. Workspace .anyt/workflows/ (user override)
    3. Package built-in workflows

    Args:
        workflow_name: Name of the workflow (without .yaml extension)
        workspace: Workspace directory path
        custom_dir: Optional custom workflows directory

    Returns:
        Path to the workflow file

    Raises:
        ValueError: If workflow file is not found in any location
    """
    workflow_filename = f"{workflow_name}.yaml"

    # Priority 1: Custom directory (highest priority)
    if custom_dir:
        workflow_path = custom_dir / workflow_filename
        if workflow_path.exists():
            return workflow_path
        raise ValueError(f"Workflow file not found: {workflow_path}")

    # Priority 2: Workspace override (user can override built-ins)
    workspace_path = workspace / ".anyt" / "workflows" / workflow_filename
    if workspace_path.exists():
        return workspace_path

    # Priority 3: Package built-in workflows
    if workflow_name in BUILT_IN_WORKFLOWS:
        # Read from package resources and write to temp file
        # TaskCoordinator needs a file path to load the workflow
        try:
            workflow_content = (
                resources.files("cli.worker.workflows")
                .joinpath(workflow_filename)
                .read_text()
            )

            # Write to temp file for TaskCoordinator to load
            temp_dir = Path(tempfile.mkdtemp())
            temp_file = temp_dir / workflow_filename
            temp_file.write_text(workflow_content)
            return temp_file
        except (FileNotFoundError, AttributeError) as e:
            raise ValueError(
                f"Built-in workflow '{workflow_name}' not found in package: {e}"
            ) from e

    # Not found anywhere
    available = ", ".join(BUILT_IN_WORKFLOWS)
    raise ValueError(
        f"Workflow '{workflow_name}' not found. "
        f"Available built-in workflows: {available}"
    )


@app.command()
def start(
    workspace_dir: Optional[Path] = typer.Option(
        None,
        "--workspace",
        "-w",
        help="Workspace directory (default: current directory)",
    ),
    workflow: Optional[str] = typer.Option(
        None,
        "--workflow",
        help="Built-in workflow to run (local_dev, feature_development, general_task). When specified, runs ONLY this workflow.",
    ),
    workflows_dir: Optional[Path] = typer.Option(
        None,
        "--workflows",
        help="Workflows directory (default: .anyt/workflows). If --workflow is specified, loads from this directory.",
    ),
    poll_interval: int = typer.Option(
        5,
        "--poll-interval",
        "-i",
        help="Polling interval in seconds",
    ),
    max_backoff: int = typer.Option(
        60,
        "--max-backoff",
        help="Maximum backoff interval in seconds",
    ),
    agent_id: Optional[str] = typer.Option(
        None,
        "--agent-id",
        "-a",
        help="Agent identifier to filter tasks (e.g., agent-xxx). Get from https://anyt.dev/home/agents.",
    ),
    project_id: Optional[int] = typer.Option(
        None,
        "--project-id",
        "-p",
        help="Project ID to scope task suggestions. If not provided, loads from .anyt/anyt.json (current_project_id field).",
    ),
) -> None:
    """
    Start the Claude task worker.

    The worker continuously polls for tasks and executes workflows automatically.

    Setup:
    1. Set ANYT_API_KEY environment variable for API authentication
    2. Get your agent identifier from https://anyt.dev/home/agents
    3. Pass agent identifier via --agent-id flag

    Note: ANYT_API_KEY (API key) and agent-id (agent identifier) are different:
    - ANYT_API_KEY: API key for authentication (e.g., anyt_agent_...)
    - agent-id: Agent identifier to filter tasks (e.g., agent-xxx)

    Workflow Options:
    - No options: Runs ALL workflows from .anyt/workflows/
    - --workflow local_dev: Runs ONLY local_dev workflow (from package or workspace)
    - --workflows-dir /custom: Runs ALL workflows from /custom directory
    - --workflow local_dev --workflows-dir /custom: Runs ONLY local_dev from /custom

    Built-in workflows (bundled with CLI, no setup required):
    - local_dev: Direct implementation on current repository
    - feature_development: Full feature workflow with branch management
    - general_task: General-purpose task execution

    Example:
        export ANYT_API_KEY=anyt_agent_...  # API key for authentication
        anyt worker start --agent-id agent-xxx  # Agent identifier from https://anyt.dev/home/agents
        anyt worker start --workflow local_dev --agent-id agent-xxx
        anyt worker start --agent-id agent-xxx --project-id 123
        anyt worker start --poll-interval 10 --workspace /path/to/project --agent-id agent-xxx
    """
    workspace = workspace_dir or Path.cwd()

    if not workspace.exists():
        console.print(
            f"[red]Error: Workspace directory does not exist: {workspace}[/red]"
        )
        raise typer.Exit(1)

    # Load workspace config to get defaults
    from cli.config import WorkspaceConfig

    workspace_config = WorkspaceConfig.load(workspace)
    if not workspace_config:
        console.print(
            f"[red]Error: No workspace config found at {workspace}/.anyt/anyt.json[/red]"
        )
        console.print(
            "[yellow]Hint: Initialize workspace with 'anyt workspace init'[/yellow]"
        )
        raise typer.Exit(1)

    # Require agent_id
    if not agent_id:
        console.print("[red]Error: --agent-id is required[/red]")
        console.print()
        console.print(
            "[yellow]The --agent-id flag specifies which agent's tasks to work on.[/yellow]"
        )
        console.print()
        console.print("[cyan]Steps:[/cyan]")
        console.print("  1. Go to https://anyt.dev/home/agents")
        console.print("  2. Find your agent identifier (e.g., agent-xxx)")
        console.print("  3. Run: anyt worker start --agent-id agent-xxx")
        console.print()
        console.print("[dim]Note: agent-id is different from ANYT_API_KEY[/dim]")
        console.print(
            "  [dim]- ANYT_API_KEY: API key for authentication (anyt_agent_...)[/dim]"
        )
        console.print(
            "  [dim]- agent-id: Agent identifier to filter tasks (agent-...)[/dim]"
        )
        raise typer.Exit(1)

    # Use config defaults if not provided via CLI
    effective_project_id = project_id or workspace_config.current_project_id

    console.print(f"[dim]Using agent_id: {agent_id}[/dim]")
    if effective_project_id:
        console.print(f"[dim]Using project_id: {effective_project_id}[/dim]")

    # Resolve workflow file if --workflow is specified
    workflow_file: Optional[Path] = None
    if workflow:
        try:
            workflow_file = resolve_workflow_file(workflow, workspace, workflows_dir)
            console.print(
                f"[green]Using workflow:[/green] {workflow} (from {workflow_file.parent})"
            )
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    # Create coordinator and run
    coordinator = TaskCoordinator(
        workspace_dir=workspace,
        workflows_dir=workflows_dir,
        workflow_file=workflow_file,  # NEW: Pass specific workflow or None
        poll_interval=poll_interval,
        max_backoff=max_backoff,
        agent_id=agent_id,
        project_id=effective_project_id,
    )

    try:
        asyncio.run(coordinator.run())
    except KeyboardInterrupt:
        console.print("\n[yellow]Worker stopped by user[/yellow]")


@app.command()
def list_workflows(
    workflows_dir: Optional[Path] = typer.Option(
        None,
        "--workflows",
        help="Workflows directory (default: .anyt/workflows)",
    ),
) -> None:
    """List available workflows."""
    import yaml

    workflows_path = workflows_dir or Path.cwd() / ".anyt" / "workflows"

    if not workflows_path.exists():
        console.print(
            f"[yellow]No workflows directory found at: {workflows_path}[/yellow]"
        )
        return

    table = Table(title="Available Workflows")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Triggers", style="yellow")

    workflows = list(workflows_path.glob("*.yaml"))
    if not workflows:
        console.print(f"[yellow]No workflows found in: {workflows_path}[/yellow]")
        return

    for workflow_file in workflows:
        try:
            with open(workflow_file) as f:
                data = yaml.safe_load(f)
                name = data.get("name", workflow_file.stem)
                description = data.get("description", "")
                triggers: list[str] = []

                if "on" in data:
                    if "task_created" in data["on"]:
                        triggers.append("task_created")
                    if "task_updated" in data["on"]:
                        triggers.append("task_updated")

                table.add_row(name, description, ", ".join(triggers))
        except Exception as e:
            console.print(f"[red]Error loading {workflow_file}: {e}[/red]")

    console.print(table)


@app.command()
def validate_workflow(
    workflow_file: Path = typer.Argument(..., help="Workflow file to validate"),
) -> None:
    """Validate a workflow definition."""
    import yaml
    from pydantic import ValidationError

    from cli.worker.models import Workflow

    if not workflow_file.exists():
        console.print(f"[red]Error: Workflow file not found: {workflow_file}[/red]")
        raise typer.Exit(1)

    try:
        with open(workflow_file) as f:
            data = yaml.safe_load(f)

        workflow = Workflow(**data)

        console.print(f"[green]✓ Workflow is valid:[/green] {workflow.name}")
        console.print(f"  Description: {workflow.description or 'N/A'}")
        console.print(f"  Jobs: {len(workflow.jobs)}")
        for job_name, job in workflow.jobs.items():
            console.print(f"    - {job.name}: {len(job.steps)} steps")

    except ValidationError as e:
        console.print("[red]✗ Workflow validation failed:[/red]")
        console.print(e)
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


# Secret management commands


@secret_app.command("set")
def secret_set(
    name: str = typer.Argument(..., help="Secret name (e.g., API_KEY)"),
    value: Optional[str] = typer.Option(
        None, "--value", "-v", help="Secret value (or will prompt)"
    ),
) -> None:
    """
    Store a secret securely in the system keyring.

    If value is not provided, you will be prompted to enter it securely.

    Example:
        anyt worker secret set PRODUCTION_API_KEY --value abc123
        anyt worker secret set DB_PASSWORD  # Will prompt
    """
    try:
        manager = SecretsManager()

        # Prompt for value if not provided
        if value is None:
            value = typer.prompt(f"Enter value for secret '{name}'", hide_input=True)

        # Value is guaranteed to be a string at this point (either provided or from prompt)
        assert value is not None
        manager.set_secret(name, value)
        console.print(f"[green]✓ Secret '{name}' stored successfully[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)


@secret_app.command("get")
def secret_get(
    name: str = typer.Argument(..., help="Secret name to retrieve"),
    show: bool = typer.Option(False, "--show", help="Show the secret value"),
) -> None:
    """
    Retrieve a secret from the keyring.

    By default, the secret value is masked. Use --show to display it.

    Example:
        anyt worker secret get API_KEY
        anyt worker secret get API_KEY --show
    """
    try:
        manager = SecretsManager()
        value = manager.get_secret(name)

        if value is None:
            console.print(f"[yellow]Secret '{name}' not found[/yellow]")
            raise typer.Exit(1)

        if show:
            console.print(f"[cyan]{name}:[/cyan] {value}")
        else:
            masked = manager.mask_secret(value)
            console.print(f"[cyan]{name}:[/cyan] {masked}")
            console.print("[dim]Use --show to display the full value[/dim]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)


@secret_app.command("delete")
def secret_delete(
    name: str = typer.Argument(..., help="Secret name to delete"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """
    Delete a secret from the keyring.

    Example:
        anyt worker secret delete OLD_API_KEY
        anyt worker secret delete OLD_API_KEY --yes
    """
    try:
        manager = SecretsManager()

        # Check if secret exists
        if manager.get_secret(name) is None:
            console.print(f"[yellow]Secret '{name}' not found[/yellow]")
            raise typer.Exit(1)

        # Confirm deletion
        if not yes:
            confirm = typer.confirm(f"Delete secret '{name}'?")
            if not confirm:
                console.print("[yellow]Cancelled[/yellow]")
                return

        manager.delete_secret(name)
        console.print(f"[green]✓ Secret '{name}' deleted[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)


@secret_app.command("test")
def secret_test(
    text: str = typer.Argument(..., help="Text with secret placeholders to test"),
) -> None:
    r"""
    Test secret interpolation with a sample text.

    This is useful for verifying your secrets are configured correctly.

    Example:
        anyt worker secret test "API_KEY=\${{ secrets.API_KEY }}"
    """
    try:
        manager = SecretsManager()
        result = manager.interpolate_secrets(text)

        console.print("[green]✓ Interpolation successful[/green]")
        console.print(f"[cyan]Input:[/cyan]  {text}")
        console.print(f"[cyan]Output:[/cyan] {result}")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except KeyringError as e:
        console.print(f"[red]Keyring error: {e}[/red]")
        raise typer.Exit(1)
