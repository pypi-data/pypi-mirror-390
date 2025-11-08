"""
LLM providers for majority vote example.
OpenAI-compatible format that works with multiple providers.
"""

import os
import time
import random
from typing import Dict, Any, Optional

def get_llm_client(provider: str = "openai"):
    """Get LLM client for specific provider."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    if provider == "openai":
        return OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-openai-api-key"))
    elif provider == "groq":
        return OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=os.environ.get("GROQ_API_KEY", "your-groq-api-key")
        )
    elif provider == "ollama":
        return OpenAI(
            base_url=os.environ.get("LLM_BASE_URL", "http://localhost:11434/v1"),
            api_key="ollama"
        )
    else:
        return OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "your-openai-api-key"))

# Model configurations for majority voting
MODEL_CONFIGS = {
    "model_1": {
        "provider": os.environ.get("MODEL_1_PROVIDER", "openai"),
        "model": os.environ.get("MODEL_1_NAME", "gpt-4o"),
        "temperature": 0.7,
    },
    "model_2": {
        "provider": os.environ.get("MODEL_2_PROVIDER", "openai"),
        "model": os.environ.get("MODEL_2_NAME", "gpt-4o-mini"),
        "temperature": 0.8,
    },
    "model_3": {
        "provider": os.environ.get("MODEL_3_PROVIDER", "groq"),
        "model": os.environ.get("MODEL_3_NAME", "llama-3.1-70b-versatile"),
        "temperature": 0.6,
    },
}

def query_llm(query: str, model_id: str = "model_1", temperature: Optional[float] = None) -> Dict[str, Any]:
    """
    Query LLM using specified model configuration.
    
    Args:
        query: The prompt to send to the LLM
        model_id: Which model configuration to use
        temperature: Override temperature if provided
        
    Returns:
        Dict with response, latency, model info, and confidence
    """
    start_time = time.time()
    
    # Get model configuration
    config = MODEL_CONFIGS.get(model_id, MODEL_CONFIGS["model_1"])
    client = get_llm_client(config["provider"])
    
    # Use provided temperature or config default
    temp = temperature if temperature is not None else config["temperature"]
    
    try:
        # Make API call
        response = client.chat.completions.create(
            model=config["model"],
            messages=[{"role": "user", "content": query}],
            temperature=temp,
            max_tokens=500,
        )
        
        # Calculate metrics
        latency = time.time() - start_time
        response_text = response.choices[0].message.content
        
        # Estimate confidence based on response characteristics
        confidence = estimate_confidence(response_text, query)
        
        return {
            "response": response_text,
            "latency": latency,
            "model": f"{config['provider']}/{config['model']}",
            "confidence": confidence,
            "temperature": temp,
        }
        
    except Exception as e:
        print(f"Error querying {model_id}: {e}")
        # Return a fallback response
        return {
            "response": f"Error: Could not get response from {config['provider']}",
            "latency": time.time() - start_time,
            "model": f"{config['provider']}/{config['model']}",
            "confidence": 0.0,
            "temperature": temp,
            "error": str(e),
        }

def estimate_confidence(response: str, query: str) -> float:
    """
    Estimate confidence based on response characteristics.
    In a real implementation, this could use more sophisticated methods.
    """
    confidence = 0.7  # Base confidence
    
    # Adjust based on response length
    if len(response) > 100:
        confidence += 0.1
    
    # Check for uncertainty markers
    uncertainty_phrases = ["i'm not sure", "might be", "possibly", "perhaps", "unclear"]
    if any(phrase in response.lower() for phrase in uncertainty_phrases):
        confidence -= 0.2
    
    # Check for definitive language
    definitive_phrases = ["definitely", "certainly", "clearly", "absolutely"]
    if any(phrase in response.lower() for phrase in definitive_phrases):
        confidence += 0.1
    
    # Ensure confidence is between 0 and 1
    return max(0.0, min(1.0, confidence))

def query_llm_mock(query: str, model: str = "gpt-3.5", temperature: float = 0.7) -> Dict[str, Any]:
    """
    Backward compatibility wrapper - redirects to query_llm.
    """
    # Map old model names to model_ids
    model_mapping = {
        "gpt-3.5": "model_1",
        "gpt-4": "model_2",
        "claude": "model_3",
    }
    
    model_id = model_mapping.get(model, "model_1")
    return query_llm(query, model_id, temperature)


if __name__ == "__main__":
    # Test the providers
    print("Testing LLM providers for majority voting...")
    
    test_query = "What is the capital of France?"
    
    for model_id in MODEL_CONFIGS.keys():
        print(f"\nTesting {model_id}:")
        result = query_llm(test_query, model_id)
        print(f"  Model: {result['model']}")
        print(f"  Response: {result['response'][:100]}...")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Latency: {result['latency']:.2f}s")