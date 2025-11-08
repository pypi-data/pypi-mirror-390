#!/usr/bin/env python3
"""
Real LLM implementation - no mocks.
"""

import os
import sys
import json
import requests


def call_llm(prompt: str, system: str = None, model: str = None, temperature: float = 0.3) -> str:
    """
    Call real LLM API. Supports OpenAI, Anthropic, or Groq.
    
    Args:
        prompt: User prompt
        system: System prompt (optional)
        model: Model to use (optional, auto-detects based on API key)
        temperature: Temperature for response (0-1)
    
    Returns:
        str: LLM response
    """
    # Check if using Ollama (local)
    if os.environ.get("OLLAMA_API_BASE"):
        return call_openai(prompt, system, model or "mistral", temperature, "not-needed")
    
    # Check which API key is available
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    groq_key = os.environ.get("GROQ_API_KEY")
    
    if openai_key:
        return call_openai(prompt, system, model or "gpt-3.5-turbo", temperature, openai_key)
    elif anthropic_key:
        return call_anthropic(prompt, system, model or "claude-3-haiku-20240307", temperature, anthropic_key)
    elif groq_key:
        return call_groq(prompt, system, model or "mixtral-8x7b-32768", temperature, groq_key)
    else:
        print("❌ No LLM API key found!")
        print("Set one of these environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - ANTHROPIC_API_KEY")  
        print("  - GROQ_API_KEY")
        print("  - OLLAMA_API_BASE (for local Ollama)")
        sys.exit(1)


def call_openai(prompt: str, system: str, model: str, temperature: float, api_key: str) -> str:
    """Call OpenAI API (or compatible APIs like Ollama)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    # Check if using Ollama (local)
    base_url = "https://api.openai.com/v1"
    if os.environ.get("OLLAMA_API_BASE"):
        base_url = os.environ.get("OLLAMA_API_BASE")
        # Ollama doesn't need auth header
        headers = {"Content-Type": "application/json"}
    else:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    response = requests.post(
        f"{base_url}/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"API error: {response.status_code} - {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]


def call_anthropic(prompt: str, system: str, model: str, temperature: float, api_key: str) -> str:
    """Call Anthropic API."""
    messages = [{"role": "user", "content": prompt}]
    
    body = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 4096
    }
    
    if system:
        body["system"] = system
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        },
        json=body
    )
    
    if response.status_code != 200:
        raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
    
    return response.json()["content"][0]["text"]


def call_groq(prompt: str, system: str, model: str, temperature: float, api_key: str) -> str:
    """Call Groq API."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Groq API error: {response.status_code} - {response.text}")
    
    return response.json()["choices"][0]["message"]["content"]


def get_available_providers():
    """Check which LLM providers are available."""
    return {
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "groq": bool(os.environ.get("GROQ_API_KEY")),
        "ollama": bool(os.environ.get("OLLAMA_API_BASE"))
    }


if __name__ == "__main__":
    # Test the LLM
    print("Testing LLM connection...")
    response = call_llm("Say 'Hello, I'm working!' in exactly 5 words.")
    print(f"Response: {response}")