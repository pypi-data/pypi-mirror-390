"""Tests for cloud provider parsers and multi-cloud support."""

from pathlib import Path
from typing import Any, Dict

from riveter.cloud_parsers import AWSParser, AzureParser, CloudProviderDetector, GCPParser
from riveter.extract_config import extract_terraform_config


class TestCloudProviderParsers:
    """Test cloud provider-specific parsers."""

    def test_aws_parser_resource_types(self) -> None:
        """Test AWS parser supports expected resource types."""
        parser = AWSParser()

        # Test some common AWS resource types
        assert parser.supports_resource_type("aws_instance")
        assert parser.supports_resource_type("aws_s3_bucket")
        assert parser.supports_resource_type("aws_security_group")
        assert not parser.supports_resource_type("azurerm_virtual_machine")
        assert not parser.supports_resource_type("google_compute_instance")

    def test_azure_parser_resource_types(self) -> None:
        """Test Azure parser supports expected resource types."""
        parser = AzureParser()

        # Test some common Azure resource types
        assert parser.supports_resource_type("azurerm_virtual_machine")
        assert parser.supports_resource_type("azurerm_storage_account")
        assert parser.supports_resource_type("azurerm_network_security_group")
        assert not parser.supports_resource_type("aws_instance")
        assert not parser.supports_resource_type("google_compute_instance")

    def test_gcp_parser_resource_types(self) -> None:
        """Test GCP parser supports expected resource types."""
        parser = GCPParser()

        # Test some common GCP resource types
        assert parser.supports_resource_type("google_compute_instance")
        assert parser.supports_resource_type("google_storage_bucket")
        assert parser.supports_resource_type("google_compute_firewall")
        assert not parser.supports_resource_type("aws_instance")
        assert not parser.supports_resource_type("azurerm_virtual_machine")

    def test_aws_parser_tag_normalization(self) -> None:
        """Test AWS parser normalizes tags correctly."""
        parser = AWSParser()

        # Test dict tags (already normalized)
        resource = {"tags": {"Environment": "prod", "Owner": "team"}}
        normalized = parser.normalize_attributes(resource)
        assert normalized["tags"] == {"Environment": "prod", "Owner": "team"}

        # Test list tags (need normalization)
        resource2: Dict[str, Any] = {
            "tags": [{"Key": "Environment", "Value": "prod"}, {"Key": "Owner", "Value": "team"}]
        }
        normalized = parser.normalize_attributes(resource2)
        assert normalized["tags"] == {"Environment": "prod", "Owner": "team"}

    def test_aws_parser_security_groups_normalization(self) -> None:
        """Test AWS parser normalizes security groups correctly."""
        parser = AWSParser()

        # Test string security group
        resource = {"security_groups": "sg-12345"}
        normalized = parser.normalize_attributes(resource)
        assert normalized["security_groups"] == ["sg-12345"]

        # Test list security groups
        resource2: Dict[str, Any] = {"security_groups": ["sg-12345", "sg-67890"]}
        normalized2 = parser.normalize_attributes(resource2)
        assert normalized2["security_groups"] == ["sg-12345", "sg-67890"]

    def test_azure_parser_location_normalization(self) -> None:
        """Test Azure parser normalizes location to region."""
        parser = AzureParser()

        resource = {"location": "West Europe"}
        normalized = parser.normalize_attributes(resource)
        assert normalized["region"] == "West Europe"
        assert "location" in normalized  # Original should still be there

    def test_gcp_parser_labels_to_tags(self) -> None:
        """Test GCP parser normalizes labels to tags."""
        parser = GCPParser()

        resource = {"labels": {"environment": "prod", "owner": "team"}}
        normalized = parser.normalize_attributes(resource)
        assert normalized["tags"] == {"environment": "prod", "owner": "team"}

    def test_gcp_parser_zone_to_region(self) -> None:
        """Test GCP parser extracts region from zone."""
        parser = GCPParser()

        resource = {"zone": "us-central1-a"}
        normalized = parser.normalize_attributes(resource)
        assert normalized["region"] == "us-central1"
        assert normalized["zone"] == "us-central1-a"  # Original should still be there


class TestCloudProviderDetector:
    """Test cloud provider detection functionality."""

    def test_detector_initialization(self) -> None:
        """Test detector initializes with all parsers."""
        detector = CloudProviderDetector()

        assert "aws" in detector.parsers
        assert "azurerm" in detector.parsers
        assert "google" in detector.parsers
        assert isinstance(detector.parsers["aws"], AWSParser)
        assert isinstance(detector.parsers["azurerm"], AzureParser)
        assert isinstance(detector.parsers["google"], GCPParser)

    def test_detect_aws_resources(self) -> None:
        """Test detection of AWS resources."""
        detector = CloudProviderDetector()

        resources = [
            {"resource_type": "aws_instance", "id": "web"},
            {"resource_type": "aws_s3_bucket", "id": "data"},
        ]

        providers = detector.detect_providers(resources)
        assert providers == {"aws"}

    def test_detect_azure_resources(self) -> None:
        """Test detection of Azure resources."""
        detector = CloudProviderDetector()

        resources = [
            {"resource_type": "azurerm_virtual_machine", "id": "web"},
            {"resource_type": "azurerm_storage_account", "id": "data"},
        ]

        providers = detector.detect_providers(resources)
        assert providers == {"azurerm"}

    def test_detect_gcp_resources(self) -> None:
        """Test detection of GCP resources."""
        detector = CloudProviderDetector()

        resources = [
            {"resource_type": "google_compute_instance", "id": "web"},
            {"resource_type": "google_storage_bucket", "id": "data"},
        ]

        providers = detector.detect_providers(resources)
        assert providers == {"google"}

    def test_detect_multi_cloud_resources(self) -> None:
        """Test detection of multi-cloud resources."""
        detector = CloudProviderDetector()

        resources = [
            {"resource_type": "aws_instance", "id": "web"},
            {"resource_type": "azurerm_virtual_machine", "id": "app"},
            {"resource_type": "google_compute_instance", "id": "db"},
        ]

        providers = detector.detect_providers(resources)
        assert providers == {"aws", "azurerm", "google"}

    def test_get_parser_for_resource(self) -> None:
        """Test getting correct parser for resource type."""
        detector = CloudProviderDetector()

        aws_parser = detector.get_parser_for_resource("aws_instance")
        assert isinstance(aws_parser, AWSParser)

        azure_parser = detector.get_parser_for_resource("azurerm_virtual_machine")
        assert isinstance(azure_parser, AzureParser)

        gcp_parser = detector.get_parser_for_resource("google_compute_instance")
        assert isinstance(gcp_parser, GCPParser)

        unknown_parser = detector.get_parser_for_resource("unknown_resource")
        assert unknown_parser is None


class TestMultiCloudIntegration:
    """Test multi-cloud integration with extract_config."""

    def test_extract_azure_config(self) -> None:
        """Test extracting Azure Terraform configuration."""
        fixtures_dir = Path(__file__).parent / "fixtures" / "terraform"
        azure_file = fixtures_dir / "azure_example.tf"

        config = extract_terraform_config(str(azure_file))
        resources = config["resources"]

        # Should have Azure resources
        resource_types = {r["resource_type"] for r in resources}
        assert "azurerm_resource_group" in resource_types
        assert "azurerm_linux_virtual_machine" in resource_types
        assert "azurerm_storage_account" in resource_types

        # Check that Azure-specific parsing was applied
        vm_resource = next(
            r for r in resources if r["resource_type"] == "azurerm_linux_virtual_machine"
        )
        assert "tags" in vm_resource
        assert vm_resource["tags"]["Environment"] == "production"

        # Check that region normalization was applied
        assert "region" in vm_resource

    def test_extract_gcp_config(self) -> None:
        """Test extracting GCP Terraform configuration."""
        fixtures_dir = Path(__file__).parent / "fixtures" / "terraform"
        gcp_file = fixtures_dir / "gcp_example.tf"

        config = extract_terraform_config(str(gcp_file))
        resources = config["resources"]

        # Should have GCP resources
        resource_types = {r["resource_type"] for r in resources}
        assert "google_compute_instance" in resource_types
        assert "google_storage_bucket" in resource_types
        assert "google_compute_firewall" in resource_types

        # Check that GCP-specific parsing was applied
        instance_resource = next(
            r for r in resources if r["resource_type"] == "google_compute_instance"
        )
        assert "labels" in instance_resource
        assert instance_resource["labels"]["environment"] == "production"

        # Check that labels were normalized to tags
        assert "tags" in instance_resource
        assert instance_resource["tags"]["environment"] == "production"

        # Check that region was extracted from zone
        assert "region" in instance_resource
        assert instance_resource["region"] == "us-central1"

    def test_provider_detection_integration(self) -> None:
        """Test provider detection works with extracted configs."""
        fixtures_dir = Path(__file__).parent / "fixtures" / "terraform"

        # Test Azure detection
        azure_config = extract_terraform_config(str(fixtures_dir / "azure_example.tf"))
        detector = CloudProviderDetector()
        azure_providers = detector.detect_providers(azure_config["resources"])
        assert azure_providers == {"azurerm"}

        # Test GCP detection
        gcp_config = extract_terraform_config(str(fixtures_dir / "gcp_example.tf"))
        gcp_providers = detector.detect_providers(gcp_config["resources"])
        assert gcp_providers == {"google"}

    def test_backward_compatibility_with_aws(self) -> None:
        """Test that existing AWS parsing still works."""
        fixtures_dir = Path(__file__).parent / "fixtures" / "terraform"
        aws_file = fixtures_dir / "example.tf"

        # This should work with existing AWS files
        if aws_file.exists():
            config = extract_terraform_config(str(aws_file))
            resources = config["resources"]

            # Should still parse AWS resources correctly
            aws_resources = [r for r in resources if r["resource_type"].startswith("aws_")]
            if aws_resources:
                # Check that AWS parsing was applied
                for resource in aws_resources:
                    if "tags" in resource:
                        assert isinstance(resource["tags"], dict)


class TestCloudSpecificAttributeHandling:
    """Test cloud-specific attribute handling."""

    def test_aws_block_device_handling(self) -> None:
        """Test AWS block device configuration handling."""
        parser = AWSParser()

        # Test root_block_device as list (should be converted to dict)
        config = {"root_block_device": [{"volume_size": 20, "encrypted": True}]}
        parsed = parser.parse_resource("aws_instance", config)
        assert isinstance(parsed["root_block_device"], dict)
        assert parsed["root_block_device"]["volume_size"] == 20

    def test_azure_network_security_rules_handling(self) -> None:
        """Test Azure network security rules handling."""
        parser = AzureParser()

        # Test single security rule (should be converted to list)
        config = {"security_rule": {"name": "SSH", "priority": 1001, "access": "Allow"}}
        parsed = parser.parse_resource("azurerm_network_security_group", config)
        assert isinstance(parsed["security_rule"], list)
        assert len(parsed["security_rule"]) == 1

    def test_gcp_network_tags_handling(self) -> None:
        """Test GCP network tags handling."""
        parser = GCPParser()

        # Test single tag (should be converted to list)
        config = {"tags": "web"}
        parsed = parser.parse_resource("google_compute_instance", config)
        assert isinstance(parsed["tags"], list)
        assert parsed["tags"] == ["web"]

        # Test list tags (should remain list)
        config2: Dict[str, Any] = {"tags": ["web", "frontend"]}
        parsed2 = parser.parse_resource("google_compute_instance", config2)
        assert isinstance(parsed2["tags"], list)
        assert parsed2["tags"] == ["web", "frontend"]
