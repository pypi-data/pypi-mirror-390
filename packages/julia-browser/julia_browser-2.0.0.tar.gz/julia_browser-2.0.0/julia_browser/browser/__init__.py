"""
CLI Browser Package
A Python-based CLI browser that renders HTML/CSS as markdown with JavaScript support
"""

from .engine import BrowserEngine
from .renderer import HTMLRenderer
from .js_engine import JavaScriptEngine
from .css_parser import CSSParser

__version__ = "0.1.0"
__author__ = "CLI Browser"

__all__ = [
    "BrowserEngine",
    "HTMLRenderer", 
    "JavaScriptEngine",
    "CSSParser"
]
