"""
Configuration loader for environment variables.

This module provides functions to retrieve database configuration values
for connecting to Supabase.
"""

import os
import json
from pathlib import Path
from typing import Optional


def get_supabase_url() -> str:
    """
    Retrieve the Supabase project URL from environment variables.

    Returns:
        str: The Supabase project URL.

    Raises:
        EnvironmentError: If the SUPABASE_URL variable is not set.
    """
    url = os.getenv("SUPABASE_URL")
    if not url:
        raise EnvironmentError("SUPABASE_URL environment variable is not set.")
    return url


def get_supabase_key() -> str:
    """
    Retrieve the Supabase service key from environment variables.

    Returns:
        str: The Supabase service key.

    Raises:
        EnvironmentError: If the SUPABASE_KEY variable is not set.
    """
    key = os.getenv("SUPABASE_KEY")
    if not key:
        raise EnvironmentError("SUPABASE_KEY environment variable is not set.")
    return key

# User configuration for default user profile
CONFIG_DIR_ENV = "PT_AGENT_CONFIG_DIR"
CONFIG_FILE_NAME = "config.json"

def get_config_dir() -> Path:
    """Get directory for storing user configuration. """
    dir_path = os.getenv(CONFIG_DIR_ENV)
    if not dir_path:
        dir_path = "~/.pt-agent"
    return Path(dir_path).expanduser()

def ensure_config_dir() -> Path:
    """Ensure the configuration directory exists. """
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def get_config_file_path() -> Path:
    """Get path to the configuration file. """
    return ensure_config_dir() / CONFIG_FILE_NAME

def load_config() -> dict:
    """Load configuration from file. """
    config_path = get_config_file_path()
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config: dict) -> None:
    """Save configuration to file. """
    config_path = get_config_file_path()
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

def get_default_user_id() -> Optional[str]:
    """Retrieve the default user ID from config."""
    config = load_config()
    return config.get("default_user_id")

def set_default_user_id(user_id: str) -> None:
    """Set the default user ID in config."""
    config = load_config()
    config["default_user_id"] = user_id
    save_config(config)