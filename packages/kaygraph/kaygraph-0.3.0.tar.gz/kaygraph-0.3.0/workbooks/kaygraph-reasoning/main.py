#!/usr/bin/env python3
"""
KayGraph Reasoning - Chain-of-Thought Patterns
"""

import argparse
import logging
from typing import Dict, Any

from kaygraph import Graph
from nodes import (
    ProblemAnalyzerNode, ChainOfThoughtNode,
    MathReasoningNode, LogicReasoningNode,
    DecisionReasoningNode, MultiPathReasoningNode,
    SelfReflectionNode, ReasoningOutputNode
)
from models import ReasoningType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_math():
    """Math problem solving example."""
    logger.info("\n=== Math Reasoning Example ===")
    
    # Create nodes
    analyzer = ProblemAnalyzerNode()
    math_solver = MathReasoningNode()
    output = ReasoningOutputNode()
    
    # Simple routing - analyzer determines it's a math problem
    analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> math_solver
    analyzer - ReasoningType.STEP_BY_STEP.value >> math_solver
    math_solver >> output
    
    graph = Graph(start=analyzer)
    
    # Test problems
    problems = [
        "A train travels 120 miles in 2 hours. How far will it travel in 5 hours at the same speed?",
        "If 3 apples cost $1.50, how much do 7 apples cost?",
        "A rectangle has a perimeter of 24 cm and length is twice the width. Find the area."
    ]
    
    for problem in problems:
        logger.info(f"\nProblem: {problem}")
        shared = {"problem": problem}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No solution")
        logger.info(f"\nSolution:\n{output_text}")


def example_logic():
    """Logic puzzle solving example."""
    logger.info("\n=== Logic Reasoning Example ===")
    
    # Create nodes
    analyzer = ProblemAnalyzerNode()
    logic_solver = LogicReasoningNode()
    output = ReasoningOutputNode()
    
    # Route logic problems
    analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> logic_solver
    analyzer - ReasoningType.STEP_BY_STEP.value >> logic_solver
    logic_solver >> output
    
    graph = Graph(start=analyzer)
    
    # Test logic puzzles
    puzzles = [
        "Three boxes are labeled 'Apples', 'Oranges', and 'Mixed'. Each label is wrong. You can pick one fruit from one box. How do you correctly label all boxes?",
        "Five houses in a row are painted different colors. The green house is to the left of the white house. The red house is to the right of the blue house. The blue house is not next to the green house. What's the order?",
        "A says 'B is lying'. B says 'C is lying'. C says 'A and B are both lying'. Who is telling the truth?"
    ]
    
    for puzzle in puzzles:
        logger.info(f"\nPuzzle: {puzzle}")
        shared = {"problem": puzzle}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No solution")
        logger.info(f"\nSolution:\n{output_text}")


def example_chain_of_thought():
    """Chain-of-thought reasoning example."""
    logger.info("\n=== Chain-of-Thought Example ===")
    
    # Create nodes
    analyzer = ProblemAnalyzerNode()
    chain = ChainOfThoughtNode()
    reflection = SelfReflectionNode()
    output = ReasoningOutputNode()
    
    # Chain of thought with self-loop and reflection
    analyzer >> chain  # Default route
    analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> chain
    analyzer - ReasoningType.STEP_BY_STEP.value >> chain
    chain - "chain_of_thought" >> chain  # Self-loop
    chain - "complete" >> reflection
    reflection >> output
    
    graph = Graph(start=analyzer)
    
    # Complex problem requiring iterative thinking
    problem = """
    A farmer needs to cross a river with a fox, a chicken, and a bag of grain. 
    The boat can only carry the farmer and one item at a time. 
    If left alone, the fox will eat the chicken, and the chicken will eat the grain. 
    How can the farmer get everything across safely?
    """
    
    logger.info(f"\nProblem: {problem.strip()}")
    shared = {"problem": problem}
    graph.run(shared)
    
    output_text = shared.get("final_output", "No solution")
    logger.info(f"\nSolution:\n{output_text}")


def example_decision():
    """Decision-making reasoning example."""
    logger.info("\n=== Decision Reasoning Example ===")
    
    # Create nodes
    analyzer = ProblemAnalyzerNode()
    decision = DecisionReasoningNode()
    output = ReasoningOutputNode()
    
    # Route decision problems
    analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> decision
    analyzer - ReasoningType.STEP_BY_STEP.value >> decision
    decision >> output
    
    graph = Graph(start=analyzer)
    
    # Test decisions
    decisions = [
        "Should I buy or lease a car for my daily 50-mile commute?",
        "Which programming language should I learn first: Python, JavaScript, or Java?",
        "Should our startup focus on B2B or B2C market initially?"
    ]
    
    for question in decisions:
        logger.info(f"\nDecision: {question}")
        shared = {"problem": question}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No analysis")
        logger.info(f"\nAnalysis:\n{output_text}")


def example_multi_path():
    """Multi-path reasoning example."""
    logger.info("\n=== Multi-Path Reasoning Example ===")
    
    # Create nodes
    analyzer = ProblemAnalyzerNode()
    multi_path = MultiPathReasoningNode()
    output = ReasoningOutputNode()
    
    # Route to multi-path exploration
    analyzer - ReasoningType.MULTI_PATH.value >> multi_path
    analyzer - ReasoningType.TREE_OF_THOUGHT.value >> multi_path
    # Fallback for other types
    analyzer >> multi_path
    
    multi_path >> output
    
    graph = Graph(start=analyzer)
    
    # Problems that benefit from multiple approaches
    problems = [
        "What's the most efficient way to sort a list of 1 million integers?",
        "How can we reduce carbon emissions in urban transportation?",
        "Design a system to detect fake news articles"
    ]
    
    for problem in problems:
        logger.info(f"\nProblem: {problem}")
        shared = {"problem": problem}
        graph.run(shared)
        
        output_text = shared.get("final_output", "No solution")
        logger.info(f"\nMulti-Path Analysis:\n{output_text}")


def example_complete():
    """Complete reasoning system with all capabilities."""
    logger.info("\n=== Complete Reasoning System ===")
    
    # Create all nodes
    analyzer = ProblemAnalyzerNode()
    chain = ChainOfThoughtNode()
    math = MathReasoningNode()
    logic = LogicReasoningNode()
    decision = DecisionReasoningNode()
    multi_path = MultiPathReasoningNode()
    reflection = SelfReflectionNode()
    output = ReasoningOutputNode()
    
    # Complex routing based on problem type and approach
    
    # Chain of thought can route to specialized solvers or self-loop
    analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> chain
    chain - "chain_of_thought" >> chain  # Self-loop
    chain - "complete" >> reflection
    
    # Direct routes to specialized solvers
    analyzer - ReasoningType.STEP_BY_STEP.value >> chain
    analyzer - ReasoningType.MULTI_PATH.value >> multi_path
    analyzer - ReasoningType.TREE_OF_THOUGHT.value >> multi_path
    
    # Reflection always goes to output
    reflection >> output
    
    # Specialized solvers go through reflection
    math >> reflection
    logic >> reflection
    decision >> reflection
    multi_path >> reflection
    
    graph = Graph(start=analyzer)
    
    # Test a complex problem
    problem = """
    A company has $100,000 to invest. They can:
    1. Invest in R&D with 30% chance of 5x return, 70% chance of losing it all
    2. Invest in marketing with guaranteed 50% return
    3. Split between both options
    What's the optimal strategy considering risk and expected value?
    """
    
    logger.info(f"\nComplex Problem: {problem.strip()}")
    shared = {"problem": problem}
    graph.run(shared)
    
    output_text = shared.get("final_output", "No solution")
    logger.info(f"\nComplete Analysis:\n{output_text}")


def run_interactive():
    """Run interactive reasoning mode."""
    logger.info("\n=== Interactive Reasoning Mode ===")
    logger.info("Enter problems to solve using advanced reasoning.")
    logger.info("Type 'exit' to quit.\n")
    
    # Build complete reasoning system
    analyzer = ProblemAnalyzerNode()
    chain = ChainOfThoughtNode()
    math = MathReasoningNode()
    logic = LogicReasoningNode()
    decision = DecisionReasoningNode()
    multi_path = MultiPathReasoningNode()
    reflection = SelfReflectionNode()
    output = ReasoningOutputNode()
    
    # Set up routing
    analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> chain
    chain - "chain_of_thought" >> chain
    chain - "complete" >> reflection
    
    analyzer - ReasoningType.STEP_BY_STEP.value >> chain
    analyzer - ReasoningType.MULTI_PATH.value >> multi_path
    analyzer - ReasoningType.TREE_OF_THOUGHT.value >> multi_path
    analyzer - ReasoningType.SELF_REFLECTION.value >> chain
    
    # All paths lead through reflection to output
    reflection >> output
    math >> reflection
    logic >> reflection
    decision >> reflection
    multi_path >> reflection
    
    graph = Graph(start=analyzer)
    
    while True:
        problem = input("\nYour problem: ").strip()
        if problem.lower() == 'exit':
            break
        
        if not problem:
            continue
        
        shared = {"problem": problem}
        graph.run(shared)
        
        output_text = shared.get("final_output", "Unable to analyze the problem.")
        print(f"\n{output_text}")
        
        # Show reasoning metrics
        state = shared.get("reasoning_state")
        if state:
            print(f"\n[Reasoning stats: {len(state.completed_steps)} steps, "
                  f"{state.plan.iterations} iterations, "
                  f"confidence: {state.total_confidence:.1%}]")


def main():
    parser = argparse.ArgumentParser(description="KayGraph Reasoning Examples")
    parser.add_argument("problem", nargs="?", help="Problem to solve")
    parser.add_argument("--example", choices=["math", "logic", "chain", "decision", 
                                               "multi", "complete", "all"],
                        help="Run specific example")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    
    elif args.problem:
        # Solve single problem with complete system
        logger.info(f"Solving: {args.problem}")
        
        # Use complete system
        analyzer = ProblemAnalyzerNode()
        chain = ChainOfThoughtNode()
        math = MathReasoningNode()
        logic = LogicReasoningNode()
        decision = DecisionReasoningNode()
        multi_path = MultiPathReasoningNode()
        reflection = SelfReflectionNode()
        output = ReasoningOutputNode()
        
        analyzer - ReasoningType.CHAIN_OF_THOUGHT.value >> chain
        chain - "chain_of_thought" >> chain
        chain - "complete" >> reflection
        
        analyzer - ReasoningType.STEP_BY_STEP.value >> chain
        analyzer - ReasoningType.MULTI_PATH.value >> multi_path
        
        reflection >> output
        math >> reflection
        logic >> reflection
        decision >> reflection
        multi_path >> reflection
        
        graph = Graph(start=analyzer)
        
        shared = {"problem": args.problem}
        graph.run(shared)
        
        logger.info(f"\nSolution:\n{shared.get('final_output', 'No solution')}")
    
    elif args.example:
        if args.example == "math" or args.example == "all":
            example_math()
        
        if args.example == "logic" or args.example == "all":
            example_logic()
        
        if args.example == "chain" or args.example == "all":
            example_chain_of_thought()
        
        if args.example == "decision" or args.example == "all":
            example_decision()
        
        if args.example == "multi" or args.example == "all":
            example_multi_path()
        
        if args.example == "complete" or args.example == "all":
            example_complete()
    
    else:
        # Run all examples
        logger.info("Running all reasoning examples...")
        example_math()
        example_logic()
        example_chain_of_thought()
        example_decision()
        example_multi_path()
        example_complete()


if __name__ == "__main__":
    main()