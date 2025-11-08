#!/usr/bin/env python3
"""Base Claude Integration Components for KayGraph.

This module provides the foundational components for integrating Claude Agent SDK with KayGraph,
including configuration management and base node classes.

Usage:
Import as a module in other examples:
    from kaygraph_claude_base import ClaudeNode, ClaudeConfig

Environment Variables:
    ANTHROPIC_BASE_URL - Custom Claude API endpoint (for io.net models)
    ANTHROPIC_AUTH_TOKEN - Authentication token for external API
    ANTHROPIC_MODEL - Model name to use (default: claude-3-sonnet-20240229)
"""

import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass

from kaygraph import Node, ValidatedNode, AsyncNode
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, query


@dataclass
class ClaudeConfig:
    """Configuration for Claude API integration."""

    model: str = "claude-3-sonnet-20240229"
    base_url: Optional[str] = None
    auth_token: Optional[str] = None
    max_tokens: int = 4000
    temperature: float = 0.7
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'ClaudeConfig':
        """Create configuration from environment variables."""
        return cls(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            base_url=os.getenv("ANTHROPIC_BASE_URL"),
            auth_token=os.getenv("ANTHROPIC_AUTH_TOKEN"),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
        )

    def to_client_kwargs(self) -> Dict[str, Any]:
        """Convert to SDK client keyword arguments."""
        kwargs = {}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        if self.auth_token:
            kwargs["api_key"] = self.auth_token
        return kwargs

    def to_options(self) -> ClaudeAgentOptions:
        """Convert to ClaudeAgentOptions."""
        return ClaudeAgentOptions(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system_prompt=self.system_prompt,
            allowed_tools=self.tools,
        )


class ClaudeNode(Node):
    """Base KayGraph node for Claude API integration.

    This node provides a simple interface for making Claude API calls
    within a KayGraph workflow.
    """

    def __init__(
        self,
        prompt_template: str,
        config: Optional[ClaudeConfig] = None,
        tools: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.prompt_template = prompt_template
        self.config = config or ClaudeConfig.from_env()
        self.tools = tools
        self.system_prompt = system_prompt
        self._client = None

    @property
    def client(self) -> ClaudeSDKClient:
        """Lazy-loaded Claude client."""
        if self._client is None:
            self._client = ClaudeSDKClient(**self.config.to_client_kwargs())
        return self._client

    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare the prompt using shared context."""
        try:
            return self.prompt_template.format(**shared)
        except KeyError as e:
            raise ValueError(f"Missing required context variable: {e}")

    def exec(self, prepared_prompt: str) -> str:
        """Execute Claude API call."""
        options = ClaudeAgentOptions(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system_prompt=self.system_prompt,
            allowed_tools=self.tools,
        )

        response_parts = []
        for message in query(prepared_prompt, options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)

        return "".join(response_parts)

    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store Claude's response in shared context."""
        shared["claude_response"] = exec_res
        shared["claude_prompt"] = prep_res
        return "default"


class AsyncClaudeNode(AsyncNode):
    """Async version of ClaudeNode for better performance."""

    def __init__(
        self,
        prompt_template: str,
        config: Optional[ClaudeConfig] = None,
        tools: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.prompt_template = prompt_template
        self.config = config or ClaudeConfig.from_env()
        self.tools = tools
        self.system_prompt = system_prompt
        self._client = None

    @property
    def client(self) -> ClaudeSDKClient:
        """Lazy-loaded Claude client."""
        if self._client is None:
            self._client = ClaudeSDKClient(**self.config.to_client_kwargs())
        return self._client

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare the prompt using shared context."""
        try:
            return self.prompt_template.format(**shared)
        except KeyError as e:
            raise ValueError(f"Missing required context variable: {e}")

    async def exec(self, prepared_prompt: str) -> str:
        """Execute Claude API call asynchronously."""
        options = ClaudeAgentOptions(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            system_prompt=self.system_prompt,
            allowed_tools=self.tools,
        )

        response_parts = []
        async for message in query(prepared_prompt, options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)

        return "".join(response_parts)

    async def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store Claude's response in shared context."""
        shared["claude_response"] = exec_res
        shared["claude_prompt"] = prep_res
        return "default"


class ValidatedClaudeNode(ValidatedNode):
    """ClaudeNode with input/output validation."""

    def __init__(
        self,
        prompt_template: str,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        config: Optional[ClaudeConfig] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.prompt_template = prompt_template
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        self.config = config or ClaudeConfig.from_env()
        self._client = None

    @property
    def client(self) -> ClaudeSDKClient:
        """Lazy-loaded Claude client."""
        if self._client is None:
            self._client = ClaudeSDKClient(**self.config.to_client_kwargs())
        return self._client

    def validate_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema."""
        # Simple validation - in real usage, you might use jsonschema or pydantic
        if self.input_schema:
            required_fields = self.input_schema.get("required", [])
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
        return data

    def validate_output(self, data: str) -> str:
        """Validate output data."""
        # Add any output validation logic here
        return data

    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare and validate prompt."""
        validated_shared = self.validate_input(shared)
        try:
            return self.prompt_template.format(**validated_shared)
        except KeyError as e:
            raise ValueError(f"Missing required context variable: {e}")

    def exec(self, prepared_prompt: str) -> str:
        """Execute Claude API call with validation."""
        options = ClaudeAgentOptions(
            model=self.config.model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )

        response_parts = []
        for message in query(prepared_prompt, options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)

        raw_response = "".join(response_parts)
        return self.validate_output(raw_response)

    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> str:
        """Store validated response."""
        shared["claude_response"] = exec_res
        shared["claude_prompt"] = prep_res
        return "default"


def create_claude_config_from_io_net() -> ClaudeConfig:
    """Create ClaudeConfig for io.net models."""
    return ClaudeConfig(
        model="glm-4.6",  # Default io.net model
        base_url="https://api.intelligence.io.solutions/api/v1",
        auth_token=os.getenv("API_KEY"),  # io.net API key
        max_tokens=4000,
        temperature=0.7,
    )


def create_claude_config_from_z_ai() -> ClaudeConfig:
    """Create ClaudeConfig for Z.ai API."""
    return ClaudeConfig(
        model="glm-4.6",  # Default Z.ai model
        base_url="https://api.z.ai/api/anthropic",
        auth_token=os.getenv("ANTHROPIC_AUTH_TOKEN"),
        max_tokens=4000,
        temperature=0.7,
    )


# Export main components
__all__ = [
    'ClaudeConfig',
    'ClaudeNode',
    'AsyncClaudeNode',
    'ValidatedClaudeNode',
    'create_claude_config_from_io_net',
    'create_claude_config_from_z_ai',
]