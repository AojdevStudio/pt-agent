"""
Error handling utilities for the Personal AI Trainer application.

This module provides decorators and utility functions for consistent error handling,
retry logic, and error conversion throughout the application.
"""

import logging
import functools
import time
from typing import Callable, TypeVar, Any, Optional, Tuple, Union

from personal_ai_trainer.exceptions import (
    PersonalAITrainerError, 
    APIError, 
    OpenAIAPIError, 
    OuraAPIError
)

# Type variable for generic function return type
T = TypeVar('T')

# Configure logger
logger = logging.getLogger(__name__)


def with_error_handling(
    error_types: Tuple[type, ...] = (Exception,),
    retry_count: int = 0,
    retry_delay: float = 1.0,
    fallback_value: Optional[Any] = None,
    log_level: int = logging.ERROR
) -> Callable:
    """
    Decorator for handling errors with optional retry logic and fallback value.
    
    Args:
        error_types (Tuple[type, ...]): Exception types to catch. Defaults to (Exception,).
        retry_count (int): Number of retries before giving up. Defaults to 0.
        retry_delay (float): Delay between retries in seconds. Defaults to 1.0.
        fallback_value (Optional[Any]): Value to return if all retries fail. Defaults to None.
        log_level (int): Logging level for errors. Defaults to logging.ERROR.
        
    Returns:
        Callable: Decorated function with error handling.
        
    Example:
        ```python
        @with_error_handling(error_types=(ValueError, TypeError), retry_count=3)
        def parse_data(data):
            # Function implementation
            return processed_data
        ```
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                except error_types as e:
                    last_exception = e
                    logger.log(
                        log_level, 
                        f"Error in {func.__name__}: {e} (Attempt {attempt+1}/{retry_count+1})"
                    )
                    
                    if attempt < retry_count:
                        # Wait before retrying
                        time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        # All retries failed
                        if fallback_value is not None:
                            logger.log(log_level, f"Using fallback value for {func.__name__}")
                            return fallback_value
                        
                        # Convert to our custom exception hierarchy if appropriate
                        if isinstance(e, APIError):
                            # Already a custom exception, just re-raise
                            raise
                        elif hasattr(e, 'api_error') or 'openai' in str(e).lower():
                            # OpenAI style error
                            raise OpenAIAPIError(f"OpenAI API error: {e}") from e
                        elif 'oura' in str(e).lower():
                            # Oura API error
                            raise OuraAPIError(f"Oura API error: {e}") from e
                        else:
                            # Generic error
                            raise PersonalAITrainerError(f"Error in {func.__name__}: {e}") from e
            
            # This should never be reached due to the raise in the else clause
            raise last_exception
            
        return wrapper
    return decorator


def log_execution_time(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to log the execution time of a function.
    
    Args:
        func (Callable[..., T]): The function to decorate.
        
    Returns:
        Callable[..., T]: The decorated function.
        
    Example:
        ```python
        @log_execution_time
        def process_data(data):
            # Function implementation
            return processed_data
        ```
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.debug(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper


def safe_execute(
    func: Callable[..., T], 
    *args, 
    default: Any = None, 
    log_error: bool = True, 
    **kwargs
) -> Union[T, Any]:
    """
    Safely execute a function and return a default value if it fails.
    
    Args:
        func (Callable[..., T]): The function to execute.
        *args: Positional arguments to pass to the function.
        default (Any): Default value to return if the function fails. Defaults to None.
        log_error (bool): Whether to log the error. Defaults to True.
        **kwargs: Keyword arguments to pass to the function.
        
    Returns:
        Union[T, Any]: The function result or the default value if it fails.
        
    Example:
        ```python
        result = safe_execute(parse_json, data, default={}, log_error=True)
        ```
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error executing {func.__name__}: {e}")
        return default