"""
Flash Messages

Temporary messages stored in session:
- Success, error, warning, info categories
- Automatic clearing after read
- Multiple messages support
- Category filtering

NO MOCK DATA: Uses session storage.
"""

from enum import Enum
from typing import List, Optional, Tuple


class FlashCategory(str, Enum):
    """Flash message categories."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


def flash(session, message: str, category: str = FlashCategory.INFO):
    """
    Add flash message to session.

    Args:
        session: Session object
        message: Message text
        category: Message category

    Example:
        flash(session, 'User created successfully', 'success')
        flash(session, 'Invalid credentials', 'error')
    """
    session.flash(message, category)


def get_flashed_messages(
    session, with_categories: bool = False, category_filter: Optional[List[str]] = None
) -> List[any]:
    """
    Get and clear flash messages from session.

    Args:
        session: Session object
        with_categories: Include categories in result
        category_filter: Only return messages matching these categories

    Returns:
        List of messages or list of (category, message) tuples

    Example:
        # Get all messages
        messages = get_flashed_messages(session)
        # ['User created successfully']

        # Get with categories
        messages = get_flashed_messages(session, with_categories=True)
        # [('success', 'User created successfully')]

        # Get only errors
        errors = get_flashed_messages(session, category_filter=['error'])
    """
    return session.get_flashed_messages(with_categories, category_filter)


__all__ = ["FlashCategory", "flash", "get_flashed_messages"]
