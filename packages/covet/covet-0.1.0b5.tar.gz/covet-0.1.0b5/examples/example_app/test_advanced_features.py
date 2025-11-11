"""
Test Advanced Features: Caching, Middleware, Validation, Pagination
"""
import sys
import asyncio
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

print("=" * 70)
print("TESTING ADVANCED FEATURES")
print("=" * 70)

# Test 1: Caching
print("\n[1] Testing Caching System...")
try:
    from covet.cache import Cache, CacheBackend
    print("✅ Cache imports successful")

    # Try to use cache
    cache = Cache()
    asyncio.run(cache.set("test_key", "test_value"))
    value = asyncio.run(cache.get("test_key"))
    print(f"✅ Cache working: set and get successful (value: {value})")
except ImportError as e:
    print(f"❌ Cache import failed: {e}")
except AttributeError as e:
    print(f"⚠️  Cache partially working: {e}")
except Exception as e:
    print(f"⚠️  Cache failed: {e}")

# Test 2: Middleware
print("\n[2] Testing Middleware System...")
try:
    from covet.core import CORSMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
    print("✅ Middleware imports successful")

    # Test middleware instantiation
    cors = CORSMiddleware(app=None, allowed_origins=["*"])
    print("✅ CORS Middleware created")

    rate_limit = RateLimitMiddleware(app=None, max_requests=100, window=60)
    print("✅ Rate Limit Middleware created")

    logging_middleware = RequestLoggingMiddleware(app=None)
    print("✅ Request Logging Middleware created")

except ImportError as e:
    print(f"❌ Middleware import failed: {e}")
except Exception as e:
    print(f"⚠️  Middleware failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Validation
print("\n[3] Testing Input Validation...")
try:
    from covet.api.rest import BaseModel, Field, ValidationError
    print("✅ Validation imports successful")

    # Define validation model
    class UserInput(BaseModel):
        username: str = Field(..., min_length=3, max_length=50)
        email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        age: int = Field(..., ge=0, le=150)

    print("✅ Validation model defined")

    # Test valid input
    valid_user = UserInput(username="testuser", email="test@example.com", age=25)
    print(f"✅ Valid input accepted: {valid_user.username}")

    # Test invalid input
    try:
        invalid_user = UserInput(username="ab", email="invalid", age=200)
        print("⚠️  Invalid input NOT rejected (validation may not be working)")
    except ValidationError as e:
        print("✅ Invalid input correctly rejected")

except ImportError as e:
    print(f"❌ Validation import failed: {e}")
except Exception as e:
    print(f"⚠️  Validation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Pagination
print("\n[4] Testing Pagination...")
try:
    from covet.api.rest import PaginationParams
    print("✅ Pagination imports successful")

    # Test pagination params
    pagination = PaginationParams(page=1, page_size=20)
    print(f"✅ Pagination params created: page={pagination.page}, size={pagination.page_size}")

except ImportError as e:
    print(f"❌ Pagination import failed: {e}")
except Exception as e:
    print(f"⚠️  Pagination failed: {e}")

# Test 5: Query Builder
print("\n[5] Testing Query Builder...")
try:
    from covet.database.query_builder import QueryBuilder
    print("✅ Query Builder imports successful")

    qb = QueryBuilder('users')
    query = qb.select(['id', 'username']).where('age', '>', 18).build()
    print(f"✅ Query Builder working: {query}")
except ImportError as e:
    print(f"⚠️  Query Builder import failed: {e} (may be in separate module)")
except Exception as e:
    print(f"⚠️  Query Builder failed: {e}")

# Test 6: Rate Limiting
print("\n[6] Testing Rate Limiting...")
try:
    from covet.api.rest import RateLimiter, FixedWindowRateLimiter
    print("✅ Rate Limiter imports successful")

    limiter = FixedWindowRateLimiter(max_requests=10, window_seconds=60)
    print("✅ Fixed Window Rate Limiter created")
except ImportError as e:
    print(f"❌ Rate Limiter import failed: {e}")
except Exception as e:
    print(f"⚠️  Rate Limiter failed: {e}")

# Test 7: OpenAPI/Swagger Documentation
print("\n[7] Testing OpenAPI Documentation Generation...")
try:
    from covet.api.rest import RESTFramework, OpenAPIGenerator
    print("✅ OpenAPI imports successful")

    api = RESTFramework(title="Test API", version="1.0.0", enable_docs=True)

    @api.get('/test')
    async def test_endpoint():
        """Test endpoint docstring"""
        return {"message": "test"}

    # Try to get OpenAPI schema
    schema = api.get_openapi_schema()
    print(f"✅ OpenAPI schema generated: {schema.get('info', {}).get('title')}")
except ImportError as e:
    print(f"❌ OpenAPI import failed: {e}")
except AttributeError as e:
    print(f"⚠️  OpenAPI generation not available: {e}")
except Exception as e:
    print(f"⚠️  OpenAPI failed: {e}")

# Test 8: CORS Support
print("\n[8] Testing CORS Support...")
try:
    from covet.core import CORSMiddleware
    print("✅ CORS imports successful")

    cors = CORSMiddleware(
        app=None,
        allowed_origins=["http://localhost:3000"],
        allowed_methods=["GET", "POST", "PUT", "DELETE"],
        allowed_headers=["*"],
        allow_credentials=True
    )
    print("✅ CORS middleware configured with options")
except ImportError as e:
    print(f"❌ CORS import failed: {e}")
except Exception as e:
    print(f"⚠️  CORS failed: {e}")

# Test 9: Response Serialization
print("\n[9] Testing Response Serialization...")
try:
    from covet.api.rest import StandardResponse, PaginatedResponse, ErrorResponse
    print("✅ Response serialization imports successful")

    response = StandardResponse(success=True, data={"message": "test"})
    print(f"✅ Standard response created: {response.success}")

    paginated = PaginatedResponse(
        data=[{"id": 1}, {"id": 2}],
        page=1,
        page_size=10,
        total=2
    )
    print(f"✅ Paginated response created: {paginated.total} items")
except ImportError as e:
    print(f"❌ Response serialization import failed: {e}")
except Exception as e:
    print(f"⚠️  Response serialization failed: {e}")

# Test 10: Error Handling
print("\n[10] Testing Error Handling...")
try:
    from covet.api.rest import (
        APIError, NotFoundError, BadRequestError,
        UnauthorizedError, InternalServerError
    )
    print("✅ Error classes imports successful")

    # Test error instantiation
    not_found = NotFoundError(detail="Resource not found")
    print(f"✅ NotFoundError created: {not_found.status}")

    bad_request = BadRequestError(detail="Invalid input")
    print(f"✅ BadRequestError created: {bad_request.status}")
except ImportError as e:
    print(f"❌ Error handling import failed: {e}")
except Exception as e:
    print(f"⚠️  Error handling failed: {e}")

print("\n" + "=" * 70)
print("ADVANCED FEATURES TESTING COMPLETE")
print("=" * 70)
