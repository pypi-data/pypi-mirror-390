"""
Comprehensive Encryption Demo
=============================

Demonstrates all encryption capabilities of CovetPy cryptography module:
- Symmetric encryption (AES, ChaCha20)
- Asymmetric encryption (RSA, ECC)
- Hybrid encryption
- Key derivation
- Password-based encryption
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.covet.security.crypto.symmetric import (
    AESCipher,
    ChaCha20Cipher,
    EncryptionMode,
    derive_key_pbkdf2,
)
from src.covet.security.crypto.asymmetric import (
    KeyPairGenerator,
    RSACipher,
    ECCCipher,
    HybridCipher,
    RSAKeySize,
    ECCCurve,
)
from src.covet.security.crypto.random import generate_random_bytes


def demo_aes_gcm():
    """Demo AES-256-GCM encryption (recommended for most use cases)."""
    print("\n" + "="*60)
    print("AES-256-GCM Encryption Demo")
    print("="*60)

    # Generate key
    key = generate_random_bytes(32)
    cipher = AESCipher(key, EncryptionMode.AES_GCM)

    # Encrypt data
    plaintext = b"This is a secret message that needs encryption."
    print(f"Plaintext: {plaintext.decode()}")

    result = cipher.encrypt(plaintext)
    print(f"Ciphertext length: {len(result.ciphertext)} bytes")
    print(f"IV length: {len(result.iv)} bytes")
    print(f"Auth tag length: {len(result.tag)} bytes")

    # Decrypt data
    decrypted = cipher.decrypt(result)
    print(f"Decrypted: {decrypted.decode()}")

    assert plaintext == decrypted
    print("✓ Encryption/Decryption successful!")


def demo_aes_gcm_with_aad():
    """Demo AES-GCM with Additional Authenticated Data."""
    print("\n" + "="*60)
    print("AES-256-GCM with AAD Demo")
    print("="*60)

    key = generate_random_bytes(32)
    cipher = AESCipher(key, EncryptionMode.AES_GCM)

    plaintext = b"Confidential document content"
    metadata = b"user_id:12345,timestamp:2024-10-11"

    print(f"Plaintext: {plaintext.decode()}")
    print(f"Metadata (AAD): {metadata.decode()}")

    # Encrypt with AAD
    result = cipher.encrypt(plaintext, associated_data=metadata)

    # Decrypt with correct AAD
    decrypted = cipher.decrypt(result, associated_data=metadata)
    print(f"Decrypted: {decrypted.decode()}")

    # Try to decrypt with wrong AAD (will fail)
    try:
        wrong_metadata = b"user_id:99999,timestamp:2024-10-11"
        cipher.decrypt(result, associated_data=wrong_metadata)
        print("✗ Should have failed with wrong AAD!")
    except Exception:
        print("✓ Correctly rejected wrong AAD!")


def demo_chacha20():
    """Demo ChaCha20-Poly1305 encryption."""
    print("\n" + "="*60)
    print("ChaCha20-Poly1305 Encryption Demo")
    print("="*60)

    key = generate_random_bytes(32)
    cipher = ChaCha20Cipher(key)

    plaintext = b"ChaCha20 is faster than AES on systems without hardware acceleration"
    print(f"Plaintext: {plaintext.decode()}")

    result = cipher.encrypt(plaintext)
    decrypted = cipher.decrypt(result)

    print(f"Decrypted: {decrypted.decode()}")
    assert plaintext == decrypted
    print("✓ ChaCha20 encryption successful!")


def demo_password_based_encryption():
    """Demo password-based encryption using key derivation."""
    print("\n" + "="*60)
    print("Password-Based Encryption Demo")
    print("="*60)

    # Derive key from password
    password = "my_secure_password_123"
    print(f"Password: {password}")

    key, salt = derive_key_pbkdf2(password)
    print(f"Derived key length: {len(key)} bytes")
    print(f"Salt length: {len(salt)} bytes")

    # Encrypt data
    cipher = AESCipher(key, EncryptionMode.AES_GCM)
    plaintext = b"Data encrypted with password-derived key"

    result = cipher.encrypt(plaintext)
    print(f"Encrypted: {len(result.ciphertext)} bytes")

    # To decrypt, need same password and salt
    key2, _ = derive_key_pbkdf2(password, salt=salt)
    cipher2 = AESCipher(key2, EncryptionMode.AES_GCM)

    decrypted = cipher2.decrypt(result)
    print(f"Decrypted: {decrypted.decode()}")
    assert plaintext == decrypted
    print("✓ Password-based encryption successful!")


def demo_rsa_encryption():
    """Demo RSA public key encryption."""
    print("\n" + "="*60)
    print("RSA Encryption Demo")
    print("="*60)

    # Generate RSA key pair
    print("Generating RSA-2048 key pair...")
    keypair = KeyPairGenerator.generate_rsa(RSAKeySize.RSA_2048)
    print(f"✓ Key pair generated (size: {keypair.key_size} bits)")

    # Encrypt with public key
    cipher = RSACipher(keypair.public_key, keypair.private_key)
    plaintext = b"Secret message encrypted with RSA"

    print(f"Plaintext: {plaintext.decode()}")

    ciphertext = cipher.encrypt(plaintext)
    print(f"Ciphertext length: {len(ciphertext)} bytes")

    # Decrypt with private key
    decrypted = cipher.decrypt(ciphertext)
    print(f"Decrypted: {decrypted.decode()}")

    assert plaintext == decrypted
    print("✓ RSA encryption successful!")


def demo_hybrid_encryption():
    """Demo hybrid encryption (RSA + AES) for large data."""
    print("\n" + "="*60)
    print("Hybrid Encryption Demo (RSA + AES)")
    print("="*60)

    # Generate RSA key pair
    keypair = KeyPairGenerator.generate_rsa(RSAKeySize.RSA_2048)
    rsa_cipher = RSACipher(keypair.public_key, keypair.private_key)
    hybrid = HybridCipher(rsa_cipher)

    # Encrypt large data (RSA alone can't handle this)
    plaintext = b"Very large message " * 1000
    print(f"Plaintext size: {len(plaintext)} bytes")

    encrypted_key, iv, ciphertext, tag = hybrid.encrypt(plaintext)
    print(f"Encrypted AES key: {len(encrypted_key)} bytes (RSA-encrypted)")
    print(f"Encrypted data: {len(ciphertext)} bytes (AES-encrypted)")

    # Decrypt
    decrypted = hybrid.decrypt(encrypted_key, iv, ciphertext, tag)
    print(f"Decrypted size: {len(decrypted)} bytes")

    assert plaintext == decrypted
    print("✓ Hybrid encryption successful!")


def demo_ecc_key_exchange():
    """Demo Elliptic Curve Diffie-Hellman key exchange."""
    print("\n" + "="*60)
    print("ECDH Key Exchange Demo")
    print("="*60)

    # Alice and Bob generate key pairs
    print("Alice generates key pair...")
    alice_keypair = KeyPairGenerator.generate_ecc(ECCCurve.SECP256R1)

    print("Bob generates key pair...")
    bob_keypair = KeyPairGenerator.generate_ecc(ECCCurve.SECP256R1)

    # Alice computes shared secret
    alice_cipher = ECCCipher(alice_keypair.private_key)
    alice_shared = alice_cipher.ecdh_exchange(bob_keypair.public_key)
    print(f"Alice's shared secret: {alice_shared.hex()[:32]}...")

    # Bob computes shared secret
    bob_cipher = ECCCipher(bob_keypair.private_key)
    bob_shared = bob_cipher.ecdh_exchange(alice_keypair.public_key)
    print(f"Bob's shared secret:   {bob_shared.hex()[:32]}...")

    assert alice_shared == bob_shared
    print("✓ Shared secrets match! Secure channel established.")

    # Use shared secret as encryption key
    cipher = AESCipher(alice_shared, EncryptionMode.AES_GCM)
    message = b"Message encrypted with shared secret"
    result = cipher.encrypt(message)
    decrypted = cipher.decrypt(result)

    assert message == decrypted
    print("✓ Communication over secure channel successful!")


def demo_secure_messaging():
    """Demo complete secure messaging workflow."""
    print("\n" + "="*60)
    print("Secure Messaging Demo")
    print("="*60)

    # Alice wants to send a secure message to Bob
    print("\n1. Alice and Bob exchange public keys")

    alice_keypair = KeyPairGenerator.generate_rsa(RSAKeySize.RSA_2048)
    bob_keypair = KeyPairGenerator.generate_rsa(RSAKeySize.RSA_2048)

    print("   ✓ Key exchange complete")

    # Alice encrypts message for Bob
    print("\n2. Alice encrypts message using Bob's public key")

    message = b"Meet me at the secret location at midnight."
    print(f"   Original message: {message.decode()}")

    bob_public_cipher = RSACipher(bob_keypair.public_key)
    hybrid = HybridCipher(bob_public_cipher)

    encrypted_key, iv, ciphertext, tag = hybrid.encrypt(message)
    print(f"   ✓ Message encrypted ({len(ciphertext)} bytes)")

    # Alice signs the message
    print("\n3. Alice signs the message with her private key")

    alice_cipher = RSACipher(None, alice_keypair.private_key)
    signature = alice_cipher.sign(message)
    print(f"   ✓ Signature generated ({len(signature)} bytes)")

    # Bob receives and decrypts
    print("\n4. Bob decrypts message using his private key")

    bob_cipher = RSACipher(bob_keypair.public_key, bob_keypair.private_key)
    hybrid_bob = HybridCipher(bob_cipher)
    decrypted = hybrid_bob.decrypt(encrypted_key, iv, ciphertext, tag)
    print(f"   Decrypted message: {decrypted.decode()}")

    assert message == decrypted

    # Bob verifies signature
    print("\n5. Bob verifies signature using Alice's public key")

    alice_public_cipher = RSACipher(alice_keypair.public_key)
    is_valid = alice_public_cipher.verify(decrypted, signature)

    if is_valid:
        print("   ✓ Signature valid! Message is authentic.")
    else:
        print("   ✗ Signature invalid! Message may be forged.")

    print("\n✓ Secure messaging complete!")


def main():
    """Run all encryption demos."""
    print("\n" + "="*60)
    print("CovetPy Cryptography - Complete Encryption Demo")
    print("="*60)

    try:
        # Symmetric encryption
        demo_aes_gcm()
        demo_aes_gcm_with_aad()
        demo_chacha20()
        demo_password_based_encryption()

        # Asymmetric encryption
        demo_rsa_encryption()
        demo_hybrid_encryption()
        demo_ecc_key_exchange()

        # Real-world scenario
        demo_secure_messaging()

        print("\n" + "="*60)
        print("All demos completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
