"""Unit tests for the extract_config module."""

import os
import tempfile
from pathlib import Path

import pytest

from riveter.extract_config import extract_terraform_config


class TestExtractTerraformConfig:
    """Test cases for the extract_terraform_config function."""

    def test_extract_simple_terraform_config(self):
        """Test extracting configuration from a simple Terraform file."""
        terraform_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
  }
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            assert "resources" in config
            assert len(config["resources"]) == 1

            resource = config["resources"][0]
            assert resource["id"] == "web_server"
            assert resource["resource_type"] == "aws_instance"
            assert resource["ami"] == "ami-12345678"
            assert resource["instance_type"] == "t3.micro"
            assert resource["tags"]["Name"] == "web-server"
            assert resource["tags"]["Environment"] == "production"

        finally:
            os.unlink(temp_file)

    def test_extract_multiple_resources(self):
        """Test extracting configuration with multiple resources."""
        terraform_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server"
  }
}

resource "aws_s3_bucket" "storage" {
  bucket = "my-storage-bucket"

  tags = {
    Purpose = "data-storage"
  }
}

resource "aws_rds_instance" "database" {
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.micro"

  tags = {
    Name = "database"
  }
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            assert len(config["resources"]) == 3

            # Check each resource type is present
            resource_types = [r["resource_type"] for r in config["resources"]]
            assert "aws_instance" in resource_types
            assert "aws_s3_bucket" in resource_types
            assert "aws_rds_instance" in resource_types

            # Check specific resource details
            web_server = next(r for r in config["resources"] if r["id"] == "web_server")
            assert web_server["resource_type"] == "aws_instance"
            assert web_server["ami"] == "ami-12345678"

            storage = next(r for r in config["resources"] if r["id"] == "storage")
            assert storage["resource_type"] == "aws_s3_bucket"
            assert storage["bucket"] == "my-storage-bucket"

            database = next(r for r in config["resources"] if r["id"] == "database")
            assert database["resource_type"] == "aws_rds_instance"
            assert database["engine"] == "mysql"

        finally:
            os.unlink(temp_file)

    def test_extract_nested_objects(self):
        """Test extracting configuration with nested objects."""
        terraform_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = {
    Name = "web-server"
  }
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            resource = config["resources"][0]
            assert "root_block_device" in resource
            # AWS parser converts root_block_device from list to dict for easier access
            assert isinstance(resource["root_block_device"], dict)
            block_device = resource["root_block_device"]
            assert block_device["volume_size"] == 20
            assert block_device["volume_type"] == "gp3"
            assert block_device["encrypted"] is True

        finally:
            os.unlink(temp_file)

    def test_extract_list_properties(self):
        """Test extracting configuration with list properties."""
        terraform_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  security_groups = ["sg-12345678", "sg-87654321"]

  tags = {
    Name = "web-server"
  }
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            resource = config["resources"][0]
            assert "security_groups" in resource
            assert isinstance(resource["security_groups"], list)
            assert len(resource["security_groups"]) == 2
            assert "sg-12345678" in resource["security_groups"]
            assert "sg-87654321" in resource["security_groups"]

        finally:
            os.unlink(temp_file)

    def test_extract_empty_terraform_file(self):
        """Test extracting configuration from file with no resources."""
        terraform_content = """
# This file has no resources
variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            assert "resources" in config
            assert len(config["resources"]) == 0

        finally:
            os.unlink(temp_file)

    def test_extract_tags_conversion(self):
        """Test that tags are properly converted from list to dict format."""
        # Note: This test assumes the current implementation handles tags as dict
        # If tags come in as list format, they should be converted
        terraform_content = """
resource "aws_instance" "web_server" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "web-server"
    Environment = "production"
    CostCenter  = "12345"
  }
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            resource = config["resources"][0]
            assert "tags" in resource
            assert isinstance(resource["tags"], dict)
            assert resource["tags"]["Name"] == "web-server"
            assert resource["tags"]["Environment"] == "production"
            assert resource["tags"]["CostCenter"] == "12345"

        finally:
            os.unlink(temp_file)

    def test_extract_multiple_instances_same_type(self):
        """Test extracting multiple instances of the same resource type."""
        terraform_content = """
resource "aws_instance" "web_server_1" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name = "web-server-1"
  }
}

resource "aws_instance" "web_server_2" {
  ami           = "ami-87654321"
  instance_type = "t3.small"

  tags = {
    Name = "web-server-2"
  }
}
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".tf", delete=False) as f:
            f.write(terraform_content)
            temp_file = f.name

        try:
            config = extract_terraform_config(temp_file)

            assert len(config["resources"]) == 2

            # Both should be aws_instance type
            assert all(r["resource_type"] == "aws_instance" for r in config["resources"])

            # Check they have different IDs and properties
            ids = [r["id"] for r in config["resources"]]
            assert "web_server_1" in ids
            assert "web_server_2" in ids

            server1 = next(r for r in config["resources"] if r["id"] == "web_server_1")
            server2 = next(r for r in config["resources"] if r["id"] == "web_server_2")

            assert server1["ami"] == "ami-12345678"
            assert server2["ami"] == "ami-87654321"
            assert server1["instance_type"] == "t3.micro"
            assert server2["instance_type"] == "t3.small"

        finally:
            os.unlink(temp_file)

    def test_extract_from_fixture_simple(self):
        """Test extracting configuration from simple fixture file."""
        fixture_path = Path(__file__).parent / "fixtures" / "terraform" / "simple.tf"

        config = extract_terraform_config(str(fixture_path))

        assert "resources" in config
        assert len(config["resources"]) == 3

        # Check resource types
        resource_types = [r["resource_type"] for r in config["resources"]]
        assert "aws_instance" in resource_types
        assert "aws_s3_bucket" in resource_types
        assert "aws_rds_instance" in resource_types

        # Check specific resource details
        web_server = next(r for r in config["resources"] if r["id"] == "web_server")
        assert web_server["instance_type"] == "t3.micro"
        assert web_server["tags"]["Environment"] == "production"

        storage = next(r for r in config["resources"] if r["id"] == "storage")
        assert storage["bucket"] == "my-test-bucket"
        assert storage["tags"]["Purpose"] == "data-storage"

    def test_extract_from_fixture_complex(self):
        """Test extracting configuration from complex fixture file."""
        fixture_path = Path(__file__).parent / "fixtures" / "terraform" / "complex.tf"

        config = extract_terraform_config(str(fixture_path))

        assert "resources" in config
        assert len(config["resources"]) == 6  # Based on complex.tf content

        # Check we have multiple instances of same type
        instances = [r for r in config["resources"] if r["resource_type"] == "aws_instance"]
        assert len(instances) == 2

        buckets = [r for r in config["resources"] if r["resource_type"] == "aws_s3_bucket"]
        assert len(buckets) == 2

        # Check specific details
        web_server_1 = next(r for r in config["resources"] if r["id"] == "web_server_1")
        assert web_server_1["instance_type"] == "t3.small"
        assert web_server_1["tags"]["Team"] == "backend"

        vpc = next(r for r in config["resources"] if r["resource_type"] == "aws_vpc")
        assert vpc["cidr_block"] == "10.0.0.0/16"

    def test_extract_malformed_terraform_file(self):
        """Test handling of malformed Terraform files."""
        fixture_path = Path(__file__).parent / "fixtures" / "terraform" / "malformed.tf"

        # This should raise an exception due to malformed HCL
        with pytest.raises((ValueError, SyntaxError, Exception)):
            extract_terraform_config(str(fixture_path))

    def test_extract_nonexistent_file(self):
        """Test handling of nonexistent files."""
        from riveter.exceptions import FileSystemError

        with pytest.raises(FileSystemError):
            extract_terraform_config("nonexistent_file.tf")
