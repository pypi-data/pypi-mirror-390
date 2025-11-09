"""File operations utilities for WNote."""

import os
import sqlite3
import subprocess
from typing import Dict, Any
from rich.console import Console

from ..core.config import CONFIG_DIR, DB_PATH, get_config

console = Console()


def open_attachment(attachment: Dict[str, Any]) -> bool:
    """Open a file or directory attachment."""
    file_path = attachment['stored_path']
    
    if not os.path.exists(file_path):
        console.print(f"[bold red]Attachment not found: {file_path}[/bold red]")
        return False
    
    try:
        config = get_config()
        subprocess.run([config['file_opener'], file_path], check=False)
        return True
    except Exception as e:
        console.print(f"[bold red]Error opening attachment: {e}[/bold red]")
        return False


def cleanup_stale_connections() -> None:
    """Clean up any stale database connections."""
    wal_file = DB_PATH + "-wal"
    shm_file = DB_PATH + "-shm"
    journal_file = DB_PATH + "-journal"
    lock_file = os.path.join(CONFIG_DIR, "notes.lock")
    
    for file in [wal_file, shm_file, journal_file, lock_file]:
        if os.path.exists(file):
            try:
                os.remove(file)
            except Exception:
                pass
    
    # Try to vacuum the database
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=1.0)
        conn.execute("VACUUM")
    except Exception:
        pass
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

