import ast
from typing import Dict, Any, List
from pathlib import Path
from collections import Counter, defaultdict


class PatternLearner:
    
    def __init__(self):
        self.patterns = {}
    
    def learn_from_project(self, project_files: List[Path]) -> Dict[str, Any]:
        """Learn patterns from existing project files with enhanced detection"""
        
        naming_styles = []
        class_naming_styles = []
        variable_naming_styles = []
        type_hint_counts = {'with_hints': 0, 'without_hints': 0}
        none_check_styles = []
        docstring_counts = {'with_docs': 0, 'without_docs': 0}
        string_quote_styles = []
        import_styles = defaultdict(int)
        error_handling_patterns = []
        code_complexity = []
        
        for file_path in project_files:
            if not file_path.suffix == '.py':
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Detect string quote preferences
                string_quote_styles.extend(self._detect_string_quotes(content))
                
                for node in ast.walk(tree):
                    # Function naming
                    if isinstance(node, ast.FunctionDef):
                        naming_styles.append(self._detect_naming_style(node.name))
                        
                        # Type hints
                        if node.returns or any(arg.annotation for arg in node.args.args):
                            type_hint_counts['with_hints'] += 1
                        else:
                            type_hint_counts['without_hints'] += 1
                        
                        # Docstrings
                        if ast.get_docstring(node):
                            docstring_counts['with_docs'] += 1
                        else:
                            docstring_counts['without_docs'] += 1
                        
                        # Complexity (number of branches)
                        complexity = self._calculate_complexity(node)
                        code_complexity.append(complexity)
                        
                        # Error handling patterns
                        error_handling_patterns.append(self._detect_error_handling(node))
                    
                    # Class naming
                    if isinstance(node, ast.ClassDef):
                        class_naming_styles.append(self._detect_class_naming_style(node.name))
                    
                    # Variable naming
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                variable_naming_styles.append(self._detect_naming_style(target.id))
                    
                    # None check styles
                    if isinstance(node, ast.Compare):
                        none_check_styles.append(self._detect_none_check_style(node))
                    
                    # Import styles
                    if isinstance(node, ast.Import):
                        import_styles['direct'] += 1
                    elif isinstance(node, ast.ImportFrom):
                        import_styles['from'] += 1
                
            except Exception:
                continue
        
        # Calculate statistics
        total_funcs_type = type_hint_counts['with_hints'] + type_hint_counts['without_hints']
        total_funcs_doc = docstring_counts['with_docs'] + docstring_counts['without_docs']
        
        naming_counter = Counter([s for s in naming_styles if s])
        most_common_naming = naming_counter.most_common(1)[0][0] if naming_counter else 'snake_case'
        
        class_naming_counter = Counter([s for s in class_naming_styles if s])
        most_common_class_naming = class_naming_counter.most_common(1)[0][0] if class_naming_counter else 'PascalCase'
        
        variable_naming_counter = Counter([s for s in variable_naming_styles if s])
        most_common_var_naming = variable_naming_counter.most_common(1)[0][0] if variable_naming_counter else 'snake_case'
        
        none_check_counter = Counter([s for s in none_check_styles if s])
        most_common_none_check = none_check_counter.most_common(1)[0][0] if none_check_counter else 'is'
        
        string_quote_counter = Counter(string_quote_styles)
        most_common_quote = string_quote_counter.most_common(1)[0][0] if string_quote_counter else 'single'
        
        error_handling_counter = Counter([p for p in error_handling_patterns if p])
        most_common_error_handling = error_handling_counter.most_common(1)[0][0] if error_handling_counter else 'exceptions'
        
        avg_complexity = sum(code_complexity) / len(code_complexity) if code_complexity else 0
        
        self.patterns = {
            'naming_convention': most_common_naming,
            'class_naming_convention': most_common_class_naming,
            'variable_naming_convention': most_common_var_naming,
            'type_hint_ratio': type_hint_counts['with_hints'] / total_funcs_type if total_funcs_type > 0 else 0.0,
            'docstring_ratio': docstring_counts['with_docs'] / total_funcs_doc if total_funcs_doc > 0 else 0.0,
            'none_check_style': most_common_none_check,
            'string_quote_style': most_common_quote,
            'import_style': 'from_imports' if import_styles['from'] > import_styles['direct'] else 'direct_imports',
            'error_handling_pattern': most_common_error_handling,
            'average_complexity': avg_complexity,
            'code_style': self._determine_code_style(avg_complexity, naming_counter, type_hint_counts),
            'naming_counts': dict(naming_counter),
            'none_check_counts': dict(none_check_counter),
        }
        
        return self.patterns
    
    def _detect_naming_style(self, name: str) -> str:
        """Detect if name uses snake_case or camelCase"""
        if not name or name.startswith('_'):
            return None
        if '_' in name:
            return 'snake_case'
        elif any(c.isupper() for c in name[1:]):
            return 'camelCase'
        return 'snake_case'
    
    def _detect_class_naming_style(self, name: str) -> str:
        """Detect class naming style"""
        if not name:
            return None
        if name[0].isupper() and '_' not in name:
            return 'PascalCase'
        elif name[0].isupper() and '_' in name:
            return 'UPPER_SNAKE_CASE'
        elif '_' in name:
            return 'snake_case'
        return 'PascalCase'
    
    def _detect_none_check_style(self, node: ast.Compare) -> str:
        """Detect if None check uses 'is' or '=='"""
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(comparator, ast.Constant) and comparator.value is None:
                if isinstance(op, ast.Is):
                    return 'is'
                elif isinstance(op, ast.Eq):
                    return 'equality'
        return None
    
    def _detect_string_quotes(self, content: str) -> List[str]:
        """Detect whether code prefers single or double quotes"""
        quotes = []
        in_string = False
        quote_char = None
        
        i = 0
        while i < len(content):
            char = content[i]
            
            # Skip triple-quoted strings
            if i + 2 < len(content) and content[i:i+3] in ['"""', "'''"]:
                i += 3
                continue
            
            if char in ['"', "'"] and not in_string:
                quotes.append('double' if char == '"' else 'single')
            
            i += 1
        
        return quotes
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _detect_error_handling(self, node: ast.FunctionDef) -> str:
        """Detect error handling pattern"""
        has_try = False
        has_return_none = False
        
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try = True
            elif isinstance(child, ast.Return):
                if isinstance(child.value, ast.Constant) and child.value.value is None:
                    has_return_none = True
        
        if has_try:
            return 'exceptions'
        elif has_return_none:
            return 'return_values'
        return None
    
    def _determine_code_style(self, avg_complexity: float, naming_counter: Counter, type_hint_counts: Dict) -> str:
        """Determine overall code style"""
        style_indicators = []
        
        # Check complexity
        if avg_complexity > 10:
            style_indicators.append('complex')
        elif avg_complexity < 5:
            style_indicators.append('simple')
        
        # Check type hints
        total = type_hint_counts['with_hints'] + type_hint_counts['without_hints']
        if total > 0:
            hint_ratio = type_hint_counts['with_hints'] / total
            if hint_ratio > 0.7:
                style_indicators.append('typed')
            elif hint_ratio < 0.3:
                style_indicators.append('untyped')
        
        # Check naming consistency
        if naming_counter:
            most_common_count = naming_counter.most_common(1)[0][1]
            total_count = sum(naming_counter.values())
            if most_common_count / total_count > 0.9:
                style_indicators.append('consistent')
            else:
                style_indicators.append('mixed')
        
        return ', '.join(style_indicators) if style_indicators else 'standard'
    
    def get_patterns(self) -> Dict[str, Any]:
        """Get learned patterns"""
        return self.patterns

