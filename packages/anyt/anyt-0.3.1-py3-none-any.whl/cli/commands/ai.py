"""AI-powered task management commands."""

import asyncio
import json
import typer
from typing_extensions import Annotated
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from cli.config import get_effective_api_config, WorkspaceConfig
from cli.client.ai import AIAPIClient
from cli.client.tasks import TasksAPIClient
from cli.ai_config import AIConfig

app = typer.Typer(help="AI-powered task management")
console = Console()


def get_workspace_or_exit() -> WorkspaceConfig:
    """Load workspace config or exit with error."""
    ws_config = WorkspaceConfig.load()
    if not ws_config:
        console.print("[red]Error:[/red] Not in a workspace directory")
        console.print("Run [cyan]anyt workspace init[/cyan] first")
        raise typer.Exit(1)

    try:
        get_effective_api_config()
    except RuntimeError:
        console.print("[red]Error:[/red] Not authenticated")
        console.print("\nSet the ANYT_API_KEY environment variable:")
        console.print("  [cyan]export ANYT_API_KEY=anyt_agent_...[/cyan]")
        raise typer.Exit(1)

    return ws_config


@app.command("decompose")
def decompose_goal(
    goal: Annotated[str, typer.Argument(help="Goal description or goal ID")],
    max_tasks: Annotated[
        int,
        typer.Option("--max-tasks", help="Maximum number of tasks to generate"),
    ] = 10,
    task_size: Annotated[
        int,
        typer.Option("--task-size", help="Preferred task size in hours"),
    ] = 4,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview tasks without creating them"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Decompose a goal into actionable tasks using AI.

    Examples:
        anyt ai decompose "Add social login"
        anyt ai decompose "Add social login" --dry-run
        anyt ai decompose "Add social login" --max-tasks 10 --task-size 3
    """
    ws_config = get_workspace_or_exit()
    client: AIAPIClient = AIAPIClient.from_config()

    async def decompose() -> None:
        try:
            workspace_id = int(ws_config.workspace_id)

            if not json_output:
                console.print("🤖 Decomposing goal...")
                console.print()
                console.print(f"Goal: {goal}")
                console.print()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                if not json_output:
                    task_progress = progress.add_task(
                        "Analyzing project structure...", total=None
                    )

                if not json_output:
                    progress.update(
                        task_progress, description="Generating task breakdown..."
                    )

                # Call actual decompose endpoint
                response = await client.decompose_goal(
                    goal=goal,
                    workspace_id=workspace_id,
                    max_tasks=max_tasks,
                    task_size=task_size,
                )

            if json_output:
                print(json.dumps(response.model_dump(mode="json"), indent=2))
            else:
                console.print("[green]✓[/green] Decomposition complete")
                console.print()

                # Display summary
                summary = response.summary if response.summary else ""
                if summary:
                    console.print(f"Summary: {summary}")
                    console.print()

                tasks_count = len(response.tasks)
                deps_count = len(response.dependencies)
                console.print(f"Tasks created: {tasks_count}")
                console.print(f"Dependencies: {deps_count}")

                # Display token usage if available
                if response.cost_tokens:
                    cost_usd = response.cost_tokens * 0.003 / 1000  # Rough estimate
                    console.print(
                        f"Cost: ~{response.cost_tokens} tokens (${cost_usd:.2f})"
                    )

                if response.cache_hit:
                    console.print("[dim]Cache hit - no API cost[/dim]")

        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                console.print(f"[red]Error:[/red] Failed to decompose goal: {e}")
            raise typer.Exit(1)

    asyncio.run(decompose())


@app.command("organize")
def organize_workspace(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Preview changes without applying them"),
    ] = False,
    titles_only: Annotated[
        bool,
        typer.Option("--titles-only", help="Only normalize task titles"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Organize workspace tasks using AI.

    This command analyzes your workspace and suggests improvements:
    - Normalize task titles to follow conventions
    - Suggest appropriate labels for tasks
    - Detect potential duplicate tasks

    Examples:
        anyt ai organize --dry-run
        anyt ai organize --titles-only
    """
    ws_config = get_workspace_or_exit()
    client: AIAPIClient = AIAPIClient.from_config()

    async def organize() -> None:
        try:
            workspace_id = int(ws_config.workspace_id)

            # Determine actions based on flags
            actions = []
            if titles_only:
                actions = ["normalize_titles"]
            else:
                actions = ["normalize_titles", "suggest_labels", "detect_duplicates"]

            if not json_output:
                console.print("🤖 Organizing workspace...")
                console.print()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                if not json_output:
                    progress.add_task("Analyzing tasks...", total=None)

                # Call actual organize endpoint
                response = await client.organize_workspace(
                    workspace_id=workspace_id, actions=actions, dry_run=dry_run
                )

            if json_output:
                print(json.dumps(response.model_dump(mode="json"), indent=2))
            else:
                if dry_run:
                    console.print("[green]✓[/green] Organization preview")
                else:
                    console.print("[green]✓[/green] Organization complete")
                console.print()

                normalized = len(response.normalized_tasks)
                label_sugg = len(response.label_suggestions)
                duplicates = len(response.duplicates)

                if normalized > 0:
                    console.print(f"Title normalization: {normalized} suggestions")
                if label_sugg > 0:
                    console.print(f"Label suggestions: {label_sugg} tasks")
                if duplicates > 0:
                    console.print(f"Potential duplicates: {duplicates} pairs")

                if response.cost_tokens:
                    cost_usd = response.cost_tokens * 0.003 / 1000
                    console.print(
                        f"Cost: ~{response.cost_tokens} tokens (${cost_usd:.2f})"
                    )

                if dry_run:
                    console.print()
                    console.print("[dim]Run without --dry-run to apply changes[/dim]")

        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                console.print(f"[red]Error:[/red] Failed to organize workspace: {e}")
            raise typer.Exit(1)

    asyncio.run(organize())


@app.command("fill")
def fill_task(
    identifier: Annotated[str, typer.Argument(help="Task identifier (e.g., DEV-42)")],
    fields: Annotated[
        Optional[str],
        typer.Option(
            "--fields",
            help="Comma-separated fields to fill (description,acceptance,labels)",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Fill in missing details for a task using AI.

    Examples:
        anyt ai fill DEV-42
        anyt ai fill DEV-42 --fields description,acceptance
        anyt ai fill DEV-42 --fields labels
    """
    ws_config = get_workspace_or_exit()
    client: AIAPIClient = AIAPIClient.from_config()

    async def fill() -> None:
        try:
            if not json_output:
                console.print(f"🤖 Analyzing task {identifier}...")
                console.print()

            # Parse fields to fill
            fields_list = None
            if fields:
                fields_list = [f.strip() for f in fields.split(",")]

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                if not json_output:
                    progress.add_task("Generating content...", total=None)

                # Call actual auto-fill endpoint
                response = await client.fill_task_details(
                    identifier=identifier,
                    workspace_id=ws_config.workspace_id,
                    fields=fields_list,
                )

            if json_output:
                print(json.dumps(response.model_dump(mode="json"), indent=2))
            else:
                console.print(f"[green]✓[/green] Content generated for {identifier}")
                console.print()

                if response.generated:
                    console.print("Generated content:")
                    for field, value in response.generated.items():
                        console.print(
                            f"  {field}: {value[:100]}..."
                            if len(str(value)) > 100
                            else f"  {field}: {value}"
                        )

                if response.cost_tokens:
                    cost_usd = response.cost_tokens * 0.003 / 1000
                    console.print(
                        f"\nCost: ~{response.cost_tokens} tokens (${cost_usd:.2f})"
                    )

        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                console.print(f"[red]Error:[/red] Failed to fill task: {e}")
            raise typer.Exit(1)

    asyncio.run(fill())


@app.command("suggest")
def suggest_tasks(
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Get AI suggestions for next task to work on.

    Analyzes the workspace and recommends tasks based on:
    - Priority and dependencies
    - Unblocking downstream tasks
    - Quick wins and impact
    """
    ws_config = get_workspace_or_exit()
    client: AIAPIClient = AIAPIClient.from_config()

    async def suggest() -> None:
        try:
            workspace_id = int(ws_config.workspace_id)

            if not json_output:
                console.print("🤖 Analyzing workspace and task graph...")
                console.print()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                if not json_output:
                    progress.add_task("Analyzing dependencies...", total=None)

                # Call actual suggestions endpoint
                response = await client.get_ai_suggestions(workspace_id=workspace_id)

            if json_output:
                print(json.dumps(response.model_dump(mode="json"), indent=2))
            else:
                console.print("[green]Recommended tasks:[/green]")
                console.print()

                recommendations = (
                    response.recommendations
                    if response.recommendations
                    else response.recommended_tasks
                )
                if not recommendations:
                    console.print("[dim]No recommendations available[/dim]")
                else:
                    for i, rec in enumerate(recommendations, 1):
                        task_id = rec.get("task_id", "Unknown")
                        reason = rec.get("reason", "")
                        console.print(f"{i}. {task_id}")
                        if reason:
                            console.print(f"   [dim]{reason}[/dim]")

        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                console.print(f"[red]Error:[/red] Failed to get suggestions: {e}")
            raise typer.Exit(1)

    asyncio.run(suggest())


@app.command("review")
def review_task(
    identifier: Annotated[str, typer.Argument(help="Task identifier (e.g., DEV-42)")],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Get AI review of a task before marking done.

    Validates:
    - Title follows naming convention
    - Description is clear and complete
    - All acceptance criteria met
    - Dependencies satisfied
    - Tests exist and pass
    """
    get_workspace_or_exit()  # Verify workspace and authentication
    ai_client: AIAPIClient = AIAPIClient.from_config()
    task_client: TasksAPIClient = TasksAPIClient.from_config()

    async def review() -> None:
        try:
            if not json_output:
                console.print(f"🤖 Reviewing task {identifier}...")
                console.print()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                if not json_output:
                    progress.add_task("Checking acceptance criteria...", total=None)

                # Get task details first for display
                task = await task_client.get_task(identifier)

                # Call actual review endpoint
                response = await ai_client.review_task(identifier=identifier)

            if json_output:
                print(json.dumps(response.model_dump(), indent=2))
            else:
                console.print(f"[green]✓[/green] Review complete for {identifier}")
                console.print()
                console.print(f"Task: {task.title}")
                console.print(f"Status: {task.status.value}")
                console.print()

                # Show checks
                if response.checks:
                    console.print("Checklist:")
                    for check in response.checks:
                        status = "✓" if check.get("passed") else "✗"
                        console.print(f"  {status} {check.get('message', '')}")

                if response.warnings:
                    console.print()
                    console.print("[yellow]Warnings:[/yellow]")
                    for warning in response.warnings:
                        console.print(f"  ⚠ {warning}")

                console.print()
                if response.is_ready:
                    console.print("[green]Task is ready to be marked as done[/green]")
                else:
                    console.print(
                        "[yellow]Task needs more work before completion[/yellow]"
                    )

        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                console.print(f"[red]Error:[/red] Failed to review task: {e}")
            raise typer.Exit(1)

    asyncio.run(review())


@app.command("summary")
def workspace_summary(
    period: Annotated[
        str,
        typer.Option("--period", help="Summary period (today, weekly, monthly)"),
    ] = "today",
    format: Annotated[
        str,
        typer.Option("--format", help="Output format (text, markdown, slack)"),
    ] = "text",
) -> None:
    """Generate workspace progress summary.

    Examples:
        anyt ai summary
        anyt ai summary --period weekly
        anyt ai summary --format markdown > summary.md
    """
    ws_config = get_workspace_or_exit()
    client: AIAPIClient = AIAPIClient.from_config()

    async def summary() -> None:
        try:
            workspace_id = int(ws_config.workspace_id)

            console.print("🤖 Generating workspace summary...")
            console.print()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                progress.add_task("Analyzing workspace activity...", total=None)

                # Call actual summary endpoint
                response = await client.generate_summary(
                    workspace_id=workspace_id, period=period
                )

            summary_text = (
                response.summary if response.summary else response.summary_text
            )

            if format == "markdown":
                print(f"# Workspace Summary - {period.capitalize()}")
                print()
                print(summary_text)
            elif format == "slack":
                print(f"*Workspace Summary - {period.capitalize()}*")
                print()
                print(summary_text)
            else:
                console.print("━" * 70)
                console.print(f"          Workspace Summary - {period.capitalize()}")
                console.print("━" * 70)
                console.print()
                console.print(summary_text)
                console.print()

                if response.cost_tokens:
                    cost_usd = response.cost_tokens * 0.003 / 1000
                    console.print(
                        f"Cost: ~{response.cost_tokens} tokens (${cost_usd:.2f})"
                    )

        except Exception as e:
            console.print(f"[red]Error:[/red] Failed to generate summary: {e}")
            raise typer.Exit(1)

    asyncio.run(summary())


@app.command("config")
def ai_config(
    show: Annotated[
        bool,
        typer.Option("--show", help="Show current AI configuration"),
    ] = True,
    model: Annotated[
        Optional[str],
        typer.Option("--model", help="Set AI model"),
    ] = None,
    max_tokens: Annotated[
        Optional[int],
        typer.Option("--max-tokens", help="Set max tokens"),
    ] = None,
    cache: Annotated[
        Optional[str],
        typer.Option("--cache", help="Enable/disable cache (on/off)"),
    ] = None,
) -> None:
    """Manage AI provider settings.

    Examples:
        anyt ai config
        anyt ai config --model claude-haiku-4-5-20251001
        anyt ai config --max-tokens 8192
        anyt ai config --cache on
    """
    try:
        # Load AI configuration
        ai_config = AIConfig.load()

        # Update config if flags provided
        updated = False
        if model:
            ai_config.model = model
            updated = True
        if max_tokens:
            ai_config.max_tokens = max_tokens
            updated = True
        if cache:
            ai_config.cache_enabled = cache.lower() == "on"
            updated = True

        if updated:
            ai_config.save()
            console.print("[green]✓[/green] AI configuration updated")
            console.print()

        # Show current config
        console.print("AI Configuration:")
        console.print(f"  Provider: {ai_config.provider}")
        console.print(f"  Model: {ai_config.model}")
        console.print(f"  Max tokens: {ai_config.max_tokens}")
        console.print(f"  Temperature: {ai_config.temperature}")
        console.print(f"  Cache enabled: {ai_config.cache_enabled}")

        # Check if API key is configured
        api_key = ai_config.get_api_key()
        if api_key:
            console.print(f"  API key: {'*' * 8}{api_key[-4:]}")
        else:
            console.print("  API key: [yellow]Not configured[/yellow]")

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to manage AI config: {e}")
        raise typer.Exit(1)


@app.command("test")
def test_ai() -> None:
    """Test AI connection and settings."""
    try:
        console.print("🤖 Testing AI connection...")
        console.print()

        # Load AI configuration
        ai_config = AIConfig.load()

        # Check if API key is configured
        api_key = ai_config.get_api_key()
        if not api_key:
            console.print(
                f"[red]✗[/red] API key not found for provider: {ai_config.provider}"
            )
            console.print(
                f"[yellow]Hint:[/yellow] Set {ai_config.provider.upper()}_API_KEY environment variable"
            )
            raise typer.Exit(1)

        # Display configuration
        console.print("[green]✓[/green] API key configured")
        console.print(f"[green]✓[/green] Provider: {ai_config.provider}")
        console.print(f"[green]✓[/green] Model: {ai_config.model}")
        console.print(
            f"[green]✓[/green] Prompt caching: {'enabled' if ai_config.cache_enabled else 'disabled'}"
        )
        console.print()
        console.print(
            "[dim]Note: Actual API connectivity test requires backend call[/dim]"
        )

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error:[/red] AI connection test failed: {e}")
        raise typer.Exit(1)


@app.command("usage")
def ai_usage(
    workspace: Annotated[
        bool,
        typer.Option("--workspace", help="Show workspace-level usage"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Track AI token usage and costs.

    Examples:
        anyt ai usage
        anyt ai usage --workspace
        anyt ai usage --json
    """
    ws_config = get_workspace_or_exit()
    client: AIAPIClient = AIAPIClient.from_config()

    async def get_usage() -> None:
        try:
            # Get workspace ID if needed
            workspace_id = None
            if workspace:
                workspace_id = int(ws_config.workspace_id)

            # Call actual usage endpoint
            usage_data = await client.get_ai_usage(workspace_id=workspace_id)

            if json_output:
                print(json.dumps(usage_data.model_dump(mode="json"), indent=2))
            else:
                period = usage_data.period if usage_data.period else "Last 30 Days"
                console.print(f"AI Usage - {period}")
                console.print("━" * 70)
                console.print()

                # Create table
                table = Table(show_header=True, header_style="bold")
                table.add_column("Operation", style="cyan")
                table.add_column("Calls", justify="right")
                table.add_column("Tokens", justify="right")
                table.add_column("Cost", justify="right")

                operations = usage_data.operations
                for op in operations:
                    table.add_row(
                        op["name"],
                        str(op["calls"]),
                        f"{op['tokens']:,}",
                        f"${op['cost']:.2f}",
                    )

                table.add_row("─" * 10, "─" * 6, "─" * 10, "─" * 6, end_section=True)
                table.add_row(
                    "Total",
                    str(usage_data.total_calls if usage_data.total_calls else 0),
                    f"{usage_data.total_tokens:,}",
                    f"${usage_data.total_cost:.2f}",
                    style="bold",
                )

                console.print(table)
                console.print()

                # Type-safe access with proper casting
                cache_hits = usage_data.cache_hits if usage_data.cache_hits else 0
                total_calls = usage_data.total_calls if usage_data.total_calls else 1
                cache_savings = (
                    usage_data.cache_savings if usage_data.cache_savings else 0.0
                )
                total_cost = usage_data.total_cost

                if total_calls > 0:
                    console.print(
                        f"Cache hits: {cache_hits}/{total_calls} ({cache_hits * 100 // total_calls}%)"
                    )
                if total_cost > 0 and cache_savings > 0:
                    console.print(
                        f"Cache savings: ${cache_savings:.2f} ({int(cache_savings * 100 / total_cost)}%)"
                    )

        except Exception as e:
            if json_output:
                print(json.dumps({"error": str(e)}, indent=2))
            else:
                console.print(f"[red]Error:[/red] Failed to get usage data: {e}")
            raise typer.Exit(1)

    asyncio.run(get_usage())
