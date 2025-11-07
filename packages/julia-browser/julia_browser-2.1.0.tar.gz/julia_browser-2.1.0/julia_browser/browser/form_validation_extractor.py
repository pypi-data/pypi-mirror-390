#!/usr/bin/env python3
"""
Form Validation API Text Extractor
Extracts client-side error messages and validation feedback
"""

import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag


class FormValidationExtractor:
    """Extracts form validation messages and client-side feedback"""
    
    def __init__(self):
        self.validation_attributes = [
            'required', 'pattern', 'min', 'max', 'minlength', 'maxlength',
            'step', 'type'
        ]
        
        self.validation_message_selectors = [
            '.error', '.invalid', '.validation-error', '.field-error',
            '.form-error', '.error-message', '.invalid-feedback',
            '[data-error]', '[data-validation]', '.help-block'
        ]
        
        self.input_types_validation = {
            'email': 'Valid email address required',
            'url': 'Valid URL required',
            'number': 'Numeric value required',
            'tel': 'Valid phone number required',
            'date': 'Valid date required',
            'time': 'Valid time required',
            'datetime-local': 'Valid date and time required',
            'month': 'Valid month required',
            'week': 'Valid week required',
            'color': 'Valid color required'
        }
    
    def extract_validation_content(self, soup: BeautifulSoup, js_context: Dict) -> str:
        """Extract form validation messages and requirements"""
        try:
            validation_content = []
            
            # Extract HTML5 validation requirements
            html5_validation = self._extract_html5_validation(soup)
            validation_content.extend(html5_validation)
            
            # Extract visible validation messages
            visible_errors = self._extract_visible_validation_messages(soup)
            validation_content.extend(visible_errors)
            
            # Extract custom validation attributes
            custom_validation = self._extract_custom_validation(soup)
            validation_content.extend(custom_validation)
            
            # Extract JavaScript validation patterns
            js_validation = self._extract_js_validation_from_context(js_context)
            validation_content.extend(js_validation)
            
            # Extract constraint validation API messages
            constraint_validation = self._extract_constraint_validation(soup)
            validation_content.extend(constraint_validation)
            
            if validation_content:
                return "\n## ✅ Form Validation Requirements\n" + "\n".join(validation_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- Form validation extraction error: {str(e)} -->\n"
    
    def _extract_html5_validation(self, soup: BeautifulSoup) -> List[str]:
        """Extract HTML5 built-in validation requirements"""
        validation_msgs = []
        
        # Required fields
        for element in soup.find_all(attrs={"required": True}):
            if hasattr(element, 'get') and hasattr(element, 'name'):
                field_name = self._get_field_name(element)
                element_type = element.get('type', element.name)
                if hasattr(element_type, 'title'):
                    field_type = element_type.title()
                else:
                    field_type = str(element_type).title() if element_type else 'Field'
                validation_msgs.append(f"⚠️ Required: {field_name} ({field_type})")
        
        # Pattern validation
        for element in soup.find_all(attrs={"pattern": True}):
            pattern = element.get('pattern', '').strip()
            field_name = self._get_field_name(element)
            if pattern:
                validation_msgs.append(f"🔤 Pattern Required ({field_name}): {pattern}")
        
        # Length constraints
        for element in soup.find_all(attrs={"minlength": True}):
            minlength = element.get('minlength')
            field_name = self._get_field_name(element)
            validation_msgs.append(f"📏 Minimum Length ({field_name}): {minlength} characters")
        
        for element in soup.find_all(attrs={"maxlength": True}):
            maxlength = element.get('maxlength')
            field_name = self._get_field_name(element)
            validation_msgs.append(f"📏 Maximum Length ({field_name}): {maxlength} characters")
        
        # Numeric constraints
        for element in soup.find_all(attrs={"min": True}):
            min_val = element.get('min')
            field_name = self._get_field_name(element)
            validation_msgs.append(f"🔢 Minimum Value ({field_name}): {min_val}")
        
        for element in soup.find_all(attrs={"max": True}):
            max_val = element.get('max')
            field_name = self._get_field_name(element)
            validation_msgs.append(f"🔢 Maximum Value ({field_name}): {max_val}")
        
        # Step validation
        for element in soup.find_all(attrs={"step": True}):
            step = element.get('step')
            field_name = self._get_field_name(element)
            if step != "any":
                validation_msgs.append(f"📊 Step Increment ({field_name}): {step}")
        
        # Input type validation
        for input_type, message in self.input_types_validation.items():
            elements = soup.find_all('input', type=input_type)
            for element in elements:
                field_name = self._get_field_name(element)
                validation_msgs.append(f"🔍 {message} ({field_name})")
        
        return validation_msgs
    
    def _extract_visible_validation_messages(self, soup: BeautifulSoup) -> List[str]:
        """Extract visible validation error messages"""
        error_msgs = []
        
        # Find elements with validation message classes
        for selector in self.validation_message_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) < 200:  # Reasonable error message length
                    error_msgs.append(f"❌ Validation Error: {text}")
        
        # Find elements with validation data attributes
        for element in soup.find_all(attrs={"data-error": True}):
            error_text = element.get('data-error', '').strip()
            if error_text:
                error_msgs.append(f"❌ Field Error: {error_text}")
        
        for element in soup.find_all(attrs={"data-validation": True}):
            validation_text = element.get('data-validation', '').strip()
            if validation_text:
                error_msgs.append(f"✅ Validation Rule: {validation_text}")
        
        # Find error messages linked via aria-describedby
        for element in soup.find_all(attrs={"aria-invalid": "true"}):
            described_by = element.get('aria-describedby', '').strip()
            if described_by:
                error_element = soup.find(id=described_by)
                if error_element:
                    error_text = error_element.get_text(strip=True)
                    if error_text:
                        field_name = self._get_field_name(element)
                        error_msgs.append(f"❌ {field_name} Error: {error_text}")
        
        return error_msgs
    
    def _extract_custom_validation(self, soup: BeautifulSoup) -> List[str]:
        """Extract custom validation messages and requirements"""
        custom_msgs = []
        
        # Find validation help text
        help_elements = soup.find_all(class_=re.compile(r'help|hint|description|note'))
        for element in help_elements:
            text = element.get_text(strip=True)
            if text and any(word in text.lower() for word in ['required', 'format', 'characters', 'valid', 'enter']):
                custom_msgs.append(f"💡 Validation Hint: {text}")
        
        # Find password strength indicators
        password_elements = soup.find_all(class_=re.compile(r'password.*strength|strength.*meter'))
        for element in password_elements:
            text = element.get_text(strip=True)
            if text:
                custom_msgs.append(f"🔐 Password Strength: {text}")
        
        # Find confirmation field requirements
        confirm_elements = soup.find_all(attrs={"name": re.compile(r'confirm|repeat')})
        for element in confirm_elements:
            field_name = self._get_field_name(element)
            custom_msgs.append(f"🔁 Confirmation Required: {field_name}")
        
        return custom_msgs
    
    def _extract_js_validation_from_context(self, js_context: Dict) -> List[str]:
        """Extract validation messages from JavaScript context"""
        js_validation = []
        
        # Look for validation messages in JavaScript variables
        if 'validation_messages' in js_context:
            messages = js_context['validation_messages']
            if isinstance(messages, dict):
                for field, message in messages.items():
                    js_validation.append(f"🔧 JS Validation ({field}): {message}")
        
        # Look for form validation libraries
        if 'form_validators' in js_context:
            validators = js_context['form_validators']
            if isinstance(validators, list):
                for validator in validators:
                    if isinstance(validator, str):
                        js_validation.append(f"🔧 JS Validator: {validator}")
        
        return js_validation
    
    def _extract_constraint_validation(self, soup: BeautifulSoup) -> List[str]:
        """Extract constraint validation API information"""
        constraint_msgs = []
        
        # Find elements with custom validity messages
        for element in soup.find_all(attrs={"data-custom-validity": True}):
            message = element.get('data-custom-validity', '').strip()
            if message:
                field_name = self._get_field_name(element)
                constraint_msgs.append(f"🎯 Custom Validity ({field_name}): {message}")
        
        # Find elements with validation state classes
        valid_elements = soup.find_all(class_=re.compile(r'is-valid|valid'))
        for element in valid_elements:
            if element.name in ['input', 'textarea', 'select']:
                field_name = self._get_field_name(element)
                constraint_msgs.append(f"✅ Valid Field: {field_name}")
        
        invalid_elements = soup.find_all(class_=re.compile(r'is-invalid|invalid'))
        for element in invalid_elements:
            if element.name in ['input', 'textarea', 'select']:
                field_name = self._get_field_name(element)
                constraint_msgs.append(f"❌ Invalid Field: {field_name}")
        
        return constraint_msgs
    
    def _get_field_name(self, element: Tag) -> str:
        """Get a human-readable name for a form field"""
        # Check for aria-label
        if element.get('aria-label'):
            return element.get('aria-label').strip()
        
        # Check for associated label
        element_id = element.get('id')
        if element_id:
            # Find by for attribute
            parent = element.find_parent()
            if parent:
                label = parent.find('label', attrs={'for': element_id})
                if label:
                    return label.get_text(strip=True)
        
        # Check for parent label
        parent_label = element.find_parent('label')
        if parent_label:
            return parent_label.get_text(strip=True)
        
        # Use name, placeholder, or generate from type
        if element.get('name'):
            return element.get('name').replace('_', ' ').replace('-', ' ').title()
        
        if element.get('placeholder'):
            return element.get('placeholder').strip()
        
        # Fallback to type
        input_type = element.get('type', element.name)
        return f"{input_type.title()} Field"