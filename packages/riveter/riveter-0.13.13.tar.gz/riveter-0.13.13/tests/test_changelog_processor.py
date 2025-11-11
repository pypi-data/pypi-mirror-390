"""Tests for changelog processing functionality."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from riveter.changelog_processor import ChangelogProcessor, ChangelogSection


class TestChangelogProcessor:
    """Test cases for ChangelogProcessor class."""

    def test_read_changelog_success(self, tmp_path: Path) -> None:
        """Test successful changelog reading."""
        changelog_content = """# Changelog

## [Unreleased]

### Added
- New feature

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        content = processor.read_changelog()

        assert content == changelog_content

    def test_read_changelog_file_not_found(self, tmp_path: Path) -> None:
        """Test error when changelog file doesn't exist."""
        changelog_path = tmp_path / "CHANGELOG.md"
        processor = ChangelogProcessor(changelog_path)

        with pytest.raises(FileNotFoundError, match="Changelog not found"):
            processor.read_changelog()

    def test_parse_changelog_basic(self) -> None:
        """Test basic changelog parsing."""
        content = """# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- New feature
- Another feature

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        processor = ChangelogProcessor()
        header, sections = processor.parse_changelog(content)

        assert "# Changelog" in header
        assert "All notable changes" in header
        assert len(sections) == 2

        # Check unreleased section
        unreleased = sections[0]
        assert unreleased.version == "Unreleased"
        assert unreleased.date is None
        assert "### Added" in unreleased.content
        assert "New feature" in unreleased.content

        # Check versioned section
        versioned = sections[1]
        assert versioned.version == "1.0.0"
        assert versioned.date == "2024-01-01"
        assert "Initial release" in versioned.content

    def test_parse_changelog_empty_sections(self) -> None:
        """Test parsing changelog with empty sections."""
        content = """# Changelog

## [Unreleased]

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        processor = ChangelogProcessor()
        header, sections = processor.parse_changelog(content)

        assert len(sections) == 2
        assert sections[0].version == "Unreleased"
        assert sections[0].content.strip() == ""
        assert sections[1].version == "1.0.0"
        assert "Initial release" in sections[1].content

    def test_find_unreleased_section(self) -> None:
        """Test finding unreleased section."""
        sections = [
            ChangelogSection("Unreleased", None, "content", "## [Unreleased]"),
            ChangelogSection("1.0.0", "2024-01-01", "content", "## [1.0.0] - 2024-01-01"),
        ]

        processor = ChangelogProcessor()
        unreleased = processor.find_unreleased_section(sections)

        assert unreleased is not None
        assert unreleased.version == "Unreleased"

    def test_find_unreleased_section_not_found(self) -> None:
        """Test when unreleased section is not found."""
        sections = [ChangelogSection("1.0.0", "2024-01-01", "content", "## [1.0.0] - 2024-01-01")]

        processor = ChangelogProcessor()
        unreleased = processor.find_unreleased_section(sections)

        assert unreleased is None

    def test_create_versioned_section(self) -> None:
        """Test creating versioned section from unreleased."""
        unreleased = ChangelogSection(
            "Unreleased", None, "### Added\n- New feature", "## [Unreleased]"
        )

        processor = ChangelogProcessor()
        versioned = processor.create_versioned_section(unreleased, "1.1.0", "2024-02-01")

        assert versioned.version == "1.1.0"
        assert versioned.date == "2024-02-01"
        assert versioned.content == "### Added\n- New feature"
        assert versioned.raw_header == "## [1.1.0] - 2024-02-01"

    def test_create_empty_unreleased_section(self) -> None:
        """Test creating empty unreleased section."""
        processor = ChangelogProcessor()
        unreleased = processor.create_empty_unreleased_section()

        assert unreleased.version == "Unreleased"
        assert unreleased.date is None
        assert unreleased.content == ""
        assert unreleased.raw_header == "## [Unreleased]"

    def test_format_changelog_content(self) -> None:
        """Test formatting changelog content from sections."""
        header = "# Changelog\n\nAll notable changes."
        sections = [
            ChangelogSection("Unreleased", None, "", "## [Unreleased]"),
            ChangelogSection(
                "1.0.0", "2024-01-01", "### Added\n- Initial release", "## [1.0.0] - 2024-01-01"
            ),
        ]

        processor = ChangelogProcessor()
        content = processor.format_changelog_content(header, sections)

        expected_lines = [
            "# Changelog",
            "",
            "All notable changes.",
            "",
            "## [Unreleased]",
            "",
            "## [1.0.0] - 2024-01-01",
            "",
            "### Added",
            "- Initial release",
        ]

        assert content == "\n".join(expected_lines)

    @patch("riveter.changelog_processor.datetime")
    def test_update_changelog_for_release_with_content(self, mock_datetime, tmp_path: Path) -> None:
        """Test updating changelog for release with existing unreleased content."""
        mock_datetime.now.return_value.strftime.return_value = "2024-02-01"

        changelog_content = """# Changelog

## [Unreleased]

### Added
- New feature
- Bug fix

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        updated_content = processor.update_changelog_for_release("1.1.0")

        # Check that unreleased content was moved to versioned section
        assert "## [1.1.0] - 2024-02-01" in updated_content
        assert "### Added\n- New feature\n- Bug fix" in updated_content

        # Check that new empty unreleased section was created
        lines = updated_content.split("\n")
        unreleased_index = next(i for i, line in enumerate(lines) if "## [Unreleased]" in line)
        version_index = next(i for i, line in enumerate(lines) if "## [1.1.0]" in line)
        assert unreleased_index < version_index

    @patch("riveter.changelog_processor.datetime")
    def test_update_changelog_for_release_minimal_content(
        self, mock_datetime, tmp_path: Path
    ) -> None:
        """Test updating changelog for release with minimal unreleased content."""
        mock_datetime.now.return_value.strftime.return_value = "2024-02-01"

        changelog_content = """# Changelog

## [Unreleased]

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        updated_content = processor.update_changelog_for_release("1.1.0")

        # Check that minimal version entry was created
        assert "## [1.1.0] - 2024-02-01" in updated_content
        assert "### Changed\n- Version release" in updated_content

    def test_update_changelog_for_release_no_unreleased(self, tmp_path: Path) -> None:
        """Test error when no unreleased section found."""
        changelog_content = """# Changelog

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)

        with pytest.raises(ValueError, match="No \\[Unreleased\\] section found"):
            processor.update_changelog_for_release("1.1.0")

    def test_update_changelog_for_release_custom_date(self, tmp_path: Path) -> None:
        """Test updating changelog with custom release date."""
        changelog_content = """# Changelog

## [Unreleased]

### Added
- New feature
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        updated_content = processor.update_changelog_for_release("1.1.0", "2024-03-15")

        assert "## [1.1.0] - 2024-03-15" in updated_content

    def test_write_changelog(self, tmp_path: Path) -> None:
        """Test writing changelog content to file."""
        changelog_path = tmp_path / "CHANGELOG.md"
        content = "# Changelog\n\n## [1.0.0] - 2024-01-01"

        processor = ChangelogProcessor(changelog_path)
        processor.write_changelog(content)

        written_content = changelog_path.read_text()
        assert written_content == content

    def test_extract_release_notes_success(self, tmp_path: Path) -> None:
        """Test successful release notes extraction."""
        changelog_content = """# Changelog

## [Unreleased]

## [1.1.0] - 2024-02-01

### Added
- New feature
- Bug fix

### Changed
- Updated documentation

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        release_notes = processor.extract_release_notes("1.1.0")

        assert release_notes.version == "1.1.0"
        assert release_notes.date == "2024-02-01"
        assert "### Added" in release_notes.content
        assert "New feature" in release_notes.content
        assert "### Changed" in release_notes.content

    def test_extract_release_notes_version_not_found(self, tmp_path: Path) -> None:
        """Test error when version not found in changelog."""
        changelog_content = """# Changelog

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)

        with pytest.raises(ValueError, match="Version \\[1.1.0\\] not found"):
            processor.extract_release_notes("1.1.0")

    @patch("subprocess.run")
    def test_extract_release_notes_empty_content(self, mock_run: Mock, tmp_path: Path) -> None:
        """Test release notes extraction with empty content."""
        # Mock subprocess to prevent fallback from running
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        changelog_content = """# Changelog

## [1.1.0] - 2024-02-01

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        release_notes = processor.extract_release_notes("1.1.0")

        assert release_notes.version == "1.1.0"
        assert release_notes.date == "2024-02-01"
        assert release_notes.content == "Version release"

    def test_format_release_notes_for_github(self) -> None:
        """Test formatting release notes for GitHub."""
        processor = ChangelogProcessor()

        # Test with normal content
        content = """### Added
- New feature
- Bug fix

### Changed
- Updated docs"""

        formatted = processor._format_release_notes_for_github(content)
        expected = """### Added
- New feature
- Bug fix

### Changed
- Updated docs"""

        assert formatted == expected

    def test_format_release_notes_for_github_empty(self) -> None:
        """Test formatting empty release notes for GitHub."""
        processor = ChangelogProcessor()

        formatted = processor._format_release_notes_for_github("")
        assert formatted == "Version release"

        formatted = processor._format_release_notes_for_github("   \n  \n  ")
        assert formatted == "Version release"

    @patch("subprocess.run")
    def test_generate_fallback_release_notes_with_commits(self, mock_run: Mock) -> None:
        """Test generating fallback release notes from git commits."""
        # Mock git describe to return previous version
        # Mock git log to return commit messages
        mock_run.side_effect = [
            Mock(stdout="v1.0.0\n", returncode=0),  # git describe
            Mock(stdout="abc123 Add new feature\ndef456 Fix bug\n", returncode=0),  # git log
        ]

        processor = ChangelogProcessor()
        notes = processor.generate_fallback_release_notes("1.1.0")

        assert "## Changes" in notes
        assert "- abc123 Add new feature" in notes
        assert "- def456 Fix bug" in notes

    @patch("subprocess.run")
    def test_generate_fallback_release_notes_git_error(self, mock_run: Mock) -> None:
        """Test fallback when git commands fail."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "git")

        processor = ChangelogProcessor()
        notes = processor.generate_fallback_release_notes("1.1.0")

        assert notes == "Release 1.1.0"

    @patch("subprocess.run")
    def test_generate_fallback_release_notes_no_commits(self, mock_run: Mock) -> None:
        """Test fallback when no commits found."""
        mock_run.side_effect = [
            Mock(stdout="v1.0.0\n", returncode=0),  # git describe
            Mock(stdout="", returncode=0),  # git log (empty)
        ]

        processor = ChangelogProcessor()
        notes = processor.generate_fallback_release_notes("1.1.0")

        assert notes == "Release 1.1.0"

    @patch("subprocess.run")
    def test_extract_release_notes_with_fallback(self, mock_run: Mock, tmp_path: Path) -> None:
        """Test release notes extraction using fallback when content is minimal."""
        changelog_content = """# Changelog

## [1.1.0] - 2024-02-01

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        # Mock git commands for fallback
        mock_run.side_effect = [
            Mock(stdout="v1.0.0\n", returncode=0),  # git describe
            Mock(stdout="abc123 Add new feature\n", returncode=0),  # git log
        ]

        processor = ChangelogProcessor(changelog_path)
        release_notes = processor.extract_release_notes("1.1.0")

        assert release_notes.version == "1.1.0"
        assert release_notes.date == "2024-02-01"
        assert "## Changes" in release_notes.content
        assert "- abc123 Add new feature" in release_notes.content

    def test_process_release_complete_workflow(self, tmp_path: Path) -> None:
        """Test complete release processing workflow."""
        changelog_content = """# Changelog

## [Unreleased]

### Added
- New feature
- Bug fix

## [1.0.0] - 2024-01-01

### Added
- Initial release
"""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(changelog_content)

        processor = ChangelogProcessor(changelog_path)
        updated_content, release_notes = processor.process_release("1.1.0", "2024-02-01")

        # Check updated changelog
        assert "## [Unreleased]" in updated_content
        assert "## [1.1.0] - 2024-02-01" in updated_content
        assert "### Added\n- New feature\n- Bug fix" in updated_content

        # Check release notes
        assert release_notes.version == "1.1.0"
        assert release_notes.date == "2024-02-01"
        assert "### Added" in release_notes.content
        assert "New feature" in release_notes.content
