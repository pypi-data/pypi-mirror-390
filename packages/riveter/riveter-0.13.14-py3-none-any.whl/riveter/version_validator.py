"""Comprehensive version validation for Riveter.

This module provides validation utilities to ensure version consistency
across all distribution methods and components.
"""

import logging
import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from .version import get_version_from_pyproject

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationIssue:
    """Represents a version validation issue."""

    component: str
    severity: ValidationSeverity
    message: str
    expected_version: Optional[str] = None
    actual_version: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class ComponentVersionInfo:
    """Version information for a specific component."""

    name: str
    version: Optional[str]
    source: str  # Where the version was found (file path, command, etc.)
    is_valid: bool = True
    issues: List[ValidationIssue] = field(default_factory=list)


@dataclass
class ValidationReport:
    """Comprehensive validation report."""

    source_version: str  # Version from pyproject.toml
    components: Dict[str, ComponentVersionInfo] = field(default_factory=dict)
    issues: List[ValidationIssue] = field(default_factory=list)
    is_consistent: bool = True

    def add_issue(self, issue: ValidationIssue) -> None:
        """Add a validation issue to the report."""
        self.issues.append(issue)
        if issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL):
            self.is_consistent = False

    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get all issues of a specific severity level."""
        return [issue for issue in self.issues if issue.severity == severity]

    def has_errors(self) -> bool:
        """Check if report contains any errors or critical issues."""
        return any(
            issue.severity in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
            for issue in self.issues
        )


class VersionValidator:
    """Comprehensive version validator for all Riveter components."""

    def __init__(self, project_root: Path, debug: bool = False):
        """Initialize the version validator.

        Args:
            project_root: Root directory of the Riveter project
            debug: Enable debug mode for verbose output
        """
        self.project_root = project_root
        self.debug = debug

        if debug:
            logger.setLevel(logging.DEBUG)

    def validate_all_components(self) -> ValidationReport:
        """Validate version consistency across all components.

        Returns:
            ValidationReport with comprehensive validation results
        """
        logger.info("Starting comprehensive version validation...")

        try:
            # Get source version from pyproject.toml
            source_version = get_version_from_pyproject(self.project_root)
            logger.debug(f"Source version from pyproject.toml: {source_version}")

            report = ValidationReport(source_version=source_version)

            # Validate each component
            self._validate_pyproject_toml(report)
            self._validate_package_metadata(report)
            self._validate_cli_version(report)
            self._validate_binary_version(report)
            self._validate_homebrew_formula(report)
            self._validate_build_scripts(report)
            self._validate_documentation(report)

            # Perform cross-component validation
            self._validate_version_consistency(report)

            logger.info(f"Validation completed. Found {len(report.issues)} issues.")
            return report

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def _validate_pyproject_toml(self, report: ValidationReport) -> None:
        """Validate pyproject.toml version configuration."""
        logger.debug("Validating pyproject.toml...")

        pyproject_path = self.project_root / "pyproject.toml"

        if not pyproject_path.exists():
            report.add_issue(
                ValidationIssue(
                    component="pyproject.toml",
                    severity=ValidationSeverity.CRITICAL,
                    message="pyproject.toml file not found",
                    suggestion="Create pyproject.toml with proper project configuration",
                )
            )
            return

        try:
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib  # type: ignore
                except ImportError as e:
                    raise ImportError(
                        "tomllib/tomli not available. Install with: pip install tomli"
                    ) from e

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            # Check project section exists
            if "project" not in data:
                report.add_issue(
                    ValidationIssue(
                        component="pyproject.toml",
                        severity=ValidationSeverity.ERROR,
                        message="Missing [project] section",
                        suggestion="Add [project] section with name and version",
                    )
                )
                return

            # Check version field
            version = data["project"].get("version")
            if not version:
                report.add_issue(
                    ValidationIssue(
                        component="pyproject.toml",
                        severity=ValidationSeverity.ERROR,
                        message="Missing version field in [project] section",
                        suggestion="Add version field to [project] section",
                    )
                )
                return

            # Validate version format
            if not self._is_valid_semver(version):
                report.add_issue(
                    ValidationIssue(
                        component="pyproject.toml",
                        severity=ValidationSeverity.WARNING,
                        message=f"Version '{version}' is not valid semantic version",
                        actual_version=version,
                        suggestion="Use semantic versioning format (e.g., 1.0.0)",
                    )
                )

            report.components["pyproject.toml"] = ComponentVersionInfo(
                name="pyproject.toml", version=version, source=str(pyproject_path)
            )

        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    component="pyproject.toml",
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to parse pyproject.toml: {e}",
                    suggestion="Fix TOML syntax errors",
                )
            )

    def _validate_package_metadata(self, report: ValidationReport) -> None:
        """Validate package metadata version."""
        logger.debug("Validating package metadata...")

        try:
            from importlib.metadata import version

            package_version = version("riveter")

            report.components["package_metadata"] = ComponentVersionInfo(
                name="package_metadata", version=package_version, source="importlib.metadata"
            )

            if package_version != report.source_version:
                report.add_issue(
                    ValidationIssue(
                        component="package_metadata",
                        severity=ValidationSeverity.WARNING,
                        message="Package metadata version differs from pyproject.toml",
                        expected_version=report.source_version,
                        actual_version=package_version,
                        suggestion="Reinstall package or rebuild to sync metadata",
                    )
                )

        except ImportError:
            report.add_issue(
                ValidationIssue(
                    component="package_metadata",
                    severity=ValidationSeverity.INFO,
                    message="Package not installed or importlib.metadata not available",
                    suggestion="Install package in development mode: pip install -e .",
                )
            )
        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    component="package_metadata",
                    severity=ValidationSeverity.WARNING,
                    message=f"Failed to get package metadata version: {e}",
                    suggestion="Check package installation",
                )
            )

    def _validate_cli_version(self, report: ValidationReport) -> None:
        """Validate CLI version handling."""
        logger.debug("Validating CLI version handling...")

        cli_path = self.project_root / "src" / "riveter" / "cli.py"

        if not cli_path.exists():
            report.add_issue(
                ValidationIssue(
                    component="cli",
                    severity=ValidationSeverity.ERROR,
                    message="CLI module not found",
                    suggestion="Ensure CLI module exists at src/riveter/cli.py",
                )
            )
            return

        try:
            with open(cli_path, "r") as f:
                content = f.read()

            # Check for proper version handling
            uses_importlib = "importlib.metadata" in content or "importlib_metadata" in content
            has_hardcoded_version = re.search(r'__version__\s*=\s*["\'][\d.]+["\']', content)

            if not uses_importlib:
                report.add_issue(
                    ValidationIssue(
                        component="cli",
                        severity=ValidationSeverity.WARNING,
                        message="CLI does not use importlib.metadata for version",
                        suggestion="Update CLI to use importlib.metadata.version('riveter')",
                    )
                )

            if has_hardcoded_version:
                report.add_issue(
                    ValidationIssue(
                        component="cli",
                        severity=ValidationSeverity.WARNING,
                        message="CLI contains hardcoded version",
                        suggestion="Remove hardcoded version and use dynamic version lookup",
                    )
                )

            report.components["cli"] = ComponentVersionInfo(
                name="cli",
                version=None,  # CLI doesn't have a static version
                source=str(cli_path),
                is_valid=uses_importlib and not has_hardcoded_version,
            )

        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    component="cli",
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to validate CLI version handling: {e}",
                    suggestion="Check CLI module syntax and accessibility",
                )
            )

    def _validate_binary_version(self, report: ValidationReport) -> None:
        """Validate binary version if binary exists."""
        logger.debug("Validating binary version...")

        binary_path = self.project_root / "dist" / "riveter"

        if not binary_path.exists():
            report.add_issue(
                ValidationIssue(
                    component="binary",
                    severity=ValidationSeverity.INFO,
                    message="Binary not found (not built yet)",
                    suggestion="Build binary to validate version consistency",
                )
            )
            return

        try:
            result = subprocess.run(
                [str(binary_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )

            # Extract version from output
            version_match = re.search(r"(\d+\.\d+\.\d+)", result.stdout)
            if version_match:
                binary_version = version_match.group(1)

                report.components["binary"] = ComponentVersionInfo(
                    name="binary", version=binary_version, source=str(binary_path)
                )

                if binary_version != report.source_version:
                    report.add_issue(
                        ValidationIssue(
                            component="binary",
                            severity=ValidationSeverity.ERROR,
                            message="Binary version differs from pyproject.toml",
                            expected_version=report.source_version,
                            actual_version=binary_version,
                            suggestion="Rebuild binary with correct version",
                        )
                    )
            else:
                report.add_issue(
                    ValidationIssue(
                        component="binary",
                        severity=ValidationSeverity.ERROR,
                        message=f"Could not parse version from binary output: {result.stdout}",
                        suggestion="Check binary version output format",
                    )
                )

        except subprocess.TimeoutExpired:
            report.add_issue(
                ValidationIssue(
                    component="binary",
                    severity=ValidationSeverity.ERROR,
                    message="Binary version check timed out",
                    suggestion="Check if binary is corrupted or hanging",
                )
            )
        except subprocess.CalledProcessError as e:
            report.add_issue(
                ValidationIssue(
                    component="binary",
                    severity=ValidationSeverity.ERROR,
                    message=f"Binary version check failed: {e.stderr}",
                    suggestion="Check binary functionality and dependencies",
                )
            )
        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    component="binary",
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to validate binary version: {e}",
                    suggestion="Check binary accessibility and permissions",
                )
            )

    def _validate_homebrew_formula(self, report: ValidationReport) -> None:
        """Validate Homebrew formula version."""
        logger.debug("Validating Homebrew formula...")

        # Check both possible locations for formula
        formula_paths = [
            self.project_root.parent / "homebrew-riveter" / "Formula" / "riveter.rb",
            self.project_root / "homebrew-riveter" / "Formula" / "riveter.rb",
        ]

        formula_path = None
        for path in formula_paths:
            if path.exists():
                formula_path = path
                break

        if not formula_path:
            report.add_issue(
                ValidationIssue(
                    component="homebrew_formula",
                    severity=ValidationSeverity.INFO,
                    message="Homebrew formula not found",
                    suggestion="Create Homebrew formula for distribution",
                )
            )
            return

        try:
            with open(formula_path, "r") as f:
                content = f.read()

            # Extract version from formula
            version_match = re.search(r'version\s+"([^"]+)"', content)
            url_version_match = re.search(r"/v(\d+\.\d+\.\d+)/", content)

            formula_version = None
            if version_match:
                formula_version = version_match.group(1)
            elif url_version_match:
                formula_version = url_version_match.group(1)

            if not formula_version:
                report.add_issue(
                    ValidationIssue(
                        component="homebrew_formula",
                        severity=ValidationSeverity.ERROR,
                        message="Could not find version in Homebrew formula",
                        suggestion="Add explicit version field to formula",
                    )
                )
                return

            report.components["homebrew_formula"] = ComponentVersionInfo(
                name="homebrew_formula", version=formula_version, source=str(formula_path)
            )

            if formula_version != report.source_version:
                report.add_issue(
                    ValidationIssue(
                        component="homebrew_formula",
                        severity=ValidationSeverity.ERROR,
                        message="Homebrew formula version differs from pyproject.toml",
                        expected_version=report.source_version,
                        actual_version=formula_version,
                        suggestion="Update formula version to match pyproject.toml",
                    )
                )

            # Validate formula syntax
            self._validate_formula_syntax(content, report)

        except Exception as e:
            report.add_issue(
                ValidationIssue(
                    component="homebrew_formula",
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to validate Homebrew formula: {e}",
                    suggestion="Check formula file accessibility and syntax",
                )
            )

    def _validate_formula_syntax(self, content: str, report: ValidationReport) -> None:
        """Validate Homebrew formula syntax and structure."""
        required_fields = ["desc", "homepage", "url", "sha256"]
        missing_fields = []

        for required_field in required_fields:
            if required_field not in content:
                missing_fields.append(required_field)

        if missing_fields:
            report.add_issue(
                ValidationIssue(
                    component="homebrew_formula",
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing required fields in formula: {', '.join(missing_fields)}",
                    suggestion="Add missing fields to formula",
                )
            )

        # Check for proper Ruby class definition
        if not re.search(r"class\s+Riveter\s*<\s*Formula", content):
            report.add_issue(
                ValidationIssue(
                    component="homebrew_formula",
                    severity=ValidationSeverity.ERROR,
                    message="Invalid Ruby class definition in formula",
                    suggestion="Ensure formula has proper 'class Riveter < Formula' definition",
                )
            )

    def _validate_build_scripts(self, report: ValidationReport) -> None:
        """Validate build scripts for hardcoded versions."""
        logger.debug("Validating build scripts...")

        build_scripts = [
            self.project_root / "scripts" / "build_binary.py",
            self.project_root / "scripts" / "build_spec.py",
        ]

        for script_path in build_scripts:
            if not script_path.exists():
                continue

            try:
                with open(script_path, "r") as f:
                    content = f.read()

                # Check for hardcoded versions
                hardcoded_versions = re.findall(r'version\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)

                if hardcoded_versions:
                    for version in hardcoded_versions:
                        if version != report.source_version:
                            report.add_issue(
                                ValidationIssue(
                                    component=f"build_script_{script_path.name}",
                                    severity=ValidationSeverity.WARNING,
                                    message=f"Hardcoded version in {script_path.name}",
                                    expected_version=report.source_version,
                                    actual_version=version,
                                    suggestion=(
                                        "Remove hardcoded version and read from pyproject.toml"
                                    ),
                                )
                            )

            except Exception as e:
                report.add_issue(
                    ValidationIssue(
                        component=f"build_script_{script_path.name}",
                        severity=ValidationSeverity.WARNING,
                        message=f"Failed to validate build script: {e}",
                        suggestion="Check script accessibility and syntax",
                    )
                )

    def _validate_documentation(self, report: ValidationReport) -> None:
        """Validate documentation for version references."""
        logger.debug("Validating documentation...")

        doc_files = [
            self.project_root / "README.md",
            self.project_root / "CHANGELOG.md",
        ]

        for doc_path in doc_files:
            if not doc_path.exists():
                continue

            try:
                with open(doc_path, "r") as f:
                    content = f.read()

                # Look for version references that might be outdated
                version_refs = re.findall(r"v?(\d+\.\d+\.\d+)", content)

                if version_refs:
                    outdated_refs = [v for v in version_refs if v != report.source_version]
                    if outdated_refs:
                        report.add_issue(
                            ValidationIssue(
                                component=f"documentation_{doc_path.name}",
                                severity=ValidationSeverity.INFO,
                                message=(
                                    f"Potentially outdated version references in {doc_path.name}"
                                ),
                                suggestion="Review and update version references in documentation",
                            )
                        )

            except Exception as e:
                logger.debug(f"Failed to validate documentation {doc_path}: {e}")

    def _validate_version_consistency(self, report: ValidationReport) -> None:
        """Perform cross-component version consistency validation."""
        logger.debug("Validating cross-component version consistency...")

        # Get all components with versions
        versioned_components = {
            name: info for name, info in report.components.items() if info.version is not None
        }

        if len(versioned_components) < 2:
            report.add_issue(
                ValidationIssue(
                    component="consistency",
                    severity=ValidationSeverity.INFO,
                    message="Not enough components with versions to validate consistency",
                    suggestion="Build more components to enable consistency validation",
                )
            )
            return

        # Check for version mismatches
        inconsistent_components = []
        for name, info in versioned_components.items():
            if info.version != report.source_version:
                inconsistent_components.append(f"{name}({info.version})")

        if inconsistent_components:
            report.add_issue(
                ValidationIssue(
                    component="consistency",
                    severity=ValidationSeverity.ERROR,
                    message=(
                        f"Version inconsistency detected in: {', '.join(inconsistent_components)}"
                    ),
                    expected_version=report.source_version,
                    suggestion="Run version synchronization to fix inconsistencies",
                )
            )

    def _is_valid_semver(self, version: str) -> bool:
        """Check if version string is valid semantic version."""
        pattern = (
            r"^(\d+)\.(\d+)\.(\d+)"
            r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
            r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
        )
        return bool(re.match(pattern, version))

    def generate_validation_report(self, report: ValidationReport) -> str:
        """Generate a human-readable validation report.

        Args:
            report: ValidationReport to format

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("🔍 Version Validation Report")
        lines.append("=" * 50)
        lines.append(f"Source Version (pyproject.toml): {report.source_version}")
        lines.append(
            f"Overall Status: {'✅ CONSISTENT' if report.is_consistent else '❌ INCONSISTENT'}"
        )
        lines.append("")

        # Component summary
        lines.append("📦 Component Versions:")
        for name, info in report.components.items():
            status = "✅" if info.is_valid and info.version == report.source_version else "❌"
            version_str = info.version or "N/A"
            lines.append(f"  {status} {name}: {version_str}")
        lines.append("")

        # Issues by severity
        for severity in [
            ValidationSeverity.CRITICAL,
            ValidationSeverity.ERROR,
            ValidationSeverity.WARNING,
            ValidationSeverity.INFO,
        ]:
            issues = report.get_issues_by_severity(severity)
            if not issues:
                continue

            icon = {"critical": "🚨", "error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity.value]
            lines.append(f"{icon} {severity.value.upper()} Issues ({len(issues)}):")

            for issue in issues:
                lines.append(f"  • {issue.component}: {issue.message}")
                if issue.expected_version and issue.actual_version:
                    lines.append(
                        f"    Expected: {issue.expected_version}, Actual: {issue.actual_version}"
                    )
                if issue.suggestion:
                    lines.append(f"    💡 {issue.suggestion}")
            lines.append("")

        return "\n".join(lines)
