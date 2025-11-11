"""
Relay-Style Pagination for GraphQL

Implements Relay cursor-based pagination specification.
"""

import base64
import json
from dataclasses import dataclass
from typing import Generic, List, Optional, TypeVar

import strawberry

T = TypeVar("T")


@strawberry.type
class PageInfo:
    """Page information for cursor pagination."""

    has_next_page: bool = strawberry.field(description="Whether there are more items")
    has_previous_page: bool = strawberry.field(description="Whether there are previous items")
    start_cursor: Optional[str] = strawberry.field(description="First cursor in page")
    end_cursor: Optional[str] = strawberry.field(description="Last cursor in page")


@strawberry.type
class Edge(Generic[T]):
    """Edge in a connection."""

    node: T = strawberry.field(description="The actual item")
    cursor: str = strawberry.field(description="Cursor for this item")


@strawberry.type
class Connection(Generic[T]):
    """Connection implementing Relay pagination."""

    edges: List[Edge[T]] = strawberry.field(description="List of edges")
    page_info: PageInfo = strawberry.field(description="Page information")
    total_count: Optional[int] = strawberry.field(
        default=None, description="Total count of items (if available)"
    )


def offset_to_cursor(offset: int) -> str:
    """
    Convert offset to cursor.

    Args:
        offset: Numeric offset

    Returns:
        Base64-encoded cursor
    """
    cursor_dict = {"offset": offset}
    cursor_json = json.dumps(cursor_dict)
    return base64.b64encode(cursor_json.encode("utf-8")).decode("utf-8")


def cursor_to_offset(cursor: str) -> int:
    """
    Convert cursor to offset.

    Args:
        cursor: Base64-encoded cursor

    Returns:
        Numeric offset
    """
    try:
        cursor_json = base64.b64decode(cursor.encode("utf-8")).decode("utf-8")
        cursor_dict = json.loads(cursor_json)
        return cursor_dict.get("offset", 0)
    except Exception:
        return 0


class ConnectionResolver(Generic[T]):
    """
    Helper for building connections from data.

    Example:
        resolver = ConnectionResolver(items, first=10, after=cursor)
        connection = resolver.resolve()
    """

    def __init__(
        self,
        items: List[T],
        first: Optional[int] = None,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None,
        total_count: Optional[int] = None,
    ):
        """
        Initialize connection resolver.

        Args:
            items: List of items
            first: Return first N items
            after: Return items after cursor
            last: Return last N items
            before: Return items before cursor
            total_count: Total count (optional)
        """
        self.items = items
        self.first = first
        self.after = after
        self.last = last
        self.before = before
        self.total_count = total_count

    def resolve(self) -> Connection[T]:
        """
        Resolve to connection.

        Returns:
            Connection with edges and page info
        """
        # Calculate slice bounds
        start_offset = 0
        end_offset = len(self.items)

        if self.after:
            start_offset = cursor_to_offset(self.after) + 1

        if self.before:
            end_offset = cursor_to_offset(self.before)

        # Apply first/last
        if self.first is not None:
            end_offset = min(end_offset, start_offset + self.first)

        if self.last is not None:
            start_offset = max(start_offset, end_offset - self.last)

        # Slice items
        sliced_items = self.items[start_offset:end_offset]

        # Build edges
        edges = [
            Edge(node=item, cursor=offset_to_cursor(start_offset + i))
            for i, item in enumerate(sliced_items)
        ]

        # Build page info
        page_info = PageInfo(
            has_next_page=end_offset < len(self.items),
            has_previous_page=start_offset > 0,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None,
        )

        return Connection(
            edges=edges,
            page_info=page_info,
            total_count=self.total_count,
        )


def relay_connection(
    items: List[T],
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
    total_count: Optional[int] = None,
) -> Connection[T]:
    """
    Create relay connection from items.

    Args:
        items: List of items
        first: Return first N items
        after: Return items after cursor
        last: Return last N items
        before: Return items before cursor
        total_count: Total count

    Returns:
        Connection
    """
    resolver = ConnectionResolver(
        items=items,
        first=first,
        after=after,
        last=last,
        before=before,
        total_count=total_count,
    )
    return resolver.resolve()


def create_connection(
    items: List[T],
    total_count: Optional[int] = None,
) -> Connection[T]:
    """
    Create simple connection from items.

    Args:
        items: List of items
        total_count: Total count

    Returns:
        Connection
    """
    return relay_connection(items, total_count=total_count)


__all__ = [
    "Connection",
    "Edge",
    "PageInfo",
    "ConnectionResolver",
    "relay_connection",
    "create_connection",
    "offset_to_cursor",
    "cursor_to_offset",
]
