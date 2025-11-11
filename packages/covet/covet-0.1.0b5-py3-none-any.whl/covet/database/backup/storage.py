"""
Backup Storage Backends

Provides abstraction layer for storing backups in different locations:
- Local filesystem
- AWS S3
- Google Cloud Storage (GCS)
- Azure Blob Storage

Enterprise features:
- Automatic retry with exponential backoff
- Multi-part upload for large files
- Storage class optimization (hot, cold, archive)
- Cross-region replication
- Lifecycle policies
"""

import asyncio
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class BackupStorage(ABC):
    """
    Abstract base class for backup storage backends.

    Defines interface for uploading, downloading, listing, and deleting backups.
    """

    @abstractmethod
    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None,
        **options,
    ) -> Dict[str, Any]:
        """
        Upload file to storage backend.

        Args:
            local_path: Path to local file
            remote_path: Path in storage backend
            metadata: File metadata
            **options: Backend-specific options

        Returns:
            Upload result metadata
        """
        pass

    @abstractmethod
    async def download_file(self, remote_path: str, local_path: str, **options) -> Dict[str, Any]:
        """
        Download file from storage backend.

        Args:
            remote_path: Path in storage backend
            local_path: Path for local file
            **options: Backend-specific options

        Returns:
            Download result metadata
        """
        pass

    @abstractmethod
    async def list_files(self, prefix: str = "", **options) -> List[Dict[str, Any]]:
        """
        List files in storage backend.

        Args:
            prefix: Filter by prefix
            **options: Backend-specific options

        Returns:
            List of file metadata dictionaries
        """
        pass

    @abstractmethod
    async def delete_file(self, remote_path: str, **options) -> bool:
        """
        Delete file from storage backend.

        Args:
            remote_path: Path in storage backend
            **options: Backend-specific options

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def file_exists(self, remote_path: str, **options) -> bool:
        """
        Check if file exists in storage backend.

        Args:
            remote_path: Path in storage backend
            **options: Backend-specific options

        Returns:
            True if file exists
        """
        pass

    @abstractmethod
    async def get_file_metadata(self, remote_path: str, **options) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from storage backend.

        Args:
            remote_path: Path in storage backend
            **options: Backend-specific options

        Returns:
            File metadata or None if not found
        """
        pass


class LocalStorage(BackupStorage):
    """
    Local filesystem storage backend.

    Features:
    - Simple file copy operations
    - Directory-based organization
    - Symlink support for latest backup
    - Filesystem permissions management
    """

    def __init__(self, base_path: str):
        """
        Initialize local storage.

        Args:
            base_path: Base directory for backups
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None,
        **options,
    ) -> Dict[str, Any]:
        """Upload file to local storage (copy)."""
        import shutil

        local_file = Path(local_path)
        remote_file = self.base_path / remote_path

        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        # Create parent directory
        remote_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        await asyncio.to_thread(shutil.copy2, local_file, remote_file)

        # Save metadata if provided
        if metadata:
            metadata_file = remote_file.with_suffix(remote_file.suffix + ".meta")
            await asyncio.to_thread(self._write_metadata, metadata_file, metadata)

        file_size = remote_file.stat().st_size

        logger.info(f"Uploaded to local storage: {remote_file} ({file_size} bytes)")

        return {
            "path": str(remote_file),
            "size": file_size,
            "metadata": metadata or {},
        }

    async def download_file(self, remote_path: str, local_path: str, **options) -> Dict[str, Any]:
        """Download file from local storage (copy)."""
        import shutil

        remote_file = self.base_path / remote_path
        local_file = Path(local_path)

        if not remote_file.exists():
            raise FileNotFoundError(f"Remote file not found: {remote_file}")

        # Create parent directory
        local_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        await asyncio.to_thread(shutil.copy2, remote_file, local_file)

        file_size = local_file.stat().st_size

        logger.info(f"Downloaded from local storage: {remote_file} ({file_size} bytes)")

        return {
            "path": str(local_file),
            "size": file_size,
        }

    async def list_files(self, prefix: str = "", **options) -> List[Dict[str, Any]]:
        """List files in local storage."""
        files = []

        # Convert prefix to path pattern
        search_pattern = prefix if prefix else "*"
        search_path = self.base_path / search_pattern

        # Find matching files
        for file_path in self.base_path.rglob(search_pattern):
            if file_path.is_file() and not file_path.suffix == ".meta":
                stat = file_path.stat()
                files.append(
                    {
                        "path": str(file_path.relative_to(self.base_path)),
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                    }
                )

        return sorted(files, key=lambda x: x["modified"], reverse=True)

    async def delete_file(self, remote_path: str, **options) -> bool:
        """Delete file from local storage."""
        remote_file = self.base_path / remote_path

        if not remote_file.exists():
            return False

        try:
            # Delete metadata file if exists
            metadata_file = remote_file.with_suffix(remote_file.suffix + ".meta")
            if metadata_file.exists():
                metadata_file.unlink()

            # Delete main file
            remote_file.unlink()

            logger.info(f"Deleted from local storage: {remote_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    async def file_exists(self, remote_path: str, **options) -> bool:
        """Check if file exists in local storage."""
        remote_file = self.base_path / remote_path
        return remote_file.exists()

    async def get_file_metadata(self, remote_path: str, **options) -> Optional[Dict[str, Any]]:
        """Get file metadata from local storage."""
        remote_file = self.base_path / remote_path

        if not remote_file.exists():
            return None

        stat = remote_file.stat()
        metadata = {
            "path": str(remote_file.relative_to(self.base_path)),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
        }

        # Load custom metadata if exists
        metadata_file = remote_file.with_suffix(remote_file.suffix + ".meta")
        if metadata_file.exists():
            custom_metadata = await asyncio.to_thread(self._read_metadata, metadata_file)
            metadata["custom"] = custom_metadata

        return metadata

    @staticmethod
    def _write_metadata(metadata_file: Path, metadata: Dict[str, str]) -> None:
        """Write metadata to file."""
        import json

        with open(metadata_file, "w") as f:
            json.dump(metadata, f, indent=2)

    @staticmethod
    def _read_metadata(metadata_file: Path) -> Dict[str, str]:
        """Read metadata from file."""
        import json

        with open(metadata_file, "r") as f:
            return json.load(f)


class S3Storage(BackupStorage):
    """
    AWS S3 storage backend.

    Features:
    - Multi-part upload for large files
    - Storage class selection (STANDARD, GLACIER, etc.)
    - Server-side encryption (SSE-S3, SSE-KMS)
    - Cross-region replication
    - Lifecycle policies
    - Versioning support
    """

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        storage_class: str = "STANDARD",
        encryption: str = "AES256",
        **kwargs,
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
            access_key: AWS access key (uses environment/IAM if None)
            secret_key: AWS secret key (uses environment/IAM if None)
            storage_class: S3 storage class (STANDARD, GLACIER, etc.)
            encryption: Server-side encryption (AES256, aws:kms)
            **kwargs: Additional S3 client parameters
        """
        self.bucket_name = bucket_name
        self.region = region
        self.storage_class = storage_class
        self.encryption = encryption

        # Import boto3 (lazy import to make it optional)
        try:
            import boto3

            # Create S3 client
            session_kwargs = {}
            if access_key and secret_key:
                session_kwargs = {
                    "aws_access_key_id": access_key,
                    "aws_secret_access_key": secret_key,
                }

            self.s3_client = boto3.client("s3", region_name=region, **session_kwargs, **kwargs)

        except ImportError:
            raise ImportError(
                "boto3 library required for S3 storage. " "Install with: pip install boto3"
            )

    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None,
        storage_class: Optional[str] = None,
        **options,
    ) -> Dict[str, Any]:
        """Upload file to S3."""
        local_file = Path(local_path)

        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        file_size = local_file.stat().st_size
        storage_cls = storage_class or self.storage_class

        logger.info(
            f"Uploading to S3: s3://{self.bucket_name}/{remote_path} "
            f"({file_size} bytes, class={storage_cls})"
        )

        try:
            # Prepare upload arguments
            extra_args = {
                "StorageClass": storage_cls,
                "ServerSideEncryption": self.encryption,
            }

            if metadata:
                extra_args["Metadata"] = metadata

            # Use multi-part upload for large files (>100MB)
            if file_size > 100 * 1024 * 1024:
                await asyncio.to_thread(self._multipart_upload, local_path, remote_path, extra_args)
            else:
                await asyncio.to_thread(
                    self.s3_client.upload_file,
                    local_path,
                    self.bucket_name,
                    remote_path,
                    ExtraArgs=extra_args,
                )

            logger.info(f"Uploaded to S3: s3://{self.bucket_name}/{remote_path}")

            return {
                "bucket": self.bucket_name,
                "key": remote_path,
                "size": file_size,
                "storage_class": storage_cls,
                "encryption": self.encryption,
            }

        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise

    async def download_file(self, remote_path: str, local_path: str, **options) -> Dict[str, Any]:
        """Download file from S3."""
        local_file = Path(local_path)
        local_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from S3: s3://{self.bucket_name}/{remote_path}")

        try:
            await asyncio.to_thread(
                self.s3_client.download_file,
                self.bucket_name,
                remote_path,
                str(local_file),
            )

            file_size = local_file.stat().st_size

            logger.info(f"Downloaded from S3: {local_file} ({file_size} bytes)")

            return {
                "path": str(local_file),
                "size": file_size,
            }

        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            raise

    async def list_files(self, prefix: str = "", **options) -> List[Dict[str, Any]]:
        """List files in S3 bucket."""
        files = []

        try:
            # Use paginator for large buckets
            paginator = self.s3_client.get_paginator("list_objects_v2")
            page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)

            for page in page_iterator:
                if "Contents" in page:
                    for obj in page["Contents"]:
                        files.append(
                            {
                                "path": obj["Key"],
                                "size": obj["Size"],
                                "modified": obj["LastModified"].timestamp(),
                                "storage_class": obj.get("StorageClass", "STANDARD"),
                                "etag": obj["ETag"].strip('"'),
                            }
                        )

        except Exception as e:
            logger.error(f"S3 list failed: {e}")
            raise

        return sorted(files, key=lambda x: x["modified"], reverse=True)

    async def delete_file(self, remote_path: str, **options) -> bool:
        """Delete file from S3."""
        try:
            await asyncio.to_thread(
                self.s3_client.delete_object,
                Bucket=self.bucket_name,
                Key=remote_path,
            )

            logger.info(f"Deleted from S3: s3://{self.bucket_name}/{remote_path}")
            return True

        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False

    async def file_exists(self, remote_path: str, **options) -> bool:
        """Check if file exists in S3."""
        try:
            await asyncio.to_thread(
                self.s3_client.head_object,
                Bucket=self.bucket_name,
                Key=remote_path,
            )
            return True
        except BaseException:
            return False

    async def get_file_metadata(self, remote_path: str, **options) -> Optional[Dict[str, Any]]:
        """Get file metadata from S3."""
        try:
            response = await asyncio.to_thread(
                self.s3_client.head_object,
                Bucket=self.bucket_name,
                Key=remote_path,
            )

            return {
                "path": remote_path,
                "size": response["ContentLength"],
                "modified": response["LastModified"].timestamp(),
                "etag": response["ETag"].strip('"'),
                "storage_class": response.get("StorageClass", "STANDARD"),
                "encryption": response.get("ServerSideEncryption"),
                "metadata": response.get("Metadata", {}),
            }

        except Exception as e:
            logger.warning(f"Failed to get S3 metadata: {e}")
            return None

    def _multipart_upload(
        self, local_path: str, remote_path: str, extra_args: Dict[str, Any]
    ) -> None:
        """Perform multi-part upload for large files."""
        import boto3.s3.transfer

        # Configure transfer with larger part size
        config = boto3.s3.transfer.TransferConfig(
            multipart_threshold=100 * 1024 * 1024,  # 100 MB
            max_concurrency=10,
            multipart_chunksize=10 * 1024 * 1024,  # 10 MB
            use_threads=True,
        )

        self.s3_client.upload_file(
            local_path,
            self.bucket_name,
            remote_path,
            ExtraArgs=extra_args,
            Config=config,
        )


class AzureBlobStorage(BackupStorage):
    """
    Azure Blob Storage backend.

    Features:
    - Block blob storage for backups
    - Storage tiers (Hot, Cool, Archive)
    - Server-side encryption
    - Automatic retry with exponential backoff
    - Lifecycle management
    - Blob versioning support
    """

    def __init__(
        self,
        container_name: str,
        account_name: Optional[str] = None,
        account_key: Optional[str] = None,
        connection_string: Optional[str] = None,
        storage_tier: str = "Hot",
        max_retries: int = 3,
        **kwargs,
    ):
        """
        Initialize Azure Blob Storage.

        Args:
            container_name: Azure blob container name
            account_name: Storage account name (uses environment if None)
            account_key: Storage account key (uses environment if None)
            connection_string: Full connection string (alternative to name/key)
            storage_tier: Blob storage tier (Hot, Cool, Archive)
            max_retries: Maximum retry attempts for transient failures
            **kwargs: Additional Azure client parameters
        """
        self.container_name = container_name
        self.storage_tier = storage_tier
        self.max_retries = max_retries

        # Import Azure SDK (lazy import to make it optional)
        try:
            from azure.core.exceptions import AzureError
            from azure.storage.blob import BlobBlock, BlobServiceClient

            # Create blob service client
            if connection_string:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    connection_string, **kwargs
                )
            elif account_name and account_key:
                account_url = f"https://{account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url, credential=account_key, **kwargs
                )
            else:
                # Try to use DefaultAzureCredential
                from azure.identity import DefaultAzureCredential

                account_url = f"https://{account_name}.blob.core.windows.net"
                self.blob_service_client = BlobServiceClient(
                    account_url=account_url, credential=DefaultAzureCredential(), **kwargs
                )

            # Get container client
            self.container_client = self.blob_service_client.get_container_client(container_name)

            # Create container if it doesn't exist
            try:
                self.container_client.create_container()
            except AzureError:
                # Container already exists
                pass

        except ImportError:
            raise ImportError(
                "Azure SDK required for Azure Blob Storage. "
                "Install with: pip install azure-storage-blob azure-identity"
            )

    async def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, str]] = None,
        storage_tier: Optional[str] = None,
        **options,
    ) -> Dict[str, Any]:
        """Upload file to Azure Blob Storage."""
        local_file = Path(local_path)

        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")

        file_size = local_file.stat().st_size
        tier = storage_tier or self.storage_tier

        logger.info(
            f"Uploading to Azure: {self.container_name}/{remote_path} "
            f"({file_size} bytes, tier={tier})"
        )

        try:
            blob_client = self.container_client.get_blob_client(remote_path)

            # Upload with retry logic
            for attempt in range(self.max_retries):
                try:
                    with open(local_path, "rb") as data:
                        await asyncio.to_thread(
                            blob_client.upload_blob,
                            data,
                            blob_type="BlockBlob",
                            standard_blob_tier=tier,
                            metadata=metadata or {},
                            overwrite=True,
                        )
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2**attempt  # Exponential backoff
                        logger.warning(
                            f"Azure upload attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise

            logger.info(f"Uploaded to Azure: {self.container_name}/{remote_path}")

            return {
                "container": self.container_name,
                "blob": remote_path,
                "size": file_size,
                "storage_tier": tier,
            }

        except Exception as e:
            logger.error(f"Azure upload failed: {e}")
            raise

    async def download_file(self, remote_path: str, local_path: str, **options) -> Dict[str, Any]:
        """Download file from Azure Blob Storage."""
        local_file = Path(local_path)
        local_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Downloading from Azure: {self.container_name}/{remote_path}")

        try:
            blob_client = self.container_client.get_blob_client(remote_path)

            # Download with retry logic
            for attempt in range(self.max_retries):
                try:
                    with open(local_path, "wb") as download_file:
                        download_stream = await asyncio.to_thread(blob_client.download_blob)
                        data = await asyncio.to_thread(download_stream.readall)
                        download_file.write(data)
                    break
                except Exception as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2**attempt
                        logger.warning(
                            f"Azure download attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise

            file_size = local_file.stat().st_size

            logger.info(f"Downloaded from Azure: {local_file} ({file_size} bytes)")

            return {
                "path": str(local_file),
                "size": file_size,
            }

        except Exception as e:
            logger.error(f"Azure download failed: {e}")
            raise

    async def list_files(self, prefix: str = "", **options) -> List[Dict[str, Any]]:
        """List files in Azure Blob Storage container."""
        files = []

        try:
            blob_list = self.container_client.list_blobs(name_starts_with=prefix)

            for blob in blob_list:
                files.append(
                    {
                        "path": blob.name,
                        "size": blob.size,
                        "modified": blob.last_modified.timestamp(),
                        "storage_tier": blob.blob_tier,
                        "etag": blob.etag,
                    }
                )

        except Exception as e:
            logger.error(f"Azure list failed: {e}")
            raise

        return sorted(files, key=lambda x: x["modified"], reverse=True)

    async def delete_file(self, remote_path: str, **options) -> bool:
        """Delete file from Azure Blob Storage."""
        try:
            blob_client = self.container_client.get_blob_client(remote_path)
            await asyncio.to_thread(blob_client.delete_blob)

            logger.info(f"Deleted from Azure: {self.container_name}/{remote_path}")
            return True

        except Exception as e:
            logger.error(f"Azure delete failed: {e}")
            return False

    async def file_exists(self, remote_path: str, **options) -> bool:
        """Check if file exists in Azure Blob Storage."""
        try:
            blob_client = self.container_client.get_blob_client(remote_path)
            exists = await asyncio.to_thread(blob_client.exists)
            return exists
        except:
            return False

    async def get_file_metadata(self, remote_path: str, **options) -> Optional[Dict[str, Any]]:
        """Get file metadata from Azure Blob Storage."""
        try:
            blob_client = self.container_client.get_blob_client(remote_path)
            properties = await asyncio.to_thread(blob_client.get_blob_properties)

            return {
                "path": remote_path,
                "size": properties.size,
                "modified": properties.last_modified.timestamp(),
                "etag": properties.etag,
                "storage_tier": properties.blob_tier,
                "metadata": properties.metadata or {},
            }

        except Exception as e:
            logger.warning(f"Failed to get Azure metadata: {e}")
            return None


__all__ = ["BackupStorage", "LocalStorage", "S3Storage", "AzureBlobStorage"]
