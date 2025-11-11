"""Unit tests for the operators module."""

import pytest

from riveter.operators import (
    AttributeResolutionError,
    ListOperator,
    NestedAttributeResolver,
    NumericOperator,
    OperatorFactory,
    RegexOperator,
)


class TestNumericOperator:
    """Test cases for the NumericOperator class."""

    def test_numeric_operator_initialization(self):
        """Test NumericOperator initialization with valid operators."""
        for op in ["gt", "lt", "gte", "lte", "ne", "eq"]:
            operator = NumericOperator(op)
            assert operator.operator == op

    def test_numeric_operator_invalid_operator(self):
        """Test NumericOperator initialization with invalid operator."""
        with pytest.raises(ValueError, match="Invalid numeric operator: invalid"):
            NumericOperator("invalid")

    def test_numeric_operator_greater_than(self):
        """Test greater than operator."""
        operator = NumericOperator("gt")

        assert operator.evaluate(10, 5) is True
        assert operator.evaluate(5, 10) is False
        assert operator.evaluate(5, 5) is False
        assert operator.evaluate(10.5, 10) is True

    def test_numeric_operator_less_than(self):
        """Test less than operator."""
        operator = NumericOperator("lt")

        assert operator.evaluate(5, 10) is True
        assert operator.evaluate(10, 5) is False
        assert operator.evaluate(5, 5) is False
        assert operator.evaluate(9.5, 10) is True

    def test_numeric_operator_greater_than_equal(self):
        """Test greater than or equal operator."""
        operator = NumericOperator("gte")

        assert operator.evaluate(10, 5) is True
        assert operator.evaluate(5, 5) is True
        assert operator.evaluate(5, 10) is False

    def test_numeric_operator_less_than_equal(self):
        """Test less than or equal operator."""
        operator = NumericOperator("lte")

        assert operator.evaluate(5, 10) is True
        assert operator.evaluate(5, 5) is True
        assert operator.evaluate(10, 5) is False

    def test_numeric_operator_not_equal(self):
        """Test not equal operator."""
        operator = NumericOperator("ne")

        assert operator.evaluate(5, 10) is True
        assert operator.evaluate(10, 5) is True
        assert operator.evaluate(5, 5) is False

    def test_numeric_operator_equal(self):
        """Test equal operator."""
        operator = NumericOperator("eq")

        assert operator.evaluate(5, 5) is True
        assert operator.evaluate(5, 10) is False
        assert operator.evaluate(10, 5) is False

    def test_numeric_operator_string_numbers(self):
        """Test numeric operator with string representations of numbers."""
        operator = NumericOperator("gt")

        assert operator.evaluate("10", "5") is True
        assert operator.evaluate("5", "10") is False
        assert operator.evaluate("10.5", "10") is True

    def test_numeric_operator_none_values(self):
        """Test numeric operator with None values."""
        operator = NumericOperator("gt")

        assert operator.evaluate(None, 5) is False
        assert operator.evaluate(10, None) is False

    def test_numeric_operator_invalid_values(self):
        """Test numeric operator with non-numeric values."""
        operator = NumericOperator("gt")

        assert operator.evaluate("not_a_number", 5) is False
        assert operator.evaluate(5, "not_a_number") is False

    def test_numeric_operator_error_message(self):
        """Test numeric operator error messages."""
        operator = NumericOperator("gt")
        message = operator.get_error_message(5, 10)
        assert "Expected 5 > 10, but condition failed" in message


class TestRegexOperator:
    """Test cases for the RegexOperator class."""

    def test_regex_operator_simple_match(self):
        """Test regex operator with simple pattern matching."""
        operator = RegexOperator()

        assert operator.evaluate("hello", "hello") is True
        assert operator.evaluate("hello", "world") is False

    def test_regex_operator_pattern_matching(self):
        """Test regex operator with pattern matching."""
        operator = RegexOperator()

        # Test pattern matching
        assert operator.evaluate("test123", r"test\d+") is True
        assert operator.evaluate("test", r"test\d+") is False

        # Test case sensitivity
        assert operator.evaluate("Hello", "hello") is False
        assert operator.evaluate("Hello", r"(?i)hello") is True

    def test_regex_operator_complex_patterns(self):
        """Test regex operator with complex patterns."""
        operator = RegexOperator()

        # Email pattern
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        assert operator.evaluate("test@example.com", email_pattern) is True
        assert operator.evaluate("invalid-email", email_pattern) is False

        # Instance type pattern
        instance_pattern = r"^(t3|m5|c5)\.(large|xlarge)$"
        assert operator.evaluate("t3.large", instance_pattern) is True
        assert operator.evaluate("t2.micro", instance_pattern) is False

    def test_regex_operator_none_value(self):
        """Test regex operator with None value."""
        operator = RegexOperator()

        assert operator.evaluate(None, "pattern") is False

    def test_regex_operator_non_string_value(self):
        """Test regex operator with non-string values."""
        operator = RegexOperator()

        # Should convert to string
        assert operator.evaluate(123, r"\d+") is True
        assert operator.evaluate(123, "123") is True

    def test_regex_operator_invalid_pattern(self):
        """Test regex operator with invalid regex pattern."""
        operator = RegexOperator()

        # Invalid regex pattern should return False
        assert operator.evaluate("test", "[invalid") is False

    def test_regex_operator_error_message(self):
        """Test regex operator error messages."""
        operator = RegexOperator()
        message = operator.get_error_message("test", "pattern")
        assert "Value 'test' does not match pattern 'pattern'" in message


class TestListOperator:
    """Test cases for the ListOperator class."""

    def test_list_operator_initialization(self):
        """Test ListOperator initialization with valid operations."""
        for op in ["contains", "length", "subset"]:
            operator = ListOperator(op)
            assert operator.operation == op

    def test_list_operator_invalid_operation(self):
        """Test ListOperator initialization with invalid operation."""
        with pytest.raises(ValueError, match="Invalid list operation: invalid"):
            ListOperator("invalid")

    def test_list_operator_contains(self):
        """Test contains operation."""
        operator = ListOperator("contains")

        assert operator.evaluate(["a", "b", "c"], "b") is True
        assert operator.evaluate(["a", "b", "c"], "d") is False
        assert operator.evaluate(("a", "b", "c"), "b") is True
        assert operator.evaluate("not_a_list", "b") is False

    def test_list_operator_length_exact(self):
        """Test length operation with exact value."""
        operator = ListOperator("length")

        assert operator.evaluate(["a", "b", "c"], 3) is True
        assert operator.evaluate(["a", "b"], 3) is False
        assert operator.evaluate("hello", 5) is True
        assert operator.evaluate("hello", 3) is False

    def test_list_operator_length_with_operators(self):
        """Test length operation with comparison operators."""
        operator = ListOperator("length")

        # Test with gte
        assert operator.evaluate(["a", "b", "c"], {"gte": 3}) is True
        assert operator.evaluate(["a", "b"], {"gte": 3}) is False

        # Test with lte
        assert operator.evaluate(["a", "b"], {"lte": 3}) is True
        assert operator.evaluate(["a", "b", "c", "d"], {"lte": 3}) is False

        # Test with multiple operators
        assert operator.evaluate(["a", "b", "c"], {"gte": 2, "lte": 5}) is True
        assert operator.evaluate(["a"], {"gte": 2, "lte": 5}) is False

    def test_list_operator_subset(self):
        """Test subset operation."""
        operator = ListOperator("subset")

        assert operator.evaluate(["a", "b", "c", "d"], ["b", "c"]) is True
        assert operator.evaluate(["a", "b"], ["b", "c"]) is False
        assert operator.evaluate(["a", "b", "c"], ["a", "b", "c"]) is True
        assert operator.evaluate("not_a_list", ["a"]) is False
        assert operator.evaluate(["a", "b"], "not_a_list") is False

    def test_list_operator_error_messages(self):
        """Test list operator error messages."""
        contains_op = ListOperator("contains")
        length_op = ListOperator("length")
        subset_op = ListOperator("subset")

        contains_msg = contains_op.get_error_message(["a", "b"], "c")
        assert "does not contain 'c'" in contains_msg

        length_msg = length_op.get_error_message(["a", "b"], 3)
        assert "List length 2 does not match expected 3" in length_msg

        subset_msg = subset_op.get_error_message(["a"], ["b"])
        assert "Expected subset ['b'] is not contained in ['a']" in subset_msg


class TestNestedAttributeResolver:
    """Test cases for the NestedAttributeResolver class."""

    def test_resolve_simple_path(self):
        """Test resolving simple attribute paths."""
        resolver = NestedAttributeResolver()
        obj = {"name": "test", "value": 42}

        assert resolver.resolve_path(obj, "name") == "test"
        assert resolver.resolve_path(obj, "value") == 42
        assert resolver.resolve_path(obj, "missing") is None

    def test_resolve_nested_path(self):
        """Test resolving nested attribute paths."""
        resolver = NestedAttributeResolver()
        obj = {
            "root_block_device": {"volume_size": 100, "volume_type": "gp3"},
            "tags": {"Environment": "production"},
        }

        assert resolver.resolve_path(obj, "root_block_device.volume_size") == 100
        assert resolver.resolve_path(obj, "root_block_device.volume_type") == "gp3"
        assert resolver.resolve_path(obj, "tags.Environment") == "production"
        assert resolver.resolve_path(obj, "root_block_device.missing") is None

    def test_resolve_array_index_path(self):
        """Test resolving paths with array indices."""
        resolver = NestedAttributeResolver()
        obj = {
            "security_groups": ["sg-123", "sg-456"],
            "network_interfaces": [
                {"device_index": 0, "subnet_id": "subnet-123"},
                {"device_index": 1, "subnet_id": "subnet-456"},
            ],
        }

        assert resolver.resolve_path(obj, "security_groups[0]") == "sg-123"
        assert resolver.resolve_path(obj, "security_groups[1]") == "sg-456"
        assert resolver.resolve_path(obj, "network_interfaces[0].device_index") == 0
        assert resolver.resolve_path(obj, "network_interfaces[1].subnet_id") == "subnet-456"
        assert resolver.resolve_path(obj, "security_groups[2]") is None  # Out of bounds

    def test_resolve_complex_nested_path(self):
        """Test resolving complex nested paths."""
        resolver = NestedAttributeResolver()
        obj = {
            "instances": [
                {
                    "id": "i-123",
                    "tags": {"Name": "web-server-1"},
                    "block_devices": [{"device_name": "/dev/sda1", "volume_size": 20}],
                },
                {
                    "id": "i-456",
                    "tags": {"Name": "web-server-2"},
                    "block_devices": [{"device_name": "/dev/sda1", "volume_size": 30}],
                },
            ]
        }

        assert resolver.resolve_path(obj, "instances[0].id") == "i-123"
        assert resolver.resolve_path(obj, "instances[0].tags.Name") == "web-server-1"
        assert resolver.resolve_path(obj, "instances[1].block_devices[0].volume_size") == 30

    def test_resolve_empty_path(self):
        """Test resolving empty path."""
        resolver = NestedAttributeResolver()
        obj = {"test": "value"}

        assert resolver.resolve_path(obj, "") == obj

    def test_resolve_invalid_array_index(self):
        """Test resolving paths with invalid array indices."""
        resolver = NestedAttributeResolver()
        obj = {"items": ["a", "b", "c"]}

        with pytest.raises(AttributeResolutionError):
            resolver.resolve_path(obj, "items[invalid]")

    def test_resolve_unclosed_bracket(self):
        """Test resolving paths with unclosed brackets."""
        resolver = NestedAttributeResolver()
        obj = {"items": ["a", "b", "c"]}

        with pytest.raises(AttributeResolutionError):
            resolver.resolve_path(obj, "items[0")

    def test_path_exists(self):
        """Test path existence checking."""
        resolver = NestedAttributeResolver()
        obj = {"existing": {"nested": "value"}, "array": ["item1", "item2"]}

        assert resolver.path_exists(obj, "existing") is True
        assert resolver.path_exists(obj, "existing.nested") is True
        assert resolver.path_exists(obj, "array[0]") is True
        assert resolver.path_exists(obj, "missing") is False
        assert resolver.path_exists(obj, "existing.missing") is False
        assert resolver.path_exists(obj, "array[5]") is False

    def test_parse_path_components(self):
        """Test path parsing into components."""
        resolver = NestedAttributeResolver()

        # Simple path
        assert resolver._parse_path("name") == ["name"]

        # Nested path
        assert resolver._parse_path("root.child") == ["root", "child"]

        # Array index
        assert resolver._parse_path("items[0]") == ["items", 0]

        # Complex path
        assert resolver._parse_path("root.items[1].name") == ["root", "items", 1, "name"]


class TestOperatorFactory:
    """Test cases for the OperatorFactory class."""

    def test_create_numeric_operators(self):
        """Test creating numeric operators."""
        for op in ["gt", "lt", "gte", "lte", "ne", "eq"]:
            operator = OperatorFactory.create_operator(op)
            assert isinstance(operator, NumericOperator)
            assert operator.operator == op

    def test_create_regex_operator(self):
        """Test creating regex operator."""
        operator = OperatorFactory.create_operator("regex")
        assert isinstance(operator, RegexOperator)

    def test_create_list_operators(self):
        """Test creating list operators."""
        for op in ["contains", "length", "subset"]:
            operator = OperatorFactory.create_operator(op)
            assert isinstance(operator, ListOperator)
            assert operator.operation == op

    def test_create_operator_from_dict(self):
        """Test creating operators from dictionary configuration."""
        # Numeric operator
        operator = OperatorFactory.create_operator({"gt": 10})
        assert isinstance(operator, NumericOperator)
        assert operator.operator == "gt"

        # Regex operator
        operator = OperatorFactory.create_operator({"regex": "pattern"})
        assert isinstance(operator, RegexOperator)

        # List operator
        operator = OperatorFactory.create_operator({"contains": "item"})
        assert isinstance(operator, ListOperator)
        assert operator.operation == "contains"

    def test_create_operator_invalid_string(self):
        """Test creating operator with invalid string."""
        with pytest.raises(ValueError, match="Unknown operator: invalid"):
            OperatorFactory.create_operator("invalid")

    def test_create_operator_invalid_dict(self):
        """Test creating operator with invalid dictionary."""
        with pytest.raises(ValueError, match="Invalid operator configuration"):
            OperatorFactory.create_operator({"invalid": "value"})

        with pytest.raises(ValueError, match="Invalid operator configuration"):
            OperatorFactory.create_operator({"gt": 10, "lt": 5})  # Multiple keys

    def test_create_operator_invalid_type(self):
        """Test creating operator with invalid type."""
        with pytest.raises(ValueError, match="Invalid operator configuration type"):
            OperatorFactory.create_operator(123)

        with pytest.raises(ValueError, match="Invalid operator configuration type"):
            OperatorFactory.create_operator(["list", "not", "supported"])
