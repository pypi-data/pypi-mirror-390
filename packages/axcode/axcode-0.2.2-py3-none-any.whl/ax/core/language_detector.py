"""Language detection and support for multiple programming languages"""

from pathlib import Path
from typing import Dict, Optional
from enum import Enum


class Language(Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    GO = "go"
    RUST = "rust"
    CPP = "cpp"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    UNKNOWN = "unknown"


class LanguageDetector:
    """Detect programming language from file extension"""
    
    EXTENSION_MAP: Dict[str, Language] = {
        '.py': Language.PYTHON,
        '.pyw': Language.PYTHON,
        '.js': Language.JAVASCRIPT,
        '.jsx': Language.JAVASCRIPT,
        '.mjs': Language.JAVASCRIPT,
        '.ts': Language.TYPESCRIPT,
        '.tsx': Language.TYPESCRIPT,
        '.java': Language.JAVA,
        '.go': Language.GO,
        '.rs': Language.RUST,
        '.cpp': Language.CPP,
        '.cc': Language.CPP,
        '.cxx': Language.CPP,
        '.c': Language.CPP,
        '.h': Language.CPP,
        '.hpp': Language.CPP,
        '.cs': Language.CSHARP,
        '.php': Language.PHP,
        '.rb': Language.RUBY,
    }
    
    LANGUAGE_FEATURES: Dict[Language, Dict[str, any]] = {
        Language.PYTHON: {
            'naming': 'snake_case',
            'none_check': 'is None',
            'comment_style': '#',
            'has_semicolons': False,
            'has_braces': False,
        },
        Language.JAVASCRIPT: {
            'naming': 'camelCase',
            'none_check': '=== null',
            'comment_style': '//',
            'has_semicolons': True,
            'has_braces': True,
        },
        Language.TYPESCRIPT: {
            'naming': 'camelCase',
            'none_check': '=== null',
            'comment_style': '//',
            'has_semicolons': True,
            'has_braces': True,
            'has_types': True,
        },
        Language.JAVA: {
            'naming': 'camelCase',
            'none_check': '== null',
            'comment_style': '//',
            'has_semicolons': True,
            'has_braces': True,
        },
        Language.GO: {
            'naming': 'camelCase',
            'none_check': '== nil',
            'comment_style': '//',
            'has_semicolons': False,
            'has_braces': True,
        },
    }
    
    @staticmethod
    def detect(file_path: Path) -> Language:
        """Detect language from file extension"""
        extension = file_path.suffix.lower()
        return LanguageDetector.EXTENSION_MAP.get(extension, Language.UNKNOWN)
    
    @staticmethod
    def is_supported(file_path: Path) -> bool:
        """Check if file language is supported"""
        return LanguageDetector.detect(file_path) != Language.UNKNOWN
    
    @staticmethod
    def get_features(language: Language) -> Dict[str, any]:
        """Get language-specific features and conventions"""
        return LanguageDetector.LANGUAGE_FEATURES.get(language, {})
    
    @staticmethod
    def build_language_context(language: Language) -> str:
        """Build language-specific context for AI prompts"""
        features = LanguageDetector.get_features(language)
        
        if language == Language.PYTHON:
            return """
PYTHON-SPECIFIC RULES:
- Functions/variables: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- None checks: use 'is None', not '== None'
- Imports: standard library, third-party, local
- Type hints: encouraged for function signatures
- Docstrings: use triple quotes
"""
        elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
            return """
JAVASCRIPT/TYPESCRIPT-SPECIFIC RULES:
- Functions/variables: camelCase
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE or camelCase
- Null checks: use '=== null' or '!== null'
- Use const/let, not var
- Arrow functions for callbacks
- TypeScript: add type annotations
- Use async/await over promises
"""
        elif language == Language.JAVA:
            return """
JAVA-SPECIFIC RULES:
- Methods/variables: camelCase
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE
- Null checks: use '== null' or '!= null'
- Use Optional for nullable values
- Follow Java naming conventions
- Use interfaces for contracts
"""
        elif language == Language.GO:
            return """
GO-SPECIFIC RULES:
- Functions/variables: camelCase (exported) or lowercase (unexported)
- Types: PascalCase
- Nil checks: use '== nil' or '!= nil'
- Error handling: return error as last value
- Use defer for cleanup
- No exceptions, use errors
"""
        else:
            return f"Language: {language.value}"

