import jwt


def generate_jwt_token(payload: dict, secret: str) -> str:
    """Generate a JWT token."""
    return jwt.encode(payload, secret, algorithm="HS256")


def authenticate_user(token: str, secret: str) -> dict:
    """Authenticate a user with a JWT token."""
    return jwt.decode(token, secret, algorithms=["HS256"])


class AuthService:
    """Authentication service for API endpoints.

    SECURITY WARNING: The default secret_key is for testing only.
    In production, ALWAYS provide a strong secret key from environment variables:

    Example:
        import os
        secret_key = os.environ.get('JWT_SECRET_KEY')
        if not secret_key:
            raise ValueError('JWT_SECRET_KEY environment variable not set')
        auth_service = AuthService(secret_key=secret_key)
    """

    def __init__(self, secret_key: str = None):
        if secret_key is None:
            import os

            secret_key = os.environ.get("JWT_SECRET_KEY", "INSECURE_DEFAULT_FOR_TESTING_ONLY")
            if secret_key == "INSECURE_DEFAULT_FOR_TESTING_ONLY":
                import warnings

                warnings.warn(
                    "Using default test secret key! Set JWT_SECRET_KEY environment variable in production.",
                    SecurityWarning,
                    stacklevel=2,
                )
        self.secret_key = secret_key

    def generate_token(self, user_id: str, **claims) -> str:
        """Generate JWT token for user."""
        payload = {"user_id": user_id, **claims}
        return generate_jwt_token(payload, self.secret_key)

    def verify_token(self, token: str) -> dict:
        """Verify and decode JWT token."""
        return authenticate_user(token, self.secret_key)

    def create_token_pair(self, subject: str, user_claims: dict) -> tuple:
        """Create access token and refresh token pair."""
        import time

        # Create access token (short-lived)
        access_payload = {
            "sub": subject,
            "exp": int(time.time()) + 3600,  # 1 hour
            "type": "access",
            **user_claims,
        }
        access_token = generate_jwt_token(access_payload, self.secret_key)

        # Create refresh token (long-lived)
        refresh_payload = {
            "sub": subject,
            "exp": int(time.time()) + 86400 * 30,  # 30 days
            "type": "refresh",
        }
        refresh_token = generate_jwt_token(refresh_payload, self.secret_key)

        return (access_token, refresh_token)


__all__ = [
    "AuthenticationError","generate_jwt_token", "authenticate_user", "AuthService", "SecurityContext", "AuthContext"]


class AuthenticationError(Exception):
    """Authentication error exception."""
    
    def __init__(self, message="Authentication failed", status_code=401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)



class AuthorizationError(Exception):
    """Authorization error exception."""
    def __init__(self, message="Authorization failed", status_code=403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


# Auto-generated stubs for missing exports

class SecurityContext:
    """Stub class for SecurityContext."""

    def __init__(self, *args, **kwargs):
        pass


class AuthContext:
    """Stub class for AuthContext."""

    def __init__(self, *args, **kwargs):
        pass

