#!/usr/bin/env python3
"""
Network-Level Interceptor
Monitors HTTP/HTTPS traffic to AI API endpoints
Works without any code changes - intercepts at network level
"""

import os
import sys
import json
import ssl
import socket
import threading
from urllib.parse import urlparse
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# AI Provider endpoints
AI_ENDPOINTS = {
    "api.openai.com": "openai",
    "api.perplexity.ai": "perplexity",
    "api.x.ai": "grok",
    "api.anthropic.com": "anthropic",
    "generativelanguage.googleapis.com": "google",
    "api.cohere.ai": "cohere",
    "api.mistral.ai": "mistral",
}


class NetworkInterceptor:
    """Intercept network traffic to AI endpoints"""
    
    def __init__(self, tracker_url: str = "http://localhost:8888"):
        self.tracker_url = tracker_url
        self.intercepting = False
        self._original_socket = None
    
    def _is_ai_endpoint(self, hostname: str) -> Optional[str]:
        """Check if hostname is an AI API endpoint"""
        for endpoint, provider in AI_ENDPOINTS.items():
            if endpoint in hostname:
                return provider
        return None
    
    def _track_request(self, provider: str, hostname: str, path: str, method: str, data: bytes):
        """Track intercepted request"""
        try:
            import requests
            
            # Extract API key from headers if possible
            api_key = "intercepted"  # Can't easily extract from socket level
            
            # Estimate cost (simplified)
            cost = 0.01  # Default estimate
            
            tracking_data = {
                "provider": provider,
                "api_key": api_key,
                "service_name": "network_intercepted",
                "language": "network",
                "api_type": "http",
                "model": "unknown",
                "operation": f"{method} {path}",
                "cost_usd": cost,
                "request_size": len(data) if data else 0,
            }
            
            requests.post(
                f"{self.tracker_url}/api/track",
                json=tracking_data,
                timeout=1
            )
        except Exception as e:
            logger.debug(f"Failed to track intercepted request: {e}")
    
    def start(self):
        """Start network interception"""
        # Note: This is a simplified version
        # Full implementation would require:
        # - Proxy server setup
        # - SSL/TLS interception
        # - Request/response parsing
        # - More complex architecture
        
        logger.warning("Network-level interception requires proxy setup")
        logger.info("For automatic tracking, use auto_interceptor.py instead")
        logger.info("Or set up a proxy server (mitmproxy, etc.)")


# Simpler approach: HTTP Proxy Middleware
class ProxyInterceptor:
    """HTTP Proxy that intercepts AI API calls"""
    
    def __init__(self, tracker_url: str = "http://localhost:8888", port: int = 8080):
        self.tracker_url = tracker_url
        self.port = port
    
    def start(self):
        """Start proxy server"""
        try:
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import urllib.request
            
            class ProxyHandler(BaseHTTPRequestHandler):
                def do_POST(self):
                    # Intercept POST requests
                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length)
                    
                    # Check if this is an AI API call
                    host = self.headers.get('Host', '')
                    provider = None
                    for endpoint, prov in AI_ENDPOINTS.items():
                        if endpoint in host:
                            provider = prov
                            break
                    
                    if provider:
                        # Track the call
                        self._track_call(provider, host, self.path, body)
                    
                    # Forward request
                    req = urllib.request.Request(
                        f"https://{host}{self.path}",
                        data=body,
                        headers=dict(self.headers)
                    )
                    response = urllib.request.urlopen(req)
                    
                    # Send response back
                    self.send_response(response.status)
                    for header, value in response.headers.items():
                        self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(response.read())
                
                def _track_call(self, provider, host, path, body):
                    try:
                        import requests
                        requests.post(
                            f"{self.tracker_url}/api/track",
                            json={
                                "provider": provider,
                                "api_key": "intercepted",
                                "service_name": "proxy_intercepted",
                                "language": "network",
                                "api_type": "http",
                                "operation": f"POST {path}",
                                "cost_usd": 0.01,
                            },
                            timeout=1
                        )
                    except:
                        pass
                
                def log_message(self, format, *args):
                    pass  # Suppress proxy logs
            
            server = HTTPServer(('localhost', self.port), ProxyHandler)
            logger.info(f"🌐 Proxy server started on port {self.port}")
            logger.info(f"Configure your apps to use proxy: http://localhost:{self.port}")
            server.serve_forever()
            
        except Exception as e:
            logger.error(f"Failed to start proxy: {e}")


if __name__ == "__main__":
    # Start proxy
    proxy = ProxyInterceptor()
    proxy.start()

