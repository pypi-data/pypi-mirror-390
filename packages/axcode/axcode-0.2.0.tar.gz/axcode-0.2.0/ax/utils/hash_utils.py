import hashlib
from typing import Any, Dict


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA256 hash of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hexadecimal hash string
    """
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256()
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                file_hash.update(chunk)
            return file_hash.hexdigest()
    except (OSError, PermissionError):
        return ""


def calculate_string_hash(content: str) -> str:
    """
    Calculate SHA256 hash of a string
    
    Args:
        content: String content to hash
        
    Returns:
        Hexadecimal hash string
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def calculate_dict_hash(data: Dict[str, Any]) -> str:
    """
    Calculate hash of a dictionary (for caching purposes)
    
    Args:
        data: Dictionary to hash
        
    Returns:
        Hexadecimal hash string
    """
    # Convert dict to sorted string representation for consistent hashing
    import json
    
    def sort_dict(obj):
        if isinstance(obj, dict):
            return {k: sort_dict(v) for k, v in sorted(obj.items())}
        elif isinstance(obj, list):
            return [sort_dict(item) for item in obj]
        else:
            return obj
    
    sorted_data = sort_dict(data)
    json_string = json.dumps(sorted_data, sort_keys=True, separators=(',', ':'))
    return calculate_string_hash(json_string)


def short_hash(hash_string: str, length: int = 8) -> str:
    """
    Get a short version of a hash for display purposes
    
    Args:
        hash_string: Full hash string
        length: Length of short hash
        
    Returns:
        Shortened hash string
    """
    return hash_string[:length] if hash_string else ""


def compare_file_hashes(file1: str, file2: str) -> bool:
    """
    Compare if two files have the same content by comparing their hashes
    
    Args:
        file1: Path to first file
        file2: Path to second file
        
    Returns:
        True if files have same content, False otherwise
    """
    hash1 = calculate_file_hash(file1)
    hash2 = calculate_file_hash(file2)
    
    return hash1 and hash2 and hash1 == hash2