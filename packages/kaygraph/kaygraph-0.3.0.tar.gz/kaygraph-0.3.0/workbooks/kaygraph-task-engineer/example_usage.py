#!/usr/bin/env python3
"""
Example usage of KayGraph Task Engineer with different configurations
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import build_task_engineer
from config import get_model_config, MODELS
import json

def demonstrate_model_configuration():
    """Show how to configure different models"""
    
    print("=== Available Model Configurations ===\n")
    
    for model_name, config in MODELS.items():
        print(f"{model_name.upper()} Model:")
        print(f"  Name: {config['name']}")
        print(f"  Temperature: {config['temperature']}")
        print(f"  Max Tokens: {config['max_tokens']}")
        print(f"  API Key Env: {config['api_key_env']}")
        print()
    
    # Example: Configure for specific use case
    print("=== Custom Configuration Example ===\n")
    
    # For security analysis, use lower temperature
    security_config = get_model_config("fast")
    security_config["temperature"] = 0.2  # More deterministic for security
    print(f"Security Analysis Config: {json.dumps(security_config, indent=2)}\n")
    
    # For creative tasks, use higher temperature
    creative_config = get_model_config("fast")
    creative_config["temperature"] = 0.8
    print(f"Creative Task Config: {json.dumps(creative_config, indent=2)}\n")


def demonstrate_security_tasks():
    """Examples of security-focused tasks"""
    
    print("=== Security Task Examples ===\n")
    
    security_tasks = [
        {
            "name": "Git Diff Security Check",
            "task": "Check the last commit for hardcoded credentials, missing auth, or SQL injection risks",
            "context": {"commit_range": "HEAD~1..HEAD"}
        },
        {
            "name": "Authentication Audit",
            "task": "Find all API endpoints in the codebase and check if they have proper authentication",
            "context": {"framework": "fastapi", "target_files": ["api/", "routes/"]}
        },
        {
            "name": "Secrets Scanner",
            "task": "Search for hardcoded passwords, API keys, or tokens in config files",
            "context": {"file_patterns": ["*.conf", "*.env", "*.config", "*.yml"]}
        },
        {
            "name": "Security Regression Check",
            "task": "Compare security between main branch and feature branch for any regressions",
            "context": {"base_branch": "main", "feature_branch": "feature/new-api"}
        }
    ]
    
    graph = build_task_engineer()
    
    # Run the first security task as demo
    task = security_tasks[0]
    print(f"Running: {task['name']}")
    print(f"Task: {task['task']}\n")
    
    shared = {
        "task": task["task"],
        "context": task["context"]
    }
    
    # Uncomment to actually run:
    # graph.run(shared, start_node="analyzer")


def demonstrate_generalized_tasks():
    """Show how the system generalizes to various tasks"""
    
    print("=== Generalized Task Examples ===\n")
    
    tasks = [
        # File Management
        {
            "category": "File Management",
            "task": "Find all log files older than 30 days that can be archived",
            "generalizes_to": ["temp file cleanup", "cache management", "backup rotation"]
        },
        
        # Code Quality
        {
            "category": "Code Quality",
            "task": "Find all functions longer than 50 lines and suggest refactoring",
            "generalizes_to": ["complexity analysis", "code smell detection", "refactoring opportunities"]
        },
        
        # Documentation
        {
            "category": "Documentation",
            "task": "Find all public functions missing docstrings and generate them",
            "generalizes_to": ["API doc generation", "README updates", "comment generation"]
        },
        
        # Dependency Management
        {
            "category": "Dependencies",
            "task": "Check for unused imports and outdated dependencies",
            "generalizes_to": ["package audit", "security updates", "import optimization"]
        },
        
        # Performance
        {
            "category": "Performance",
            "task": "Find all database queries in loops and suggest optimization",
            "generalizes_to": ["N+1 detection", "cache opportunities", "query optimization"]
        }
    ]
    
    for task_info in tasks:
        print(f"{task_info['category']}:")
        print(f"  Task: {task_info['task']}")
        print(f"  Generalizes to: {', '.join(task_info['generalizes_to'])}")
        print()


def demonstrate_prompt_customization():
    """Show how to customize prompts for specific needs"""
    
    print("=== Custom Prompt Examples ===\n")
    
    from config import PROMPTS
    
    # Add custom prompt for specific use case
    custom_prompts = {
        "code_review": {
            "system": "You are a senior engineer reviewing code for a financial system. Focus on security, correctness, and compliance.",
            "review_pr": """Review this pull request for:
1. Security vulnerabilities (especially around money handling)
2. Business logic correctness
3. Regulatory compliance (PCI, SOX)
4. Performance implications
5. Test coverage

PR Diff:
{diff_content}

Provide actionable feedback with specific line references."""
        },
        
        "migration_planning": {
            "system": "You are a migration specialist helping plan complex system migrations.",
            "analyze": """Analyze this codebase for migration from {source_tech} to {target_tech}:

Files:
{file_list}

Create a migration plan including:
1. Risk assessment
2. Dependency mapping  
3. Phase-by-phase approach
4. Rollback strategy
5. Testing requirements"""
        }
    }
    
    print("Custom Security Review Prompt:")
    print(custom_prompts["code_review"]["review_pr"][:200] + "...\n")
    
    print("Custom Migration Prompt:")
    print(custom_prompts["migration_planning"]["analyze"][:200] + "...\n")


def main():
    """Run all demonstrations"""
    
    print("🚀 KayGraph Task Engineer - Advanced Examples\n")
    
    demonstrate_model_configuration()
    print("\n" + "="*60 + "\n")
    
    demonstrate_security_tasks()
    print("\n" + "="*60 + "\n")
    
    demonstrate_generalized_tasks()
    print("\n" + "="*60 + "\n")
    
    demonstrate_prompt_customization()
    
    print("\n✅ Examples complete! The system can handle these and many more task types.")
    print("\nTo use with Cerebras API:")
    print("1. Set CEREBRAS_API_KEY environment variable")
    print("2. Uncomment the API calls in utils/llm_cerebras.py")
    print("3. Run tasks with: python main.py")


if __name__ == "__main__":
    main()