"""Abstract task queue interface.

Concrete implementations swap the backend without changing call sites:
  BackgroundTaskQueue  — FastAPI BackgroundTasks (in-process, current)
  Future: CeleryTaskQueue, RQTaskQueue, etc.
"""
from abc import ABC, abstractmethod
from typing import Any, Callable


class TaskQueue(ABC):
    """Minimal contract for enqueuing fire-and-forget background tasks."""

    @abstractmethod
    def enqueue(self, task_fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        """Schedule task_fn(*args, **kwargs) for background execution."""
