"""
Browser Engine - Core functionality for web browsing
Handles HTTP requests, HTML parsing, and coordinate rendering pipeline
"""

import requests
import urllib.parse
import json
from typing import Dict, List, Optional, Tuple, Union, Any
from bs4 import BeautifulSoup
import re
import time

from .renderer import HTMLRenderer
from .js_engine import JavaScriptEngine
from .css_parser import CSSParser

try:
    from ..proxy import ProxyServer
except ImportError:
    from julia_browser.proxy import ProxyServer


class BrowserEngine:
    """Core browser engine that handles web page fetching and processing"""
    
    def __init__(self, user_agent: str = None):
        """Initialize browser engine with optional custom user agent"""
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
        
        # Enhanced session with cookie and authentication support
        self.session = requests.Session()
        self.base_headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(self.base_headers)
        
        # Initialize components
        self.renderer = HTMLRenderer()
        self.js_engine = JavaScriptEngine(session=self.session)  # Pass session for real APIs
        self.css_parser = CSSParser()
        
        # Initialize intercepting proxy (Burp Suite-style)
        self.proxy = ProxyServer()
        
        # Navigation history and state
        self.history: List[str] = []
        self.history_index: int = -1
        self.current_url: Optional[str] = None
        self.current_soup: Optional[BeautifulSoup] = None
        self.current_links: List[Dict[str, str]] = []
        self.bookmarks: Dict[str, str] = {}  # name -> url mapping
        self.current_content_type: str = "text/html"
        self.current_json_data: Optional[Dict] = None  # Store JSON responses
        
    def get_js_enhanced_headers(self, url: str) -> Dict[str, str]:
        """Get enhanced headers that signal JavaScript capability for ALL websites"""
        enhanced_headers = self.base_headers.copy()
        
        # Universal JavaScript-capable browser headers for ALL websites
        # These headers tell websites that we support JavaScript
        enhanced_headers.update({
            # Chrome client hints indicating full JavaScript support
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-full-version-list': '"Google Chrome";v="131.0.6778.205", "Chromium";v="131.0.6778.205", "Not_A Brand";v="24.0.0.0"',
            'sec-ch-ua-arch': '"x86"',
            'sec-ch-ua-bitness': '"64"',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-wow64': '?0',
            
            # Additional headers that signal JavaScript capability
            'X-Requested-With': 'XMLHttpRequest',  # Indicates AJAX capability
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            
            # WebKit/V8 JavaScript engine indicators
            'Sec-Ch-Ua-Engine': '"Blink"',
            'Sec-Ch-Ua-Engine-Version': '"131.0.6778.205"',
            
            # Modern browser features that require JavaScript
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            
            # Service Worker and PWA support (requires JavaScript)
            'Service-Worker-Navigation-Preload': 'true',
        })
        
        # Site-specific JavaScript enablement
        domain = url.lower()
        
        # Twitter/X.com specific headers
        if 'x.com' in domain or 'twitter.com' in domain:
            enhanced_headers.update({
                'X-Twitter-Client-Language': 'en',
                'X-Twitter-Active-User': 'yes',
                'X-Csrf-Token': 'undefined',  # Will be set by JS
                'Authorization': 'Bearer undefined',  # Will be set by JS
            })
            
        # Facebook specific headers
        elif 'facebook.com' in domain or 'fb.com' in domain:
            enhanced_headers.update({
                'X-FB-LSD': 'undefined',  # Will be set by JS
                'X-ASBD-ID': 'undefined',  # Will be set by JS
            })
            
        # Google services headers - Enhanced for JavaScript detection
        elif any(google_domain in domain for google_domain in ['google.com', 'gmail.com', 'youtube.com', 'googleusercontent.com']):
            enhanced_headers.update({
                # Critical Google JavaScript detection headers
                'X-Client-Data': 'CKq1yQEIkrbJAQiltskBCKmdygEIqKPKAQioo8oBCJ2nygEI9anKAQi6qsoBCOKsygEI/qzKAQjkrco',  # Simulated Chrome client data
                'X-Goog-Visitor-Id': 'CgtOSVluek1UUXdOUSi4kP6tBg%3D%3D',  # Simulated visitor ID
                'X-Same-Domain': '1',  # Google same-domain check
                'X-Requested-With': 'XMLHttpRequest',  # AJAX capability
                
                # Additional Google-specific headers that indicate JavaScript support
                'Sec-Ch-Prefers-Color-Scheme': 'light',
                'Sec-Ch-Prefers-Reduced-Motion': 'no-preference',
                'Sec-Ch-Viewport-Width': '1920',
                'Sec-Ch-Device-Memory': '8',
                'Accept-CH': 'Sec-CH-UA, Sec-CH-UA-Arch, Sec-CH-UA-Bitness, Sec-CH-UA-Full-Version-List, Sec-CH-UA-Mobile, Sec-CH-UA-Model, Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version, Sec-CH-UA-WoW64',
            })
            
        # Add referrer for internal navigation
        if 'search' in url or '/search' in url:
            base_url = url.split('/search')[0] + '/'
            enhanced_headers['Referer'] = base_url
        
        return enhanced_headers
        
    def _detect_js_requirement(self, soup: BeautifulSoup, html_content: str) -> bool:
        """Detect if a website requires JavaScript to function properly"""
        # Check for common patterns that indicate JavaScript requirement
        js_required_patterns = [
            # Direct JS requirement messages
            'javascript is disabled',
            'enable javascript',
            'javascript is not available',
            'javascript must be enabled',
            'requires javascript',
            
            # React/Vue/Angular patterns
            '<div id="root"',
            '<div id="app"',
            'data-reactroot',
            'ng-app=',
            'v-app',
            
            # Modern web app patterns
            '<noscript>',
            'window.__INITIAL_State__',
            'window.__PRELOADED_STATE__',
            'window.APP_CONFIG',
            
            # Social media patterns
            'x.com',
            'twitter.com',
            'facebook.com',
            'instagram.com',
            
            # Single Page Application patterns
            'spa-',
            'single-page',
            'dynamic-content',
        ]
        
        html_lower = html_content.lower()
        
        # Check for JavaScript requirement patterns
        for pattern in js_required_patterns:
            if pattern in html_lower:
                return True
                
        # Check for minimal HTML content (likely needs JS to load content)
        text_content = soup.get_text(strip=True)
        if len(text_content) < 200 and soup.find_all('script'):
            return True
            
        # Check for empty main content areas that likely need JS
        main_containers = soup.find_all(['main', 'div'], {'id': ['root', 'app', 'content', 'main']})
        if main_containers:
            for container in main_containers:
                if not container.get_text(strip=True):
                    return True
                    
        return False
    
    def _proxy_request(self, method: str, url: str, headers: Dict[str, str], 
                       timeout: int = 30, **kwargs) -> requests.Response:
        """
        Make HTTP request through intercepting proxy
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            timeout: Request timeout
            **kwargs: Additional requests arguments
            
        Returns:
            HTTP response (potentially modified by proxy interceptors)
        """
        # Intercept request through proxy
        intercepted_request = self.proxy.intercept_request(
            method=method.upper(),
            url=url,
            headers=headers,
            body=kwargs.get('data') or kwargs.get('json')
        )
        
        # Check if request was blocked by proxy rules
        if intercepted_request.metadata.get('_blocked', False):
            # Create a blocked response without making HTTP request
            from requests import Response
            blocked_response = Response()
            blocked_response.status_code = 403
            blocked_response._content = b'Request blocked by proxy rule'
            blocked_response.headers['X-Blocked-By-Proxy'] = 'true'
            blocked_response.url = intercepted_request.url
            return blocked_response
        
        # Make actual HTTP request with potentially modified data
        response = self.session.request(
            method=intercepted_request.method,
            url=intercepted_request.url,
            headers=intercepted_request.headers,
            timeout=timeout,
            **kwargs
        )
        
        # Intercept response through proxy
        intercepted_response = self.proxy.intercept_response(
            request=intercepted_request,
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.text
        )
        
        # Apply intercepted modifications to response
        response._content = intercepted_response.body.encode() if intercepted_response.body else response.content
        response.status_code = intercepted_response.status_code
        response.headers.update(intercepted_response.headers)
        
        return response

    def fetch_page(self, url: str, timeout: int = 30) -> Tuple[bool, str, Optional[BeautifulSoup]]:
        """
        Fetch a web page and return success status, content, and parsed HTML
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (success, content/error_message, BeautifulSoup object or None)
        """
        try:
            # Normalize URL
            if url.startswith('//'):
                url = 'https:' + url
            elif not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Get enhanced headers for JavaScript detection
            enhanced_headers = self.get_js_enhanced_headers(url)
            
            # Make request through proxy with enhanced headers
            response = self._proxy_request('GET', url, enhanced_headers, timeout=timeout, allow_redirects=True)
            response.raise_for_status()
            
            # Detect content type and parse accordingly
            content_type = response.headers.get('content-type', '').lower()
            self.current_content_type = content_type
            
            if 'application/json' in content_type or url.endswith('.json'):
                # Handle JSON responses
                try:
                    self.current_json_data = json.loads(response.text)
                    soup = self._json_to_html(self.current_json_data, url)
                except json.JSONDecodeError:
                    # Fallback to HTML parsing if JSON parsing fails
                    soup = BeautifulSoup(response.text, 'html.parser')
                    self.current_json_data = None
            else:
                # Standard HTML parsing
                soup = BeautifulSoup(response.text, 'html.parser')
                self.current_json_data = None
                
                # Check for JavaScript or meta refresh redirects
                final_url = self._handle_client_side_redirects(soup, response.url)
                if final_url and final_url != response.url:
                    # Follow the redirect
                    try:
                        redirect_response = self._proxy_request('GET', final_url, enhanced_headers, timeout=timeout, allow_redirects=True)
                        redirect_response.raise_for_status()
                        soup = BeautifulSoup(redirect_response.text, 'html.parser')
                        response = redirect_response  # Update response to the final destination
                    except Exception:
                        # If redirect fails, continue with original page
                        pass
            
            # Update navigation state
            self.current_url = response.url
            self.current_soup = soup
            
            # Update history (only add new pages, not back/forward navigation)
            if self.history_index == -1 or response.url != self.history[self.history_index]:
                # Remove any forward history when navigating to new page
                if self.history_index < len(self.history) - 1:
                    self.history = self.history[:self.history_index + 1]
                
                self.history.append(response.url)
                self.history_index = len(self.history) - 1
            
            # Extract links for navigation
            self.current_links = self._extract_links(soup)
                
            return True, response.text, soup
            
        except requests.exceptions.Timeout:
            return False, f"Request timeout after {timeout} seconds", None
        except requests.exceptions.ConnectionError:
            return False, f"Connection error: Could not connect to {url}", None  
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP error {e.response.status_code}: {e.response.reason}", None
        except requests.exceptions.RequestException as e:
            return False, f"Request error: {str(e)}", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
    
    def _handle_client_side_redirects(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """
        Handle client-side redirects (JavaScript and meta refresh)
        
        Args:
            soup: BeautifulSoup parsed HTML
            current_url: Current page URL
            
        Returns:
            Redirect URL if found, None otherwise
        """
        # Check for meta refresh redirect
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if 'URL=' in content.upper():
                # Extract URL from content="0;URL=https://example.com"
                try:
                    if 'URL=' in content:
                        url_part = content.split('URL=', 1)[1]
                    else:
                        url_part = content.split('url=', 1)[1]
                    
                    redirect_url = url_part.strip().strip('"\'')
                    if redirect_url.startswith(('http://', 'https://')):
                        return redirect_url
                    elif redirect_url.startswith('//'):
                        return 'https:' + redirect_url
                    elif redirect_url.startswith('/'):
                        return urllib.parse.urljoin(current_url, redirect_url)
                except IndexError:
                    # Malformed meta refresh tag, skip
                    pass
        
        # Check for JavaScript redirects
        scripts = soup.find_all('script')
        for script in scripts:
            script_text = script.get_text()
            
            # Look for common JavaScript redirect patterns
            patterns = [
                r'window\.location\.replace\(["\']([^"\']+)["\']\)',
                r'window\.location\.href\s*=\s*["\']([^"\']+)["\']',
                r'location\.replace\(["\']([^"\']+)["\']\)',
                r'location\.href\s*=\s*["\']([^"\']+)["\']',
                r'window\.parent\.location\.replace\(["\']([^"\']+)["\']\)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, script_text)
                if match:
                    redirect_url = match.group(1)
                    if redirect_url.startswith(('http://', 'https://')):
                        return redirect_url
                    elif redirect_url.startswith('//'):
                        return 'https:' + redirect_url
                    elif redirect_url.startswith('/'):
                        return urllib.parse.urljoin(current_url, redirect_url)
        
        # Check for DuckDuckGo specific redirect URL parameter
        if 'duckduckgo.com/l/' in current_url:
            parsed = urllib.parse.urlparse(current_url)
            query_params = urllib.parse.parse_qs(parsed.query)
            if 'uddg' in query_params:
                return urllib.parse.unquote(query_params['uddg'][0])
        
        return None
            
    def render_page(self, soup: BeautifulSoup, execute_js: bool = False) -> str:
        """
        Render HTML page to markdown format - JavaScript disabled by default for clean output
        
        Args:
            soup: BeautifulSoup parsed HTML
            execute_js: Whether to execute JavaScript (disabled by default for cleaner output)
            
        Returns:
            Clean rendered markdown content without JavaScript code blocks
        """
        try:
            # Extract and parse CSS
            css_rules = self.css_parser.extract_css_from_soup(soup)
            
            # For clean output, skip JavaScript execution entirely
            # This prevents JavaScript code from appearing in the rendered output
            js_context = {}
            
            # Render HTML to markdown with clean mode enabled by default
            markdown_content = self.renderer.render_to_markdown(soup, css_rules, js_context, clean_mode=True)
            
            return markdown_content
            
        except Exception as e:
            return f"Error rendering page: {str(e)}\n\nRaw content available but could not be processed."
    
    def go_back(self) -> Optional[str]:
        """Navigate back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            return self.history[self.history_index]
        return None
    
    def go_forward(self) -> Optional[str]:
        """Navigate forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            return self.history[self.history_index]
        return None
    
    def can_go_back(self) -> bool:
        """Check if we can navigate back"""
        return self.history_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if we can navigate forward"""
        return self.history_index < len(self.history) - 1
    
    def get_current_links(self) -> List[Dict[str, str]]:
        """Get links from current page"""
        return self.current_links.copy()
    
    def follow_link(self, link_index: int) -> Optional[str]:
        """Follow a link by index from current page"""
        if 0 <= link_index < len(self.current_links):
            link_url = self.current_links[link_index]['url']
            # Enhanced URL resolution for all relative URL types
            if link_url.startswith('/') and self.current_url:
                # Absolute path relative to domain
                from urllib.parse import urljoin
                link_url = urljoin(self.current_url, link_url)
            elif not link_url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                # Relative path (like "community_api_reference.html")
                if self.current_url:
                    from urllib.parse import urljoin
                    link_url = urljoin(self.current_url, link_url)
                else:
                    # Fallback for cases without current URL context
                    link_url = 'https://' + link_url
            return link_url
        return None
    
    def add_bookmark(self, name: str, url: str = None) -> bool:
        """Add a bookmark"""
        bookmark_url = url or self.current_url
        if bookmark_url:
            self.bookmarks[name] = bookmark_url
            return True
        return False
    
    def get_bookmark(self, name: str) -> Optional[str]:
        """Get bookmark URL by name"""
        return self.bookmarks.get(name)
    
    def list_bookmarks(self) -> Dict[str, str]:
        """List all bookmarks"""
        return self.bookmarks.copy()
    
    def remove_bookmark(self, name: str) -> bool:
        """Remove a bookmark"""
        if name in self.bookmarks:
            del self.bookmarks[name]
            return True
        return False
    
    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links from the page"""
        links = []
        try:
            for link in soup.find_all('a', href=True):
                url = link.get('href', '').strip()
                text = link.get_text(strip=True) or url
                
                if url and url not in ['#', 'javascript:void(0)', 'javascript:;']:
                    links.append({
                        'text': text[:100],  # Limit text length
                        'url': url,
                        'title': link.get('title', '')
                    })
        except Exception:
            pass
        
        return links
    
    def _json_to_html(self, json_data: Union[Dict, List], source_url: str) -> BeautifulSoup:
        """Convert JSON data to HTML for display purposes"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>JSON Response - {source_url}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace; margin: 20px; }}
                .json-container {{ background: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .json-key {{ color: #0969da; font-weight: bold; }}
                .json-string {{ color: #0a3069; }}
                .json-number {{ color: #cf222e; }}
                .json-boolean {{ color: #8250df; }}
                .json-null {{ color: #656d76; font-style: italic; }}
                .json-object {{ margin-left: 20px; }}
                .json-array {{ margin-left: 20px; }}
                h1 {{ color: #24292f; border-bottom: 1px solid #d1d9e0; padding-bottom: 8px; }}
                .api-info {{ background: #ddf4ff; padding: 10px; border-radius: 4px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>JSON API Response</h1>
            <div class="api-info">
                <strong>URL:</strong> {source_url}<br>
                <strong>Content-Type:</strong> application/json<br>
                <strong>Response Size:</strong> {len(str(json_data))} characters
            </div>
            <div class="json-container">
                {self._format_json_as_html(json_data)}
            </div>
        </body>
        </html>
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def _format_json_as_html(self, data: Union[Dict, List, str, int, float, bool, None], indent: int = 0) -> str:
        """Recursively format JSON data as HTML"""
        if data is None:
            return '<span class="json-null">null</span>'
        elif isinstance(data, bool):
            return f'<span class="json-boolean">{"true" if data else "false"}</span>'
        elif isinstance(data, (int, float)):
            return f'<span class="json-number">{data}</span>'
        elif isinstance(data, str):
            # Check if string contains URLs for potential navigation
            if data.startswith(('http://', 'https://')):
                return f'<span class="json-string"><a href="{data}" style="color: #0969da;">"{data}"</a></span>'
            return f'<span class="json-string">"{data}"</span>'
        elif isinstance(data, list):
            if not data:
                return '<span class="json-array">[]</span>'
            
            items = []
            for i, item in enumerate(data):
                formatted_item = self._format_json_as_html(item, indent + 1)
                items.append(f'<div style="margin-left: {indent * 20}px;">[{i}]: {formatted_item}</div>')
            
            return f'<div class="json-array">[<br>{"<br>".join(items)}<br><div style="margin-left: {(indent-1) * 20}px;">]</div></div>'
        elif isinstance(data, dict):
            if not data:
                return '<span class="json-object">{}</span>'
            
            items = []
            for key, value in data.items():
                formatted_value = self._format_json_as_html(value, indent + 1)
                items.append(f'<div style="margin-left: {indent * 20}px;"><span class="json-key">"{key}"</span>: {formatted_value}</div>')
            
            return f'<div class="json-object">{{<br>{"<br>".join(items)}<br><div style="margin-left: {(indent-1) * 20}px;">}}</div></div>'
        else:
            return f'<span>{str(data)}</span>'
    
    def get_json_data(self) -> Optional[Dict]:
        """Get the current JSON data if the page is a JSON response"""
        return self.current_json_data
    
    def is_json_response(self) -> bool:
        """Check if the current page is a JSON response"""
        return self.current_json_data is not None
    
    def search_json(self, query: str) -> List[Dict[str, Union[str, Any]]]:
        """Search for values in JSON data"""
        if not self.current_json_data:
            return []
        
        results = []
        self._search_json_recursive(self.current_json_data, query, "", results)
        return results
    
    def _search_json_recursive(self, data: Union[Dict, List, Any], query: str, path: str, results: List):
        """Recursively search JSON data for matching values"""
        query_lower = query.lower()
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check if key matches
                if query_lower in key.lower():
                    results.append({
                        'path': current_path,
                        'type': 'key',
                        'value': key,
                        'data': value
                    })
                
                # Check if value matches (for strings)
                if isinstance(value, str) and query_lower in value.lower():
                    results.append({
                        'path': current_path,
                        'type': 'value',
                        'value': value,
                        'data': value
                    })
                
                # Recurse into nested structures
                self._search_json_recursive(value, query, current_path, results)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]" if path else f"[{i}]"
                self._search_json_recursive(item, query, current_path, results)
                
        elif isinstance(data, str) and query_lower in data.lower():
            results.append({
                'path': path,
                'type': 'value', 
                'value': data,
                'data': data
            })
            
    def _execute_page_javascript(self, soup: BeautifulSoup) -> Dict:
        """Execute JavaScript found in the page and return DOM modifications"""
        modifications = {}
        
        try:
            # Check if website requires JavaScript (common patterns)
            html_content = str(soup)
            requires_js = self._detect_js_requirement(soup, html_content)
            
            # Extract all script tags
            scripts = soup.find_all('script')
            
            # Always initialize JavaScript environment for modern websites
            if requires_js or scripts:
                print("🔧 JavaScript engine active - enabling JavaScript support...")
                
                # Initialize JavaScript environment with advanced Google-compatible APIs
                init_js = """
                // Advanced JavaScript environment for Google and modern websites
                window._jsEnabled = true;
                window._cliBrowser = true;
                window._googleCompatible = true;
                
                console.log('✅ Advanced JavaScript environment initialized');
                console.log('🌐 Google-compatible browser APIs enabled');
                
                // CRITICAL: Advanced Google JavaScript detection bypass
                if (typeof window !== 'undefined') {
                    // Google checks for these specific properties and methods
                    window.chrome = window.chrome || {
                        runtime: {
                            onConnect: {
                                addListener: function() {},
                                removeListener: function() {},
                                hasListener: function() { return false; }
                            },
                            sendMessage: function() {},
                            onMessage: {
                                addListener: function() {},
                                removeListener: function() {}
                            }
                        },
                        webstore: {
                            install: function() {}
                        }
                    };
                    
                    // Performance API that Google checks
                    window.performance = window.performance || {
                        now: function() { return Date.now(); },
                        timing: {
                            navigationStart: Date.now() - 1000,
                            loadEventEnd: Date.now()
                        },
                        navigation: {
                            type: 0
                        },
                        mark: function() {},
                        measure: function() {},
                        getEntriesByType: function() { return []; }
                    };
                    
                    // Screen properties Google expects
                    window.screen = window.screen || {
                        width: 1920,
                        height: 1080,
                        availWidth: 1920,
                        availHeight: 1040,
                        colorDepth: 24,
                        pixelDepth: 24,
                        orientation: {
                            type: 'landscape-primary',
                            angle: 0
                        }
                    };
                    
                    // Advanced navigator properties for Google detection
                    if (window.navigator) {
                        window.navigator.webdriver = false;  // Critical: not a bot
                        window.navigator.plugins = window.navigator.plugins || [];
                        window.navigator.mimeTypes = window.navigator.mimeTypes || [];
                        window.navigator.permissions = window.navigator.permissions || {
                            query: function() {
                                return Promise.resolve({ state: 'granted' });
                            }
                        };
                        window.navigator.serviceWorker = window.navigator.serviceWorker || {
                            register: function() {
                                return Promise.resolve({
                                    unregister: function() { return Promise.resolve(true); }
                                });
                            },
                            ready: Promise.resolve({})
                        };
                        
                        // Hardware concurrency and device memory Google checks
                        window.navigator.hardwareConcurrency = 8;
                        window.navigator.deviceMemory = 8;
                        window.navigator.connection = {
                            effectiveType: '4g',
                            downlink: 10,
                            rtt: 50
                        };
                    }
                    
                    // History API for SPA detection
                    window.history = window.history || {
                        pushState: function() { console.log('history.pushState called'); },
                        replaceState: function() { console.log('history.replaceState called'); },
                        back: function() { console.log('history.back called'); },
                        forward: function() { console.log('history.forward called'); },
                        go: function() { console.log('history.go called'); },
                        length: 1,
                        state: null
                    };
                    
                    // Location object with Google-compatible properties
                    window.location = window.location || {
                        href: 'https://www.google.com/',
                        protocol: 'https:',
                        host: 'www.google.com',
                        hostname: 'www.google.com',
                        port: '',
                        pathname: '/',
                        search: '',
                        hash: '',
                        origin: 'https://www.google.com',
                        assign: function(url) { console.log('location.assign:', url); },
                        replace: function(url) { console.log('location.replace:', url); },
                        reload: function() { console.log('location.reload'); }
                    };
                    
                    // Enhanced fetch API with Google-compatible responses
                    window.fetch = window.fetch || function(url, options) {
                        console.log('🌐 Advanced fetch API call:', url);
                        return Promise.resolve({
                            ok: true,
                            status: 200,
                            statusText: 'OK',
                            headers: {
                                get: function(name) {
                                    if (name.toLowerCase() === 'content-type') return 'application/json';
                                    return null;
                                },
                                has: function() { return true; }
                            },
                            json: function() { return Promise.resolve({}); },
                            text: function() { return Promise.resolve('{}'); },
                            blob: function() { return Promise.resolve(new Blob()); },
                            arrayBuffer: function() { return Promise.resolve(new ArrayBuffer(0)); }
                        });
                    };
                    
                    // Enhanced XMLHttpRequest for Google compatibility
                    window.XMLHttpRequest = window.XMLHttpRequest || function() {
                        this.readyState = 0;
                        this.status = 0;
                        this.statusText = '';
                        this.responseText = '';
                        this.responseXML = null;
                        this.onreadystatechange = null;
                        this.onload = null;
                        this.onerror = null;
                        
                        this.open = function(method, url, async) {
                            this.readyState = 1;
                            console.log('📡 XMLHttpRequest.open:', method, url);
                        };
                        
                        this.send = function(data) {
                            var self = this;
                            setTimeout(function() {
                                self.readyState = 4;
                                self.status = 200;
                                self.statusText = 'OK';
                                self.responseText = '{}';
                                if (self.onreadystatechange) self.onreadystatechange();
                                if (self.onload) self.onload();
                            }, 10);
                        };
                        
                        this.setRequestHeader = function(name, value) {
                            console.log('📡 XMLHttpRequest header:', name, value);
                        };
                        
                        this.getResponseHeader = function(name) {
                            if (name.toLowerCase() === 'content-type') return 'application/json';
                            return null;
                        };
                        
                        this.getAllResponseHeaders = function() {
                            return 'content-type: application/json\\r\\n';
                        };
                        
                        this.abort = function() {
                            this.readyState = 0;
                        };
                    };
                    
                    // WebSocket for advanced web apps
                    window.WebSocket = window.WebSocket || function(url) {
                        this.readyState = 1; // OPEN
                        this.url = url;
                        this.protocol = '';
                        this.onopen = null;
                        this.onmessage = null;
                        this.onclose = null;
                        this.onerror = null;
                        
                        this.send = function(data) {
                            console.log('🔌 WebSocket send:', data);
                        };
                        
                        this.close = function() {
                            this.readyState = 3; // CLOSED
                            if (this.onclose) this.onclose();
                        };
                        
                        console.log('🔌 WebSocket created:', url);
                        setTimeout(() => {
                            if (this.onopen) this.onopen();
                        }, 10);
                    };
                }
                
                // Signal to document that JavaScript is fully operational
                if (typeof document !== 'undefined') {
                    // Create a flag that Google specifically looks for
                    document._javascriptEnabled = true;
                    document._chromeCompatible = true;
                    
                    // Set up enhanced navigator in document context too
                    document.navigator = window.navigator;
                    
                    // Trigger all DOM events that Google expects
                    setTimeout(function() {
                        try {
                            if (typeof window.dispatchEvent === 'function') {
                                var events = ['DOMContentLoaded', 'load', 'readystatechange'];
                                events.forEach(function(eventType) {
                                    var event = new Event(eventType, { bubbles: true, cancelable: true });
                                    window.dispatchEvent(event);
                                    if (document.dispatchEvent) document.dispatchEvent(event);
                                });
                                console.log('📡 All DOM events dispatched for Google compatibility');
                            }
                            
                            // Set document ready state
                            document.readyState = 'complete';
                            
                        } catch(e) {
                            console.log('Event dispatch completed with fallback');
                        }
                    }, 50);
                }
                
                console.log('🎯 Google JavaScript detection bypass completed');
                """
                
                try:
                    init_result = self.js_engine.execute_script(init_js, soup)
                    if init_result:
                        modifications.update(init_result)
                    print("   ✅ JavaScript environment initialized")
                except Exception as e:
                    print(f"   ⚠️  JavaScript init error: {str(e)[:50]}...")
            
            # Process all scripts found on the page
            script_count = 0
            for script in scripts:
                script_content = script.string or script.get_text()
                if script_content and script_content.strip():
                    # Skip external scripts (would need separate fetching)
                    if script.get('src'):
                        print(f"   📂 External script: {script.get('src')[:50]}...")
                        continue
                    
                    # Skip JSON-LD structured data scripts (not executable JavaScript)
                    script_type = script.get('type', 'text/javascript').lower()
                    if script_type in ['application/ld+json', 'application/json']:
                        continue
                        
                    try:
                        # Execute JavaScript and capture DOM modifications
                        result = self.js_engine.execute_script(script_content, soup)
                        if result:
                            modifications.update(result)
                        script_count += 1
                        
                    except Exception as e:
                        # Silently handle JS errors to avoid cluttering output
                        # Only log critical errors
                        error_msg = str(e)
                        if len(error_msg) < 100 and 'unexpected token' not in error_msg.lower():
                            print(f"   ⚠️  Script error: {error_msg[:50]}...")
                        continue
                        
            if script_count > 0:
                print(f"   ✅ Processed {script_count} JavaScript files")
            
            # For websites that require JS but have no inline scripts, inject basic functionality
            if requires_js and script_count == 0:
                fallback_js = """
                // Fallback JavaScript for sites that require JS but have no inline scripts
                console.log('🔄 Fallback JavaScript activated for modern website');
                
                // Create basic interactive elements
                if (typeof document !== 'undefined') {
                    document.body = document.body || { innerHTML: '' };
                    console.log('📄 Document body initialized');
                }
                """
                
                try:
                    fallback_result = self.js_engine.execute_script(fallback_js, soup)
                    if fallback_result:
                        modifications.update(fallback_result)
                    print("   ✅ Fallback JavaScript activated")
                except Exception:
                    pass
                        
        except Exception as e:
            print(f"Error processing JavaScript: {str(e)}")
            
        return modifications
    
    def extract_javascript(self, soup):
        """Extract JavaScript content from page for external execution"""
        if not soup:
            return ""
        
        scripts = []
        for script in soup.find_all('script'):
            script_content = script.string or script.get_text()
            if script_content and script_content.strip():
                # Skip external scripts
                if script.get('src'):
                    continue
                
                # Skip JSON-LD structured data
                script_type = script.get('type', 'text/javascript').lower()
                if script_type in ['application/ld+json', 'application/json']:
                    continue
                
                scripts.append(script_content.strip())
        
        return '\n'.join(scripts)
    
    def apply_dom_updates(self, soup, dom_updates):
        """Apply DOM updates from JavaScript execution to the soup object"""
        if not soup or not dom_updates:
            return
        
        try:
            for update in dom_updates:
                if update.get('type') == 'modify_element':
                    # Handle element modifications
                    selector = update.get('selector')
                    if selector:
                        elements = soup.select(selector)
                        for element in elements:
                            if update.get('innerHTML'):
                                element.clear()
                                element.append(BeautifulSoup(update['innerHTML'], 'html.parser'))
                            if update.get('attributes'):
                                for attr, value in update['attributes'].items():
                                    element[attr] = value
        except Exception as e:
            # Silently handle DOM update errors
            pass
        
    def _apply_js_modifications(self, soup: BeautifulSoup, modifications: Dict) -> BeautifulSoup:
        """Apply JavaScript modifications to the BeautifulSoup object"""
        # This is a simplified implementation
        # In a full browser, this would handle complex DOM manipulation
        
        try:
            for element_id, changes in modifications.items():
                element = soup.find(id=element_id)
                if element:
                    if 'innerHTML' in changes:
                        element.clear()
                        element.append(BeautifulSoup(changes['innerHTML'], 'html.parser'))
                    if 'textContent' in changes:
                        element.string = changes['textContent']
                    if 'style' in changes:
                        element['style'] = changes['style']
                        
        except Exception as e:
            print(f"Error applying JavaScript modifications: {str(e)}")
            
        return soup
        
    def browse(self, url: str, execute_js: bool = True) -> Tuple[bool, str]:
        """
        Browse to a URL and return rendered content
        
        Args:
            url: URL to browse to
            execute_js: Whether to execute JavaScript
            
        Returns:
            Tuple of (success, rendered_content_or_error_message)
        """
        # Fetch the page
        success, content, soup = self.fetch_page(url)
        
        if not success:
            return False, content
            
        # Render the page
        try:
            rendered_content = self.render_page(soup, execute_js)
            return True, rendered_content
        except Exception as e:
            return False, f"Error rendering page: {str(e)}"
            
    def get_links(self) -> List[Tuple[str, str]]:
        """Get all links from current page as (text, url) tuples"""
        if not self.current_soup:
            return []
            
        links = []
        for link in self.current_soup.find_all('a', href=True):
            text = link.get_text(strip=True) or link.get('href', '')
            href = link.get('href')
            
            # Convert relative URLs to absolute
            if href and self.current_url:
                absolute_url = urllib.parse.urljoin(self.current_url, href)
                links.append((text, absolute_url))
                
        return links
        
    def search_page(self, query: str) -> List[str]:
        """Search for text in current page"""
        if not self.current_soup:
            return []
            
        results = []
        text_content = self.current_soup.get_text()
        
        # Simple case-insensitive search
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if query.lower() in line.lower():
                results.append(f"Line {i+1}: {line.strip()}")
                
        return results
        
    def get_page_info(self) -> Dict[str, str]:
        """Get information about current page"""
        if not self.current_soup or not self.current_url:
            return {}
            
        info = {
            'url': self.current_url,
            'title': '',
            'description': '',
            'keywords': ''
        }
        
        # Get title
        title_tag = self.current_soup.find('title')
        if title_tag:
            info['title'] = title_tag.get_text(strip=True)
            
        # Get meta description
        desc_tag = self.current_soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            info['description'] = desc_tag.get('content', '')
            
        # Get meta keywords
        keywords_tag = self.current_soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            info['keywords'] = keywords_tag.get('content', '')
            
        return info
