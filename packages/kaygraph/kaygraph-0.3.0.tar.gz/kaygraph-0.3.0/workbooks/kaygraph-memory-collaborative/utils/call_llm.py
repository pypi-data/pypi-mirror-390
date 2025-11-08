"""
LLM integration for collaborative memory workflows.
"""

import requests
import json
import logging
import time
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def call_llm(prompt: str, system: str = "", model: str = "llama3.2:3b", 
             timeout: int = 60, max_tokens: int = 1000) -> str:
    """Call local Ollama LLM with OpenAI-compatible API."""
    try:
        return _call_ollama(prompt, system, model, timeout, max_tokens)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return f"LLM Error: {str(e)}"


def _call_ollama(prompt: str, system: str, model: str, timeout: int, max_tokens: int) -> str:
    """Call Ollama using OpenAI-compatible endpoint."""
    url = "http://localhost:11434/v1/chat/completions"
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.3,  # Lower for more consistent collaborative responses
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    logger.debug(f"Calling Ollama with model {model}")
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            logger.debug(f"Ollama response length: {len(content)} characters")
            return content.strip()
        else:
            logger.error(f"Unexpected Ollama response format: {result}")
            return "Error: Invalid response format from Ollama"
            
    except requests.exceptions.Timeout:
        logger.error(f"Ollama request timed out after {timeout}s")
        return "Error: Request timed out. Ollama might be processing a large request."
    
    except requests.exceptions.ConnectionError:
        logger.error("Cannot connect to Ollama. Make sure it's running on http://localhost:11434")
        return "Error: Cannot connect to Ollama. Please ensure it's running."
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return f"Error: Request failed - {str(e)}"
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Ollama response: {e}")
        return "Error: Invalid JSON response from Ollama"


def extract_memories_from_conversation(conversation: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract structured memories from conversation using LLM."""
    system = """You are a memory extraction specialist for team collaboration. 
Extract valuable memories that would benefit team members in future situations.
Focus on actionable insights, decisions, lessons learned, and best practices.
Return only memories that would be genuinely useful for future reference."""
    
    prompt = f"""Analyze this team conversation and extract valuable memories:

CONVERSATION:
{conversation}

CONTEXT:
- Team: {context.get('team_id', 'Unknown')}
- Project: {context.get('project_id', 'Unknown')}
- Participants: {', '.join(context.get('participants', []))}

Extract memories in JSON format with these fields:
- content: The memory content (what should be remembered)
- type: One of [decision, lesson_learned, best_practice, issue, solution, pattern, insight, experience]
- title: Short descriptive title (max 50 chars)
- importance: Float 0.1-1.0 (how important is this to remember)
- tags: List of relevant keywords
- expertise_areas: List of relevant domains/skills

Only extract memories that provide genuine value for team collaboration.
Return as a JSON array."""
    
    response = call_llm(prompt, system)
    
    try:
        # Clean and parse JSON
        response_clean = _clean_json_response(response)
        memories = json.loads(response_clean)
        
        # Validate structure
        validated_memories = []
        for memory in memories:
            if isinstance(memory, dict) and "content" in memory:
                validated_memories.append({
                    "content": memory.get("content", ""),
                    "type": memory.get("type", "experience"),
                    "title": memory.get("title", "")[:50],  # Limit title length
                    "importance": max(0.1, min(1.0, float(memory.get("importance", 0.5)))),
                    "tags": memory.get("tags", []),
                    "expertise_areas": memory.get("expertise_areas", [])
                })
        
        return validated_memories
        
    except Exception as e:
        logger.warning(f"Failed to parse extracted memories: {e}")
        return []


def synthesize_team_insight(memories: List[Dict[str, Any]], target_context: Dict[str, Any]) -> str:
    """Synthesize multiple memories into a cross-team insight."""
    if not memories:
        return "No memories provided for synthesis"
    
    system = """You are a knowledge synthesis expert specializing in cross-team collaboration.
Create valuable insights that can help other teams learn from experiences and avoid common pitfalls.
Focus on transferable patterns, reusable solutions, and actionable guidance."""
    
    memory_summaries = []
    for i, memory in enumerate(memories, 1):
        memory_summaries.append(
            f"{i}. [{memory.get('type', 'unknown')}] {memory.get('content', '')[:150]}..."
        )
    
    prompt = f"""Synthesize these team memories into a valuable cross-team insight:

MEMORIES:
{chr(10).join(memory_summaries)}

TARGET AUDIENCE:
- Teams working in: {', '.join(target_context.get('domains', ['general']))}
- Expertise levels: {target_context.get('expertise_level', 'mixed')}
- Team size: {target_context.get('team_size', 'unknown')}

Create an insight that:
1. Identifies the key pattern or learning
2. Explains why it matters for other teams
3. Provides actionable recommendations
4. Includes specific examples or evidence

Keep it concise (under 400 words) but comprehensive enough to be actionable.
Focus on transferable knowledge that can prevent problems or improve outcomes."""
    
    return call_llm(prompt, system)


def validate_memory_quality(memory: Dict[str, Any]) -> Dict[str, Any]:
    """Use LLM to assess memory quality and provide recommendations."""
    system = """You are a memory quality assessor for team knowledge management.
Evaluate memories for clarity, actionability, completeness, and potential value to the team.
Provide constructive feedback to help improve memory quality."""
    
    prompt = f"""Assess this team memory for quality:

MEMORY:
Title: {memory.get('title', 'No title')}
Type: {memory.get('type', 'unknown')}
Content: {memory.get('content', '')}
Tags: {', '.join(memory.get('tags', []))}
Importance: {memory.get('importance', 0.5)}

Evaluate on these criteria:
1. Clarity: Is the memory clear and understandable?
2. Completeness: Does it contain sufficient detail?
3. Actionability: Can others act on this information?
4. Specificity: Is it specific enough to be useful?
5. Context: Is there enough context to understand when/why it applies?

Provide:
- Overall score (0.0-1.0)
- Key strengths
- Areas for improvement
- Specific recommendations

Return as JSON with fields: score, strengths, improvements, recommendations."""
    
    response = call_llm(prompt, system)
    
    try:
        response_clean = _clean_json_response(response)
        validation = json.loads(response_clean)
        
        # Ensure required fields
        return {
            "score": max(0.0, min(1.0, float(validation.get("score", 0.5)))),
            "strengths": validation.get("strengths", []),
            "improvements": validation.get("improvements", []),
            "recommendations": validation.get("recommendations", [])
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse quality validation: {e}")
        return {
            "score": 0.5,
            "strengths": [],
            "improvements": ["LLM validation failed"],
            "recommendations": ["Manual review recommended"]
        }


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract JSON."""
    # Remove markdown code blocks
    if "```json" in response:
        response = response.split("```json", 1)[1].split("```", 1)[0]
    elif "```" in response:
        parts = response.split("```")
        if len(parts) >= 3:
            response = parts[1]
    
    # Find JSON-like content
    response = response.strip()
    
    # Find first [ or { and last ] or }
    start_bracket = min(
        (response.find('[') if '[' in response else len(response)),
        (response.find('{') if '{' in response else len(response))
    )
    
    if start_bracket < len(response):
        if response[start_bracket] == '[':
            end_bracket = response.rfind(']')
        else:
            end_bracket = response.rfind('}')
        
        if end_bracket > start_bracket:
            response = response[start_bracket:end_bracket + 1]
    
    return response


if __name__ == "__main__":
    """Test LLM integration."""
    print("Testing collaborative memory LLM integration...")
    
    # Test basic call
    response = call_llm("What makes a good team memory?", 
                       "You are a team collaboration expert.")
    print(f"Basic LLM call: {response[:100]}...")
    
    # Test memory extraction
    conversation = """
    Alice: We decided to use React for the frontend after comparing it with Vue.
    Bob: Yeah, the component reusability was the main factor.
    Alice: We should remember that the learning curve was steeper than expected.
    Bob: Next time we should budget more time for team training.
    """
    
    context = {"team_id": "frontend_team", "participants": ["Alice", "Bob"]}
    memories = extract_memories_from_conversation(conversation, context)
    print(f"Extracted {len(memories)} memories from conversation")
    
    # Test synthesis
    if memories:
        insight = synthesize_team_insight(memories, {"domains": ["frontend", "web_development"]})
        print(f"Synthesized insight: {insight[:100]}...")
    
    print("Collaborative memory LLM integration test completed!")