from typing import List, Dict, Any
from pathlib import Path
from .parser import ASTParser
from .pattern_learner import PatternLearner
from .cache_service import CacheService
from ..strategies import (
    NamingStrategy,
    TypeHintStrategy,
    ErrorHandlingStrategy,
    DocstringStrategy,
    ImportStrategy,
    LogicalErrorStrategy,
    SecurityStrategy,
    PerformanceStrategy
)


class AnalysisPipeline:
    
    def __init__(self, use_cache: bool = True):
        self.parser = ASTParser()
        self.pattern_learner = PatternLearner()
        self.cache_service = CacheService() if use_cache else None
        
        self.strategies = [
            NamingStrategy(),
            TypeHintStrategy(),
            ErrorHandlingStrategy(),
            DocstringStrategy(),
            ImportStrategy(),
            LogicalErrorStrategy(),
            SecurityStrategy(),
            PerformanceStrategy(),
        ]
    
    def analyze_file(self, file_path: Path, project_files: List[Path]) -> Dict[str, Any]:
        """Run full analysis pipeline on a file"""
        
        if self.cache_service:
            cached_result = self.cache_service.get_cached_result(file_path)
            if cached_result:
                return cached_result
        
        result = {
            'file_path': str(file_path),
            'issues': [],
            'syntax_valid': True,
            'syntax_errors': []
        }
        
        syntax_check = self.parser.check_syntax(file_path)
        if not syntax_check['valid']:
            result['syntax_valid'] = False
            result['syntax_errors'] = syntax_check['errors']
            return result
        
        tree = self.parser.parse_file(file_path)
        if not tree:
            result['error'] = 'Failed to parse file'
            return result
        
        content = file_path.read_text(encoding='utf-8')
        
        project_context = self.pattern_learner.learn_from_project(project_files)
        
        for strategy in self.strategies:
            try:
                issues = strategy.analyze(file_path, tree, content, project_context)
                result['issues'].extend(issues)
            except Exception as e:
                pass
        
        result['issue_count'] = len(result['issues'])
        
        if self.cache_service:
            self.cache_service.cache_result(file_path, result)
        
        return result
    
    def generate_fixes(self, file_path: Path, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate fixes for issues"""
        fixes = []
        
        content = file_path.read_text(encoding='utf-8')
        
        for issue in issues:
            issue_type = issue.get('type')
            
            strategy = self._get_strategy_for_type(issue_type)
            if strategy:
                try:
                    fix = strategy.fix(file_path, issue, content)
                    if fix:
                        fixes.append(fix)
                except Exception:
                    pass
        
        return self._prioritize_fixes(fixes)
    
    def _get_strategy_for_type(self, issue_type: str):
        """Get strategy for issue type"""
        strategy_map = {
            'naming_convention': NamingStrategy,
            'type_hint': TypeHintStrategy,
            'error_handling': ErrorHandlingStrategy,
            'docstring': DocstringStrategy,
            'import_style': ImportStrategy,
            'logical_error': LogicalErrorStrategy,
            'security': SecurityStrategy,
            'performance': PerformanceStrategy,
            'dead_code': LogicalErrorStrategy,
            'code_smell': PerformanceStrategy,
        }
        
        strategy_class = strategy_map.get(issue_type)
        if strategy_class:
            return strategy_class()
        return None
    
    def _prioritize_fixes(self, fixes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort fixes by confidence score (highest first)"""
        return sorted(fixes, key=lambda f: f.get('confidence', 0.0), reverse=True)

