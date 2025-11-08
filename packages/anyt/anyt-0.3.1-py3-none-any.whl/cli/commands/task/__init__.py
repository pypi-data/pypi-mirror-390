"""Task commands for AnyTask CLI."""

import typer

from .crud.bulk import bulk_update_tasks
from .crud.create import add_task, create_task_from_template
from .crud.delete import remove_task
from .crud.read import share_task, show_task
from .crud.update import add_note_to_task, edit_task, mark_done
from .dependencies import add_dependency, list_dependencies, remove_dependency
from .list import list_tasks
from .pick import pick_task
from .suggest import suggest_tasks

# Main task command app
app = typer.Typer(help="Manage tasks")

# Register CRUD commands
app.command("add")(add_task)
app.command("create")(create_task_from_template)
app.command("list")(list_tasks)
app.command("show")(show_task)
app.command("share")(share_task)
app.command("edit")(edit_task)
app.command("done")(mark_done)
app.command("note")(add_note_to_task)
app.command("rm")(remove_task)
app.command("pick")(pick_task)
app.command("suggest")(suggest_tasks)
app.command("bulk-update")(bulk_update_tasks)

# Dependency management subcommands
dep_app = typer.Typer(help="Manage task dependencies")
dep_app.command("add")(add_dependency)
dep_app.command("rm")(remove_dependency)
dep_app.command("list")(list_dependencies)

# Add dependency subcommand to main app
app.add_typer(dep_app, name="dep")
