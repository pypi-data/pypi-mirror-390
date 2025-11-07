#!/usr/bin/env python3
"""
ARIA and Accessibility Content Extractor
Extracts screen reader descriptions, semantic info, and accessibility content
"""

import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag


class ARIAAccessibilityExtractor:
    """Extracts ARIA attributes and accessibility content for better markdown context"""
    
    def __init__(self):
        self.aria_properties = [
            'aria-label', 'aria-labelledby', 'aria-describedby', 'aria-description',
            'aria-expanded', 'aria-hidden', 'aria-current', 'aria-live',
            'aria-atomic', 'aria-relevant', 'aria-busy', 'aria-controls',
            'aria-owns', 'aria-flowto', 'aria-details', 'aria-errormessage'
        ]
        
        self.semantic_roles = [
            'button', 'link', 'heading', 'banner', 'navigation', 'main',
            'complementary', 'contentinfo', 'article', 'section', 'aside',
            'search', 'form', 'dialog', 'alert', 'status', 'log', 'marquee',
            'timer', 'alertdialog', 'application', 'document', 'feed'
        ]
    
    def extract_aria_content(self, soup: BeautifulSoup, js_context: Dict) -> str:
        """Extract ARIA and accessibility content from HTML"""
        try:
            aria_content = []
            
            # Extract ARIA labels and descriptions
            for element in soup.find_all(attrs={"aria-label": True}):
                if hasattr(element, 'get') and hasattr(element, 'name'):
                    label = element.get('aria-label', '')
                    if label and hasattr(label, 'strip'):
                        label = label.strip()
                    if label and element.name:
                        tag_name = element.name.upper()
                        aria_content.append(f"🏷️ {tag_name} Label: {label}")
            
            # Extract aria-describedby references
            for element in soup.find_all(attrs={"aria-describedby": True}):
                described_by_id = element.get('aria-describedby', '').strip()
                if described_by_id:
                    # Find the describing element
                    describing_element = soup.find(id=described_by_id)
                    if describing_element:
                        description = describing_element.get_text(strip=True)
                        if description:
                            aria_content.append(f"📝 Description: {description}")
            
            # Extract semantic role information
            for element in soup.find_all(attrs={"role": True}):
                role = element.get('role', '').strip()
                if role in self.semantic_roles:
                    text_content = element.get_text(strip=True)[:100]
                    if text_content:
                        aria_content.append(f"🎭 {role.title()}: {text_content}")
            
            # Extract live region updates
            for element in soup.find_all(attrs={"aria-live": True}):
                live_type = element.get('aria-live', '').strip()
                content = element.get_text(strip=True)
                if content and live_type:
                    aria_content.append(f"📢 Live {live_type.title()}: {content}")
            
            # Extract error messages
            for element in soup.find_all(attrs={"aria-errormessage": True}):
                error_id = element.get('aria-errormessage', '').strip()
                if error_id:
                    error_element = soup.find(id=error_id)
                    if error_element:
                        error_text = error_element.get_text(strip=True)
                        if error_text:
                            aria_content.append(f"❌ Error: {error_text}")
            
            # Extract expanded/collapsed state information
            for element in soup.find_all(attrs={"aria-expanded": True}):
                expanded = element.get('aria-expanded', '').strip().lower()
                label = element.get('aria-label', element.get_text(strip=True)[:50])
                if label:
                    state = "Expanded" if expanded == "true" else "Collapsed"
                    aria_content.append(f"🔽 {state}: {label}")
            
            # Extract current page/step indicators
            for element in soup.find_all(attrs={"aria-current": True}):
                current_type = element.get('aria-current', '').strip()
                if current_type and current_type != "false":
                    text = element.get_text(strip=True)
                    if text:
                        aria_content.append(f"👉 Current {current_type}: {text}")
            
            # Extract alternative text and descriptions
            alt_texts = self._extract_alt_descriptions(soup)
            aria_content.extend(alt_texts)
            
            # Extract form accessibility info
            form_accessibility = self._extract_form_accessibility(soup)
            aria_content.extend(form_accessibility)
            
            # Combine all ARIA content
            if aria_content:
                return "\n## 🔍 Accessibility Content\n" + "\n".join(aria_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- ARIA extraction error: {str(e)} -->\n"
    
    def _extract_alt_descriptions(self, soup: BeautifulSoup) -> List[str]:
        """Extract alternative text and descriptions"""
        alt_content = []
        
        # Images with alt text
        for img in soup.find_all('img', alt=True):
            alt_text = img.get('alt', '').strip()
            if alt_text:
                src = img.get('src', 'unknown')[:50]
                alt_content.append(f"🖼️ Image ({src}): {alt_text}")
        
        # Figures with captions
        for figure in soup.find_all('figure'):
            caption = figure.find('figcaption')
            if caption:
                caption_text = caption.get_text(strip=True)
                if caption_text:
                    alt_content.append(f"📊 Figure Caption: {caption_text}")
        
        # Tables with captions and summaries
        for table in soup.find_all('table'):
            caption = table.find('caption')
            if caption:
                caption_text = caption.get_text(strip=True)
                if caption_text:
                    alt_content.append(f"📋 Table Caption: {caption_text}")
            
            summary = table.get('summary', '').strip()
            if summary:
                alt_content.append(f"📋 Table Summary: {summary}")
        
        return alt_content
    
    def _extract_form_accessibility(self, soup: BeautifulSoup) -> List[str]:
        """Extract form accessibility information"""
        form_content = []
        
        # Form field labels
        for label in soup.find_all('label'):
            label_text = label.get_text(strip=True)
            if label_text:
                for_attr = label.get('for')
                if for_attr:
                    target_element = soup.find(id=for_attr)
                    if target_element:
                        element_type = target_element.get('type', target_element.name)
                        form_content.append(f"🏷️ {element_type.title()} Label: {label_text}")
        
        # Required field indicators
        for element in soup.find_all(attrs={"required": True}):
            label = self._get_element_label(element, soup)
            if label:
                form_content.append(f"⚠️ Required Field: {label}")
        
        # Field descriptions and hints
        for element in soup.find_all(attrs={"aria-describedby": True}):
            if element.name in ['input', 'textarea', 'select']:
                described_by = element.get('aria-describedby', '').strip()
                if described_by:
                    desc_element = soup.find(id=described_by)
                    if desc_element:
                        description = desc_element.get_text(strip=True)
                        if description:
                            label = self._get_element_label(element, soup)
                            form_content.append(f"💡 Field Hint ({label}): {description}")
        
        return form_content
    
    def _get_element_label(self, element: Tag, soup: BeautifulSoup) -> str:
        """Get the label for a form element"""
        # Check for aria-label
        if element.get('aria-label'):
            return element.get('aria-label').strip()
        
        # Check for associated label
        element_id = element.get('id')
        if element_id:
            label = soup.find('label', attrs={'for': element_id})
            if label:
                return label.get_text(strip=True)
        
        # Check for parent label
        parent_label = element.find_parent('label')
        if parent_label:
            return parent_label.get_text(strip=True)
        
        # Fallback to placeholder or name
        return element.get('placeholder', element.get('name', 'Unknown Field'))
    
    def extract_screen_reader_content(self, soup: BeautifulSoup) -> str:
        """Extract content specifically for screen readers"""
        try:
            sr_content = []
            
            # Screen reader only content (sr-only classes)
            for element in soup.find_all(class_=re.compile(r'sr-only|screen-reader|visually-hidden')):
                text = element.get_text(strip=True)
                if text:
                    sr_content.append(f"👁️ Screen Reader: {text}")
            
            # Skip links
            for element in soup.find_all('a', href=re.compile(r'^#')):
                if 'skip' in element.get_text('').lower():
                    sr_content.append(f"⏭️ Skip Link: {element.get_text(strip=True)}")
            
            # Landmark regions
            landmarks = soup.find_all(attrs={"role": re.compile(r'banner|navigation|main|complementary|contentinfo')})
            for landmark in landmarks:
                role = landmark.get('role')
                label = landmark.get('aria-label', landmark.get('aria-labelledby', ''))
                if label:
                    sr_content.append(f"🗺️ {role.title()} Region: {label}")
            
            if sr_content:
                return "\n## 👁️ Screen Reader Content\n" + "\n".join(sr_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- Screen reader extraction error: {str(e)} -->\n"