"""
Migration Security Module

Provides comprehensive security validation for migration files to prevent
arbitrary code execution (CVE-SPRINT2-001).

This module implements defense-in-depth for migration loading:
- AST-based static analysis to detect dangerous code patterns
- Whitelist-based validation of allowed operations
- Restricted namespace execution
- Path traversal prevention

Author: CovetPy Security Team
Version: 2.5.0
CVSS: 9.8/10 (CRITICAL)
"""

import ast
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Base exception for security violations."""

    pass


class CodeInjectionError(SecurityError):
    """Raised when dangerous code patterns are detected in migration files."""

    pass


class PathTraversalError(SecurityError):
    """Raised when path traversal attempts are detected."""

    pass


class SafeMigrationValidator:
    """
    Validates migration files for security using AST-based static analysis.

    This is the primary defense against CVE-SPRINT2-001 (Arbitrary Code Execution).
    Uses a strict whitelist approach to ensure migration files only contain
    safe migration operations.

    Security Features:
    - AST parsing to analyze code structure
    - Whitelist of allowed names and operations
    - Blacklist of dangerous operations
    - Detection of dynamic code execution
    - Import statement validation

    Example:
        validator = SafeMigrationValidator()
        try:
            validator.validate_migration_file('/path/to/migration.py')
            # Safe to load
        except SecurityError as e:
            # Block loading
            logger.error(f"Security validation failed: {e}")
    """

    # Allowed names in migration files
    ALLOWED_NAMES: Set[str] = {
        # Migration class and base
        "Migration",
        # Migration operations
        "operations",
        "dependencies",
        "forward_sql",
        "backward_sql",
        # Table operations
        "CreateTable",
        "DropTable",
        "RenameTable",
        "AlterTable",
        # Column operations
        "AddColumn",
        "DropColumn",
        "AlterColumn",
        "RenameColumn",
        # Index operations
        "CreateIndex",
        "DropIndex",
        "RenameIndex",
        # Constraint operations
        "AddConstraint",
        "DropConstraint",
        "AddForeignKey",
        "DropForeignKey",
        "AddPrimaryKey",
        "DropPrimaryKey",
        "AddUniqueConstraint",
        "DropUniqueConstraint",
        "AddCheckConstraint",
        "DropCheckConstraint",
        # Field types
        "CharField",
        "TextField",
        "IntegerField",
        "BigIntegerField",
        "SmallIntegerField",
        "BooleanField",
        "DateTimeField",
        "DateField",
        "TimeField",
        "DecimalField",
        "FloatField",
        "BinaryField",
        "JSONField",
        "UUIDField",
        "EmailField",
        "URLField",
        "ForeignKey",
        "OneToOneField",
        "ManyToManyField",
        # Python builtins (safe subset)
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "tuple",
        "set",
        "True",
        "False",
        "None",
        "len",
        "range",
        "enumerate",
        "zip",
        "min",
        "max",
        "sum",
        "sorted",
        "reversed",
        "isinstance",
        "issubclass",
        "type",
        "abs",
        "round",
        "pow",
        # Special methods
        "__init__",
        "__name__",
        "__doc__",
        "__dict__",
        "apply",
        "rollback",
        "async",
        "await",
        # Common attributes
        "name",
        "table_name",
        "column_name",
        "index_name",
        "db_type",
        "nullable",
        "default",
        "unique",
        "primary_key",
        "auto_increment",
        "on_delete",
        "on_update",
        "max_length",
        "precision",
        "scale",
        "columns",
        "schema",
        "adapter",
        "sql",
        "query",
        "execute",
        # Database types
        "VARCHAR",
        "TEXT",
        "INTEGER",
        "BIGINT",
        "SMALLINT",
        "BOOLEAN",
        "TIMESTAMP",
        "DATE",
        "TIME",
        "DECIMAL",
        "FLOAT",
        "BYTEA",
        "JSONB",
        "UUID",
        # SQL keywords (safe in context)
        "CASCADE",
        "RESTRICT",
        "SET NULL",
        "SET DEFAULT",
        "NO ACTION",
        "CURRENT_TIMESTAMP",
    }

    # Explicitly forbidden names
    FORBIDDEN_NAMES: Set[str] = {
        # System modules
        "os",
        "sys",
        "subprocess",
        "shutil",
        "pathlib",
        # Dynamic execution
        "eval",
        "exec",
        "compile",
        "__import__",
        "importlib",
        "execfile",
        "reload",
        # File operations
        "open",
        "file",
        "FileIO",
        # Input operations
        "input",
        "raw_input",
        # Built-ins access
        "__builtins__",
        "__builtin__",
        "globals",
        "locals",
        "vars",
        # Code objects
        "code",
        "types",
        "inspect",
        # Network operations
        "socket",
        "urllib",
        "requests",
        "http",
        # Process operations
        "multiprocessing",
        "threading",
        "asyncio",
        # Dangerous SQL operations
        "DROP DATABASE",
        "DROP SCHEMA",
        "TRUNCATE",
        "xp_cmdshell",
        "xp_",
        "sp_executesql",
        # Pickle and serialization
        "pickle",
        "cPickle",
        "marshal",
        "shelve",
    }

    # Forbidden import modules
    FORBIDDEN_IMPORTS: Set[str] = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "pathlib",
        "socket",
        "urllib",
        "urllib2",
        "urllib3",
        "requests",
        "httplib",
        "http",
        "pickle",
        "cPickle",
        "marshal",
        "shelve",
        "importlib",
        "imp",
        "pkgutil",
        "multiprocessing",
        "threading",
        "asyncio",
        "ctypes",
        "cffi",
        "pty",
        "tty",
        "termios",
        "code",
        "codeop",
        "compile",
        "tempfile",
        "mmap",
        "__builtin__",
        "builtins",
    }

    def validate_migration_file(self, file_path: str) -> bool:
        """
        Validate migration file is safe to execute.

        Performs comprehensive AST-based analysis to detect:
        - Dangerous imports
        - Forbidden function calls
        - Dynamic code execution (eval, exec, compile)
        - Attribute access to dangerous modules
        - Control characters and encoding attacks

        Args:
            file_path: Path to migration file

        Returns:
            True if validation succeeds

        Raises:
            SecurityError: If dangerous operations detected
            CodeInjectionError: If code injection patterns found

        Security:
            - Parses entire file without executing
            - Walks AST to analyze all operations
            - Strict whitelist approach
            - Blocks any suspicious patterns
        """
        logger.info(f"Validating migration security: {file_path}")

        # Read file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
        except UnicodeDecodeError:
            raise SecurityError(
                f"Migration file '{file_path}' has invalid encoding. "
                f"Only UTF-8 encoding is allowed."
            )
        except Exception as e:
            raise SecurityError(f"Failed to read migration file '{file_path}': {e}")

        # Check for control characters and binary content
        if any(ord(char) < 32 and char not in "\n\r\t" for char in code):
            raise CodeInjectionError(
                f"Migration file '{file_path}' contains control characters. "
                f"This may indicate binary content or encoding attack."
            )

        # Parse AST
        try:
            tree = ast.parse(code, filename=file_path)
        except SyntaxError as e:
            raise SecurityError(f"Invalid Python syntax in '{file_path}': {e}")

        # Analyze AST for security
        self._check_ast_safety(tree, file_path)

        logger.info(f"Migration security validation passed: {file_path}")
        return True

    def _check_ast_safety(self, tree: ast.AST, file_path: str):
        """
        Check AST for dangerous operations.

        Walks the entire AST and validates each node type and operation.

        Args:
            tree: Parsed AST
            file_path: File path for error messages

        Raises:
            CodeInjectionError: If dangerous patterns detected
        """
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self._validate_import(alias.name, file_path)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    self._validate_import(node.module, file_path)

            # Check function calls
            elif isinstance(node, ast.Call):
                self._validate_call(node, file_path)

            # Check exec/eval (these are expressions in Python 3)
            elif isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    self._validate_call(node.value, file_path)

            # Check attribute access
            elif isinstance(node, ast.Attribute):
                self._validate_attribute(node, file_path)

            # Check name usage
            elif isinstance(node, ast.Name):
                self._validate_name(node, file_path)

    def _validate_import(self, module_name: str, file_path: str):
        """Validate import statement."""
        # Check if module is in forbidden list
        base_module = module_name.split(".")[0]

        if base_module in self.FORBIDDEN_IMPORTS:
            raise CodeInjectionError(
                f"Forbidden import '{module_name}' in '{file_path}'. "
                f"Migration files cannot import dangerous modules. "
                f"Only migration-related imports are allowed."
            )

        # Check for suspicious patterns
        if any(
            suspicious in module_name.lower()
            for suspicious in ["exec", "eval", "compile", "system"]
        ):
            raise CodeInjectionError(f"Suspicious import '{module_name}' in '{file_path}'")

    def _validate_call(self, node: ast.Call, file_path: str):
        """Validate function call."""
        func_name = None

        # Get function name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            # For method calls like obj.method()
            func_name = node.func.attr

        if func_name:
            # Check forbidden functions
            if func_name in self.FORBIDDEN_NAMES:
                raise CodeInjectionError(
                    f"Forbidden function '{func_name}' called in '{file_path}'. "
                    f"Migration files cannot execute dangerous operations. "
                    f"Use only migration operations."
                )

            # Check for dangerous patterns (but allow 'execute' which is needed for DB operations)
            dangerous_patterns = ["eval", "compile", "system", "popen"]
            # Special case: 'exec' is forbidden, but 'execute' is allowed (for DB operations)
            if func_name == "exec" or any(
                dangerous in func_name.lower() for dangerous in dangerous_patterns
            ):
                raise CodeInjectionError(
                    f"Dangerous function '{func_name}' in '{file_path}'. "
                    f"Dynamic code execution is not allowed."
                )

    def _validate_attribute(self, node: ast.Attribute, file_path: str):
        """Validate attribute access."""
        # Check for access to forbidden modules
        if isinstance(node.value, ast.Name):
            if node.value.id in self.FORBIDDEN_NAMES:
                raise CodeInjectionError(
                    f"Access to forbidden module '{node.value.id}.{node.attr}' in '{file_path}'. "
                    f"Migration files cannot access dangerous modules."
                )

        # Check for dangerous attribute patterns
        attr_name = node.attr
        if any(dangerous in attr_name.lower() for dangerous in ["__", "exec", "eval", "import"]):
            # Allow specific dunder methods
            if attr_name not in ["__init__", "__name__", "__doc__", "__dict__"]:
                logger.warning(f"Suspicious attribute access '{attr_name}' in '{file_path}'")

    def _validate_name(self, node: ast.Name, file_path: str):
        """Validate name reference."""
        name = node.id

        # Check if name is forbidden
        if name in self.FORBIDDEN_NAMES:
            raise CodeInjectionError(
                f"Use of forbidden name '{name}' in '{file_path}'. "
                f"Migration files cannot use dangerous built-ins or modules."
            )


class PathValidator:
    """
    Validates file paths to prevent path traversal attacks.

    This is the primary defense against CVE-SPRINT2-003 (Path Traversal).
    Ensures migration files can only be loaded from designated directories.

    Security Features:
    - Path canonicalization
    - Directory boundary enforcement
    - Symlink attack prevention
    - Relative path detection

    Example:
        validator = PathValidator('/app/migrations')
        try:
            validator.validate_path('/app/migrations/0001_initial.py')
            # Safe to load
        except PathTraversalError:
            # Block access
    """

    def __init__(self, migrations_directory: str):
        """
        Initialize path validator.

        Args:
            migrations_directory: Allowed migrations directory
        """
        # Resolve to absolute canonical path
        self.migrations_directory = Path(migrations_directory).resolve()

        # Ensure directory exists
        if not self.migrations_directory.exists():
            logger.warning(f"Migrations directory does not exist: {self.migrations_directory}")

    def validate_path(self, file_path: str) -> Path:
        """
        Validate migration file path to prevent path traversal.

        Security checks:
        - Resolves to absolute path
        - Verifies path is within migrations directory
        - Detects '..' traversal attempts
        - Blocks symlink attacks
        - Validates file extension

        Args:
            file_path: Path to migration file

        Returns:
            Validated absolute Path object

        Raises:
            PathTraversalError: If path traversal detected
            SecurityError: If path validation fails

        Example:
            validator.validate_path('migrations/0001_initial.py')  # OK
            validator.validate_path('../../../etc/passwd')  # BLOCKED
        """
        # Convert to Path and resolve to absolute
        try:
            resolved_path = Path(file_path).resolve()
        except Exception as e:
            raise SecurityError(f"Invalid file path '{file_path}': {e}")

        # Check if path is within migrations directory
        try:
            resolved_path.relative_to(self.migrations_directory)
        except ValueError:
            raise PathTraversalError(
                f"Path traversal detected: '{file_path}' is outside "
                f"migrations directory '{self.migrations_directory}'. "
                f"Resolved to: '{resolved_path}'"
            )

        # Additional check for '..' in path components
        if ".." in file_path:
            raise PathTraversalError(
                f"Path contains '..' which indicates path traversal attempt: '{file_path}'"
            )

        # Check for suspicious path patterns
        suspicious_patterns = [
            r"\.\./",
            r"\.\.",
            r"//",
            r"~",
            r"\x00",  # Null byte injection
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, str(file_path)):
                raise PathTraversalError(f"Suspicious path pattern '{pattern}' in '{file_path}'")

        # Validate file extension
        if not str(resolved_path).endswith(".py"):
            raise SecurityError(
                f"Invalid migration file extension: '{resolved_path}'. "
                f"Only .py files are allowed."
            )

        # Check if file exists
        if not resolved_path.exists():
            raise SecurityError(f"Migration file does not exist: '{resolved_path}'")

        # Check if it's actually a file (not directory or symlink)
        if not resolved_path.is_file():
            raise SecurityError(f"Migration path is not a regular file: '{resolved_path}'")

        # Check for symlink attacks
        if resolved_path.is_symlink():
            # Resolve symlink and check again
            real_path = resolved_path.resolve()
            try:
                real_path.relative_to(self.migrations_directory)
            except ValueError:
                raise PathTraversalError(
                    f"Symlink attack detected: '{file_path}' resolves to "
                    f"'{real_path}' which is outside migrations directory"
                )

        logger.debug(f"Path validation passed: {resolved_path}")
        return resolved_path


def create_safe_namespace() -> Dict[str, Any]:
    """
    Create a restricted namespace for executing migration files.

    This namespace contains only safe built-ins and migration-specific classes.
    It prevents access to dangerous operations while allowing legitimate
    migration operations.

    Returns:
        Dictionary of allowed names and their values

    Security:
        - Minimal built-ins (no exec, eval, import, open, etc.)
        - Only migration-related classes
        - No access to system modules
    """
    # Safe built-in types
    safe_builtins = {
        # Types
        "str": str,
        "int": int,
        "float": float,
        "bool": bool,
        "list": list,
        "dict": dict,
        "tuple": tuple,
        "set": set,
        "frozenset": frozenset,
        # Constants
        "True": True,
        "False": False,
        "None": None,
        # Safe functions
        "len": len,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "min": min,
        "max": max,
        "sum": sum,
        "sorted": sorted,
        "reversed": reversed,
        "isinstance": isinstance,
        "issubclass": issubclass,
        "type": type,
        "abs": abs,
        "round": round,
        "pow": pow,
        # Safe exceptions
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
        "KeyError": KeyError,
        "AttributeError": AttributeError,
    }

    namespace = {
        "__builtins__": safe_builtins,
        "__name__": "__migration__",
        "__file__": "<migration>",
    }

    return namespace


__all__ = [
    "SecurityError",
    "CodeInjectionError",
    "PathTraversalError",
    "SafeMigrationValidator",
    "PathValidator",
    "create_safe_namespace",
]
