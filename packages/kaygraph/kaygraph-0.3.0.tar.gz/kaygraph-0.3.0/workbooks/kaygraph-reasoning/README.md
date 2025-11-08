# KayGraph Reasoning - Chain-of-Thought Patterns

This workbook demonstrates advanced reasoning patterns using KayGraph, including chain-of-thought (CoT), step-by-step reasoning, self-reflection, and multi-path exploration.

## Key Concepts

1. **Chain-of-Thought (CoT)**: Breaking down complex problems into sequential reasoning steps
2. **Self-Evaluation**: Nodes that check their own reasoning before proceeding
3. **Multi-Path Reasoning**: Exploring multiple solution paths in parallel
4. **Reasoning Traces**: Maintaining detailed logs of the reasoning process
5. **Confidence Scoring**: Tracking reasoning confidence at each step

## Examples

### 1. Math Problem Solver
- Breaks down word problems into steps
- Shows work for each calculation
- Verifies answer with alternative methods

### 2. Logic Puzzle Solver
- Analyzes constraints systematically
- Builds solution incrementally
- Validates against all conditions

### 3. Code Analysis
- Step-by-step code walkthrough
- Identifies potential issues
- Suggests improvements with reasoning

### 4. Decision Making
- Evaluates pros and cons
- Considers multiple perspectives
- Provides justified recommendations

## Usage

```bash
# Run all examples
python main.py

# Run specific example
python main.py --example math

# Solve a specific problem
python main.py "If a train travels 120 miles in 2 hours, how far will it travel in 5 hours at the same speed?"

# Interactive reasoning mode
python main.py --interactive
```

## Implementation Details

The reasoning system uses:
- Self-looping nodes for iterative thinking
- Structured reasoning formats (YAML/JSON)
- Confidence thresholds for decision making
- Parallel exploration for complex problems
- Reasoning validation and error correction