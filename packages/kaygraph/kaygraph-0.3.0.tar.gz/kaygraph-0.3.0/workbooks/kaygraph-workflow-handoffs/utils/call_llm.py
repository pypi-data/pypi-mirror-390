"""
LLM utility for handoff workflows.
"""

import os
import json
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


def get_available_providers() -> List[str]:
    """Get list of available LLM providers based on environment variables."""
    providers = []
    
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    if os.getenv("GROQ_API_KEY"):
        providers.append("groq")
    
    # Ollama is available if running locally
    providers.append("ollama")
    
    return providers


def call_llm(
    prompt: str,
    system: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    response_format: Optional[Dict] = None
) -> str:
    """
    Call LLM with automatic provider selection.
    
    Args:
        prompt: User prompt
        system: System prompt
        model: Model name (optional, will auto-select)
        temperature: Temperature for generation
        max_tokens: Maximum tokens to generate
        response_format: Optional response format (e.g., {"type": "json"})
    
    Returns:
        Generated text response
    """
    providers = get_available_providers()
    
    if not providers:
        logger.warning("No LLM providers available, using mock response")
        return _mock_llm_response(prompt, response_format)
    
    # Try providers in order of preference
    for provider in ["anthropic", "openai", "groq", "ollama"]:
        if provider in providers:
            try:
                return _call_provider(
                    provider, prompt, system, model,
                    temperature, max_tokens, response_format
                )
            except Exception as e:
                logger.warning(f"Failed to call {provider}: {e}")
                continue
    
    # Fallback to mock
    return _mock_llm_response(prompt, response_format)


def _call_provider(
    provider: str,
    prompt: str,
    system: Optional[str],
    model: Optional[str],
    temperature: float,
    max_tokens: int,
    response_format: Optional[Dict]
) -> str:
    """Call specific LLM provider."""
    
    if provider == "openai":
        return _call_openai(prompt, system, model, temperature, max_tokens, response_format)
    elif provider == "anthropic":
        return _call_anthropic(prompt, system, model, temperature, max_tokens)
    elif provider == "groq":
        return _call_groq(prompt, system, model, temperature, max_tokens)
    elif provider == "ollama":
        return _call_ollama(prompt, system, model, temperature, max_tokens)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _call_openai(
    prompt: str,
    system: Optional[str],
    model: Optional[str],
    temperature: float,
    max_tokens: int,
    response_format: Optional[Dict]
) -> str:
    """Call OpenAI API."""
    try:
        import openai
        
        client = openai.OpenAI()
        model = model or "gpt-4o-mini"
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        raise


def _call_anthropic(
    prompt: str,
    system: Optional[str],
    model: Optional[str],
    temperature: float,
    max_tokens: int
) -> str:
    """Call Anthropic API."""
    try:
        import anthropic
        
        client = anthropic.Anthropic()
        model = model or "claude-3-haiku-20240307"
        
        kwargs = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if system:
            kwargs["system"] = system
        
        response = client.messages.create(**kwargs)
        return response.content[0].text
        
    except Exception as e:
        logger.error(f"Anthropic error: {e}")
        raise


def _call_groq(
    prompt: str,
    system: Optional[str],
    model: Optional[str],
    temperature: float,
    max_tokens: int
) -> str:
    """Call Groq API."""
    try:
        from groq import Groq
        
        client = Groq()
        model = model or "llama3-8b-8192"
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Groq error: {e}")
        raise


def _call_ollama(
    prompt: str,
    system: Optional[str],
    model: Optional[str],
    temperature: float,
    max_tokens: int
) -> str:
    """Call Ollama API."""
    try:
        import requests
        
        model = model or "llama3.2"
        url = "http://localhost:11434/api/generate"
        
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        response = requests.post(url, json={
            "model": model,
            "prompt": full_prompt,
            "temperature": temperature,
            "options": {
                "num_predict": max_tokens
            },
            "stream": False
        })
        
        response.raise_for_status()
        return response.json()["response"]
        
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        raise


def _mock_llm_response(prompt: str, response_format: Optional[Dict]) -> str:
    """Generate mock LLM response for testing."""
    
    if response_format and response_format.get("type") == "json":
        # Return mock JSON based on prompt content
        if "analyze" in prompt.lower() and "customer request" in prompt.lower():
            return json.dumps({
                "request_type": "technical",
                "priority": "medium",
                "recommended_agent": "tech_support",
                "confidence": 0.8,
                "reasoning": "Mock analysis",
                "keywords": ["technical", "issue"],
                "requires_escalation": False
            })
        elif "technical support" in prompt.lower():
            return json.dumps({
                "response": "I'll help you with that technical issue. Please try restarting the application.",
                "confidence": 0.8,
                "needs_handoff": False,
                "suggested_handoff": None,
                "handoff_reason": None,
                "resolution_complete": False
            })
        elif "billing" in prompt.lower():
            return json.dumps({
                "response": "I can help with your billing inquiry. Your current balance is $0.",
                "confidence": 0.8,
                "needs_handoff": False,
                "suggested_handoff": None,
                "handoff_reason": None,
                "resolution_complete": True
            })
        elif "break down" in prompt.lower():
            return json.dumps({
                "original_task": "Complex task",
                "subtasks": [
                    {
                        "id": "task_1",
                        "description": "Analyze requirements",
                        "required_skills": ["analysis"],
                        "estimated_duration": 1.0,
                        "priority": "high",
                        "dependencies": []
                    },
                    {
                        "id": "task_2",
                        "description": "Implement solution",
                        "required_skills": ["coding"],
                        "estimated_duration": 2.0,
                        "priority": "medium",
                        "dependencies": ["task_1"]
                    }
                ],
                "suggested_assignments": {
                    "task_1": "document_analyzer",
                    "task_2": "data_extractor"
                },
                "estimated_total_time": 3.0,
                "parallel_execution": False
            })
        else:
            return json.dumps({"response": "Mock JSON response", "status": "ok"})
    
    # Regular text response
    if "technical" in prompt.lower():
        return "I'll help you troubleshoot that technical issue. First, let's try restarting the application."
    elif "billing" in prompt.lower():
        return "I can assist with your billing question. Your account is in good standing."
    else:
        return "I understand your request. Let me help you with that."


if __name__ == "__main__":
    # Test the LLM caller
    print("Available providers:", get_available_providers())
    
    # Test basic call
    response = call_llm(
        "What is 2+2?",
        system="You are a helpful assistant."
    )
    print(f"\nBasic response: {response}")
    
    # Test JSON response
    json_response = call_llm(
        "Analyze this customer request: 'My app keeps crashing'",
        system="You are a triage specialist.",
        response_format={"type": "json"}
    )
    print(f"\nJSON response: {json_response}")