"""Version utilities for Riveter.

This module provides utilities for extracting and managing version information
from pyproject.toml as the single source of truth with comprehensive error handling
and fallback strategies.
"""

from pathlib import Path
from typing import Optional, Union

# Defer tomllib import until needed
tomllib = None


def _ensure_tomllib() -> None:
    """Ensure tomllib is imported."""
    global tomllib
    if tomllib is None:
        try:
            import tomllib as _tomllib

            tomllib = _tomllib
        except ImportError:
            try:
                import tomli as _tomllib  # type: ignore[no-redef]

                tomllib = _tomllib
            except ImportError:
                tomllib = None


def get_version_from_pyproject(project_root: Optional[Path] = None) -> str:
    """Get version from pyproject.toml as single source of truth.

    Args:
        project_root: Path to project root directory. If None, uses current directory.

    Returns:
        Version string from pyproject.toml

    Raises:
        FileNotFoundError: If pyproject.toml doesn't exist
        ValueError: If version field is missing or invalid
    """
    if project_root is None:
        project_root = Path.cwd()

    pyproject_path = project_root / "pyproject.toml"

    if not pyproject_path.exists():
        raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

    _ensure_tomllib()
    if tomllib is None:
        raise ImportError("tomllib/tomli not available. Install with: pip install tomli")

    try:
        with open(pyproject_path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        raise ValueError(f"Invalid TOML in pyproject.toml: {e}") from e

    try:
        version = data["project"]["version"]
    except KeyError as e:
        raise ValueError("Version field not found in pyproject.toml [project] section") from e

    if not isinstance(version, str):
        raise ValueError(f"Version must be a string, got {type(version)}")

    return version


def get_package_version() -> str:
    """Get version using importlib.metadata for installed packages.

    This is the preferred method for getting version in CLI and runtime contexts.

    Returns:
        Version string from package metadata

    Raises:
        ImportError: If package is not installed or importlib.metadata not available
    """
    try:
        from importlib.metadata import version
    except ImportError:
        try:
            from importlib_metadata import version
        except ImportError as e:
            raise ImportError(
                "Neither importlib.metadata nor importlib_metadata is available. "
                "Install the package or use get_version_from_pyproject() instead."
            ) from e

    try:
        result = version("riveter")
        if result is None:
            raise ImportError("Package 'riveter' not found or version is None")
        return result
    except Exception as e:
        raise ImportError(f"Could not get version for 'riveter' package: {e}") from e


def get_version(prefer_pyproject: bool = False, project_root: Optional[Path] = None) -> str:
    """Get version with fallback strategy.

    Args:
        prefer_pyproject: If True, prefer pyproject.toml over package metadata
        project_root: Path to project root directory for pyproject.toml lookup

    Returns:
        Version string

    Raises:
        ValueError: If no version can be determined
    """
    if prefer_pyproject:
        try:
            return get_version_from_pyproject(project_root)
        except (FileNotFoundError, ValueError):
            try:
                return get_package_version()
            except ImportError as e:
                raise ValueError(f"Could not determine version: {e}") from e
    else:
        try:
            return get_package_version()
        except ImportError:
            try:
                return get_version_from_pyproject(project_root)
            except (FileNotFoundError, ValueError) as e:
                raise ValueError(f"Could not determine version: {e}") from e


def is_development_version(version: str) -> bool:
    """Check if version indicates development/pre-release.

    Args:
        version: Version string to check

    Returns:
        True if version contains development indicators
    """
    dev_indicators = ["-dev", "-alpha", "-beta", "-rc", ".dev", "a", "b", "rc"]
    version_lower = version.lower()
    return any(indicator in version_lower for indicator in dev_indicators)


def compare_versions(version1: str, version2: str) -> int:
    """Compare two semantic version strings.

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2, 0 if equal, 1 if version1 > version2

    Raises:
        ValueError: If version strings are not valid semantic versions
    """
    import re

    def parse_version(version: str) -> tuple[int, int, int, str]:
        """Parse version string into components."""
        # Remove 'v' prefix if present
        if version.startswith("v"):
            version = version[1:]

        # Split on pre-release/build metadata
        core_version = version.split("-")[0].split("+")[0]

        # Extract pre-release info
        pre_release = ""
        if "-" in version:
            pre_release = version.split("-", 1)[1].split("+")[0]

        # Parse core version
        parts = core_version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid semantic version: {version}")

        try:
            major, minor, patch = map(int, parts)
        except ValueError as e:
            raise ValueError(f"Invalid semantic version components: {version}") from e

        return major, minor, patch, pre_release

    try:
        v1_parts = parse_version(version1)
        v2_parts = parse_version(version2)

        # Compare major, minor, patch
        for i in range(3):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1

        # If core versions are equal, compare pre-release
        pre1, pre2 = v1_parts[3], v2_parts[3]

        # No pre-release is greater than pre-release
        if not pre1 and pre2:
            return 1
        elif pre1 and not pre2:
            return -1
        elif not pre1 and not pre2:
            return 0
        else:
            # Both have pre-release, compare lexicographically
            return -1 if pre1 < pre2 else (1 if pre1 > pre2 else 0)

    except Exception as e:
        raise ValueError(f"Failed to compare versions '{version1}' and '{version2}': {e}") from e


def get_version_info() -> dict[str, Union[str, bool]]:
    """Get comprehensive version information.

    Returns:
        Dictionary with version details including source and development status
    """
    try:
        # Try package metadata first
        version = get_package_version()
        source = "package_metadata"
    except ImportError:
        try:
            # Fall back to pyproject.toml
            version = get_version_from_pyproject()
            source = "pyproject.toml"
        except (FileNotFoundError, ValueError) as e:
            return {
                "version": "unknown",
                "source": "none",
                "is_development": False,
                "error": str(e),
            }

    return {
        "version": version,
        "source": source,
        "is_development": is_development_version(version),
        "error": None,
    }


def validate_version_format(version: str) -> bool:
    """Validate if version string follows semantic versioning.

    Args:
        version: Version string to validate

    Returns:
        True if version is valid semantic version
    """
    import re

    # Semantic version pattern with optional pre-release and build metadata
    pattern = (
        r"^(?P<major>0|[1-9]\d*)\."
        r"(?P<minor>0|[1-9]\d*)\."
        r"(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))"
        r"?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    return bool(re.match(pattern, version))
