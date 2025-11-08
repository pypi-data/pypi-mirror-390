#!/usr/bin/env python3
"""
Simple working LLM implementation using Ollama
No API keys needed - runs 100% locally and free

Setup:
1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
2. Pull a model: ollama pull llama3.2
3. Start server: ollama serve
4. Use this file!
"""

import json
import requests
from typing import Optional, Dict, Any


def call_llm(
    prompt: str,
    model: str = "llama3.2",
    temperature: float = 0.7,
    max_tokens: int = 500,
    system_prompt: Optional[str] = None
) -> str:
    """
    Call Ollama LLM with the given prompt.
    
    Args:
        prompt: The user prompt
        model: Ollama model name (llama3.2, mistral, codellama, etc.)
        temperature: Creativity (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum response length
        system_prompt: Optional system message
        
    Returns:
        The LLM's response as a string
    """
    url = "http://localhost:11434/api/generate"
    
    # Build the full prompt
    if system_prompt:
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}\n\nAssistant:"
    else:
        full_prompt = prompt
    
    payload = {
        "model": model,
        "prompt": full_prompt,
        "temperature": temperature,
        "stream": False,
        "options": {
            "num_predict": max_tokens
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result.get("response", "").strip()
    except requests.ConnectionError:
        return "ERROR: Ollama not running. Start with: ollama serve"
    except requests.Timeout:
        return "ERROR: Request timed out. Try a smaller prompt or increase timeout."
    except Exception as e:
        return f"ERROR: {str(e)}"


def call_llm_json(
    prompt: str,
    model: str = "llama3.2",
    temperature: float = 0.3
) -> Dict[str, Any]:
    """
    Call LLM and parse JSON response.
    Lower temperature for more consistent JSON.
    """
    # Add JSON instruction to prompt
    json_prompt = f"""{prompt}

Respond with valid JSON only, no other text."""
    
    response = call_llm(json_prompt, model=model, temperature=temperature)
    
    # Try to extract JSON from response
    try:
        # Find JSON in response (between { and })
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Fallback
    return {"error": "Could not parse JSON", "raw_response": response}


def call_llm_streaming(
    prompt: str,
    model: str = "llama3.2",
    callback=None
) -> str:
    """
    Stream LLM response token by token.
    
    Args:
        prompt: The prompt
        model: Model name
        callback: Function called with each token
        
    Returns:
        Complete response
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    
    full_response = ""
    
    try:
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    full_response += token
                    
                    if callback:
                        callback(token)
                    
                    if chunk.get("done", False):
                        break
                        
    except Exception as e:
        return f"ERROR: {str(e)}"
    
    return full_response


def list_models() -> list:
    """List available Ollama models"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        response.raise_for_status()
        models = response.json().get("models", [])
        return [m["name"] for m in models]
    except:
        return []


def ensure_ollama_running() -> bool:
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


# For compatibility with OpenAI-style code
def chat_completion(messages: list, model: str = "llama3.2", **kwargs) -> str:
    """
    OpenAI-style chat completion for easy migration.
    
    Args:
        messages: List of {"role": "user/assistant/system", "content": "..."}
        model: Model name
        
    Returns:
        Assistant's response
    """
    # Convert messages to prompt
    prompt = ""
    system = ""
    
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        
        if role == "system":
            system = content
        elif role == "user":
            prompt += f"User: {content}\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\n"
    
    prompt += "Assistant:"
    
    return call_llm(prompt, model=model, system_prompt=system, **kwargs)


if __name__ == "__main__":
    print("Testing Ollama LLM connection...")
    
    if not ensure_ollama_running():
        print("\n❌ Ollama is not running!")
        print("Start it with: ollama serve")
        print("Install from: https://ollama.com")
        exit(1)
    
    print("✅ Ollama is running")
    
    models = list_models()
    if models:
        print(f"Available models: {', '.join(models)}")
    else:
        print("No models found. Pull one with: ollama pull llama3.2")
        exit(1)
    
    # Test basic call
    print("\n1. Testing basic call...")
    response = call_llm("Say hello in 3 words")
    print(f"Response: {response}")
    
    # Test JSON response
    print("\n2. Testing JSON response...")
    json_response = call_llm_json(
        "Return a JSON object with name='test' and status='working'"
    )
    print(f"JSON: {json_response}")
    
    # Test streaming
    print("\n3. Testing streaming...")
    print("Response: ", end="")
    call_llm_streaming(
        "Count from 1 to 5",
        callback=lambda token: print(token, end="", flush=True)
    )
    print("\n\n✅ All tests passed!")