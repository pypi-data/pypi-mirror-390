"""
Test JWT Authentication
"""
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

try:
    from covet.security.jwt_auth import JWTAuthenticator, JWTConfig
    print("✅ JWT imports successful")
except ImportError as e:
    print(f"❌ JWT import failed: {e}")
    sys.exit(1)

# Test JWT operations
try:
    from covet.security.jwt_auth import JWTAlgorithm, TokenType

    config = JWTConfig(
        secret_key="test_secret_key_minimum_32_chars_long",
        algorithm=JWTAlgorithm.HS256
    )
    print("✅ JWT config created")

    auth = JWTAuthenticator(config)
    print("✅ JWT authenticator created")

    # Create token with enum
    token = auth.create_token(
        subject="user123",
        token_type=TokenType.ACCESS
    )
    print(f"✅ Token created: {token[:50]}...")

    # Verify token
    claims = auth.verify_token(token)
    print(f"✅ Token verified, subject: {claims.get('sub')}")

    # Test token pair
    token_pair = auth.create_token_pair(subject="user456")
    print(f"✅ Token pair created (access + refresh)")

except Exception as e:
    print(f"❌ JWT operations failed: {e}")
    import traceback
    traceback.print_exc()
