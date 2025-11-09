"""Note management commands for WNote."""

import os
import click
import tempfile
import subprocess
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from ..core import (
    create_note, get_notes, update_note, delete_note,
    get_attachments, add_attachment, get_reminders, get_config
)
from ..utils import format_datetime, get_tag_color, truncate_text, open_attachment

console = Console()


@click.command()
@click.argument('title')
@click.option('--content', '-c', help='Note content (if not provided, will open editor)')
@click.option('--tags', '-t', help='Comma separated tags')
@click.option('--file', '-f', help='Attach a file or directory to the note')
@click.option('--template', help='Use a template for the note')
@click.option('--attach-mode', '-m', 
              type=click.Choice(['symlink', 'copy', 'reference']), 
              default='symlink',
              help='Attachment mode (if --file is used): symlink, copy, or reference')
def add(title, content, tags, file, template, attach_mode):
    """Create a new note with content, tags, and optional file attachment
    
    Creates a note with title and content. Opens your default editor if no 
    content provided. Supports templates and file attachments with different modes.
    
    \b
    Examples:
      Create simple note:
        $ wnote add "Meeting notes" -t "work,meeting"
      
      Create note with inline content:
        $ wnote add "Quick reminder" -c "Buy groceries" -t "personal,todo"
      
      Create note with file attachment (symlink by default):
        $ wnote add "Report" -f ~/Documents/report.pdf -t "work"
      
      Create note with copied file (snapshot):
        $ wnote add "Backup" -f ~/config.json --attach-mode copy
      
      Create note from template:
        $ wnote add "Weekly standup" --template meeting -t "work"
      
      Create note with folder attachment:
        $ wnote add "Project files" -f ~/Projects/myproject/ -t "code"
      
      Create note with reference only (large file):
        $ wnote add "Dataset" -f /data/large.csv --attach-mode reference
    
    \b
    Attachment Modes (with --file):
      • symlink (default) - Creates link, saves space, stays in sync
      • copy - Copies file, uses more space but safer
      • reference - Only saves path, no link or copy
    """
    config = get_config()
    
    if not content:
        # Create a temporary file and open it in the editor
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
            temp_path = temp.name
        
        # Open the editor
        editor = config['editor']
        try:
            subprocess.run([editor, temp_path], check=True)
            
            # Read the content from the file
            with open(temp_path, 'r') as f:
                content = f.read()
            
            # Remove the temporary file
            os.unlink(temp_path)
        except Exception as e:
            console.print(f"[bold red]Error opening editor: {e}[/bold red]")
            return
    
    tag_list = []
    if tags:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    # Add file/folder type tag if attaching
    if file:
        if os.path.isdir(file):
            if 'folder' not in tag_list:
                tag_list.append('folder')
        else:
            if 'file' not in tag_list:
                tag_list.append('file')
    
    note_id = create_note(title, content, tag_list, template_name=template)
    
    # Add file attachment if provided
    if file:
        try:
            abs_file = os.path.abspath(os.path.expanduser(file))
            add_attachment(note_id, abs_file, mode=attach_mode)
            file_type = "folder" if os.path.isdir(abs_file) else "file"
            mode_text = {
                'symlink': 'linked',
                'copy': 'copied',
                'reference': 'referenced'
            }.get(attach_mode, 'attached')
            console.print(f"[bold green]Attached {file_type} ({mode_text}): {file}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error attaching file: {e}[/bold red]")
    
    console.print(f"[bold green]✓ Note created with ID: {note_id}[/bold green]")


@click.command()
@click.argument('note_id', type=int, required=False)
@click.option('--tag', '-t', help='Filter notes by tag')
@click.option('--open-attachments', '-o', is_flag=True, help='Automatically open all attachments')
@click.option('--archived', '-a', is_flag=True, help='Show archived notes only')
@click.option('--all', is_flag=True, help='Show all notes including archived')
def show(note_id, tag, open_attachments, archived, all):
    """Display notes with various filters and options
    
    View all notes in a table, see detailed note with ID, or filter by tag.
    Shows attachment info, reminders, and allows opening files directly.
    
    \b
    Examples:
      Show all active notes (default):
        $ wnote show
      
      Show specific note by ID:
        $ wnote show 5
      
      Show note and open all attachments automatically:
        $ wnote show 5 -o
        $ wnote show 5 --open-attachments
      
      Filter notes by tag:
        $ wnote show -t work
        $ wnote show --tag personal
      
      Show archived notes only:
        $ wnote show --archived
        $ wnote show -a
      
      Show ALL notes (active + archived):
        $ wnote show --all
      
      Combine filters (tag + archived):
        $ wnote show -t work --all
    
    \b
    Tips:
      • Use -o to quickly open all files attached to a note
      • Table view shows preview of note content
      • Archived notes are hidden by default
    """
    config = get_config()
    
    if note_id:
        notes = get_notes(note_id=note_id, include_archived=True)
        if not notes:
            console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
            return
        
        note = notes[0]
        
        # Format tags with colors
        formatted_tags = []
        for tag_name in note.get('tags', []):
            color = get_tag_color(tag_name, config)
            formatted_tags.append(f"[{color}]{tag_name}[/{color}]")
        
        tag_display = " ".join(formatted_tags) if formatted_tags else ""
        
        # Create a panel for the note
        title_text = Text(f"#{note['id']} - {note['title']}")
        if tag_display:
            title_text.append(" - ")
            title_text.append(Text.from_markup(tag_display))
        
        # Add archived indicator
        if note['is_archived']:
            title_text.append(" ")
            title_text.append(Text("[ARCHIVED]", style="bold red"))
        
        panel = Panel(
            note['content'],
            title=title_text,
            subtitle=f"Created: {format_datetime(note['created_at'])} | Updated: {format_datetime(note['updated_at'])}",
            box=box.ROUNDED
        )
        console.print(panel)
        
        # Show attachments
        attachments = get_attachments(note_id)
        if attachments:
            console.print("\n[bold]Attachments:[/bold]")
            
            table = Table(box=box.ROUNDED)
            table.add_column("#", style="cyan", no_wrap=True)
            table.add_column("Filename", style="green")
            table.add_column("Type", style="magenta")
            table.add_column("Original Path", style="white")
            
            for i, attachment in enumerate(attachments):
                file_type = "Directory" if attachment['is_directory'] else "File"
                color = "bright_yellow" if attachment['is_directory'] else "bright_blue"
                
                table.add_row(
                    str(i + 1),
                    attachment['filename'],
                    f"[{color}]{file_type}[/{color}]",
                    attachment['original_path']
                )
            
            console.print(table)
            
            # Open attachments if requested or ask if not specified
            if open_attachments:
                for attachment in attachments:
                    open_attachment(attachment)
            else:
                console.print("\n[bold]Would you like to open any attachments?[/bold]")
                console.print("Enter the number of the attachment to open, 'all' to open all, or press Enter to skip:")
                choice = click.prompt("Choice", default="", show_default=False)
                
                if choice.lower() == 'all':
                    for attachment in attachments:
                        open_attachment(attachment)
                elif choice and choice.isdigit():
                    idx = int(choice) - 1
                    if 0 <= idx < len(attachments):
                        open_attachment(attachments[idx])
                    else:
                        console.print("[bold red]Invalid selection[/bold red]")
    else:
        # Show list of notes
        notes = get_notes(tag=tag, include_archived=all, archived_only=archived)
        
        if not notes:
            message = "No notes found"
            if tag:
                message += f" with tag '{tag}'"
            if archived:
                message += " (archived)"
            console.print(f"[bold yellow]{message}[/bold yellow]")
            return
        
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Tags", no_wrap=True)
        table.add_column("Updated", style="magenta")
        table.add_column("Attachments", style="bright_blue")
        table.add_column("Preview", style="white")
        
        for note in notes:
            # Format tags with colors
            formatted_tags = []
            for tag_name in note.get('tags', []):
                color = get_tag_color(tag_name, config)
                formatted_tags.append(f"[{color}]{tag_name}[/{color}]")
            
            tag_display = " ".join(formatted_tags) if formatted_tags else ""
            
            # Count attachments
            attachments = get_attachments(note['id'])
            attachment_count = len(attachments)
            attachment_display = f"{attachment_count}" if attachment_count > 0 else ""
            
            # Create a preview of the content
            preview = truncate_text(note['content'], config.get('preview_length', 40))
            
            # Add archived indicator to title
            title_display = note['title']
            if note['is_archived']:
                title_display += " [dim](archived)[/dim]"
            
            table.add_row(
                str(note['id']),
                title_display,
                tag_display,
                format_datetime(note['updated_at']),
                attachment_display,
                preview
            )
        
        console.print(table)


@click.command()
@click.argument('note_id', type=int)
def edit(note_id):
    """Open and edit note content in your default editor
    
    Opens the note in your configured text editor (vim, nano, etc.).
    Changes are saved when you exit the editor.
    
    \b
    Examples:
      Edit note content:
        $ wnote edit 1
        $ wnote edit 42
      
      Edit archived note (works too):
        $ wnote edit 5
    
    \b
    Tips:
      • Editor is configured in config.json (default: nano)
      • Set EDITOR environment variable to change default
      • Works with vim, nano, emacs, code, etc.
    """
    config = get_config()
    notes = get_notes(note_id=note_id, include_archived=True)
    if not notes:
        console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
        return
    
    note = notes[0]
    
    # Create a temporary file with the note content
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp:
        temp.write(note['content'].encode())
        temp_path = temp.name
    
    # Open the editor
    editor = config['editor']
    try:
        subprocess.run([editor, temp_path], check=True)
        
        # Read the updated content
        with open(temp_path, 'r') as f:
            new_content = f.read()
        
        # Remove the temporary file
        os.unlink(temp_path)
        
        # Update the note
        update_note(note_id, content=new_content)
        console.print(f"[bold green]Note {note_id} updated[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error opening editor: {e}[/bold red]")


@click.command()
@click.argument('note_id', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--tags', help='Comma separated tags')
@click.option('--archive', is_flag=True, help='Archive the note')
@click.option('--unarchive', is_flag=True, help='Unarchive the note')
def update(note_id, title, tags, archive, unarchive):
    """Update note metadata (title, tags, archive status)
    
    Modify note properties without opening the editor. Use 'edit' command
    to change note content, use 'update' for metadata changes.
    
    \b
    Examples:
      Update title only:
        $ wnote update 1 -t "Updated Title"
        $ wnote update 5 --title "Meeting Notes 2025"
      
      Update tags only (replaces all tags):
        $ wnote update 1 --tags "work,urgent"
        $ wnote update 2 --tags "personal,todo,important"
      
      Remove all tags:
        $ wnote update 3 --tags ""
      
      Archive a note (hide from default view):
        $ wnote update 10 --archive
      
      Unarchive a note (bring back):
        $ wnote update 10 --unarchive
      
      Update multiple things at once:
        $ wnote update 1 -t "New Title" --tags "work,done" --archive
    
    \b
    Tips:
      • Use 'wnote edit' to change content
      • Use 'wnote update' to change metadata
      • Archived notes are hidden but not deleted
    """
    notes = get_notes(note_id=note_id, include_archived=True)
    if not notes:
        console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
        return
    
    tag_list = None
    if tags is not None:
        tag_list = [tag.strip() for tag in tags.split(',')]
    
    is_archived = None
    if archive:
        is_archived = True
    elif unarchive:
        is_archived = False
    
    update_note(note_id, title=title, tags=tag_list, is_archived=is_archived)
    console.print(f"[bold green]Note {note_id} updated[/bold green]")


@click.command()
@click.argument('target', required=True)
@click.option('--force', '-f', is_flag=True, help='Delete without confirmation')
@click.option('--tag', '-t', is_flag=True, help='Delete a tag instead of a note')
@click.option('--reminder', '-r', is_flag=True, help='Delete a reminder by ID')
@click.option('--permanent', '-p', is_flag=True, help='Permanently delete (instead of archiving)')
def delete(target, force, tag, reminder, permanent):
    """Delete or archive notes, tags, and reminders
    
    By DEFAULT, notes are ARCHIVED (not deleted). Use --permanent for real deletion.
    Tags and reminders are always permanently deleted.
    
    \b
    Examples:
      Archive a note (soft delete, can restore):
        $ wnote delete 1
        $ wnote delete 5
      
      Permanently delete note and all related data:
        $ wnote delete 1 --permanent
        $ wnote delete 1 -p
      
      Force delete without confirmation:
        $ wnote delete 10 -pf
      
      Delete a tag from all notes:
        $ wnote delete work --tag
        $ wnote delete urgent -t
      
      Delete a reminder by ID:
        $ wnote delete 3 --reminder
        $ wnote delete 3 -r
    
    \b
    What Gets Deleted:
      • Note (permanent): Content + attachments + reminders + links
      • Note (archive): Hidden but recoverable
      • Tag: Removed from all notes that use it
      • Reminder: Removed from database
    
    \b
    Important:
      • Symlink attachments: Only link removed, original file intact ✓
      • Copy attachments: Copied file deleted, original intact ✓
      • Reference attachments: Only path record removed ✓
    """
    from ..core.database import delete_tag as db_delete_tag, delete_reminder as db_delete_reminder
    
    if reminder:
        # Delete a reminder
        try:
            reminder_id = int(target)
        except ValueError:
            console.print(f"[bold red]Invalid reminder ID: {target}. Must be a number.[/bold red]")
            return
        
        # Get reminder info for confirmation
        reminder_list = get_reminders()
        reminder_found = None
        for r in reminder_list:
            if r['id'] == reminder_id:
                reminder_found = r
                break
        
        if not reminder_found:
            console.print(f"[bold red]Reminder with ID {reminder_id} not found[/bold red]")
            return
        
        if not force:
            console.print(f"[bold yellow]Are you sure you want to delete reminder #{reminder_id}?[/bold yellow]")
            console.print(f"[yellow]Note: #{reminder_found['note_id']} - {reminder_found['note_title']}[/yellow]")
            console.print(f"[yellow]Due: {format_datetime(reminder_found['reminder_datetime'])}[/yellow]")
            console.print(f"[yellow]Message: {reminder_found['message'] or 'No message'}[/yellow]")
            confirm = click.confirm("Delete?")
            if not confirm:
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        success, message = db_delete_reminder(reminder_id)
        if success:
            console.print(f"[bold green]{message}[/bold green]")
        else:
            console.print(f"[bold red]{message}[/bold red]")
        
    elif tag:
        # Delete a tag
        tag_name = target
        
        if not force:
            console.print(f"[bold yellow]Are you sure you want to delete tag '{tag_name}'? This will remove the tag from all notes.[/bold yellow]")
            confirm = click.confirm("Delete?")
            if not confirm:
                console.print("[yellow]Deletion cancelled[/yellow]")
                return
        
        success, message = db_delete_tag(tag_name)
        if success:
            console.print(f"[bold green]{message}[/bold green]")
        else:
            console.print(f"[bold red]{message}[/bold red]")
        
    else:
        # Delete a note
        try:
            note_id = int(target)
        except ValueError:
            console.print(f"[bold red]Invalid note ID: {target}. Must be a number.[/bold red]")
            return
            
        notes = get_notes(note_id=note_id, include_archived=True)
        if not notes:
            console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
            return
        
        note = notes[0]
        
        # Check for related reminders and attachments
        note_reminders = get_reminders(note_id=note_id, include_completed=True)
        note_attachments = get_attachments(note_id)
        
        action = "permanently delete" if permanent else "archive"
        
        if not force:
            console.print(f"[bold yellow]Are you sure you want to {action} note #{note_id} - {note['title']}?[/bold yellow]")
            
            if permanent:
                if note_reminders:
                    console.print(f"[yellow]This note has {len(note_reminders)} reminder(s) that will also be deleted.[/yellow]")
                
                if note_attachments:
                    console.print(f"[yellow]This note has {len(note_attachments)} attachment(s) that will also be deleted.[/yellow]")
            
            confirm = click.confirm(action.capitalize() + "?")
            if not confirm:
                console.print(f"[yellow]{action.capitalize()} cancelled[/yellow]")
                return
        
        success = delete_note(note_id, permanent=permanent)
        if success:
            if permanent:
                deleted_items = [f"Note {note_id}"]
                if note_reminders:
                    deleted_items.append(f"{len(note_reminders)} reminder(s)")
                if note_attachments:
                    deleted_items.append(f"{len(note_attachments)} attachment(s)")
                
                console.print(f"[bold green]Deleted: {', '.join(deleted_items)}[/bold green]")
            else:
                console.print(f"[bold green]Note {note_id} archived[/bold green]")
        else:
            console.print(f"[bold red]Failed to {action} note {note_id}[/bold red]")

