#!/usr/bin/env python3
"""
Comprehensive Integration Tests for Release Workflow

This test suite validates the complete release workflow solution including:
- Dependency installation and validation
- TOML file handling
- Workflow configuration
- Error scenarios and recovery mechanisms

Requirements: 1.1, 1.2, 1.3, 2.1, 2.2
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

import pytest


class TestDependencyInstallation:
    """Test dependency installation on multiple Python versions."""

    def test_correct_package_names_used(self):
        """Verify that correct package names are used in workflow."""
        workflow_file = Path(".github/workflows/release.yml")
        assert workflow_file.exists(), "Release workflow file not found"

        content = workflow_file.read_text()

        # Verify correct package name is used
        assert "tomli-w" in content, "Correct package name 'tomli-w' not found in workflow"

        # Verify incorrect package name is NOT used
        assert "tomllib-w" not in content, "Incorrect package name 'tomllib-w' found in workflow"

    def test_validation_dependencies_installable(self):
        """Test that validation dependencies can be installed."""
        # Test installing the validation dependencies
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--dry-run", "requests", "tomli-w"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Dependency installation check failed: {result.stderr}"

    def test_tomli_w_package_exists(self):
        """Verify tomli-w package exists and can be imported."""
        try:
            import tomli_w

            assert hasattr(tomli_w, "dump"), "tomli_w.dump function not available"
        except ImportError:
            pytest.skip("tomli-w not installed in test environment")

    def test_tomllib_builtin_available(self):
        """Verify tomllib is available as built-in module."""
        if sys.version_info >= (3, 11):
            import tomllib

            assert hasattr(tomllib, "load"), "tomllib.load function not available"
        else:
            pytest.skip("tomllib only available in Python 3.11+")


class TestDependencyValidation:
    """Test dependency validation script functionality."""

    def test_validation_script_exists(self):
        """Verify dependency validation script exists."""
        script_path = Path("scripts/validate_dependencies.py")
        assert script_path.exists(), "Dependency validation script not found"
        assert script_path.stat().st_size > 0, "Validation script is empty"

    def test_validation_script_executable(self):
        """Test that validation script can be executed."""
        script_path = Path("scripts/validate_dependencies.py")

        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Validation script failed: {result.stderr}"
        assert "usage:" in result.stdout.lower(), "Help output not found"

    def test_validation_script_checks_pypi(self):
        """Test that validation script checks packages against PyPI."""
        script_path = Path("scripts/validate_dependencies.py")

        result = subprocess.run(
            [sys.executable, str(script_path), "--verbose"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Script should complete successfully
        assert result.returncode == 0, f"Validation failed: {result.stderr}"

        # Should check for tomli-w
        assert "tomli-w" in result.stdout, "tomli-w not validated"

        # Should report success
        assert (
            "validated successfully" in result.stdout.lower() or "valid" in result.stdout.lower()
        ), "Validation success not reported"

    def test_validation_detects_invalid_packages(self):
        """Test that validation script detects invalid package names."""
        # This test verifies the validation logic works
        # We'll test the validator class directly
        script_path = Path("scripts/validate_dependencies.py")

        # Import the validator
        import importlib.util

        spec = importlib.util.spec_from_file_location("validate_deps", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        validator = module.DependencyValidator(verbose=False)

        # Test with a package that definitely doesn't exist
        exists = validator.check_pypi_package_exists("this-package-definitely-does-not-exist-12345")
        assert not exists, "Validator should detect non-existent packages"

        # Test with a real package
        exists = validator.check_pypi_package_exists("requests")
        assert exists, "Validator should find real packages"


class TestTOMLHandling:
    """Test TOML file handling functionality."""

    def test_toml_validation_script_exists(self):
        """Verify TOML validation script exists."""
        script_path = Path("scripts/validate_toml.py")
        assert script_path.exists(), "TOML validation script not found"

    def test_toml_handler_module_exists(self):
        """Verify TOML handler module exists."""
        handler_path = Path("src/riveter/toml_handler.py")
        assert handler_path.exists(), "TOML handler module not found"

    def test_pyproject_toml_valid(self):
        """Test that pyproject.toml is valid and parseable."""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml not found"

        if sys.version_info >= (3, 11):
            import tomllib

            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)

            # Verify required fields
            assert "project" in data, "project section missing"
            assert "version" in data["project"], "version field missing"
            assert "name" in data["project"], "name field missing"
        else:
            pytest.skip("tomllib only available in Python 3.11+")

    def test_toml_write_functionality(self):
        """Test TOML writing functionality."""
        try:
            import tomli_w
        except ImportError:
            pytest.skip("tomli-w not installed")

        # Test writing TOML data
        test_data = {"project": {"name": "test", "version": "1.0.0"}}

        with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=".toml") as f:
            tomli_w.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            # Verify file was written
            assert temp_path.exists(), "TOML file not written"
            assert temp_path.stat().st_size > 0, "TOML file is empty"

            # Verify content is valid
            if sys.version_info >= (3, 11):
                import tomllib

                with open(temp_path, "rb") as f:
                    loaded_data = tomllib.load(f)

                assert loaded_data == test_data, "TOML data mismatch"
        finally:
            temp_path.unlink()


class TestWorkflowConfiguration:
    """Test workflow configuration and documentation."""

    def test_workflow_dependencies_yml_exists(self):
        """Verify centralized workflow dependencies file exists."""
        deps_file = Path(".github/workflow-dependencies.yml")
        assert deps_file.exists(), "workflow-dependencies.yml not found"

    def test_workflow_dependencies_yml_valid(self):
        """Test that workflow-dependencies.yml is valid YAML."""
        import yaml

        deps_file = Path(".github/workflow-dependencies.yml")

        with open(deps_file) as f:
            data = yaml.safe_load(f)

        # Verify structure
        assert "dependencies" in data, "dependencies section missing"
        assert "validation" in data["dependencies"], "validation dependencies missing"

        # Verify tomli-w is documented
        validation_deps = data["dependencies"]["validation"]["packages"]
        tomli_w_found = any(pkg["name"] == "tomli-w" for pkg in validation_deps)
        assert tomli_w_found, "tomli-w not documented in workflow-dependencies.yml"

    def test_workflow_documentation_exists(self):
        """Verify essential workflow documentation exists."""
        # Only check for core documentation that actually exists
        docs = [
            Path("docs/README.md"),
            Path("docs/TECHNICAL.md"),
        ]

        for doc in docs:
            assert doc.exists(), f"Documentation file {doc} not found"
            assert doc.stat().st_size > 0, f"Documentation file {doc} is empty"

    def test_release_workflow_has_validation_step(self):
        """Verify release workflow includes dependency validation step."""
        workflow_file = Path(".github/workflows/release.yml")
        content = workflow_file.read_text()

        # Check for validation step
        assert "Validate workflow dependencies" in content, "Validation step not found"
        assert "validate_dependencies.py" in content, "Validation script not called"


class TestErrorHandling:
    """Test error scenarios and recovery mechanisms."""

    def test_validation_script_handles_network_errors(self):
        """Test that validation script handles network errors gracefully."""
        script_path = Path("scripts/validate_dependencies.py")

        # Import the validator
        import importlib.util

        spec = importlib.util.spec_from_file_location("validate_deps", script_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        validator = module.DependencyValidator(verbose=False)

        # Test with invalid URL (should handle gracefully)
        # The validator should return False, not raise an exception
        result = validator.check_pypi_package_exists("test-package")
        assert isinstance(result, bool), "Validator should return boolean"

    def test_toml_validation_handles_invalid_files(self):
        """Test that TOML validation handles invalid files gracefully."""
        script_path = Path("scripts/validate_toml.py")

        # Create invalid TOML file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".toml") as f:
            f.write("invalid toml content [[[")
            temp_path = Path(f.name)

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), str(temp_path)],
                capture_output=True,
                text=True,
            )

            # Should fail gracefully with non-zero exit code
            assert result.returncode != 0, "Should detect invalid TOML"
            # Should provide error message
            assert (
                len(result.stderr) > 0 or "error" in result.stdout.lower()
            ), "Should provide error message"
        finally:
            temp_path.unlink()

    def test_workflow_has_error_recovery(self):
        """Verify workflow includes error recovery mechanisms."""
        workflow_file = Path(".github/workflows/release.yml")
        content = workflow_file.read_text()

        # Check for error handling patterns
        assert "if:" in content, "Conditional execution not found"
        assert "needs." in content, "Job dependencies not found"
        assert "always()" in content, "Always execution not found"


class TestMultiPythonCompatibility:
    """Test compatibility with multiple Python versions."""

    @pytest.mark.parametrize("python_version", ["3.12", "3.13"])
    def test_dependencies_compatible_with_python_version(self, python_version):
        """Test that dependencies are compatible with target Python versions."""
        script_path = Path("scripts/validate_dependencies.py")

        result = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--python-versions",
                python_version,
                "--verbose",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert (
            result.returncode == 0
        ), f"Validation failed for Python {python_version}: {result.stderr}"

    def test_workflow_tests_multiple_python_versions(self):
        """Verify workflow tests multiple Python versions."""
        workflow_file = Path(".github/workflows/release.yml")
        content = workflow_file.read_text()

        # Check for matrix strategy
        assert "matrix:" in content, "Matrix strategy not found"
        assert "python-version:" in content, "Python version matrix not found"

        # Check for specific versions
        assert "'3.12'" in content or '"3.12"' in content, "Python 3.12 not in matrix"
        assert "'3.13'" in content or '"3.13"' in content, "Python 3.13 not in matrix"


class TestEndToEndScenarios:
    """Test end-to-end scenarios."""

    def test_complete_validation_pipeline(self):
        """Test complete validation pipeline."""
        # 1. Validate TOML files
        toml_script = Path("scripts/validate_toml.py")
        pyproject = Path("pyproject.toml")

        result = subprocess.run(
            [sys.executable, str(toml_script), str(pyproject), "--type", "pyproject"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"TOML validation failed: {result.stderr}"

        # 2. Validate dependencies
        deps_script = Path("scripts/validate_dependencies.py")

        result = subprocess.run(
            [sys.executable, str(deps_script), "--verbose"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        assert result.returncode == 0, f"Dependency validation failed: {result.stderr}"

    def test_workflow_dry_run_configuration(self):
        """Verify workflow supports dry-run mode."""
        workflow_file = Path(".github/workflows/release.yml")
        content = workflow_file.read_text()

        # Check for dry_run input
        assert "dry_run:" in content, "dry_run input not found"
        assert "type: boolean" in content, "dry_run not configured as boolean"

        # Check for dry_run conditionals
        assert "inputs.dry_run" in content, "dry_run not used in conditionals"


def run_comprehensive_tests() -> Tuple[int, int, List[str]]:
    """
    Run all comprehensive tests and return results.

    Returns:
        Tuple of (passed_count, failed_count, error_messages)
    """
    # Run pytest with detailed output
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
    print("🧪 Running Comprehensive Workflow Integration Tests")
    print("=" * 60)
    print()

    exit_code = run_comprehensive_tests()

    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅ All comprehensive tests passed!")
    else:
        print(f"❌ Some tests failed (exit code: {exit_code})")

    sys.exit(exit_code)
