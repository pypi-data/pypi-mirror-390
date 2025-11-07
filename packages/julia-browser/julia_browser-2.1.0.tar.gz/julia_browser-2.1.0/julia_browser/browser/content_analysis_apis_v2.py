#!/usr/bin/env python3
"""
Content Analysis APIs for CLI Browser - Simplified and working implementation
"""

import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Tag

class XPathAPI:
    """XPath API with CSS selector fallback for CLI browser automation"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
    
    def xpath(self, expression: str) -> List[Dict[str, Any]]:
        """Execute XPath expression (converted to CSS selector)"""
        css_selector = self._xpath_to_css(expression)
        if css_selector:
            elements = self.soup.select(css_selector)
            return [self._element_to_dict(el) for el in elements]
        
        # Fallback: try basic element matching
        return self._basic_xpath_match(expression)
    
    def _xpath_to_css(self, xpath: str) -> str:
        """Convert common XPath expressions to CSS selectors"""
        # Handle descendant selectors first (// becomes space in CSS)
        css_expr = xpath.replace('//', ' ').strip()
        
        # Common XPath patterns to CSS conversion
        conversions = [
            (r'^([a-zA-Z][a-zA-Z0-9\-]*)$', r'\1'),  # div -> div
            (r'^\*$', '*'),  # * -> *
            (r'([a-zA-Z][a-zA-Z0-9\-]*)\[@class=[\'"]([^\'"]+)[\'"]\]', r'\1.\2'),  # div[@class="foo"] -> div.foo
            (r'([a-zA-Z][a-zA-Z0-9\-]*)\[@id=[\'"]([^\'"]+)[\'"]\]', r'\1#\2'),  # div[@id="foo"] -> div#foo
            (r'([a-zA-Z][a-zA-Z0-9\-]*)\[@data-([^=]+)=[\'"]([^\'"]+)[\'"]\]', r'\1[data-\2="\3"]'),  # data attributes
            (r'([a-zA-Z][a-zA-Z0-9\-]*)\[contains\(@class,[\'"]([^\'"]+)[\'"]\)\]', r'\1[class*="\2"]'),  # contains class
            (r'([a-zA-Z][a-zA-Z0-9\-]*)\[text\(\)=[\'"]([^\'"]+)[\'"]\]', r'\1:contains("\2")'),  # text content
            (r'([a-zA-Z][a-zA-Z0-9\-]*)\[starts-with\(@([^,]+),[\'"]([^\'"]+)[\'"]\)\]', r'\1[\2^="\3"]'),  # starts-with
        ]
        
        # Apply conversions
        for pattern, replacement in conversions:
            css_expr = re.sub(pattern, replacement, css_expr)
        
        # Handle complex expressions that couldn't be converted
        if '[' in css_expr and not re.match(r'^[a-zA-Z][\w\-\s\[\]=:"#.*]+$', css_expr):
            # Extract just the element names for fallback
            element_parts = re.findall(r'([a-zA-Z][a-zA-Z0-9\-]*)', xpath)
            if element_parts:
                return ' '.join(element_parts)
        
        return css_expr if css_expr else ''
    
    def _basic_xpath_match(self, expression: str) -> List[Dict[str, Any]]:
        """Basic XPath matching for common patterns"""
        results = []
        
        if expression == '//*':
            # All elements
            elements = self.soup.find_all()
            results = [self._element_to_dict(el) for el in elements]
        elif expression.startswith('//') and '[' not in expression:
            # Simple element selection like //div, //p
            tag_name = expression[2:]
            elements = self.soup.find_all(tag_name)
            results = [self._element_to_dict(el) for el in elements]
        
        return results
    
    def xpath_text(self, expression: str) -> List[str]:
        """Get text content from XPath expression"""
        results = self.xpath(expression)
        return [r.get('text', '') for r in results]
    
    def xpath_count(self, expression: str) -> int:
        """Count elements matching XPath expression"""
        return len(self.xpath(expression))
    
    def xpath_exists(self, expression: str) -> bool:
        """Check if XPath expression matches any elements"""
        return self.xpath_count(expression) > 0
    
    def _element_to_dict(self, element: Tag) -> Dict[str, Any]:
        """Convert BeautifulSoup element to dictionary"""
        return {
            'type': 'element',
            'tag': element.name,
            'text': element.get_text().strip(),
            'attributes': dict(element.attrs) if element.attrs else {},
            'innerHTML': ''.join(str(child) for child in element.children),
            'outerHTML': str(element)
        }

class EnhancedCSSSelector:
    """Enhanced CSS Selector Engine with additional features"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
    
    def select_advanced(self, selector: str) -> List[Dict[str, Any]]:
        """Enhanced CSS selector with pseudo-classes"""
        try:
            # Handle :contains() pseudo-class
            if ':contains(' in selector:
                return self._select_contains(selector)
            
            # Handle attribute operators
            if any(op in selector for op in ['~=', '|=', '^=', '$=', '*=']):
                return self._select_attribute_operators(selector)
            
            # Default to BeautifulSoup selector
            elements = self.soup.select(selector)
            return [self._element_to_dict(el) for el in elements]
            
        except Exception as e:
            return [{'error': f'CSS selector error: {str(e)}', 'selector': selector}]
    
    def _select_contains(self, selector: str) -> List[Dict[str, Any]]:
        """Handle :contains() pseudo-class"""
        contains_match = re.search(r':contains\(["\']?([^"\']+)["\']?\)', selector)
        if not contains_match:
            return []
        
        contains_text = contains_match.group(1)
        base_selector = selector[:contains_match.start()]
        
        if base_selector:
            elements = self.soup.select(base_selector)
        else:
            elements = self.soup.find_all()
        
        results = []
        for el in elements:
            if contains_text.lower() in el.get_text().lower():
                results.append(self._element_to_dict(el))
        
        return results
    
    def _select_attribute_operators(self, selector: str) -> List[Dict[str, Any]]:
        """Handle advanced attribute operators"""
        # This is a simplified implementation
        try:
            elements = self.soup.select(selector)
            return [self._element_to_dict(el) for el in elements]
        except:
            return []
    
    def select_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Select elements by text pattern"""
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for element in self.soup.find_all():
            text = element.get_text()
            if text and regex.search(text):
                results.append(self._element_to_dict(element))
        
        return results
    
    def _element_to_dict(self, element: Tag) -> Dict[str, Any]:
        """Convert BeautifulSoup element to dictionary"""
        return {
            'type': 'element',
            'tag': element.name,
            'text': element.get_text().strip(),
            'attributes': dict(element.attrs) if element.attrs else {},
            'innerHTML': ''.join(str(child) for child in element.children),
            'outerHTML': str(element),
            'className': element.get('class', []),
            'id': element.get('id', '')
        }

class TextSearchAPI:
    """Advanced text search API for content analysis"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.text_content = soup.get_text()
    
    def search_text(self, query: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Advanced text search with options"""
        if options is None:
            options = {}
            
        case_sensitive = options.get('caseSensitive', False)
        whole_words = options.get('wholeWords', False)
        regex_mode = options.get('regex', False)
        context_length = options.get('contextLength', 100)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        if regex_mode:
            pattern = query
        elif whole_words:
            pattern = r'\b' + re.escape(query) + r'\b'
        else:
            pattern = re.escape(query)
        
        try:
            matches = []
            for match in re.finditer(pattern, self.text_content, flags):
                start = max(0, match.start() - context_length // 2)
                end = min(len(self.text_content), match.end() + context_length // 2)
                context = self.text_content[start:end]
                
                matches.append({
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'context': context,
                    'line': self.text_content[:match.start()].count('\n') + 1
                })
            
            return {
                'query': query,
                'matches': matches,
                'count': len(matches),
                'options': options
            }
        except Exception as e:
            return {'error': f'Text search error: {str(e)}', 'query': query}
    
    def search_in_elements(self, query: str, selector: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search text within specific elements"""
        if selector:
            elements = self.soup.select(selector)
        else:
            elements = self.soup.find_all()
        
        results = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        
        for element in elements:
            text = element.get_text()
            if pattern.search(text):
                matches = list(pattern.finditer(text))
                results.append({
                    'element': {
                        'tag': element.name,
                        'text': text.strip(),
                        'attributes': dict(element.attrs) if element.attrs else {},
                        'outerHTML': str(element)
                    },
                    'matches': [{
                        'match': m.group(),
                        'start': m.start(),
                        'end': m.end()
                    } for m in matches],
                    'count': len(matches)
                })
        
        return results
    
    def extract_patterns(self, patterns: Dict[str, str]) -> Dict[str, Any]:
        """Extract data using named regex patterns"""
        results = {}
        
        for name, pattern in patterns.items():
            try:
                matches = re.findall(pattern, self.text_content, re.IGNORECASE | re.MULTILINE)
                results[name] = matches
            except Exception as e:
                results[name] = {'error': f'Pattern error: {str(e)}'}
        
        return results
    
    def get_text_statistics(self) -> Dict[str, Any]:
        """Get text content statistics"""
        words = self.text_content.split()
        sentences = re.split(r'[.!?]+', self.text_content)
        paragraphs = self.text_content.split('\n\n')
        
        return {
            'characters': len(self.text_content),
            'characters_no_spaces': len(self.text_content.replace(' ', '')),
            'words': len(words),
            'sentences': len([s for s in sentences if s.strip()]),
            'paragraphs': len([p for p in paragraphs if p.strip()]),
            'lines': self.text_content.count('\n') + 1,
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0
        }

class DocumentFragmentAPI:
    """Document Fragment API for efficient DOM manipulation"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
    
    def create_fragment(self, html_content: Optional[str] = None) -> Dict[str, Any]:
        """Create a document fragment"""
        if html_content:
            fragment_soup = BeautifulSoup(html_content, 'html.parser')
        else:
            fragment_soup = BeautifulSoup('', 'html.parser')
        
        children = [child for child in fragment_soup.children if hasattr(child, 'name') and child.name]
        
        return {
            'type': 'DocumentFragment',
            'children': [self._element_to_dict(child) for child in children if isinstance(child, Tag)],
            'innerHTML': str(fragment_soup),
            'childElementCount': len(children),
            'textContent': fragment_soup.get_text()
        }
    
    def clone_nodes(self, selector: str, deep: bool = True) -> Dict[str, Any]:
        """Clone nodes matching selector into a fragment"""
        elements = self.soup.select(selector)
        fragment_html = ''
        
        for element in elements:
            if deep:
                fragment_html += str(element)
            else:
                # Shallow clone - just the element without children
                attrs = ' '.join(f'{k}="{v}"' if isinstance(v, str) else f'{k}="{" ".join(v)}"' 
                                for k, v in element.attrs.items())
                fragment_html += f'<{element.name} {attrs}></{element.name}>'
        
        return self.create_fragment(fragment_html)
    
    def extract_content(self, selector: str, extract_type: str = 'innerHTML') -> Dict[str, Any]:
        """Extract content from elements into a fragment"""
        elements = self.soup.select(selector)
        content_parts = []
        
        for element in elements:
            if extract_type == 'innerHTML':
                content = ''.join(str(child) for child in element.children)
            elif extract_type == 'outerHTML':
                content = str(element)
            elif extract_type == 'textContent':
                content = element.get_text()
            else:
                content = str(element)
            
            content_parts.append(content)
        
        fragment_content = ''.join(content_parts)
        return self.create_fragment(fragment_content)
    
    def _element_to_dict(self, element: Tag) -> Dict[str, Any]:
        """Convert BeautifulSoup element to dictionary"""
        return {
            'type': 'element',
            'tag': element.name,
            'text': element.get_text().strip(),
            'attributes': dict(element.attrs) if element.attrs else {},
            'innerHTML': ''.join(str(child) for child in element.children),
            'outerHTML': str(element)
        }

class ContentAnalysisIntegrator:
    """Integrated content analysis API combining all features"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.xpath_api = XPathAPI(soup)
        self.css_selector = EnhancedCSSSelector(soup)
        self.text_search = TextSearchAPI(soup)
        self.document_fragment = DocumentFragmentAPI(soup)
    
    def get_content_analysis_apis(self) -> Dict[str, Any]:
        """Get all content analysis APIs for JavaScript integration"""
        return {
            # XPath API
            'xpath': self.xpath_api.xpath,
            'xpathText': self.xpath_api.xpath_text,
            'xpathCount': self.xpath_api.xpath_count,
            'xpathExists': self.xpath_api.xpath_exists,
            
            # Enhanced CSS Selector API
            'selectAdvanced': self.css_selector.select_advanced,
            'selectByPattern': self.css_selector.select_by_pattern,
            
            # Text Search API
            'searchText': self.text_search.search_text,
            'searchInElements': self.text_search.search_in_elements,
            'extractPatterns': self.text_search.extract_patterns,
            'getTextStatistics': self.text_search.get_text_statistics,
            
            # Document Fragment API
            'createFragment': self.document_fragment.create_fragment,
            'cloneNodes': self.document_fragment.clone_nodes,
            'extractContent': self.document_fragment.extract_content
        }