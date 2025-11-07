"""
Dynamic Content Filter - Intelligently filters noise from web content
"""

import re
from typing import List, Set, Dict, Tuple
from collections import Counter

class DynamicContentFilter:
    """Dynamically identifies and filters content noise patterns"""
    
    def __init__(self):
        self.noise_indicators = {
            'repetition_threshold': 0.7,      # Lines with >70% repeated chars
            'length_threshold': 150,           # Lines longer than 150 chars
            'bracket_density': 0.3,            # Lines with >30% brackets/braces
            'json_like_threshold': 0.5,        # Lines that look like JSON
            'code_density': 0.4,               # Lines with >40% code-like chars
        }
        
    def filter_content(self, content: str) -> str:
        """Dynamically filter content based on learned patterns"""
        lines = content.split('\n')
        
        # Analyze content patterns
        line_stats = self._analyze_lines(lines)
        
        # Identify noise patterns
        noise_lines = self._identify_noise_lines(lines, line_stats)
        
        # Filter out noise while preserving structure
        filtered_lines = self._filter_with_context(lines, noise_lines, line_stats)
        
        return '\n'.join(filtered_lines)
    
    def _analyze_lines(self, lines: List[str]) -> Dict:
        """Analyze lines to understand content patterns"""
        stats = {
            'lengths': [len(line.strip()) for line in lines],
            'char_distributions': [],
            'patterns': Counter(),
            'line_types': [],
        }
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                stats['line_types'].append('empty')
                continue
                
            # Character distribution analysis
            char_counts = {
                'letters': sum(1 for c in stripped if c.isalpha()),
                'digits': sum(1 for c in stripped if c.isdigit()),
                'brackets': sum(1 for c in stripped if c in '{}[]()'),
                'quotes': sum(1 for c in stripped if c in '"\''),
                'punctuation': sum(1 for c in stripped if c in ':;,.!?'),
                'special': sum(1 for c in stripped if not c.isalnum() and c not in ' \t'),
            }
            
            stats['char_distributions'].append(char_counts)
            
            # Pattern recognition
            line_type = self._classify_line_type(stripped, char_counts)
            stats['line_types'].append(line_type)
            stats['patterns'][line_type] += 1
            
        return stats
    
    def _classify_line_type(self, line: str, char_counts: Dict) -> str:
        """Classify what type of content a line represents"""
        total_chars = len(line)
        if total_chars == 0:
            return 'empty'
            
        # Calculate ratios
        ratios = {k: v / total_chars for k, v in char_counts.items()}
        
        # Enhanced classification logic
        line_lower = line.lower().strip()
        
        # Detect framework configuration patterns
        if line.startswith('{"require":[') or 'handlePayload' in line:
            return 'framework_config'
        elif line.startswith('{"') and ratios['brackets'] > 0.2 and ratios['quotes'] > 0.15:
            return 'json_config'
        elif line.startswith(('function', 'var ', 'const ', 'let ', 'window.', 'import ')):
            return 'javascript_declaration'
        elif 'qpl' in line_lower and ('server' in line_lower or 'timing' in line_lower):
            return 'performance_tracking'
        elif self._is_css_rule(line):
            return 'css_rule'
        elif self._is_image_data(line):
            return 'image_data'
        elif self._is_module_import(line):
            return 'module_import'
        elif ratios['special'] > 0.5 or ratios['digits'] > 0.4:
            return 'encoded_data'
        elif line.startswith(('http', 'data:', '//', 'src=')):
            return 'url_or_reference'
        elif ratios['letters'] > 0.6 and ratios['punctuation'] < 0.1 and len(line.strip()) > 10:
            return 'readable_text'
        elif line.startswith(('#', '*', '-', '+')):
            return 'markdown_structure'
        elif ratios['brackets'] > 0.2 and ratios['quotes'] > 0.1:
            return 'structured_data'
        elif line.strip().startswith('<') and line.strip().endswith('>'):
            return 'html_tag'
        else:
            return 'mixed_content'
    
    def _identify_noise_lines(self, lines: List[str], stats: Dict) -> Set[int]:
        """Identify which lines are likely noise"""
        noise_indices = set()
        
        # Enhanced noise detection patterns (but preserve meaningful content)
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # Skip obvious JavaScript code but keep meaningful text
            if any(pattern in line_stripped for pattern in [
                'window[', 'tesla_cta[', 'sl_tr_', 'qpl_', 'handlePayload',
                'function(', 'var ', 'let ', 'const ', '();'
            ]) and not any(keep in line_stripped.lower() for keep in [
                'tesla', 'cybertruck', 'solar', 'energy', 'cars'
            ]):
                noise_indices.add(i)
                continue
                
            # Skip JSON configuration lines but keep readable content
            if (line_stripped.startswith('"') and '":' in line_stripped and 
                not any(keep in line_stripped.lower() for keep in [
                    'slide', 'image', 'delivery', 'autonomous'
                ])):
                noise_indices.add(i)
                continue
                
            # Skip pure CSS/config data
            if any(pattern in line_stripped for pattern in [
                'marginBlock', 'paddingBlock', 'gridRows', 'gridCols',
                'mobileConfigOverwrite', 'tabletConfigOverwrite'
            ]) and line_stripped.count(':') > 1:
                noise_indices.add(i)
                continue
        
        # Statistical analysis approach
        lengths = stats['lengths']
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            length_threshold = max(avg_length * 2, self.noise_indicators['length_threshold'])
        else:
            length_threshold = self.noise_indicators['length_threshold']
        
        # Pattern-based noise detection
        pattern_counts = stats['patterns']
        total_lines = len(lines)
        
        # Enhanced noise patterns - focus on framework and configuration content
        noise_patterns = {
            'framework_config', 
            'json_config', 
            'encoded_data', 
            'javascript_declaration',
            'performance_tracking',
            'css_rule',
            'module_import'
        }
        
        # Special handling for image data - don't filter completely but simplify
        image_patterns = {'image_data'}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue
                
            line_type = stats['line_types'][i]
            
            # Multiple criteria for noise detection
            is_noise = (
                # Pattern-based
                line_type in noise_patterns or
                
                # Length-based (dynamic threshold) - more aggressive for certain patterns
                (len(stripped) > length_threshold) or
                (len(stripped) > 80 and line_type in ['structured_data', 'mixed_content']) or
                
                # Repetition-based
                self._has_excessive_repetition(stripped) or
                
                # Density-based
                self._has_high_noise_density(stripped) or
                
                # Framework-specific patterns (learned dynamically)
                self._is_framework_noise(stripped)
            )
            
            if is_noise:
                noise_indices.add(i)
        
        return noise_indices
    
    def _has_excessive_repetition(self, line: str) -> bool:
        """Check if line has excessive character repetition"""
        if len(line) < 10:
            return False
            
        # Count character frequency
        char_freq = Counter(line.lower())
        total_chars = len(line)
        
        # Check for any character appearing too frequently
        for char, count in char_freq.items():
            if char.isalnum() and count / total_chars > self.noise_indicators['repetition_threshold']:
                return True
                
        return False
    
    def _has_high_noise_density(self, line: str) -> bool:
        """Check if line has high density of noise characters"""
        noise_chars = set('{}[]()":;,=&%@#$')
        noise_count = sum(1 for c in line if c in noise_chars)
        
        return noise_count / len(line) > self.noise_indicators['code_density']
    
    def _is_framework_noise(self, line: str) -> bool:
        """Dynamically detect framework/library noise patterns"""
        line_lower = line.lower()
        
        # Common framework patterns that indicate configuration/noise
        framework_indicators = [
            # Count of specific patterns that suggest framework code
            line.count('"') > 6,  # Heavy JSON
            line.count('[') > 3,  # Deep nesting
            line.count(',') > 5,  # Long parameter lists
            'null' in line and line.count('null') > 2,  # Many null values
            
            # Specific framework terms (learned patterns)
            any(term in line_lower for term in [
                'preloader', 'bootstrap', 'payload', 'timing', 
                'consistency', 'server', 'config', 'handle',
                'import ', 'from "', 'cdn.', '.js"'
            ]) and len(line) > 50,
            
            # URL-like patterns in long lines
            ('//' in line or 'http' in line_lower) and len(line) > 100,
            
            # Base64 or hash-like patterns
            any(len(part) > 20 and part.replace('_', '').replace('-', '').isalnum() 
                for part in line.split() if len(part) > 20),
        ]
        
        # If multiple indicators are present, likely framework noise
        return sum(framework_indicators) >= 2
    
    def _is_css_rule(self, line: str) -> bool:
        """Detect CSS rules and declarations"""
        line_stripped = line.strip()
        
        # CSS selector patterns
        css_patterns = [
            # CSS class/ID selectors with properties
            re.match(r'^[.#][a-zA-Z][\w-]*\{', line_stripped),
            re.match(r'^[.#][a-zA-Z][\w-]*[,\s.#:\w-]*\{', line_stripped),
            
            # CSS properties (key:value patterns)
            re.match(r'^[a-zA-Z-]+\s*:\s*[^;]+;?\s*$', line_stripped),
            
            # Complex CSS selectors
            ':' in line_stripped and '{' in line_stripped and any(prop in line_stripped for prop in [
                'display', 'padding', 'margin', 'width', 'height', 'color', 'background', 
                'font', 'border', 'position', 'flex', 'grid', 'z-index'
            ]),
            
            # CSS media queries and at-rules
            line_stripped.startswith('@media') or line_stripped.startswith('@'),
            
            # Long lines with multiple CSS properties
            len(line_stripped) > 60 and line_stripped.count(':') >= 2 and (
                'px' in line_stripped or 'em' in line_stripped or 'rem' in line_stripped or
                'auto' in line_stripped or 'none' in line_stripped or 'flex' in line_stripped
            ),
        ]
        
        return any(css_patterns)
    
    def _is_image_data(self, line: str) -> bool:
        """Detect image data URIs and long base64 encoded images"""
        line_stripped = line.strip()
        
        # Check for data URI images
        if line_stripped.startswith('data:image/'):
            return True
        
        # Check for base64 image patterns in markdown or HTML
        if ('base64,' in line_stripped and 
            ('data:image' in line_stripped or len(line_stripped) > 100)):
            return True
            
        # Check for very long base64-like strings that might be images
        if (len(line_stripped) > 200 and 
            line_stripped.replace('/', '').replace('+', '').replace('=', '').isalnum()):
            return True
            
        return False
    
    def _simplify_image_line(self, line: str) -> str:
        """Simplify image data lines to show image presence without data"""
        line_stripped = line.strip()
        
        # Extract meaningful information about the image
        if line_stripped.startswith('[!['):
            # Markdown image with alt text
            alt_match = re.search(r'\[!\[(.*?)\]', line_stripped)
            if alt_match:
                alt_text = alt_match.group(1)
                return f"[Image: {alt_text}]" if alt_text else "[Image supported]"
        
        elif line_stripped.startswith('!['):
            # Simple markdown image
            alt_match = re.search(r'!\[(.*?)\]', line_stripped)
            if alt_match:
                alt_text = alt_match.group(1)
                return f"[Image: {alt_text}]" if alt_text else "[Image supported]"
        
        elif 'data:image/' in line_stripped:
            # Data URI - extract image type
            type_match = re.search(r'data:image/(\w+)', line_stripped)
            if type_match:
                img_type = type_match.group(1).upper()
                return f"[Image: {img_type} format supported]"
        
        # Fallback for other image patterns
        return "[Image supported]"
    
    def _is_module_import(self, line: str) -> bool:
        """Detect ES6 module import statements and CDN references"""
        line_stripped = line.strip()
        
        # ES6 import patterns
        import_patterns = [
            line_stripped.startswith('import '),
            line_stripped.startswith('export '),
            'from "http' in line_stripped and '.js"' in line_stripped,
            'cdn.' in line_stripped and ('.js"' in line_stripped or '.css"' in line_stripped),
            line_stripped.startswith('import('),
            'oaistatic.com' in line_stripped,
            'assets/' in line_stripped and '.js' in line_stripped,
        ]
        
        return any(import_patterns)
    
    def _filter_with_context(self, lines: List[str], noise_indices: Set[int], stats: Dict) -> List[str]:
        """Filter lines while preserving important context"""
        filtered = []
        
        for i, line in enumerate(lines):
            if i in noise_indices:
                # Check if this noise line provides important context
                if self._is_contextually_important(line, i, lines):
                    # Keep but maybe simplify
                    simplified = self._simplify_noise_line(line)
                    if simplified:
                        filtered.append(simplified)
            else:
                # Handle image data specially
                line_type = stats['line_types'][i] if i < len(stats['line_types']) else 'mixed_content'
                if line_type == 'image_data':
                    simplified_image = self._simplify_image_line(line)
                    filtered.append(simplified_image)
                else:
                    filtered.append(line)
        
        return filtered
    
    def _is_contextually_important(self, line: str, index: int, all_lines: List[str]) -> bool:
        """Determine if a noise line provides important context"""
        stripped = line.strip()
        
        # Keep short JSON/config if it might be important
        if len(stripped) < 50 and any(word in stripped.lower() for word in ['error', 'warning', 'title', 'name']):
            return True
            
        # Keep lines that seem to be titles or headers
        if stripped.startswith(('# ', '## ', '### ')) or stripped.isupper():
            return True
            
        return False
    
    def _simplify_noise_line(self, line: str) -> str:
        """Simplify a noise line to keep essential information"""
        stripped = line.strip()
        
        # For very long lines, try to extract meaningful parts
        if len(stripped) > 100:
            # Look for quoted strings that might be titles or important text
            quotes_content = re.findall(r'["\']([^"\']{10,50})["\']', stripped)
            if quotes_content:
                return f"// {quotes_content[0]}"
        
        return ""
    
    def update_thresholds(self, feedback: Dict[str, float]):
        """Allow dynamic adjustment of filtering thresholds"""
        for key, value in feedback.items():
            if key in self.noise_indicators:
                self.noise_indicators[key] = max(0.1, min(0.9, value))