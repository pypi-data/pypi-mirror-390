"""Performance optimization utilities for Riveter."""

import hashlib
import json
import os
import pickle
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

from .logging import debug, info
from .rules import Rule
from .scanner import ValidationResult, validate_resources


class ParallelProcessor:
    """Handles parallel processing of rule validation."""

    def __init__(self, max_workers: Optional[int] = None):
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker threads. If None, uses CPU count.
        """
        self.max_workers = max_workers or os.cpu_count()
        debug("Parallel processor initialized", max_workers=self.max_workers)

    def validate_resources_parallel(
        self, rules: List[Rule], resources: List[Dict[str, Any]], batch_size: int = 10
    ) -> List[ValidationResult]:
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
        self, resources: List[Dict[str, Any]], batch_size: int
    ) -> List[List[Dict[str, Any]]]:
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
        self, rules: List[Rule], resources: List[Dict[str, Any]]
    ) -> List[ValidationResult]:
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

    def __init__(self, cache_dir: Optional[str] = None, max_size_mb: int = 100):
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

    def get_cached_config(self, file_path: str) -> Optional[Dict[str, Any]]:
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

    def cache_parsed_config(self, file_path: str, config: Dict[str, Any]) -> None:
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

    def __init__(self, baseline_file: Optional[str] = None):
        """Initialize incremental scanner.

        Args:
            baseline_file: Path to baseline file for comparison
        """
        self.baseline_file = baseline_file or ".riveter_baseline.json"
        debug("Incremental scanner initialized", baseline_file=self.baseline_file)

    def load_baseline(self) -> Optional[Dict[str, Any]]:
        """Load baseline configuration from file.

        Returns:
            Baseline configuration or None if not found
        """
        try:
            if not os.path.exists(self.baseline_file):
                debug("Baseline file not found", baseline_file=self.baseline_file)
                return None

            with open(self.baseline_file, "r") as f:
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

    def save_baseline(self, config: Dict[str, Any]) -> None:
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
        self, current_resources: List[Dict[str, Any]], baseline: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
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

    def _get_resource_key(self, resource: Dict[str, Any]) -> str:
        """Generate unique key for a resource.

        Args:
            resource: Resource dictionary

        Returns:
            Unique resource key
        """
        resource_type = resource.get("resource_type", "unknown")
        resource_id = resource.get("id", "unknown")
        return f"{resource_type}:{resource_id}"

    def _resource_changed(self, current: Dict[str, Any], baseline: Dict[str, Any]) -> bool:
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

    def _normalize_resource_for_comparison(self, resource: Dict[str, Any]) -> Dict[str, Any]:
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
    """Collects and reports performance metrics."""

    def __init__(self) -> None:
        """Initialize performance metrics collector."""
        self.metrics: Dict[str, List[Any]] = {}
        self.start_times: Dict[str, float] = {}
        debug("Performance metrics initialized")

    def start_timer(self, operation: str) -> None:
        """Start timing an operation.

        Args:
            operation: Name of the operation to time
        """
        self.start_times[operation] = time.time()

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

    def get_summary(self) -> Dict[str, Any]:
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

        return summary

    def print_summary(self) -> None:
        """Print performance metrics summary."""
        summary = self.get_summary()

        info("Performance metrics summary")
        for operation, stats in summary.items():
            if "total" in stats:
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
