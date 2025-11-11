"""Version utilities for Riveter.

This module provides utilities for extracting and managing version information
from pyproject.toml as the single source of truth.
"""

from pathlib import Path
from typing import Optional

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]


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
        return version("riveter")
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
