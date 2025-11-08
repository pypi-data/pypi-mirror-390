"""
Example 4: Parallel Workflows (Content Validation & Code Review)

This example shows two parallelization patterns:
1. Sectioning - Multiple independent checks run simultaneously
2. Voting - Same check repeated multiple times for consensus

Pattern A (Sectioning): Check1 + Check2 + Check3 → Combine results
Pattern B (Voting): Check × 5 → Consensus
"""

import asyncio
from kaygraph.agent import run_parallel_sectioning, run_parallel_voting


# =============================================================================
# MOCK LLM
# =============================================================================

check_counter = {"count": 0}


async def mock_llm(messages):
    """Mock LLM with different responses"""
    check_counter["count"] += 1

    system_prompt = ""
    user_content = ""
    for msg in messages:
        if msg["role"] == "system":
            system_prompt = msg["content"].lower()
        if msg["role"] == "user":
            user_content = msg["content"]

    # Return different responses based on check type
    if "bias" in system_prompt:
        return {"content": "✓ No bias detected. Language is neutral and inclusive."}
    elif "fact" in system_prompt:
        return {"content": "⚠️  Found 1 potential factual issue: The claim about '100%' should be verified."}
    elif "tone" in system_prompt:
        return {"content": "✓ Tone is professional and appropriate for business communication."}
    elif "spam" in system_prompt:
        return {"content": "✓ No spam or promotional content detected."}
    elif "security" in system_prompt:
        # For voting - vary the responses
        issues = [
            "🔴 CRITICAL: SQL injection vulnerability on line 15",
            "🔴 CRITICAL: SQL injection found in database query",
            "🟡 WARNING: Potential SQL injection risk detected",
            "🔴 HIGH: Unsafe database query, risk of SQL injection",
            "🔴 CRITICAL: Security vulnerability - SQL injection possible"
        ]
        return {"content": issues[check_counter["count"] % len(issues)]}
    else:
        return {"content": "Analysis complete."}


# =============================================================================
# EXAMPLE 1: PARALLEL SECTIONING (Content Validation)
# =============================================================================

async def content_validation_example():
    """Run multiple independent validation checks in parallel"""
    print("=" * 70)
    print("Example 1: Parallel Sectioning - Content Validation")
    print("=" * 70)
    print()

    # Content to validate
    content = """Our new AI platform delivers 100% accuracy in predictions
and will revolutionize your business operations. Sign up now for exclusive
early access and transform your workflow today!"""

    print("Content to validate:")
    print("-" * 70)
    print(content)
    print()

    # Define independent validation checks
    validation_tasks = [
        {
            "system": "Check for bias, discrimination, or inappropriate language",
            "input": content
        },
        {
            "system": "Check for factual accuracy and verify claims",
            "input": content
        },
        {
            "system": "Analyze tone and professionalism",
            "input": content
        },
        {
            "system": "Check for spam or excessive promotional language",
            "input": content
        }
    ]

    print(f"Running {len(validation_tasks)} validation checks in parallel...")
    print()

    # Run all checks simultaneously
    results = await run_parallel_sectioning(mock_llm, validation_tasks)

    # Display results
    print("Validation Results:")
    print("=" * 70)

    check_names = ["Bias Check", "Fact Check", "Tone Check", "Spam Check"]
    for name, result in zip(check_names, results):
        print(f"{name}:")
        print(f"  {result['content']}")
        print()

    # Aggregate results
    issues = sum(1 for r in results if "⚠️" in r["content"] or "🔴" in r["content"])
    print(f"Summary: {issues} issues found out of {len(results)} checks")
    print()


# =============================================================================
# EXAMPLE 2: PARALLEL VOTING (Code Review)
# =============================================================================

async def code_review_example():
    """Run same review multiple times and get consensus"""
    print("=" * 70)
    print("Example 2: Parallel Voting - Code Review Consensus")
    print("=" * 70)
    print()

    # Code to review
    code = """
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = " + str(user_id)
    return db.execute(query)
"""

    print("Code to review:")
    print("-" * 70)
    print(code)
    print()

    # Define review task
    review_task = {
        "system": "Review this code for security vulnerabilities. Be specific about issues and severity.",
        "input": code
    }

    num_reviews = 5
    print(f"Running {num_reviews} independent security reviews...")
    print()

    # Run multiple reviews in parallel
    result = await run_parallel_voting(mock_llm, review_task, num_samples=num_reviews)

    # Display all reviews
    print("Individual Reviews:")
    print("=" * 70)
    for i, review in enumerate(result["samples"], 1):
        print(f"Review #{i}: {review['content']}")
        print()

    # Analyze consensus
    print("Consensus Analysis:")
    print("-" * 70)

    # Count issues mentioned
    sql_injection_mentions = sum(1 for r in result["samples"] if "sql injection" in r["content"].lower())
    critical_severity = sum(1 for r in result["samples"] if "CRITICAL" in r["content"] or "HIGH" in r["content"])

    print(f"SQL Injection mentioned: {sql_injection_mentions}/{num_reviews} reviews")
    print(f"Critical/High severity: {critical_severity}/{num_reviews} reviews")
    print()

    if sql_injection_mentions >= 3:
        print("✓ CONSENSUS: SQL injection vulnerability confirmed")
        print("  Confidence: HIGH")
    else:
        print("⚠️  No consensus reached")
        print(f"  Confidence: LOW ({sql_injection_mentions}/{num_reviews})")
    print()


# =============================================================================
# EXAMPLE 3: REAL-WORLD USE CASE (Combined)
# =============================================================================

async def combined_example():
    """Combine both patterns for comprehensive validation"""
    print("=" * 70)
    print("Example 3: Combined - Comprehensive Content Review")
    print("=" * 70)
    print()

    content = "AI content to review..."

    print("Phase 1: Parallel Sectioning (Different Checks)")
    # Run different checks
    tasks = [
        {"system": "Check grammar", "input": content},
        {"system": "Check facts", "input": content},
        {"system": "Check tone", "input": content}
    ]
    section_results = await run_parallel_sectioning(mock_llm, tasks)
    print(f"✓ Completed {len(section_results)} different checks")
    print()

    print("Phase 2: Parallel Voting (Consensus on Quality)")
    # Get consensus on overall quality
    quality_task = {"system": "Rate overall quality 1-10", "input": content}
    voting_results = await run_parallel_voting(mock_llm, quality_task, num_samples=5)
    print(f"✓ Got {voting_results['count']} independent quality ratings")
    print()

    print("Final Decision: Approved with minor revisions")


# =============================================================================
# PRACTICAL TIPS
# =============================================================================

def show_tips():
    print()
    print("=" * 70)
    print("Practical Tips for Parallel Workflows")
    print("=" * 70)
    print()
    print("SECTIONING - Use when:")
    print("  ✓ Tasks are independent")
    print("  ✓ Need different analyses (bias, facts, tone)")
    print("  ✓ Want to save time on multi-aspect checks")
    print()
    print("VOTING - Use when:")
    print("  ✓ Need consensus or confidence level")
    print("  ✓ Reducing single-run errors matters")
    print("  ✓ Examples: code review, content moderation, quality assessment")
    print()
    print("COST CONSIDERATION:")
    print("  - Sectioning: N different tasks = N × cost")
    print("  - Voting: Same task × N samples = N × cost")
    print("  - Trade latency & cost for better results")
    print()


# =============================================================================
# RUN EXAMPLES
# =============================================================================

async def main():
    # Run sectioning example
    await content_validation_example()

    # Run voting example
    await code_review_example()

    # Run combined example
    # await combined_example()

    # Show tips
    show_tips()


if __name__ == "__main__":
    asyncio.run(main())
