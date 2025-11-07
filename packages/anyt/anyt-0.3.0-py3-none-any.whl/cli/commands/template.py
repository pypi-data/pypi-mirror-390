"""Template management commands for AnyTask CLI."""

import os
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

console = Console()
app = typer.Typer(help="Manage task templates")

# Default template directory
TEMPLATE_DIR = Path.home() / ".config" / "anyt" / "templates"

# Default template content
DEFAULT_TEMPLATE = """## Objectives
-

## Acceptance Criteria
- [ ]
- [ ]

## Technical Notes


## Dependencies


## Estimated Effort
 hours

## Events
### {datetime} - Task created
- Task created from template
"""


def get_template_path(name: str) -> Path:
    """Get the full path for a template file.

    Args:
        name: Template name (without .md extension)

    Returns:
        Path to the template file
    """
    if not name.endswith(".md"):
        name = f"{name}.md"
    return TEMPLATE_DIR / name


@app.command("init")
def init_templates() -> None:
    """Initialize template directory with default template.

    Creates the template directory at ~/.config/anyt/templates/
    and creates a default.md template if it doesn't exist.
    """
    try:
        # Create directory if it doesn't exist
        TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓[/green] Template directory created: {TEMPLATE_DIR}")

        # Create default template if it doesn't exist
        default_path = get_template_path("default")
        if not default_path.exists():
            default_path.write_text(DEFAULT_TEMPLATE)
            console.print(f"[green]✓[/green] Default template created: {default_path}")
        else:
            console.print(
                f"[yellow]![/yellow] Default template already exists: {default_path}"
            )

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to initialize templates: {e}")
        raise typer.Exit(1)


@app.command("list")
def list_templates() -> None:
    """List available templates.

    Shows all .md files in the template directory.
    """
    if not TEMPLATE_DIR.exists():
        console.print("[yellow]No templates found.[/yellow]")
        console.print(
            "Run [cyan]anyt template init[/cyan] to create the template directory"
        )
        raise typer.Exit(1)

    # Find all .md files
    templates = sorted(TEMPLATE_DIR.glob("*.md"))

    if not templates:
        console.print("[yellow]No templates found.[/yellow]")
        console.print(f"Template directory: {TEMPLATE_DIR}")
        return

    # Create table
    table = Table(title="Available Templates", show_header=True)
    table.add_column("Name", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", style="dim")

    for template in templates:
        name = template.stem
        size_kb = template.stat().st_size / 1024
        modified = datetime.fromtimestamp(template.stat().st_mtime).strftime(
            "%Y-%m-%d %H:%M"
        )
        table.add_row(name, f"{size_kb:.1f} KB", modified)

    console.print(table)
    console.print(f"\nTemplate directory: {TEMPLATE_DIR}")


@app.command("show")
def show_template(
    name: str = typer.Argument("default", help="Template name to display"),
) -> None:
    """Display template content.

    Args:
        name: Name of the template to display (default: "default")
    """
    template_path = get_template_path(name)

    if not template_path.exists():
        console.print(f"[red]Error:[/red] Template not found: {name}")
        console.print("Run [cyan]anyt template list[/cyan] to see available templates")
        raise typer.Exit(1)

    try:
        content = template_path.read_text()
        console.print(f"\n[bold]Template:[/bold] {name}")
        console.print(f"[dim]Path: {template_path}[/dim]\n")

        # Render markdown
        md = Markdown(content)
        console.print(md)

    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to read template: {e}")
        raise typer.Exit(1)


@app.command("edit")
def edit_template(
    name: str = typer.Argument("default", help="Template name to edit"),
) -> None:
    """Open template in editor.

    Opens the template file in the system's default editor
    (respects $EDITOR environment variable).

    Args:
        name: Name of the template to edit (default: "default")
    """
    template_path = get_template_path(name)

    if not template_path.exists():
        console.print(f"[red]Error:[/red] Template not found: {name}")
        console.print(
            "Run [cyan]anyt template init[/cyan] to create the default template"
        )
        raise typer.Exit(1)

    # Get editor from environment
    editor = os.environ.get("EDITOR", "nano")

    try:
        import subprocess

        subprocess.run([editor, str(template_path)], check=True)
        console.print(f"[green]✓[/green] Template edited: {name}")
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to open editor: {e}")
        raise typer.Exit(1)


def load_template(name: str = "default") -> str:
    """Load a template and return its content with placeholders replaced.

    Args:
        name: Template name to load

    Returns:
        Template content with placeholders replaced
    """
    template_path = get_template_path(name)

    if not template_path.exists():
        # Return default template if file doesn't exist
        content = DEFAULT_TEMPLATE
    else:
        content = template_path.read_text()

    # Replace placeholders
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    content = content.replace("{datetime}", now)

    return content
