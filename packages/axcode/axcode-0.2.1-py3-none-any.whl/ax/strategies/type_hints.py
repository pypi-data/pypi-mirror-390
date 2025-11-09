import ast
from typing import List, Dict, Any
from pathlib import Path
from .base import ConsistencyStrategy


class TypeHintStrategy(ConsistencyStrategy):
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        total_functions = 0
        typed_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                has_hints = self._has_type_hints(node)
                if has_hints:
                    typed_functions += 1
        
        type_hint_ratio = project_context.get('type_hint_ratio', 0.5)
        
        if total_functions > 0:
            current_ratio = typed_functions / total_functions
            
            if type_hint_ratio > 0.7 and current_ratio < 0.5:
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not self._has_type_hints(node):
                            issues.append({
                                'line': node.lineno,
                                'column': node.col_offset,
                                'severity': 'info',
                                'type': 'type_hint',
                                'message': f"Function '{node.name}' missing type hints (project uses type hints in {type_hint_ratio*100:.0f}% of functions)",
                                'current_code': node.name,
                                'confidence': 0.60
                            })
        
        return issues
    
    def _has_type_hints(self, node: ast.FunctionDef) -> bool:
        has_return_hint = node.returns is not None
        has_arg_hints = any(arg.annotation is not None for arg in node.args.args)
        return has_return_hint or has_arg_hints
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        return {
            'original_line': '',
            'fixed_line': '',
            'line_number': issue['line'],
            'description': f"Add type hints to function '{issue['current_code']}'",
            'confidence': 0.40
        }

