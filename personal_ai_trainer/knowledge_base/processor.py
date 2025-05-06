"""
Document processing utilities for the Knowledge Base.

Includes functions for chunking, key information extraction, and topic categorization.
"""

from typing import List, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

try:
    import nltk
    nltk.data.find('tokenizers/punkt')
    SENTENCE_TOKENIZER_AVAILABLE = True
except (ImportError, LookupError):
    SENTENCE_TOKENIZER_AVAILABLE = False


def chunk_document(text: str, max_chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """
    Split a document into chunks suitable for embedding.

    Args:
        text (str): The document text.
        max_chunk_size (int): Maximum number of words per chunk.
        overlap (int): Number of words to overlap between chunks.

    Returns:
        List[str]: List of text chunks.
    """
    if SENTENCE_TOKENIZER_AVAILABLE:
        from nltk.tokenize import sent_tokenize, word_tokenize
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        for sentence in sentences:
            words = word_tokenize(sentence)
            if current_length + len(words) > max_chunk_size:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    # Overlap
                    current_chunk = current_chunk[-overlap:] if overlap > 0 else []
                    current_length = len(current_chunk)
            current_chunk.extend(words)
            current_length += len(words)
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks
    else:
        # Fallback: split by whitespace
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = words[i:i + max_chunk_size]
            chunks.append(' '.join(chunk))
            i += max_chunk_size - overlap
        return chunks


def extract_key_info(text: str) -> Dict[str, Any]:
    """
    Extract key information from a research document.

    Args:
        text (str): The document text.

    Returns:
        Dict[str, Any]: Dictionary with extracted fields (title, summary, etc.).
    """
    # Simple heuristics: title = first line, summary = first paragraph
    lines = text.strip().split('\n')
    title = lines[0].strip() if lines else ""
    paragraphs = re.split(r'\n\s*\n', text.strip())
    summary = paragraphs[0].strip() if paragraphs else ""
    return {
        "title": title,
        "summary": summary
    }


def categorize_document(text: str) -> str:
    """
    Categorize a document by topic using keyword heuristics.

    Args:
        text (str): The document text.

    Returns:
        str: The category (e.g., "exercise science", "recovery", "nutrition", "other").
    """
    categories = {
        "exercise science": ["strength", "hypertrophy", "endurance", "training", "exercise", "muscle", "cardio"],
        "recovery": ["sleep", "recovery", "rest", "fatigue", "overtraining", "rehab"],
        "nutrition": ["nutrition", "diet", "protein", "carbohydrate", "fat", "supplement", "calorie", "hydration"]
    }
    text_lower = text.lower()
    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text_lower:
                return category
    return "other"