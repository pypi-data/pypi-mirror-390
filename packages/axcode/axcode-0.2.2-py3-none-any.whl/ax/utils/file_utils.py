import os
import shutil
from pathlib import Path
from typing import List, Optional


def find_code_files(directory: str, 
                   file_extensions: List[str] = None, 
                   ignore_patterns: List[str] = None) -> List[str]:
    """
    Find all code files in a directory recursively
    
    Args:
        directory: Directory to search
        file_extensions: List of file extensions to include (e.g., ['.py', '.js', '.ts'])
        ignore_patterns: List of patterns to ignore (glob-style)
        
    Returns:
        List of code file paths
    """
    if file_extensions is None:
        # Default supported programming languages
        file_extensions = [
            '.py',      # Python
            '.js',      # JavaScript
            '.ts',      # TypeScript
            '.jsx',     # React JSX
            '.tsx',     # TypeScript JSX
            '.java',    # Java
            '.cpp',     # C++
            '.cc',      # C++
            '.cxx',     # C++
            '.c',       # C
            '.h',       # C/C++ Header
            '.hpp',     # C++ Header
            '.cs',      # C#
            '.php',     # PHP
            '.rb',      # Ruby
            '.go',      # Go
            '.rs',      # Rust
            '.swift',   # Swift
            '.kt',      # Kotlin
            '.scala',   # Scala
            '.r',       # R
            '.R',       # R
            '.m',       # Objective-C/MATLAB
            '.mm',      # Objective-C++
            '.pl',      # Perl
            '.sh',      # Shell script
            '.bash',    # Bash script
            '.zsh',     # Zsh script
            '.fish',    # Fish script
            '.ps1',     # PowerShell
            '.sql',     # SQL
            '.html',    # HTML
            '.css',     # CSS
            '.scss',    # SCSS
            '.sass',    # SASS
            '.less',    # LESS
            '.vue',     # Vue.js
            '.svelte',  # Svelte
            '.dart',    # Dart
            '.lua',     # Lua
            '.vim',     # Vim script
            '.yaml',    # YAML
            '.yml',     # YAML
            '.json',    # JSON
            '.xml',     # XML
            '.toml',    # TOML
            '.ini',     # INI
            '.cfg',     # Config
            '.conf',    # Config
        ]
    
    if ignore_patterns is None:
        ignore_patterns = [
            "__pycache__/*", 
            "*.pyc", 
            ".git/*", 
            "venv/*", 
            "env/*",
            "node_modules/*",
            ".vscode/*",
            ".idea/*",
            "build/*",
            "dist/*",
            "target/*",
            "*.min.js",
            "*.min.css",
            "package-lock.json",
            "yarn.lock",
            "Cargo.lock",
            ".DS_Store"
        ]
    
    directory_path = Path(directory)
    code_files = []
    
    # Find files with specified extensions
    for ext in file_extensions:
        pattern = f"*{ext}"
        for file_path in directory_path.rglob(pattern):
            # Check if file matches any ignore pattern
            should_ignore = False
            relative_path = file_path.relative_to(directory_path)
            
            for ignore_pattern in ignore_patterns:
                if file_path.match(ignore_pattern) or str(relative_path).startswith(ignore_pattern.rstrip('/*')):
                    should_ignore = True
                    break
            
            if not should_ignore and file_path.is_file():
                code_files.append(str(file_path))
    
    return sorted(code_files)


def find_python_files(directory: str, ignore_patterns: List[str] = None) -> List[str]:
    """
    Find all Python files in a directory recursively
    
    Args:
        directory: Directory to search
        ignore_patterns: List of patterns to ignore (glob-style)
        
    Returns:
        List of Python file paths
    """
    return find_code_files(directory, ['.py'], ignore_patterns)


def ensure_directory_exists(directory: str) -> None:
    """Ensure a directory exists, create if it doesn't"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def backup_file(file_path: str, backup_suffix: str = ".ax_backup") -> str:
    """
    Create a backup of a file
    
    Args:
        file_path: Path to the file to backup
        backup_suffix: Suffix to add to backup file
        
    Returns:
        Path to the backup file
    """
    backup_path = f"{file_path}{backup_suffix}"
    shutil.copy2(file_path, backup_path)
    return backup_path


def restore_from_backup(file_path: str, backup_suffix: str = ".ax_backup") -> bool:
    """
    Restore a file from its backup
    
    Args:
        file_path: Original file path
        backup_suffix: Suffix of backup file
        
    Returns:
        True if restore was successful, False otherwise
    """
    backup_path = f"{file_path}{backup_suffix}"
    
    if not os.path.exists(backup_path):
        return False
    
    try:
        shutil.copy2(backup_path, file_path)
        return True
    except (OSError, PermissionError):
        return False


def clean_backup_files(directory: str, backup_suffix: str = ".ax_backup") -> int:
    """
    Clean up backup files in a directory
    
    Args:
        directory: Directory to clean
        backup_suffix: Suffix of backup files
        
    Returns:
        Number of backup files removed
    """
    directory_path = Path(directory)
    backup_files = list(directory_path.rglob(f"*{backup_suffix}"))
    
    removed_count = 0
    for backup_file in backup_files:
        try:
            backup_file.unlink()
            removed_count += 1
        except OSError:
            pass
    
    return removed_count


def detect_language(file_path: str) -> str:
    """
    Detect the programming language of a file based on its extension
    
    Args:
        file_path: Path to the file
        
    Returns:
        Programming language name
    """
    extension = Path(file_path).suffix.lower()
    
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'react',
        '.tsx': 'react-typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.h': 'c-header',
        '.hpp': 'cpp-header',
        '.cs': 'csharp',
        '.php': 'php',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.r': 'r',
        '.R': 'r',
        '.m': 'objective-c',
        '.mm': 'objective-cpp',
        '.pl': 'perl',
        '.sh': 'shell',
        '.bash': 'bash',
        '.zsh': 'zsh',
        '.fish': 'fish',
        '.ps1': 'powershell',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sass': 'sass',
        '.less': 'less',
        '.vue': 'vue',
        '.svelte': 'svelte',
        '.dart': 'dart',
        '.lua': 'lua',
        '.vim': 'vim',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'config',
        '.conf': 'config',
    }
    
    return language_map.get(extension, 'unknown')


def is_python_file(file_path: str) -> bool:
    """Check if a file is a Python file"""
    return file_path.endswith('.py')


def is_code_file(file_path: str) -> bool:
    """Check if a file is a code file"""
    return detect_language(file_path) != 'unknown'


def get_relative_path(file_path: str, base_path: str) -> str:
    """Get relative path from base path"""
    try:
        return str(Path(file_path).relative_to(Path(base_path)))
    except ValueError:
        return file_path


def safe_read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
    """
    Safely read a file with fallback encodings
    
    Args:
        file_path: Path to the file
        encoding: Primary encoding to try
        
    Returns:
        File content or None if reading fails
    """
    encodings_to_try = [encoding, 'utf-8', 'latin-1', 'cp1252']
    
    for enc in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, OSError):
            continue
    
    return None


def safe_write_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
    """
    Safely write content to a file
    
    Args:
        file_path: Path to the file
        content: Content to write
        encoding: Encoding to use
        
    Returns:
        True if write was successful, False otherwise
    """
    try:
        # Ensure parent directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        return True
    except (OSError, PermissionError):
        return False


def is_file_writable(file_path: str) -> bool:
    """Check if a file is writable"""
    try:
        if os.path.exists(file_path):
            return os.access(file_path, os.W_OK)
        else:
            # Check if parent directory is writable
            parent_dir = os.path.dirname(file_path) or '.'
            return os.access(parent_dir, os.W_OK)
    except OSError:
        return False