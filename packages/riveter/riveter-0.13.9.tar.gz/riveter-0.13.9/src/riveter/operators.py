"""Comparison operators for advanced rule validation.

This module provides a modern, extensible operator system with:
- Protocol-based interfaces for type safety
- Comprehensive operator implementations
- Performance optimizations
- Extensible operator registry
- Detailed error reporting
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Protocol, runtime_checkable

from .logging import debug, warning


@runtime_checkable
class ComparisonOperatorProtocol(Protocol):
    """Protocol for comparison operators."""

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate the comparison between actual and expected values.

        Args:
            actual: The actual value from the resource
            expected: The expected value from the rule

        Returns:
            True if the comparison passes, False otherwise
        """
        ...

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get a descriptive error message for failed comparisons.

        Args:
            actual: The actual value from the resource
            expected: The expected value from the rule

        Returns:
            A descriptive error message
        """
        ...

    def get_operator_name(self) -> str:
        """Get the operator name for registration and debugging."""
        ...

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        ...


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

    @abstractmethod
    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get a descriptive error message for failed comparisons.

        Args:
            actual: The actual value from the resource
            expected: The expected value from the rule

        Returns:
            A descriptive error message
        """

    def get_operator_name(self) -> str:
        """Get the operator name for registration and debugging."""
        return self.__class__.__name__.lower().replace("operator", "")

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        _ = value_type  # Mark as intentionally unused
        return True  # Base implementation supports all types


class NumericOperator(ComparisonOperator):
    """Handles numerical comparison operations with enhanced type safety."""

    def __init__(self, operator: str) -> None:
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
        """Evaluate numerical comparison with enhanced error handling."""
        try:
            # Convert to numbers for comparison
            actual_num = self._to_number(actual)
            expected_num = self._to_number(expected)

            if actual_num is None:
                debug(f"Numeric operator {self.operator}: actual value '{actual}' is not numeric")
                return False

            if expected_num is None:
                warning(
                    f"Numeric operator {self.operator}: expected value '{expected}' is not numeric"
                )
                return False

            result = self._compare_numbers(actual_num, expected_num)
            debug(
                f"Numeric comparison: {actual_num} "
                f"{self.operator_symbols[self.operator]} {expected_num} = {result}"
            )
            return result

        except (ValueError, TypeError) as e:
            debug(f"Numeric operator {self.operator} evaluation failed: {e!s}")
            return False

    def _to_number(self, value: Any) -> float | None:
        """Convert value to number with comprehensive type handling."""
        if value is None:
            return None

        if isinstance(value, int | float):
            return float(value)

        if isinstance(value, str):
            # Handle common string representations
            value = value.strip()
            if not value:
                return None

            # Handle boolean strings
            if value.lower() in ("true", "false"):
                return float(value.lower() == "true")

            try:
                return float(value)
            except ValueError:
                return None

        if isinstance(value, bool):
            return float(value)

        # Try to extract numeric value from complex types
        if hasattr(value, "__float__"):
            try:
                return float(value)
            except (ValueError, TypeError):
                pass

        return None

    def _compare_numbers(self, actual: float, expected: float) -> bool:
        """Perform the actual numeric comparison."""
        if self.operator == "gt":
            return actual > expected
        if self.operator == "lt":
            return actual < expected
        if self.operator == "gte":
            return actual >= expected
        if self.operator == "lte":
            return actual <= expected
        if self.operator == "ne":
            return actual != expected
        if self.operator == "eq":
            return actual == expected
        return False

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed numerical comparison."""
        symbol = self.operator_symbols[self.operator]
        return f"Expected {actual} {symbol} {expected}, but condition failed"

    def get_operator_name(self) -> str:
        """Get the operator name."""
        return self.operator

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        return value_type in (int, float, str, bool) or hasattr(value_type, "__float__")


class RegexOperator(ComparisonOperator):
    """Handles regular expression pattern matching with caching and validation."""

    def __init__(self):
        """Initialize regex operator with pattern cache."""
        self._pattern_cache: dict[str, re.Pattern] = {}

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate regex pattern matching with caching."""
        if actual is None:
            debug("Regex operator: actual value is None")
            return False

        try:
            # Convert actual to string for regex matching
            actual_str = str(actual)
            pattern_str = str(expected)

            # Get compiled pattern from cache
            pattern = self._get_compiled_pattern(pattern_str)
            if pattern is None:
                warning(f"Regex operator: invalid pattern '{pattern_str}'")
                return False

            result = bool(pattern.match(actual_str))
            debug(f"Regex match: '{actual_str}' against '{pattern_str}' = {result}")
            return result

        except Exception as e:
            debug(f"Regex operator evaluation failed: {e!s}")
            return False

    def _get_compiled_pattern(self, pattern_str: str) -> re.Pattern | None:
        """Get compiled regex pattern with caching."""
        if pattern_str in self._pattern_cache:
            return self._pattern_cache[pattern_str]

        try:
            compiled_pattern = re.compile(pattern_str)
            self._pattern_cache[pattern_str] = compiled_pattern
            return compiled_pattern
        except re.error as e:
            debug(f"Failed to compile regex pattern '{pattern_str}': {e!s}")
            return None

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed regex matching."""
        return f"Value '{actual}' does not match pattern '{expected}'"

    def get_operator_name(self) -> str:
        """Get the operator name."""
        return "regex"

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        _ = value_type  # Mark as intentionally unused
        return True  # Can convert any type to string for regex matching


class ListOperator(ComparisonOperator):
    """Handles list-based operations with enhanced type support."""

    def __init__(self, operation: str) -> None:
        """Initialize with a specific list operation.

        Args:
            operation: One of 'contains', 'length', 'subset', 'empty', 'unique'
        """
        self.operation = operation
        self.valid_operations = ["contains", "length", "subset", "empty", "unique"]

        if operation not in self.valid_operations:
            raise ValueError(
                f"Invalid list operation: {operation}. Valid operations: {self.valid_operations}"
            )

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate list operations with comprehensive type handling."""
        try:
            if self.operation == "contains":
                return self._evaluate_contains(actual, expected)
            if self.operation == "length":
                return self._evaluate_length(actual, expected)
            if self.operation == "subset":
                return self._evaluate_subset(actual, expected)
            if self.operation == "empty":
                return self._evaluate_empty(actual, expected)
            if self.operation == "unique":
                return self._evaluate_unique(actual, expected)
        except Exception as e:
            debug(f"List operator {self.operation} evaluation failed: {e!s}")
            return False

        return False

    def _evaluate_contains(self, actual: Any, expected: Any) -> bool:
        """Check if actual list contains expected value with type flexibility."""
        if not self._is_iterable(actual):
            debug(f"Contains check: actual value '{actual}' is not iterable")
            return False

        # Handle string containment
        if isinstance(actual, str) and isinstance(expected, str):
            return expected in actual

        # Handle list/tuple containment
        if isinstance(actual, list | tuple):
            return expected in actual

        # Handle dict containment (check keys)
        if isinstance(actual, dict):
            return expected in actual

        return False

    def _evaluate_length(self, actual: Any, expected: Any) -> bool:
        """Check length against expected criteria with flexible comparison."""
        if not hasattr(actual, "__len__"):
            debug(f"Length check: actual value '{actual}' has no length")
            return False

        actual_length = len(actual)
        debug(f"Length check: actual length = {actual_length}, expected = {expected}")

        # Handle different expected formats
        if isinstance(expected, int):
            return actual_length == expected
        if isinstance(expected, dict):
            # Support operators like {'gte': 5, 'lte': 10}
            for op, value in expected.items():
                try:
                    numeric_op = NumericOperator(op)
                    if not numeric_op.evaluate(actual_length, value):
                        return False
                except ValueError:
                    warning(f"Invalid numeric operator '{op}' in length check")
                    return False
            return True
        if isinstance(expected, str):
            # Handle string representations of numbers
            try:
                expected_int = int(expected)
                return actual_length == expected_int
            except ValueError:
                return False

        return False

    def _evaluate_subset(self, actual: Any, expected: Any) -> bool:
        """Check if expected is a subset of actual with robust type handling."""
        if not self._is_iterable(actual) or not self._is_iterable(expected):
            debug("Subset check: one or both values are not iterable")
            return False

        # Convert to lists for consistent handling
        actual_list = list(actual) if not isinstance(actual, list | tuple) else actual
        expected_list = list(expected) if not isinstance(expected, list | tuple) else expected

        # Handle unhashable types by manual checking
        try:
            return set(expected_list).issubset(set(actual_list))
        except TypeError:
            # Manual check for unhashable types
            return all(expected_item in actual_list for expected_item in expected_list)

    def _evaluate_empty(self, actual: Any, expected: Any) -> bool:
        """Check if collection is empty."""
        if not hasattr(actual, "__len__"):
            return False

        is_empty = len(actual) == 0
        expected_empty = bool(expected) if expected is not None else True

        return is_empty == expected_empty

    def _evaluate_unique(self, actual: Any, expected: Any) -> bool:
        """Check if all items in collection are unique."""
        if not self._is_iterable(actual):
            return False

        actual_list = list(actual)
        has_unique_items = len(actual_list) == len(set(actual_list))
        expected_unique = bool(expected) if expected is not None else True

        return has_unique_items == expected_unique

    def _is_iterable(self, value: Any) -> bool:
        """Check if value is iterable (but not string for some operations)."""
        try:
            iter(value)
            return True
        except TypeError:
            return False

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed list operations."""
        if self.operation == "contains":
            return f"Collection {actual} does not contain '{expected}'"
        if self.operation == "length":
            if hasattr(actual, "__len__"):
                return f"Collection length {len(actual)} does not match expected {expected}"
            return f"Value '{actual}' has no length for length check"
        if self.operation == "subset":
            return f"Expected subset {expected} is not contained in {actual}"
        if self.operation == "empty":
            if hasattr(actual, "__len__"):
                is_empty = len(actual) == 0
                return (
                    f"Collection is {'empty' if is_empty else 'not empty'} "
                    f"but expected {'empty' if expected else 'not empty'}"
                )
            return f"Value '{actual}' cannot be checked for emptiness"
        if self.operation == "unique":
            return "Collection uniqueness check failed"

        return f"List operation '{self.operation}' failed"

    def get_operator_name(self) -> str:
        """Get the operator name."""
        return self.operation

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        if self.operation in ["contains", "subset", "empty", "unique"]:
            return hasattr(value_type, "__iter__") or hasattr(value_type, "__len__")
        if self.operation == "length":
            return hasattr(value_type, "__len__")
        return False


class OperatorRegistry:
    """Registry for managing available operators with extensibility support."""

    def __init__(self):
        """Initialize the operator registry with default operators."""
        self._operators: dict[str, type[ComparisonOperator]] = {}
        self._register_default_operators()

    def _register_default_operators(self) -> None:
        """Register all default operators."""
        # Numeric operators
        for op in ["gt", "lt", "gte", "lte", "ne", "eq"]:
            self._operators[op] = lambda op=op: NumericOperator(op)

        # Regex operator
        self._operators["regex"] = RegexOperator

        # List operators
        for op in ["contains", "length", "subset", "empty", "unique"]:
            self._operators[op] = lambda op=op: ListOperator(op)

    def register_operator(self, name: str, operator_class: type[ComparisonOperator]) -> None:
        """Register a custom operator.

        Args:
            name: Operator name
            operator_class: Operator class to register
        """
        if not issubclass(operator_class, ComparisonOperator):
            raise TypeError("Operator class must inherit from ComparisonOperator")

        self._operators[name] = operator_class
        debug(f"Registered custom operator: {name}")

    def get_operator(self, name: str) -> ComparisonOperator:
        """Get an operator instance by name.

        Args:
            name: Operator name

        Returns:
            Operator instance

        Raises:
            ValueError: If operator is not registered
        """
        if name not in self._operators:
            available = list(self._operators.keys())
            raise ValueError(f"Unknown operator: {name}. Available operators: {available}")

        operator_factory = self._operators[name]
        if callable(operator_factory):
            return operator_factory()
        return operator_factory

    def list_operators(self) -> list[str]:
        """Get list of all registered operator names."""
        return list(self._operators.keys())

    def is_registered(self, name: str) -> bool:
        """Check if an operator is registered."""
        return name in self._operators


# Global operator registry instance
_operator_registry = OperatorRegistry()


class OperatorFactory:
    """Factory class for creating appropriate operators with enhanced extensibility."""

    @staticmethod
    def create_operator(operator_config: str | dict[str, Any]) -> ComparisonOperator:
        """Create an operator based on configuration.

        Args:
            operator_config: String operator name or dict with operator details

        Returns:
            Appropriate ComparisonOperator instance

        Raises:
            ValueError: If operator configuration is invalid
        """
        try:
            if isinstance(operator_config, str):
                # Simple string operators
                return _operator_registry.get_operator(operator_config)

            if isinstance(operator_config, dict):
                # Dict-based operator configuration
                if len(operator_config) == 1:
                    op_name = next(iter(operator_config.keys()))
                    return _operator_registry.get_operator(op_name)
                raise ValueError(
                    f"Operator configuration dict must have exactly one key, "
                    f"got {len(operator_config)}"
                )

            raise ValueError(
                f"Invalid operator configuration type: {type(operator_config)}. "
                f"Expected str or dict."
            )

        except Exception as e:
            available_operators = _operator_registry.list_operators()
            raise ValueError(
                f"Failed to create operator from config {operator_config}: {e!s}. "
                f"Available operators: {available_operators}"
            ) from e

    @staticmethod
    def register_operator(name: str, operator_class: type[ComparisonOperator]) -> None:
        """Register a custom operator globally.

        Args:
            name: Operator name
            operator_class: Operator class to register
        """
        _operator_registry.register_operator(name, operator_class)

    @staticmethod
    def list_operators() -> list[str]:
        """Get list of all available operator names."""
        return _operator_registry.list_operators()

    @staticmethod
    def is_operator_available(name: str) -> bool:
        """Check if an operator is available."""
        return _operator_registry.is_registered(name)


class NestedAttributeResolver:
    """Handles resolution of nested object attributes using dot notation."""

    def resolve_path(self, obj: dict[str, Any], path: str) -> Any:
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
                    if isinstance(current, list | tuple) and 0 <= part < len(current):
                        current = current[part]
                    else:
                        return None

                if current is None:
                    return None

            return current

        except Exception as e:
            raise AttributeResolutionError(f"Failed to resolve path '{path}': {e!s}") from e

    def _parse_path(self, path: str) -> list[str | int]:
        """Parse a dot-notation path into components.

        Args:
            path: Path like 'root_block_device.volume_size' or 'security_groups[0].name'

        Returns:
            List of path components (strings for attributes, ints for array indices)
        """
        parts: list[str | int] = []
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

    def path_exists(self, obj: dict[str, Any], path: str) -> bool:
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


class DateOperator(ComparisonOperator):
    """Handles date and time comparisons."""

    def __init__(self, operation: str) -> None:
        """Initialize with a specific date operation.

        Args:
            operation: One of 'before', 'after', 'between', 'age_days'
        """
        self.operation = operation
        self.valid_operations = ["before", "after", "between", "age_days"]

        if operation not in self.valid_operations:
            raise ValueError(
                f"Invalid date operation: {operation}. Valid operations: {self.valid_operations}"
            )

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate date operations."""
        try:
            from datetime import datetime

            # Parse actual date
            actual_date = self._parse_date(actual)
            if actual_date is None:
                return False

            if self.operation == "before":
                expected_date = self._parse_date(expected)
                return actual_date < expected_date if expected_date else False
            if self.operation == "after":
                expected_date = self._parse_date(expected)
                return actual_date > expected_date if expected_date else False
            if self.operation == "between":
                if not isinstance(expected, list | tuple) or len(expected) != 2:
                    return False
                start_date = self._parse_date(expected[0])
                end_date = self._parse_date(expected[1])
                if not start_date or not end_date:
                    return False
                return start_date <= actual_date <= end_date
            if self.operation == "age_days":
                now = datetime.now()
                age_days = (now - actual_date).days
                if isinstance(expected, dict):
                    # Support operators like {'gte': 30, 'lte': 90}
                    for op, value in expected.items():
                        numeric_op = NumericOperator(op)
                        if not numeric_op.evaluate(age_days, value):
                            return False
                    return True
                return age_days == int(expected)

        except Exception as e:
            debug(f"Date operator {self.operation} evaluation failed: {e!s}")
            return False

        return False

    def _parse_date(self, date_value: Any) -> Any:
        """Parse various date formats."""
        from datetime import datetime

        if date_value is None:
            return None

        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            # Try common date formats
            formats = [
                "%Y-%m-%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ",
                "%m/%d/%Y",
                "%d/%m/%Y",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

        return None

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed date operations."""
        return f"Date operation '{self.operation}' failed: {actual} vs {expected}"

    def get_operator_name(self) -> str:
        """Get the operator name."""
        return f"date_{self.operation}"

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        from datetime import datetime

        return value_type in (str, datetime) or hasattr(value_type, "strftime")


class NetworkOperator(ComparisonOperator):
    """Handles network-related validations like IP addresses and CIDR blocks."""

    def __init__(self, operation: str) -> None:
        """Initialize with a specific network operation.

        Args:
            operation: One of 'ip_in_cidr', 'valid_ip', 'private_ip', 'public_ip'
        """
        self.operation = operation
        self.valid_operations = ["ip_in_cidr", "valid_ip", "private_ip", "public_ip"]

        if operation not in self.valid_operations:
            raise ValueError(
                f"Invalid network operation: {operation}. Valid operations: {self.valid_operations}"
            )

    def evaluate(self, actual: Any, expected: Any) -> bool:
        """Evaluate network operations."""
        try:
            import ipaddress

            if self.operation == "valid_ip":
                try:
                    ipaddress.ip_address(str(actual))
                    return True
                except ValueError:
                    return False
            elif self.operation == "ip_in_cidr":
                try:
                    ip = ipaddress.ip_address(str(actual))
                    network = ipaddress.ip_network(str(expected), strict=False)
                    return ip in network
                except ValueError:
                    return False
            elif self.operation == "private_ip":
                try:
                    ip = ipaddress.ip_address(str(actual))
                    return ip.is_private
                except ValueError:
                    return False
            elif self.operation == "public_ip":
                try:
                    ip = ipaddress.ip_address(str(actual))
                    return not ip.is_private and not ip.is_loopback
                except ValueError:
                    return False

        except Exception as e:
            debug(f"Network operator {self.operation} evaluation failed: {e!s}")
            return False

        return False

    def get_error_message(self, actual: Any, expected: Any) -> str:
        """Get error message for failed network operations."""
        _ = expected  # Mark as intentionally unused
        return f"Network operation '{self.operation}' failed for value '{actual}'"

    def get_operator_name(self) -> str:
        """Get the operator name."""
        return f"network_{self.operation}"

    def supports_type(self, value_type: type) -> bool:
        """Check if operator supports the given value type."""
        return value_type in (str, bytes) or hasattr(value_type, "__str__")


# Register the new operators
def register_extended_operators():
    """Register extended operators with the global registry."""
    # Date operators
    for op in ["before", "after", "between", "age_days"]:
        # Create a proper class factory function
        def make_date_operator(operation=op):
            return lambda: DateOperator(operation)

        _operator_registry._operators[f"date_{op}"] = make_date_operator()

    # Network operators
    for op in ["ip_in_cidr", "valid_ip", "private_ip", "public_ip"]:
        # Create a proper class factory function
        def make_network_operator(operation=op):
            return lambda: NetworkOperator(operation)

        _operator_registry._operators[f"network_{op}"] = make_network_operator()


# Auto-register extended operators
register_extended_operators()
