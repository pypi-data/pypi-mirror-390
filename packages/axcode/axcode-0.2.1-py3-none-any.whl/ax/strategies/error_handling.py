import ast
from typing import List, Dict, Any
from pathlib import Path
from .base import ConsistencyStrategy


class ErrorHandlingStrategy(ConsistencyStrategy):
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        none_checks = []
        exception_handlers = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                if self._is_none_check_with_equality(node):
                    none_checks.append(node)
            
            if isinstance(node, ast.Try):
                exception_handlers.append(node)
        
        project_none_check_style = project_context.get('none_check_style', 'is')
        
        for node in none_checks:
            issues.append({
                'line': node.lineno,
                'column': node.col_offset,
                'severity': 'warning',
                'type': 'error_handling',
                'message': f"Use 'is None' instead of '== None' for None checks",
                'current_code': '== None',
                'suggested_fix': 'is None',
                'confidence': 0.95
            })
        
        return issues
    
    def _is_none_check_with_equality(self, node: ast.Compare) -> bool:
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant):
                if comparator.value is None:
                    return True
        return False
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        lines = file_content.split('\n')
        line_idx = issue['line'] - 1
        
        if line_idx < len(lines):
            original_line = lines[line_idx]
            fixed_line = original_line.replace('== None', 'is None').replace('!= None', 'is not None')
            
            return {
                'original_line': original_line,
                'fixed_line': fixed_line,
                'line_number': issue['line'],
                'description': "Changed '== None' to 'is None'",
                'confidence': issue.get('confidence', 0.95)
            }
        
        return None

