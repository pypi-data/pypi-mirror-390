"""
Comprehensive GraphQL + WebSocket Demo

Demonstrates production-ready GraphQL API with real-time subscriptions
over WebSocket, JWT authentication, DataLoader optimization, and more.

Features:
- GraphQL queries, mutations, and subscriptions
- JWT authentication integration
- DataLoader for N+1 query optimization
- Relay-style pagination
- Real-time updates via WebSocket subscriptions
- Pub/sub system for broadcasting
- GraphQL Playground UI
"""

import asyncio
import sys
sys.path.append('/Users/vipin/Downloads/NeutrinoPy/src')

from covet.api.graphql import (
    GraphQLFramework,
    GraphQLConfig,
    create_graphql_app,
    graphql_type,
    graphql_input,
    field,
    DataLoader,
    relay_connection,
    Connection,
    subscribe,
    publish,
)
from covet.security.jwt_auth import JWTConfig, JWTAuthenticator
from typing import List, Optional, AsyncIterator
from dataclasses import dataclass
import strawberry


# =============================================================================
# Data Models
# =============================================================================

@strawberry.type
class User:
    """User type."""
    id: int
    name: str
    email: str
    role: str
    
    @strawberry.field
    async def posts(self, info) -> List['Post']:
        """Get user's posts (with DataLoader)."""
        # In production, use DataLoader from context
        # For demo, return mock data
        return [
            Post(id=1, title="Hello World", content="First post", author_id=self.id),
            Post(id=2, title="GraphQL is Great", content="Second post", author_id=self.id),
        ]


@strawberry.type
class Post:
    """Post type."""
    id: int
    title: str
    content: str
    author_id: int
    
    @strawberry.field
    async def author(self, info) -> User:
        """Get post author (with DataLoader)."""
        # In production, use DataLoader to batch fetch authors
        return User(
            id=self.author_id,
            name="John Doe",
            email="john@example.com",
            role="user"
        )


@strawberry.input
class CreateUserInput:
    """Input for creating user."""
    name: str
    email: str
    password: str


@strawberry.input
class CreatePostInput:
    """Input for creating post."""
    title: str
    content: str


@strawberry.type
class AuthPayload:
    """Authentication payload."""
    access_token: str
    refresh_token: str
    user: User


# =============================================================================
# Mock Database
# =============================================================================

class MockDatabase:
    """Mock database for demo."""
    
    def __init__(self):
        self.users = [
            User(id=1, name="Alice", email="alice@example.com", role="admin"),
            User(id=2, name="Bob", email="bob@example.com", role="user"),
            User(id=3, name="Charlie", email="charlie@example.com", role="user"),
        ]
        self.posts = [
            Post(id=1, title="First Post", content="Hello", author_id=1),
            Post(id=2, title="GraphQL Tutorial", content="Learn GraphQL", author_id=1),
            Post(id=3, title="WebSocket Chat", content="Real-time chat", author_id=2),
        ]
        self._next_user_id = 4
        self._next_post_id = 4
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    async def get_users(self, limit: int = 10) -> List[User]:
        """Get all users."""
        return self.users[:limit]
    
    async def create_user(self, input: CreateUserInput) -> User:
        """Create new user."""
        user = User(
            id=self._next_user_id,
            name=input.name,
            email=input.email,
            role="user"
        )
        self.users.append(user)
        self._next_user_id += 1
        return user
    
    async def get_post(self, post_id: int) -> Optional[Post]:
        """Get post by ID."""
        for post in self.posts:
            if post.id == post_id:
                return post
        return None
    
    async def get_posts(self, limit: int = 10) -> List[Post]:
        """Get all posts."""
        return self.posts[:limit]
    
    async def create_post(self, input: CreatePostInput, author_id: int) -> Post:
        """Create new post."""
        post = Post(
            id=self._next_post_id,
            title=input.title,
            content=input.content,
            author_id=author_id,
        )
        self.posts.append(post)
        self._next_post_id += 1
        
        # Publish event for subscriptions
        await publish('post.created', {
            'id': post.id,
            'title': post.title,
            'author_id': author_id,
        })
        
        return post


db = MockDatabase()


# =============================================================================
# DataLoaders
# =============================================================================

async def batch_load_users(user_ids: List[int]) -> List[Optional[User]]:
    """Batch load users (prevents N+1 queries)."""
    print(f"[DataLoader] Batch loading {len(user_ids)} users")
    
    # In production, make single database query for all IDs
    users = {user.id: user for user in db.users}
    return [users.get(user_id) for user_id in user_ids]


async def batch_load_posts(post_ids: List[int]) -> List[Optional[Post]]:
    """Batch load posts."""
    print(f"[DataLoader] Batch loading {len(post_ids)} posts")
    
    posts = {post.id: post for post in db.posts}
    return [posts.get(post_id) for post_id in post_ids]


# =============================================================================
# GraphQL Schema
# =============================================================================

@strawberry.type
class Query:
    """Root Query type."""
    
    @strawberry.field
    async def me(self, info) -> Optional[User]:
        """Get current user."""
        # Get user from auth context
        context = info.context
        if hasattr(context, 'user') and context.user:
            user_id = context.user.get('id')
            # In production, parse user_id properly
            return await db.get_user(1)  # Mock
        return None
    
    @strawberry.field
    async def user(self, id: int) -> Optional[User]:
        """Get user by ID."""
        return await db.get_user(id)
    
    @strawberry.field
    async def users(
        self,
        first: Optional[int] = 10,
        after: Optional[str] = None,
    ) -> Connection[User]:
        """Get users with pagination."""
        users = await db.get_users(limit=first or 10)
        return relay_connection(users, first=first, after=after, total_count=len(db.users))
    
    @strawberry.field
    async def post(self, id: int) -> Optional[Post]:
        """Get post by ID."""
        return await db.get_post(id)
    
    @strawberry.field
    async def posts(
        self,
        first: Optional[int] = 10,
    ) -> List[Post]:
        """Get posts."""
        return await db.get_posts(limit=first or 10)


@strawberry.type
class Mutation:
    """Root Mutation type."""
    
    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> User:
        """Create new user."""
        user = await db.create_user(input)
        
        # Publish event
        await publish('user.created', {
            'id': user.id,
            'name': user.name,
            'email': user.email,
        })
        
        return user
    
    @strawberry.mutation
    async def create_post(self, input: CreatePostInput, info) -> Post:
        """Create new post (requires authentication)."""
        # Get current user
        context = info.context
        if not hasattr(context, 'user') or not context.user:
            raise PermissionError("Authentication required")
        
        author_id = 1  # Mock - should get from context.user['id']
        return await db.create_post(input, author_id)


@strawberry.type
class Subscription:
    """Root Subscription type."""
    
    @strawberry.subscription
    async def post_created(self) -> AsyncIterator[Post]:
        """Subscribe to new posts."""
        # Subscribe to pub/sub topic
        async for message in subscribe('post.created'):
            # Convert message to Post object
            post = await db.get_post(message['id'])
            if post:
                yield post
    
    @strawberry.subscription
    async def user_created(self) -> AsyncIterator[User]:
        """Subscribe to new users."""
        async for message in subscribe('user.created'):
            user = await db.get_user(message['id'])
            if user:
                yield user
    
    @strawberry.subscription
    async def notifications(self, user_id: int) -> AsyncIterator[str]:
        """Subscribe to user-specific notifications."""
        # Filter messages for specific user
        async for message in subscribe(f'notifications.{user_id}'):
            yield message


# =============================================================================
# Create GraphQL Application
# =============================================================================

def create_demo_app():
    """Create demo GraphQL application."""
    
    # Configure JWT authentication
    jwt_config = JWTConfig(
        algorithm='HS256',
        secret_key='demo-secret-key-change-in-production',
        access_token_expire_minutes=15,
    )
    jwt_auth = JWTAuthenticator(jwt_config)
    
    # Configure GraphQL
    config = GraphQLConfig(
        enable_introspection=True,
        enable_playground=True,
        playground_path='/graphql',
        playground_type='graphql-playground',  # or 'graphiql' or 'apollo-sandbox'
        enable_subscriptions=True,
        subscription_path='/graphql',
        max_query_depth=10,
        max_query_complexity=1000,
        debug=True,
    )
    
    # Create framework
    framework = GraphQLFramework(config=config, authenticator=jwt_auth)
    
    # Register schema
    framework.query(Query)
    framework.mutation(Mutation)
    framework.subscription(Subscription)
    
    # Build schema
    schema = framework.build_schema()
    
    print("GraphQL Schema SDL:")
    print("=" * 80)
    print(schema)
    print("=" * 80)
    
    return framework


# =============================================================================
# Demo Queries
# =============================================================================

async def demo_queries(framework: GraphQLFramework):
    """Demonstrate GraphQL queries."""
    
    print("\n" + "=" * 80)
    print("DEMO: GraphQL Queries")
    print("=" * 80)
    
    # Query: Get all users
    print("\n1. Query: Get all users")
    result = await framework.execute_query("""
        query GetUsers {
            users(first: 5) {
                edges {
                    node {
                        id
                        name
                        email
                        role
                    }
                    cursor
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                }
                totalCount
            }
        }
    """)
    print(f"Result: {result.to_dict()}")
    
    # Query: Get user with posts
    print("\n2. Query: Get user with posts")
    result = await framework.execute_query("""
        query GetUserWithPosts {
            user(id: 1) {
                id
                name
                posts {
                    id
                    title
                }
            }
        }
    """)
    print(f"Result: {result.to_dict()}")
    
    # Mutation: Create user
    print("\n3. Mutation: Create user")
    result = await framework.execute_query("""
        mutation CreateUser {
            createUser(input: {
                name: "New User"
                email: "newuser@example.com"
                password: "secret123"
            }) {
                id
                name
                email
            }
        }
    """)
    print(f"Result: {result.to_dict()}")


# =============================================================================
# Main
# =============================================================================

async def main():
    """Run demo."""
    print("=" * 80)
    print("GraphQL + WebSocket Production Demo")
    print("=" * 80)
    
    # Create application
    framework = create_demo_app()
    
    # Run demo queries
    await demo_queries(framework)
    
    print("\n" + "=" * 80)
    print("Server Information")
    print("=" * 80)
    print("To run the GraphQL server:")
    print("  uvicorn graphql_websocket_demo:app --host 0.0.0.0 --port 8000")
    print("\nEndpoints:")
    print("  GraphQL API: http://localhost:8000/graphql")
    print("  GraphQL Playground: http://localhost:8000/graphql (in browser)")
    print("  WebSocket Subscriptions: ws://localhost:8000/graphql")
    print("\nExample Subscription (in Playground):")
    print("""
  subscription {
    postCreated {
      id
      title
      author {
        name
      }
    }
  }
    """)
    print("=" * 80)


# ASGI application for uvicorn
def create_app():
    """Create ASGI app for uvicorn."""
    framework = create_demo_app()
    return framework.create_asgi_app()


app = create_app()


if __name__ == '__main__':
    asyncio.run(main())
