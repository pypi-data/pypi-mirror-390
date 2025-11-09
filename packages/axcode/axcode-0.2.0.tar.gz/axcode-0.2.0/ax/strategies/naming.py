import ast
import re
from typing import List, Dict, Any
from pathlib import Path
from .base import ConsistencyStrategy


class NamingStrategy(ConsistencyStrategy):
    
    def __init__(self):
        super().__init__()
        self.function_pattern = re.compile(r'^[a-z_][a-z0-9_]*$')
        self.class_pattern = re.compile(r'^[A-Z][a-zA-Z0-9]*$')
        self.constant_pattern = re.compile(r'^[A-Z_][A-Z0-9_]*$')
        self.camel_case_pattern = re.compile(r'^[a-z]+([A-Z][a-z0-9]*)+$')
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        project_style = project_context.get('naming_convention', 'snake_case')
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                issue = self._check_function_name(node, file_path, project_style)
                if issue:
                    issues.append(issue)
            
            elif isinstance(node, ast.ClassDef):
                issue = self._check_class_name(node, file_path)
                if issue:
                    issues.append(issue)
            
            elif isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    issue = self._check_variable_name(node, file_path, project_style)
                    if issue:
                        issues.append(issue)
        
        return issues
    
    def _check_function_name(self, node: ast.FunctionDef, file_path: Path, style: str) -> Dict[str, Any]:
        name = node.name
        
        if name.startswith('_'):
            return None
        
        is_snake_case = self.function_pattern.match(name)
        is_camel_case = self.camel_case_pattern.match(name)
        
        if style == 'snake_case' and is_camel_case:
            snake_name = self._camel_to_snake(name)
            return {
                'line': node.lineno,
                'column': node.col_offset,
                'severity': 'warning',
                'type': 'naming_convention',
                'message': f"Function '{name}' uses camelCase but project prefers snake_case",
                'current_code': name,
                'suggested_fix': snake_name,
                'confidence': 0.95
            }
        
        return None
    
    def _check_class_name(self, node: ast.ClassDef, file_path: Path) -> Dict[str, Any]:
        name = node.name
        
        if not self.class_pattern.match(name):
            return {
                'line': node.lineno,
                'column': node.col_offset,
                'severity': 'warning',
                'type': 'naming_convention',
                'message': f"Class '{name}' should use PascalCase",
                'current_code': name,
                'suggested_fix': self._to_pascal_case(name),
                'confidence': 0.85
            }
        
        return None
    
    def _check_variable_name(self, node: ast.Name, file_path: Path, style: str) -> Dict[str, Any]:
        name = node.id
        
        if len(name) <= 1 or name.startswith('_'):
            return None
        
        is_camel_case = self.camel_case_pattern.match(name)
        
        if style == 'snake_case' and is_camel_case and not name[0].isupper():
            return {
                'line': node.lineno,
                'column': node.col_offset,
                'severity': 'info',
                'type': 'naming_convention',
                'message': f"Variable '{name}' uses camelCase but project prefers snake_case",
                'current_code': name,
                'suggested_fix': self._camel_to_snake(name),
                'confidence': 0.80
            }
        
        return None
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        current = issue['current_code']
        suggested = issue['suggested_fix']
        
        lines = file_content.split('\n')
        line_idx = issue['line'] - 1
        
        if line_idx < len(lines):
            original_line = lines[line_idx]
            fixed_line = original_line.replace(current, suggested)
            
            return {
                'original_line': original_line,
                'fixed_line': fixed_line,
                'line_number': issue['line'],
                'description': f"Renamed '{current}' to '{suggested}'",
                'confidence': issue.get('confidence', 0.8)
            }
        
        return None
    
    @staticmethod
    def _camel_to_snake(name: str) -> str:
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    @staticmethod
    def _to_pascal_case(name: str) -> str:
        if '_' in name:
            return ''.join(word.capitalize() for word in name.split('_'))
        return name[0].upper() + name[1:] if name else name

