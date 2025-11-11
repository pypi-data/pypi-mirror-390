"""
CovetPy Async Example
Demonstrating async/await patterns and advanced features
"""

import asyncio
from covet import Covet, json_response

app = Covet(debug=True)

# Simulated database
fake_db = {
    'users': {
        '1': {'id': '1', 'name': 'Alice', 'email': 'alice@example.com'},
        '2': {'id': '2', 'name': 'Bob', 'email': 'bob@example.com'},
        '3': {'id': '3', 'name': 'Charlie', 'email': 'charlie@example.com'},
    },
    'posts': {
        '1': {'id': '1', 'user_id': '1', 'title': 'First Post', 'body': 'Hello World'},
        '2': {'id': '2', 'user_id': '1', 'title': 'Second Post', 'body': 'Testing'},
        '3': {'id': '3', 'user_id': '2', 'title': 'Bob Post', 'body': 'From Bob'},
    }
}


# Simulate async database query
async def db_query(table, id):
    """Simulate database query with delay"""
    await asyncio.sleep(0.1)  # Simulate I/O
    return fake_db.get(table, {}).get(str(id))


# Simulate async database list
async def db_list(table):
    """Simulate database list with delay"""
    await asyncio.sleep(0.1)  # Simulate I/O
    return list(fake_db.get(table, {}).values())


@app.route('/')
async def index(request):
    """API information"""
    return {
        'name': 'CovetPy Async API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/users',
            'user_detail': '/users/{id}',
            'user_posts': '/users/{id}/posts',
            'posts': '/posts',
            'post_detail': '/posts/{id}'
        }
    }


@app.route('/users')
async def list_users(request):
    """List all users (async)"""
    users = await db_list('users')
    return {
        'count': len(users),
        'users': users
    }


@app.route('/users/{user_id}')
async def get_user(request, user_id):
    """Get user by ID (async)"""
    user = await db_query('users', user_id)

    if not user:
        return json_response(
            {'error': 'User not found'},
            status_code=404
        )

    return {'user': user}


@app.route('/users/{user_id}/posts')
async def get_user_posts(request, user_id):
    """Get all posts for a user (async with multiple queries)"""
    # First, get the user
    user = await db_query('users', user_id)

    if not user:
        return json_response(
            {'error': 'User not found'},
            status_code=404
        )

    # Then get all posts
    all_posts = await db_list('posts')

    # Filter posts by user_id
    user_posts = [p for p in all_posts if p['user_id'] == user_id]

    return {
        'user': user,
        'post_count': len(user_posts),
        'posts': user_posts
    }


@app.route('/posts')
async def list_posts(request):
    """List all posts (async)"""
    posts = await db_list('posts')
    return {
        'count': len(posts),
        'posts': posts
    }


@app.route('/posts/{post_id}')
async def get_post(request, post_id):
    """Get post with author info (concurrent async queries)"""
    # Get post
    post = await db_query('posts', post_id)

    if not post:
        return json_response(
            {'error': 'Post not found'},
            status_code=404
        )

    # Get author info
    user = await db_query('users', post['user_id'])

    return {
        'post': post,
        'author': user
    }


@app.route('/users/{user_id}/stats')
async def get_user_stats(request, user_id):
    """Get user statistics (parallel async operations)"""
    # Run multiple async operations concurrently
    user_task = db_query('users', user_id)
    posts_task = db_list('posts')

    # Wait for both to complete
    user, all_posts = await asyncio.gather(user_task, posts_task)

    if not user:
        return json_response(
            {'error': 'User not found'},
            status_code=404
        )

    user_posts = [p for p in all_posts if p['user_id'] == user_id]

    return {
        'user': user,
        'stats': {
            'total_posts': len(user_posts),
            'total_words': sum(len(p['body'].split()) for p in user_posts)
        }
    }


@app.post('/users')
async def create_user(request):
    """Create a new user (async)"""
    try:
        data = await request.json()

        # Validate
        if 'name' not in data or 'email' not in data:
            return json_response(
                {'error': 'Missing required fields: name, email'},
                status_code=400
            )

        # Simulate async save
        await asyncio.sleep(0.1)

        new_id = str(len(fake_db['users']) + 1)
        new_user = {
            'id': new_id,
            'name': data['name'],
            'email': data['email']
        }

        fake_db['users'][new_id] = new_user

        return json_response(
            {'success': True, 'user': new_user},
            status_code=201
        )

    except Exception as e:
        return json_response(
            {'error': str(e)},
            status_code=500
        )


@app.route('/slow')
async def slow_endpoint(request):
    """Demonstrate long-running async operation"""
    # Simulate long operation
    await asyncio.sleep(2)

    return {
        'message': 'This took 2 seconds',
        'status': 'complete'
    }


# Startup event
@app.on_event('startup')
async def startup():
    print("\nAsync API Starting...")
    print(f"Loaded {len(fake_db['users'])} users")
    print(f"Loaded {len(fake_db['posts'])} posts")


if __name__ == '__main__':
    print("\nCovetPy Async Example")
    print("=" * 50)
    print("\nThis example demonstrates:")
    print("  - Async route handlers")
    print("  - Async database queries")
    print("  - Concurrent operations with asyncio.gather")
    print("  - Path parameters")
    print("  - JSON request/response")
    print("  - Error handling")
    print("\nTry these endpoints:")
    print("  GET  /users           - List all users")
    print("  GET  /users/1         - Get user #1")
    print("  GET  /users/1/posts   - Get user's posts")
    print("  GET  /users/1/stats   - Get user stats")
    print("  GET  /posts           - List all posts")
    print("  GET  /posts/1         - Get post #1")
    print("  POST /users           - Create user")
    print("  GET  /slow            - Slow endpoint (2s)")
    print("\nStarting server on http://127.0.0.1:8000\n")

    app.run(host='127.0.0.1', port=8000)
