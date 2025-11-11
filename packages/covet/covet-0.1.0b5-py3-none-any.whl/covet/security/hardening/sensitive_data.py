"""
CovetPy Sensitive Data Protection Module

Comprehensive protection for sensitive data including:
- Data masking (credit cards, SSN, emails, phone numbers)
- Secret detection in logs/responses
- PII (Personally Identifiable Information) handling
- Secure credential storage
- Memory scrubbing for sensitive data

Implements OWASP Top 10 2021 - A02:2021 Cryptographic Failures and
A04:2021 Insecure Design (sensitive data exposure) protections.

Author: CovetPy Security Team
License: MIT
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern, Set

logger = logging.getLogger(__name__)


class DataType(Enum):
    """Types of sensitive data."""

    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    API_KEY = "api_key"
    PASSWORD = "password"
    JWT_TOKEN = "jwt_token"
    AWS_KEY = "aws_key"
    PRIVATE_KEY = "private_key"


@dataclass
class SensitivePattern:
    """Pattern for detecting sensitive data."""

    data_type: DataType
    pattern: Pattern
    mask_char: str = "*"
    reveal_chars: int = 4  # Number of chars to reveal


class SensitiveDataDetector:
    """
    Detect sensitive data in strings.
    """

    # Regex patterns for sensitive data
    PATTERNS = [
        SensitivePattern(
            DataType.CREDIT_CARD, re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"), reveal_chars=4
        ),
        SensitivePattern(DataType.SSN, re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), reveal_chars=4),
        SensitivePattern(
            DataType.EMAIL,
            re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            reveal_chars=3,
        ),
        SensitivePattern(
            DataType.PHONE,
            re.compile(r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b"),
            reveal_chars=4,
        ),
        SensitivePattern(DataType.API_KEY, re.compile(r"\b[A-Za-z0-9]{32,}\b"), reveal_chars=6),
        SensitivePattern(
            DataType.PASSWORD,
            re.compile(r'(password|passwd|pwd)[\s]*[:=][\s]*[\'"]?([^\s\'"]+)', re.IGNORECASE),
            reveal_chars=0,
        ),
        SensitivePattern(
            DataType.JWT_TOKEN,
            re.compile(r"\beyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\b"),
            reveal_chars=10,
        ),
        SensitivePattern(DataType.AWS_KEY, re.compile(r"\bAKIA[0-9A-Z]{16}\b"), reveal_chars=8),
        SensitivePattern(
            DataType.PRIVATE_KEY,
            re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----"),
            reveal_chars=0,
        ),
    ]

    def __init__(self, custom_patterns: Optional[List[SensitivePattern]] = None):
        """
        Initialize sensitive data detector.

        Args:
            custom_patterns: Additional custom patterns to detect
        """
        self.patterns = self.PATTERNS.copy()
        if custom_patterns:
            self.patterns.extend(custom_patterns)

    def detect(self, text: str) -> Dict[DataType, List[str]]:
        """
        Detect sensitive data in text.

        Args:
            text: Text to scan

        Returns:
            Dictionary of detected sensitive data by type
        """
        detected = {}

        for pattern_info in self.patterns:
            matches = pattern_info.pattern.findall(text)
            if matches:
                if pattern_info.data_type not in detected:
                    detected[pattern_info.data_type] = []
                detected[pattern_info.data_type].extend(matches)

        return detected

    def has_sensitive_data(self, text: str) -> bool:
        """Check if text contains any sensitive data."""
        for pattern_info in self.patterns:
            if pattern_info.pattern.search(text):
                return True
        return False


class DataMasker:
    """
    Mask sensitive data.
    """

    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """
        Mask credit card number, showing only last 4 digits.

        Example: 4532-1234-5678-9012 -> ****-****-****-9012
        """
        digits = re.sub(r"[^0-9]", "", card_number)
        if len(digits) < 13:
            return "*" * len(card_number)

        masked = "*" * (len(digits) - 4) + digits[-4:]
        # Preserve original formatting
        result = ""
        digit_idx = 0
        for char in card_number:
            if char.isdigit():
                result += masked[digit_idx]
                digit_idx += 1
            else:
                result += char
        return result

    @staticmethod
    def mask_ssn(ssn: str) -> str:
        """
        Mask SSN, showing only last 4 digits.

        Example: 123-45-6789 -> ***-**-6789
        """
        parts = ssn.split("-")
        if len(parts) == 3:
            return "***-**-" + parts[2]
        return "*" * (len(ssn) - 4) + ssn[-4:]

    @staticmethod
    def mask_email(email: str) -> str:
        """
        Mask email, showing only first 2 chars and domain.

        Example: john.doe@example.com -> jo****@example.com
        """
        if "@" not in email:
            return "*" * len(email)

        local, domain = email.split("@", 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[:2] + "*" * (len(local) - 2)

        return f"{masked_local}@{domain}"

    @staticmethod
    def mask_phone(phone: str) -> str:
        """
        Mask phone number, showing only last 4 digits.

        Example: (555) 123-4567 -> (***) ***-4567
        """
        digits = re.sub(r"[^0-9]", "", phone)
        if len(digits) < 10:
            return "*" * len(phone)

        masked = "*" * (len(digits) - 4) + digits[-4:]
        result = ""
        digit_idx = 0
        for char in phone:
            if char.isdigit():
                result += masked[digit_idx]
                digit_idx += 1
            else:
                result += char
        return result

    @staticmethod
    def mask_api_key(api_key: str, reveal: int = 6) -> str:
        """
        Mask API key, showing only first few characters.

        Example: 1234567890abcdef1234567890abcdef -> 123456**************************
        """
        if len(api_key) <= reveal:
            return "*" * len(api_key)
        return api_key[:reveal] + "*" * (len(api_key) - reveal)

    @staticmethod
    def mask_password(password: str) -> str:
        """Completely mask password."""
        return "********"

    @staticmethod
    def mask_generic(value: str, reveal: int = 4) -> str:
        """Generic masking showing first/last characters."""
        if len(value) <= reveal * 2:
            return "*" * len(value)
        return value[:reveal] + "*" * (len(value) - reveal * 2) + value[-reveal:]

    @classmethod
    def mask_data(cls, data: Any, data_type: Optional[DataType] = None) -> Any:
        """
        Mask data based on type.

        Args:
            data: Data to mask
            data_type: Type of sensitive data (auto-detect if None)

        Returns:
            Masked data
        """
        if not isinstance(data, str):
            return data

        if data_type == DataType.CREDIT_CARD:
            return cls.mask_credit_card(data)
        elif data_type == DataType.SSN:
            return cls.mask_ssn(data)
        elif data_type == DataType.EMAIL:
            return cls.mask_email(data)
        elif data_type == DataType.PHONE:
            return cls.mask_phone(data)
        elif data_type == DataType.API_KEY:
            return cls.mask_api_key(data)
        elif data_type == DataType.PASSWORD:
            return cls.mask_password(data)
        else:
            return cls.mask_generic(data)


class SecureLogger:
    """
    Logger that automatically masks sensitive data.
    """

    def __init__(self, logger_name: str, mask_sensitive: bool = True):
        """
        Initialize secure logger.

        Args:
            logger_name: Name for the logger
            mask_sensitive: Enable automatic masking
        """
        self.logger = logging.getLogger(logger_name)
        self.mask_sensitive = mask_sensitive
        self.detector = SensitiveDataDetector()
        self.masker = DataMasker()

    def _sanitize_message(self, message: str) -> str:
        """Sanitize log message by masking sensitive data."""
        if not self.mask_sensitive:
            return message

        # Detect sensitive data
        detected = self.detector.detect(message)

        # Mask each type
        for data_type, values in detected.items():
            for value in values:
                if isinstance(value, tuple):
                    value = value[0]  # Extract from regex groups
                masked = self.masker.mask_data(value, data_type)
                message = message.replace(str(value), masked)

        return message

    def debug(self, message: str, *args, **kwargs):
        """Log debug message with sanitization."""
        message = self._sanitize_message(message)
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        """Log info message with sanitization."""
        message = self._sanitize_message(message)
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        """Log warning message with sanitization."""
        message = self._sanitize_message(message)
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        """Log error message with sanitization."""
        message = self._sanitize_message(message)
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        """Log critical message with sanitization."""
        message = self._sanitize_message(message)
        self.logger.critical(message, *args, **kwargs)


class ResponseSanitizer:
    """
    Sanitize HTTP responses to prevent sensitive data leaks.
    """

    def __init__(self):
        """Initialize response sanitizer."""
        self.detector = SensitiveDataDetector()
        self.masker = DataMasker()

    def sanitize_response(self, response_data: Any) -> Any:
        """
        Sanitize response data.

        Args:
            response_data: Response data (dict, list, str, etc.)

        Returns:
            Sanitized response data
        """
        if isinstance(response_data, dict):
            return self._sanitize_dict(response_data)
        elif isinstance(response_data, list):
            return [self.sanitize_response(item) for item in response_data]
        elif isinstance(response_data, str):
            return self._sanitize_string(response_data)
        else:
            return response_data

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary."""
        sanitized = {}
        sensitive_keys = {"password", "passwd", "pwd", "secret", "token", "api_key", "private_key"}

        for key, value in data.items():
            # Check if key indicates sensitive data
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "********"
            elif isinstance(value, (dict, list)):
                sanitized[key] = self.sanitize_response(value)
            elif isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            else:
                sanitized[key] = value

        return sanitized

    def _sanitize_string(self, text: str) -> str:
        """Sanitize string."""
        # Detect and mask sensitive data
        detected = self.detector.detect(text)

        for data_type, values in detected.items():
            for value in values:
                if isinstance(value, tuple):
                    value = value[0]
                masked = self.masker.mask_data(value, data_type)
                text = text.replace(str(value), masked)

        return text


class MemoryScrubber:
    """
    Scrub sensitive data from memory.

    NOTE: Python's garbage collection makes this difficult, but we try.
    """

    @staticmethod
    def scrub_string(s: str) -> None:
        """
        Attempt to overwrite string in memory.

        Note: In CPython, strings are immutable, so this has limited effect.
        For true memory scrubbing, use ctypes or C extensions.
        """
        try:
            import ctypes

            # Overwrite string memory with zeros
            location = id(s) + 20  # Offset to string data
            size = len(s)
            ctypes.memset(location, 0, size)
        except Exception:
            # If ctypes not available or fails, just delete reference
            pass

    @staticmethod
    def scrub_dict(d: Dict[str, Any], sensitive_keys: Optional[Set[str]] = None) -> None:
        """
        Scrub sensitive data from dictionary.

        Args:
            d: Dictionary to scrub
            sensitive_keys: Set of sensitive key names
        """
        if sensitive_keys is None:
            sensitive_keys = {
                "password",
                "passwd",
                "pwd",
                "secret",
                "token",
                "api_key",
                "private_key",
            }

        for key in list(d.keys()):
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(d[key], str):
                    MemoryScrubber.scrub_string(d[key])
                d[key] = None
                del d[key]


__all__ = [
    "DataType",
    "SensitivePattern",
    "SensitiveDataDetector",
    "DataMasker",
    "SecureLogger",
    "ResponseSanitizer",
    "MemoryScrubber",
]
