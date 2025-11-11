"""Modern output formatters with protocol-based interfaces.

This module provides modernized output formatters that implement
the FormatterProtocol interface and work with the new ValidationResult
data structures while maintaining backward compatibility.
"""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any

from rich.console import Console
from rich.table import Table

from ..models.core import RuleResult, Severity, ValidationResult
from .protocols import FormatterProtocol


class OutputFormatter(ABC):
    """Abstract base class for output formatters.

    This class provides a base implementation of the FormatterProtocol
    and common functionality for all formatters.
    """

    @abstractmethod
    def format(self, result: ValidationResult) -> str:
        """Format validation result for output.

        Args:
            result: Validation result to format

        Returns:
            Formatted output string
        """

    def format_summary(self, result: ValidationResult) -> str:
        """Format just the summary portion of results.

        Args:
            result: Validation result to format

        Returns:
            Formatted summary string
        """
        summary = result.summary
        return f"Summary: {summary.passed}/{summary.total_results} rules passed validation" + (
            f" ({summary.failed} failed)" if summary.failed > 0 else ""
        )

    @property
    @abstractmethod
    def format_name(self) -> str:
        """Get the name of this output format."""

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Get the recommended file extension for this format."""

    def _calculate_legacy_summary(self, result: ValidationResult) -> dict[str, int]:
        """Calculate summary statistics in legacy format for compatibility."""
        # Count skipped results from details
        skipped = sum(
            1
            for r in result.results
            if r.details.get("is_skipped", False) or r.message.startswith("SKIPPED:")
        )

        return {
            "total": len(result.results),
            "passed": result.summary.passed,
            "failed": result.summary.failed,
            "skipped": skipped,
            "active_checks": result.summary.total_results,
        }


class TableFormatter(OutputFormatter):
    """Rich table formatter for console output.

    This formatter creates a rich table display that matches the
    original table output format for backward compatibility.
    """

    def __init__(self, console_instance: Console | None = None) -> None:
        """Initialize table formatter.

        Args:
            console_instance: Optional Rich console instance
        """
        self._console = console_instance or Console()

    @property
    def format_name(self) -> str:
        """Get the name of this output format."""
        return "table"

    @property
    def file_extension(self) -> str:
        """Get the recommended file extension for this format."""
        return ".txt"

    def format(self, result: ValidationResult) -> str:
        """Format validation result as a rich table.

        Args:
            result: Validation result to format

        Returns:
            Formatted table string (note: this captures rich output)
        """
        if not result.results:
            # For empty results, print directly to console for backward compatibility
            self._console.print("[green]All rules passed![/green]")
            return ""

        # Create main results table
        table = Table(title="Rule Validation Results")
        table.add_column("Rule ID", style="cyan")
        table.add_column("Resource Type", style="blue")
        table.add_column("Resource ID", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Message", style="white")

        skipped_results = []

        for rule_result in result.results:
            # Check if this is a skipped rule
            is_skipped = rule_result.details.get(
                "is_skipped", False
            ) or rule_result.message.startswith("SKIPPED:")

            if is_skipped:
                skipped_results.append(rule_result)
                status_style = "yellow"
                message_style = "yellow"
                status_text = "⚠️ SKIPPED"
            else:
                status_style = "green" if rule_result.passed else "red"
                message_style = "green" if rule_result.passed else "red"
                status_text = "✅ PASSED" if rule_result.passed else "❌ FAILED"

            table.add_row(
                rule_result.rule_id,
                rule_result.resource.type,
                rule_result.resource.name,
                f"[{status_style}]{status_text}[/{status_style}]",
                f"[{message_style}]{rule_result.message}[/{message_style}]",
            )

        # For table format, we need to print directly to console for backward compatibility
        # The tests expect console.print to be called, not to return a string
        self._console.print(table)

        # Add summary
        summary = result.summary
        skipped_count = len(skipped_results)
        active_checks = summary.total_results

        summary_msg = f"\nSummary: [green]{summary.passed}[/green]/[white]{active_checks}[/white] rules passed validation"
        self._console.print(summary_msg)

        if summary.failed > 0:
            self._console.print(f"[red]{summary.failed}[/red] rules failed validation")

        if skipped_count > 0:
            skipped_msg = f"[yellow]{skipped_count}[/yellow] rules were skipped (no matching resources found):"
            self._console.print(skipped_msg)

            # Create skipped rules table
            skipped_table = Table(title="Skipped Rules", box=None)
            skipped_table.add_column("Rule ID", style="cyan")
            skipped_table.add_column("Resource Type", style="blue")
            skipped_table.add_column("Description", style="white")

            for rule_result in skipped_results:
                # Try to get description from rule details or use a default
                description = rule_result.details.get("description", "No description available")

                skipped_table.add_row(rule_result.rule_id, rule_result.resource.type, description)

            self._console.print(skipped_table)

        # Return empty string since we printed directly to console
        return ""


class JSONFormatter(OutputFormatter):
    """JSON formatter for programmatic consumption."""

    @property
    def format_name(self) -> str:
        """Get the name of this output format."""
        return "json"

    @property
    def file_extension(self) -> str:
        """Get the recommended file extension for this format."""
        return ".json"

    def format(self, result: ValidationResult) -> str:
        """Format results as JSON."""
        summary = self._calculate_legacy_summary(result)

        output = {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "summary": summary,
            "results": [self._convert_result_to_legacy_dict(r) for r in result.results],
        }

        return json.dumps(output, indent=2, ensure_ascii=False)

    def _convert_result_to_legacy_dict(self, rule_result: RuleResult) -> dict[str, Any]:
        """Convert modern RuleResult to legacy dictionary format."""
        return {
            "rule_id": rule_result.rule_id,
            "resource_type": rule_result.resource.type,
            "resource_id": rule_result.resource.name,
            "passed": rule_result.passed,
            "severity": rule_result.severity.value,
            "message": rule_result.message,
            "execution_time": rule_result.details.get("execution_time", 0.0),
            "assertion_results": rule_result.details.get("assertion_results", []),
        }


class JUnitXMLFormatter(OutputFormatter):
    """JUnit XML formatter for CI/CD integration."""

    @property
    def format_name(self) -> str:
        """Get the name of this output format."""
        return "junit"

    @property
    def file_extension(self) -> str:
        """Get the recommended file extension for this format."""
        return ".xml"

    def format(self, result: ValidationResult) -> str:
        """Format results as JUnit XML."""
        summary = self._calculate_legacy_summary(result)

        # Create root testsuite element
        testsuite = ET.Element("testsuite")
        testsuite.set("name", "Riveter Infrastructure Rules")
        testsuite.set("tests", str(summary["active_checks"]))
        testsuite.set("failures", str(summary["failed"]))
        testsuite.set("skipped", str(summary["skipped"]))
        testsuite.set("time", str(result.summary.duration or 0.0))
        testsuite.set("timestamp", datetime.now(UTC).isoformat().replace("+00:00", "Z"))

        for rule_result in result.results:
            # Skip the skipped results in JUnit XML as they're not real test cases
            if rule_result.details.get("is_skipped", False) or rule_result.message.startswith(
                "SKIPPED:"
            ):
                continue

            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("classname", f"riveter.{rule_result.resource.type}")
            testcase.set("name", rule_result.rule_id)
            testcase.set("time", str(rule_result.details.get("execution_time", 0.0)))

            # Add resource information as properties
            properties = ET.SubElement(testcase, "properties")

            prop_resource_id = ET.SubElement(properties, "property")
            prop_resource_id.set("name", "resource_id")
            prop_resource_id.set("value", rule_result.resource.name)

            prop_severity = ET.SubElement(properties, "property")
            prop_severity.set("name", "severity")
            prop_severity.set("value", rule_result.severity.value)

            if not rule_result.passed:
                failure = ET.SubElement(testcase, "failure")
                failure.set("message", rule_result.message)
                failure.set("type", "RuleViolation")

                # Add detailed assertion results if available
                assertion_results = rule_result.details.get("assertion_results", [])
                if assertion_results:
                    failure_details = []
                    for ar in assertion_results:
                        if hasattr(ar, "passed") and not ar.passed:
                            failure_details.append(
                                f"Property: {getattr(ar, 'property_path', 'unknown')}\n"
                                f"Operator: {getattr(ar, 'operator', 'unknown')}\n"
                                f"Expected: {getattr(ar, 'expected', 'unknown')}\n"
                                f"Actual: {getattr(ar, 'actual', 'unknown')}\n"
                                f"Message: {getattr(ar, 'message', 'unknown')}\n"
                            )
                    if failure_details:
                        failure.text = "\n".join(failure_details)
                    else:
                        failure.text = rule_result.message
                else:
                    failure.text = rule_result.message

        # Convert to string
        return ET.tostring(testsuite, encoding="unicode", xml_declaration=True)


class SARIFFormatter(OutputFormatter):
    """SARIF formatter for security scanning tools."""

    @property
    def format_name(self) -> str:
        """Get the name of this output format."""
        return "sarif"

    @property
    def file_extension(self) -> str:
        """Get the recommended file extension for this format."""
        return ".sarif"

    def format(self, result: ValidationResult) -> str:
        """Format results as SARIF (Static Analysis Results Interchange Format)."""
        summary = self._calculate_legacy_summary(result)

        # SARIF 2.1.0 format
        sarif_output = {
            "version": "2.1.0",
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Riveter",
                            "version": "0.1.0",
                            "informationUri": "https://github.com/your-org/riveter",
                            "shortDescription": {"text": "Infrastructure Rule Enforcement as Code"},
                            "fullDescription": {
                                "text": (
                                    "Riveter validates Terraform configurations "
                                    "against custom YAML rules"
                                )
                            },
                            "rules": self._create_sarif_rules(result.results),
                        }
                    },
                    "results": self._create_sarif_results(result.results),
                    "invocations": [
                        {
                            "executionSuccessful": summary["failed"] == 0,
                            "endTimeUtc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                        }
                    ],
                }
            ],
        }

        return json.dumps(sarif_output, indent=2, ensure_ascii=False)

    def _create_sarif_rules(self, results: list[RuleResult]) -> list[dict[str, Any]]:
        """Create SARIF rule definitions from validation results."""
        rules_dict = {}

        for rule_result in results:
            if rule_result.details.get("is_skipped", False) or rule_result.message.startswith(
                "SKIPPED:"
            ):
                continue

            rule_id = rule_result.rule_id
            if rule_id not in rules_dict:
                # Map severity levels to SARIF levels
                severity_mapping = {
                    "error": "error",
                    "warning": "warning",
                    "info": "note",
                }

                rules_dict[rule_id] = {
                    "id": rule_id,
                    "shortDescription": {
                        "text": rule_result.details.get("description", f"Rule {rule_id}")
                    },
                    "fullDescription": {
                        "text": rule_result.details.get(
                            "description",
                            f"Infrastructure rule validation for {rule_id}",
                        )
                    },
                    "defaultConfiguration": {
                        "level": severity_mapping.get(rule_result.severity.value, "warning")
                    },
                    "properties": {
                        "category": "infrastructure",
                        "resource_type": rule_result.resource.type,
                    },
                }

        return list(rules_dict.values())

    def _create_sarif_results(self, results: list[RuleResult]) -> list[dict[str, Any]]:
        """Create SARIF result entries from validation results."""
        sarif_results = []

        for rule_result in results:
            # Skip successful validations and skipped rules in SARIF
            if (
                rule_result.passed
                or rule_result.details.get("is_skipped", False)
                or rule_result.message.startswith("SKIPPED:")
            ):
                continue

            # Map severity levels to SARIF levels
            severity_mapping = {
                "error": "error",
                "warning": "warning",
                "info": "note",
            }

            sarif_result = {
                "ruleId": rule_result.rule_id,
                "level": severity_mapping.get(rule_result.severity.value, "warning"),
                "message": {"text": rule_result.message},
                "locations": [
                    {
                        "logicalLocations": [
                            {
                                "name": rule_result.resource.name,
                                "fullyQualifiedName": rule_result.resource.id,
                                "kind": "resource",
                            }
                        ]
                    }
                ],
                "properties": {
                    "resource_type": rule_result.resource.type,
                    "resource_id": rule_result.resource.name,
                    "execution_time": rule_result.details.get("execution_time", 0.0),
                },
            }

            # Add detailed assertion information if available
            assertion_results = rule_result.details.get("assertion_results", [])
            if assertion_results:
                failed_assertions = [
                    ar for ar in assertion_results if hasattr(ar, "passed") and not ar.passed
                ]
                if failed_assertions:
                    sarif_result["properties"]["failed_assertions"] = [
                        {
                            "property_path": getattr(ar, "property_path", "unknown"),
                            "operator": getattr(ar, "operator", "unknown"),
                            "expected": str(getattr(ar, "expected", "unknown")),
                            "actual": str(getattr(ar, "actual", "unknown")),
                            "message": getattr(ar, "message", "unknown"),
                        }
                        for ar in failed_assertions
                    ]

            sarif_results.append(sarif_result)

        return sarif_results
