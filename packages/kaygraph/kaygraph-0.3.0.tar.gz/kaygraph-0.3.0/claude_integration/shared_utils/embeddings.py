"""
Embedding service utilities for KayGraph.

This module provides embedding generation capabilities from various providers
including io.net, OpenAI, and other embedding services.
"""

import os
import logging
import asyncio
import aiohttp
import numpy as np
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class EmbeddingConfig:
    """Configuration for embedding services."""
    provider: str
    model: str
    api_key: str
    base_url: Optional[str] = None
    batch_size: int = 100
    dimension: Optional[int] = None
    max_retries: int = 3
    timeout: int = 30


class EmbeddingService(ABC):
    """Abstract base class for embedding services."""

    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        pass

    async def get_embeddings_batched(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings with automatic batching."""
        all_embeddings = []

        for i in range(0, len(texts), self.config.batch_size):
            batch = texts[i:i + self.config.batch_size]
            batch_embeddings = await self.get_embeddings(batch)
            all_embeddings.extend(batch_embeddings)

            self.logger.debug(f"Processed batch {i//self.config.batch_size + 1}, "
                            f"texts {i+1}-{min(i+self.config.batch_size, len(texts))}")

        return all_embeddings


class IOEmbeddingService(EmbeddingService):
    """Embedding service for io.net API."""

    def __init__(self, api_key: str, model: str = "BAAI/bge-multilingual-gemma2"):
        config = EmbeddingConfig(
            provider="io_net",
            model=model,
            api_key=api_key,
            base_url="https://api.intelligence.io.solutions/api/v1",
            dimension=1024  # Typical dimension for multilingual models
        )
        super().__init__(config)

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text from io.net."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.config.model,
                "input": text,
                "encoding_format": "float"
            }

            for attempt in range(self.config.max_retries + 1):
                try:
                    async with session.post(
                        f"{self.config.base_url}/embeddings",
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["data"][0]["embedding"]
                        else:
                            error_text = await response.text()
                            raise Exception(f"API error: {response.status} - {error_text}")

                except Exception as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Embedding request failed (attempt {attempt + 1}): {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        self.logger.error(f"All retries exhausted for embedding request: {e}")
                        raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts from io.net."""
        if not texts:
            return []

        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.config.model,
                "input": texts,
                "encoding_format": "float"
            }

            for attempt in range(self.config.max_retries + 1):
                try:
                    async with session.post(
                        f"{self.config.base_url}/embeddings",
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            # Sort by index to maintain order
                            sorted_data = sorted(result["data"], key=lambda x: x["index"])
                            return [item["embedding"] for item in sorted_data]
                        else:
                            error_text = await response.text()
                            raise Exception(f"API error: {response.status} - {error_text}")

                except Exception as e:
                    if attempt < self.config.max_retries:
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Batch embedding request failed (attempt {attempt + 1}): {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        self.logger.error(f"All retries exhausted for batch embedding request: {e}")
                        raise


class OpenAIEmbeddingService(EmbeddingService):
    """Embedding service for OpenAI API."""

    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        config = EmbeddingConfig(
            provider="openai",
            model=model,
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            dimension=1536 if model == "text-embedding-3-small" else 3072
        )
        super().__init__(config)

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text from OpenAI."""
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.config.api_key)

            response = await client.embeddings.create(
                model=self.config.model,
                input=text
            )
            return response.data[0].embedding

        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            self.logger.error(f"OpenAI embedding request failed: {e}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts from OpenAI."""
        if not texts:
            return []

        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.config.api_key)

            response = await client.embeddings.create(
                model=self.config.model,
                input=texts
            )
            # Sort by index to maintain order
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]

        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
        except Exception as e:
            self.logger.error(f"OpenAI batch embedding request failed: {e}")
            raise


class HuggingFaceEmbeddingService(EmbeddingService):
    """Local embedding service using HuggingFace transformers."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        config = EmbeddingConfig(
            provider="huggingface",
            model=model_name,
            api_key="",  # Not needed for local models
            dimension=384  # Dimension for all-MiniLM-L6-v2
        )
        super().__init__(config)
        self._model = None
        self._tokenizer = None

    def _load_model(self):
        """Load the HuggingFace model."""
        try:
            from transformers import AutoTokenizer, AutoModel
            import torch

            if self._model is None:
                self.logger.info(f"Loading HuggingFace model: {self.config.model}")
                self._tokenizer = AutoTokenizer.from_pretrained(self.config.model)
                self._model = AutoModel.from_pretrained(self.config.model)
                self.logger.info("Model loaded successfully")

        except ImportError:
            raise ImportError("transformers package not installed. Install with: pip install transformers torch")

    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text using local HuggingFace model."""
        if self._model is None:
            self._load_model()

        try:
            import torch

            # Tokenize and get embeddings
            inputs = self._tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

            with torch.no_grad():
                outputs = self._model(**inputs)
                # Use mean pooling
                embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

            return embeddings.tolist()

        except Exception as e:
            self.logger.error(f"HuggingFace embedding request failed: {e}")
            raise

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts using local HuggingFace model."""
        if self._model is None:
            self._load_model()

        try:
            import torch

            # Process in batches to avoid memory issues
            batch_size = min(self.config.batch_size, 32)  # Smaller batch for local processing
            all_embeddings = []

            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                inputs = self._tokenizer(
                    batch_texts,
                    return_tensors="pt",
                    truncation=True,
                    padding=True,
                    max_length=512
                )

                with torch.no_grad():
                    outputs = self._model(**inputs)
                    # Use mean pooling
                    batch_embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

                # Handle single text case
                if batch_embeddings.ndim == 1:
                    batch_embeddings = batch_embeddings.reshape(1, -1)

                all_embeddings.extend(batch_embeddings.tolist())

            return all_embeddings

        except Exception as e:
            self.logger.error(f"HuggingFace batch embedding request failed: {e}")
            raise


def create_embedding_service(
    provider: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> EmbeddingService:
    """
    Factory function to create embedding service based on provider.

    Args:
        provider: Provider name ('io_net', 'openai', 'huggingface')
        api_key: API key (not needed for huggingface)
        model: Model name

    Returns:
        EmbeddingService instance
    """
    if provider == "io_net":
        if not api_key:
            api_key = os.getenv("API_KEY")
            if not api_key:
                raise ValueError("API key required for io.net provider")
        return IOEmbeddingService(api_key, model or "BAAI/bge-multilingual-gemma2")

    elif provider == "openai":
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        return OpenAIEmbeddingService(api_key, model or "text-embedding-3-small")

    elif provider == "huggingface":
        return HuggingFaceEmbeddingService(model or "sentence-transformers/all-MiniLM-L6-v2")

    else:
        raise ValueError(f"Unsupported provider: {provider}")


if __name__ == "__main__":
    """Test embedding services."""
    import asyncio

    async def test_embedding_services():
        """Test different embedding services."""
        # Test io.net embeddings
        try:
            api_key = os.getenv("API_KEY")
            if api_key:
                print("Testing io.net embeddings...")
                io_service = IOEmbeddingService(api_key)

                # Test single embedding
                embedding = await io_service.get_embedding("Hello, world!")
                print(f"Single embedding dimension: {len(embedding)}")

                # Test batch embeddings
                texts = ["Hello", "World", "Embeddings"]
                embeddings = await io_service.get_embeddings(texts)
                print(f"Batch embeddings: {len(embeddings)} embeddings, each with {len(embeddings[0])} dimensions")

        except Exception as e:
            print(f"io.net test failed: {e}")

        # Test HuggingFace embeddings
        try:
            print("\nTesting HuggingFace embeddings...")
            hf_service = HuggingFaceEmbeddingService()

            # Test single embedding
            embedding = await hf_service.get_embedding("Hello, world!")
            print(f"Single embedding dimension: {len(embedding)}")

            # Test batch embeddings
            texts = ["Hello", "World", "Embeddings"]
            embeddings = await hf_service.get_embeddings(texts)
            print(f"Batch embeddings: {len(embeddings)} embeddings, each with {len(embeddings[0])} dimensions")

        except Exception as e:
            print(f"HuggingFace test failed: {e}")

    # Run tests
    asyncio.run(test_embedding_services())