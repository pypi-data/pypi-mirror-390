"""
CSS Generated Content Extractor - Extract text from ::before and ::after pseudo-elements
Critical for CLI browsers to capture content added via CSS
"""

from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import re
import json

class CSSGeneratedContentExtractor:
    """Extracts content from CSS pseudo-elements (::before, ::after)"""
    
    def __init__(self):
        self.generated_content = {}
        self.css_counters = {}
        
    def extract_generated_content(self, soup: BeautifulSoup, css_rules: Dict = None) -> str:
        """
        Extract content from CSS ::before and ::after pseudo-elements
        
        Args:
            soup: BeautifulSoup parsed HTML
            css_rules: Parsed CSS rules containing generated content
            
        Returns:
            Additional text content from CSS pseudo-elements
        """
        try:
            if not css_rules:
                return ""
                
            generated_content = []
            
            # 1. Extract ::before and ::after content
            pseudo_content = self._extract_pseudo_element_content(soup, css_rules)
            if pseudo_content:
                generated_content.extend(pseudo_content)
            
            # 2. Extract CSS counter content
            counter_content = self._extract_css_counter_content(soup, css_rules)
            if counter_content:
                generated_content.extend(counter_content)
            
            # 3. Extract content from CSS attr() functions
            attr_content = self._extract_css_attr_content(soup, css_rules)
            if attr_content:
                generated_content.extend(attr_content)
            
            # 4. Extract list marker content
            list_content = self._extract_list_marker_content(soup, css_rules)
            if list_content:
                generated_content.extend(list_content)
            
            return "\n".join(generated_content)
            
        except Exception as e:
            return f"<!-- CSS generated content extraction error: {str(e)} -->"
    
    def _extract_pseudo_element_content(self, soup: BeautifulSoup, css_rules: Dict) -> List[str]:
        """Extract content from ::before and ::after pseudo-elements"""
        try:
            pseudo_content = []
            
            for selector, rules in css_rules.items():
                # Check for ::before and ::after selectors
                if '::before' in selector or ':before' in selector:
                    content = self._get_pseudo_content(rules, 'before')
                    if content:
                        elements = self._find_elements_for_selector(soup, selector.replace('::before', '').replace(':before', ''))
                        for element in elements:
                            element_desc = self._describe_element(element)
                            pseudo_content.append(f"Before {element_desc}: {content}")
                
                elif '::after' in selector or ':after' in selector:
                    content = self._get_pseudo_content(rules, 'after')
                    if content:
                        elements = self._find_elements_for_selector(soup, selector.replace('::after', '').replace(':after', ''))
                        for element in elements:
                            element_desc = self._describe_element(element)
                            pseudo_content.append(f"After {element_desc}: {content}")
            
            return pseudo_content
            
        except Exception as e:
            return [f"<!-- Pseudo-element extraction error: {str(e)} -->"]
    
    def _extract_css_counter_content(self, soup: BeautifulSoup, css_rules: Dict) -> List[str]:
        """Extract content from CSS counters"""
        try:
            counter_content = []
            counter_values = {}
            
            # First pass: find counter-reset and counter-increment
            for selector, rules in css_rules.items():
                if 'counter-reset' in rules:
                    counter_name = rules['counter-reset'].strip()
                    if counter_name and counter_name != 'none':
                        counter_values[counter_name] = 0
                
                if 'counter-increment' in rules:
                    counter_name = rules['counter-increment'].strip()
                    if counter_name in counter_values:
                        counter_values[counter_name] += 1
                    else:
                        counter_values[counter_name] = 1
            
            # Second pass: find counter() usage in content
            for selector, rules in css_rules.items():
                if 'content' in rules:
                    content_value = rules['content']
                    
                    # Look for counter() functions
                    counter_matches = re.findall(r'counter\(\s*([^)]+)\s*\)', content_value)
                    
                    for counter_match in counter_matches:
                        counter_parts = [part.strip().strip('"\'') for part in counter_match.split(',')]
                        counter_name = counter_parts[0]
                        counter_style = counter_parts[1] if len(counter_parts) > 1 else 'decimal'
                        
                        if counter_name in counter_values:
                            counter_val = self._format_counter_value(counter_values[counter_name], counter_style)
                            elements = self._find_elements_for_selector(soup, selector.replace('::before', '').replace(':before', '').replace('::after', '').replace(':after', ''))
                            
                            for element in elements:
                                element_desc = self._describe_element(element)
                                counter_content.append(f"Counter {element_desc}: {counter_val}")
            
            return counter_content
            
        except Exception as e:
            return [f"<!-- Counter extraction error: {str(e)} -->"]
    
    def _extract_css_attr_content(self, soup: BeautifulSoup, css_rules: Dict) -> List[str]:
        """Extract content from CSS attr() functions"""
        try:
            attr_content = []
            
            for selector, rules in css_rules.items():
                if 'content' in rules:
                    content_value = rules['content']
                    
                    # Look for attr() functions
                    attr_matches = re.findall(r'attr\(\s*([^)]+)\s*\)', content_value)
                    
                    for attr_name in attr_matches:
                        attr_name = attr_name.strip().strip('"\'')
                        elements = self._find_elements_for_selector(soup, selector.replace('::before', '').replace(':before', '').replace('::after', '').replace(':after', ''))
                        
                        for element in elements:
                            attr_value = element.get(attr_name)
                            if attr_value:
                                element_desc = self._describe_element(element)
                                pseudo_type = 'before' if '::before' in selector or ':before' in selector else 'after'
                                attr_content.append(f"{pseudo_type.title()} {element_desc} ({attr_name}): {attr_value}")
            
            return attr_content
            
        except Exception as e:
            return [f"<!-- Attr extraction error: {str(e)} -->"]
    
    def _extract_list_marker_content(self, soup: BeautifulSoup, css_rules: Dict) -> List[str]:
        """Extract content from list markers and custom list styling"""
        try:
            list_content = []
            
            # Find list elements
            lists = soup.find_all(['ul', 'ol'])
            
            for list_elem in lists:
                list_items = list_elem.find_all('li')
                
                # Check for custom list-style-type
                list_style = self._get_list_style_for_element(list_elem, css_rules)
                
                if list_style and list_style not in ['disc', 'circle', 'square', 'decimal', 'none']:
                    for i, item in enumerate(list_items):
                        marker = self._generate_list_marker(i + 1, list_style)
                        if marker:
                            item_text = item.get_text(strip=True)[:50]  # First 50 chars
                            list_content.append(f"List marker: {marker} ({item_text}...)")
            
            # Look for ::marker pseudo-element styling
            for selector, rules in css_rules.items():
                if '::marker' in selector:
                    if 'content' in rules:
                        marker_content = self._clean_css_content_value(rules['content'])
                        elements = self._find_elements_for_selector(soup, selector.replace('::marker', ''))
                        
                        for element in elements:
                            element_desc = self._describe_element(element)
                            list_content.append(f"Custom marker {element_desc}: {marker_content}")
            
            return list_content
            
        except Exception as e:
            return [f"<!-- List marker extraction error: {str(e)} -->"]
    
    def _get_pseudo_content(self, rules: Dict, pseudo_type: str) -> str:
        """Get content value from CSS rules"""
        try:
            if 'content' not in rules:
                return ""
            
            content_value = rules['content']
            return self._clean_css_content_value(content_value)
            
        except Exception:
            return ""
    
    def _clean_css_content_value(self, content_value: str) -> str:
        """Clean CSS content value and extract text"""
        try:
            # Remove quotes
            cleaned = content_value.strip().strip('"\'')
            
            # Handle special values
            if cleaned in ['none', 'normal', 'initial', 'inherit', 'unset']:
                return ""
            
            # Handle string concatenation (multiple quoted strings)
            parts = re.findall(r'["\']([^"\']*)["\']', content_value)
            if parts:
                return ''.join(parts)
            
            # Handle escape sequences
            cleaned = cleaned.replace('\\A', '\n').replace('\\D', '\r')
            cleaned = re.sub(r'\\([0-9A-Fa-f]{1,6})', lambda m: chr(int(m.group(1), 16)), cleaned)
            
            return cleaned
            
        except Exception:
            return content_value
    
    def _find_elements_for_selector(self, soup: BeautifulSoup, selector: str) -> List[Tag]:
        """Find elements matching a CSS selector"""
        try:
            selector = selector.strip()
            
            if not selector:
                return []
            
            # Handle basic selectors
            if selector.startswith('#'):
                # ID selector
                element = soup.find(id=selector[1:])
                return [element] if element else []
            
            elif selector.startswith('.'):
                # Class selector
                return soup.find_all(class_=selector[1:])
            
            elif ':' not in selector and '[' not in selector:
                # Simple tag selector
                return soup.find_all(selector)
            
            else:
                # Complex selector - try CSS select if available
                try:
                    return soup.select(selector)
                except:
                    # Fallback to tag name only
                    tag_match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)', selector)
                    if tag_match:
                        return soup.find_all(tag_match.group(1))
            
            return []
            
        except Exception:
            return []
    
    def _describe_element(self, element: Tag) -> str:
        """Create a description of an element for content labeling"""
        try:
            parts = [f"<{element.name}>"]
            
            if element.get('id'):
                parts.append(f"#{element.get('id')}")
            
            if element.get('class'):
                classes = element.get('class')
                if isinstance(classes, list):
                    parts.append(f".{'.'.join(classes[:2])}")  # First 2 classes
                else:
                    parts.append(f".{classes}")
            
            # Add a bit of text content for context
            text = element.get_text(strip=True)[:30]
            if text:
                parts.append(f'"{text}..."')
            
            return " ".join(parts)
            
        except Exception:
            return f"<{element.name}>"
    
    def _get_list_style_for_element(self, element: Tag, css_rules: Dict) -> str:
        """Get the list-style-type for a list element"""
        try:
            # Check CSS rules for this element
            for selector, rules in css_rules.items():
                if 'list-style-type' in rules:
                    # Check if selector matches this element
                    if self._selector_matches_element(selector, element):
                        return rules['list-style-type']
            
            # Default list styles
            if element.name == 'ol':
                return 'decimal'
            elif element.name == 'ul':
                return 'disc'
            
            return 'disc'
            
        except Exception:
            return 'disc'
    
    def _selector_matches_element(self, selector: str, element: Tag) -> bool:
        """Check if a CSS selector matches an element"""
        try:
            # Simple matching logic
            if selector == element.name:
                return True
            
            if selector.startswith('#') and element.get('id') == selector[1:]:
                return True
            
            if selector.startswith('.') and selector[1:] in (element.get('class') or []):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _generate_list_marker(self, index: int, style: str) -> str:
        """Generate list marker based on style"""
        try:
            if style == 'decimal':
                return str(index)
            elif style == 'lower-roman':
                return self._to_roman(index).lower()
            elif style == 'upper-roman':
                return self._to_roman(index).upper()
            elif style == 'lower-alpha' or style == 'lower-latin':
                return chr(ord('a') + (index - 1) % 26)
            elif style == 'upper-alpha' or style == 'upper-latin':
                return chr(ord('A') + (index - 1) % 26)
            elif style == 'disc':
                return '•'
            elif style == 'circle':
                return '○'
            elif style == 'square':
                return '■'
            
            return str(index)
            
        except Exception:
            return str(index)
    
    def _to_roman(self, num: int) -> str:
        """Convert number to Roman numerals"""
        try:
            values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
            numerals = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
            
            result = ''
            for i, value in enumerate(values):
                count = num // value
                result += numerals[i] * count
                num -= value * count
            
            return result
            
        except Exception:
            return str(num)
    
    def _format_counter_value(self, value: int, style: str) -> str:
        """Format counter value according to style"""
        try:
            if style == 'decimal':
                return str(value)
            elif style == 'lower-roman':
                return self._to_roman(value).lower()
            elif style == 'upper-roman':
                return self._to_roman(value).upper()
            elif style == 'lower-alpha':
                return chr(ord('a') + (value - 1) % 26)
            elif style == 'upper-alpha':
                return chr(ord('A') + (value - 1) % 26)
            
            return str(value)
            
        except Exception:
            return str(value)