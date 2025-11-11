"""Tests for rule linting and validation system."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from riveter.rule_linter import LintSeverity, RuleLinter, RuleTester


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def valid_rule_file(temp_directory):
    """Create a valid rule file for testing."""
    rule_data = {
        "metadata": {
            "name": "test-rules",
            "version": "1.0.0",
            "description": "Test rule pack",
            "author": "Test Author",
        },
        "rules": [
            {
                "id": "test_rule_1",
                "resource_type": "aws_instance",
                "description": "Test rule for instance types",
                "severity": "error",
                "filter": {"tags.Environment": "production"},
                "assert": {"instance_type": {"regex": "^(t3|m5|c5)\\.(large|xlarge)$"}},
                "metadata": {"tags": ["security", "compliance"]},
            },
            {
                "id": "test_rule_2",
                "resource_type": "aws_s3_bucket",
                "description": "Test rule for S3 bucket encryption",
                "severity": "warning",
                "assert": {"server_side_encryption_configuration": {"present": True}},
            },
        ],
    }

    rule_file = temp_directory / "valid_rules.yml"
    with open(rule_file, "w") as f:
        yaml.dump(rule_data, f)

    return rule_file


@pytest.fixture
def invalid_rule_file(temp_directory):
    """Create an invalid rule file for testing."""
    rule_data = {
        "rules": [
            {
                # Missing required fields
                "description": "Invalid rule missing ID and resource type",
                "assert": {"some_field": {"eq": "value"}},
            },
            {
                "id": "invalid_rule_2",
                "resource_type": "aws_instance",
                # Missing description
                "severity": "invalid_severity",  # Invalid severity
                "assert": {"instance_type": {"invalid_operator": "value"}},  # Invalid operator
            },
        ]
    }

    rule_file = temp_directory / "invalid_rules.yml"
    with open(rule_file, "w") as f:
        yaml.dump(rule_data, f)

    return rule_file


class TestRuleLinter:
    """Test RuleLinter functionality."""

    def test_lint_valid_file(self, valid_rule_file):
        """Test linting a valid rule file."""
        linter = RuleLinter()
        result = linter.lint_file(str(valid_rule_file))

        assert result.valid is True
        assert result.rule_count == 2
        assert result.error_count == 0

        # May have some warnings or info messages
        assert len(result.issues) >= 0

    def test_lint_invalid_file(self, invalid_rule_file):
        """Test linting an invalid rule file."""
        linter = RuleLinter()
        result = linter.lint_file(str(invalid_rule_file))

        assert result.valid is False
        assert result.rule_count == 2
        assert result.error_count > 0

        # Check for specific errors
        error_messages = [
            issue.message for issue in result.issues if issue.severity == LintSeverity.ERROR
        ]
        assert any("Missing required field: id" in msg for msg in error_messages)
        assert any("Missing required field: resource_type" in msg for msg in error_messages)
        assert any("Invalid severity" in msg for msg in error_messages)

    def test_lint_nonexistent_file(self):
        """Test linting a nonexistent file."""
        linter = RuleLinter()
        result = linter.lint_file("/nonexistent/file.yml")

        assert result.valid is False
        assert result.error_count > 0
        assert "Error reading file" in result.issues[0].message

    def test_lint_invalid_yaml(self, temp_directory):
        """Test linting a file with invalid YAML."""
        invalid_yaml_file = temp_directory / "invalid.yml"
        invalid_yaml_file.write_text("invalid: yaml: content: [")

        linter = RuleLinter()
        result = linter.lint_file(str(invalid_yaml_file))

        assert result.valid is False
        assert result.error_count > 0
        assert "Invalid YAML syntax" in result.issues[0].message

    def test_lint_empty_rules(self, temp_directory):
        """Test linting a file with no rules."""
        empty_rules_file = temp_directory / "empty.yml"
        empty_rules_file.write_text("rules: []")

        linter = RuleLinter()
        result = linter.lint_file(str(empty_rules_file))

        assert result.valid is True  # Valid but with warnings
        assert result.rule_count == 0
        assert result.warning_count > 0
        assert "contains no rules" in result.issues[0].message

    def test_validate_rule_id(self):
        """Test rule ID validation."""
        linter = RuleLinter()

        # Valid rule ID
        issues = linter._validate_rule_id("valid_rule_id", "test_rule")
        assert len(issues) == 0

        # Invalid rule ID (uppercase)
        issues = linter._validate_rule_id("Invalid_Rule_ID", "test_rule")
        assert len(issues) > 0
        assert any("lowercase" in issue.message for issue in issues)

        # Empty rule ID
        issues = linter._validate_rule_id("", "test_rule")
        assert len(issues) > 0
        assert any("cannot be empty" in issue.message for issue in issues)

    def test_validate_resource_type(self):
        """Test resource type validation."""
        linter = RuleLinter()

        # Valid resource type
        issues = linter._validate_resource_type("aws_instance", "test_rule")
        assert len(issues) == 0  # Should be in known types

        # Unknown resource type
        issues = linter._validate_resource_type("unknown_resource", "test_rule")
        assert len(issues) > 0
        assert any("Unknown resource type" in issue.message for issue in issues)

        # Invalid format
        issues = linter._validate_resource_type("Invalid-Resource", "test_rule")
        assert len(issues) > 0
        assert any("lowercase" in issue.message for issue in issues)

    def test_validate_severity(self):
        """Test severity validation."""
        linter = RuleLinter()

        # Valid severities
        for severity in ["error", "warning", "info"]:
            issues = linter._validate_severity(severity, "test_rule")
            assert len(issues) == 0

        # Invalid severity
        issues = linter._validate_severity("invalid", "test_rule")
        assert len(issues) > 0
        assert any("Invalid severity" in issue.message for issue in issues)

    def test_validate_description(self):
        """Test description validation."""
        linter = RuleLinter()

        # Valid description
        issues = linter._validate_description("This is a valid description", "test_rule")
        assert len(issues) == 0

        # Empty description
        issues = linter._validate_description("", "test_rule")
        assert len(issues) > 0
        assert any("should not be empty" in issue.message for issue in issues)

        # Very short description
        issues = linter._validate_description("Short", "test_rule")
        assert len(issues) > 0
        assert any("very short" in issue.message for issue in issues)

    def test_validate_operator_usage(self):
        """Test operator usage validation."""
        linter = RuleLinter()

        # Valid regex operator
        issues = linter._validate_operator_usage(
            "instance_type", {"regex": "^t3\\.(micro|small)$"}, "test_rule", "assert"
        )
        assert len(issues) == 0

        # Invalid regex pattern
        issues = linter._validate_operator_usage(
            "instance_type", {"regex": "[invalid"}, "test_rule", "assert"
        )
        assert len(issues) > 0
        assert any("Invalid regex pattern" in issue.message for issue in issues)

        # Unknown operator
        issues = linter._validate_operator_usage(
            "instance_type", {"unknown_op": "value"}, "test_rule", "assert"
        )
        assert len(issues) > 0
        assert any("Unknown operators" in issue.message for issue in issues)

        # Conflicting operators
        issues = linter._validate_operator_usage(
            "instance_type", {"eq": "value", "ne": "other"}, "test_rule", "assert"
        )
        assert len(issues) > 0
        assert any("Conflicting operators" in issue.message for issue in issues)

    def test_check_duplicate_rule_ids(self, temp_directory):
        """Test duplicate rule ID detection."""
        rule_data = {
            "rules": [
                {
                    "id": "duplicate_id",
                    "resource_type": "aws_instance",
                    "description": "First rule",
                    "assert": {"instance_type": {"eq": "t3.micro"}},
                },
                {
                    "id": "duplicate_id",
                    "resource_type": "aws_s3_bucket",
                    "description": "Second rule with same ID",
                    "assert": {"versioning": {"present": True}},
                },
            ]
        }

        rule_file = temp_directory / "duplicate_ids.yml"
        with open(rule_file, "w") as f:
            yaml.dump(rule_data, f)

        linter = RuleLinter()
        result = linter.lint_file(str(rule_file))

        assert result.valid is False
        assert result.error_count > 0
        assert any("Duplicate rule ID" in issue.message for issue in result.issues)

    def test_lint_rule_data_directly(self):
        """Test linting rule data directly without file."""
        linter = RuleLinter()

        # Valid rule data
        valid_rule = {
            "id": "test_rule",
            "resource_type": "aws_instance",
            "description": "Test rule",
            "severity": "error",
            "assert": {"instance_type": {"eq": "t3.micro"}},
        }

        issues = linter.lint_rule_data(valid_rule, "test_rule")
        error_issues = [i for i in issues if i.severity == LintSeverity.ERROR]
        assert len(error_issues) == 0

        # Invalid rule data
        invalid_rule = {
            "id": "test_rule",
            # Missing resource_type
            "description": "Test rule",
            "severity": "invalid_severity",
            # Missing assert
        }

        issues = linter.lint_rule_data(invalid_rule, "test_rule")
        error_issues = [i for i in issues if i.severity == LintSeverity.ERROR]
        assert len(error_issues) > 0


class TestRuleTester:
    """Test RuleTester functionality."""

    def test_test_rule_with_passing_cases(self):
        """Test rule testing with passing test cases."""
        tester = RuleTester()

        rule_data = {
            "id": "test_instance_type",
            "resource_type": "aws_instance",
            "description": "Test instance type rule",
            "severity": "error",
            "assert": {"instance_type": {"eq": "t3.micro"}},
        }

        test_cases = [
            {
                "description": "Instance with correct type",
                "resource": {
                    "type": "aws_instance",
                    "name": "test_instance",
                    "config": {"instance_type": "t3.micro"},
                },
                "expected": True,
            },
            {
                "description": "Instance with incorrect type",
                "resource": {
                    "type": "aws_instance",
                    "name": "test_instance",
                    "config": {"instance_type": "t3.large"},
                },
                "expected": False,
            },
        ]

        with patch("riveter.scanner.validate_resources") as mock_validate:
            # Mock validation results
            from riveter.rules import Rule
            from riveter.scanner import ValidationResult

            mock_results = [
                ValidationResult(
                    rule=Rule(rule_data),
                    resource=test_cases[0]["resource"],
                    passed=True,
                    message="Test passed",
                    assertion_results=[],
                    execution_time=0.001,
                ),
                ValidationResult(
                    rule=Rule(rule_data),
                    resource=test_cases[1]["resource"],
                    passed=False,
                    message="Test failed",
                    assertion_results=[],
                    execution_time=0.001,
                ),
            ]

            mock_validate.side_effect = [[mock_results[0]], [mock_results[1]]]

            result = tester.test_rule(rule_data, test_cases)

            assert result["valid"] is True
            assert result["rule_id"] == "test_instance_type"
            assert len(result["test_results"]) == 2
            assert result["test_results"][0]["passed"] is True
            assert result["test_results"][1]["passed"] is True  # Expected False, got False
            assert result["summary"]["total"] == 2
            assert result["summary"]["passed"] == 2

    def test_test_rule_with_invalid_rule(self):
        """Test rule testing with invalid rule data."""
        tester = RuleTester()

        invalid_rule_data = {
            # Missing required fields
            "description": "Invalid rule",
        }

        test_cases = []

        result = tester.test_rule(invalid_rule_data, test_cases)

        assert result["valid"] is False
        assert "Failed to create rule" in result["error"]

    def test_create_test_template(self):
        """Test creating test template for a rule."""
        tester = RuleTester()

        rule_data = {
            "id": "test_rule",
            "resource_type": "aws_instance",
            "description": "Test rule",
            "assert": {"instance_type": {"eq": "t3.micro"}},
        }

        template = tester.create_test_template(rule_data)

        assert template["rule"] == rule_data
        assert len(template["test_cases"]) == 2
        assert template["test_cases"][0]["expected"] is True
        assert template["test_cases"][1]["expected"] is False
        assert template["test_cases"][0]["resource"]["type"] == "aws_instance"


class TestIntegration:
    """Integration tests for rule linting system."""

    def test_comprehensive_rule_validation(self, temp_directory):
        """Test comprehensive validation of a complex rule file."""
        complex_rule_data = {
            "metadata": {
                "name": "comprehensive-rules",
                "version": "2.1.0",
                "description": "Comprehensive rule pack for testing",
                "author": "Test Suite",
                "tags": ["security", "compliance", "best-practices"],
            },
            "rules": [
                {
                    "id": "ec2_instance_security",
                    "resource_type": "aws_instance",
                    "description": "Ensure EC2 instances follow security best practices",
                    "severity": "error",
                    "filter": {
                        "tags.Environment": {"in": ["production", "staging"]},
                        "instance_type": {"regex": "^(t3|m5|c5)\\.(large|xlarge)$"},
                    },
                    "assert": {
                        "monitoring": {"eq": True},
                        "security_groups": {"length": {"gte": 1}},
                        "tags.Owner": {"present": True},
                        "root_block_device.encrypted": {"eq": True},
                    },
                    "metadata": {
                        "tags": ["security", "encryption", "monitoring"],
                        "references": [
                            "https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-best-practices.html"
                        ],
                        "category": "security",
                    },
                },
                {
                    "id": "s3_bucket_compliance",
                    "resource_type": "aws_s3_bucket",
                    "description": "Ensure S3 buckets are compliant with security policies",
                    "severity": "warning",
                    "assert": {
                        "server_side_encryption_configuration": {"present": True},
                        "versioning.enabled": {"eq": True},
                        "public_read_acl": {"eq": False},
                        "public_write_acl": {"eq": False},
                    },
                    "metadata": {
                        "tags": ["security", "compliance", "data-protection"],
                        "references": [
                            "https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html"
                        ],
                    },
                },
            ],
        }

        rule_file = temp_directory / "comprehensive_rules.yml"
        with open(rule_file, "w") as f:
            yaml.dump(complex_rule_data, f)

        linter = RuleLinter()
        result = linter.lint_file(str(rule_file))

        # Should be valid with minimal issues
        assert result.valid is True
        assert result.rule_count == 2
        assert result.error_count == 0

        # May have some info-level suggestions
        info_issues = [i for i in result.issues if i.severity == LintSeverity.INFO]
        assert len(info_issues) >= 0  # Could have suggestions for improvements
