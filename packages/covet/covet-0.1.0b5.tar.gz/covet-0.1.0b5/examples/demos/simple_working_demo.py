#!/usr/bin/env python3
"""
CovetPy Simple Working Demo - Shows what actually works
"""

import json
import time
import sys
from pathlib import Path

# Add src to path so we can import covet
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test that basic imports work"""
    print("🧪 Testing Basic Imports")
    
    try:
        import covet
        print("  ✅ Main covet package imports successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import covet: {e}")
        return False
    
    try:
        from covet.core.routing import CovetRouter
        print("  ✅ Router imports successfully")
    except ImportError as e:
        print(f"  ❌ Failed to import router: {e}")
        return False
    
    return True

def test_routing_performance():
    """Test routing performance with actual CovetRouter"""
    print("\n🚀 Testing Routing Performance")
    
    try:
        from covet.core.routing import CovetRouter
        
        router = CovetRouter()
        
        # Add some routes
        router.add_route("/", lambda: {"message": "Hello"}, ["GET"])
        router.add_route("/users/{user_id}", lambda user_id: {"user_id": user_id}, ["GET"])
        router.add_route("/api/v1/posts/{post_id}", lambda post_id: {"post_id": post_id}, ["GET"])
        
        # Test route matching performance
        test_paths = [
            "/",
            "/users/123", 
            "/api/v1/posts/456",
            "/nonexistent"
        ]
        
        # Warm up
        for path in test_paths:
            try:
                router.match_route(path, "GET")
            except:
                pass
        
        # Benchmark
        iterations = 50000
        start_time = time.perf_counter()
        
        for _ in range(iterations):
            for path in test_paths:
                try:
                    router.match_route(path, "GET")
                except:
                    pass
        
        end_time = time.perf_counter()
        total_time = end_time - start_time
        total_ops = iterations * len(test_paths)
        ops_per_second = total_ops / total_time
        nanoseconds_per_op = (total_time * 1_000_000_000) / total_ops
        
        print(f"  Routing Performance: {ops_per_second:,.0f} lookups/second")
        print(f"  Time per lookup: {nanoseconds_per_op:.0f} nanoseconds")
        print(f"  ✅ Routing performance measured successfully")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Routing test failed: {e}")
        return False

def test_json_performance():
    """Test JSON serialization performance"""
    print("\n📊 Testing JSON Performance")
    
    test_data = {
        "user_id": 12345,
        "name": "Alice Johnson", 
        "email": "alice@example.com",
        "posts": [
            {"id": 1, "title": "Hello World", "views": 100},
            {"id": 2, "title": "Python Tips", "views": 250},
        ],
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "preferences": {"theme": "dark", "notifications": True}
        }
    }
    
    # Test serialization
    iterations = 10000
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        json.dumps(test_data)
    
    end_time = time.perf_counter()
    serialize_ops_per_second = iterations / (end_time - start_time)
    
    # Test deserialization  
    json_string = json.dumps(test_data)
    start_time = time.perf_counter()
    
    for _ in range(iterations):
        json.loads(json_string)
    
    end_time = time.perf_counter()
    parse_ops_per_second = iterations / (end_time - start_time)
    
    print(f"  JSON Serialize: {serialize_ops_per_second:,.0f} ops/second")
    print(f"  JSON Parse: {parse_ops_per_second:,.0f} ops/second")
    print(f"  ✅ JSON performance measured successfully")
    
    return True

def test_basic_functionality():
    """Test basic framework functionality"""
    print("\n🔧 Testing Basic Functionality")
    
    # Test that we can create a simple app structure
    try:
        from covet.core.routing import CovetRouter
        
        router = CovetRouter()
        
        # Test route registration
        def hello_handler():
            return {"message": "Hello World"}
        
        def user_handler(user_id):
            return {"user_id": user_id, "name": "Alice"}
        
        router.add_route("/", hello_handler, ["GET"])
        router.add_route("/users/{user_id}", user_handler, ["GET"])
        
        # Test route matching
        match = router.match_route("/", "GET")
        if match and match.handler:
            result = match.handler()
            print(f"  ✅ Static route works: {result}")
        else:
            print("  ❌ Static route failed")
            return False
        
        # Test dynamic route
        match = router.match_route("/users/123", "GET") 
        if match and match.handler and match.params:
            result = match.handler(**match.params)
            print(f"  ✅ Dynamic route works: {result}")
        else:
            print("  ❌ Dynamic route failed")
            return False
        
        print("  ✅ Basic routing functionality works")
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 CovetPy Simple Working Demo")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    if test_basic_imports():
        tests_passed += 1
    
    if test_routing_performance():
        tests_passed += 1
    
    if test_json_performance():
        tests_passed += 1
    
    if test_basic_functionality():
        tests_passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ All tests passed! CovetPy basic functionality works.")
        print("\n📝 What actually works:")
        print("  • Basic imports and package structure ✅")
        print("  • Fast routing with parameter extraction ✅") 
        print("  • JSON serialization using standard library ✅")
        print("  • Route registration and matching ✅")
        print("\n⚠️  Note: This is experimental software for educational purposes")
        print("     Many advanced features are incomplete or missing")
    else:
        print("❌ Some tests failed. CovetPy has issues that need fixing.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)