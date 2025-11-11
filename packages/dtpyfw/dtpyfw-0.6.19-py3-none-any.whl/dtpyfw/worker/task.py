"""Task registry utilities for Celery routing and scheduling."""

from __future__ import annotations

from datetime import timedelta
from typing import Any, Optional, Sequence

from celery.schedules import crontab

__all__ = ("Task",)


class Task:
    """Task registry for managing Celery task routing and scheduling.

    Description:
        Provides a centralized registry for collecting Celery task import paths,
        configuring task-to-queue routing, and defining periodic task schedules.
        This class maintains internal state for task routes and periodic schedules
        that can be consumed by the Worker builder to configure a Celery application.

    Attributes:
        _tasks (list[str]): List of registered task module paths for autodiscovery.
        _tasks_routes (dict[str, dict[str, str]]): Dictionary mapping task names to queue configurations.
        _periodic_tasks (dict[str, dict[str, Any]]): Dictionary mapping task names to schedule configurations.
    """

    _tasks: list[str] = []
    _tasks_routes: dict[str, dict[str, str]] = {}
    _periodic_tasks: dict[str, dict[str, Any]] = {}

    def _register_task_route(self, route: str) -> "Task":
        """Register a task module path for Celery autodiscovery.

        Description:
            Adds a task import path to the internal list used by Celery's
            autodiscover_tasks mechanism. This is a private helper method
            called by public registration methods.

        Args:
            route (str): The dotted import path to the task module
                (e.g., "my_app.tasks.process_data").

        Returns:
            Task: The current Task instance for method chaining.
        """
        self._tasks.append(route)
        return self

    def register(self, route: str, queue: Optional[str] = None) -> "Task":
        """Register a single Celery task with optional queue routing.

        Description:
            Registers a task module path for autodiscovery and optionally
            assigns it to a specific queue. If no queue is specified, the
            task will use Celery's default queue routing.

        Args:
            route (str): The dotted import path to the task module
                (e.g., "my_app.tasks.process_data").
            queue (Optional[str]): Optional queue name to route this task to.
                If None, uses default routing. Defaults to None.

        Returns:
            Task: The current Task instance for method chaining.
        """
        self._register_task_route(route=route)
        task_dict: dict[str, str] = {}
        if queue:
            task_dict["queue"] = queue

        self._tasks_routes[route] = task_dict
        return self

    def bulk_register(
        self, routes: Sequence[str], queue: Optional[str] = None
    ) -> "Task":
        """Register multiple Celery tasks with an optional shared queue.

        Description:
            Convenience method for registering multiple task module paths
            at once. All tasks in the sequence will be assigned to the same
            queue if one is specified.

        Args:
            routes (Sequence[str]): A sequence of dotted import paths to task modules
                (e.g., ["my_app.tasks.task1", "my_app.tasks.task2"]).
            queue (Optional[str]): Optional queue name to route all tasks to.
                If None, uses default routing. Defaults to None.

        Returns:
            Task: The current Task instance for method chaining.
        """
        for route in routes:
            self.register(route=route, queue=queue)
        return self

    def register_periodic_task(
        self,
        route: str,
        schedule: crontab | timedelta,
        queue: Optional[str] = None,
        *args: Any,
    ) -> "Task":
        """Register a periodic task with schedule and optional arguments.

        Description:
            Registers a task that should run on a recurring schedule using
            either crontab-style scheduling or time-based intervals. The task
            is also registered for autodiscovery and optional queue routing.

        Args:
            route (str): The dotted import path to the task module
                (e.g., "my_app.tasks.nightly_cleanup").
            schedule (crontab | timedelta): The schedule for task execution.
                Use crontab for cron-style schedules or timedelta for interval-based.
            queue (Optional[str]): Optional queue name to route this task to.
                If None, uses default routing. Defaults to None.
            *args (Any): Positional arguments to pass to the task when it executes.

        Returns:
            Task: The current Task instance for method chaining.
        """
        self.register(route=route, queue=queue)
        self._periodic_tasks[route] = {
            "task": route,
            "schedule": schedule,
            "args": args,
        }
        return self

    def bulk_register_periodic_task(
        self,
        tasks: Sequence[tuple[str, crontab | timedelta, Sequence[Any]]],
        queue: Optional[str] = None,
    ) -> "Task":
        """Register multiple periodic tasks in bulk with optional shared queue.

        Description:
            Convenience method for registering multiple periodic tasks at once.
            Each task is defined as a tuple containing the route, schedule, and
            arguments. All tasks will be assigned to the same queue if specified.

        Args:
            tasks (Sequence[tuple[str, crontab | timedelta, Sequence[Any]]]): A sequence
                of tuples where each tuple contains:
                - route (str): The dotted import path to the task module.
                - schedule (crontab | timedelta): The schedule for task execution.
                - args (Sequence[Any]): Positional arguments to pass to the task.
            queue (Optional[str]): Optional queue name to route all tasks to.
                If None, uses default routing. Defaults to None.

        Returns:
            Task: The current Task instance for method chaining.
        """
        for route, schedule, task_args in tasks:
            # Unpack task_args as positional arguments to register_periodic_task
            self.register_periodic_task(route, schedule, queue, *task_args)
        return self

    def get_tasks(self) -> list[str]:
        """Retrieve all registered task module paths for autodiscovery.

        Description:
            Returns the list of task import paths that have been registered
            via register() or bulk_register() methods. This list is used by
            Celery's autodiscover_tasks mechanism.

        Returns:
            list[str]: A list of dotted import paths to task modules.
        """
        return self._tasks

    def get_tasks_routes(self) -> dict[str, dict[str, str]]:
        """Retrieve the task-to-queue routing configuration.

        Description:
            Returns a dictionary mapping task names to their queue routing
            configuration. This dictionary is suitable for Celery's task_routes
            configuration setting.

        Returns:
            dict[str, dict[str, str]]: A dictionary where keys are task import paths and values are
                dictionaries containing routing configuration (e.g., {"queue": "name"}).
        """
        return self._tasks_routes

    def get_periodic_tasks(self) -> dict[str, dict[str, Any]]:
        """Retrieve the periodic task schedule configuration.

        Description:
            Returns a dictionary containing all registered periodic tasks with
            their schedules and arguments. This dictionary is suitable for
            Celery's beat_schedule configuration setting (used by RedBeat).

        Returns:
            dict[str, dict[str, Any]]: A dictionary where keys are task import paths and values are
                dictionaries containing "task", "schedule", and "args" keys.
        """
        return self._periodic_tasks
