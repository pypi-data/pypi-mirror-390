"""Rule data models for Riveter.

This module defines data structures for validation rules, rule packs,
and rule-related metadata.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from .core import Severity


class RuleScope(Enum):
    """Scope of rule application."""

    RESOURCE = "resource"
    CONFIGURATION = "configuration"
    GLOBAL = "global"

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class RuleCondition:
    """A single condition within a rule."""

    operator: str
    field: str
    value: Any
    negate: bool = False

    def __str__(self) -> str:
        op_str = f"NOT {self.operator}" if self.negate else self.operator
        return f"{self.field} {op_str} {self.value}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "operator": self.operator,
            "field": self.field,
            "value": self.value,
            "negate": self.negate,
        }


@dataclass(frozen=True)
class RuleFilter:
    """Filter conditions for rule application."""

    conditions: list[RuleCondition] = field(default_factory=list)
    logic: str = "AND"  # AND or OR

    @property
    def is_empty(self) -> bool:
        """Check if filter has no conditions."""
        return len(self.conditions) == 0

    def __str__(self) -> str:
        if self.is_empty:
            return "No filter"

        condition_strs = [str(condition) for condition in self.conditions]
        return f" {self.logic} ".join(condition_strs)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "conditions": [condition.to_dict() for condition in self.conditions],
            "logic": self.logic,
        }


@dataclass(frozen=True)
class RuleAssertion:
    """Assertion conditions for rule validation."""

    conditions: list[RuleCondition] = field(default_factory=list)
    logic: str = "AND"  # AND or OR

    @property
    def is_empty(self) -> bool:
        """Check if assertion has no conditions."""
        return len(self.conditions) == 0

    def __str__(self) -> str:
        if self.is_empty:
            return "No assertion"

        condition_strs = [str(condition) for condition in self.conditions]
        return f" {self.logic} ".join(condition_strs)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "conditions": [condition.to_dict() for condition in self.conditions],
            "logic": self.logic,
        }


@dataclass(frozen=True)
class RuleMetadata:
    """Metadata for a validation rule."""

    category: str | None = None
    subcategory: str | None = None
    framework: str | None = None
    control_id: str | None = None
    references: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    author: str | None = None
    created_date: str | None = None
    modified_date: str | None = None
    version: str = "1.0"

    def has_tag(self, tag: str) -> bool:
        """Check if rule has a specific tag."""
        return tag in self.tags

    def has_reference(self, reference: str) -> bool:
        """Check if rule has a specific reference."""
        return reference in self.references

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "framework": self.framework,
            "control_id": self.control_id,
            "references": self.references,
            "tags": self.tags,
            "author": self.author,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "version": self.version,
        }


@dataclass(frozen=True)
class Rule:
    """A validation rule for Terraform resources."""

    id: str
    description: str
    resource_type: str
    severity: Severity = Severity.ERROR
    scope: RuleScope = RuleScope.RESOURCE

    # Rule logic
    filter: RuleFilter = field(default_factory=RuleFilter)
    assertion: RuleAssertion = field(default_factory=RuleAssertion)

    # Metadata
    metadata: RuleMetadata = field(default_factory=RuleMetadata)

    # Configuration
    enabled: bool = True

    def __post_init__(self):
        """Validate rule after initialization."""
        if not self.id:
            raise ValueError("Rule ID cannot be empty")
        if not self.description:
            raise ValueError("Rule description cannot be empty")
        if not self.resource_type:
            raise ValueError("Rule resource_type cannot be empty")

    @property
    def applies_to_all_resources(self) -> bool:
        """Check if rule applies to all resource types."""
        return self.resource_type == "*"

    @property
    def has_filter(self) -> bool:
        """Check if rule has filter conditions."""
        return not self.filter.is_empty

    @property
    def has_assertion(self) -> bool:
        """Check if rule has assertion conditions."""
        return not self.assertion.is_empty

    def applies_to_resource_type(self, resource_type: str) -> bool:
        """Check if rule applies to a specific resource type."""
        return self.applies_to_all_resources or self.resource_type == resource_type

    def __str__(self) -> str:
        return f"Rule({self.id}: {self.description})"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "description": self.description,
            "resource_type": self.resource_type,
            "severity": self.severity.value,
            "scope": self.scope.value,
            "filter": self.filter.to_dict(),
            "assertion": self.assertion.to_dict(),
            "metadata": self.metadata.to_dict(),
            "enabled": self.enabled,
        }


@dataclass(frozen=True)
class RulePack:
    """A collection of related validation rules."""

    name: str
    description: str
    version: str
    rules: list[Rule]

    # Metadata
    author: str | None = None
    framework: str | None = None
    category: str | None = None
    tags: list[str] = field(default_factory=list)

    # Source information
    source_file: Path | None = None

    def __post_init__(self):
        """Validate rule pack after initialization."""
        if not self.name:
            raise ValueError("Rule pack name cannot be empty")
        if not self.description:
            raise ValueError("Rule pack description cannot be empty")
        if not self.version:
            raise ValueError("Rule pack version cannot be empty")

    @property
    def rule_count(self) -> int:
        """Get total number of rules."""
        return len(self.rules)

    @property
    def enabled_rule_count(self) -> int:
        """Get number of enabled rules."""
        return sum(1 for rule in self.rules if rule.enabled)

    @property
    def rule_ids(self) -> set[str]:
        """Get set of all rule IDs."""
        return {rule.id for rule in self.rules}

    @property
    def resource_types(self) -> set[str]:
        """Get set of all resource types covered by rules."""
        return {rule.resource_type for rule in self.rules if rule.resource_type != "*"}

    @property
    def severities(self) -> set[Severity]:
        """Get set of all severities used by rules."""
        return {rule.severity for rule in self.rules}

    def get_rule_by_id(self, rule_id: str) -> Rule | None:
        """Get a rule by its ID."""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None

    def get_rules_by_resource_type(self, resource_type: str) -> list[Rule]:
        """Get all rules that apply to a specific resource type."""
        return [rule for rule in self.rules if rule.applies_to_resource_type(resource_type)]

    def get_rules_by_severity(self, severity: Severity) -> list[Rule]:
        """Get all rules with a specific severity."""
        return [rule for rule in self.rules if rule.severity == severity]

    def get_enabled_rules(self) -> list[Rule]:
        """Get all enabled rules."""
        return [rule for rule in self.rules if rule.enabled]

    def has_rule(self, rule_id: str) -> bool:
        """Check if pack contains a specific rule."""
        return rule_id in self.rule_ids

    def has_tag(self, tag: str) -> bool:
        """Check if pack has a specific tag."""
        return tag in self.tags

    def __str__(self) -> str:
        return f"RulePack({self.name} v{self.version}: {self.rule_count} rules)"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "framework": self.framework,
            "category": self.category,
            "tags": self.tags,
            "source_file": str(self.source_file) if self.source_file else None,
            "metadata": {
                "rule_count": self.rule_count,
                "enabled_rule_count": self.enabled_rule_count,
                "resource_types": list(self.resource_types),
                "severities": [s.value for s in self.severities],
            },
            "rules": [rule.to_dict() for rule in self.rules],
        }
