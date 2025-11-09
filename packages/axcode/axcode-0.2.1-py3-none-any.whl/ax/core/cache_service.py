import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from ..utils.hash_utils import calculate_file_hash


class CacheService:
    
    def __init__(self, cache_dir: str = ".ax_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_index_file = self.cache_dir / "index.json"
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict[str, Any]:
        """Load cache index from disk"""
        if self.cache_index_file.exists():
            try:
                with open(self.cache_index_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        try:
            with open(self.cache_index_file, 'w') as f:
                json.dump(self.cache_index, f, indent=2)
        except Exception:
            pass
    
    def get_cached_result(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get cached analysis result for a file"""
        file_hash = calculate_file_hash(str(file_path))
        
        if not file_hash:
            return None
        
        cache_key = str(file_path)
        
        if cache_key in self.cache_index:
            cached_entry = self.cache_index[cache_key]
            
            if cached_entry.get('file_hash') == file_hash:
                cache_file = self.cache_dir / f"{cached_entry['cache_id']}.json"
                
                if cache_file.exists():
                    try:
                        with open(cache_file, 'r') as f:
                            return json.load(f)
                    except Exception:
                        return None
        
        return None
    
    def cache_result(self, file_path: Path, result: Dict[str, Any]):
        """Cache analysis result for a file"""
        file_hash = calculate_file_hash(str(file_path))
        
        if not file_hash:
            return
        
        cache_key = str(file_path)
        cache_id = file_hash[:16]
        
        self.cache_index[cache_key] = {
            'file_hash': file_hash,
            'cache_id': cache_id,
            'timestamp': datetime.now().isoformat()
        }
        
        cache_file = self.cache_dir / f"{cache_id}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass
        
        self._save_cache_index()
    
    def invalidate_cache(self, file_path: Path):
        """Invalidate cache for a file"""
        cache_key = str(file_path)
        
        if cache_key in self.cache_index:
            cached_entry = self.cache_index[cache_key]
            cache_file = self.cache_dir / f"{cached_entry['cache_id']}.json"
            
            if cache_file.exists():
                try:
                    cache_file.unlink()
                except Exception:
                    pass
            
            del self.cache_index[cache_key]
            self._save_cache_index()
    
    def clear_cache(self):
        """Clear all cached results"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file != self.cache_index_file:
                    cache_file.unlink()
            
            self.cache_index = {}
            self._save_cache_index()
        except Exception:
            pass

