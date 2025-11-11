"""
CovetPy Security Module

Comprehensive security components for authentication, authorization, encryption,
and protection against common web vulnerabilities. Follows OWASP guidelines
and security best practices.

Example usage:
    from covet.security import SimpleAuth, require_auth, PasswordHasher

    # Setup authentication
    auth = SimpleAuth("your-secret-key")

    # Register a user
    user = auth.register_user("john_doe", "secure_password", "john@example.com")

    # Create authentication middleware
    @require_auth(auth)
    async def protected_endpoint(request):
        return {"message": f"Hello {request.user.username}!"}
"""

from typing import TYPE_CHECKING

# Core authentication components - always available
from covet.security.simple_auth import (
    PasswordHasher,
    SimpleAuth,
    SimpleJWT,
    User,
    auth_middleware,
    require_auth,
    require_role,
)

# Production JWT authentication (when dependencies available)
try:
    from covet.security.jwt_auth import (
        JWTAlgorithm,
        JWTAuthenticator,
        JWTConfig,
        JWTManager,  # Alias for JWTAuthenticator
        JWTMiddleware,
        OAuth2ClientCredentialsFlow,
        OAuth2GrantType,
        OAuth2PasswordFlow,
        RBACManager,
        TokenBlacklist,
        TokenClaims,
        TokenPair,
        TokenType,
        require_permissions,
        require_roles,
    )

    _HAS_JWT_AUTH = True
except ImportError:
    _HAS_JWT_AUTH = False

# Import advanced authentication when available
try:
    from covet.auth import (
        JWTAuth,
        OAuth2Provider,
        RBACManager,
        SessionAuth,
        TwoFactorAuth,
    )

    _HAS_ADVANCED_AUTH = True
except ImportError:
    _HAS_ADVANCED_AUTH = False

# Import cryptographic components when available
try:
    from covet.security.crypto import (
        CryptoManager,
        EncryptionProvider,
        SecureHasher,
        SecureRandom,
    )

    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False

# Import CORS protection when available
try:
    from covet.security.cors import CORSMiddleware as SecurityCORSMiddleware
    from covet.security.cors import (
        CORSPolicy,
        configure_cors,
    )

    _HAS_CORS = True
except ImportError:
    _HAS_CORS = False

# Import CSRF protection when available
try:
    from covet.security.csrf import (
        CSRFMiddleware,
        CSRFProtection,
        generate_csrf_token,
        verify_csrf_token,
    )

    _HAS_CSRF = True
except ImportError:
    _HAS_CSRF = False

# Import rate limiting when available
try:
    from covet.security.rate_limiting import (
        InMemoryRateLimiter,
        RateLimiter,
        RateLimitPolicy,
        RedisRateLimiter,
    )

    _HAS_RATE_LIMITING = True
except ImportError:
    _HAS_RATE_LIMITING = False

# Import session management when available
try:
    from covet.security.sessions import (
        InMemorySessionStore,
        RedisSessionStore,
        SecureCookieSession,
        SessionManager,
        SessionStore,
    )

    _HAS_SESSIONS = True
except ImportError:
    _HAS_SESSIONS = False

# Import security headers when available
try:
    from covet.security.headers import (
        SecurityHeaders,
        SecurityHeadersMiddleware,
        configure_security_headers,
    )

    _HAS_SECURITY_HEADERS = True
except ImportError:
    _HAS_SECURITY_HEADERS = False

# Import input validation when available
try:
    from covet.security.validation import (
        InputValidator,
        PathTraversalProtection,
        SQLInjectionProtection,
        XSSProtection,
    )

    _HAS_VALIDATION = True
except ImportError:
    _HAS_VALIDATION = False

# Import enhanced validation module (new secure modules)
try:
    from covet.security.enhanced_validation import EnhancedValidator

    _HAS_ENHANCED_VALIDATION = True
except ImportError:
    _HAS_ENHANCED_VALIDATION = False

# Import secure JWT module (new secure modules)
try:
    from covet.security.secure_jwt import (
        ExpiredSignatureError,
        ExpiredTokenError,
        InvalidTokenError,
        JWTAuth,
        JWTError,
        SecureJWT,
        SecureJWTManager,
        configure_jwt,
        create_access_token,
        create_refresh_token,
        revoke_token,
        verify_token,
    )

    _HAS_SECURE_JWT = True
except ImportError:
    _HAS_SECURE_JWT = False

# Import secure crypto module (new secure modules)
try:
    from covet.security.secure_crypto import (
        SecureCrypto,
        constant_time_compare,
        generate_api_key,
        generate_csrf_token,
        generate_secure_token,
        generate_session_id,
        hash_password,
        verify_password,
    )

    _HAS_SECURE_CRYPTO = True
except ImportError:
    _HAS_SECURE_CRYPTO = False


# Public API exports - core security components always available
__all__ = [
    # Core authentication - Simple, zero-dependency auth system
    "SimpleAuth",  # Main authentication class
    "SimpleJWT",  # JWT token handling
    "PasswordHasher",  # Secure password hashing
    "User",  # User model
    "auth_middleware",  # Authentication middleware
    "require_auth",  # Authentication decorator
    "require_role",  # Role-based access control decorator
]

# Production JWT authentication
if _HAS_JWT_AUTH:
    __all__.extend(
        [
            "JWTAuthenticator",  # JWT token operations
            "JWTManager",  # Alias for JWTAuthenticator
            "JWTConfig",  # JWT configuration
            "JWTAlgorithm",  # JWT algorithms (HS256, RS256)
            "TokenType",  # Token types (access, refresh)
            "TokenPair",  # Access + refresh token pair
            "TokenClaims",  # JWT claims model
            "TokenBlacklist",  # Token revocation
            "RBACManager",  # Role-based access control
            "OAuth2PasswordFlow",  # OAuth2 password flow
            "OAuth2ClientCredentialsFlow",  # OAuth2 client credentials
            "OAuth2GrantType",  # OAuth2 grant types
            "JWTMiddleware",  # JWT ASGI middleware
            "require_permissions",  # Permission decorator
            "require_roles",  # Role decorator
        ]
    )

# Advanced authentication components
if _HAS_ADVANCED_AUTH:
    __all__.extend(
        [
            "JWTAuth",  # Advanced JWT authentication
            "OAuth2Provider",  # OAuth2 server implementation
            "SessionAuth",  # Session-based authentication
            "TwoFactorAuth",  # Two-factor authentication
            "RBACManager",  # Role-based access control
        ]
    )

# Cryptographic components
if _HAS_CRYPTO:
    __all__.extend(
        [
            "CryptoManager",  # Encryption/decryption management
            "SecureHasher",  # Cryptographic hashing
            "EncryptionProvider",  # Symmetric/asymmetric encryption
            "SecureRandom",  # Cryptographically secure random
        ]
    )

# CORS protection
if _HAS_CORS:
    __all__.extend(
        [
            "CORSPolicy",  # CORS policy configuration
            "SecurityCORSMiddleware",  # CORS middleware
            "configure_cors",  # CORS setup utility
        ]
    )

# CSRF protection
if _HAS_CSRF:
    __all__.extend(
        [
            "CSRFProtection",  # CSRF protection system
            "CSRFMiddleware",  # CSRF middleware
            "generate_csrf_token",  # CSRF token generation
            "verify_csrf_token",  # CSRF token verification
        ]
    )

# Rate limiting
if _HAS_RATE_LIMITING:
    __all__.extend(
        [
            "RateLimiter",  # Rate limiting interface
            "RateLimitPolicy",  # Rate limit policy configuration
            "InMemoryRateLimiter",  # In-memory rate limiter
            "RedisRateLimiter",  # Redis-backed rate limiter
        ]
    )

# Session management
if _HAS_SESSIONS:
    __all__.extend(
        [
            "SessionManager",  # Session lifecycle management
            "SessionStore",  # Session storage interface
            "InMemorySessionStore",  # In-memory session storage
            "RedisSessionStore",  # Redis session storage
            "SecureCookieSession",  # Secure cookie-based sessions
        ]
    )

# Security headers
if _HAS_SECURITY_HEADERS:
    __all__.extend(
        [
            "SecurityHeaders",  # Security headers configuration
            "SecurityHeadersMiddleware",  # Security headers middleware
            "configure_security_headers",  # Security headers setup
        ]
    )

# Input validation and protection
if _HAS_VALIDATION:
    __all__.extend(
        [
            "InputValidator",  # Input validation system
            "SQLInjectionProtection",  # SQL injection prevention
            "XSSProtection",  # Cross-site scripting protection
            "PathTraversalProtection",  # Path traversal prevention
        ]
    )

# Enhanced validation (new secure modules)
if _HAS_ENHANCED_VALIDATION:
    __all__.extend(
        [
            "EnhancedValidator",  # Enhanced input validation
        ]
    )

# Secure JWT (new secure modules)
if _HAS_SECURE_JWT:
    __all__.extend(
        [
            "SecureJWTManager",  # Secure JWT manager
            "SecureJWT",  # Simplified secure JWT interface
            "JWTAuth",  # JWT authentication helper
            "configure_jwt",  # Configure global JWT settings
            "create_access_token",  # Create access token
            "create_refresh_token",  # Create refresh token
            "verify_token",  # Verify JWT token
            "revoke_token",  # Revoke JWT token
            "InvalidTokenError",  # Invalid token exception
            "ExpiredSignatureError",  # Expired signature exception
            "JWTError",  # Base JWT error exception
            "ExpiredTokenError",  # Expired token exception
        ]
    )

# Secure crypto (new secure modules)
if _HAS_SECURE_CRYPTO:
    __all__.extend(
        [
            "SecureCrypto",  # Secure cryptography operations
            "hash_password",  # Hash password (convenience function)
            "verify_password",  # Verify password (convenience function)
            "generate_api_key",  # Generate API key
            "generate_secure_token",  # Generate secure token
            "generate_session_id",  # Generate session ID
            "generate_csrf_token",  # Generate CSRF token
            "constant_time_compare",  # Constant-time comparison
        ]
    )


def get_security_features():
    """
    Get a list of available security features in this installation.

    Returns:
        dict: Dictionary of security feature availability
    """
    return {
        "jwt_auth": _HAS_JWT_AUTH,
        "advanced_auth": _HAS_ADVANCED_AUTH,
        "crypto": _HAS_CRYPTO,
        "cors": _HAS_CORS,
        "csrf": _HAS_CSRF,
        "rate_limiting": _HAS_RATE_LIMITING,
        "sessions": _HAS_SESSIONS,
        "security_headers": _HAS_SECURITY_HEADERS,
        "validation": _HAS_VALIDATION,
        "enhanced_validation": _HAS_ENHANCED_VALIDATION,
        "secure_jwt": _HAS_SECURE_JWT,
        "secure_crypto": _HAS_SECURE_CRYPTO,
    }


def configure_basic_security(app, secret_key: str):
    """
    Configure basic security for a CovetPy application.

    This function sets up essential security measures including:
    - Authentication system
    - CSRF protection (if available)
    - Security headers (if available)
    - Rate limiting (if available)

    Args:
        app: CovetPy application instance
        secret_key: Secret key for cryptographic operations

    Returns:
        SimpleAuth: Configured authentication system
    """
    # Setup basic authentication
    auth = SimpleAuth(secret_key)

    # Add authentication middleware
    app.middleware(auth_middleware(auth))

    # Configure additional security if available
    if _HAS_CSRF:
        csrf = CSRFProtection(secret_key)
        app.middleware(CSRFMiddleware(csrf))

    if _HAS_SECURITY_HEADERS:
        app.middleware(SecurityHeadersMiddleware())

    if _HAS_RATE_LIMITING:
        rate_limiter = InMemoryRateLimiter()
        from covet.security.rate_limiting import RateLimitMiddleware

        app.middleware(RateLimitMiddleware(rate_limiter))

    return auth


# Add utility functions to exports
__all__.extend(
    [
        "get_security_features",
        "configure_basic_security",
    ]
)
