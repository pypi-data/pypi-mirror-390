"""Tests for version management functionality."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from riveter.version_manager import VersionManager, VersionType


class TestVersionManager:
    """Test cases for VersionManager class."""

    def test_read_current_version_success(self, tmp_path: Path) -> None:
        """Test successful version reading from pyproject.toml."""
        pyproject_content = """
[project]
name = "test-project"
version = "1.2.3"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        manager = VersionManager(tmp_path)
        version = manager.read_current_version()

        assert version == "1.2.3"

    def test_read_current_version_file_not_found(self, tmp_path: Path) -> None:
        """Test error when pyproject.toml doesn't exist."""
        manager = VersionManager(tmp_path)

        with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
            manager.read_current_version()

    def test_read_current_version_missing_version_field(self, tmp_path: Path) -> None:
        """Test error when version field is missing."""
        pyproject_content = """
[project]
name = "test-project"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        manager = VersionManager(tmp_path)

        with pytest.raises(ValueError, match="Version field not found"):
            manager.read_current_version()

    def test_read_current_version_invalid_type(self, tmp_path: Path) -> None:
        """Test error when version is not a string."""
        pyproject_content = """
[project]
name = "test-project"
version = 123
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        manager = VersionManager(tmp_path)

        with pytest.raises(ValueError, match="Version must be a string"):
            manager.read_current_version()

    @pytest.mark.parametrize(
        "version",
        [
            "1.2.3",
            "0.0.1",
            "10.20.30",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0+build.1",
            "1.0.0-alpha+build.1",
        ],
    )
    def test_validate_version_format_valid(self, version: str) -> None:
        """Test validation of valid semantic version formats."""
        manager = VersionManager()
        # Should not raise any exception
        manager._validate_version_format(version)

    @pytest.mark.parametrize(
        "version", ["1.2", "1.2.3.4", "1.2.a", "a.b.c", "1.2.3-", "1.2.3+", ""]
    )
    def test_validate_version_format_invalid(self, version: str) -> None:
        """Test validation of invalid semantic version formats."""
        manager = VersionManager()

        with pytest.raises(ValueError, match="Invalid semantic version format"):
            manager._validate_version_format(version)

    @pytest.mark.parametrize(
        "version,expected",
        [
            ("1.2.3", (1, 2, 3)),
            ("0.0.1", (0, 0, 1)),
            ("10.20.30", (10, 20, 30)),
            ("1.0.0-alpha", (1, 0, 0)),
            ("1.0.0+build", (1, 0, 0)),
        ],
    )
    def test_parse_version_components(self, version: str, expected: tuple[int, int, int]) -> None:
        """Test parsing version components."""
        manager = VersionManager()
        result = manager._parse_version_components(version)
        assert result == expected

    def test_parse_version_components_invalid(self) -> None:
        """Test parsing invalid version components."""
        manager = VersionManager()

        with pytest.raises(ValueError, match="Version must have exactly 3 parts"):
            manager._parse_version_components("1.2")

        with pytest.raises(ValueError, match="Version parts must be integers"):
            manager._parse_version_components("1.2.a")

    @pytest.mark.parametrize(
        "current,version_type,expected",
        [
            ("1.2.3", VersionType.PATCH, "1.2.4"),
            ("1.2.3", VersionType.MINOR, "1.3.0"),
            ("1.2.3", VersionType.MAJOR, "2.0.0"),
            ("0.0.1", VersionType.PATCH, "0.0.2"),
            ("0.1.0", VersionType.MINOR, "0.2.0"),
            ("1.0.0", VersionType.MAJOR, "2.0.0"),
        ],
    )
    def test_calculate_next_version(
        self, current: str, version_type: VersionType, expected: str
    ) -> None:
        """Test version calculation logic."""
        manager = VersionManager()
        result = manager.calculate_next_version(current, version_type)
        assert result == expected

    def test_create_version_info(self, tmp_path: Path) -> None:
        """Test creation of VersionInfo object."""
        pyproject_content = """
[project]
name = "test-project"
version = "1.2.3"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        manager = VersionManager(tmp_path)
        version_info = manager.create_version_info(VersionType.MINOR)

        assert version_info.current == "1.2.3"
        assert version_info.new == "1.3.0"
        assert version_info.tag == "v1.3.0"
        assert version_info.major == 1
        assert version_info.minor == 3
        assert version_info.patch == 0

    def test_update_pyproject_version(self, tmp_path: Path) -> None:
        """Test updating version in pyproject.toml."""
        pyproject_content = """[build-system]
requires = ["hatchling"]

[project]
name = "test-project"
version = "1.2.3"
description = "Test project"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        manager = VersionManager(tmp_path)
        manager.update_pyproject_version("1.3.0")

        updated_content = pyproject_path.read_text()
        assert 'version = "1.3.0"' in updated_content
        assert 'version = "1.2.3"' not in updated_content
        # Ensure other content is preserved
        assert 'name = "test-project"' in updated_content
        assert '"hatchling"' in updated_content  # Check for hatchling regardless of formatting

    def test_update_pyproject_version_file_not_found(self, tmp_path: Path) -> None:
        """Test error when pyproject.toml doesn't exist for update."""
        manager = VersionManager(tmp_path)

        with pytest.raises(FileNotFoundError, match="pyproject.toml not found"):
            manager.update_pyproject_version("1.3.0")

    def test_update_pyproject_version_no_version_field(self, tmp_path: Path) -> None:
        """Test error when version field is not found for update."""
        pyproject_content = """[project]
name = "test-project"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        manager = VersionManager(tmp_path)

        with pytest.raises(ValueError, match="Failed to find and update version field"):
            manager.update_pyproject_version("1.3.0")

    @patch("subprocess.run")
    def test_check_tag_exists_true(self, mock_run: Mock) -> None:
        """Test checking for existing git tag."""
        mock_run.return_value = Mock(stdout="v1.2.3\n", returncode=0)

        manager = VersionManager()
        result = manager.check_tag_exists("v1.2.3")

        assert result is True
        # Check that the tag lookup call was made (may be called after git-dir check)
        mock_run.assert_any_call(
            ["git", "tag", "-l", "v1.2.3"],
            cwd=manager.project_root,
            capture_output=True,
            text=True,
            check=True,
        )

    @patch("subprocess.run")
    def test_check_tag_exists_false(self, mock_run: Mock) -> None:
        """Test checking for non-existing git tag."""
        mock_run.return_value = Mock(stdout="", returncode=0)

        manager = VersionManager()
        result = manager.check_tag_exists("v1.2.3")

        assert result is False

    @patch("subprocess.run")
    def test_check_tag_exists_git_error(self, mock_run: Mock) -> None:
        """Test handling git command error when checking tags."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        manager = VersionManager()

        with pytest.raises(RuntimeError, match="Git repository not available or accessible"):
            manager.check_tag_exists("v1.2.3")

    @patch("subprocess.run")
    def test_create_git_tag_success(self, mock_run: Mock) -> None:
        """Test successful git tag creation."""
        # Mock multiple git calls that happen in create_git_tag
        mock_run.side_effect = [
            Mock(stdout="", returncode=0),  # git rev-parse --git-dir (check if git repo)
            Mock(stdout="", returncode=0),  # git tag -l v1.2.3 (check_tag_exists - local)
            Mock(stdout="", returncode=0),  # git fetch --tags (check_tag_exists - remote)
            Mock(stdout="", returncode=0),  # git tag -l v1.2.3 (check_tag_exists - after fetch)
            Mock(stdout="", returncode=0),  # git status --porcelain (check working dir)
            Mock(returncode=0),  # git tag -a (create tag)
        ]

        manager = VersionManager()
        manager.create_git_tag("v1.2.3", "Release v1.2.3")

        assert mock_run.call_count >= 2  # At least tag check and tag creation
        mock_run.assert_any_call(
            ["git", "tag", "-a", "v1.2.3", "-m", "Release v1.2.3"],
            cwd=manager.project_root,
            check=True,
            timeout=30,
        )

    @patch("subprocess.run")
    def test_create_git_tag_default_message(self, mock_run: Mock) -> None:
        """Test git tag creation with default message."""
        mock_run.side_effect = [
            Mock(stdout="", returncode=0),  # git rev-parse --git-dir (check if git repo)
            Mock(stdout="", returncode=0),  # git tag -l v1.2.3 (check_tag_exists - local)
            Mock(stdout="", returncode=0),  # git fetch --tags (check_tag_exists - remote)
            Mock(stdout="", returncode=0),  # git tag -l v1.2.3 (check_tag_exists - after fetch)
            Mock(stdout="", returncode=0),  # git status --porcelain (check working dir)
            Mock(returncode=0),  # git tag -a (create tag)
        ]

        manager = VersionManager()
        manager.create_git_tag("v1.2.3")

        mock_run.assert_any_call(
            ["git", "tag", "-a", "v1.2.3", "-m", "Release v1.2.3"],
            cwd=manager.project_root,
            check=True,
            timeout=30,
        )

    @patch("subprocess.run")
    def test_create_git_tag_already_exists(self, mock_run: Mock) -> None:
        """Test error when trying to create existing git tag."""
        mock_run.return_value = Mock(stdout="v1.2.3\n", returncode=0)

        manager = VersionManager()

        with pytest.raises(ValueError, match="Git tag 'v1.2.3' already exists"):
            manager.create_git_tag("v1.2.3")

    def test_update_version_and_tag_success(self, tmp_path: Path) -> None:
        """Test complete version update and tagging process."""
        pyproject_content = """[project]
name = "test-project"
version = "1.2.3"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch("subprocess.run") as mock_run:
            # Mock all subprocess calls for check_tag_exists (called twice) and create_git_tag
            mock_run.side_effect = [
                # First check_tag_exists call in update_version_and_tag
                Mock(stdout="", returncode=0),  # git rev-parse --git-dir
                Mock(stdout="", returncode=0),  # git tag -l v1.3.0 (local)
                Mock(stdout="", returncode=0),  # git fetch --tags
                Mock(stdout="", returncode=0),  # git tag -l v1.3.0 (after fetch)
                # Second check_tag_exists call in create_git_tag
                Mock(stdout="", returncode=0),  # git rev-parse --git-dir
                Mock(stdout="", returncode=0),  # git tag -l v1.3.0 (local)
                Mock(stdout="", returncode=0),  # git fetch --tags
                Mock(stdout="", returncode=0),  # git tag -l v1.3.0 (after fetch)
                # create_git_tag calls
                Mock(stdout="", returncode=0),  # git status --porcelain
                Mock(returncode=0),  # git tag -a
            ]

            manager = VersionManager(tmp_path)
            version_info = manager.update_version_and_tag(VersionType.MINOR)

            assert version_info.current == "1.2.3"
            assert version_info.new == "1.3.0"
            assert version_info.tag == "v1.3.0"

            # Check that pyproject.toml was updated
            updated_content = pyproject_path.read_text()
            assert 'version = "1.3.0"' in updated_content

    def test_update_version_and_tag_existing_tag(self, tmp_path: Path) -> None:
        """Test error when tag already exists during update."""
        pyproject_content = """[project]
name = "test-project"
version = "1.2.3"
"""
        pyproject_path = tmp_path / "pyproject.toml"
        pyproject_path.write_text(pyproject_content)

        with patch("subprocess.run") as mock_run:
            # Mock check_tag_exists to return that tag exists
            mock_run.return_value = Mock(stdout="v1.3.0\n", returncode=0)

            manager = VersionManager(tmp_path)

            with pytest.raises(ValueError, match="Git tag 'v1.3.0' already exists"):
                manager.update_version_and_tag(VersionType.MINOR)

            # Ensure pyproject.toml was not modified
            content = pyproject_path.read_text()
            assert 'version = "1.2.3"' in content
