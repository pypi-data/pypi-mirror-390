"""Backup, restore, archive, and template commands for WNote."""

import os
import shutil
import click
import datetime
import tempfile
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ..core import (
    DB_PATH, BACKUP_DIR, ATTACHMENTS_DIR, CONFIG_PATH, TEMPLATES_DIR,
    get_notes, create_template, get_templates, get_config
)
from ..core.database import get_connection, safe_close_connection
from ..utils import format_datetime

console = Console()


@click.command()
@click.option('--name', '-n', help='Backup name (default: auto-generated timestamp)')
@click.option('--compress', '-c', is_flag=True, help='Compress the backup')
def backup(name, compress):
    """Create a backup of notes database
    
    Creates a backup of the database and attachments directory.
    Backups are stored in ~/.config/wnote/backups/
    
    Examples:
      Create automatic backup:
        wnote backup
        
      Create named backup:
        wnote backup --name "before-cleanup"
        
      Create compressed backup:
        wnote backup --compress
    """
    try:
        # Generate backup name
        if not name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"backup_{timestamp}"
        
        backup_path = os.path.join(BACKUP_DIR, name)
        
        # Check if backup already exists
        if os.path.exists(backup_path):
            console.print(f"[bold red]Backup '{name}' already exists[/bold red]")
            return
        
        # Create backup directory
        os.makedirs(backup_path, exist_ok=True)
        
        # Copy database
        if os.path.exists(DB_PATH):
            shutil.copy2(DB_PATH, os.path.join(backup_path, "notes.db"))
        
        # Copy config
        if os.path.exists(CONFIG_PATH):
            shutil.copy2(CONFIG_PATH, os.path.join(backup_path, "config.json"))
        
        # Copy attachments directory
        if os.path.exists(ATTACHMENTS_DIR):
            attachments_backup = os.path.join(backup_path, "attachments")
            shutil.copytree(ATTACHMENTS_DIR, attachments_backup)
        
        # Create backup metadata
        metadata = {
            "created_at": datetime.datetime.now().isoformat(),
            "name": name,
            "compressed": compress
        }
        
        import json
        with open(os.path.join(backup_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Compress if requested
        if compress:
            console.print(f"[yellow]Compressing backup...[/yellow]")
            archive_name = f"{backup_path}.tar.gz"
            shutil.make_archive(backup_path, 'gztar', BACKUP_DIR, name)
            shutil.rmtree(backup_path)
            console.print(f"[bold green]Backup created and compressed: {archive_name}[/bold green]")
        else:
            console.print(f"[bold green]Backup created: {backup_path}[/bold green]")
        
        # Clean up old backups if auto_backup is enabled
        config = get_config()
        if config.get('auto_backup', True):
            _cleanup_old_backups(config.get('max_backups', 10))
            
    except Exception as e:
        console.print(f"[bold red]Error creating backup: {e}[/bold red]")


@click.command()
@click.argument('backup_name', required=True)
@click.option('--force', '-f', is_flag=True, help='Restore without confirmation')
def restore(backup_name, force):
    """Restore notes from a backup
    
    Restores the database and attachments from a previous backup.
    WARNING: This will replace your current notes!
    
    Examples:
      Restore from backup:
        wnote restore backup_20250315_120000
        
      Force restore without confirmation:
        wnote restore backup_20250315_120000 --force
    """
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    # Check if backup exists (as directory or compressed)
    if not os.path.exists(backup_path) and not os.path.exists(f"{backup_path}.tar.gz"):
        console.print(f"[bold red]Backup '{backup_name}' not found[/bold red]")
        console.print("[yellow]Use 'wnote backup --list' to see available backups[/yellow]")
        return
    
    if not force:
        console.print("[bold yellow]⚠️  WARNING: This will replace your current notes![/bold yellow]")
        console.print("[yellow]Consider creating a backup before restoring[/yellow]")
        if not click.confirm("Do you want to continue?"):
            console.print("[yellow]Restore cancelled[/yellow]")
            return
    
    try:
        # Extract if compressed
        if os.path.exists(f"{backup_path}.tar.gz"):
            console.print("[yellow]Extracting compressed backup...[/yellow]")
            shutil.unpack_archive(f"{backup_path}.tar.gz", BACKUP_DIR)
        
        # Restore database
        db_backup = os.path.join(backup_path, "notes.db")
        if os.path.exists(db_backup):
            shutil.copy2(db_backup, DB_PATH)
        
        # Restore config
        config_backup = os.path.join(backup_path, "config.json")
        if os.path.exists(config_backup):
            shutil.copy2(config_backup, CONFIG_PATH)
        
        # Restore attachments
        attachments_backup = os.path.join(backup_path, "attachments")
        if os.path.exists(attachments_backup):
            if os.path.exists(ATTACHMENTS_DIR):
                shutil.rmtree(ATTACHMENTS_DIR)
            shutil.copytree(attachments_backup, ATTACHMENTS_DIR)
        
        console.print(f"[bold green]Successfully restored from backup: {backup_name}[/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error restoring backup: {e}[/bold red]")


@click.command()
@click.argument('note_id', type=int, required=False)
@click.option('--list', '-l', is_flag=True, help='List archived notes')
@click.option('--restore-note', '-r', type=int, help='Restore an archived note by ID')
def archive(note_id, list, restore_note):
    """Archive or restore notes
    
    Archive notes to hide them from normal view, or restore archived notes.
    Archived notes are not deleted and can be restored at any time.
    
    Examples:
      Archive a note:
        wnote archive 1
        
      List archived notes:
        wnote archive --list
        
      Restore an archived note:
        wnote archive --restore-note 1
    """
    from ..core import update_note
    
    if list:
        # List archived notes
        archived_notes = get_notes(archived_only=True)
        
        if not archived_notes:
            console.print("[bold yellow]No archived notes found[/bold yellow]")
            return
        
        console.print(f"[bold]📦 Archived Notes ({len(archived_notes)}):[/bold]\n")
        
        config = get_config()
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Tags", no_wrap=True)
        table.add_column("Archived", style="yellow")
        
        for note in archived_notes:
            from ..utils import get_tag_color
            
            # Format tags
            formatted_tags = []
            for tag_name in note.get('tags', []):
                color = get_tag_color(tag_name, config)
                formatted_tags.append(f"[{color}]{tag_name}[/{color}]")
            
            tag_display = " ".join(formatted_tags) if formatted_tags else ""
            
            table.add_row(
                str(note['id']),
                note['title'],
                tag_display,
                format_datetime(note['updated_at'])
            )
        
        console.print(table)
        console.print("\n[dim]Use 'wnote archive --restore-note <ID>' to restore a note[/dim]")
        return
    
    if restore_note:
        # Restore archived note
        notes = get_notes(note_id=restore_note, include_archived=True)
        if not notes:
            console.print(f"[bold red]Note with ID {restore_note} not found[/bold red]")
            return
        
        note = notes[0]
        if not note['is_archived']:
            console.print(f"[bold yellow]Note {restore_note} is not archived[/bold yellow]")
            return
        
        update_note(restore_note, is_archived=False)
        console.print(f"[bold green]Note {restore_note} restored from archive[/bold green]")
        return
    
    if note_id:
        # Archive a note
        notes = get_notes(note_id=note_id)
        if not notes:
            console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
            return
        
        update_note(note_id, is_archived=True)
        console.print(f"[bold green]Note {note_id} archived[/bold green]")
        console.print("[dim]Use 'wnote archive --restore-note {note_id}' to restore later[/dim]")
    else:
        console.print("[bold yellow]Please specify a note ID to archive or use --list to view archived notes[/bold yellow]")


@click.command()
@click.option('--delete', '-d', help='Delete a backup by name')
def list_archives(delete):
    """List all available backups
    
    Shows all backups stored in the backups directory.
    
    Examples:
      List all backups:
        wnote list-backups
        
      Delete a backup:
        wnote list-backups --delete backup_20250315_120000
    """
    if delete:
        backup_path = os.path.join(BACKUP_DIR, delete)
        compressed_path = f"{backup_path}.tar.gz"
        
        if os.path.exists(backup_path):
            shutil.rmtree(backup_path)
            console.print(f"[bold green]Backup '{delete}' deleted[/bold green]")
        elif os.path.exists(compressed_path):
            os.remove(compressed_path)
            console.print(f"[bold green]Backup '{delete}.tar.gz' deleted[/bold green]")
        else:
            console.print(f"[bold red]Backup '{delete}' not found[/bold red]")
        return
    
    # List all backups
    backups = []
    
    if os.path.exists(BACKUP_DIR):
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            
            # Check if it's a directory or compressed file
            if os.path.isdir(item_path):
                metadata_file = os.path.join(item_path, "metadata.json")
                if os.path.exists(metadata_file):
                    import json
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    backups.append({
                        'name': item,
                        'created': metadata.get('created_at', 'Unknown'),
                        'compressed': False,
                        'size': _get_dir_size(item_path)
                    })
            elif item.endswith('.tar.gz'):
                backups.append({
                    'name': item.replace('.tar.gz', ''),
                    'created': datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat(),
                    'compressed': True,
                    'size': os.path.getsize(item_path)
                })
    
    if not backups:
        console.print("[bold yellow]No backups found[/bold yellow]")
        console.print("[dim]Create a backup with: wnote backup[/dim]")
        return
    
    # Sort by creation time
    backups.sort(key=lambda x: x['created'], reverse=True)
    
    console.print(f"[bold]💾 Available Backups ({len(backups)}):[/bold]\n")
    
    table = Table(box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Created", style="green")
    table.add_column("Type", style="magenta")
    table.add_column("Size", style="yellow", justify="right")
    
    for backup in backups:
        backup_type = "Compressed" if backup['compressed'] else "Directory"
        size_str = _format_size(backup['size'])
        
        # Format date
        try:
            created_dt = datetime.datetime.fromisoformat(backup['created'])
            created_str = format_datetime(created_dt.strftime("%Y-%m-%d %H:%M:%S"))
        except:
            created_str = backup['created']
        
        table.add_row(
            backup['name'],
            created_str,
            backup_type,
            size_str
        )
    
    console.print(table)
    console.print("\n[dim]Restore a backup with: wnote restore <backup_name>[/dim]")
    console.print("[dim]Delete a backup with: wnote list-backups --delete <backup_name>[/dim]")


def _cleanup_old_backups(max_backups: int):
    """Clean up old backups keeping only the most recent ones."""
    try:
        backups = []
        for item in os.listdir(BACKUP_DIR):
            item_path = os.path.join(BACKUP_DIR, item)
            if os.path.isdir(item_path) or item.endswith('.tar.gz'):
                backups.append((item, os.path.getmtime(item_path)))
        
        # Sort by modification time
        backups.sort(key=lambda x: x[1], reverse=True)
        
        # Remove old backups
        for backup_name, _ in backups[max_backups:]:
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            else:
                os.remove(backup_path)
    except Exception:
        pass


def _get_dir_size(path: str) -> int:
    """Calculate total size of a directory."""
    total = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total += os.path.getsize(filepath)
    except Exception:
        pass
    return total


def _format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


# Template commands
@click.group()
def template():
    """Manage note templates"""
    pass


@template.command('create')
@click.argument('name')
@click.option('--description', '-d', help='Template description')
def create_template_cmd(name, description):
    """Create a new note template
    
    Creates a template that can be used when creating new notes.
    Opens your default editor to write the template content.
    
    Examples:
      wnote template create meeting
      wnote template create "project-plan" --description "Template for project planning"
    """
    config = get_config()
    
    # Create temporary file and open in editor
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode='w') as temp:
        temp.write(f"# Template: {name}\n\n")
        if description:
            temp.write(f"# Description: {description}\n\n")
        temp.write("# Write your template content below:\n\n")
        temp_path = temp.name
    
    editor = config['editor']
    try:
        subprocess.run([editor, temp_path], check=True)
        
        # Read the content
        with open(temp_path, 'r') as f:
            content = f.read()
        
        os.unlink(temp_path)
        
        # Create template
        success, msg = create_template(name, content, description)
        if success:
            console.print(f"[bold green]{msg}[/bold green]")
        else:
            console.print(f"[bold red]{msg}[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]Error creating template: {e}[/bold red]")


@template.command('list')
def list_templates():
    """List all available templates
    
    Shows all note templates that can be used when creating notes.
    """
    templates = get_templates()
    
    if not templates:
        console.print("[bold yellow]No templates found[/bold yellow]")
        console.print("[dim]Create a template with: wnote template create <name>[/dim]")
        return
    
    console.print(f"[bold]📋 Available Templates ({len(templates)}):[/bold]\n")
    
    table = Table(box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Created", style="magenta")
    
    for tmpl in templates:
        table.add_row(
            tmpl['name'],
            tmpl['description'] or "[dim]No description[/dim]",
            format_datetime(tmpl['created_at'])
        )
    
    console.print(table)
    console.print("\n[dim]Use a template with: wnote add \"Title\" --template <template_name>[/dim]")


@template.command('show')
@click.argument('name')
def show_template(name):
    """Show template content
    
    Display the content of a specific template.
    
    Example:
      wnote template show meeting
    """
    templates = get_templates()
    template_found = None
    
    for tmpl in templates:
        if tmpl['name'] == name:
            template_found = tmpl
            break
    
    if not template_found:
        console.print(f"[bold red]Template '{name}' not found[/bold red]")
        return
    
    panel = Panel(
        template_found['content'],
        title=f"Template: {name}",
        subtitle=template_found['description'] or "No description",
        box=box.ROUNDED
    )
    console.print(panel)


# Add template subcommands to the backup group for organization
# These will be imported separately in cli.py

