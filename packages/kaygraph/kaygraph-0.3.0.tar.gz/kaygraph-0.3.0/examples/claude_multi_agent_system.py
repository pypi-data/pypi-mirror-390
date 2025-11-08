#!/usr/bin/env python3
"""Multi-Agent System with Claude Coordination and KayGraph.

This example demonstrates a sophisticated multi-agent system where multiple Claude agents
collaborate, coordinate, and delegate tasks to achieve complex goals.

Examples:
    specialist_agents - Domain specialist agents working together
    hierarchical_agents - Multi-level agent hierarchy with coordination
    collaborative_problem_solving - Agents working on different aspects of a problem
    agent_delegation - Intelligent task delegation between agents
    competitive_agents - Multiple agents providing different perspectives

Usage:
./examples/claude_multi_agent_system.py - List the examples
./examples/claude_multi_agent_system.py all - Run all examples
./examples/claude_multi_agent_system.py specialist_agents - Run specific example

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
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

from kaygraph import Graph, AsyncNode
from kaygraph_claude_base import AsyncClaudeNode, ClaudeConfig


class AgentRole(Enum):
    """Different roles that agents can play in a multi-agent system."""
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    EXECUTOR = "executor"
    ADVISOR = "advisor"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    sender: str
    recipient: str
    content: str
    message_type: str = "task"
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    """Task assigned to an agent."""
    id: str
    description: str
    assigned_to: str
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)


class CoordinatorAgent(AsyncClaudeNode):
    """Coordinates between multiple specialist agents."""

    def __init__(self, available_agents: List[str], **kwargs):
        self.available_agents = available_agents
        prompt_template = """You are a coordinator agent managing a team of specialist agents.

Available specialists: {agents}

Current project: {project}
Current task: {task}
Team progress: {progress}

Your responsibilities:
1. Analyze the current task and determine which specialists are needed
2. Delegate subtasks to appropriate agents
3. Coordinate the workflow and manage dependencies
4. Synthesize results from specialist agents

Available agents: {agents}

Please coordinate this task by:
1. Breaking it down into subtasks if needed
2. Assigning subtasks to appropriate specialists
3. Providing a coordination plan

COORDINATION_PLAN:"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare coordination context."""
        return {
            "agents": ", ".join(self.available_agents),
            "project": shared.get("project", "Unknown project"),
            "task": shared.get("current_task", "No task specified"),
            "progress": shared.get("team_progress", "No progress yet")
        }


class SpecialistAgent(AsyncClaudeNode):
    """Domain specialist agent."""

    def __init__(self, specialty: str, expertise_areas: List[str], **kwargs):
        self.specialty = specialty
        self.expertise_areas = expertise_areas
        prompt_template = """You are a {specialty} specialist with expertise in: {expertise}.

Task assigned: {task}
Context: {context}
Additional requirements: {requirements}

Please provide your specialist analysis and recommendations:
1. Apply your domain expertise to the task
2. Identify key considerations specific to your field
3. Provide actionable recommendations
4. Note any limitations or areas requiring other expertise

SPECIALIST_ANALYSIS:"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare specialist context."""
        return {
            "specialty": self.specialty,
            "expertise": ", ".join(self.expertise_areas),
            "task": shared.get("assigned_task", "No task assigned"),
            "context": shared.get("task_context", ""),
            "requirements": shared.get("requirements", "No specific requirements")
        }


class AnalystAgent(AsyncClaudeNode):
    """Analyzes and synthesizes information from multiple agents."""

    def __init__(self, **kwargs):
        prompt_template = """You are an analyst agent that synthesizes information from multiple specialist perspectives.

Project context: {project}
Specialist inputs: {specialist_inputs}
Analysis requirements: {requirements}

Please analyze the specialist inputs and provide:
1. Key insights and patterns across different perspectives
2. Areas of agreement and disagreement
3. Integrated recommendations
4. Critical success factors and risks

SYNTHESIS_ANALYSIS:"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare analysis context."""
        specialist_inputs = shared.get("specialist_results", [])
        formatted_inputs = []

        for i, input_data in enumerate(specialist_inputs):
            if isinstance(input_data, dict):
                specialist = input_data.get("specialist", "Unknown")
                result = input_data.get("result", "No result")
                formatted_inputs.append(f"{specialist}: {result}")

        return {
            "project": shared.get("project", "Unknown project"),
            "specialist_inputs": "\n\n".join(formatted_inputs),
            "requirements": shared.get("analysis_requirements", "Comprehensive analysis")
        }


class ReviewerAgent(AsyncClaudeNode):
    """Reviews and validates work from other agents."""

    def __init__(self, review_criteria: List[str], **kwargs):
        self.review_criteria = review_criteria
        prompt_template = """You are a reviewer agent ensuring quality and consistency across the multi-agent system.

Work to review: {work_to_review}
Review criteria: {criteria}
Context: {context}

Please review the work against the following criteria: {criteria}

Provide:
1. Overall assessment (Excellent/Good/Adequate/Needs Improvement)
2. Specific feedback for each criterion
3. Recommendations for improvement
4. Approval status (Approved/Needs Revision/Rejected)

REVIEW_REPORT:"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare review context."""
        return {
            "work_to_review": shared.get("work_for_review", "No work provided"),
            "criteria": ", ".join(self.review_criteria),
            "context": shared.get("review_context", "No context provided")
        }


class DelegationAgent(AsyncClaudeNode):
    """Intelligently delegates tasks to the most appropriate agents."""

    def __init__(self, agent_capabilities: Dict[str, List[str]], **kwargs):
        self.agent_capabilities = agent_capabilities
        prompt_template = """You are a delegation agent that assigns tasks to the most suitable agents.

Available agents and their capabilities:
{agent_capabilities}

Current task: {task}
Task requirements: {requirements}
Deadline: {deadline}

Analyze the task and determine:
1. Which agent(s) are best suited for this task
2. How to break down the task if multiple agents are needed
3. Priority level and estimated timeline
4. Any special considerations

DELEGATION_PLAN:"""

        super().__init__(prompt_template=prompt_template, **kwargs)

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare delegation context."""
        capabilities_text = []
        for agent, caps in self.agent_capabilities.items():
            capabilities_text.append(f"{agent}: {', '.join(caps)}")

        return {
            "agent_capabilities": "\n".join(capabilities_text),
            "task": shared.get("task_to_delegate", "No task provided"),
            "requirements": shared.get("task_requirements", "No requirements specified"),
            "deadline": shared.get("deadline", "No deadline specified")
        }


# ===== EXAMPLE FUNCTIONS =====

async def example_specialist_agents():
    """Example 1: Domain specialist agents collaborating on a complex project."""
    print("\n" + "="*70)
    print("Example 1: Specialist Agent Collaboration")
    print("="*70)

    # Create specialist agents
    tech_specialist = SpecialistAgent(
        specialty="Technology",
        expertise_areas=["Software architecture", "Cloud computing", "AI/ML", "Security"]
    )

    business_specialist = SpecialistAgent(
        specialty="Business Strategy",
        expertise_areas=["Market analysis", "Business models", "Competitive analysis", "ROI analysis"]
    )

    ux_specialist = SpecialistAgent(
        specialty="User Experience",
        expertise_areas=["User research", "Interface design", "Usability testing", "Accessibility"]
    )

    # Create coordinator and analyst
    coordinator = CoordinatorAgent(
        available_agents=["technology", "business_strategy", "user_experience"],
        system_prompt="You are coordinating a digital product launch project."
    )

    analyst = AnalystAgent(
        system_prompt="You are synthesizing inputs for a comprehensive product strategy."
    )

    # Create multi-agent graph
    graph = Graph(nodes={
        "coordinator": coordinator,
        "tech_specialist": tech_specialist,
        "business_specialist": business_specialist,
        "ux_specialist": ux_specialist,
        "analyst": analyst
    })

    # Project: Launch a new mobile app
    shared_context = {
        "project": "Launch a new mobile fitness tracking app",
        "current_task": "Develop comprehensive launch strategy",
        "team_progress": "Initial planning phase"
    }

    try:
        print("Project: Launch a new mobile fitness tracking app")
        print("="*50)

        # Step 1: Coordination planning
        print("\n--- Step 1: Coordinator Planning ---")
        result = await graph.run(
            start_node="coordinator",
            shared=shared_context
        )
        coordination_plan = shared_context.get("claude_response", "")
        print(f"{coordination_plan}")

        # Step 2: Specialist contributions
        specialists = [
            ("tech_specialist", "technology", "Evaluate technical architecture and scalability requirements"),
            ("business_specialist", "business_strategy", "Analyze market opportunities and monetization strategy"),
            ("ux_specialist", "user_experience", "Design user journey and engagement strategy")
        ]

        specialist_results = []

        for specialist_id, specialty, task in specialists:
            print(f"\n--- Step 2: {specialty.title()} Specialist Analysis ---")
            shared_context.update({
                "assigned_task": task,
                "task_context": f"Mobile fitness app for tracking workouts and nutrition",
                "requirements": "Focus on scalable, user-friendly solution with clear monetization"
            })

            result = await graph.run(
                start_node=specialist_id,
                shared=shared_context
            )

            specialist_result = shared_context.get("claude_response", "")
            specialist_results.append({
                "specialist": specialty,
                "result": specialist_result
            })
            print(f"{specialty.title()} Analysis:\n{specialist_result}")

        # Step 3: Analysis and synthesis
        print("\n--- Step 3: Cross-Functional Analysis ---")
        shared_context.update({
            "specialist_results": specialist_results,
            "analysis_requirements": "Synthesize into comprehensive launch strategy with timeline and risks"
        })

        result = await graph.run(
            start_node="analyst",
            shared=shared_context
        )

        final_analysis = shared_context.get("claude_response", "")
        print(f"\nFinal Integrated Strategy:\n{final_analysis}")

    except Exception as e:
        print(f"Error in specialist agent collaboration: {e}")


async def example_hierarchical_agents():
    """Example 2: Hierarchical agent system with multiple coordination levels."""
    print("\n" + "="*70)
    print("Example 2: Hierarchical Multi-Agent System")
    print("="*70)

    # Create different levels of agents
    # Executive level
    executive_coordinator = CoordinatorAgent(
        available_agents=["department_heads"],
        system_prompt="You are an executive coordinator overseeing strategic initiatives."
    )

    # Department level
    tech_lead = SpecialistAgent(
        specialty="Technology Leadership",
        expertise_areas=["Technical strategy", "Team management", "Architecture oversight"]
    )

    product_lead = SpecialistAgent(
        specialty="Product Leadership",
        expertise_areas=["Product strategy", "Roadmap planning", "Stakeholder management"]
    )

    # Specialist level
    frontend_specialist = SpecialistAgent(
        specialty="Frontend Development",
        expertise_areas=["React/Vue", "UI/UX implementation", "Performance optimization"]
    )

    backend_specialist = SpecialistAgent(
        specialty="Backend Development",
        expertise_areas=["API design", "Database architecture", "System integration"]
    )

    # Review level
    quality_reviewer = ReviewerAgent(
        review_criteria=["strategic_alignment", "feasibility", "resource_allocation", "timeline_realism"],
        system_prompt="You are a quality assurance reviewer ensuring strategic alignment."
    )

    # Create hierarchical graph
    hierarchical_graph = Graph(nodes={
        "executive": executive_coordinator,
        "tech_lead": tech_lead,
        "product_lead": product_lead,
        "frontend_specialist": frontend_specialist,
        "backend_specialist": backend_specialist,
        "quality_reviewer": quality_reviewer
    })

    # Strategic initiative: Digital transformation
    shared_context = {
        "project": "Company-wide Digital Transformation Initiative",
        "current_task": "Develop 3-year digital transformation roadmap",
        "team_progress": "Strategic planning phase"
    }

    try:
        print("Strategic Initiative: Company-wide Digital Transformation")
        print("="*60)

        # Level 1: Executive coordination
        print("\n--- Level 1: Executive Coordination ---")
        result = await hierarchical_graph.run(
            start_node="executive",
            shared=shared_context
        )
        executive_direction = shared_context.get("claude_response", "")
        print(f"Executive Direction:\n{executive_direction}")

        # Level 2: Department leadership
        print("\n--- Level 2: Department Leadership Planning ---")

        # Technology leadership
        shared_context.update({
            "assigned_task": "Develop technology transformation roadmap",
            "task_context": "Legacy systems modernization, cloud migration, digital infrastructure",
            "requirements": "Align with business goals, ensure scalability, manage risk"
        })

        result = await hierarchical_graph.run(
            start_node="tech_lead",
            shared=shared_context
        )
        tech_roadmap = shared_context.get("claude_response", "")
        print(f"\nTechnology Leadership Roadmap:\n{tech_roadmap}")

        # Product leadership
        shared_context.update({
            "assigned_task": "Develop product digitalization strategy",
            "task_context": "Product roadmap, customer experience digitalization, go-to-market strategy",
            "requirements": "Customer-centric, measurable impact, competitive advantage"
        })

        result = await hierarchical_graph.run(
            start_node="product_lead",
            shared=shared_context
        )
        product_strategy = shared_context.get("claude_response", "")
        print(f"\nProduct Leadership Strategy:\n{product_strategy}")

        # Level 3: Specialist implementation
        print("\n--- Level 3: Specialist Implementation Planning ---")

        # Frontend specialist
        shared_context.update({
            "assigned_task": "Frontend modernization and user experience transformation",
            "task_context": "Modern frontend stack, responsive design, performance optimization",
            "requirements": "Mobile-first, accessible, performant, maintainable"
        })

        result = await hierarchical_graph.run(
            start_node="frontend_specialist",
            shared=shared_context
        )
        frontend_plan = shared_context.get("claude_response", "")
        print(f"\nFrontend Modernization Plan:\n{frontend_plan}")

        # Backend specialist
        shared_context.update({
            "assigned_task": "Backend architecture modernization",
            "task_context": "Microservices migration, API strategy, data architecture",
            "requirements": "Scalable, secure, maintainable, cloud-native"
        })

        result = await hierarchical_graph.run(
            start_node="backend_specialist",
            shared=shared_context
        )
        backend_plan = shared_context.get("claude_response", "")
        print(f"\nBackend Modernization Plan:\n{backend_plan}")

        # Level 4: Quality review
        print("\n--- Level 4: Strategic Quality Review ---")
        combined_results = [
            executive_direction,
            tech_roadmap,
            product_strategy,
            frontend_plan,
            backend_plan
        ]

        shared_context.update({
            "work_for_review": "\n\n".join([f"Section {i+1}:\n{result}" for i, result in enumerate(combined_results)]),
            "review_context": "Review complete digital transformation roadmap for strategic alignment and feasibility"
        })

        result = await hierarchical_graph.run(
            start_node="quality_reviewer",
            shared=shared_context
        )
        quality_review = shared_context.get("claude_response", "")
        print(f"\nQuality Review:\n{quality_review}")

    except Exception as e:
        print(f"Error in hierarchical agent system: {e}")


async def example_collaborative_problem_solving():
    """Example 3: Agents working on different aspects of a complex problem."""
    print("\n" + "="*70)
    print("Example 3: Collaborative Problem Solving")
    print("="*70)

    # Problem: Sustainable urban development
    # Create specialist agents for different aspects
    environmental_specialist = SpecialistAgent(
        specialty="Environmental Science",
        expertise_areas=["Sustainability", "Climate impact", "Green infrastructure", "Conservation"]
    )

    urban_planning_specialist = SpecialistAgent(
        specialty="Urban Planning",
        expertise_areas=["City design", "Transportation", "Zoning", "Public spaces"]
    )

    economic_specialist = SpecialistAgent(
        specialty="Economic Development",
        expertise_areas=["Cost-benefit analysis", "Economic impact", "Funding strategies", "Job creation"]
    )

    social_specialist = SpecialistAgent(
        specialty="Social Impact",
        expertise_areas=["Community engagement", "Equity", "Public health", "Education"]
    )

    # Integration agents
    integration_analyst = AnalystAgent(
        system_prompt="You are integrating multiple perspectives for sustainable urban development."
    )

    consensus_builder = CoordinatorAgent(
        available_agents=["environmental", "urban_planning", "economic", "social"],
        system_prompt="You are building consensus among different stakeholders for urban development."
    )

    # Create collaborative graph
    collaborative_graph = Graph(nodes={
        "environmental": environmental_specialist,
        "urban_planning": urban_planning_specialist,
        "economic": economic_specialist,
        "social": social_specialist,
        "integration": integration_analyst,
        "consensus": consensus_builder
    })

    # Complex problem scenario
    shared_context = {
        "project": "Sustainable Urban Development Plan",
        "current_task": "Develop comprehensive sustainability plan for mid-sized city",
        "team_progress": "Stakeholder analysis complete"
    }

    try:
        print("Problem: Sustainable Urban Development for Mid-Sized City")
        print("="*65)

        # Phase 1: Individual specialist analysis
        specialists = [
            ("environmental", "environmental", "Analyze environmental impact and sustainability opportunities"),
            ("urban_planning", "urban_planning", "Design sustainable urban layout and infrastructure"),
            ("economic", "economic", "Evaluate economic viability and funding strategies"),
            ("social", "social", "Assess social impact and community benefits")
        ]

        specialist_analyses = []

        for specialist_id, specialty, task in specialists:
            print(f"\n--- {specialty.title()} Analysis ---")
            shared_context.update({
                "assigned_task": task,
                "task_context": "Mid-sized city (500K population) aiming for carbon neutrality by 2035",
                "requirements": "Balance environmental goals with economic and social feasibility"
            })

            result = await collaborative_graph.run(
                start_node=specialist_id,
                shared=shared_context
            )

            analysis = shared_context.get("claude_response", "")
            specialist_analyses.append({
                "specialist": specialty,
                "analysis": analysis
            })
            print(f"{analysis}")

        # Phase 2: Integration analysis
        print("\n--- Cross-Domain Integration ---")
        shared_context.update({
            "specialist_results": specialist_analyses,
            "analysis_requirements": "Identify synergies, conflicts, and integrated solutions across all domains"
        })

        result = await collaborative_graph.run(
            start_node="integration",
            shared=shared_context
        )
        integration_result = shared_context.get("claude_response", "")
        print(f"Integration Analysis:\n{integration_result}")

        # Phase 3: Consensus building
        print("\n--- Consensus Building ---")
        shared_context.update({
            "current_task": "Build consensus on integrated sustainable development plan",
            "team_progress": "Individual analyses complete, integration analysis available"
        })

        result = await collaborative_graph.run(
            start_node="consensus",
            shared=shared_context
        )
        consensus_plan = shared_context.get("claude_response", "")
        print(f"\nConsensus-Based Action Plan:\n{consensus_plan}")

    except Exception as e:
        print(f"Error in collaborative problem solving: {e}")


async def example_agent_delegation():
    """Example 4: Intelligent task delegation between agents."""
    print("\n" + "="*70)
    print("Example 4: Intelligent Agent Delegation")
    print("="*70)

    # Define agent capabilities
    agent_capabilities = {
        "data_analyst": ["Statistical analysis", "Data visualization", "Pattern recognition", "Report generation"],
        "researcher": ["Literature review", "Fact-checking", "Source verification", "Information synthesis"],
        "writer": ["Content creation", "Editing", "Technical writing", "Creative writing"],
        "strategist": ["Planning", "Risk assessment", "Resource allocation", "Timeline development"],
        "technical_expert": ["System design", "Implementation", "Troubleshooting", "Optimization"]
    }

    # Create delegation system
    delegator = DelegationAgent(
        agent_capabilities=agent_capabilities,
        system_prompt="You are an intelligent task delegator optimizing for efficiency and quality."
    )

    # Create specialist agents
    data_analyst = SpecialistAgent(
        specialty="Data Analysis",
        expertise_areas=agent_capabilities["data_analyst"]
    )

    researcher = SpecialistAgent(
        specialty="Research",
        expertise_areas=agent_capabilities["researcher"]
    )

    writer = SpecialistAgent(
        specialty="Writing",
        expertise_areas=agent_capabilities["writer"]
    )

    strategist = SpecialistAgent(
        specialty="Strategy",
        expertise_areas=agent_capabilities["strategist"]
    )

    technical_expert = SpecialistAgent(
        specialty="Technical Implementation",
        expertise_areas=agent_capabilities["technical_expert"]
    )

    # Create delegation graph
    delegation_graph = Graph(nodes={
        "delegator": delegator,
        "data_analyst": data_analyst,
        "researcher": researcher,
        "writer": writer,
        "strategist": strategist,
        "technical_expert": technical_expert
    })

    # Complex tasks requiring delegation
    delegation_tasks = [
        {
            "task": "Create comprehensive market analysis report for new product launch",
            "requirements": "Include market size, competitor analysis, customer segments, and recommendations",
            "deadline": "2 weeks"
        },
        {
            "task": "Develop AI-powered customer service chatbot",
            "requirements": "Natural language processing, integration with existing systems, user-friendly interface",
            "deadline": "3 months"
        },
        {
            "task": "Write grant proposal for renewable energy research project",
            "requirements": "Technical specifications, budget justification, impact assessment, timeline",
            "deadline": "1 month"
        }
    ]

    try:
        for i, task_info in enumerate(delegation_tasks, 1):
            print(f"\n--- Delegation Task {i} ---")
            print(f"Task: {task_info['task']}")
            print(f"Requirements: {task_info['requirements']}")
            print(f"Deadline: {task_info['deadline']}")

            # Step 1: Delegation planning
            shared_context = {
                "task_to_delegate": task_info["task"],
                "task_requirements": task_info["requirements"],
                "deadline": task_info["deadline"]
            }

            result = await delegation_graph.run(
                start_node="delegator",
                shared=shared_context
            )
            delegation_plan = shared_context.get("claude_response", "")
            print(f"\nDelegation Plan:\n{delegation_plan}")

            # Step 2: Execute delegated tasks (simulation)
            print(f"\n--- Executing Delegated Tasks ---")

            # Simulate task execution by relevant specialists
            # (In a real system, this would be dynamically determined)
            if "market analysis" in task_info["task"].lower():
                # Delegate to researcher, data_analyst, writer, strategist
                for specialist in ["researcher", "data_analyst", "strategist", "writer"]:
                    shared_context.update({
                        "assigned_task": f"Contribute {specialist} expertise to: {task_info['task']}",
                        "task_context": task_info["requirements"],
                        "requirements": f"Focus on {specialist} perspective, deadline: {task_info['deadline']}"
                    })

                    result = await delegation_graph.run(
                        start_node=specialist,
                        shared=shared_context
                    )
                    contribution = shared_context.get("claude_response", "")
                    print(f"\n{specialist.title()} Contribution:\n{contribution}")

            elif "chatbot" in task_info["task"].lower():
                # Delegate to technical_expert, researcher, writer, strategist
                for specialist in ["researcher", "technical_expert", "writer", "strategist"]:
                    shared_context.update({
                        "assigned_task": f"Provide {specialist} input for: {task_info['task']}",
                        "task_context": task_info["requirements"],
                        "requirements": f"Focus on {specialist} expertise, deadline: {task_info['deadline']}"
                    })

                    result = await delegation_graph.run(
                        start_node=specialist,
                        shared=shared_context
                    )
                    contribution = shared_context.get("claude_response", "")
                    print(f"\n{specialist.title()} Input:\n{contribution}")

            elif "grant proposal" in task_info["task"].lower():
                # Delegate to researcher, writer, strategist, technical_expert
                for specialist in ["researcher", "technical_expert", "strategist", "writer"]:
                    shared_context.update({
                        "assigned_task": f"Develop {specialist} section for: {task_info['task']}",
                        "task_context": task_info["requirements"],
                        "requirements": f"Create compelling {specialist} content, deadline: {task_info['deadline']}"
                    })

                    result = await delegation_graph.run(
                        start_node=specialist,
                        shared=shared_context
                    )
                    contribution = shared_context.get("claude_response", "")
                    print(f"\n{specialist.title()} Section:\n{contribution}")

    except Exception as e:
        print(f"Error in agent delegation: {e}")


async def main():
    """Run all examples."""
    examples = [
        ("specialist_agents", "Specialist Agent Collaboration"),
        ("hierarchical_agents", "Hierarchical Multi-Agent System"),
        ("collaborative_problem_solving", "Collaborative Problem Solving"),
        ("agent_delegation", "Intelligent Agent Delegation"),
    ]

    # List available examples
    import sys
    if len(sys.argv) == 1:
        print("Available examples:")
        for example_id, description in examples:
            print(f"  {example_id} - {description}")
        print("\nUsage:")
        print("  python claude_multi_agent_system.py all                    # Run all examples")
        print("  python claude_multi_agent_system.py <example_name>       # Run specific example")
        print("\nThese examples demonstrate sophisticated multi-agent coordination patterns.")
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