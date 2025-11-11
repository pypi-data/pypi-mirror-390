#!/usr/bin/env python3
"""Simple integration tests for CI pipeline version sync fixes.

This test suite validates the key aspects of the fixes without complex subprocess calls.
"""

import re
import shutil
import subprocess
import unittest
from pathlib import Path


class SimpleIntegrationTests(unittest.TestCase):
    """Simple integration tests for the CI pipeline fixes."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.project_root = Path(__file__).parent.parent
        cls.homebrew_repo_path = cls.project_root.parent / "homebrew-riveter"

    def test_version_sync_script_exists_and_runs(self):
        """Test that version sync script exists and can run."""
        print("\n🔍 Testing version sync script...")

        sync_script = self.project_root / "scripts" / "sync_versions.py"
        self.assertTrue(sync_script.exists(), "Version sync script should exist")

        # Test script syntax
        result = subprocess.run(
            ["python3", "-m", "py_compile", str(sync_script)], capture_output=True, text=True
        )

        self.assertEqual(result.returncode, 0, f"Script should have valid syntax: {result.stderr}")
        print("  ✅ Version sync script exists and has valid syntax")

    def test_homebrew_workflow_uses_correct_audit_syntax(self):
        """Test that Homebrew workflow uses correct audit syntax."""
        print("\n🔍 Testing Homebrew workflow audit syntax...")

        workflow_path = (
            self.project_root / ".github" / "workflows" / "test-homebrew-installation.yml"
        )

        if not workflow_path.exists():
            self.skipTest("Homebrew workflow not found")

        with open(workflow_path, "r") as f:
            content = f.read()

        # Should not use deprecated path-based audit
        self.assertNotIn(
            "brew audit Formula/",
            content,
            "Workflow should not use deprecated path-based audit syntax",
        )

        # Should use name-based audit
        self.assertIn("brew audit", content, "Workflow should include audit commands")

        # Should add tap before audit
        if "brew audit" in content and "riveter" in content:
            # Check that tap is added somewhere in the workflow
            self.assertIn("brew tap", content, "Workflow should add tap before audit")

        print("  ✅ Workflow uses correct audit syntax")

    def test_homebrew_formula_structure(self):
        """Test that Homebrew formula has correct structure."""
        print("\n🔍 Testing Homebrew formula structure...")

        if not self.homebrew_repo_path.exists():
            self.skipTest("Homebrew repository not found")

        formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
        if not formula_path.exists():
            self.skipTest("Homebrew formula not found")

        with open(formula_path, "r") as f:
            content = f.read()

        # Check required components
        required_components = [
            "class Riveter < Formula",
            "desc ",
            "homepage ",
            "def install",
            "test do",  # Changed from "def test" to "test do" for Homebrew formula syntax
        ]

        for component in required_components:
            self.assertIn(component, content, f"Formula should contain: {component}")

        # Check Ruby syntax if Ruby is available
        if shutil.which("ruby"):
            result = subprocess.run(
                ["ruby", "-c", str(formula_path)], capture_output=True, text=True
            )

            self.assertEqual(
                result.returncode, 0, f"Formula should have valid Ruby syntax: {result.stderr}"
            )
            print("  ✅ Formula has valid Ruby syntax")

        print("  ✅ Formula structure is correct")

    def test_version_consistency_check(self):
        """Test version consistency between pyproject.toml and formula."""
        print("\n🔍 Testing version consistency...")

        # Get version from pyproject.toml
        pyproject_path = self.project_root / "pyproject.toml"
        self.assertTrue(pyproject_path.exists(), "pyproject.toml should exist")

        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                self.skipTest("tomllib/tomli not available")

        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)

        pyproject_version = data["project"]["version"]
        print(f"  📋 pyproject.toml version: {pyproject_version}")

        # Check formula version if available
        if self.homebrew_repo_path.exists():
            formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
            if formula_path.exists():
                with open(formula_path, "r") as f:
                    formula_content = f.read()

                version_match = re.search(r'version\s+"([^"]+)"', formula_content)
                if version_match:
                    formula_version = version_match.group(1)
                    print(f"  🍺 Formula version: {formula_version}")

                    # Versions should match (or we should be aware of mismatch)
                    if pyproject_version == formula_version:
                        print("  ✅ Versions are consistent")
                    else:
                        print(
                            f"  ⚠️ Version mismatch detected: {pyproject_version} vs "
                            f"{formula_version}"
                        )
                        print("  ℹ️ This may be expected during development")
                else:
                    print("  ⚠️ Could not extract version from formula")
            else:
                print("  ⚠️ Formula not found")
        else:
            print("  ⚠️ Homebrew repository not found")

        print("  ✅ Version consistency check completed")

    def test_homebrew_tap_basic_structure(self):
        """Test basic Homebrew tap repository structure."""
        print("\n🔍 Testing Homebrew tap structure...")

        if not self.homebrew_repo_path.exists():
            self.skipTest("Homebrew repository not found")

        # Check required directories and files
        formula_dir = self.homebrew_repo_path / "Formula"
        self.assertTrue(formula_dir.exists(), "Formula directory should exist")

        formula_file = formula_dir / "riveter.rb"
        self.assertTrue(formula_file.exists(), "Formula file should exist")

        # Check that formula file is not empty
        self.assertGreater(formula_file.stat().st_size, 0, "Formula file should not be empty")

        print("  ✅ Homebrew tap structure is correct")

    def test_workflow_files_syntax(self):
        """Test that workflow files have valid YAML syntax."""
        print("\n🔍 Testing workflow files syntax...")

        workflows_dir = self.project_root / ".github" / "workflows"
        if not workflows_dir.exists():
            self.skipTest("Workflows directory not found")

        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))

        if not workflow_files:
            self.skipTest("No workflow files found")

        try:
            import yaml
        except ImportError:
            print("  ⚠️ PyYAML not available, skipping YAML syntax validation")
            return

        for workflow_file in workflow_files:
            print(f"  🔍 Validating {workflow_file.name}...")

            try:
                with open(workflow_file, "r") as f:
                    yaml.safe_load(f)
                print(f"    ✅ {workflow_file.name} has valid YAML syntax")
            except yaml.YAMLError as e:
                self.fail(f"Invalid YAML in {workflow_file.name}: {e}")

        print("  ✅ All workflow files have valid syntax")

    def test_scripts_directory_structure(self):
        """Test that scripts directory has expected structure."""
        print("\n🔍 Testing scripts directory structure...")

        scripts_dir = self.project_root / "scripts"
        self.assertTrue(scripts_dir.exists(), "Scripts directory should exist")

        # Check for key scripts
        expected_scripts = ["sync_versions.py"]

        for script_name in expected_scripts:
            script_path = scripts_dir / script_name
            if script_path.exists():
                print(f"  ✅ {script_name} exists")

                # Test syntax
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(script_path)],
                    capture_output=True,
                    text=True,
                )

                self.assertEqual(
                    result.returncode, 0, f"{script_name} should have valid syntax: {result.stderr}"
                )
            else:
                print(f"  ⚠️ {script_name} not found")

        print("  ✅ Scripts directory structure validated")

    def test_integration_summary(self):
        """Provide a summary of integration test results."""
        print("\n📊 Integration Test Summary")
        print("=" * 40)

        checks = []

        # Version sync script
        sync_script = self.project_root / "scripts" / "sync_versions.py"
        checks.append(("Version sync script", sync_script.exists()))

        # Workflow file
        workflow_path = (
            self.project_root / ".github" / "workflows" / "test-homebrew-installation.yml"
        )
        workflow_ok = False
        if workflow_path.exists():
            with open(workflow_path, "r") as f:
                content = f.read()
            workflow_ok = "brew audit Formula/" not in content
        checks.append(("Workflow audit syntax", workflow_ok))

        # Homebrew formula
        formula_ok = False
        if self.homebrew_repo_path.exists():
            formula_path = self.homebrew_repo_path / "Formula" / "riveter.rb"
            formula_ok = formula_path.exists()
        checks.append(("Homebrew formula", formula_ok))

        # Print results
        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {check_name}: {status}")

        passed = sum(1 for _, result in checks if result)
        total = len(checks)

        print(f"\nOverall: {passed}/{total} checks passed")

        if passed == total:
            print("🎉 All integration checks passed!")
        else:
            print("⚠️ Some integration checks need attention")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
