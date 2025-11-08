"""
Example 2: Prompt Chaining (Content Pipeline)

This example shows a complete content generation pipeline using prompt chaining:
1. Research the topic
2. Create an outline
3. Write the content
4. Edit for quality
5. Optimize for SEO

Pattern: Step 1 → Step 2 → Step 3 → Step 4 → Step 5
Each step validates output before proceeding to the next.
"""

import asyncio
import os
from kaygraph.agent import create_prompt_chain


# =============================================================================
# VALIDATION GATES
# =============================================================================

def validate_research(output: str) -> bool:
    """Ensure research has key points"""
    # Must have bullet points or numbered lists
    has_structure = ("•" in output or "-" in output or "1." in output)
    has_length = len(output) > 200
    return has_structure and has_length


def validate_outline(output: str) -> bool:
    """Ensure outline has sections"""
    # Must have headers (##)
    has_headers = "##" in output
    has_sections = output.count("##") >= 3
    return has_headers and has_sections


def validate_content(output: str) -> bool:
    """Ensure content meets minimum length"""
    word_count = len(output.split())
    return word_count >= 300


def validate_edited(output: str) -> bool:
    """Ensure editing made improvements"""
    # Check for proper capitalization and structure
    has_caps = any(c.isupper() for c in output[:50])
    return has_caps and len(output) > 200


# =============================================================================
# MOCK LLM FOR DEMONSTRATION
# =============================================================================

step_counter = [0]  # Mutable counter for demo


async def mock_llm(messages: list) -> dict:
    """Mock LLM that simulates content generation"""
    step_counter[0] += 1

    # Extract the system prompt to know which step we're on
    system_prompt = ""
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"].lower()
            break

    # Simulate different responses based on step
    if "research" in system_prompt:
        return {
            "content": """Research findings on AI Agents:

• AI agents are autonomous systems that use LLMs to make decisions
• They follow the ReAct pattern (Reasoning + Acting)
• Popular frameworks: LangChain, AutoGPT, KayGraph
• Key components: Tools, Memory, Planning
• Applications: Code generation, data analysis, customer support
• Challenges: Cost, latency, reliability"""
        }

    elif "outline" in system_prompt:
        return {
            "content": """## Introduction to AI Agents

## The ReAct Pattern
- What is ReAct?
- How it works
- Benefits

## Key Components
- Tool integration
- Memory systems
- Planning mechanisms

## Real-World Applications
- Software development
- Data analysis
- Customer service

## Challenges and Solutions
- Managing costs
- Ensuring reliability
- Reducing latency

## Conclusion"""
        }

    elif "write" in system_prompt or "draft" in system_prompt:
        return {
            "content": """# AI Agents: The Future of Intelligent Automation

AI agents represent a significant leap in artificial intelligence, enabling systems to autonomously make decisions and take actions based on language model reasoning. In this article, we'll explore how these intelligent systems work and their practical applications.

## The ReAct Pattern

At the core of modern AI agents lies the ReAct pattern - Reasoning plus Acting. This approach allows agents to think through problems step by step, use tools to gather information, and learn from the results. Unlike traditional software that follows fixed paths, ReAct agents adapt their behavior based on what they discover.

The pattern works in a simple loop: the agent thinks about what to do next, takes an action (like searching for information or running code), observes the results, and then thinks again. This cycle continues until the task is complete.

## Key Components

Successful AI agents require three essential components. First, they need tools - interfaces to interact with the world, whether that's searching databases, reading files, or calling APIs. Second, they need memory systems to maintain context across multiple interactions. Third, they need planning mechanisms to break down complex tasks into manageable steps.

## Real-World Applications

AI agents are already transforming industries. In software development, they can write code, fix bugs, and even conduct code reviews. For data analysis, they can query databases, generate visualizations, and derive insights. In customer service, they handle complex inquiries by gathering information from multiple sources and providing comprehensive responses.

## Challenges and Solutions

Despite their power, AI agents face several challenges. Cost management is crucial, as multiple LLM calls can become expensive. Reliability must be ensured through proper error handling and validation. Latency can be reduced by parallelizing independent operations and using efficient tool designs.

## Conclusion

AI agents represent a powerful new paradigm in artificial intelligence, combining the reasoning capabilities of large language models with the ability to take concrete actions. As the technology matures, we can expect to see even more sophisticated applications across every industry."""
        }

    elif "edit" in system_prompt:
        return {
            "content": """# AI Agents: The Future of Intelligent Automation

AI agents represent a transformative advancement in artificial intelligence, enabling systems to autonomously make decisions and execute actions through sophisticated language model reasoning. This comprehensive guide explores how these intelligent systems function and their practical applications across industries.

## Understanding the ReAct Pattern

Modern AI agents are built on the ReAct pattern—a powerful combination of Reasoning and Acting. This methodology enables agents to systematically analyze problems, leverage tools for information gathering, and learn from outcomes. Unlike conventional software following predetermined paths, ReAct agents dynamically adapt their behavior based on real-time discoveries.

The pattern operates through an elegant feedback loop: the agent analyzes the situation, executes an action (such as database queries or API calls), evaluates the results, and iterates. This cycle persists until achieving the desired outcome.

## Essential Components

Effective AI agents require three fundamental elements:

**Tools:** Sophisticated interfaces enabling interaction with various systems—from database searches to file operations and API integrations.

**Memory Systems:** Robust mechanisms maintaining conversational context and historical interactions across sessions.

**Planning Mechanisms:** Intelligent frameworks decomposing complex objectives into actionable, manageable subtasks.

## Practical Industry Applications

AI agents are revolutionizing multiple sectors:

**Software Development:** Automated code generation, intelligent debugging, and comprehensive code review processes.

**Data Analysis:** Advanced database querying, dynamic visualization generation, and actionable insight derivation.

**Customer Service:** Complex inquiry resolution through multi-source information aggregation and comprehensive response formulation.

## Addressing Key Challenges

While powerful, AI agents encounter specific challenges requiring strategic solutions:

**Cost Optimization:** Implement efficient tool design and strategic caching to manage LLM API expenses.

**Reliability Assurance:** Deploy robust error handling, comprehensive validation, and systematic testing protocols.

**Latency Reduction:** Leverage parallel processing for independent operations and optimize tool response times.

## Looking Forward

AI agents embody a paradigm shift in artificial intelligence, seamlessly merging large language model reasoning with practical action execution. As the technology evolves, expect increasingly sophisticated applications transforming business operations across all sectors."""
        }

    else:  # SEO optimization
        return {
            "content": """# AI Agents: The Future of Intelligent Automation | Complete 2025 Guide

**Meta Description:** Discover how AI agents work, the ReAct pattern, real-world applications, and implementation best practices. Complete guide to building intelligent autonomous systems.

**Keywords:** AI agents, ReAct pattern, intelligent automation, LLM agents, autonomous AI systems

---

AI agents represent a transformative advancement in artificial intelligence, enabling systems to autonomously make decisions and execute actions through sophisticated language model reasoning. This comprehensive guide explores how these intelligent systems function and their practical applications across industries.

## Understanding the ReAct Pattern for AI Agents

Modern AI agents are built on the **ReAct pattern**—a powerful combination of Reasoning and Acting that enables intelligent decision-making. This methodology enables agents to systematically analyze problems, leverage tools for information gathering, and learn from outcomes.

Unlike conventional software following predetermined paths, **ReAct agents** dynamically adapt their behavior based on real-time discoveries, making them ideal for complex, unpredictable tasks.

### How the ReAct Pattern Works

The pattern operates through an elegant feedback loop:
1. **Analyze** the current situation
2. **Execute** an action (database queries, API calls, file operations)
3. **Evaluate** the results
4. **Iterate** until achieving the desired outcome

## Essential Components of AI Agent Systems

Effective AI agents require three fundamental elements:

### 1. Tools and Integrations

Sophisticated interfaces enabling interaction with various systems—from database searches to file operations and API integrations. Well-designed tools are the foundation of capable AI agents.

### 2. Memory Systems

Robust mechanisms maintaining conversational context and historical interactions across sessions, enabling agents to learn and improve over time.

### 3. Planning Mechanisms

Intelligent frameworks decomposing complex objectives into actionable, manageable subtasks for systematic execution.

## Practical Industry Applications of AI Agents

### Software Development Automation
- Automated code generation and refactoring
- Intelligent debugging and error resolution
- Comprehensive code review processes

### Advanced Data Analysis
- Complex database querying and optimization
- Dynamic visualization generation
- Actionable insight derivation from large datasets

### Intelligent Customer Service
- Complex inquiry resolution
- Multi-source information aggregation
- Comprehensive response formulation

## Addressing Key Challenges in AI Agent Development

### Cost Optimization Strategies
Implement efficient tool design and strategic caching to manage LLM API expenses without sacrificing functionality.

### Ensuring System Reliability
Deploy robust error handling, comprehensive validation, and systematic testing protocols to maintain agent stability.

### Reducing Response Latency
Leverage parallel processing for independent operations and optimize tool response times for better user experience.

## The Future of AI Agents

AI agents embody a paradigm shift in artificial intelligence, seamlessly merging large language model reasoning with practical action execution. As the technology evolves, expect increasingly sophisticated applications transforming business operations across all sectors.

**Ready to build your own AI agent?** Start with frameworks like KayGraph, LangChain, or AutoGPT, and follow best practices for tool design, memory management, and systematic planning.

---

**Related Topics:** LangChain vs KayGraph, Building ReAct Agents, AI Agent Best Practices, LLM Tool Integration, Autonomous AI Systems"""
        }


# =============================================================================
# CREATE AND RUN PIPELINE
# =============================================================================

async def main():
    print("=" * 70)
    print("Prompt Chaining Example: Content Generation Pipeline")
    print("=" * 70)
    print()

    # Define the pipeline steps
    steps = [
        {
            "name": "research",
            "prompt": "Research the topic 'AI Agents'. Provide key facts, trends, and important concepts. Use bullet points.",
            "gate": validate_research
        },
        {
            "name": "outline",
            "prompt": "Based on the research, create a detailed outline for a blog post. Use ## for main sections. Include introduction, body sections, and conclusion.",
            "gate": validate_outline
        },
        {
            "name": "draft",
            "prompt": "Write a complete blog post following the outline. Aim for 400-500 words. Be informative and engaging.",
            "gate": validate_content
        },
        {
            "name": "edit",
            "prompt": "Edit the blog post for clarity, grammar, flow, and professionalism. Improve sentence structure and word choice.",
            "gate": validate_edited
        },
        {
            "name": "seo",
            "prompt": "Optimize the blog post for SEO. Add meta description, keywords, internal structure with H2/H3 tags, and improve readability."
        }
    ]

    print("Pipeline steps:")
    for i, step in enumerate(steps, 1):
        has_gate = "✓" if step.get("gate") else "○"
        print(f"  {i}. {step['name']:15} {has_gate} validation gate")
    print()

    # Create the chain
    chain = create_prompt_chain(steps, mock_llm)

    print("✓ Created prompt chain")
    print()

    # Run the pipeline
    print("Running pipeline...")
    print("-" * 70)

    result = await chain.run_async({
        "chain_output": "Topic: AI Agents and the ReAct Pattern"
    })

    print()
    print("=" * 70)
    print("FINAL OUTPUT")
    print("=" * 70)
    print()
    print(result["chain_output"])
    print()
    print("=" * 70)
    print()

    # Show pipeline history
    print("Pipeline History:")
    print("-" * 70)
    for entry in result["chain_history"]:
        step_name = entry["step"]
        output_preview = entry["output"][:100] + "..."
        print(f"✓ {step_name:15} {output_preview}")
    print()

    print(f"Total steps completed: {len(result['chain_history'])}")


# =============================================================================
# USAGE WITH REAL LLM
# =============================================================================

async def with_real_llm():
    """Example using real Anthropic Claude"""
    from anthropic import AsyncAnthropic

    async def claude_llm(messages):
        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            messages=messages,
            max_tokens=4000,
            temperature=0.7
        )

        return {"content": response.content[0].text}

    # Create chain with real LLM
    steps = [
        {"name": "research", "prompt": "Research AI agents...", "gate": validate_research},
        {"name": "outline", "prompt": "Create outline...", "gate": validate_outline},
        {"name": "draft", "prompt": "Write post...", "gate": validate_content},
        {"name": "edit", "prompt": "Edit...", "gate": validate_edited},
        {"name": "seo", "prompt": "SEO optimize..."}
    ]

    chain = create_prompt_chain(steps, claude_llm)
    result = await chain.run_async({"chain_output": "AI Agents"})

    print(result["chain_output"])


if __name__ == "__main__":
    # Run with mock LLM
    asyncio.run(main())

    # Uncomment to run with real LLM:
    # asyncio.run(with_real_llm())
