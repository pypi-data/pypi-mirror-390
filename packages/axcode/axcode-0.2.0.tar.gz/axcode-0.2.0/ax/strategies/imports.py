import ast
from typing import List, Dict, Any
from pathlib import Path
from .base import ConsistencyStrategy


class ImportStrategy(ConsistencyStrategy):
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        issues = []
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        if len(imports) > 1:
            sorted_imports = sorted(imports, key=lambda x: x.lineno)
            
            stdlib_imports = []
            third_party_imports = []
            local_imports = []
            
            for imp in sorted_imports:
                if isinstance(imp, ast.ImportFrom):
                    module = imp.module or ''
                    if module.startswith('.'):
                        local_imports.append(imp)
                    elif self._is_stdlib(module):
                        stdlib_imports.append(imp)
                    else:
                        third_party_imports.append(imp)
        
        return issues
    
    def _is_stdlib(self, module: str) -> bool:
        stdlib_modules = {
            'os', 'sys', 'json', 'ast', 're', 'typing', 'pathlib', 
            'datetime', 'collections', 'itertools', 'functools'
        }
        first_part = module.split('.')[0]
        return first_part in stdlib_modules
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        return None

