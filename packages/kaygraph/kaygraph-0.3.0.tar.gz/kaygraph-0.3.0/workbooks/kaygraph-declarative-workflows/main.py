"""
Declarative Workflow Patterns - Overview and Examples

This file demonstrates all the key patterns for building declarative workflows
with KayGraph, including multiplicity parsing, concept validation, configuration-driven
nodes, and flexible data mapping.
"""

import sys
import logging
from typing import Dict, Any, List

# Add the utils directory to path
sys.path.insert(0, '.')

from kaygraph import Node, Graph, ValidatedNode
from utils import Multiplicity, Concept, ConceptValidator, ConfigLoader, call_llm
from nodes import (
    ConceptNode, ConfigNode, MapperNode, ConditionalNode,
    ConfigurableBatchNode, create_node_from_config
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_multiplicity_system():
    """Demonstrate the multiplicity parsing system."""
    print("=" * 60)
    print("🔢 MULTIPLICITY SYSTEM DEMO")
    print("=" * 60)

    examples = [
        "Text",
        "Text[]",
        "Image[3]",
        "domain.Concept",
        "domain.Concept[]",
        "domain.Concept[5]"
    ]

    for example in examples:
        result = Multiplicity.parse(example)
        print(f"📝 {example}")
        print(f"   Concept: {result.concept}")
        print(f"   Multiplicity: {result.multiplicity}")
        print(f"   Is single: {result.is_single}")
        print(f"   Is multiple: {result.is_multiple}")
        print(f"   Is variable length: {result.is_variable_length}")
        print(f"   Is fixed length: {result.is_fixed_length}")
        if result.is_fixed_length:
            print(f"   Count: {result.count}")
        print()

    # Demonstrate compatibility checking
    print("🔍 Compatibility Examples:")
    compat_examples = [
        ("Text", "Text"),
        ("Text", "Text[]"),
        ("Text[]", "Text[3]"),
        ("Image[2]", "Image[5]"),
        ("Document", "Image")  # Incompatible
    ]

    for input_spec, output_spec in compat_examples:
        compatible = Multiplicity.is_compatible(input_spec, output_spec)
        status = "✅" if compatible else "❌"
        print(f"   {status} {input_spec} → {output_spec}")

    print()


def demo_concept_validation():
    """Demonstrate concept validation system."""
    print("=" * 60)
    print("🛡️ CONCEPT VALIDATION DEMO")
    print("=" * 60)

    # Register a custom concept
    product_review = {
        "description": "Product review analysis",
        "structure": {
            "product_name": {
                "type": "text",
                "required": True,
                "description": "Name of the reviewed product"
            },
            "rating": {
                "type": "number",
                "required": True,
                "min_value": 1.0,
                "max_value": 5.0,
                "description": "Rating from 1 to 5"
            },
            "sentiment": {
                "type": "text",
                "required": True,
                "choices": ["positive", "negative", "neutral"],
                "description": "Overall sentiment"
            },
            "review_text": {
                "type": "text",
                "required": False,
                "pattern": r".{10,}",  # At least 10 characters
                "description": "Full review text"
            }
        }
    }

    validator = ConceptValidator()
    validator.register_concept("product_review", product_review)

    print("✅ Registered concept: product_review")
    print()

    # Test valid data
    valid_data = {
        "product_name": "Smart Widget Pro",
        "rating": 4.5,
        "sentiment": "positive",
        "review_text": "This is an amazing product that exceeded my expectations!"
    }

    try:
        validated = validator.validate_data("product_review", valid_data)
        print("✅ Valid data passed validation:")
        for key, value in validated.items():
            print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Validation failed: {e}")

    print()

    # Test invalid data
    invalid_data = {
        "product_name": "Smart Widget Pro",
        "rating": 6.0,  # Invalid: above max 5.0
        "sentiment": "okay",  # Invalid: not in choices
        "review_text": "Too short"  # Invalid: doesn't match pattern
    }

    try:
        validated = validator.validate_data("product_review", invalid_data)
        print("❌ This shouldn't happen!")
    except Exception as e:
        print("✅ Invalid data correctly rejected:")
        print(f"   Error: {e}")

    print()


def demo_config_node():
    """Demonstrate configuration-driven node."""
    print("=" * 60)
    print("⚙️ CONFIGURATION-DRIVEN NODE DEMO")
    print("=" * 60)

    # Create a simple LLM configuration
    llm_config = {
        "node_id": "sentiment_analyzer",
        "type": "llm",
        "description": "Analyzes sentiment of text",
        "inputs": {"text": "Text"},
        "outputs": {"result": "SentimentResult"},
        "params": {
            "model": "meta-llama/Llama-3.3-70B-Instruct",
            "temperature": 0.3
        },
        "config": {
            "prompt": "Analyze the sentiment of this text and respond with 'positive', 'negative', or 'neutral': @text",
            "system_prompt": "You are a sentiment analysis expert.",
            "structured": False
        },
        "next_action": "default"
    }

    # Create the node from configuration
    analyzer = create_node_from_config(llm_config)

    print("✅ Created ConfigNode from configuration:")
    print(f"   Node ID: {analyzer.node_id}")
    print(f"   Type: {analyzer.node_type}")
    print(f"   Description: {analyzer.description}")
    print()

    # Test the node
    shared_data = {
        "text": "I absolutely love this product! It's amazing and works perfectly."
    }

    try:
        result = analyzer.run(shared_data)
        print(f"✅ LLM Analysis Result: {result}")
        print(f"   Stored in shared['result']: {shared_data.get('result', 'Not found')}")
    except Exception as e:
        print(f"❌ LLM Node failed: {e}")

    print()


def demo_mapper_node():
    """Demonstrate flexible data mapping."""
    print("=" * 60)
    print("🗺️ MAPPER NODE DEMO")
    print("=" * 60)

    # Complex mapping configuration
    mapping_config = {
        "sources": ["user_input", "api_response", "metadata"],
        "mappings": {
            "clean_name": {
                "from": "user_input",
                "transform": "title"
            },
            "email_lower": {
                "from": "user_input",
                "transform": "lower"
            },
            "extracted_numbers": {
                "from": "api_response",
                "transform": "extract_numbers"
            },
            "contact_emails": {
                "from": "user_input",
                "transform": "extract_emails"
            },
            "processed_at": {
                "computed": "{current_timestamp}"
            },
            "user_category": {
                "from": "metadata",
                "computed": "metadata.get('category', 'standard')"
            },
            "has_contact_info": {
                "from": "contact_emails",
                "computed": "len(contact_emails) > 0"
            }
        },
        "options": {
            "next_action": "default"
        }
    }

    mapper = MapperNode(mapping_config, node_id="data_transformer")

    print("✅ Created MapperNode with complex transformations:")
    print(f"   Sources: {mapping_config['sources']}")
    print(f"   Transformations: {len(mapping_config['mappings'])}")
    print()

    # Test the mapper
    shared_data = {
        "user_input": "John Doe <john.doe@example.com> is looking for a job",
        "api_response": "The user has 5 years of experience and expects a salary of $75000",
        "metadata": {"category": "premium", "level": "senior"},
        "current_timestamp": "2025-01-15T10:30:00Z"
    }

    try:
        result = mapper.run(shared_data)
        print("✅ Mapping Results:")
        for key, value in shared_data.items():
            if key.startswith(('clean_', 'email_', 'extracted_', 'contact_', 'processed_', 'user_', 'has_')):
                print(f"   {key}: {value}")
    except Exception as e:
        print(f"❌ Mapper Node failed: {e}")

    print()


def demo_conditional_node():
    """Demonstrate enhanced conditional flow control."""
    print("=" * 60)
    print("🔀 CONDITIONAL NODE DEMO")
    print("=" * 60)

    # Create conditional node
    conditional = ConditionalNode(
        expression="score >= 0.8",
        outcomes={
            "True": "premium_workflow",
            "False": "standard_workflow"
        },
        default_outcome="standard_workflow",
        node_id="route_decision"
    )

    print("✅ Created ConditionalNode:")
    print(f"   Expression: {conditional.expression}")
    print(f"   Outcomes: {conditional.outcomes}")
    print(f"   Default: {conditional.default_outcome}")
    print()

    # Test with high score
    print("🧪 Test 1: High score (0.9)")
    shared_data_1 = {"score": 0.9, "user_type": "premium"}

    try:
        result_1 = conditional.run(shared_data_1)
        action_1 = shared_data_1["_conditional_result"]
        print(f"   Score: 0.9 → Action: {action_1}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    # Test with low score
    print("🧪 Test 2: Low score (0.6)")
    shared_data_2 = {"score": 0.6, "user_type": "standard"}

    try:
        result_2 = conditional.run(shared_data_2)
        action_2 = shared_data_2["_conditional_result"]
        print(f"   Score: 0.6 → Action: {action_2}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")

    print()


def demo_batch_processing():
    """Demonstrate configurable batch processing with multiplicity."""
    print("=" * 60)
    print("📦 CONFIGURABLE BATCH PROCESSING DEMO")
    print("=" * 60)

    class TextProcessor(ConfigurableBatchNode):
        """Custom batch processor for text items."""

        def process_item(self, item: Any, index: int) -> Dict[str, Any]:
            """Process individual text item."""
            if isinstance(item, str):
                words = len(item.split())
                chars = len(item)
                return {
                    "original": item,
                    "word_count": words,
                    "char_count": chars,
                    "index": index,
                    "category": "short" if words < 10 else "medium" if words < 50 else "long"
                }
            else:
                return {"original": str(item), "error": "Not a string", "index": index}

    # Test different input/output specifications
    batch_configs = [
        ("Text[]", "ProcessedItem[]", "Variable list input, variable list output"),
        ("Text[3]", "ProcessedItem[3]", "Fixed list input, fixed list output"),
        ("Text", "ProcessedItem[]", "Single input, list output"),
        ("Text[]", "ProcessedItem", "List input, single output")
    ]

    for input_spec, output_spec, description in batch_configs:
        print(f"📋 {description}")
        print(f"   Input spec: {input_spec}")
        print(f"   Output spec: {output_spec}")

        processor = TextProcessor(input_spec, output_spec, node_id=f"batch_{input_spec.replace('[]', '_').replace('[', '_').replace(']', '_')}")

        # Test data
        if "Text[]" in input_spec:
            test_data = {"Text": ["Short text", "This is a medium length text", "This is a much longer text with many more words to process"]}
        elif "[3]" in input_spec:
            test_data = {"Text": ["Item 1", "Item 2", "Item 3", "Extra item"]}  # Will be truncated to 3
        else:
            test_data = {"Text": "Single text item"}

        try:
            result = processor.run(test_data)
            print(f"   ✅ Processed {len(test_data.get('Text', []))} items")

            # Show output metadata
            metadata_key = f"{processor.output_concept}_batch_metadata"
            if metadata_key in test_data:
                metadata = test_data[metadata_key]
                print(f"   📊 Metadata: {metadata}")

        except Exception as e:
            print(f"   ❌ Failed: {e}")

        print()


def demo_config_loading():
    """Demonstrate configuration file loading."""
    print("=" * 60)
    print("📁 CONFIGURATION LOADING DEMO")
    print("=" * 60)

    loader = ConfigLoader()

    # Test TOML loading
    try:
        toml_config = loader.load("configs/workflow.toml")
        print("✅ Loaded TOML configuration:")
        print(f"   Workflow name: {toml_config.get('workflow', {}).get('name')}")
        print(f"   Concepts defined: {len(toml_config.get('concepts', {}))}")
        print(f"   Nodes defined: {len(toml_config.get('nodes', {}))}")
        print()
    except Exception as e:
        print(f"❌ Failed to load TOML: {e}")

    # Test YAML loading
    try:
        yaml_config = loader.load("configs/resume_workflow.yaml")
        print("✅ Loaded YAML configuration:")
        print(f"   Workflow name: {yaml_config.get('workflow', {}).get('name')}")
        print(f"   Concepts defined: {len(yaml_config.get('concepts', {}))}")
        print(f"   Nodes defined: {len(yaml_config.get('nodes', {}))}")
        print()
    except Exception as e:
        print(f"❌ Failed to load YAML: {e}")

    # Test JSON loading
    try:
        json_config = loader.load("configs/mappings.json")
        print("✅ Loaded JSON configuration:")
        print(f"   Mapping definitions: {len(json_config)}")
        first_mapping = list(json_config.keys())[0]
        print(f"   First mapping: {first_mapping}")
        print()
    except Exception as e:
        print(f"❌ Failed to load JSON: {e}")


def demo_end_to_end_workflow():
    """Demonstrate a complete declarative workflow."""
    print("=" * 60)
    print("🔄 END-TO-END DECLARATIVE WORKFLOW DEMO")
    print("=" * 60)

    # Create a sentiment analysis workflow
    class TextCleaner(ConfigNode):
        def __init__(self):
            config = {
                "node_id": "text_cleaner",
                "type": "transform",
                "description": "Cleans and normalizes input text",
                "inputs": {"raw_text": "Text"},
                "outputs": {"clean_text": "CleanText"},
                "config": {
                    "transforms": {
                        "clean_text": {
                            "from": "raw_text",
                            "transform": "normalize_text"
                        }
                    }
                }
            }
            super().__init__(config)

    class SentimentAnalyzer(ConfigNode):
        def __init__(self):
            config = {
                "node_id": "sentiment_analyzer",
                "type": "llm",
                "description": "Analyzes text sentiment",
                "inputs": {"clean_text": "CleanText"},
                "outputs": {"sentiment": "SentimentResult"},
                "params": {"model": "meta-llama/Llama-3.3-70B-Instruct", "temperature": 0.3},
                "config": {
                    "prompt": "Analyze sentiment and respond with only 'positive', 'negative', or 'neutral': @clean_text",
                    "system_prompt": "You are a sentiment analysis expert."
                }
            }
            super().__init__(config)

    class ResultFormatter(MapperNode):
        def __init__(self):
            config = {
                "sources": ["sentiment", "clean_text"],
                "mappings": {
                    "sentiment_label": {"from": "sentiment"},
                    "text_preview": {
                        "from": "clean_text",
                        "transform": "split",
                        "params": {"separator": " "},
                        "computed": "text_preview[:5] + ['...'] if len(text_preview) > 5 else text_preview"
                    },
                    "confidence": {"computed": "0.85"},
                    "processed_at": {"computed": "{timestamp}"}
                }
            }
            super().__init__(config)

    # Build the workflow
    cleaner = TextCleaner()
    analyzer = SentimentAnalyzer()
    formatter = ResultFormatter()

    # Connect nodes
    cleaner >> analyzer >> formatter

    # Create graph
    workflow = Graph(start=cleaner)

    # Test the workflow
    test_inputs = [
        "I love this product! It's absolutely amazing and works perfectly!",
        "This is terrible. Complete waste of money and doesn't work at all.",
        "It's okay, nothing special but does what it's supposed to do."
    ]

    print("🚀 Running sentiment analysis workflow:")
    print()

    for i, text in enumerate(test_inputs, 1):
        print(f"📝 Test {i}: {text[:50]}{'...' if len(text) > 50 else ''}")

        shared_data = {
            "raw_text": text,
            "timestamp": "2025-01-15T10:30:00Z"
        }

        try:
            workflow.run(shared_data)
            result = shared_data.get("sentiment_label", "Unknown")
            confidence = shared_data.get("confidence", 0.0)
            print(f"   ✅ Result: {result} (confidence: {confidence})")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
        print()

    print("🎉 Workflow demonstration completed!")


def main():
    """Run all demonstrations."""
    print("🎯 KayGraph Declarative Workflow Patterns")
    print("=" * 60)
    print("This demo showcases advanced patterns for building type-safe,")
    print("configuration-driven workflows with KayGraph.")
    print()

    try:
        # Run all demos
        demo_multiplicity_system()
        demo_concept_validation()
        demo_config_node()
        demo_mapper_node()
        demo_conditional_node()
        demo_batch_processing()
        demo_config_loading()
        demo_end_to_end_workflow()

        print("\n" + "=" * 60)
        print("🎉 All demonstrations completed successfully!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nNote: Some demos require API keys or external dependencies.")
        print("Check the configuration and try again.")


if __name__ == "__main__":
    main()