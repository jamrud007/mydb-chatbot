"""FastAPI BackgroundTasks implementation of TaskQueue."""
from typing import Any, Callable

from fastapi import BackgroundTasks

from task_queue.task_queue import TaskQueue


class BackgroundTaskQueue(TaskQueue):
    """Wraps FastAPI BackgroundTasks — runs tasks in the same process after response."""

    def __init__(self, background_tasks: BackgroundTasks) -> None:
        self._bg = background_tasks

    def enqueue(self, task_fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        self._bg.add_task(task_fn, *args, **kwargs)
