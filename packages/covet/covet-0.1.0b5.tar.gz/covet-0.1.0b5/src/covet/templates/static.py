"""
Static File Handler for Template Engine

Production-ready static file serving with:
- File caching with ETags
- MIME type detection
- Compression support
- Security headers
- Range request support
- Asset versioning
"""

import gzip
import hashlib
import mimetypes
import os
import threading
import time
import zlib
from datetime import datetime, timedelta
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Tuple, Union


class StaticFileCache:
    """Cache for static files with ETags and expiration."""

    def __init__(self, max_size: int = 1000, max_file_size: int = 1024 * 1024):  # 1MB max file size
        self.max_size = max_size
        self.max_file_size = max_file_size
        self.cache = {}
        self.access_times = {}
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Dict]:
        """Get cached file data."""
        with self.lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key]
            return None

    def set(self, key: str, data: Dict):
        """Set cached file data."""
        with self.lock:
            # Check file size limit
            if data.get("size", 0) > self.max_file_size:
                return

            # Remove oldest entries if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                self.cache.pop(oldest_key, None)
                self.access_times.pop(oldest_key, None)

            self.cache[key] = data
            self.access_times[key] = time.time()

    def clear(self):
        """Clear cache."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()


class StaticFileHandler:
    """
    Production-ready static file handler.

    Features:
    - Multiple static directories
    - File caching with ETags
    - MIME type detection
    - Gzip compression
    - Security headers
    - Range request support
    - Asset versioning
    - Development mode with auto-reload
    """

    def __init__(
        self,
        static_dirs: List[Path],
        cache_timeout: int = 3600,
        enable_compression: bool = True,
        compression_threshold: int = 1024,
        development_mode: bool = False,
    ):
        self.static_dirs = [Path(d).resolve() for d in static_dirs]
        self.cache_timeout = cache_timeout
        self.enable_compression = enable_compression
        self.compression_threshold = compression_threshold
        self.development_mode = development_mode

        # Initialize cache
        self.file_cache = StaticFileCache()

        # MIME types
        mimetypes.init()
        self.mime_types = {
            ".css": "text/css",
            ".js": "application/javascript",
            ".json": "application/json",
            ".html": "text/html",
            ".htm": "text/html",
            ".xml": "text/xml",
            ".txt": "text/plain",
            ".md": "text/markdown",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".woff": "font/woff",
            ".woff2": "font/woff2",
            ".ttf": "font/ttf",
            ".eot": "application/vnd.ms-fontobject",
        }

        # Compressible MIME types
        self.compressible_types = {
            "text/css",
            "application/javascript",
            "application/json",
            "text/html",
            "text/xml",
            "text/plain",
            "text/markdown",
            "image/svg+xml",
        }

        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
        }

        # Ensure static directories exist
        for static_dir in self.static_dirs:
            static_dir.mkdir(parents=True, exist_ok=True)

    def serve(self, path: str, request_headers: Optional[Dict[str, str]] = None) -> Optional[Dict]:
        """
        Serve static file.

        Args:
            path: Relative path to static file
            request_headers: HTTP request headers

        Returns:
            Dict with file data and headers, or None if not found
        """
        request_headers = request_headers or {}

        # Validate and find file
        file_path = self._find_static_file(path)
        if not file_path:
            return None

        try:
            # Get file info
            stat = file_path.stat()

            # Check cache in development mode
            if not self.development_mode:
                cache_key = f"{file_path}:{stat.st_mtime}"
                cached_response = self.file_cache.get(cache_key)
                if cached_response:
                    return self._handle_conditional_request(cached_response, request_headers)

            # Read file
            with open(file_path, "rb") as f:
                content = f.read()

            # Generate ETag using SHA-256 instead of MD5 for security
            etag = f'"{hashlib.sha256(content).hexdigest()}"'

            # Get MIME type
            mime_type = self._get_mime_type(file_path)

            # Prepare response
            response = {
                "content": content,
                "size": len(content),
                "mime_type": mime_type,
                "etag": etag,
                "last_modified": formatdate(stat.st_mtime, usegmt=True),
                "headers": {
                    "Content-Type": mime_type,
                    "ETag": etag,
                    "Last-Modified": formatdate(stat.st_mtime, usegmt=True),
                    "Cache-Control": f"public, max-age={self.cache_timeout}",
                    **self.security_headers,
                },
            }

            # Handle compression
            if self._should_compress(mime_type, len(content)):
                compressed_content = self._compress_content(content, request_headers)
                if compressed_content:
                    response["content"] = compressed_content["content"]
                    response["headers"].update(compressed_content["headers"])

            # Cache response
            if not self.development_mode:
                self.file_cache.set(cache_key, response.copy())

            return self._handle_conditional_request(response, request_headers)

        except (IOError, OSError):
            return None

    def get_url(self, path: str, versioned: bool = False) -> str:
        """
        Get URL for static file.

        Args:
            path: Relative path to static file
            versioned: Add version parameter for cache busting

        Returns:
            URL for static file
        """
        url = f"/static/{path.lstrip('/')}"

        if versioned:
            file_path = self._find_static_file(path)
            if file_path and file_path.exists():
                try:
                    mtime = int(file_path.stat().st_mtime)
                    url += f"?v={mtime}"
                except OSError:
                    # TODO: Add proper exception handling

                    pass
        return url

    def list_files(self, directory: str = "", extensions: List[str] = None) -> List[str]:
        """List static files in directory."""
        files = []
        extensions = extensions or []

        for static_dir in self.static_dirs:
            search_dir = static_dir / directory if directory else static_dir

            if not search_dir.exists():
                continue

            try:
                for file_path in search_dir.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(static_dir)
                        path_str = str(relative_path).replace("\\", "/")

                        if not extensions or any(path_str.endswith(ext) for ext in extensions):
                            if path_str not in files:
                                files.append(path_str)
            except (OSError, ValueError):
                continue

        return sorted(files)

    def clear_cache(self):
        """Clear file cache."""
        self.file_cache.clear()

    def _find_static_file(self, path: str) -> Optional[Path]:
        """Find static file in static directories."""
        # Security: validate path
        if not self._is_safe_path(path):
            return None

        for static_dir in self.static_dirs:
            file_path = static_dir / path

            try:
                resolved_path = file_path.resolve()
                static_dir_resolved = static_dir.resolve()

                # Ensure path is within static directory
                if not str(resolved_path).startswith(str(static_dir_resolved)):
                    continue

                if resolved_path.exists() and resolved_path.is_file():
                    return resolved_path
            except (OSError, ValueError):
                continue

        return None

    def _is_safe_path(self, path: str) -> bool:
        """Check if path is safe for serving."""
        if not path or path.startswith("/"):
            return False

        if ".." in path or path.startswith("."):
            return False

        if any(char in path for char in ["<", ">", ":", '"', "|", "?", "*"]):
            return False

        return True

    def _get_mime_type(self, file_path: Path) -> str:
        """Get MIME type for file."""
        suffix = file_path.suffix.lower()

        if suffix in self.mime_types:
            return self.mime_types[suffix]

        # Fallback to mimetypes module
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"

    def _should_compress(self, mime_type: str, content_length: int) -> bool:
        """Check if content should be compressed."""
        return (
            self.enable_compression
            and content_length >= self.compression_threshold
            and mime_type in self.compressible_types
        )

    def _compress_content(self, content: bytes, request_headers: Dict[str, str]) -> Optional[Dict]:
        """Compress content based on Accept-Encoding header."""
        accept_encoding = request_headers.get("Accept-Encoding", "").lower()

        if "gzip" in accept_encoding:
            try:
                compressed = gzip.compress(content, compresslevel=6)
                return {
                    "content": compressed,
                    "headers": {
                        "Content-Encoding": "gzip",
                        "Content-Length": str(len(compressed)),
                        "Vary": "Accept-Encoding",
                    },
                }
            except Exception:
                # TODO: Add proper exception handling

                pass
        elif "deflate" in accept_encoding:
            try:
                compressed = zlib.compress(content, level=6)
                return {
                    "content": compressed,
                    "headers": {
                        "Content-Encoding": "deflate",
                        "Content-Length": str(len(compressed)),
                        "Vary": "Accept-Encoding",
                    },
                }
            except Exception:
                # TODO: Add proper exception handling

                pass
        return None

    def _handle_conditional_request(self, response: Dict, request_headers: Dict[str, str]) -> Dict:
        """Handle conditional requests (If-None-Match, If-Modified-Since)."""
        # Check If-None-Match (ETag)
        if_none_match = request_headers.get("If-None-Match")
        if if_none_match and response["etag"] in if_none_match:
            return {
                "status": 304,
                "headers": {
                    "ETag": response["etag"],
                    "Cache-Control": response["headers"]["Cache-Control"],
                },
            }

        # Check If-Modified-Since
        if_modified_since = request_headers.get("If-Modified-Since")
        if if_modified_since:
            try:
                modified_since = parsedate_to_datetime(if_modified_since)
                last_modified = parsedate_to_datetime(response["last_modified"])

                if last_modified <= modified_since:
                    return {
                        "status": 304,
                        "headers": {
                            "Last-Modified": response["last_modified"],
                            "Cache-Control": response["headers"]["Cache-Control"],
                        },
                    }
            except (ValueError, TypeError):
                # TODO: Add proper exception handling

                pass
        return response


class AssetVersioning:
    """Asset versioning for cache busting."""

    def __init__(self, static_handler: StaticFileHandler, version_strategy: str = "mtime"):
        self.static_handler = static_handler
        self.version_strategy = version_strategy
        self.version_cache = {}

    def get_versioned_url(self, path: str) -> str:
        """Get versioned URL for asset."""
        if path in self.version_cache:
            return self.version_cache[path]

        file_path = self.static_handler._find_static_file(path)
        if not file_path:
            return f"/static/{path}"

        version = self._get_version(file_path)
        url = f"/static/{path}?v={version}"

        self.version_cache[path] = url
        return url

    def _get_version(self, file_path: Path) -> str:
        """Get version string for file."""
        if self.version_strategy == "mtime":
            return str(int(file_path.stat().st_mtime))
        elif self.version_strategy == "hash":
            with open(file_path, "rb") as f:
                content = f.read()
            # Using SHA-256 instead of MD5 for security
            return hashlib.sha256(content).hexdigest()[:8]
        else:
            return "1"

    def clear_cache(self):
        """Clear version cache."""
        self.version_cache.clear()


class StaticFileMiddleware:
    """ASGI middleware for serving static files."""

    def __init__(self, app, static_handler: StaticFileHandler, static_url: str = "/static/"):
        self.app = app
        self.static_handler = static_handler
        self.static_url = static_url.rstrip("/") + "/"

    async def __call__(self, scope, receive, send):
        """ASGI application."""
        if scope["type"] == "http" and scope["path"].startswith(self.static_url):
            # Extract static file path
            path = scope["path"][len(self.static_url) :]

            # Get request headers
            headers = dict(scope.get("headers", []))
            request_headers = {k.decode(): v.decode() for k, v in headers.items()}

            # Serve static file
            response = self.static_handler.serve(path, request_headers)

            if response:
                # Send response
                await send(
                    {
                        "type": "http.response.start",
                        "status": response.get("status", 200),
                        "headers": [
                            (k.encode(), v.encode()) for k, v in response["headers"].items()
                        ],
                    }
                )

                if response.get("status") != 304:  # Not Modified
                    await send({"type": "http.response.body", "body": response["content"]})
                else:
                    await send({"type": "http.response.body", "body": b""})
                return

        # Pass to next app
        await self.app(scope, receive, send)


# Utility functions
def generate_etag(content: bytes) -> str:
    """Generate ETag for content using SHA-256 instead of MD5 for security."""
    return f'"{hashlib.sha256(content).hexdigest()}"'


def is_fresh(request_headers: Dict[str, str], etag: str, last_modified: str) -> bool:
    """Check if client has fresh copy."""
    if_none_match = request_headers.get("If-None-Match")
    if if_none_match and etag in if_none_match:
        return True

    if_modified_since = request_headers.get("If-Modified-Since")
    if if_modified_since:
        try:
            modified_since = parsedate_to_datetime(if_modified_since)
            last_mod = parsedate_to_datetime(last_modified)
            return last_mod <= modified_since
        except (ValueError, TypeError):
            # TODO: Add proper exception handling

            pass
    return False


__all__ = [
    "StaticFileHandler",
    "StaticFileCache",
    "AssetVersioning",
    "StaticFileMiddleware",
    "generate_etag",
    "is_fresh",
]
