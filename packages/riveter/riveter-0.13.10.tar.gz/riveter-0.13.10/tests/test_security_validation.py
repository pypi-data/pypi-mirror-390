"""Tests for security validation functionality."""

# Import the security validator
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent / "scripts"))
from validate_security import SecurityValidator


class TestSecurityValidator:
    """Test cases for the SecurityValidator class."""

    def test_validate_workflow_permissions_success(self, tmp_path):
        """Test successful workflow permissions validation."""
        # Create a mock workflow file with correct permissions
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)

        workflow_content = """
name: Release
permissions:
  contents: write
  id-token: write
  actions: read
"""
        workflow_file = workflow_dir / "release.yml"
        workflow_file.write_text(workflow_content)

        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_workflow_permissions()

        assert result is True
        assert "Workflow permissions configured correctly" in validator.passed_checks

    def test_validate_workflow_permissions_missing_file(self, tmp_path):
        """Test workflow permissions validation with missing file."""
        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_workflow_permissions()

        assert result is False
        assert "Release workflow file not found" in validator.issues

    def test_validate_workflow_permissions_missing_permissions(self, tmp_path):
        """Test workflow permissions validation with missing permissions."""
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)

        workflow_content = """
name: Release
permissions:
  contents: write
  # Only has contents write, missing the other two
"""
        workflow_file = workflow_dir / "release.yml"
        workflow_file.write_text(workflow_content)

        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_workflow_permissions()

        assert result is False
        assert any("Missing workflow permissions" in issue for issue in validator.issues)

    def test_validate_secret_usage_success(self, tmp_path):
        """Test successful secret usage validation."""
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)

        workflow_content = """
name: Release
jobs:
  publish:
    steps:
      - name: Publish
        run: echo "Publishing"
        env:
          PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
      - name: Create release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""
        workflow_file = workflow_dir / "release.yml"
        workflow_file.write_text(workflow_content)

        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_secret_usage()

        assert result is True
        assert "Secret usage patterns are secure" in validator.passed_checks

    def test_validate_secret_usage_missing_secrets(self, tmp_path):
        """Test secret usage validation with missing secrets."""
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)

        workflow_content = """
name: Release
jobs:
  publish:
    steps:
      - name: Publish
        run: echo "Publishing"
        # Missing PYPI_API_TOKEN and GITHUB_TOKEN
"""
        workflow_file = workflow_dir / "release.yml"
        workflow_file.write_text(workflow_content)

        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_secret_usage()

        assert result is False
        assert any("PYPI_API_TOKEN secret not referenced" in issue for issue in validator.issues)

    def test_validate_security_documentation_success(self, tmp_path):
        """Test successful security documentation validation."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        # Create required documentation files
        security_setup = docs_dir / "SECURITY_SETUP.md"
        security_setup.write_text(
            """
# Security Setup
## Required Repository Secrets
### PYPI_API_TOKEN
### GITHUB_TOKEN
## Secret Validation
## Security Best Practices
## Troubleshooting
"""
        )

        security_checklist = docs_dir / "SECURITY_CHECKLIST.md"
        security_checklist.write_text("# Security Checklist")

        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_security_documentation()

        assert result is True
        assert "Security documentation exists and appears complete" in validator.passed_checks

    def test_validate_security_documentation_missing_files(self, tmp_path):
        """Test security documentation validation with missing files."""
        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_security_documentation()

        assert result is False
        assert any("Missing security documentation" in issue for issue in validator.issues)

    def test_validate_pyproject_security_success(self, tmp_path):
        """Test successful pyproject.toml validation."""
        pyproject_content = """
[project]
name = "riveter"
version = "1.0.0"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_pyproject_security()

        assert result is True
        assert "pyproject.toml configuration is valid" in validator.passed_checks

    def test_validate_pyproject_security_missing_file(self, tmp_path):
        """Test pyproject.toml validation with missing file."""
        validator = SecurityValidator(str(tmp_path))
        result = validator.validate_pyproject_security()

        assert result is False
        assert "pyproject.toml not found" in validator.issues

    def test_check_for_hardcoded_secrets_clean(self, tmp_path):
        """Test hardcoded secrets check with clean repository."""
        # Create a clean workflow file
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)

        workflow_content = """
name: Release
env:
  PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
"""
        workflow_file = workflow_dir / "release.yml"
        workflow_file.write_text(workflow_content)

        validator = SecurityValidator(str(tmp_path))
        result = validator.check_for_hardcoded_secrets()

        assert result is True
        assert "No hardcoded secrets detected" in validator.passed_checks

    def test_run_validation_success(self, tmp_path):
        """Test complete validation run with successful configuration."""
        # Set up a complete valid repository structure
        workflow_dir = tmp_path / ".github" / "workflows"
        workflow_dir.mkdir(parents=True)

        workflow_content = """
name: Release
permissions:
  contents: write
  id-token: write
  actions: read
jobs:
  publish:
    steps:
      - name: Publish
        env:
          PYPI_API_TOKEN: ${{ secrets.PYPI_API_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""
        workflow_file = workflow_dir / "release.yml"
        workflow_file.write_text(workflow_content)

        # Create documentation
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()

        security_setup = docs_dir / "SECURITY_SETUP.md"
        security_setup.write_text(
            """
# Security Setup
## Required Repository Secrets
### PYPI_API_TOKEN
### GITHUB_TOKEN
## Secret Validation
## Security Best Practices
## Troubleshooting
"""
        )

        security_checklist = docs_dir / "SECURITY_CHECKLIST.md"
        security_checklist.write_text("# Security Checklist")

        # Create pyproject.toml
        pyproject_content = """
[project]
name = "riveter"
version = "1.0.0"
"""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text(pyproject_content)

        validator = SecurityValidator(str(tmp_path))
        success, results = validator.run_validation()

        assert success is True
        assert len(results["issues"]) == 0
        assert len(results["passed_checks"]) > 0

    def test_run_validation_with_issues(self, tmp_path):
        """Test complete validation run with security issues."""
        # Create minimal structure with issues
        validator = SecurityValidator(str(tmp_path))
        success, results = validator.run_validation()

        assert success is False
        assert len(results["issues"]) > 0


@pytest.fixture
def tmp_path():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])
