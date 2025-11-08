"""
Artifact management commands.

Commands for downloading and viewing workflow execution artifacts.
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from cli.services.context import ServiceContext
from sdk.generated.services.async_Artifacts_service import (
    get_artifact_v1_workspaces__workspace_id__artifacts__artifact_id__get,
)

app = typer.Typer(help="Manage workflow execution artifacts")
console = Console()


@app.command("download")
def download(
    artifact_id: int = typer.Argument(..., help="Artifact ID"),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    stdout: bool = typer.Option(
        False, "--stdout", help="Print to stdout instead of file"
    ),
) -> None:
    """Download artifact content."""

    async def _download() -> None:
        try:
            context = ServiceContext.from_config()
            workspace_id = context.get_workspace_id()

            # Get artifact metadata and content
            response = await get_artifact_v1_workspaces__workspace_id__artifacts__artifact_id__get(
                workspace_id=workspace_id, artifact_id=artifact_id
            )
            artifact = response.data

            # Get content from artifact
            content = getattr(artifact, "content", "")

            if stdout:
                # Print to stdout
                console.print(content)
            else:
                # Write to file
                file_path = output or Path(artifact.name)

                # Ensure parent directory exists
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Write content
                file_path.write_text(content)

                console.print(f"[green]Downloaded to:[/green] {file_path.absolute()}")
                console.print(
                    f"[dim]Type: {artifact.type}, Size: {len(content)} bytes[/dim]"
                )

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)

    asyncio.run(_download())
