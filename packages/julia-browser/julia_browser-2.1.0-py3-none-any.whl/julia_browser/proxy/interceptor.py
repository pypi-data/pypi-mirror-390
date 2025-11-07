"""
HTTP Intercepting Proxy Server

Provides Burp Suite-style request/response interception for AI agents to inspect
and manipulate HTTP traffic from the Julia browser.
"""

import threading
import time
import re
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


class DeclarativeRule:
    """
    Declarative rule for AI agents - no Python functions needed!
    
    Rules are simple dictionaries with 'match' and 'actions' keys.
    
    Example:
        {
            "name": "add_auth",
            "match": {"url_contains": "api"},
            "actions": {"set_headers": {"Authorization": "Bearer token"}}
        }
    """
    
    def __init__(self, rule_dict: Dict[str, Any]):
        self.name = rule_dict.get('name', 'unnamed_rule')
        self.match_conditions = rule_dict.get('match', {})
        self.actions = rule_dict.get('actions', {})
        self.rule_type = rule_dict.get('type', 'request')  # 'request' or 'response'
        self.enabled = True
    
    def matches_request(self, request: HTTPRequest) -> bool:
        """Check if request matches this rule's conditions"""
        if not self.match_conditions:
            return True  # No conditions = matches all
        
        for condition, value in self.match_conditions.items():
            if condition == 'url_contains':
                if value not in request.url:
                    return False
            elif condition == 'url_matches':
                if not re.search(value, request.url):
                    return False
            elif condition == 'method':
                if request.method.upper() != value.upper():
                    return False
            elif condition == 'header_equals':
                for header_name, header_value in value.items():
                    if request.headers.get(header_name) != header_value:
                        return False
            elif condition == 'header_contains':
                for header_name, search_value in value.items():
                    if search_value not in request.headers.get(header_name, ''):
                        return False
        
        return True
    
    def matches_response(self, request: HTTPRequest, response: HTTPResponse) -> bool:
        """Check if response matches this rule's conditions"""
        if not self.match_conditions:
            return True  # No conditions = matches all
        
        # Check request conditions
        if not self.matches_request(request):
            return False
        
        # Check response-specific conditions
        for condition, value in self.match_conditions.items():
            if condition == 'status_code':
                if response.status_code != value:
                    return False
            elif condition == 'content_type':
                content_type = response.headers.get('content-type', '')
                if value not in content_type:
                    return False
        
        return True
    
    def apply_to_request(self, request: HTTPRequest) -> HTTPRequest:
        """Apply actions to a request"""
        for action, value in self.actions.items():
            if action == 'set_headers':
                for header_name, header_value in value.items():
                    request.headers[header_name] = header_value
            elif action == 'remove_headers':
                for header_name in value:
                    request.headers.pop(header_name, None)
            elif action == 'set_method':
                request.method = value.upper()
            elif action == 'rewrite_url':
                for pattern, replacement in value.items():
                    request.url = re.sub(pattern, replacement, request.url)
            elif action == 'replace_body':
                request.body = value
            elif action == 'append_body':
                if request.body:
                    request.body += value
                else:
                    request.body = value
            elif action == 'find_replace':
                if request.body:
                    for pattern, replacement in value.items():
                        request.body = request.body.replace(pattern, replacement)
            elif action == 'block_request':
                # Mark request as blocked
                request.metadata['_blocked'] = True
        
        return request
    
    def apply_to_response(self, response: HTTPResponse) -> HTTPResponse:
        """Apply actions to a response"""
        for action, value in self.actions.items():
            if action == 'set_headers':
                for header_name, header_value in value.items():
                    response.headers[header_name] = header_value
            elif action == 'remove_headers':
                for header_name in value:
                    response.headers.pop(header_name, None)
            elif action == 'set_status':
                response.status_code = value
            elif action == 'replace_body':
                response.body = value
            elif action == 'append_body':
                if response.body:
                    response.body += value
                else:
                    response.body = value
            elif action == 'find_replace':
                if response.body:
                    for pattern, replacement in value.items():
                        response.body = response.body.replace(pattern, replacement)
        
        return response
    
    def to_dict(self) -> Dict:
        """Convert rule to dictionary"""
        return {
            'name': self.name,
            'type': self.rule_type,
            'match': self.match_conditions,
            'actions': self.actions,
            'enabled': self.enabled
        }


class DeclarativeRequestInterceptor(RequestInterceptor):
    """Request interceptor that uses declarative rules"""
    
    def __init__(self, rule: DeclarativeRule):
        super().__init__(name=rule.name)
        self.rule = rule
    
    def should_intercept(self, request: HTTPRequest) -> bool:
        return self.enabled and self.rule.enabled and self.rule.matches_request(request)
    
    def intercept(self, request: HTTPRequest) -> HTTPRequest:
        return self.rule.apply_to_request(request)


class DeclarativeResponseInterceptor(ResponseInterceptor):
    """Response interceptor that uses declarative rules"""
    
    def __init__(self, rule: DeclarativeRule):
        super().__init__(name=rule.name)
        self.rule = rule
    
    def should_intercept(self, request: HTTPRequest, response: HTTPResponse) -> bool:
        return self.enabled and self.rule.enabled and self.rule.matches_response(request, response)
    
    def intercept(self, request: HTTPRequest, response: HTTPResponse) -> HTTPResponse:
        return self.rule.apply_to_response(response)


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
        
        # Declarative rules storage
        self.rules: Dict[str, DeclarativeRule] = {}
        
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
    
    def add_declarative_rule(self, rule_dict: Dict[str, Any]) -> Dict:
        """
        Add a declarative rule - super simple for AI agents!
        
        Args:
            rule_dict: Rule configuration as dictionary
                {
                    "name": "rule_name",
                    "type": "request" or "response",
                    "match": {...},
                    "actions": {...}
                }
        
        Returns:
            Status dictionary
        """
        try:
            rule = DeclarativeRule(rule_dict)
            
            with self._lock:
                # Store the rule
                self.rules[rule.name] = rule
                
                # Create and register appropriate interceptor
                if rule.rule_type == 'response':
                    interceptor = DeclarativeResponseInterceptor(rule)
                    self.registry.add_response_interceptor(interceptor)
                else:
                    interceptor = DeclarativeRequestInterceptor(rule)
                    self.registry.add_request_interceptor(interceptor)
            
            return {
                'success': True,
                'message': f'Rule "{rule.name}" added successfully',
                'rule': rule.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_rule(self, rule_name: str) -> Dict:
        """Remove a declarative rule by name"""
        with self._lock:
            if rule_name in self.rules:
                rule = self.rules.pop(rule_name)
                
                # Remove from registry
                if rule.rule_type == 'response':
                    self.registry.remove_response_interceptor(rule_name)
                else:
                    self.registry.remove_request_interceptor(rule_name)
                
                return {
                    'success': True,
                    'message': f'Rule "{rule_name}" removed'
                }
            else:
                return {
                    'success': False,
                    'error': f'Rule "{rule_name}" not found'
                }
    
    def list_rules(self) -> List[Dict]:
        """List all declarative rules"""
        with self._lock:
            return [rule.to_dict() for rule in self.rules.values()]
    
    def get_traffic_log(self, limit: int = 100, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Get recent traffic log entries with optional filtering
        
        Args:
            limit: Maximum number of entries to return
            filter_dict: Optional filter conditions
                {
                    "url_contains": "api",
                    "method": "POST",
                    "status_code": 200
                }
            
        Returns:
            List of traffic log entries as dictionaries
        """
        with self._lock:
            logs = self.traffic_log
            
            # Apply filters if provided
            if filter_dict:
                filtered_logs = []
                for log in logs:
                    matches = True
                    
                    # Check URL filter
                    if 'url_contains' in filter_dict:
                        if filter_dict['url_contains'] not in log.request.url:
                            matches = False
                    
                    # Check method filter
                    if 'method' in filter_dict:
                        if log.request.method.upper() != filter_dict['method'].upper():
                            matches = False
                    
                    # Check status code filter
                    if 'status_code' in filter_dict and log.response:
                        if log.response.status_code != filter_dict['status_code']:
                            matches = False
                    
                    if matches:
                        filtered_logs.append(log)
                
                logs = filtered_logs
            
            # Apply limit
            recent_logs = logs[-limit:] if limit and len(logs) > limit else logs
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
