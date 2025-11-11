"""Encryption and hashing utilities for DealerTower framework.

This module provides JWT token encryption/decryption and password hashing
functionality using industry-standard libraries (jose, passlib).

Modules:
    encryption: JWT token creation and validation utilities
    hashing: Password hashing and verification using Argon2/bcrypt
"""

from ..core.require_extra import require_extra

__all__ = (
    "encryption",
    "hashing",
)

require_extra("encrypt", "jose", "passlib")
