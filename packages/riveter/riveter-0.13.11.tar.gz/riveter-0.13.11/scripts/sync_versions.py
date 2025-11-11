#!/usr/bin/env python3
"""Version synchronization script for Riveter.

This script ensures version consistency across all distribution methods by:
1. Reading version from pyproject.toml as the single source of truth
2. Updating binary build configuration with correct version
3. Updating Homebrew formula with matching version and checksums
4. Validating version consistency across all components

Usage:
    python scripts/sync_versions.py --validate
    python scripts/sync_versions.py --sync
    python scripts/sync_versions.py --update-formula --checksums \\
        macos-intel:abc123,linux-x86_64:def456
"""

import argparse
import hashlib
import logging
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # noqa: F401
    except ImportError:
        print("Error: tomllib/tomli not available. Install with: pip install tomli")
        sys.exit(1)

# Add project root to Python path to import riveter modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class VersionConsistencyReport:
    """Report on version consistency across components."""

    pyproject_version: str
    binary_version: Optional[str]
    formula_version: Optional[str]
    is_consistent: bool
    discrepancies: List[str]
    recommended_actions: List[str]


class VersionSynchronizer:
    """Handles version synchronization across all Riveter distribution methods."""

    def __init__(
        self, project_root: Path, debug: bool = False, homebrew_repo_path: Optional[Path] = None
    ):
        """Initialize the version synchronizer.

        Args:
            project_root: Root directory of the Riveter project
            debug: Enable debug mode for verbose output
            homebrew_repo_path: Optional path to homebrew repository (defaults to sibling directory)
        """
        self.project_root = project_root
        self.debug = debug
        self.pyproject_path = project_root / "pyproject.toml"

        # Allow custom homebrew repo path for CI/CD workflows
        if homebrew_repo_path:
            self.homebrew_repo_path = homebrew_repo_path
        else:
            self.homebrew_repo_path = project_root.parent / "homebrew-riveter"

        self.formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
        self.build_binary_script = project_root / "scripts" / "build_binary.py"

        if debug:
            logger.setLevel(logging.DEBUG)

    def get_pyproject_version(self) -> str:
        """Get version from pyproject.toml as single source of truth.

        Returns:
            Version string from pyproject.toml

        Raises:
            RuntimeError: If pyproject.toml cannot be read or version not found
        """
        logger.debug(f"Reading version from {self.pyproject_path}")

        try:
            # Use centralized version utilities
            from riveter.version import get_version_from_pyproject

            version = get_version_from_pyproject(self.project_root)
            logger.debug(f"Found version in pyproject.toml: {version}")
            return version
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to read version from pyproject.toml: {e}") from e

    def get_binary_version(self) -> Optional[str]:
        """Get version from built binary if it exists.

        Returns:
            Version string from binary, or None if binary doesn't exist

        Raises:
            RuntimeError: If binary exists but version cannot be extracted
        """
        binary_path = self.project_root / "dist" / "riveter"

        if not binary_path.exists():
            logger.debug("Binary not found, skipping binary version check")
            return None

        logger.debug(f"Extracting version from binary at {binary_path}")

        try:
            import subprocess

            result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )

            # Extract version from output (e.g., "riveter 0.9.0" -> "0.9.0")
            version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
            if version_match:
                version = version_match.group(1)
                logger.debug(f"Found version in binary: {version}")
                return version
            else:
                raise RuntimeError(f"Could not parse version from binary output: {result.stdout}")

        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Binary version check timed out") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Binary version check failed: {e.stderr}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to get binary version: {e}") from e

    def get_formula_version(self) -> Optional[str]:
        """Get version from Homebrew formula if it exists.

        Returns:
            Version string from formula, or None if formula doesn't exist

        Raises:
            RuntimeError: If formula exists but version cannot be extracted
        """
        if not self.formula_path.exists():
            logger.debug("Homebrew formula not found, skipping formula version check")
            return None

        logger.debug(f"Reading version from formula at {self.formula_path}")

        try:
            with open(self.formula_path, "r") as f:
                content = f.read()

            # Look for version line in Ruby formula
            version_match = re.search(r'version\s+"([^"]+)"', content)
            if version_match:
                version = version_match.group(1)
                logger.debug(f"Found version in formula: {version}")
                return version
            else:
                # Also check URL for version (fallback)
                url_match = re.search(r"/v(\d+\.\d+\.\d+)/", content)
                if url_match:
                    version = url_match.group(1)
                    logger.debug(f"Found version in formula URL: {version}")
                    return version
                else:
                    raise RuntimeError("Could not find version in Homebrew formula")

        except Exception as e:
            raise RuntimeError(f"Failed to read version from formula: {e}") from e

    def validate_version_consistency(self, release_mode: bool = False) -> VersionConsistencyReport:
        """Validate version consistency across all components.

        Returns:
            VersionConsistencyReport with consistency status and recommendations
        """
        logger.info("Validating version consistency across components...")

        try:
            # Use comprehensive validation
            from riveter.version_validator import VersionValidator

            validator = VersionValidator(self.project_root, debug=self.debug)
            validation_report = validator.validate_all_components()

            # Convert to legacy format for backward compatibility
            pyproject_version = validation_report.source_version
            binary_version = (
                validation_report.components.get("binary", {}).version
                if "binary" in validation_report.components
                else None
            )
            formula_version = (
                validation_report.components.get("homebrew_formula", {}).version
                if "homebrew_formula" in validation_report.components
                else None
            )

            discrepancies = []
            recommended_actions = []

            # Extract discrepancies from validation report
            all_discrepancies = []
            core_discrepancies = []

            for issue in validation_report.issues:
                if issue.expected_version and issue.actual_version:
                    discrepancy = (
                        f"{issue.component}: {issue.actual_version} != {issue.expected_version}"
                    )
                    all_discrepancies.append(discrepancy)

                    # In release mode, only track core component discrepancies
                    if issue.component not in ["homebrew_formula", "binary"]:
                        core_discrepancies.append(discrepancy)
                        if issue.suggestion:
                            recommended_actions.append(issue.suggestion)
                    elif release_mode:
                        logger.info(
                            f"Ignoring {issue.component} discrepancy in release mode: {discrepancy}"
                        )

            # Determine consistency based on mode
            if release_mode:
                is_consistent = len(core_discrepancies) == 0
                discrepancies = core_discrepancies
                if is_consistent:
                    logger.info("✅ Core components are consistent (release mode)")
                else:
                    logger.warning(
                        f"❌ Found {len(core_discrepancies)} core component discrepancies"
                    )
            else:
                is_consistent = len(all_discrepancies) == 0
                discrepancies = all_discrepancies

            if is_consistent:
                logger.info("✅ All versions are consistent")
            else:
                logger.warning(f"❌ Found {len(discrepancies)} version discrepancies")
                for discrepancy in discrepancies:
                    logger.warning(f"  - {discrepancy}")

            return VersionConsistencyReport(
                pyproject_version=pyproject_version,
                binary_version=binary_version,
                formula_version=formula_version,
                is_consistent=is_consistent,
                discrepancies=discrepancies,
                recommended_actions=recommended_actions,
            )

        except Exception as e:
            logger.error(f"Version consistency validation failed: {e}")
            raise

    def validate_comprehensive(self):
        """Perform comprehensive version validation using the new validator.

        Returns:
            ValidationReport with detailed validation results
        """
        logger.info("Performing comprehensive version validation...")

        try:
            from riveter.version_validator import VersionValidator

            validator = VersionValidator(self.project_root, debug=self.debug)
            return validator.validate_all_components()
        except Exception as e:
            logger.error(f"Comprehensive validation failed: {e}")
            raise

    def update_binary_build_config(self, version: str) -> None:
        """Update binary build configuration to use the specified version.

        Args:
            version: Version string to embed in binary

        Raises:
            RuntimeError: If build configuration update fails
        """
        logger.info(f"Updating binary build configuration to version {version}")

        # Check and update PyInstaller spec files if they exist
        self._update_pyinstaller_specs(version)

        # Check and update any build scripts
        self._update_build_scripts(version)

        # Verify CLI module uses proper version handling
        self._verify_cli_version_handling()

    def _update_pyinstaller_specs(self, version: str) -> None:
        """Update PyInstaller spec files with correct version.

        Args:
            version: Version string to embed
        """
        spec_files = list(self.project_root.glob("*.spec"))

        for spec_file in spec_files:
            logger.debug(f"Checking PyInstaller spec file: {spec_file}")

            try:
                with open(spec_file, "r") as f:
                    content = f.read()

                # Update version in spec file if hardcoded
                if re.search(r'version\s*=\s*["\'][\d.]+["\']', content):
                    updated_content = re.sub(
                        r'(version\s*=\s*["\'])[\d.]+(["\'])', f"\\g<1>{version}\\g<2>", content
                    )

                    with open(spec_file, "w") as f:
                        f.write(updated_content)

                    logger.info(f"Updated version in PyInstaller spec: {spec_file}")

            except Exception as e:
                logger.warning(f"Failed to update spec file {spec_file}: {e}")

    def _update_build_scripts(self, version: str) -> None:
        """Update build scripts with correct version.

        Args:
            version: Version string to use
        """
        build_scripts = [
            self.project_root / "scripts" / "build_binary.py",
            self.project_root / "scripts" / "build_spec.py",
        ]

        for script_path in build_scripts:
            if not script_path.exists():
                continue

            logger.debug(f"Checking build script: {script_path}")

            try:
                with open(script_path, "r") as f:
                    content = f.read()

                # Update hardcoded versions in build scripts
                if re.search(r'version\s*=\s*["\'][\d.]+["\']', content):
                    updated_content = re.sub(
                        r'(version\s*=\s*["\'])[\d.]+(["\'])', f"\\g<1>{version}\\g<2>", content
                    )

                    with open(script_path, "w") as f:
                        f.write(updated_content)

                    logger.info(f"Updated version in build script: {script_path}")

            except Exception as e:
                logger.warning(f"Failed to update build script {script_path}: {e}")

    def _verify_cli_version_handling(self) -> None:
        """Verify CLI module uses proper version handling."""
        cli_path = self.project_root / "src" / "riveter" / "cli.py"

        if not cli_path.exists():
            logger.warning(f"CLI module not found at {cli_path}")
            return

        try:
            with open(cli_path, "r") as f:
                content = f.read()

            # Check if CLI uses importlib.metadata for version
            if "importlib.metadata" in content or "importlib_metadata" in content:
                logger.debug("✅ CLI uses importlib.metadata for version")
            else:
                logger.warning("⚠️  CLI should use importlib.metadata for version")

            # Check for hardcoded versions
            if re.search(r'__version__\s*=\s*["\'][\d.]+["\']', content):
                logger.warning("⚠️  Found hardcoded __version__ in CLI module")

        except Exception as e:
            logger.warning(f"Failed to verify CLI version handling: {e}")

    def calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to the file to checksum

        Returns:
            SHA256 checksum as hexadecimal string

        Raises:
            RuntimeError: If checksum calculation fails
        """
        logger.debug(f"Calculating SHA256 checksum for {file_path}")

        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)

            checksum = sha256_hash.hexdigest()
            logger.debug(f"SHA256 checksum: {checksum}")
            return checksum

        except Exception as e:
            raise RuntimeError(f"Failed to calculate SHA256 checksum: {e}") from e

    def calculate_release_checksums(
        self, version: str, release_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """Calculate checksums for all release artifacts.

        Args:
            version: Version string to look for in artifact names
            release_dir: Directory containing release artifacts (defaults to dist/)

        Returns:
            Dictionary mapping platform to checksum

        Raises:
            RuntimeError: If checksum calculation fails
        """
        if release_dir is None:
            release_dir = self.project_root / "dist"

        if not release_dir.exists():
            logger.warning(f"Release directory not found: {release_dir}")
            return {}

        logger.info(f"Calculating checksums for release artifacts in {release_dir}")

        checksums = {}
        platform_patterns = {
            "macos-intel": f"*{version}*macos*intel*.tar.gz",
            "macos-arm64": f"*{version}*macos*arm64*.tar.gz",
            "linux-x86_64": f"*{version}*linux*x86_64*.tar.gz",
        }

        for platform, pattern in platform_patterns.items():
            artifacts = list(release_dir.glob(pattern))

            if not artifacts:
                logger.warning(f"No artifacts found for {platform} with pattern: {pattern}")
                continue

            if len(artifacts) > 1:
                logger.warning(f"Multiple artifacts found for {platform}: {artifacts}")

            artifact = artifacts[0]
            try:
                checksum = self.calculate_file_checksum(artifact)
                checksums[platform] = checksum
                logger.info(f"✅ {platform}: {checksum} ({artifact.name})")
            except Exception as e:
                logger.error(
                    f"Failed to calculate checksum for {platform} artifact {artifact}: {e}"
                )

        return checksums

    def validate_checksums(
        self, expected_checksums: Dict[str, str], version: str, release_dir: Optional[Path] = None
    ) -> bool:
        """Validate that calculated checksums match expected values.

        Args:
            expected_checksums: Dictionary of platform -> expected checksum
            version: Version string to look for in artifact names
            release_dir: Directory containing release artifacts

        Returns:
            True if all checksums match, False otherwise
        """
        logger.info("Validating release artifact checksums...")

        calculated_checksums = self.calculate_release_checksums(version, release_dir)

        all_valid = True
        for platform, expected in expected_checksums.items():
            if platform not in calculated_checksums:
                logger.error(f"❌ Missing checksum for platform: {platform}")
                all_valid = False
                continue

            calculated = calculated_checksums[platform]
            if calculated != expected:
                logger.error(f"❌ Checksum mismatch for {platform}:")
                logger.error(f"   Expected:   {expected}")
                logger.error(f"   Calculated: {calculated}")
                all_valid = False
            else:
                logger.info(f"✅ Checksum valid for {platform}")

        return all_valid

    def update_homebrew_formula(
        self, version: str, checksums: Optional[Dict[str, str]] = None
    ) -> None:
        """Update Homebrew formula with the specified version and checksums.

        Args:
            version: Version string to use in formula
            checksums: Optional dictionary of platform -> checksum mappings

        Raises:
            RuntimeError: If formula update fails
        """
        logger.info(f"Updating Homebrew formula to version {version}")

        if not self.homebrew_repo_path.exists():
            raise RuntimeError(f"Homebrew repository not found at {self.homebrew_repo_path}")

        # Ensure Formula directory exists
        formula_dir = self.homebrew_repo_path / "Formula"
        formula_dir.mkdir(exist_ok=True)

        # Generate formula content
        formula_content = self._generate_formula_content(version, checksums)

        try:
            with open(self.formula_path, "w") as f:
                f.write(formula_content)

            logger.info(f"Updated Homebrew formula at {self.formula_path}")

        except Exception as e:
            raise RuntimeError(f"Failed to update Homebrew formula: {e}") from e

    def _generate_formula_content(
        self, version: str, checksums: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate Homebrew formula content with the specified version.

        Args:
            version: Version string to use in formula
            checksums: Optional dictionary of platform -> checksum mappings

        Returns:
            Complete formula content as string
        """
        # Default checksums if not provided
        if checksums is None:
            checksums = {
                "macos-intel": "PLACEHOLDER_CHECKSUM_MACOS_INTEL",
                "macos-arm64": "PLACEHOLDER_CHECKSUM_MACOS_ARM64",
                "linux-x86_64": "PLACEHOLDER_CHECKSUM_LINUX_X86_64",
            }

        # Get source archive checksum for rule packs
        source_checksum = checksums.get("source", "PLACEHOLDER_SOURCE_CHECKSUM")

        formula_template = f"""class Riveter < Formula
  desc "Infrastructure Rule Enforcement as Code for Terraform configurations"
  homepage "https://github.com/riveter/riveter"
  version "{version}"
  license "MIT"

  if OS.mac? && Hardware::CPU.intel?
    url "https://github.com/ScottRyanHoward/riveter/releases/download/v{version}/riveter-{version}-macos-intel.tar.gz"
    sha256 "{checksums.get('macos-intel', 'PLACEHOLDER_CHECKSUM_MACOS_INTEL')}"
  elsif OS.mac? && Hardware::CPU.arm?
    url "https://github.com/ScottRyanHoward/riveter/releases/download/v{version}/riveter-{version}-macos-arm64.tar.gz"
    sha256 "{checksums.get('macos-arm64', 'PLACEHOLDER_CHECKSUM_MACOS_ARM64')}"
  elsif OS.linux?
    url "https://github.com/ScottRyanHoward/riveter/releases/download/v{version}/riveter-{version}-linux-x86_64.tar.gz"
    sha256 "{checksums.get('linux-x86_64', 'PLACEHOLDER_CHECKSUM_LINUX_X86_64')}"
  end

  resource "rule_packs" do
    url "https://github.com/ScottRyanHoward/riveter/archive/v{version}.tar.gz"
    sha256 "{source_checksum}"
  end

  def install
    bin.install "riveter"

    # Install rule packs
    resource("rule_packs").stage do
      (share/"riveter/rule_packs").install Dir["rule_packs/*.yml"]
    end
  end

  test do
    # Test that the binary runs and shows version
    assert_match "{version}", shell_output("#{{bin}}/riveter --version")

    # Test that help command works and contains expected content
    help_output = shell_output("#{{bin}}/riveter --help")
    assert_match "Infrastructure Rule Enforcement", help_output

    # Test that rule packs are installed
    assert_predicate share/"riveter/rule_packs/aws-security.yml", :exist?
  end
end
"""

        return formula_template

    def sync_all_versions(self, checksums: Optional[Dict[str, str]] = None) -> None:
        """Synchronize all component versions to match pyproject.toml.

        Args:
            checksums: Optional dictionary of platform -> checksum mappings

        Raises:
            RuntimeError: If synchronization fails
        """
        logger.info("Starting version synchronization across all components...")

        # Create backup before making changes
        backups = None
        try:
            backups = self.create_backup()
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
            logger.warning("Proceeding without backup (rollback will use git)")

        try:
            # Get authoritative version
            source_version = self.get_pyproject_version()
            logger.info(f"Using version {source_version} as single source of truth")

            # Update binary build configuration
            self.update_binary_build_config(source_version)

            # Update Homebrew formula (skip if repository not available)
            if self.homebrew_repo_path.exists():
                self.update_homebrew_formula(source_version, checksums)
            else:
                logger.info("Skipping Homebrew formula update - repository not available")
                logger.info("Homebrew formula will be updated by separate workflow after release")

            # Validate that synchronization worked (skip Homebrew if not available)
            report = self.validate_version_consistency()
            if not report.is_consistent:
                # Check if the only issue is missing Homebrew formula
                homebrew_only_issue = all(
                    "homebrew" in disc.lower() or "formula" in disc.lower()
                    for disc in report.discrepancies
                )

                if homebrew_only_issue and not self.homebrew_repo_path.exists():
                    logger.info(
                        "Ignoring Homebrew formula discrepancies - repository not available"
                    )
                    logger.info("Homebrew formula will be updated by separate workflow")
                else:
                    raise RuntimeError(
                        f"Version synchronization validation failed: {report.discrepancies}"
                    )

            logger.info("✅ Version synchronization completed successfully")

            # Clean up backup files on success
            if backups:
                backup_dir = self.project_root / ".version_sync_backup"
                for backup_path in backups.values():
                    if backup_path.exists():
                        backup_path.unlink()
                # Remove backup directory if empty
                if backup_dir.exists() and not any(backup_dir.iterdir()):
                    backup_dir.rmdir()

        except Exception as e:
            logger.error(f"Version synchronization failed: {e}")

            # Attempt rollback
            try:
                logger.info("Attempting to rollback changes...")
                self.rollback_changes(backups)
                logger.info("✅ Rollback completed successfully")
            except Exception as rollback_error:
                logger.error(f"Rollback also failed: {rollback_error}")
                logger.error("Manual intervention may be required")

            raise

    def create_backup(self) -> Dict[str, Path]:
        """Create backup of files before synchronization.

        Returns:
            Dictionary mapping component names to backup file paths

        Raises:
            RuntimeError: If backup creation fails
        """
        logger.info("Creating backup of files before synchronization...")

        backup_dir = self.project_root / ".version_sync_backup"
        backup_dir.mkdir(exist_ok=True)

        backups = {}

        try:
            # Backup pyproject.toml
            if self.pyproject_path.exists():
                backup_path = backup_dir / f"pyproject.toml.{int(time.time())}"
                backup_path.write_text(self.pyproject_path.read_text())
                backups["pyproject"] = backup_path
                logger.debug(f"Backed up pyproject.toml to {backup_path}")

            # Backup CLI module
            cli_path = self.project_root / "src" / "riveter" / "cli.py"
            if cli_path.exists():
                backup_path = backup_dir / f"cli.py.{int(time.time())}"
                backup_path.write_text(cli_path.read_text())
                backups["cli"] = backup_path
                logger.debug(f"Backed up CLI module to {backup_path}")

            # Backup Homebrew formula
            if self.formula_path.exists():
                backup_path = backup_dir / f"riveter.rb.{int(time.time())}"
                backup_path.write_text(self.formula_path.read_text())
                backups["formula"] = backup_path
                logger.debug(f"Backed up Homebrew formula to {backup_path}")

            logger.info(f"Created {len(backups)} backup files")
            return backups

        except Exception as e:
            raise RuntimeError(f"Failed to create backup: {e}") from e

    def rollback_changes(self, backups: Optional[Dict[str, Path]] = None) -> None:
        """Rollback version synchronization changes.

        Args:
            backups: Optional dictionary of backup file paths from create_backup()

        Raises:
            RuntimeError: If rollback fails
        """
        logger.info("Rolling back version synchronization changes...")

        try:
            if backups:
                # Restore from provided backups
                restored_count = 0

                if "pyproject" in backups and backups["pyproject"].exists():
                    self.pyproject_path.write_text(backups["pyproject"].read_text())
                    logger.info("Restored pyproject.toml from backup")
                    restored_count += 1

                if "cli" in backups and backups["cli"].exists():
                    cli_path = self.project_root / "src" / "riveter" / "cli.py"
                    cli_path.write_text(backups["cli"].read_text())
                    logger.info("Restored CLI module from backup")
                    restored_count += 1

                if "formula" in backups and backups["formula"].exists():
                    self.formula_path.write_text(backups["formula"].read_text())
                    logger.info("Restored Homebrew formula from backup")
                    restored_count += 1

                logger.info(f"Restored {restored_count} files from backup")

                # Clean up backup files
                for backup_path in backups.values():
                    if backup_path.exists():
                        backup_path.unlink()

            else:
                # Fallback to git-based rollback
                logger.info("No backups provided, attempting git-based rollback...")
                self._git_rollback()

        except Exception as e:
            raise RuntimeError(f"Rollback failed: {e}") from e

    def _git_rollback(self) -> None:
        """Rollback changes using git.

        Raises:
            RuntimeError: If git rollback fails
        """
        import subprocess

        try:
            # Restore CLI module from git
            cli_path = self.project_root / "src" / "riveter" / "cli.py"
            if cli_path.exists():
                subprocess.run(
                    ["git", "checkout", "HEAD", "--", str(cli_path)],
                    cwd=self.project_root,
                    check=True,
                    capture_output=True,
                )
                logger.info("Restored CLI module from git")

            # Restore formula from git (if in same repo)
            if self.formula_path.exists():
                try:
                    subprocess.run(
                        ["git", "checkout", "HEAD", "--", str(self.formula_path)],
                        cwd=self.homebrew_repo_path,
                        check=True,
                        capture_output=True,
                    )
                    logger.info("Restored Homebrew formula from git")
                except subprocess.CalledProcessError:
                    logger.warning("Could not restore formula from git (may be in separate repo)")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git rollback failed: {e}") from e


def parse_checksums(checksums_str: str) -> Dict[str, str]:
    """Parse checksums string into dictionary.

    Args:
        checksums_str: Comma-separated platform:checksum pairs

    Returns:
        Dictionary mapping platform to checksum

    Example:
        "macos-intel:abc123,linux-x86_64:def456" ->
        {"macos-intel": "abc123", "linux-x86_64": "def456"}
    """
    checksums = {}

    if not checksums_str:
        return checksums

    for pair in checksums_str.split(","):
        if ":" not in pair:
            continue

        platform, checksum = pair.split(":", 1)
        checksums[platform.strip()] = checksum.strip()

    return checksums


def main() -> None:
    """Main entry point for the version synchronization script."""
    parser = argparse.ArgumentParser(
        description="Synchronize versions across all Riveter distribution methods",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/sync_versions.py --validate
  python scripts/sync_versions.py --sync
  python scripts/sync_versions.py --update-formula \\
      --checksums "macos-intel:abc123,linux-x86_64:def456"

This script ensures version consistency by:
1. Using pyproject.toml as the single source of truth
2. Updating binary build configuration
3. Updating Homebrew formula with correct version and checksums
4. Validating consistency across all components
        """,
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate version consistency across all components",
    )

    parser.add_argument(
        "--validate-comprehensive",
        action="store_true",
        help="Perform comprehensive version validation with detailed reporting",
    )

    parser.add_argument(
        "--sync",
        action="store_true",
        help="Synchronize all component versions to match pyproject.toml",
    )

    parser.add_argument(
        "--update-formula",
        action="store_true",
        help="Update only the Homebrew formula",
    )

    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback previous version synchronization changes",
    )

    parser.add_argument(
        "--checksums",
        help="Comma-separated platform:checksum pairs "
        "(e.g., 'macos-intel:abc123,linux-x86_64:def456')",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with verbose output",
    )

    parser.add_argument(
        "--homebrew-repo",
        help="Path to homebrew repository (defaults to ../homebrew-riveter)",
    )

    parser.add_argument(
        "--release-mode",
        action="store_true",
        help="Release mode: only validate core components, skip external ones",
    )

    args = parser.parse_args()

    # Validate arguments
    if not any(
        [args.validate, args.validate_comprehensive, args.sync, args.update_formula, args.rollback]
    ):
        parser.error(
            "Must specify one of --validate, --validate-comprehensive, "
            "--sync, --update-formula, or --rollback"
        )

    # Find project root (directory containing pyproject.toml)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent

    if not (project_root / "pyproject.toml").exists():
        logger.error("Could not find project root (pyproject.toml not found)")
        sys.exit(1)

    try:
        homebrew_repo_path = Path(args.homebrew_repo) if args.homebrew_repo else None
        synchronizer = VersionSynchronizer(
            project_root, debug=args.debug, homebrew_repo_path=homebrew_repo_path
        )

        if args.validate:
            report = synchronizer.validate_version_consistency(release_mode=args.release_mode)

            print("\n📊 Version Consistency Report")
            print("=" * 50)
            print(f"pyproject.toml version: {report.pyproject_version}")
            print(f"Binary version: {report.binary_version or 'N/A (binary not found)'}")
            print(f"Formula version: {report.formula_version or 'N/A (formula not found)'}")
            print(f"Consistent: {'✅ Yes' if report.is_consistent else '❌ No'}")

            if report.discrepancies:
                print("\n🔍 Discrepancies Found:")
                for i, discrepancy in enumerate(report.discrepancies, 1):
                    print(f"  {i}. {discrepancy}")

                print("\n💡 Recommended Actions:")
                for i, action in enumerate(report.recommended_actions, 1):
                    print(f"  {i}. {action}")

                sys.exit(1)
            else:
                print("\n✅ All versions are consistent!")

        elif args.validate_comprehensive:
            from riveter.version_validator import VersionValidator

            validator = VersionValidator(project_root, debug=args.debug)
            validation_report = validator.validate_all_components()

            # Print comprehensive report
            report_text = validator.generate_validation_report(validation_report)
            print(f"\n{report_text}")

            if validation_report.has_errors():
                sys.exit(1)
            else:
                print("✅ Comprehensive validation passed!")

        elif args.sync:
            checksums = parse_checksums(args.checksums) if args.checksums else None
            synchronizer.sync_all_versions(checksums)
            print("\n✅ Version synchronization completed successfully!")

        elif args.update_formula:
            version = synchronizer.get_pyproject_version()
            checksums = parse_checksums(args.checksums) if args.checksums else None
            synchronizer.update_homebrew_formula(version, checksums)
            print(f"\n✅ Homebrew formula updated to version {version}!")

        elif args.rollback:
            synchronizer.rollback_changes()
            print("\n✅ Rollback completed successfully!")

    except Exception as e:
        logger.error(f"Operation failed: {e}")
        if args.debug:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
