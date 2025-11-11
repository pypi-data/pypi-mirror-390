#!/usr/bin/env python3
"""
Zero-Dependency CovetPy Demo App
Demonstrates TRUE zero-dependency web framework
"""

import asyncio
import json
import socket
from datetime import datetime

class ZeroDepCovetApp:
    def __init__(self):
        self.routes = {}
    
    def get(self, path):
        def decorator(handler):
            self.routes[f"GET:{path}"] = handler
            return handler
        return decorator
    
    def json_response(self, data, status=200):
        body = json.dumps(data, default=str).encode()
        response = f"HTTP/1.1 {status} OK\r\n"
        response += "Content-Type: application/json\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "\r\n"
        return response.encode() + body
    
    async def handle_request(self, reader, writer):
        try:
            data = await reader.read(1024)
            request_line = data.decode().split('\r\n')[0]
            method, path, _ = request_line.split(' ')
            
            route_key = f"{method}:{path}"
            if route_key in self.routes:
                response_data = self.routes[route_key]()
                writer.write(response_data)
            else:
                writer.write(b"HTTP/1.1 404 Not Found\r\n\r\n")
            
            await writer.drain()
        except:
            pass
        finally:
            writer.close()
    
    async def run(self, host='127.0.0.1', port=8000):
        server = await asyncio.start_server(self.handle_request, host, port)
        print(f"Zero-Dependency CovetPy running on http://{host}:{port}")
        async with server:
            await server.serve_forever()

# Create demo app
app = ZeroDepCovetApp()

@app.get("/")
def home():
    return app.json_response({
        "message": "Hello from TRULY Zero-Dependency CovetPy!",
        "framework": "CovetPy",
        "dependencies": 0,
        "timestamp": datetime.now().isoformat(),
        "proof": "Uses only Python standard library"
    })

@app.get("/health")
def health():
    return app.json_response({
        "status": "healthy",
        "dependencies": [],
        "external_packages": 0
    })

if __name__ == "__main__":
    print("Starting Zero-Dependency CovetPy Demo...")
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nDemo stopped")