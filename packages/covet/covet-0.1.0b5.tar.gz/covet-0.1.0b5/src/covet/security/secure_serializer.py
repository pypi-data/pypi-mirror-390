"""
Secure Serialization Module

Provides HMAC-signed JSON serialization as a secure alternative to pickle.
Prevents deserialization attacks and ensures data integrity.

SECURITY: This module is designed to prevent CWE-502 (Insecure Deserialization)
"""

import hashlib
import hmac
import json
import secrets
from typing import Any, Optional


class SecureSerializationError(Exception):
    """Raised when serialization/deserialization fails"""

    pass


class DataIntegrityError(SecureSerializationError):
    """Raised when HMAC signature verification fails (potential tampering)"""

    pass


class SecureSerializer:
    """
    HMAC-signed JSON serializer for secure data storage

    Features:
    - JSON serialization (no code execution risk)
    - HMAC-SHA256 signature for integrity
    - Constant-time signature comparison
    - Secure key derivation support

    Usage:
        serializer = SecureSerializer(secret_key="your-secret-key")
        data = {"user_id": 123, "roles": ["admin"]}

        # Serialize
        signed_data = serializer.dumps(data)

        # Deserialize and verify
        verified_data = serializer.loads(signed_data)
    """

    SIGNATURE_SIZE = 32  # SHA-256 produces 32 bytes

    def __init__(
        self,
        secret_key: str,
        hash_algorithm: str = "sha256",
        json_encoder: Optional[type] = None,
    ):
        """
        Initialize secure serializer

        Args:
            secret_key: Secret key for HMAC signing
            hash_algorithm: Hash algorithm for HMAC (default: sha256)
            json_encoder: Optional custom JSON encoder class
        """
        if not secret_key:
            raise ValueError("Secret key cannot be empty")

        self.secret_key = secret_key.encode() if isinstance(secret_key, str) else secret_key
        self.hash_algorithm = hash_algorithm
        self.json_encoder = json_encoder

        # Validate hash algorithm
        try:
            hashlib.new(hash_algorithm)
        except ValueError as e:
            raise ValueError(f"Unsupported hash algorithm: {hash_algorithm}") from e

    def dumps(self, data: Any) -> bytes:
        """
        Serialize data with integrity protection

        Args:
            data: Data to serialize (must be JSON-serializable)

        Returns:
            HMAC signature + JSON data as bytes

        Raises:
            SecureSerializationError: If serialization fails
        """
        try:
            # Serialize to JSON
            json_data = json.dumps(
                data,
                cls=self.json_encoder,
                ensure_ascii=False,
                sort_keys=True,  # Deterministic output
            ).encode("utf-8")

            # Create HMAC signature
            signature = hmac.new(self.secret_key, json_data, self.hash_algorithm).digest()

            # Return signature + data
            return signature + json_data

        except (TypeError, ValueError) as e:
            raise SecureSerializationError(f"Serialization failed: {e}") from e

    def loads(self, signed_data: bytes) -> Any:
        """
        Deserialize and verify data integrity

        Args:
            signed_data: HMAC signature + JSON data

        Returns:
            Deserialized data

        Raises:
            DataIntegrityError: If signature verification fails
            SecureSerializationError: If deserialization fails
        """
        if not isinstance(signed_data, bytes):
            raise SecureSerializationError("Signed data must be bytes")

        if len(signed_data) < self.SIGNATURE_SIZE:
            raise SecureSerializationError("Data too short to contain signature")

        try:
            # Extract signature and data
            received_signature = signed_data[: self.SIGNATURE_SIZE]
            json_data = signed_data[self.SIGNATURE_SIZE :]

            # Compute expected signature
            expected_signature = hmac.new(self.secret_key, json_data, self.hash_algorithm).digest()

            # Constant-time comparison to prevent timing attacks
            if not hmac.compare_digest(received_signature, expected_signature):
                raise DataIntegrityError(
                    "HMAC signature verification failed - possible data tampering detected"
                )

            # Deserialize JSON
            return json.loads(json_data.decode("utf-8"))

        except DataIntegrityError:
            raise  # Re-raise integrity errors
        except (ValueError, UnicodeDecodeError) as e:
            raise SecureSerializationError(f"Deserialization failed: {e}") from e

    def verify_only(self, signed_data: bytes) -> bool:
        """
        Verify data integrity without deserializing

        Args:
            signed_data: HMAC signature + JSON data

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if len(signed_data) < self.SIGNATURE_SIZE:
                return False

            received_signature = signed_data[: self.SIGNATURE_SIZE]
            json_data = signed_data[self.SIGNATURE_SIZE :]

            expected_signature = hmac.new(self.secret_key, json_data, self.hash_algorithm).digest()

            return hmac.compare_digest(received_signature, expected_signature)

        except Exception:
            return False


class VersionedSerializer(SecureSerializer):
    """
    Secure serializer with version support for format migrations

    Adds version byte to serialized data for backward compatibility
    """

    VERSION = b"\x01"  # Current version

    def dumps(self, data: Any) -> bytes:
        """Serialize with version prefix"""
        signed_data = super().dumps(data)
        return self.VERSION + signed_data

    def loads(self, versioned_data: bytes) -> Any:
        """Deserialize with version check"""
        if not versioned_data or len(versioned_data) < 1:
            raise SecureSerializationError("Data too short to contain version")

        version = versioned_data[:1]
        signed_data = versioned_data[1:]

        if version != self.VERSION:
            raise SecureSerializationError(
                f"Unsupported version: {version!r} (expected {self.VERSION!r})"
            )

        return super().loads(signed_data)


def generate_secure_key(length: int = 32) -> str:
    """
    Generate cryptographically secure random key

    Args:
        length: Key length in bytes (default: 32 for 256-bit)

    Returns:
        URL-safe base64-encoded key
    """
    return secrets.token_urlsafe(length)


def secure_hash(data: str, algorithm: str = "sha256") -> str:
    """
    Generate secure hash for non-cryptographic purposes

    Args:
        data: Data to hash
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hexadecimal hash digest
    """
    if algorithm.lower() in ("md5", "sha1"):
        raise ValueError(f"Weak hash algorithm not allowed: {algorithm}")

    h = hashlib.new(algorithm)
    h.update(data.encode("utf-8"))
    return h.hexdigest()


def cache_key_hash(data: str) -> str:
    """
    Fast, secure hash for cache keys

    Uses Blake2b for performance while maintaining security
    """
    return hashlib.blake2b(data.encode("utf-8"), digest_size=16).hexdigest()  # 128-bit output


# Example usage and migration guide
__doc__ += """

Migration from Pickle to SecureSerializer:

Before (INSECURE):
    import pickle
    serialized = pickle.dumps(data)
    data = pickle.loads(serialized)

After (SECURE):
    from covet.security.secure_serializer import SecureSerializer

    serializer = SecureSerializer(secret_key=config.SECRET_KEY)
    serialized = serializer.dumps(data)
    data = serializer.loads(serialized)

Cache Backend Migration:
    # In cache backends, replace:
    pickle.dumps(value) -> serializer.dumps(value)
    pickle.loads(data) -> serializer.loads(data)

    # Update cache backend initialization:
    def __init__(self, secret_key: str):
        self.serializer = SecureSerializer(secret_key)

Session Backend Migration:
    # Same pattern as cache backends
    # Ensure all session backends use SecureSerializer
"""

__all__ = [
    "SecureSerializer",
    "VersionedSerializer",
    "SecureSerializationError",
    "DataIntegrityError",
    "generate_secure_key",
    "secure_hash",
    "cache_key_hash",
]
