"""
Example 7: Combined Patterns (Production Content System)

This example shows how to combine multiple patterns for a real-world system:
- ROUTING: Classify content type
- PROMPT CHAINING: Multi-step content generation
- PARALLEL SECTIONING: Quality validation
- EVALUATOR-OPTIMIZER: Refinement for premium content
- REACT AGENT: Handle complex requests

Real-world scenario: Content generation platform that:
1. Routes different content types to specialized pipelines
2. Uses chaining for standard content
3. Uses eval-optimize for premium content
4. Validates with parallel checks
5. Falls back to agent for complex requests
"""

import asyncio
from kaygraph import AsyncNode, AsyncGraph, AsyncInteractiveGraph
from kaygraph.agent import (
    create_router,
    create_prompt_chain,
    run_parallel_sectioning,
    create_react_agent,
    ToolRegistry
)


# =============================================================================
# STEP 1: ROUTING (Content Type Classification)
# =============================================================================

class BlogPipeline(AsyncNode):
    """Handles blog post generation"""
    async def exec_async(self, prep_res):
        print("\n→ Routing to: BLOG PIPELINE")
        return await generate_blog(prep_res["topic"])


class SocialPipeline(AsyncNode):
    """Handles social media content"""
    async def exec_async(self, prep_res):
        print("\n→ Routing to: SOCIAL MEDIA PIPELINE")
        return await generate_social(prep_res["topic"])


class ComplexPipeline(AsyncNode):
    """Handles complex requests with agent"""
    async def exec_async(self, prep_res):
        print("\n→ Routing to: COMPLEX REQUEST HANDLER (ReAct Agent)")
        return await handle_complex_request(prep_res["topic"])


# =============================================================================
# STEP 2: PROMPT CHAINING (Blog Generation)
# =============================================================================

async def generate_blog(topic: str) -> dict:
    """Generate blog post using prompt chaining"""
    print("  [Chain Step 1/3] Researching...")

    async def mock_llm(messages):
        content = messages[-1]["content"] if messages else ""
        if "research" in content.lower():
            return {"content": f"Research findings on {topic}: Key points A, B, C"}
        elif "draft" in content.lower():
            return {"content": f"Draft blog post about {topic} (500 words)"}
        else:
            return {"content": f"Final polished blog post on {topic}"}

    steps = [
        {"name": "research", "prompt": f"Research {topic}"},
        {"name": "draft", "prompt": "Write draft"},
        {"name": "polish", "prompt": "Polish and edit"}
    ]

    chain = create_prompt_chain(steps, mock_llm)
    result = await chain.run_async({"chain_output": topic})

    print("  ✓ Blog generation complete")
    return {"content": result["chain_output"], "type": "blog"}


# =============================================================================
# STEP 3: PARALLEL VALIDATION (Quality Checks)
# =============================================================================

async def validate_content(content: str) -> dict:
    """Run parallel quality checks"""
    print("\n  → Running parallel validation checks...")

    async def mock_llm(messages):
        system = messages[0]["content"] if messages else ""
        if "seo" in system.lower():
            return {"content": "✓ SEO score: 85/100"}
        elif "readability" in system.lower():
            return {"content": "✓ Readability: Grade 8"}
        else:
            return {"content": "✓ Check passed"}

    checks = [
        {"system": "Check SEO optimization", "input": content},
        {"system": "Check readability", "input": content},
        {"system": "Check tone consistency", "input": content}
    ]

    results = await run_parallel_sectioning(mock_llm, checks)

    print(f"  ✓ Completed {len(results)} validation checks")
    return {"validation_results": results, "passed": True}


# =============================================================================
# STEP 4: SOCIAL MEDIA (Shorter Pipeline)
# =============================================================================

async def generate_social(topic: str) -> dict:
    """Generate social media content (simpler pipeline)"""
    print("  [Social] Generating post...")
    content = f"🚀 Check out: {topic}\n\n#AI #Tech #Innovation"
    print("  ✓ Social content generated")
    return {"content": content, "type": "social"}


# =============================================================================
# STEP 5: COMPLEX HANDLER (ReAct Agent)
# =============================================================================

async def handle_complex_request(topic: str) -> dict:
    """Use ReAct agent for complex requests"""
    print("  [Agent] Processing complex request...")

    def research_tool(query: str) -> str:
        return f"Research results for: {query}"

    async def mock_llm(messages):
        return {"content": '{"action": "finish", "answer": "Complex task completed"}'}

    registry = ToolRegistry()
    registry.register_function("research", research_tool, "Research information")

    agent = create_react_agent(registry, mock_llm)
    result = await agent.run_interactive_async(
        {"messages": [{"role": "user", "content": topic}]},
        max_iterations=5
    )

    print("  ✓ Complex request handled")
    return {"content": result.get("final_answer"), "type": "complex"}


# =============================================================================
# MAIN ORCHESTRATION SYSTEM
# =============================================================================

async def content_generation_system(user_request: str):
    """
    Complete content generation system combining all patterns
    """
    print("=" * 70)
    print("PRODUCTION CONTENT GENERATION SYSTEM")
    print("=" * 70)
    print()
    print(f"User Request: {user_request}")
    print()

    # STEP 1: ROUTING - Classify content type
    print("STEP 1: CONTENT CLASSIFICATION")
    print("-" * 70)

    async def classifier_llm(messages):
        content = messages[-1]["content"] if messages else ""
        if "blog" in content.lower() or "article" in content.lower():
            return {"content": "blog"}
        elif "tweet" in content.lower() or "social" in content.lower():
            return {"content": "social"}
        else:
            return {"content": "complex"}

    router = create_router(classifier_llm, {
        "blog": BlogPipeline(),
        "social": SocialPipeline(),
        "complex": ComplexPipeline()
    })

    # Route the request
    result = await router.run_async({"user_input": user_request, "topic": user_request})
    content_type = result.get("type", "unknown")

    # STEP 2: VALIDATION (for blog posts)
    if content_type == "blog":
        print("\nSTEP 2: QUALITY VALIDATION")
        print("-" * 70)
        validation = await validate_content(result["content"])
        result["validation"] = validation

    # STEP 3: RESULTS
    print("\n" + "=" * 70)
    print("FINAL OUTPUT")
    print("=" * 70)
    print()
    print(f"Content Type: {content_type.upper()}")
    print(f"Content: {result['content'][:200]}...")
    if "validation" in result:
        print(f"Quality Checks: {len(result['validation']['validation_results'])} passed")
    print()

    return result


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

async def main():
    """Run different scenarios"""

    # Scenario 1: Blog post (uses chaining + validation)
    await content_generation_system("Write a blog article about AI agents")

    print("\n" + "=" * 70)
    print()

    # Scenario 2: Social media (simple pipeline)
    await content_generation_system("Create a tweet about machine learning")

    print("\n" + "=" * 70)
    print()

    # Scenario 3: Complex request (uses agent)
    await content_generation_system("Analyze trends and create a comprehensive report")


# =============================================================================
# ARCHITECTURE OVERVIEW
# =============================================================================

def show_architecture():
    print("\n" + "=" * 70)
    print("SYSTEM ARCHITECTURE")
    print("=" * 70)
    print()
    print("""
User Request
     │
     ▼
┌────────────────┐
│    ROUTER      │  ← Pattern 1: Routing
│  (Classify)    │
└────┬───────────┘
     │
     ├─→ Blog ──────┐
     │              ▼
     │         ┌──────────────┐
     │         │ PROMPT CHAIN │  ← Pattern 2: Chaining
     │         │ Research      │
     │         │   ↓ Draft     │
     │         │   ↓ Polish    │
     │         └──────┬───────┘
     │                │
     │                ▼
     │         ┌──────────────┐
     │         │  PARALLEL    │  ← Pattern 3: Parallelization
     │         │  Validate × 3│
     │         └──────────────┘
     │
     ├─→ Social → [Quick Generate]
     │
     └─→ Complex ──┐
                   ▼
            ┌──────────────┐
            │ REACT AGENT  │  ← Pattern 4: Agent
            │ Think→Act    │
            └──────────────┘

Each pattern used where it makes most sense!
    """)


if __name__ == "__main__":
    asyncio.run(main())
    show_architecture()
