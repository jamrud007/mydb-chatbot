"""
SQLite-based cache implementation
Default cache backend for development
"""
import sqlite3
import json
import hashlib
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from pathlib import Path

from .cache_interface import CacheInterface

logger = logging.getLogger(__name__)


class SQLiteCache(CacheInterface):
    """
    SQLite cache implementation with persistent storage
    
    Features:
    - Auto-initialization of database and tables
    - JSON storage for query results
    - TTL (Time To Live) support
    - Automatic cleanup of expired entries
    - Cache statistics tracking
    """
    
    def __init__(self, db_path: str = "./data/cache.db", max_size_mb: int = 500):
        """
        Initialize SQLite cache
        
        Args:
            db_path: Path to SQLite database file
            max_size_mb: Maximum database size in MB
        """
        self.db_path = db_path
        self.max_size_mb = max_size_mb
        
        # Create data directory if not exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Cache statistics
        self.hits = 0
        self.misses = 0
        
        logger.info(f"SQLite cache initialized at {db_path}")
    
    def _init_database(self):
        """Create database schema if not exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create cache table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                query_text TEXT NOT NULL,
                user_question TEXT,
                summary TEXT,
                analysis TEXT,
                summary_analysis TEXT,
                visualization TEXT,
                results BLOB NOT NULL,
                columns TEXT NOT NULL,
                row_count INTEGER,
                user_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON query_cache(cache_key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expires_at ON query_cache(expires_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON query_cache(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON query_cache(created_at)")

        # Safe migration for existing DBs created before summary_analysis field existed.
        try:
            cursor.execute("ALTER TABLE query_cache ADD COLUMN summary_analysis TEXT")
        except sqlite3.OperationalError:
            # Column already exists.
            pass
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data by key"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get entry and check if expired
            cursor.execute("""
                SELECT cache_key, query_text, user_question, summary, analysis, summary_analysis, visualization, results, columns, row_count, 
                       user_id, created_at, expires_at, access_count
                FROM query_cache
                WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > ?)
            """, (key, datetime.now()))
            
            row = cursor.fetchone()
            
            if row:
                # Update access statistics
                cursor.execute("""
                    UPDATE query_cache
                    SET last_accessed = ?, access_count = access_count + 1
                    WHERE cache_key = ?
                """, (datetime.now(), key))
                conn.commit()
                
                # Parse stored data
                results = json.loads(row['results'])
                columns = json.loads(row['columns'])
                try:
                    visualization = json.loads(row['visualization']) if row['visualization'] else None
                except:
                    visualization = None
                    
                created_at = datetime.fromisoformat(row['created_at'])
                age = int((datetime.now() - created_at).total_seconds())
                
                self.hits += 1
                
                conn.close()
                return {
                    'results': results,
                    'columns': columns,
                    'row_count': row['row_count'],
                    'user_id': row['user_id'],
                    'query_text': row['query_text'],
                    'user_question': row['user_question'] or '',
                    'summary': row['summary'] or '',
                    'analysis': row['analysis'] or '',
                    'summary_analysis': row['summary_analysis'] or '',
                    'visualization': visualization,
                    'created_at': created_at,
                    'age': age,
                    'access_count': row['access_count'] + 1
                }
            else:
                self.misses += 1
                conn.close()
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, key: str, value: Dict[str, Any], ttl: int = 604800) -> bool:
        """Store data in cache"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculate expiration time
            expires_at = datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
            
            # Serialize data
            results_json = json.dumps(value.get('results', []))
            columns_json = json.dumps(value.get('columns', []))
            viz = value.get('visualization')
            visualization_json = json.dumps(viz) if viz else None
            
            # Insert or replace
            cursor.execute("""
                INSERT OR REPLACE INTO query_cache 
                (cache_key, query_text, user_question, summary, analysis, summary_analysis, visualization, results, columns, row_count, user_id, created_at, expires_at, last_accessed, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (
                key,
                value.get('query_text', ''),
                value.get('user_question', ''),
                value.get('summary', ''),
                value.get('analysis', ''),
                value.get('summary_analysis', ''),
                visualization_json,
                results_json,
                columns_json,
                value.get('row_count', 0),
                value.get('user_id', 'unknown'),
                datetime.now(),
                expires_at,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()

            
            # Check size limit
            self._enforce_size_limit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error storing in cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cache entry by key"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM query_cache WHERE cache_key = ?", (key,))
            deleted = cursor.rowcount > 0
            
            conn.commit()
            conn.close()
            
            return deleted
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM query_cache")
            
            conn.commit()
            conn.close()
            
            logger.info("All cache entries cleared")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def clear_user_cache(self, user_id: str) -> int:
        """Clear all cache entries for specific user"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM query_cache WHERE user_id = ?", (user_id,))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            logger.info(f"Cleared {deleted_count} cache entries for user {user_id}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing user cache: {e}")
            return 0
    
    def clear_expired(self) -> int:
        """Remove expired cache entries"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM query_cache 
                WHERE expires_at IS NOT NULL AND expires_at < ?
            """, (datetime.now(),))
            
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleared {deleted_count} expired cache entries")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error clearing expired entries: {e}")
            return 0
    
    def _enforce_size_limit(self):
        """Ensure database doesn't exceed max size"""
        try:
            # Get current database size
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            
            if size_mb > self.max_size_mb:
                # Delete oldest entries until under limit
                conn = self._get_connection()
                cursor = conn.cursor()
                
                # Delete 10% of oldest entries
                cursor.execute("""
                    DELETE FROM query_cache
                    WHERE id IN (
                        SELECT id FROM query_cache
                        ORDER BY last_accessed ASC
                        LIMIT (SELECT COUNT(*) / 10 FROM query_cache)
                    )
                """)
                
                deleted = cursor.rowcount
                conn.commit()
                conn.close()
                
                logger.warning(f"Cache size limit reached ({size_mb:.1f}MB). Deleted {deleted} old entries.")
                
        except Exception as e:
            logger.error(f"Error enforcing size limit: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_entries,
                    MIN(created_at) as oldest_entry,
                    MAX(created_at) as newest_entry,
                    SUM(access_count) as total_accesses
                FROM query_cache
            """)
            
            row = cursor.fetchone()
            
            # Get database size
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024) if os.path.exists(self.db_path) else 0
            
            # Calculate hit rate
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            
            conn.close()
            
            return {
                'backend': 'sqlite',
                'database_path': self.db_path,
                'total_entries': row['total_entries'] or 0,
                'total_size_mb': round(size_mb, 2),
                'max_size_mb': self.max_size_mb,
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': round(hit_rate, 3),
                'total_accesses': row['total_accesses'] or 0,
                'oldest_entry': row['oldest_entry'],
                'newest_entry': row['newest_entry']
            }
            
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {
                'backend': 'sqlite',
                'error': str(e)
            }
    
    def list_entries(self, user_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List cached query entries"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT cache_key, query_text, user_question, row_count, user_id, created_at, 
                           expires_at, last_accessed, access_count
                    FROM query_cache
                    WHERE user_id = ?
                    ORDER BY last_accessed DESC
                    LIMIT ?
                """, (user_id, limit))
            else:
                cursor.execute("""
                    SELECT cache_key, query_text, user_question, row_count, user_id, created_at, 
                           expires_at, last_accessed, access_count
                    FROM query_cache
                    ORDER BY last_accessed DESC
                    LIMIT ?
                """, (limit,))
            
            entries = []
            for row in cursor.fetchall():
                # Use user_question if available, otherwise fallback to truncated query
                display_text = row['user_question'] if row['user_question'] else (row['query_text'][:100] + '...' if len(row['query_text']) > 100 else row['query_text'])
                
                entries.append({
                    'cache_key': row['cache_key'],
                    'query_text': row['query_text'],
                    'user_question': row['user_question'] or '',
                    'display_text': display_text,
                    'row_count': row['row_count'],
                    'user_id': row['user_id'],
                    'created_at': row['created_at'],
                    'expires_at': row['expires_at'],
                    'last_accessed': row['last_accessed'],
                    'access_count': row['access_count']
                })
            
            conn.close()
            return entries
            
        except Exception as e:
            logger.error(f"Error listing cache entries: {e}")
            return []
            
    def update_analysis(self, key: str, analysis: str) -> bool:
        """Update analysis field for an existing entry"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE query_cache 
                SET analysis = ? 
                WHERE cache_key = ?
            """, (analysis, key))
            
            row_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            return row_count > 0
            
        except Exception as e:
            logger.error(f"Error updating analysis in cache: {e}")
            return False

    def update_summary_analysis(self, key: str, summary_analysis: str) -> bool:
        """Update final combined summary+analysis text for an existing entry."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE query_cache
                SET summary_analysis = ?
                WHERE cache_key = ?
            """, (summary_analysis, key))

            row_count = cursor.rowcount
            conn.commit()
            conn.close()

            return row_count > 0
        except Exception as e:
            logger.error(f"Error updating summary_analysis in cache: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test if cache backend is available"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"SQLite cache connection test failed: {e}")
            return False
