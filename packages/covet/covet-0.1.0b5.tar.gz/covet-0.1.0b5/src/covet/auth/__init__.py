"""
CovetPy Authentication and Authorization System

A comprehensive, production-ready authentication system with:
- Secure password hashing with scrypt
- JWT token authentication with RS256/ES256
- Session management with CSRF protection
- OAuth2 support (Google, GitHub, Microsoft, etc.)
- Role-based access control (RBAC) with fine-grained permissions
- Permissions system with context-aware evaluation
- 2FA support (TOTP) with backup codes
- Comprehensive security middleware
- Audit logging and security monitoring
- Threat detection and compliance reporting

Quick Start (Simple API):
    from covet import Covet
    from covet.auth import Auth, login_required

    app = Covet()
    auth = Auth(app, secret_key='your-secret-key')

    @app.route('/login', methods=['POST'])
    async def login(request):
        data = await request.json()
        if verify_credentials(data['username'], data['password']):
            token = auth.create_token(user_id=data['username'])
            return {'token': token}
        return {'error': 'Invalid credentials'}, 401

    @app.route('/protected')
    @login_required
    async def protected(request):
        return {'user': request.user_id}
"""

# Simple Authentication API (recommended for most users)
from .simple_auth import Auth, create_auth
from .decorators import login_required, roles_required, permission_required
from .jwt import JWTAuth as SimpleJWTAuth
from .password import (
    hash_password,
    verify_password,
    check_password_strength,
    generate_secure_password,
)

# Advanced Authentication and authorization managers
from .auth import AuthManager, TokenManager, configure_auth_manager, get_auth_manager

# API endpoints
from .endpoints import AuthEndpoints, create_auth_router

# Exceptions
from .exceptions import (
    AccountLockedError,
    AuthException,
    InvalidCredentialsError,
    OAuth2Error,
    PasswordResetRequiredError,
    PermissionDeniedError,
    RateLimitExceededError,
    RoleRequiredError,
    SecurityViolationError,
    SessionExpiredError,
    TokenExpiredError,
    TokenInvalidError,
    TwoFactorInvalidError,
    TwoFactorRequiredError,
    to_dict,
)
from .jwt_auth import JWTAuth, JWTConfig, TokenPair, configure_jwt_auth, get_jwt_auth

# Middleware
from .middleware import (
    AuthMiddleware,
    CORSMiddleware,
    CSRFMiddleware,
    RateLimitMiddleware,
    RBACMiddleware,
    SecurityConfig,
    SecurityHeadersMiddleware,
    cors,
    csrf_protection,
    rate_limit,
    require_auth,
    require_permission,
    security_headers,
)

# Core models
from .models import (
    LoginAttempt,
    PasswordPolicy,
    PasswordResetToken,
    Permission,
    Role,
    SecuritySettings,
    Session,
    TwoFactorSecret,
    User,
    UserStatus,
)
from .oauth2 import (
    OAuth2Config,
    OAuth2Manager,
    OAuth2Provider,
    configure_oauth2_provider,
    get_oauth2_manager,
)

# Decorators for easy use
from .rbac import AccessContext, RBACManager, configure_rbac_manager, get_rbac_manager
from .rbac import require_permission as require_permission_decorator
from .rbac import require_role

# Security and monitoring
from .security import (
    SecurityEvent,
    SecurityEventSeverity,
    SecurityEventType,
    SecurityManager,
    configure_security_manager,
    get_security_manager,
    log_login_failed,
    log_login_success,
    log_permission_denied,
)
from .session import (
    SessionConfig,
    SessionManager,
    configure_session_manager,
    get_session_manager,
)
from .two_factor import (
    TwoFactorAuth,
    TwoFactorConfig,
    configure_two_factor_auth,
    get_two_factor_auth,
)

__version__ = "1.0.0"

__all__ = [
    # ============================================================
    # SIMPLE API (Recommended for most users)
    # ============================================================
    # Main Auth class - Flask-like API
    "Auth",
    "create_auth",
    # Decorators
    "login_required",
    "roles_required",
    "permission_required",
    # Password utilities
    "hash_password",
    "verify_password",
    "check_password_strength",
    "generate_secure_password",
    # JWT auth
    "SimpleJWTAuth",

    # ============================================================
    # ADVANCED API (For complex use cases)
    # ============================================================
    # Models
    "User",
    "Role",
    "Permission",
    "Session",
    "UserStatus",
    "PasswordPolicy",
    "SecuritySettings",
    "TwoFactorSecret",
    "LoginAttempt",
    "PasswordResetToken",
    # Core managers
    "AuthManager",
    "TokenManager",
    "JWTAuth",
    "SessionManager",
    "OAuth2Manager",
    "RBACManager",
    "TwoFactorAuth",
    "SecurityManager",
    # Configuration
    "JWTConfig",
    "SessionConfig",
    "OAuth2Config",
    "TwoFactorConfig",
    "SecurityConfig",
    # OAuth2
    "OAuth2Provider",
    # Security
    "SecurityEvent",
    "SecurityEventType",
    "SecurityEventSeverity",
    "AccessContext",
    # Middleware
    "AuthMiddleware",
    "RBACMiddleware",
    "RateLimitMiddleware",
    "SecurityHeadersMiddleware",
    "CORSMiddleware",
    "CSRFMiddleware",
    # API
    "AuthEndpoints",
    "create_auth_router",
    # Exceptions
    "AuthException",
    "InvalidCredentialsError",
    "TokenExpiredError",
    "TokenInvalidError",
    "PermissionDeniedError",
    "RoleRequiredError",
    "TwoFactorRequiredError",
    "TwoFactorInvalidError",
    "AccountLockedError",
    "PasswordResetRequiredError",
    "OAuth2Error",
    "SessionExpiredError",
    "RateLimitExceededError",
    "SecurityViolationError",
    # Singleton getters
    "get_auth_manager",
    "get_jwt_auth",
    "get_session_manager",
    "get_oauth2_manager",
    "get_rbac_manager",
    "get_two_factor_auth",
    "get_security_manager",
    # Configuration functions
    "configure_auth_manager",
    "configure_jwt_auth",
    "configure_session_manager",
    "configure_oauth2_provider",
    "configure_rbac_manager",
    "configure_two_factor_auth",
    "configure_security_manager",
    # Convenience functions
    "require_auth",
    "require_permission",
    "rate_limit",
    "security_headers",
    "cors",
    "csrf_protection",
    "require_permission_decorator",
    "require_role",
    "log_login_success",
    "log_login_failed",
    "log_permission_denied",
    # Utilities
    "to_dict",
    "TokenPair",
]
