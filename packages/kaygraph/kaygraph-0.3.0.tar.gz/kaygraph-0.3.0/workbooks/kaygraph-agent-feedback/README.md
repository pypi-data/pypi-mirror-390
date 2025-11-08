# KayGraph Agent Feedback - Human-in-the-Loop Patterns

This example demonstrates how to implement human-in-the-loop (HITL) patterns in KayGraph for high-risk decisions, complex judgments, and quality control workflows.

## Overview

The feedback component provides strategic points where human judgment is required. This is essential for:
- High-stakes decisions requiring human oversight
- Complex judgments beyond AI capabilities
- Quality control and validation workflows
- Continuous improvement through human feedback

## Key Features

1. **Approval Workflows** - Get human approval before critical actions
2. **Feedback Collection** - Gather human input to improve responses
3. **Quality Review** - Human validation of AI outputs
4. **Escalation Patterns** - Route complex cases to humans
5. **Interactive Refinement** - Iterative improvement with human guidance

## Running the Examples

```bash
# Run all examples
python main.py --example all

# Specific examples
python main.py --example approval      # Basic approval workflow
python main.py --example feedback      # Feedback collection
python main.py --example review        # Quality review process
python main.py --example escalation    # Escalation patterns
python main.py --example refinement    # Interactive refinement

# Interactive mode
python main.py --interactive

# Process specific content
python main.py "Write an email to cancel a subscription"
```

## Implementation Patterns

### 1. Approval Workflow
- AI generates content/decision
- Human reviews and approves/rejects
- Optional modifications before approval

### 2. Feedback Collection
- AI provides response
- Human rates quality (1-5 scale)
- Optional comments for improvement

### 3. Quality Review
- Batch review of AI outputs
- Flag problematic responses
- Track quality metrics

### 4. Escalation Logic
- Confidence-based escalation
- Topic-based routing
- Complexity thresholds

### 5. Interactive Refinement
- Initial AI response
- Human provides guidance
- AI refines based on feedback
- Iterate until satisfactory

## Use Cases

- **Content Moderation** - Review AI-generated content before publishing
- **Customer Support** - Escalate complex issues to human agents
- **Medical/Legal** - Require human validation for critical decisions
- **Training Data** - Collect feedback to improve models
- **Quality Assurance** - Ensure AI outputs meet standards

## Architecture

```
Start -> GenerateNode -> ApprovalNode -> ActionNode
                              |
                              v
                        RejectionNode
```

The graph implements branching based on human decisions, with support for:
- Retry loops for refinement
- Escalation paths for complex cases
- Feedback storage for continuous improvement