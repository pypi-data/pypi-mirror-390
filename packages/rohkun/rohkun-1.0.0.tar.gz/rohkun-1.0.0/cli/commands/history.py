"""
CLI command: rohkun history

View snapshot history for a project.
"""

import typer
from pathlib import Path
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from server.processor.tracking import ProjectTracker

console = Console()
app = typer.Typer()


@app.command()
def history(
    directory: str = typer.Argument(None, help="Directory to check (default: current directory)")
):
    """
    View snapshot history for the project.
    
    Shows chronological list of all snapshots with drift scores.
    """
    # Get directory path
    if not directory:
        directory = os.getcwd()
    
    dir_path = Path(directory).resolve()
    
    if not dir_path.exists() or not dir_path.is_dir():
        console.print(f"[red]Error: Invalid directory: {directory}[/red]")
        raise typer.Exit(1)
    
    # Check if project exists
    tracker = ProjectTracker(str(dir_path))
    if not tracker.file_manager.project_exists():
        console.print(f"[yellow]No project tracking found in {directory}[/yellow]")
        console.print("Run [bold]rohkun init[/bold] to initialize tracking.")
        raise typer.Exit(1)
    
    # Load project
    project = tracker.load_project()
    if not project:
        console.print(f"[red]Error: Could not load project[/red]")
        raise typer.Exit(1)
    
    # Get snapshots
    snapshots = tracker.list_snapshots(project)
    
    if not snapshots:
        console.print(f"[yellow]No snapshots found. Run [bold]rohkun scan[/bold] to create one.[/yellow]")
        raise typer.Exit(0)
    
    # Display project info
    console.print(Panel(
        f"[bold]{project.project_name}[/bold]\n"
        f"Hash: {project.project_hash}\n"
        f"Tracking: {project.tracking_days} day{'s' if project.tracking_days != 1 else ''} | "
        f"{project.total_snapshots} snapshot{'s' if project.total_snapshots != 1 else ''}",
        title="Project Tracking",
        border_style="cyan"
    ))
    
    # Create table
    table = Table(title="Snapshot History", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("Snapshot ID", style="cyan")
    table.add_column("Date", style="green")
    table.add_column("Endpoints", justify="right", style="blue")
    table.add_column("API Calls", justify="right", style="blue")
    table.add_column("Files", justify="right", style="blue")
    table.add_column("Drift", justify="right")
    table.add_column("Status", justify="center")
    
    for snapshot in snapshots:
        sequence = snapshot.get("sequence", 0)
        snapshot_id = snapshot.get("id", "")
        timestamp = snapshot.get("timestamp", "")
        endpoints = snapshot.get("endpoints", 0)
        api_calls = snapshot.get("api_calls", 0)
        files = snapshot.get("files", 0)
        drift = snapshot.get("drift", 0.0)
        status = snapshot.get("status", "healthy")
        
        # Format timestamp
        try:
            from datetime import datetime
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            else:
                date_str = str(timestamp)
        except:
            date_str = str(timestamp)
        
        # Format drift with emoji
        if status == "healthy":
            drift_display = f"🟢 {drift:.2f}"
        elif status == "caution":
            drift_display = f"🟡 {drift:.2f}"
        elif status == "high":
            drift_display = f"🔴 {drift:.2f}"
        else:
            drift_display = f"{drift:.2f}"
        
        # Status emoji
        status_emoji = {
            "baseline": "📌",
            "healthy": "🟢",
            "caution": "🟡",
            "high": "🔴"
        }.get(status, "⚪")
        
        table.add_row(
            str(sequence),
            snapshot_id,
            date_str,
            str(endpoints),
            str(api_calls),
            str(files),
            drift_display,
            status_emoji
        )
    
    console.print()
    console.print(table)
    
    # Show summary
    if len(snapshots) > 1:
        avg_drift = sum(s.get("drift", 0.0) for s in snapshots) / len(snapshots)
        max_drift = max((s.get("drift", 0.0) for s in snapshots), default=0.0)
        
        console.print()
        console.print(f"[dim]Average drift: {avg_drift:.2f} | Max drift: {max_drift:.2f}[/dim]")


if __name__ == "__main__":
    app()

