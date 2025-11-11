"""
REST API Pagination Strategies

Production-grade pagination with multiple strategies:
- Offset-based pagination (page=1&limit=20)
- Cursor-based pagination (cursor=xyz, better performance)
- Keyset pagination (last_id=123, most efficient)

Features:
- Automatic pagination metadata
- Link headers (RFC 5988)
- Total count support (optional)
- Performance optimized for large datasets
- Database adapter integration

Example:
    from covet.api.rest.pagination import OffsetPaginator, CursorPaginator
    from covet.database.orm import User

    # Offset pagination
    paginator = OffsetPaginator(page=1, page_size=20)
    result = await paginator.paginate(User.objects.filter(is_active=True))

    # Returns:
    # {
    #     "items": [...],
    #     "pagination": {
    #         "page": 1,
    #         "page_size": 20,
    #         "total_pages": 5,
    #         "total_items": 100,
    #         "has_next": True,
    #         "has_previous": False
    #     },
    #     "links": {
    #         "first": "/api/users?page=1",
    #         "last": "/api/users?page=5",
    #         "next": "/api/users?page=2",
    #         "previous": None
    #     }
    # }

    # Cursor pagination (better performance)
    paginator = CursorPaginator(cursor=None, page_size=20)
    result = await paginator.paginate(User.objects.order_by('-created_at'))

    # Returns:
    # {
    #     "items": [...],
    #     "pagination": {
    #         "page_size": 20,
    #         "has_next": True,
    #         "has_previous": False,
    #         "next_cursor": "eyJjcmVhdGVkX2F0IjogIjIwMjUtMTAt...",
    #         "previous_cursor": None
    #     }
    # }
"""

import base64
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Type
from urllib.parse import parse_qs, urlencode, urlparse

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class PaginationStyle(str):
    """Pagination strategy types."""

    OFFSET = "offset"  # Traditional page-based
    CURSOR = "cursor"  # Cursor-based (scalable)
    KEYSET = "keyset"  # Keyset pagination (most efficient)


@dataclass
class PaginationMetadata:
    """
    Pagination metadata returned with results.

    Attributes:
        page_size: Number of items per page
        has_next: Whether next page exists
        has_previous: Whether previous page exists
        page: Current page number (offset pagination)
        total_pages: Total number of pages (offset pagination)
        total_items: Total number of items (offset pagination, expensive)
        next_cursor: Cursor for next page (cursor pagination)
        previous_cursor: Cursor for previous page (cursor pagination)
    """

    page_size: int
    has_next: bool
    has_previous: bool
    page: Optional[int] = None
    total_pages: Optional[int] = None
    total_items: Optional[int] = None
    next_cursor: Optional[str] = None
    previous_cursor: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class PaginationLinks:
    """
    RFC 5988 Link header values.

    Attributes:
        first: First page URL
        last: Last page URL (only available with total count)
        next: Next page URL
        previous: Previous page URL
    """

    first: Optional[str] = None
    last: Optional[str] = None
    next: Optional[str] = None
    previous: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary."""
        return {
            "first": self.first,
            "last": self.last,
            "next": self.next,
            "previous": self.previous,
        }

    def to_link_header(self) -> str:
        """
        Convert to RFC 5988 Link header format.

        Returns:
            Link header string

        Example:
            <https://api.example.com/users?page=2>; rel="next",
            <https://api.example.com/users?page=1>; rel="prev"
        """
        links = []
        if self.first:
            links.append(f'<{self.first}>; rel="first"')
        if self.last:
            links.append(f'<{self.last}>; rel="last"')
        if self.next:
            links.append(f'<{self.next}>; rel="next"')
        if self.previous:
            links.append(f'<{self.previous}>; rel="prev"')

        return ", ".join(links)


class PaginatedResponse(BaseModel):
    """
    Standard paginated response format.

    Attributes:
        items: List of items
        pagination: Pagination metadata
        links: Pagination links (optional)
    """

    items: List[Any]
    pagination: Dict[str, Any]
    links: Optional[Dict[str, Optional[str]]] = None

    class Config:
        arbitrary_types_allowed = True


class BasePaginator(ABC):
    """
    Abstract base class for paginators.

    All paginators must implement:
    - paginate(): Main pagination method
    - get_metadata(): Generate pagination metadata
    - get_links(): Generate pagination links
    """

    def __init__(
        self,
        page_size: int = 20,
        max_page_size: int = 100,
        include_total_count: bool = False,
        base_url: Optional[str] = None,
    ):
        """
        Initialize paginator.

        Args:
            page_size: Number of items per page
            max_page_size: Maximum allowed page size
            include_total_count: Whether to count total items (expensive)
            base_url: Base URL for pagination links
        """
        self.page_size = min(page_size, max_page_size)
        self.max_page_size = max_page_size
        self.include_total_count = include_total_count
        self.base_url = base_url

    @abstractmethod
    async def paginate(self, queryset) -> PaginatedResponse:
        """
        Paginate queryset.

        Args:
            queryset: Database queryset or list

        Returns:
            PaginatedResponse with items and metadata
        """
        pass

    @abstractmethod
    def get_metadata(self, **kwargs) -> PaginationMetadata:
        """Generate pagination metadata."""
        pass

    @abstractmethod
    def get_links(self, request_url: str, **kwargs) -> PaginationLinks:
        """Generate pagination links."""
        pass


class OffsetPaginator(BasePaginator):
    """
    Traditional offset-based pagination.

    Uses page numbers and page size (e.g., page=1&limit=20).

    Pros:
    - Simple and intuitive
    - Random access to any page
    - Easy to implement

    Cons:
    - Performance degrades with large offsets
    - Inconsistent results if data changes during pagination
    - Expensive total count queries

    Example:
        paginator = OffsetPaginator(page=1, page_size=20, include_total_count=True)
        result = await paginator.paginate(User.objects.filter(is_active=True))
    """

    def __init__(
        self,
        page: int = 1,
        page_size: int = 20,
        max_page_size: int = 100,
        include_total_count: bool = True,
        base_url: Optional[str] = None,
    ):
        """
        Initialize offset paginator.

        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            max_page_size: Maximum allowed page size
            include_total_count: Whether to count total items
            base_url: Base URL for pagination links
        """
        super().__init__(page_size, max_page_size, include_total_count, base_url)
        self.page = max(1, page)  # Ensure page >= 1
        self.offset = (self.page - 1) * self.page_size

    async def paginate(self, queryset) -> PaginatedResponse:
        """
        Paginate queryset using offset/limit.

        Args:
            queryset: Database queryset

        Returns:
            PaginatedResponse with items and metadata
        """
        # Get total count if requested (expensive for large tables)
        total_items = None
        if self.include_total_count:
            total_items = await queryset.count()

        # Fetch one extra item to check if there's a next page
        items = await queryset.offset(self.offset).limit(self.page_size + 1).all()

        # Check if there's a next page
        has_next = len(items) > self.page_size
        if has_next:
            items = items[: self.page_size]

        has_previous = self.page > 1

        # Calculate total pages if we have total count
        total_pages = None
        if total_items is not None:
            total_pages = (total_items + self.page_size - 1) // self.page_size

        # Generate metadata
        metadata = self.get_metadata(
            has_next=has_next,
            has_previous=has_previous,
            total_items=total_items,
            total_pages=total_pages,
        )

        # Generate links
        links = None
        if self.base_url:
            links = self.get_links(
                request_url=self.base_url,
                has_next=has_next,
                has_previous=has_previous,
                total_pages=total_pages,
            )

        return PaginatedResponse(
            items=items,
            pagination=metadata.to_dict(),
            links=links.to_dict() if links else None,
        )

    def get_metadata(
        self,
        has_next: bool,
        has_previous: bool,
        total_items: Optional[int] = None,
        total_pages: Optional[int] = None,
    ) -> PaginationMetadata:
        """Generate pagination metadata."""
        return PaginationMetadata(
            page_size=self.page_size,
            has_next=has_next,
            has_previous=has_previous,
            page=self.page,
            total_pages=total_pages,
            total_items=total_items,
        )

    def get_links(
        self,
        request_url: str,
        has_next: bool,
        has_previous: bool,
        total_pages: Optional[int] = None,
    ) -> PaginationLinks:
        """Generate pagination links."""
        # Parse base URL
        parsed = urlparse(request_url)
        query_params = parse_qs(parsed.query)

        def build_url(page: int) -> str:
            """Build URL for specific page."""
            params = {**query_params, "page": page, "limit": self.page_size}
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"

        links = PaginationLinks()

        # First page
        links.first = build_url(1)

        # Last page (if we have total pages)
        if total_pages:
            links.last = build_url(total_pages)

        # Next page
        if has_next:
            links.next = build_url(self.page + 1)

        # Previous page
        if has_previous:
            links.previous = build_url(self.page - 1)

        return links


class CursorPaginator(BasePaginator):
    """
    Cursor-based pagination.

    Uses opaque cursor tokens for efficient pagination.

    Pros:
    - Consistent performance regardless of position
    - Handles data changes gracefully
    - No expensive count queries

    Cons:
    - No random access to pages
    - More complex implementation
    - Cursor tokens can be large

    The cursor encodes the position in the dataset using
    the ordering field values of the last item.

    Example:
        # First page
        paginator = CursorPaginator(cursor=None, page_size=20)
        result = await paginator.paginate(User.objects.order_by('-created_at'))

        # Next page
        next_cursor = result.pagination['next_cursor']
        paginator = CursorPaginator(cursor=next_cursor, page_size=20)
        result = await paginator.paginate(User.objects.order_by('-created_at'))
    """

    def __init__(
        self,
        cursor: Optional[str] = None,
        page_size: int = 20,
        max_page_size: int = 100,
        base_url: Optional[str] = None,
        order_by_field: str = "id",
        reverse: bool = False,
    ):
        """
        Initialize cursor paginator.

        Args:
            cursor: Cursor token for current position
            page_size: Number of items per page
            max_page_size: Maximum allowed page size
            base_url: Base URL for pagination links
            order_by_field: Field to order by (must be unique or indexed)
            reverse: Whether to reverse order
        """
        super().__init__(page_size, max_page_size, False, base_url)
        self.cursor = cursor
        self.order_by_field = order_by_field
        self.reverse = reverse

        # Decode cursor if provided
        self.cursor_data = self._decode_cursor(cursor) if cursor else None

    def _encode_cursor(self, data: Dict[str, Any]) -> str:
        """
        Encode cursor data to base64 string.

        Args:
            data: Cursor data dictionary

        Returns:
            Base64 encoded cursor string
        """
        json_str = json.dumps(data, sort_keys=True)
        encoded = base64.b64encode(json_str.encode("utf-8"))
        return encoded.decode("utf-8")

    def _decode_cursor(self, cursor: str) -> Dict[str, Any]:
        """
        Decode cursor string to data dictionary.

        Args:
            cursor: Base64 encoded cursor string

        Returns:
            Decoded cursor data
        """
        try:
            decoded = base64.b64decode(cursor.encode("utf-8"))
            return json.loads(decoded.decode("utf-8"))
        except Exception as e:
            logger.warning(f"Failed to decode cursor: {e}")
            return {}

    async def paginate(self, queryset) -> PaginatedResponse:
        """
        Paginate queryset using cursor.

        Args:
            queryset: Database queryset (must be ordered)

        Returns:
            PaginatedResponse with items and metadata
        """
        # Apply cursor filter if present
        if self.cursor_data:
            cursor_value = self.cursor_data.get(self.order_by_field)
            if cursor_value is not None:
                # Add WHERE clause based on cursor
                if self.reverse:
                    queryset = queryset.filter(**{f"{self.order_by_field}__lt": cursor_value})
                else:
                    queryset = queryset.filter(**{f"{self.order_by_field}__gt": cursor_value})

        # Fetch one extra item to check if there's a next page
        items = await queryset.limit(self.page_size + 1).all()

        # Check if there's a next page
        has_next = len(items) > self.page_size
        if has_next:
            items = items[: self.page_size]

        has_previous = self.cursor is not None

        # Generate cursors
        next_cursor = None
        if has_next and items:
            last_item = items[-1]
            cursor_value = getattr(last_item, self.order_by_field)
            next_cursor = self._encode_cursor({self.order_by_field: cursor_value})

        previous_cursor = None
        if has_previous and items:
            first_item = items[0]
            cursor_value = getattr(first_item, self.order_by_field)
            previous_cursor = self._encode_cursor({self.order_by_field: cursor_value})

        # Generate metadata
        metadata = self.get_metadata(
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

        # Generate links
        links = None
        if self.base_url:
            links = self.get_links(
                request_url=self.base_url,
                next_cursor=next_cursor,
                previous_cursor=previous_cursor,
            )

        return PaginatedResponse(
            items=items,
            pagination=metadata.to_dict(),
            links=links.to_dict() if links else None,
        )

    def get_metadata(
        self,
        has_next: bool,
        has_previous: bool,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
    ) -> PaginationMetadata:
        """Generate pagination metadata."""
        return PaginationMetadata(
            page_size=self.page_size,
            has_next=has_next,
            has_previous=has_previous,
            next_cursor=next_cursor,
            previous_cursor=previous_cursor,
        )

    def get_links(
        self,
        request_url: str,
        next_cursor: Optional[str] = None,
        previous_cursor: Optional[str] = None,
    ) -> PaginationLinks:
        """Generate pagination links."""
        parsed = urlparse(request_url)
        query_params = parse_qs(parsed.query)

        def build_url(cursor: Optional[str]) -> str:
            """Build URL with cursor."""
            params = {**query_params, "page_size": self.page_size}
            if cursor:
                params["cursor"] = cursor
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"

        links = PaginationLinks()

        # First page (no cursor)
        links.first = build_url(None)

        # Next page
        if next_cursor:
            links.next = build_url(next_cursor)

        # Previous page
        if previous_cursor:
            links.previous = build_url(previous_cursor)

        return links


class KeysetPaginator(BasePaginator):
    """
    Keyset pagination (also called seek method).

    Uses the last seen value for efficient pagination.
    Most efficient for large datasets.

    Pros:
    - Best performance (uses indexed WHERE clause)
    - Consistent results even with data changes
    - Simple implementation

    Cons:
    - No random access
    - Requires unique ordering field
    - Cannot jump to arbitrary page

    Example:
        # First page
        paginator = KeysetPaginator(last_id=None, page_size=20)
        result = await paginator.paginate(User.objects.order_by('id'))

        # Next page
        last_id = result.items[-1].id
        paginator = KeysetPaginator(last_id=last_id, page_size=20)
        result = await paginator.paginate(User.objects.order_by('id'))
    """

    def __init__(
        self,
        last_id: Optional[Any] = None,
        page_size: int = 20,
        max_page_size: int = 100,
        base_url: Optional[str] = None,
        order_by_field: str = "id",
        reverse: bool = False,
    ):
        """
        Initialize keyset paginator.

        Args:
            last_id: Last seen ID/value
            page_size: Number of items per page
            max_page_size: Maximum allowed page size
            base_url: Base URL for pagination links
            order_by_field: Field to order by (must be unique)
            reverse: Whether to reverse order
        """
        super().__init__(page_size, max_page_size, False, base_url)
        self.last_id = last_id
        self.order_by_field = order_by_field
        self.reverse = reverse

    async def paginate(self, queryset) -> PaginatedResponse:
        """
        Paginate queryset using keyset.

        Args:
            queryset: Database queryset (must be ordered)

        Returns:
            PaginatedResponse with items and metadata
        """
        # Apply keyset filter if present
        if self.last_id is not None:
            if self.reverse:
                queryset = queryset.filter(**{f"{self.order_by_field}__lt": self.last_id})
            else:
                queryset = queryset.filter(**{f"{self.order_by_field}__gt": self.last_id})

        # Fetch one extra item to check if there's a next page
        items = await queryset.limit(self.page_size + 1).all()

        # Check if there's a next page
        has_next = len(items) > self.page_size
        if has_next:
            items = items[: self.page_size]

        has_previous = self.last_id is not None

        # Get last ID for next page
        next_id = None
        if has_next and items:
            next_id = getattr(items[-1], self.order_by_field)

        # Generate metadata
        metadata = self.get_metadata(
            has_next=has_next,
            has_previous=has_previous,
            next_id=next_id,
        )

        # Generate links
        links = None
        if self.base_url:
            links = self.get_links(
                request_url=self.base_url,
                next_id=next_id,
            )

        return PaginatedResponse(
            items=items,
            pagination=metadata.to_dict(),
            links=links.to_dict() if links else None,
        )

    def get_metadata(
        self,
        has_next: bool,
        has_previous: bool,
        next_id: Optional[Any] = None,
    ) -> PaginationMetadata:
        """Generate pagination metadata."""
        metadata = PaginationMetadata(
            page_size=self.page_size,
            has_next=has_next,
            has_previous=has_previous,
        )

        # Add next_id as custom field
        if next_id is not None:
            metadata.next_cursor = str(next_id)

        return metadata

    def get_links(
        self,
        request_url: str,
        next_id: Optional[Any] = None,
    ) -> PaginationLinks:
        """Generate pagination links."""
        parsed = urlparse(request_url)
        query_params = parse_qs(parsed.query)

        def build_url(last_id: Optional[Any]) -> str:
            """Build URL with last_id."""
            params = {**query_params, "page_size": self.page_size}
            if last_id is not None:
                params["last_id"] = str(last_id)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params, doseq=True)}"

        links = PaginationLinks()

        # First page (no last_id)
        links.first = build_url(None)

        # Next page
        if next_id is not None:
            links.next = build_url(next_id)

        return links


def paginate_queryset(queryset, strategy: str = PaginationStyle.OFFSET, **kwargs) -> BasePaginator:
    """
    Factory function to create appropriate paginator.

    Args:
        queryset: Database queryset
        strategy: Pagination strategy
        **kwargs: Strategy-specific arguments

    Returns:
        Paginator instance

    Example:
        paginator = paginate_queryset(
            User.objects.filter(is_active=True),
            strategy="cursor",
            cursor=None,
            page_size=20
        )
        result = await paginator.paginate(queryset)
    """
    if strategy == PaginationStyle.OFFSET:
        return OffsetPaginator(**kwargs)
    elif strategy == PaginationStyle.CURSOR:
        return CursorPaginator(**kwargs)
    elif strategy == PaginationStyle.KEYSET:
        return KeysetPaginator(**kwargs)
    else:
        raise ValueError(f"Unknown pagination strategy: {strategy}")


__all__ = [
    "BasePaginator",
    "OffsetPaginator",
    "CursorPaginator",
    "KeysetPaginator",
    "PaginationMetadata",
    "PaginationLinks",
    "PaginatedResponse",
    "PaginationStyle",
    "paginate_queryset",
]
