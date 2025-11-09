"""Export and search commands for WNote."""

import click
import datetime
import html
import markdown
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ..core import get_notes, get_connection, get_notes_statistics, get_config
from ..core.database import safe_close_connection
from ..utils import format_datetime, get_tag_color

console = Console()


@click.command()
@click.argument('note_id', type=int)
@click.option('--format', '-f', type=click.Choice(['text', 'markdown', 'html']), default='text', help='Export format')
@click.option('--output', '-o', help='Output file (if not provided, prints to stdout)')
def export(note_id, format, output):
    """Export note to various formats
    
    Export a note to plain text, Markdown, or HTML format.
    
    Examples:
      Export to console:
        wnote export 1 --format markdown
      
      Export to file:
        wnote export 1 --format html --output note.html
    """
    notes = get_notes(note_id=note_id, include_archived=True)
    if not notes:
        console.print(f"[bold red]Note with ID {note_id} not found[/bold red]")
        return
    
    note = notes[0]
    
    # Prepare header with metadata
    header = f"# {note['title']}\n\n"
    if note['tags']:
        header += f"Tags: {', '.join(note['tags'])}\n"
    header += f"Created: {format_datetime(note['created_at'])}\n"
    header += f"Updated: {format_datetime(note['updated_at'])}\n\n"
    
    # Prepare content based on format
    content = header + note['content']
    
    if format == 'markdown':
        exported_content = content
        
    elif format == 'html':
        # Convert to HTML
        md_content = markdown.markdown(content)
        
        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(note['title'])}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; max-width: 800px; margin: auto; }}
        h1 {{ color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }}
        .metadata {{ color: #666; margin-bottom: 20px; font-size: 0.9em; }}
        code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
    </style>
</head>
<body>
    {md_content}
</body>
</html>
"""
        exported_content = html_template
        
    else:  # text
        exported_content = content
    
    # Output the content
    if output:
        try:
            with open(output, 'w') as f:
                f.write(exported_content)
            console.print(f"[bold green]Note exported to {output}[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error writing to file: {e}[/bold red]")
    else:
        if format == 'html':
            console.print("[bold yellow]HTML output would be better saved to a file.[/bold yellow]")
        console.print(exported_content)


@click.command()
@click.argument('query', required=True)
@click.option('--case-sensitive', '-c', is_flag=True, help='Enable case-sensitive search')
@click.option('--tag', '-t', help='Filter search results by tag')
@click.option('--archived', '-a', is_flag=True, help='Include archived notes in search')
def search(query, case_sensitive, tag, archived):
    """Search notes by content or title
    
    Search through notes' content and titles for matching text.
    By default, the search is case-insensitive and excludes archived notes.
    
    Examples:
      wnote search meeting
      wnote search "python code" --case-sensitive
      wnote search project --tag work
      wnote search todo --archived
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Base query
        base_query = """
            SELECT n.*, GROUP_CONCAT(t.name) as tags
            FROM notes n
            LEFT JOIN note_tags nt ON n.id = nt.note_id
            LEFT JOIN tags t ON nt.tag_id = t.id
        """
        
        conditions = []
        params = []
        
        # Add search condition
        if case_sensitive:
            conditions.append("(n.title LIKE ? OR n.content LIKE ?)")
            search_param = f"%{query}%"
        else:
            conditions.append("(n.title LIKE ? COLLATE NOCASE OR n.content LIKE ? COLLATE NOCASE)")
            search_param = f"%{query}%"
        params.extend([search_param, search_param])
        
        # Add tag filter if specified
        if tag:
            base_query = """
                SELECT n.*, GROUP_CONCAT(t2.name) as tags
                FROM notes n
                JOIN note_tags nt ON n.id = nt.note_id
                JOIN tags t ON nt.tag_id = t.id
                LEFT JOIN note_tags nt2 ON n.id = nt2.note_id
                LEFT JOIN tags t2 ON nt2.tag_id = t2.id
            """
            conditions.append("t.name = ?")
            params.append(tag)
        
        # Add archived filter
        if not archived:
            conditions.append("n.is_archived = 0")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " GROUP BY n.id ORDER BY n.updated_at DESC"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        if not results:
            console.print(f"[bold yellow]No notes found matching '{query}'[/bold yellow]")
            return
        
        # Process and display results
        console.print(f"[bold green]Found {len(results)} notes matching '{query}':[/bold green]\n")
        
        config = get_config()
        table = Table(box=box.ROUNDED)
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Title", style="green")
        table.add_column("Tags", no_wrap=True)
        table.add_column("Updated", style="magenta")
        table.add_column("Relevance", style="yellow")
        
        for note in results:
            note_dict = dict(note)
            
            # Format tags with colors
            tags_list = note_dict['tags'].split(',') if note_dict['tags'] else []
            formatted_tags = []
            for tag_name in tags_list:
                color = get_tag_color(tag_name, config)
                formatted_tags.append(f"[{color}]{tag_name}[/{color}]")
            
            tag_display = " ".join(formatted_tags) if formatted_tags else ""
            
            # Calculate relevance score
            title_count = note_dict['title'].lower().count(query.lower()) if not case_sensitive else note_dict['title'].count(query)
            content_count = note_dict['content'].lower().count(query.lower()) if not case_sensitive else note_dict['content'].count(query)
            relevance = title_count * 2 + content_count  # Title matches weighted more
            
            # Add archived indicator
            title_display = note_dict['title']
            if note_dict.get('is_archived', 0):
                title_display += " [dim](archived)[/dim]"
            
            # Add row to table
            table.add_row(
                str(note_dict['id']),
                title_display,
                tag_display,
                format_datetime(note_dict['updated_at']),
                f"{relevance} matches"
            )
        
        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error searching notes: {e}[/bold red]")
    finally:
        safe_close_connection(conn)


@click.command()
def stats():
    """Display comprehensive statistics about your notes
    
    Shows detailed statistics including note counts, tag usage,
    recent activity, attachments, and reminders.
    """
    stats_data = get_notes_statistics()
    
    if not stats_data:
        console.print("[bold red]Unable to retrieve statistics[/bold red]")
        return
    
    config = get_config()
    
    # Main statistics panel
    main_stats = f"""[bold cyan]📊 WNote Statistics[/bold cyan]

[green]📝 Active Notes:[/green] {stats_data['active_notes']}
[yellow]📦 Archived Notes:[/yellow] {stats_data['archived_notes']}
[white]📄 Total Notes:[/white] {stats_data['total_notes']}
[blue]🏷️  Tags:[/blue] {stats_data['total_tags']}
[yellow]📎 Attachments:[/yellow] {stats_data['total_attachments']} ({stats_data['attachment_types']['files']} files, {stats_data['attachment_types']['directories']} directories)
[magenta]⏰ Active Reminders:[/magenta] {stats_data['active_reminders']}
[cyan]✅ Completed Reminders:[/cyan] {stats_data['completed_reminders']}
[red]📅 Upcoming (7 days):[/red] {stats_data['upcoming_reminders']}
[bright_blue]🔗 Note Links:[/bright_blue] {stats_data.get('total_note_links', 0)}
[bright_magenta]📋 Templates:[/bright_magenta] {stats_data.get('total_templates', 0)}
[white]📏 Avg Content Length:[/white] {stats_data['avg_content_length']} characters"""
    
    console.print(Panel(main_stats, title="Overview", box=box.ROUNDED))
    console.print()
    
    # Notes by tag
    if stats_data['notes_by_tag']:
        console.print("[bold]🏷️  Notes by Tag (Top 10):[/bold]")
        tag_table = Table(box=box.ROUNDED)
        tag_table.add_column("Tag", style="green")
        tag_table.add_column("Count", style="cyan", justify="right")
        tag_table.add_column("Percentage", style="yellow", justify="right")
        
        for tag_data in stats_data['notes_by_tag']:
            if tag_data['count'] > 0:
                percentage = (tag_data['count'] / stats_data['total_notes']) * 100 if stats_data['total_notes'] > 0 else 0
                color = get_tag_color(tag_data['name'], config)
                tag_table.add_row(
                    f"[{color}]{tag_data['name']}[/{color}]",
                    str(tag_data['count']),
                    f"{percentage:.1f}%"
                )
        
        console.print(tag_table)
        console.print()
    
    # Recent activity
    if stats_data['recent_activity']:
        console.print("[bold]📈 Recent Activity (Last 7 Days):[/bold]")
        activity_table = Table(box=box.ROUNDED)
        activity_table.add_column("Date", style="magenta")
        activity_table.add_column("Notes Created", style="green", justify="right")
        activity_table.add_column("Activity Bar", style="blue")
        
        max_count = max(day['count'] for day in stats_data['recent_activity']) if stats_data['recent_activity'] else 1
        
        for day_data in stats_data['recent_activity']:
            date_obj = datetime.datetime.strptime(day_data['date'], '%Y-%m-%d')
            formatted_date = date_obj.strftime('%m/%d')
            
            # Create simple activity bar
            bar_length = int((day_data['count'] / max_count) * 20) if max_count > 0 else 0
            activity_bar = "█" * bar_length + "░" * (20 - bar_length)
            
            activity_table.add_row(
                formatted_date,
                str(day_data['count']),
                f"[blue]{activity_bar}[/blue]"
            )
        
        console.print(activity_table)
        console.print()
    
    # Oldest and newest notes
    if stats_data['oldest_note'] and stats_data['newest_note']:
        timeline_info = f"""[bold]📅 Timeline:[/bold]

[green]📝 Oldest Note:[/green] "{stats_data['oldest_note']['title']}" 
    Created: {format_datetime(stats_data['oldest_note']['created_at'])}

[blue]✨ Newest Note:[/blue] "{stats_data['newest_note']['title']}"
    Created: {format_datetime(stats_data['newest_note']['created_at'])}"""
        
        console.print(Panel(timeline_info, title="Note Timeline", box=box.ROUNDED))
        console.print()
    
    # Quick tips
    tips = []
    
    if stats_data['total_notes'] == 0:
        tips.append("💡 Get started by creating your first note: wnote add \"My First Note\"")
    elif stats_data['active_notes'] < 10:
        tips.append("📝 You're just getting started! Try organizing your notes with tags.")
    elif stats_data['total_tags'] == 0:
        tips.append("🏷️  Consider adding tags to your notes for better organization.")
    elif stats_data['active_reminders'] == 0:
        tips.append("⏰ Set reminders for important notes: wnote reminder <note_id> \"2025-12-31 14:30\"")
    
    if stats_data['total_attachments'] == 0:
        tips.append("📎 Attach files to your notes: wnote attach <note_id> <file_path>")
    
    if stats_data['avg_content_length'] < 50:
        tips.append("📏 Your notes are quite short. Consider adding more detailed content!")
    
    if stats_data.get('total_templates', 0) == 0:
        tips.append("📋 Create templates for common note types: wnote template create <name>")
    
    if tips:
        tip_text = "\n".join(f"  {tip}" for tip in tips[:3])
        console.print(Panel(tip_text, title="💡 Tips", box=box.ROUNDED))

