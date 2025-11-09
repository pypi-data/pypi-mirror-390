"""Tag management commands for WNote."""

import click
from rich.console import Console
from rich.table import Table
from rich import box

from ..core import get_all_tags, get_config, save_config
from ..utils import get_tag_color

console = Console()


@click.command()
def tags():
    """List all available tags
    
    Display all tags in the database with their assigned colors.
    """
    config = get_config()
    all_tags = get_all_tags()
    
    if not all_tags:
        console.print("[bold yellow]No tags found[/bold yellow]")
        return
    
    table = Table(box=box.ROUNDED)
    table.add_column("Tag", style="white")
    table.add_column("Color", style="white")
    
    for tag in all_tags:
        color = get_tag_color(tag, config)
        table.add_row(f"[{color}]{tag}[/{color}]", color)
    
    console.print(table)


@click.command()
@click.argument('tag', required=True)
@click.argument('color_name', required=True)
def color(tag, color_name):
    """Set color for a tag
    
    Available colors:
      - Standard: red, green, blue, yellow, magenta, cyan, white, black
      - Bright: bright_red, bright_green, bright_blue, bright_yellow, bright_magenta, bright_cyan, bright_white
    
    Example:
      wnote color work blue
      wnote color personal green
    """
    valid_colors = [
        "red", "green", "blue", "yellow", "magenta", "cyan", 
        "white", "black", "bright_red", "bright_green", 
        "bright_blue", "bright_yellow", "bright_magenta", 
        "bright_cyan", "bright_white", "bright_black"
    ]
    
    if color_name not in valid_colors:
        console.print(f"[bold red]Invalid color. Choose from: {', '.join(valid_colors)}[/bold red]")
        return
    
    config = get_config()
    config['tag_colors'][tag] = color_name
    save_config(config)
    console.print(f"[bold green]Color for tag '{tag}' set to [{color_name}]{color_name}[/{color_name}][/bold green]")

