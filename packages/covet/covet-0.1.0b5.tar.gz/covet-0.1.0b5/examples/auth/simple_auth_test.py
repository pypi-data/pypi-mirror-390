"""
Simple Authentication Test Script

Quick test to verify the new authentication system works correctly.

Run with:
    python examples/auth/simple_auth_test.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from covet.auth import (
    Auth,
    hash_password,
    verify_password,
    check_password_strength,
    generate_secure_password,
    login_required,
)

print("=" * 70)
print("CovetPy Authentication System Test")
print("=" * 70)
print()

# Test 1: Password Hashing
print("Test 1: Password Hashing")
print("-" * 70)
password = "SecurePass123!"
hashed = hash_password(password)
print(f"✓ Password hashed: {hashed[:50]}...")
print(f"✓ Verification: {verify_password(password, hashed)}")
print(f"✗ Wrong password: {verify_password('WrongPass', hashed)}")
print()

# Test 2: Password Strength Validation
print("Test 2: Password Strength Validation")
print("-" * 70)
test_passwords = [
    "weak",
    "WeakPassword",
    "SecurePass123!",
    "password123",
]

for pwd in test_passwords:
    is_strong, issues = check_password_strength(pwd)
    status = "✓" if is_strong else "✗"
    print(f"{status} '{pwd}': {is_strong}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
print()

# Test 3: Generate Secure Password
print("Test 3: Generate Secure Password")
print("-" * 70)
secure_pwd = generate_secure_password(16)
print(f"✓ Generated: {secure_pwd}")
is_strong, _ = check_password_strength(secure_pwd)
print(f"✓ Is strong: {is_strong}")
print()

# Test 4: JWT Token Creation and Verification
print("Test 4: JWT Token Creation and Verification")
print("-" * 70)
auth = Auth(secret_key='test-secret-key-12345')

# Create token
token = auth.create_token(
    user_id='123',
    username='john_doe',
    roles=['user', 'admin']
)
print(f"✓ Token created: {token[:50]}...")

# Verify token
try:
    payload = auth.verify_token(token)
    print(f"✓ Token verified")
    print(f"  - User ID: {payload['sub']}")
    print(f"  - Username: {payload.get('username')}")
    print(f"  - Roles: {payload.get('roles')}")
except Exception as e:
    print(f"✗ Token verification failed: {e}")
print()

# Test 5: Token Expiration
print("Test 5: Refresh Token")
print("-" * 70)
refresh_token = auth.create_refresh_token(user_id='123')
print(f"✓ Refresh token created: {refresh_token[:50]}...")

try:
    new_access_token = auth.refresh_access_token(refresh_token)
    print(f"✓ New access token created: {new_access_token[:50]}...")
except Exception as e:
    print(f"✗ Token refresh failed: {e}")
print()

# Test 6: Token Revocation
print("Test 6: Token Revocation")
print("-" * 70)
token_to_revoke = auth.create_token(user_id='456', username='jane')
print(f"✓ Token created: {token_to_revoke[:50]}...")

# Verify before revocation
try:
    auth.verify_token(token_to_revoke)
    print("✓ Token valid before revocation")
except Exception:
    print("✗ Token invalid before revocation")

# Revoke token
auth.revoke_token(token_to_revoke)
print("✓ Token revoked")

# Try to verify after revocation
try:
    auth.verify_token(token_to_revoke)
    print("✗ Token still valid after revocation (SECURITY ISSUE!)")
except Exception as e:
    print(f"✓ Token invalid after revocation: {type(e).__name__}")
print()

# Test 7: Decorator Integration Test
print("Test 7: Decorator Integration")
print("-" * 70)

from covet.auth.decorators import configure_auth_decorators
from covet.core.http import Request

# Configure decorators
configure_auth_decorators(auth.jwt)

# Create mock request with token
class MockRequest(Request):
    def __init__(self):
        super().__init__(
            method='GET',
            url='/test',
            headers={'authorization': f'Bearer {token}'},
            body=None
        )

# Test protected function
@login_required
def protected_function(request):
    return f"Hello {request.username}!"

try:
    mock_request = MockRequest()
    result = protected_function(mock_request)
    print(f"✓ Protected function called successfully")
    print(f"  - Result: {result}")
    print(f"  - User ID: {mock_request.user_id}")
    print(f"  - Username: {mock_request.username}")
except Exception as e:
    print(f"✗ Protected function failed: {e}")
print()

# Summary
print("=" * 70)
print("All Tests Completed!")
print("=" * 70)
print()
print("Next Steps:")
print("1. Run the full example: python examples/auth_example.py")
print("2. Test with curl or Postman")
print("3. Integrate into your Covet application")
print()
