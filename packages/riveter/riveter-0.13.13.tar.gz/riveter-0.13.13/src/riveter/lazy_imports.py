"""Lazy import utilities for Riveter CLI performance optimization.

This module provides lazy loading capabilities to defer heavy dependency imports
until they are actually needed, significantly improving CLI startup time for
basic operations like --version and --help.

The LazyImporter class handles:
- Deferred module loading with caching
- Test environment compatibility
- Error handling for missing dependencies
- Pre-loading capabilities for test environments

Example:
    Basic usage:
        from .lazy_imports import lazy_importer

        # Lazy load a module
        hcl2 = lazy_importer.lazy_import('hcl2')

        # Lazy load a specific attribute
        extract_config = lazy_importer.lazy_import(
            'riveter.extract_config', 'extract_terraform_config'
        )

    Command-specific usage:
        @requires_heavy_deps('riveter.extract_config', 'riveter.scanner')
        def scan_command():
            # Heavy imports happen here only when scan is called
            pass
"""

import importlib
import os
from functools import wraps
from typing import Any, Dict, List, Optional


class LazyImporter:
    """Manages lazy loading of heavy dependencies with test compatibility.

    This class provides a centralized way to defer module imports until they
    are actually needed, while maintaining compatibility with existing test
    suites that may expect modules to be available immediately.

    Features:
    - Module caching to avoid repeated imports
    - Test environment detection and pre-loading
    - Clear error handling for missing dependencies
    - Cache management for testing scenarios
    """

    def __init__(self) -> None:
        """Initialize the lazy importer with empty cache and test detection."""
        self._cached_modules: Dict[str, Any] = {}
        self._test_mode = self._detect_test_environment()

    def _detect_test_environment(self) -> bool:
        """Detect if we're running in a test environment.

        Returns:
            True if running in test environment, False otherwise
        """
        # Check for pytest
        if os.getenv("PYTEST_CURRENT_TEST") is not None:
            return True

        # Check for other test indicators
        if "pytest" in os.getenv("_", "").lower():
            return True

        # Check if we're being imported by a test module
        import sys

        for module_name in sys.modules:
            if "test_" in module_name or module_name.endswith("_test"):
                return True

        return False

    def lazy_import(self, module_name: str, attribute: Optional[str] = None) -> Any:
        """Lazy load a module or module attribute with caching.

        Args:
            module_name: The name of the module to import (e.g., 'riveter.extract_config')
            attribute: Optional specific attribute to get from the module

        Returns:
            The imported module or attribute

        Raises:
            ImportError: If the module cannot be imported
            AttributeError: If the specified attribute doesn't exist
        """
        cache_key = f"{module_name}.{attribute}" if attribute else module_name

        # Return cached version if available
        if cache_key in self._cached_modules:
            return self._cached_modules[cache_key]

        try:
            # Import the module
            module = importlib.import_module(module_name)

            # Get specific attribute if requested
            if attribute:
                if not hasattr(module, attribute):
                    raise AttributeError(f"Module '{module_name}' has no attribute '{attribute}'")
                result = getattr(module, attribute)
            else:
                result = module

            # Cache the result
            self._cached_modules[cache_key] = result
            return result

        except ImportError as e:
            # Provide helpful error messages for common missing dependencies
            error_msg = self._get_helpful_error_message(module_name, str(e))
            raise ImportError(error_msg) from e

    def _get_helpful_error_message(self, module_name: str, original_error: str) -> str:
        """Generate helpful error messages for common import failures.

        Args:
            module_name: The module that failed to import
            original_error: The original error message

        Returns:
            A more helpful error message with installation suggestions
        """
        if "cryptography" in original_error.lower():
            return (
                f"Failed to import {module_name}: Cryptography features require "
                "additional dependencies. Install with: pip install riveter[crypto]"
            )
        elif "hcl2" in original_error.lower():
            return (
                f"Failed to import {module_name}: Terraform parsing requires hcl2. "
                "Install with: pip install riveter[terraform]"
            )
        elif "requests" in original_error.lower():
            return (
                f"Failed to import {module_name}: HTTP features require requests. "
                "Install with: pip install riveter[http]"
            )
        else:
            return f"Failed to import {module_name}: {original_error}"

    def clear_cache(self) -> None:
        """Clear all cached modules.

        This is useful for testing scenarios where you want to ensure
        fresh imports or test different import scenarios.
        """
        self._cached_modules.clear()

    def preload_all_dependencies(self) -> None:
        """Pre-load all heavy dependencies for test compatibility.

        In test environments, this method can be called to pre-load all
        the heavy modules that tests might expect to be available,
        maintaining compatibility with existing test suites.
        """
        if not self._test_mode:
            return

        # List of heavy modules that should be pre-loaded in test environments
        heavy_modules = [
            "riveter.extract_config",
            "riveter.rule_distribution",
            "riveter.rule_repository",
            "riveter.performance",
            "riveter.scanner",
            "riveter.rule_packs",
            "riveter.rule_filter",
            "riveter.rule_linter",
            "riveter.formatters",
            "riveter.reporter",
        ]

        for module in heavy_modules:
            try:
                self.lazy_import(module)
            except ImportError:
                # Skip modules that aren't available - this is expected
                # in some test environments or when optional dependencies
                # are not installed
                pass

    def get_cached_modules(self) -> List[str]:
        """Get list of currently cached module names.

        Returns:
            List of cached module/attribute names
        """
        return list(self._cached_modules.keys())

    def is_test_mode(self) -> bool:
        """Check if running in test mode.

        Returns:
            True if in test environment, False otherwise
        """
        return self._test_mode


# Global instance for use throughout the application
lazy_importer = LazyImporter()


def safe_lazy_import(module_name: str, attribute: Optional[str] = None) -> Any:
    """Safely import with clear error messages and graceful handling.

    This is a convenience function that wraps lazy_importer.lazy_import
    with additional error handling and user-friendly messages.

    Args:
        module_name: The name of the module to import
        attribute: Optional specific attribute to get from the module

    Returns:
        The imported module or attribute

    Raises:
        RuntimeError: With user-friendly error message if import fails
    """
    try:
        return lazy_importer.lazy_import(module_name, attribute)
    except ImportError as e:
        raise RuntimeError(str(e)) from e


def get_optional_feature(module_name: str, feature_name: str) -> Optional[Any]:
    """Get optional features that can gracefully degrade.

    This function attempts to import optional features and returns None
    if they're not available, allowing the application to continue with
    reduced functionality rather than failing completely.

    Args:
        module_name: The name of the module to import
        feature_name: The specific feature/attribute to get

    Returns:
        The feature if available, None otherwise
    """
    try:
        return lazy_importer.lazy_import(module_name, feature_name)
    except ImportError:
        return None


def requires_heavy_deps(*deps: str) -> Any:
    """Decorator to lazy load heavy dependencies for commands.

    This decorator ensures that heavy dependencies are loaded just before
    the decorated function is executed, rather than at module import time.

    Args:
        *deps: Module names to lazy load before function execution

    Returns:
        Decorator function

    Example:
        @requires_heavy_deps('riveter.extract_config', 'riveter.scanner')
        def scan_command():
            # Heavy imports are loaded here, just before execution
            pass
    """

    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Load dependencies just before function execution
            for dep in deps:
                try:
                    lazy_importer.lazy_import(dep)
                except ImportError as e:
                    # Convert to RuntimeError with helpful message
                    raise RuntimeError(f"Required dependency '{dep}' not available: {e}") from e

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Command dependency mapping for reference
COMMAND_DEPENDENCIES = {
    "scan": [
        "riveter.extract_config",  # hcl2 dependency
        "riveter.scanner",
        "riveter.performance",
        "riveter.rule_packs",
        "riveter.rule_filter",
    ],
    "install_rule_pack": [
        "riveter.rule_distribution",  # cryptography dependency
        "riveter.rule_repository",  # requests dependency
    ],
    "update_rule_packs": ["riveter.rule_distribution", "riveter.rule_repository"],
    "validate_rule_pack": ["riveter.rule_packs", "riveter.rule_linter"],
    "validate_rules": ["riveter.rule_linter"],
    "list_rule_packs": ["riveter.rule_packs"],
    "list_installed_packs": ["riveter.rule_packs"],
    "create_rule_pack_template": ["riveter.rule_packs"],
    # Basic commands have no heavy dependencies
    "version": [],
    "help": [],
    "create_config": [],
}
