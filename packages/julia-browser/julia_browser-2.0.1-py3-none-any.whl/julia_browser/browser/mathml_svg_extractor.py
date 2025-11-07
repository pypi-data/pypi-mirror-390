#!/usr/bin/env python3
"""
MathML and SVG Text Extraction
Extracts mathematical formulas and vector graphics text content
"""

import re
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag


class MathMLSVGExtractor:
    """Extracts text content from MathML mathematical formulas and SVG graphics"""
    
    def __init__(self):
        self.mathml_elements = [
            'math', 'mi', 'mn', 'mo', 'mtext', 'mspace', 'ms',
            'mrow', 'mfrac', 'msup', 'msub', 'msubsup', 'munder',
            'mover', 'munderover', 'mmultiscripts', 'mtable', 'mtr',
            'mtd', 'maligngroup', 'malignmark', 'menclose', 'maction',
            'mpadded', 'mphantom', 'mfenced', 'msqrt', 'mroot'
        ]
        
        self.svg_text_elements = [
            'text', 'tspan', 'textPath', 'title', 'desc'
        ]
        
        self.math_operators = {
            '&plus;': '+', '&minus;': '−', '&times;': '×', '&divide;': '÷',
            '&equals;': '=', '&ne;': '≠', '&lt;': '<', '&gt;': '>',
            '&le;': '≤', '&ge;': '≥', '&plusmn;': '±', '&infin;': '∞',
            '&int;': '∫', '&sum;': '∑', '&prod;': '∏', '&part;': '∂',
            '&nabla;': '∇', '&radic;': '√', '&prop;': '∝', '&empty;': '∅',
            '&isin;': '∈', '&notin;': '∉', '&ni;': '∋', '&cap;': '∩',
            '&cup;': '∪', '&sub;': '⊂', '&sup;': '⊃', '&nsub;': '⊄',
            '&sube;': '⊆', '&supe;': '⊇', '&oplus;': '⊕', '&otimes;': '⊗',
            '&perp;': '⊥', '&sdot;': '⋅', '&lceil;': '⌈', '&rceil;': '⌉',
            '&lfloor;': '⌊', '&rfloor;': '⌋', '&lang;': '⟨', '&rang;': '⟩'
        }
    
    def extract_mathml_svg_content(self, soup: BeautifulSoup, js_context: Dict) -> str:
        """Extract content from MathML and SVG elements"""
        try:
            math_svg_content = []
            
            # Extract MathML mathematical formulas
            mathml_content = self._extract_mathml_formulas(soup)
            math_svg_content.extend(mathml_content)
            
            # Extract SVG text content
            svg_content = self._extract_svg_text(soup)
            math_svg_content.extend(svg_content)
            
            # Extract LaTeX-style math notation
            latex_content = self._extract_latex_math(soup)
            math_svg_content.extend(latex_content)
            
            # Extract ASCII math representations
            ascii_math = self._extract_ascii_math(soup)
            math_svg_content.extend(ascii_math)
            
            if math_svg_content:
                return "\n## 🔢 Mathematical Content & Graphics\n" + "\n".join(math_svg_content) + "\n"
            
            return ""
            
        except Exception as e:
            return f"<!-- MathML/SVG extraction error: {str(e)} -->\n"
    
    def _extract_mathml_formulas(self, soup: BeautifulSoup) -> List[str]:
        """Extract and convert MathML mathematical formulas to readable text"""
        mathml_formulas = []
        
        # Find all math elements
        math_elements = soup.find_all('math')
        for math in math_elements:
            formula_text = self._convert_mathml_to_text(math)
            if formula_text.strip():
                mathml_formulas.append(f"📐 Formula: {formula_text}")
        
        # Find inline math expressions
        mi_elements = soup.find_all('mi')  # Math identifiers (variables)
        if mi_elements and not math_elements:  # Only if not already in math context
            for mi in mi_elements:
                text = mi.get_text(strip=True)
                if text and len(text) <= 5:  # Likely a variable
                    mathml_formulas.append(f"🔤 Variable: {text}")
        
        # Find math numbers
        mn_elements = soup.find_all('mn')  # Math numbers
        if mn_elements and not math_elements:
            for mn in mn_elements:
                text = mn.get_text(strip=True)
                if text:
                    mathml_formulas.append(f"🔢 Number: {text}")
        
        # Find math operators
        mo_elements = soup.find_all('mo')  # Math operators
        if mo_elements and not math_elements:
            operators = []
            for mo in mo_elements:
                text = mo.get_text(strip=True)
                if text:
                    operators.append(text)
            if operators:
                mathml_formulas.append(f"➕ Operators: {' '.join(operators)}")
        
        return mathml_formulas
    
    def _convert_mathml_to_text(self, math_element: Tag) -> str:
        """Convert MathML element to readable mathematical text"""
        try:
            # Handle fractions
            fractions = math_element.find_all('mfrac')
            for frac in fractions:
                numerator = frac.find('mn') or frac.find('mi')
                denominator = frac.find_all(['mn', 'mi'])[1] if len(frac.find_all(['mn', 'mi'])) > 1 else None
                
                if numerator and denominator:
                    num_text = numerator.get_text(strip=True)
                    den_text = denominator.get_text(strip=True)
                    frac_text = f"({num_text}/{den_text})"
                    # Replace the fraction with readable text
                    frac.replace_with(frac_text)
            
            # Handle superscripts (powers)
            superscripts = math_element.find_all('msup')
            for sup in superscripts:
                base = sup.find(['mi', 'mn'])
                exponent = sup.find_all(['mi', 'mn'])[1] if len(sup.find_all(['mi', 'mn'])) > 1 else None
                
                if base and exponent:
                    base_text = base.get_text(strip=True)
                    exp_text = exponent.get_text(strip=True)
                    sup_text = f"{base_text}^{exp_text}"
                    sup.replace_with(sup_text)
            
            # Handle subscripts
            subscripts = math_element.find_all('msub')
            for sub in subscripts:
                base = sub.find(['mi', 'mn'])
                subscript = sub.find_all(['mi', 'mn'])[1] if len(sub.find_all(['mi', 'mn'])) > 1 else None
                
                if base and subscript:
                    base_text = base.get_text(strip=True)
                    sub_text = subscript.get_text(strip=True)
                    subsup_text = f"{base_text}_{sub_text}"
                    sub.replace_with(subsup_text)
            
            # Handle square roots
            roots = math_element.find_all('msqrt')
            for root in roots:
                content = root.get_text(strip=True)
                if content:
                    root.replace_with(f"√{content}")
            
            # Handle general roots
            nth_roots = math_element.find_all('mroot')
            for root in nth_roots:
                elements = root.find_all(['mi', 'mn'])
                if len(elements) >= 2:
                    radicand = elements[0].get_text(strip=True)
                    index = elements[1].get_text(strip=True)
                    root.replace_with(f"√[{index}]{radicand}")
            
            # Get final text and clean up
            formula_text = math_element.get_text(separator=' ', strip=True)
            
            # Replace HTML entities with math symbols
            for entity, symbol in self.math_operators.items():
                formula_text = formula_text.replace(entity, symbol)
            
            return formula_text
            
        except Exception:
            # Fallback to simple text extraction
            return math_element.get_text(separator=' ', strip=True)
    
    def _extract_svg_text(self, soup: BeautifulSoup) -> List[str]:
        """Extract text content from SVG graphics"""
        svg_texts = []
        
        # Find all SVG elements
        svg_elements = soup.find_all('svg')
        for svg in svg_elements:
            # Extract title and description
            title = svg.find('title')
            if title:
                title_text = title.get_text(strip=True)
                if title_text:
                    svg_texts.append(f"🎨 SVG Title: {title_text}")
            
            desc = svg.find('desc')
            if desc:
                desc_text = desc.get_text(strip=True)
                if desc_text:
                    svg_texts.append(f"📝 SVG Description: {desc_text}")
            
            # Extract text elements
            text_elements = svg.find_all(['text', 'tspan'])
            for text_elem in text_elements:
                text_content = text_elem.get_text(strip=True)
                if text_content:
                    # Get position if available
                    x = text_elem.get('x', '')
                    y = text_elem.get('y', '')
                    position = f" at ({x},{y})" if x and y else ""
                    svg_texts.append(f"📄 SVG Text{position}: {text_content}")
            
            # Extract textPath elements (text along paths)
            textpaths = svg.find('textPath')
            for textpath in textpaths:
                path_text = textpath.get_text(strip=True)
                if path_text:
                    svg_texts.append(f"🛤️ SVG Path Text: {path_text}")
        
        return svg_texts
    
    def _extract_latex_math(self, soup: BeautifulSoup) -> List[str]:
        """Extract LaTeX-style mathematical notation"""
        latex_math = []
        
        # Find elements with LaTeX delimiters
        latex_patterns = [
            (r'\$\$([^$]+)\$\$', 'Display Math'),  # Display math $$...$$
            (r'\$([^$]+)\$', 'Inline Math'),       # Inline math $...$
            (r'\\begin\{([^}]+)\}(.*?)\\end\{\1\}', 'LaTeX Environment'),  # LaTeX environments
            (r'\\([a-zA-Z]+)(\{[^}]*\})*', 'LaTeX Command')  # LaTeX commands
        ]
        
        page_text = soup.get_text()
        
        for pattern, math_type in latex_patterns:
            matches = re.findall(pattern, page_text, re.DOTALL)
            for match in matches:
                if isinstance(match, tuple):
                    if len(match) == 2 and match[0] and match[1]:  # Environment
                        latex_math.append(f"📚 {math_type} ({match[0]}): {match[1].strip()[:100]}...")
                    elif match[0]:  # Command or simple match
                        latex_math.append(f"🔤 {math_type}: {match[0].strip()[:100]}...")
                else:
                    latex_math.append(f"🔤 {math_type}: {match.strip()[:100]}...")
        
        # Find MathJax/KaTeX script tags
        math_scripts = soup.find_all('script', type=re.compile(r'math|tex'))
        for script in math_scripts:
            content = script.get_text(strip=True)
            if content:
                latex_math.append(f"🧮 Math Script: {content[:100]}...")
        
        return latex_math
    
    def _extract_ascii_math(self, soup: BeautifulSoup) -> List[str]:
        """Extract ASCII-style mathematical representations"""
        ascii_math = []
        
        # Look for mathematical expressions in code blocks or pre elements
        code_elements = soup.find_all(['code', 'pre', 'kbd', 'samp'])
        for code in code_elements:
            content = code.get_text(strip=True)
            if content and self._looks_like_math(content):
                ascii_math.append(f"💻 ASCII Math: {content[:100]}...")
        
        # Look for mathematical expressions in specific classes
        math_classes = soup.find_all(class_=re.compile(r'math|formula|equation|expression'))
        for element in math_classes:
            content = element.get_text(strip=True)
            if content and not element.find(['math', 'svg']):  # Not already processed
                ascii_math.append(f"🔢 Math Expression: {content[:100]}...")
        
        # Look for table-based mathematical layouts (matrices, etc.)
        tables = soup.find_all('table', class_=re.compile(r'matrix|math'))
        for table in tables:
            # Extract table structure as mathematical matrix
            rows = table.find_all('tr')
            if rows and len(rows) <= 10:  # Reasonable size for math
                matrix_content = []
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_content = [cell.get_text(strip=True) for cell in cells]
                    if all(self._is_numeric_or_variable(cell) for cell in row_content):
                        matrix_content.append(' '.join(row_content))
                
                if matrix_content:
                    ascii_math.append(f"📊 Math Matrix:\n  " + "\n  ".join(matrix_content))
        
        return ascii_math
    
    def _looks_like_math(self, text: str) -> bool:
        """Check if text looks like mathematical content"""
        math_indicators = [
            r'[+\-*/=<>≤≥≠±∞∑∏∫∂∇√π∈∉⊂⊃∩∪]',  # Math symbols
            r'\b\d+\s*[+\-*/]\s*\d+',  # Simple arithmetic
            r'\b[a-zA-Z]\s*[=<>]\s*\d+',  # Variables with values
            r'\b(sin|cos|tan|log|ln|exp|sqrt|abs)\s*\(',  # Math functions
            r'\^\d+|\b\d+\^\d+',  # Exponents
            r'\b(matrix|vector|equation|formula|theorem|proof)\b'  # Math terms
        ]
        
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in math_indicators)
    
    def _is_numeric_or_variable(self, text: str) -> bool:
        """Check if text is numeric or a mathematical variable"""
        if not text:
            return False
        
        # Remove whitespace
        text = text.strip()
        
        # Check if it's a number (including decimals, negatives, fractions)
        if re.match(r'^[-+]?\d*\.?\d+([eE][-+]?\d+)?$', text):
            return True
        
        # Check if it's a simple variable (1-3 characters, mostly letters)
        if re.match(r'^[a-zA-Z][a-zA-Z0-9]{0,2}$', text):
            return True
        
        # Check if it's a mathematical expression
        if re.search(r'[+\-*/=<>√∑∏∫]', text):
            return True
        
        return False