"""Rule filtering and selection utilities."""

import fnmatch
import re
from typing import Any, Dict, List, Optional

from .rules import Rule, Severity


class RuleFilter:
    """Filters rules based on various criteria."""

    def __init__(
        self,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        min_severity: str = "info",
        environment_context: Optional[Dict[str, Any]] = None,
    ):
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.min_severity = self._parse_severity(min_severity)
        self.environment_context = environment_context or {}

    def _parse_severity(self, severity_str: str) -> Severity:
        """Parse severity string into Severity enum."""
        try:
            return Severity(severity_str.lower())
        except ValueError as e:
            raise ValueError(
                f"Invalid severity '{severity_str}'. Must be one of: error, warning, info"
            ) from e

    def filter_rules(self, rules: List[Rule]) -> List[Rule]:
        """Filter rules based on all configured criteria."""
        filtered_rules = []

        for rule in rules:
            # Check severity filter
            if not self._passes_severity_filter(rule):
                continue

            # Check include patterns
            if self.include_patterns and not self._matches_include_patterns(rule):
                continue

            # Check exclude patterns
            if self.exclude_patterns and self._matches_exclude_patterns(rule):
                continue

            # Check environment-specific filters
            if not self._passes_environment_filter(rule):
                continue

            filtered_rules.append(rule)

        return filtered_rules

    def _passes_severity_filter(self, rule: Rule) -> bool:
        """Check if rule passes minimum severity filter."""
        severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}

        return severity_order[rule.severity] >= severity_order[self.min_severity]

    def _matches_include_patterns(self, rule: Rule) -> bool:
        """Check if rule matches any include pattern."""
        return any(self._matches_pattern(rule, pattern) for pattern in self.include_patterns)

    def _matches_exclude_patterns(self, rule: Rule) -> bool:
        """Check if rule matches any exclude pattern."""
        return any(self._matches_pattern(rule, pattern) for pattern in self.exclude_patterns)

    def _matches_pattern(self, rule: Rule, pattern: str) -> bool:
        """Check if rule matches a specific pattern."""
        # Support different pattern types
        if pattern.startswith("id:"):
            # Match by rule ID
            id_pattern = pattern[3:]
            return fnmatch.fnmatch(rule.id, id_pattern)

        elif pattern.startswith("type:"):
            # Match by resource type
            type_pattern = pattern[5:]
            return fnmatch.fnmatch(rule.resource_type, type_pattern)

        elif pattern.startswith("severity:"):
            # Match by severity
            severity_pattern = pattern[9:].lower()
            return rule.severity.value == severity_pattern

        elif pattern.startswith("tag:"):
            # Match by metadata tag
            tag_pattern = pattern[4:]
            tags = rule.metadata.get("tags", [])
            if isinstance(tags, list):
                return any(fnmatch.fnmatch(tag, tag_pattern) for tag in tags)
            return False

        elif pattern.startswith("regex:"):
            # Match by regex on rule ID or description
            regex_pattern = pattern[6:]
            try:
                regex = re.compile(regex_pattern, re.IGNORECASE)
                return bool(regex.search(rule.id) or regex.search(rule.description))
            except re.error:
                return False

        else:
            # Default: match against rule ID, description, or resource type
            return (
                fnmatch.fnmatch(rule.id, pattern)
                or fnmatch.fnmatch(rule.description.lower(), pattern.lower())
                or fnmatch.fnmatch(rule.resource_type, pattern)
            )

    def _passes_environment_filter(self, rule: Rule) -> bool:
        """Check if rule passes environment-specific filters."""
        if not self.environment_context:
            return True

        # Check if rule has environment-specific conditions
        rule_environments = rule.metadata.get("environments", [])
        if rule_environments:
            # If rule specifies environments, check if current environment matches
            current_env = self.environment_context.get("environment")
            if current_env and current_env not in rule_environments:
                return False

        # Check environment-specific rule overrides
        env_overrides = rule.metadata.get("environment_overrides", {})
        current_env = self.environment_context.get("environment")

        if current_env and current_env in env_overrides:
            overrides = env_overrides[current_env]

            # Check if rule is disabled for this environment
            if overrides.get("disabled", False):
                return False

            # Check environment-specific severity override
            env_severity = overrides.get("severity")
            if env_severity:
                try:
                    env_severity_enum = Severity(env_severity.lower())
                    severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2}
                    if severity_order[env_severity_enum] < severity_order[self.min_severity]:
                        return False
                except ValueError:
                    pass  # Invalid severity, ignore override

        return True


class RuleSelector:
    """Advanced rule selection with complex criteria."""

    def __init__(self) -> None:
        self.filters: List[RuleFilter] = []

    def add_filter(self, rule_filter: RuleFilter) -> None:
        """Add a rule filter to the selection criteria."""
        self.filters.append(rule_filter)

    def select_rules(self, rules: List[Rule]) -> List[Rule]:
        """Select rules using all configured filters."""
        selected_rules = rules

        for rule_filter in self.filters:
            selected_rules = rule_filter.filter_rules(selected_rules)

        return selected_rules

    def create_environment_filter(
        self, environment: str, resources: List[Dict[str, Any]]
    ) -> RuleFilter:
        """Create a rule filter based on environment context."""
        # Extract environment context from resources
        environment_context = {
            "environment": environment,
            "resource_types": list(set(r.get("type", "") for r in resources)),
            "has_tags": any("tags" in r for r in resources),
            "providers": list(
                set(self._extract_provider(r) for r in resources if self._extract_provider(r))
            ),
        }

        return RuleFilter(environment_context=environment_context)

    def _extract_provider(self, resource: Dict[str, Any]) -> Optional[str]:
        """Extract cloud provider from resource type."""
        resource_type = resource.get("type", "")
        if resource_type.startswith("aws_"):
            return "aws"
        elif resource_type.startswith("azurerm_"):
            return "azure"
        elif resource_type.startswith("google_"):
            return "gcp"
        return None


def create_rule_filter_from_config(config_dict: Dict[str, Any]) -> RuleFilter:
    """Create a RuleFilter from configuration dictionary."""
    return RuleFilter(
        include_patterns=config_dict.get("include_rules", []),
        exclude_patterns=config_dict.get("exclude_rules", []),
        min_severity=config_dict.get("min_severity", "info"),
        environment_context=config_dict.get("environment_context", {}),
    )


def filter_rules_by_patterns(
    rules: List[Rule],
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    min_severity: str = "info",
) -> List[Rule]:
    """Convenience function to filter rules by patterns and severity."""
    rule_filter = RuleFilter(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        min_severity=min_severity,
    )
    return rule_filter.filter_rules(rules)
