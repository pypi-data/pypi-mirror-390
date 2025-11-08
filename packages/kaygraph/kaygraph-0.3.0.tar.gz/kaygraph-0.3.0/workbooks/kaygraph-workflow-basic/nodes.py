"""
Workflow nodes implementing basic patterns.
These nodes demonstrate how to build simple linear workflows.
"""

import json
import logging
from typing import Dict, Any, Optional
from kaygraph import Node
from utils import call_llm


class InputNode(Node):
    """
    Input node - receives and prepares user input.
    
    This is typically the first node in a workflow.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user input from shared state."""
        user_input = shared.get("user_input", "")
        if not user_input:
            raise ValueError("No user input provided")
        
        self.logger.info(f"Processing input: {user_input}")
        return user_input
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Validate and prepare input."""
        # Simple validation
        cleaned_input = prep_res.strip()
        
        return {
            "original": prep_res,
            "cleaned": cleaned_input,
            "length": len(cleaned_input),
            "words": len(cleaned_input.split())
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store processed input."""
        shared["processed_input"] = exec_res
        self.logger.info(f"Input processed: {exec_res['words']} words")
        return None  # Continue to default next node


class ProcessNode(Node):
    """
    Process node - performs main processing logic.
    
    This node does the core work of the workflow.
    """
    
    def __init__(self, task_type: str = "general", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_type = task_type
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for processing."""
        processed_input = shared.get("processed_input", {})
        if not processed_input:
            raise ValueError("No processed input found")
        
        return {
            "text": processed_input["cleaned"],
            "task_type": self.task_type
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Execute main processing using LLM."""
        text = prep_res["text"]
        task_type = prep_res["task_type"]
        
        # Different prompts based on task type
        if task_type == "limerick":
            prompt = f"Write a limerick about: {text}"
            system = "You are a creative poet who writes fun limericks."
        elif task_type == "summary":
            prompt = f"Summarize this text in 2-3 sentences: {text}"
            system = "You are a concise summarizer."
        elif task_type == "analyze":
            prompt = f"Analyze the sentiment and key themes in: {text}"
            system = "You are a text analyst."
        else:
            prompt = f"Process this text: {text}"
            system = "You are a helpful assistant."
        
        self.logger.info(f"Processing with task type: {task_type}")
        response = call_llm(prompt, system)
        
        return response
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Store processing result."""
        shared["process_result"] = exec_res
        shared["task_type"] = prep_res["task_type"]
        return None


class EnhanceNode(Node):
    """
    Enhance node - improves or enriches the processed output.
    
    Optional node that adds polish to results.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get processing result."""
        result = shared.get("process_result", "")
        task_type = shared.get("task_type", "general")
        
        if not result:
            raise ValueError("No process result found")
        
        return {"result": result, "task_type": task_type}
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Enhance the result."""
        result = prep_res["result"]
        task_type = prep_res["task_type"]
        
        # Different enhancements based on task type
        if task_type == "limerick":
            prompt = f"Add a title and format this limerick nicely:\n{result}"
            system = "You are a poetry formatter. Add a clever title and nice formatting."
        elif task_type == "summary":
            prompt = f"Add key takeaways as bullet points to this summary:\n{result}"
            system = "You extract key points from summaries."
        else:
            # General enhancement
            prompt = f"Improve the clarity and formatting of:\n{result}"
            system = "You enhance text for better readability."
        
        self.logger.info("Enhancing result...")
        enhanced = call_llm(prompt, system)
        
        return enhanced
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Store enhanced result."""
        shared["enhanced_result"] = exec_res
        shared["enhancement_applied"] = True
        return None


class OutputNode(Node):
    """
    Output node - formats and presents final results.
    
    The last node in the workflow.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all results."""
        return {
            "input": shared.get("processed_input", {}),
            "process_result": shared.get("process_result", ""),
            "enhanced_result": shared.get("enhanced_result", ""),
            "enhancement_applied": shared.get("enhancement_applied", False),
            "task_type": shared.get("task_type", "general")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Format final output."""
        # Choose which result to use
        if prep_res["enhancement_applied"] and prep_res["enhanced_result"]:
            final_result = prep_res["enhanced_result"]
            result_type = "enhanced"
        else:
            final_result = prep_res["process_result"]
            result_type = "processed"
        
        return {
            "final_result": final_result,
            "result_type": result_type,
            "input_stats": {
                "original_length": prep_res["input"].get("length", 0),
                "word_count": prep_res["input"].get("words", 0)
            },
            "task_type": prep_res["task_type"]
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Store final output."""
        shared["final_output"] = exec_res
        self.logger.info(f"Workflow completed: {exec_res['result_type']} result")
        return None


class DataCleanNode(Node):
    """
    Data cleaning node for data processing workflows.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get raw data."""
        return shared.get("raw_data", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Clean the data."""
        # Simple cleaning operations
        cleaned = prep_res.strip()
        cleaned = " ".join(cleaned.split())  # Normalize whitespace
        
        # Remove special characters if needed
        import re
        cleaned_alpha = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', cleaned)
        
        return {
            "original": prep_res,
            "cleaned": cleaned,
            "cleaned_alpha": cleaned_alpha,
            "removed_chars": len(prep_res) - len(cleaned)
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store cleaned data."""
        shared["cleaned_data"] = exec_res["cleaned"]
        shared["cleaning_stats"] = {
            "removed_chars": exec_res["removed_chars"]
        }
        self.logger.info(f"Data cleaned: removed {exec_res['removed_chars']} chars")
        return None


class DataTransformNode(Node):
    """
    Data transformation node.
    """
    
    def __init__(self, transform_type: str = "uppercase", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transform_type = transform_type
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get cleaned data."""
        return shared.get("cleaned_data", "")
    
    def exec(self, prep_res: str) -> str:
        """Transform the data."""
        if self.transform_type == "uppercase":
            return prep_res.upper()
        elif self.transform_type == "lowercase":
            return prep_res.lower()
        elif self.transform_type == "title":
            return prep_res.title()
        elif self.transform_type == "reverse":
            return prep_res[::-1]
        else:
            return prep_res
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store transformed data."""
        shared["transformed_data"] = exec_res
        shared["transform_type"] = self.transform_type
        self.logger.info(f"Data transformed: {self.transform_type}")
        return None


class DataEnrichNode(Node):
    """
    Data enrichment node - adds metadata.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get transformed data."""
        return shared.get("transformed_data", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Enrich with metadata."""
        # Calculate statistics
        words = prep_res.split()
        unique_words = set(word.lower() for word in words)
        
        # Simple sentiment (very basic)
        positive_words = {"good", "great", "excellent", "happy", "love"}
        negative_words = {"bad", "terrible", "sad", "hate", "awful"}
        
        positive_count = sum(1 for word in unique_words if word in positive_words)
        negative_count = sum(1 for word in unique_words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "text": prep_res,
            "metadata": {
                "word_count": len(words),
                "unique_words": len(unique_words),
                "char_count": len(prep_res),
                "sentiment": sentiment,
                "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store enriched data."""
        shared["enriched_data"] = exec_res
        self.logger.info(f"Data enriched with metadata: {exec_res['metadata']['sentiment']} sentiment")
        return None


class ErrorHandlerNode(Node):
    """
    Error handler node - demonstrates graceful failure handling.
    """
    
    def __init__(self, error_action: str = "log", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_action = error_action
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Check for errors in workflow."""
        return {
            "has_error": shared.get("workflow_error", False),
            "error_message": shared.get("error_message", ""),
            "error_step": shared.get("error_step", "")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the error."""
        if not prep_res["has_error"]:
            return {"action": "continue", "message": "No errors found"}
        
        # Different error handling strategies
        if self.error_action == "retry":
            return {
                "action": "retry",
                "message": f"Retrying after error in {prep_res['error_step']}"
            }
        elif self.error_action == "skip":
            return {
                "action": "skip",
                "message": f"Skipping {prep_res['error_step']} due to error"
            }
        elif self.error_action == "fallback":
            return {
                "action": "fallback",
                "message": "Using fallback processing"
            }
        else:
            return {
                "action": "log",
                "message": f"Error logged: {prep_res['error_message']}"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Apply error handling decision."""
        shared["error_handled"] = True
        shared["error_action"] = exec_res["action"]
        
        # Return different actions based on handling
        if exec_res["action"] == "retry":
            return "retry"
        elif exec_res["action"] == "skip":
            return "skip"
        elif exec_res["action"] == "fallback":
            return "fallback"
        else:
            return None  # Continue normally