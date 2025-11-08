"""
Declarative workflow nodes for KayGraph.

Provides configuration-driven, type-safe nodes that enable building
workflows through configuration rather than code.
"""

import re
import copy
import json
from typing import Any, Dict, List, Optional, Union
from kaygraph import Node, ValidatedNode, AsyncNode
import logging

from utils.multiplicity import Multiplicity, MultiplicityParseResult
from utils.concepts import Concept, ConceptValidator, ValidationError
from utils.config_loader import ConfigLoader
from utils.call_llm import call_llm, extract_json, LLMConfig

logger = logging.getLogger(__name__)


class ConceptNode(ValidatedNode):
    """
    Node that provides type-safe data processing using concept validation.

    Validates input and output data against concept definitions to ensure
    type safety and data integrity throughout the workflow.
    """

    def __init__(self, concept_name: str, node_id: Optional[str] = None, **kwargs):
        """
        Initialize concept node.

        Args:
            concept_name: Name of the concept to validate against
            node_id: Optional node identifier
            **kwargs: Additional arguments passed to ValidatedNode
        """
        super().__init__(node_id=node_id or f"concept_{concept_name}", **kwargs)
        self.concept_name = concept_name
        self._concept_validator = ConceptValidator()

        # Get the concept (will raise if not found)
        try:
            self.concept = self._concept_validator.get_concept(concept_name)
        except KeyError:
            # Register a basic concept if not found
            self.concept = Concept({
                "description": f"Auto-generated concept for {concept_name}",
                "structure": {"data": {"type": "text", "required": True}}
            })
            self._concept_validator.register_concept(concept_name, self.concept.to_dict())

    def validate_input(self, input_data: Any) -> Any:
        """Validate input data against the concept."""
        try:
            return self.concept.validate(input_data)
        except ValidationError as e:
            self.logger.error(f"Input validation failed: {e}")
            raise

    def validate_output(self, output_data: Any) -> Any:
        """Validate output data against the concept."""
        try:
            return self.concept.validate(output_data)
        except ValidationError as e:
            self.logger.error(f"Output validation failed: {e}")
            raise

    def create_example_input(self) -> Dict[str, Any]:
        """Create an example input that would pass validation."""
        return self.concept.create_example(include_optional=False)

    def get_concept_definition(self) -> Dict[str, Any]:
        """Get the concept definition for documentation."""
        return self.concept.to_dict()


class ConfigNode(ValidatedNode):
    """
    Node that loads its behavior from configuration rather than code.

    Enables building workflows through declarative configuration files.
    """

    def __init__(self, config: Dict[str, Any], node_id: Optional[str] = None,
                 result_name: Optional[str] = None, input_names: Optional[List[str]] = None,
                 output_concept: Optional[str] = None, **kwargs):
        """
        Initialize configuration-driven node.

        Args:
            config: Configuration dictionary defining node behavior
            node_id: Optional node identifier
            result_name: Optional name for storing output in results store
            input_names: Optional list of named results to use as inputs
            output_concept: Optional concept name for output validation
            **kwargs: Additional arguments passed to ValidatedNode
        """
        super().__init__(node_id=node_id or config.get("node_id", "config_node"), **kwargs)
        self.config = config
        self.result_name = result_name
        self.input_names = input_names or []
        self.output_concept = output_concept

        # Validate required config fields
        if "type" not in config:
            raise ValueError("ConfigNode requires 'type' field in configuration")

        self.node_type = config["type"]
        self.description = config.get("description", f"Configurable {self.node_type} node")
        self.inputs = config.get("inputs", {})
        self.outputs = config.get("outputs", {})
        self.params = config.get("params", {})

        # Override node params
        self.set_params({**self.params, **kwargs.get("params", {})})

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Prepare inputs based on configuration."""
        inputs = {}

        # Get inputs from named results first
        if self.input_names:
            results_store = shared.get("__results__", {})
            for input_name in self.input_names:
                if input_name not in results_store:
                    raise ValueError(
                        f"Node '{self.node_id}': Required input '{input_name}' "
                        f"not found in results. Available: {list(results_store.keys())}"
                    )
                inputs[input_name] = results_store[input_name]

        # Extract inputs based on config
        for input_name, input_spec in self.inputs.items():
            if isinstance(input_spec, str):
                # Simple reference to shared state
                inputs[input_name] = shared.get(input_name)
            elif isinstance(input_spec, dict):
                # Complex input specification
                if "from" in input_spec:
                    inputs[input_name] = shared.get(input_spec["from"])
                elif "value" in input_spec:
                    inputs[input_name] = input_spec["value"]
                elif "default" in input_spec:
                    inputs[input_name] = shared.get(input_name, input_spec["default"])

        return inputs

    def exec(self, inputs: Any) -> Any:
        """Execute based on node type from configuration."""
        # Execute node-specific logic
        if self.node_type == "llm":
            result = self._exec_llm(inputs)
        elif self.node_type == "extract":
            result = self._exec_extract(inputs)
        elif self.node_type == "transform":
            result = self._exec_transform(inputs)
        elif self.node_type == "validate":
            result = self._exec_validate(inputs)
        elif self.node_type == "condition":
            result = self._exec_condition(inputs)
        else:
            raise ValueError(f"Unsupported node type: {self.node_type}")

        # Validate against output concept if specified
        if self.output_concept:
            from utils.concepts import get_concept_registry
            registry = get_concept_registry()

            if registry.has(self.output_concept):
                validation = registry.validate(self.output_concept, result)

                if not validation.get("valid", False):
                    errors = validation.get("errors", [])
                    raise ValueError(
                        f"Node '{self.node_id}': Output validation failed for "
                        f"concept '{self.output_concept}':\n" +
                        "\n".join(f"  - {err}" for err in errors)
                    )

        return result

    def _exec_llm(self, inputs: Dict[str, Any]) -> Any:
        """Execute LLM node type."""
        prompt = self.config.get("prompt", "")
        system_prompt = self.config.get("system_prompt", "")
        model = self.config.get("model", "meta-llama/Llama-3.3-70B-Instruct")
        temperature = self.config.get("temperature", 0.7)
        max_tokens = self.config.get("max_tokens", 2000)

        # Replace variable placeholders
        formatted_prompt = self._format_template(prompt, inputs)

        # Check if we want structured output
        if self.config.get("structured", False):
            schema = self.config.get("schema", {})
            result = extract_json(formatted_prompt, schema, model=model, temperature=temperature, max_tokens=max_tokens)
        else:
            # Regular LLM call
            if system_prompt:
                result = call_llm(
                    [{"role": "system", "content": system_prompt},
                     {"role": "user", "content": formatted_prompt}],
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                result = call_llm(
                    [{"role": "user", "content": formatted_prompt}],
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

        return result

    def _exec_extract(self, inputs: Dict[str, Any]) -> Any:
        """Execute extract node type."""
        field = self.config.get("field", "content")
        pattern = self.config.get("pattern", "")
        input_data = inputs.get(field, "")

        if pattern:
            # Extract using regex pattern
            match = re.search(pattern, str(input_data))
            if match:
                return match.group(1) if match.groups() else match.group(0)
        else:
            # Simple extraction
            return input_data

    def _exec_transform(self, inputs: Dict[str, Any]) -> Any:
        """Execute transform node type."""
        transforms = self.config.get("transforms", {})
        result = {}

        for output_field, transform_spec in transforms.items():
            if isinstance(transform_spec, str):
                # Simple field copy
                result[output_field] = inputs.get(transform_spec)
            elif isinstance(transform_spec, dict):
                # Complex transformation
                if "from" in transform_spec:
                    value = inputs.get(transform_spec["from"])
                    transform_type = transform_spec.get("transform", "identity")

                    if transform_type == "upper":
                        result[output_field] = str(value).upper() if value else value
                    elif transform_type == "lower":
                        result[output_field] = str(value).lower() if value else value
                    elif transform_type == "split":
                        separator = transform_spec.get("separator", ",")
                        result[output_field] = str(value).split(separator) if value else []
                    elif transform_type == "join":
                        separator = transform_spec.get("separator", ",")
                        if isinstance(value, list):
                            result[output_field] = separator.join(str(v) for v in value)
                        else:
                            result[output_field] = str(value)
                    elif transform_type == "regex":
                        pattern = transform_spec.get("pattern", "")
                        replacement = transform_spec.get("replacement", "")
                        result[output_field] = re.sub(pattern, replacement, str(value)) if value else value
                    else:
                        result[output_field] = value
                elif "value" in transform_spec:
                    result[output_field] = transform_spec["value"]

        return result if result else inputs

    def _exec_validate(self, inputs: Dict[str, Any]) -> Any:
        """Execute validate node type."""
        validations = self.config.get("validations", {})
        result = {"valid": True, "errors": []}

        for field, validation_spec in validations.items():
            value = inputs.get(field)
            field_errors = []

            if validation_spec.get("required", False) and (value is None or value == ""):
                field_errors.append(f"Field '{field}' is required")

            if "min_length" in validation_spec and value and len(str(value)) < validation_spec["min_length"]:
                field_errors.append(f"Field '{field}' is too short")

            if "max_length" in validation_spec and value and len(str(value)) > validation_spec["max_length"]:
                field_errors.append(f"Field '{field}' is too long")

            if "pattern" in validation_spec and value and not re.match(validation_spec["pattern"], str(value)):
                field_errors.append(f"Field '{field}' does not match required pattern")

            if field_errors:
                result["valid"] = False
                result["errors"].extend(field_errors)

        return result

    def _exec_condition(self, inputs: Dict[str, Any]) -> Any:
        """Execute condition node type using safe expression evaluation."""
        expression = self.config.get("expression", "")
        context = {**inputs, **self.params}

        try:
            if not expression:
                return True

            # Safe expression evaluation supporting:
            # - Comparisons: ==, !=, <, >, <=, >=
            # - Boolean: and, or
            # - Examples: "age >= 18", "status == 'approved'", "score > 0.5 and verified == True"

            expr = expression.strip()

            # Handle "and" operator
            if ' and ' in expr:
                parts = [p.strip() for p in expr.split(' and ')]
                return all(self._evaluate_comparison(p, context) for p in parts)

            # Handle "or" operator
            if ' or ' in expr:
                parts = [p.strip() for p in expr.split(' or ')]
                return any(self._evaluate_comparison(p, context) for p in parts)

            # Single comparison
            return self._evaluate_comparison(expr, context)

        except Exception as e:
            self.logger.error(f"Error evaluating condition '{expression}': {e}")
            return False

    def _evaluate_comparison(self, expr: str, context: Dict[str, Any]) -> bool:
        """Evaluate a simple comparison: var OP value"""
        expr = expr.strip()

        # Check for comparison operators (order matters - check >= before >)
        for op in ['>=', '<=', '==', '!=', '>', '<']:
            if op in expr:
                left, right = expr.split(op, 1)
                left_val = self._get_expression_value(left.strip(), context)
                right_val = self._get_expression_value(right.strip(), context)

                if op == '==':
                    return left_val == right_val
                elif op == '!=':
                    return left_val != right_val
                elif op == '>':
                    return float(left_val) > float(right_val)
                elif op == '<':
                    return float(left_val) < float(right_val)
                elif op == '>=':
                    return float(left_val) >= float(right_val)
                elif op == '<=':
                    return float(left_val) <= float(right_val)

        # No operator found - treat as truthy check
        return bool(self._get_expression_value(expr, context))

    def _get_expression_value(self, expr: str, context: Dict[str, Any]) -> Any:
        """Get value from expression (variable, string literal, or number)"""
        expr = expr.strip()

        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Number
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Boolean
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False

        # Variable from context
        return context.get(expr, expr)

    def _format_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Format a template string with variable substitution."""
        result = template

        # Replace @variable patterns
        for key, value in variables.items():
            if value is not None:
                result = result.replace(f"@{key}", str(value))

        return result

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store results and return next action."""
        # Store named result if specified
        if self.result_name:
            if "__results__" not in shared:
                shared["__results__"] = {}
            shared["__results__"][self.result_name] = exec_res

        # Store results based on output configuration
        for output_name, output_spec in self.outputs.items():
            if isinstance(output_spec, str):
                # Simple storage
                shared[output_name] = exec_res
            elif isinstance(output_spec, dict):
                # Complex output handling
                if "from" in output_spec:
                    # Extract specific field from result
                    if isinstance(exec_res, dict) and output_spec["from"] in exec_res:
                        shared[output_name] = exec_res[output_spec["from"]]
                    else:
                        shared[output_name] = exec_res
                else:
                    shared[output_name] = exec_res

        # Return next action
        return self.config.get("next_action", "default")


class BatchConfigNode(ConfigNode):
    """
    Batch processing wrapper for ConfigNode with YAML-friendly syntax.

    Allows LLMs to generate batch processing using simple YAML:
        batch_over: items
        batch_as: item

    Instead of requiring separate BatchNode Python class.
    """

    def __init__(self, batch_over: str, batch_as: str, **kwargs):
        """
        Initialize batch config node.

        Args:
            batch_over: Name of the named result containing items to batch
            batch_as: Variable name for each item in batch
            **kwargs: Arguments passed to ConfigNode
        """
        super().__init__(**kwargs)
        self.batch_over = batch_over
        self.batch_as = batch_as

    def prep(self, shared: Dict[str, Any]) -> List[Any]:
        """Get items to batch over from named results."""
        results_store = shared.get("__results__", {})

        if self.batch_over not in results_store:
            raise ValueError(
                f"Batch node '{self.node_id}': batch_over '{self.batch_over}' "
                f"not found in results. Available: {list(results_store.keys())}"
            )

        items = results_store[self.batch_over]

        # Ensure items is a list
        if not isinstance(items, list):
            items = [items]

        return items

    def exec(self, items: List[Any]) -> List[Any]:
        """Process each item using parent ConfigNode logic."""
        results = []

        for i, item in enumerate(items):
            try:
                # Create temporary shared store with batch item
                temp_inputs = {self.batch_as: item}

                # Call parent exec logic with single item
                result = super().exec(temp_inputs)
                results.append(result)

            except Exception as e:
                self.logger.error(
                    f"Batch item {i} failed in node '{self.node_id}': {e}"
                )
                # Continue processing other items
                results.append({"error": str(e), "item_index": i})

        return results

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: List[Any]) -> str:
        """Store batch results if result_name specified."""
        # Store named result if specified
        if self.result_name:
            if "__results__" not in shared:
                shared["__results__"] = {}
            shared["__results__"][self.result_name] = exec_res

        # Return next action
        return self.config.get("next_action", "default")


class ParallelConfigNode(ConfigNode):
    """
    Execute multiple independent operations in parallel.

    This enables task parallelism - running different operations simultaneously
    rather than sequentially. Each parallel operation:
    - Runs in its own thread
    - Can access the same shared context
    - Stores its own named result
    - Executes independently of others

    Example use cases:
    - Analyze CV + job description + company info simultaneously
    - Call multiple APIs in parallel
    - Process different aspects of data concurrently

    YAML syntax:
        - node: parallel_analysis
          type: parallel
          parallels:
            - node: analyze_cv
              type: llm
              result: cv_analysis
            - node: analyze_job
              type: llm
              result: job_analysis
    """

    def __init__(self, parallels: List[Dict[str, Any]], **kwargs):
        """
        Initialize parallel config node.

        Args:
            parallels: List of step configurations to run in parallel
            **kwargs: Arguments passed to ConfigNode
        """
        super().__init__(**kwargs)
        self.parallels = parallels
        self.parallel_nodes = []

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare parallel execution.

        Creates child nodes from parallel configurations.
        All child nodes share the same shared context.
        """
        # Create child nodes if not already created
        if not self.parallel_nodes:
            from workflow_loader import create_config_node_from_step

            for i, parallel_config in enumerate(self.parallels):
                try:
                    node = create_config_node_from_step(parallel_config)
                    self.parallel_nodes.append(node)
                except Exception as e:
                    raise ValueError(
                        f"Error creating parallel node {i} "
                        f"in '{self.node_id}': {e}"
                    ) from e

        return shared

    def exec(self, shared: Dict[str, Any]) -> List[tuple]:
        """
        Execute all child nodes in parallel using ThreadPoolExecutor.

        Returns:
            List of (node, result) tuples
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=len(self.parallel_nodes)) as executor:
            # Submit all nodes for parallel execution
            future_to_node = {
                executor.submit(self._execute_node, node, shared): node
                for node in self.parallel_nodes
            }

            # Collect results as they complete
            for future in as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    result = future.result()
                    results.append((node, result))
                    self.logger.info(f"Parallel node '{node.node_id}' completed")
                except Exception as e:
                    self.logger.error(
                        f"Parallel node '{node.node_id}' failed: {e}"
                    )
                    raise RuntimeError(
                        f"Parallel execution failed in node '{node.node_id}': {e}"
                    ) from e

        return results

    def _execute_node(self, node: ConfigNode, shared: Dict[str, Any]) -> Any:
        """
        Execute a single child node.

        This runs in a separate thread for each parallel operation.

        Args:
            node: The ConfigNode to execute
            shared: Shared context dictionary

        Returns:
            The execution result
        """
        # Each node runs its full lifecycle
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)

        # Store result if node has result_name
        # (post() would normally do this, but we handle it in parent's post())
        return exec_res

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: List[tuple]) -> str:
        """
        Store all parallel results in shared context.

        Each child node's result is stored with its result_name.

        Args:
            shared: Shared context dictionary
            prep_res: Shared context from prep
            exec_res: List of (node, result) tuples from exec

        Returns:
            Next action (default: "default")
        """
        # Initialize results store if needed
        if "__results__" not in shared:
            shared["__results__"] = {}

        # Store each parallel result
        for node, result in exec_res:
            if node.result_name:
                shared["__results__"][node.result_name] = result
                self.logger.debug(
                    f"Stored parallel result '{node.result_name}'"
                )

        # Return next action
        return self.config.get("next_action", "default")


class MapperNode(ValidatedNode):
    """
    Node that performs flexible data transformation based on mapping configuration.

    Enables complex data transformations without writing code.
    """

    def __init__(self, mapping_config: Dict[str, Any], node_id: Optional[str] = None, **kwargs):
        """
        Initialize mapper node.

        Args:
            mapping_config: Configuration defining how to map/transform data
            node_id: Optional node identifier
            **kwargs: Additional arguments passed to ValidatedNode
        """
        super().__init__(node_id=node_id or "mapper", **kwargs)
        self.mapping_config = mapping_config

        # Validate mapping config
        if "sources" not in mapping_config:
            raise ValueError("MapperNode requires 'sources' in mapping_config")
        if "mappings" not in mapping_config:
            raise ValueError("MapperNode requires 'mappings' in mapping_config")

        self.sources = mapping_config["sources"]
        self.mappings = mapping_config["mappings"]
        self.options = mapping_config.get("options", {})

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract source data from shared state."""
        source_data = {}

        for source_key in self.sources:
            if source_key in shared:
                source_data[source_key] = shared[source_key]
            else:
                self.logger.warning(f"Source key '{source_key}' not found in shared state")

        return source_data

    def exec(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mapping transformations."""
        result = {}

        for target_key, mapping_spec in self.mappings.items():
            if isinstance(mapping_spec, str):
                # Simple copy
                result[target_key] = source_data.get(mapping_spec)
            elif isinstance(mapping_spec, dict):
                # Complex transformation
                if "from" in mapping_spec:
                    source_value = source_data.get(mapping_spec["from"])
                    transform = mapping_spec.get("transform", "identity")

                    result[target_key] = self._apply_transform(source_value, transform, mapping_spec)
                elif "computed" in mapping_spec:
                    # Computed value
                    result[target_key] = self._compute_value(mapping_spec["computed"], source_data)
                elif "default" in mapping_spec:
                    # Default value if source not found
                    source_name = mapping_spec.get("source")
                    if source_name and source_name in source_data:
                        result[target_key] = source_data[source_name]
                    else:
                        result[target_key] = mapping_spec["default"]

        return result

    def _apply_transform(self, value: Any, transform: str, params: Dict[str, Any]) -> Any:
        """Apply a transformation to a value."""
        if value is None and not params.get("allow_none", False):
            return None

        if transform == "identity":
            return value
        elif transform == "upper":
            return str(value).upper() if value else value
        elif transform == "lower":
            return str(value).lower() if value else value
        elif transform == "title":
            return str(value).title() if value else value
        elif transform == "strip":
            return str(value).strip() if value else value
        elif transform == "split":
            separator = params.get("separator", ",")
            max_split = params.get("max_split", -1)
            return str(value).split(separator, max_split) if value else []
        elif transform == "join":
            separator = params.get("separator", ",")
            if isinstance(value, list):
                return separator.join(str(v) for v in value)
            else:
                return str(value)
        elif transform == "regex_extract":
            pattern = params.get("pattern", "")
            group = params.get("group", 0)
            if value and pattern:
                match = re.search(pattern, str(value))
                if match:
                    return match.group(group) if match.groups() else match.group(0)
            return value
        elif transform == "regex_replace":
            pattern = params.get("pattern", "")
            replacement = params.get("replacement", "")
            if value and pattern:
                return re.sub(pattern, replacement, str(value))
            return value
        elif transform == "extract_numbers":
            if value:
                numbers = re.findall(r'\d+\.?\d*', str(value))
                return [float(n) if '.' in n else int(n) for n in numbers]
            return []
        elif transform == "extract_emails":
            if value:
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(value))
                return emails
            return []
        elif transform == "extract_urls":
            if value:
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', str(value))
                return urls
            return []
        elif transform == "normalize_text":
            if value:
                # Remove extra whitespace and normalize
                text = re.sub(r'\s+', ' ', str(value).strip())
                return text
            return value
        elif transform == "json_parse":
            if value:
                try:
                    return json.loads(str(value))
                except json.JSONDecodeError:
                    self.logger.warning(f"Failed to parse JSON: {value}")
                    return value
            return value
        elif transform == "json_stringify":
            if value:
                try:
                    return json.dumps(value, ensure_ascii=False)
                except TypeError:
                    self.logger.warning(f"Failed to stringify JSON: {value}")
                    return str(value)
            return value
        else:
            self.logger.warning(f"Unknown transform: {transform}")
            return value

    def _compute_value(self, computation: str, source_data: Dict[str, Any]) -> Any:
        """Compute a value from source data."""
        try:
            # Simple template computation
            result = computation
            for key, value in source_data.items():
                if value is not None:
                    result = result.replace(f"{{{key}}}", str(value))
            return result
        except Exception as e:
            self.logger.error(f"Error computing value '{computation}': {e}")
            return computation

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store mapped data."""
        for key, value in exec_res.items():
            shared[key] = value

        return self.options.get("next_action", "default")


class ConditionalNode(ValidatedNode):
    """
    Node that provides enhanced conditional flow control.

    Supports complex expressions and multiple outcome routing.
    """

    def __init__(self, expression: str, outcomes: Dict[str, str], default_outcome: str,
                 node_id: Optional[str] = None, **kwargs):
        """
        Initialize conditional node.

        Args:
            expression: Python expression to evaluate
            outcomes: Mapping of expression results to next actions
            default_outcome: Default action if no match found
            node_id: Optional node identifier
            **kwargs: Additional arguments passed to ValidatedNode
        """
        super().__init__(node_id=node_id or "conditional", **kwargs)
        self.expression = expression
        self.outcomes = outcomes
        self.default_outcome = default_outcome

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare evaluation context."""
        return {
            "shared": shared,
            "params": self.params
        }

    def exec(self, context: Dict[str, Any]) -> str:
        """Evaluate expression and return appropriate outcome."""
        try:
            # Create safe evaluation context
            safe_context = {
                "shared": context["shared"],
                "params": context["params"]
            }

            # Add shared values to context
            for key, value in context["shared"].items():
                if isinstance(value, (str, int, float, bool)) and key.isidentifier():
                    safe_context[key] = value

            # Add params to context
            for key, value in context["params"].items():
                if isinstance(value, (str, int, float, bool)) and key.isidentifier():
                    safe_context[key] = value

            # Evaluate expression
            result = eval(self.expression, {"__builtins__": {}}, safe_context)

            # Find matching outcome
            if str(result) in self.outcomes:
                return self.outcomes[str(result)]
            else:
                self.logger.info(f"No outcome found for result '{result}', using default")
                return self.default_outcome

        except Exception as e:
            self.logger.error(f"Error evaluating expression '{self.expression}': {e}")
            return self.default_outcome

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Return the computed next action."""
        # Store the decision for debugging
        shared["_conditional_result"] = exec_res
        shared["_conditional_expression"] = self.expression

        return exec_res


class ConfigurableBatchNode(ValidatedNode):
    """
    Enhanced batch node that supports multiplicity notation and flexible processing.

    Extends KayGraph's batch processing with configuration-driven behavior.
    """

    def __init__(self, input_spec: str, output_spec: str, node_id: Optional[str] = None, **kwargs):
        """
        Initialize configurable batch node.

        Args:
            input_spec: Input multiplicity specification (e.g., "Item[]", "Items[5]")
            output_spec: Output multiplicity specification
            node_id: Optional node identifier
            **kwargs: Additional arguments passed to ValidatedNode
        """
        super().__init__(node_id=node_id or "configurable_batch", **kwargs)

        # Parse multiplicity specifications
        self.input_spec_result = Multiplicity.parse(input_spec)
        self.output_spec_result = Multiplicity.parse(output_spec)

        self.input_concept = self.input_spec_result.concept
        self.output_concept = self.output_spec_result.concept
        self.input_multiplicity = self.input_spec_result.multiplicity
        self.output_multiplicity = self.output_spec_result.multiplicity

    def prep(self, shared: Dict[str, Any]) -> List[Any]:
        """Prepare batch items with multiplicity handling."""
        # Get input data based on concept name
        input_data = shared.get(self.input_concept)

        if input_data is None:
            self.logger.warning(f"No input data found for concept '{self.input_concept}'")
            return []

        # Normalize to list using multiplicity
        items = Multiplicity.normalize_data(input_data, self.input_spec_result.to_spec())

        if not isinstance(items, list):
            items = [items]

        return items

    def exec(self, items: List[Any]) -> List[Any]:
        """Process each item in the batch."""
        results = []

        for i, item in enumerate(items):
            try:
                # Process item (override this method in subclasses)
                processed_item = self.process_item(item, i)
                results.append(processed_item)
            except Exception as e:
                self.logger.error(f"Error processing item {i}: {e}")
                if self.params.get("fail_fast", False):
                    raise
                # Continue with other items
                continue

        return results

    def process_item(self, item: Any, index: int) -> Any:
        """
        Process a single item from the batch.

        Override this method in subclasses to implement custom processing logic.

        Args:
            item: The item to process
            index: Index of the item in the batch

        Returns:
            Processed item
        """
        # Default implementation - pass through
        return item

    def post(self, shared: Dict[str, Any], prep_res: List[Any], exec_res: List[Any]) -> str:
        """Handle output multiplicity and store results."""
        # Apply output multiplicity rules
        normalized_output = Multiplicity.normalize_data(exec_res, self.output_spec_result.to_spec())

        # Store results
        shared[self.output_concept] = normalized_output

        # Store batch metadata
        shared[f"{self.output_concept}_batch_metadata"] = {
            "input_count": len(prep_res),
            "output_count": len(exec_res),
            "input_spec": self.input_spec_result.to_spec(),
            "output_spec": self.output_spec_result.to_spec()
        }

        return "default"


# Factory function for creating nodes from configuration
def create_node_from_config(config: Dict[str, Any], **kwargs) -> Node:
    """
    Create a node instance from configuration.

    Args:
        config: Node configuration dictionary
        **kwargs: Additional parameters

    Returns:
        Configured node instance
    """
    node_type = config.get("type", "")

    if node_type == "concept":
        return ConceptNode(config["concept"], **kwargs)
    elif node_type == "config":
        return ConfigNode(config, **kwargs)
    elif node_type == "mapper":
        return MapperNode(config["mapping"], **kwargs)
    elif node_type == "conditional":
        return ConditionalNode(
            config["expression"],
            config["outcomes"],
            config["default_outcome"],
            **kwargs
        )
    elif node_type == "batch":
        return ConfigurableBatchNode(
            config["input_spec"],
            config["output_spec"],
            **kwargs
        )
    else:
        # Default to ConfigNode for unknown types
        return ConfigNode(config, **kwargs)