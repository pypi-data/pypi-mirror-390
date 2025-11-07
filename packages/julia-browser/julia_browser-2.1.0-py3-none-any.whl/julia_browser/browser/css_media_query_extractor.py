#!/usr/bin/env python3
"""
CSS Media Query Content Selection
Extracts content based on media queries and responsive design patterns
"""

import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag


class CSSMediaQueryExtractor:
    """Extracts content that's conditionally shown based on CSS media queries"""
    
    def __init__(self):
        self.media_query_patterns = [
            r'@media\s+([^{]+)\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}',
            r'@media\s+screen\s+and\s+\(([^)]+)\)',
            r'@media\s+print',
            r'@media\s+\(([^)]+)\)'
        ]
        
        self.responsive_breakpoints = {
            'xs': '(max-width: 575px)',
            'sm': '(min-width: 576px)',
            'md': '(min-width: 768px)', 
            'lg': '(min-width: 992px)',
            'xl': '(min-width: 1200px)',
            'mobile': '(max-width: 767px)',
            'tablet': '(min-width: 768px) and (max-width: 1023px)',
            'desktop': '(min-width: 1024px)',
            'print': 'print'
        }
        
        self.css_display_classes = [
            'd-none', 'd-block', 'd-inline', 'd-flex', 'd-grid',
            'hidden', 'visible', 'show', 'hide',
            'desktop-only', 'mobile-only', 'tablet-only',
            'print-only', 'screen-only'
        ]
    
    def extract_media_query_content(self, soup: BeautifulSoup, js_context: Dict) -> str:
        """Extract content that's conditionally displayed based on media queries"""
        try:
            media_content = []
            
            # Extract CSS media query rules
            css_media_queries = self._extract_css_media_queries(soup)
            media_content.extend(css_media_queries)
            
            # Extract responsive content classes
            responsive_content = self._extract_responsive_content(soup)
            media_content.extend(responsive_content)
            
            # Extract print-specific content
            print_content = self._extract_print_content(soup)
            media_content.extend(print_content)
            
            # Extract mobile/desktop specific content
            device_content = self._extract_device_specific_content(soup)
            media_content.extend(device_content)
            
            # Extract content hidden by default but shown on certain screen sizes
            conditional_content = self._extract_conditional_display_content(soup)
            media_content.extend(conditional_content)
            
            if media_content:
                return "\n## 📱 Responsive & Media-Specific Content\n" + "\n".join(media_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- Media query extraction error: {str(e)} -->\n"
    
    def _extract_css_media_queries(self, soup: BeautifulSoup) -> List[str]:
        """Extract CSS media query rules and their content"""
        media_queries = []
        
        # Find all style elements
        style_elements = soup.find_all('style')
        for style in style_elements:
            css_content = style.get_text()
            if css_content:
                # Find media queries in CSS
                for pattern in self.media_query_patterns:
                    matches = re.findall(pattern, css_content, re.DOTALL | re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple) and len(match) >= 2:
                            media_condition = match[0].strip()
                            css_rules = match[1].strip()
                            if media_condition and css_rules:
                                media_queries.append(f"📐 Media Query ({media_condition}): {css_rules[:100]}...")
                        elif isinstance(match, str):
                            media_queries.append(f"📐 Media Condition: {match}")
        
        # Find linked stylesheets with media attributes
        link_elements = soup.find_all('link', rel='stylesheet', media=True)
        for link in link_elements:
            media_attr = link.get('media', '')
            href = link.get('href', '')
            if media_attr and href:
                media_queries.append(f"🔗 Stylesheet ({media_attr}): {href}")
        
        return media_queries
    
    def _extract_responsive_content(self, soup: BeautifulSoup) -> List[str]:
        """Extract content with responsive display classes"""
        responsive_content = []
        
        # Find elements with responsive classes
        for class_pattern in self.css_display_classes:
            # Find exact matches
            exact_elements = soup.find_all(class_=class_pattern)
            for element in exact_elements:
                if hasattr(element, 'get_text'):
                    content = element.get_text(strip=True)
                    if content:
                        responsive_content.append(f"📱 {class_pattern.title()}: {content[:100]}...")
            
            # Find pattern matches (like d-md-block, d-lg-none, etc.)
            pattern_elements = soup.find_all(class_=re.compile(rf'{class_pattern}-\w+'))
            for element in pattern_elements:
                if hasattr(element, 'get') and hasattr(element, 'get_text'):
                    classes = element.get('class', [])
                    if classes:
                        responsive_classes = [cls for cls in classes if class_pattern in cls]
                        if responsive_classes:
                            content = element.get_text(strip=True)
                            if content:
                                responsive_content.append(f"📱 {responsive_classes[0]}: {content[:100]}...")
        
        # Find Bootstrap responsive utilities
        bootstrap_patterns = [
            r'd-\w+-none', r'd-\w+-block', r'd-\w+-flex', r'd-\w+-grid',
            r'visible-\w+', r'hidden-\w+',
            r'show-\w+', r'hide-\w+'
        ]
        
        for pattern in bootstrap_patterns:
            elements = soup.find_all(class_=re.compile(pattern))
            for element in elements[:5]:  # Limit to avoid spam
                if hasattr(element, 'get') and hasattr(element, 'get_text'):
                    classes = element.get('class', [])
                    content = element.get_text(strip=True)
                    if content and classes:
                        matching_classes = [cls for cls in classes if re.match(pattern, cls)]
                        if matching_classes:
                            responsive_content.append(f"📱 {matching_classes[0]}: {content[:100]}...")
        
        return responsive_content
    
    def _extract_print_content(self, soup: BeautifulSoup) -> List[str]:
        """Extract content specifically for print media"""
        print_content = []
        
        # Find elements with print-specific classes
        print_classes = ['print-only', 'd-print-block', 'visible-print', 'show-print']
        for print_class in print_classes:
            elements = soup.find_all(class_=print_class)
            for element in elements:
                if hasattr(element, 'get_text'):
                    content = element.get_text(strip=True)
                    if content:
                        print_content.append(f"🖨️ Print Only: {content[:100]}...")
        
        # Find elements that are hidden on screen but visible in print
        screen_hidden = soup.find_all(class_=re.compile(r'd-none.*d-print-block|hidden.*visible-print'))
        for element in screen_hidden:
            if hasattr(element, 'get_text'):
                content = element.get_text(strip=True)
                if content:
                    print_content.append(f"🖨️ Print Version: {content[:100]}...")
        
        # Find print-specific elements by common patterns
        print_elements = soup.find_all(attrs={'data-print': True})
        for element in print_elements:
            if hasattr(element, 'get_text'):
                content = element.get_text(strip=True)
                if content:
                    print_content.append(f"🖨️ Print Content: {content[:100]}...")
        
        # Find page break indicators
        page_breaks = soup.find_all(class_=re.compile(r'page-break|break-page'))
        for break_elem in page_breaks:
            if hasattr(break_elem, 'get_text'):
                content = break_elem.get_text(strip=True)
                if content:
                    print_content.append(f"📄 Page Break: {content}")
                else:
                    print_content.append("📄 Page Break Marker")
        
        return print_content
    
    def _extract_device_specific_content(self, soup: BeautifulSoup) -> List[str]:
        """Extract content specific to mobile, tablet, or desktop"""
        device_content = []
        
        # Mobile-specific content
        mobile_selectors = ['.mobile-only', '.d-block.d-md-none', '.visible-xs', '.show-mobile']
        for selector in mobile_selectors:
            elements = soup.select(selector)
            for element in elements:
                if hasattr(element, 'get_text'):
                    content = element.get_text(strip=True)
                    if content:
                        device_content.append(f"📱 Mobile Only: {content[:100]}...")
        
        # Desktop-specific content
        desktop_selectors = ['.desktop-only', '.d-none.d-lg-block', '.visible-lg', '.show-desktop']
        for selector in desktop_selectors:
            elements = soup.select(selector)
            for element in elements:
                if hasattr(element, 'get_text'):
                    content = element.get_text(strip=True)
                    if content:
                        device_content.append(f"🖥️ Desktop Only: {content[:100]}...")
        
        # Tablet-specific content
        tablet_selectors = ['.tablet-only', '.d-none.d-md-block.d-lg-none', '.visible-md', '.show-tablet']
        for selector in tablet_selectors:
            elements = soup.select(selector)
            for element in elements:
                if hasattr(element, 'get_text'):
                    content = element.get_text(strip=True)
                    if content:
                        device_content.append(f"📺 Tablet Only: {content[:100]}...")
        
        # Touch vs non-touch specific content
        touch_elements = soup.find_all(class_=re.compile(r'touch|no-touch'))
        for element in touch_elements:
            if hasattr(element, 'get') and hasattr(element, 'get_text'):
                classes = element.get('class', [])
                content = element.get_text(strip=True)
                if content and classes:
                    touch_classes = [cls for cls in classes if 'touch' in cls]
                    if touch_classes:
                        device_content.append(f"👆 {touch_classes[0].title()}: {content[:100]}...")
        
        return device_content
    
    def _extract_conditional_display_content(self, soup: BeautifulSoup) -> List[str]:
        """Extract content that's conditionally displayed"""
        conditional_content = []
        
        # Find elements with display conditions in data attributes
        conditional_elements = soup.find_all(attrs={'data-show-on': True})
        for element in conditional_elements:
            if hasattr(element, 'get') and hasattr(element, 'get_text'):
                condition = element.get('data-show-on', '')
                content = element.get_text(strip=True)
                if content and condition:
                    conditional_content.append(f"👁️ Show On ({condition}): {content[:100]}...")
        
        # Find elements with breakpoint-specific visibility
        breakpoint_elements = soup.find_all(attrs={'data-breakpoint': True})
        for element in breakpoint_elements:
            if hasattr(element, 'get') and hasattr(element, 'get_text'):
                breakpoint = element.get('data-breakpoint', '')
                content = element.get_text(strip=True)
                if content and breakpoint:
                    conditional_content.append(f"📐 Breakpoint ({breakpoint}): {content[:100]}...")
        
        # Find elements with viewport-specific content
        viewport_elements = soup.find_all(attrs={'data-viewport': True})
        for element in viewport_elements:
            if hasattr(element, 'get') and hasattr(element, 'get_text'):
                viewport = element.get('data-viewport', '')
                content = element.get_text(strip=True)
                if content and viewport:
                    conditional_content.append(f"🔍 Viewport ({viewport}): {content[:100]}...")
        
        # Find CSS Grid and Flexbox responsive patterns
        responsive_layout_elements = soup.find_all(class_=re.compile(r'col-\w+|flex-\w+|grid-\w+'))
        for element in responsive_layout_elements[:10]:  # Limit to avoid spam
            if hasattr(element, 'get') and hasattr(element, 'get_text'):
                classes = element.get('class', [])
                content = element.get_text(strip=True)
                if content and classes:
                    layout_classes = [cls for cls in classes if any(pattern in cls for pattern in ['col-', 'flex-', 'grid-'])]
                    if layout_classes:
                        conditional_content.append(f"🔧 Layout ({layout_classes[0]}): {content[:100]}...")
        
        return conditional_content
    
    def simulate_media_queries(self, soup: BeautifulSoup, target_width: int = 1200, target_media: str = "screen") -> str:
        """Simulate media query evaluation for a specific viewport"""
        try:
            simulated_content = []
            
            # Simulate common breakpoints
            breakpoint_status = {}
            for name, query in self.responsive_breakpoints.items():
                if 'max-width' in query:
                    max_width = int(re.search(r'max-width:\s*(\d+)', query).group(1))
                    breakpoint_status[name] = target_width <= max_width
                elif 'min-width' in query:
                    min_width = int(re.search(r'min-width:\s*(\d+)', query).group(1))
                    breakpoint_status[name] = target_width >= min_width
                elif query == 'print':
                    breakpoint_status[name] = target_media == 'print'
                else:
                    breakpoint_status[name] = True  # Default to visible
            
            # Report which breakpoints are active
            active_breakpoints = [name for name, active in breakpoint_status.items() if active]
            if active_breakpoints:
                simulated_content.append(f"📐 Active Breakpoints ({target_width}px): {', '.join(active_breakpoints)}")
            
            # Find content that would be visible at this breakpoint
            for breakpoint in active_breakpoints:
                # Look for elements with classes matching this breakpoint
                breakpoint_elements = soup.find_all(class_=re.compile(rf'd-{breakpoint}-block|show-{breakpoint}|visible-{breakpoint}'))
                for element in breakpoint_elements[:5]:  # Limit results
                    if hasattr(element, 'get_text'):
                        content = element.get_text(strip=True)
                        if content:
                            simulated_content.append(f"👁️ Visible at {breakpoint}: {content[:100]}...")
            
            if simulated_content:
                return f"\n## 🎯 Media Query Simulation ({target_width}px, {target_media})\n" + "\n".join(simulated_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- Media query simulation error: {str(e)} -->\n"