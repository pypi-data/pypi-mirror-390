"""Database operations for WNote."""

import os
import sqlite3
import datetime
import shutil
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path

from .config import DB_PATH, ATTACHMENTS_DIR
from ..utils.decorators import retry_on_locked


def init_db() -> None:
    """Initialize the database if it doesn't exist."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL;")
        cursor = conn.cursor()
        
        # Create notes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            is_archived INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create tags table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
        ''')
        
        # Create note_tags table (many-to-many relationship)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_tags (
            note_id INTEGER,
            tag_id INTEGER,
            PRIMARY KEY (note_id, tag_id),
            FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
        )
        ''')
        
        # Create attachments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attachments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            original_path TEXT NOT NULL,
            stored_path TEXT NOT NULL,
            is_directory INTEGER NOT NULL DEFAULT 0,
            attachment_mode TEXT DEFAULT 'symlink',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
        )
        ''')
        
        # Add attachment_mode column if it doesn't exist (migration)
        try:
            cursor.execute("SELECT attachment_mode FROM attachments LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE attachments ADD COLUMN attachment_mode TEXT DEFAULT 'symlink'")
        
        # Create reminders table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            reminder_datetime TIMESTAMP NOT NULL,
            message TEXT,
            is_completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES notes (id) ON DELETE CASCADE
        )
        ''')
        
        # Create note_links table for linking notes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS note_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_note_id INTEGER NOT NULL,
            target_note_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_note_id) REFERENCES notes (id) ON DELETE CASCADE,
            FOREIGN KEY (target_note_id) REFERENCES notes (id) ON DELETE CASCADE,
            UNIQUE(source_note_id, target_note_id)
        )
        ''')
        
        # Create templates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


def get_connection() -> sqlite3.Connection:
    """Get a database connection with proper settings."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0, isolation_level=None)
    conn.row_factory = sqlite3.Row
    
    # Execute pragma commands to improve reliability
    conn.execute("PRAGMA journal_mode = DELETE")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("PRAGMA busy_timeout = 10000")
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn


def safe_close_connection(conn: Optional[sqlite3.Connection]) -> None:
    """Safely close a database connection."""
    try:
        if conn:
            conn.close()
    except Exception:
        pass


@retry_on_locked
def get_tag_id(tag_name: str) -> int:
    """Get tag ID or create if it doesn't exist."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        result = cursor.fetchone()
        
        if result:
            tag_id = result['id']
        else:
            cursor.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
            tag_id = cursor.lastrowid
        
        conn.commit()
        return tag_id
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        safe_close_connection(conn)


@retry_on_locked
def create_note(title: str, content: str, tags: Optional[List[str]] = None, 
                template_name: Optional[str] = None, is_archived: bool = False) -> int:
    """Create a new note with optional tags and template."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # If template is specified, use its content
        if template_name:
            cursor.execute("SELECT content FROM templates WHERE name = ?", (template_name,))
            template_result = cursor.fetchone()
            if template_result:
                content = template_result['content'] + "\n\n" + content
        
        # Check for the smallest unused ID (to reuse deleted IDs)
        cursor.execute("""
            WITH RECURSIVE
            numbers(id) AS (
                SELECT 1
                UNION ALL
                SELECT id + 1
                FROM numbers
                WHERE id < (SELECT COALESCE(MAX(id), 0) + 1 FROM notes)
            )
            SELECT MIN(n.id)
            FROM numbers n
            LEFT JOIN notes t ON n.id = t.id
            WHERE t.id IS NULL
        """)
        result = cursor.fetchone()
        next_id = result[0] if result[0] is not None else 1
        
        # Insert note
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO notes (id, title, content, is_archived, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (next_id, title, content, 1 if is_archived else 0, current_time, current_time)
        )
        note_id = next_id
        
        # Add tags
        if tags:
            for tag in tags:
                tag_id = get_tag_id(tag)
                cursor.execute(
                    "INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)",
                    (note_id, tag_id)
                )
        
        conn.commit()
        return note_id
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        safe_close_connection(conn)


def get_notes(note_id: Optional[int] = None, tag: Optional[str] = None, 
              include_archived: bool = False, archived_only: bool = False) -> List[Dict[str, Any]]:
    """Get all notes or a specific note by ID or tag."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        base_query = """
            SELECT n.*, GROUP_CONCAT(t.name) as tags
            FROM notes n
            LEFT JOIN note_tags nt ON n.id = nt.note_id
            LEFT JOIN tags t ON nt.tag_id = t.id
        """
        
        conditions = []
        params = []
        
        if note_id:
            conditions.append("n.id = ?")
            params.append(note_id)
        
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
        
        # Handle archived filter
        if archived_only:
            conditions.append("n.is_archived = 1")
        elif not include_archived:
            conditions.append("n.is_archived = 0")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " GROUP BY n.id ORDER BY n.updated_at DESC"
        
        cursor.execute(base_query, params)
        notes = [dict(row) for row in cursor.fetchall()]
        
        # Process tags from string to list
        for note in notes:
            if note['tags']:
                note['tags'] = note['tags'].split(',')
            else:
                note['tags'] = []
        
        return notes
    except Exception as e:
        print(f"Error getting notes: {e}")
        return []
    finally:
        safe_close_connection(conn)


@retry_on_locked
def update_note(note_id: int, title: Optional[str] = None, content: Optional[str] = None, 
                tags: Optional[List[str]] = None, is_archived: Optional[bool] = None) -> bool:
    """Update an existing note."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if is_archived is not None:
            updates.append("is_archived = ?")
            params.append(1 if is_archived else 0)
        
        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
            params.append(note_id)
            cursor.execute(query, params)
        
        if tags is not None:
            # Remove existing tags
            cursor.execute("DELETE FROM note_tags WHERE note_id = ?", (note_id,))
            
            # Add new tags
            for tag in tags:
                tag_id = get_tag_id(tag)
                cursor.execute(
                    "INSERT INTO note_tags (note_id, tag_id) VALUES (?, ?)",
                    (note_id, tag_id)
                )
        
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        safe_close_connection(conn)


@retry_on_locked
def delete_note(note_id: int, permanent: bool = False) -> bool:
    """Delete or archive a note by ID."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if permanent:
            # Get attachments info to delete properly based on mode
            cursor.execute("SELECT stored_path, attachment_mode, is_directory FROM attachments WHERE note_id = ?", (note_id,))
            attachments = cursor.fetchall()
            
            # Delete attachment records from database
            cursor.execute("DELETE FROM attachments WHERE note_id = ?", (note_id,))
            
            # Delete the note (cascades to note_tags, reminders, note_links)
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            
            conn.commit()
            
            # Delete attachment files/links from disk (NOT original files!)
            for attachment in attachments:
                stored_path = attachment['stored_path']
                attach_mode = attachment.get('attachment_mode', 'copy')  # Default to copy for old entries
                is_directory = attachment['is_directory']
                
                # Skip if reference mode (no file to delete)
                if attach_mode == 'reference':
                    continue
                
                if os.path.exists(stored_path) or os.path.islink(stored_path):
                    try:
                        if attach_mode == 'symlink':
                            # Remove symlink only (DON'T touch original file!)
                            if os.path.islink(stored_path):
                                os.unlink(stored_path)
                                print(f"Removed symlink: {stored_path}")
                            # Safety: If somehow it's not a symlink, don't delete!
                            # This protects original files
                        elif attach_mode == 'copy':
                            # Remove copied file/directory
                            if is_directory and os.path.isdir(stored_path):
                                shutil.rmtree(stored_path)
                                print(f"Removed copied directory: {stored_path}")
                            elif os.path.isfile(stored_path):
                                os.remove(stored_path)
                                print(f"Removed copied file: {stored_path}")
                    except Exception as e:
                        print(f"Warning: Could not delete attachment {stored_path}: {e}")
        else:
            # Archive the note instead of deleting
            cursor.execute("UPDATE notes SET is_archived = 1 WHERE id = ?", (note_id,))
            conn.commit()
        
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error deleting note: {e}")
        return False
    finally:
        safe_close_connection(conn)


def get_all_tags() -> List[str]:
    """Get all existing tags."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM tags ORDER BY name")
        tags = [row['name'] for row in cursor.fetchall()]
        
        return tags
    except Exception as e:
        print(f"Error getting tags: {e}")
        return []
    finally:
        safe_close_connection(conn)


@retry_on_locked
def delete_tag(tag_name: str) -> Tuple[bool, str]:
    """Delete a tag from the database and remove it from all notes."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        result = cursor.fetchone()
        
        if not result:
            return False, f"Tag '{tag_name}' not found"
        
        tag_id = result[0]
        
        cursor.execute("SELECT COUNT(*) FROM note_tags WHERE tag_id = ?", (tag_id,))
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM note_tags WHERE tag_id = ?", (tag_id,))
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        
        conn.commit()
        return True, f"Tag '{tag_name}' deleted from {count} notes"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error deleting tag: {e}"
    finally:
        safe_close_connection(conn)


@retry_on_locked
def add_attachment(note_id: int, file_path: str, mode: str = 'symlink') -> bool:
    """Add a file or directory attachment to a note.
    
    Args:
        note_id: ID of the note to attach to
        file_path: Path to the file or directory
        mode: Attachment mode - 'symlink' (default), 'copy', or 'reference'
              - symlink: Create symbolic link (saves space, file stays in sync)
              - copy: Copy file (safe but uses more space)
              - reference: Only save path reference (no copy, no link)
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        abs_path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File or directory not found: {abs_path}")
        
        if not os.access(abs_path, os.R_OK):
            raise PermissionError(f"No read permission for: {abs_path}")
        
        filename = os.path.basename(abs_path)
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        unique_name = f"{note_id}_{timestamp}_{filename}"
        attachment_path = os.path.join(ATTACHMENTS_DIR, unique_name)
        
        is_directory = os.path.isdir(abs_path)
        
        # Handle different attachment modes
        if mode == 'reference':
            # Reference only - no file operation, just save path
            attachment_path = abs_path
        elif mode == 'symlink':
            # Create symlink (default)
            try:
                if os.path.exists(attachment_path) or os.path.islink(attachment_path):
                    os.remove(attachment_path)
                os.symlink(abs_path, attachment_path)
            except OSError as e:
                raise IOError(f"Failed to create symlink: {e}")
        elif mode == 'copy':
            # Copy file or directory (old behavior)
            if not os.access(ATTACHMENTS_DIR, os.W_OK):
                raise PermissionError(f"No write permission to attachments directory: {ATTACHMENTS_DIR}")
            
            try:
                if is_directory:
                    if os.path.exists(attachment_path):
                        shutil.rmtree(attachment_path)
                    shutil.copytree(abs_path, attachment_path)
                else:
                    shutil.copy2(abs_path, attachment_path)
            except (shutil.Error, IOError, OSError) as e:
                raise IOError(f"Failed to copy file: {e}")
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'symlink', 'copy', or 'reference'")
        
        # Record in database with mode
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO attachments (note_id, filename, original_path, stored_path, is_directory, attachment_mode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (note_id, filename, abs_path, attachment_path, 1 if is_directory else 0, mode, current_time))
        
        conn.commit()
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        safe_close_connection(conn)


def get_attachments(note_id: int) -> List[Dict[str, Any]]:
    """Get all attachments for a note."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM attachments
            WHERE note_id = ?
            ORDER BY created_at
        """, (note_id,))
        
        attachments = [dict(row) for row in cursor.fetchall()]
        return attachments
    except Exception as e:
        print(f"Error getting attachments: {e}")
        return []
    finally:
        safe_close_connection(conn)


@retry_on_locked
def remove_attachment(attachment_id: int) -> Tuple[bool, str]:
    """Remove an attachment from a note and delete the file/link."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT stored_path, attachment_mode, is_directory FROM attachments WHERE id = ?", (attachment_id,))
        result = cursor.fetchone()
        
        if not result:
            return False, f"Attachment with ID {attachment_id} not found"
        
        stored_path = result['stored_path']
        attach_mode = result.get('attachment_mode', 'copy')
        is_directory = result['is_directory']
        
        # Delete from database first
        cursor.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
        conn.commit()
        
        # Handle file/link deletion based on mode
        if attach_mode == 'reference':
            # Reference only - no file to delete
            return True, "Reference removed successfully (original file intact)"
        
        if os.path.exists(stored_path) or os.path.islink(stored_path):
            try:
                if attach_mode == 'symlink':
                    # Remove symlink only (original file stays intact)
                    if os.path.islink(stored_path):
                        os.unlink(stored_path)
                        return True, "Symlink removed successfully (original file intact)"
                    elif is_directory:
                        shutil.rmtree(stored_path)
                    else:
                        os.remove(stored_path)
                elif attach_mode == 'copy':
                    # Remove copied file/directory
                    if is_directory and os.path.isdir(stored_path):
                        shutil.rmtree(stored_path)
                    elif os.path.isfile(stored_path):
                        os.remove(stored_path)
                    return True, "Copied file removed successfully"
            except Exception as e:
                print(f"Warning: Could not delete file {stored_path}: {e}")
                return True, f"Attachment removed from database, but file deletion failed: {e}"
        
        return True, "Attachment removed successfully"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error removing attachment: {e}"
    finally:
        safe_close_connection(conn)


@retry_on_locked
def add_reminder(note_id: int, reminder_datetime: str, message: Optional[str] = None) -> Tuple[bool, str]:
    """Add a reminder for a note."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
        if not cursor.fetchone():
            return False, f"Note with ID {note_id} not found"
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO reminders (note_id, reminder_datetime, message, created_at)
            VALUES (?, ?, ?, ?)
        """, (note_id, reminder_datetime, message, current_time))
        
        conn.commit()
        return True, "Reminder added successfully"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error adding reminder: {e}"
    finally:
        safe_close_connection(conn)


def get_reminders(note_id: Optional[int] = None, include_completed: bool = False) -> List[Dict[str, Any]]:
    """Get reminders, optionally filtered by note_id."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        base_query = """
            SELECT r.id, r.note_id, n.title as note_title, r.reminder_datetime, 
                   r.message, r.is_completed, r.created_at
            FROM reminders r
            JOIN notes n ON r.note_id = n.id
        """
        
        conditions = []
        params = []
        
        if note_id:
            conditions.append("r.note_id = ?")
            params.append(note_id)
        
        if not include_completed:
            conditions.append("r.is_completed = 0")
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY r.reminder_datetime ASC"
        
        cursor.execute(base_query, params)
        reminders = [dict(row) for row in cursor.fetchall()]
        
        return reminders
    except Exception as e:
        print(f"Error getting reminders: {e}")
        return []
    finally:
        safe_close_connection(conn)


@retry_on_locked
def complete_reminder(reminder_id: int) -> Tuple[bool, str]:
    """Mark a reminder as completed."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE reminders SET is_completed = 1 WHERE id = ?", (reminder_id,))
        
        if cursor.rowcount == 0:
            return False, f"Reminder with ID {reminder_id} not found"
        
        conn.commit()
        return True, "Reminder marked as completed"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error completing reminder: {e}"
    finally:
        safe_close_connection(conn)


@retry_on_locked
def delete_reminder(reminder_id: int) -> Tuple[bool, str]:
    """Delete a reminder."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        
        if cursor.rowcount == 0:
            return False, f"Reminder with ID {reminder_id} not found"
        
        conn.commit()
        return True, "Reminder deleted successfully"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error deleting reminder: {e}"
    finally:
        safe_close_connection(conn)


def get_notes_statistics() -> Dict[str, Any]:
    """Get comprehensive statistics about notes."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total notes (including archived)
        cursor.execute("SELECT COUNT(*) FROM notes")
        stats['total_notes'] = cursor.fetchone()[0]
        
        # Active notes (not archived)
        cursor.execute("SELECT COUNT(*) FROM notes WHERE is_archived = 0")
        stats['active_notes'] = cursor.fetchone()[0]
        
        # Archived notes
        cursor.execute("SELECT COUNT(*) FROM notes WHERE is_archived = 1")
        stats['archived_notes'] = cursor.fetchone()[0]
        
        # Total tags
        cursor.execute("SELECT COUNT(*) FROM tags")
        stats['total_tags'] = cursor.fetchone()[0]
        
        # Total attachments
        cursor.execute("SELECT COUNT(*) FROM attachments")
        stats['total_attachments'] = cursor.fetchone()[0]
        
        # Total reminders
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE is_completed = 0")
        stats['active_reminders'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM reminders WHERE is_completed = 1")
        stats['completed_reminders'] = cursor.fetchone()[0]
        
        # Notes by tag (top 10)
        cursor.execute("""
            SELECT t.name, COUNT(nt.note_id) as count
            FROM tags t
            LEFT JOIN note_tags nt ON t.id = nt.tag_id
            GROUP BY t.id, t.name
            ORDER BY count DESC
            LIMIT 10
        """)
        stats['notes_by_tag'] = [dict(row) for row in cursor.fetchall()]
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM notes
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """)
        stats['recent_activity'] = [dict(row) for row in cursor.fetchall()]
        
        # Average content length
        cursor.execute("SELECT AVG(LENGTH(content)) FROM notes")
        avg_length = cursor.fetchone()[0]
        stats['avg_content_length'] = int(avg_length) if avg_length else 0
        
        # Oldest and newest notes
        cursor.execute("SELECT title, created_at FROM notes ORDER BY created_at ASC LIMIT 1")
        oldest = cursor.fetchone()
        stats['oldest_note'] = dict(oldest) if oldest else None
        
        cursor.execute("SELECT title, created_at FROM notes ORDER BY created_at DESC LIMIT 1")
        newest = cursor.fetchone()
        stats['newest_note'] = dict(newest) if newest else None
        
        # Files vs directories in attachments
        cursor.execute("SELECT is_directory, COUNT(*) as count FROM attachments GROUP BY is_directory")
        attachment_types = cursor.fetchall()
        stats['attachment_types'] = {'files': 0, 'directories': 0}
        for row in attachment_types:
            if row[0] == 0:
                stats['attachment_types']['files'] = row[1]
            else:
                stats['attachment_types']['directories'] = row[1]
        
        # Upcoming reminders (next 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM reminders 
            WHERE is_completed = 0 
            AND reminder_datetime BETWEEN datetime('now') AND datetime('now', '+7 days')
        """)
        stats['upcoming_reminders'] = cursor.fetchone()[0]
        
        # Total note links
        cursor.execute("SELECT COUNT(*) FROM note_links")
        stats['total_note_links'] = cursor.fetchone()[0]
        
        # Total templates
        cursor.execute("SELECT COUNT(*) FROM templates")
        stats['total_templates'] = cursor.fetchone()[0]
        
        return stats
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}
    finally:
        safe_close_connection(conn)


@retry_on_locked
def link_notes(source_id: int, target_id: int) -> Tuple[bool, str]:
    """Create a link between two notes."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if both notes exist
        cursor.execute("SELECT id FROM notes WHERE id IN (?, ?)", (source_id, target_id))
        if len(cursor.fetchall()) != 2:
            return False, "One or both notes not found"
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO note_links (source_note_id, target_note_id, created_at)
            VALUES (?, ?, ?)
        """, (source_id, target_id, current_time))
        
        conn.commit()
        return True, f"Note #{source_id} linked to note #{target_id}"
    except sqlite3.IntegrityError:
        return False, "Link already exists"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error creating link: {e}"
    finally:
        safe_close_connection(conn)


def get_linked_notes(note_id: int) -> List[Dict[str, Any]]:
    """Get all notes linked from a specific note."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT n.*, GROUP_CONCAT(t.name) as tags
            FROM notes n
            JOIN note_links nl ON n.id = nl.target_note_id
            LEFT JOIN note_tags nt ON n.id = nt.note_id
            LEFT JOIN tags tag ON nt.tag_id = tag.id
            WHERE nl.source_note_id = ?
            GROUP BY n.id
        """, (note_id,))
        
        notes = [dict(row) for row in cursor.fetchall()]
        
        # Process tags
        for note in notes:
            if note['tags']:
                note['tags'] = note['tags'].split(',')
            else:
                note['tags'] = []
        
        return notes
    except Exception as e:
        print(f"Error getting linked notes: {e}")
        return []
    finally:
        safe_close_connection(conn)


@retry_on_locked
def create_template(name: str, content: str, description: Optional[str] = None) -> Tuple[bool, str]:
    """Create a new note template."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO templates (name, content, description, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, content, description, current_time, current_time))
        
        conn.commit()
        return True, f"Template '{name}' created successfully"
    except sqlite3.IntegrityError:
        return False, f"Template '{name}' already exists"
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Error creating template: {e}"
    finally:
        safe_close_connection(conn)


def get_templates() -> List[Dict[str, Any]]:
    """Get all templates."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM templates ORDER BY name")
        templates = [dict(row) for row in cursor.fetchall()]
        
        return templates
    except Exception as e:
        print(f"Error getting templates: {e}")
        return []
    finally:
        safe_close_connection(conn)

