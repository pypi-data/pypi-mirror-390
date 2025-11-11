"""Parallel processing system for Riveter.

This package provides thread-safe parallel processing capabilities
for rule evaluation, configuration parsing, and other CPU-intensive
operations while maintaining backward compatibility.
"""

from .executor import ParallelExecutor, ParallelExecutorConfig
from .pool import ThreadPoolManager, WorkerPool
from .scheduler import TaskPriority, TaskScheduler
from .types import ParallelTask, TaskResult, TaskStatus

__all__ = [
    "ParallelExecutor",
    "ParallelExecutorConfig",
    "ParallelTask",
    "TaskPriority",
    "TaskResult",
    "TaskScheduler",
    "TaskStatus",
    "ThreadPoolManager",
    "WorkerPool",
]
