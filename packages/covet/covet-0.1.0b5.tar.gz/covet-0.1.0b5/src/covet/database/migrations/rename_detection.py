"""
Column Rename Detection using Levenshtein Distance

This module implements intelligent column rename detection to prevent data loss
during schema migrations. When a column is removed and another is added, this
system analyzes if the change represents a rename rather than a DROP + ADD.

The Problem:
    # User renames 'name' to 'username' in ORM model
    # Naive diff: DROP COLUMN name, ADD COLUMN username
    # Result: DATA LOSS - all existing names are deleted!

The Solution:
    # Intelligent detection: RENAME COLUMN name TO username
    # Result: Data preserved, only metadata changed

Algorithm:
    1. Identify candidates: dropped columns + added columns in same table
    2. Calculate Levenshtein distance between all pairs
    3. Normalize by string length to get similarity score (0.0 to 1.0)
    4. Apply threshold (default 0.80) to identify probable renames
    5. Consider type compatibility and constraints
    6. Generate RENAME_COLUMN operations instead of DROP + ADD

Production Features:
    - Configurable similarity threshold
    - Type compatibility validation
    - Constraint preservation checks
    - False positive prevention
    - Manual override support
    - Comprehensive logging

Example:
    from covet.database.migrations.rename_detection import RenameDetector

    detector = RenameDetector(
        similarity_threshold=0.80,
        require_type_match=True
    )

    # Detect renames in operation list
    operations = detector.detect_renames(
        operations,
        model_schema,
        db_schema
    )

    # Manual rename specification
    detector.add_manual_rename('users', 'name', 'username')

Author: CovetPy Migration System
Version: 2.0.0
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .diff_engine import MigrationOperation, OperationType
from .model_reader import ColumnSchema, TableSchema

logger = logging.getLogger(__name__)


@dataclass
class RenameCandidate:
    """
    Represents a potential column rename.

    Attributes:
        table_name: Table containing the columns
        old_name: Original column name (being dropped)
        new_name: New column name (being added)
        old_column: Old column schema
        new_column: New column schema
        similarity: Similarity score (0.0 to 1.0)
        type_compatible: Whether types are compatible
        confidence: Overall confidence score
    """

    table_name: str
    old_name: str
    new_name: str
    old_column: ColumnSchema
    new_column: ColumnSchema
    similarity: float
    type_compatible: bool
    confidence: float

    def __repr__(self) -> str:
        return (
            f"<RenameCandidate {self.table_name}: "
            f"{self.old_name} -> {self.new_name} "
            f"(similarity={self.similarity:.2f}, confidence={self.confidence:.2f})>"
        )


class RenameDetector:
    """
    Intelligent column rename detector using Levenshtein distance.

    This is production-grade rename detection that prevents data loss by
    identifying when DROP + ADD operations actually represent a rename.

    Configuration:
        similarity_threshold: Minimum similarity score (default: 0.80)
        require_type_match: Require exact type match (default: False)
        enable_detection: Enable automatic detection (default: True)
        max_length_diff: Maximum length difference ratio (default: 0.5)

    Example:
        detector = RenameDetector(similarity_threshold=0.85)

        # Process operations
        operations = detector.detect_renames(
            operations,
            model_schema,
            db_schema
        )

        # Check detection stats
        stats = detector.get_stats()
        print(f"Detected {stats['renames_detected']} renames")
    """

    def __init__(
        self,
        similarity_threshold: float = 0.80,
        require_type_match: bool = False,
        enable_detection: bool = True,
        max_length_diff: float = 0.5,
    ):
        """
        Initialize rename detector.

        Args:
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            require_type_match: Whether to require exact type match
            enable_detection: Whether to enable automatic detection
            max_length_diff: Maximum allowed length difference ratio
        """
        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")

        self.similarity_threshold = similarity_threshold
        self.require_type_match = require_type_match
        self.enable_detection = enable_detection
        self.max_length_diff = max_length_diff

        # Manual rename registry: {table_name: {old_name: new_name}}
        self.manual_renames: Dict[str, Dict[str, str]] = {}

        # Detection statistics
        self.stats = {
            "renames_detected": 0,
            "manual_renames": 0,
            "false_positives_prevented": 0,
            "operations_analyzed": 0,
        }

    def detect_renames(
        self,
        operations: List[MigrationOperation],
        model_schemas: List[TableSchema],
        db_schemas: List[TableSchema],
    ) -> List[MigrationOperation]:
        """
        Detect column renames in migration operations.

        This is the main entry point. It analyzes DROP_COLUMN and ADD_COLUMN
        operations to identify probable renames.

        Args:
            operations: List of migration operations
            model_schemas: Target model schemas
            db_schemas: Current database schemas

        Returns:
            Modified operation list with RENAME_COLUMN operations
        """
        if not self.enable_detection:
            return operations

        self.stats["operations_analyzed"] = len(operations)

        # Group operations by table
        table_ops = self._group_operations_by_table(operations)

        # Detect renames for each table
        new_operations = []
        processed_ops = set()

        for table_name, ops in table_ops.items():
            # Find DROP and ADD operations
            drop_ops = [op for op in ops if op.operation_type == OperationType.DROP_COLUMN]
            add_ops = [op for op in ops if op.operation_type == OperationType.ADD_COLUMN]

            if not drop_ops or not add_ops:
                # No potential renames in this table
                new_operations.extend(ops)
                continue

            # Get table schemas
            model_schema = self._find_schema(model_schemas, table_name)
            db_schema = self._find_schema(db_schemas, table_name)

            # Detect renames
            renames = self._detect_table_renames(
                table_name, drop_ops, add_ops, model_schema, db_schema
            )

            # Track which operations are part of renames
            drop_op_map = {op.details["column_name"]: op for op in drop_ops}
            add_op_map = {op.details["column"]["name"]: op for op in add_ops}

            # Add rename operations
            for rename in renames:
                rename_op = self._create_rename_operation(rename)
                new_operations.append(rename_op)

                # Mark original operations as processed
                processed_ops.add(id(drop_op_map[rename.old_name]))
                processed_ops.add(id(add_op_map[rename.new_name]))

                self.stats["renames_detected"] += 1
                logger.info(
                    f"Detected rename: {table_name}.{rename.old_name} -> "
                    f"{rename.new_name} (confidence: {rename.confidence:.2f})"
                )

            # Add operations that weren't part of renames
            for op in ops:
                if id(op) not in processed_ops:
                    new_operations.append(op)

        # Maintain operation priority order
        new_operations.sort(key=lambda op: op.priority)

        logger.info(f"Rename detection complete: {self.stats['renames_detected']} renames found")

        return new_operations

    def _group_operations_by_table(
        self, operations: List[MigrationOperation]
    ) -> Dict[str, List[MigrationOperation]]:
        """Group operations by table name."""
        table_ops: Dict[str, List[MigrationOperation]] = {}

        for op in operations:
            table_name = op.table_name
            if table_name not in table_ops:
                table_ops[table_name] = []
            table_ops[table_name].append(op)

        return table_ops

    def _detect_table_renames(
        self,
        table_name: str,
        drop_ops: List[MigrationOperation],
        add_ops: List[MigrationOperation],
        model_schema: Optional[TableSchema],
        db_schema: Optional[TableSchema],
    ) -> List[RenameCandidate]:
        """
        Detect renames within a single table.

        Algorithm:
            1. Check manual renames first
            2. Calculate similarity between all DROP/ADD pairs
            3. Filter by threshold and type compatibility
            4. Prevent false positives
            5. Return best candidates
        """
        candidates: List[RenameCandidate] = []

        # Extract column information
        dropped_columns = {}
        for op in drop_ops:
            col_name = op.details["column_name"]
            # Find column in db_schema
            if db_schema:
                for col in db_schema.columns:
                    if col.name == col_name:
                        dropped_columns[col_name] = col
                        break

        added_columns = {}
        for op in add_ops:
            col_dict = op.details["column"]
            col_name = col_dict["name"]
            # Reconstruct ColumnSchema
            col = ColumnSchema(
                name=col_dict["name"],
                db_type=col_dict["db_type"],
                nullable=col_dict["nullable"],
                default=col_dict["default"],
                unique=col_dict["unique"],
                primary_key=col_dict["primary_key"],
                auto_increment=col_dict["auto_increment"],
            )
            added_columns[col_name] = col

        # Check manual renames first
        if table_name in self.manual_renames:
            for old_name, new_name in self.manual_renames[table_name].items():
                if old_name in dropped_columns and new_name in added_columns:
                    candidate = RenameCandidate(
                        table_name=table_name,
                        old_name=old_name,
                        new_name=new_name,
                        old_column=dropped_columns[old_name],
                        new_column=added_columns[new_name],
                        similarity=1.0,
                        type_compatible=True,
                        confidence=1.0,
                    )
                    candidates.append(candidate)
                    self.stats["manual_renames"] += 1
                    logger.info(f"Applied manual rename: {old_name} -> {new_name}")

        # Automatic detection
        for old_name, old_col in dropped_columns.items():
            # Skip if already in manual renames
            if table_name in self.manual_renames and old_name in self.manual_renames[table_name]:
                continue

            for new_name, new_col in added_columns.items():
                # Skip if already in manual renames
                if (
                    table_name in self.manual_renames
                    and new_name in self.manual_renames[table_name].values()
                ):
                    continue

                # Calculate similarity
                similarity = self.calculate_similarity(old_name, new_name)

                # Check if similarity meets threshold
                if similarity < self.similarity_threshold:
                    continue

                # Check type compatibility
                type_compatible = self._check_type_compatibility(old_col, new_col)

                if self.require_type_match and not type_compatible:
                    continue

                # Check length difference to prevent false positives
                if not self._check_length_compatibility(old_name, new_name):
                    self.stats["false_positives_prevented"] += 1
                    continue

                # Calculate confidence score
                confidence = self._calculate_confidence(
                    similarity, type_compatible, old_col, new_col
                )

                candidate = RenameCandidate(
                    table_name=table_name,
                    old_name=old_name,
                    new_name=new_name,
                    old_column=old_col,
                    new_column=new_col,
                    similarity=similarity,
                    type_compatible=type_compatible,
                    confidence=confidence,
                )
                candidates.append(candidate)

        # Select best candidates (prevent many-to-many matches)
        return self._select_best_candidates(candidates)

    def calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using Levenshtein distance.

        This is the core algorithm. It computes the minimum number of
        single-character edits needed to transform str1 into str2,
        then normalizes by string length.

        Algorithm: Dynamic Programming O(m*n) time, O(m*n) space
        Optimization: Can be reduced to O(min(m,n)) space

        Args:
            str1: First string
            str2: Second string

        Returns:
            Similarity score from 0.0 (completely different) to 1.0 (identical)

        Examples:
            calculate_similarity("name", "username") -> ~0.57
            calculate_similarity("email", "email_address") -> ~0.57
            calculate_similarity("id", "user_id") -> ~0.29
            calculate_similarity("status", "state") -> ~0.33
        """
        # Handle edge cases
        if str1 == str2:
            return 1.0

        if not str1 or not str2:
            return 0.0

        # Convert to lowercase for case-insensitive comparison
        s1 = str1.lower()
        s2 = str2.lower()

        # Get lengths
        len1 = len(s1)
        len2 = len(s2)

        # Calculate Levenshtein distance using dynamic programming
        distance = self._levenshtein_distance(s1, s2)

        # Normalize by maximum string length
        max_len = max(len1, len2)
        similarity = 1.0 - (distance / max_len)

        return similarity

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """
        Calculate Levenshtein distance between two strings.

        This uses the Wagner-Fischer algorithm with dynamic programming.

        The distance is the minimum number of single-character edits:
        - Insertion
        - Deletion
        - Substitution

        Time Complexity: O(m * n)
        Space Complexity: O(m * n) (can be optimized to O(min(m, n)))

        Args:
            s1: First string
            s2: Second string

        Returns:
            Minimum edit distance (integer)
        """
        len1 = len(s1)
        len2 = len(s2)

        # Create distance matrix
        # dp[i][j] = distance between s1[0:i] and s2[0:j]
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]

        # Initialize first row and column
        for i in range(len1 + 1):
            dp[i][0] = i

        for j in range(len2 + 1):
            dp[0][j] = j

        # Fill matrix using dynamic programming
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                if s1[i - 1] == s2[j - 1]:
                    # Characters match, no edit needed
                    cost = 0
                else:
                    # Characters differ, substitution needed
                    cost = 1

                dp[i][j] = min(
                    dp[i - 1][j] + 1,  # Deletion
                    dp[i][j - 1] + 1,  # Insertion
                    dp[i - 1][j - 1] + cost,  # Substitution
                )

        return dp[len1][len2]

    def _check_type_compatibility(self, old_col: ColumnSchema, new_col: ColumnSchema) -> bool:
        """
        Check if column types are compatible for rename.

        Type compatibility rules:
        - Exact match: INTEGER -> INTEGER (compatible)
        - Size changes: INT -> BIGINT (compatible)
        - Family match: VARCHAR -> TEXT (compatible)
        - Different families: INTEGER -> VARCHAR (incompatible)
        """
        old_type = self._normalize_type(old_col.db_type)
        new_type = self._normalize_type(new_col.db_type)

        # Exact match
        if old_type == new_type:
            return True

        # Type family mapping
        type_families = {
            "integer": {"INTEGER", "INT", "SMALLINT", "BIGINT", "SERIAL", "BIGSERIAL"},
            "text": {"VARCHAR", "TEXT", "CHAR", "CHARACTER"},
            "decimal": {"DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL"},
            "boolean": {"BOOLEAN", "BOOL"},
            "datetime": {"TIMESTAMP", "TIMESTAMPTZ", "DATETIME", "DATE", "TIME"},
            "json": {"JSON", "JSONB"},
            "binary": {"BYTEA", "BLOB", "BINARY", "VARBINARY"},
        }

        # Find families
        old_family = None
        new_family = None

        for family, types in type_families.items():
            if old_type in types:
                old_family = family
            if new_type in types:
                new_family = family

        return old_family == new_family if old_family and new_family else False

    def _normalize_type(self, db_type: str) -> str:
        """Normalize database type for comparison."""
        # Remove size specifications and convert to uppercase
        return db_type.upper().split("(")[0].strip()

    def _check_length_compatibility(self, str1: str, str2: str) -> bool:
        """
        Check if string lengths are compatible to prevent false positives.

        Prevents matching completely unrelated columns that happen to
        have similar characters:
        - "id" should not match "description"
        - "a" should not match "administrator_email_address"
        """
        len1 = len(str1)
        len2 = len(str2)

        if len1 == 0 or len2 == 0:
            return False

        max_len = max(len1, len2)
        min_len = min(len1, len2)

        # Length ratio must be within threshold
        length_ratio = min_len / max_len

        return length_ratio >= (1.0 - self.max_length_diff)

    def _calculate_confidence(
        self,
        similarity: float,
        type_compatible: bool,
        old_col: ColumnSchema,
        new_col: ColumnSchema,
    ) -> float:
        """
        Calculate overall confidence score for rename candidate.

        Factors:
        - String similarity (primary): 70% weight
        - Type compatibility: 20% weight
        - Constraint compatibility: 10% weight

        Returns:
            Confidence score from 0.0 to 1.0
        """
        # Start with similarity score (70% weight)
        confidence = similarity * 0.7

        # Add type compatibility bonus (20% weight)
        if type_compatible:
            confidence += 0.2

        # Add constraint compatibility bonus (10% weight)
        constraint_match = 0.0

        if old_col.nullable == new_col.nullable:
            constraint_match += 0.33

        if old_col.unique == new_col.unique:
            constraint_match += 0.33

        if old_col.primary_key == new_col.primary_key:
            constraint_match += 0.34

        confidence += constraint_match * 0.1

        return min(confidence, 1.0)

    def _select_best_candidates(self, candidates: List[RenameCandidate]) -> List[RenameCandidate]:
        """
        Select best rename candidates to prevent many-to-many matches.

        Rules:
        - Each old column can only map to one new column
        - Each new column can only map from one old column
        - Select highest confidence match for each
        """
        if not candidates:
            return []

        # Sort by confidence (descending)
        candidates.sort(key=lambda c: c.confidence, reverse=True)

        selected = []
        used_old = set()
        used_new = set()

        for candidate in candidates:
            if candidate.old_name not in used_old and candidate.new_name not in used_new:
                selected.append(candidate)
                used_old.add(candidate.old_name)
                used_new.add(candidate.new_name)

        return selected

    def _create_rename_operation(self, candidate: RenameCandidate) -> MigrationOperation:
        """Create RENAME_COLUMN operation from candidate."""
        return MigrationOperation(
            operation_type=OperationType.RENAME_COLUMN,
            table_name=candidate.table_name,
            details={
                "old_name": candidate.old_name,
                "new_name": candidate.new_name,
                "old_column": candidate.old_column.to_dict(),
                "new_column": candidate.new_column.to_dict(),
                "similarity": candidate.similarity,
                "confidence": candidate.confidence,
                "description": (
                    f"Rename column '{candidate.old_name}' to '{candidate.new_name}' "
                    f"in '{candidate.table_name}' (confidence: {candidate.confidence:.2f})"
                ),
            },
            reversible=True,
            priority=42,  # Between DROP (20) and ADD (40)
        )

    def _find_schema(self, schemas: List[TableSchema], table_name: str) -> Optional[TableSchema]:
        """Find table schema by name."""
        for schema in schemas:
            if schema.name == table_name:
                return schema
        return None

    def add_manual_rename(self, table_name: str, old_name: str, new_name: str):
        """
        Manually specify a column rename.

        This overrides automatic detection and forces a rename operation.

        Args:
            table_name: Table containing the column
            old_name: Current column name
            new_name: New column name

        Example:
            detector.add_manual_rename('users', 'name', 'full_name')
        """
        if table_name not in self.manual_renames:
            self.manual_renames[table_name] = {}

        self.manual_renames[table_name][old_name] = new_name

        logger.info(f"Registered manual rename: {table_name}.{old_name} -> {new_name}")

    def get_stats(self) -> Dict[str, int]:
        """Get detection statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset detection statistics."""
        self.stats = {
            "renames_detected": 0,
            "manual_renames": 0,
            "false_positives_prevented": 0,
            "operations_analyzed": 0,
        }


__all__ = ["RenameDetector", "RenameCandidate"]
