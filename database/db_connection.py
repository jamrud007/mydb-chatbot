"""
Database Connection Handler (MySQL / Oracle / Any SQL DB)
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

from exceptions.chatbot_exceptions import DatabaseConnectionError, SQLExecutionError

try:
    import mysql.connector
    from mysql.connector import pooling as mysql_pooling
except Exception:  # pragma: no cover - optional dependency path
    mysql = None
    mysql_pooling = None

try:
    import oracledb
except Exception:  # pragma: no cover - optional dependency path
    oracledb = None

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages MySQL/Oracle database connections with pooling"""

    def __init__(self, db_config: Dict[str, Any], pool_size: int = 5) -> None:
        self.db_config = db_config
        self.pool_size = pool_size
        self.engine = db_config.get('engine', 'mysql').lower()
        self.connection_pool: Any = None
        self._create_pool()

    def _create_pool(self) -> None:
        """Create connection pool"""
        try:
            if self.engine == 'oracle':
                if oracledb is None:
                    raise RuntimeError("oracledb package is not installed")

                self.connection_pool = oracledb.create_pool(
                    user=self.db_config.get('user'),
                    password=self.db_config.get('password'),
                    dsn=self.db_config.get('dsn'),
                    min=1,
                    max=self.pool_size,
                    increment=1
                )
                logger.info("Oracle connection pool created successfully")
                return

            if mysql_pooling is None:
                raise RuntimeError("mysql-connector-python package is not installed")

            mysql_cfg = {
                'host': self.db_config.get('host'),
                'port': self.db_config.get('port'),
                'user': self.db_config.get('user'),
                'password': self.db_config.get('password'),
                'database': self.db_config.get('database')
            }
            self.connection_pool = mysql_pooling.MySQLConnectionPool(
                pool_name="chatbot_pool",
                pool_size=self.pool_size,
                pool_reset_session=True,
                **mysql_cfg
            )
            logger.info("MySQL connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise DatabaseConnectionError(
                self.db_config.get('host', 'unknown'),
                self.db_config.get('database') or self.db_config.get('schema', 'unknown'),
                e
            )

    def get_connection(self) -> Any:
        """Get a connection from the pool."""
        try:
            if self.engine == 'oracle':
                return self.connection_pool.acquire()
            return self.connection_pool.get_connection()
        except Exception as e:
            logger.error(f"Failed to get connection from pool: {e}")
            raise DatabaseConnectionError(
                self.db_config.get('host', 'unknown'),
                self.db_config.get('database') or self.db_config.get('schema', 'unknown'),
                e
            )

    def test_connection(self) -> bool:
        """Test database connectivity."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.engine == 'oracle':
                cursor.execute("SELECT 1 FROM dual")
            else:
                cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise DatabaseConnectionError(
                self.db_config.get('host', 'unknown'),
                self.db_config.get('database') or self.db_config.get('schema', 'unknown'),
                e
            )

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Tuple[List[str], List[Tuple]]:
        """Execute query and return (column_names, rows)."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            from config import Config
            timeout_ms = max(1000, Config.QUERY_TIMEOUT_SECONDS * 1000)

            if self.engine == 'mysql':
                # MySQL specific statement timeout
                cursor.execute(f"SET SESSION max_execution_time = {timeout_ms}")
            else:
                # Oracle call timeout in milliseconds
                try:
                    conn.call_timeout = timeout_ms
                except Exception:
                    pass

            if params is not None:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()

            return columns, rows
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise SQLExecutionError(query, e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def close(self) -> None:
        """Close connection pool"""
        if not self.connection_pool:
            return

        try:
            if self.engine == 'oracle':
                self.connection_pool.close()
            logger.info("Database connection pool closed")
        except Exception as e:
            logger.warning(f"Error closing connection pool: {e}")
