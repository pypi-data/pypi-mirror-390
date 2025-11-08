#!/usr/bin/env python3
"""Test raw Ollama response."""

import requests

prompt = """Generate a simple JSON object for a support ticket with these fields:
- ticket_id: "TICKET-001"  
- priority: "high"
- category: "billing"
- issue_summary: "Customer charged twice"

Just return the JSON object, nothing else."""

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.2:3b",
    "prompt": prompt,
    "temperature": 0.1,
    "options": {
        "num_predict": 200
    },
    "stream": False
}, timeout=60)

result = response.json()["response"]
print("Raw response:")
print(result)
print("\n" + "="*50 + "\n")

# Try to extract JSON
import re
json_match = re.search(r'\{[^}]+\}', result, re.DOTALL)
if json_match:
    print("Extracted JSON:")
    print(json_match.group())