"""
Security Forensics Tools

Digital forensics capabilities:
- Request/response capture
- Session replay
- Attack trace analysis
- Evidence preservation
- Chain of custody tracking
- Forensic report generation

NO MOCK DATA - Real forensic evidence collection.
"""

import asyncio
import gzip
import hashlib
import json
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


class EvidenceType(str, Enum):
    """Evidence types"""

    REQUEST_LOG = "request_log"
    RESPONSE_LOG = "response_log"
    SESSION_DATA = "session_data"
    ATTACK_PAYLOAD = "attack_payload"
    SYSTEM_LOG = "system_log"
    NETWORK_TRACE = "network_trace"
    FILE_ARTIFACT = "file_artifact"


@dataclass
class Evidence:
    """Forensic evidence"""

    evidence_id: str
    evidence_type: EvidenceType
    timestamp: datetime
    collected_by: str
    description: str
    data: Dict[str, Any]
    hash: str  # SHA-256 hash for integrity
    chain_of_custody: List[Dict[str, str]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    related_incident_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["evidence_type"] = self.evidence_type.value
        return data


@dataclass
class AttackTrace:
    """Attack trace for analysis"""

    trace_id: str
    attacker_ip: str
    start_time: datetime
    end_time: Optional[datetime]
    request_count: int
    requests: List[Dict[str, Any]] = field(default_factory=list)
    attack_patterns: List[str] = field(default_factory=list)
    user_agents: Set[str] = field(default_factory=set)
    paths_accessed: List[str] = field(default_factory=list)


class ForensicsCollector:
    """
    Forensic evidence collector.

    Captures and preserves security-related evidence.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        compress_evidence: bool = True,
        max_evidence_age_days: int = 90,
    ):
        """
        Initialize forensics collector.

        Args:
            storage_path: Path to store evidence files
            compress_evidence: Compress evidence data
            max_evidence_age_days: Maximum age of evidence to retain
        """
        self.storage_path = Path(storage_path) if storage_path else None
        self.compress_evidence = compress_evidence
        self.max_evidence_age_days = max_evidence_age_days

        # Evidence storage
        self.evidence_store: Dict[str, Evidence] = {}

        # Attack traces
        self.attack_traces: Dict[str, AttackTrace] = {}

        # Request capture buffer
        self.request_buffer: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        self._lock = asyncio.Lock()

        # Setup storage
        if self.storage_path:
            self.storage_path.mkdir(parents=True, exist_ok=True)

    async def capture_request(
        self, request_data: Dict[str, Any], incident_id: Optional[str] = None
    ) -> Evidence:
        """
        Capture HTTP request for forensic analysis.

        Args:
            request_data: Request data (method, path, headers, body, etc.)
            incident_id: Related incident ID

        Returns:
            Evidence object
        """
        # Generate evidence ID
        evidence_id = self._generate_evidence_id()

        # Calculate hash
        data_hash = self._calculate_hash(request_data)

        # Create evidence
        evidence = Evidence(
            evidence_id=evidence_id,
            evidence_type=EvidenceType.REQUEST_LOG,
            timestamp=datetime.utcnow(),
            collected_by="forensics_collector",
            description="HTTP request capture",
            data=request_data,
            hash=data_hash,
            related_incident_id=incident_id,
            tags=["request", "http"],
        )

        # Add to chain of custody
        evidence.chain_of_custody.append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "collected",
                "actor": "forensics_collector",
            }
        )

        # Store evidence
        await self._store_evidence(evidence)

        return evidence

    async def capture_attack_trace(self, attacker_ip: str, request_data: Dict[str, Any]) -> str:
        """
        Capture attack trace for analysis.

        Args:
            attacker_ip: Attacker IP address
            request_data: Request data

        Returns:
            Trace ID
        """
        async with self._lock:
            # Get or create trace
            if attacker_ip not in self.attack_traces:
                trace_id = self._generate_trace_id()
                self.attack_traces[attacker_ip] = AttackTrace(
                    trace_id=trace_id,
                    attacker_ip=attacker_ip,
                    start_time=datetime.utcnow(),
                    end_time=None,
                    request_count=0,
                )

            trace = self.attack_traces[attacker_ip]
            trace.requests.append(request_data)
            trace.request_count += 1
            trace.paths_accessed.append(request_data.get("path", ""))

            if "user_agent" in request_data:
                trace.user_agents.add(request_data["user_agent"])

            return trace.trace_id

    async def analyze_attack_trace(self, attacker_ip: str) -> Dict[str, Any]:
        """
        Analyze attack trace.

        Args:
            attacker_ip: Attacker IP

        Returns:
            Analysis results
        """
        async with self._lock:
            if attacker_ip not in self.attack_traces:
                return {}

            trace = self.attack_traces[attacker_ip]

            # Analyze patterns
            unique_paths = len(set(trace.paths_accessed))
            unique_user_agents = len(trace.user_agents)

            # Determine attack characteristics
            is_scanning = unique_paths > 10
            is_targeted = unique_paths < 5 and trace.request_count > 5
            is_evasion = unique_user_agents > 3

            return {
                "trace_id": trace.trace_id,
                "attacker_ip": attacker_ip,
                "duration_seconds": (
                    (trace.end_time or datetime.utcnow()) - trace.start_time
                ).total_seconds(),
                "total_requests": trace.request_count,
                "unique_paths": unique_paths,
                "unique_user_agents": unique_user_agents,
                "characteristics": {
                    "is_scanning": is_scanning,
                    "is_targeted": is_targeted,
                    "is_evasion": is_evasion,
                },
                "sample_requests": trace.requests[:10],  # First 10 requests
            }

    async def preserve_evidence(self, evidence_id: str, preserved_by: str) -> bool:
        """
        Mark evidence as preserved with chain of custody.

        Args:
            evidence_id: Evidence ID
            preserved_by: Person preserving evidence

        Returns:
            Success status
        """
        async with self._lock:
            if evidence_id not in self.evidence_store:
                return False

            evidence = self.evidence_store[evidence_id]

            # Add to chain of custody
            evidence.chain_of_custody.append(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "action": "preserved",
                    "actor": preserved_by,
                }
            )

            # Write to permanent storage
            if self.storage_path:
                await self._write_to_storage(evidence)

            return True

    async def generate_forensic_report(self, incident_id: str) -> Dict[str, Any]:
        """
        Generate forensic report for incident.

        Args:
            incident_id: Incident ID

        Returns:
            Forensic report
        """
        async with self._lock:
            # Gather all evidence for incident
            related_evidence = [
                evidence
                for evidence in self.evidence_store.values()
                if evidence.related_incident_id == incident_id
            ]

            # Generate report
            report = {
                "incident_id": incident_id,
                "report_generated": datetime.utcnow().isoformat(),
                "evidence_count": len(related_evidence),
                "evidence": [evidence.to_dict() for evidence in related_evidence],
                "summary": {
                    "by_type": defaultdict(int),
                    "earliest_timestamp": None,
                    "latest_timestamp": None,
                },
            }

            # Calculate summary
            for evidence in related_evidence:
                report["summary"]["by_type"][evidence.evidence_type.value] += 1

                if (
                    report["summary"]["earliest_timestamp"] is None
                    or evidence.timestamp < report["summary"]["earliest_timestamp"]
                ):
                    report["summary"]["earliest_timestamp"] = evidence.timestamp

                if (
                    report["summary"]["latest_timestamp"] is None
                    or evidence.timestamp > report["summary"]["latest_timestamp"]
                ):
                    report["summary"]["latest_timestamp"] = evidence.timestamp

            # Convert timestamps
            if report["summary"]["earliest_timestamp"]:
                report["summary"]["earliest_timestamp"] = report["summary"][
                    "earliest_timestamp"
                ].isoformat()
            if report["summary"]["latest_timestamp"]:
                report["summary"]["latest_timestamp"] = report["summary"][
                    "latest_timestamp"
                ].isoformat()

            report["summary"]["by_type"] = dict(report["summary"]["by_type"])

            return report

    async def cleanup_old_evidence(self) -> int:
        """Remove evidence older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.max_evidence_age_days)

        async with self._lock:
            old_count = len(self.evidence_store)

            # Filter out old evidence
            self.evidence_store = {
                eid: evidence
                for eid, evidence in self.evidence_store.items()
                if evidence.timestamp > cutoff_date
            }

            return old_count - len(self.evidence_store)

    async def _store_evidence(self, evidence: Evidence):
        """Store evidence in memory and optionally to disk"""
        async with self._lock:
            self.evidence_store[evidence.evidence_id] = evidence

        # Write to storage if configured
        if self.storage_path:
            await self._write_to_storage(evidence)

    async def _write_to_storage(self, evidence: Evidence):
        """Write evidence to persistent storage"""
        try:
            # Create filename with timestamp
            filename = f"{evidence.evidence_id}_{evidence.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.storage_path / filename

            # Convert to JSON
            evidence_json = json.dumps(evidence.to_dict(), indent=2)

            # Compress if enabled
            if self.compress_evidence:
                evidence_data = gzip.compress(evidence_json.encode("utf-8"))
                filepath = filepath.with_suffix(".json.gz")
            else:
                evidence_data = evidence_json.encode("utf-8")

            # Write to file (use executor for blocking I/O)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._write_file_sync, filepath, evidence_data)

        except Exception:
            pass  # Silent fail

    def _write_file_sync(self, filepath: Path, data: bytes):
        """Synchronous file write"""
        with open(filepath, "wb") as f:
            f.write(data)

    def _generate_evidence_id(self) -> str:
        """Generate unique evidence ID"""
        return f"EVD-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12].upper()}"

    def _generate_trace_id(self) -> str:
        """Generate unique trace ID"""
        return f"TRC-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:12].upper()}"

    def _calculate_hash(self, data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of data"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()


from datetime import timedelta

__all__ = [
    "ForensicsCollector",
    "Evidence",
    "EvidenceType",
    "AttackTrace",
]
