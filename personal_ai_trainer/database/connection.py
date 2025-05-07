"""
Supabase database connection utility.

This module provides functions to initialize and retrieve the Supabase client,
with error handling for connection issues.
"""

from typing import Optional
try:
    from supabase import create_client, Client
except ImportError:
    create_client = None  # type: ignore
    Client = None  # type: ignore
from personal_ai_trainer.config.config import get_supabase_url, get_supabase_key

_supabase_client: Optional[Client] = None


def init_supabase_client() -> Client:
    """
    Initialize the Supabase client using configuration from environment variables.

    Returns:
        Client: The initialized Supabase client.

    Raises:
        RuntimeError: If the client cannot be initialized.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    if create_client is None:
        raise RuntimeError("Supabase client library is not installed.")
    try:
        url = get_supabase_url()
        key = get_supabase_key()
        _supabase_client = create_client(url, key)
        return _supabase_client
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Supabase client: {e}")


def get_supabase_client() -> Client:
    """
    Retrieve the current Supabase client instance, initializing if necessary.

    Returns:
        Client: The Supabase client instance.

    Raises:
        RuntimeError: If the client cannot be initialized.
    """
    if _supabase_client is not None:
        return _supabase_client
    return init_supabase_client()