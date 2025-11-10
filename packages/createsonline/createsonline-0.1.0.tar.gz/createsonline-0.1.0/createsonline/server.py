# createsonline/server.py
"""
CREATESONLINE Pure Python HTTP Server

Zero external dependencies - runs ASGI apps with just Python stdlib.
This eliminates the need for uvicorn.
"""

import asyncio
import socket
import json
import time
from datetime import datetime
from typing import Callable
from urllib.parse import parse_qs, urlparse
import logging`n`nlogger = logging.getLogger("createsonline.server")`n

class CreatesonlineServer:
    """Pure Python HTTP server for ASGI applications"""
    
    def __init__(self, app: Callable, host: str = "127.0.0.1", port: int = 8000):
        self.app = app
        self.host = host
        self.port = port
        self.server = None
        
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle individual client connection"""
        start_time = time.time()
        response_size = 0
        status_code = 500
        
        try:
            # Read HTTP request
            request_line = await reader.readline()
            if not request_line:
                return
                
            request_line = request_line.decode('utf-8').strip()
            method, path, _ = request_line.split(' ', 2)
            
            # Read headers
            headers = {}
            while True:
                line = await reader.readline()
                if line == b'\r\n':
                    break
                if line:
                    key, value = line.decode('utf-8').strip().split(':', 1)
                    headers[key.lower()] = value.strip()
            
            # Read body if present
            body = b''
            if 'content-length' in headers:
                content_length = int(headers['content-length'])
                body = await reader.readexactly(content_length)
            
            # Parse URL
            parsed_url = urlparse(path)
            query_string = parsed_url.query.encode() if parsed_url.query else b''
            
            # Build ASGI scope
            scope = {
                'type': 'http',
                'asgi': {'version': '3.0'},
                'http_version': '1.1',
                'method': method,
                'scheme': 'http',
                'path': parsed_url.path,
                'query_string': query_string,
                'root_path': '',
                'headers': [[k.encode(), v.encode()] for k, v in headers.items()],
                'server': (self.host, self.port),
            }
            
            # ASGI receive callable
            body_sent = False
            async def receive():
                nonlocal body_sent
                if not body_sent:
                    body_sent = True
                    return {
                        'type': 'http.request',
                        'body': body,
                        'more_body': False,
                    }
                return {'type': 'http.disconnect'}
            
            # ASGI send callable
            response_started = False
            async def send(message):
                nonlocal response_started, response_size, status_code
                
                if message['type'] == 'http.response.start':
                    response_started = True
                    status_code = message['status']
                    headers = message.get('headers', [])
                    
                    # Write status line
                    writer.write(f'HTTP/1.1 {status_code} OK\r\n'.encode())
                    
                    # Write headers
                    for name, value in headers:
                        writer.write(f'{name.decode()}: {value.decode()}\r\n'.encode())
                    writer.write(b'\r\n')
                    
                elif message['type'] == 'http.response.body':
                    body = message.get('body', b'')
                    if body:
                        response_size += len(body)
                        writer.write(body)
                    await writer.drain()
            
            # Call ASGI app
            await self.app(scope, receive, send)
            
            # Log request after completion
            elapsed_ms = (time.time() - start_time) * 1000
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status_indicator = self._get_status_indicator(status_code)
            
            # Format size
            if response_size < 1024:
                size_str = f"{response_size}B"
            elif response_size < 1024 * 1024:
                size_str = f"{response_size / 1024:.1f}KB"
            else:
                size_str = f"{response_size / (1024 * 1024):.1f}MB"
            logger.info(f"[{timestamp}] [{status_indicator}] {method:6} {path:40} {status_code} {size_str:>8} {elapsed_ms:>6.0f}ms")
        except Exception as e:
            # Log error to console
            elapsed_ms = (time.time() - start_time) * 1000
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.error(f"[{timestamp}] [X] {method:6} {path:40} 500 ERROR   {elapsed_ms:>6.0f}ms - {str(e)}")
            # Send 500 error
            error_response = json.dumps({
                "error": "Internal Server Error",
                "message": str(e)
            }).encode()
            
            response = (
                b'HTTP/1.1 500 Internal Server Error\r\n'
                b'Content-Type: application/json\r\n'
                b'Content-Length: ' + str(len(error_response)).encode() + b'\r\n'
                b'\r\n'
            ) + error_response
            
            writer.write(response)
            await writer.drain()
        
        finally:
            writer.close()
            await writer.wait_closed()
    
    def _get_status_indicator(self, status: int) -> str:
        """Get visual indicator for HTTP status code"""
        if 200 <= status < 300:
            return "Ã¢Å“â€œ"  # Success
        elif 300 <= status < 400:
            return "Ã¢â€ â€™"  # Redirect
        elif 400 <= status < 500:
            return "!"  # Client error
        else:
            return "Ã¢Å“â€”"  # Server error
    
    async def serve(self):
        """Start the server"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        
        # Print server info
        startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info("=" * 60)
        logger.info("CREATESONLINE v0.1.0")
        logger.info(f"Started: {startup_time}")
        logger.info(f"Listening on http://{self.host}:{self.port}")
        logger.info("=" * 60)
        
        
        async with self.server:
            await self.server.serve_forever()
    
    def run(self):
        """Run the server (blocking)"""
        try:
            asyncio.run(self.serve())
        except KeyboardInterrupt:
            logger.info("Server stopped")
def run_server(app: Callable, host: str = "127.0.0.1", port: int = 8000):
    """
    Run CREATESONLINE pure Python server
    
    Args:
        app: ASGI application callable
        host: Host to bind to
        port: Port to listen on
    """
    server = CreatesonlineServer(app, host, port)
    server.run()

