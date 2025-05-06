"""
Embedding utilities for the Knowledge Base component.

Provides functions to generate vector embeddings from text using OpenAI,
calculate similarity between embeddings, and handle errors/retries.
"""

from typing import List, Optional, Union, Dict, Any
import numpy as np
import logging
import os

from personal_ai_trainer.exceptions import EmbeddingError
from personal_ai_trainer.agents.openai_integration import get_embedding as openai_get_embedding
from personal_ai_trainer.agents.openai_integration import get_embeddings as openai_get_embeddings
from personal_ai_trainer.utils.error_handling import with_error_handling

logger = logging.getLogger(__name__)

# Default model settings
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-ada-002")


@with_error_handling(error_types=(Exception,), retry_count=2, retry_delay=1.0)
def get_embedding(
    text: str,
    model: str = OPENAI_EMBEDDING_MODEL
) -> List[float]:
    """
    Generate a vector embedding for the given text using OpenAI's embedding API.
    
    Args:
        text (str): The input text to embed. Should be cleaned and preprocessed.
        model (str): The OpenAI embedding model to use. Defaults to the value of
            OPENAI_EMBEDDING_MODEL environment variable or "text-embedding-ada-002".
            
    Returns:
        List[float]: The embedding vector as a list of floating-point numbers.
            
    Raises:
        EmbeddingError: If the OpenAI API call fails after retries.
        
    Example:
        ```python
        embedding = get_embedding("Running is good for cardiovascular health")
        # Returns: [0.123, 0.456, ...]
        ```
    """
    try:
        # Use the centralized embedding function from openai_integration
        return openai_get_embedding(text, model)
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise EmbeddingError(f"Failed to generate embedding: {e}") from e


@with_error_handling(error_types=(Exception,), retry_count=2, retry_delay=1.0)
def get_embeddings(
    texts: List[str],
    model: str = OPENAI_EMBEDDING_MODEL
) -> List[List[float]]:
    """
    Generate vector embeddings for multiple texts using OpenAI's embedding API.
    
    This is more efficient than calling get_embedding multiple times for batch processing.
    
    Args:
        texts (List[str]): The input texts to embed. Should be cleaned and preprocessed.
        model (str): The OpenAI embedding model to use. Defaults to the value of
            OPENAI_EMBEDDING_MODEL environment variable or "text-embedding-ada-002".
            
    Returns:
        List[List[float]]: List of embedding vectors, one for each input text.
            
    Raises:
        EmbeddingError: If the OpenAI API call fails after retries.
        
    Example:
        ```python
        embeddings = get_embeddings(["Running is good", "Swimming is also good"])
        # Returns: [[0.123, 0.456, ...], [0.789, 0.321, ...]]
        ```
    """
    try:
        # Use the centralized embeddings function from openai_integration
        return openai_get_embeddings(texts, model)
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise EmbeddingError(f"Failed to generate embeddings: {e}") from e


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate the cosine similarity between two embedding vectors.
    
    Cosine similarity measures the cosine of the angle between two vectors,
    providing a similarity score between -1 and 1, where 1 means identical,
    0 means orthogonal, and -1 means opposite.
    
    Args:
        vec1 (List[float]): First embedding vector.
        vec2 (List[float]): Second embedding vector.
            
    Returns:
        float: Cosine similarity score between -1 and 1.
            
    Example:
        ```python
        similarity = cosine_similarity([0.1, 0.2, 0.3], [0.2, 0.3, 0.4])
        # Returns: 0.9914
        ```
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    # Handle zero vectors to avoid division by zero
    if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
        return 0.0
        
    return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


def batch_cosine_similarity(
    query_embedding: List[float],
    document_embeddings: List[List[float]]
) -> List[float]:
    """
    Calculate cosine similarity between a query embedding and multiple document embeddings.
    
    This is more efficient than calling cosine_similarity in a loop.
    
    Args:
        query_embedding (List[float]): The query embedding vector.
        document_embeddings (List[List[float]]): List of document embedding vectors.
            
    Returns:
        List[float]: List of similarity scores, one for each document embedding.
            
    Example:
        ```python
        query_emb = get_embedding("running")
        doc_embs = get_embeddings(["jogging", "swimming", "cycling"])
        similarities = batch_cosine_similarity(query_emb, doc_embs)
        # Returns: [0.92, 0.45, 0.38]
        ```
    """
    query_vec = np.array(query_embedding)
    doc_vecs = np.array(document_embeddings)
    
    # Calculate query norm
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return [0.0] * len(document_embeddings)
    
    # Calculate document norms
    doc_norms = np.linalg.norm(doc_vecs, axis=1)
    
    # Replace zero norms with 1 to avoid division by zero
    doc_norms = np.where(doc_norms == 0, 1.0, doc_norms)
    
    # Calculate dot products
    dot_products = np.dot(doc_vecs, query_vec)
    
    # Calculate similarities
    similarities = dot_products / (doc_norms * query_norm)
    
    return similarities.tolist()