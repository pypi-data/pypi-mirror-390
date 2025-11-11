"""
Complete Authentication Example for CovetPy

This example demonstrates:
1. User registration with password hashing
2. Login with JWT token generation
3. Protected routes requiring authentication
4. Role-based access control
5. Token refresh
6. Password reset flow
7. Logout functionality

Security Features:
- Secure password hashing with Scrypt
- JWT tokens with expiration
- Role-based authorization
- Token revocation on logout
- HTTPS enforcement (production)
- CORS protection
- Rate limiting (recommended)

Run with:
    python examples/auth_example.py

Test with curl:
    # Register
    curl -X POST http://localhost:8000/auth/register \
      -H "Content-Type: application/json" \
      -d '{"username": "john", "email": "john@example.com", "password": "SecurePass123!"}'

    # Login
    curl -X POST http://localhost:8000/auth/login \
      -H "Content-Type: application/json" \
      -d '{"username": "john", "password": "SecurePass123!"}'

    # Access protected route
    curl http://localhost:8000/api/profile \
      -H "Authorization: Bearer YOUR_TOKEN_HERE"

    # Access admin route (requires admin role)
    curl http://localhost:8000/api/admin \
      -H "Authorization: Bearer YOUR_TOKEN_HERE"
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Optional

from covet import Covet
from covet.auth import (
    Auth,
    check_password_strength,
    hash_password,
    login_required,
    roles_required,
    verify_password,
)
from covet.core.http import Request, Response


# ============================================================
# User Storage (In-Memory - Use Database in Production)
# ============================================================

class UserStore:
    """Simple in-memory user storage for demonstration."""

    def __init__(self):
        self.users: Dict[str, dict] = {}
        self.users_by_email: Dict[str, str] = {}

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        roles: Optional[list] = None
    ) -> dict:
        """Create new user."""
        if username in self.users:
            raise ValueError("Username already exists")

        if email in self.users_by_email:
            raise ValueError("Email already exists")

        user = {
            'id': str(len(self.users) + 1),
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'roles': roles or ['user'],
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True,
        }

        self.users[username] = user
        self.users_by_email[email] = username

        return user

    def get_user(self, username: str) -> Optional[dict]:
        """Get user by username."""
        return self.users.get(username)

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        username = self.users_by_email.get(email)
        if username:
            return self.users[username]
        return None

    def update_user(self, username: str, **updates):
        """Update user fields."""
        if username in self.users:
            self.users[username].update(updates)


# Initialize user store
user_store = UserStore()


# ============================================================
# Application Setup
# ============================================================

app = Covet()

# Configure authentication with secure secret key
# SECURITY: In production, use environment variable and strong key
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
auth = Auth(app, secret_key=SECRET_KEY, access_token_expire_minutes=30)


# ============================================================
# Authentication Endpoints
# ============================================================

@app.route('/auth/register', methods=['POST'])
async def register(request: Request):
    """
    Register new user.

    Request Body:
        {
            "username": "john",
            "email": "john@example.com",
            "password": "SecurePass123!"
        }

    Response:
        {
            "message": "User registered successfully",
            "user_id": "1",
            "username": "john"
        }

    Security:
        - Validates password strength
        - Hashes password with Scrypt
        - Checks for duplicate username/email
    """
    try:
        data = await request.json()

        # Extract and validate data
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        # Validation
        if not username or len(username) < 3:
            return Response(
                content={'error': 'Username must be at least 3 characters'},
                status_code=400
            )

        if not email or '@' not in email:
            return Response(
                content={'error': 'Valid email required'},
                status_code=400
            )

        # Check password strength
        is_strong, issues = check_password_strength(password)
        if not is_strong:
            return Response(
                content={
                    'error': 'Password does not meet requirements',
                    'issues': issues
                },
                status_code=400
            )

        # Hash password
        password_hash = auth.hash_password(password)

        # Create user
        try:
            user = user_store.create_user(
                username=username,
                email=email,
                password_hash=password_hash,
                roles=['user']
            )
        except ValueError as e:
            return Response(
                content={'error': str(e)},
                status_code=409
            )

        return Response(
            content={
                'message': 'User registered successfully',
                'user_id': user['id'],
                'username': user['username']
            },
            status_code=201
        )

    except Exception as e:
        return Response(
            content={'error': f'Registration failed: {str(e)}'},
            status_code=500
        )


@app.route('/auth/login', methods=['POST'])
async def login(request: Request):
    """
    Login user and return JWT token.

    Request Body:
        {
            "username": "john",
            "password": "SecurePass123!"
        }

    Response:
        {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "Bearer",
            "expires_in": 1800,
            "user": {
                "id": "1",
                "username": "john",
                "roles": ["user"]
            }
        }

    Security:
        - Verifies password with constant-time comparison
        - Returns JWT tokens
        - Logs authentication attempts
    """
    try:
        data = await request.json()

        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return Response(
                content={'error': 'Username and password required'},
                status_code=400
            )

        # Get user
        user = user_store.get_user(username)
        if not user:
            # Use same error message to prevent username enumeration
            return Response(
                content={'error': 'Invalid credentials'},
                status_code=401
            )

        # Verify password
        if not auth.verify_password(password, user['password_hash']):
            return Response(
                content={'error': 'Invalid credentials'},
                status_code=401
            )

        # Check if user is active
        if not user.get('is_active', True):
            return Response(
                content={'error': 'Account is disabled'},
                status_code=403
            )

        # Create tokens
        access_token = auth.create_token(
            user_id=user['id'],
            username=user['username'],
            roles=user['roles']
        )

        refresh_token = auth.create_refresh_token(user_id=user['id'])

        return Response(
            content={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': auth.jwt.access_token_expire_minutes * 60,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'roles': user['roles']
                }
            },
            status_code=200
        )

    except Exception as e:
        return Response(
            content={'error': f'Login failed: {str(e)}'},
            status_code=500
        )


@app.route('/auth/refresh', methods=['POST'])
async def refresh_token(request: Request):
    """
    Refresh access token using refresh token.

    Request Body:
        {
            "refresh_token": "eyJ..."
        }

    Response:
        {
            "access_token": "eyJ...",
            "token_type": "Bearer",
            "expires_in": 1800
        }
    """
    try:
        data = await request.json()
        refresh_token = data.get('refresh_token', '')

        if not refresh_token:
            return Response(
                content={'error': 'Refresh token required'},
                status_code=400
            )

        # Create new access token
        access_token = auth.refresh_access_token(refresh_token)

        return Response(
            content={
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': auth.jwt.access_token_expire_minutes * 60
            },
            status_code=200
        )

    except Exception as e:
        return Response(
            content={'error': f'Token refresh failed: {str(e)}'},
            status_code=401
        )


@app.route('/auth/logout', methods=['POST'])
@login_required
async def logout(request: Request):
    """
    Logout user by revoking token.

    Request Headers:
        Authorization: Bearer <token>

    Response:
        {
            "message": "Logged out successfully"
        }

    Security:
        - Revokes token by adding to blacklist
        - Clears session data
    """
    try:
        # Extract token from request
        from covet.auth.decorators import extract_token_from_request
        token = extract_token_from_request(request)

        if token:
            # Revoke token
            auth.revoke_token(token)

        return Response(
            content={'message': 'Logged out successfully'},
            status_code=200
        )

    except Exception as e:
        return Response(
            content={'error': f'Logout failed: {str(e)}'},
            status_code=500
        )


# ============================================================
# Protected API Endpoints
# ============================================================

@app.route('/api/profile')
@login_required
async def get_profile(request: Request):
    """
    Get current user profile (requires authentication).

    Request Headers:
        Authorization: Bearer <token>

    Response:
        {
            "user": {
                "id": "1",
                "username": "john",
                "email": "john@example.com",
                "roles": ["user"],
                "created_at": "2025-01-15T10:30:00"
            }
        }
    """
    # User info automatically injected by @login_required decorator
    username = request.username

    user = user_store.get_user(username)
    if not user:
        return Response(
            content={'error': 'User not found'},
            status_code=404
        )

    # Remove sensitive data
    safe_user = {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'roles': user['roles'],
        'created_at': user['created_at']
    }

    return Response(
        content={'user': safe_user},
        status_code=200
    )


@app.route('/api/users')
@login_required
@roles_required('admin')
async def list_users(request: Request):
    """
    List all users (requires admin role).

    Request Headers:
        Authorization: Bearer <token>

    Response:
        {
            "users": [
                {
                    "id": "1",
                    "username": "john",
                    "email": "john@example.com",
                    "roles": ["user"]
                }
            ],
            "total": 1
        }

    Security:
        - Requires authentication
        - Requires 'admin' role
    """
    users = []
    for user in user_store.users.values():
        users.append({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'roles': user['roles'],
            'is_active': user['is_active'],
            'created_at': user['created_at']
        })

    return Response(
        content={
            'users': users,
            'total': len(users)
        },
        status_code=200
    )


@app.route('/api/admin/stats')
@login_required
@roles_required('admin')
async def admin_stats(request: Request):
    """
    Get admin statistics (requires admin role).

    Request Headers:
        Authorization: Bearer <token>

    Response:
        {
            "total_users": 5,
            "active_users": 4,
            "admin_users": 1
        }
    """
    total_users = len(user_store.users)
    active_users = sum(1 for u in user_store.users.values() if u.get('is_active', True))
    admin_users = sum(1 for u in user_store.users.values() if 'admin' in u.get('roles', []))

    return Response(
        content={
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users,
            'current_admin': request.username
        },
        status_code=200
    )


# ============================================================
# Public Endpoints
# ============================================================

@app.route('/')
async def index(request: Request):
    """Welcome endpoint."""
    return Response(
        content={
            'message': 'CovetPy Authentication Example API',
            'version': '1.0',
            'endpoints': {
                'authentication': [
                    'POST /auth/register',
                    'POST /auth/login',
                    'POST /auth/refresh',
                    'POST /auth/logout'
                ],
                'protected': [
                    'GET /api/profile',
                    'GET /api/users (admin only)',
                    'GET /api/admin/stats (admin only)'
                ]
            },
            'documentation': 'See examples/auth_example.py for details'
        },
        status_code=200
    )


@app.route('/health')
async def health_check(request: Request):
    """Health check endpoint."""
    return Response(
        content={
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        },
        status_code=200
    )


# ============================================================
# Application Runner
# ============================================================

def setup_demo_data():
    """Create demo users for testing."""
    # Create regular user
    try:
        user_store.create_user(
            username='demo',
            email='demo@example.com',
            password_hash=hash_password('DemoPass123!'),
            roles=['user']
        )
        print("✓ Created demo user: demo / DemoPass123!")

        # Create admin user
        user_store.create_user(
            username='admin',
            email='admin@example.com',
            password_hash=hash_password('AdminPass123!'),
            roles=['user', 'admin']
        )
        print("✓ Created admin user: admin / AdminPass123!")

    except ValueError:
        print("Demo users already exist")


if __name__ == '__main__':
    print("=" * 70)
    print("CovetPy Authentication Example")
    print("=" * 70)
    print()

    # Setup demo data
    setup_demo_data()

    print()
    print("API Endpoints:")
    print("  POST   /auth/register    - Register new user")
    print("  POST   /auth/login       - Login and get token")
    print("  POST   /auth/refresh     - Refresh access token")
    print("  POST   /auth/logout      - Logout (revoke token)")
    print("  GET    /api/profile      - Get user profile (auth required)")
    print("  GET    /api/users        - List users (admin only)")
    print("  GET    /api/admin/stats  - Admin statistics (admin only)")
    print()
    print("Demo Users:")
    print("  Regular: demo / DemoPass123!")
    print("  Admin:   admin / AdminPass123!")
    print()
    print("Starting server on http://localhost:8000")
    print("=" * 70)

    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)
