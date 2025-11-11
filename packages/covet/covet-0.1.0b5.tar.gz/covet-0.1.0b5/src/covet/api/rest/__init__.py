"""
CovetPy REST API Framework

Production-ready REST API framework with comprehensive features:
- Request validation with Pydantic
- Response serialization and content negotiation
- RFC 7807 error handling
- OpenAPI 3.1 automatic documentation
- API versioning (URL, header, query param)
- Rate limiting with multiple algorithms
- ASGI middleware integration

Example:
    from covet.api.rest import RESTFramework, BaseModel, Field

    api = RESTFramework(
        title="My API",
        version="1.0.0",
        enable_docs=True
    )

    class UserCreate(BaseModel):
        name: str = Field(..., min_length=1, max_length=100)
        email: str

    @api.post("/users", request_model=UserCreate)
    async def create_user(user: UserCreate):
        # Your logic here
        return {"id": 1, "name": user.name, "email": user.email}

Features:
- NO MOCK DATA: Real Pydantic validation
- Production-ready error handling
- Automatic OpenAPI generation
- Swagger UI and ReDoc included
"""

# Error handling
from .errors import (
    APIError,
    BadRequestError,
    ConflictError,
    ErrorHandler,
    ErrorMiddleware,
    ForbiddenError,
    InternalServerError,
    MethodNotAllowedError,
    NotFoundError,
    ProblemDetail,
    ServiceUnavailableError,
    TooManyRequestsError,
    UnauthorizedError,
)

# Core framework
from .framework import RESTFramework

# OpenAPI
from .openapi import (
    OpenAPIGenerator,
    ReDocConfig,
    SwaggerUIConfig,
)

# Rate limiting
from .ratelimit import (
    FixedWindowRateLimiter,
    RateLimitAlgorithm,
    RateLimiter,
    RateLimitExceeded,
    RateLimitMiddleware,
    SlidingWindowRateLimiter,
    TokenBucketRateLimiter,
)

# Serialization
from .serialization import (
    ContentNegotiator,
    CreatedResponse,
    ErrorResponse,
    NoContentResponse,
    PaginatedResponse,
    ResponseFormatter,
    ResponseSerializer,
    SerializationError,
    StandardResponse,
    SuccessResponse,
)

# Validation
from .validation import (
    BaseModel,
    Field,
    FilterParams,
    IDPathParam,
    PaginationParams,
    PydanticValidator,
    RequestValidator,
    SortParams,
    StandardQueryParams,
    UUIDPathParam,
    ValidationError,
    ValidationErrorDetail,
    ValidationErrorResponse,
    validator,
)

# Versioning
from .versioning import (
    APIVersion,
    VersioningStrategy,
    VersionNegotiator,
    VersionRouter,
)

__all__ = [
    # Core framework
    "RESTFramework",
    # Validation
    "RequestValidator",
    "PydanticValidator",
    "ValidationError",
    "ValidationErrorDetail",
    "ValidationErrorResponse",
    "PaginationParams",
    "SortParams",
    "FilterParams",
    "StandardQueryParams",
    "IDPathParam",
    "UUIDPathParam",
    "BaseModel",
    "Field",
    "validator",
    # Serialization
    "ResponseSerializer",
    "ResponseFormatter",
    "ContentNegotiator",
    "SerializationError",
    "StandardResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "CreatedResponse",
    "NoContentResponse",
    # Error handling
    "ProblemDetail",
    "APIError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "MethodNotAllowedError",
    "ConflictError",
    "TooManyRequestsError",
    "InternalServerError",
    "ServiceUnavailableError",
    "ErrorHandler",
    "ErrorMiddleware",
    # OpenAPI
    "OpenAPIGenerator",
    "SwaggerUIConfig",
    "ReDocConfig",
    # Versioning
    "VersioningStrategy",
    "APIVersion",
    "VersionNegotiator",
    "VersionRouter",
    # Rate limiting
    "RateLimitAlgorithm",
    "RateLimitExceeded",
    "RateLimiter",
    "FixedWindowRateLimiter",
    "SlidingWindowRateLimiter",
    "TokenBucketRateLimiter",
    "RateLimitMiddleware",
]
