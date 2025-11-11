"""
Complete Security Monitoring Setup Example

This example demonstrates how to set up comprehensive security monitoring
for a CovetPy application with all components integrated.
"""

import asyncio
from covet.security.monitoring import (
    IDS,
    ThreatIntelligence,
    AuditLogger,
    SecurityAlerter,
    SecurityMetrics,
    IncidentResponseAutomation,
    ForensicsCollector,
    Honeypot,
    RequestProfile,
    EventType,
    Severity,
    AlertSeverity,
    IncidentSeverity,
)


class SecurityMonitoringStack:
    """Complete security monitoring stack"""

    def __init__(self):
        """Initialize all security components"""

        # 1. Intrusion Detection System
        self.ids = IDS(
            enable_signatures=True,
            enable_anomaly=True,
            enable_behavioral=True,
            alert_callback=self.handle_ids_detection
        )

        # 2. Threat Intelligence
        self.threat_intel = ThreatIntelligence(
            abuseipdb_key=None,  # Add your API key
            enable_external=False,  # Enable when API key available
            cache_ttl=3600
        )

        # 3. Audit Logging with SIEM
        self.audit = AuditLogger(
            log_file="/var/log/covet/security/audit.log",
            siem_config={
                'platform': 'elastic',  # or 'splunk', 'datadog'
                'endpoint': 'http://localhost:9200',
                # 'api_key': 'your-api-key'
            },
            enable_console=True,
            alert_callback=self.handle_critical_audit_event
        )

        # 4. Multi-channel Alerting
        self.alerter = SecurityAlerter(
            email_config={
                'smtp_host': 'smtp.example.com',
                'smtp_port': 587,
                'smtp_user': 'security@example.com',
                'smtp_password': 'password',
                'from_email': 'security@example.com',
                'to_emails': ['security-team@example.com']
            },
            slack_webhook='https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
            # pagerduty_key='your-pagerduty-key',
            enable_throttling=True
        )

        # 5. Security Metrics
        self.metrics = SecurityMetrics(enable_prometheus=True)

        # 6. Incident Response
        self.incident_response = IncidentResponseAutomation(
            enable_auto_containment=True,
            alert_callback=self.handle_incident_alert,
            containment_callback=self.execute_containment_action
        )

        # 7. Forensics
        self.forensics = ForensicsCollector(
            storage_path="/var/log/covet/forensics",
            compress_evidence=True
        )

        # 8. Honeypot
        self.honeypot = Honeypot(
            alert_callback=self.handle_honeypot_interaction,
            auto_block_threshold=3
        )

    async def handle_ids_detection(self, detections):
        """Handle IDS detections"""
        for detection in detections:
            if detection.recommended_action == "block":
                # Log to audit
                await self.audit.log(
                    EventType.ATTACK_DETECTED,
                    Severity.CRITICAL,
                    f"Attack detected: {detection.attack_type.value if detection.attack_type else 'unknown'}",
                    details=detection.details
                )

                # Record metric
                if detection.attack_type:
                    await self.metrics.record_attack_attempt(
                        detection.attack_type.value
                    )

    async def handle_critical_audit_event(self, event):
        """Handle critical audit events"""
        # Send alert for critical events
        await self.alerter.send_alert(
            title=f"Critical Security Event: {event.event_type.value}",
            message=event.message,
            severity=AlertSeverity.CRITICAL,
            details=event.details
        )

    async def handle_incident_alert(self, incident):
        """Handle incident alerts"""
        await self.alerter.send_alert(
            title=f"Security Incident: {incident.incident_id}",
            message=incident.description,
            severity=(
                AlertSeverity.CRITICAL if incident.severity == IncidentSeverity.CRITICAL
                else AlertSeverity.HIGH
            ),
            details={
                'incident_id': incident.incident_id,
                'attack_type': incident.attack_type,
                'affected_resources': incident.affected_resources
            }
        )

    async def execute_containment_action(self, action, incident):
        """Execute containment actions"""
        from covet.security.monitoring import ContainmentAction

        if action == ContainmentAction.BLOCK_IP:
            for ip in incident.attacker_ips:
                await self.threat_intel.block_ip(
                    ip,
                    reason=f"Incident {incident.incident_id}",
                    permanent=False
                )
                await self.metrics.record_blocked_ip(ip)

    async def handle_honeypot_interaction(self, interaction):
        """Handle honeypot interactions"""
        # Log to audit
        await self.audit.log(
            EventType.SECURITY_EVENT,
            Severity.WARNING,
            f"Honeypot triggered: {interaction.honeypot_type.value}",
            ip_address=interaction.attacker_ip,
            user_agent=interaction.user_agent,
            path=interaction.request_path
        )

        # Collect forensic evidence
        await self.forensics.capture_request(
            {
                'method': interaction.request_method,
                'path': interaction.request_path,
                'headers': interaction.request_headers
            }
        )

    async def analyze_request(self, request_data: dict):
        """
        Comprehensive request analysis.

        Args:
            request_data: HTTP request data
        """
        # Create request profile
        profile = RequestProfile(
            method=request_data.get('method', 'GET'),
            path=request_data.get('path', '/'),
            query_params=request_data.get('query_params', {}),
            headers=request_data.get('headers', {}),
            body=request_data.get('body'),
            ip_address=request_data.get('ip_address'),
            user_agent=request_data.get('user_agent'),
            user_id=request_data.get('user_id'),
            session_id=request_data.get('session_id')
        )

        # 1. Check if honeypot
        honeypot_hit = await self.honeypot.record_interaction(
            path=profile.path,
            attacker_ip=profile.ip_address,
            request_data=request_data
        )

        if honeypot_hit:
            # Honeypot triggered - already handled
            return

        # 2. Check threat intelligence
        if profile.ip_address:
            ip_reputation = await self.threat_intel.check_ip(profile.ip_address)

            if ip_reputation.threat_score.is_blocked:
                await self.audit.log(
                    EventType.IP_BLOCKED,
                    Severity.WARNING,
                    f"Blocked IP attempted access: {profile.ip_address}",
                    ip_address=profile.ip_address,
                    details={'threat_score': ip_reputation.threat_score.score}
                )
                return  # Block request

        # 3. Run IDS analysis
        detections = await self.ids.analyze_request(profile)

        if detections:
            # Attacks detected
            critical_detections = [
                d for d in detections
                if d.threat_level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH]
            ]

            if critical_detections:
                # Capture forensic evidence
                evidence = await self.forensics.capture_request(request_data)

                # Create incident
                incident = await self.incident_response.create_incident(
                    title=f"Attack Detected: {critical_detections[0].attack_type.value if critical_detections[0].attack_type else 'Unknown'}",
                    description=f"IDS detected {len(critical_detections)} critical threats",
                    severity=IncidentSeverity.CRITICAL,
                    attack_type=critical_detections[0].attack_type.value if critical_detections[0].attack_type else None,
                    attacker_ips=[profile.ip_address] if profile.ip_address else [],
                    evidence={'detections': [d.details for d in critical_detections]}
                )

                # Link evidence to incident
                await self.forensics.preserve_evidence(
                    evidence.evidence_id,
                    "automated_incident_response"
                )

    async def get_security_status(self):
        """Get overall security status"""
        return {
            'ids': await self.ids.get_statistics(),
            'audit': await self.audit.get_statistics(),
            'alerts': await self.alerter.get_statistics(),
            'metrics': await self.metrics.get_statistics(),
            'incidents': await self.incident_response.get_statistics(),
            'honeypot': await self.honeypot.get_statistics(),
        }


# Example usage
async def main():
    """Example usage"""
    # Initialize security stack
    security = SecurityMonitoringStack()

    # Simulate legitimate request
    legitimate_request = {
        'method': 'GET',
        'path': '/api/users/123',
        'query_params': {},
        'headers': {'User-Agent': 'Mozilla/5.0'},
        'ip_address': '192.0.2.1',
        'user_id': 'user123'
    }

    await security.analyze_request(legitimate_request)
    print("✓ Legitimate request processed")

    # Simulate SQL injection attack
    attack_request = {
        'method': 'POST',
        'path': '/api/login',
        'query_params': {'username': "admin' OR '1'='1", 'password': 'anything'},
        'headers': {'User-Agent': 'sqlmap/1.0'},
        'body': '{"username": "admin", "password": "\'OR \'1\'=\'1"}',
        'ip_address': '198.51.100.99'
    }

    await security.analyze_request(attack_request)
    print("✓ Attack detected and contained")

    # Simulate honeypot interaction
    honeypot_request = {
        'method': 'GET',
        'path': '/admin',  # Honeypot endpoint
        'query_params': {},
        'headers': {'User-Agent': 'nikto'},
        'ip_address': '203.0.113.50'
    }

    await security.analyze_request(honeypot_request)
    print("✓ Honeypot interaction recorded")

    # Get security status
    status = await security.get_security_status()
    print(f"\nSecurity Status:")
    print(f"  Total attacks detected: {status['ids']['total_detections']}")
    print(f"  Active incidents: {status['incidents']['open_incidents']}")
    print(f"  Honeypot interactions: {status['honeypot']['total_interactions']}")

    # Export Prometheus metrics
    prometheus_metrics = await security.metrics.export_prometheus_metrics()
    print(f"\nPrometheus Metrics:")
    print(prometheus_metrics[:500] + "...")


if __name__ == "__main__":
    asyncio.run(main())
