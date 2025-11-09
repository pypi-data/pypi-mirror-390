"""Configuration commands for WNote."""

import json
import click
from rich.console import Console
from rich.panel import Panel
from rich import box

from ..core import get_config, CONFIG_PATH

console = Console()


@click.command()
@click.option('--reset', is_flag=True, help='Reset configuration to defaults')
def config(reset):
    """View or reset configuration
    
    Display the current configuration settings or reset to defaults.
    The configuration file is stored at ~/.config/wnote/config.json
    
    Examples:
      View configuration:
        wnote config
        
      Reset to defaults:
        wnote config --reset
    """
    if reset:
        from ..core.config import reset_config
        if click.confirm("Are you sure you want to reset configuration to defaults?"):
            if reset_config():
                console.print("[bold green]Configuration reset to defaults[/bold green]")
            else:
                console.print("[bold red]Failed to reset configuration[/bold red]")
        else:
            console.print("[yellow]Reset cancelled[/yellow]")
        return
    
    # Display current config
    app_config = get_config()
    
    # Create a serializable copy
    serializable_config = {}
    for key, value in app_config.items():
        if key == 'tag_colors':
            serializable_config[key] = dict(value)
        elif isinstance(value, (str, int, float, bool, list, dict)) or value is None:
            serializable_config[key] = value
    
    console.print(Panel(json.dumps(serializable_config, indent=2), title="Current Configuration", box=box.ROUNDED))
    console.print("\n[bold]Configuration Tips:[/bold]")
    console.print("  • Set tag colors: [cyan]wnote color <tag> <color>[/cyan]")
    console.print("  • Edit config file directly: [cyan]~/.config/wnote/config.json[/cyan]")
    console.print(f"  • Config location: [yellow]{CONFIG_PATH}[/yellow]")
    console.print("  • Reset to defaults: [cyan]wnote config --reset[/cyan]")

