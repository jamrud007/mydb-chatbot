"""
Redis-based cache implementation (optional)
For production deployment with distributed caching
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

from .cache_interface import CacheInterface

logger = logging.getLogger(__name__)

try:
    import redis
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis library not available. Install with: pip install redis")


class RedisCache(CacheInterface):
    """
    Redis cache implementation for production
    
    Features:
    - Connection pooling
    - Native TTL support
    - Fast in-memory operations
    - Distributed caching support
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", max_connections: int = 10):
        """
        Initialize Redis cache
        
        Args:
            redis_url: Redis connection URL
            max_connections: Connection pool size
        """
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library not installed. Install with: pip install redis")
        
        self.redis_url = redis_url
        
        # Create connection pool
        self.pool = ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            decode_responses=True
        )
        
        self.client = redis.Redis(connection_pool=self.pool)
        
        # Test connection
        self.client.ping()
        
        # Statistics counters (stored in Redis)
        self.hits_key = "stats:cache:hits"
        self.misses_key = "stats:cache:misses"
        
        logger.info(f"Redis cache initialized at {redis_url}")
    
    def _make_data_key(self, cache_key: str) -> str:
        """Generate Redis key for data"""
        return f"query:{cache_key}:data"
    
    def _make_meta_key(self, cache_key: str) -> str:
        """Generate Redis key for metadata"""
        return f"query:{cache_key}:meta"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data by key"""
        try:
            data_key = self._make_data_key(key)
            meta_key = self._make_meta_key(key)
            
            # Get data and metadata
            pipe = self.client.pipeline()
            pipe.get(data_key)
            pipe.hgetall(meta_key)
            results = pipe.execute()
            
            data_json = results[0]
            metadata = results[1]
            
            if data_json and metadata:
                # Increment hits counter
                self.client.incr(self.hits_key)
                
                # Parse data
                cache_data = json.loads(data_json)
                
                # Calculate age
                created_at = datetime.fromisoformat(metadata['created_at'])
                age = int((datetime.now() - created_at).total_seconds())
                
                return {
                    'results': cache_data['results'],
                    'columns': cache_data['columns'],
                    'row_count': int(metadata['row_count']),
                    'user_id': metadata['user_id'],
                    'query_text': metadata['query_text'],
                    'user_question': metadata.get('user_question', ''),
                    'summary': metadata.get('summary', ''),
                    'analysis': metadata.get('analysis', ''),
                    'summary_analysis': metadata.get('summary_analysis', ''),
                    'created_at': created_at,
                    'age': age,
                    'access_count': int(metadata.get('access_count', 0)) + 1
                }
            else:
                # Increment misses counter
                self.client.incr(self.misses_key)
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving from Redis cache: {e}")
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 604800) -> bool:
        """Store data in cache"""
        try:
            data_key = self._make_data_key(key)
            meta_key = self._make_meta_key(key)
            
            # Prepare data
            cache_data = {
                'results': value.get('results', []),
                'columns': value.get('columns', [])
            }
            data_json = json.dumps(cache_data)
            
            # Prepare metadata
            metadata = {
                'query_text': value.get('query_text', ''),
                'row_count': value.get('row_count', 0),
                'user_id': value.get('user_id', 'unknown'),
                'user_question': value.get('user_question', ''),
                'summary': value.get('summary', ''),
                'analysis': value.get('analysis', ''),
                'summary_analysis': value.get('summary_analysis', ''),
                'created_at': datetime.now().isoformat(),
                'access_count': 0
            }
            
            # Store with TTL
            pipe = self.client.pipeline()
            pipe.set(data_key, data_json, ex=ttl)
            pipe.hset(meta_key, mapping=metadata)
            pipe.expire(meta_key, ttl)
            pipe.execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing in Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cache entry by key"""
        try:
            data_key = self._make_data_key(key)
            meta_key = self._make_meta_key(key)
            
            deleted = self.client.delete(data_key, meta_key)
            return deleted > 0
            
        except Exception as e:
            logger.error(f"Error deleting from Redis cache: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            # Delete all query:* keys
            keys = self.client.keys("query:*")
            if keys:
                self.client.delete(*keys)
            
            # Reset statistics
            self.client.delete(self.hits_key, self.misses_key)
            
            logger.info(f"Cleared {len(keys)} Redis cache entries")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False
    
    def clear_user_cache(self, user_id: str) -> int:
        """Clear all cache entries for specific user"""
        try:
            # Find all meta keys
            meta_keys = self.client.keys("query:*:meta")
            
            deleted_count = 0
            for meta_key in meta_keys:
                # Check if belongs to user
                stored_user_id = self.client.hget(meta_key, 'user_id')
                if stored_user_id == user_id:
                    # Extract cache key
                    cache_key = meta_key.replace('query:', '').replace(':meta', '')
                    if self.delete(cache_key):
                        deleted_count += 1
            
            logger.info(f"Cleared {deleted_count} Redis cache entries for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing user cache: {e}")
            return 0
    
    def clear_expired(self) -> int:
        """Remove expired cache entries (Redis handles this automatically)"""
        # Redis automatically removes expired keys
        # This method is here for interface compatibility
        logger.info("Redis automatically handles TTL expiration")
        return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            # Get counters
            hits = int(self.client.get(self.hits_key) or 0)
            misses = int(self.client.get(self.misses_key) or 0)
            
            # Calculate hit rate
            total_requests = hits + misses
            hit_rate = hits / total_requests if total_requests > 0 else 0
            
            # Count entries
            data_keys = self.client.keys("query:*:data")
            total_entries = len(data_keys)
            
            # Estimate size (rough approximation)
            memory_info = self.client.info('memory')
            size_mb = memory_info.get('used_memory', 0) / (1024 * 1024)
            
            return {
                'backend': 'redis',
                'redis_url': self.redis_url,
                'total_entries': total_entries,
                'total_size_mb': round(size_mb, 2),
                'hits': hits,
                'misses': misses,
                'hit_rate': round(hit_rate, 3),
                'redis_version': self.client.info('server').get('redis_version', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"Error getting Redis cache stats: {e}")
            return {
                'backend': 'redis',
                'error': str(e)
            }
    
    def list_entries(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List cached query entries"""
        try:
            meta_keys = self.client.keys("query:*:meta")
            
            entries = []
            for meta_key in meta_keys[:limit]:
                metadata = self.client.hgetall(meta_key)
                
                # Filter by user if specified
                if user_id and metadata.get('user_id') != user_id:
                    continue
                
                cache_key = meta_key.replace('query:', '').replace(':meta', '')
                
                entries.append({
                    'cache_key': cache_key,
                    'query_text': metadata.get('query_text', '')[:100] + '...',
                    'row_count': int(metadata.get('row_count', 0)),
                    'user_id': metadata.get('user_id', 'unknown'),
                    'created_at': metadata.get('created_at'),
                    'access_count': int(metadata.get('access_count', 0))
                })
            
            return entries
            
        except Exception as e:
            logger.error(f"Error listing Redis cache entries: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test if Redis is available"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection test failed: {e}")
            return False

    def update_analysis(self, key: str, analysis: str) -> bool:
        """Update analysis field for an existing cache entry."""
        try:
            meta_key = self._make_meta_key(key)
            if not self.client.exists(meta_key):
                return False
            return self.client.hset(meta_key, mapping={'analysis': analysis}) >= 0
        except Exception as e:
            logger.error(f"Error updating analysis in Redis cache: {e}")
            return False

    def update_summary_analysis(self, key: str, summary_analysis: str) -> bool:
        """Update final combined summary+analysis text for an existing cache entry."""
        try:
            meta_key = self._make_meta_key(key)
            if not self.client.exists(meta_key):
                return False
            return self.client.hset(meta_key, mapping={'summary_analysis': summary_analysis}) >= 0
        except Exception as e:
            logger.error(f"Error updating summary_analysis in Redis cache: {e}")
            return False
