"""
Setup script for Julia Browser
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="julia-browser",
    version="1.15.0",
    author="Harish Santhanalakshmi Ganesan",
    author_email="harishsg99@gmail.com",
    description="A comprehensive Python-based CLI web browser with JavaScript support and modern web compatibility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juliabrowser/julia-browser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "Topic :: Terminals",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "markdownify>=1.0.0",
        "pythonmonkey>=1.0.0",
        "rich>=13.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "performance": [
            "ujson>=5.0.0",
            "lxml>=4.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "julia-browser=julia_browser.cli:main",
            "jbrowser=julia_browser.cli:main",
            "jb=julia_browser.cli:main",
        ],
    },
    keywords=[
        "browser", "cli", "terminal", "web", "html", "css", "javascript", 
        "markdown", "scraping", "automation", "headless", "spidermonkey",
        "pythonmonkey", "web-browser", "command-line", "text-based"
    ],
    project_urls={
        "Bug Reports": "https://github.com/juliabrowser/julia-browser/issues",
        "Documentation": "https://docs.juliabrowser.com",
        "Source": "https://github.com/juliabrowser/julia-browser",
        "Changelog": "https://github.com/juliabrowser/julia-browser/blob/main/CHANGELOG.md",
    },
)