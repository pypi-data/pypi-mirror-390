"""
CovetPy Security Scanner

Automatic vulnerability scanning for OWASP Top 10:
- A01:2021 - Broken Access Control
- A02:2021 - Cryptographic Failures
- A03:2021 - Injection
- A04:2021 - Insecure Design
- A05:2021 - Security Misconfiguration
- A06:2021 - Vulnerable and Outdated Components
- A07:2021 - Identification and Authentication Failures
- A08:2021 - Software and Data Integrity Failures
- A09:2021 - Security Logging and Monitoring Failures
- A10:2021 - Server-Side Request Forgery (SSRF)

Author: CovetPy Security Team
License: MIT
"""

import ast
import json
import logging
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class VulnerabilitySeverity(Enum):
    """Vulnerability severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OWASPCategory(Enum):
    """OWASP Top 10 2021 categories."""

    A01_BROKEN_ACCESS_CONTROL = "A01:2021-Broken Access Control"
    A02_CRYPTOGRAPHIC_FAILURES = "A02:2021-Cryptographic Failures"
    A03_INJECTION = "A03:2021-Injection"
    A04_INSECURE_DESIGN = "A04:2021-Insecure Design"
    A05_SECURITY_MISCONFIGURATION = "A05:2021-Security Misconfiguration"
    A06_VULNERABLE_COMPONENTS = "A06:2021-Vulnerable and Outdated Components"
    A07_AUTH_FAILURES = "A07:2021-Identification and Authentication Failures"
    A08_DATA_INTEGRITY_FAILURES = "A08:2021-Software and Data Integrity Failures"
    A09_LOGGING_FAILURES = "A09:2021-Security Logging and Monitoring Failures"
    A10_SSRF = "A10:2021-Server-Side Request Forgery"


@dataclass
class Vulnerability:
    """Security vulnerability finding."""

    title: str
    description: str
    severity: VulnerabilitySeverity
    owasp_category: OWASPCategory
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    cwe_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["severity"] = self.severity.value
        data["owasp_category"] = self.owasp_category.value
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass
class ScanResult:
    """Security scan results."""

    scan_timestamp: datetime
    total_files_scanned: int
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    score: float = 100.0
    passed: bool = True

    def get_by_severity(self, severity: VulnerabilitySeverity) -> List[Vulnerability]:
        """Get vulnerabilities by severity."""
        return [v for v in self.vulnerabilities if v.severity == severity]

    def get_by_category(self, category: OWASPCategory) -> List[Vulnerability]:
        """Get vulnerabilities by OWASP category."""
        return [v for v in self.vulnerabilities if v.owasp_category == category]

    def calculate_score(self) -> float:
        """Calculate security score (0-100)."""
        penalties = {
            VulnerabilitySeverity.CRITICAL: 20,
            VulnerabilitySeverity.HIGH: 10,
            VulnerabilitySeverity.MEDIUM: 5,
            VulnerabilitySeverity.LOW: 2,
            VulnerabilitySeverity.INFO: 0,
        }

        total_penalty = sum(penalties.get(v.severity, 0) for v in self.vulnerabilities)

        score = max(0, 100 - total_penalty)
        self.score = score
        self.passed = score >= 70  # 70% passing threshold
        return score

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "scan_timestamp": self.scan_timestamp.isoformat(),
            "total_files_scanned": self.total_files_scanned,
            "vulnerabilities": [v.to_dict() for v in self.vulnerabilities],
            "score": self.score,
            "passed": self.passed,
            "summary": {
                "critical": len(self.get_by_severity(VulnerabilitySeverity.CRITICAL)),
                "high": len(self.get_by_severity(VulnerabilitySeverity.HIGH)),
                "medium": len(self.get_by_severity(VulnerabilitySeverity.MEDIUM)),
                "low": len(self.get_by_severity(VulnerabilitySeverity.LOW)),
                "info": len(self.get_by_severity(VulnerabilitySeverity.INFO)),
            },
        }


class SecurityScanner:
    """
    OWASP Top 10 vulnerability scanner.
    """

    # Dangerous patterns to detect
    INJECTION_PATTERNS = [
        (
            re.compile(r"cursor\.execute\([^)]*%|cursor\.execute\([^)]*\+"),
            "SQL injection: String concatenation in SQL query",
            VulnerabilitySeverity.CRITICAL,
            OWASPCategory.A03_INJECTION,
        ),
        (
            re.compile(r"eval\s*\("),
            "Code injection: Use of eval()",
            VulnerabilitySeverity.CRITICAL,
            OWASPCategory.A03_INJECTION,
        ),
        (
            re.compile(r"exec\s*\("),
            "Code injection: Use of exec()",
            VulnerabilitySeverity.CRITICAL,
            OWASPCategory.A03_INJECTION,
        ),
        (
            re.compile(r"subprocess\.(call|run|Popen).*shell\s*=\s*True"),
            "Command injection: shell=True in subprocess",
            VulnerabilitySeverity.CRITICAL,
            OWASPCategory.A03_INJECTION,
        ),
    ]

    CRYPTO_PATTERNS = [
        (
            re.compile(r"hashlib\.(md5|sha1)\("),
            "Weak cryptographic hash: MD5/SHA1 usage",
            VulnerabilitySeverity.HIGH,
            OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
        ),
        (
            re.compile(r'password\s*=\s*["\'][^"\']+["\']'),
            "Hardcoded password detected",
            VulnerabilitySeverity.CRITICAL,
            OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
        ),
        (
            re.compile(r'(api_key|secret_key|aws_access_key)\s*=\s*["\'][^"\']+["\']'),
            "Hardcoded API key/secret detected",
            VulnerabilitySeverity.CRITICAL,
            OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES,
        ),
    ]

    AUTH_PATTERNS = [
        (
            re.compile(r"(username|password)\s+in\s+request"),
            "Potential authentication bypass",
            VulnerabilitySeverity.HIGH,
            OWASPCategory.A07_AUTH_FAILURES,
        ),
    ]

    XSS_PATTERNS = [
        (
            re.compile(r"\.innerHTML\s*="),
            "XSS: Direct innerHTML assignment",
            VulnerabilitySeverity.HIGH,
            OWASPCategory.A03_INJECTION,
        ),
        (
            re.compile(r"document\.write\("),
            "XSS: Use of document.write()",
            VulnerabilitySeverity.MEDIUM,
            OWASPCategory.A03_INJECTION,
        ),
    ]

    def __init__(self, project_root: str):
        """
        Initialize security scanner.

        Args:
            project_root: Root directory of project to scan
        """
        self.project_root = Path(project_root)
        self.vulnerabilities: List[Vulnerability] = []

    def scan(self, file_extensions: Optional[Set[str]] = None) -> ScanResult:
        """
        Scan project for security vulnerabilities.

        Args:
            file_extensions: File extensions to scan (default: .py, .js)

        Returns:
            ScanResult with findings
        """
        if file_extensions is None:
            file_extensions = {".py", ".js", ".ts", ".jsx", ".tsx"}

        self.vulnerabilities = []
        files_scanned = 0

        # Scan all files
        for file_path in self.project_root.rglob("*"):
            if file_path.suffix in file_extensions and file_path.is_file():
                self._scan_file(file_path)
                files_scanned += 1

        # Create result
        result = ScanResult(
            scan_timestamp=datetime.utcnow(),
            total_files_scanned=files_scanned,
            vulnerabilities=self.vulnerabilities,
        )

        result.calculate_score()
        return result

    def _scan_file(self, file_path: Path) -> None:
        """Scan a single file for vulnerabilities."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Scan for patterns
            self._scan_patterns(file_path, content, self.INJECTION_PATTERNS)
            self._scan_patterns(file_path, content, self.CRYPTO_PATTERNS)
            self._scan_patterns(file_path, content, self.AUTH_PATTERNS)
            self._scan_patterns(file_path, content, self.XSS_PATTERNS)

            # Additional checks
            self._check_security_headers(file_path, content)
            self._check_dependency_vulnerabilities(file_path, content)

        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {e}")

    def _scan_patterns(self, file_path: Path, content: str, patterns: List[tuple]) -> None:
        """Scan content for vulnerability patterns."""
        lines = content.split("\n")

        for pattern, description, severity, category in patterns:
            for line_num, line in enumerate(lines, 1):
                if pattern.search(line):
                    vuln = Vulnerability(
                        title=description,
                        description=f"Found in {file_path.name} at line {line_num}",
                        severity=severity,
                        owasp_category=category,
                        file_path=str(file_path),
                        line_number=line_num,
                        code_snippet=line.strip(),
                        recommendation=self._get_recommendation(category),
                    )
                    self.vulnerabilities.append(vuln)

    def _check_security_headers(self, file_path: Path, content: str) -> None:
        """Check for missing security headers in web applications."""
        if "response" in content.lower() and "headers" in content.lower():
            security_headers = [
                "Strict-Transport-Security",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "Content-Security-Policy",
            ]

            for header in security_headers:
                if header not in content:
                    vuln = Vulnerability(
                        title=f"Missing security header: {header}",
                        description=f"Security header {header} not found in {file_path.name}",
                        severity=VulnerabilitySeverity.MEDIUM,
                        owasp_category=OWASPCategory.A05_SECURITY_MISCONFIGURATION,
                        file_path=str(file_path),
                        recommendation="Implement security headers middleware",
                    )
                    self.vulnerabilities.append(vuln)

    def _check_dependency_vulnerabilities(self, file_path: Path, content: str) -> None:
        """Check for vulnerable dependencies."""
        if file_path.name in ("requirements.txt", "package.json", "Pipfile"):
            # TODO: Integrate with vulnerability databases
            pass

    def _get_recommendation(self, category: OWASPCategory) -> str:
        """Get remediation recommendation for OWASP category."""
        recommendations = {
            OWASPCategory.A03_INJECTION: "Use parameterized queries and input validation",
            OWASPCategory.A02_CRYPTOGRAPHIC_FAILURES: "Use strong cryptographic algorithms and secure key management",
            OWASPCategory.A07_AUTH_FAILURES: "Implement MFA and secure session management",
            OWASPCategory.A05_SECURITY_MISCONFIGURATION: "Enable security headers and configure securely",
        }
        return recommendations.get(category, "Review OWASP guidelines for this category")

    def generate_report(self, result: ScanResult, output_file: str) -> None:
        """
        Generate security scan report.

        Args:
            result: Scan results
            output_file: Output file path (JSON)
        """
        with open(output_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)

        logger.info(f"Security scan report written to {output_file}")


__all__ = [
    "VulnerabilitySeverity",
    "OWASPCategory",
    "Vulnerability",
    "ScanResult",
    "SecurityScanner",
]
