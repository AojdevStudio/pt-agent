"""
Service Provider for the Personal AI Trainer application.

This module configures and registers all services with the dependency injection container.
It serves as the central configuration point for the application's dependencies.
"""

from personal_ai_trainer.di.container import DIContainer
from personal_ai_trainer.agents.research_agent.agent import ResearchAgent
# Removed BiometricAgent import to break circular dependency
from personal_ai_trainer.agents.biometric_agent.oura_client import OuraClientWrapper
from personal_ai_trainer.agents.orchestrator_agent.agent import OrchestratorAgent
from personal_ai_trainer.knowledge_base.embeddings import get_embedding
from personal_ai_trainer.exceptions import ConfigurationError

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_supabase_client():
    """
    Factory function to create a Supabase client.
    
    Returns:
        The Supabase client instance.
        
    Raises:
        ConfigurationError: If required environment variables are missing.
    """
    from personal_ai_trainer.database.connection import get_supabase_client as get_client
    try:
        return get_client()
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        raise ConfigurationError(f"Failed to create Supabase client: {e}") from e


def get_openai_client():
    """
    Factory function to create an OpenAI client.
    
    Returns:
        The OpenAI client instance.
        
    Raises:
        ConfigurationError: If required environment variables are missing.
    """
    from openai import OpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ConfigurationError("OPENAI_API_KEY not found in environment variables")
        
    return OpenAI(api_key=api_key)


# Factory function for BiometricAgent to handle import internally
def create_biometric_agent(container: DIContainer, user_id: Optional[str]):
    """Factory function to create a BiometricAgent instance."""
    # Import locally to avoid circular dependency at module level
    from personal_ai_trainer.agents.biometric_agent.agent import BiometricAgent
    return BiometricAgent(
        oura_client=container.resolve(OuraClientWrapper),
        supabase_client=container.resolve('supabase_client'),
        user_id=user_id
    )

def configure_services(user_id: Optional[str] = None) -> DIContainer:
    """
    Configure and register all services with the DI container.
    
    Args:
        user_id (Optional[str]): Optional user ID to associate with agents.
            
    Returns:
        DIContainer: The configured container.
        
    Example:
        ```python
        container = configure_services(user_id="user123")
        research_agent = container.resolve(ResearchAgent)
        ```
    """
    container = DIContainer()
    
    # Register external clients and services
    container.register('supabase_client', get_supabase_client)
    container.register('openai_client', get_openai_client)
    container.register(OuraClientWrapper, OuraClientWrapper)
    
    # Register embedding function
    container.register('get_embedding', get_embedding)
    
    # Register agents
    container.register(ResearchAgent, lambda c: ResearchAgent(
        supabase_client=c.resolve('supabase_client'),
        name="ResearchAgent"
    ))
    
    # Register BiometricAgent using the factory function
    container.register('BiometricAgent', lambda c: create_biometric_agent(c, user_id))
    
    container.register(OrchestratorAgent, lambda c: OrchestratorAgent(
        research_agent=c.resolve(ResearchAgent),
        biometric_agent=c.resolve('BiometricAgent'), # Still resolve using string key
        supabase_client=c.resolve('supabase_client'),
        user_id=user_id
    ))
    
    return container


# Global container instance for singleton access pattern
_container = None


def get_container(user_id: Optional[str] = None) -> DIContainer:
    """
    Get the global container instance, creating it if necessary.
    
    Args:
        user_id (Optional[str]): Optional user ID to associate with agents.
            
    Returns:
        DIContainer: The global container instance.
        
    Example:
        ```python
        container = get_container(user_id="user123")
        research_agent = container.resolve(ResearchAgent)
        ```
    """
    global _container
    if _container is None:
        _container = configure_services(user_id)
    return _container


def reset_container() -> None:
    """
    Reset the global container instance.
    
    This is useful for testing or when you need to reconfigure the container.
    
    Example:
        ```python
        reset_container()  # Container will be recreated on next get_container call
        ```
    """
    global _container
    _container = None