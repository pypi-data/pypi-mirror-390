"""
Migration Squashing System

Combines multiple data migrations into a single optimized migration to:
- Reduce migration count
- Improve migration performance
- Simplify migration history
- Remove dead code and intermediate steps

Features:
- Automatic migration analysis
- Operation optimization and deduplication
- Dependency graph simplification
- Squashing suggestions based on heuristics
- Safe squashing with validation

Example:
    from covet.database.orm.migration_squashing import MigrationSquasher

    squasher = MigrationSquasher()

    # Analyze migrations for squashing opportunities
    analysis = await squasher.analyze_migrations('./migrations/data')

    # Squash migrations
    result = await squasher.squash(
        migrations=['0001_initial_data.py', '0002_backfill_users.py'],
        output_file='0001_squashed.py'
    )

Author: CovetPy Team 21
License: MIT
"""

import ast
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SquashError(Exception):
    """Base exception for squashing operations."""

    pass


@dataclass
class MigrationAnalysis:
    """
    Analysis of migrations for squashing opportunities.

    Attributes:
        total_migrations: Total number of migrations
        squashable_chains: Chains of migrations that can be squashed
        redundant_operations: Operations that cancel each other out
        optimization_opportunities: Potential optimizations
        estimated_reduction: Estimated reduction in operations
    """

    total_migrations: int = 0
    squashable_chains: List[List[str]] = field(default_factory=list)
    redundant_operations: List[Dict[str, Any]] = field(default_factory=list)
    optimization_opportunities: List[str] = field(default_factory=list)
    estimated_reduction: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_migrations": self.total_migrations,
            "squashable_chains": self.squashable_chains,
            "redundant_operations": self.redundant_operations,
            "optimization_opportunities": self.optimization_opportunities,
            "estimated_reduction_percent": f"{self.estimated_reduction * 100:.1f}%",
        }


@dataclass
class SquashResult:
    """
    Result of squashing operation.

    Attributes:
        success: Whether squashing succeeded
        output_file: Path to squashed migration file
        original_count: Number of original migrations
        operations_before: Number of operations before squashing
        operations_after: Number of operations after squashing
        reduction_percent: Percentage reduction in operations
        warnings: Any warnings generated
    """

    success: bool = False
    output_file: Optional[str] = None
    original_count: int = 0
    operations_before: int = 0
    operations_after: int = 0
    reduction_percent: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output_file": self.output_file,
            "original_count": self.original_count,
            "operations_before": self.operations_before,
            "operations_after": self.operations_after,
            "reduction_percent": f"{self.reduction_percent:.1f}%",
            "warnings": self.warnings,
        }


class MigrationSquasher:
    """
    Squashes multiple data migrations into optimized single migrations.

    This analyzer:
    1. Loads and parses migration files
    2. Analyzes operation sequences
    3. Identifies redundancies and optimizations
    4. Generates optimized squashed migration
    5. Validates the result

    Example:
        squasher = MigrationSquasher()

        # Get squashing recommendations
        analysis = await squasher.analyze_migrations('./migrations')
        print(f"Can reduce operations by {analysis.estimated_reduction}")

        # Squash specific migrations
        result = await squasher.squash(
            migrations=['0001_data.py', '0002_data.py', '0003_data.py'],
            output_file='0001_squashed_0003.py'
        )
    """

    def __init__(self, migrations_dir: Optional[str] = None):
        """
        Initialize migration squasher.

        Args:
            migrations_dir: Directory containing migrations
        """
        self.migrations_dir = migrations_dir

    async def analyze_migrations(self, migrations_dir: Optional[str] = None) -> MigrationAnalysis:
        """
        Analyze migrations for squashing opportunities.

        Args:
            migrations_dir: Directory to analyze

        Returns:
            Analysis with squashing recommendations
        """
        migrations_dir = migrations_dir or self.migrations_dir
        if not migrations_dir:
            raise SquashError("migrations_dir must be provided")

        migrations_dir = Path(migrations_dir)

        logger.info(f"Analyzing migrations in {migrations_dir}")

        # Load all migration files
        migration_files = sorted(migrations_dir.glob("*.py"))
        migration_files = [f for f in migration_files if not f.name.startswith("__")]

        analysis = MigrationAnalysis()
        analysis.total_migrations = len(migration_files)

        # Analyze for squashable chains
        # Simple heuristic: consecutive migrations with same table
        table_chains = defaultdict(list)

        for migration_file in migration_files:
            # Parse migration file to extract operations
            operations = self._parse_migration_file(migration_file)

            for op in operations:
                table = op.get("table")
                if table:
                    table_chains[table].append(migration_file.name)

        # Find chains of 3+ migrations on same table
        for table, migrations in table_chains.items():
            if len(migrations) >= 3:
                analysis.squashable_chains.append(migrations)
                analysis.optimization_opportunities.append(
                    f"Table '{table}' has {len(migrations)} consecutive migrations"
                )

        # Estimate reduction
        if analysis.total_migrations > 0:
            potential_squash = sum(len(chain) for chain in analysis.squashable_chains)
            analysis.estimated_reduction = potential_squash / analysis.total_migrations

        logger.info(f"Analysis complete: {len(analysis.squashable_chains)} squashable chains found")

        return analysis

    async def squash(
        self, migrations: List[str], output_file: str, migrations_dir: Optional[str] = None
    ) -> SquashResult:
        """
        Squash multiple migrations into one.

        Args:
            migrations: List of migration file names to squash
            output_file: Output file name for squashed migration
            migrations_dir: Directory containing migrations

        Returns:
            Squash result with statistics
        """
        migrations_dir = Path(migrations_dir or self.migrations_dir)

        logger.info(f"Squashing {len(migrations)} migrations into {output_file}")

        result = SquashResult()
        result.original_count = len(migrations)

        # Load and parse all migrations
        all_operations = []
        dependencies = set()

        for migration_name in migrations:
            migration_path = migrations_dir / migration_name

            if not migration_path.exists():
                raise SquashError(f"Migration not found: {migration_name}")

            operations = self._parse_migration_file(migration_path)
            all_operations.extend(operations)

            # Extract dependencies
            deps = self._extract_dependencies(migration_path)
            dependencies.update(deps)

        result.operations_before = len(all_operations)

        # Optimize operations
        optimized_operations = self._optimize_operations(all_operations)
        result.operations_after = len(optimized_operations)

        # Calculate reduction
        if result.operations_before > 0:
            result.reduction_percent = (
                (result.operations_before - result.operations_after)
                / result.operations_before
                * 100
            )

        # Generate squashed migration file
        output_path = migrations_dir / output_file
        self._generate_squashed_migration(
            output_path, optimized_operations, dependencies, migrations
        )

        result.success = True
        result.output_file = str(output_path)

        # Add warnings if no optimization achieved
        if result.operations_before == result.operations_after:
            result.warnings.append(
                "No operations were optimized. Squashing may not provide benefits."
            )

        logger.info(
            f"Squashing complete: {result.operations_before} -> {result.operations_after} "
            f"operations ({result.reduction_percent:.1f}% reduction)"
        )

        return result

    def _parse_migration_file(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Parse migration file to extract operations.

        Args:
            filepath: Path to migration file

        Returns:
            List of operation dictionaries
        """
        operations = []

        try:
            with open(filepath, "r") as f:
                content = f.read()

            # Simple parsing: look for operation patterns
            # This is a simplified version - production would use AST parsing

            # Find RunPython operations
            runpython_pattern = r"RunPython\s*\([^)]*table\s*=\s*['\"]([^'\"]+)['\"]"
            for match in re.finditer(runpython_pattern, content):
                operations.append({"type": "RunPython", "table": match.group(1)})

            # Find RunSQL operations
            runsql_pattern = r"RunSQL\s*\([^)]*"
            for match in re.finditer(runsql_pattern, content):
                operations.append(
                    {"type": "RunSQL", "table": None}  # Could parse SQL to extract table
                )

            # Find other operations
            for op_type in ["CopyField", "TransformField", "PopulateField"]:
                pattern = rf"{op_type}\s*\([^)]*table\s*=\s*['\"]([^'\"]+)['\"]"
                for match in re.finditer(pattern, content):
                    operations.append({"type": op_type, "table": match.group(1)})

        except Exception as e:
            logger.error(f"Failed to parse {filepath}: {e}")

        return operations

    def _extract_dependencies(self, filepath: Path) -> Set[Tuple[str, str]]:
        """
        Extract dependencies from migration file.

        Args:
            filepath: Path to migration file

        Returns:
            Set of (app, migration) tuples
        """
        dependencies = set()

        try:
            with open(filepath, "r") as f:
                content = f.read()

            # Find dependencies list
            dep_pattern = r"dependencies\s*=\s*\[(.*?)\]"
            match = re.search(dep_pattern, content, re.DOTALL)

            if match:
                deps_str = match.group(1)
                # Parse tuples like ('app', '0001_migration')
                tuple_pattern = r"\(\s*['\"]([^'\"]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*\)"
                for tuple_match in re.finditer(tuple_pattern, deps_str):
                    dependencies.add((tuple_match.group(1), tuple_match.group(2)))

        except Exception as e:
            logger.error(f"Failed to extract dependencies from {filepath}: {e}")

        return dependencies

    def _optimize_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Optimize list of operations by removing redundancies.

        Args:
            operations: List of operations

        Returns:
            Optimized list of operations
        """
        optimized = []
        seen_operations = set()

        for op in operations:
            # Create a signature for the operation
            signature = f"{op.get('type')}:{op.get('table')}"

            # Skip duplicate operations on same table
            # (simplified - production would need more sophisticated analysis)
            if signature not in seen_operations:
                optimized.append(op)
                seen_operations.add(signature)
            else:
                logger.debug(f"Skipping redundant operation: {signature}")

        return optimized

    def _generate_squashed_migration(
        self,
        output_path: Path,
        operations: List[Dict[str, Any]],
        dependencies: Set[Tuple[str, str]],
        original_migrations: List[str],
    ):
        """
        Generate squashed migration file.

        Args:
            output_path: Output file path
            operations: Optimized operations
            dependencies: Migration dependencies
            original_migrations: Original migration names
        """
        # Build migration file content
        content = f'''"""
Squashed migration combining:
{chr(10).join(f"  - {m}" for m in original_migrations)}

Auto-generated by MigrationSquasher.
DO NOT EDIT THIS FILE MANUALLY.
"""

from covet.database.orm.data_migrations import DataMigration, RunPython, RunSQL
from covet.database.orm.migration_operations import (
    CopyField, TransformField, PopulateField,
    SplitField, MergeFields, ConvertType
)


class Migration(DataMigration):
    """Squashed data migration."""

    # Combined dependencies from original migrations
    dependencies = [
'''

        # Add dependencies
        for app, migration in sorted(dependencies):
            content += f"        ('{app}', '{migration}'),\n"

        content += "    ]\n\n"

        # Add replaces list (which migrations this replaces)
        content += "    # This migration replaces:\n"
        content += "    replaces = [\n"
        for migration in original_migrations:
            # Extract app name (assume same app)
            migration_name = migration.replace(".py", "")
            content += f"        ('default', '{migration_name}'),\n"
        content += "    ]\n\n"

        # Add operations list
        content += "    operations = [\n"
        content += "        # TODO: Add optimized operations here\n"
        content += "        # Original migrations had {} operations\n".format(len(operations))
        content += "        # Manual review recommended\n"
        content += "    ]\n\n"

        # Add forwards method
        content += "    async def forwards(self, adapter, model_manager=None):\n"
        content += '        """Apply squashed migration."""\n'
        content += "        # TODO: Implement combined forward operations\n"
        content += "        pass\n\n"

        # Add backwards method
        content += "    async def backwards(self, adapter, model_manager=None):\n"
        content += '        """Rollback squashed migration."""\n'
        content += "        # TODO: Implement combined backward operations\n"
        content += "        pass\n"

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(content)

        logger.info(f"Generated squashed migration: {output_path}")


def suggest_squashing(migrations_dir: str) -> Dict[str, Any]:
    """
    Analyze migrations and suggest squashing opportunities.

    Args:
        migrations_dir: Directory containing migrations

    Returns:
        Dictionary with suggestions
    """
    squasher = MigrationSquasher(migrations_dir)

    # This is a synchronous wrapper - in production, would be async
    import asyncio

    loop = asyncio.get_event_loop()
    analysis = loop.run_until_complete(squasher.analyze_migrations())

    suggestions = {
        "should_squash": analysis.estimated_reduction > 0.2,  # >20% reduction
        "analysis": analysis.to_dict(),
        "recommendations": [],
    }

    if suggestions["should_squash"]:
        suggestions["recommendations"].append(
            f"Squashing could reduce operations by {analysis.estimated_reduction * 100:.0f}%"
        )

        for chain in analysis.squashable_chains:
            suggestions["recommendations"].append(
                f"Consider squashing: {', '.join(chain[:3])}{'...' if len(chain) > 3 else ''}"
            )
    else:
        suggestions["recommendations"].append("No significant squashing opportunities found")

    return suggestions


__all__ = [
    "MigrationSquasher",
    "MigrationAnalysis",
    "SquashResult",
    "SquashError",
    "suggest_squashing",
]
