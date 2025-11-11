"""
CovetPy Simple Authentication
Basic JWT authentication for Sprint 2
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union


class SimpleJWT:
    """Simple JWT implementation without external dependencies."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode("utf-8")

    def encode(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """
        Encode a JWT token.

        Args:
            payload: Token payload
            expires_in: Expiration time in seconds

        Returns:
            JWT token string
        """
        # Add standard claims
        now = int(time.time())
        payload.update(
            {
                "iat": now,  # issued at
                "exp": now + expires_in,  # expires at
            }
        )

        # Create header
        header = {"typ": "JWT", "alg": "HS256"}

        # Encode header and payload
        header_b64 = self._base64url_encode(json.dumps(header).encode())
        payload_b64 = self._base64url_encode(json.dumps(payload).encode())

        # Create signature
        message = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(self.secret_key, message, hashlib.sha256).digest()
        signature_b64 = self._base64url_encode(signature)

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def decode(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload or None if invalid
        """
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            # Verify signature
            message = f"{header_b64}.{payload_b64}".encode()
            expected_signature = hmac.new(self.secret_key, message, hashlib.sha256).digest()
            expected_signature_b64 = self._base64url_encode(expected_signature)

            if not hmac.compare_digest(signature_b64.encode(), expected_signature_b64.encode()):
                return None

            # Decode payload
            payload_data = self._base64url_decode(payload_b64)
            payload = json.loads(payload_data.decode())

            # Check expiration
            if "exp" in payload and payload["exp"] < int(time.time()):
                return None

            return payload

        except Exception:
            return None

    def _base64url_encode(self, data: bytes) -> str:
        """Base64URL encode."""
        return base64.urlsafe_b64encode(data).decode().rstrip("=")

    def _base64url_decode(self, data: str) -> bytes:
        """Base64URL decode."""
        # Add padding if needed
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)


class PasswordHasher:
    """Simple password hashing using PBKDF2."""

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> str:
        """
        Hash a password.

        Args:
            password: Plain text password
            salt: Optional salt (generated if not provided)

        Returns:
            Hashed password string
        """
        if salt is None:
            salt = hashlib.sha256(str(time.time()).encode()).digest()[:16]

        # Use PBKDF2 with SHA256
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

        # Combine salt and key
        combined = salt + key
        return base64.b64encode(combined).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        try:
            combined = base64.b64decode(hashed.encode())
            salt = combined[:16]
            stored_key = combined[16:]

            # Hash the provided password with the stored salt
            key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

            return hmac.compare_digest(stored_key, key)
        except Exception:
            return False


class User:
    """Simple user model for authentication."""

    def __init__(self, user_id: str, username: str, email: str = "", roles: list = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.roles = roles or []
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "roles": self.roles,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create user from dictionary."""
        user = cls(
            user_id=data["user_id"],
            username=data["username"],
            email=data.get("email", ""),
            roles=data.get("roles", []),
        )
        if "created_at" in data:
            user.created_at = datetime.fromisoformat(data["created_at"])
        return user


class SimpleAuth:
    """Simple authentication system."""

    def __init__(self, secret_key: str):
        self.jwt = SimpleJWT(secret_key)
        self.password_hasher = PasswordHasher()
        self.users: Dict[str, Dict[str, Any]] = {}  # In-memory user store

    def register_user(
        self, username: str, password: str, email: str = "", roles: list = None
    ) -> User:
        """
        Register a new user.

        Args:
            username: Username
            password: Plain text password
            email: Email address
            roles: User roles

        Returns:
            Created user
        """
        if username in self.users:
            raise ValueError(f"User {username} already exists")

        user_id = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()[:12]
        hashed_password = self.password_hasher.hash_password(password)

        user = User(user_id, username, email, roles or [])

        self.users[username] = {
            "user": user.to_dict(),
            "password_hash": hashed_password,
        }

        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user.

        Args:
            username: Username
            password: Plain text password

        Returns:
            User object if authenticated, None otherwise
        """
        if username not in self.users:
            return None

        user_data = self.users[username]
        if not self.password_hasher.verify_password(password, user_data["password_hash"]):
            return None

        return User.from_dict(user_data["user"])

    def create_token(self, user: User, expires_in: int = 3600) -> str:
        """
        Create a JWT token for a user.

        Args:
            user: User object
            expires_in: Token expiration in seconds

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "roles": user.roles,
        }

        return self.jwt.encode(payload, expires_in)

    def verify_token(self, token: str) -> Optional[User]:
        """
        Verify a JWT token and return the user.

        Args:
            token: JWT token string

        Returns:
            User object if token is valid, None otherwise
        """
        payload = self.jwt.decode(token)
        if not payload:
            return None

        # Find user by username (could be optimized with user_id index)
        for username, user_data in self.users.items():
            if user_data["user"]["user_id"] == payload["user_id"]:
                return User.from_dict(user_data["user"])

        return None

    def require_role(self, user: User, required_role: str) -> bool:
        """
        Check if user has required role.

        Args:
            user: User object
            required_role: Required role name

        Returns:
            True if user has the role
        """
        return required_role in user.roles

    def get_user(self, username: str) -> Optional[User]:
        """Get user by username."""
        if username in self.users:
            return User.from_dict(self.users[username]["user"])
        return None


# Middleware function for authentication
def auth_middleware(auth: SimpleAuth):
    """
    Create authentication middleware.

    Args:
        auth: SimpleAuth instance

    Returns:
        Middleware function
    """

    def middleware(request):
        """Authentication middleware function."""
        # Extract token from Authorization header
        auth_header = request.headers.get("authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            user = auth.verify_token(token)
            request.user = user
        else:
            request.user = None

        return request

    return middleware


def require_auth(auth: SimpleAuth):
    """
    Decorator to require authentication.

    Args:
        auth: SimpleAuth instance

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, "user") or request.user is None:
                return {"error": "Authentication required", "status_code": 401}
            return func(request, *args, **kwargs)

        return wrapper

    return decorator


def require_role(auth: SimpleAuth, role: str):
    """
    Decorator to require specific role.

    Args:
        auth: SimpleAuth instance
        role: Required role name

    Returns:
        Decorator function
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, "user") or request.user is None:
                return {"error": "Authentication required", "status_code": 401}

            if not auth.require_role(request.user, role):
                return {"error": f"Role {role} required", "status_code": 403}

            return func(request, *args, **kwargs)

        return wrapper

    return decorator
