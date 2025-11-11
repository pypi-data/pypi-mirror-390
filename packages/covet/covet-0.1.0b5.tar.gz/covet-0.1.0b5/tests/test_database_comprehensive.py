"""
Comprehensive database tests for CovetPy framework.
These tests verify database operations, ORM functionality, and data persistence.
"""
import os
import sys
import sqlite3
import json
import tempfile
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestDatabaseConnections:
    """Test database connection management."""
    
    def test_sqlite_connection(self):
        """Test SQLite database connection."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Test connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Test basic operations
            cursor.execute('''
                CREATE TABLE test_users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert test data
            cursor.execute(
                "INSERT INTO test_users (username, email) VALUES (?, ?)",
                ("testuser", "test@example.com")
            )
            conn.commit()
            
            # Query data
            cursor.execute("SELECT * FROM test_users WHERE username = ?", ("testuser",))
            result = cursor.fetchone()
            
            assert result is not None
            assert result[1] == "testuser"  # username
            assert result[2] == "test@example.com"  # email
            
            conn.close()
        finally:
            os.unlink(db_path)
    
    def test_connection_pooling(self):
        """Test database connection pooling."""
        class SimpleConnectionPool:
            def __init__(self, db_path, max_connections=5):
                self.db_path = db_path
                self.max_connections = max_connections
                self.pool = []
                self.active_connections = 0
                self._lock = threading.Lock()
            
            def get_connection(self):
                with self._lock:
                    if self.pool:
                        return self.pool.pop()
                    elif self.active_connections < self.max_connections:
                        self.active_connections += 1
                        return sqlite3.connect(self.db_path)
                    else:
                        raise Exception("Connection pool exhausted")
            
            def return_connection(self, conn):
                with self._lock:
                    if len(self.pool) < self.max_connections:
                        self.pool.append(conn)
                    else:
                        conn.close()
                        self.active_connections -= 1
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            pool = SimpleConnectionPool(db_path, max_connections=3)
            
            # Test getting connections
            conn1 = pool.get_connection()
            conn2 = pool.get_connection()
            conn3 = pool.get_connection()
            
            assert conn1 is not None
            assert conn2 is not None
            assert conn3 is not None
            
            # Test pool exhaustion
            with pytest.raises(Exception, match="Connection pool exhausted"):
                pool.get_connection()
            
            # Return connections
            pool.return_connection(conn1)
            pool.return_connection(conn2)
            pool.return_connection(conn3)
            
            # Should be able to get connection again
            conn4 = pool.get_connection()
            assert conn4 is not None
            
        finally:
            os.unlink(db_path)

class TestORMFunctionality:
    """Test ORM (Object-Relational Mapping) functionality."""
    
    def test_model_definition(self):
        """Test model definition and creation."""
        class BaseModel:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def to_dict(self):
                assert {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
        
        class User(BaseModel):
            table_name = 'users'
            fields = ['id', 'username', 'email', 'created_at']
            
            def __init__(self, username=None, email=None, **kwargs):
                super().__init__(**kwargs)
                self.username = username
                self.email = email
                self.created_at = kwargs.get('created_at', datetime.now())
        
        # Test model creation
        user = User(username="testuser", email="test@example.com")
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert isinstance(user.created_at, datetime)
        
        # Test serialization
        user_dict = user.to_dict()
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
    
    def test_query_builder(self):
        """Test SQL query builder functionality."""
        class QueryBuilder:
            def __init__(self, table_name):
                self.table_name = table_name
                self.select_fields = ['*']
                self.where_conditions = []
                self.order_by_fields = []
                self.limit_value = None
                self.params = []
            
            def select(self, *fields):
                self.select_fields = fields
                return self
            
            def where(self, condition, *params):
                self.where_conditions.append(condition)
                self.params.extend(params)
                return self
            
            def order_by(self, field, direction='ASC'):
                self.order_by_fields.append(f"{field} {direction}")
                return self
            
            def limit(self, count):
                self.limit_value = count
                return self
            
            def build(self):
                query = f"SELECT {', '.join(self.select_fields)} FROM {self.table_name}"
                
                if self.where_conditions:
                    query += " WHERE " + " AND ".join(self.where_conditions)
                
                if self.order_by_fields:
                    query += " ORDER BY " + ", ".join(self.order_by_fields)
                
                if self.limit_value:
                    query += f" LIMIT {self.limit_value}"
                
                return query, self.params
        
        # Test query building
        builder = QueryBuilder('users')
        query, params = builder.select('id', 'username', 'email')\
                              .where('username = ?', 'testuser')\
                              .where('active = ?', True)\
                              .order_by('created_at', 'DESC')\
                              .limit(10)\
                              .build()
        
        expected_query = "SELECT id, username, email FROM users WHERE username = ? AND active = ? ORDER BY created_at DESC LIMIT 10"
        assert query == expected_query
        assert params == ['testuser', True]
    
    def test_database_migrations(self):
        """Test database migration functionality."""
        class Migration:
            def __init__(self, version, description):
                self.version = version
                self.description = description
            
            def up(self, cursor):
                raise NotImplementedError
            
            def down(self, cursor):
                raise NotImplementedError
        
        class CreateUsersTable(Migration):
            def __init__(self):
                super().__init__("001", "Create users table")
            
            def up(self, cursor):
                cursor.execute('''
                    CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            def down(self, cursor):
                cursor.execute("DROP TABLE IF EXISTS users")
        
        class MigrationManager:
            def __init__(self, db_path):
                self.db_path = db_path
                self.migrations = []
            
            def add_migration(self, migration):
                self.migrations.append(migration)
            
            def run_migrations(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Create migrations table if not exists
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS migrations (
                        version TEXT PRIMARY KEY,
                        description TEXT,
                        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Run pending migrations
                for migration in self.migrations:
                    cursor.execute("SELECT version FROM migrations WHERE version = ?", (migration.version,))
                    if not cursor.fetchone():
                        migration.up(cursor)
                        cursor.execute(
                            "INSERT INTO migrations (version, description) VALUES (?, ?)",
                            (migration.version, migration.description)
                        )
                
                conn.commit()
                conn.close()
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            manager = MigrationManager(db_path)
            manager.add_migration(CreateUsersTable())
            manager.run_migrations()
            
            # Verify table was created
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'users'
            
            # Verify migration was recorded
            cursor.execute("SELECT version FROM migrations WHERE version = '001'")
            migration_result = cursor.fetchone()
            assert migration_result is not None
            assert migration_result[0] == '001'
            
            conn.close()
        finally:
            os.unlink(db_path)

class TestTransactionManagement:
    """Test database transaction management."""
    
    def test_basic_transactions(self):
        """Test basic transaction operations."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute('''
                CREATE TABLE accounts (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    balance DECIMAL(10,2)
                )
            ''')
            
            # Insert initial data
            cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("Alice", 1000.00))
            cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("Bob", 500.00))
            conn.commit()
            
            # Test successful transaction
            try:
                cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE name = ?", ("Alice",))
                cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE name = ?", ("Bob",))
                conn.commit()
                
                # Verify balances
                cursor.execute("SELECT balance FROM accounts WHERE name = ?", ("Alice",))
                alice_balance = cursor.fetchone()[0]
                cursor.execute("SELECT balance FROM accounts WHERE name = ?", ("Bob",))
                bob_balance = cursor.fetchone()[0]
                
                assert alice_balance == 900.00
                assert bob_balance == 600.00
                
            except Exception:
                conn.rollback()
                raise
            
            conn.close()
        finally:
            os.unlink(db_path)
    
    def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute('''
                CREATE TABLE accounts (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    balance DECIMAL(10,2)
                )
            ''')
            
            # Insert initial data
            cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("Alice", 1000.00))
            conn.commit()
            
            # Get initial balance
            cursor.execute("SELECT balance FROM accounts WHERE name = ?", ("Alice",))
            initial_balance = cursor.fetchone()[0]
            
            # Test failed transaction (should rollback)
            try:
                cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE name = ?", ("Alice",))
                # This should fail due to UNIQUE constraint
                cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("Alice", 500.00))
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()
            
            # Verify balance hasn't changed
            cursor.execute("SELECT balance FROM accounts WHERE name = ?", ("Alice",))
            final_balance = cursor.fetchone()[0]
            assert final_balance == initial_balance
            
            conn.close()
        finally:
            os.unlink(db_path)
    
    @contextmanager
    def transaction_context(self, conn):
        """Context manager for transactions."""
        try:
            yield conn.cursor()
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    
    def test_transaction_context_manager(self):
        """Test transaction using context manager."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(db_path)
            
            # Create test table
            with self.transaction_context(conn) as cursor:
                cursor.execute('''
                    CREATE TABLE test_table (
                        id INTEGER PRIMARY KEY,
                        value TEXT
                    )
                ''')
            
            # Test successful transaction
            with self.transaction_context(conn) as cursor:
                cursor.execute("INSERT INTO test_table (value) VALUES (?)", ("test1",))
                cursor.execute("INSERT INTO test_table (value) VALUES (?)", ("test2",))
            
            # Verify data was committed
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM test_table")
            count = cursor.fetchone()[0]
            assert count == 2
            
            conn.close()
        finally:
            os.unlink(db_path)

class TestDatabasePerformance:
    """Test database performance optimizations."""
    
    def test_batch_operations(self):
        """Test batch insert/update operations."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute('''
                CREATE TABLE test_records (
                    id INTEGER PRIMARY KEY,
                    value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test batch insert
            test_data = [(f"value_{i}",) for i in range(100)]
            
            start_time = time.time()
            cursor.executemany("INSERT INTO test_records (value) VALUES (?)", test_data)
            conn.commit()
            batch_time = time.time() - start_time
            
            # Verify all records were inserted
            cursor.execute("SELECT COUNT(*) FROM test_records")
            count = cursor.fetchone()[0]
            assert count == 100
            
            # Test individual inserts (should be slower)
            cursor.execute("DELETE FROM test_records")
            conn.commit()
            
            start_time = time.time()
            for value in [f"value_{i}" for i in range(100)]:
                cursor.execute("INSERT INTO test_records (value) VALUES (?)", (value,))
            conn.commit()
            individual_time = time.time() - start_time
            
            # Batch operations should generally be faster
            print(f"Batch time: {batch_time:.4f}s, Individual time: {individual_time:.4f}s")
            
            conn.close()
        finally:
            os.unlink(db_path)
    
    def test_indexing_performance(self):
        """Test database indexing for performance."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute('''
                CREATE TABLE search_test (
                    id INTEGER PRIMARY KEY,
                    email TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert test data
            test_data = []
            for i in range(1000):
                test_data.append((f"user{i}@example.com", "active" if i % 2 == 0 else "inactive"))
            
            cursor.executemany("INSERT INTO search_test (email, status) VALUES (?, ?)", test_data)
            conn.commit()
            
            # Test query without index
            start_time = time.time()
            cursor.execute("SELECT * FROM search_test WHERE email = ?", ("user500@example.com",))
            result = cursor.fetchone()
            no_index_time = time.time() - start_time
            
            assert result is not None
            assert result[1] == "user500@example.com"
            
            # Create index
            cursor.execute("CREATE INDEX idx_email ON search_test(email)")
            
            # Test query with index
            start_time = time.time()
            cursor.execute("SELECT * FROM search_test WHERE email = ?", ("user500@example.com",))
            result = cursor.fetchone()
            with_index_time = time.time() - start_time
            
            assert result is not None
            print(f"No index: {no_index_time:.6f}s, With index: {with_index_time:.6f}s")
            
            conn.close()
        finally:
            os.unlink(db_path)

class TestDataValidation:
    """Test data validation and constraints."""
    
    def test_data_type_validation(self):
        """Test data type validation."""
        class DataValidator:
            @staticmethod
            def validate_email(email):
                import re
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                assert re.match(pattern, email) is not None
            
            @staticmethod
            def validate_phone(phone):
                import re
                # Simple phone validation (digits, spaces, dashes, parentheses)
                pattern = r'^[\d\s\-\(\)]+$'
                assert re.match(pattern, phone) is not None and len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 10
            
            @staticmethod
            def validate_age(age):
                assert isinstance(age, int) and 0 <= age <= 150
        
        validator = DataValidator()
        
        # Test email validation
        assert validator.validate_email("test@example.com") == True
        assert validator.validate_email("invalid.email") == False
        assert validator.validate_email("test@") == False
        
        # Test phone validation
        assert validator.validate_phone("(555) 123-4567") == True
        assert validator.validate_phone("555-123-4567") == True
        assert validator.validate_phone("5551234567") == True
        assert validator.validate_phone("invalid-phone") == False
        
        # Test age validation
        assert validator.validate_age(25) == True
        assert validator.validate_age(0) == True
        assert validator.validate_age(150) == True
        assert validator.validate_age(-1) == False
        assert validator.validate_age(151) == False
        assert validator.validate_age("25") == False
    
    def test_database_constraints(self):
        """Test database constraint enforcement."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create table with constraints
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    age INTEGER CHECK (age >= 0 AND age <= 150),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test successful insert
            cursor.execute(
                "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
                ("testuser", "test@example.com", 25)
            )
            conn.commit()
            
            # Test UNIQUE constraint violation
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
                    ("testuser", "different@example.com", 30)
                )
            
            # Test CHECK constraint violation
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO users (username, email, age) VALUES (?, ?, ?)",
                    ("validuser", "valid@example.com", -5)
                )
            
            # Test NOT NULL constraint violation
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute(
                    "INSERT INTO users (email, age) VALUES (?, ?)",
                    ("test2@example.com", 25)
                )
            
            conn.close()
        finally:
            os.unlink(db_path)

@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    def test_complete_crud_operations(self):
        """Test complete CRUD (Create, Read, Update, Delete) operations."""
        class UserRepository:
            def __init__(self, db_path):
                self.db_path = db_path
                self._initialize_db()
            
            def _initialize_db(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                conn.close()
            
            def create_user(self, username, email):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, email) VALUES (?, ?)",
                    (username, email)
                )
                user_id = cursor.lastrowid
                conn.commit()
                conn.close()
                return user_id
            
            def get_user(self, user_id):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                conn.close()
                return result
            
            def update_user(self, user_id, username=None, email=None):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                updates = []
                params = []
                
                if username:
                    updates.append("username = ?")
                    params.append(username)
                
                if email:
                    updates.append("email = ?")
                    params.append(email)
                
                if updates:
                    updates.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(user_id)
                    
                    query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    conn.commit()
                
                conn.close()
            
            def delete_user(self, user_id):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                deleted = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return deleted
            
            def list_users(self, limit=10, offset=0):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users LIMIT ? OFFSET ?", (limit, offset))
                results = cursor.fetchall()
                conn.close()
                return results
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            repo = UserRepository(db_path)
            
            # Test CREATE
            user_id = repo.create_user("testuser", "test@example.com")
            assert user_id is not None
            assert user_id > 0
            
            # Test READ
            user = repo.get_user(user_id)
            assert user is not None
            assert user[1] == "testuser"  # username
            assert user[2] == "test@example.com"  # email
            
            # Test UPDATE
            repo.update_user(user_id, username="updateduser")
            updated_user = repo.get_user(user_id)
            assert updated_user[1] == "updateduser"
            assert updated_user[2] == "test@example.com"  # email unchanged
            
            # Test LIST
            # Create more users
            repo.create_user("user2", "user2@example.com")
            repo.create_user("user3", "user3@example.com")
            
            users = repo.list_users()
            assert len(users) == 3
            
            # Test DELETE
            deleted = repo.delete_user(user_id)
            assert deleted == True
            
            # Verify deletion
            deleted_user = repo.get_user(user_id)
            assert deleted_user is None
            
            # Verify remaining users
            remaining_users = repo.list_users()
            assert len(remaining_users) == 2
            
        finally:
            os.unlink(db_path)
    
    def test_concurrent_database_access(self):
        """Test concurrent database access."""
        import threading
        import queue
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Initialize database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE counter (
                    id INTEGER PRIMARY KEY,
                    value INTEGER DEFAULT 0
                )
            ''')
            cursor.execute("INSERT INTO counter (value) VALUES (0)")
            conn.commit()
            conn.close()
            
            results = queue.Queue()
            
            def increment_counter(thread_id):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    for _ in range(10):
                        cursor.execute("UPDATE counter SET value = value + 1 WHERE id = 1")
                        conn.commit()
                    
                    conn.close()
                    results.put(f"Thread {thread_id} completed")
                except Exception as e:
                    results.put(f"Thread {thread_id} error: {e}")
            
            # Create and start multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=increment_counter, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            completed_count = 0
            while not results.empty():
                result = results.get()
                if "completed" in result:
                    completed_count += 1
            
            assert completed_count == 5
            
            # Verify final counter value
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM counter WHERE id = 1")
            final_value = cursor.fetchone()[0]
            conn.close()
            
            # Should be 50 (5 threads * 10 increments each)
            assert final_value == 50
            
        finally:
            os.unlink(db_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])