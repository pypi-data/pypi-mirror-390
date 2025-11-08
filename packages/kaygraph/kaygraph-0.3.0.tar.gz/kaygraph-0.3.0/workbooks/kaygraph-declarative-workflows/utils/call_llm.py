"""
LLM integration utilities with pre-configured API settings.

Uses the provided API configuration for calling language models.
"""

import os
import json
import logging
import requests
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM API calls."""

    url: str = "https://api.intelligence.io.solutions/api/v1/chat/completions"
    api_key: str = "io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJvd25lciI6IjUwZjcxMTM1LTA4NDktNDcwMC04ZTkyLTgwMjllYWFhNzc0OSIsImV4cCI6NDkxNDkzNzMzNH0.HlbIBeZUwHyh9GZaWW1-oMro-vFu_TeHs748tRQ6wGxvJq-QvGB-H4tJjp2J3T7FpI0VdYEemGijDRawAGhK1A"
    model: str = "meta-llama/Llama-3.3-70B-Instruct"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60

    # Available models
    AVAILABLE_MODELS = [
        "deepseek-ai/DeepSeek-R1-0528",
        "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "swiss-ai/Apertus-70B-Instruct-2509",
        "meta-llama/Llama-3.3-70B-Instruct",
        "Qwen/Qwen3-Next-80B-A3B-Instruct"
    ]

    # Embedding model
    EMBEDDING_MODEL = "BAAI/bge-multilingual-gemma2"


class LLMClient:
    """
    Client for making LLM API calls with retry logic and error handling.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        })

    def call(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Make a synchronous LLM API call.

        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters to override config

        Returns:
            LLM response text
        """
        # Merge config with kwargs
        payload = {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": False
        }

        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]

        try:
            logger.info(f"Calling LLM model: {payload['model']}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")

            response = self.session.post(
                self.config.url,
                json=payload,
                timeout=self.config.timeout
            )

            response.raise_for_status()
            result = response.json()

            # Extract content from response
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.info(f"LLM response received ({len(content)} chars)")
                return content
            else:
                raise ValueError("Invalid response format: no choices found")

        except requests.exceptions.Timeout:
            logger.error(f"LLM call timed out after {self.config.timeout}s")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API error: {e}")
            raise
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Invalid LLM response format: {e}")
            raise

    def call_with_system_prompt(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        Convenience method for calls with system and user prompts.

        Args:
            system_prompt: System message content
            user_prompt: User message content
            **kwargs: Additional parameters

        Returns:
            LLM response text
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        return self.call(messages, **kwargs)

    def extract_json(self, prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        Call LLM and extract JSON response.

        Args:
            prompt: Prompt that asks for JSON response
            schema: Optional JSON schema for structured output
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response
        """
        messages = [
            {
                "role": "system",
                "content": "You must respond with valid JSON only. No other text."
            },
            {"role": "user", "content": prompt}
        ]

        # Add schema if provided
        if schema:
            messages[0]["content"] += f"\n\nUse this JSON schema:\n{json.dumps(schema, indent=2)}"

        response = self.call(messages, **kwargs)

        try:
            # Try to extract JSON from response
            if "```json" in response:
                # Extract JSON from code block
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                # Assume entire response is JSON
                json_str = response.strip()

            return json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Response was: {response}")
            raise ValueError(f"Invalid JSON response from LLM: {e}")

    def get_embeddings(self, texts: Union[str, List[str]], **kwargs) -> List[List[float]]:
        """
        Get embeddings for text(s).

        Args:
            texts: Single text or list of texts to embed
            **kwargs: Additional parameters

        Returns:
            List of embedding vectors
        """
        url = "https://api.intelligence.io.solutions/api/v1/embeddings"

        # Normalize input to list
        if isinstance(texts, str):
            texts = [texts]

        payload = {
            "model": kwargs.get("model", self.config.EMBEDDING_MODEL),
            "input": texts
        }

        try:
            response = self.session.post(url, json=payload, timeout=self.config.timeout)
            response.raise_for_status()
            result = response.json()

            if "data" in result:
                embeddings = [item["embedding"] for item in result["data"]]
                logger.info(f"Generated {len(embeddings)} embeddings")
                return embeddings
            else:
                raise ValueError("Invalid embedding response format")

        except Exception as e:
            logger.error(f"Embedding API error: {e}")
            raise


# Global client instance
_default_client = LLMClient()


def call_llm(messages: List[Dict[str, str]], **kwargs) -> str:
    """
    Call LLM using default client.

    Args:
        messages: List of message dicts
        **kwargs: Additional parameters

    Returns:
        LLM response text
    """
    return _default_client.call(messages, **kwargs)


def call_llm_with_system(system_prompt: str, user_prompt: str, **kwargs) -> str:
    """
    Call LLM with system and user prompts using default client.

    Args:
        system_prompt: System message
        user_prompt: User message
        **kwargs: Additional parameters

    Returns:
        LLM response text
    """
    return _default_client.call_with_system_prompt(system_prompt, user_prompt, **kwargs)


def extract_json(prompt: str, schema: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Extract JSON from LLM response using default client.

    Args:
        prompt: Prompt requesting JSON response
        schema: Optional JSON schema
        **kwargs: Additional parameters

    Returns:
        Parsed JSON response
    """
    return _default_client.extract_json(prompt, schema, **kwargs)


def get_embeddings(texts: Union[str, List[str]], **kwargs) -> List[List[float]]:
    """
    Get embeddings using default client.

    Args:
        texts: Text(s) to embed
        **kwargs: Additional parameters

    Returns:
        List of embedding vectors
    """
    return _default_client.get_embeddings(texts, **kwargs)


def set_default_config(config: LLMConfig):
    """Update the default client configuration."""
    global _default_client
    _default_client = LLMClient(config)


def test_connection() -> bool:
    """
    Test the LLM API connection.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        response = call_llm(
            [{"role": "user", "content": "Respond with just 'OK'"}],
            max_tokens=10,
            temperature=0.1
        )
        return "OK" in response.upper()
    except Exception as e:
        logger.error(f"LLM connection test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    print("Testing LLM connection...")
    if test_connection():
        print("✅ LLM connection successful!")

        # Test a simple call
        response = call_llm_with_system(
            "You are a helpful assistant.",
            "What is 2 + 2?",
            max_tokens=50,
            temperature=0.1
        )
        print(f"Response: {response}")
    else:
        print("❌ LLM connection failed!")