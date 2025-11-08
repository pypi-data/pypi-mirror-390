"""
LLM utility for web search workflows.
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
    max_tokens: int = 1500,
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
    
    # Query analysis
    if "analyze this search query" in prompt.lower():
        query = prompt.split("Query: ")[1].split("\n")[0] if "Query: " in prompt else "test query"
        return json.dumps({
            "original_query": query,
            "cleaned_query": query,
            "intent": "informational",
            "entities": [query.split()[0]] if query else [],
            "temporal_markers": ["latest"] if "latest" in query else [],
            "requires_current": "latest" in query or "today" in query,
            "suggested_filters": {},
            "related_queries": [f"{query} tutorial", f"{query} examples"]
        })
    
    # Answer synthesis
    elif "synthesize a comprehensive answer" in prompt.lower():
        return json.dumps({
            "answer": "Based on the search results, here's what I found about your query. Multiple sources indicate this is an important topic with various perspectives.",
            "confidence": 0.8,
            "key_points": [
                "This is a key finding from the search results",
                "Another important point to consider"
            ],
            "caveats": ["Information may be outdated"],
            "follow_up_questions": [
                "Would you like more specific information?",
                "Are you interested in recent developments?"
            ]
        })
    
    # Research planning
    elif "create a research plan" in prompt.lower():
        topic = prompt.split("Topic: ")[1].split("\n")[0] if "Topic: " in prompt else "research topic"
        return json.dumps({
            "main_topic": topic,
            "subtopics": [
                f"{topic} fundamentals",
                f"{topic} applications",
                f"{topic} future trends"
            ],
            "research_questions": [
                f"What is {topic}?",
                f"How does {topic} work?",
                f"What are the implications of {topic}?"
            ],
            "required_sources": 10
        })
    
    # Default response
    return "This is a mock response for web search integration."


if __name__ == "__main__":
    # Test the LLM caller
    print("Available providers:", get_available_providers())
    
    # Test query analysis
    response = call_llm(
        "Analyze this search query to optimize web search.\n\nQuery: quantum computing latest developments",
        system="You are a search query analyst."
    )
    print(f"\nQuery analysis: {response}")
    
    # Test answer synthesis
    response = call_llm(
        "Synthesize a comprehensive answer from these search results.",
        system="You are a research assistant."
    )
    print(f"\nAnswer synthesis: {response}")