#!/usr/bin/env python3
"""
Dependency Update Helper Script

This script assists with safely updating workflow dependencies by:
- Checking for available updates
- Testing compatibility
- Updating documentation
- Validating changes

Requirements: 4.4, 4.5
"""

import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.request import Request, urlopen


@dataclass
class DependencyUpdate:
    """Information about a dependency update."""

    name: str
    current_version: str
    latest_version: str
    update_type: str  # 'major', 'minor', 'patch', 'security'
    breaking_changes: bool
    release_notes_url: str


class DependencyUpdater:
    """Helper for updating workflow dependencies."""

    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.pypi_base_url = "https://pypi.org/pypi"

    def log(self, message: str) -> None:
        """Log message if verbose mode is enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def get_package_info(self, package_name: str) -> Optional[dict]:
        """Get package information from PyPI."""
        url = f"{self.pypi_base_url}/{package_name}/json"
        self.log(f"Fetching package info for: {package_name}")

        try:
            request = Request(url)
            request.add_header("User-Agent", "riveter-dependency-updater/1.0")
            with urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode("utf-8"))
                    return data
        except Exception as e:
            self.log(f"Error fetching package info: {e}")
            return None

        return None

    def get_current_version(self, package_name: str) -> Optional[str]:
        """Get currently installed version of a package."""
        try:
            result = subprocess.run(
                ["pip", "show", package_name],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
        except Exception as e:
            self.log(f"Error getting current version: {e}")

        return None

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse semantic version string."""
        try:
            parts = version.split(".")
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2].split("-")[0]) if len(parts) > 2 else 0
            return (major, minor, patch)
        except (ValueError, IndexError):
            return (0, 0, 0)

    def determine_update_type(self, current: str, latest: str) -> Tuple[str, bool]:
        """Determine update type and if there are breaking changes."""
        current_parts = self.parse_version(current)
        latest_parts = self.parse_version(latest)

        if latest_parts[0] > current_parts[0]:
            return "major", True
        elif latest_parts[1] > current_parts[1]:
            return "minor", False
        elif latest_parts[2] > current_parts[2]:
            return "patch", False
        else:
            return "none", False

    def check_for_updates(self, package_name: str) -> Optional[DependencyUpdate]:
        """Check if updates are available for a package."""
        print(f"🔍 Checking for updates: {package_name}")

        # Get current version
        current_version = self.get_current_version(package_name)
        if not current_version:
            print(f"⚠️  Package {package_name} not installed")
            return None

        # Get latest version from PyPI
        package_info = self.get_package_info(package_name)
        if not package_info:
            print("❌ Could not fetch package info from PyPI")
            return None

        latest_version = package_info.get("info", {}).get("version")
        if not latest_version:
            print("❌ Could not determine latest version")
            return None

        # Determine update type
        update_type, breaking_changes = self.determine_update_type(current_version, latest_version)

        if update_type == "none":
            print(f"✅ {package_name} is up to date ({current_version})")
            return None

        # Create update info
        release_notes_url = f"https://pypi.org/project/{package_name}/{latest_version}/"

        update = DependencyUpdate(
            name=package_name,
            current_version=current_version,
            latest_version=latest_version,
            update_type=update_type,
            breaking_changes=breaking_changes,
            release_notes_url=release_notes_url,
        )

        print(f"📦 Update available: {current_version} → {latest_version} ({update_type})")
        if breaking_changes:
            print("⚠️  Warning: This is a major version update with potential breaking changes")

        return update

    def test_update_in_isolation(
        self, package_name: str, version: str, python_versions: List[str]
    ) -> bool:
        """Test package update in isolated environment."""
        print(f"\n🧪 Testing {package_name}=={version} in isolation...")

        for py_version in python_versions:
            print(f"\n  Testing with Python {py_version}...")

            # Create temporary virtual environment
            with tempfile.TemporaryDirectory() as tmpdir:
                venv_path = Path(tmpdir) / "test_env"

                try:
                    # Create venv
                    self.log(f"Creating virtual environment at {venv_path}")
                    result = subprocess.run(
                        [f"python{py_version}", "-m", "venv", str(venv_path)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if result.returncode != 0:
                        print("    ❌ Failed to create virtual environment")
                        print(f"    Error: {result.stderr}")
                        return False

                    # Determine pip path
                    pip_path = venv_path / "bin" / "pip"
                    if not pip_path.exists():
                        pip_path = venv_path / "Scripts" / "pip.exe"  # Windows

                    # Install package
                    self.log(f"Installing {package_name}=={version}")
                    result = subprocess.run(
                        [str(pip_path), "install", f"{package_name}=={version}"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if result.returncode != 0:
                        print("    ❌ Failed to install package")
                        print(f"    Error: {result.stderr}")
                        return False

                    print("    ✅ Installation successful")

                    # Test import
                    python_path = venv_path / "bin" / "python"
                    if not python_path.exists():
                        python_path = venv_path / "Scripts" / "python.exe"  # Windows

                    import_name = package_name.replace("-", "_")
                    result = subprocess.run(
                        [str(python_path), "-c", f"import {import_name}"],
                        capture_output=True,
                        text=True,
                        check=False,
                    )

                    if result.returncode != 0:
                        print("    ⚠️  Import test failed (may be expected for some packages)")
                        self.log(f"Import error: {result.stderr}")
                    else:
                        print("    ✅ Import test passed")

                except Exception as e:
                    print(f"    ❌ Test failed with error: {e}")
                    return False

        print("\n✅ Isolation testing completed successfully")
        return True

    def run_validation_tests(self) -> bool:
        """Run validation tests after update."""
        print("\n🔍 Running validation tests...")

        # Run dependency validation
        print("  Running dependency validation...")
        result = subprocess.run(
            ["python", "scripts/validate_dependencies.py", "--verbose"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("  ❌ Dependency validation failed")
            print(result.stdout)
            return False

        print("  ✅ Dependency validation passed")

        # Run TOML validation
        print("  Running TOML validation...")
        result = subprocess.run(
            [
                "python",
                "scripts/validate_toml.py",
                "pyproject.toml",
                "--type",
                "pyproject",
                "--verbose",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("  ❌ TOML validation failed")
            print(result.stdout)
            return False

        print("  ✅ TOML validation passed")

        return True

    def update_documentation(
        self, package_name: str, old_version: str, new_version: str, notes: str
    ) -> None:
        """Update documentation with new version information."""
        if self.dry_run:
            print("\n📝 [DRY RUN] Would update documentation:")
            print(f"  Package: {package_name}")
            print(f"  Version: {old_version} → {new_version}")
            print(f"  Notes: {notes}")
            return

        print("\n📝 Updating documentation...")
        print("  ⚠️  Manual update required:")
        print("  1. Update .github/workflow-dependencies.yml")
        print("  2. Update .github/workflow-dependencies.yml documentation")
        print("  3. Add notes about the update")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Helper script for updating workflow dependencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("package", help="Package name to update (e.g., requests, tomli-w)")
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check for updates, don't perform update",
    )
    parser.add_argument(
        "--test-version",
        help="Test specific version instead of latest",
    )
    parser.add_argument(
        "--python-versions",
        nargs="+",
        default=["3.12", "3.13"],
        help="Python versions to test (default: 3.12 3.13)",
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip isolation testing (not recommended)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    updater = DependencyUpdater(verbose=args.verbose, dry_run=args.dry_run)

    # Check for updates
    update = updater.check_for_updates(args.package)

    if not update:
        if args.check_only:
            return 0
        print("\n✅ No updates needed")
        return 0

    if args.check_only:
        print("\n📋 Update Information:")
        print(f"  Package: {update.name}")
        print(f"  Current: {update.current_version}")
        print(f"  Latest: {update.latest_version}")
        print(f"  Type: {update.update_type}")
        print(f"  Breaking: {update.breaking_changes}")
        print(f"  Release Notes: {update.release_notes_url}")
        return 0

    # Determine version to test
    test_version = args.test_version or update.latest_version

    # Test in isolation
    if not args.skip_tests:
        if not updater.test_update_in_isolation(args.package, test_version, args.python_versions):
            print("\n❌ Isolation testing failed")
            print("   Review errors above and fix issues before updating")
            return 1
    else:
        print("\n⚠️  Skipping isolation tests (not recommended)")

    # Run validation tests
    if not args.skip_tests:
        if not updater.run_validation_tests():
            print("\n❌ Validation tests failed")
            return 1

    # Update documentation
    updater.update_documentation(
        args.package,
        update.current_version,
        test_version,
        f"Updated from {update.current_version} to {test_version}",
    )

    # Print next steps
    print("\n✅ Update testing completed successfully")
    print("\n📋 Next Steps:")
    print(f"  1. Review release notes: {update.release_notes_url}")
    print("  2. Update .github/workflow-dependencies.yml")
    print("  3. Update .github/workflow-dependencies.yml documentation")
    print("  4. Update .github/workflows/release.yml if needed")
    print("  5. Run full test suite: pytest tests/ -v")
    print("  6. Test workflow in dry-run mode")
    print("  7. Commit changes with descriptive message")
    print("\n📖 See .github/workflow-dependencies.yml for detailed procedures")

    return 0


if __name__ == "__main__":
    sys.exit(main())
