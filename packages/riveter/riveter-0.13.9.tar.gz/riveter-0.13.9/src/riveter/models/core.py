"""Core data models for Riveter.

This module defines the fundamental data structures used throughout
the Riveter system, including resources, validation results, and
common types.
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(Enum):
    """Severity levels for validation results."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    def __str__(self) -> str:
        return self.value

    @property
    def priority(self) -> int:
        """Get numeric priority for sorting (higher = more severe)."""
        return {
            Severity.ERROR: 3,
            Severity.WARNING: 2,
            Severity.INFO: 1,
        }[self]


@dataclass(frozen=True)
class SourceLocation:
    """Location information for a resource or rule in source code."""

    file: Path
    line: int
    column: int = 0

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"

    @property
    def file_name(self) -> str:
        """Get just the filename without path."""
        return self.file.name


@dataclass(frozen=True)
class TerraformResource:
    """Represents a Terraform resource with its attributes and metadata."""

    type: str
    name: str
    attributes: dict[str, Any]
    source_location: SourceLocation | None = None

    @property
    def id(self) -> str:
        """Get the resource identifier."""
        return f"{self.type}.{self.name}"

    @property
    def tags(self) -> dict[str, str]:
        """Get resource tags, if any."""
        return self.attributes.get("tags", {})

    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get a resource attribute with optional default."""
        return self.attributes.get(key, default)

    def has_attribute(self, key: str) -> bool:
        """Check if resource has a specific attribute."""
        return key in self.attributes

    def has_tag(self, tag_name: str) -> bool:
        """Check if resource has a specific tag."""
        return tag_name in self.tags

    def get_tag(self, tag_name: str, default: str = "") -> str:
        """Get a tag value with optional default."""
        return self.tags.get(tag_name, default)


@dataclass(frozen=True)
class RuleResult:
    """Result of applying a single rule to a single resource."""

    rule_id: str
    resource: TerraformResource
    passed: bool
    message: str
    severity: Severity
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Get human-readable status."""
        return "PASS" if self.passed else "FAIL"

    @property
    def resource_id(self) -> str:
        """Get the resource identifier."""
        return self.resource.id

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
            "details": self.details,
            "source_location": (
                str(self.resource.source_location) if self.resource.source_location else None
            ),
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Summary statistics for a validation run."""

    total_rules: int
    total_resources: int
    passed: int
    failed: int
    errors: int
    warnings: int
    info: int
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None

    @property
    def total_results(self) -> int:
        """Get total number of validation results."""
        return self.passed + self.failed

    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_results == 0:
            return 100.0
        return (self.passed / self.total_results) * 100.0

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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_rules": self.total_rules,
            "total_resources": self.total_resources,
            "total_results": self.total_results,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "success_rate": round(self.success_rate, 2),
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


@dataclass(frozen=True)
class ValidationResult:
    """Complete result of a validation run."""

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

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "summary": self.summary.to_dict(),
            "results": [result.to_dict() for result in self.results],
            "metadata": self.metadata,
        }


# Type aliases for common patterns
ResourceDict = dict[str, Any]
RuleDict = dict[str, Any]
ConfigDict = dict[str, Any]
AttributeValue = str | int | float | bool | list[Any] | dict[str, Any]
