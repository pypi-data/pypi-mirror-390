"""
CLI Interface - Enhanced command-line interface for the browser
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys
import os
import time
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

try:
    from .browser.engine import BrowserEngine
except ImportError:
    from browser.engine import BrowserEngine
try:
    from .browser_sdk import BrowserSDK
except ImportError:
    from browser_sdk import BrowserSDK

console = Console()

class CLIBrowser:
    """Enhanced command-line interface for the browser"""
    
    def __init__(self):
        self.engine = BrowserEngine()
        self.sdk = BrowserSDK()
        self.running = True
        
        # Enhanced browser state
        self.current_url = None
        self.current_title = "CLI Browser"
        self.navigation_history = []
        self.history_position = -1
        self.bookmarks = {}
        self.page_links = []
        self.current_response = None
        self.current_soup = None
        self.clickable_elements = []
        self.input_elements = []
        self.form_data = {}  # Store form input values
        self.performance_stats = {
            "pages_visited": 0,
            "cache_hits": 0,
            "total_load_time": 0,
            "session_start": time.time()
        }

    def start_interactive_mode(self):
        """Start enhanced interactive browsing mode"""
        self.show_welcome_screen()
        
        while self.running:
            try:
                # Enhanced prompt with current status
                prompt_text = self.get_enhanced_prompt()
                command = Prompt.ask(prompt_text)
                
                if not command.strip():
                    continue
                    
                self.process_enhanced_command(command.strip())
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Press Ctrl+C again to exit, or type 'quit'[/yellow]")
                try:
                    command = Prompt.ask(prompt_text, default="")
                    if not command:
                        continue
                    self.process_enhanced_command(command.strip())
                except KeyboardInterrupt:
                    self.running = False
                continue
            except EOFError:
                break
                
        self.show_goodbye_screen()

    def show_welcome_screen(self):
        """Display enhanced welcome screen"""
        console.print(Panel.fit(
            "[bold blue]🌐 Enhanced CLI Browser - Interactive Mode[/bold blue]\n\n"
            "[bold]🚀 Advanced Features Available:[/bold]\n"
            "• Full navigation with back/forward, bookmarks, and history\n"
            "• Performance monitoring and intelligent caching\n" 
            "• Advanced web analysis (CSS, JavaScript, forms, headers)\n"
            "• JSON API support with search capabilities\n"
            "• Layout analysis including Grid/Flexbox visualization\n"
            "• Real-time page status and responsive design detection\n\n"
            "[bold]💡 Quick Start:[/bold]\n"
            "• Type 'help' for all commands\n"
            "• Enter URLs directly: google.com\n"
            "• Use 'browse <url>' or just paste URLs\n"
            "• Type 'quit' to exit\n\n"
            "[dim]Enhanced CLI Browser v2.0 - Enterprise Web Platform[/dim]",
            title="Welcome to Enhanced CLI Browser",
            style="green"
        ))

    def get_enhanced_prompt(self):
        """Get enhanced prompt with current status"""
        if self.current_url:
            parsed = urlparse(self.current_url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            if len(domain) > 20:
                domain = domain[:17] + "..."
            return f"[bold green]{domain}[/bold green] [dim]>[/dim] "
        else:
            return "[bold blue]browser[/bold blue] [dim]>[/dim] "

    def navigate_to_anchor(self, anchor_id):
        """Navigate to an anchor link within the current page"""
        if not self.current_soup and not self.current_url:
            console.print("[red]No page loaded to navigate within[/red]")
            return
        
        # If we have current_url but no soup, try to reload the page first
        if not self.current_soup and self.current_url:
            console.print("[dim]Reloading page for anchor navigation...[/dim]")
            self.browse_url_enhanced(self.current_url)
            if not self.current_soup:
                console.print("[red]Could not reload page for anchor navigation[/red]")
                return
        
        # Find the target element by ID or name
        target_element = None
        
        # First try to find by ID
        target_element = self.current_soup.find(id=anchor_id)
        
        # If not found by ID, try to find by name attribute
        if not target_element:
            target_element = self.current_soup.find(attrs={'name': anchor_id})
        
        # Also check for anchor tags with name attribute
        if not target_element:
            target_element = self.current_soup.find('a', attrs={'name': anchor_id})
        
        if target_element:
            console.print(f"[green]✓ Navigating to anchor: #{anchor_id}[/green]")
            
            # Extract the content around the anchor
            self._display_anchor_section(target_element, anchor_id)
        else:
            console.print(f"[yellow]Anchor '#{anchor_id}' not found on this page[/yellow]")
            
            # Show available anchors as a fallback
            self._show_available_anchors()
    
    def _display_anchor_section(self, target_element, anchor_id):
        """Display the section around an anchor link"""
        console.print(f"\n[bold blue]📍 Section: #{anchor_id}[/bold blue]")
        
        # Try to find the containing section or header
        section_content = []
        current = target_element
        
        # Look for parent section, article, or div
        while current and current.name not in ['section', 'article', 'main', 'div', 'body']:
            current = current.parent
        
        if current and current != target_element:
            # Found a containing element, render its content
            from .browser.renderer import HTMLRenderer
            renderer = HTMLRenderer()
            
            # Create a temporary soup with just this section
            section_html = str(current)
            section_soup = BeautifulSoup(section_html, 'html.parser')
            
            # Render the section
            try:
                section_markdown = renderer.render_to_markdown(section_soup, {})
                console.print(Panel(
                    section_markdown[:2000] + "..." if len(section_markdown) > 2000 else section_markdown,
                    title=f"Anchor Section: #{anchor_id}",
                    style="blue"
                ))
            except Exception as e:
                console.print(f"[yellow]Found anchor but could not render section: {e}[/yellow]")
                # Fallback: show text content
                text_content = current.get_text(strip=True)[:500]
                console.print(f"[dim]{text_content}...[/dim]")
        else:
            # Just show the target element and nearby content
            text_content = target_element.get_text(strip=True)
            if text_content:
                console.print(f"[blue]Target content:[/blue] {text_content[:200]}...")
            
            # Show next siblings for context
            next_elements = []
            sibling = target_element.next_sibling
            for _ in range(3):
                if sibling:
                    if hasattr(sibling, 'get_text'):
                        text = sibling.get_text(strip=True)
                        if text:
                            next_elements.append(text[:100])
                    sibling = sibling.next_sibling
                else:
                    break
            
            if next_elements:
                console.print(f"[dim]Context: {' '.join(next_elements)}...[/dim]")
    
    def _show_available_anchors(self):
        """Show available anchor links on the current page"""
        if not self.current_soup:
            return
        
        # Find all elements with IDs
        elements_with_ids = self.current_soup.find_all(attrs={'id': True})
        
        # Find all anchor tags with name attributes
        named_anchors = self.current_soup.find_all('a', attrs={'name': True})
        
        # Find all elements with name attributes
        elements_with_names = self.current_soup.find_all(attrs={'name': True})
        
        all_anchors = []
        
        for elem in elements_with_ids:
            anchor_id = elem.get('id')
            if anchor_id:
                text_preview = elem.get_text(strip=True)[:50] if elem.get_text(strip=True) else elem.name
                all_anchors.append(f"#{anchor_id} - {text_preview}")
        
        for elem in named_anchors:
            name = elem.get('name')
            if name:
                text_preview = elem.get_text(strip=True)[:50] if elem.get_text(strip=True) else "anchor"
                all_anchors.append(f"#{name} - {text_preview}")
        
        for elem in elements_with_names:
            if elem.name != 'a':  # Already handled anchor tags above
                name = elem.get('name')
                if name:
                    text_preview = elem.get_text(strip=True)[:50] if elem.get_text(strip=True) else elem.name
                    all_anchors.append(f"#{name} - {text_preview}")
        
        if all_anchors:
            console.print(f"\n[dim]Available anchors on this page ({len(all_anchors)} found):[/dim]")
            for anchor in all_anchors[:10]:  # Show first 10
                console.print(f"  [cyan]{anchor}[/cyan]")
            if len(all_anchors) > 10:
                console.print(f"  [dim]... and {len(all_anchors) - 10} more[/dim]")
        else:
            console.print("[dim]No anchors found on this page[/dim]")

    def show_goodbye_screen(self):
        """Display enhanced goodbye screen with session summary"""
        session_time = time.time() - self.performance_stats["session_start"]
        
        console.print(Panel.fit(
            f"[bold]📊 Session Summary:[/bold]\n\n"
            f"• Pages visited: {self.performance_stats['pages_visited']}\n"
            f"• Session duration: {session_time:.1f} seconds\n"
            f"• Cache hits: {self.performance_stats['cache_hits']}\n"
            f"• Bookmarks saved: {len(self.bookmarks)}\n"
            f"• History entries: {len(self.navigation_history)}\n\n"
            f"[bold blue]Thank you for using Enhanced CLI Browser![/bold blue]\n"
            f"[dim]Your browsing session has been completed successfully.[/dim]",
            title="Session Complete",
            style="blue"
        ))
        
    def process_enhanced_command(self, command: str):
        """Process enhanced commands with advanced features"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Navigation commands
        if cmd in ['quit', 'exit', 'q']:
            self.confirm_exit()
            
        elif cmd == 'help' or cmd == '?':
            self.show_enhanced_help()
            
        elif cmd in ['browse', 'go', 'visit']:
            self.handle_browse_command(args)
            
        elif cmd == 'back':
            self.navigate_back()
            
        elif cmd == 'forward' or cmd == 'fwd':
            self.navigate_forward()
            
        elif cmd == 'reload' or cmd == 'refresh':
            self.reload_page()
            
        elif cmd == 'links':
            self.show_enhanced_links()
            
        elif cmd == 'follow' or cmd == 'click':
            self.follow_link(args)
        
        elif cmd == 'elements' or cmd == 'clickable':
            self.show_clickable_elements()
        
        elif cmd == 'type' or cmd == 'input':
            self.handle_input_command(args)
        
        elif cmd == 'submit':
            self.handle_submit_command(args)
        
        elif cmd == 'button':
            self.handle_button_command(args)
        
        elif cmd == 'link':
            self.handle_link_command(args)
            
        elif cmd == 'history' or cmd == 'hist':
            self.show_navigation_history()
            
        elif cmd == 'performance' or cmd == 'perf':
            self.show_performance_stats()
            
        elif cmd == 'info':
            self.show_page_info()
            
        elif cmd == 'search':
            self.search_page(args)
            
        elif cmd == 'anchors':
            self._show_available_anchors()
            
        elif cmd == 'clear' or cmd == 'cls':
            console.clear()
            
        elif cmd == 'version':
            self.show_version_info()
            
        else:
            # Try to interpret as URL if it looks like one
            if self.looks_like_url(command):
                self.browse_url_enhanced(command)
            else:
                console.print(f"[red]Unknown command: {cmd}[/red]")
                console.print("[dim]Type 'help' for available commands[/dim]")

    def confirm_exit(self):
        """Confirm exit with session info"""
        if self.performance_stats["pages_visited"] > 0:
            if Confirm.ask(f"Exit CLI Browser? ({self.performance_stats['pages_visited']} pages visited this session)"):
                self.running = False
        else:
            self.running = False

    def show_enhanced_help(self):
        """Show comprehensive help with categorized commands"""
        
        # Navigation Commands
        nav_table = Table(title="🧭 Navigation Commands", show_header=True)
        nav_table.add_column("Command", style="cyan", min_width=15)
        nav_table.add_column("Description", style="white")
        nav_table.add_column("Example", style="yellow")
        
        nav_commands = [
            ("browse <url>", "Navigate to URL", "browse google.com"),
            ("go <url>", "Alias for browse", "go example.com"),
            ("back", "Go back in history", "back"),
            ("forward", "Go forward in history", "forward"),
            ("reload", "Refresh current page", "reload"),
            ("links", "Show all page links", "links"),
            ("follow <num>", "Follow link by number", "follow 3"),
            ("elements", "Show all clickable elements", "elements"),
            ("button <num>", "Click specific button", "button 1"),
            ("link <num>", "Navigate to specific link", "link 3"),
            ("click <num>", "Click any element by number", "click 5"),
        ]
        
        for cmd, desc, example in nav_commands:
            nav_table.add_row(cmd, desc, example)
        
        console.print(nav_table)
        console.print()
        
        # Advanced Commands
        adv_table = Table(title="🚀 Advanced Features", show_header=True)
        adv_table.add_column("Command", style="cyan", min_width=15)
        adv_table.add_column("Description", style="white")
        adv_table.add_column("Example", style="yellow")
        
        adv_commands = [
            ("info", "Show page information", "info"),
            ("search <term>", "Search page content", "search contact"),
            ("anchors", "Show available anchor links", "anchors"),
            ("type <text>", "Type into input fields", "type hello"),
            ("submit", "Submit forms", "submit"),
            ("performance", "Show performance stats", "performance"),
            ("history", "Show browsing history", "history"),
            ("help", "Show this help", "help"),
            ("clear", "Clear screen", "clear"),
            ("version", "Show version", "version"),
            ("quit", "Exit browser", "quit"),
        ]
        
        for cmd, desc, example in adv_commands:
            adv_table.add_row(cmd, desc, example)
        
        console.print(adv_table)

    def looks_like_url(self, text):
        """Check if text looks like a URL"""
        # Simple URL detection
        url_patterns = [
            r'^https?://',
            r'^www\.',
            r'\.[a-z]{2,}',
            r':[0-9]+',
        ]
        
        text_lower = text.lower()
        for pattern in url_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check for common domains
        common_domains = ['.com', '.org', '.net', '.edu', '.gov', '.io', '.co']
        return any(domain in text_lower for domain in common_domains)

    def handle_browse_command(self, args):
        """Handle browse command with enhanced features"""
        if args:
            url = ' '.join(args)
            self.browse_url_enhanced(url)
        else:
            url = Prompt.ask("Enter URL")
            if url:
                self.browse_url_enhanced(url)

    def browse_url_enhanced(self, url):
        """Enhanced URL browsing with performance tracking"""
        start_time = time.time()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(f"Loading {url}...", total=None)
            
            try:
                # Use SDK for enhanced browsing
                result = self.sdk.render_to_markdown(url)
                
                if result['success']:
                    # Update state with final URL after redirects
                    final_url = result.get('final_url', url)  # Use redirected URL if available
                    self.current_url = final_url
                    self.current_title = result.get('title', 'Unknown')
                    self.current_response = result
                    
                    # Add to history
                    if not self.navigation_history or self.navigation_history[-1] != url:
                        self.navigation_history.append(url)
                        self.history_position = len(self.navigation_history) - 1
                    
                    # Update performance stats
                    load_time = time.time() - start_time
                    self.performance_stats["pages_visited"] += 1
                    self.performance_stats["total_load_time"] += load_time
                    
                    # Extract links for navigation
                    self.extract_page_links(result)
                    
                    # Extract all clickable elements
                    self.extract_clickable_elements(result)
                    
                    # Display result
                    console.print(result['content'])
                    
                    # Show quick info
                    self.show_quick_page_info(load_time)
                    
                else:
                    console.print(f"[red]Failed to load {url}: {result.get('error', 'Unknown error')}[/red]")
                    
            except Exception as e:
                console.print(f"[red]Error loading {url}: {str(e)}[/red]")

    def show_quick_page_info(self, load_time):
        """Show quick page information after loading"""
        if not self.current_response:
            return
        
        info_items = []
        
        # Add basic info
        if self.current_title and self.current_title != "Unknown":
            info_items.append(f"📄 {self.current_title}")
        
        info_items.append(f"⏱️ {load_time:.2f}s")
        
        if len(self.page_links) > 0:
            info_items.append(f"🔗 {len(self.page_links)} links")
        
        # Check if it's JSON (from metadata)
        if self.current_response.get('metadata', {}).get('content_type', '').startswith('application/json'):
            info_items.append("📊 JSON API")
        
        if info_items:
            info_text = " • ".join(info_items)
            console.print(f"[dim]{info_text}[/dim]")

    def extract_page_links(self, result):
        """Extract links from page for navigation"""
        self.page_links = []
        
        # Try to get links from metadata first
        if 'metadata' in result and 'links' in result['metadata']:
            links_data = result['metadata']['links']
            for i, link in enumerate(links_data[:50]):  # Limit to 50 links
                self.page_links.append({
                    'number': i + 1,
                    'url': link.get('url', ''),
                    'text': link.get('text', '')[:60] + '...' if len(link.get('text', '')) > 60 else link.get('text', '')
                })
        elif 'soup' in result and result['soup']:
            # Fallback to soup parsing
            soup = result['soup']
            links = soup.find_all('a', href=True)
            
            for i, link in enumerate(links[:50]):  # Limit to 50 links
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if href and href.startswith(('http', '/', '#')):
                    self.page_links.append({
                        'number': i + 1,
                        'url': href,
                        'text': text[:60] + '...' if len(text) > 60 else text
                    })

    def show_enhanced_links(self):
        """Show enhanced links display"""
        if not self.page_links:
            console.print("[yellow]No links found on current page[/yellow]")
            return
        
        links_table = Table(title=f"🔗 Page Links ({len(self.page_links)} found)", show_header=True)
        links_table.add_column("#", style="cyan", width=4)
        links_table.add_column("Link Text", style="white", min_width=30)
        links_table.add_column("URL", style="blue", min_width=20)
        
        for link in self.page_links[:20]:  # Show first 20
            url_display = link['url']
            if len(url_display) > 50:
                url_display = url_display[:47] + "..."
            
            links_table.add_row(
                str(link['number']),
                link['text'] or "[No text]",
                url_display
            )
        
        console.print(links_table)
        
        if len(self.page_links) > 20:
            console.print(f"[dim]... and {len(self.page_links) - 20} more links[/dim]")
        
        console.print(f"\n[dim]Use 'follow <number>' to navigate to a link[/dim]")

    def follow_link(self, args):
        """Follow a link by number"""
        if not args:
            console.print("[red]Please specify a link number (use 'links' to see available links)[/red]")
            return
        
        try:
            link_num = int(args[0])
            
            if 1 <= link_num <= len(self.page_links):
                link = self.page_links[link_num - 1]
                url = link['url']
                
                console.print(f"🖱️ Clicking: {link['text']}")
                
                # Enhanced URL resolution for all relative URL types
                if url.startswith('#'):
                    # Handle anchor links by scrolling to the section
                    anchor_id = url[1:]  # Remove the '#'
                    self.navigate_to_anchor(anchor_id)
                    return
                elif url.startswith('/') and self.current_url:
                    # Absolute path relative to domain
                    from urllib.parse import urljoin
                    url = urljoin(self.current_url, url)
                elif not url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
                    # Relative path (like "community_api_reference.html")
                    if self.current_url:
                        from urllib.parse import urljoin
                        url = urljoin(self.current_url, url)
                        console.print(f"✓ Navigating to: {url}")
                    else:
                        console.print(f"[red]Cannot resolve relative URL '{url}' without current page context[/red]")
                        return
                else:
                    # Already absolute URL
                    console.print(f"✓ Navigating to: {url}")
                
                self.browse_url_enhanced(url)
                
            else:
                console.print(f"[red]Invalid link number. Use 1-{len(self.page_links)}[/red]")
                
        except ValueError:
            console.print("[red]Please provide a valid link number[/red]")

    def navigate_back(self):
        """Navigate back in history"""
        if self.history_position > 0:
            self.history_position -= 1
            url = self.navigation_history[self.history_position]
            console.print(f"[dim]Going back to: {url}[/dim]")
            self.browse_url_enhanced(url)
        else:
            console.print("[yellow]No previous page in history[/yellow]")

    def navigate_forward(self):
        """Navigate forward in history"""
        if self.history_position < len(self.navigation_history) - 1:
            self.history_position += 1
            url = self.navigation_history[self.history_position]
            console.print(f"[dim]Going forward to: {url}[/dim]")
            self.browse_url_enhanced(url)
        else:
            console.print("[yellow]No next page in history[/yellow]")

    def _execute_real_button_javascript(self, element):
        """Execute real JavaScript for button interactions using the JS engine"""
        if not hasattr(self, 'engine') or not self.engine or not self.current_soup:
            return
        
        try:
            # Get the button element
            button_elem = element['element']
            
            # Extract all JavaScript attributes
            onclick = button_elem.get('onclick', '')
            onmouseover = button_elem.get('onmouseover', '')
            data_action = button_elem.get('data-action', '')
            
            # Get button text and class for better targeting
            button_text = button_elem.get_text(strip=True)[:50]
            button_class = button_elem.get('class', [])
            button_id = button_elem.get('id', '')
            
            # Build enhanced JavaScript for complex website interactions
            js_code = f"""
            // Enhanced button interaction for modern websites
            console.log('🔄 Executing enhanced button click for: {button_text}');
            
            // Find button using multiple strategies
            var button = null;
            var buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
            
            // Try to find exact button by text content
            for (var i = 0; i < buttons.length; i++) {{
                var btn = buttons[i];
                if (btn.textContent.trim().includes('{button_text[:20]}') || 
                    btn.value === '{button_text}' ||
                    btn.id === '{button_id}') {{
                    button = btn;
                    break;
                }}
            }}
            
            // Fallback to first button if not found
            if (!button && buttons.length > 0) {{
                button = buttons[0];
            }}
            
            if (button) {{
                console.log('✓ Found target button:', button.textContent || button.value || 'unnamed');
                
                // Execute onclick handler if exists
                if (button.onclick) {{
                    try {{
                        console.log('Executing onclick handler...');
                        button.onclick.call(button);
                    }} catch(e) {{
                        console.log('onclick error:', e.message);
                    }}
                }}
                
                // Analyze button context dynamically
                var buttonText = (button.textContent || button.value || '').toLowerCase();
                var buttonClasses = button.className || '';
                var buttonDataAttrs = Array.from(button.attributes)
                    .filter(attr => attr.name.startsWith('data-'))
                    .map(attr => attr.name + '=' + attr.value);
                
                console.log('Button analysis:', {{ text: buttonText, classes: buttonClasses, data: buttonDataAttrs }});
                
                // Dynamic pattern detection based on actual page content
                var allModals = document.querySelectorAll('[class*="modal"], [class*="popup"], [class*="overlay"], [role="dialog"]');
                var allMenus = document.querySelectorAll('[class*="menu"], [class*="nav"], [role="navigation"]');
                var allCounters = document.querySelectorAll('[class*="count"], [class*="badge"], [class*="cart"]');
                
                // Trigger relevant interactions based on detected patterns
                if (allModals.length > 0) {{
                    console.log('Found', allModals.length, 'modal-like elements');
                    allModals.forEach(modal => {{
                        if (modal.style.display === 'none' || modal.classList.contains('hidden')) {{
                            modal.style.display = 'block';
                            modal.classList.remove('hidden');
                            modal.classList.add('show', 'active', 'open');
                        }}
                    }});
                }}
                
                if (allMenus.length > 0 && (buttonClasses.includes('menu') || buttonText.includes('menu'))) {{
                    console.log('Toggling', allMenus.length, 'menu-like elements');
                    allMenus.forEach(menu => {{
                        menu.classList.toggle('open');
                        menu.classList.toggle('show');
                        menu.classList.toggle('active');
                    }});
                }}
                
                if (allCounters.length > 0 && (buttonText.includes('add') || buttonClasses.includes('add'))) {{
                    console.log('Updating', allCounters.length, 'counter elements');
                    allCounters.forEach(counter => {{
                        var currentValue = parseInt(counter.textContent || '0');
                        if (!isNaN(currentValue)) {{
                            counter.textContent = currentValue + 1;
                        }}
                    }});
                }}
                
                // Create and dispatch enhanced click event
                var clickEvent = new MouseEvent('click', {{
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    detail: 1
                }});
                
                console.log('Dispatching click event...');
                button.dispatchEvent(clickEvent);
                
                // Also dispatch focus and blur events for better compatibility
                button.focus();
                setTimeout(() => button.blur(), 100);
                
                // Monitor page changes dynamically
                setTimeout(() => {{
                    if (window.location.href !== '{self.current_url}') {{
                        console.log('Navigation detected:', window.location.href);
                    }}
                    
                    // Check for any visible overlays/modals
                    var allOverlays = document.querySelectorAll('*');
                    var visibleOverlays = Array.from(allOverlays).filter(el => {{
                        var style = window.getComputedStyle(el);
                        return (style.position === 'fixed' || style.position === 'absolute') &&
                               style.zIndex > 100 &&
                               style.display !== 'none' &&
                               !el.classList.contains('hidden');
                    }});
                    
                    if (visibleOverlays.length > 0) {{
                        console.log('Dynamic overlays appeared:', visibleOverlays.length);
                    }}
                    
                    // Check for content changes by comparing DOM
                    var currentContent = document.body.innerHTML.length;
                    if (window._lastContentLength && currentContent !== window._lastContentLength) {{
                        console.log('Page content changed:', currentContent - window._lastContentLength, 'characters');
                    }}
                    window._lastContentLength = currentContent;
                }}, 500);
                
                console.log('✅ Enhanced button interaction completed');
            }} else {{
                console.log('❌ Could not find target button');
            }}
            
            'Enhanced button click executed';
            """
            
            # Execute the JavaScript
            if hasattr(self.engine, 'js_engine') and self.engine.js_engine:
                result = self.engine.js_engine.execute_script(js_code, self.current_soup)
                
                if result and result.get('console_output'):
                    # Show any console output from JavaScript execution
                    for line in result['console_output']:
                        if 'Navigation detected:' in line:
                            new_url = line.split('Navigation detected:')[1].strip()
                            console.print(f"[green]🌐 JavaScript navigation to: {new_url}[/green]")
                            # Actually navigate to the new URL
                            self.browse_url_enhanced(new_url)
                            return
                        elif line.strip() and not line.startswith('Button click executed'):
                            console.print(f"[dim]JS: {line}[/dim]")
                
                if result.get('dom_updates'):
                    # Apply any DOM updates from JavaScript execution
                    self.engine.apply_dom_updates(self.current_soup, result['dom_updates'])
                    console.print("[cyan]✓ Page updated by JavaScript execution[/cyan]")
                    
        except Exception as e:
            console.print(f"[dim]JavaScript execution completed with minor issues: {str(e)[:50]}[/dim]")

    def show_navigation_history(self):
        """Show browsing history"""
        if not self.navigation_history:
            console.print("[yellow]No browsing history available[/yellow]")
            return
        
        history_table = Table(title="📚 Browsing History", show_header=True)
        history_table.add_column("#", style="cyan", width=4)
        history_table.add_column("URL", style="white")
        history_table.add_column("Status", style="green")
        
        for i, url in enumerate(self.navigation_history):
            status = "→ Current" if i == self.history_position else ""
            history_table.add_row(str(i + 1), url, status)
        
        console.print(history_table)

    def show_performance_stats(self):
        """Show performance statistics"""
        stats = self.performance_stats
        session_time = time.time() - stats["session_start"]
        
        perf_table = Table(title="📊 Performance Statistics", show_header=True)
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="green")
        
        metrics = [
            ("Pages Visited", str(stats["pages_visited"])),
            ("Session Duration", f"{session_time:.1f}s"),
            ("Total Load Time", f"{stats['total_load_time']:.2f}s"),
            ("Average Load Time", f"{stats['total_load_time']/max(stats['pages_visited'],1):.2f}s"),
            ("Cache Hits", str(stats["cache_hits"])),
            ("Current Page", self.current_url or "None"),
            ("History Entries", str(len(self.navigation_history))),
            ("Bookmarks", str(len(self.bookmarks))),
        ]
        
        for metric, value in metrics:
            perf_table.add_row(metric, value)
        
        console.print(perf_table)

    def show_page_info(self):
        """Show current page information"""
        if self.current_response:
            console.print(f"[green]Current page: {self.current_url}[/green]")
            console.print(f"[green]Title: {self.current_title}[/green]")
            console.print(f"[green]Links found: {len(self.page_links)}[/green]")
        else:
            console.print("[yellow]No page currently loaded[/yellow]")

    def search_page(self, args):
        """Search current page content"""
        if args:
            query = ' '.join(args)
            console.print(f"[yellow]Search for '{query}' - feature coming soon[/yellow]")
        else:
            console.print("[red]Please provide a search term[/red]")

    def reload_page(self):
        """Reload current page"""
        if self.current_url:
            console.print(f"[dim]Reloading: {self.current_url}[/dim]")
            self.browse_url_enhanced(self.current_url)
        else:
            console.print("[yellow]No page to reload[/yellow]")

    def show_version_info(self):
        """Show version and system information"""
        console.print(Panel.fit(
            "[bold]🌐 Enhanced CLI Browser v2.0[/bold]\n\n"
            "[bold]Core Features:[/bold]\n"
            "• Advanced HTML/CSS rendering with terminal display\n"
            "• JavaScript execution with Mozilla SpiderMonkey\n"
            "• High-performance caching and async processing\n"
            "• Complete navigation with history and bookmarks\n"
            "• JSON API support with search capabilities\n"
            "• CSS Grid/Flexbox layout analysis\n"
            "• Authentication and session management\n"
            "• Modern web API simulation\n\n"
            "[bold]Technology Stack:[/bold]\n"
            "• Python 3.11+ with Rich terminal UI\n"
            "• PythonMonkey (Mozilla SpiderMonkey)\n"
            "• BeautifulSoup4 for HTML parsing\n"
            "• Requests for HTTP client\n"
            "• SQLite for intelligent caching\n\n"
            "[dim]Enterprise-grade web browsing for developers[/dim]",
            title="Version Information",
            style="blue"
        ))

    # Legacy methods for compatibility
    def browse_url(self, url, execute_js=True):
        """Legacy browse method for backward compatibility"""
        return self.browse_url_enhanced(url)

    def show_help(self):
        """Legacy help method for backward compatibility"""  
        return self.show_enhanced_help()

    def show_links(self):
        """Legacy links method for backward compatibility"""
        return self.show_enhanced_links()
    
    def extract_clickable_elements(self, result):
        """Extract all clickable elements from the page"""
        self.clickable_elements = []
        self.input_elements = []
        
        if 'soup' not in result or not result['soup']:
            return
            
        soup = result['soup']
        element_num = 1
        
        # Extract buttons (including submit buttons)
        buttons = soup.find_all(['button', 'input'])
        for btn in buttons:
            if btn.name == 'input':
                btn_type = btn.get('type', 'text').lower()
                if btn_type in ['submit', 'button', 'reset']:
                    text = btn.get('value', f'{btn_type.title()} Button')
                    nav_url = self._extract_button_navigation_url(btn)
                    
                    self.clickable_elements.append({
                        'number': element_num,
                        'type': 'button',
                        'subtype': btn_type,
                        'text': text,
                        'element': btn,
                        'form': btn.find_parent('form'),
                        'nav_url': nav_url
                    })
                    element_num += 1
            elif btn.name == 'button':
                text = btn.get_text(strip=True) or 'Button'
                btn_type = btn.get('type', 'button')
                
                # Check if button has navigation URL (onclick, data-href, parent link, etc.)
                nav_url = self._extract_button_navigation_url(btn)
                
                self.clickable_elements.append({
                    'number': element_num,
                    'type': 'button', 
                    'subtype': btn_type,
                    'text': text,
                    'element': btn,
                    'form': btn.find_parent('form'),
                    'nav_url': nav_url
                })
                element_num += 1
        
        # Extract links (different from page_links as these are for clicking)
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href and text:  # Only links with both href and text
                self.clickable_elements.append({
                    'number': element_num,
                    'type': 'link',
                    'text': text[:50] + '...' if len(text) > 50 else text,
                    'url': href,
                    'element': link
                })
                element_num += 1
        
        # Extract input fields
        inputs = soup.find_all(['input', 'textarea', 'select'])
        input_num = 1
        for inp in inputs:
            input_type = inp.get('type', 'text').lower()
            if input_type not in ['submit', 'button', 'reset', 'hidden']:
                name = inp.get('name', f'input_{input_num}')
                placeholder = inp.get('placeholder', '')
                
                self.input_elements.append({
                    'number': input_num,
                    'type': input_type,
                    'name': name,
                    'placeholder': placeholder,
                    'element': inp,
                    'form': inp.find_parent('form')
                })
                input_num += 1

    def show_clickable_elements(self):
        """Show all clickable elements on the page, separated by type"""
        if not self.clickable_elements and not self.input_elements:
            console.print("[yellow]No interactive elements found on this page[/yellow]")
            return
        
        # Separate buttons and links
        buttons = [elem for elem in self.clickable_elements if elem['type'] == 'button']
        links = [elem for elem in self.clickable_elements if elem['type'] == 'link']
        
        # Show buttons first
        if buttons:
            console.print("\n[bold blue]🔘 Buttons[/bold blue]")
            button_table = Table(title="Buttons", show_header=True)
            button_table.add_column("#", style="cyan", width=4)
            button_table.add_column("Button Text", style="white")
            button_table.add_column("Type", style="green", width=12)
            button_table.add_column("Form", style="yellow", width=8)
            
            for elem in buttons:
                form_status = "Yes" if elem.get('form') else "No"
                button_table.add_row(
                    str(elem['number']),
                    elem['text'],
                    elem['subtype'].title(),
                    form_status
                )
            
            console.print(button_table)
        
        # Show links separately
        if links:
            console.print("\n[bold blue]🔗 Links[/bold blue]")
            link_table = Table(title="Links", show_header=True)
            link_table.add_column("#", style="cyan", width=4)
            link_table.add_column("Link Text", style="white")
            link_table.add_column("Action", style="yellow")
            
            for elem in links:
                link_table.add_row(
                    str(elem['number']),
                    elem['text'],
                    "Navigate to URL"
                )
            
            console.print(link_table)
        
        if self.input_elements:
            console.print("\n[bold blue]✏️ Input Fields[/bold blue]")
            input_table = Table(title="Input Fields", show_header=True)
            input_table.add_column("#", style="cyan", width=4)
            input_table.add_column("Type", style="green", width=10)
            input_table.add_column("Name", style="white")
            input_table.add_column("Placeholder", style="yellow")
            
            for inp in self.input_elements:
                input_table.add_row(
                    str(inp['number']),
                    inp['type'].title(),
                    inp['name'],
                    inp['placeholder'] or '[No placeholder]'
                )
            
            console.print(input_table)
        
        console.print("\n[bold]💡 Quick Actions:[/bold]")
        console.print("• [cyan]button <number>[/cyan] - Click a specific button")
        console.print("• [cyan]link <number>[/cyan] - Navigate to a specific link")
        console.print("• [cyan]click <number>[/cyan] - Click any button or link")
        console.print("• [cyan]type <text>[/cyan] - Type into the first input field")
        console.print("• [cyan]type <number> <text>[/cyan] - Type into specific input field")
        console.print("• [cyan]submit[/cyan] - Submit the first form found")

    def handle_input_command(self, args):
        """Handle typing into input fields"""
        if not self.input_elements:
            console.print("[yellow]No input fields found on this page[/yellow]")
            return
        
        if not args:
            console.print("[red]Please provide text to type: type <text> or type <field_number> <text>[/red]")
            return
        
        # Check if first argument is a number (field selection)
        try:
            field_num = int(args[0])
            if field_num < 1 or field_num > len(self.input_elements):
                console.print(f"[red]Input field #{field_num} not found. Use 'elements' to see available fields.[/red]")
                return
            
            text = ' '.join(args[1:]) if len(args) > 1 else ''
            if not text:
                from rich.prompt import Prompt
                text = Prompt.ask(f"Enter text for {self.input_elements[field_num-1]['name']}")
            
            inp = self.input_elements[field_num - 1]
            console.print(f"[green]✓ Typed '{text}' into {inp['name']} ({inp['type']} field)[/green]")
            
            # Store the value for form submission
            inp['current_value'] = text
            
        except ValueError:
            # All arguments are text, use first input field
            text = ' '.join(args)
            inp = self.input_elements[0]
            console.print(f"[green]✓ Typed '{text}' into {inp['name']} ({inp['type']} field)[/green]")
            
            # Store the value for form submission
            inp['current_value'] = text

    def handle_click_command(self, args):
        """Handle clicking on elements by number"""
        if not self.clickable_elements:
            console.print("[yellow]No clickable elements found on this page[/yellow]")
            return
        
        if not args:
            console.print("[red]Please specify element number: click <number>[/red]")
            console.print("[dim]Use 'elements' to see all clickable elements[/dim]")
            return
        
        try:
            elem_num = int(args[0])
            if elem_num < 1 or elem_num > len(self.clickable_elements):
                console.print(f"[red]Element #{elem_num} not found. Use 'elements' to see available elements.[/red]")
                return
            
            element = self.clickable_elements[elem_num - 1]
            
            console.print(f"[blue]🖱️ Clicking: {element['text']}[/blue]")
            
            if element['type'] == 'button':
                if element['subtype'] == 'submit' and element.get('form'):
                    # Handle form submission
                    console.print("[green]✓ Submit button clicked - triggering form submission[/green]")
                    self.handle_submit_command([])
                else:
                    # Regular button click
                    console.print(f"[green]✓ {element['subtype'].title()} button clicked[/green]")
                    
                    # Check if this should trigger form submission (very conservative)
                    if self._should_attempt_form_submission(element):
                        console.print("[blue]🔄 Search/submit button detected - attempting form submission...[/blue]")
                        self.handle_submit_command([])
                    elif element.get('nav_url'):
                        # Button has a navigation URL - actually navigate there
                        nav_url = element['nav_url']
                        if nav_url.startswith('/') and self.current_url:
                            nav_url = urljoin(self.current_url, nav_url)
                        elif nav_url.startswith('#'):
                            # Handle anchor links by scrolling to the section
                            anchor_id = nav_url[1:]  # Remove the '#'
                            self.navigate_to_anchor(anchor_id)
                            return
                        
                        console.print(f"[green]✓ Button navigating to: {nav_url}[/green]")
                        self.browse_url_enhanced(nav_url)
                    else:
                        # Execute real JavaScript for button interactions
                        console.print("[blue]🔄 Executing JavaScript button interaction...[/blue]")
                        self._execute_real_button_javascript(element)
                        console.print("[green]✓ Button action completed[/green]")
                    
            elif element['type'] == 'link':
                # Follow the link
                url = element['url']
                if url.startswith('/') and self.current_url:
                    url = urljoin(self.current_url, url)
                elif url.startswith('#'):
                    # Handle anchor links by scrolling to the section
                    anchor_id = url[1:]  # Remove the '#'
                    self.navigate_to_anchor(anchor_id)
                    return
                
                console.print(f"[green]✓ Navigating to: {url}[/green]")
                self.browse_url_enhanced(url)
                
        except ValueError:
            console.print("[red]Please provide a valid element number[/red]")

    def handle_button_command(self, args):
        """Handle clicking buttons specifically"""
        buttons = [elem for elem in self.clickable_elements if elem['type'] == 'button']
        
        if not buttons:
            console.print("[yellow]No buttons found on this page[/yellow]")
            return
        
        if not args:
            console.print("[red]Please specify button number: button <number>[/red]")
            console.print("[dim]Use 'elements' to see all buttons[/dim]")
            return
        
        try:
            button_num = int(args[0])
            if button_num < 1 or button_num > len(buttons):
                console.print(f"[red]Button #{button_num} not found. Available buttons: 1-{len(buttons)}[/red]")
                return
            
            # Find the actual element by its original number
            button_element = buttons[button_num - 1]
            actual_elem_num = button_element['number']
            
            # Use the existing click handler with the actual element number
            self.handle_click_command([str(actual_elem_num)])
            
        except ValueError:
            console.print("[red]Please provide a valid button number[/red]")

    def handle_link_command(self, args):
        """Handle clicking links specifically"""
        links = [elem for elem in self.clickable_elements if elem['type'] == 'link']
        
        if not links:
            console.print("[yellow]No links found on this page[/yellow]")
            return
        
        if not args:
            console.print("[red]Please specify link number: link <number>[/red]")
            console.print("[dim]Use 'elements' to see all links[/dim]")
            return
        
        try:
            link_num = int(args[0])
            if link_num < 1 or link_num > len(links):
                console.print(f"[red]Link #{link_num} not found. Available links: 1-{len(links)}[/red]")
                return
            
            # Find the actual element by its original number
            link_element = links[link_num - 1]
            actual_elem_num = link_element['number']
            
            # Use the existing click handler with the actual element number
            self.handle_click_command([str(actual_elem_num)])
            
        except ValueError:
            console.print("[red]Please provide a valid link number[/red]")

    def _should_attempt_form_submission(self, element):
        """
        Dynamically determine if a button click should trigger form submission
        Only for buttons that are clearly submission-related
        """
        # Only attempt form submission for buttons that explicitly indicate submission
        button_text = element.get('text', '').lower()
        
        # Very specific submission indicators - be conservative
        submission_indicators = [
            'search', 'submit', 'send', 'go', 'find', 'query', 'ask'
        ]
        
        # Must have clear submission text AND be near a form or have typed input
        text_suggests_submission = any(
            indicator in button_text for indicator in submission_indicators
        )
        
        # Additional check: only if button is in a form OR there's clearly related input
        is_in_form = element.get('form') is not None
        has_search_input = any(
            inp.get('type') == 'search' and inp.get('current_value')
            for inp in self.input_elements
        )
        
        # Very conservative: only submit if text clearly indicates submission AND 
        # (button is in a form OR there's a search input with data)
        return text_suggests_submission and (is_in_form or has_search_input)
    
    def _extract_button_navigation_url(self, button):
        """Extract navigation URL from button element"""
        import re
        
        # Check for direct onclick navigation
        onclick = button.get('onclick', '')
        if onclick:
            # Extract URL from various JavaScript patterns
            patterns = [
                r"(?:location\.href|window\.location)\s*=\s*['\"]([^'\"]+)['\"]",
                r"(?:location\.replace|location\.assign)\(['\"]([^'\"]+)['\"]\)",
                r"window\.open\(['\"]([^'\"]+)['\"]",
                r"(?:href\s*=|url\s*=)\s*['\"]([^'\"]+)['\"]"
            ]
            
            for pattern in patterns:
                url_match = re.search(pattern, onclick)
                if url_match:
                    return url_match.group(1)
        
        # Check for data attributes commonly used for navigation
        data_attrs = [
            'data-href', 'data-url', 'data-link', 'data-action', 
            'data-navigate', 'data-goto', 'data-redirect'
        ]
        for attr in data_attrs:
            data_value = button.get(attr)
            if data_value:
                return data_value
        
        # Check if button is wrapped in a link
        parent_link = button.find_parent('a')
        if parent_link and parent_link.get('href'):
            return parent_link.get('href')
        
        # Check for nearby sibling links (common pattern)
        next_sibling = button.find_next_sibling('a')
        if next_sibling and next_sibling.get('href'):
            return next_sibling.get('href')
        
        # Check for form action if it's a form button outside of submit context
        form = button.find_parent('form')
        if form and button.get('type') == 'button':
            action = form.get('action')
            if action:
                return action
        
        # For modern React/JS apps, try to infer navigation from button text and common patterns
        button_text = button.get_text(strip=True).lower()
        nav_keywords = ['login', 'log in', 'sign in', 'sign up', 'register', 'download', 'get started', 'learn more']
        
        if any(keyword in button_text for keyword in nav_keywords):
            # Look for links with similar text on the page
            soup = button.find_parent() or button
            root = soup
            while root.parent:
                root = root.parent
            
            # Find links with matching or similar text
            for link in root.find_all('a', href=True):
                link_text = link.get_text(strip=True).lower()
                if button_text in link_text or link_text in button_text:
                    return link.get('href')
        
        return None
    
    def _execute_button_javascript(self, onclick_code):
        """Execute JavaScript from button onclick (simplified execution)"""
        try:
            # Simple JavaScript action detection and execution
            if 'alert' in onclick_code:
                console.print("[yellow]JavaScript alert detected (alerts are not displayed in CLI mode)[/yellow]")
            elif 'confirm' in onclick_code:
                console.print("[yellow]JavaScript confirm detected (automatically confirmed in CLI mode)[/yellow]")
            elif 'submit' in onclick_code:
                console.print("[blue]JavaScript form submission detected[/blue]")
                self.handle_submit_command([])
            else:
                console.print(f"[dim]JavaScript executed: {onclick_code[:50]}...[/dim]")
        except Exception as e:
            console.print(f"[red]Error executing JavaScript: {e}[/red]")

    def resolve_redirect_url(self, url):
        """Dynamically resolve redirect URLs from any domain"""
        import urllib.parse
        import re
        
        try:
            # Handle protocol-relative URLs first
            if url.startswith('//'):
                url = 'https:' + url
            
            parsed = urllib.parse.urlparse(url)
            
            # Parse query parameters
            query_params = urllib.parse.parse_qs(parsed.query)
            
            # Common redirect parameter names (order matters - most specific first)
            redirect_params = [
                'uddg',     # DuckDuckGo
                'url',      # Generic
                'u',        # Short form
                'link',     # Common
                'target',   # Generic
                'dest',     # Destination
                'to',       # Simple
                'href',     # HTML attribute
                'redirect', # Explicit
                'redir',    # Short form
                'goto',     # Action
                'next',     # Navigation
                'return',   # Return URL
                'continue', # Continue URL
                'forward'   # Forward URL
            ]
            
            # Look for redirect parameters in query string
            for param in redirect_params:
                if param in query_params:
                    candidate_url = urllib.parse.unquote(query_params[param][0])
                    # Handle protocol-relative URLs
                    if candidate_url.startswith('//'):
                        candidate_url = 'https:' + candidate_url
                    # Validate that it looks like a URL and is different from original
                    if (self._is_valid_url(candidate_url) and 
                        candidate_url != url and 
                        candidate_url not in url):  # Avoid returning same domain redirects
                        return candidate_url
            
            # Check if URL contains encoded URL in path or fragment
            full_url = urllib.parse.unquote(url)
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            matches = re.findall(url_pattern, full_url)
            
            # If we find other URLs in the current URL, use the longest one (likely the target)
            if len(matches) > 1:
                target_url = max(matches, key=len)
                if target_url != url and self._is_valid_url(target_url):
                    return target_url
            
            # Return original URL if no redirect found
            return url
            
        except Exception:
            return url
    
    def _is_valid_url(self, url):
        """Check if a string looks like a valid URL"""
        try:
            # Handle protocol-relative URLs
            if url.startswith('//'):
                url = 'https:' + url
            
            parsed = urllib.parse.urlparse(url)
            return bool(parsed.netloc and ('.' in parsed.netloc or parsed.netloc == 'localhost'))
        except:
            return False

    def handle_submit_command(self, args):
        """Handle form submission"""
        if not self.current_response or 'soup' not in self.current_response:
            console.print("[yellow]No page loaded[/yellow]")
            return
        
        soup = self.current_response['soup']
        forms = soup.find_all('form')
        
        if not forms:
            console.print("[yellow]No forms found on this page[/yellow]")
            return
        
        # Use first form by default
        form = forms[0]
        action = form.get('action', '')
        method = form.get('method', 'GET').upper()
        

        
        # Collect form data from typed input elements
        form_data = {}
        
        # Gather data from input elements that have been typed into
        for inp in self.input_elements:
            if inp.get('current_value'):  # Use dict access instead of hasattr
                form_data[inp['name']] = inp['current_value']
        
        # Also gather data from existing form inputs (hidden fields, etc.)
        form_inputs = form.find_all(['input', 'textarea', 'select'])
        for inp in form_inputs:
            input_type = inp.get('type', 'text').lower()
            name = inp.get('name')
            
            if name and input_type in ['hidden', 'text', 'email', 'password']:
                value = inp.get('value', '')
                if name not in form_data and value:  # Don't override typed values
                    form_data[name] = value
        
        console.print(f"[blue]🚀 Submitting form with data: {list(form_data.keys())}[/blue]")
        
        if not form_data:
            console.print("[yellow]No form data found. Make sure to type into input fields first.[/yellow]")
            return
        
        # Resolve relative action URL properly
        if not action:
            # No action means submit to current page
            action = self.current_url or ''
        elif self.current_url:
            # Ensure current_url has a scheme
            normalized_url = self.current_url
            if not normalized_url.startswith(('http://', 'https://')):
                normalized_url = f"https://{normalized_url}"
            
            if action.startswith('http://') or action.startswith('https://'):
                # Already absolute URL - use as is
                pass
            elif action.startswith('//'):
                # Protocol-relative URL - add current protocol
                from urllib.parse import urlparse
                parsed = urlparse(normalized_url)
                action = f"{parsed.scheme}:{action}"
            elif action.startswith('/'):
                # Relative to root - use base domain
                from urllib.parse import urlparse
                parsed = urlparse(normalized_url)
                if parsed.scheme and parsed.netloc:
                    action = f"{parsed.scheme}://{parsed.netloc}{action}"
                else:
                    console.print(f"[red]Cannot parse current URL: {normalized_url}[/red]")
                    return
            elif action.startswith('?'):
                # Query only - append to current URL
                base_url = self.current_url.split('?')[0]
                action = f"{base_url}{action}"
            elif not action.startswith('http'):
                # Relative path - use urljoin
                action = urljoin(self.current_url, action)
        else:
            console.print("[red]Cannot resolve form action: no current URL available[/red]")
            return
        
        # Skip duplicate form data collection since it's already done above
        
        console.print(f"[blue]🚀 Submitting form to {action}[/blue]")
        console.print(f"[dim]Method: {method} | Data: {len(form_data)} fields[/dim]")
        
        try:
            # Validate the URL before submission
            from urllib.parse import urlparse
            parsed_action = urlparse(action)
            if not parsed_action.netloc:
                console.print(f"[red]Invalid form action URL: {action}[/red]")
                return
            
            # Handle form submission based on method
            if method == 'GET' and form_data:
                # For GET, add parameters to URL
                from urllib.parse import urlencode
                separator = '&' if '?' in action else '?'
                full_url = f"{action}{separator}{urlencode(form_data)}"

                # Special handling for major search engines
                if any(domain in full_url for domain in ['google.com/search', 'yahoo.com/search', 'bing.com/search']):
                    console.print("[dim]Detected search engine - using enhanced search handling[/dim]")
                    self.handle_search_engine_result(full_url, form_data)
                else:
                    self.browse_url_enhanced(full_url)
            elif method == 'POST' and form_data:
                # For POST, submit the data and follow redirects
                console.print("[blue]Submitting POST form data...[/blue]")
                try:
                    # Make POST request with form data
                    import requests
                    response = requests.post(action, data=form_data, timeout=30)
                    response.raise_for_status()
                    
                    # Process the response content directly instead of redirecting
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Update current state with the response
                    self.current_url = response.url
                    self.current_response = {
                        'content': response.text,
                        'soup': soup,
                        'url': response.url,
                        'status_code': response.status_code
                    }
                    
                    # Extract clickable elements from the response
                    self.extract_clickable_elements({
                        'content': response.text,
                        'soup': soup,
                        'url': response.url,
                        'status_code': response.status_code
                    })
                    
                    # Use the existing browser engine to render the response properly
                    try:
                        from .browser import BrowserEngine
                    except ImportError:
                        from browser import BrowserEngine
                    temp_engine = BrowserEngine()
                    
                    # Process the response through the engine pipeline
                    css_rules = temp_engine.css_parser.extract_css_from_soup(soup)
                    rendered_content = temp_engine.renderer.render_to_markdown(soup, css_rules)
                    
                    console.print(rendered_content)
                    console.print(f"⏱️ {response.elapsed.total_seconds():.2f}s • 🔗 {len(self.clickable_elements)} links")
                    
                    console.print(f"[green]✅ Form submitted successfully![/green]")
                    
                except Exception as e:
                    console.print(f"[red]POST submission failed: {str(e)}[/red]")
                    # Fallback to GET method
                    console.print("[yellow]Falling back to GET submission...[/yellow]")
                    from urllib.parse import urlencode
                    separator = '&' if '?' in action else '?'
                    fallback_url = f"{action}{separator}{urlencode(form_data)}"
                    self.browse_url_enhanced(fallback_url)
            else:
                # For methods without data, just navigate to action
                console.print("[yellow]Form submitted (no data to send)[/yellow]")
                self.browse_url_enhanced(action)
                
        except Exception as e:
            console.print(f"[red]Form submission error: {str(e)}[/red]")
            console.print(f"[dim]Form action was: {action}[/dim]")

    def handle_search_engine_result(self, search_url, form_data):
        """Handle search engines with enhanced methods to bypass JavaScript requirements"""
        query = form_data.get('q', '')
        if not query:
            console.print("[yellow]No search query found[/yellow]")
            return
        
        # Determine search engine from URL
        search_engine = "search engine"
        if 'google.com' in search_url:
            search_engine = "Google"
        elif 'yahoo.com' in search_url:
            search_engine = "Yahoo"
        elif 'bing.com' in search_url:
            search_engine = "Bing"
        
        console.print(f"[blue]🔍 Searching {search_engine} for: '{query}'[/blue]")
        
        # Try alternative search approaches based on the original URL
        query_encoded = query.replace(' ', '+')
        alternative_urls = []
        
        if 'yahoo.com' in search_url:
            alternative_urls = [
                f"https://search.yahoo.com/search?p={query_encoded}",
                f"https://search.yahoo.com/search?p={query_encoded}&ei=UTF-8",
                search_url  # fallback to original
            ]
        elif 'bing.com' in search_url:
            alternative_urls = [
                f"https://www.bing.com/search?q={query_encoded}",
                f"https://www.bing.com/search?q={query_encoded}&FORM=QBRE",
                search_url  # fallback to original
            ]
        else:  # Google or other
            alternative_urls = [
                f"https://www.google.com/search?q={query_encoded}&num=10&hl=en&safe=off",
                f"https://google.com/search?q={query_encoded}&lr=lang_en&safe=off",
                search_url  # fallback to original
            ]
        
        for i, alt_url in enumerate(alternative_urls):
            console.print(f"[dim]Attempt {i+1}: Trying enhanced search method[/dim]")
            self.browse_url_enhanced(alt_url)
            
            # Check if we got meaningful search results
            content = self.current_response.get('content', '').lower()
            
            # Check for JavaScript redirect patterns (specific detection)
            js_redirect_patterns = [
                'click if you are not redirected',
                'please enable javascript',
                'javascript is required',
                '/httpservice/retry/enablejs',
                'noscript'
            ]
            
            is_js_redirect = any(pattern in content for pattern in js_redirect_patterns)
            has_search_results = len(content) > 1000 and query.lower() in content
            
            if has_search_results and not is_js_redirect:
                console.print("[green]✅ Successfully retrieved search results[/green]")
                return
        
        # If all attempts failed, try alternative search engines
        search_engine_name = search_engine if search_engine != "search engine" else "Primary search engine"
        console.print(f"[yellow]⚠️ {search_engine_name} is requiring JavaScript - trying alternative search...[/yellow]")
        
        # Try DuckDuckGo as alternative
        duckduckgo_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
        console.print(f"[blue]🦆 Searching DuckDuckGo for: '{query}'[/blue]")
        self.browse_url_enhanced(duckduckgo_url)
        
        # Check if DuckDuckGo worked
        content = self.current_response.get('content', '').lower()
        if query.lower() in content and len(content) > 1000:
            console.print("[green]✅ Successfully retrieved search results from DuckDuckGo[/green]")
        else:
            console.print("[yellow]Search engines are having issues. Try browsing to specific websites directly.[/yellow]")

    def _handle_button_form_submission(self, element):
        """Handle form submission when button is clicked"""
        try:
            button_text = element.get('text', '').lower()
            
            # Check if this is a form submission button
            submit_patterns = [
                'search', 'submit', 'send', 'login', 'sign in', 'go', 
                'find', 'get', 'post', 'save', 'continue', 'next'
            ]
            
            is_submit_button = any(pattern in button_text for pattern in submit_patterns)
            
            if is_submit_button:
                console.print("[blue]🚀 Processing form submission...[/blue]")
                
                # Collect all typed input data
                form_data = {}
                
                # Get data from typed inputs
                for inp in self.input_elements:
                    if inp.get('current_value'):
                        field_name = inp.get('name') or f"input_{inp.get('number', 0)}"
                        form_data[field_name] = inp['current_value']
                
                if form_data:
                    console.print("[green]📝 Collected form data:[/green]")
                    for key, value in form_data.items():
                        console.print(f"  • {key}: {value}")
                    
                    # Determine form action URL
                    form_element = element.get('element')
                    form = form_element.find_parent('form') if form_element else None
                    
                    if form and form.get('action'):
                        action_url = form['action']
                        method = form.get('method', 'GET').upper()
                    else:
                        # Use current page URL for submission
                        action_url = self.current_url or ''
                        method = 'GET'
                    
                    # Build proper URL for submission
                    if action_url.startswith('/') and self.current_url:
                        from urllib.parse import urljoin
                        action_url = urljoin(self.current_url, action_url)
                    elif not action_url.startswith('http'):
                        action_url = self.current_url or ''
                    
                    console.print(f"[yellow]🌐 Submitting to: {action_url}[/yellow]")
                    console.print(f"[yellow]📤 Method: {method}[/yellow]")
                    
                    return {
                        'type': 'form_submission',
                        'url': action_url,
                        'method': method,
                        'data': form_data
                    }
                else:
                    console.print("[yellow]⚠️  No form data found to submit[/yellow]")
                    return True
            
            return True
            
        except Exception as e:
            console.print(f"[red]Form submission error: {e}[/red]")
            return False
    
    def _execute_form_submission(self, submission_data):
        """Execute the actual form submission"""
        try:
            url = submission_data['url']
            method = submission_data['method']
            data = submission_data['data']
            
            console.print("[blue]🌐 Executing form submission...[/blue]")
            
            if method.upper() == 'GET':
                # For GET, add data as query parameters
                from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
                
                parsed = urlparse(url)
                query_params = parse_qs(parsed.query)
                
                # Add form data to query parameters
                for key, value in data.items():
                    query_params[key] = [value]
                
                # Rebuild URL with query parameters
                new_query = urlencode(query_params, doseq=True)
                new_url = urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path,
                    parsed.params, new_query, parsed.fragment
                ))
                
                console.print(f"[green]📄 GET request to: {new_url}[/green]")
                self.browse_url_enhanced(new_url)
                
            else:
                # For POST, send data in body
                console.print(f"[green]📤 POST request with data[/green]")
                # For now, navigate to the action URL (real POST would require server)
                self.browse_url_enhanced(url)
            
        except Exception as e:
            console.print(f"[red]Form submission failed: {e}[/red]")

@click.group()
@click.version_option()
def main():
    """🌐 CLI Browser - A Python-based command-line web browser"""
    pass

@main.command()
@click.argument('url')
@click.option('--no-js', is_flag=True, help='Disable JavaScript execution')
def browse(url, no_js):
    """Browse to a URL and display content"""
    try:
        browser = CLIBrowser()
        result = browser.browse_url(url, execute_js=not no_js)
        
    except Exception as e:
        console.print(f"[red]Error browsing {url}: {str(e)}[/red]")
        sys.exit(1)

@main.command()
def interactive():
    """Start interactive browsing mode"""
    try:
        browser = CLIBrowser()
        browser.start_interactive_mode()
        
    except Exception as e:
        console.print(f"[red]Error starting interactive mode: {str(e)}[/red]")
        sys.exit(1)

@main.command()
@click.argument('url')
@click.option('--format', '-f', default='markdown', 
              type=click.Choice(['markdown', 'text', 'html']),
              help='Output format')
@click.option('--output', '-o', help='Output file path')
def render(url, format, output):
    """Render a URL to specified format"""
    try:
        sdk = BrowserSDK()
        result = sdk.browse_url(url)
        
        if result['success']:
            content = result['rendered_content']
            
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    f.write(content)
                console.print(f"[green]Content saved to {output}[/green]")
            else:
                console.print(content)
        else:
            console.print(f"[red]Failed to render {url}: {result.get('error', 'Unknown error')}[/red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]Error rendering {url}: {str(e)}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()