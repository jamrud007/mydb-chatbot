"""
Cache Manager with Auto-Detection and Fallback
Manages cache backend selection and provides unified API
"""
import hashlib
import logging
from typing import Optional, Dict, List, Any

from .cache_interface import CacheInterface
from .sqlite_cache import SQLiteCache

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Central cache manager with auto-backend selection
    
    Automatically selects:
    1. Redis (if available and configured)
    2. SQLite (fallback, default)
    
    Provides unified API for all cache operations
    """
    
    def __init__(self, 
                 backend: str = 'sqlite',
                 sqlite_path: str = './data/cache.db',
                 sqlite_max_size_mb: int = 500,
                 redis_url: Optional[str] = None,
                 redis_max_connections: int = 10,
                 default_ttl: int = 604800,
                 enabled: bool = True):
        """
        Initialize cache manager
        
        Args:
            backend: 'sqlite' or 'redis'
            sqlite_path: Path to SQLite database
            sqlite_max_size_mb: Maximum SQLite database size
            redis_url: Redis connection URL
            redis_max_connections: Redis connection pool size
            default_ttl: Default time to live in seconds (7 days)
            enabled: Enable/disable caching
        """
        self.backend_type = backend
        self.default_ttl = default_ttl
        self.enabled = enabled
        self.cache: Optional[CacheInterface] = None
        
        if not enabled:
            logger.info("Cache is disabled")
            return
        
        # Try to initialize requested backend
        if backend == 'redis' and redis_url:
            try:
                from .redis_cache import RedisCache
                self.cache = RedisCache(redis_url, redis_max_connections)
                logger.info("✓ Redis cache initialized")
            except ImportError:
                logger.warning("Redis library not installed. Install with: pip install redis")
                logger.info("Falling back to SQLite cache...")
                self.cache = SQLiteCache(sqlite_path, sqlite_max_size_mb)
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                logger.info("Falling back to SQLite cache...")
                self.cache = SQLiteCache(sqlite_path, sqlite_max_size_mb)
        else:
            # Default to SQLite
            self.cache = SQLiteCache(sqlite_path, sqlite_max_size_mb)
            logger.info("✓ SQLite cache initialized")
    
    @staticmethod
    def generate_cache_key(sql_query: str) -> str:
        """
        Generate cache key from SQL query
        
        Args:
            sql_query: SQL query string
        
        Returns:
            MD5 hash of normalized query
        """
        # Normalize query (remove extra whitespace, lowercase)
        normalized = ' '.join(sql_query.strip().lower().split())
        
        # Generate MD5 hash
        hash_object = hashlib.md5(normalized.encode())
        return hash_object.hexdigest()
    
    def cache_query_result(self, 
                          sql_query: str, 
                          results: List[Dict], 
                          columns: List[str], 
                          user_id: str = 'unknown',
                          summary: str = '',
                          user_question: str = '',
                          analysis: str = '',
                          summary_analysis: str = '',
                          ttl: Optional[int] = None) -> bool:
        """
        Cache query results
        
        Args:
            sql_query: SQL query string
            results: Query results (list of dicts)
            columns: Column names
            user_id: User identifier
            summary: Natural language summary/explanation
            user_question: Original user question
            analysis: Data analysis insight
            ttl: Time to live (uses default if None)
        
        Returns:
            True if cached successfully
        """
        if not self.enabled or not self.cache:
            return False
        
        try:
            cache_key = self.generate_cache_key(sql_query)
            
            cache_data = {
                'query_text': sql_query,
                'results': results,
                'columns': columns,
                'row_count': len(results),
                'user_id': user_id,
                'summary': summary,
                'user_question': user_question,
                'analysis': analysis,
                'summary_analysis': summary_analysis
            }
            
            ttl = ttl or self.default_ttl
            success = self.cache.set(cache_key, cache_data, ttl)
            
            if success:
                logger.debug(f"Cached query result: {cache_key[:8]}... ({len(results)} rows)")
            
            return success
            
        except Exception as e:
            logger.error(f"Error caching query result: {e}")
            return False
    
    def get_cached_result(self, sql_query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached query result
        
        Args:
            sql_query: SQL query string
        
        Returns:
            Cached data or None if not found
        """
        if not self.enabled or not self.cache:
            return None
        
        try:
            cache_key = self.generate_cache_key(sql_query)
            cached_data = self.cache.get(cache_key)
            
            if cached_data:
                logger.debug(f"Cache HIT: {cache_key[:8]}... (age: {cached_data.get('age', 0)}s)")
            else:
                logger.debug(f"Cache MISS: {cache_key[:8]}...")
            
            return cached_data
            
        except Exception as e:
            logger.error(f"Error retrieving cached result: {e}")
            return None
    
    def clear_user_cache(self, user_id: str) -> int:
        """
        Clear all cache entries for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of entries deleted
        """
        if not self.enabled or not self.cache:
            return 0
        
        try:
            return self.cache.clear_user_cache(user_id)
        except Exception as e:
            logger.error(f"Error clearing user cache: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """Clear all cache entries"""
        if not self.enabled or not self.cache:
            return False
        
        try:
            return self.cache.clear_all()
        except Exception as e:
            logger.error(f"Error clearing all cache: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        if not self.enabled or not self.cache:
            return 0
        
        try:
            return self.cache.clear_expired()
        except Exception as e:
            logger.error(f"Error clearing expired entries: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled or not self.cache:
            return {
                'enabled': False,
                'backend': 'none'
            }
        
        try:
            stats = self.cache.get_stats()
            stats['enabled'] = True
            stats['default_ttl_days'] = self.default_ttl / 86400
            return stats
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'enabled': True,
                'error': str(e)
            }
    
    def list_entries(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List cached entries"""
        if not self.enabled or not self.cache:
            return []
        
        try:
            return self.cache.list_entries(user_id, limit)
        except Exception as e:
            logger.error(f"Error listing cache entries: {e}")
            return []
    
    
    def update_analysis(self, sql_query: str, analysis: str) -> bool:
        """Update analysis for a cached query"""
        if not self.enabled or not self.cache:
            return False
            
        try:
            cache_key = self.generate_cache_key(sql_query)
            # Check if backend supports update_analysis
            if hasattr(self.cache, 'update_analysis'):
                return self.cache.update_analysis(cache_key, analysis)
            return False
        except Exception as e:
            logger.error(f"Error updating analysis: {e}")
            return False

    def update_summary_analysis(self, sql_query: str, summary_analysis: str) -> bool:
        """Update final summary+analysis text for a cached query."""
        if not self.enabled or not self.cache:
            return False

        try:
            cache_key = self.generate_cache_key(sql_query)
            if hasattr(self.cache, 'update_summary_analysis'):
                return self.cache.update_summary_analysis(cache_key, summary_analysis)
            return False
        except Exception as e:
            logger.error(f"Error updating summary_analysis: {e}")
            return False

    
    def update_visualization(self, sql_query: str, visualization: Dict) -> bool:
        """Update visualization for a cached query"""
        if not self.enabled or not self.cache:
            return False
            
        try:
            cache_key = self.generate_cache_key(sql_query)
            if hasattr(self.cache, 'update_visualization'):
                return self.cache.update_visualization(cache_key, visualization)
            return False
        except Exception as e:
            logger.error(f"Error updating visualization: {e}")
            return False

    def test_connection(self) -> bool:
        """Test cache backend connection"""
        if not self.enabled or not self.cache:
            return False
        
        try:
            return self.cache.test_connection()
        except Exception as e:
            logger.error(f"Error testing cache connection: {e}")
            return False
