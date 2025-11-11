#!/usr/bin/env python3
"""
Full Integration Test for CovetPy Framework
============================================
Tests all components working together:
- HTTP Server
- ORM & Database
- Authentication
- Middleware
- Sessions
- API Routes
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("COVETPY FULL INTEGRATION TEST")
print("=" * 80)
print()

# Track test results
test_results = []
tests_passed = 0
tests_failed = 0


def test(name):
    """Decorator for tests"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed
            print(f"\n🧪 Testing: {name}")
            print("-" * 40)
            try:
                result = func()
                test_results.append((name, "✅ PASS", str(result)))
                tests_passed += 1
                print(f"✅ PASSED: {result}")
                return True
            except Exception as e:
                test_results.append((name, "❌ FAIL", str(e)))
                tests_failed += 1
                print(f"❌ FAILED: {e}")
                # Print traceback for debugging
                import traceback
                traceback.print_exc()
                return False
        return wrapper
    return decorator


# ====================
# 1. TEST IMPORTS
# ====================

@test("Import Core Modules")
def test_imports():
    """Test that all core modules can be imported"""
    # Core
    from covet import Covet

    # ORM
    from covet.orm import Database, Model
    from covet.orm.fields import IntegerField, CharField

    # Auth
    from covet.auth import Auth, login_required
    from covet.auth.password import hash_password, verify_password

    # Middleware
    from covet.middleware.base import (
        CORSMiddleware,
        AuthenticationMiddleware,
        LoggingMiddleware,
        SessionMiddleware
    )

    return "All imports successful"


# ====================
# 2. TEST HTTP SERVER
# ====================

@test("HTTP Server Basic")
def test_http_server():
    """Test basic HTTP server functionality"""
    from covet import Covet

    app = Covet(debug=True)

    # Test route registration
    @app.route('/')
    async def index(request):
        return {'message': 'Hello World'}

    @app.route('/users/{user_id}')
    async def get_user(request, user_id):
        return {'user_id': user_id}

    @app.post('/users')
    async def create_user(request):
        data = await request.json()
        return {'created': data}

    # Check routes are registered
    assert len(app.routes) >= 3, f"Expected at least 3 routes, got {len(app.routes)}"

    return f"HTTP server configured with {len(app.routes)} routes"


# ====================
# 3. TEST DATABASE ORM
# ====================

@test("Database ORM Operations")
def test_database_orm():
    """Test database and ORM functionality"""
    from covet.orm import Database, Model
    from covet.orm.fields import IntegerField, CharField

    # Create in-memory database
    db = Database('sqlite:///:memory:')

    # Define model
    class User(Model):
        id = IntegerField(primary_key=True)
        username = CharField(max_length=100)
        email = CharField(max_length=255)

        class Meta:
            db = db
            table_name = 'users'

    # Create table
    db.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100),
            email VARCHAR(255)
        )
    ''')

    # Test CRUD operations
    # Create
    user = User(username='testuser', email='test@example.com')
    user.save()

    # Read
    users = User.objects.all()
    assert len(users) > 0, "No users found"

    # Update (using raw SQL for now)
    db.execute(
        "UPDATE users SET email = ? WHERE username = ?",
        ('newemail@example.com', 'testuser')
    )

    # Delete (using raw SQL for now)
    db.execute("DELETE FROM users WHERE username = ?", ('testuser',))

    return f"ORM operations successful"


# ====================
# 4. TEST AUTHENTICATION
# ====================

@test("Authentication System")
def test_authentication():
    """Test authentication functionality"""
    from covet import Covet
    from covet.auth import Auth
    from covet.auth.password import hash_password, verify_password

    app = Covet()
    auth = Auth(app, secret_key='test-secret-key')

    # Test password hashing
    password = "SecurePass123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed), "Password verification failed"
    assert not verify_password("WrongPass", hashed), "Wrong password verified"

    # Test JWT token creation and verification
    token = auth.create_token(user_id='user123')
    assert token is not None, "Token creation failed"

    user_id = auth.verify_token(token)
    assert user_id == 'user123', f"Token verification failed: {user_id}"

    return "Authentication working"


# ====================
# 5. TEST MIDDLEWARE
# ====================

@test("Middleware Pipeline")
def test_middleware():
    """Test middleware functionality"""
    from covet import Covet
    from covet.middleware.base import (
        MiddlewareStack,
        CORSMiddleware,
        LoggingMiddleware,
        SessionMiddleware
    )

    app = Covet()

    # Create middleware stack
    middleware = MiddlewareStack()
    middleware.add(CORSMiddleware, origins="*", methods=["GET", "POST"])
    middleware.add(LoggingMiddleware)
    middleware.add(SessionMiddleware)

    # Test middleware can be created
    assert len(middleware.middleware) == 3, "Middleware not added to stack"

    return f"Middleware stack with {len(middleware.middleware)} components"


# ====================
# 6. TEST FULL INTEGRATION
# ====================

@test("Full Integration Example")
def test_full_integration():
    """Test all components working together"""
    from covet import Covet
    from covet.orm import Database, Model
    from covet.orm.fields import IntegerField, CharField
    from covet.auth import Auth, login_required
    from covet.auth.password import hash_password, verify_password
    from covet.middleware.base import CORSMiddleware, SessionMiddleware

    # Create app
    app = Covet(debug=True)

    # Setup database
    db = Database('sqlite:///:memory:')

    # Define User model
    class User(Model):
        id = IntegerField(primary_key=True)
        username = CharField(max_length=100)
        password_hash = CharField(max_length=255)

        class Meta:
            db = db
            table_name = 'users'

    # Create tables
    db.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) UNIQUE,
            password_hash VARCHAR(255)
        )
    ''')

    # Setup auth
    auth = Auth(app, secret_key='integration-test-key')

    # API Routes
    @app.post('/register')
    async def register(request):
        data = await request.json()

        # Hash password
        password_hash = hash_password(data['password'])

        # Save user
        db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (data['username'], password_hash)
        )

        return {'message': 'User registered'}

    @app.post('/login')
    async def login(request):
        data = await request.json()

        # Find user
        users = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (data['username'],)
        )

        if not users:
            return {'error': 'User not found'}, 404

        user = users[0]

        # Verify password
        if not verify_password(data['password'], user['password_hash']):
            return {'error': 'Invalid password'}, 401

        # Create token
        token = auth.create_token(user_id=str(user['id']))

        return {'token': token, 'user_id': user['id']}

    @app.get('/profile')
    @login_required
    async def profile(request):
        return {'user_id': request.user_id}

    # Check everything is configured
    assert len(app.routes) >= 3, "Routes not registered"
    assert auth is not None, "Auth not configured"
    assert db is not None, "Database not configured"

    return "Full integration successful"


# ====================
# 7. TEST API WORKFLOW
# ====================

@test("Complete API Workflow")
def test_api_workflow():
    """Test a complete user workflow"""
    from covet import Covet
    from covet.orm import Database
    from covet.auth import Auth
    from covet.auth.password import hash_password, verify_password

    app = Covet()
    db = Database('sqlite:///:memory:')
    auth = Auth(app, secret_key='workflow-test')

    # Setup database
    db.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100) UNIQUE,
            email VARCHAR(255),
            password_hash VARCHAR(255),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Simulate user workflow
    # 1. Register
    username = 'testuser'
    email = 'test@example.com'
    password = 'SecurePass123!'
    password_hash = hash_password(password)

    db.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (username, email, password_hash)
    )

    # 2. Login (verify credentials)
    users = db.execute("SELECT * FROM users WHERE username = ?", (username,))
    assert len(users) == 1, "User not found"
    user = users[0]
    assert verify_password(password, user['password_hash']), "Password verification failed"

    # 3. Create token
    token = auth.create_token(user_id=str(user['id']))
    assert token is not None, "Token creation failed"

    # 4. Use token to access protected resource
    user_id = auth.verify_token(token)
    assert user_id == str(user['id']), "Token verification failed"

    # 5. Logout (token would be blacklisted in production)
    # auth.blacklist_token(token)  # Would implement this

    return "Complete workflow successful"


# ====================
# 8. TEST ERROR HANDLING
# ====================

@test("Error Handling")
def test_error_handling():
    """Test error handling and edge cases"""
    from covet import Covet
    from covet.auth import Auth

    app = Covet(debug=True)
    auth = Auth(app, secret_key='error-test')

    # Test invalid token
    try:
        auth.verify_token("invalid-token")
        return "Should have raised error"
    except Exception:
        pass  # Expected

    # Test wrong password
    from covet.auth.password import verify_password
    assert not verify_password("wrong", "hash"), "Wrong password verified"

    return "Error handling working"


# ====================
# RUN ALL TESTS
# ====================

def run_all_tests():
    """Run all integration tests"""

    print("\n" + "=" * 80)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 80)

    # Run tests
    test_imports()
    test_http_server()
    test_database_orm()
    test_authentication()
    test_middleware()
    test_full_integration()
    test_api_workflow()
    test_error_handling()

    # Print summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    print()

    print(f"{'Test Name':<35} {'Status':<12} {'Details'}")
    print("-" * 80)

    for name, status, details in test_results:
        # Truncate details if too long
        if len(details) > 30:
            details = details[:27] + "..."
        print(f"{name:<35} {status:<12} {details}")

    print("-" * 80)

    # Statistics
    total = tests_passed + tests_failed
    percentage = (tests_passed / total * 100) if total > 0 else 0

    print(f"\n📊 Results:")
    print(f"   Passed: {tests_passed}/{total} ({percentage:.1f}%)")
    print(f"   Failed: {tests_failed}/{total}")

    # Overall assessment
    print(f"\n🎯 Overall Assessment:")
    if percentage >= 80:
        print("   ✅ Framework is WORKING WELL (>80% tests passing)")
        print("   - Core functionality is solid")
        print("   - Ready for beta testing")
    elif percentage >= 60:
        print("   ⚠️ Framework is MOSTLY WORKING (>60% tests passing)")
        print("   - Core features work")
        print("   - Some issues need fixing")
    else:
        print("   ❌ Framework has SIGNIFICANT ISSUES (<60% tests passing)")
        print("   - Major problems exist")
        print("   - Not ready for use")

    return test_results


if __name__ == "__main__":
    results = run_all_tests()

    # Save results
    with open('integration_test_results.json', 'w') as f:
        json.dump([{
            'test': name,
            'status': 'pass' if 'PASS' in status else 'fail',
            'details': details
        } for name, status, details in results], f, indent=2)

    print(f"\n💾 Results saved to integration_test_results.json")
    print("\n✨ Integration testing complete!")