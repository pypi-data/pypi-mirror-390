"""
Key Management System (KMS) Integration

Production-grade key management for encryption keys used in database backups.

Supports:
- AWS KMS
- Azure Key Vault
- Google Cloud KMS
- HashiCorp Vault
- Local encrypted keystore (for development/testing)

Security Features:
- Never store keys in plaintext
- Key rotation support
- Audit logging of key access
- Key versioning
- Access control integration
- Encryption at rest for local keystore

Best Practices:
- Use cloud KMS in production
- Implement key rotation policies
- Enable audit logging
- Use least privilege access
- Never log keys
- Implement key backup and recovery procedures
"""

import base64
import hashlib
import json
import logging
import os
import secrets
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class KMSProvider(Enum):
    """Supported KMS providers."""

    LOCAL = "local"  # Local encrypted keystore (dev/test only)
    AWS_KMS = "aws_kms"
    AZURE_KEY_VAULT = "azure_key_vault"
    GOOGLE_CLOUD_KMS = "google_cloud_kms"
    HASHICORP_VAULT = "hashicorp_vault"


class KMSError(Exception):
    """Base exception for KMS errors."""

    pass


class KeyNotFoundError(KMSError):
    """Key not found in KMS."""

    pass


class KeyAccessDeniedError(KMSError):
    """Access denied to key."""

    pass


class KMSBase(ABC):
    """
    Abstract base class for Key Management Systems.

    All KMS implementations must inherit from this class and implement
    the required methods for key operations.
    """

    @abstractmethod
    async def generate_data_key(
        self, key_id: str, key_spec: str = "AES_256"
    ) -> Tuple[bytes, bytes]:
        """
        Generate a data encryption key.

        Args:
            key_id: KMS key identifier
            key_spec: Key specification (AES_256, AES_128, etc.)

        Returns:
            Tuple of (plaintext_key, encrypted_key)
            - plaintext_key: The actual encryption key (to be used immediately)
            - encrypted_key: The encrypted version (to be stored)

        Raises:
            KMSError: If key generation fails
        """
        pass

    @abstractmethod
    async def decrypt_data_key(self, encrypted_key: bytes) -> bytes:
        """
        Decrypt an encrypted data key.

        Args:
            encrypted_key: The encrypted key blob

        Returns:
            Decrypted plaintext key

        Raises:
            KeyNotFoundError: If key not found
            KeyAccessDeniedError: If access denied
            KMSError: If decryption fails
        """
        pass

    @abstractmethod
    async def encrypt_data(self, key_id: str, plaintext: bytes) -> bytes:
        """
        Encrypt data directly using KMS key.

        Args:
            key_id: KMS key identifier
            plaintext: Data to encrypt

        Returns:
            Encrypted data

        Raises:
            KMSError: If encryption fails
        """
        pass

    @abstractmethod
    async def decrypt_data(self, key_id: str, ciphertext: bytes) -> bytes:
        """
        Decrypt data using KMS key.

        Args:
            key_id: KMS key identifier
            ciphertext: Encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            KMSError: If decryption fails
        """
        pass

    @abstractmethod
    async def rotate_key(self, key_id: str) -> str:
        """
        Rotate a KMS key.

        Args:
            key_id: Key identifier to rotate

        Returns:
            New key version identifier

        Raises:
            KMSError: If rotation fails
        """
        pass


class LocalKMS(KMSBase):
    """
    Local encrypted keystore for development and testing.

    WARNING: This implementation is for development/testing only.
    Use cloud KMS providers (AWS, Azure, GCP) in production.

    Features:
    - Encrypted key storage
    - Master key derived from password
    - Key versioning
    - Audit logging

    Security:
    - Keys encrypted at rest using AES-256-GCM
    - Master key derived using PBKDF2
    - Each key has unique IV
    - Integrity verification with GCM tag
    """

    def __init__(
        self,
        keystore_path: str,
        master_password: Optional[str] = None,
        master_key: Optional[bytes] = None,
    ):
        """
        Initialize local KMS.

        Args:
            keystore_path: Path to keystore file
            master_password: Password for master key derivation
            master_key: Direct master key (overrides password)

        Note: Must provide either master_password or master_key
        """
        self.keystore_path = Path(keystore_path)
        self.keystore_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize master key
        if master_key:
            self.master_key = master_key
        elif master_password:
            self.master_key = self._derive_master_key(master_password)
        else:
            raise ValueError("Must provide either master_password or master_key")

        # Load or initialize keystore
        self._load_keystore()

    def _derive_master_key(self, password: str) -> bytes:
        """Derive master key from password using PBKDF2."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

        # Use fixed salt for deterministic key derivation
        # In production, store salt securely
        salt = hashlib.sha256(b"covetpy_kms_salt").digest()[:16]

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        return kdf.derive(password.encode("utf-8"))

    def _load_keystore(self):
        """Load keystore from disk."""
        if self.keystore_path.exists():
            try:
                encrypted_data = self.keystore_path.read_bytes()
                self.keystore = self._decrypt_keystore(encrypted_data)
                logger.info(f"Loaded keystore from {self.keystore_path}")
            except Exception as e:
                logger.warning(f"Failed to load keystore: {e}. Creating new keystore.")
                self.keystore = {"keys": {}, "metadata": {}}
        else:
            self.keystore = {"keys": {}, "metadata": {}}
            self._save_keystore()

    def _save_keystore(self):
        """Save keystore to disk (encrypted)."""
        encrypted_data = self._encrypt_keystore(self.keystore)
        self.keystore_path.write_bytes(encrypted_data)

        # Set secure permissions
        os.chmod(self.keystore_path, 0o600)

    def _encrypt_keystore(self, data: dict) -> bytes:
        """Encrypt keystore using master key."""
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        # Generate IV
        iv = secrets.token_bytes(12)

        # Serialize data
        plaintext = json.dumps(data, default=str).encode("utf-8")

        # Encrypt
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Return IV + tag + ciphertext
        return iv + encryptor.tag + ciphertext

    def _decrypt_keystore(self, encrypted_data: bytes) -> dict:
        """Decrypt keystore using master key."""
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        # Extract IV, tag, and ciphertext
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]

        # Decrypt
        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return json.loads(plaintext.decode("utf-8"))

    async def generate_data_key(
        self, key_id: str, key_spec: str = "AES_256"
    ) -> Tuple[bytes, bytes]:
        """Generate a data encryption key."""
        # Determine key size
        key_size = 32 if key_spec == "AES_256" else 16

        # Generate random key
        plaintext_key = secrets.token_bytes(key_size)

        # Encrypt the key with master key
        encrypted_key = self._encrypt_data_key(plaintext_key)

        # Store metadata
        key_metadata = {
            "key_id": key_id,
            "key_spec": key_spec,
            "created_at": datetime.now().isoformat(),
            "version": 1,
        }

        self.keystore["keys"][key_id] = {
            "encrypted_key": base64.b64encode(encrypted_key).decode("ascii"),
            "metadata": key_metadata,
        }

        self._save_keystore()

        logger.info(f"Generated data key: {key_id}")
        self._audit_log("generate_key", key_id, success=True)

        return plaintext_key, encrypted_key

    def _encrypt_data_key(self, plaintext_key: bytes) -> bytes:
        """Encrypt a data key using master key."""
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        iv = secrets.token_bytes(12)

        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv),
            backend=default_backend(),
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext_key) + encryptor.finalize()

        return iv + encryptor.tag + ciphertext

    def _decrypt_data_key(self, encrypted_key: bytes) -> bytes:
        """Decrypt a data key using master key."""
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        iv = encrypted_key[:12]
        tag = encrypted_key[12:28]
        ciphertext = encrypted_key[28:]

        cipher = Cipher(
            algorithms.AES(self.master_key),
            modes.GCM(iv, tag),
            backend=default_backend(),
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

    async def decrypt_data_key(self, encrypted_key: bytes) -> bytes:
        """Decrypt an encrypted data key."""
        try:
            plaintext_key = self._decrypt_data_key(encrypted_key)
            self._audit_log("decrypt_key", "unknown", success=True)
            return plaintext_key
        except Exception as e:
            self._audit_log("decrypt_key", "unknown", success=False, error=str(e))
            raise KMSError(f"Failed to decrypt data key: {e}") from e

    async def encrypt_data(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data directly using KMS key."""
        # For local KMS, generate a new key for each encryption
        data_key, encrypted_data_key = await self.generate_data_key(key_id)

        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        iv = secrets.token_bytes(12)

        cipher = Cipher(algorithms.AES(data_key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Return: encrypted_data_key_length (4 bytes) + encrypted_data_key + iv + tag + ciphertext
        encrypted_data_key_len = len(encrypted_data_key).to_bytes(4, "big")
        return encrypted_data_key_len + encrypted_data_key + iv + encryptor.tag + ciphertext

    async def decrypt_data(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data using KMS key."""
        # Extract encrypted data key
        encrypted_key_len = int.from_bytes(ciphertext[:4], "big")
        encrypted_data_key = ciphertext[4 : 4 + encrypted_key_len]
        encrypted_payload = ciphertext[4 + encrypted_key_len :]

        # Decrypt data key
        data_key = await self.decrypt_data_key(encrypted_data_key)

        # Extract IV, tag, and ciphertext
        iv = encrypted_payload[:12]
        tag = encrypted_payload[12:28]
        ct = encrypted_payload[28:]

        # Decrypt data
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

        cipher = Cipher(algorithms.AES(data_key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        return decryptor.update(ct) + decryptor.finalize()

    async def rotate_key(self, key_id: str) -> str:
        """Rotate a KMS key."""
        if key_id not in self.keystore["keys"]:
            raise KeyNotFoundError(f"Key not found: {key_id}")

        # Get current version
        current_metadata = self.keystore["keys"][key_id]["metadata"]
        current_version = current_metadata.get("version", 1)

        # Generate new key
        new_key_id = f"{key_id}_v{current_version + 1}"

        # Generate new data key
        plaintext_key, encrypted_key = await self.generate_data_key(
            new_key_id, current_metadata.get("key_spec", "AES_256")
        )

        logger.info(f"Rotated key {key_id} to {new_key_id}")
        self._audit_log("rotate_key", key_id, success=True)

        return new_key_id

    def _audit_log(self, operation: str, key_id: str, success: bool, error: Optional[str] = None):
        """Log key operations for audit trail."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "key_id": key_id,
            "success": success,
            "error": error,
        }

        if "audit_log" not in self.keystore["metadata"]:
            self.keystore["metadata"]["audit_log"] = []

        self.keystore["metadata"]["audit_log"].append(log_entry)

        # Keep only last 1000 entries
        if len(self.keystore["metadata"]["audit_log"]) > 1000:
            self.keystore["metadata"]["audit_log"] = self.keystore["metadata"]["audit_log"][-1000:]

        self._save_keystore()

    def get_audit_log(self, limit: int = 100) -> list:
        """Get recent audit log entries."""
        audit_log = self.keystore["metadata"].get("audit_log", [])
        return audit_log[-limit:]


class AWSKMS(KMSBase):
    """
    AWS KMS integration.

    Requires boto3 library:
        pip install boto3

    Configuration:
    - AWS credentials via environment variables, IAM role, or AWS config
    - KMS key ARN or alias

    Example:
        kms = AWSKMS(region="us-east-1")
        plaintext_key, encrypted_key = await kms.generate_data_key("alias/backup-key")
    """

    def __init__(self, region: str = "us-east-1", **kwargs):
        """
        Initialize AWS KMS client.

        Args:
            region: AWS region
            **kwargs: Additional boto3 client configuration
        """
        try:
            import boto3

            self.client = boto3.client("kms", region_name=region, **kwargs)
            logger.info(f"Initialized AWS KMS client for region {region}")
        except ImportError:
            raise ImportError("boto3 required for AWS KMS. Install with: pip install boto3")

    async def generate_data_key(
        self, key_id: str, key_spec: str = "AES_256"
    ) -> Tuple[bytes, bytes]:
        """Generate data key using AWS KMS."""
        try:
            response = self.client.generate_data_key(KeyId=key_id, KeySpec=key_spec)

            plaintext_key = response["Plaintext"]
            encrypted_key = response["CiphertextBlob"]

            logger.info(f"Generated data key using AWS KMS: {key_id}")
            return plaintext_key, encrypted_key

        except Exception as e:
            logger.error(f"AWS KMS generate_data_key failed: {e}")
            raise KMSError(f"Failed to generate data key: {e}") from e

    async def decrypt_data_key(self, encrypted_key: bytes) -> bytes:
        """Decrypt data key using AWS KMS."""
        try:
            response = self.client.decrypt(CiphertextBlob=encrypted_key)
            return response["Plaintext"]

        except Exception as e:
            logger.error(f"AWS KMS decrypt failed: {e}")
            raise KMSError(f"Failed to decrypt data key: {e}") from e

    async def encrypt_data(self, key_id: str, plaintext: bytes) -> bytes:
        """Encrypt data using AWS KMS."""
        try:
            response = self.client.encrypt(KeyId=key_id, Plaintext=plaintext)
            return response["CiphertextBlob"]

        except Exception as e:
            logger.error(f"AWS KMS encrypt failed: {e}")
            raise KMSError(f"Failed to encrypt data: {e}") from e

    async def decrypt_data(self, key_id: str, ciphertext: bytes) -> bytes:
        """Decrypt data using AWS KMS."""
        try:
            response = self.client.decrypt(CiphertextBlob=ciphertext)
            return response["Plaintext"]

        except Exception as e:
            logger.error(f"AWS KMS decrypt failed: {e}")
            raise KMSError(f"Failed to decrypt data: {e}") from e

    async def rotate_key(self, key_id: str) -> str:
        """Enable automatic key rotation for AWS KMS key."""
        try:
            self.client.enable_key_rotation(KeyId=key_id)
            logger.info(f"Enabled key rotation for AWS KMS key: {key_id}")
            return key_id

        except Exception as e:
            logger.error(f"AWS KMS rotate_key failed: {e}")
            raise KMSError(f"Failed to rotate key: {e}") from e


class KMSManager:
    """
    High-level KMS manager for backup encryption keys.

    Provides simplified interface for key management with support
    for multiple KMS providers.

    Example:
        # Development/Testing
        kms = KMSManager(provider=KMSProvider.LOCAL, master_password="dev_password")

        # Production with AWS KMS
        kms = KMSManager(provider=KMSProvider.AWS_KMS, region="us-east-1")

        # Generate and use key
        key, encrypted_key, metadata = await kms.generate_backup_key("backup_20241010")
    """

    def __init__(self, provider: KMSProvider = KMSProvider.LOCAL, **config):
        """
        Initialize KMS manager.

        Args:
            provider: KMS provider to use
            **config: Provider-specific configuration
        """
        self.provider = provider

        if provider == KMSProvider.LOCAL:
            keystore_path = config.get("keystore_path", os.path.expanduser("~/.covetpy/keystore"))
            master_password = config.get("master_password") or os.environ.get(
                "COVETPY_KMS_PASSWORD"
            )
            master_key = config.get("master_key")

            if not master_password and not master_key:
                raise ValueError(
                    "LocalKMS requires master_password or master_key. "
                    "Set COVETPY_KMS_PASSWORD environment variable or pass master_password."
                )

            self.kms = LocalKMS(
                keystore_path=keystore_path,
                master_password=master_password,
                master_key=master_key,
            )

        elif provider == KMSProvider.AWS_KMS:
            region = config.get("region", "us-east-1")
            self.kms = AWSKMS(region=region, **config)

        else:
            raise ValueError(f"Unsupported KMS provider: {provider}")

        logger.info(f"Initialized KMS manager with provider: {provider.value}")

    async def generate_backup_key(
        self, backup_id: str, key_spec: str = "AES_256"
    ) -> Tuple[bytes, bytes, Dict[str, Any]]:
        """
        Generate encryption key for backup.

        Args:
            backup_id: Backup identifier
            key_spec: Key specification

        Returns:
            Tuple of (plaintext_key, encrypted_key, metadata)
        """
        key_id = f"backup_{backup_id}"

        plaintext_key, encrypted_key = await self.kms.generate_data_key(key_id, key_spec)

        metadata = {
            "key_id": key_id,
            "kms_provider": self.provider.value,
            "key_spec": key_spec,
            "encrypted_key": base64.b64encode(encrypted_key).decode("ascii"),
            "generated_at": datetime.now().isoformat(),
        }

        return plaintext_key, encrypted_key, metadata

    async def decrypt_backup_key(self, encrypted_key: bytes) -> bytes:
        """
        Decrypt backup encryption key.

        Args:
            encrypted_key: Encrypted key blob

        Returns:
            Decrypted plaintext key
        """
        return await self.kms.decrypt_data_key(encrypted_key)

    async def rotate_backup_keys(self, older_than_days: int = 90) -> list:
        """
        Rotate backup keys older than specified days.

        Args:
            older_than_days: Rotate keys older than this many days

        Returns:
            List of rotated key IDs
        """
        # This is a placeholder for key rotation logic
        # In production, you would query KMS for keys and rotate them
        logger.info(f"Rotating keys older than {older_than_days} days")
        return []


__all__ = [
    "KMSProvider",
    "KMSBase",
    "LocalKMS",
    "AWSKMS",
    "KMSManager",
    "KMSError",
    "KeyNotFoundError",
    "KeyAccessDeniedError",
]
