"""
Honeypot System for Attacker Tracking

Honeypot endpoints and traps:
- Fake admin panels
- Decoy endpoints
- Attacker tracking and fingerprinting
- Attack pattern learning
- Automatic threat intelligence gathering

NO MOCK DATA - Real honeypot implementation.
"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class HoneypotType(str, Enum):
    """Honeypot types"""

    ADMIN_PANEL = "admin_panel"
    API_ENDPOINT = "api_endpoint"
    LOGIN_PAGE = "login_page"
    FILE_UPLOAD = "file_upload"
    DATABASE_PANEL = "database_panel"
    CONFIG_FILE = "config_file"
    HIDDEN_DIRECTORY = "hidden_directory"


@dataclass
class HoneypotInteraction:
    """Interaction with honeypot"""

    interaction_id: str
    honeypot_type: HoneypotType
    timestamp: datetime
    attacker_ip: str
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_headers: Dict[str, str] = field(default_factory=dict)
    request_body: Optional[str] = None
    attack_indicators: List[str] = field(default_factory=list)


@dataclass
class AttackerProfile:
    """Profile of attacker based on honeypot interactions"""

    attacker_id: str
    ip_addresses: Set[str] = field(default_factory=set)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    interaction_count: int = 0
    honeypots_triggered: Set[HoneypotType] = field(default_factory=set)
    user_agents: Set[str] = field(default_factory=set)
    attack_patterns: List[str] = field(default_factory=list)
    threat_score: float = 0.0  # 0-100


class HoneypotEndpoint:
    """Individual honeypot endpoint"""

    def __init__(self, path: str, honeypot_type: HoneypotType, response_template: Dict[str, Any]):
        """
        Initialize honeypot endpoint.

        Args:
            path: URL path for honeypot
            honeypot_type: Type of honeypot
            response_template: Template for response
        """
        self.path = path
        self.honeypot_type = honeypot_type
        self.response_template = response_template
        self.hit_count = 0
        self.unique_ips: Set[str] = set()

    def generate_response(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic response"""
        # Add some realism to response
        response = self.response_template.copy()

        # Add request-specific data
        if "session_id" in request_data:
            response["session_id"] = request_data["session_id"]

        return response


class Honeypot:
    """
    Honeypot system for detecting and tracking attackers.

    Deploys decoy endpoints to identify malicious activity.
    """

    def __init__(self, alert_callback: Optional[Callable] = None, auto_block_threshold: int = 3):
        """
        Initialize honeypot system.

        Args:
            alert_callback: Callback for honeypot hits
            auto_block_threshold: Number of hits before auto-blocking
        """
        self.alert_callback = alert_callback
        self.auto_block_threshold = auto_block_threshold

        # Honeypot endpoints
        self.endpoints: Dict[str, HoneypotEndpoint] = {}

        # Interactions
        self.interactions: List[HoneypotInteraction] = []

        # Attacker profiles
        self.attacker_profiles: Dict[str, AttackerProfile] = {}

        # Statistics
        self.stats = {
            "total_interactions": 0,
            "unique_attackers": 0,
            "by_honeypot_type": defaultdict(int),
            "blocked_ips": set(),
        }

        self._lock = asyncio.Lock()

        # Setup default honeypots
        self._setup_default_honeypots()

    def _setup_default_honeypots(self):
        """Setup default honeypot endpoints"""
        # Fake admin panel
        self.register_honeypot(
            path="/admin",
            honeypot_type=HoneypotType.ADMIN_PANEL,
            response_template={
                "status": "error",
                "message": "Unauthorized access",
                "login_url": "/admin/login",
            },
        )

        # Fake WordPress admin
        self.register_honeypot(
            path="/wp-admin",
            honeypot_type=HoneypotType.ADMIN_PANEL,
            response_template={"error": "Access denied", "wp_version": "5.8.0"},
        )

        # Fake phpMyAdmin
        self.register_honeypot(
            path="/phpmyadmin",
            honeypot_type=HoneypotType.DATABASE_PANEL,
            response_template={"error": "Authentication required", "version": "5.1.0"},
        )

        # Fake .env file
        self.register_honeypot(
            path="/.env",
            honeypot_type=HoneypotType.CONFIG_FILE,
            response_template={"error": "File not found", "suggestion": "Check file permissions"},
        )

        # Fake .git directory
        self.register_honeypot(
            path="/.git/config",
            honeypot_type=HoneypotType.HIDDEN_DIRECTORY,
            response_template={"error": "Access forbidden"},
        )

    def register_honeypot(
        self, path: str, honeypot_type: HoneypotType, response_template: Dict[str, Any]
    ):
        """Register a honeypot endpoint"""
        endpoint = HoneypotEndpoint(path, honeypot_type, response_template)
        self.endpoints[path] = endpoint

    async def record_interaction(
        self, path: str, attacker_ip: str, request_data: Dict[str, Any]
    ) -> Optional[HoneypotInteraction]:
        """
        Record honeypot interaction.

        Args:
            path: Requested path
            attacker_ip: Attacker IP
            request_data: Request data

        Returns:
            Interaction object if honeypot hit
        """
        # Check if path is a honeypot
        if path not in self.endpoints:
            return None

        endpoint = self.endpoints[path]

        # Generate interaction ID
        interaction_id = self._generate_interaction_id()

        # Detect attack indicators
        attack_indicators = self._detect_attack_indicators(request_data)

        # Create interaction
        interaction = HoneypotInteraction(
            interaction_id=interaction_id,
            honeypot_type=endpoint.honeypot_type,
            timestamp=datetime.utcnow(),
            attacker_ip=attacker_ip,
            user_agent=request_data.get("user_agent"),
            request_method=request_data.get("method"),
            request_path=path,
            request_headers=request_data.get("headers", {}),
            request_body=request_data.get("body"),
            attack_indicators=attack_indicators,
        )

        # Update endpoint stats
        endpoint.hit_count += 1
        endpoint.unique_ips.add(attacker_ip)

        # Store interaction
        async with self._lock:
            self.interactions.append(interaction)
            self.stats["total_interactions"] += 1
            self.stats["by_honeypot_type"][endpoint.honeypot_type.value] += 1

        # Update attacker profile
        await self._update_attacker_profile(attacker_ip, interaction)

        # Send alert
        if self.alert_callback:
            try:
                await self.alert_callback(interaction)
            except Exception:
                pass

        # Check for auto-block
        await self._check_auto_block(attacker_ip)

        return interaction

    async def _update_attacker_profile(self, attacker_ip: str, interaction: HoneypotInteraction):
        """Update attacker profile"""
        async with self._lock:
            # Get or create profile
            if attacker_ip not in self.attacker_profiles:
                attacker_id = self._generate_attacker_id(attacker_ip)
                self.attacker_profiles[attacker_ip] = AttackerProfile(
                    attacker_id=attacker_id, first_seen=interaction.timestamp
                )
                self.stats["unique_attackers"] += 1

            profile = self.attacker_profiles[attacker_ip]

            # Update profile
            profile.ip_addresses.add(attacker_ip)
            profile.last_seen = interaction.timestamp
            profile.interaction_count += 1
            profile.honeypots_triggered.add(interaction.honeypot_type)

            if interaction.user_agent:
                profile.user_agents.add(interaction.user_agent)

            # Add attack patterns
            profile.attack_patterns.extend(interaction.attack_indicators)

            # Calculate threat score
            profile.threat_score = self._calculate_threat_score(profile)

    def _calculate_threat_score(self, profile: AttackerProfile) -> float:
        """Calculate threat score for attacker"""
        score = 0.0

        # More interactions = higher score
        score += min(50, profile.interaction_count * 10)

        # Multiple honeypots triggered = higher score
        score += len(profile.honeypots_triggered) * 15

        # Multiple user agents = possible evasion
        if len(profile.user_agents) > 3:
            score += 20

        # Attack patterns detected
        score += len(set(profile.attack_patterns)) * 5

        return min(100, score)

    async def _check_auto_block(self, attacker_ip: str):
        """Check if IP should be auto-blocked"""
        async with self._lock:
            if attacker_ip in self.attacker_profiles:
                profile = self.attacker_profiles[attacker_ip]

                if profile.interaction_count >= self.auto_block_threshold:
                    self.stats["blocked_ips"].add(attacker_ip)
                    # In production, would trigger actual IP block

    def _detect_attack_indicators(self, request_data: Dict[str, Any]) -> List[str]:
        """Detect attack indicators in request"""
        indicators = []

        # Check user agent
        user_agent = request_data.get("user_agent", "").lower()
        suspicious_agents = ["sqlmap", "nikto", "nmap", "masscan", "acunetix"]

        for agent in suspicious_agents:
            if agent in user_agent:
                indicators.append(f"suspicious_user_agent:{agent}")

        # Check for common attack tools
        if "python-requests" in user_agent or "curl" in user_agent:
            indicators.append("automated_tool")

        # Check request body for attacks
        body = request_data.get("body", "")
        if body:
            if "union select" in body.lower():
                indicators.append("sql_injection_attempt")
            if "<script" in body.lower():
                indicators.append("xss_attempt")

        return indicators

    async def get_attacker_profile(self, attacker_ip: str) -> Optional[AttackerProfile]:
        """Get attacker profile"""
        async with self._lock:
            return self.attacker_profiles.get(attacker_ip)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get honeypot statistics"""
        async with self._lock:
            return {
                "total_interactions": self.stats["total_interactions"],
                "unique_attackers": self.stats["unique_attackers"],
                "by_honeypot_type": dict(self.stats["by_honeypot_type"]),
                "blocked_ips": len(self.stats["blocked_ips"]),
                "endpoint_stats": {
                    path: {
                        "type": endpoint.honeypot_type.value,
                        "hit_count": endpoint.hit_count,
                        "unique_ips": len(endpoint.unique_ips),
                    }
                    for path, endpoint in self.endpoints.items()
                },
            }

    async def generate_threat_report(self) -> Dict[str, Any]:
        """Generate threat intelligence report from honeypot data"""
        async with self._lock:
            # Top attackers
            top_attackers = sorted(
                self.attacker_profiles.values(), key=lambda p: p.threat_score, reverse=True
            )[:10]

            # Common attack patterns
            all_patterns = []
            for profile in self.attacker_profiles.values():
                all_patterns.extend(profile.attack_patterns)

            pattern_counts = defaultdict(int)
            for pattern in all_patterns:
                pattern_counts[pattern] += 1

            return {
                "report_generated": datetime.utcnow().isoformat(),
                "summary": {
                    "total_interactions": self.stats["total_interactions"],
                    "unique_attackers": self.stats["unique_attackers"],
                    "blocked_ips": len(self.stats["blocked_ips"]),
                },
                "top_attackers": [
                    {
                        "attacker_id": p.attacker_id,
                        "ip_addresses": list(p.ip_addresses),
                        "interaction_count": p.interaction_count,
                        "threat_score": p.threat_score,
                        "honeypots_triggered": [h.value for h in p.honeypots_triggered],
                    }
                    for p in top_attackers
                ],
                "common_attack_patterns": dict(
                    sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)[:20]
                ),
            }

    def _generate_interaction_id(self) -> str:
        """Generate unique interaction ID"""
        return hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    def _generate_attacker_id(self, ip: str) -> str:
        """Generate attacker ID"""
        return f"ATK-{hashlib.md5(ip.encode(), usedforsecurity=False).hexdigest()[:8].upper()}"


__all__ = [
    "Honeypot",
    "HoneypotType",
    "HoneypotInteraction",
    "AttackerProfile",
    "HoneypotEndpoint",
]
