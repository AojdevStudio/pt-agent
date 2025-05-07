"""
Repository for storing and retrieving user profiles using Supabase.
"""

import logging
from typing import Optional, List, Any, Dict

from personal_ai_trainer.database.connection import get_supabase_client
from personal_ai_trainer.database.models import UserProfile
from personal_ai_trainer.config.config import get_config_dir
import json
from pathlib import Path

logger = logging.getLogger(__name__)

TABLE_NAME = "user_profiles"
_LOCAL_FILE = get_config_dir() / "profiles.json"

def _load_local_profiles() -> list[dict]:
    """Load user profiles from local JSON fallback."""
    try:
        _LOCAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        if _LOCAL_FILE.exists():
            with open(_LOCAL_FILE, "r") as f:
                return json.load(f) or []
    except Exception:
        pass
    return []

def _save_local_profiles(profiles: list[dict]) -> None:
    """Save user profiles to local JSON fallback."""
    try:
        _LOCAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_LOCAL_FILE, "w") as f:
            json.dump(profiles, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save local profiles: {e}", exc_info=True)

def add_user_profile(profile: UserProfile) -> Optional[str]:
    """
    Add a new user profile to the database.

    Returns:
        Optional[str]: The user_id of the inserted profile, or None if failed.
    """
    # Try Supabase first
    try:
        client = get_supabase_client()
        data = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()
        response = client.table(TABLE_NAME).insert(data).execute()
        if response.data and len(response.data) > 0:
            return profile.user_id
    except Exception as e:
        logger.warning(f"Supabase unavailable, saving profile locally: {e}")
    # Fallback to local storage
    try:
        profiles = _load_local_profiles()
        data = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()
        profiles.append(data)
        _save_local_profiles(profiles)
        return profile.user_id
    except Exception as e:
        logger.error(f"Failed to add user profile locally: {e}", exc_info=True)
        return None

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """
    Retrieve a user profile by user_id.

    Returns:
        Optional[UserProfile]: The profile if found, else None.
    """
    # Try Supabase first
    try:
        client = get_supabase_client()
        response = client.table(TABLE_NAME).select("*").eq("user_id", user_id).execute()
        if response.data and len(response.data) > 0:
            return UserProfile(**response.data[0])
    except Exception as e:
        logger.warning(f"Supabase unavailable, loading profile locally: {e}")
    # Fallback to local storage
    try:
        for row in _load_local_profiles():
            if row.get("user_id") == user_id:
                return UserProfile(**row)
    except Exception as e:
        logger.error(f"Failed to load user profile locally: {e}", exc_info=True)
    return None

def update_user_profile(user_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update fields of an existing user profile.

    Returns:
        bool: True if update succeeded, False otherwise.
    """
    # Try Supabase first
    try:
        client = get_supabase_client()
        response = client.table(TABLE_NAME).update(updates).eq("user_id", user_id).execute()
        if response.data is not None and len(response.data) > 0:
            return True
    except Exception as e:
        logger.warning(f"Supabase unavailable, updating profile locally: {e}")
    # Fallback to local storage
    try:
        profiles = _load_local_profiles()
        updated = False
        for idx, row in enumerate(profiles):
            if row.get("user_id") == user_id:
                profiles[idx] = {**row, **updates}
                updated = True
                break
        if updated:
            _save_local_profiles(profiles)
            return True
    except Exception as e:
        logger.error(f"Failed to update user profile locally: {e}", exc_info=True)
    return False

def delete_user_profile(user_id: str) -> bool:
    """
    Delete a user profile by user_id.

    Returns:
        bool: True if deletion succeeded, False otherwise.
    """
    # Try Supabase first
    try:
        client = get_supabase_client()
        response = client.table(TABLE_NAME).delete().eq("user_id", user_id).execute()
        if response.data is not None and len(response.data) > 0:
            return True
    except Exception as e:
        logger.warning(f"Supabase unavailable, deleting profile locally: {e}")
    # Fallback to local storage
    try:
        profiles = _load_local_profiles()
        new_profiles = [row for row in profiles if row.get("user_id") != user_id]
        if len(new_profiles) < len(profiles):
            _save_local_profiles(new_profiles)
            return True
    except Exception as e:
        logger.error(f"Failed to delete user profile locally: {e}", exc_info=True)
    return False

def list_user_profiles() -> List[UserProfile]:
    """
    List all user profiles.

    Returns:
        List[UserProfile]: List of user profiles.
    """
    # Try Supabase first
    try:
        client = get_supabase_client()
        response = client.table(TABLE_NAME).select("*").execute()
        return [UserProfile(**row) for row in (response.data or [])]
    except Exception as e:
        logger.warning(f"Supabase unavailable, listing profiles locally: {e}")
    # Fallback to local storage
    profiles: List[UserProfile] = []
    try:
        for row in _load_local_profiles():
            profiles.append(UserProfile(**row))
    except Exception as e:
        logger.error(f"Failed to list user profiles locally: {e}", exc_info=True)
    return profiles