"""
Memory nodes implementing different conversation memory strategies.
These nodes demonstrate various patterns for maintaining context across interactions.
"""

import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node
from utils import call_llm
from utils.memory_utils import (
    format_messages_for_llm,
    trim_messages_to_fit,
    save_conversation,
    load_conversation,
    summarize_messages,
    format_memory_stats
)


class BasicMemoryNode(Node):
    """
    Basic memory implementation - stores complete conversation history.
    
    This is the simplest form of memory: just keep all messages and
    include them in each LLM call. Works well for short conversations
    but can hit context limits with long ones.
    """
    
    def __init__(self, system_prompt: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare conversation context with full history."""
        # Get current prompt
        prompt = shared.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided")
        
        # Get conversation history
        if "messages" not in shared:
            shared["messages"] = []
        
        # Format messages for LLM
        messages_for_llm = format_messages_for_llm(
            shared["messages"],
            self.system_prompt
        )
        
        # Add current user message
        messages_for_llm.append({"role": "user", "content": prompt})
        
        self.logger.info(f"Prepared context with {len(shared['messages'])} historical messages")
        
        return {
            "messages": messages_for_llm,
            "user_prompt": prompt,
            "history_length": len(shared["messages"])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Make LLM call with conversation history."""
        messages = prep_res["messages"]
        
        # Call LLM with formatted messages
        # Extract system prompt if present
        system = None
        if messages and messages[0]["role"] == "system":
            system = messages[0]["content"]
            messages = messages[1:]
        
        # Convert to prompt format for our simple LLM interface
        # In production, you'd use the messages API directly
        if len(messages) == 1:
            # Just the current prompt
            response = call_llm(messages[0]["content"], system=system)
        else:
            # Include conversation history in prompt
            conversation = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in messages[:-1]
            ])
            current_prompt = messages[-1]["content"]
            
            full_prompt = f"Previous conversation:\n{conversation}\n\nCurrent message: {current_prompt}"
            response = call_llm(full_prompt, system=system)
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Update conversation history with new messages."""
        # Add user message to history
        shared["messages"].append({
            "role": "user",
            "content": prep_res["user_prompt"]
        })
        
        # Add assistant response to history
        shared["messages"].append({
            "role": "assistant",
            "content": exec_res
        })
        
        # Store response for easy access
        shared["response"] = exec_res
        
        # Log memory stats
        stats = format_memory_stats(shared["messages"])
        self.logger.info(f"Memory stats: {stats['message_count']} messages, ~{stats['total_tokens']} tokens")
        
        return None


class WindowedMemoryNode(Node):
    """
    Windowed memory - keeps only the most recent N messages.
    
    This prevents memory overflow by maintaining a sliding window
    of conversation history. Older messages are dropped.
    """
    
    def __init__(self, window_size: int = 10, system_prompt: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window_size = window_size
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context with windowed history."""
        prompt = shared.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided")
        
        # Initialize messages if needed
        if "messages" not in shared:
            shared["messages"] = []
        
        # Apply windowing - keep only recent messages
        windowed_messages = shared["messages"][-self.window_size:]
        
        # Format for LLM
        messages_for_llm = format_messages_for_llm(
            windowed_messages,
            self.system_prompt
        )
        messages_for_llm.append({"role": "user", "content": prompt})
        
        self.logger.info(f"Using {len(windowed_messages)} messages from window (total: {len(shared['messages'])})")
        
        return {
            "messages": messages_for_llm,
            "user_prompt": prompt,
            "windowed_count": len(windowed_messages),
            "total_count": len(shared["messages"])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Make LLM call with windowed history."""
        # Same as BasicMemoryNode
        messages = prep_res["messages"]
        
        system = None
        if messages and messages[0]["role"] == "system":
            system = messages[0]["content"]
            messages = messages[1:]
        
        if len(messages) == 1:
            response = call_llm(messages[0]["content"], system=system)
        else:
            conversation = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in messages[:-1]
            ])
            current_prompt = messages[-1]["content"]
            
            full_prompt = f"Recent conversation:\n{conversation}\n\nCurrent message: {current_prompt}"
            response = call_llm(full_prompt, system=system)
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Update history with windowing."""
        # Add new messages
        shared["messages"].append({
            "role": "user",
            "content": prep_res["user_prompt"]
        })
        shared["messages"].append({
            "role": "assistant",
            "content": exec_res
        })
        
        # Apply window limit to stored messages
        if len(shared["messages"]) > self.window_size * 2:
            # Keep some buffer in storage even if we only use window_size in context
            shared["messages"] = shared["messages"][-(self.window_size * 2):]
            self.logger.info(f"Trimmed message history to {len(shared['messages'])} messages")
        
        shared["response"] = exec_res
        return None


class SummarizedMemoryNode(Node):
    """
    Summarized memory - compresses old conversations to save space.
    
    When conversation gets too long, old messages are summarized
    into key points, keeping full detail only for recent messages.
    """
    
    def __init__(
        self, 
        max_messages: int = 20,
        summary_threshold: int = 10,
        system_prompt: Optional[str] = None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context with summarized history."""
        prompt = shared.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided")
        
        # Initialize if needed
        if "messages" not in shared:
            shared["messages"] = []
        if "conversation_summary" not in shared:
            shared["conversation_summary"] = ""
        
        # Check if we need to summarize
        if len(shared["messages"]) > self.max_messages:
            self._summarize_old_messages(shared)
        
        # Build context
        context_parts = []
        
        # Add summary if exists
        if shared["conversation_summary"]:
            context_parts.append(f"Previous conversation summary:\n{shared['conversation_summary']}")
        
        # Add recent messages
        if shared["messages"]:
            recent_conversation = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in shared["messages"]
            ])
            context_parts.append(f"Recent conversation:\n{recent_conversation}")
        
        # Combine context
        full_context = "\n\n".join(context_parts) if context_parts else ""
        
        return {
            "prompt": prompt,
            "context": full_context,
            "has_summary": bool(shared["conversation_summary"]),
            "message_count": len(shared["messages"])
        }
    
    def _summarize_old_messages(self, shared: Dict[str, Any]):
        """Summarize old messages and update storage."""
        # Split messages into old and recent
        old_messages = shared["messages"][:-self.summary_threshold]
        recent_messages = shared["messages"][-self.summary_threshold:]
        
        # Summarize old messages
        old_summary = summarize_messages(old_messages, call_llm)
        
        # Combine with existing summary if any
        if shared["conversation_summary"]:
            combined_prompt = f"""Combine these conversation summaries into one concise summary:

Previous summary:
{shared['conversation_summary']}

New summary:
{old_summary}

Combined summary:"""
            shared["conversation_summary"] = call_llm(combined_prompt)
        else:
            shared["conversation_summary"] = old_summary
        
        # Keep only recent messages
        shared["messages"] = recent_messages
        
        self.logger.info(f"Summarized {len(old_messages)} old messages. Kept {len(recent_messages)} recent.")
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Make LLM call with summarized context."""
        prompt = prep_res["prompt"]
        context = prep_res["context"]
        
        if context:
            full_prompt = f"{context}\n\nCurrent message: {prompt}"
        else:
            full_prompt = prompt
        
        return call_llm(full_prompt, system=self.system_prompt)
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Update history with new messages."""
        # Add new messages
        shared["messages"].append({
            "role": "user",
            "content": prep_res["prompt"]
        })
        shared["messages"].append({
            "role": "assistant",
            "content": exec_res
        })
        
        shared["response"] = exec_res
        
        # Log summary status
        if prep_res["has_summary"]:
            self.logger.info(f"Using summarized history + {prep_res['message_count']} recent messages")
        
        return None


class PersistentMemoryNode(Node):
    """
    Persistent memory - saves and loads conversation history from disk.
    
    This allows conversations to continue across program restarts.
    """
    
    def __init__(
        self,
        save_path: str = "conversations/default.json",
        auto_save: bool = True,
        system_prompt: Optional[str] = None,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.save_path = save_path
        self.auto_save = auto_save
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Load existing conversation on init
        self._loaded = False
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context, loading from disk if needed."""
        # Load conversation on first use
        if not self._loaded:
            loaded_messages = load_conversation(self.save_path)
            if loaded_messages:
                shared["messages"] = loaded_messages
                self.logger.info(f"Loaded {len(loaded_messages)} messages from {self.save_path}")
            self._loaded = True
        
        # Rest is same as BasicMemoryNode
        prompt = shared.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided")
        
        if "messages" not in shared:
            shared["messages"] = []
        
        messages_for_llm = format_messages_for_llm(
            shared["messages"],
            self.system_prompt
        )
        messages_for_llm.append({"role": "user", "content": prompt})
        
        return {
            "messages": messages_for_llm,
            "user_prompt": prompt
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Same as BasicMemoryNode."""
        messages = prep_res["messages"]
        
        system = None
        if messages and messages[0]["role"] == "system":
            system = messages[0]["content"]
            messages = messages[1:]
        
        if len(messages) == 1:
            response = call_llm(messages[0]["content"], system=system)
        else:
            conversation = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in messages[:-1]
            ])
            current_prompt = messages[-1]["content"]
            
            full_prompt = f"Previous conversation:\n{conversation}\n\nCurrent message: {current_prompt}"
            response = call_llm(full_prompt, system=system)
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Update history and save to disk."""
        # Update messages
        shared["messages"].append({
            "role": "user",
            "content": prep_res["user_prompt"]
        })
        shared["messages"].append({
            "role": "assistant",
            "content": exec_res
        })
        
        # Auto-save if enabled
        if self.auto_save:
            save_conversation(shared["messages"], self.save_path)
            self.logger.debug(f"Auto-saved conversation to {self.save_path}")
        
        shared["response"] = exec_res
        return None
    
    def save_conversation(self, shared: Dict[str, Any]):
        """Manually save conversation."""
        if "messages" in shared:
            save_conversation(shared["messages"], self.save_path)
            self.logger.info(f"Saved {len(shared['messages'])} messages to {self.save_path}")