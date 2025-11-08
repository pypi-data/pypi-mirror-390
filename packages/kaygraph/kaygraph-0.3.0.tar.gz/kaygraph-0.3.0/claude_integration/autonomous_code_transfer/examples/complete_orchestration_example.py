#!/usr/bin/env python3
"""Complete Orchestration Example - All Droids Working Together.

This example demonstrates:
1. Multi-droid orchestration (all specialists working in parallel)
2. Competitive solutions (multiple approaches racing)
3. Complete end-to-end autonomous feature transfer

Run this to see the full power of Factory AI patterns + KayGraph!
"""

import asyncio
import logging
from pathlib import Path
import json
from datetime import datetime

from workflows.multi_droid_orchestration import (
    create_multi_droid_transfer_workflow,
    create_fast_track_workflow,
    create_security_focused_workflow
)
from workflows.competitive_orchestration import (
    create_competitive_workflow,
    create_common_competitive_workflow,
    COMPETITIVE_STRATEGIES
)
from graphs import run_transfer_workflow


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_1_multi_droid_transfer():
    """Example 1: Complete transfer with all droids working together.

    This shows the FULL power - all specialized droids reviewing in parallel:
    - Code Reviewer checks quality
    - Security Checker finds vulnerabilities
    - Test Generator fills coverage gaps

    Perfect for production-ready transfers.
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Multi-Droid Orchestration")
    print("="*80)
    print("""
This example demonstrates ALL specialized droids working together in parallel:

Workflow:
  Task Init → Research → Planning → Implementation →
    ┌─ Code Reviewer Droid    (checks code quality)
    ├─ Security Checker Droid (finds vulnerabilities)
    └─ Test Generator Droid   (generates missing tests)
      → Aggregate Results → Final Validation

The droids run in parallel for maximum speed, then results are aggregated
to provide a comprehensive assessment.

Duration: 2-4 hours depending on complexity
Cost: $10-$30
Best for: Production-ready feature transfers
""")

    # Configuration
    config = {
        "task_description": "Transfer Doppler integration from template to target",
        "source_repo": "/path/to/template-with-doppler",
        "target_repo": "/path/to/target-codebase",
        "documentation": "/path/to/doppler-docs.md",
        "mode": "autonomous",
        "max_runtime_hours": 4.0,
        "max_cost_usd": 30.0,
        # Optional monitoring
        "webhook_url": None,
        "slack_webhook": None,
        "email_config": None
    }

    # Create multi-droid workflow
    print("\n📋 Creating multi-droid workflow...")
    workflow = create_multi_droid_transfer_workflow(
        workspace_root="./tasks",
        safety_guidelines_path=Path("./safety_guidelines.md"),
        supervised=False  # Fully autonomous
    )
    print("✓ Multi-droid workflow created")

    # Run the workflow
    print("\n🚀 Starting autonomous transfer with multi-droid review...")
    print("   This will run all droids in parallel after implementation")
    print("   Check ./tasks/<task-id>/ for real-time progress\n")

    try:
        results = await run_transfer_workflow(
            workflow=workflow,
            config=config,
            max_runtime_hours=config["max_runtime_hours"],
            max_cost_usd=config["max_cost_usd"]
        )

        # Display results
        print("\n" + "="*80)
        if results["success"]:
            print("✅ MULTI-DROID TRANSFER COMPLETE!")
        else:
            print("⚠️  TRANSFER COMPLETED WITH WARNINGS")

        print(f"""
Task ID: {results.get('task_id', 'N/A')}
Duration: {results.get('duration_hours', 0):.2f} hours
Task Directory: {results.get('task_dir', 'N/A')}

Droid Review Summary:
{json.dumps(results.get('summary', {}), indent=2)}

Review Reports:
1. Code Review: tasks/{results.get('task_id')}/code_review_report.md
2. Security Scan: tasks/{results.get('task_id')}/security_report.md
3. Test Generation: tasks/{results.get('task_id')}/test_generation_report.md
4. Aggregate Review: tasks/{results.get('task_id')}/aggregate_review_report.md

Next Steps:
1. Review aggregate report for overall assessment
2. Check individual droid reports for details
3. Address any issues flagged by droids
4. Create PR for human final review
""")

        return results

    except KeyboardInterrupt:
        print("\n\n⏸️  Transfer interrupted - progress saved")
        return None


async def example_2_competitive_solutions():
    """Example 2: Competitive approaches racing to solve the problem.

    This shows multiple implementations of the same feature, each using
    a different strategy. The best one wins!

    Perfect for complex problems where the optimal approach isn't clear.
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Competitive Solution Orchestration")
    print("="*80)
    print("""
This example demonstrates competitive solutions - multiple approaches racing:

Approaches:
  1. Minimalist  → Keep it simple, minimal dependencies
  2. Robust      → Full error handling, production-ready
  3. Performant  → Optimize for speed and efficiency

All three approaches implement the same feature in parallel, then a judge
evaluates them on:
- Code Quality (25%)
- Performance (20%)
- Correctness (25%)
- Testability (15%)
- Documentation (10%)
- Innovation (5%)

The best approach wins and gets deployed!

Duration: 1-2 hours (all approaches run in parallel)
Cost: $15-$40 (3x implementation cost)
Best for: Complex problems with unclear optimal approach
""")

    # Configuration
    config = {
        "task_description": """
Implement a rate limiter for the API with these requirements:
- Support multiple strategies (token bucket, sliding window, fixed window)
- Handle distributed systems (Redis-backed)
- Provide per-user and per-endpoint limits
- Include monitoring and alerting
- Must scale to 10K requests/second
        """,
        "target_repo": "/path/to/target-codebase",
        "mode": "competitive",
        "max_runtime_hours": 2.0,
        "max_cost_usd": 40.0
    }

    # Define competitive approaches
    print("\n📋 Creating competitive workflow with 3 approaches...")

    approaches = [
        ("minimalist", COMPETITIVE_STRATEGIES["minimalist"]),
        ("robust", COMPETITIVE_STRATEGIES["robust"]),
        ("performant", COMPETITIVE_STRATEGIES["performant"])
    ]

    workflow = create_competitive_workflow(
        approaches=approaches,
        workspace_root="./tasks"
    )
    print("✓ Competitive workflow created with 3 approaches")

    # Run the competition
    print("\n🏁 Starting competitive implementation race...")
    print("   All 3 approaches will implement in parallel")
    print("   Judge will evaluate and pick the winner\n")

    try:
        results = await run_transfer_workflow(
            workflow=workflow,
            config=config,
            max_runtime_hours=config["max_runtime_hours"],
            max_cost_usd=config["max_cost_usd"]
        )

        # Display results
        print("\n" + "="*80)
        print("🏆 COMPETITIVE SOLUTIONS COMPLETE!")

        winner = results.get("competitive_winner", {})

        print(f"""
Winner: {winner.get('approach', 'N/A')}

Rationale:
{winner.get('rationale', 'N/A')}

All Implementations:
{json.dumps(results.get('competitive_implementations', {}), indent=2)}

Comparison Report:
{winner.get('comparison_path', 'N/A')}

Next Steps:
1. Review winning implementation
2. Check comparison report for detailed scoring
3. Review runner-up implementations for insights
4. Deploy winning approach
""")

        return results

    except KeyboardInterrupt:
        print("\n\n⏸️  Competition interrupted - progress saved")
        return None


async def example_3_security_focused_workflow():
    """Example 3: Security-focused transfer with enhanced security checks.

    Extra emphasis on security scanning - perfect for sensitive codebases
    like payment systems, healthcare, or financial applications.
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Security-Focused Workflow")
    print("="*80)
    print("""
This example emphasizes security above all else:

Workflow:
  Research → Planning → Implementation → **Security Scan FIRST** →
    If Critical: BLOCK DEPLOYMENT
    If Issues: Fix & Re-implement
    If Clean: Code Review → Test Gen → Deploy

Perfect for:
- Payment processing systems
- Healthcare applications
- Financial services
- User authentication systems
- Any PCI/HIPAA/SOX compliance needs

Duration: 2-5 hours
Cost: $15-$35
Best for: Security-critical feature transfers
""")

    config = {
        "task_description": "Transfer Stripe payment integration to new checkout system",
        "source_repo": "/path/to/template-with-stripe",
        "target_repo": "/path/to/checkout-system",
        "documentation": "/path/to/stripe-docs.md",
        "mode": "security_focused",
        "max_runtime_hours": 5.0,
        "max_cost_usd": 35.0
    }

    print("\n📋 Creating security-focused workflow...")
    workflow = create_security_focused_workflow(
        workspace_root="./tasks",
        safety_guidelines_path=Path("./safety_guidelines.md")
    )
    print("✓ Security-focused workflow created")

    print("\n🔒 Starting security-focused transfer...")
    print("   Security scan runs FIRST - blocks on critical issues")
    print("   Multiple security iterations if needed\n")

    try:
        results = await run_transfer_workflow(
            workflow=workflow,
            config=config,
            max_runtime_hours=config["max_runtime_hours"],
            max_cost_usd=config["max_cost_usd"]
        )

        print("\n" + "="*80)
        if results["success"]:
            print("✅ SECURITY-FOCUSED TRANSFER COMPLETE - NO CRITICAL ISSUES")
        else:
            print("⚠️  TRANSFER BLOCKED - SECURITY ISSUES FOUND")

        security_scan = results.get("security_scan", {})

        print(f"""
Security Status: {security_scan.get('risk_level', 'N/A')}
Action: {security_scan.get('action', 'N/A')}

Security Report: {security_scan.get('report_path', 'N/A')}

Next Steps:
1. Review security report thoroughly
2. Address any flagged vulnerabilities
3. Re-run if critical issues were found
4. Only deploy after security approval
""")

        return results

    except KeyboardInterrupt:
        print("\n\n⏸️  Transfer interrupted - progress saved")
        return None


async def example_4_fast_track_workflow():
    """Example 4: Fast-track workflow for simple, low-risk transfers.

    Skips some droid reviews for faster execution.
    Perfect for simple configuration changes or documentation updates.
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Fast-Track Workflow")
    print("="*80)
    print("""
This example uses a streamlined workflow for low-risk changes:

Workflow:
  Research → Planning → Implementation → Code Review → Validation

Skips:
- Security scan (low-risk change)
- Test generation (existing tests sufficient)

Perfect for:
- Configuration changes
- Documentation updates
- Simple refactoring
- Low-risk improvements

Duration: 30 minutes - 1 hour
Cost: $3-$10
Best for: Simple, low-risk transfers
""")

    config = {
        "task_description": "Update API documentation and add new examples",
        "target_repo": "/path/to/project",
        "mode": "fast_track",
        "max_runtime_hours": 1.0,
        "max_cost_usd": 10.0
    }

    print("\n📋 Creating fast-track workflow...")
    workflow = create_fast_track_workflow(
        workspace_root="./tasks",
        safety_guidelines_path=Path("./safety_guidelines.md")
    )
    print("✓ Fast-track workflow created")

    print("\n⚡ Starting fast-track transfer...")
    print("   Minimal reviews for speed\n")

    try:
        results = await run_transfer_workflow(
            workflow=workflow,
            config=config,
            max_runtime_hours=config["max_runtime_hours"],
            max_cost_usd=config["max_cost_usd"]
        )

        print("\n" + "="*80)
        print("✅ FAST-TRACK TRANSFER COMPLETE!")

        print(f"""
Duration: {results.get('duration_hours', 0):.2f} hours
Cost: ${results.get('summary', {}).get('cost_usd', 0):.2f}

Fast-track is perfect for low-risk changes!
""")

        return results

    except KeyboardInterrupt:
        print("\n\n⏸️  Transfer interrupted - progress saved")
        return None


async def run_all_examples():
    """Run all examples in sequence to demonstrate capabilities."""
    print("\n" + "="*80)
    print("COMPLETE ORCHESTRATION DEMONSTRATION")
    print("="*80)
    print("""
This will run ALL orchestration examples:

1. Multi-Droid Transfer (all specialists in parallel)
2. Competitive Solutions (multiple approaches racing)
3. Security-Focused Workflow (security-first approach)
4. Fast-Track Workflow (quick simple transfers)

This is a DEMONSTRATION - adjust paths and config for real usage.
Press Ctrl+C to skip any example.
""")

    examples = [
        ("Multi-Droid Transfer", example_1_multi_droid_transfer),
        ("Competitive Solutions", example_2_competitive_solutions),
        ("Security-Focused", example_3_security_focused_workflow),
        ("Fast-Track", example_4_fast_track_workflow)
    ]

    results = {}

    for name, example_func in examples:
        try:
            print(f"\n\n{'='*80}")
            print(f"Running: {name}")
            print('='*80)

            input(f"\nPress Enter to start {name} example (or Ctrl+C to skip)...")

            result = await example_func()
            results[name] = result

        except KeyboardInterrupt:
            print(f"\n⏭️  Skipping {name}")
            continue

    print("\n\n" + "="*80)
    print("ALL EXAMPLES COMPLETE")
    print("="*80)

    print("\nSummary:")
    for name, result in results.items():
        if result:
            print(f"✓ {name}: {'Success' if result.get('success') else 'Completed with warnings'}")
        else:
            print(f"⏭️  {name}: Skipped")


def main():
    """Main entry point."""
    import sys

    if len(sys.argv) < 2:
        print("\nUsage: python complete_orchestration_example.py <example>")
        print("\nExamples:")
        print("  1  - Multi-droid transfer (all specialists)")
        print("  2  - Competitive solutions (multiple approaches)")
        print("  3  - Security-focused workflow")
        print("  4  - Fast-track workflow")
        print("  all - Run all examples in sequence")
        return

    example = sys.argv[1]

    if example == "1":
        asyncio.run(example_1_multi_droid_transfer())
    elif example == "2":
        asyncio.run(example_2_competitive_solutions())
    elif example == "3":
        asyncio.run(example_3_security_focused_workflow())
    elif example == "4":
        asyncio.run(example_4_fast_track_workflow())
    elif example == "all":
        asyncio.run(run_all_examples())
    else:
        print(f"Unknown example: {example}")
        print("Use: 1, 2, 3, 4, or all")


if __name__ == "__main__":
    main()
