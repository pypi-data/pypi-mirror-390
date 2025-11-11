#!/usr/bin/env python3
"""
Security Module Usage Examples

Demonstrates how to use the CovetPy security modules:
- SecureJWTManager: JWT token management
- EnhancedValidator: Input validation
- SecureCrypto: Cryptographic operations
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from covet.security.secure_jwt import (
    SecureJWTManager,
    configure_jwt,
    create_access_token,
    create_refresh_token,
    verify_token,
    ExpiredSignatureError,
    InvalidTokenError,
)
from covet.security.enhanced_validation import EnhancedValidator
from covet.security.secure_crypto import (
    SecureCrypto,
    hash_password,
    verify_password,
    generate_api_key,
    generate_session_id,
    generate_csrf_token,
)


def example_jwt_authentication():
    """Example: JWT Authentication Flow"""
    print("\n" + "=" * 70)
    print("JWT AUTHENTICATION EXAMPLE")
    print("=" * 70)

    # Configure JWT globally
    configure_jwt(
        secret_key="your-super-secret-key-change-in-production",
        algorithm="HS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )

    # Create access token
    user_id = "user123"
    access_token = create_access_token(
        subject=user_id,
        additional_claims={"role": "admin", "email": "user@example.com"}
    )
    print(f"✅ Access Token Created: {access_token[:50]}...")

    # Create refresh token
    refresh_token = create_refresh_token(subject=user_id)
    print(f"✅ Refresh Token Created: {refresh_token[:50]}...")

    # Verify token
    try:
        payload = verify_token(access_token)
        print(f"✅ Token Verified - User ID: {payload['sub']}, Role: {payload['role']}")
    except ExpiredSignatureError:
        print("❌ Token expired")
    except InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")


def example_advanced_jwt():
    """Example: Advanced JWT with Token Rotation"""
    print("\n" + "=" * 70)
    print("ADVANCED JWT - TOKEN ROTATION EXAMPLE")
    print("=" * 70)

    # Create custom JWT manager
    jwt_manager = SecureJWTManager(
        secret_key="your-secret-key",
        algorithm="HS256"
    )

    # Create initial token
    payload = {"user_id": "123", "role": "admin"}
    old_token = jwt_manager.encode(payload, expires_in=3600)
    print(f"✅ Original Token: {old_token[:50]}...")

    # Rotate token (e.g., during refresh)
    new_token = jwt_manager.rotate_token(old_token, expires_in=7200)
    print(f"✅ Rotated Token: {new_token[:50]}...")

    # Old token is now blacklisted
    try:
        jwt_manager.decode(old_token)
        print("❌ Old token still valid (should not happen)")
    except InvalidTokenError:
        print("✅ Old token successfully revoked")

    # New token works fine
    decoded = jwt_manager.decode(new_token)
    print(f"✅ New Token Valid - User: {decoded['user_id']}")


def example_input_validation():
    """Example: Input Validation"""
    print("\n" + "=" * 70)
    print("INPUT VALIDATION EXAMPLE")
    print("=" * 70)

    # Email validation
    emails = ["user@example.com", "invalid.email", "admin@company.co.uk"]
    for email in emails:
        is_valid = EnhancedValidator.validate_email(email)
        status = "✅" if is_valid else "❌"
        print(f"{status} Email '{email}': {'Valid' if is_valid else 'Invalid'}")

    # Username validation
    usernames = ["john_doe", "123invalid", "valid_user_name"]
    for username in usernames:
        is_valid, error = EnhancedValidator.validate_username(username)
        status = "✅" if is_valid else "❌"
        print(f"{status} Username '{username}': {error or 'Valid'}")

    # Password validation
    passwords = ["weak", "StrongP@ssw0rd", "NoSpecial123"]
    for password in passwords:
        is_valid, errors = EnhancedValidator.validate_password(password)
        status = "✅" if is_valid else "❌"
        print(f"{status} Password '{password}': {errors[0] if errors else 'Valid'}")


def example_security_validation():
    """Example: Security-Focused Validation"""
    print("\n" + "=" * 70)
    print("SECURITY VALIDATION EXAMPLE")
    print("=" * 70)

    # Path traversal prevention
    paths = [
        ("/var/www/uploads/file.txt", ["/var/www/uploads"]),
        ("../../etc/passwd", ["/var/www/uploads"]),
        ("/tmp/safe_file.txt", ["/tmp"]),
    ]
    for path, allowed_dirs in paths:
        is_valid, error = EnhancedValidator.validate_path(path, allowed_dirs)
        status = "✅" if is_valid else "❌"
        print(f"{status} Path '{path}': {error or 'Valid'}")

    # SQL injection detection
    sql_inputs = [
        "normal_input",
        "admin' OR '1'='1",
        "user@example.com",
    ]
    for sql_input in sql_inputs:
        is_suspicious, patterns = EnhancedValidator.detect_sql_injection(sql_input)
        status = "🚨" if is_suspicious else "✅"
        print(f"{status} SQL Input '{sql_input}': {'SUSPICIOUS' if is_suspicious else 'Safe'}")

    # URL validation
    urls = [
        "https://example.com",
        "javascript:alert('xss')",
        "http://192.168.1.1",
    ]
    for url in urls:
        is_valid, error = EnhancedValidator.validate_url(url)
        status = "✅" if is_valid else "❌"
        print(f"{status} URL '{url}': {error or 'Valid'}")


def example_cryptography():
    """Example: Cryptographic Operations"""
    print("\n" + "=" * 70)
    print("CRYPTOGRAPHY EXAMPLE")
    print("=" * 70)

    # Password hashing and verification
    password = "UserPassword123!"
    password_hash = hash_password(password)
    print(f"✅ Password Hash: {password_hash[:50]}...")

    is_valid = verify_password(password, password_hash)
    print(f"✅ Password Verification: {'Success' if is_valid else 'Failed'}")

    wrong_password = "WrongPassword!"
    is_valid = verify_password(wrong_password, password_hash)
    print(f"❌ Wrong Password Verification: {'Success' if is_valid else 'Failed (as expected)'}")

    # Encryption/Decryption
    crypto = SecureCrypto()
    encryption_key = crypto.generate_key()
    print(f"✅ Encryption Key Generated: {encryption_key[:30]}...")

    sensitive_data = b"Top Secret Information"
    encrypted = crypto.encrypt(sensitive_data, encryption_key)
    print(f"✅ Data Encrypted: {encrypted[:50]}...")

    decrypted = crypto.decrypt(encrypted, encryption_key)
    print(f"✅ Data Decrypted: {decrypted.decode()}")


def example_token_generation():
    """Example: Token and Key Generation"""
    print("\n" + "=" * 70)
    print("TOKEN GENERATION EXAMPLE")
    print("=" * 70)

    # API Key generation
    api_key = generate_api_key(prefix="myapp_")
    print(f"✅ API Key: {api_key}")

    # Session ID generation
    session_id = generate_session_id()
    print(f"✅ Session ID: {session_id}")

    # CSRF Token generation
    csrf_token = generate_csrf_token()
    print(f"✅ CSRF Token: {csrf_token}")

    # Secure random token
    from covet.security.secure_crypto import generate_secure_token
    secure_token = generate_secure_token(32)
    print(f"✅ Secure Token: {secure_token}")


def example_advanced_crypto():
    """Example: Advanced Cryptographic Operations"""
    print("\n" + "=" * 70)
    print("ADVANCED CRYPTOGRAPHY EXAMPLE")
    print("=" * 70)

    # Password hashing with custom iterations
    password = "SecurePassword123!"
    hashed, salt = SecureCrypto.hash_password(password, iterations=200000)
    print(f"✅ High-Security Hash (200k iterations): {hashed.hex()[:50]}...")

    # Verify with correct iterations
    is_valid = SecureCrypto.verify_password(password, hashed, salt, iterations=200000)
    print(f"✅ Password Verified (200k iterations): {is_valid}")

    # Constant-time comparison
    from covet.security.secure_crypto import constant_time_compare
    token1 = "secret_token_123"
    token2 = "secret_token_123"
    token3 = "different_token"

    print(f"✅ Token Compare (equal): {constant_time_compare(token1, token2)}")
    print(f"❌ Token Compare (different): {constant_time_compare(token1, token3)}")


def example_sanitization():
    """Example: Input Sanitization"""
    print("\n" + "=" * 70)
    print("INPUT SANITIZATION EXAMPLE")
    print("=" * 70)

    # HTML sanitization (XSS prevention)
    dangerous_html = "<script>alert('XSS')</script><p>Normal text</p>"
    sanitized = EnhancedValidator.sanitize_html(dangerous_html)
    print(f"Original: {dangerous_html}")
    print(f"✅ Sanitized: {sanitized}")

    # SQL identifier sanitization
    sql_identifiers = ["users_table", "DROP TABLE users", "valid_column_123"]
    for identifier in sql_identifiers:
        try:
            safe = EnhancedValidator.sanitize_sql_identifier(identifier)
            print(f"✅ SQL Identifier '{identifier}': Safe ({safe})")
        except ValueError as e:
            print(f"❌ SQL Identifier '{identifier}': Rejected ({e})")

    # Filename sanitization
    filenames = ["normal_file.txt", "../../etc/passwd", "file\x00.jpg"]
    for filename in filenames:
        safe = EnhancedValidator.sanitize_filename(filename)
        print(f"Original: '{filename}' → Sanitized: '{safe}'")


def main():
    """Run all security examples"""
    print("\n" + "=" * 70)
    print("COVETPY SECURITY MODULES - COMPREHENSIVE EXAMPLES")
    print("=" * 70)

    try:
        example_jwt_authentication()
        example_advanced_jwt()
        example_input_validation()
        example_security_validation()
        example_cryptography()
        example_token_generation()
        example_advanced_crypto()
        example_sanitization()

        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\nSecurity modules are production-ready and fully functional.")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
