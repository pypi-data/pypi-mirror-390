"""
KMS Integration Demo
===================

Demonstrates Key Management System usage:
- Key creation and management
- Key rotation
- Envelope encryption
- AWS/Azure KMS integration examples
- Production best practices
"""

import sys
import os
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.covet.security.crypto.kms import (
    KeyManagementSystem,
    KeyPurpose,
    KeyStatus,
    KeyRotationPolicy,
)


def demo_basic_kms():
    """Demo basic KMS operations."""
    print("\n" + "="*60)
    print("Basic KMS Operations Demo")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "demo_keys.db")

        # Initialize KMS
        kms = KeyManagementSystem(storage_path=storage_path)
        print("✓ KMS initialized")

        # Create encryption key
        print("\n1. Creating encryption key...")
        metadata = kms.create_key(
            key_id="app_db_encryption",
            purpose=KeyPurpose.ENCRYPT,
            algorithm="AES-256-GCM",
            tags={"app": "demo", "env": "production"}
        )

        print(f"   Key ID: {metadata.key_id}")
        print(f"   Version: {metadata.version}")
        print(f"   Status: {metadata.status.value}")
        print(f"   Algorithm: {metadata.algorithm}")

        # Encrypt data
        print("\n2. Encrypting data...")
        plaintext = b"Sensitive customer data"
        encrypted = kms.encrypt_data("app_db_encryption", plaintext)
        print(f"   ✓ Data encrypted ({len(encrypted.ciphertext)} bytes)")

        # Decrypt data
        print("\n3. Decrypting data...")
        decrypted = kms.decrypt_data("app_db_encryption", encrypted)
        print(f"   ✓ Data decrypted: {decrypted.decode()}")

        assert plaintext == decrypted
        print("\n✓ Basic KMS operations successful!")


def demo_key_rotation():
    """Demo automatic key rotation."""
    print("\n" + "="*60)
    print("Key Rotation Demo")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "rotation_keys.db")

        # Initialize KMS with rotation policy
        rotation_policy = KeyRotationPolicy(
            enabled=True,
            rotation_interval_days=90,
            max_versions=5,
            auto_deactivate_old_versions=True,
            grace_period_days=7
        )

        kms = KeyManagementSystem(
            storage_path=storage_path,
            rotation_policy=rotation_policy
        )

        print("✓ KMS initialized with rotation policy")
        print(f"  Rotation interval: {rotation_policy.rotation_interval_days} days")

        # Create key
        print("\n1. Creating key...")
        kms.create_key(key_id="rotating_key", purpose=KeyPurpose.ENCRYPT)

        # Encrypt data with version 1
        print("\n2. Encrypting with version 1...")
        data_v1 = b"Data encrypted with version 1"
        encrypted_v1 = kms.encrypt_data("rotating_key", data_v1)
        print("   ✓ Encrypted with version 1")

        # Rotate key
        print("\n3. Rotating key...")
        new_metadata = kms.rotate_key("rotating_key")
        print(f"   ✓ Key rotated to version {new_metadata.version}")

        # Encrypt data with version 2
        print("\n4. Encrypting with version 2...")
        data_v2 = b"Data encrypted with version 2"
        encrypted_v2 = kms.encrypt_data("rotating_key", data_v2)
        print("   ✓ Encrypted with version 2")

        # Decrypt both versions
        print("\n5. Decrypting data...")
        decrypted_v1 = kms.decrypt_data("rotating_key", encrypted_v1, version=1)
        print(f"   ✓ Decrypted v1: {decrypted_v1.decode()}")

        decrypted_v2 = kms.decrypt_data("rotating_key", encrypted_v2)
        print(f"   ✓ Decrypted v2 (latest): {decrypted_v2.decode()}")

        assert data_v1 == decrypted_v1
        assert data_v2 == decrypted_v2

        print("\n✓ Key rotation successful!")


def demo_key_lifecycle():
    """Demo complete key lifecycle."""
    print("\n" + "="*60)
    print("Key Lifecycle Demo")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "lifecycle_keys.db")
        kms = KeyManagementSystem(storage_path=storage_path)

        # Create key
        print("\n1. ACTIVE: Creating key...")
        kms.create_key(key_id="lifecycle_key", purpose=KeyPurpose.ENCRYPT)
        print("   ✓ Key is ACTIVE")

        # Use key
        print("\n2. Using key for encryption...")
        plaintext = b"Test data"
        encrypted = kms.encrypt_data("lifecycle_key", plaintext)
        print("   ✓ Data encrypted")

        # Deactivate key
        print("\n3. DEACTIVATED: Deactivating key...")
        kms.deactivate_key("lifecycle_key")
        print("   ✓ Key is DEACTIVATED")

        # Can still decrypt old data
        print("\n4. Decrypting old data with deactivated key...")
        decrypted = kms.decrypt_data("lifecycle_key", encrypted)
        assert plaintext == decrypted
        print("   ✓ Old data still accessible")

        # List keys
        print("\n5. Listing keys...")
        active_keys = kms.list_keys(status=KeyStatus.ACTIVE)
        deactivated_keys = kms.list_keys(status=KeyStatus.DEACTIVATED)

        print(f"   Active keys: {len(active_keys)}")
        print(f"   Deactivated keys: {len(deactivated_keys)}")

        print("\n✓ Key lifecycle complete!")


def demo_audit_logging():
    """Demo KMS audit logging."""
    print("\n" + "="*60)
    print("Audit Logging Demo")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "audit_keys.db")
        kms = KeyManagementSystem(storage_path=storage_path)

        # Perform operations
        print("\n1. Performing operations...")
        kms.create_key(key_id="audited_key", purpose=KeyPurpose.ENCRYPT)
        kms.get_key("audited_key")
        kms.encrypt_data("audited_key", b"test")
        kms.rotate_key("audited_key")

        # Get audit log
        print("\n2. Retrieving audit log...")
        logs = kms.get_audit_log(key_id="audited_key")

        print(f"\n   Found {len(logs)} audit entries:")
        for log in logs:
            print(f"   - {log['timestamp']}: {log['action']} - {log['details']}")

        print("\n✓ Audit logging working!")


def demo_envelope_encryption():
    """Demo envelope encryption pattern."""
    print("\n" + "="*60)
    print("Envelope Encryption Demo")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        storage_path = os.path.join(tmpdir, "envelope_keys.db")
        kms = KeyManagementSystem(storage_path=storage_path)

        # Create master key (KEK - Key Encryption Key)
        print("\n1. Creating master key (KEK)...")
        kms.create_key(
            key_id="master_key",
            purpose=KeyPurpose.WRAP,
            algorithm="AES-256-GCM"
        )
        print("   ✓ Master key created")

        # Encrypt large data
        print("\n2. Encrypting large dataset...")
        large_data = b"Large dataset " * 10000
        print(f"   Data size: {len(large_data)} bytes")

        encrypted = kms.encrypt_data("master_key", large_data)
        print(f"   Encrypted size: {len(encrypted.ciphertext)} bytes")

        # Decrypt
        print("\n3. Decrypting data...")
        decrypted = kms.decrypt_data("master_key", encrypted)
        print(f"   Decrypted size: {len(decrypted)} bytes")

        assert large_data == decrypted
        print("\n✓ Envelope encryption successful!")


def demo_aws_kms_integration():
    """Demo AWS KMS integration (requires boto3)."""
    print("\n" + "="*60)
    print("AWS KMS Integration Demo")
    print("="*60)

    try:
        from src.covet.security.crypto.kms_aws import AWSKMSProvider, AWSKeySpec

        print("\nNOTE: This demo requires:")
        print("  1. boto3 installed: pip install boto3")
        print("  2. AWS credentials configured")
        print("  3. IAM permissions for KMS operations")

        print("\n Example usage:")
        print("""
        # Initialize AWS KMS
        aws_kms = AWSKMSProvider(
            region_name="us-east-1",
            use_iam_role=True
        )

        # Create key
        metadata = aws_kms.create_key(
            description="Application encryption key",
            key_spec=AWSKeySpec.SYMMETRIC_DEFAULT
        )

        # Encrypt data
        plaintext = b"Secret data"
        ciphertext = aws_kms.encrypt(
            metadata.key_id,
            plaintext,
            encryption_context={"app": "demo"}
        )

        # Decrypt data
        decrypted = aws_kms.decrypt(
            ciphertext,
            encryption_context={"app": "demo"}
        )

        # Envelope encryption
        result = aws_kms.envelope_encrypt(
            metadata.key_id,
            b"Large data",
            encryption_context={"purpose": "backup"}
        )

        # Enable automatic rotation
        aws_kms.enable_key_rotation(metadata.key_id)
        """)

        print("\n✓ AWS KMS integration available")

    except ImportError:
        print("\n! AWS KMS requires boto3: pip install boto3")


def demo_azure_kms_integration():
    """Demo Azure Key Vault integration (requires azure-identity)."""
    print("\n" + "="*60)
    print("Azure Key Vault Integration Demo")
    print("="*60)

    try:
        from src.covet.security.crypto.kms_azure import AzureKMSProvider, AzureKeyType

        print("\nNOTE: This demo requires:")
        print("  1. Azure SDK installed: pip install azure-identity azure-keyvault-keys")
        print("  2. Azure credentials configured")
        print("  3. Key Vault created")

        print("\nExample usage:")
        print("""
        # Initialize Azure Key Vault
        azure_kms = AzureKMSProvider(
            vault_url="https://myvault.vault.azure.net/",
            use_managed_identity=True
        )

        # Create key
        metadata = azure_kms.create_key(
            name="app-encryption-key",
            key_type=AzureKeyType.RSA,
            key_size=2048
        )

        # Encrypt data
        plaintext = b"Secret data"
        ciphertext = azure_kms.encrypt(
            "app-encryption-key",
            plaintext,
            algorithm="RSA-OAEP-256"
        )

        # Decrypt data
        decrypted = azure_kms.decrypt(
            "app-encryption-key",
            ciphertext,
            algorithm="RSA-OAEP-256"
        )

        # Store secret
        azure_kms.set_secret(
            "database-password",
            "super_secret_password",
            tags={"env": "production"}
        )
        """)

        print("\n✓ Azure Key Vault integration available")

    except ImportError:
        print("\n! Azure Key Vault requires azure-identity and azure-keyvault-keys")


def main():
    """Run all KMS demos."""
    print("\n" + "="*60)
    print("CovetPy Cryptography - KMS Integration Demo")
    print("="*60)

    try:
        demo_basic_kms()
        demo_key_rotation()
        demo_key_lifecycle()
        demo_audit_logging()
        demo_envelope_encryption()
        demo_aws_kms_integration()
        demo_azure_kms_integration()

        print("\n" + "="*60)
        print("All KMS demos completed!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
