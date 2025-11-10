"""
CLI command: rohkun pause

Pause project tracking in a directory.
"""

import typer
from pathlib import Path
import os
from rich.console import Console
from rich.panel import Panel

from server.processor.tracking import ProjectTracker
from server.processor.tracking.file_manager import RohkunFileManager

console = Console()
app = typer.Typer()


@app.command()
def pause(
    directory: str = typer.Argument(None, help="Directory to pause (default: current directory)")
):
    """
    Pause Rohkun project tracking in a directory.
    
    This stops automatic snapshot creation but keeps all existing tracking data.
    Use 'rohkun track' to resume tracking.
    """
    # Get directory path
    if not directory:
        directory = os.getcwd()
    
    dir_path = Path(directory).resolve()
    
    if not dir_path.exists() or not dir_path.is_dir():
        console.print(f"[red]Error: Invalid directory: {directory}[/red]")
        raise typer.Exit(1)
    
    try:
        tracker = ProjectTracker(str(dir_path))
        file_manager = RohkunFileManager(str(dir_path))
        
        # Check if project exists
        if not file_manager.project_exists():
            console.print(f"[yellow]No tracked project found in {directory}[/yellow]")
            console.print(f"[dim]Run 'rohkun track' to start tracking first.[/dim]")
            raise typer.Exit(1)
        
        project = tracker.load_project()
        if not project:
            console.print(f"[red]Error: Could not load project data[/red]")
            raise typer.Exit(1)
        
        # Check if already paused
        is_paused = project.metadata.get("paused", False)
        if is_paused:
            console.print(Panel(
                f"[yellow]Project tracking is already paused[/yellow]\n\n"
                f"Project: [bold]{project.project_name}[/bold]\n"
                f"Hash: [bold]{project.project_hash}[/bold]\n"
                f"Snapshots: {project.total_snapshots}\n\n"
                f"Use [bold]rohkun track[/bold] to resume tracking.",
                title="Already Paused",
                border_style="yellow"
            ))
            raise typer.Exit(0)
        
        # Pause tracking
        project.metadata["paused"] = True
        file_manager.save_project_json(project.to_dict())
        
        console.print(Panel(
            f"[yellow]✓ Project tracking paused[/yellow]\n\n"
            f"Project: [bold]{project.project_name}[/bold]\n"
            f"Hash: [bold]{project.project_hash}[/bold]\n"
            f"Snapshots: {project.total_snapshots}\n\n"
            f"No new snapshots will be created until you run [bold]rohkun track[/bold] to resume.",
            title="Tracking Paused",
            border_style="yellow"
        ))
        
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

