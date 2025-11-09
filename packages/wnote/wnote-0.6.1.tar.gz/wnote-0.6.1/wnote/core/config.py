"""Configuration management for WNote."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/wnote")
DB_PATH = os.path.join(CONFIG_DIR, "notes.db")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
ATTACHMENTS_DIR = os.path.join(CONFIG_DIR, "attachments")
BACKUP_DIR = os.path.join(CONFIG_DIR, "backups")
TEMPLATES_DIR = os.path.join(CONFIG_DIR, "templates")
ARCHIVE_DIR = os.path.join(CONFIG_DIR, "archive")

# Create necessary directories
for directory in [CONFIG_DIR, ATTACHMENTS_DIR, BACKUP_DIR, TEMPLATES_DIR, ARCHIVE_DIR]:
    os.makedirs(directory, exist_ok=True)

DEFAULT_CONFIG: Dict[str, Any] = {
    "editor": os.environ.get("EDITOR", "nano"),
    "default_color": "white",
    "file_opener": "xdg-open",  # xdg-open for Linux, "open" for macOS, "start" for Windows
    "auto_backup": True,
    "backup_interval_days": 7,
    "max_backups": 10,
    "search_limit": 100,
    "preview_length": 40,
    "date_format": "%d/%m/%Y %H:%M",
    "tag_colors": {
        "work": "blue",
        "personal": "green",
        "urgent": "red",
        "idea": "yellow",
        "task": "cyan",
        "file": "bright_blue",
        "folder": "bright_yellow",
        "archived": "bright_black",
    }
}

# Global config instance
_config: Optional[Dict[str, Any]] = None


def load_config() -> Dict[str, Any]:
    """Load or create configuration file."""
    global _config
    
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        _config = DEFAULT_CONFIG.copy()
        return _config
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            loaded_config = json.load(f)
        
        # Merge with defaults to ensure all keys exist
        config = DEFAULT_CONFIG.copy()
        config.update(loaded_config)
        
        # Ensure tag_colors is updated properly
        if "tag_colors" in loaded_config:
            config["tag_colors"].update(loaded_config["tag_colors"])
        
        _config = config
        return config
    except Exception as e:
        print(f"Error loading config: {e}. Using default configuration.")
        _config = DEFAULT_CONFIG.copy()
        return _config


def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file."""
    global _config
    
    # Create a serializable copy of the config
    serializable_config = {}
    for key, value in config.items():
        if key == 'tag_colors':
            serializable_config[key] = dict(value)
        elif isinstance(value, (str, int, float, bool, list, dict)) or value is None:
            serializable_config[key] = value
    
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(serializable_config, f, indent=2)
        _config = config
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        # Try backup location
        backup_path = os.path.join(CONFIG_DIR, "config.backup.json")
        try:
            with open(backup_path, 'w') as f:
                json.dump(serializable_config, f, indent=2)
            print(f"Config saved to backup location: {backup_path}")
            return True
        except Exception:
            return False


def get_config() -> Dict[str, Any]:
    """Get the current configuration."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def update_config(key: str, value: Any) -> bool:
    """Update a specific configuration value."""
    config = get_config()
    config[key] = value
    return save_config(config)


def reset_config() -> bool:
    """Reset configuration to defaults."""
    return save_config(DEFAULT_CONFIG.copy())

