#!/usr/bin/env python3
"""
Regression Tests for Release Workflow

This test suite ensures that existing workflow functionality remains intact after
the dependency fix implementation. Tests validate:
- Existing workflow functionality
- Different package versions and configurations
- Workflow performance and execution time

Requirements: 1.1, 3.1, 4.5
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest


class TestWorkflowFunctionalityIntact:
    """Test that existing workflow functionality remains intact."""

    def test_workflow_file_structure_valid(self):
        """Verify workflow file has valid YAML structure."""
        import yaml

        workflow_file = Path(".github/workflows/release.yml")
        assert workflow_file.exists(), "Workflow file not found"

        with open(workflow_file) as f:
            data = yaml.safe_load(f)

        # Verify basic structure
        assert "name" in data, "Workflow name missing"
        # 'on' is a reserved word in YAML and gets parsed as True
        assert True in data or "on" in data, "Workflow triggers missing"
        assert "jobs" in data, "Workflow jobs missing"

    def test_workflow_has_required_jobs(self):
        """Verify all required jobs are present in workflow."""
        import yaml

        workflow_file = Path(".github/workflows/release.yml")

        with open(workflow_file) as f:
            data = yaml.safe_load(f)

        required_jobs = [
            "validate",
            "test",
            "build-validation",
            "pre-release-summary",
            "version-management",
            "changelog",
            "build",
            "publish-pypi",
            "github-release",
            "summary",
        ]

        jobs = data.get("jobs", {})
        for job in required_jobs:
            assert job in jobs, f"Required job '{job}' missing from workflow"

    def test_workflow_job_dependencies_intact(self):
        """Verify job dependencies are correctly configured."""
        import yaml

        workflow_file = Path(".github/workflows/release.yml")

        with open(workflow_file) as f:
            data = yaml.safe_load(f)

        jobs = data.get("jobs", {})

        # Test job depends on validate
        assert "needs" in jobs["test"], "Test job missing dependencies"
        assert "validate" in jobs["test"]["needs"], "Test job not dependent on validate"

        # Build depends on multiple jobs
        assert "needs" in jobs["build"], "Build job missing dependencies"
        build_needs = jobs["build"]["needs"]
        assert "validate" in build_needs, "Build not dependent on validate"
        assert "pre-release-summary" in build_needs, "Build not dependent on pre-release-summary"

    def test_workflow_permissions_configured(self):
        """Verify workflow permissions are properly configured."""
        import yaml

        workflow_file = Path(".github/workflows/release.yml")

        with open(workflow_file) as f:
            data = yaml.safe_load(f)

        # Check permissions are defined
        assert "permissions" in data, "Workflow permissions not defined"

        permissions = data["permissions"]
        assert "contents" in permissions, "Contents permission not defined"
        assert "id-token" in permissions, "ID token permission not defined"

    def test_workflow_inputs_configured(self):
        """Verify workflow inputs are properly configured."""
        import yaml

        workflow_file = Path(".github/workflows/release.yml")

        with open(workflow_file) as f:
            data = yaml.safe_load(f)

        # Check workflow_dispatch inputs ('on' is parsed as True in YAML)
        triggers = data.get(True, data.get("on", {}))
        assert "workflow_dispatch" in triggers, "workflow_dispatch trigger not found"
        inputs = triggers["workflow_dispatch"].get("inputs", {})

        assert "version_type" in inputs, "version_type input missing"
        assert "dry_run" in inputs, "dry_run input missing"


class TestPackageVersionCompatibility:
    """Test with different package versions and configurations."""

    def test_tomli_w_version_compatibility(self):
        """Test that tomli-w works with different versions."""
        try:
            import tomli_w

            # Test basic functionality
            test_data = {"test": {"key": "value"}}
            result = tomli_w.dumps(test_data)

            assert isinstance(result, str), "tomli_w.dumps should return string"
            assert "test" in result, "TOML output should contain test key"
        except ImportError:
            pytest.skip("tomli-w not installed")

    def test_requests_version_compatibility(self):
        """Test that requests package works correctly."""
        try:
            import requests

            # Verify requests can be imported and has expected attributes
            assert hasattr(requests, "get"), "requests.get not available"
            assert hasattr(requests, "post"), "requests.post not available"
            assert hasattr(requests, "Session"), "requests.Session not available"
        except ImportError:
            pytest.skip("requests not installed")

    def test_python_version_compatibility(self):
        """Test that code works with current Python version."""
        # Verify Python version is supported
        assert sys.version_info >= (3, 12), "Python 3.12+ required"

        # Test tomllib availability (Python 3.11+)
        if sys.version_info >= (3, 11):
            import tomllib

            assert hasattr(tomllib, "load"), "tomllib.load not available"
            assert hasattr(tomllib, "loads"), "tomllib.loads not available"

    def test_dependency_versions_documented(self):
        """Verify dependency versions are documented."""
        import yaml

        deps_file = Path(".github/workflow-dependencies.yml")
        assert deps_file.exists(), "Dependency documentation not found"

        with open(deps_file) as f:
            data = yaml.safe_load(f)

        # Check version information is present
        assert "dependencies" in data, "Dependencies section missing"

        for category in data["dependencies"].values():
            packages = category.get("packages", [])
            for pkg in packages:
                assert "name" in pkg, "Package name missing"
                assert "version" in pkg, "Package version missing"
                assert "purpose" in pkg, "Package purpose missing"


class TestWorkflowPerformance:
    """Test workflow performance and execution time."""

    def test_validation_script_performance(self):
        """Test that validation script completes in reasonable time."""
        script_path = Path("scripts/validate_dependencies.py")

        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path), "--verbose"],
            capture_output=True,
            text=True,
            timeout=60,  # Should complete within 60 seconds
        )
        elapsed_time = time.time() - start_time

        assert result.returncode == 0, "Validation script failed"
        assert elapsed_time < 60, f"Validation took too long: {elapsed_time:.2f}s"

        print(f"✅ Validation completed in {elapsed_time:.2f} seconds")

    def test_toml_validation_performance(self):
        """Test that TOML validation completes quickly."""
        script_path = Path("scripts/validate_toml.py")
        pyproject = Path("pyproject.toml")

        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path), str(pyproject), "--type", "pyproject"],
            capture_output=True,
            text=True,
            timeout=10,  # Should complete within 10 seconds
        )
        elapsed_time = time.time() - start_time

        assert result.returncode == 0, "TOML validation failed"
        assert elapsed_time < 10, f"TOML validation took too long: {elapsed_time:.2f}s"

        print(f"✅ TOML validation completed in {elapsed_time:.2f} seconds")

    def test_workflow_file_size_reasonable(self):
        """Verify workflow file size is reasonable."""
        workflow_file = Path(".github/workflows/release.yml")

        file_size = workflow_file.stat().st_size
        # Workflow should be less than 100KB
        assert file_size < 100 * 1024, f"Workflow file too large: {file_size} bytes"

        print(f"✅ Workflow file size: {file_size} bytes")


class TestBackwardCompatibility:
    """Test backward compatibility with existing functionality."""

    def test_pyproject_toml_structure_preserved(self):
        """Verify pyproject.toml structure is preserved."""
        if sys.version_info >= (3, 11):
            import tomllib

            pyproject = Path("pyproject.toml")

            with open(pyproject, "rb") as f:
                data = tomllib.load(f)

            # Verify essential fields are present
            assert "project" in data, "project section missing"
            assert "name" in data["project"], "project name missing"
            assert "version" in data["project"], "project version missing"
            assert "description" in data["project"], "project description missing"

            # Verify build system
            assert "build-system" in data, "build-system section missing"
            assert "requires" in data["build-system"], "build-system requires missing"
        else:
            pytest.skip("tomllib only available in Python 3.11+")

    def test_existing_scripts_still_work(self):
        """Verify existing scripts still function correctly."""
        scripts = [
            "scripts/validate_dependencies.py",
            "scripts/validate_toml.py",
            "scripts/validate_security.py",
            "scripts/workflow_error_handler.py",
        ]

        for script_path in scripts:
            script = Path(script_path)
            if not script.exists():
                continue

            # Test that script can be executed with --help
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            assert result.returncode == 0, f"Script {script_path} failed: {result.stderr}"

    def test_documentation_links_valid(self):
        """Verify documentation references are valid."""
        workflow_file = Path(".github/workflows/release.yml")
        content = workflow_file.read_text()

        # Extract documentation references - only check for docs that actually exist
        doc_refs = [
            "docs/README.md",
            "docs/TECHNICAL.md",
        ]

        for doc_ref in doc_refs:
            if doc_ref in content:
                doc_path = Path(doc_ref)
                assert doc_path.exists(), f"Referenced documentation {doc_ref} not found"


class TestErrorHandlingRegression:
    """Test that error handling still works correctly."""

    def test_invalid_toml_handling(self):
        """Test that invalid TOML is handled gracefully."""
        import tempfile

        script_path = Path("scripts/validate_toml.py")

        # Create invalid TOML
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("invalid [[[")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), str(temp_path)],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Should fail gracefully
            assert result.returncode != 0, "Should detect invalid TOML"
            # Should not crash
            assert (
                "Traceback" not in result.stderr or "error" in result.stdout.lower()
            ), "Should handle error gracefully"
        finally:
            temp_path.unlink()

    def test_network_error_handling(self):
        """Test that network errors are handled gracefully."""
        script_path = Path("scripts/validate_dependencies.py")

        # Import and test the validator directly
        import importlib.util

        spec = importlib.util.spec_from_file_location("validate_deps", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        validator = module.DependencyValidator(verbose=False)

        # Test with non-existent package (should not crash)
        result = validator.check_pypi_package_exists("nonexistent-package-xyz-123")
        assert isinstance(result, bool), "Should return boolean, not crash"


class TestConfigurationRegression:
    """Test that configuration changes don't break existing functionality."""

    def test_workflow_dependencies_yml_structure(self):
        """Verify workflow-dependencies.yml has correct structure."""
        import yaml

        deps_file = Path(".github/workflow-dependencies.yml")

        with open(deps_file) as f:
            data = yaml.safe_load(f)

        # Verify structure
        assert "version" in data, "version field missing"
        assert "dependencies" in data, "dependencies section missing"
        assert "maintenance" in data, "maintenance section missing"

        # Verify dependency categories
        deps = data["dependencies"]
        assert "validation" in deps, "validation dependencies missing"
        assert "build" in deps, "build dependencies missing"
        assert "security" in deps, "security dependencies missing"

    def test_all_documented_dependencies_valid(self):
        """Verify all documented dependencies are valid."""
        import yaml

        deps_file = Path(".github/workflow-dependencies.yml")

        with open(deps_file) as f:
            data = yaml.safe_load(f)

        # Get all package names
        all_packages = []
        for category in data["dependencies"].values():
            packages = category.get("packages", [])
            for pkg in packages:
                all_packages.append(pkg["name"])

        # Verify critical packages are documented
        critical_packages = ["requests", "tomli-w", "build", "twine"]
        for pkg in critical_packages:
            assert pkg in all_packages, f"Critical package {pkg} not documented"


def run_regression_tests() -> int:
    """
    Run all regression tests and return exit code.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    result = pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--color=yes",
            "-ra",
        ]
    )

    return result


if __name__ == "__main__":
    print("🔄 Running Regression Tests for Release Workflow")
    print("=" * 60)
    print()

    exit_code = run_regression_tests()

    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅ All regression tests passed!")
    else:
        print(f"❌ Some regression tests failed (exit code: {exit_code})")

    sys.exit(exit_code)
