import ast
from typing import Optional, Dict, Any
from pathlib import Path


class ASTParser:
    
    @staticmethod
    def parse_file(file_path: Path) -> Optional[ast.AST]:
        """Parse a Python file into an AST"""
        try:
            content = file_path.read_text(encoding='utf-8')
            return ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def parse_string(content: str, filename: str = '<string>') -> Optional[ast.AST]:
        """Parse a Python string into an AST"""
        try:
            return ast.parse(content, filename=filename)
        except SyntaxError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def check_syntax(file_path: Path) -> Dict[str, Any]:
        """Check if a file has syntax errors"""
        try:
            content = file_path.read_text(encoding='utf-8')
            ast.parse(content, filename=str(file_path))
            return {'valid': True, 'errors': []}
        except SyntaxError as e:
            return {
                'valid': False,
                'errors': [{
                    'line': e.lineno,
                    'column': e.offset or 0,
                    'message': e.msg,
                    'text': e.text
                }]
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [{
                    'line': 0,
                    'column': 0,
                    'message': str(e),
                    'text': ''
                }]
            }
    
    @staticmethod
    def fix_syntax_errors(file_path: Path, content: str, interactive: bool = True) -> Dict[str, Any]:
        """Attempt to fix common syntax errors, with interactive fallback"""
        fixed_content = content
        all_changes = []
        max_iterations = 10  # Prevent infinite loops
        
        for iteration in range(max_iterations):
            result = ASTParser.check_syntax_string(fixed_content)
            
            if result['valid']:
                return {
                    'fixed': len(all_changes) > 0,
                    'content': fixed_content,
                    'changes': all_changes,
                    'needs_manual': False
                }
            
            lines = fixed_content.split('\n')
            made_change = False
            
            for error in result['errors']:
                line_num = error['line']
                message = error['message']
                
                if line_num > 0 and line_num <= len(lines):
                    line = lines[line_num - 1]
                    original_line = line
                    
                    if "was never closed" in message or "closing parenthesis" in message or "unclosed" in message.lower():
                        if '[' in message or "'['" in message or ('[' in line and line.count('[') > line.count(']')):
                            line = line.rstrip() + ']'
                            all_changes.append(f"Line {line_num}: Added missing closing bracket ']'")
                            made_change = True
                        elif '(' in message or "'('" in message or ('(' in line and line.count('(') > line.count(')')):
                            line = line.rstrip() + ')'
                            all_changes.append(f"Line {line_num}: Added missing closing parenthesis ')'")
                            made_change = True
                        elif '{' in message or "'{'" in message or ('{' in line and line.count('{') > line.count('}')):
                            line = line.rstrip() + '}'
                            all_changes.append(f"Line {line_num}: Added missing closing brace '}}'")
                            made_change = True
                    
                    elif "expected ':'" in message.lower() or message.endswith("expected ':'"):
                        if line.strip().startswith(('def ', 'class ', 'if ', 'for ', 'while ', 'elif ', 'else', 'try', 'except', 'finally', 'with')):
                            line = line.rstrip() + ':'
                            all_changes.append(f"Line {line_num}: Added missing colon ':'")
                            made_change = True
                    
                    if line != original_line:
                        lines[line_num - 1] = line
            
            fixed_content = '\n'.join(lines)
            
            if not made_change:
                break
        
        is_fixed = ASTParser.check_syntax_string(fixed_content)['valid']
        
        return {
            'fixed': is_fixed,
            'content': fixed_content if is_fixed else content,
            'changes': all_changes if is_fixed else [],
            'needs_manual': not is_fixed and interactive,
            'errors': ASTParser.check_syntax_string(fixed_content if not is_fixed else content)['errors']
        }
    
    @staticmethod
    def check_syntax_string(content: str) -> Dict[str, Any]:
        """Check if a string has syntax errors"""
        try:
            ast.parse(content)
            return {'valid': True, 'errors': []}
        except SyntaxError as e:
            return {
                'valid': False,
                'errors': [{
                    'line': e.lineno,
                    'column': e.offset or 0,
                    'message': e.msg,
                    'text': e.text
                }]
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [{
                    'line': 0,
                    'column': 0,
                    'message': str(e),
                    'text': ''
                }]
            }

