#!/usr/bin/env python3
"""Autonomous Code Transfer Agent - Main Entry Point.

Usage:
    python main.py --example doppler_transfer
    python main.py --example generic_transfer
    python main.py --config config.json
"""

import asyncio
import argparse
import json
import logging
from pathlib import Path
import sys

from graphs import (
    create_doppler_transfer_workflow,
    create_generic_feature_transfer_workflow,
    run_transfer_workflow
)
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


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_doppler_transfer():
    """Example 1: Transfer Doppler integration from template to target."""
    print("\n" + "="*80)
    print("Example 1: Doppler Integration Transfer")
    print("="*80)
    print("""
This example demonstrates autonomous transfer of Doppler integration
from a FastAPI + React template to a new codebase.

Setup:
1. Source codebase with Doppler integration at: ./examples/doppler_transfer/source/
2. Target codebase without Doppler at: ./examples/doppler_transfer/target/
3. Documentation at: ./examples/doppler_transfer/source_docs.md

The agent will:
- Research both codebases
- Create detailed plan
- Execute transfer step-by-step
- Validate with tests
- Run autonomously (can take 1-3 hours)
""")

    # Configuration
    config = {
        "source_repo": str(Path("./examples/doppler_transfer/source").absolute()),
        "target_repo": str(Path("./examples/doppler_transfer/target").absolute()),
        "documentation": str(Path("./examples/doppler_transfer/source_docs.md").absolute()),
        "mode": "autonomous",  # or "supervised" for human checkpoints
        "webhook_url": None,  # Optional: "https://your-webhook.com/notify"
        "slack_webhook": None,  # Optional: Slack webhook URL
        "email_config": None  # Optional: Email configuration
    }

    # Create workflow
    workflow = create_doppler_transfer_workflow(
        config=config,
        workspace_root="./tasks",
        safety_guidelines_path=Path("./safety_guidelines.md")
    )

    # Run with limits
    print("\n🚀 Starting autonomous transfer...")
    print("   This will run unattended - check ./tasks/ for progress")
    print("   Press Ctrl+C to interrupt\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=8.0,  # Timeout after 8 hours
        max_cost_usd=50.0  # Stop if cost exceeds $50
    )

    # Print results
    print("\n" + "="*80)
    if results["success"]:
        print("✅ TRANSFER COMPLETE!")
    else:
        print("❌ TRANSFER FAILED")

    print(f"""
Task ID: {results.get('task_id', 'N/A')}
Duration: {results.get('duration_hours', 0):.2f} hours
Task Directory: {results.get('task_dir', 'N/A')}

Summary:
{json.dumps(results.get('summary', {}), indent=2)}

Next steps:
1. Review task directory for complete logs
2. Review code changes in target repository
3. Run tests manually if needed
4. Create PR for human review
""")

    return results


async def example_generic_transfer():
    """Example 2: Transfer any feature with configuration."""
    print("\n" + "="*80)
    print("Example 2: Generic Feature Transfer")
    print("="*80)
    print("""
This example shows how to transfer ANY feature between codebases
by providing appropriate configuration.

You can adapt this for:
- Authentication systems (Auth0, JWT, OAuth)
- Payment integrations (Stripe, PayPal)
- Analytics (Google Analytics, Mixpanel)
- Database integrations (Redis, MongoDB)
- Any other feature with documentation
""")

    # Configuration
    feature_name = "authentication-jwt"
    config = {
        "source_repo": "/path/to/source/codebase",
        "target_repo": "/path/to/target/codebase",
        "documentation": "/path/to/auth-docs.md",
        "mode": "supervised",  # Human approval after each phase
        "custom_prompts": {
            "research": "Focus on JWT token handling, refresh logic, and middleware",
            "planning": "Ensure backward compatibility with existing auth",
            "implementation": "Prioritize security best practices"
        }
    }

    print(f"\n📝 Transferring feature: {feature_name}")
    print("   Mode: Supervised (will pause for approval)")

    workflow = create_generic_feature_transfer_workflow(
        feature_name=feature_name,
        config=config,
        workspace_root="./tasks"
    )

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=6.0,
        max_cost_usd=30.0
    )

    print(f"\n{'✅ Complete' if results['success'] else '❌ Failed'}: {results.get('task_id')}")
    return results


async def example_supervised_mode():
    """Example 3: Supervised mode with human checkpoints."""
    print("\n" + "="*80)
    print("Example 3: Supervised Transfer with Human Approval")
    print("="*80)
    print("""
In supervised mode, the agent will:
1. Complete research → Pause for approval
2. Complete planning → Pause for approval
3. Execute each step → Continue automatically
4. Complete validation → Final report

This gives you control while maintaining automation.
""")

    config = {
        "source_repo": "./examples/doppler_transfer/source",
        "target_repo": "./examples/doppler_transfer/target",
        "documentation": "./examples/doppler_transfer/source_docs.md",
        "mode": "supervised",
        "supervised": True  # Enable human checkpoints
    }

    workflow = create_doppler_transfer_workflow(config=config)

    print("\n⏸️  Agent will pause after each major phase for your approval")
    print("   Review output in ./tasks/<task-id>/ directory")
    print("   Approve to continue or modify plan manually\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=8.0,
        max_cost_usd=50.0
    )

    return results


async def example_multi_droid_orchestration():
    """Example 4: Multi-droid orchestration with all specialists."""
    print("\n" + "="*80)
    print("Example 4: Multi-Droid Orchestration")
    print("="*80)
    print("""
This example shows ALL specialized droids working together in parallel:

After implementation, THREE droids review simultaneously:
- Code Reviewer Droid: Checks code quality, correctness, best practices
- Security Checker Droid: Scans for OWASP Top 10 vulnerabilities
- Test Generator Droid: Generates comprehensive test suites

Results are aggregated and scored to provide final recommendation.

Duration: 2-4 hours
Cost: $10-$30
Best for: Production-ready transfers
""")

    config = {
        "source_repo": "/path/to/source",
        "target_repo": "/path/to/target",
        "documentation": "/path/to/docs.md",
        "mode": "multi_droid",
        "max_runtime_hours": 4.0,
        "max_cost_usd": 30.0
    }

    workflow = create_multi_droid_transfer_workflow(
        workspace_root="./tasks",
        safety_guidelines_path=Path("./safety_guidelines.md")
    )

    print("\n🚀 Starting multi-droid transfer...")
    print("   All droids will run in parallel after implementation\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=4.0,
        max_cost_usd=30.0
    )

    if results.get("aggregate_review"):
        agg = results["aggregate_review"]
        print(f"\n✅ Multi-Droid Review Complete!")
        print(f"   Overall Score: {agg['overall_score']:.1f}/100")
        print(f"   Recommendation: {agg['recommendation']}")
        print(f"   Report: {agg['report_path']}")

    return results


async def example_competitive_solutions():
    """Example 5: Competitive solutions - multiple approaches racing."""
    print("\n" + "="*80)
    print("Example 5: Competitive Solutions")
    print("="*80)
    print("""
This example demonstrates competitive orchestration where multiple
approaches implement the same feature in parallel, then a judge picks
the best one!

Approaches racing:
1. Minimalist - Simple, minimal dependencies
2. Robust - Full error handling, production-ready
3. Performant - Optimized for speed

Judge evaluates on:
- Code Quality (25%)
- Performance (20%)
- Correctness (25%)
- Testability (15%)
- Documentation (10%)
- Innovation (5%)

Duration: 1-2 hours (parallel execution)
Cost: $15-$40 (3x implementations)
Best for: Complex problems with unclear optimal approach
""")

    config = {
        "task_description": "Implement a rate limiter with Redis backend",
        "target_repo": "/path/to/target",
        "mode": "competitive",
        "max_runtime_hours": 2.0,
        "max_cost_usd": 40.0
    }

    workflow = create_common_competitive_workflow(
        workspace_root="./tasks",
        include_approaches=['minimalist', 'robust', 'performant']
    )

    print("\n🏁 Starting competitive implementation race...")
    print("   3 approaches will implement in parallel\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=2.0,
        max_cost_usd=40.0
    )

    if results.get("competitive_winner"):
        winner = results["competitive_winner"]
        print(f"\n🏆 Winner: {winner['approach']}")
        print(f"   Rationale: {winner['rationale'][:200]}...")
        print(f"   Comparison: {winner['comparison_path']}")

    return results


async def example_security_focused():
    """Example 6: Security-focused workflow with enhanced checks."""
    print("\n" + "="*80)
    print("Example 6: Security-Focused Workflow")
    print("="*80)
    print("""
This example prioritizes security above all else.

Security scan runs FIRST after implementation:
- If CRITICAL: Block deployment immediately
- If HIGH/MEDIUM: Fix issues and re-implement
- If LOW: Continue to other reviews

Perfect for:
- Payment systems
- Healthcare applications
- Financial services
- Authentication systems

Duration: 2-5 hours
Cost: $15-$35
Best for: Security-critical transfers
""")

    config = {
        "source_repo": "/path/to/secure-source",
        "target_repo": "/path/to/target",
        "documentation": "/path/to/security-docs.md",
        "mode": "security_focused",
        "max_runtime_hours": 5.0,
        "max_cost_usd": 35.0
    }

    workflow = create_security_focused_workflow(
        workspace_root="./tasks",
        safety_guidelines_path=Path("./safety_guidelines.md")
    )

    print("\n🔒 Starting security-focused transfer...\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=5.0,
        max_cost_usd=35.0
    )

    if results.get("security_scan"):
        sec = results["security_scan"]
        print(f"\n🔒 Security Status: {sec['risk_level']}")
        print(f"   Action: {sec['action']}")
        print(f"   Report: {sec['report_path']}")

    return results


async def example_fast_track():
    """Example 7: Fast-track for simple, low-risk transfers."""
    print("\n" + "="*80)
    print("Example 7: Fast-Track Workflow")
    print("="*80)
    print("""
Streamlined workflow for simple, low-risk changes.

Skips:
- Security scan (low-risk)
- Test generation (existing tests OK)

Perfect for:
- Configuration changes
- Documentation updates
- Simple refactoring

Duration: 30min - 1 hour
Cost: $3-$10
Best for: Quick, simple transfers
""")

    config = {
        "target_repo": "/path/to/target",
        "mode": "fast_track",
        "max_runtime_hours": 1.0,
        "max_cost_usd": 10.0
    }

    workflow = create_fast_track_workflow(
        workspace_root="./tasks"
    )

    print("\n⚡ Starting fast-track transfer...\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=1.0,
        max_cost_usd=10.0
    )

    print(f"\n✅ Fast-track complete in {results.get('duration_hours', 0):.2f}h")

    return results


async def run_from_config(config_path: Path):
    """Run transfer from JSON configuration file."""
    print(f"\n📄 Loading configuration from: {config_path}")

    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = json.load(f)

    print(f"✓ Configuration loaded")
    print(f"  Feature: {config.get('feature_name', 'N/A')}")
    print(f"  Source: {config.get('source_repo', 'N/A')}")
    print(f"  Target: {config.get('target_repo', 'N/A')}")

    # Determine workflow type
    feature_name = config.get("feature_name", "feature-transfer")

    if feature_name == "doppler-integration":
        workflow = create_doppler_transfer_workflow(config=config)
    else:
        workflow = create_generic_feature_transfer_workflow(
            feature_name=feature_name,
            config=config
        )

    print(f"\n🚀 Starting transfer for: {feature_name}\n")

    results = await run_transfer_workflow(
        workflow=workflow,
        config=config,
        max_runtime_hours=config.get("max_runtime_hours", 8.0),
        max_cost_usd=config.get("max_cost_usd", 50.0)
    )

    print(f"\n{'✅' if results['success'] else '❌'} Transfer complete!")
    print(f"Task ID: {results.get('task_id')}")
    print(f"Duration: {results.get('duration_hours', 0):.2f}h")
    print(f"Task Directory: {results.get('task_dir')}")

    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Code Transfer Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run Doppler transfer example
  python main.py --example doppler_transfer

  # Run generic feature transfer
  python main.py --example generic_transfer

  # Run supervised mode
  python main.py --example supervised_mode

  # Run from configuration file
  python main.py --config ./examples/doppler_transfer/transfer_config.json

  # List available examples
  python main.py --list-examples
        """
    )

    parser.add_argument(
        "--example",
        choices=[
            "doppler_transfer",
            "generic_transfer",
            "supervised_mode",
            "multi_droid",
            "competitive",
            "security_focused",
            "fast_track"
        ],
        help="Run a specific example"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to JSON configuration file"
    )

    parser.add_argument(
        "--list-examples",
        action="store_true",
        help="List available examples"
    )

    args = parser.parse_args()

    if args.list_examples:
        print("\nAvailable Examples:")
        print("\n  Basic Transfers:")
        print("    doppler_transfer    - Transfer Doppler integration (autonomous)")
        print("    generic_transfer    - Transfer any feature with config")
        print("    supervised_mode     - Transfer with human approval checkpoints")
        print("\n  Advanced Orchestration:")
        print("    multi_droid         - All droids working in parallel (Factory AI pattern)")
        print("    competitive         - Multiple approaches racing, judge picks best")
        print("    security_focused    - Security-first workflow for sensitive code")
        print("    fast_track          - Quick workflow for low-risk changes")
        print("\nSee examples/ directory for configuration templates")
        print("See workflows/ directory for orchestration patterns")
        return

    if not args.example and not args.config:
        parser.print_help()
        return

    # Run selected example or config
    try:
        if args.example:
            example_map = {
                "doppler_transfer": example_doppler_transfer,
                "generic_transfer": example_generic_transfer,
                "supervised_mode": example_supervised_mode,
                "multi_droid": example_multi_droid_orchestration,
                "competitive": example_competitive_solutions,
                "security_focused": example_security_focused,
                "fast_track": example_fast_track
            }
            asyncio.run(example_map[args.example]())
        elif args.config:
            asyncio.run(run_from_config(args.config))

    except KeyboardInterrupt:
        print("\n\n⏸️  Transfer interrupted by user")
        print("   Task progress saved in ./tasks/ directory")
        print("   Resume by checking task ID and running from checkpoint")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Transfer failed with exception: {e}", exc_info=True)
        print(f"\n❌ Transfer failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
