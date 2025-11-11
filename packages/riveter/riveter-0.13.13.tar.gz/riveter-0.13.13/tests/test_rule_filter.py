"""Tests for rule filtering functionality."""

import pytest

from riveter.rule_filter import (
    RuleFilter,
    RuleSelector,
    create_rule_filter_from_config,
    filter_rules_by_patterns,
)
from riveter.rules import Rule, Severity


class TestRuleFilter:
    """Test RuleFilter class."""

    @pytest.fixture
    def sample_rules(self):
        """Create sample rules for testing."""
        rules_data = [
            {
                "id": "aws-ec2-security-001",
                "resource_type": "aws_instance",
                "description": "EC2 security rule for production",
                "severity": "error",
                "assert": {"tags": {"Environment": "present"}},
                "metadata": {
                    "tags": ["security", "ec2"],
                    "environments": ["production", "staging"],
                },
            },
            {
                "id": "aws-s3-encryption-001",
                "resource_type": "aws_s3_bucket",
                "description": "S3 encryption requirement",
                "severity": "warning",
                "assert": {"encryption": "present"},
                "metadata": {"tags": ["encryption", "s3"], "environments": ["production"]},
            },
            {
                "id": "test-rule-001",
                "resource_type": "aws_instance",
                "description": "Test rule for development",
                "severity": "info",
                "assert": {"tags": {"Name": "present"}},
                "metadata": {"tags": ["test"], "environments": ["development"]},
            },
            {
                "id": "universal-tagging-001",
                "resource_type": "*",
                "description": "Universal tagging rule",
                "severity": "warning",
                "assert": {"tags": {"Owner": "present"}},
                "metadata": {
                    "tags": ["tagging"],
                    "environment_overrides": {"development": {"disabled": True}},
                },
            },
        ]

        return [Rule(rule_dict) for rule_dict in rules_data]

    def test_filter_by_severity_info(self, sample_rules):
        """Test filtering by info severity (should include all)."""
        rule_filter = RuleFilter(min_severity="info")
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 4
        assert all(rule in filtered_rules for rule in sample_rules)

    def test_filter_by_severity_warning(self, sample_rules):
        """Test filtering by warning severity."""
        rule_filter = RuleFilter(min_severity="warning")
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 3
        # Should exclude the info severity rule
        rule_ids = [rule.id for rule in filtered_rules]
        assert "test-rule-001" not in rule_ids
        assert "aws-ec2-security-001" in rule_ids
        assert "aws-s3-encryption-001" in rule_ids
        assert "universal-tagging-001" in rule_ids

    def test_filter_by_severity_error(self, sample_rules):
        """Test filtering by error severity."""
        rule_filter = RuleFilter(min_severity="error")
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "aws-ec2-security-001"

    def test_filter_by_include_patterns_id(self, sample_rules):
        """Test filtering by include patterns matching rule ID."""
        rule_filter = RuleFilter(include_patterns=["id:*security*"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "aws-ec2-security-001"

    def test_filter_by_include_patterns_type(self, sample_rules):
        """Test filtering by include patterns matching resource type."""
        rule_filter = RuleFilter(include_patterns=["type:aws_instance"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 2
        rule_ids = [rule.id for rule in filtered_rules]
        assert "aws-ec2-security-001" in rule_ids
        assert "test-rule-001" in rule_ids

    def test_filter_by_include_patterns_tag(self, sample_rules):
        """Test filtering by include patterns matching metadata tags."""
        rule_filter = RuleFilter(include_patterns=["tag:encryption"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "aws-s3-encryption-001"

    def test_filter_by_include_patterns_severity(self, sample_rules):
        """Test filtering by include patterns matching severity."""
        rule_filter = RuleFilter(include_patterns=["severity:warning"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 2
        rule_ids = [rule.id for rule in filtered_rules]
        assert "aws-s3-encryption-001" in rule_ids
        assert "universal-tagging-001" in rule_ids

    def test_filter_by_include_patterns_regex(self, sample_rules):
        """Test filtering by include patterns using regex."""
        rule_filter = RuleFilter(include_patterns=["regex:.*encryption.*"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "aws-s3-encryption-001"

    def test_filter_by_include_patterns_wildcard(self, sample_rules):
        """Test filtering by include patterns using wildcards."""
        rule_filter = RuleFilter(include_patterns=["*security*"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "aws-ec2-security-001"

    def test_filter_by_exclude_patterns(self, sample_rules):
        """Test filtering by exclude patterns."""
        rule_filter = RuleFilter(exclude_patterns=["*test*"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 3
        rule_ids = [rule.id for rule in filtered_rules]
        assert "test-rule-001" not in rule_ids

    def test_filter_by_include_and_exclude_patterns(self, sample_rules):
        """Test filtering by both include and exclude patterns."""
        rule_filter = RuleFilter(
            include_patterns=["type:aws_instance"], exclude_patterns=["*test*"]
        )
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "aws-ec2-security-001"

    def test_filter_by_environment_context_matching(self, sample_rules):
        """Test filtering by environment context with matching environment."""
        environment_context = {"environment": "production"}
        rule_filter = RuleFilter(environment_context=environment_context)
        filtered_rules = rule_filter.filter_rules(sample_rules)

        # Should include rules that specify production or no environment restriction
        assert len(filtered_rules) == 3
        rule_ids = [rule.id for rule in filtered_rules]
        assert "aws-ec2-security-001" in rule_ids  # production environment
        assert "aws-s3-encryption-001" in rule_ids  # production environment
        assert "universal-tagging-001" in rule_ids  # no environment restriction
        assert "test-rule-001" not in rule_ids  # development only

    def test_filter_by_environment_context_disabled_override(self, sample_rules):
        """Test filtering with environment-specific disabled override."""
        environment_context = {"environment": "development"}
        rule_filter = RuleFilter(environment_context=environment_context)
        filtered_rules = rule_filter.filter_rules(sample_rules)

        # universal-tagging-001 should be disabled in development
        rule_ids = [rule.id for rule in filtered_rules]
        assert "universal-tagging-001" not in rule_ids
        assert "test-rule-001" in rule_ids  # development environment

    def test_filter_combined_criteria(self, sample_rules):
        """Test filtering with multiple criteria combined."""
        rule_filter = RuleFilter(
            include_patterns=["*aws*"],
            exclude_patterns=["*test*"],
            min_severity="warning",
            environment_context={"environment": "production"},
        )
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 2
        rule_ids = [rule.id for rule in filtered_rules]
        assert "aws-ec2-security-001" in rule_ids
        assert "aws-s3-encryption-001" in rule_ids

    def test_filter_no_matches(self, sample_rules):
        """Test filtering that results in no matches."""
        rule_filter = RuleFilter(include_patterns=["nonexistent"])
        filtered_rules = rule_filter.filter_rules(sample_rules)

        assert len(filtered_rules) == 0

    def test_invalid_severity(self):
        """Test error handling for invalid severity."""
        with pytest.raises(ValueError, match="Invalid severity"):
            RuleFilter(min_severity="invalid")


class TestRuleSelector:
    """Test RuleSelector class."""

    @pytest.fixture
    def sample_rules(self):
        """Create sample rules for testing."""
        rules_data = [
            {
                "id": "rule-001",
                "resource_type": "aws_instance",
                "description": "EC2 rule",
                "severity": "error",
                "assert": {"tags": {"Environment": "present"}},
            },
            {
                "id": "rule-002",
                "resource_type": "aws_s3_bucket",
                "description": "S3 rule",
                "severity": "warning",
                "assert": {"encryption": "present"},
            },
            {
                "id": "rule-003",
                "resource_type": "aws_instance",
                "description": "Another EC2 rule",
                "severity": "info",
                "assert": {"tags": {"Name": "present"}},
            },
        ]

        return [Rule(rule_dict) for rule_dict in rules_data]

    def test_select_rules_single_filter(self, sample_rules):
        """Test rule selection with single filter."""
        selector = RuleSelector()
        selector.add_filter(RuleFilter(min_severity="warning"))

        selected_rules = selector.select_rules(sample_rules)

        assert len(selected_rules) == 2
        rule_ids = [rule.id for rule in selected_rules]
        assert "rule-001" in rule_ids
        assert "rule-002" in rule_ids
        assert "rule-003" not in rule_ids

    def test_select_rules_multiple_filters(self, sample_rules):
        """Test rule selection with multiple filters."""
        selector = RuleSelector()
        selector.add_filter(RuleFilter(min_severity="info"))  # Include all
        selector.add_filter(RuleFilter(include_patterns=["type:aws_instance"]))  # Only EC2

        selected_rules = selector.select_rules(sample_rules)

        assert len(selected_rules) == 2
        rule_ids = [rule.id for rule in selected_rules]
        assert "rule-001" in rule_ids
        assert "rule-003" in rule_ids
        assert "rule-002" not in rule_ids

    def test_create_environment_filter(self):
        """Test creating environment filter from resources."""
        resources = [
            {"id": "web_server", "type": "aws_instance", "tags": {"Environment": "production"}},
            {"id": "storage", "type": "aws_s3_bucket", "tags": {"Environment": "production"}},
        ]

        selector = RuleSelector()
        env_filter = selector.create_environment_filter("production", resources)

        assert env_filter.environment_context["environment"] == "production"
        assert "aws_instance" in env_filter.environment_context["resource_types"]
        assert "aws_s3_bucket" in env_filter.environment_context["resource_types"]
        assert env_filter.environment_context["has_tags"] is True
        assert "aws" in env_filter.environment_context["providers"]

    def test_extract_provider_aws(self):
        """Test provider extraction for AWS resources."""
        selector = RuleSelector()

        resource = {"type": "aws_instance"}
        provider = selector._extract_provider(resource)
        assert provider == "aws"

    def test_extract_provider_azure(self):
        """Test provider extraction for Azure resources."""
        selector = RuleSelector()

        resource = {"type": "azurerm_virtual_machine"}
        provider = selector._extract_provider(resource)
        assert provider == "azure"

    def test_extract_provider_gcp(self):
        """Test provider extraction for GCP resources."""
        selector = RuleSelector()

        resource = {"type": "google_compute_instance"}
        provider = selector._extract_provider(resource)
        assert provider == "gcp"

    def test_extract_provider_unknown(self):
        """Test provider extraction for unknown resources."""
        selector = RuleSelector()

        resource = {"type": "unknown_resource"}
        provider = selector._extract_provider(resource)
        assert provider is None


class TestUtilityFunctions:
    """Test utility functions."""

    def test_create_rule_filter_from_config(self):
        """Test creating rule filter from configuration dictionary."""
        config_dict = {
            "include_rules": ["*security*"],
            "exclude_rules": ["*test*"],
            "min_severity": "warning",
            "environment_context": {"environment": "production"},
        }

        rule_filter = create_rule_filter_from_config(config_dict)

        assert rule_filter.include_patterns == ["*security*"]
        assert rule_filter.exclude_patterns == ["*test*"]
        assert rule_filter.min_severity == Severity.WARNING
        assert rule_filter.environment_context == {"environment": "production"}

    def test_filter_rules_by_patterns(self):
        """Test convenience function for filtering rules by patterns."""
        rules_data = [
            {
                "id": "security-rule-001",
                "resource_type": "aws_instance",
                "description": "Security rule",
                "severity": "error",
                "assert": {"tags": {"Environment": "present"}},
            },
            {
                "id": "test-rule-001",
                "resource_type": "aws_instance",
                "description": "Test rule",
                "severity": "info",
                "assert": {"tags": {"Name": "present"}},
            },
        ]

        rules = [Rule(rule_dict) for rule_dict in rules_data]

        filtered_rules = filter_rules_by_patterns(
            rules,
            include_patterns=["*security*"],
            exclude_patterns=["*test*"],
            min_severity="warning",
        )

        assert len(filtered_rules) == 1
        assert filtered_rules[0].id == "security-rule-001"
