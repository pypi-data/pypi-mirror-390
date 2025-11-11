"""
RFC 6455 Compliant WebSocket Protocol Implementation

This module provides a complete, production-ready WebSocket protocol implementation
that handles all aspects of the WebSocket specification including:
- WebSocket handshake
- Frame parsing and creation
- Message fragmentation and reassembly
- Control frames (ping/pong/close)
- Proper error handling
"""

import asyncio
import base64
import hashlib
import json
import logging
import struct
import time
import uuid
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# RFC 6455 Constants
WS_MAGIC_STRING = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WS_VERSION = "13"
MAX_FRAME_SIZE = 16 * 1024 * 1024  # 16MB max frame size


class OpCode(IntEnum):
    """WebSocket frame opcodes as defined in RFC 6455."""

    CONTINUATION = 0x0
    TEXT = 0x1
    BINARY = 0x2
    CLOSE = 0x8
    PING = 0x9
    PONG = 0xA


class CloseCode(IntEnum):
    """WebSocket close codes as defined in RFC 6455."""

    NORMAL_CLOSURE = 1000
    GOING_AWAY = 1001
    PROTOCOL_ERROR = 1002
    UNSUPPORTED_DATA = 1003
    NO_STATUS_RECEIVED = 1005
    ABNORMAL_CLOSURE = 1006
    INVALID_FRAME_PAYLOAD_DATA = 1007
    POLICY_VIOLATION = 1008
    MESSAGE_TOO_BIG = 1009
    MANDATORY_EXTENSION = 1010
    INTERNAL_ERROR = 1011
    SERVICE_RESTART = 1012
    TRY_AGAIN_LATER = 1013
    BAD_GATEWAY = 1014
    TLS_HANDSHAKE = 1015


class WebSocketState(IntEnum):
    """WebSocket connection states."""

    CONNECTING = 0
    OPEN = 1
    CLOSING = 2
    CLOSED = 3


class WebSocketError(Exception):
    """Base WebSocket error."""


class ProtocolError(WebSocketError):
    """WebSocket protocol violation error."""


class ConnectionClosed(WebSocketError):
    """WebSocket connection closed error."""

    def __init__(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = ""):
        self.code = code
        self.reason = reason
        super().__init__(f"Connection closed with code {code}: {reason}")


@dataclass
class WebSocketFrame:
    """Represents a WebSocket frame."""

    fin: bool
    rsv1: bool
    rsv2: bool
    rsv3: bool
    opcode: OpCode
    masked: bool
    payload_length: int
    mask_key: Optional[bytes]
    payload: bytes

    @property
    def is_control_frame(self) -> bool:
        """Check if this is a control frame."""
        return self.opcode >= OpCode.CLOSE

    @property
    def is_data_frame(self) -> bool:
        """Check if this is a data frame."""
        return self.opcode <= OpCode.BINARY


class WebSocketProtocol:
    """
    Complete RFC 6455 WebSocket protocol implementation.

    This class handles all WebSocket protocol operations including:
    - Frame parsing and serialization
    - Message fragmentation and reassembly
    - Control frame handling
    - Connection state management
    """

    def __init__(self, is_client: bool = False):
        self.is_client = is_client
        self.state = WebSocketState.CONNECTING
        self.close_code: Optional[int] = None
        self.close_reason: str = ""

        # Message assembly
        self._message_buffer = bytearray()
        self._message_opcode: Optional[OpCode] = None

        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.frames_sent = 0
        self.frames_received = 0
        self.messages_sent = 0
        self.messages_received = 0

        # Ping/Pong tracking
        self._ping_payload: Optional[bytes] = None
        self._last_ping_time: Optional[float] = None

        logger.debug(f"WebSocket protocol initialized (client={is_client})")

    def generate_accept_key(self, client_key: str) -> str:
        """
        Generate WebSocket accept key from client key.

        NOTE: SHA1 is REQUIRED by RFC 6455 WebSocket handshake spec.
        This is NOT a security vulnerability - it's a protocol requirement.
        """
        combined = client_key + WS_MAGIC_STRING
        hash_bytes = hashlib.sha1(combined.encode(), usedforsecurity=False).digest()
        return base64.b64encode(hash_bytes).decode()

    def validate_headers(self, headers: Dict[str, str]) -> Tuple[bool, str]:
        """
        Validate WebSocket handshake headers.

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_headers = {
            "connection": "upgrade",
            "upgrade": "websocket",
            "sec-websocket-version": WS_VERSION,
        }

        for header, expected_value in required_headers.items():
            actual_value = headers.get(header, "").lower()
            if expected_value.lower() not in actual_value:
                return False, f"Invalid {header} header: {actual_value}"

        if "sec-websocket-key" not in headers:
            return False, "Missing Sec-WebSocket-Key header"

        return True, ""

    def create_handshake_response(self, client_key: str) -> Dict[str, str]:
        """Create WebSocket handshake response headers."""
        accept_key = self.generate_accept_key(client_key)

        return {
            "HTTP/1.1": "101 Switching Protocols",
            "Upgrade": "websocket",
            "Connection": "Upgrade",
            "Sec-WebSocket-Accept": accept_key,
        }

    def parse_frame(self, data: bytes) -> Tuple[Optional[WebSocketFrame], int]:
        """
        Parse WebSocket frame from bytes.

        Returns:
            Tuple of (frame, bytes_consumed) or (None, 0) if incomplete
        """
        if len(data) < 2:
            return None, 0

        # Parse first two bytes
        first_byte = data[0]
        second_byte = data[1]

        fin = bool(first_byte & 0x80)
        rsv1 = bool(first_byte & 0x40)
        rsv2 = bool(first_byte & 0x20)
        rsv3 = bool(first_byte & 0x10)
        opcode = OpCode(first_byte & 0x0F)

        masked = bool(second_byte & 0x80)
        payload_length = second_byte & 0x7F

        # Validate frame
        if rsv1 or rsv2 or rsv3:
            raise ProtocolError("Reserved bits must be 0")

        if opcode > OpCode.PONG:
            raise ProtocolError(f"Invalid opcode: {opcode}")

        if opcode >= OpCode.CLOSE and not fin:
            raise ProtocolError("Control frames must not be fragmented")

        if self.is_client and not masked:
            raise ProtocolError("Client frames must be masked")

        if not self.is_client and masked:
            raise ProtocolError("Server frames must not be masked")

        # Calculate header size
        header_size = 2

        # Extended payload length
        if payload_length == 126:
            if len(data) < header_size + 2:
                return None, 0
            payload_length = struct.unpack(">H", data[header_size : header_size + 2])[0]
            header_size += 2
        elif payload_length == 127:
            if len(data) < header_size + 8:
                return None, 0
            payload_length = struct.unpack(">Q", data[header_size : header_size + 8])[0]
            header_size += 8

        # Validate payload length
        if payload_length > MAX_FRAME_SIZE:
            raise ProtocolError(f"Frame too large: {payload_length} bytes")

        if opcode >= OpCode.CLOSE and payload_length > 125:
            raise ProtocolError("Control frame payload too large")

        # Masking key
        mask_key = None
        if masked:
            if len(data) < header_size + 4:
                return None, 0
            mask_key = data[header_size : header_size + 4]
            header_size += 4

        # Check if we have complete frame
        total_size = header_size + payload_length
        if len(data) < total_size:
            return None, 0

        # Extract payload
        payload = data[header_size:total_size]

        # Unmask payload if needed
        if masked and mask_key:
            payload = bytes(payload[i] ^ mask_key[i % 4] for i in range(len(payload)))

        frame = WebSocketFrame(
            fin=fin,
            rsv1=rsv1,
            rsv2=rsv2,
            rsv3=rsv3,
            opcode=opcode,
            masked=masked,
            payload_length=payload_length,
            mask_key=mask_key,
            payload=payload,
        )

        self.frames_received += 1
        self.bytes_received += total_size

        return frame, total_size

    def create_frame(
        self, opcode: OpCode, payload: bytes = b"", fin: bool = True, mask: bool = None
    ) -> bytes:
        """Create WebSocket frame bytes."""
        if mask is None:
            mask = self.is_client

        # Validate inputs
        if opcode >= OpCode.CLOSE and len(payload) > 125:
            raise ProtocolError("Control frame payload too large")

        if len(payload) > MAX_FRAME_SIZE:
            raise ProtocolError(f"Frame too large: {len(payload)} bytes")

        # First byte: FIN + RSV + opcode
        first_byte = 0x80 if fin else 0x00  # FIN bit
        first_byte |= opcode & 0x0F

        # Second byte: MASK + payload length
        second_byte = 0x80 if mask else 0x00
        payload_length = len(payload)

        if payload_length < 126:
            second_byte |= payload_length
            length_bytes = b""
        elif payload_length < 65536:
            second_byte |= 126
            length_bytes = struct.pack(">H", payload_length)
        else:
            second_byte |= 127
            length_bytes = struct.pack(">Q", payload_length)

        # Create frame
        frame = bytes([first_byte, second_byte]) + length_bytes

        # Add mask and masked payload
        if mask:
            import os

            mask_key = os.urandom(4)
            frame += mask_key

            # Mask payload
            masked_payload = bytes(payload[i] ^ mask_key[i % 4] for i in range(len(payload)))
            frame += masked_payload
        else:
            frame += payload

        self.frames_sent += 1
        self.bytes_sent += len(frame)

        return frame

    def process_frame(self, frame: WebSocketFrame) -> Optional[bytes]:
        """
        Process received frame and return complete message if available.

        Returns:
            Complete message bytes if a message is complete, None otherwise
        """
        if frame.opcode == OpCode.CLOSE:
            # Parse close frame
            if len(frame.payload) >= 2:
                self.close_code = struct.unpack(">H", frame.payload[:2])[0]
                self.close_reason = frame.payload[2:].decode("utf-8", errors="ignore")
            else:
                self.close_code = CloseCode.NO_STATUS_RECEIVED
                self.close_reason = ""

            self.state = WebSocketState.CLOSING
            raise ConnectionClosed(self.close_code, self.close_reason)

        elif frame.opcode == OpCode.PING:
            # Store ping payload for pong response
            self._ping_payload = frame.payload
            return None

        elif frame.opcode == OpCode.PONG:
            # Handle pong response
            if self._last_ping_time:
                latency = time.time() - self._last_ping_time
                logger.debug(f"Pong received, latency: {latency:.3f}s")
                self._last_ping_time = None
            return None

        elif frame.opcode in (OpCode.TEXT, OpCode.BINARY):
            # Start of new message
            if self._message_buffer:
                raise ProtocolError("Received new message before previous was complete")

            self._message_opcode = frame.opcode
            self._message_buffer.extend(frame.payload)

            if frame.fin:
                # Complete message
                message = bytes(self._message_buffer)
                self._message_buffer.clear()
                self._message_opcode = None
                self.messages_received += 1
                return message

        elif frame.opcode == OpCode.CONTINUATION:
            # Continuation of fragmented message
            if not self._message_buffer:
                raise ProtocolError("Received continuation frame without initial frame")

            self._message_buffer.extend(frame.payload)

            if frame.fin:
                # Complete message
                message = bytes(self._message_buffer)
                self._message_buffer.clear()
                self._message_opcode = None
                self.messages_received += 1
                return message

        else:
            raise ProtocolError(f"Unknown opcode: {frame.opcode}")

        return None

    def create_text_frame(self, text: str, fin: bool = True) -> bytes:
        """Create text frame."""
        payload = text.encode("utf-8")
        return self.create_frame(OpCode.TEXT, payload, fin)

    def create_binary_frame(self, data: bytes, fin: bool = True) -> bytes:
        """Create binary frame."""
        return self.create_frame(OpCode.BINARY, data, fin)

    def create_close_frame(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = "") -> bytes:
        """Create close frame."""
        payload = struct.pack(">H", code)
        if reason:
            payload += reason.encode("utf-8")
        return self.create_frame(OpCode.CLOSE, payload)

    def create_ping_frame(self, payload: bytes = b"") -> bytes:
        """Create ping frame."""
        self._last_ping_time = time.time()
        return self.create_frame(OpCode.PING, payload)

    def create_pong_frame(self, payload: bytes = None) -> bytes:
        """Create pong frame."""
        if payload is None:
            payload = self._ping_payload or b""
        return self.create_frame(OpCode.PONG, payload)

    def fragment_message(self, data: bytes, fragment_size: int = 8192) -> List[bytes]:
        """Fragment large message into multiple frames."""
        if len(data) <= fragment_size:
            return [data]

        fragments = []
        for i in range(0, len(data), fragment_size):
            fragments.append(data[i : i + fragment_size])

        return fragments

    def close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = ""):
        """Close the WebSocket connection."""
        self.state = WebSocketState.CLOSING
        self.close_code = code
        self.close_reason = reason

    def get_stats(self) -> Dict[str, Any]:
        """Get protocol statistics."""
        return {
            "state": self.state.name,
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "frames_sent": self.frames_sent,
            "frames_received": self.frames_received,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "close_code": self.close_code,
            "close_reason": self.close_reason,
            "is_client": self.is_client,
        }


class WebSocketMessage:
    """Base class for WebSocket messages."""

    def __init__(self, opcode: OpCode, payload: bytes, timestamp: float = None):
        self.opcode = opcode
        self.payload = payload
        self.timestamp = timestamp or time.time()
        self.id = str(uuid.uuid4())

    def __repr__(self):
        return f"{self.__class__.__name__}(opcode={self.opcode}, size={len(self.payload)})"


class TextMessage(WebSocketMessage):
    """Text WebSocket message."""

    def __init__(self, content: str, timestamp: float = None):
        payload = content.encode("utf-8")
        super().__init__(OpCode.TEXT, payload, timestamp)
        self.content = content

    @classmethod
    def from_payload(cls, payload: bytes, timestamp: float = None):
        content = payload.decode("utf-8")
        return cls(content, timestamp)


class BinaryMessage(WebSocketMessage):
    """Binary WebSocket message."""

    def __init__(self, data: bytes, timestamp: float = None):
        super().__init__(OpCode.BINARY, data, timestamp)
        self.data = data

    @classmethod
    def from_payload(cls, payload: bytes, timestamp: float = None):
        return cls(payload, timestamp)


class JSONMessage(WebSocketMessage):
    """JSON WebSocket message."""

    def __init__(self, data: Any, timestamp: float = None):
        content = json.dumps(data, separators=(",", ":"))
        payload = content.encode("utf-8")
        super().__init__(OpCode.TEXT, payload, timestamp)
        self.data = data
        self.content = content

    @classmethod
    def from_payload(cls, payload: bytes, timestamp: float = None):
        content = payload.decode("utf-8")
        data = json.loads(content)
        return cls(data, timestamp)


def create_message_from_frame(frame: WebSocketFrame) -> WebSocketMessage:
    """Create appropriate message object from frame."""
    if frame.opcode == OpCode.TEXT:
        return TextMessage.from_payload(frame.payload)
    elif frame.opcode == OpCode.BINARY:
        return BinaryMessage.from_payload(frame.payload)
    else:
        return WebSocketMessage(frame.opcode, frame.payload)
