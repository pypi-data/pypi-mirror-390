"""Decorators for WNote."""

import sqlite3
import time
import os
import functools
from typing import Callable, Any

from ..core.config import CONFIG_DIR, DB_PATH


def retry_on_locked(fn: Callable) -> Callable:
    """Decorator to retry database operations when database is locked."""
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        retries = 3
        for i in range(retries):
            try:
                return fn(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    # Check for stale lock file
                    lock_file = os.path.join(CONFIG_DIR, "notes.lock")
                    if os.path.exists(lock_file):
                        if time.time() - os.path.getmtime(lock_file) > 5:
                            os.remove(lock_file)
                    
                    time.sleep(0.2)
                    
                    # On last retry, try to vacuum
                    if i == retries - 1:
                        try:
                            temp_conn = sqlite3.connect(DB_PATH, timeout=1.0)
                            temp_conn.execute("PRAGMA locking_mode = EXCLUSIVE")
                            temp_conn.execute("VACUUM")
                            temp_conn.close()
                        except Exception:
                            pass
                else:
                    raise
        raise sqlite3.OperationalError("database is locked (after retries)")
    return wrapper

