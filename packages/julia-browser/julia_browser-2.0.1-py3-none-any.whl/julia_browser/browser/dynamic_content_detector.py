#!/usr/bin/env python3
"""
Dynamic Content Loading Detection
Detects and extracts lazy-loaded and infinite scroll content
"""

import re
import time
from typing import Dict, List, Tuple, Optional, Set
from bs4 import BeautifulSoup, Tag


class DynamicContentDetector:
    """Detects and attempts to load dynamic content that's not immediately visible"""
    
    def __init__(self):
        self.lazy_load_selectors = [
            '[data-lazy]', '[data-src]', '[loading="lazy"]',
            '.lazy', '.lazyload', '.lazy-load',
            '[data-original]', '[data-echo]'
        ]
        
        self.infinite_scroll_indicators = [
            '.load-more', '.show-more', '.infinite-scroll',
            '[data-infinite]', '[data-scroll]', '.pagination-next',
            '.load-next', '.more-content'
        ]
        
        self.dynamic_content_patterns = [
            r'data-.*url', r'data-.*src', r'data-.*content',
            r'data-.*load', r'data-.*fetch'
        ]
    
    def detect_dynamic_content(self, soup: BeautifulSoup, js_context: Dict) -> str:
        """Detect and extract information about dynamic content"""
        try:
            dynamic_content = []
            
            # Detect lazy-loaded images and media
            lazy_media = self._detect_lazy_media(soup)
            dynamic_content.extend(lazy_media)
            
            # Detect infinite scroll content
            infinite_scroll = self._detect_infinite_scroll(soup)
            dynamic_content.extend(infinite_scroll)
            
            # Detect AJAX content placeholders
            ajax_content = self._detect_ajax_content(soup, js_context)
            dynamic_content.extend(ajax_content)
            
            # Detect progressive enhancement content
            progressive_content = self._detect_progressive_content(soup)
            dynamic_content.extend(progressive_content)
            
            # Extract data from lazy loading attributes
            lazy_data = self._extract_lazy_loading_data(soup)
            dynamic_content.extend(lazy_data)
            
            if dynamic_content:
                return "\n## 🔄 Dynamic Content Detected\n" + "\n".join(dynamic_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- Dynamic content detection error: {str(e)} -->\n"
    
    def _detect_lazy_media(self, soup: BeautifulSoup) -> List[str]:
        """Detect lazy-loaded images, videos, and other media"""
        lazy_media = []
        
        # Images with lazy loading attributes
        for selector in self.lazy_load_selectors:
            elements = soup.select(selector)
            for element in elements:
                if element.name == 'img':
                    # Get the actual source
                    src = (element.get('data-src') or 
                           element.get('data-original') or 
                           element.get('data-lazy') or
                           element.get('src', ''))
                    
                    alt = element.get('alt', 'Image')
                    if src:
                        lazy_media.append(f"🖼️ Lazy Image: {alt} ({src[:50]}...)")
                    else:
                        lazy_media.append(f"🖼️ Lazy Image: {alt} (source pending)")
        
        # Videos with lazy loading
        for video in soup.find_all('video', attrs={'data-src': True}):
            title = video.get('title', video.get('aria-label', 'Video'))
            src = video.get('data-src', '')[:50]
            lazy_media.append(f"🎥 Lazy Video: {title} ({src}...)")
        
        # Iframes with lazy loading (embeds, widgets)
        for iframe in soup.find_all('iframe', attrs={'data-src': True}):
            title = iframe.get('title', iframe.get('aria-label', 'Embedded Content'))
            src = iframe.get('data-src', '')[:50]
            lazy_media.append(f"📱 Lazy Embed: {title} ({src}...)")
        
        return lazy_media
    
    def _detect_infinite_scroll(self, soup: BeautifulSoup) -> List[str]:
        """Detect infinite scroll and load-more functionality"""
        infinite_content = []
        
        # Load more buttons
        for selector in self.infinite_scroll_indicators:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text:
                    infinite_content.append(f"📜 Load More: {text}")
                
                # Check for data attributes indicating more content
                load_url = (element.get('data-url') or 
                           element.get('data-next') or
                           element.get('data-load'))
                if load_url:
                    infinite_content.append(f"🔗 Next Content URL: {load_url[:50]}...")
        
        # Pagination indicators
        pagination = soup.find_all(class_=re.compile(r'pagination|pager'))
        for pag in pagination:
            next_link = pag.find('a', text=re.compile(r'next|more', re.I))
            if next_link:
                href = next_link.get('href', '')
                infinite_content.append(f"➡️ Next Page: {href[:50]}...")
        
        # Scroll triggers
        scroll_triggers = soup.find_all(attrs={'data-scroll': True})
        for trigger in scroll_triggers:
            trigger_info = trigger.get('data-scroll', '')
            if trigger_info:
                infinite_content.append(f"📏 Scroll Trigger: {trigger_info}")
        
        return infinite_content
    
    def _detect_ajax_content(self, soup: BeautifulSoup, js_context: Dict) -> List[str]:
        """Detect AJAX content loading patterns"""
        ajax_content = []
        
        # Elements with AJAX loading indicators
        ajax_elements = soup.find_all(attrs={'data-ajax': True})
        for element in ajax_elements:
            ajax_url = element.get('data-ajax', '')
            element_text = element.get_text(strip=True)[:50] or 'Content Area'
            if ajax_url:
                ajax_content.append(f"⚡ AJAX Content: {element_text} → {ajax_url[:50]}...")
        
        # Loading spinners and placeholders
        loading_elements = soup.find_all(class_=re.compile(r'loading|spinner|placeholder|skeleton'))
        for element in loading_elements:
            if element.get_text(strip=True):
                ajax_content.append(f"⏳ Loading Placeholder: {element.get_text(strip=True)[:50]}...")
            else:
                ajax_content.append("⏳ Content Loading Indicator")
        
        # JavaScript context AJAX URLs
        if 'ajax_endpoints' in js_context:
            endpoints = js_context['ajax_endpoints']
            if isinstance(endpoints, (list, tuple)):
                for endpoint in endpoints[:5]:  # Limit to first 5
                    ajax_content.append(f"🔗 AJAX Endpoint: {endpoint}")
        
        # API endpoints in data attributes
        api_elements = soup.find_all(attrs={'data-api': True})
        for element in api_elements:
            api_url = element.get('data-api', '')
            if api_url:
                ajax_content.append(f"🌐 API Endpoint: {api_url[:50]}...")
        
        return ajax_content
    
    def _detect_progressive_content(self, soup: BeautifulSoup) -> List[str]:
        """Detect progressive enhancement and conditional content"""
        progressive_content = []
        
        # Noscript alternatives
        noscript_elements = soup.find_all('noscript')
        for noscript in noscript_elements:
            content = noscript.get_text(strip=True)
            if content:
                progressive_content.append(f"🚫 No-JS Alternative: {content[:100]}...")
        
        # Template elements (potential dynamic content)
        templates = soup.find_all('template')
        for template in templates:
            template_id = template.get('id', 'Unknown')
            content_preview = template.get_text(strip=True)[:50]
            if content_preview:
                progressive_content.append(f"📋 Template ({template_id}): {content_preview}...")
        
        # Elements with show/hide conditions
        conditional_elements = soup.find_all(attrs={'data-show': True})
        for element in conditional_elements:
            condition = element.get('data-show', '')
            content = element.get_text(strip=True)[:50]
            if content:
                progressive_content.append(f"👁️ Conditional Content ({condition}): {content}...")
        
        # Elements with visibility toggles
        toggle_elements = soup.find_all(class_=re.compile(r'collapse|accordion|dropdown|toggle'))
        for element in toggle_elements:
            content = element.get_text(strip=True)[:50]
            if content:
                progressive_content.append(f"🔽 Collapsible Content: {content}...")
        
        return progressive_content
    
    def _extract_lazy_loading_data(self, soup: BeautifulSoup) -> List[str]:
        """Extract data from lazy loading data attributes"""
        lazy_data = []
        
        # Find all elements with data attributes that might contain URLs or content
        for pattern in self.dynamic_content_patterns:
            elements = soup.find_all(attrs={re.compile(pattern): True})
            for element in elements[:10]:  # Limit to avoid spam
                for attr_name, attr_value in element.attrs.items():
                    if re.match(pattern, attr_name) and attr_value:
                        # Check if it looks like a URL or content
                        if (attr_value.startswith(('http', '//', '/')) or 
                            len(attr_value) > 20):
                            lazy_data.append(f"📦 Lazy Data ({attr_name}): {attr_value[:50]}...")
        
        # Extract JSON data in script tags (often used for lazy loading)
        script_tags = soup.find_all('script', type='application/json')
        for script in script_tags:
            script_id = script.get('id', 'unknown')
            content = script.get_text(strip=True)
            if content and len(content) > 50:
                lazy_data.append(f"🔧 JSON Data ({script_id}): {content[:50]}...")
        
        return lazy_data
    
    def attempt_dynamic_content_extraction(self, soup: BeautifulSoup, js_context: Dict) -> str:
        """Attempt to extract actual content from dynamic loading patterns"""
        try:
            extracted_content = []
            
            # Try to resolve data-src to actual content
            for element in soup.find_all(attrs={'data-src': True}):
                data_src = element.get('data-src', '')
                if data_src and not data_src.startswith('data:'):
                    # For CLI browser, we note the URL but can't fetch without network
                    element_type = element.name.title()
                    extracted_content.append(f"🔗 {element_type} URL: {data_src}")
            
            # Extract content from templates
            for template in soup.find_all('template'):
                template_content = template.get_text(strip=True)
                if template_content:
                    template_id = template.get('id', 'Template')
                    extracted_content.append(f"📄 {template_id}: {template_content}")
            
            # Extract hidden content that might be shown dynamically
            hidden_elements = soup.find_all(style=re.compile(r'display:\s*none'))
            for element in hidden_elements:
                content = element.get_text(strip=True)
                if content and len(content) > 10:
                    extracted_content.append(f"👁️ Hidden Content: {content[:100]}...")
            
            if extracted_content:
                return "\n## 📥 Extracted Dynamic Content\n" + "\n".join(extracted_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- Dynamic content extraction error: {str(e)} -->\n"