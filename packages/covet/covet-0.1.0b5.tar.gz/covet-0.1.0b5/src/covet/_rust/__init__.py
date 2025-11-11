"""
Python integration layer for Rust extensions with fallback to pure Python.
"""

import hashlib
import json
import re
import sys
import time
import warnings
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import parse_qs, urlencode, urlparse

# Try to import Rust extensions
try:
    from covet_rust import (
        FastArgon2Hasher,
        FastBcryptHasher,
        FastBlake3Hasher,
        FastJsonDecoder,
        FastJsonEncoder,
        FastJwtDecoder,
        FastJwtEncoder,
        FastRouter,
        FixedWindowLimiter,
        LeakyBucketLimiter,
        SlidingWindowLimiter,
        TokenBucketLimiter,
    )
    from covet_rust import create_composite_limiter as rust_create_composite_limiter
    from covet_rust import encode_query_string as rust_encode_query_string
    from covet_rust import generate_jwt_secret as rust_generate_jwt_secret
    from covet_rust import generate_salt as rust_generate_salt
    from covet_rust import generate_token as rust_generate_token
    from covet_rust import get_jwt_header as rust_get_jwt_header
    from covet_rust import hash_password as rust_hash_password
    from covet_rust import json_extract as rust_json_extract
    from covet_rust import json_merge as rust_json_merge
    from covet_rust import minify_json as rust_minify_json
    from covet_rust import parse_query_string as rust_parse_query_string
    from covet_rust import parse_url as rust_parse_url
    from covet_rust import prettify_json as rust_prettify_json
    from covet_rust import quick_hash as rust_quick_hash
    from covet_rust import (
        validate_json as rust_validate_json,  # JSON; JWT; Hashing; Rate Limiting; Routing
    )
    from covet_rust import verify_password as rust_verify_password

    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    warnings.warn(
        "Rust extensions not available. Falling back to pure Python implementation. "
        "Install with: cd rust_extensions && maturin develop --release",
        RuntimeWarning,
    )


# Pure Python fallbacks

if not RUST_AVAILABLE:

    # JSON Fallbacks
    class FastJsonEncoder:
        def __init__(self, pretty=False, sort_keys=False, compact=True):
            self.pretty = pretty
            self.sort_keys = sort_keys
            self.compact = compact

        def encode(self, obj):
            if self.pretty:
                return json.dumps(obj, indent=2, sort_keys=self.sort_keys)
            elif self.compact:
                return json.dumps(obj, separators=(",", ":"), sort_keys=self.sort_keys)
            else:
                return json.dumps(obj, sort_keys=self.sort_keys)

        def encode_bytes(self, obj):
            return self.encode(obj).encode("utf-8")

        def encode_batch(self, objects):
            return [self.encode(obj) for obj in objects]

    class FastJsonDecoder:
        def __init__(self, strict=True, allow_nan=False):
            self.strict = strict
            self.allow_nan = allow_nan

        def decode(self, json_str):
            return json.loads(json_str, strict=self.strict)

        def decode_bytes(self, json_bytes):
            return json.loads(json_bytes.decode("utf-8"), strict=self.strict)

        def decode_batch(self, json_strings):
            return [self.decode(s) for s in json_strings]

        def decode_stream(self, json_str):
            data = json.loads(json_str)
            if not isinstance(data, list):
                raise TypeError("Expected JSON array for stream decoding")
            return data

    def rust_validate_json(json_str):
        try:
            json.loads(json_str)
            return True
        except (json.JSONDecodeError, ValueError):
            return False

    def rust_minify_json(json_str):
        return json.dumps(json.loads(json_str), separators=(",", ":"))

    def rust_prettify_json(json_str):
        return json.dumps(json.loads(json_str), indent=2)

    def rust_json_extract(json_str, path):
        data = json.loads(json_str)
        parts = path.split(".")

        for part in parts:
            if part.startswith("[") and part.endswith("]"):
                idx = int(part[1:-1])
                if isinstance(data, list) and idx < len(data):
                    data = data[idx]
                else:
                    return None
            else:
                if isinstance(data, dict) and part in data:
                    data = data[part]
                else:
                    return None

        return json.dumps(data) if data is not None else None

    def rust_json_merge(json1, json2, deep=False):
        data1 = json.loads(json1)
        data2 = json.loads(json2)

        if deep and isinstance(data1, dict) and isinstance(data2, dict):

            def deep_merge(base, other):
                for key, value in other.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        deep_merge(base[key], value)
                    else:
                        base[key] = value

            deep_merge(data1, data2)
        elif isinstance(data1, dict) and isinstance(data2, dict):
            data1.update(data2)

        return json.dumps(data1)

    # JWT Fallbacks (simplified - use PyJWT in production)
    import base64
    import hmac
    import secrets

    class FastJwtEncoder:
        def __init__(self, secret, algorithm="HS256", issuer=None, audience=None, expires_in=None):
            self.secret = secret
            self.algorithm = algorithm
            self.issuer = issuer
            self.audience = audience
            self.expires_in = expires_in

        def encode(self, claims):
            # Simplified JWT encoding (HS256 only for fallback)
            import time

            if self.issuer:
                claims["iss"] = self.issuer
            if self.audience:
                claims["aud"] = self.audience
            if self.expires_in:
                claims["exp"] = int(time.time()) + self.expires_in
            if "iat" not in claims:
                claims["iat"] = int(time.time())

            header = {"alg": self.algorithm, "typ": "JWT"}

            header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()

            payload_b64 = (
                base64.urlsafe_b64encode(json.dumps(claims).encode()).rstrip(b"=").decode()
            )

            message = f"{header_b64}.{payload_b64}"

            if self.algorithm == "HS256":
                signature = (
                    base64.urlsafe_b64encode(
                        hmac.new(self.secret, message.encode(), hashlib.sha256).digest()
                    )
                    .rstrip(b"=")
                    .decode()
                )
            else:
                raise NotImplementedError(f"Algorithm {self.algorithm} not supported in fallback")

            return f"{message}.{signature}"

        def encode_batch(self, claims_list):
            return [self.encode(claims) for claims in claims_list]

        def generate_refresh_token(self, user_id, expires_in=None):
            expires_in = expires_in or 86400 * 30
            claims = {
                "sub": user_id,
                "type": "refresh",
                "exp": int(time.time()) + expires_in,
            }
            return self.encode(claims)

    class FastJwtDecoder:
        def __init__(
            self,
            secret,
            algorithm="HS256",
            validate_exp=True,
            validate_nbf=True,
            issuer=None,
            audience=None,
            cache_enabled=True,
        ):
            self.secret = secret
            self.algorithm = algorithm
            self.validate_exp = validate_exp
            self.issuer = issuer
            self.audience = audience
            self._cache = {} if cache_enabled else None

        def decode(self, token):
            # Check cache
            if self._cache is not None and token in self._cache:
                claims, exp_time = self._cache[token]
                if time.time() < exp_time:
                    return claims

            # Simplified JWT decoding (HS256 only for fallback)
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            header_b64, payload_b64, signature_b64 = parts

            # Decode payload
            payload = base64.urlsafe_b64decode(payload_b64 + "=" * (4 - len(payload_b64) % 4))
            claims = json.loads(payload)

            # Verify signature (simplified)
            if self.algorithm == "HS256":
                expected_signature = (
                    base64.urlsafe_b64encode(
                        hmac.new(
                            self.secret,
                            f"{header_b64}.{payload_b64}".encode(),
                            hashlib.sha256,
                        ).digest()
                    )
                    .rstrip(b"=")
                    .decode()
                )

                if signature_b64 != expected_signature:
                    raise PermissionError("Invalid JWT signature")

            # Validate claims
            if self.validate_exp and "exp" in claims:
                if time.time() > claims["exp"]:
                    raise PermissionError("JWT token expired")

            if self.issuer and claims.get("iss") != self.issuer:
                raise PermissionError("Invalid issuer")

            if self.audience and claims.get("aud") != self.audience:
                raise PermissionError("Invalid audience")

            # Cache if enabled
            if self._cache is not None and "exp" in claims:
                self._cache[token] = (claims, claims["exp"])

            return claims

        def decode_unsafe(self, token):
            parts = token.split(".")
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            payload = base64.urlsafe_b64decode(parts[1] + "=" * (4 - len(parts[1]) % 4))
            return json.loads(payload)

        def decode_batch(self, tokens):
            results = []
            for token in tokens:
                try:
                    results.append(self.decode(token))
                except Exception as e:
                    results.append(e)
            return results

        def verify_signature(self, token):
            try:
                self.decode(token)
                return True
            except (ValueError, PermissionError, KeyError, TypeError):
                return False

        def clear_cache(self):
            if self._cache is not None:
                self._cache.clear()

    def rust_get_jwt_header(token):
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid JWT format")

        header = base64.urlsafe_b64decode(parts[0] + "=" * (4 - len(parts[0]) % 4))
        return json.loads(header)

    def rust_generate_jwt_secret(length=None):
        length = length or 32
        return secrets.token_bytes(length)

    # Hashing Fallbacks
    try:
        import bcrypt

        BCRYPT_AVAILABLE = True
    except ImportError:
        BCRYPT_AVAILABLE = False

    class FastArgon2Hasher:
        def __init__(
            self,
            time_cost=2,
            memory_cost=19456,
            parallelism=1,
            hash_length=32,
            salt_length=16,
            use_cache=True,
        ):
            self.time_cost = time_cost
            self.memory_cost = memory_cost
            self._cache = {} if use_cache else None

        def hash_password(self, password):
            # Simplified fallback using hashlib
            import secrets

            salt = secrets.token_hex(16)
            h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
            return f"$argon2$fallback${salt}${h.hex()}"

        def verify_password(self, password, hash_str):
            if self._cache is not None:
                cache_key = (password, hash_str)
                if cache_key in self._cache:
                    return self._cache[cache_key]

            if hash_str.startswith("$argon2$fallback$"):
                parts = hash_str.split("$")
                salt = parts[3]
                stored_hash = parts[4]
                h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
                result = h.hex() == stored_hash

                if self._cache is not None:
                    self._cache[(password, hash_str)] = result

                return result
            return False

        def hash_batch(self, passwords):
            return [self.hash_password(pwd) for pwd in passwords]

        def verify_batch(self, pairs):
            return [self.verify_password(pwd, h) for pwd, h in pairs]

        def clear_cache(self):
            if self._cache is not None:
                self._cache.clear()

        def needs_rehash(self, hash_str):
            return hash_str.startswith("$argon2$fallback$")

    class FastBcryptHasher:
        def __init__(self, cost=12, use_cache=True):
            self.cost = cost
            self._cache = {} if use_cache else None

        def hash_password(self, password):
            if BCRYPT_AVAILABLE:
                return bcrypt.hashpw(password.encode(), bcrypt.gensalt(self.cost)).decode()
            else:
                # Fallback to PBKDF2
                import secrets

                salt = secrets.token_hex(16)
                h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
                return f"$2b$fallback${salt}${h.hex()}"

        def verify_password(self, password, hash_str):
            if self._cache is not None:
                cache_key = (password, hash_str)
                if cache_key in self._cache:
                    return self._cache[cache_key]

            if BCRYPT_AVAILABLE and hash_str.startswith("$2"):
                result = bcrypt.checkpw(password.encode(), hash_str.encode())
            elif hash_str.startswith("$2b$fallback$"):
                parts = hash_str.split("$")
                salt = parts[3]
                stored_hash = parts[4]
                h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
                result = h.hex() == stored_hash
            else:
                result = False

            if self._cache is not None:
                self._cache[(password, hash_str)] = result

            return result

        def hash_batch(self, passwords):
            return [self.hash_password(pwd) for pwd in passwords]

        def needs_rehash(self, hash_str):
            return hash_str.startswith("$2b$fallback$")

    class FastBlake3Hasher:
        def __init__(self, key=None):
            self.key = key

        def hash(self, data):
            if self.key:
                h = hmac.new(self.key, data, hashlib.sha256)
            else:
                h = hashlib.sha256(data)
            return h.hexdigest()

        def hash_string(self, data):
            return self.hash(data.encode())

        def hash_file(self, file_path):
            h = hashlib.sha256()
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()

        def create_mac(self, data, key):
            return hmac.new(key, data, hashlib.sha256).hexdigest()

        def verify_mac(self, data, key, mac):
            return hmac.compare_digest(self.create_mac(data, key), mac)

    def rust_generate_salt(length=None):
        import secrets

        length = length or 16
        return secrets.token_hex(length)

    def rust_hash_password(password, time_cost=2, memory_cost=19456, parallelism=1):
        hasher = FastArgon2Hasher(time_cost, memory_cost, parallelism)
        return hasher.hash_password(password)

    def rust_verify_password(password, hash_str):
        if hash_str.startswith("$argon2"):
            hasher = FastArgon2Hasher()
        elif hash_str.startswith("$2"):
            hasher = FastBcryptHasher()
        else:
            raise ValueError("Unsupported hash format")
        return hasher.verify_password(password, hash_str)

    def rust_quick_hash(data):
        return hashlib.sha256(data).hexdigest()

    def rust_generate_token(length=None):
        import secrets

        length = length or 32
        return secrets.token_urlsafe(length)

    # Rate Limiting Fallbacks
    class TokenBucketLimiter:
        def __init__(self, capacity=100.0, refill_rate=10.0, cleanup_interval=60):
            self.capacity = capacity
            self.refill_rate = refill_rate
            self.buckets = {}
            self.last_cleanup = time.time()
            self.cleanup_interval = cleanup_interval

        def allow_request(self, key, tokens=None):
            tokens = tokens or 1.0
            now = time.time()

            if key not in self.buckets:
                self.buckets[key] = {"tokens": self.capacity, "last_refill": now}

            bucket = self.buckets[key]
            elapsed = now - bucket["last_refill"]
            bucket["tokens"] = min(self.capacity, bucket["tokens"] + elapsed * self.refill_rate)
            bucket["last_refill"] = now

            if bucket["tokens"] >= tokens:
                bucket["tokens"] -= tokens
                return True
            return False

        def available_tokens(self, key):
            if key not in self.buckets:
                return self.capacity

            bucket = self.buckets[key]
            now = time.time()
            elapsed = now - bucket["last_refill"]
            return min(self.capacity, bucket["tokens"] + elapsed * self.refill_rate)

        def time_until_available(self, key, tokens=None):
            tokens = tokens or 1.0
            available = self.available_tokens(key)

            if available >= tokens:
                return 0.0

            needed = tokens - available
            return needed / self.refill_rate

        def reset(self, key):
            self.buckets.pop(key, None)

        def reset_all(self):
            self.buckets.clear()

        def bucket_count(self):
            return len(self.buckets)

    class SlidingWindowLimiter:
        def __init__(self, window_size=60, max_requests=100, cleanup_interval=300):
            self.window_size = window_size
            self.max_requests = max_requests
            self.windows = defaultdict(deque)

        def allow_request(self, key):
            now = time.time()
            window = self.windows[key]

            # Remove old requests
            while window and window[0] < now - self.window_size:
                window.popleft()

            if len(window) < self.max_requests:
                window.append(now)
                return True
            return False

        def remaining_requests(self, key):
            now = time.time()
            window = self.windows[key]

            # Remove old requests
            while window and window[0] < now - self.window_size:
                window.popleft()

            return self.max_requests - len(window)

        def reset_time(self, key):
            window = self.windows.get(key)
            if window and window:
                return self.window_size - (time.time() - window[0])
            return None

        def reset(self, key):
            self.windows.pop(key, None)

        def reset_all(self):
            self.windows.clear()

    class FixedWindowLimiter:
        def __init__(self, window_size=60, max_requests=100):
            self.window_size = window_size
            self.max_requests = max_requests
            self.counters = {}

        def allow_request(self, key):
            current_window = int(time.time() / self.window_size)

            if key not in self.counters:
                self.counters[key] = {"window": current_window, "count": 0}

            counter = self.counters[key]

            if counter["window"] != current_window:
                counter["window"] = current_window
                counter["count"] = 0

            if counter["count"] < self.max_requests:
                counter["count"] += 1
                return True
            return False

        def remaining_requests(self, key):
            current_window = int(time.time() / self.window_size)

            if key in self.counters:
                counter = self.counters[key]
                if counter["window"] == current_window:
                    return self.max_requests - counter["count"]

            return self.max_requests

        def seconds_until_reset(self):
            current_time = time.time()
            return self.window_size - (current_time % self.window_size)

        def reset(self, key):
            self.counters.pop(key, None)

        def reset_all(self):
            self.counters.clear()

    class LeakyBucketLimiter:
        def __init__(self, capacity=100, leak_rate=10.0):
            self.capacity = capacity
            self.leak_rate = leak_rate
            self.buckets = defaultdict(deque)

        def add_request(self, key):
            now = time.time()
            bucket = self.buckets[key]

            # Leak old requests
            leak_duration = 1.0 / self.leak_rate
            while bucket and now - bucket[0] > leak_duration:
                bucket.popleft()

            if len(bucket) < self.capacity:
                bucket.append(now)
                return True
            return False

        def bucket_size(self, key):
            now = time.time()
            bucket = self.buckets[key]

            # Leak old requests
            leak_duration = 1.0 / self.leak_rate
            while bucket and now - bucket[0] > leak_duration:
                bucket.popleft()

            return len(bucket)

        def reset(self, key):
            self.buckets.pop(key, None)

    def rust_create_composite_limiter(strategies, window_size=None, max_requests=None):
        return f"composite:{strategies}"

    # Routing Fallbacks
    class FastRouter:
        def __init__(self):
            self.routes = []
            self.exact_routes = {}
            self.prefix_routes = []
            self.regex_routes = []
            self.param_routes = []

        def add_route(self, pattern, handler, methods=None, priority=None):
            methods = methods or ["GET"]
            priority = priority or 0

            route = {
                "pattern": pattern,
                "handler": handler,
                "methods": methods,
                "priority": priority,
            }

            self.routes.append(route)

            if "{" in pattern:
                # Parameterized route
                self.param_routes.append((self._parse_pattern(pattern), route))
            elif pattern.endswith("*"):
                # Prefix route
                self.prefix_routes.append((pattern[:-1], route))
            elif pattern.startswith("regex:"):
                # Regex route
                self.regex_routes.append((re.compile(pattern[6:]), route))
            else:
                # Exact route
                self.exact_routes[pattern] = route

        def _parse_pattern(self, pattern):
            segments = []
            for part in pattern.split("/"):
                if part.startswith("{") and part.endswith("}"):
                    param_name = part[1:-1]
                    if ":" in param_name:
                        name, validator = param_name.split(":", 1)
                        segments.append(("param", name, validator))
                    else:
                        segments.append(("param", param_name, None))
                elif part:
                    segments.append(("static", part))
            return segments

        def match_route(self, path, method="GET"):
            # Try exact match
            if path in self.exact_routes:
                route = self.exact_routes[path]
                if method in route["methods"]:
                    return {"handler": route["handler"], "params": {}}

            # Try parameterized routes
            for segments, route in self.param_routes:
                if method in route["methods"]:
                    params = self._match_segments(segments, path)
                    if params is not None:
                        return {"handler": route["handler"], "params": params}

            # Try prefix match
            for prefix, route in self.prefix_routes:
                if path.startswith(prefix) and method in route["methods"]:
                    return {
                        "handler": route["handler"],
                        "params": {},
                        "matched_prefix": prefix,
                    }

            # Try regex match
            for regex, route in self.regex_routes:
                if method in route["methods"]:
                    match = regex.match(path)
                    if match:
                        return {
                            "handler": route["handler"],
                            "params": match.groupdict(),
                        }

            return None

        def _match_segments(self, segments, path):
            path_parts = [p for p in path.split("/") if p]
            params = {}

            seg_idx = 0
            path_idx = 0

            while seg_idx < len(segments) and path_idx < len(path_parts):
                seg_type, seg_value, *rest = segments[seg_idx]

                if seg_type == "static":
                    if path_parts[path_idx] != seg_value:
                        return None
                elif seg_type == "param":
                    params[seg_value] = path_parts[path_idx]

                seg_idx += 1
                path_idx += 1

            if seg_idx == len(segments) and path_idx == len(path_parts):
                return params

            return None

        def match_batch(self, paths, method=None):
            method = method or "GET"
            return [self.match_route(path, method) for path in paths]

        def url_for(self, name, params):
            for route in self.routes:
                if route["handler"] == name:
                    pattern = route["pattern"]
                    for key, value in params.items():
                        pattern = pattern.replace(f"{{{key}}}", str(value))
                    return pattern
            raise KeyError(f"Route '{name}' not found")

        def clear(self):
            self.routes.clear()
            self.exact_routes.clear()
            self.prefix_routes.clear()
            self.regex_routes.clear()
            self.param_routes.clear()

        def stats(self):
            return {
                "total_routes": len(self.routes),
                "exact_routes": len(self.exact_routes),
                "prefix_routes": len(self.prefix_routes),
                "regex_routes": len(self.regex_routes),
                "param_routes": len(self.param_routes),
            }

    def rust_parse_query_string(query):
        return dict(parse_qs(query))

    def rust_encode_query_string(params):
        return urlencode(params, doseq=True)

    def rust_parse_url(url_str):
        parsed = urlparse(url_str)
        return {
            "scheme": parsed.scheme,
            "host": parsed.hostname or "",
            "port": parsed.port,
            "path": parsed.path,
            "query": parsed.query or "",
            "fragment": parsed.fragment or "",
            "username": parsed.username or "",
            "password": parsed.password or "",
        }


# Export the appropriate implementations
__all__ = [
    "RUST_AVAILABLE",
    # JSON
    "FastJsonEncoder",
    "FastJsonDecoder",
    "validate_json",
    "minify_json",
    "prettify_json",
    "json_extract",
    "json_merge",
    # JWT
    "FastJwtEncoder",
    "FastJwtDecoder",
    "get_jwt_header",
    "generate_jwt_secret",
    # Hashing
    "FastArgon2Hasher",
    "FastBcryptHasher",
    "FastBlake3Hasher",
    "generate_salt",
    "hash_password",
    "verify_password",
    "quick_hash",
    "generate_token",
    # Rate Limiting
    "TokenBucketLimiter",
    "SlidingWindowLimiter",
    "FixedWindowLimiter",
    "LeakyBucketLimiter",
    "create_composite_limiter",
    # Routing
    "FastRouter",
    "parse_query_string",
    "encode_query_string",
    "parse_url",
]

# Create aliases for convenience
validate_json = rust_validate_json
minify_json = rust_minify_json
prettify_json = rust_prettify_json
json_extract = rust_json_extract
json_merge = rust_json_merge

get_jwt_header = rust_get_jwt_header
generate_jwt_secret = rust_generate_jwt_secret

generate_salt = rust_generate_salt
hash_password = rust_hash_password
verify_password = rust_verify_password
quick_hash = rust_quick_hash
generate_token = rust_generate_token

create_composite_limiter = rust_create_composite_limiter

parse_query_string = rust_parse_query_string
encode_query_string = rust_encode_query_string
parse_url = rust_parse_url
