#!/usr/bin/env python3
"""
Universal LLM implementation for OpenAI-compatible APIs.
Works with: OpenAI, Ollama, Groq, Together, Anyscale, any OpenAI-compatible API.

If no API key is set, assumes Ollama running locally.
No OpenAI package required - uses requests directly.
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional


def call_llm(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    messages: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Call any OpenAI-compatible LLM API.
    
    Environment variables:
    - OPENAI_API_KEY: API key (if not set, assumes Ollama)
    - OPENAI_BASE_URL: Custom base URL (default: auto-detect)
    - LLM_MODEL: Model to use (default: auto-detect)
    
    Args:
        prompt: User prompt
        system: System prompt (optional)
        model: Model override (optional)
        temperature: Response creativity (0-1)
        max_tokens: Max response length
        messages: Full message history (overrides prompt/system)
        
    Returns:
        LLM response text
    """
    # Get configuration from environment
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    
    # Auto-detect endpoint based on API key presence
    if not api_key:
        # No API key = Ollama local
        base_url = base_url or "http://localhost:11434/v1"
        api_key = "no-key-needed"
        model = model or os.environ.get("LLM_MODEL", "gemma3:4b")
    else:
        # Has API key = OpenAI or compatible
        base_url = base_url or "https://api.openai.com/v1"
        model = model or os.environ.get("LLM_MODEL", "gpt-4o-mini")
    
    # Build messages
    if messages is None:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # Make request
    try:
        response = requests.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            # Get error details
            try:
                error_data = response.json()
                error = error_data.get("error", {}).get("message", response.text)
            except:
                error = response.text
            
            # Handle common errors
            if "model" in error.lower() and "not found" in error.lower():
                available = suggest_models(base_url)
                return f"Error: Model '{model}' not found. Available: {available}"
            elif "api" in error.lower() and "key" in error.lower():
                return "Error: Invalid API key. Set OPENAI_API_KEY or remove it for Ollama."
            else:
                return f"Error {response.status_code}: {error}"
                
    except requests.ConnectionError:
        return (
            "Error: Cannot connect to LLM API.\n"
            "If using Ollama: Run 'ollama serve' first\n"
            "If using OpenAI: Check internet connection"
        )
    except requests.Timeout:
        return "Error: Request timed out. Try a shorter prompt or increase timeout."
    except Exception as e:
        return f"Error: {str(e)}"


def call_llm_json(
    prompt: str,
    schema: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get JSON response from LLM.
    
    Args:
        prompt: Prompt (will append JSON instruction)
        schema: Optional JSON schema to include
        **kwargs: Passed to call_llm
        
    Returns:
        Parsed JSON dict or {"error": "..."} on failure
    """
    json_prompt = prompt + "\n\nRespond with valid JSON only."
    
    if schema:
        json_prompt += f"\n\nFollow this schema:\n{json.dumps(schema, indent=2)}"
    
    # Lower temperature for structured output
    kwargs["temperature"] = kwargs.get("temperature", 0.3)
    
    response = call_llm(json_prompt, **kwargs)
    
    # Handle errors
    if response.startswith("Error"):
        return {"error": response}
    
    # Try to parse JSON
    try:
        # Look for JSON in response
        if "{" in response:
            start = response.find("{")
            end = response.rfind("}") + 1
            if end > start:
                return json.loads(response[start:end])
        
        # Try parsing entire response
        return json.loads(response)
        
    except json.JSONDecodeError:
        # Try extracting from markdown
        if "```json" in response:
            try:
                json_str = response.split("```json")[1].split("```")[0].strip()
                return json.loads(json_str)
            except:
                pass
        
        return {"error": "Could not parse JSON", "raw": response}


def suggest_models(base_url: str) -> str:
    """Suggest available models based on endpoint."""
    if "localhost" in base_url or "11434" in base_url:
        # Try to get Ollama models
        try:
            resp = requests.get("http://localhost:11434/api/tags", timeout=2)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    names = [m["name"] for m in models[:5]]
                    return ", ".join(names)
        except:
            pass
        return "Run 'ollama list' to see available models"
    elif "groq" in base_url:
        return "llama-3.1-8b-instant, mixtral-8x7b-32768"
    else:
        return "gpt-4o-mini, gpt-3.5-turbo, gpt-4"


def test_connection() -> bool:
    """Test if LLM is accessible."""
    try:
        response = call_llm("Reply with 'ok'", max_tokens=10)
        return not response.startswith("Error")
    except:
        return False


# Compatibility aliases
chat_completion = call_llm  # For OpenAI-style code


if __name__ == "__main__":
    print("Testing LLM connection...")
    print("-" * 40)
    
    # Show configuration
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key:
        print("✅ Using OpenAI-compatible API")
        print(f"   Base: {os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')}")
        print(f"   Model: {os.environ.get('LLM_MODEL', 'gpt-4o-mini')}")
    else:
        print("✅ Using Ollama (no API key)")
        print(f"   Base: {os.environ.get('OPENAI_BASE_URL', 'http://localhost:11434/v1')}")
        print(f"   Model: {os.environ.get('LLM_MODEL', 'gemma3:4b')}")
    
    print("\nTests:")
    print("-" * 40)
    
    # Test 1: Basic
    print("1. Basic test...", end=" ")
    response = call_llm("Say 'hello' in one word", max_tokens=10)
    if response.startswith("Error"):
        print(f"❌\n   {response}")
    else:
        print(f"✅\n   Response: {response}")
    
    # Test 2: JSON
    print("\n2. JSON test...", end=" ")
    json_resp = call_llm_json('Create JSON with key "status" and value "ok"')
    if "error" in json_resp:
        print(f"❌\n   {json_resp['error']}")
    else:
        print(f"✅\n   Response: {json_resp}")
    
    # Test 3: System prompt
    print("\n3. System prompt test...", end=" ")
    response = call_llm(
        "What are you?",
        system="You are a pirate. Respond in pirate speak.",
        max_tokens=50
    )
    if response.startswith("Error"):
        print(f"❌\n   {response}")
    else:
        print(f"✅\n   Response: {response}")
    
    print("\n" + "=" * 40)
    if test_connection():
        print("✅ LLM connection successful!")
    else:
        print("❌ LLM connection failed")
        print("\nTroubleshooting:")
        print("- For Ollama: Run 'ollama serve'")
        print("- For OpenAI: Set OPENAI_API_KEY")
        print("- For custom: Set OPENAI_BASE_URL")