"""
CovetPy Security Integration Example

Complete example demonstrating all security features implemented in Days 22-24:
- CSRF Protection
- CORS Configuration
- Security Headers with CSP
- Input Sanitization
- Rate Limiting
- Security Audit Logging

This example shows production-ready security configuration for a real-world application.
"""

import asyncio
import re
from datetime import datetime, timedelta

# CovetPy imports (assumes package structure)
try:
    from covet.core.app import CovetApp
    from covet.core.http_objects import Request, Response

    # Security components
    from covet.security.csrf import CSRFConfig, CSRFProtection, get_csrf_protection
    from covet.security.csrf_middleware import CSRFMiddleware
    from covet.security.csrf_helpers import csrf_protect, csrf_exempt, add_csrf_to_jinja2

    from covet.middleware.cors import CORSMiddleware
    from covet.security.headers import SecurityHeadersMiddleware, CSPBuilder, CSPSource, SecurityPresets
    from covet.security.sanitization import sanitize_html, prevent_path_traversal, sanitize_filename, validate_email
    from covet.security.advanced_ratelimit import AdvancedRateLimitMiddleware, RateLimitConfig
    from covet.security.audit import get_audit_logger, configure_audit_logger, EventType, Severity

except ImportError:
    print("Note: This example requires CovetPy to be installed")
    print("The code demonstrates the security features available")


# ============================================================================
# SECURITY CONFIGURATION
# ============================================================================

def create_secure_app():
    """
    Create CovetPy application with production-grade security

    Security layers:
    1. Security Headers (CSP, HSTS, etc.)
    2. CORS Protection
    3. CSRF Protection
    4. Rate Limiting
    5. Audit Logging
    """

    app = CovetApp()

    # ========================================================================
    # 1. AUDIT LOGGING (Setup first to log all security events)
    # ========================================================================

    audit = configure_audit_logger(
        log_file='/var/log/myapp/security.log',
        retention_days=90,
        alert_callback=critical_security_alert  # Alert on critical events
    )

    # ========================================================================
    # 2. SECURITY HEADERS
    # ========================================================================

    # Option A: Use preset configuration
    # app.add_middleware(SecurityHeadersMiddleware, config=SecurityPresets.strict())

    # Option B: Custom CSP configuration
    csp = CSPBuilder()
    csp.default_src([CSPSource.SELF])
    csp.script_src([
        CSPSource.SELF,
        'https://cdn.example.com',
        'https://analytics.example.com'
    ])
    csp.style_src([CSPSource.SELF, CSPSource.UNSAFE_INLINE])  # Allow inline styles
    csp.img_src([CSPSource.SELF, CSPSource.DATA, CSPSource.HTTPS])
    csp.font_src([CSPSource.SELF, 'https://fonts.gstatic.com'])
    csp.connect_src([CSPSource.SELF, 'https://api.example.com'])
    csp.frame_ancestors([CSPSource.NONE])  # Prevent clickjacking
    csp.base_uri([CSPSource.SELF])
    csp.form_action([CSPSource.SELF])
    csp.upgrade_insecure_requests()  # Upgrade HTTP to HTTPS
    csp.report_uri('/api/csp-report')  # CSP violation reporting

    from covet.security.headers import SecurityHeadersConfig

    security_headers_config = SecurityHeadersConfig(
        csp_policy=csp.build(),
        hsts_max_age=31536000,  # 1 year
        hsts_include_subdomains=True,
        x_frame_options='DENY',
        referrer_policy='strict-origin-when-cross-origin',
        permissions_policy={
            'geolocation': [],  # Block geolocation
            'camera': [],       # Block camera
            'microphone': [],   # Block microphone
            'payment': ['self'],  # Allow payment API on same origin
        },
        cross_origin_opener_policy='same-origin',
        hide_server_header=True
    )

    app.add_middleware(SecurityHeadersMiddleware, config=security_headers_config)

    # ========================================================================
    # 3. CORS PROTECTION
    # ========================================================================

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            'https://app.example.com',
            'https://admin.example.com'
        ],
        allow_origin_regex=[
            re.compile(r'https://.*\.example\.com'),  # All subdomains
            re.compile(r'https://preview-\d+\.example\.com')  # Preview environments
        ],
        allow_credentials=True,  # Allow cookies/auth
        allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-CSRF-Token'],
        expose_headers=['X-Total-Count', 'X-Page-Count', 'X-Total-Pages'],
        max_age=86400,  # Cache preflight for 24 hours
        enforce_https_with_credentials=True
    )

    # ========================================================================
    # 4. CSRF PROTECTION
    # ========================================================================

    csrf_config = CSRFConfig(
        secret_key=b'your-production-secret-key-from-env',  # Load from environment!
        token_ttl=3600,  # 1 hour token validity
        cookie_secure=True,  # HTTPS only
        cookie_samesite='Strict',
        exempt_paths=[
            '/api/webhooks/github',  # GitHub webhooks
            '/api/webhooks/stripe',  # Stripe webhooks
            '/api/public/*',         # Public API endpoints
        ],
        validate_origin=True,
        validate_referer=True,
        rotate_after_use=True  # Prevent token reuse
    )

    app.add_middleware(CSRFMiddleware, config=csrf_config)

    # ========================================================================
    # 5. RATE LIMITING
    # ========================================================================

    # Default rate limit configuration
    default_rate_config = RateLimitConfig(
        requests=100,        # 100 requests
        window=60,           # per 60 seconds
        algorithm='token_bucket',  # Allows bursts
        include_headers=True
    )

    rate_limiter = AdvancedRateLimitMiddleware(
        app.wsgi_app if hasattr(app, 'wsgi_app') else app,
        default_config=default_rate_config,
        # Optional: Redis backend for distributed rate limiting
        # backend=RedisRateLimitBackend(redis_client),
        whitelist=['127.0.0.1', '::1'],  # Localhost exempt
    )

    # Endpoint-specific rate limits
    rate_limiter.add_endpoint_limit(
        '/api/auth/login',
        RateLimitConfig(requests=5, window=300)  # 5 attempts per 5 minutes
    )

    rate_limiter.add_endpoint_limit(
        '/api/search',
        RateLimitConfig(requests=20, window=60)  # 20 searches per minute
    )

    app.add_middleware(lambda app: rate_limiter)

    return app, audit


# ============================================================================
# SECURITY EVENT HANDLERS
# ============================================================================

async def critical_security_alert(event):
    """
    Handle critical security events

    This function is called when a critical security event occurs:
    - Session hijack attempts
    - SQL injection attempts
    - Multiple failed login attempts
    """
    print(f"🚨 CRITICAL SECURITY EVENT: {event.event_type}")
    print(f"   Message: {event.message}")
    print(f"   User: {event.user_id}")
    print(f"   IP: {event.ip_address}")

    # In production:
    # - Send email to security team
    # - Trigger PagerDuty/OpsGenie alert
    # - Post to Slack security channel
    # - Block IP address if needed


# ============================================================================
# APPLICATION ROUTES
# ============================================================================

def setup_routes(app, audit):
    """Setup application routes with security examples"""

    # ========================================================================
    # PUBLIC ENDPOINTS (No CSRF required)
    # ========================================================================

    @app.route('/')
    async def homepage(request):
        """Public homepage"""
        return Response(
            body="<h1>Secure Application</h1>",
            content_type='text/html'
        )

    @app.route('/api/public/status')
    @csrf_exempt
    async def public_status(request):
        """Public API endpoint (exempt from CSRF)"""
        return {
            'status': 'operational',
            'timestamp': datetime.utcnow().isoformat()
        }

    # ========================================================================
    # PROTECTED ENDPOINTS (CSRF required)
    # ========================================================================

    @app.route('/api/user/profile', methods=['GET', 'POST'])
    @csrf_protect()
    async def user_profile(request):
        """
        User profile endpoint

        Automatically protected by:
        - CSRF middleware (POST requires valid token)
        - Rate limiting (100 req/min default)
        - Security headers
        - Audit logging
        """

        if request.method == 'POST':
            # Log profile update
            await audit.log(
                event_type=EventType.PERMISSION_DENIED if not request.user else EventType.LOGIN_SUCCESS,
                severity=Severity.INFO,
                user_id=request.user.id if hasattr(request, 'user') else None,
                ip_address=request.client.host,
                message="User profile updated"
            )

            # Sanitize input
            name = sanitize_html(request.form.get('name', ''))
            email = request.form.get('email', '')

            if not validate_email(email):
                return {'error': 'Invalid email'}, 400

            # Update profile...
            return {'status': 'updated'}

        # GET request
        return {
            'user': {
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }

    # ========================================================================
    # FILE UPLOAD (Sanitization example)
    # ========================================================================

    @app.route('/api/upload', methods=['POST'])
    @csrf_protect()
    async def upload_file(request):
        """
        Secure file upload

        Demonstrates:
        - Filename sanitization
        - Path traversal prevention
        - File type validation
        """

        file = request.files.get('file')
        if not file:
            return {'error': 'No file provided'}, 400

        # Sanitize filename
        safe_filename = sanitize_filename(file.filename)

        # Prevent path traversal
        upload_dir = '/var/uploads/user_files'
        safe_path = prevent_path_traversal(
            f"{upload_dir}/{safe_filename}",
            upload_dir
        )

        # Validate file type (example)
        allowed_extensions = {'.jpg', '.png', '.pdf', '.txt'}
        import os
        ext = os.path.splitext(safe_filename)[1].lower()

        if ext not in allowed_extensions:
            await audit.log(
                event_type=EventType.XSS_ATTEMPT,
                severity=Severity.WARNING,
                ip_address=request.client.host,
                message=f"Attempted upload of disallowed file type: {ext}"
            )
            return {'error': 'File type not allowed'}, 400

        # Save file
        # with open(safe_path, 'wb') as f:
        #     f.write(await file.read())

        return {
            'status': 'uploaded',
            'filename': safe_filename
        }

    # ========================================================================
    # AUTHENTICATION ENDPOINTS
    # ========================================================================

    @app.route('/api/auth/login', methods=['POST'])
    async def login(request):
        """
        Login endpoint

        Protected by:
        - Rate limiting (5 attempts per 5 minutes)
        - CSRF protection
        - Audit logging
        """

        username = request.json.get('username')
        password = request.json.get('password')

        # Validate credentials (example)
        if username == 'admin' and password == 'secure_password':
            # Success
            await audit.log_login_success(
                user_id=username,
                ip_address=request.client.host,
                user_agent=request.headers.get('User-Agent')
            )

            return {
                'status': 'success',
                'token': 'jwt_token_here'
            }
        else:
            # Failed login
            await audit.log_login_failed(
                username=username,
                ip_address=request.client.host,
                reason='Invalid credentials'
            )

            return {'error': 'Invalid credentials'}, 401

    # ========================================================================
    # ADMIN ENDPOINTS (High security)
    # ========================================================================

    @app.route('/api/admin/users', methods=['DELETE'])
    @csrf_protect()
    async def delete_user(request):
        """
        Admin endpoint - delete user

        Demonstrates:
        - Permission checking
        - Audit logging for sensitive operations
        - Input validation
        """

        user_id = request.json.get('user_id')

        # Check permissions (example)
        if not hasattr(request, 'user') or not request.user.is_admin:
            await audit.log_permission_denied(
                user_id=request.user.id if hasattr(request, 'user') else 'anonymous',
                resource='/api/admin/users',
                action='delete',
                ip_address=request.client.host
            )
            return {'error': 'Permission denied'}, 403

        # Log deletion
        await audit.log(
            event_type=EventType.PRIVILEGE_ESCALATION,
            severity=Severity.WARNING,
            user_id=request.user.id,
            ip_address=request.client.host,
            message=f"Admin deleted user: {user_id}",
            details={'deleted_user_id': user_id}
        )

        # Perform deletion...
        return {'status': 'deleted'}

    # ========================================================================
    # CSP VIOLATION REPORTING
    # ========================================================================

    @app.route('/api/csp-report', methods=['POST'])
    @csrf_exempt  # CSP reports don't include CSRF tokens
    async def csp_report(request):
        """
        Content Security Policy violation reporting

        Receives and logs CSP violations from browsers
        """

        violation = request.json

        await audit.log(
            event_type=EventType.SECURITY_HEADER_VIOLATION,
            severity=Severity.WARNING,
            ip_address=request.client.host,
            message="CSP violation reported",
            details=violation
        )

        return {'status': 'received'}, 204

    # ========================================================================
    # SECURITY DASHBOARD (Example)
    # ========================================================================

    @app.route('/api/admin/security/stats')
    async def security_stats(request):
        """
        Security statistics dashboard

        Shows audit log statistics
        """

        # Get last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)

        stats = await audit.get_statistics(start_date=yesterday)

        # Get recent critical events
        critical_events = await audit.query(
            severity=Severity.CRITICAL,
            start_date=yesterday,
            limit=10
        )

        return {
            'stats': stats,
            'critical_events': [e.to_dict() for e in critical_events]
        }


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main application entry point

    Creates secure application with all security features enabled
    """

    # Create secure app
    app, audit = create_secure_app()

    # Setup routes
    setup_routes(app, audit)

    # Development server
    print("=" * 70)
    print("CovetPy Secure Application")
    print("=" * 70)
    print("\nSecurity Features Enabled:")
    print("  ✅ CSRF Protection (HMAC-SHA256, session-bound tokens)")
    print("  ✅ CORS Protection (origin validation, credentials support)")
    print("  ✅ Security Headers (CSP, HSTS, X-Frame-Options, etc.)")
    print("  ✅ Input Sanitization (XSS, path traversal prevention)")
    print("  ✅ Rate Limiting (token bucket, 100 req/min default)")
    print("  ✅ Audit Logging (comprehensive security event tracking)")
    print("\nEndpoints:")
    print("  Public:    GET  /")
    print("  Public:    GET  /api/public/status")
    print("  Protected: POST /api/user/profile")
    print("  Protected: POST /api/upload")
    print("  Protected: POST /api/auth/login (5 attempts/5min)")
    print("  Admin:     DELETE /api/admin/users")
    print("  Reporting: POST /api/csp-report")
    print("  Stats:     GET  /api/admin/security/stats")
    print("\n" + "=" * 70)

    # Run application
    # app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
# Example 1: Making a CSRF-protected request from JavaScript

```javascript
// Get CSRF token from meta tag
const token = document.querySelector('meta[name="csrf-token"]').content;

// Make protected POST request
fetch('/api/user/profile', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': token
    },
    credentials: 'include',  // Include cookies
    body: JSON.stringify({
        name: 'John Doe',
        email: 'john@example.com'
    })
});
```

# Example 2: HTML form with CSRF protection

```html
<form method="POST" action="/api/user/profile">
    {{ csrf_input() }}  <!-- Jinja2 helper -->
    <input type="text" name="name" value="John Doe">
    <input type="email" name="email" value="john@example.com">
    <button type="submit">Update Profile</button>
</form>
```

# Example 3: Query audit logs

```python
from covet.security.audit import get_audit_logger, EventType, Severity
from datetime import datetime, timedelta

audit = get_audit_logger()

# Get failed logins (last 24 hours)
yesterday = datetime.utcnow() - timedelta(days=1)
failed_logins = await audit.query(
    event_type=EventType.LOGIN_FAILED,
    start_date=yesterday,
    limit=100
)

print(f"Failed login attempts: {len(failed_logins)}")

for event in failed_logins:
    print(f"  {event.timestamp} - {event.ip_address} - {event.details.get('username')}")

# Get statistics
stats = await audit.get_statistics(start_date=yesterday)
print(f"Total security events: {stats['total_events']}")
print(f"By severity: {stats['by_severity']}")
print(f"Top IPs: {list(stats['by_ip'].items())[:5]}")
```

# Example 4: Custom rate limiting

```python
from covet.security.advanced_ratelimit import RateLimitConfig

# Strict rate limit for sensitive endpoints
strict_config = RateLimitConfig(
    requests=3,
    window=300,  # 3 requests per 5 minutes
    algorithm='sliding_window'  # More accurate
)

rate_limiter.add_endpoint_limit('/api/admin/delete', strict_config)

# Generous limit for public API
public_config = RateLimitConfig(
    requests=1000,
    window=60,
    algorithm='token_bucket'  # Allows bursts
)

rate_limiter.add_endpoint_limit('/api/public/*', public_config)
```

# Example 5: Input sanitization

```python
from covet.security.sanitization import (
    sanitize_html,
    prevent_path_traversal,
    sanitize_filename,
    validate_email
)

# Sanitize user-generated HTML content
unsafe_html = request.form.get('content')
safe_html = sanitize_html(unsafe_html, allowed_tags=['p', 'br', 'strong', 'em'])

# Prevent path traversal in file operations
user_path = request.args.get('file')
safe_path = prevent_path_traversal(user_path, '/var/uploads')

# Sanitize filename
uploaded_file = request.files.get('file')
safe_filename = sanitize_filename(uploaded_file.filename)

# Validate email
email = request.form.get('email')
if not validate_email(email):
    return {'error': 'Invalid email'}, 400
```
"""
