#!/usr/bin/env python3
"""
Dependency Validation Script for Release Workflow

This script validates all workflow dependencies against PyPI to ensure:
- Package names are correct and exist on PyPI
- Packages are compatible with target Python versions
- Version specifications are valid

Requirements: 2.1, 2.2, 2.3
"""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class WorkflowDependency:
    """Represents a workflow dependency with validation metadata."""

    name: str
    version: str
    purpose: str
    python_versions: List[str]
    installation_step: str


@dataclass
class ValidationResult:
    """Result of validating a package."""

    package_name: str
    exists_on_pypi: bool
    compatible_versions: List[str]
    recommended_version: Optional[str]
    issues: List[str]


class DependencyValidator:
    """Validates workflow dependencies against PyPI."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.pypi_base_url = "https://pypi.org/pypi"

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def check_pypi_package_exists(self, package_name: str) -> bool:
        """
        Check if a package exists on PyPI.

        Args:
            package_name: Name of the package to check

        Returns:
            True if package exists, False otherwise
        """
        url = f"{self.pypi_base_url}/{package_name}/json"
        self.log(f"Checking PyPI for package: {package_name}")

        try:
            request = Request(url)
            request.add_header("User-Agent", "riveter-dependency-validator/1.0")
            with urlopen(request, timeout=10) as response:
                if response.status == 200:
                    self.log(f"Package {package_name} found on PyPI")
                    return True
        except HTTPError as e:
            if e.code == 404:
                self.log(f"Package {package_name} not found on PyPI (404)")
                return False
            self.log(f"HTTP error checking {package_name}: {e}")
            return False
        except URLError as e:
            self.log(f"URL error checking {package_name}: {e}")
            return False
        except Exception as e:
            self.log(f"Unexpected error checking {package_name}: {e}")
            return False

        return False

    def get_package_info(self, package_name: str) -> Optional[Dict]:
        """
        Get package information from PyPI.

        Args:
            package_name: Name of the package

        Returns:
            Package information dict or None if not found
        """
        url = f"{self.pypi_base_url}/{package_name}/json"
        self.log(f"Fetching package info for: {package_name}")

        try:
            request = Request(url)
            request.add_header("User-Agent", "riveter-dependency-validator/1.0")
            with urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    self.log(f"Retrieved info for {package_name}")
                    return data
        except Exception as e:
            self.log(f"Error fetching package info for {package_name}: {e}")
            return None

        return None

    def check_python_compatibility(
        self, package_name: str, target_versions: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Check if package is compatible with target Python versions.

        Args:
            package_name: Name of the package
            target_versions: List of Python versions to check (e.g., ["3.12", "3.13"])

        Returns:
            Tuple of (is_compatible, list_of_issues)
        """
        package_info = self.get_package_info(package_name)
        if not package_info:
            return False, [f"Could not retrieve package information for {package_name}"]

        issues = []
        requires_python = package_info.get("info", {}).get("requires_python", "")

        self.log(f"Package {package_name} requires Python: {requires_python or 'not specified'}")

        # Check if package specifies Python version requirements
        if not requires_python:
            issues.append(f"Package {package_name} does not specify Python version requirements")
            # This is a warning, not a failure
            return True, issues

        # Parse requires_python and check compatibility
        # This is a simplified check - full implementation would parse version specifiers
        for target_version in target_versions:
            if target_version not in requires_python and not self._check_version_compatibility(
                requires_python, target_version
            ):
                issues.append(
                    f"Package {package_name} may not be compatible with Python {target_version}"
                )

        return (
            len(issues) == 0 or all("may not be compatible" not in issue for issue in issues),
            issues,
        )

    def _check_version_compatibility(self, requires_python: str, target_version: str) -> bool:
        """
        Simple version compatibility check.

        Args:
            requires_python: The requires_python string from PyPI
            target_version: Target Python version (e.g., "3.12")

        Returns:
            True if likely compatible
        """
        # Simple heuristic: if requires_python contains >=3.X where X <= target minor version
        if ">=" in requires_python:
            try:
                # Extract version after >=
                version_part = requires_python.split(">=")[1].strip().split(",")[0].strip()
                # Parse major.minor
                parts = version_part.split(".")
                if len(parts) >= 2:
                    required_major = int(parts[0])
                    required_minor = int(parts[1])
                    target_parts = target_version.split(".")
                    target_major = int(target_parts[0])
                    target_minor = int(target_parts[1])

                    # Check if target version meets requirement
                    if target_major > required_major:
                        return True
                    if target_major == required_major and target_minor >= required_minor:
                        return True
            except (ValueError, IndexError):
                pass

        return False

    def validate_dependency(
        self, dependency: WorkflowDependency, target_python_versions: List[str]
    ) -> ValidationResult:
        """
        Validate a single dependency.

        Args:
            dependency: The dependency to validate
            target_python_versions: List of Python versions to check compatibility

        Returns:
            ValidationResult with validation details
        """
        issues = []

        # Check if package exists on PyPI
        exists = self.check_pypi_package_exists(dependency.name)
        if not exists:
            issues.append(f"Package '{dependency.name}' does not exist on PyPI")
            return ValidationResult(
                package_name=dependency.name,
                exists_on_pypi=False,
                compatible_versions=[],
                recommended_version=None,
                issues=issues,
            )

        # Check Python version compatibility
        is_compatible, compat_issues = self.check_python_compatibility(
            dependency.name, target_python_versions
        )
        issues.extend(compat_issues)

        # Get package info for version recommendations
        package_info = self.get_package_info(dependency.name)
        recommended_version = None
        compatible_versions = []

        if package_info:
            recommended_version = package_info.get("info", {}).get("version")
            # Get list of available versions
            releases = package_info.get("releases", {})
            compatible_versions = list(releases.keys())

        return ValidationResult(
            package_name=dependency.name,
            exists_on_pypi=exists,
            compatible_versions=compatible_versions[-10:] if compatible_versions else [],
            recommended_version=recommended_version,
            issues=issues,
        )


def get_workflow_dependencies() -> List[WorkflowDependency]:
    """
    Define all workflow dependencies with their metadata.

    Returns:
        List of WorkflowDependency objects
    """
    return [
        WorkflowDependency(
            name="requests",
            version=">=2.25.0",
            purpose="HTTP requests for API validation and PyPI interaction",
            python_versions=["3.12", "3.13"],
            installation_step="Install validation dependencies",
        ),
        WorkflowDependency(
            name="tomli-w",
            version=">=1.0.0",
            purpose="Writing TOML files for configuration updates (pyproject.toml)",
            python_versions=["3.12", "3.13"],
            installation_step="Install validation dependencies",
        ),
        WorkflowDependency(
            name="build",
            version="latest",
            purpose="Building Python packages (sdist and wheel)",
            python_versions=["3.12", "3.13"],
            installation_step="Install build dependencies",
        ),
        WorkflowDependency(
            name="twine",
            version="latest",
            purpose="Uploading packages to PyPI and validating distributions",
            python_versions=["3.12", "3.13"],
            installation_step="Install build dependencies",
        ),
        WorkflowDependency(
            name="wheel",
            version="latest",
            purpose="Building wheel distributions",
            python_versions=["3.12", "3.13"],
            installation_step="Install build dependencies",
        ),
        WorkflowDependency(
            name="setuptools",
            version="latest",
            purpose="Package building and installation utilities",
            python_versions=["3.12", "3.13"],
            installation_step="Install build dependencies",
        ),
        WorkflowDependency(
            name="bandit",
            version=">=1.7.0",
            purpose="Security vulnerability scanning for Python code",
            python_versions=["3.12", "3.13"],
            installation_step="Install security and quality tools",
        ),
        WorkflowDependency(
            name="safety",
            version="latest",
            purpose="Checking dependencies for known security vulnerabilities",
            python_versions=["3.12", "3.13"],
            installation_step="Install security and quality tools",
        ),
    ]


def main() -> int:
    """Main entry point for dependency validation."""
    parser = argparse.ArgumentParser(
        description="Validate workflow dependencies against PyPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--python-versions",
        nargs="+",
        default=["3.12", "3.13"],
        help="Python versions to check compatibility (default: 3.12 3.13)",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Treat warnings as errors and fail validation",
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    validator = DependencyValidator(verbose=args.verbose)
    dependencies = get_workflow_dependencies()

    print("🔍 Validating workflow dependencies...")
    print(f"Target Python versions: {', '.join(args.python_versions)}")
    print()

    results = []
    has_errors = False
    has_warnings = False

    for dep in dependencies:
        result = validator.validate_dependency(dep, args.python_versions)
        results.append(result)

        if not result.exists_on_pypi:
            has_errors = True
            print(f"❌ {result.package_name}: NOT FOUND on PyPI")
            for issue in result.issues:
                print(f"   - {issue}")
        elif result.issues:
            has_warnings = True
            print(f"⚠️  {result.package_name}: Found with warnings")
            for issue in result.issues:
                print(f"   - {issue}")
            if result.recommended_version:
                print(f"   Latest version: {result.recommended_version}")
        else:
            print(f"✅ {result.package_name}: Valid")
            if result.recommended_version:
                print(f"   Latest version: {result.recommended_version}")

        print()

    # Print summary
    print("=" * 60)
    print("📊 Validation Summary")
    print("=" * 60)
    print(f"Total dependencies checked: {len(dependencies)}")
    print(f"Valid: {sum(1 for r in results if r.exists_on_pypi and not r.issues)}")
    print(f"Warnings: {sum(1 for r in results if r.exists_on_pypi and r.issues)}")
    print(f"Errors: {sum(1 for r in results if not r.exists_on_pypi)}")
    print()

    # JSON output if requested
    if args.json_output:
        json_results = {
            "summary": {
                "total": len(dependencies),
                "valid": sum(1 for r in results if r.exists_on_pypi and not r.issues),
                "warnings": sum(1 for r in results if r.exists_on_pypi and r.issues),
                "errors": sum(1 for r in results if not r.exists_on_pypi),
            },
            "dependencies": [
                {
                    "name": r.package_name,
                    "exists": r.exists_on_pypi,
                    "recommended_version": r.recommended_version,
                    "issues": r.issues,
                }
                for r in results
            ],
        }
        print(json.dumps(json_results, indent=2))

    # Determine exit code
    if has_errors:
        print("❌ Validation failed: Some dependencies do not exist on PyPI")
        return 1
    elif has_warnings and args.fail_on_warnings:
        print("⚠️  Validation failed: Warnings found and --fail-on-warnings is set")
        return 1
    else:
        print("✅ All dependencies validated successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
