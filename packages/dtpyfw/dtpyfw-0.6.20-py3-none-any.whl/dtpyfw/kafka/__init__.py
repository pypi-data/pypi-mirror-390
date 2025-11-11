"""Kafka messaging utilities for DealerTower framework.

This module provides high-level wrappers for Kafka producers and
consumers, simplifying message publishing and consumption with built-in
configuration management, error handling, and logging integration.

The module requires the 'kafka' extra to be installed:     pip install
dtpyfw[kafka]
"""

from ..core.require_extra import require_extra

__all__ = (
    "config",
    "connection",
    "consumer",
    "producer",
)

require_extra("kafka", "kafka")
