"""
Node implementations for tool workflows.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from kaygraph import Node, BatchNode, ParallelBatchNode, Graph
from tools import TOOL_REGISTRY
from utils import call_llm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _clean_json_response(response: str) -> str:
    """Clean LLM response to extract JSON."""
    response = response.strip()
    
    # Remove thinking tags if present
    if "<think>" in response and "</think>" in response:
        parts = response.split("</think>")
        if len(parts) > 1:
            response = parts[-1].strip()
    
    # Remove markdown code blocks
    if response.startswith("```json"):
        response = response[7:]
    if response.endswith("```"):
        response = response[:-3]
    
    return response.strip()


# ============== Tool Selection Nodes ==============

class ToolSelectorNode(Node):
    """Select appropriate tool based on user query."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Analyze query and select tool."""
        if not query:
            return {"error": "No query provided"}
        
        # Build tool descriptions
        tool_descriptions = []
        for tool_name, tool_info in TOOL_REGISTRY.items():
            metadata = tool_info["metadata"]
            tool_descriptions.append(f"- {tool_name}: {metadata['description']}")
        
        prompt = f"""Analyze the user query and select the most appropriate tool.

Available tools:
{chr(10).join(tool_descriptions)}

User query: {query}

Return a JSON object with:
{{
  "tool": "tool_name",
  "parameters": {{"param1": "value1", ...}},
  "reasoning": "why this tool was selected"
}}

Output JSON only:"""
        
        system = "You are a tool selection expert. Select the best tool for the task."
        
        try:
            response = call_llm(prompt, system, temperature=0.1)
            cleaned = _clean_json_response(response)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Tool selection error: {e}")
            return {"error": str(e)}
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store tool selection."""
        shared["tool_selection"] = exec_res
        
        if "error" in exec_res:
            return "selection_error"
        
        # Store selected tool and parameters for executor
        tool_name = exec_res.get("tool")
        if tool_name in TOOL_REGISTRY:
            shared["selected_tool"] = tool_name
            shared["tool_parameters"] = exec_res.get("parameters", {})
            return None  # Continue to default successor
        
        return "unknown_tool"


class MultiToolSelectorNode(Node):
    """Select multiple tools for complex queries."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Analyze query and select multiple tools if needed."""
        if not query:
            return {"error": "No query provided"}
        
        # Build tool descriptions
        tool_descriptions = []
        for tool_name, tool_info in TOOL_REGISTRY.items():
            metadata = tool_info["metadata"]
            tool_descriptions.append(f"- {tool_name}: {metadata['description']}")
        
        prompt = f"""Analyze the user query and select all appropriate tools needed.

Available tools:
{chr(10).join(tool_descriptions)}

User query: {query}

Return a JSON object with:
{{
  "tools": [
    {{
      "tool": "tool_name",
      "parameters": {{"param1": "value1", ...}},
      "order": 1,
      "depends_on": []
    }}
  ],
  "reasoning": "overall strategy"
}}

Output JSON only:"""
        
        system = "You are a multi-tool orchestration expert. Select all needed tools."
        
        try:
            response = call_llm(prompt, system, temperature=0.1)
            cleaned = _clean_json_response(response)
            return json.loads(cleaned)
        except Exception as e:
            logger.error(f"Multi-tool selection error: {e}")
            return {"error": str(e)}
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Store multi-tool selection."""
        shared["multi_tool_selection"] = exec_res
        
        if "error" in exec_res:
            return "selection_error"
        
        tools = exec_res.get("tools", [])
        if tools:
            shared["selected_tools"] = tools
            return "execute_tools"
        
        return "no_tools_selected"


# ============== Tool Execution Nodes ==============

class ToolExecutorNode(Node):
    """Execute a single tool with parameters."""
    
    def __init__(self, tool_name: Optional[str] = None, **kwargs):
        self.tool_name = tool_name
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get tool and parameters."""
        tool_name = self.tool_name or shared.get("selected_tool")
        parameters = shared.get("tool_parameters", {})
        
        return {
            "tool_name": tool_name,
            "parameters": parameters
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool."""
        tool_name = prep_res.get("tool_name")
        parameters = prep_res.get("parameters", {})
        
        if not tool_name:
            return {"error": "No tool specified"}
        
        if tool_name not in TOOL_REGISTRY:
            return {"error": f"Unknown tool: {tool_name}"}
        
        try:
            # Get tool function
            tool_func = TOOL_REGISTRY[tool_name]["function"]
            
            # Execute tool
            logger.info(f"Executing tool '{tool_name}' with parameters: {parameters}")
            result = tool_func(**parameters)
            
            return {
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "success": result.get("success", True) if isinstance(result, dict) else True
            }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "tool": tool_name,
                "parameters": parameters,
                "error": str(e),
                "success": False
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store tool result."""
        tool_name = prep_res.get("tool_name", "unknown")
        shared[f"{tool_name}_result"] = exec_res
        shared["last_tool_result"] = exec_res
        
        # Return None to continue to default successor
        return None


class ParallelToolExecutorNode(Node):
    """Execute multiple tools in parallel."""
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tools to execute."""
        return shared.get("selected_tools", [])
    
    def exec(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tools in parallel."""
        if not tools:
            return [{"error": "No tools to execute"}]
        
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(tools), 5)) as executor:
            # Submit all tool executions
            future_to_tool = {}
            for tool_info in tools:
                tool_name = tool_info.get("tool")
                parameters = tool_info.get("parameters", {})
                
                if tool_name in TOOL_REGISTRY:
                    tool_func = TOOL_REGISTRY[tool_name]["function"]
                    future = executor.submit(tool_func, **parameters)
                    future_to_tool[future] = (tool_name, parameters)
            
            # Collect results
            for future in as_completed(future_to_tool):
                tool_name, parameters = future_to_tool[future]
                try:
                    result = future.result(timeout=30)
                    results.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "result": result,
                        "success": result.get("success", True) if isinstance(result, dict) else True
                    })
                except Exception as e:
                    logger.error(f"Tool '{tool_name}' execution error: {e}")
                    results.append({
                        "tool": tool_name,
                        "parameters": parameters,
                        "error": str(e),
                        "success": False
                    })
        
        return results
    
    def post(self, shared: Dict[str, Any], prep_res: List[Dict[str, Any]], exec_res: List[Dict[str, Any]]) -> Optional[str]:
        """Store parallel execution results."""
        shared["parallel_tool_results"] = exec_res
        
        # Check if all succeeded
        all_success = all(r.get("success", False) for r in exec_res)
        
        if all_success:
            return "all_tools_success"
        elif any(r.get("success", False) for r in exec_res):
            return "partial_success"
        else:
            return "all_tools_failed"


# ============== Tool Chain Nodes ==============

class ToolChainNode(Node):
    """Execute tools in sequence, passing results between them."""
    
    def prep(self, shared: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get tool chain configuration."""
        return shared.get("tool_chain", [])
    
    def exec(self, chain: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute tool chain."""
        if not chain:
            return {"error": "No tool chain defined"}
        
        results = []
        previous_result = None
        
        for i, tool_info in enumerate(chain):
            tool_name = tool_info.get("tool")
            parameters = tool_info.get("parameters", {})
            
            # Check if this tool uses output from previous
            if tool_info.get("use_previous_output") and previous_result:
                # Merge previous result into parameters
                if isinstance(previous_result, dict):
                    parameters.update(previous_result)
            
            if tool_name not in TOOL_REGISTRY:
                error_result = {
                    "step": i + 1,
                    "tool": tool_name,
                    "error": f"Unknown tool: {tool_name}",
                    "success": False
                }
                results.append(error_result)
                break
            
            try:
                # Execute tool
                tool_func = TOOL_REGISTRY[tool_name]["function"]
                result = tool_func(**parameters)
                
                step_result = {
                    "step": i + 1,
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": result,
                    "success": result.get("success", True) if isinstance(result, dict) else True
                }
                results.append(step_result)
                
                # Store for next iteration
                previous_result = result
                
                # Break chain if tool failed
                if not step_result["success"]:
                    break
                    
            except Exception as e:
                error_result = {
                    "step": i + 1,
                    "tool": tool_name,
                    "parameters": parameters,
                    "error": str(e),
                    "success": False
                }
                results.append(error_result)
                break
        
        return {
            "chain_length": len(chain),
            "executed_steps": len(results),
            "all_success": all(r.get("success", False) for r in results),
            "results": results
        }
    
    def post(self, shared: Dict[str, Any], prep_res: List[Dict[str, Any]], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store chain execution results."""
        shared["tool_chain_results"] = exec_res
        
        if exec_res.get("all_success"):
            return "chain_complete"
        else:
            return "chain_interrupted"


# ============== Result Processing Nodes ==============

class ToolResultFormatterNode(Node):
    """Format tool results for user presentation."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all tool results."""
        return {
            "query": shared.get("query", ""),
            "single_result": shared.get("last_tool_result"),
            "parallel_results": shared.get("parallel_tool_results"),
            "chain_results": shared.get("tool_chain_results")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Format results as user-friendly response."""
        if not prep_res:
            prep_res = {}
            
        query = prep_res.get("query", "")
        
        # Gather all results
        all_results = []
        
        if prep_res.get("single_result"):
            all_results.append(prep_res["single_result"])
        
        if prep_res.get("parallel_results"):
            all_results.extend(prep_res["parallel_results"])
        
        chain_results = prep_res.get("chain_results", {})
        if isinstance(chain_results, dict) and chain_results.get("results"):
            all_results.extend(chain_results["results"])
        
        if not all_results:
            return "I couldn't process your request. No tools were executed."
        
        # Format with LLM
        prompt = f"""Format the following tool execution results into a clear, user-friendly response.

User query: {query}

Tool results:
{json.dumps(all_results, indent=2)}

Create a natural language response that:
1. Directly answers the user's question
2. Includes relevant data from the tools
3. Is concise and well-formatted
4. Mentions any errors in a helpful way

Response:"""
        
        system = "You are a helpful assistant formatting tool results for users."
        
        try:
            response = call_llm(prompt, system, temperature=0.3)
            return response
        except Exception as e:
            # Fallback formatting
            return f"Here are the results for your query '{query}':\n\n{json.dumps(all_results, indent=2)}"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str) -> Optional[str]:
        """Store formatted response."""
        shared["formatted_response"] = exec_res
        return None


class ToolErrorHandlerNode(Node):
    """Handle tool execution errors with retries or fallbacks."""
    
    def __init__(self, max_retries: int = 2, **kwargs):
        self.max_retries = max_retries
        super().__init__(**kwargs)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get error information."""
        last_result = shared.get("last_tool_result", {})
        retry_count = shared.get("tool_retry_count", 0)
        
        return {
            "tool": last_result.get("tool"),
            "parameters": last_result.get("parameters", {}),
            "error": last_result.get("error"),
            "retry_count": retry_count
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Determine error handling strategy."""
        tool_name = prep_res.get("tool")
        error = prep_res.get("error")
        retry_count = prep_res.get("retry_count", 0)
        
        if retry_count < self.max_retries:
            # Try to fix parameters
            return {
                "action": "retry",
                "tool": tool_name,
                "modified_parameters": prep_res.get("parameters"),
                "retry_count": retry_count + 1
            }
        else:
            # Suggest alternative
            return {
                "action": "fallback",
                "original_tool": tool_name,
                "error": error,
                "suggestion": "Try a different approach or tool"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> Optional[str]:
        """Store error handling decision."""
        shared["error_handling"] = exec_res
        
        if exec_res.get("action") == "retry":
            shared["tool_retry_count"] = exec_res.get("retry_count", 0)
            return "retry_tool"
        else:
            return "use_fallback"


# ============== Orchestration Nodes ==============

class ToolOrchestrationNode(Node):
    """Orchestrate complex tool workflows based on query analysis."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user query."""
        return shared.get("query", "")
    
    def exec(self, query: str) -> Dict[str, Any]:
        """Analyze query and design tool workflow."""
        if not query:
            return {"error": "No query provided"}
        
        # Analyze query complexity
        query_lower = query.lower()
        
        # Simple heuristics for demonstration
        if " and " in query_lower or " also " in query_lower:
            # Multiple independent queries - use parallel
            return {
                "strategy": "parallel",
                "reasoning": "Query contains multiple independent requests"
            }
        elif " then " in query_lower or " after " in query_lower:
            # Sequential dependency - use chain
            return {
                "strategy": "chain",
                "reasoning": "Query indicates sequential dependencies"
            }
        else:
            # Single tool
            return {
                "strategy": "single",
                "reasoning": "Query can be handled by a single tool"
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict[str, Any]) -> Optional[str]:
        """Route to appropriate strategy."""
        shared["orchestration_strategy"] = exec_res
        
        strategy = exec_res.get("strategy", "single")
        
        if strategy == "parallel":
            return "parallel_execution"
        elif strategy == "chain":
            return "chain_execution"
        else:
            return "single_execution"