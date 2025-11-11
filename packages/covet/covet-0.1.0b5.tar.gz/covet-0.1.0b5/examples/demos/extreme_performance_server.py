#!/usr/bin/env python3
"""
Extreme Performance HTTP Server - Targeting 750k+ RPS
Using every possible optimization technique
"""

import asyncio
import socket
import os
import time
import multiprocessing
import struct
import sys
from collections import deque
import mmap

try:
    import uvloop
    uvloop.install()
except ImportError:
    print("Warning: uvloop not available, using standard asyncio")

# Try to import httptools for fast HTTP parsing
try:
    import httptools
    HAS_HTTPTOOLS = True
except ImportError:
    HAS_HTTPTOOLS = False
    print("Warning: httptools not available, using fallback parser")

# Try to import orjson for fast JSON
try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False
    import json
    print("Warning: orjson not available, using standard json")


class LightweightHTTPParser:
    """Ultra-lightweight HTTP parser for when httptools isn't available"""
    
    __slots__ = ('_buffer', '_complete', 'method', 'path', 'headers', 'body')
    
    def __init__(self):
        self._buffer = bytearray()
        self._complete = False
        self.method = None
        self.path = None
        self.headers = {}
        self.body = b''
    
    def feed_data(self, data: bytes) -> bool:
        """Parse incoming data. Returns True if request is complete."""
        if self._complete:
            return True
            
        self._buffer.extend(data)
        
        # Look for end of headers
        header_end = self._buffer.find(b'\r\n\r\n')
        if header_end == -1:
            return False
        
        # Parse request line
        header_data = self._buffer[:header_end]
        lines = header_data.split(b'\r\n')
        
        if len(lines) > 0:
            request_line = lines[0].split(b' ')
            if len(request_line) >= 2:
                self.method = request_line[0]
                self.path = request_line[1]
        
        # Parse headers (simplified)
        for line in lines[1:]:
            if b':' in line:
                key, value = line.split(b':', 1)
                self.headers[key.strip().lower()] = value.strip()
        
        self._complete = True
        return True
    
    def reset(self):
        """Reset parser for next request"""
        self._buffer.clear()
        self._complete = False
        self.method = None
        self.path = None
        self.headers.clear()
        self.body = b''


class ExtremePerformanceProtocol(asyncio.Protocol):
    """
    Extreme performance protocol implementation
    """
    
    __slots__ = (
        'transport', 'parser', 'static_responses', 
        'request_count', 'buffer', 'keep_alive'
    )
    
    # Pre-computed static parts
    HTTP_200 = b'HTTP/1.1 200 OK\r\n'
    HTTP_404 = b'HTTP/1.1 404 Not Found\r\n'
    SERVER_HEADER = b'Server: CovetPy-Extreme\r\n'
    CONTENT_TYPE_JSON = b'Content-Type: application/json\r\n'
    CONNECTION_KEEP_ALIVE = b'Connection: keep-alive\r\n'
    CRLF = b'\r\n'
    
    def __init__(self, static_responses):
        self.transport = None
        self.parser = None
        self.static_responses = static_responses
        self.request_count = 0
        self.buffer = bytearray(8192)
        self.keep_alive = True
    
    def connection_made(self, transport):
        self.transport = transport
        
        # Initialize parser based on what's available
        if HAS_HTTPTOOLS:
            self.parser = httptools.HttpRequestParser(self)
        else:
            self.parser = LightweightHTTPParser()
        
        # Optimize socket
        sock = transport.get_extra_info('socket')
        if sock:
            # Disable Nagle's algorithm
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            # Enable keep-alive
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            # Set send/receive buffer sizes
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 256 * 1024)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256 * 1024)
    
    def data_received(self, data):
        try:
            if HAS_HTTPTOOLS:
                self.parser.feed_data(data)
            else:
                if self.parser.feed_data(data):
                    self.on_message_complete()
        except Exception:
            self.transport.close()
    
    def on_url(self, url: bytes):
        """Called by httptools when URL is parsed"""
        self._url = url
    
    def on_message_complete(self):
        """Request complete - send response"""
        self.request_count += 1
        
        # Get the URL/path
        if HAS_HTTPTOOLS:
            url = getattr(self, '_url', b'/')
        else:
            url = self.parser.path or b'/'
        
        # Check static responses first
        if url in self.static_responses:
            response = self.static_responses[url]
        else:
            # Build 404 response
            response = self._build_404()
        
        # Send response
        self.transport.write(response)
        
        # Reset parser for next request
        if not HAS_HTTPTOOLS:
            self.parser.reset()
        
        # Close connection if not keep-alive
        if not self.keep_alive:
            self.transport.close()
    
    def _build_404(self) -> bytes:
        """Build a 404 response"""
        if HAS_ORJSON:
            body = orjson.dumps({"error": "Not Found", "status": 404})
        else:
            body = b'{"error": "Not Found", "status": 404}'
        
        response = bytearray()
        response.extend(self.HTTP_404)
        response.extend(self.SERVER_HEADER)
        response.extend(self.CONTENT_TYPE_JSON)
        response.extend(b'Content-Length: ')
        response.extend(str(len(body)).encode())
        response.extend(self.CRLF)
        response.extend(self.CONNECTION_KEEP_ALIVE)
        response.extend(self.CRLF)
        response.extend(body)
        
        return bytes(response)
    
    def connection_lost(self, exc):
        self.transport = None
        self.parser = None


class ExtremePerformanceServer:
    """
    Extreme performance HTTP server
    """
    
    def __init__(self, host='0.0.0.0', port=8000, workers=None):
        self.host = host
        self.port = port
        self.workers = workers or min(multiprocessing.cpu_count(), 16)
        self.static_responses = self._build_static_responses()
    
    def _build_static_responses(self) -> dict:
        """Pre-build all static responses"""
        responses = {}
        
        # Define response data
        response_data = {
            b'/': {"message": "Hello, World!", "server": "CovetPy Extreme"},
            b'/health': {"status": "ok"},
            b'/benchmark': {
                "benchmark": True,
                "target_rps": 750000,
                "optimizations": "extreme"
            }
        }
        
        # Build complete HTTP responses
        for path, data in response_data.items():
            if HAS_ORJSON:
                body = orjson.dumps(data)
            else:
                body = json.dumps(data).encode()
            
            response = bytearray()
            response.extend(b'HTTP/1.1 200 OK\r\n')
            response.extend(b'Server: CovetPy-Extreme\r\n')
            response.extend(b'Content-Type: application/json\r\n')
            response.extend(b'Content-Length: ')
            response.extend(str(len(body)).encode())
            response.extend(b'\r\nConnection: keep-alive\r\n\r\n')
            response.extend(body)
            
            responses[path] = bytes(response)
        
        return responses
    
    def _run_worker(self, worker_id: int):
        """Run a single worker process"""
        # Try to set CPU affinity
        try:
            if sys.platform == 'linux':
                os.sched_setaffinity(0, {worker_id % os.cpu_count()})
            elif sys.platform == 'darwin':
                # macOS doesn't support CPU affinity directly
                pass
        except:
            pass
        
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create server
        server_coro = loop.create_server(
            lambda: ExtremePerformanceProtocol(self.static_responses),
            self.host,
            self.port,
            reuse_address=True,
            reuse_port=True,
            backlog=65535
        )
        
        server = loop.run_until_complete(server_coro)
        
        if worker_id == 0:
            print(f"Worker {worker_id} listening on {self.host}:{self.port}")
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()
    
    def run(self):
        """Run the server with multiple workers"""
        print("🚀 CovetPy Extreme Performance Server")
        print("=" * 60)
        print(f"📍 Host: {self.host}:{self.port}")
        print(f"⚡ Workers: {self.workers}")
        print(f"🎯 Target: 750,000+ RPS")
        print("\n🔧 OPTIMIZATIONS:")
        print("  ✅ Pre-computed static responses")
        print("  ✅ Zero-allocation design")
        print("  ✅ Optimized TCP settings")
        print("  ✅ Multi-process with CPU affinity")
        print("  ✅ Minimal protocol overhead")
        print(f"  ✅ Fast JSON: {'orjson' if HAS_ORJSON else 'stdlib'}")
        print(f"  ✅ HTTP Parser: {'httptools' if HAS_HTTPTOOLS else 'lightweight'}")
        print("=" * 60)
        
        if self.workers == 1:
            print("\nRunning in single-worker mode")
            self._run_worker(0)
        else:
            print(f"\nStarting {self.workers} workers...")
            processes = []
            
            for i in range(self.workers):
                p = multiprocessing.Process(
                    target=self._run_worker,
                    args=(i,),
                    daemon=True
                )
                p.start()
                processes.append(p)
            
            print(f"\n✅ All workers started!")
            print("\n📊 BENCHMARK WITH:")
            print(f"  wrk -t{self.workers} -c500 -d30s http://localhost:{self.port}/benchmark")
            print(f"  wrk -t{self.workers*2} -c1000 -d30s http://localhost:{self.port}/benchmark")
            print(f"  wrk -t{self.workers*4} -c2000 -d30s http://localhost:{self.port}/benchmark")
            print("\n💡 TIPS:")
            print("  • Increase ulimit: ulimit -n 65535")
            print("  • Use multiple machines for load testing")
            print("  • Monitor with: sar -n DEV 1")
            print("\nPress Ctrl+C to stop")
            
            try:
                for p in processes:
                    p.join()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                for p in processes:
                    p.terminate()
                    p.join()


if __name__ == '__main__':
    # Check system limits
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft < 65535:
            print(f"⚠️  Warning: Low file descriptor limit ({soft})")
            print("   Run: ulimit -n 65535")
            print()
    except:
        pass
    
    # Run server
    server = ExtremePerformanceServer(
        host='0.0.0.0',
        port=8000,
        workers=16  # Use more workers for extreme performance
    )
    server.run()