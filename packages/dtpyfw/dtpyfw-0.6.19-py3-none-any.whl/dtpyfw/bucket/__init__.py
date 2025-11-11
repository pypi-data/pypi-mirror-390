"""S3-compatible bucket storage utilities.

This module provides high-level interfaces for interacting with
S3-compatible object storage services using boto3.
"""

from ..core.require_extra import require_extra

__all__ = ("bucket",)

require_extra("bucket", "boto3", "botocore")
