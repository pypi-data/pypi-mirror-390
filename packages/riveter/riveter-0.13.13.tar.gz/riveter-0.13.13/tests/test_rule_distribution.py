"""Tests for rule distribution and packaging system."""

import json
import tempfile
import zipfile
from pathlib import Path

import pytest

from riveter.rule_distribution import (
    RulePackageBuilder,
    RulePackageManifest,
    RulePackageRegistry,
    RulePackageValidator,
)
from riveter.rule_packs import RulePack, RulePackMetadata
from riveter.rules import Rule


@pytest.fixture
def sample_rule_pack():
    """Create a sample rule pack for testing."""
    metadata = RulePackMetadata(
        name="test-pack",
        version="1.0.0",
        description="Test rule pack",
        author="Test Author",
        created="2024-01-01",
        updated="2024-01-01",
        dependencies=[],
        tags=["test"],
        min_riveter_version="0.1.0",
    )

    rule_data = {
        "id": "test_rule",
        "resource_type": "aws_instance",
        "description": "Test rule",
        "severity": "error",
        "filter": {"tags.Environment": "production"},
        "assert": {"instance_type": {"eq": "t3.micro"}},
        "metadata": {"tags": ["test"]},
    }

    rule = Rule(rule_data)
    return RulePack(metadata=metadata, rules=[rule])


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestRulePackageManifest:
    """Test RulePackageManifest functionality."""

    def test_from_rule_pack_metadata(self, sample_rule_pack):
        """Test creating manifest from rule pack metadata."""
        manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)

        assert manifest.name == "test-pack"
        assert manifest.version == "1.0.0"
        assert manifest.description == "Test rule pack"
        assert manifest.author == "Test Author"
        assert manifest.package_format == "zip"
        assert manifest.file_list == []

    def test_to_dict(self, sample_rule_pack):
        """Test converting manifest to dictionary."""
        manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
        manifest.checksum = "abc123"
        manifest.size_bytes = 1024

        data = manifest.to_dict()

        assert data["name"] == "test-pack"
        assert data["version"] == "1.0.0"
        assert data["checksum"] == "abc123"
        assert data["size_bytes"] == 1024

    def test_from_dict(self):
        """Test creating manifest from dictionary."""
        data = {
            "name": "test-pack",
            "version": "1.0.0",
            "description": "Test pack",
            "author": "Test Author",
            "created": "2024-01-01",
            "updated": "2024-01-01",
            "dependencies": [],
            "tags": ["test"],
            "min_riveter_version": "0.1.0",
            "package_format": "zip",
            "checksum": "abc123",
            "signature": "",
            "file_list": ["rules.yml"],
            "size_bytes": 1024,
        }

        manifest = RulePackageManifest.from_dict(data)

        assert manifest.name == "test-pack"
        assert manifest.checksum == "abc123"
        assert manifest.file_list == ["rules.yml"]


class TestRulePackageBuilder:
    """Test RulePackageBuilder functionality."""

    def test_create_package_zip(self, sample_rule_pack, temp_directory):
        """Test creating a ZIP package."""
        builder = RulePackageBuilder()
        output_path = temp_directory / "test-pack.zip"

        result_path = builder.create_package(
            sample_rule_pack,
            str(output_path),
            package_format="zip",
            include_signature=False,
        )

        assert result_path == str(output_path)
        assert output_path.exists()

        # Verify package contents
        with zipfile.ZipFile(output_path, "r") as zipf:
            files = zipf.namelist()
            assert "rules.yml" in files
            assert "README.md" in files
            assert "manifest.json" in files

    def test_create_package_tar_gz(self, sample_rule_pack, temp_directory):
        """Test creating a TAR.GZ package."""
        builder = RulePackageBuilder()
        output_path = temp_directory / "test-pack.tar.gz"

        result_path = builder.create_package(
            sample_rule_pack,
            str(output_path),
            package_format="tar.gz",
            include_signature=False,
        )

        assert result_path == str(output_path)
        assert output_path.exists()

    def test_create_package_with_signature(self, sample_rule_pack, temp_directory):
        """Test creating a package with signature."""
        # Generate test key pair
        private_key, public_key = RulePackageBuilder.generate_key_pair()

        builder = RulePackageBuilder(private_key=private_key)
        output_path = temp_directory / "test-pack.zip"

        result_path = builder.create_package(
            sample_rule_pack,
            str(output_path),
            include_signature=True,
        )

        assert result_path == str(output_path)
        assert output_path.exists()

        # Verify signature is included
        with zipfile.ZipFile(output_path, "r") as zipf:
            manifest_data = zipf.read("manifest.json")
            manifest = json.loads(manifest_data)
            assert manifest["signature"] != ""

    def test_unsupported_package_format(self, sample_rule_pack, temp_directory):
        """Test error handling for unsupported package format."""
        builder = RulePackageBuilder()
        output_path = temp_directory / "test-pack.rar"

        with pytest.raises(Exception) as exc_info:
            builder.create_package(
                sample_rule_pack,
                str(output_path),
                package_format="rar",
            )

        assert "Unsupported package format" in str(exc_info.value)

    def test_signature_without_private_key(self, sample_rule_pack, temp_directory):
        """Test error when signature requested without private key."""
        builder = RulePackageBuilder()
        output_path = temp_directory / "test-pack.zip"

        with pytest.raises(Exception) as exc_info:
            builder.create_package(
                sample_rule_pack,
                str(output_path),
                include_signature=True,
            )

        assert "Private key required" in str(exc_info.value)

    def test_key_pair_generation(self):
        """Test RSA key pair generation."""
        private_key, public_key = RulePackageBuilder.generate_key_pair()

        assert private_key is not None
        assert public_key is not None
        assert private_key.key_size == 2048

    def test_key_serialization(self, temp_directory):
        """Test key serialization and loading."""
        private_key, public_key = RulePackageBuilder.generate_key_pair()

        private_key_path = temp_directory / "private.pem"
        public_key_path = temp_directory / "public.pem"

        # Save keys
        RulePackageBuilder.save_private_key(private_key, str(private_key_path))
        RulePackageBuilder.save_public_key(public_key, str(public_key_path))

        assert private_key_path.exists()
        assert public_key_path.exists()

        # Load keys
        loaded_private = RulePackageBuilder.load_private_key(str(private_key_path))
        loaded_public = RulePackageBuilder.load_public_key(str(public_key_path))

        assert loaded_private.key_size == private_key.key_size
        assert loaded_public.key_size == public_key.key_size


class TestRulePackageValidator:
    """Test RulePackageValidator functionality."""

    def test_validate_valid_package(self, sample_rule_pack, temp_directory):
        """Test validating a valid package."""
        # Create package
        builder = RulePackageBuilder()
        package_path = temp_directory / "test-pack.zip"
        builder.create_package(sample_rule_pack, str(package_path), include_signature=False)

        # Validate package
        validator = RulePackageValidator()
        result = validator.validate_package(str(package_path), verify_signature=False)

        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["manifest"] is not None
        assert result["rule_pack"] is not None

    def test_validate_nonexistent_package(self, temp_directory):
        """Test validating a nonexistent package."""
        validator = RulePackageValidator()
        package_path = temp_directory / "nonexistent.zip"

        result = validator.validate_package(str(package_path))

        assert result["valid"] is False
        assert "does not exist" in result["errors"][0]

    def test_validate_invalid_format(self, temp_directory):
        """Test validating a package with invalid format."""
        # Create a file with wrong extension
        invalid_path = temp_directory / "test.txt"
        invalid_path.write_text("not a package")

        validator = RulePackageValidator()
        result = validator.validate_package(str(invalid_path))

        assert result["valid"] is False
        assert "Unsupported package format" in result["errors"][0]

    def test_validate_package_with_signature(self, sample_rule_pack, temp_directory):
        """Test validating a package with signature verification."""
        # Generate key pair
        private_key, public_key = RulePackageBuilder.generate_key_pair()

        # Create signed package
        builder = RulePackageBuilder(private_key=private_key)
        package_path = temp_directory / "test-pack.zip"
        builder.create_package(sample_rule_pack, str(package_path), include_signature=True)

        # Validate with correct public key
        validator = RulePackageValidator(public_key=public_key)
        result = validator.validate_package(str(package_path), verify_signature=True)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_package_invalid_signature(self, sample_rule_pack, temp_directory):
        """Test validating a package with invalid signature."""
        # Generate two different key pairs
        private_key1, _ = RulePackageBuilder.generate_key_pair()
        _, public_key2 = RulePackageBuilder.generate_key_pair()

        # Create package with first private key
        builder = RulePackageBuilder(private_key=private_key1)
        package_path = temp_directory / "test-pack.zip"
        builder.create_package(sample_rule_pack, str(package_path), include_signature=True)

        # Validate with different public key
        validator = RulePackageValidator(public_key=public_key2)
        result = validator.validate_package(str(package_path), verify_signature=True)

        assert result["valid"] is False
        assert "signature verification failed" in result["errors"][0].lower()


class TestRulePackageRegistry:
    """Test RulePackageRegistry functionality."""

    def test_register_package(self, sample_rule_pack, temp_directory):
        """Test registering a package in the registry."""
        registry = RulePackageRegistry(str(temp_directory))

        manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
        package_path = "/path/to/package.zip"

        registry.register_package(manifest, package_path)

        # Verify package is registered
        package_info = registry.get_package_info("test-pack", "1.0.0")
        assert package_info is not None
        assert package_info["manifest"]["name"] == "test-pack"
        assert package_info["package_path"] == package_path

    def test_get_package_info_latest(self, sample_rule_pack, temp_directory):
        """Test getting latest package version."""
        registry = RulePackageRegistry(str(temp_directory))

        # Register multiple versions
        for version in ["1.0.0", "1.1.0", "2.0.0"]:
            manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
            manifest.version = version
            registry.register_package(manifest, f"/path/to/package-{version}.zip")

        # Get latest version
        package_info = registry.get_package_info("test-pack", "latest")
        assert package_info is not None
        assert package_info["manifest"]["version"] == "2.0.0"

    def test_list_packages(self, sample_rule_pack, temp_directory):
        """Test listing all packages in registry."""
        registry = RulePackageRegistry(str(temp_directory))

        # Register packages
        manifest1 = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
        manifest1.name = "pack1"
        registry.register_package(manifest1, "/path/to/pack1.zip")

        manifest2 = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
        manifest2.name = "pack2"
        registry.register_package(manifest2, "/path/to/pack2.zip")

        packages = registry.list_packages()
        assert len(packages) == 2

        package_names = [p["name"] for p in packages]
        assert "pack1" in package_names
        assert "pack2" in package_names

    def test_list_package_versions(self, sample_rule_pack, temp_directory):
        """Test listing versions of a specific package."""
        registry = RulePackageRegistry(str(temp_directory))

        # Register multiple versions
        versions = ["1.0.0", "1.1.0", "2.0.0"]
        for version in versions:
            manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
            manifest.version = version
            registry.register_package(manifest, f"/path/to/package-{version}.zip")

        package_versions = registry.list_package_versions("test-pack")
        assert len(package_versions) == 3
        assert package_versions == ["2.0.0", "1.1.0", "1.0.0"]  # Sorted descending

    def test_remove_package_version(self, sample_rule_pack, temp_directory):
        """Test removing a specific package version."""
        registry = RulePackageRegistry(str(temp_directory))

        # Register multiple versions
        for version in ["1.0.0", "1.1.0"]:
            manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
            manifest.version = version
            registry.register_package(manifest, f"/path/to/package-{version}.zip")

        # Remove specific version
        result = registry.remove_package("test-pack", "1.0.0")
        assert result is True

        # Verify version is removed
        package_info = registry.get_package_info("test-pack", "1.0.0")
        assert package_info is None

        # Verify other version still exists
        package_info = registry.get_package_info("test-pack", "1.1.0")
        assert package_info is not None

    def test_remove_entire_package(self, sample_rule_pack, temp_directory):
        """Test removing an entire package."""
        registry = RulePackageRegistry(str(temp_directory))

        manifest = RulePackageManifest.from_rule_pack_metadata(sample_rule_pack.metadata)
        registry.register_package(manifest, "/path/to/package.zip")

        # Remove entire package
        result = registry.remove_package("test-pack")
        assert result is True

        # Verify package is removed
        package_info = registry.get_package_info("test-pack", "1.0.0")
        assert package_info is None

    def test_remove_nonexistent_package(self, temp_directory):
        """Test removing a nonexistent package."""
        registry = RulePackageRegistry(str(temp_directory))

        result = registry.remove_package("nonexistent-pack")
        assert result is False


class TestIntegration:
    """Integration tests for rule distribution system."""

    def test_full_package_lifecycle(self, sample_rule_pack, temp_directory):
        """Test complete package creation, validation, and registry workflow."""
        # Create package
        builder = RulePackageBuilder()
        package_path = temp_directory / "test-pack.zip"
        builder.create_package(sample_rule_pack, str(package_path), include_signature=False)

        # Validate package
        validator = RulePackageValidator()
        validation_result = validator.validate_package(str(package_path))
        assert validation_result["valid"] is True

        # Register package
        registry = RulePackageRegistry(str(temp_directory / "registry"))
        manifest = RulePackageManifest.from_dict(validation_result["manifest"])
        registry.register_package(manifest, str(package_path))

        # Verify registration
        package_info = registry.get_package_info("test-pack", "1.0.0")
        assert package_info is not None
        assert package_info["manifest"]["name"] == "test-pack"

        # List packages
        packages = registry.list_packages()
        assert len(packages) == 1
        assert packages[0]["name"] == "test-pack"

    def test_signed_package_workflow(self, sample_rule_pack, temp_directory):
        """Test workflow with signed packages."""
        # Generate key pair
        private_key, public_key = RulePackageBuilder.generate_key_pair()

        # Create signed package
        builder = RulePackageBuilder(private_key=private_key)
        package_path = temp_directory / "signed-pack.zip"
        builder.create_package(sample_rule_pack, str(package_path), include_signature=True)

        # Validate with signature verification
        validator = RulePackageValidator(public_key=public_key)
        result = validator.validate_package(str(package_path), verify_signature=True)

        assert result["valid"] is True
        assert result["manifest"]["signature"] != ""

        # Verify signature verification fails with wrong key
        _, wrong_public_key = RulePackageBuilder.generate_key_pair()
        wrong_validator = RulePackageValidator(public_key=wrong_public_key)
        wrong_result = wrong_validator.validate_package(str(package_path), verify_signature=True)

        assert wrong_result["valid"] is False
