"""
LLM utility for reasoning workflows.
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
    
    # For YAML responses
    if "yaml" in prompt.lower() and "thought_process" in prompt.lower():
        return """thought_process: |
  Looking at this problem, I need to break it down step by step.
  First, I'll identify what we know and what we need to find.
  Then I'll work through the solution systematically.
result: "Step completed successfully"
confidence: 0.8
insights:
  - "This type of problem requires careful analysis"
  - "Breaking it into steps makes it manageable"
next_steps: []
issues: []"""
    
    # For JSON responses
    if response_format and response_format.get("type") == "json":
        # Math problem response
        if "math problem" in prompt.lower():
            return json.dumps({
                "problem": {
                    "description": "A mock math problem",
                    "known_values": {"speed": 60, "time": 2},
                    "unknown_variable": "distance",
                    "problem_type": "algebra"
                },
                "steps": [
                    {
                        "step_number": 1,
                        "description": "Use distance = speed × time",
                        "operation": "multiply",
                        "expression": "60 × 2",
                        "result": 120,
                        "units": "miles"
                    }
                ],
                "final_answer": "120 miles",
                "verification_method": "Check: 120 ÷ 60 = 2 hours"
            })
        
        # Problem analysis response
        elif "analyze this problem" in prompt.lower():
            return json.dumps({
                "problem": "Mock problem analysis",
                "problem_type": "math",
                "approach": "chain_of_thought",
                "steps": [
                    {
                        "id": "step_1",
                        "content": "Understand the problem",
                        "reasoning_type": "analysis",
                        "confidence": 0.8,
                        "dependencies": []
                    },
                    {
                        "id": "step_2",
                        "content": "Identify key information",
                        "reasoning_type": "analysis",
                        "confidence": 0.8,
                        "dependencies": ["step_1"]
                    },
                    {
                        "id": "step_3",
                        "content": "Solve step by step",
                        "reasoning_type": "calculation",
                        "confidence": 0.7,
                        "dependencies": ["step_2"]
                    }
                ],
                "confidence": 0.75,
                "max_iterations": 10
            })
        
        # Logic problem response
        elif "logic problem" in prompt.lower():
            return json.dumps({
                "entities": {"Box A": "Oranges", "Box B": "Apples", "Box C": "Mixed"},
                "constraints": [
                    {
                        "id": "c1",
                        "description": "All labels are wrong",
                        "entities": ["Box A", "Box B", "Box C"],
                        "relationship": "mislabeled",
                        "satisfied": True
                    }
                ],
                "deductions": [
                    "Step 1: Since all labels are wrong, Box A (labeled 'Apples') cannot contain apples",
                    "Step 2: If we pick from Box C (labeled 'Mixed'), it must contain only one type",
                    "Step 3: Based on what we find, we can deduce all contents"
                ],
                "solution_valid": True
            })
        
        # Decision analysis response
        elif "decision" in prompt.lower():
            return json.dumps({
                "question": "Mock decision question",
                "context": "Considering various factors",
                "options": [
                    {
                        "id": "opt1",
                        "name": "Option A",
                        "description": "First option",
                        "pros": ["Fast", "Simple"],
                        "cons": ["Limited features"],
                        "factors": [
                            {
                                "name": "Speed",
                                "description": "How fast it is",
                                "weight": 0.4,
                                "score": 8.0,
                                "reasoning": "Very fast implementation"
                            }
                        ],
                        "total_score": 7.5
                    },
                    {
                        "id": "opt2",
                        "name": "Option B",
                        "description": "Second option",
                        "pros": ["Feature-rich", "Scalable"],
                        "cons": ["Complex"],
                        "factors": [
                            {
                                "name": "Features",
                                "description": "Available features",
                                "weight": 0.6,
                                "score": 9.0,
                                "reasoning": "Many features available"
                            }
                        ],
                        "total_score": 8.2
                    }
                ],
                "recommendation": "Option B",
                "confidence": 0.8,
                "reasoning_summary": "Option B provides better long-term value"
            })
        
        # Multi-path response
        elif "multiple ways" in prompt.lower():
            return json.dumps({
                "paths": [
                    {
                        "id": "path_1",
                        "description": "Direct calculation approach",
                        "steps": [
                            {
                                "id": "p1_s1",
                                "content": "Calculate directly",
                                "reasoning_type": "calculation",
                                "confidence": 0.8
                            }
                        ],
                        "confidence": 0.8,
                        "result": "Result via direct calculation"
                    },
                    {
                        "id": "path_2",
                        "description": "Step-by-step breakdown",
                        "steps": [
                            {
                                "id": "p2_s1",
                                "content": "Break into sub-problems",
                                "reasoning_type": "analysis",
                                "confidence": 0.7
                            }
                        ],
                        "confidence": 0.75,
                        "result": "Result via breakdown"
                    }
                ],
                "best_path_id": "path_1",
                "consensus_answer": "Both paths lead to same answer"
            })
        
        # Reflection response
        elif "reflect" in prompt.lower():
            return json.dumps({
                "reflection": "This step seems logically sound",
                "issues_found": [],
                "corrections_made": [],
                "confidence_after": 0.85
            })
        
        else:
            return json.dumps({"result": "Mock reasoning result", "confidence": 0.7})
    
    # Regular text response
    if "math" in prompt.lower():
        return "To solve this math problem, I'll work step by step. First, I identify what we know..."
    elif "logic" in prompt.lower():
        return "This logic puzzle requires systematic deduction. Let me work through the constraints..."
    else:
        return "I'll analyze this problem using structured reasoning..."


if __name__ == "__main__":
    # Test the LLM caller
    print("Available providers:", get_available_providers())
    
    # Test basic call
    response = call_llm(
        "What is the speed if distance is 120 miles and time is 2 hours?",
        system="You are a math tutor."
    )
    print(f"\nBasic response: {response}")
    
    # Test JSON response
    json_response = call_llm(
        "Analyze this problem: A train travels 120 miles in 2 hours",
        system="You are a problem analyzer.",
        response_format={"type": "json"}
    )
    print(f"\nJSON response: {json_response}")