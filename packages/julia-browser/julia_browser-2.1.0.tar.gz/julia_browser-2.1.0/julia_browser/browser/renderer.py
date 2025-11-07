"""
HTML Renderer - Converts HTML/CSS to markdown format for terminal display
"""

from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString
import markdownify
import re
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from .content_filter import DynamicContentFilter
from .web_components_extractor import WebComponentsExtractor
from .css_generated_content import CSSGeneratedContentExtractor
from .css_layout_calculator import CSSLayoutCalculator
from .aria_accessibility_extractor import ARIAAccessibilityExtractor
from .form_validation_extractor import FormValidationExtractor
from .dynamic_content_detector import DynamicContentDetector
from .mathml_svg_extractor import MathMLSVGExtractor
from .css_media_query_extractor import CSSMediaQueryExtractor


class HTMLRenderer:
    """Renders HTML content to markdown format with CSS styling support"""
    
    def __init__(self):
        self.console = Console()
        self.content_filter = DynamicContentFilter()
        self.web_components_extractor = WebComponentsExtractor()
        self.css_generated_extractor = CSSGeneratedContentExtractor()
        self.layout_calculator = CSSLayoutCalculator()
        self.aria_extractor = ARIAAccessibilityExtractor()
        self.form_validation_extractor = FormValidationExtractor()
        self.dynamic_detector = DynamicContentDetector()
        self.mathml_svg_extractor = MathMLSVGExtractor()
        self.media_query_extractor = CSSMediaQueryExtractor()
        
        # HTML to markdown conversion options - strip all technical elements
        self.md_options = {
            'heading_style': markdownify.ATX,
            'bullets': '-',
            'strip': ['script', 'style', 'meta', 'link', 'head', 'noscript']
        }
        
    def render_to_markdown(self, soup: BeautifulSoup, css_rules: Dict = None, js_context: Dict = None, clean_mode: bool = True) -> str:
        """
        Convert HTML to markdown format with CSS-based styling and intelligent content filtering
        
        Args:
            soup: BeautifulSoup parsed HTML
            css_rules: Parsed CSS rules for styling
            js_context: JavaScript context for enhanced extraction
            clean_mode: If True, show only core content. If False, show all technical details
            
        Returns:
            Clean markdown formatted string with meaningful content only
        """
        try:
            # Clean up the HTML first
            cleaned_soup = self._clean_html(soup)
            
            if clean_mode:
                # Clean mode: Only show core page content without technical details
                return self._render_clean_content(cleaned_soup, css_rules)
            
            # Full mode: Extract all technical details (legacy behavior)
            # Extract Web Components content BEFORE regular processing
            web_components_content = self.web_components_extractor.extract_web_components_content(cleaned_soup, js_context)
            
            # Extract CSS generated content (::before, ::after)
            css_generated_content = self.css_generated_extractor.extract_generated_content(cleaned_soup, css_rules)
            
            # Calculate proper layout order for Grid/Flexbox
            layout_orders = self.layout_calculator.calculate_layout_order(cleaned_soup, css_rules)
            
            # Extract new content types (initialize with empty strings to avoid None issues)
            aria_content = self.aria_extractor.extract_aria_content(cleaned_soup, js_context or {}) or ""
            form_validation_content = self.form_validation_extractor.extract_validation_content(cleaned_soup, js_context or {}) or ""
            dynamic_content = self.dynamic_detector.detect_dynamic_content(cleaned_soup, js_context or {}) or ""
            mathml_svg_content = self.mathml_svg_extractor.extract_mathml_svg_content(cleaned_soup, js_context or {}) or ""
            media_query_content = self.media_query_extractor.extract_media_query_content(cleaned_soup, js_context or {}) or ""
            
            # Apply layout reordering for correct text flow
            if layout_orders:
                cleaned_soup = self.layout_calculator.apply_layout_order_to_content(cleaned_soup, layout_orders)
            
            # Apply CSS styling to HTML elements
            if css_rules:
                self._apply_css_styling(cleaned_soup, css_rules)
                
            # Convert to markdown
            html_string = str(cleaned_soup)
            markdown_content = markdownify.markdownify(
                html_string,
                **self.md_options
            )
            
            # Post-process markdown for better terminal display
            processed_markdown = self._post_process_markdown(markdown_content)
            
            # Add extracted content to markdown
            content_parts = [processed_markdown]
            
            if web_components_content.strip():
                content_parts.append(web_components_content)
            
            if css_generated_content.strip():
                content_parts.append(css_generated_content)
                
            if aria_content.strip():
                content_parts.append(aria_content)
                
            if form_validation_content.strip():
                content_parts.append(form_validation_content)
                
            if dynamic_content.strip():
                content_parts.append(dynamic_content)
                
            if mathml_svg_content.strip():
                content_parts.append(mathml_svg_content)
                
            if media_query_content.strip():
                content_parts.append(media_query_content)
            
            # Combine all content
            combined_content = "\n".join(content_parts)
            
            # Apply intelligent content filtering like the SDK
            clean_content = self._extract_meaningful_content(combined_content)
            
            return clean_content
            
        except Exception as e:
            # Fallback to basic text extraction
            return f"Error converting to markdown: {str(e)}\n\n{soup.get_text()}"
    
    def _render_clean_content(self, soup: BeautifulSoup, css_rules: Dict = None) -> str:
        """Render only core page content without technical details"""
        try:
            # Remove all script and style elements completely
            for script in soup.find_all('script'):
                script.decompose()
            for style in soup.find_all('style'):
                style.decompose()
            for noscript in soup.find_all('noscript'):
                noscript.decompose()
            
            # Apply basic CSS styling if provided
            if css_rules:
                self._apply_css_styling(soup, css_rules)
            
            # Enhance form elements for better display (simplified)
            self._enhance_form_elements_clean(soup)
            
            # Convert to markdown using markdownify
            markdown = markdownify.markdownify(
                str(soup), 
                **self.md_options
            )
            
            # Apply comprehensive content filtering
            clean_markdown = self._comprehensive_content_filter(markdown)
            
            return clean_markdown.strip()
            
        except Exception as e:
            # Fallback to text extraction
            return soup.get_text(separator='\n').strip()
    
    def _enhance_form_elements_clean(self, soup: BeautifulSoup):
        """Enhance form elements with clean, simple display"""
        try:
            # Simple input rendering
            for input_tag in soup.find_all('input'):
                input_type = input_tag.get('type', 'text').lower()
                value = input_tag.get('value', '')
                placeholder = input_tag.get('placeholder', '')
                
                if input_type == 'submit':
                    button_text = value or 'Submit'
                    input_tag.replace_with(f"[{button_text}]")
                elif input_type == 'search':
                    search_text = placeholder or 'Search'
                    if value:
                        input_tag.replace_with(f"[{value}] ({search_text})")
                    else:
                        input_tag.replace_with(f"[________] ({search_text})")
                elif input_type in ['text', 'email']:
                    field_name = placeholder or input_tag.get('name', 'Input')
                    if value:
                        input_tag.replace_with(f"[{value}]")
                    else:
                        input_tag.replace_with(f"[{field_name}]")
                elif input_type == 'hidden':
                    input_tag.decompose()
                    
            # Simple button rendering
            for button_tag in soup.find_all('button'):
                button_text = button_tag.get_text(strip=True) or 'Button'
                button_tag.replace_with(f"[{button_text}]")
                
            # Simple textarea rendering  
            for textarea_tag in soup.find_all('textarea'):
                placeholder = textarea_tag.get('placeholder', 'Text Area')
                textarea_tag.replace_with(f"[{placeholder}]")
                
        except Exception:
            pass
    
    def _comprehensive_content_filter(self, markdown: str) -> str:
        """Apply comprehensive content filtering to show only HTML/CSS content as clean markdown"""
        try:
            # Split into lines and filter out ALL technical content
            lines = markdown.split('\n')
            clean_lines = []
            
            # Track if we're in a JavaScript block
            in_js_block = False
            
            for line in lines:
                line_stripped = line.strip()
                
                # Skip JavaScript-related content entirely
                if (line_stripped.startswith('var ') or line_stripped.startswith('function') or
                    line_stripped.startswith('const ') or line_stripped.startswith('let ') or
                    '= function' in line or 'function(' in line or
                    line_stripped.endswith(';') and ('=' in line or 'var' in line) or
                    'setTimeout' in line or 'addEventListener' in line or
                    'translationsHash' in line or 'portalSearchDomain' in line or
                    'rtlLangs' in line or 'translationsPortalKey' in line or
                    'wmL10nVisible' in line or 'document.body.className' in line or
                    'document.documentElement' in line or 'className' in line or
                    '.replace(' in line or '.addClass' in line or '.removeClass' in line or
                    'window.' in line or 'console.' in line or
                    line_stripped.startswith('/*') or line_stripped.startswith('*') or
                    line_stripped.startswith('//') or line_stripped.endswith('*/') or
                    line_stripped.startswith('/**') or
                    'jQuery' in line or '$(' in line or 'getElementById' in line):
                    continue
                
                # Skip CSS-related lines
                if ('{' in line or '}' in line or 
                    ':' in line and ';' in line and not line.startswith('#') or
                    line.strip().startswith('@') or
                    'Custom Element' in line or
                    line.startswith('🏷️') or line.startswith('🎭') or 
                    line.startswith('📏') or line.startswith('📐') or
                    line.startswith('🔽') or line.startswith('*data-') or
                    line.startswith('Visible:') or
                    'Media Condition:' in line):
                    continue
                
                # Skip obvious technical patterns
                if (line_stripped.startswith('[') and line_stripped.endswith(']') and 
                    (',' in line or "'" in line)):
                    continue
                    
                # Skip empty lines between filtered content
                if not line.strip() and (not clean_lines or not clean_lines[-1].strip()):
                    continue
                    
                clean_lines.append(line)
            
            # Join and remove technical sections
            clean_content = '\n'.join(clean_lines)
            
            # Remove entire technical sections with headers
            section_patterns = [
                r'## 🔍 Accessibility Content[\s\S]*?(?=##|\Z)',
                r'## ✅ Form Validation Requirements[\s\S]*?(?=##|\Z)', 
                r'## 📱 Responsive & Media-Specific Content[\s\S]*?(?=##|\Z)',
                r'/\*\*[\s\S]*?\*/',  # Remove multi-line comments
                r'/\*[\s\S]*?\*/',   # Remove single-line comments  
            ]
            
            for pattern in section_patterns:
                clean_content = re.sub(pattern, '', clean_content, flags=re.MULTILINE)
            
            # Clean up excessive whitespace
            clean_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean_content)
            clean_content = re.sub(r'^\s*\n+', '', clean_content)
            
            return clean_content.strip()
            
        except Exception:
            return markdown
            
    def _clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Clean HTML and enhance form elements for better terminal display"""
        # Create a copy to avoid modifying original
        cleaned = BeautifulSoup(str(soup), 'html.parser')
        
        # Enhance interactive elements before cleaning
        self._enhance_form_elements(cleaned)
        
        # Remove comments
        comments = cleaned.find_all(string=lambda text: hasattr(text, 'parent') and text.parent.name == '[document]')
        for comment in comments:
            if hasattr(comment, 'extract'):
                comment.extract()
                
        # Clean up empty elements but preserve form elements
        for tag in cleaned.find_all():
            if tag.name and not tag.get_text(strip=True) and tag.name not in ['br', 'hr', 'img', 'input', 'button', 'textarea', 'select', 'form']:
                if not tag.find_all(['img', 'br', 'hr', 'input', 'button', 'textarea', 'select']):
                    tag.decompose()
                    
        return cleaned
        
    def _apply_css_styling(self, soup: BeautifulSoup, css_rules: Dict):
        """Apply basic CSS styling by modifying HTML elements"""
        try:
            if css_rules:
                for selector, rules in css_rules.items():
                    elements = self._select_elements(soup, selector)
                    
                    for element in elements:
                        self._apply_element_styling(element, rules)
                        
        except Exception as e:
            print(f"Error applying CSS styling: {str(e)}")
            
    def _select_elements(self, soup: BeautifulSoup, selector: str) -> List[Tag]:
        """Select elements based on CSS selector (simplified implementation)"""
        try:
            # Handle basic selectors
            if selector.startswith('#'):
                # ID selector
                element_id = selector[1:]
                element = soup.find(id=element_id)
                return [element] if element else []
                
            elif selector.startswith('.'):
                # Class selector
                class_name = selector[1:]
                return soup.find_all(class_=class_name)
                
            else:
                # Tag selector
                return soup.find_all(selector)
                
        except Exception:
            return []
            
    def _apply_element_styling(self, element: Tag, rules: Dict):
        """Apply CSS rules to an HTML element"""
        try:
            # Handle text styling
            if 'font-weight' in rules and rules['font-weight'] in ['bold', '700', '800', '900']:
                self._wrap_element_content(element, '**', '**')
                
            if 'font-style' in rules and rules['font-style'] == 'italic':
                self._wrap_element_content(element, '*', '*')
                
            if 'text-decoration' in rules and 'underline' in rules['text-decoration']:
                self._wrap_element_content(element, '<u>', '</u>')
                
            # Handle display properties
            if 'display' in rules and rules['display'] == 'none':
                element.decompose()
                
        except Exception as e:
            print(f"Error applying element styling: {str(e)}")
            
    def _wrap_element_content(self, element: Tag, prefix: str, suffix: str):
        """Wrap element content with markdown formatting"""
        try:
            if element.string:
                element.string = f"{prefix}{element.string}{suffix}"
            else:
                # Handle elements with mixed content
                contents = list(element.contents)
                element.clear()
                element.append(prefix)
                element.extend(contents)
                element.append(suffix)
                
        except Exception:
            pass
            
    def _post_process_markdown(self, markdown: str) -> str:
        """Post-process markdown for better terminal display using dynamic filtering"""
        try:
            # Use dynamic content filter instead of hardcoded patterns
            markdown = self.content_filter.filter_content(markdown)
            
            # Clean up excessive whitespace
            markdown = re.sub(r'\n\s*\n\s*\n', '\n\n', markdown)
            
            # Fix list formatting
            markdown = re.sub(r'\n\s*-\s*\n', '\n\n- ', markdown)
            
            # Ensure proper heading spacing
            markdown = re.sub(r'\n(#{1,6}\s+[^\n]+)\n', r'\n\n\1\n\n', markdown)
            
            # Clean up table formatting
            markdown = self._fix_table_formatting(markdown)
            
            return markdown.strip()
            
        except Exception:
            return markdown
    
    def configure_filter(self, **settings):
        """Allow configuration of the dynamic content filter"""
        if hasattr(self.content_filter, 'update_thresholds'):
            self.content_filter.update_thresholds(settings)
        
    def _enhance_form_elements(self, soup: BeautifulSoup):
        """Enhance form elements for better terminal display"""
        try:
            # Enhance input elements
            for input_tag in soup.find_all('input'):
                self._render_input_element(input_tag)
            
            # Enhance button elements
            for button_tag in soup.find_all('button'):
                self._render_button_element(button_tag)
                
            # Enhance textarea elements
            for textarea_tag in soup.find_all('textarea'):
                self._render_textarea_element(textarea_tag)
                
            # Enhance select elements
            for select_tag in soup.find_all('select'):
                self._render_select_element(select_tag)
                
            # Enhance form elements
            for form_tag in soup.find_all('form'):
                self._render_form_element(form_tag)
                
        except Exception as e:
            print(f"Error enhancing form elements: {str(e)}")
    
    def _render_input_element(self, input_tag: Tag):
        """Convert input elements to terminal-friendly display"""
        try:
            input_type = input_tag.get('type', 'text').lower()
            name = input_tag.get('name', '')
            placeholder = input_tag.get('placeholder', '')
            value = input_tag.get('value', '')
            
            # Create visual representation based on input type
            if input_type == 'submit':
                # Render submit button
                button_text = value or 'Submit'
                new_content = f"[🔍 **{button_text}**]"
                
            elif input_type == 'button':
                # Render regular button
                button_text = value or 'Button'
                new_content = f"[📱 **{button_text}**]"
                
            elif input_type == 'search':
                # Render search box
                search_text = placeholder or 'Search...'
                search_value = value or ''
                if search_value:
                    new_content = f"🔍 [{search_value}] ({search_text})"
                else:
                    new_content = f"🔍 [____________] ({search_text})"
                    
            elif input_type == 'text':
                # Render text input
                input_text = placeholder or f'{name}' if name else 'Text input'
                input_value = value or ''
                if input_value:
                    new_content = f"📝 [{input_value}] ({input_text})"
                else:
                    new_content = f"📝 [____________] ({input_text})"
                    
            elif input_type == 'email':
                # Render email input
                email_text = placeholder or 'Email address'
                email_value = value or ''
                if email_value:
                    new_content = f"📧 [{email_value}] ({email_text})"
                else:
                    new_content = f"📧 [____________] ({email_text})"
                    
            elif input_type == 'password':
                # Render password input
                password_text = placeholder or 'Password'
                new_content = f"🔒 [••••••••••••] ({password_text})"
                
            elif input_type == 'checkbox':
                # Render checkbox
                checked = input_tag.get('checked') is not None
                check_symbol = '☑️' if checked else '☐'
                label_text = input_tag.get('value', name or 'Option')
                new_content = f"{check_symbol} {label_text}"
                
            elif input_type == 'radio':
                # Render radio button
                checked = input_tag.get('checked') is not None
                radio_symbol = '🔘' if checked else '⚪'
                label_text = input_tag.get('value', name or 'Option')
                new_content = f"{radio_symbol} {label_text}"
                
            elif input_type == 'file':
                # Render file input
                new_content = f"📁 [Choose File...] (File upload)"
                
            elif input_type == 'range':
                # Render range slider
                min_val = input_tag.get('min', '0')
                max_val = input_tag.get('max', '100')
                current_val = input_tag.get('value', '50')
                new_content = f"🎚️ [{min_val}◄─────●─────►{max_val}] ({current_val})"
                
            elif input_type == 'hidden':
                # Don't render hidden inputs
                return
                
            else:
                # Generic input rendering
                generic_text = placeholder or f'{input_type.title()} input'
                new_content = f"⚙️ [____________] ({generic_text})"
            
            # Replace the input tag with enhanced content
            input_tag.clear()
            input_tag.name = 'span'
            input_tag.string = new_content
            
        except Exception as e:
            # Fallback for problematic inputs
            input_tag.string = f"[Input: {input_tag.get('type', 'text')}]"
    
    def _render_button_element(self, button_tag: Tag):
        """Convert button elements to terminal-friendly display"""
        try:
            button_text = button_tag.get_text(strip=True)
            button_type = button_tag.get('type', 'button').lower()
            
            if not button_text:
                button_text = button_tag.get('value', 'Button')
            
            # Choose appropriate emoji based on button type/context
            if button_type == 'submit' or 'submit' in button_text.lower():
                emoji = '🔍'
            elif 'search' in button_text.lower():
                emoji = '🔍'
            elif 'login' in button_text.lower() or 'sign in' in button_text.lower():
                emoji = '🔐'
            elif 'menu' in button_text.lower():
                emoji = '☰'
            elif 'close' in button_text.lower():
                emoji = '❌'
            elif 'next' in button_text.lower():
                emoji = '▶️'
            elif 'previous' in button_text.lower() or 'prev' in button_text.lower():
                emoji = '◀️'
            elif 'save' in button_text.lower():
                emoji = '💾'
            elif 'delete' in button_text.lower():
                emoji = '🗑️'
            else:
                emoji = '📱'
            
            # Create enhanced button display
            new_content = f"{emoji} **[{button_text}]**"
            
            button_tag.clear()
            button_tag.name = 'span'
            button_tag.string = new_content
            
        except Exception:
            button_tag.string = "[Button]"
    
    def _render_textarea_element(self, textarea_tag: Tag):
        """Convert textarea elements to terminal-friendly display"""
        try:
            placeholder = textarea_tag.get('placeholder', '')
            content = textarea_tag.get_text(strip=True)
            rows = textarea_tag.get('rows', '3')
            
            if content:
                new_content = f"📝 **Text Area:**\n┌{'─' * 50}┐\n│ {content[:46]:<46} │\n└{'─' * 50}┘"
            else:
                placeholder_text = placeholder or 'Enter text here...'
                new_content = f"📝 **Text Area:** ({placeholder_text})\n┌{'─' * 50}┐\n│{' ' * 50}│\n└{'─' * 50}┘"
            
            textarea_tag.clear()
            textarea_tag.name = 'div'
            textarea_tag.string = new_content
            
        except Exception:
            textarea_tag.string = "[Text Area]"
    
    def _render_select_element(self, select_tag: Tag):
        """Convert select elements to terminal-friendly display"""
        try:
            options = select_tag.find_all('option')
            selected_option = None
            
            # Find selected option
            for option in options:
                if option.get('selected') is not None:
                    selected_option = option.get_text(strip=True)
                    break
            
            if not selected_option and options:
                selected_option = options[0].get_text(strip=True)
            
            if not selected_option:
                selected_option = "Select option"
            
            # Count total options
            option_count = len(options)
            
            new_content = f"📋 **[{selected_option} ▼]** ({option_count} options)"
            
            select_tag.clear()
            select_tag.name = 'span'
            select_tag.string = new_content
            
        except Exception:
            select_tag.string = "[Select Menu]"
    
    def _render_form_element(self, form_tag: Tag):
        """Enhance form elements with visual boundaries"""
        try:
            # Add visual form boundary
            form_title = "Form"
            action = form_tag.get('action', '')
            method = form_tag.get('method', 'GET').upper()
            
            if action:
                form_info = f" → {method} {action}"
            else:
                form_info = f" ({method})"
            
            # Create form header using the form's soup reference
            form_header = form_tag.find_parent().new_tag('div') if form_tag.find_parent() else None
            if form_header:
                form_header.string = f"📋 **{form_title}**{form_info}\n{'─' * 60}\n"
                form_tag.insert(0, form_header)
            
                # Add form footer
                form_footer = form_tag.find_parent().new_tag('div')
                form_footer.string = f"\n{'─' * 60}"
                form_tag.append(form_footer)
            
        except Exception:
            pass
            
    def _fix_table_formatting(self, markdown: str) -> str:
        """Fix table formatting in markdown"""
        try:
            # Ensure tables have proper spacing
            markdown = re.sub(r'\n(\|[^\n]+\|)\n', r'\n\n\1\n', markdown)
            
            return markdown
            
        except Exception:
            return markdown
            
    def render_to_rich(self, markdown_content: str) -> None:
        """Render markdown content using Rich for better terminal display"""
        try:
            # Create Rich markdown object
            md = Markdown(markdown_content)
            
            # Print with Rich
            self.console.print(md)
            
        except Exception as e:
            # Fallback to plain text
            print(f"Rich rendering error: {str(e)}")
            print(markdown_content)
            
    def create_link_table(self, links: List[tuple]) -> Table:
        """Create a Rich table for displaying links"""
        table = Table(title="Page Links", show_header=True, header_style="bold magenta")
        table.add_column("Text", style="cyan", min_width=20)
        table.add_column("URL", style="blue", min_width=30)
        
        for text, url in links[:20]:  # Limit to first 20 links
            # Truncate long text/URLs for display
            display_text = text[:50] + "..." if len(text) > 50 else text
            display_url = url[:60] + "..." if len(url) > 60 else url
            
            table.add_row(display_text, display_url)
            
        return table
        
    def create_page_info_panel(self, info: Dict[str, str]) -> Panel:
        """Create a Rich panel for displaying page information"""
        content = []
        
        if info.get('title'):
            content.append(f"**Title:** {info['title']}")
            
        if info.get('url'):
            content.append(f"**URL:** {info['url']}")
            
        if info.get('description'):
            content.append(f"**Description:** {info['description']}")
            
        panel_content = "\n".join(content) if content else "No page information available"
        
        return Panel(panel_content, title="Page Information", border_style="green")
        
    def _extract_meaningful_content(self, markdown_content: str) -> str:
        """Extract meaningful content and filter out technical clutter (like AgentSDK)"""
        if not markdown_content:
            return ""
            
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
            'console.', 'addEventListener', 'setTimeout', 'config.',
            'ContextHub.', '.customEnvironment', '.beaconUrl', 
            '.adrumExt', 'cdcext.', 'cdclocale.', 'cpe.config',
            'cpe.version', 'maxUrlLength', 'Paths.CONTEXTHUB',
            'Paths.RESOURCE', 'Paths.SEGMENTATION', 'CQ_CONTEXT',
            'ANONYMOUS_HOME', 'targetedComponent', '.style.visibility',
            '.cdn.', '/content/dam/', 'icon_', '.svg)', 
            'if (targetedComponent)', '// Make the targeted', '/\\*',
            '\\*/', 'hideMethod', 'setting paths', 'setting initial'
        ]
        
        line_lower = line.lower()
        if any(pattern in line_lower for pattern in technical_patterns):
            return False
        
        # Skip lines that are mostly symbols or numbers
        alpha_chars = sum(c.isalpha() for c in line)
        if alpha_chars < len(line) * 0.3:  # Less than 30% letters
            return False
            
        # Skip lines that look like configuration or code assignments
        if '=' in line and any(pattern in line for pattern in ['.config', '.Paths', '.Constants', 'appKey', 'version']):
            return False
            
        # Skip lines with too many forward slashes (URLs/paths)
        if line.count('/') > 3:
            return False
        
        # Keep meaningful content
        return True
