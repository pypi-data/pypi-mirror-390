#!/usr/bin/env python3
"""
Content Analysis APIs for CLI Browser - XPath, Enhanced CSS Selectors, Text Search, Document Fragments
"""

import re
from typing import List, Dict, Any, Optional, Union
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import json

# Try to import lxml, fallback to basic XML parsing if not available
try:
    from lxml import etree, html
    LXML_AVAILABLE = True
except ImportError:
    import xml.etree.ElementTree as etree
    LXML_AVAILABLE = False

class XPathAPI:
    """Complete XPath API implementation for advanced element selection"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.html_content = str(soup)
        
        if LXML_AVAILABLE:
            try:
                self.doc = html.fromstring(self.html_content)
            except:
                # Fallback for malformed HTML
                self.doc = html.document_fromstring(self.html_content)
        else:
            # Basic XPath simulation without lxml
            self.doc = None
    
    def xpath(self, expression: str) -> List[Dict[str, Any]]:
        """Execute XPath expression and return matching elements"""
        if not LXML_AVAILABLE or self.doc is None:
            return self._xpath_fallback(expression)
        
        try:
            elements = self.doc.xpath(expression)
            results = []
            
            for element in elements:
                if hasattr(element, 'tag'):
                    # Element node
                    result = {
                        'type': 'element',
                        'tag': element.tag,
                        'text': element.text_content().strip() if element.text_content() else '',
                        'attributes': dict(element.attrib),
                        'xpath': self._get_element_xpath(element),
                        'innerHTML': etree.tostring(element, encoding='unicode', method='html'),
                        'outerHTML': etree.tostring(element, encoding='unicode', method='html')
                    }
                else:
                    # Text node or attribute
                    result = {
                        'type': 'text',
                        'value': str(element),
                        'text': str(element)
                    }
                results.append(result)
            
            return results
        except Exception as e:
            return [{'error': f'XPath error: {str(e)}', 'expression': expression}]
    
    def _xpath_fallback(self, expression: str) -> List[Dict[str, Any]]:
        """Fallback XPath implementation using BeautifulSoup"""
        # Basic XPath patterns to CSS selector conversion
        css_selector = self._xpath_to_css(expression)
        if css_selector:
            elements = self.soup.select(css_selector)
            return [self._element_to_dict(el) for el in elements if isinstance(el, Tag)]
        
        return [{'error': f'XPath not supported without lxml: {expression}', 'fallback': 'Using CSS selectors'}]
    
    def _xpath_to_css(self, xpath: str) -> str:
        """Convert basic XPath expressions to CSS selectors"""
        # Simple XPath to CSS conversion
        xpath_patterns = {
            r'^//([a-zA-Z][a-zA-Z0-9]*)$': r'\1',  # //div -> div
            r'^//\*$': '*',  # //* -> *
            r'//([a-zA-Z][a-zA-Z0-9]*)\[@([^=]+)=([\'"][^"\']+[\'"])\]': r'\1[\2=\3]',  # //div[@class="foo"] -> div[class="foo"]
            r'//([a-zA-Z][a-zA-Z0-9]*)\[@([^=]+)\]': r'\1[\2]',  # //div[@class] -> div[class]
        }
        
        for pattern, replacement in xpath_patterns.items():
            if re.match(pattern, xpath):
                return re.sub(pattern, replacement, xpath)
        
        return ''
    
    def _get_element_xpath(self, element) -> str:
        """Generate XPath for an element"""
        if not LXML_AVAILABLE or self.doc is None:
            return ''
        try:
            return self.doc.getroottree().getpath(element)
        except:
            return ''
    
    def xpath_text(self, expression: str) -> List[str]:
        """Get text content from XPath expression"""
        results = self.xpath(expression)
        return [r.get('text', '') for r in results if r.get('text')]
    
    def xpath_attributes(self, expression: str, attribute: str) -> List[str]:
        """Get specific attribute values from XPath expression"""
        results = self.xpath(expression)
        return [r.get('attributes', {}).get(attribute, '') for r in results if r.get('attributes')]
    
    def xpath_count(self, expression: str) -> int:
        """Count elements matching XPath expression"""
        return len(self.xpath(expression))
    
    def xpath_exists(self, expression: str) -> bool:
        """Check if XPath expression matches any elements"""
        return self.xpath_count(expression) > 0

class EnhancedCSSSelector:
    """Enhanced CSS Selector Engine with advanced selector support"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
    
    def select_advanced(self, selector: str) -> List[Dict[str, Any]]:
        """Enhanced CSS selector with additional pseudo-classes and combinators"""
        try:
            # Handle advanced selectors not supported by BeautifulSoup
            elements = []
            
            # CSS4 pseudo-classes
            if ':contains(' in selector:
                elements = self._select_contains(selector)
            elif ':matches(' in selector or ':is(' in selector:
                elements = self._select_matches(selector)
            elif ':not(' in selector and selector.count(':not(') > 1:
                elements = self._select_complex_not(selector)
            elif '[*]' in selector:
                elements = self._select_any_attribute(selector)
            elif '~=' in selector or '|=' in selector or '^=' in selector or '$=' in selector or '*=' in selector:
                elements = self._select_attribute_operators(selector)
            else:
                # Use BeautifulSoup's built-in selector
                soup_elements = self.soup.select(selector)
                elements = [self._element_to_dict(el) for el in soup_elements]
            
            return elements
        except Exception as e:
            return [{'error': f'CSS selector error: {str(e)}', 'selector': selector}]
    
    def _select_contains(self, selector: str) -> List[Dict[str, Any]]:
        """Handle :contains() pseudo-class"""
        # Extract the contains text
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
    
    def _select_matches(self, selector: str) -> List[Dict[str, Any]]:
        """Handle :matches() or :is() pseudo-class"""
        # Extract selectors inside :matches() or :is()
        match_pattern = r':(?:matches|is)\(([^)]+)\)'
        match_obj = re.search(match_pattern, selector)
        if not match_obj:
            return []
        
        inner_selectors = [s.strip() for s in match_obj.group(1).split(',')]
        base_selector = selector[:match_obj.start()]
        
        results = []
        for inner_sel in inner_selectors:
            full_selector = base_selector + inner_sel if base_selector else inner_sel
            elements = self.soup.select(full_selector)
            results.extend([self._element_to_dict(el) for el in elements])
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in results:
            key = result.get('outerHTML', '')
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        return unique_results
    
    def _select_complex_not(self, selector: str) -> List[Dict[str, Any]]:
        """Handle complex :not() selectors"""
        # For now, use basic implementation
        try:
            elements = self.soup.select(selector)
            return [self._element_to_dict(el) for el in elements]
        except:
            return []
    
    def _select_any_attribute(self, selector: str) -> List[Dict[str, Any]]:
        """Handle [*] selector (elements with any attribute)"""
        base_selector = selector.replace('[*]', '')
        if base_selector:
            elements = self.soup.select(base_selector)
        else:
            elements = self.soup.find_all()
        
        results = []
        for el in elements:
            if el.attrs:  # Has any attributes
                results.append(self._element_to_dict(el))
        
        return results
    
    def _select_attribute_operators(self, selector: str) -> List[Dict[str, Any]]:
        """Handle advanced attribute operators"""
        # Extract attribute conditions
        attr_patterns = {
            r'\[([^=~|^$*]+)~=([^]]+)\]': 'word',      # word match
            r'\[([^=~|^$*]+)\|=([^]]+)\]': 'lang',      # language match
            r'\[([^=~|^$*]+)\^=([^]]+)\]': 'prefix',    # prefix match
            r'\[([^=~|^$*]+)\$=([^]]+)\]': 'suffix',    # suffix match
            r'\[([^=~|^$*]+)\*=([^]]+)\]': 'substring', # substring match
        }
        
        for pattern, match_type in attr_patterns.items():
            match = re.search(pattern, selector)
            if match:
                attr_name = match.group(1).strip()
                attr_value = match.group(2).strip('\'"')
                base_selector = selector[:match.start()] + selector[match.end():]
                
                if base_selector:
                    elements = self.soup.select(base_selector)
                else:
                    elements = self.soup.find_all()
                
                results = []
                for el in elements:
                    el_attr_value = el.get(attr_name, '')
                    if self._matches_attribute_condition(el_attr_value, attr_value, match_type):
                        results.append(self._element_to_dict(el))
                
                return results
        
        return []
    
    def _matches_attribute_condition(self, el_value: str, target_value: str, match_type: str) -> bool:
        """Check if attribute value matches the condition"""
        if match_type == 'word':
            return target_value in el_value.split()
        elif match_type == 'lang':
            return el_value == target_value or el_value.startswith(target_value + '-')
        elif match_type == 'prefix':
            return el_value.startswith(target_value)
        elif match_type == 'suffix':
            return el_value.endswith(target_value)
        elif match_type == 'substring':
            return target_value in el_value
        return False
    
    def _element_to_dict(self, element: Tag) -> Dict[str, Any]:
        """Convert BeautifulSoup element to dictionary"""
        return {
            'type': 'element',
            'tag': element.name,
            'text': element.get_text().strip(),
            'attributes': dict(element.attrs),
            'innerHTML': ''.join(str(child) for child in element.children),
            'outerHTML': str(element),
            'className': element.get('class', []),
            'id': element.get('id', ''),
        }
    
    def select_by_pattern(self, pattern: str) -> List[Dict[str, Any]]:
        """Select elements by text pattern"""
        results = []
        regex = re.compile(pattern, re.IGNORECASE)
        
        for element in self.soup.find_all():
            if element.string and regex.search(element.string):
                results.append(self._element_to_dict(element))
        
        return results

class TextSearchAPI:
    """Advanced text search API for content analysis"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
        self.text_content = soup.get_text()
    
    def search_text(self, query: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Advanced text search with options"""
        options = options or {}
        case_sensitive = options.get('caseSensitive', False)
        whole_words = options.get('wholeWords', False)
        regex = options.get('regex', False)
        context_length = options.get('contextLength', 100)
        
        flags = 0 if case_sensitive else re.IGNORECASE
        
        if regex:
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
    
    def search_in_elements(self, query: str, selector: str = None) -> List[Dict[str, Any]]:
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
                        'attributes': dict(element.attrs),
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
    
    def extract_patterns(self, patterns: Dict[str, str]) -> Dict[str, List[str]]:
        """Extract data using named regex patterns"""
        results = {}
        
        for name, pattern in patterns.items():
            try:
                matches = re.findall(pattern, self.text_content, re.IGNORECASE | re.MULTILINE)
                results[name] = matches if isinstance(matches[0], str) if matches else []
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
            'average_word_length': sum(len(word) for word in words) / len(words) if words else 0,
            'most_common_words': self._get_word_frequency(words)[:10]
        }
    
    def _get_word_frequency(self, words: List[str]) -> List[tuple]:
        """Get word frequency count"""
        word_count = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word and len(clean_word) > 2:  # Skip short words
                word_count[clean_word] = word_count.get(clean_word, 0) + 1
        
        return sorted(word_count.items(), key=lambda x: x[1], reverse=True)

class DocumentFragmentAPI:
    """Document Fragment API for efficient DOM manipulation"""
    
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup
    
    def create_fragment(self, html_content: str = None) -> Dict[str, Any]:
        """Create a document fragment"""
        fragment_soup = BeautifulSoup('', 'html.parser')
        
        if html_content:
            fragment_soup = BeautifulSoup(html_content, 'html.parser')
        
        return {
            'type': 'DocumentFragment',
            'children': [self._element_to_dict(child) for child in fragment_soup.children if hasattr(child, 'name')],
            'innerHTML': str(fragment_soup),
            'childElementCount': len([child for child in fragment_soup.children if hasattr(child, 'name')]),
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
    
    def merge_fragments(self, fragments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple fragments into one"""
        merged_html = ''.join(fragment.get('innerHTML', '') for fragment in fragments)
        return self.create_fragment(merged_html)
    
    def filter_fragment(self, fragment: Dict[str, Any], filter_selector: str) -> Dict[str, Any]:
        """Filter fragment content by selector"""
        fragment_soup = BeautifulSoup(fragment.get('innerHTML', ''), 'html.parser')
        filtered_elements = fragment_soup.select(filter_selector)
        filtered_html = ''.join(str(el) for el in filtered_elements)
        
        return self.create_fragment(filtered_html)
    
    def _element_to_dict(self, element: Tag) -> Dict[str, Any]:
        """Convert BeautifulSoup element to dictionary"""
        return {
            'type': 'element',
            'tag': element.name,
            'text': element.get_text().strip() if hasattr(element, 'get_text') else str(element),
            'attributes': dict(element.attrs) if hasattr(element, 'attrs') else {},
            'innerHTML': ''.join(str(child) for child in element.children) if hasattr(element, 'children') else '',
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
    
    def analyze_content(self, analysis_config: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive content analysis"""
        results = {
            'timestamp': str(__import__('datetime').datetime.now()),
            'analysis_config': analysis_config
        }
        
        # XPath analysis
        if 'xpath' in analysis_config:
            results['xpath_results'] = {}
            for name, expression in analysis_config['xpath'].items():
                results['xpath_results'][name] = self.xpath_api.xpath(expression)
        
        # CSS selector analysis
        if 'selectors' in analysis_config:
            results['selector_results'] = {}
            for name, selector in analysis_config['selectors'].items():
                results['selector_results'][name] = self.css_selector.select_advanced(selector)
        
        # Text search analysis
        if 'text_search' in analysis_config:
            results['text_search_results'] = {}
            for name, config in analysis_config['text_search'].items():
                query = config.get('query', '')
                options = config.get('options', {})
                results['text_search_results'][name] = self.text_search.search_text(query, options)
        
        # Pattern extraction
        if 'patterns' in analysis_config:
            results['pattern_results'] = self.text_search.extract_patterns(analysis_config['patterns'])
        
        # Document fragment operations
        if 'fragments' in analysis_config:
            results['fragment_results'] = {}
            for name, config in analysis_config['fragments'].items():
                operation = config.get('operation', 'extract')
                selector = config.get('selector', '')
                
                if operation == 'extract':
                    extract_type = config.get('type', 'innerHTML')
                    results['fragment_results'][name] = self.document_fragment.extract_content(selector, extract_type)
                elif operation == 'clone':
                    deep = config.get('deep', True)
                    results['fragment_results'][name] = self.document_fragment.clone_nodes(selector, deep)
        
        # Text statistics
        if analysis_config.get('include_statistics', False):
            results['text_statistics'] = self.text_search.get_text_statistics()
        
        return results
    
    def get_all_apis(self) -> Dict[str, Any]:
        """Get all available content analysis APIs"""
        return {
            'xpath': {
                'xpath': 'Execute XPath expressions',
                'xpath_text': 'Get text content from XPath',
                'xpath_attributes': 'Get attribute values from XPath',
                'xpath_count': 'Count matching elements',
                'xpath_exists': 'Check if XPath matches'
            },
            'css_selectors': {
                'select_advanced': 'Enhanced CSS selector with CSS4 support',
                'select_by_pattern': 'Select by text pattern'
            },
            'text_search': {
                'search_text': 'Advanced text search with options',
                'search_in_elements': 'Search within specific elements',
                'extract_patterns': 'Extract using regex patterns',
                'get_text_statistics': 'Text content statistics'
            },
            'document_fragments': {
                'create_fragment': 'Create document fragment',
                'clone_nodes': 'Clone elements into fragment',
                'extract_content': 'Extract content into fragment',
                'merge_fragments': 'Merge multiple fragments',
                'filter_fragment': 'Filter fragment by selector'
            }
        }