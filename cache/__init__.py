"""
Cache module for query results
Supports SQLite (default) and Redis (production) backends
"""
from .cache_manager import CacheManager

__all__ = ['CacheManager']
