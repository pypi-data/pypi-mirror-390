#!/usr/bin/env python3
"""
CovetPy HTTP/1.1 Server Demo

This demo showcases the production-grade HTTP/1.1 server implementation
with full RFC compliance and performance optimizations.
"""

import asyncio
import sys
import time
import json
from typing import Dict, Any

# Add src to path
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

from covet.core.http_server import CovetHTTPServer, ServerConfig
from covet.core.http import Response, json_response, text_response, html_response


class DemoApp:
    """Demo ASGI application showcasing HTTP/1.1 features"""
    
    def __init__(self):
        self.request_count = 0
        self.start_time = time.time()
        
    async def __call__(self, scope, receive, send):
        """ASGI application interface"""
        if scope['type'] != 'http':
            return
            
        self.request_count += 1
        path = scope['path']
        method = scope['method']
        
        print(f"[{self.request_count}] {method} {path}")
        
        # Route handling
        if path == '/':
            response = self.home_page()
            
        elif path == '/api/stats':
            response = self.api_stats()
            
        elif path == '/api/echo' and method == 'POST':
            response = await self.api_echo(receive)
            
        elif path == '/api/headers':
            response = self.api_headers(scope)
            
        elif path == '/api/large':
            response = self.api_large_response()
            
        elif path == '/api/slow':
            response = await self.api_slow()
            
        elif path == '/health':
            response = self.health_check()
            
        elif path.startswith('/static/'):
            response = self.serve_static(path)
            
        else:
            response = self.not_found(path)
            
        # Send response
        await response.send(send)
        
    def home_page(self) -> Response:
        """Home page with server information"""
        html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CovetPy HTTP/1.1 Server Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                .content { margin: 20px 0; }
                .feature { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .endpoint { background: #3498db; color: white; padding: 10px; margin: 5px 0; border-radius: 3px; }
                code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 CovetPy HTTP/1.1 Server</h1>
                <p>Production-Grade HTTP/1.1 Compliant Server</p>
            </div>
            
            <div class="content">
                <h2>Features</h2>
                <div class="feature">
                    <h3>✅ HTTP/1.1 RFC Compliance</h3>
                    <p>Full implementation of HTTP/1.1 standards (RFC 7230-7235)</p>
                </div>
                
                <div class="feature">
                    <h3>⚡ Keep-Alive Connections</h3>
                    <p>Persistent connections with configurable timeout</p>
                </div>
                
                <div class="feature">
                    <h3>📦 Chunked Transfer Encoding</h3>
                    <p>Streaming responses for large data</p>
                </div>
                
                <div class="feature">
                    <h3>🔒 Production Ready</h3>
                    <p>Connection pooling, error handling, and monitoring</p>
                </div>
                
                <h2>API Endpoints</h2>
                <div class="endpoint">GET /api/stats - Server statistics</div>
                <div class="endpoint">POST /api/echo - Echo request body</div>
                <div class="endpoint">GET /api/headers - Request headers</div>
                <div class="endpoint">GET /api/large - Large response test</div>
                <div class="endpoint">GET /api/slow - Slow response test</div>
                <div class="endpoint">GET /health - Health check</div>
                
                <h2>Test Commands</h2>
                <p>Try these curl commands:</p>
                <code>curl http://127.0.0.1:8000/api/stats</code><br>
                <code>curl -X POST -d '{"test":"data"}' http://127.0.0.1:8000/api/echo</code><br>
                <code>curl -H "X-Custom: test" http://127.0.0.1:8000/api/headers</code><br>
                <code>curl http://127.0.0.1:8000/api/large</code><br>
            </div>
        </body>
        </html>
        """
        return html_response(html)
        
    def api_stats(self) -> Response:
        """API endpoint returning server statistics"""
        uptime = time.time() - self.start_time
        
        stats = {
            "server": "CovetPy HTTP/1.1",
            "version": "1.0.0",
            "uptime_seconds": round(uptime, 2),
            "total_requests": self.request_count,
            "requests_per_second": round(self.request_count / uptime, 2) if uptime > 0 else 0,
            "features": {
                "http_version": "1.1",
                "keep_alive": True,
                "chunked_encoding": True,
                "connection_pooling": True,
                "zero_copy_optimization": True
            },
            "timestamp": time.time()
        }
        
        return json_response(stats)
        
    async def api_echo(self, receive) -> Response:
        """Echo the request body back"""
        message = await receive()
        body = message.get('body', b'')
        
        try:
            # Try to parse as JSON
            data = json.loads(body.decode('utf-8'))
            response_data = {
                "echo": data,
                "metadata": {
                    "body_size": len(body),
                    "content_type": "application/json",
                    "processed_at": time.time()
                }
            }
            return json_response(response_data)
            
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Return raw body
            return Response(
                content=body,
                status_code=200,
                headers={'Content-Type': 'application/octet-stream'}
            )
            
    def api_headers(self, scope) -> Response:
        """Return request headers"""
        headers = {}
        for name, value in scope.get('headers', []):
            name_str = name.decode() if isinstance(name, bytes) else name
            value_str = value.decode() if isinstance(value, bytes) else value
            headers[name_str] = value_str
            
        data = {
            "method": scope['method'],
            "path": scope['path'],
            "query_string": scope['query_string'].decode(),
            "headers": headers,
            "server_info": {
                "client": scope.get('client'),
                "server": scope.get('server')
            }
        }
        
        return json_response(data)
        
    def api_large_response(self) -> Response:
        """Return a large response for testing"""
        # Generate 1MB of data
        data = {
            "message": "Large response test",
            "size": "1MB",
            "data": ["CovetPy HTTP/1.1 Server - Large Response Test"] * 10000
        }
        
        return json_response(data)
        
    async def api_slow(self) -> Response:
        """Simulate a slow response"""
        await asyncio.sleep(2)  # 2 second delay
        
        data = {
            "message": "Slow response completed",
            "delay": "2 seconds",
            "timestamp": time.time()
        }
        
        return json_response(data)
        
    def health_check(self) -> Response:
        """Health check endpoint"""
        uptime = time.time() - self.start_time
        
        health = {
            "status": "healthy",
            "uptime": round(uptime, 2),
            "requests": self.request_count,
            "timestamp": time.time()
        }
        
        return json_response(health)
        
    def serve_static(self, path: str) -> Response:
        """Serve static content (placeholder)"""
        return text_response(f"Static file: {path}", status_code=404)
        
    def not_found(self, path: str) -> Response:
        """404 handler"""
        return json_response(
            {"error": "Not Found", "path": path, "message": "The requested resource was not found"},
            status_code=404
        )


async def run_demo():
    """Run the HTTP/1.1 server demo"""
    print("🚀 CovetPy HTTP/1.1 Server Demo")
    print("=" * 40)
    
    # Create demo application
    app = DemoApp()
    
    # Configure server for demo
    config = ServerConfig(
        host="127.0.0.1",
        port=8000,
        max_connections=1000,
        keep_alive_timeout=75,
        max_keep_alive_requests=1000,
        debug=True,
        access_log=True,
        server_name="CovetPy-Demo/1.0"
    )
    
    # Create and start server
    server = CovetHTTPServer(app, config)
    
    print(f"Starting server on http://{config.host}:{config.port}")
    print("\nFeatures enabled:")
    print("  ✅ HTTP/1.1 RFC Compliance")
    print("  ✅ Keep-Alive Connections") 
    print("  ✅ Chunked Transfer Encoding")
    print("  ✅ Connection Pooling")
    print("  ✅ Zero-Copy Optimizations")
    print("  ✅ Production Error Handling")
    
    print(f"\n🌐 Open http://{config.host}:{config.port} in your browser")
    print("📡 Try the API endpoints:")
    print(f"   curl http://{config.host}:{config.port}/api/stats")
    print(f"   curl -X POST -d '{{\"test\":\"data\"}}' http://{config.host}:{config.port}/api/echo")
    print(f"   curl http://{config.host}:{config.port}/health")
    
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
        await server.shutdown()
        print("✅ Server stopped successfully")


def main():
    """Main entry point"""
    try:
        asyncio.run(run_demo())
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()