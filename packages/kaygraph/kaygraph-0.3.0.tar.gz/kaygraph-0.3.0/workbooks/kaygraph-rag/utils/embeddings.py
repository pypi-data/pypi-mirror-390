"""
Embedding utilities for RAG system.

Supports OpenAI, Groq, Ollama, and any OpenAI-compatible embedding service.
Falls back to local sentence transformers if no API is available.
"""

import os
import logging
import numpy as np
from typing import List, Union, Optional

logger = logging.getLogger(__name__)


def get_embedding_client():
    """Get the appropriate embedding client based on environment."""
    provider = os.environ.get("EMBEDDING_PROVIDER", "openai").lower()
    
    try:
        from openai import OpenAI
        
        if provider == "openai":
            return OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
            ), "text-embedding-ada-002"
        elif provider == "ollama":
            return OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"  # Ollama doesn't need a real key
            ), "nomic-embed-text"
        elif provider == "voyageai":
            return OpenAI(
                base_url="https://api.voyageai.com/v1",
                api_key=os.environ.get("VOYAGE_API_KEY", "your-voyage-api-key")
            ), "voyage-2"
        elif provider == "custom":
            return OpenAI(
                base_url=os.environ.get("EMBEDDING_BASE_URL", "http://localhost:8000/v1"),
                api_key=os.environ.get("EMBEDDING_API_KEY", "your-api-key")
            ), os.environ.get("EMBEDDING_MODEL", "text-embedding-ada-002")
        else:
            # Default to OpenAI
            return OpenAI(
                api_key=os.environ.get("OPENAI_API_KEY", "your-openai-api-key")
            ), "text-embedding-ada-002"
    except ImportError:
        logger.warning("OpenAI package not installed. Using local embeddings.")
        return None, None


def generate_embedding(text: str, model: Optional[str] = None) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Text to embed
        model: Embedding model to use (overrides default)
        
    Returns:
        Embedding vector (list of floats)
    """
    client, default_model = get_embedding_client()
    model = model or default_model or "text-embedding-ada-002"
    
    if client:
        try:
            # Use OpenAI-compatible API
            response = client.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"API embedding failed: {e}. Using local fallback.")
    
    # Fallback to local embeddings
    return generate_local_embedding(text)


def generate_embeddings_batch(texts: List[str], model: Optional[str] = None) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently.
    
    Args:
        texts: List of texts to embed
        model: Embedding model to use
        
    Returns:
        List of embedding vectors
    """
    if not texts:
        return []
    
    client, default_model = get_embedding_client()
    model = model or default_model or "text-embedding-ada-002"
    
    if client:
        try:
            # Most OpenAI-compatible APIs support batch embedding
            response = client.embeddings.create(
                input=texts,
                model=model
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.warning(f"Batch API embedding failed: {e}. Using local fallback.")
    
    # Fallback to local embeddings
    return [generate_local_embedding(text) for text in texts]


def generate_local_embedding(text: str, dimension: int = 384) -> List[float]:
    """
    Generate embedding locally using a simple but effective method.
    
    This uses TF-IDF-like features combined with semantic hashing.
    Not as good as neural embeddings but works offline.
    """
    import hashlib
    import math
    
    # Tokenize and extract features
    words = text.lower().split()
    
    # Initialize embedding
    embedding = [0.0] * dimension
    
    # Word frequency features
    word_counts = {}
    for word in words:
        word_counts[word] = word_counts.get(word, 0) + 1
    
    # TF-IDF-like scoring
    total_words = len(words)
    for word, count in word_counts.items():
        tf = count / total_words if total_words > 0 else 0
        
        # Hash word to multiple positions (simulating distributed representation)
        word_hash = hashlib.sha256(word.encode()).digest()
        for i in range(min(10, dimension // 10)):  # Spread each word across 10 dimensions
            pos = int.from_bytes(word_hash[i*2:(i+1)*2], 'big') % dimension
            weight = tf * (1.0 + math.log(len(word)))  # Favor longer words
            embedding[pos] += weight
    
    # Add position-based features
    if words:
        # Beginning of text
        for i, word in enumerate(words[:5]):
            pos = hash(f"start_{word}") % dimension
            embedding[pos] += 0.5 / (i + 1)
        
        # End of text
        for i, word in enumerate(words[-5:]):
            pos = hash(f"end_{word}") % dimension
            embedding[pos] += 0.5 / (i + 1)
    
    # Add character n-gram features
    text_lower = text.lower()
    for n in [2, 3]:  # Bigrams and trigrams
        for i in range(len(text_lower) - n + 1):
            ngram = text_lower[i:i+n]
            pos = hash(f"ngram_{ngram}") % dimension
            embedding[pos] += 0.1
    
    # Normalize to unit vector
    norm = math.sqrt(sum(x*x for x in embedding))
    if norm > 0:
        embedding = [x / norm for x in embedding]
    
    return embedding


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score between -1 and 1
    """
    # Simple implementation
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 * magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def find_similar_chunks(
    query_embedding: List[float],
    chunk_embeddings: List[List[float]],
    chunks: List[dict],
    top_k: int = 5,
    threshold: float = 0.5
) -> List[dict]:
    """
    Find most similar chunks to query.
    
    Args:
        query_embedding: Query embedding vector
        chunk_embeddings: List of chunk embeddings
        chunks: List of chunk dictionaries
        top_k: Number of results to return
        threshold: Minimum similarity threshold
        
    Returns:
        List of relevant chunks with similarity scores
    """
    # Calculate similarities
    similarities = []
    for i, chunk_embedding in enumerate(chunk_embeddings):
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        if similarity >= threshold:
            similarities.append((i, similarity))
    
    # Sort by similarity
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Get top chunks
    results = []
    for idx, score in similarities[:top_k]:
        chunk_with_score = chunks[idx].copy()
        chunk_with_score['similarity_score'] = score
        results.append(chunk_with_score)
    
    logger.info(f"Found {len(results)} relevant chunks (threshold={threshold})")
    return results


if __name__ == "__main__":
    # Test embedding generation
    logging.basicConfig(level=logging.INFO)
    
    test_text = "KayGraph is a framework for building AI applications."
    embedding = generate_embedding(test_text)
    print(f"Generated embedding of dimension: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")
    
    # Test similarity
    text1 = "KayGraph helps build AI apps"
    text2 = "KayGraph is an AI framework"
    text3 = "The weather is nice today"
    
    emb1 = generate_embedding(text1)
    emb2 = generate_embedding(text2)
    emb3 = generate_embedding(text3)
    
    print(f"\nSimilarity between related texts: {cosine_similarity(emb1, emb2):.3f}")
    print(f"Similarity between unrelated texts: {cosine_similarity(emb1, emb3):.3f}")