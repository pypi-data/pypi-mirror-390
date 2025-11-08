#!/usr/bin/env python3
"""
KayGraph Scaffold - Zero-dependency boilerplate generator for KayGraph patterns

A non-LLM based scaffolding tool to quickly create working KayGraph applications
from production-tested patterns. Based on 47+ real-world workbook examples.

Usage:
    python kaygraph_scaffold.py <pattern> <name> [--output-dir PATH]
    
Examples:
    python kaygraph_scaffold.py node MyTask
    python kaygraph_scaffold.py agent ResearchAgent
    python kaygraph_scaffold.py rag DocumentQA
    python kaygraph_scaffold.py chat CustomerSupport
    python kaygraph_scaffold.py supervisor WorkerManager
"""

import os
import sys
from pathlib import Path
import argparse
from datetime import datetime

TEMPLATES = {
    "node": {
        "description": "Basic node with prep/exec/post lifecycle",
        "files": {
            "nodes.py": '''"""
{name} Node Implementation
Generated on: {date}
"""
from kaygraph import Node


class {class_name}Node(Node):
    """
    {description}
    
    This node follows the standard 3-phase lifecycle:
    1. prep: Read from shared store
    2. exec: Process data (pure computation)
    3. post: Write results to shared store
    """
    
    def prep(self, shared):
        """Prepare data for execution"""
        # Read required data from shared store
        input_data = shared.get("{input_key}", None)
        if input_data is None:
            raise ValueError("{input_key} not found in shared store")
        return input_data
    
    def exec(self, prep_res):
        """Execute the main logic - NO shared access here"""
        # TODO: Implement your processing logic
        # Example: result = process_data(prep_res)
        result = f"Processed: {{prep_res}}"
        return result
    
    def post(self, shared, prep_res, exec_res):
        """Store results and determine next action"""
        # Write results to shared store
        shared["{output_key}"] = exec_res
        
        # Return next action (None means "default")
        return None
''',
            "main.py": '''"""
{name} - Main entry point
Generated on: {date}
"""
from kaygraph import Graph
from nodes import {class_name}Node


def main():
    # Create the node
    {var_name}_node = {class_name}Node("{node_id}")
    
    # Create the graph with start node
    graph = Graph({var_name}_node)
    
    # Define the flow (if multiple nodes)
    # node1 >> node2  # Default action
    # node1 >> ("success", node2)  # Named action
    
    # Prepare shared context
    shared = {{
        "{input_key}": "Your input data here"
    }}
    
    # Run the graph
    graph.run(shared)
    
    # Display results
    print(f"Result: {{shared.get('{output_key}')}}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "async_node": {
        "description": "Async node for I/O-bound operations",
        "files": {
            "nodes.py": '''"""
{name} Async Node Implementation
Generated on: {date}
"""
from kaygraph import AsyncNode
import asyncio


class {class_name}Node(AsyncNode):
    """
    Async node for {description}
    
    Use this pattern for:
    - API calls
    - Database operations
    - File I/O
    - Network requests
    """
    
    async def prep(self, shared):
        """Prepare data for async execution"""
        input_data = shared.get("{input_key}", None)
        if input_data is None:
            raise ValueError("{input_key} not found in shared store")
        return input_data
    
    async def exec(self, prep_res):
        """Execute async operations - NO shared access here"""
        # TODO: Implement your async logic
        # Example: result = await async_api_call(prep_res)
        await asyncio.sleep(0.1)  # Simulate async work
        result = f"Async processed: {{prep_res}}"
        return result
    
    async def post(self, shared, prep_res, exec_res):
        """Store results asynchronously"""
        shared["{output_key}"] = exec_res
        return None
''',
        }
    },
    
    "batch_node": {
        "description": "Batch processing node for data collections",
        "files": {
            "nodes.py": '''"""
{name} Batch Node Implementation
Generated on: {date}
"""
from kaygraph import BatchNode


class {class_name}Node(BatchNode):
    """
    Batch processing node for {description}
    
    Processes collections of items efficiently.
    Each item goes through prep/exec/post independently.
    """
    
    def prep(self, shared):
        """Prepare batch data"""
        items = shared.get("{input_key}", [])
        if not items:
            raise ValueError("No items to process in {input_key}")
        return items
    
    def exec(self, item):
        """Process individual item - called for each item"""
        # TODO: Process each item
        result = f"Processed item: {{item}}"
        return result
    
    def post(self, shared, items, results):
        """Store all results after batch processing"""
        shared["{output_key}"] = results
        
        # Optional: Store summary
        shared["{output_key}_count"] = len(results)
        return None
''',
        }
    },
    
    "agent": {
        "description": "Autonomous agent with decision-making",
        "files": {
            "nodes.py": '''"""
{name} Agent Implementation
Generated on: {date}
"""
from kaygraph import Node


class ObserveNode(Node):
    """Observe the environment and gather information"""
    
    def prep(self, shared):
        return shared.get("environment", {{}})
    
    def exec(self, environment):
        # TODO: Implement observation logic
        observation = {{
            "status": "observed",
            "data": environment
        }}
        return observation
    
    def post(self, shared, prep_res, exec_res):
        shared["observation"] = exec_res
        return "think"  # Next: thinking


class ThinkNode(Node):
    """Analyze observations and plan actions"""
    
    def prep(self, shared):
        return {{
            "observation": shared.get("observation"),
            "history": shared.get("history", [])
        }}
    
    def exec(self, data):
        # TODO: Implement reasoning logic
        # This is where you'd call an LLM for decision making
        thought = {{
            "analysis": "Based on observation...",
            "next_action": "act",
            "confidence": 0.8
        }}
        return thought
    
    def post(self, shared, prep_res, exec_res):
        shared["thought"] = exec_res
        
        # Update history
        history = shared.get("history", [])
        history.append(exec_res)
        shared["history"] = history
        
        return exec_res["next_action"]


class ActNode(Node):
    """Execute the planned action"""
    
    def prep(self, shared):
        return shared.get("thought")
    
    def exec(self, thought):
        # TODO: Implement action execution
        action_result = {{
            "action": "performed_action",
            "success": True,
            "output": "Action completed"
        }}
        return action_result
    
    def post(self, shared, prep_res, exec_res):
        shared["last_action"] = exec_res
        
        # Decide whether to continue or stop
        if exec_res["success"]:
            return "observe"  # Continue the loop
        else:
            return "error"  # Handle error
''',
            "graph.py": '''"""
{name} Agent Graph Configuration
Generated on: {date}
"""
from kaygraph import Graph
from nodes import ObserveNode, ThinkNode, ActNode


def create_agent_graph():
    """Create the agent decision-making graph"""
    # Create nodes
    observe = ObserveNode("observe")
    think = ThinkNode("think")
    act = ActNode("act")
    
    # Create graph with start node
    graph = Graph(observe)
    
    # Define the agent loop
    observe - "think" >> think
    think - "act" >> act
    act - "observe" >> observe  # Loop back
    
    # Optional: Add error handling
    # error_handler = ErrorNode("error")
    # act - "error" >> error_handler
    
    return graph
''',
            "main.py": '''"""
{name} Agent - Main entry point
Generated on: {date}
"""
from graph import create_agent_graph


def main():
    # Create the agent graph
    graph = create_agent_graph()
    
    # Initialize shared context
    shared = {{
        "environment": {{
            "task": "Your task description",
            "constraints": [],
            "resources": []
        }},
        "history": [],
        "max_iterations": 5
    }}
    
    # Run the agent
    graph.run(shared, start_node="observe")
    
    # Display results
    print(f"Final thought: {{shared.get('thought')}}")
    print(f"Last action: {{shared.get('last_action')}}")
    print(f"History length: {{len(shared.get('history', []))}}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "rag": {
        "description": "Retrieval-Augmented Generation pipeline",
        "files": {
            "nodes.py": '''"""
{name} RAG Implementation
Generated on: {date}
"""
from kaygraph import Node, BatchNode


class ChunkDocumentsNode(BatchNode):
    """Split documents into chunks for processing"""
    
    def prep(self, shared):
        return shared.get("documents", [])
    
    def exec(self, document):
        # TODO: Implement chunking logic
        # Simple example - split by paragraphs
        chunks = document.split("\\n\\n")
        return [{{
            "text": chunk.strip(),
            "source": "document",
            "index": i
        }} for i, chunk in enumerate(chunks) if chunk.strip()]
    
    def post(self, shared, docs, all_chunks):
        # Flatten nested list of chunks
        flat_chunks = [chunk for doc_chunks in all_chunks for chunk in doc_chunks]
        shared["chunks"] = flat_chunks
        return "embed"


class EmbedChunksNode(BatchNode):
    """Generate embeddings for chunks"""
    
    def prep(self, shared):
        return shared.get("chunks", [])
    
    def exec(self, chunk):
        # TODO: Generate real embeddings
        # Example: embedding = generate_embedding(chunk["text"])
        import hashlib
        fake_embedding = [float(ord(c)) for c in hashlib.md5(
            chunk["text"].encode()).hexdigest()[:8]]
        
        return {{
            "chunk": chunk,
            "embedding": fake_embedding
        }}
    
    def post(self, shared, chunks, embeddings):
        shared["embeddings"] = embeddings
        return "index"


class CreateIndexNode(Node):
    """Create searchable index from embeddings"""
    
    def prep(self, shared):
        return shared.get("embeddings", [])
    
    def exec(self, embeddings):
        # TODO: Create real vector index
        # Example: index = create_faiss_index(embeddings)
        index = {{
            "type": "simple_index",
            "embeddings": embeddings,
            "dimension": len(embeddings[0]["embedding"]) if embeddings else 0
        }}
        return index
    
    def post(self, shared, prep_res, exec_res):
        shared["index"] = exec_res
        return None  # End of indexing phase


class RetrieveNode(Node):
    """Retrieve relevant chunks for query"""
    
    def prep(self, shared):
        return {{
            "query": shared.get("query"),
            "index": shared.get("index"),
            "top_k": shared.get("top_k", 3)
        }}
    
    def exec(self, data):
        # TODO: Implement vector search
        # Example: results = search_index(data["index"], data["query"], data["top_k"])
        
        # Mock retrieval - return top chunks
        results = data["index"]["embeddings"][:data["top_k"]]
        return results
    
    def post(self, shared, prep_res, exec_res):
        shared["retrieved_chunks"] = exec_res
        return "generate"


class GenerateAnswerNode(Node):
    """Generate answer using retrieved context"""
    
    def prep(self, shared):
        return {{
            "query": shared.get("query"),
            "context": shared.get("retrieved_chunks", [])
        }}
    
    def exec(self, data):
        # TODO: Call LLM with context
        # Example: answer = generate_answer_with_llm(data["query"], data["context"])
        
        context_text = "\\n".join([
            chunk["chunk"]["text"] for chunk in data["context"]
        ])
        
        answer = f"""Based on the context, here's the answer to "{{data['query']}}":
        
        [Generated answer would go here]
        
        Context used: {{len(data['context'])}} chunks"""
        
        return answer
    
    def post(self, shared, prep_res, exec_res):
        shared["answer"] = exec_res
        return None  # End of pipeline
''',
            "graph.py": '''"""
{name} RAG Graph Configuration
Generated on: {date}
"""
from kaygraph import Graph
from nodes import (
    ChunkDocumentsNode, EmbedChunksNode, CreateIndexNode,
    RetrieveNode, GenerateAnswerNode
)


def create_indexing_graph():
    """Create the offline indexing graph"""
    # Indexing nodes
    chunk = ChunkDocumentsNode("chunk")
    embed = EmbedChunksNode("embed")
    index = CreateIndexNode("index")
    
    # Create graph with start node
    graph = Graph(chunk)
    
    # Define flow
    chunk - "embed" >> embed
    embed - "index" >> index
    
    return graph


def create_query_graph():
    """Create the online query graph"""
    # Query nodes
    retrieve = RetrieveNode("retrieve")
    generate = GenerateAnswerNode("generate")
    
    # Create graph with start node
    graph = Graph(retrieve)
    
    # Define flow
    retrieve - "generate" >> generate
    
    return graph
''',
        }
    },
    
    "workflow": {
        "description": "Multi-step workflow orchestration",
        "files": {
            "nodes.py": '''"""
{name} Workflow Implementation
Generated on: {date}
"""
from kaygraph import Node, ValidatedNode


class ValidateInputNode(ValidatedNode):
    """Validate workflow inputs"""
    
    input_schema = {{
        "type": "object",
        "properties": {{
            "{input_key}": {{"type": "string"}},
            "config": {{"type": "object"}}
        }},
        "required": ["{input_key}"]
    }}
    
    def prep(self, shared):
        return {{
            "{input_key}": shared.get("{input_key}"),
            "config": shared.get("config", {{}})
        }}
    
    def exec(self, inputs):
        # Validation happens automatically via ValidatedNode
        return {{"validated": True, "inputs": inputs}}
    
    def post(self, shared, prep_res, exec_res):
        shared["validated_inputs"] = exec_res
        return "process"


class ProcessStep1Node(Node):
    """First processing step"""
    
    def prep(self, shared):
        return shared.get("validated_inputs")
    
    def exec(self, validated_data):
        # TODO: Implement step 1 logic
        result = {{
            "step": 1,
            "status": "completed",
            "output": f"Processed: {{validated_data}}"
        }}
        return result
    
    def post(self, shared, prep_res, exec_res):
        shared["step1_result"] = exec_res
        
        # Conditional routing
        if exec_res["status"] == "completed":
            return "step2"
        else:
            return "error"


class ProcessStep2Node(Node):
    """Second processing step"""
    
    def prep(self, shared):
        return {{
            "step1": shared.get("step1_result"),
            "config": shared.get("config", {{}})
        }}
    
    def exec(self, data):
        # TODO: Implement step 2 logic
        result = {{
            "step": 2,
            "status": "completed",
            "output": f"Enhanced: {{data['step1']['output']}}"
        }}
        return result
    
    def post(self, shared, prep_res, exec_res):
        shared["step2_result"] = exec_res
        return "finalize"


class FinalizeNode(Node):
    """Finalize workflow and prepare output"""
    
    def prep(self, shared):
        return {{
            "step1": shared.get("step1_result"),
            "step2": shared.get("step2_result")
        }}
    
    def exec(self, results):
        # TODO: Combine results and create final output
        final_output = {{
            "status": "success",
            "steps_completed": 2,
            "final_result": results["step2"]["output"],
            "summary": "Workflow completed successfully"
        }}
        return final_output
    
    def post(self, shared, prep_res, exec_res):
        shared["{output_key}"] = exec_res
        return None  # End workflow
''',
        }
    },
    
    "chat": {
        "description": "Interactive chat interface with conversation history",
        "files": {
            "nodes.py": '''"""
{name} Chat Implementation
Generated on: {date}
"""
from kaygraph import Node


class ChatNode(Node):
    """Handle chat interactions with conversation history"""
    
    max_retries = 3  # Retry on LLM failures
    wait = 1.0      # Wait between retries
    
    def prep(self, shared):
        """Prepare chat context"""
        return {
            "user_input": shared.get("user_input"),
            "history": shared.get("history", []),
            "system_prompt": shared.get("system_prompt", "You are a helpful assistant.")
        }
    
    def exec(self, data):
        """Process chat with LLM"""
        # TODO: Implement LLM call
        # Example:
        # from utils.call_llm import call_llm
        # messages = [{"role": "system", "content": data["system_prompt"]}]
        # messages.extend(data["history"])
        # messages.append({"role": "user", "content": data["user_input"]})
        # response = call_llm(messages)
        
        response = f"Response to: {data['user_input']}"
        return response
    
    def exec_fallback(self, prep_res):
        """Fallback if LLM fails"""
        return "I apologize, but I'm having trouble responding right now. Please try again."
    
    def post(self, shared, prep_res, exec_res):
        """Update conversation history"""
        history = shared.get("history", [])
        history.append({"role": "user", "content": prep_res["user_input"]})
        history.append({"role": "assistant", "content": exec_res})
        
        # Keep last N messages to manage context
        max_history = shared.get("max_history", 20)
        shared["history"] = history[-max_history:]
        shared["last_response"] = exec_res
        
        return None
''',
            "main.py": '''"""
{name} Chat Interface
Generated on: {date}
"""
from kaygraph import Graph
from nodes import ChatNode
import sys


def main():
    # Get system prompt from command line or use default
    system_prompt = sys.argv[1] if len(sys.argv) > 1 else "You are a helpful assistant."
    
    # Create graph
    chat_node = ChatNode("chat")
    graph = Graph(chat_node)
    
    # Initialize shared context
    shared = {
        "system_prompt": system_prompt,
        "history": [],
        "max_history": 20
    }
    
    print(f"Chat initialized with: {system_prompt}")
    print("Type 'quit' to exit\\n")
    
    # Chat loop
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
            
        # Update shared context and run
        shared["user_input"] = user_input
        graph.run(shared)
        
        # Display response
        response = shared.get("last_response", "No response")
        print(f"\\nAssistant: {response}\\n")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "parallel_batch": {
        "description": "High-performance parallel batch processing",
        "files": {
            "nodes.py": '''"""
{name} Parallel Batch Implementation
Generated on: {date}
"""
from kaygraph import ParallelBatchNode
import time


class {class_name}Node(ParallelBatchNode):
    """
    Parallel batch processing for {description}
    
    Processes items concurrently using ThreadPoolExecutor.
    Ideal for I/O-bound operations like API calls.
    """
    
    # Configure parallelism
    max_workers = 4  # Number of concurrent workers
    
    def prep(self, shared):
        """Prepare items for parallel processing"""
        items = shared.get("{input_key}", [])
        if not items:
            raise ValueError("No items to process")
        
        print(f"Processing {len(items)} items with {self.max_workers} workers")
        return items
    
    def exec(self, item):
        """Process individual item - runs in parallel"""
        # TODO: Implement your processing logic
        # This runs concurrently for multiple items
        
        # Simulate work
        time.sleep(0.1)
        
        result = {
            "item": item,
            "processed_at": time.time(),
            "result": f"Processed: {item}"
        }
        return result
    
    def post(self, shared, items, results):
        """Aggregate results after parallel processing"""
        shared["{output_key}"] = results
        
        # Calculate performance metrics
        processing_times = [r["processed_at"] for r in results]
        duration = max(processing_times) - min(processing_times) if processing_times else 0
        
        shared["metrics"] = {
            "total_items": len(items),
            "duration": duration,
            "items_per_second": len(items) / duration if duration > 0 else 0
        }
        
        return None
''',
            "main.py": '''"""
{name} Parallel Processing Demo
Generated on: {date}
"""
from kaygraph import Graph
from nodes import {class_name}Node
import time


def main():
    # Create graph
    parallel_node = {class_name}Node("{node_id}")
    graph = Graph(parallel_node)
    
    # Prepare test data
    test_items = [f"item_{i}" for i in range(20)]
    
    shared = {
        "{input_key}": test_items
    }
    
    # Run with timing
    start_time = time.time()
    graph.run(shared)
    total_time = time.time() - start_time
    
    # Display results
    results = shared.get("{output_key}", [])
    metrics = shared.get("metrics", {})
    
    print(f"\\nProcessed {len(results)} items in {total_time:.2f}s")
    print(f"Throughput: {metrics.get('items_per_second', 0):.2f} items/second")
    print(f"\\nFirst result: {results[0] if results else 'None'}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "supervisor": {
        "description": "Supervisor pattern for managing multiple workers",
        "files": {
            "nodes.py": '''"""
{name} Supervisor Pattern Implementation
Generated on: {date}
"""
from kaygraph import Node
import random


class SupervisorNode(Node):
    """Analyze task and assign to appropriate worker"""
    
    def prep(self, shared):
        return {
            "task": shared.get("task"),
            "workers": shared.get("workers", [])
        }
    
    def exec(self, data):
        """Decide which worker should handle the task"""
        task = data["task"]
        workers = data["workers"]
        
        # TODO: Implement worker selection logic
        # Example: based on task type, worker availability, performance
        
        # Simple random selection for demo
        if workers:
            selected_worker = random.choice(workers)
        else:
            selected_worker = "default_worker"
            
        assignment = {
            "task": task,
            "assigned_to": selected_worker,
            "priority": "normal"
        }
        
        return assignment
    
    def post(self, shared, prep_res, exec_res):
        shared["assignment"] = exec_res
        
        # Route to specific worker
        worker_name = exec_res["assigned_to"]
        return f"worker_{worker_name}"


class WorkerNode(Node):
    """Generic worker that processes assigned tasks"""
    
    def __init__(self, node_id, worker_name):
        super().__init__(node_id)
        self.worker_name = worker_name
    
    def prep(self, shared):
        assignment = shared.get("assignment", {})
        if assignment.get("assigned_to") != self.worker_name:
            raise ValueError(f"Task not assigned to {self.worker_name}")
        return assignment
    
    def exec(self, assignment):
        """Process the assigned task"""
        # TODO: Implement task processing
        result = {
            "worker": self.worker_name,
            "task": assignment["task"],
            "status": "completed",
            "output": f"Processed by {self.worker_name}: {assignment['task']}"
        }
        return result
    
    def post(self, shared, prep_res, exec_res):
        shared["result"] = exec_res
        
        # Check if result is satisfactory
        if exec_res["status"] == "completed":
            return "validate"
        else:
            return "retry"


class ValidateResultNode(Node):
    """Validate worker output quality"""
    
    def prep(self, shared):
        return shared.get("result")
    
    def exec(self, result):
        """Validate the result"""
        # TODO: Implement validation logic
        validation = {
            "is_valid": True,
            "quality_score": 0.85,
            "feedback": "Result meets requirements"
        }
        return validation
    
    def post(self, shared, prep_res, exec_res):
        shared["validation"] = exec_res
        
        if exec_res["is_valid"]:
            return None  # Complete
        else:
            return "supervisor"  # Reassign
''',
            "graph.py": '''"""
{name} Supervisor Graph Configuration
Generated on: {date}
"""
from kaygraph import Graph
from nodes import SupervisorNode, WorkerNode, ValidateResultNode


def create_supervisor_graph():
    """Create a supervisor-worker graph"""
    # Create supervisor
    supervisor = SupervisorNode("supervisor")
    
    # Create graph with start node
    graph = Graph(supervisor)
    
    # Create multiple workers
    workers = []
    worker_names = ["alice", "bob", "charlie"]
    
    for name in worker_names:
        worker = WorkerNode(f"worker_{name}", name)
        workers.append(worker)
        
        # Connect supervisor to each worker
        supervisor - f"worker_{name}" >> worker
    
    # Create validator
    validator = ValidateResultNode("validate")
    
    # Connect workers to validator
    for worker in workers:
        worker - "validate" >> validator
    
    # Connect validator back to supervisor for reassignment
    validator - "supervisor" >> supervisor
    
    return graph, worker_names
''',
            "main.py": '''"""
{name} Supervisor Demo
Generated on: {date}
"""
from graph import create_supervisor_graph


def main():
    # Create supervisor graph
    graph, worker_names = create_supervisor_graph()
    
    # Initialize shared context
    shared = {
        "task": "Analyze quarterly sales data",
        "workers": worker_names
    }
    
    print(f"Task: {shared['task']}")
    print(f"Available workers: {', '.join(worker_names)}")
    print("\\nRunning supervisor workflow...")
    
    # Run the graph
    graph.run(shared, start_node="supervisor")
    
    # Display results
    assignment = shared.get("assignment", {})
    result = shared.get("result", {})
    validation = shared.get("validation", {})
    
    print(f"\\nAssignment: {assignment.get('assigned_to')}")
    print(f"Result: {result.get('output')}")
    print(f"Validation: {validation.get('feedback')}")
    print(f"Quality Score: {validation.get('quality_score', 0):.2f}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "validated_pipeline": {
        "description": "Pipeline with input/output validation",
        "files": {
            "nodes.py": '''"""
{name} Validated Pipeline Implementation
Generated on: {date}
"""
from kaygraph import ValidatedNode, Node
import json


class ValidatedInputNode(ValidatedNode):
    """Validate and parse input data"""
    
    # Define input schema
    input_schema = {
        "type": "object",
        "properties": {
            "{input_key}": {
                "type": "object",
                "properties": {
                    "data": {"type": "array"},
                    "config": {"type": "object"}
                },
                "required": ["data"]
            }
        },
        "required": ["{input_key}"]
    }
    
    def prep(self, shared):
        return shared.get("{input_key}")
    
    def exec(self, input_data):
        """Process validated input"""
        # Input is guaranteed to match schema
        processed = {
            "item_count": len(input_data.get("data", [])),
            "has_config": "config" in input_data,
            "validated": True
        }
        return processed
    
    def post(self, shared, prep_res, exec_res):
        shared["validated_input"] = exec_res
        return "transform"


class TransformNode(Node):
    """Transform data with business logic"""
    
    def prep(self, shared):
        return {
            "input_info": shared.get("validated_input"),
            "data": shared.get("{input_key}", {}).get("data", [])
        }
    
    def exec(self, data):
        """Apply transformation"""
        # TODO: Implement transformation logic
        transformed = []
        for item in data["data"]:
            transformed.append({
                "original": item,
                "transformed": str(item).upper(),
                "metadata": {"processed": True}
            })
        
        return transformed
    
    def post(self, shared, prep_res, exec_res):
        shared["transformed_data"] = exec_res
        return "validate_output"


class ValidatedOutputNode(ValidatedNode):
    """Validate final output before returning"""
    
    # Define output schema
    output_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "original": {},
                "transformed": {"type": "string"},
                "metadata": {"type": "object"}
            },
            "required": ["original", "transformed", "metadata"]
        }
    }
    
    def prep(self, shared):
        return shared.get("transformed_data")
    
    def exec(self, transformed_data):
        """Validate and finalize output"""
        # Output is guaranteed to match schema
        summary = {
            "total_items": len(transformed_data),
            "all_valid": True,
            "data": transformed_data
        }
        return summary
    
    def post(self, shared, prep_res, exec_res):
        shared["{output_key}"] = exec_res
        return None


class ValidationErrorHandler(Node):
    """Handle validation errors gracefully"""
    
    def prep(self, shared):
        return shared.get("_last_error", {})
    
    def exec(self, error_info):
        """Create user-friendly error message"""
        return {
            "error": "Validation failed",
            "details": str(error_info),
            "suggestion": "Please check your input format"
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["error_response"] = exec_res
        return None
''',
            "main.py": '''"""
{name} Validated Pipeline Demo
Generated on: {date}
"""
from kaygraph import Graph
from nodes import (
    ValidatedInputNode, TransformNode, 
    ValidatedOutputNode, ValidationErrorHandler
)


def main():
    # Create nodes
    validate_input = ValidatedInputNode("validate_input")
    transform = TransformNode("transform")
    validate_output = ValidatedOutputNode("validate_output")
    error_handler = ValidationErrorHandler("error")
    
    # Create graph with start node
    graph = Graph(validate_input)
    
    # Define flow with error handling
    validate_input - "transform" >> transform
    validate_input - "error" >> error_handler  # On validation error
    
    transform - "validate_output" >> validate_output
    
    validate_output - "error" >> error_handler  # On validation error
    
    # Test with valid data
    print("Testing with valid data...")
    shared_valid = {
        "{input_key}": {
            "data": ["item1", "item2", "item3"],
            "config": {"uppercase": True}
        }
    }
    
    graph.run(shared_valid, start_node="validate_input")
    
    if "{output_key}" in shared_valid:
        output = shared_valid["{output_key}"]
        print(f"Success! Processed {output['total_items']} items")
        print(f"First item: {output['data'][0] if output['data'] else 'None'}")
    
    # Test with invalid data
    print("\\nTesting with invalid data...")
    shared_invalid = {
        "{input_key}": "not an object"  # Will fail validation
    }
    
    try:
        graph.run(shared_invalid, start_node="validate_input")
    except Exception as e:
        print(f"Validation error (expected): {e}")
    
    if "error_response" in shared_invalid:
        error = shared_invalid["error_response"]
        print(f"Error handled: {error['suggestion']}")


if __name__ == "__main__":
    main()
''',
        }
    },
    
    "metrics": {
        "description": "Pipeline with comprehensive metrics collection",
        "files": {
            "nodes.py": '''"""
{name} Metrics-Enabled Pipeline
Generated on: {date}
"""
from kaygraph import MetricsNode
import time
import random


class DataProcessingNode(MetricsNode):
    """Process data with automatic metrics collection"""
    
    # Retry configuration
    max_retries = 3
    wait = 0.5
    
    def prep(self, shared):
        """Prepare data for processing"""
        return shared.get("{input_key}", [])
    
    def exec(self, data):
        """Process with simulated variability"""
        # Simulate processing time
        time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate occasional failures for retry metrics
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Simulated processing error")
        
        # Process data
        result = {
            "processed_count": len(data),
            "timestamp": time.time(),
            "success": True
        }
        return result
    
    def post(self, shared, prep_res, exec_res):
        shared["processing_result"] = exec_res
        
        # Get metrics
        stats = self.get_stats()
        shared["processing_metrics"] = stats
        
        return "analyze"


class AnalysisNode(MetricsNode):
    """Analyze results with metrics"""
    
    def prep(self, shared):
        return shared.get("processing_result")
    
    def exec(self, result):
        """Perform analysis"""
        time.sleep(0.05)  # Simulate work
        
        analysis = {
            "total_processed": result["processed_count"],
            "processing_time": result["timestamp"],
            "recommendations": ["Optimize batch size", "Add caching"]
        }
        return analysis
    
    def post(self, shared, prep_res, exec_res):
        shared["analysis"] = exec_res
        
        # Collect final metrics
        stats = self.get_stats()
        shared["analysis_metrics"] = stats
        
        return None


class MetricsSummaryNode(Node):
    """Summarize all collected metrics"""
    
    def prep(self, shared):
        return {
            "processing": shared.get("processing_metrics", {}),
            "analysis": shared.get("analysis_metrics", {})
        }
    
    def exec(self, metrics):
        """Create metrics summary"""
        summary = {
            "total_executions": sum(
                m.get("execution_count", 0) 
                for m in metrics.values()
            ),
            "total_retries": sum(
                m.get("retry_count", 0) 
                for m in metrics.values()
            ),
            "total_errors": sum(
                m.get("error_count", 0) 
                for m in metrics.values()
            ),
            "performance": {
                node: {
                    "avg_time": stats.get("avg_execution_time", 0),
                    "max_time": stats.get("max_execution_time", 0),
                    "success_rate": stats.get("success_rate", 0)
                }
                for node, stats in metrics.items()
            }
        }
        return summary
    
    def post(self, shared, prep_res, exec_res):
        shared["{output_key}"] = exec_res
        return None
''',
            "main.py": '''"""
{name} Metrics Collection Demo
Generated on: {date}
"""
from kaygraph import Graph
from nodes import DataProcessingNode, AnalysisNode, MetricsSummaryNode


def main():
    # Create nodes
    process = DataProcessingNode("process")
    analyze = AnalysisNode("analyze")
    summarize = MetricsSummaryNode("summarize")
    
    # Create graph with start node
    graph = Graph(process)
    
    # Define flow
    process - "analyze" >> analyze
    analyze >> summarize
    
    # Run multiple times to collect metrics
    print("Running pipeline multiple times to collect metrics...\\n")
    
    test_data = list(range(10))
    
    for i in range(5):
        shared = {
            "{input_key}": test_data
        }
        
        try:
            graph.run(shared)
            print(f"Run {i+1}: Success")
        except Exception as e:
            print(f"Run {i+1}: Failed - {e}")
    
    # Get final metrics
    shared_final = {
        "{input_key}": test_data
    }
    graph.run(shared_final)
    
    # Display metrics summary
    metrics = shared_final.get("{output_key}", {})
    
    print("\\n=== Metrics Summary ===")
    print(f"Total Executions: {metrics.get('total_executions', 0)}")
    print(f"Total Retries: {metrics.get('total_retries', 0)}")
    print(f"Total Errors: {metrics.get('total_errors', 0)}")
    
    print("\\n=== Performance by Node ===")
    for node, perf in metrics.get("performance", {}).items():
        print(f"\\n{node}:")
        print(f"  Average Time: {perf.get('avg_time', 0):.3f}s")
        print(f"  Max Time: {perf.get('max_time', 0):.3f}s")
        print(f"  Success Rate: {perf.get('success_rate', 0):.1%}")


if __name__ == "__main__":
    main()
''',
        }
    }
}


def generate_template(template_type, name, output_dir):
    """Generate template files for the specified pattern"""
    if template_type not in TEMPLATES:
        print(f"Error: Unknown template type '{template_type}'")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        return False
    
    template = TEMPLATES[template_type]
    
    # Create output directory
    output_path = Path(output_dir) / name.lower().replace(" ", "_")
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate variable names
    class_name = "".join(word.capitalize() for word in name.split())
    var_name = "_".join(name.lower().split())
    node_id = var_name
    
    # Common replacements
    replacements = {
        "{name}": name,
        "{class_name}": class_name,
        "{var_name}": var_name,
        "{node_id}": node_id,
        "{input_key}": f"{var_name}_input",
        "{output_key}": f"{var_name}_output",
        "{description}": template["description"],
        "{date}": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Generate files
    for filename, content in template["files"].items():
        file_content = content
        for key, value in replacements.items():
            file_content = file_content.replace(key, value)
        
        file_path = output_path / filename
        with open(file_path, 'w') as f:
            f.write(file_content)
        print(f"✓ Created: {file_path}")
    
    # Create utils directory if needed
    if template_type in ["agent", "rag"]:
        utils_dir = output_path / "utils"
        utils_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        (utils_dir / "__init__.py").touch()
        
        # Create placeholder LLM wrapper
        llm_wrapper = utils_dir / "call_llm.py"
        with open(llm_wrapper, 'w') as f:
            f.write('''"""
LLM wrapper - implement your preferred LLM here
"""

def call_llm(prompt, **kwargs):
    """
    Call your LLM of choice
    
    Args:
        prompt: The prompt to send
        **kwargs: Additional parameters (temperature, max_tokens, etc.)
    
    Returns:
        str: LLM response
    """
    # TODO: Implement your LLM call
    # Example with OpenAI:
    # response = openai.chat.completions.create(
    #     model="gpt-4",
    #     messages=[{"role": "user", "content": prompt}],
    #     **kwargs
    # )
    # return response.choices[0].message.content
    
    return f"[LLM would process: {prompt[:50]}...]"
''')
        print(f"✓ Created: {llm_wrapper}")
    
    # Create requirements.txt
    req_path = output_path / "requirements.txt"
    with open(req_path, 'w') as f:
        f.write("kaygraph\n")
        if template_type == "rag":
            f.write("# For embeddings and vector search:\n")
            f.write("# numpy\n# faiss-cpu\n")
        if template_type in ["agent", "rag"]:
            f.write("# For LLM calls:\n")
            f.write("# openai\n# anthropic\n# litellm\n")
    print(f"✓ Created: {req_path}")
    
    # Create README
    readme_path = output_path / "README.md"
    with open(readme_path, 'w') as f:
        f.write(f"""# {name}

{template['description']}

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Implement TODOs in the code:
   - Complete the processing logic in `nodes.py`
   - Add any utility functions needed

3. Run the application:
   ```bash
   python main.py
   ```

## Structure

- `nodes.py` - Node implementations
- `main.py` - Entry point
""")
        if "graph.py" in template["files"]:
            f.write("- `graph.py` - Graph configuration\n")
        if template_type in ["agent", "rag"]:
            f.write("- `utils/` - Utility functions (LLM calls, etc.)\n")
        
        f.write(f"""
## Pattern: {template_type}

This template implements the {template_type} pattern with KayGraph.

Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
""")
    print(f"✓ Created: {readme_path}")
    
    print(f"\n✅ Successfully generated {template_type} template: {output_path}")
    print(f"\n📝 Next steps:")
    print(f"1. cd {output_path}")
    print(f"2. Review and implement TODOs in the generated code")
    print(f"3. Run with: python main.py")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Scaffold - Zero-dependency boilerplate generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available templates (based on 47+ production workbooks):

Basic Patterns:
  node              - Basic node with prep/exec/post lifecycle
  async_node        - Async node for I/O operations  
  batch_node        - Batch processing for collections
  parallel_batch    - High-performance parallel batch processing

AI/LLM Patterns:
  chat              - Interactive chat with conversation history
  agent             - Autonomous agent with observe/think/act loop
  rag               - Retrieval-Augmented Generation pipeline
  
Production Patterns:
  supervisor        - Supervisor pattern for managing workers
  validated_pipeline - Pipeline with input/output validation
  metrics           - Pipeline with comprehensive metrics
  workflow          - Multi-step workflow orchestration

Examples:
  python kaygraph_scaffold.py node DataProcessor
  python kaygraph_scaffold.py chat CustomerSupport
  python kaygraph_scaffold.py agent ResearchBot
  python kaygraph_scaffold.py supervisor TaskManager --output-dir ./projects
  
The generated code includes:
  - Complete working example with proper structure
  - Comprehensive documentation and TODOs
  - Requirements.txt with optional dependencies
  - README with quick start instructions
"""
    )
    
    parser.add_argument("template", 
                       choices=list(TEMPLATES.keys()),
                       help="Template type to generate")
    parser.add_argument("name", 
                       help="Name for your component")
    parser.add_argument("--output-dir", 
                       default="./generated",
                       help="Output directory (default: ./generated)")
    
    args = parser.parse_args()
    
    success = generate_template(args.template, args.name, args.output_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()