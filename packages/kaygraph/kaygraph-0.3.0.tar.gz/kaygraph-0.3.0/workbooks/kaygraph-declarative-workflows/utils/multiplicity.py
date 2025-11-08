"""
Multiplicity parsing utilities for declarative workflows.

Handles parsing of multiplicity notation like "Text[]", "Image[3]", "Document".
"""

import re
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


@dataclass
class MultiplicityParseResult:
    """Result of parsing a concept string with multiplicity notation."""

    concept: str
    multiplicity: Optional[Union[int, bool]] = None

    @property
    def is_single(self) -> bool:
        """Returns True if this represents a single item."""
        return self.multiplicity is None

    @property
    def is_multiple(self) -> bool:
        """Returns True if this represents multiple items."""
        return self.multiplicity is not None

    @property
    def is_variable_length(self) -> bool:
        """Returns True if this represents a variable-length list."""
        return self.multiplicity is True

    @property
    def is_fixed_length(self) -> bool:
        """Returns True if this represents a fixed-count list."""
        return isinstance(self.multiplicity, int)

    @property
    def count(self) -> Optional[int]:
        """Returns the fixed count if specified, None otherwise."""
        return self.multiplicity if isinstance(self.multiplicity, int) else None

    def to_spec(self) -> str:
        """Convert back to specification string."""
        if self.is_single:
            return self.concept
        elif self.is_variable_length:
            return f"{self.concept}[]"
        elif self.is_fixed_length:
            return f"{self.concept}[{self.multiplicity}]"
        else:
            return self.concept


class Multiplicity:
    """
    Utility class for parsing and working with multiplicity notation.

    Supported formats:
    - "Text" -> single Text item
    - "Text[]" -> variable-length list of Text items
    - "Text[3]" -> exactly 3 Text items
    - "domain.Concept" -> single Concept from domain
    - "domain.Concept[]" -> variable-length list
    - "domain.Concept[5]" -> exactly 5 items
    """

    # Pattern matches: ConceptName, ConceptName[], ConceptName[N], Domain.ConceptName, etc.
    _PATTERN = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?)(?:\[(\d*)\])?$")

    @classmethod
    def parse(cls, spec: str) -> MultiplicityParseResult:
        """
        Parse a concept specification string.

        Args:
            spec: Concept specification like "Text", "Text[]", "Image[3]", "domain.Concept[]"

        Returns:
            MultiplicityParseResult with parsed concept and multiplicity

        Raises:
            ValueError: If the specification has invalid syntax
        """
        if not spec or not isinstance(spec, str):
            raise ValueError(f"Invalid concept specification: {spec!r}")

        match = cls._PATTERN.match(spec.strip())
        if not match:
            raise ValueError(
                f"Invalid concept specification syntax: '{spec}'. "
                f"Expected format: 'ConceptName', 'ConceptName[]', 'ConceptName[N]', "
                f"'domain.ConceptName', 'domain.ConceptName[]', or 'domain.Concept[N]'"
            )

        concept = match.group(1)
        bracket_content = match.group(2)

        # Determine multiplicity
        if bracket_content is None:
            # No brackets - single item
            multiplicity = None
        elif bracket_content == "":
            # Empty brackets [] - variable list
            multiplicity = True
        else:
            # Number in brackets [N] - fixed count
            try:
                multiplicity = int(bracket_content)
                if multiplicity < 0:
                    raise ValueError(f"Multiplicity count must be non-negative: {multiplicity}")
            except ValueError as e:
                raise ValueError(f"Invalid multiplicity count in '{spec}': {bracket_content}") from e

        return MultiplicityParseResult(concept=concept, multiplicity=multiplicity)

    @classmethod
    def validate_spec(cls, spec: str) -> bool:
        """
        Validate if a specification string is syntactically correct.

        Args:
            spec: Concept specification to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            cls.parse(spec)
            return True
        except ValueError:
            return False

    @classmethod
    def make_spec(cls, concept: str, multiplicity: Optional[Union[int, bool]] = None) -> str:
        """
        Create a specification string from concept and multiplicity.

        Args:
            concept: Base concept name
            multiplicity: None for single, True for list, int for fixed count

        Returns:
            Specification string like "Text[]", "Image[3]", etc.
        """
        if not isinstance(concept, str) or not concept:
            raise ValueError(f"Invalid concept name: {concept!r}")

        result = MultiplicityParseResult(concept=concept, multiplicity=multiplicity)
        return result.to_spec()

    @classmethod
    def extract_concept(cls, spec: str) -> str:
        """
        Extract just the concept name from a specification.

        Args:
            spec: Concept specification like "Text[]", "Image[3]"

        Returns:
            Just the concept name like "Text", "Image"
        """
        result = cls.parse(spec)
        return result.concept

    @classmethod
    def extract_multiplicity(cls, spec: str) -> Optional[Union[int, bool]]:
        """
        Extract just the multiplicity from a specification.

        Args:
            spec: Concept specification like "Text[]", "Image[3]"

        Returns:
            Multiplicity: None, True, or int
        """
        result = cls.parse(spec)
        return result.multiplicity

    @classmethod
    def is_compatible(cls, input_spec: str, output_spec: str) -> bool:
        """
        Check if an input specification is compatible with an output specification.

        Args:
            input_spec: Required input specification
            output_spec: Provided output specification

        Returns:
            True if compatible, False otherwise
        """
        try:
            input_result = cls.parse(input_spec)
            output_result = cls.parse(output_spec)
        except ValueError:
            return False

        # Concepts must match exactly
        if input_result.concept != output_result.concept:
            return False

        # If input expects single item, output must be single
        if input_result.is_single and not output_result.is_single:
            return False

        # If input expects multiple, output must be multiple
        if input_result.is_multiple and output_result.is_single:
            return False

        # If input expects fixed count, output must have at least that many
        if input_result.is_fixed_length and output_result.is_fixed_length:
            return input_result.count <= output_result.count

        # If input expects fixed count, output variable list is OK
        if input_result.is_fixed_length and output_result.is_variable_length:
            return True

        # If input expects variable list, output fixed count is OK
        if input_result.is_variable_length and output_result.is_fixed_length:
            return True

        # Variable to variable is OK
        if input_result.is_variable_length and output_result.is_variable_length:
            return True

        # Single to single is OK (checked above)
        return True

    @classmethod
    def normalize_data(cls, data: Any, spec: str) -> Any:
        """
        Normalize data to match the expected multiplicity specification.

        Args:
            data: Input data to normalize
            spec: Target specification

        Returns:
            Normalized data matching the specification
        """
        result = cls.parse(spec)

        if result.is_single:
            # Expect single item
            if isinstance(data, (list, tuple)):
                if len(data) == 0:
                    return None
                elif len(data) == 1:
                    return data[0]
                else:
                    # Take first item from list
                    return data[0]
            else:
                return data

        elif result.is_variable_length:
            # Expect list
            if not isinstance(data, (list, tuple)):
                return [data]
            else:
                return list(data)

        elif result.is_fixed_length:
            # Expect exactly N items
            target_count = result.count

            if not isinstance(data, (list, tuple)):
                # Single item to list
                data = [data]
            else:
                data = list(data)

            # Pad or truncate to target count
            if len(data) < target_count:
                # Pad with None or zeros
                padding = [None] * (target_count - len(data))
                data.extend(padding)
            elif len(data) > target_count:
                # Truncate
                data = data[:target_count]

            return data

        return data


# Convenience functions for common operations
def parse_spec(spec: str) -> MultiplicityParseResult:
    """Parse a multiplicity specification."""
    return Multiplicity.parse(spec)


def make_spec(concept: str, multiplicity: Optional[Union[int, bool]] = None) -> str:
    """Create a multiplicity specification."""
    return Multiplicity.make_spec(concept, multiplicity)


def is_compatible(input_spec: str, output_spec: str) -> bool:
    """Check if two specifications are compatible."""
    return Multiplicity.is_compatible(input_spec, output_spec)


def normalize_data(data: Any, spec: str) -> Any:
    """Normalize data to match a specification."""
    return Multiplicity.normalize_data(data, spec)