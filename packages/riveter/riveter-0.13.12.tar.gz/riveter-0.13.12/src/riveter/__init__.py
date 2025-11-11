"""Riveter - Infrastructure Rule Enforcement as Code."""

# Version is now managed through pyproject.toml as single source of truth
# Use get_version() from .version module for runtime version access
from .version import get_version

try:
    __version__ = get_version()
except ValueError:
    # Fallback for development/testing scenarios
    __version__ = "unknown"

# Export TOML handling utilities
from riveter.toml_handler import (
    TOMLError,
    TOMLHandler,
    TOMLReadError,
    TOMLValidationError,
    TOMLWriteError,
)

# Export version utilities
from .version import get_package_version, get_version, get_version_from_pyproject

__all__ = [
    "TOMLError",
    "TOMLHandler",
    "TOMLReadError",
    "TOMLValidationError",
    "TOMLWriteError",
    "get_version",
    "get_version_from_pyproject",
    "get_package_version",
]
