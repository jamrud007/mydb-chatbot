"""
Database Schema Manager with Caching (MySQL / Oracle / Any SQL DB)
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from cachetools import TTLCache

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages database schema extraction and caching"""

    def __init__(self, db_connection: Any, cache_ttl: Optional[int] = None) -> None:
        from config import Config
        effective_ttl = cache_ttl if cache_ttl is not None else Config.SCHEMA_CACHE_TTL
        self.db_connection = db_connection
        self.engine = getattr(db_connection, 'engine', 'mysql').lower()
        self.cache: TTLCache = TTLCache(maxsize=1, ttl=effective_ttl)
        self.cache_key = 'schema'
        logger.info(f"SchemaManager initialized with cache TTL: {effective_ttl}s (engine={self.engine})")

    def get_schema(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get database schema (cached)

        Args:
            force_refresh: Force refresh cache

        Returns:
            dict: Schema information
        """
        if force_refresh or self.cache_key not in self.cache:
            logger.info("Fetching fresh schema from database")
            schema = self._extract_schema()
            self.cache[self.cache_key] = schema
            return schema

        logger.info("Returning cached schema")
        return self.cache[self.cache_key]

    def _extract_schema(self) -> Dict[str, Any]:
        """Extract schema from configured database engine"""
        if self.engine == 'oracle':
            return self._extract_schema_oracle()
        return self._extract_schema_mysql()

    def _extract_schema_mysql(self) -> Dict[str, Any]:
        db_name = self.db_connection.db_config['database']
        schema = {
            'database': db_name,
            'tables': [],
            'extracted_at': datetime.now().isoformat()
        }

        tables_query = """
            SELECT TABLE_NAME
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = %s
            ORDER BY TABLE_NAME
        """
        _, tables = self.db_connection.execute_query(tables_query, (db_name,))

        for (table_name,) in tables:
            schema['tables'].append(self._get_table_info_mysql(table_name, db_name))

        logger.info(f"MySQL schema extracted: {len(schema['tables'])} tables")
        return schema

    def _extract_schema_oracle(self) -> Dict[str, Any]:
        owner = self.db_connection.db_config.get('schema', self.db_connection.db_config.get('user', '')).upper()
        schema = {
            'database': owner,
            'tables': [],
            'extracted_at': datetime.now().isoformat()
        }

        tables_query = """
            SELECT table_name
            FROM all_tables
            WHERE owner = :1
            ORDER BY table_name
        """
        _, tables = self.db_connection.execute_query(tables_query, (owner,))

        for (table_name,) in tables:
            schema['tables'].append(self._get_table_info_oracle(table_name, owner))

        logger.info(f"Oracle schema extracted: {len(schema['tables'])} tables")
        return schema

    def _get_table_info_mysql(self, table_name: str, db_name: str) -> Dict[str, Any]:
        table_info = {
            'name': table_name,
            'columns': [],
            'primary_keys': [],
            'foreign_keys': []
        }

        columns_query = """
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_KEY,
                COLUMN_COMMENT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """
        _, columns = self.db_connection.execute_query(columns_query, (db_name, table_name))

        for col_name, data_type, is_nullable, col_key, comment in columns:
            table_info['columns'].append({
                'name': col_name,
                'type': data_type,
                'nullable': is_nullable == 'YES',
                'comment': comment or ''
            })
            if col_key == 'PRI':
                table_info['primary_keys'].append(col_name)

        fk_query = """
            SELECT
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL
        """
        _, foreign_keys = self.db_connection.execute_query(fk_query, (db_name, table_name))

        for col_name, ref_table, ref_column in foreign_keys:
            table_info['foreign_keys'].append({
                'column': col_name,
                'references_table': ref_table,
                'references_column': ref_column
            })

        return table_info

    def _get_table_info_oracle(self, table_name: str, owner: str) -> Dict[str, Any]:
        table_info = {
            'name': table_name,
            'columns': [],
            'primary_keys': [],
            'foreign_keys': []
        }

        columns_query = """
            SELECT
                column_name,
                data_type,
                nullable,
                data_default
            FROM all_tab_columns
            WHERE owner = :1 AND table_name = :2
            ORDER BY column_id
        """
        _, columns = self.db_connection.execute_query(columns_query, (owner, table_name))

        # Fetch column comments from all_col_comments for better LLM context
        comments_query = """
            SELECT column_name, comments
            FROM all_col_comments
            WHERE owner = :1 AND table_name = :2
              AND comments IS NOT NULL
        """
        _, col_comments_rows = self.db_connection.execute_query(comments_query, (owner, table_name))
        col_comments: Dict[str, str] = {col: cmt for col, cmt in col_comments_rows if cmt}

        # Fetch sample values ONLY for truly enum-like columns (≤4 distinct values)
        # Limit to STATUS/TYPE-like columns to keep schema small for low-context models
        sample_values: Dict[str, list] = {}
        enum_hint_cols = [col_name for col_name, data_type, _, _ in columns
                          if data_type in ('NVARCHAR2', 'VARCHAR2', 'CHAR')
                          and any(kw in col_name.upper() for kw in ('STATUS', 'TYPE', 'ACTIVE', 'MODE', 'STATE'))]
        for col_name in enum_hint_cols:
            try:
                _, cnt_rows = self.db_connection.execute_query(
                    f"SELECT COUNT(DISTINCT {col_name}) FROM {owner}.{table_name}", ()
                )
                distinct_count = cnt_rows[0][0] if cnt_rows else 999
                if 1 < distinct_count <= 4:
                    _, sv_rows = self.db_connection.execute_query(
                        f"SELECT DISTINCT {col_name} FROM {owner}.{table_name} "
                        f"WHERE {col_name} IS NOT NULL FETCH FIRST 4 ROWS ONLY",
                        ()
                    )
                    vals = [str(r[0]) for r in sv_rows if r[0] is not None]
                    if vals:
                        sample_values[col_name] = vals
            except Exception:
                pass

        for col_name, data_type, nullable, data_default in columns:
            comment = col_comments.get(col_name, '')
            if not comment and data_default is not None:
                comment = f"default={data_default}"
            # Append known enum values (only for truly low-cardinality columns)
            if col_name in sample_values:
                vals_str = ', '.join(f"'{v}'" for v in sample_values[col_name])
                comment = (comment + f" | values: {vals_str}").lstrip(' | ')
            table_info['columns'].append({
                'name': col_name,
                'type': data_type,
                'nullable': nullable == 'Y',
                'comment': comment,
            })

        pk_query = """
            SELECT cc.column_name
            FROM all_constraints c
            JOIN all_cons_columns cc
              ON c.owner = cc.owner
             AND c.constraint_name = cc.constraint_name
            WHERE c.owner = :1
              AND c.table_name = :2
              AND c.constraint_type = 'P'
            ORDER BY cc.position
        """
        _, primary_keys = self.db_connection.execute_query(pk_query, (owner, table_name))
        table_info['primary_keys'] = [col_name for (col_name,) in primary_keys]

        fk_query = """
            SELECT
                acc.column_name,
                r.table_name AS referenced_table_name,
                rcc.column_name AS referenced_column_name
            FROM all_constraints c
            JOIN all_cons_columns acc
              ON c.owner = acc.owner
             AND c.constraint_name = acc.constraint_name
            JOIN all_constraints r
              ON c.r_owner = r.owner
             AND c.r_constraint_name = r.constraint_name
            JOIN all_cons_columns rcc
              ON r.owner = rcc.owner
             AND r.constraint_name = rcc.constraint_name
             AND acc.position = rcc.position
            WHERE c.owner = :1
              AND c.table_name = :2
              AND c.constraint_type = 'R'
            ORDER BY acc.position
        """
        _, foreign_keys = self.db_connection.execute_query(fk_query, (owner, table_name))

        for col_name, ref_table, ref_column in foreign_keys:
            table_info['foreign_keys'].append({
                'column': col_name,
                'references_table': ref_table,
                'references_column': ref_column
            })

        return table_info

    def format_schema_for_llm(self, table_filter=None) -> str:
        """
        Format schema for LLM prompt (with types and comments for accuracy).

        Args:
            table_filter: Optional list of table names to include (case-insensitive).
                          If None, all tables are included.

        Returns:
            str: Formatted schema string
        """
        schema = self.get_schema()

        filter_set = {t.upper() for t in table_filter} if table_filter else None

        lines = ["Tables structure (use ONLY these exact column names):"]
        for table in schema['tables']:
            if filter_set and table['name'].upper() not in filter_set:
                continue
            lines.append(f"\nTABLE {table['name']}:")
            for col in table['columns']:
                comment = f"  -- {col['comment']}" if col.get('comment') else ""
                lines.append(f"  {col['name']} {col['type']}{comment}")
            if table.get('primary_keys'):
                lines.append(f"  PK: {', '.join(table['primary_keys'])}")
        return "\n".join(lines)

    def invalidate_cache(self) -> None:
        """Clear schema cache"""
        self.cache.clear()
        logger.info("Schema cache invalidated")
