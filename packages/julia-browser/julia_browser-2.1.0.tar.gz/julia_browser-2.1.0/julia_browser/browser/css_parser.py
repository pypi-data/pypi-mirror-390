"""
CSS Parser - Extracts and parses CSS rules from HTML pages
"""

from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
import re
import requests
import base64
import urllib.parse


class CSSParser:
    """Parses CSS from HTML pages and converts rules to usable format"""
    
    def __init__(self):
        """Initialize CSS parser"""
        self.parsed_rules = {}
        
    def extract_css_from_soup(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """
        Extract all CSS rules from HTML document
        
        Args:
            soup: BeautifulSoup parsed HTML
            
        Returns:
            Dictionary of CSS rules {selector: {property: value}}
        """
        all_rules = {}
        
        try:
            # Extract inline styles
            inline_rules = self._extract_inline_styles(soup)
            all_rules.update(inline_rules)
            
            # Extract embedded CSS from <style> tags
            embedded_rules = self._extract_embedded_css(soup)
            all_rules.update(embedded_rules)
            
            # Extract CSS from external stylesheets
            external_rules = self._extract_external_css(soup)
            all_rules.update(external_rules)
            
            return all_rules
            
        except Exception as e:
            print(f"Error extracting CSS: {str(e)}")
            return {}
            
    def _extract_inline_styles(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """Extract CSS rules from inline style attributes"""
        rules = {}
        
        try:
            elements_with_style = soup.find_all(attrs={'style': True})
            
            for i, element in enumerate(elements_with_style):
                style_attr = element.get('style', '')
                if style_attr:
                    # Create unique selector for inline styles
                    selector = f"inline-{i}"
                    if element.get('id'):
                        selector = f"#{element['id']}"
                    elif element.get('class'):
                        selector = f".{element['class'][0]}"
                    else:
                        selector = f"{element.name}-inline-{i}"
                        
                    parsed_style = self._parse_css_properties(style_attr)
                    if parsed_style:
                        rules[selector] = parsed_style
                        
        except Exception as e:
            print(f"Error extracting inline styles: {str(e)}")
            
        return rules
        
    def _extract_embedded_css(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """Extract CSS rules from <style> tags"""
        rules = {}
        
        try:
            style_tags = soup.find_all('style')
            
            for style_tag in style_tags:
                if style_tag.string:
                    css_content = style_tag.string
                    parsed_rules = self._parse_css_content(css_content)
                    rules.update(parsed_rules)
                    
        except Exception as e:
            print(f"Error extracting embedded CSS: {str(e)}")
            
        return rules
        
    def _extract_external_css(self, soup: BeautifulSoup) -> Dict[str, Dict[str, str]]:
        """Extract CSS rules from external stylesheets"""
        rules = {}
        
        try:
            link_tags = soup.find_all('link', rel='stylesheet')
            
            for link_tag in link_tags:
                href = link_tag.get('href')
                if href:
                    try:
                        # Handle data URIs (inline CSS)
                        if href.startswith('data:'):
                            css_content = self._parse_data_uri(href)
                            if css_content:
                                parsed_rules = self._parse_css_content(css_content)
                                rules.update(parsed_rules)
                            continue
                            
                        # Fix protocol-relative URLs (like //fonts.googleapis.com/...)
                        if href.startswith('//'):
                            href = f"https:{href}"
                        elif href.startswith('/'):
                            # Handle relative URLs by prepending domain
                            href = urllib.parse.urljoin('https://www.google.com', href)
                            
                        # Fetch external CSS (with timeout to avoid hanging)
                        response = requests.get(href, timeout=10)
                        if response.status_code == 200:
                            css_content = response.text
                            parsed_rules = self._parse_css_content(css_content)
                            rules.update(parsed_rules)
                    except Exception as e:
                        # Suppress CSS URL errors for cleaner output - don't show data URI errors
                        if not any(pattern in str(e) for pattern in ['Invalid URL', 'No scheme supplied', 'data:', 'No connection adapters']):
                            print(f"Error fetching external CSS {href}: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error extracting external CSS: {str(e)}")
            
        return rules
    
    def _parse_data_uri(self, data_uri: str) -> Optional[str]:
        """Parse CSS content from data URI"""
        try:
            # Data URI format: data:[<mediatype>][;base64],<data>
            if not data_uri.startswith('data:'):
                return None
                
            # Remove 'data:' prefix
            uri_content = data_uri[5:]
            
            # Check if it's CSS
            if not uri_content.startswith('text/css'):
                return None
            
            # Find the comma separator
            comma_index = uri_content.find(',')
            if comma_index == -1:
                return None
                
            header = uri_content[:comma_index]
            content = uri_content[comma_index + 1:]
            
            # Check if it's base64 encoded
            if ';base64' in header:
                try:
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    return decoded_content
                except Exception:
                    return None
            else:
                # URL decode the content
                return urllib.parse.unquote(content)
                
        except Exception as e:
            # Silently handle data URI parsing errors
            return None
        
    def _parse_css_content(self, css_content: str) -> Dict[str, Dict[str, str]]:
        """Parse CSS content and extract rules"""
        rules = {}
        
        try:
            # Remove CSS comments
            css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
            
            # Basic CSS rule regex pattern
            # This is a simplified parser - a full CSS parser would be more complex
            rule_pattern = r'([^{]+)\{([^}]+)\}'
            matches = re.findall(rule_pattern, css_content, re.MULTILINE | re.DOTALL)
            
            for selector_group, properties in matches:
                # Handle multiple selectors separated by commas
                selectors = [s.strip() for s in selector_group.split(',')]
                
                parsed_properties = self._parse_css_properties(properties)
                
                for selector in selectors:
                    if selector and parsed_properties:
                        rules[selector] = parsed_properties
                        
        except Exception as e:
            print(f"Error parsing CSS content: {str(e)}")
            
        return rules
        
    def _parse_css_properties(self, properties_string: str) -> Dict[str, str]:
        """Parse CSS properties string into dictionary"""
        properties = {}
        
        try:
            # Split by semicolon and parse each property
            property_pairs = properties_string.split(';')
            
            for pair in property_pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key and value:
                        properties[key] = value
                        
        except Exception as e:
            print(f"Error parsing CSS properties: {str(e)}")
            
        return properties
        
    def get_element_styles(self, element_selector: str, all_rules: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Get computed styles for a specific element selector"""
        computed_styles = {}
        
        try:
            # This is a simplified implementation
            # A full CSS engine would handle specificity, cascading, inheritance, etc.
            
            for selector, rules in all_rules.items():
                if self._selector_matches(selector, element_selector):
                    computed_styles.update(rules)
                    
        except Exception as e:
            print(f"Error computing element styles: {str(e)}")
            
        return computed_styles
        
    def _selector_matches(self, css_selector: str, element_selector: str) -> bool:
        """Check if CSS selector matches element selector (simplified)"""
        try:
            # Very basic matching - a full implementation would handle complex selectors
            css_selector = css_selector.strip().lower()
            element_selector = element_selector.strip().lower()
            
            # Exact match
            if css_selector == element_selector:
                return True
                
            # Tag name match
            if css_selector == element_selector.split('#')[0].split('.')[0]:
                return True
                
            # ID match
            if css_selector.startswith('#') and f"#{element_selector}" == css_selector:
                return True
                
            # Class match
            if css_selector.startswith('.') and f".{element_selector}" == css_selector:
                return True
                
            return False
            
        except Exception:
            return False
            
    def get_font_styles(self, rules: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Extract font-related styles for text formatting"""
        font_styles = {}
        
        try:
            for selector, properties in rules.items():
                for prop, value in properties.items():
                    if prop.startswith('font-') or prop in ['color', 'text-decoration', 'text-transform']:
                        if selector not in font_styles:
                            font_styles[selector] = {}
                        font_styles[selector][prop] = value
                        
        except Exception as e:
            print(f"Error extracting font styles: {str(e)}")
            
        return font_styles
        
    def get_layout_styles(self, rules: Dict[str, Dict[str, str]]) -> Dict[str, str]:
        """Extract layout-related styles"""
        layout_styles = {}
        
        try:
            layout_properties = [
                'display', 'position', 'float', 'clear', 'width', 'height',
                'margin', 'padding', 'border', 'background'
            ]
            
            for selector, properties in rules.items():
                for prop, value in properties.items():
                    if any(prop.startswith(layout_prop) for layout_prop in layout_properties):
                        if selector not in layout_styles:
                            layout_styles[selector] = {}
                        layout_styles[selector][prop] = value
                        
        except Exception as e:
            print(f"Error extracting layout styles: {str(e)}")
            
        return layout_styles
