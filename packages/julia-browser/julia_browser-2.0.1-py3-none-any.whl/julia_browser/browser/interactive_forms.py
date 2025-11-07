"""
Interactive Forms Handler - Enhanced form interaction for CLI browser
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
import re
from urllib.parse import urljoin, urlparse
import requests

console = Console()

class InteractiveFormsHandler:
    """Handle interactive form elements and user input"""
    
    def __init__(self, browser_engine):
        self.engine = browser_engine
        self.current_forms = []
        self.current_buttons = []
        self.current_inputs = []
        
    def extract_interactive_elements(self, soup, base_url):
        """Extract all interactive elements from the page"""
        self.current_forms = []
        self.current_buttons = []
        self.current_inputs = []
        
        # Extract forms
        forms = soup.find_all('form')
        for i, form in enumerate(forms, 1):
            form_data = {
                'number': i,
                'action': form.get('action', ''),
                'method': form.get('method', 'GET').upper(),
                'inputs': [],
                'buttons': []
            }
            
            # Keep action URL as-is, let form submission handler resolve it
            # This prevents double URL resolution that causes malformed URLs
            
            # Extract inputs within this form
            inputs = form.find_all(['input', 'textarea', 'select'])
            for input_elem in inputs:
                input_data = self._extract_input_data(input_elem)
                if input_data:
                    form_data['inputs'].append(input_data)
            
            # Extract buttons within this form
            buttons = form.find_all(['button', 'input'])
            for btn in buttons:
                if btn.name == 'input' and btn.get('type') in ['submit', 'button']:
                    btn_data = self._extract_button_data(btn)
                    if btn_data:
                        form_data['buttons'].append(btn_data)
                elif btn.name == 'button':
                    btn_data = self._extract_button_data(btn)
                    if btn_data:
                        form_data['buttons'].append(btn_data)
            
            self.current_forms.append(form_data)
        
        # Extract standalone buttons (not in forms)
        standalone_buttons = soup.find_all(['button', 'a'])
        button_number = len([btn for form in self.current_forms for btn in form['buttons']]) + 1
        
        for btn in standalone_buttons:
            if btn.name == 'a' and btn.get('href'):
                btn_data = {
                    'number': button_number,
                    'text': btn.get_text(strip=True) or 'Link',
                    'type': 'link',
                    'action': urljoin(base_url, btn.get('href')),
                    'form': None
                }
                self.current_buttons.append(btn_data)
                button_number += 1
            elif btn.name == 'button' and not btn.find_parent('form'):
                btn_data = self._extract_button_data(btn)
                if btn_data:
                    btn_data['number'] = button_number
                    btn_data['form'] = None
                    self.current_buttons.append(btn_data)
                    button_number += 1
        
        # Extract standalone inputs
        standalone_inputs = soup.find_all(['input', 'textarea'])
        input_number = len([inp for form in self.current_forms for inp in form['inputs']]) + 1
        
        for inp in standalone_inputs:
            if not inp.find_parent('form'):
                input_data = self._extract_input_data(inp)
                if input_data:
                    input_data['number'] = input_number
                    input_data['form'] = None
                    self.current_inputs.append(input_data)
                    input_number += 1

    def _extract_input_data(self, input_elem):
        """Extract data from input element"""
        input_type = input_elem.get('type', 'text').lower()
        name = input_elem.get('name', '')
        placeholder = input_elem.get('placeholder', '')
        value = input_elem.get('value', '')
        required = input_elem.has_attr('required')
        
        if input_type in ['hidden', 'submit', 'button']:
            return None
        
        text = input_elem.get_text(strip=True) if input_elem.name == 'textarea' else ''
        
        return {
            'name': name,
            'type': input_type,
            'placeholder': placeholder,
            'value': value or text,
            'required': required,
            'element': input_elem.name
        }

    def _extract_button_data(self, button_elem):
        """Extract data from button element"""
        if button_elem.name == 'input':
            btn_type = button_elem.get('type', 'button')
            text = button_elem.get('value', 'Button')
        else:
            btn_type = button_elem.get('type', 'button')
            text = button_elem.get_text(strip=True) or 'Button'
        
        return {
            'text': text,
            'type': btn_type,
            'name': button_elem.get('name', ''),
            'value': button_elem.get('value', '')
        }

    def show_interactive_elements(self):
        """Display all interactive elements in a user-friendly way"""
        if not self.current_forms and not self.current_buttons and not self.current_inputs:
            console.print("[yellow]No interactive elements found on this page[/yellow]")
            return
        
        console.print("\n[bold blue]📋 Interactive Elements on This Page[/bold blue]")
        
        # Show forms
        if self.current_forms:
            for form in self.current_forms:
                self._display_form(form)
        
        # Show standalone buttons
        if self.current_buttons:
            console.print("\n[bold]🔘 Standalone Buttons[/bold]")
            buttons_table = Table(show_header=True)
            buttons_table.add_column("#", style="cyan", width=4)
            buttons_table.add_column("Button Text", style="white")
            buttons_table.add_column("Action", style="blue")
            
            for btn in self.current_buttons:
                action_display = btn.get('action', 'JavaScript action')
                if len(action_display) > 50:
                    action_display = action_display[:47] + "..."
                
                buttons_table.add_row(
                    str(btn['number']),
                    btn['text'],
                    action_display
                )
            
            console.print(buttons_table)
        
        # Show standalone inputs
        if self.current_inputs:
            console.print("\n[bold]📝 Standalone Input Fields[/bold]")
            inputs_table = Table(show_header=True)
            inputs_table.add_column("#", style="cyan", width=4)
            inputs_table.add_column("Type", style="green")
            inputs_table.add_column("Field Name", style="white")
            inputs_table.add_column("Placeholder", style="yellow")
            
            for inp in self.current_inputs:
                inputs_table.add_row(
                    str(inp['number']),
                    inp['type'].title(),
                    inp['name'] or '[No name]',
                    inp['placeholder'] or '[No placeholder]'
                )
            
            console.print(inputs_table)
        
        # Show usage instructions
        console.print("\n[bold]💡 Quick Actions:[/bold]")
        console.print("• Type [cyan]'click <number>'[/cyan] to click a button")
        console.print("• Type [cyan]'fill <form_number>'[/cyan] to fill out a form")
        console.print("• Type [cyan]'submit <form_number>'[/cyan] to submit a form")
        console.print("• Type [cyan]'forms'[/cyan] to see this list again")

    def _display_form(self, form):
        """Display a single form with its elements"""
        console.print(f"\n[bold]📋 Form #{form['number']}[/bold]")
        
        form_info = f"Method: {form['method']}"
        if form['action']:
            form_info += f" | Action: {form['action']}"
        console.print(f"[dim]{form_info}[/dim]")
        
        if form['inputs']:
            inputs_table = Table(title="Input Fields", show_header=True)
            inputs_table.add_column("Field", style="cyan")
            inputs_table.add_column("Type", style="green") 
            inputs_table.add_column("Name", style="white")
            inputs_table.add_column("Placeholder", style="yellow")
            inputs_table.add_column("Required", style="red")
            
            for inp in form['inputs']:
                inputs_table.add_row(
                    f"📝",
                    inp['type'].title(),
                    inp['name'] or '[No name]',
                    inp['placeholder'] or '[No placeholder]',
                    "✓" if inp['required'] else ""
                )
            
            console.print(inputs_table)
        
        if form['buttons']:
            buttons_table = Table(title="Form Buttons", show_header=True)
            buttons_table.add_column("Button", style="cyan")
            buttons_table.add_column("Text", style="white")
            buttons_table.add_column("Type", style="green")
            
            for btn in form['buttons']:
                buttons_table.add_row(
                    "🔘",
                    btn['text'],
                    btn['type'].title()
                )
            
            console.print(buttons_table)

    def click_button(self, button_number):
        """Click a button by number"""
        try:
            button_num = int(button_number)
            
            # Find button in forms first
            for form in self.current_forms:
                for i, btn in enumerate(form['buttons'], 1):
                    if button_num == len([b for f in self.current_forms[:self.current_forms.index(form)] for b in f['buttons']]) + i:
                        return self._click_form_button(form, btn)
            
            # Find in standalone buttons
            for btn in self.current_buttons:
                if btn['number'] == button_num:
                    return self._click_standalone_button(btn)
            
            console.print(f"[red]Button #{button_num} not found[/red]")
            return False
            
        except ValueError:
            console.print("[red]Please provide a valid button number[/red]")
            return False

    def _click_form_button(self, form, button):
        """Handle clicking a form button"""
        if button['type'] == 'submit':
            console.print(f"[yellow]Submitting form with '{button['text']}' button...[/yellow]")
            return self.submit_form(self.current_forms.index(form) + 1, button)
        else:
            console.print(f"[blue]Clicked '{button['text']}' button[/blue]")
            # For non-submit buttons, we can't do much in CLI mode
            console.print("[dim]JavaScript buttons are not fully interactive in CLI mode[/dim]")
            return True

    def _click_standalone_button(self, button):
        """Handle clicking a standalone button"""
        if button['type'] == 'link':
            console.print(f"[blue]Following link: {button['text']}[/blue]")
            return button['action']  # Return URL to navigate to
        else:
            console.print(f"[blue]Clicked '{button['text']}' button[/blue]")
            console.print("[dim]JavaScript buttons are not fully interactive in CLI mode[/dim]")
            return True

    def fill_form(self, form_number):
        """Interactive form filling"""
        try:
            form_num = int(form_number)
            if form_num < 1 or form_num > len(self.current_forms):
                console.print(f"[red]Form #{form_num} not found[/red]")
                return False
            
            form = self.current_forms[form_num - 1]
            console.print(f"\n[bold blue]📝 Filling Form #{form_num}[/bold blue]")
            
            form_data = {}
            
            for inp in form['inputs']:
                value = self._get_input_value(inp)
                if value is not None:
                    form_data[inp['name']] = value
            
            # Store filled data for later submission
            form['filled_data'] = form_data
            
            console.print("\n[green]✅ Form filled successfully![/green]")
            console.print(f"Type [cyan]'submit {form_num}'[/cyan] to submit this form")
            
            return True
            
        except ValueError:
            console.print("[red]Please provide a valid form number[/red]")
            return False

    def _get_input_value(self, inp):
        """Get value for a specific input field"""
        field_name = inp['name'] or f"{inp['type']} field"
        
        if inp['type'] == 'password':
            prompt_text = f"🔒 {field_name}"
            if inp['placeholder']:
                prompt_text += f" ({inp['placeholder']})"
            return Prompt.ask(prompt_text, password=True)
        
        elif inp['type'] == 'email':
            prompt_text = f"📧 {field_name}"
            if inp['placeholder']:
                prompt_text += f" ({inp['placeholder']})"
            while True:
                value = Prompt.ask(prompt_text, default=inp['value'])
                if self._validate_email(value):
                    return value
                console.print("[red]Please enter a valid email address[/red]")
        
        elif inp['type'] == 'url':
            prompt_text = f"🌐 {field_name}"
            if inp['placeholder']:
                prompt_text += f" ({inp['placeholder']})"
            return Prompt.ask(prompt_text, default=inp['value'])
        
        elif inp['type'] == 'number':
            prompt_text = f"🔢 {field_name}"
            if inp['placeholder']:
                prompt_text += f" ({inp['placeholder']})"
            while True:
                value = Prompt.ask(prompt_text, default=inp['value'])
                try:
                    float(value)
                    return value
                except ValueError:
                    console.print("[red]Please enter a valid number[/red]")
        
        elif inp['type'] == 'checkbox':
            prompt_text = f"☑️ {field_name}"
            return "on" if Confirm.ask(prompt_text) else ""
        
        elif inp['type'] == 'radio':
            console.print(f"[yellow]Radio button '{field_name}' - select to enable[/yellow]")
            return "on" if Confirm.ask(f"Select {field_name}?") else ""
        
        elif inp['element'] == 'textarea':
            prompt_text = f"📝 {field_name}"
            if inp['placeholder']:
                prompt_text += f" ({inp['placeholder']})"
            console.print(f"{prompt_text} (press Enter twice to finish):")
            lines = []
            while True:
                line = input()
                if line == "" and lines and lines[-1] == "":
                    break
                lines.append(line)
            return '\n'.join(lines[:-1])  # Remove the last empty line
        
        else:  # text, search, tel, etc.
            icon = "🔍" if inp['type'] == 'search' else "📝"
            prompt_text = f"{icon} {field_name}"
            if inp['placeholder']:
                prompt_text += f" ({inp['placeholder']})"
            
            value = Prompt.ask(prompt_text, default=inp['value'])
            
            # Validate required fields
            if inp['required'] and not value.strip():
                console.print("[red]This field is required[/red]")
                return self._get_input_value(inp)  # Retry
            
            return value

    def _validate_email(self, email):
        """Simple email validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def submit_form(self, form_number, button=None):
        """Submit a form"""
        try:
            form_num = int(form_number)
            if form_num < 1 or form_num > len(self.current_forms):
                console.print(f"[red]Form #{form_num} not found[/red]")
                return False
            
            form = self.current_forms[form_num - 1]
            
            # Check if form has been filled
            if 'filled_data' not in form:
                console.print(f"[yellow]Form #{form_num} hasn't been filled yet.[/yellow]")
                if Confirm.ask("Fill it now?"):
                    if not self.fill_form(form_num):
                        return False
                else:
                    return False
            
            form_data = form['filled_data']
            
            # Add button data if provided
            if button and button['name']:
                form_data[button['name']] = button['value']
            
            console.print(f"\n[bold blue]🚀 Submitting Form #{form_num}[/bold blue]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("Submitting form...", total=None)
                
                try:
                    if form['method'] == 'POST':
                        response = requests.post(form['action'], data=form_data, timeout=30)
                    else:
                        response = requests.get(form['action'], params=form_data, timeout=30)
                    
                    if response.status_code == 200:
                        console.print("[green]✅ Form submitted successfully![/green]")
                        console.print(f"[dim]Response: {response.status_code} {response.reason}[/dim]")
                        
                        # Return new URL if redirected
                        if response.url != form['action']:
                            console.print(f"[blue]Redirected to: {response.url}[/blue]")
                            return response.url
                        
                        return True
                    else:
                        console.print(f"[red]Form submission failed: {response.status_code} {response.reason}[/red]")
                        return False
                        
                except requests.RequestException as e:
                    console.print(f"[red]Error submitting form: {str(e)}[/red]")
                    return False
            
        except ValueError:
            console.print("[red]Please provide a valid form number[/red]")
            return False