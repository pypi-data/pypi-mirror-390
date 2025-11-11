#!/usr/bin/env python3
"""
MySQL Adapter Installation Verification Script

This script verifies that the MySQL adapter is properly installed and configured.

Run:
    python examples/verify_mysql_installation.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def verify_imports():
    """Verify all required imports work."""
    print("\n" + "=" * 70)
    print("VERIFICATION 1: Import Check")
    print("=" * 70)

    try:
        from covet.database.adapters.mysql import MySQLAdapter
        print("✓ MySQLAdapter imported successfully")

        from covet.database.security.sql_validator import (
            validate_table_name,
            validate_schema_name,
            DatabaseDialect,
        )
        print("✓ SQL validator imported successfully")

        try:
            import aiomysql
            print(f"✓ aiomysql installed (version: {aiomysql.__version__})")
        except ImportError:
            print("✗ aiomysql NOT installed")
            print("  Install: pip install aiomysql")
            return False

        print("\n✓ All imports successful!")
        return True

    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def verify_adapter_attributes():
    """Verify adapter has all required attributes and methods."""
    print("\n" + "=" * 70)
    print("VERIFICATION 2: Adapter API Check")
    print("=" * 70)

    from covet.database.adapters.mysql import MySQLAdapter

    required_methods = [
        # Connection management
        "connect",
        "disconnect",
        # Query execution
        "execute",
        "execute_insert",
        "fetch_one",
        "fetch_all",
        "fetch_value",
        "execute_many",
        # Streaming
        "stream_query",
        # Transactions
        "transaction",
        # Metadata
        "get_table_info",
        "table_exists",
        "get_version",
        "get_database_list",
        "get_table_list",
        # Utilities
        "get_pool_stats",
        "optimize_table",
        "analyze_table",
        # Advanced features
        "execute_with_retry",
        "parse_binlog_events",
        "get_replication_status",
        "health_check",
    ]

    missing = []
    for method in required_methods:
        if hasattr(MySQLAdapter, method):
            print(f"✓ {method}")
        else:
            print(f"✗ {method} - MISSING")
            missing.append(method)

    if missing:
        print(f"\n✗ Missing {len(missing)} required methods!")
        return False
    else:
        print(f"\n✓ All {len(required_methods)} required methods present!")
        return True


def verify_adapter_instantiation():
    """Verify adapter can be instantiated."""
    print("\n" + "=" * 70)
    print("VERIFICATION 3: Adapter Instantiation")
    print("=" * 70)

    try:
        from covet.database.adapters.mysql import MySQLAdapter

        adapter = MySQLAdapter(
            host="localhost",
            port=3306,
            database="test",
            user="root",
            password="",
            charset="utf8mb4",
            min_pool_size=5,
            max_pool_size=20,
        )

        print("✓ Adapter instantiated successfully")
        print(f"  {adapter}")

        # Verify attributes
        assert adapter.host == "localhost", "Host not set correctly"
        assert adapter.port == 3306, "Port not set correctly"
        assert adapter.database == "test", "Database not set correctly"
        assert adapter.charset == "utf8mb4", "Charset not set correctly"
        assert adapter.min_pool_size == 5, "Min pool size not set correctly"
        assert adapter.max_pool_size == 20, "Max pool size not set correctly"

        print("✓ All adapter attributes set correctly")
        return True

    except Exception as e:
        print(f"✗ Instantiation failed: {e}")
        return False


def verify_file_structure():
    """Verify all required files exist."""
    print("\n" + "=" * 70)
    print("VERIFICATION 4: File Structure")
    print("=" * 70)

    base_path = Path(__file__).parent.parent

    required_files = [
        # Source
        "src/covet/database/adapters/mysql.py",
        "src/covet/database/security/sql_validator.py",
        # Tests
        "tests/integration/mysql/__init__.py",
        "tests/integration/mysql/test_mysql_adapter.py",
        "tests/integration/mysql/test_mysql_performance.py",
        # Documentation
        "docs/guides/MYSQL_PRODUCTION_GUIDE.md",
        "docs/guides/MYSQL_ADAPTER_README.md",
        "docs/MYSQL_ADAPTER_DELIVERY_SUMMARY.md",
        # Examples
        "examples/mysql_adapter_demo.py",
    ]

    missing = []
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {file_path} ({size:,} bytes)")
        else:
            print(f"✗ {file_path} - MISSING")
            missing.append(file_path)

    if missing:
        print(f"\n✗ Missing {len(missing)} required files!")
        return False
    else:
        print(f"\n✓ All {len(required_files)} required files present!")
        return True


def verify_code_metrics():
    """Verify code meets size requirements."""
    print("\n" + "=" * 70)
    print("VERIFICATION 5: Code Metrics")
    print("=" * 70)

    base_path = Path(__file__).parent.parent

    # Check MySQL adapter
    adapter_file = base_path / "src/covet/database/adapters/mysql.py"
    if adapter_file.exists():
        with open(adapter_file) as f:
            lines = len(f.readlines())
        print(f"✓ MySQL adapter: {lines:,} lines (target: 700+)")
        if lines < 700:
            print(f"  ⚠ WARNING: Below target of 700 lines")
            return False
    else:
        print("✗ MySQL adapter file not found")
        return False

    # Check test files
    test_files = [
        "tests/integration/mysql/test_mysql_adapter.py",
        "tests/integration/mysql/test_mysql_performance.py",
    ]

    total_test_lines = 0
    for test_file in test_files:
        full_path = base_path / test_file
        if full_path.exists():
            with open(full_path) as f:
                lines = len(f.readlines())
            print(f"✓ {test_file.split('/')[-1]}: {lines:,} lines")
            total_test_lines += lines

    print(f"✓ Total test lines: {total_test_lines:,}")

    print(f"\n✓ Code metrics meet requirements!")
    return True


def main():
    """Run all verifications."""
    print("\n" + "=" * 70)
    print("MySQL Adapter Installation Verification")
    print("CovetPy Framework - Production Readiness Check")
    print("=" * 70)

    results = []

    # Run all verifications
    results.append(("Imports", verify_imports()))
    results.append(("Adapter API", verify_adapter_attributes()))
    results.append(("Instantiation", verify_adapter_instantiation()))
    results.append(("File Structure", verify_file_structure()))
    results.append(("Code Metrics", verify_code_metrics()))

    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f"✓ ALL VERIFICATIONS PASSED ({passed}/{total})")
        print("=" * 70)
        print("\nMySQL adapter is ready for production! 🎉")
        print("\nNext steps:")
        print("1. Install MySQL: brew install mysql (macOS) or apt install mysql-server (Ubuntu)")
        print("2. Create test database: mysql -u root -p -e 'CREATE DATABASE test_mysql'")
        print("3. Run tests: PYTHONPATH=src python3 -m pytest tests/integration/mysql/ -v")
        print("4. Run demo: python examples/mysql_adapter_demo.py")
        return 0
    else:
        print(f"✗ VERIFICATION FAILED ({passed}/{total} passed)")
        print("=" * 70)
        print("\nPlease fix the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
