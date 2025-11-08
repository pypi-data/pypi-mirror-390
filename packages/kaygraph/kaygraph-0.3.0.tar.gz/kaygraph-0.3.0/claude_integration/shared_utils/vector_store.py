"""
Vector store utilities for KayGraph RAG systems.

This module provides vector storage and retrieval capabilities for
semantic search and document retrieval in RAG workflows.
"""

import os
import json
import pickle
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from pathlib import Path
import asyncio
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Document:
    """Document representation for vector storage."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class SearchResult:
    """Result from vector search."""
    document: Document
    score: float
    rank: int


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def add_document(self, document: Document) -> None:
        """Add a document to the store."""
        pass

    @abstractmethod
    async def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to the store."""
        pass

    @abstractmethod
    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar documents."""
        pass

    @abstractmethod
    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        pass

    @abstractmethod
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        pass

    @abstractmethod
    async def update_document(self, document: Document) -> bool:
        """Update a document."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Get the number of documents in the store."""
        pass


class SimpleVectorStore(VectorStore):
    """In-memory vector store using NumPy for similarity calculations."""

    def __init__(self, embedding_dimension: Optional[int] = None):
        self.embedding_dimension = embedding_dimension
        self.documents: Dict[str, Document] = {}
        self.embeddings: List[np.ndarray] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def add_document(self, document: Document) -> None:
        """Add a document to the store."""
        if document.id in self.documents:
            self.logger.warning(f"Document {document.id} already exists, updating")
            await self.update_document(document)
            return

        if document.embedding is None:
            raise ValueError(f"Document {document.id} must have an embedding")

        if self.embedding_dimension is None:
            self.embedding_dimension = len(document.embedding)
        elif len(document.embedding) != self.embedding_dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.embedding_dimension}, got {len(document.embedding)}")

        self.documents[document.id] = document
        self.embeddings.append(np.array(document.embedding))

        self.logger.debug(f"Added document {document.id}")

    async def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to the store."""
        for document in documents:
            await self.add_document(document)

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar documents using cosine similarity."""
        if not self.documents:
            return []

        if len(query_embedding) != self.embedding_dimension:
            raise ValueError(f"Query embedding dimension mismatch: expected {self.embedding_dimension}, got {len(query_embedding)}")

        # Convert query to numpy array
        query_array = np.array(query_embedding).reshape(1, -1)

        # Calculate similarities
        if self.embeddings:
            embeddings_matrix = np.vstack(self.embeddings)
            similarities = cosine_similarity(query_array, embeddings_matrix)[0]
        else:
            similarities = np.array([])

        # Get top-k results above threshold
        valid_indices = np.where(similarities >= threshold)[0]
        sorted_indices = valid_indices[np.argsort(-similarities[valid_indices])][:top_k]

        results = []
        for rank, idx in enumerate(sorted_indices):
            doc_id = list(self.documents.keys())[idx]
            document = self.documents[doc_id]
            score = float(similarities[idx])

            results.append(SearchResult(
                document=document,
                score=score,
                rank=rank + 1
            ))

        self.logger.debug(f"Search returned {len(results)} results")
        return results

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return self.documents.get(doc_id)

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if doc_id not in self.documents:
            return False

        # Find index of document
        doc_ids = list(self.documents.keys())
        try:
            idx = doc_ids.index(doc_id)
            del self.documents[doc_id]
            del self.embeddings[idx]
            self.logger.debug(f"Deleted document {doc_id}")
            return True
        except ValueError:
            return False

    async def update_document(self, document: Document) -> bool:
        """Update a document."""
        if document.id not in self.documents:
            return False

        if document.embedding is None:
            raise ValueError("Updated document must have an embedding")

        if len(document.embedding) != self.embedding_dimension:
            raise ValueError(f"Embedding dimension mismatch")

        # Find and update embedding
        doc_ids = list(self.documents.keys())
        idx = doc_ids.index(document.id)
        self.documents[document.id] = document
        self.embeddings[idx] = np.array(document.embedding)

        self.logger.debug(f"Updated document {document.id}")
        return True

    def size(self) -> int:
        """Get the number of documents in the store."""
        return len(self.documents)

    async def save_to_file(self, file_path: str) -> None:
        """Save the vector store to a file."""
        data = {
            'embedding_dimension': self.embedding_dimension,
            'documents': {doc_id: doc.to_dict() for doc_id, doc in self.documents.items()}
        }

        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

        self.logger.info(f"Saved vector store to {file_path}")

    async def load_from_file(self, file_path: str) -> None:
        """Load the vector store from a file."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Vector store file not found: {file_path}")

        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        self.embedding_dimension = data['embedding_dimension']
        self.documents = {}
        self.embeddings = []

        for doc_id, doc_data in data['documents'].items():
            document = Document.from_dict(doc_data)
            self.documents[doc_id] = document
            self.embeddings.append(np.array(document.embedding))

        self.logger.info(f"Loaded vector store from {file_path} with {len(self.documents)} documents")


class ChromaVectorStore(VectorStore):
    """Vector store using ChromaDB for persistent storage."""

    def __init__(self, collection_name: str, persist_directory: Optional[str] = None):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._client = None
        self._collection = None

    def __enter__(self):
        """Context manager entry."""
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_directory)
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
            self.logger.info(f"ChromaDB collection '{self.collection_name}' initialized")
        except ImportError:
            raise ImportError("chromadb package not installed. Install with: pip install chromadb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client:
            self._client = None
        self.logger.info("ChromaDB client cleaned up")

    async def add_document(self, document: Document) -> None:
        """Add a document to ChromaDB."""
        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")

        # Check if document already exists
        existing = await self.get_document(document.id)
        if existing:
            await self.update_document(document)
            return

        # Add to ChromaDB
        self._collection.add(
            ids=[document.id],
            embeddings=[document.embedding],
            documents=[document.content],
            metadatas=[document.metadata]
        )

        self.logger.debug(f"Added document {document.id} to ChromaDB")

    async def add_documents(self, documents: List[Document]) -> None:
        """Add multiple documents to ChromaDB."""
        if not documents:
            return

        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")

        # Prepare batch data
        ids = [doc.id for doc in documents]
        embeddings = [doc.embedding for doc in documents]
        contents = [doc.content for doc in documents]
        metadatas = [doc.metadata for doc in documents]

        # Add batch to ChromaDB
        self._collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas
        )

        self.logger.debug(f"Added {len(documents)} documents to ChromaDB")

    async def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: float = 0.0
    ) -> List[SearchResult]:
        """Search for similar documents in ChromaDB."""
        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")

        # Query ChromaDB
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Convert to SearchResult objects
        search_results = []
        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                score = results['distances'][0][i] if 'distances' in results else 0.0
                content = results['documents'][0][i] if 'documents' in results else ""
                metadata = results['metadatas'][0][i] if 'metadatas' in results else {}

                # Convert distance to similarity (ChromaDB returns L2 distance)
                similarity = 1 / (1 + score) if score >= 0 else 1

                if similarity >= threshold:
                    document = Document(
                        id=doc_id,
                        content=content,
                        metadata=metadata,
                        embedding=None  # Not stored in query results
                    )

                    search_results.append(SearchResult(
                        document=document,
                        score=similarity,
                        rank=i + 1
                    ))

        return search_results

    async def get_document(self, doc_id: str) -> Optional[Document]:
        """Get a document by ID from ChromaDB."""
        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")

        results = self._collection.get(ids=[doc_id])

        if results['ids'] and results['ids'][0]:
            document = Document(
                id=results['ids'][0],
                content=results['documents'][0] if 'documents' in results else "",
                metadata=results['metadatas'][0] if 'metadatas' in results else {},
                embedding=None
            )
            return document

        return None

    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID from ChromaDB."""
        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")

        try:
            self._collection.delete(ids=[doc_id])
            self.logger.debug(f"Deleted document {doc_id} from ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete document {doc_id}: {e}")
            return False

    async def update_document(self, document: Document) -> bool:
        """Update a document in ChromaDB."""
        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")

        try:
            self._collection.update(
                ids=[document.id],
                embeddings=[document.embedding],
                documents=[document.content],
                metadatas=[document.metadata]
            )
            self.logger.debug(f"Updated document {document.id} in ChromaDB")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update document {document.id}: {e}")
            return False

    def size(self) -> int:
        """Get the number of documents in the store."""
        if self._collection is None:
            raise RuntimeError("ChromaDB not initialized. Use context manager.")
        return self._collection.count()


def create_vector_store(
    store_type: str = "simple",
    collection_name: str = "default",
    persist_directory: Optional[str] = None,
    embedding_dimension: Optional[int] = None
) -> VectorStore:
    """
    Factory function to create vector store.

    Args:
        store_type: Type of store ('simple', 'chroma')
        collection_name: Name of the collection (for ChromaDB)
        persist_directory: Directory to persist ChromaDB data
        embedding_dimension: Embedding dimension (for simple store)

    Returns:
        VectorStore instance
    """
    if store_type == "simple":
        return SimpleVectorStore(embedding_dimension)
    elif store_type == "chroma":
        return ChromaVectorStore(collection_name, persist_directory)
    else:
        raise ValueError(f"Unsupported store type: {store_type}")


if __name__ == "__main__":
    """Test vector stores."""
    import asyncio

    async def test_vector_stores():
        """Test simple vector store."""
        print("Testing SimpleVectorStore...")

        # Create store
        store = SimpleVectorStore(embedding_dimension=384)

        # Create test documents
        docs = [
            Document(
                id="doc1",
                content="This is about machine learning",
                metadata={"topic": "AI", "source": "textbook"},
                embedding=np.random.rand(384).tolist()
            ),
            Document(
                id="doc2",
                content="This discusses deep learning algorithms",
                metadata={"topic": "AI", "source": "paper"},
                embedding=np.random.rand(384).tolist()
            ),
            Document(
                id="doc3",
                content="This is about cooking recipes",
                metadata={"topic": "food", "source": "blog"},
                embedding=np.random.rand(384).tolist()
            )
        ]

        # Add documents
        await store.add_documents(docs)
        print(f"Added {store.size()} documents")

        # Test search
        query_embedding = np.random.rand(384).tolist()
        results = await store.search(query_embedding, top_k=2)
        print(f"Search returned {len(results)} results")
        for result in results:
            print(f"  {result.rank}. {result.document.id} (score: {result.score:.3f})")

        # Test persistence
        await store.save_to_file("test_vector_store.pkl")
        print("Saved to file")

        # Load from file
        new_store = SimpleVectorStore()
        await new_store.load_from_file("test_vector_store.pkl")
        print(f"Loaded {new_store.size()} documents from file")

        # Cleanup
        os.remove("test_vector_store.pkl")
        print("Test completed!")

    # Run test
    asyncio.run(test_vector_stores())