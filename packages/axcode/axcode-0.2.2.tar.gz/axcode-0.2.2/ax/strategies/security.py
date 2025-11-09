from typing import List, Dict, Any
from pathlib import Path
import ast
import re
from .base import ConsistencyStrategy


class SecurityStrategy(ConsistencyStrategy):
    """Detect security vulnerabilities and issues"""
    
    def __init__(self):
        super().__init__()
        
        # Expanded patterns for security issues
        self.hardcoded_secret_patterns = [
            # Generic secrets
            r'password\s*=\s*["\'][^"\']+["\']',
            r'passwd\s*=\s*["\'][^"\']+["\']',
            r'pwd\s*=\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            
            # AWS credentials
            r'aws[_-]?secret\s*=\s*["\'][^"\']+["\']',
            r'aws[_-]?access[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'["\']AKIA[0-9A-Z]{16}["\']',  # AWS Access Key
            
            # GitHub tokens
            r'gh[ps]_[a-zA-Z0-9]{36}',  # GitHub Personal/Secret token
            r'github[_-]?token\s*=\s*["\'][^"\']+["\']',
            
            # OpenAI/Anthropic API keys
            r'sk-[a-zA-Z0-9\-_]{20,}',  # OpenAI API key (various formats)
            r'sk-ant-[a-zA-Z0-9\-]{95,}',  # Anthropic API key
            r'sk-proj-[a-zA-Z0-9\-_]{20,}',  # OpenAI project key
            
            # Generic API keys and tokens
            r'bearer\s+[a-zA-Z0-9\-._~+/]+=*',
            r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9\-_]{16,}["\']',
            r'["\']?access[_-]?token["\']?\s*[:=]\s*["\'][a-zA-Z0-9\-_]{16,}["\']',
            
            # Stripe keys
            r'sk_live_[a-zA-Z0-9]{24,}',
            r'pk_live_[a-zA-Z0-9]{24,}',
            r'sk_test_[a-zA-Z0-9]{24,}',
            
            # Slack tokens
            r'xox[baprs]-[a-zA-Z0-9\-]{10,}',
            
            # Google API keys
            r'AIza[a-zA-Z0-9\-_]{35}',
            
            # Firebase
            r'AAAA[a-zA-Z0-9\-_:]{7,}',
            
            # Database credentials
            r'db[_-]?password\s*=\s*["\'][^"\']+["\']',
            r'database[_-]?password\s*=\s*["\'][^"\']+["\']',
            r'mysql[_-]?password\s*=\s*["\'][^"\']+["\']',
            r'postgres[_-]?password\s*=\s*["\'][^"\']+["\']',
            
            # Private keys
            r'private[_-]?key\s*=\s*["\'][^"\']+["\']',
            r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----',
            
            # JWT tokens
            r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*',
            
            # Connection strings
            r'mongodb(\+srv)?://[^:]+:[^@]+@',
            r'postgresql://[^:]+:[^@]+@',
            r'mysql://[^:]+:[^@]+@',
        ]
        
        # Keywords that suggest secrets
        self.secret_keywords = [
            'password', 'passwd', 'pwd', 'api_key', 'apikey', 'secret', 
            'token', 'auth', 'credential', 'private_key', 'secret_key',
            'access_key', 'encryption_key', 'oauth', 'jwt',
            # Provider-specific keywords
            'openai', 'anthropic', 'aws', 'azure', 'gcp', 'github',
            'stripe', 'twilio', 'sendgrid', 'firebase', 'supabase',
            # Additional secret-related keywords
            'bearer', 'session', 'cookie', 'csrf'
        ]
    
    def analyze(self, file_path: Path, tree: ast.AST, file_content: str, project_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect security issues in code"""
        issues = []
        
        # Check for hardcoded secrets
        issues.extend(self._check_hardcoded_secrets(tree, file_content))
        
        # Check for SQL injection risks
        issues.extend(self._check_sql_injection(tree, file_content))
        
        # Check for command injection risks
        issues.extend(self._check_command_injection(tree, file_content))
        
        # Check for unsafe file operations
        issues.extend(self._check_unsafe_file_ops(tree, file_content))
        
        # Check for unsafe deserialization
        issues.extend(self._check_unsafe_deserialization(tree, file_content))
        
        # Check for weak crypto
        issues.extend(self._check_weak_crypto(tree, file_content))
        
        # Check for unsafe eval/exec
        issues.extend(self._check_eval_exec(tree, file_content))
        
        # Check for path traversal vulnerabilities
        issues.extend(self._check_path_traversal(tree, file_content))
        
        # Check for insecure random number generation
        issues.extend(self._check_insecure_random(tree, file_content))
        
        # Check for empty except blocks
        issues.extend(self._check_empty_except(tree, file_content))
        
        # NEW: Check for hardcoded IPs and URLs
        issues.extend(self._check_hardcoded_urls(tree, file_content))
        
        # NEW: Check for sensitive data in logs
        issues.extend(self._check_sensitive_logging(tree, file_content))
        
        # NEW: Check for unsafe yaml.load
        issues.extend(self._check_unsafe_yaml(tree, file_content))
        
        # NEW: Check for shell=True with user input
        issues.extend(self._check_shell_injection_advanced(tree, file_content))
        
        return issues
    
    def _check_hardcoded_secrets(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect hardcoded passwords, API keys, and secrets"""
        issues = []
        
        # Check AST for suspicious variable assignments
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id.lower()
                        
                        # Check if variable name suggests a secret
                        if any(keyword in var_name for keyword in self.secret_keywords):
                            # Check if assigned a string literal
                            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                                # Exclude common placeholders
                                value = node.value.value
                                if value and value not in ['', 'YOUR_API_KEY', 'YOUR_PASSWORD', 'TODO', 'PLACEHOLDER', 'CHANGE_ME']:
                                    # Additional check: if value looks like a real secret (length > 8)
                                    if len(value) > 8:
                                        issues.append({
                                            'line': node.lineno,
                                            'column': node.col_offset,
                                            'severity': 'error',
                                            'type': 'security',
                                            'message': f"Hardcoded secret detected: '{target.id}'. Use environment variables instead",
                                            'suggestion': f"Replace with: {target.id} = os.getenv('{target.id.upper()}')",
                                            'fixable': True
                                        })
        
        # Check content using regex patterns for various secret formats
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith('#'):
                continue
            
            # Check each pattern
            for pattern in self.hardcoded_secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Check if it's not already flagged by AST check
                    already_flagged = any(issue['line'] == line_num for issue in issues)
                    if not already_flagged:
                        issues.append({
                            'line': line_num,
                            'column': 0,
                            'severity': 'error',
                            'type': 'security',
                            'message': f"Potential hardcoded secret or credential detected",
                            'suggestion': 'Use environment variables or a secure secret management system',
                            'fixable': False
                        })
                    break  # Only flag once per line
        
        return issues
    
    def _check_sql_injection(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential SQL injection vulnerabilities"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for string formatting in SQL queries
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['execute', 'executemany', 'raw']:
                        if node.args:
                            query_arg = node.args[0]
                            
                            # Check for f-strings
                            if isinstance(query_arg, ast.JoinedStr):
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'error',
                                    'type': 'security',
                                    'message': 'Potential SQL injection: using f-string in SQL query',
                                    'suggestion': 'Use parameterized queries instead',
                                    'fixable': False
                                })
                            
                            # Check for .format() or % formatting
                            elif isinstance(query_arg, ast.Call):
                                if isinstance(query_arg.func, ast.Attribute) and query_arg.func.attr == 'format':
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'error',
                                        'type': 'security',
                                        'message': 'Potential SQL injection: using .format() in SQL query',
                                        'suggestion': 'Use parameterized queries instead',
                                        'fixable': False
                                    })
                            
                            elif isinstance(query_arg, ast.BinOp) and isinstance(query_arg.op, ast.Mod):
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'error',
                                    'type': 'security',
                                    'message': 'Potential SQL injection: using % formatting in SQL query',
                                    'suggestion': 'Use parameterized queries instead',
                                    'fixable': False
                                })
        
        return issues
    
    def _check_command_injection(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential command injection vulnerabilities"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for unsafe shell command execution
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['system', 'popen', 'popen2', 'popen3', 'popen4']:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': f"Command injection risk with os.{node.func.attr}()",
                            'suggestion': 'Use subprocess.run() with shell=False and a list of arguments',
                            'fixable': False
                        })
                    
                    # Check for subprocess with shell=True
                    elif node.func.attr in ['run', 'call', 'Popen'] and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'subprocess':
                            # Check for shell=True in keywords
                            for keyword in node.keywords:
                                if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                                    if keyword.value.value is True:
                                        issues.append({
                                            'line': node.lineno,
                                            'column': node.col_offset,
                                            'severity': 'error',
                                            'type': 'security',
                                            'message': 'subprocess with shell=True is vulnerable to command injection',
                                            'suggestion': 'Use shell=False and pass command as a list',
                                            'fixable': False
                                        })
                
                elif isinstance(node.func, ast.Name):
                    if node.func.id == 'eval':
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': 'eval() is dangerous and can execute arbitrary code',
                            'suggestion': 'Use ast.literal_eval() for safe evaluation of literals',
                            'fixable': False
                        })
                    
                    elif node.func.id == 'exec':
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': 'exec() is dangerous and can execute arbitrary code',
                            'suggestion': 'Avoid dynamic code execution',
                            'fixable': False
                        })
                    
                    elif node.func.id == 'compile':
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'security',
                            'message': 'compile() can be dangerous if used with untrusted input',
                            'suggestion': 'Validate and sanitize all input before compiling',
                            'fixable': False
                        })
                    
                    elif node.func.id == '__import__':
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'security',
                            'message': '__import__() can be dangerous with untrusted input',
                            'suggestion': 'Use importlib.import_module() with proper validation',
                            'fixable': False
                        })
        
        return issues
    
    def _check_unsafe_file_ops(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unsafe file operations"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Check for missing encoding
                    has_encoding = any(
                        isinstance(kw, ast.keyword) and kw.arg == 'encoding'
                        for kw in node.keywords
                    )
                    
                    if not has_encoding:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'info',
                            'type': 'security',
                            'message': 'File opened without explicit encoding',
                            'suggestion': "Use encoding='utf-8' for consistent behavior",
                            'fixable': True
                        })
        
        return issues
    
    def _check_unsafe_deserialization(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unsafe deserialization"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for pickle.loads or pickle.load
                    if node.func.attr in ['load', 'loads']:
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'pickle':
                            issues.append({
                                'line': node.lineno,
                                'column': node.col_offset,
                                'severity': 'warning',
                                'type': 'security',
                                'message': 'Unsafe deserialization with pickle can execute arbitrary code',
                                'suggestion': 'Only unpickle data from trusted sources, or use JSON instead',
                                'fixable': False
                            })
        
        return issues
    
    def _check_weak_crypto(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect weak cryptography"""
        issues = []
        
        weak_hash_algorithms = ['md5', 'sha1']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'new' and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == 'hashlib':
                            # Check first argument for algorithm name
                            if node.args and isinstance(node.args[0], ast.Constant):
                                algo = node.args[0].value
                                if algo in weak_hash_algorithms:
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'warning',
                                        'type': 'security',
                                        'message': f"Weak cryptographic algorithm '{algo}' detected",
                                        'suggestion': 'Use SHA-256 or better',
                                        'fixable': False
                                    })
                
                elif isinstance(node.func, ast.Name):
                    if node.func.id in weak_hash_algorithms:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'warning',
                            'type': 'security',
                            'message': f"Weak cryptographic algorithm '{node.func.id}' detected",
                            'suggestion': 'Use SHA-256 or better',
                            'fixable': False
                        })
        
        return issues
    
    def _check_eval_exec(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect eval/exec usage"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['eval', 'exec', '__import__']:
                        issues.append({
                            'line': node.lineno,
                            'column': node.col_offset,
                            'severity': 'error',
                            'type': 'security',
                            'message': f"Dangerous function '{node.func.id}()' can execute arbitrary code",
                            'suggestion': 'Avoid dynamic code execution or use safer alternatives',
                            'fixable': False
                        })
        
        return issues
    
    def _check_path_traversal(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect potential path traversal vulnerabilities"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for file operations with unsanitized paths
                if isinstance(node.func, ast.Name) and node.func.id == 'open':
                    # Check if the path argument contains user input patterns
                    if node.args:
                        arg = node.args[0]
                        # Check for f-strings or format operations that might contain user input
                        if isinstance(arg, (ast.JoinedStr, ast.Call)):
                            issues.append({
                                'line': node.lineno,
                                'column': node.col_offset,
                                'severity': 'warning',
                                'type': 'security',
                                'message': 'Potential path traversal vulnerability: validate file paths',
                                'suggestion': 'Sanitize and validate file paths to prevent directory traversal attacks',
                                'fixable': False
                            })
        
        return issues
    
    def _check_insecure_random(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect insecure random number generation for security purposes"""
        issues = []
        
        # Check for random module usage with security-sensitive variable names
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for random.* calls in security contexts
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'random':
                        if node.func.attr in ['random', 'randint', 'choice', 'randrange']:
                            # Try to determine context by looking at assignment
                            parent_assign = self._find_parent_assignment(node, tree)
                            if parent_assign:
                                var_name = self._get_assignment_target_name(parent_assign)
                                if var_name and any(keyword in var_name.lower() for keyword in 
                                                   ['token', 'secret', 'key', 'password', 'nonce', 'salt']):
                                    issues.append({
                                        'line': node.lineno,
                                        'column': node.col_offset,
                                        'severity': 'error',
                                        'type': 'security',
                                        'message': f"Insecure random number generation for security-sensitive value '{var_name}'",
                                        'suggestion': 'Use secrets module for cryptographically secure random numbers',
                                        'fixable': False
                                    })
        
        return issues
    
    def _check_empty_except(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect empty except blocks that silently swallow exceptions"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for handler in node.handlers:
                    # Check if handler body is empty or just 'pass'
                    if len(handler.body) == 1 and isinstance(handler.body[0], ast.Pass):
                        # Check if catching all exceptions
                        if handler.type is None:
                            issues.append({
                                'line': handler.lineno,
                                'column': handler.col_offset,
                                'severity': 'warning',
                                'type': 'security',
                                'message': 'Empty except block silently swallows all exceptions',
                                'suggestion': 'Either handle specific exceptions or at least log the error',
                                'fixable': False
                            })
                        else:
                            issues.append({
                                'line': handler.lineno,
                                'column': handler.col_offset,
                                'severity': 'info',
                                'type': 'security',
                                'message': 'Empty except block silently swallows exceptions',
                                'suggestion': 'Add proper error handling or logging',
                                'fixable': False
                            })
        
        return issues
    
    def _find_parent_assignment(self, node: ast.AST, tree: ast.AST) -> ast.Assign:
        """Helper to find parent assignment for a node"""
        for parent in ast.walk(tree):
            if isinstance(parent, ast.Assign):
                if node in ast.walk(parent.value):
                    return parent
        return None
    
    def _get_assignment_target_name(self, assign: ast.Assign) -> str:
        """Helper to get variable name from assignment"""
        if assign.targets:
            target = assign.targets[0]
            if isinstance(target, ast.Name):
                return target.id
        return None
    
    def _check_hardcoded_urls(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect hardcoded URLs and IP addresses"""
        issues = []
        
        # Patterns for URLs and IPs
        url_patterns = [
            r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            r'ftp://[a-zA-Z0-9.-]+',
            r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',  # IP addresses
        ]
        
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Skip comments and strings that are obviously examples
            if 'example.com' in line.lower() or 'localhost' in line.lower():
                continue
            if line.strip().startswith('#'):
                continue
                
            for pattern in url_patterns:
                matches = re.findall(pattern, line)
                if matches:
                    # Check if it's in a string assignment
                    if '=' in line and ('"' in line or "'" in line):
                        issues.append({
                            'line': line_num,
                            'column': 0,
                            'severity': 'warning',
                            'type': 'security',
                            'message': 'Hardcoded URL/IP address detected - consider using configuration',
                            'suggestion': 'Use environment variables or config files for URLs and IPs',
                            'fixable': False
                        })
                        break
        
        return issues
    
    def _check_sensitive_logging(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect logging of sensitive information"""
        issues = []
        
        sensitive_keywords = ['password', 'token', 'secret', 'api_key', 'private_key']
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Check for logging calls
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['debug', 'info', 'warning', 'error', 'critical', 'log']:
                        # Check if logging sensitive data
                        for arg in node.args:
                            # Check f-strings with sensitive variables
                            if isinstance(arg, ast.JoinedStr):
                                for value in arg.values:
                                    if isinstance(value, ast.FormattedValue):
                                        if isinstance(value.value, ast.Name):
                                            var_name = value.value.id.lower()
                                            if any(kw in var_name for kw in sensitive_keywords):
                                                issues.append({
                                                    'line': node.lineno,
                                                    'column': node.col_offset,
                                                    'severity': 'warning',
                                                    'type': 'security',
                                                    'message': f'Logging sensitive variable "{value.value.id}" - potential data leak',
                                                    'suggestion': 'Avoid logging passwords, tokens, or other secrets',
                                                    'fixable': False
                                                })
        
        return issues
    
    def _check_unsafe_yaml(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Detect unsafe yaml.load() usage"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check for yaml.load without Loader
                    if node.func.attr == 'load':
                        if isinstance(node.func.value, ast.Name) and node.func.value.id == 'yaml':
                            # Check if Loader argument is present
                            has_safe_loader = False
                            for keyword in node.keywords:
                                if keyword.arg == 'Loader':
                                    has_safe_loader = True
                                    break
                            
                            if not has_safe_loader:
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'error',
                                    'type': 'security',
                                    'message': 'Unsafe yaml.load() without Loader parameter - can execute arbitrary code',
                                    'suggestion': 'Use yaml.safe_load() or yaml.load(data, Loader=yaml.SafeLoader)',
                                    'fixable': False
                                })
        
        return issues
    
    def _check_shell_injection_advanced(self, tree: ast.AST, content: str) -> List[Dict[str, Any]]:
        """Advanced check for shell injection with user input patterns"""
        issues = []
        
        # Track variables that might contain user input
        user_input_vars = set()
        
        for node in ast.walk(tree):
            # Identify potential user input
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['input', 'raw_input']:
                        # Track the variable this is assigned to
                        parent = self._find_parent_assignment(node, tree)
                        if parent:
                            var_name = self._get_assignment_target_name(parent)
                            if var_name:
                                user_input_vars.add(var_name)
                
                # Check if user input used in shell commands
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['system', 'popen']:
                        for arg in node.args:
                            if self._contains_variable(arg, user_input_vars):
                                issues.append({
                                    'line': node.lineno,
                                    'column': node.col_offset,
                                    'severity': 'error',
                                    'type': 'security',
                                    'message': 'Shell command with user input - critical injection risk',
                                    'suggestion': 'Never use user input directly in shell commands',
                                    'fixable': False
                                })
        
        return issues
    
    def _contains_variable(self, node: ast.AST, var_names: set) -> bool:
        """Check if an AST node contains any of the specified variables"""
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id in var_names:
                return True
        return False
    
    def fix(self, file_path: Path, issue: Dict[str, Any], file_content: str) -> Dict[str, Any]:
        """Generate fix for security issues where possible"""
        
        if not issue.get('fixable', False):
            return {}
        
        lines = file_content.split('\n')
        line_idx = issue['line'] - 1
        
        if line_idx >= len(lines):
            return {}
        
        original_line = lines[line_idx]
        
        # Fix hardcoded secrets
        if 'Hardcoded secret' in issue.get('message', ''):
            match = re.search(r"(\w+)\s*=\s*['\"]([^'\"]+)['\"]", original_line)
            if match:
                var_name = match.group(1)
                indent = len(original_line) - len(original_line.lstrip())
                fixed_line = ' ' * indent + f"{var_name} = os.getenv('{var_name.upper()}')"
                
                return {
                    'line_number': issue['line'],
                    'original_line': original_line,
                    'fixed_line': fixed_line,
                    'description': f"Changed to use environment variable",
                    'confidence': 0.90
                }
        
        # Fix missing encoding in file operations
        if 'without explicit encoding' in issue.get('message', ''):
            if 'open(' in original_line and 'encoding=' not in original_line:
                # Add encoding parameter
                fixed_line = original_line.replace('open(', 'open(', 1)
                # Find the closing parenthesis
                close_paren = original_line.rfind(')')
                if close_paren > 0:
                    before_paren = original_line[:close_paren]
                    after_paren = original_line[close_paren:]
                    
                    # Check if there are other parameters
                    if before_paren.count(',') > 0:
                        fixed_line = before_paren + ", encoding='utf-8'" + after_paren
                    else:
                        # Only filename parameter
                        parts = before_paren.split('open(', 1)
                        if len(parts) == 2:
                            fixed_line = parts[0] + 'open(' + parts[1] + ", encoding='utf-8'" + after_paren
                
                return {
                    'line_number': issue['line'],
                    'original_line': original_line,
                    'fixed_line': fixed_line,
                    'description': "Added encoding='utf-8' parameter",
                    'confidence': 0.85
                }
        
        return {}

