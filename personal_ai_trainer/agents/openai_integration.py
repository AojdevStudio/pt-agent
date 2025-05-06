"""
OpenAI integration utilities for Personal AI Training Agent.

Handles API key setup, provides utility functions for OpenAI model interaction,
and includes error handling and retry logic.
"""

import os
import logging
from typing import Any, Dict, Optional, List

from openai import OpenAI

from personal_ai_trainer.exceptions import OpenAIAPIError, ConfigurationError
from personal_ai_trainer.utils.error_handling import with_error_handling

logger = logging.getLogger(__name__)

# Default model settings
DEFAULT_CHAT_MODEL = "gpt-4o"
DEFAULT_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")


def get_openai_api_key() -> str:
    """
    Retrieve the OpenAI API key from environment variables.
    
    Returns:
        str: The OpenAI API key.
        
    Raises:
        ConfigurationError: If the API key is not found.
        
    Example:
        ```python
        api_key = get_openai_api_key()
        ```
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY not found in environment variables")
        raise ConfigurationError("OPENAI_API_KEY not found in environment variables")
    return api_key


def get_openai_client() -> OpenAI:
    """
    Create and return an OpenAI client using the API key from environment.
    
    Returns:
        OpenAI: The OpenAI client instance.
        
    Raises:
        ConfigurationError: If the API key is not found.
        
    Example:
        ```python
        client = get_openai_client()
        response = client.chat.completions.create(...)
        ```
    """
    api_key = get_openai_api_key()
    return OpenAI(api_key=api_key)


@with_error_handling(error_types=(Exception,), retry_count=3, retry_delay=2.0)
def openai_chat_completion(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_CHAT_MODEL,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
    **kwargs: Any
) -> str:
    """
    Call the OpenAI chat completion API with retry logic.
    
    Args:
        messages (List[Dict[str, str]]): List of message dicts for the chat.
            Each message should have 'role' and 'content' keys.
        model (str): Model name. Defaults to DEFAULT_CHAT_MODEL.
        max_tokens (Optional[int]): Max tokens for the response. Defaults to None.
        temperature (float): Sampling temperature. Defaults to 0.7.
        **kwargs: Additional parameters for the API.
        
    Returns:
        str: The generated response text.
        
    Raises:
        OpenAIAPIError: If the API call fails after retries.
        
    Example:
        ```python
        response = openai_chat_completion([
            {"role": "system", "content": "You are a fitness expert."},
            {"role": "user", "content": "What's a good workout routine?"}
        ])
        ```
    """
    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise OpenAIAPIError(f"OpenAI API call failed: {e}") from e


@with_error_handling(error_types=(Exception,), retry_count=3, retry_delay=2.0)
def openai_chat_completion_json(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_CHAT_MODEL,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Call the OpenAI chat completion API and parse the response as JSON.
    
    Args:
        messages (List[Dict[str, str]]): List of message dicts for the chat.
            Each message should have 'role' and 'content' keys.
        model (str): Model name. Defaults to DEFAULT_CHAT_MODEL.
        max_tokens (Optional[int]): Max tokens for the response. Defaults to None.
        temperature (float): Sampling temperature. Defaults to 0.7.
        **kwargs: Additional parameters for the API.
        
    Returns:
        Dict[str, Any]: The parsed JSON response.
        
    Raises:
        OpenAIAPIError: If the API call fails after retries or JSON parsing fails.
        
    Example:
        ```python
        response_json = openai_chat_completion_json([
            {"role": "system", "content": "You are a fitness expert. Respond in JSON format."},
            {"role": "user", "content": "Give me a workout plan for the week."}
        ])
        ```
    """
    import json
    
    # Add instruction to respond in JSON format if not already present
    system_message_found = False
    for message in messages:
        if message.get("role") == "system":
            system_message_found = True
            if "JSON" not in message.get("content", ""):
                message["content"] += " Respond in valid JSON format."
            break
    
    if not system_message_found:
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful assistant. Respond in valid JSON format."
        })
    
    # Set response format to JSON
    kwargs["response_format"] = {"type": "json_object"}
    
    # Get the response
    response_text = openai_chat_completion(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        **kwargs
    )
    
    # Parse the response as JSON
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        logger.debug(f"Response text: {response_text}")
        raise OpenAIAPIError(f"Failed to parse OpenAI response as JSON: {e}") from e


@with_error_handling(error_types=(Exception,), retry_count=3, retry_delay=2.0)
def get_embedding(text: str, model: str = DEFAULT_EMBEDDING_MODEL) -> List[float]:
    """
    Generate a vector embedding for the given text using OpenAI's embedding API.
    
    Args:
        text (str): The input text to embed.
        model (str): The OpenAI embedding model to use. Defaults to DEFAULT_EMBEDDING_MODEL.
        
    Returns:
        List[float]: The embedding vector.
        
    Raises:
        OpenAIAPIError: If the OpenAI API call fails after retries.
        
    Example:
        ```python
        embedding = get_embedding("Running is good for cardiovascular health")
        ```
    """
    client = get_openai_client()
    try:
        response = client.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"OpenAI API error generating embedding: {e}")
        raise OpenAIAPIError(f"Failed to generate embedding: {e}") from e


@with_error_handling(error_types=(Exception,), retry_count=3, retry_delay=2.0)
def get_embeddings(texts: List[str], model: str = DEFAULT_EMBEDDING_MODEL) -> List[List[float]]:
    """
    Generate vector embeddings for multiple texts using OpenAI's embedding API.
    
    Args:
        texts (List[str]): The input texts to embed.
        model (str): The OpenAI embedding model to use. Defaults to DEFAULT_EMBEDDING_MODEL.
        
    Returns:
        List[List[float]]: The embedding vectors.
        
    Raises:
        OpenAIAPIError: If the OpenAI API call fails after retries.
        
    Example:
        ```python
        embeddings = get_embeddings(["Running is good", "Swimming is also good"])
        ```
    """
    client = get_openai_client()
    try:
        response = client.embeddings.create(
            input=texts,
            model=model
        )
        # Sort by index to ensure order matches input
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]
    except Exception as e:
        logger.error(f"OpenAI API error generating embeddings: {e}")
        raise OpenAIAPIError(f"Failed to generate embeddings: {e}") from e