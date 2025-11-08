#!/usr/bin/env python3
"""
Complete KayGraph Example: Research Assistant
=============================================
This example combines multiple patterns into a working system:
- Agent (decision making)
- RAG (document retrieval)
- Workflow (multi-step pipeline)
- Human-in-the-loop (approval for actions)
- Batch processing (handle multiple queries)

This is a REAL, WORKING implementation using Ollama (free, local LLM).

Setup:
1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
2. Pull model: ollama pull llama3.2
3. Start server: ollama serve
4. Run: python main.py
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, List
from kaygraph import Node, Graph, BatchNode, ValidatedNode

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import our real LLM implementation
from utils.call_llm import call_llm, call_llm_json


# ============================================================================
# PART 1: AGENT PATTERN - Decision Making
# ============================================================================

class AgentDecisionNode(Node):
    """Agent that decides what action to take based on user query"""
    
    def prep(self, shared):
        return {
            "query": shared.get("query", ""),
            "context": shared.get("context", []),
            "capabilities": ["search_docs", "calculate", "answer", "need_more_info"]
        }
    
    def exec(self, data):
        prompt = f"""You are a research assistant. Analyze this query and decide the best action.

Query: {data['query']}
Current Context: {data.get('context', 'None yet')}

Available actions:
- search_docs: Search through documents for information
- calculate: Perform calculations or data analysis
- answer: Provide final answer (only if you have enough info)
- need_more_info: Ask user for clarification

Respond with JSON: {{"action": "chosen_action", "reasoning": "why this action"}}"""
        
        return call_llm_json(prompt)
    
    def post(self, shared, prep_res, exec_res):
        shared["last_decision"] = exec_res
        action = exec_res.get("action", "answer")
        
        self.logger.info(f"Agent decided: {action} - {exec_res.get('reasoning', '')}")
        
        # Return the action for graph routing
        return action


# ============================================================================
# PART 2: RAG PATTERN - Document Search & Retrieval
# ============================================================================

class DocumentSearchNode(Node):
    """Search through documents (simplified for demo)"""
    
    def prep(self, shared):
        return shared.get("query", "")
    
    def exec(self, query):
        # In real implementation, this would search a vector database
        # For demo, we'll use a simple keyword search
        
        documents = [
            {"id": 1, "content": "KayGraph is a framework for building AI workflows using graphs."},
            {"id": 2, "content": "Nodes process data in three steps: prep, exec, and post."},
            {"id": 3, "content": "Graphs connect nodes using actions and the >> operator."},
            {"id": 4, "content": "BatchNode processes multiple items efficiently."},
            {"id": 5, "content": "AsyncNode handles asynchronous operations."}
        ]
        
        # Simple keyword matching
        query_lower = query.lower()
        results = []
        for doc in documents:
            if any(word in doc["content"].lower() for word in query_lower.split()):
                results.append(doc["content"])
        
        return results[:3]  # Return top 3 matches
    
    def post(self, shared, prep_res, exec_res):
        # Add results to context
        if "context" not in shared:
            shared["context"] = []
        shared["context"].extend(exec_res)
        
        self.logger.info(f"Found {len(exec_res)} relevant documents")
        
        # Go back to agent for next decision
        return "decide"


# ============================================================================
# PART 3: WORKFLOW PATTERN - Multi-step Processing
# ============================================================================

class CalculateNode(ValidatedNode):
    """Perform calculations with validation"""
    
    def validate_input(self, prep_res):
        if not prep_res:
            raise ValueError("No calculation requested")
        return prep_res
    
    def prep(self, shared):
        return shared.get("query", "")
    
    def exec(self, query):
        prompt = f"""Extract and solve any mathematical calculations from this query.
Query: {query}

Provide step-by-step solution and final answer.
If no calculations needed, say 'No calculations required.'"""
        
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        shared["calculation_result"] = exec_res
        if "context" not in shared:
            shared["context"] = []
        shared["context"].append(f"Calculation: {exec_res}")
        
        # Go back to agent
        return "decide"


class AnswerNode(Node):
    """Generate final answer based on all context"""
    
    def prep(self, shared):
        return {
            "query": shared.get("query", ""),
            "context": shared.get("context", []),
            "calculation": shared.get("calculation_result", "")
        }
    
    def exec(self, data):
        context_str = "\n".join(data["context"]) if data["context"] else "No additional context"
        
        prompt = f"""Based on the following information, provide a comprehensive answer.

Original Question: {data['query']}

Context Information:
{context_str}

Calculations (if any): {data.get('calculation', 'None')}

Provide a clear, helpful answer:"""
        
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        shared["final_answer"] = exec_res
        self.logger.info("Generated final answer")
        
        # Move to approval step
        return "approve"


# ============================================================================
# PART 4: HUMAN-IN-THE-LOOP - Approval Process
# ============================================================================

class HumanApprovalNode(Node):
    """Simulate human approval (in real app, this would wait for user input)"""
    
    def prep(self, shared):
        return shared.get("final_answer", "")
    
    def exec(self, answer):
        # In real implementation, this would:
        # 1. Send to UI for human review
        # 2. Wait for approval/rejection
        # 3. Return the decision
        
        # For demo, auto-approve if answer exists
        if answer and len(answer) > 20:
            return {"approved": True, "feedback": "Looks good!"}
        else:
            return {"approved": False, "feedback": "Need more detail"}
    
    def post(self, shared, prep_res, exec_res):
        shared["approval"] = exec_res
        
        if exec_res["approved"]:
            self.logger.info("Answer approved by human")
            return "deliver"
        else:
            self.logger.info(f"Answer rejected: {exec_res['feedback']}")
            shared["context"].append(f"Feedback: {exec_res['feedback']}")
            return "decide"  # Go back to agent with feedback


class DeliverResultNode(Node):
    """Deliver the final result to user"""
    
    def prep(self, shared):
        return {
            "query": shared.get("query"),
            "answer": shared.get("final_answer"),
            "sources": shared.get("context", [])
        }
    
    def exec(self, data):
        # Format the final response
        return {
            "status": "success",
            "question": data["query"],
            "answer": data["answer"],
            "sources_used": len(data["sources"]),
            "confidence": "high" if len(data["sources"]) > 2 else "medium"
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        
        # Print result for user
        print("\n" + "="*60)
        print("RESEARCH COMPLETE")
        print("="*60)
        print(f"Question: {exec_res['question']}")
        print(f"Answer: {exec_res['answer']}")
        print(f"Confidence: {exec_res['confidence']}")
        print(f"Sources Used: {exec_res['sources_used']}")
        print("="*60 + "\n")
        
        return None  # End of workflow


class NeedMoreInfoNode(Node):
    """Ask user for clarification"""
    
    def prep(self, shared):
        return shared.get("query", "")
    
    def exec(self, query):
        prompt = f"""The user asked: '{query}'
This is unclear. Generate a clarifying question to better understand what they need."""
        
        return call_llm(prompt)
    
    def post(self, shared, prep_res, exec_res):
        print(f"\n❓ Clarification needed: {exec_res}")
        
        # In real app, wait for user response
        # For demo, we'll add mock clarification
        shared["query"] += " (specifically about implementation details)"
        shared["context"].append(f"User clarified: implementation details requested")
        
        return "decide"


# ============================================================================
# PART 5: BATCH PATTERN - Handle Multiple Queries
# ============================================================================

class BatchQueryProcessor(BatchNode):
    """Process multiple queries in batch"""
    
    def prep(self, shared):
        # Return list of queries to process
        return shared.get("batch_queries", [])
    
    def exec(self, query):
        # Each query goes through the full workflow
        sub_graph = create_research_graph()
        sub_shared = {"query": query}
        sub_graph.run(sub_shared)
        return sub_shared.get("result", {"status": "failed"})
    
    def post(self, shared, prep_res, exec_res):
        shared["batch_results"] = exec_res
        
        print("\n📊 Batch Processing Complete:")
        for i, result in enumerate(exec_res, 1):
            print(f"{i}. {result.get('status', 'unknown')}")


# ============================================================================
# GRAPH CONSTRUCTION - Connecting Everything
# ============================================================================

def create_research_graph():
    """Create the complete research assistant graph"""
    
    # Create all nodes
    decide = AgentDecisionNode(node_id="agent_decide")
    search = DocumentSearchNode(node_id="search_docs")
    calculate = CalculateNode(node_id="calculate")
    answer = AnswerNode(node_id="generate_answer")
    approve = HumanApprovalNode(node_id="human_approval")
    deliver = DeliverResultNode(node_id="deliver_result")
    need_info = NeedMoreInfoNode(node_id="need_more_info")
    
    # Connect nodes based on actions
    # Agent decision routing
    decide - "search_docs" >> search
    decide - "calculate" >> calculate
    decide - "answer" >> answer
    decide - "need_more_info" >> need_info
    
    # After search or calculate, go back to agent
    search - "decide" >> decide
    calculate - "decide" >> decide
    need_info - "decide" >> decide
    
    # Answer flow with approval
    answer - "approve" >> approve
    approve - "deliver" >> deliver
    approve - "decide" >> decide  # If rejected, back to agent
    
    # Create graph starting with agent
    return Graph(decide)


def create_batch_graph():
    """Create a batch processing graph"""
    batch_processor = BatchQueryProcessor(node_id="batch_processor")
    return Graph(batch_processor)


# ============================================================================
# MAIN - Demonstration
# ============================================================================

def main():
    print("🤖 KayGraph Complete Example: Research Assistant")
    print("="*60)
    print("This demonstrates:")
    print("✓ Agent pattern (decision making)")
    print("✓ RAG pattern (document search)")
    print("✓ Workflow pattern (multi-step)")
    print("✓ Human-in-the-loop (approval)")
    print("✓ Batch processing")
    print("="*60)
    
    # Example 1: Single Query
    print("\n📝 Example 1: Single Research Query")
    print("-"*40)
    
    graph = create_research_graph()
    shared = {
        "query": "What is KayGraph and how do nodes work?",
        "context": []
    }
    
    graph.run(shared)
    
    # Example 2: Batch Processing
    print("\n📝 Example 2: Batch Processing Multiple Queries")
    print("-"*40)
    
    batch_graph = create_batch_graph()
    batch_shared = {
        "batch_queries": [
            "What is a Node in KayGraph?",
            "How do I connect nodes?",
            "What is BatchNode used for?"
        ]
    }
    
    batch_graph.run(batch_shared)
    
    print("\n✅ Complete example finished!")
    print("\nThis example showed how to combine:")
    print("• Agent decision making")
    print("• Document retrieval (RAG)")
    print("• Multi-step workflows")
    print("• Human approval loops")
    print("• Batch processing")
    print("\nAll with REAL, WORKING code using Ollama!")


if __name__ == "__main__":
    main()