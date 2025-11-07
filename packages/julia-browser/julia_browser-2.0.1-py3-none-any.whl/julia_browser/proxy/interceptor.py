"""
HTTP Intercepting Proxy Server

Provides Burp Suite-style request/response interception for AI agents to inspect
and manipulate HTTP traffic from the Julia browser.
"""

import threading
import time
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import copy


@dataclass
class HTTPRequest:
    """Represents an HTTP request that can be inspected and modified"""
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert request to dictionary for agent inspection"""
        return {
            'method': self.method,
            'url': self.url,
            'headers': dict(self.headers),
            'body': self.body,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class HTTPResponse:
    """Represents an HTTP response that can be inspected and modified"""
    status_code: int
    headers: Dict[str, str]
    body: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert response to dictionary for agent inspection"""
        return {
            'status_code': self.status_code,
            'headers': dict(self.headers),
            'body': self.body[:1000] if self.body else None,  # Limit body preview
            'body_length': len(self.body) if self.body else 0,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class TrafficLog:
    """Log entry for HTTP request/response pair"""
    request: HTTPRequest
    response: Optional[HTTPResponse] = None
    intercepted: bool = False
    modified: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convert traffic log to dictionary"""
        return {
            'request': self.request.to_dict(),
            'response': self.response.to_dict() if self.response else None,
            'intercepted': self.intercepted,
            'modified': self.modified,
            'timestamp': self.timestamp.isoformat()
        }


class RequestInterceptor:
    """Base class for request interceptors"""
    
    def __init__(self, name: str = "RequestInterceptor"):
        self.name = name
        self.enabled = True
    
    def intercept(self, request: HTTPRequest) -> HTTPRequest:
        """
        Intercept and potentially modify an HTTP request
        
        Args:
            request: Original HTTP request
            
        Returns:
            Modified or original request
        """
        return request
    
    def should_intercept(self, request: HTTPRequest) -> bool:
        """
        Determine if this interceptor should process the request
        
        Args:
            request: HTTP request to check
            
        Returns:
            True if interceptor should process this request
        """
        return self.enabled


class ResponseInterceptor:
    """Base class for response interceptors"""
    
    def __init__(self, name: str = "ResponseInterceptor"):
        self.name = name
        self.enabled = True
    
    def intercept(self, request: HTTPRequest, response: HTTPResponse) -> HTTPResponse:
        """
        Intercept and potentially modify an HTTP response
        
        Args:
            request: Original HTTP request
            response: Original HTTP response
            
        Returns:
            Modified or original response
        """
        return response
    
    def should_intercept(self, request: HTTPRequest, response: HTTPResponse) -> bool:
        """
        Determine if this interceptor should process the response
        
        Args:
            request: HTTP request that generated this response
            response: HTTP response to check
            
        Returns:
            True if interceptor should process this response
        """
        return self.enabled


class InterceptorRegistry:
    """Registry for managing request and response interceptors"""
    
    def __init__(self):
        self.request_interceptors: List[RequestInterceptor] = []
        self.response_interceptors: List[ResponseInterceptor] = []
        self._lock = threading.Lock()
    
    def add_request_interceptor(self, interceptor: RequestInterceptor) -> None:
        """Add a request interceptor"""
        with self._lock:
            self.request_interceptors.append(interceptor)
    
    def add_response_interceptor(self, interceptor: ResponseInterceptor) -> None:
        """Add a response interceptor"""
        with self._lock:
            self.response_interceptors.append(interceptor)
    
    def remove_request_interceptor(self, name: str) -> bool:
        """Remove a request interceptor by name"""
        with self._lock:
            before_count = len(self.request_interceptors)
            self.request_interceptors = [i for i in self.request_interceptors if i.name != name]
            return len(self.request_interceptors) < before_count
    
    def remove_response_interceptor(self, name: str) -> bool:
        """Remove a response interceptor by name"""
        with self._lock:
            before_count = len(self.response_interceptors)
            self.response_interceptors = [i for i in self.response_interceptors if i.name != name]
            return len(self.response_interceptors) < before_count
    
    def clear_all(self) -> None:
        """Remove all interceptors"""
        with self._lock:
            self.request_interceptors.clear()
            self.response_interceptors.clear()
    
    def get_interceptor_info(self) -> Dict:
        """Get information about registered interceptors"""
        with self._lock:
            return {
                'request_interceptors': [
                    {'name': i.name, 'enabled': i.enabled} 
                    for i in self.request_interceptors
                ],
                'response_interceptors': [
                    {'name': i.name, 'enabled': i.enabled}
                    for i in self.response_interceptors
                ]
            }


class ProxyServer:
    """
    HTTP Intercepting Proxy Server
    
    Provides Burp Suite-style capabilities for intercepting and manipulating
    HTTP requests and responses from the Julia browser.
    """
    
    def __init__(self):
        self.enabled = False
        self.registry = InterceptorRegistry()
        self.traffic_log: List[TrafficLog] = []
        self.max_log_size = 1000  # Maximum number of traffic logs to keep
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'total_responses': 0,
            'intercepted_requests': 0,
            'intercepted_responses': 0,
            'modified_requests': 0,
            'modified_responses': 0
        }
    
    def start(self) -> None:
        """Start the proxy server"""
        self.enabled = True
    
    def stop(self) -> None:
        """Stop the proxy server"""
        self.enabled = False
    
    def is_running(self) -> bool:
        """Check if proxy is running"""
        return self.enabled
    
    def intercept_request(self, method: str, url: str, headers: Dict[str, str], 
                         body: Optional[str] = None) -> HTTPRequest:
        """
        Intercept an outgoing HTTP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            body: Request body (optional)
            
        Returns:
            Potentially modified HTTP request
        """
        if not self.enabled:
            return HTTPRequest(method=method, url=url, headers=headers, body=body)
        
        with self._lock:
            self.stats['total_requests'] += 1
        
        # Create request object
        request = HTTPRequest(
            method=method,
            url=url,
            headers=copy.deepcopy(headers),
            body=body
        )
        
        original_request = copy.deepcopy(request)
        intercepted = False
        
        # Apply request interceptors
        for interceptor in self.registry.request_interceptors:
            if interceptor.should_intercept(request):
                intercepted = True
                request = interceptor.intercept(request)
        
        # Track modifications
        modified = (
            request.method != original_request.method or
            request.url != original_request.url or
            request.headers != original_request.headers or
            request.body != original_request.body
        )
        
        if intercepted:
            with self._lock:
                self.stats['intercepted_requests'] += 1
                if modified:
                    self.stats['modified_requests'] += 1
        
        # Log the request
        self._add_traffic_log(TrafficLog(
            request=request,
            intercepted=intercepted,
            modified=modified
        ))
        
        return request
    
    def intercept_response(self, request: HTTPRequest, status_code: int, 
                          headers: Dict[str, str], body: Optional[str] = None) -> HTTPResponse:
        """
        Intercept an incoming HTTP response
        
        Args:
            request: Original HTTP request
            status_code: Response status code
            headers: Response headers
            body: Response body (optional)
            
        Returns:
            Potentially modified HTTP response
        """
        if not self.enabled:
            return HTTPResponse(status_code=status_code, headers=headers, body=body)
        
        with self._lock:
            self.stats['total_responses'] += 1
        
        # Create response object
        response = HTTPResponse(
            status_code=status_code,
            headers=copy.deepcopy(headers),
            body=body
        )
        
        original_response = copy.deepcopy(response)
        intercepted = False
        
        # Apply response interceptors
        for interceptor in self.registry.response_interceptors:
            if interceptor.should_intercept(request, response):
                intercepted = True
                response = interceptor.intercept(request, response)
        
        # Track modifications
        modified = (
            response.status_code != original_response.status_code or
            response.headers != original_response.headers or
            response.body != original_response.body
        )
        
        if intercepted:
            with self._lock:
                self.stats['intercepted_responses'] += 1
                if modified:
                    self.stats['modified_responses'] += 1
        
        # Update traffic log with response
        self._update_traffic_log_with_response(request, response, intercepted, modified)
        
        return response
    
    def _add_traffic_log(self, log: TrafficLog) -> None:
        """Add a traffic log entry"""
        with self._lock:
            self.traffic_log.append(log)
            
            # Trim log if needed
            if len(self.traffic_log) > self.max_log_size:
                self.traffic_log = self.traffic_log[-self.max_log_size:]
    
    def _update_traffic_log_with_response(self, request: HTTPRequest, response: HTTPResponse,
                                         intercepted: bool, modified: bool) -> None:
        """Update traffic log with response information"""
        with self._lock:
            # Find the matching request in the log
            for log in reversed(self.traffic_log):
                if (log.request.url == request.url and 
                    log.request.method == request.method and
                    log.response is None):
                    log.response = response
                    log.intercepted = log.intercepted or intercepted
                    log.modified = log.modified or modified
                    break
    
    def get_traffic_log(self, limit: int = 100) -> List[Dict]:
        """
        Get recent traffic log entries
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of traffic log entries as dictionaries
        """
        with self._lock:
            recent_logs = self.traffic_log[-limit:] if limit else self.traffic_log
            return [log.to_dict() for log in recent_logs]
    
    def get_stats(self) -> Dict:
        """Get proxy statistics"""
        with self._lock:
            return copy.deepcopy(self.stats)
    
    def clear_traffic_log(self) -> None:
        """Clear all traffic logs"""
        with self._lock:
            self.traffic_log.clear()
    
    def reset_stats(self) -> None:
        """Reset all statistics"""
        with self._lock:
            for key in self.stats:
                self.stats[key] = 0
    
    def get_status(self) -> Dict:
        """Get comprehensive proxy status"""
        return {
            'enabled': self.enabled,
            'stats': self.get_stats(),
            'interceptors': self.registry.get_interceptor_info(),
            'traffic_log_size': len(self.traffic_log)
        }
