"""Thread pool management for parallel processing."""

import queue
import threading
import time
from typing import Dict, List, Optional

from ..exceptions import PerformanceError
from ..logging import debug, error, info, warning
from .types import ParallelTask, TaskResult, TaskStatus, WorkerStats


class WorkerThread(threading.Thread):
    """Worker thread for executing parallel tasks."""

    def __init__(
        self,
        worker_id: str,
        task_queue: queue.Queue,
        result_queue: queue.Queue,
        shutdown_event: threading.Event,
    ):
        super().__init__(name=f"RiveterWorker-{worker_id}", daemon=True)
        self.worker_id = worker_id
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.shutdown_event = shutdown_event
        self.stats = WorkerStats(worker_id)
        self.current_task: Optional[ParallelTask] = None
        self._lock = threading.Lock()

    def run(self) -> None:
        """Main worker loop."""
        debug(f"Worker {self.worker_id} started")

        while not self.shutdown_event.is_set():
            try:
                # Get task with timeout to allow periodic shutdown checks
                task = self.task_queue.get(timeout=1.0)

                if task is None:  # Poison pill
                    break

                self._execute_task(task)
                self.task_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                error(f"Worker {self.worker_id} encountered error: {e}")

        debug(f"Worker {self.worker_id} stopped")

    def _execute_task(self, task: ParallelTask) -> None:
        """Execute a single task."""
        with self._lock:
            self.current_task = task

        start_time = time.time()
        result = TaskResult(
            task_id=task.task_id,
            status=TaskStatus.RUNNING,
            start_time=start_time,
            worker_id=self.worker_id,
        )

        try:
            debug(f"Worker {self.worker_id} executing task {task.task_id}")

            # Execute task with timeout if specified
            if task.timeout:
                result.result = self._execute_with_timeout(task)
            else:
                result.result = task.execute()

            result.status = TaskStatus.COMPLETED
            result.end_time = time.time()

            # Update worker stats
            execution_time = result.end_time - start_time
            self.stats.record_task_completion(execution_time)

            debug(
                f"Worker {self.worker_id} completed task {task.task_id} "
                f"in {execution_time:.3f}s"
            )

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = e
            result.end_time = time.time()

            self.stats.record_task_failure()

            error(f"Worker {self.worker_id} failed task {task.task_id}: {e}")

        finally:
            with self._lock:
                self.current_task = None

            # Send result back
            self.result_queue.put(result)

    def _execute_with_timeout(self, task: ParallelTask) -> any:
        """Execute task with timeout using threading."""
        result_container = {}
        exception_container = {}

        def target():
            try:
                result_container["result"] = task.execute()
            except Exception as e:
                exception_container["exception"] = e

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=task.timeout)

        if thread.is_alive():
            # Task timed out
            raise PerformanceError(
                f"Task {task.task_id} timed out after {task.timeout}s",
                operation_timeout=task.timeout,
            )

        if "exception" in exception_container:
            raise exception_container["exception"]

        return result_container.get("result")

    def get_current_task(self) -> Optional[ParallelTask]:
        """Get the currently executing task."""
        with self._lock:
            return self.current_task

    def get_stats(self) -> WorkerStats:
        """Get worker statistics."""
        return self.stats


class WorkerPool:
    """Manages a pool of worker threads."""

    def __init__(self, pool_size: int, max_queue_size: int = 1000):
        self.pool_size = pool_size
        self.max_queue_size = max_queue_size
        self.task_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self.result_queue: queue.Queue = queue.Queue()
        self.shutdown_event = threading.Event()
        self.workers: List[WorkerThread] = []
        self._lock = threading.Lock()
        self._started = False

    def start(self) -> None:
        """Start the worker pool."""
        with self._lock:
            if self._started:
                return

            info(f"Starting worker pool with {self.pool_size} workers")

            for i in range(self.pool_size):
                worker = WorkerThread(
                    worker_id=f"worker-{i}",
                    task_queue=self.task_queue,
                    result_queue=self.result_queue,
                    shutdown_event=self.shutdown_event,
                )
                worker.start()
                self.workers.append(worker)

            self._started = True
            info(f"Worker pool started with {len(self.workers)} workers")

    def submit_task(
        self, task: ParallelTask, block: bool = True, timeout: Optional[float] = None
    ) -> bool:
        """Submit a task to the pool."""
        if not self._started:
            raise RuntimeError("Worker pool not started")

        try:
            self.task_queue.put(task, block=block, timeout=timeout)
            debug(f"Submitted task {task.task_id} to worker pool")
            return True
        except queue.Full:
            warning(f"Worker pool queue full, could not submit task {task.task_id}")
            return False

    def get_result(
        self, block: bool = True, timeout: Optional[float] = None
    ) -> Optional[TaskResult]:
        """Get a task result from the pool."""
        try:
            return self.result_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def shutdown(self, wait: bool = True, timeout: Optional[float] = None) -> None:
        """Shutdown the worker pool."""
        with self._lock:
            if not self._started:
                return

            info("Shutting down worker pool")

            # Signal shutdown
            self.shutdown_event.set()

            # Send poison pills to workers
            for _ in self.workers:
                try:
                    self.task_queue.put(None, block=False)
                except queue.Full:
                    pass

            if wait:
                # Wait for workers to finish
                for worker in self.workers:
                    worker.join(timeout=timeout)

                # Wait for remaining tasks
                try:
                    self.task_queue.join()
                except:
                    pass

            self.workers.clear()
            self._started = False

            info("Worker pool shutdown complete")

    def resize(self, new_size: int) -> None:
        """Resize the worker pool."""
        with self._lock:
            if not self._started:
                self.pool_size = new_size
                return

            current_size = len(self.workers)

            if new_size > current_size:
                # Add workers
                for i in range(current_size, new_size):
                    worker = WorkerThread(
                        worker_id=f"worker-{i}",
                        task_queue=self.task_queue,
                        result_queue=self.result_queue,
                        shutdown_event=self.shutdown_event,
                    )
                    worker.start()
                    self.workers.append(worker)

                info(f"Expanded worker pool to {new_size} workers")

            elif new_size < current_size:
                # Remove workers
                workers_to_remove = self.workers[new_size:]
                self.workers = self.workers[:new_size]

                # Send poison pills to removed workers
                for _ in workers_to_remove:
                    try:
                        self.task_queue.put(None, block=False)
                    except queue.Full:
                        pass

                info(f"Reduced worker pool to {new_size} workers")

            self.pool_size = new_size

    def get_stats(self) -> Dict[str, any]:
        """Get pool statistics."""
        with self._lock:
            worker_stats = [worker.get_stats().to_dict() for worker in self.workers]

            return {
                "pool_size": self.pool_size,
                "active_workers": len(self.workers),
                "queue_size": self.task_queue.qsize(),
                "result_queue_size": self.result_queue.qsize(),
                "max_queue_size": self.max_queue_size,
                "is_started": self._started,
                "worker_stats": worker_stats,
            }

    def get_active_tasks(self) -> List[ParallelTask]:
        """Get currently executing tasks."""
        active_tasks = []
        for worker in self.workers:
            current_task = worker.get_current_task()
            if current_task:
                active_tasks.append(current_task)
        return active_tasks

    def is_busy(self) -> bool:
        """Check if the pool is busy (has queued or active tasks)."""
        return self.task_queue.qsize() > 0 or len(self.get_active_tasks()) > 0


class ThreadPoolManager:
    """Manages multiple thread pools for different types of work."""

    def __init__(self):
        self.pools: Dict[str, WorkerPool] = {}
        self._lock = threading.Lock()

    def create_pool(self, name: str, pool_size: int, max_queue_size: int = 1000) -> WorkerPool:
        """Create a new worker pool."""
        with self._lock:
            if name in self.pools:
                raise ValueError(f"Pool '{name}' already exists")

            pool = WorkerPool(pool_size, max_queue_size)
            self.pools[name] = pool

            debug(f"Created worker pool '{name}' with {pool_size} workers")
            return pool

    def get_pool(self, name: str) -> Optional[WorkerPool]:
        """Get a worker pool by name."""
        return self.pools.get(name)

    def start_pool(self, name: str) -> bool:
        """Start a specific pool."""
        pool = self.get_pool(name)
        if pool:
            pool.start()
            return True
        return False

    def start_all_pools(self) -> None:
        """Start all pools."""
        for name, pool in self.pools.items():
            pool.start()
            debug(f"Started pool '{name}'")

    def shutdown_pool(self, name: str, wait: bool = True, timeout: Optional[float] = None) -> bool:
        """Shutdown a specific pool."""
        pool = self.get_pool(name)
        if pool:
            pool.shutdown(wait, timeout)
            return True
        return False

    def shutdown_all_pools(self, wait: bool = True, timeout: Optional[float] = None) -> None:
        """Shutdown all pools."""
        for name, pool in self.pools.items():
            pool.shutdown(wait, timeout)
            debug(f"Shutdown pool '{name}'")

    def remove_pool(self, name: str) -> bool:
        """Remove a pool."""
        with self._lock:
            if name in self.pools:
                pool = self.pools[name]
                pool.shutdown(wait=True)
                del self.pools[name]
                debug(f"Removed pool '{name}'")
                return True
            return False

    def get_all_stats(self) -> Dict[str, any]:
        """Get statistics for all pools."""
        return {name: pool.get_stats() for name, pool in self.pools.items()}

    def resize_pool(self, name: str, new_size: int) -> bool:
        """Resize a specific pool."""
        pool = self.get_pool(name)
        if pool:
            pool.resize(new_size)
            return True
        return False
