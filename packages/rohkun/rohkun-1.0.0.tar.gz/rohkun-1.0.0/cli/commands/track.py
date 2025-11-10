"""
CLI command: rohkun track

Start or resume project tracking in a directory.
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
def track(
    directory: str = typer.Argument(None, help="Directory to track (default: current directory)")
):
    """
    Start or resume Rohkun project tracking in a directory.
    
    - If not tracked: Initializes tracking and creates .rohkun/ directory
    - If paused: Resumes tracking (removes pause flag)
    - If already active: Shows current status
    
    Creates .rohkun/ directory structure and project.json file.
    This enables automatic snapshot creation on each scan.
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
        
        # Check if already initialized
        if file_manager.project_exists():
            project = tracker.load_project()
            if not project:
                console.print(f"[red]Error: Could not load project data[/red]")
                raise typer.Exit(1)
            
            # Check if paused
            is_paused = project.metadata.get("paused", False)
            
            if is_paused:
                # Resume tracking
                project.metadata["paused"] = False
                file_manager.save_project_json(project.to_dict())
                
                console.print(Panel(
                    f"[green]✓ Project tracking resumed![/green]\n\n"
                    f"Project: [bold]{project.project_name}[/bold]\n"
                    f"Hash: [bold]{project.project_hash}[/bold]\n"
                    f"Snapshots: {project.total_snapshots}\n\n"
                    f"Tracking is now active. Snapshots will be created on each scan.",
                    title="Tracking Resumed",
                    border_style="green"
                ))
            else:
                # Already active
                console.print(Panel(
                    f"[green]Project tracking is active[/green]\n\n"
                    f"Project: [bold]{project.project_name}[/bold]\n"
                    f"Hash: [bold]{project.project_hash}[/bold]\n"
                    f"Snapshots: {project.total_snapshots}\n"
                    f"Tracking Days: {project.tracking_days}\n\n"
                    f"Use [bold]rohkun pause[/bold] to pause tracking.",
                    title="Tracking Status",
                    border_style="green"
                ))
        else:
            # Initialize new project
            console.print(f"[cyan]Initializing Rohkun project tracking in {directory}...[/cyan]")
            
            project = tracker.initialize_project()
            
            console.print(Panel(
                f"[green]✓ Project tracking enabled![/green]\n\n"
                f"Project: [bold]{project.project_name}[/bold]\n"
                f"Hash: [bold]{project.project_hash}[/bold]\n\n"
                f"Created:\n"
                f"  • .rohkun/project.json\n"
                f"  • .rohkun/README.md\n"
                f"  • .rohkun/snapshots/\n"
                f"  • .rohkun/reports/\n\n"
                f"Run [bold]rohkun run[/bold] to create your first snapshot.",
                title="Tracking Enabled",
                border_style="green"
            ))
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

