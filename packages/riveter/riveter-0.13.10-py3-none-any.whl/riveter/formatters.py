"""Output formatters for validation results."""

import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List

from .scanner import ValidationResult


class OutputFormatter(ABC):
    """Base class for output formatters."""

    @abstractmethod
    def format(self, results: List[ValidationResult]) -> str:
        """Format validation results into the desired output format.

        Args:
            results: List of validation results to format

        Returns:
            Formatted string representation of the results
        """
        pass

    def _calculate_summary(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Calculate summary statistics for results."""
        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed and not r.message.startswith("SKIPPED:"))
        skipped = sum(1 for r in results if r.message.startswith("SKIPPED:"))
        total = len(results)
        active_checks = total - skipped

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "active_checks": active_checks,
        }


class JSONFormatter(OutputFormatter):
    """JSON formatter for programmatic consumption."""

    def format(self, results: List[ValidationResult]) -> str:
        """Format results as JSON."""
        summary = self._calculate_summary(results)

        output = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "summary": summary,
            "results": [result.to_dict() for result in results],
        }

        return json.dumps(output, indent=2, ensure_ascii=False)


class JUnitXMLFormatter(OutputFormatter):
    """JUnit XML formatter for CI/CD integration."""

    def format(self, results: List[ValidationResult]) -> str:
        """Format results as JUnit XML."""
        summary = self._calculate_summary(results)

        # Create root testsuite element
        testsuite = ET.Element("testsuite")
        testsuite.set("name", "Riveter Infrastructure Rules")
        testsuite.set("tests", str(summary["active_checks"]))
        testsuite.set("failures", str(summary["failed"]))
        testsuite.set("skipped", str(summary["skipped"]))
        testsuite.set("time", str(sum(r.execution_time for r in results)))
        testsuite.set("timestamp", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))

        for result in results:
            # Skip the skipped results in JUnit XML as they're not real test cases
            if result.message.startswith("SKIPPED:"):
                continue

            testcase = ET.SubElement(testsuite, "testcase")
            testcase.set("classname", f"riveter.{result.resource.get('resource_type', 'unknown')}")
            testcase.set("name", f"{result.rule.id}")
            testcase.set("time", str(result.execution_time))

            # Add resource information as properties
            properties = ET.SubElement(testcase, "properties")

            prop_resource_id = ET.SubElement(properties, "property")
            prop_resource_id.set("name", "resource_id")
            prop_resource_id.set("value", result.resource.get("id", ""))

            prop_severity = ET.SubElement(properties, "property")
            prop_severity.set("name", "severity")
            prop_severity.set("value", result.severity.value)

            if not result.passed:
                failure = ET.SubElement(testcase, "failure")
                failure.set("message", result.message)
                failure.set("type", "RuleViolation")

                # Add detailed assertion results if available
                if result.assertion_results:
                    failure_details = []
                    for ar in result.assertion_results:
                        if not ar.passed:
                            failure_details.append(
                                f"Property: {ar.property_path}\n"
                                f"Operator: {ar.operator}\n"
                                f"Expected: {ar.expected}\n"
                                f"Actual: {ar.actual}\n"
                                f"Message: {ar.message}\n"
                            )
                    failure.text = "\n".join(failure_details)
                else:
                    failure.text = result.message

        # Convert to string
        return ET.tostring(testsuite, encoding="unicode", xml_declaration=True)


class SARIFFormatter(OutputFormatter):
    """SARIF formatter for security scanning tools."""

    def format(self, results: List[ValidationResult]) -> str:
        """Format results as SARIF (Static Analysis Results Interchange Format)."""
        summary = self._calculate_summary(results)

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
                            "rules": self._create_sarif_rules(results),
                        }
                    },
                    "results": self._create_sarif_results(results),
                    "invocations": [
                        {
                            "executionSuccessful": summary["failed"] == 0,
                            "endTimeUtc": datetime.now(timezone.utc)
                            .isoformat()
                            .replace("+00:00", "Z"),
                        }
                    ],
                }
            ],
        }

        return json.dumps(sarif_output, indent=2, ensure_ascii=False)

    def _create_sarif_rules(self, results: List[ValidationResult]) -> List[Dict[str, Any]]:
        """Create SARIF rule definitions from validation results."""
        rules_dict = {}

        for result in results:
            if result.message.startswith("SKIPPED:"):
                continue

            rule_id = result.rule.id
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
                        "text": getattr(result.rule, "description", f"Rule {rule_id}")
                    },
                    "fullDescription": {
                        "text": getattr(
                            result.rule,
                            "description",
                            f"Infrastructure rule validation for {rule_id}",
                        )
                    },
                    "defaultConfiguration": {
                        "level": severity_mapping.get(result.severity.value, "warning")
                    },
                    "properties": {
                        "category": "infrastructure",
                        "resource_type": result.rule.resource_type,
                    },
                }

        return list(rules_dict.values())

    def _create_sarif_results(self, results: List[ValidationResult]) -> List[Dict[str, Any]]:
        """Create SARIF result entries from validation results."""
        sarif_results = []

        for result in results:
            # Skip successful validations and skipped rules in SARIF
            if result.passed or result.message.startswith("SKIPPED:"):
                continue

            # Map severity levels to SARIF levels
            severity_mapping = {
                "error": "error",
                "warning": "warning",
                "info": "note",
            }

            sarif_result = {
                "ruleId": result.rule.id,
                "level": severity_mapping.get(result.severity.value, "warning"),
                "message": {"text": result.message},
                "locations": [
                    {
                        "logicalLocations": [
                            {
                                "name": result.resource.get("id", "unknown"),
                                "fullyQualifiedName": (
                                    f"{result.resource.get('resource_type', 'unknown')}"
                                    f".{result.resource.get('id', 'unknown')}"
                                ),
                                "kind": "resource",
                            }
                        ]
                    }
                ],
                "properties": {
                    "resource_type": result.resource.get("resource_type"),
                    "resource_id": result.resource.get("id"),
                    "execution_time": result.execution_time,
                },
            }

            # Add detailed assertion information if available
            if result.assertion_results:
                failed_assertions = [ar for ar in result.assertion_results if not ar.passed]
                if failed_assertions:
                    sarif_result["properties"]["failed_assertions"] = [
                        {
                            "property_path": ar.property_path,
                            "operator": ar.operator,
                            "expected": str(ar.expected),
                            "actual": str(ar.actual),
                            "message": ar.message,
                        }
                        for ar in failed_assertions
                    ]

            sarif_results.append(sarif_result)

        return sarif_results
