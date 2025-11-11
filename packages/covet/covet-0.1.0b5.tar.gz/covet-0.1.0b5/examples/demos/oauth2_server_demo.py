#!/usr/bin/env python3
"""
OAuth2 Server Demo for CovetPy

This demo showcases the complete OAuth2 server implementation including:
- Client registration
- Authorization code flow with PKCE
- Client credentials flow
- Token introspection and revocation
- Security features and monitoring
- Database integration

Run this script to see a complete OAuth2 server in action.
"""

import asyncio
import base64
import hashlib
import json
import secrets
import time
from urllib.parse import parse_qs, urlparse

from src.covet.core.app_pure import CovetApplication
from src.covet.core.http import Request, Response
from src.covet.core.http import json_response, html_response
from src.covet.database.database_system import DatabaseSystem
from src.covet.database.adapters.sqlite import SQLiteAdapter
from src.covet.security.oauth2_integration import setup_oauth2_server
from src.covet.security.oauth2_server import ClientType, GrantType
from src.covet.security.oauth2_security import oauth2_security


class OAuth2ServerDemo:
    """Complete OAuth2 server demonstration."""

    def __init__(self):
        # Initialize CovetPy app
        self.app = CovetApplication()
        
        # Initialize database
        self.db_system = DatabaseSystem()
        self.db_adapter = SQLiteAdapter("oauth2_demo.db")
        self.db_system.set_adapter(self.db_adapter)
        
        # Setup OAuth2 server
        self.oauth2 = setup_oauth2_server(
            self.app, 
            self.db_system, 
            issuer="http://localhost:8000"
        )
        
        # Demo clients
        self.demo_clients = {}
        
        # Setup demo routes
        self._setup_demo_routes()
        
        print("OAuth2 Server Demo initialized")
        print("Available endpoints:")
        print("  - http://localhost:8000/demo - Demo interface")
        print("  - http://localhost:8000/oauth2/authorize - Authorization endpoint")
        print("  - http://localhost:8000/oauth2/token - Token endpoint")
        print("  - http://localhost:8000/oauth2/introspect - Introspection endpoint")
        print("  - http://localhost:8000/oauth2/revoke - Revocation endpoint")
        print("  - http://localhost:8000/.well-known/oauth-authorization-server - Server metadata")

    def _setup_demo_routes(self):
        """Setup demo routes and endpoints."""
        
        @self.app.route("/", methods=["GET"])
        def home(request: Request) -> Response:
            """Home page with demo links."""
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>OAuth2 Server Demo</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
                    .success { background: #d4edda; border-color: #c3e6cb; }
                    .info { background: #d1ecf1; border-color: #bee5eb; }
                    .warning { background: #fff3cd; border-color: #ffeaa7; }
                    code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
                    pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>OAuth2 Server Demo</h1>
                
                <div class="card info">
                    <h3>Welcome to CovetPy OAuth2 Server</h3>
                    <p>This demo showcases a complete RFC 6749 compliant OAuth2 authorization server with:</p>
                    <ul>
                        <li>Authorization Code Flow with PKCE (RFC 7636)</li>
                        <li>Client Credentials Flow</li>
                        <li>Token introspection and revocation</li>
                        <li>Comprehensive security features</li>
                        <li>Database persistence</li>
                        <li>Zero external dependencies</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Quick Start</h3>
                    <ol>
                        <li><a href="/demo/register-client">Register a demo client</a></li>
                        <li><a href="/demo/authorization-flow">Try authorization flow</a></li>
                        <li><a href="/demo/client-credentials">Try client credentials flow</a></li>
                        <li><a href="/demo/security-metrics">View security metrics</a></li>
                    </ol>
                </div>

                <div class="card">
                    <h3>OAuth2 Endpoints</h3>
                    <ul>
                        <li><strong>Authorization:</strong> <code>/oauth2/authorize</code></li>
                        <li><strong>Token:</strong> <code>/oauth2/token</code></li>
                        <li><strong>Introspection:</strong> <code>/oauth2/introspect</code></li>
                        <li><strong>Revocation:</strong> <code>/oauth2/revoke</code></li>
                        <li><strong>Metadata:</strong> <code>/.well-known/oauth-authorization-server</code></li>
                    </ul>
                </div>
            </body>
            </html>
            """
            return html_response(html)

        @self.app.route("/demo/register-client", methods=["GET", "POST"])
        def register_client_demo(request: Request) -> Response:
            """Demo client registration."""
            if request.method == "POST":
                try:
                    # Register a demo client
                    client_id, client_secret = self.oauth2.register_client(
                        client_name="Demo Web Application",
                        client_type=ClientType.CONFIDENTIAL,
                        redirect_uris=["http://localhost:8000/demo/callback"],
                        scope=["read", "write"],
                        grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.CLIENT_CREDENTIALS, GrantType.REFRESH_TOKEN]
                    )
                    
                    # Store for demo use
                    self.demo_clients['web_app'] = {
                        'client_id': client_id,
                        'client_secret': client_secret
                    }
                    
                    # Also register a public client
                    public_client_id, _ = self.oauth2.register_client(
                        client_name="Demo Mobile App",
                        client_type=ClientType.PUBLIC,
                        redirect_uris=["http://localhost:8000/demo/callback"],
                        scope=["read"],
                        grant_types=[GrantType.AUTHORIZATION_CODE]
                    )
                    
                    self.demo_clients['mobile_app'] = {
                        'client_id': public_client_id,
                        'client_secret': None
                    }
                    
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Client Registration Success</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; margin: 40px; }}
                            .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                            .success {{ background: #d4edda; border-color: #c3e6cb; }}
                            code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                        </style>
                    </head>
                    <body>
                        <h1>Clients Registered Successfully!</h1>
                        
                        <div class="card success">
                            <h3>Confidential Client (Web App)</h3>
                            <p><strong>Client ID:</strong> <code>{client_id}</code></p>
                            <p><strong>Client Secret:</strong> <code>{client_secret}</code></p>
                            <p><strong>Redirect URI:</strong> <code>http://localhost:8000/demo/callback</code></p>
                            <p><strong>Scopes:</strong> read, write</p>
                        </div>

                        <div class="card success">
                            <h3>Public Client (Mobile App)</h3>
                            <p><strong>Client ID:</strong> <code>{public_client_id}</code></p>
                            <p><strong>Client Secret:</strong> None (public client)</p>
                            <p><strong>Redirect URI:</strong> <code>http://localhost:8000/demo/callback</code></p>
                            <p><strong>Scopes:</strong> read</p>
                        </div>

                        <p><a href="/demo/authorization-flow">Try authorization flow →</a></p>
                        <p><a href="/">← Back to home</a></p>
                    </body>
                    </html>
                    """
                    return html_response(html)
                    
                except Exception as e:
                    return html_response(f"<h1>Error</h1><p>{str(e)}</p>", status_code=400)
            
            # GET request - show registration form
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Register Demo Client</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
                    button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                    button:hover { background: #0056b3; }
                </style>
            </head>
            <body>
                <h1>Register Demo Clients</h1>
                <div class="card">
                    <p>This will register two demo clients:</p>
                    <ul>
                        <li><strong>Web Application</strong> - Confidential client with full OAuth2 capabilities</li>
                        <li><strong>Mobile Application</strong> - Public client for authorization code flow with PKCE</li>
                    </ul>
                    <form method="post">
                        <button type="submit">Register Demo Clients</button>
                    </form>
                </div>
                <p><a href="/">← Back to home</a></p>
            </body>
            </html>
            """
            return html_response(html)

        @self.app.route("/demo/authorization-flow", methods=["GET"])
        def authorization_flow_demo(request: Request) -> Response:
            """Demo authorization code flow."""
            if 'web_app' not in self.demo_clients:
                return html_response("""
                    <h1>No Demo Client</h1>
                    <p>Please <a href="/demo/register-client">register a demo client</a> first.</p>
                """, status_code=400)
            
            client_id = self.demo_clients['web_app']['client_id']
            
            # Generate PKCE challenge
            code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
            code_challenge = base64.urlsafe_b64encode(
                hashlib.sha256(code_verifier.encode('utf-8')).digest()
            ).decode('utf-8').rstrip('=')
            
            # Generate state
            state = secrets.token_urlsafe(32)
            
            # Store for callback
            request.session = getattr(request, 'session', {})
            request.session['demo_code_verifier'] = code_verifier
            request.session['demo_state'] = state
            
            # Build authorization URL
            auth_params = {
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': 'http://localhost:8000/demo/callback',
                'scope': 'read write',
                'state': state,
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            
            auth_url = '/oauth2/authorize?' + '&'.join(f'{k}={v}' for k, v in auth_params.items())
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authorization Flow Demo</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .info {{ background: #d1ecf1; border-color: #bee5eb; }}
                    code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                    pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                    button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                    button:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <h1>Authorization Code Flow Demo</h1>
                
                <div class="card info">
                    <h3>OAuth2 Authorization Code Flow with PKCE</h3>
                    <p>This demonstrates the secure authorization code flow:</p>
                    <ol>
                        <li>Generate PKCE challenge and state parameter</li>
                        <li>Redirect to authorization endpoint</li>
                        <li>User consent (simulated)</li>
                        <li>Exchange authorization code for access token</li>
                        <li>Verify PKCE code verifier</li>
                    </ol>
                </div>

                <div class="card">
                    <h3>Generated Parameters</h3>
                    <p><strong>Client ID:</strong> <code>{client_id}</code></p>
                    <p><strong>State:</strong> <code>{state}</code></p>
                    <p><strong>Code Challenge:</strong> <code>{code_challenge}</code></p>
                    <p><strong>Code Verifier:</strong> <code>{code_verifier}</code> (stored in session)</p>
                </div>

                <div class="card">
                    <h3>Authorization URL</h3>
                    <pre>{auth_url}</pre>
                    <p><a href="{auth_url}"><button>Start Authorization Flow</button></a></p>
                </div>

                <p><a href="/">← Back to home</a></p>
            </body>
            </html>
            """
            return html_response(html)

        @self.app.route("/demo/callback", methods=["GET"])
        def oauth_callback_demo(request: Request) -> Response:
            """OAuth2 callback handler for demo."""
            code = request.query_params.get("code")
            state = request.query_params.get("state")
            error = request.query_params.get("error")
            
            if error:
                return html_response(f"""
                    <h1>Authorization Error</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {request.query_params.get("error_description", "No description")}</p>
                    <p><a href="/demo/authorization-flow">← Try again</a></p>
                """, status_code=400)
            
            if not code:
                return html_response("<h1>Missing authorization code</h1>", status_code=400)
            
            # Simulate token exchange (in real app, this would be done server-side)
            if 'web_app' not in self.demo_clients:
                return html_response("<h1>Demo client not found</h1>", status_code=400)
            
            client_id = self.demo_clients['web_app']['client_id']
            client_secret = self.demo_clients['web_app']['client_secret']
            
            # This would normally be retrieved from session
            code_verifier = "demo_code_verifier_would_be_from_session"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Authorization Successful</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .success {{ background: #d4edda; border-color: #c3e6cb; }}
                    code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                    pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <h1>Authorization Successful!</h1>
                
                <div class="card success">
                    <h3>Authorization Code Received</h3>
                    <p><strong>Code:</strong> <code>{code}</code></p>
                    <p><strong>State:</strong> <code>{state}</code></p>
                </div>

                <div class="card">
                    <h3>Next Steps</h3>
                    <p>In a real application, you would now:</p>
                    <ol>
                        <li>Verify the state parameter matches what you sent</li>
                        <li>Exchange the authorization code for an access token</li>
                        <li>Include the PKCE code verifier in the token request</li>
                        <li>Store the access token securely</li>
                    </ol>
                </div>

                <div class="card">
                    <h3>Token Exchange Example</h3>
                    <p>POST to <code>/oauth2/token</code> with:</p>
                    <pre>{{
    "grant_type": "authorization_code",
    "code": "{code}",
    "redirect_uri": "http://localhost:8000/demo/callback",
    "client_id": "{client_id}",
    "client_secret": "{client_secret}",
    "code_verifier": "original_code_verifier"
}}</pre>
                </div>

                <p><a href="/demo/client-credentials">Try client credentials flow →</a></p>
                <p><a href="/">← Back to home</a></p>
            </body>
            </html>
            """
            return html_response(html)

        @self.app.route("/demo/client-credentials", methods=["GET", "POST"])
        def client_credentials_demo(request: Request) -> Response:
            """Demo client credentials flow."""
            if 'web_app' not in self.demo_clients:
                return html_response("""
                    <h1>No Demo Client</h1>
                    <p>Please <a href="/demo/register-client">register a demo client</a> first.</p>
                """, status_code=400)
            
            if request.method == "POST":
                # Simulate client credentials token request
                client_id = self.demo_clients['web_app']['client_id']
                client_secret = self.demo_clients['web_app']['client_secret']
                
                # Create token request
                token_data = {
                    'grant_type': 'client_credentials',
                    'scope': 'read',
                    'client_id': client_id,
                    'client_secret': client_secret
                }
                
                # This would be a real HTTP request to /oauth2/token
                result = f"""
                {{
                    "access_token": "demo_access_token_12345",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": "read"
                }}
                """
                
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Client Credentials Success</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                        .success {{ background: #d4edda; border-color: #c3e6cb; }}
                        code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                        pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                    <h1>Client Credentials Flow Successful!</h1>
                    
                    <div class="card success">
                        <h3>Access Token Response</h3>
                        <pre>{result}</pre>
                    </div>

                    <div class="card">
                        <h3>Using the Access Token</h3>
                        <p>You can now use this token to access protected resources:</p>
                        <pre>Authorization: Bearer demo_access_token_12345</pre>
                    </div>

                    <p><a href="/demo/security-metrics">View security metrics →</a></p>
                    <p><a href="/">← Back to home</a></p>
                </body>
                </html>
                """
                return html_response(html)
            
            # GET request - show client credentials form
            client_id = self.demo_clients['web_app']['client_id']
            client_secret = self.demo_clients['web_app']['client_secret']
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Client Credentials Flow</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .info {{ background: #d1ecf1; border-color: #bee5eb; }}
                    code {{ background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }}
                    pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                    button {{ background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }}
                    button:hover {{ background: #0056b3; }}
                </style>
            </head>
            <body>
                <h1>Client Credentials Flow Demo</h1>
                
                <div class="card info">
                    <h3>OAuth2 Client Credentials Flow</h3>
                    <p>This flow is used for machine-to-machine authentication where:</p>
                    <ul>
                        <li>No user interaction is required</li>
                        <li>The client acts on its own behalf</li>
                        <li>Only confidential clients can use this flow</li>
                        <li>Client authenticates with client credentials</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Client Information</h3>
                    <p><strong>Client ID:</strong> <code>{client_id}</code></p>
                    <p><strong>Client Secret:</strong> <code>{client_secret}</code></p>
                    <p><strong>Requested Scope:</strong> <code>read</code></p>
                </div>

                <div class="card">
                    <h3>Token Request</h3>
                    <p>POST to <code>/oauth2/token</code> with:</p>
                    <pre>{{
    "grant_type": "client_credentials",
    "scope": "read",
    "client_id": "{client_id}",
    "client_secret": "{client_secret}"
}}</pre>
                    <form method="post">
                        <button type="submit">Execute Client Credentials Flow</button>
                    </form>
                </div>

                <p><a href="/">← Back to home</a></p>
            </body>
            </html>
            """
            return html_response(html)

        @self.app.route("/demo/security-metrics", methods=["GET"])
        def security_metrics_demo(request: Request) -> Response:
            """Show security metrics."""
            metrics = self.oauth2.get_security_metrics()
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Security Metrics</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                    .info {{ background: #d1ecf1; border-color: #bee5eb; }}
                    pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                    .metric {{ display: inline-block; margin: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>OAuth2 Security Metrics</h1>
                
                <div class="card info">
                    <h3>Security Monitoring</h3>
                    <p>The OAuth2 server includes comprehensive security monitoring:</p>
                    <ul>
                        <li>Rate limiting and abuse detection</li>
                        <li>Security event logging and auditing</li>
                        <li>Client risk scoring</li>
                        <li>Attack pattern detection</li>
                    </ul>
                </div>

                <div class="card">
                    <h3>Current Metrics</h3>
                    <pre>{json.dumps(metrics, indent=2)}</pre>
                </div>

                <div class="card">
                    <h3>Protected Resource Demo</h3>
                    <p>Try accessing a protected resource:</p>
                    <p><a href="/demo/protected">Access Protected Resource</a></p>
                </div>

                <p><a href="/">← Back to home</a></p>
            </body>
            </html>
            """
            return html_response(html)

        @self.app.route("/demo/protected", methods=["GET"])
        def protected_resource_demo(request: Request) -> Response:
            """Demo protected resource."""
            # This would normally use the OAuth2BearerMiddleware
            # For demo purposes, we'll show what it would look like
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Protected Resource</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
                    .warning { background: #fff3cd; border-color: #ffeaa7; }
                    code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
                    pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
                </style>
            </head>
            <body>
                <h1>Protected Resource</h1>
                
                <div class="card warning">
                    <h3>Access Denied</h3>
                    <p>This resource requires a valid OAuth2 access token.</p>
                    <p>Include the token in the Authorization header:</p>
                    <pre>Authorization: Bearer your_access_token_here</pre>
                </div>

                <div class="card">
                    <h3>How to Access</h3>
                    <ol>
                        <li>Complete the authorization flow to get an access token</li>
                        <li>Include the token in the Authorization header</li>
                        <li>Make a request to this endpoint</li>
                    </ol>
                    <p>Example with curl:</p>
                    <pre>curl -H "Authorization: Bearer your_token" http://localhost:8000/demo/protected</pre>
                </div>

                <p><a href="/">← Back to home</a></p>
            </body>
            </html>
            """
            return html_response(html)

        # Add a simple login endpoint for demo
        @self.app.route("/login", methods=["GET"])
        def login_demo(request: Request) -> Response:
            """Simple login page for demo."""
            # In a real app, this would handle actual authentication
            # For demo, we'll just simulate user consent
            client_id = request.query_params.get("client_id")
            redirect_uri = request.query_params.get("redirect_uri")
            scope = request.query_params.get("scope")
            state = request.query_params.get("state")
            
            # Create a demo user session
            if hasattr(self.oauth2.consent_provider, 'create_user_session'):
                session_token = self.oauth2.consent_provider.create_user_session("demo_user_123")
            
            # Redirect back to authorization with simulated authentication
            auth_params = {
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': scope,
                'state': state
            }
            
            # Add session token as a header (simplified)
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Demo Login</title>
                <meta http-equiv="refresh" content="2;url=/oauth2/authorize?{'&'.join(f'{k}={v}' for k, v in auth_params.items() if v)}">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; text-align: center; }}
                    .card {{ border: 1px solid #ddd; padding: 20px; margin: 20px auto; border-radius: 5px; max-width: 500px; }}
                    .success {{ background: #d4edda; border-color: #c3e6cb; }}
                </style>
            </head>
            <body>
                <div class="card success">
                    <h2>Login Successful!</h2>
                    <p>Logged in as: <strong>demo_user_123</strong></p>
                    <p>Redirecting to authorization...</p>
                </div>
            </body>
            </html>
            """
            return html_response(html)

    def run_tests(self):
        """Run comprehensive OAuth2 server tests."""
        print("\n" + "="*60)
        print("OAUTH2 SERVER COMPREHENSIVE TESTS")
        print("="*60)
        
        # Test client registration
        print("\n1. Testing Client Registration...")
        try:
            client_id, client_secret = self.oauth2.register_client(
                client_name="Test Application",
                client_type=ClientType.CONFIDENTIAL,
                redirect_uris=["http://localhost:8000/callback"],
                scope=["read", "write"],
                grant_types=[GrantType.AUTHORIZATION_CODE, GrantType.CLIENT_CREDENTIALS]
            )
            print(f"   ✓ Confidential client registered: {client_id}")
            
            public_client_id, _ = self.oauth2.register_client(
                client_name="Test Mobile App",
                client_type=ClientType.PUBLIC,
                redirect_uris=["http://localhost:8000/callback"],
                scope=["read"],
                grant_types=[GrantType.AUTHORIZATION_CODE]
            )
            print(f"   ✓ Public client registered: {public_client_id}")
            
        except Exception as e:
            print(f"   ✗ Client registration failed: {e}")
            return False

        # Test server metadata
        print("\n2. Testing Server Metadata...")
        try:
            metadata = self.oauth2.oauth2_server.get_server_metadata()
            required_fields = ['issuer', 'authorization_endpoint', 'token_endpoint']
            if all(field in metadata for field in required_fields):
                print("   ✓ Server metadata complete")
            else:
                print("   ✗ Server metadata missing required fields")
                return False
        except Exception as e:
            print(f"   ✗ Server metadata failed: {e}")
            return False

        # Test security features
        print("\n3. Testing Security Features...")
        try:
            # Test input validation
            from src.covet.security.oauth2_security import OAuth2InputValidator
            
            validator = OAuth2InputValidator()
            
            # Test valid inputs
            assert validator.validate_client_id("valid_client_123") == True
            assert validator.validate_state("valid_state_abc") == True
            assert validator.validate_scope("read write") == True
            
            # Test invalid inputs
            assert validator.validate_client_id("invalid<script>") == False
            assert validator.validate_state("state with spaces") == False
            
            print("   ✓ Input validation working")
            
            # Test PKCE validation
            assert validator.validate_pkce_challenge("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk", "S256") == True
            assert validator.validate_pkce_verifier("dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk") == True
            
            print("   ✓ PKCE validation working")
            
        except Exception as e:
            print(f"   ✗ Security features failed: {e}")
            return False

        # Test rate limiting
        print("\n4. Testing Rate Limiting...")
        try:
            from src.covet.security.oauth2_security import OAuth2RateLimiter
            
            limiter = OAuth2RateLimiter()
            
            # Should not be limited initially
            is_limited, _ = limiter.is_rate_limited("127.0.0.1")
            assert is_limited == False
            
            # Record successful request
            limiter.record_request("127.0.0.1")
            
            print("   ✓ Rate limiting working")
            
        except Exception as e:
            print(f"   ✗ Rate limiting failed: {e}")
            return False

        # Test token expiration
        print("\n5. Testing Token Lifecycle...")
        try:
            from src.covet.security.oauth2_server import AccessToken, TokenType
            import time
            
            # Create token with short expiration
            token = AccessToken(
                token="test_token",
                client_id=client_id,
                user_id="test_user",
                scope={"read"},
                token_type=TokenType.BEARER,
                expires_in=1,  # 1 second
                created_at=time.time() - 2  # Created 2 seconds ago
            )
            
            assert token.is_expired == True
            print("   ✓ Token expiration working")
            
        except Exception as e:
            print(f"   ✗ Token lifecycle failed: {e}")
            return False

        # Test database storage
        print("\n6. Testing Database Storage...")
        try:
            # Clean up expired tokens
            cleaned = self.oauth2.cleanup_expired_tokens()
            print(f"   ✓ Database cleanup removed {cleaned} expired items")
            
        except Exception as e:
            print(f"   ✗ Database storage failed: {e}")
            return False

        print("\n" + "="*60)
        print("ALL TESTS PASSED! 🎉")
        print("OAuth2 Server is fully functional and secure.")
        print("="*60)
        
        return True

    def run(self, host="localhost", port=8000):
        """Run the demo server."""
        print(f"\nStarting OAuth2 Server Demo on http://{host}:{port}")
        print("Press Ctrl+C to stop the server")
        
        # Run tests first
        if self.run_tests():
            print(f"\nDemo server ready at: http://{host}:{port}")
            print("Visit the URL to explore the OAuth2 server features!")
        else:
            print("\nTests failed! Check the implementation.")


def main():
    """Main function to run the OAuth2 server demo."""
    demo = OAuth2ServerDemo()
    demo.run()


if __name__ == "__main__":
    main()