#!/usr/bin/env python3
"""Test Ollama directly."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.call_llm import call_llm
import json

def test_simple():
    """Test simple JSON generation."""
    print("Testing simple JSON generation with Ollama...")
    
    prompt = """Generate a JSON object with these fields:
    - name: string
    - age: number
    - city: string
    
    Example: {"name": "John", "age": 30, "city": "New York"}
    
    Generate JSON for a person named Alice who is 25 and lives in Boston:"""
    
    result = call_llm(prompt, temperature=0.1, max_tokens=100)
    print(f"Result: {result}")
    
    try:
        parsed = json.loads(result)
        print(f"✓ Valid JSON: {parsed}")
    except Exception as e:
        print(f"✗ Invalid JSON: {e}")
        # Try to extract JSON from response
        import re
        json_match = re.search(r'\{[^}]+\}', result)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                print(f"✓ Extracted JSON: {parsed}")
            except:
                print("✗ Could not extract valid JSON")

if __name__ == "__main__":
    test_simple()