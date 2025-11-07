"""
Web Components Content Extractor - Extract text from Shadow DOM and Custom Elements
Critical for CLI browsers to access content hidden in Web Components
"""

from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup, Tag
import re
import json

class WebComponentsExtractor:
    """Extracts content from Web Components and Shadow DOM for CLI rendering"""
    
    def __init__(self):
        self.shadow_dom_content = {}
        self.custom_elements = {}
        self.component_registry = {}
        
    def extract_web_components_content(self, soup: BeautifulSoup, js_context: Dict = None) -> str:
        """
        Extract all content from Web Components, Shadow DOM, and Custom Elements
        
        Args:
            soup: BeautifulSoup parsed HTML
            js_context: JavaScript execution context with component definitions
            
        Returns:
            Additional text content found in Web Components
        """
        try:
            extracted_content = []
            
            # 1. Extract Shadow DOM content from JavaScript context
            if js_context:
                shadow_content = self._extract_shadow_dom_from_js(js_context)
                if shadow_content:
                    extracted_content.append(shadow_content)
            
            # 2. Find custom elements in HTML
            custom_elements = self._find_custom_elements(soup)
            for element in custom_elements:
                content = self._extract_custom_element_content(element, js_context)
                if content:
                    extracted_content.append(content)
            
            # 3. Extract template content
            template_content = self._extract_template_content(soup)
            if template_content:
                extracted_content.append(template_content)
            
            # 4. Extract slot content
            slot_content = self._extract_slot_content(soup)
            if slot_content:
                extracted_content.append(slot_content)
            
            # 5. Parse declarative Shadow DOM
            declarative_content = self._extract_declarative_shadow_dom(soup)
            if declarative_content:
                extracted_content.append(declarative_content)
            
            return "\n\n".join(extracted_content)
            
        except Exception as e:
            return f"<!-- Web Components extraction error: {str(e)} -->"
    
    def _extract_shadow_dom_from_js(self, js_context: Dict) -> str:
        """Extract Shadow DOM content from JavaScript execution context"""
        try:
            shadow_content = []
            
            # Look for Shadow DOM creation patterns in JavaScript
            js_logs = js_context.get('console_output', [])
            
            for log in js_logs:
                log_str = str(log)
                
                # Pattern 1: Shadow DOM attachment logging
                if 'attachShadow' in log_str or 'shadowRoot' in log_str:
                    content = self._parse_shadow_dom_log(log_str)
                    if content:
                        shadow_content.append(content)
                
                # Pattern 2: Custom element content updates
                if 'customElements.define' in log_str:
                    content = self._parse_custom_element_log(log_str)
                    if content:
                        shadow_content.append(content)
            
            # Look for Shadow DOM content in DOM modifications
            dom_mods = js_context.get('dom_modifications', {})
            for element_id, changes in dom_mods.items():
                if 'shadowRoot' in str(changes):
                    shadow_text = self._extract_shadow_text_from_changes(changes)
                    if shadow_text:
                        shadow_content.append(f"Shadow DOM ({element_id}): {shadow_text}")
            
            return "\n".join(shadow_content)
            
        except Exception as e:
            return f"<!-- Shadow DOM JS extraction error: {str(e)} -->"
    
    def _find_custom_elements(self, soup: BeautifulSoup) -> List[Tag]:
        """Find custom elements (elements with hyphens in tag names)"""
        try:
            custom_elements = []
            
            # Find elements with hyphenated tag names (custom elements)
            for element in soup.find_all():
                if element.name and '-' in element.name:
                    custom_elements.append(element)
            
            # Also look for elements with custom element attributes
            for element in soup.find_all():
                if element.get('is'):  # Customized built-in elements
                    custom_elements.append(element)
                    
                # Look for Shadow DOM host indicators
                if element.get('data-shadow-host') or element.get('shadowroot'):
                    custom_elements.append(element)
            
            return custom_elements
            
        except Exception:
            return []
    
    def _extract_custom_element_content(self, element: Tag, js_context: Dict = None) -> str:
        """Extract content from a custom element"""
        try:
            content_parts = []
            
            # 1. Get visible text content
            visible_text = element.get_text(strip=True)
            if visible_text:
                content_parts.append(f"Visible: {visible_text}")
            
            # 2. Extract data attributes (often contain content)
            data_attrs = {}
            for attr_name, attr_value in element.attrs.items():
                if attr_name.startswith('data-'):
                    data_attrs[attr_name] = attr_value
            
            if data_attrs:
                content_parts.append(f"Data: {json.dumps(data_attrs, indent=2)}")
            
            # 3. Look for content in common content attributes
            content_attrs = ['title', 'alt', 'aria-label', 'aria-describedby', 'placeholder']
            for attr in content_attrs:
                if element.get(attr):
                    content_parts.append(f"{attr.title()}: {element.get(attr)}")
            
            # 4. Extract content from JavaScript context if available
            if js_context and element.get('id'):
                js_content = self._get_element_content_from_js(element.get('id'), js_context)
                if js_content:
                    content_parts.append(f"JS Content: {js_content}")
            
            if content_parts:
                return f"Custom Element <{element.name}>:\n" + "\n".join(content_parts)
            
            return ""
            
        except Exception as e:
            return f"<!-- Custom element extraction error: {str(e)} -->"
    
    def _extract_template_content(self, soup: BeautifulSoup) -> str:
        """Extract content from HTML template elements"""
        try:
            template_content = []
            
            # Find all template elements
            templates = soup.find_all('template')
            
            for i, template in enumerate(templates):
                # Extract template content
                template_html = template.decode_contents()
                if template_html.strip():
                    # Parse template content
                    template_soup = BeautifulSoup(template_html, 'html.parser')
                    template_text = template_soup.get_text(separator=' ', strip=True)
                    
                    if template_text:
                        template_id = template.get('id', f'template-{i+1}')
                        template_content.append(f"Template ({template_id}): {template_text}")
            
            return "\n".join(template_content)
            
        except Exception as e:
            return f"<!-- Template extraction error: {str(e)} -->"
    
    def _extract_slot_content(self, soup: BeautifulSoup) -> str:
        """Extract content from slot elements and slotted content"""
        try:
            slot_content = []
            
            # Find slot elements
            slots = soup.find_all('slot')
            
            for slot in slots:
                slot_name = slot.get('name', 'default')
                slot_text = slot.get_text(strip=True)
                
                if slot_text:
                    slot_content.append(f"Slot ({slot_name}): {slot_text}")
                
                # Look for fallback content
                if not slot_text and slot.contents:
                    fallback_text = ' '.join([str(content) for content in slot.contents if str(content).strip()])
                    if fallback_text:
                        slot_content.append(f"Slot Fallback ({slot_name}): {fallback_text}")
            
            # Find elements with slot attributes (slotted content)
            slotted_elements = soup.find_all(attrs={'slot': True})
            
            for element in slotted_elements:
                slot_name = element.get('slot')
                element_text = element.get_text(strip=True)
                
                if element_text:
                    slot_content.append(f"Slotted Content ({slot_name}): {element_text}")
            
            return "\n".join(slot_content)
            
        except Exception as e:
            return f"<!-- Slot extraction error: {str(e)} -->"
    
    def _extract_declarative_shadow_dom(self, soup: BeautifulSoup) -> str:
        """Extract content from declarative Shadow DOM"""
        try:
            shadow_content = []
            
            # Find template elements with shadowrootmode attribute
            shadow_templates = soup.find_all('template', shadowrootmode=True)
            
            for template in shadow_templates:
                shadow_mode = template.get('shadowrootmode', 'open')
                shadow_html = template.decode_contents()
                
                if shadow_html.strip():
                    # Parse shadow content
                    shadow_soup = BeautifulSoup(shadow_html, 'html.parser')
                    shadow_text = shadow_soup.get_text(separator=' ', strip=True)
                    
                    if shadow_text:
                        shadow_content.append(f"Declarative Shadow DOM ({shadow_mode}): {shadow_text}")
            
            return "\n".join(shadow_content)
            
        except Exception as e:
            return f"<!-- Declarative Shadow DOM extraction error: {str(e)} -->"
    
    def _parse_shadow_dom_log(self, log_str: str) -> str:
        """Parse Shadow DOM content from JavaScript log"""
        try:
            # Look for common Shadow DOM content patterns
            patterns = [
                r'shadowRoot\.innerHTML\s*=\s*[\'"`]([^\'"`]+)[\'"`]',
                r'shadow\.textContent\s*=\s*[\'"`]([^\'"`]+)[\'"`]',
                r'attachShadow.*?innerHTML.*?[\'"`]([^\'"`]+)[\'"`]'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, log_str, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return ""
            
        except Exception:
            return ""
    
    def _parse_custom_element_log(self, log_str: str) -> str:
        """Parse custom element content from JavaScript log"""
        try:
            # Look for custom element content patterns
            patterns = [
                r'customElements\.define\([\'"`]([^\'"`]+)[\'"`].*?innerHTML.*?[\'"`]([^\'"`]+)[\'"`]',
                r'connectedCallback.*?textContent.*?[\'"`]([^\'"`]+)[\'"`]'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, log_str, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    if len(groups) >= 2:
                        return f"{groups[0]}: {groups[1]}"
                    return groups[0]
            
            return ""
            
        except Exception:
            return ""
    
    def _extract_shadow_text_from_changes(self, changes: Dict) -> str:
        """Extract text content from DOM modification changes"""
        try:
            text_content = []
            
            for change_type, change_data in changes.items():
                if isinstance(change_data, dict):
                    # Look for text content in changes
                    if 'textContent' in change_data:
                        text_content.append(str(change_data['textContent']))
                    if 'innerHTML' in change_data:
                        # Parse HTML and extract text
                        html_soup = BeautifulSoup(str(change_data['innerHTML']), 'html.parser')
                        text = html_soup.get_text(separator=' ', strip=True)
                        if text:
                            text_content.append(text)
            
            return ' '.join(text_content)
            
        except Exception:
            return ""
    
    def _get_element_content_from_js(self, element_id: str, js_context: Dict) -> str:
        """Get element content that was set via JavaScript"""
        try:
            # Look in DOM modifications for this element
            dom_mods = js_context.get('dom_modifications', {})
            
            if element_id in dom_mods:
                changes = dom_mods[element_id]
                return self._extract_shadow_text_from_changes({element_id: changes})
            
            # Look in console output for element updates
            console_output = js_context.get('console_output', [])
            
            for log in console_output:
                log_str = str(log)
                if element_id in log_str:
                    # Try to extract content from log
                    content_match = re.search(rf'{element_id}.*?[\'"`]([^\'"`]+)[\'"`]', log_str)
                    if content_match:
                        return content_match.group(1)
            
            return ""
            
        except Exception:
            return ""

    def register_component_definition(self, component_name: str, definition: Dict):
        """Register a custom component definition for content extraction"""
        self.component_registry[component_name] = definition
    
    def get_registered_components(self) -> Dict:
        """Get all registered component definitions"""
        return self.component_registry.copy()