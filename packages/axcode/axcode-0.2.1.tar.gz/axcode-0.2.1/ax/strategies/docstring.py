import ast
from typing import List, Dict, Any
from pathlib import Path
from .base import ConsistencyStrategy


class DocstringStrategy(ConsistencyStrategy):
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        total_functions = 0
        documented_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):
                    total_functions += 1
                    if ast.get_docstring(node):
                        documented_functions += 1
        
        docstring_ratio = project_context.get('docstring_ratio', 0.5)
        
        if total_functions > 0:
            current_ratio = documented_functions / total_functions
            
            if docstring_ratio > 0.6 and current_ratio < 0.3:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_') and not ast.get_docstring(node):
                            issues.append({
                                'line': node.lineno,
                                'column': node.col_offset,
                                'severity': 'info',
                                'type': 'docstring',
                                'message': f"Function '{node.name}' missing docstring (project has {docstring_ratio*100:.0f}% documentation coverage)",
                                'current_code': node.name,
                                'confidence': 0.50
                            })
        
        return issues
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        return {
            'original_line': '',
            'fixed_line': '',
            'line_number': issue['line'],
            'description': f"Add docstring to function '{issue['current_code']}'",
            'confidence': 0.30
        }

