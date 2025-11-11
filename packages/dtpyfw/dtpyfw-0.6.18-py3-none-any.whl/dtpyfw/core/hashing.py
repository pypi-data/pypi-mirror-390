"""Helpers for hashing arbitrary data."""

import hashlib
import json
from typing import Any, Union

__all__ = ("hash_data",)


def serialize_data(data: Any) -> bytes:
    """Serialize data into a bytes object for hashing.

    Description:
        Converts various data types into a consistent byte representation
        suitable for hashing. Handles strings, dictionaries, and other
        JSON-serializable types with fallback to repr().

    Args:
        data: The data to serialize. Can be str, dict, list, tuple, or other types.

    Returns:
        The serialized data as bytes.
    """
    if isinstance(data, str):
        return data.encode("utf-8")
    if isinstance(data, dict):
        return json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    try:
        # Attempt JSON serialization for other types (e.g., list, tuple)
        return json.dumps(data).encode("utf-8")
    except (TypeError, OverflowError):
        # Fallback to repr for objects that aren't JSON serializable
        return repr(data).encode("utf-8")


def hash_data(data: Any, algorithm: str = "sha512") -> str:
    """Hash the provided data using the specified algorithm.

    Description:
        Serializes the input data and generates a cryptographic hash using
        one of the supported algorithms. Default algorithm is SHA-512.

    Args:
        data: The data to hash. Can be any serializable type.
        algorithm: The hashing algorithm to use. Supported values:
            'md5', 'sha1', 'sha256', 'sha512', 'blake2b', 'blake2s'.
            Defaults to 'sha512'.

    Returns:
        The hexadecimal string representation of the hash digest.

    Raises:
        ValueError: If an unsupported algorithm is specified.
    """
    serialized = serialize_data(data)

    hash_obj: Union[hashlib._Hash, hashlib.blake2b, hashlib.blake2s]
    if algorithm.lower() == "md5":
        hash_obj = hashlib.md5(serialized)
    elif algorithm.lower() == "sha1":
        hash_obj = hashlib.sha1(serialized)
    elif algorithm.lower() == "sha256":
        hash_obj = hashlib.sha256(serialized)
    elif algorithm.lower() == "sha512":
        hash_obj = hashlib.sha512(serialized)
    elif algorithm.lower() == "blake2b":
        # Using 16-byte digest size for a 32-character hex digest
        hash_obj = hashlib.blake2b(serialized, digest_size=16)
    elif algorithm.lower() == "blake2s":
        # Using 16-byte digest size for a 32-character hex digest
        hash_obj = hashlib.blake2s(serialized, digest_size=16)
    else:
        raise ValueError("Unsupported algorithm selected.")

    return hash_obj.hexdigest()
