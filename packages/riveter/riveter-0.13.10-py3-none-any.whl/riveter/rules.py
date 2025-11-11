"""Rule parsing and validation.

This module handles the loading, parsing, and validation of Riveter rules.
Rules are defined in YAML format and specify how to validate Terraform
resources using advanced operators and assertions.

The module provides:
- Rule class for representing individual validation rules
- AssertionResult class for detailed assertion outcomes
- Severity enumeration for rule importance levels
- Rule loading and validation functions
- Support for advanced operators and nested attribute access

Rule Format:
    rules:
      - id: unique-rule-identifier
        resource_type: aws_instance
        description: Human-readable description
        severity: error|warning|info
        filter:
          # Conditions that determine if rule applies
          tags.Environment: production
        assert:
          # Assertions that must be true
          instance_type:
            regex: "^(t3|m5)\\.(large|xlarge)$"
          root_block_device.volume_size:
            gte: 100

Example:
    # Load rules from file
    rules = load_rules("security-rules.yml")

    # Create rule programmatically
    rule = Rule({
        "id": "test-rule",
        "resource_type": "aws_instance",
        "assert": {"instance_type": {"eq": "t3.large"}}
    })

    # Validate resource against rule
    if rule.matches_resource(resource):
        results = rule.validate_assertions(resource)
"""

from enum import Enum
from typing import Any, Dict, List, Optional

import yaml

from .exceptions import FileSystemError, RuleValidationError, handle_error_with_recovery
from .logging import debug, error, info, warning
from .operators import AttributeResolutionError, NestedAttributeResolver, OperatorFactory


class Severity(Enum):
    """Rule severity levels for categorizing validation importance.

    Severity levels help users prioritize validation results and filter
    output based on the importance of different rule violations.

    Attributes:
        ERROR: Critical violations that must be addressed (highest priority)
        WARNING: Best practice violations that should be addressed
        INFO: Informational checks for awareness (lowest priority)

    Example:
        # Create a rule with ERROR severity
        rule = Rule({
            "id": "critical-security-rule",
            "resource_type": "aws_instance",
            "severity": "error",
            "assert": {"instance_type": {"ne": "t1.micro"}}
        })

        # Filter results by severity
        error_results = [r for r in results if r.severity == Severity.ERROR]
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Rule:
    """Represents a single validation rule for Terraform resources.

    A Rule defines how to validate a specific aspect of Terraform resources
    using filters to determine applicability and assertions to check properties.
    Rules support advanced operators for sophisticated validation logic.

    Attributes:
        id: Unique identifier for the rule
        resource_type: Terraform resource type this rule applies to (or "*" for all)
        description: Human-readable description of what the rule checks
        filter: Conditions that determine if the rule applies to a resource
        assert_conditions: Assertions that must be true for the rule to pass
        severity: Importance level (ERROR, WARNING, or INFO)
        metadata: Additional metadata about the rule
        resolver: Helper for resolving nested attribute paths

    Example:
        rule_dict = {
            "id": "ec2-instance-type-check",
            "resource_type": "aws_instance",
            "description": "Ensure EC2 instances use approved instance types",
            "severity": "error",
            "filter": {
                "tags.Environment": "production"
            },
            "assert": {
                "instance_type": {
                    "regex": "^(t3|m5|c5)\\.(large|xlarge)$"
                }
            }
        }
        rule = Rule(rule_dict)
    """

    def __init__(self, rule_dict: Dict[str, Any], rule_file: Optional[str] = None):
        """Initialize a rule from dictionary definition.

        Validates the rule definition and creates a Rule object with all
        necessary components for resource validation.

        Args:
            rule_dict: Dictionary containing rule definition with required
                      fields: id, resource_type, assert. Optional fields:
                      description, filter, severity, metadata
            rule_file: Optional path to the file containing this rule,
                      used for error reporting and debugging

        Raises:
            RuleValidationError: When rule definition is invalid, missing
                               required fields, or contains invalid operators

        Example:
            rule = Rule({
                "id": "my-rule",
                "resource_type": "aws_instance",
                "assert": {"instance_type": "t3.large"}
            })
        """
        self.rule_file = rule_file

        try:
            # Validate required fields first
            self._validate_required_fields(rule_dict)

            self.id = rule_dict["id"]
            self.resource_type = rule_dict["resource_type"]
            self.description = rule_dict.get("description", "No description provided")
            self.filter = rule_dict.get("filter", {})
            self.assert_conditions = rule_dict["assert"]
            self.severity = self._parse_severity(rule_dict.get("severity", "error"))
            self.metadata = rule_dict.get("metadata", {})

            # Initialize helper objects
            self.resolver = NestedAttributeResolver()

            # Validate the rule during initialization
            self._validate_rule()

            debug(
                "Rule initialized successfully", rule_id=self.id, resource_type=self.resource_type
            )

        except RuleValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise RuleValidationError(
                f"Failed to initialize rule: {str(e)}",
                rule_id=rule_dict.get("id", "unknown"),
                rule_file=rule_file,
                suggestions=[
                    "Check the rule definition syntax",
                    "Ensure all required fields are present",
                    "Verify that field values are of the correct type",
                ],
            ) from e

    def _validate_required_fields(self, rule_dict: Dict[str, Any]) -> None:
        """Validate that all required fields are present."""
        required_fields = ["id", "resource_type", "assert"]
        missing_fields = []

        for field in required_fields:
            if field not in rule_dict:
                missing_fields.append(field)

        if missing_fields:
            raise RuleValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                rule_id=rule_dict.get("id", "unknown"),
                rule_file=self.rule_file,
                suggestions=[
                    f"Add the missing field(s): {', '.join(missing_fields)}",
                    "Check the rule definition against the schema",
                    "Ensure the rule follows the correct format",
                ],
            )

        # Validate field types
        if not isinstance(rule_dict["id"], str) or not rule_dict["id"].strip():
            raise RuleValidationError(
                "Rule 'id' must be a non-empty string",
                rule_id=rule_dict.get("id", "unknown"),
                rule_file=self.rule_file,
                suggestions=[
                    "Provide a unique, descriptive rule ID",
                    "Use alphanumeric characters and hyphens/underscores",
                    "Ensure the ID is not empty or just whitespace",
                ],
            )

        if (
            not isinstance(rule_dict["resource_type"], str)
            or not rule_dict["resource_type"].strip()
        ):
            raise RuleValidationError(
                "Rule 'resource_type' must be a non-empty string",
                rule_id=rule_dict["id"],
                rule_file=self.rule_file,
                suggestions=[
                    "Specify a valid Terraform resource type (e.g., 'aws_instance')",
                    "Check the resource type spelling and format",
                    "Ensure the resource type matches your Terraform configuration",
                ],
            )

        if not isinstance(rule_dict["assert"], dict) or not rule_dict["assert"]:
            raise RuleValidationError(
                "Rule 'assert' must be a non-empty dictionary",
                rule_id=rule_dict["id"],
                rule_file=self.rule_file,
                suggestions=[
                    "Add at least one assertion condition",
                    "Use the format: 'assert: { property: expected_value }'",
                    "Check the assertion syntax and structure",
                ],
            )

    def _parse_severity(self, severity_str: str) -> Severity:
        """Parse severity string into Severity enum."""
        if not isinstance(severity_str, str):
            raise RuleValidationError(
                f"Severity must be a string, got {type(severity_str).__name__}",
                rule_id=self.id,
                rule_file=self.rule_file,
                suggestions=[
                    "Use one of: 'error', 'warning', 'info'",
                    "Ensure the severity value is quoted in YAML",
                    "Check for typos in the severity value",
                ],
            )

        try:
            return Severity(severity_str.lower())
        except ValueError as e:
            raise RuleValidationError(
                f"Invalid severity '{severity_str}'. Must be one of: error, warning, info",
                rule_id=self.id,
                rule_file=self.rule_file,
                field_path="severity",
                suggestions=[
                    "Use 'error' for critical violations",
                    "Use 'warning' for best practice violations",
                    "Use 'info' for informational checks",
                    "Check for typos in the severity value",
                ],
            ) from e

    def _validate_rule(self) -> None:
        """Validate the rule definition for correct operator usage."""
        try:
            self._validate_assertions(self.assert_conditions)
            self._validate_filter_conditions(self.filter)
        except RuleValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            raise RuleValidationError(
                f"Rule validation failed: {str(e)}",
                rule_id=self.id,
                rule_file=self.rule_file,
                suggestions=[
                    "Check the rule syntax and structure",
                    "Verify that all operators are used correctly",
                    "Ensure property paths are valid",
                ],
            ) from e

    def _validate_assertions(self, assertions: Dict[str, Any], path: str = "") -> None:
        """Recursively validate assertion structure and operators."""
        if not isinstance(assertions, dict):
            raise RuleValidationError(
                f"Assertions must be a dictionary, got {type(assertions).__name__}",
                rule_id=self.id,
                rule_file=self.rule_file,
                field_path=path or "assert",
                suggestions=[
                    "Use dictionary format for assertions: { property: expected_value }",
                    "Check the indentation and structure of the assert block",
                    "Ensure each assertion is a key-value pair",
                ],
            )

        for key, value in assertions.items():
            current_path = f"{path}.{key}" if path else key

            if not isinstance(key, str):
                raise RuleValidationError(
                    f"Assertion property name must be a string, got {type(key).__name__}",
                    rule_id=self.id,
                    rule_file=self.rule_file,
                    field_path=current_path,
                    suggestions=[
                        "Use string property names for assertions",
                        "Check for proper YAML quoting if needed",
                        "Ensure property names are valid identifiers",
                    ],
                )

            if isinstance(value, dict):
                # Check if this is an operator configuration
                if self._is_operator_config(value):
                    try:
                        # Validate each operator in the configuration
                        for op_key, op_value in value.items():
                            if op_key in {
                                "gt",
                                "lt",
                                "gte",
                                "lte",
                                "ne",
                                "eq",
                                "regex",
                                "contains",
                                "length",
                                "subset",
                            }:
                                try:
                                    OperatorFactory.create_operator({op_key: op_value})
                                except Exception as op_error:
                                    raise RuleValidationError(
                                        (
                                            f"Invalid operator '{op_key}' configuration: "
                                            f"{str(op_error)}"
                                        ),
                                        rule_id=self.id,
                                        rule_file=self.rule_file,
                                        field_path=f"{current_path}.{op_key}",
                                        suggestions=[
                                            f"Check the value for operator '{op_key}'",
                                            "Ensure the operator value is of the correct type",
                                            "Refer to the operator documentation for valid formats",
                                        ],
                                    ) from op_error
                            else:
                                available_ops = [
                                    "gt",
                                    "lt",
                                    "gte",
                                    "lte",
                                    "ne",
                                    "eq",
                                    "regex",
                                    "contains",
                                    "length",
                                    "subset",
                                ]
                                raise RuleValidationError(
                                    f"Unknown operator '{op_key}' at '{current_path}'",
                                    rule_id=self.id,
                                    rule_file=self.rule_file,
                                    field_path=f"{current_path}.{op_key}",
                                    suggestions=[
                                        (
                                            f"Use one of the available operators: "
                                            f"{', '.join(available_ops)}"
                                        ),
                                        "Check for typos in the operator name",
                                        "Refer to the documentation for supported operators",
                                    ],
                                )
                    except RuleValidationError:
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        raise RuleValidationError(
                            f"Operator validation failed at '{current_path}': {str(e)}",
                            rule_id=self.id,
                            rule_file=self.rule_file,
                            field_path=current_path,
                            suggestions=[
                                "Check the operator configuration syntax",
                                "Ensure operator values are properly formatted",
                                "Verify that the operator is supported",
                            ],
                        ) from e
                else:
                    # Recursively validate nested assertions
                    try:
                        self._validate_assertions(value, current_path)
                    except RuleValidationError:
                        # Re-raise with context preserved
                        raise
            elif isinstance(value, str):
                # Check for special string operators
                if value in ["present"]:
                    continue  # These are valid
                elif not value.strip():
                    raise RuleValidationError(
                        f"Empty string value at '{current_path}'",
                        rule_id=self.id,
                        rule_file=self.rule_file,
                        field_path=current_path,
                        suggestions=[
                            "Provide a non-empty expected value",
                            "Use 'present' to check for property existence",
                            "Remove empty assertions or provide valid values",
                        ],
                    )
            elif value is None:
                raise RuleValidationError(
                    f"Null value at '{current_path}' - use 'present' to check existence",
                    rule_id=self.id,
                    rule_file=self.rule_file,
                    field_path=current_path,
                    suggestions=[
                        "Use 'present' to check if a property exists",
                        "Provide an expected value instead of null",
                        "Remove the assertion if it's not needed",
                    ],
                )
            # Other primitive values (numbers, booleans, lists) are considered valid

    def _validate_filter_conditions(self, filter_config: Dict[str, Any]) -> None:
        """Validate filter conditions structure."""
        if not filter_config:
            return  # Empty filter is valid

        if not isinstance(filter_config, dict):
            raise RuleValidationError(
                f"Filter must be a dictionary, got {type(filter_config).__name__}",
                rule_id=self.id,
                rule_file=self.rule_file,
                field_path="filter",
                suggestions=[
                    "Use dictionary format for filters: { property: expected_value }",
                    "Check the indentation and structure of the filter block",
                    "Ensure each filter condition is a key-value pair",
                ],
            )

        # Validate filter conditions using similar logic to assertions
        try:
            self._validate_assertions(filter_config, "filter")
        except RuleValidationError as e:
            # Re-raise with filter context
            raise RuleValidationError(
                f"Invalid filter condition: {e.message}",
                rule_id=self.id,
                rule_file=self.rule_file,
                field_path=e.field_path,
                suggestions=e.suggestions,
            ) from e

    def _is_operator_config(self, value: Dict[str, Any]) -> bool:
        """Check if a dictionary represents an operator configuration."""
        operator_keys = {
            "gt",
            "lt",
            "gte",
            "lte",
            "ne",
            "eq",
            "regex",
            "contains",
            "length",
            "subset",
        }
        # Check if any key is an operator key, or if it looks like it should be an operator
        return any(key in operator_keys for key in value.keys()) or any(
            key.endswith("_op") for key in value.keys()
        )

    def matches_resource(self, resource: Dict[str, Any]) -> bool:
        """Check if a resource matches this rule's filters.

        Evaluates all filter conditions against the resource to determine
        if this rule should be applied. If no filters are defined, the
        rule matches all resources of the correct type.

        Args:
            resource: Resource dictionary from Terraform configuration

        Returns:
            True if the resource matches all filter conditions, False otherwise

        Example:
            resource = {
                "resource_type": "aws_instance",
                "tags": {"Environment": "production"},
                "instance_type": "t3.large"
            }

            # Rule with filter
            rule = Rule({
                "id": "prod-rule",
                "resource_type": "aws_instance",
                "filter": {"tags.Environment": "production"},
                "assert": {"instance_type": "t3.large"}
            })

            assert rule.matches_resource(resource) == True
        """
        if not self.filter:
            return True

        return self._evaluate_filter(self.filter, resource)

    def _evaluate_filter(self, filter_config: Dict[str, Any], resource: Dict[str, Any]) -> bool:
        """Evaluate filter conditions against a resource."""
        for key, expected in filter_config.items():
            try:
                actual = self.resolver.resolve_path(resource, key)

                if isinstance(expected, dict):
                    # Handle operator-based filtering
                    if self._is_operator_config(expected):
                        operator = OperatorFactory.create_operator(expected)
                        op_key = list(expected.keys())[0]
                        op_value = expected[op_key]
                        if not operator.evaluate(actual, op_value):
                            return False
                    else:
                        # Nested filter conditions
                        if not isinstance(actual, dict):
                            return False
                        if not self._evaluate_filter(expected, actual):
                            return False
                else:
                    # Handle special values and direct comparison
                    if expected == "present":
                        if actual is None:
                            return False
                    elif actual != expected:
                        return False

            except AttributeResolutionError:
                return False

        return True

    def validate_assertions(self, resource: Dict[str, Any]) -> List["AssertionResult"]:
        """Validate all assertions against a resource and return detailed results.

        Executes all assertion conditions defined in the rule against the
        provided resource, using the advanced operator framework for
        sophisticated comparisons.

        Args:
            resource: Resource dictionary from Terraform configuration

        Returns:
            List of AssertionResult objects, one for each assertion evaluated.
            Each result contains detailed information about what was tested
            and whether it passed or failed.

        Example:
            rule = Rule({
                "id": "test-rule",
                "resource_type": "aws_instance",
                "assert": {
                    "instance_type": {"regex": "^t3\\.(large|xlarge)$"},
                    "tags.Environment": "production"
                }
            })

            resource = {
                "resource_type": "aws_instance",
                "instance_type": "t3.large",
                "tags": {"Environment": "production"}
            }

            results = rule.validate_assertions(resource)
            assert len(results) == 2
            assert all(r.passed for r in results)
        """
        results: List["AssertionResult"] = []
        self._validate_assertion_group(self.assert_conditions, resource, results)
        return results

    def _validate_assertion_group(
        self,
        assertions: Dict[str, Any],
        resource: Dict[str, Any],
        results: List["AssertionResult"],
        path_prefix: str = "",
    ) -> None:
        """Recursively validate a group of assertions."""
        for key, expected in assertions.items():
            property_path = f"{path_prefix}.{key}" if path_prefix else key

            try:
                # Handle nested assertions like tags.Environment
                if isinstance(expected, dict) and not self._is_operator_config(expected):
                    # This is a nested group - recurse into it
                    self._validate_assertion_group(expected, resource, results, property_path)
                    continue

                actual = self.resolver.resolve_path(resource, property_path)

                if isinstance(expected, dict):
                    if self._is_operator_config(expected):
                        # Handle multiple operator-based assertions for the same property
                        for op_key, op_value in expected.items():
                            if op_key in {
                                "gt",
                                "lt",
                                "gte",
                                "lte",
                                "ne",
                                "eq",
                                "regex",
                                "contains",
                                "length",
                                "subset",
                            }:
                                operator = OperatorFactory.create_operator({op_key: op_value})

                                passed = operator.evaluate(actual, op_value)
                                message = (
                                    "Assertion passed"
                                    if passed
                                    else operator.get_error_message(actual, op_value)
                                )

                                results.append(
                                    AssertionResult(
                                        property_path=property_path,
                                        operator=op_key,
                                        expected=op_value,
                                        actual=actual,
                                        passed=passed,
                                        message=message,
                                    )
                                )
                    else:
                        # Nested assertions - recurse
                        if isinstance(actual, dict):
                            self._validate_assertion_group(expected, actual, results, property_path)
                        else:
                            results.append(
                                AssertionResult(
                                    property_path=property_path,
                                    operator="nested",
                                    expected=expected,
                                    actual=actual,
                                    passed=False,
                                    message=(
                                        f"Expected nested object at '{property_path}' "
                                        f"but got {type(actual).__name__}"
                                    ),
                                )
                            )
                else:
                    # Direct value comparison or special handling
                    if expected == "present":
                        passed = actual is not None
                        if passed:
                            message = "Property is present"
                        else:
                            # Format message to match old behavior
                            if property_path.startswith("tags."):
                                tag_name = property_path.split(".", 1)[1]
                                message = f"Required tag '{tag_name}' is missing"
                            else:
                                message = f"Property '{property_path}' is missing"
                    else:
                        passed = actual == expected
                        if passed:
                            message = "Values match"
                        else:
                            # Format message to match old behavior
                            if property_path.startswith("tags."):
                                tag_name = property_path.split(".", 1)[1]
                                message = (
                                    f"Tag '{tag_name}' has value '{actual}' "
                                    f"but expected '{expected}'"
                                )
                            else:
                                message = (
                                    f"Property '{property_path}' has value '{actual}' "
                                    f"but expected '{expected}'"
                                )

                    results.append(
                        AssertionResult(
                            property_path=property_path,
                            operator="eq" if expected != "present" else "present",
                            expected=expected,
                            actual=actual,
                            passed=passed,
                            message=message,
                        )
                    )

            except AttributeResolutionError as e:
                results.append(
                    AssertionResult(
                        property_path=property_path,
                        operator="unknown",
                        expected=expected,
                        actual=None,
                        passed=False,
                        message=f"Failed to resolve path: {str(e)}",
                    )
                )


class AssertionResult:
    """Represents the result of a single assertion evaluation.

    This class captures detailed information about each individual assertion
    within a rule, providing granular feedback about what passed or failed
    and why.

    Attributes:
        property_path: The path to the property being tested (e.g., "tags.Environment")
        operator: The operator used for comparison (e.g., "eq", "gt", "regex")
        expected: The expected value from the rule definition
        actual: The actual value found in the resource
        passed: Whether this assertion passed (True) or failed (False)
        message: Human-readable description of the result

    Example:
        result = AssertionResult(
            property_path="instance_type",
            operator="regex",
            expected="^(t3|m5)\\.(large|xlarge)$",
            actual="t2.micro",
            passed=False,
            message="Value 't2.micro' does not match pattern '^(t3|m5)\\.(large|xlarge)$'"
        )
    """

    def __init__(
        self,
        property_path: str,
        operator: str,
        expected: Any,
        actual: Any,
        passed: bool,
        message: str,
    ):
        """Initialize an AssertionResult.

        Args:
            property_path: The path to the property being tested
            operator: The operator used for comparison
            expected: The expected value from the rule definition
            actual: The actual value found in the resource
            passed: Whether this assertion passed
            message: Human-readable description of the result
        """
        self.property_path = property_path
        self.operator = operator
        self.expected = expected
        self.actual = actual
        self.passed = passed
        self.message = message


def load_rules(rules_file: str) -> List[Rule]:
    """Load and validate rules from a YAML file.

    Reads a YAML file containing rule definitions, validates the file structure
    and individual rules, and returns a list of Rule objects. The function
    includes comprehensive error handling and recovery mechanisms.

    Expected file format:
        rules:
          - id: unique-rule-id
            resource_type: aws_instance
            description: Human-readable description
            severity: error|warning|info
            filter:
              # Optional conditions for rule applicability
              tags.Environment: production
            assert:
              # Required assertions
              instance_type:
                regex: "^(t3|m5)\\.(large|xlarge)$"
              root_block_device.volume_size:
                gte: 100

    Args:
        rules_file: Path to the YAML file containing rule definitions.
                   File must exist and be readable.

    Returns:
        List of validated Rule objects. Empty list if file contains no rules.
        Invalid rules are skipped with warnings logged.

    Raises:
        FileSystemError: When the file cannot be read, doesn't exist, or
                        has encoding issues
        RuleValidationError: When the file structure is invalid or contains
                           critical rule definition errors that prevent loading

    Example:
        # Load rules from file
        rules = load_rules("security-rules.yml")

        # Use rules for validation
        for rule in rules:
            if rule.matches_resource(resource):
                results = rule.validate_assertions(resource)
    """
    info("Loading rules from file", file_path=rules_file)

    try:
        # Check if file exists and is readable
        from pathlib import Path

        rules_path = Path(rules_file)

        if not rules_path.exists():
            raise FileSystemError(
                f"Rules file not found: {rules_file}",
                file_path=rules_file,
                operation="read",
                suggestions=[
                    "Check that the file path is correct",
                    "Ensure the file exists in the specified location",
                    "Verify you have read permissions for the file",
                ],
            )

        if not rules_path.is_file():
            raise FileSystemError(
                f"Path is not a file: {rules_file}",
                file_path=rules_file,
                operation="read",
                suggestions=[
                    "Ensure the path points to a file, not a directory",
                    "Check that the file extension is correct (.yml or .yaml)",
                ],
            )

        debug("Reading rules file", file_path=rules_file, file_size=rules_path.stat().st_size)

        # Read and parse the YAML file
        try:
            with open(rules_file, "r", encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    warning("Rules file is empty", file_path=rules_file)
                    return []

                data = yaml.safe_load(content)

        except UnicodeDecodeError as e:
            raise FileSystemError(
                f"File encoding error in {rules_file}: {str(e)}",
                file_path=rules_file,
                operation="read",
                suggestions=[
                    "Ensure the file is saved with UTF-8 encoding",
                    "Check for binary content or special characters",
                    "Try opening the file in a text editor to verify content",
                ],
            ) from e
        except yaml.YAMLError as e:
            line_info = ""
            if hasattr(e, "problem_mark") and e.problem_mark:
                line_info = (
                    f" at line {e.problem_mark.line + 1}, column {e.problem_mark.column + 1}"
                )

            raise RuleValidationError(
                f"YAML parsing error in {rules_file}{line_info}: {str(e)}",
                rule_file=rules_file,
                suggestions=[
                    "Check YAML syntax and indentation",
                    "Ensure all quotes and brackets are properly closed",
                    "Verify that lists and dictionaries are correctly formatted",
                    "Use a YAML validator to check the file structure",
                ],
            ) from e
        except Exception as e:
            raise FileSystemError(
                f"Unexpected error reading rules file {rules_file}: {str(e)}",
                file_path=rules_file,
                operation="read",
                suggestions=[
                    "Check file permissions and accessibility",
                    "Ensure sufficient disk space and memory",
                    "Try with a different file or smaller rule set",
                ],
            ) from e

        # Validate file structure
        if data is None:
            warning("Rules file contains no data", file_path=rules_file)
            return []

        if not isinstance(data, dict):
            raise RuleValidationError(
                (
                    f"Invalid rules file format: root element must be a dictionary, "
                    f"got {type(data).__name__}"
                ),
                rule_file=rules_file,
                suggestions=[
                    "Ensure the file starts with a dictionary structure",
                    "Check that the file contains 'rules:' at the top level",
                    "Verify the YAML structure is correct",
                ],
            )

        if "rules" not in data:
            available_keys = list(data.keys()) if data else []
            raise RuleValidationError(
                (
                    f"Invalid rules file format: must contain a 'rules' key. "
                    f"Found keys: {available_keys}"
                ),
                rule_file=rules_file,
                suggestions=[
                    "Add a 'rules:' section to the file",
                    "Check the file structure against the expected format",
                    "Ensure the rules are nested under a 'rules' key",
                ],
            )

        if not isinstance(data["rules"], list):
            raise RuleValidationError(
                f"Invalid rules format: 'rules' must be a list, got {type(data['rules']).__name__}",
                rule_file=rules_file,
                suggestions=[
                    "Format rules as a YAML list using '-' for each rule",
                    "Check that each rule is properly indented",
                    "Ensure the rules section contains a list of rule definitions",
                ],
            )

        if not data["rules"]:
            warning("Rules file contains no rules", file_path=rules_file)
            return []

        # Process each rule
        rules = []
        rule_ids = set()

        for i, rule_dict in enumerate(data["rules"]):
            try:
                if not isinstance(rule_dict, dict):
                    raise RuleValidationError(
                        f"Rule at index {i} must be a dictionary, got {type(rule_dict).__name__}",
                        rule_file=rules_file,
                        suggestions=[
                            f"Check rule #{i + 1} in the file",
                            "Ensure each rule is a dictionary with key-value pairs",
                            "Verify proper YAML indentation and structure",
                        ],
                    )

                # Check for duplicate rule IDs
                rule_id = rule_dict.get("id")
                if rule_id and rule_id in rule_ids:
                    raise RuleValidationError(
                        f"Duplicate rule ID '{rule_id}' found",
                        rule_id=rule_id,
                        rule_file=rules_file,
                        suggestions=[
                            "Ensure each rule has a unique ID",
                            "Check for copy-paste errors in rule definitions",
                            "Use descriptive, unique identifiers for each rule",
                        ],
                    )

                if rule_id:
                    rule_ids.add(rule_id)

                # Create the rule (this will validate it)
                try:
                    rule = Rule(rule_dict, rules_file)
                    rules.append(rule)

                    debug(
                        "Rule loaded successfully",
                        rule_id=rule.id,
                        resource_type=rule.resource_type,
                        severity=rule.severity.value,
                    )
                except RuleValidationError as rule_error:
                    # Try to recover from rule validation errors
                    rule_id = rule_dict.get("id", f"rule_at_index_{i}")
                    error("Rule validation failed", rule_id=rule_id, error=str(rule_error))

                    try:
                        handle_error_with_recovery(rule_error)
                    except RuleValidationError:
                        # If recovery fails, continue with next rule
                        warning("Skipping invalid rule", rule_id=rule_id)
                        continue

            except Exception as e:
                # Handle unexpected errors during rule creation
                rule_id = (
                    rule_dict.get("id", f"rule_at_index_{i}")
                    if isinstance(rule_dict, dict)
                    else f"rule_at_index_{i}"
                )
                error("Failed to create rule", rule_id=rule_id, error=str(e))

                try:
                    handle_error_with_recovery(
                        RuleValidationError(
                            f"Failed to create rule {rule_id}: {str(e)}",
                            rule_id=rule_id,
                            rule_file=rules_file,
                            suggestions=[
                                f"Check the definition of rule '{rule_id}'",
                                "Verify all required fields are present and correctly formatted",
                                "Check for syntax errors in the rule definition",
                            ],
                        )
                    )
                except RuleValidationError:
                    # If recovery fails, continue with next rule
                    warning("Skipping problematic rule", rule_id=rule_id)
                    continue

        info(
            "Rules loading completed",
            file_path=rules_file,
            total_rules=len(rules),
            unique_resource_types=len(set(rule.resource_type for rule in rules)),
        )

        return rules

    except (FileSystemError, RuleValidationError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise FileSystemError(
            f"Unexpected error loading rules from {rules_file}: {str(e)}",
            file_path=rules_file,
            operation="read",
            suggestions=[
                "Check file permissions and accessibility",
                "Ensure the file is a valid YAML file",
                "Try with a different rules file",
            ],
        ) from e
