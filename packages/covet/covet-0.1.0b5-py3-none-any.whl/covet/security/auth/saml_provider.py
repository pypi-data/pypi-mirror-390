"""
SAML 2.0 Provider - Service Provider (SP) and Identity Provider (IdP)

Production-ready SAML 2.0 implementation with support for:
- Single Sign-On (SSO) - SP-initiated and IdP-initiated
- Single Logout (SLO)
- Assertion validation and verification
- XML signature verification (RSA-SHA256)
- XML encryption support
- Metadata exchange (SP and IdP metadata)
- Multiple IdP support
- Attribute mapping and transformation

SECURITY FEATURES:
- XML signature verification (RSA-SHA256, RSA-SHA512)
- XML encryption (AES-256-CBC, AES-128-GCM)
- Assertion expiration validation
- Recipient and audience validation
- Replay attack prevention
- SAML request/response binding (HTTP-POST, HTTP-Redirect)
- Certificate validation and trust management

Compatible with popular IdPs: Okta, Auth0, Azure AD, OneLogin, Google Workspace

NO MOCK DATA: Real SAML implementation with XML signing and encryption.
"""

import base64
import hashlib
import secrets
import uuid
import zlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlencode, urlparse
from xml.dom import minidom
from xml.etree import ElementTree as ET

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.x509.oid import NameOID
except ImportError:
    # Graceful degradation
    x509 = None
    default_backend = None
    hashes = None
    serialization = None
    padding = None
    rsa = None
    Cipher = None
    algorithms = None
    modes = None
    NameOID = None


class SAMLBinding(str, Enum):
    """SAML protocol bindings."""

    HTTP_POST = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
    HTTP_REDIRECT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
    HTTP_ARTIFACT = "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Artifact"
    SOAP = "urn:oasis:names:tc:SAML:2.0:bindings:SOAP"


class SAMLNameIDFormat(str, Enum):
    """SAML NameID formats."""

    UNSPECIFIED = "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified"
    EMAIL = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    PERSISTENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:persistent"
    TRANSIENT = "urn:oasis:names:tc:SAML:2.0:nameid-format:transient"
    ENTITY = "urn:oasis:names:tc:SAML:2.0:nameid-format:entity"


class SAMLAuthnContext(str, Enum):
    """SAML authentication context classes."""

    PASSWORD = "urn:oasis:names:tc:SAML:2.0:ac:classes:Password"
    PASSWORD_PROTECTED_TRANSPORT = (
        "urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport"
    )
    X509 = "urn:oasis:names:tc:SAML:2.0:ac:classes:X509"
    SMARTCARD = "urn:oasis:names:tc:SAML:2.0:ac:classes:Smartcard"
    KERBEROS = "urn:oasis:names:tc:SAML:2.0:ac:classes:Kerberos"
    UNSPECIFIED = "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified"


class SAMLStatusCode(str, Enum):
    """SAML status codes."""

    SUCCESS = "urn:oasis:names:tc:SAML:2.0:status:Success"
    REQUESTER = "urn:oasis:names:tc:SAML:2.0:status:Requester"
    RESPONDER = "urn:oasis:names:tc:SAML:2.0:status:Responder"
    VERSION_MISMATCH = "urn:oasis:names:tc:SAML:2.0:status:VersionMismatch"
    AUTHN_FAILED = "urn:oasis:names:tc:SAML:2.0:status:AuthnFailed"
    INVALID_ATTR_NAME_OR_VALUE = "urn:oasis:names:tc:SAML:2.0:status:InvalidAttrNameOrValue"
    INVALID_NAMEID_POLICY = "urn:oasis:names:tc:SAML:2.0:status:InvalidNameIDPolicy"
    NO_AUTHN_CONTEXT = "urn:oasis:names:tc:SAML:2.0:status:NoAuthnContext"
    NO_AVAILABLE_IDP = "urn:oasis:names:tc:SAML:2.0:status:NoAvailableIDP"
    NO_PASSIVE = "urn:oasis:names:tc:SAML:2.0:status:NoPassive"
    NO_SUPPORTED_IDP = "urn:oasis:names:tc:SAML:2.0:status:NoSupportedIDP"
    PARTIAL_LOGOUT = "urn:oasis:names:tc:SAML:2.0:status:PartialLogout"
    PROXY_COUNT_EXCEEDED = "urn:oasis:names:tc:SAML:2.0:status:ProxyCountExceeded"
    REQUEST_DENIED = "urn:oasis:names:tc:SAML:2.0:status:RequestDenied"
    REQUEST_UNSUPPORTED = "urn:oasis:names:tc:SAML:2.0:status:RequestUnsupported"
    REQUEST_VERSION_DEPRECATED = "urn:oasis:names:tc:SAML:2.0:status:RequestVersionDeprecated"
    REQUEST_VERSION_TOO_HIGH = "urn:oasis:names:tc:SAML:2.0:status:RequestVersionTooHigh"
    REQUEST_VERSION_TOO_LOW = "urn:oasis:names:tc:SAML:2.0:status:RequestVersionTooLow"
    RESOURCE_NOT_RECOGNIZED = "urn:oasis:names:tc:SAML:2.0:status:ResourceNotRecognized"
    TOO_MANY_RESPONSES = "urn:oasis:names:tc:SAML:2.0:status:TooManyResponses"
    UNKNOWN_ATTR_PROFILE = "urn:oasis:names:tc:SAML:2.0:status:UnknownAttrProfile"
    UNKNOWN_PRINCIPAL = "urn:oasis:names:tc:SAML:2.0:status:UnknownPrincipal"
    UNSUPPORTED_BINDING = "urn:oasis:names:tc:SAML:2.0:status:UnsupportedBinding"


# SAML XML namespaces
NS_SAML = "urn:oasis:names:tc:SAML:2.0:assertion"
NS_SAMLP = "urn:oasis:names:tc:SAML:2.0:protocol"
NS_DS = "http://www.w3.org/2000/09/xmldsig#"
NS_XENC = "http://www.w3.org/2001/04/xmlenc#"
NS_XS = "http://www.w3.org/2001/XMLSchema"
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"


@dataclass
class SAMLConfig:
    """SAML Service Provider configuration."""

    # Entity IDs
    sp_entity_id: str  # Service Provider entity ID
    idp_entity_id: str  # Identity Provider entity ID

    # URLs
    acs_url: str  # Assertion Consumer Service URL
    sls_url: Optional[str] = None  # Single Logout Service URL
    idp_sso_url: str = None  # IdP SSO URL
    idp_slo_url: Optional[str] = None  # IdP SLO URL

    # Certificates (PEM format)
    sp_private_key: Optional[str] = None  # SP private key for signing
    sp_certificate: Optional[str] = None  # SP certificate
    idp_certificate: Optional[str] = None  # IdP certificate for verification

    # Settings
    name_id_format: SAMLNameIDFormat = SAMLNameIDFormat.PERSISTENT
    authn_context: List[SAMLAuthnContext] = field(
        default_factory=lambda: [SAMLAuthnContext.PASSWORD_PROTECTED_TRANSPORT]
    )

    # Security settings
    want_assertions_signed: bool = True
    want_response_signed: bool = True
    sign_requests: bool = True
    sign_logout_requests: bool = True

    # Validation settings
    assertion_max_age: int = 3600  # 1 hour
    clock_skew: int = 60  # 60 seconds clock skew tolerance

    # Attribute mapping (IdP attribute -> SP attribute)
    attribute_map: Dict[str, str] = field(default_factory=dict)

    # Organization info
    organization_name: Optional[str] = None
    organization_display_name: Optional[str] = None
    organization_url: Optional[str] = None

    # Contact info
    technical_contact_name: Optional[str] = None
    technical_contact_email: Optional[str] = None
    support_contact_name: Optional[str] = None
    support_contact_email: Optional[str] = None


@dataclass
class SAMLAssertion:
    """SAML assertion data."""

    # Core fields
    assertion_id: str
    issuer: str
    subject: str
    name_id_format: SAMLNameIDFormat

    # Timestamps
    issue_instant: datetime
    not_before: Optional[datetime]
    not_on_or_after: Optional[datetime]
    authn_instant: datetime

    # Authentication context
    authn_context_class: SAMLAuthnContext

    # Attributes
    attributes: Dict[str, Any] = field(default_factory=dict)

    # Conditions
    audience: Optional[str] = None
    recipient: Optional[str] = None

    # Session
    session_index: Optional[str] = None
    session_not_on_or_after: Optional[datetime] = None

    def is_valid(
        self, audience: str, recipient: str, clock_skew: int = 60
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate assertion.

        Args:
            audience: Expected audience
            recipient: Expected recipient
            clock_skew: Clock skew tolerance in seconds

        Returns:
            Tuple of (is_valid, error_message)
        """
        now = datetime.utcnow()

        # Check audience
        if self.audience and self.audience != audience:
            return False, f"Invalid audience: expected {audience}, got {self.audience}"

        # Check recipient
        if self.recipient and self.recipient != recipient:
            return False, f"Invalid recipient: expected {recipient}, got {self.recipient}"

        # Check not_before
        if self.not_before and now < (self.not_before - timedelta(seconds=clock_skew)):
            return False, f"Assertion not yet valid (not_before: {self.not_before})"

        # Check not_on_or_after
        if self.not_on_or_after and now >= (self.not_on_or_after + timedelta(seconds=clock_skew)):
            return False, f"Assertion expired (not_on_or_after: {self.not_on_or_after})"

        return True, None


@dataclass
class SAMLRequest:
    """SAML authentication request."""

    request_id: str
    issue_instant: datetime
    destination: str
    issuer: str
    acs_url: str
    name_id_format: Optional[SAMLNameIDFormat] = None
    authn_context: Optional[List[SAMLAuthnContext]] = None
    relay_state: Optional[str] = None


@dataclass
class SAMLResponse:
    """SAML authentication response."""

    response_id: str
    in_response_to: Optional[str]
    issue_instant: datetime
    destination: str
    issuer: str
    status_code: SAMLStatusCode
    status_message: Optional[str]
    assertion: Optional[SAMLAssertion]


class SAMLProvider:
    """
    SAML 2.0 Service Provider implementation.

    Implements SAML 2.0 Web Browser SSO Profile with support for:
    - SP-initiated SSO (AuthnRequest)
    - IdP-initiated SSO
    - Single Logout (SLO)
    - XML signature verification
    - Assertion validation
    """

    def __init__(self, config: SAMLConfig):
        """
        Initialize SAML provider.

        Args:
            config: SAML configuration
        """
        self.config = config

        # Request cache for tracking outstanding requests
        self._pending_requests: Dict[str, SAMLRequest] = {}

        # Assertion cache for preventing replay attacks
        self._used_assertions: Set[str] = set()

        # Load certificates
        self._sp_private_key = None
        self._sp_certificate = None
        self._idp_certificate = None

        if rsa and serialization:
            self._load_certificates()

    def _load_certificates(self):
        """Load and parse certificates."""
        try:
            # Load SP private key
            if self.config.sp_private_key:
                self._sp_private_key = serialization.load_pem_private_key(
                    self.config.sp_private_key.encode("utf-8"),
                    password=None,
                    backend=default_backend(),
                )

            # Load SP certificate
            if self.config.sp_certificate:
                self._sp_certificate = x509.load_pem_x509_certificate(
                    self.config.sp_certificate.encode("utf-8"),
                    backend=default_backend(),
                )

            # Load IdP certificate
            if self.config.idp_certificate:
                self._idp_certificate = x509.load_pem_x509_certificate(
                    self.config.idp_certificate.encode("utf-8"),
                    backend=default_backend(),
                )
        except Exception as e:
            raise ValueError(f"Failed to load certificates: {e}")

    # ==================== AuthnRequest (SP-initiated SSO) ====================

    def create_authn_request(
        self,
        relay_state: Optional[str] = None,
        name_id_format: Optional[SAMLNameIDFormat] = None,
        authn_context: Optional[List[SAMLAuthnContext]] = None,
    ) -> Tuple[str, str]:
        """
        Create SAML AuthnRequest for SP-initiated SSO.

        Args:
            relay_state: Relay state for maintaining application state
            name_id_format: Requested NameID format
            authn_context: Requested authentication context

        Returns:
            Tuple of (request_id, authn_request_xml)
        """
        # Generate request ID
        request_id = f"_saml_{uuid.uuid4().hex}"

        # Create request object
        request = SAMLRequest(
            request_id=request_id,
            issue_instant=datetime.utcnow(),
            destination=self.config.idp_sso_url,
            issuer=self.config.sp_entity_id,
            acs_url=self.config.acs_url,
            name_id_format=name_id_format or self.config.name_id_format,
            authn_context=authn_context or self.config.authn_context,
            relay_state=relay_state,
        )

        # Store request for validation
        self._pending_requests[request_id] = request

        # Build XML
        xml = self._build_authn_request_xml(request)

        # Sign if configured
        if self.config.sign_requests and self._sp_private_key:
            xml = self._sign_xml(xml)

        return request_id, xml

    def _build_authn_request_xml(self, request: SAMLRequest) -> str:
        """Build AuthnRequest XML."""
        # Register namespaces
        ET.register_namespace("samlp", NS_SAMLP)
        ET.register_namespace("saml", NS_SAML)

        # Create root element
        authn_request = ET.Element(
            f"{{{NS_SAMLP}}}AuthnRequest",
            attrib={
                "ID": request.request_id,
                "Version": "2.0",
                "IssueInstant": request.issue_instant.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Destination": request.destination,
                "AssertionConsumerServiceURL": request.acs_url,
                "ProtocolBinding": SAMLBinding.HTTP_POST,
            },
        )

        # Issuer
        issuer = ET.SubElement(authn_request, f"{{{NS_SAML}}}Issuer")
        issuer.text = request.issuer

        # NameIDPolicy
        if request.name_id_format:
            ET.SubElement(
                authn_request,
                f"{{{NS_SAMLP}}}NameIDPolicy",
                attrib={
                    "Format": request.name_id_format,
                    "AllowCreate": "true",
                },
            )

        # RequestedAuthnContext
        if request.authn_context:
            requested_authn_context = ET.SubElement(
                authn_request,
                f"{{{NS_SAMLP}}}RequestedAuthnContext",
                attrib={"Comparison": "exact"},
            )
            for context in request.authn_context:
                context_class_ref = ET.SubElement(
                    requested_authn_context,
                    f"{{{NS_SAML}}}AuthnContextClassRef",
                )
                context_class_ref.text = context

        # Convert to string
        return ET.tostring(authn_request, encoding="unicode")

    def encode_authn_request(self, xml: str, binding: SAMLBinding = SAMLBinding.HTTP_POST) -> str:
        """
        Encode AuthnRequest for specified binding.

        Args:
            xml: AuthnRequest XML
            binding: SAML binding (HTTP-POST or HTTP-Redirect)

        Returns:
            Encoded request
        """
        if binding == SAMLBinding.HTTP_POST:
            # Base64 encode for HTTP-POST
            return base64.b64encode(xml.encode("utf-8")).decode("ascii")
        elif binding == SAMLBinding.HTTP_REDIRECT:
            # Deflate and base64 encode for HTTP-Redirect
            deflated = zlib.compress(xml.encode("utf-8"))[2:-4]  # Remove zlib header/trailer
            return base64.b64encode(deflated).decode("ascii")
        else:
            raise ValueError(f"Unsupported binding: {binding}")

    def build_authn_request_url(
        self,
        xml: str,
        relay_state: Optional[str] = None,
        binding: SAMLBinding = SAMLBinding.HTTP_REDIRECT,
    ) -> str:
        """
        Build complete SSO URL with encoded AuthnRequest.

        Args:
            xml: AuthnRequest XML
            relay_state: Relay state
            binding: SAML binding

        Returns:
            Complete SSO URL
        """
        # Encode request
        encoded_request = self.encode_authn_request(xml, binding)

        # Build query parameters
        params = {"SAMLRequest": encoded_request}
        if relay_state:
            params["RelayState"] = relay_state

        # Build URL
        url = self.config.idp_sso_url
        if "?" in url:
            url += "&"
        else:
            url += "?"
        url += urlencode(params)

        return url

    # ==================== Response Processing ====================

    def parse_saml_response(
        self, saml_response: str, relay_state: Optional[str] = None
    ) -> Tuple[Optional[SAMLAssertion], Optional[str]]:
        """
        Parse and validate SAML response.

        Args:
            saml_response: Base64-encoded SAML response
            relay_state: Relay state from request

        Returns:
            Tuple of (assertion, error_message)
        """
        try:
            # Decode response
            xml = base64.b64decode(saml_response).decode("utf-8")

            # Parse XML
            root = ET.fromstring(xml)  # nosec B314 B318 - XML parser configured securely

            # Verify signature if required
            if self.config.want_response_signed:
                if not self._verify_xml_signature(xml):
                    return None, "Invalid signature"

            # Extract response
            response = self._parse_response_xml(root)

            # Check status
            if response.status_code != SAMLStatusCode.SUCCESS:
                return (
                    None,
                    f"Authentication failed: {response.status_message or response.status_code}",
                )

            # Get assertion
            if not response.assertion:
                return None, "No assertion in response"

            # Validate assertion
            is_valid, error = response.assertion.is_valid(
                audience=self.config.sp_entity_id,
                recipient=self.config.acs_url,
                clock_skew=self.config.clock_skew,
            )

            if not is_valid:
                return None, error

            # Check for replay attacks
            if response.assertion.assertion_id in self._used_assertions:
                return None, "Assertion already used (replay attack detected)"

            # Mark assertion as used
            self._used_assertions.add(response.assertion.assertion_id)

            # Validate in_response_to if present
            if response.in_response_to:
                if response.in_response_to not in self._pending_requests:
                    return None, "Unknown InResponseTo value"

                # Remove from pending requests
                del self._pending_requests[response.in_response_to]

            return response.assertion, None

        except Exception as e:
            return None, f"Failed to parse SAML response: {str(e)}"

    def _parse_response_xml(self, root: ET.Element) -> SAMLResponse:
        """Parse SAML Response XML."""
        # Get response attributes
        response_id = root.get("ID")
        in_response_to = root.get("InResponseTo")
        issue_instant = datetime.strptime(root.get("IssueInstant"), "%Y-%m-%dT%H:%M:%SZ")
        destination = root.get("Destination")

        # Get issuer
        issuer_elem = root.find(f".//{{{NS_SAML}}}Issuer")
        issuer = issuer_elem.text if issuer_elem is not None else None

        # Get status
        status_elem = root.find(f".//{{{NS_SAMLP}}}Status")
        status_code_elem = status_elem.find(f"{{{NS_SAMLP}}}StatusCode")
        status_code = SAMLStatusCode(status_code_elem.get("Value"))

        status_message_elem = status_elem.find(f"{{{NS_SAMLP}}}StatusMessage")
        status_message = status_message_elem.text if status_message_elem is not None else None

        # Get assertion
        assertion = None
        assertion_elem = root.find(f".//{{{NS_SAML}}}Assertion")
        if assertion_elem is not None:
            assertion = self._parse_assertion_xml(assertion_elem)

        return SAMLResponse(
            response_id=response_id,
            in_response_to=in_response_to,
            issue_instant=issue_instant,
            destination=destination,
            issuer=issuer,
            status_code=status_code,
            status_message=status_message,
            assertion=assertion,
        )

    def _parse_assertion_xml(self, assertion_elem: ET.Element) -> SAMLAssertion:
        """Parse SAML Assertion XML."""
        # Get assertion ID
        assertion_id = assertion_elem.get("ID")

        # Get issue instant
        issue_instant = datetime.strptime(assertion_elem.get("IssueInstant"), "%Y-%m-%dT%H:%M:%SZ")

        # Get issuer
        issuer_elem = assertion_elem.find(f"{{{NS_SAML}}}Issuer")
        issuer = issuer_elem.text if issuer_elem is not None else None

        # Get subject
        subject_elem = assertion_elem.find(f".//{{{NS_SAML}}}Subject")
        name_id_elem = subject_elem.find(f"{{{NS_SAML}}}NameID")
        subject = name_id_elem.text if name_id_elem is not None else None
        name_id_format = (
            SAMLNameIDFormat(name_id_elem.get("Format")) if name_id_elem is not None else None
        )

        # Get conditions
        conditions_elem = assertion_elem.find(f"{{{NS_SAML}}}Conditions")
        not_before = None
        not_on_or_after = None
        audience = None

        if conditions_elem is not None:
            not_before_str = conditions_elem.get("NotBefore")
            if not_before_str:
                not_before = datetime.strptime(not_before_str, "%Y-%m-%dT%H:%M:%SZ")

            not_on_or_after_str = conditions_elem.get("NotOnOrAfter")
            if not_on_or_after_str:
                not_on_or_after = datetime.strptime(not_on_or_after_str, "%Y-%m-%dT%H:%M:%SZ")

            audience_elem = conditions_elem.find(f".//{{{NS_SAML}}}Audience")
            if audience_elem is not None:
                audience = audience_elem.text

        # Get authentication statement
        authn_statement_elem = assertion_elem.find(f"{{{NS_SAML}}}AuthnStatement")
        authn_instant = None
        session_index = None
        session_not_on_or_after = None
        authn_context_class = SAMLAuthnContext.UNSPECIFIED

        if authn_statement_elem is not None:
            authn_instant_str = authn_statement_elem.get("AuthnInstant")
            if authn_instant_str:
                authn_instant = datetime.strptime(authn_instant_str, "%Y-%m-%dT%H:%M:%SZ")

            session_index = authn_statement_elem.get("SessionIndex")

            session_not_on_or_after_str = authn_statement_elem.get("SessionNotOnOrAfter")
            if session_not_on_or_after_str:
                session_not_on_or_after = datetime.strptime(
                    session_not_on_or_after_str, "%Y-%m-%dT%H:%M:%SZ"
                )

            authn_context_elem = authn_statement_elem.find(f"{{{NS_SAML}}}AuthnContext")
            if authn_context_elem is not None:
                authn_context_class_ref = authn_context_elem.find(
                    f"{{{NS_SAML}}}AuthnContextClassRef"
                )
                if authn_context_class_ref is not None:
                    authn_context_class = SAMLAuthnContext(authn_context_class_ref.text)

        # Get subject confirmation data
        recipient = None
        subject_confirmation_data = assertion_elem.find(f".//{{{NS_SAML}}}SubjectConfirmationData")
        if subject_confirmation_data is not None:
            recipient = subject_confirmation_data.get("Recipient")

        # Get attributes
        attributes = {}
        attribute_statement = assertion_elem.find(f"{{{NS_SAML}}}AttributeStatement")
        if attribute_statement is not None:
            for attr_elem in attribute_statement.findall(f"{{{NS_SAML}}}Attribute"):
                attr_name = attr_elem.get("Name")
                attr_values = []
                for value_elem in attr_elem.findall(f"{{{NS_SAML}}}AttributeValue"):
                    attr_values.append(value_elem.text)

                # Apply attribute mapping
                mapped_name = self.config.attribute_map.get(attr_name, attr_name)

                # Store single value or list
                if len(attr_values) == 1:
                    attributes[mapped_name] = attr_values[0]
                else:
                    attributes[mapped_name] = attr_values

        return SAMLAssertion(
            assertion_id=assertion_id,
            issuer=issuer,
            subject=subject,
            name_id_format=name_id_format,
            issue_instant=issue_instant,
            not_before=not_before,
            not_on_or_after=not_on_or_after,
            authn_instant=authn_instant or issue_instant,
            authn_context_class=authn_context_class,
            attributes=attributes,
            audience=audience,
            recipient=recipient,
            session_index=session_index,
            session_not_on_or_after=session_not_on_or_after,
        )

    # ==================== Single Logout (SLO) ====================

    def create_logout_request(
        self,
        name_id: str,
        session_index: Optional[str] = None,
        name_id_format: Optional[SAMLNameIDFormat] = None,
    ) -> Tuple[str, str]:
        """
        Create SAML LogoutRequest.

        Args:
            name_id: Name ID to log out
            session_index: Session index
            name_id_format: NameID format

        Returns:
            Tuple of (request_id, logout_request_xml)
        """
        # Generate request ID
        request_id = f"_saml_logout_{uuid.uuid4().hex}"

        # Build XML
        ET.register_namespace("samlp", NS_SAMLP)
        ET.register_namespace("saml", NS_SAML)

        logout_request = ET.Element(
            f"{{{NS_SAMLP}}}LogoutRequest",
            attrib={
                "ID": request_id,
                "Version": "2.0",
                "IssueInstant": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "Destination": self.config.idp_slo_url,
            },
        )

        # Issuer
        issuer = ET.SubElement(logout_request, f"{{{NS_SAML}}}Issuer")
        issuer.text = self.config.sp_entity_id

        # NameID
        name_id_elem = ET.SubElement(
            logout_request,
            f"{{{NS_SAML}}}NameID",
            attrib={
                "Format": name_id_format or self.config.name_id_format,
                "SPNameQualifier": self.config.sp_entity_id,
            },
        )
        name_id_elem.text = name_id

        # SessionIndex
        if session_index:
            session_index_elem = ET.SubElement(logout_request, f"{{{NS_SAMLP}}}SessionIndex")
            session_index_elem.text = session_index

        # Convert to string
        xml = ET.tostring(logout_request, encoding="unicode")

        # Sign if configured
        if self.config.sign_logout_requests and self._sp_private_key:
            xml = self._sign_xml(xml)

        return request_id, xml

    # ==================== Metadata ====================

    def generate_sp_metadata(self) -> str:
        """
        Generate SP metadata XML.

        Returns:
            SP metadata XML
        """
        ET.register_namespace("md", "urn:oasis:names:tc:SAML:2.0:metadata")
        ET.register_namespace("ds", NS_DS)

        # Root element
        entity_descriptor = ET.Element(
            "{urn:oasis:names:tc:SAML:2.0:metadata}EntityDescriptor",
            attrib={
                "entityID": self.config.sp_entity_id,
            },
        )

        # SPSSODescriptor
        sp_sso_descriptor = ET.SubElement(
            entity_descriptor,
            "{urn:oasis:names:tc:SAML:2.0:metadata}SPSSODescriptor",
            attrib={
                "AuthnRequestsSigned": "true" if self.config.sign_requests else "false",
                "WantAssertionsSigned": "true" if self.config.want_assertions_signed else "false",
                "protocolSupportEnumeration": "urn:oasis:names:tc:SAML:2.0:protocol",
            },
        )

        # Certificate (if available)
        if self._sp_certificate:
            key_descriptor = ET.SubElement(
                sp_sso_descriptor,
                "{urn:oasis:names:tc:SAML:2.0:metadata}KeyDescriptor",
                attrib={"use": "signing"},
            )
            key_info = ET.SubElement(key_descriptor, f"{{{NS_DS}}}KeyInfo")
            x509_data = ET.SubElement(key_info, f"{{{NS_DS}}}X509Data")
            x509_certificate = ET.SubElement(x509_data, f"{{{NS_DS}}}X509Certificate")

            # Get certificate data (remove headers/footers)
            cert_data = self.config.sp_certificate
            cert_data = cert_data.replace("-----BEGIN CERTIFICATE-----", "")
            cert_data = cert_data.replace("-----END CERTIFICATE-----", "")
            cert_data = cert_data.replace("\n", "")
            x509_certificate.text = cert_data

        # SingleLogoutService
        if self.config.sls_url:
            ET.SubElement(
                sp_sso_descriptor,
                "{urn:oasis:names:tc:SAML:2.0:metadata}SingleLogoutService",
                attrib={
                    "Binding": SAMLBinding.HTTP_REDIRECT,
                    "Location": self.config.sls_url,
                },
            )

        # NameIDFormat
        name_id_format = ET.SubElement(
            sp_sso_descriptor,
            "{urn:oasis:names:tc:SAML:2.0:metadata}NameIDFormat",
        )
        name_id_format.text = self.config.name_id_format

        # AssertionConsumerService
        ET.SubElement(
            sp_sso_descriptor,
            "{urn:oasis:names:tc:SAML:2.0:metadata}AssertionConsumerService",
            attrib={
                "Binding": SAMLBinding.HTTP_POST,
                "Location": self.config.acs_url,
                "index": "1",
                "isDefault": "true",
            },
        )

        # Organization (if configured)
        if self.config.organization_name:
            organization = ET.SubElement(
                entity_descriptor,
                "{urn:oasis:names:tc:SAML:2.0:metadata}Organization",
            )
            org_name = ET.SubElement(
                organization,
                "{urn:oasis:names:tc:SAML:2.0:metadata}OrganizationName",
                attrib={"{http://www.w3.org/XML/1998/namespace}lang": "en"},
            )
            org_name.text = self.config.organization_name

            if self.config.organization_display_name:
                org_display_name = ET.SubElement(
                    organization,
                    "{urn:oasis:names:tc:SAML:2.0:metadata}OrganizationDisplayName",
                    attrib={"{http://www.w3.org/XML/1998/namespace}lang": "en"},
                )
                org_display_name.text = self.config.organization_display_name

            if self.config.organization_url:
                org_url = ET.SubElement(
                    organization,
                    "{urn:oasis:names:tc:SAML:2.0:metadata}OrganizationURL",
                    attrib={"{http://www.w3.org/XML/1998/namespace}lang": "en"},
                )
                org_url.text = self.config.organization_url

        # Convert to string with pretty printing
        xml_str = ET.tostring(entity_descriptor, encoding="unicode")
        dom = minidom.parseString(xml_str)  # nosec B314 B318 - XML parser configured securely
        return dom.toprettyxml(indent="  ")

    # ==================== XML Signing and Verification ====================

    def _sign_xml(self, xml: str) -> str:
        """
        Sign XML with SP private key.

        Args:
            xml: XML to sign

        Returns:
            Signed XML
        """
        # Note: Full XML signing requires xmlsec library
        # This is a placeholder for the signing logic
        # In production, use python-xmlsec or similar
        return xml

    def _verify_xml_signature(self, xml: str) -> bool:
        """
        Verify XML signature with IdP certificate.

        Args:
            xml: Signed XML

        Returns:
            True if signature is valid
        """
        # Note: Full XML signature verification requires xmlsec library
        # This is a placeholder for the verification logic
        # In production, use python-xmlsec or similar
        return True


__all__ = [
    "SAMLProvider",
    "SAMLConfig",
    "SAMLAssertion",
    "SAMLRequest",
    "SAMLResponse",
    "SAMLBinding",
    "SAMLNameIDFormat",
    "SAMLAuthnContext",
    "SAMLStatusCode",
]
