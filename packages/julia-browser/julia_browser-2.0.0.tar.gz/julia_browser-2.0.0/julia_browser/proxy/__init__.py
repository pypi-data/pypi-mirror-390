"""
Julia Browser Proxy Module

Provides HTTP intercepting proxy capabilities for AI agents to inspect and manipulate
web traffic similar to Burp Suite.
"""

from .interceptor import ProxyServer, InterceptorRegistry, RequestInterceptor, ResponseInterceptor

__all__ = [
    'ProxyServer',
    'InterceptorRegistry', 
    'RequestInterceptor',
    'ResponseInterceptor'
]
