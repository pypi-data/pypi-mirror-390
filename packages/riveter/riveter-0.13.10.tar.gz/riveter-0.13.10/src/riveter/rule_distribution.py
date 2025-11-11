"""Rule distribution and packaging system for Riveter."""

import hashlib
import json
import os
import tarfile
import tempfile
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

from .exceptions import RiveterError
from .rule_packs import RulePack, RulePackMetadata


class RulePackageError(RiveterError):
    """Errors related to rule package operations."""


@dataclass
class RulePackageManifest:
    """Manifest for a rule package with metadata and integrity information."""

    name: str
    version: str
    description: str
    author: str
    created: str
    updated: str
    dependencies: List[str]
    tags: List[str]
    min_riveter_version: str

    # Package-specific metadata
    package_format: str = "zip"  # zip or tar.gz
    checksum: str = ""
    signature: str = ""
    file_list: List[str] = field(default_factory=list)
    size_bytes: int = 0

    @classmethod
    def from_rule_pack_metadata(cls, metadata: RulePackMetadata) -> "RulePackageManifest":
        """Create a package manifest from rule pack metadata."""
        return cls(
            name=metadata.name,
            version=metadata.version,
            description=metadata.description,
            author=metadata.author,
            created=metadata.created,
            updated=metadata.updated,
            dependencies=metadata.dependencies,
            tags=metadata.tags,
            min_riveter_version=metadata.min_riveter_version,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RulePackageManifest":
        """Create manifest from dictionary."""
        return cls(**data)


class RulePackageBuilder:
    """Builder for creating rule packages with versioning and signatures."""

    def __init__(self, private_key: Optional[RSAPrivateKey] = None):
        """Initialize package builder with optional signing key."""
        self.private_key = private_key

    def create_package(
        self,
        rule_pack: RulePack,
        output_path: str,
        package_format: str = "zip",
        include_signature: bool = True,
    ) -> str:
        """Create a rule package from a rule pack."""
        if package_format not in ["zip", "tar.gz"]:
            raise RulePackageError(f"Unsupported package format: {package_format}")

        if include_signature and not self.private_key:
            raise RulePackageError("Private key required for package signing")

        # Create temporary directory for package contents
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create manifest
            manifest = RulePackageManifest.from_rule_pack_metadata(rule_pack.metadata)
            manifest.package_format = package_format
            manifest.updated = datetime.now().isoformat()

            # Write rule pack to YAML file
            rules_file = temp_path / "rules.yml"
            with open(rules_file, "w", encoding="utf-8") as f:
                yaml.dump(rule_pack.to_dict(), f, default_flow_style=False, sort_keys=False)

            manifest.file_list.append("rules.yml")

            # Add README if it doesn't exist
            readme_file = temp_path / "README.md"
            if not readme_file.exists():
                self._create_readme(readme_file, rule_pack)
                manifest.file_list.append("README.md")

            # Calculate checksums
            manifest.checksum = self._calculate_directory_checksum(temp_path)

            # Sign package if requested
            if include_signature and self.private_key:
                manifest.signature = self._sign_package(temp_path, self.private_key)

            # Write manifest
            manifest_file = temp_path / "manifest.json"
            with open(manifest_file, "w", encoding="utf-8") as f:
                json.dump(manifest.to_dict(), f, indent=2)

            manifest.file_list.append("manifest.json")

            # Create package
            if package_format == "zip":
                return self._create_zip_package(temp_path, output_path, manifest)
            else:
                return self._create_tar_package(temp_path, output_path, manifest)

    def _create_readme(self, readme_path: Path, rule_pack: RulePack) -> None:
        """Create a README file for the rule pack."""
        content = f"""# {rule_pack.metadata.name}

{rule_pack.metadata.description}

## Information

- **Version**: {rule_pack.metadata.version}
- **Author**: {rule_pack.metadata.author}
- **Created**: {rule_pack.metadata.created}
- **Updated**: {rule_pack.metadata.updated}
- **Rules**: {len(rule_pack.rules)}

## Dependencies

{chr(10).join(f"- {dep}" for dep in rule_pack.metadata.dependencies)
 if rule_pack.metadata.dependencies else "None"}

## Tags

{", ".join(rule_pack.metadata.tags)}

## Rules

{chr(10).join(f"- **{rule.id}**: {rule.description}" for rule in rule_pack.rules)}

## Installation

```bash
riveter install-rule-pack {rule_pack.metadata.name}-{rule_pack.metadata.version}.zip
```

## Usage

```bash
riveter scan --rule-pack {rule_pack.metadata.name} /path/to/terraform
```
"""
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

    def _calculate_directory_checksum(self, directory: Path) -> str:
        """Calculate SHA256 checksum of all files in directory."""
        hasher = hashlib.sha256()

        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file() and file_path.name != "manifest.json":
                with open(file_path, "rb") as f:
                    hasher.update(f.read())

        return hasher.hexdigest()

    def _sign_package(self, directory: Path, private_key: RSAPrivateKey) -> str:
        """Sign package contents with private key."""
        # Create signature of the checksum
        checksum = self._calculate_directory_checksum(directory)
        checksum_bytes = checksum.encode("utf-8")

        from cryptography.hazmat.primitives.asymmetric import padding

        signature = private_key.sign(
            checksum_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        return str(signature.hex())

    def _create_zip_package(
        self, source_dir: Path, output_path: str, manifest: RulePackageManifest
    ) -> str:
        """Create ZIP package."""
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    zipf.write(file_path, arcname)

        # Update manifest with package size
        manifest.size_bytes = os.path.getsize(output_path)

        return output_path

    def _create_tar_package(
        self, source_dir: Path, output_path: str, manifest: RulePackageManifest
    ) -> str:
        """Create TAR.GZ package."""
        with tarfile.open(output_path, "w:gz") as tarf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(source_dir)
                    tarf.add(file_path, arcname)

        # Update manifest with package size
        manifest.size_bytes = os.path.getsize(output_path)

        return output_path

    @staticmethod
    def generate_key_pair() -> tuple[RSAPrivateKey, RSAPublicKey]:
        """Generate RSA key pair for package signing."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        public_key = private_key.public_key()
        return private_key, public_key

    @staticmethod
    def save_private_key(
        private_key: RSAPrivateKey, file_path: str, password: Optional[str] = None
    ) -> None:
        """Save private key to file."""
        encryption = (
            NoEncryption()
            if password is None
            else serialization.BestAvailableEncryption(password.encode())
        )

        pem = private_key.private_bytes(
            encoding=Encoding.PEM, format=PrivateFormat.PKCS8, encryption_algorithm=encryption
        )

        with open(file_path, "wb") as f:
            f.write(pem)

    @staticmethod
    def save_public_key(public_key: RSAPublicKey, file_path: str) -> None:
        """Save public key to file."""
        pem = public_key.public_bytes(
            encoding=Encoding.PEM, format=PublicFormat.SubjectPublicKeyInfo
        )

        with open(file_path, "wb") as f:
            f.write(pem)

    @staticmethod
    def load_private_key(file_path: str, password: Optional[str] = None) -> RSAPrivateKey:
        """Load private key from file."""
        with open(file_path, "rb") as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=password.encode() if password else None,
            )

        if not isinstance(private_key, RSAPrivateKey):
            raise RulePackageError("Invalid private key format")

        return private_key

    @staticmethod
    def load_public_key(file_path: str) -> RSAPublicKey:
        """Load public key from file."""
        with open(file_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())

        if not isinstance(public_key, RSAPublicKey):
            raise RulePackageError("Invalid public key format")

        return public_key


class RulePackageValidator:
    """Validator for rule packages with signature verification."""

    def __init__(self, public_key: Optional[RSAPublicKey] = None):
        """Initialize validator with optional public key for signature verification."""
        self.public_key = public_key

    def validate_package(self, package_path: str, verify_signature: bool = True) -> Dict[str, Any]:
        """Validate a rule package and return validation results."""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "manifest": None,
            "rule_pack": None,
        }

        try:
            # Check if package exists
            if not os.path.exists(package_path):
                result["errors"].append(f"Package file does not exist: {package_path}")
                return result

            # Extract and validate package
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Extract package
                if package_path.endswith(".zip"):
                    self._extract_zip_package(package_path, temp_path)
                elif package_path.endswith(".tar.gz"):
                    self._extract_tar_package(package_path, temp_path)
                else:
                    result["errors"].append("Unsupported package format. Must be .zip or .tar.gz")
                    return result

                # Load and validate manifest
                manifest_file = temp_path / "manifest.json"
                if not manifest_file.exists():
                    result["errors"].append("Package missing manifest.json")
                    return result

                with open(manifest_file, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)

                manifest = RulePackageManifest.from_dict(manifest_data)
                result["manifest"] = manifest.to_dict()

                # Verify checksum
                calculated_checksum = self._calculate_directory_checksum(temp_path)
                if calculated_checksum != manifest.checksum:
                    result["errors"].append("Package checksum verification failed")
                    return result

                # Verify signature if requested and available
                if verify_signature and manifest.signature:
                    if not self.public_key:
                        result["warnings"].append("Cannot verify signature: no public key provided")
                    else:
                        if not self._verify_signature(
                            temp_path, manifest.signature, self.public_key
                        ):
                            result["errors"].append("Package signature verification failed")
                            return result

                # Load and validate rule pack
                rules_file = temp_path / "rules.yml"
                if not rules_file.exists():
                    result["errors"].append("Package missing rules.yml")
                    return result

                with open(rules_file, "r", encoding="utf-8") as f:
                    rules_data = yaml.safe_load(f)

                # Validate rule pack structure
                if not isinstance(rules_data, dict):
                    result["errors"].append("Invalid rules.yml format")
                    return result

                if "metadata" not in rules_data or "rules" not in rules_data:
                    result["errors"].append("rules.yml missing required sections")
                    return result

                # Create RulePack object for validation
                from .rule_packs import RulePackManager

                manager = RulePackManager()
                rule_pack = manager._load_rule_pack_from_file(str(rules_file))
                result["rule_pack"] = {
                    "name": rule_pack.metadata.name,
                    "version": rule_pack.metadata.version,
                    "rule_count": len(rule_pack.rules),
                }

                result["valid"] = True

        except Exception as e:
            result["errors"].append(f"Package validation error: {str(e)}")

        return result

    def _extract_zip_package(self, package_path: str, extract_path: Path) -> None:
        """Extract ZIP package."""
        with zipfile.ZipFile(package_path, "r") as zipf:
            zipf.extractall(extract_path)

    def _extract_tar_package(self, package_path: str, extract_path: Path) -> None:
        """Extract TAR.GZ package."""
        with tarfile.open(package_path, "r:gz") as tarf:
            tarf.extractall(extract_path)

    def _calculate_directory_checksum(self, directory: Path) -> str:
        """Calculate SHA256 checksum of all files in directory."""
        hasher = hashlib.sha256()

        for file_path in sorted(directory.rglob("*")):
            if file_path.is_file() and file_path.name != "manifest.json":
                with open(file_path, "rb") as f:
                    hasher.update(f.read())

        return hasher.hexdigest()

    def _verify_signature(
        self, directory: Path, signature_hex: str, public_key: RSAPublicKey
    ) -> bool:
        """Verify package signature."""
        try:
            checksum = self._calculate_directory_checksum(directory)
            checksum_bytes = checksum.encode("utf-8")
            signature_bytes = bytes.fromhex(signature_hex)

            from cryptography.hazmat.primitives.asymmetric import padding

            public_key.verify(
                signature_bytes,
                checksum_bytes,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


class RulePackageRegistry:
    """Registry for managing rule package metadata and versions."""

    def __init__(self, registry_path: str):
        """Initialize registry with storage path."""
        self.registry_path = Path(registry_path)
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.registry_path / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load package index from file."""
        if self.index_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.index = json.load(f)
        else:
            self.index = {"packages": {}, "last_updated": datetime.now().isoformat()}

    def _save_index(self) -> None:
        """Save package index to file."""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.index, f, indent=2)

    def register_package(self, manifest: RulePackageManifest, package_path: str) -> None:
        """Register a package in the registry."""
        package_name = manifest.name
        version = manifest.version

        if package_name not in self.index["packages"]:
            self.index["packages"][package_name] = {"versions": {}}

        self.index["packages"][package_name]["versions"][version] = {
            "manifest": manifest.to_dict(),
            "package_path": package_path,
            "registered": datetime.now().isoformat(),
        }

        # Update latest version
        versions = list(self.index["packages"][package_name]["versions"].keys())
        latest_version = self._get_latest_version(versions)
        self.index["packages"][package_name]["latest"] = latest_version

        self._save_index()

    def get_package_info(
        self, package_name: str, version: str = "latest"
    ) -> Optional[Dict[str, Any]]:
        """Get package information from registry."""
        if package_name not in self.index["packages"]:
            return None

        package_info = self.index["packages"][package_name]

        if version == "latest":
            version = package_info.get("latest")
            if not version:
                return None

        if version not in package_info["versions"]:
            return None

        return dict(package_info["versions"][version])

    def list_packages(self) -> List[Dict[str, Any]]:
        """List all packages in registry."""
        packages = []

        for package_name, package_info in self.index["packages"].items():
            latest_version = package_info.get("latest")
            if latest_version and latest_version in package_info["versions"]:
                version_info = package_info["versions"][latest_version]
                manifest = version_info["manifest"]

                packages.append(
                    {
                        "name": package_name,
                        "version": latest_version,
                        "description": manifest.get("description", ""),
                        "author": manifest.get("author", ""),
                        "versions": list(package_info["versions"].keys()),
                        "registered": version_info.get("registered", ""),
                    }
                )

        return sorted(packages, key=lambda x: x["name"])

    def list_package_versions(self, package_name: str) -> List[str]:
        """List all versions of a package."""
        if package_name not in self.index["packages"]:
            return []

        versions = list(self.index["packages"][package_name]["versions"].keys())
        return sorted(versions, key=self._version_key, reverse=True)

    def remove_package(self, package_name: str, version: Optional[str] = None) -> bool:
        """Remove package or specific version from registry."""
        if package_name not in self.index["packages"]:
            return False

        if version is None:
            # Remove entire package
            del self.index["packages"][package_name]
        else:
            # Remove specific version
            if version not in self.index["packages"][package_name]["versions"]:
                return False

            del self.index["packages"][package_name]["versions"][version]

            # Update latest version
            remaining_versions = list(self.index["packages"][package_name]["versions"].keys())
            if remaining_versions:
                latest_version = self._get_latest_version(remaining_versions)
                self.index["packages"][package_name]["latest"] = latest_version
            else:
                # No versions left, remove package
                del self.index["packages"][package_name]

        self._save_index()
        return True

    def _get_latest_version(self, versions: List[str]) -> str:
        """Get the latest version from a list of versions."""
        return max(versions, key=self._version_key)

    def _version_key(self, version: str) -> tuple[int, ...]:
        """Convert version string to tuple for comparison."""
        try:
            return tuple(map(int, version.split(".")))
        except ValueError:
            # Fallback for non-semantic versions
            return (0, 0, 0)
