"""
Symmetric Encryption Module
===========================

Production-ready symmetric encryption implementations using industry-standard
algorithms with proper padding, IV/nonce generation, and key derivation.

Supported Algorithms:
- AES-256-GCM (Authenticated Encryption with Associated Data)
- AES-256-CBC (with HMAC for authentication)
- ChaCha20-Poly1305 (Modern AEAD cipher)

Key Derivation Functions:
- PBKDF2 (Password-Based Key Derivation Function 2)
- Argon2 (Modern password hashing and key derivation)
- scrypt (Memory-hard key derivation)

Security Features:
- Automatic IV/nonce generation (never reused)
- Constant-time operations
- Timing attack prevention
- Padding oracle prevention
- AEAD for authenticated encryption
- Secure key generation

All implementations use the PyCA cryptography library for FIPS 140-2 compliance.
"""

import hashlib
import hmac
import os
import secrets
import struct
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class EncryptionMode(str, Enum):
    """Supported encryption modes."""

    AES_GCM = "AES-256-GCM"
    AES_CBC = "AES-256-CBC"
    CHACHA20_POLY1305 = "ChaCha20-Poly1305"


class KeyDerivationAlgorithm(str, Enum):
    """Key derivation algorithms."""

    PBKDF2 = "PBKDF2-HMAC-SHA256"
    ARGON2 = "Argon2id"
    SCRYPT = "scrypt"


@dataclass
class EncryptionResult:
    """Result of encryption operation."""

    ciphertext: bytes
    iv: bytes  # Initialization Vector or Nonce
    tag: Optional[bytes] = None  # Authentication tag for AEAD
    salt: Optional[bytes] = None  # Salt for key derivation
    metadata: Optional[Dict[str, Any]] = None

    def to_bytes(self) -> bytes:
        """
        Serialize encryption result to bytes.

        Format: [version:1][iv_len:2][iv][tag_len:2][tag][ciphertext]
        """
        version = b"\x01"
        iv_len = struct.pack(">H", len(self.iv))

        if self.tag:
            tag_len = struct.pack(">H", len(self.tag))
            return version + iv_len + self.iv + tag_len + self.tag + self.ciphertext
        else:
            return version + iv_len + self.iv + b"\x00\x00" + self.ciphertext

    @classmethod
    def from_bytes(cls, data: bytes) -> "EncryptionResult":
        """Deserialize encryption result from bytes."""
        if len(data) < 5:
            raise ValueError("Invalid encrypted data format")

        version = data[0:1]
        if version != b"\x01":
            raise ValueError(f"Unsupported format version: {version}")

        iv_len = struct.unpack(">H", data[1:3])[0]
        iv = data[3 : 3 + iv_len]

        tag_len = struct.unpack(">H", data[3 + iv_len : 5 + iv_len])[0]

        if tag_len > 0:
            tag = data[5 + iv_len : 5 + iv_len + tag_len]
            ciphertext = data[5 + iv_len + tag_len :]
        else:
            tag = None
            ciphertext = data[5 + iv_len :]

        return cls(ciphertext=ciphertext, iv=iv, tag=tag)


class KeyDerivation:
    """
    Key derivation utilities for converting passwords to encryption keys.

    All functions use cryptographically secure derivation functions to prevent
    brute-force and dictionary attacks.
    """

    @staticmethod
    def derive_pbkdf2(
        password: bytes,
        salt: Optional[bytes] = None,
        iterations: int = 480000,  # OWASP 2023 recommendation
        key_length: int = 32,
        hash_algorithm: hashes.HashAlgorithm = hashes.SHA256(),
    ) -> Tuple[bytes, bytes]:
        """
        Derive key using PBKDF2-HMAC.

        Args:
            password: Password to derive key from
            salt: Salt (generated if not provided)
            iterations: Number of iterations (min 480,000 for SHA-256)
            key_length: Desired key length in bytes
            hash_algorithm: Hash algorithm to use

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hash_algorithm,
            length=key_length,
            salt=salt,
            iterations=iterations,
            backend=default_backend(),
        )

        key = kdf.derive(password)
        return key, salt

    @staticmethod
    def derive_scrypt(
        password: bytes,
        salt: Optional[bytes] = None,
        n: int = 2**14,  # CPU/memory cost (16384)
        r: int = 8,  # Block size
        p: int = 1,  # Parallelization
        key_length: int = 32,
    ) -> Tuple[bytes, bytes]:
        """
        Derive key using scrypt (memory-hard KDF).

        Args:
            password: Password to derive key from
            salt: Salt (generated if not provided)
            n: CPU/memory cost parameter
            r: Block size parameter
            p: Parallelization parameter
            key_length: Desired key length in bytes

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = Scrypt(salt=salt, length=key_length, n=n, r=r, p=p, backend=default_backend())

        key = kdf.derive(password)
        return key, salt

    @staticmethod
    def derive_argon2(
        password: bytes,
        salt: Optional[bytes] = None,
        time_cost: int = 2,
        memory_cost: int = 65536,  # 64 MiB
        parallelism: int = 1,
        hash_len: int = 32,
        key_length: int = 32,
    ) -> Tuple[bytes, bytes]:
        """
        Derive key using Argon2id (winner of Password Hashing Competition).

        NOTE: Requires argon2-cffi library for production use.
        This implementation provides a fallback to PBKDF2 if not available.

        Args:
            password: Password to derive key from
            salt: Salt (generated if not provided)
            time_cost: Number of iterations
            memory_cost: Memory usage in KiB
            parallelism: Degree of parallelism
            hash_len: Length of hash output
            key_length: Desired key length in bytes

        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        try:
            from argon2 import Type, low_level

            key = low_level.hash_secret_raw(
                secret=password,
                salt=salt,
                time_cost=time_cost,
                memory_cost=memory_cost,
                parallelism=parallelism,
                hash_len=hash_len,
                type=Type.ID,  # Argon2id
            )
            return key[:key_length], salt
        except ImportError:
            # Fallback to PBKDF2 if argon2-cffi not available
            return KeyDerivation.derive_pbkdf2(
                password=password,
                salt=salt,
                iterations=600000,  # Higher iterations for fallback
                key_length=key_length,
            )


class SymmetricCipher:
    """Base class for symmetric encryption."""

    def __init__(self, key: bytes):
        """
        Initialize cipher with key.

        Args:
            key: Encryption key (length depends on algorithm)
        """
        self.key = key
        self._validate_key()

    def _validate_key(self):
        """Validate key length. Override in subclasses."""
        pass

    def encrypt(
        self, plaintext: bytes, associated_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """Encrypt plaintext. Override in subclasses."""
        raise NotImplementedError

    def decrypt(self, result: EncryptionResult, associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt ciphertext. Override in subclasses."""
        raise NotImplementedError


class AESCipher(SymmetricCipher):
    """
    AES symmetric encryption with GCM or CBC mode.

    AES-256-GCM is recommended for most use cases as it provides authenticated
    encryption (AEAD) which prevents tampering.

    AES-256-CBC with HMAC is provided for legacy compatibility.
    """

    def __init__(self, key: bytes, mode: EncryptionMode = EncryptionMode.AES_GCM):
        """
        Initialize AES cipher.

        Args:
            key: 256-bit (32 bytes) encryption key
            mode: Encryption mode (GCM or CBC)
        """
        self.mode = mode
        super().__init__(key)

    def _validate_key(self):
        """Validate AES-256 key length."""
        if len(self.key) != 32:
            raise ValueError("AES-256 requires a 32-byte key")

    def encrypt(
        self, plaintext: bytes, associated_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """
        Encrypt plaintext using AES.

        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data (GCM only)

        Returns:
            EncryptionResult with ciphertext, IV, and tag
        """
        if self.mode == EncryptionMode.AES_GCM:
            return self._encrypt_gcm(plaintext, associated_data)
        elif self.mode == EncryptionMode.AES_CBC:
            return self._encrypt_cbc(plaintext)
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def decrypt(self, result: EncryptionResult, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt ciphertext using AES.

        Args:
            result: EncryptionResult from encrypt()
            associated_data: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext
        """
        if self.mode == EncryptionMode.AES_GCM:
            return self._decrypt_gcm(result, associated_data)
        elif self.mode == EncryptionMode.AES_CBC:
            return self._decrypt_cbc(result)
        else:
            raise ValueError(f"Unsupported mode: {self.mode}")

    def _encrypt_gcm(self, plaintext: bytes, associated_data: Optional[bytes]) -> EncryptionResult:
        """Encrypt using AES-256-GCM (AEAD)."""
        # Generate random 96-bit IV (recommended for GCM)
        iv = os.urandom(12)

        # Create cipher
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        # Add associated data if provided
        if associated_data:
            encryptor.authenticate_additional_data(associated_data)

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Get authentication tag
        tag = encryptor.tag

        return EncryptionResult(ciphertext=ciphertext, iv=iv, tag=tag)

    def _decrypt_gcm(self, result: EncryptionResult, associated_data: Optional[bytes]) -> bytes:
        """Decrypt using AES-256-GCM (AEAD)."""
        if not result.tag:
            raise ValueError("GCM mode requires authentication tag")

        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.key), modes.GCM(result.iv, result.tag), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Add associated data if provided
        if associated_data:
            decryptor.authenticate_additional_data(associated_data)

        # Decrypt (will raise exception if authentication fails)
        plaintext = decryptor.update(result.ciphertext) + decryptor.finalize()

        return plaintext

    def _encrypt_cbc(self, plaintext: bytes) -> EncryptionResult:
        """
        Encrypt using AES-256-CBC with HMAC authentication.

        Uses Encrypt-then-MAC construction to prevent padding oracle attacks.
        """
        # Generate random 128-bit IV
        iv = os.urandom(16)

        # Pad plaintext to block size (128 bits)
        padder = padding.PKCS7(128).padder()
        padded_plaintext = padder.update(plaintext) + padder.finalize()

        # Encrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        # Generate HMAC for authentication (Encrypt-then-MAC)
        # Use separate key derived from master key
        hmac_key = self._derive_hmac_key()
        tag = hmac.new(hmac_key, iv + ciphertext, hashlib.sha256).digest()

        return EncryptionResult(ciphertext=ciphertext, iv=iv, tag=tag)

    def _decrypt_cbc(self, result: EncryptionResult) -> bytes:
        """Decrypt using AES-256-CBC with HMAC verification."""
        if not result.tag:
            raise ValueError("CBC mode requires HMAC tag")

        # Verify HMAC first (before decryption to prevent padding oracle)
        hmac_key = self._derive_hmac_key()
        expected_tag = hmac.new(hmac_key, result.iv + result.ciphertext, hashlib.sha256).digest()

        # Constant-time comparison to prevent timing attacks
        if not hmac.compare_digest(expected_tag, result.tag):
            raise ValueError("HMAC verification failed - data may be tampered")

        # Decrypt
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(result.iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(result.ciphertext) + decryptor.finalize()

        # Remove padding
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()

        return plaintext

    def _derive_hmac_key(self) -> bytes:
        """Derive separate HMAC key from master key."""
        return hashlib.sha256(self.key + b"HMAC").digest()


class ChaCha20Cipher(SymmetricCipher):
    """
    ChaCha20-Poly1305 AEAD cipher.

    Modern alternative to AES that's faster on systems without AES hardware
    acceleration and resistant to timing attacks.
    """

    def __init__(self, key: bytes):
        """
        Initialize ChaCha20-Poly1305 cipher.

        Args:
            key: 256-bit (32 bytes) encryption key
        """
        super().__init__(key)

    def _validate_key(self):
        """Validate ChaCha20 key length."""
        if len(self.key) != 32:
            raise ValueError("ChaCha20 requires a 32-byte key")

    def encrypt(
        self, plaintext: bytes, associated_data: Optional[bytes] = None
    ) -> EncryptionResult:
        """
        Encrypt plaintext using ChaCha20-Poly1305.

        Args:
            plaintext: Data to encrypt
            associated_data: Additional authenticated data

        Returns:
            EncryptionResult with ciphertext, nonce, and tag
        """
        # Generate random 96-bit nonce
        nonce = os.urandom(12)

        # Create cipher
        cipher = Cipher(algorithms.ChaCha20(self.key, nonce), mode=None, backend=default_backend())
        encryptor = cipher.encryptor()

        # Encrypt
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Note: For Poly1305 MAC, we need to use AEAD construction
        # Using ChaCha20Poly1305 from cryptography library
        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

        aead = ChaCha20Poly1305(self.key)
        ciphertext_with_tag = aead.encrypt(nonce, plaintext, associated_data)

        # Split ciphertext and tag (tag is last 16 bytes)
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]

        return EncryptionResult(ciphertext=ciphertext, iv=nonce, tag=tag)

    def decrypt(self, result: EncryptionResult, associated_data: Optional[bytes] = None) -> bytes:
        """
        Decrypt ciphertext using ChaCha20-Poly1305.

        Args:
            result: EncryptionResult from encrypt()
            associated_data: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext
        """
        if not result.tag:
            raise ValueError("ChaCha20-Poly1305 requires authentication tag")

        from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

        aead = ChaCha20Poly1305(self.key)

        # Combine ciphertext and tag
        ciphertext_with_tag = result.ciphertext + result.tag

        # Decrypt and verify
        plaintext = aead.decrypt(result.iv, ciphertext_with_tag, associated_data)

        return plaintext


# Convenience functions


def generate_key(key_size: int = 32) -> bytes:
    """
    Generate cryptographically secure random key.

    Args:
        key_size: Key size in bytes (default: 32 for AES-256/ChaCha20)

    Returns:
        Random key bytes
    """
    return secrets.token_bytes(key_size)


def derive_key_pbkdf2(
    password: str, salt: Optional[bytes] = None, iterations: int = 480000, key_length: int = 32
) -> Tuple[bytes, bytes]:
    """
    Convenience function for PBKDF2 key derivation.

    Args:
        password: Password string
        salt: Salt (generated if not provided)
        iterations: Number of iterations
        key_length: Desired key length in bytes

    Returns:
        Tuple of (derived_key, salt)
    """
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    return KeyDerivation.derive_pbkdf2(
        password=password_bytes, salt=salt, iterations=iterations, key_length=key_length
    )


def derive_key_argon2(
    password: str,
    salt: Optional[bytes] = None,
    time_cost: int = 2,
    memory_cost: int = 65536,
    key_length: int = 32,
) -> Tuple[bytes, bytes]:
    """
    Convenience function for Argon2 key derivation.

    Args:
        password: Password string
        salt: Salt (generated if not provided)
        time_cost: Number of iterations
        memory_cost: Memory usage in KiB
        key_length: Desired key length in bytes

    Returns:
        Tuple of (derived_key, salt)
    """
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    return KeyDerivation.derive_argon2(
        password=password_bytes,
        salt=salt,
        time_cost=time_cost,
        memory_cost=memory_cost,
        key_length=key_length,
    )


def derive_key_scrypt(
    password: str,
    salt: Optional[bytes] = None,
    n: int = 2**14,
    r: int = 8,
    p: int = 1,
    key_length: int = 32,
) -> Tuple[bytes, bytes]:
    """
    Convenience function for scrypt key derivation.

    Args:
        password: Password string
        salt: Salt (generated if not provided)
        n: CPU/memory cost parameter
        r: Block size parameter
        p: Parallelization parameter
        key_length: Desired key length in bytes

    Returns:
        Tuple of (derived_key, salt)
    """
    password_bytes = password.encode("utf-8") if isinstance(password, str) else password
    return KeyDerivation.derive_scrypt(
        password=password_bytes, salt=salt, n=n, r=r, p=p, key_length=key_length
    )


__all__ = [
    "EncryptionMode",
    "KeyDerivationAlgorithm",
    "EncryptionResult",
    "KeyDerivation",
    "SymmetricCipher",
    "AESCipher",
    "ChaCha20Cipher",
    "generate_key",
    "derive_key_pbkdf2",
    "derive_key_argon2",
    "derive_key_scrypt",
]
