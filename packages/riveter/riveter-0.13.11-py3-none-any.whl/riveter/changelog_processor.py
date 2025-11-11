"""Changelog processing functionality for automated releases."""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class ChangelogSection:
    """Represents a section in the changelog."""

    version: str
    date: Optional[str]
    content: str
    raw_header: str


@dataclass
class ReleaseNotes:
    """Release notes extracted from changelog."""

    version: str
    content: str
    date: str


class ChangelogProcessor:
    """Processes changelog files for automated releases."""

    def __init__(self, changelog_path: Optional[Path] = None) -> None:
        """Initialize changelog processor.

        Args:
            changelog_path: Path to CHANGELOG.md file. If None, uses CHANGELOG.md
                in current directory.
        """
        self.changelog_path = changelog_path or Path("CHANGELOG.md")

    def read_changelog(self) -> str:
        """Read changelog content from file.

        Returns:
            Changelog content as string.

        Raises:
            FileNotFoundError: If changelog file doesn't exist.
            PermissionError: If changelog file cannot be read.
            UnicodeDecodeError: If changelog file has encoding issues.
        """
        if not self.changelog_path.exists():
            raise FileNotFoundError(f"Changelog not found at {self.changelog_path}")

        try:
            return self.changelog_path.read_text(encoding="utf-8")
        except PermissionError as e:
            raise PermissionError(f"Cannot read changelog file {self.changelog_path}: {e}") from e
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(
                e.encoding,
                e.object,
                e.start,
                e.end,
                f"Changelog file {self.changelog_path} has encoding issues: {e.reason}",
            ) from e

    def parse_changelog(self, content: str) -> Tuple[str, List[ChangelogSection]]:
        """Parse changelog content into header and sections.

        Args:
            content: Changelog content to parse.

        Returns:
            Tuple of (header_content, list_of_sections).
        """
        lines = content.split("\n")
        sections = []
        current_section = None
        header_lines = []
        in_header = True

        for line in lines:
            # Check if this is a version header (## [version] or ## [Unreleased])
            version_match = re.match(r"^##\s+\[([^\]]+)\](?:\s*-\s*(.+))?", line)

            if version_match:
                # Save previous section if exists
                if current_section is not None:
                    sections.append(current_section)

                in_header = False
                version = version_match.group(1)
                date = version_match.group(2)

                current_section = ChangelogSection(
                    version=version, date=date, content="", raw_header=line
                )
            elif current_section is not None:
                # Add content to current section
                if current_section.content:
                    current_section.content += "\n" + line
                else:
                    current_section.content = line
            elif in_header:
                # Still in header section
                header_lines.append(line)

        # Add the last section
        if current_section is not None:
            sections.append(current_section)

        header = "\n".join(header_lines).rstrip()
        return header, sections

    def find_unreleased_section(
        self, sections: List[ChangelogSection]
    ) -> Optional[ChangelogSection]:
        """Find the unreleased section in changelog sections.

        Args:
            sections: List of changelog sections.

        Returns:
            Unreleased section if found, None otherwise.
        """
        for section in sections:
            if section.version.lower() == "unreleased":
                return section
        return None

    def create_versioned_section(
        self, unreleased_section: ChangelogSection, version: str, release_date: str
    ) -> ChangelogSection:
        """Create a versioned section from unreleased content.

        Args:
            unreleased_section: The unreleased section to convert.
            version: New version number.
            release_date: Release date in YYYY-MM-DD format.

        Returns:
            New versioned section.
        """
        return ChangelogSection(
            version=version,
            date=release_date,
            content=unreleased_section.content,
            raw_header=f"## [{version}] - {release_date}",
        )

    def create_empty_unreleased_section(self) -> ChangelogSection:
        """Create a new empty unreleased section.

        Returns:
            Empty unreleased section.
        """
        return ChangelogSection(
            version="Unreleased", date=None, content="", raw_header="## [Unreleased]"
        )

    def format_changelog_content(self, header: str, sections: List[ChangelogSection]) -> str:
        """Format changelog sections back into content string.

        Args:
            header: Changelog header content.
            sections: List of changelog sections.

        Returns:
            Formatted changelog content.
        """
        content_parts = [header]

        for section in sections:
            content_parts.append("")  # Empty line before section
            content_parts.append(section.raw_header)

            if section.content.strip():
                content_parts.append("")  # Empty line after header
                content_parts.append(section.content.rstrip())

        return "\n".join(content_parts)

    def update_changelog_for_release(self, version: str, release_date: Optional[str] = None) -> str:
        """Update changelog for a new release.

        Args:
            version: New version number.
            release_date: Release date in YYYY-MM-DD format. If None, uses current date.

        Returns:
            Updated changelog content.

        Raises:
            ValueError: If no unreleased section found or other processing errors.
        """
        if release_date is None:
            release_date = datetime.now().strftime("%Y-%m-%d")

        content = self.read_changelog()
        header, sections = self.parse_changelog(content)

        # Find unreleased section
        unreleased_section = self.find_unreleased_section(sections)
        if unreleased_section is None:
            raise ValueError("No [Unreleased] section found in changelog")

        # Remove unreleased section from list
        sections = [s for s in sections if s.version.lower() != "unreleased"]

        # Create versioned section from unreleased content
        if unreleased_section.content.strip():
            versioned_section = self.create_versioned_section(
                unreleased_section, version, release_date
            )
            sections.insert(0, versioned_section)
        else:
            # Create minimal version entry if no unreleased changes
            minimal_section = ChangelogSection(
                version=version,
                date=release_date,
                content="### Changed\n- Version release",
                raw_header=f"## [{version}] - {release_date}",
            )
            sections.insert(0, minimal_section)

        # Add new empty unreleased section at the beginning
        empty_unreleased = self.create_empty_unreleased_section()
        sections.insert(0, empty_unreleased)

        return self.format_changelog_content(header, sections)

    def write_changelog(self, content: str) -> None:
        """Write updated changelog content to file.

        Args:
            content: Updated changelog content.

        Raises:
            PermissionError: If changelog file cannot be written.
            OSError: If there are filesystem issues.
        """
        try:
            # Create backup before writing
            if self.changelog_path.exists():
                backup_path = self.changelog_path.with_suffix(".md.backup")
                backup_path.write_text(
                    self.changelog_path.read_text(encoding="utf-8"), encoding="utf-8"
                )

            self.changelog_path.write_text(content, encoding="utf-8")

            # Verify the write was successful
            if not self.changelog_path.exists():
                raise OSError(f"Failed to write changelog to {self.changelog_path}")

        except PermissionError as e:
            raise PermissionError(
                f"Cannot write to changelog file {self.changelog_path}: {e}"
            ) from e
        except OSError as e:
            raise OSError(f"Filesystem error writing changelog {self.changelog_path}: {e}") from e

    def extract_release_notes(self, version: str, content: Optional[str] = None) -> ReleaseNotes:
        """Extract release notes for a specific version.

        Args:
            version: Version to extract notes for.
            content: Optional changelog content. If None, reads from file.

        Returns:
            ReleaseNotes object with extracted content.

        Raises:
            ValueError: If version section not found.
        """
        if content is None:
            content = self.read_changelog()

        header, sections = self.parse_changelog(content)

        # Find the section for the specified version
        target_section = None
        for section in sections:
            if section.version == version:
                target_section = section
                break

        if target_section is None:
            raise ValueError(f"Version [{version}] not found in changelog")

        # Format release notes content for GitHub
        notes_content = self._format_release_notes_for_github(target_section.content)

        # If content is minimal, try to generate from git commits
        if notes_content == "Version release":
            fallback_notes = self.generate_fallback_release_notes(version)
            if fallback_notes != f"Release {version}":
                notes_content = fallback_notes

        return ReleaseNotes(
            version=version, content=notes_content, date=target_section.date or "Unknown"
        )

    def _format_release_notes_for_github(self, content: str) -> str:
        """Format changelog content for GitHub release description.

        Args:
            content: Raw changelog content for a version.

        Returns:
            Formatted content suitable for GitHub release.
        """
        content = content.strip()

        # Handle minimal or missing content
        if not content:
            return "Version release"

        # For GitHub, preserve the original formatting but clean up extra whitespace
        lines = content.split("\n")
        formatted_lines = []

        for line in lines:
            # Keep empty lines but strip trailing whitespace from non-empty lines
            if line.strip():
                formatted_lines.append(line.rstrip())
            else:
                formatted_lines.append("")

        # Remove trailing empty lines
        while formatted_lines and not formatted_lines[-1]:
            formatted_lines.pop()

        if not formatted_lines:
            return "Version release"

        return "\n".join(formatted_lines)

    def generate_fallback_release_notes(
        self, version: str, previous_version: Optional[str] = None
    ) -> str:
        """Generate fallback release notes when changelog content is minimal.

        Args:
            version: Current version being released.
            previous_version: Previous version for commit range. If None, uses git to find it.

        Returns:
            Generated release notes content.
        """
        import subprocess

        try:
            # If no previous version specified, try to get the latest tag
            if previous_version is None:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--abbrev=0"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                previous_version = result.stdout.strip()

            # Get commit messages between versions
            commit_range = f"{previous_version}..HEAD" if previous_version else "HEAD"
            result = subprocess.run(
                ["git", "log", commit_range, "--oneline", "--no-merges"],
                capture_output=True,
                text=True,
                check=True,
            )

            commits = result.stdout.strip().split("\n")
            if commits and commits[0]:
                formatted_commits = []
                for commit in commits[:10]:  # Limit to 10 most recent commits
                    if commit.strip():
                        # Format as bullet point
                        formatted_commits.append(f"- {commit.strip()}")

                if formatted_commits:
                    return "## Changes\n\n" + "\n".join(formatted_commits)

        except subprocess.CalledProcessError:
            # Git command failed, fall back to minimal content
            pass

        return f"Release {version}"

    def process_release(
        self, version: str, release_date: Optional[str] = None
    ) -> Tuple[str, ReleaseNotes]:
        """Process changelog for release and extract release notes.

        Args:
            version: New version number.
            release_date: Release date in YYYY-MM-DD format. If None, uses current date.

        Returns:
            Tuple of (updated_changelog_content, release_notes).
        """
        # Update changelog
        updated_content = self.update_changelog_for_release(version, release_date)

        # Extract release notes from updated content
        release_notes = self.extract_release_notes(version, updated_content)

        return updated_content, release_notes
