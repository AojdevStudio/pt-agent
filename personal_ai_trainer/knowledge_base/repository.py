"""
Repository for storing and retrieving knowledge base documents using Supabase.

Implements CRUD operations and similarity-based retrieval for research documents.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from personal_ai_trainer.database.connection import get_supabase_client
from personal_ai_trainer.database.models import KnowledgeBase
from personal_ai_trainer.knowledge_base.embeddings import cosine_similarity

import logging

logger = logging.getLogger(__name__)

TABLE_NAME = "knowledge_base"


def add_document(document: KnowledgeBase) -> Optional[str]:
    """
    Store a new document in the knowledge base.

    Args:
        document (KnowledgeBase): The document to store.

    Returns:
        Optional[str]: The document_id of the inserted document, or None if failed.
    """
    client = get_supabase_client()
    try:
        # Use model_dump(mode='json') for proper serialization, including dates
        data = document.model_dump(mode='json')
        response = client.table(TABLE_NAME).insert(data).execute()
        if response.data and len(response.data) > 0:
            return response.data[0].get("document_id")
        return None
    except Exception as e:
        # Log the full exception details
        logger.error(f"Failed to add document: {e}", exc_info=True)
        return None


def get_document(document_id: str) -> Optional[KnowledgeBase]:
    """
    Retrieve a document by its ID.

    Args:
        document_id (str): The document ID.

    Returns:
        Optional[KnowledgeBase]: The document if found, else None.
    """
    client = get_supabase_client()
    try:
        response = client.table(TABLE_NAME).select("*").eq("document_id", document_id).execute()
        if response.data and len(response.data) > 0:
            return KnowledgeBase(**response.data[0])
        return None
    except Exception as e:
        logger.error(f"Failed to get document: {e}")
        return None


def update_document(document_id: str, updates: Dict[str, Any]) -> bool:
    """
    Update fields of a document.

    Args:
        document_id (str): The document ID.
        updates (Dict[str, Any]): Fields to update.

    Returns:
        bool: True if update succeeded, False otherwise.
    """
    client = get_supabase_client()
    try:
        response = client.table(TABLE_NAME).update(updates).eq("document_id", document_id).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        logger.error(f"Failed to update document: {e}")
        return False


def delete_document(document_id: str) -> bool:
    """
    Delete a document from the knowledge base.

    Args:
        document_id (str): The document ID.

    Returns:
        bool: True if deletion succeeded, False otherwise.
    """
    client = get_supabase_client()
    try:
        response = client.table(TABLE_NAME).delete().eq("document_id", document_id).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        return False


def query_similar_documents(query_embedding: List[float], top_k: int = 5, min_score: float = 0.7) -> List[KnowledgeBase]:
    """
    Retrieve the most similar documents to a query embedding.

    Args:
        query_embedding (List[float]): The embedding to compare against.
        top_k (int): Number of top results to return.
        min_score (float): Minimum similarity score to include.

    Returns:
        List[KnowledgeBase]: List of similar documents, sorted by similarity.
    """
    client = get_supabase_client()
    try:
        # Fetch all embeddings and metadata (could be optimized with pgvector in production)
        response = client.table(TABLE_NAME).select("*").execute()
        docs = []
        scored = []
        for row in response.data:
            if "embedding" in row and row["embedding"]:
                score = cosine_similarity(query_embedding, row["embedding"])
                if score >= min_score:
                    scored.append((score, row))
        # Sort by similarity
        scored.sort(reverse=True, key=lambda x: x[0])
        for score, row in scored[:top_k]:
            docs.append(KnowledgeBase(**row))
        return docs
    except Exception as e:
        logger.error(f"Failed to query similar documents: {e}")
        return []