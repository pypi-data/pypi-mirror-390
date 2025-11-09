"""Attachment management commands for WNote."""

import os
import click
from rich.console import Console
from rich.table import Table
from rich import box

from ..core import get_notes, add_attachment, get_attachments, remove_attachment, update_note
from ..utils.formatters import format_file_size

console = Console()


@click.command()
@click.argument('note_id', type=int)
@click.argument('file_path')
@click.option('--mode', '-m', 
              type=click.Choice(['symlink', 'copy', 'reference']), 
              default='symlink',
              help='Attachment mode: symlink (default, saves space), copy (safer), or reference (path only)')
def attach(note_id, file_path, mode):
    """Attach a file or directory to an existing note
    
    By default, creates a symbolic link (symlink) to save disk space.
    The file stays in sync with the original.
    
    \b
    Attachment Modes:
      • symlink (default) - Creates symbolic link, saves space, stays in sync
      • copy - Copies file, uses more space but safer
      • reference - Only saves path, no link or copy
    
    \b
    Examples:
      Attach with symlink (default, recommended):
        $ wnote attach 1 ./myfile.txt
      
      Attach folder with symlink:
        $ wnote attach 2 ~/Documents/project/
      
      Attach with copy (if you need a snapshot):
        $ wnote attach 3 report.pdf --mode copy
      
      Attach as reference only (no link/copy):
        $ wnote attach 4 /external/drive/data.csv --mode reference
      
      Attach from different drive:
        $ wnote attach 5 /run/media/user/USB/backup/
    
    \b
    Tips:
      • Use symlink for files that update frequently
      • Use copy for files you might delete later
      • Use reference for large files on external drives
    """
    # Check if note exists
    notes = get_notes(note_id=note_id, include_archived=True)
    if not notes:
        console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
        return
    
    # Expand the file path
    expanded_path = os.path.expanduser(file_path)
    abs_path = os.path.abspath(expanded_path)
    
    # Check if the file exists
    if not os.path.exists(abs_path):
        console.print(f"[bold red]File or directory not found: {abs_path}[/bold red]")
        console.print("[yellow]Please provide a valid absolute path or a path relative to the current directory[/yellow]")
        return
    
    # Add appropriate tag
    note_tags = notes[0].get('tags', [])
    if os.path.isdir(abs_path):
        if 'folder' not in note_tags:
            note_tags.append('folder')
    else:
        if 'file' not in note_tags:
            note_tags.append('file')
    
    update_note(note_id, tags=note_tags)
    
    # Add the attachment
    try:
        add_attachment(note_id, abs_path, mode=mode)
        file_type = "folder" if os.path.isdir(abs_path) else "file"
        
        # Show appropriate message based on mode
        if mode == 'symlink':
            console.print(f"[bold green]✓ Created symlink to {file_type}: {abs_path}[/bold green]")
            console.print(f"[dim]Mode: symbolic link (saves space, stays in sync)[/dim]")
        elif mode == 'copy':
            console.print(f"[bold green]✓ Copied {file_type} to note {note_id}: {abs_path}[/bold green]")
            console.print(f"[dim]Mode: copy (snapshot taken)[/dim]")
        else:  # reference
            console.print(f"[bold green]✓ Added reference to {file_type}: {abs_path}[/bold green]")
            console.print(f"[dim]Mode: reference only (path saved)[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        console.print("[yellow]Try using an absolute path or check file permissions[/yellow]")


@click.command()
@click.argument('note_id', type=int)
@click.option('--attachment-id', '-a', type=int, help='Specific attachment ID to remove')
@click.option('--list', '-l', is_flag=True, help='List attachments for the note')
@click.option('--all', is_flag=True, help='Remove all attachments from the note')
def deattach(note_id, attachment_id, list, all):
    """Manage and remove attachments from notes
    
    List, view details, and remove file/folder attachments from your notes.
    Shows attachment mode (symlink, copy, or reference) for each attachment.
    
    \b
    Examples:
      List all attachments for a note:
        $ wnote deattach 1 --list
        $ wnote deattach 1 -l
      
      Remove specific attachment by ID:
        $ wnote deattach 1 --attachment-id 3
        $ wnote deattach 1 -a 3
      
      Remove all attachments from a note:
        $ wnote deattach 1 --all
      
      Workflow: list first, then remove:
        $ wnote deattach 5 -l    # See attachment IDs
        $ wnote deattach 5 -a 2  # Remove attachment ID 2
    
    \b
    Note:
      • Removing symlink: Only removes the link, original file stays intact
      • Removing copy: Deletes the copied file
      • Removing reference: Only removes the path record
    """
    # Check if note exists
    notes = get_notes(note_id=note_id, include_archived=True)
    if not notes:
        console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
        return
    
    attachments = get_attachments(note_id)
    
    if not attachments:
        console.print(f"[bold yellow]Note {note_id} has no attachments[/bold yellow]")
        return
    
    if list:
        # List attachments
        console.print(f"[bold]Attachments for Note #{note_id}:[/bold]")
        
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Filename", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Mode", style="yellow")
        table.add_column("Original Path", style="white")
        table.add_column("Size", style="bright_blue")
        
        for attachment in attachments:
            file_type = "Directory" if attachment['is_directory'] else "File"
            attach_mode = attachment.get('attachment_mode', 'copy')  # Default to copy for old entries
            
            # Mode with icon
            mode_display = {
                'symlink': '🔗 link',
                'copy': '📄 copy',
                'reference': '📌 ref'
            }.get(attach_mode, attach_mode)
            
            # Get file/directory size
            size_str = "N/A"
            stored_path = attachment['stored_path']
            
            # Check if file exists (handle broken symlinks)
            file_exists = False
            if attach_mode == 'symlink':
                file_exists = os.path.exists(stored_path) and not os.path.islink(stored_path) or (os.path.islink(stored_path) and os.path.exists(os.readlink(stored_path)))
            elif attach_mode == 'reference':
                file_exists = os.path.exists(attachment['original_path'])
            else:
                file_exists = os.path.exists(stored_path)
            
            if file_exists:
                check_path = attachment['original_path'] if attach_mode == 'reference' else stored_path
                if os.path.isdir(check_path):
                    try:
                        item_count = len(os.listdir(check_path))
                        size_str = f"{item_count} items"
                    except:
                        size_str = "N/A"
                else:
                    try:
                        size_bytes = os.path.getsize(check_path)
                        size_str = format_file_size(size_bytes)
                    except:
                        size_str = "N/A"
            else:
                size_str = "[red]❌ Missing[/red]"
            
            table.add_row(
                str(attachment['id']),
                attachment['filename'],
                f"[{'bright_yellow' if attachment['is_directory'] else 'bright_blue'}]{file_type}[/{'bright_yellow' if attachment['is_directory'] else 'bright_blue'}]",
                mode_display,
                attachment['original_path'],
                size_str
            )
        
        console.print(table)
        return
    
    if all:
        # Remove all attachments
        if not click.confirm(f"Are you sure you want to remove all {len(attachments)} attachments from note {note_id}?"):
            console.print("[yellow]Operation cancelled[/yellow]")
            return
        
        removed_count = 0
        for attachment in attachments:
            success, msg = remove_attachment(attachment['id'])
            if success:
                removed_count += 1
            else:
                console.print(f"[bold red]Failed to remove {attachment['filename']}: {msg}[/bold red]")
        
        console.print(f"[bold green]Removed {removed_count} attachments from note {note_id}[/bold green]")
        return
    
    if attachment_id:
        # Remove specific attachment
        attachment_found = False
        for attachment in attachments:
            if attachment['id'] == attachment_id:
                attachment_found = True
                break
        
        if not attachment_found:
            console.print(f"[bold red]Attachment with ID {attachment_id} not found in note {note_id}[/bold red]")
            return
        
        success, msg = remove_attachment(attachment_id)
        if success:
            console.print(f"[bold green]{msg}[/bold green]")
        else:
            console.print(f"[bold red]{msg}[/bold red]")
        return
    
    # If no specific action, show help
    console.print("[bold yellow]Please specify an action:[/bold yellow]")
    console.print("  --list (-l): List attachments")
    console.print("  --attachment-id (-a) <ID>: Remove specific attachment")
    console.print("  --all: Remove all attachments")
    console.print("\nUse 'wnote deattach --help' for more information.")

