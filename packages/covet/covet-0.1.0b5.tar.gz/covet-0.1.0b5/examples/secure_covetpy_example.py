"""
Production-Grade Secure CovetPy Application Example

This example demonstrates how to use all the security implementations
from Sprint 2 to create a fully secured web application.

Features Demonstrated:
1. Secure JWT authentication with PyJWT
2. OAuth2 server and client with Authlib
3. CSRF protection with double-submit cookies
4. Comprehensive security middleware
5. Input validation and sanitization
6. Rate limiting with Redis
7. Security headers and OWASP compliance
8. Real-time security monitoring

Security Architecture:
- Defense in depth with multiple security layers
- Production-ready configurations
- Comprehensive audit logging
- Real-time threat detection and response
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Import CovetPy core components
try:
    from src.covet.core.app import CovetApp, Request, Response
    from src.covet.core.http import json_response, redirect_response
    from src.covet.core.middleware import Middleware
    
    # Import secure implementations
    from src.covet.security.jwt_secure import SecureJWTAuth, JWTMiddleware
    from src.covet.security.oauth2_authlib import (
        OAuth2Server, OAuth2Client, RedisOAuth2Storage,
        GrantType, ClientType, ResponseType, OAuth2Scope
    )
    from src.covet.security.csrf_protection import CSRFProtection, CSRFMiddleware, csrf_token
    from src.covet.security.security_middleware import (
        ComprehensiveSecurityMiddleware,
        SecurityHeadersConfig,
        InputValidationConfig,
        RateLimitConfig
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all security modules are properly installed.")
    exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecureCovetPyApp:
    """Production-grade secure CovetPy application."""
    
    def __init__(
        self,
        secret_key: str,
        redis_url: str = "redis://localhost:6379",
        debug: bool = False,
    ):
        """
        Initialize secure application.
        
        Args:
            secret_key: Master secret key (min 64 chars for production)
            redis_url: Redis connection URL
            debug: Debug mode (should be False in production)
        """
        if len(secret_key) < 64:
            raise ValueError("Secret key must be at least 64 characters for production")
        
        self.secret_key = secret_key
        self.redis_url = redis_url
        self.debug = debug
        
        # Initialize core application
        self.app = CovetApp(debug=debug)
        
        # Initialize security components
        self._setup_security_components()
        self._setup_middleware()
        self._setup_routes()
        
        logger.info("Secure CovetPy application initialized")
    
    def _setup_security_components(self):
        """Initialize all security components."""
        # 1. JWT Authentication
        self.jwt_auth = SecureJWTAuth(
            secret_key=self.secret_key,
            algorithm="HS256",
            issuer="secure-covetpy-app",
            audience="secure-covetpy-api",
            access_token_expire_minutes=15,  # Short-lived for security
            refresh_token_expire_days=7,
            redis_url=self.redis_url,
            enable_blacklist=True,
            max_auth_attempts=5,
        )
        
        # 2. OAuth2 Server
        self.oauth2_storage = RedisOAuth2Storage(self.redis_url)
        
        # Register OAuth2 clients
        self.oauth2_clients = {
            "web_app": OAuth2Client(
                client_id="web_app",
                client_secret="web_app_secret_key_here",
                client_type=ClientType.CONFIDENTIAL,
                redirect_uris=["https://app.example.com/callback"],
                grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
                response_types=[ResponseType.CODE],
                scopes=[OAuth2Scope.OPENID, OAuth2Scope.PROFILE, OAuth2Scope.EMAIL, "read", "write"],
                require_pkce=True,
            ),
            "mobile_app": OAuth2Client(
                client_id="mobile_app", 
                client_secret=None,  # Public client
                client_type=ClientType.PUBLIC,
                redirect_uris=["com.example.app://callback"],
                grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.REFRESH_TOKEN],
                response_types=[ResponseType.CODE],
                scopes=[OAuth2Scope.OPENID, OAuth2Scope.PROFILE, "read"],
                require_pkce=True,  # Required for public clients
            ),
            "api_service": OAuth2Client(
                client_id="api_service",
                client_secret="api_service_secret_key_here",
                client_type=ClientType.CONFIDENTIAL,
                redirect_uris=[],  # No redirect for client credentials
                grant_types=[GrantType.CLIENT_CREDENTIALS],
                response_types=[],
                scopes=["api:read", "api:write"],
                require_pkce=False,
            ),
        }
        
        self.oauth2_server = OAuth2Server(
            storage=self.oauth2_storage,
            clients=self.oauth2_clients,
            issuer="https://auth.example.com",
            secret_key=self.secret_key,
            enable_pkce=True,
            require_pkce_for_public=True,
        )
        
        # 3. CSRF Protection
        self.csrf_protection = CSRFProtection(
            secret_key=self.secret_key,
            cookie_name="csrftoken",
            header_name="X-CSRFToken",
            token_lifetime=3600,
            cookie_secure=True,
            cookie_samesite="Strict",
            require_https=not self.debug,
            trusted_origins=["https://app.example.com", "https://admin.example.com"],
        )
        
        # 4. Security Configuration
        self.security_headers_config = SecurityHeadersConfig(
            enable_hsts=True,
            hsts_max_age=31536000,  # 1 year
            enable_csp=True,
            csp_default_src=["'self'"],
            csp_script_src=["'self'", "'unsafe-inline'"],  # Will use nonces in production
            csp_report_uri="/api/security/csp-report",
            x_frame_options="DENY",
        )
        
        self.input_validation_config = InputValidationConfig(
            max_request_size=10 * 1024 * 1024,  # 10MB
            max_query_params=100,
            max_form_fields=1000,
        )
        
        self.rate_limit_config = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            endpoint_limits={
                "/api/auth/login": {"requests_per_minute": 5},
                "/api/auth/register": {"requests_per_minute": 3},
                "/api/auth/forgot-password": {"requests_per_minute": 2},
            },
            redis_url=self.redis_url,
        )
    
    def _setup_middleware(self):
        """Setup security middleware stack."""
        # 1. Comprehensive Security Middleware (includes headers, validation, rate limiting)
        self.security_middleware = ComprehensiveSecurityMiddleware(
            security_headers_config=self.security_headers_config,
            input_validation_config=self.input_validation_config,
            rate_limit_config=self.rate_limit_config,
        )
        self.app.add_middleware(self.security_middleware)
        
        # 2. CSRF Protection Middleware
        self.csrf_middleware = CSRFMiddleware(
            csrf_protection=self.csrf_protection,
            exempt_paths=["/api/webhook", "/api/oauth2/", "/api/public/"],
        )
        self.app.add_middleware(self.csrf_middleware)
        
        # 3. JWT Authentication Middleware
        self.jwt_middleware = JWTMiddleware(
            jwt_auth=self.jwt_auth,
            protected_paths=["/api/protected/", "/api/user/", "/admin/"],
            excluded_paths=["/api/auth/", "/api/public/", "/api/oauth2/"],
        )
        self.app.add_middleware(self.jwt_middleware)
    
    def _setup_routes(self):
        """Setup application routes."""
        # Public routes
        self.app.route("GET", "/", self.home)
        self.app.route("GET", "/api/public/health", self.health_check)
        
        # Authentication routes
        self.app.route("POST", "/api/auth/login", self.login)
        self.app.route("POST", "/api/auth/register", self.register)
        self.app.route("POST", "/api/auth/refresh", self.refresh_token)
        self.app.route("POST", "/api/auth/logout", self.logout)
        
        # OAuth2 routes
        self.app.route("GET", "/api/oauth2/authorize", self.oauth2_authorize)
        self.app.route("POST", "/api/oauth2/token", self.oauth2_token)
        self.app.route("POST", "/api/oauth2/introspect", self.oauth2_introspect)
        self.app.route("POST", "/api/oauth2/revoke", self.oauth2_revoke)
        
        # Protected routes
        self.app.route("GET", "/api/protected/profile", self.get_profile)
        self.app.route("PUT", "/api/protected/profile", self.update_profile)
        self.app.route("GET", "/api/protected/data", self.get_user_data)
        
        # Admin routes
        self.app.route("GET", "/admin/security/events", self.get_security_events)
        self.app.route("GET", "/admin/security/stats", self.get_security_stats)
        
        # Security utility routes
        self.app.route("GET", "/api/csrf-token", self.get_csrf_token)
        self.app.route("POST", "/api/security/csp-report", self.csp_report)
    
    async def home(self, request: Request) -> Response:
        """Home page with CSRF protection demo."""
        csrf_token_value = csrf_token(request, self.csrf_protection)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Secure CovetPy App</title>
            <meta name="csrf-token" content="{csrf_token_value}">
        </head>
        <body>
            <h1>🔒 Secure CovetPy Application</h1>
            <p>This application demonstrates production-grade security features:</p>
            <ul>
                <li>✅ Secure JWT authentication with PyJWT</li>
                <li>✅ OAuth2 server with Authlib</li>
                <li>✅ CSRF protection with double-submit cookies</li>
                <li>✅ Input validation and sanitization</li>
                <li>✅ Rate limiting with Redis</li>
                <li>✅ Security headers and CSP</li>
                <li>✅ Real-time security monitoring</li>
            </ul>
            
            <h2>Test Authentication</h2>
            <form method="post" action="/api/auth/login">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token_value}">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            
            <h2>Security Status</h2>
            <ul>
                <li>HTTPS Enforced: {"✅" if not self.debug else "⚠️ (Debug Mode)"}</li>
                <li>CSRF Protection: ✅</li>
                <li>XSS Protection: ✅</li>
                <li>SQL Injection Protection: ✅</li>
                <li>Rate Limiting: ✅</li>
            </ul>
        </body>
        </html>
        """
        
        return Response(html, media_type="text/html")
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint."""
        return json_response({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "security": {
                "jwt_auth": "enabled",
                "oauth2": "enabled", 
                "csrf_protection": "enabled",
                "rate_limiting": "enabled",
                "input_validation": "enabled",
            }
        })
    
    async def login(self, request: Request) -> Response:
        """User login with comprehensive security."""
        try:
            # Get form data (already validated by input validation middleware)
            if hasattr(request.state, "sanitized_form"):
                form_data = request.state.sanitized_form
            else:
                form_data = await request.form()
            
            email = form_data.get("email")
            password = form_data.get("password")
            
            if not email or not password:
                return json_response(
                    {"error": "Email and password required"},
                    status_code=400
                )
            
            # In production, verify against database with hashed passwords
            # This is a demo implementation
            if email == "admin@example.com" and password == "secure_password":
                user_id = "admin_user_123"
                user_claims = {
                    "email": email,
                    "role": "admin",
                    "permissions": ["read", "write", "admin"]
                }
                
                # Create JWT token pair
                access_token, refresh_token = self.jwt_auth.create_token_pair(
                    subject=user_id,
                    user_claims=user_claims,
                    scopes=["read", "write", "admin"]
                )
                
                return json_response({
                    "success": True,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer",
                    "expires_in": 900,  # 15 minutes
                    "user": {
                        "id": user_id,
                        "email": email,
                        "role": "admin"
                    }
                })
            else:
                # Invalid credentials
                return json_response(
                    {"error": "Invalid credentials"},
                    status_code=401
                )
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return json_response(
                {"error": "Login failed"},
                status_code=500
            )
    
    async def register(self, request: Request) -> Response:
        """User registration with input validation."""
        try:
            form_data = await request.form()
            
            email = form_data.get("email")
            password = form_data.get("password")
            name = form_data.get("name")
            
            if not all([email, password, name]):
                return json_response(
                    {"error": "Email, password, and name required"},
                    status_code=400
                )
            
            # Password strength validation
            if len(password) < 12:
                return json_response(
                    {"error": "Password must be at least 12 characters"},
                    status_code=400
                )
            
            # In production, save to database with bcrypt/argon2 hashing
            user_id = f"user_{hash(email) % 1000000}"
            
            return json_response({
                "success": True,
                "message": "User registered successfully",
                "user_id": user_id
            })
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return json_response(
                {"error": "Registration failed"},
                status_code=500
            )
    
    async def refresh_token(self, request: Request) -> Response:
        """Refresh JWT tokens."""
        try:
            form_data = await request.form()
            refresh_token = form_data.get("refresh_token")
            
            if not refresh_token:
                return json_response(
                    {"error": "Refresh token required"},
                    status_code=400
                )
            
            # Refresh tokens
            new_access_token, new_refresh_token = self.jwt_auth.refresh_access_token(
                refresh_token,
                client_ip=request.client.host if request.client else None
            )
            
            return json_response({
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer",
                "expires_in": 900
            })
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return json_response(
                {"error": "Token refresh failed"},
                status_code=401
            )
    
    async def logout(self, request: Request) -> Response:
        """User logout with token blacklisting."""
        try:
            # Get token from Authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                self.jwt_auth.blacklist_token(token)
            
            return json_response({"success": True, "message": "Logged out successfully"})
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return json_response({"error": "Logout failed"}, status_code=500)
    
    async def oauth2_authorize(self, request: Request) -> Response:
        """OAuth2 authorization endpoint."""
        return await self.oauth2_server.authorize(request)
    
    async def oauth2_token(self, request: Request) -> Response:
        """OAuth2 token endpoint."""
        return await self.oauth2_server.token(request)
    
    async def oauth2_introspect(self, request: Request) -> Response:
        """OAuth2 token introspection endpoint."""
        return await self.oauth2_server.introspect(request)
    
    async def oauth2_revoke(self, request: Request) -> Response:
        """OAuth2 token revocation endpoint."""
        return await self.oauth2_server.revoke(request)
    
    async def get_profile(self, request: Request) -> Response:
        """Get user profile (protected endpoint)."""
        user_id = request.state.jwt_subject
        scopes = request.state.jwt_scopes
        
        # In production, fetch from database
        profile = {
            "user_id": user_id,
            "email": "admin@example.com",
            "name": "Admin User",
            "role": "admin",
            "scopes": scopes,
            "last_login": datetime.utcnow().isoformat()
        }
        
        return json_response(profile)
    
    async def update_profile(self, request: Request) -> Response:
        """Update user profile (protected endpoint with CSRF)."""
        user_id = request.state.jwt_subject
        
        try:
            # Get sanitized form data
            if hasattr(request.state, "sanitized_form"):
                form_data = request.state.sanitized_form
            else:
                form_data = await request.form()
            
            # In production, update database
            updated_fields = {
                "name": form_data.get("name"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            return json_response({
                "success": True,
                "message": "Profile updated successfully",
                "updated_fields": updated_fields
            })
            
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return json_response(
                {"error": "Profile update failed"},
                status_code=500
            )
    
    async def get_user_data(self, request: Request) -> Response:
        """Get user data with pagination (protected endpoint)."""
        user_id = request.state.jwt_subject
        
        # Query parameters are already validated by input validation middleware
        page = int(request.query_params.get("page", 1))
        limit = min(int(request.query_params.get("limit", 10)), 100)  # Max 100 items
        
        # In production, fetch from database with proper pagination
        data = {
            "user_id": user_id,
            "page": page,
            "limit": limit,
            "total": 150,
            "items": [
                {"id": i, "data": f"User data item {i}"} 
                for i in range((page - 1) * limit, min(page * limit, 150))
            ]
        }
        
        return json_response(data)
    
    async def get_security_events(self, request: Request) -> Response:
        """Get security events (admin only)."""
        # Check admin permissions (in production, verify from JWT claims)
        if not hasattr(request.state, "jwt_payload") or \
           request.state.jwt_payload.get("role") != "admin":
            return json_response({"error": "Admin access required"}, status_code=403)
        
        # Get security events from all middleware
        events = self.security_middleware.get_security_events(limit=100)
        
        return json_response({
            "events": events,
            "total": len(events),
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def get_security_stats(self, request: Request) -> Response:
        """Get security statistics (admin only)."""
        # Check admin permissions
        if not hasattr(request.state, "jwt_payload") or \
           request.state.jwt_payload.get("role") != "admin":
            return json_response({"error": "Admin access required"}, status_code=403)
        
        stats = {
            "jwt_auth": self.jwt_auth.get_security_stats(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return json_response(stats)
    
    async def get_csrf_token(self, request: Request) -> Response:
        """Get CSRF token for AJAX requests."""
        token = self.csrf_protection.generate_token(request)
        return json_response({
            "csrf_token": token,
            "cookie_name": self.csrf_protection.cookie_name,
            "header_name": self.csrf_protection.header_name
        })
    
    async def csp_report(self, request: Request) -> Response:
        """Handle CSP violation reports."""
        try:
            report_data = await request.json()
            logger.warning(f"CSP Violation: {report_data}")
            
            # In production, store in database for analysis
            return Response(status_code=204)  # No content
            
        except Exception as e:
            logger.error(f"CSP report error: {e}")
            return Response(status_code=400)
    
    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the secure application."""
        logger.info(f"Starting secure CovetPy application on {host}:{port}")
        logger.info("Security features enabled:")
        logger.info("  ✅ Secure JWT authentication")
        logger.info("  ✅ OAuth2 server with PKCE")
        logger.info("  ✅ CSRF protection")
        logger.info("  ✅ Input validation and sanitization")
        logger.info("  ✅ Rate limiting")
        logger.info("  ✅ Security headers")
        logger.info("  ✅ Real-time security monitoring")
        
        # In production, use ASGI server like uvicorn
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


def create_production_app() -> SecureCovetPyApp:
    """Create production-ready secure application."""
    # In production, load from environment variables
    secret_key = os.getenv(
        "SECRET_KEY",
        "your_production_secret_key_should_be_at_least_64_characters_long_and_random"
    )
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    return SecureCovetPyApp(
        secret_key=secret_key,
        redis_url=redis_url,
        debug=debug
    )


if __name__ == "__main__":
    print("🔒 Starting Secure CovetPy Application")
    print("=" * 50)
    print("This application demonstrates:")
    print("✅ Production-grade JWT authentication")
    print("✅ OAuth2 server with comprehensive security")
    print("✅ CSRF protection with double-submit cookies") 
    print("✅ Input validation and SQL injection protection")
    print("✅ XSS protection and sanitization")
    print("✅ Rate limiting with Redis")
    print("✅ Security headers and CSP")
    print("✅ Real-time security monitoring")
    print("=" * 50)
    
    # Create and run the application
    app = create_production_app()
    
    try:
        app.run(host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("\n👋 Shutting down secure application...")
    except Exception as e:
        print(f"❌ Application error: {e}")
        logger.error(f"Application startup failed: {e}")
    
    print("🔒 Secure CovetPy application stopped.")