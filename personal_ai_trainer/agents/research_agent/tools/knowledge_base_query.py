"""
Tool for querying the knowledge base for relevant research documents.

This module provides functionality to:
- Convert text queries to vector embeddings
- Search for semantically similar documents in the knowledge base
- Return relevant research documents for further processing
"""

from typing import List, Dict, Any, Optional, Union
import logging

from personal_ai_trainer.knowledge_base import repository as kb_repo
from personal_ai_trainer.knowledge_base.embeddings import get_embedding
from personal_ai_trainer.exceptions import QueryError, EmbeddingError
from personal_ai_trainer.utils.error_handling import with_error_handling

logger = logging.getLogger(__name__)

class KnowledgeBaseQueryTool:
    """
    Tool to retrieve research documents from the knowledge base based on a query.
    
    Uses semantic search with vector embeddings to find documents relevant to the query.
    """

    def __init__(self):
        """
        Initialize the KnowledgeBaseQueryTool.
        
        No repository object needed as it uses standalone functions.
        """
        pass  # No repository instance needed

    @with_error_handling(
        error_types=(EmbeddingError, QueryError, Exception),
        retry_count=1,
        retry_delay=1.0,
        fallback_value=[]
    )
    def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant research documents from the knowledge base.
        
        Converts the query to a vector embedding and finds semantically similar documents.
        
        Args:
            query (str): The search query text. Should be a clear, focused question or topic.
            top_k (int): Number of top documents to retrieve. Defaults to 5.
                
        Returns:
            List[Dict[str, Any]]: List of research documents matching the query, serialized as dicts.
                Each dict contains:
                - document_id: Unique identifier
                - title: Document title
                - content: Document content
                - source: Document source
                - category: Document category
                - date_added: Date the document was added
                - similarity: Similarity score to the query (0-1)
                
        Raises:
            EmbeddingError: If there is an error generating the query embedding.
            QueryError: If there is an error querying the knowledge base.
            
        Example:
            ```python
            docs = kb_query_tool.query("optimal running cadence", top_k=3)
            # Returns: [{"document_id": "doc-123", "title": "Running Cadence", ...}, ...]
            ```
        """
        try:
            logger.info(f"Querying knowledge base with: '{query}'")
            
            # 1. Get the embedding for the query text
            query_embedding = get_embedding(query)
            
            # 2. Query the repository for similar documents using the embedding
            similar_docs = kb_repo.query_similar_documents(query_embedding, top_k=top_k)
            
            # 3. Serialize the Pydantic models to dictionaries for consistent output
            result = [doc.model_dump() for doc in similar_docs]
            
            logger.info(f"Found {len(result)} relevant documents")
            return result
            
        except EmbeddingError as e:
            logger.error(f"Embedding error during knowledge base query: {e}")
            raise
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            raise QueryError(f"Failed to query knowledge base: {e}") from e
            
    def query_by_category(self, query: str, category: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant research documents from a specific category.
        
        Args:
            query (str): The search query text.
            category (str): The category to search within (e.g., "nutrition", "strength").
            top_k (int): Number of top documents to retrieve. Defaults to 5.
                
        Returns:
            List[Dict[str, Any]]: List of research documents matching the query and category.
                
        Raises:
            EmbeddingError: If there is an error generating the query embedding.
            QueryError: If there is an error querying the knowledge base.
            
        Example:
            ```python
            docs = kb_query_tool.query_by_category("protein intake", "nutrition", top_k=3)
            ```
        """
        try:
            # Get all documents first
            all_docs = self.query(query, top_k=top_k * 2)  # Get more docs to filter from
            
            # Filter by category
            filtered_docs = [doc for doc in all_docs if doc.get('category') == category]
            
            # Return top_k filtered docs
            return filtered_docs[:top_k]
        except Exception as e:
            logger.error(f"Error querying knowledge base by category: {e}")
            raise QueryError(f"Failed to query knowledge base by category: {e}") from e
            
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID.
        
        Args:
            document_id (str): The unique identifier of the document.
                
        Returns:
            Optional[Dict[str, Any]]: The document if found, None otherwise.
                
        Raises:
            QueryError: If there is an error querying the knowledge base.
            
        Example:
            ```python
            doc = kb_query_tool.get_document_by_id("doc-123")
            ```
        """
        try:
            document = kb_repo.get_document_by_id(document_id)
            if document:
                return document.model_dump()
            return None
        except Exception as e:
            logger.error(f"Error retrieving document by ID: {e}")
            raise QueryError(f"Failed to retrieve document by ID: {e}") from e