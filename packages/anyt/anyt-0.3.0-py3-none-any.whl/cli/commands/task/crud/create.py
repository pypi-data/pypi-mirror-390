"""Create commands for tasks (add, create from template)."""

import asyncio
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from cli.client.projects import ProjectsAPIClient
from cli.models.common import Priority, Status
from cli.models.task import TaskCreate
from cli.services.task_service import TaskService

from ..helpers import (
    console,
    format_priority,
    get_workspace_or_exit,
    output_json,
)


def add_task(
    title: Annotated[str, typer.Argument(help="Task title")],
    description: Annotated[
        Optional[str],
        typer.Option("-d", "--description", help="Task description"),
    ] = None,
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Phase/milestone identifier (e.g., T3, Phase 1)"),
    ] = None,
    priority: Annotated[
        int,
        typer.Option("-p", "--priority", help="Priority (-2 to 2, default: 0)"),
    ] = 0,
    labels: Annotated[
        Optional[str],
        typer.Option("--labels", help="Comma-separated labels"),
    ] = None,
    status: Annotated[
        str,
        typer.Option("--status", help="Task status (default: backlog)"),
    ] = "backlog",
    owner: Annotated[
        Optional[str],
        typer.Option("--owner", help="Assign to user or agent ID"),
    ] = None,
    estimate: Annotated[
        Optional[int],
        typer.Option("--estimate", help="Time estimate in hours"),
    ] = None,
    project: Annotated[
        Optional[int],
        typer.Option(
            "--project",
            help="Project ID (uses current/default project if not specified)",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Create a new task."""
    ws_config = get_workspace_or_exit()
    service = TaskService.from_config()
    projects_client = ProjectsAPIClient.from_config()

    async def create() -> None:
        try:
            # Validate priority range
            if priority < -2 or priority > 2:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "Invalid priority value",
                            "details": "Priority must be between -2 and 2\n  -2: Lowest\n  -1: Low\n   0: Normal (default)\n   1: High\n   2: Highest",
                        },
                        success=False,
                    )
                else:
                    console.print("[red] Error:[/red] Invalid priority value")
                    console.print()
                    console.print("  Priority must be between -2 and 2")
                    console.print("    -2: Lowest")
                    console.print("    -1: Low")
                    console.print("     0: Normal (default)")
                    console.print("     1: High")
                    console.print("     2: Highest")
                raise typer.Exit(1)

            # If project not specified, use the current project from workspace config or API
            project_id = project
            if not project_id:
                # Priority 1: Check workspace config for current_project_id
                if ws_config.current_project_id:
                    project_id = ws_config.current_project_id
                    if not json_output:
                        console.print(
                            f"[dim]Using project from workspace config (ID: {project_id})[/dim]"
                        )
                else:
                    # Priority 2: Fetch from API as fallback
                    try:
                        current_project = await projects_client.get_current_project(
                            int(ws_config.workspace_id)
                        )
                        project_id = current_project.id

                        if not json_output:
                            console.print(
                                f"[dim]Using project: {current_project.name} (ID: {project_id})[/dim]"
                            )
                    except Exception as e:
                        if json_output:
                            output_json(
                                {
                                    "error": "ProjectError",
                                    "message": f"Failed to get current project: {str(e)}",
                                    "hint": "Specify --project ID explicitly or set current_project_id in .anyt/anyt.json",
                                },
                                success=False,
                            )
                        else:
                            console.print(
                                f"[red]Error:[/red] Failed to get current project: {e}"
                            )
                            console.print(
                                "Options:\n"
                                "  1. Specify project explicitly: --project <ID>\n"
                                "  2. Set current_project_id in .anyt/anyt.json\n"
                                "  3. Run 'anyt project use <project-id>' to set default"
                            )
                        raise typer.Exit(1)

            # Parse labels
            label_list = []
            if labels:
                label_list = [label.strip() for label in labels.split(",")]

            # Ensure project_id is set
            if project_id is None:
                raise ValueError("Project ID is required but not set")

            # Convert priority to enum
            priority_enum = Priority(priority)
            # Convert status to enum
            status_enum = Status(status)

            # Create task using typed model
            task_create = TaskCreate(
                title=title,
                description=description,
                phase=phase,
                status=status_enum,
                priority=priority_enum,
                owner_id=owner,
                project_id=project_id,
                labels=label_list,
                estimate=estimate,
            )

            # Create task via service
            task = await service.create_task_with_validation(
                project_id=project_id,
                task=task_create,
            )

            # Display success
            if json_output:
                output_json(task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green][/green] Created: [cyan]{task.identifier}[/cyan] ({task.title})"
                )

        except typer.Exit:
            raise
        except ValueError as e:
            # Handle enum conversion errors
            if json_output:
                output_json(
                    {"error": "ValidationError", "message": str(e)}, success=False
                )
            else:
                console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
        except Exception as e:
            if json_output:
                output_json({"error": "CreateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to create task: {e}")
            raise typer.Exit(1)

    asyncio.run(create())


def create_task_from_template(
    title: Annotated[str, typer.Argument(help="Task title")],
    template: Annotated[
        str,
        typer.Option(
            "--template", "-t", help="Template name to use (default: default)"
        ),
    ] = "default",
    phase: Annotated[
        Optional[str],
        typer.Option("--phase", help="Phase/milestone identifier (e.g., T3, Phase 1)"),
    ] = None,
    priority: Annotated[
        int,
        typer.Option("-p", "--priority", help="Priority (-2 to 2, default: 0)"),
    ] = 0,
    project: Annotated[
        Optional[int],
        typer.Option(
            "--project",
            help="Project ID (uses current/default project if not specified)",
        ),
    ] = None,
    no_edit: Annotated[
        bool,
        typer.Option("--no-edit", help="Skip opening editor, use template as-is"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output in JSON format"),
    ] = False,
) -> None:
    """Create a new task from a template.

    Opens the template in your editor ($EDITOR) for customization before creating the task.
    The template content will be stored in the task's description field.
    """
    # Import template loading function
    try:
        from cli.commands.template import load_template
    except ImportError:
        console.print("[red]Error:[/red] Template module not available")
        raise typer.Exit(1)

    ws_config = get_workspace_or_exit()
    task_service = TaskService.from_config()
    projects_client = ProjectsAPIClient.from_config()

    async def create() -> None:
        try:
            # Validate priority range
            if priority < -2 or priority > 2:
                if json_output:
                    output_json(
                        {
                            "error": "ValidationError",
                            "message": "Invalid priority value",
                            "details": "Priority must be between -2 and 2",
                        },
                        success=False,
                    )
                else:
                    console.print("[red] Error:[/red] Invalid priority value")
                    console.print("  Priority must be between -2 and 2")
                raise typer.Exit(1)

            # Load template
            try:
                template_content = load_template(template)
            except Exception as e:
                if json_output:
                    output_json(
                        {
                            "error": "TemplateError",
                            "message": f"Failed to load template: {e}",
                        },
                        success=False,
                    )
                else:
                    console.print(f"[red]Error:[/red] Failed to load template: {e}")
                    console.print(
                        "Run [cyan]anyt template init[/cyan] to create templates"
                    )
                raise typer.Exit(1)

            # If no-edit is set, use template as-is
            description = template_content
            if not no_edit:
                # Open editor with template
                editor = os.environ.get("EDITOR", "nano")

                # Create temp file with template content
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False
                ) as tmp:
                    tmp.write(template_content)
                    tmp_path = tmp.name

                try:
                    # Open editor
                    result = subprocess.run([editor, tmp_path])

                    if result.returncode != 0:
                        if not json_output:
                            console.print(
                                "[yellow]Editor exited with error, using template as-is[/yellow]"
                            )

                    # Read edited content
                    with open(tmp_path, "r") as f:
                        description = f.read()

                finally:
                    # Clean up temp file
                    Path(tmp_path).unlink(missing_ok=True)

            # Get project ID
            project_id = project
            if not project_id:
                try:
                    current_project = await projects_client.get_current_project(
                        int(ws_config.workspace_id)
                    )
                    project_id = current_project.id

                    if not json_output:
                        console.print(
                            f"[dim]Using project: {current_project.name} (ID: {project_id})[/dim]"
                        )
                except Exception as e:
                    if json_output:
                        output_json(
                            {
                                "error": "ProjectError",
                                "message": f"Failed to get current project: {str(e)}",
                                "hint": "Specify --project ID explicitly",
                            },
                            success=False,
                        )
                    else:
                        console.print(
                            f"[red]Error:[/red] Failed to get current project: {e}"
                        )
                        console.print(
                            "Specify the project ID explicitly with --project <ID>"
                        )
                    raise typer.Exit(1)

            # Ensure project_id is set
            if project_id is None:
                raise ValueError("Project ID is required but not set")

            # Create task
            task_create = TaskCreate(
                title=title,
                description=description,
                phase=phase,
                status=Status.BACKLOG,
                priority=Priority(priority),
                project_id=project_id,
            )
            task = await task_service.create_task_with_validation(
                project_id=project_id, task=task_create
            )

            # Display success
            if json_output:
                output_json(task.model_dump(mode="json"))
            else:
                console.print(
                    f"[green][/green] Created: [cyan]{task.identifier}[/cyan] ({task.title})"
                )

                if phase:
                    console.print(f"  Phase: {phase}")

                console.print(f"  Priority: {format_priority(priority)}")
                console.print(f"  Template: {template}")

        except typer.Exit:
            raise
        except Exception as e:
            if json_output:
                output_json({"error": "CreateError", "message": str(e)}, success=False)
            else:
                console.print(f"[red]Error:[/red] Failed to create task: {e}")
            raise typer.Exit(1)

    asyncio.run(create())
