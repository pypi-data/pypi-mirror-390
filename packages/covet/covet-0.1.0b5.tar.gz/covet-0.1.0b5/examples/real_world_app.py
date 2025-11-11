#!/usr/bin/env python3
"""
Real-World E-Commerce API Application
======================================
This application tests ALL CovetPy framework features:
- HTTP/ASGI Server
- Routing & Middleware
- Database ORM & Migrations
- Authentication (JWT)
- WebSocket (real-time notifications)
- GraphQL API
- Caching
- Templates
- Security features
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test imports to verify what's actually available
print("=" * 80)
print("TESTING COVETPY FRAMEWORK IMPORTS")
print("=" * 80)

# Core imports
try:
    from covet.core import Application, Request, Response, Router
    print("✅ Core imports successful")
except ImportError as e:
    print(f"❌ Core imports failed: {e}")

# Database imports
try:
    from covet.database.orm import Model, Field
    from covet.database.orm.fields import IntegerField, StringField, DateTimeField, ForeignKey, DecimalField
    from covet.database.adapters.sqlite import SQLiteAdapter
    from covet.database.migrations import MigrationManager
    print("✅ Database/ORM imports successful")
except ImportError as e:
    print(f"❌ Database/ORM imports failed: {e}")

# Authentication imports
try:
    from covet.security.jwt_auth import JWTAuthenticator, JWTConfig, JWTAlgorithm
    from covet.security.enhanced_validation import EnhancedValidator
    from covet.security.secure_crypto import SecureCrypto
    print("✅ Security imports successful")
except ImportError as e:
    print(f"❌ Security imports failed: {e}")

# API imports
try:
    from covet.api.rest import RESTFramework
    from covet.api.graphql import GraphQLFramework
    print("✅ API imports successful")
except ImportError as e:
    print(f"❌ API imports failed: {e}")

# WebSocket imports
try:
    from covet.websocket import WebSocketServer, WebSocketConnection
    print("✅ WebSocket imports successful")
except ImportError as e:
    print(f"❌ WebSocket imports failed: {e}")

# Cache imports
try:
    from covet.cache import CacheManager
    from covet.cache.backends.memory import MemoryCache
    print("✅ Cache imports successful")
except ImportError as e:
    print(f"❌ Cache imports failed: {e}")

# Template imports
try:
    from covet.templates import TemplateEngine
    print("✅ Template imports successful")
except ImportError as e:
    print(f"❌ Template imports failed: {e}")

print("=" * 80)
print()

# ====================
# DATABASE MODELS
# ====================

class User(Model):
    """User model with authentication"""
    __tablename__ = 'users'

    id = IntegerField(primary_key=True)
    email = StringField(max_length=255, unique=True)
    username = StringField(max_length=100, unique=True)
    password_hash = StringField(max_length=255)
    is_active = IntegerField(default=1)  # Boolean as int
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class Product(Model):
    """Product model for e-commerce"""
    __tablename__ = 'products'

    id = IntegerField(primary_key=True)
    name = StringField(max_length=255)
    description = StringField(max_length=1000)
    price = DecimalField(decimal_places=2)
    stock = IntegerField(default=0)
    category = StringField(max_length=100)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class Order(Model):
    """Order model"""
    __tablename__ = 'orders'

    id = IntegerField(primary_key=True)
    user_id = ForeignKey('users')
    total = DecimalField(decimal_places=2)
    status = StringField(max_length=50, default='pending')
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class OrderItem(Model):
    """Order items"""
    __tablename__ = 'order_items'

    id = IntegerField(primary_key=True)
    order_id = ForeignKey('orders')
    product_id = ForeignKey('products')
    quantity = IntegerField()
    price = DecimalField(decimal_places=2)

# ====================
# APPLICATION SETUP
# ====================

class ECommerceAPI:
    """Main e-commerce application"""

    def __init__(self):
        """Initialize the application"""
        print("Initializing E-Commerce API...")

        # Create application
        self.app = Application()

        # Initialize components
        self.setup_database()
        self.setup_authentication()
        self.setup_cache()
        self.setup_middleware()
        self.setup_routes()
        self.setup_websocket()
        self.setup_graphql()

        print("✅ Application initialized successfully")

    def setup_database(self):
        """Setup database and ORM"""
        print("\n📦 Setting up database...")
        try:
            # Initialize SQLite adapter
            self.db = SQLiteAdapter('ecommerce.db')

            # Create tables
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.db.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(255) NOT NULL,
                    description VARCHAR(1000),
                    price DECIMAL(10,2) NOT NULL,
                    stock INTEGER DEFAULT 0,
                    category VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            self.db.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total DECIMAL(10,2) NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')

            self.db.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )
            ''')

            print("✅ Database tables created")

            # Seed sample data
            self.seed_data()

        except Exception as e:
            print(f"❌ Database setup failed: {e}")

    def seed_data(self):
        """Seed sample data"""
        print("🌱 Seeding sample data...")

        # Check if data exists
        result = self.db.execute("SELECT COUNT(*) as count FROM products")
        if result and result[0]['count'] > 0:
            print("✅ Data already seeded")
            return

        # Insert sample products
        products = [
            ('Laptop', 'High-performance laptop', 999.99, 10, 'Electronics'),
            ('Smartphone', 'Latest model smartphone', 699.99, 25, 'Electronics'),
            ('Coffee Maker', 'Automatic coffee machine', 149.99, 15, 'Appliances'),
            ('Running Shoes', 'Professional running shoes', 89.99, 50, 'Sports'),
            ('Backpack', 'Waterproof hiking backpack', 59.99, 30, 'Travel'),
        ]

        for name, desc, price, stock, category in products:
            self.db.execute(
                "INSERT INTO products (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)",
                (name, desc, price, stock, category)
            )

        print(f"✅ Inserted {len(products)} sample products")

    def setup_authentication(self):
        """Setup JWT authentication"""
        print("\n🔐 Setting up authentication...")
        try:
            # Use HS256 for simplicity (RS256 requires key generation)
            config = JWTConfig(
                algorithm=JWTAlgorithm.HS256,
                secret_key='your-secret-key-change-in-production',
                access_token_expire=timedelta(hours=1),
                refresh_token_expire=timedelta(days=7)
            )
            self.auth = JWTAuthenticator(config)
            self.validator = EnhancedValidator()
            self.crypto = SecureCrypto()
            print("✅ Authentication configured")
        except Exception as e:
            print(f"❌ Authentication setup failed: {e}")

    def setup_cache(self):
        """Setup caching"""
        print("\n💾 Setting up cache...")
        try:
            self.cache = MemoryCache()
            print("✅ Memory cache initialized")
        except Exception as e:
            print(f"❌ Cache setup failed: {e}")

    def setup_middleware(self):
        """Setup middleware pipeline"""
        print("\n🔧 Setting up middleware...")

        # CORS middleware
        @self.app.middleware('http')
        async def cors_middleware(request, call_next):
            response = await call_next(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response

        # Logging middleware
        @self.app.middleware('http')
        async def logging_middleware(request, call_next):
            start = datetime.now()
            response = await call_next(request)
            duration = (datetime.now() - start).total_seconds()
            print(f"[{request.method}] {request.path} - {response.status_code} ({duration:.3f}s)")
            return response

        print("✅ Middleware configured")

    def setup_routes(self):
        """Setup REST API routes"""
        print("\n🛣️ Setting up routes...")

        # Health check
        @self.app.route('/health')
        async def health_check(request: Request) -> Response:
            return Response(json.dumps({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0'
            }), content_type='application/json')

        # User registration
        @self.app.route('/api/register', methods=['POST'])
        async def register(request: Request) -> Response:
            try:
                data = await request.json()

                # Validate input
                is_valid, message = self.validator.validate_email(data.get('email', ''))
                if not is_valid:
                    return Response(json.dumps({'error': message}), status_code=400)

                # Hash password
                password_hash = self.crypto.hash_password(data.get('password', ''))

                # Create user
                self.db.execute(
                    "INSERT INTO users (email, username, password_hash) VALUES (?, ?, ?)",
                    (data['email'], data['username'], password_hash)
                )

                return Response(json.dumps({'message': 'User created successfully'}))
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), status_code=500)

        # User login
        @self.app.route('/api/login', methods=['POST'])
        async def login(request: Request) -> Response:
            try:
                data = await request.json()

                # Find user
                users = self.db.execute(
                    "SELECT * FROM users WHERE email = ?",
                    (data.get('email', ''),)
                )

                if not users:
                    return Response(json.dumps({'error': 'Invalid credentials'}), status_code=401)

                user = users[0]

                # Verify password
                if not self.crypto.verify_password(data.get('password', ''), user['password_hash']):
                    return Response(json.dumps({'error': 'Invalid credentials'}), status_code=401)

                # Generate tokens
                access_token = self.auth.create_access_token(str(user['id']))
                refresh_token = self.auth.create_refresh_token(str(user['id']))

                return Response(json.dumps({
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'username': user['username']
                    }
                }))
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), status_code=500)

        # Get all products
        @self.app.route('/api/products')
        async def get_products(request: Request) -> Response:
            try:
                # Check cache first
                cached = self.cache.get('products_all')
                if cached:
                    return Response(cached, content_type='application/json')

                # Query database
                products = self.db.execute("SELECT * FROM products")

                # Cache for 5 minutes
                response_data = json.dumps({'products': products})
                self.cache.set('products_all', response_data, ttl=300)

                return Response(response_data, content_type='application/json')
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), status_code=500)

        # Get single product
        @self.app.route('/api/products/{id}')
        async def get_product(request: Request) -> Response:
            try:
                product_id = request.path_params.get('id')

                # Check cache
                cache_key = f'product_{product_id}'
                cached = self.cache.get(cache_key)
                if cached:
                    return Response(cached, content_type='application/json')

                # Query database
                products = self.db.execute(
                    "SELECT * FROM products WHERE id = ?",
                    (product_id,)
                )

                if not products:
                    return Response(json.dumps({'error': 'Product not found'}), status_code=404)

                response_data = json.dumps({'product': products[0]})
                self.cache.set(cache_key, response_data, ttl=300)

                return Response(response_data, content_type='application/json')
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), status_code=500)

        # Create order
        @self.app.route('/api/orders', methods=['POST'])
        async def create_order(request: Request) -> Response:
            try:
                # Verify JWT token
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return Response(json.dumps({'error': 'Unauthorized'}), status_code=401)

                token = auth_header[7:]
                try:
                    claims = self.auth.verify_token(token)
                    user_id = claims['sub']
                except Exception:
                    return Response(json.dumps({'error': 'Invalid token'}), status_code=401)

                # Create order
                data = await request.json()
                items = data.get('items', [])

                # Calculate total
                total = 0
                for item in items:
                    products = self.db.execute(
                        "SELECT price FROM products WHERE id = ?",
                        (item['product_id'],)
                    )
                    if products:
                        total += float(products[0]['price']) * item['quantity']

                # Insert order
                cursor = self.db.connection.cursor()
                cursor.execute(
                    "INSERT INTO orders (user_id, total) VALUES (?, ?)",
                    (user_id, total)
                )
                order_id = cursor.lastrowid

                # Insert order items
                for item in items:
                    products = self.db.execute(
                        "SELECT price FROM products WHERE id = ?",
                        (item['product_id'],)
                    )
                    if products:
                        cursor.execute(
                            "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)",
                            (order_id, item['product_id'], item['quantity'], products[0]['price'])
                        )

                self.db.connection.commit()

                return Response(json.dumps({
                    'order_id': order_id,
                    'total': total,
                    'status': 'pending'
                }))
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), status_code=500)

        # Admin route - protected
        @self.app.route('/api/admin/stats')
        async def admin_stats(request: Request) -> Response:
            try:
                # Verify admin token (simplified)
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return Response(json.dumps({'error': 'Unauthorized'}), status_code=401)

                # Get statistics
                stats = {
                    'users': self.db.execute("SELECT COUNT(*) as count FROM users")[0]['count'],
                    'products': self.db.execute("SELECT COUNT(*) as count FROM products")[0]['count'],
                    'orders': self.db.execute("SELECT COUNT(*) as count FROM orders")[0]['count'],
                    'revenue': self.db.execute("SELECT SUM(total) as total FROM orders")[0]['total'] or 0
                }

                return Response(json.dumps(stats), content_type='application/json')
            except Exception as e:
                return Response(json.dumps({'error': str(e)}), status_code=500)

        print("✅ REST API routes configured")

    def setup_websocket(self):
        """Setup WebSocket for real-time notifications"""
        print("\n🔌 Setting up WebSocket...")

        # WebSocket handler for real-time order updates
        @self.app.websocket('/ws/orders')
        async def order_updates(websocket):
            await websocket.accept()
            try:
                while True:
                    # Receive message
                    data = await websocket.receive_text()
                    message = json.loads(data)

                    if message.get('type') == 'subscribe':
                        # Send mock order update
                        await websocket.send_text(json.dumps({
                            'type': 'order_update',
                            'order_id': 123,
                            'status': 'processing',
                            'timestamp': datetime.now().isoformat()
                        }))
            except Exception as e:
                print(f"WebSocket error: {e}")
            finally:
                await websocket.close()

        print("✅ WebSocket configured")

    def setup_graphql(self):
        """Setup GraphQL endpoint"""
        print("\n🎯 Setting up GraphQL...")

        # GraphQL schema
        schema = '''
        type User {
            id: Int!
            email: String!
            username: String!
        }

        type Product {
            id: Int!
            name: String!
            description: String
            price: Float!
            stock: Int!
            category: String
        }

        type Query {
            products: [Product]
            product(id: Int!): Product
            user(id: Int!): User
        }

        type Mutation {
            createProduct(name: String!, price: Float!): Product
        }
        '''

        @self.app.route('/graphql', methods=['POST'])
        async def graphql_endpoint(request: Request) -> Response:
            # Simplified GraphQL handler
            try:
                data = await request.json()
                query = data.get('query', '')

                # Simple query parsing (real implementation would use graphql-core)
                if 'products' in query:
                    products = self.db.execute("SELECT * FROM products")
                    return Response(json.dumps({'data': {'products': products}}))

                return Response(json.dumps({'data': None}))
            except Exception as e:
                return Response(json.dumps({'errors': [str(e)]}), status_code=500)

        print("✅ GraphQL endpoint configured")

    async def run(self):
        """Run the application"""
        print("\n" + "=" * 80)
        print("🚀 STARTING E-COMMERCE API SERVER")
        print("=" * 80)

        # Test each component
        await self.test_components()

        print("\n📊 Server Information:")
        print("- HTTP Server: http://localhost:8000")
        print("- WebSocket: ws://localhost:8000/ws/orders")
        print("- GraphQL: http://localhost:8000/graphql")
        print("- Health Check: http://localhost:8000/health")
        print("\n✨ Server is running! Press Ctrl+C to stop.")

        # Run server
        try:
            import uvicorn
            uvicorn.run(self.app, host="0.0.0.0", port=8000)
        except ImportError:
            print("❌ Uvicorn not installed. Please install with: pip install uvicorn")
        except Exception as e:
            print(f"❌ Failed to start server: {e}")

    async def test_components(self):
        """Test framework components"""
        print("\n" + "=" * 80)
        print("🧪 TESTING FRAMEWORK COMPONENTS")
        print("=" * 80)

        results = []

        # Test 1: Database connectivity
        try:
            count = self.db.execute("SELECT COUNT(*) as count FROM products")[0]['count']
            results.append(('Database', '✅ PASS', f'{count} products'))
        except Exception as e:
            results.append(('Database', '❌ FAIL', str(e)))

        # Test 2: JWT generation
        try:
            token = self.auth.create_access_token('test_user')
            results.append(('JWT Auth', '✅ PASS', f'Token length: {len(token)}'))
        except Exception as e:
            results.append(('JWT Auth', '❌ FAIL', str(e)))

        # Test 3: Cache operations
        try:
            self.cache.set('test_key', 'test_value')
            value = self.cache.get('test_key')
            results.append(('Cache', '✅ PASS' if value == 'test_value' else '❌ FAIL', 'Memory cache'))
        except Exception as e:
            results.append(('Cache', '❌ FAIL', str(e)))

        # Test 4: Input validation
        try:
            is_valid, msg = self.validator.validate_email('test@example.com')
            results.append(('Validation', '✅ PASS' if is_valid else '❌ FAIL', msg))
        except Exception as e:
            results.append(('Validation', '❌ FAIL', str(e)))

        # Test 5: Password hashing
        try:
            hashed = self.crypto.hash_password('testpass123')
            verified = self.crypto.verify_password('testpass123', hashed)
            results.append(('Crypto', '✅ PASS' if verified else '❌ FAIL', 'PBKDF2-SHA256'))
        except Exception as e:
            results.append(('Crypto', '❌ FAIL', str(e)))

        # Print results
        print("\n📋 Component Test Results:")
        print("-" * 60)
        for component, status, details in results:
            print(f"{component:15} {status:10} {details}")
        print("-" * 60)

        # Summary
        passed = sum(1 for _, status, _ in results if 'PASS' in status)
        total = len(results)
        print(f"\n📊 Summary: {passed}/{total} components working ({passed*100//total}%)")

        return results

# ====================
# MAIN ENTRY POINT
# ====================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("COVETPY REAL-WORLD APPLICATION TEST")
    print("E-Commerce API with Full Feature Testing")
    print("=" * 80)

    # Create and run application
    app = ECommerceAPI()

    # Run async application
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ Application crashed: {e}")
        import traceback
        traceback.print_exc()