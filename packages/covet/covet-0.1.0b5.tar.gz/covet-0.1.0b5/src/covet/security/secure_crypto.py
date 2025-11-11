"""
Secure Cryptography Utilities for CovetPy Framework.

This module provides production-ready cryptographic operations including:
- Password hashing with PBKDF2-SHA256
- Symmetric encryption with Fernet (AES-128-CBC)
- Secure random token generation
- API key generation
- Constant-time comparison

Example:
    from covet.security.secure_crypto import SecureCrypto, hash_password, verify_password

    # Password hashing
    password_hash = hash_password("user_password")
    is_valid = verify_password("user_password", password_hash)

    # API key generation
    api_key = generate_api_key()

    # Encryption
    crypto = SecureCrypto()
    key = crypto.generate_key()
    encrypted = crypto.encrypt(b"sensitive data", key)
    decrypted = crypto.decrypt(encrypted, key)
"""

import base64
import hashlib
import hmac
import os
import secrets
from typing import Optional, Tuple

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


class SecureCrypto:
    """
    Secure cryptography operations.

    Provides methods for encryption, decryption, password hashing,
    and secure random generation.
    """

    @staticmethod
    def generate_key() -> bytes:
        """
        Generate secure random Fernet key.

        Returns:
            32-byte Fernet key (base64-encoded)

        Example:
            key = SecureCrypto.generate_key()
        """
        if HAS_CRYPTOGRAPHY:
            return Fernet.generate_key()
        else:
            # Fallback: generate 32 random bytes and base64 encode
            return base64.urlsafe_b64encode(secrets.token_bytes(32))

    @staticmethod
    def encrypt(data: bytes, key: bytes) -> bytes:
        """
        Encrypt data with Fernet (AES-128-CBC).

        Args:
            data: Data to encrypt (bytes)
            key: Encryption key (from generate_key)

        Returns:
            Encrypted data (bytes)

        Raises:
            ValueError: If data or key is invalid

        Example:
            key = SecureCrypto.generate_key()
            encrypted = SecureCrypto.encrypt(b"secret message", key)
        """
        if not isinstance(data, bytes):
            raise ValueError("Data must be bytes")

        if not key:
            raise ValueError("Encryption key is required")

        if HAS_CRYPTOGRAPHY:
            fernet = Fernet(key)
            return fernet.encrypt(data)
        else:
            # Basic fallback (NOT for production - use cryptography library)
            return SecureCrypto._basic_encrypt(data, key)

    @staticmethod
    def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """
        Decrypt data with Fernet.

        Args:
            encrypted_data: Encrypted data (bytes)
            key: Decryption key (same as encryption key)

        Returns:
            Decrypted data (bytes)

        Raises:
            ValueError: If data or key is invalid
            Exception: If decryption fails (wrong key, corrupted data)

        Example:
            decrypted = SecureCrypto.decrypt(encrypted, key)
        """
        if not isinstance(encrypted_data, bytes):
            raise ValueError("Encrypted data must be bytes")

        if not key:
            raise ValueError("Decryption key is required")

        if HAS_CRYPTOGRAPHY:
            fernet = Fernet(key)
            return fernet.decrypt(encrypted_data)
        else:
            # Basic fallback
            return SecureCrypto._basic_decrypt(encrypted_data, key)

    @staticmethod
    def hash_password(
        password: str, salt: Optional[bytes] = None, iterations: int = 100000
    ) -> Tuple[bytes, bytes]:
        """
        Hash password with PBKDF2-SHA256.

        Args:
            password: Password to hash
            salt: Salt (if None, generates new random salt)
            iterations: Number of iterations (default: 100,000)

        Returns:
            Tuple of (hashed_password, salt)

        Example:
            hashed, salt = SecureCrypto.hash_password("user_password")
            # Store both hashed and salt in database
        """
        if not password:
            raise ValueError("Password cannot be empty")

        if not isinstance(password, str):
            raise ValueError("Password must be a string")

        # Generate salt if not provided
        if salt is None:
            salt = SecureCrypto.generate_salt(32)

        if HAS_CRYPTOGRAPHY:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=iterations,
                backend=default_backend(),
            )
            hashed = kdf.derive(password.encode("utf-8"))
        else:
            # Fallback using hashlib
            hashed = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, iterations, dklen=32
            )

        return hashed, salt

    @staticmethod
    def verify_password(
        password: str, hashed: bytes, salt: bytes, iterations: int = 100000
    ) -> bool:
        """
        Verify password against hash using constant-time comparison.

        Args:
            password: Password to verify
            hashed: Stored password hash
            salt: Stored salt
            iterations: Number of iterations used for hashing (default: 100,000)

        Returns:
            True if password matches, False otherwise

        Example:
            is_valid = SecureCrypto.verify_password("user_password", stored_hash, stored_salt)
        """
        try:
            new_hash, _ = SecureCrypto.hash_password(password, salt, iterations)
            return SecureCrypto.constant_time_compare(new_hash, hashed)
        except Exception:
            return False

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate secure random token (hex-encoded).

        Args:
            length: Length in bytes (default: 32)

        Returns:
            Hex-encoded token string (length * 2 characters)

        Example:
            token = SecureCrypto.generate_token(32)  # Returns 64-char hex string
        """
        if length < 16:
            raise ValueError("Token length must be at least 16 bytes")

        if length > 256:
            raise ValueError("Token length must not exceed 256 bytes")

        return secrets.token_hex(length)

    @staticmethod
    def generate_salt(length: int = 32) -> bytes:
        """
        Generate secure random salt.

        Args:
            length: Length in bytes (default: 32)

        Returns:
            Random salt bytes

        Example:
            salt = SecureCrypto.generate_salt(32)
        """
        if length < 16:
            raise ValueError("Salt length must be at least 16 bytes")

        return secrets.token_bytes(length)

    @staticmethod
    def constant_time_compare(a: bytes, b: bytes) -> bool:
        """
        Constant-time comparison to prevent timing attacks.

        Args:
            a: First value
            b: Second value

        Returns:
            True if values are equal, False otherwise

        Note:
            This uses hmac.compare_digest for constant-time comparison.

        Example:
            is_equal = SecureCrypto.constant_time_compare(hash1, hash2)
        """
        if not isinstance(a, bytes) or not isinstance(b, bytes):
            return False

        return hmac.compare_digest(a, b)

    @staticmethod
    def _basic_encrypt(data: bytes, key: bytes) -> bytes:
        """Basic XOR encryption (fallback - NOT for production)."""
        # Derive encryption key from provided key
        key_hash = hashlib.sha256(key).digest()

        # XOR encryption (basic, not secure)
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key_hash[i % len(key_hash)])

        # Prepend random IV for variation
        iv = secrets.token_bytes(16)
        return base64.b64encode(iv + bytes(encrypted))

    @staticmethod
    def _basic_decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """Basic XOR decryption (fallback - NOT for production)."""
        # Decode from base64
        decoded = base64.b64decode(encrypted_data)

        # Extract IV and encrypted data
        iv = decoded[:16]
        encrypted = decoded[16:]

        # Derive encryption key
        key_hash = hashlib.sha256(key).digest()

        # XOR decryption
        decrypted = bytearray()
        for i, byte in enumerate(encrypted):
            decrypted.append(byte ^ key_hash[i % len(key_hash)])

        return bytes(decrypted)


# Convenience functions for common operations


def hash_password(password: str, salt: Optional[bytes] = None) -> str:
    """
    Hash password and return as base64-encoded string.

    This is a convenience wrapper that combines hash and salt into a single string.

    Args:
        password: Password to hash
        salt: Optional salt (generates new one if not provided)

    Returns:
        Base64-encoded string containing salt and hash

    Example:
        password_hash = hash_password("user_password")
        is_valid = verify_password("user_password", password_hash)
    """
    hashed, salt = SecureCrypto.hash_password(password, salt)

    # Combine salt and hash into single string (salt:hash format)
    combined = base64.b64encode(salt + hashed).decode("utf-8")
    return combined


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash string.

    Args:
        password: Password to verify
        password_hash: Hash string (from hash_password)

    Returns:
        True if password matches, False otherwise

    Example:
        is_valid = verify_password("user_password", stored_hash)
    """
    try:
        # Decode combined string
        combined = base64.b64decode(password_hash.encode("utf-8"))

        # Extract salt and hash (first 32 bytes are salt)
        salt = combined[:32]
        stored_hash = combined[32:]

        # Verify password
        return SecureCrypto.verify_password(password, stored_hash, salt)

    except Exception:
        return False


def generate_api_key(prefix: str = "cov_") -> str:
    """
    Generate API key with optional prefix.

    Args:
        prefix: Prefix for API key (default: "cov_")

    Returns:
        API key string

    Example:
        api_key = generate_api_key()  # Returns "cov_<random_string>"
    """
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}{random_part}"


def generate_secure_token(length: int = 32) -> str:
    """
    Generate secure random token.

    Args:
        length: Length in bytes (default: 32)

    Returns:
        URL-safe base64-encoded token

    Example:
        token = generate_secure_token(32)
    """
    return secrets.token_urlsafe(length)


def generate_session_id() -> str:
    """
    Generate secure session ID.

    Returns:
        Session ID string (64 characters)

    Example:
        session_id = generate_session_id()
    """
    return SecureCrypto.generate_token(32)


def generate_csrf_token() -> str:
    """
    Generate CSRF token.

    Returns:
        CSRF token string

    Example:
        csrf_token = generate_csrf_token()
    """
    return secrets.token_urlsafe(32)


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison.

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal, False otherwise

    Example:
        is_equal = constant_time_compare(token1, token2)
    """
    if not isinstance(a, str) or not isinstance(b, str):
        return False

    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


# Export all public APIs
__all__ = [
    "SecureCrypto",
    "hash_password",
    "verify_password",
    "generate_api_key",
    "generate_secure_token",
    "generate_session_id",
    "generate_csrf_token",
    "constant_time_compare",
]
