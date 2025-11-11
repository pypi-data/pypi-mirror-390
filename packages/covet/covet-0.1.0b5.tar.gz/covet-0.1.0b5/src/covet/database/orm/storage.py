"""
File Storage Backends for FileField and ImageField

Provides abstraction for storing uploaded files to various backends:
- LocalFileStorage: Store files on local filesystem
- S3FileStorage: Store files on AWS S3 (requires boto3)
- AzureFileStorage: Store files on Azure Blob Storage (requires azure-storage-blob)
"""

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO, Optional
from urllib.parse import urljoin


class FileStorage(ABC):
    """Abstract base class for file storage backends."""

    @abstractmethod
    async def save(self, name: str, content: BinaryIO) -> str:
        """
        Save file content and return the stored file path/name.

        Args:
            name: Desired file name
            content: File content (binary file object)

        Returns:
            Stored file path/name
        """
        pass

    @abstractmethod
    async def delete(self, name: str) -> bool:
        """
        Delete a file.

        Args:
            name: File path/name to delete

        Returns:
            True if deleted successfully
        """
        pass

    @abstractmethod
    async def exists(self, name: str) -> bool:
        """
        Check if file exists.

        Args:
            name: File path/name to check

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
    async def url(self, name: str) -> str:
        """
        Get URL for accessing the file.

        Args:
            name: File path/name

        Returns:
            URL string
        """
        pass

    @abstractmethod
    async def size(self, name: str) -> int:
        """
        Get file size in bytes.

        Args:
            name: File path/name

        Returns:
            Size in bytes
        """
        pass


class LocalFileStorage(FileStorage):
    """
    Local filesystem storage backend.

    Stores files on the local filesystem.

    Example:
        storage = LocalFileStorage(
            base_path='/var/www/media',
            base_url='/media/'
        )
    """

    def __init__(
        self,
        base_path: str = 'media',
        base_url: str = '/media/',
        create_dirs: bool = True
    ):
        """
        Initialize local file storage.

        Args:
            base_path: Base directory for storing files
            base_url: Base URL for accessing files
            create_dirs: Create directories if they don't exist
        """
        self.base_path = Path(base_path)
        self.base_url = base_url
        self.create_dirs = create_dirs

        if create_dirs:
            self.base_path.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.

        Args:
            name: Original filename

        Returns:
            Sanitized filename

        Raises:
            ValueError: If filename is invalid or empty
        """
        if not name:
            raise ValueError("Filename cannot be empty")

        # Remove path components, keep only the filename
        name = os.path.basename(name)

        # Remove any remaining path separators (double check)
        name = name.replace('/', '').replace('\\', '')

        # Remove null bytes
        name = name.replace('\x00', '')

        # Remove any other dangerous characters
        # Allow: alphanumeric, dots, hyphens, underscores, spaces
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_ ')
        name = ''.join(c for c in name if c in safe_chars)

        # Limit length to filesystem max (255 bytes for most systems)
        if len(name.encode('utf-8')) > 255:
            # Truncate while preserving extension
            name_path = Path(name)
            stem = name_path.stem
            suffix = name_path.suffix
            max_stem_length = 255 - len(suffix.encode('utf-8'))
            stem_bytes = stem.encode('utf-8')[:max_stem_length]
            name = stem_bytes.decode('utf-8', errors='ignore') + suffix

        # Ensure not empty after sanitization
        if not name or name.strip() == '':
            raise ValueError("Invalid filename after sanitization")

        # Prevent directory names
        if name in ('.', '..'):
            raise ValueError("Invalid filename")

        return name

    def _validate_path(self, name: str) -> Path:
        """
        Validate that the file path is within the base directory.

        Args:
            name: Sanitized file name

        Returns:
            Validated absolute path

        Raises:
            ValueError: If path escapes base directory
        """
        file_path = self.base_path / name

        # Resolve to absolute path
        try:
            resolved_path = file_path.resolve()
            base_resolved = self.base_path.resolve()

            # Check if resolved path is within base_path
            # Use is_relative_to() for Python 3.9+, fallback for earlier versions
            try:
                is_safe = resolved_path.is_relative_to(base_resolved)
            except AttributeError:
                # Python < 3.9 fallback
                try:
                    resolved_path.relative_to(base_resolved)
                    is_safe = True
                except ValueError:
                    is_safe = False

            if not is_safe:
                raise ValueError("Path traversal detected")

        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid file path: {e}")

        return file_path

    def _get_available_name(self, name: str) -> str:
        """
        Get an available file name by appending numbers if file exists.

        Args:
            name: Desired file name

        Returns:
            Available file name

        Raises:
            ValueError: If filename is invalid or causes path traversal
        """
        # Sanitize filename first (CRITICAL security fix)
        name = self._sanitize_filename(name)

        # Validate path is within base directory
        file_path = self._validate_path(name)

        if not file_path.exists():
            return name

        # File exists, find available name
        name_path = Path(name)
        stem = name_path.stem
        suffix = name_path.suffix

        counter = 1
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = self._validate_path(new_name)
            if not new_path.exists():
                return new_name
            counter += 1

    async def save(self, name: str, content: BinaryIO) -> str:
        """Save file to local filesystem."""
        # Get available name (handle duplicates)
        name = self._get_available_name(name)

        file_path = self.base_path / name

        # Create parent directories
        if self.create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(content, f)

        return name

    async def delete(self, name: str) -> bool:
        """Delete file from local filesystem."""
        try:
            # Sanitize and validate path
            name = self._sanitize_filename(name)
            file_path = self._validate_path(name)

            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except (OSError, ValueError):
            return False

    async def exists(self, name: str) -> bool:
        """Check if file exists on local filesystem."""
        try:
            # Sanitize and validate path
            name = self._sanitize_filename(name)
            file_path = self._validate_path(name)
            return file_path.exists()
        except ValueError:
            return False

    async def url(self, name: str) -> str:
        """Get URL for accessing the file."""
        # Sanitize filename first
        name = self._sanitize_filename(name)
        # Normalize path separators for URL
        name = name.replace('\\', '/')
        return urljoin(self.base_url, name)

    async def size(self, name: str) -> int:
        """Get file size in bytes."""
        try:
            # Sanitize and validate path
            name = self._sanitize_filename(name)
            file_path = self._validate_path(name)
            if file_path.exists():
                return file_path.stat().st_size
            return 0
        except ValueError:
            return 0


# Default storage instance
_default_storage: Optional[FileStorage] = None


def get_default_storage() -> FileStorage:
    """
    Get the default file storage backend.

    Returns:
        FileStorage instance
    """
    global _default_storage

    if _default_storage is None:
        # Create default local storage
        _default_storage = LocalFileStorage()

    return _default_storage


def set_default_storage(storage: FileStorage) -> None:
    """
    Set the default file storage backend.

    Args:
        storage: FileStorage instance to use as default
    """
    global _default_storage
    _default_storage = storage


# S3 Storage (optional, requires boto3)
try:
    import boto3
    from botocore.exceptions import ClientError

    class S3FileStorage(FileStorage):
        """
        AWS S3 storage backend.

        Stores files on Amazon S3.

        Example:
            storage = S3FileStorage(
                bucket_name='my-bucket',
                region_name='us-east-1',
                access_key='...',
                secret_key='...'
            )
        """

        def __init__(
            self,
            bucket_name: str,
            region_name: str = 'us-east-1',
            access_key: Optional[str] = None,
            secret_key: Optional[str] = None,
            base_path: str = '',
            acl: str = 'private'
        ):
            """
            Initialize S3 storage.

            Args:
                bucket_name: S3 bucket name
                region_name: AWS region
                access_key: AWS access key (optional, uses environment if not provided)
                secret_key: AWS secret key (optional, uses environment if not provided)
                base_path: Base path within bucket
                acl: Access control list (default: 'private' for security)
            """
            self.bucket_name = bucket_name
            self.region_name = region_name
            self.base_path = base_path.rstrip('/')
            self.acl = acl

            # Initialize S3 client
            self.s3_client = boto3.client(
                's3',
                region_name=region_name,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key
            )

        def _get_key(self, name: str) -> str:
            """Get full S3 key including base path."""
            if self.base_path:
                return f"{self.base_path}/{name}"
            return name

        async def save(self, name: str, content: BinaryIO) -> str:
            """Upload file to S3."""
            key = self._get_key(name)

            try:
                self.s3_client.upload_fileobj(
                    content,
                    self.bucket_name,
                    key,
                    ExtraArgs={'ACL': self.acl}
                )
                return name
            except ClientError as e:
                raise IOError(f"Failed to upload to S3: {e}")

        async def delete(self, name: str) -> bool:
            """Delete file from S3."""
            key = self._get_key(name)

            try:
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
                return True
            except ClientError:
                return False

        async def exists(self, name: str) -> bool:
            """Check if file exists on S3."""
            key = self._get_key(name)

            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
                return True
            except ClientError:
                return False

        async def url(self, name: str) -> str:
            """Get URL for accessing file on S3."""
            key = self._get_key(name)
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{key}"

        async def size(self, name: str) -> int:
            """Get file size from S3."""
            key = self._get_key(name)

            try:
                response = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
                return response['ContentLength']
            except ClientError:
                return 0

except ImportError:
    # boto3 not installed
    S3FileStorage = None


__all__ = [
    'FileStorage',
    'LocalFileStorage',
    'S3FileStorage',
    'get_default_storage',
    'set_default_storage',
]
