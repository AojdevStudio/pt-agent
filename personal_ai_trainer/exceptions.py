"""
Custom exceptions for the Personal AI Trainer application.

This module defines a hierarchy of custom exceptions used throughout the application
to provide more specific error handling and better error messages.
"""

class PersonalAITrainerError(Exception):
    """Base exception for all personal_ai_trainer errors."""
    pass


class ConfigurationError(PersonalAITrainerError):
    """
    Raised when there is a configuration issue.
    
    This could be due to missing environment variables, invalid configuration values,
    or other configuration-related issues.
    """
    pass


class APIError(PersonalAITrainerError):
    """
    Base class for API-related errors.
    
    This is the parent class for all errors related to external API calls.
    """
    pass


class OuraAPIError(APIError):
    """
    Raised when there is an error with the Oura API.
    
    This could be due to authentication issues, rate limiting, or other API-specific errors.
    """
    pass


class OpenAIAPIError(APIError):
    """
    Raised when there is an error with the OpenAI API.
    
    This could be due to authentication issues, rate limiting, invalid requests,
    or other OpenAI API-specific errors.
    """
    pass


class DatabaseError(PersonalAITrainerError):
    """
    Base class for database-related errors.
    
    This is the parent class for all errors related to database operations.
    """
    pass


class KnowledgeBaseError(PersonalAITrainerError):
    """
    Base class for knowledge base errors.
    
    This is the parent class for all errors related to the knowledge base operations.
    """
    pass


class EmbeddingError(KnowledgeBaseError):
    """
    Raised when there is an error generating embeddings.
    
    This could be due to issues with the embedding model, invalid input text,
    or other embedding-specific errors.
    """
    pass


class QueryError(KnowledgeBaseError):
    """
    Raised when there is an error querying the knowledge base.
    
    This could be due to invalid query parameters, database connection issues,
    or other query-specific errors.
    """
    pass


class AgentError(PersonalAITrainerError):
    """
    Base class for agent-related errors.
    
    This is the parent class for all errors related to agent operations.
    """
    pass


class WorkoutGenerationError(AgentError):
    """
    Raised when there is an error generating a workout plan.
    
    This could be due to invalid user preferences, missing research insights,
    or other workout generation-specific errors.
    """
    pass