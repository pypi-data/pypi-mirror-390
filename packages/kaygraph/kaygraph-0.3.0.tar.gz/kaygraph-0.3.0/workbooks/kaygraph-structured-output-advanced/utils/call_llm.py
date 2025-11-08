"""
LLM utility for advanced structured output workflows.
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
    max_tokens: int = 2000,
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
        
        # Use available models - prefer smaller ones for speed
        available_models = ["llama3.2:3b", "llama3.2:1b", "qwen2.5:latest", "mistral:latest"]
        model = model or available_models[0]
        
        # Check if model exists
        try:
            tags_response = requests.get("http://localhost:11434/api/tags")
            if tags_response.ok:
                models = tags_response.json().get("models", [])
                model_names = [m["name"] for m in models]
                # Find first available model from our list
                for preferred in available_models:
                    if preferred in model_names:
                        model = preferred
                        break
        except:
            pass  # Use default if can't check
        
        url = "http://localhost:11434/api/generate"
        
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        logger.info(f"Calling Ollama with model: {model}")
        
        response = requests.post(url, json={
            "model": model,
            "prompt": full_prompt,
            "temperature": temperature,
            "options": {
                "num_predict": min(max_tokens, 1000)  # Limit for faster response
            },
            "stream": False
        }, timeout=60)  # Longer timeout for structured generation
        
        response.raise_for_status()
        result = response.json()["response"]
        logger.info(f"Ollama returned {len(result)} characters")
        return result
        
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        logger.warning(f"Failed to call ollama: {e}")
        # Return mock response as fallback
        return _mock_llm_response(prompt, None)


def _mock_llm_response(prompt: str, response_format: Optional[Dict]) -> str:
    """Generate mock LLM response for testing."""
    
    # Ticket generation response
    if "ticket resolution" in prompt.lower() and "ticketresolution" in prompt.lower():
        return json.dumps({
            "ticket_id": "TICKET-12345",
            "category": "billing",
            "priority": "high",
            "sentiment": "negative",
            "customer_info": {
                "customer_id": "CUST-789",
                "email": "customer@example.com",
                "name": "Test Customer"
            },
            "issue_summary": "Customer is experiencing billing issues with incorrect charges on their account",
            "steps": [
                {
                    "step_number": 1,
                    "description": "Verify customer account and billing history",
                    "action": "Access customer account in billing system",
                    "requires_customer_input": False,
                    "estimated_time_minutes": 5
                },
                {
                    "step_number": 2,
                    "description": "Identify the incorrect charges",
                    "action": "Review recent transactions and compare with service usage",
                    "requires_customer_input": True,
                    "estimated_time_minutes": 10
                },
                {
                    "step_number": 3,
                    "description": "Process refund for incorrect charges",
                    "action": "Submit refund request through billing system",
                    "requires_customer_input": False,
                    "estimated_time_minutes": 5
                }
            ],
            "final_resolution": "I've reviewed your account and identified the billing discrepancy you mentioned. I've processed a refund for the incorrect charges, which should appear in your account within 3-5 business days. I've also added a note to your account to prevent this issue from happening again. Is there anything else I can help you with today?",
            "response_tone": "empathetic",
            "confidence": 0.9,
            "requires_follow_up": True,
            "safety_check": {
                "has_pii": False,
                "has_harmful_content": False,
                "has_prompt_injection": False,
                "pii_entities": [],
                "harmful_categories": [],
                "confidence": 0.95
            }
        })
    
    # Report generation response
    elif "structured report" in prompt.lower() and "structuredreport" in prompt.lower():
        return json.dumps({
            "metadata": {
                "report_id": "RPT-2024-001",
                "title": "Quarterly Business Analysis Report",
                "author": "AI Assistant",
                "created_at": "2024-01-15T10:00:00Z",
                "version": "1.0",
                "tags": ["quarterly", "analysis", "business"],
                "confidentiality_level": "internal"
            },
            "executive_summary": "This quarterly report provides a comprehensive analysis of business performance, highlighting key achievements and areas for improvement. Revenue grew by 15% compared to the previous quarter, while operational efficiency improved by 8%. Strategic initiatives are showing positive results.",
            "sections": [
                {
                    "title": "Financial Performance",
                    "content": "The financial performance this quarter exceeded expectations with total revenue reaching $12.5M, representing a 15% increase from Q3. Key drivers included strong sales in the enterprise segment and successful upselling initiatives. Operating margins improved to 22%, up from 20% in the previous quarter.",
                    "subsections": [],
                    "data_points": {
                        "revenue": 12500000,
                        "growth_rate": 0.15,
                        "operating_margin": 0.22
                    },
                    "confidence": 0.95
                },
                {
                    "title": "Operational Metrics",
                    "content": "Operational efficiency showed significant improvement with customer response times reduced by 25% and system uptime maintained at 99.9%. The implementation of new automation tools contributed to a 30% reduction in manual processing time.",
                    "subsections": [],
                    "data_points": {
                        "response_time_improvement": 0.25,
                        "uptime": 0.999,
                        "automation_impact": 0.30
                    },
                    "confidence": 0.90
                }
            ],
            "conclusions": [
                "Overall business performance is strong with positive trends in both revenue and efficiency",
                "Investment in automation and process improvements is yielding measurable results"
            ],
            "recommendations": [
                "Continue investing in automation technologies to further improve efficiency",
                "Expand successful enterprise sales strategies to other market segments"
            ],
            "quality_score": 0.85
        })
    
    # Form field generation
    elif "form field" in prompt.lower() or "formfield" in prompt.lower():
        return json.dumps([
            {
                "field_id": "full_name",
                "label": "Full Name",
                "field_type": "text",
                "validation": {
                    "required": True,
                    "min_length": 2,
                    "max_length": 100
                },
                "help_text": "Enter your full legal name"
            },
            {
                "field_id": "email",
                "label": "Email Address",
                "field_type": "email",
                "validation": {
                    "required": True,
                    "pattern": "^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$"
                },
                "help_text": "We'll use this to contact you"
            },
            {
                "field_id": "issue_type",
                "label": "Issue Type",
                "field_type": "select",
                "validation": {
                    "required": True,
                    "allowed_values": ["billing", "technical", "account", "other"]
                },
                "help_text": "Select the type of issue you're experiencing"
            }
        ])
    
    # Default structured response
    return json.dumps({
        "status": "success",
        "message": "Mock structured output generated",
        "data": {
            "timestamp": "2024-01-15T10:00:00Z",
            "confidence": 0.8
        }
    })


if __name__ == "__main__":
    # Test the LLM caller
    print("Available providers:", get_available_providers())
    
    # Test ticket generation
    response = call_llm(
        "Generate a TicketResolution for a customer complaining about billing issues",
        system="You are a customer support AI."
    )
    print(f"\nTicket response: {response[:200]}...")
    
    # Test report generation
    response = call_llm(
        "Generate a StructuredReport about quarterly performance",
        system="You are a report generation AI."
    )
    print(f"\nReport response: {response[:200]}...")