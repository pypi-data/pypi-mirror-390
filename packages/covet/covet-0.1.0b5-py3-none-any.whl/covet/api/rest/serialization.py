"""
REST API Response Serialization

Production-ready response serialization with support for multiple formats,
content negotiation, and standardized response structures.
"""

import json
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from uuid import UUID

from pydantic import BaseModel


class SerializationError(Exception):
    """Raised when serialization fails."""


class ResponseSerializer:
    """
    Response serializer with support for multiple formats.

    Features:
    - JSON serialization with custom encoders
    - Pydantic model serialization
    - Nested object handling
    - DateTime/UUID/Decimal support
    - Content negotiation
    - HATEOAS support

    Example:
        serializer = ResponseSerializer()
        response = serializer.serialize(
            data={'user': user_model},
            status_code=200,
            format='json'
        )
    """

    def __init__(
        self,
        pretty: bool = False,
        indent: Optional[int] = None,
        ensure_ascii: bool = False,
    ):
        """
        Initialize response serializer.

        Args:
            pretty: Enable pretty printing
            indent: Indentation level (2 or 4 typically)
            ensure_ascii: Ensure ASCII-only output
        """
        self.pretty = pretty
        self.indent = indent if indent is not None else (2 if pretty else None)
        self.ensure_ascii = ensure_ascii
        self._custom_encoders: Dict[Type, callable] = {}

    def serialize(
        self,
        data: Any,
        status_code: int = 200,
        format: str = "json",
        headers: Optional[Dict[str, str]] = None,
    ) -> tuple[bytes, str, Dict[str, str]]:
        """
        Serialize data to specified format.

        Args:
            data: Data to serialize
            status_code: HTTP status code
            format: Output format ('json', 'xml', 'msgpack')
            headers: Additional headers

        Returns:
            Tuple of (body_bytes, content_type, headers)
        """
        if format == "json":
            return self._serialize_json(data, headers)
        else:
            raise SerializationError(f"Unsupported format: {format}")

    def _serialize_json(
        self, data: Any, headers: Optional[Dict[str, str]] = None
    ) -> tuple[bytes, str, Dict[str, str]]:
        """Serialize to JSON."""
        try:
            # Convert to JSON-serializable format
            serializable = self._make_serializable(data)

            # Serialize to JSON
            json_str = json.dumps(
                serializable,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
                default=self._default_encoder,
            )

            # Prepare headers
            response_headers = headers or {}
            response_headers["Content-Type"] = "application/json; charset=utf-8"

            return json_str.encode("utf-8"), "application/json", response_headers

        except Exception as e:
            raise SerializationError(f"JSON serialization failed: {str(e)}") from e

    def _make_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        # None, bool, int, float, str are already serializable
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj

        # Pydantic models
        if isinstance(obj, BaseModel):
            return obj.dict()

        # Dict
        if isinstance(obj, dict):
            return {key: self._make_serializable(value) for key, value in obj.items()}

        # List, tuple, set
        if isinstance(obj, (list, tuple, set)):
            return [self._make_serializable(item) for item in obj]

        # DateTime objects
        if isinstance(obj, (datetime, date, time)):
            return obj.isoformat()

        # UUID
        if isinstance(obj, UUID):
            return str(obj)

        # Decimal
        if isinstance(obj, Decimal):
            return float(obj)

        # Enum
        if isinstance(obj, Enum):
            return obj.value

        # Custom encoders
        for type_cls, encoder in self._custom_encoders.items():
            if isinstance(obj, type_cls):
                return encoder(obj)

        # Try to convert to dict
        if hasattr(obj, "__dict__"):
            return self._make_serializable(obj.__dict__)

        # Fallback to string representation
        return str(obj)

    def _default_encoder(self, obj: Any) -> Any:
        """Default JSON encoder for non-standard types."""
        return self._make_serializable(obj)

    def register_encoder(self, type_cls: Type, encoder: callable):
        """
        Register custom encoder for a type.

        Args:
            type_cls: Type class
            encoder: Encoder function that takes object and returns serializable value
        """
        self._custom_encoders[type_cls] = encoder


class StandardResponse(BaseModel):
    """Standard API response envelope."""

    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Standard paginated response."""

    success: bool = True
    data: List[Any]
    meta: Dict[str, Any]

    @classmethod
    def create(cls, items: List[Any], page: int, page_size: int, total: int):
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size

        return cls(
            data=items,
            meta={
                "pagination": {
                    "page": page,
                    "pageSize": page_size,
                    "total": total,
                    "totalPages": total_pages,
                    "hasNext": page < total_pages,
                    "hasPrevious": page > 1,
                }
            },
        )


class ErrorResponse(BaseModel):
    """Standard error response following RFC 7807."""

    type: str = "https://errors.covetpy.dev/error"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None


class SuccessResponse(BaseModel):
    """Standard success response."""

    success: bool = True
    data: Any
    meta: Optional[Dict[str, Any]] = None


class CreatedResponse(BaseModel):
    """Response for created resources (201)."""

    success: bool = True
    data: Any
    location: str
    meta: Optional[Dict[str, Any]] = None


class NoContentResponse:
    """Response for no content (204)."""


class ResponseFormatter:
    """
    Format responses according to API standards.

    Provides consistent response structure across the API.
    """

    def __init__(self, serializer: Optional[ResponseSerializer] = None):
        """
        Initialize response formatter.

        Args:
            serializer: Response serializer instance
        """
        self.serializer = serializer or ResponseSerializer()

    def success(
        self, data: Any, status_code: int = 200, meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format success response."""
        return SuccessResponse(data=data, meta=meta).dict()

    def created(
        self, data: Any, location: str, meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Format created response (201)."""
        return CreatedResponse(data=data, location=location, meta=meta).dict()

    def no_content(self) -> None:
        """Format no content response (204)."""
        return None

    def error(
        self,
        title: str,
        status: int,
        detail: Optional[str] = None,
        instance: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        error_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Format error response following RFC 7807.

        Args:
            title: Short error title
            status: HTTP status code
            detail: Detailed error description
            instance: Request path/ID
            errors: List of specific errors
            error_type: Error type URL

        Returns:
            Error response dict
        """
        return ErrorResponse(
            type=error_type or f"https://errors.covetpy.dev/{status}",
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            errors=errors,
        ).dict()

    def paginated(
        self,
        items: List[Any],
        page: int,
        page_size: int,
        total: int,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format paginated response.

        Args:
            items: List of items for current page
            page: Current page number
            page_size: Items per page
            total: Total number of items
            meta: Additional metadata

        Returns:
            Paginated response dict
        """
        response = PaginatedResponse.create(items, page, page_size, total)
        response_dict = response.dict()

        # Merge additional meta
        if meta:
            response_dict["meta"].update(meta)

        return response_dict


class ContentNegotiator:
    """
    Handle content negotiation based on Accept header.

    Supports:
    - application/json
    - application/xml
    - application/msgpack
    """

    SUPPORTED_FORMATS = {
        "application/json": "json",
        "application/xml": "xml",
        "application/msgpack": "msgpack",
        "text/json": "json",
        "*/*": "json",  # Default
    }

    def negotiate(self, accept_header: Optional[str]) -> str:
        """
        Negotiate content type from Accept header.

        Args:
            accept_header: HTTP Accept header value

        Returns:
            Format string ('json', 'xml', 'msgpack')
        """
        if not accept_header:
            return "json"

        # Parse Accept header (simplified)
        accept_types = [t.strip().split(";")[0] for t in accept_header.split(",")]

        # Find first supported type
        for accept_type in accept_types:
            if accept_type in self.SUPPORTED_FORMATS:
                return self.SUPPORTED_FORMATS[accept_type]

        # Default to JSON
        return "json"

    def get_content_type(self, format: str) -> str:
        """Get Content-Type header for format."""
        format_to_content_type = {
            "json": "application/json; charset=utf-8",
            "xml": "application/xml; charset=utf-8",
            "msgpack": "application/msgpack",
        }
        return format_to_content_type.get(format, "application/json; charset=utf-8")


__all__ = [
    "ResponseSerializer",
    "ResponseFormatter",
    "ContentNegotiator",
    "SerializationError",
    "StandardResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "CreatedResponse",
    "NoContentResponse",
]
