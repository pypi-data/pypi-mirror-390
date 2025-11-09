"""Main CLI interface for WNote."""

import click
from rich.console import Console

from .core import init_db, load_config
from .utils import cleanup_stale_connections
from .commands import (
    add, show, edit, update, delete,
    tags, color,
    attach, deattach,
    reminder, reminders,
    export, search, stats,
    config as config_cmd,
    backup, restore, archive, list_archives
)
from .commands.backup_commands import template

console = Console()


@click.group()
@click.version_option(version="0.6.1", prog_name="WNote")
def cli():
    """WNote - Terminal Note Taking Application
    
    A beautiful and user-friendly CLI note-taking application with rich features
    including tags, attachments, reminders, search, templates, backups, and more.
    
    \b
    Quick Start:
      Create a note:     wnote add "My Note" -t "tag1,tag2"
      List notes:        wnote show
      Search notes:      wnote search "keyword"
      View stats:        wnote stats
      Create backup:     wnote backup
    
    \b
    For detailed help on any command, use:
      wnote <command> --help
    
    \b
    Documentation: https://github.com/imnotnahn/wnote
    Report issues: https://github.com/imnotnahn/wnote/issues
    """
    pass


# Initialize database and clean up on startup
init_db()
cleanup_stale_connections()
load_config()


# Note management commands
cli.add_command(add)
cli.add_command(show)
cli.add_command(edit)
cli.add_command(update)
cli.add_command(delete)

# Tag commands
cli.add_command(tags)
cli.add_command(color)

# Attachment commands
cli.add_command(attach)
cli.add_command(deattach)

# Reminder commands
cli.add_command(reminder)
cli.add_command(reminders)

# Export and search commands
cli.add_command(export)
cli.add_command(search)
cli.add_command(stats)

# Configuration command
cli.add_command(config_cmd, name='config')

# Backup and archive commands
cli.add_command(backup)
cli.add_command(restore)
cli.add_command(archive)
cli.add_command(list_archives, name='list-backups')

# Template commands (as subgroup)
cli.add_command(template)


if __name__ == "__main__":
    cli()

