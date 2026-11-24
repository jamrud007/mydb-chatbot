"""
Safe SQL Query Executor with Query Result Caching
"""
import logging
import re
import time
from typing import Any, Dict, Optional, Tuple

from cache.cache_manager import CacheManager
from config import Config
from utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class QueryExecutor:
    """Executes SQL queries with validation, safety checks, and caching"""

    # Precompiled at class load — avoids recompiling on every validate_query() call
    _COMPILED_DANGEROUS = [
        re.compile(p, re.IGNORECASE)
        for p in [
            r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b', r'\bUPDATE\b',
            r'\bINSERT\b', r'\bALTER\b', r'\bCREATE\b', r'\bGRANT\b',
            r'\bREVOKE\b', r'\bEXEC\b', r';.*--;',
        ]
    ]
    _RE_TOP_N = re.compile(r'^(SELECT)\s+TOP\s+\d+\s+', re.IGNORECASE)
    _RE_FETCH_FIRST = re.compile(r'\bFETCH\s+FIRST\b', re.IGNORECASE)
    _RE_ROWNUM = re.compile(r'\bROWNUM\b', re.IGNORECASE)
    _RE_LIMIT_KW = re.compile(r'\bLIMIT\b', re.IGNORECASE)
    
    def __init__(
        self,
        db_connection: Any,
        read_only: Optional[bool] = None,
        max_rows: Optional[int] = None,
        cache_manager: Optional[Any] = None,
    ) -> None:
        self.db_connection = db_connection
        self.engine = getattr(db_connection, 'engine', 'mysql').lower()
        self.read_only = read_only if read_only is not None else Config.READ_ONLY_MODE
        self.max_rows = max_rows if max_rows is not None else Config.MAX_QUERY_ROWS
        
        # Initialize cache manager
        if cache_manager is None and Config.CACHE_ENABLED:
            self.cache_manager = CacheManager(
                backend=Config.CACHE_BACKEND,
                sqlite_path=Config.CACHE_SQLITE_PATH,
                sqlite_max_size_mb=Config.CACHE_SQLITE_MAX_SIZE_MB,
                redis_url=Config.REDIS_URL,
                redis_max_connections=Config.REDIS_MAX_CONNECTIONS,
                default_ttl=Config.CACHE_DEFAULT_TTL,
                enabled=Config.CACHE_ENABLED
            )
        else:
            self.cache_manager = cache_manager
        
        logger.info(
            f"QueryExecutor initialized (engine={self.engine}, read_only={self.read_only}, "
            f"max_rows={self.max_rows}, cache_enabled={Config.CACHE_ENABLED})"
        )
    
    def validate_query(self, query: str) -> Tuple[bool, Optional[str]]:
        """Validate SQL query for safety. Returns (is_valid, error_message)."""
        query_upper = query.upper().strip()

        for pattern in self._COMPILED_DANGEROUS:
            if pattern.search(query_upper):
                return False, f"Query contains forbidden operation: {pattern.pattern}"
        
        # In read-only mode, only allow SELECT
        if self.read_only and not query_upper.startswith('SELECT'):
            return False, "Only SELECT queries are allowed in read-only mode"
        
        # Check for multiple statements (preventing SQL injection)
        if query.count(';') > 1 or (query.count(';') == 1 and not query.strip().endswith(';')):
            return False, "Multiple SQL statements are not allowed"
        
        return True, None
    
    def execute(
        self,
        query: str,
        use_cache: bool = True,
        user_id: str = 'unknown',
        nl_summary: str = '',
        user_question: str = '',
        analysis: str = '',
        summary_analysis: str = '',
    ) -> Dict[str, Any]:
        """Execute a validated SQL query with caching support."""
        # Validate query
        is_valid, error_msg = self.validate_query(query)
        if not is_valid:
            logger.warning(f"Query validation failed: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'columns': [],
                'rows': [],
                'row_count': 0,
                'from_cache': False
            }
        
        # Add LIMIT if not present and it's a SELECT query
        modified_query = self._add_limit(query)
        
        # Check cache first (for safe read queries)
        cacheable_prefixes = ('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')
        query_upper_clean = modified_query.upper().strip()
        is_cacheable = any(query_upper_clean.startswith(prefix) for prefix in cacheable_prefixes)
        
        from_cache = False
        cache_age = None
        
        if use_cache and self.cache_manager and is_cacheable:
            cached_result = self.cache_manager.get_cached_result(modified_query)
            
            if cached_result:
                logger.info(f"Cache HIT: Returning cached result (age: {cached_result.get('age', 0)}s)")
                get_metrics_collector().record_query_duration(0, user_id=user_id, query=modified_query, from_cache=True)
                return {
                    'success': True,
                    'error': None,
                    'columns': cached_result['columns'],
                    'rows': cached_result['results'],
                    'row_count': cached_result['row_count'],
                    'limited': cached_result['row_count'] == self.max_rows,
                    'from_cache': True,
                    'cache_age': cached_result.get('age', 0),
                    'cache_access_count': cached_result.get('access_count', 0),
                    'nl_summary': cached_result.get('summary', ''),
                    'user_question': cached_result.get('user_question', ''),
                    'analysis': cached_result.get('analysis', ''), # Return analysis from cache
                    'summary_analysis': cached_result.get('summary_analysis', '')
                }
        
        # Cache MISS - Execute query
        try:
            logger.info(f"Cache MISS: Executing query: {modified_query[:100]}...")
            _t0 = time.time()
            columns, rows = self.db_connection.execute_query(modified_query)
            _duration_ms = (time.time() - _t0) * 1000
            get_metrics_collector().record_query_duration(
                _duration_ms, user_id=user_id, query=modified_query, from_cache=False
            )
            
            # Convert rows to list of dictionaries for easier handling
            row_dicts = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    # Handle None and convert to string
                    value = row[i]
                    if value is None:
                        row_dict[col] = None
                    else:
                        row_dict[col] = str(value) if not isinstance(value, (int, float, bool)) else value
                row_dicts.append(row_dict)
            
            result = {
                'success': True,
                'error': None,
                'columns': columns,
                'rows': row_dicts,
                'row_count': len(row_dicts),
                'limited': len(row_dicts) == self.max_rows,
                'from_cache': False,
                'cache_age': None,
                'nl_summary': nl_summary,
                'user_question': user_question,
                'analysis': analysis,
                'summary_analysis': summary_analysis
            }
            
            # Store in cache (for safe read queries)
            if use_cache and self.cache_manager and is_cacheable:
                self.cache_manager.cache_query_result(
                    modified_query,
                    row_dicts,
                    columns,
                    user_id,
                    summary=nl_summary,
                    user_question=user_question,
                    analysis=analysis, # Store analysis
                    summary_analysis=summary_analysis
                )
            
            logger.info(f"Query executed successfully: {result['row_count']} rows returned")
            return result
        
        except Exception as e:
            # Auto-fix: DPY-3022 = TIMESTAMP WITH TIME ZONE not supported in thin mode
            # Retry by wrapping timestamp columns with CAST(... AS TIMESTAMP)
            if 'DPY-3022' in str(e) and self.engine == 'oracle':
                logger.warning("DPY-3022 timezone error — retrying with CAST on timestamp columns")
                fixed_query = self._cast_timezone_columns(modified_query)
                if fixed_query != modified_query:
                    try:
                        columns, rows = self.db_connection.execute_query(fixed_query)
                        row_dicts = []
                        for row in rows:
                            row_dict = {}
                            for i, col in enumerate(columns):
                                value = row[i]
                                row_dict[col] = None if value is None else (
                                    value if isinstance(value, (int, float, bool)) else str(value)
                                )
                            row_dicts.append(row_dict)
                        result = {
                            'success': True, 'error': None,
                            'columns': columns, 'rows': row_dicts,
                            'row_count': len(row_dicts),
                            'limited': len(row_dicts) == self.max_rows,
                            'from_cache': False, 'cache_age': None,
                            'nl_summary': nl_summary, 'user_question': user_question,
                            'analysis': analysis, 'summary_analysis': summary_analysis
                        }
                        if use_cache and self.cache_manager and is_cacheable:
                            self.cache_manager.cache_query_result(
                                fixed_query, row_dicts, columns, user_id,
                                summary=nl_summary, user_question=user_question,
                                analysis=analysis, summary_analysis=summary_analysis
                            )
                        logger.info(f"Timezone retry succeeded: {result['row_count']} rows")
                        return result
                    except Exception as e2:
                        logger.error(f"Timezone retry also failed: {e2}")
                        e = e2

            logger.error(f"Query execution error: {e}")
            get_metrics_collector().record_error('SQL_EXECUTION_ERROR', user_id=user_id)
            return {
                'success': False,
                'error': str(e),
                'columns': [],
                'rows': [],
                'row_count': 0,
                'from_cache': False
            }

    def _cast_timezone_columns(self, query: str) -> str:
        """Rewrite TIMESTAMP WITH TIME ZONE columns to CAST(col AS TIMESTAMP) for Oracle thin mode."""
        try:
            schema = self.db_connection.schema_manager.get_schema() if hasattr(self.db_connection, 'schema_manager') else None
            tz_cols = set()
            if schema:
                for table in schema.get('tables', []):
                    for col in table.get('columns', []):
                        if 'WITH TIME ZONE' in (col.get('type') or ''):
                            tz_cols.add(col['name'].upper())
            else:
                # Fallback: known timezone columns
                tz_cols = {'TIME_CREATED', 'TIME_UPDATED', 'TIME_DELETED'}

            fixed = query
            for col in tz_cols:
                # Replace bare column name (not already inside a CAST)
                fixed = re.sub(
                    rf'(?<!CAST\()(?<!\w)({re.escape(col)})(?!\w)(?!\s*AS\s)',
                    rf'CAST(\1 AS TIMESTAMP)',
                    fixed,
                    flags=re.IGNORECASE
                )
            return fixed
        except Exception as ex:
            logger.warning(f"_cast_timezone_columns failed: {ex}")
            return query

    def get_cache_query(self, query: str) -> str:
        """Get canonical query string used for cache key generation.

        This must match the query shape used in execute(), including LIMIT normalization.
        """
        return self._add_limit(query)
    
    def _add_limit(self, query: str) -> str:
        """Add row limiter clause to SELECT queries if not present."""
        query = query.rstrip(';').strip()

        # Auto-fix: remove SQL Server TOP N syntax (incompatible with Oracle/MySQL)
        query = self._RE_TOP_N.sub(r'\1 ', query)

        query_upper = query.upper().strip()

        if not query_upper.startswith('SELECT'):
            return query

        if self.engine == 'oracle':
            if self._RE_FETCH_FIRST.search(query_upper) or self._RE_ROWNUM.search(query_upper):
                return query
            return f"{query} FETCH FIRST {self.max_rows} ROWS ONLY"

        # MySQL default
        if self._RE_LIMIT_KW.search(query_upper):
            return query
        return f"{query} LIMIT {self.max_rows}"
    
    def format_results_as_table(self, result: Dict[str, Any]) -> str:
        """Format query results as ASCII table."""
        if not result['success']:
            return f"Error: {result['error']}"
        
        if result['row_count'] == 0:
            return "No results found."
        
        columns = result['columns']
        rows = result['rows']
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = len(col)
        
        for row in rows:
            for col in columns:
                value_len = len(str(row.get(col, '')))
                col_widths[col] = max(col_widths[col], value_len)
        
        # Build table
        lines = []
        
        # Header separator
        separator = '┌' + '┬'.join(['─' * (col_widths[col] + 2) for col in columns]) + '┐'
        lines.append(separator)
        
        # Header
        header = '│'
        for col in columns:
            header += f" {col:<{col_widths[col]}} │"
        lines.append(header)
        
        # Header bottom
        separator = '├' + '┼'.join(['─' * (col_widths[col] + 2) for col in columns]) + '┤'
        lines.append(separator)
        
        # Rows
        for row in rows:
            row_str = '│'
            for col in columns:
                value = str(row.get(col, ''))
                row_str += f" {value:<{col_widths[col]}} │"
            lines.append(row_str)
        
        # Bottom
        separator = '└' + '┴'.join(['─' * (col_widths[col] + 2) for col in columns]) + '┘'
        lines.append(separator)
        
        # Add note if results were limited
        if result.get('limited'):
            lines.append(f"\n⚠ Results limited to {self.max_rows} rows")
        
        return '\n'.join(lines)
