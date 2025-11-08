"""
Configuration-Driven Workflow Example

Demonstrates building workflows entirely from configuration files,
showing how behavior can be modified without changing code.
"""

import sys
import logging

# Add the utils directory to path
sys.path.insert(0, '.')

from kaygraph import Graph
from utils import load_config, call_llm
from nodes import create_node_from_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_workflow_from_config(config_path: str) -> Graph:
    """
    Build a complete workflow from a configuration file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Constructed KayGraph workflow
    """
    print(f"🔧 Building workflow from: {config_path}")

    # Load configuration
    config = load_config(config_path)

    # Extract workflow information
    workflow_info = config.get("workflow", {})
    concepts = config.get("concepts", {})
    nodes_config = config.get("nodes", {})

    print(f"   Workflow: {workflow_info.get('name')}")
    print(f"   Description: {workflow_info.get('description')}")
    print(f"   Concepts: {len(concepts)}")
    print(f"   Nodes: {len(nodes_config)}")
    print()

    # Create nodes from configuration
    created_nodes = {}

    for node_name, node_config in nodes_config.items():
        try:
            # Convert config node to KayGraph node
            node_config["node_id"] = node_name
            node = create_node_from_config(node_config)
            created_nodes[node_name] = node
            print(f"   ✅ Created node: {node_name}")
        except Exception as e:
            print(f"   ❌ Failed to create node {node_name}: {e}")
            continue

    print()

    # Build workflow connections
    # For this example, we'll create a simple linear workflow
    workflow_nodes = list(created_nodes.values())

    if len(workflow_nodes) == 0:
        raise ValueError("No valid nodes created from configuration")

    # Connect nodes in sequence
    for i in range(len(workflow_nodes) - 1):
        workflow_nodes[i] >> workflow_nodes[i + 1]
        print(f"   🔗 Connected: {workflow_nodes[i].node_id} → {workflow_nodes[i + 1].node_id}")

    print()

    # Create and return graph
    return Graph(start=workflow_nodes[0])


def run_sentiment_analysis_example():
    """Run sentiment analysis using TOML configuration."""
    print("=" * 60)
    print("😊 SENTIMENT ANALYSIS WORKFLOW (TOML)")
    print("=" * 60)

    try:
        # Build workflow from TOML config
        workflow = build_workflow_from_config("configs/workflow.toml")

        # Test data
        test_texts = [
            "I absolutely love this product! It's amazing and works perfectly!",
            "This is terrible. Complete waste of money and doesn't work at all.",
            "It's okay, nothing special but does what it's supposed to do.",
            "Outstanding quality and excellent customer service!",
            "Disappointed with the purchase. Expected much better quality."
        ]

        print("🚀 Running sentiment analysis workflow:")
        print()

        for i, text in enumerate(test_texts, 1):
            print(f"📝 Test {i}: {text}")
            print("-" * 50)

            # Initialize shared state
            shared = {
                "text": text,
                "timestamp": "2025-01-15T10:30:00Z"
            }

            try:
                # Run workflow
                workflow.run(shared)

                # Show results
                if "sentiment" in shared:
                    print(f"✅ Sentiment: {shared['sentiment']}")
                if "confidence" in shared:
                    print(f"📊 Confidence: {shared['confidence']}")
                if "reasoning" in shared:
                    print(f"💭 Reasoning: {shared['reasoning']}")
                if "is_valid" in shared:
                    validation_status = "✅ Valid" if shared["is_valid"] else "❌ Invalid"
                    print(f"🔍 Validation: {validation_status}")

            except Exception as e:
                print(f"❌ Workflow failed: {e}")
                logger.error(f"Workflow execution error: {e}")

            print()

    except Exception as e:
        print(f"❌ Failed to build workflow: {e}")
        logger.error(f"Workflow building error: {e}")


def run_resume_analysis_example():
    """Run resume-job matching using YAML configuration."""
    print("=" * 60)
    print("📄 RESUME-JOB MATCHING WORKFLOW (YAML)")
    print("=" * 60)

    try:
        # Build workflow from YAML config
        workflow = build_workflow_from_config("configs/resume_workflow.yaml")

        # Test data
        test_resumes = [
            {
                "resume_text": """
                Name: Jane Smith
                Experience: Senior Software Engineer with 8 years of experience in Python, Django, and machine learning. Led team of 5 developers.
                Skills: Python, Django, PostgreSQL, Machine Learning, Team Leadership
                Education: BS Computer Science from Stanford University
                """,
                "job_text": """
                Position: Senior Python Developer
                Requirements: 5+ years Python experience, web development, database knowledge
                Qualifications: Experience with Django framework preferred, leadership experience a plus
                Company: TechCorp Inc
                """
            },
            {
                "resume_text": """
                Name: John Doe
                Experience: Junior developer with 2 years of basic web development experience
                Skills: HTML, CSS, basic JavaScript
                Education: Associate's degree in Web Development
                """,
                "job_text": """
                Position: Senior Python Developer
                Requirements: 5+ years Python experience, web development, database knowledge
                Qualifications: Experience with Django framework preferred, leadership experience a plus
                Company: TechCorp Inc
                """
            }
        ]

        print("🚀 Running resume-job matching workflow:")
        print()

        for i, test_case in enumerate(test_resumes, 1):
            print(f"📋 Test Case {i}:")
            print("-" * 50)

            # Initialize shared state
            shared = {
                "resume_text": test_case["resume_text"],
                "job_text": test_case["job_text"],
                "current_date": "2025-01-15"
            }

            try:
                # Run workflow
                workflow.run(shared)

                # Show results
                if "analysis" in shared:
                    analysis = shared["analysis"]
                    if isinstance(analysis, dict):
                        print(f"📊 Overall Score: {analysis.get('overall_score', 'N/A')}")
                        print(f"💪 Strengths: {analysis.get('strengths', 'N/A')}")
                        print(f"🔍 Gaps: {analysis.get('gaps', 'N/A')}")
                        print(f"🎯 Recommendation: {analysis.get('recommendation', 'N/A')}")
                        if "key_matches" in analysis:
                            print(f"🔑 Key Matches: {analysis['key_matches']}")

                if "final_result" in shared:
                    final_result = shared["final_result"]
                    if isinstance(final_result, dict):
                        print(f"📈 Category: {final_result.get('category', 'N/A')}")
                        print(f"💬 Message: {final_result.get('message', 'N/A')}")
                        print(f"➡️ Next Steps: {final_result.get('next_steps', 'N/A')}")

            except Exception as e:
                print(f"❌ Workflow failed: {e}")
                logger.error(f"Workflow execution error: {e}")

            print()

    except Exception as e:
        print(f"❌ Failed to build workflow: {e}")
        logger.error(f"Workflow building error: {e}")


def demonstrate_config_modification():
    """
    Demonstrate how modifying configuration changes workflow behavior
    without touching any code.
    """
    print("=" * 60)
    print("🔧 CONFIGURATION MODIFICATION DEMO")
    print("=" * 60)

    # Load original config
    original_config = load_config("configs/workflow.toml")

    print("📋 Original Configuration:")
    print(f"   Model: {original_config['nodes']['analyzer']['params']['model']}")
    print(f"   Temperature: {original_config['nodes']['analyzer']['params']['temperature']}")
    print(f"   Max Tokens: {original_config['nodes']['analyzer']['params'].get('max_tokens', 'Not set')}")
    print()

    # Create modified configuration
    modified_config = original_config.copy()
    modified_config['nodes']['analyzer']['params']['model'] = "deepseek-ai/DeepSeek-R1-0528"
    modified_config['nodes']['analyzer']['params']['temperature'] = 0.1
    modified_config['nodes']['analyzer']['params']['max_tokens'] = 1000
    modified_config['nodes']['analyzer']['config']['prompt'] = """
    Analyze the sentiment of this text and provide detailed reasoning:
    Text: @processed_text

    Respond with JSON format:
    {
        "sentiment": "positive/negative/neutral",
        "confidence": 0.0-1.0,
        "reasoning": "Detailed explanation",
        "key_phrases": ["phrase1", "phrase2"]
    }
    """
    modified_config['nodes']['analyzer']['config']['structured'] = True

    print("🔄 Modified Configuration:")
    print(f"   Model: {modified_config['nodes']['analyzer']['params']['model']}")
    print(f"   Temperature: {modified_config['nodes']['analyzer']['params']['temperature']}")
    print(f"   Max Tokens: {modified_config['nodes']['analyzer']['params']['max_tokens']}")
    print(f"   Structured Output: {modified_config['nodes']['analyzer']['config']['structured']}")
    print()

    # Build and test modified workflow
    print("🚀 Testing Modified Workflow:")
    print()

    from utils.config_loader import ConfigLoader
    loader = ConfigLoader()
    import tempfile
    import os

    # Save modified config to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
        loader.save(modified_config, f.name, format='toml')
        temp_config_path = f.name

    try:
        # Build workflow from modified config
        modified_workflow = build_workflow_from_config(temp_config_path)

        # Test with same text
        test_text = "This product exceeded all my expectations! Incredible quality and amazing customer service."

        shared = {
            "text": test_text,
            "timestamp": "2025-01-15T10:30:00Z"
        }

        print(f"📝 Test: {test_text}")
        print("-" * 50)

        modified_workflow.run(shared)

        # Show results from modified workflow
        if "analysis" in shared:
            analysis = shared["analysis"]
            if isinstance(analysis, dict):
                print(f"🎯 Sentiment: {analysis.get('sentiment', 'N/A')}")
                print(f"📊 Confidence: {analysis.get('confidence', 'N/A')}")
                print(f"💭 Reasoning: {analysis.get('reasoning', 'N/A')}")
                print(f"🔑 Key Phrases: {analysis.get('key_phrases', 'N/A')}")

    except Exception as e:
        print(f"❌ Modified workflow failed: {e}")
        logger.error(f"Modified workflow error: {e}")
    finally:
        # Clean up temp file
        os.unlink(temp_config_path)

    print()
    print("✨ This demonstrates how workflow behavior can be changed")
    print("   simply by modifying configuration files!")


def main():
    """Run all configuration-driven examples."""
    print("🎯 Configuration-Driven Workflow Examples")
    print("=" * 60)
    print("These examples show how to build entire workflows from")
    print("configuration files, enabling behavior changes without code modifications.")
    print()

    try:
        # Run examples
        run_sentiment_analysis_example()
        run_resume_analysis_example()
        demonstrate_config_modification()

        print("=" * 60)
        print("🎉 All configuration examples completed!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Configuration examples failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nMake sure configuration files exist in the configs/ directory.")
        print("Install required packages: pip install toml pyyaml")


if __name__ == "__main__":
    main()