#!/usr/bin/env python3
"""
KayGraph Workflow Orchestrator - Complex task orchestration patterns.

Demonstrates how to implement orchestrator-worker patterns for managing
multi-step workflows with dynamic task allocation and coordination.
"""

import sys
import json
import logging
import argparse
import time
from typing import Dict, Any, List
from datetime import datetime
from kaygraph import Graph, Node
from nodes import (
    BlogOrchestratorNode, BlogWriterNode, BlogReviewerNode,
    TaskOrchestratorNode, WorkerNode,
    ReportOrchestratorNode, ProjectPlannerNode,
    OrchestrationAggregatorNode
)
from models import WorkerCapability, TaskType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============== Graph Creation Functions ==============

def create_blog_orchestration_graph() -> Graph:
    """
    Create blog writing orchestration workflow.
    Orchestrator → Workers → Reviewer
    """
    orchestrator = BlogOrchestratorNode()
    writer = BlogWriterNode()
    reviewer = BlogReviewerNode()
    
    # Connect nodes
    orchestrator >> writer
    writer >> ("write_next", writer)  # Loop for multiple sections
    writer >> ("all_sections_complete", reviewer)
    writer >> ("no_more_sections", reviewer)
    
    return Graph(start=orchestrator)


def create_general_orchestration_graph() -> Graph:
    """
    Create general task orchestration workflow.
    Supports any complex multi-step process.
    """
    orchestrator = TaskOrchestratorNode()
    
    # Create multiple workers
    workers = [WorkerNode(worker_id=f"worker_{i}") for i in range(4)]
    
    aggregator = OrchestrationAggregatorNode()
    
    # Connect orchestrator to all workers
    for worker in workers:
        orchestrator >> worker
        worker >> ("more_tasks", worker)  # Self-loop for more tasks
        worker >> ("no_more_tasks", aggregator)
        worker >> ("no_task", aggregator)
    
    return Graph(start=orchestrator)


def create_report_orchestration_graph() -> Graph:
    """
    Create report generation orchestration workflow.
    """
    orchestrator = ReportOrchestratorNode()
    
    # In a full implementation, would have data gathering and analysis workers
    # For this example, we'll use a simple flow
    
    return Graph(start=orchestrator)


def create_project_planning_graph() -> Graph:
    """
    Create project planning orchestration workflow.
    """
    planner = ProjectPlannerNode()
    
    return Graph(start=planner)


# ============== Example Functions ==============

def example_blog_orchestration():
    """Demonstrate blog writing orchestration."""
    print("\n=== Blog Writing Orchestration Example ===")
    
    graph = create_blog_orchestration_graph()
    
    # Test topics
    test_topics = [
        {
            "topic": "The Future of AI in Healthcare",
            "target_length": 1200,
            "style": "informative yet accessible",
            "target_audience": "healthcare professionals"
        },
        {
            "topic": "Getting Started with Python Programming",
            "target_length": 800,
            "style": "beginner-friendly tutorial",
            "target_audience": "programming beginners"
        }
    ]
    
    for test in test_topics:
        print(f"\n📝 Orchestrating blog about: {test['topic']}")
        print(f"Target: {test['target_length']} words, Style: {test['style']}")
        
        shared = test.copy()
        graph.run(shared)
        
        if "blog_structure" in shared:
            structure = shared["blog_structure"]
            print(f"\n📋 Blog Structure:")
            print(f"  Sections: {len(structure.sections)}")
            for section in structure.sections:
                print(f"    - {section.title} ({section.target_length_words} words)")
        
        if "written_sections" in shared:
            sections = shared["written_sections"]
            print(f"\n✍️  Written Sections: {len(sections)}")
            total_words = sum(s.word_count for s in sections.values())
            print(f"  Total words: {total_words}")
        
        if "blog_review" in shared:
            review = shared["blog_review"]
            print(f"\n📊 Review Scores:")
            print(f"  Cohesion: {review.cohesion_score:.2f}")
            print(f"  Readability: {review.readability_score:.2f}")
            
            if review.suggested_edits:
                print(f"\n💡 Suggested Edits:")
                for edit in review.suggested_edits[:3]:
                    print(f"  - {edit}")
            
            print(f"\n📄 Final blog preview:")
            print(review.final_version[:300] + "...")


def example_general_orchestration():
    """Demonstrate general task orchestration."""
    print("\n=== General Task Orchestration Example ===")
    
    graph = create_general_orchestration_graph()
    
    # Test objectives
    test_objectives = [
        "Create a comprehensive marketing strategy for a new product launch",
        "Analyze customer feedback data and generate actionable insights",
        "Design and implement a data processing pipeline"
    ]
    
    for objective in test_objectives:
        print(f"\n🎯 Orchestrating: {objective}")
        
        shared = {"objective": objective}
        
        # Run orchestration
        start_time = time.time()
        graph.run(shared)
        elapsed = time.time() - start_time
        
        if "orchestration_state" in shared:
            state = shared["orchestration_state"]
            plan = state.plan
            
            print(f"\n📋 Execution Plan:")
            print(f"  Strategy: {plan.strategy}")
            print(f"  Tasks: {len(plan.tasks)}")
            print(f"  Expected duration: {plan.expected_duration_minutes} minutes")
            
            # Show task breakdown
            print(f"\n📝 Task Breakdown:")
            for task in plan.tasks[:5]:  # Show first 5 tasks
                deps = f" (depends on: {', '.join(task.dependencies)})" if task.dependencies else ""
                print(f"  - [{task.priority.value}] {task.description}{deps}")
        
        if "orchestration_result" in shared:
            result = shared["orchestration_result"]
            
            print(f"\n📊 Execution Results:")
            print(f"  Status: {result.status}")
            print(f"  Completed: {result.completed_tasks} tasks")
            print(f"  Failed: {result.failed_tasks} tasks")
            print(f"  Duration: {elapsed:.1f}s (planned: {plan.expected_duration_minutes * 60}s)")
            
            if result.performance_metrics:
                metrics = result.performance_metrics
                print(f"\n⚡ Performance Metrics:")
                print(f"  Efficiency: {metrics.get('efficiency', 0)*100:.1f}%")
                print(f"  Avg task time: {metrics.get('average_task_time', 0):.1f}s")


def example_report_orchestration():
    """Demonstrate report generation orchestration."""
    print("\n=== Report Generation Orchestration Example ===")
    
    graph = create_report_orchestration_graph()
    
    # Test reports
    test_reports = [
        {
            "report_topic": "Q4 2024 Sales Performance Analysis",
            "data_sources": ["sales_db", "crm_system", "marketing_analytics"],
            "report_type": "quarterly_analysis"
        },
        {
            "report_topic": "Customer Satisfaction Survey Results",
            "data_sources": ["survey_responses", "support_tickets", "nps_scores"],
            "report_type": "survey_analysis"
        }
    ]
    
    for report in test_reports:
        print(f"\n📊 Orchestrating report: {report['report_topic']}")
        
        shared = report.copy()
        graph.run(shared)
        
        if "report_structure" in shared:
            structure = shared["report_structure"]
            print(f"\n📋 Report Structure:")
            print(f"  Title: {structure.title}")
            print(f"  Purpose: {structure.purpose}")
            print(f"  Sections: {len(structure.sections)}")
            
            for section in structure.sections:
                deps = f" → {', '.join(section.dependencies)}" if section.dependencies else ""
                print(f"    - {section.section_name} ({section.analysis_type}){deps}")
                if section.visualization_requirements:
                    print(f"      Visuals: {', '.join(section.visualization_requirements)}")


def example_project_planning():
    """Demonstrate project planning orchestration."""
    print("\n=== Project Planning Orchestration Example ===")
    
    graph = create_project_planning_graph()
    
    # Test projects
    test_projects = [
        {
            "project_description": "Develop a mobile app for task management with AI features",
            "constraints": {"budget": "$100k", "timeline": "6 months"},
            "available_resources": {"developers": 4, "designers": 2, "qa": 2}
        },
        {
            "project_description": "Migrate legacy system to cloud infrastructure",
            "constraints": {"downtime": "minimal", "compliance": "HIPAA"},
            "available_resources": {"engineers": 6, "architects": 2}
        }
    ]
    
    for project in test_projects:
        print(f"\n🗂️ Planning project: {project['project_description']}")
        
        shared = project.copy()
        graph.run(shared)
        
        if "project_plan" in shared:
            plan = shared["project_plan"]
            print(f"\n📋 Project Plan:")
            print(f"  Name: {plan.project_name}")
            print(f"  Duration: {plan.total_duration_weeks} weeks")
            print(f"  Phases: {len(plan.phases)}")
            
            # Show phases
            for phase in plan.phases:
                print(f"\n  Phase: {phase.phase_name} ({phase.duration_weeks} weeks)")
                print(f"    Objectives: {', '.join(phase.objectives[:2])}")
                print(f"    Tasks: {len(phase.tasks)}")
                
                # Show sample tasks
                for task in phase.tasks[:2]:
                    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(task.risk_level, "⚪")
                    print(f"      {risk_emoji} {task.task_name} ({task.estimated_hours}h)")
            
            # Show resources
            if plan.required_resources:
                print(f"\n  Required Resources:")
                for resource, count in plan.required_resources.items():
                    print(f"    - {resource}: {count}")


def interactive_mode():
    """Interactive orchestration mode."""
    print("\n=== Interactive Orchestration Mode ===")
    print("Commands:")
    print("  blog <topic>        - Orchestrate blog writing")
    print("  task <objective>    - General task orchestration")
    print("  report <topic>      - Report generation")
    print("  project <desc>      - Project planning")
    print("  quit                - Exit")
    
    graphs = {
        "blog": create_blog_orchestration_graph(),
        "task": create_general_orchestration_graph(),
        "report": create_report_orchestration_graph(),
        "project": create_project_planning_graph()
    }
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command == "quit":
                break
            
            parts = command.split(" ", 1)
            if len(parts) < 2:
                print("Please provide input after the command")
                continue
            
            cmd, input_text = parts
            
            if cmd == "blog":
                shared = {
                    "topic": input_text,
                    "target_length": 1000,
                    "style": "informative"
                }
                graphs["blog"].run(shared)
                
                if "blog_review" in shared:
                    review = shared["blog_review"]
                    print(f"Blog complete! Cohesion: {review.cohesion_score:.2f}")
                    print(f"Preview: {review.final_version[:200]}...")
                    
            elif cmd == "task":
                shared = {"objective": input_text}
                graphs["task"].run(shared)
                
                if "orchestration_result" in shared:
                    result = shared["orchestration_result"]
                    print(f"Orchestration {result.status}")
                    print(f"Completed {result.completed_tasks} tasks")
                    
            elif cmd == "report":
                shared = {
                    "report_topic": input_text,
                    "data_sources": ["data_source_1", "data_source_2"]
                }
                graphs["report"].run(shared)
                
                if "report_structure" in shared:
                    structure = shared["report_structure"]
                    print(f"Report planned: {len(structure.sections)} sections")
                    
            elif cmd == "project":
                shared = {"project_description": input_text}
                graphs["project"].run(shared)
                
                if "project_plan" in shared:
                    plan = shared["project_plan"]
                    print(f"Project: {plan.project_name}")
                    print(f"Duration: {plan.total_duration_weeks} weeks")
                    print(f"Phases: {len(plan.phases)}")
                    
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all orchestration examples."""
    example_blog_orchestration()
    example_general_orchestration()
    example_report_orchestration()
    example_project_planning()


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Workflow Orchestrator Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input for orchestration"
    )
    parser.add_argument(
        "--example",
        choices=["blog", "general", "report", "project", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.example == "all":
        run_all_examples()
    elif args.example == "blog":
        example_blog_orchestration()
    elif args.example == "general":
        example_general_orchestration()
    elif args.example == "report":
        example_report_orchestration()
    elif args.example == "project":
        example_project_planning()
    elif args.input:
        # Default to blog orchestration
        graph = create_blog_orchestration_graph()
        shared = {
            "topic": args.input,
            "target_length": 1000,
            "style": "informative"
        }
        graph.run(shared)
        
        if "blog_review" in shared:
            review = shared["blog_review"]
            print(f"\nBlog complete!")
            print(f"Cohesion score: {review.cohesion_score:.2f}")
            print(f"\nFinal blog:\n{review.final_version}")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()