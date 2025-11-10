"""
CLI command: rohkun help

Open the help documentation page in the browser.
"""

import typer
import webbrowser
from rich.console import Console
from rich.panel import Panel

from cli.config import get_config

console = Console()
app = typer.Typer()


@app.command()
def help():
    """
    Open Rohkun help documentation in your browser.
    
    This will open the help page that contains:
    - Installation instructions
    - All available commands
    - Usage examples
    - Troubleshooting guide
    """
    try:
        config = get_config()
        
        # Get webapp URL from API URL
        api_url = config.api_url.rstrip('/')
        if api_url.endswith('/api'):
            # Remove /api suffix
            webapp_url = api_url[:-4]
        elif 'api.' in api_url:
            # If API is at api.rohkun.com, frontend is likely at rohkun.com
            webapp_url = api_url.replace('api.', '')
        else:
            # Same domain (e.g., localhost:8000 or rohkun.com)
            webapp_url = api_url
        
        help_url = f"{webapp_url}/help.html"
        
        console.print(Panel(
            f"[cyan]Opening help documentation...[/cyan]\n\n"
            f"URL: [bold]{help_url}[/bold]\n\n"
            f"If the page doesn't open automatically, copy the URL above and paste it in your browser.",
            title="Help",
            border_style="cyan"
        ))
        
        # Open in browser
        webbrowser.open(help_url)
        
    except Exception as e:
        console.print(f"[red]Error opening help page: {e}[/red]")
        console.print(f"[yellow]You can manually visit: {get_config().api_url}/help.html[/yellow]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

