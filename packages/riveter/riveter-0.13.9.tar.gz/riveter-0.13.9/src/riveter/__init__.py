# type: ignore
"""Riveter - Infrastructure Rule Enforcement as Code."""

from typing import Any, Optional

from .lazy_imports import lazy_importer


# Lazy load version utilities to avoid heavy imports at package initialization
def get_version() -> str:
    """Get version with lazy loading."""
    get_version_func = lazy_importer.lazy_import("riveter.version", "get_version")
    return str(get_version_func())


def get_package_version() -> str:
    """Get package version with lazy loading."""
    get_package_version_func = lazy_importer.lazy_import("riveter.version", "get_package_version")
    return str(get_package_version_func())


def get_version_from_pyproject(project_root: str | None = None) -> str:
    """Get version from pyproject.toml with lazy loading."""
    get_version_from_pyproject_func = lazy_importer.lazy_import(
        "riveter.version", "get_version_from_pyproject"
    )
    return str(get_version_from_pyproject_func(project_root))


# Create lazy accessors for TOML classes
def _create_lazy_class(class_name: str) -> Any:
    """Create a lazy-loaded class accessor."""

    def lazy_class(*args: Any, **kwargs: Any) -> Any:
        actual_class = lazy_importer.lazy_import("riveter.toml_handler", class_name)
        return actual_class(*args, **kwargs)

    return lazy_class


# Export lazy-loaded classes as functions that return the actual classes
TOMLHandler = _create_lazy_class("TOMLHandler")
TOMLError = _create_lazy_class("TOMLError")
TOMLReadError = _create_lazy_class("TOMLReadError")
TOMLWriteError = _create_lazy_class("TOMLWriteError")
TOMLValidationError = _create_lazy_class("TOMLValidationError")

# Set version lazily only when accessed
try:
    __version__ = get_version()
except ValueError:
    # Fallback for development/testing scenarios
    __version__ = "unknown"

__all__ = [
    "TOMLError",
    "TOMLHandler",
    "TOMLReadError",
    "TOMLValidationError",
    "TOMLWriteError",
    "get_package_version",
    "get_version",
    "get_version_from_pyproject",
]
