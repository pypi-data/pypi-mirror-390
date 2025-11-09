from typing import List, Dict, Any
from pathlib import Path
import ast
from .base import ConsistencyStrategy


class PerformanceStrategy(ConsistencyStrategy):
    """Detect performance issues and anti-patterns"""
    
    def __init__(self):
        super().__init__()
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect performance issues in code"""
        issues = []
        
        # Check for inefficient loops
        issues.extend(self._check_inefficient_loops(tree, file_content))
        
        # Check for N+1 query patterns
        issues.extend(self._check_n_plus_one(tree, file_content))
        
        # Check for repeated computation
        issues.extend(self._check_repeated_computation(tree, file_content))
        
        # Check for inefficient string concatenation
        issues.extend(self._check_string_concat(tree, file_content))
        
        # Check for unnecessary list conversions
        issues.extend(self._check_unnecessary_conversions(tree, file_content))
        
        # Check for missing caching opportunities
        issues.extend(self._check_caching_opportunities(tree, file_content))
        
        return issues
    
    def _check_inefficient_loops(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect loops that can be optimized"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for append in loop (can use list comprehension)
            if isinstance(node, ast.For):
                has_simple_append = False
                
                for child in node.body:
                    if isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
                        if isinstance(child.value.func, ast.Attribute):
                            if child.value.func.attr == 'append':
                                has_simple_append = True
                                break
                
                # Also check for direct append statements
                for child in node.body:
                    if isinstance(child, ast.Expr):
                        if isinstance(child.value, ast.Call):
                            if isinstance(child.value.func, ast.Attribute) and child.value.func.attr == 'append':
                                # Check if it's a simple transformation
                                if len(node.body) == 1 or (len(node.body) == 2 and isinstance(node.body[0], ast.Expr)):
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'info',
                                        'type': 'performance',
                                        'message': 'Loop with append can be replaced with list comprehension',
                                        'suggestion': 'Use list comprehension for better performance and readability',
                                        'fixable': False
                                    })
                                    break
            
            # Check for nested loops with O(n^2) or worse complexity
            if isinstance(node, ast.For):
                nested_loops = [n for n in ast.walk(node) if isinstance(n, ast.For) and n != node]
                if len(nested_loops) >= 2:
                    issues.append({
                        'line': node.lineno,
                        'column': node.col_offset,
                        'severity': 'warning',
                        'type': 'performance',
                        'message': 'Multiple nested loops detected - consider using a more efficient algorithm',
                        'suggestion': 'Review algorithm complexity and consider using sets, dicts, or other data structures',
                        'fixable': False
                    })
        
        return issues
    
    def _check_n_plus_one(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect N+1 query patterns"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for database queries inside loops
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            # Common query methods
                            if child.func.attr in ['get', 'filter', 'execute', 'query', 'find', 'find_one']:
                                issues.append({
                                    'line': child.lineno,
                                    'column': child.col_offset,
                                    'severity': 'warning',
                                    'type': 'performance',
                                    'message': 'Potential N+1 query: database query inside loop',
                                    'suggestion': 'Consider fetching all data at once or using batch queries',
                                    'fixable': False
                                })
                                break
        
        return issues
    
    def _check_repeated_computation(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect repeated expensive computations"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for function calls in loop condition or body that don't depend on loop var
                if isinstance(node.iter, ast.Call):
                    if isinstance(node.iter.func, ast.Name):
                        if node.iter.func.id == 'range':
                            # Check if range is called with a function result
                            if node.iter.args and isinstance(node.iter.args[0], ast.Call):
                                if isinstance(node.iter.args[0].func, ast.Name):
                                    if node.iter.args[0].func.id == 'len':
                                        # This is actually a common pattern, but could be optimized
                                        pass
        
        return issues
    
    def _check_string_concat(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect inefficient string concatenation"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check for += with strings inside loop
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign):
                        if isinstance(child.op, ast.Add):
                            # Check if we're dealing with strings
                            # This is a heuristic - we can't always tell without type info
                            issues.append({
                                'line': child.lineno,
                                'column': child.col_offset,
                                'severity': 'info',
                                'type': 'performance',
                                'message': 'String concatenation in loop may be inefficient',
                                'suggestion': 'Consider using list.append() and "".join() for better performance',
                                'fixable': False
                            })
        
        return issues
    
    def _check_unnecessary_conversions(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unnecessary type conversions"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for list(dict.keys()) - dict.keys() is already iterable
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'list':
                    if node.args and isinstance(node.args[0], ast.Call):
                        if isinstance(node.args[0].func, ast.Attribute):
                            if node.args[0].func.attr in ['keys', 'values', 'items']:
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'info',
                                    'type': 'performance',
                                    'message': f"Unnecessary list() conversion - .{node.args[0].func.attr}() is already iterable",
                                    'suggestion': f"Remove list() wrapper unless you need list-specific features",
                                    'fixable': False
                                })
        
        return issues
    
    def _check_caching_opportunities(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect functions that could benefit from caching"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Check if function is called multiple times with same args
                # This is a heuristic - we look for pure functions with no side effects
                
                # Check if function has no side effects (no assignments to non-local, no I/O)
                has_side_effects = False
                
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            # I/O functions
                            if child.func.id in ['print', 'open', 'input']:
                                has_side_effects = True
                                break
                        elif isinstance(child.func, ast.Attribute):
                            if child.func.attr in ['write', 'read', 'execute', 'commit']:
                                has_side_effects = True
                                break
                
                # Check for expensive operations
                has_expensive_ops = False
                for child in ast.walk(node):
                    # Nested loops
                    if isinstance(child, ast.For):
                        nested = [n for n in ast.walk(child) if isinstance(n, ast.For) and n != child]
                        if nested:
                            has_expensive_ops = True
                            break
                
                if has_expensive_ops and not has_side_effects:
                    # Check if function has parameters (cacheable)
                    if node.args.args:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'info',
                            'type': 'performance',
                            'message': f"Function '{node.name}' may benefit from caching (memoization)",
                            'suggestion': 'Consider using @functools.lru_cache decorator',
                            'fixable': False
                        })
        
        return issues
    
    def _check_string_operations(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect inefficient string concatenation and operations"""
        issues = []
        
        for node in ast.walk(tree):
            # Check for string concatenation in loops
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.AugAssign):
                        if isinstance(child.op, ast.Add):
                            # Check if operating on strings
                            if isinstance(child.target, ast.Name):
                                issues.append({
                                    'line': child.lineno,
                                    'column': child.col_offset,
                                    'severity': 'info',
                                    'type': 'performance',
                                    'message': 'String concatenation in loop - use join() for better performance',
                                    'suggestion': 'Collect strings in a list and use "".join(list) at the end',
                                    'fixable': False
                                })
        
        return issues
    
    def _check_nested_loops(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect deeply nested loops that might have performance issues"""
        issues = []
        
        def count_nested_loops(node, depth=0):
            if isinstance(node, (ast.For, ast.While)):
                depth += 1
                if depth >= 3:
                    issues.append({
                        'line': node.lineno,
                        'column': node.col_offset,
                        'severity': 'warning',
                        'type': 'performance',
                        'message': f'Deeply nested loops (depth {depth}) - O(n^{depth}) complexity',
                        'suggestion': 'Consider algorithmic optimization or caching',
                        'fixable': False
                    })
                
                for child in node.body:
                    count_nested_loops(child, depth)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                count_nested_loops(node)
        
        return issues
    
    def _check_regex_compilation(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect repeated regex compilation in loops"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Check for re.compile in loop
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if (isinstance(child.func.value, ast.Name) and 
                                child.func.value.id == 're' and 
                                child.func.attr == 'compile'):
                                issues.append({
                                    'line': child.lineno,
                                    'column': child.col_offset,
                                    'severity': 'warning',
                                    'type': 'performance',
                                    'message': 'Regex compilation inside loop - compile once outside the loop',
                                    'suggestion': 'Move re.compile() outside the loop and reuse the compiled pattern',
                                    'fixable': False
                                })
        
        return issues
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        """Generate fix for performance issues where possible"""
        
        # Most performance issues require manual review and refactoring
        # We don't auto-fix these as they can change behavior
        
        return {}

