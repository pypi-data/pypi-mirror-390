"""Rule parsing and validation.

This module handles the loading, parsing, and validation of Riveter rules.
Rules are defined in YAML format and specify how to validate Terraform
resources using advanced operators and assertions.

The module provides:
- Modern immutable Rule data structures with comprehensive type safety
- AssertionResult class for detailed assertion outcomes
- Rule loading and validation functions with structured error handling
- Support for advanced operators and nested attribute access
- Protocol-based interfaces for extensibility

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
    rule = create_rule_from_dict({
        "id": "test-rule",
        "resource_type": "aws_instance",
        "assert": {"instance_type": {"eq": "t3.large"}}
    })

    # Validate resource against rule
    if matches_resource_filter(rule, resource):
        results = validate_rule_assertions(rule, resource)
"""

from typing import Any

import yaml

from .exceptions import FileSystemError, RuleValidationError, handle_error_with_recovery
from .logging import debug, error, info, warning
from .models.core import Severity, TerraformResource
from .models.rules import Rule as ModernRule
from .models.rules import RuleAssertion, RuleCondition, RuleFilter, RuleMetadata, RuleScope
from .operators import AttributeResolutionError, NestedAttributeResolver, OperatorFactory

# Modern rule creation and validation functions


def create_rule_from_dict(rule_dict: dict[str, Any], rule_file: str | None = None) -> ModernRule:
    """Create an immutable Rule from dictionary definition.

    Validates the rule definition and creates a modern immutable Rule object
    with comprehensive type safety and structured error handling.

    Args:
        rule_dict: Dictionary containing rule definition with required
                  fields: id, resource_type, assert. Optional fields:
                  description, filter, severity, metadata
        rule_file: Optional path to the file containing this rule,
                  used for error reporting and debugging

    Returns:
        Immutable Rule object with validated structure

    Raises:
        RuleValidationError: When rule definition is invalid, missing
                           required fields, or contains invalid operators

    Example:
        rule = create_rule_from_dict({
            "id": "my-rule",
            "resource_type": "aws_instance",
            "assert": {"instance_type": "t3.large"}
        })
    """
    try:
        # Validate required fields first
        _validate_required_fields(rule_dict, rule_file)

        rule_id = rule_dict["id"]
        resource_type = rule_dict["resource_type"]
        description = rule_dict.get("description", "No description provided")
        severity = _parse_severity(rule_dict.get("severity", "error"), rule_id, rule_file)

        # Parse filter conditions
        filter_dict = rule_dict.get("filter", {})
        rule_filter = _parse_filter_conditions(filter_dict, rule_id, rule_file)

        # Parse assertion conditions
        assert_dict = rule_dict["assert"]
        rule_assertion = _parse_assertion_conditions(assert_dict, rule_id, rule_file)

        # Parse metadata
        metadata_dict = rule_dict.get("metadata", {})
        rule_metadata = _parse_rule_metadata(metadata_dict)

        # Create immutable rule
        rule = ModernRule(
            id=rule_id,
            description=description,
            resource_type=resource_type,
            severity=severity,
            scope=RuleScope.RESOURCE,
            filter=rule_filter,
            assertion=rule_assertion,
            metadata=rule_metadata,
            enabled=True,
        )

        debug(
            "Rule created successfully",
            rule_id=rule.id,
            resource_type=rule.resource_type,
            severity=rule.severity.value,
        )

        return rule

    except RuleValidationError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        raise RuleValidationError(
            f"Failed to create rule: {e!s}",
            rule_id=rule_dict.get("id", "unknown"),
            rule_file=rule_file,
            suggestions=[
                "Check the rule definition syntax",
                "Ensure all required fields are present",
                "Verify that field values are of the correct type",
            ],
        ) from e


def _validate_required_fields(rule_dict: dict[str, Any], rule_file: str | None) -> None:
    """Validate that all required fields are present and valid."""
    required_fields = ["id", "resource_type", "assert"]
    missing_fields = [field for field in required_fields if field not in rule_dict]

    if missing_fields:
        raise RuleValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            rule_id=rule_dict.get("id", "unknown"),
            rule_file=rule_file,
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
            rule_file=rule_file,
            suggestions=[
                "Provide a unique, descriptive rule ID",
                "Use alphanumeric characters and hyphens/underscores",
                "Ensure the ID is not empty or just whitespace",
            ],
        )

    if not isinstance(rule_dict["resource_type"], str) or not rule_dict["resource_type"].strip():
        raise RuleValidationError(
            "Rule 'resource_type' must be a non-empty string",
            rule_id=rule_dict["id"],
            rule_file=rule_file,
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
            rule_file=rule_file,
            suggestions=[
                "Add at least one assertion condition",
                "Use the format: 'assert: { property: expected_value }'",
                "Check the assertion syntax and structure",
            ],
        )


def _parse_severity(severity_str: str, rule_id: str, rule_file: str | None) -> Severity:
    """Parse severity string into Severity enum."""
    if not isinstance(severity_str, str):
        raise RuleValidationError(
            f"Severity must be a string, got {type(severity_str).__name__}",
            rule_id=rule_id,
            rule_file=rule_file,
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
            rule_id=rule_id,
            rule_file=rule_file,
            field_path="severity",
            suggestions=[
                "Use 'error' for critical violations",
                "Use 'warning' for best practice violations",
                "Use 'info' for informational checks",
                "Check for typos in the severity value",
            ],
        ) from e


def _parse_filter_conditions(
    filter_dict: dict[str, Any], rule_id: str, rule_file: str | None
) -> RuleFilter:
    """Parse filter conditions into RuleFilter object."""
    if not filter_dict:
        return RuleFilter()

    if not isinstance(filter_dict, dict):
        raise RuleValidationError(
            f"Filter must be a dictionary, got {type(filter_dict).__name__}",
            rule_id=rule_id,
            rule_file=rule_file,
            field_path="filter",
            suggestions=[
                "Use dictionary format for filters: { property: expected_value }",
                "Check the indentation and structure of the filter block",
                "Ensure each filter condition is a key-value pair",
            ],
        )

    conditions = []
    for field, value in filter_dict.items():
        try:
            condition = _parse_condition(field, value, rule_id, rule_file, "filter")
            conditions.append(condition)
        except RuleValidationError as e:
            # Re-raise with filter context
            raise RuleValidationError(
                f"Invalid filter condition: {e.message}",
                rule_id=rule_id,
                rule_file=rule_file,
                field_path=getattr(e, "field_path", f"filter.{field}"),
                suggestions=getattr(e, "suggestions", []),
            ) from e

    return RuleFilter(conditions=conditions, logic="AND")


def _parse_assertion_conditions(
    assert_dict: dict[str, Any], rule_id: str, rule_file: str | None
) -> RuleAssertion:
    """Parse assertion conditions into RuleAssertion object."""
    if not isinstance(assert_dict, dict):
        raise RuleValidationError(
            f"Assertions must be a dictionary, got {type(assert_dict).__name__}",
            rule_id=rule_id,
            rule_file=rule_file,
            field_path="assert",
            suggestions=[
                "Use dictionary format for assertions: { property: expected_value }",
                "Check the indentation and structure of the assert block",
                "Ensure each assertion is a key-value pair",
            ],
        )

    conditions = []
    for field, value in assert_dict.items():
        try:
            condition = _parse_condition(field, value, rule_id, rule_file, "assert")
            conditions.append(condition)
        except RuleValidationError:
            raise

    return RuleAssertion(conditions=conditions, logic="AND")


def _parse_condition(
    field: str, value: Any, rule_id: str, rule_file: str | None, context: str
) -> RuleCondition:
    """Parse a single condition from field and value."""
    if not isinstance(field, str):
        raise RuleValidationError(
            f"Condition field name must be a string, got {type(field).__name__}",
            rule_id=rule_id,
            rule_file=rule_file,
            field_path=f"{context}.{field}",
            suggestions=[
                "Use string property names for conditions",
                "Check for proper YAML quoting if needed",
                "Ensure property names are valid identifiers",
            ],
        )

    if isinstance(value, dict):
        # Check if this is an operator configuration
        if _is_operator_config(value):
            # For now, use the first operator found
            # TODO: Support multiple operators per condition
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
                        # Validate operator
                        OperatorFactory.create_operator({op_key: op_value})
                        return RuleCondition(
                            operator=op_key, field=field, value=op_value, negate=False
                        )
                    except Exception as op_error:
                        raise RuleValidationError(
                            f"Invalid operator '{op_key}' configuration: {op_error!s}",
                            rule_id=rule_id,
                            rule_file=rule_file,
                            field_path=f"{context}.{field}.{op_key}",
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
                        f"Unknown operator '{op_key}' at '{context}.{field}'",
                        rule_id=rule_id,
                        rule_file=rule_file,
                        field_path=f"{context}.{field}.{op_key}",
                        suggestions=[
                            f"Use one of the available operators: {', '.join(available_ops)}",
                            "Check for typos in the operator name",
                            "Refer to the documentation for supported operators",
                        ],
                    )
        # Handle nested conditions like {"tags": {"Environment": "production"}}
        elif field == "tags" and isinstance(value, dict):
            # Convert nested tag conditions to dot notation
            conditions = []
            for tag_name, tag_value in value.items():
                tag_field = f"tags.{tag_name}"
                tag_condition = _parse_condition(tag_field, tag_value, rule_id, rule_file, context)
                conditions.append(tag_condition)
            # For now, return the first condition (we could extend this to support multiple)
            return (
                conditions[0]
                if conditions
                else RuleCondition(operator="present", field=field, value=True, negate=False)
            )
        else:
            # Other nested conditions not supported in this simplified version
            raise RuleValidationError(
                f"Nested conditions not supported at '{context}.{field}'",
                rule_id=rule_id,
                rule_file=rule_file,
                field_path=f"{context}.{field}",
                suggestions=[
                    "Use operator-based conditions instead",
                    "Flatten nested conditions into separate rules",
                    "Use supported operators for complex conditions",
                ],
            )
    elif isinstance(value, str):
        # Handle special string operators
        if value == "present":
            return RuleCondition(operator="present", field=field, value=True, negate=False)
        if not value.strip():
            raise RuleValidationError(
                f"Empty string value at '{context}.{field}'",
                rule_id=rule_id,
                rule_file=rule_file,
                field_path=f"{context}.{field}",
                suggestions=[
                    "Provide a non-empty expected value",
                    "Use 'present' to check for property existence",
                    "Remove empty conditions or provide valid values",
                ],
            )
        # Direct string comparison
        return RuleCondition(operator="eq", field=field, value=value, negate=False)
    elif value is None:
        raise RuleValidationError(
            f"Null value at '{context}.{field}' - use 'present' to check existence",
            rule_id=rule_id,
            rule_file=rule_file,
            field_path=f"{context}.{field}",
            suggestions=[
                "Use 'present' to check if a property exists",
                "Provide an expected value instead of null",
                "Remove the condition if it's not needed",
            ],
        )
    else:
        # Direct value comparison (numbers, booleans, lists)
        return RuleCondition(operator="eq", field=field, value=value, negate=False)
    return None


def _parse_rule_metadata(metadata_dict: dict[str, Any]) -> RuleMetadata:
    """Parse rule metadata into RuleMetadata object."""
    return RuleMetadata(
        category=metadata_dict.get("category"),
        subcategory=metadata_dict.get("subcategory"),
        framework=metadata_dict.get("framework"),
        control_id=metadata_dict.get("control_id"),
        references=metadata_dict.get("references", []),
        tags=metadata_dict.get("tags", []),
        author=metadata_dict.get("author"),
        created_date=metadata_dict.get("created_date"),
        modified_date=metadata_dict.get("modified_date"),
        version=metadata_dict.get("version", "1.0"),
    )


def _is_operator_config(value: dict[str, Any]) -> bool:
    """Check if a dictionary represents an operator configuration."""
    operator_keys = {"gt", "lt", "gte", "lte", "ne", "eq", "regex", "contains", "length", "subset"}
    # Check if any key is an operator key, or if it looks like it should be an operator
    return any(key in operator_keys for key in value) or any(key.endswith("_op") for key in value)


def matches_resource_filter(rule: ModernRule, resource: TerraformResource) -> bool:
    """Check if a resource matches a rule's filter conditions.

    Evaluates all filter conditions against the resource to determine
    if this rule should be applied. If no filters are defined, the
    rule matches all resources of the correct type.

    Args:
        rule: Rule with filter conditions
        resource: Terraform resource to check

    Returns:
        True if the resource matches all filter conditions, False otherwise

    Example:
        resource = TerraformResource(
            type="aws_instance",
            name="web_server",
            attributes={
                "tags": {"Environment": "production"},
                "instance_type": "t3.large"
            }
        )

        # Rule with filter
        rule = create_rule_from_dict({
            "id": "prod-rule",
            "resource_type": "aws_instance",
            "filter": {"tags.Environment": "production"},
            "assert": {"instance_type": "t3.large"}
        })

        assert matches_resource_filter(rule, resource) == True
    """
    if rule.filter.is_empty:
        return True

    resolver = NestedAttributeResolver()

    for condition in rule.filter.conditions:
        try:
            actual = resolver.resolve_path(resource.attributes, condition.field)

            if condition.operator == "present":
                result = actual is not None
            elif condition.operator == "eq":
                result = actual == condition.value
            else:
                # Use operator factory for complex operators
                operator = OperatorFactory.create_operator({condition.operator: condition.value})
                result = operator.evaluate(actual, condition.value)

            # Apply negation if needed
            if condition.negate:
                result = not result

            # For AND logic, if any condition fails, return False
            if rule.filter.logic == "AND" and not result:
                return False
            # For OR logic, if any condition passes, we need to continue checking all
            if rule.filter.logic == "OR" and result:
                return True

        except AttributeResolutionError:
            # If we can't resolve the path, condition fails
            if rule.filter.logic == "AND":
                return False
            # For OR logic, continue to next condition

    # For AND logic, all conditions passed
    # For OR logic, no conditions passed
    return rule.filter.logic == "AND"


def validate_rule_assertions(
    rule: ModernRule, resource: TerraformResource
) -> list["AssertionResult"]:
    """Validate all assertions in a rule against a resource.

    Executes all assertion conditions defined in the rule against the
    provided resource, using the advanced operator framework for
    sophisticated comparisons.

    Args:
        rule: Rule with assertion conditions
        resource: Terraform resource to validate

    Returns:
        List of AssertionResult objects, one for each assertion evaluated.
        Each result contains detailed information about what was tested
        and whether it passed or failed.

    Example:
        rule = create_rule_from_dict({
            "id": "test-rule",
            "resource_type": "aws_instance",
            "assert": {
                "instance_type": {"regex": "^t3\\.(large|xlarge)$"},
                "tags.Environment": "production"
            }
        })

        resource = TerraformResource(
            type="aws_instance",
            name="web_server",
            attributes={
                "instance_type": "t3.large",
                "tags": {"Environment": "production"}
            }
        )

        results = validate_rule_assertions(rule, resource)
        assert len(results) == 2
        assert all(r.passed for r in results)
    """
    results: list[AssertionResult] = []
    resolver = NestedAttributeResolver()

    for condition in rule.assertion.conditions:
        try:
            actual = resolver.resolve_path(resource.attributes, condition.field)

            if condition.operator == "present":
                passed = actual is not None
                if passed:
                    message = "Property is present"
                # Format message to match old behavior
                elif condition.field.startswith("tags."):
                    tag_name = condition.field.split(".", 1)[1]
                    message = f"Required tag '{tag_name}' is missing"
                else:
                    message = f"Property '{condition.field}' is missing"
            elif condition.operator == "eq":
                passed = actual == condition.value
                if passed:
                    message = "Values match"
                # Format message to match old behavior
                elif condition.field.startswith("tags."):
                    tag_name = condition.field.split(".", 1)[1]
                    message = (
                        f"Tag '{tag_name}' has value '{actual}' "
                        f"but expected '{condition.value}'"
                    )
                else:
                    message = (
                        f"Property '{condition.field}' has value '{actual}' "
                        f"but expected '{condition.value}'"
                    )
            else:
                # Use operator factory for complex operators
                operator = OperatorFactory.create_operator({condition.operator: condition.value})
                passed = operator.evaluate(actual, condition.value)
                message = (
                    "Assertion passed"
                    if passed
                    else operator.get_error_message(actual, condition.value)
                )

            # Apply negation if needed
            if condition.negate:
                passed = not passed
                message = f"NOT ({message})"

            results.append(
                AssertionResult(
                    property_path=condition.field,
                    operator=condition.operator,
                    expected=condition.value,
                    actual=actual,
                    passed=passed,
                    message=message,
                )
            )

        except AttributeResolutionError as e:
            results.append(
                AssertionResult(
                    property_path=condition.field,
                    operator=condition.operator,
                    expected=condition.value,
                    actual=None,
                    passed=False,
                    message=f"Failed to resolve path: {e!s}",
                )
            )

    return results


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
    ) -> None:
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


def load_rules(rules_file: str) -> list[ModernRule]:
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
            with rules_path.open(encoding="utf-8") as f:
                content = f.read()
                if not content.strip():
                    warning("Rules file is empty", file_path=rules_file)
                    return []

                data = yaml.safe_load(content)

        except UnicodeDecodeError as e:
            raise FileSystemError(
                f"File encoding error in {rules_file}: {e!s}",
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
                f"YAML parsing error in {rules_file}{line_info}: {e!s}",
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
                f"Unexpected error reading rules file {rules_file}: {e!s}",
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
                    rule = create_rule_from_dict(rule_dict, rules_file)
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
                            f"Failed to create rule {rule_id}: {e!s}",
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
            unique_resource_types=len({rule.resource_type for rule in rules}),
        )

        return rules

    except (FileSystemError, RuleValidationError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Catch any other unexpected errors
        raise FileSystemError(
            f"Unexpected error loading rules from {rules_file}: {e!s}",
            file_path=rules_file,
            operation="read",
            suggestions=[
                "Check file permissions and accessibility",
                "Ensure the file is a valid YAML file",
                "Try with a different rules file",
            ],
        ) from e


# Legacy compatibility layer for tests
class Rule:
    """Legacy Rule class for backward compatibility with tests.

    This class provides a simple wrapper around the modern Rule system
    to maintain compatibility with existing tests that expect the old
    constructor interface.
    """

    def __init__(self, rule_dict: dict[str, Any]) -> None:
        """Initialize legacy Rule from dictionary.

        Args:
            rule_dict: Dictionary containing rule definition
        """
        # Create modern rule using the proper function
        self._modern_rule = create_rule_from_dict(rule_dict)

        # Expose attributes for backward compatibility
        self.id = self._modern_rule.id
        self.description = self._modern_rule.description
        self.resource_type = self._modern_rule.resource_type
        self.severity = self._modern_rule.severity

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to modern rule."""
        return getattr(self._modern_rule, name)

    def __str__(self) -> str:
        """String representation."""
        return str(self._modern_rule)
