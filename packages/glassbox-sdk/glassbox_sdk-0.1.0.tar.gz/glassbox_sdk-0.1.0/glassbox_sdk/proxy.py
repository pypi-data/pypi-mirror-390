"""
HTTP Proxy Server for Zero-Code Glassbox Integration
Intercepts AI API calls and logs them automatically without code changes.
"""

import time
import json
import threading
import socket
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from .logger import get_logger, init
from .http_interceptor import is_ai_api_call, extract_tokens_from_response, extract_model_from_request
from .utils import calculate_cost, generate_prompt_id, get_timestamp, validate_output


class ProxyRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler that intercepts and logs AI API calls."""
    
    def __init__(self, *args, logger=None, **kwargs):
        self.logger = logger
        super().__init__(*args, **kwargs)
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_CONNECT(self):
        """Handle CONNECT method for HTTPS tunneling."""
        try:
            # Parse the target host and port from the path
            # Format: hostname:port
            host_port = self.path.split(':')
            if len(host_port) != 2:
                self.send_error(400, "Invalid CONNECT request")
                return
            
            host = host_port[0]
            port = int(host_port[1])
            
            # Connect to the target server
            try:
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.settimeout(10)
                target_socket.connect((host, port))
            except Exception as e:
                self.send_error(502, f"Failed to connect to {host}:{port}: {str(e)}")
                return
            
            # Send 200 Connection Established
            self.send_response(200, 'Connection Established')
            self.end_headers()
            
            # Tunnel the connection - forward data bidirectionally
            import select
            
            def tunnel():
                try:
                    while True:
                        # Check if client has data
                        if select.select([self.connection], [], [], 0.1)[0]:
                            data = self.connection.recv(8192)
                            if not data:
                                break
                            target_socket.sendall(data)
                        
                        # Check if target has data
                        if select.select([target_socket], [], [], 0.1)[0]:
                            data = target_socket.recv(8192)
                            if not data:
                                break
                            self.connection.sendall(data)
                except (OSError, socket.error, ConnectionError, BrokenPipeError, EOFError):
                    # Network errors in tunneling - non-fatal, connection closed
                    pass
                finally:
                    try:
                        target_socket.close()
                    except:
                        pass
                    try:
                        self.connection.close()
                    except:
                        pass
            
            # Start tunneling in a separate thread
            tunnel_thread = threading.Thread(target=tunnel, daemon=True)
            tunnel_thread.start()
            
        except Exception as e:
            self.send_error(500, f"HTTPS tunneling error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests."""
        self._handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests."""
        self._handle_request('POST')
    
    def do_PUT(self):
        """Handle PUT requests."""
        self._handle_request('PUT')
    
    def do_PATCH(self):
        """Handle PATCH requests."""
        self._handle_request('PATCH')
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        self._handle_request('DELETE')
    
    def _handle_request(self, method: str):
        """Handle any HTTP request method."""
        try:
            # Parse request URL
            # For proxy requests, path may be absolute URL (http://host/path)
            # or relative path (/path) with Host header
            url = self.path
            
            # Check if path is absolute URL (proxy-style request)
            if url.startswith('http://') or url.startswith('https://'):
                # Already a full URL
                pass
            else:
                # Relative path - reconstruct from Host header
                host = self.headers.get('Host', '')
                if not host:
                    self.send_error(400, "Missing Host header")
                    return
                # Determine protocol (default to http, but could be https)
                protocol = 'http'
                if 'https' in self.headers.get('X-Forwarded-Proto', '').lower():
                    protocol = 'https'
                url = f"{protocol}://{host}{url}"
            
            # Check if this is an AI API call
            is_ai, provider = is_ai_api_call(url, method)
            
            if is_ai:
                # This is an AI API call - intercept and log it
                self._handle_ai_request(url, method, provider)
            else:
                # Regular request - forward as-is
                self._forward_request(url, method)
        
        except Exception as e:
            self.send_error(500, f"Proxy error: {str(e)}")
    
    def _handle_ai_request(self, url: str, method: str, provider: str):
        """Handle an AI API call - intercept, log, and forward."""
        start_time = time.time()
        prompt_id = generate_prompt_id()
        
        # Read request body
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Parse request data
        request_data = {}
        if body:
            try:
                request_data = json.loads(body.decode('utf-8'))
            except (UnicodeDecodeError, json.JSONDecodeError):
                try:
                    request_data = json.loads(body)
                except (TypeError, json.JSONDecodeError):
                    request_data = {}
        
        # Extract model from request
        model = extract_model_from_request(request_data, provider or 'unknown')
        
        # Prepare headers for forwarding
        headers = {}
        for key, value in self.headers.items():
            # Skip proxy-specific headers
            if key.lower() not in ['host', 'connection', 'proxy-connection', 'proxy-authorization']:
                headers[key] = value
        
        # Forward request to actual API
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=30,
                allow_redirects=False
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Parse response
            try:
                response_data = response.json()
            except (ValueError, json.JSONDecodeError):
                # Response is not JSON, use text
                response_data = response.text
            
            # Extract tokens and calculate cost
            input_tokens, output_tokens = extract_tokens_from_response(response_data, provider or 'unknown')
            cost_usd = calculate_cost(model, input_tokens, output_tokens)
            valid = validate_output(response_data)
            
            # Log to Glassbox
            if self.logger:
                try:
                    self.logger.log(
                        model=model,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        latency_ms=latency_ms,
                        cost_usd=cost_usd,
                        valid=valid,
                        prompt_id=prompt_id
                    )
                except (AttributeError, ValueError, TypeError, KeyError) as e:
                    # Logging errors - don't break proxy functionality
                    pass
            
            # Send response back to client
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                # Skip headers that shouldn't be forwarded
                if header.lower() not in ['connection', 'transfer-encoding', 'content-encoding', 'content-length']:
                    self.send_header(header, value)
            # Add content-length if not chunked
            if 'transfer-encoding' not in response.headers.get('transfer-encoding', '').lower():
                self.send_header('Content-Length', str(len(response.content)))
            self.end_headers()
            self.wfile.write(response.content)
            self.wfile.flush()
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            # Log error
            if self.logger:
                try:
                    self.logger.log(
                        model=model,
                        input_tokens=0,
                        output_tokens=0,
                        latency_ms=latency_ms,
                        cost_usd=0.0,
                        valid=False,
                        prompt_id=prompt_id
                    )
                except (AttributeError, ValueError, TypeError) as e:
                    # Logging failed - non-fatal, don't break error handling
                    pass
            
            self.send_error(502, f"Proxy forwarding error: {str(e)}")
    
    def _forward_request(self, url: str, method: str):
        """Forward a non-AI request as-is."""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Prepare headers
            headers = {}
            for key, value in self.headers.items():
                # Skip proxy-specific headers
                if key.lower() not in ['host', 'connection', 'proxy-connection', 'proxy-authorization']:
                    headers[key] = value
            
            # Forward request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=30,
                allow_redirects=False
            )
            
            # Send response back
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                # Skip headers that shouldn't be forwarded
                if header.lower() not in ['connection', 'transfer-encoding', 'content-encoding', 'content-length']:
                    self.send_header(header, value)
            # Add content-length if not chunked
            if 'transfer-encoding' not in response.headers.get('transfer-encoding', '').lower():
                self.send_header('Content-Length', str(len(response.content)))
            self.end_headers()
            self.wfile.write(response.content)
            self.wfile.flush()
            
        except Exception as e:
            self.send_error(502, f"Proxy forwarding error: {str(e)}")


class GlassboxProxy:
    """HTTP proxy server that intercepts AI API calls."""
    
    def __init__(
        self,
        port: int = 5000,
        app_id: Optional[str] = None,
        backend_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.port = port
        self.logger = None
        self.server = None
        self.running = False
        
        # Initialize logger
        self.logger = init(
            app_id=app_id or 'proxy-app',
            backend_url=backend_url,
            api_key=api_key,
            sync_enabled=True,
            auto_wrap=False  # Don't auto-wrap when using proxy
        )
    
    def _make_handler(self):
        """Create request handler with logger."""
        def handler(*args, **kwargs):
            return ProxyRequestHandler(*args, logger=self.logger, **kwargs)
        return handler
    
    def start(self, auto_configure: bool = False):
        """Start the proxy server."""
        try:
            handler = self._make_handler()
            self.server = HTTPServer(('localhost', self.port), handler)
            self.running = True
            
            proxy_url = f"http://localhost:{self.port}"
            
            # Auto-configure environment if requested
            if auto_configure:
                import os
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
                print(f"✅ Proxy configured automatically!")
                print(f"   HTTP_PROXY={proxy_url}")
                print(f"   HTTPS_PROXY={proxy_url}")
                print()
            
            print(f"🚀 Glassbox Proxy running on {proxy_url}")
            print()
            
            if not auto_configure:
                print("📝 Configure your app to use this proxy:")
                print(f"   export HTTP_PROXY={proxy_url}")
                print(f"   export HTTPS_PROXY={proxy_url}")
                print()
                print("   Or set in your code:")
                print(f"   import os")
                print(f"   os.environ['HTTP_PROXY'] = '{proxy_url}'")
                print(f"   os.environ['HTTPS_PROXY'] = '{proxy_url}'")
                print()
            
            print("✨ AI API calls will be automatically logged!")
            print()
            print("⚠️  Note: HTTPS connections are tunneled but encrypted traffic")
            print("   cannot be intercepted. For full HTTPS support, use SDK integration:")
            print("   import glassbox; glassbox.init()")
            print()
            print("   Press Ctrl+C to stop")
            print()
            
            # Start server in a thread
            def run_server():
                self.server.serve_forever()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            return True
            
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"❌ Port {self.port} is already in use")
                print(f"   Try: glassbox proxy --port {self.port + 1}")
            else:
                print(f"❌ Failed to start proxy: {e}")
            return False
    
    def stop(self):
        """Stop the proxy server."""
        if self.server:
            self.server.shutdown()
            self.running = False


def start_proxy(
    port: int = 5000,
    app_id: Optional[str] = None,
    backend_url: Optional[str] = None,
    api_key: Optional[str] = None
) -> GlassboxProxy:
    """Start a Glassbox proxy server."""
    proxy = GlassboxProxy(port=port, app_id=app_id, backend_url=backend_url, api_key=api_key)
    if proxy.start():
        return proxy
    return None

