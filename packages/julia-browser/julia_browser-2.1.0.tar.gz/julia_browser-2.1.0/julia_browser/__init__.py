"""
Julia Browser - A comprehensive Python-based CLI web browser with JavaScript support

Julia Browser transforms command-line web browsing into a dynamic, intelligent experience
with comprehensive JavaScript simulation and rendering capabilities.

Key Features:
- Enhanced JavaScript engine with browser API simulation
- Advanced URL resolution and content parsing
- Dynamic web content exploration with intelligent search processing
- Flexible browser automation supporting multiple rendering strategies
- Interactive CLI interface with comprehensive web interaction support
- Full modern web compatibility including HTML DOM API, CSS Object Model (CSSOM)
- Real interactive behaviors, authentication flows, and session management
- Advanced CSS layouts with Grid/Flexbox visual representation
- Performance optimizations with caching and asynchronous execution
"""

__version__ = "1.2.0"
__author__ = "Julia Browser Development Team"
__email__ = "dev@juliabrowser.com"
__license__ = "MIT"

# Import main classes for easy access
from .browser.engine import BrowserEngine
from .browser_sdk import BrowserSDK
from .agent_sdk import AgentSDK
from .cli_interface import CLIBrowser

# Package metadata
__all__ = [
    "BrowserEngine",
    "BrowserSDK",
    "AgentSDK", 
    "CLIBrowser",
    "__version__",
    "__author__",
    "__email__",
    "__license__"
]

# Version info tuple
version_info = tuple(map(int, __version__.split('.')))