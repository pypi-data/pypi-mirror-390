"""
Concept validation system for type-safe data structures.

Provides validation and type checking for structured data based on concept definitions.
"""

import re
from typing import Any, Dict, List, Optional, Union, get_origin, get_args
from dataclasses import dataclass
from datetime import datetime
import json


class ValidationError(Exception):
    """Raised when concept validation fails."""

    def __init__(self, message: str, path: str = "", value: Any = None):
        self.message = message
        self.path = path
        self.value = value
        super().__init__(f"Validation error at '{path}': {message}")


@dataclass
class FieldDefinition:
    """Definition of a field in a concept structure."""

    name: str
    field_type: str
    required: bool = True
    default_value: Any = None
    description: Optional[str] = None
    choices: Optional[List[str]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    pattern: Optional[str] = None


class Concept:
    """
    Represents a type-safe data structure concept with validation.

    Concepts define the structure and validation rules for data processed
    by declarative workflows.
    """

    def __init__(self, definition: Dict[str, Any]):
        """
        Initialize a concept from its definition.

        Args:
            definition: Concept definition dict with 'description' and 'structure'
        """
        if not isinstance(definition, dict):
            raise ValidationError("Concept definition must be a dictionary")

        if "description" not in definition:
            raise ValidationError("Concept definition must include 'description'")

        if "structure" not in definition:
            raise ValidationError("Concept definition must include 'structure'")

        self.description = definition["description"]
        self.structure_def = definition["structure"]
        self._fields = self._parse_structure()

    @classmethod
    def from_yaml_dict(cls, name: str, definition: Dict[str, Any]) -> 'Concept':
        """Create Concept from YAML dictionary definition.

        Allows defining concepts inline in YAML workflows.

        Args:
            name: Concept name (for reference)
            definition: Dict with 'description' and 'structure' keys

        Returns:
            Concept instance

        Example YAML:
            concepts:
              Invoice:
                description: "Commercial invoice"
                structure:
                  total:
                    type: number
                    required: true
                    min_value: 0.0
                  status:
                    type: text
                    choices: ["pending", "paid"]
        """
        # Validate structure
        if not isinstance(definition, dict):
            raise ValidationError(f"Concept '{name}' definition must be a dict")

        if "structure" not in definition:
            raise ValidationError(f"Concept '{name}' missing 'structure' field")

        # Add description if missing
        if "description" not in definition:
            definition["description"] = f"Concept: {name}"

        # Create concept using standard __init__
        concept = cls(definition)
        concept.name = name  # Store name for reference
        return concept

    def _parse_structure(self) -> Dict[str, FieldDefinition]:
        """Parse the structure definition into FieldDefinition objects."""
        fields = {}

        for field_name, field_spec in self.structure_def.items():
            if isinstance(field_spec, str):
                # Simple type specification: "text", "number", etc.
                fields[field_name] = FieldDefinition(
                    name=field_name,
                    field_type=field_spec,
                    required=True
                )
            elif isinstance(field_spec, dict):
                # Detailed field specification
                field_def = FieldDefinition(
                    name=field_name,
                    field_type=field_spec.get("type", "text"),
                    required=field_spec.get("required", True),
                    default_value=field_spec.get("default"),
                    description=field_spec.get("description"),
                    choices=field_spec.get("choices"),
                    min_value=field_spec.get("min_value"),
                    max_value=field_spec.get("max_value"),
                    pattern=field_spec.get("pattern")
                )
                fields[field_name] = field_def
            else:
                raise ValidationError(
                    f"Invalid field specification for '{field_name}': {field_spec!r}"
                )

        return fields

    def validate(self, data: Any, path: str = "") -> Any:
        """
        Validate data against this concept's structure.

        Args:
            data: Data to validate
            path: Current validation path (for error reporting)

        Returns:
            Validated and possibly normalized data

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(data, dict):
            raise ValidationError(
                f"Expected dict, got {type(data).__name__}",
                path=path,
                value=data
            )

        validated_data = {}

        # Check required fields and validate all present fields
        for field_name, field_def in self._fields.items():
            current_path = f"{path}.{field_name}" if path else field_name

            if field_name in data:
                # Field is present, validate it
                validated_value = self._validate_field(
                    field_def, data[field_name], current_path
                )
                validated_data[field_name] = validated_value
            elif field_def.required:
                # Required field is missing
                raise ValidationError(
                    f"Required field '{field_name}' is missing",
                    path=current_path
                )
            elif field_def.default_value is not None:
                # Use default value for optional field
                validated_data[field_name] = field_def.default_value

        # Check for unexpected fields
        for field_name in data:
            if field_name not in self._fields:
                current_path = f"{path}.{field_name}" if path else field_name
                raise ValidationError(
                    f"Unexpected field '{field_name}'",
                    path=current_path,
                    value=data[field_name]
                )

        return validated_data

    def _validate_field(self, field_def: FieldDefinition, value: Any, path: str) -> Any:
        """Validate a single field value."""
        # Check for None values
        if value is None:
            if field_def.required:
                raise ValidationError(
                    f"Field '{field_def.name}' cannot be None",
                    path=path,
                    value=value
                )
            return None

        # Type-specific validation
        validated_value = self._validate_field_type(field_def, value, path)

        # Constraint validation
        validated_value = self._validate_field_constraints(field_def, validated_value, path)

        return validated_value

    def _validate_field_type(self, field_def: FieldDefinition, value: Any, path: str) -> Any:
        """Validate field type."""
        field_type = field_def.field_type.lower()

        if field_type == "text" or field_type == "string":
            if not isinstance(value, str):
                raise ValidationError(
                    f"Expected text, got {type(value).__name__}",
                    path=path,
                    value=value
                )
            return value

        elif field_type == "number" or field_type == "numeric" or field_type == "float":
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value)
                except ValueError:
                    raise ValidationError(
                        f"Cannot convert '{value}' to number",
                        path=path,
                        value=value
                    )
            else:
                raise ValidationError(
                    f"Expected number, got {type(value).__name__}",
                    path=path,
                    value=value
                )

        elif field_type == "integer" or field_type == "int":
            if isinstance(value, int):
                return value
            elif isinstance(value, float) and value.is_integer():
                return int(value)
            elif isinstance(value, str):
                try:
                    return int(value)
                except ValueError:
                    raise ValidationError(
                        f"Cannot convert '{value}' to integer",
                        path=path,
                        value=value
                    )
            else:
                raise ValidationError(
                    f"Expected integer, got {type(value).__name__}",
                    path=path,
                    value=value
                )

        elif field_type == "boolean" or field_type == "bool":
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                if value.lower() in ("true", "1", "yes", "on"):
                    return True
                elif value.lower() in ("false", "0", "no", "off"):
                    return False
                else:
                    raise ValidationError(
                        f"Cannot convert '{value}' to boolean",
                        path=path,
                        value=value
                    )
            elif isinstance(value, (int, float)):
                return bool(value)
            else:
                raise ValidationError(
                    f"Expected boolean, got {type(value).__name__}",
                    path=path,
                    value=value
                )

        elif field_type == "date" or field_type == "datetime":
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                try:
                    # Try ISO format first
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        # Try common formats
                        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        raise ValidationError(
                            f"Cannot parse '{value}' as datetime",
                            path=path,
                            value=value
                        )
            else:
                raise ValidationError(
                    f"Expected datetime, got {type(value).__name__}",
                    path=path,
                    value=value
                )

        elif field_type == "list" or field_type == "array":
            if not isinstance(value, (list, tuple)):
                raise ValidationError(
                    f"Expected list, got {type(value).__name__}",
                    path=path,
                    value=value
                )
            return list(value)

        elif field_type == "dict" or field_type == "object":
            if not isinstance(value, dict):
                raise ValidationError(
                    f"Expected dict, got {type(value).__name__}",
                    path=path,
                    value=value
                )
            return dict(value)

        else:
            # Unknown type, accept as-is
            return value

    def _validate_field_constraints(self, field_def: FieldDefinition, value: Any, path: str) -> Any:
        """Validate field constraints like choices, min/max, patterns."""
        # Choice validation
        if field_def.choices and value not in field_def.choices:
            raise ValidationError(
                f"Value '{value}' not in allowed choices: {field_def.choices}",
                path=path,
                value=value
            )

        # Numeric range validation
        if isinstance(value, (int, float)):
            if field_def.min_value is not None and value < field_def.min_value:
                raise ValidationError(
                    f"Value {value} is less than minimum {field_def.min_value}",
                    path=path,
                    value=value
                )
            if field_def.max_value is not None and value > field_def.max_value:
                raise ValidationError(
                    f"Value {value} is greater than maximum {field_def.max_value}",
                    path=path,
                    value=value
                )

        # Pattern validation for strings
        if isinstance(value, str) and field_def.pattern:
            if not re.match(field_def.pattern, value):
                raise ValidationError(
                    f"Value '{value}' does not match pattern '{field_def.pattern}'",
                    path=path,
                    value=value
                )

        return value

    def create_example(self, include_optional: bool = False) -> Dict[str, Any]:
        """
        Create an example data structure for this concept.

        Args:
            include_optional: Whether to include optional fields in the example

        Returns:
            Example data dictionary
        """
        example = {}

        for field_name, field_def in self._fields.items():
            if not field_def.required and not include_optional:
                continue

            example[field_name] = self._create_field_example(field_def)

        return example

    def _create_field_example(self, field_def: FieldDefinition) -> Any:
        """Create an example value for a field."""
        if field_def.default_value is not None:
            return field_def.default_value

        if field_def.choices:
            return field_def.choices[0]

        field_type = field_def.field_type.lower()

        if field_type in ("text", "string"):
            return f"example_{field_def.name}"
        elif field_type in ("number", "numeric", "float"):
            return 42.0
        elif field_type in ("integer", "int"):
            return 42
        elif field_type in ("boolean", "bool"):
            return True
        elif field_type in ("date", "datetime"):
            return datetime.now().isoformat()
        elif field_type in ("list", "array"):
            return [f"item_{i}" for i in range(3)]
        elif field_type in ("dict", "object"):
            return {"key": "value"}
        else:
            return f"example_{field_def.name}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert concept definition to dictionary."""
        return {
            "description": self.description,
            "structure": self.structure_def
        }


class ConceptValidator:
    """
    Utility class for validating concepts and managing concept registries.
    """

    def __init__(self):
        self._concepts: Dict[str, Concept] = {}

    def register_concept(self, name: str, definition: Dict[str, Any]) -> Concept:
        """
        Register a new concept.

        Args:
            name: Concept name
            definition: Concept definition

        Returns:
            Created Concept object
        """
        concept = Concept(definition)
        self._concepts[name] = concept
        return concept

    def get_concept(self, name: str) -> Concept:
        """
        Get a registered concept by name.

        Args:
            name: Concept name

        Returns:
            Concept object

        Raises:
            KeyError: If concept not found
        """
        if name not in self._concepts:
            raise KeyError(f"Concept '{name}' not registered")
        return self._concepts[name]

    def validate_data(self, concept_name: str, data: Any) -> Any:
        """
        Validate data against a registered concept.

        Args:
            concept_name: Name of concept to validate against
            data: Data to validate

        Returns:
            Validated data

        Raises:
            KeyError: If concept not found
            ValidationError: If validation fails
        """
        concept = self.get_concept(concept_name)
        return concept.validate(data)

    def list_concepts(self) -> List[str]:
        """Get list of registered concept names."""
        return list(self._concepts.keys())

    def create_example(self, concept_name: str, include_optional: bool = False) -> Dict[str, Any]:
        """
        Create example data for a concept.

        Args:
            concept_name: Name of concept
            include_optional: Whether to include optional fields

        Returns:
            Example data dictionary
        """
        concept = self.get_concept(concept_name)
        return concept.create_example(include_optional)


# Global concept validator instance
_default_validator = ConceptValidator()


# Convenience functions
def register_concept(name: str, definition: Dict[str, Any]) -> Concept:
    """Register a concept with the default validator."""
    return _default_validator.register_concept(name, definition)


def get_concept(name: str) -> Concept:
    """Get a concept from the default validator."""
    return _default_validator.get_concept(name)


def validate_data(concept_name: str, data: Any) -> Any:
    """Validate data against a concept using the default validator."""
    return _default_validator.validate_data(concept_name, data)


def create_example(concept_name: str, include_optional: bool = False) -> Dict[str, Any]:
    """Create example data for a concept using the default validator."""
    return _default_validator.create_example(concept_name, include_optional)


# Predefined common concepts
SENTIMENT_ANALYSIS = {
    "description": "Sentiment analysis result",
    "structure": {
        "sentiment": {
            "type": "text",
            "required": True,
            "choices": ["positive", "negative", "neutral"],
            "description": "Overall sentiment classification"
        },
        "confidence": {
            "type": "number",
            "required": True,
            "min_value": 0.0,
            "max_value": 1.0,
            "description": "Confidence score"
        },
        "reasoning": {
            "type": "text",
            "required": False,
            "description": "Explanation for sentiment classification"
        }
    }
}

RESUME_MATCH = {
    "description": "Resume-job matching analysis",
    "structure": {
        "overall_score": {
            "type": "number",
            "required": True,
            "min_value": 0.0,
            "max_value:": 1.0,
            "description": "Overall match score"
        },
        "strengths": {
            "type": "text",
            "required": True,
            "description": "Candidate's strengths relative to requirements"
        },
        "gaps": {
            "type": "text",
            "required": True,
            "description": "Areas where candidate doesn't meet requirements"
        },
        "recommendation": {
            "type": "text",
            "required": True,
            "choices": ["strong_recommend", "recommend", "consider", "not_recommended"],
            "description": "Hiring recommendation"
        }
    }
}

CONTENT_ANALYSIS = {
    "description": "Content analysis result",
    "structure": {
        "main_topic": {
            "type": "text",
            "required": True,
            "description": "Primary topic of the content"
        },
        "key_points": {
            "type": "list",
            "required": True,
            "description": "List of key points extracted"
        },
        "sentiment": {
            "type": "text",
            "required": True,
            "choices": ["positive", "negative", "neutral"],
            "description": "Overall sentiment"
        },
        "readability_score": {
            "type": "number",
            "required": False,
            "min_value": 0.0,
            "max_value": 100.0,
            "description": "Readability score (0-100)"
        }
    }
}


# Register predefined concepts
register_concept("sentiment_analysis", SENTIMENT_ANALYSIS)
register_concept("resume_match", RESUME_MATCH)
register_concept("content_analysis", CONTENT_ANALYSIS)


class ConceptRegistry:
    """Registry for managing concepts defined in workflows.

    Allows loading concepts from YAML definitions and validating
    data against registered concepts.
    """

    def __init__(self):
        """Initialize empty concept registry."""
        self._concepts: Dict[str, Concept] = {}

    def register(self, name: str, concept: Concept):
        """Register a concept by name.

        Args:
            name: Concept name
            concept: Concept instance
        """
        self._concepts[name] = concept

    def get(self, name: str) -> Concept:
        """Get concept by name.

        Args:
            name: Concept name

        Returns:
            Concept instance

        Raises:
            ValueError: If concept not found
        """
        if name not in self._concepts:
            raise ValueError(
                f"Concept '{name}' not defined. "
                f"Available: {sorted(self._concepts.keys())}"
            )
        return self._concepts[name]

    def has(self, name: str) -> bool:
        """Check if concept exists.

        Args:
            name: Concept name

        Returns:
            True if concept is registered
        """
        return name in self._concepts

    def load_from_yaml(self, concepts_dict: Dict[str, Any]):
        """Load concepts from YAML dictionary.

        Args:
            concepts_dict: Dict of concept_name -> concept_definition

        Example:
            concepts_dict = {
                "Invoice": {
                    "description": "Commercial invoice",
                    "structure": {
                        "total": {"type": "number", "required": True}
                    }
                }
            }
            registry.load_from_yaml(concepts_dict)
        """
        for name, definition in concepts_dict.items():
            concept = Concept.from_yaml_dict(name, definition)
            self.register(name, concept)

    def validate(self, concept_name: str, data: Any) -> Dict[str, Any]:
        """Validate data against a concept.

        Args:
            concept_name: Name of concept to validate against
            data: Data to validate

        Returns:
            Validation result dict with keys:
                - valid: bool
                - data: validated/normalized data (if valid)
                - errors: list of error messages (if invalid)

        Example:
            result = registry.validate("Invoice", invoice_data)
            if result["valid"]:
                print("Valid!")
            else:
                print("Errors:", result["errors"])
        """
        concept = self.get(concept_name)
        validator = ConceptValidator(concept)
        return validator.validate(data)

    def list_concepts(self) -> List[str]:
        """Get list of registered concept names.

        Returns:
            Sorted list of concept names
        """
        return sorted(self._concepts.keys())


# Global default registry
_default_registry = ConceptRegistry()


def get_concept_registry() -> ConceptRegistry:
    """Get the default global concept registry.

    Returns:
        Default ConceptRegistry instance
    """
    return _default_registry