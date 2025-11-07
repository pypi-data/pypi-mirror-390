"""
Advanced Layout Engine - CSS Grid and Flexbox visual representation
Handles complex layouts with performance optimization
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup, Tag
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
import json

class LayoutEngine:
    """Advanced CSS layout engine for Grid and Flexbox rendering"""
    
    def __init__(self):
        self.console = Console()
        self.grid_cache = {}
        self.flexbox_cache = {}
        
    def parse_css_layout(self, soup: BeautifulSoup, css_rules: Dict) -> Dict[str, Any]:
        """Parse CSS layout properties and create visual representations"""
        layout_info = {
            'grids': [],
            'flexboxes': [],
            'complex_layouts': [],
            'responsive_breakpoints': []
        }
        
        # Find elements with CSS Grid
        grid_elements = self._find_grid_elements(soup, css_rules)
        for element in grid_elements:
            grid_layout = self._analyze_grid_layout(element, css_rules)
            if grid_layout:
                layout_info['grids'].append(grid_layout)
        
        # Find elements with Flexbox
        flex_elements = self._find_flex_elements(soup, css_rules)
        for element in flex_elements:
            flex_layout = self._analyze_flex_layout(element, css_rules)
            if flex_layout:
                layout_info['flexboxes'].append(flex_layout)
        
        # Detect responsive layouts
        responsive_layouts = self._detect_responsive_layouts(css_rules)
        layout_info['responsive_breakpoints'] = responsive_layouts
        
        return layout_info
    
    def _find_grid_elements(self, soup: BeautifulSoup, css_rules: Dict) -> List[Tag]:
        """Find elements using CSS Grid"""
        grid_elements = []
        
        # Check for display: grid in CSS rules
        for selector, rules in css_rules.items():
            if isinstance(rules, dict) and rules.get('display') == 'grid':
                elements = soup.select(selector)
                grid_elements.extend(elements)
        
        # Check for inline grid styles
        for element in soup.find_all(attrs={'style': True}):
            style = element.get('style', '')
            if 'display:grid' in style.replace(' ', '') or 'display: grid' in style:
                grid_elements.append(element)
        
        return grid_elements
    
    def _find_flex_elements(self, soup: BeautifulSoup, css_rules: Dict) -> List[Tag]:
        """Find elements using Flexbox"""
        flex_elements = []
        
        # Check for display: flex in CSS rules
        for selector, rules in css_rules.items():
            if isinstance(rules, dict) and rules.get('display') in ['flex', 'inline-flex']:
                elements = soup.select(selector)
                flex_elements.extend(elements)
        
        # Check for inline flex styles
        for element in soup.find_all(attrs={'style': True}):
            style = element.get('style', '')
            if any(display in style.replace(' ', '') for display in ['display:flex', 'display:inline-flex']):
                flex_elements.append(element)
        
        return flex_elements
    
    def _analyze_grid_layout(self, element: Tag, css_rules: Dict) -> Optional[Dict]:
        """Analyze CSS Grid properties and create visual representation"""
        grid_props = self._extract_grid_properties(element, css_rules)
        if not grid_props:
            return None
        
        # Create grid visualization
        grid_visual = self._create_grid_visualization(element, grid_props)
        
        return {
            'element': str(element.name) if element.name else 'div',
            'id': element.get('id', ''),
            'classes': element.get('class', []),
            'properties': grid_props,
            'visual': grid_visual,
            'children': self._analyze_grid_children(element, grid_props)
        }
    
    def _analyze_flex_layout(self, element: Tag, css_rules: Dict) -> Optional[Dict]:
        """Analyze Flexbox properties and create visual representation"""
        flex_props = self._extract_flex_properties(element, css_rules)
        if not flex_props:
            return None
        
        # Create flexbox visualization
        flex_visual = self._create_flex_visualization(element, flex_props)
        
        return {
            'element': str(element.name) if element.name else 'div',
            'id': element.get('id', ''),
            'classes': element.get('class', []),
            'properties': flex_props,
            'visual': flex_visual,
            'children': self._analyze_flex_children(element, flex_props)
        }
    
    def _extract_grid_properties(self, element: Tag, css_rules: Dict) -> Dict:
        """Extract CSS Grid properties from element and CSS rules"""
        props = {}
        
        # Get properties from CSS rules
        for selector, rules in css_rules.items():
            if isinstance(rules, dict) and element.name:
                try:
                    if element.select(selector) or self._matches_selector(element, selector):
                        for prop, value in rules.items():
                            if prop.startswith('grid-'):
                                props[prop] = value
                except:
                    continue
        
        # Get inline style properties
        style = element.get('style', '')
        if style:
            style_props = self._parse_inline_styles(style)
            for prop, value in style_props.items():
                if prop.startswith('grid-'):
                    props[prop] = value
        
        # Set defaults for common grid properties
        grid_defaults = {
            'grid-template-columns': props.get('grid-template-columns', 'auto'),
            'grid-template-rows': props.get('grid-template-rows', 'auto'),
            'grid-gap': props.get('grid-gap', '0'),
            'grid-auto-flow': props.get('grid-auto-flow', 'row'),
            'justify-content': props.get('justify-content', 'start'),
            'align-content': props.get('align-content', 'start')
        }
        
        props.update(grid_defaults)
        return props
    
    def _extract_flex_properties(self, element: Tag, css_rules: Dict) -> Dict:
        """Extract Flexbox properties from element and CSS rules"""
        props = {}
        
        # Get properties from CSS rules
        for selector, rules in css_rules.items():
            if isinstance(rules, dict) and element.name:
                try:
                    if element.select(selector) or self._matches_selector(element, selector):
                        flex_props = ['flex-direction', 'flex-wrap', 'justify-content', 'align-items', 'align-content', 'flex', 'flex-grow', 'flex-shrink', 'flex-basis']
                        for prop in flex_props:
                            if prop in rules:
                                props[prop] = rules[prop]
                except:
                    continue
        
        # Get inline style properties
        style = element.get('style', '')
        if style:
            style_props = self._parse_inline_styles(style)
            for prop, value in style_props.items():
                if 'flex' in prop or prop in ['justify-content', 'align-items', 'align-content']:
                    props[prop] = value
        
        # Set defaults for common flex properties
        flex_defaults = {
            'flex-direction': props.get('flex-direction', 'row'),
            'flex-wrap': props.get('flex-wrap', 'nowrap'),
            'justify-content': props.get('justify-content', 'flex-start'),
            'align-items': props.get('align-items', 'stretch'),
            'align-content': props.get('align-content', 'stretch')
        }
        
        props.update(flex_defaults)
        return props
    
    def _create_grid_visualization(self, element: Tag, props: Dict) -> str:
        """Create ASCII visualization of CSS Grid layout"""
        cols = self._parse_grid_template(props.get('grid-template-columns', 'auto'))
        rows = self._parse_grid_template(props.get('grid-template-rows', 'auto'))
        
        # Create grid representation
        grid_lines = []
        col_count = len(cols) if cols else 3
        row_count = len(rows) if rows else 2
        
        # Top border
        grid_lines.append('┌' + '─' * (col_count * 8 - 1) + '┐')
        
        # Grid cells
        for row in range(row_count):
            cell_line = '│'
            for col in range(col_count):
                cell_content = f' [{row+1},{col+1}] '
                cell_line += cell_content + '│'
            grid_lines.append(cell_line)
            
            if row < row_count - 1:
                grid_lines.append('├' + ('─' * 7 + '┼') * (col_count - 1) + '─' * 7 + '┤')
        
        # Bottom border
        grid_lines.append('└' + '─' * (col_count * 8 - 1) + '┘')
        
        return '\n'.join(grid_lines)
    
    def _create_flex_visualization(self, element: Tag, props: Dict) -> str:
        """Create ASCII visualization of Flexbox layout"""
        direction = props.get('flex-direction', 'row')
        wrap = props.get('flex-wrap', 'nowrap')
        justify = props.get('justify-content', 'flex-start')
        align = props.get('align-items', 'stretch')
        
        children = element.find_all(recursive=False) if element else []
        child_count = min(len(children), 6) if children else 3
        
        if direction in ['row', 'row-reverse']:
            # Horizontal flexbox
            flex_lines = []
            
            # Top border
            flex_lines.append('┌' + ('─' * 10 + '┬') * (child_count - 1) + '─' * 10 + '┐')
            
            # Flex items
            item_line = '│'
            for i in range(child_count):
                item_content = f'  Item {i+1}  '
                item_line += item_content + '│'
            flex_lines.append(item_line)
            
            # Bottom border
            flex_lines.append('└' + ('─' * 10 + '┴') * (child_count - 1) + '─' * 10 + '┘')
            
            # Add direction indicator
            if direction == 'row-reverse':
                flex_lines.append('Direction: ← (row-reverse)')
            else:
                flex_lines.append('Direction: → (row)')
        
        else:
            # Vertical flexbox
            flex_lines = []
            
            for i in range(child_count):
                flex_lines.append('┌──────────┐')
                flex_lines.append(f'│  Item {i+1}  │')
                flex_lines.append('└──────────┘')
                if i < child_count - 1:
                    flex_lines.append('     ↓')
            
            # Add direction indicator
            if direction == 'column-reverse':
                flex_lines.append('Direction: ↑ (column-reverse)')
            else:
                flex_lines.append('Direction: ↓ (column)')
        
        return '\n'.join(flex_lines)
    
    def _analyze_grid_children(self, element: Tag, grid_props: Dict) -> List[Dict]:
        """Analyze grid child elements and their placement"""
        children = []
        if not element:
            return children
        
        for i, child in enumerate(element.find_all(recursive=False)):
            child_props = self._extract_grid_child_properties(child)
            children.append({
                'index': i + 1,
                'element': str(child.name) if child.name else 'div',
                'id': child.get('id', ''),
                'classes': child.get('class', []),
                'grid_area': child_props.get('grid-area', f'auto / auto / auto / auto'),
                'properties': child_props
            })
        
        return children
    
    def _analyze_flex_children(self, element: Tag, flex_props: Dict) -> List[Dict]:
        """Analyze flex child elements and their properties"""
        children = []
        if not element:
            return children
        
        for i, child in enumerate(element.find_all(recursive=False)):
            child_props = self._extract_flex_child_properties(child)
            children.append({
                'index': i + 1,
                'element': str(child.name) if child.name else 'div',
                'id': child.get('id', ''),
                'classes': child.get('class', []),
                'flex': child_props.get('flex', '0 1 auto'),
                'properties': child_props
            })
        
        return children
    
    def _extract_grid_child_properties(self, child: Tag) -> Dict:
        """Extract grid-specific properties from child element"""
        props = {}
        style = child.get('style', '')
        
        if style:
            style_props = self._parse_inline_styles(style)
            grid_child_props = ['grid-column', 'grid-row', 'grid-area', 'justify-self', 'align-self']
            for prop in grid_child_props:
                if prop in style_props:
                    props[prop] = style_props[prop]
        
        return props
    
    def _extract_flex_child_properties(self, child: Tag) -> Dict:
        """Extract flex-specific properties from child element"""
        props = {}
        style = child.get('style', '')
        
        if style:
            style_props = self._parse_inline_styles(style)
            flex_child_props = ['flex', 'flex-grow', 'flex-shrink', 'flex-basis', 'align-self', 'order']
            for prop in flex_child_props:
                if prop in style_props:
                    props[prop] = style_props[prop]
        
        return props
    
    def _parse_grid_template(self, template: str) -> List[str]:
        """Parse grid-template-columns/rows values"""
        if not template or template == 'auto':
            return ['auto']
        
        # Handle common grid templates
        if 'repeat' in template:
            # Parse repeat() function
            match = re.search(r'repeat\((\d+),\s*(.+?)\)', template)
            if match:
                count = int(match.group(1))
                value = match.group(2).strip()
                return [value] * count
        
        # Split by spaces (simplified parsing)
        return [col.strip() for col in template.split() if col.strip()]
    
    def _parse_inline_styles(self, style: str) -> Dict:
        """Parse inline CSS styles into dictionary"""
        props = {}
        declarations = style.split(';')
        
        for declaration in declarations:
            if ':' in declaration:
                prop, value = declaration.split(':', 1)
                props[prop.strip()] = value.strip()
        
        return props
    
    def _matches_selector(self, element: Tag, selector: str) -> bool:
        """Check if element matches CSS selector (simplified)"""
        try:
            # Very basic selector matching
            if selector.startswith('.'):
                class_name = selector[1:]
                return class_name in element.get('class', [])
            elif selector.startswith('#'):
                id_name = selector[1:]
                return element.get('id') == id_name
            else:
                return element.name == selector
        except:
            return False
    
    def _detect_responsive_layouts(self, css_rules: Dict) -> List[Dict]:
        """Detect responsive design breakpoints and layouts"""
        breakpoints = []
        
        for selector, rules in css_rules.items():
            if isinstance(rules, dict):
                # Look for media query indicators
                if any(prop.startswith('@media') for prop in rules.keys()):
                    breakpoints.append({
                        'selector': selector,
                        'breakpoint': 'detected',
                        'properties': rules
                    })
        
        # Common responsive breakpoints
        common_breakpoints = [
            {'name': 'Mobile', 'min_width': 0, 'max_width': 767},
            {'name': 'Tablet', 'min_width': 768, 'max_width': 1023},
            {'name': 'Desktop', 'min_width': 1024, 'max_width': 1439},
            {'name': 'Large Desktop', 'min_width': 1440, 'max_width': None}
        ]
        
        return common_breakpoints
    
    def render_layout_summary(self, layout_info: Dict) -> None:
        """Render a comprehensive layout summary to console"""
        console = Console()
        
        # Grid Layouts
        if layout_info['grids']:
            console.print("\n[bold cyan]CSS Grid Layouts Detected:[/bold cyan]")
            
            for i, grid in enumerate(layout_info['grids'], 1):
                console.print(f"\n[yellow]Grid {i}:[/yellow] {grid['element']}")
                if grid['id']:
                    console.print(f"  ID: #{grid['id']}")
                if grid['classes']:
                    console.print(f"  Classes: .{' .'.join(grid['classes'])}")
                
                # Grid properties
                props_table = Table(show_header=True, header_style="bold blue")
                props_table.add_column("Property", style="cyan")
                props_table.add_column("Value", style="green")
                
                for prop, value in grid['properties'].items():
                    props_table.add_row(prop, str(value))
                
                console.print(props_table)
                
                # Visual representation
                console.print("\n[bold]Visual Layout:[/bold]")
                console.print(Panel(grid['visual'], title="Grid Structure"))
                
                # Children
                if grid['children']:
                    console.print(f"\n[bold]Grid Items ({len(grid['children'])}):[/bold]")
                    for child in grid['children']:
                        console.print(f"  {child['index']}. {child['element']} - Area: {child['grid_area']}")
        
        # Flexbox Layouts
        if layout_info['flexboxes']:
            console.print("\n[bold cyan]Flexbox Layouts Detected:[/bold cyan]")
            
            for i, flex in enumerate(layout_info['flexboxes'], 1):
                console.print(f"\n[yellow]Flexbox {i}:[/yellow] {flex['element']}")
                if flex['id']:
                    console.print(f"  ID: #{flex['id']}")
                if flex['classes']:
                    console.print(f"  Classes: .{' .'.join(flex['classes'])}")
                
                # Flex properties
                props_table = Table(show_header=True, header_style="bold blue")
                props_table.add_column("Property", style="cyan")
                props_table.add_column("Value", style="green")
                
                for prop, value in flex['properties'].items():
                    props_table.add_row(prop, str(value))
                
                console.print(props_table)
                
                # Visual representation
                console.print("\n[bold]Visual Layout:[/bold]")
                console.print(Panel(flex['visual'], title="Flex Structure"))
                
                # Children
                if flex['children']:
                    console.print(f"\n[bold]Flex Items ({len(flex['children'])}):[/bold]")
                    for child in flex['children']:
                        console.print(f"  {child['index']}. {child['element']} - Flex: {child['flex']}")
        
        # Responsive Breakpoints
        if layout_info['responsive_breakpoints']:
            console.print("\n[bold cyan]Responsive Design Breakpoints:[/bold cyan]")
            
            breakpoints_table = Table(show_header=True, header_style="bold blue")
            breakpoints_table.add_column("Device", style="cyan")
            breakpoints_table.add_column("Min Width", style="green")
            breakpoints_table.add_column("Max Width", style="green")
            
            for bp in layout_info['responsive_breakpoints']:
                min_w = f"{bp['min_width']}px" if bp['min_width'] else "0px"
                max_w = f"{bp['max_width']}px" if bp['max_width'] else "∞"
                breakpoints_table.add_row(bp['name'], min_w, max_w)
            
            console.print(breakpoints_table)