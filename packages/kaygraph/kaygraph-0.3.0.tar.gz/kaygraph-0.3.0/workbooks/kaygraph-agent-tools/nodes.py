"""
Tool nodes implementing external system integration patterns.
These nodes demonstrate how LLMs can use tools to interact with the real world.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from kaygraph import Node
from utils import call_llm
from utils.tools import (
    execute_tool,
    get_tool_descriptions,
    format_tool_result,
    TOOL_REGISTRY
)


class BasicToolNode(Node):
    """
    Basic tool usage - LLM decides if and how to use tools.
    
    This node demonstrates the fundamental pattern:
    1. LLM analyzes user query
    2. Decides if a tool is needed
    3. Selects appropriate tool and parameters
    4. Executes tool
    5. Formats response with tool results
    """
    
    def __init__(self, tools: Optional[List[str]] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tools = tools or list(TOOL_REGISTRY.keys())
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare query and available tools."""
        query = shared.get("query", "")
        if not query:
            raise ValueError("No query provided")
        
        # Get descriptions of available tools
        available_tools = []
        for tool_name in self.tools:
            if tool_name in TOOL_REGISTRY:
                tool_info = TOOL_REGISTRY[tool_name]
                available_tools.append({
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                })
        
        self.logger.info(f"Query: {query}")
        self.logger.info(f"Available tools: {[t['name'] for t in available_tools]}")
        
        return {
            "query": query,
            "tools": available_tools
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """LLM analyzes query and potentially calls tools."""
        query = prep_res["query"]
        tools = prep_res["tools"]
        
        # Create tool descriptions for LLM
        tools_desc = "\n".join([
            f"- {t['name']}: {t['description']}"
            for t in tools
        ])
        
        # First, ask LLM if it needs to use any tools
        analysis_prompt = f"""Analyze this query and determine if you need to use any tools to answer it.

Query: {query}

Available tools:
{tools_desc}

If you need to use a tool, respond with JSON in this format:
{{
    "use_tool": true,
    "tool_name": "name_of_tool",
    "parameters": {{...}},
    "reasoning": "why this tool is needed"
}}

If no tool is needed, respond with:
{{
    "use_tool": false,
    "response": "your direct answer",
    "reasoning": "why no tool is needed"
}}"""
        
        # Get LLM decision
        decision_response = call_llm(
            analysis_prompt,
            system="You are a helpful assistant that can use tools to answer questions. Always respond with valid JSON."
        )
        
        # Parse decision
        try:
            # Clean up response to ensure valid JSON
            decision_response = decision_response.strip()
            if decision_response.startswith("```json"):
                decision_response = decision_response[7:]
            if decision_response.endswith("```"):
                decision_response = decision_response[:-3]
            
            decision = json.loads(decision_response.strip())
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse LLM decision: {e}")
            self.logger.error(f"Response was: {decision_response}")
            # Fallback to direct response
            return {
                "tool_used": False,
                "response": decision_response
            }
        
        # Execute tool if needed
        if decision.get("use_tool", False):
            tool_name = decision.get("tool_name")
            parameters = decision.get("parameters", {})
            
            self.logger.info(f"Using tool: {tool_name} with parameters: {parameters}")
            
            # Execute the tool
            tool_result = execute_tool(tool_name, parameters)
            
            # Format result
            formatted_result = format_tool_result(tool_result)
            
            # Generate final response with tool results
            final_prompt = f"""Based on the tool results, provide a helpful answer to the user's query.

Original query: {query}
Tool used: {tool_name}
Tool result: {formatted_result}

Provide a natural, conversational response that incorporates the tool results."""
            
            final_response = call_llm(final_prompt)
            
            return {
                "tool_used": True,
                "tool_name": tool_name,
                "tool_parameters": parameters,
                "tool_result": tool_result,
                "response": final_response
            }
        else:
            # No tool needed, use direct response
            return {
                "tool_used": False,
                "response": decision.get("response", "I can answer that without using tools.")
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Store results and response."""
        shared["response"] = exec_res["response"]
        shared["tool_used"] = exec_res["tool_used"]
        
        if exec_res["tool_used"]:
            shared["tool_details"] = {
                "name": exec_res["tool_name"],
                "parameters": exec_res["tool_parameters"],
                "result": exec_res["tool_result"]
            }
            self.logger.info(f"Completed with tool: {exec_res['tool_name']}")
        else:
            self.logger.info("Completed without tool usage")
        
        return None


class MultiToolNode(Node):
    """
    Multi-tool usage - can chain multiple tools in sequence.
    
    Example: "Compare weather in Paris and London"
    Requires: get_coordinates for both cities, then get_weather for both
    """
    
    def __init__(self, max_tools: int = 5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_tools = max_tools
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for multi-tool execution."""
        query = shared.get("query", "")
        if not query:
            raise ValueError("No query provided")
        
        return {
            "query": query,
            "available_tools": get_tool_descriptions()
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple tools as needed."""
        query = prep_res["query"]
        tools = prep_res["available_tools"]
        
        # Create execution plan
        plan_prompt = f"""Create a step-by-step plan to answer this query using available tools.

Query: {query}

Available tools:
{json.dumps(tools, indent=2)}

Respond with a JSON array of steps, each with:
{{
    "step": 1,
    "tool": "tool_name",
    "parameters": {{...}},
    "purpose": "what this step accomplishes"
}}

If no tools are needed, return an empty array: []"""
        
        plan_response = call_llm(
            plan_prompt,
            system="You are a planning assistant. Always respond with valid JSON."
        )
        
        # Parse plan
        try:
            # Clean JSON response
            plan_response = plan_response.strip()
            if plan_response.startswith("```json"):
                plan_response = plan_response[7:]
            if plan_response.endswith("```"):
                plan_response = plan_response[:-3]
            
            plan = json.loads(plan_response.strip())
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse plan: {plan_response}")
            plan = []
        
        # Execute plan
        results = []
        for step in plan[:self.max_tools]:  # Limit tool calls
            self.logger.info(f"Executing step {step.get('step')}: {step.get('tool')}")
            
            tool_result = execute_tool(
                step.get("tool"),
                step.get("parameters", {})
            )
            
            results.append({
                "step": step.get("step"),
                "tool": step.get("tool"),
                "purpose": step.get("purpose"),
                "result": tool_result
            })
        
        # Generate final response
        if results:
            results_summary = "\n".join([
                f"Step {r['step']} ({r['tool']}): {format_tool_result(r['result'])}"
                for r in results
            ])
            
            final_prompt = f"""Based on these tool results, answer the user's query comprehensively.

Query: {query}

Tool Results:
{results_summary}

Provide a complete, natural response."""
            
            response = call_llm(final_prompt)
        else:
            response = call_llm(query)
        
        return {
            "plan": plan,
            "results": results,
            "response": response
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Store execution details."""
        shared["response"] = exec_res["response"]
        shared["execution_plan"] = exec_res["plan"]
        shared["tool_results"] = exec_res["results"]
        
        self.logger.info(f"Executed {len(exec_res['results'])} tools")
        return None


class ToolChainNode(Node):
    """
    Tool chaining - output of one tool feeds into the next.
    
    Demonstrates dependent tool execution where each tool's
    output influences the next tool call.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare query."""
        query = shared.get("query", "")
        if not query:
            raise ValueError("No query provided")
        return query
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Execute tool chain based on query."""
        query = prep_res
        
        # Example: Weather query that needs location lookup first
        if "weather" in query.lower():
            # Extract location from query
            location_prompt = f"""Extract the location name from this query. 
Just return the location name, nothing else.

Query: {query}"""
            
            location = call_llm(location_prompt).strip()
            self.logger.info(f"Extracted location: {location}")
            
            # Chain: location -> coordinates -> weather
            chain_results = []
            
            # Step 1: Get coordinates
            coord_result = execute_tool("get_coordinates", {"location": location})
            chain_results.append(("get_coordinates", coord_result))
            
            if "error" not in coord_result:
                # Step 2: Get weather using coordinates
                weather_result = execute_tool("get_weather", {
                    "latitude": coord_result["latitude"],
                    "longitude": coord_result["longitude"],
                    "location_name": coord_result["location"]
                })
                chain_results.append(("get_weather", weather_result))
                
                # Format response
                response = format_tool_result(weather_result)
            else:
                response = f"Could not find location: {location}"
        
        # Example: Time calculation chain
        elif "time" in query.lower() and ("difference" in query.lower() or "between" in query.lower()):
            # Extract two locations
            locations_prompt = f"""Extract two location/timezone names from this query.
Return as JSON: {{"location1": "...", "location2": "..."}}

Query: {query}"""
            
            locations_response = call_llm(locations_prompt)
            try:
                locations = json.loads(locations_response)
                
                # Get times for both locations
                time1 = execute_tool("get_time", {"timezone": f"US/{locations['location1']}"})
                time2 = execute_tool("get_time", {"timezone": f"Europe/{locations['location2']}"})
                
                chain_results = [
                    ("get_time_1", time1),
                    ("get_time_2", time2)
                ]
                
                # Calculate difference
                if "error" not in time1 and "error" not in time2:
                    response = (f"Time in {locations['location1']}: {time1['current_time']}\n"
                               f"Time in {locations['location2']}: {time2['current_time']}")
                else:
                    response = "Could not get time for one or both locations"
                    
            except:
                response = call_llm(query)
                chain_results = []
        
        else:
            # Default: single tool or no tool
            response = call_llm(query)
            chain_results = []
        
        return {
            "response": response,
            "chain": chain_results
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store chain results."""
        shared["response"] = exec_res["response"]
        shared["tool_chain"] = exec_res["chain"]
        
        if exec_res["chain"]:
            self.logger.info(f"Executed tool chain with {len(exec_res['chain'])} steps")
        
        return None


class SafeToolNode(Node):
    """
    Safe tool usage with validation and confirmation.
    
    Demonstrates best practices:
    - Input validation
    - Parameter sanitization  
    - Confirmation for sensitive operations
    - Error handling
    """
    
    def __init__(self, require_confirmation: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.require_confirmation = require_confirmation
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare with safety checks."""
        query = shared.get("query", "")
        if not query:
            raise ValueError("No query provided")
        
        # Check for potentially dangerous operations
        dangerous_keywords = ["delete", "remove", "destroy", "format", "sudo", "admin"]
        is_dangerous = any(keyword in query.lower() for keyword in dangerous_keywords)
        
        return {
            "query": query,
            "is_dangerous": is_dangerous,
            "confirmation": shared.get("confirmation", False)
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with safety measures."""
        query = prep_res["query"]
        is_dangerous = prep_res["is_dangerous"]
        confirmation = prep_res["confirmation"]
        
        # Block dangerous operations without confirmation
        if is_dangerous and self.require_confirmation and not confirmation:
            return {
                "response": "This operation appears to be potentially dangerous. Please confirm you want to proceed.",
                "requires_confirmation": True,
                "tool_used": False
            }
        
        # Safe tool selection with validation
        safe_tools = ["get_weather", "calculate", "get_time", "get_coordinates"]
        
        # Let LLM pick a safe tool
        tool_prompt = f"""Select an appropriate tool for this query from the safe tools list.

Query: {query}

Safe tools:
{json.dumps([t for t in get_tool_descriptions() if t['name'] in safe_tools], indent=2)}

Respond with JSON:
{{
    "tool": "tool_name",
    "parameters": {{...}}
}}

If no tool is appropriate, respond with:
{{
    "tool": null,
    "reason": "why no tool is needed"
}}"""
        
        tool_response = call_llm(tool_prompt, system="You are a safety-conscious assistant.")
        
        try:
            tool_decision = json.loads(tool_response.strip())
            
            if tool_decision.get("tool") and tool_decision["tool"] in safe_tools:
                # Validate parameters
                params = tool_decision.get("parameters", {})
                
                # Example validation for calculator
                if tool_decision["tool"] == "calculate":
                    expr = params.get("expression", "")
                    # Block potential code execution
                    if any(bad in expr for bad in ["import", "exec", "eval", "__"]):
                        return {
                            "response": "Invalid calculation expression",
                            "tool_used": False,
                            "error": "Security validation failed"
                        }
                
                # Execute safe tool
                result = execute_tool(tool_decision["tool"], params)
                response = format_tool_result(result)
                
                return {
                    "response": response,
                    "tool_used": True,
                    "tool_name": tool_decision["tool"],
                    "validated": True
                }
            else:
                # No tool or unsafe tool
                return {
                    "response": call_llm(query),
                    "tool_used": False
                }
                
        except Exception as e:
            self.logger.error(f"Tool execution error: {e}")
            return {
                "response": "I encountered an error processing your request safely.",
                "tool_used": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Store results with safety metadata."""
        shared["response"] = exec_res["response"]
        shared["tool_used"] = exec_res.get("tool_used", False)
        
        if exec_res.get("requires_confirmation"):
            shared["requires_confirmation"] = True
        
        if exec_res.get("validated"):
            self.logger.info("Tool executed with validation")
        
        return None