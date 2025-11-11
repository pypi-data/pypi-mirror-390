"""
Cryptographic utilities for CovetPy.

Provides encryption, hashing, and signing utilities.
"""

import hashlib
from typing import Optional


class CryptoProvider:
    """Cryptographic operations provider."""

    def __init__(self, algorithm: str = "sha256"):
        self.algorithm = algorithm

    def hash(self, data: bytes) -> str:
        """Hash data."""
        h = hashlib.new(self.algorithm)
        h.update(data)
        return h.hexdigest()

    def verify_hash(self, data: bytes, expected_hash: str) -> bool:
        """Verify hash of data."""
        return self.hash(data) == expected_hash


__all__ = [
    "APIKeyGenerator","CryptoProvider", "SecureTokenGenerator"]


import hashlib
import secrets


class PasswordHasher:
    """Secure password hashing."""

    @staticmethod
    def hash_password(password: str, salt: str = None) -> str:
        """Hash password with salt."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return f"{salt}${hashed.hex()}"

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        try:
            salt, hash_value = hashed.split("$")
            new_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
            return new_hash.hex() == hash_value
        except:
            return False



import secrets
import hashlib

class APIKeyGenerator:
    """Generate secure API keys."""
    
    @staticmethod
    def generate(length=32):
        """Generate a random API key."""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def verify_key(key: str, hashed_key: str) -> bool:
        """Verify an API key against its hash."""
        return hashlib.sha256(key.encode()).hexdigest() == hashed_key


# Auto-generated stubs for missing exports

class SecureTokenGenerator:
    """Stub class for SecureTokenGenerator."""

    def __init__(self, *args, **kwargs):
        pass

