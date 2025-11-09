"""Command modules for WNote CLI."""

from .note_commands import add, show, edit, update, delete
from .tag_commands import tags, color
from .attachment_commands import attach, deattach
from .reminder_commands import reminder, reminders
from .export_commands import export, search, stats
from .config_commands import config
from .backup_commands import backup, restore, archive, list_archives

__all__ = [
    "add",
    "show",
    "edit",
    "update",
    "delete",
    "tags",
    "color",
    "attach",
    "deattach",
    "reminder",
    "reminders",
    "export",
    "search",
    "stats",
    "config",
    "backup",
    "restore",
    "archive",
    "list_archives",
]

