"""
CSRF Template Helpers

Utilities for integrating CSRF protection into templates and views.

Provides:
- Template functions for token injection
- Decorators for view protection
- Manual token access
- AJAX helper utilities
"""

import json
from functools import wraps
from typing import Any, Callable, Dict, Optional

from .csrf import CSRFProtection, CSRFTokenError, get_csrf_protection


class CSRFTemplateHelpers:
    """
    CSRF template integration helpers

    Provides functions for use in template engines (Jinja2, etc.)
    """

    def __init__(self, csrf_protection: Optional[CSRFProtection] = None):
        self.csrf = csrf_protection or get_csrf_protection()

    def csrf_token(self, session_id: Optional[str] = None) -> str:
        """
        Generate CSRF token for template

        Usage in Jinja2:
            {{ csrf_token() }}

        Args:
            session_id: Optional session ID

        Returns:
            CSRF token string
        """
        return self.csrf.generate_token(session_id)

    def csrf_input(self, session_id: Optional[str] = None) -> str:
        """
        Generate hidden input field with CSRF token

        Usage in Jinja2:
            {{ csrf_input() | safe }}

        Args:
            session_id: Optional session ID

        Returns:
            HTML input field
        """
        token = self.csrf.generate_token(session_id)
        field_name = self.csrf.config.form_field_name

        return f'<input type="hidden" name="{field_name}" value="{token}">'

    def csrf_meta_tag(self, session_id: Optional[str] = None) -> str:
        """
        Generate meta tag with CSRF token

        Usage in Jinja2:
            <head>
                {{ csrf_meta_tag() | safe }}
            </head>

        Then in JavaScript:
            const token = document.querySelector('meta[name="csrf-token"]').content;

        Args:
            session_id: Optional session ID

        Returns:
            HTML meta tag
        """
        token = self.csrf.generate_token(session_id)
        return f'<meta name="csrf-token" content="{token}">'

    def csrf_header_name(self) -> str:
        """
        Get CSRF header name for AJAX requests

        Returns:
            Header name string
        """
        return self.csrf.config.header_name

    def csrf_javascript(self, session_id: Optional[str] = None) -> str:
        """
        Generate JavaScript code for AJAX CSRF protection

        Usage in template:
            <script>
                {{ csrf_javascript() | safe }}
            </script>

        This adds CSRF token to all AJAX requests automatically.

        Args:
            session_id: Optional session ID

        Returns:
            JavaScript code
        """
        token = self.csrf.generate_token(session_id)
        header_name = self.csrf.config.header_name

        js_code = f"""
// CSRF Protection for AJAX requests
(function() {{
    const csrfToken = "{token}";
    const csrfHeaderName = "{header_name}";

    // Patch XMLHttpRequest
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {{
        this._method = method;
        this._url = url;
        return originalOpen.apply(this, arguments);
    }};

    const originalSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function(data) {{
        // Add CSRF header for unsafe methods
        const unsafeMethods = ['POST', 'PUT', 'DELETE', 'PATCH'];
        if (unsafeMethods.includes(this._method.toUpperCase())) {{
            this.setRequestHeader(csrfHeaderName, csrfToken);
        }}
        return originalSend.apply(this, arguments);
    }};

    // Patch fetch API
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {{
        options = options || {{}};
        const method = (options.method || 'GET').toUpperCase();
        const unsafeMethods = ['POST', 'PUT', 'DELETE', 'PATCH'];

        if (unsafeMethods.includes(method)) {{
            options.headers = options.headers || {{}};
            options.headers[csrfHeaderName] = csrfToken;
        }}

        return originalFetch.apply(this, arguments);
    }};
}})();
"""
        return js_code.strip()


def csrf_protect(
    csrf_protection: Optional[CSRFProtection] = None,
    get_session_id: Optional[Callable] = None,
):
    """
    Decorator to protect view functions with CSRF validation

    Usage:
        @app.route('/submit', methods=['POST'])
        @csrf_protect()
        async def submit_form(request):
            # This view is protected

    Args:
        csrf_protection: CSRF protection instance
        get_session_id: Function to extract session ID from request

    Returns:
        Decorator function
    """
    csrf = csrf_protection or get_csrf_protection()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            # Extract CSRF token from request
            token = _extract_token_from_request(request, csrf)

            # Extract session ID
            session_id = None
            if get_session_id:
                session_id = get_session_id(request)

            # Validate token
            try:
                csrf.validate_token(token, session_id)
            except CSRFTokenError as e:
                # Return error response
                return {
                    "status": 403,
                    "body": {"error": "CSRF validation failed", "detail": str(e)},
                }

            # Call original function
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def csrf_exempt(func: Callable) -> Callable:
    """
    Decorator to exempt view from CSRF protection

    Usage:
        @app.route('/webhook', methods=['POST'])
        @csrf_exempt
        async def webhook(request):
            # This view is exempt from CSRF

    Args:
        func: View function

    Returns:
        Wrapped function with exempt marker
    """
    func._csrf_exempt = True
    return func


def _extract_token_from_request(request: Any, csrf: CSRFProtection) -> Optional[str]:
    """
    Extract CSRF token from request

    Tries multiple sources:
    1. Custom header
    2. Form data
    3. JSON body
    4. Query parameters

    Args:
        request: Request object
        csrf: CSRF protection instance

    Returns:
        CSRF token or None
    """
    # Try header first
    header_name = csrf.config.header_name
    token = getattr(request, "headers", {}).get(header_name)

    if token:
        return token

    # Try form data
    field_name = csrf.config.form_field_name

    # Check form data
    if hasattr(request, "form"):
        token = request.form.get(field_name)
        if token:
            return token

    # Check JSON body
    if hasattr(request, "json"):
        json_data = request.json
        if isinstance(json_data, dict):
            token = json_data.get(field_name)
            if token:
                return token

    # Check query parameters
    if hasattr(request, "query_params"):
        token = request.query_params.get(field_name)
        if token:
            return token

    return None


def get_csrf_token(request: Any, csrf_protection: Optional[CSRFProtection] = None) -> str:
    """
    Get CSRF token for request

    Args:
        request: Request object
        csrf_protection: CSRF protection instance

    Returns:
        CSRF token
    """
    csrf = csrf_protection or get_csrf_protection()

    # Try to get session ID
    session_id = None
    if hasattr(request, "session"):
        session_id = getattr(request.session, "id", None)

    return csrf.generate_token(session_id)


class CSRFMiddlewareHelper:
    """
    Helper class for integrating CSRF into custom middleware

    Provides utilities for middleware that needs CSRF awareness
    """

    @staticmethod
    def is_exempt(request: Any) -> bool:
        """
        Check if request is exempt from CSRF

        Args:
            request: Request object

        Returns:
            True if exempt
        """
        # Check if view function is marked as exempt
        if hasattr(request, "endpoint"):
            endpoint = request.endpoint
            if hasattr(endpoint, "_csrf_exempt"):
                return endpoint._csrf_exempt

        return False

    @staticmethod
    def add_token_to_context(
        context: Dict[str, Any], request: Any, csrf: Optional[CSRFProtection] = None
    ):
        """
        Add CSRF token to template context

        Args:
            context: Template context dict
            request: Request object
            csrf: CSRF protection instance
        """
        csrf = csrf or get_csrf_protection()

        # Add token generation function
        helpers = CSRFTemplateHelpers(csrf)

        context["csrf_token"] = lambda: get_csrf_token(request, csrf)
        context["csrf_input"] = lambda: helpers.csrf_input()
        context["csrf_meta"] = lambda: helpers.csrf_meta_tag()
        context["csrf_js"] = lambda: helpers.csrf_javascript()


# Jinja2 Integration
def add_csrf_to_jinja2(env, csrf_protection: Optional[CSRFProtection] = None):
    """
    Add CSRF functions to Jinja2 environment

    Usage:
        from jinja2 import Environment
        env = Environment()
        add_csrf_to_jinja2(env)

    Args:
        env: Jinja2 environment
        csrf_protection: CSRF protection instance
    """
    helpers = CSRFTemplateHelpers(csrf_protection)

    env.globals["csrf_token"] = helpers.csrf_token
    env.globals["csrf_input"] = helpers.csrf_input
    env.globals["csrf_meta"] = helpers.csrf_meta_tag
    env.globals["csrf_header_name"] = helpers.csrf_header_name
    env.globals["csrf_js"] = helpers.csrf_javascript


# Example usage documentation
CSRF_USAGE_EXAMPLES = """
# CSRF Protection Usage Examples

## 1. Basic Form Protection (HTML)

```html
<form method="POST" action="/submit">
    {{ csrf_input() }}
    <input type="text" name="data">
    <button type="submit">Submit</button>
</form>
```

## 2. AJAX with Meta Tag

```html
<head>
    {{ csrf_meta() }}
</head>

<script>
function submitData(data) {
    const token = document.querySelector('meta[name="csrf-token"]').content;

    fetch('/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-Token': token
        },
        body: JSON.stringify(data)
    });
}
</script>
```

## 3. Automatic AJAX Protection

```html
<head>
    <script>{{ csrf_js() }}</script>
</head>

<script>
// All AJAX requests now automatically include CSRF token
fetch('/api/data', { method: 'POST', body: {...} });
</script>
```

## 4. View Decorator

```python
from covet.security.csrf_helpers import csrf_protect, csrf_exempt

@app.route('/protected', methods=['POST'])
@csrf_protect()
async def protected_view(request):
    # Automatically validated
    return {'status': 'ok'}

@app.route('/webhook', methods=['POST'])
@csrf_exempt
async def webhook(request):
    # Exempt from CSRF
    return {'status': 'received'}
```

## 5. Manual Token Access

```python
from covet.security.csrf_helpers import get_csrf_token

@app.route('/form')
async def show_form(request):
    token = get_csrf_token(request)
    return render_template('form.html', csrf_token=token)
```
"""
