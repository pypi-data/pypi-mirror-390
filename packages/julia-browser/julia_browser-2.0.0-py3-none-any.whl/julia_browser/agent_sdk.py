"""
AI Agent SDK - Simple website interaction functions for AI agents
Clean, direct functions matching CLI browser commands
"""

from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime

try:
    from .browser.engine import BrowserEngine
except ImportError:
    from browser.engine import BrowserEngine


class AgentSDK:
    """
    Simple AI Agent SDK for Julia Browser
    Provides direct website interaction functions like CLI commands
    """
    
    def __init__(self, user_agent: str = None, timeout: int = 30):
        """
        Initialize Agent SDK
        
        Args:
            user_agent: Custom user agent string
            timeout: Default timeout for requests
        """
        self.engine = BrowserEngine(user_agent)
        self.current_url = None
        self.current_soup = None
        self.form_data = {}
        self.default_timeout = timeout
        
        # Scroll state for long pages
        self.scroll_position = 0  # Current scroll position (0 = top)
        self.scroll_chunk_size = 20  # Number of elements per scroll
        self.content_cache = []  # Cache content elements for scrolling
        
        # Scroll state for long pages
        self.scroll_position = 0  # Current scroll position (0 = top)
        self.scroll_chunk_size = 20  # Number of elements per scroll
        self.content_cache = []  # Cache content elements for scrolling
        
    def open_website(self, url: str) -> Dict[str, Any]:
        """
        Open a website
        
        Args:
            url: Website URL to open
            
        Returns:
            Dict with success status and page info
        """
        try:
            success, content, soup = self.engine.fetch_page(url, timeout=self.default_timeout)
            
            if not success:
                return {'success': False, 'error': content}
            
            self.current_url = url
            self.current_soup = soup
            self.form_data = {}
            
            # Execute JavaScript if available
            if soup:
                js_content = self.engine.extract_javascript(soup)
                if js_content:
                    js_output = self.engine.js_engine.execute_script(js_content, soup)
                    if js_output.get('dom_updates'):
                        self.engine.apply_dom_updates(soup, js_output['dom_updates'])
            
            # Get basic page info
            title = soup.title.get_text() if soup.title else "No title"
            markdown = self.engine.render_page(soup)
            
            # Extract only meaningful text content (no markdown, HTML, or technical elements)
            clean_content = self._extract_text_only_content(soup)
            
            # Initialize scroll state for new page
            self._initialize_scroll_state(soup)
            
            return {
                'success': True,
                'url': url,
                'title': title,
                'content': clean_content,
                'page_title': title
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_elements(self) -> Dict[str, Any]:
        """
        List all interactive elements on page (like CLI 'elements' command)
        
        Returns:
            Dict with numbered buttons, inputs, and links
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            from .browser.interactive_forms import InteractiveFormsHandler
            forms_handler = InteractiveFormsHandler(self.engine)
            forms_handler.extract_interactive_elements(self.current_soup, self.current_url)
            
            # Get buttons with numbers
            buttons = []
            button_num = 1
            
            for form in forms_handler.current_forms:
                for btn in form.get('buttons', []):
                    buttons.append({
                        'number': button_num,
                        'text': btn['text'],
                        'type': btn['type']
                    })
                    button_num += 1
            
            # Add standalone buttons and links
            standalone = self.current_soup.find_all(['button', 'a'])
            for elem in standalone:
                if elem.name == 'button':
                    buttons.append({
                        'number': button_num,
                        'text': elem.get_text(strip=True) or 'Button',
                        'type': 'button'
                    })
                    button_num += 1
                elif elem.name == 'a' and elem.get('href'):
                    buttons.append({
                        'number': button_num,
                        'text': elem.get_text(strip=True) or 'Link',
                        'type': 'link'
                    })
                    button_num += 1
            
            # Get input fields with numbers
            inputs = []
            input_num = 1
            
            for form in forms_handler.current_forms:
                for inp in form.get('inputs', []):
                    inputs.append({
                        'number': input_num,
                        'name': inp['name'],
                        'type': inp['type'],
                        'placeholder': inp.get('placeholder', '')
                    })
                    input_num += 1
            
            # Create clean text summary for users
            element_summary = self._create_element_summary(buttons, inputs)
            
            return {
                'success': True,
                'summary': element_summary,
                'buttons': buttons,
                'inputs': inputs,
                'total_elements': len(buttons) + len(inputs)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def click_element(self, element_number: int) -> Dict[str, Any]:
        """
        Click an element by its number (like CLI 'click' command)
        
        Args:
            element_number: Number of element to click
            
        Returns:
            Dict with click result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            elements = self.list_elements()
            if not elements['success']:
                return elements
            
            # Find the element to click
            target = None
            for btn in elements['buttons']:
                if btn['number'] == element_number:
                    target = btn
                    break
            
            if not target:
                return {'success': False, 'error': f'Element {element_number} not found'}
            
            # Handle different click types
            if target['type'] == 'link':
                # Find and follow the link
                links = self.current_soup.find_all('a', href=True)
                for link in links:
                    if link.get_text(strip=True) == target['text']:
                        href = link.get('href')
                        new_url = urljoin(self.current_url, href)
                        result = self.open_website(new_url)
                        if result['success']:
                            result['message'] = f"Followed '{target['text']}' link to {result['title']}"
                        return result
                        
            elif target['type'] == 'submit':
                # Submit form
                return self.submit_form()
                
            else:
                # Regular button click
                return {
                    'success': True, 
                    'message': f"Clicked '{target['text']}' button successfully",
                    'action': 'clicked', 
                    'element': target['text']
                }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def type_text(self, field_number: int, text: str) -> Dict[str, Any]:
        """
        Type text into an input field by number (like CLI 'type' command)
        
        Args:
            field_number: Number of input field (starting from 1)
            text: Text to type
            
        Returns:
            Dict with typing result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            elements = self.list_elements()
            if not elements['success']:
                return elements
            
            inputs = elements['inputs']
            if field_number > len(inputs) or field_number < 1:
                return {'success': False, 'error': f'Input field {field_number} not found. Found {len(inputs)} fields.'}
            
            target_input = inputs[field_number - 1]
            field_name = target_input['name'] or f'field_{field_number}'
            
            # Store typed data for form submission
            self.form_data[field_name] = text
            
            return {
                'success': True,
                'message': f"Typed '{text}' into {field_name} field",
                'action': 'typed',
                'field': field_name,
                'text': text,
                'field_number': field_number
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def submit_form(self) -> Dict[str, Any]:
        """
        Submit the current form (like CLI form submission)
        
        Returns:
            Dict with submission result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            form = self.current_soup.find('form')
            if not form:
                return {'success': False, 'error': 'No form found on page'}
            
            action = form.get('action', '')
            method = form.get('method', 'GET').upper()
            
            # Resolve form action URL
            if not action:
                submit_url = self.current_url
            elif action.startswith('//'):
                parsed = urlparse(self.current_url)
                submit_url = f"{parsed.scheme}:{action}"
            elif action.startswith('/'):
                parsed = urlparse(self.current_url)
                submit_url = f"{parsed.scheme}://{parsed.netloc}{action}"
            elif action.startswith('http'):
                submit_url = action
            else:
                submit_url = urljoin(self.current_url, action)
            
            # Collect form data
            form_data = dict(self.form_data)
            
            # Add default form values
            for input_elem in form.find_all(['input', 'textarea', 'select']):
                name = input_elem.get('name')
                if name and name not in form_data:
                    value = input_elem.get('value', '')
                    if input_elem.name == 'textarea':
                        value = input_elem.get_text()
                    form_data[name] = value
            
            # Submit form
            if method == 'POST':
                response = self.engine.session.post(submit_url, data=form_data, timeout=self.default_timeout)
            else:
                response = self.engine.session.get(submit_url, params=form_data, timeout=self.default_timeout)
            
            if response.status_code == 200:
                # Update current page
                soup = BeautifulSoup(response.text, 'html.parser')
                self.current_soup = soup
                self.current_url = response.url
                
                # Clear form data
                self.form_data = {}
                
                # Render new page
                markdown = self.engine.render_page(soup)
                title = soup.title.get_text() if soup.title else "No title"
                
                return {
                    'success': True,
                    'action': 'form_submitted',
                    'url': response.url,
                    'title': title,
                    'content': markdown,
                    'page_title': title,
                    'markdown': markdown
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.reason}'
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def follow_link(self, link_number: int) -> Dict[str, Any]:
        """
        Follow a link by number (like CLI link following)
        
        Args:
            link_number: Number of link to follow
            
        Returns:
            Dict with navigation result
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            # Get all links
            links = self.current_soup.find_all('a', href=True)
            if link_number > len(links) or link_number < 1:
                return {'success': False, 'error': f'Link {link_number} not found. Found {len(links)} links.'}
            
            target_link = links[link_number - 1]
            href = target_link.get('href')
            new_url = urljoin(self.current_url, href)
            
            return self.open_website(new_url)
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def search_page(self, search_term: str) -> Dict[str, Any]:
        """
        Search for text on current page with context
        
        Args:
            search_term: Text to search for
            
        Returns:
            Dict with search results and context
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            # Search in all text elements
            matches = []
            search_term_lower = search_term.lower()
            
            # Find all text elements and search within them
            for element in self.current_soup.find_all(text=True):
                text = element.strip()
                if text and search_term_lower in text.lower():
                    # Get context around the match
                    start_idx = text.lower().find(search_term_lower)
                    context_start = max(0, start_idx - 50)
                    context_end = min(len(text), start_idx + len(search_term) + 50)
                    context = text[context_start:context_end].strip()
                    
                    matches.append({
                        'text': text,
                        'context': context,
                        'parent_tag': element.parent.name if element.parent else None
                    })
            
            return {
                'success': True,
                'search_term': search_term,
                'matches': matches[:10],  # Limit to first 10 matches
                'total_matches': len(matches),
                'found': len(matches) > 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_page_info(self) -> Dict[str, Any]:
        """
        Get current page information
        
        Returns:
            Dict with page title, URL, content, and element counts
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        try:
            title = self.current_soup.title.get_text() if self.current_soup.title else "No title"
            markdown = self.engine.render_page(self.current_soup)
            
            # Count elements
            forms = len(self.current_soup.find_all('form'))
            buttons = len(self.current_soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]']))
            inputs = len(self.current_soup.find_all('input'))
            links = len(self.current_soup.find_all('a', href=True))
            
            # Get meta description
            meta_desc = ""
            meta_tag = self.current_soup.find('meta', attrs={'name': 'description'})
            if meta_tag:
                meta_desc = meta_tag.get('content', '')
            
            # Count words
            word_count = len(self.current_soup.get_text().split())
            
            # Check for JavaScript
            has_javascript = bool(self.current_soup.find_all('script'))
            
            return {
                'success': True,
                'title': title,
                'url': self.current_url,
                'content': markdown,
                'page_title': title,
                'markdown': markdown,
                'meta_description': meta_desc,
                'word_count': word_count,
                'element_counts': {
                    'forms': forms,
                    'buttons': buttons,
                    'inputs': inputs,
                    'links': links
                },
                'has_javascript': has_javascript,
                'has_forms': forms > 0,
                'is_interactive': buttons > 0 or inputs > 0 or forms > 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def follow_link(self, link_url: str) -> Dict[str, Any]:
        """
        Follow a link by URL (alternative to follow_link_number)
        
        Args:
            link_url: URL to navigate to
            
        Returns:
            Dict with navigation result
        """
        return self.open_website(link_url)
    
    # Legacy aliases for backward compatibility
    navigate = open_website
    get_elements = list_elements
    click_button = click_element
    fill_input = type_text
    submit_current_form = submit_form
    
    def _clean_content_for_display(self, markdown: str) -> str:
        """Clean markdown content to show proper page content like CLI browser"""
        lines = markdown.split('\n')
        clean_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Keep empty lines for formatting
            if not line_stripped:
                clean_lines.append('')
                continue
                
            # Skip JavaScript/technical patterns
            skip_patterns = [
                'window[', 'function(', 'console.log', 'var ', 'let ', 'const ',
                '():', '();', 'sl_tr_', '$.', 'jQuery', 'addEventListener',
                'createElement', 'getElementById', 'getElementsBy', 'tesla_cta',
                '"slides":', '"media":', '"componentList":', '"props":',
                '"desktopConfigOverwrite":', '"mobileConfigOverwrite":',
                '"tabletConfigOverwrite":', '"landscapeConfigOverwrite":',
                '"type":', '"name":', '"value":', '"gridRows":', '"gridCols":',
                'marginBlock', 'paddingBlock', 'marginInline', 'paddingInline',
                '"media_type":', '"roundedCorners":', '"alt_text":', '"source_type":',
                'while(paras[', '.template-landing-page', '.tds-footer'
            ]
            
            if any(skip in line_stripped for skip in skip_patterns):
                continue
                
            # Skip obvious JSON data lines
            if (line_stripped.startswith('"') and '":' in line_stripped) or \
               (line_stripped.count('"') > 2 and ':' in line_stripped):
                continue
                
            # Skip pure data lines with numbers and special chars
            if line_stripped.replace('"', '').replace(',', '').replace(':', '').replace(' ', '').isdigit():
                continue
                
            # Skip CSS-like syntax
            if line_stripped.endswith('{') and '.' in line_stripped:
                continue
                
            # Keep meaningful content: headers, text, links, etc.
            clean_lines.append(line)
        
        # Remove excessive empty lines
        result_lines = []
        empty_count = 0
        for line in clean_lines:
            if line.strip() == '':
                empty_count += 1
                if empty_count <= 2:  # Max 2 consecutive empty lines
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
    def _create_element_summary(self, buttons: List[dict], inputs: List[dict]) -> str:
        """Create a clean text summary of page elements"""
        summary_parts = []
        
        if buttons:
            summary_parts.append(f"Found {len(buttons)} clickable elements:")
            for btn in buttons:  # Show all buttons
                summary_parts.append(f"  {btn['number']}. {btn['text']} ({btn['type']})")
        
        if inputs:
            summary_parts.append(f"Found {len(inputs)} input fields:")
            for inp in inputs:  # Show all inputs
                placeholder = f" - {inp['placeholder']}" if inp['placeholder'] else ""
                summary_parts.append(f"  {inp['number']}. {inp['name']} ({inp['type']}){placeholder}")
        
        if not buttons and not inputs:
            summary_parts.append("No interactive elements found on this page.")
        
        return '\n'.join(summary_parts)
    
    def _extract_text_only_content(self, soup: BeautifulSoup) -> str:
        """Extract meaningful text content and convert to clean markdown format"""
        if not soup:
            return ""
            
        # Remove script, style, and other technical elements
        for element in soup(['script', 'style', 'meta', 'link', 'noscript', 'head']):
            element.decompose()
        
        # Use the existing renderer to get clean markdown, then extract text
        try:
            markdown_content = self.engine.render_page(soup)
            
            # Parse the markdown to extract clean text with proper formatting
            lines = markdown_content.split('\n')
            clean_lines = []
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines, but preserve one empty line for spacing
                if not line:
                    if clean_lines and clean_lines[-1] != "":
                        clean_lines.append("")
                    continue
                
                # Skip technical elements and keep meaningful content
                if self._is_meaningful_content(line):
                    clean_lines.append(line)
            
            # Remove excessive empty lines at the end
            while clean_lines and clean_lines[-1] == "":
                clean_lines.pop()
            
            return '\n'.join(clean_lines)
            
        except Exception as e:
            # Fallback to simple text extraction
            return soup.get_text(separator='\n', strip=True)
    
    def _is_meaningful_content(self, line: str) -> bool:
        """Determine if a line contains meaningful content worth showing"""
        # Skip very short lines (likely noise)
        if len(line.strip()) < 3:
            return False
            
        # Skip lines that look like technical content
        technical_patterns = [
            'javascript:', 'function(', 'var ', 'const ', 'let ',
            'href=', 'src=', 'class=', 'id=', 'style=',
            '<!DOCTYPE', '<html', '<head', '<script', '<style',
            '{', '}', '();', 'return ', 'window.', 'document.',
            'console.', 'addEventListener', 'setTimeout'
        ]
        
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in technical_patterns):
            return False
        
        # Skip lines that are mostly symbols or numbers
        alpha_chars = sum(c.isalpha() for c in line)
        if alpha_chars < len(line) * 0.3:  # Less than 30% letters
            return False
        
        # Keep meaningful content
        return True
    
    def _initialize_scroll_state(self, soup: BeautifulSoup):
        """Initialize scroll state when opening a new page"""
        if not soup:
            self.content_cache = []
            self.scroll_position = 0
            return
            
        # Extract all meaningful content elements for scrolling
        content_elements = []
        
        # Get all major content elements
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section', 'article', 'ul', 'ol', 'li', 'table', 'blockquote', 'pre']):
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Only meaningful content
                element_type = element.name
                content_elements.append({
                    'type': element_type,
                    'text': text[:200] + '...' if len(text) > 200 else text,
                    'full_text': text,
                    'element': element
                })
        
        self.content_cache = content_elements
        self.scroll_position = 0
    
    def scroll_down(self, chunks: int = 1) -> Dict[str, Any]:
        """
        Scroll down the page to see more content (like scrolling in a browser)
        
        Args:
            chunks: Number of content chunks to scroll (default 1)
            
        Returns:
            Dict with scrolled content
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        if not self.content_cache:
            return {'success': False, 'error': 'No content available to scroll through.'}
        
        try:
            # Calculate new scroll position
            new_position = min(self.scroll_position + (chunks * self.scroll_chunk_size), 
                             len(self.content_cache))
            
            if new_position == self.scroll_position:
                return {
                    'success': True,
                    'message': 'Already at bottom of page',
                    'scroll_position': self.scroll_position,
                    'total_elements': len(self.content_cache),
                    'content': 'End of page reached'
                }
            
            # Get content for the current scroll window
            start_idx = self.scroll_position
            end_idx = new_position
            visible_content = self.content_cache[start_idx:end_idx]
            
            # Update scroll position
            self.scroll_position = new_position
            
            # Format content for display
            content_lines = []
            for i, item in enumerate(visible_content, start=start_idx + 1):
                if item['type'] in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(item['type'][1])
                    prefix = '#' * level
                    content_lines.append(f"{prefix} {item['text']}")
                else:
                    content_lines.append(item['text'])
                content_lines.append('')  # Add spacing
            
            scrolled_content = '\n'.join(content_lines)
            
            return {
                'success': True,
                'message': f'Scrolled down {chunks} chunk(s)',
                'scroll_position': self.scroll_position,
                'total_elements': len(self.content_cache),
                'visible_range': f'{start_idx + 1}-{end_idx}',
                'content': scrolled_content,
                'can_scroll_down': self.scroll_position < len(self.content_cache),
                'can_scroll_up': self.scroll_position > 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scroll_up(self, chunks: int = 1) -> Dict[str, Any]:
        """
        Scroll up the page to see previous content (like scrolling in a browser)
        
        Args:
            chunks: Number of content chunks to scroll up (default 1)
            
        Returns:
            Dict with scrolled content
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        if not self.content_cache:
            return {'success': False, 'error': 'No content available to scroll through.'}
        
        try:
            # Calculate new scroll position
            scroll_amount = chunks * self.scroll_chunk_size
            new_position = max(self.scroll_position - scroll_amount, 0)
            
            if new_position == self.scroll_position:
                return {
                    'success': True,
                    'message': 'Already at top of page',
                    'scroll_position': self.scroll_position,
                    'total_elements': len(self.content_cache),
                    'content': 'Top of page reached'
                }
            
            # Get content for the current scroll window  
            start_idx = new_position
            end_idx = min(start_idx + self.scroll_chunk_size, len(self.content_cache))
            visible_content = self.content_cache[start_idx:end_idx]
            
            # Update scroll position
            self.scroll_position = new_position
            
            # Format content for display
            content_lines = []
            for i, item in enumerate(visible_content, start=start_idx + 1):
                if item['type'] in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(item['type'][1])
                    prefix = '#' * level
                    content_lines.append(f"{prefix} {item['text']}")
                else:
                    content_lines.append(item['text'])
                content_lines.append('')  # Add spacing
            
            scrolled_content = '\n'.join(content_lines)
            
            return {
                'success': True,
                'message': f'Scrolled up {chunks} chunk(s)',
                'scroll_position': self.scroll_position,
                'total_elements': len(self.content_cache),
                'visible_range': f'{start_idx + 1}-{end_idx}',
                'content': scrolled_content,
                'can_scroll_down': self.scroll_position < len(self.content_cache),
                'can_scroll_up': self.scroll_position > 0
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scroll_to_top(self) -> Dict[str, Any]:
        """
        Scroll to the top of the page
        
        Returns:
            Dict with top content
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        self.scroll_position = 0
        return self.scroll_down(1)  # Show first chunk
    
    def scroll_to_bottom(self) -> Dict[str, Any]:
        """
        Scroll to the bottom of the page
        
        Returns:
            Dict with bottom content
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        if not self.content_cache:
            return {'success': False, 'error': 'No content available to scroll through.'}
        
        # Set position to show last chunk
        self.scroll_position = max(0, len(self.content_cache) - self.scroll_chunk_size)
        
        # Get the last chunk of content
        visible_content = self.content_cache[self.scroll_position:]
        
        # Format content for display
        content_lines = []
        for i, item in enumerate(visible_content, start=self.scroll_position + 1):
            if item['type'] in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                level = int(item['type'][1])
                prefix = '#' * level
                content_lines.append(f"{prefix} {item['text']}")
            else:
                content_lines.append(item['text'])
            content_lines.append('')  # Add spacing
        
        scrolled_content = '\n'.join(content_lines)
        
        return {
            'success': True,
            'message': 'Scrolled to bottom of page',
            'scroll_position': self.scroll_position,
            'total_elements': len(self.content_cache),
            'visible_range': f'{self.scroll_position + 1}-{len(self.content_cache)}',
            'content': scrolled_content,
            'can_scroll_down': False,
            'can_scroll_up': self.scroll_position > 0
        }
    
    def get_scroll_info(self) -> Dict[str, Any]:
        """
        Get current scroll position and navigation info
        
        Returns:
            Dict with scroll state information
        """
        if not self.current_soup:
            return {'success': False, 'error': 'No website open. Use open_website() first.'}
        
        return {
            'success': True,
            'scroll_position': self.scroll_position,
            'total_elements': len(self.content_cache),
            'chunk_size': self.scroll_chunk_size,
            'can_scroll_down': self.scroll_position < len(self.content_cache),
            'can_scroll_up': self.scroll_position > 0,
            'progress_percentage': round((self.scroll_position / max(len(self.content_cache), 1)) * 100, 1),
            'current_page': self.current_url
        }
    
    # ===== PROXY CONTROL METHODS (Burp Suite-style) =====
    
    def proxy_start(self) -> Dict[str, Any]:
        """
        Start the intercepting proxy
        
        Returns:
            Dict with success status
        """
        try:
            self.engine.proxy.start()
            return {
                'success': True,
                'message': 'Proxy started - all traffic will be intercepted',
                'status': self.engine.proxy.get_status()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_stop(self) -> Dict[str, Any]:
        """
        Stop the intercepting proxy
        
        Returns:
            Dict with success status
        """
        try:
            self.engine.proxy.stop()
            return {
                'success': True,
                'message': 'Proxy stopped - traffic will pass through normally',
                'status': self.engine.proxy.get_status()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_status(self) -> Dict[str, Any]:
        """
        Get proxy status and statistics
        
        Returns:
            Dict with proxy status, statistics, and interceptor info
        """
        try:
            return {
                'success': True,
                'proxy_status': self.engine.proxy.get_status()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_get_traffic(self, limit: int = 50) -> Dict[str, Any]:
        """
        Get recent HTTP traffic logs
        
        Args:
            limit: Maximum number of traffic entries to return
            
        Returns:
            Dict with traffic log entries
        """
        try:
            traffic = self.engine.proxy.get_traffic_log(limit=limit)
            return {
                'success': True,
                'traffic_count': len(traffic),
                'traffic': traffic
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_clear_traffic(self) -> Dict[str, Any]:
        """
        Clear all traffic logs
        
        Returns:
            Dict with success status
        """
        try:
            self.engine.proxy.clear_traffic_log()
            return {
                'success': True,
                'message': 'All traffic logs cleared'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_add_request_interceptor(self, interceptor_func: callable, name: str = "CustomRequestInterceptor") -> Dict[str, Any]:
        """
        Add custom request interceptor
        
        Args:
            interceptor_func: Function that takes HTTPRequest and returns modified HTTPRequest
            name: Name for the interceptor
            
        Returns:
            Dict with success status
            
        Example:
            def modify_headers(request):
                request.headers['X-Custom-Header'] = 'AI Agent'
                return request
            
            sdk.proxy_add_request_interceptor(modify_headers, "HeaderInjector")
        """
        try:
            from julia_browser.proxy import RequestInterceptor
            
            class CustomInterceptor(RequestInterceptor):
                def __init__(self, func, interceptor_name):
                    super().__init__(interceptor_name)
                    self.func = func
                
                def intercept(self, request):
                    return self.func(request)
            
            interceptor = CustomInterceptor(interceptor_func, name)
            self.engine.proxy.registry.add_request_interceptor(interceptor)
            
            return {
                'success': True,
                'message': f'Request interceptor "{name}" added successfully',
                'interceptors': self.engine.proxy.registry.get_interceptor_info()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_add_response_interceptor(self, interceptor_func: callable, name: str = "CustomResponseInterceptor") -> Dict[str, Any]:
        """
        Add custom response interceptor
        
        Args:
            interceptor_func: Function that takes (HTTPRequest, HTTPResponse) and returns modified HTTPResponse
            name: Name for the interceptor
            
        Returns:
            Dict with success status
            
        Example:
            def modify_response(request, response):
                response.body = response.body.replace('old', 'new')
                return response
            
            sdk.proxy_add_response_interceptor(modify_response, "ContentModifier")
        """
        try:
            from julia_browser.proxy import ResponseInterceptor
            
            class CustomInterceptor(ResponseInterceptor):
                def __init__(self, func, interceptor_name):
                    super().__init__(interceptor_name)
                    self.func = func
                
                def intercept(self, request, response):
                    return self.func(request, response)
            
            interceptor = CustomInterceptor(interceptor_func, name)
            self.engine.proxy.registry.add_response_interceptor(interceptor)
            
            return {
                'success': True,
                'message': f'Response interceptor "{name}" added successfully',
                'interceptors': self.engine.proxy.registry.get_interceptor_info()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_remove_interceptor(self, name: str) -> Dict[str, Any]:
        """
        Remove an interceptor by name
        
        Args:
            name: Name of the interceptor to remove
            
        Returns:
            Dict with success status
        """
        try:
            removed_req = self.engine.proxy.registry.remove_request_interceptor(name)
            removed_resp = self.engine.proxy.registry.remove_response_interceptor(name)
            
            if removed_req or removed_resp:
                return {
                    'success': True,
                    'message': f'Interceptor "{name}" removed successfully',
                    'interceptors': self.engine.proxy.registry.get_interceptor_info()
                }
            else:
                return {
                    'success': False,
                    'error': f'Interceptor "{name}" not found'
                }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def proxy_list_interceptors(self) -> Dict[str, Any]:
        """
        List all registered interceptors
        
        Returns:
            Dict with interceptor information
        """
        try:
            return {
                'success': True,
                'interceptors': self.engine.proxy.registry.get_interceptor_info()
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}