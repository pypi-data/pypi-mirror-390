"""
CSS Layout Calculator - Calculate proper text flow for Grid and Flexbox layouts
Critical for CLI browsers to maintain correct reading order in markdown
"""

from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup, Tag
import re
import json

class CSSLayoutCalculator:
    """Calculates text flow order for modern CSS layouts (Grid, Flexbox)"""
    
    def __init__(self):
        self.layout_cache = {}
        self.reading_order = {}
        
    def calculate_layout_order(self, soup: BeautifulSoup, css_rules: Dict = None) -> Dict[str, List[str]]:
        """
        Calculate proper text reading order for CSS Grid and Flexbox layouts
        
        Args:
            soup: BeautifulSoup parsed HTML
            css_rules: Parsed CSS rules containing layout information
            
        Returns:
            Dictionary mapping container IDs to ordered element lists
        """
        try:
            if not css_rules:
                return {}
                
            layout_containers = {}
            
            # 1. Find Grid containers
            grid_containers = self._find_grid_containers(soup, css_rules)
            for container in grid_containers:
                order = self._calculate_grid_order(container, css_rules)
                if order:
                    container_id = self._get_element_identifier(container)
                    layout_containers[f"grid-{container_id}"] = order
            
            # 2. Find Flexbox containers
            flex_containers = self._find_flex_containers(soup, css_rules)
            for container in flex_containers:
                order = self._calculate_flex_order(container, css_rules)
                if order:
                    container_id = self._get_element_identifier(container)
                    layout_containers[f"flex-{container_id}"] = order
            
            # 3. Calculate CSS order property effects
            ordered_elements = self._calculate_css_order_effects(soup, css_rules)
            if ordered_elements:
                layout_containers["css-order"] = ordered_elements
            
            return layout_containers
            
        except Exception as e:
            return {"error": f"Layout calculation error: {str(e)}"}
    
    def apply_layout_order_to_content(self, soup: BeautifulSoup, layout_orders: Dict[str, List[str]]) -> BeautifulSoup:
        """Apply calculated layout order to HTML for proper markdown rendering"""
        try:
            if not layout_orders:
                return soup
            
            # Create a copy to modify
            modified_soup = BeautifulSoup(str(soup), 'html.parser')
            
            for container_type, element_order in layout_orders.items():
                if container_type.startswith("grid-"):
                    self._reorder_grid_elements(modified_soup, container_type, element_order)
                elif container_type.startswith("flex-"):
                    self._reorder_flex_elements(modified_soup, container_type, element_order)
                elif container_type == "css-order":
                    self._apply_css_order_reordering(modified_soup, element_order)
            
            return modified_soup
            
        except Exception as e:
            # Return original if reordering fails
            return soup
    
    def _find_grid_containers(self, soup: BeautifulSoup, css_rules: Dict) -> List[Tag]:
        """Find elements using CSS Grid layout"""
        try:
            grid_containers = []
            
            for selector, rules in css_rules.items():
                if 'display' in rules and rules['display'] in ['grid', 'inline-grid']:
                    elements = self._select_elements(soup, selector)
                    grid_containers.extend(elements)
            
            return grid_containers
            
        except Exception:
            return []
    
    def _find_flex_containers(self, soup: BeautifulSoup, css_rules: Dict) -> List[Tag]:
        """Find elements using CSS Flexbox layout"""
        try:
            flex_containers = []
            
            for selector, rules in css_rules.items():
                if 'display' in rules and rules['display'] in ['flex', 'inline-flex']:
                    elements = self._select_elements(soup, selector)
                    flex_containers.extend(elements)
            
            return flex_containers
            
        except Exception:
            return []
    
    def _calculate_grid_order(self, container: Tag, css_rules: Dict) -> List[str]:
        """Calculate reading order for CSS Grid items"""
        try:
            grid_items = []
            
            # Get all direct children (grid items)
            for child in container.find_all(recursive=False):
                if child.name:
                    item_info = {
                        'element': child,
                        'id': self._get_element_identifier(child),
                        'text': child.get_text(strip=True)[:50],  # First 50 chars
                        'grid_area': self._get_grid_item_properties(child, css_rules),
                        'order': self._get_css_order(child, css_rules)
                    }
                    grid_items.append(item_info)
            
            # Sort by grid position and CSS order
            sorted_items = self._sort_grid_items(grid_items)
            
            # Return text content in proper order
            return [f"{item['id']}: {item['text']}" for item in sorted_items if item['text']]
            
        except Exception as e:
            return [f"Grid calculation error: {str(e)}"]
    
    def _calculate_flex_order(self, container: Tag, css_rules: Dict) -> List[str]:
        """Calculate reading order for Flexbox items"""
        try:
            flex_items = []
            
            # Get container direction
            flex_direction = self._get_flex_direction(container, css_rules)
            flex_wrap = self._get_flex_wrap(container, css_rules)
            
            # Get all direct children (flex items)
            for child in container.find_all(recursive=False):
                if child.name:
                    item_info = {
                        'element': child,
                        'id': self._get_element_identifier(child),
                        'text': child.get_text(strip=True)[:50],
                        'order': self._get_css_order(child, css_rules),
                        'flex_grow': self._get_flex_grow(child, css_rules),
                        'flex_basis': self._get_flex_basis(child, css_rules)
                    }
                    flex_items.append(item_info)
            
            # Sort by CSS order first, then by document order
            sorted_items = sorted(flex_items, key=lambda x: (x['order'], flex_items.index(x)))
            
            # Reverse if flex-direction is row-reverse or column-reverse
            if 'reverse' in flex_direction:
                sorted_items.reverse()
            
            return [f"{item['id']}: {item['text']}" for item in sorted_items if item['text']]
            
        except Exception as e:
            return [f"Flex calculation error: {str(e)}"]
    
    def _calculate_css_order_effects(self, soup: BeautifulSoup, css_rules: Dict) -> Dict[str, int]:
        """Find elements with CSS order property"""
        try:
            ordered_elements = {}
            
            for selector, rules in css_rules.items():
                if 'order' in rules:
                    try:
                        order_value = int(rules['order'])
                        elements = self._select_elements(soup, selector)
                        
                        for element in elements:
                            element_id = self._get_element_identifier(element)
                            ordered_elements[element_id] = order_value
                    except ValueError:
                        continue
            
            return ordered_elements
            
        except Exception:
            return {}
    
    def _get_grid_item_properties(self, element: Tag, css_rules: Dict) -> Dict[str, str]:
        """Get grid-specific properties for an element"""
        try:
            properties = {}
            
            element_selector = self._create_element_selector(element)
            
            for selector, rules in css_rules.items():
                if self._selector_could_match_element(selector, element):
                    # Grid item properties
                    for prop in ['grid-column', 'grid-row', 'grid-area', 'grid-column-start', 'grid-column-end', 'grid-row-start', 'grid-row-end']:
                        if prop in rules:
                            properties[prop] = rules[prop]
            
            return properties
            
        except Exception:
            return {}
    
    def _get_flex_direction(self, container: Tag, css_rules: Dict) -> str:
        """Get flex-direction for a flex container"""
        try:
            for selector, rules in css_rules.items():
                if self._selector_could_match_element(selector, container):
                    if 'flex-direction' in rules:
                        return rules['flex-direction']
            
            return 'row'  # Default
            
        except Exception:
            return 'row'
    
    def _get_flex_wrap(self, container: Tag, css_rules: Dict) -> str:
        """Get flex-wrap for a flex container"""
        try:
            for selector, rules in css_rules.items():
                if self._selector_could_match_element(selector, container):
                    if 'flex-wrap' in rules:
                        return rules['flex-wrap']
            
            return 'nowrap'  # Default
            
        except Exception:
            return 'nowrap'
    
    def _get_css_order(self, element: Tag, css_rules: Dict) -> int:
        """Get CSS order value for an element"""
        try:
            for selector, rules in css_rules.items():
                if self._selector_could_match_element(selector, element):
                    if 'order' in rules:
                        return int(rules['order'])
            
            return 0  # Default order
            
        except Exception:
            return 0
    
    def _get_flex_grow(self, element: Tag, css_rules: Dict) -> float:
        """Get flex-grow value for a flex item"""
        try:
            for selector, rules in css_rules.items():
                if self._selector_could_match_element(selector, element):
                    if 'flex-grow' in rules:
                        return float(rules['flex-grow'])
            
            return 0.0  # Default
            
        except Exception:
            return 0.0
    
    def _get_flex_basis(self, element: Tag, css_rules: Dict) -> str:
        """Get flex-basis value for a flex item"""
        try:
            for selector, rules in css_rules.items():
                if self._selector_could_match_element(selector, element):
                    if 'flex-basis' in rules:
                        return rules['flex-basis']
            
            return 'auto'  # Default
            
        except Exception:
            return 'auto'
    
    def _sort_grid_items(self, grid_items: List[Dict]) -> List[Dict]:
        """Sort grid items by their grid position"""
        try:
            # Simple sorting by CSS order first, then document order
            return sorted(grid_items, key=lambda x: (x['order'], grid_items.index(x)))
            
        except Exception:
            return grid_items
    
    def _select_elements(self, soup: BeautifulSoup, selector: str) -> List[Tag]:
        """Select elements based on CSS selector"""
        try:
            selector = selector.strip()
            
            if not selector:
                return []
            
            # Handle basic selectors
            if selector.startswith('#'):
                element = soup.find(id=selector[1:])
                return [element] if element else []
            
            elif selector.startswith('.'):
                return soup.find_all(class_=selector[1:])
            
            elif ':' not in selector and '[' not in selector:
                return soup.find_all(selector)
            
            else:
                # Try CSS select if available
                try:
                    return soup.select(selector)
                except:
                    # Fallback to tag name
                    tag_match = re.match(r'^([a-zA-Z][a-zA-Z0-9]*)', selector)
                    if tag_match:
                        return soup.find_all(tag_match.group(1))
            
            return []
            
        except Exception:
            return []
    
    def _get_element_identifier(self, element: Tag) -> str:
        """Create unique identifier for an element"""
        try:
            if element.get('id'):
                return f"#{element.get('id')}"
            
            if element.get('class'):
                classes = element.get('class')
                if isinstance(classes, list):
                    return f".{'.'.join(classes[:2])}"
                return f".{classes}"
            
            # Use tag name and position
            parent = element.parent
            if parent:
                siblings = [child for child in parent.children if hasattr(child, 'name') and child.name == element.name]
                index = siblings.index(element) if element in siblings else 0
                return f"{element.name}[{index}]"
            
            return element.name
            
        except Exception:
            return f"{element.name}"
    
    def _create_element_selector(self, element: Tag) -> str:
        """Create CSS selector for an element"""
        try:
            selector_parts = [element.name]
            
            if element.get('id'):
                selector_parts.append(f"#{element.get('id')}")
            
            if element.get('class'):
                classes = element.get('class')
                if isinstance(classes, list):
                    selector_parts.extend([f".{cls}" for cls in classes])
                else:
                    selector_parts.append(f".{classes}")
            
            return "".join(selector_parts)
            
        except Exception:
            return element.name
    
    def _selector_could_match_element(self, selector: str, element: Tag) -> bool:
        """Check if a CSS selector could match an element (simplified)"""
        try:
            # Very basic matching - this could be enhanced
            if selector == element.name:
                return True
            
            if selector.startswith('#') and element.get('id') == selector[1:]:
                return True
            
            if selector.startswith('.'):
                class_name = selector[1:]
                element_classes = element.get('class', [])
                if isinstance(element_classes, str):
                    element_classes = [element_classes]
                return class_name in element_classes
            
            # For complex selectors, assume they could match
            if any(char in selector for char in [' ', '>', '+', '~', ':', '[']):
                return True
            
            return False
            
        except Exception:
            return False
    
    def _reorder_grid_elements(self, soup: BeautifulSoup, container_id: str, element_order: List[str]):
        """Reorder grid elements in HTML for proper text flow"""
        try:
            # This is a placeholder for complex grid reordering
            # In practice, would need to identify the container and reorder its children
            pass
            
        except Exception:
            pass
    
    def _reorder_flex_elements(self, soup: BeautifulSoup, container_id: str, element_order: List[str]):
        """Reorder flex elements in HTML for proper text flow"""
        try:
            # This is a placeholder for complex flex reordering
            # In practice, would need to identify the container and reorder its children
            pass
            
        except Exception:
            pass
    
    def _apply_css_order_reordering(self, soup: BeautifulSoup, ordered_elements: Dict[str, int]):
        """Apply CSS order property effects to HTML structure"""
        try:
            # This is a placeholder for CSS order reordering
            # Would need to find elements and reorder them based on order values
            pass
            
        except Exception:
            pass
    
    def get_layout_summary(self, layout_orders: Dict[str, List[str]]) -> str:
        """Generate a summary of layout calculations for debugging"""
        try:
            if not layout_orders:
                return "No layout calculations performed"
            
            summary_parts = []
            
            for container_type, elements in layout_orders.items():
                summary_parts.append(f"{container_type.title()} Layout:")
                for i, element in enumerate(elements[:5], 1):  # Show first 5
                    summary_parts.append(f"  {i}. {element}")
                
                if len(elements) > 5:
                    summary_parts.append(f"  ... and {len(elements) - 5} more elements")
                
                summary_parts.append("")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            return f"Layout summary error: {str(e)}"