"""
Template Loader with Caching and Inheritance Support

Handles template loading, caching, and file system operations.
"""

import os
import threading
import time
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TemplateCache:
    """LRU cache with TTL for templates."""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = OrderedDict()
        self.access_times = {}
        self.lock = threading.RLock()

    def get(self, key: str) -> Optional[Tuple[str, float]]:
        """Get cached template with timestamp."""
        with self.lock:
            if key not in self.cache:
                return None

            # Check TTL
            cached_time = self.access_times[key]
            if time.time() - cached_time > self.ttl:
                del self.cache[key]
                del self.access_times[key]
                return None

            # Move to end (LRU)
            content = self.cache.pop(key)
            self.cache[key] = content

            return content, cached_time

    def set(self, key: str, content: str, mtime: float):
        """Set cached template."""
        with self.lock:
            # Remove oldest entries if at capacity
            while len(self.cache) >= self.max_size:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = (content, mtime)
            self.access_times[key] = time.time()

    def clear(self):
        """Clear all cached templates."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()

    def invalidate(self, key: str):
        """Invalidate specific cached template."""
        with self.lock:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)


class TemplateLoader:
    """
    Template loader with file system monitoring and caching.

    Features:
    - Multiple template directories
    - LRU cache with TTL
    - File modification time checking
    - Template inheritance support
    - Secure path handling
    """

    def __init__(self, template_dirs: List[Path], cache_size: int = 1000, cache_ttl: int = 3600):
        self.template_dirs = [Path(d).resolve() for d in template_dirs]
        self.cache = TemplateCache(cache_size, cache_ttl)
        self.encoding = "utf-8"

        # Ensure template directories exist (only if they're writable)
        for template_dir in self.template_dirs:
            try:
                template_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError):
                # Skip directories we can't create (like system directories)

                pass

    def load(self, template_name: str) -> str:
        """
        Load template content by name.

        Args:
            template_name: Name of template to load

        Returns:
            Template content as string

        Raises:
            TemplateNotFound: If template doesn't exist
            TemplateSecurityError: If path is not secure
        """
        # Validate template name for security
        self._validate_template_name(template_name)

        # Find template file
        template_path = self._find_template(template_name)
        if not template_path:
            raise TemplateNotFound(f"Template not found: {template_name}")

        # Check cache
        cache_key = str(template_path)
        cached_result = self.cache.get(cache_key)

        if cached_result:
            cached_content, cached_mtime = cached_result

            # Check if file was modified
            current_mtime = template_path.stat().st_mtime
            if current_mtime <= cached_mtime:
                return cached_content

        # Load from file
        try:
            with open(template_path, "r", encoding=self.encoding) as f:
                content = f.read()

            # Cache the content
            file_mtime = template_path.stat().st_mtime
            self.cache.set(cache_key, content, file_mtime)

            return content

        except IOError as e:
            raise TemplateNotFound(f"Cannot read template '{template_name}': {str(e)}")

    def get_template_path(self, template_name: str) -> Optional[Path]:
        """Get full path for template name."""
        self._validate_template_name(template_name)
        return self._find_template(template_name)

    def template_exists(self, template_name: str) -> bool:
        """Check if template exists."""
        try:
            return self._find_template(template_name) is not None
        except TemplateSecurityError:
            return False

    def list_templates(self, directory: str = "") -> List[str]:
        """List all available templates in directory."""
        templates = []

        for template_dir in self.template_dirs:
            search_dir = template_dir / directory if directory else template_dir

            if not search_dir.exists():
                continue

            try:
                for file_path in search_dir.rglob("*.html"):
                    # Get relative path from template directory
                    relative_path = file_path.relative_to(template_dir)
                    template_name = str(relative_path).replace("\\", "/")

                    if template_name not in templates:
                        templates.append(template_name)
            except (OSError, ValueError):
                continue

        return sorted(templates)

    def clear_cache(self):
        """Clear template cache."""
        self.cache.clear()

    def invalidate_template(self, template_name: str):
        """Invalidate specific template in cache."""
        template_path = self._find_template(template_name)
        if template_path:
            self.cache.invalidate(str(template_path))

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self.cache.lock:
            return {
                "size": len(self.cache.cache),
                "max_size": self.cache.max_size,
                "ttl": self.cache.ttl,
            }

    def _find_template(self, template_name: str) -> Optional[Path]:
        """Find template file in template directories."""
        for template_dir in self.template_dirs:
            template_path = template_dir / template_name

            # Ensure path is within template directory (security)
            try:
                resolved_path = template_path.resolve()
                template_dir_resolved = template_dir.resolve()

                # Check if the resolved path is within the template directory
                if not str(resolved_path).startswith(str(template_dir_resolved)):
                    continue

                if resolved_path.exists() and resolved_path.is_file():
                    return resolved_path

            except (OSError, ValueError):
                continue

        return None

    def _validate_template_name(self, template_name: str):
        """Validate template name for security."""
        if not template_name:
            raise TemplateSecurityError("Template name cannot be empty")

        if template_name.startswith("/"):
            raise TemplateSecurityError("Template name cannot start with '/'")

        if ".." in template_name:
            raise TemplateSecurityError("Template name cannot contain '..'")

        if any(char in template_name for char in ["<", ">", ":", '"', "|", "?", "*"]):
            raise TemplateSecurityError("Template name contains invalid characters")

        # Normalize path separators
        normalized = template_name.replace("\\", "/")
        if normalized != template_name:
            raise TemplateSecurityError("Template name should use forward slashes only")


class TemplateWatcher:
    """File system watcher for template changes."""

    def __init__(self, loader: TemplateLoader):
        self.loader = loader
        self.watched_files = {}
        self.callbacks = []

    def watch_template(self, template_name: str):
        """Add template to watch list."""
        template_path = self.loader.get_template_path(template_name)
        if template_path and template_path.exists():
            self.watched_files[template_name] = template_path.stat().st_mtime

    def check_changes(self) -> List[str]:
        """Check for changed templates."""
        changed = []

        for template_name, last_mtime in list(self.watched_files.items()):
            template_path = self.loader.get_template_path(template_name)

            if not template_path or not template_path.exists():
                # Template was deleted
                del self.watched_files[template_name]
                changed.append(template_name)
                continue

            current_mtime = template_path.stat().st_mtime
            if current_mtime > last_mtime:
                self.watched_files[template_name] = current_mtime
                changed.append(template_name)

        return changed

    def add_change_callback(self, callback: callable):
        """Add callback for template changes."""
        self.callbacks.append(callback)

    def notify_changes(self, changed_templates: List[str]):
        """Notify callbacks of changes."""
        for callback in self.callbacks:
            try:
                callback(changed_templates)
            except Exception:
                pass  # Ignore callback errors


class TemplateNotFound(Exception):
    """Exception raised when template is not found."""


class TemplateSecurityError(Exception):
    """Exception raised for template security violations."""


# Template discovery utilities
def discover_templates(directories: List[Path], extensions: List[str] = None) -> Dict[str, Path]:
    """Discover all templates in given directories."""
    extensions = extensions or [".html", ".htm", ".xml", ".txt"]
    templates = {}

    for directory in directories:
        if not directory.exists():
            continue

        for ext in extensions:
            pattern = f"**/*{ext}"
            for template_path in directory.glob(pattern):
                if template_path.is_file():
                    # Use relative path as template name
                    relative_path = template_path.relative_to(directory)
                    template_name = str(relative_path).replace("\\", "/")
                    templates[template_name] = template_path

    return templates


def validate_template_syntax(content: str, template_name: str = None) -> List[str]:
    """Basic template syntax validation."""
    errors = []
    lines = content.split("\n")

    # Track opening/closing tags
    tag_stack = []

    for line_num, line in enumerate(lines, 1):
        # Find template tags
        import re

        # Check for unmatched braces
        open_braces = line.count("{{")
        close_braces = line.count("}}")
        if open_braces != close_braces:
            errors.append(f"Line {line_num}: Unmatched template braces")

        # Check for unmatched blocks
        block_start = re.findall(r"{%\s*(\w+)", line)
        block_end = re.findall(r"{%\s*end(\w+)", line)

        for tag in block_start:
            if tag in ["if", "for", "block", "macro"]:
                tag_stack.append((tag, line_num))

        for tag in block_end:
            if tag_stack and tag_stack[-1][0] == tag:
                tag_stack.pop()
            else:
                errors.append(f"Line {line_num}: Unmatched end{tag}")

    # Check for unclosed blocks
    for tag, line_num in tag_stack:
        errors.append(f"Line {line_num}: Unclosed {tag} block")

    return errors


__all__ = [
    "TemplateLoader",
    "TemplateCache",
    "TemplateWatcher",
    "TemplateNotFound",
    "TemplateSecurityError",
    "discover_templates",
    "validate_template_syntax",
]
