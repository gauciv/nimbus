"""
Simple response caching to reduce API calls and improve speed.
"""
import json
import hashlib
from typing import Optional
from datetime import datetime, timedelta

class ResponseCache:
    def __init__(self, cache_file='data/response_cache.json'):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
    
    def _load_cache(self) -> dict:
        """Load cache from file."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except:
            pass
    
    def _get_cache_key(self, question: str) -> str:
        """Generate cache key from question."""
        normalized = question.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_cached_response(self, question: str) -> Optional[str]:
        """Get cached response if available and not expired."""
        cache_key = self._get_cache_key(question)
        
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data['response']
            else:
                # Remove expired cache
                del self.cache[cache_key]
                self._save_cache()
        
        return None
    
    def cache_response(self, question: str, response: str):
        """Cache a response."""
        cache_key = self._get_cache_key(question)
        
        self.cache[cache_key] = {
            'response': response,
            'timestamp': datetime.now().isoformat()
        }
        
        # Keep only last 100 entries to prevent unlimited growth
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
        
        self._save_cache()