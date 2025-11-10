"""
CLI command: rohkun compare

Compare two snapshots to see what changed.
"""

import typer
from pathlib import Path
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from server.processor.tracking import ProjectTracker

console = Console()
app = typer.Typer()


@app.command()
def compare(
    snapshot1: str = typer.Argument(..., help="First snapshot ID or sequence number"),
    snapshot2: str = typer.Argument(..., help="Second snapshot ID or sequence number"),
    directory: str = typer.Argument(None, help="Directory to check (default: current directory)")
):
    """
    Compare two snapshots to see structural changes.
    
    Shows added, removed, and modified endpoints/API calls between snapshots.
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
    
    # Resolve snapshot IDs (handle sequence numbers)
    def find_snapshot(identifier: str):
        # Try as sequence number
        try:
            seq = int(identifier)
            for s in snapshots:
                if s.get("sequence") == seq:
                    return s.get("id")
        except ValueError:
            pass
        
        # Try as snapshot ID
        for s in snapshots:
            if s.get("id") == identifier or s.get("id").endswith(identifier):
                return s.get("id")
        
        return identifier
    
    snapshot1_id = find_snapshot(snapshot1)
    snapshot2_id = find_snapshot(snapshot2)
    
    # Load snapshots
    snapshot1_obj = tracker.snapshot_manager.load_snapshot(snapshot1_id)
    snapshot2_obj = tracker.snapshot_manager.load_snapshot(snapshot2_id)
    
    if not snapshot1_obj:
        console.print(f"[red]Error: Snapshot '{snapshot1}' not found[/red]")
        raise typer.Exit(1)
    
    if not snapshot2_obj:
        console.print(f"[red]Error: Snapshot '{snapshot2}' not found[/red]")
        raise typer.Exit(1)
    
    # Compute diff
    diff = tracker.compute_diff(snapshot1_obj, snapshot2_obj)
    
    # Display comparison
    console.print(Panel(
        f"[bold]Comparing Snapshots[/bold]\n\n"
        f"From: [cyan]{snapshot1_obj.id}[/cyan] (Sequence {snapshot1_obj.sequence})\n"
        f"To:   [cyan]{snapshot2_obj.id}[/cyan] (Sequence {snapshot2_obj.sequence})\n\n"
        f"Time Elapsed: {diff.time_elapsed}",
        title="Snapshot Comparison",
        border_style="cyan"
    ))
    
    # Backend changes
    backend_changes = diff.backend_changes
    console.print("\n[bold]Backend Changes:[/bold]")
    
    if backend_changes.get("added_count", 0) > 0:
        console.print(f"  [green]+ {backend_changes.get('added_count')} endpoint(s) added[/green]")
        for added in backend_changes.get("added", [])[:5]:
            method = added.get("method", "GET")
            path = added.get("path", "")
            console.print(f"    [green]+ {method} {path}[/green]")
    
    if backend_changes.get("removed_count", 0) > 0:
        console.print(f"  [red]- {backend_changes.get('removed_count')} endpoint(s) removed[/red]")
        for removed in backend_changes.get("removed", [])[:5]:
            method = removed.get("method", "GET")
            path = removed.get("path", "")
            console.print(f"    [red]- {method} {path}[/red]")
    
    if backend_changes.get("modified_count", 0) > 0:
        console.print(f"  [yellow]~ {backend_changes.get('modified_count')} endpoint(s) modified[/yellow]")
    
    # Frontend changes
    frontend_changes = diff.frontend_changes
    console.print("\n[bold]Frontend Changes:[/bold]")
    
    if frontend_changes.get("added_count", 0) > 0:
        console.print(f"  [green]+ {frontend_changes.get('added_count')} API call(s) added[/green]")
        for added in frontend_changes.get("added", [])[:5]:
            method = added.get("method", "GET")
            url = added.get("url", "")
            console.print(f"    [green]+ {method} {url}[/green]")
    
    if frontend_changes.get("removed_count", 0) > 0:
        console.print(f"  [red]- {frontend_changes.get('removed_count')} API call(s) removed[/red]")
        for removed in frontend_changes.get("removed", [])[:5]:
            method = removed.get("method", "GET")
            url = removed.get("url", "")
            console.print(f"    [red]- {method} {url}[/red]")
    
    if frontend_changes.get("modified_count", 0) > 0:
        console.print(f"  [yellow]~ {frontend_changes.get('modified_count')} API call(s) modified[/yellow]")
    
    # File changes
    file_changes = diff.file_changes
    console.print("\n[bold]File Changes:[/bold]")
    console.print(f"  [green]+ {file_changes.get('new_files', 0)} new file(s)[/green]")
    console.print(f"  [red]- {file_changes.get('deleted_files', 0)} deleted file(s)[/red]")
    console.print(f"  [yellow]~ {file_changes.get('modified_files', 0)} modified file(s)[/yellow]")
    console.print(f"  LOC Change: {file_changes.get('loc_change', 0):+d}")
    
    # Drift analysis
    drift_score = diff.drift_score
    from server.processor.tracking.drift_calculator import DriftCalculator
    drift_calc = DriftCalculator()
    status = drift_calc._get_drift_status(drift_score)
    emoji = drift_calc.get_drift_status_emoji(status)
    
    console.print(f"\n[bold]Drift Analysis:[/bold]")
    console.print(f"  Score: {emoji} {drift_score:.2f} ({status.title()})")
    
    interpretation = drift_calc._get_interpretation(drift_score, status)
    console.print(f"  {interpretation}")


if __name__ == "__main__":
    app()

