"""
Configuration for Task Engineer - Models and Prompts
"""

import os
from typing import Dict, Any

# Model Configuration
MODELS = {
    "fast": {
        "name": "qwen-3-32b",
        "base_url": "https://api.cerebras.ai/v1",
        "api_key_env": "CEREBRAS_API_KEY",
        "temperature": 0.6,
        "top_p": 0.95,
        "max_tokens": 4096
    },
    "large": {
        "name": "qwen-3-coder-480b",
        "base_url": "https://api.cerebras.ai/v1", 
        "api_key_env": "CEREBRAS_API_KEY",
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 8192
    },
    "local": {
        "name": "llama3.2:3b",
        "base_url": "http://localhost:11434/v1",
        "api_key_env": None,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 2048
    }
}

# Task-specific prompts
PROMPTS = {
    "security_analysis": {
        "system": """You are a security expert analyzing code changes for vulnerabilities. Focus on:
1. Authentication/authorization issues
2. Hardcoded secrets or credentials
3. SQL injection risks
4. XSS vulnerabilities
5. Insecure configurations
6. Missing input validation
7. Exposed sensitive data""",
        
        "git_diff_analysis": """Analyze this git diff for security issues:

{diff_content}

Look for:
- Missing authentication checks
- Hardcoded passwords, API keys, or secrets
- Removed security controls
- New endpoints without proper authorization
- Database queries without parameterization
- Exposed sensitive information in logs/errors
- Insecure default configurations

Format your response as JSON:
{{
    "severity": "critical|high|medium|low|none",
    "issues": [
        {{
            "type": "issue_type",
            "severity": "critical|high|medium|low",
            "file": "filename",
            "line": "line_number or range",
            "description": "what's wrong",
            "recommendation": "how to fix it"
        }}
    ],
    "summary": "overall assessment"
}}""",
        
        "commit_comparison": """Compare these commits for security regressions:

Old commit: {old_commit}
New commit: {new_commit}

Changes:
{changes}

Identify any security degradation or new vulnerabilities introduced."""
    },
    
    "code_quality": {
        "system": "You are a code quality expert focusing on maintainability, performance, and best practices.",
        
        "analyze": """Analyze this code for quality issues:

{code}

Check for:
- Code smells and anti-patterns
- Performance bottlenecks
- Maintainability issues
- Missing error handling
- Resource leaks
- Thread safety issues"""
    },
    
    "task_planning": {
        "system": "You are a task planning assistant that breaks down complex tasks into executable steps.",
        
        "decompose": """Break down this task into specific, actionable steps:

Task: {task}
Context: {context}

Create a step-by-step plan where each step:
1. Has a clear, single responsibility
2. Specifies inputs and outputs
3. Can be verified/tested
4. Indicates if it needs human review

Use this format:
{{
    "task_summary": "what we're doing",
    "steps": [
        {{
            "id": "step_1",
            "action": "specific action",
            "target": "what to act on",
            "validation": "how to verify success",
            "automated": true/false
        }}
    ]
}}"""
    }
}

# Security patterns to detect
SECURITY_PATTERNS = {
    "hardcoded_secrets": [
        r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
        r'(?i)(api_key|apikey|api_token)\s*=\s*["\'][^"\']+["\']',
        r'(?i)(secret|token)\s*=\s*["\'][^"\']+["\']',
        r'(?i)aws_access_key_id\s*=\s*["\'][^"\']+["\']',
        r'(?i)private_key\s*=\s*["\'][^"\']+["\']'
    ],
    "missing_auth": [
        r'@app\.(get|post|put|delete|patch)\s*\([^)]*\)\s*\n\s*def\s+\w+\s*\([^)]*\):(?!.*(?:current_user|require_auth|login_required|authenticate))',
        r'router\.(get|post|put|delete|patch)\s*\([^)]*\)\s*\n(?!.*dependencies.*Depends)',
        r'app\.route\s*\([^)]*\)\s*\n\s*def\s+\w+\s*\([^)]*\):(?!.*(?:@login_required|@require_auth))'
    ],
    "sql_injection": [
        r'(?i)(?:execute|query)\s*\(\s*["\'].*%[s|d].*["\'].*%',
        r'(?i)(?:execute|query)\s*\(\s*[^,]+\+\s*[^,]+\)',
        r'(?i)(?:execute|query)\s*\(\s*f["\'].*\{.*\}.*["\']'
    ],
    "exposed_data": [
        r'(?i)print\s*\(.*(?:password|token|secret|key).*\)',
        r'(?i)(?:logger|log)\.\w+\s*\(.*(?:password|token|secret|key).*\)',
        r'(?i)return\s+.*(?:password_hash|secret_key|api_key)'
    ]
}

# File patterns for different analyses
FILE_PATTERNS = {
    "config_files": ["*.conf", "*.config", "*.ini", "*.env", "*.yaml", "*.yml", "*.toml"],
    "code_files": ["*.py", "*.js", "*.ts", "*.java", "*.go", "*.rb", "*.php"],
    "sensitive_files": [".env*", "*secret*", "*credential*", "*key*", "*.pem", "*.key"],
    "api_files": ["*api*.py", "*route*.py", "*controller*.py", "*endpoint*.py", "*view*.py"]
}

def get_model_config(model_type: str = "fast") -> Dict[str, Any]:
    """Get model configuration"""
    return MODELS.get(model_type, MODELS["fast"])

def get_prompt(category: str, prompt_type: str) -> str:
    """Get specific prompt template"""
    return PROMPTS.get(category, {}).get(prompt_type, "")

def get_security_patterns(pattern_type: str) -> list:
    """Get security detection patterns"""
    return SECURITY_PATTERNS.get(pattern_type, [])