"""
Intelligence nodes implementing the fundamental AI building block.
These nodes demonstrate different patterns for LLM interaction.
"""

import logging
from typing import Dict, Any, Optional
from kaygraph import Node
from utils import call_llm


class BasicIntelligenceNode(Node):
    """
    The simplest form of intelligence - text in, text out.
    
    This node demonstrates the fundamental pattern: prepare context,
    make expensive LLM call, process response.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Extract the prompt from shared state."""
        prompt = shared.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided in shared state")
        
        self.logger.info(f"Preparing to process prompt: {prompt[:50]}...")
        return prompt
    
    def exec(self, prep_res: str) -> str:
        """
        Make the LLM call - this is the expensive operation.
        
        Key principle: This is the ONLY place where AI happens.
        Everything else is just regular code.
        """
        self.logger.info("Calling LLM...")
        response = call_llm(prep_res)
        self.logger.info(f"Received response: {len(response)} characters")
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store the response and decide next action."""
        shared["response"] = exec_res
        shared["prompt_processed"] = prep_res
        
        # In this simple example, we're done
        return None  # Default action


class ContextAwareIntelligenceNode(Node):
    """
    Intelligence with context management - system prompts and conversation history.
    
    This demonstrates how to enhance the basic intelligence with context,
    which is crucial for getting good responses from LLMs.
    """
    
    def __init__(self, system_prompt: Optional[str] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare prompt with context."""
        prompt = shared.get("prompt", "")
        if not prompt:
            raise ValueError("No prompt provided")
        
        # Gather any additional context
        context = {
            "prompt": prompt,
            "system": self.system_prompt,
            "temperature": shared.get("temperature", 0.7),
            "model": shared.get("model", None)
        }
        
        # Add conversation history if available
        if "history" in shared:
            context["history"] = shared["history"]
        
        self.logger.info(f"Prepared context with system prompt: {self.system_prompt[:50]}...")
        return context
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Make context-aware LLM call."""
        response = call_llm(
            prompt=prep_res["prompt"],
            system=prep_res["system"],
            model=prep_res.get("model"),
            temperature=prep_res.get("temperature", 0.7)
        )
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Update conversation history."""
        shared["response"] = exec_res
        
        # Maintain conversation history
        if "history" not in shared:
            shared["history"] = []
        
        shared["history"].append({
            "role": "user",
            "content": prep_res["prompt"]
        })
        shared["history"].append({
            "role": "assistant", 
            "content": exec_res
        })
        
        return None


class CreativeIntelligenceNode(Node):
    """
    Intelligence with creativity control via temperature.
    
    Demonstrates how temperature affects LLM responses:
    - Low (0.0-0.3): Deterministic, factual
    - Medium (0.4-0.7): Balanced
    - High (0.8-1.0): Creative, varied
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare prompt with creativity settings."""
        prompt = shared.get("prompt", "")
        task_type = shared.get("task_type", "balanced")
        
        # Set temperature based on task type
        temperature_map = {
            "factual": 0.1,      # Very deterministic
            "analytical": 0.3,   # Mostly deterministic
            "balanced": 0.7,     # Default balanced
            "creative": 0.9,     # Very creative
            "brainstorm": 1.0    # Maximum creativity
        }
        
        temperature = temperature_map.get(task_type, 0.7)
        
        # Adjust system prompt based on task
        system_prompts = {
            "factual": "You are a precise AI that provides accurate, factual information.",
            "analytical": "You are an analytical AI that provides detailed analysis.",
            "balanced": "You are a helpful AI assistant.",
            "creative": "You are a creative AI that thinks outside the box.",
            "brainstorm": "You are a brainstorming partner generating diverse ideas."
        }
        
        return {
            "prompt": prompt,
            "temperature": temperature,
            "system": system_prompts.get(task_type, system_prompts["balanced"]),
            "task_type": task_type
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Make temperature-controlled LLM call."""
        self.logger.info(f"Calling LLM with temperature {prep_res['temperature']} for {prep_res['task_type']} task")
        
        response = call_llm(
            prompt=prep_res["prompt"],
            system=prep_res["system"],
            temperature=prep_res["temperature"]
        )
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Store response with metadata."""
        shared["response"] = exec_res
        shared["temperature_used"] = prep_res["temperature"]
        shared["task_type"] = prep_res["task_type"]
        
        return None


class StreamingIntelligenceNode(Node):
    """
    Intelligence with streaming support for real-time responses.
    
    Note: This is a simplified example. Full streaming would require
    async support and websockets for real-time UI updates.
    """
    
    def __init__(self, chunk_callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_callback = chunk_callback or self._default_callback
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _default_callback(self, chunk: str):
        """Default callback just prints chunks."""
        print(chunk, end='', flush=True)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare prompt for streaming."""
        prompt = shared.get("prompt", "")
        shared["streaming"] = True
        return prompt
    
    def exec(self, prep_res: str) -> str:
        """
        Simulate streaming response.
        
        In a real implementation, this would use the streaming APIs
        from OpenAI/Anthropic and yield chunks as they arrive.
        """
        # For now, we'll get the full response and simulate streaming
        response = call_llm(prep_res)
        
        # Simulate streaming by chunking the response
        words = response.split()
        chunks = []
        current_chunk = []
        
        for i, word in enumerate(words):
            current_chunk.append(word)
            if i % 5 == 4:  # Every 5 words
                chunk = ' '.join(current_chunk) + ' '
                chunks.append(chunk)
                self.chunk_callback(chunk)
                current_chunk = []
        
        # Don't forget remaining words
        if current_chunk:
            chunk = ' '.join(current_chunk)
            chunks.append(chunk)
            self.chunk_callback(chunk)
        
        print()  # New line after streaming
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store complete response."""
        shared["response"] = exec_res
        shared["streamed"] = True
        return None