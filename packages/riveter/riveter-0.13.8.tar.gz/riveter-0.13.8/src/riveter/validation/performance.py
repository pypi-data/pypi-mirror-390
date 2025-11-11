"""Performance monitoring and optimization utilities.

This module provides performance monitoring, profiling, and optimization
utilities for the validation engine.
"""

import threading
import time
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any

from riveter.logging import debug, info, warning

from .protocols import PerformanceMonitorProtocol


@dataclass
class TimingInfo:
    """Information about operation timing."""

    operation: str
    start_time: float
    end_time: float | None = None
    duration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def finish(self) -> float:
        """Mark timing as finished and calculate duration."""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return self.duration

    @property
    def is_finished(self) -> bool:
        """Check if timing is finished."""
        return self.end_time is not None


@dataclass
class PerformanceMetric:
    """Performance metric data."""

    name: str
    value: float
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp,
            "tags": self.tags,
        }


class PerformanceMonitor(PerformanceMonitorProtocol):
    """Performance monitoring implementation with detailed metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self._timers: dict[str, TimingInfo] = {}
        self._metrics: list[PerformanceMetric] = []
        self._lock = threading.Lock()
        self._timer_counter = 0

        debug("Performance monitor initialized")

    def start_timer(self, operation: str) -> str:
        """Start timing an operation."""
        with self._lock:
            self._timer_counter += 1
            timer_id = f"{operation}_{self._timer_counter}_{int(time.time() * 1000)}"

            self._timers[timer_id] = TimingInfo(operation=operation, start_time=time.time())

            debug(f"Started timer: {timer_id} for operation: {operation}")
            return timer_id

    def stop_timer(self, timer_id: str) -> float:
        """Stop timing an operation."""
        with self._lock:
            if timer_id not in self._timers:
                warning(f"Timer not found: {timer_id}")
                return 0.0

            timing = self._timers[timer_id]
            duration = timing.finish()

            debug(f"Stopped timer: {timer_id}, duration: {duration:.4f}s")

            # Record as metric
            self.record_metric(
                f"operation_duration_{timing.operation}",
                duration,
                {"operation": timing.operation, "timer_id": timer_id},
            )

            return duration

    def record_metric(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a performance metric."""
        metric = PerformanceMetric(name=name, value=value, tags=tags or {})

        with self._lock:
            self._metrics.append(metric)

        debug(f"Recorded metric: {name} = {value}")

    @contextmanager
    def time_operation(self, operation: str) -> Generator[str, None, None]:
        """Context manager for timing operations."""
        timer_id = self.start_timer(operation)
        try:
            yield timer_id
        finally:
            self.stop_timer(timer_id)

    def get_metrics(self, name_filter: str | None = None) -> list[PerformanceMetric]:
        """Get recorded metrics with optional filtering."""
        with self._lock:
            if name_filter:
                return [m for m in self._metrics if name_filter in m.name]
            return self._metrics.copy()

    def get_timing_summary(self) -> dict[str, Any]:
        """Get summary of timing information."""
        with self._lock:
            finished_timings = [t for t in self._timers.values() if t.is_finished]

            if not finished_timings:
                return {"total_operations": 0}

            # Group by operation
            by_operation: dict[str, list[float]] = {}
            for timing in finished_timings:
                if timing.operation not in by_operation:
                    by_operation[timing.operation] = []
                by_operation[timing.operation].append(timing.duration)

            # Calculate statistics
            summary = {"total_operations": len(finished_timings)}

            for operation, durations in by_operation.items():
                summary[operation] = {
                    "count": len(durations),
                    "total_time": sum(durations),
                    "avg_time": sum(durations) / len(durations),
                    "min_time": min(durations),
                    "max_time": max(durations),
                }

            return summary

    def clear_metrics(self) -> None:
        """Clear all recorded metrics and timings."""
        with self._lock:
            self._metrics.clear()
            self._timers.clear()
            self._timer_counter = 0

        info("Performance metrics cleared")


class ParallelProcessor:
    """Utility for parallel processing of validation tasks."""

    def __init__(self, max_workers: int | None = None) -> None:
        """Initialize parallel processor.

        Args:
            max_workers: Maximum number of worker threads
        """
        self._max_workers = max_workers
        self._performance_monitor = PerformanceMonitor()

        debug(f"Parallel processor initialized with max_workers={max_workers}")

    def process_batch(
        self,
        items: list[Any],
        processor_func: callable,
        batch_size: int = 100,
        timeout: float | None = None,
    ) -> list[Any]:
        """Process items in parallel batches.

        Args:
            items: Items to process
            processor_func: Function to process each item
            batch_size: Size of each batch
            timeout: Timeout for each batch in seconds

        Returns:
            List of processed results
        """
        if not items:
            return []

        # Determine optimal number of workers
        num_workers = min(self._max_workers or len(items), len(items), 32)  # Reasonable upper limit

        with self._performance_monitor.time_operation("parallel_batch_processing"):
            results = []

            # Split items into batches
            batches = [items[i : i + batch_size] for i in range(0, len(items), batch_size)]

            debug(
                f"Processing {len(items)} items in {len(batches)} batches "
                f"with {num_workers} workers"
            )

            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                # Submit batch processing tasks
                future_to_batch = {
                    executor.submit(self._process_batch_items, batch, processor_func): batch
                    for batch in batches
                }

                # Collect results as they complete
                for future in as_completed(future_to_batch, timeout=timeout):
                    batch = future_to_batch[future]
                    try:
                        batch_results = future.result()
                        results.extend(batch_results)
                    except Exception as e:
                        warning(f"Batch processing failed for batch of size {len(batch)}: {e!s}")
                        # Continue with other batches
                        continue

            info(f"Parallel processing completed: {len(results)} results from {len(items)} items")
            return results

    def _process_batch_items(self, batch: list[Any], processor_func: callable) -> list[Any]:
        """Process a single batch of items."""
        results = []

        for item in batch:
            try:
                result = processor_func(item)
                results.append(result)
            except Exception as e:
                warning(f"Item processing failed: {e!s}")
                # Continue with other items in batch
                continue

        return results

    @property
    def performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        return self._performance_monitor.get_timing_summary()


class MemoryOptimizer:
    """Utilities for memory optimization during validation."""

    @staticmethod
    def optimize_resource_attributes(attributes: dict[str, Any]) -> dict[str, Any]:
        """Optimize resource attributes for memory efficiency.

        Args:
            attributes: Original attributes dictionary

        Returns:
            Optimized attributes dictionary
        """
        optimized = {}

        for key, value in attributes.items():
            # Skip None values to save memory
            if value is None:
                continue

            # Optimize string values
            if isinstance(value, str):
                # Intern common strings to save memory
                if len(value) < 100 and value.isalnum():
                    optimized[key] = value
                else:
                    optimized[key] = value

            # Optimize list values
            elif isinstance(value, list):
                if value:  # Only keep non-empty lists
                    optimized[key] = value

            # Optimize dict values recursively
            elif isinstance(value, dict):
                optimized_dict = MemoryOptimizer.optimize_resource_attributes(value)
                if optimized_dict:  # Only keep non-empty dicts
                    optimized[key] = optimized_dict

            else:
                optimized[key] = value

        return optimized

    @staticmethod
    def estimate_memory_usage(obj: Any) -> int:
        """Estimate memory usage of an object in bytes.

        Args:
            obj: Object to estimate

        Returns:
            Estimated memory usage in bytes
        """
        import sys

        try:
            return sys.getsizeof(obj)
        except Exception:
            # Fallback estimation
            if isinstance(obj, str):
                return len(obj.encode("utf-8"))
            if isinstance(obj, (list, tuple)):
                return sum(MemoryOptimizer.estimate_memory_usage(item) for item in obj)
            if isinstance(obj, dict):
                return sum(
                    MemoryOptimizer.estimate_memory_usage(k)
                    + MemoryOptimizer.estimate_memory_usage(v)
                    for k, v in obj.items()
                )
            return 64  # Default estimate


class ValidationProfiler:
    """Profiler specifically designed for validation operations."""

    def __init__(self):
        """Initialize validation profiler."""
        self._performance_monitor = PerformanceMonitor()
        self._memory_optimizer = MemoryOptimizer()
        self._enabled = True

    def profile_rule_evaluation(self, rule_id: str, resource_id: str) -> Any:
        """Context manager for profiling rule evaluation."""
        return self._performance_monitor.time_operation(f"rule_evaluation_{rule_id}_{resource_id}")

    def profile_resource_processing(self, resource_count: int) -> Any:
        """Context manager for profiling resource processing."""
        return self._performance_monitor.time_operation(f"resource_processing_{resource_count}")

    def record_cache_stats(self, hits: int, misses: int) -> None:
        """Record cache performance statistics."""
        total = hits + misses
        if total > 0:
            hit_rate = (hits / total) * 100
            self._performance_monitor.record_metric("cache_hit_rate", hit_rate)
            self._performance_monitor.record_metric("cache_requests", total)

    def get_profile_report(self) -> dict[str, Any]:
        """Get comprehensive profiling report."""
        return {
            "timing_summary": self._performance_monitor.get_timing_summary(),
            "metrics": [m.to_dict() for m in self._performance_monitor.get_metrics()],
            "enabled": self._enabled,
        }

    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True
        debug("Validation profiler enabled")

    def disable(self) -> None:
        """Disable profiling."""
        self._enabled = False
        debug("Validation profiler disabled")

    def clear(self) -> None:
        """Clear all profiling data."""
        self._performance_monitor.clear_metrics()
        info("Validation profiler data cleared")


# Global profiler instance
validation_profiler = ValidationProfiler()
