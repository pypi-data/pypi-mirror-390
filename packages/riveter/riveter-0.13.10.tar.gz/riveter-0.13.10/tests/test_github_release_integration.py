"""Integration tests for GitHub release workflow functionality."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

from riveter.changelog_processor import ChangelogProcessor
from riveter.version_manager import VersionManager, VersionType

# Add scripts directory to Python path for WorkflowErrorHandler import
_scripts_dir = Path(__file__).parent.parent / "scripts"
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from workflow_error_handler import RetryConfig, WorkflowErrorHandler  # noqa: E402


class TestGitHubReleaseIntegration:
    """Test GitHub release creation and workflow integration."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary git repository for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Initialize git repository with main branch
            subprocess.run(
                ["git", "init", "-b", "main"], cwd=repo_path, check=True, capture_output=True
            )

            subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_path, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"], cwd=repo_path, check=True
            )

            # Create basic project structure
            pyproject_content = """[project]
name = "riveter"
version = "1.0.0"
description = "Test project"
"""
            (repo_path / "pyproject.toml").write_text(pyproject_content)

            changelog_content = """# Changelog

## [Unreleased]

### Added
- New feature for testing

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
            (repo_path / "CHANGELOG.md").write_text(changelog_content)

            # Create README.md
            readme_content = """# Test Project

This is a test project for release workflow validation.
"""
            (repo_path / "README.md").write_text(readme_content)

            # Initial commit
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

            yield repo_path

    @pytest.fixture
    def mock_github_api(self):
        """Mock GitHub API responses."""
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # Mock successful API responses
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "tag_name": "v1.1.0",
                "name": "Release 1.1.0",
                "html_url": "https://github.com/test/repo/releases/tag/v1.1.0",
                "id": 12345,
            }

            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                "tag_name": "v1.1.0",
                "name": "Release 1.1.0",
                "html_url": "https://github.com/test/repo/releases/tag/v1.1.0",
                "id": 12345,
            }

            yield mock_get, mock_post

    def test_dry_run_workflow_validation(self, temp_repo):
        """Test complete release workflow in dry-run mode."""
        # Set up environment variables for dry run
        env_vars = {
            "GITHUB_TOKEN": "fake-token",
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
            "GITHUB_REF_NAME": "main",
        }

        with patch.dict(os.environ, env_vars):
            # Test version management
            version_manager = VersionManager(temp_repo)
            version_info = version_manager.create_version_info(VersionType.PATCH)

            assert version_info.current == "1.0.0"
            assert version_info.new == "1.0.1"
            assert version_info.tag == "v1.0.1"

            # Test changelog processing
            changelog_processor = ChangelogProcessor(temp_repo / "CHANGELOG.md")
            updated_content, release_notes = changelog_processor.process_release("1.0.1")

            assert "## [1.0.1]" in updated_content
            assert "New feature for testing" in release_notes.content

            # Test that no actual changes are made in dry run
            original_content = (temp_repo / "pyproject.toml").read_text()
            assert 'version = "1.0.0"' in original_content

    def test_workflow_permissions_validation(self, temp_repo):
        """Test workflow permissions and access controls."""

        handler = WorkflowErrorHandler(temp_repo)

        # Test with missing environment variables (clear all env vars)
        with patch.dict(os.environ, {}, clear=True):
            result = handler.validate_secrets_and_permissions(dry_run=False)
            assert not result.passed
            assert result.details and "issues" in result.details
            issues = result.details["issues"]
            assert any("GITHUB_TOKEN" in issue for issue in issues)
            assert any("PYPI_API_TOKEN" in issue for issue in issues)

        # Test with valid environment variables
        env_vars = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,  # Valid GitHub token format
            "PYPI_API_TOKEN": "pypi-" + "x" * 100,  # Valid PyPI token format
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars):
            result = handler.validate_secrets_and_permissions(dry_run=False)
            assert result.passed

    def test_branch_restriction_validation(self, temp_repo):
        """Test branch restriction enforcement."""

        handler = WorkflowErrorHandler(temp_repo)

        # Create and switch to a feature branch
        subprocess.run(["git", "checkout", "-b", "feature-branch"], cwd=temp_repo, check=True)

        # Test that validation fails on non-main branch
        result = handler.validate_branch_permissions("main")
        assert not result.passed
        assert "feature-branch" in result.message
        assert "main" in result.message

        # Switch back to main branch
        subprocess.run(["git", "checkout", "main"], cwd=temp_repo, check=True)

        # Test that validation passes on main branch
        result = handler.validate_branch_permissions("main")
        assert result.passed

    def test_tag_uniqueness_validation(self, temp_repo):
        """Test git tag uniqueness validation."""

        handler = WorkflowErrorHandler(temp_repo)

        # Test with non-existent tag
        result = handler.validate_tag_uniqueness("v1.1.0")
        assert result.passed

        # Create a tag
        subprocess.run(["git", "tag", "v1.1.0"], cwd=temp_repo, check=True)

        # Test with existing tag
        result = handler.validate_tag_uniqueness("v1.1.0")
        assert not result.passed
        assert "already exists" in result.message

    def test_network_connectivity_validation(self):
        """Test network connectivity validation."""

        handler = WorkflowErrorHandler()

        with patch("requests.get") as mock_get:
            # Test successful connectivity
            mock_get.return_value.status_code = 200
            result = handler.validate_network_connectivity()
            assert result.passed

            # Test failed connectivity
            mock_get.side_effect = requests.RequestException("Connection failed")
            result = handler.validate_network_connectivity()
            assert not result.passed
            assert "Connection failed" in str(result.details)

    def test_error_scenario_handling(self, temp_repo):
        """Test various error scenarios and failure handling."""
        version_manager = VersionManager(temp_repo)

        # Test invalid version type
        with pytest.raises(ValueError, match="Unknown version type"):
            version_manager.calculate_next_version("1.0.0", "invalid")

        # Test invalid version format
        with pytest.raises(ValueError, match="Invalid semantic version format"):
            version_manager._validate_version_format("invalid-version")

        # Test missing pyproject.toml
        (temp_repo / "pyproject.toml").unlink()
        with pytest.raises(FileNotFoundError):
            version_manager.read_current_version()

    def test_rollback_documentation_generation(self, temp_repo):
        """Test rollback documentation creation."""

        handler = WorkflowErrorHandler(temp_repo)

        # Test rollback documentation creation
        rollback_doc = handler.create_rollback_documentation("1.1.0", "v1.1.0")

        assert "Release Rollback Guide - 1.1.0" in rollback_doc
        assert "git tag -d v1.1.0" in rollback_doc
        assert "git push origin --delete v1.1.0" in rollback_doc
        assert "pyproject.toml" in rollback_doc
        assert "CHANGELOG.md" in rollback_doc

        # Test saving rollback documentation
        rollback_file = handler.save_rollback_documentation("1.1.0", "v1.1.0")
        assert rollback_file.exists()
        assert rollback_file.name.startswith("rollback-1.1.0-")
        assert rollback_file.suffix == ".md"

    @patch("subprocess.run")
    def test_git_operation_error_handling(self, mock_run, temp_repo):
        """Test git operation error handling and recovery."""
        version_manager = VersionManager(temp_repo)

        # Test git command failure
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        with pytest.raises(RuntimeError, match="Git repository not available"):
            version_manager.check_tag_exists("v1.1.0")

        # Test timeout handling
        mock_run.side_effect = subprocess.TimeoutExpired("git", 30)

        with pytest.raises(RuntimeError, match="Git operation timed out"):
            version_manager.check_tag_exists("v1.1.0")

    def test_comprehensive_workflow_validation(self, temp_repo):
        """Test comprehensive workflow validation."""

        handler = WorkflowErrorHandler(temp_repo)

        # Set up valid environment
        env_vars = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "PYPI_API_TOKEN": "pypi-" + "x" * 100,
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars), patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200

            # Test comprehensive validation
            success = handler.run_comprehensive_validation("v1.1.0", dry_run=True)
            assert success

            # Verify all validation results were recorded
            assert len(handler.validation_results) > 0
            assert any(result.passed for result in handler.validation_results)

    def test_retry_logic_functionality(self, temp_repo):
        """Test retry logic with different strategies."""

        handler = WorkflowErrorHandler(temp_repo)

        # Test successful operation (no retries needed)
        def successful_operation():
            return "success"

        retry_config = RetryConfig(max_attempts=3, base_delay=0.1)
        success, result, error = handler.retry_with_backoff(
            successful_operation, retry_config, "test_operation"
        )

        assert success
        assert result == "success"
        assert error is None

        # Test failing operation with retries
        call_count = 0

        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Attempt {call_count} failed")
            return "success_after_retries"

        call_count = 0
        success, result, error = handler.retry_with_backoff(
            failing_operation, retry_config, "test_operation"
        )

        assert success
        assert result == "success_after_retries"
        assert call_count == 3

        # Test operation that always fails
        def always_failing_operation():
            raise Exception("Always fails")

        success, result, error = handler.retry_with_backoff(
            always_failing_operation, retry_config, "test_operation"
        )

        assert not success
        assert result is None
        assert error is not None
        assert "Always fails" in str(error)

    def test_workflow_security_validation(self, temp_repo):
        """Test security validation and configuration checks."""

        handler = WorkflowErrorHandler(temp_repo)

        # Test with insecure token formats
        insecure_env = {
            "GITHUB_TOKEN": "short",  # Too short
            "PYPI_API_TOKEN": "invalid-format",  # Wrong format
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, insecure_env):
            result = handler.validate_secrets_and_permissions(dry_run=False)
            assert not result.passed
            assert any(
                "short" in issue or "format" in issue for issue in result.details.get("issues", [])
            )

    def test_project_structure_validation(self, temp_repo):
        """Test project structure validation."""

        handler = WorkflowErrorHandler(temp_repo)

        # Test with complete project structure
        result = handler.validate_project_structure()
        assert result.passed

        # Test with missing files
        (temp_repo / "CHANGELOG.md").unlink()
        result = handler.validate_project_structure()
        assert not result.passed
        assert "CHANGELOG.md" in result.details["missing_files"]

        # Test with invalid pyproject.toml (recreate CHANGELOG.md first)
        changelog_content = """# Changelog

## [Unreleased]

### Added
- New feature for testing
"""
        (temp_repo / "CHANGELOG.md").write_text(changelog_content)
        (temp_repo / "pyproject.toml").write_text("invalid toml content [[[")
        result = handler.validate_project_structure()
        assert not result.passed
        assert "Failed to validate pyproject.toml" in result.message

    @patch("subprocess.run")
    def test_uncommitted_changes_detection(self, mock_run, temp_repo):
        """Test detection of uncommitted changes."""

        handler = WorkflowErrorHandler(temp_repo)

        # Mock git commands with side_effect to handle different commands
        from unittest.mock import MagicMock

        def mock_git_commands(cmd, **kwargs):
            result = MagicMock()
            if len(cmd) > 1 and cmd[1] == "rev-parse":
                result.stdout = "main"
                result.returncode = 0
            elif len(cmd) > 1 and cmd[1] == "status":
                result.stdout = "M  pyproject.toml\n?? new_file.txt"
                result.returncode = 0
            elif len(cmd) > 1 and cmd[1] == "fetch":
                result.stdout = ""
                result.returncode = 0
            elif len(cmd) > 1 and cmd[1] == "rev-list":
                result.stdout = "0"
                result.returncode = 0
            else:
                result.stdout = ""
                result.returncode = 0
            return result

        mock_run.side_effect = mock_git_commands

        result = handler.validate_branch_permissions()
        assert not result.passed
        assert "uncommitted changes" in result.message
        assert "pyproject.toml" in str(result.details)

    def test_workflow_integration_with_mocked_services(self, temp_repo):
        """Test workflow integration with version management and changelog processing."""
        # Test version management and changelog integration
        version_manager = VersionManager(temp_repo)
        changelog_processor = ChangelogProcessor(temp_repo / "CHANGELOG.md")

        # Simulate workflow steps
        version_info = version_manager.create_version_info(VersionType.PATCH)
        updated_content, release_notes = changelog_processor.process_release(version_info.new)

        # Verify the workflow components work together
        assert version_info.new == "1.0.1"
        assert release_notes.version == "1.0.1"
        assert "New feature for testing" in release_notes.content

        # Verify changelog was updated
        assert f"## [{version_info.new}]" in updated_content
