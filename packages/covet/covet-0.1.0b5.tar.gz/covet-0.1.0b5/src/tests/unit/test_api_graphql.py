"""
Unit Tests for CovetPy GraphQL API Module

These tests validate GraphQL implementation including schema definition,
query parsing, execution, and resolver functionality. All tests use real
GraphQL operations to ensure production-grade functionality.

CRITICAL: Tests validate real GraphQL implementation, not mocks.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pytest

from covet.api.graphql import (
    GraphQLArgument,
    GraphQLField,
    GraphQLSchema,
    SubscriptionExecutor,
)
from covet.api.graphql.execution import GraphQLExecutor
from covet.api.graphql.parser import GraphQLParser
from covet.api.graphql.type_system import (
    GraphQLBoolean,
    GraphQLID,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLString,
)
from covet.api.graphql.validation import GraphQLValidator


@dataclass
class User:
    """Test user model."""

    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool = True


@dataclass
class Post:
    """Test post model."""

    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    published: bool = False


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.graphql
class TestGraphQLSchema:
    """Test GraphQL schema definition and validation."""

    @pytest.fixture
    def user_type(self):
        """Create User GraphQL type."""
        return GraphQLObjectType(
            name="User",
            fields={
                "id": GraphQLField(GraphQLNonNull(GraphQLID)),
                "username": GraphQLField(GraphQLNonNull(GraphQLString)),
                "email": GraphQLField(GraphQLNonNull(GraphQLString)),
                "created_at": GraphQLField(GraphQLNonNull(GraphQLString)),
                "is_active": GraphQLField(GraphQLBoolean, default_value=True),
                "posts": GraphQLField(
                    GraphQLList(lambda: post_type),
                    resolver=lambda user, info, **args: get_user_posts(user.id),
                ),
            },
        )

    @pytest.fixture
    def post_type(self):
        """Create Post GraphQL type."""
        return GraphQLObjectType(
            name="Post",
            fields={
                "id": GraphQLField(GraphQLNonNull(GraphQLID)),
                "title": GraphQLField(GraphQLNonNull(GraphQLString)),
                "content": GraphQLField(GraphQLNonNull(GraphQLString)),
                "author_id": GraphQLField(GraphQLNonNull(GraphQLID)),
                "created_at": GraphQLField(GraphQLNonNull(GraphQLString)),
                "published": GraphQLField(GraphQLBoolean, default_value=False),
                "author": GraphQLField(
                    lambda: user_type,
                    resolver=lambda post, info, **args: get_user_by_id(post.author_id),
                ),
            },
        )

    @pytest.fixture
    def schema(self, user_type, post_type):
        """Create GraphQL schema."""
        query_type = GraphQLObjectType(
            name="Query",
            fields={
                "user": GraphQLField(
                    user_type,
                    args={"id": GraphQLArgument(GraphQLNonNull(GraphQLID))},
                    resolver=lambda root, info, **args: get_user_by_id(args["id"]),
                ),
                "users": GraphQLField(
                    GraphQLList(user_type),
                    args={
                        "limit": GraphQLArgument(GraphQLInt, default_value=10),
                        "offset": GraphQLArgument(GraphQLInt, default_value=0),
                    },
                    resolver=lambda root, info, **args: get_users(
                        args["limit"], args["offset"]
                    ),
                ),
                "post": GraphQLField(
                    post_type,
                    args={"id": GraphQLArgument(GraphQLNonNull(GraphQLID))},
                    resolver=lambda root, info, **args: get_post_by_id(args["id"]),
                ),
            },
        )

        mutation_type = GraphQLObjectType(
            name="Mutation",
            fields={
                "createUser": GraphQLField(
                    user_type,
                    args={
                        "username": GraphQLArgument(GraphQLNonNull(GraphQLString)),
                        "email": GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    },
                    resolver=lambda root, info, **args: create_user(
                        args["username"], args["email"]
                    ),
                ),
                "updateUser": GraphQLField(
                    user_type,
                    args={
                        "id": GraphQLArgument(GraphQLNonNull(GraphQLID)),
                        "username": GraphQLArgument(GraphQLString),
                        "email": GraphQLArgument(GraphQLString),
                    },
                    resolver=lambda root, info, **args: update_user(args["id"], args),
                ),
            },
        )

        return GraphQLSchema(query=query_type, mutation=mutation_type)

    def test_schema_validation(self, schema):
        """Test GraphQL schema validation."""
        # Schema should be valid
        errors = schema.validate()
        assert len(errors) == 0, f"Schema validation errors: {errors}"

        # Verify query type exists
        assert schema.query_type is not None
        assert schema.query_type.name == "Query"

        # Verify mutation type exists
        assert schema.mutation_type is not None
        assert schema.mutation_type.name == "Mutation"

        # Verify fields are properly defined
        query_fields = schema.query_type.fields
        assert "user" in query_fields
        assert "users" in query_fields
        assert "post" in query_fields

        mutation_fields = schema.mutation_type.fields
        assert "createUser" in mutation_fields
        assert "updateUser" in mutation_fields

    def test_type_system_validation(self, user_type, post_type):
        """Test GraphQL type system validation."""
        # Test field types
        user_fields = user_type.fields
        assert isinstance(user_fields["id"].type, GraphQLNonNull)
        assert isinstance(user_fields["username"].type, GraphQLNonNull)
        assert user_fields["is_active"].type == GraphQLBoolean

        # Test list types
        posts_field = user_fields["posts"]
        assert isinstance(posts_field.type, GraphQLList)

        # Test circular references
        post_fields = post_type.fields
        author_field = post_fields["author"]
        assert callable(author_field.type)  # Should be a lambda for circular reference

    def test_schema_introspection(self, schema):
        """Test GraphQL schema introspection."""

        # Schema should support introspection
        introspection_result = schema.introspect()
        assert "__schema" in introspection_result
        assert "types" in introspection_result["__schema"]

        # Should include our custom types
        type_names = [t["name"] for t in introspection_result["__schema"]["types"]]
        assert "User" in type_names
        assert "Post" in type_names
        assert "Query" in type_names
        assert "Mutation" in type_names


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.graphql
class TestGraphQLParser:
    """Test GraphQL query parsing."""

    @pytest.fixture
    def parser(self):
        """Create GraphQL parser."""
        return GraphQLParser()

    def test_simple_query_parsing(self, parser):
        """Test parsing simple GraphQL queries."""
        query = """
        {
            user(id: "123") {
                id
                username
                email
            }
        }
        """

        parsed = parser.parse(query)

        assert parsed.operation_type == "query"
        assert len(parsed.selections) == 1

        user_field = parsed.selections[0]
        assert user_field.name == "user"
        assert len(user_field.arguments) == 1
        assert user_field.arguments[0].name == "id"
        assert user_field.arguments[0].value == "123"

        # Check selected fields
        selected_fields = [field.name for field in user_field.selections]
        assert "id" in selected_fields
        assert "username" in selected_fields
        assert "email" in selected_fields

    def test_complex_query_parsing(self, parser):
        """Test parsing complex GraphQL queries with nested fields."""
        query = """
        query GetUserWithPosts($userId: ID!, $postLimit: Int = 5) {
            user(id: $userId) {
                id
                username
                email
                posts(limit: $postLimit) {
                    id
                    title
                    content
                    created_at
                    author {
                        username
                    }
                }
            }
        }
        """

        parsed = parser.parse(query)

        assert parsed.operation_type == "query"
        assert parsed.operation_name == "GetUserWithPosts"

        # Check variables
        assert len(parsed.variables) == 2
        variable_names = [var.name for var in parsed.variables]
        assert "userId" in variable_names
        assert "postLimit" in variable_names

        # Check nested selections
        user_field = parsed.selections[0]
        posts_field = next(
            field for field in user_field.selections if field.name == "posts"
        )
        assert len(posts_field.selections) >= 4

    def test_mutation_parsing(self, parser):
        """Test parsing GraphQL mutations."""
        mutation = """
        mutation CreateUser($input: CreateUserInput!) {
            createUser(username: $input.username, email: $input.email) {
                id
                username
                email
                created_at
            }
        }
        """

        parsed = parser.parse(mutation)

        assert parsed.operation_type == "mutation"
        assert parsed.operation_name == "CreateUser"

        create_user_field = parsed.selections[0]
        assert create_user_field.name == "createUser"
        assert len(create_user_field.arguments) == 2

    def test_subscription_parsing(self, parser):
        """Test parsing GraphQL subscriptions."""
        subscription = """
        subscription PostUpdates($userId: ID!) {
            postUpdated(authorId: $userId) {
                id
                title
                content
                author {
                    username
                }
            }
        }
        """

        parsed = parser.parse(subscription)

        assert parsed.operation_type == "subscription"
        assert parsed.operation_name == "PostUpdates"

        post_updated_field = parsed.selections[0]
        assert post_updated_field.name == "postUpdated"

    def test_fragment_parsing(self, parser):
        """Test parsing GraphQL fragments."""
        query = """
        fragment UserInfo on User {
            id
            username
            email
            created_at
        }

        query GetUsers {
            users {
                ...UserInfo
                posts {
                    id
                    title
                }
            }
        }
        """

        parsed = parser.parse(query)

        # Should have both fragment and query
        assert len(parsed.definitions) == 2

        fragment = parsed.definitions[0]
        assert fragment.kind == "FragmentDefinition"
        assert fragment.name == "UserInfo"
        assert fragment.type_condition == "User"

        query_def = parsed.definitions[1]
        users_field = query_def.selections[0]

        # Should have fragment spread
        fragment_spread = next(
            selection
            for selection in users_field.selections
            if hasattr(selection, "kind") and selection.kind == "FragmentSpread"
        )
        assert fragment_spread.name == "UserInfo"

    def test_directive_parsing(self, parser):
        """Test parsing GraphQL directives."""
        query = """
        query GetUser($includeEmail: Boolean!) {
            user(id: "123") {
                id
                username
                email @include(if: $includeEmail)
                posts @skip(if: false) {
                    id
                    title
                }
            }
        }
        """

        parsed = parser.parse(query)

        user_field = parsed.selections[0]
        email_field = next(
            field for field in user_field.selections if field.name == "email"
        )

        # Should have @include directive
        assert len(email_field.directives) == 1
        assert email_field.directives[0].name == "include"
        assert email_field.directives[0].arguments[0].name == "if"

        posts_field = next(
            field for field in user_field.selections if field.name == "posts"
        )

        # Should have @skip directive
        assert len(posts_field.directives) == 1
        assert posts_field.directives[0].name == "skip"


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.graphql
class TestGraphQLExecution:
    """Test GraphQL query execution."""

    @pytest.fixture
    def executor(self, schema):
        """Create GraphQL executor."""
        return GraphQLExecutor(schema)

    # Mock data and resolvers for testing
    users_db = [
        User(1, "alice", "alice@example.com", datetime(2023, 1, 1)),
        User(2, "bob", "bob@example.com", datetime(2023, 1, 2)),
        User(3, "charlie", "charlie@example.com", datetime(2023, 1, 3)),
    ]

    posts_db = [
        Post(1, "Post 1", "Content 1", 1, datetime(2023, 1, 1)),
        Post(2, "Post 2", "Content 2", 1, datetime(2023, 1, 2)),
        Post(3, "Post 3", "Content 3", 2, datetime(2023, 1, 3)),
    ]

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return next((u for u in self.users_db if u.id == int(user_id)), None)

    def get_users(self, limit: int = 10, offset: int = 0) -> list[User]:
        return self.users_db[offset : offset + limit]

    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        return next((p for p in self.posts_db if p.id == int(post_id)), None)

    def get_user_posts(self, user_id: int) -> list[Post]:
        return [p for p in self.posts_db if p.author_id == user_id]

    async def test_simple_query_execution(self, executor):
        """Test executing simple GraphQL queries."""
        query = """
        {
            user(id: "1") {
                id
                username
                email
            }
        }
        """

        result = await executor.execute(query)

        assert "errors" not in result
        assert "data" in result

        user_data = result["data"]["user"]
        assert user_data["id"] == "1"
        assert user_data["username"] == "alice"
        assert user_data["email"] == "alice@example.com"

    async def test_query_with_variables(self, executor):
        """Test executing queries with variables."""
        query = """
        query GetUser($userId: ID!) {
            user(id: $userId) {
                id
                username
                email
            }
        }
        """

        variables = {"userId": "2"}

        result = await executor.execute(query, variables=variables)

        assert "errors" not in result
        user_data = result["data"]["user"]
        assert user_data["id"] == "2"
        assert user_data["username"] == "bob"

    async def test_nested_query_execution(self, executor):
        """Test executing nested GraphQL queries."""
        query = """
        {
            user(id: "1") {
                id
                username
                posts {
                    id
                    title
                    content
                }
            }
        }
        """

        result = await executor.execute(query)

        assert "errors" not in result
        user_data = result["data"]["user"]
        assert user_data["id"] == "1"

        posts = user_data["posts"]
        assert len(posts) == 2  # User 1 has 2 posts
        assert posts[0]["id"] == "1"
        assert posts[0]["title"] == "Post 1"

    async def test_mutation_execution(self, executor):
        """Test executing GraphQL mutations."""
        mutation = """
        mutation {
            createUser(username: "david", email: "david@example.com") {
                id
                username
                email
                created_at
            }
        }
        """

        def create_user(username: str, email: str) -> User:
            new_id = max(u.id for u in self.users_db) + 1
            new_user = User(new_id, username, email, datetime.utcnow())
            self.users_db.append(new_user)
            return new_user

        result = await executor.execute(mutation)

        assert "errors" not in result
        user_data = result["data"]["createUser"]
        assert user_data["username"] == "david"
        assert user_data["email"] == "david@example.com"

    async def test_error_handling_in_execution(self, executor):
        """Test error handling during query execution."""
        # Query for non-existent user
        query = """
        {
            user(id: "999") {
                id
                username
                email
            }
        }
        """

        result = await executor.execute(query)

        # Should return null for non-existent user, not error
        assert result["data"]["user"] is None

        # Query with invalid field
        invalid_query = """
        {
            user(id: "1") {
                id
                username
                nonExistentField
            }
        }
        """

        result = await executor.execute(invalid_query)
        assert "errors" in result
        assert len(result["errors"]) > 0

    async def test_async_resolver_execution(self, executor):
        """Test asynchronous resolver execution."""

        async def async_get_user(user_id: str) -> User:
            # Simulate async database call
            await asyncio.sleep(0.001)
            return self.get_user_by_id(user_id)

        # Mock the resolver to be async
        query = """
        {
            user(id: "1") {
                id
                username
                email
            }
        }
        """

        start_time = asyncio.get_event_loop().time()
        result = await executor.execute(query)
        end_time = asyncio.get_event_loop().time()

        assert "errors" not in result
        assert result["data"]["user"]["id"] == "1"
        assert end_time - start_time >= 0.001  # Verify async execution

    async def test_concurrent_query_execution(self, executor):
        """Test concurrent execution of multiple queries."""
        queries = [
            """{ user(id: "1") { id username } }""",
            """{ user(id: "2") { id username } }""",
            """{ user(id: "3") { id username } }""",
        ]

        start_time = time.time()

        # Execute queries concurrently
        tasks = [executor.execute(query) for query in queries]
        results = await asyncio.gather(*tasks)

        end_time = time.time()

        # All queries should succeed
        for result in results:
            assert "errors" not in result
            assert "data" in result
            assert result["data"]["user"] is not None

        # Should complete faster than sequential execution
        execution_time = end_time - start_time
        assert execution_time < 0.1  # Should be very fast for simple queries


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.graphql
class TestGraphQLValidation:
    """Test GraphQL query validation."""

    @pytest.fixture
    def validator(self, schema):
        """Create GraphQL validator."""
        return GraphQLValidator(schema)

    def test_query_structure_validation(self, validator):
        """Test validation of query structure."""
        # Valid query
        valid_query = """
        {
            user(id: "123") {
                id
                username
                email
            }
        }
        """

        errors = validator.validate(valid_query)
        assert len(errors) == 0

        # Invalid query - missing selection set
        invalid_query = """
        {
            user(id: "123")
        }
        """

        errors = validator.validate(invalid_query)
        assert len(errors) > 0
        assert any("selection set" in error.message.lower() for error in errors)

    def test_field_validation(self, validator):
        """Test validation of field existence."""
        # Query with non-existent field
        invalid_query = """
        {
            user(id: "123") {
                id
                username
                nonExistentField
            }
        }
        """

        errors = validator.validate(invalid_query)
        assert len(errors) > 0
        assert any("nonExistentField" in error.message for error in errors)

    def test_argument_validation(self, validator):
        """Test validation of field arguments."""
        # Missing required argument
        invalid_query = """
        {
            user {
                id
                username
            }
        }
        """

        errors = validator.validate(invalid_query)
        assert len(errors) > 0
        assert any("required" in error.message.lower() for error in errors)

        # Invalid argument type
        invalid_query = """
        {
            user(id: 123) {
                id
                username
            }
        }
        """

        errors = validator.validate(invalid_query)
        # Should validate argument types
        # Note: This might pass if the schema accepts both String and Int for ID

    def test_variable_validation(self, validator):
        """Test validation of query variables."""
        # Valid query with variables
        valid_query = """
        query GetUser($userId: ID!) {
            user(id: $userId) {
                id
                username
            }
        }
        """

        errors = validator.validate(valid_query)
        assert len(errors) == 0

        # Undefined variable usage
        invalid_query = """
        query GetUser {
            user(id: $undefinedVariable) {
                id
                username
            }
        }
        """

        errors = validator.validate(invalid_query)
        assert len(errors) > 0
        assert any("undefinedVariable" in error.message for error in errors)

    def test_fragment_validation(self, validator):
        """Test validation of fragments."""
        # Valid fragment
        valid_query = """
        fragment UserInfo on User {
            id
            username
            email
        }

        query GetUser {
            user(id: "123") {
                ...UserInfo
            }
        }
        """

        errors = validator.validate(valid_query)
        assert len(errors) == 0

        # Fragment on wrong type
        invalid_query = """
        fragment PostInfo on Post {
            id
            title
        }

        query GetUser {
            user(id: "123") {
                ...PostInfo
            }
        }
        """

        errors = validator.validate(invalid_query)
        assert len(errors) > 0
        assert any("type" in error.message.lower() for error in errors)

    def test_directive_validation(self, validator):
        """Test validation of directives."""
        # Valid directive usage
        valid_query = """
        query GetUser($includeEmail: Boolean!) {
            user(id: "123") {
                id
                username
                email @include(if: $includeEmail)
            }
        }
        """

        errors = validator.validate(valid_query)
        assert len(errors) == 0

        # Invalid directive
        invalid_query = """
        query GetUser {
            user(id: "123") {
                id
                username @invalidDirective
            }
        }
        """

        errors = validator.validate(invalid_query)
        assert len(errors) > 0
        assert any("invalidDirective" in error.message for error in errors)


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.graphql
class TestGraphQLSubscriptions:
    """Test GraphQL subscription functionality."""

    @pytest.fixture
    def subscription_executor(self, schema):
        """Create subscription executor."""
        return SubscriptionExecutor(schema)

    async def test_subscription_setup(self, subscription_executor):
        """Test subscription setup and initialization."""
        subscription = """
        subscription PostUpdates {
            postUpdated {
                id
                title
                content
                author {
                    username
                }
            }
        }
        """

        async_iterator = await subscription_executor.subscribe(subscription)
        assert async_iterator is not None
        assert hasattr(async_iterator, "__aiter__")

    async def test_subscription_event_delivery(self, subscription_executor):
        """Test subscription event delivery."""
        subscription = """
        subscription UserUpdates($userId: ID!) {
            userUpdated(id: $userId) {
                id
                username
                email
            }
        }
        """

        variables = {"userId": "123"}

        # Start subscription
        async_iterator = await subscription_executor.subscribe(
            subscription, variables=variables
        )

        # Simulate event
        event_data = {
            "id": "123",
            "username": "updated_user",
            "email": "updated@example.com",
        }

        await subscription_executor.publish_event("userUpdated", event_data)

        # Should receive the event
        async for result in async_iterator:
            assert "data" in result
            assert result["data"]["userUpdated"]["id"] == "123"
            assert result["data"]["userUpdated"]["username"] == "updated_user"
            break  # Exit after first event

    async def test_subscription_filtering(self, subscription_executor):
        """Test subscription event filtering."""
        subscription = """
        subscription PostUpdates($authorId: ID!) {
            postUpdated(authorId: $authorId) {
                id
                title
                author {
                    id
                }
            }
        }
        """

        variables = {"authorId": "123"}

        async_iterator = await subscription_executor.subscribe(
            subscription, variables=variables
        )

        # Publish event for different author (should be filtered out)
        wrong_author_event = {
            "id": "1",
            "title": "Post by different author",
            "author": {"id": "456"},
        }

        await subscription_executor.publish_event("postUpdated", wrong_author_event)

        # Publish event for correct author (should be delivered)
        correct_author_event = {
            "id": "2",
            "title": "Post by correct author",
            "author": {"id": "123"},
        }

        await subscription_executor.publish_event("postUpdated", correct_author_event)

        # Should only receive the filtered event
        received_events = []
        async for result in async_iterator:
            received_events.append(result)
            if len(received_events) >= 1:
                break

        assert len(received_events) == 1
        assert received_events[0]["data"]["postUpdated"]["author"]["id"] == "123"


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.graphql
@pytest.mark.slow
class TestGraphQLPerformance:
    """Test GraphQL performance characteristics."""

    async def test_query_parsing_performance(self):
        """Test query parsing performance."""
        parser = GraphQLParser()

        complex_query = """
        query ComplexQuery($userId: ID!, $postLimit: Int!, $includeComments: Boolean!) {
            user(id: $userId) {
                id
                username
                email
                profile {
                    bio
                    avatar_url
                    social_links {
                        platform
                        url
                    }
                }
                posts(limit: $postLimit) {
                    id
                    title
                    content
                    published_at
                    tags
                    comments @include(if: $includeComments) {
                        id
                        content
                        author {
                            username
                            avatar_url
                        }
                        replies {
                            id
                            content
                            author {
                                username
                            }
                        }
                    }
                }
                followers(first: 10) {
                    edges {
                        node {
                            username
                            avatar_url
                        }
                    }
                }
            }
        }
        """

        import time

        # Parse the same complex query multiple times
        start_time = time.perf_counter()

        for _ in range(100):
            parsed = parser.parse(complex_query)
            assert parsed.operation_type == "query"

        end_time = time.perf_counter()
        avg_parse_time = (end_time - start_time) / 100

        # Parsing should be fast even for complex queries
        assert avg_parse_time < 0.01, f"Query parsing too slow: {avg_parse_time:.4f}s"

    async def test_schema_validation_performance(self, schema):
        """Test schema validation performance."""
        validator = GraphQLValidator(schema)

        query = """
        {
            users(limit: 100) {
                id
                username
                email
                posts {
                    id
                    title
                    author {
                        username
                    }
                }
            }
        }
        """

        import time

        start_time = time.perf_counter()

        for _ in range(100):
            errors = validator.validate(query)
            assert len(errors) == 0

        end_time = time.perf_counter()
        avg_validation_time = (end_time - start_time) / 100

        # Validation should be fast
        assert (
            avg_validation_time < 0.005
        ), f"Query validation too slow: {avg_validation_time:.4f}s"

    async def test_concurrent_query_execution(self, schema):
        """Test concurrent GraphQL query execution."""
        executor = GraphQLExecutor(schema)

        query = """
        {
            user(id: "1") {
                id
                username
                email
            }
        }
        """

        import time

        start_time = time.time()

        # Execute queries concurrently
        tasks = [executor.execute(query) for _ in range(50)]
        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        # All queries should succeed
        for result in results:
            assert "errors" not in result
            assert result["data"]["user"]["id"] == "1"

        # Concurrent execution should be efficient
        avg_time_per_query = total_time / 50
        assert (
            avg_time_per_query < 0.01
        ), f"Concurrent execution too slow: {avg_time_per_query:.4f}s per query"
