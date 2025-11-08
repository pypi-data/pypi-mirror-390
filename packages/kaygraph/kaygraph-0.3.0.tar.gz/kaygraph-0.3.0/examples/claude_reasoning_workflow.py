#!/usr/bin/env python3
"""Multi-step Claude Reasoning Workflow with KayGraph.

This example demonstrates complex reasoning workflows using Claude within KayGraph.
It shows how to break down complex problems into multiple reasoning steps.

Examples:
    problem_analysis - Step-by-step problem decomposition
    decision_tree - Multi-path decision making
    creative_process - Creative ideation workflow
    research_synthesis - Research and synthesis workflow

Usage:
./examples/claude_reasoning_workflow.py - List the examples
./examples/claude_reasoning_workflow.py all - Run all examples
./examples/claude_reasoning_workflow.py problem_analysis - Run specific example

Environment Setup:
# For io.net models:
export API_KEY="your-io-net-api-key"
export ANTHROPIC_MODEL="glm-4.6"

# For Z.ai models:
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-auth-token"
export ANTHROPIC_MODEL="glm-4.6"
"""

import anyio
from typing import Dict, Any, List
from dataclasses import dataclass

from kaygraph import Graph, AsyncNode
from kaygraph_claude_base import ClaudeNode, AsyncClaudeNode, ClaudeConfig


@dataclass
class ReasoningStep:
    """Represents a step in the reasoning process."""
    name: str
    description: str
    prompt_template: str
    depends_on: List[str] = None


class ProblemDecompositionNode(AsyncClaudeNode):
    """Breaks down complex problems into smaller, manageable parts."""

    def __init__(self, **kwargs):
        prompt_template = """You are an expert problem solver. Given a complex problem, your task is to break it down into logical, manageable steps.

Problem: {problem}

Please analyze this problem and provide:
1. A clear problem statement
2. Key components or sub-problems
3. Required information or assumptions
4. Suggested approach for solving

Format your response as follows:
PROBLEM_STATEMENT: [Clear statement]
COMPONENTS: [List of key components]
ASSUMPTIONS: [List of needed assumptions]
APPROACH: [Suggested step-by-step approach]"""

        super().__init__(prompt_template=prompt_template, **kwargs)


class StepAnalysisNode(AsyncClaudeNode):
    """Analyzes individual steps in the reasoning process."""

    def __init__(self, step_focus: str, **kwargs):
        self.step_focus = step_focus
        prompt_template = """You are analyzing a specific step in solving a complex problem.

Original Problem: {problem}
Problem Decomposition: {decomposition}

Current Step Focus: {step_focus}

Please provide detailed analysis for this step:
1. Specific actions required
2. Potential challenges or obstacles
3. Resources or information needed
4. Success criteria

Format your response as follows:
ACTIONS: [List of specific actions]
CHALLENGES: [List of potential challenges]
RESOURCES: [List of needed resources]
SUCCESS_CRITERIA: [Clear success criteria]"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare with step-specific focus."""
        shared["step_focus"] = self.step_focus
        return self.prompt_template.format(**shared)


class SynthesisNode(AsyncClaudeNode):
    """Synthesizes results from multiple reasoning steps."""

    def __init__(self, **kwargs):
        prompt_template = """You are synthesizing the results of a multi-step reasoning process.

Original Problem: {problem}
Problem Decomposition: {decomposition}

Step Analyses:
{step_analyses}

Please synthesize all the information and provide:
1. A comprehensive solution
2. Key insights gained
3. Potential risks or limitations
4. Next steps or recommendations

Format your response as follows:
SOLUTION: [Comprehensive solution]
INSIGHTS: [Key insights from the process]
RISKS: [Potential risks or limitations]
RECOMMENDATIONS: [Next steps or recommendations]"""

        super().__init__(prompt_template=prompt_template, **kwargs)


class DecisionNode(AsyncClaudeNode):
    """Makes decisions based on analysis and criteria."""

    def __init__(self, decision_type: str = "binary", **kwargs):
        self.decision_type = decision_type
        prompt_template = """You are making a {decision_type} decision based on available information.

Context: {context}
Analysis: {analysis}
Decision Criteria: {criteria}

Please evaluate the options and make a decision:
1. Evaluation of each option against criteria
2. Rationale for your decision
3. Confidence level (1-10)
4. Potential consequences

Format your response as follows:
EVALUATION: [Evaluation of options]
RATIONALE: [Clear reasoning for decision]
CONFIDENCE: [1-10 confidence level]
CONSEQUENCES: [Potential outcomes]
DECISION: [Clear decision statement]"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare with decision-specific context."""
        shared["decision_type"] = self.decision_type
        return self.prompt_template.format(**shared)


class CreativeIdeationNode(AsyncClaudeNode):
    """Generates creative ideas using structured thinking."""

    def __init__(self, ideation_phase: str, **kwargs):
        self.ideation_phase = ideation_phase
        prompt_templates = {
            "divergent": """You are in the divergent thinking phase. Generate as many ideas as possible without judgment.

Topic: {topic}
Constraints: {constraints}

Generate diverse, creative ideas. Quantity over quality at this stage.
IDEAS: [List of creative ideas]""",

            "convergent": """You are in the convergent thinking phase. Evaluate and refine the generated ideas.

Topic: {topic}
Generated Ideas: {ideas}
Evaluation Criteria: {criteria}

Select and refine the best ideas.
SELECTED_IDEAS: [Top 3-5 refined ideas with rationale]""",

            "development": """You are developing the selected ideas into concrete solutions.

Topic: {topic}
Selected Ideas: {selected_ideas}

Develop each idea with practical details.
DEVELOPED_SOLUTIONS: [Detailed solutions with implementation steps]"""
        }

        super().__init__(prompt_template=prompt_templates[ideation_phase], **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare with phase-specific context."""
        shared["ideation_phase"] = self.ideation_phase
        return self.prompt_template.format(**shared)


async def example_problem_analysis():
    """Example 1: Complex problem analysis workflow."""
    print("\n" + "="*60)
    print("Example 1: Complex Problem Analysis Workflow")
    print("="*60)

    # Define the reasoning workflow
    problem = "How can we reduce plastic waste in our city by 50% within 2 years?"

    # Create nodes for each step
    decomposition_node = ProblemDecompositionNode(
        system_prompt="You are an expert environmental policy advisor."
    )

    analysis_nodes = {
        "policy": StepAnalysisNode(
            step_focus="Policy and regulation",
            system_prompt="You are an expert in environmental policy."
        ),
        "infrastructure": StepAnalysisNode(
            step_focus="Infrastructure and technology",
            system_prompt="You are an expert in waste management infrastructure."
        ),
        "community": StepAnalysisNode(
            step_focus="Community engagement and education",
            system_prompt="You are an expert in community outreach programs."
        )
    }

    synthesis_node = SynthesisNode(
        system_prompt="You are a senior consultant integrating environmental solutions."
    )

    # Create the graph
    graph = Graph(nodes={
        "decompose": decomposition_node,
        **analysis_nodes,
        "synthesize": synthesis_node
    })

    # Execute the workflow
    shared_context = {"problem": problem}

    try:
        print(f"Problem: {problem}\n")

        # Step 1: Problem decomposition
        print("--- Step 1: Problem Decomposition ---")
        result = await graph.run(
            start_node="decompose",
            shared=shared_context
        )
        decomposition = shared_context.get("claude_response", "")
        print(f"{decomposition}\n")

        # Step 2: Analyze each component
        step_analyses = []
        for step_name, step_node in analysis_nodes.items():
            print(f"--- Step 2: Analyzing {step_name.title()} ---")
            shared_context["decomposition"] = decomposition

            result = await graph.run(
                start_node=step_name,
                shared=shared_context
            )

            analysis = shared_context.get("claude_response", "")
            step_analyses.append(f"{step_name.upper()} ANALYSIS:\n{analysis}")
            print(f"{analysis}\n")

        # Step 3: Synthesize results
        print("--- Step 3: Synthesis and Solution ---")
        shared_context["step_analyses"] = "\n\n".join(step_analyses)

        result = await graph.run(
            start_node="synthesize",
            shared=shared_context
        )

        final_solution = shared_context.get("claude_response", "")
        print(f"{final_solution}")

    except Exception as e:
        print(f"Error in problem analysis workflow: {e}")


async def example_decision_tree():
    """Example 2: Multi-path decision making workflow."""
    print("\n" + "="*60)
    print("Example 2: Multi-path Decision Making")
    print("="*60)

    # Decision scenario
    context = "A software company needs to choose a new technology stack for their flagship product."
    criteria = "Performance, scalability, developer productivity, cost, and time to market"

    # Create decision nodes
    initial_decision = DecisionNode(
        decision_type="technology_selection",
        system_prompt="You are a CTO making strategic technology decisions."
    )

    # Risk assessment
    risk_decision = DecisionNode(
        decision_type="risk_assessment",
        system_prompt="You are a risk management specialist evaluating technology choices."
    )

    # Final go/no-go decision
    final_decision = DecisionNode(
        decision_type="implementation",
        system_prompt="You are the CEO making final implementation decisions."
    )

    # Create graph
    graph = Graph(nodes={
        "initial_decision": initial_decision,
        "risk_assessment": risk_decision,
        "final_decision": final_decision
    })

    shared_context = {
        "context": context,
        "criteria": criteria
    }

    try:
        print(f"Context: {context}\n")
        print(f"Criteria: {criteria}\n")

        # Step 1: Initial technology decision
        print("--- Step 1: Technology Selection Decision ---")
        result = await graph.run(
            start_node="initial_decision",
            shared=shared_context
        )

        initial_result = shared_context.get("claude_response", "")
        print(f"{initial_result}\n")

        # Step 2: Risk assessment
        print("--- Step 2: Risk Assessment ---")
        shared_context["analysis"] = initial_result

        result = await graph.run(
            start_node="risk_assessment",
            shared=shared_context
        )

        risk_assessment = shared_context.get("claude_response", "")
        print(f"{risk_assessment}\n")

        # Step 3: Final implementation decision
        print("--- Step 3: Final Implementation Decision ---")
        shared_context["analysis"] = risk_assessment

        result = await graph.run(
            start_node="final_decision",
            shared=shared_context
        )

        final_decision_result = shared_context.get("claude_response", "")
        print(f"{final_decision_result}")

    except Exception as e:
        print(f"Error in decision workflow: {e}")


async def example_creative_process():
    """Example 3: Creative ideation workflow."""
    print("\n" + "="*60)
    print("Example 3: Creative Ideation Workflow")
    print("="*60)

    # Creative challenge
    topic = "Design an innovative mobile app to help people reduce their carbon footprint"
    constraints = "Must be user-friendly, measurable impact, and sustainable business model"

    # Create ideation nodes
    divergent_node = CreativeIdeationNode(
        ideation_phase="divergent",
        system_prompt="You are a creative brainstorming facilitator. Think expansively and without limits."
    )

    convergent_node = CreativeIdeationNode(
        ideation_phase="convergent",
        system_prompt="You are a product evaluation expert. Critically assess ideas for feasibility and impact."
    )

    development_node = CreativeIdeationNode(
        ideation_phase="development",
        system_prompt="You are a product development specialist. Turn concepts into actionable plans."
    )

    # Create graph
    graph = Graph(nodes={
        "divergent": divergent_node,
        "convergent": convergent_node,
        "development": development_node
    })

    shared_context = {
        "topic": topic,
        "constraints": constraints,
        "criteria": "Innovation, impact, feasibility, user engagement, sustainability"
    }

    try:
        print(f"Topic: {topic}")
        print(f"Constraints: {constraints}\n")

        # Phase 1: Divergent thinking
        print("--- Phase 1: Divergent Thinking (Idea Generation) ---")
        result = await graph.run(
            start_node="divergent",
            shared=shared_context
        )

        generated_ideas = shared_context.get("claude_response", "")
        print(f"{generated_ideas}\n")

        # Phase 2: Convergent thinking
        print("--- Phase 2: Convergent Thinking (Idea Selection) ---")
        shared_context["ideas"] = generated_ideas

        result = await graph.run(
            start_node="convergent",
            shared=shared_context
        )

        selected_ideas = shared_context.get("claude_response", "")
        print(f"{selected_ideas}\n")

        # Phase 3: Development
        print("--- Phase 3: Solution Development ---")
        shared_context["selected_ideas"] = selected_ideas

        result = await graph.run(
            start_node="development",
            shared=shared_context
        )

        developed_solutions = shared_context.get("claude_response", "")
        print(f"{developed_solutions}")

    except Exception as e:
        print(f"Error in creative process: {e}")


async def example_research_synthesis():
    """Example 4: Research and synthesis workflow."""
    print("\n" + "="*60)
    print("Example 4: Research Synthesis Workflow")
    print("="*60)

    # Research topic
    research_question = "What are the most effective strategies for remote team collaboration in post-pandemic workplaces?"

    # Create research nodes
    literature_review_node = ClaudeNode(
        prompt_template="""You are conducting a literature review on the following research question:

Research Question: {research_question}

Provide a comprehensive literature review covering:
1. Key theories and frameworks
2. Major findings from recent studies
3. Identified gaps in research
4. Emerging trends

LITERATURE_REVIEW: [Comprehensive review of existing knowledge]""",
        system_prompt="You are an academic researcher specializing in organizational behavior and remote work."
    )

    gap_analysis_node = ClaudeNode(
        prompt_template="""Based on the literature review, identify critical gaps and opportunities for new research.

Research Question: {research_question}
Literature Review: {literature_review}

Analyze and identify:
1. Critical research gaps
2. Contradictory findings
3. Underexplored areas
4. Methodological limitations

GAP_ANALYSIS: [Detailed analysis of research gaps]""",
        system_prompt="You are a research methodology expert identifying opportunities for new knowledge."
    )

    methodology_node = ClaudeNode(
        prompt_template="""Design a research methodology to address the identified gaps.

Research Question: {research_question}
Gap Analysis: {gap_analysis}

Propose a comprehensive research approach:
1. Research design and methods
2. Data collection strategies
3. Analysis framework
4. Expected contributions

METHODOLOGY: [Detailed research methodology]""",
        system_prompt="You are a research design specialist creating robust research methodologies."
    )

    # Create graph
    graph = Graph(nodes={
        "literature_review": literature_review_node,
        "gap_analysis": gap_analysis_node,
        "methodology": methodology_node
    })

    shared_context = {"research_question": research_question}

    try:
        print(f"Research Question: {research_question}\n")

        # Step 1: Literature review
        print("--- Step 1: Literature Review ---")
        result = await graph.run(
            start_node="literature_review",
            shared=shared_context
        )

        literature = shared_context.get("claude_response", "")
        print(f"{literature}\n")

        # Step 2: Gap analysis
        print("--- Step 2: Gap Analysis ---")
        shared_context["literature_review"] = literature

        result = await graph.run(
            start_node="gap_analysis",
            shared=shared_context
        )

        gaps = shared_context.get("claude_response", "")
        print(f"{gaps}\n")

        # Step 3: Methodology design
        print("--- Step 3: Research Methodology ---")
        shared_context["gap_analysis"] = gaps

        result = await graph.run(
            start_node="methodology",
            shared=shared_context
        )

        methodology = shared_context.get("claude_response", "")
        print(f"{methodology}")

    except Exception as e:
        print(f"Error in research synthesis: {e}")


async def main():
    """Run all examples."""
    examples = [
        ("problem_analysis", "Complex Problem Analysis Workflow"),
        ("decision_tree", "Multi-path Decision Making"),
        ("creative_process", "Creative Ideation Workflow"),
        ("research_synthesis", "Research Synthesis Workflow"),
    ]

    # List available examples
    import sys
    if len(sys.argv) == 1:
        print("Available examples:")
        for example_id, description in examples:
            print(f"  {example_id} - {description}")
        print("\nUsage:")
        print("  python claude_reasoning_workflow.py all                    # Run all examples")
        print("  python claude_reasoning_workflow.py <example_name>       # Run specific example")
        return

    # Run specific example or all examples
    target = sys.argv[1] if len(sys.argv) > 1 else None

    if target == "all":
        for example_id, _ in examples:
            try:
                await globals()[f"example_{example_id}"]()
            except Exception as e:
                print(f"Error in {example_id}: {e}")
    elif target in [ex[0] for ex in examples]:
        try:
            await globals()[f"example_{target}"]()
        except Exception as e:
            print(f"Error in {target}: {e}")
    else:
        print(f"Unknown example: {target}")
        print("Available examples:", ", ".join([ex[0] for ex in examples]))


if __name__ == "__main__":
    anyio.run(main)