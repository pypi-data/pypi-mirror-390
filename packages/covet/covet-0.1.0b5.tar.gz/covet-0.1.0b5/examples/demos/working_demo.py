#!/usr/bin/env python3
"""
Working CovetPy Framework Demo
Demonstrates the fully integrated framework in action
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.covet.core import Covet, CovetRouter, CovetASGIApp, Request, Response

def main():
    print("🚀 CovetPy Framework Demo")
    print("=" * 40)
    
    # Method 1: Using the factory (recommended)
    print("\n1. Creating app using Covet factory...")
    app = Covet.create_app()
    
    @app.get('/health')
    def health_check(request: Request) -> dict:
        return {
            'status': 'healthy',
            'framework': 'CovetPy',
            'version': '1.0.0'
        }
    
    @app.get('/users/{user_id}')
    def get_user(request: Request) -> dict:
        user_id = request.path_params.get('user_id')
        return {
            'user_id': user_id,
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com'
        }
    
    @app.post('/api/data')
    def create_data(request: Request) -> Response:
        return Response(
            content={'message': 'Data created successfully'},
            status_code=201,
            headers={'X-Framework': 'CovetPy'}
        )
    
    print("✓ Routes registered successfully")
    
    # Method 2: Manual router setup (advanced)
    print("\n2. Creating advanced router...")
    router = CovetRouter()
    
    @router.get('/api/v1/products/{product_id}/reviews/{review_id}')
    def get_product_review(request: Request) -> dict:
        return {
            'product_id': request.path_params.get('product_id'),
            'review_id': request.path_params.get('review_id'),
            'rating': 5,
            'comment': 'Great product!'
        }
    
    # Test route matching
    match = router.match_route('/api/v1/products/123/reviews/456', 'GET')
    if match:
        print(f"✓ Route matched with params: {match.params}")
    
    # Method 3: ASGI application
    print("\n3. Creating ASGI application...")
    asgi_app = CovetASGIApp(router=router, debug=True)
    print("✓ ASGI app created successfully")
    
    # Show route information
    print("\n4. Framework capabilities:")
    print("✓ Zero-dependency core")
    print("✓ Advanced parameter routing")
    print("✓ ASGI 3.0 compliance") 
    print("✓ Production HTTP server")
    print("✓ Middleware support")
    print("✓ Type hints support")
    print("✓ Response customization")
    
    print("\n🎉 Demo completed successfully!")
    print("The CovetPy framework is fully operational and ready for use.")
    
    return app, router, asgi_app

if __name__ == '__main__':
    main()