"""Unit tests for the scanner module."""

from riveter.rules import Rule
from riveter.scanner import ValidationResult, validate_resources


class TestValidationResult:
    """Test cases for the ValidationResult class."""

    def test_validation_result_initialization(self, sample_rule):
        """Test ValidationResult initialization."""
        resource = {"id": "test-resource", "resource_type": "aws_instance"}
        result = ValidationResult(
            rule=sample_rule, resource=resource, passed=True, message="All checks passed"
        )

        assert result.rule == sample_rule
        assert result.resource == resource
        assert result.passed is True
        assert result.message == "All checks passed"

    def test_validation_result_failure(self, sample_rule):
        """Test ValidationResult for failed validation."""
        resource = {"id": "failing-resource", "resource_type": "aws_instance"}
        result = ValidationResult(
            rule=sample_rule,
            resource=resource,
            passed=False,
            message="Required tag 'CostCenter' is missing",
        )

        assert result.rule == sample_rule
        assert result.resource == resource
        assert result.passed is False
        assert result.message == "Required tag 'CostCenter' is missing"


class TestValidateResources:
    """Test cases for the validate_resources function."""

    def test_validate_resources_empty_lists(self):
        """Test validation with empty rules and resources."""
        results = validate_resources([], [])
        assert len(results) == 0

    def test_validate_resources_no_matching_resources(self):
        """Test validation when no resources match the rules."""
        rule_dict = {
            "id": "test-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        # Resource with different type
        resources = [
            {"id": "bucket", "resource_type": "aws_s3_bucket", "tags": {"Purpose": "storage"}}
        ]

        results = validate_resources([rule], resources)

        # Should have one result indicating the rule was skipped
        assert len(results) == 1
        assert results[0].passed is False
        assert "SKIPPED: No matching resources found" in results[0].message
        assert results[0].rule.id == "test-rule"

    def test_validate_resources_successful_validation(self):
        """Test successful resource validation."""
        rule_dict = {
            "id": "environment-tag-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "web-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production", "Name": "web-server"},
            }
        ]

        results = validate_resources([rule], resources)

        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].message == "All checks passed"
        assert results[0].rule.id == "environment-tag-rule"
        assert results[0].resource["id"] == "web-server"

    def test_validate_resources_failed_validation_missing_tag(self):
        """Test failed validation due to missing required tag."""
        rule_dict = {
            "id": "cost-center-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "web-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production"},
            }
        ]

        results = validate_resources([rule], resources)

        assert len(results) == 1
        assert results[0].passed is False
        assert "Required tag 'CostCenter' is missing" in results[0].message

    def test_validate_resources_failed_validation_wrong_tag_value(self):
        """Test failed validation due to incorrect tag value."""
        rule_dict = {
            "id": "environment-value-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "production"}},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "test-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "staging"},
            }
        ]

        results = validate_resources([rule], resources)

        assert len(results) == 1
        assert results[0].passed is False
        assert (
            "Tag 'Environment' has value 'staging' but expected 'production'" in results[0].message
        )

    def test_validate_resources_failed_validation_missing_property(self):
        """Test failed validation due to missing property."""
        rule_dict = {
            "id": "instance-type-rule",
            "resource_type": "aws_instance",
            "assert": {"instance_type": "t3.micro"},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "web-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production"},
            }
        ]

        results = validate_resources([rule], resources)

        assert len(results) == 1
        assert results[0].passed is False
        assert (
            "Property 'instance_type' has value 'None' but expected 't3.micro'"
            in results[0].message
        )

    def test_validate_resources_failed_validation_wrong_property_value(self):
        """Test failed validation due to incorrect property value."""
        rule_dict = {
            "id": "instance-type-rule",
            "resource_type": "aws_instance",
            "assert": {"instance_type": "t3.micro"},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "web-server",
                "resource_type": "aws_instance",
                "instance_type": "t3.large",
                "tags": {"Environment": "production"},
            }
        ]

        results = validate_resources([rule], resources)

        assert len(results) == 1
        assert results[0].passed is False
        assert (
            "Property 'instance_type' has value 't3.large' but expected 't3.micro'"
            in results[0].message
        )

    def test_validate_resources_with_filter(self):
        """Test validation with rule filters."""
        rule_dict = {
            "id": "production-cost-center-rule",
            "resource_type": "aws_instance",
            "filter": {"tags": {"Environment": "production"}},
            "assert": {"tags": {"CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "prod-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production", "CostCenter": "12345"},
            },
            {
                "id": "test-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "staging"},
            },
        ]

        results = validate_resources([rule], resources)

        # Should only validate the production server
        assert len(results) == 1
        assert results[0].passed is True
        assert results[0].resource["id"] == "prod-server"

    def test_validate_resources_wildcard_resource_type(self):
        """Test validation with wildcard resource type."""
        rule_dict = {
            "id": "universal-environment-rule",
            "resource_type": "*",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "web-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production"},
            },
            {
                "id": "data-bucket",
                "resource_type": "aws_s3_bucket",
                "tags": {"Environment": "production", "Purpose": "storage"},
            },
            {
                "id": "database",
                "resource_type": "aws_rds_instance",
                "tags": {"Name": "database"},  # Missing Environment tag
            },
        ]

        results = validate_resources([rule], resources)

        assert len(results) == 3
        assert results[0].passed is True  # web-server
        assert results[1].passed is True  # data-bucket
        assert results[2].passed is False  # database missing Environment tag

    def test_validate_resources_multiple_rules_single_resource(self):
        """Test validation with multiple rules against a single resource."""
        rule1_dict = {
            "id": "environment-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule2_dict = {
            "id": "cost-center-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"CostCenter": "present"}},
        }

        rules = [Rule(rule1_dict), Rule(rule2_dict)]

        resources = [
            {
                "id": "web-server",
                "resource_type": "aws_instance",
                "tags": {"Environment": "production", "CostCenter": "12345"},
            }
        ]

        results = validate_resources(rules, resources)

        assert len(results) == 2
        assert all(result.passed for result in results)
        assert results[0].rule.id == "environment-rule"
        assert results[1].rule.id == "cost-center-rule"

    def test_validate_resources_multiple_assertions_single_rule(self):
        """Test validation with multiple assertions in a single rule."""
        rule_dict = {
            "id": "multi-tag-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "production", "CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        # Resource that passes all assertions
        passing_resource = {
            "id": "good-server",
            "resource_type": "aws_instance",
            "tags": {"Environment": "production", "CostCenter": "12345"},
        }

        # Resource that fails one assertion
        failing_resource = {
            "id": "bad-server",
            "resource_type": "aws_instance",
            "tags": {"Environment": "staging", "CostCenter": "12345"},
        }

        # Test passing resource
        results = validate_resources([rule], [passing_resource])
        assert len(results) == 1
        assert results[0].passed is True

        # Test failing resource
        results = validate_resources([rule], [failing_resource])
        assert len(results) == 1
        assert results[0].passed is False
        assert (
            "Tag 'Environment' has value 'staging' but expected 'production'" in results[0].message
        )

    def test_validate_resources_no_resource_type(self):
        """Test validation with resources missing resource_type."""
        rule_dict = {
            "id": "test-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        resources = [
            {
                "id": "invalid-resource",
                "tags": {"Environment": "production"},
            }  # Missing resource_type
        ]

        results = validate_resources([rule], resources)

        # Should skip the resource and report rule as not applied
        assert len(results) == 1
        assert results[0].passed is False
        assert "SKIPPED: No matching resources found" in results[0].message

    def test_validate_resources_complex_scenario(self, sample_terraform_config, sample_rules_list):
        """Test validation with complex scenario using fixtures."""
        results = validate_resources(sample_rules_list, sample_terraform_config["resources"])

        # Should have results for each rule-resource combination
        assert len(results) > 0

        # Check that we have results for different rule types
        rule_ids = [result.rule.id for result in results]
        assert "test-rule-001" in rule_ids  # aws_instance rule
        assert "test-rule-002" in rule_ids  # aws_s3_bucket rule
        assert "test-rule-003" in rule_ids  # universal rule

        # Verify some results are passing
        passing_results = [r for r in results if r.passed]
        assert len(passing_results) > 0


class TestAdvancedValidation:
    """Test cases for advanced validation features."""

    def test_validation_result_with_assertion_results(self):
        """Test ValidationResult with detailed assertion results."""
        from riveter.rules import AssertionResult, Severity

        rule_dict = {
            "id": "test-rule",
            "resource_type": "aws_instance",
            "severity": "error",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        resource = {"id": "test", "resource_type": "aws_instance"}
        assertion_results = [
            AssertionResult("tags.Environment", "present", "present", None, False, "Missing tag")
        ]

        result = ValidationResult(
            rule=rule,
            resource=resource,
            passed=False,
            message="Validation failed",
            assertion_results=assertion_results,
            execution_time=0.1,
        )

        assert result.severity == Severity.ERROR
        assert len(result.assertion_results) == 1
        assert result.execution_time == 0.1

    def test_validation_result_to_dict(self):
        """Test ValidationResult conversion to dictionary."""
        from riveter.rules import AssertionResult

        rule_dict = {
            "id": "test-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        resource = {"id": "test", "resource_type": "aws_instance"}
        assertion_results = [
            AssertionResult("tags.Environment", "present", "present", None, False, "Missing tag")
        ]

        result = ValidationResult(
            rule=rule,
            resource=resource,
            passed=False,
            message="Validation failed",
            assertion_results=assertion_results,
        )

        result_dict = result.to_dict()

        assert result_dict["rule_id"] == "test-rule"
        assert result_dict["resource_type"] == "aws_instance"
        assert result_dict["passed"] is False
        assert result_dict["severity"] == "error"
        assert len(result_dict["assertion_results"]) == 1

    def test_validate_resources_with_advanced_operators(self):
        """Test resource validation with advanced operators."""
        rule_dict = {
            "id": "advanced-rule",
            "resource_type": "aws_instance",
            "assert": {
                "root_block_device.volume_size": {"gte": 100},
                "instance_type": {"regex": r"^t3\."},
                "security_groups": {"length": {"gte": 1}},
            },
        }
        rule = Rule(rule_dict)

        # Resource that passes all assertions
        passing_resource = {
            "id": "good-instance",
            "resource_type": "aws_instance",
            "root_block_device": {"volume_size": 150},
            "instance_type": "t3.large",
            "security_groups": ["sg-123", "sg-456"],
        }

        # Resource that fails some assertions
        failing_resource = {
            "id": "bad-instance",
            "resource_type": "aws_instance",
            "root_block_device": {"volume_size": 50},  # Fails gte 100
            "instance_type": "m5.large",  # Fails regex
            "security_groups": ["sg-123"],  # Passes length check
        }

        # Test passing resource
        results = validate_resources([rule], [passing_resource])
        assert len(results) == 1
        assert results[0].passed is True
        assert len(results[0].assertion_results) == 3
        assert all(ar.passed for ar in results[0].assertion_results)

        # Test failing resource
        results = validate_resources([rule], [failing_resource])
        assert len(results) == 1
        assert results[0].passed is False
        assert len(results[0].assertion_results) == 3

        # Check specific assertion failures
        failed_assertions = [ar for ar in results[0].assertion_results if not ar.passed]
        assert len(failed_assertions) == 2  # volume_size and instance_type should fail

    def test_validate_resources_with_severity_filtering(self):
        """Test resource validation with severity filtering."""
        from riveter.scanner import Severity

        error_rule_dict = {
            "id": "error-rule",
            "resource_type": "aws_instance",
            "severity": "error",
            "assert": {"tags": {"Critical": "present"}},
        }

        warning_rule_dict = {
            "id": "warning-rule",
            "resource_type": "aws_instance",
            "severity": "warning",
            "assert": {"tags": {"Optional": "present"}},
        }

        info_rule_dict = {
            "id": "info-rule",
            "resource_type": "aws_instance",
            "severity": "info",
            "assert": {"tags": {"Nice": "present"}},
        }

        rules = [Rule(error_rule_dict), Rule(warning_rule_dict), Rule(info_rule_dict)]

        resource = {"id": "test-instance", "resource_type": "aws_instance", "tags": {}}

        # Test with minimum severity ERROR (should only include error rule)
        results = validate_resources(rules, [resource], min_severity=Severity.ERROR)
        assert len(results) == 1
        assert results[0].rule.id == "error-rule"

        # Test with minimum severity WARNING (should include error and warning rules)
        results = validate_resources(rules, [resource], min_severity=Severity.WARNING)
        assert len(results) == 2
        rule_ids = [r.rule.id for r in results]
        assert "error-rule" in rule_ids
        assert "warning-rule" in rule_ids

        # Test with minimum severity INFO (should include all rules)
        results = validate_resources(rules, [resource], min_severity=Severity.INFO)
        assert len(results) == 3

    def test_filter_results_by_severity(self):
        """Test filtering validation results by severity."""
        from riveter.scanner import Severity, filter_results_by_severity

        # Create rules with different severities
        error_rule = Rule(
            {
                "id": "error-rule",
                "resource_type": "aws_instance",
                "severity": "error",
                "assert": {"tags": {"Environment": "present"}},
            }
        )

        warning_rule = Rule(
            {
                "id": "warning-rule",
                "resource_type": "aws_instance",
                "severity": "warning",
                "assert": {"tags": {"Team": "present"}},
            }
        )

        resource = {"id": "test", "resource_type": "aws_instance", "tags": {}}

        # Create validation results
        results = [
            ValidationResult(error_rule, resource, False, "Error message"),
            ValidationResult(warning_rule, resource, False, "Warning message"),
        ]

        # Filter by ERROR severity
        error_results = filter_results_by_severity(results, Severity.ERROR)
        assert len(error_results) == 1
        assert error_results[0].rule.id == "error-rule"

        # Filter by WARNING severity
        warning_results = filter_results_by_severity(results, Severity.WARNING)
        assert len(warning_results) == 2  # Both error and warning

    def test_validate_resources_execution_time_tracking(self):
        """Test that validation tracks execution time."""
        rule_dict = {
            "id": "timing-test",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        resource = {
            "id": "test-instance",
            "resource_type": "aws_instance",
            "tags": {"Environment": "production"},
        }

        results = validate_resources([rule], [resource])
        assert len(results) == 1
        assert results[0].execution_time >= 0  # Should have some execution time recorded
