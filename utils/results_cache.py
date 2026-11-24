"""
Results Cache Module
Stores query execution results in-memory for API consumption
"""
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


class ResultsCache:
    """
    In-memory cache for storing query results with TTL expiration
    """
    
    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize the cache
        
        Args:
            ttl_seconds: Time-to-live for cached results (default: 1 hour)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def store(self, 
              sql_query: str,
              results: List[Dict],
              columns: List[str],
              row_count: int,
              nl_summary: str,
              visualization: Optional[Dict] = None,
              user_query: str = "") -> str:
        """
        Store query results in cache
        
        Returns:
            result_id: Unique identifier for this result
        """
        result_id = str(uuid.uuid4())[:8]  # Short UUID
        
        self.cache[result_id] = {
            'id': result_id,
            'sql_query': sql_query,
            'results': results,
            'columns': columns,
            'row_count': row_count,
            'nl_summary': nl_summary,
            'visualization': visualization,
            'user_query': user_query,
            'timestamp': time.time(),
            'created_at': datetime.now().isoformat(),
            'analysis_status': 'ready',  # 'pending' | 'ready' | 'failed' | 'disabled'
        }
        
        # Clean expired entries
        self._cleanup_expired()
        
        return result_id
    
    def update_analysis(self, result_id: str, analysis_text: str, status: str = 'ready') -> bool:
        """Append analysis text to an existing cached result. Called by background tasks."""
        entry = self.cache.get(result_id)
        if not entry:
            return False
        if analysis_text and "🤖 **Analisis Otomatis:**" not in entry['nl_summary']:
            entry['nl_summary'] += f"\n\n🤖 **Analisis Otomatis:**\n{analysis_text}"
        entry['analysis_status'] = status
        return True

    def get(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result by ID
        
        Returns:
            result dict or None if not found/expired
        """
        if result_id not in self.cache:
            return None
        
        result = self.cache[result_id]
        
        # Check if expired
        if time.time() - result['timestamp'] > self.ttl:
            del self.cache[result_id]
            return None
        
        return result
    
    def list_recent(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List recent cached results (sorted by timestamp, newest first).

        Args:
            limit: Maximum number of entries to return.
            offset: Number of entries to skip (for pagination).

        Returns:
            List of result metadata (excluding full results data)
        """
        self._cleanup_expired()

        sorted_results = sorted(
            self.cache.values(),
            key=lambda x: x['timestamp'],
            reverse=True,
        )

        page = sorted_results[offset: offset + limit]
        return [
            {
                'id': r['id'],
                'user_query': r['user_query'],
                'sql_query': r['sql_query'][:100] + '...' if len(r['sql_query']) > 100 else r['sql_query'],
                'row_count': r['row_count'],
                'created_at': r['created_at'],
                'has_visualization': r['visualization'] is not None and r['visualization'].get('can_visualize', False),
            }
            for r in page
        ]

    def total(self) -> int:
        """Total number of non-expired entries."""
        self._cleanup_expired()
        return len(self.cache)
    
    def _cleanup_expired(self):
        """
        Remove expired entries from cache
        """
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value['timestamp'] > self.ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def clear(self):
        """
        Clear all cached results
        """
        self.cache.clear()
    
    def size(self) -> int:
        """
        Get number of cached results
        """
        self._cleanup_expired()
        return len(self.cache)
