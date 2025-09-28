import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import hashlib
import time

class CacheManager:
    """Simple caching system for performance optimization"""
    
    def __init__(self, cache_dir: str = "app/data/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, data: Any) -> str:
        """Generate a cache key from data"""
        if isinstance(data, str):
            key_data = data
        elif isinstance(data, dict):
            key_data = json.dumps(data, sort_keys=True)
        else:
            key_data = str(data)
        
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path for a key"""
        return self.cache_dir / f"{key}.json"
    
    def get(self, key: str, max_age_seconds: int = 3600) -> Optional[Any]:
        """Get cached data if it exists and is not expired"""
        cache_file = self._get_cache_file(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cache_time = cache_data.get('timestamp', 0)
            if time.time() - cache_time > max_age_seconds:
                cache_file.unlink()  # Remove expired cache
                return None
            
            return cache_data.get('data')
        
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            cache_file.unlink()  # Remove corrupted cache
            return None
    
    def set(self, key: str, data: Any) -> None:
        """Cache data with timestamp"""
        cache_file = self._get_cache_file(key)
        
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            # If caching fails, just continue without caching
            pass
    
    def clear(self, pattern: str = "*") -> None:
        """Clear cache files matching pattern"""
        for cache_file in self.cache_dir.glob(f"{pattern}.json"):
            try:
                cache_file.unlink()
            except Exception:
                pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        
        total_files = len(cache_files)
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': total_size / (1024 * 1024)
        }

# Global cache manager instance
cache_manager = CacheManager()

def cached_dataframe(key: str, max_age_seconds: int = 3600):
    """Decorator to cache DataFrame operations"""
    def decorator(func):
        @st.cache_data(ttl=max_age_seconds)
        def wrapper(*args, **kwargs):
            cache_key = f"{key}_{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache first
            cached_result = cache_manager.get(cache_key, max_age_seconds)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result
        
        return wrapper
    return decorator

def cache_validation_results(file_path: str, rules_hash: str):
    """Cache validation results for a file with specific rules"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = f"validation_{hashlib.md5(f'{file_path}_{rules_hash}'.encode()).hexdigest()}"
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key, max_age_seconds=1800)  # 30 minutes
            if cached_result is not None:
                return cached_result
            
            # Execute validation and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result
        
        return wrapper
    return decorator

def clear_validation_cache():
    """Clear validation cache"""
    cache_manager.clear("validation_*")

def get_cache_info() -> Dict[str, Any]:
    """Get information about cache usage"""
    return cache_manager.get_stats()

# Streamlit-specific caching functions
@st.cache_data(ttl=300)  # 5 minutes
def load_rules_cached(rules_path: str) -> Dict[str, Any]:
    """Cached version of rules loading"""
    with open(rules_path, 'r') as f:
        return json.load(f)

@st.cache_data(ttl=600)  # 10 minutes
def load_validation_reports_cached(report_path: str) -> List[Dict[str, Any]]:
    """Cached version of validation reports loading"""
    if not Path(report_path).exists():
        return []
    
    rows = []
    with open(report_path, 'r') as f:
        for line in f:
            try:
                rows.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    return rows

@st.cache_data(ttl=1800)  # 30 minutes
def get_user_activity_summary_cached(username: str) -> Dict[str, Any]:
    """Cached version of user activity summary"""
    from core.audit_logger import audit_logger
    return audit_logger.get_user_activity_summary(username)
