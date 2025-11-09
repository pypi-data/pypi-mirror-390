"""Reminder management commands for WNote."""

import click
import datetime
from rich.console import Console
from rich.table import Table
from rich import box

from ..core import add_reminder, get_reminders, complete_reminder, delete_reminder
from ..utils import format_datetime

console = Console()


@click.command()
@click.argument('note_id', type=int)
@click.argument('datetime_str', required=True)
@click.argument('message', required=False)
def reminder(note_id, datetime_str, message):
    """Add a reminder for a note
    
    Add a reminder that will alert you at a specific date and time.
    
    Datetime format: YYYY-MM-DD HH:MM or YYYY-MM-DD
    
    Examples:
      Add reminder with specific time:
        wnote reminder 1 "2025-12-31 14:30" "Project deadline"
        
      Add reminder for a specific date (will use 09:00 as default time):
        wnote reminder 1 "2025-12-31" "Important meeting"
    """
    try:
        # Parse the datetime string
        if len(datetime_str) == 10:  # YYYY-MM-DD format
            datetime_str += " 09:00"  # Default to 9:00 AM
        
        # Validate datetime format
        parsed_datetime = datetime.datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
        
        # Check if the datetime is in the future
        if parsed_datetime <= datetime.datetime.now():
            console.print("[bold red]Reminder datetime must be in the future[/bold red]")
            return
        
        success, msg = add_reminder(note_id, datetime_str, message)
        
        if success:
            console.print(f"[bold green]{msg}[/bold green]")
            console.print(f"[green]Reminder set for {format_datetime(datetime_str)}[/green]")
        else:
            console.print(f"[bold red]{msg}[/bold red]")
            
    except ValueError:
        console.print("[bold red]Invalid datetime format. Use YYYY-MM-DD HH:MM or YYYY-MM-DD[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@click.command()
@click.option('--note-id', '-n', type=int, help='Show reminders for specific note')
@click.option('--include-completed', '-c', is_flag=True, help='Include completed reminders')
@click.option('--complete', type=int, help='Mark reminder as completed by ID')
@click.option('--delete', type=int, help='Delete reminder by ID')
def reminders(note_id, include_completed, complete, delete):
    """Manage reminders for notes
    
    This command allows you to view, complete, and delete reminders for your notes.
    You can view all reminders, filter by note ID, and manage their status.
    
    Examples:
      Show all active reminders:
        wnote reminders
        
      Show reminders for a specific note:
        wnote reminders -n 1
        
      Show all reminders including completed ones:
        wnote reminders -c
        
      Mark a reminder as completed:
        wnote reminders --complete 1
        
      Delete a reminder:
        wnote reminders --delete 1
    """
    if complete:
        success, msg = complete_reminder(complete)
        if success:
            console.print(f"[bold green]{msg}[/bold green]")
        else:
            console.print(f"[bold red]{msg}[/bold red]")
        return
    
    if delete:
        success, msg = delete_reminder(delete)
        if success:
            console.print(f"[bold green]{msg}[/bold green]")
        else:
            console.print(f"[bold red]{msg}[/bold red]")
        return
    
    # Show reminders
    reminder_list = get_reminders(note_id, include_completed)
    
    if not reminder_list:
        message = "No reminders found"
        if note_id:
            message += f" for note {note_id}"
        if not include_completed:
            message += " (use --include-completed to see completed reminders)"
        console.print(f"[bold yellow]{message}[/bold yellow]")
        return
    
    # Separate overdue, upcoming, and completed reminders
    now = datetime.datetime.now()
    overdue = []
    upcoming = []
    completed = []
    
    for reminder in reminder_list:
        reminder_dt = datetime.datetime.fromisoformat(reminder['reminder_datetime'])
        if reminder['is_completed']:
            completed.append(reminder)
        elif reminder_dt < now:
            overdue.append(reminder)
        else:
            upcoming.append(reminder)
    
    # Display overdue reminders
    if overdue:
        console.print("[bold red]⚠️  OVERDUE REMINDERS:[/bold red]")
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Note", style="green")
        table.add_column("Due", style="red")
        table.add_column("Message", style="white")
        
        for reminder in overdue:
            table.add_row(
                str(reminder['id']),
                f"#{reminder['note_id']} - {reminder['note_title']}",
                format_datetime(reminder['reminder_datetime']),
                reminder['message'] or ""
            )
        console.print(table)
        console.print()
    
    # Display upcoming reminders
    if upcoming:
        console.print("[bold green]📅 UPCOMING REMINDERS:[/bold green]")
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Note", style="green")
        table.add_column("Due", style="magenta")
        table.add_column("Message", style="white")
        
        for reminder in upcoming:
            table.add_row(
                str(reminder['id']),
                f"#{reminder['note_id']} - {reminder['note_title']}",
                format_datetime(reminder['reminder_datetime']),
                reminder['message'] or ""
            )
        console.print(table)
        console.print()
    
    # Display completed reminders if requested
    if completed and include_completed:
        console.print("[bold blue]✅ COMPLETED REMINDERS:[/bold blue]")
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Note", style="green")
        table.add_column("Was Due", style="blue")
        table.add_column("Message", style="white")
        
        for reminder in completed:
            table.add_row(
                str(reminder['id']),
                f"#{reminder['note_id']} - {reminder['note_title']}",
                format_datetime(reminder['reminder_datetime']),
                reminder['message'] or ""
            )
        console.print(table)

