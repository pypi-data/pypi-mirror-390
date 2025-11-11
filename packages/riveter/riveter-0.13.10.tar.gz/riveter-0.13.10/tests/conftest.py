"""Pytest configuration and fixtures for Riveter tests."""

import os
import tempfile
from typing import Any, Dict

import pytest

from riveter.rules import Rule
from riveter.scanner import ValidationResult


@pytest.fixture
def sample_terraform_config():
    """Sample Terraform configuration for testing."""
    return {
        "resources": [
            {
                "id": "web_server",
                "resource_type": "aws_instance",
                "instance_type": "t3.micro",
                "ami": "ami-12345678",
                "tags": {"Environment": "production", "Name": "web-server", "CostCenter": "12345"},
                "security_groups": ["sg-12345678"],
                "root_block_device": {"volume_size": 20, "volume_type": "gp3"},
            },
            {
                "id": "database",
                "resource_type": "aws_rds_instance",
                "engine": "mysql",
                "engine_version": "8.0",
                "instance_class": "db.t3.micro",
                "allocated_storage": 20,
                "tags": {"Environment": "production", "Name": "database"},
            },
            {
                "id": "storage_bucket",
                "resource_type": "aws_s3_bucket",
                "bucket": "my-test-bucket",
                "tags": {"Environment": "production", "Purpose": "data-storage"},
            },
        ]
    }


@pytest.fixture
def sample_rule_dict():
    """Sample rule dictionary for testing."""
    return {
        "id": "test-rule-001",
        "resource_type": "aws_instance",
        "description": "Test rule for EC2 instances",
        "filter": {"tags": {"Environment": "production"}},
        "assert": {"tags": {"CostCenter": "present"}},
    }


@pytest.fixture
def sample_rule(sample_rule_dict):
    """Sample Rule object for testing."""
    return Rule(sample_rule_dict)


@pytest.fixture
def sample_rules_list(sample_rule_dict):
    """List of sample rules for testing."""
    rules_data = [
        sample_rule_dict,
        {
            "id": "test-rule-002",
            "resource_type": "aws_s3_bucket",
            "description": "Test rule for S3 buckets",
            "assert": {"tags": {"Purpose": "present"}},
        },
        {
            "id": "test-rule-003",
            "resource_type": "*",
            "description": "Universal rule for all resources",
            "assert": {"tags": {"Environment": "production"}},
        },
    ]
    return [Rule(rule_dict) for rule_dict in rules_data]


@pytest.fixture
def temp_terraform_file():
    """Create a temporary Terraform file for testing."""
    terraform_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
    CostCenter  = "12345"
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  security_groups = ["sg-12345678"]
}

resource "aws_s3_bucket" "storage" {
  bucket = "my-test-bucket"

  tags = {
    Environment = "production"
    Purpose     = "data-storage"
  }
}
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
        f.write(terraform_content)
        temp_file_path = f.name

    yield temp_file_path

    # Cleanup
    os.unlink(temp_file_path)


@pytest.fixture
def temp_rules_file():
    """Create a temporary rules YAML file for testing."""
    rules_content = """
rules:
  - id: test-rule-001
    resource_type: aws_instance
    description: Test rule for EC2 instances
    filter:
      tags:
        Environment: production
    assert:
      tags:
        CostCenter: present

  - id: test-rule-002
    resource_type: aws_s3_bucket
    description: Test rule for S3 buckets
    assert:
      tags:
        Purpose: present

  - id: test-rule-003
    resource_type: "*"
    description: Universal rule for all resources
    assert:
      tags:
        Environment: production
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        f.write(rules_content)
        temp_file_path = f.name

    yield temp_file_path

    # Cleanup
    os.unlink(temp_file_path)


@pytest.fixture
def mock_validation_results(sample_rules_list, sample_terraform_config):
    """Create mock validation results for testing."""
    results = []

    # Create some passing and failing results
    rule1 = sample_rules_list[0]  # aws_instance rule
    resource1 = sample_terraform_config["resources"][0]  # web_server

    results.append(
        ValidationResult(rule=rule1, resource=resource1, passed=True, message="All checks passed")
    )

    rule2 = sample_rules_list[1]  # aws_s3_bucket rule
    resource2 = sample_terraform_config["resources"][2]  # storage_bucket

    results.append(
        ValidationResult(rule=rule2, resource=resource2, passed=True, message="All checks passed")
    )

    # Add a failing result
    results.append(
        ValidationResult(
            rule=rule1,
            resource={"id": "failing_instance", "resource_type": "aws_instance"},
            passed=False,
            message="Required tag 'CostCenter' is missing",
        )
    )

    return results


class MockResource:
    """Utility class for creating mock resources in tests."""

    @staticmethod
    def create_aws_instance(
        instance_id: str = "test-instance",
        instance_type: str = "t3.micro",
        tags: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Create a mock AWS instance resource."""
        if tags is None:
            tags = {"Environment": "test"}

        return {
            "id": instance_id,
            "resource_type": "aws_instance",
            "instance_type": instance_type,
            "ami": "ami-12345678",
            "tags": tags,
            "security_groups": ["sg-12345678"],
        }

    @staticmethod
    def create_s3_bucket(
        bucket_id: str = "test-bucket",
        bucket_name: str = "my-test-bucket",
        tags: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Create a mock S3 bucket resource."""
        if tags is None:
            tags = {"Environment": "test"}

        return {
            "id": bucket_id,
            "resource_type": "aws_s3_bucket",
            "bucket": bucket_name,
            "tags": tags,
        }

    @staticmethod
    def create_rds_instance(
        instance_id: str = "test-db", engine: str = "mysql", tags: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Create a mock RDS instance resource."""
        if tags is None:
            tags = {"Environment": "test"}

        return {
            "id": instance_id,
            "resource_type": "aws_rds_instance",
            "engine": engine,
            "engine_version": "8.0",
            "instance_class": "db.t3.micro",
            "allocated_storage": 20,
            "tags": tags,
        }


class MockRule:
    """Utility class for creating mock rules in tests."""

    @staticmethod
    def create_tag_rule(
        rule_id: str = "test-rule",
        resource_type: str = "aws_instance",
        required_tags: Dict[str, str] = None,
        filter_tags: Dict[str, str] = None,
    ) -> Dict[str, Any]:
        """Create a mock rule that checks for required tags."""
        if required_tags is None:
            required_tags = {"Environment": "present"}

        rule_dict = {
            "id": rule_id,
            "resource_type": resource_type,
            "description": f"Test rule for {resource_type}",
            "assert": {"tags": required_tags},
        }

        if filter_tags:
            rule_dict["filter"] = {"tags": filter_tags}

        return rule_dict

    @staticmethod
    def create_property_rule(
        rule_id: str = "test-property-rule",
        resource_type: str = "aws_instance",
        property_name: str = "instance_type",
        expected_value: str = "t3.micro",
    ) -> Dict[str, Any]:
        """Create a mock rule that checks a specific property value."""
        return {
            "id": rule_id,
            "resource_type": resource_type,
            "description": f"Test rule checking {property_name}",
            "assert": {property_name: expected_value},
        }


@pytest.fixture
def mock_resource():
    """Provide MockResource utility class."""
    return MockResource


@pytest.fixture
def mock_rule():
    """Provide MockRule utility class."""
    return MockRule
