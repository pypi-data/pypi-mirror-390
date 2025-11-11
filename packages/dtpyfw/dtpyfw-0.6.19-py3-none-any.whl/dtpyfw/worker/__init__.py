"""Celery worker configuration and task management utilities.

Description:
    This module provides helper classes and functions for configuring Celery
    applications and managing task registration. It includes the Task class
    for collecting task routes and periodic schedules, and the Worker class
    for building fully configured Celery application instances with Redis
    integration, SSL support, and advanced scheduling features.

Exports:
    limited: Task execution rate limiting decorator (from celery-once).
    task: Celery task decorator for defining tasks.
    worker: Worker builder class for Celery application configuration.
"""

from ..core.require_extra import require_extra

__all__ = (
    "limited",
    "task",
    "worker",
)

require_extra("worker", "redis", "celery")
