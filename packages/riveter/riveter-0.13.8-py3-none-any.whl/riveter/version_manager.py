"""Version management functionality for automated releases."""

import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from riveter.toml_handler import TOMLHandler, TOMLReadError, TOMLValidationError, TOMLWriteError
from riveter.version import get_version_from_pyproject, validate_version_format


class VersionType(Enum):
    """Version bump types following semantic versioning."""

    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"


@dataclass
class VersionInfo:
    """Version information container."""

    current: str
    new: str
    tag: str
    major: int
    minor: int
    patch: int


class VersionManager:
    """Manages version parsing, calculation, and updates."""

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """Initialize version manager.

        Args:
            project_root: Path to project root directory. If None, uses current directory.
        """
        self.project_root = project_root or Path.cwd()
        self.pyproject_path = self.project_root / "pyproject.toml"

    def read_current_version(self) -> str:
        """Read current version from pyproject.toml using centralized version utilities.

        Returns:
            Current version string.

        Raises:
            FileNotFoundError: If pyproject.toml doesn't exist.
            ValueError: If version field is missing or invalid.
        """
        try:
            version = get_version_from_pyproject(self.project_root)
            self._validate_version_format(version)
            return version
        except (FileNotFoundError, ValueError) as e:
            raise e

    def _validate_version_format(self, version: str) -> None:
        """Validate semantic version format.

        Args:
            version: Version string to validate.

        Raises:
            ValueError: If version format is invalid.
        """
        if not validate_version_format(version):
            raise ValueError(f"Invalid semantic version format: {version}")

    def _parse_version_components(self, version: str) -> tuple[int, int, int]:
        """Parse version string into major, minor, patch components.

        Args:
            version: Version string to parse.

        Returns:
            Tuple of (major, minor, patch) as integers.
        """
        # Extract just the core version numbers (ignore pre-release/build metadata)
        core_version = version.split("-")[0].split("+")[0]
        parts = core_version.split(".")

        if len(parts) != 3:
            raise ValueError(f"Version must have exactly 3 parts (major.minor.patch): {version}")

        try:
            major, minor, patch = map(int, parts)
        except ValueError as e:
            raise ValueError(f"Version parts must be integers: {e}") from e

        return major, minor, patch

    def calculate_next_version(self, current_version: str, version_type: VersionType) -> str:
        """Calculate next version based on current version and bump type.

        Args:
            current_version: Current semantic version string.
            version_type: Type of version bump to perform.

        Returns:
            New version string.
        """
        major, minor, patch = self._parse_version_components(current_version)

        if version_type == VersionType.MAJOR:
            major += 1
            minor = 0
            patch = 0
        elif version_type == VersionType.MINOR:
            minor += 1
            patch = 0
        elif version_type == VersionType.PATCH:
            patch += 1
        else:
            raise ValueError(f"Unknown version type: {version_type}")

        return f"{major}.{minor}.{patch}"

    def create_version_info(self, version_type: VersionType) -> VersionInfo:
        """Create version information for a release.

        Args:
            version_type: Type of version bump to perform.

        Returns:
            VersionInfo object with current and new version details.
        """
        current_version = self.read_current_version()
        new_version = self.calculate_next_version(current_version, version_type)
        major, minor, patch = self._parse_version_components(new_version)

        return VersionInfo(
            current=current_version,
            new=new_version,
            tag=f"v{new_version}",
            major=major,
            minor=minor,
            patch=patch,
        )

    def update_pyproject_version(self, new_version: str) -> None:
        """Update version in pyproject.toml file using TOML handler.

        Args:
            new_version: New version string to set.

        Raises:
            FileNotFoundError: If pyproject.toml doesn't exist.
            ValueError: If unable to update version.
        """
        if not self.pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {self.pyproject_path}")

        try:
            # Create backup before modifying
            handler = TOMLHandler(self.pyproject_path)
            handler.read()
            handler.backup()

            # Verify version field exists before updating
            try:
                handler.validate_structure(required_keys=["project.version"])
            except TOMLValidationError as e:
                raise ValueError("Failed to find and update version field in pyproject.toml") from e

            # Update version using TOML handler
            handler.set_value("project.version", new_version)

            # Write with formatting preservation
            if handler._parsed_data is not None:
                handler.write(handler._parsed_data, preserve_formatting=True)
            else:
                raise ValueError("TOML data not loaded")

            # Verify the update was successful
            handler.read()
            updated_version = handler.get_value("project.version")

            if updated_version != new_version:
                # Restore from backup if verification fails
                handler.restore_from_backup()
                raise ValueError(
                    f"Version update verification failed: expected {new_version}, "
                    f"got {updated_version}"
                )

        except (TOMLReadError, TOMLWriteError) as e:
            raise ValueError(f"Failed to update version in pyproject.toml: {e}") from e

    def check_tag_exists(self, tag: str) -> bool:
        """Check if a git tag already exists.

        Args:
            tag: Git tag to check.

        Returns:
            True if tag exists, False otherwise.

        Raises:
            RuntimeError: If git repository is not available or accessible.
        """
        try:
            # First check if we're in a git repository
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                check=True,
            )

            # Check local tags
            result = subprocess.run(
                ["git", "tag", "-l", tag],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                return True

            # Also check remote tags to be thorough
            try:
                subprocess.run(
                    ["git", "fetch", "--tags", "--quiet"],
                    cwd=self.project_root,
                    capture_output=True,
                    check=True,
                    timeout=30,  # Add timeout for network operations
                )

                result = subprocess.run(
                    ["git", "tag", "-l", tag],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    check=True,
                )

                return bool(result.stdout.strip())

            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                # If remote fetch fails, just use local check
                return False

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git repository not available or accessible: {e}") from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Git operation timed out - check network connectivity") from e

    def create_git_tag(self, tag: str, message: Optional[str] = None) -> None:
        """Create a git tag.

        Args:
            tag: Tag name to create.
            message: Optional tag message. If None, uses default message.

        Raises:
            ValueError: If tag already exists or tag name is invalid.
            RuntimeError: If git operations fail.
        """
        # Validate tag name format
        if not re.match(r"^v?\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?$", tag):
            raise ValueError(f"Invalid tag format: {tag}. Expected format: v1.2.3 or 1.2.3")

        if self.check_tag_exists(tag):
            raise ValueError(f"Git tag '{tag}' already exists")

        tag_message = message or f"Release {tag}"

        try:
            # Ensure we have a clean working directory
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )

            if result.stdout.strip():
                raise RuntimeError(
                    "Cannot create tag with uncommitted changes in working directory"
                )

            # Create annotated tag
            subprocess.run(
                ["git", "tag", "-a", tag, "-m", tag_message],
                cwd=self.project_root,
                check=True,
                timeout=30,
            )

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create git tag '{tag}': {e}") from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(f"Git tag creation timed out for tag '{tag}'") from e

    def update_version_and_tag(
        self, version_type: VersionType, tag_message: Optional[str] = None
    ) -> VersionInfo:
        """Update version in pyproject.toml and create git tag.

        Args:
            version_type: Type of version bump to perform.
            tag_message: Optional custom tag message.

        Returns:
            VersionInfo object with version details.

        Raises:
            ValueError: If tag already exists or update fails.
        """
        version_info = self.create_version_info(version_type)

        # Validate tag doesn't exist before making any changes
        if self.check_tag_exists(version_info.tag):
            raise ValueError(f"Git tag '{version_info.tag}' already exists")

        # Update pyproject.toml
        self.update_pyproject_version(version_info.new)

        # Create git tag
        self.create_git_tag(version_info.tag, tag_message)

        return version_info

    def get_version_history(self, limit: int = 10) -> List[str]:
        """Get version history from git tags.

        Args:
            limit: Maximum number of versions to return

        Returns:
            List of version tags in reverse chronological order

        Raises:
            RuntimeError: If git operations fail
        """
        try:
            result = subprocess.run(
                ["git", "tag", "-l", "--sort=-version:refname", "v*"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )

            tags = result.stdout.strip().split("\n") if result.stdout.strip() else []
            return tags[:limit]

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get version history: {e}") from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError("Git operation timed out while getting version history") from e

    def get_latest_version_tag(self) -> Optional[str]:
        """Get the latest version tag from git.

        Returns:
            Latest version tag or None if no tags exist

        Raises:
            RuntimeError: If git operations fail
        """
        try:
            history = self.get_version_history(limit=1)
            return history[0] if history else None
        except RuntimeError:
            return None

    def is_version_ahead_of_tag(self, version: str) -> bool:
        """Check if given version is ahead of the latest git tag.

        Args:
            version: Version string to check

        Returns:
            True if version is ahead of latest tag

        Raises:
            RuntimeError: If git operations fail
        """
        latest_tag = self.get_latest_version_tag()
        if not latest_tag:
            return True  # No tags exist, so any version is ahead

        # Remove 'v' prefix from tag for comparison
        latest_version = latest_tag[1:] if latest_tag.startswith("v") else latest_tag

        from riveter.version import compare_versions

        try:
            return compare_versions(version, latest_version) > 0
        except ValueError:
            # If comparison fails, assume version is ahead
            return True

    def suggest_next_version(self, current_version: Optional[str] = None) -> Dict[str, str]:
        """Suggest next version numbers for different bump types.

        Args:
            current_version: Current version, reads from pyproject.toml if None

        Returns:
            Dictionary with suggested versions for each bump type

        Raises:
            ValueError: If current version is invalid
        """
        if current_version is None:
            current_version = self.read_current_version()

        suggestions = {}
        for version_type in VersionType:
            try:
                suggestions[version_type.value] = self.calculate_next_version(
                    current_version, version_type
                )
            except ValueError as e:
                suggestions[version_type.value] = f"Error: {e}"

        return suggestions

    def dry_run_version_update(self, version_type: VersionType) -> Dict[str, Any]:
        """Perform a dry run of version update without making changes.

        Args:
            version_type: Type of version bump to simulate

        Returns:
            Dictionary with simulation results

        Raises:
            ValueError: If version update would fail
        """
        try:
            version_info = self.create_version_info(version_type)

            # Check if tag already exists
            tag_exists = self.check_tag_exists(version_info.tag)

            # Check if version is ahead of latest tag
            is_ahead = self.is_version_ahead_of_tag(version_info.new)

            return {
                "current_version": version_info.current,
                "new_version": version_info.new,
                "tag": version_info.tag,
                "tag_exists": tag_exists,
                "is_ahead_of_latest": is_ahead,
                "would_succeed": not tag_exists and is_ahead,
                "issues": (
                    []
                    if not tag_exists and is_ahead
                    else [
                        f"Tag {version_info.tag} already exists" if tag_exists else None,
                        (
                            f"Version {version_info.new} is not ahead of latest tag"
                            if not is_ahead
                            else None
                        ),
                    ]
                ),
            }

        except Exception as e:
            return {
                "current_version": None,
                "new_version": None,
                "tag": None,
                "tag_exists": False,
                "is_ahead_of_latest": False,
                "would_succeed": False,
                "issues": [str(e)],
            }
