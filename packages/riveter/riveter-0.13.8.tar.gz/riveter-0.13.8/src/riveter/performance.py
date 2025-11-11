"""Performance optimization utilities for Riveter with CLI focus.

This module provides comprehensive performance monitoring, profiling, and optimization
utilities specifically designed for CLI operations and command execution.
"""

import hashlib
import json
import os
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import psutil

from .logging import debug, info
from .logging import performance as log_performance
from .rules import Rule
from .scanner import ValidationResult, validate_resources


@dataclass
class CLIPerformanceMetrics:
    """Performance metrics for CLI operations."""

    startup_time: float = 0.0
    command_execution_time: float = 0.0
    memory_peak_mb: float = 0.0
    memory_current_mb: float = 0.0
    cpu_percent: float = 0.0
    io_read_bytes: int = 0
    io_write_bytes: int = 0
    file_operations: int = 0
    network_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    validation_time: float = 0.0
    parsing_time: float = 0.0
    output_time: float = 0.0


@dataclass
class PerformanceBenchmark:
    """Performance benchmark data for regression detection."""

    operation: str
    baseline_time: float
    current_time: float
    memory_baseline_mb: float
    memory_current_mb: float
    regression_threshold: float = 0.2  # 20% regression threshold
    timestamp: float = field(default_factory=time.time)

    @property
    def time_regression_percent(self) -> float:
        """Calculate time regression percentage."""
        if self.baseline_time == 0:
            return 0.0
        return (self.current_time - self.baseline_time) / self.baseline_time

    @property
    def memory_regression_percent(self) -> float:
        """Calculate memory regression percentage."""
        if self.memory_baseline_mb == 0:
            return 0.0
        return (self.memory_current_mb - self.memory_baseline_mb) / self.memory_baseline_mb

    @property
    def has_time_regression(self) -> bool:
        """Check if there's a significant time regression."""
        return self.time_regression_percent > self.regression_threshold

    @property
    def has_memory_regression(self) -> bool:
        """Check if there's a significant memory regression."""
        return self.memory_regression_percent > self.regression_threshold


class CLIPerformanceMonitor:
    """Performance monitor specifically designed for CLI operations."""

    def __init__(self, enable_detailed_monitoring: bool = False):
        """Initialize CLI performance monitor.

        Args:
            enable_detailed_monitoring: Enable detailed system monitoring
        """
        self.enable_detailed_monitoring = enable_detailed_monitoring
        self.metrics = CLIPerformanceMetrics()
        self.operation_timers: Dict[str, float] = {}
        self.benchmarks: List[PerformanceBenchmark] = []
        self.process = psutil.Process()
        self._startup_time = time.time()
        self._initial_memory = self._get_memory_usage()
        self._initial_io = self._get_io_counters()

        debug("CLI performance monitor initialized", detailed_monitoring=enable_detailed_monitoring)

    def record_startup_complete(self) -> None:
        """Record CLI startup completion time."""
        self.metrics.startup_time = (time.time() - self._startup_time) * 1000  # Convert to ms
        log_performance(
            "CLI startup completed",
            duration=self.metrics.startup_time,
            operation="cli_startup",
        )

    def start_command_execution(self, command: str) -> None:
        """Start timing command execution."""
        self.operation_timers["command_execution"] = time.time()
        self.operation_timers[f"command_{command}"] = time.time()
        debug("Started timing command execution", command=command)

    def end_command_execution(self, command: str) -> None:
        """End timing command execution."""
        if "command_execution" in self.operation_timers:
            self.metrics.command_execution_time = (
                time.time() - self.operation_timers["command_execution"]
            ) * 1000

        command_key = f"command_{command}"
        if command_key in self.operation_timers:
            command_time = (time.time() - self.operation_timers[command_key]) * 1000
            log_performance(
                f"Command '{command}' execution completed",
                duration=command_time,
                operation=f"command_{command}",
            )
            del self.operation_timers[command_key]

        if "command_execution" in self.operation_timers:
            del self.operation_timers["command_execution"]

    @contextmanager
    def time_operation(self, operation: str):
        """Context manager for timing operations."""
        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            yield
        finally:
            duration = (time.time() - start_time) * 1000
            end_memory = self._get_memory_usage()
            memory_delta = end_memory - start_memory

            # Store operation-specific metrics
            if operation == "validation":
                self.metrics.validation_time = duration
            elif operation == "parsing":
                self.metrics.parsing_time = duration
            elif operation == "output":
                self.metrics.output_time = duration

            log_performance(
                f"Operation '{operation}' completed",
                duration=duration,
                memory_delta_mb=memory_delta,
                operation=operation,
            )

    def update_system_metrics(self) -> None:
        """Update current system performance metrics."""
        if not self.enable_detailed_monitoring:
            return

        try:
            # Memory metrics
            self.metrics.memory_current_mb = self._get_memory_usage()
            if self.metrics.memory_current_mb > self.metrics.memory_peak_mb:
                self.metrics.memory_peak_mb = self.metrics.memory_current_mb

            # CPU metrics
            self.metrics.cpu_percent = self.process.cpu_percent()

            # I/O metrics
            current_io = self._get_io_counters()
            if current_io and self._initial_io:
                self.metrics.io_read_bytes = current_io.read_bytes - self._initial_io.read_bytes
                self.metrics.io_write_bytes = current_io.write_bytes - self._initial_io.write_bytes

        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            debug("Failed to update system metrics", error=str(e))

    def record_file_operation(self) -> None:
        """Record a file operation."""
        self.metrics.file_operations += 1

    def record_network_operation(self) -> None:
        """Record a network operation."""
        self.metrics.network_operations += 1

    def record_cache_hit(self) -> None:
        """Record a cache hit."""
        self.metrics.cache_hits += 1

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.metrics.cache_misses += 1

    def create_benchmark(
        self,
        operation: str,
        baseline_time: float,
        baseline_memory: float,
        regression_threshold: float = 0.2,
    ) -> PerformanceBenchmark:
        """Create a performance benchmark for regression detection."""
        current_time = getattr(self.metrics, f"{operation}_time", 0.0)
        current_memory = self.metrics.memory_current_mb

        benchmark = PerformanceBenchmark(
            operation=operation,
            baseline_time=baseline_time,
            current_time=current_time,
            memory_baseline_mb=baseline_memory,
            memory_current_mb=current_memory,
            regression_threshold=regression_threshold,
        )

        self.benchmarks.append(benchmark)

        if benchmark.has_time_regression or benchmark.has_memory_regression:
            log_performance(
                f"Performance regression detected for '{operation}'",
                operation=operation,
                time_regression_percent=benchmark.time_regression_percent * 100,
                memory_regression_percent=benchmark.memory_regression_percent * 100,
                baseline_time=baseline_time,
                current_time=current_time,
            )

        return benchmark

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        self.update_system_metrics()

        cache_total = self.metrics.cache_hits + self.metrics.cache_misses
        cache_hit_rate = (self.metrics.cache_hits / cache_total * 100) if cache_total > 0 else 0.0

        return {
            "startup_time_ms": self.metrics.startup_time,
            "command_execution_time_ms": self.metrics.command_execution_time,
            "validation_time_ms": self.metrics.validation_time,
            "parsing_time_ms": self.metrics.parsing_time,
            "output_time_ms": self.metrics.output_time,
            "memory_peak_mb": self.metrics.memory_peak_mb,
            "memory_current_mb": self.metrics.memory_current_mb,
            "cpu_percent": self.metrics.cpu_percent,
            "io_read_bytes": self.metrics.io_read_bytes,
            "io_write_bytes": self.metrics.io_write_bytes,
            "file_operations": self.metrics.file_operations,
            "network_operations": self.metrics.network_operations,
            "cache_hit_rate_percent": cache_hit_rate,
            "cache_hits": self.metrics.cache_hits,
            "cache_misses": self.metrics.cache_misses,
            "regressions_detected": len(
                [b for b in self.benchmarks if b.has_time_regression or b.has_memory_regression]
            ),
        }

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def _get_io_counters(self) -> Optional[Any]:
        """Get current I/O counters."""
        try:
            return self.process.io_counters()
        except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
            return None


class PerformanceProfiler:
    """Advanced performance profiler for detailed analysis."""

    def __init__(self, profile_file: Optional[Path] = None):
        """Initialize performance profiler.

        Args:
            profile_file: Optional file to save profiling data
        """
        self.profile_file = profile_file
        self.profiles: Dict[str, Dict[str, Any]] = {}
        self.active_profiles: Dict[str, Dict[str, Any]] = {}

    @contextmanager
    def profile_operation(self, operation: str, details: Optional[Dict[str, Any]] = None):
        """Context manager for profiling operations with detailed metrics."""
        profile_data = {
            "operation": operation,
            "start_time": time.time(),
            "start_memory": self._get_memory_usage(),
            "details": details or {},
        }

        self.active_profiles[operation] = profile_data

        try:
            yield profile_data
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()

            profile_data.update(
                {
                    "end_time": end_time,
                    "duration_ms": (end_time - profile_data["start_time"]) * 1000,
                    "end_memory": end_memory,
                    "memory_delta_mb": end_memory - profile_data["start_memory"],
                    "peak_memory": max(profile_data["start_memory"], end_memory),
                }
            )

            self.profiles[operation] = profile_data
            del self.active_profiles[operation]

            if self.profile_file:
                self._save_profile_data()

    def get_profile_summary(self) -> Dict[str, Any]:
        """Get profiling summary."""
        if not self.profiles:
            return {}

        total_time = sum(p["duration_ms"] for p in self.profiles.values())
        total_memory = sum(p["memory_delta_mb"] for p in self.profiles.values())

        return {
            "total_operations": len(self.profiles),
            "total_time_ms": total_time,
            "total_memory_delta_mb": total_memory,
            "operations": {
                name: {
                    "duration_ms": profile["duration_ms"],
                    "memory_delta_mb": profile["memory_delta_mb"],
                    "percentage_of_total": (
                        (profile["duration_ms"] / total_time * 100) if total_time > 0 else 0
                    ),
                }
                for name, profile in self.profiles.items()
            },
        }

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    def _save_profile_data(self) -> None:
        """Save profiling data to file."""
        if not self.profile_file:
            return

        try:
            self.profile_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.profile_file, "w") as f:
                json.dump(self.profiles, f, indent=2, default=str)
        except Exception as e:
            debug("Failed to save profile data", error=str(e))


class ParallelProcessor:
    """Handles parallel processing of rule validation."""

    def __init__(self, max_workers: int | None = None):
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker threads. If None, uses CPU count.
        """
        self.max_workers = max_workers or os.cpu_count()
        debug("Parallel processor initialized", max_workers=self.max_workers)

    def validate_resources_parallel(
        self, rules: list[Rule], resources: list[dict[str, Any]], batch_size: int = 10
    ) -> list[ValidationResult]:
        """Validate resources against rules using parallel processing.

        Args:
            rules: List of rules to validate against
            resources: List of resources to validate
            batch_size: Number of resources to process per batch

        Returns:
            List of validation results
        """
        start_time = time.time()
        info(
            "Starting parallel validation",
            rule_count=len(rules),
            resource_count=len(resources),
            max_workers=self.max_workers,
            batch_size=batch_size,
        )

        # Create resource batches for optimal parallel processing
        resource_batches = self._create_resource_batches(resources, batch_size)

        all_results = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit validation tasks for each batch
            future_to_batch = {
                executor.submit(self._validate_batch, rules, batch): batch_idx
                for batch_idx, batch in enumerate(resource_batches)
            }

            # Collect results as they complete
            for future in as_completed(future_to_batch):
                batch_idx = future_to_batch[future]
                try:
                    batch_results = future.result()
                    all_results.extend(batch_results)
                    debug(
                        "Batch validation completed",
                        batch_index=batch_idx,
                        result_count=len(batch_results),
                    )
                except Exception as e:
                    debug(
                        "Batch validation failed",
                        batch_index=batch_idx,
                        error=str(e),
                    )
                    raise

        execution_time = time.time() - start_time
        info(
            "Parallel validation completed",
            total_results=len(all_results),
            execution_time=execution_time,
            batches_processed=len(resource_batches),
        )

        return all_results

    def _create_resource_batches(
        self, resources: list[dict[str, Any]], batch_size: int
    ) -> list[list[dict[str, Any]]]:
        """Create batches of resources for parallel processing.

        Args:
            resources: List of resources to batch
            batch_size: Size of each batch

        Returns:
            List of resource batches
        """
        batches = []
        for i in range(0, len(resources), batch_size):
            batch = resources[i : i + batch_size]
            batches.append(batch)

        debug("Resource batches created", batch_count=len(batches), batch_size=batch_size)
        return batches

    def _validate_batch(
        self, rules: list[Rule], resources: list[dict[str, Any]]
    ) -> list[ValidationResult]:
        """Validate a batch of resources against rules.

        Args:
            rules: List of rules to validate against
            resources: Batch of resources to validate

        Returns:
            List of validation results for this batch
        """
        # Use the existing validate_resources function for each batch
        return validate_resources(rules, resources)


class ResourceCache:
    """Caches parsed Terraform configurations for improved performance."""

    def __init__(self, cache_dir: str | None = None, max_size_mb: int = 100):
        """Initialize resource cache.

        Args:
            cache_dir: Directory to store cache files. If None, uses system temp dir.
            max_size_mb: Maximum cache size in megabytes
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".riveter" / "cache"

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024

        debug("Resource cache initialized", cache_dir=str(self.cache_dir), max_size_mb=max_size_mb)

    def get_cache_key(self, file_path: str) -> str:
        """Generate cache key for a file.

        Args:
            file_path: Path to the file

        Returns:
            Cache key string
        """
        # Include file path and modification time in cache key
        file_stat = os.stat(file_path)
        key_data = f"{file_path}:{file_stat.st_mtime}:{file_stat.st_size}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_cached_config(self, file_path: str) -> dict[str, Any] | None:
        """Get cached configuration for a file.

        Args:
            file_path: Path to the Terraform file

        Returns:
            Cached configuration or None if not found/invalid
        """
        try:
            cache_key = self.get_cache_key(file_path)
            cache_file = self.cache_dir / f"{cache_key}.pkl"

            if not cache_file.exists():
                debug("Cache miss", file_path=file_path, cache_key=cache_key)
                return None

            # Load cached data
            with open(cache_file, "rb") as f:
                cached_data = pickle.load(f)

            # Verify cache is still valid
            if cached_data.get("cache_key") != cache_key:
                debug("Cache key mismatch", file_path=file_path, cache_key=cache_key)
                cache_file.unlink()  # Remove invalid cache
                return None

            debug("Cache hit", file_path=file_path, cache_key=cache_key)
            return cached_data.get("config")  # type: ignore[no-any-return]

        except Exception as e:
            debug("Cache read error", file_path=file_path, error=str(e))
            return None

    def cache_parsed_config(self, file_path: str, config: dict[str, Any]) -> None:
        """Cache parsed configuration for a file.

        Args:
            file_path: Path to the Terraform file
            config: Parsed configuration to cache
        """
        try:
            cache_key = self.get_cache_key(file_path)
            cache_file = self.cache_dir / f"{cache_key}.pkl"

            # Prepare cache data
            cache_data = {
                "cache_key": cache_key,
                "file_path": file_path,
                "timestamp": time.time(),
                "config": config,
            }

            # Write to cache
            with open(cache_file, "wb") as f:
                pickle.dump(cache_data, f)

            debug("Configuration cached", file_path=file_path, cache_key=cache_key)

            # Clean up old cache files if needed
            self._cleanup_cache()

        except Exception as e:
            debug("Cache write error", file_path=file_path, error=str(e))

    def invalidate_cache(self, file_path: str) -> None:
        """Invalidate cache for a specific file.

        Args:
            file_path: Path to the file to invalidate
        """
        try:
            cache_key = self.get_cache_key(file_path)
            cache_file = self.cache_dir / f"{cache_key}.pkl"

            if cache_file.exists():
                cache_file.unlink()
                debug("Cache invalidated", file_path=file_path, cache_key=cache_key)

        except Exception as e:
            debug("Cache invalidation error", file_path=file_path, error=str(e))

    def clear_cache(self) -> None:
        """Clear all cached files."""
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            debug("Cache cleared", cache_dir=str(self.cache_dir))

        except Exception as e:
            debug("Cache clear error", error=str(e))

    def _cleanup_cache(self) -> None:
        """Clean up old cache files if cache size exceeds limit."""
        try:
            cache_files = list(self.cache_dir.glob("*.pkl"))
            total_size = sum(f.stat().st_size for f in cache_files)

            if total_size <= self.max_size_bytes:
                return

            # Sort by modification time (oldest first)
            cache_files.sort(key=lambda f: f.stat().st_mtime)

            # Remove oldest files until under size limit
            while total_size > self.max_size_bytes and cache_files:
                oldest_file = cache_files.pop(0)
                file_size = oldest_file.stat().st_size
                oldest_file.unlink()
                total_size -= file_size
                debug("Removed old cache file", file_path=str(oldest_file), size_bytes=file_size)

            debug(
                "Cache cleanup completed",
                remaining_files=len(cache_files),
                total_size_mb=total_size / 1024 / 1024,
            )

        except Exception as e:
            debug("Cache cleanup error", error=str(e))


class IncrementalScanner:
    """Supports incremental scanning of changed resources."""

    def __init__(self, baseline_file: str | None = None):
        """Initialize incremental scanner.

        Args:
            baseline_file: Path to baseline file for comparison
        """
        self.baseline_file = baseline_file or ".riveter_baseline.json"
        debug("Incremental scanner initialized", baseline_file=self.baseline_file)

    def load_baseline(self) -> dict[str, Any] | None:
        """Load baseline configuration from file.

        Returns:
            Baseline configuration or None if not found
        """
        try:
            if not os.path.exists(self.baseline_file):
                debug("Baseline file not found", baseline_file=self.baseline_file)
                return None

            with open(self.baseline_file) as f:
                baseline = json.load(f)

            debug(
                "Baseline loaded",
                baseline_file=self.baseline_file,
                resource_count=len(baseline.get("resources", [])),
            )
            return baseline  # type: ignore[no-any-return]

        except Exception as e:
            debug("Baseline load error", baseline_file=self.baseline_file, error=str(e))
            return None

    def save_baseline(self, config: dict[str, Any]) -> None:
        """Save current configuration as baseline.

        Args:
            config: Configuration to save as baseline
        """
        try:
            baseline_data = {
                "timestamp": time.time(),
                "resources": config.get("resources", []),
                "version": "1.0",
            }

            with open(self.baseline_file, "w") as f:
                json.dump(baseline_data, f, indent=2)

            debug(
                "Baseline saved",
                baseline_file=self.baseline_file,
                resource_count=len(baseline_data["resources"]),
            )

        except Exception as e:
            debug("Baseline save error", baseline_file=self.baseline_file, error=str(e))

    def get_changed_resources(
        self, current_resources: list[dict[str, Any]], baseline: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Get resources that have changed since baseline.

        Args:
            current_resources: Current list of resources
            baseline: Baseline to compare against (loads from file if None)

        Returns:
            List of changed resources
        """
        if baseline is None:
            baseline = self.load_baseline()

        if baseline is None:
            debug("No baseline available, returning all resources")
            return current_resources

        baseline_resources = baseline.get("resources", [])

        # Create lookup for baseline resources
        baseline_lookup = {}
        for resource in baseline_resources:
            resource_key = self._get_resource_key(resource)
            baseline_lookup[resource_key] = resource

        changed_resources = []

        for resource in current_resources:
            resource_key = self._get_resource_key(resource)
            baseline_resource = baseline_lookup.get(resource_key)

            if baseline_resource is None:
                # New resource
                changed_resources.append(resource)
                debug("New resource detected", resource_key=resource_key)
            elif self._resource_changed(resource, baseline_resource):
                # Modified resource
                changed_resources.append(resource)
                debug("Modified resource detected", resource_key=resource_key)

        info(
            "Incremental scan analysis",
            total_resources=len(current_resources),
            changed_resources=len(changed_resources),
            baseline_resources=len(baseline_resources),
        )

        return changed_resources

    def _get_resource_key(self, resource: dict[str, Any]) -> str:
        """Generate unique key for a resource.

        Args:
            resource: Resource dictionary

        Returns:
            Unique resource key
        """
        resource_type = resource.get("resource_type", "unknown")
        resource_id = resource.get("id", "unknown")
        return f"{resource_type}:{resource_id}"

    def _resource_changed(self, current: dict[str, Any], baseline: dict[str, Any]) -> bool:
        """Check if a resource has changed compared to baseline.

        Args:
            current: Current resource configuration
            baseline: Baseline resource configuration

        Returns:
            True if resource has changed
        """
        # Compare resource configurations (excluding metadata that might change)
        current_config = self._normalize_resource_for_comparison(current)
        baseline_config = self._normalize_resource_for_comparison(baseline)

        return current_config != baseline_config

    def _normalize_resource_for_comparison(self, resource: dict[str, Any]) -> dict[str, Any]:
        """Normalize resource for comparison by removing volatile fields.

        Args:
            resource: Resource to normalize

        Returns:
            Normalized resource dictionary
        """
        # Create a copy and remove fields that might change but don't affect validation
        normalized = resource.copy()

        # Remove fields that are not relevant for rule validation
        fields_to_ignore = ["_terraform_meta", "_source_file", "_line_number"]
        for field in fields_to_ignore:
            normalized.pop(field, None)

        return normalized


class PerformanceMetrics:
    """Enhanced performance metrics collector with CLI integration."""

    def __init__(self, enable_cli_monitoring: bool = True) -> None:
        """Initialize performance metrics collector.

        Args:
            enable_cli_monitoring: Enable CLI-specific performance monitoring
        """
        self.metrics: dict[str, list[Any]] = {}
        self.start_times: dict[str, float] = {}
        self.cli_monitor: Optional[CLIPerformanceMonitor] = None

        if enable_cli_monitoring:
            self.cli_monitor = CLIPerformanceMonitor(enable_detailed_monitoring=True)

        debug("Performance metrics initialized", cli_monitoring=enable_cli_monitoring)

    def start_timer(self, operation: str) -> None:
        """Start timing an operation.

        Args:
            operation: Name of the operation to time
        """
        self.start_times[operation] = time.time()

        # Also start CLI monitoring if available
        if self.cli_monitor and operation in [
            "command_execution",
            "validation",
            "parsing",
            "output",
        ]:
            if operation == "command_execution":
                self.cli_monitor.start_command_execution("generic")

    def end_timer(self, operation: str) -> float:
        """End timing an operation and record the duration.

        Args:
            operation: Name of the operation to stop timing

        Returns:
            Duration in seconds
        """
        if operation not in self.start_times:
            debug("Timer not started for operation", operation=operation)
            return 0.0

        duration: float = time.time() - self.start_times[operation]

        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration)
        del self.start_times[operation]

        # Log performance with enhanced logging
        log_performance(
            f"Operation '{operation}' completed",
            duration=duration * 1000,  # Convert to ms
            operation=operation,
        )

        # Also end CLI monitoring if available
        if self.cli_monitor and operation in [
            "command_execution",
            "validation",
            "parsing",
            "output",
        ]:
            if operation == "command_execution":
                self.cli_monitor.end_command_execution("generic")

        return duration

    def record_metric(self, name: str, value: Any) -> None:
        """Record a custom metric.

        Args:
            name: Metric name
            value: Metric value
        """
        if name not in self.metrics:
            self.metrics[name] = []

        self.metrics[name].append(value)

        # Record specific metrics in CLI monitor
        if self.cli_monitor:
            if name == "file_operation":
                self.cli_monitor.record_file_operation()
            elif name == "network_operation":
                self.cli_monitor.record_network_operation()
            elif name == "cache_hit":
                self.cli_monitor.record_cache_hit()
            elif name == "cache_miss":
                self.cli_monitor.record_cache_miss()

    def get_summary(self) -> dict[str, Any]:
        """Get performance metrics summary.

        Returns:
            Dictionary containing performance metrics
        """
        summary = {}

        for operation, times in self.metrics.items():
            if isinstance(times[0], (int, float)):
                summary[operation] = {
                    "count": len(times),
                    "total": sum(times),
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                }
            else:
                summary[operation] = {
                    "count": len(times),
                    "values": times,
                }

        # Add CLI monitoring summary if available
        if self.cli_monitor:
            summary["cli_performance"] = self.cli_monitor.get_performance_summary()

        return summary

    def get_cli_summary(self) -> Dict[str, Any]:
        """Get CLI-specific performance summary."""
        if not self.cli_monitor:
            return {}
        return self.cli_monitor.get_performance_summary()

    def create_benchmark(
        self,
        operation: str,
        baseline_time: float,
        baseline_memory: float,
        regression_threshold: float = 0.2,
    ) -> Optional[PerformanceBenchmark]:
        """Create performance benchmark for regression detection."""
        if not self.cli_monitor:
            return None
        return self.cli_monitor.create_benchmark(
            operation, baseline_time, baseline_memory, regression_threshold
        )

    def print_summary(self) -> None:
        """Print performance metrics summary."""
        summary = self.get_summary()

        info("Performance metrics summary")
        for operation, stats in summary.items():
            if operation == "cli_performance":
                info("CLI Performance Summary:")
                for key, value in stats.items():
                    if isinstance(value, (int, float)):
                        if "time" in key or "duration" in key:
                            info(f"  {key}: {value:.3f}ms")
                        elif "memory" in key:
                            info(f"  {key}: {value:.1f}MB")
                        elif "percent" in key:
                            info(f"  {key}: {value:.1f}%")
                        else:
                            info(f"  {key}: {value}")
            elif "total" in stats:
                info(
                    f"Operation: {operation}",
                    count=stats["count"],
                    total_time=f"{stats['total']:.3f}s",
                    average_time=f"{stats['average']:.3f}s",
                    min_time=f"{stats['min']:.3f}s",
                    max_time=f"{stats['max']:.3f}s",
                )
            else:
                info(f"Metric: {operation}", count=stats["count"], values=stats["values"])

    def record_startup_complete(self) -> None:
        """Record CLI startup completion."""
        if self.cli_monitor:
            self.cli_monitor.record_startup_complete()

    @contextmanager
    def time_operation(self, operation: str):
        """Context manager for timing operations."""
        if self.cli_monitor:
            with self.cli_monitor.time_operation(operation):
                yield
        else:
            self.start_timer(operation)
            try:
                yield
            finally:
                self.end_timer(operation)


# Global performance monitor instance
_global_performance_monitor: Optional[PerformanceMetrics] = None


def get_performance_monitor(enable_cli_monitoring: bool = True) -> PerformanceMetrics:
    """Get or create global performance monitor instance."""
    global _global_performance_monitor
    if _global_performance_monitor is None:
        _global_performance_monitor = PerformanceMetrics(enable_cli_monitoring)
    return _global_performance_monitor


def configure_performance_monitoring(
    enable_cli_monitoring: bool = True,
    enable_detailed_monitoring: bool = False,
    profile_file: Optional[Path] = None,
) -> None:
    """Configure global performance monitoring settings."""
    global _global_performance_monitor
    _global_performance_monitor = PerformanceMetrics(enable_cli_monitoring)

    if profile_file:
        # Create a global profiler instance
        global _global_profiler
        _global_profiler = PerformanceProfiler(profile_file)


def record_startup_complete() -> None:
    """Record CLI startup completion using global monitor."""
    get_performance_monitor().record_startup_complete()


def start_timer(operation: str) -> None:
    """Start timing operation using global monitor."""
    get_performance_monitor().start_timer(operation)


def end_timer(operation: str) -> float:
    """End timing operation using global monitor."""
    return get_performance_monitor().end_timer(operation)


def record_metric(name: str, value: Any) -> None:
    """Record metric using global monitor."""
    get_performance_monitor().record_metric(name, value)


def get_performance_summary() -> Dict[str, Any]:
    """Get performance summary from global monitor."""
    return get_performance_monitor().get_summary()


def get_cli_performance_summary() -> Dict[str, Any]:
    """Get CLI-specific performance summary from global monitor."""
    return get_performance_monitor().get_cli_summary()


def create_performance_benchmark(
    operation: str,
    baseline_time: float,
    baseline_memory: float,
    regression_threshold: float = 0.2,
) -> Optional[PerformanceBenchmark]:
    """Create performance benchmark using global monitor."""
    return get_performance_monitor().create_benchmark(
        operation, baseline_time, baseline_memory, regression_threshold
    )


@contextmanager
def time_operation(operation: str):
    """Context manager for timing operations using global monitor."""
    with get_performance_monitor().time_operation(operation):
        yield


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_profiler(profile_file: Optional[Path] = None) -> PerformanceProfiler:
    """Get or create global profiler instance."""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler(profile_file)
    return _global_profiler


@contextmanager
def profile_operation(operation: str, details: Optional[Dict[str, Any]] = None):
    """Context manager for profiling operations using global profiler."""
    with get_profiler().profile_operation(operation, details):
        yield


def get_profile_summary() -> Dict[str, Any]:
    """Get profiling summary from global profiler."""
    return get_profiler().get_profile_summary()


# CLI-specific convenience functions
def record_file_operation() -> None:
    """Record a file operation."""
    record_metric("file_operation", 1)


def record_network_operation() -> None:
    """Record a network operation."""
    record_metric("network_operation", 1)


def record_cache_hit() -> None:
    """Record a cache hit."""
    record_metric("cache_hit", 1)


def record_cache_miss() -> None:
    """Record a cache miss."""
    record_metric("cache_miss", 1)
