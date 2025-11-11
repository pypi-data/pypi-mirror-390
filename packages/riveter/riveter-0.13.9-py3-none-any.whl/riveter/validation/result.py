"""Result classes for validation operations.

This module provides immutable result classes that capture the outcomes
of validation operations with comprehensive type safety.
"""

import time
from dataclasses import dataclass, field
from typing import Any

from riveter.models.core import Severity, TerraformResource
from riveter.models.rules import Rule


@dataclass(frozen=True)
class AssertionResult:
    """Result of evaluating a single assertion within a rule.

    This class captures detailed information about each individual assertion
    within a rule, providing granular feedback about what passed or failed.
    """

    property_path: str
    operator: str
    expected: Any
    actual: Any
    passed: bool
    message: str
    execution_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "property_path": self.property_path,
            "operator": self.operator,
            "expected": self.expected,
            "actual": self.actual,
            "passed": self.passed,
            "message": self.message,
            "execution_time": self.execution_time,
        }


@dataclass(frozen=True)
class RuleResult:
    """Result of evaluating a single rule against a single resource.

    This class encapsulates all information about a single validation operation,
    including the rule that was applied, the resource that was checked, whether
    the validation passed, and detailed assertion results.
    """

    rule: Rule
    resource: TerraformResource
    passed: bool
    message: str
    assertion_results: list[AssertionResult] = field(default_factory=list)
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def rule_id(self) -> str:
        """Get the rule ID."""
        return self.rule.id

    @property
    def resource_id(self) -> str:
        """Get the resource ID."""
        return self.resource.id

    @property
    def severity(self) -> Severity:
        """Get the rule severity."""
        return self.rule.severity

    @property
    def status(self) -> str:
        """Get human-readable status."""
        return "PASS" if self.passed else "FAIL"

    @property
    def failed_assertions(self) -> list[AssertionResult]:
        """Get all failed assertions."""
        return [ar for ar in self.assertion_results if not ar.passed]

    @property
    def passed_assertions(self) -> list[AssertionResult]:
        """Get all passed assertions."""
        return [ar for ar in self.assertion_results if ar.passed]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "rule_id": self.rule_id,
            "resource_id": self.resource_id,
            "resource_type": self.resource.type,
            "resource_name": self.resource.name,
            "passed": self.passed,
            "status": self.status,
            "message": self.message,
            "severity": self.severity.value,
            "execution_time": self.execution_time,
            "assertion_results": [ar.to_dict() for ar in self.assertion_results],
            "metadata": self.metadata,
            "source_location": (
                str(self.resource.source_location) if self.resource.source_location else None
            ),
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Summary statistics for a validation run."""

    total_rules: int
    total_resources: int
    total_evaluations: int
    passed: int
    failed: int
    errors: int
    warnings: int
    info: int
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_evaluations == 0:
            return 100.0
        return (self.passed / self.total_evaluations) * 100.0

    @property
    def duration(self) -> float | None:
        """Get validation duration in seconds."""
        if self.end_time is not None:
            return self.end_time - self.start_time
        return None

    @property
    def has_failures(self) -> bool:
        """Check if there are any failures."""
        return self.failed > 0 or self.errors > 0

    @property
    def evaluations_per_second(self) -> float | None:
        """Get evaluations per second."""
        duration = self.duration
        if duration and duration > 0:
            return self.total_evaluations / duration
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_rules": self.total_rules,
            "total_resources": self.total_resources,
            "total_evaluations": self.total_evaluations,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "success_rate": round(self.success_rate, 2),
            "duration": self.duration,
            "evaluations_per_second": self.evaluations_per_second,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Complete result of a validation run.

    This class contains all results from validating resources against rules,
    including summary statistics and detailed per-rule results.
    """

    summary: ValidationSummary
    results: list[RuleResult]
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def passed_results(self) -> list[RuleResult]:
        """Get all passed results."""
        return [r for r in self.results if r.passed]

    @property
    def failed_results(self) -> list[RuleResult]:
        """Get all failed results."""
        return [r for r in self.results if not r.passed]

    @property
    def results_by_severity(self) -> dict[Severity, list[RuleResult]]:
        """Group results by severity."""
        by_severity: dict[Severity, list[RuleResult]] = {
            Severity.ERROR: [],
            Severity.WARNING: [],
            Severity.INFO: [],
        }

        for result in self.results:
            by_severity[result.severity].append(result)

        return by_severity

    @property
    def results_by_resource(self) -> dict[str, list[RuleResult]]:
        """Group results by resource ID."""
        by_resource: dict[str, list[RuleResult]] = {}

        for result in self.results:
            resource_id = result.resource_id
            if resource_id not in by_resource:
                by_resource[resource_id] = []
            by_resource[resource_id].append(result)

        return by_resource

    @property
    def results_by_rule(self) -> dict[str, list[RuleResult]]:
        """Group results by rule ID."""
        by_rule: dict[str, list[RuleResult]] = {}

        for result in self.results:
            rule_id = result.rule_id
            if rule_id not in by_rule:
                by_rule[rule_id] = []
            by_rule[rule_id].append(result)

        return by_rule

    def get_results_for_resource(self, resource_id: str) -> list[RuleResult]:
        """Get all results for a specific resource."""
        return [r for r in self.results if r.resource_id == resource_id]

    def get_results_for_rule(self, rule_id: str) -> list[RuleResult]:
        """Get all results for a specific rule."""
        return [r for r in self.results if r.rule_id == rule_id]

    def get_results_by_severity(self, severity: Severity) -> list[RuleResult]:
        """Get all results with specific severity."""
        return [r for r in self.results if r.severity == severity]

    def filter_by_status(self, passed: bool) -> list[RuleResult]:
        """Filter results by pass/fail status."""
        return [r for r in self.results if r.passed == passed]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "summary": self.summary.to_dict(),
            "results": [result.to_dict() for result in self.results],
            "metadata": self.metadata,
        }
