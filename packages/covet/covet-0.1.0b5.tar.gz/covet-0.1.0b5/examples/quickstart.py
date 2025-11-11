"""
CovetPy Quickstart Example
A simple Flask-like API demonstrating the core features
"""

from covet import Covet

# Create application
app = Covet(debug=True)


# Simple route
@app.route('/')
async def index(request):
    """Welcome endpoint"""
    return {
        'message': 'Welcome to CovetPy!',
        'docs': '/docs',
        'version': '1.0.0'
    }


# Route with path parameter
@app.route('/users/{user_id}')
async def get_user(request, user_id):
    """Get user by ID"""
    return {
        'user_id': user_id,
        'name': f'User {user_id}',
        'email': f'user{user_id}@example.com'
    }


# Multiple path parameters
@app.route('/posts/{post_id}/comments/{comment_id}')
async def get_comment(request, post_id, comment_id):
    """Get comment on a post"""
    return {
        'post_id': post_id,
        'comment_id': comment_id,
        'text': f'Comment {comment_id} on post {post_id}'
    }


# POST endpoint
@app.post('/users')
async def create_user(request):
    """Create a new user"""
    try:
        data = await request.json()
        return {
            'success': True,
            'user': data,
            'id': 123
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


# Query parameters
@app.route('/search')
async def search(request):
    """Search with query parameters"""
    query = request.query.get('q', '')
    limit = request.query.get('limit', '10')

    return {
        'query': query,
        'limit': limit,
        'results': [
            {'id': 1, 'title': f'Result for {query}'},
            {'id': 2, 'title': f'Another result for {query}'}
        ]
    }


# Return plain text
@app.route('/health')
async def health(request):
    """Health check endpoint"""
    return 'OK'


# Return HTML
@app.route('/hello')
async def hello(request):
    """HTML response"""
    from covet import html_response
    return html_response("""
    <html>
        <body>
            <h1>Hello from CovetPy!</h1>
            <p>This is HTML content</p>
        </body>
    </html>
    """)


# Startup event
@app.on_event('startup')
async def startup():
    """Run on application startup"""
    print("Application is starting...")
    print("Database connected")


# Shutdown event
@app.on_event('shutdown')
async def shutdown():
    """Run on application shutdown"""
    print("Application is shutting down...")
    print("Database disconnected")


# Run the application
if __name__ == '__main__':
    print("\nCovetPy Quickstart Example")
    print("=" * 50)
    print("\nAvailable endpoints:")
    print("  GET  /                    - Welcome message")
    print("  GET  /users/{user_id}     - Get user by ID")
    print("  GET  /posts/{post_id}/comments/{comment_id}")
    print("  POST /users               - Create user")
    print("  GET  /search?q=...        - Search")
    print("  GET  /health              - Health check")
    print("  GET  /hello               - HTML response")
    print("\nStarting server on http://127.0.0.1:8000")
    print("Press CTRL+C to stop\n")

    app.run(host='127.0.0.1', port=8000)
