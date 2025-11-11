"""
CovetPy XXE (XML External Entity) Protection Module

Protection against XXE attacks through:
- XML parser hardening
- Disable external entity processing
- DTD validation
- Safe XML parsing defaults

Author: CovetPy Security Team
License: MIT
"""

import xml.etree.ElementTree as ET
from typing import Optional, Union
from xml.dom import minidom

import defusedxml.ElementTree as DefusedET


class XXEProtector:
    """
    XXE protection through safe XML parsing.
    """

    @staticmethod
    def parse_xml_safe(xml_string: str) -> ET.Element:
        """
        Parse XML safely with XXE protection.

        Args:
            xml_string: XML string to parse

        Returns:
            Parsed XML element

        Raises:
            ValueError: If XML contains dangerous content
        """
        # Use defusedxml for safe parsing
        try:
            return DefusedET.fromstring(xml_string)
        except Exception as e:
            raise ValueError(f"XML parsing failed: {e}")

    @staticmethod
    def is_xml_safe(xml_string: str) -> bool:
        """Check if XML is safe to parse."""
        dangerous_patterns = [b"<!ENTITY", b"<!DOCTYPE", b"SYSTEM", b"PUBLIC"]

        xml_bytes = xml_string.encode() if isinstance(xml_string, str) else xml_string

        for pattern in dangerous_patterns:
            if pattern in xml_bytes:
                return False

        return True


__all__ = ["XXEProtector"]
