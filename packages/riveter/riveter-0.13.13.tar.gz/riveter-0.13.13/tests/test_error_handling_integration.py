"""Integration tests for workflow error handling functionality."""

import os
import subprocess

# Import the error handler directly
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from workflow_error_handler import (
    ErrorSeverity,
    RetryConfig,
    RetryStrategy,
    ValidationResult,
    WorkflowErrorHandler,
)


class TestWorkflowErrorHandling:
    """Test comprehensive error handling for release workflow."""

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
            (repo_path / "README.md").write_text("# Test Project")

            # Initial commit
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo_path, check=True)

            yield repo_path

    @pytest.fixture
    def error_handler(self, temp_repo):
        """Create error handler instance."""
        return WorkflowErrorHandler(temp_repo)

    def test_error_logging_formats(self, error_handler, capsys):
        """Test error logging with GitHub Actions formatting."""
        # Test different severity levels
        error_handler.log_error("Test info message", ErrorSeverity.INFO)
        error_handler.log_error("Test warning message", ErrorSeverity.WARNING)
        error_handler.log_error("Test error message", ErrorSeverity.ERROR)
        error_handler.log_error(
            "Test critical message", ErrorSeverity.CRITICAL, {"detail": "value"}
        )

        captured = capsys.readouterr()

        # Check GitHub Actions formatting
        assert "::notice::Test info message" in captured.out
        assert "::warning::Test warning message" in captured.out
        assert "::error::Test error message" in captured.out
        assert "::error::Test critical message" in captured.out
        assert '"detail": "value"' in captured.out

    def test_branch_permissions_validation_success(self, error_handler):
        """Test successful branch permissions validation."""
        result = error_handler.validate_branch_permissions("main")

        assert result.passed
        assert result.severity == ErrorSeverity.INFO
        assert "main" in result.message
        assert "up to date" in result.message

    def test_branch_permissions_validation_wrong_branch(self, error_handler, temp_repo):
        """Test branch permissions validation on wrong branch."""
        # Create and switch to feature branch
        subprocess.run(["git", "checkout", "-b", "feature"], cwd=temp_repo, check=True)

        result = error_handler.validate_branch_permissions("main")

        assert not result.passed
        assert result.severity == ErrorSeverity.CRITICAL
        assert "feature" in result.message
        assert "main" in result.message

    def test_secrets_validation_missing_tokens(self, error_handler):
        """Test secrets validation with missing tokens."""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            result = error_handler.validate_secrets_and_permissions(dry_run=False)

            assert not result.passed
            assert result.severity == ErrorSeverity.CRITICAL
            assert "GITHUB_TOKEN" in str(result.details["issues"])
            assert "PYPI_API_TOKEN" in str(result.details["issues"])

    def test_secrets_validation_dry_run(self, error_handler):
        """Test secrets validation in dry run mode."""
        env_vars = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars):
            result = error_handler.validate_secrets_and_permissions(dry_run=True)

            assert result.passed
            assert result.details["dry_run"] is True

    def test_secrets_validation_invalid_format(self, error_handler):
        """Test secrets validation with invalid token formats."""
        env_vars = {
            "GITHUB_TOKEN": "short",  # Too short
            "PYPI_API_TOKEN": "wrong-format",  # Wrong format
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars):
            result = error_handler.validate_secrets_and_permissions(dry_run=False)

            assert not result.passed
            issues = result.details["issues"]
            assert any("short" in issue for issue in issues)
            assert any("format" in issue for issue in issues)

    def test_project_structure_validation_success(self, error_handler):
        """Test successful project structure validation."""
        result = error_handler.validate_project_structure()

        assert result.passed
        assert result.severity == ErrorSeverity.INFO

    def test_project_structure_validation_missing_files(self, error_handler, temp_repo):
        """Test project structure validation with missing files."""
        # Remove required files
        (temp_repo / "CHANGELOG.md").unlink()
        (temp_repo / "README.md").unlink()

        result = error_handler.validate_project_structure()

        assert not result.passed
        assert result.severity == ErrorSeverity.ERROR
        assert "CHANGELOG.md" in result.details["missing_files"]
        assert "README.md" in result.details["missing_files"]

    def test_project_structure_validation_invalid_pyproject(self, error_handler, temp_repo):
        """Test project structure validation with invalid pyproject.toml."""
        # Write invalid TOML content
        (temp_repo / "pyproject.toml").write_text("invalid toml [[[")

        result = error_handler.validate_project_structure()

        assert not result.passed
        assert "Failed to validate pyproject.toml" in result.message

    def test_network_connectivity_validation_success(self, error_handler):
        """Test successful network connectivity validation."""
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200

            result = error_handler.validate_network_connectivity()

            assert result.passed
            assert result.severity == ErrorSeverity.INFO

    def test_network_connectivity_validation_failure(self, error_handler):
        """Test network connectivity validation with failures."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Connection failed")

            result = error_handler.validate_network_connectivity()

            assert not result.passed
            assert result.severity == ErrorSeverity.WARNING
            assert "Connection failed" in str(result.details["failed_services"])

    def test_tag_uniqueness_validation_success(self, error_handler):
        """Test successful tag uniqueness validation."""
        result = error_handler.validate_tag_uniqueness("v1.1.0")

        assert result.passed
        assert result.severity == ErrorSeverity.INFO
        assert "unique" in result.message

    def test_tag_uniqueness_validation_existing_tag(self, error_handler, temp_repo):
        """Test tag uniqueness validation with existing tag."""
        # Create a tag
        subprocess.run(["git", "tag", "v1.1.0"], cwd=temp_repo, check=True)

        result = error_handler.validate_tag_uniqueness("v1.1.0")

        assert not result.passed
        assert result.severity == ErrorSeverity.CRITICAL
        assert "already exists" in result.message

    def test_retry_logic_exponential_backoff(self, error_handler):
        """Test retry logic with exponential backoff."""
        call_count = 0

        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Attempt {call_count} failed")
            return "success"

        retry_config = RetryConfig(
            max_attempts=3,
            base_delay=0.01,  # Very short for testing
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_multiplier=2.0,
        )

        start_time = time.time()
        success, result, error = error_handler.retry_with_backoff(
            failing_operation, retry_config, "test_operation"
        )
        end_time = time.time()

        assert success
        assert result == "success"
        assert error is None
        assert call_count == 3
        # Should have some delay due to backoff
        assert end_time - start_time > 0.01

    def test_retry_logic_linear_backoff(self, error_handler):
        """Test retry logic with linear backoff."""
        call_count = 0

        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception(f"Attempt {call_count} failed")
            return "success"

        retry_config = RetryConfig(max_attempts=3, base_delay=0.01, strategy=RetryStrategy.LINEAR)

        success, result, error = error_handler.retry_with_backoff(
            failing_operation, retry_config, "test_operation"
        )

        assert success
        assert result == "success"
        assert call_count == 2

    def test_retry_logic_max_attempts_exceeded(self, error_handler):
        """Test retry logic when max attempts are exceeded."""

        def always_failing_operation():
            raise Exception("Always fails")

        retry_config = RetryConfig(max_attempts=2, base_delay=0.01)

        success, result, error = error_handler.retry_with_backoff(
            always_failing_operation, retry_config, "test_operation"
        )

        assert not success
        assert result is None
        assert error is not None
        assert "Always fails" in str(error)

    def test_comprehensive_validation_success(self, error_handler):
        """Test comprehensive validation with all checks passing."""
        env_vars = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "PYPI_API_TOKEN": "pypi-" + "x" * 100,
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars), patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200

            success = error_handler.run_comprehensive_validation("v1.1.0", dry_run=True)

            assert success
            assert len(error_handler.validation_results) > 0
            assert all(result.passed for result in error_handler.validation_results)

    def test_comprehensive_validation_failure(self, error_handler, temp_repo):
        """Test comprehensive validation with failures."""
        # Remove required file to cause failure
        (temp_repo / "CHANGELOG.md").unlink()

        env_vars = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars), patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200

            success = error_handler.run_comprehensive_validation("v1.1.0", dry_run=True)

            assert not success
            assert len(error_handler.validation_results) > 0
            assert any(not result.passed for result in error_handler.validation_results)

    def test_rollback_documentation_creation(self, error_handler):
        """Test rollback documentation creation."""
        rollback_doc = error_handler.create_rollback_documentation("1.1.0", "v1.1.0")

        # Check required sections
        assert "Release Rollback Guide - 1.1.0" in rollback_doc
        assert "## Rollback Steps" in rollback_doc
        assert "git tag -d v1.1.0" in rollback_doc
        assert "git push origin --delete v1.1.0" in rollback_doc
        assert "pyproject.toml" in rollback_doc
        assert "CHANGELOG.md" in rollback_doc
        assert "## Prevention for Next Release" in rollback_doc
        assert "dry_run: true" in rollback_doc

    def test_rollback_documentation_saving(self, error_handler, temp_repo):
        """Test saving rollback documentation to file."""
        rollback_file = error_handler.save_rollback_documentation("1.1.0", "v1.1.0")

        assert rollback_file.exists()
        assert rollback_file.parent == temp_repo / ".github" / "rollback"
        assert rollback_file.name.startswith("rollback-1.1.0-")
        assert rollback_file.suffix == ".md"

        content = rollback_file.read_text()
        assert "Release Rollback Guide - 1.1.0" in content

    def test_validation_result_dataclass(self):
        """Test ValidationResult dataclass functionality."""
        result = ValidationResult(
            passed=True,
            message="Test message",
            severity=ErrorSeverity.INFO,
            details={"key": "value"},
        )

        assert result.passed
        assert result.message == "Test message"
        assert result.severity == ErrorSeverity.INFO
        assert result.details["key"] == "value"

    def test_retry_config_dataclass(self):
        """Test RetryConfig dataclass functionality."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_multiplier=3.0,
        )

        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.backoff_multiplier == 3.0

    def test_error_severity_enum(self):
        """Test ErrorSeverity enum values."""
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_retry_strategy_enum(self):
        """Test RetryStrategy enum values."""
        assert RetryStrategy.NONE.value == "none"
        assert RetryStrategy.LINEAR.value == "linear"
        assert RetryStrategy.EXPONENTIAL.value == "exponential"

    @patch("subprocess.run")
    def test_git_error_handling(self, mock_run, error_handler):
        """Test git command error handling."""
        # Test CalledProcessError
        mock_run.side_effect = subprocess.CalledProcessError(1, "git", "error output")

        result = error_handler.validate_branch_permissions()
        assert not result.passed
        assert result.severity == ErrorSeverity.CRITICAL
        assert "Git command failed" in result.message

    def test_git_timeout_handling(self, error_handler):
        """Test git command timeout handling."""
        with patch("subprocess.run") as mock_run:
            # Test TimeoutExpired
            mock_run.side_effect = subprocess.TimeoutExpired("git", 30)

            result = error_handler.validate_tag_uniqueness("v1.1.0")
            assert not result.passed
            assert "timeout" in result.message.lower()

    def test_uncommitted_changes_detection(self, error_handler, temp_repo):
        """Test detection of uncommitted changes."""
        # Create uncommitted changes
        (temp_repo / "test_file.txt").write_text("test content")

        # Mock git commands to simulate being on main branch but with uncommitted changes
        with patch("subprocess.run") as mock_run:

            def mock_git_commands(cmd, **kwargs):
                from unittest.mock import MagicMock

                result = MagicMock()
                if len(cmd) > 1 and cmd[1] == "rev-parse":
                    result.stdout = "main"
                    result.returncode = 0
                elif len(cmd) > 1 and cmd[1] == "status":
                    result.stdout = "?? test_file.txt"  # Uncommitted file
                    result.returncode = 0
                elif len(cmd) > 1 and cmd[1] == "fetch":
                    result.stdout = ""
                    result.returncode = 0
                elif len(cmd) > 1 and cmd[1] == "rev-list":
                    result.stdout = "0"  # Up to date with remote
                    result.returncode = 0
                else:
                    result.stdout = ""
                    result.returncode = 0
                return result

            mock_run.side_effect = mock_git_commands

            result = error_handler.validate_branch_permissions()
            assert not result.passed
            assert "uncommitted changes" in result.message
            assert "test_file.txt" in str(result.details)

    def test_behind_remote_detection(self, error_handler, temp_repo):
        """Test detection when local branch is behind remote."""
        with patch("subprocess.run") as mock_run:
            # Mock git fetch success
            mock_run.return_value.returncode = 0

            # Mock being behind remote
            def side_effect(*args, **kwargs):
                if "rev-list" in args[0]:
                    result = Mock()
                    result.stdout = "2"  # 2 commits behind
                    result.returncode = 0
                    return result
                elif "status" in args[0]:
                    result = Mock()
                    result.stdout = ""  # No uncommitted changes
                    result.returncode = 0
                    return result
                else:
                    result = Mock()
                    result.stdout = "main"
                    result.returncode = 0
                    return result

            mock_run.side_effect = side_effect

            result = error_handler.validate_branch_permissions()
            assert not result.passed
            assert "behind" in result.message
            assert result.details["commits_behind"] == 2

    def test_environment_variable_validation(self, error_handler):
        """Test comprehensive environment variable validation."""
        # Test with minimal valid environment
        minimal_env = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, minimal_env):
            result = error_handler.validate_secrets_and_permissions(dry_run=True)
            assert result.passed

        # Test with missing repository context (not in dry run mode)
        # Clear all environment variables to ensure clean test
        incomplete_env = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "GITHUB_ACTOR": "test-user",
            # Missing GITHUB_REPOSITORY
        }

        with patch.dict(os.environ, incomplete_env, clear=True):
            result = error_handler.validate_secrets_and_permissions(dry_run=False)
            assert not result.passed
            assert "GITHUB_REPOSITORY" in str(result.details["issues"])

    def test_command_line_interface(self, temp_repo):
        """Test command line interface functionality."""
        script_path = temp_repo.parent / "workflow_error_handler.py"

        # Copy the script to a testable location
        import shutil

        original_script = Path(__file__).parent.parent / "scripts" / "workflow_error_handler.py"
        shutil.copy(original_script, script_path)

        # Test validation command
        env_vars = {
            "GITHUB_TOKEN": "ghp_" + "x" * 36,
            "GITHUB_REPOSITORY": "test/repo",
            "GITHUB_ACTOR": "test-user",
        }

        with patch.dict(os.environ, env_vars, clear=True), patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 200

            result = subprocess.run(
                [
                    sys.executable,
                    str(script_path),
                    "--validate",
                    "--tag",
                    "v1.1.0",
                    "--dry-run",
                    "--project-root",
                    str(temp_repo),
                ],
                capture_output=True,
                text=True,
            )

            # In CI, network connectivity might fail, but that's expected
            # The important thing is that the script runs and produces output
            assert result.returncode in [0, 1]  # Allow both success and validation failure
            assert "validation" in result.stdout.lower()

    def test_error_handler_initialization(self):
        """Test error handler initialization with different parameters."""
        # Test with default project root
        handler1 = WorkflowErrorHandler()
        assert handler1.project_root == Path.cwd()

        # Test with custom project root
        custom_path = Path("/tmp/test")
        handler2 = WorkflowErrorHandler(custom_path)
        assert handler2.project_root == custom_path

        # Test validation results initialization
        assert handler1.validation_results == []
        assert handler2.validation_results == []
