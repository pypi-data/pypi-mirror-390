"""
Azure Key Vault Integration
===========================

Integration with Microsoft Azure Key Vault for enterprise key management,
secret storage, and certificate management.

Features:
- Azure Key Vault key management
- Secret storage and retrieval
- Certificate management
- Managed Identity support
- RBAC integration
- Soft delete and purge protection
- Key versioning
- HSM-backed keys

Security:
- FIPS 140-2 Level 2 validated HSMs (Premium tier)
- Azure AD authentication
- Network access control
- Private endpoint support
- Audit logging via Azure Monitor

NOTE: Requires azure-identity and azure-keyvault libraries.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AzureKeyType(str, Enum):
    """Azure Key Vault key types."""

    RSA = "RSA"
    RSA_HSM = "RSA-HSM"
    EC = "EC"
    EC_HSM = "EC-HSM"
    OCT = "oct"  # Symmetric key
    OCT_HSM = "oct-HSM"


class AzureKeyOperation(str, Enum):
    """Key operations."""

    ENCRYPT = "encrypt"
    DECRYPT = "decrypt"
    SIGN = "sign"
    VERIFY = "verify"
    WRAP_KEY = "wrapKey"
    UNWRAP_KEY = "unwrapKey"


@dataclass
class AzureKeyMetadata:
    """Azure Key Vault key metadata."""

    key_id: str
    name: str
    version: str
    key_type: str
    enabled: bool
    created: datetime
    updated: datetime
    expires: Optional[datetime] = None
    not_before: Optional[datetime] = None
    tags: Optional[Dict[str, str]] = None


class AzureKMSProvider:
    """
    Azure Key Vault provider for enterprise key management.

    Integrates with Azure Key Vault for secure key storage and
    cryptographic operations.
    """

    def __init__(
        self, vault_url: str, credential: Optional[Any] = None, use_managed_identity: bool = True
    ):
        """
        Initialize Azure Key Vault provider.

        Args:
            vault_url: Key Vault URL (e.g., https://myvault.vault.azure.net/)
            credential: Azure credential (optional if using managed identity)
            use_managed_identity: Use Azure Managed Identity

        Raises:
            ImportError: If Azure SDK not installed
        """
        try:
            from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
            from azure.keyvault.certificates import CertificateClient
            from azure.keyvault.keys import KeyClient
            from azure.keyvault.secrets import SecretClient

            self.KeyClient = KeyClient
            self.SecretClient = SecretClient
            self.CertificateClient = CertificateClient
        except ImportError:
            raise ImportError(
                "Azure SDK required for Azure Key Vault integration. "
                "Install with: pip install azure-identity azure-keyvault-keys "
                "azure-keyvault-secrets azure-keyvault-certificates"
            )

        # Initialize credential
        if credential is None:
            if use_managed_identity:
                from azure.identity import ManagedIdentityCredential

                credential = ManagedIdentityCredential()
            else:
                from azure.identity import DefaultAzureCredential

                credential = DefaultAzureCredential()

        self.vault_url = vault_url
        self.credential = credential

        # Initialize clients
        self.key_client = KeyClient(vault_url=vault_url, credential=credential)
        self.secret_client = SecretClient(vault_url=vault_url, credential=credential)
        self.cert_client = CertificateClient(vault_url=vault_url, credential=credential)

    def create_key(
        self,
        name: str,
        key_type: AzureKeyType = AzureKeyType.RSA,
        key_size: Optional[int] = None,
        key_operations: Optional[List[AzureKeyOperation]] = None,
        enabled: bool = True,
        expires: Optional[datetime] = None,
        not_before: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> AzureKeyMetadata:
        """
        Create Azure Key Vault key.

        Args:
            name: Key name
            key_type: Key type
            key_size: Key size in bits (2048, 3072, 4096 for RSA)
            key_operations: Allowed operations
            enabled: Enable key
            expires: Expiration date
            not_before: Not valid before date
            tags: Resource tags

        Returns:
            Key metadata
        """
        from azure.keyvault.keys import KeyType

        # Map key type
        key_type_map = {
            AzureKeyType.RSA: KeyType.RSA,
            AzureKeyType.RSA_HSM: KeyType.RSA_HSM,
            AzureKeyType.EC: KeyType.EC,
            AzureKeyType.EC_HSM: KeyType.EC_HSM,
            AzureKeyType.OCT: KeyType.OCT,
            AzureKeyType.OCT_HSM: KeyType.OCT_HSM,
        }

        kwargs = {"name": name, "key_type": key_type_map[key_type]}

        if key_size:
            kwargs["size"] = key_size

        if key_operations:
            from azure.keyvault.keys import KeyOperation

            ops_map = {
                AzureKeyOperation.ENCRYPT: KeyOperation.ENCRYPT,
                AzureKeyOperation.DECRYPT: KeyOperation.DECRYPT,
                AzureKeyOperation.SIGN: KeyOperation.SIGN,
                AzureKeyOperation.VERIFY: KeyOperation.VERIFY,
                AzureKeyOperation.WRAP_KEY: KeyOperation.WRAP_KEY,
                AzureKeyOperation.UNWRAP_KEY: KeyOperation.UNWRAP_KEY,
            }
            kwargs["key_operations"] = [ops_map[op] for op in key_operations]

        if not enabled:
            kwargs["enabled"] = enabled
        if expires:
            kwargs["expires_on"] = expires
        if not_before:
            kwargs["not_before"] = not_before
        if tags:
            kwargs["tags"] = tags

        try:
            key = self.key_client.create_key(**kwargs)

            return AzureKeyMetadata(
                key_id=key.id,
                name=key.name,
                version=key.properties.version,
                key_type=key.key_type.value,
                enabled=key.properties.enabled,
                created=key.properties.created_on,
                updated=key.properties.updated_on,
                expires=key.properties.expires_on,
                not_before=key.properties.not_before,
                tags=key.properties.tags,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create Azure key: {str(e)}")

    def get_key(self, name: str, version: Optional[str] = None) -> AzureKeyMetadata:
        """
        Get key metadata.

        Args:
            name: Key name
            version: Key version (latest if None)

        Returns:
            Key metadata
        """
        try:
            if version:
                key = self.key_client.get_key(name, version)
            else:
                key = self.key_client.get_key(name)

            return AzureKeyMetadata(
                key_id=key.id,
                name=key.name,
                version=key.properties.version,
                key_type=key.key_type.value,
                enabled=key.properties.enabled,
                created=key.properties.created_on,
                updated=key.properties.updated_on,
                expires=key.properties.expires_on,
                not_before=key.properties.not_before,
                tags=key.properties.tags,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to get key: {str(e)}")

    def encrypt(
        self,
        key_name: str,
        plaintext: bytes,
        algorithm: str = "RSA-OAEP-256",
        version: Optional[str] = None,
    ) -> bytes:
        """
        Encrypt data using Azure Key Vault.

        Args:
            key_name: Key name
            plaintext: Data to encrypt
            algorithm: Encryption algorithm
            version: Key version

        Returns:
            Ciphertext
        """
        from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

        try:
            # Get key
            if version:
                key = self.key_client.get_key(key_name, version)
            else:
                key = self.key_client.get_key(key_name)

            # Create crypto client
            crypto_client = CryptographyClient(key, credential=self.credential)

            # Map algorithm
            algo_map = {
                "RSA-OAEP": EncryptionAlgorithm.rsa_oaep,
                "RSA-OAEP-256": EncryptionAlgorithm.rsa_oaep_256,
                "RSA1_5": EncryptionAlgorithm.rsa1_5,
            }

            result = crypto_client.encrypt(
                algo_map.get(algorithm, EncryptionAlgorithm.rsa_oaep_256), plaintext
            )

            return result.ciphertext
        except Exception as e:
            raise RuntimeError(f"Azure encryption failed: {str(e)}")

    def decrypt(
        self,
        key_name: str,
        ciphertext: bytes,
        algorithm: str = "RSA-OAEP-256",
        version: Optional[str] = None,
    ) -> bytes:
        """
        Decrypt data using Azure Key Vault.

        Args:
            key_name: Key name
            ciphertext: Encrypted data
            algorithm: Encryption algorithm
            version: Key version

        Returns:
            Plaintext
        """
        from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm

        try:
            # Get key
            if version:
                key = self.key_client.get_key(key_name, version)
            else:
                key = self.key_client.get_key(key_name)

            # Create crypto client
            crypto_client = CryptographyClient(key, credential=self.credential)

            # Map algorithm
            algo_map = {
                "RSA-OAEP": EncryptionAlgorithm.rsa_oaep,
                "RSA-OAEP-256": EncryptionAlgorithm.rsa_oaep_256,
                "RSA1_5": EncryptionAlgorithm.rsa1_5,
            }

            result = crypto_client.decrypt(
                algo_map.get(algorithm, EncryptionAlgorithm.rsa_oaep_256), ciphertext
            )

            return result.plaintext
        except Exception as e:
            raise RuntimeError(f"Azure decryption failed: {str(e)}")

    def sign(
        self, key_name: str, digest: bytes, algorithm: str = "RS256", version: Optional[str] = None
    ) -> bytes:
        """
        Sign digest using Azure Key Vault.

        Args:
            key_name: Key name
            digest: Digest to sign (pre-hashed)
            algorithm: Signature algorithm
            version: Key version

        Returns:
            Signature
        """
        from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

        try:
            # Get key
            if version:
                key = self.key_client.get_key(key_name, version)
            else:
                key = self.key_client.get_key(key_name)

            # Create crypto client
            crypto_client = CryptographyClient(key, credential=self.credential)

            # Map algorithm
            algo_map = {
                "RS256": SignatureAlgorithm.rs256,
                "RS384": SignatureAlgorithm.rs384,
                "RS512": SignatureAlgorithm.rs512,
                "PS256": SignatureAlgorithm.ps256,
                "PS384": SignatureAlgorithm.ps384,
                "PS512": SignatureAlgorithm.ps512,
                "ES256": SignatureAlgorithm.es256,
                "ES384": SignatureAlgorithm.es384,
                "ES512": SignatureAlgorithm.es512,
            }

            result = crypto_client.sign(algo_map.get(algorithm, SignatureAlgorithm.rs256), digest)

            return result.signature
        except Exception as e:
            raise RuntimeError(f"Azure signing failed: {str(e)}")

    def verify(
        self,
        key_name: str,
        digest: bytes,
        signature: bytes,
        algorithm: str = "RS256",
        version: Optional[str] = None,
    ) -> bool:
        """
        Verify signature using Azure Key Vault.

        Args:
            key_name: Key name
            digest: Original digest
            signature: Signature to verify
            algorithm: Signature algorithm
            version: Key version

        Returns:
            True if signature valid
        """
        from azure.keyvault.keys.crypto import CryptographyClient, SignatureAlgorithm

        try:
            # Get key
            if version:
                key = self.key_client.get_key(key_name, version)
            else:
                key = self.key_client.get_key(key_name)

            # Create crypto client
            crypto_client = CryptographyClient(key, credential=self.credential)

            # Map algorithm
            algo_map = {
                "RS256": SignatureAlgorithm.rs256,
                "RS384": SignatureAlgorithm.rs384,
                "RS512": SignatureAlgorithm.rs512,
                "PS256": SignatureAlgorithm.ps256,
                "PS384": SignatureAlgorithm.ps384,
                "PS512": SignatureAlgorithm.ps512,
                "ES256": SignatureAlgorithm.es256,
                "ES384": SignatureAlgorithm.es384,
                "ES512": SignatureAlgorithm.es512,
            }

            result = crypto_client.verify(
                algo_map.get(algorithm, SignatureAlgorithm.rs256), digest, signature
            )

            return result.is_valid
        except Exception:
            return False

    def wrap_key(self, key_name: str, key_to_wrap: bytes, algorithm: str = "RSA-OAEP-256") -> bytes:
        """
        Wrap (encrypt) key using Key Vault key.

        Args:
            key_name: Wrapping key name
            key_to_wrap: Key material to wrap
            algorithm: Wrapping algorithm

        Returns:
            Wrapped key
        """
        from azure.keyvault.keys.crypto import CryptographyClient, KeyWrapAlgorithm

        try:
            key = self.key_client.get_key(key_name)
            crypto_client = CryptographyClient(key, credential=self.credential)

            algo_map = {
                "RSA-OAEP": KeyWrapAlgorithm.rsa_oaep,
                "RSA-OAEP-256": KeyWrapAlgorithm.rsa_oaep_256,
                "RSA1_5": KeyWrapAlgorithm.rsa1_5,
            }

            result = crypto_client.wrap_key(
                algo_map.get(algorithm, KeyWrapAlgorithm.rsa_oaep_256), key_to_wrap
            )

            return result.encrypted_key
        except Exception as e:
            raise RuntimeError(f"Key wrapping failed: {str(e)}")

    def unwrap_key(
        self, key_name: str, wrapped_key: bytes, algorithm: str = "RSA-OAEP-256"
    ) -> bytes:
        """
        Unwrap (decrypt) key using Key Vault key.

        Args:
            key_name: Wrapping key name
            wrapped_key: Wrapped key material
            algorithm: Wrapping algorithm

        Returns:
            Unwrapped key
        """
        from azure.keyvault.keys.crypto import CryptographyClient, KeyWrapAlgorithm

        try:
            key = self.key_client.get_key(key_name)
            crypto_client = CryptographyClient(key, credential=self.credential)

            algo_map = {
                "RSA-OAEP": KeyWrapAlgorithm.rsa_oaep,
                "RSA-OAEP-256": KeyWrapAlgorithm.rsa_oaep_256,
                "RSA1_5": KeyWrapAlgorithm.rsa1_5,
            }

            result = crypto_client.unwrap_key(
                algo_map.get(algorithm, KeyWrapAlgorithm.rsa_oaep_256), wrapped_key
            )

            return result.key
        except Exception as e:
            raise RuntimeError(f"Key unwrapping failed: {str(e)}")

    def set_secret(
        self,
        name: str,
        value: str,
        enabled: bool = True,
        content_type: Optional[str] = None,
        expires: Optional[datetime] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Store secret in Key Vault.

        Args:
            name: Secret name
            value: Secret value
            enabled: Enable secret
            content_type: Content type
            expires: Expiration date
            tags: Resource tags

        Returns:
            Secret ID
        """
        try:
            kwargs = {"name": name, "value": value}

            if not enabled:
                kwargs["enabled"] = enabled
            if content_type:
                kwargs["content_type"] = content_type
            if expires:
                kwargs["expires_on"] = expires
            if tags:
                kwargs["tags"] = tags

            secret = self.secret_client.set_secret(**kwargs)
            return secret.id
        except Exception as e:
            raise RuntimeError(f"Failed to set secret: {str(e)}")

    def get_secret(self, name: str, version: Optional[str] = None) -> str:
        """
        Retrieve secret from Key Vault.

        Args:
            name: Secret name
            version: Secret version (latest if None)

        Returns:
            Secret value
        """
        try:
            if version:
                secret = self.secret_client.get_secret(name, version)
            else:
                secret = self.secret_client.get_secret(name)

            return secret.value
        except Exception as e:
            raise RuntimeError(f"Failed to get secret: {str(e)}")

    def delete_secret(self, name: str):
        """
        Delete secret (soft delete).

        Args:
            name: Secret name
        """
        try:
            self.secret_client.begin_delete_secret(name).wait()
        except Exception as e:
            raise RuntimeError(f"Failed to delete secret: {str(e)}")

    def delete_key(self, name: str):
        """
        Delete key (soft delete).

        Args:
            name: Key name
        """
        try:
            self.key_client.begin_delete_key(name).wait()
        except Exception as e:
            raise RuntimeError(f"Failed to delete key: {str(e)}")

    def list_keys(self) -> List[AzureKeyMetadata]:
        """
        List all keys in vault.

        Returns:
            List of key metadata
        """
        try:
            keys = []
            for properties in self.key_client.list_properties_of_keys():
                keys.append(
                    AzureKeyMetadata(
                        key_id=properties.id,
                        name=properties.name,
                        version=properties.version,
                        key_type="unknown",  # Not available in list
                        enabled=properties.enabled,
                        created=properties.created_on,
                        updated=properties.updated_on,
                        expires=properties.expires_on,
                        not_before=properties.not_before,
                        tags=properties.tags,
                    )
                )
            return keys
        except Exception as e:
            raise RuntimeError(f"Failed to list keys: {str(e)}")


__all__ = [
    "AzureKeyType",
    "AzureKeyOperation",
    "AzureKeyMetadata",
    "AzureKMSProvider",
]
