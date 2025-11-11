"""Tests for documentation examples and code snippets."""

from pathlib import Path

import pytest
import yaml

from riveter.rules import load_rules
from riveter.scanner import validate_resources


class TestTutorialExamples:
    """Test code examples from the tutorial documentation."""

    def test_basic_terraform_example(self, tmp_path):
        """Test the basic Terraform example from the tutorial."""
        # Create the sample Terraform file from tutorial
        tf_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
"""
        tf_file = tmp_path / "main.tf"
        tf_file.write_text(tf_content)

        # Create the sample rule from tutorial
        rule_content = """
rules:
  - id: ec2-instance-type-check
    resource_type: aws_instance
    description: Ensure EC2 instances use approved instance types
    severity: error
    assert:
      instance_type:
        regex: "^(t3|m5|c5)\\\\.(large|xlarge)$"
"""
        rules_file = tmp_path / "rules.yml"
        rules_file.write_text(rule_content)

        # Test that the rule loads correctly
        rules = load_rules(str(rules_file))
        assert len(rules) == 1
        assert rules[0].id == "ec2-instance-type-check"

        # Test that the rule fails as expected in tutorial
        from riveter.extract_config import extract_terraform_config

        config = extract_terraform_config(str(tf_file))
        results = validate_resources(rules, config["resources"])

        # Should have one result that fails
        assert len(results) == 1
        assert not results[0].passed

    def test_fixed_terraform_example(self, tmp_path):
        """Test the fixed Terraform example from the tutorial."""
        # Create the fixed Terraform file from tutorial
        tf_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.large"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
"""
        tf_file = tmp_path / "main.tf"
        tf_file.write_text(tf_content)

        # Create the sample rule from tutorial
        rule_content = """
rules:
  - id: ec2-instance-type-check
    resource_type: aws_instance
    description: Ensure EC2 instances use approved instance types
    severity: error
    assert:
      instance_type:
        regex: "^(t3|m5|c5)\\\\.(large|xlarge)$"
"""
        rules_file = tmp_path / "rules.yml"
        rules_file.write_text(rule_content)

        # Test that the rule passes with the fix
        rules = load_rules(str(rules_file))
        from riveter.extract_config import extract_terraform_config

        config = extract_terraform_config(str(tf_file))
        results = validate_resources(rules, config["resources"])

        # Should have one result that passes
        assert len(results) == 1
        assert results[0].passed

    def test_advanced_operators_examples(self, tmp_path):
        """Test advanced operator examples from tutorial."""
        rule_content = """
rules:
  - id: volume-size-check
    resource_type: aws_instance
    description: Ensure root volume is large enough
    assert:
      root_block_device.volume_size:
        gte: 100

  - id: naming-convention
    resource_type: aws_instance
    description: Enforce naming convention
    assert:
      tags.Name:
        regex: "^(web|app|db)-[a-z0-9-]+$"
"""
        rules_file = tmp_path / "rules.yml"
        rules_file.write_text(rule_content)

        rules = load_rules(str(rules_file))
        assert len(rules) == 2

        # Test volume size rule
        volume_rule = next(r for r in rules if r.id == "volume-size-check")

        # Resource with sufficient volume size
        resource_good = {
            "resource_type": "aws_instance",
            "id": "instance-1",
            "root_block_device": {"volume_size": 150},
        }
        results = volume_rule.validate_assertions(resource_good)
        assert len(results) == 1
        assert results[0].passed

        # Test naming convention rule
        naming_rule = next(r for r in rules if r.id == "naming-convention")

        # Resource with good naming
        resource_good_name = {
            "resource_type": "aws_instance",
            "id": "instance-3",
            "tags": {"Name": "web-server-01"},
        }
        results = naming_rule.validate_assertions(resource_good_name)
        assert len(results) == 1
        assert results[0].passed


class TestConfigurationExamples:
    """Test configuration file examples."""

    def test_basic_config_example(self):
        """Test the basic configuration example."""
        config_path = Path("examples/configurations/basic-config.yml")
        if not config_path.exists():
            pytest.skip("Basic config example not found")

        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        # Validate basic structure
        assert "rule_packs" in config_data
        assert "rule_dirs" in config_data
        assert "output_format" in config_data
        assert "min_severity" in config_data

        # Validate values
        assert config_data["output_format"] in ["table", "json", "junit", "sarif"]
        assert config_data["min_severity"] in ["info", "warning", "error"]
        assert isinstance(config_data["rule_packs"], list)
        assert isinstance(config_data["rule_dirs"], list)

    def test_all_config_examples_valid_yaml(self):
        """Test that all configuration examples are valid YAML."""
        config_dir = Path("examples/configurations")
        if not config_dir.exists():
            pytest.skip("Configuration examples directory not found")

        yaml_files = list(config_dir.glob("*.yml")) + list(config_dir.glob("*.yaml"))

        for config_file in yaml_files:
            if config_file.name == "README.md":
                continue

            with open(config_file) as f:
                try:
                    config_data = yaml.safe_load(f)
                    assert config_data is not None, f"Empty config in {config_file}"
                    assert isinstance(config_data, dict), f"Config must be dict in {config_file}"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {config_file}: {e}")


class TestDocumentationIntegrity:
    """Test that documentation examples are consistent and up-to-date."""

    def test_tutorial_terraform_syntax(self, tmp_path):
        """Test that Terraform examples in tutorial have valid syntax."""
        tf_examples = [
            """
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
""",
            """
resource "aws_instance" "web_server" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t3.large"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
""",
        ]

        for i, tf_content in enumerate(tf_examples):
            tf_file = tmp_path / f"example_{i}.tf"
            tf_file.write_text(tf_content)

            # Basic syntax validation - check that file can be parsed
            try:
                from riveter.extract_config import extract_terraform_config

                config = extract_terraform_config(str(tf_file))
                assert "resources" in config
                assert len(config["resources"]) > 0
            except Exception as e:
                pytest.fail(f"Terraform example {i} has invalid syntax: {e}")

    def test_example_consistency(self):
        """Test that examples are consistent across documentation."""
        tutorial_path = Path("docs/tutorial.md")
        if tutorial_path.exists():
            tutorial_content = tutorial_path.read_text()

            # Check that tutorial mentions key concepts
            assert "riveter scan" in tutorial_content
            assert "rules.yml" in tutorial_content
            assert "main.tf" in tutorial_content
            assert "rule_packs" in tutorial_content
