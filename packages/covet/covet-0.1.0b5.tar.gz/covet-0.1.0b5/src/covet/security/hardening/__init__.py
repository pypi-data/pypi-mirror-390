"""
CovetPy Security Hardening Module

Comprehensive OWASP Top 10 protection and security hardening.

Author: CovetPy Security Team
License: MIT
"""

from covet.security.hardening.audit_logging import (
    SecurityAuditLogger,
    SecurityEvent,
    SecurityEventType,
)
from covet.security.hardening.csrf_protection import (
    CSRFProtectionMethod,
    CSRFProtectionMiddleware,
    CSRFProtector,
    CSRFToken,
    CSRFTokenGenerator,
    CSRFTokenStore,
    CSRFTokenType,
    CSRFViolation,
    generate_csrf_token,
    validate_csrf_token,
)
from covet.security.hardening.deserialization import (
    DeserializationError,
    SafeDeserializer,
)
from covet.security.hardening.header_security import (
    FrameOptions,
    ReferrerPolicy,
    SecurityHeadersConfig,
    SecurityHeadersMiddleware,
    create_secure_headers_config,
)
from covet.security.hardening.injection_protection import (
    CommandInjectionProtector,
    InjectionDetection,
    InjectionProtectionMiddleware,
    InjectionSeverity,
    InjectionType,
    LDAPInjectionProtector,
    NoSQLInjectionProtector,
    SQLInjectionProtector,
    TemplateInjectionProtector,
    XMLInjectionProtector,
    detect_command_injection,
    detect_nosql_injection,
    detect_sql_injection,
)
from covet.security.hardening.input_validation import (
    FileUploadValidator,
    InputValidator,
    ValidationError,
    ValidationRule,
    ValidationType,
)
from covet.security.hardening.rate_limiting import (
    FixedWindowLimiter,
    LeakyBucketLimiter,
    RateLimitAlgorithm,
    RateLimitConfig,
    RateLimiter,
    RateLimitMiddleware,
    RateLimitResult,
    RateLimitScope,
    RateLimitViolation,
    RedisRateLimiter,
    SlidingWindowCounterLimiter,
    SlidingWindowLogLimiter,
    TokenBucketLimiter,
)
from covet.security.hardening.sensitive_data import (
    DataMasker,
    DataType,
    MemoryScrubber,
    ResponseSanitizer,
    SecureLogger,
    SensitiveDataDetector,
    SensitivePattern,
)
from covet.security.hardening.xss_protection import (
    ContentSecurityPolicy,
    EncodingContext,
    HTMLSanitizer,
    OutputEncoder,
    XSSDetection,
    XSSDetector,
    XSSProtectionMiddleware,
    XSSType,
    safe_html,
    safe_js,
    safe_output,
    safe_url,
)
from covet.security.hardening.xxe_protection import (
    XXEProtector,
)

__all__ = [
    # Injection Protection
    "InjectionType",
    "InjectionSeverity",
    "InjectionDetection",
    "SQLInjectionProtector",
    "NoSQLInjectionProtector",
    "CommandInjectionProtector",
    "LDAPInjectionProtector",
    "XMLInjectionProtector",
    "TemplateInjectionProtector",
    "InjectionProtectionMiddleware",
    "detect_sql_injection",
    "detect_nosql_injection",
    "detect_command_injection",
    # XSS Protection
    "XSSType",
    "EncodingContext",
    "XSSDetection",
    "XSSDetector",
    "OutputEncoder",
    "HTMLSanitizer",
    "ContentSecurityPolicy",
    "XSSProtectionMiddleware",
    "safe_output",
    "safe_html",
    "safe_js",
    "safe_url",
    # CSRF Protection
    "CSRFTokenType",
    "CSRFProtectionMethod",
    "CSRFToken",
    "CSRFViolation",
    "CSRFTokenGenerator",
    "CSRFTokenStore",
    "CSRFProtector",
    "CSRFProtectionMiddleware",
    "generate_csrf_token",
    "validate_csrf_token",
    # Rate Limiting
    "RateLimitAlgorithm",
    "RateLimitScope",
    "RateLimitConfig",
    "RateLimitResult",
    "RateLimitViolation",
    "TokenBucketLimiter",
    "LeakyBucketLimiter",
    "FixedWindowLimiter",
    "SlidingWindowLogLimiter",
    "SlidingWindowCounterLimiter",
    "RateLimiter",
    "RedisRateLimiter",
    "RateLimitMiddleware",
    # Header Security
    "FrameOptions",
    "ReferrerPolicy",
    "SecurityHeadersConfig",
    "SecurityHeadersMiddleware",
    "create_secure_headers_config",
    # Input Validation
    "ValidationError",
    "ValidationType",
    "ValidationRule",
    "InputValidator",
    "FileUploadValidator",
    # Sensitive Data Protection
    "DataType",
    "SensitivePattern",
    "SensitiveDataDetector",
    "DataMasker",
    "SecureLogger",
    "ResponseSanitizer",
    "MemoryScrubber",
    # Audit Logging
    "SecurityEventType",
    "SecurityEvent",
    "SecurityAuditLogger",
    # XXE Protection
    "XXEProtector",
    # Deserialization Protection
    "DeserializationError",
    "SafeDeserializer",
]
