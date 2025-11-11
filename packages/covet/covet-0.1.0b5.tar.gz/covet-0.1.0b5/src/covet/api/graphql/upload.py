"""
File Upload Support for GraphQL

Implements multipart/form-data file uploads for GraphQL.
"""

import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import strawberry


@strawberry.scalar(
    serialize=lambda v: None,  # Cannot serialize upload
    parse_value=lambda v: v,  # Return Upload object as-is
)
class Upload:
    """
    File upload scalar.

    Used in GraphQL mutations to accept file uploads.

    Example:
        @strawberry.input
        class FileInput:
            file: Upload
            description: Optional[str] = None

        @strawberry.type
        class Mutation:
            @strawberry.mutation
            async def upload_file(self, input: FileInput) -> bool:
                content = await input.file.read()
                # Save file...
                return True
    """

    def __init__(
        self,
        filename: str,
        content_type: str,
        file: io.BytesIO,
    ):
        """
        Initialize upload.

        Args:
            filename: Original filename
            content_type: MIME type
            file: File object
        """
        self.filename = filename
        self.content_type = content_type
        self.file = file

    async def read(self, size: int = -1) -> bytes:
        """Read file contents."""
        return self.file.read(size)

    async def save(self, destination: str):
        """
        Save file to destination.

        Args:
            destination: Path to save file
        """
        with open(destination, "wb") as f:
            f.write(self.file.read())


# Export scalar for use in schema
upload_scalar = Upload


@dataclass
class MultipartRequest:
    """
    Multipart GraphQL request.

    Contains operations, map, and files as per graphql-multipart-request-spec.
    """

    operations: Dict[str, Any]
    map: Dict[str, List[str]]
    files: Dict[str, Upload]


async def process_multipart(
    operations: str,
    map_data: str,
    files: Dict[str, Any],
) -> MultipartRequest:
    """
    Process multipart GraphQL request.

    Follows graphql-multipart-request-spec specification.

    Args:
        operations: JSON operations string
        map_data: JSON map string
        files: Uploaded files dict

    Returns:
        Processed multipart request
    """
    import json

    # Parse operations and map
    operations_dict = json.loads(operations)
    map_dict = json.loads(map_data)

    # Process files
    processed_files = {}
    for key, file_data in files.items():
        # Create Upload object
        upload = Upload(
            filename=getattr(file_data, "filename", "upload"),
            content_type=getattr(file_data, "content_type", "application/octet-stream"),
            file=io.BytesIO(await file_data.read() if hasattr(file_data, "read") else file_data),
        )
        processed_files[key] = upload

        # Map file to variables
        if key in map_dict:
            for path in map_dict[key]:
                # Set upload in operations at path
                # e.g., "variables.input.file"
                parts = path.split(".")
                target = operations_dict
                for part in parts[:-1]:
                    target = target[part]
                target[parts[-1]] = upload

    return MultipartRequest(
        operations=operations_dict,
        map=map_dict,
        files=processed_files,
    )


__all__ = [
    "Upload",
    "upload_scalar",
    "MultipartRequest",
    "process_multipart",
]
