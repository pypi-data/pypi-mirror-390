"""
CLI command: rohkun uninstall

Uninstall Rohkun CLI and clean up all local data.
"""

import typer
import os
import sys
import subprocess
import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from cli.config import get_config
from cli.auth import clear_auth_token
from cli.auth import AUTH_FILE, RATE_LIMIT_FILE

console = Console()
app = typer.Typer()


def _get_config_directory() -> Path:
    """Get the configuration directory path."""
    config = get_config()
    # Config directory is typically ~/.rohkun or similar
    # Check where AUTH_FILE is located
    if AUTH_FILE.exists():
        return AUTH_FILE.parent
    # Fallback to default
    if os.name == 'nt':  # Windows
        return Path(os.environ.get('APPDATA', Path.home())) / '.rohkun'
    else:  # Unix-like
        return Path.home() / '.rohkun'


def _get_package_name() -> str:
    """Get the installed package name."""
    return "rohkun"


@app.command()
def uninstall(
    keep_config: bool = typer.Option(False, "--keep-config", help="Keep configuration files and auth tokens"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompts")
):
    """
    Uninstall Rohkun CLI and clean up all local data.
    
    This will:
    - Uninstall the rohkun package (pip uninstall)
    - Remove configuration files
    - Remove authentication tokens
    - Remove cached data
    
    Use --keep-config to preserve your authentication and settings.
    """
    console.print(Panel(
        "[bold]Rohkun CLI Uninstaller[/bold]\n\n"
        "This will remove:\n"
        "  • The rohkun package from your Python environment\n"
        "  • Configuration files\n"
        "  • Authentication tokens\n"
        "  • Cached data\n\n"
        "[yellow]Note: This will NOT delete any project tracking data (.rohkun/ directories in your projects).[/yellow]",
        title="Uninstall Rohkun",
        border_style="yellow"
    ))
    
    # Confirmation
    if not force:
        confirmed = Confirm.ask(
            "\n[bold red]Are you sure you want to uninstall Rohkun?[/bold red]",
            default=False
        )
        if not confirmed:
            console.print("[yellow]Uninstall cancelled.[/yellow]")
            raise typer.Exit(0)
    
    # Check if package is installed
    package_name = _get_package_name()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        is_installed = result.returncode == 0
    except Exception:
        is_installed = False
    
    if not is_installed:
        console.print(f"[yellow]Package '{package_name}' is not installed via pip.[/yellow]")
        console.print("[dim]Skipping package uninstallation...[/dim]")
    else:
        # Uninstall package
        console.print(f"[cyan]Uninstalling {package_name} package...[/cyan]")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", package_name, "-y"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                console.print(f"[green]✓ Package '{package_name}' uninstalled successfully[/green]")
            else:
                console.print(f"[yellow]Warning: Package uninstallation may have failed[/yellow]")
                console.print(f"[dim]{result.stderr}[/dim]")
        except subprocess.TimeoutExpired:
            console.print("[yellow]Warning: Uninstall timed out[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not uninstall package: {e}[/yellow]")
    
    # Clean up configuration files
    if not keep_config:
        console.print("[cyan]Cleaning up configuration files...[/cyan]")
        
        # Remove auth token
        try:
            if AUTH_FILE.exists():
                clear_auth_token()
                console.print("[green]✓ Authentication token removed[/green]")
        except Exception as e:
            console.print(f"[yellow]Warning: Could not remove auth token: {e}[/yellow]")
        
        # Remove config directory
        config_dir = _get_config_directory()
        if config_dir.exists() and config_dir.is_dir():
            try:
                # Remove all files in config directory
                for item in config_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                
                # Try to remove the directory itself (if empty)
                try:
                    config_dir.rmdir()
                    console.print(f"[green]✓ Configuration directory removed[/green]")
                except OSError:
                    # Directory not empty or permission issue
                    console.print(f"[dim]Configuration directory may contain other files[/dim]")
            except Exception as e:
                console.print(f"[yellow]Warning: Could not remove config directory: {e}[/yellow]")
        
        # Remove rate limit file if it exists
        if RATE_LIMIT_FILE.exists():
            try:
                RATE_LIMIT_FILE.unlink()
                console.print("[green]✓ Rate limit data removed[/green]")
            except Exception as e:
                console.print(f"[dim]Could not remove rate limit file: {e}[/dim]")
    else:
        console.print("[yellow]Keeping configuration files (--keep-config flag)[/yellow]")
    
    # Final message
    console.print(Panel(
        "[green]✓ Uninstall complete![/green]\n\n"
        "Rohkun CLI has been removed from your system.\n\n"
        "[dim]Note: Project tracking data (.rohkun/ directories) in your projects has NOT been removed.[/dim]\n"
        "[dim]If you want to remove tracking from specific projects, use 'rohkun delete' in those directories.[/dim]",
        title="Uninstall Complete",
        border_style="green"
    ))


if __name__ == "__main__":
    app()

