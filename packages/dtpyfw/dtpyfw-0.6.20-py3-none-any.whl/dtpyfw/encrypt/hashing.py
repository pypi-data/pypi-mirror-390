"""Password hashing and verification utilities.

This module provides secure password hashing using Argon2 and bcrypt algorithms
via the passlib library. It offers methods for hashing passwords, verifying them,
and checking if existing hashes need updating when algorithms or parameters change.

The password context is configured to:
    - Use Argon2 as the primary hashing algorithm (recommended)
    - Support bcrypt for backward compatibility (marked as deprecated)
    - Disable bcrypt truncation errors for compatibility
"""

from passlib.context import CryptContext

# Configure password hashing context with Argon2 as primary and bcrypt as fallback
pwd_cxt: CryptContext = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated=["bcrypt"],
    bcrypt__truncate_error=False,
)


__all__ = ("Hash",)


class Hash:
    """Password hashing and verification using Argon2 and bcrypt.

    This class provides static methods for secure password operations using
    the passlib library. It uses Argon2 as the primary hashing algorithm with
    bcrypt as a deprecated fallback for legacy password compatibility.

    The class is designed to be used without instantiation, as all methods
    are static utilities.

    Attributes:
        None - All operations are performed through static methods.

    Example:
        >>> # Hash a new password
        >>> hashed = Hash.crypt("my_secure_password")
        >>>
        >>> # Verify a password
        >>> is_valid = Hash.verify("my_secure_password", hashed)
        >>> print(is_valid)  # True
        >>>
        >>> # Check if password needs rehashing
        >>> if Hash.needs_update(hashed):
        ...     new_hash = Hash.crypt("my_secure_password")
        ...     # Update database with new_hash
    """

    @staticmethod
    def crypt(password: str) -> str:
        """Hash a password using the configured password context.

        Generates a secure hash of the provided plaintext password using the
        Argon2 algorithm. The resulting hash includes the algorithm identifier,
        salt, and other parameters needed for verification, making it safe to
        store directly in a database.

        Args:
            password: The plaintext password string to hash. Can be any length,
                though extremely long passwords may be truncated by the algorithm.

        Returns:
            str: The hashed password string including algorithm identifier, salt,
                and hash value. Format varies by algorithm but is self-contained
                and can be verified using the verify() method.

        Note:
            Each call to this method generates a new random salt, so hashing the
            same password twice will produce different results. This is expected
            and secure behavior.

        Example:
            >>> hashed = Hash.crypt("my_password_123")
            >>> print(hashed[:10])  # Shows algorithm prefix
            $argon2id$
        """
        return pwd_cxt.hash(password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hashed password.

        Compares a plaintext password with a previously hashed password to
        determine if they match. This method is constant-time to prevent
        timing attacks and works with both Argon2 and bcrypt hashes.

        Args:
            plain_password: The plaintext password string to verify. This is
                the password provided by the user during authentication.
            hashed_password: The previously hashed password string to compare
                against. This is typically retrieved from a database.

        Returns:
            bool: True if the plaintext password matches the hash, False otherwise.
                Returns False for malformed hashes or algorithm mismatches.

        Note:
            This method is safe to use in authentication flows as it uses
            constant-time comparison to prevent timing-based attacks.

        Example:
            >>> hashed = Hash.crypt("correct_password")
            >>> Hash.verify("correct_password", hashed)
            True
            >>> Hash.verify("wrong_password", hashed)
            False
        """
        return pwd_cxt.verify(plain_password, hashed_password)

    @staticmethod
    def needs_update(hashed_password: str) -> bool:
        """Check if a hashed password needs to be updated.

        Determines whether a stored password hash should be re-hashed using
        current algorithm settings. This is useful when migrating from deprecated
        algorithms (like bcrypt) to newer ones (like Argon2), or when algorithm
        parameters have been strengthened.

        Args:
            hashed_password: The stored password hash string to check. This should
                be a valid hash created by one of the supported algorithms.

        Returns:
            bool: True if the password should be re-hashed with current settings
                (e.g., it uses bcrypt instead of Argon2), False if it's already
                using the current algorithm and parameters.

        Note:
            When this returns True, you should verify the user's password on their
            next login, then re-hash it using crypt() and update your database.
            This allows transparent migration to stronger algorithms.

        Example:
            >>> # Example with old bcrypt hash
            >>> old_hash = "$2b$12$someoldbcrypthash..."
            >>> if Hash.needs_update(old_hash):
            ...     # On next successful login:
            ...     new_hash = Hash.crypt(user_password)
            ...     # Update database with new_hash
        """
        return pwd_cxt.needs_update(hashed_password)
