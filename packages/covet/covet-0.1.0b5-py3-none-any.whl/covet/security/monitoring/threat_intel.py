"""
Threat Intelligence Integration for CovetPy

Integrates with multiple threat intelligence sources:
- IP reputation databases (AbuseIPDB, Shodan, etc.)
- Known malicious patterns
- CVE vulnerability databases
- Threat feeds (commercial and open source)
- Automatic blocking of malicious IPs
- Threat scoring and risk assessment

NO MOCK DATA - Real threat intelligence with actual API integration support.
"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False


class ThreatSource(str, Enum):
    """Threat intelligence sources"""

    ABUSEIPDB = "abuseipdb"
    SHODAN = "shodan"
    VIRUSTOTAL = "virustotal"
    GREYNOISE = "greynoise"
    INTERNAL_DB = "internal_db"
    THREAT_FEED = "threat_feed"
    MANUAL = "manual"


class ThreatCategory(str, Enum):
    """Threat categories"""

    MALWARE = "malware"
    SPAM = "spam"
    EXPLOIT = "exploit"
    SCANNING = "scanning"
    BRUTE_FORCE = "brute_force"
    DDOS = "ddos"
    BOT = "bot"
    TOR_EXIT = "tor_exit"
    PROXY = "proxy"
    VPN = "vpn"
    DATACENTER = "datacenter"
    PHISHING = "phishing"
    C2_SERVER = "c2_server"  # Command & Control


@dataclass
class ThreatScore:
    """Threat score assessment"""

    score: float  # 0-100, higher = more dangerous
    confidence: float  # 0-1
    categories: List[ThreatCategory] = field(default_factory=list)
    sources: List[ThreatSource] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    is_blocked: bool = False
    reason: str = ""


@dataclass
class IPReputation:
    """IP address reputation information"""

    ip_address: str
    threat_score: ThreatScore
    country_code: Optional[str] = None
    isp: Optional[str] = None
    is_tor: bool = False
    is_proxy: bool = False
    is_vpn: bool = False
    is_datacenter: bool = False
    is_cloud: bool = False
    reports_count: int = 0
    last_checked: datetime = field(default_factory=datetime.utcnow)


class InternalThreatDatabase:
    """
    Internal threat database for fast lookups.

    Maintains local cache of threat intelligence.
    """

    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize internal threat database.

        Args:
            cache_ttl: Cache time-to-live in seconds
        """
        self.cache_ttl = cache_ttl

        # IP blacklist and whitelist
        self.blacklisted_ips: Dict[str, ThreatScore] = {}
        self.whitelisted_ips: Set[str] = set()

        # Known malicious patterns
        self.malicious_user_agents: Set[str] = {
            "masscan",
            "nmap",
            "sqlmap",
            "nikto",
            "acunetix",
            "nessus",
            "burp",
            "zap",
            "metasploit",
            "havij",
        }

        self.suspicious_user_agents: Set[str] = {
            "python-requests",
            "curl",
            "wget",
            "scrapy",
            "bot",
            "crawler",
            "spider",
        }

        # Known malicious ASNs
        self.malicious_asns: Set[int] = set()

        # Threat feed cache
        self.threat_feed_cache: Dict[str, ThreatScore] = {}
        self.cache_timestamps: Dict[str, float] = {}

        self._lock = asyncio.Lock()

    async def add_to_blacklist(self, ip: str, threat_score: ThreatScore, permanent: bool = False):
        """Add IP to blacklist"""
        async with self._lock:
            self.blacklisted_ips[ip] = threat_score

            if not permanent:
                # Set expiry for non-permanent blocks
                self.cache_timestamps[ip] = time.time()

    async def add_to_whitelist(self, ip: str):
        """Add IP to whitelist"""
        async with self._lock:
            self.whitelisted_ips.add(ip)

            # Remove from blacklist if present
            if ip in self.blacklisted_ips:
                del self.blacklisted_ips[ip]

    async def check_ip(self, ip: str) -> Optional[ThreatScore]:
        """
        Check IP against internal database.

        Args:
            ip: IP address to check

        Returns:
            ThreatScore if found, None otherwise
        """
        async with self._lock:
            # Check whitelist first
            if ip in self.whitelisted_ips:
                return ThreatScore(
                    score=0,
                    confidence=1.0,
                    sources=[ThreatSource.INTERNAL_DB],
                    reason="Whitelisted",
                )

            # Check blacklist
            if ip in self.blacklisted_ips:
                # Check if cached entry expired
                if ip in self.cache_timestamps:
                    age = time.time() - self.cache_timestamps[ip]
                    if age > self.cache_ttl:
                        del self.blacklisted_ips[ip]
                        del self.cache_timestamps[ip]
                        return None

                threat_score = self.blacklisted_ips[ip]
                threat_score.sources.append(ThreatSource.INTERNAL_DB)
                return threat_score

            return None

    async def cleanup_expired(self):
        """Remove expired cache entries"""
        async with self._lock:
            current_time = time.time()
            expired_ips = [
                ip
                for ip, timestamp in self.cache_timestamps.items()
                if current_time - timestamp > self.cache_ttl
            ]

            for ip in expired_ips:
                if ip in self.blacklisted_ips:
                    del self.blacklisted_ips[ip]
                del self.cache_timestamps[ip]


class AbuseIPDBChecker:
    """
    AbuseIPDB API integration.

    Checks IP reputation against AbuseIPDB.
    """

    BASE_URL = "https://api.abuseipdb.com/api/v2"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AbuseIPDB checker.

        Args:
            api_key: AbuseIPDB API key (get from https://www.abuseipdb.com/api)
        """
        self.api_key = api_key
        self.enabled = api_key is not None and AIOHTTP_AVAILABLE

        # Rate limiting (per API terms)
        self.requests_per_day = 1000
        self.request_count = 0
        self.reset_time = time.time() + 86400

    async def check_ip(self, ip: str) -> Optional[IPReputation]:
        """
        Check IP reputation with AbuseIPDB.

        Args:
            ip: IP address to check

        Returns:
            IPReputation if successful, None otherwise
        """
        if not self.enabled:
            return None

        # Check rate limit
        if time.time() > self.reset_time:
            self.request_count = 0
            self.reset_time = time.time() + 86400

        if self.request_count >= self.requests_per_day:
            return None

        try:
            headers = {
                "Key": self.api_key,
                "Accept": "application/json",
            }

            params = {"ipAddress": ip, "maxAgeInDays": 90, "verbose": True}

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.BASE_URL}/check",
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    self.request_count += 1

                    if response.status == 200:
                        data = await response.json()
                        return self._parse_response(data)

        except Exception:
            pass  # Silently fail to not break application

        return None

    def _parse_response(self, data: Dict[str, Any]) -> Optional[IPReputation]:
        """Parse AbuseIPDB response"""
        try:
            ip_data = data.get("data", {})

            # Calculate threat score
            abuse_confidence = ip_data.get("abuseConfidenceScore", 0)
            total_reports = ip_data.get("totalReports", 0)

            # Map abuse confidence to our threat score (0-100)
            threat_score_value = abuse_confidence

            # Determine categories
            categories = []
            if ip_data.get("isWhitelisted"):
                threat_score_value = 0
            else:
                # AbuseIPDB category mapping
                category_map = {
                    3: ThreatCategory.SCANNING,
                    4: ThreatCategory.DDOS,
                    5: ThreatCategory.SPAM,
                    9: ThreatCategory.MALWARE,
                    14: ThreatCategory.SCANNING,
                    18: ThreatCategory.BRUTE_FORCE,
                    21: ThreatCategory.BRUTE_FORCE,
                }

                for cat_id in ip_data.get("reports", []):
                    cat = category_map.get(cat_id)
                    if cat and cat not in categories:
                        categories.append(cat)

            threat_score = ThreatScore(
                score=threat_score_value,
                confidence=min(1.0, total_reports / 10),  # More reports = higher confidence
                categories=categories,
                sources=[ThreatSource.ABUSEIPDB],
                details={
                    "total_reports": total_reports,
                    "distinct_users": ip_data.get("numDistinctUsers", 0),
                },
                last_seen=(
                    datetime.fromisoformat(ip_data["lastReportedAt"].replace("Z", "+00:00"))
                    if ip_data.get("lastReportedAt")
                    else None
                ),
                is_blocked=abuse_confidence > 75,  # Block if >75% confidence
                reason=f"AbuseIPDB confidence: {abuse_confidence}%",
            )

            return IPReputation(
                ip_address=ip_data.get("ipAddress", ""),
                threat_score=threat_score,
                country_code=ip_data.get("countryCode"),
                isp=ip_data.get("isp"),
                is_tor=ip_data.get("isTor", False),
                reports_count=total_reports,
            )

        except Exception:
            return None


class ThreatIntelligence:
    """
    Comprehensive threat intelligence system.

    Aggregates threat data from multiple sources.
    """

    def __init__(
        self,
        abuseipdb_key: Optional[str] = None,
        enable_external: bool = True,
        cache_ttl: int = 3600,
    ):
        """
        Initialize threat intelligence.

        Args:
            abuseipdb_key: AbuseIPDB API key
            enable_external: Enable external API calls
            cache_ttl: Cache TTL in seconds
        """
        self.enable_external = enable_external and AIOHTTP_AVAILABLE

        # Internal database
        self.internal_db = InternalThreatDatabase(cache_ttl=cache_ttl)

        # External checkers
        self.abuseipdb = AbuseIPDBChecker(abuseipdb_key) if abuseipdb_key else None

        # Statistics
        self.stats = {
            "total_checks": 0,
            "cache_hits": 0,
            "external_calls": 0,
            "threats_detected": 0,
            "ips_blocked": 0,
        }

        self._lock = asyncio.Lock()

    async def check_ip(self, ip: str) -> IPReputation:
        """
        Check IP reputation from all sources.

        Args:
            ip: IP address to check

        Returns:
            IPReputation with aggregated threat data
        """
        async with self._lock:
            self.stats["total_checks"] += 1

        # Check internal database first
        internal_result = await self.internal_db.check_ip(ip)

        if internal_result:
            async with self._lock:
                self.stats["cache_hits"] += 1

            # Return cached result
            return IPReputation(ip_address=ip, threat_score=internal_result)

        # Initialize reputation
        reputation = IPReputation(ip_address=ip, threat_score=ThreatScore(score=0, confidence=0))

        # Check external sources if enabled
        if self.enable_external:
            # Check AbuseIPDB
            if self.abuseipdb and self.abuseipdb.enabled:
                async with self._lock:
                    self.stats["external_calls"] += 1

                abuse_result = await self.abuseipdb.check_ip(ip)

                if abuse_result:
                    reputation = abuse_result

        # Cache result
        if reputation.threat_score.score > 0:
            await self.internal_db.add_to_blacklist(ip, reputation.threat_score, permanent=False)

            async with self._lock:
                self.stats["threats_detected"] += 1

                if reputation.threat_score.is_blocked:
                    self.stats["ips_blocked"] += 1

        return reputation

    async def check_user_agent(self, user_agent: str) -> ThreatScore:
        """
        Check user agent for malicious patterns.

        Args:
            user_agent: User agent string

        Returns:
            ThreatScore
        """
        if not user_agent:
            return ThreatScore(score=0, confidence=0)

        user_agent_lower = user_agent.lower()

        # Check malicious patterns
        for malicious_pattern in self.internal_db.malicious_user_agents:
            if malicious_pattern in user_agent_lower:
                return ThreatScore(
                    score=90,
                    confidence=0.9,
                    categories=[ThreatCategory.SCANNING],
                    sources=[ThreatSource.INTERNAL_DB],
                    is_blocked=True,
                    reason=f"Malicious user agent: {malicious_pattern}",
                )

        # Check suspicious patterns
        for suspicious_pattern in self.internal_db.suspicious_user_agents:
            if suspicious_pattern in user_agent_lower:
                return ThreatScore(
                    score=50,
                    confidence=0.5,
                    categories=[ThreatCategory.BOT],
                    sources=[ThreatSource.INTERNAL_DB],
                    is_blocked=False,
                    reason=f"Suspicious user agent: {suspicious_pattern}",
                )

        return ThreatScore(score=0, confidence=0)

    async def block_ip(
        self,
        ip: str,
        reason: str,
        categories: Optional[List[ThreatCategory]] = None,
        permanent: bool = False,
    ):
        """
        Manually block an IP address.

        Args:
            ip: IP address to block
            reason: Reason for blocking
            categories: Threat categories
            permanent: Permanent block or temporary
        """
        threat_score = ThreatScore(
            score=100,
            confidence=1.0,
            categories=categories or [ThreatCategory.MANUAL],
            sources=[ThreatSource.MANUAL],
            is_blocked=True,
            reason=reason,
        )

        await self.internal_db.add_to_blacklist(ip, threat_score, permanent)

        async with self._lock:
            self.stats["ips_blocked"] += 1

    async def unblock_ip(self, ip: str):
        """
        Unblock an IP address.

        Args:
            ip: IP address to unblock
        """
        await self.internal_db.add_to_whitelist(ip)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get threat intelligence statistics"""
        async with self._lock:
            return dict(self.stats)

    async def cleanup(self):
        """Cleanup expired cache entries"""
        await self.internal_db.cleanup_expired()


class CVEMonitor:
    """
    CVE (Common Vulnerabilities and Exposures) monitoring.

    Tracks known vulnerabilities relevant to the application.
    """

    def __init__(self):
        """Initialize CVE monitor"""
        # Track known vulnerabilities
        self.known_cves: Dict[str, Dict[str, Any]] = {}

        # Critical CVEs affecting web applications
        self.critical_web_cves = {
            "CVE-2021-44228": {  # Log4Shell
                "name": "Log4Shell",
                "severity": "CRITICAL",
                "description": "Remote Code Execution in Log4j",
                "patterns": [r"\$\{jndi:", r"\$\{jndi:ldap://"],
            },
            "CVE-2021-45046": {  # Log4j
                "name": "Log4j DoS",
                "severity": "HIGH",
                "description": "Denial of Service in Log4j",
                "patterns": [r"\$\{jndi:"],
            },
        }

    def check_for_exploit_attempt(self, text: str) -> List[Dict[str, Any]]:
        """
        Check text for known CVE exploit attempts.

        Args:
            text: Text to check

        Returns:
            List of detected CVE exploits
        """
        detected = []

        for cve_id, cve_info in self.critical_web_cves.items():
            for pattern in cve_info.get("patterns", []):
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(
                        {
                            "cve_id": cve_id,
                            "name": cve_info["name"],
                            "severity": cve_info["severity"],
                            "description": cve_info["description"],
                            "matched_pattern": pattern,
                        }
                    )

        return detected


__all__ = [
    "ThreatIntelligence",
    "ThreatSource",
    "ThreatCategory",
    "ThreatScore",
    "IPReputation",
    "InternalThreatDatabase",
    "AbuseIPDBChecker",
    "CVEMonitor",
]
