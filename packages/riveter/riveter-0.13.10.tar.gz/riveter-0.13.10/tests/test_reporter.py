"""Unit tests for the reporter module."""

from unittest.mock import patch

import pytest

from riveter.reporter import _get_formatter, report_results
from riveter.rules import Rule
from riveter.scanner import ValidationResult


class TestReportResults:
    """Test cases for the report_results function."""

    def test_report_results_empty_list(self):
        """Test reporting with empty results list."""
        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results([])

            # Should print success message and return 0
            mock_console.print.assert_called_once_with("[green]All rules passed![/green]")
            assert exit_code == 0

    def test_report_results_all_passing(self, sample_rules_list, sample_terraform_config):
        """Test reporting with all passing results."""
        # Create passing results
        results = []
        rule = sample_rules_list[0]  # aws_instance rule
        resource = sample_terraform_config["resources"][0]  # web_server

        results.append(
            ValidationResult(rule=rule, resource=resource, passed=True, message="All checks passed")
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should print table and summary, return 0
            assert mock_console.print.call_count >= 2  # Table + summary
            assert exit_code == 0

    def test_report_results_some_failing(self, sample_rules_list):
        """Test reporting with some failing results."""
        results = []
        rule = sample_rules_list[0]

        # Add passing result
        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "good-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
            )
        )

        # Add failing result
        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "bad-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Required tag 'CostCenter' is missing",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should print table and summary, return 1 due to failures
            assert mock_console.print.call_count >= 2
            assert exit_code == 1

    def test_report_results_with_skipped_rules(self, sample_rules_list):
        """Test reporting with skipped rules."""
        results = []
        rule = sample_rules_list[0]

        # Add skipped result
        results.append(
            ValidationResult(
                rule=rule,
                resource={"resource_type": rule.resource_type, "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should print table, summary, and skipped rules table
            assert mock_console.print.call_count >= 3  # Main table + summary + skipped table
            assert exit_code == 0  # Skipped rules don't cause failure exit code

    def test_report_results_mixed_results(self, sample_rules_list):
        """Test reporting with mixed passing, failing, and skipped results."""
        results = []

        # Passing result
        results.append(
            ValidationResult(
                rule=sample_rules_list[0],
                resource={"id": "good-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
            )
        )

        # Failing result
        results.append(
            ValidationResult(
                rule=sample_rules_list[1],
                resource={"id": "bad-bucket", "resource_type": "aws_s3_bucket"},
                passed=False,
                message="Required tag 'Purpose' is missing",
            )
        )

        # Skipped result
        results.append(
            ValidationResult(
                rule=sample_rules_list[2],
                resource={"resource_type": "*", "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should print all tables and return 1 due to failures
            assert mock_console.print.call_count >= 3
            assert exit_code == 1

    def test_report_results_table_structure(self, sample_rules_list):
        """Test that the results table has correct structure."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
            )
        )

        # Capture console output
        with patch("riveter.reporter.console") as mock_console:
            report_results(results)

            # Check that print was called with a Table object
            calls = mock_console.print.call_args_list
            assert len(calls) >= 2  # At least table and summary

            # The first call should be the table
            table_call = calls[0]
            # We can't easily inspect the Table object, but we can verify it was called
            assert table_call is not None

    def test_report_results_summary_calculations(self, sample_rules_list):
        """Test that summary calculations are correct."""
        results = []

        # 2 passing results
        for i in range(2):
            results.append(
                ValidationResult(
                    rule=sample_rules_list[0],
                    resource={"id": f"good-instance-{i}", "resource_type": "aws_instance"},
                    passed=True,
                    message="All checks passed",
                )
            )

        # 1 failing result
        results.append(
            ValidationResult(
                rule=sample_rules_list[1],
                resource={"id": "bad-bucket", "resource_type": "aws_s3_bucket"},
                passed=False,
                message="Required tag 'Purpose' is missing",
            )
        )

        # 1 skipped result
        results.append(
            ValidationResult(
                rule=sample_rules_list[2],
                resource={"resource_type": "*", "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Verify exit code reflects failures
            assert exit_code == 1

            # Check that summary information is printed
            summary_calls = [
                call
                for call in mock_console.print.call_args_list
                if len(call[0]) > 0 and "Summary:" in str(call[0][0])
            ]
            assert len(summary_calls) > 0

    def test_report_results_resource_without_id(self, sample_rules_list):
        """Test reporting with resource that has no ID."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"resource_type": "aws_instance"},  # No ID field
                passed=True,
                message="All checks passed",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should handle missing ID gracefully
            assert exit_code == 0
            assert mock_console.print.call_count >= 2

    def test_report_results_resource_without_type(self, sample_rules_list):
        """Test reporting with resource that has no resource_type."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "test-resource"},  # No resource_type field
                passed=True,
                message="All checks passed",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should handle missing resource_type gracefully
            assert exit_code == 0
            assert mock_console.print.call_count >= 2

    def test_report_results_rule_without_description(self):
        """Test reporting with rule that has no description."""
        rule_dict = {
            "id": "test-rule",
            "resource_type": "aws_instance",
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        results = [
            ValidationResult(
                rule=rule,
                resource={"resource_type": "aws_instance", "id": "N/A"},
                passed=False,
                message="SKIPPED: No matching resources found for this rule",
            )
        ]

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results)

            # Should handle missing description gracefully
            assert exit_code == 0
            assert mock_console.print.call_count >= 3  # Main table + summary + skipped table

    def test_report_results_with_mock_validation_results(self, mock_validation_results):
        """Test reporting using mock validation results fixture."""
        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(mock_validation_results)

            # Should handle the mixed results appropriately
            # mock_validation_results has 2 passing and 1 failing result
            assert exit_code == 1  # Due to failing result
            assert mock_console.print.call_count >= 2

    def test_report_results_json_format(self, sample_rules_list):
        """Test reporting with JSON output format."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
            )
        )

        with patch("builtins.print") as mock_print:
            exit_code = report_results(results, output_format="json")

            # Should print JSON output and return 0
            assert exit_code == 0
            mock_print.assert_called_once()

            # Verify it's valid JSON
            import json

            json_output = mock_print.call_args[0][0]
            data = json.loads(json_output)
            assert "summary" in data
            assert "results" in data

    def test_report_results_junit_format(self, sample_rules_list):
        """Test reporting with JUnit XML output format."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Test failure",
            )
        )

        with patch("builtins.print") as mock_print:
            exit_code = report_results(results, output_format="junit")

            # Should print XML output and return 1 due to failure
            assert exit_code == 1
            mock_print.assert_called_once()

            # Verify it's valid XML
            import xml.etree.ElementTree as ET

            xml_output = mock_print.call_args[0][0]
            root = ET.fromstring(xml_output)
            assert root.tag == "testsuite"

    def test_report_results_sarif_format(self, sample_rules_list):
        """Test reporting with SARIF output format."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=False,
                message="Security issue",
            )
        )

        with patch("builtins.print") as mock_print:
            exit_code = report_results(results, output_format="sarif")

            # Should print SARIF output and return 1 due to failure
            assert exit_code == 1
            mock_print.assert_called_once()

            # Verify it's valid JSON with SARIF structure
            import json

            sarif_output = mock_print.call_args[0][0]
            data = json.loads(sarif_output)
            assert data["version"] == "2.1.0"
            assert "runs" in data

    def test_get_formatter_valid_formats(self):
        """Test _get_formatter with valid format strings."""
        from riveter.formatters import JSONFormatter, JUnitXMLFormatter, SARIFFormatter

        assert isinstance(_get_formatter("json"), JSONFormatter)
        assert isinstance(_get_formatter("JSON"), JSONFormatter)  # Case insensitive
        assert isinstance(_get_formatter("junit"), JUnitXMLFormatter)
        assert isinstance(_get_formatter("sarif"), SARIFFormatter)

    def test_get_formatter_invalid_format(self):
        """Test _get_formatter with invalid format string."""
        with pytest.raises(ValueError, match="Unsupported output format"):
            _get_formatter("invalid")

    def test_report_results_table_format_explicit(self, sample_rules_list):
        """Test that explicitly specifying table format works."""
        results = []
        rule = sample_rules_list[0]

        results.append(
            ValidationResult(
                rule=rule,
                resource={"id": "test-instance", "resource_type": "aws_instance"},
                passed=True,
                message="All checks passed",
            )
        )

        with patch("riveter.reporter.console") as mock_console:
            exit_code = report_results(results, output_format="table")

            # Should use table format (same as default)
            assert exit_code == 0
            assert mock_console.print.call_count >= 2
