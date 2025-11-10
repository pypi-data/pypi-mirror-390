"""
CLI for Rohkun - Ultra-minimal "dumb terminal" client.

Philosophy:
- CLI handles: Auth, Upload, Polling
- Server handles: ALL processing, ALL formatting, ALL display logic
- CLI just prints whatever text the server sends
- Server can change output format anytime without CLI updates

This keeps CLI stable and puts all flexibility on the server side.
"""
import os
import time
import zipfile
import tempfile
import requests
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from cli.auth import login_interactive, logout as auth_logout, check_auth, get_auth_token
from cli.config import get_config
from cli.logging_config import setup_cli_logging, get_logger

# Set up logging
setup_cli_logging()
logger = get_logger(__name__)

console = Console()

# Version info
__version__ = "1.0.0"

def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"Rohkun CLI v{__version__}")
        raise typer.Exit()

app = typer.Typer(
    help="Rohkun - Code analysis tool",
    add_completion=False,
    no_args_is_help=True,
)

@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit"
    )
):
    """Rohkun CLI - Code analysis tool."""
    pass


def _sanitize_path(path_str: str) -> Optional[Path]:
    """Sanitize and validate directory path."""
    if not path_str or not isinstance(path_str, str):
        return None
    
    # Remove any null bytes or control characters
    path_str = path_str.replace('\x00', '').strip()
    if not path_str:
        return None
    
    try:
        path = Path(path_str).resolve()
        
        # Security check: prevent directory traversal
        if '..' in path.parts:
            return None
        
        # Check if path exists and is accessible
        if not path.exists() or not path.is_dir():
            return None
        
        # Check read permissions
        if not os.access(path, os.R_OK):
            return None
        
        return path
    except (OSError, ValueError, RuntimeError):
        return None


def _copy_to_clipboard(text: str, timeout: int = 5) -> tuple[bool, Optional[str]]:
    """Copy text to clipboard with timeout."""
    import threading
    
    result = [False, "Timeout"]
    
    def _copy_thread():
        try:
            import pyperclip
            pyperclip.copy(text)
            result[0] = True
            result[1] = None
        except ImportError:
            result[1] = "pyperclip not installed. Install with: pip install pyperclip"
        except Exception as e:
            result[1] = f"Clipboard error: {type(e).__name__}: {str(e)}"
    
    thread = threading.Thread(target=_copy_thread, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        return False, "Clipboard operation timed out"
    
    return result[0], result[1]


@app.command()
def run(
    directory: str = typer.Argument(None, help="Directory to analyze"),
    no_copy: bool = typer.Option(False, "--no-copy", help="Don't copy link to clipboard"),
    format: str = typer.Option("rich", "--format", help="Output format: rich, plain, json")
):
    """
    Analyze codebase by uploading to server.
    
    Server does ALL processing and formatting. CLI just displays what server sends.
    This means server can change output anytime without updating CLI.
    """
    # Check authentication
    if not check_auth():
        console.print("[red]Error: Not authenticated. Please run 'rohkun login' first.[/red]")
        raise typer.Exit(1)
    
    # Get directory path - default to current directory
    if not directory:
        # Default to current working directory
        import os
        directory = os.getcwd()
        console.print(f"[dim]Using current directory: {directory}[/dim]")
    
    # Sanitize and validate path
    dir_path = _sanitize_path(directory)
    if not dir_path:
        console.print(f"[red]Error: Invalid or inaccessible directory: '{directory}'[/red]")
        console.print("[yellow]Please provide a valid, accessible directory path.[/yellow]")
        raise typer.Exit(1)
    
    console.print(f"[cyan]Preparing to upload {dir_path.name}...[/cyan]")
    
    temp_dir = None
    try:
        # Create ZIP file
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Creating ZIP archive...", total=None)
            
            # Create temp ZIP file
            temp_dir = tempfile.mkdtemp()
            zip_path = Path(temp_dir) / f"{dir_path.name}.zip"
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in dir_path.rglob('*'):
                    if file_path.is_file():
                        # Skip common directories to ignore
                        skip_dirs = {'node_modules', '.git', '__pycache__', 'venv', '.venv', 'dist', 'build', '.next', 'target'}
                        if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                            continue
                        
                        arcname = file_path.relative_to(dir_path)
                        zipf.write(file_path, arcname)
            
            zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
            console.print(f"[dim]ZIP created: {zip_size_mb:.2f} MB[/dim]")
            
            # Upload to server
            progress.update(task, description="Uploading to server...")
            
            config = get_config()
            token = get_auth_token()
            
            with open(zip_path, 'rb') as f:
                files = {'file': (zip_path.name, f, 'application/zip')}
                headers = {'Authorization': f'Bearer {token}'}
                
                response = requests.post(
                    f"{config.api_url}/upload",
                    files=files,
                    headers=headers,
                    timeout=300  # 5 minute timeout for upload
                )
            
            if response.status_code != 200:
                error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
                console.print(f"[red]Upload failed: {error_detail}[/red]")
                raise typer.Exit(1)
            
            upload_result = response.json()
            project_id = upload_result.get('project_id')
            webapp_url = upload_result.get('webapp_url')
            
            console.print(f"[green]✓ Upload successful![/green]")
            console.print(f"[dim]Project ID: {project_id}[/dim]")
            
            # Poll for completion
            progress.update(task, description="Processing on server...")
            
            max_wait = 300  # 5 minutes max
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Check project status
                status_response = requests.get(
                    f"{config.api_url}/projects/{project_id}",
                    headers=headers,
                    timeout=30
                )
                
                if status_response.status_code == 200:
                    project_data = status_response.json()
                    status = project_data.get('status')
                    
                    if status == 'completed':
                        # Get PRE-FORMATTED output from server
                        # Server sends plain text - we just print it!
                        report_response = requests.get(
                            f"{config.api_url}/reports/{project_id}/cli-output",
                            headers=headers,
                            params={'format': format},
                            timeout=30
                        )
                        
                        if report_response.status_code == 200:
                            progress.update(task, completed=True)
                            
                            # Server sends TEXT - we just display it!
                            # No parsing, no logic, no formatting - just print
                            output_text = report_response.text
                            
                            # Print whatever server sent
                            if format == 'json':
                                print(output_text)  # Raw output
                            else:
                                console.print(output_text)  # Rich markup rendering
                            
                            # Copy report to clipboard (always, unless --no-copy)
                            if not no_copy:
                                try:
                                    import pyperclip
                                    pyperclip.copy(output_text)
                                    console.print("\n[green]✓ Report copied to clipboard![/green]")
                                except ImportError:
                                    console.print("\n[yellow]Note: Install pyperclip to enable clipboard copy (pip install pyperclip)[/yellow]")
                                except Exception as e:
                                    console.print(f"\n[yellow]Could not copy to clipboard: {e}[/yellow]")
                            
                            return
                        
                    elif status == 'failed':
                        error_msg = project_data.get('error_message', 'Unknown error')
                        console.print(f"\n[red]Analysis failed: {error_msg}[/red]")
                        raise typer.Exit(1)
                    
                    # Still processing, wait and retry
                    time.sleep(2)
                else:
                    console.print(f"[yellow]Warning: Could not check status (HTTP {status_response.status_code})[/yellow]")
                    time.sleep(2)
            
            # Timeout
            console.print(f"\n[yellow]Analysis is taking longer than expected.[/yellow]")
            if webapp_url:
                console.print(f"[yellow]Check status at: {webapp_url}[/yellow]")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        raise typer.Exit(130)
    except typer.Exit:
        # Re-raise typer.Exit without logging - these are intentional exits
        raise
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Network error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {type(e).__name__}: {e}[/red]")
        logger.exception("Unexpected error during analysis")
        raise typer.Exit(1)
    finally:
        # Cleanup temp files
        if temp_dir:
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass


@app.command()
def login(
    token: Optional[str] = typer.Option(None, "--token", help="Authentication token"),
    api_url: Optional[str] = typer.Option(None, "--api-url", help="API URL (overrides ROHKUN_API_URL env var)")
):
    """Login to Rohkun."""
    # Use provided API URL, or from config
    if api_url:
        target_api_url = api_url
    else:
        target_api_url = get_config().api_url
    
    if token:
        # Save token directly
        try:
            from cli.auth import save_auth_token
            save_auth_token(token, target_api_url)
            console.print("[green]✓ Token saved successfully[/green]")
        except Exception as e:
            console.print(f"[red]Error saving token: {type(e).__name__}: {e}[/red]")
            raise typer.Exit(1)
    else:
        # Interactive login
        success = login_interactive(target_api_url)
        if not success:
            raise typer.Exit(1)


@app.command()
def logout():
    """Logout from Rohkun."""
    auth_logout()
    console.print("[green]✓ Logged out[/green]")


# Register tracking commands
try:
    from cli.commands.track import track
    from cli.commands.pause import pause
    from cli.commands.delete import delete
    from cli.commands.history import history
    from cli.commands.compare import compare
    
    # Add track command (starts or resumes tracking)
    @app.command("track")
    def track_command(directory: str = typer.Argument(None, help="Directory to track")):
        """Start or resume Rohkun project tracking."""
        track(directory)
    
    # Add pause command
    @app.command("pause")
    def pause_command(directory: str = typer.Argument(None, help="Directory to pause")):
        """Pause Rohkun project tracking (stops snapshot creation)."""
        pause(directory)
    
    # Add delete command
    @app.command("delete")
    def delete_command(
        directory: str = typer.Argument(None, help="Directory to delete"),
        force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
    ):
        """Delete project from database and remove local tracking (requires typing 'confirm')."""
        delete(directory, force)
    
    # Add history command
    @app.command("history")
    def history_command(directory: str = typer.Argument(None, help="Directory to check")):
        """View snapshot history."""
        history(directory)
    
    # Add compare command
    @app.command("compare")
    def compare_command(
        snapshot1: str = typer.Argument(..., help="First snapshot ID or sequence"),
        snapshot2: str = typer.Argument(..., help="Second snapshot ID or sequence"),
        directory: str = typer.Argument(None, help="Directory to check")
    ):
        """Compare two snapshots."""
        compare(snapshot1, snapshot2, directory)
    
    logger.info("Tracking commands (track, pause, delete, history, compare) registered")
except Exception as e:
    logger.warning(f"Could not register tracking commands: {e}")

# Register help command
try:
    from cli.commands.help import help as help_command
    
    @app.command("help")
    def help_cmd():
        """Open Rohkun help documentation in your browser."""
        help_command()
    
    logger.info("Help command registered")
except Exception as e:
    logger.warning(f"Could not register help command: {e}")

# Register uninstall command (separate try/except so it works even if tracking commands fail)
try:
    from cli.commands.uninstall import uninstall
    
    @app.command("uninstall")
    def uninstall_command(
        keep_config: bool = typer.Option(False, "--keep-config", help="Keep configuration files and auth tokens"),
        force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompts")
    ):
        """Uninstall Rohkun CLI and clean up all local data."""
        uninstall(keep_config, force)
    
    logger.info("Uninstall command registered")
except Exception as e:
    logger.warning(f"Could not register uninstall command: {e}")


if __name__ == "__main__":
    app()
