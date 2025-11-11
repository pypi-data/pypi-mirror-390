"""
Comprehensive Security Tests for Error Handling

Tests for Sprint 1.6: Information Disclosure Prevention

SECURITY TEST COVERAGE:
1. Environment-aware error responses
2. Stack trace sanitization
3. Sensitive data removal
4. Error correlation IDs
5. Security headers
6. Error rate limiting
7. Timing attack prevention
"""

import os
import pytest
import time
from unittest.mock import patch

from covet.security.error_security import (
    SecurityConfig,
    get_security_config,
    generate_error_id,
    sanitize_path,
    sanitize_sql_query,
    sanitize_connection_string,
    sanitize_ip_address,
    sanitize_stack_trace,
    sanitize_exception_context,
    create_secure_error_response,
    get_security_headers,
    constant_time_compare,
    add_timing_jitter,
    normalize_error_message,
    ErrorRateLimiter,
)

from covet.security.auth_security import (
    constant_time_compare as auth_constant_time_compare,
    add_auth_timing_jitter,
    normalize_auth_error,
    generate_secure_token,
    AuthRateLimiter,
)


class TestSecurityConfig:
    """Test security configuration"""

    def test_production_environment(self):
        """Test production environment detection"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            config = SecurityConfig()
            assert config.is_production is True
            assert config.is_development is False
            assert config.sanitize_paths is True
            assert config.remove_stack_traces is True

    def test_development_environment(self):
        """Test development environment detection"""
        with patch.dict(os.environ, {"COVET_ENV": "development"}):
            config = SecurityConfig()
            assert config.is_production is False
            assert config.is_development is True
            assert config.remove_stack_traces is False

    def test_default_environment(self):
        """Test default to production for safety"""
        with patch.dict(os.environ, {}, clear=True):
            config = SecurityConfig()
            # Should default to production for security
            assert config.is_production is True


class TestErrorIDGeneration:
    """Test error ID generation"""

    def test_error_id_format(self):
        """Test error ID has correct format"""
        error_id = generate_error_id()
        assert error_id.startswith("ERR-")
        assert len(error_id) == 20  # ERR- + 16 hex chars

    def test_error_id_uniqueness(self):
        """Test error IDs are unique"""
        ids = {generate_error_id() for _ in range(1000)}
        assert len(ids) == 1000  # All unique


class TestPathSanitization:
    """Test file path sanitization"""

    def test_sanitize_absolute_path(self):
        """Test absolute path sanitization"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            config = SecurityConfig()
            path = "/home/user/myproject/src/module.py"
            sanitized = sanitize_path(path, config)
            assert "/home/user" not in sanitized
            assert "<" in sanitized  # Should contain placeholder

    def test_sanitize_home_directory(self):
        """Test home directory sanitization"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            config = SecurityConfig()
            home = os.path.expanduser("~")
            path = f"{home}/myproject/file.py"
            sanitized = sanitize_path(path, config)
            assert home not in sanitized
            assert "<home>" in sanitized

    def test_sanitize_site_packages(self):
        """Test site-packages path sanitization"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            config = SecurityConfig()
            path = "/usr/local/lib/python3.9/site-packages/module.py"
            sanitized = sanitize_path(path, config)
            assert "<packages>" in sanitized

    def test_development_mode_preserves_paths(self):
        """Test paths preserved in development mode"""
        with patch.dict(os.environ, {"COVET_ENV": "development"}):
            config = SecurityConfig()
            path = "/home/user/myproject/src/module.py"
            sanitized = sanitize_path(path, config)
            # In development, paths are preserved
            assert sanitized == path


class TestSQLSanitization:
    """Test SQL query sanitization"""

    def test_sanitize_sql_literals(self):
        """Test SQL string literal sanitization"""
        query = "SELECT * FROM users WHERE email = 'user@example.com'"
        sanitized = sanitize_sql_query(query)
        assert "user@example.com" not in sanitized
        assert "<redacted>" in sanitized

    def test_sanitize_sql_passwords(self):
        """Test SQL password sanitization"""
        query = "UPDATE users SET password='secret123' WHERE id=1"
        sanitized = sanitize_sql_query(query)
        assert "secret123" not in sanitized
        assert "password=<redacted>" in sanitized.lower()

    def test_sanitize_sql_numeric_values(self):
        """Test SQL numeric value sanitization"""
        query = "SELECT * FROM orders WHERE user_id = 12345"
        sanitized = sanitize_sql_query(query)
        assert "12345" not in sanitized


class TestConnectionStringSanitization:
    """Test database connection string sanitization"""

    def test_sanitize_postgres_connection(self):
        """Test PostgreSQL connection string sanitization"""
        conn = "postgresql://username:secretpass@localhost:5432/mydb"
        sanitized = sanitize_connection_string(conn)
        assert "secretpass" not in sanitized
        assert "<redacted>" in sanitized

    def test_sanitize_mysql_connection(self):
        """Test MySQL connection string sanitization"""
        conn = "mysql://root:password123@127.0.0.1/database"
        sanitized = sanitize_connection_string(conn)
        assert "password123" not in sanitized
        assert "<redacted>" in sanitized

    def test_sanitize_api_keys(self):
        """Test API key sanitization in connection strings"""
        conn = "mongodb://host?api_key=sk_live_abc123xyz"
        sanitized = sanitize_connection_string(conn)
        assert "sk_live_abc123xyz" not in sanitized


class TestIPAddressSanitization:
    """Test IP address sanitization"""

    def test_sanitize_ipv4(self):
        """Test IPv4 address masking"""
        ip = "192.168.1.100"
        sanitized = sanitize_ip_address(ip)
        assert sanitized == "192.168.x.x"

    def test_sanitize_ipv6(self):
        """Test IPv6 address masking"""
        ip = "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
        sanitized = sanitize_ip_address(ip)
        assert "2001:0db8:85a3:0000" in sanitized
        assert ":x:x:x:x" in sanitized


class TestStackTraceSanitization:
    """Test stack trace sanitization"""

    def test_sanitize_file_paths_in_stack_trace(self):
        """Test file path sanitization in stack traces"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            config = SecurityConfig()
            trace = """Traceback (most recent call last):
  File "/home/user/myproject/app.py", line 10, in handler
    process_data(password="secret123")
  File "/usr/local/lib/python3.9/site-packages/module.py", line 5
    raise ValueError("Invalid data")
ValueError: Invalid data"""

            sanitized = sanitize_stack_trace(trace, config)
            assert "/home/user" not in sanitized
            assert "secret123" not in sanitized

    def test_sanitize_variables_in_stack_trace(self):
        """Test variable sanitization in stack traces"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            config = SecurityConfig()
            trace = "locals: password='secret', token='abc123'"
            sanitized = sanitize_stack_trace(trace, config)
            assert "secret" not in sanitized
            assert "password=<redacted>" in sanitized


class TestExceptionContextSanitization:
    """Test exception context sanitization"""

    def test_sanitize_password_in_context(self):
        """Test password removal from context"""
        context = {
            "username": "john",
            "password": "secret123",
            "email": "john@example.com"
        }
        sanitized = sanitize_exception_context(context)
        assert sanitized["password"] == "<redacted>"
        assert sanitized["username"] == "john"
        assert sanitized["email"] == "john@example.com"

    def test_sanitize_tokens_in_context(self):
        """Test token removal from context"""
        context = {
            "api_key": "sk_test_123",
            "access_token": "eyJhbGc...",
            "user_id": "123"
        }
        sanitized = sanitize_exception_context(context)
        assert sanitized["api_key"] == "<redacted>"
        assert sanitized["access_token"] == "<redacted>"
        assert sanitized["user_id"] == "123"

    def test_sanitize_connection_strings_in_context(self):
        """Test connection string sanitization in context"""
        context = {
            "database_url": "postgresql://user:pass@localhost/db"
        }
        sanitized = sanitize_exception_context(context)
        assert "pass" not in sanitized["database_url"]


class TestSecureErrorResponse:
    """Test secure error response generation"""

    def test_production_error_response(self):
        """Test production error response is generic"""
        with patch.dict(os.environ, {"COVET_ENV": "production"}):
            error = ValueError("Sensitive information here")
            response = create_secure_error_response(error)

            assert response["error"] == "An internal error occurred"
            assert response["error_id"].startswith("ERR-")
            assert "timestamp" in response
            assert "Sensitive information" not in str(response)

    def test_development_error_response(self):
        """Test development error response includes details"""
        with patch.dict(os.environ, {"COVET_ENV": "development"}):
            error = ValueError("Debug information")
            response = create_secure_error_response(error)

            assert "details" in response
            assert "stack_trace" in response
            assert "Debug information" in response["details"]

    def test_error_id_in_response(self):
        """Test error ID is included for correlation"""
        error = Exception("Test error")
        response = create_secure_error_response(error)
        assert "error_id" in response
        assert response["error_id"].startswith("ERR-")


class TestSecurityHeaders:
    """Test security headers"""

    def test_security_headers_present(self):
        """Test all required security headers are present"""
        headers = get_security_headers()

        assert b'x-content-type-options' in headers
        assert b'x-frame-options' in headers
        assert b'content-security-policy' in headers
        assert b'x-xss-protection' in headers

    def test_security_header_values(self):
        """Test security header values are correct"""
        headers = get_security_headers()

        assert headers[b'x-content-type-options'] == b'nosniff'
        assert headers[b'x-frame-options'] == b'DENY'
        assert b"default-src 'none'" in headers[b'content-security-policy']


class TestConstantTimeComparison:
    """Test constant-time comparison functions"""

    def test_constant_time_compare_equal(self):
        """Test constant-time comparison with equal strings"""
        assert constant_time_compare("secret123", "secret123") is True

    def test_constant_time_compare_not_equal(self):
        """Test constant-time comparison with different strings"""
        assert constant_time_compare("secret123", "secret456") is False

    def test_constant_time_compare_timing(self):
        """Test that comparison time is constant"""
        short_string = "a"
        long_string = "a" * 1000
        matching_long = "a" * 1000

        # Time comparison with short string
        start = time.perf_counter()
        for _ in range(1000):
            constant_time_compare(short_string, short_string)
        short_time = time.perf_counter() - start

        # Time comparison with long string
        start = time.perf_counter()
        for _ in range(1000):
            constant_time_compare(long_string, matching_long)
        long_time = time.perf_counter() - start

        # Times should be relatively similar (within order of magnitude)
        # This is a basic check - real timing attacks are more sophisticated
        assert long_time < short_time * 100  # Reasonable bound


class TestTimingJitter:
    """Test timing jitter functions"""

    def test_timing_jitter_adds_delay(self):
        """Test that timing jitter adds delay"""
        start = time.time()
        add_timing_jitter(min_ms=10, max_ms=20)
        elapsed = (time.time() - start) * 1000  # Convert to ms

        assert elapsed >= 10  # At least min delay
        assert elapsed <= 30  # Max delay + some tolerance

    def test_auth_timing_jitter(self):
        """Test authentication timing jitter"""
        start = time.time()
        add_auth_timing_jitter(min_ms=10, max_ms=30)
        elapsed = (time.time() - start) * 1000

        assert elapsed >= 10


class TestErrorMessageNormalization:
    """Test error message normalization"""

    def test_normalize_auth_error_user_not_found(self):
        """Test user not found returns generic message"""
        msg = normalize_error_message("", "auth")
        assert msg == "Invalid credentials"
        # Should NOT say "user not found"

    def test_normalize_auth_error_invalid_password(self):
        """Test invalid password returns same message as user not found"""
        msg = normalize_error_message("", "auth")
        assert msg == "Invalid credentials"
        # Prevents user enumeration

    def test_normalize_not_found_error(self):
        """Test not found error normalization"""
        msg = normalize_error_message("", "not_found")
        assert msg == "Resource not found"


class TestErrorRateLimiter:
    """Test error rate limiting"""

    def test_rate_limiter_tracks_errors(self):
        """Test rate limiter tracks error occurrences"""
        limiter = ErrorRateLimiter(
            window_seconds=60,
            max_errors=5,
            block_duration_seconds=300
        )

        client_id = "test_client_1"

        # Record errors
        for i in range(5):
            limiter.record_error(client_id, f"ERR-{i}")

        # Should not be limited yet
        is_limited, _ = limiter.is_rate_limited(client_id)
        assert is_limited is False

    def test_rate_limiter_blocks_excessive_errors(self):
        """Test rate limiter blocks after max errors"""
        limiter = ErrorRateLimiter(
            window_seconds=60,
            max_errors=3,
            block_duration_seconds=300
        )

        client_id = "test_client_2"

        # Exceed limit
        for i in range(5):
            limiter.record_error(client_id, f"ERR-{i}")

        # Should be blocked
        is_limited, retry_after = limiter.is_rate_limited(client_id)
        assert is_limited is True
        assert retry_after is not None
        assert retry_after > 0

    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleans up old entries"""
        limiter = ErrorRateLimiter(
            window_seconds=1,  # 1 second window
            max_errors=5
        )

        client_id = "test_client_3"

        # Record errors
        for i in range(3):
            limiter.record_error(client_id, f"ERR-{i}")

        # Wait for window to expire
        time.sleep(1.5)

        # Record one more
        limiter.record_error(client_id, "ERR-new")

        # Should only have 1 error in window
        stats = limiter.get_error_stats(client_id)
        assert stats["error_count"] == 1


class TestAuthRateLimiter:
    """Test authentication rate limiting"""

    def test_auth_limiter_tracks_failed_attempts(self):
        """Test auth limiter tracks failed login attempts"""
        limiter = AuthRateLimiter(
            max_attempts=3,
            window_seconds=300,
            lockout_duration=600
        )

        username = "testuser1"

        # Record failed attempts
        for _ in range(2):
            limiter.record_attempt(username, success=False)

        # Should not be locked yet
        is_locked, _ = limiter.is_locked_out(username)
        assert is_locked is False

        # One more failed attempt should trigger lockout
        limiter.record_attempt(username, success=False)

        is_locked, seconds = limiter.is_locked_out(username)
        assert is_locked is True
        assert seconds is not None

    def test_auth_limiter_resets_on_success(self):
        """Test auth limiter resets after successful login"""
        limiter = AuthRateLimiter(max_attempts=3)
        username = "testuser2"

        # Failed attempts
        limiter.record_attempt(username, success=False)
        limiter.record_attempt(username, success=False)

        # Success resets
        limiter.reset(username)

        # Should have full attempts available
        remaining = limiter.get_remaining_attempts(username)
        assert remaining == 3


class TestSecureTokenGeneration:
    """Test secure token generation"""

    def test_token_generation(self):
        """Test secure token generation"""
        token = generate_secure_token(32)
        assert len(token) == 64  # 32 bytes = 64 hex chars
        assert isinstance(token, str)

    def test_token_uniqueness(self):
        """Test tokens are unique"""
        tokens = {generate_secure_token(16) for _ in range(1000)}
        assert len(tokens) == 1000  # All unique


class TestAuthErrorNormalization:
    """Test authentication error normalization"""

    def test_normalize_user_not_found(self):
        """Test user not found gives generic message"""
        msg = normalize_auth_error("user_not_found")
        assert msg == "Invalid credentials"

    def test_normalize_invalid_password(self):
        """Test invalid password gives same message"""
        msg = normalize_auth_error("invalid_password")
        assert msg == "Invalid credentials"

    def test_normalize_account_locked(self):
        """Test account locked gives generic message"""
        msg = normalize_auth_error("account_locked")
        assert msg == "Invalid credentials"
        # Don't reveal account is locked!

    def test_normalize_2fa_invalid(self):
        """Test 2FA failure gives generic message"""
        msg = normalize_auth_error("2fa_invalid")
        assert msg == "Invalid credentials"
        # Don't reveal 2FA was the issue!


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
