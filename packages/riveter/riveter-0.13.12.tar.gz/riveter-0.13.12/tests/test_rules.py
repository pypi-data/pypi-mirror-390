"""Unit tests for the rules module."""

import os
import tempfile
from pathlib import Path

import pytest

from riveter.rules import Rule, load_rules


class TestRule:
    """Test cases for the Rule class."""

    def test_rule_initialization(self, sample_rule_dict):
        """Test Rule object initialization with valid data."""
        rule = Rule(sample_rule_dict)

        assert rule.id == "test-rule-001"
        assert rule.resource_type == "aws_instance"
        assert rule.description == "Test rule for EC2 instances"
        assert rule.filter == {"tags": {"Environment": "production"}}
        assert rule.assert_conditions == {"tags": {"CostCenter": "present"}}

    def test_rule_initialization_minimal(self):
        """Test Rule initialization with minimal required fields."""
        rule_dict = {
            "id": "minimal-rule",
            "resource_type": "aws_s3_bucket",
            "assert": {"tags": {"Purpose": "present"}},
        }

        rule = Rule(rule_dict)

        assert rule.id == "minimal-rule"
        assert rule.resource_type == "aws_s3_bucket"
        assert rule.description == "No description provided"
        assert rule.filter == {}
        assert rule.assert_conditions == {"tags": {"Purpose": "present"}}

    def test_matches_resource_with_no_filter(self):
        """Test that rule matches any resource when no filter is specified."""
        rule_dict = {
            "id": "no-filter-rule",
            "resource_type": "aws_instance",
            "assert": {"instance_type": "t3.micro"},
        }
        rule = Rule(rule_dict)

        resource = {
            "id": "test-instance",
            "resource_type": "aws_instance",
            "instance_type": "t3.large",
            "tags": {"Environment": "test"},
        }

        assert rule.matches_resource(resource) is True

    def test_matches_resource_with_tag_filter_exact_match(self):
        """Test resource matching with exact tag filter match."""
        rule_dict = {
            "id": "tag-filter-rule",
            "resource_type": "aws_instance",
            "filter": {"tags": {"Environment": "production"}},
            "assert": {"tags": {"CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        resource = {
            "id": "prod-instance",
            "resource_type": "aws_instance",
            "tags": {"Environment": "production", "Name": "web-server"},
        }

        assert rule.matches_resource(resource) is True

    def test_matches_resource_with_tag_filter_no_match(self):
        """Test resource matching with tag filter that doesn't match."""
        rule_dict = {
            "id": "tag-filter-rule",
            "resource_type": "aws_instance",
            "filter": {"tags": {"Environment": "production"}},
            "assert": {"tags": {"CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        resource = {
            "id": "test-instance",
            "resource_type": "aws_instance",
            "tags": {"Environment": "staging", "Name": "test-server"},
        }

        assert rule.matches_resource(resource) is False

    def test_matches_resource_with_tag_filter_missing_tags(self):
        """Test resource matching when resource has no tags."""
        rule_dict = {
            "id": "tag-filter-rule",
            "resource_type": "aws_instance",
            "filter": {"tags": {"Environment": "production"}},
            "assert": {"tags": {"CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        resource = {
            "id": "no-tags-instance",
            "resource_type": "aws_instance",
            "instance_type": "t3.micro",
        }

        assert rule.matches_resource(resource) is False

    def test_matches_resource_with_present_tag_filter(self):
        """Test resource matching with 'present' tag filter."""
        rule_dict = {
            "id": "present-tag-rule",
            "resource_type": "aws_instance",
            "filter": {"tags": {"CostCenter": "present"}},
            "assert": {"tags": {"Environment": "present"}},
        }
        rule = Rule(rule_dict)

        # Resource with the required tag present
        resource_with_tag = {
            "id": "tagged-instance",
            "resource_type": "aws_instance",
            "tags": {"CostCenter": "12345", "Environment": "production"},
        }

        # Resource without the required tag
        resource_without_tag = {
            "id": "untagged-instance",
            "resource_type": "aws_instance",
            "tags": {"Environment": "production"},
        }

        assert rule.matches_resource(resource_with_tag) is True
        assert rule.matches_resource(resource_without_tag) is False

    def test_matches_resource_multiple_tag_filters(self):
        """Test resource matching with multiple tag filters."""
        rule_dict = {
            "id": "multi-tag-rule",
            "resource_type": "aws_instance",
            "filter": {"tags": {"Environment": "production", "Team": "backend"}},
            "assert": {"tags": {"CostCenter": "present"}},
        }
        rule = Rule(rule_dict)

        # Resource matching all filters
        matching_resource = {
            "id": "matching-instance",
            "resource_type": "aws_instance",
            "tags": {"Environment": "production", "Team": "backend", "Name": "web-server"},
        }

        # Resource matching only one filter
        partial_match_resource = {
            "id": "partial-instance",
            "resource_type": "aws_instance",
            "tags": {"Environment": "production", "Team": "frontend"},
        }

        assert rule.matches_resource(matching_resource) is True
        assert rule.matches_resource(partial_match_resource) is False


class TestLoadRules:
    """Test cases for the load_rules function."""

    def test_load_rules_valid_file(self):
        """Test loading rules from a valid YAML file."""
        rules_content = """
rules:
  - id: test-rule-1
    resource_type: aws_instance
    description: Test rule 1
    assert:
      tags:
        Environment: present

  - id: test-rule-2
    resource_type: aws_s3_bucket
    description: Test rule 2
    filter:
      tags:
        Purpose: data-storage
    assert:
      tags:
        Compliance: present
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(rules_content)
            temp_file = f.name

        try:
            rules = load_rules(temp_file)

            assert len(rules) == 2

            # Check first rule
            assert rules[0].id == "test-rule-1"
            assert rules[0].resource_type == "aws_instance"
            assert rules[0].description == "Test rule 1"
            assert rules[0].filter == {}
            assert rules[0].assert_conditions == {"tags": {"Environment": "present"}}

            # Check second rule
            assert rules[1].id == "test-rule-2"
            assert rules[1].resource_type == "aws_s3_bucket"
            assert rules[1].description == "Test rule 2"
            assert rules[1].filter == {"tags": {"Purpose": "data-storage"}}
            assert rules[1].assert_conditions == {"tags": {"Compliance": "present"}}

        finally:
            os.unlink(temp_file)

    def test_load_rules_empty_file(self):
        """Test loading rules from an empty rules file."""
        rules_content = "rules: []"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(rules_content)
            temp_file = f.name

        try:
            rules = load_rules(temp_file)
            assert len(rules) == 0
        finally:
            os.unlink(temp_file)

    def test_load_rules_invalid_format_no_rules_key(self):
        """Test loading rules from file without 'rules' key."""
        invalid_content = """
invalid_key:
  - id: test-rule
    resource_type: aws_instance
    assert:
      tags:
        Environment: present
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            from riveter.exceptions import RuleValidationError

            with pytest.raises(RuleValidationError, match="must contain a 'rules' key"):
                load_rules(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_rules_invalid_format_not_dict(self):
        """Test loading rules from file that's not a dictionary."""
        invalid_content = "- invalid format"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            from riveter.exceptions import RuleValidationError

            with pytest.raises(RuleValidationError, match="root element must be a dictionary"):
                load_rules(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_rules_invalid_rule_not_dict(self):
        """Test loading rules where a rule is not a dictionary."""
        invalid_content = """
rules:
  - id: valid-rule
    resource_type: aws_instance
    assert:
      tags:
        Environment: present
  - invalid_rule_format
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            # With error recovery, this should load the valid rule and skip the invalid one
            rules = load_rules(temp_file)
            assert len(rules) == 1  # Only the valid rule should be loaded
            assert rules[0].id == "valid-rule"
        finally:
            os.unlink(temp_file)

    def test_load_rules_missing_id(self):
        """Test loading rules where a rule is missing an ID."""
        invalid_content = """
rules:
  - resource_type: aws_instance
    assert:
      tags:
        Environment: present
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            # With error recovery, this should return empty list (invalid rule skipped)
            rules = load_rules(temp_file)
            assert rules == []  # Invalid rule should be skipped
        finally:
            os.unlink(temp_file)

    def test_load_rules_missing_resource_type(self):
        """Test loading rules where a rule is missing resource_type."""
        invalid_content = """
rules:
  - id: missing-resource-type
    assert:
      tags:
        Environment: present
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            # With error recovery, this should return empty list (invalid rule skipped)
            rules = load_rules(temp_file)
            assert rules == []  # Invalid rule should be skipped
        finally:
            os.unlink(temp_file)

    def test_load_rules_missing_assert(self):
        """Test loading rules where a rule is missing assert conditions."""
        invalid_content = """
rules:
  - id: missing-assert
    resource_type: aws_instance
    description: Rule without assert conditions
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name

        try:
            # With error recovery, this should return empty list (invalid rule skipped)
            rules = load_rules(temp_file)
            assert rules == []  # Invalid rule should be skipped
        finally:
            os.unlink(temp_file)

    def test_load_rules_from_fixture(self):
        """Test loading rules from fixture files."""
        # Test with basic rules fixture
        fixture_path = Path(__file__).parent / "fixtures" / "rules" / "basic_rules.yml"
        rules = load_rules(str(fixture_path))

        assert len(rules) == 3
        assert rules[0].id == "ec2-cost-center-required"
        assert rules[1].id == "s3-purpose-required"
        assert rules[2].id == "all-resources-environment"

        # Verify wildcard resource type
        assert rules[2].resource_type == "*"


class TestAdvancedRuleFeatures:
    """Test cases for advanced rule features with operators."""

    def test_rule_with_severity(self):
        """Test rule initialization with severity levels."""
        rule_dict = {
            "id": "severity-test",
            "resource_type": "aws_instance",
            "severity": "warning",
            "assert": {"tags": {"Environment": "present"}},
        }

        rule = Rule(rule_dict)
        assert rule.severity.value == "warning"

    def test_rule_with_invalid_severity(self):
        """Test rule initialization with invalid severity."""
        rule_dict = {
            "id": "invalid-severity",
            "resource_type": "aws_instance",
            "severity": "invalid",
            "assert": {"tags": {"Environment": "present"}},
        }

        from riveter.exceptions import RuleValidationError

        with pytest.raises(RuleValidationError, match="Invalid severity 'invalid'"):
            Rule(rule_dict)

    def test_rule_with_numeric_operators(self):
        """Test rule with numeric comparison operators."""
        rule_dict = {
            "id": "numeric-test",
            "resource_type": "aws_instance",
            "assert": {"root_block_device.volume_size": {"gte": 100}, "cpu_credits": {"lt": 50}},
        }

        rule = Rule(rule_dict)

        # Test resource that passes
        passing_resource = {
            "resource_type": "aws_instance",
            "root_block_device": {"volume_size": 150},
            "cpu_credits": 30,
        }

        results = rule.validate_assertions(passing_resource)
        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_rule_with_regex_operator(self):
        """Test rule with regex pattern matching."""
        rule_dict = {
            "id": "regex-test",
            "resource_type": "aws_instance",
            "assert": {"instance_type": {"regex": r"^(t3|m5)\.(large|xlarge)$"}},
        }

        rule = Rule(rule_dict)

        # Test passing resource
        passing_resource = {"resource_type": "aws_instance", "instance_type": "t3.large"}

        results = rule.validate_assertions(passing_resource)
        assert len(results) == 1
        assert results[0].passed is True

    def test_rule_with_list_operators(self):
        """Test rule with list operations."""
        rule_dict = {
            "id": "list-test",
            "resource_type": "aws_instance",
            "assert": {"security_groups": {"length": {"gte": 1}, "contains": "sg-default"}},
        }

        rule = Rule(rule_dict)

        # Test passing resource
        passing_resource = {
            "resource_type": "aws_instance",
            "security_groups": ["sg-default", "sg-web"],
        }

        results = rule.validate_assertions(passing_resource)
        assert len(results) == 2  # length and contains
        assert all(r.passed for r in results)

    def test_rule_with_nested_path_resolution(self):
        """Test rule with nested attribute resolution."""
        rule_dict = {
            "id": "nested-test",
            "resource_type": "aws_instance",
            "assert": {
                "root_block_device.volume_size": {"gte": 20},
                "network_interfaces[0].subnet_id": "present",
            },
        }

        rule = Rule(rule_dict)

        # Test passing resource
        passing_resource = {
            "resource_type": "aws_instance",
            "root_block_device": {"volume_size": 50},
            "network_interfaces": [{"subnet_id": "subnet-123"}],
        }

        results = rule.validate_assertions(passing_resource)
        assert len(results) == 2
        assert all(r.passed for r in results)

    def test_rule_validation_with_invalid_operator(self):
        """Test rule validation fails with invalid operators."""
        rule_dict = {
            "id": "invalid-operator",
            "resource_type": "aws_instance",
            "assert": {"volume_size": {"invalid_op": 100}},
        }

        from riveter.exceptions import RuleValidationError

        with pytest.raises(RuleValidationError, match="Unknown operator 'invalid_op'"):
            Rule(rule_dict)

    def test_rule_filter_with_operators(self):
        """Test rule filtering with advanced operators."""
        rule_dict = {
            "id": "filter-test",
            "resource_type": "aws_instance",
            "filter": {"instance_type": {"regex": r"^t3\."}, "tags.Environment": "production"},
            "assert": {"tags": {"CostCenter": "present"}},
        }

        rule = Rule(rule_dict)

        # Resource that matches filter
        matching_resource = {
            "resource_type": "aws_instance",
            "instance_type": "t3.large",
            "tags": {"Environment": "production", "CostCenter": "12345"},
        }

        # Resource that doesn't match filter
        non_matching_resource = {
            "resource_type": "aws_instance",
            "instance_type": "m5.large",
            "tags": {"Environment": "production"},
        }

        assert rule.matches_resource(matching_resource) is True
        assert rule.matches_resource(non_matching_resource) is False

    def test_assertion_result_details(self):
        """Test detailed assertion results."""
        rule_dict = {
            "id": "detailed-test",
            "resource_type": "aws_instance",
            "assert": {"volume_size": {"gte": 100}, "instance_type": {"regex": r"^t3\."}},
        }

        rule = Rule(rule_dict)

        # Resource with mixed results
        resource = {
            "resource_type": "aws_instance",
            "volume_size": 50,  # Fails gte 100
            "instance_type": "t3.large",  # Passes regex
        }

        results = rule.validate_assertions(resource)
        assert len(results) == 2

        # Check volume_size assertion (should fail)
        volume_result = next(r for r in results if r.property_path == "volume_size")
        assert volume_result.passed is False
        assert volume_result.operator == "gte"
        assert volume_result.expected == 100
        assert volume_result.actual == 50

        # Check instance_type assertion (should pass)
        instance_result = next(r for r in results if r.property_path == "instance_type")
        assert instance_result.passed is True
        assert instance_result.operator == "regex"
