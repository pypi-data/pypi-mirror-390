"""Rule validation and linting tools for Riveter."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import yaml

from .rules import Rule


class LintSeverity(Enum):
    """Severity levels for lint issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class LintIssue:
    """A linting issue found in a rule."""

    rule_id: str
    severity: LintSeverity
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class LintResult:
    """Result of linting a rule file or rule pack."""

    file_path: str
    valid: bool
    issues: List[LintIssue]
    rule_count: int

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == LintSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == LintSeverity.WARNING)

    @property
    def info_count(self) -> int:
        """Count of info-level issues."""
        return sum(1 for issue in self.issues if issue.severity == LintSeverity.INFO)


class RuleLinter:
    """Linter for rule files and rule packs."""

    def __init__(self) -> None:
        """Initialize the rule linter."""
        self.known_resource_types = self._load_known_resource_types()
        self.known_operators = {
            "eq",
            "ne",
            "gt",
            "gte",
            "lt",
            "lte",
            "in",
            "not_in",
            "regex",
            "not_regex",
            "contains",
            "not_contains",
            "length",
            "present",
            "absent",
            "starts_with",
            "ends_with",
        }

    def lint_file(self, file_path: str) -> LintResult:
        """Lint a rule file and return results."""
        issues = []
        rule_count = 0

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                data = yaml.safe_load(content)

            if not isinstance(data, dict):
                issues.append(
                    LintIssue(
                        rule_id="file",
                        severity=LintSeverity.ERROR,
                        message="Rule file must contain a YAML dictionary",
                    )
                )
                return LintResult(file_path, False, issues, 0)

            # Check file structure
            issues.extend(self._check_file_structure(data))

            # Lint individual rules
            if "rules" in data and isinstance(data["rules"], list):
                rule_count = len(data["rules"])
                for i, rule_data in enumerate(data["rules"]):
                    rule_issues = self._lint_rule(rule_data, i + 1)
                    issues.extend(rule_issues)

            # Check for duplicate rule IDs
            issues.extend(self._check_duplicate_rule_ids(data))

            # Check metadata if present
            if "metadata" in data:
                issues.extend(self._lint_metadata(data["metadata"]))

        except yaml.YAMLError as e:
            issues.append(
                LintIssue(
                    rule_id="file",
                    severity=LintSeverity.ERROR,
                    message=f"Invalid YAML syntax: {str(e)}",
                )
            )
        except Exception as e:
            issues.append(
                LintIssue(
                    rule_id="file",
                    severity=LintSeverity.ERROR,
                    message=f"Error reading file: {str(e)}",
                )
            )

        valid = not any(issue.severity == LintSeverity.ERROR for issue in issues)
        return LintResult(file_path, valid, issues, rule_count)

    def lint_rule_data(
        self, rule_data: Dict[str, Any], rule_id: str = "unknown"
    ) -> List[LintIssue]:
        """Lint a single rule data dictionary."""
        return self._lint_rule(rule_data, rule_id=rule_id)

    def _check_file_structure(self, data: Dict[str, Any]) -> List[LintIssue]:
        """Check the overall structure of the rule file."""
        issues = []

        # Check for required sections
        if "rules" not in data:
            issues.append(
                LintIssue(
                    rule_id="file",
                    severity=LintSeverity.ERROR,
                    message="Rule file must contain a 'rules' section",
                )
            )
        elif not isinstance(data["rules"], list):
            issues.append(
                LintIssue(
                    rule_id="file",
                    severity=LintSeverity.ERROR,
                    message="'rules' section must be a list",
                )
            )
        elif len(data["rules"]) == 0:
            issues.append(
                LintIssue(
                    rule_id="file",
                    severity=LintSeverity.WARNING,
                    message="Rule file contains no rules",
                )
            )

        # Check for unknown top-level keys
        known_keys = {"metadata", "rules"}
        unknown_keys = set(data.keys()) - known_keys
        if unknown_keys:
            issues.append(
                LintIssue(
                    rule_id="file",
                    severity=LintSeverity.WARNING,
                    message=f"Unknown top-level keys: {', '.join(unknown_keys)}",
                )
            )

        return issues

    def _lint_rule(
        self, rule_data: Any, rule_index: Optional[int] = None, rule_id: Optional[str] = None
    ) -> List[LintIssue]:
        """Lint a single rule."""
        issues = []

        if rule_id is None:
            rule_id = (
                rule_data.get("id", f"rule_{rule_index}")
                if isinstance(rule_data, dict)
                else f"rule_{rule_index}"
            )

        if not isinstance(rule_data, dict):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Rule must be a dictionary",
                )
            )
            return issues

        # Check required fields
        required_fields = ["id", "resource_type", "assert"]
        for field in required_fields:
            if field not in rule_data:
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.ERROR,
                        message=f"Missing required field: {field}",
                    )
                )

        # Validate rule ID
        if "id" in rule_data:
            issues.extend(self._validate_rule_id(rule_data["id"], rule_id))

        # Validate resource type
        if "resource_type" in rule_data:
            issues.extend(self._validate_resource_type(rule_data["resource_type"], rule_id))

        # Validate severity
        if "severity" in rule_data:
            issues.extend(self._validate_severity(rule_data["severity"], rule_id))

        # Validate description
        if "description" in rule_data:
            issues.extend(self._validate_description(rule_data["description"], rule_id))
        else:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message="Rule should have a description",
                )
            )

        # Validate filter
        if "filter" in rule_data:
            issues.extend(self._validate_filter(rule_data["filter"], rule_id))

        # Validate assertions
        if "assert" in rule_data:
            issues.extend(self._validate_assertions(rule_data["assert"], rule_id))

        # Validate metadata
        if "metadata" in rule_data:
            issues.extend(self._validate_rule_metadata(rule_data["metadata"], rule_id))

        # Check for unknown fields
        known_fields = {
            "id",
            "resource_type",
            "description",
            "severity",
            "filter",
            "assert",
            "metadata",
            "tags",
        }
        unknown_fields = set(rule_data.keys()) - known_fields
        if unknown_fields:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message=f"Unknown rule fields: {', '.join(unknown_fields)}",
                )
            )

        return issues

    def _validate_rule_id(self, rule_id: Any, context_rule_id: str) -> List[LintIssue]:
        """Validate rule ID format and content."""
        issues = []

        if not isinstance(rule_id, str):
            issues.append(
                LintIssue(
                    rule_id=context_rule_id,
                    severity=LintSeverity.ERROR,
                    message="Rule ID must be a string",
                )
            )
            return issues

        if not rule_id:
            issues.append(
                LintIssue(
                    rule_id=context_rule_id,
                    severity=LintSeverity.ERROR,
                    message="Rule ID cannot be empty",
                )
            )
            return issues

        # Check ID format (should be lowercase with underscores or hyphens)
        if not re.match(r"^[a-z0-9_-]+$", rule_id):
            issues.append(
                LintIssue(
                    rule_id=context_rule_id,
                    severity=LintSeverity.WARNING,
                    message=(
                        "Rule ID should contain only lowercase letters, numbers, "
                        "underscores, and hyphens"
                    ),
                    suggestion="Use lowercase letters, numbers, underscores, and hyphens only",
                )
            )

        # Check length
        if len(rule_id) > 100:
            issues.append(
                LintIssue(
                    rule_id=context_rule_id,
                    severity=LintSeverity.WARNING,
                    message="Rule ID is very long (>100 characters)",
                )
            )

        return issues

    def _validate_resource_type(self, resource_type: Any, rule_id: str) -> List[LintIssue]:
        """Validate resource type."""
        issues = []

        if not isinstance(resource_type, str):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Resource type must be a string",
                )
            )
            return issues

        if not resource_type:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Resource type cannot be empty",
                )
            )
            return issues

        # Check if resource type follows expected pattern
        if not re.match(r"^[a-z0-9_]+$", resource_type):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message=(
                        "Resource type should contain only lowercase letters, "
                        "numbers, and underscores"
                    ),
                )
            )

        # Check against known resource types
        if resource_type not in self.known_resource_types:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.INFO,
                    message=f"Unknown resource type: {resource_type}",
                )
            )

        return issues

    def _validate_severity(self, severity: Any, rule_id: str) -> List[LintIssue]:
        """Validate severity level."""
        issues = []

        if not isinstance(severity, str):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Severity must be a string",
                )
            )
            return issues

        valid_severities = {"error", "warning", "info"}
        if severity not in valid_severities:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message=(
                        f"Invalid severity '{severity}'. Must be one of: "
                        f"{', '.join(valid_severities)}"
                    ),
                )
            )

        return issues

    def _validate_description(self, description: Any, rule_id: str) -> List[LintIssue]:
        """Validate rule description."""
        issues = []

        if not isinstance(description, str):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Description must be a string",
                )
            )
            return issues

        if not description.strip():
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message="Description should not be empty",
                )
            )
        elif len(description) < 10:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message="Description is very short (<10 characters)",
                )
            )
        elif len(description) > 500:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message="Description is very long (>500 characters)",
                )
            )

        return issues

    def _validate_filter(self, filter_data: Any, rule_id: str) -> List[LintIssue]:
        """Validate rule filter."""
        issues = []

        if not isinstance(filter_data, dict):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Filter must be a dictionary",
                )
            )
            return issues

        # Recursively validate filter conditions
        issues.extend(self._validate_conditions(filter_data, rule_id, "filter"))

        return issues

    def _validate_assertions(self, assert_data: Any, rule_id: str) -> List[LintIssue]:
        """Validate rule assertions."""
        issues = []

        if not isinstance(assert_data, dict):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Assertions must be a dictionary",
                )
            )
            return issues

        if not assert_data:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Assertions cannot be empty",
                )
            )
            return issues

        # Recursively validate assertion conditions
        issues.extend(self._validate_conditions(assert_data, rule_id, "assert"))

        return issues

    def _validate_conditions(
        self, conditions: Dict[str, Any], rule_id: str, context: str
    ) -> List[LintIssue]:
        """Validate filter or assertion conditions."""
        issues = []

        for key, value in conditions.items():
            if isinstance(value, dict):
                # Check for operator usage
                operator_keys = set(value.keys()) & self.known_operators
                if operator_keys:
                    # Validate operator usage
                    issues.extend(self._validate_operator_usage(key, value, rule_id, context))
                else:
                    # Nested conditions
                    issues.extend(self._validate_conditions(value, rule_id, context))
            elif isinstance(value, list):
                # List of values or conditions
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        issues.extend(self._validate_conditions(item, rule_id, f"{context}[{i}]"))
            # Simple value conditions are generally valid

        return issues

    def _validate_operator_usage(
        self, property_path: str, operator_dict: Dict[str, Any], rule_id: str, context: str
    ) -> List[LintIssue]:
        """Validate operator usage in conditions."""
        issues = []

        operators_used = set(operator_dict.keys()) & self.known_operators
        unknown_operators = set(operator_dict.keys()) - self.known_operators

        if unknown_operators:
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.WARNING,
                    message=(
                        f"Unknown operators in {context}.{property_path}: "
                        f"{', '.join(unknown_operators)}"
                    ),
                )
            )

        # Check for conflicting operators
        conflicting_pairs = [
            ("eq", "ne"),
            ("gt", "lt"),
            ("gte", "lte"),
            ("in", "not_in"),
            ("contains", "not_contains"),
            ("regex", "not_regex"),
            ("present", "absent"),
        ]

        for op1, op2 in conflicting_pairs:
            if op1 in operators_used and op2 in operators_used:
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.WARNING,
                        message=(
                            f"Conflicting operators in {context}.{property_path}: "
                            f"{op1} and {op2}"
                        ),
                    )
                )

        # Validate specific operator usage
        for operator, value in operator_dict.items():
            if operator in self.known_operators:
                issues.extend(
                    self._validate_specific_operator(
                        operator, value, property_path, rule_id, context
                    )
                )

        return issues

    def _validate_specific_operator(
        self, operator: str, value: Any, property_path: str, rule_id: str, context: str
    ) -> List[LintIssue]:
        """Validate specific operator usage."""
        issues = []

        if operator == "regex" or operator == "not_regex":
            if not isinstance(value, str):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.ERROR,
                        message=(
                            f"Regex operator in {context}.{property_path} " "must have string value"
                        ),
                    )
                )
            else:
                # Validate regex pattern
                try:
                    re.compile(value)
                except re.error as e:
                    issues.append(
                        LintIssue(
                            rule_id=rule_id,
                            severity=LintSeverity.ERROR,
                            message=f"Invalid regex pattern in {context}.{property_path}: {str(e)}",
                        )
                    )

        elif operator in ["gt", "gte", "lt", "lte"]:
            if not isinstance(value, (int, float)):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.WARNING,
                        message=(
                            f"Numeric comparison operator {operator} in "
                            f"{context}.{property_path} should have numeric value"
                        ),
                    )
                )

        elif operator == "length":
            if not isinstance(value, dict):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.ERROR,
                        message=(
                            f"Length operator in {context}.{property_path} "
                            "must have dictionary value"
                        ),
                    )
                )
            else:
                # Validate length conditions
                valid_length_ops = {"eq", "ne", "gt", "gte", "lt", "lte"}
                invalid_ops = set(value.keys()) - valid_length_ops
                if invalid_ops:
                    issues.append(
                        LintIssue(
                            rule_id=rule_id,
                            severity=LintSeverity.ERROR,
                            message=(
                                f"Invalid length operators in {context}.{property_path}: "
                                f"{', '.join(invalid_ops)}"
                            ),
                        )
                    )

        elif operator in ["in", "not_in", "contains", "not_contains"]:
            if not isinstance(value, (list, str)):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.WARNING,
                        message=(
                            f"Operator {operator} in {context}.{property_path} "
                            f"should have list or string value"
                        ),
                    )
                )

        elif operator in ["present", "absent"]:
            if not isinstance(value, bool):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.WARNING,
                        message=(
                            f"Operator {operator} in {context}.{property_path} "
                            f"should have boolean value"
                        ),
                    )
                )

        return issues

    def _validate_rule_metadata(self, metadata: Any, rule_id: str) -> List[LintIssue]:
        """Validate rule metadata."""
        issues = []

        if not isinstance(metadata, dict):
            issues.append(
                LintIssue(
                    rule_id=rule_id,
                    severity=LintSeverity.ERROR,
                    message="Rule metadata must be a dictionary",
                )
            )
            return issues

        # Check for recommended metadata fields
        recommended_fields = ["tags", "references", "category"]
        for field in recommended_fields:
            if field not in metadata:
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.INFO,
                        message=f"Consider adding '{field}' to rule metadata",
                    )
                )

        # Validate tags
        if "tags" in metadata:
            if not isinstance(metadata["tags"], list):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.WARNING,
                        message="Rule metadata 'tags' should be a list",
                    )
                )
            elif not metadata["tags"]:
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.INFO,
                        message="Rule metadata 'tags' is empty",
                    )
                )

        # Validate references
        if "references" in metadata:
            if not isinstance(metadata["references"], list):
                issues.append(
                    LintIssue(
                        rule_id=rule_id,
                        severity=LintSeverity.WARNING,
                        message="Rule metadata 'references' should be a list",
                    )
                )
            else:
                for ref in metadata["references"]:
                    if not isinstance(ref, str):
                        issues.append(
                            LintIssue(
                                rule_id=rule_id,
                                severity=LintSeverity.WARNING,
                                message="Rule metadata references should be strings",
                            )
                        )
                    elif ref.startswith("http"):
                        # Basic URL validation
                        if not re.match(r"https?://[^\s]+", ref):
                            issues.append(
                                LintIssue(
                                    rule_id=rule_id,
                                    severity=LintSeverity.WARNING,
                                    message=f"Invalid URL in references: {ref}",
                                )
                            )

        return issues

    def _lint_metadata(self, metadata: Any) -> List[LintIssue]:
        """Lint rule pack metadata."""
        issues = []

        if not isinstance(metadata, dict):
            issues.append(
                LintIssue(
                    rule_id="metadata",
                    severity=LintSeverity.ERROR,
                    message="Metadata must be a dictionary",
                )
            )
            return issues

        # Check required metadata fields
        required_fields = ["name", "version", "description"]
        for field in required_fields:
            if field not in metadata:
                issues.append(
                    LintIssue(
                        rule_id="metadata",
                        severity=LintSeverity.ERROR,
                        message=f"Missing required metadata field: {field}",
                    )
                )

        # Validate version format
        if "version" in metadata:
            version = metadata["version"]
            if not isinstance(version, str):
                issues.append(
                    LintIssue(
                        rule_id="metadata",
                        severity=LintSeverity.ERROR,
                        message="Version must be a string",
                    )
                )
            elif not re.match(r"^\d+\.\d+\.\d+", version):
                issues.append(
                    LintIssue(
                        rule_id="metadata",
                        severity=LintSeverity.WARNING,
                        message="Version should follow semantic versioning (x.y.z)",
                    )
                )

        # Validate name
        if "name" in metadata:
            name = metadata["name"]
            if not isinstance(name, str):
                issues.append(
                    LintIssue(
                        rule_id="metadata",
                        severity=LintSeverity.ERROR,
                        message="Name must be a string",
                    )
                )
            elif not re.match(r"^[a-z0-9-]+$", name):
                issues.append(
                    LintIssue(
                        rule_id="metadata",
                        severity=LintSeverity.WARNING,
                        message="Name should contain only lowercase letters, numbers, and hyphens",
                    )
                )

        return issues

    def _check_duplicate_rule_ids(self, data: Dict[str, Any]) -> List[LintIssue]:
        """Check for duplicate rule IDs."""
        issues: List[LintIssue] = []

        if "rules" not in data or not isinstance(data["rules"], list):
            return issues

        rule_ids = []
        for rule in data["rules"]:
            if isinstance(rule, dict) and "id" in rule:
                rule_ids.append(rule["id"])

        seen = set()
        duplicates = set()
        for rule_id in rule_ids:
            if rule_id in seen:
                duplicates.add(rule_id)
            seen.add(rule_id)

        for duplicate_id in duplicates:
            issues.append(
                LintIssue(
                    rule_id=duplicate_id,
                    severity=LintSeverity.ERROR,
                    message=f"Duplicate rule ID: {duplicate_id}",
                )
            )

        return issues

    def _load_known_resource_types(self) -> Set[str]:
        """Load known Terraform resource types."""
        # This is a subset of common resource types
        # In a real implementation, this could be loaded from a comprehensive list
        return {
            # AWS
            "aws_instance",
            "aws_s3_bucket",
            "aws_security_group",
            "aws_vpc",
            "aws_subnet",
            "aws_route_table",
            "aws_internet_gateway",
            "aws_nat_gateway",
            "aws_load_balancer",
            "aws_autoscaling_group",
            "aws_launch_configuration",
            "aws_rds_instance",
            "aws_rds_cluster",
            "aws_elasticache_cluster",
            "aws_lambda_function",
            "aws_api_gateway_rest_api",
            "aws_cloudfront_distribution",
            "aws_route53_zone",
            "aws_route53_record",
            "aws_acm_certificate",
            "aws_iam_role",
            "aws_iam_policy",
            "aws_iam_user",
            "aws_iam_group",
            "aws_kms_key",
            "aws_cloudwatch_log_group",
            "aws_sns_topic",
            "aws_sqs_queue",
            # Azure
            "azurerm_resource_group",
            "azurerm_virtual_network",
            "azurerm_subnet",
            "azurerm_virtual_machine",
            "azurerm_storage_account",
            "azurerm_storage_container",
            "azurerm_network_security_group",
            "azurerm_public_ip",
            "azurerm_load_balancer",
            "azurerm_application_gateway",
            "azurerm_sql_server",
            "azurerm_sql_database",
            "azurerm_cosmosdb_account",
            "azurerm_function_app",
            "azurerm_app_service",
            # GCP
            "google_compute_instance",
            "google_compute_network",
            "google_compute_subnetwork",
            "google_compute_firewall",
            "google_storage_bucket",
            "google_sql_database_instance",
            "google_container_cluster",
            "google_cloud_run_service",
            "google_pubsub_topic",
            "google_bigquery_dataset",
            "google_bigquery_table",
            "google_cloud_function",
        }


class RuleTester:
    """Framework for testing rule behavior against sample resources."""

    def __init__(self) -> None:
        """Initialize the rule tester."""
        pass

    def test_rule(
        self, rule_data: Dict[str, Any], test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Test a rule against sample test cases."""
        from .scanner import validate_resources

        try:
            rule = Rule(rule_data)
        except Exception as e:
            return {"valid": False, "error": f"Failed to create rule: {str(e)}", "test_results": []}

        test_results = []

        for i, test_case in enumerate(test_cases):
            try:
                resource = test_case.get("resource", {})
                expected_result = test_case.get("expected", True)
                description = test_case.get("description", f"Test case {i + 1}")

                # Run the rule against the resource
                results = validate_resources([rule], [resource])

                if results:
                    actual_result = results[0].passed
                else:
                    actual_result = False

                test_results.append(
                    {
                        "description": description,
                        "expected": expected_result,
                        "actual": actual_result,
                        "passed": actual_result == expected_result,
                        "resource": resource,
                    }
                )

            except Exception as e:
                test_results.append(
                    {
                        "description": description,
                        "expected": expected_result,
                        "actual": None,
                        "passed": False,
                        "error": str(e),
                        "resource": resource,
                    }
                )

        passed_tests = sum(1 for result in test_results if result.get("passed", False))
        total_tests = len(test_results)

        return {
            "valid": True,
            "rule_id": rule.id,
            "test_results": test_results,
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            },
        }

    def create_test_template(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a test template for a rule."""
        resource_type = rule_data.get("resource_type", "unknown")

        template = {
            "rule": rule_data,
            "test_cases": [
                {
                    "description": "Resource that should pass the rule",
                    "resource": {
                        "type": resource_type,
                        "name": "test_resource_pass",
                        "config": {
                            # Add sample configuration that should pass
                        },
                    },
                    "expected": True,
                },
                {
                    "description": "Resource that should fail the rule",
                    "resource": {
                        "type": resource_type,
                        "name": "test_resource_fail",
                        "config": {
                            # Add sample configuration that should fail
                        },
                    },
                    "expected": False,
                },
            ],
        }

        return template
