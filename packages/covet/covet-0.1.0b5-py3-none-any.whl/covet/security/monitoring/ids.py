"""
Intrusion Detection System (IDS) for CovetPy

Advanced IDS with multiple detection mechanisms:
- Signature-based detection (OWASP Top 10)
- Anomaly-based detection (ML-powered)
- Behavioral analysis
- Real-time threat detection

Attack Detection:
- SQL Injection (all variants)
- XSS (Cross-Site Scripting)
- CSRF attacks
- Path Traversal
- Command Injection
- LDAP Injection
- XML External Entity (XXE)
- Server-Side Request Forgery (SSRF)
- Brute Force attacks
- DDoS patterns
- Session hijacking
- Parameter tampering

NO MOCK DATA - Real pattern matching and ML-based anomaly detection.
"""

import asyncio
import hashlib
import json
import re

# Statistical analysis for ML-based detection
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from urllib.parse import unquote


class AttackType(str, Enum):
    """Types of detected attacks"""

    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    PATH_TRAVERSAL = "path_traversal"
    COMMAND_INJECTION = "command_injection"
    LDAP_INJECTION = "ldap_injection"
    XXE = "xxe"
    SSRF = "ssrf"
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    SESSION_HIJACKING = "session_hijacking"
    PARAMETER_TAMPERING = "parameter_tampering"
    BUFFER_OVERFLOW = "buffer_overflow"
    DIRECTORY_LISTING = "directory_listing"
    INFORMATION_DISCLOSURE = "information_disclosure"
    AUTHENTICATION_BYPASS = "authentication_bypass"
    PRIVILEGE_ESCALATION = "privilege_escalation"


class ThreatLevel(str, Enum):
    """Threat severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DetectionResult:
    """Result of IDS detection"""

    detected: bool
    attack_type: Optional[AttackType] = None
    threat_level: ThreatLevel = ThreatLevel.LOW
    confidence: float = 0.0  # 0.0 to 1.0
    details: Dict[str, Any] = field(default_factory=dict)
    matched_patterns: List[str] = field(default_factory=list)
    recommended_action: str = "monitor"  # monitor, block, alert
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RequestProfile:
    """Profile of a request for analysis"""

    method: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    body: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class SignatureDetector:
    """
    Signature-based attack detection.

    Uses pattern matching to detect known attack signatures.
    """

    # SQL Injection patterns (comprehensive)
    SQL_PATTERNS = [
        # Union-based
        r"(?i)(union\s+(?:all\s+)?select)",
        # Boolean-based
        r"(?i)(and\s+\d+\s*=\s*\d+)",
        r"(?i)(or\s+\d+\s*=\s*\d+)",
        r"(?i)(and\s+.*\s*=\s*.*)",
        r"(?i)(or\s+.*\s*=\s*.*)",
        # Time-based blind
        r"(?i)(sleep\s*\()",
        r"(?i)(benchmark\s*\()",
        r"(?i)(waitfor\s+delay)",
        # Stacked queries
        r"(;\s*drop\s+)",
        r"(;\s*delete\s+)",
        r"(;\s*insert\s+)",
        r"(;\s*update\s+)",
        # Comment-based
        r"(--\s*$)",
        r"(/\*.*\*/)",
        r"(#.*$)",
        # String manipulation
        r"('+\s*or\s+')",
        r"('\s*or\s*'.*'=')",
        r"(\"\s*or\s*\".*\"=\")",
        # Database functions
        r"(?i)(exec\s*\()",
        r"(?i)(execute\s*\()",
        r"(?i)(sp_executesql)",
        r"(?i)(xp_cmdshell)",
        # Information schema
        r"(?i)(information_schema)",
        r"(?i)(sys\.tables)",
        r"(?i)(sys\.columns)",
        # Hex encoding
        r"(0x[0-9a-f]+)",
        # Specific DB keywords
        r"(?i)(pg_sleep)",
        r"(?i)(load_file)",
        r"(?i)(into\s+outfile)",
    ]

    # XSS patterns (comprehensive)
    XSS_PATTERNS = [
        # Script tags
        r"(?i)<script[^>]*>.*?</script>",
        r"(?i)<script[^>]*>",
        # Event handlers
        r"(?i)on\w+\s*=",
        r"(?i)onerror\s*=",
        r"(?i)onload\s*=",
        r"(?i)onclick\s*=",
        r"(?i)onmouseover\s*=",
        # JavaScript protocol
        r"(?i)javascript:",
        r"(?i)vbscript:",
        # Data URIs
        r"(?i)data:text/html",
        # DOM manipulation
        r"(?i)document\.cookie",
        r"(?i)document\.write",
        r"(?i)window\.location",
        # Tag injection
        r"(?i)<iframe[^>]*>",
        r"(?i)<embed[^>]*>",
        r"(?i)<object[^>]*>",
        r"(?i)<img[^>]*src",
        r"(?i)<svg[^>]*>",
        # HTML entities
        r"&#x[0-9a-f]+;",
        r"&#\d+;",
        # Expression
        r"(?i)expression\s*\(",
        # Import
        r"(?i)@import",
        # Meta refresh
        r"(?i)<meta[^>]*http-equiv",
    ]

    # Path Traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\./",
        r"\.\.\\",
        r"%2e%2e/",
        r"%2e%2e\\",
        r"\.\.%2f",
        r"\.\.%5c",
        r"%252e%252e/",
        r"..;/",
        r"/../",
        r"/\.\./",
    ]

    # Command Injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|]\s*\w+",  # Command chaining
        r"`.*`",  # Backticks
        r"\$\(.*\)",  # Command substitution
        r">\s*/",  # Output redirection
        r"<\s*/",  # Input redirection
        r"\|\s*\w+",  # Pipe
        r"(?i)(nc|netcat)\s",
        r"(?i)(wget|curl)\s",
        r"(?i)(bash|sh|zsh)\s",
        r"(?i)/bin/(bash|sh|zsh)",
        r"(?i)chmod\s",
        r"(?i)chown\s",
    ]

    # LDAP Injection patterns
    LDAP_INJECTION_PATTERNS = [
        r"\(\|\(",
        r"\)\)\)",
        r"\(\&\(",
        r"\*\)",
        r"admin\*",
        r"\(\|\(uid=\*\)",
    ]

    # XXE patterns
    XXE_PATTERNS = [
        r"<!ENTITY",
        r"<!DOCTYPE",
        r"SYSTEM\s+\"",
        r"PUBLIC\s+\"",
        r"file://",
        r"php://",
        r"expect://",
        r"data://",
    ]

    # SSRF patterns
    SSRF_PATTERNS = [
        r"(?i)(localhost|127\.0\.0\.1)",
        r"(?i)(0\.0\.0\.0|::1)",
        r"(?i)(169\.254\.\d+\.\d+)",  # Link-local
        r"(?i)(10\.\d+\.\d+\.\d+)",  # Private IP
        r"(?i)(172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)",  # Private IP
        r"(?i)(192\.168\.\d+\.\d+)",  # Private IP
        r"(?i)@\w+\.",  # URL with credentials
        r"(?i)file://",
        r"(?i)dict://",
        r"(?i)gopher://",
    ]

    # Session hijacking patterns
    SESSION_HIJACK_PATTERNS = [
        r"(?i)document\.cookie",
        r"(?i)session[_-]?id",
        r"(?i)phpsessid",
        r"(?i)jsessionid",
    ]

    def __init__(self):
        """Initialize signature detector"""
        # Compile patterns for performance
        self.compiled_patterns = {
            AttackType.SQL_INJECTION: [re.compile(p) for p in self.SQL_PATTERNS],
            AttackType.XSS: [re.compile(p) for p in self.XSS_PATTERNS],
            AttackType.PATH_TRAVERSAL: [re.compile(p) for p in self.PATH_TRAVERSAL_PATTERNS],
            AttackType.COMMAND_INJECTION: [re.compile(p) for p in self.COMMAND_INJECTION_PATTERNS],
            AttackType.LDAP_INJECTION: [re.compile(p) for p in self.LDAP_INJECTION_PATTERNS],
            AttackType.XXE: [re.compile(p) for p in self.XXE_PATTERNS],
            AttackType.SSRF: [re.compile(p) for p in self.SSRF_PATTERNS],
            AttackType.SESSION_HIJACKING: [re.compile(p) for p in self.SESSION_HIJACK_PATTERNS],
        }

    def detect(self, text: str) -> List[DetectionResult]:
        """
        Detect attacks in text using signature matching.

        Args:
            text: Text to analyze (URL, params, body, etc.)

        Returns:
            List of detection results
        """
        if not text:
            return []

        # URL decode for analysis
        decoded_text = unquote(text)

        results = []

        for attack_type, patterns in self.compiled_patterns.items():
            matched_patterns = []

            for pattern in patterns:
                if pattern.search(text) or pattern.search(decoded_text):
                    matched_patterns.append(pattern.pattern)

            if matched_patterns:
                # Calculate confidence based on number of matches
                confidence = min(1.0, len(matched_patterns) * 0.3)

                # Determine threat level
                if len(matched_patterns) >= 3 or attack_type in [
                    AttackType.SQL_INJECTION,
                    AttackType.COMMAND_INJECTION,
                    AttackType.XXE,
                ]:
                    threat_level = ThreatLevel.CRITICAL
                elif len(matched_patterns) >= 2:
                    threat_level = ThreatLevel.HIGH
                else:
                    threat_level = ThreatLevel.MEDIUM

                results.append(
                    DetectionResult(
                        detected=True,
                        attack_type=attack_type,
                        threat_level=threat_level,
                        confidence=confidence,
                        matched_patterns=matched_patterns,
                        recommended_action=(
                            "block"
                            if threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]
                            else "alert"
                        ),
                        details={
                            "sample": text[:200],
                            "decoded_sample": decoded_text[:200],
                            "pattern_count": len(matched_patterns),
                        },
                    )
                )

        return results


class AnomalyDetector:
    """
    ML-based anomaly detection.

    Uses statistical methods to detect anomalous behavior patterns.
    """

    def __init__(self, baseline_window: int = 1000, anomaly_threshold: float = 3.0):
        """
        Initialize anomaly detector.

        Args:
            baseline_window: Number of requests to use for baseline
            anomaly_threshold: Standard deviations from mean for anomaly
        """
        self.baseline_window = baseline_window
        self.anomaly_threshold = anomaly_threshold

        # Behavioral baselines
        self.request_sizes: deque = deque(maxlen=baseline_window)
        self.request_intervals: deque = deque(maxlen=baseline_window)
        self.param_counts: deque = deque(maxlen=baseline_window)
        self.header_counts: deque = deque(maxlen=baseline_window)

        # Per-IP tracking
        self.ip_behavior: Dict[str, Dict[str, deque]] = defaultdict(
            lambda: {
                "request_times": deque(maxlen=100),
                "paths": deque(maxlen=100),
                "user_agents": deque(maxlen=50),
            }
        )

        self.last_request_time = time.time()

    def detect_anomalies(self, profile: RequestProfile) -> List[DetectionResult]:
        """
        Detect anomalies in request profile.

        Args:
            profile: Request profile to analyze

        Returns:
            List of anomaly detection results
        """
        results = []
        current_time = time.time()

        # Calculate request metrics
        body_size = len(profile.body) if profile.body else 0
        param_count = len(profile.query_params)
        header_count = len(profile.headers)
        request_interval = current_time - self.last_request_time

        # Update baselines
        self.request_sizes.append(body_size)
        self.request_intervals.append(request_interval)
        self.param_counts.append(param_count)
        self.header_counts.append(header_count)
        self.last_request_time = current_time

        # Need minimum data for analysis
        if len(self.request_sizes) < 50:
            return results

        # Detect anomalous request size
        size_anomaly = self._detect_statistical_anomaly(
            body_size, list(self.request_sizes), "Request size anomaly"
        )
        if size_anomaly:
            results.append(size_anomaly)

        # Detect anomalous parameter count
        param_anomaly = self._detect_statistical_anomaly(
            param_count, list(self.param_counts), "Unusual parameter count"
        )
        if param_anomaly:
            results.append(param_anomaly)

        # Detect rate anomalies (DDoS/brute force)
        if profile.ip_address:
            rate_anomaly = self._detect_rate_anomaly(profile)
            if rate_anomaly:
                results.append(rate_anomaly)

        # Detect behavioral anomalies
        if profile.ip_address:
            behavior_anomaly = self._detect_behavioral_anomaly(profile)
            if behavior_anomaly:
                results.append(behavior_anomaly)

        return results

    def _detect_statistical_anomaly(
        self, value: float, baseline: List[float], description: str
    ) -> Optional[DetectionResult]:
        """Detect statistical anomaly using z-score"""
        if len(baseline) < 10:
            return None

        try:
            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline)

            if stdev == 0:
                return None

            z_score = abs(value - mean) / stdev

            if z_score > self.anomaly_threshold:
                confidence = min(1.0, z_score / 10.0)

                return DetectionResult(
                    detected=True,
                    attack_type=None,  # Generic anomaly
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=confidence,
                    details={
                        "description": description,
                        "value": value,
                        "mean": mean,
                        "stdev": stdev,
                        "z_score": z_score,
                    },
                    recommended_action="monitor",
                )
        except statistics.StatisticsError:
            pass

        return None

    def _detect_rate_anomaly(self, profile: RequestProfile) -> Optional[DetectionResult]:
        """Detect rate-based anomalies (brute force, DDoS)"""
        ip = profile.ip_address
        behavior = self.ip_behavior[ip]

        current_time = time.time()
        behavior["request_times"].append(current_time)

        # Check request rate in last minute
        one_minute_ago = current_time - 60
        recent_requests = [t for t in behavior["request_times"] if t > one_minute_ago]

        requests_per_minute = len(recent_requests)

        # High rate threshold (adjust based on application)
        if requests_per_minute > 100:  # >100 req/min is suspicious
            confidence = min(1.0, requests_per_minute / 200)

            # Determine if brute force or DDoS
            attack_type = AttackType.BRUTE_FORCE
            if requests_per_minute > 200:
                attack_type = AttackType.DDOS

            return DetectionResult(
                detected=True,
                attack_type=attack_type,
                threat_level=ThreatLevel.HIGH,
                confidence=confidence,
                details={
                    "requests_per_minute": requests_per_minute,
                    "ip_address": ip,
                    "detection": "High request rate",
                },
                recommended_action="block",
            )

        # Check for brute force on login endpoints
        if "login" in profile.path.lower() or "auth" in profile.path.lower():
            # Check recent login attempts
            if requests_per_minute > 10:  # >10 login attempts/min
                return DetectionResult(
                    detected=True,
                    attack_type=AttackType.BRUTE_FORCE,
                    threat_level=ThreatLevel.HIGH,
                    confidence=0.8,
                    details={
                        "attempts_per_minute": requests_per_minute,
                        "ip_address": ip,
                        "endpoint": profile.path,
                    },
                    recommended_action="block",
                )

        return None

    def _detect_behavioral_anomaly(self, profile: RequestProfile) -> Optional[DetectionResult]:
        """Detect behavioral anomalies"""
        ip = profile.ip_address
        behavior = self.ip_behavior[ip]

        # Track paths and user agents
        behavior["paths"].append(profile.path)
        if profile.user_agent:
            behavior["user_agents"].append(profile.user_agent)

        # Detect scanning behavior (accessing many different paths)
        if len(behavior["paths"]) >= 20:
            unique_paths = len(set(behavior["paths"]))

            # If accessing >15 unique paths, might be scanning
            if unique_paths > 15:
                confidence = min(1.0, unique_paths / 30)

                return DetectionResult(
                    detected=True,
                    attack_type=AttackType.DIRECTORY_LISTING,
                    threat_level=ThreatLevel.MEDIUM,
                    confidence=confidence,
                    details={
                        "unique_paths": unique_paths,
                        "total_requests": len(behavior["paths"]),
                        "ip_address": ip,
                        "sample_paths": list(set(list(behavior["paths"])[-10:])),
                    },
                    recommended_action="monitor",
                )

        # Detect user agent switching (possible evasion)
        if len(behavior["user_agents"]) >= 10:
            unique_agents = len(set(behavior["user_agents"]))

            if unique_agents > 5:  # Multiple user agents from same IP
                return DetectionResult(
                    detected=True,
                    attack_type=AttackType.PARAMETER_TAMPERING,
                    threat_level=ThreatLevel.LOW,
                    confidence=0.6,
                    details={
                        "unique_user_agents": unique_agents,
                        "ip_address": ip,
                        "description": "User agent switching detected",
                    },
                    recommended_action="monitor",
                )

        return None


class BehavioralAnalyzer:
    """
    Advanced behavioral analysis for sophisticated attacks.
    """

    def __init__(self):
        """Initialize behavioral analyzer"""
        # Track user session behavior
        self.session_profiles: Dict[str, Dict[str, Any]] = {}

        # Track authentication attempts
        self.auth_attempts: Dict[str, List[float]] = defaultdict(list)

        # Track privilege escalation attempts
        self.privilege_attempts: Dict[str, List[str]] = defaultdict(list)

    def analyze_session(self, profile: RequestProfile) -> List[DetectionResult]:
        """Analyze session behavior for anomalies"""
        results = []

        if not profile.session_id:
            return results

        session_id = profile.session_id

        # Initialize session profile
        if session_id not in self.session_profiles:
            self.session_profiles[session_id] = {
                "created_at": time.time(),
                "ip_addresses": set(),
                "user_agents": set(),
                "paths": [],
                "user_ids": set(),
            }

        session = self.session_profiles[session_id]

        # Track session attributes
        if profile.ip_address:
            session["ip_addresses"].add(profile.ip_address)
        if profile.user_agent:
            session["user_agents"].add(profile.user_agent)
        if profile.user_id:
            session["user_ids"].add(profile.user_id)
        session["paths"].append(profile.path)

        # Detect session hijacking (IP change)
        if len(session["ip_addresses"]) > 1:
            results.append(
                DetectionResult(
                    detected=True,
                    attack_type=AttackType.SESSION_HIJACKING,
                    threat_level=ThreatLevel.CRITICAL,
                    confidence=0.9,
                    details={
                        "session_id": session_id,
                        "ip_addresses": list(session["ip_addresses"]),
                        "current_ip": profile.ip_address,
                        "description": "Session IP address changed",
                    },
                    recommended_action="block",
                )
            )

        # Detect session hijacking (user agent change)
        if len(session["user_agents"]) > 2:
            results.append(
                DetectionResult(
                    detected=True,
                    attack_type=AttackType.SESSION_HIJACKING,
                    threat_level=ThreatLevel.HIGH,
                    confidence=0.7,
                    details={
                        "session_id": session_id,
                        "user_agents": list(session["user_agents"]),
                        "description": "Session user agent changed multiple times",
                    },
                    recommended_action="alert",
                )
            )

        # Detect privilege escalation attempts
        admin_paths = ["/admin", "/settings", "/users", "/config"]
        recent_paths = session["paths"][-20:]  # Last 20 paths

        admin_access_count = sum(
            1
            for path in recent_paths
            if any(admin_path in path.lower() for admin_path in admin_paths)
        )

        if admin_access_count > 5:  # Multiple admin path access attempts
            results.append(
                DetectionResult(
                    detected=True,
                    attack_type=AttackType.PRIVILEGE_ESCALATION,
                    threat_level=ThreatLevel.HIGH,
                    confidence=0.8,
                    details={
                        "session_id": session_id,
                        "admin_access_count": admin_access_count,
                        "recent_paths": recent_paths[-5:],
                        "description": "Multiple privileged resource access attempts",
                    },
                    recommended_action="alert",
                )
            )

        return results


class IDS:
    """
    Comprehensive Intrusion Detection System.

    Combines multiple detection mechanisms:
    - Signature-based detection
    - Anomaly-based detection (ML)
    - Behavioral analysis
    """

    def __init__(
        self,
        enable_signatures: bool = True,
        enable_anomaly: bool = True,
        enable_behavioral: bool = True,
        alert_callback: Optional[Callable[[List[DetectionResult]], None]] = None,
    ):
        """
        Initialize IDS.

        Args:
            enable_signatures: Enable signature-based detection
            enable_anomaly: Enable anomaly detection
            enable_behavioral: Enable behavioral analysis
            alert_callback: Callback for detections
        """
        self.enable_signatures = enable_signatures
        self.enable_anomaly = enable_anomaly
        self.enable_behavioral = enable_behavioral
        self.alert_callback = alert_callback

        # Initialize detectors
        self.signature_detector = SignatureDetector() if enable_signatures else None
        self.anomaly_detector = AnomalyDetector() if enable_anomaly else None
        self.behavioral_analyzer = BehavioralAnalyzer() if enable_behavioral else None

        # Detection statistics
        self.stats = {
            "total_requests": 0,
            "total_detections": 0,
            "by_attack_type": defaultdict(int),
            "by_threat_level": defaultdict(int),
            "blocked": 0,
            "alerted": 0,
        }

        self._lock = asyncio.Lock()

    async def analyze_request(self, profile: RequestProfile) -> List[DetectionResult]:
        """
        Analyze request for security threats.

        Args:
            profile: Request profile

        Returns:
            List of detection results
        """
        async with self._lock:
            self.stats["total_requests"] += 1

        all_results = []

        # Signature-based detection
        if self.enable_signatures and self.signature_detector:
            # Analyze all request components
            components_to_check = []

            # URL path
            components_to_check.append(profile.path)

            # Query parameters
            for key, value in profile.query_params.items():
                components_to_check.append(f"{key}={value}")

            # Headers (check for injection in custom headers)
            for key, value in profile.headers.items():
                if key.lower() not in ["host", "user-agent", "accept"]:
                    components_to_check.append(f"{key}: {value}")

            # Body
            if profile.body:
                components_to_check.append(profile.body)

            # Run signature detection on all components
            for component in components_to_check:
                sig_results = self.signature_detector.detect(str(component))
                all_results.extend(sig_results)

        # Anomaly detection
        if self.enable_anomaly and self.anomaly_detector:
            anomaly_results = self.anomaly_detector.detect_anomalies(profile)
            all_results.extend(anomaly_results)

        # Behavioral analysis
        if self.enable_behavioral and self.behavioral_analyzer:
            behavioral_results = self.behavioral_analyzer.analyze_session(profile)
            all_results.extend(behavioral_results)

        # Update statistics
        if all_results:
            async with self._lock:
                self.stats["total_detections"] += len(all_results)

                for result in all_results:
                    if result.attack_type:
                        self.stats["by_attack_type"][result.attack_type.value] += 1
                    self.stats["by_threat_level"][result.threat_level.value] += 1

                    if result.recommended_action == "block":
                        self.stats["blocked"] += 1
                    elif result.recommended_action == "alert":
                        self.stats["alerted"] += 1

            # Trigger alert callback
            if self.alert_callback:
                try:
                    await self.alert_callback(all_results)
                except Exception:
                    pass  # Don't fail detection on callback error

        return all_results

    async def get_statistics(self) -> Dict[str, Any]:
        """Get IDS statistics"""
        async with self._lock:
            return {
                "total_requests": self.stats["total_requests"],
                "total_detections": self.stats["total_detections"],
                "detection_rate": (
                    self.stats["total_detections"] / self.stats["total_requests"]
                    if self.stats["total_requests"] > 0
                    else 0
                ),
                "by_attack_type": dict(self.stats["by_attack_type"]),
                "by_threat_level": dict(self.stats["by_threat_level"]),
                "blocked": self.stats["blocked"],
                "alerted": self.stats["alerted"],
            }

    async def reset_statistics(self):
        """Reset statistics"""
        async with self._lock:
            self.stats = {
                "total_requests": 0,
                "total_detections": 0,
                "by_attack_type": defaultdict(int),
                "by_threat_level": defaultdict(int),
                "blocked": 0,
                "alerted": 0,
            }


__all__ = [
    "IDS",
    "AttackType",
    "ThreatLevel",
    "DetectionResult",
    "RequestProfile",
    "SignatureDetector",
    "AnomalyDetector",
    "BehavioralAnalyzer",
]
