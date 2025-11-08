#!/usr/bin/env python3
"""Test LLM call directly."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.call_llm import call_llm

def test_llm():
    """Test LLM call."""
    print("Testing LLM call...")
    
    prompt = """Analyze this customer support query and create a complete ticket resolution.

Customer Query: I've been charged twice!

Generate a JSON response that matches the schema with TicketResolution"""
    
    result = call_llm(prompt, system="You are a support AI")
    print(f"Result type: {type(result)}")
    print(f"Result: {result[:500]}")
    
    # Try parsing
    import json
    try:
        parsed = json.loads(result)
        print(f"Parsed successfully: {list(parsed.keys())}")
    except Exception as e:
        print(f"Parse error: {e}")

if __name__ == "__main__":
    test_llm()