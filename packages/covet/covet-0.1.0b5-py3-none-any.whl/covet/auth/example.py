"""
Complete Authentication System Example

This example demonstrates how to use all components of the CovetPy
authentication and authorization system in a production application.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from covet.auth import (  # Core managers; OAuth2; Models; Middleware; Security; Exceptions
    AuthConfig,
    AuthManager,
    InvalidCredentialsError,
    JWTConfig,
    OAuth2Provider,
    PasswordPolicy,
    PermissionDeniedError,
    SecurityConfig,
    SessionConfig,
    TwoFactorConfig,
    TwoFactorRequiredError,
    User,
    UserStatus,
    configure_auth_manager,
    configure_jwt_auth,
    configure_oauth2_provider,
    configure_session_manager,
    configure_two_factor_auth,
    cors,
    csrf_protection,
    get_auth_manager,
    get_security_manager,
    log_login_failed,
    log_login_success,
    require_auth,
    require_permission,
    require_permission_decorator,
    require_role,
    security_headers,
)
from covet.core.app import App
from covet.core.http import Request, Response
from covet.core.routing import Router

logger = logging.getLogger(__name__)

# Import the authentication system

# Import CovetPy framework components


def configure_authentication():
    """Configure the authentication system"""

    # Configure password policy
    password_policy = PasswordPolicy(
        min_length=12,
        require_uppercase=True,
        require_lowercase=True,
        require_digits=True,
        require_special_chars=True,
        max_age_days=90,
        history_count=5,
    )

    # Configure authentication
    auth_config = AuthConfig(
        password_policy=password_policy,
        max_login_attempts=5,
        lockout_duration_minutes=30,
        require_email_verification=True,
        allow_registration=True,
        default_user_role="user",
    )

    # Configure JWT with strong security
    jwt_config = JWTConfig(
        algorithm="RS256",  # Use RSA signing
        access_token_expire_minutes=15,
        refresh_token_expire_days=30,
        issuer="myapp",
        audience="myapp-api",
        include_jti=True,  # For token blacklisting
        require_https=True,
    )

    # Configure sessions
    session_config = SessionConfig(
        timeout_minutes=60,
        idle_timeout_minutes=30,
        regenerate_on_login=True,
        secure_cookies=True,
        httponly_cookies=True,
        samesite="Strict",
        csrf_protection=True,
        max_sessions_per_user=5,
    )

    # Configure 2FA
    two_factor_config = TwoFactorConfig(
        issuer="MyApp",
        verification_window=1,
        max_verification_attempts=5,
        lockout_duration_minutes=15,
    )

    # Configure security middleware
    security_config = SecurityConfig(
        require_auth_paths=["/api/", "/admin/"],
        exclude_auth_paths=["/auth/", "/health", "/docs"],
        rate_limit_requests=100,
        rate_limit_window_minutes=15,
        enable_security_headers=True,
        cors_origins=["https://myapp.com"],
        csrf_protection=True,
    )

    # Apply configurations
    configure_auth_manager(auth_config)
    configure_jwt_auth(jwt_config)
    configure_session_manager(session_config)
    configure_two_factor_auth(two_factor_config)

    # Configure OAuth2 providers
    configure_oauth2_provider(
        OAuth2Provider.GOOGLE,
        client_id="your-google-client-id",
        client_secret="your-google-client-secret",
        redirect_uri="https://myapp.com/auth/oauth2/google/callback",
    )

    configure_oauth2_provider(
        OAuth2Provider.GITHUB,
        client_id="your-github-client-id",
        client_secret="your-github-client-secret",
        redirect_uri="https://myapp.com/auth/oauth2/github/callback",
    )

    return security_config


def create_app():
    """Create the main application with authentication"""

    # Configure authentication
    security_config = configure_authentication()

    # Create app
    app = App()

    # Add security middleware (order matters!)
    app.add_middleware(security_headers(security_config))
    app.add_middleware(cors(security_config))
    app.add_middleware(csrf_protection(security_config))
    app.add_middleware(require_auth(security_config))

    # Create routers
    auth_router = create_auth_routes()
    api_router = create_api_routes()
    admin_router = create_admin_routes()

    # Mount routers
    app.mount("/auth", auth_router)
    app.mount("/api", api_router)
    app.mount("/admin", admin_router)

    return app


def create_auth_routes():
    """Create authentication routes"""
    from covet.auth import create_auth_router

    # The auth system provides pre-built endpoints
    return create_auth_router()


def create_api_routes():
    """Create API routes with authentication and authorization"""
    router = Router()

    @router.get("/profile")
    @require_permission_decorator("users", "read")
    def get_profile(request: Request, current_user: User):
        """Get user profile - requires 'users:read' permission"""
        return Response(
            {
                "user": current_user.to_dict(),
                "message": "Profile retrieved successfully",
            }
        )

    @router.put("/profile")
    @require_permission_decorator("users", "update")
    def update_profile(request: Request, current_user: User):
        """Update user profile - requires 'users:update' permission"""
        data = request.json()

        # Update user profile
        if "first_name" in data:
            current_user.first_name = data["first_name"]
        if "last_name" in data:
            current_user.last_name = data["last_name"]

        # Save user (in production, use proper database)
        auth_manager = get_auth_manager()
        auth_manager.user_store.update_user(current_user)

        return Response({"user": current_user.to_dict(), "message": "Profile updated successfully"})

    @router.get("/users")
    @require_permission_decorator("users", "read_all")
    def list_users(request: Request, current_user: User):
        """List all users - requires 'users:read_all' permission"""
        auth_manager = get_auth_manager()

        # In production, implement proper pagination
        users = [user.to_dict() for user in auth_manager.user_store._users.values()]

        return Response(
            {
                "users": users,
                "total": len(users),
                "message": "Users retrieved successfully",
            }
        )

    @router.post("/posts")
    @require_permission_decorator("posts", "create")
    def create_post(request: Request, current_user: User):
        """Create a post - requires 'posts:create' permission"""
        data = request.json()

        # Create post logic here
        post = {
            "id": "post_123",
            "title": data.get("title"),
            "content": data.get("content"),
            "author_id": current_user.id,
            "created_at": datetime.utcnow().isoformat(),
        }

        return Response({"post": post, "message": "Post created successfully"}, status_code=201)

    return router


def create_admin_routes():
    """Create admin routes with role-based access"""
    router = Router()

    @router.get("/dashboard")
    @require_role("admin")
    def admin_dashboard(request: Request, current_user: User):
        """Admin dashboard - requires 'admin' role"""
        security_manager = get_security_manager()
        metrics = security_manager.get_security_metrics()

        return Response({"metrics": metrics.to_dict(), "message": "Admin dashboard data"})

    @router.get("/security/events")
    @require_role("admin")
    def get_security_events(request: Request, current_user: User):
        """Get security events - admin only"""
        security_manager = get_security_manager()

        # Get events from last 24 hours
        start_time = datetime.utcnow() - timedelta(days=1)
        events = security_manager.audit_logger.get_events(start_time=start_time)

        return Response(
            {
                "events": [event.to_dict() for event in events],
                "total": len(events),
                "message": "Security events retrieved",
            }
        )

    @router.get("/reports/compliance")
    @require_role("admin")
    def generate_compliance_report(request: Request, current_user: User):
        """Generate compliance report - admin only"""
        security_manager = get_security_manager()

        # Generate report for last 30 days
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=30)

        access_report = security_manager.generate_compliance_report("access", start_time, end_time)
        security_report = security_manager.generate_compliance_report(
            "security", start_time, end_time
        )

        return Response(
            {
                "access_report": access_report,
                "security_report": security_report,
                "message": "Compliance reports generated",
            }
        )

    return router


async def setup_demo_data():
    """Setup demo users and permissions"""
    auth_manager = get_auth_manager()

    # Create demo admin user
    admin_result = auth_manager.register_user(
        username="admin",
        email="admin@example.com",
        password="SecureAdmin123!",
        first_name="System",
        last_name="Administrator",
    )

    if admin_result.success:
        admin_user = admin_result.user
        admin_user.status = UserStatus.ACTIVE  # Skip email verification
        admin_user.add_role("admin")
        auth_manager.user_store.update_user(admin_user)

        logger.info("✓ Created admin user: {admin_user.username}")

    # Create demo regular user
    user_result = auth_manager.register_user(
        username="john_doe",
        email="john@example.com",
        password="SecureUser123!",
        first_name="John",
        last_name="Doe",
    )

    if user_result.success:
        user = user_result.user
        user.status = UserStatus.ACTIVE  # Skip email verification
        auth_manager.user_store.update_user(user)

        logger.info("✓ Created user: {user.username}")

    # Setup 2FA for demo (optional)
    if admin_result.success and user_result.success:
        try:
            two_factor_auth = auth_manager.two_factor_auth
            secret, provisioning_uri, qr_code = two_factor_auth.setup_totp(admin_result.user)
            auth_manager.user_store.update_user(admin_result.user)

            logger.info("✓ 2FA enabled for admin user")
            logger.info("  Secret: {secret}")
            logger.info("  Provisioning URI: {provisioning_uri}")
        except Exception:
            logger.error("✗ Failed to setup 2FA: {e}")


def demonstrate_authentication():
    """Demonstrate authentication flows"""
    auth_manager = get_auth_manager()

    logger.info("\n=== Authentication Demo ===")

    # Test login
    try:
        login_result = auth_manager.login(
            username_or_email="admin",
            password="SecureAdmin123!",
            ip_address="192.168.1.100",
            user_agent="Demo Client",
        )

        if login_result.success:
            logger.info("✓ Admin login successful")
            user = login_result.user

            # Test permission checking
            try:
                auth_manager.rbac_manager.require_permission(user.id, "users", "read_all")
                logger.info("✓ Admin has users:read_all permission")
            except PermissionDeniedError:
                logger.info("✗ Admin lacks users:read_all permission")

            # Test role checking
            if auth_manager.rbac_manager.check_role(user.id, "admin"):
                logger.info("✓ Admin has admin role")
            else:
                logger.info("✗ Admin lacks admin role")

        else:
            logger.error("✗ Admin login failed: {login_result.message}")

    except Exception:
        logger.error("✗ Login error: {e}")

    # Test failed login
    try:
        auth_manager.login(
            username_or_email="admin",
            password="wrong_password",
            ip_address="192.168.1.100",
            user_agent="Demo Client",
        )
        logger.error("✓ Failed login properly rejected: {failed_login.message}")
    except Exception:
        logger.error("✗ Failed login error: {e}")


def demonstrate_security_monitoring():
    """Demonstrate security monitoring"""
    security_manager = get_security_manager()

    logger.info("\n=== Security Monitoring Demo ===")

    # Simulate security events
    log_login_success("admin", "192.168.1.100", "session_123")
    log_login_failed("unknown_user", "192.168.1.200", "Invalid credentials")
    log_permission_denied("john_doe", "admin", "access", "192.168.1.150")

    # Get security metrics
    security_manager.get_security_metrics()
    logger.info("✓ Security metrics: {metrics.successful_logins} successful logins")

    # Get recent events
    security_manager.audit_logger.get_events(start_time=datetime.utcnow() - timedelta(minutes=5))
    logger.info("✓ Recent security events: {len(recent_events)}")


async def main():
    """Main demo function"""
    logger.info("CovetPy Authentication System Demo")
    logger.info("=" * 40)

    # Configure the authentication system
    configure_authentication()
    logger.info("✓ Authentication system configured")

    # Setup demo data
    await setup_demo_data()

    # Demonstrate authentication
    demonstrate_authentication()

    # Demonstrate security monitoring
    demonstrate_security_monitoring()

    logger.info("\n=== Demo Complete ===")
    logger.info("\nThe authentication system is now ready for production use!")
    logger.info("\nKey features demonstrated:")
    logger.info("- User registration and login")
    logger.info("- Password security and validation")
    logger.info("- Role-based access control")
    logger.info("- Permission checking")
    logger.info("- Security event logging")
    logger.info("- 2FA support")
    logger.info("- JWT token authentication")
    logger.info("- Session management")
    logger.info("- OAuth2 configuration")
    logger.info("- Security middleware")
    logger.info("- Audit logging and monitoring")

    logger.info("\nNext steps:")
    logger.info("1. Configure your database for production")
    logger.info("2. Set up OAuth2 provider credentials")
    logger.info("3. Configure email service for verification")
    logger.info("4. Set up monitoring and alerting")
    logger.info("5. Customize permissions for your application")


if __name__ == "__main__":
    asyncio.run(main())
