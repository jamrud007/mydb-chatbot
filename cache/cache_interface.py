"""
Base interface for cache adapters
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any
from datetime import datetime


class CacheInterface(ABC):
    """
    Abstract base class for cache implementations
    
    All cache adapters (SQLite, Redis) must implement these methods
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached data by key
        
        Args:
            key: Cache key (usually MD5 hash of SQL query)
        
        Returns:
            Cached data dict or None if not found/expired
            {
                'results': [...],
                'columns': [...],
                'row_count': int,
                'user_id': str,
                'created_at': datetime,
                'age': int  # seconds since creation
            }
        """
        pass
    
    @abstractmethod
    def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Store data in cache
        
        Args:
            key: Cache key
            value: Data to cache
            ttl: Time to live in seconds
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """
        Delete cache entry by key
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear_all(self) -> bool:
        """
        Clear all cache entries
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def clear_user_cache(self, user_id: str) -> int:
        """
        Clear all cache entries for specific user
        
        Args:
            user_id: User identifier
        
        Returns:
            Number of entries deleted
        """
        pass
    
    @abstractmethod
    def clear_expired(self) -> int:
        """
        Remove expired cache entries
        
        Returns:
            Number of entries deleted
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            {
                'total_entries': int,
                'total_size_mb': float,
                'hits': int,
                'misses': int,
                'hit_rate': float,
                'oldest_entry': datetime,
                'newest_entry': datetime
            }
        """
        pass
    
    @abstractmethod
    def list_entries(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List cached query entries
        
        Args:
            user_id: Filter by user (optional)
            limit: Maximum number of entries
        
        Returns:
            List of cache entry metadata
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test if cache backend is available
        
        Returns:
            True if connection successful
        """
        pass
