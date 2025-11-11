"""Comparison operators for advanced rule validation."""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Union


class ComparisonOperator(ABC):
    """Base class for all comparison operators."""

    @abstractmethod
    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate the comparison between actual and expected values.

        Args:
            actual: The actual value from the resource
            expected: The expected value from the rule

        Returns:
            True if the comparison passes, False otherwise
        """
        pass

    @abstractmethod
    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get a descriptive error message for failed comparisons.

        Args:
            actual: The actual value from the resource
            expected: The expected value from the rule

        Returns:
            A descriptive error message
        """
        pass


class NumericOperator(ComparisonOperator):
    """Handles numerical comparison operations."""

    def __init__(self, operator: str):
        """Initialize with a specific operator.

        Args:
            operator: One of 'gt', 'lt', 'gte', 'lte', 'ne', 'eq'
        """
        self.operator = operator
        self.operator_symbols = {
            "gt": ">",
            "lt": "<",
            "gte": ">=",
            "lte": "<=",
            "ne": "!=",
            "eq": "==",
        }

        if operator not in self.operator_symbols:
            raise ValueError(f"Invalid numeric operator: {operator}")

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate numerical comparison."""
        try:
            # Convert to numbers for comparison
            actual_num = float(actual) if actual is not None else None
            expected_num = float(expected)

            if actual_num is None:
                return False

            if self.operator == "gt":
                return actual_num > expected_num
            elif self.operator == "lt":
                return actual_num < expected_num
            elif self.operator == "gte":
                return actual_num >= expected_num
            elif self.operator == "lte":
                return actual_num <= expected_num
            elif self.operator == "ne":
                return actual_num != expected_num
            elif self.operator == "eq":
                return actual_num == expected_num

        except (ValueError, TypeError):
            return False

        return False

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed numerical comparison."""
        symbol = self.operator_symbols[self.operator]
        return f"Expected {actual} {symbol} {expected}, but condition failed"


class RegexOperator(ComparisonOperator):
    """Handles regular expression pattern matching."""

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate regex pattern matching."""
        if actual is None:
            return False

        try:
            # Convert actual to string for regex matching
            actual_str = str(actual)
            pattern = str(expected)
            return bool(re.match(pattern, actual_str))
        except re.error:
            return False

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed regex matching."""
        return f"Value '{actual}' does not match pattern '{expected}'"


class ListOperator(ComparisonOperator):
    """Handles list-based operations."""

    def __init__(self, operation: str):
        """Initialize with a specific list operation.

        Args:
            operation: One of 'contains', 'length', 'subset'
        """
        self.operation = operation

        if operation not in ["contains", "length", "subset"]:
            raise ValueError(f"Invalid list operation: {operation}")

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate list operations."""
        if self.operation == "contains":
            return self._evaluate_contains(actual, expected)
        elif self.operation == "length":
            return self._evaluate_length(actual, expected)
        elif self.operation == "subset":
            return self._evaluate_subset(actual, expected)

        return False

    def _evaluate_contains(self, actual: Any, expected: Any) -> bool:
        """Check if actual list contains expected value."""
        if not isinstance(actual, (list, tuple)):
            return False
        return expected in actual

    def _evaluate_length(self, actual: Any, expected: Any) -> bool:
        """Check list length against expected criteria."""
        if not isinstance(actual, (list, tuple, str)):
            return False

        actual_length = len(actual)

        # Handle different expected formats
        if isinstance(expected, int):
            return actual_length == expected
        elif isinstance(expected, dict):
            # Support operators like {'gte': 5, 'lte': 10}
            for op, value in expected.items():
                numeric_op = NumericOperator(op)
                if not numeric_op.evaluate(actual_length, value):
                    return False
            return True

        return False

    def _evaluate_subset(self, actual: Any, expected: Any) -> bool:
        """Check if expected is a subset of actual."""
        if not isinstance(actual, (list, tuple)) or not isinstance(expected, (list, tuple)):
            return False

        # Handle unhashable types (like dicts) by using a different approach
        try:
            return set(expected).issubset(set(actual))
        except TypeError:
            # If we can't use sets (due to unhashable types), check manually
            for expected_item in expected:
                if expected_item not in actual:
                    return False
            return True

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed list operations."""
        if self.operation == "contains":
            return f"List {actual} does not contain '{expected}'"
        elif self.operation == "length":
            if isinstance(actual, (list, tuple, str)):
                return f"List length {len(actual)} does not match expected {expected}"
            else:
                return f"Value '{actual}' is not a list/string for length check"
        elif self.operation == "subset":
            return f"Expected subset {expected} is not contained in {actual}"

        return f"List operation '{self.operation}' failed"


class OperatorFactory:
    """Factory class for creating appropriate operators."""

    @staticmethod
    def create_operator(operator_config: Union[str, Dict[str, Any]]) -> ComparisonOperator:
        """Create an operator based on configuration.

        Args:
            operator_config: String operator name or dict with operator details

        Returns:
            Appropriate ComparisonOperator instance
        """
        if isinstance(operator_config, str):
            # Simple string operators
            if operator_config in ["gt", "lt", "gte", "lte", "ne", "eq"]:
                return NumericOperator(operator_config)
            elif operator_config == "regex":
                return RegexOperator()
            elif operator_config in ["contains", "length", "subset"]:
                return ListOperator(operator_config)
            else:
                raise ValueError(f"Unknown operator: {operator_config}")

        elif isinstance(operator_config, dict):
            # Dict-based operator configuration
            if len(operator_config) == 1:
                op_name = list(operator_config.keys())[0]
                if op_name in ["gt", "lt", "gte", "lte", "ne", "eq"]:
                    return NumericOperator(op_name)
                elif op_name == "regex":
                    return RegexOperator()
                elif op_name in ["contains", "length", "subset"]:
                    return ListOperator(op_name)

            raise ValueError(f"Invalid operator configuration: {operator_config}")

        else:
            raise ValueError(f"Invalid operator configuration type: {type(operator_config)}")


class NestedAttributeResolver:
    """Handles resolution of nested object attributes using dot notation."""

    def resolve_path(self, obj: Dict[str, Any], path: str) -> Any:
        """Resolve a dot-notation path in a nested object.

        Args:
            obj: The object to traverse
            path: Dot-notation path like 'root_block_device.volume_size' or 'tags[0].name'

        Returns:
            The value at the specified path, or None if path doesn't exist

        Raises:
            AttributeResolutionError: If path is invalid or cannot be resolved
        """
        if not path:
            return obj

        try:
            current: Any = obj
            parts = self._parse_path(path)

            for part in parts:
                if isinstance(part, str):
                    # Regular attribute access
                    if isinstance(current, dict):
                        current = current.get(part)
                    else:
                        return None
                elif isinstance(part, int):
                    # Array index access
                    if isinstance(current, (list, tuple)) and 0 <= part < len(current):
                        current = current[part]
                    else:
                        return None

                if current is None:
                    return None

            return current

        except Exception as e:
            raise AttributeResolutionError(f"Failed to resolve path '{path}': {str(e)}") from e

    def _parse_path(self, path: str) -> List[Union[str, int]]:
        """Parse a dot-notation path into components.

        Args:
            path: Path like 'root_block_device.volume_size' or 'security_groups[0].name'

        Returns:
            List of path components (strings for attributes, ints for array indices)
        """
        parts: List[Union[str, int]] = []
        current_part = ""
        i = 0

        while i < len(path):
            char = path[i]

            if char == ".":
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            elif char == "[":
                # Handle array index
                if current_part:
                    parts.append(current_part)
                    current_part = ""

                # Find the closing bracket
                j = i + 1
                while j < len(path) and path[j] != "]":
                    j += 1

                if j >= len(path):
                    raise ValueError(f"Unclosed bracket in path: {path}")

                # Extract and parse the index
                index_str = path[i + 1 : j]
                try:
                    index = int(index_str)
                    parts.append(index)
                except ValueError as e:
                    raise ValueError(f"Invalid array index '{index_str}' in path: {path}") from e

                i = j  # Skip to closing bracket
            else:
                current_part += char

            i += 1

        # Add the last part if it exists
        if current_part:
            parts.append(current_part)

        return parts

    def path_exists(self, obj: Dict[str, Any], path: str) -> bool:
        """Check if a path exists in the object without raising exceptions.

        Args:
            obj: The object to check
            path: Dot-notation path to check

        Returns:
            True if path exists, False otherwise
        """
        try:
            result = self.resolve_path(obj, path)
            return result is not None
        except AttributeResolutionError:
            return False


class AttributeResolutionError(Exception):
    """Exception raised when attribute resolution fails."""

    pass
