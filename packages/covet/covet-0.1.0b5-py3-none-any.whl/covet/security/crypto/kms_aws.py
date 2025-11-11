"""
AWS KMS Integration
==================

Integration with Amazon Web Services Key Management Service for enterprise
key management with CloudHSM support.

Features:
- AWS KMS key creation and management
- Envelope encryption pattern
- CloudHSM integration
- IAM role-based access control
- Key alias management
- Automatic key rotation
- Cross-region key replication
- Grant-based access delegation

Security:
- FIPS 140-2 Level 3 validated HSMs
- Separation of duties
- Audit logging via CloudTrail
- VPC endpoint support

NOTE: Requires boto3 library for AWS SDK.
"""

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class AWSKeySpec(str, Enum):
    """AWS KMS key specifications."""

    SYMMETRIC_DEFAULT = "SYMMETRIC_DEFAULT"  # AES-256-GCM
    RSA_2048 = "RSA_2048"
    RSA_3072 = "RSA_3072"
    RSA_4096 = "RSA_4096"
    ECC_NIST_P256 = "ECC_NIST_P256"
    ECC_NIST_P384 = "ECC_NIST_P384"
    ECC_NIST_P521 = "ECC_NIST_P521"
    ECC_SECG_P256K1 = "ECC_SECG_P256K1"


class AWSKeyUsage(str, Enum):
    """AWS KMS key usage."""

    ENCRYPT_DECRYPT = "ENCRYPT_DECRYPT"
    SIGN_VERIFY = "SIGN_VERIFY"


@dataclass
class AWSKeyMetadata:
    """AWS KMS key metadata."""

    key_id: str
    arn: str
    alias: Optional[str]
    key_spec: str
    key_usage: str
    creation_date: datetime
    enabled: bool
    key_state: str
    origin: str
    description: Optional[str] = None


class AWSKMSProvider:
    """
    AWS KMS provider for enterprise key management.

    Integrates with AWS KMS for hardware-backed key storage and
    cryptographic operations.
    """

    def __init__(
        self,
        region_name: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        use_iam_role: bool = True,
    ):
        """
        Initialize AWS KMS provider.

        Args:
            region_name: AWS region
            aws_access_key_id: AWS access key (optional if using IAM role)
            aws_secret_access_key: AWS secret key (optional if using IAM role)
            aws_session_token: AWS session token (for temporary credentials)
            use_iam_role: Use IAM role for authentication

        Raises:
            ImportError: If boto3 not installed
        """
        try:
            import boto3

            self.boto3 = boto3
        except ImportError:
            raise ImportError(
                "boto3 required for AWS KMS integration. " "Install with: pip install boto3"
            )

        # Initialize KMS client
        if use_iam_role:
            # Use IAM role credentials
            self.kms_client = boto3.client("kms", region_name=region_name)
        else:
            # Use explicit credentials
            self.kms_client = boto3.client(
                "kms",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
            )

        self.region_name = region_name

    def create_key(
        self,
        description: str,
        key_spec: AWSKeySpec = AWSKeySpec.SYMMETRIC_DEFAULT,
        key_usage: AWSKeyUsage = AWSKeyUsage.ENCRYPT_DECRYPT,
        origin: str = "AWS_KMS",
        policy: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        multi_region: bool = False,
    ) -> AWSKeyMetadata:
        """
        Create AWS KMS key.

        Args:
            description: Key description
            key_spec: Key specification
            key_usage: Key usage
            origin: Key origin (AWS_KMS, EXTERNAL, AWS_CLOUDHSM)
            policy: Key policy (IAM policy document)
            tags: Resource tags
            multi_region: Create multi-region key

        Returns:
            Key metadata
        """
        kwargs = {
            "Description": description,
            "KeySpec": key_spec.value,
            "KeyUsage": key_usage.value,
            "Origin": origin,
            "MultiRegion": multi_region,
        }

        if policy:
            kwargs["Policy"] = json.dumps(policy)

        if tags:
            kwargs["Tags"] = [{"TagKey": k, "TagValue": v} for k, v in tags.items()]

        try:
            response = self.kms_client.create_key(**kwargs)
            metadata = response["KeyMetadata"]

            return AWSKeyMetadata(
                key_id=metadata["KeyId"],
                arn=metadata["Arn"],
                alias=None,
                key_spec=metadata["KeySpec"],
                key_usage=metadata["KeyUsage"],
                creation_date=metadata["CreationDate"],
                enabled=metadata["Enabled"],
                key_state=metadata["KeyState"],
                origin=metadata["Origin"],
                description=metadata.get("Description"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create AWS KMS key: {str(e)}")

    def create_alias(self, alias_name: str, key_id: str):
        """
        Create alias for key.

        Args:
            alias_name: Alias name (must start with 'alias/')
            key_id: Key ID or ARN
        """
        if not alias_name.startswith("alias/"):
            alias_name = f"alias/{alias_name}"

        try:
            self.kms_client.create_alias(AliasName=alias_name, TargetKeyId=key_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create alias: {str(e)}")

    def encrypt(
        self, key_id: str, plaintext: bytes, encryption_context: Optional[Dict[str, str]] = None
    ) -> bytes:
        """
        Encrypt data using AWS KMS.

        Args:
            key_id: Key ID, ARN, or alias
            plaintext: Data to encrypt
            encryption_context: Additional authenticated data

        Returns:
            Ciphertext blob
        """
        kwargs = {"KeyId": key_id, "Plaintext": plaintext}

        if encryption_context:
            kwargs["EncryptionContext"] = encryption_context

        try:
            response = self.kms_client.encrypt(**kwargs)
            return response["CiphertextBlob"]
        except Exception as e:
            raise RuntimeError(f"AWS KMS encryption failed: {str(e)}")

    def decrypt(
        self, ciphertext: bytes, encryption_context: Optional[Dict[str, str]] = None
    ) -> bytes:
        """
        Decrypt data using AWS KMS.

        Args:
            ciphertext: Encrypted data
            encryption_context: Additional authenticated data (must match encryption)

        Returns:
            Decrypted plaintext
        """
        kwargs = {"CiphertextBlob": ciphertext}

        if encryption_context:
            kwargs["EncryptionContext"] = encryption_context

        try:
            response = self.kms_client.decrypt(**kwargs)
            return response["Plaintext"]
        except Exception as e:
            raise RuntimeError(f"AWS KMS decryption failed: {str(e)}")

    def generate_data_key(
        self,
        key_id: str,
        key_spec: str = "AES_256",
        encryption_context: Optional[Dict[str, str]] = None,
    ) -> tuple[bytes, bytes]:
        """
        Generate data encryption key (envelope encryption pattern).

        Args:
            key_id: Master key ID
            key_spec: Data key specification (AES_256, AES_128)
            encryption_context: Additional authenticated data

        Returns:
            Tuple of (plaintext_key, encrypted_key)
        """
        kwargs = {"KeyId": key_id, "KeySpec": key_spec}

        if encryption_context:
            kwargs["EncryptionContext"] = encryption_context

        try:
            response = self.kms_client.generate_data_key(**kwargs)
            return response["Plaintext"], response["CiphertextBlob"]
        except Exception as e:
            raise RuntimeError(f"Failed to generate data key: {str(e)}")

    def envelope_encrypt(
        self, key_id: str, plaintext: bytes, encryption_context: Optional[Dict[str, str]] = None
    ) -> Dict[str, bytes]:
        """
        Envelope encryption pattern.

        Generates a data key, encrypts data locally, and returns both
        encrypted data and encrypted data key.

        Args:
            key_id: Master key ID
            plaintext: Data to encrypt
            encryption_context: Additional authenticated data

        Returns:
            Dictionary with encrypted_data and encrypted_key
        """
        # Generate data encryption key
        plaintext_key, encrypted_key = self.generate_data_key(
            key_id, encryption_context=encryption_context
        )

        # Encrypt data locally with data key
        from .symmetric import AESCipher, EncryptionMode

        cipher = AESCipher(plaintext_key, EncryptionMode.AES_GCM)
        result = cipher.encrypt(plaintext)

        return {"encrypted_data": result.to_bytes(), "encrypted_key": encrypted_key}

    def envelope_decrypt(
        self,
        encrypted_data: bytes,
        encrypted_key: bytes,
        encryption_context: Optional[Dict[str, str]] = None,
    ) -> bytes:
        """
        Envelope decryption pattern.

        Decrypts data key using KMS, then decrypts data locally.

        Args:
            encrypted_data: Encrypted data
            encrypted_key: Encrypted data key
            encryption_context: Additional authenticated data

        Returns:
            Decrypted plaintext
        """
        # Decrypt data key using KMS
        plaintext_key = self.decrypt(encrypted_key, encryption_context)

        # Decrypt data locally
        from .symmetric import AESCipher, EncryptionMode, EncryptionResult

        cipher = AESCipher(plaintext_key, EncryptionMode.AES_GCM)
        result = EncryptionResult.from_bytes(encrypted_data)

        return cipher.decrypt(result)

    def sign(
        self, key_id: str, message: bytes, signing_algorithm: str = "RSASSA_PSS_SHA_256"
    ) -> bytes:
        """
        Sign message using AWS KMS.

        Args:
            key_id: Key ID (must be asymmetric signing key)
            message: Message to sign
            signing_algorithm: Signing algorithm

        Returns:
            Digital signature
        """
        try:
            response = self.kms_client.sign(
                KeyId=key_id, Message=message, SigningAlgorithm=signing_algorithm
            )
            return response["Signature"]
        except Exception as e:
            raise RuntimeError(f"AWS KMS signing failed: {str(e)}")

    def verify(
        self,
        key_id: str,
        message: bytes,
        signature: bytes,
        signing_algorithm: str = "RSASSA_PSS_SHA_256",
    ) -> bool:
        """
        Verify signature using AWS KMS.

        Args:
            key_id: Key ID
            message: Original message
            signature: Signature to verify
            signing_algorithm: Signing algorithm

        Returns:
            True if signature valid
        """
        try:
            response = self.kms_client.verify(
                KeyId=key_id,
                Message=message,
                Signature=signature,
                SigningAlgorithm=signing_algorithm,
            )
            return response["SignatureValid"]
        except Exception:
            return False

    def enable_key_rotation(self, key_id: str):
        """
        Enable automatic key rotation.

        Args:
            key_id: Key ID
        """
        try:
            self.kms_client.enable_key_rotation(KeyId=key_id)
        except Exception as e:
            raise RuntimeError(f"Failed to enable key rotation: {str(e)}")

    def disable_key_rotation(self, key_id: str):
        """
        Disable automatic key rotation.

        Args:
            key_id: Key ID
        """
        try:
            self.kms_client.disable_key_rotation(KeyId=key_id)
        except Exception as e:
            raise RuntimeError(f"Failed to disable key rotation: {str(e)}")

    def get_key_rotation_status(self, key_id: str) -> bool:
        """
        Get key rotation status.

        Args:
            key_id: Key ID

        Returns:
            True if rotation enabled
        """
        try:
            response = self.kms_client.get_key_rotation_status(KeyId=key_id)
            return response["KeyRotationEnabled"]
        except Exception as e:
            raise RuntimeError(f"Failed to get rotation status: {str(e)}")

    def describe_key(self, key_id: str) -> AWSKeyMetadata:
        """
        Get key metadata.

        Args:
            key_id: Key ID, ARN, or alias

        Returns:
            Key metadata
        """
        try:
            response = self.kms_client.describe_key(KeyId=key_id)
            metadata = response["KeyMetadata"]

            return AWSKeyMetadata(
                key_id=metadata["KeyId"],
                arn=metadata["Arn"],
                alias=None,
                key_spec=metadata["KeySpec"],
                key_usage=metadata["KeyUsage"],
                creation_date=metadata["CreationDate"],
                enabled=metadata["Enabled"],
                key_state=metadata["KeyState"],
                origin=metadata["Origin"],
                description=metadata.get("Description"),
            )
        except Exception as e:
            raise RuntimeError(f"Failed to describe key: {str(e)}")

    def list_keys(self, limit: int = 100) -> List[str]:
        """
        List KMS keys.

        Args:
            limit: Maximum number of keys to return

        Returns:
            List of key IDs
        """
        try:
            response = self.kms_client.list_keys(Limit=limit)
            return [key["KeyId"] for key in response["Keys"]]
        except Exception as e:
            raise RuntimeError(f"Failed to list keys: {str(e)}")

    def schedule_key_deletion(self, key_id: str, pending_days: int = 30):
        """
        Schedule key deletion (cannot be reversed after deletion).

        Args:
            key_id: Key ID
            pending_days: Days until deletion (7-30)
        """
        try:
            self.kms_client.schedule_key_deletion(KeyId=key_id, PendingWindowInDays=pending_days)
        except Exception as e:
            raise RuntimeError(f"Failed to schedule key deletion: {str(e)}")

    def cancel_key_deletion(self, key_id: str):
        """
        Cancel scheduled key deletion.

        Args:
            key_id: Key ID
        """
        try:
            self.kms_client.cancel_key_deletion(KeyId=key_id)
        except Exception as e:
            raise RuntimeError(f"Failed to cancel key deletion: {str(e)}")

    def create_grant(
        self,
        key_id: str,
        grantee_principal: str,
        operations: List[str],
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create grant for delegated access.

        Args:
            key_id: Key ID
            grantee_principal: ARN of grantee
            operations: List of operations (Encrypt, Decrypt, etc.)
            constraints: Grant constraints

        Returns:
            Grant ID
        """
        kwargs = {"KeyId": key_id, "GranteePrincipal": grantee_principal, "Operations": operations}

        if constraints:
            kwargs["Constraints"] = constraints

        try:
            response = self.kms_client.create_grant(**kwargs)
            return response["GrantId"]
        except Exception as e:
            raise RuntimeError(f"Failed to create grant: {str(e)}")


__all__ = [
    "AWSKeySpec",
    "AWSKeyUsage",
    "AWSKeyMetadata",
    "AWSKMSProvider",
]
