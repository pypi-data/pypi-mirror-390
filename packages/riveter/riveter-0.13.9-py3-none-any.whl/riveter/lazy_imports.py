# type: ignore
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
import sys
import time
import weakref
from enum import Enum
from functools import wraps
from typing import Any


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
        self._cached_modules: dict[str, Any] = {}
        self._test_mode = self._detect_test_environment()
        self._binary_mode = self._detect_binary_environment()
        self._import_times: dict[str, float] = {}
        self._import_count: dict[str, int] = {}
        self._cache_hits: dict[str, int] = {}
        self._cache_misses: dict[str, int] = {}
        self._memory_usage: dict[str, int] = {}
        self._weak_cache: weakref.WeakValueDictionary[str, Any] = weakref.WeakValueDictionary()
        self._performance_threshold = float(
            os.getenv("RIVETER_IMPORT_THRESHOLD", "0.1")
        )  # 100ms default
        self._failed_imports: set[str] = set()  # Track failed imports to avoid retries

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
        for module_name in sys.modules:
            if "test_" in module_name or module_name.endswith("_test"):
                return True

        return False

    def _detect_binary_environment(self) -> bool:
        """Detect if we're running in a PyInstaller binary environment.

        Returns:
            True if running in PyInstaller binary, False otherwise
        """
        # PyInstaller sets sys.frozen attribute
        if getattr(sys, "frozen", False):
            return True

        # Check for PyInstaller-specific paths
        if hasattr(sys, "_MEIPASS"):
            return True

        # Check executable path patterns
        if sys.executable and (
            "pyinstaller" in sys.executable.lower() or sys.executable.endswith(".exe")
        ):
            return True

        return False

    def lazy_import_with_timing(self, module_name: str, attribute: str | None = None) -> Any:
        """Enhanced lazy load with comprehensive performance tracking and memory management.

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

        # Check cache first (track cache hits)
        if cache_key in self._cached_modules:
            self._cache_hits[cache_key] = self._cache_hits.get(cache_key, 0) + 1
            self._import_count[cache_key] = self._import_count.get(cache_key, 0) + 1
            return self._cached_modules[cache_key]

        # Check weak cache for memory management
        if cache_key in self._weak_cache:
            result = self._weak_cache[cache_key]
            if result is not None:
                self._cache_hits[cache_key] = self._cache_hits.get(cache_key, 0) + 1
                # Promote back to strong cache if frequently accessed
                if self._cache_hits[cache_key] > 3:
                    self._cached_modules[cache_key] = result
                return result

        # Track cache miss
        self._cache_misses[cache_key] = self._cache_misses.get(cache_key, 0) + 1

        # Measure import time and memory
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()

        try:
            # Check if this import previously failed to avoid retries
            if cache_key in self._failed_imports:
                raise ImportError(f"Module '{module_name}' previously failed to import")

            # Use binary-aware import strategy
            if self._binary_mode:
                module = self._binary_import_module(module_name)
            else:
                module = importlib.import_module(module_name)

            # Get specific attribute if requested
            if attribute:
                if not hasattr(module, attribute):
                    raise AttributeError(f"Module '{module_name}' has no attribute '{attribute}'")
                result = getattr(module, attribute)
            else:
                result = module

            # Record performance metrics
            end_time = time.perf_counter()
            end_memory = self._get_memory_usage()

            import_time = end_time - start_time
            memory_delta = end_memory - start_memory

            self._import_times[cache_key] = import_time
            self._import_count[cache_key] = 1
            self._memory_usage[cache_key] = memory_delta

            # Log performance warnings if import is slow
            if import_time > self._performance_threshold:
                self._log_performance_warning(cache_key, import_time)

            # Binary-aware cache management
            if self._binary_mode:
                # In binary mode, prefer strong caching for better performance
                self._cached_modules[cache_key] = result
            # In Python mode, use memory-based caching strategy
            elif memory_delta > 10 * 1024 * 1024:  # 10MB threshold
                self._weak_cache[cache_key] = result
            else:
                self._cached_modules[cache_key] = result

            return result

        except ImportError as e:
            # Record failed import time
            end_time = time.perf_counter()
            import_time = end_time - start_time
            self._import_times[f"{cache_key}_FAILED"] = import_time

            # Mark as failed to avoid future retries
            self._failed_imports.add(cache_key)

            # Try fallback mechanisms for binary environments
            if self._binary_mode:
                fallback_result = self._try_binary_fallbacks(module_name, attribute)
                if fallback_result is not None:
                    self._cached_modules[cache_key] = fallback_result
                    return fallback_result

            # Provide helpful error messages for common missing dependencies
            error_msg = self._get_helpful_error_message(module_name, str(e))
            raise ImportError(error_msg) from e

    def lazy_import(self, module_name: str, attribute: str | None = None) -> Any:
        """Backward compatibility wrapper for lazy_import_with_timing."""
        return self.lazy_import_with_timing(module_name, attribute)

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
        if "hcl2" in original_error.lower():
            return (
                f"Failed to import {module_name}: Terraform parsing requires hcl2. "
                "Install with: pip install riveter[terraform]"
            )
        if "requests" in original_error.lower():
            return (
                f"Failed to import {module_name}: HTTP features require requests. "
                "Install with: pip install riveter[http]"
            )
        return f"Failed to import {module_name}: {original_error}"

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes.

        Returns:
            Current memory usage in bytes, or 0 if unavailable
        """
        try:
            import psutil

            process = psutil.Process()
            return int(process.memory_info().rss)
        except (ImportError, AttributeError):
            # Fallback to basic memory tracking if psutil not available
            return 0

    def _log_performance_warning(self, module_key: str, import_time: float) -> None:
        """Log performance warning for slow imports.

        Args:
            module_key: The module cache key
            import_time: Time taken to import in seconds
        """
        if os.getenv("RIVETER_PERFORMANCE_WARNINGS", "").lower() in ("1", "true", "yes"):
            print(
                f"Warning: Slow import detected - {module_key} took {import_time:.3f}s",
                file=sys.stderr,
            )

    def clear_cache(self) -> None:
        """Clear all cached modules and performance data.

        This is useful for testing scenarios where you want to ensure
        fresh imports or test different import scenarios.
        """
        self._cached_modules.clear()
        self._weak_cache.clear()

    def clear_performance_cache(self) -> None:
        """Clear performance metrics while keeping module cache."""
        self._import_times.clear()
        self._import_count.clear()
        self._cache_hits.clear()
        self._cache_misses.clear()
        self._memory_usage.clear()

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

    def get_cached_modules(self) -> list[str]:
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

    def get_import_metrics(self) -> dict[str, dict[str, Any]]:
        """Get comprehensive import performance metrics.

        Returns:
            Dictionary with detailed performance metrics for each module
        """
        metrics = {}
        all_keys = set(self._import_times.keys()) | set(self._import_count.keys())

        for cache_key in all_keys:
            if cache_key.endswith("_FAILED"):
                continue

            metrics[cache_key] = {
                "import_time": self._import_times.get(cache_key, 0.0),
                "access_count": self._import_count.get(cache_key, 0),
                "cache_hits": self._cache_hits.get(cache_key, 0),
                "cache_misses": self._cache_misses.get(cache_key, 0),
                "memory_usage": self._memory_usage.get(cache_key, 0),
                "cached_strong": cache_key in self._cached_modules,
                "cached_weak": cache_key in self._weak_cache,
                "hit_ratio": self._calculate_hit_ratio(cache_key),
            }
        return metrics

    def _calculate_hit_ratio(self, cache_key: str) -> float:
        """Calculate cache hit ratio for a module.

        Args:
            cache_key: The module cache key

        Returns:
            Hit ratio as a float between 0 and 1
        """
        hits = self._cache_hits.get(cache_key, 0)
        misses = self._cache_misses.get(cache_key, 0)
        total = hits + misses
        return hits / total if total > 0 else 0.0

    def get_total_import_time(self) -> float:
        """Get total time spent on imports.

        Returns:
            Total import time in seconds
        """
        return sum(time for key, time in self._import_times.items() if not key.endswith("_FAILED"))

    def get_slowest_imports(self, limit: int = 10) -> list[tuple[str, float]]:
        """Get the slowest imports.

        Args:
            limit: Maximum number of results to return

        Returns:
            List of (module_name, import_time) tuples sorted by time
        """
        import_items = [
            (key, time) for key, time in self._import_times.items() if not key.endswith("_FAILED")
        ]
        import_items.sort(key=lambda x: x[1], reverse=True)
        return import_items[:limit]

    def clear_performance_metrics(self) -> None:
        """Clear all performance tracking data."""
        self._import_times.clear()
        self._import_count.clear()
        self._cache_hits.clear()
        self._cache_misses.clear()
        self._memory_usage.clear()

    def get_cache_statistics(self) -> dict[str, Any]:
        """Get cache performance statistics.

        Returns:
            Dictionary with cache performance statistics
        """
        total_hits = sum(self._cache_hits.values())
        total_misses = sum(self._cache_misses.values())
        total_requests = total_hits + total_misses

        return {
            "total_modules_cached": len(self._cached_modules),
            "total_weak_cached": len(self._weak_cache),
            "total_cache_hits": total_hits,
            "total_cache_misses": total_misses,
            "overall_hit_ratio": total_hits / total_requests if total_requests > 0 else 0.0,
            "total_import_time": self.get_total_import_time(),
            "average_import_time": self._get_average_import_time(),
            "total_memory_usage": sum(self._memory_usage.values()),
        }

    def _get_average_import_time(self) -> float:
        """Calculate average import time across all modules.

        Returns:
            Average import time in seconds
        """
        valid_times = [
            time for key, time in self._import_times.items() if not key.endswith("_FAILED")
        ]
        return sum(valid_times) / len(valid_times) if valid_times else 0.0

    def preload_for_command(self, command: str) -> None:
        """Preload dependencies for a specific command based on priority.

        Args:
            command: The command name to preload dependencies for
        """
        if command not in COMMAND_PROFILES:
            return

        profile = COMMAND_PROFILES[command]

        # Sort dependencies by priority (critical first)
        dependencies = sorted(profile["dependencies"], key=lambda x: x[1].value)  # type: ignore[misc]

        # Preload critical and high priority dependencies
        for module_name, priority in dependencies:
            if priority in (ImportPriority.CRITICAL, ImportPriority.HIGH):
                try:
                    self.lazy_import_with_timing(module_name)
                except ImportError:
                    # Log but don't fail - some dependencies might be optional
                    if os.getenv("RIVETER_DEBUG_IMPORTS", "").lower() in ("1", "true"):
                        print(
                            f"Debug: Failed to preload {module_name} for {command}", file=sys.stderr
                        )

    def get_command_category(self, command: str) -> "CommandCategory":
        """Get the performance category for a command.

        Args:
            command: The command name

        Returns:
            CommandCategory enum value
        """
        if command in COMMAND_PROFILES:
            return COMMAND_PROFILES[command]["category"]  # type: ignore[return-value]
        return CommandCategory.MEDIUM  # Default for unknown commands

    def get_command_dependencies(self, command: str) -> list[str]:
        """Get the list of dependencies for a command.

        Args:
            command: The command name

        Returns:
            List of module names that the command depends on
        """
        if command in COMMAND_PROFILES:
            return [dep[0] for dep in COMMAND_PROFILES[command]["dependencies"]]
        return []

    def optimize_import_order(self, modules: list[str]) -> list[str]:
        """Optimize the import order based on dependency analysis and frequency.

        Args:
            modules: List of module names to optimize

        Returns:
            Optimized list of module names
        """
        # Create a scoring system based on:
        # 1. Historical import time (faster modules first for quick wins)
        # 2. Access frequency (more frequently used modules first)
        # 3. Dependency relationships

        module_scores = {}
        for module in modules:
            score = 0.0

            # Factor 1: Import time (lower is better, so invert)
            import_time = self._import_times.get(module, 0.1)  # Default 100ms
            score += 1.0 / (import_time + 0.001)  # Avoid division by zero

            # Factor 2: Access frequency (higher is better)
            access_count = self._import_count.get(module, 0)
            score += access_count * 10

            # Factor 3: Cache hit ratio (higher is better)
            hit_ratio = self._calculate_hit_ratio(module)
            score += hit_ratio * 5

            module_scores[module] = score

        # Sort by score (highest first)
        return sorted(modules, key=lambda m: module_scores.get(m, 0), reverse=True)

    def create_import_profile(self, command: str) -> dict[str, Any]:
        """Create an import profile for performance analysis.

        Args:
            command: The command name

        Returns:
            Dictionary with import profile information
        """
        if command not in COMMAND_PROFILES:
            return {"error": f"Unknown command: {command}"}

        profile = COMMAND_PROFILES[command].copy()

        # Add runtime performance data
        dependencies = [dep[0] for dep in profile["dependencies"]]
        profile["runtime_metrics"] = {
            "total_import_time": sum(self._import_times.get(dep, 0) for dep in dependencies),
            "cached_modules": [dep for dep in dependencies if dep in self._cached_modules],
            "missing_modules": [dep for dep in dependencies if dep not in self._cached_modules],
            "estimated_startup_time": self._estimate_startup_time(dependencies),
        }

        return profile

    def _estimate_startup_time(self, dependencies: list[str]) -> float:
        """Estimate startup time for a list of dependencies.

        Args:
            dependencies: List of module names

        Returns:
            Estimated startup time in seconds
        """
        total_time = 0.0
        for dep in dependencies:
            if dep in self._cached_modules:
                # Cached modules have minimal overhead
                total_time += 0.001  # 1ms overhead
            else:
                # Use historical import time or estimate
                total_time += self._import_times.get(dep, 0.05)  # Default 50ms

        return total_time

    def _binary_import_module(self, module_name: str) -> Any:
        """Import module with PyInstaller-specific optimizations.

        Args:
            module_name: The module name to import

        Returns:
            The imported module

        Raises:
            ImportError: If the module cannot be imported
        """
        # In PyInstaller, some modules might be bundled differently
        # Try direct import first
        try:
            return importlib.import_module(module_name)
        except ImportError:
            # Try alternative import paths for PyInstaller
            if "." in module_name:
                # Try importing parent module first
                parent_module = ".".join(module_name.split(".")[:-1])
                child_name = module_name.split(".")[-1]
                try:
                    parent = importlib.import_module(parent_module)
                    return getattr(parent, child_name)
                except (ImportError, AttributeError):
                    pass

            # Re-raise original error if fallbacks fail
            raise

    def _try_binary_fallbacks(self, module_name: str, attribute: str | None = None) -> Any | None:
        """Try fallback mechanisms for missing dependencies in binary environments.

        Args:
            module_name: The module name that failed to import
            attribute: Optional attribute name

        Returns:
            Fallback implementation or None if no fallback available
        """
        # Define fallbacks for common optional dependencies
        fallbacks = {
            "psutil": self._create_psutil_fallback,
            "cryptography": self._create_crypto_fallback,
            "requests": self._create_requests_fallback,
        }

        # Check if we have a fallback for this module
        for fallback_module, fallback_func in fallbacks.items():
            if fallback_module in module_name:
                try:
                    fallback = fallback_func()
                    if attribute and hasattr(fallback, attribute):
                        return getattr(fallback, attribute)
                    if not attribute:
                        return fallback
                except Exception:
                    pass

        return None

    def _create_psutil_fallback(self) -> Any:
        """Create a minimal psutil fallback for memory monitoring."""

        class PsutilFallback:
            class Process:
                def memory_info(self) -> Any:
                    class MemInfo:
                        rss = 0

                    return MemInfo()

            def __init__(self) -> None:
                pass

        return PsutilFallback()

    def _create_crypto_fallback(self) -> Any:
        """Create a minimal cryptography fallback."""

        class CryptoFallback:
            def __init__(self) -> None:
                pass

            def __getattr__(self, name: str) -> Any:
                raise ImportError(
                    f"Cryptography feature '{name}' not available in binary distribution"
                )

        return CryptoFallback()

    def _create_requests_fallback(self) -> Any:
        """Create a minimal requests fallback using urllib."""
        try:
            import urllib.error
            import urllib.request

            class RequestsFallback:
                def get(self, url: str, **kwargs: Any) -> Any:
                    try:
                        response = urllib.request.urlopen(url)

                        class Response:
                            def __init__(self, response: Any) -> None:
                                self.status_code = response.getcode()
                                self.text = response.read().decode("utf-8")
                                self.content = response.read()

                            def json(self) -> Any:
                                import json

                                return json.loads(self.text)

                        return Response(response)
                    except urllib.error.URLError as e:
                        raise ImportError(f"HTTP request failed: {e}") from e

            return RequestsFallback()
        except ImportError:
            return None

    def is_binary_mode(self) -> bool:
        """Check if running in binary mode.

        Returns:
            True if running in PyInstaller binary, False otherwise
        """
        return self._binary_mode

    def get_binary_optimization_stats(self) -> dict[str, Any]:
        """Get statistics about binary-specific optimizations.

        Returns:
            Dictionary with binary optimization statistics
        """
        return {
            "is_binary_mode": self._binary_mode,
            "failed_imports": len(self._failed_imports),
            "failed_import_list": list(self._failed_imports),
            "fallback_usage": self._count_fallback_usage(),
            "binary_cache_strategy": "strong_caching" if self._binary_mode else "memory_aware",
        }

    def _count_fallback_usage(self) -> int:
        """Count how many fallback implementations are in use."""
        fallback_count = 0
        for module in self._cached_modules.values():
            if hasattr(module, "__class__") and "Fallback" in module.__class__.__name__:
                fallback_count += 1
        return fallback_count


# Global instance for use throughout the application
lazy_importer = LazyImporter()


def safe_lazy_import(module_name: str, attribute: str | None = None) -> Any:
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


def get_optional_feature(module_name: str, feature_name: str) -> Any | None:
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


# Enhanced command dependency mapping with categories and priorities


class CommandCategory(Enum):
    """Command categories for import optimization."""

    LIGHTWEIGHT = "lightweight"  # <500ms target
    MEDIUM = "medium"  # <1s target
    HEAVYWEIGHT = "heavyweight"  # <2s target


class ImportPriority(Enum):
    """Import priority levels for optimization."""

    CRITICAL = 1  # Must be loaded immediately
    HIGH = 2  # Load early in command execution
    MEDIUM = 3  # Load when needed
    LOW = 4  # Load lazily or cache for future use


# Command profiles with categories, dependencies, and import priorities
COMMAND_PROFILES = {
    # Lightweight commands - minimal dependencies
    "version": {
        "category": CommandCategory.LIGHTWEIGHT,
        "dependencies": [],
        "optional_deps": [],
        "max_startup_time": 0.5,
    },
    "help": {
        "category": CommandCategory.LIGHTWEIGHT,
        "dependencies": [],
        "optional_deps": [],
        "max_startup_time": 0.5,
    },
    "create_config": {
        "category": CommandCategory.LIGHTWEIGHT,
        "dependencies": [],
        "optional_deps": [],
        "max_startup_time": 0.5,
    },
    # Medium complexity commands
    "list_rule_packs": {
        "category": CommandCategory.MEDIUM,
        "dependencies": [("riveter.rule_packs", ImportPriority.CRITICAL)],
        "optional_deps": [],
        "max_startup_time": 1.0,
    },
    "list_installed_packs": {
        "category": CommandCategory.MEDIUM,
        "dependencies": [("riveter.rule_packs", ImportPriority.CRITICAL)],
        "optional_deps": [],
        "max_startup_time": 1.0,
    },
    "create_rule_pack_template": {
        "category": CommandCategory.MEDIUM,
        "dependencies": [("riveter.rule_packs", ImportPriority.CRITICAL)],
        "optional_deps": [],
        "max_startup_time": 1.0,
    },
    "validate_rules": {
        "category": CommandCategory.MEDIUM,
        "dependencies": [("riveter.rule_linter", ImportPriority.CRITICAL)],
        "optional_deps": [],
        "max_startup_time": 1.0,
    },
    # Heavyweight commands - complex dependencies
    "scan": {
        "category": CommandCategory.HEAVYWEIGHT,
        "dependencies": [
            ("riveter.extract_config", ImportPriority.CRITICAL),  # hcl2 dependency
            ("riveter.scanner", ImportPriority.CRITICAL),
            ("riveter.rule_packs", ImportPriority.HIGH),
            ("riveter.rule_filter", ImportPriority.HIGH),
        ],
        "optional_deps": [
            ("riveter.performance", ImportPriority.MEDIUM),
            ("riveter.formatters", ImportPriority.LOW),
        ],
        "max_startup_time": 2.0,
    },
    "install_rule_pack": {
        "category": CommandCategory.HEAVYWEIGHT,
        "dependencies": [
            ("riveter.rule_distribution", ImportPriority.CRITICAL),  # cryptography dependency
            ("riveter.rule_repository", ImportPriority.CRITICAL),  # requests dependency
        ],
        "optional_deps": [],
        "max_startup_time": 2.0,
    },
    "update_rule_packs": {
        "category": CommandCategory.HEAVYWEIGHT,
        "dependencies": [
            ("riveter.rule_distribution", ImportPriority.CRITICAL),
            ("riveter.rule_repository", ImportPriority.CRITICAL),
        ],
        "optional_deps": [],
        "max_startup_time": 2.0,
    },
    "validate_rule_pack": {
        "category": CommandCategory.HEAVYWEIGHT,
        "dependencies": [
            ("riveter.rule_packs", ImportPriority.CRITICAL),
            ("riveter.rule_linter", ImportPriority.CRITICAL),
        ],
        "optional_deps": [],
        "max_startup_time": 2.0,
    },
}

# Legacy compatibility mapping
COMMAND_DEPENDENCIES = {
    cmd: [dep[0] for dep in profile["dependencies"]] for cmd, profile in COMMAND_PROFILES.items()
}
