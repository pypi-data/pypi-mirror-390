#!/usr/bin/env python3
"""
Quick integration test for CovetPy Core Framework components
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from covet.core.asgi import CovetPyASGI
from covet.core.routing import CovetRouter
from covet.core.http_objects import Request, Response, json_response


async def test_basic_routing():
    """Test basic routing works"""
    router = CovetRouter()

    # Add test routes
    async def hello_handler(request):
        return Response(content={"message": "Hello World"})

    async def user_handler(request):
        user_id = request.path_params.get('user_id')
        return Response(content={"user_id": user_id})

    router.add_route("/", hello_handler, ["GET"])
    router.add_route("/users/{user_id}", user_handler, ["GET"])

    # Test static route matching
    match = router.match_route("/", "GET")
    assert match is not None, "Failed to match static route"
    assert match.handler == hello_handler
    assert match.params == {}

    # Test dynamic route matching
    match = router.match_route("/users/123", "GET")
    assert match is not None, "Failed to match dynamic route"
    assert match.handler == user_handler
    assert match.params == {"user_id": 123}

    print("✓ Routing tests passed")
    return True


async def test_http_objects():
    """Test Request and Response objects"""
    # Test Request
    request = Request(
        method="POST",
        url="/api/users?page=1&limit=10",
        headers={"Content-Type": "application/json", "Authorization": "Bearer token"},
        body=b'{"name": "John"}',
        query_string="page=1&limit=10"
    )

    assert request.method == "POST"
    assert request.path == "/api/users"
    assert request.query_params.get("page") == "1"
    assert request.query_params.get("limit") == "10"
    assert request.headers.get("content-type") == "application/json"

    # Test body parsing
    json_data = await request.json()
    assert json_data == {"name": "John"}

    # Test Response
    response = Response(
        content={"status": "success", "data": {"id": 1}},
        status_code=201
    )

    assert response.status_code == 201
    assert response.media_type == "application/json"
    assert response.is_success()

    # Test response body
    body = response.get_body_bytes()
    assert b'"status"' in body
    assert b'"success"' in body

    print("✓ HTTP objects tests passed")
    return True


async def test_asgi_integration():
    """Test ASGI application integration"""
    router = CovetRouter()

    async def test_handler(request):
        return json_response({"test": "works"})

    router.add_route("/test", test_handler, ["GET"])

    # Create ASGI app
    app = CovetPyASGI(router=router)

    # Simulate ASGI request
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "method": "GET",
        "path": "/test",
        "query_string": b"",
        "headers": [],
        "scheme": "http",
        "server": ("localhost", 8000),
    }

    received_messages = []

    async def receive():
        return {"type": "http.request", "body": b""}

    async def send(message):
        received_messages.append(message)

    # Call ASGI app
    await app(scope, receive, send)

    # Verify response
    assert len(received_messages) == 2, f"Expected 2 messages, got {len(received_messages)}"
    assert received_messages[0]["type"] == "http.response.start"
    assert received_messages[0]["status"] == 200
    assert received_messages[1]["type"] == "http.response.body"
    assert b'"test"' in received_messages[1]["body"]
    assert b'"works"' in received_messages[1]["body"]

    print("✓ ASGI integration tests passed")
    return True


async def test_middleware():
    """Test middleware system"""
    from covet.core.builtin_middleware import RequestIDMiddleware, CORSMiddleware

    # Create middleware instances
    request_id_mw = RequestIDMiddleware()
    cors_mw = CORSMiddleware(allow_origins=["*"])

    # Test RequestIDMiddleware
    request = Request(method="GET", url="/test")
    result = await request_id_mw.process_request(request)
    assert hasattr(result, 'request_id'), "Request ID not added"
    assert result.request_id is not None

    # Test CORS preflight
    options_request = Request(
        method="OPTIONS",
        url="/api/test",
        headers={"Origin": "http://example.com"}
    )
    cors_result = await cors_mw.process_request(options_request)
    assert isinstance(cors_result, Response), "CORS didn't return response for OPTIONS"
    assert cors_result.status_code == 200

    print("✓ Middleware tests passed")
    return True


async def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("CovetPy Core Framework Integration Tests")
    print("="*60 + "\n")

    tests = [
        ("Routing System", test_basic_routing),
        ("HTTP Objects", test_http_objects),
        ("ASGI Integration", test_asgi_integration),
        ("Middleware System", test_middleware),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"Testing {name}...")
        try:
            result = await test_func()
            if result:
                passed += 1
            else:
                failed += 1
                print(f"✗ {name} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
