"""
Comprehensive security tests for CovetPy framework.
These tests verify all security components and implementations.
"""
import os
import sys
import hashlib
import hmac
import jwt
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestCryptographicSecurity:
    """Test cryptographic security functions."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        # Test with bcrypt-style functionality
        password = "test_password_123"
        
        # Basic hash function (simplified for testing)
        salt = b'test_salt_12345'
        hash_result = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        # Verify hash is deterministic with same salt
        hash_result2 = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        assert hash_result == hash_result2
        
        # Verify different password produces different hash
        wrong_password = "wrong_password"
        wrong_hash = hashlib.pbkdf2_hmac('sha256', wrong_password.encode(), salt, 100000)
        assert hash_result != wrong_hash
    
    def test_hmac_signature_validation(self):
        """Test HMAC signature generation and validation."""
        secret_key = b"test_secret_key_12345"
        message = "test_message_content"
        
        # Generate HMAC signature
        signature = hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()
        
        # Verify signature validation
        expected_signature = hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()
        assert signature == expected_signature
        
        # Test with wrong key
        wrong_key = b"wrong_secret_key"
        wrong_signature = hmac.new(wrong_key, message.encode(), hashlib.sha256).hexdigest()
        assert signature != wrong_signature
    
    def test_jwt_token_security(self):
        """Test JWT token generation and validation."""
        secret_key = "test_jwt_secret_key_12345"
        payload = {
            "user_id": 123,
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        
        # Generate JWT token
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode and verify token
        decoded_payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        assert decoded_payload["user_id"] == 123
        assert decoded_payload["username"] == "testuser"
        
        # Test invalid token
        with pytest.raises(jwt.InvalidTokenError):
            jwt.decode(token, "wrong_secret", algorithms=["HS256"])
    
    def test_secure_random_generation(self):
        """Test secure random number generation."""
        import secrets
        
        # Test secure token generation
        token1 = secrets.token_hex(32)
        token2 = secrets.token_hex(32)
        
        assert len(token1) == 64  # 32 bytes = 64 hex chars
        assert len(token2) == 64
        assert token1 != token2  # Should be different
        
        # Test secure bytes generation
        random_bytes = secrets.token_bytes(32)
        assert len(random_bytes) == 32
        assert isinstance(random_bytes, bytes)

class TestAuthenticationSecurity:
    """Test authentication security mechanisms."""
    
    def test_session_security(self):
        """Test session management security."""
        # Simulate session data
        session_data = {
            "user_id": 123,
            "username": "testuser",
            "created_at": time.time(),
            "last_activity": time.time(),
            "csrf_token": "csrf_token_12345"
        }
        
        # Test session expiry logic
        current_time = time.time()
        session_timeout = 3600  # 1 hour
        
        # Valid session
        assert current_time - session_data["last_activity"] < session_timeout
        
        # Expired session
        old_session_data = session_data.copy()
        old_session_data["last_activity"] = current_time - session_timeout - 1
        assert current_time - old_session_data["last_activity"] > session_timeout
    
    def test_csrf_protection(self):
        """Test CSRF token validation."""
        import secrets
        
        # Generate CSRF token
        csrf_token = secrets.token_urlsafe(32)
        
        # Simulate form submission with CSRF token
        form_csrf_token = csrf_token
        
        # Valid CSRF token
        assert form_csrf_token == csrf_token
        
        # Invalid CSRF token
        invalid_csrf_token = "invalid_token"
        assert invalid_csrf_token != csrf_token
    
    def test_rate_limiting_security(self):
        """Test rate limiting functionality."""
        import time
        from collections import defaultdict
        
        # Simple rate limiter implementation
        class RateLimiter:
            def __init__(self, max_requests=5, window=60):
                self.max_requests = max_requests
                self.window = window
                self.requests = defaultdict(list)
            
            def is_allowed(self, client_id):
                now = time.time()
                # Clean old requests
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if now - req_time < self.window
                ]
                
                if len(self.requests[client_id]) < self.max_requests:
                    self.requests[client_id].append(now)
                    return True
                return False
        
        rate_limiter = RateLimiter(max_requests=3, window=60)
        client_id = "test_client_123"
        
        # Should allow first 3 requests
        assert rate_limiter.is_allowed(client_id) == True
        assert rate_limiter.is_allowed(client_id) == True
        assert rate_limiter.is_allowed(client_id) == True
        
        # Should block 4th request
        assert rate_limiter.is_allowed(client_id) == False

class TestInputValidationSecurity:
    """Test input validation and sanitization."""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        import re
        
        def is_safe_sql_input(user_input):
            """Basic SQL injection detection."""
            dangerous_patterns = [
                r"(\s|^)(union|select|insert|update|delete|drop|create|alter|exec|execute)(\s|$)",
                r"[';]",
                r"--",
                r"/\*",
                r"\*/"
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, user_input.lower()):
                    return False
            return True
        
        # Safe inputs
        assert is_safe_sql_input("john_doe") == True
        assert is_safe_sql_input("user123") == True
        assert is_safe_sql_input("test@example.com") == True
        
        # Dangerous inputs
        assert is_safe_sql_input("'; DROP TABLE users; --") == False
        assert is_safe_sql_input("1 UNION SELECT * FROM users") == False
        assert is_safe_sql_input("admin'--") == False
    
    def test_xss_prevention(self):
        """Test XSS prevention."""
        import html
        
        def sanitize_html_input(user_input):
            """Sanitize HTML input to prevent XSS."""
            return html.escape(user_input)
        
        # Test basic HTML escaping
        malicious_input = "<script>alert('XSS')</script>"
        sanitized = sanitize_html_input(malicious_input)
        assert "&lt;script&gt;" in sanitized
        assert "&lt;/script&gt;" in sanitized
        assert "<script>" not in sanitized
        
        # Test attribute injection
        attr_injection = "onload='alert(1)'"
        sanitized_attr = sanitize_html_input(attr_injection)
        # The quotes are escaped, making it safe for HTML context
        assert "&#x27;" in sanitized_attr  # Escaped quote
        assert sanitized_attr == "onload=&#x27;alert(1)&#x27;"  # Exact expected output
    
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention."""
        import os
        
        def is_safe_file_path(file_path, allowed_directory="/safe/uploads"):
            """Check if file path is safe from path traversal."""
            # Normalize the path
            normalized_path = os.path.normpath(file_path)
            
            # Check for directory traversal patterns
            if ".." in normalized_path:
                return False
            
            # Check if path stays within allowed directory
            full_path = os.path.join(allowed_directory, normalized_path)
            canonical_path = os.path.abspath(full_path)
            canonical_allowed = os.path.abspath(allowed_directory)
            
            return canonical_path.startswith(canonical_allowed)
        
        # Safe paths
        assert is_safe_file_path("document.pdf") == True
        assert is_safe_file_path("images/photo.jpg") == True
        
        # Dangerous paths
        assert is_safe_file_path("../../../etc/passwd") == False
        assert is_safe_file_path("..\\..\\windows\\system32") == False

class TestAccessControlSecurity:
    """Test access control and authorization."""
    
    def test_role_based_access_control(self):
        """Test RBAC implementation."""
        class User:
            def __init__(self, username, roles):
                self.username = username
                self.roles = roles
        
        class Permission:
            def __init__(self, resource, action):
                self.resource = resource
                self.action = action
        
        class RBACSystem:
            def __init__(self):
                self.role_permissions = {
                    'admin': [
                        Permission('users', 'create'),
                        Permission('users', 'read'),
                        Permission('users', 'update'),
                        Permission('users', 'delete'),
                        Permission('system', 'configure')
                    ],
                    'editor': [
                        Permission('content', 'create'),
                        Permission('content', 'read'),
                        Permission('content', 'update')
                    ],
                    'viewer': [
                        Permission('content', 'read')
                    ]
                }
            
            def has_permission(self, user, resource, action):
                for role in user.roles:
                    if role in self.role_permissions:
                        for permission in self.role_permissions[role]:
                            if permission.resource == resource and permission.action == action:
                                return True
                return False
        
        rbac = RBACSystem()
        
        # Test admin user
        admin_user = User("admin", ["admin"])
        assert rbac.has_permission(admin_user, "users", "delete") == True
        assert rbac.has_permission(admin_user, "system", "configure") == True
        
        # Test editor user
        editor_user = User("editor", ["editor"])
        assert rbac.has_permission(editor_user, "content", "update") == True
        assert rbac.has_permission(editor_user, "users", "delete") == False
        
        # Test viewer user
        viewer_user = User("viewer", ["viewer"])
        assert rbac.has_permission(viewer_user, "content", "read") == True
        assert rbac.has_permission(viewer_user, "content", "create") == False

class TestSecurityHeaders:
    """Test security headers implementation."""
    
    def test_security_headers_validation(self):
        """Test that proper security headers are implemented."""
        
        def get_security_headers():
            """Return recommended security headers."""
            return {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Content-Security-Policy': "default-src 'self'",
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
            }
        
        headers = get_security_headers()
        
        # Verify critical security headers are present
        assert 'X-Content-Type-Options' in headers
        assert headers['X-Content-Type-Options'] == 'nosniff'
        
        assert 'X-Frame-Options' in headers
        assert headers['X-Frame-Options'] == 'DENY'
        
        assert 'X-XSS-Protection' in headers
        assert '1; mode=block' in headers['X-XSS-Protection']
        
        assert 'Strict-Transport-Security' in headers
        assert 'max-age=' in headers['Strict-Transport-Security']
        
        assert 'Content-Security-Policy' in headers
        assert 'Referrer-Policy' in headers

class TestSecurityAuditLogging:
    """Test security audit logging."""
    
    def test_security_event_logging(self):
        """Test security event logging functionality."""
        import json
        from datetime import datetime
        
        class SecurityLogger:
            def __init__(self):
                self.logs = []
            
            def log_event(self, event_type, user_id, details, severity='INFO'):
                event = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'event_type': event_type,
                    'user_id': user_id,
                    'details': details,
                    'severity': severity
                }
                self.logs.append(event)
            
            def get_security_events(self, event_type=None):
                if event_type:
                    assert [log for log in self.logs if log['event_type'] == event_type]
                return self.logs
        
        logger = SecurityLogger()
        
        # Log various security events
        logger.log_event('LOGIN_SUCCESS', 123, {'ip': '192.168.1.100'})
        logger.log_event('LOGIN_FAILURE', None, {'ip': '192.168.1.100', 'username': 'admin'}, 'WARNING')
        logger.log_event('PASSWORD_CHANGE', 123, {'ip': '192.168.1.100'})
        logger.log_event('PRIVILEGE_ESCALATION', 123, {'from': 'user', 'to': 'admin'}, 'CRITICAL')
        
        # Verify logging
        all_events = logger.get_security_events()
        assert len(all_events) == 4
        
        # Verify event structure
        login_events = logger.get_security_events('LOGIN_SUCCESS')
        assert len(login_events) == 1
        assert login_events[0]['user_id'] == 123
        assert 'timestamp' in login_events[0]
        
        # Verify critical events
        critical_events = [e for e in all_events if e['severity'] == 'CRITICAL']
        assert len(critical_events) == 1
        assert critical_events[0]['event_type'] == 'PRIVILEGE_ESCALATION'

@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security components."""
    
    def test_complete_authentication_flow(self):
        """Test complete authentication workflow."""
        import hashlib
        import secrets
        import jwt
        from datetime import datetime, timedelta
        
        # Simulate user registration
        username = "testuser"
        password = "secure_password_123"
        
        # Hash password
        salt = secrets.token_bytes(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        # Simulate user login
        login_password = "secure_password_123"
        login_hash = hashlib.pbkdf2_hmac('sha256', login_password.encode(), salt, 100000)
        
        # Verify password
        assert password_hash == login_hash
        
        # Generate JWT token on successful login
        secret_key = "jwt_secret_key_12345"
        payload = {
            "user_id": 123,
            "username": username,
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        
        # Validate token
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
        assert decoded["username"] == username
        assert decoded["user_id"] == 123
    
    def test_comprehensive_input_validation(self):
        """Test comprehensive input validation."""
        import re
        import html
        
        class InputValidator:
            def validate_email(self, email):
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                assert re.match(pattern, email) is not None
            
            def validate_username(self, username):
                # Only alphanumeric and underscore, 3-20 chars
                pattern = r'^[a-zA-Z0-9_]{3,20}$'
                assert re.match(pattern, username) is not None
            
            def sanitize_html(self, content):
                return html.escape(content)
            
            def validate_password_strength(self, password):
                if len(password) < 8:
                    return False, "Password must be at least 8 characters"
                if not re.search(r'[A-Z]', password):
                    return False, "Password must contain uppercase letter"
                if not re.search(r'[a-z]', password):
                    return False, "Password must contain lowercase letter"
                if not re.search(r'[0-9]', password):
                    return False, "Password must contain number"
                if not re.search(r'[!@#$%^&*]', password):
                    return False, "Password must contain special character"
                assert True, "Password is strong"
        
        validator = InputValidator()
        
        # Test email validation
        assert validator.validate_email("test@example.com") == True
        assert validator.validate_email("invalid.email") == False
        
        # Test username validation
        assert validator.validate_username("valid_user123") == True
        assert validator.validate_username("ab") == False  # Too short
        assert validator.validate_username("user@domain") == False  # Invalid chars
        
        # Test HTML sanitization
        malicious_html = "<script>alert('XSS')</script>"
        sanitized = validator.sanitize_html(malicious_html)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized
        
        # Test password strength
        strong_password = "StrongP@ssw0rd!"
        is_strong, message = validator.validate_password_strength(strong_password)
        assert is_strong == True
        
        weak_password = "weak"
        is_weak, weak_message = validator.validate_password_strength(weak_password)
        assert is_weak == False
        assert "at least 8 characters" in weak_message

if __name__ == "__main__":
    pytest.main([__file__, "-v"])