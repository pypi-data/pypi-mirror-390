"""Tests for rule pack management system."""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from riveter.rule_packs import RulePack, RulePackManager, RulePackMetadata
from riveter.rules import Rule, Severity


class TestRulePackMetadata:
    """Test RulePackMetadata class."""

    def test_metadata_creation(self) -> None:
        """Test creating rule pack metadata."""
        metadata = RulePackMetadata(
            name="test-pack",
            version="1.0.0",
            description="Test pack",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test"],
            min_riveter_version="0.1.0",
        )

        assert metadata.name == "test-pack"
        assert metadata.version == "1.0.0"
        assert metadata.description == "Test pack"
        assert metadata.author == "Test Author"
        assert metadata.dependencies == []
        assert metadata.tags == ["test"]


class TestRulePack:
    """Test RulePack class."""

    def test_rule_pack_creation(self) -> None:
        """Test creating a rule pack."""
        metadata = RulePackMetadata(
            name="test-pack",
            version="1.0.0",
            description="Test pack",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test"],
            min_riveter_version="0.1.0",
        )

        rule_dict = {
            "id": "test_rule",
            "resource_type": "aws_instance",
            "description": "Test rule",
            "severity": "error",
            "assert": {"instance_type": "t3.large"},
        }
        rule = Rule(rule_dict)

        pack = RulePack(metadata=metadata, rules=[rule])

        assert pack.metadata.name == "test-pack"
        assert len(pack.rules) == 1
        assert pack.rules[0].id == "test_rule"

    def test_rule_pack_duplicate_rule_ids(self) -> None:
        """Test that rule pack validation catches duplicate rule IDs."""
        metadata = RulePackMetadata(
            name="test-pack",
            version="1.0.0",
            description="Test pack",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test"],
            min_riveter_version="0.1.0",
        )

        rule1_dict = {
            "id": "duplicate_rule",
            "resource_type": "aws_instance",
            "description": "First rule",
            "severity": "error",
            "assert": {"instance_type": "t3.large"},
        }
        rule2_dict = {
            "id": "duplicate_rule",
            "resource_type": "aws_s3_bucket",
            "description": "Second rule",
            "severity": "warning",
            "assert": {"versioning.enabled": True},
        }

        rule1 = Rule(rule1_dict)
        rule2 = Rule(rule2_dict)

        with pytest.raises(ValueError, match="Duplicate rule ID"):
            RulePack(metadata=metadata, rules=[rule1, rule2])

    def test_filter_by_severity(self) -> None:
        """Test filtering rules by severity."""
        metadata = RulePackMetadata(
            name="test-pack",
            version="1.0.0",
            description="Test pack",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test"],
            min_riveter_version="0.1.0",
        )

        error_rule = Rule(
            {
                "id": "error_rule",
                "resource_type": "aws_instance",
                "description": "Error rule",
                "severity": "error",
                "assert": {"instance_type": "t3.large"},
            }
        )

        warning_rule = Rule(
            {
                "id": "warning_rule",
                "resource_type": "aws_s3_bucket",
                "description": "Warning rule",
                "severity": "warning",
                "assert": {"versioning.enabled": True},
            }
        )

        info_rule = Rule(
            {
                "id": "info_rule",
                "resource_type": "aws_vpc",
                "description": "Info rule",
                "severity": "info",
                "assert": {"enable_dns_hostnames": True},
            }
        )

        pack = RulePack(metadata=metadata, rules=[error_rule, warning_rule, info_rule])

        # Filter by error severity (should include only error rules)
        error_pack = pack.filter_by_severity(Severity.ERROR)
        assert len(error_pack.rules) == 1
        assert error_pack.rules[0].id == "error_rule"

        # Filter by warning severity (should include warning and error rules)
        warning_pack = pack.filter_by_severity(Severity.WARNING)
        assert len(warning_pack.rules) == 2
        rule_ids = {rule.id for rule in warning_pack.rules}
        assert rule_ids == {"error_rule", "warning_rule"}

        # Filter by info severity (should include all rules)
        info_pack = pack.filter_by_severity(Severity.INFO)
        assert len(info_pack.rules) == 3

    def test_filter_by_resource_type(self) -> None:
        """Test filtering rules by resource type."""
        metadata = RulePackMetadata(
            name="test-pack",
            version="1.0.0",
            description="Test pack",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test"],
            min_riveter_version="0.1.0",
        )

        ec2_rule = Rule(
            {
                "id": "ec2_rule",
                "resource_type": "aws_instance",
                "description": "EC2 rule",
                "severity": "error",
                "assert": {"instance_type": "t3.large"},
            }
        )

        s3_rule = Rule(
            {
                "id": "s3_rule",
                "resource_type": "aws_s3_bucket",
                "description": "S3 rule",
                "severity": "warning",
                "assert": {"versioning.enabled": True},
            }
        )

        pack = RulePack(metadata=metadata, rules=[ec2_rule, s3_rule])

        # Filter by EC2 resource type
        ec2_pack = pack.filter_by_resource_type(["aws_instance"])
        assert len(ec2_pack.rules) == 1
        assert ec2_pack.rules[0].id == "ec2_rule"

        # Filter by multiple resource types
        multi_pack = pack.filter_by_resource_type(["aws_instance", "aws_s3_bucket"])
        assert len(multi_pack.rules) == 2

    def test_merge_rule_packs(self) -> None:
        """Test merging two rule packs."""
        metadata1 = RulePackMetadata(
            name="pack1",
            version="1.0.0",
            description="First pack",
            author="Author 1",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test1"],
            min_riveter_version="0.1.0",
        )

        metadata2 = RulePackMetadata(
            name="pack2",
            version="2.0.0",
            description="Second pack",
            author="Author 2",
            created="2024-02-01",
            updated="2024-02-01",
            dependencies=["pack1"],
            tags=["test2"],
            min_riveter_version="0.2.0",
        )

        rule1 = Rule(
            {
                "id": "rule1",
                "resource_type": "aws_instance",
                "description": "Rule 1",
                "severity": "error",
                "assert": {"instance_type": "t3.large"},
            }
        )

        rule2 = Rule(
            {
                "id": "rule2",
                "resource_type": "aws_s3_bucket",
                "description": "Rule 2",
                "severity": "warning",
                "assert": {"versioning.enabled": True},
            }
        )

        pack1 = RulePack(metadata=metadata1, rules=[rule1])
        pack2 = RulePack(metadata=metadata2, rules=[rule2])

        merged_pack = pack1.merge_with(pack2)

        assert len(merged_pack.rules) == 2
        assert merged_pack.metadata.name == "pack1+pack2"
        assert merged_pack.metadata.version == "merged"
        assert "Author 1" in merged_pack.metadata.author
        assert "Author 2" in merged_pack.metadata.author
        assert set(merged_pack.metadata.tags) == {"test1", "test2"}
        assert merged_pack.metadata.min_riveter_version == "0.2.0"

    def test_merge_conflicting_rule_ids(self) -> None:
        """Test that merging packs with conflicting rule IDs raises an error."""
        metadata1 = RulePackMetadata(
            name="pack1",
            version="1.0.0",
            description="First pack",
            author="Author 1",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test1"],
            min_riveter_version="0.1.0",
        )

        metadata2 = RulePackMetadata(
            name="pack2",
            version="2.0.0",
            description="Second pack",
            author="Author 2",
            created="2024-02-01",
            updated="2024-02-01",
            dependencies=[],
            tags=["test2"],
            min_riveter_version="0.1.0",
        )

        rule1 = Rule(
            {
                "id": "conflicting_rule",
                "resource_type": "aws_instance",
                "description": "Rule 1",
                "severity": "error",
                "assert": {"instance_type": "t3.large"},
            }
        )

        rule2 = Rule(
            {
                "id": "conflicting_rule",
                "resource_type": "aws_s3_bucket",
                "description": "Rule 2",
                "severity": "warning",
                "assert": {"versioning.enabled": True},
            }
        )

        pack1 = RulePack(metadata=metadata1, rules=[rule1])
        pack2 = RulePack(metadata=metadata2, rules=[rule2])

        with pytest.raises(ValueError, match="conflicting rule IDs"):
            pack1.merge_with(pack2)

    def test_to_dict(self) -> None:
        """Test converting rule pack to dictionary."""
        metadata = RulePackMetadata(
            name="test-pack",
            version="1.0.0",
            description="Test pack",
            author="Test Author",
            created="2024-01-01",
            updated="2024-01-01",
            dependencies=[],
            tags=["test"],
            min_riveter_version="0.1.0",
        )

        rule = Rule(
            {
                "id": "test_rule",
                "resource_type": "aws_instance",
                "description": "Test rule",
                "severity": "error",
                "assert": {"instance_type": "t3.large"},
                "metadata": {"tags": ["test"]},
            }
        )

        pack = RulePack(metadata=metadata, rules=[rule])
        pack_dict = pack.to_dict()

        assert pack_dict["metadata"]["name"] == "test-pack"
        assert pack_dict["metadata"]["version"] == "1.0.0"
        assert len(pack_dict["rules"]) == 1
        assert pack_dict["rules"][0]["id"] == "test_rule"
        assert pack_dict["rules"][0]["resource_type"] == "aws_instance"


class TestRulePackManager:
    """Test RulePackManager class."""

    def test_manager_initialization(self) -> None:
        """Test rule pack manager initialization."""
        manager = RulePackManager()
        assert isinstance(manager.rule_pack_dirs, list)

    def test_manager_with_custom_dirs(self) -> None:
        """Test rule pack manager with custom directories."""
        custom_dirs = ["/custom/path1", "/custom/path2"]
        manager = RulePackManager(rule_pack_dirs=custom_dirs)

        # Custom dirs should be included
        for custom_dir in custom_dirs:
            assert custom_dir in manager.rule_pack_dirs

    def test_load_rule_pack_from_file(self, fixtures_dir: Path) -> None:
        """Test loading a rule pack from file."""
        manager = RulePackManager()
        pack_file = fixtures_dir / "rule_packs" / "test-pack.yml"

        pack = manager.load_rule_pack_from_file(str(pack_file))

        assert pack.metadata.name == "test-pack"
        assert pack.metadata.version == "1.0.0"
        assert len(pack.rules) == 2
        assert pack.rules[0].id == "test_rule_1"
        assert pack.rules[1].id == "test_rule_2"

    def test_load_invalid_rule_pack(self, fixtures_dir: Path) -> None:
        """Test loading an invalid rule pack."""
        manager = RulePackManager()
        pack_file = fixtures_dir / "rule_packs" / "invalid-pack.yml"

        with pytest.raises(ValueError, match="Missing required metadata field"):
            manager.load_rule_pack_from_file(str(pack_file))

    def test_load_rule_pack_with_duplicate_ids(self, fixtures_dir: Path) -> None:
        """Test loading a rule pack with duplicate rule IDs."""
        manager = RulePackManager()
        pack_file = fixtures_dir / "rule_packs" / "duplicate-rules.yml"

        with pytest.raises(ValueError, match="Duplicate rule ID"):
            manager.load_rule_pack_from_file(str(pack_file))

    def test_load_rule_pack_by_name(self, fixtures_dir: Path) -> None:
        """Test loading a rule pack by name."""
        # Create a temporary manager with the fixtures directory
        manager = RulePackManager(rule_pack_dirs=[str(fixtures_dir / "rule_packs")])

        pack = manager.load_rule_pack("test-pack")

        assert pack.metadata.name == "test-pack"
        assert len(pack.rules) == 2

    def test_load_nonexistent_rule_pack(self) -> None:
        """Test loading a nonexistent rule pack."""
        manager = RulePackManager(rule_pack_dirs=[])

        with pytest.raises(
            FileNotFoundError, match="Rule pack 'nonexistent' version 'latest' not found"
        ):
            manager.load_rule_pack("nonexistent")

    def test_list_available_packs(self, fixtures_dir: Path) -> None:
        """Test listing available rule packs."""
        manager = RulePackManager(rule_pack_dirs=[str(fixtures_dir / "rule_packs")])

        packs = manager.list_available_packs()

        # Should find at least the test packs
        pack_names = {pack["name"] for pack in packs}
        assert "test-pack" in pack_names
        assert "second-pack" in pack_names

        # Check that pack info is populated
        test_pack = next(pack for pack in packs if pack["name"] == "test-pack")
        assert test_pack["version"] == "1.0.0"
        assert test_pack["rule_count"] == 2
        assert test_pack["author"] == "Test Author"

    def test_validate_rule_pack_valid(self, fixtures_dir: Path) -> None:
        """Test validating a valid rule pack."""
        manager = RulePackManager()
        pack_file = str(fixtures_dir / "rule_packs" / "test-pack.yml")

        result = manager.validate_rule_pack(pack_file)

        assert result["valid"] is True
        assert result["rule_count"] == 2
        assert result["metadata"]["name"] == "test-pack"
        assert len(result["errors"]) == 0

    def test_validate_rule_pack_invalid(self, fixtures_dir: Path) -> None:
        """Test validating an invalid rule pack."""
        manager = RulePackManager()
        pack_file = str(fixtures_dir / "rule_packs" / "invalid-pack.yml")

        result = manager.validate_rule_pack(pack_file)

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_nonexistent_file(self) -> None:
        """Test validating a nonexistent file."""
        manager = RulePackManager()

        result = manager.validate_rule_pack("/nonexistent/file.yml")

        assert result["valid"] is False
        assert "File does not exist" in result["errors"][0]

    def test_merge_rule_packs(self, fixtures_dir: Path) -> None:
        """Test merging multiple rule packs."""
        manager = RulePackManager(rule_pack_dirs=[str(fixtures_dir / "rule_packs")])

        merged_pack = manager.merge_rule_packs(["test-pack", "second-pack"])

        assert len(merged_pack.rules) == 4  # 2 from test-pack + 2 from second-pack
        assert merged_pack.metadata.name == "test-pack+second-pack"

        # Check that all rules are present
        rule_ids = {rule.id for rule in merged_pack.rules}
        expected_ids = {"test_rule_1", "test_rule_2", "second_pack_rule_1", "second_pack_rule_2"}
        assert rule_ids == expected_ids

    def test_merge_empty_pack_list(self) -> None:
        """Test merging with empty pack list."""
        manager = RulePackManager()

        with pytest.raises(ValueError, match="At least one rule pack name must be provided"):
            manager.merge_rule_packs([])

    def test_create_rule_pack_template(self) -> None:
        """Test creating a rule pack template."""
        manager = RulePackManager()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            template_file = f.name

        try:
            manager.create_rule_pack_template("my-pack", template_file)

            # Verify the template was created
            assert os.path.exists(template_file)

            # Verify the template content
            with open(template_file, "r") as f:
                template_data = yaml.safe_load(f)

            assert template_data["metadata"]["name"] == "my-pack"
            assert template_data["metadata"]["version"] == "1.0.0"
            assert len(template_data["rules"]) == 1
            assert template_data["rules"][0]["id"] == "my_pack_example_rule"

        finally:
            if os.path.exists(template_file):
                os.unlink(template_file)


@pytest.fixture
def fixtures_dir() -> Path:
    """Provide path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


class TestGCPSecurityRulePack:
    """Integration tests for GCP Security Best Practices rule pack."""

    def test_gcp_security_pack_loads(self) -> None:
        """Test that the GCP security rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        assert pack.metadata.name == "gcp-security"
        assert pack.metadata.version == "1.0.0"
        assert pack.metadata.description == "GCP Security Best Practices Rule Pack"
        assert "gcp" in pack.metadata.tags
        assert "security" in pack.metadata.tags
        assert len(pack.rules) == 29

    def test_gcp_security_pack_metadata(self) -> None:
        """Test GCP security rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_gcp_security_pack_rule_categories(self) -> None:
        """Test that GCP security pack covers all expected categories."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        # Get all resource types covered
        resource_types = {rule.resource_type for rule in pack.rules}

        # Verify coverage of major GCP resource types
        expected_types = {
            "google_compute_instance",
            "google_compute_project_metadata",
            "google_compute_disk",
            "google_storage_bucket",
            "google_sql_database_instance",
            "google_compute_subnetwork",
            "google_compute_firewall",
            "google_compute_router_nat",
            "google_project_iam_binding",
            "google_service_account",
            "google_container_cluster",
            "google_kms_crypto_key",
        }

        assert expected_types.issubset(resource_types)

    def test_gcp_security_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in GCP security pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_gcp_security_pack_all_rules_have_metadata(self) -> None:
        """Test that all rules have proper metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        for rule in pack.rules:
            # Each rule should have an ID and description
            assert rule.id is not None
            assert rule.description is not None
            assert len(rule.description) > 10

            # Each rule should have metadata with tags and references
            assert hasattr(rule, "metadata")
            assert "tags" in rule.metadata
            assert "references" in rule.metadata
            assert len(rule.metadata["tags"]) > 0
            assert len(rule.metadata["references"]) > 0

    def test_gcp_security_pack_severity_levels(self) -> None:
        """Test that GCP security pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities

        # Most rules should be error or warning
        error_warning_count = sum(1 for s in severities if s in [Severity.ERROR, Severity.WARNING])
        assert error_warning_count >= len(pack.rules) * 0.7  # At least 70%

    def test_gcp_security_pack_filter_by_compute(self) -> None:
        """Test filtering GCP security pack by compute resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        compute_pack = pack.filter_by_resource_type(
            ["google_compute_instance", "google_compute_project_metadata", "google_compute_disk"]
        )

        # Should have at least 6 compute-related rules
        assert len(compute_pack.rules) >= 6

        # All rules should be compute-related
        for rule in compute_pack.rules:
            assert rule.resource_type.startswith("google_compute")

    def test_gcp_security_pack_filter_by_storage(self) -> None:
        """Test filtering GCP security pack by storage resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        storage_pack = pack.filter_by_resource_type(["google_storage_bucket"])

        # Should have at least 6 storage-related rules
        assert len(storage_pack.rules) >= 6

        # All rules should be storage-related
        for rule in storage_pack.rules:
            assert rule.resource_type == "google_storage_bucket"

    def test_gcp_security_pack_filter_by_sql(self) -> None:
        """Test filtering GCP security pack by Cloud SQL resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-security")

        sql_pack = pack.filter_by_resource_type(["google_sql_database_instance"])

        # Should have at least 5 SQL-related rules
        assert len(sql_pack.rules) >= 5

        # All rules should be SQL-related
        for rule in sql_pack.rules:
            assert rule.resource_type == "google_sql_database_instance"

    def test_gcp_security_pack_merge_with_aws(self) -> None:
        """Test merging GCP security pack with AWS security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["gcp-security", "aws-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 29  # More than just GCP rules

        # Should have both GCP and AWS resource types
        resource_types = {rule.resource_type for rule in merged_pack.rules}
        assert any(rt.startswith("google_") for rt in resource_types)
        assert any(rt.startswith("aws_") for rt in resource_types)

        # Metadata should reflect merge
        assert "gcp-security" in merged_pack.metadata.name
        assert "aws-security" in merged_pack.metadata.name


class TestCISGCPRulePack:
    """Integration tests for CIS GCP Benchmark rule pack."""

    def test_cis_gcp_pack_loads(self) -> None:
        """Test that the CIS GCP rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        assert pack.metadata.name == "cis-gcp"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "CIS Google Cloud Platform Foundation Benchmark v1.3.0 Rule Pack"
        )
        assert "cis" in pack.metadata.tags
        assert "gcp" in pack.metadata.tags
        assert len(pack.rules) == 43

    def test_cis_gcp_pack_metadata(self) -> None:
        """Test CIS GCP rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_cis_gcp_pack_rule_categories(self) -> None:
        """Test that CIS GCP pack covers all expected sections."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        # Get all CIS control numbers
        cis_controls = set()
        for rule in pack.rules:
            if "cis_control" in rule.metadata:
                control = rule.metadata["cis_control"]
                section = control.split(".")[0]
                cis_controls.add(section)

        # Verify coverage of major CIS sections
        expected_sections = {"1", "2", "3", "4", "5", "6"}
        assert expected_sections.issubset(cis_controls)

    def test_cis_gcp_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in CIS GCP pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_cis_gcp_pack_all_rules_have_cis_control(self) -> None:
        """Test that all rules have CIS control references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        for rule in pack.rules:
            # Each rule should have CIS control metadata
            assert "cis_control" in rule.metadata
            assert rule.metadata["cis_control"] is not None
            assert len(rule.metadata["cis_control"]) > 0

            # CIS control should be in format "X.Y"
            control = rule.metadata["cis_control"]
            parts = control.split(".")
            assert len(parts) == 2
            assert parts[0].isdigit()
            assert parts[1].isdigit()

    def test_cis_gcp_pack_severity_levels(self) -> None:
        """Test that CIS GCP pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error and warning rules
        assert Severity.ERROR in severities

        # Most rules should be error (CIS benchmarks are strict)
        error_count = sum(1 for s in severities if s == Severity.ERROR)
        assert error_count >= len(pack.rules) * 0.7  # At least 70% error

    def test_cis_gcp_pack_filter_by_iam(self) -> None:
        """Test filtering CIS GCP pack by IAM resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        iam_pack = pack.filter_by_resource_type(
            [
                "google_project_iam_binding",
                "google_service_account_key",
                "google_organization_iam_binding",
                "google_kms_crypto_key_iam_binding",
            ]
        )

        # Should have at least 8 IAM-related rules (Section 1)
        assert len(iam_pack.rules) >= 8

    def test_cis_gcp_pack_filter_by_logging(self) -> None:
        """Test filtering CIS GCP pack by logging resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        logging_pack = pack.filter_by_resource_type(
            [
                "google_logging_metric",
                "google_logging_project_bucket_config",
                "google_logging_project_sink",
            ]
        )

        # Should have at least 8 logging-related rules (Section 2)
        assert len(logging_pack.rules) >= 8

    def test_cis_gcp_pack_filter_by_networking(self) -> None:
        """Test filtering CIS GCP pack by networking resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("cis-gcp")

        network_pack = pack.filter_by_resource_type(
            [
                "google_compute_network",
                "google_dns_managed_zone",
                "google_compute_firewall",
                "google_compute_subnetwork",
            ]
        )

        # Should have at least 6 networking-related rules (Section 3)
        assert len(network_pack.rules) >= 6

    def test_cis_gcp_pack_merge_with_gcp_security(self) -> None:
        """Test merging CIS GCP pack with GCP security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["cis-gcp", "gcp-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 43  # More than just CIS rules

        # Should have both CIS and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("cis_gcp_") for rid in rule_ids)
        assert any(rid.startswith("gcp_") for rid in rule_ids)

        # Metadata should reflect merge
        assert "cis-gcp" in merged_pack.metadata.name
        assert "gcp-security" in merged_pack.metadata.name


class TestAzureSecurityRulePack:
    """Integration tests for Azure Security Best Practices rule pack."""

    def test_azure_security_pack_loads(self) -> None:
        """Test that the Azure security rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        assert pack.metadata.name == "azure-security"
        assert pack.metadata.version == "1.0.0"
        assert pack.metadata.description == "Azure Security Best Practices Rule Pack"
        assert "azure" in pack.metadata.tags
        assert "security" in pack.metadata.tags
        assert len(pack.rules) == 28

    def test_azure_security_pack_metadata(self) -> None:
        """Test Azure security rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_azure_security_pack_rule_categories(self) -> None:
        """Test that Azure security pack covers all expected categories."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        # Get all resource types covered
        resource_types = {rule.resource_type for rule in pack.rules}

        # Verify coverage of major Azure resource types
        expected_types = {
            "azurerm_linux_virtual_machine",
            "azurerm_network_interface",
            "azurerm_managed_disk",
            "azurerm_storage_account",
            "azurerm_mssql_server",
            "azurerm_mssql_database",
            "azurerm_network_security_rule",
            "azurerm_network_security_group",
            "azurerm_key_vault",
            "azurerm_role_assignment",
        }

        assert expected_types.issubset(resource_types)

    def test_azure_security_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in Azure security pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_azure_security_pack_all_rules_have_metadata(self) -> None:
        """Test that all rules have proper metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        for rule in pack.rules:
            # Each rule should have an ID and description
            assert rule.id is not None
            assert rule.description is not None
            assert len(rule.description) > 10

            # Each rule should have metadata with tags and references
            assert hasattr(rule, "metadata")
            assert "tags" in rule.metadata
            assert "references" in rule.metadata
            assert len(rule.metadata["tags"]) > 0
            assert len(rule.metadata["references"]) > 0

    def test_azure_security_pack_severity_levels(self) -> None:
        """Test that Azure security pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities

        # Most rules should be error or warning
        error_warning_count = sum(1 for s in severities if s in [Severity.ERROR, Severity.WARNING])
        assert error_warning_count >= len(pack.rules) * 0.7  # At least 70%

    def test_azure_security_pack_filter_by_vm(self) -> None:
        """Test filtering Azure security pack by VM resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        vm_pack = pack.filter_by_resource_type(
            [
                "azurerm_virtual_machine",
                "azurerm_linux_virtual_machine",
                "azurerm_network_interface",
                "azurerm_managed_disk",
            ]
        )

        # Should have at least 6 VM-related rules
        assert len(vm_pack.rules) >= 6

    def test_azure_security_pack_filter_by_storage(self) -> None:
        """Test filtering Azure security pack by storage resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        storage_pack = pack.filter_by_resource_type(["azurerm_storage_account"])

        # Should have at least 6 storage-related rules
        assert len(storage_pack.rules) >= 6

        # All rules should be storage-related
        for rule in storage_pack.rules:
            assert rule.resource_type == "azurerm_storage_account"

    def test_azure_security_pack_filter_by_sql(self) -> None:
        """Test filtering Azure security pack by SQL resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-security")

        sql_pack = pack.filter_by_resource_type(
            [
                "azurerm_mssql_server",
                "azurerm_mssql_database",
                "azurerm_mssql_server_security_alert_policy",
            ]
        )

        # Should have at least 5 SQL-related rules
        assert len(sql_pack.rules) >= 5

    def test_azure_security_pack_merge_with_aws(self) -> None:
        """Test merging Azure security pack with AWS security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["azure-security", "aws-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 28  # More than just Azure rules

        # Should have both Azure and AWS resource types
        resource_types = {rule.resource_type for rule in merged_pack.rules}
        assert any(rt.startswith("azurerm_") for rt in resource_types)
        assert any(rt.startswith("aws_") for rt in resource_types)

        # Metadata should reflect merge
        assert "azure-security" in merged_pack.metadata.name
        assert "aws-security" in merged_pack.metadata.name


class TestAWSWellArchitectedRulePack:
    """Integration tests for AWS Well-Architected Framework rule pack."""

    def test_aws_wa_pack_loads(self) -> None:
        """Test that the AWS Well-Architected rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        assert pack.metadata.name == "aws-well-architected"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "AWS Well-Architected Framework Rule Pack covering all 6 pillars"
        )
        assert "well-architected" in pack.metadata.tags
        assert "aws" in pack.metadata.tags
        assert len(pack.rules) == 34

    def test_aws_wa_pack_metadata(self) -> None:
        """Test AWS Well-Architected rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_aws_wa_pack_pillar_coverage(self) -> None:
        """Test that AWS Well-Architected pack covers all 6 pillars."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        # Get all pillars covered
        pillars = set()
        for rule in pack.rules:
            if "pillar" in rule.metadata:
                pillars.add(rule.metadata["pillar"])

        # Verify coverage of all 6 pillars
        expected_pillars = {
            "Operational Excellence",
            "Security",
            "Reliability",
            "Performance Efficiency",
            "Cost Optimization",
            "Sustainability",
        }
        assert expected_pillars == pillars

    def test_aws_wa_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in AWS Well-Architected pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_aws_wa_pack_all_rules_have_pillar(self) -> None:
        """Test that all rules have pillar references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        for rule in pack.rules:
            # Each rule should have pillar metadata
            assert "pillar" in rule.metadata
            assert rule.metadata["pillar"] is not None
            assert len(rule.metadata["pillar"]) > 0

    def test_aws_wa_pack_severity_levels(self) -> None:
        """Test that AWS Well-Architected pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities
        assert Severity.INFO in severities

    def test_aws_wa_pack_operational_excellence_pillar(self) -> None:
        """Test filtering AWS Well-Architected pack by Operational Excellence pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        opex_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Operational Excellence"
        ]

        # Should have 6-8 Operational Excellence rules
        assert 6 <= len(opex_rules) <= 8

        # Verify resource types are appropriate for operational excellence
        resource_types = {rule.resource_type for rule in opex_rules}
        expected_types = {"aws_cloudwatch_metric_alarm", "aws_autoscaling_policy", "aws_instance"}
        assert expected_types.issubset(resource_types)

    def test_aws_wa_pack_security_pillar(self) -> None:
        """Test filtering AWS Well-Architected pack by Security pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        security_rules = [rule for rule in pack.rules if rule.metadata.get("pillar") == "Security"]

        # Should have 6-8 Security rules
        assert 6 <= len(security_rules) <= 8

    def test_aws_wa_pack_reliability_pillar(self) -> None:
        """Test filtering AWS Well-Architected pack by Reliability pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        reliability_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Reliability"
        ]

        # Should have 6-8 Reliability rules
        assert 6 <= len(reliability_rules) <= 8

        # Verify resource types are appropriate for reliability
        resource_types = {rule.resource_type for rule in reliability_rules}
        expected_types = {"aws_db_instance", "aws_autoscaling_group", "aws_lb_target_group"}
        assert expected_types.issubset(resource_types)

    def test_aws_wa_pack_performance_pillar(self) -> None:
        """Test filtering AWS Well-Architected pack by Performance Efficiency pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        performance_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Performance Efficiency"
        ]

        # Should have 4-6 Performance Efficiency rules
        assert 4 <= len(performance_rules) <= 6

    def test_aws_wa_pack_cost_optimization_pillar(self) -> None:
        """Test filtering AWS Well-Architected pack by Cost Optimization pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        cost_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Cost Optimization"
        ]

        # Should have 4-6 Cost Optimization rules
        assert 4 <= len(cost_rules) <= 6

    def test_aws_wa_pack_sustainability_pillar(self) -> None:
        """Test filtering AWS Well-Architected pack by Sustainability pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-well-architected")

        sustainability_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Sustainability"
        ]

        # Should have 2-4 Sustainability rules
        assert 2 <= len(sustainability_rules) <= 4

    def test_aws_wa_pack_merge_with_aws_security(self) -> None:
        """Test merging AWS Well-Architected pack with AWS security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["aws-well-architected", "aws-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 34  # More than just Well-Architected rules

        # Should have both Well-Architected and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("aws_wa_") for rid in rule_ids)
        assert any(not rid.startswith("aws_wa_") for rid in rule_ids)

        # Metadata should reflect merge
        assert "aws-well-architected" in merged_pack.metadata.name
        assert "aws-security" in merged_pack.metadata.name


class TestAzureWellArchitectedRulePack:
    """Integration tests for Azure Well-Architected Framework rule pack."""

    def test_azure_wa_pack_loads(self) -> None:
        """Test that the Azure Well-Architected rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        assert pack.metadata.name == "azure-well-architected"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "Azure Well-Architected Framework Rule Pack covering all 5 pillars"
        )
        assert "well-architected" in pack.metadata.tags
        assert "azure" in pack.metadata.tags
        assert len(pack.rules) == 35

    def test_azure_wa_pack_metadata(self) -> None:
        """Test Azure Well-Architected rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_azure_wa_pack_pillar_coverage(self) -> None:
        """Test that Azure Well-Architected pack covers all 5 pillars."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        # Get all pillars covered
        pillars = set()
        for rule in pack.rules:
            if "pillar" in rule.metadata:
                pillars.add(rule.metadata["pillar"])

        # Verify coverage of all 5 pillars
        expected_pillars = {
            "Cost Optimization",
            "Operational Excellence",
            "Performance Efficiency",
            "Reliability",
            "Security",
        }
        assert expected_pillars == pillars

    def test_azure_wa_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in Azure Well-Architected pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_azure_wa_pack_all_rules_have_pillar(self) -> None:
        """Test that all rules have pillar references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        for rule in pack.rules:
            # Each rule should have pillar metadata
            assert "pillar" in rule.metadata
            assert rule.metadata["pillar"] is not None
            assert len(rule.metadata["pillar"]) > 0

    def test_azure_wa_pack_severity_levels(self) -> None:
        """Test that Azure Well-Architected pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities
        assert Severity.INFO in severities

    def test_azure_wa_pack_cost_optimization_pillar(self) -> None:
        """Test filtering Azure Well-Architected pack by Cost Optimization pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        cost_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Cost Optimization"
        ]

        # Should have 6-8 Cost Optimization rules
        assert 6 <= len(cost_rules) <= 8

    def test_azure_wa_pack_operational_excellence_pillar(self) -> None:
        """Test filtering Azure Well-Architected pack by Operational Excellence pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        opex_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Operational Excellence"
        ]

        # Should have 6-8 Operational Excellence rules
        assert 6 <= len(opex_rules) <= 8

    def test_azure_wa_pack_performance_pillar(self) -> None:
        """Test filtering Azure Well-Architected pack by Performance Efficiency pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        performance_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Performance Efficiency"
        ]

        # Should have 6-8 Performance Efficiency rules
        assert 6 <= len(performance_rules) <= 8

    def test_azure_wa_pack_reliability_pillar(self) -> None:
        """Test filtering Azure Well-Architected pack by Reliability pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        reliability_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Reliability"
        ]

        # Should have 6-8 Reliability rules
        assert 6 <= len(reliability_rules) <= 8

    def test_azure_wa_pack_security_pillar(self) -> None:
        """Test filtering Azure Well-Architected pack by Security pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-well-architected")

        security_rules = [rule for rule in pack.rules if rule.metadata.get("pillar") == "Security"]

        # Should have 6-8 Security rules
        assert 6 <= len(security_rules) <= 8

    def test_azure_wa_pack_merge_with_azure_security(self) -> None:
        """Test merging Azure Well-Architected pack with Azure security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["azure-well-architected", "azure-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 35  # More than just Well-Architected rules

        # Should have both Well-Architected and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("azure_wa_") for rid in rule_ids)
        assert any(rid.startswith("azure_") and not rid.startswith("azure_wa_") for rid in rule_ids)

        # Metadata should reflect merge
        assert "azure-well-architected" in merged_pack.metadata.name
        assert "azure-security" in merged_pack.metadata.name


class TestGCPWellArchitectedRulePack:
    """Integration tests for GCP Well-Architected Framework rule pack."""

    def test_gcp_wa_pack_loads(self) -> None:
        """Test that the GCP Well-Architected rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        assert pack.metadata.name == "gcp-well-architected"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "GCP Well-Architected Framework Rule Pack covering all 5 pillars"
        )
        assert "well-architected" in pack.metadata.tags
        assert "gcp" in pack.metadata.tags
        assert len(pack.rules) == 30

    def test_gcp_wa_pack_metadata(self) -> None:
        """Test GCP Well-Architected rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_gcp_wa_pack_pillar_coverage(self) -> None:
        """Test that GCP Well-Architected pack covers all 5 pillars."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        # Get all pillars covered
        pillars = set()
        for rule in pack.rules:
            if "pillar" in rule.metadata:
                pillars.add(rule.metadata["pillar"])

        # Verify coverage of all 5 pillars
        expected_pillars = {
            "Operational Excellence",
            "Security",
            "Reliability",
            "Performance",
            "Cost Optimization",
        }
        assert expected_pillars == pillars

    def test_gcp_wa_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in GCP Well-Architected pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_gcp_wa_pack_all_rules_have_pillar(self) -> None:
        """Test that all rules have pillar references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        for rule in pack.rules:
            # Each rule should have pillar metadata
            assert "pillar" in rule.metadata
            assert rule.metadata["pillar"] is not None
            assert len(rule.metadata["pillar"]) > 0

    def test_gcp_wa_pack_severity_levels(self) -> None:
        """Test that GCP Well-Architected pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities
        assert Severity.INFO in severities

    def test_gcp_wa_pack_operational_excellence_pillar(self) -> None:
        """Test filtering GCP Well-Architected pack by Operational Excellence pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        opex_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Operational Excellence"
        ]

        # Should have 5-7 Operational Excellence rules
        assert 5 <= len(opex_rules) <= 7

    def test_gcp_wa_pack_security_pillar(self) -> None:
        """Test filtering GCP Well-Architected pack by Security pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        security_rules = [rule for rule in pack.rules if rule.metadata.get("pillar") == "Security"]

        # Should have 5-7 Security rules
        assert 5 <= len(security_rules) <= 7

    def test_gcp_wa_pack_reliability_pillar(self) -> None:
        """Test filtering GCP Well-Architected pack by Reliability pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        reliability_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Reliability"
        ]

        # Should have 5-7 Reliability rules
        assert 5 <= len(reliability_rules) <= 7

    def test_gcp_wa_pack_performance_pillar(self) -> None:
        """Test filtering GCP Well-Architected pack by Performance pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        performance_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Performance"
        ]

        # Should have 5-7 Performance rules
        assert 5 <= len(performance_rules) <= 7

    def test_gcp_wa_pack_cost_optimization_pillar(self) -> None:
        """Test filtering GCP Well-Architected pack by Cost Optimization pillar."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("gcp-well-architected")

        cost_rules = [
            rule for rule in pack.rules if rule.metadata.get("pillar") == "Cost Optimization"
        ]

        # Should have 5-7 Cost Optimization rules
        assert 5 <= len(cost_rules) <= 7

    def test_gcp_wa_pack_merge_with_gcp_security(self) -> None:
        """Test merging GCP Well-Architected pack with GCP security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["gcp-well-architected", "gcp-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 30  # More than just Well-Architected rules

        # Should have both Well-Architected and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("gcp_wa_") for rid in rule_ids)
        assert any(rid.startswith("gcp_") and not rid.startswith("gcp_wa_") for rid in rule_ids)

        # Metadata should reflect merge
        assert "gcp-well-architected" in merged_pack.metadata.name
        assert "gcp-security" in merged_pack.metadata.name


class TestAWSHIPAARulePack:
    """Integration tests for AWS HIPAA Compliance rule pack."""

    def test_aws_hipaa_pack_loads(self) -> None:
        """Test that the AWS HIPAA rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        assert pack.metadata.name == "aws-hipaa"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "AWS HIPAA Compliance Rule Pack - Healthcare data protection requirements"
        )
        assert "hipaa" in pack.metadata.tags
        assert "aws" in pack.metadata.tags
        assert "compliance" in pack.metadata.tags
        assert len(pack.rules) == 35

    def test_aws_hipaa_pack_metadata(self) -> None:
        """Test AWS HIPAA rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_aws_hipaa_pack_rule_categories(self) -> None:
        """Test that AWS HIPAA pack covers all expected categories."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        # Get all resource types covered
        resource_types = {rule.resource_type for rule in pack.rules}

        # Verify coverage of major AWS resource types for HIPAA
        expected_types = {
            "aws_s3_bucket",
            "aws_db_instance",
            "aws_ebs_volume",
            "aws_instance",
            "aws_kms_key",
            "aws_cloudtrail",
            "aws_iam_policy",
            "aws_iam_user",
            "aws_security_group",
            "aws_cloudwatch_log_group",
        }

        assert expected_types.issubset(resource_types)

    def test_aws_hipaa_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in AWS HIPAA pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_aws_hipaa_pack_all_rules_have_hipaa_control(self) -> None:
        """Test that all rules have HIPAA control references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        for rule in pack.rules:
            # Each rule should have HIPAA control metadata
            assert "hipaa_control" in rule.metadata
            assert rule.metadata["hipaa_control"] is not None
            assert len(rule.metadata["hipaa_control"]) > 0

            # HIPAA control should reference 164.xxx format
            control = rule.metadata["hipaa_control"]
            assert control.startswith("164.")

    def test_aws_hipaa_pack_severity_levels(self) -> None:
        """Test that AWS HIPAA pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        severities = [rule.severity for rule in pack.rules]

        # Should have mostly error rules (HIPAA is strict)
        assert Severity.ERROR in severities

        # Most rules should be error (HIPAA compliance is mandatory)
        error_count = sum(1 for s in severities if s == Severity.ERROR)
        assert error_count >= len(pack.rules) * 0.8  # At least 80% error

    def test_aws_hipaa_pack_filter_by_encryption(self) -> None:
        """Test filtering AWS HIPAA pack by encryption rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        encryption_rules = [
            rule
            for rule in pack.rules
            if "encryption" in rule.metadata.get("tags", [])
            or "encryption-in-transit" in rule.metadata.get("tags", [])
        ]

        # Should have 8-12 encryption-related rules (includes at-rest and in-transit)
        assert 8 <= len(encryption_rules) <= 12

    def test_aws_hipaa_pack_filter_by_access_control(self) -> None:
        """Test filtering AWS HIPAA pack by access control rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        access_control_rules = [
            rule for rule in pack.rules if "access-control" in rule.metadata.get("tags", [])
        ]

        # Should have 6-8 access control rules
        assert 6 <= len(access_control_rules) <= 8

    def test_aws_hipaa_pack_filter_by_audit_logging(self) -> None:
        """Test filtering AWS HIPAA pack by audit logging rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        audit_logging_rules = [
            rule for rule in pack.rules if "audit-logging" in rule.metadata.get("tags", [])
        ]

        # Should have 5-7 audit logging rules
        assert 5 <= len(audit_logging_rules) <= 7

    def test_aws_hipaa_pack_filter_by_network_security(self) -> None:
        """Test filtering AWS HIPAA pack by network security rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        network_security_rules = [
            rule for rule in pack.rules if "network-security" in rule.metadata.get("tags", [])
        ]

        # Should have 4-6 network security rules
        assert 4 <= len(network_security_rules) <= 6

    def test_aws_hipaa_pack_filter_by_backup(self) -> None:
        """Test filtering AWS HIPAA pack by backup and recovery rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        backup_rules = [
            rule
            for rule in pack.rules
            if "backup" in rule.metadata.get("tags", [])
            or "disaster-recovery" in rule.metadata.get("tags", [])
        ]

        # Should have 2-4 backup and recovery rules
        assert 2 <= len(backup_rules) <= 4

    def test_aws_hipaa_pack_phi_specific_rules(self) -> None:
        """Test that AWS HIPAA pack has PHI-specific rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        phi_rules = [rule for rule in pack.rules if "phi" in rule.metadata.get("tags", [])]

        # Should have several PHI-specific rules
        assert len(phi_rules) >= 5

        # PHI rules should have filters for DataClassification tag
        phi_filtered_rules = [rule for rule in phi_rules if rule.filter is not None]
        assert len(phi_filtered_rules) >= 3

    def test_aws_hipaa_pack_merge_with_aws_security(self) -> None:
        """Test merging AWS HIPAA pack with AWS security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["aws-hipaa", "aws-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 35  # More than just HIPAA rules

        # Should have both HIPAA and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("hipaa_") for rid in rule_ids)
        assert any(not rid.startswith("hipaa_") for rid in rule_ids)

        # Metadata should reflect merge
        assert "aws-hipaa" in merged_pack.metadata.name
        assert "aws-security" in merged_pack.metadata.name

    def test_aws_hipaa_pack_encryption_at_rest_coverage(self) -> None:
        """Test that AWS HIPAA pack covers encryption at rest for major services."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        # Get encryption at rest rules
        encryption_rules = [
            rule
            for rule in pack.rules
            if "164.312(a)(2)(iv)" in rule.metadata.get("hipaa_control", "")
        ]

        # Should cover S3, RDS, EBS, ElastiCache, Redshift
        resource_types = {rule.resource_type for rule in encryption_rules}
        expected_types = {
            "aws_s3_bucket",
            "aws_db_instance",
            "aws_ebs_volume",
            "aws_elasticache_replication_group",
            "aws_redshift_cluster",
        }

        assert expected_types.issubset(resource_types)

    def test_aws_hipaa_pack_encryption_in_transit_coverage(self) -> None:
        """Test that AWS HIPAA pack covers encryption in transit."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        # Get encryption in transit rules
        transit_encryption_rules = [
            rule for rule in pack.rules if "164.312(e)(1)" in rule.metadata.get("hipaa_control", "")
        ]

        # Should have rules for HTTPS, TLS, SSL enforcement
        assert len(transit_encryption_rules) >= 4

        # Should cover ALB, CloudFront, ElastiCache, network security
        resource_types = {rule.resource_type for rule in transit_encryption_rules}
        expected_types = {
            "aws_lb_listener",
            "aws_cloudfront_distribution",
            "aws_elasticache_replication_group",
        }

        # At least some of these should be present
        assert len(expected_types.intersection(resource_types)) >= 2

    def test_aws_hipaa_pack_audit_trail_integrity(self) -> None:
        """Test that AWS HIPAA pack enforces audit trail integrity."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        # Get audit logging rules
        audit_rules = [
            rule for rule in pack.rules if "164.312(b)" in rule.metadata.get("hipaa_control", "")
        ]

        # Should have CloudTrail log validation rule
        cloudtrail_validation_rules = [
            rule for rule in audit_rules if rule.resource_type == "aws_cloudtrail"
        ]
        assert len(cloudtrail_validation_rules) >= 1

        # Check that log validation is required
        validation_rule = next(
            (
                rule
                for rule in cloudtrail_validation_rules
                if "validation" in rule.id or "validation" in rule.description.lower()
            ),
            None,
        )
        assert validation_rule is not None

    def test_aws_hipaa_pack_least_privilege_enforcement(self) -> None:
        """Test that AWS HIPAA pack enforces least privilege principle."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-hipaa")

        # Get access control rules related to least privilege
        least_privilege_rules = [
            rule
            for rule in pack.rules
            if "164.308(a)(4)(ii)(B)" in rule.metadata.get("hipaa_control", "")
        ]

        # Should have rules for IAM policies, public access, etc.
        assert len(least_privilege_rules) >= 4

        # Should include IAM policy wildcard check
        iam_policy_rules = [
            rule for rule in least_privilege_rules if rule.resource_type == "aws_iam_policy"
        ]
        assert len(iam_policy_rules) >= 1


class TestAzureHIPAARulePack:
    """Integration tests for Azure HIPAA Compliance rule pack."""

    def test_azure_hipaa_pack_loads(self) -> None:
        """Test that the Azure HIPAA rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        assert pack.metadata.name == "azure-hipaa"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "Azure HIPAA Compliance Rule Pack - Healthcare data protection requirements"
        )
        assert "hipaa" in pack.metadata.tags
        assert "azure" in pack.metadata.tags
        assert "compliance" in pack.metadata.tags
        assert "healthcare" in pack.metadata.tags
        assert "phi" in pack.metadata.tags
        assert len(pack.rules) == 30

    def test_azure_hipaa_pack_metadata(self) -> None:
        """Test Azure HIPAA rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_azure_hipaa_pack_rule_categories(self) -> None:
        """Test that Azure HIPAA pack covers all expected categories."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Get all resource types covered
        resource_types = {rule.resource_type for rule in pack.rules}

        # Verify coverage of major Azure resource types for HIPAA
        expected_types = {
            "azurerm_storage_account",
            "azurerm_mssql_database",
            "azurerm_mssql_server",
            "azurerm_linux_virtual_machine",
            "azurerm_managed_disk",
            "azurerm_cosmosdb_account",
            "azurerm_app_service",
            "azurerm_function_app",
            "azurerm_key_vault",
            "azurerm_role_assignment",
            "azurerm_monitor_log_profile",
            "azurerm_network_security_rule",
            "azurerm_network_interface",
            "azurerm_network_watcher_flow_log",
            "azurerm_backup_protected_vm",
        }

        assert expected_types.issubset(resource_types)

    def test_azure_hipaa_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in Azure HIPAA pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_azure_hipaa_pack_all_rules_have_hipaa_control(self) -> None:
        """Test that all rules have HIPAA control references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        for rule in pack.rules:
            # Each rule should have HIPAA control metadata
            assert "hipaa_control" in rule.metadata
            assert rule.metadata["hipaa_control"] is not None
            assert len(rule.metadata["hipaa_control"]) > 0

            # HIPAA control should be in format "164.XXX(x)(x)(x)"
            control = rule.metadata["hipaa_control"]
            assert control.startswith("164.")
            assert "(" in control and ")" in control

    def test_azure_hipaa_pack_severity_levels(self) -> None:
        """Test that Azure HIPAA pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        severities = [rule.severity for rule in pack.rules]

        # Should have mostly error rules (HIPAA compliance is strict)
        assert Severity.ERROR in severities

        # Most rules should be error (HIPAA requirements are mandatory)
        error_count = sum(1 for s in severities if s == Severity.ERROR)
        assert error_count >= len(pack.rules) * 0.8  # At least 80% error

    def test_azure_hipaa_pack_filter_by_encryption(self) -> None:
        """Test filtering Azure HIPAA pack by encryption rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Filter rules by encryption-related tags
        encryption_rules = []
        for rule in pack.rules:
            if "encryption" in rule.metadata.get("tags", []):
                encryption_rules.append(rule)

        # Should have at least 5 encryption-related rules
        assert len(encryption_rules) >= 5

        # Check that encryption rules cover key resource types
        encryption_resource_types = {rule.resource_type for rule in encryption_rules}
        # Should include storage, database, and compute encryption
        assert "azurerm_storage_account" in encryption_resource_types
        assert "azurerm_mssql_database" in encryption_resource_types

    def test_azure_hipaa_pack_filter_by_access_control(self) -> None:
        """Test filtering Azure HIPAA pack by access control rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Filter rules by access-control-related tags
        access_control_rules = []
        for rule in pack.rules:
            if "access-control" in rule.metadata.get("tags", []):
                access_control_rules.append(rule)

        # Should have at least 6 access control-related rules
        assert len(access_control_rules) >= 6

        # Check that access control rules cover key resource types
        access_control_resource_types = {rule.resource_type for rule in access_control_rules}
        # Should include storage and database access controls
        assert "azurerm_storage_account" in access_control_resource_types
        assert "azurerm_key_vault" in access_control_resource_types

    def test_azure_hipaa_pack_filter_by_audit_logging(self) -> None:
        """Test filtering Azure HIPAA pack by audit logging rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Filter rules by audit-logging-related tags
        audit_logging_rules = []
        for rule in pack.rules:
            if "audit-logging" in rule.metadata.get("tags", []):
                audit_logging_rules.append(rule)

        # Should have at least 6 audit logging-related rules
        assert len(audit_logging_rules) >= 6

        # Check that audit logging rules cover key resource types
        audit_logging_resource_types = {rule.resource_type for rule in audit_logging_rules}
        expected_audit_logging_types = {
            "azurerm_monitor_log_profile",
            "azurerm_mssql_server",
            "azurerm_storage_account",
            "azurerm_key_vault",
            "azurerm_network_watcher_flow_log",
            "azurerm_app_service",
        }
        assert expected_audit_logging_types.issubset(audit_logging_resource_types)

    def test_azure_hipaa_pack_filter_by_network_security(self) -> None:
        """Test filtering Azure HIPAA pack by network security rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Filter rules by network-security-related tags
        network_security_rules = []
        for rule in pack.rules:
            if "network-security" in rule.metadata.get("tags", []):
                network_security_rules.append(rule)

        # Should have at least 4 network security-related rules
        assert len(network_security_rules) >= 4

        # Check that network security rules cover key resource types
        network_security_resource_types = {rule.resource_type for rule in network_security_rules}
        # Should include network security group rules
        assert "azurerm_network_security_rule" in network_security_resource_types

    def test_azure_hipaa_pack_filter_by_backup_recovery(self) -> None:
        """Test filtering Azure HIPAA pack by backup and recovery rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Filter rules by backup/recovery-related tags
        backup_recovery_rules = []
        for rule in pack.rules:
            rule_tags = rule.metadata.get("tags", [])
            if any(tag in rule_tags for tag in ["backup", "disaster-recovery", "data-protection"]):
                backup_recovery_rules.append(rule)

        # Should have at least 4 backup/recovery-related rules
        assert len(backup_recovery_rules) >= 4

        # Check that backup/recovery rules cover key resource types
        backup_recovery_resource_types = {rule.resource_type for rule in backup_recovery_rules}
        expected_backup_recovery_types = {
            "azurerm_backup_protected_vm",
            "azurerm_mssql_database",
            "azurerm_storage_account",
            "azurerm_key_vault",
        }
        assert expected_backup_recovery_types.issubset(backup_recovery_resource_types)

    def test_azure_hipaa_pack_phi_data_rules(self) -> None:
        """Test that rules properly handle PHI data classification."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Find rules that specifically check for PHI data classification
        phi_rules = []
        for rule in pack.rules:
            if hasattr(rule, "filter") and rule.filter:
                if (
                    isinstance(rule.filter, dict)
                    and rule.filter.get("tags", {}).get("DataClassification") == "PHI"
                ):
                    phi_rules.append(rule)
            # Also check rules tagged with PHI
            if "phi" in rule.metadata.get("tags", []):
                phi_rules.append(rule)

        # Should have several rules specifically for PHI data
        assert len(phi_rules) >= 7

        # PHI rules should cover critical resource types
        phi_resource_types = {rule.resource_type for rule in phi_rules}
        expected_phi_types = {
            "azurerm_storage_account",
            "azurerm_mssql_database",
            "azurerm_network_interface",
            "azurerm_app_service",
        }
        assert expected_phi_types.issubset(phi_resource_types)

    def test_azure_hipaa_pack_merge_with_azure_security(self) -> None:
        """Test merging Azure HIPAA pack with Azure security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["azure-hipaa", "azure-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 26  # More than just HIPAA rules

        # Should have both HIPAA and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("azure_hipaa_") for rid in rule_ids)
        assert any(
            rid.startswith("azure_") and not rid.startswith("azure_hipaa_") for rid in rule_ids
        )

        # Metadata should reflect merge
        assert "azure-hipaa" in merged_pack.metadata.name
        assert "azure-security" in merged_pack.metadata.name

    def test_azure_hipaa_pack_hipaa_control_coverage(self) -> None:
        """Test that Azure HIPAA pack covers key HIPAA controls."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        # Collect all HIPAA controls referenced
        hipaa_controls = set()
        for rule in pack.rules:
            control = rule.metadata.get("hipaa_control")
            if control:
                hipaa_controls.add(control)

        # Should cover key HIPAA controls
        expected_controls = {
            "164.312(a)(2)(iv)",  # Encryption at rest
            "164.312(e)(1)",  # Encryption in transit
            "164.308(a)(4)(ii)(B)",  # Access controls
            "164.312(b)",  # Audit logging
            "164.308(a)(7)(ii)(A)",  # Backup and recovery
        }

        assert expected_controls.issubset(hipaa_controls)

    def test_azure_hipaa_pack_all_rules_have_references(self) -> None:
        """Test that all rules have proper documentation references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        for rule in pack.rules:
            # Each rule should have references
            assert "references" in rule.metadata
            assert isinstance(rule.metadata["references"], list)
            assert len(rule.metadata["references"]) >= 2

            # Should have HIPAA reference and Azure documentation
            references = rule.metadata["references"]
            has_hipaa_ref = any("hipaa" in ref.lower() for ref in references)
            has_azure_ref = any(
                "microsoft.com" in ref or "docs.microsoft.com" in ref for ref in references
            )

            assert has_hipaa_ref, f"Rule {rule.id} missing HIPAA reference"
            assert has_azure_ref, f"Rule {rule.id} missing Azure documentation reference"

    def test_azure_hipaa_pack_rule_descriptions(self) -> None:
        """Test that all rules have proper descriptions."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("azure-hipaa")

        for rule in pack.rules:
            # Each rule should have a description
            assert rule.description is not None
            assert len(rule.description) > 20

            # Description should mention HIPAA
            assert "HIPAA" in rule.description

            # Description should be descriptive
            assert not rule.description.startswith("Rule")
            assert not rule.description.startswith("Check")


class TestAWSPCIDSSRulePack:
    """Integration tests for AWS PCI-DSS Compliance rule pack."""

    def test_aws_pci_dss_pack_loads(self) -> None:
        """Test that the AWS PCI-DSS rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        assert pack.metadata.name == "aws-pci-dss"
        assert pack.metadata.version == "1.0.0"
        expected_description = (
            "AWS PCI-DSS Compliance Rule Pack - "
            "Payment Card Industry Data Security Standard requirements"
        )
        assert pack.metadata.description == expected_description
        assert "pci-dss" in pack.metadata.tags
        assert "aws" in pack.metadata.tags
        assert "compliance" in pack.metadata.tags
        assert len(pack.rules) == 40

    def test_aws_pci_dss_pack_metadata(self) -> None:
        """Test AWS PCI-DSS rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_aws_pci_dss_pack_rule_categories(self) -> None:
        """Test that AWS PCI-DSS pack covers all expected categories."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        # Get all resource types covered
        resource_types = {rule.resource_type for rule in pack.rules}

        # Verify coverage of major AWS resource types for PCI-DSS
        expected_types = {
            "aws_security_group",
            "aws_network_acl",
            "aws_flow_log",
            "aws_lb",
            "aws_db_instance",
            "aws_instance",
            "aws_elasticache_replication_group",
            "aws_redshift_cluster",
            "aws_s3_bucket",
            "aws_ebs_volume",
            "aws_kms_key",
            "aws_cloudfront_distribution",
            "aws_lb_listener",
            "aws_dynamodb_table",
            "aws_iam_user",
            "aws_iam_policy",
            "aws_s3_bucket_public_access_block",
            "aws_iam_account_password_policy",
            "aws_iam_access_key",
            "aws_lambda_function",
            "aws_cloudtrail",
            "aws_cloudwatch_log_group",
            "aws_s3_bucket_logging",
            "aws_guardduty_detector",
            "aws_config_configuration_recorder",
            "aws_ssm_patch_baseline",
            "aws_inspector_assessment_target",
        }

        assert expected_types.issubset(resource_types)

    def test_aws_pci_dss_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in AWS PCI-DSS pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_aws_pci_dss_pack_all_rules_have_pci_control(self) -> None:
        """Test that all rules have PCI-DSS control references."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        for rule in pack.rules:
            # Each rule should have PCI-DSS control metadata
            assert "pci_requirement" in rule.metadata
            assert rule.metadata["pci_requirement"] is not None
            assert len(rule.metadata["pci_requirement"]) > 0

            # PCI requirement should be in format "X.Y" or "X.Y.Z"
            requirement = rule.metadata["pci_requirement"]
            parts = requirement.split(".")
            assert len(parts) >= 2
            assert parts[0].isdigit()
            assert parts[1].isdigit()

            # Should have PCI version
            assert "pci_version" in rule.metadata
            assert rule.metadata["pci_version"] == "3.2.1"

    def test_aws_pci_dss_pack_severity_levels(self) -> None:
        """Test that AWS PCI-DSS pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        severities = [rule.severity for rule in pack.rules]

        # Should have mostly error rules (PCI-DSS is strict)
        assert Severity.ERROR in severities

        # Most rules should be error (PCI-DSS compliance is mandatory)
        error_count = sum(1 for s in severities if s == Severity.ERROR)
        assert error_count >= len(pack.rules) * 0.8  # At least 80% error

    def test_aws_pci_dss_pack_filter_by_network_segmentation(self) -> None:
        """Test filtering AWS PCI-DSS pack by network segmentation rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        network_rules = [
            rule for rule in pack.rules if "network-segmentation" in rule.metadata.get("tags", [])
        ]

        # Should have 8-10 network segmentation rules
        assert 8 <= len(network_rules) <= 10

        # Verify resource types are appropriate for network segmentation
        resource_types = {rule.resource_type for rule in network_rules}
        expected_types = {
            "aws_security_group",
            "aws_network_acl",
            "aws_lb",
            "aws_db_instance",
            "aws_instance",
            "aws_elasticache_replication_group",
            "aws_redshift_cluster",
        }
        assert expected_types.issubset(resource_types)

    def test_aws_pci_dss_pack_filter_by_encryption(self) -> None:
        """Test filtering AWS PCI-DSS pack by encryption rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        encryption_rules = [
            rule for rule in pack.rules if "encryption" in rule.metadata.get("tags", [])
        ]

        # Should have 6-9 encryption rules
        assert 6 <= len(encryption_rules) <= 9

        # Verify resource types are appropriate for encryption
        resource_types = {rule.resource_type for rule in encryption_rules}
        expected_types = {
            "aws_s3_bucket",
            "aws_db_instance",
            "aws_ebs_volume",
            "aws_kms_key",
            "aws_elasticache_replication_group",
            "aws_dynamodb_table",
        }
        assert expected_types.issubset(resource_types)

    def test_aws_pci_dss_pack_filter_by_access_control(self) -> None:
        """Test filtering AWS PCI-DSS pack by access control rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        access_control_rules = [
            rule for rule in pack.rules if "access-control" in rule.metadata.get("tags", [])
        ]

        # Should have 6-8 access control rules
        assert 6 <= len(access_control_rules) <= 8

        # Verify resource types are appropriate for access control
        resource_types = {rule.resource_type for rule in access_control_rules}
        expected_types = {
            "aws_iam_user",
            "aws_s3_bucket_public_access_block",
            "aws_iam_account_password_policy",
            "aws_iam_access_key",
            "aws_lambda_function",
            "aws_instance",
        }
        assert expected_types.issubset(resource_types)

    def test_aws_pci_dss_pack_filter_by_logging(self) -> None:
        """Test filtering AWS PCI-DSS pack by logging and monitoring rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        logging_rules = [
            rule
            for rule in pack.rules
            if any(tag in rule.metadata.get("tags", []) for tag in ["audit-logging", "monitoring"])
        ]

        # Should have 5-10 logging and monitoring rules
        assert 5 <= len(logging_rules) <= 10

        # Verify resource types are appropriate for logging
        resource_types = {rule.resource_type for rule in logging_rules}
        expected_types = {
            "aws_cloudtrail",
            "aws_cloudwatch_log_group",
            "aws_s3_bucket_logging",
            "aws_lb",
            "aws_guardduty_detector",
            "aws_config_configuration_recorder",
        }
        assert expected_types.issubset(resource_types)

    def test_aws_pci_dss_pack_filter_by_vulnerability_management(self) -> None:
        """Test filtering AWS PCI-DSS pack by vulnerability management rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        vuln_mgmt_rules = [
            rule
            for rule in pack.rules
            if any(
                tag in rule.metadata.get("tags", [])
                for tag in [
                    "vulnerability-management",
                    "patch-management",
                    "vulnerability-scanning",
                ]
            )
        ]

        # Should have 2-6 vulnerability management rules
        assert 2 <= len(vuln_mgmt_rules) <= 6

        # Verify resource types are appropriate for vulnerability management
        resource_types = {rule.resource_type for rule in vuln_mgmt_rules}
        expected_types = {
            "aws_ssm_patch_baseline",
            "aws_inspector_assessment_target",
        }
        assert expected_types.issubset(resource_types)

    def test_aws_pci_dss_pack_pci_requirement_coverage(self) -> None:
        """Test that AWS PCI-DSS pack covers major PCI-DSS requirements."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        # Get all PCI requirements covered
        pci_requirements = set()
        for rule in pack.rules:
            if "pci_requirement" in rule.metadata:
                requirement = rule.metadata["pci_requirement"]
                # Get the main requirement number (e.g., "1" from "1.2.1")
                main_req = requirement.split(".")[0]
                pci_requirements.add(main_req)

        # Verify coverage of major PCI-DSS requirements
        expected_requirements = {"1", "3", "4", "6", "7", "8", "10", "11"}
        assert expected_requirements.issubset(pci_requirements)

    def test_aws_pci_dss_pack_cardholder_data_scope(self) -> None:
        """Test that rules properly identify cardholder data scope."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        # Find rules that specifically target cardholder data
        cardholder_rules = [
            rule for rule in pack.rules if "cardholder-data" in rule.metadata.get("tags", [])
        ]

        # Should have several rules specifically for cardholder data
        assert len(cardholder_rules) >= 3

        # These rules should use PCIScope filter
        for rule in cardholder_rules:
            if hasattr(rule, "filter") and rule.filter:
                # Should filter by PCIScope tag
                assert "tags.PCIScope" in rule.filter

    def test_aws_pci_dss_pack_merge_with_aws_security(self) -> None:
        """Test merging AWS PCI-DSS pack with AWS security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["aws-pci-dss", "aws-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 40  # More than just PCI-DSS rules

        # Should have both PCI-DSS and security rules
        rule_ids = {rule.id for rule in merged_pack.rules}
        assert any(rid.startswith("pci_") for rid in rule_ids)
        assert any(not rid.startswith("pci_") for rid in rule_ids)

        # Metadata should reflect merge
        assert "aws-pci-dss" in merged_pack.metadata.name
        assert "aws-security" in merged_pack.metadata.name

    def test_aws_pci_dss_pack_references_valid(self) -> None:
        """Test that all rules have valid reference URLs."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("aws-pci-dss")

        for rule in pack.rules:
            # Each rule should have references
            assert "references" in rule.metadata
            assert len(rule.metadata["references"]) > 0

            # Should include PCI Security Standards reference
            references = rule.metadata["references"]
            assert any("pcisecuritystandards.org" in ref.lower() for ref in references)

            # Should include AWS documentation reference
            assert any("docs.aws.amazon.com" in ref.lower() for ref in references)


class TestMultiCloudSecurityRulePack:
    """Integration tests for Multi-Cloud Security rule pack."""

    def test_multi_cloud_security_pack_loads(self) -> None:
        """Test that the Multi-Cloud Security rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        assert pack.metadata.name == "multi-cloud-security"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description == "Multi-Cloud Security Best Practices Rule Pack - "
            "Common security patterns across AWS, Azure, and GCP"
        )
        assert "multi-cloud" in pack.metadata.tags
        assert "security" in pack.metadata.tags
        assert "aws" in pack.metadata.tags
        assert "azure" in pack.metadata.tags
        assert "gcp" in pack.metadata.tags
        assert len(pack.rules) == 40

    def test_multi_cloud_security_pack_metadata(self) -> None:
        """Test Multi-Cloud Security rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_multi_cloud_security_pack_provider_coverage(self) -> None:
        """Test that Multi-Cloud Security pack covers all three providers."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Get all providers covered
        providers = set()
        for rule in pack.rules:
            if "providers" in rule.metadata:
                providers.update(rule.metadata["providers"])

        # Verify coverage of all three providers
        expected_providers = {"aws", "azure", "gcp"}
        assert expected_providers == providers

    def test_multi_cloud_security_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in Multi-Cloud Security pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_multi_cloud_security_pack_all_rules_have_provider(self) -> None:
        """Test that all rules have provider metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        for rule in pack.rules:
            # Each rule should have provider metadata
            assert "providers" in rule.metadata
            assert rule.metadata["providers"] is not None
            assert len(rule.metadata["providers"]) > 0

            # Provider should be one of the expected values
            providers = rule.metadata["providers"]
            for provider in providers:
                assert provider in ["aws", "azure", "gcp"]

    def test_multi_cloud_security_pack_severity_levels(self) -> None:
        """Test that Multi-Cloud Security pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities
        assert Severity.INFO in severities

        # Most rules should be error or warning (security is important)
        error_warning_count = sum(1 for s in severities if s in [Severity.ERROR, Severity.WARNING])
        assert error_warning_count >= len(pack.rules) * 0.8  # At least 80%

    def test_multi_cloud_security_pack_filter_by_aws(self) -> None:
        """Test filtering Multi-Cloud Security pack by AWS resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        aws_rules = [rule for rule in pack.rules if "aws" in rule.metadata.get("providers", [])]

        # Should have AWS rules
        assert len(aws_rules) >= 10

        # All rules should be AWS-related
        for rule in aws_rules:
            assert rule.resource_type.startswith("aws_")

    def test_multi_cloud_security_pack_filter_by_azure(self) -> None:
        """Test filtering Multi-Cloud Security pack by Azure resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        azure_rules = [rule for rule in pack.rules if "azure" in rule.metadata.get("providers", [])]

        # Should have Azure rules
        assert len(azure_rules) >= 10

        # All rules should be Azure-related
        for rule in azure_rules:
            assert rule.resource_type.startswith("azurerm_")

    def test_multi_cloud_security_pack_filter_by_gcp(self) -> None:
        """Test filtering Multi-Cloud Security pack by GCP resources."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        gcp_rules = [rule for rule in pack.rules if "gcp" in rule.metadata.get("providers", [])]

        # Should have GCP rules
        assert len(gcp_rules) >= 10

        # All rules should be GCP-related
        for rule in gcp_rules:
            assert rule.resource_type.startswith("google_")

    def test_multi_cloud_security_pack_encryption_category(self) -> None:
        """Test filtering Multi-Cloud Security pack by encryption rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        encryption_rules = [
            rule for rule in pack.rules if "encryption" in rule.metadata.get("tags", [])
        ]

        # Should have encryption rules for all providers
        assert len(encryption_rules) >= 12

        # Should cover all three providers
        providers = set()
        for rule in encryption_rules:
            providers.update(rule.metadata.get("providers", []))
        assert {"aws", "azure", "gcp"}.issubset(providers)

    def test_multi_cloud_security_pack_network_security_category(self) -> None:
        """Test filtering Multi-Cloud Security pack by network security rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        network_rules = [
            rule for rule in pack.rules if "network-security" in rule.metadata.get("tags", [])
        ]

        # Should have network security rules for all providers
        assert len(network_rules) >= 9

        # Should cover all three providers
        providers = set()
        for rule in network_rules:
            providers.update(rule.metadata.get("providers", []))
        assert {"aws", "azure", "gcp"}.issubset(providers)

    def test_multi_cloud_security_pack_iam_category(self) -> None:
        """Test filtering Multi-Cloud Security pack by IAM rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        iam_rules = [rule for rule in pack.rules if "iam" in rule.metadata.get("tags", [])]

        # Should have IAM rules for all providers
        assert len(iam_rules) >= 6

        # Should cover all three providers
        providers = set()
        for rule in iam_rules:
            providers.update(rule.metadata.get("providers", []))
        assert {"aws", "azure", "gcp"}.issubset(providers)

    def test_multi_cloud_security_pack_logging_category(self) -> None:
        """Test filtering Multi-Cloud Security pack by logging rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        logging_rules = [rule for rule in pack.rules if "logging" in rule.metadata.get("tags", [])]

        # Should have logging rules for all providers
        assert len(logging_rules) >= 6

        # Should cover all three providers
        providers = set()
        for rule in logging_rules:
            providers.update(rule.metadata.get("providers", []))
        assert {"aws", "azure", "gcp"}.issubset(providers)

    def test_multi_cloud_security_pack_monitoring_category(self) -> None:
        """Test filtering Multi-Cloud Security pack by monitoring rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        monitoring_rules = [
            rule for rule in pack.rules if "monitoring" in rule.metadata.get("tags", [])
        ]

        # Should have monitoring rules for all providers
        assert len(monitoring_rules) >= 3

        # Should cover all three providers
        providers = set()
        for rule in monitoring_rules:
            providers.update(rule.metadata.get("providers", []))
        assert {"aws", "azure", "gcp"}.issubset(providers)

    def test_multi_cloud_security_pack_governance_category(self) -> None:
        """Test filtering Multi-Cloud Security pack by governance rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        governance_rules = [
            rule for rule in pack.rules if "governance" in rule.metadata.get("tags", [])
        ]

        # Should have governance rules for all providers
        assert len(governance_rules) >= 3

        # Should cover all three providers
        providers = set()
        for rule in governance_rules:
            providers.update(rule.metadata.get("providers", []))
        assert {"aws", "azure", "gcp"}.issubset(providers)

    def test_multi_cloud_security_pack_merge_with_provider_packs(self) -> None:
        """Test merging Multi-Cloud Security pack with provider-specific packs."""
        manager = RulePackManager()

        # Test merging with AWS security pack
        aws_merged = manager.merge_rule_packs(["multi-cloud-security", "aws-security"])
        assert len(aws_merged.rules) > 42  # More than just multi-cloud rules

        # Test merging with Azure security pack
        azure_merged = manager.merge_rule_packs(["multi-cloud-security", "azure-security"])
        assert len(azure_merged.rules) > 42  # More than just multi-cloud rules

        # Test merging with GCP security pack
        gcp_merged = manager.merge_rule_packs(["multi-cloud-security", "gcp-security"])
        assert len(gcp_merged.rules) > 42  # More than just multi-cloud rules

    def test_multi_cloud_security_pack_all_rules_have_metadata(self) -> None:
        """Test that all rules have proper metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        for rule in pack.rules:
            # Each rule should have an ID and description
            assert rule.id is not None
            assert rule.description is not None
            assert len(rule.description) > 10

            # Each rule should have metadata with tags, providers, and references
            assert hasattr(rule, "metadata")
            assert "tags" in rule.metadata
            assert "providers" in rule.metadata
            assert "references" in rule.metadata
            assert len(rule.metadata["tags"]) > 0
            assert len(rule.metadata["providers"]) > 0
            assert len(rule.metadata["references"]) > 0

            # Description should indicate multi-cloud nature
            assert "Multi-Cloud" in rule.description

    def test_multi_cloud_security_pack_references_valid(self) -> None:
        """Test that all rules have valid reference URLs."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        for rule in pack.rules:
            # Each rule should have references
            assert "references" in rule.metadata
            assert len(rule.metadata["references"]) > 0

            # References should be valid URLs
            references = rule.metadata["references"]
            for ref in references:
                assert ref.startswith("https://")
                # Should reference appropriate provider documentation
                providers = rule.metadata.get("providers", [])
                if "aws" in providers:
                    assert any("docs.aws.amazon.com" in ref.lower() for ref in references)
                elif "azure" in providers:
                    assert any("docs.microsoft.com" in ref.lower() for ref in references)
                elif "gcp" in providers:
                    assert any("cloud.google.com" in ref.lower() for ref in references)


class TestMultiCloudSecurityIntegration:
    """Integration tests for Multi-Cloud Security rule pack against test fixtures."""

    def test_multi_cloud_security_pack_against_fixtures(self, fixtures_dir: Path) -> None:
        """Test Multi-Cloud Security pack against multi-cloud test fixtures."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Validate resources with rules
        results = validate_resources(pack.rules, resources)

        # Should have both passing and failing results
        assert len(results) > 0

        # Check that we have results for all three providers
        aws_results = [r for r in results if r.resource["resource_type"].startswith("aws_")]
        azure_results = [r for r in results if r.resource["resource_type"].startswith("azurerm_")]
        gcp_results = [r for r in results if r.resource["resource_type"].startswith("google_")]

        assert len(aws_results) > 0
        assert len(azure_results) > 0
        assert len(gcp_results) > 0

    def test_multi_cloud_aws_encryption_rules(self, fixtures_dir: Path) -> None:
        """Test AWS encryption rules in multi-cloud pack."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to AWS encryption rules
        aws_encryption_rules = [
            rule
            for rule in pack.rules
            if "aws" in rule.metadata.get("providers", [])
            and "encryption" in rule.metadata.get("tags", [])
        ]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to AWS resources
        aws_resources = [r for r in resources if r["resource_type"].startswith("aws_")]

        # Validate AWS resources with AWS encryption rules
        results = validate_resources(aws_encryption_rules, aws_resources)

        # Should have results for AWS encryption
        assert len(results) > 0

        # Should have both passes and failures
        passes = [r for r in results if r.passed]
        failures = [r for r in results if not r.passed]

        assert len(passes) > 0
        assert len(failures) > 0

    def test_multi_cloud_azure_encryption_rules(self, fixtures_dir: Path) -> None:
        """Test Azure encryption rules in multi-cloud pack."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to Azure encryption rules
        azure_encryption_rules = [
            rule
            for rule in pack.rules
            if "azure" in rule.metadata.get("providers", [])
            and "encryption" in rule.metadata.get("tags", [])
        ]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to Azure resources
        azure_resources = [r for r in resources if r["resource_type"].startswith("azurerm_")]

        # Validate Azure resources with Azure encryption rules
        results = validate_resources(azure_encryption_rules, azure_resources)

        # Should have results for Azure encryption
        assert len(results) > 0

        # Should have both passes and failures
        passes = [r for r in results if r.passed]
        failures = [r for r in results if not r.passed]

        assert len(passes) > 0
        assert len(failures) > 0

    def test_multi_cloud_gcp_encryption_rules(self, fixtures_dir: Path) -> None:
        """Test GCP encryption rules in multi-cloud pack."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to GCP encryption rules
        gcp_encryption_rules = [
            rule
            for rule in pack.rules
            if "gcp" in rule.metadata.get("providers", [])
            and "encryption" in rule.metadata.get("tags", [])
        ]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to GCP resources
        gcp_resources = [r for r in resources if r["resource_type"].startswith("google_")]

        # Validate GCP resources with GCP encryption rules
        results = validate_resources(gcp_encryption_rules, gcp_resources)

        # Should have results for GCP encryption
        assert len(results) > 0

        # Should have both passes and failures
        passes = [r for r in results if r.passed]
        failures = [r for r in results if not r.passed]

        assert len(passes) > 0
        assert len(failures) > 0

    def test_multi_cloud_network_security_rules(self, fixtures_dir: Path) -> None:
        """Test network security rules across all providers."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to network security rules
        network_rules = [
            rule for rule in pack.rules if "network-security" in rule.metadata.get("tags", [])
        ]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Validate resources with network security rules
        results = validate_resources(network_rules, resources)

        # Should have results for network security
        assert len(results) > 0

        # Should have results for all three providers
        aws_results = [r for r in results if r.resource["resource_type"].startswith("aws_")]
        azure_results = [r for r in results if r.resource["resource_type"].startswith("azurerm_")]
        gcp_results = [r for r in results if r.resource["resource_type"].startswith("google_")]

        assert len(aws_results) > 0
        assert len(azure_results) > 0
        assert len(gcp_results) > 0

    def test_multi_cloud_iam_rules(self, fixtures_dir: Path) -> None:
        """Test IAM rules across all providers."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to IAM rules
        iam_rules = [rule for rule in pack.rules if "iam" in rule.metadata.get("tags", [])]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Validate resources with IAM rules
        results = validate_resources(iam_rules, resources)

        # Should have results for IAM
        assert len(results) > 0

    def test_multi_cloud_logging_rules(self, fixtures_dir: Path) -> None:
        """Test logging rules across all providers."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to logging rules
        logging_rules = [rule for rule in pack.rules if "logging" in rule.metadata.get("tags", [])]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Validate resources with logging rules
        results = validate_resources(logging_rules, resources)

        # Should have results for logging
        assert len(results) > 0

    def test_multi_cloud_governance_rules(self, fixtures_dir: Path) -> None:
        """Test governance rules across all providers."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Filter to governance rules
        governance_rules = [
            rule for rule in pack.rules if "governance" in rule.metadata.get("tags", [])
        ]

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Validate resources with governance rules
        results = validate_resources(governance_rules, resources)

        # Should have results for governance
        assert len(results) > 0

        # Should have results for all three providers
        aws_results = [r for r in results if r.resource["resource_type"].startswith("aws_")]
        azure_results = [r for r in results if r.resource["resource_type"].startswith("azurerm_")]
        gcp_results = [r for r in results if r.resource["resource_type"].startswith("google_")]

        assert len(aws_results) > 0
        assert len(azure_results) > 0
        assert len(gcp_results) > 0

    def test_multi_cloud_mixed_provider_scanning(self, fixtures_dir: Path) -> None:
        """Test scanning mixed provider resources with multi-cloud pack."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("multi-cloud-security")

        # Parse the multi-cloud test fixture
        fixture_file = fixtures_dir / "terraform" / "multi_cloud_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Validate all resources with all rules
        results = validate_resources(pack.rules, resources)

        # Should have results
        assert len(results) > 0

        # Group results by provider
        aws_results = [r for r in results if r.resource["resource_type"].startswith("aws_")]
        azure_results = [r for r in results if r.resource["resource_type"].startswith("azurerm_")]
        gcp_results = [r for r in results if r.resource["resource_type"].startswith("google_")]

        # Should have results for all providers
        assert len(aws_results) > 0
        assert len(azure_results) > 0
        assert len(gcp_results) > 0

        # Should have both passes and failures for each provider
        for provider_results in [aws_results, azure_results, gcp_results]:
            passes = [r for r in provider_results if r.passed]
            failures = [r for r in provider_results if not r.passed]

            # Each provider should have at least some results
            assert len(provider_results) > 0
            # Should have both passes and failures (based on our test fixtures)
            assert len(passes) > 0 or len(failures) > 0


class TestKubernetesSecurityRulePack:
    """Integration tests for Kubernetes Security rule pack."""

    def test_kubernetes_security_pack_loads(self) -> None:
        """Test that the Kubernetes security rule pack loads successfully."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        assert pack.metadata.name == "kubernetes-security"
        assert pack.metadata.version == "1.0.0"
        assert (
            pack.metadata.description
            == "Kubernetes Security Best Practices Rule Pack for EKS, AKS, and GKE"
        )
        assert "kubernetes" in pack.metadata.tags
        assert "security" in pack.metadata.tags
        assert "containers" in pack.metadata.tags
        assert "eks" in pack.metadata.tags
        assert "aks" in pack.metadata.tags
        assert "gke" in pack.metadata.tags
        assert len(pack.rules) == 40

    def test_kubernetes_security_pack_metadata(self) -> None:
        """Test Kubernetes security rule pack metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Verify metadata fields
        assert pack.metadata.author == "Riveter Team"
        assert pack.metadata.min_riveter_version == "0.1.0"
        assert pack.metadata.dependencies == []

    def test_kubernetes_security_pack_rule_categories(self) -> None:
        """Test that Kubernetes security pack covers all expected categories."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Get all resource types covered
        resource_types = set()
        for rule in pack.rules:
            # Handle multi-resource type rules (separated by |)
            types = rule.resource_type.split("|")
            resource_types.update(types)

        # Verify coverage of major Kubernetes resource types
        expected_types = {
            "kubernetes_pod",
            "kubernetes_deployment",
            "kubernetes_daemonset",
            "kubernetes_stateful_set",
            "kubernetes_role",
            "kubernetes_cluster_role",
            "kubernetes_role_binding",
            "kubernetes_cluster_role_binding",
            "kubernetes_service_account",
            "kubernetes_network_policy",
            "kubernetes_service",
            "kubernetes_ingress",
            "kubernetes_secret",
        }

        assert expected_types.issubset(resource_types)

    def test_kubernetes_security_pack_rule_ids_unique(self) -> None:
        """Test that all rule IDs in Kubernetes security pack are unique."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        rule_ids = [rule.id for rule in pack.rules]
        assert len(rule_ids) == len(set(rule_ids))

    def test_kubernetes_security_pack_all_rules_have_metadata(self) -> None:
        """Test that all rules have proper metadata."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        for rule in pack.rules:
            # Each rule should have an ID and description
            assert rule.id is not None
            assert rule.description is not None
            assert len(rule.description) > 10

            # Each rule should have metadata with tags, providers, and references
            assert hasattr(rule, "metadata")
            assert "tags" in rule.metadata
            assert "providers" in rule.metadata
            assert "references" in rule.metadata
            assert len(rule.metadata["tags"]) > 0
            assert len(rule.metadata["providers"]) > 0
            assert len(rule.metadata["references"]) > 0

            # All rules should support EKS, AKS, and GKE
            providers = rule.metadata["providers"]
            assert "eks" in providers
            assert "aks" in providers
            assert "gke" in providers

    def test_kubernetes_security_pack_severity_levels(self) -> None:
        """Test that Kubernetes security pack has appropriate severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        severities = [rule.severity for rule in pack.rules]

        # Should have a mix of error, warning, and info rules
        assert Severity.ERROR in severities
        assert Severity.WARNING in severities
        assert Severity.INFO in severities

        # Most rules should be error or warning (security is important)
        error_warning_count = sum(1 for s in severities if s in [Severity.ERROR, Severity.WARNING])
        assert error_warning_count >= len(pack.rules) * 0.7  # At least 70%

    def test_kubernetes_security_pack_pod_security_rules(self) -> None:
        """Test filtering Kubernetes security pack by pod security rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        pod_security_rules = [
            rule for rule in pack.rules if "pod-security" in rule.metadata.get("tags", [])
        ]

        # Should have 8-10 pod security rules
        assert 8 <= len(pod_security_rules) <= 10

        # All pod security rules should apply to pod-like resources
        for rule in pod_security_rules:
            resource_types = rule.resource_type.split("|")
            pod_like_types = [
                "kubernetes_pod",
                "kubernetes_deployment",
                "kubernetes_daemonset",
                "kubernetes_stateful_set",
            ]
            assert any(rt in pod_like_types for rt in resource_types)

    def test_kubernetes_security_pack_rbac_rules(self) -> None:
        """Test filtering Kubernetes security pack by RBAC rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        rbac_rules = [rule for rule in pack.rules if "rbac" in rule.metadata.get("tags", [])]

        # Should have 6-8 RBAC rules
        assert 6 <= len(rbac_rules) <= 8

        # All RBAC rules should apply to RBAC resources
        for rule in rbac_rules:
            resource_types = rule.resource_type.split("|")
            rbac_types = [
                "kubernetes_role",
                "kubernetes_cluster_role",
                "kubernetes_role_binding",
                "kubernetes_cluster_role_binding",
                "kubernetes_service_account",
            ]
            assert any(rt in rbac_types for rt in resource_types)

    def test_kubernetes_security_pack_network_policy_rules(self) -> None:
        """Test filtering Kubernetes security pack by network policy rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        network_rules = [
            rule for rule in pack.rules if "network-policy" in rule.metadata.get("tags", [])
        ]

        # Should have 6-8 network policy rules
        assert 6 <= len(network_rules) <= 8

        # Network policy rules should apply to network resources
        for rule in network_rules:
            resource_types = rule.resource_type.split("|")
            network_types = [
                "kubernetes_network_policy",
                "kubernetes_service",
                "kubernetes_ingress",
            ]
            assert any(rt in network_types for rt in resource_types)

    def test_kubernetes_security_pack_secrets_management_rules(self) -> None:
        """Test filtering Kubernetes security pack by secrets management rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        secrets_rules = [
            rule for rule in pack.rules if "secrets-management" in rule.metadata.get("tags", [])
        ]

        # Should have 5-7 secrets management rules
        assert 5 <= len(secrets_rules) <= 7

    def test_kubernetes_security_pack_image_security_rules(self) -> None:
        """Test filtering Kubernetes security pack by image security rules."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        image_rules = [
            rule for rule in pack.rules if "image-security" in rule.metadata.get("tags", [])
        ]

        # Should have 5-7 image security rules
        assert 5 <= len(image_rules) <= 7

        # Image security rules should apply to pod-like resources
        for rule in image_rules:
            resource_types = rule.resource_type.split("|")
            pod_like_types = [
                "kubernetes_pod",
                "kubernetes_deployment",
                "kubernetes_daemonset",
                "kubernetes_stateful_set",
            ]
            # Most image security rules apply to pods, but some may apply to admission controllers
            if not any("admission" in rt for rt in resource_types):
                assert any(rt in pod_like_types for rt in resource_types)

    def test_kubernetes_security_pack_filter_by_severity(self) -> None:
        """Test filtering Kubernetes security pack by severity levels."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Filter by error severity
        error_pack = pack.filter_by_severity(Severity.ERROR)
        error_count = len(error_pack.rules)

        # Filter by warning severity (includes error + warning)
        warning_pack = pack.filter_by_severity(Severity.WARNING)
        warning_count = len(warning_pack.rules)

        # Filter by info severity (includes all)
        info_pack = pack.filter_by_severity(Severity.INFO)
        info_count = len(info_pack.rules)

        # Should have hierarchical filtering
        assert error_count <= warning_count <= info_count
        assert info_count == len(pack.rules)

    def test_kubernetes_security_pack_merge_with_aws_security(self) -> None:
        """Test merging Kubernetes security pack with AWS security pack."""
        manager = RulePackManager()

        merged_pack = manager.merge_rule_packs(["kubernetes-security", "aws-security"])

        # Should have rules from both packs
        assert len(merged_pack.rules) > 39  # More than just Kubernetes rules

        # Should have both Kubernetes and AWS resource types
        resource_types = set()
        for rule in merged_pack.rules:
            types = rule.resource_type.split("|")
            resource_types.update(types)

        assert any(rt.startswith("kubernetes_") for rt in resource_types)
        assert any(rt.startswith("aws_") for rt in resource_types)

        # Metadata should reflect merge
        assert "kubernetes-security" in merged_pack.metadata.name
        assert "aws-security" in merged_pack.metadata.name

    def test_kubernetes_security_pack_integration_with_fixtures(self, fixtures_dir: Path) -> None:
        """Test Kubernetes security pack against test fixtures."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Parse the Kubernetes test fixture
        fixture_file = fixtures_dir / "terraform" / "kubernetes_security_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to Kubernetes resources only
        k8s_resources = [r for r in resources if r["resource_type"].startswith("kubernetes_")]

        # Should have Kubernetes resources in the fixture
        assert len(k8s_resources) > 0

        # Validate resources with Kubernetes security rules
        results = validate_resources(pack.rules, k8s_resources)

        # Should have validation results
        assert len(results) > 0

        # Should have both passes and failures
        passes = [r for r in results if r.passed]
        failures = [r for r in results if not r.passed]

        assert len(passes) > 0
        assert len(failures) > 0

    def test_kubernetes_security_pack_pod_security_integration(self, fixtures_dir: Path) -> None:
        """Test pod security rules against fixtures."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Filter to pod security rules
        pod_security_rules = [
            rule for rule in pack.rules if "pod-security" in rule.metadata.get("tags", [])
        ]

        # Parse the Kubernetes test fixture
        fixture_file = fixtures_dir / "terraform" / "kubernetes_security_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to pod-like resources
        pod_resources = [
            r
            for r in resources
            if r["resource_type"]
            in [
                "kubernetes_pod",
                "kubernetes_deployment",
                "kubernetes_daemonset",
                "kubernetes_stateful_set",
            ]
        ]

        # Should have pod resources in the fixture
        assert len(pod_resources) > 0

        # Validate pod resources with pod security rules
        results = validate_resources(pod_security_rules, pod_resources)

        # Should have validation results
        assert len(results) > 0

        # Should detect security violations in test fixtures
        failures = [r for r in results if not r.passed]
        assert len(failures) > 0

        # Check for specific security violations
        failure_rule_ids = {r.rule.id for r in failures}

        # Should catch privileged containers
        assert "k8s_no_privileged_containers" in failure_rule_ids
        # Should catch root users
        assert "k8s_no_root_user" in failure_rule_ids

    def test_kubernetes_security_pack_rbac_integration(self, fixtures_dir: Path) -> None:
        """Test RBAC rules against fixtures."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Filter to RBAC rules
        rbac_rules = [rule for rule in pack.rules if "rbac" in rule.metadata.get("tags", [])]

        # Parse the Kubernetes test fixture
        fixture_file = fixtures_dir / "terraform" / "kubernetes_security_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to RBAC resources
        rbac_resources = [
            r
            for r in resources
            if r["resource_type"]
            in [
                "kubernetes_role",
                "kubernetes_cluster_role",
                "kubernetes_role_binding",
                "kubernetes_cluster_role_binding",
                "kubernetes_service_account",
            ]
        ]

        # Should have RBAC resources in the fixture
        assert len(rbac_resources) > 0

        # Validate RBAC resources with RBAC rules
        results = validate_resources(rbac_rules, rbac_resources)

        # Should have validation results
        assert len(results) > 0

        # Should detect RBAC violations in test fixtures
        failures = [r for r in results if not r.passed]
        assert len(failures) > 0

        # Check for specific RBAC violations
        failure_rule_ids = {r.rule.id for r in failures}

        # Should catch wildcard permissions
        assert (
            "k8s_rbac_no_wildcard_verbs" in failure_rule_ids
            or "k8s_rbac_no_wildcard_resources" in failure_rule_ids
        )

    def test_kubernetes_security_pack_network_policy_integration(self, fixtures_dir: Path) -> None:
        """Test network policy rules against fixtures."""
        from riveter.extract_config import extract_terraform_config
        from riveter.scanner import validate_resources

        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # Filter to network policy rules
        network_rules = [
            rule for rule in pack.rules if "network-policy" in rule.metadata.get("tags", [])
        ]

        # Parse the Kubernetes test fixture
        fixture_file = fixtures_dir / "terraform" / "kubernetes_security_test.tf"
        config = extract_terraform_config(str(fixture_file))
        resources = config["resources"]

        # Filter to network resources
        network_resources = [
            r
            for r in resources
            if r["resource_type"]
            in ["kubernetes_network_policy", "kubernetes_service", "kubernetes_ingress"]
        ]

        # Should have network resources in the fixture
        assert len(network_resources) > 0

        # Validate network resources with network rules
        results = validate_resources(network_rules, network_resources)

        # Should have validation results
        assert len(results) > 0

    def test_kubernetes_security_pack_cross_provider_compatibility(self) -> None:
        """Test that Kubernetes security rules work across EKS, AKS, and GKE."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        # All rules should support all three providers
        for rule in pack.rules:
            providers = rule.metadata.get("providers", [])
            assert "eks" in providers, f"Rule {rule.id} missing EKS support"
            assert "aks" in providers, f"Rule {rule.id} missing AKS support"
            assert "gke" in providers, f"Rule {rule.id} missing GKE support"

        # Rules should be provider-agnostic (focus on Kubernetes resources)
        kubernetes_resource_rules = [
            rule for rule in pack.rules if rule.resource_type.startswith("kubernetes_")
        ]

        # Most rules should be provider-agnostic Kubernetes resources
        assert len(kubernetes_resource_rules) >= len(pack.rules) * 0.8  # At least 80%

    def test_kubernetes_security_pack_rule_id_conventions(self) -> None:
        """Test that rule IDs follow consistent naming conventions."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        for rule in pack.rules:
            # All rule IDs should start with k8s_
            assert rule.id.startswith("k8s_"), f"Rule ID {rule.id} doesn't follow k8s_ convention"

            # Rule IDs should be lowercase with underscores
            assert rule.id.islower(), f"Rule ID {rule.id} should be lowercase"
            assert " " not in rule.id, f"Rule ID {rule.id} should not contain spaces"

    def test_kubernetes_security_pack_description_quality(self) -> None:
        """Test that rule descriptions are clear and actionable."""
        manager = RulePackManager()
        pack = manager.load_rule_pack("kubernetes-security")

        for rule in pack.rules:
            description = rule.description

            # Descriptions should be meaningful
            assert len(description) >= 20, f"Rule {rule.id} description too short"
            assert len(description) <= 200, f"Rule {rule.id} description too long"

            # Descriptions should not end with period (consistent style)
            assert not description.endswith(
                "."
            ), f"Rule {rule.id} description should not end with period"

            # Descriptions should be actionable (contain "should" or other action words)
            actionable_words = ["should", "must", "avoid", "ensure", "require", "use", "consider"]
            assert any(
                word in description.lower() for word in actionable_words
            ), f"Rule {rule.id} description should be actionable"
