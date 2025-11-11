"""Main parallel executor for coordinating parallel task execution."""

import threading
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4

from ..exceptions import PerformanceError
from ..logging import debug, error, info, warning
from .pool import ThreadPoolManager, WorkerPool
from .scheduler import TaskScheduler
from .types import (
    BatchTaskResult,
    ParallelExecutorStats,
    ParallelTask,
    TaskPriority,
    TaskResult,
    TaskStatus,
)


@dataclass
class ParallelExecutorConfig:
    """Configuration for the parallel executor."""

    default_pool_size: int = 4
    max_queue_size: int = 1000
    result_timeout: float = 30.0
    batch_timeout: float = 300.0
    enable_task_scheduling: bool = True
    auto_scale_pools: bool = True
    max_pool_size: int = 16
    min_pool_size: int = 1
    scale_threshold: float = 0.8  # Scale up when queue is 80% full
    scale_down_threshold: float = 0.2  # Scale down when queue is 20% full
    stats_collection: bool = True


class ParallelExecutor:
    """Main executor for parallel task processing with advanced features."""

    def __init__(self, config: Optional[ParallelExecutorConfig] = None):
        self.config = config or ParallelExecutorConfig()
        self.pool_manager = ThreadPoolManager()
        self.scheduler = TaskScheduler() if self.config.enable_task_scheduling else None
        self.stats = ParallelExecutorStats() if self.config.stats_collection else None

        self._result_handlers: Dict[str, Callable[[TaskResult], None]] = {}
        self._batch_results: Dict[str, BatchTaskResult] = {}
        self._shutdown_event = threading.Event()
        self._result_processor_thread: Optional[threading.Thread] = None
        self._auto_scaler_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()

        # Create default pool
        self._setup_default_pool()

        # Start background threads
        self._start_background_threads()

    def _setup_default_pool(self) -> None:
        """Set up the default worker pool."""
        default_pool = self.pool_manager.create_pool(
            "default", self.config.default_pool_size, self.config.max_queue_size
        )
        default_pool.start()

        info(f"Created default worker pool with {self.config.default_pool_size} workers")

    def _start_background_threads(self) -> None:
        """Start background processing threads."""
        # Result processor thread
        self._result_processor_thread = threading.Thread(
            target=self._process_results, name="ResultProcessor", daemon=True
        )
        self._result_processor_thread.start()

        # Auto-scaler thread
        if self.config.auto_scale_pools:
            self._auto_scaler_thread = threading.Thread(
                target=self._auto_scale_pools, name="AutoScaler", daemon=True
            )
            self._auto_scaler_thread.start()

    def submit_task(
        self,
        function: Callable[..., Any],
        *args,
        pool_name: str = "default",
        priority: TaskPriority = TaskPriority.NORMAL,
        timeout: Optional[float] = None,
        max_retries: int = 0,
        dependencies: Optional[List[str]] = None,
        task_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Submit a single task for execution."""
        task = ParallelTask(
            task_id=task_id or str(uuid4()),
            function=function,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout,
            max_retries=max_retries,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        return self._submit_task_internal(task, pool_name)

    def submit_batch(
        self,
        tasks: List[Dict[str, Any]],
        pool_name: str = "default",
        batch_id: Optional[str] = None,
        wait_for_completion: bool = False,
        timeout: Optional[float] = None,
    ) -> str:
        """Submit a batch of tasks for execution."""
        batch_id = batch_id or str(uuid4())
        batch_result = BatchTaskResult(
            batch_id=batch_id,
            total_tasks=len(tasks),
            completed_tasks=0,
            failed_tasks=0,
            results=[],
            start_time=time.time(),
        )

        with self._lock:
            self._batch_results[batch_id] = batch_result

        # Submit individual tasks
        task_ids = []
        for task_config in tasks:
            task_id = self.submit_task(
                pool_name=pool_name, task_id=task_config.get("task_id"), **task_config
            )
            task_ids.append(task_id)

        if wait_for_completion:
            return self.wait_for_batch(batch_id, timeout)

        return batch_id

    def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> TaskResult:
        """Wait for a specific task to complete."""
        timeout = timeout or self.config.result_timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.scheduler:
                result = self.scheduler.get_task_result(task_id)
                if result:
                    return result

            time.sleep(0.1)

        raise PerformanceError(
            f"Task {task_id} did not complete within {timeout}s", operation_timeout=timeout
        )

    def wait_for_batch(self, batch_id: str, timeout: Optional[float] = None) -> BatchTaskResult:
        """Wait for a batch of tasks to complete."""
        timeout = timeout or self.config.batch_timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            with self._lock:
                batch_result = self._batch_results.get(batch_id)
                if batch_result and batch_result.is_complete:
                    batch_result.end_time = time.time()
                    return batch_result

            time.sleep(0.1)

        # Return partial results on timeout
        with self._lock:
            batch_result = self._batch_results.get(batch_id)
            if batch_result:
                batch_result.end_time = time.time()
                return batch_result

        raise PerformanceError(
            f"Batch {batch_id} did not complete within {timeout}s", operation_timeout=timeout
        )

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        if self.scheduler:
            return self.scheduler.cancel_task(task_id)
        return False

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a task."""
        if self.scheduler:
            return self.scheduler.get_task_status(task_id)
        return None

    def get_batch_status(self, batch_id: str) -> Optional[BatchTaskResult]:
        """Get the status of a batch."""
        with self._lock:
            return self._batch_results.get(batch_id)

    def create_pool(self, name: str, pool_size: int, max_queue_size: Optional[int] = None) -> bool:
        """Create a new worker pool."""
        try:
            max_queue_size = max_queue_size or self.config.max_queue_size
            pool = self.pool_manager.create_pool(name, pool_size, max_queue_size)
            pool.start()
            return True
        except Exception as e:
            error(f"Failed to create pool {name}: {e}")
            return False

    def resize_pool(self, pool_name: str, new_size: int) -> bool:
        """Resize a worker pool."""
        return self.pool_manager.resize_pool(pool_name, new_size)

    def get_pool_stats(self, pool_name: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for pools."""
        if pool_name:
            pool = self.pool_manager.get_pool(pool_name)
            return pool.get_stats() if pool else {}
        return self.pool_manager.get_all_stats()

    def get_executor_stats(self) -> Optional[ParallelExecutorStats]:
        """Get executor statistics."""
        if self.stats and self.scheduler:
            scheduler_stats = self.scheduler.get_statistics()

            # Update stats from scheduler
            self.stats.queued_tasks = scheduler_stats["pending_tasks"]
            self.stats.active_tasks = scheduler_stats["running_tasks"]
            self.stats.total_tasks_completed = scheduler_stats["successful_tasks"]
            self.stats.total_tasks_failed = scheduler_stats["failed_tasks"]

            # Update from pools
            pool_stats = self.get_pool_stats()
            total_workers = sum(stats.get("active_workers", 0) for stats in pool_stats.values())
            self.stats.worker_count = total_workers

        return self.stats

    def register_result_handler(self, task_id: str, handler: Callable[[TaskResult], None]) -> None:
        """Register a callback for when a specific task completes."""
        with self._lock:
            self._result_handlers[task_id] = handler

    def _submit_task_internal(self, task: ParallelTask, pool_name: str) -> str:
        """Internal task submission logic."""
        if self.scheduler:
            self.scheduler.submit_task(task)

            if self.stats:
                self.stats.total_tasks_submitted += 1

        # Try to get ready tasks and submit to pool
        self._process_ready_tasks(pool_name)

        debug(f"Submitted task {task.task_id} to scheduler")
        return task.task_id

    def _process_ready_tasks(self, pool_name: str) -> None:
        """Process tasks that are ready for execution."""
        if not self.scheduler:
            return

        pool = self.pool_manager.get_pool(pool_name)
        if not pool:
            warning(f"Pool {pool_name} not found")
            return

        ready_tasks = self.scheduler.get_ready_tasks(max_tasks=10)

        for task in ready_tasks:
            success = pool.submit_task(task, block=False)
            if not success:
                warning(f"Failed to submit task {task.task_id} to pool {pool_name}")

    def _process_results(self) -> None:
        """Background thread to process task results."""
        while not self._shutdown_event.is_set():
            try:
                # Process results from all pools
                for pool_name, pool in self.pool_manager.pools.items():
                    result = pool.get_result(block=False, timeout=0.1)
                    if result:
                        self._handle_task_result(result)

                time.sleep(0.1)

            except Exception as e:
                error(f"Error processing results: {e}")

    def _handle_task_result(self, result: TaskResult) -> None:
        """Handle a completed task result."""
        task_id = result.task_id

        # Update scheduler
        if self.scheduler:
            newly_available = self.scheduler.mark_task_completed(result)

            # Process newly available tasks
            if newly_available:
                self._process_ready_tasks("default")

        # Update batch results
        self._update_batch_results(result)

        # Call result handler if registered
        with self._lock:
            handler = self._result_handlers.pop(task_id, None)
            if handler:
                try:
                    handler(result)
                except Exception as e:
                    error(f"Error in result handler for task {task_id}: {e}")

        # Update stats
        if self.stats:
            if result.is_successful:
                self.stats.total_tasks_completed += 1
            else:
                self.stats.total_tasks_failed += 1

        debug(f"Processed result for task {task_id}: {result.status.value}")

    def _update_batch_results(self, result: TaskResult) -> None:
        """Update batch results with individual task result."""
        with self._lock:
            for batch_result in self._batch_results.values():
                # Simple check - in practice you'd track which tasks belong to which batch
                if len(batch_result.results) < batch_result.total_tasks:
                    batch_result.results.append(result)

                    if result.is_successful:
                        batch_result.completed_tasks += 1
                    else:
                        batch_result.failed_tasks += 1

                    break

    def _auto_scale_pools(self) -> None:
        """Background thread to automatically scale pools based on load."""
        while not self._shutdown_event.is_set():
            try:
                for pool_name, pool in self.pool_manager.pools.items():
                    stats = pool.get_stats()
                    queue_size = stats["queue_size"]
                    max_queue_size = stats["max_queue_size"]
                    current_workers = stats["active_workers"]

                    # Calculate queue utilization
                    queue_utilization = queue_size / max_queue_size if max_queue_size > 0 else 0

                    # Scale up if queue is getting full
                    if (
                        queue_utilization > self.config.scale_threshold
                        and current_workers < self.config.max_pool_size
                    ):
                        new_size = min(current_workers + 1, self.config.max_pool_size)
                        pool.resize(new_size)
                        debug(f"Scaled up pool {pool_name} to {new_size} workers")

                    # Scale down if queue is mostly empty
                    elif (
                        queue_utilization < self.config.scale_down_threshold
                        and current_workers > self.config.min_pool_size
                        and not pool.is_busy()
                    ):
                        new_size = max(current_workers - 1, self.config.min_pool_size)
                        pool.resize(new_size)
                        debug(f"Scaled down pool {pool_name} to {new_size} workers")

                time.sleep(10.0)  # Check every 10 seconds

            except Exception as e:
                error(f"Error in auto-scaler: {e}")

    def shutdown(self, wait: bool = True, timeout: Optional[float] = None) -> None:
        """Shutdown the parallel executor."""
        info("Shutting down parallel executor")

        # Signal shutdown
        self._shutdown_event.set()

        # Wait for background threads
        if self._result_processor_thread and self._result_processor_thread.is_alive():
            self._result_processor_thread.join(timeout=5.0)

        if self._auto_scaler_thread and self._auto_scaler_thread.is_alive():
            self._auto_scaler_thread.join(timeout=5.0)

        # Shutdown all pools
        self.pool_manager.shutdown_all_pools(wait=wait, timeout=timeout)

        # Clear state
        with self._lock:
            self._result_handlers.clear()
            self._batch_results.clear()

        if self.scheduler:
            self.scheduler.reset()

        info("Parallel executor shutdown complete")
