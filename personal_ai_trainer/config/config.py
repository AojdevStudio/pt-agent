"""
Configuration loader for environment variables.

This module provides functions to retrieve database configuration values
for connecting to Supabase.
"""

import os


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