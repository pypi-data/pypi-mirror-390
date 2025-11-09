"""Formatting utilities for WNote."""

import datetime
from typing import Dict, Any


def format_datetime(dt_str: str, format_string: str = "%d/%m/%Y %H:%M") -> str:
    """Format datetime string for display."""
    try:
        # Try to parse as standard datetime format first
        dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Fallback to ISO format
            dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            # If all fails, try without timezone
            dt = datetime.datetime.fromisoformat(dt_str)
    
    return dt.strftime(format_string)


def get_tag_color(tag: str, config: Dict[str, Any]) -> str:
    """Get color for a tag, use default if not specified."""
    return config['tag_colors'].get(tag, config['default_color'])


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def truncate_text(text: str, max_length: int = 40, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    text = text.replace('\n', ' ')
    if len(text) > max_length:
        return text[:max_length - len(suffix)] + suffix
    return text

