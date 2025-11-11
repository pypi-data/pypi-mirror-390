"""Task scheduler for managing parallel task execution with dependencies."""

import heapq
import threading
import time
from typing import Dict, List, Optional, Set

from ..logging import debug, error, info, warning
from .types import ParallelTask, TaskPriority, TaskResult, TaskStatus


class TaskScheduler:
    """Schedules and manages task execution with dependency resolution."""

    def __init__(self):
        self.pending_tasks: List[tuple[int, float, ParallelTask]] = []  # Priority queue
        self.running_tasks: Dict[str, ParallelTask] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.task_dependencies: Dict[str, Set[str]] = {}
        self.dependent_tasks: Dict[str, Set[str]] = {}  # Reverse mapping
        self._lock = threading.RLock()
        self._task_counter = 0

    def submit_task(self, task: ParallelTask) -> None:
        """Submit a task for scheduling."""
        with self._lock:
            # Build dependency mappings
            self.task_dependencies[task.task_id] = set(task.dependencies)

            for dep_id in task.dependencies:
                if dep_id not in self.dependent_tasks:
                    self.dependent_tasks[dep_id] = set()
                self.dependent_tasks[dep_id].add(task.task_id)

            # Add to priority queue
            priority_value = -task.priority.value  # Negative for max-heap behavior
            self._task_counter += 1
            heapq.heappush(
                self.pending_tasks, (priority_value, task.created_at, self._task_counter, task)
            )

            debug(f"Scheduled task {task.task_id} with priority {task.priority.name}")

    def get_ready_tasks(self, max_tasks: Optional[int] = None) -> List[ParallelTask]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        remaining_tasks = []

        with self._lock:
            while self.pending_tasks and (max_tasks is None or len(ready_tasks) < max_tasks):
                priority, created_at, counter, task = heapq.heappop(self.pending_tasks)

                if self._are_dependencies_satisfied(task):
                    ready_tasks.append(task)
                    self.running_tasks[task.task_id] = task
                    debug(f"Task {task.task_id} is ready for execution")
                else:
                    remaining_tasks.append((priority, created_at, counter, task))

            # Put back tasks that aren't ready
            for task_tuple in remaining_tasks:
                heapq.heappush(self.pending_tasks, task_tuple)

        return ready_tasks

    def mark_task_completed(self, result: TaskResult) -> List[str]:
        """Mark a task as completed and return newly available task IDs."""
        newly_available = []

        with self._lock:
            task_id = result.task_id

            # Remove from running tasks
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]

            # Store result
            self.completed_tasks[task_id] = result

            # Check if any dependent tasks are now ready
            if task_id in self.dependent_tasks:
                for dependent_id in self.dependent_tasks[task_id]:
                    if (
                        dependent_id not in self.completed_tasks
                        and dependent_id not in self.running_tasks
                    ):
                        # Check if this dependent task is now ready
                        if self._is_task_ready_by_id(dependent_id):
                            newly_available.append(dependent_id)

            debug(f"Task {task_id} completed, {len(newly_available)} tasks now available")

        return newly_available

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        with self._lock:
            # Remove from pending tasks
            new_pending = []
            found = False

            for task_tuple in self.pending_tasks:
                _, _, _, task = task_tuple
                if task.task_id == task_id:
                    found = True
                    # Create cancelled result
                    result = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.CANCELLED,
                        start_time=time.time(),
                        end_time=time.time(),
                    )
                    self.completed_tasks[task_id] = result
                else:
                    new_pending.append(task_tuple)

            if found:
                self.pending_tasks = new_pending
                heapq.heapify(self.pending_tasks)
                debug(f"Cancelled task {task_id}")
                return True

            return False

    def get_pending_count(self) -> int:
        """Get number of pending tasks."""
        return len(self.pending_tasks)

    def get_running_count(self) -> int:
        """Get number of running tasks."""
        return len(self.running_tasks)

    def get_completed_count(self) -> int:
        """Get number of completed tasks."""
        return len(self.completed_tasks)

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        with self._lock:
            if task_id in self.completed_tasks:
                return self.completed_tasks[task_id].status
            elif task_id in self.running_tasks:
                return TaskStatus.RUNNING
            else:
                # Check if it's in pending
                for _, _, _, task in self.pending_tasks:
                    if task.task_id == task_id:
                        return TaskStatus.PENDING
                return None

    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get the result of a completed task."""
        return self.completed_tasks.get(task_id)

    def get_dependency_chain(self, task_id: str) -> List[str]:
        """Get the dependency chain for a task."""
        chain = []
        visited = set()

        def build_chain(tid: str) -> None:
            if tid in visited:
                return
            visited.add(tid)

            dependencies = self.task_dependencies.get(tid, set())
            for dep_id in dependencies:
                build_chain(dep_id)
                if dep_id not in chain:
                    chain.append(dep_id)

        build_chain(task_id)
        return chain

    def detect_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies in the task graph."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(task_id: str, path: List[str]) -> None:
            if task_id in rec_stack:
                # Found a cycle
                cycle_start = path.index(task_id)
                cycle = path[cycle_start:] + [task_id]
                cycles.append(cycle)
                return

            if task_id in visited:
                return

            visited.add(task_id)
            rec_stack.add(task_id)
            path.append(task_id)

            dependencies = self.task_dependencies.get(task_id, set())
            for dep_id in dependencies:
                dfs(dep_id, path.copy())

            rec_stack.remove(task_id)

        # Check all tasks
        all_task_ids = set(self.task_dependencies.keys())
        for task_id in all_task_ids:
            if task_id not in visited:
                dfs(task_id, [])

        return cycles

    def get_statistics(self) -> Dict[str, any]:
        """Get scheduler statistics."""
        with self._lock:
            # Calculate priority distribution
            priority_dist = {}
            for _, _, _, task in self.pending_tasks:
                priority = task.priority.name
                priority_dist[priority] = priority_dist.get(priority, 0) + 1

            # Calculate average wait time for pending tasks
            current_time = time.time()
            wait_times = [current_time - task.created_at for _, _, _, task in self.pending_tasks]
            avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0.0

            # Calculate completion statistics
            successful_tasks = sum(
                1
                for result in self.completed_tasks.values()
                if result.status == TaskStatus.COMPLETED
            )
            failed_tasks = sum(
                1 for result in self.completed_tasks.values() if result.status == TaskStatus.FAILED
            )

            return {
                "pending_tasks": len(self.pending_tasks),
                "running_tasks": len(self.running_tasks),
                "completed_tasks": len(self.completed_tasks),
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "priority_distribution": priority_dist,
                "average_wait_time": avg_wait_time,
                "total_dependencies": len(self.task_dependencies),
            }

    def clear_completed_tasks(self, keep_recent: int = 100) -> int:
        """Clear old completed tasks to free memory."""
        with self._lock:
            if len(self.completed_tasks) <= keep_recent:
                return 0

            # Sort by completion time and keep most recent
            sorted_results = sorted(
                self.completed_tasks.items(), key=lambda x: x[1].end_time or 0, reverse=True
            )

            tasks_to_keep = dict(sorted_results[:keep_recent])
            removed_count = len(self.completed_tasks) - len(tasks_to_keep)

            self.completed_tasks = tasks_to_keep

            debug(f"Cleared {removed_count} old completed tasks")
            return removed_count

    def _are_dependencies_satisfied(self, task: ParallelTask) -> bool:
        """Check if all dependencies for a task are satisfied."""
        dependencies = self.task_dependencies.get(task.task_id, set())

        for dep_id in dependencies:
            if dep_id not in self.completed_tasks:
                return False

            # Check if dependency completed successfully
            result = self.completed_tasks[dep_id]
            if result.status != TaskStatus.COMPLETED:
                return False

        return True

    def _is_task_ready_by_id(self, task_id: str) -> bool:
        """Check if a task is ready by its ID."""
        dependencies = self.task_dependencies.get(task_id, set())

        for dep_id in dependencies:
            if dep_id not in self.completed_tasks:
                return False

            result = self.completed_tasks[dep_id]
            if result.status != TaskStatus.COMPLETED:
                return False

        return True

    def reset(self) -> None:
        """Reset the scheduler state."""
        with self._lock:
            self.pending_tasks.clear()
            self.running_tasks.clear()
            self.completed_tasks.clear()
            self.task_dependencies.clear()
            self.dependent_tasks.clear()
            self._task_counter = 0

            info("Task scheduler reset")
