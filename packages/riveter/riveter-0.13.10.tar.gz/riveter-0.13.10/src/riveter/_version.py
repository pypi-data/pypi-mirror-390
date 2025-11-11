"""Version handling for Riveter.

This module provides version information that works both in normal Python
environments and in PyInstaller bundles where importlib.metadata may not work.
"""

import sys

# Fallback version - should be updated by build process
__version__ = "0.11.13"


def get_version() -> str:
    """Get the version of Riveter.

    Tries multiple methods to determine the version:
    1. importlib.metadata (normal installation)
    2. Fallback to hardcoded version (PyInstaller bundle)

    Returns:
        Version string
    """
    try:
        # Try importlib.metadata first (normal installation)
        try:
            from importlib.metadata import version
        except ImportError:
            from importlib_metadata import version

        pkg_version = version("riveter")
        if pkg_version:
            return pkg_version
        else:
            # If version returns None, fall back to hardcoded
            return __version__
    except Exception:
        # Fallback to hardcoded version (PyInstaller bundle)
        return __version__


def get_version_info() -> dict[str, str]:
    """Get detailed version information.

    Returns:
        Dictionary with version details
    """
    return {
        "version": get_version(),
        "python_version": sys.version,
        "platform": sys.platform,
    }
