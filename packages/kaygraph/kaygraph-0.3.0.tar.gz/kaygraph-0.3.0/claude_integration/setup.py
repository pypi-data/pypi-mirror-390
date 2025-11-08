#!/usr/bin/env python
"""
Claude + KayGraph Integration Setup Script.

This script sets up the Claude integration with KayGraph,
installs dependencies, and verifies the configuration.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")


def check_python_version():
    """Check if Python version is 3.8+."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor} detected")
    return True


def check_kaygraph():
    """Check if KayGraph is installed."""
    try:
        import kaygraph
        print_success("KayGraph is installed")
        return True
    except ImportError:
        print_warning("KayGraph not found")
        return False


def install_dependencies(workbook: Optional[str] = None):
    """Install dependencies for workbooks."""
    base_deps = [
        "anthropic>=0.34.0",
        "httpx>=0.24.0",
        "pydantic>=2.5.0",
        "numpy>=1.24.0",
        "tenacity>=8.2.0",
        "python-dotenv>=1.0.0",
        "structlog>=24.1.0"
    ]

    workbook_deps = {
        "customer_support": [
            "nltk>=3.8.1",
            "textblob>=0.17.1",
            "pandas>=2.1.0",
            "redis>=5.0.0"
        ],
        "document_analysis": [
            "pypdf>=4.0.0",
            "python-docx>=1.1.0",
            "beautifulsoup4>=4.12.0",
            "markdown>=3.5.0",
            "chardet>=5.2.0"
        ],
        "conversation_memory": [
            "sqlalchemy>=2.0.0",
            "alembic>=1.13.0",
            "asyncpg>=0.29.0"
        ]
    }

    print_header("Installing Dependencies")

    # Install base dependencies
    print("Installing base dependencies...")
    for dep in base_deps:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", dep],
                check=True,
                capture_output=True
            )
            print_success(f"Installed {dep}")
        except subprocess.CalledProcessError as e:
            print_warning(f"Failed to install {dep}: {e}")

    # Install workbook-specific dependencies
    if workbook and workbook in workbook_deps:
        print(f"\nInstalling {workbook} dependencies...")
        for dep in workbook_deps[workbook]:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True
                )
                print_success(f"Installed {dep}")
            except subprocess.CalledProcessError as e:
                print_warning(f"Failed to install {dep}: {e}")


def check_api_keys():
    """Check for Claude API keys in environment."""
    print_header("Checking API Configuration")

    keys = {
        "ANTHROPIC_API_KEY": "Anthropic (Official)",
        "IOAI_API_KEY": "io.net",
        "Z_API_KEY": "Z.ai"
    }

    found = False
    for key, provider in keys.items():
        if os.getenv(key):
            print_success(f"{provider} API key found")
            found = True
        else:
            print_warning(f"{provider} API key not set ({key})")

    if not found:
        print_error("No Claude API keys found!")
        print("\nTo set an API key, run:")
        print(f"  export ANTHROPIC_API_KEY='your-key-here'")
        print(f"  # OR")
        print(f"  export IOAI_API_KEY='your-io-net-key'")
        print(f"  # OR")
        print(f"  export Z_API_KEY='your-z-ai-key'")
        return False

    return True


def create_env_file():
    """Create a template .env file."""
    env_template = """# Claude API Configuration
# Uncomment and set one of the following:

# Anthropic (Official)
# ANTHROPIC_API_KEY=sk-ant-...

# io.net
# IOAI_API_KEY=your-io-net-key
# IOAI_MODEL=claude-3.5-sonnet

# Z.ai
# Z_API_KEY=your-z-ai-key
# Z_MODEL=claude-3.5-sonnet

# Database Configuration (for conversation_memory)
# DATABASE_URL=sqlite:///conversation_memory.db
# DATABASE_URL=postgresql://user:pass@localhost/conversations

# Optional: OpenAI for embeddings
# OPENAI_API_KEY=sk-...

# Logging
LOG_LEVEL=INFO
"""

    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_template)
        print_success("Created .env template file")
        print("  Edit .env and add your API keys")
    else:
        print_warning(".env file already exists")


def test_claude_connection():
    """Test Claude API connection."""
    print_header("Testing Claude Connection")

    try:
        # Add parent directory to path for imports
        sys.path.insert(0, str(Path(__file__).parent))

        from shared_utils.claude_api import ClaudeAPIClient

        client = ClaudeAPIClient()
        print("Testing Claude API...")

        # Simple test prompt
        import asyncio
        async def test():
            try:
                response = await client.call_claude(
                    prompt="Say 'Hello from Claude!' in 5 words or less.",
                    max_tokens=20
                )
                return response
            except Exception as e:
                return None

        response = asyncio.run(test())

        if response:
            print_success(f"Claude responded: {response}")
            return True
        else:
            print_error("Failed to get response from Claude")
            return False

    except Exception as e:
        print_error(f"Failed to test Claude: {e}")
        return False


def test_database_connection():
    """Test database connection for conversation_memory."""
    print_header("Testing Database Connection")

    try:
        # Add parent directory to path
        sys.path.insert(0, str(Path(__file__).parent))

        from conversation_memory.models import DatabaseManager

        # Test with SQLite
        db = DatabaseManager("sqlite:///test_setup.db")

        # Create test conversation
        import uuid
        test_conv = db.create_conversation(
            conversation_id=str(uuid.uuid4()),
            user_id="test_user",
            title="Test Conversation"
        )

        if test_conv:
            print_success("Database connection successful")
            print(f"  Created test conversation: {test_conv.conversation_id}")

            # Clean up test database
            os.remove("test_setup.db")
            return True

    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False


def list_workbooks():
    """List available workbooks."""
    print_header("Available Workbooks")

    workbooks = {
        "customer_support": {
            "description": "Automated customer service system",
            "features": ["Multi-channel support", "Sentiment analysis", "CRM integration"],
            "nodes": 9,
            "workflows": 5
        },
        "document_analysis": {
            "description": "Enterprise document processing",
            "features": ["Compliance checking", "Risk assessment", "Batch processing"],
            "nodes": 7,
            "workflows": 4
        },
        "conversation_memory": {
            "description": "Database-backed conversations with memory",
            "features": ["SQLite/PostgreSQL", "Session recovery", "Semantic search"],
            "nodes": 8,
            "workflows": 5
        }
    }

    for name, info in workbooks.items():
        print(f"{Colors.BOLD}{name}{Colors.ENDC}")
        print(f"  Description: {info['description']}")
        print(f"  Nodes: {info['nodes']}, Workflows: {info['workflows']}")
        print(f"  Features: {', '.join(info['features'][:3])}")
        print()


def run_demo(workbook: str):
    """Run a workbook demo."""
    print_header(f"Running {workbook} Demo")

    workbook_path = Path(__file__).parent / workbook
    if not workbook_path.exists():
        print_error(f"Workbook '{workbook}' not found")
        return False

    main_file = workbook_path / "main.py"
    if not main_file.exists():
        print_error(f"Demo file not found: {main_file}")
        return False

    try:
        print(f"Running {main_file}...")
        subprocess.run([sys.executable, str(main_file)], check=True)
        print_success(f"{workbook} demo completed")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Demo failed: {e}")
        return False


def main():
    """Main setup function."""
    print_header("Claude + KayGraph Integration Setup")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Check for KayGraph
    if not check_kaygraph():
        print("\nTo install KayGraph:")
        print("  pip install kaygraph")
        print("  # OR")
        print("  pip install -e /path/to/KayGraph")

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "install":
            workbook = sys.argv[2] if len(sys.argv) > 2 else None
            install_dependencies(workbook)

        elif command == "test":
            check_api_keys()
            test_claude_connection()
            test_database_connection()

        elif command == "demo":
            if len(sys.argv) > 2:
                run_demo(sys.argv[2])
            else:
                print_error("Please specify a workbook")
                list_workbooks()

        elif command == "list":
            list_workbooks()

        elif command == "env":
            create_env_file()

        else:
            print(f"Unknown command: {command}")

    else:
        # Interactive setup
        print("\n🚀 Welcome to Claude + KayGraph Integration!\n")

        # Create .env file
        create_env_file()

        # Check API keys
        has_keys = check_api_keys()

        # List workbooks
        list_workbooks()

        print_header("Setup Options")
        print("Run this script with:")
        print(f"  {Colors.BOLD}python setup.py install{Colors.ENDC} - Install all dependencies")
        print(f"  {Colors.BOLD}python setup.py install customer_support{Colors.ENDC} - Install specific workbook")
        print(f"  {Colors.BOLD}python setup.py test{Colors.ENDC} - Test Claude and database connections")
        print(f"  {Colors.BOLD}python setup.py demo customer_support{Colors.ENDC} - Run a workbook demo")
        print(f"  {Colors.BOLD}python setup.py list{Colors.ENDC} - List available workbooks")
        print(f"  {Colors.BOLD}python setup.py env{Colors.ENDC} - Create .env template")

        if not has_keys:
            print(f"\n{Colors.YELLOW}⚠️  Don't forget to set your API keys!{Colors.ENDC}")

        print(f"\n{Colors.GREEN}✅ Setup complete! Choose a workbook and start building.{Colors.ENDC}")


if __name__ == "__main__":
    main()