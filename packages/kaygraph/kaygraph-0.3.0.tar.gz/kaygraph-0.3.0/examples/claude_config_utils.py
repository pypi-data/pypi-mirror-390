#!/usr/bin/env python3
"""Configuration Utilities for Claude Agent SDK with KayGraph.

This module provides utilities for configuring Claude Agent SDK to work with
different providers (Anthropic, io.net, Z.ai) and managing environment setups.

Usage:
    from claude_config_utils import (
        setup_claude_config,
        get_available_models,
        validate_configuration,
        create_config_file
    )

Environment Variables Supported:
    # Claude API (default)
    ANTHROPIC_API_KEY - Anthropic API key
    ANTHROPIC_MODEL - Model name (default: claude-3-sonnet-20240229)

    # io.net configuration
    API_KEY - io.net API key
    ANTHROPIC_BASE_URL - https://api.intelligence.io.solutions/api/v1
    ANTHROPIC_MODEL - Model from io.net (e.g., glm-4.6)

    # Z.ai configuration
    ANTHROPIC_BASE_URL - https://api.z.ai/api/anthropic
    ANTHROPIC_AUTH_TOKEN - Z.ai authentication token
    ANTHROPIC_MODEL - Model from Z.ai (e.g., glm-4.6)

    # Embedding configuration
    EMBEDDING_MODEL - Embedding model name
    EMBEDDING_BASE_URL - Embedding API base URL
    EMBEDDING_API_KEY - Embedding API key
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from kaygraph_claude_base import ClaudeConfig


class Provider(Enum):
    """Supported API providers."""
    ANTHROPIC = "anthropic"
    IO_NET = "io_net"
    Z_AI = "z_ai"


class ModelCategory(Enum):
    """Model categories for different use cases."""
    CHAT = "chat"
    VISION = "vision"
    EMBEDDING = "embedding"
    REASONING = "reasoning"
    CODE = "code"


@dataclass
class ModelInfo:
    """Information about available models."""
    name: str
    provider: Provider
    category: ModelCategory
    max_tokens: int
    supports_vision: bool = False
    supports_tools: bool = True
    description: str = ""
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0


@dataclass
class ProviderConfig:
    """Configuration for a specific provider."""
    provider: Provider
    base_url: Optional[str] = None
    api_key_env: str = ""
    auth_token_env: str = ""
    default_model: str = ""
    requires_auth_token: bool = False


# Provider configurations
PROVIDER_CONFIGS = {
    Provider.ANTHROPIC: ProviderConfig(
        provider=Provider.ANTHROPIC,
        base_url="https://api.anthropic.com",
        api_key_env="ANTHROPIC_API_KEY",
        default_model="claude-3-sonnet-20240229"
    ),
    Provider.IO_NET: ProviderConfig(
        provider=Provider.IO_NET,
        base_url="https://api.intelligence.io.solutions/api/v1",
        api_key_env="API_KEY",
        default_model="glm-4.6"
    ),
    Provider.Z_AI: ProviderConfig(
        provider=Provider.Z_AI,
        base_url="https://api.z.ai/api/anthropic",
        api_key_env="ANTHROPIC_AUTH_TOKEN",
        auth_token_env="ANTHROPIC_AUTH_TOKEN",
        default_model="glm-4.6",
        requires_auth_token=True
    )
}

# Available models database
AVAILABLE_MODELS = {
    # Anthropic models
    "claude-3-sonnet-20240229": ModelInfo(
        name="claude-3-sonnet-20240229",
        provider=Provider.ANTHROPIC,
        category=ModelCategory.CHAT,
        max_tokens=200000,
        supports_vision=True,
        supports_tools=True,
        description="Balanced model for general use cases",
        cost_per_1k_input=3.0,
        cost_per_1k_output=15.0
    ),
    "claude-3-haiku-20240307": ModelInfo(
        name="claude-3-haiku-20240307",
        provider=Provider.ANTHROPIC,
        category=ModelCategory.CHAT,
        max_tokens=200000,
        supports_vision=True,
        supports_tools=True,
        description="Fast and compact model",
        cost_per_1k_input=0.25,
        cost_per_1k_output=1.25
    ),
    "claude-3-opus-20240229": ModelInfo(
        name="claude-3-opus-20240229",
        provider=Provider.ANTHROPIC,
        category=ModelCategory.CHAT,
        max_tokens=200000,
        supports_vision=True,
        supports_tools=True,
        description="Most capable model for complex tasks",
        cost_per_1k_input=15.0,
        cost_per_1k_output=75.0
    ),

    # io.net models
    "glm-4.6": ModelInfo(
        name="glm-4.6",
        provider=Provider.IO_NET,
        category=ModelCategory.CHAT,
        max_tokens=8192,
        supports_vision=False,
        supports_tools=True,
        description="General purpose model from Zhipu AI",
        cost_per_1k_input=0.5,
        cost_per_1k_output=1.5
    ),
    "Qwen2.5-VL-32B-Instruct": ModelInfo(
        name="Qwen2.5-VL-32B-Instruct",
        provider=Provider.IO_NET,
        category=ModelCategory.VISION,
        max_tokens=32768,
        supports_vision=True,
        supports_tools=True,
        description="Vision-language model from Alibaba",
        cost_per_1k_input=1.0,
        cost_per_1k_output=2.0
    ),
    "DeepSeek-R1-0528": ModelInfo(
        name="DeepSeek-R1-0528",
        provider=Provider.IO_NET,
        category=ModelCategory.REASONING,
        max_tokens=65536,
        supports_vision=False,
        supports_tools=True,
        description="Advanced reasoning model",
        cost_per_1k_input=0.8,
        cost_per_1k_output=2.4
    ),
    "Llama-3.3-70B-Instruct": ModelInfo(
        name="Llama-3.3-70B-Instruct",
        provider=Provider.IO_NET,
        category=ModelCategory.CHAT,
        max_tokens=131072,
        supports_vision=False,
        supports_tools=True,
        description="Meta's latest instruction model",
        cost_per_1k_input=0.6,
        cost_per_1k_output=1.8
    ),
    "Qwen3-Next-80B-A3B-Instruct": ModelInfo(
        name="Qwen3-Next-80B-A3B-Instruct",
        provider=Provider.IO_NET,
        category=ModelCategory.CHAT,
        max_tokens=32768,
        supports_vision=False,
        supports_tools=True,
        description="Next generation Qwen model",
        cost_per_1k_input=0.9,
        cost_per_1k_output=2.7
    ),

    # Embedding models
    "BAAI/bge-multilingual-gemma2": ModelInfo(
        name="BAAI/bge-multilingual-gemma2",
        provider=Provider.IO_NET,
        category=ModelCategory.EMBEDDING,
        max_tokens=8192,
        supports_vision=False,
        supports_tools=False,
        description="Multilingual embedding model",
        cost_per_1k_input=0.1,
        cost_per_1k_output=0.0
    )
}


def detect_provider() -> Provider:
    """Detect the provider based on environment variables."""
    # Check for io.net configuration
    if os.getenv("API_KEY") and os.getenv("ANTHROPIC_BASE_URL") == "https://api.intelligence.io.solutions/api/v1":
        return Provider.IO_NET

    # Check for Z.ai configuration
    if os.getenv("ANTHROPIC_BASE_URL") == "https://api.z.ai/api/anthropic":
        return Provider.Z_AI

    # Default to Anthropic
    return Provider.ANTHROPIC


def get_provider_config(provider: Provider) -> ProviderConfig:
    """Get configuration for a specific provider."""
    return PROVIDER_CONFIGS.get(provider, PROVIDER_CONFIGS[Provider.ANTHROPIC])


def validate_provider_config(provider: Provider) -> Dict[str, Any]:
    """Validate configuration for a provider."""
    config = get_provider_config(provider)
    validation_result = {
        "provider": provider.value,
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # Check API key
    api_key = os.getenv(config.api_key_env)
    if not api_key:
        validation_result["valid"] = False
        validation_result["errors"].append(f"Missing environment variable: {config.api_key_env}")

    # Check auth token if required
    if config.requires_auth_token:
        auth_token = os.getenv(config.auth_token_env)
        if not auth_token:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Missing environment variable: {config.auth_token_env}")

    # Check model availability
    model = os.getenv("ANTHROPIC_MODEL", config.default_model)
    if model not in AVAILABLE_MODELS:
        validation_result["warnings"].append(f"Model '{model}' not in known models list")

    return validation_result


def setup_claude_config(
    provider: Optional[Provider] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    **kwargs
) -> ClaudeConfig:
    """Setup Claude configuration with automatic provider detection."""

    # Detect provider if not specified
    if provider is None:
        provider = detect_provider()

    # Get provider configuration
    provider_config = get_provider_config(provider)

    # Use defaults from environment or provider config
    if model is None:
        model = os.getenv("ANTHROPIC_MODEL", provider_config.default_model)

    if base_url is None:
        base_url = os.getenv("ANTHROPIC_BASE_URL", provider_config.base_url)

    # Get API key
    if api_key is None:
        if provider == Provider.Z_AI:
            api_key = os.getenv(provider_config.auth_token_env)
        else:
            api_key = os.getenv(provider_config.api_key_env)

    # Create configuration
    config = ClaudeConfig(
        model=model,
        base_url=base_url,
        auth_token=api_key,
        **kwargs
    )

    return config


def get_available_models(
    provider: Optional[Provider] = None,
    category: Optional[ModelCategory] = None,
    supports_vision: Optional[bool] = None,
    supports_tools: Optional[bool] = None
) -> List[ModelInfo]:
    """Get available models filtered by criteria."""
    models = list(AVAILABLE_MODELS.values())

    # Filter by provider
    if provider:
        models = [m for m in models if m.provider == provider]

    # Filter by category
    if category:
        models = [m for m in models if m.category == category]

    # Filter by vision support
    if supports_vision is not None:
        models = [m for m in models if m.supports_vision == supports_vision]

    # Filter by tool support
    if supports_tools is not None:
        models = [m for m in models if m.supports_tools == supports_tools]

    return sorted(models, key=lambda m: (m.provider.value, m.name))


def get_model_info(model_name: str) -> Optional[ModelInfo]:
    """Get information about a specific model."""
    return AVAILABLE_MODELS.get(model_name)


def estimate_cost(
    model_name: str,
    input_tokens: int,
    output_tokens: int
) -> Dict[str, float]:
    """Estimate cost for using a model."""
    model_info = get_model_info(model_name)
    if not model_info:
        return {"error": "Model not found"}

    input_cost = (input_tokens / 1000) * model_info.cost_per_1k_input
    output_cost = (output_tokens / 1000) * model_info.cost_per_1k_output
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "currency": "USD"
    }


def create_env_file(
    provider: Provider,
    api_key: str,
    output_path: str = ".env",
    model: Optional[str] = None,
    **additional_env
) -> str:
    """Create environment file for a provider."""
    provider_config = get_provider_config(provider)

    env_content = []
    env_content.append(f"# Claude Agent SDK Configuration")
    env_content.append(f"# Provider: {provider.value}")
    env_content.append(f"")

    # Basic configuration
    if provider == Provider.ANTHROPIC:
        env_content.append(f"ANTHROPIC_API_KEY={api_key}")
    elif provider == Provider.IO_NET:
        env_content.append(f"API_KEY={api_key}")
        env_content.append(f"ANTHROPIC_BASE_URL={provider_config.base_url}")
    elif provider == Provider.Z_AI:
        env_content.append(f"ANTHROPIC_AUTH_TOKEN={api_key}")
        env_content.append(f"ANTHROPIC_BASE_URL={provider_config.base_url}")

    # Model configuration
    if model:
        env_content.append(f"ANTHROPIC_MODEL={model}")
    else:
        env_content.append(f"ANTHROPIC_MODEL={provider_config.default_model}")

    # Additional environment variables
    for key, value in additional_env.items():
        env_content.append(f"{key}={value}")

    # Write to file
    env_file = Path(output_path)
    env_file.write_text("\n".join(env_content))

    return str(env_file.absolute())


def create_config_file(
    provider: Provider,
    output_path: str = "claude_config.json",
    **config_kwargs
) -> str:
    """Create JSON configuration file."""

    # Create configuration
    config = setup_claude_config(provider=provider, **config_kwargs)

    # Convert to dictionary
    config_dict = asdict(config)
    config_dict["provider"] = provider.value

    # Add additional metadata
    config_dict["created_at"] = "2024-01-01T00:00:00Z"
    config_dict["version"] = "1.0.0"

    # Write to file
    config_file = Path(output_path)
    config_file.write_text(json.dumps(config_dict, indent=2))

    return str(config_file.absolute())


def validate_configuration() -> Dict[str, Any]:
    """Validate the current configuration."""
    provider = detect_provider()
    validation_result = validate_provider_config(provider)

    # Add additional information
    validation_result["detected_provider"] = provider.value
    validation_result["current_model"] = os.getenv("ANTHROPIC_MODEL", get_provider_config(provider).default_model)

    # Add model information
    model_info = get_model_info(validation_result["current_model"])
    if model_info:
        validation_result["model_info"] = asdict(model_info)
    else:
        validation_result["warnings"].append(f"Model information not available for: {validation_result['current_model']}")

    return validation_result


def print_configuration_status():
    """Print current configuration status."""
    print("Claude Agent SDK Configuration Status")
    print("=" * 50)

    provider = detect_provider()
    print(f"Detected Provider: {provider.value}")

    validation = validate_configuration()
    print(f"Configuration Valid: {'✅ Yes' if validation['valid'] else '❌ No'}")

    if validation['errors']:
        print("\nErrors:")
        for error in validation['errors']:
            print(f"  ❌ {error}")

    if validation['warnings']:
        print("\nWarnings:")
        for warning in validation['warnings']:
            print(f"  ⚠️  {warning}")

    print(f"\nCurrent Model: {validation['current_model']}")

    if 'model_info' in validation:
        model_info = validation['model_info']
        print(f"  Category: {model_info['category']}")
        print(f"  Max Tokens: {model_info['max_tokens']}")
        print(f"  Vision Support: {'Yes' if model_info['supports_vision'] else 'No'}")
        print(f"  Tool Support: {'Yes' if model_info['supports_tools'] else 'No'}")


def list_available_providers() -> List[Dict[str, Any]]:
    """List all available providers with their status."""
    providers_info = []

    for provider in Provider:
        config = get_provider_config(provider)
        validation = validate_provider_config(provider)

        provider_info = {
            "name": provider.value,
            "base_url": config.base_url,
            "default_model": config.default_model,
            "configured": validation["valid"],
            "errors": validation["errors"],
            "available_models": len([m for m in AVAILABLE_MODELS.values() if m.provider == provider])
        }

        providers_info.append(provider_info)

    return providers_info


def get_recommended_model(
    use_case: str,
    provider: Optional[Provider] = None,
    budget_conscious: bool = False
) -> Optional[ModelInfo]:
    """Get recommended model for a specific use case."""

    # Define use case mappings
    use_case_mappings = {
        "chat": ModelCategory.CHAT,
        "conversation": ModelCategory.CHAT,
        "qa": ModelCategory.CHAT,
        "vision": ModelCategory.VISION,
        "image": ModelCategory.VISION,
        "embedding": ModelCategory.EMBEDDING,
        "search": ModelCategory.EMBEDDING,
        "reasoning": ModelCategory.REASONING,
        "complex": ModelCategory.REASONING,
        "code": ModelCategory.CODE,
        "programming": ModelCategory.CODE
    }

    category = use_case_mappings.get(use_case.lower(), ModelCategory.CHAT)

    # Get available models
    models = get_available_models(provider=provider, category=category)

    if not models:
        return None

    # Filter by budget consciousness
    if budget_conscious:
        models = [m for m in models if m.cost_per_1k_input < 1.0]

    # Sort by cost (cheapest first) and capability
    models.sort(key=lambda m: (m.cost_per_1k_input, m.max_tokens))

    # Return best balance of cost and capability
    return models[0] if models else None


# Export main functions
__all__ = [
    'Provider',
    'ModelCategory',
    'ModelInfo',
    'ProviderConfig',
    'detect_provider',
    'setup_claude_config',
    'get_available_models',
    'get_model_info',
    'validate_configuration',
    'create_env_file',
    'create_config_file',
    'estimate_cost',
    'print_configuration_status',
    'list_available_providers',
    'get_recommended_model'
]


if __name__ == "__main__":
    # Demo configuration utilities
    print("Claude Agent SDK Configuration Utilities")
    print("=" * 50)
    print_configuration_status()

    print(f"\nAvailable Providers:")
    for provider_info in list_available_providers():
        status = "✅ Configured" if provider_info["configured"] else "❌ Not configured"
        print(f"  {provider_info['name']}: {status} ({provider_info['available_models']} models)")

    print(f"\nRecommended Models:")
    for use_case in ["chat", "vision", "reasoning", "embedding"]:
        model = get_recommended_model(use_case, budget_conscious=True)
        if model:
            print(f"  {use_case.title()}: {model.name} (${model.cost_per_1k_input}/1K input)")
        else:
            print(f"  {use_case.title()}: No suitable model found")