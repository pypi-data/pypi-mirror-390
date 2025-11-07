"""
Browser SDK - Python SDK interface for programmatic usage
"""

from typing import Dict, List, Optional, Any, Union
import json
from datetime import datetime

try:
    from .browser.engine import BrowserEngine
except ImportError:
    from browser.engine import BrowserEngine


class BrowserSDK:
    """
    Python SDK for the CLI Browser
    Provides programmatic access to browser functionality
    """
    
    def __init__(self, user_agent: str = None, timeout: int = 30):
        """
        Initialize Browser SDK
        
        Args:
            user_agent: Custom user agent string
            timeout: Default timeout for requests
        """
        self.engine = BrowserEngine(user_agent)
        self.default_timeout = timeout
        
    def fetch_page(self, url: str, timeout: int = None) -> Dict[str, Any]:
        """
        Fetch a web page
        
        Args:
            url: URL to fetch
            timeout: Request timeout (uses default if None)
            
        Returns:
            Dictionary with success status, content, and metadata
        """
        try:
            timeout = timeout or self.default_timeout
            success, content, soup = self.engine.fetch_page(url, timeout)
            
            result = {
                'success': success,
                'url': url,
                'final_url': self.engine.current_url if success else None,
                'timestamp': datetime.now().isoformat(),
                'content': content if success else None,
                'error': content if not success else None,
                'soup': soup if success else None
            }
            
            if success and soup:
                # Add metadata
                result['metadata'] = self._extract_metadata(soup)
                
            return result
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'final_url': None,
                'timestamp': datetime.now().isoformat(),
                'content': None,
                'error': f"SDK error: {str(e)}",
                'soup': None,
                'metadata': None
            }
            
    def render_to_markdown(self, url: str, execute_js: bool = True, timeout: int = None) -> Dict[str, Any]:
        """
        Fetch and render a page to markdown
        
        Args:
            url: URL to render
            execute_js: Whether to execute JavaScript
            timeout: Request timeout
            
        Returns:
            Dictionary with rendered content and metadata
        """
        try:
            # Fetch page
            fetch_result = self.fetch_page(url, timeout)
            
            if not fetch_result['success']:
                return fetch_result
                
            # Render page
            soup = fetch_result['soup']
            markdown_content = self.engine.render_page(soup, execute_js)
            
            return {
                'success': True,
                'url': url,
                'final_url': fetch_result['final_url'],
                'timestamp': fetch_result['timestamp'],
                'content': markdown_content,
                'soup': soup,
                'metadata': fetch_result['metadata'],
                'format': 'markdown',
                'javascript_executed': execute_js
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': f"Rendering error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            
    def render_to_text(self, url: str, execute_js: bool = True, timeout: int = None) -> Dict[str, Any]:
        """
        Fetch and render a page to plain text
        
        Args:
            url: URL to render
            execute_js: Whether to execute JavaScript
            timeout: Request timeout
            
        Returns:
            Dictionary with rendered text content
        """
        try:
            # First get markdown
            md_result = self.render_to_markdown(url, execute_js, timeout)
            
            if not md_result['success']:
                return md_result
                
            # Convert markdown to plain text (simplified)
            markdown_content = md_result['content']
            
            # Remove markdown formatting
            import re
            text_content = re.sub(r'[*_`#\[\]()>-]', '', markdown_content)
            text_content = re.sub(r'\n+', '\n', text_content)
            text_content = text_content.strip()
            
            result = md_result.copy()
            result['content'] = text_content
            result['format'] = 'text'
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': f"Text rendering error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            
    def get_page_links(self, url: str, timeout: int = None) -> Dict[str, Any]:
        """
        Get all links from a page
        
        Args:
            url: URL to analyze
            timeout: Request timeout
            
        Returns:
            Dictionary with links and metadata
        """
        try:
            # Fetch page
            fetch_result = self.fetch_page(url, timeout)
            
            if not fetch_result['success']:
                return fetch_result
                
            # Get links
            links = self.engine.get_links()
            
            return {
                'success': True,
                'url': url,
                'final_url': fetch_result['final_url'],
                'timestamp': fetch_result['timestamp'],
                'links': [{'text': text, 'url': link_url} for text, link_url in links],
                'link_count': len(links),
                'metadata': fetch_result['metadata']
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': f"Link extraction error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            
    def search_page(self, url: str, query: str, timeout: int = None) -> Dict[str, Any]:
        """
        Search for text within a page
        
        Args:
            url: URL to search
            query: Search query
            timeout: Request timeout
            
        Returns:
            Dictionary with search results
        """
        try:
            # Fetch page
            fetch_result = self.fetch_page(url, timeout)
            
            if not fetch_result['success']:
                return fetch_result
                
            # Search page
            results = self.engine.search_page(query)
            
            return {
                'success': True,
                'url': url,
                'final_url': fetch_result['final_url'],
                'timestamp': fetch_result['timestamp'],
                'query': query,
                'results': results,
                'result_count': len(results),
                'metadata': fetch_result['metadata']
            }
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'query': query,
                'error': f"Search error: {str(e)}",
                'timestamp': datetime.now().isoformat()
            }
            
    def batch_process(self, urls: List[str], output_format: str = 'markdown', 
                     execute_js: bool = True, timeout: int = None) -> List[Dict[str, Any]]:
        """
        Process multiple URLs in batch
        
        Args:
            urls: List of URLs to process
            output_format: Output format ('markdown', 'text')
            execute_js: Whether to execute JavaScript
            timeout: Request timeout
            
        Returns:
            List of results for each URL
        """
        results = []
        
        for url in urls:
            try:
                if output_format == 'markdown':
                    result = self.render_to_markdown(url, execute_js, timeout)
                elif output_format == 'text':
                    result = self.render_to_text(url, execute_js, timeout)
                else:
                    result = {
                        'success': False,
                        'url': url,
                        'error': f"Unsupported format: {output_format}",
                        'timestamp': datetime.now().isoformat()
                    }
                    
                results.append(result)
                
            except Exception as e:
                results.append({
                    'success': False,
                    'url': url,
                    'error': f"Batch processing error: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                })
                
        return results
        
    def fetch_and_render(self, url: str, output_format: str = 'markdown', 
                        execute_js: bool = True, timeout: int = None) -> Dict[str, Any]:
        """
        Convenience method to fetch and render in one call
        
        Args:
            url: URL to process
            output_format: Output format ('markdown', 'text', 'html')
            execute_js: Whether to execute JavaScript
            timeout: Request timeout
            
        Returns:
            Dictionary with rendered content
        """
        if output_format == 'markdown':
            return self.render_to_markdown(url, execute_js, timeout)
        elif output_format == 'text':
            return self.render_to_text(url, execute_js, timeout)
        elif output_format == 'html':
            # Return raw HTML
            fetch_result = self.fetch_page(url, timeout)
            if fetch_result['success']:
                result = fetch_result.copy()
                result['format'] = 'html'
                # Content is already HTML from fetch_page
                return result
            return fetch_result
        else:
            return {
                'success': False,
                'url': url,
                'error': f"Unsupported output format: {output_format}",
                'timestamp': datetime.now().isoformat()
            }
            
    def _extract_metadata(self, soup) -> Dict[str, Any]:
        """Extract metadata from BeautifulSoup object"""
        try:
            metadata = {}
            
            # Title
            title_tag = soup.find('title')
            if title_tag:
                metadata['title'] = title_tag.get_text(strip=True)
                
            # Meta tags
            meta_tags = soup.find_all('meta')
            metadata['meta'] = {}
            
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                
                if name and content:
                    metadata['meta'][name] = content
                    
            # Language
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang'):
                metadata['language'] = html_tag.get('lang')
                
            # Character count and word count
            text_content = soup.get_text()
            metadata['character_count'] = len(text_content)
            metadata['word_count'] = len(text_content.split())
            
            # Link count
            links = soup.find_all('a', href=True)
            metadata['link_count'] = len(links)
            
            # Image count
            images = soup.find_all('img')
            metadata['image_count'] = len(images)
            
            return metadata
            
        except Exception as e:
            return {'error': f"Metadata extraction error: {str(e)}"}
            
    def get_browser_info(self) -> Dict[str, Any]:
        """Get information about the browser engine"""
        return {
            'user_agent': self.engine.user_agent,
            'default_timeout': self.default_timeout,
            'history_count': len(self.engine.history),
            'current_url': self.engine.current_url,
            'version': '0.1.0'
        }
        
    def clear_history(self):
        """Clear browsing history"""
        self.engine.history.clear()
        self.engine.current_url = None
        self.engine.current_soup = None
        
    def set_user_agent(self, user_agent: str):
        """Set custom user agent"""
        self.engine.user_agent = user_agent
        self.engine.session.headers.update({'User-Agent': user_agent})
        
    def export_results(self, results: Union[Dict, List[Dict]], 
                      filename: str, format: str = 'json') -> bool:
        """
        Export results to file
        
        Args:
            results: Results to export
            filename: Output filename
            format: Export format ('json', 'csv')
            
        Returns:
            Success status
        """
        try:
            if format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                return True
                
            elif format == 'csv' and isinstance(results, list):
                import csv
                
                if not results:
                    return False
                    
                # Get all possible keys
                all_keys = set()
                for result in results:
                    if isinstance(result, dict):
                        all_keys.update(result.keys())
                        
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
                    writer.writeheader()
                    
                    for result in results:
                        if isinstance(result, dict):
                            # Flatten complex fields
                            flattened = {}
                            for k, v in result.items():
                                if isinstance(v, (dict, list)):
                                    flattened[k] = json.dumps(v)
                                else:
                                    flattened[k] = v
                            writer.writerow(flattened)
                            
                return True
                
            else:
                return False
                
        except Exception as e:
            print(f"Export error: {str(e)}")
            return False


# Example usage functions for SDK
def example_basic_usage():
    """Example of basic SDK usage"""
    sdk = BrowserSDK()
    
    # Fetch and render a page
    result = sdk.render_to_markdown("https://example.com")
    
    if result['success']:
        print("Title:", result.get('metadata', {}).get('title', 'N/A'))
        print("Content length:", len(result['content']))
        print("First 200 characters:")
        print(result['content'][:200])
    else:
        print("Error:", result['error'])


def example_batch_processing():
    """Example of batch processing multiple URLs"""
    sdk = BrowserSDK()
    
    urls = [
        "https://example.com",
        "https://httpbin.org/html",
        "https://google.com"
    ]
    
    results = sdk.batch_process(urls, output_format='text')
    
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Success: {result['success']}")
        if result['success']:
            print(f"Word count: {result.get('metadata', {}).get('word_count', 'N/A')}")
        else:
            print(f"Error: {result['error']}")
        print("-" * 50)


def example_link_extraction():
    """Example of extracting links from a page"""
    sdk = BrowserSDK()
    
    result = sdk.get_page_links("https://news.ycombinator.com")
    
    if result['success']:
        print(f"Found {result['link_count']} links:")
        for link in result['links'][:10]:  # Show first 10
            print(f"- {link['text'][:50]}... -> {link['url']}")
    else:
        print("Error:", result['error'])


if __name__ == "__main__":
    # Run examples
    print("=== Basic Usage Example ===")
    example_basic_usage()
    
    print("\n=== Link Extraction Example ===")
    example_link_extraction()
