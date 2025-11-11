"""
Comprehensive Unit Tests for Security Components

Tests all critical security features:
- Rate limiting (token bucket, Redis, in-memory)
- Security audit logging
- Input validation (SQL injection, XSS, CSRF, path traversal)
- IP filtering (allowlist, blocklist, CIDR)
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Import security components
from covet.middleware.rate_limiter import (
    InMemoryRateLimiter,
    RateLimitConfig,
    RateLimiter,
    TokenBucket,
)
from covet.security.audit_logger import (
    AuditEventType,
    AuditSeverity,
    SecurityAuditLogger,
)
from covet.security.ip_filter import (
    IPFilter,
    IPFilterRule,
    InMemoryIPFilter,
)
from covet.validation.validator import (
    CSRFValidator,
    InputValidator,
    PathTraversalError,
    SQLInjectionError,
    ValidationException,
    XSSError,
)


class TestTokenBucket:
    """Test token bucket algorithm implementation."""

    def test_bucket_creation(self):
        """Test bucket initialization."""
        bucket = TokenBucket(capacity=10, refill_rate=2.0)
        assert bucket.capacity == 10
        assert bucket.refill_rate == 2.0
        assert bucket.get_tokens() == 10.0

    def test_token_consumption(self):
        """Test consuming tokens."""
        bucket = TokenBucket(capacity=10, refill_rate=1.0)

        # Consume tokens
        assert bucket.consume(1) is True
        assert bucket.consume(5) is True
        assert bucket.consume(3) is True

        # Should have 1 token left
        assert bucket.consume(2) is False
        assert bucket.consume(1) is True

        # Bucket empty
        assert bucket.consume(1) is False

    def test_token_refill(self):
        """Test token bucket refills over time."""
        bucket = TokenBucket(capacity=10, refill_rate=10.0)  # 10 tokens/sec

        # Consume all tokens
        assert bucket.consume(10) is True
        assert bucket.consume(1) is False

        # Wait for refill (0.5 seconds = 5 tokens)
        time.sleep(0.5)

        # Should have ~5 tokens
        assert bucket.consume(5) is True
        assert bucket.consume(1) is False

    def test_bucket_max_capacity(self):
        """Test bucket doesn't exceed max capacity."""
        bucket = TokenBucket(capacity=5, refill_rate=10.0)

        # Wait for refill
        time.sleep(1.0)

        # Should still be capped at 5
        tokens = bucket.get_tokens()
        assert tokens <= 5.0

    def test_time_to_refill(self):
        """Test calculating refill time."""
        bucket = TokenBucket(capacity=10, refill_rate=2.0)  # 2 tokens/sec

        # Consume all tokens
        bucket.consume(10)

        # Should take ~0.5 seconds to get 1 token
        refill_time = bucket.time_to_refill()
        assert 0.4 <= refill_time <= 0.6


class TestInMemoryRateLimiter:
    """Test in-memory rate limiter."""

    @pytest.mark.asyncio
    async def test_basic_rate_limiting(self):
        """Test basic rate limit enforcement."""
        limiter = InMemoryRateLimiter(default_limit=5, default_window=60)

        # Should allow first 5 requests
        for i in range(5):
            result = await limiter.check_rate_limit("192.168.1.1")
            assert result.allowed is True
            assert result.remaining == 4 - i

        # 6th request should be blocked
        result = await limiter.check_rate_limit("192.168.1.1")
        assert result.allowed is False
        assert result.retry_after is not None

    @pytest.mark.asyncio
    async def test_endpoint_specific_limits(self):
        """Test per-endpoint rate limiting."""
        limiter = InMemoryRateLimiter(default_limit=100, default_window=60)

        # Configure strict limit for auth endpoint
        limiter.configure_endpoint("/api/auth/login", limit=3, window=60)

        # Auth endpoint should have strict limit
        for i in range(3):
            result = await limiter.check_rate_limit("192.168.1.1", "/api/auth/login")
            assert result.allowed is True

        result = await limiter.check_rate_limit("192.168.1.1", "/api/auth/login")
        assert result.allowed is False

        # Other endpoints should have default limit
        for i in range(10):
            result = await limiter.check_rate_limit("192.168.1.1", "/api/users")
            assert result.allowed is True

    @pytest.mark.asyncio
    async def test_per_ip_isolation(self):
        """Test that different IPs have separate limits."""
        limiter = InMemoryRateLimiter(default_limit=3, default_window=60)

        # IP1 consumes its limit
        for i in range(3):
            result = await limiter.check_rate_limit("192.168.1.1")
            assert result.allowed is True

        result = await limiter.check_rate_limit("192.168.1.1")
        assert result.allowed is False

        # IP2 should still have full quota
        for i in range(3):
            result = await limiter.check_rate_limit("192.168.1.2")
            assert result.allowed is True

    @pytest.mark.asyncio
    async def test_bucket_cleanup(self):
        """Test old bucket cleanup."""
        limiter = InMemoryRateLimiter(
            default_limit=10,
            default_window=60,
            cleanup_interval=0,  # Immediate cleanup
        )

        # Create buckets
        await limiter.check_rate_limit("192.168.1.1")
        await limiter.check_rate_limit("192.168.1.2")

        stats = limiter.get_stats()
        assert stats["total_buckets"] == 2

        # Cleanup happens automatically on next check
        # (in real usage, this happens periodically)


class TestSecurityAuditLogger:
    """Test security audit logging."""

    def test_logger_creation(self):
        """Test logger initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "security.log")
            logger = SecurityAuditLogger(
                log_file=log_file,
                console_output=False,
                structured_format=True,
            )

            assert os.path.exists(log_file)

    def test_auth_success_logging(self):
        """Test logging successful authentication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "security.log")
            logger = SecurityAuditLogger(
                log_file=log_file,
                console_output=False,
                structured_format=True,
            )

            logger.log_auth_attempt(
                username="john_doe",
                ip_address="192.168.1.100",
                success=True,
                method="password",
            )

            # Verify log file contains entry
            with open(log_file) as f:
                log_data = json.loads(f.read())
                assert log_data["event_type"] == "auth_success"
                assert log_data["username"] == "john_doe"
                assert log_data["success"] is True

    def test_auth_failure_logging(self):
        """Test logging failed authentication."""
        logger = SecurityAuditLogger(console_output=False)

        logger.log_auth_attempt(
            username="attacker",
            ip_address="203.0.113.100",
            success=False,
            method="password",
        )

        # Check that failure was tracked
        failure_count = logger.get_failed_auth_count("203.0.113.100", "ip")
        assert failure_count == 1

    def test_brute_force_detection(self):
        """Test automatic brute force detection."""
        logger = SecurityAuditLogger(console_output=False)
        logger.failed_auth_threshold = 3
        logger.failed_auth_window = 300

        ip = "203.0.113.100"

        # Simulate multiple failed attempts
        for i in range(3):
            logger.log_auth_attempt(
                username=f"user{i}",
                ip_address=ip,
                success=False,
            )

        # Should detect brute force (logged as security alert)
        assert logger.is_suspicious_activity(ip) is True

    def test_rate_limit_violation_logging(self):
        """Test logging rate limit violations."""
        logger = SecurityAuditLogger(console_output=False)

        logger.log_rate_limit_violation(
            ip_address="192.168.1.100",
            endpoint="/api/auth/login",
            limit=10,
            window=60,
        )

        stats = logger.get_statistics()
        assert stats["rate_limit_violations"] > 0

    def test_suspicious_activity_logging(self):
        """Test logging suspicious activity."""
        logger = SecurityAuditLogger(console_output=False)

        logger.log_suspicious_activity(
            ip_address="203.0.113.100",
            activity_type="sql_injection",
            description="SQL injection attempt detected",
            severity=AuditSeverity.CRITICAL,
        )

        assert logger.is_suspicious_activity("203.0.113.100") is True

    def test_data_access_logging(self):
        """Test logging data access events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "security.log")
            logger = SecurityAuditLogger(
                log_file=log_file,
                console_output=False,
                structured_format=True,
            )

            logger.log_data_access(
                user_id="user123",
                resource="/api/users/sensitive",
                action="READ",
                sensitive=True,
                record_count=100,
            )

            # Verify sensitive data access was logged
            with open(log_file) as f:
                log_data = json.loads(f.read())
                assert log_data["event_type"] == "sensitive_data_access"
                assert log_data["metadata"]["sensitive"] is True


class TestInputValidator:
    """Test input validation framework."""

    def test_string_validation(self):
        """Test basic string validation."""
        validator = InputValidator()

        # Valid string
        result = validator.validate_string("Hello, World!", min_length=1, max_length=20)
        assert result == "Hello, World!"

        # Too short
        with pytest.raises(ValidationException):
            validator.validate_string("Hi", min_length=10)

        # Too long
        with pytest.raises(ValidationException):
            validator.validate_string("x" * 1000, max_length=100)

    def test_sql_injection_detection(self):
        """Test SQL injection detection."""
        validator = InputValidator()

        # Should detect SQL injection attempts
        malicious_inputs = [
            "' OR '1'='1",
            "admin'--",
            "1; DROP TABLE users;",
            "1 UNION SELECT * FROM passwords",
        ]

        for malicious in malicious_inputs:
            with pytest.raises(SQLInjectionError):
                validator.check_sql_injection(malicious)

        # Should allow safe inputs
        safe_inputs = ["john_doe", "user@example.com", "Product Name 123"]
        for safe in safe_inputs:
            validator.check_sql_injection(safe)  # Should not raise

    def test_xss_detection(self):
        """Test XSS detection."""
        validator = InputValidator()

        # Should detect XSS attempts
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<iframe src='evil.com'></iframe>",
        ]

        for malicious in malicious_inputs:
            with pytest.raises(XSSError):
                validator.check_xss(malicious)

        # Should allow safe inputs
        safe_inputs = ["Hello, World!", "user@example.com", "Normal text"]
        for safe in safe_inputs:
            validator.check_xss(safe)  # Should not raise

    def test_html_sanitization(self):
        """Test HTML sanitization."""
        validator = InputValidator()

        # Full escaping
        malicious = "<script>alert('xss')</script>"
        sanitized = validator.sanitize_html(malicious, escape=True)
        assert "<script>" not in sanitized
        assert "&lt;script&gt;" in sanitized

    def test_path_traversal_detection(self):
        """Test path traversal detection."""
        validator = InputValidator()

        # Should detect path traversal attempts
        malicious_paths = [
            "../etc/passwd",
            "..\\windows\\system32",
            "....//....//etc/passwd",
            "%2e%2e/etc/passwd",
        ]

        for malicious in malicious_paths:
            with pytest.raises(PathTraversalError):
                validator.check_path_traversal(malicious)

        # Should allow safe paths
        safe_paths = ["documents/file.txt", "/var/www/public/image.png"]
        for safe in safe_paths:
            validator.check_path_traversal(safe)  # Should not raise

    def test_path_sanitization(self):
        """Test path sanitization with base directory."""
        validator = InputValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Should allow path within base directory
            safe_path = validator.sanitize_path("subdir/file.txt", base_dir=tmpdir)
            assert tmpdir in safe_path

            # Should reject path outside base directory
            with pytest.raises(PathTraversalError):
                validator.sanitize_path("../../etc/passwd", base_dir=tmpdir)

    def test_email_validation(self):
        """Test email validation."""
        validator = InputValidator()

        # Valid emails
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test+tag@domain.org",
        ]

        for email in valid_emails:
            result = validator.validate_email(email)
            assert result == email.lower()

        # Invalid emails
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "user@",
            "user@.com",
        ]

        for email in invalid_emails:
            with pytest.raises(ValidationException):
                validator.validate_email(email)

    def test_url_validation(self):
        """Test URL validation."""
        validator = InputValidator()

        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://example.com/path?query=value",
        ]

        for url in valid_urls:
            validator.validate_url(url)  # Should not raise

        # Invalid scheme
        with pytest.raises(ValidationException):
            validator.validate_url("ftp://example.com")

        # JavaScript URL (XSS vector)
        with pytest.raises(XSSError):
            validator.validate_url("javascript:alert(1)")


class TestCSRFValidator:
    """Test CSRF token validation."""

    def test_token_generation(self):
        """Test CSRF token generation."""
        validator = CSRFValidator(secret_key="test-secret-key")

        token1 = validator.generate_token()
        token2 = validator.generate_token()

        # Tokens should be unique
        assert token1 != token2
        assert len(token1) > 0

    def test_token_validation(self):
        """Test CSRF token validation."""
        validator = CSRFValidator(secret_key="test-secret-key")

        # Generate and validate token
        token = validator.generate_token(session_id="session123")
        assert validator.validate_token(token, session_id="session123") is True

        # Wrong session ID
        assert validator.validate_token(token, session_id="wrong") is False

        # Invalid token
        assert validator.validate_token("invalid-token") is False

    def test_token_timing_attack_resistance(self):
        """Test constant-time comparison."""
        validator = CSRFValidator(secret_key="test-secret-key")

        # Same length strings should use constant-time comparison
        result1 = validator._constant_time_compare("abc123", "abc123")
        result2 = validator._constant_time_compare("abc123", "xyz789")

        assert result1 is True
        assert result2 is False


class TestIPFilter:
    """Test IP filtering."""

    def test_basic_allowlist(self):
        """Test IP allowlist functionality."""
        filter = InMemoryIPFilter(
            allowlist=["192.168.1.100", "10.0.0.0/8"],
            default_action="block",
        )

        # Should allow whitelisted IPs
        allowed, _ = filter.is_allowed("192.168.1.100")
        assert allowed is True

        # Should allow CIDR range
        allowed, _ = filter.is_allowed("10.0.0.1")
        assert allowed is True

        allowed, _ = filter.is_allowed("10.255.255.255")
        assert allowed is True

        # Should block unlisted IPs
        allowed, reason = filter.is_allowed("203.0.113.100")
        assert allowed is False
        assert "not in allowlist" in reason

    def test_basic_blocklist(self):
        """Test IP blocklist functionality."""
        filter = InMemoryIPFilter(
            blocklist=["203.0.113.0/24"],
            default_action="allow",
        )

        # Should block blacklisted IPs
        allowed, reason = filter.is_allowed("203.0.113.50")
        assert allowed is False
        assert "blocked" in reason.lower()

        # Should allow other IPs
        allowed, _ = filter.is_allowed("192.168.1.100")
        assert allowed is True

    def test_cidr_notation(self):
        """Test CIDR notation support."""
        filter = InMemoryIPFilter(
            allowlist=["192.168.1.0/24"],
            default_action="block",
        )

        # Should allow entire subnet
        for i in range(256):
            ip = f"192.168.1.{i}"
            allowed, _ = filter.is_allowed(ip)
            assert allowed is True, f"Failed for {ip}"

        # Should block outside subnet
        allowed, _ = filter.is_allowed("192.168.2.1")
        assert allowed is False

    def test_temporary_blocks(self):
        """Test time-based temporary blocking."""
        filter = InMemoryIPFilter()

        # Block IP for 1 second
        filter.block_ip("203.0.113.100", duration=1, reason="Test block")

        # Should be blocked initially
        allowed, _ = filter.is_allowed("203.0.113.100")
        assert allowed is False

        # Wait for expiration
        time.sleep(1.1)

        # Should be allowed after expiration
        allowed, _ = filter.is_allowed("203.0.113.100")
        assert allowed is True

    def test_auto_blocking(self):
        """Test automatic IP blocking after violations."""
        filter = InMemoryIPFilter()
        filter.configure_auto_block(threshold=3, window=60, duration=300)

        ip = "203.0.113.100"

        # Record violations
        for i in range(3):
            was_blocked = filter.record_violation(ip)
            if i < 2:
                assert was_blocked is False
            else:
                assert was_blocked is True  # 3rd violation triggers block

        # IP should now be blocked
        allowed, reason = filter.is_allowed(ip)
        assert allowed is False
        assert "Auto-blocked" in reason

    def test_blocklist_priority(self):
        """Test that blocklist takes priority over allowlist."""
        filter = InMemoryIPFilter(
            allowlist=["192.168.1.0/24"],
            blocklist=["192.168.1.100"],
            default_action="block",
        )

        # 192.168.1.100 is in both lists - should be blocked
        allowed, _ = filter.is_allowed("192.168.1.100")
        assert allowed is False

        # Other IPs in allowlist should be allowed
        allowed, _ = filter.is_allowed("192.168.1.101")
        assert allowed is True


class TestIPFilterRule:
    """Test IP filter rule validation."""

    def test_rule_creation(self):
        """Test creating IP filter rules."""
        rule = IPFilterRule(
            ip_or_cidr="192.168.1.0/24",
            rule_type="allow",
            reason="Office network",
        )

        assert rule.ip_or_cidr == "192.168.1.0/24"
        assert rule.rule_type == "allow"

    def test_invalid_ip_format(self):
        """Test validation of IP format."""
        with pytest.raises(ValueError):
            IPFilterRule(
                ip_or_cidr="invalid-ip",
                rule_type="block",
            )

    def test_rule_expiration(self):
        """Test rule expiration."""
        # Create rule that expires in 1 second
        rule = IPFilterRule(
            ip_or_cidr="192.168.1.100",
            rule_type="block",
            expires_at=datetime.utcnow() + timedelta(seconds=1),
        )

        assert rule.is_expired() is False

        time.sleep(1.1)

        assert rule.is_expired() is True

    def test_ip_matching(self):
        """Test IP matching logic."""
        rule = IPFilterRule(
            ip_or_cidr="192.168.1.0/24",
            rule_type="allow",
        )

        # Should match IPs in range
        assert rule.matches("192.168.1.1") is True
        assert rule.matches("192.168.1.255") is True

        # Should not match outside range
        assert rule.matches("192.168.2.1") is False
        assert rule.matches("10.0.0.1") is False


# Integration Tests
class TestSecurityIntegration:
    """Integration tests for security components."""

    @pytest.mark.asyncio
    async def test_rate_limit_with_audit_logging(self):
        """Test rate limiter integration with audit logger."""
        limiter = InMemoryRateLimiter(default_limit=3, default_window=60)
        logger = SecurityAuditLogger(console_output=False)

        ip = "192.168.1.100"

        # Make requests until rate limited
        for i in range(4):
            result = await limiter.check_rate_limit(ip, "/api/test")

            if not result.allowed:
                # Log rate limit violation
                logger.log_rate_limit_violation(
                    ip_address=ip,
                    endpoint="/api/test",
                    limit=result.limit,
                    window=60,
                )

        # Verify violation was logged
        stats = logger.get_statistics()
        assert stats["rate_limit_violations"] > 0

    def test_ip_filter_with_audit_logging(self):
        """Test IP filter integration with audit logger."""
        ip_filter = InMemoryIPFilter(blocklist=["203.0.113.100"])
        logger = SecurityAuditLogger(console_output=False)

        # Try to access from blocked IP
        allowed, reason = ip_filter.is_allowed("203.0.113.100")

        if not allowed:
            logger.log_security_alert(
                message=f"Blocked IP attempted access: {reason}",
                ip_address="203.0.113.100",
                alert_type="ip_blocked",
            )

        assert allowed is False
        assert logger.is_suspicious_activity("203.0.113.100") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
