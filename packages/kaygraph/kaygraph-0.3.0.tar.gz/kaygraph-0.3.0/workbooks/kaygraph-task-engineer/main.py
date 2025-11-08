#!/usr/bin/env python3
"""
KayGraph Task Engineer - A lightweight, fast task execution system

Features:
- Find and clean up one-time use files
- Find specific lines in files and edit them
- Generalizable task execution with fast LLMs
- Bidirectional: decompose for humans OR execute autonomously
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from kaygraph import Graph, Node, BatchNode
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from config import get_model_config, get_prompt

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ===== TASK UNDERSTANDING NODES =====

class TaskAnalyzer(Node):
    """Analyzes incoming tasks and determines execution strategy"""
    
    def prep(self, shared):
        return {
            "task": shared.get("task"),
            "context": shared.get("context", {})
        }
    
    def exec(self, prep_res):
        task = prep_res["task"]
        
        # Analyze task type
        task_patterns = {
            "file_cleanup": ["find", "one-time", "temporary", "cleanup", "remove", "unused"],
            "code_edit": ["edit", "modify", "change", "replace", "update", "lines"],
            "file_search": ["find", "search", "locate", "where", "files"],
            "code_generation": ["create", "generate", "write", "implement", "build"],
            "analysis": ["analyze", "review", "check", "inspect", "examine"],
            "security_check": ["security", "auth", "authentication", "hardcoded", "insecure", "vulnerability"],
            "git_analysis": ["git diff", "git log", "commit", "changes", "compare"]
        }
        
        task_lower = task.lower()
        detected_type = "general"
        
        for task_type, keywords in task_patterns.items():
            if any(keyword in task_lower for keyword in keywords):
                detected_type = task_type
                break
        
        return {
            "task_type": detected_type,
            "original_task": task,
            "requires_llm": detected_type in ["code_generation", "analysis", "general"]
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["task_analysis"] = exec_res
        logger.info(f"Task type detected: {exec_res['task_type']}")
        
        # Route to appropriate handler
        task_type = exec_res["task_type"]
        if task_type == "file_cleanup":
            return "file_cleanup"
        elif task_type == "code_edit":
            return "code_edit"
        elif task_type == "file_search":
            return "file_search"
        elif task_type == "security_check":
            return "security_analysis"
        elif task_type == "git_analysis":
            return "git_analysis"
        else:
            return "llm_planning"


# ===== FILE OPERATION NODES =====

class FileCleanupFinder(Node):
    """Finds files that appear to be one-time use or temporary"""
    
    def prep(self, shared):
        return {
            "task": shared.get("task"),
            "search_path": shared.get("search_path", ".")
        }
    
    def exec(self, prep_res):
        from utils.file_analyzer import find_onetime_files
        
        # Find potential one-time use files
        candidates = find_onetime_files(prep_res["search_path"])
        
        return {
            "candidates": candidates,
            "count": len(candidates)
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["cleanup_candidates"] = exec_res["candidates"]
        logger.info(f"Found {exec_res['count']} potential cleanup candidates")
        
        if exec_res["count"] > 0:
            return "confirm_cleanup"
        else:
            return "complete"


class CodeEditor(Node):
    """Finds and edits specific lines in files"""
    
    def prep(self, shared):
        task_analysis = shared.get("task_analysis", {})
        return {
            "task": task_analysis.get("original_task"),
            "target_files": shared.get("target_files", [])
        }
    
    def exec(self, prep_res):
        from utils.code_editor import extract_edit_instructions, apply_edits
        
        # Extract edit instructions from task
        instructions = extract_edit_instructions(prep_res["task"])
        
        # Apply edits
        results = []
        for instruction in instructions:
            result = apply_edits(
                instruction["file_pattern"],
                instruction["search_pattern"],
                instruction["replacement"],
                instruction.get("options", {})
            )
            results.append(result)
        
        return {
            "instructions": instructions,
            "results": results,
            "total_changes": sum(r["changes_made"] for r in results)
        }
    
    def post(self, shared, prep_res, exec_res):
        shared["edit_results"] = exec_res
        logger.info(f"Made {exec_res['total_changes']} changes across files")
        return "complete"


class FileSearcher(BatchNode):
    """Searches for files matching patterns"""
    
    def prep(self, shared):
        from utils.file_search import extract_search_criteria
        
        task = shared.get("task_analysis", {}).get("original_task", "")
        criteria = extract_search_criteria(task)
        
        return criteria  # Returns list of search criteria
    
    def exec(self, criterion):
        from utils.file_search import search_files
        
        results = search_files(
            criterion["pattern"],
            criterion.get("path", "."),
            criterion.get("content_pattern")
        )
        
        return {
            "criterion": criterion,
            "matches": results,
            "count": len(results)
        }
    
    def post(self, shared, prep_res, exec_res):
        if "search_results" not in shared:
            shared["search_results"] = []
        
        shared["search_results"].extend(exec_res)
        
        total_matches = sum(r["count"] for r in exec_res)
        logger.info(f"Found {total_matches} matching files")
        
        return "complete"


# ===== LLM INTEGRATION NODES =====

class LLMPlanner(Node):
    """Uses fast LLM to plan complex tasks"""
    
    def prep(self, shared):
        return {
            "task": shared.get("task"),
            "context": shared.get("context", {}),
            "task_analysis": shared.get("task_analysis", {})
        }
    
    def exec(self, prep_res):
        from utils.llm_cerebras import plan_task
        
        # Use fast LLM to create execution plan
        plan = plan_task(
            prep_res["task"],
            prep_res["context"],
            model="qwen-3-32b"
        )
        
        return plan
    
    def post(self, shared, prep_res, exec_res):
        shared["execution_plan"] = exec_res
        logger.info(f"Created plan with {len(exec_res['steps'])} steps")
        
        # Determine if we can execute automatically
        if exec_res.get("auto_executable", False):
            return "execute_plan"
        else:
            return "human_review"


class PlanExecutor(BatchNode):
    """Executes plan steps in sequence"""
    
    def prep(self, shared):
        plan = shared.get("execution_plan", {})
        return plan.get("steps", [])
    
    def exec(self, step):
        from utils.llm_cerebras import execute_step
        
        # Execute individual step
        result = execute_step(step, model="qwen-3-32b")
        
        return {
            "step": step,
            "result": result,
            "success": result.get("success", False)
        }
    
    def post(self, shared, prep_res, exec_res):
        if "execution_results" not in shared:
            shared["execution_results"] = []
        
        shared["execution_results"].extend(exec_res)
        
        # Check if all steps succeeded
        all_success = all(r["success"] for r in exec_res)
        
        if all_success:
            logger.info("All steps executed successfully")
            return "complete"
        else:
            failed = [r for r in exec_res if not r["success"]]
            logger.warning(f"{len(failed)} steps failed")
            return "handle_failures"


# ===== REVIEW AND COMPLETION NODES =====

class HumanReviewer(Node):
    """Presents plan for human review"""
    
    def exec(self, prep_res):
        plan = prep_res["plan"]
        
        print("\n=== EXECUTION PLAN ===")
        for i, step in enumerate(plan["steps"], 1):
            print(f"\n{i}. {step['description']}")
            print(f"   Type: {step['type']}")
            if step.get("details"):
                print(f"   Details: {step['details']}")
        
        print("\n=== END PLAN ===\n")
        
        # In real implementation, would wait for approval
        return {"approved": True}
    
    def post(self, shared, prep_res, exec_res):
        if exec_res["approved"]:
            return "execute_plan"
        else:
            return "complete"


class CompletionHandler(Node):
    """Handles task completion and summarizes results"""
    
    def prep(self, shared):
        return {
            "task": shared.get("task"),
            "task_type": shared.get("task_analysis", {}).get("task_type"),
            "results": {
                "search_results": shared.get("search_results"),
                "edit_results": shared.get("edit_results"),
                "cleanup_candidates": shared.get("cleanup_candidates"),
                "execution_results": shared.get("execution_results")
            }
        }
    
    def exec(self, prep_res):
        # Summarize results based on task type
        task_type = prep_res["task_type"]
        results = prep_res["results"]
        
        summary = {
            "task": prep_res["task"],
            "task_type": task_type,
            "completed_at": datetime.now().isoformat()
        }
        
        if task_type == "file_search" and results["search_results"]:
            summary["files_found"] = sum(r["count"] for r in results["search_results"])
            summary["matches"] = [r["matches"] for r in results["search_results"]]
        
        elif task_type == "code_edit" and results["edit_results"]:
            summary["changes_made"] = results["edit_results"]["total_changes"]
            summary["files_modified"] = len(results["edit_results"]["results"])
        
        elif task_type == "file_cleanup" and results["cleanup_candidates"]:
            summary["cleanup_candidates"] = len(results["cleanup_candidates"])
            summary["candidates"] = results["cleanup_candidates"]
        
        elif results["execution_results"]:
            summary["steps_executed"] = len(results["execution_results"])
            summary["steps_succeeded"] = sum(1 for r in results["execution_results"] if r["success"])
        
        return summary
    
    def post(self, shared, prep_res, exec_res):
        shared["final_summary"] = exec_res
        
        print(f"\n✅ Task completed: {exec_res['task_type']}")
        print(json.dumps(exec_res, indent=2))
        
        return None  # End of graph


# ===== BUILD THE TASK ENGINEER GRAPH =====

def build_task_engineer():
    """Builds the complete task engineering graph"""
    
    # Import security nodes
    from nodes.security_analyzer import (
        GitDiffAnalyzer, SecurityLLMAnalyzer, 
        AuthChecker, SecurityReporter
    )
    
    # Initialize nodes
    analyzer = TaskAnalyzer("analyzer")
    
    # File operation nodes
    cleanup_finder = FileCleanupFinder("cleanup_finder")
    code_editor = CodeEditor("code_editor")
    file_searcher = FileSearcher("file_searcher")
    
    # LLM nodes
    planner = LLMPlanner("planner")
    executor = PlanExecutor("executor")
    reviewer = HumanReviewer("reviewer")
    
    # Security nodes
    git_analyzer = GitDiffAnalyzer("git_analyzer")
    security_llm = SecurityLLMAnalyzer("security_llm")
    auth_checker = AuthChecker("auth_checker")
    security_reporter = SecurityReporter("security_reporter")
    
    # Completion
    completion = CompletionHandler("completion")
    
    # Build graph with conditional routing
    graph = Graph("task_engineer")
    
    # Main flow
    graph.add(analyzer)
    
    # Route based on task type
    analyzer >> ("file_cleanup", cleanup_finder)
    analyzer >> ("code_edit", code_editor)
    analyzer >> ("file_search", file_searcher)
    analyzer >> ("security_analysis", auth_checker)
    analyzer >> ("git_analysis", git_analyzer)
    analyzer >> ("llm_planning", planner)
    
    # File operation flows
    cleanup_finder >> ("confirm_cleanup", reviewer)
    cleanup_finder >> ("complete", completion)
    
    code_editor >> completion
    file_searcher >> completion
    
    # LLM flow
    planner >> ("execute_plan", executor)
    planner >> ("human_review", reviewer)
    
    reviewer >> ("execute_plan", executor)
    reviewer >> ("complete", completion)
    
    executor >> ("complete", completion)
    executor >> ("handle_failures", completion)
    
    # Security analysis flows
    git_analyzer >> ("deep_security_analysis", security_llm)
    git_analyzer >> ("security_report", security_reporter)
    
    security_llm >> ("block_changes", security_reporter)
    security_llm >> ("security_report", security_reporter)
    
    auth_checker >> ("auth_remediation", security_llm)
    auth_checker >> ("complete", completion)
    
    security_reporter >> completion
    
    return graph


# ===== MAIN EXECUTION =====

def main():
    """Example usage of the Task Engineer"""
    
    # Example tasks to demonstrate
    example_tasks = [
        {
            "task": "Find all temporary files in the project that look like one-time use and can be cleaned up",
            "context": {"search_path": "."}
        },
        {
            "task": "Find the file config.py and edit line 42 to change DEBUG=True to DEBUG=False",
            "context": {}
        },
        {
            "task": "Search for all Python files containing 'TODO' comments",
            "context": {}
        },
        {
            "task": "Create a simple REST API endpoint for user authentication",
            "context": {"framework": "FastAPI"}
        },
        {
            "task": "Check git diff for any hardcoded passwords or missing authentication",
            "context": {"commit_range": "HEAD~1..HEAD"}
        },
        {
            "task": "Analyze the last 5 commits for security vulnerabilities",
            "context": {"branch": "main"}
        }
    ]
    
    # Build the graph
    graph = build_task_engineer()
    
    # Execute example task
    task_num = 0  # Change this to try different tasks
    
    print(f"\n🚀 Task Engineer Demo")
    print(f"Task: {example_tasks[task_num]['task']}\n")
    
    shared = {
        "task": example_tasks[task_num]["task"],
        "context": example_tasks[task_num]["context"]
    }
    
    # Run the task
    graph.run(shared, start_node="analyzer")


if __name__ == "__main__":
    main()