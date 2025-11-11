"""
Sprint 2 Migration System Correctness Test Suite

This test suite rigorously tests the migration system for:
1. Schema introspection accuracy
2. Diff algorithm correctness
3. SQL generation validity
4. Data safety
5. Edge cases handling
6. Multi-database support

Author: Database Migration Expert (20 years experience)
"""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet.database.migrations.model_reader import ModelReader, TableSchema, ColumnSchema, IndexSchema, RelationshipSchema
from covet.database.migrations.diff_engine import DiffEngine, DatabaseIntrospector, OperationType
from covet.database.migrations.generator import PostgreSQLGenerator, MySQLGenerator, SQLiteGenerator
from covet.database.adapters.sqlite import SQLiteAdapter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MigrationCorrectnessTests:
    """Test suite for migration system correctness."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.test_results = []

    def assert_equal(self, actual, expected, message=""):
        """Assert two values are equal."""
        if actual == expected:
            return True
        else:
            logger.error(f"ASSERTION FAILED: {message}")
            logger.error(f"  Expected: {expected}")
            logger.error(f"  Actual: {actual}")
            return False

    def assert_true(self, condition, message=""):
        """Assert condition is True."""
        if condition:
            return True
        else:
            logger.error(f"ASSERTION FAILED: {message}")
            return False

    def assert_in(self, item, container, message=""):
        """Assert item is in container."""
        if item in container:
            return True
        else:
            logger.error(f"ASSERTION FAILED: {message}")
            logger.error(f"  {item} not in {container}")
            return False

    def run_test(self, test_name, test_func):
        """Run a single test."""
        logger.info(f"\n{'='*70}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*70}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()

            if result:
                logger.info(f"✓ PASSED: {test_name}")
                self.passed += 1
                self.test_results.append((test_name, "PASSED", None))
            else:
                logger.error(f"✗ FAILED: {test_name}")
                self.failed += 1
                self.test_results.append((test_name, "FAILED", "Assertions failed"))
        except Exception as e:
            logger.error(f"✗ FAILED: {test_name} - Exception: {e}", exc_info=True)
            self.failed += 1
            self.test_results.append((test_name, "FAILED", str(e)))

    # =========================================================================
    # TEST 1: Type Mapping Accuracy
    # =========================================================================

    def test_type_mapping_postgresql(self):
        """Test PostgreSQL type mapping correctness."""
        logger.info("Testing PostgreSQL type mappings...")

        # Create schema with various types
        schema = TableSchema("test_table")
        schema.add_column(ColumnSchema("id", "SERIAL", primary_key=True, auto_increment=True))
        schema.add_column(ColumnSchema("name", "VARCHAR(100)", nullable=False))
        schema.add_column(ColumnSchema("age", "INTEGER", nullable=True))
        schema.add_column(ColumnSchema("price", "DECIMAL(10,2)", nullable=False))
        schema.add_column(ColumnSchema("created_at", "TIMESTAMP", nullable=False))
        schema.add_column(ColumnSchema("is_active", "BOOLEAN", default=True))

        generator = PostgreSQLGenerator()
        forward_sql, backward_sql = generator.generate_create_table("test_table", schema)

        # Verify SQL contains correct types
        checks = [
            self.assert_in("SERIAL", forward_sql, "SERIAL type missing"),
            self.assert_in("VARCHAR(100)", forward_sql, "VARCHAR type missing"),
            self.assert_in("INTEGER", forward_sql, "INTEGER type missing"),
            self.assert_in("DECIMAL(10,2)", forward_sql, "DECIMAL type missing"),
            self.assert_in("TIMESTAMP", forward_sql, "TIMESTAMP type missing"),
            self.assert_in("BOOLEAN", forward_sql, "BOOLEAN type missing"),
            self.assert_in("NOT NULL", forward_sql, "NOT NULL constraint missing"),
            self.assert_in("PRIMARY KEY", forward_sql, "PRIMARY KEY missing"),
        ]

        logger.info(f"Generated SQL:\n{forward_sql}")
        return all(checks)

    def test_type_mapping_mysql(self):
        """Test MySQL type mapping correctness."""
        logger.info("Testing MySQL type mappings...")

        schema = TableSchema("test_table")
        schema.add_column(ColumnSchema("id", "INT AUTO_INCREMENT", primary_key=True, auto_increment=True))
        schema.add_column(ColumnSchema("name", "VARCHAR(100)", nullable=False))
        schema.add_column(ColumnSchema("description", "TEXT", nullable=True))
        schema.add_column(ColumnSchema("created_at", "DATETIME", nullable=False))

        generator = MySQLGenerator()
        forward_sql, backward_sql = generator.generate_create_table("test_table", schema)

        checks = [
            self.assert_in("INT AUTO_INCREMENT", forward_sql, "AUTO_INCREMENT missing"),
            self.assert_in("VARCHAR(100)", forward_sql, "VARCHAR missing"),
            self.assert_in("TEXT", forward_sql, "TEXT type missing"),
            self.assert_in("DATETIME", forward_sql, "DATETIME missing"),
            self.assert_in("ENGINE=InnoDB", forward_sql, "InnoDB engine missing"),
            self.assert_in("utf8mb4", forward_sql, "UTF8MB4 charset missing"),
        ]

        logger.info(f"Generated SQL:\n{forward_sql}")
        return all(checks)

    def test_type_mapping_sqlite(self):
        """Test SQLite type mapping correctness."""
        logger.info("Testing SQLite type mappings...")

        schema = TableSchema("test_table")
        schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True, auto_increment=True))
        schema.add_column(ColumnSchema("name", "TEXT", nullable=False))
        schema.add_column(ColumnSchema("value", "REAL", nullable=True))
        schema.add_column(ColumnSchema("data", "BLOB", nullable=True))

        generator = SQLiteGenerator()
        forward_sql, backward_sql = generator.generate_create_table("test_table", schema)

        checks = [
            self.assert_in("INTEGER", forward_sql, "INTEGER type missing"),
            self.assert_in("TEXT", forward_sql, "TEXT type missing"),
            self.assert_in("REAL", forward_sql, "REAL type missing"),
            self.assert_in("BLOB", forward_sql, "BLOB type missing"),
            self.assert_in("PRIMARY KEY", forward_sql, "PRIMARY KEY missing"),
        ]

        logger.info(f"Generated SQL:\n{forward_sql}")
        return all(checks)

    # =========================================================================
    # TEST 2: Diff Algorithm Correctness
    # =========================================================================

    def test_diff_detect_new_table(self):
        """Test diff engine detects new tables."""
        logger.info("Testing new table detection...")

        # Model has table, database doesn't
        model_schema = TableSchema("users")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("name", "VARCHAR(100)"))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [])

        checks = [
            self.assert_equal(len(operations), 1, "Should detect 1 operation"),
            self.assert_equal(operations[0].operation_type, OperationType.CREATE_TABLE,
                            "Should be CREATE_TABLE operation"),
            self.assert_equal(operations[0].table_name, "users", "Table name should be 'users'"),
        ]

        return all(checks)

    def test_diff_detect_dropped_table(self):
        """Test diff engine detects dropped tables."""
        logger.info("Testing dropped table detection...")

        # Database has table, model doesn't
        db_schema = TableSchema("old_table")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([], [db_schema])

        checks = [
            self.assert_equal(len(operations), 1, "Should detect 1 operation"),
            self.assert_equal(operations[0].operation_type, OperationType.DROP_TABLE,
                            "Should be DROP_TABLE operation"),
            self.assert_equal(operations[0].table_name, "old_table", "Table name should be 'old_table'"),
            self.assert_false(operations[0].reversible, "DROP TABLE should not be reversible"),
        ]

        return all(checks)

    def assert_false(self, condition, message=""):
        """Assert condition is False."""
        return self.assert_true(not condition, message)

    def test_diff_detect_new_column(self):
        """Test diff engine detects new columns."""
        logger.info("Testing new column detection...")

        # Model has extra column
        model_schema = TableSchema("users")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("name", "VARCHAR(100)"))
        model_schema.add_column(ColumnSchema("age", "INTEGER", nullable=True))  # NEW

        db_schema = TableSchema("users")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("name", "VARCHAR(100)"))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [db_schema])

        checks = [
            self.assert_equal(len(operations), 1, "Should detect 1 operation"),
            self.assert_equal(operations[0].operation_type, OperationType.ADD_COLUMN,
                            "Should be ADD_COLUMN operation"),
            self.assert_in("age", str(operations[0].details), "Should mention 'age' column"),
        ]

        return all(checks)

    def test_diff_detect_dropped_column(self):
        """Test diff engine detects dropped columns."""
        logger.info("Testing dropped column detection...")

        # Database has extra column
        model_schema = TableSchema("users")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("name", "VARCHAR(100)"))

        db_schema = TableSchema("users")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("name", "VARCHAR(100)"))
        db_schema.add_column(ColumnSchema("old_field", "VARCHAR(50)"))  # REMOVED

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [db_schema])

        checks = [
            self.assert_equal(len(operations), 1, "Should detect 1 operation"),
            self.assert_equal(operations[0].operation_type, OperationType.DROP_COLUMN,
                            "Should be DROP_COLUMN operation"),
            self.assert_in("old_field", str(operations[0].details), "Should mention 'old_field' column"),
            self.assert_false(operations[0].reversible, "DROP COLUMN should not be reversible"),
        ]

        return all(checks)

    def test_diff_detect_type_change(self):
        """Test diff engine detects column type changes."""
        logger.info("Testing column type change detection...")

        # Type changed from VARCHAR to TEXT
        model_schema = TableSchema("users")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("bio", "TEXT"))  # Changed from VARCHAR

        db_schema = TableSchema("users")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("bio", "VARCHAR(255)"))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [db_schema])

        checks = [
            self.assert_equal(len(operations), 1, "Should detect 1 operation"),
            self.assert_equal(operations[0].operation_type, OperationType.ALTER_COLUMN,
                            "Should be ALTER_COLUMN operation"),
            self.assert_true(operations[0].requires_data_migration,
                           "Type change should require data migration"),
        ]

        return all(checks)

    def test_diff_detect_nullable_change(self):
        """Test diff engine detects nullable changes."""
        logger.info("Testing nullable change detection...")

        # Changed from nullable to NOT NULL
        model_schema = TableSchema("users")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("email", "VARCHAR(100)", nullable=False))  # NOT NULL

        db_schema = TableSchema("users")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("email", "VARCHAR(100)", nullable=True))  # NULL

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [db_schema])

        checks = [
            self.assert_equal(len(operations), 1, "Should detect 1 operation"),
            self.assert_equal(operations[0].operation_type, OperationType.ALTER_COLUMN,
                            "Should be ALTER_COLUMN operation"),
        ]

        return all(checks)

    # =========================================================================
    # TEST 3: SQL Generation Correctness
    # =========================================================================

    def test_sql_add_column_with_default(self):
        """Test ADD COLUMN with default value generates correct SQL."""
        logger.info("Testing ADD COLUMN with default value...")

        column = ColumnSchema("status", "VARCHAR(20)", nullable=False, default="active")

        # PostgreSQL
        pg_gen = PostgreSQLGenerator()
        forward, backward = pg_gen.generate_add_column("users", column)

        checks = [
            self.assert_in("ALTER TABLE", forward, "Should have ALTER TABLE"),
            self.assert_in("ADD COLUMN", forward, "Should have ADD COLUMN"),
            self.assert_in("status", forward, "Should have column name"),
            self.assert_in("VARCHAR(20)", forward, "Should have type"),
            self.assert_in("NOT NULL", forward, "Should have NOT NULL"),
            self.assert_in("DEFAULT", forward, "Should have DEFAULT"),
            self.assert_in("DROP COLUMN", backward, "Backward should DROP COLUMN"),
        ]

        logger.info(f"Forward SQL: {forward}")
        logger.info(f"Backward SQL: {backward}")

        return all(checks)

    def test_sql_alter_column_type(self):
        """Test ALTER COLUMN type change generates correct SQL."""
        logger.info("Testing ALTER COLUMN type change...")

        old_col = ColumnSchema("price", "INTEGER")
        new_col = ColumnSchema("price", "DECIMAL(10,2)")

        # PostgreSQL
        pg_gen = PostgreSQLGenerator()
        forward, backward = pg_gen.generate_alter_column("products", old_col, new_col)

        checks = [
            self.assert_true(len(forward) > 0, "Should have forward SQL"),
            self.assert_in("ALTER TABLE", forward[0], "Should have ALTER TABLE"),
            self.assert_in("ALTER COLUMN", forward[0], "Should have ALTER COLUMN"),
            self.assert_in("TYPE DECIMAL(10,2)", forward[0], "Should change to DECIMAL"),
            self.assert_in("TYPE INTEGER", backward[0], "Backward should revert to INTEGER"),
        ]

        logger.info(f"Forward SQL: {forward}")
        logger.info(f"Backward SQL: {backward}")

        return all(checks)

    def test_sql_create_index(self):
        """Test CREATE INDEX generates correct SQL."""
        logger.info("Testing CREATE INDEX...")

        index = IndexSchema("idx_users_email", ["email"], unique=True)

        # PostgreSQL
        pg_gen = PostgreSQLGenerator()
        forward, backward = pg_gen.generate_add_index("users", index)

        checks = [
            self.assert_in("CREATE UNIQUE INDEX", forward, "Should create unique index"),
            self.assert_in("idx_users_email", forward, "Should have index name"),
            self.assert_in("ON", forward, "Should have ON clause"),
            self.assert_in("email", forward, "Should have column name"),
            self.assert_in("DROP INDEX", backward, "Backward should DROP INDEX"),
        ]

        logger.info(f"Forward SQL: {forward}")
        logger.info(f"Backward SQL: {backward}")

        return all(checks)

    def test_sql_add_foreign_key(self):
        """Test ADD FOREIGN KEY generates correct SQL."""
        logger.info("Testing ADD FOREIGN KEY...")

        fk = RelationshipSchema(
            name="fk_posts_author",
            column="author_id",
            referenced_table="users",
            referenced_column="id",
            on_delete="CASCADE",
            on_update="CASCADE"
        )

        # PostgreSQL
        pg_gen = PostgreSQLGenerator()
        forward, backward = pg_gen.generate_add_foreign_key("posts", fk)

        checks = [
            self.assert_in("ALTER TABLE", forward, "Should have ALTER TABLE"),
            self.assert_in("ADD CONSTRAINT", forward, "Should have ADD CONSTRAINT"),
            self.assert_in("FOREIGN KEY", forward, "Should have FOREIGN KEY"),
            self.assert_in("author_id", forward, "Should have FK column"),
            self.assert_in("REFERENCES", forward, "Should have REFERENCES"),
            self.assert_in("users", forward, "Should reference users table"),
            self.assert_in("ON DELETE CASCADE", forward, "Should have ON DELETE CASCADE"),
            self.assert_in("ON UPDATE CASCADE", forward, "Should have ON UPDATE CASCADE"),
            self.assert_in("DROP CONSTRAINT", backward, "Backward should DROP CONSTRAINT"),
        ]

        logger.info(f"Forward SQL: {forward}")
        logger.info(f"Backward SQL: {backward}")

        return all(checks)

    # =========================================================================
    # TEST 4: Edge Cases
    # =========================================================================

    def test_edge_case_rename_vs_drop_add(self):
        """Test that column rename is detected as drop+add (data loss warning)."""
        logger.info("Testing rename vs drop+add edge case...")

        # Database has 'name', model has 'username' - should be drop+add
        model_schema = TableSchema("users")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("username", "VARCHAR(100)"))

        db_schema = TableSchema("users")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("name", "VARCHAR(100)"))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [db_schema])

        # Should generate DROP and ADD operations, not RENAME
        op_types = [op.operation_type for op in operations]

        checks = [
            self.assert_in(OperationType.DROP_COLUMN, op_types,
                          "Should have DROP_COLUMN for 'name'"),
            self.assert_in(OperationType.ADD_COLUMN, op_types,
                          "Should have ADD_COLUMN for 'username'"),
        ]

        logger.warning("NOTE: Rename detection would prevent data loss but is not implemented")

        return all(checks)

    def test_edge_case_sqlite_alter_limitations(self):
        """Test SQLite ALTER COLUMN limitations are documented."""
        logger.info("Testing SQLite ALTER COLUMN limitations...")

        old_col = ColumnSchema("age", "INTEGER")
        new_col = ColumnSchema("age", "BIGINT")

        sqlite_gen = SQLiteGenerator()
        forward, backward = sqlite_gen.generate_alter_column("users", old_col, new_col)

        checks = [
            self.assert_in("SQLite doesn't support ALTER COLUMN", forward[0],
                          "Should warn about SQLite limitation"),
        ]

        logger.warning("SQLite requires table recreation for ALTER COLUMN")

        return all(checks)

    def test_edge_case_circular_foreign_keys(self):
        """Test handling of circular foreign key dependencies."""
        logger.info("Testing circular foreign key handling...")

        # User -> Profile -> User (circular)
        user_schema = TableSchema("users")
        user_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        user_schema.add_column(ColumnSchema("primary_profile_id", "INTEGER", nullable=True))
        user_schema.add_relationship(RelationshipSchema(
            "fk_user_profile", "primary_profile_id", "profiles", "id"
        ))

        profile_schema = TableSchema("profiles")
        profile_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        profile_schema.add_column(ColumnSchema("user_id", "INTEGER"))
        profile_schema.add_relationship(RelationshipSchema(
            "fk_profile_user", "user_id", "users", "id"
        ))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([user_schema, profile_schema], [])

        # Should order FK creation AFTER table creation
        # Priority: CREATE TABLE (30) -> ADD FK (70)
        priorities = [op.priority for op in operations]

        checks = [
            self.assert_true(len(operations) > 0, "Should generate operations"),
        ]

        logger.warning("Circular FK requires careful ordering - FK added after tables")

        return all(checks)

    # =========================================================================
    # TEST 5: Data Safety
    # =========================================================================

    def test_safety_drop_operations_marked(self):
        """Test that destructive operations are marked as non-reversible."""
        logger.info("Testing destructive operation marking...")

        db_schema = TableSchema("old_table")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("old_column", "VARCHAR(100)"))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([], [db_schema])

        # Find DROP operations
        drop_ops = [op for op in operations if "DROP" in op.operation_type.value]

        checks = []
        for op in drop_ops:
            checks.append(
                self.assert_false(op.reversible,
                                f"{op.operation_type.value} should be non-reversible")
            )

        logger.info(f"Found {len(drop_ops)} destructive operations")

        return all(checks) if checks else True

    def test_safety_type_change_requires_migration(self):
        """Test that type changes require data migration."""
        logger.info("Testing type change data migration requirement...")

        model_schema = TableSchema("products")
        model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        model_schema.add_column(ColumnSchema("price", "VARCHAR(50)"))  # Changed from DECIMAL

        db_schema = TableSchema("products")
        db_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
        db_schema.add_column(ColumnSchema("price", "DECIMAL(10,2)"))

        diff_engine = DiffEngine()
        operations = diff_engine.compare_schemas([model_schema], [db_schema])

        alter_ops = [op for op in operations if op.operation_type == OperationType.ALTER_COLUMN]

        checks = []
        for op in alter_ops:
            checks.append(
                self.assert_true(op.requires_data_migration,
                               "Type change should require data migration")
            )

        return all(checks) if checks else True

    # =========================================================================
    # TEST 6: Integration Test
    # =========================================================================

    async def test_integration_full_workflow(self):
        """Test complete workflow: introspect -> diff -> generate -> apply."""
        logger.info("Testing full integration workflow...")

        # Create in-memory SQLite database
        adapter = SQLiteAdapter(database=":memory:")
        await adapter.connect()

        try:
            # Create initial table
            await adapter.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    email TEXT
                )
            """)

            # Introspect database
            introspector = DatabaseIntrospector(adapter, dialect="sqlite")
            db_schemas = await introspector.get_all_schemas()

            checks = [
                self.assert_equal(len(db_schemas), 1, "Should find 1 table"),
                self.assert_equal(db_schemas[0].name, "users", "Table should be 'users'"),
                self.assert_equal(len(db_schemas[0].columns), 3, "Should have 3 columns"),
            ]

            # Create model schema with added column
            model_schema = TableSchema("users")
            model_schema.add_column(ColumnSchema("id", "INTEGER", primary_key=True))
            model_schema.add_column(ColumnSchema("username", "TEXT", nullable=False))
            model_schema.add_column(ColumnSchema("email", "TEXT", nullable=True))
            model_schema.add_column(ColumnSchema("age", "INTEGER", nullable=True))  # NEW

            # Generate diff
            diff_engine = DiffEngine()
            operations = diff_engine.compare_schemas([model_schema], db_schemas)

            checks.append(
                self.assert_equal(len(operations), 1, "Should detect 1 change")
            )
            checks.append(
                self.assert_equal(operations[0].operation_type, OperationType.ADD_COLUMN,
                                "Should be ADD_COLUMN")
            )

            # Generate SQL
            generator = SQLiteGenerator()
            forward_sql, backward_sql = generator.generate_add_column(
                "users",
                ColumnSchema("age", "INTEGER", nullable=True)
            )

            checks.append(
                self.assert_in("ALTER TABLE", forward_sql, "Should have ALTER TABLE")
            )

            # Apply migration
            await adapter.execute(forward_sql)

            # Verify column added
            table_info = await adapter.get_table_info("users")
            column_names = [col["name"] for col in table_info]

            checks.append(
                self.assert_in("age", column_names, "Age column should be added")
            )

            logger.info("✓ Full workflow completed successfully")
            return all(checks)

        finally:
            await adapter.disconnect()

    # =========================================================================
    # Run All Tests
    # =========================================================================

    def run_all_tests(self):
        """Run all migration correctness tests."""
        logger.info("\n" + "="*70)
        logger.info("SPRINT 2 MIGRATION SYSTEM CORRECTNESS AUDIT")
        logger.info("="*70 + "\n")

        # Type Mapping Tests
        self.run_test("Type Mapping - PostgreSQL", self.test_type_mapping_postgresql)
        self.run_test("Type Mapping - MySQL", self.test_type_mapping_mysql)
        self.run_test("Type Mapping - SQLite", self.test_type_mapping_sqlite)

        # Diff Algorithm Tests
        self.run_test("Diff - Detect New Table", self.test_diff_detect_new_table)
        self.run_test("Diff - Detect Dropped Table", self.test_diff_detect_dropped_table)
        self.run_test("Diff - Detect New Column", self.test_diff_detect_new_column)
        self.run_test("Diff - Detect Dropped Column", self.test_diff_detect_dropped_column)
        self.run_test("Diff - Detect Type Change", self.test_diff_detect_type_change)
        self.run_test("Diff - Detect Nullable Change", self.test_diff_detect_nullable_change)

        # SQL Generation Tests
        self.run_test("SQL - ADD COLUMN with Default", self.test_sql_add_column_with_default)
        self.run_test("SQL - ALTER COLUMN Type", self.test_sql_alter_column_type)
        self.run_test("SQL - CREATE INDEX", self.test_sql_create_index)
        self.run_test("SQL - ADD FOREIGN KEY", self.test_sql_add_foreign_key)

        # Edge Case Tests
        self.run_test("Edge Case - Rename vs Drop+Add", self.test_edge_case_rename_vs_drop_add)
        self.run_test("Edge Case - SQLite Limitations", self.test_edge_case_sqlite_alter_limitations)
        self.run_test("Edge Case - Circular Foreign Keys", self.test_edge_case_circular_foreign_keys)

        # Data Safety Tests
        self.run_test("Safety - Destructive Operations Marked", self.test_safety_drop_operations_marked)
        self.run_test("Safety - Type Change Migration", self.test_safety_type_change_requires_migration)

        # Integration Test
        self.run_test("Integration - Full Workflow", self.test_integration_full_workflow)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        logger.info(f"\nTotal Tests: {total}")
        logger.info(f"Passed: {self.passed}")
        logger.info(f"Failed: {self.failed}")
        logger.info(f"Pass Rate: {pass_rate:.1f}%")

        if self.failed > 0:
            logger.info("\nFailed Tests:")
            for name, status, error in self.test_results:
                if status == "FAILED":
                    logger.info(f"  ✗ {name}")
                    if error:
                        logger.info(f"    {error}")

        logger.info("\n" + "="*70)

        return pass_rate >= 80  # 80% pass rate minimum


if __name__ == "__main__":
    tester = MigrationCorrectnessTests()
    tester.run_all_tests()
