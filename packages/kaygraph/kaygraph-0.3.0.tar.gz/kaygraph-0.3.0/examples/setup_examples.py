#!/usr/bin/env python3
"""Setup script for Claude Agent SDK + KayGraph examples.

This script helps users set up their environment for running the examples
by detecting the current setup, validating configurations, and creating
necessary configuration files.

Usage:
    python setup_examples.py                    # Interactive setup
    python setup_examples.py --check           # Check current configuration
    python setup_examples.py --provider io.net # Setup for specific provider
    python setup_examples.py --demo            # Run demo with mock configuration
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from claude_config_utils import (
        Provider,
        setup_claude_config,
        validate_configuration,
        create_env_file,
        create_config_file,
        print_configuration_status,
        get_available_models,
        list_available_providers
    )
except ImportError as e:
    print(f"Error importing configuration utilities: {e}")
    print("Please install required dependencies:")
    print("pip install claude-agent-sdk kaygraph")
    sys.exit(1)


def check_dependencies() -> Dict[str, bool]:
    """Check if required dependencies are installed."""
    dependencies = {
        "claude_agent_sdk": False,
        "kaygraph": False,
        "aiohttp": False,
        "sklearn": False,
        "numpy": False
    }

    try:
        import claude_agent_sdk
        dependencies["claude_agent_sdk"] = True
    except ImportError:
        pass

    try:
        import kaygraph
        dependencies["kaygraph"] = True
    except ImportError:
        pass

    try:
        import aiohttp
        dependencies["aiohttp"] = True
    except ImportError:
        pass

    try:
        import sklearn
        dependencies["sklearn"] = True
    except ImportError:
        pass

    try:
        import numpy
        dependencies["numpy"] = True
    except ImportError:
        pass

    return dependencies


def install_dependencies():
    """Install missing dependencies."""
    print("Installing missing dependencies...")

    basic_deps = ["claude-agent-sdk", "kaygraph", "aiohttp"]
    optional_deps = ["scikit-learn", "numpy"]

    # Install basic dependencies
    basic_cmd = f"pip install {' '.join(basic_deps)}"
    print(f"Running: {basic_cmd}")
    os.system(basic_cmd)

    # Install optional dependencies for RAG examples
    optional_cmd = f"pip install {' '.join(optional_deps)}"
    print(f"Running: {optional_cmd}")
    os.system(optional_cmd)


def interactive_provider_setup() -> Provider:
    """Interactive provider selection and setup."""
    print("\n" + "="*50)
    print("Claude Agent SDK + KayGraph Setup")
    print("="*50)

    print("\nAvailable providers:")
    providers = list_available_providers()

    for i, provider_info in enumerate(providers, 1):
        status = "✅ Configured" if provider_info["configured"] else "❌ Not configured"
        print(f"  {i}. {provider_info['name']} - {status}")

    while True:
        try:
            choice = input(f"\nSelect provider (1-{len(providers)}) or 'q' to quit: ")
            if choice.lower() == 'q':
                sys.exit(0)

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(providers):
                selected_provider = providers[choice_idx]
                provider_name = selected_provider["name"]
                provider = Provider(provider_name)
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    print(f"\nSelected provider: {provider_name}")

    # Get API key
    api_key_prompt = {
        Provider.ANTHROPIC.value: "Enter your Anthropic API key (sk-ant-...): ",
        Provider.IO_NET.value: "Enter your io.net API key (io-v2-...): ",
        Provider.Z_AI.value: "Enter your Z.ai auth token: "
    }

    api_key = input(api_key_prompt.get(provider_name, "Enter API key: ")).strip()
    if not api_key:
        print("API key cannot be empty.")
        return interactive_provider_setup()

    # Get model selection
    available_models = get_available_models(provider)
    print(f"\nAvailable models for {provider_name}:")
    for i, model in enumerate(available_models, 1):
        print(f"  {i}. {model.name} - {model.description}")

    model_choice = input(f"\nSelect model (1-{len(available_models)}) or press Enter for default: ")
    selected_model = None

    if model_choice.strip():
        try:
            choice_idx = int(model_choice) - 1
            if 0 <= choice_idx < len(available_models):
                selected_model = available_models[choice_idx].name
        except ValueError:
            print("Invalid choice. Using default model.")

    # Create configuration files
    print("\nCreating configuration files...")

    # Create .env file
    env_path = create_env_file(
        provider=provider,
        api_key=api_key,
        model=selected_model,
        output_path=".env.claude"
    )
    print(f"✅ Created environment file: {env_path}")

    # Create JSON config file
    config_path = create_config_file(
        provider=provider,
        model=selected_model,
        output_path="claude_config.json"
    )
    print(f"✅ Created configuration file: {config_path}")

    # Set environment variables for current session
    print("\nSetting environment variables for current session...")
    if provider == Provider.ANTHROPIC:
        os.environ["ANTHROPIC_API_KEY"] = api_key
    elif provider == Provider.IO_NET:
        os.environ["API_KEY"] = api_key
        os.environ["ANTHROPIC_BASE_URL"] = "https://api.intelligence.io.solutions/api/v1"
    elif provider == Provider.Z_AI:
        os.environ["ANTHROPIC_AUTH_TOKEN"] = api_key
        os.environ["ANTHROPIC_BASE_URL"] = "https://api.z.ai/api/anthropic"

    if selected_model:
        os.environ["ANTHROPIC_MODEL"] = selected_model

    print("✅ Environment variables set for current session")

    return provider


def setup_for_provider(provider_name: str):
    """Setup for a specific provider."""
    try:
        provider = Provider(provider_name)
    except ValueError:
        print(f"Unknown provider: {provider_name}")
        print(f"Available providers: {[p.value for p in Provider]}")
        return

    print(f"Setting up for provider: {provider_name}")

    # Provider-specific setup instructions
    setup_instructions = {
        Provider.ANTHROPIC.value: """
To set up Anthropic Claude:

1. Get your API key from: https://console.anthropic.com/
2. Set environment variable:
   export ANTHROPIC_API_KEY="sk-ant-api03-..."
3. Optional: Set model:
   export ANTHROPIC_MODEL="claude-3-sonnet-20240229"
        """,

        Provider.IO_NET.value: """
To set up io.net:

1. Get your API key from io.net dashboard
2. Set environment variables:
   export API_KEY="io-v2-..."
   export ANTHROPIC_BASE_URL="https://api.intelligence.io.solutions/api/v1"
3. Set model:
   export ANTHROPIC_MODEL="glm-4.6"
        """,

        Provider.Z_AI.value: """
To set up Z.ai:

1. Get your auth token from Z.ai
2. Set environment variables:
   export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
   export ANTHROPIC_AUTH_TOKEN="your-auth-token"
3. Set model:
   export ANTHROPIC_MODEL="glm-4.6"
        """
    }

    print(setup_instructions.get(provider_name, "No specific instructions available."))

    # Validate current setup
    validation = validate_configuration()
    if validation["valid"]:
        print("✅ Configuration is valid!")
    else:
        print("❌ Configuration issues found:")
        for error in validation["errors"]:
            print(f"  - {error}")


def create_demo_setup():
    """Create a demo setup with mock configuration."""
    print("Creating demo setup with mock configuration...")

    # Create demo configuration
    demo_config = {
        "provider": "demo",
        "model": "demo-model",
        "base_url": "https://api.demo.com",
        "api_key": "demo-key",
        "max_tokens": 1000,
        "temperature": 0.7,
        "demo_mode": True
    }

    # Create demo config file
    config_path = Path("claude_demo_config.json")
    config_path.write_text(json.dumps(demo_config, indent=2))
    print(f"✅ Created demo configuration: {config_path}")

    # Create demo environment file
    demo_env = """# Demo Configuration for Claude Agent SDK + KayGraph
# This is a mock configuration for testing purposes

DEMO_MODE=true
DEMO_PROVIDER=demo
DEMO_MODEL=demo-model
DEMO_API_KEY=demo-key-for-testing-only
"""

    env_path = Path(".env.demo")
    env_path.write_text(demo_env)
    print(f"✅ Created demo environment file: {env_path}")

    print("\nDemo setup complete!")
    print("Note: This uses mock configuration and will not make real API calls.")
    print("To use real APIs, please run the interactive setup with:")
    print("  python setup_examples.py")


def run_example_test():
    """Run a quick test to verify the setup."""
    print("\nRunning setup verification test...")

    try:
        # Test basic imports
        from kaygraph_claude_base import ClaudeNode, ClaudeConfig
        print("✅ Basic imports successful")

        # Test configuration
        config = ClaudeConfig.from_env()
        print(f"✅ Configuration loaded: model={config.model}")

        # Test node creation
        node = ClaudeNode(prompt_template="Test: {input}")
        print("✅ Claude node created successfully")

        # Test graph creation
        from kaygraph import Graph
        graph = Graph(nodes={"test": node})
        print("✅ Graph created successfully")

        print("\n🎉 Setup verification passed!")
        print("You can now run the examples:")
        print("  python claude_chat_agent.py basic_chat")
        print("  python claude_reasoning_workflow.py problem_analysis")
        print("  python claude_tool_agent.py multi_tool_agent")

    except Exception as e:
        print(f"❌ Setup verification failed: {e}")
        print("Please check your configuration and try again.")


def main():
    """Main setup function."""
    parser = argparse.ArgumentParser(description="Setup Claude Agent SDK + KayGraph examples")
    parser.add_argument("--check", action="store_true", help="Check current configuration")
    parser.add_argument("--provider", choices=[p.value for p in Provider], help="Setup for specific provider")
    parser.add_argument("--demo", action="store_true", help="Create demo setup with mock configuration")
    parser.add_argument("--install-deps", action="store_true", help="Install missing dependencies")

    args = parser.parse_args()

    print("Claude Agent SDK + KayGraph Examples Setup")
    print("=" * 50)

    # Check dependencies
    print("Checking dependencies...")
    deps = check_dependencies()
    missing_deps = [dep for dep, installed in deps.items() if not installed]

    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        if args.install_deps or input("Install missing dependencies? (y/n): ").lower() == 'y':
            install_dependencies()
            print("✅ Dependencies installed")
        else:
            print("⚠️  Some examples may not work without all dependencies")
    else:
        print("✅ All dependencies installed")

    # Handle different modes
    if args.demo:
        create_demo_setup()
        return

    if args.provider:
        setup_for_provider(args.provider)
        return

    if args.check:
        print("\nCurrent configuration status:")
        print_configuration_status()
        return

    # Interactive setup
    provider = interactive_provider_setup()

    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)

    print(f"\n✅ Provider: {provider.value}")
    print("✅ Configuration files created")
    print("✅ Environment variables set")

    # Test the setup
    if input("\nRun setup verification test? (y/n): ").lower() == 'y':
        run_example_test()

    print("\nNext steps:")
    print("1. Try running an example:")
    print("   python claude_chat_agent.py basic_chat")
    print("\n2. Explore all examples:")
    print("   python claude_chat_agent.py --help")
    print("   python claude_reasoning_workflow.py --help")
    print("   python claude_tool_agent.py --help")
    print("   python claude_multi_agent_system.py --help")
    print("\n3. Check configuration status:")
    print("   python claude_config_utils.py")


if __name__ == "__main__":
    main()