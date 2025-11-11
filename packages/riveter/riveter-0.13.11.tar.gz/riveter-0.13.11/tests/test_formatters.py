"""Unit tests for the formatters module."""

import json
import xml.etree.ElementTree as ET
from datetime import datetime

from riveter.formatters import JSONFormatter, JUnitXMLFormatter, SARIFFormatter
from riveter.rules import Rule
from riveter.scanner import ValidationResult


class TestJSONFormatter:
    """Test cases for the JSON formatter."""

    def test_json_formatter_empty_results(self):
        """Test JSON formatter with empty results."""
        formatter = JSONFormatter()
        output = formatter.format([])

        data = json.loads(output)
        assert data["summary"]["total"] == 0
        assert data["summary"]["passed"] == 0
        assert data["summary"]["failed"] == 0
        assert data["summary"]["skipped"] == 0
        assert data["results"] == []
        assert "timestamp" in data

    def test_json_formatter_with_results(self, sample_rules_list):
        """Test JSON formatter with validation results."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
                execution_time=0.1,
            ),
            ValidationResult(
                rule=rule,
                resource={"id": "bad-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Required tag missing",
                execution_time=0.2,
            ),
        ]

        formatter = JSONFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        assert data["summary"]["total"] == 2
        assert data["summary"]["passed"] == 1
        assert data["summary"]["failed"] == 1
        assert data["summary"]["skipped"] == 0
        assert data["summary"]["active_checks"] == 2
        assert len(data["results"]) == 2

        # Check first result
        result1 = data["results"][0]
        assert result1["rule_id"] == rule.id
        assert result1["resource_type"] == "aws_instance"
        assert result1["resource_id"] == "test-instance"
        assert result1["passed"] is True
        assert result1["message"] == "All checks passed"
        assert result1["execution_time"] == 0.1

    def test_json_formatter_with_skipped_results(self, sample_rules_list):
        """Test JSON formatter with skipped results."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"resource_type": rule.resource_type, "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
                execution_time=0.0,
            )
        ]

        formatter = JSONFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        assert data["summary"]["total"] == 1
        assert data["summary"]["passed"] == 0
        assert data["summary"]["failed"] == 0
        assert data["summary"]["skipped"] == 1
        assert data["summary"]["active_checks"] == 0

    def test_json_formatter_timestamp_format(self):
        """Test that JSON formatter includes valid ISO timestamp."""
        formatter = JSONFormatter()
        output = formatter.format([])

        data = json.loads(output)
        timestamp = data["timestamp"]

        # Should be valid ISO format ending with Z
        assert timestamp.endswith("Z")
        # Should be parseable as datetime
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


class TestJUnitXMLFormatter:
    """Test cases for the JUnit XML formatter."""

    def test_junit_formatter_empty_results(self):
        """Test JUnit XML formatter with empty results."""
        formatter = JUnitXMLFormatter()
        output = formatter.format([])

        # Parse XML
        root = ET.fromstring(output)
        assert root.tag == "testsuite"
        assert root.get("tests") == "0"
        assert root.get("failures") == "0"
        assert root.get("skipped") == "0"
        assert "timestamp" in root.attrib

    def test_junit_formatter_with_results(self, sample_rules_list):
        """Test JUnit XML formatter with validation results."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
                execution_time=0.1,
            ),
            ValidationResult(
                rule=rule,
                resource={"id": "bad-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Required tag missing",
                execution_time=0.2,
            ),
        ]

        formatter = JUnitXMLFormatter()
        output = formatter.format(results)

        # Parse XML
        root = ET.fromstring(output)
        assert root.tag == "testsuite"
        assert root.get("tests") == "2"
        assert root.get("failures") == "1"
        assert root.get("skipped") == "0"

        # Check testcase elements
        testcases = root.findall("testcase")
        assert len(testcases) == 2

        # Check passing test
        passing_test = testcases[0]
        assert passing_test.get("name") == rule.id
        assert passing_test.get("classname") == "riveter.aws_instance"
        assert passing_test.get("time") == "0.1"
        assert passing_test.find("failure") is None

        # Check failing test
        failing_test = testcases[1]
        assert failing_test.get("name") == rule.id
        assert failing_test.get("classname") == "riveter.aws_instance"
        assert failing_test.get("time") == "0.2"
        failure = failing_test.find("failure")
        assert failure is not None
        assert failure.get("message") == "Required tag missing"

    def test_junit_formatter_skips_skipped_results(self, sample_rules_list):
        """Test that JUnit XML formatter excludes skipped results."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
                execution_time=0.1,
            ),
            ValidationResult(
                rule=rule,
                resource={"resource_type": rule.resource_type, "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
                execution_time=0.0,
            ),
        ]

        formatter = JUnitXMLFormatter()
        output = formatter.format(results)

        # Parse XML
        root = ET.fromstring(output)
        assert root.get("tests") == "1"  # Only non-skipped tests
        assert root.get("skipped") == "1"  # Skipped count in summary

        # Only one testcase element (skipped results are not included as testcases)
        testcases = root.findall("testcase")
        assert len(testcases) == 1

    def test_junit_formatter_properties(self, sample_rules_list):
        """Test that JUnit XML formatter includes properties."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
                execution_time=0.1,
            )
        ]

        formatter = JUnitXMLFormatter()
        output = formatter.format(results)

        # Parse XML
        root = ET.fromstring(output)
        testcase = root.find("testcase")
        properties = testcase.find("properties")
        assert properties is not None

        # Check properties
        prop_elements = properties.findall("property")
        prop_dict = {prop.get("name"): prop.get("value") for prop in prop_elements}

        assert "resource_id" in prop_dict
        assert "severity" in prop_dict
        assert prop_dict["resource_id"] == "test-instance"
        assert prop_dict["severity"] == rule.severity.value


class TestSARIFFormatter:
    """Test cases for the SARIF formatter."""

    def test_sarif_formatter_empty_results(self):
        """Test SARIF formatter with empty results."""
        formatter = SARIFFormatter()
        output = formatter.format([])

        data = json.loads(output)
        assert data["version"] == "2.1.0"
        assert "$schema" in data
        assert len(data["runs"]) == 1

        run = data["runs"][0]
        assert run["tool"]["driver"]["name"] == "Riveter"
        assert run["results"] == []
        assert run["invocations"][0]["executionSuccessful"] is True

    def test_sarif_formatter_with_failures(self, sample_rules_list):
        """Test SARIF formatter with failed validation results."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
                execution_time=0.1,
            ),
            ValidationResult(
                rule=rule,
                resource={"id": "bad-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Required tag missing",
                execution_time=0.2,
            ),
        ]

        formatter = SARIFFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        run = data["runs"][0]

        # Should only include failed results
        assert len(run["results"]) == 1

        result = run["results"][0]
        assert result["ruleId"] == rule.id
        assert result["level"] == "error"  # Based on rule severity
        assert result["message"]["text"] == "Required tag missing"

        # Check locations
        location = result["locations"][0]
        logical_location = location["logicalLocations"][0]
        assert logical_location["name"] == "bad-instance"
        assert logical_location["kind"] == "resource"

        # Check properties
        properties = result["properties"]
        assert properties["resource_type"] == "aws_instance"
        assert properties["resource_id"] == "bad-instance"
        assert properties["execution_time"] == 0.2

    def test_sarif_formatter_excludes_passed_and_skipped(self, sample_rules_list):
        """Test that SARIF formatter only includes failed results."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "good-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
                execution_time=0.1,
            ),
            ValidationResult(
                rule=rule,
                resource={"resource_type": rule.resource_type, "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
                execution_time=0.0,
            ),
        ]

        formatter = SARIFFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        run = data["runs"][0]

        # Should not include passed or skipped results
        assert len(run["results"]) == 0
        assert run["invocations"][0]["executionSuccessful"] is True

    def test_sarif_formatter_rule_definitions(self, sample_rules_list):
        """Test that SARIF formatter includes rule definitions."""
        rule = sample_rules_list[0]
        results = [
            ValidationResult(
                rule=rule,
                resource={"id": "bad-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Required tag missing",
                execution_time=0.1,
            )
        ]

        formatter = SARIFFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        run = data["runs"][0]
        rules = run["tool"]["driver"]["rules"]

        assert len(rules) == 1
        rule_def = rules[0]
        assert rule_def["id"] == rule.id
        assert "shortDescription" in rule_def
        assert "fullDescription" in rule_def
        assert rule_def["defaultConfiguration"]["level"] == "error"
        assert rule_def["properties"]["resource_type"] == rule.resource_type

    def test_sarif_formatter_severity_mapping(self):
        """Test SARIF formatter severity level mapping."""
        # Create rules with different severities
        error_rule_dict = {
            "id": "error-rule",
            "resource_type": "aws_instance",
            "severity": "error",
            "assert": {"tags": {"Environment": "present"}},
        }
        warning_rule_dict = {
            "id": "warning-rule",
            "resource_type": "aws_instance",
            "severity": "warning",
            "assert": {"tags": {"Environment": "present"}},
        }
        info_rule_dict = {
            "id": "info-rule",
            "resource_type": "aws_instance",
            "severity": "info",
            "assert": {"tags": {"Environment": "present"}},
        }

        error_rule = Rule(error_rule_dict)
        warning_rule = Rule(warning_rule_dict)
        info_rule = Rule(info_rule_dict)

        results = [
            ValidationResult(
                rule=error_rule,
                resource={"id": "instance1", "resource_type": "aws_instance"},
                passed=False,
                message="Error message",
            ),
            ValidationResult(
                rule=warning_rule,
                resource={"id": "instance2", "resource_type": "aws_instance"},
                passed=False,
                message="Warning message",
            ),
            ValidationResult(
                rule=info_rule,
                resource={"id": "instance3", "resource_type": "aws_instance"},
                passed=False,
                message="Info message",
            ),
        ]

        formatter = SARIFFormatter()
        output = formatter.format(results)

        data = json.loads(output)
        run = data["runs"][0]

        # Check result levels
        result_levels = [result["level"] for result in run["results"]]
        assert "error" in result_levels
        assert "warning" in result_levels
        assert "note" in result_levels  # info maps to note in SARIF

        # Check rule definition levels
        rule_levels = [
            rule["defaultConfiguration"]["level"] for rule in run["tool"]["driver"]["rules"]
        ]
        assert "error" in rule_levels
        assert "warning" in rule_levels
        assert "note" in rule_levels

    def test_sarif_formatter_execution_success_status(self, sample_rules_list):
        """Test SARIF formatter execution success status."""
        rule = sample_rules_list[0]

        # Test with failures
        results_with_failures = [
            ValidationResult(
                rule=rule,
                resource={"id": "bad-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Failed validation",
            )
        ]

        formatter = SARIFFormatter()
        output = formatter.format(results_with_failures)
        data = json.loads(output)
        assert data["runs"][0]["invocations"][0]["executionSuccessful"] is False

        # Test without failures
        results_without_failures = [
            ValidationResult(
                rule=rule,
                resource={"id": "good-instance", "resource_type": "aws_instance"},
                passed=True,
                message="Passed validation",
            )
        ]

        output = formatter.format(results_without_failures)
        data = json.loads(output)
        assert data["runs"][0]["invocations"][0]["executionSuccessful"] is True
