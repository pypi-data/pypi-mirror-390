"""CLI performance optimization system.

This module provides comprehensive performance optimizations for CLI operations
including lazy loading, intelligent caching, and startup time optimization.
"""

import functools
import importlib
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from ..cache import CacheManager
from ..logging import debug, info, warning

F = TypeVar("F", bound=Callable[..., Any])


class LazyInitializer:
    """Lazy initializer for expensive operations."""

    def __init__(self, initializer: Callable[[], Any]):
        self._initializer = initializer
        self._value = None
        self._initialized = False

    def get(self) -> Any:
        """Get the initialized value."""
        if not self._initialized:
            self._value = self._initializer()
            self._initialized = True
        return self._value

    def reset(self) -> None:
        """Reset the initializer."""
        self._value = None
        self._initialized = False


class LazyLoader:
    """Lazy loader for heavy CLI dependencies."""

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}
        self._import_times: Dict[str, float] = {}
        # Disable disk cache for CLI lazy loader to prevent hanging
        from ..cache.types import CacheConfiguration

        lazy_cache_config = CacheConfiguration(
            enable_disk_cache=False,  # Disable disk cache
            max_entries=50,  # Small memory cache
            max_size_bytes=5 * 1024 * 1024,  # 5MB max
        )
        self._cache = CacheManager(config=lazy_cache_config)

    def lazy_import(self, module_name: str, attribute: Optional[str] = None) -> Any:
        """Lazily import a module or attribute."""
        cache_key = f"lazy_import:{module_name}:{attribute or 'module'}"

        # Check cache first
        cached = self._cache.get_provider().get(cache_key)
        if cached is not None:
            return cached

        start_time = time.perf_counter()

        try:
            if module_name not in self._loaded_modules:
                module = importlib.import_module(module_name)
                self._loaded_modules[module_name] = module
            else:
                module = self._loaded_modules[module_name]

            result = getattr(module, attribute) if attribute else module

            # Cache the result
            self._cache.get_provider().set(cache_key, result, ttl=3600)  # 1 hour

            import_time = time.perf_counter() - start_time
            self._import_times[f"{module_name}.{attribute or 'module'}"] = import_time

            debug(f"Lazy loaded {module_name}.{attribute or 'module'} in {import_time:.3f}s")

            return result

        except ImportError as e:
            warning(f"Failed to lazy import {module_name}.{attribute}: {e}")
            raise

    def get_import_stats(self) -> Dict[str, float]:
        """Get import timing statistics."""
        return self._import_times.copy()


class CLICache:
    """Specialized cache for CLI operations."""

    def __init__(self):
        # Disable disk cache for CLI to prevent hanging issues
        from ..cache.types import CacheConfiguration

        cli_cache_config = CacheConfiguration(
            enable_disk_cache=False,  # Disable disk cache for CLI
            max_entries=100,  # Smaller memory cache for CLI
            max_size_bytes=10 * 1024 * 1024,  # 10MB max for CLI
        )
        self._cache_manager = CacheManager(config=cli_cache_config)
        self._session_cache: Dict[str, Any] = {}
        self._startup_cache_path = Path.home() / ".riveter" / "cli_cache"
        # Don't create the directory to avoid permission issues
        # self._startup_cache_path.mkdir(parents=True, exist_ok=True)

    def cache_command_result(
        self, command: str, args_hash: str, result: Any, ttl: int = 300
    ) -> None:
        """Cache a command result."""
        cache_key = f"cli_command:{command}:{args_hash}"
        self._cache_manager.get_provider().set(cache_key, result, ttl=ttl)

    def get_cached_command_result(self, command: str, args_hash: str) -> Optional[Any]:
        """Get a cached command result."""
        cache_key = f"cli_command:{command}:{args_hash}"
        return self._cache_manager.get_provider().get(cache_key)

    def cache_startup_data(self, key: str, data: Any) -> None:
        """Cache data that helps with startup performance."""
        self._session_cache[key] = data

        # Also persist to disk for next startup
        try:
            import pickle

            cache_file = self._startup_cache_path / f"{key}.pkl"
            with open(cache_file, "wb") as f:
                pickle.dump(data, f)
        except Exception as e:
            debug(f"Failed to persist startup cache {key}: {e}")

    def get_startup_data(self, key: str) -> Optional[Any]:
        """Get cached startup data."""
        # Check session cache first
        if key in self._session_cache:
            return self._session_cache[key]

        # Check disk cache
        try:
            import pickle

            cache_file = self._startup_cache_path / f"{key}.pkl"
            if cache_file.exists():
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)
                    self._session_cache[key] = data
                    return data
        except Exception as e:
            debug(f"Failed to load startup cache {key}: {e}")

        return None

    def clear_startup_cache(self) -> None:
        """Clear startup cache."""
        self._session_cache.clear()

        try:
            import shutil

            if self._startup_cache_path.exists():
                shutil.rmtree(self._startup_cache_path)
                self._startup_cache_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            warning(f"Failed to clear startup cache: {e}")


class StartupProfiler:
    """Profiles CLI startup performance."""

    def __init__(self):
        self._start_time = time.perf_counter()
        self._checkpoints: List[tuple[str, float, Optional[str]]] = []
        self._enabled = self._should_enable_profiling()
        self._import_tracker = ImportTracker()

    def _should_enable_profiling(self) -> bool:
        """Determine if profiling should be enabled."""
        return any(
            [
                os.getenv("RIVETER_PROFILE_STARTUP", "").lower() in ("1", "true", "yes"),
                os.getenv("RIVETER_DEBUG", "").lower() in ("1", "true", "yes"),
                "--profile" in sys.argv,
            ]
        )

    def checkpoint(self, name: str, details: Optional[str] = None) -> None:
        """Record a performance checkpoint."""
        if self._enabled:
            elapsed = time.perf_counter() - self._start_time
            self._checkpoints.append((name, elapsed, details))

    def start_import_tracking(self) -> None:
        """Start tracking imports."""
        if self._enabled:
            self._import_tracker.start()

    def stop_import_tracking(self) -> None:
        """Stop tracking imports."""
        if self._enabled:
            self._import_tracker.stop()

    def report(self) -> None:
        """Report performance metrics."""
        if not self._enabled:
            return

        total_time = time.perf_counter() - self._start_time

        print(f"\n[RIVETER STARTUP PROFILE]", file=sys.stderr)
        print(f"Total startup time: {total_time:.3f}s", file=sys.stderr)

        if self._checkpoints:
            print("\nCheckpoints:", file=sys.stderr)
            prev_time = 0.0
            for name, elapsed, details in self._checkpoints:
                delta = elapsed - prev_time
                print(f"  {name:25} {elapsed:6.3f}s (+{delta:5.3f}s)", file=sys.stderr)
                if details:
                    print(f"    {details}", file=sys.stderr)
                prev_time = elapsed

        # Report import statistics
        import_stats = self._import_tracker.get_stats()
        if import_stats:
            print(f"\nImport statistics:", file=sys.stderr)
            print(f"  Total imports: {import_stats['total_imports']}", file=sys.stderr)
            print(f"  Import time: {import_stats['total_time']:.3f}s", file=sys.stderr)

            if import_stats["slowest_imports"]:
                print("  Slowest imports:", file=sys.stderr)
                for module, import_time in import_stats["slowest_imports"][:5]:
                    print(f"    {module:30} {import_time:.3f}s", file=sys.stderr)


class ImportTracker:
    """Tracks module imports for performance analysis."""

    def __init__(self):
        self._original_import = None
        self._import_times: Dict[str, float] = {}
        self._tracking = False

    def start(self) -> None:
        """Start tracking imports."""
        if self._tracking:
            return

        self._original_import = __builtins__["__import__"]
        __builtins__["__import__"] = self._tracked_import
        self._tracking = True

    def stop(self) -> None:
        """Stop tracking imports."""
        if not self._tracking or not self._original_import:
            return

        __builtins__["__import__"] = self._original_import
        self._tracking = False

    def _tracked_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Tracked import function."""
        start_time = time.perf_counter()

        try:
            result = self._original_import(name, globals, locals, fromlist, level)
            import_time = time.perf_counter() - start_time

            # Only track significant imports
            if import_time > 0.001:  # 1ms threshold
                self._import_times[name] = import_time

            return result
        except Exception:
            # Don't interfere with import errors
            return self._original_import(name, globals, locals, fromlist, level)

    def get_stats(self) -> Dict[str, Any]:
        """Get import statistics."""
        if not self._import_times:
            return {}

        total_time = sum(self._import_times.values())
        slowest_imports = sorted(self._import_times.items(), key=lambda x: x[1], reverse=True)

        return {
            "total_imports": len(self._import_times),
            "total_time": total_time,
            "slowest_imports": slowest_imports,
            "average_time": total_time / len(self._import_times),
        }


def lazy_import_decorator(module_name: str, attribute: Optional[str] = None):
    """Decorator for lazy importing."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the lazy loader from the global instance
            loader = _get_global_lazy_loader()
            imported = loader.lazy_import(module_name, attribute)

            # Replace the function with the imported one
            if attribute:
                return imported(*args, **kwargs)
            else:
                # If no attribute specified, assume the module has a function with the same name
                func_name = func.__name__
                actual_func = getattr(imported, func_name)
                return actual_func(*args, **kwargs)

        return wrapper

    return decorator


def cached_command(ttl: int = 300):
    """Decorator for caching command results."""

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a hash of the arguments
            import hashlib
            import json

            try:
                args_str = json.dumps(
                    [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
                )
                args_hash = hashlib.md5(args_str.encode()).hexdigest()
            except (TypeError, ValueError):
                # If we can't serialize args, don't cache
                return func(*args, **kwargs)

            cache = _get_global_cli_cache()
            command_name = func.__name__

            # Try to get cached result
            cached_result = cache.get_cached_command_result(command_name, args_hash)
            if cached_result is not None:
                debug(f"Using cached result for {command_name}")
                return cached_result

            # Execute and cache result
            result = func(*args, **kwargs)
            cache.cache_command_result(command_name, args_hash, result, ttl)

            return result

        return wrapper

    return decorator


def optimize_cli_startup():
    """Apply CLI startup optimizations."""
    profiler = StartupProfiler()
    profiler.checkpoint("startup_begin")

    # Start import tracking
    profiler.start_import_tracking()
    profiler.checkpoint("import_tracking_started")

    # Pre-load commonly used modules in background
    _preload_common_modules()
    profiler.checkpoint("common_modules_preloaded")

    # Set up CLI cache
    _setup_cli_cache()
    profiler.checkpoint("cli_cache_setup")

    # Stop import tracking
    profiler.stop_import_tracking()
    profiler.checkpoint("import_tracking_stopped")

    # Register cleanup
    import atexit

    atexit.register(profiler.report)

    return profiler


def _preload_common_modules():
    """Preload commonly used modules."""
    common_modules = [
        "json",
        "os",
        "sys",
        "pathlib",
        "time",
        "hashlib",
    ]

    for module_name in common_modules:
        try:
            importlib.import_module(module_name)
        except ImportError:
            pass


def _setup_cli_cache():
    """Set up CLI caching."""
    # Temporarily disable cache setup to fix CLI hanging issue
    # TODO: Fix cache provider SQLite locking issue
    debug("CLI cache setup skipped (temporary fix for hanging issue)")
    return


# Global instances
_global_lazy_loader: Optional[LazyLoader] = None
_global_cli_cache: Optional[CLICache] = None


def _get_global_lazy_loader() -> LazyLoader:
    """Get the global lazy loader instance."""
    global _global_lazy_loader
    if _global_lazy_loader is None:
        _global_lazy_loader = LazyLoader()
    return _global_lazy_loader


def _get_global_cli_cache() -> CLICache:
    """Get the global CLI cache instance."""
    global _global_cli_cache
    if _global_cli_cache is None:
        _global_cli_cache = CLICache()
    return _global_cli_cache


class FastPathOptimizer:
    """Optimizes CLI execution paths for common operations."""

    def __init__(self):
        self._fast_paths: Dict[str, Callable] = {}
        self._usage_stats: Dict[str, int] = {}

    def register_fast_path(self, command_pattern: str, handler: Callable) -> None:
        """Register a fast path for a command pattern."""
        self._fast_paths[command_pattern] = handler
        debug(f"Registered fast path for: {command_pattern}")

    def try_fast_path(self, command: str, args: List[str]) -> Optional[Any]:
        """Try to execute a command via fast path."""
        for pattern, handler in self._fast_paths.items():
            if self._matches_pattern(command, pattern):
                self._usage_stats[pattern] = self._usage_stats.get(pattern, 0) + 1
                debug(f"Using fast path for: {command}")
                return handler(args)

        return None

    def _matches_pattern(self, command: str, pattern: str) -> bool:
        """Check if command matches pattern."""
        # Simple pattern matching - can be enhanced
        return command == pattern or pattern == "*"

    def get_usage_stats(self) -> Dict[str, int]:
        """Get fast path usage statistics."""
        return self._usage_stats.copy()


# Global fast path optimizer
_global_fast_path_optimizer: Optional[FastPathOptimizer] = None


def get_fast_path_optimizer() -> FastPathOptimizer:
    """Get the global fast path optimizer."""
    global _global_fast_path_optimizer
    if _global_fast_path_optimizer is None:
        _global_fast_path_optimizer = FastPathOptimizer()
    return _global_fast_path_optimizer


def setup_cli_performance_optimizations():
    """Set up all CLI performance optimizations."""
    profiler = optimize_cli_startup()

    # Set up fast path optimizer
    optimizer = get_fast_path_optimizer()

    # Register common fast paths
    optimizer.register_fast_path("--version", _fast_version_handler)
    optimizer.register_fast_path("--help", _fast_help_handler)

    return profiler, optimizer


def _fast_version_handler(args: List[str]) -> str:
    """Fast path handler for version command."""
    loader = _get_global_lazy_loader()
    get_version = loader.lazy_import("riveter.version", "get_version")
    return str(get_version())


def _fast_help_handler(args: List[str]) -> str:
    """Fast path handler for help command."""
    return "Riveter - Infrastructure Rule Enforcement as Code\nUse 'riveter --help' for full help."


def performance_monitor(func: F) -> F:
    """Decorator to monitor function performance."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            debug(f"Performance: {func.__name__} took {elapsed:.3f}s")

    return wrapper


def get_performance_stats() -> Dict[str, Any]:
    """Get current performance statistics."""
    loader = _get_global_lazy_loader()
    cache = _get_global_cli_cache()

    stats = {
        "import_stats": loader.get_import_stats(),
        "cache_hits": 0,  # Would need to track this in cache implementation
        "startup_time": 0.0,  # Would need to track this globally
    }

    return stats


def report_performance() -> None:
    """Report performance statistics."""
    stats = get_performance_stats()

    print("\n[RIVETER PERFORMANCE REPORT]", file=sys.stderr)

    if stats["import_stats"]:
        print("Import Statistics:", file=sys.stderr)
        for module, import_time in stats["import_stats"].items():
            print(f"  {module}: {import_time:.3f}s", file=sys.stderr)

    print(f"Cache hits: {stats['cache_hits']}", file=sys.stderr)
    print(f"Startup time: {stats['startup_time']:.3f}s", file=sys.stderr)
