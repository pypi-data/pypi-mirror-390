"""
Memory utility functions for managing conversation history.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


def format_messages_for_llm(messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> List[Dict[str, str]]:
    """
    Format message history for LLM API calls.
    
    Args:
        messages: List of message dictionaries with 'role' and 'content'
        system_prompt: Optional system prompt to prepend
        
    Returns:
        Formatted messages list ready for LLM API
    """
    formatted = []
    
    # Add system prompt if provided
    if system_prompt:
        formatted.append({"role": "system", "content": system_prompt})
    
    # Add conversation history
    formatted.extend(messages)
    
    return formatted


def count_tokens_approximate(text: str) -> int:
    """
    Approximate token count (rough estimate).
    
    Real token counting would use tiktoken or similar, but for
    simplicity we use character count / 4 as approximation.
    """
    return len(text) // 4


def trim_messages_to_fit(messages: List[Dict[str, str]], max_tokens: int = 3000) -> List[Dict[str, str]]:
    """
    Trim message history to fit within token limit.
    
    Keeps most recent messages that fit within limit.
    """
    total_tokens = 0
    kept_messages = []
    
    # Work backwards from most recent
    for msg in reversed(messages):
        msg_tokens = count_tokens_approximate(msg["content"])
        if total_tokens + msg_tokens > max_tokens:
            break
        kept_messages.insert(0, msg)
        total_tokens += msg_tokens
    
    return kept_messages


def save_conversation(messages: List[Dict[str, str]], filepath: str):
    """Save conversation history to file."""
    data = {
        "messages": messages,
        "saved_at": datetime.now().isoformat(),
        "message_count": len(messages)
    }
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def load_conversation(filepath: str) -> List[Dict[str, str]]:
    """Load conversation history from file."""
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return data.get("messages", [])


def summarize_messages(messages: List[Dict[str, str]], call_llm_func) -> str:
    """
    Summarize a list of messages into key points.
    
    This is used for compressing old conversation history.
    """
    if not messages:
        return ""
    
    # Create a conversation transcript
    transcript = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in messages
    ])
    
    prompt = f"""Summarize the following conversation into key points and important context.
Keep the summary concise but preserve critical information.

Conversation:
{transcript}

Summary:"""
    
    return call_llm_func(prompt, system="You are a helpful assistant that creates concise summaries.")


def format_memory_stats(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """Get statistics about current memory usage."""
    if not messages:
        return {
            "message_count": 0,
            "total_tokens": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "oldest_message": None,
            "newest_message": None
        }
    
    total_tokens = sum(count_tokens_approximate(msg["content"]) for msg in messages)
    user_messages = sum(1 for msg in messages if msg["role"] == "user")
    assistant_messages = sum(1 for msg in messages if msg["role"] == "assistant")
    
    return {
        "message_count": len(messages),
        "total_tokens": total_tokens,
        "user_messages": user_messages,
        "assistant_messages": assistant_messages,
        "oldest_message": messages[0]["content"][:50] + "..." if messages else None,
        "newest_message": messages[-1]["content"][:50] + "..." if messages else None
    }