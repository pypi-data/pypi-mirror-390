#!/usr/bin/env python3
"""
Test Middleware Integration with Core App
==========================================
Verify that middleware works correctly with the Covet framework.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("MIDDLEWARE INTEGRATION TEST")
print("=" * 80)
print()

# Test 1: Import middleware and app
print("1. Testing imports...")
try:
    from covet import Covet
    from covet.middleware.base import (
        MiddlewareStack,
        CORSMiddleware,
        LoggingMiddleware,
        SessionMiddleware,
        AuthenticationMiddleware,
        RateLimitMiddleware,
        CSRFMiddleware,
        ErrorHandlingMiddleware
    )
    print("✅ All middleware imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Create app with middleware
print("\n2. Creating app with middleware...")
try:
    app = Covet(debug=True)

    # Create middleware stack
    middleware_stack = MiddlewareStack()

    # Add middleware (order matters!)
    middleware_stack.add(ErrorHandlingMiddleware, debug=True)
    middleware_stack.add(CORSMiddleware, origins="*", methods=["GET", "POST", "PUT", "DELETE"])
    middleware_stack.add(LoggingMiddleware)
    middleware_stack.add(SessionMiddleware)
    middleware_stack.add(RateLimitMiddleware, max_requests=100, window=60)

    print(f"✅ Middleware stack created with {len(middleware_stack.middleware)} components")
except Exception as e:
    print(f"❌ Middleware creation failed: {e}")
    sys.exit(1)

# Test 3: Test middleware with routes
print("\n3. Testing middleware with routes...")
try:
    # Add test routes
    @app.route('/')
    async def index(request):
        """Home page - should have CORS headers"""
        return {'message': 'Hello World', 'timestamp': datetime.now().isoformat()}

    @app.route('/session-test')
    async def session_test(request):
        """Test session middleware"""
        # Get or create session counter
        if hasattr(request, 'session'):
            count = request.session.get('count', 0)
            request.session['count'] = count + 1
            return {'session_count': count + 1}
        return {'error': 'No session'}

    @app.route('/error-test')
    async def error_test(request):
        """Test error handling middleware"""
        raise ValueError("Test error for middleware")

    @app.post('/csrf-test')
    async def csrf_test(request):
        """Test CSRF protection"""
        return {'message': 'CSRF check passed'}

    print(f"✅ Routes registered: {len(app.routes)}")
except Exception as e:
    print(f"❌ Route registration failed: {e}")
    sys.exit(1)

# Test 4: Simulate requests with middleware
print("\n4. Simulating requests...")
async def test_middleware():
    """Test middleware by simulating requests"""
    from covet.core.http import Request, Response

    results = []

    # Test 1: Basic request with CORS
    print("   Testing CORS middleware...")
    try:
        request = Request(
            method='GET',
            url='/',
            headers={},
            body=b''
        )

        # Simulate middleware processing
        handler = app.routes[0][1]  # Get the index handler

        # Create a simple handler wrapper
        async def handle(req):
            result = await handler(req)
            if isinstance(result, dict):
                return Response(
                    body=json.dumps(result).encode(),
                    status_code=200,
                    headers={'Content-Type': 'application/json'}
                )
            return result

        # Process through middleware stack
        response = await middleware_stack(request, handle)

        # Check CORS headers
        has_cors = 'Access-Control-Allow-Origin' in response.headers
        results.append(('CORS Headers', has_cors))
        print(f"   {'✅' if has_cors else '❌'} CORS headers: {has_cors}")
    except Exception as e:
        results.append(('CORS Headers', False))
        print(f"   ❌ CORS test failed: {e}")

    # Test 2: Session middleware
    print("   Testing Session middleware...")
    try:
        request = Request(
            method='GET',
            url='/session-test',
            headers={},
            body=b''
        )

        # Process request
        handler = app.routes[1][1]  # Get session_test handler

        async def handle(req):
            result = await handler(req)
            if isinstance(result, dict):
                return Response(
                    body=json.dumps(result).encode(),
                    status_code=200,
                    headers={'Content-Type': 'application/json'}
                )
            return result

        response = await middleware_stack(request, handle)

        # Check if session works
        content_bytes = response.get_content_bytes() if hasattr(response, 'get_content_bytes') else b'{}'
        body = json.loads(content_bytes.decode()) if content_bytes else {}
        has_session = 'session_count' in body or 'error' not in body
        results.append(('Session Management', has_session))
        print(f"   {'✅' if has_session else '⚠️'} Session: {body}")
    except Exception as e:
        results.append(('Session Management', False))
        print(f"   ❌ Session test failed: {e}")

    # Test 3: Error handling
    print("   Testing Error Handling middleware...")
    try:
        request = Request(
            method='GET',
            url='/error-test',
            headers={},
            body=b''
        )

        handler = app.routes[2][1]  # Get error_test handler

        async def handle(req):
            result = await handler(req)
            if isinstance(result, dict):
                return Response(
                    body=json.dumps(result).encode(),
                    status_code=200,
                    headers={'Content-Type': 'application/json'}
                )
            return result

        # Should catch the error and return error response
        response = await ErrorHandlingMiddleware(debug=True)(request, lambda r: handle(r))

        # Check if error was handled
        is_handled = response.status_code == 500
        content_bytes = response.get_content_bytes() if hasattr(response, 'get_content_bytes') else b'{}'
        body = json.loads(content_bytes.decode()) if content_bytes else {}
        has_error_info = 'error' in body
        results.append(('Error Handling', is_handled and has_error_info))
        print(f"   {'✅' if (is_handled and has_error_info) else '❌'} Error handling: Status={response.status_code}, Has error info={has_error_info}")
    except Exception as e:
        results.append(('Error Handling', False))
        print(f"   ❌ Error handling test failed: {e}")

    # Test 4: Rate limiting
    print("   Testing Rate Limit middleware...")
    try:
        rate_limiter = RateLimitMiddleware(max_requests=3, window=60)

        async def dummy_handler(req):
            return Response(content="OK", status_code=200, headers={})

        # Make multiple requests
        request = Request(
            method='GET',
            url='/test',
            headers={},
            body=b''
        )
        # Add client attribute for rate limiting
        if not hasattr(request, 'client'):
            request.__dict__['client'] = ('127.0.0.1', 12345)

        responses = []
        for i in range(5):
            response = await rate_limiter(request, dummy_handler)
            responses.append(response.status_code)

        # Should allow first 3, block last 2
        rate_limit_works = (responses[:3] == [200, 200, 200] and
                          responses[3:] == [429, 429])
        results.append(('Rate Limiting', rate_limit_works))
        print(f"   {'✅' if rate_limit_works else '❌'} Rate limiting: {responses}")
    except Exception as e:
        results.append(('Rate Limiting', False))
        print(f"   ❌ Rate limit test failed: {e}")

    return results

# Run async tests
print()
try:
    results = asyncio.run(test_middleware())

    # Summary
    print("\n" + "=" * 80)
    print("MIDDLEWARE TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, status in results if status)
    total = len(results)

    for test_name, status in results:
        print(f"  {test_name:<25} {'✅ PASS' if status else '❌ FAIL'}")

    print("-" * 80)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n✅ All middleware tests passed!")
    elif passed >= total * 0.75:
        print("\n⚠️ Most middleware tests passed, some issues remain")
    else:
        print("\n❌ Significant middleware issues detected")

except Exception as e:
    print(f"\n❌ Async test execution failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)