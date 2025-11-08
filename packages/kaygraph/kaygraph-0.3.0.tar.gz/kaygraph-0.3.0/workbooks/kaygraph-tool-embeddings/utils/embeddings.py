"""
Embeddings utility with OpenAI-compatible API support.

Supports OpenAI, Groq, Ollama, and any OpenAI-compatible embedding service.
Falls back to local sentence transformers if no API is available.
"""

import os
import logging
import numpy as np
from typing import List, Union, Optional, Dict, Any, Tuple
import json
import math

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
    if len(vec1) != len(vec2):
        raise ValueError(f"Vectors must have same dimension: {len(vec1)} != {len(vec2)}")
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = sum(a * a for a in vec1) ** 0.5
    magnitude2 = sum(b * b for b in vec2) ** 0.5
    
    if magnitude1 * magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def find_similar(
    query_embedding: List[float],
    embeddings: List[List[float]],
    texts: List[str],
    top_k: int = 5
) -> List[Tuple[str, float]]:
    """
    Find most similar texts based on embeddings.
    
    Args:
        query_embedding: Query vector
        embeddings: List of document embeddings
        texts: List of document texts
        top_k: Number of results to return
        
    Returns:
        List of (text, similarity_score) tuples
    """
    similarities = []
    
    for i, embedding in enumerate(embeddings):
        score = cosine_similarity(query_embedding, embedding)
        similarities.append((texts[i], score))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]


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


class EmbeddingGenerator:
    """Generate embeddings for text using various methods."""
    
    def __init__(self, method: str = "api", dimension: int = 384):
        """
        Initialize embedding generator.
        
        Args:
            method: Embedding method ('api', 'local')
            dimension: Embedding dimension for local method
        """
        self.method = method
        self.dimension = dimension
        
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        if self.method == "api":
            return generate_embedding(text)
        else:
            return generate_local_embedding(text, self.dimension)
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if self.method == "api":
            return generate_embeddings_batch(texts)
        else:
            return [generate_local_embedding(text, self.dimension) for text in texts]


class EmbeddingIndex:
    """Simple in-memory embedding index for similarity search."""
    
    def __init__(self, embedding_generator: Optional[EmbeddingGenerator] = None):
        """Initialize index with embedding generator."""
        self.generator = embedding_generator or EmbeddingGenerator()
        self.embeddings = []
        self.texts = []
        self.metadata = []
    
    def add(self, text: str, metadata: Dict[str, Any] = None):
        """Add text to index."""
        embedding = self.generator.embed_text(text)
        self.embeddings.append(embedding)
        self.texts.append(text)
        self.metadata.append(metadata or {})
    
    def add_batch(self, texts: List[str], metadata_list: List[Dict[str, Any]] = None):
        """Add multiple texts to index."""
        embeddings = self.generator.embed_batch(texts)
        self.embeddings.extend(embeddings)
        self.texts.extend(texts)
        
        if metadata_list:
            self.metadata.extend(metadata_list)
        else:
            self.metadata.extend([{}] * len(texts))
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar texts."""
        if not self.embeddings:
            return []
        
        query_embedding = self.generator.embed_text(query)
        
        results = []
        for i, embedding in enumerate(self.embeddings):
            score = cosine_similarity(query_embedding, embedding)
            results.append({
                "text": self.texts[i],
                "score": score,
                "metadata": self.metadata[i],
                "index": i
            })
        
        # Sort by score
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:top_k]
    
    def save(self, path: str):
        """Save index to file."""
        data = {
            "embeddings": self.embeddings,
            "texts": self.texts,
            "metadata": self.metadata,
            "generator_config": {
                "method": self.generator.method,
                "dimension": self.generator.dimension
            }
        }
        
        with open(path, 'w') as f:
            json.dump(data, f)
    
    def load(self, path: str):
        """Load index from file."""
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.embeddings = data["embeddings"]
        self.texts = data["texts"]
        self.metadata = data["metadata"]


# Convenience functions

def create_embeddings(texts: List[str], method: str = "api") -> List[List[float]]:
    """Create embeddings for a list of texts."""
    generator = EmbeddingGenerator(method=method)
    return generator.embed_batch(texts)


def create_index(texts: List[str], method: str = "api") -> EmbeddingIndex:
    """Create an embedding index from texts."""
    generator = EmbeddingGenerator(method=method)
    index = EmbeddingIndex(generator)
    index.add_batch(texts)
    return index


if __name__ == "__main__":
    # Test embedding generation
    logging.basicConfig(level=logging.INFO)
    
    # Show current configuration
    provider = os.environ.get("EMBEDDING_PROVIDER", "openai")
    print(f"Using embedding provider: {provider}")
    
    if provider == "openai":
        print(f"API Key set: {'OPENAI_API_KEY' in os.environ}")
    
    # Test single embedding
    test_text = "KayGraph is a framework for building AI applications."
    print(f"\nGenerating embedding for: '{test_text}'")
    
    embedding = generate_embedding(test_text)
    print(f"Generated embedding of dimension: {len(embedding)}")
    print(f"First 10 values: {embedding[:10]}")
    
    # Test batch embeddings
    texts = [
        "KayGraph helps build AI apps",
        "KayGraph is an AI framework",
        "The weather is nice today"
    ]
    
    print("\nGenerating batch embeddings...")
    embeddings = generate_embeddings_batch(texts)
    print(f"Generated {len(embeddings)} embeddings")
    
    # Test similarity
    print("\nTesting similarity:")
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = cosine_similarity(embeddings[i], embeddings[j])
            print(f"'{texts[i]}' <-> '{texts[j]}': {sim:.3f}")
    
    # Test index
    print("\n\nTesting Embedding Index:")
    index = create_index(texts)
    
    results = index.search("coding with Python", top_k=3)
    print("\nSearch results for 'coding with Python':")
    for result in results:
        print(f"  {result['score']:.3f}: {result['text']}")