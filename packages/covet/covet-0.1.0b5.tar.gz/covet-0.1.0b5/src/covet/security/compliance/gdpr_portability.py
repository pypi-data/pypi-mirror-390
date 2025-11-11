"""
GDPR Data Portability (Article 20)

Right to data portability: Individuals can obtain and reuse
their personal data for their own purposes across different services.

REQUIREMENTS:
- Provide data in structured, commonly used format
- Machine-readable format (JSON, CSV, XML)
- Complete data export
- Include all processing activities
"""

import csv
import json
import secrets
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from io import StringIO
from typing import Any, Dict, List, Optional, Set


class DataExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    XML = "xml"


@dataclass
class ExportRequest:
    """Data portability request."""

    request_id: str
    user_id: str
    requested_at: datetime
    format: DataExportFormat
    status: str  # "pending", "processing", "completed", "failed"
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class DataPortabilityService:
    """GDPR data portability service."""

    def __init__(self):
        """Initialize data portability service."""
        self.export_requests: Dict[str, ExportRequest] = {}

    def create_export_request(
        self,
        user_id: str,
        format: DataExportFormat = DataExportFormat.JSON,
    ) -> ExportRequest:
        """Create data export request."""
        request = ExportRequest(
            request_id=f"export_{secrets.token_hex(12)}",
            user_id=user_id,
            requested_at=datetime.utcnow(),
            format=format,
            status="pending",
        )

        self.export_requests[request.request_id] = request
        return request

    def export_user_data(
        self,
        user_data: Dict[str, Any],
        format: DataExportFormat = DataExportFormat.JSON,
    ) -> str:
        """
        Export user data in specified format.

        Args:
            user_data: Complete user data
            format: Export format

        Returns:
            Formatted export data
        """
        if format == DataExportFormat.JSON:
            return self._export_json(user_data)
        elif format == DataExportFormat.CSV:
            return self._export_csv(user_data)
        elif format == DataExportFormat.XML:
            return self._export_xml(user_data)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_json(self, data: Dict[str, Any]) -> str:
        """Export as JSON."""
        export_data = {
            "export_date": datetime.utcnow().isoformat(),
            "data": data,
        }
        return json.dumps(export_data, indent=2, default=str)

    def _export_csv(self, data: Dict[str, Any]) -> str:
        """Export as CSV."""
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(["Category", "Field", "Value"])

        # Flatten data
        def flatten(obj, parent_key=""):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k
                    items.extend(flatten(v, new_key))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_key = f"{parent_key}[{i}]"
                    items.extend(flatten(item, new_key))
            else:
                items.append((parent_key, str(obj)))
            return items

        for category, field, value in flatten(data):
            writer.writerow([category, field, value])

        return output.getvalue()

    def _export_xml(self, data: Dict[str, Any]) -> str:
        """Export as XML."""
        root = ET.Element("user_data_export")
        root.set("export_date", datetime.utcnow().isoformat())

        def dict_to_xml(parent, data_dict):
            for key, value in data_dict.items():
                child = ET.SubElement(parent, key)
                if isinstance(value, dict):
                    dict_to_xml(child, value)
                elif isinstance(value, list):
                    for item in value:
                        item_elem = ET.SubElement(child, "item")
                        if isinstance(item, dict):
                            dict_to_xml(item_elem, item)
                        else:
                            item_elem.text = str(item)
                else:
                    child.text = str(value)

        dict_to_xml(root, data)
        return ET.tostring(root, encoding="unicode")


__all__ = [
    "DataPortabilityService",
    "DataExportFormat",
    "ExportRequest",
]
