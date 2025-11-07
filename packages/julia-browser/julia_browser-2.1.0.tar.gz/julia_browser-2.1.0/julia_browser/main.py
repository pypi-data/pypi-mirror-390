#!/usr/bin/env python3
"""
CLI Browser - Main entry point
A Python-based CLI browser that renders HTML/CSS as markdown with JavaScript support
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli import main

if __name__ == "__main__":
    main()
