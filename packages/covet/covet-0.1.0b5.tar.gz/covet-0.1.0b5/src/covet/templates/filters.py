"""
Template Filters - Built-in and Custom Filter System

Comprehensive filter implementation with:
- String manipulation filters
- Number formatting filters
- Date/time filters
- List/dict filters
- Security filters
- Custom filter registration
"""

import hashlib
import html
import json
import math
import re
import urllib.parse
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class FilterRegistry:
    """Registry for template filters with built-in filters."""

    def __init__(self):
        self.filters = {}
        self._register_builtin_filters()

    def add_filter(self, name: str, filter_func: Callable):
        """Add custom filter function."""
        self.filters[name] = filter_func

    def get_filter(self, name: str) -> Optional[Callable]:
        """Get filter function by name."""
        return self.filters.get(name)

    def remove_filter(self, name: str):
        """Remove filter by name."""
        self.filters.pop(name, None)

    def list_filters(self) -> List[str]:
        """Get list of available filter names."""
        return list(self.filters.keys())

    def _register_builtin_filters(self):
        """Register all built-in filters."""
        # String filters
        self.filters.update(
            {
                "upper": filter_upper,
                "lower": filter_lower,
                "title": filter_title,
                "capitalize": filter_capitalize,
                "trim": filter_trim,
                "strip": filter_trim,  # Alias
                "length": filter_length,
                "reverse": filter_reverse,
                "replace": filter_replace,
                "truncate": filter_truncate,
                "wordwrap": filter_wordwrap,
                "indent": filter_indent,
                "center": filter_center,
                "ljust": filter_ljust,
                "rjust": filter_rjust,
                "slice": filter_slice,
                "join": filter_join,
                "split": filter_split,
                "regex_replace": filter_regex_replace,
                "regex_search": filter_regex_search,
                "slugify": filter_slugify,
            }
        )

        # Number filters
        self.filters.update(
            {
                "abs": filter_abs,
                "round": filter_round,
                "int": filter_int,
                "float": filter_float,
                "format": filter_format,
                "filesizeformat": filter_filesizeformat,
                "currency": filter_currency,
                "percentage": filter_percentage,
            }
        )

        # Date/time filters
        self.filters.update(
            {
                "date": filter_date,
                "datetime": filter_datetime,
                "time": filter_time,
                "strftime": filter_strftime,
                "age": filter_age,
                "naturaltime": filter_naturaltime,
            }
        )

        # List/dict filters
        self.filters.update(
            {
                "first": filter_first,
                "last": filter_last,
                "random": filter_random,
                "sort": filter_sort,
                "unique": filter_unique,
                "list": filter_list,
                "dict": filter_dict,
                "items": filter_items,
                "keys": filter_keys,
                "values": filter_values,
                "sum": filter_sum,
                "min": filter_min,
                "max": filter_max,
                "batch": filter_batch,
                "groupby": filter_groupby,
            }
        )

        # Security filters
        self.filters.update(
            {
                "escape": filter_escape,
                "e": filter_escape,  # Short alias
                "safe": filter_safe,
                "urlencode": filter_urlencode,
                "urlquote": filter_urlquote,
                "base64encode": filter_base64encode,
                "base64decode": filter_base64decode,
                "md5": filter_md5,
                "sha1": filter_sha1,
                "sha256": filter_sha256,
            }
        )

        # Utility filters
        self.filters.update(
            {
                "default": filter_default,
                "d": filter_default,  # Short alias
                "json": filter_json,
                "tojson": filter_json,  # Alias
                "fromjson": filter_fromjson,
                "bool": filter_bool,
                "string": filter_string,
                "attr": filter_attr,
                "map": filter_map,
                "select": filter_select,
                "reject": filter_reject,
                "selectattr": filter_selectattr,
                "rejectattr": filter_rejectattr,
            }
        )


# String Filters
def filter_upper(value: Any) -> str:
    """Convert to uppercase."""
    return str(value).upper()


def filter_lower(value: Any) -> str:
    """Convert to lowercase."""
    return str(value).lower()


def filter_title(value: Any) -> str:
    """Convert to title case."""
    return str(value).title()


def filter_capitalize(value: Any) -> str:
    """Capitalize first letter."""
    s = str(value)
    return s.capitalize() if s else s


def filter_trim(value: Any) -> str:
    """Remove leading/trailing whitespace."""
    return str(value).strip()


def filter_length(value: Any) -> int:
    """Get length of value."""
    try:
        return len(value)
    except TypeError:
        return 0


def filter_reverse(value: Any) -> Any:
    """Reverse string or list."""
    if isinstance(value, str):
        return value[::-1]
    try:
        return list(reversed(value))
    except TypeError:
        return value


def filter_replace(value: Any, old: str, new: str = "", count: int = -1) -> str:
    """Replace substring in string."""
    return str(value).replace(old, new, count)


def filter_truncate(value: Any, length: int = 255, end: str = "...", leeway: int = 0) -> str:
    """Truncate string to specified length."""
    s = str(value)
    if len(s) <= length + leeway:
        return s

    # If truncation would cut mid-word, try to cut at word boundary
    truncated = s[:length]
    if " " in truncated:
        # Find last space to avoid cutting words
        last_space = truncated.rfind(" ")
        if last_space > length // 2:  # Only if we don't lose too much text
            truncated = truncated[:last_space]

    return truncated + end


def filter_wordwrap(value: Any, width: int = 79, break_long_words: bool = True) -> str:
    """Wrap text to specified width."""
    import textwrap

    return textwrap.fill(str(value), width=width, break_long_words=break_long_words)


def filter_indent(value: Any, width: int = 4, first: bool = False) -> str:
    """Indent each line of text."""
    lines = str(value).splitlines()
    if not lines:
        return ""

    indent_str = " " * width
    if first:
        return indent_str + f"\n{indent_str}".join(lines)
    else:
        return (
            lines[0] + "\n" + indent_str + f"\n{indent_str}".join(lines[1:])
            if len(lines) > 1
            else lines[0]
        )


def filter_center(value: Any, width: int = 80) -> str:
    """Center string in field of given width."""
    return str(value).center(width)


def filter_ljust(value: Any, width: int = 80) -> str:
    """Left-justify string in field of given width."""
    return str(value).ljust(width)


def filter_rjust(value: Any, width: int = 80) -> str:
    """Right-justify string in field of given width."""
    return str(value).rjust(width)


def filter_slice(value: Any, start: int = 0, stop: int = None, step: int = 1) -> Any:
    """Slice sequence."""
    try:
        if stop is None:
            return value[start::step]
        return value[start:stop:step]
    except (TypeError, IndexError):
        return value


def filter_join(value: Any, separator: str = "") -> str:
    """Join sequence with separator."""
    try:
        return separator.join(str(item) for item in value)
    except TypeError:
        return str(value)


def filter_split(value: Any, separator: str = None, maxsplit: int = -1) -> List[str]:
    """Split string by separator."""
    return str(value).split(separator, maxsplit)


def filter_regex_replace(value: Any, pattern: str, replacement: str = "", flags: int = 0) -> str:
    """Replace using regular expression."""
    return re.sub(pattern, replacement, str(value), flags=flags)


def filter_regex_search(value: Any, pattern: str, flags: int = 0) -> bool:
    """Search for pattern in string."""
    return bool(re.search(pattern, str(value), flags=flags))


def filter_slugify(value: Any) -> str:
    """Convert to URL-friendly slug."""
    s = str(value).lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s)
    return s.strip("-")


# Number Filters
def filter_abs(value: Any) -> Union[int, float]:
    """Get absolute value."""
    try:
        return abs(float(value))
    except (TypeError, ValueError):
        return 0


def filter_round(value: Any, precision: int = 0, method: str = "common") -> Union[int, float]:
    """Round number to precision."""
    try:
        num = float(value)
        if precision == 0:
            return int(round(num))
        return round(num, precision)
    except (TypeError, ValueError):
        return 0


def filter_int(value: Any, default: int = 0) -> int:
    """Convert to integer."""
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def filter_float(value: Any, default: float = 0.0) -> float:
    """Convert to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def filter_format(value: Any, fmt: str = "{}") -> str:
    """Format value using format string."""
    try:
        return fmt.format(value)
    except (ValueError, TypeError):
        return str(value)


def filter_filesizeformat(value: Any) -> str:
    """Format file size in human readable format."""
    try:
        bytes_val = int(value)
        if bytes_val == 0:
            return "0 bytes"

        size_names = ["bytes", "KB", "MB", "GB", "TB", "PB"]
        i = int(math.floor(math.log(bytes_val, 1024)))
        p = math.pow(1024, i)
        s = round(bytes_val / p, 2)
        return f"{s} {size_names[i]}"
    except (TypeError, ValueError):
        return str(value)


def filter_currency(value: Any, symbol: str = "$", precision: int = 2) -> str:
    """Format as currency."""
    try:
        num = float(value)
        return f"{symbol}{num:,.{precision}f}"
    except (TypeError, ValueError):
        return str(value)


def filter_percentage(value: Any, precision: int = 1) -> str:
    """Format as percentage."""
    try:
        num = float(value) * 100
        return f"{num:.{precision}f}%"
    except (TypeError, ValueError):
        return str(value)


# Date/Time Filters
def filter_date(value: Any, fmt: str = "%Y-%m-%d") -> str:
    """Format date."""
    if isinstance(value, datetime):
        return value.strftime(fmt)
    elif isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return dt.strftime(fmt)
        except ValueError:
            return str(value)
    return str(value)


def filter_datetime(value: Any, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime."""
    return filter_date(value, fmt)


def filter_time(value: Any, fmt: str = "%H:%M:%S") -> str:
    """Format time."""
    return filter_date(value, fmt)


def filter_strftime(value: Any, fmt: str) -> str:
    """Format datetime with strftime."""
    return filter_date(value, fmt)


def filter_age(value: Any) -> str:
    """Get age of datetime."""
    try:
        if isinstance(value, str):
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif isinstance(value, datetime):
            dt = value
        else:
            return str(value)

        now = datetime.now()
        if dt.tzinfo and not now.tzinfo:
            now = now.replace(tzinfo=dt.tzinfo)

        delta = now - dt
        days = delta.days

        if days == 0:
            return "Today"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days < 365:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
    except (ValueError, TypeError):
        return str(value)


def filter_naturaltime(value: Any) -> str:
    """Natural time representation."""
    return filter_age(value)


# List/Dict Filters
def filter_first(value: Any, default: Any = None) -> Any:
    """Get first item."""
    try:
        return next(iter(value))
    except (TypeError, StopIteration):
        return default


def filter_last(value: Any, default: Any = None) -> Any:
    """Get last item."""
    try:
        if hasattr(value, "__getitem__"):
            return value[-1]
        return list(value)[-1]
    except (TypeError, IndexError):
        return default


def filter_random(value: Any) -> Any:
    """Get random item."""
    try:
        import random

        return random.choice(list(value))
    except (TypeError, IndexError):
        return value


def filter_sort(
    value: Any,
    reverse: bool = False,
    case_sensitive: bool = True,
    attribute: str = None,
) -> List[Any]:
    """Sort sequence."""
    try:
        items = list(value)
        if attribute:

            def key_func(x):
                return getattr(x, attribute, x)

        elif not case_sensitive:

            def key_func(x):
                return str(x).lower()

        else:
            key_func = None

        return sorted(items, key=key_func, reverse=reverse)
    except TypeError:
        return list(value) if hasattr(value, "__iter__") else [value]


def filter_unique(value: Any) -> List[Any]:
    """Get unique items preserving order."""
    try:
        seen = set()
        result = []
        for item in value:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    except TypeError:
        return [value]


def filter_list(value: Any) -> List[Any]:
    """Convert to list."""
    if isinstance(value, list):
        return value
    try:
        return list(value)
    except TypeError:
        return [value]


def filter_dict(value: Any) -> Dict[Any, Any]:
    """Convert to dict."""
    if isinstance(value, dict):
        return value
    try:
        return dict(value)
    except (TypeError, ValueError):
        return {}


def filter_items(value: Any) -> List[Tuple[Any, Any]]:
    """Get dict items."""
    try:
        return list(value.items())
    except AttributeError:
        return []


def filter_keys(value: Any) -> List[Any]:
    """Get dict keys."""
    try:
        return list(value.keys())
    except AttributeError:
        return []


def filter_values(value: Any) -> List[Any]:
    """Get dict values."""
    try:
        return list(value.values())
    except AttributeError:
        return []


def filter_sum(value: Any, start: Union[int, float] = 0) -> Union[int, float]:
    """Sum numeric values."""
    try:
        return sum(value, start)
    except TypeError:
        return start


def filter_min(value: Any) -> Any:
    """Get minimum value."""
    try:
        return min(value)
    except (TypeError, ValueError):
        return value


def filter_max(value: Any) -> Any:
    """Get maximum value."""
    try:
        return max(value)
    except (TypeError, ValueError):
        return value


def filter_batch(value: Any, size: int, fill_with: Any = None) -> List[List[Any]]:
    """Batch items into groups."""
    try:
        items = list(value)
        batches = []
        for i in range(0, len(items), size):
            batch = items[i : i + size]
            if fill_with is not None and len(batch) < size:
                batch.extend([fill_with] * (size - len(batch)))
            batches.append(batch)
        return batches
    except TypeError:
        return [[value]]


def filter_groupby(value: Any, attribute: str) -> List[Tuple[Any, List[Any]]]:
    """Group items by attribute."""
    try:
        from itertools import groupby

        items = list(value)

        def key_func(x):
            return getattr(x, attribute) if hasattr(x, attribute) else x.get(attribute)

        return [
            (key, list(group)) for key, group in groupby(sorted(items, key=key_func), key=key_func)
        ]
    except (TypeError, AttributeError):
        return [(None, [value])]


# Security Filters
def filter_escape(value: Any) -> str:
    """Escape HTML characters."""
    return html.escape(str(value), quote=True)


def filter_safe(value: Any) -> "SafeString":
    """Mark string as safe."""
    from .engine import SafeString

    return SafeString(str(value))


def filter_urlencode(value: Any) -> str:
    """URL encode string."""
    return urllib.parse.quote_plus(str(value))


def filter_urlquote(value: Any) -> str:
    """URL quote string."""
    return urllib.parse.quote(str(value))


def filter_base64encode(value: Any) -> str:
    """Base64 encode string."""
    import base64

    return base64.b64encode(str(value).encode("utf-8")).decode("ascii")


def filter_base64decode(value: Any) -> str:
    """Base64 decode string."""
    import base64

    try:
        return base64.b64decode(str(value)).decode("utf-8")
    except Exception:
        return str(value)


def filter_md5(value: Any) -> str:
    """Generate MD5 hash."""
    return hashlib.md5(str(value).encode("utf-8"), usedforsecurity=False).hexdigest()


def filter_sha1(value: Any) -> str:
    """Generate SHA1 hash."""
    return hashlib.sha1(str(value).encode("utf-8"), usedforsecurity=False).hexdigest()


def filter_sha256(value: Any) -> str:
    """Generate SHA256 hash."""
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


# Utility Filters
def filter_default(value: Any, default: Any = "", boolean: bool = False) -> Any:
    """Return default if value is falsy."""
    if boolean:
        return default if not bool(value) else value
    return default if value is None or value == "" else value


def filter_json(value: Any, indent: int = None) -> str:
    """Convert to JSON string."""
    try:
        return json.dumps(value, indent=indent, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def filter_fromjson(value: Any) -> Any:
    """Parse JSON string."""
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return value


def filter_bool(value: Any) -> bool:
    """Convert to boolean."""
    return bool(value)


def filter_string(value: Any) -> str:
    """Convert to string."""
    return str(value)


def filter_attr(value: Any, name: str) -> Any:
    """Get attribute from object."""
    try:
        return getattr(value, name)
    except AttributeError:
        if isinstance(value, dict):
            return value.get(name)
        return None


def filter_map(value: Any, filter_name: str, *args) -> List[Any]:
    """Apply filter to each item."""
    # This would need access to the filter registry
    try:
        return [item for item in value]  # Simplified implementation
    except TypeError:
        return [value]


def filter_select(value: Any, test: str = None) -> List[Any]:
    """Select items that pass test."""
    try:
        if test is None:
            return [item for item in value if item]
        # Simplified - would need proper test function implementation
        return list(value)
    except TypeError:
        return [value]


def filter_reject(value: Any, test: str = None) -> List[Any]:
    """Reject items that pass test."""
    try:
        if test is None:
            return [item for item in value if not item]
        # Simplified - would need proper test function implementation
        return []
    except TypeError:
        return []


def filter_selectattr(value: Any, attr: str, test: str = None) -> List[Any]:
    """Select items by attribute test."""
    try:
        result = []
        for item in value:
            attr_value = (
                getattr(item, attr, None)
                if hasattr(item, attr)
                else item.get(attr) if isinstance(item, dict) else None
            )
            if test is None and attr_value:
                result.append(item)
            # Would need proper test implementation
        return result
    except TypeError:
        return [value]


def filter_rejectattr(value: Any, attr: str, test: str = None) -> List[Any]:
    """Reject items by attribute test."""
    try:
        result = []
        for item in value:
            attr_value = (
                getattr(item, attr, None)
                if hasattr(item, attr)
                else item.get(attr) if isinstance(item, dict) else None
            )
            if test is None and not attr_value:
                result.append(item)
            # Would need proper test implementation
        return result
    except TypeError:
        return []


__all__ = [
    "FilterRegistry",
    # All filter functions would be listed here
]
