"""
Agent-specific prompts and behaviors for multi-agent system.
"""

from typing import Dict, Any, List


def get_supervisor_prompt(task: str, agent_capabilities: Dict[str, str]) -> str:
    """Get prompt for supervisor agent to plan task delegation."""
    agents_desc = "\n".join([f"- {name}: {desc}" for name, desc in agent_capabilities.items()])
    
    return f"""You are a supervisor agent coordinating a team to complete the following task:

Task: {task}

Available agents and their capabilities:
{agents_desc}

Analyze the task and create a delegation plan. Consider:
1. Which agents are needed for this task?
2. What order should they work in?
3. What specific subtasks should each agent handle?

Provide a structured plan for task delegation."""


def get_researcher_prompt(research_topic: str, specific_questions: List[str] = None) -> str:
    """Get prompt for research agent."""
    questions_text = ""
    if specific_questions:
        questions_text = "\n\nSpecific questions to address:\n" + \
                        "\n".join([f"- {q}" for q in specific_questions])
    
    return f"""You are a research agent tasked with gathering information on:

Topic: {research_topic}
{questions_text}

Conduct thorough research and provide:
1. Key facts and findings
2. Important context and background
3. Relevant statistics or data
4. Credible sources (if available)
5. Areas that need further investigation

Structure your findings clearly for other agents to use."""


def get_writer_prompt(topic: str, research_findings: str, style: str = "informative") -> str:
    """Get prompt for writer agent."""
    return f"""You are a writer agent creating content on:

Topic: {topic}
Writing style: {style}

Research findings provided:
{research_findings}

Create well-structured content that:
1. Is engaging and appropriate for the target audience
2. Incorporates the research findings naturally
3. Maintains the requested writing style
4. Is properly organized with clear sections
5. Includes a compelling introduction and conclusion"""


def get_reviewer_prompt(content: str, review_criteria: List[str] = None) -> str:
    """Get prompt for reviewer agent."""
    criteria_text = ""
    if review_criteria:
        criteria_text = "\n\nReview criteria:\n" + \
                       "\n".join([f"- {c}" for c in review_criteria])
    else:
        criteria_text = """
Review criteria:
- Accuracy and factual correctness
- Clarity and readability
- Structure and organization
- Grammar and style
- Completeness"""
    
    return f"""You are a reviewer agent evaluating the following content:

{content}
{criteria_text}

Provide a detailed review including:
1. Overall assessment
2. Strengths of the content
3. Areas for improvement
4. Specific suggestions for edits
5. Final recommendation (approve/revise)"""


def parse_supervisor_plan(response: str) -> Dict[str, Any]:
    """Parse supervisor's delegation plan."""
    # Simple parsing - in production, use structured output
    plan = {
        "agents_needed": [],
        "task_order": [],
        "agent_tasks": {}
    }
    
    # Mock parsing
    if "research" in response.lower():
        plan["agents_needed"].append("researcher")
        plan["agent_tasks"]["researcher"] = "Gather information on the topic"
    
    if "writ" in response.lower():
        plan["agents_needed"].append("writer")
        plan["agent_tasks"]["writer"] = "Create content based on research"
    
    if "review" in response.lower():
        plan["agents_needed"].append("reviewer")
        plan["agent_tasks"]["reviewer"] = "Review and improve the content"
    
    # Default order
    plan["task_order"] = ["researcher", "writer", "reviewer"]
    
    return plan


def format_final_output(task: str, results: Dict[str, Any]) -> str:
    """Format the final output from all agents."""
    output = f"""Multi-Agent Task Completion Report
=====================================

Original Task: {task}

Agent Contributions:
-------------------
"""
    
    for agent, result in results.items():
        output += f"\n{agent.title()} Agent:\n"
        output += f"{result}\n"
        output += "-" * 40 + "\n"
    
    output += "\nTask Status: Completed Successfully"
    
    return output


def get_agent_response(agent_type: str, prompt: str) -> str:
    """Get real LLM response for agent."""
    from .call_llm import call_llm
    
    # Map agent types to their system prompts
    system_prompts = {
        "supervisor": """You are a supervisor agent that coordinates other agents. When creating delegation plans, always include:
1. Research phase - to gather information
2. Writer phase - to create content
3. Review phase - to ensure quality
Your response should mention which agents are needed (researcher, writer, reviewer).""",
        "researcher": "You are a research agent that gathers information and provides comprehensive analysis.",
        "writer": "You are a writer agent that creates well-structured content based on research.",
        "reviewer": "You are a reviewer agent that evaluates content quality and suggests improvements."
    }
    
    system_prompt = system_prompts.get(agent_type, "You are a helpful AI assistant.")
    
    # Call real LLM
    return call_llm(prompt, system=system_prompt)