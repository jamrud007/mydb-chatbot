"""
SQL Validator with Auto-Correction
Validates and fixes SQL queries before execution
"""
import re
import logging
from difflib import get_close_matches, SequenceMatcher
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class SQLValidator:
    """Validates and auto-corrects SQL queries"""
    
    def __init__(self, schema_manager):
        """
        Initialize validator with schema
        
        Args:
            schema_manager: SchemaManager instance
        """
        self.schema_manager = schema_manager
        self._refresh_schema()
        logger.info("SQLValidator initialized")
    
    def _refresh_schema(self):
        """Refresh table and column cache from schema"""
        schema = self.schema_manager.get_schema()
        
        # Build lookup tables
        self.table_names = [t['name'].lower() for t in schema['tables']]
        self.columns_by_table = {}
        
        for table in schema['tables']:
            table_name = table['name'].lower()
            self.columns_by_table[table_name] = [
                col['name'].lower() for col in table['columns']
            ]
        
        logger.info(f"Schema cache refreshed: {len(self.table_names)} tables")
    
    def validate_and_fix(self, sql: str) -> Dict:
        """
        Validate SQL and auto-fix common issues
        
        Args:
            sql: SQL query string
        
        Returns:
            dict: Validation result with fixed SQL
        """
        logger.info(f"Validating SQL: {sql[:100]}...")
        
        # 1. Safety check
        if not self._is_safe_query(sql):
            logger.warning(f"Unsafe SQL detected: {sql}")
            return {
                'valid': False,
                'error': 'Unsafe SQL operation detected (only SELECT allowed)',
                'error_type': 'UNSAFE_OPERATION',
                'original_sql': sql,
                'fixed_sql': None,
                'corrections': []
            }
        
        # 2. Auto-correct table names
        fixed_sql, table_corrections = self._fix_table_names(sql)
        
        # 3. Check for unknown tables (after correction)
        unknown_tables = self._find_unknown_tables(fixed_sql)
        
        # 4. Check for unknown columns (NEW!)
        unknown_columns = self._find_unknown_columns(fixed_sql)
        
        if unknown_tables:
            logger.warning(f"Unknown tables found: {unknown_tables}")
            suggestions = []
            for table in unknown_tables:
                matches = get_close_matches(table.lower(), self.table_names, n=3, cutoff=0.4)
                if matches:
                    suggestions.append(f"'{table}' → mungkin maksud: {', '.join(matches)}")
            
            error_msg = f"Tabel tidak ditemukan: {', '.join(unknown_tables)}"
            if suggestions:
                error_msg += f"\n\nSaran: {'; '.join(suggestions)}"
            
            return {
                'valid': False,
                'error': error_msg,
                'error_type': 'UNKNOWN_TABLE',
                'original_sql': sql,
                'fixed_sql': fixed_sql,
                'corrections': table_corrections,
                'unknown_tables': unknown_tables,
                'available_tables': self.table_names
            }
        
        # Check for column hallucinations
        if unknown_columns:
            logger.warning(f"Unknown columns found: {unknown_columns}")
            error_msg = f"Kolom tidak ditemukan: {', '.join([f'{t}.{c}' for t, c in unknown_columns[:5]])}"
            error_msg += "\n\nLLM mungkin 'hallucinate' (mengarang) nama kolom yang tidak ada."
            error_msg += "\nSilakan cek schema atau gunakan pertanyaan yang lebih spesifik."
            
            return {
                'valid': False,
                'error': error_msg,
                'error_type': 'UNKNOWN_COLUMN',
                'original_sql': sql,
                'fixed_sql': fixed_sql,
                'corrections': table_corrections,
                'unknown_columns': unknown_columns
            }
        
        # Success!
        logger.info(f"SQL validation passed. Corrections: {len(table_corrections)}")
        return {
            'valid': True,
            'original_sql': sql,
            'fixed_sql': fixed_sql,
            'corrections': table_corrections,
            'changed': sql != fixed_sql
        }
    
    def _is_safe_query(self, sql: str) -> bool:
        """
        Check if SQL is safe (read-only)
        
        Args:
            sql: SQL query
        
        Returns:
            bool: True if safe
        """
        sql_upper = sql.upper().strip()
        
        # Must start with SELECT or WITH
        if not sql_upper.startswith(('SELECT', 'WITH')):
            return False
        
        # Check for forbidden keywords
        forbidden = [
            'DELETE', 'UPDATE', 'DROP', 'ALTER', 'TRUNCATE', 
            'INSERT', 'CREATE', 'GRANT', 'REVOKE', 'EXEC',
            'EXECUTE', 'CALL', 'PROCEDURE', 'FUNCTION'
        ]
        
        # Use word boundaries to avoid false positives
        for keyword in forbidden:
            if re.search(rf'\b{keyword}\b', sql_upper):
                logger.warning(f"Forbidden keyword found: {keyword}")
                return False
        
        return True
    
    def _fix_table_names(self, sql: str) -> Tuple[str, List[Dict]]:
        """
        Auto-correct table name typos
        
        Args:
            sql: SQL query
        
        Returns:
            tuple: (fixed_sql, corrections_list)
        """
        # Extract table names from SQL
        # Patterns: FROM table, JOIN table
        pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        tables_in_sql = re.findall(pattern, sql, re.IGNORECASE)
        
        if not tables_in_sql:
            return sql, []
        
        fixed_sql = sql
        corrections = []
        
        for table in set(tables_in_sql):
            table_lower = table.lower()
            
            # Check if table exists (case-insensitive)
            if table_lower not in self.table_names:
                # Try to find closest match
                matches = get_close_matches(
                    table_lower,
                    self.table_names,
                    n=1,
                    cutoff=0.6  # 60% similarity threshold
                )
                
                if matches:
                    correct_table = matches[0]
                    
                    # Replace table name (case-insensitive)
                    fixed_sql = re.sub(
                        rf'\b{re.escape(table)}\b',
                        correct_table,
                        fixed_sql,
                        flags=re.IGNORECASE
                    )
                    
                    similarity = SequenceMatcher(None, table_lower, correct_table).ratio()
                    
                    corrections.append({
                        'type': 'table_name',
                        'original': table,
                        'corrected': correct_table,
                        'similarity': round(similarity, 2)
                    })
                    
                    logger.info(f"Auto-corrected: '{table}' → '{correct_table}'")
                    
        return fixed_sql, corrections
    
    def _find_unknown_columns(self, sql: str) -> List[Tuple[str, str]]:
        """
        Find column references that don't exist in schema
        
        Returns:
            list: [(table, column), ...] of unknown columns
        """
        unknown = []
        
        # Pattern: table_alias.column_name or table.column_name
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.findall(pattern, sql, re.IGNORECASE)
        
        # Build table alias map
        alias_pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*))?'
        aliases = re.findall(alias_pattern, sql, re.IGNORECASE)
        alias_map = {}
        for table, alias in aliases:
            table_lower = table.lower()
            if table_lower in self.table_names:
                if alias:
                    alias_map[alias.lower()] = table_lower
                alias_map[table_lower] = table_lower
        
        # Check each column reference
        for table_or_alias, column in matches:
            table_or_alias_lower = table_or_alias.lower()
            column_lower = column.lower()
            
            # Resolve alias to actual table
            actual_table = alias_map.get(table_or_alias_lower)
            
            if actual_table and actual_table in self.columns_by_table:
                valid_columns = self.columns_by_table[actual_table]
                if column_lower not in valid_columns:
                    unknown.append((actual_table, column))
        
        return unknown
    
    def _find_unknown_tables(self, sql: str) -> List[str]:
        """
        Find table names that don't exist in schema
        
        Args:
            sql: SQL query
        
        Returns:
            list: Unknown table names
        """
        pattern = r'(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        tables_in_sql = re.findall(pattern, sql, re.IGNORECASE)
        
        unknown = []
        for table in set(tables_in_sql):
            if table.lower() not in self.table_names:
                unknown.append(table)
        
        return unknown
    
    def get_table_suggestions(self, partial_name: str, limit: int = 5) -> List[str]:
        """
        Get table name suggestions for partial input
        
        Args:
            partial_name: Partial table name
            limit: Max suggestions
        
        Returns:
            list: Suggested table names
        """
        matches = get_close_matches(
            partial_name.lower(),
            self.table_names,
            n=limit,
            cutoff=0.3
        )
        return matches
