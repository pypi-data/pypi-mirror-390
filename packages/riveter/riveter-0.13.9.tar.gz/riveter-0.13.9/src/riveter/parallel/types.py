"""Type definitions for parallel processing."""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4


class TaskStatus(Enum):
    """Status of a parallel task."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Priority levels for tasks."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TaskResult:
    """Result of a parallel task execution."""

    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[Exception] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    worker_id: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Get task execution duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def is_successful(self) -> bool:
        """Check if task completed successfully."""
        return self.status == TaskStatus.COMPLETED and self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "result": self.result,
            "error": str(self.error) if self.error else None,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "worker_id": self.worker_id,
        }


@dataclass
class ParallelTask:
    """Represents a task that can be executed in parallel."""

    task_id: str = field(default_factory=lambda: str(uuid4()))
    function: Callable[..., Any] = None
    args: tuple = field(default_factory=tuple)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    timeout: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 0
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        """Validate task parameters."""
        if self.function is None:
            raise ValueError("Task function cannot be None")

        if not callable(self.function):
            raise ValueError("Task function must be callable")

    @property
    def age(self) -> float:
        """Get task age in seconds."""
        return time.time() - self.created_at

    @property
    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries

    def execute(self) -> Any:
        """Execute the task function."""
        return self.function(*self.args, **self.kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_id": self.task_id,
            "function_name": getattr(self.function, "__name__", str(self.function)),
            "priority": self.priority.value,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "age": self.age,
        }


@dataclass
class WorkerStats:
    """Statistics for a worker thread."""

    worker_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    last_task_time: Optional[float] = None
    created_at: float = field(default_factory=time.time)

    @property
    def uptime(self) -> float:
        """Get worker uptime in seconds."""
        return time.time() - self.created_at

    @property
    def success_rate(self) -> float:
        """Calculate task success rate."""
        total_tasks = self.tasks_completed + self.tasks_failed
        return self.tasks_completed / total_tasks if total_tasks > 0 else 0.0

    def record_task_completion(self, execution_time: float) -> None:
        """Record a successful task completion."""
        self.tasks_completed += 1
        self.total_execution_time += execution_time
        self.average_execution_time = self.total_execution_time / self.tasks_completed
        self.last_task_time = time.time()

    def record_task_failure(self) -> None:
        """Record a task failure."""
        self.tasks_failed += 1
        self.last_task_time = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "worker_id": self.worker_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": self.average_execution_time,
            "success_rate": self.success_rate,
            "uptime": self.uptime,
            "last_task_time": self.last_task_time,
        }


@dataclass
class ParallelExecutorStats:
    """Statistics for the parallel executor."""

    total_tasks_submitted: int = 0
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    total_tasks_cancelled: int = 0
    active_tasks: int = 0
    queued_tasks: int = 0
    worker_count: int = 0
    average_queue_time: float = 0.0
    average_execution_time: float = 0.0
    peak_queue_size: int = 0
    peak_active_tasks: int = 0

    @property
    def completion_rate(self) -> float:
        """Calculate task completion rate."""
        return (
            self.total_tasks_completed / self.total_tasks_submitted
            if self.total_tasks_submitted > 0
            else 0.0
        )

    @property
    def failure_rate(self) -> float:
        """Calculate task failure rate."""
        return (
            self.total_tasks_failed / self.total_tasks_submitted
            if self.total_tasks_submitted > 0
            else 0.0
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_tasks_submitted": self.total_tasks_submitted,
            "total_tasks_completed": self.total_tasks_completed,
            "total_tasks_failed": self.total_tasks_failed,
            "total_tasks_cancelled": self.total_tasks_cancelled,
            "active_tasks": self.active_tasks,
            "queued_tasks": self.queued_tasks,
            "worker_count": self.worker_count,
            "completion_rate": self.completion_rate,
            "failure_rate": self.failure_rate,
            "average_queue_time": self.average_queue_time,
            "average_execution_time": self.average_execution_time,
            "peak_queue_size": self.peak_queue_size,
            "peak_active_tasks": self.peak_active_tasks,
        }


@dataclass
class BatchTaskResult:
    """Result of a batch task execution."""

    batch_id: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    results: List[TaskResult]
    start_time: float
    end_time: Optional[float] = None

    @property
    def duration(self) -> Optional[float]:
        """Get batch execution duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return None

    @property
    def success_rate(self) -> float:
        """Calculate batch success rate."""
        return self.completed_tasks / self.total_tasks if self.total_tasks > 0 else 0.0

    @property
    def is_complete(self) -> bool:
        """Check if batch is complete."""
        return (self.completed_tasks + self.failed_tasks) >= self.total_tasks

    def get_successful_results(self) -> List[TaskResult]:
        """Get only successful task results."""
        return [result for result in self.results if result.is_successful]

    def get_failed_results(self) -> List[TaskResult]:
        """Get only failed task results."""
        return [result for result in self.results if not result.is_successful]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "batch_id": self.batch_id,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "success_rate": self.success_rate,
            "duration": self.duration,
            "is_complete": self.is_complete,
            "results": [result.to_dict() for result in self.results],
        }
