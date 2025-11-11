"""Integration tests for CLI commands with new rule packs."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


def run_cli_command(args: List[str], **kwargs) -> subprocess.CompletedProcess:
    """Helper function to run CLI commands with proper environment setup."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parent.parent / "src")

    return subprocess.run(
        [sys.executable, "-m", "riveter.cli"] + args,
        env=env,
        capture_output=True,
        text=True,
        **kwargs,
    )


def extract_json_from_output(output: str) -> Dict[str, Any]:
    """Extract JSON from CLI output that may contain informational messages."""
    lines = output.strip().split("\n")
    json_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("{"):
            json_start = i
            break

    if json_start >= 0:
        json_output = "\n".join(lines[json_start:])
        return json.loads(json_output)
    else:
        raise ValueError(f"No JSON found in output: {output}")


class TestListRulePacksCommand:
    """Test the list-rule-packs CLI command."""

    def test_list_rule_packs_basic(self) -> None:
        """Test basic list-rule-packs command functionality."""
        result = run_cli_command(["list-rule-packs"])

        assert result.returncode == 0
        assert "Available Rule Packs" in result.stdout

        # Verify all new rule packs appear in the output
        expected_packs = [
            "gcp-security",
            "cis-gcp",
            "azure-security",
            "aws-well-architected",
            "azure-well-architected",
            "gcp-well-architected",
            "aws-hipaa",
            "azure-hipaa",
            "aws-pci-dss",
            "multi-cloud-security",
            "kubernetes-security",
        ]

        for pack_name in expected_packs:
            assert pack_name in result.stdout

    def test_list_rule_packs_shows_correct_metadata(self) -> None:
        """Test that list-rule-packs shows correct metadata for new packs."""
        result = run_cli_command(["list-rule-packs"])

        assert result.returncode == 0

        # Check for version information
        assert "1.0.0" in result.stdout

        # Check for author information
        assert "Riveter Team" in result.stdout

        # Check for rule count information (should show numbers)
        lines = result.stdout.split("\n")
        rule_count_lines = [line for line in lines if any(char.isdigit() for char in line)]
        assert len(rule_count_lines) > 0

    def test_list_rule_packs_shows_descriptions(self) -> None:
        """Test that list-rule-packs shows proper descriptions."""
        result = run_cli_command(["list-rule-packs"])

        assert result.returncode == 0

        # Check for key description terms
        expected_terms = [
            "Security",
            "Best Practices",
            "CIS",
            "Well-Architected",
            "HIPAA",
            "PCI-DSS",
            "Multi-Cloud",
            "Kubernetes",
        ]

        for term in expected_terms:
            assert term in result.stdout

    def test_list_rule_packs_shows_accurate_rule_counts(self) -> None:
        """Test that rule counts are accurate for new rule packs."""
        result = run_cli_command(["list-rule-packs"])

        assert result.returncode == 0

        # Parse the output to extract rule counts
        lines = result.stdout.split("\n")

        # Find lines that contain rule pack information
        pack_lines = []
        for line in lines:
            if any(pack in line for pack in ["gcp-security", "cis-gcp", "azure-security"]):
                pack_lines.append(line)

        # Verify we found pack information
        assert len(pack_lines) > 0

        # Check that rule counts are reasonable (should be > 0 and < 100 for each pack)
        for line in pack_lines:
            # Extract numbers from the line
            numbers = [int(s) for s in line.split() if s.isdigit()]
            if numbers:
                rule_count = max(numbers)  # Assume the largest number is the rule count
                assert (
                    0 < rule_count < 100
                ), f"Rule count {rule_count} seems unreasonable in line: {line}"

    def test_list_rule_packs_total_count(self) -> None:
        """Test that the total rule pack count is correct."""
        result = run_cli_command(["list-rule-packs"])

        assert result.returncode == 0

        # Should show total count at the end
        assert "Total rule packs:" in result.stdout

        # Extract the total count
        lines = result.stdout.split("\n")
        total_line = [line for line in lines if "Total rule packs:" in line]
        assert len(total_line) == 1

        # Extract the number
        total_count = int(total_line[0].split(":")[-1].strip())

        # Should have at least 11 new packs plus existing ones
        assert total_count >= 11

    def test_list_rule_packs_error_handling(self) -> None:
        """Test error handling in list-rule-packs command."""
        # Test with invalid arguments (should still work as it takes no args)
        result = run_cli_command(["list-rule-packs", "--invalid-arg"])

        # Should either work (ignoring invalid arg) or show help
        assert result.returncode in [0, 2]  # 0 for success, 2 for argument error


class TestScanCommandWithNewRulePacks:
    """Test the scan command with new rule packs."""

    @pytest.fixture
    def sample_terraform_file(self, tmp_path: Path) -> Path:
        """Create a sample Terraform file for testing."""
        tf_content = """
# Sample Terraform configuration for testing
resource "aws_instance" "example" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"

  tags = {
    Name        = "test-instance"
    Environment = "production"
  }
}

resource "google_compute_instance" "example" {
  name         = "test-instance"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
  }

  tags = ["test"]
}

resource "azurerm_linux_virtual_machine" "example" {
  name                = "test-vm"
  resource_group_name = "test-rg"
  location            = "East US"
  size                = "Standard_B1s"
  admin_username      = "adminuser"

  network_interface_ids = [
    azurerm_network_interface.example.id,
  ]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts-gen2"
    version   = "latest"
  }
}
"""
        tf_file = tmp_path / "main.tf"
        tf_file.write_text(tf_content)
        return tf_file

    def test_scan_with_gcp_security_pack(self, sample_terraform_file: Path) -> None:
        """Test scanning with GCP security rule pack."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "gcp-security",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "json",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # Extract and validate JSON output
        try:
            output_data = extract_json_from_output(result.stdout)
            assert isinstance(output_data, dict)
            # Verify it contains expected structure
            assert "results" in output_data or "summary" in output_data
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"Failed to parse JSON output: {e}")

    def test_scan_with_cis_gcp_pack(self, sample_terraform_file: Path) -> None:
        """Test scanning with CIS GCP rule pack."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "cis-gcp",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "json",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # Extract and validate JSON output
        try:
            output_data = extract_json_from_output(result.stdout)
            assert isinstance(output_data, dict)
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"Failed to parse JSON output: {e}")

    def test_scan_with_azure_security_pack(self, sample_terraform_file: Path) -> None:
        """Test scanning with Azure security rule pack."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "azure-security",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "json",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # Extract and validate JSON output
        try:
            output_data = extract_json_from_output(result.stdout)
            assert isinstance(output_data, dict)
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"Failed to parse JSON output: {e}")

    def test_scan_with_multiple_new_rule_packs(self, sample_terraform_file: Path) -> None:
        """Test scanning with multiple new rule packs combined."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "gcp-security",
                "--rule-pack",
                "azure-security",
                "--rule-pack",
                "aws-well-architected",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "json",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # Extract and validate JSON output
        try:
            output_data = extract_json_from_output(result.stdout)
            assert isinstance(output_data, dict)
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"Failed to parse JSON output: {e}")

    def test_scan_combining_new_and_existing_packs(self, sample_terraform_file: Path) -> None:
        """Test combining new rule packs with existing rule packs."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "aws-security",  # existing pack
                "--rule-pack",
                "gcp-security",  # new pack
                "--rule-pack",
                "azure-security",  # new pack
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "json",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # Extract and validate JSON output
        try:
            output_data = extract_json_from_output(result.stdout)
            assert isinstance(output_data, dict)
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"Failed to parse JSON output: {e}")

    def test_scan_all_output_formats_table(self, sample_terraform_file: Path) -> None:
        """Test scanning with table output format."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "gcp-security",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "table",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # Table output should contain some structure
        assert len(result.stdout.strip()) > 0

    def test_scan_all_output_formats_junit(self, sample_terraform_file: Path) -> None:
        """Test scanning with JUnit XML output format."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "gcp-security",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "junit",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # JUnit output should contain XML
        assert "<?xml" in result.stdout or "<testsuite" in result.stdout

    def test_scan_all_output_formats_sarif(self, sample_terraform_file: Path) -> None:
        """Test scanning with SARIF output format."""
        result = run_cli_command(
            [
                "scan",
                "--rule-pack",
                "gcp-security",
                "--terraform",
                str(sample_terraform_file),
                "--output-format",
                "sarif",
            ]
        )

        assert result.returncode in [0, 1]  # 0 for pass, 1 for violations found

        # SARIF output should be valid JSON with specific structure
        try:
            output_data = extract_json_from_output(result.stdout)
            assert "$schema" in output_data or "version" in output_data
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"Failed to parse SARIF output: {e}")


class TestValidateRulePackCommand:
    """Test the validate-rule-pack CLI command."""

    def test_validate_gcp_security_pack(self) -> None:
        """Test validating the GCP security rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/gcp-security.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "gcp-security" in result.stdout
        assert "1.0.0" in result.stdout

    def test_validate_cis_gcp_pack(self) -> None:
        """Test validating the CIS GCP rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/cis-gcp.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "cis-gcp" in result.stdout

    def test_validate_azure_security_pack(self) -> None:
        """Test validating the Azure security rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/azure-security.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "azure-security" in result.stdout

    def test_validate_aws_well_architected_pack(self) -> None:
        """Test validating the AWS Well-Architected rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/aws-well-architected.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "aws-well-architected" in result.stdout

    def test_validate_azure_well_architected_pack(self) -> None:
        """Test validating the Azure Well-Architected rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/azure-well-architected.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "azure-well-architected" in result.stdout

    def test_validate_gcp_well_architected_pack(self) -> None:
        """Test validating the GCP Well-Architected rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/gcp-well-architected.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "gcp-well-architected" in result.stdout

    def test_validate_aws_hipaa_pack(self) -> None:
        """Test validating the AWS HIPAA rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/aws-hipaa.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "aws-hipaa" in result.stdout

    def test_validate_azure_hipaa_pack(self) -> None:
        """Test validating the Azure HIPAA rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/azure-hipaa.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "azure-hipaa" in result.stdout

    def test_validate_aws_pci_dss_pack(self) -> None:
        """Test validating the AWS PCI-DSS rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/aws-pci-dss.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "aws-pci-dss" in result.stdout

    def test_validate_multi_cloud_security_pack(self) -> None:
        """Test validating the Multi-Cloud Security rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/multi-cloud-security.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "multi-cloud-security" in result.stdout

    def test_validate_kubernetes_security_pack(self) -> None:
        """Test validating the Kubernetes Security rule pack."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/kubernetes-security.yml"])

        assert result.returncode == 0
        assert "✓ Rule pack is valid" in result.stdout
        assert "kubernetes-security" in result.stdout

    def test_validate_nonexistent_pack(self) -> None:
        """Test validating a nonexistent rule pack file."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/nonexistent-pack.yml"])

        assert result.returncode in [1, 2]  # 1 for validation error, 2 for argument error
        assert (
            "Error:" in result.stdout
            or "Error:" in result.stderr
            or "does not exist" in result.stderr
        )

    def test_validate_pack_shows_rule_counts(self) -> None:
        """Test that validation shows accurate rule counts."""
        result = run_cli_command(["validate-rule-pack", "rule_packs/gcp-security.yml"])

        assert result.returncode == 0
        assert "Rules:" in result.stdout

        # Extract rule count
        lines = result.stdout.split("\n")
        rules_line = [line for line in lines if "Rules:" in line]
        assert len(rules_line) == 1

        # Should show a reasonable number of rules
        rule_count_str = rules_line[0].split("Rules:")[-1].strip()
        rule_count = int(rule_count_str)
        assert 0 < rule_count < 100

    def test_validate_pack_shows_warnings_if_any(self) -> None:
        """Test that validation shows warnings if any exist."""
        # This test assumes some packs might have warnings
        # We'll test with a pack that might have version warnings
        result = run_cli_command(["validate-rule-pack", "rule_packs/multi-cloud-security.yml"])

        assert result.returncode == 0
        # If there are warnings, they should be displayed
        # If no warnings, that's also fine
        assert "✓ Rule pack is valid" in result.stdout
