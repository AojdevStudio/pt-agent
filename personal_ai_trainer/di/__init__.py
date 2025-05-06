"""
Dependency Injection package for the Personal AI Trainer application.

This package provides a lightweight dependency injection framework for managing
service dependencies throughout the application.
"""

from personal_ai_trainer.di.container import DIContainer
from personal_ai_trainer.di.provider import (
    configure_services,
    get_container,
    reset_container,
    get_supabase_client,
    get_openai_client
)

__all__ = [
    'DIContainer',
    'configure_services',
    'get_container',
    'reset_container',
    'get_supabase_client',
    'get_openai_client'
]