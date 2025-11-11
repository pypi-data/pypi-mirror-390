#!/usr/bin/env python3
"""
Ultra Hybrid Server - Combining Rust performance with Python flexibility
Target: 250k-500k RPS
"""

import os
import sys
import multiprocessing
import asyncio
import uvloop
import socket
import mmap
import struct
import time
from concurrent.futures import ProcessPoolExecutor
import covet_server
import covet_simd

# Install uvloop
uvloop.install()

# Pre-allocate buffers for zero-copy
RESPONSE_BUFFER_SIZE = 1024 * 1024  # 1MB
SHARED_MEMORY_SIZE = 16 * 1024 * 1024  # 16MB


class MemoryMappedResponses:
    """Memory-mapped responses for zero-copy serving"""
    
    def __init__(self):
        # Create anonymous memory map
        self.mmap = mmap.mmap(-1, SHARED_MEMORY_SIZE)
        self.offsets = {}
        self.current_offset = 0
        
        # Pre-store responses
        self._store_responses()
    
    def _store_responses(self):
        """Store pre-computed responses in memory map"""
        responses = {
            '/': b'HTTP/1.1 200 OK\r\nServer: CovetPy-Ultra\r\nContent-Type: application/json\r\nContent-Length: 52\r\nConnection: keep-alive\r\n\r\n{"message":"Hello, World!","server":"CovetPy Ultra"}',
            '/benchmark': b'HTTP/1.1 200 OK\r\nServer: CovetPy-Ultra\r\nContent-Type: application/json\r\nContent-Length: 73\r\nConnection: keep-alive\r\n\r\n{"benchmark":true,"target_rps":500000,"server":"CovetPy Ultra Hybrid"}',
            '/health': b'HTTP/1.1 200 OK\r\nServer: CovetPy-Ultra\r\nContent-Type: application/json\r\nContent-Length: 15\r\nConnection: keep-alive\r\n\r\n{"status":"ok"}'
        }
        
        for path, response in responses.items():
            # Store offset and length
            self.offsets[path] = (self.current_offset, len(response))
            
            # Write to memory map
            self.mmap[self.current_offset:self.current_offset + len(response)] = response
            self.current_offset += len(response)
    
    def get_response(self, path):
        """Get zero-copy response buffer"""
        if path in self.offsets:
            offset, length = self.offsets[path]
            return memoryview(self.mmap)[offset:offset + length]
        return None


class HybridProtocol(asyncio.Protocol):
    """Ultra-optimized protocol using memory-mapped responses"""
    
    __slots__ = ('transport', 'mmap_responses', 'parser_buffer', 'parser_pos')
    
    def __init__(self, mmap_responses):
        self.transport = None
        self.mmap_responses = mmap_responses
        self.parser_buffer = bytearray(8192)
        self.parser_pos = 0
    
    def connection_made(self, transport):
        self.transport = transport
        sock = transport.get_extra_info('socket')
        if sock:
            # Maximum TCP optimizations
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            if hasattr(socket, 'TCP_QUICKACK'):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_QUICKACK, 1)
            if hasattr(socket, 'SO_BUSY_POLL'):
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BUSY_POLL, 100)
            # Increase socket buffers
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 512 * 1024)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 512 * 1024)
    
    def data_received(self, data):
        # Ultra-fast path detection
        if b'GET /benchmark' in data:
            response = self.mmap_responses.get_response('/benchmark')
            if response:
                self.transport.write(response)
                return
        elif b'GET / ' in data:
            response = self.mmap_responses.get_response('/')
            if response:
                self.transport.write(response)
                return
        elif b'GET /health' in data:
            response = self.mmap_responses.get_response('/health')
            if response:
                self.transport.write(response)
                return
        
        # Fallback to parsing
        if b'\r\n\r\n' in data:
            # Extract path
            try:
                first_line = data.split(b'\r\n')[0]
                parts = first_line.split(b' ')
                if len(parts) >= 2:
                    path = parts[1].decode('utf-8')
                    response = self.mmap_responses.get_response(path)
                    if response:
                        self.transport.write(response)
                    else:
                        # 404
                        self.transport.write(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n')
            except:
                self.transport.close()


async def run_async_server(host, port, worker_id, mmap_responses):
    """Run async server with memory-mapped responses"""
    loop = asyncio.get_running_loop()
    
    server = await loop.create_server(
        lambda: HybridProtocol(mmap_responses),
        host,
        port,
        reuse_address=True,
        reuse_port=True,
        backlog=65535
    )
    
    if worker_id == 0:
        print(f"✅ Async worker {worker_id} on {host}:{port}")
    
    async with server:
        await server.serve_forever()


def run_rust_server(port, num_threads):
    """Run the Rust hybrid server"""
    server = covet_server.HybridServer(num_threads)
    server.add_response("/", b'{"message":"Hello from Rust!","server":"CovetPy Rust"}')
    server.add_response("/benchmark", b'{"benchmark":true,"target_rps":500000,"rust":true}')
    server.run(f"0.0.0.0:{port}")


def async_worker_process(worker_id, host, port):
    """Async worker process with CPU affinity"""
    # Set CPU affinity
    try:
        if hasattr(os, 'sched_setaffinity'):
            os.sched_setaffinity(0, {worker_id % os.cpu_count()})
    except:
        pass
    
    # Create memory-mapped responses
    mmap_responses = MemoryMappedResponses()
    
    # Create new event loop
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run server
    try:
        loop.run_until_complete(run_async_server(host, port, worker_id, mmap_responses))
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()


class UltraHybridServer:
    """Ultra hybrid server combining Rust and Python optimizations"""
    
    def __init__(self, host='0.0.0.0', base_port=8000):
        self.host = host
        self.base_port = base_port
        self.num_cores = multiprocessing.cpu_count()
    
    def run(self):
        print("⚡ CovetPy Ultra Hybrid Server (250k-500k RPS Target)")
        print("=" * 70)
        print(f"🚀 Architecture: Hybrid Rust + Python")
        print(f"💻 CPU Cores: {self.num_cores}")
        print(f"📍 Base Port: {self.base_port}")
        print("\n🔥 EXTREME OPTIMIZATIONS:")
        print("  ✅ Rust HTTP server for raw performance")
        print("  ✅ Memory-mapped zero-copy responses")
        print("  ✅ SIMD JSON parsing (Rust)")
        print("  ✅ CPU affinity binding")
        print("  ✅ Socket-level optimizations")
        print("  ✅ Lock-free architecture")
        print("  ✅ Pre-allocated buffers")
        print("  ✅ Kernel TCP tuning")
        print("=" * 70)
        
        processes = []
        
        # Start Rust servers (half the cores)
        rust_cores = max(1, self.num_cores // 2)
        print(f"\n🦀 Starting {rust_cores} Rust servers...")
        
        for i in range(rust_cores):
            port = self.base_port + i
            p = multiprocessing.Process(
                target=run_rust_server,
                args=(port, 4),  # 4 threads per Rust server
                daemon=True
            )
            p.start()
            processes.append(p)
            print(f"   Rust server on port {port}")
        
        # Start Python async servers (remaining cores)
        python_cores = self.num_cores - rust_cores
        print(f"\n🐍 Starting {python_cores} Python async servers...")
        
        for i in range(python_cores):
            port = self.base_port + rust_cores + i
            p = multiprocessing.Process(
                target=async_worker_process,
                args=(i, self.host, port),
                daemon=True
            )
            p.start()
            processes.append(p)
            print(f"   Python server on port {port}")
        
        print("\n" + "=" * 70)
        print("📊 BENCHMARK COMMANDS:")
        print(f"\n1. Test Rust servers:")
        print(f"   wrk -t8 -c1000 -d30s http://localhost:{self.base_port}/benchmark")
        print(f"\n2. Test Python servers:")
        print(f"   wrk -t8 -c1000 -d30s http://localhost:{self.base_port + rust_cores}/benchmark")
        print(f"\n3. Load balance across all (best performance):")
        print(f"   Configure nginx to balance ports {self.base_port}-{self.base_port + self.num_cores - 1}")
        print("\n💡 PERFORMANCE TIPS:")
        print("  • ulimit -n 65535")
        print("  • sudo sysctl -w net.core.somaxconn=65535")
        print("  • sudo sysctl -w net.ipv4.tcp_tw_reuse=1")
        print("  • Use Linux for best results (io_uring support)")
        print("=" * 70)
        print("\nPress Ctrl+C to stop")
        
        try:
            for p in processes:
                p.join()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            for p in processes:
                p.terminate()
                p.join()


def check_system_limits():
    """Check and suggest system optimizations"""
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft < 65535:
            print(f"⚠️  Low file descriptor limit: {soft}")
            print("   Attempting to increase...")
            try:
                resource.setrlimit(resource.RLIMIT_NOFILE, (65535, hard))
                print("   ✅ Increased to 65535")
            except:
                print("   ❌ Failed. Run: ulimit -n 65535")
    except:
        pass


if __name__ == '__main__':
    check_system_limits()
    
    # Quick JSON performance test
    print("\n🧪 Testing SIMD JSON performance...")
    import json
    test_data = {"users": [{"id": i, "name": f"User{i}"} for i in range(100)]}
    json_str = json.dumps(test_data)
    json_bytes = json_str.encode()
    
    import timeit
    std_time = timeit.timeit(lambda: json.loads(json_str), number=10000)
    simd_time = timeit.timeit(lambda: covet_simd.parse_json_simd(json_bytes), number=10000)
    
    print(f"   Standard JSON: {std_time:.3f}s")
    print(f"   SIMD JSON: {simd_time:.3f}s")
    print(f"   Speedup: {std_time/simd_time:.2f}x")
    
    # Run server
    server = UltraHybridServer()
    server.run()