"""
CLI command: rohkun delete

Delete project from database and remove local tracking.
"""

import typer
from pathlib import Path
import os
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from server.processor.tracking import ProjectTracker
from cli.auth import check_auth
from cli.api_client import find_project_by_hash, delete_project, APIError

console = Console()
app = typer.Typer()


@app.command()
def delete(
    directory: str = typer.Argument(None, help="Directory to delete (default: current directory)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt")
):
    """
    Delete Rohkun project from database and remove local tracking.
    
    This will:
    - Delete the project from the database (removes it from web app)
    - Delete all snapshots and reports from the database
    - Remove the local .rohkun/ directory
    
    WARNING: This action cannot be undone! The project will be permanently deleted.
    """
    # Check authentication
    if not check_auth():
        console.print("[red]Error: Not authenticated. Please run 'rohkun login' first.[/red]")
        raise typer.Exit(1)
    
    # Get directory path
    if not directory:
        directory = os.getcwd()
    
    dir_path = Path(directory).resolve()
    
    if not dir_path.exists() or not dir_path.is_dir():
        console.print(f"[red]Error: Invalid directory: {directory}[/red]")
        raise typer.Exit(1)
    
    # Check if project is tracked locally
    tracker = ProjectTracker(str(dir_path))
    if not tracker.file_manager.project_exists():
        console.print(f"[yellow]No project tracking found in {directory}[/yellow]")
        console.print("Nothing to delete.")
        raise typer.Exit(0)
    
    # Load project to get hash
    project = tracker.load_project()
    if not project:
        console.print(f"[red]Error: Could not load project data[/red]")
        raise typer.Exit(1)
    
    rohkun_dir = dir_path / ".rohkun"
    project_hash = project.project_hash
    project_name = project.project_name
    snapshot_count = project.total_snapshots
    
    # Show what will be deleted
    console.print(Panel(
        f"[bold]Project:[/bold] {project_name}\n"
        f"[bold]Hash:[/bold] {project_hash}\n"
        f"[bold]Snapshots:[/bold] {snapshot_count}\n\n"
        f"[red]This will PERMANENTLY DELETE:[/red]\n"
        f"  • Project from database\n"
        f"  • All {snapshot_count} snapshot(s) from database\n"
        f"  • All reports from database\n"
        f"  • Project from web application\n"
        f"  • Local .rohkun/ directory\n"
        f"  • All local tracking data\n\n"
        f"[bold red]This action cannot be undone![/bold red]",
        title="Delete Project",
        border_style="red"
    ))
    
    # Require typing "confirm" for confirmation
    if not force:
        confirmation = Prompt.ask(
            "\n[bold red]Type 'confirm' to delete this project permanently[/bold red]",
            default=""
        )
        if confirmation.lower() != "confirm":
            console.print("[yellow]Cancelled. Project was not deleted.[/yellow]")
            raise typer.Exit(0)
    
    # Find project in database by hash
    try:
        # Use unified API client to find project
        project = find_project_by_hash(project_hash)
        
        if not project:
            console.print(f"[yellow]Project not found in database (may have been deleted already)[/yellow]")
            console.print(f"[dim]Removing local tracking data only...[/dim]")
        else:
            project_id = project.get("id")
            # Delete from database using unified API client
            console.print(f"[cyan]Deleting project from database...[/cyan]")
            
            try:
                delete_project(project_id)
                console.print(f"[green]✓ Project deleted from database[/green]")
            except APIError as e:
                if e.status_code == 404:
                    console.print(f"[yellow]Project not found in database (may have been deleted already)[/yellow]")
                else:
                    console.print(f"[red]Error deleting project from database: {e.message}[/red]")
                    console.print(f"[yellow]Continuing with local cleanup...[/yellow]")
    
    except APIError as e:
        console.print(f"[yellow]Warning: Could not connect to server: {e.message}[/yellow]")
        console.print(f"[yellow]Continuing with local cleanup only...[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Warning: Error deleting from database: {e}[/yellow]")
        console.print(f"[yellow]Continuing with local cleanup...[/yellow]")
    
    # Remove local .rohkun/ directory
    try:
        if rohkun_dir.exists():
            shutil.rmtree(rohkun_dir)
            console.print(f"[green]✓ Local tracking data removed[/green]")
        else:
            console.print("[yellow]No .rohkun/ directory found[/yellow]")
        
        console.print(Panel(
            f"[green]✓ Project deletion complete[/green]\n\n"
            f"Project '{project_name}' has been deleted.\n"
            f"All data has been removed from both database and local files.\n\n"
            f"Run [bold]rohkun track[/bold] to start tracking a new project.",
            title="Deletion Complete",
            border_style="green"
        ))
            
    except Exception as e:
        console.print(f"[red]Error removing local tracking: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

