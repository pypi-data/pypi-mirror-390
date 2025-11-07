# Changelog

All notable changes to Julia Browser will be documented in this file.

## [2.0.1] - 2025-11-07

### Updated
- **README Documentation**: Added comprehensive Burp Suite-style intercepting proxy documentation with examples
- **Proxy Examples**: Added quick start, custom interceptors, security testing, API monitoring, and traffic analysis examples
- **API Reference**: Complete proxy API reference with all 9 proxy methods documented
- **Clean Formatting**: Consistent formatting matching existing README style

## [2.0.0] - 2025-11-07

### Added
- **Burp Suite-Style Intercepting Proxy**: Complete HTTP/HTTPS traffic interception system for AI agents
- **Request Interception**: Intercept and modify outgoing HTTP requests (headers, body, URL)
- **Response Interception**: Intercept and modify incoming HTTP responses (status, headers, content)
- **Traffic Logging**: Comprehensive logging of all HTTP requests and responses with metadata
- **Custom Interceptors**: AI agents can register custom request/response interceptors via SDK
- **Proxy Management API**: Full SDK control with `proxy_start()`, `proxy_stop()`, `proxy_status()`
- **Traffic Analysis**: Get traffic logs, statistics, and comprehensive analytics via `proxy_get_traffic()`
- **Interceptor Registry**: Add, remove, and list custom interceptors dynamically
- **Security Testing**: Built-in support for security header analysis and vulnerability testing
- **API Monitoring**: Automatic detection and logging of API calls and JSON responses
- **Zero Breaking Changes**: All existing SDK functions work identically with optional proxy layer

### Features
- 9 new Agent SDK methods: `proxy_start()`, `proxy_stop()`, `proxy_status()`, `proxy_get_traffic()`, `proxy_clear_traffic()`, `proxy_add_request_interceptor()`, `proxy_add_response_interceptor()`, `proxy_remove_interceptor()`, `proxy_list_interceptors()`
- HTTPRequest and HTTPResponse dataclasses for structured traffic representation
- TrafficLog entries with request/response pairs and modification tracking
- InterceptorRegistry for managing multiple interceptors with thread safety
- ProxyServer with comprehensive statistics and metrics tracking
- Integration with browser engine via `_proxy_request()` method
- Complete backward compatibility - proxy is optional and transparent when disabled

### Documentation
- Comprehensive proxy examples in `examples/proxy_demo.py`
- Complete API documentation in `examples/README_proxy.md`
- 7 real-world use case examples (traffic logging, header injection, response modification, etc.)
- Performance testing and validation with multiple websites

### Tested
- All existing SDK functions work with and without proxy enabled
- GET and POST request handling verified
- Form submission compatibility confirmed
- Custom interceptor functionality validated
- Traffic logging and statistics accuracy verified
- No performance degradation or memory leaks detected

## [1.17.1] - 2025-01-29

### Added
- Data URI CSS support for inline stylesheets (data:text/css format)
- Enhanced CSS parser with data URI decoding (plain text and base64)
- Comprehensive error suppression for data URI connection adapter issues

### Fixed
- Resolved "No connection adapters were found for 'data:text/css'" error
- Added proper data URI parsing for CSS content in link tags
- Enhanced CSS extraction to handle both plain text and base64-encoded data URIs
- Eliminated connection errors when processing inline CSS data URIs

## [1.17.0] - 2025-01-29

### Added
- Comprehensive JavaScript code filtering in clean rendering mode
- Enhanced script tag removal and JavaScript block detection
- Advanced content filtering for CSS blocks, accessibility markers, media queries
- Clean HTML-only markdown output without technical implementation details

### Fixed
- Completely eliminated JavaScript code blocks (rtlLangs, translationsHash, etc.)
- Removed all script tags and JavaScript execution remnants from output
- Enhanced CSS and technical content filtering for cleaner markdown
- Disabled JavaScript execution by default for cleaner page rendering
- Clean output shows only meaningful HTML content as readable markdown

## [1.16.0] - 2025-01-29

### Added
- Clean rendering mode as default to show only core page content
- Comprehensive technical content filtering (CSS blocks, accessibility markers, media queries)
- Simplified form element display without technical attributes
- Enhanced content filtering to remove implementation details

### Fixed
- Eliminated CSS code blocks from rendered output
- Removed accessibility labels and custom element details from clean display
- Filtered out media conditions and form validation technical information
- Clean, readable markdown output focused on actual website content

## [1.15.0] - 2025-01-29

### Fixed
- **JavaScript Bridge Return Values**: Resolved critical issue where JavaScript engine always returned empty dictionaries instead of actual JavaScript values. Modified execute_script() method to return pm.eval() result directly instead of DOM modifications only. JavaScript expressions now properly return values: 2+2 returns 4.0, "hello" returns "hello", true returns True, document.title returns actual page title.

- **Interactive Mode Session Loop**: Resolved issue where interactive CLI mode immediately exited after showing welcome screen. Changed EOFError handling from break to continue with user message, preventing premature session termination. Interactive mode now maintains proper session state and waits for user input instead of exiting immediately.

### Improved
- JavaScript-Python bridge communication now provides real bidirectional communication between contexts
- Interactive CLI maintains proper session loops without premature termination
- Component integration improved with consistent method naming across modules
- Enhanced error handling in JavaScript execution with better debugging output

## [1.0.0] - 2025-01-26

### Added
- Initial release of Julia Browser
- Enhanced JavaScript engine with Mozilla SpiderMonkey integration
- Interactive CLI interface with Rich terminal formatting
- Modern web compatibility with HTML DOM API and CSS Object Model
- Advanced navigation system with back/forward, bookmarks, and history
- Intelligent content processing and clean markdown output
- Performance optimizations with caching and asynchronous execution
- Real web interactions including form submission and file uploads
- Authentication flows and session management
- Multiple output formats (Markdown, HTML, JSON)
- Comprehensive button interaction logic
- Enhanced JavaScript engine for modern web compatibility
- Google search compatibility with DuckDuckGo fallback
- Advanced CSS layout engine with Grid/Flexbox visualization
- High-performance asynchronous browser engine
- Intelligent caching system with SQLite backend
- Enhanced image handling and content filtering
- Complete module import filtering
- Natural redirect handling
- Client-side redirect support
- Form submission bug fixes
- API website compatibility
- Button navigation system

### Features
- Command-line interface with multiple commands
- Python SDK for programmatic access
- JavaScript execution with real browser environment simulation
- Modern web framework support (React, Vue, Angular)
- Network request handling with fetch API and WebSocket support
- Cookie management and persistent sessions
- Responsive design detection
- JSON API support with search capabilities

### Technical Improvements
- Fixed critical JavaScript engine errors
- Resolved form submission bugs
- Enhanced URL resolution for protocol-relative URLs
- Improved error handling and logging
- Dynamic content filtering with intelligent pattern recognition
- Separated interactive elements display
- Fixed Wikipedia rendering errors
- Enhanced search engine compatibility

## Future Releases

### Planned Features
- Headless browser integration for enhanced JavaScript support
- Advanced network simulation with Service Workers
- Progressive Web App (PWA) support
- Enhanced mobile device simulation
- Plugin system for extensibility
- Advanced debugging capabilities
- Performance monitoring dashboard
- Export functionality for browsing sessions