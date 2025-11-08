"""
Claude API integration utilities for KayGraph.

This module provides a clean interface for interacting with Claude API
across different providers (Anthropic, io.net, Z.ai) while following
KayGraph patterns.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

import aiohttp
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, query


class Provider(Enum):
    """Supported API providers."""
    ANTHROPIC = "anthropic"
    IO_NET = "io_net"
    Z_AI = "z_ai"


@dataclass
class ClaudeConfig:
    """Configuration for Claude API integration."""
    provider: Provider
    model: str
    api_key: str
    base_url: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 1.0

    @classmethod
    def from_env(cls, provider: Optional[Provider] = None) -> 'ClaudeConfig':
        """Create configuration from environment variables."""
        if provider is None:
            provider = cls._detect_provider()

        if provider == Provider.ANTHROPIC:
            return cls(
                provider=Provider.ANTHROPIC,
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                api_key=os.getenv("ANTHROPIC_API_KEY", ""),
                base_url="https://api.anthropic.com",
            )
        elif provider == Provider.IO_NET:
            return cls(
                provider=Provider.IO_NET,
                model=os.getenv("ANTHROPIC_MODEL", "glm-4.6"),
                api_key=os.getenv("API_KEY", ""),
                base_url="https://api.intelligence.io.solutions/api/v1",
            )
        elif provider == Provider.Z_AI:
            return cls(
                provider=Provider.Z_AI,
                model=os.getenv("ANTHROPIC_MODEL", "glm-4.6"),
                api_key=os.getenv("ANTHROPIC_AUTH_TOKEN", ""),
                base_url="https://api.z.ai/api/anthropic",
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    @staticmethod
    def _detect_provider() -> Provider:
        """Detect provider from environment variables."""
        if os.getenv("API_KEY") and os.getenv("ANTHROPIC_BASE_URL") == "https://api.intelligence.io.solutions/api/v1":
            return Provider.IO_NET
        elif os.getenv("ANTHROPIC_BASE_URL") == "https://api.z.ai/api/anthropic":
            return Provider.Z_AI
        else:
            return Provider.ANTHROPIC


class ClaudeAPIClient:
    """
    Production-ready Claude API client with retry logic, monitoring, and error handling.

    This client follows KayGraph patterns for external service integration.
    """

    def __init__(self, config: ClaudeConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._client = None
        self._metrics = {
            'requests': 0,
            'errors': 0,
            'tokens_used': 0,
            'response_times': []
        }

    def __enter__(self):
        """Context manager entry."""
        self._client = ClaudeSDKClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key
        )
        self.logger.info(f"Claude client initialized for provider: {self.config.provider.value}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._client:
            self._client = None
        self.logger.info("Claude client cleaned up")

    async def call_claude(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        tools: Optional[List[str]] = None,
        stream: bool = False
    ) -> str:
        """
        Call Claude API with retry logic and monitoring.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            max_tokens: Override default max tokens
            temperature: Override default temperature
            tools: List of available tools
            stream: Whether to stream the response

        Returns:
            Claude's response as a string
        """
        start_time = time.time()

        for attempt in range(self.config.max_retries + 1):
            try:
                self._metrics['requests'] += 1

                # Create options
                options = ClaudeAgentOptions(
                    model=self.config.model,
                    max_tokens=max_tokens or self.config.max_tokens,
                    temperature=temperature or self.config.temperature,
                    system_prompt=system_prompt,
                    allowed_tools=tools,
                )

                # Make the API call
                response_parts = []

                if stream:
                    async for message in query(prompt, options):
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    response_parts.append(block.text)
                else:
                    for message in query(prompt, options):
                        if hasattr(message, 'content'):
                            for block in message.content:
                                if hasattr(block, 'text'):
                                    response_parts.append(block.text)

                response = "".join(response_parts)

                # Update metrics
                response_time = time.time() - start_time
                self._metrics['response_times'].append(response_time)
                self._metrics['tokens_used'] += len(response.split())  # Rough estimate

                self.logger.info(f"Claude call successful in {response_time:.2f}s")
                return response

            except Exception as e:
                self.logger.warning(f"Claude API call failed (attempt {attempt + 1}): {e}")

                if attempt < self.config.max_retries:
                    # Exponential backoff
                    delay = self.config.retry_delay * (2 ** attempt)
                    self.logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    self._metrics['errors'] += 1
                    self.logger.error(f"All retries exhausted for Claude API call: {e}")
                    raise

    async def call_claude_with_structured_output(
        self,
        prompt: str,
        output_schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call Claude and parse structured JSON output.

        Args:
            prompt: The user prompt
            output_schema: Expected output schema
            system_prompt: Optional system prompt

        Returns:
            Parsed structured output
        """
        # Add schema instruction to prompt
        schema_instruction = f"""
Please respond with valid JSON that matches this schema:
{output_schema}

Your response should be only the JSON, no additional text.
"""

        full_prompt = f"{prompt}\n\n{schema_instruction}"

        response = await self.call_claude(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=0.1  # Lower temperature for structured output
        )

        # Parse JSON response
        try:
            import json
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse structured response: {e}")
            # Return a default structure matching the schema
            return {"error": "Failed to parse response", "raw_response": response}

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if self._metrics['response_times']:
            avg_response_time = sum(self._metrics['response_times']) / len(self._metrics['response_times'])
        else:
            avg_response_time = 0

        return {
            'requests': self._metrics['requests'],
            'errors': self._metrics['errors'],
            'error_rate': self._metrics['errors'] / max(self._metrics['requests'], 1),
            'tokens_used': self._metrics['tokens_used'],
            'avg_response_time': avg_response_time,
            'provider': self.config.provider.value,
            'model': self.config.model
        }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self._metrics = {
            'requests': 0,
            'errors': 0,
            'tokens_used': 0,
            'response_times': []
        }
        self.logger.info("Metrics reset")


# Convenience functions for common use cases
async def simple_claude_call(
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: Optional[Provider] = None
) -> str:
    """
    Simple one-shot Claude call for quick prototyping.

    Args:
        prompt: The prompt to send
        system_prompt: Optional system prompt
        provider: API provider to use

    Returns:
        Claude's response
    """
    config = ClaudeConfig.from_env(provider)

    async with ClaudeAPIClient(config) as client:
        return await client.call_claude(prompt, system_prompt)


async def structured_claude_call(
    prompt: str,
    output_schema: Dict[str, Any],
    system_prompt: Optional[str] = None,
    provider: Optional[Provider] = None
) -> Dict[str, Any]:
    """
    Claude call that returns structured data.

    Args:
        prompt: The prompt to send
        output_schema: Expected output schema
        system_prompt: Optional system prompt
        provider: API provider to use

    Returns:
        Structured response data
    """
    config = ClaudeConfig.from_env(provider)

    async with ClaudeAPIClient(config) as client:
        return await client.call_claude_with_structured_output(
            prompt, output_schema, system_prompt
        )


if __name__ == "__main__":
    """Test the Claude API integration."""
    import asyncio

    async def test_claude_integration():
        """Test basic Claude integration."""
        config = ClaudeConfig.from_env()

        async with ClaudeAPIClient(config) as client:
            # Test simple call
            response = await client.call_claude(
                "What is KayGraph and how does it work?",
                system_prompt="You are a helpful AI assistant."
            )
            print("Simple call response:")
            print(response)

            # Test structured output
            schema = {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "key_features": {"type": "array", "items": {"type": "string"}},
                    "use_cases": {"type": "array", "items": {"type": "string"}}
                }
            }

            structured_response = await client.call_claude_with_structured_output(
                "Analyze KayGraph and provide information about it.",
                schema
            )
            print("\nStructured response:")
            print(structured_response)

            # Print metrics
            print("\nMetrics:")
            print(client.get_metrics())

    # Run test
    asyncio.run(test_claude_integration())