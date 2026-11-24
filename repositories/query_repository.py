"""Repository pattern pilot: wraps QueryExecutor with a clean data-access interface."""
from typing import Any, Dict, Optional, Tuple

from database.query_executor import QueryExecutor


class QueryRepository:
    """
    Data-access boundary for SQL query execution.

    Wraps QueryExecutor so the service layer never imports
    database internals directly.
    """

    def __init__(self, query_executor: QueryExecutor):
        self._executor = query_executor

    def validate(self, query: str) -> Tuple[bool, Optional[str]]:
        """Return (is_valid, error_message)."""
        return self._executor.validate_query(query)

    def execute(
        self,
        query: str,
        *,
        use_cache: bool = True,
        user_id: str = "unknown",
        nl_summary: str = "",
        user_question: str = "",
        analysis: str = "",
        summary_analysis: str = "",
    ) -> Dict[str, Any]:
        """Execute a validated SQL query and return the result dict."""
        return self._executor.execute(
            query,
            use_cache=use_cache,
            user_id=user_id,
            nl_summary=nl_summary,
            user_question=user_question,
            analysis=analysis,
            summary_analysis=summary_analysis,
        )

    def get_cache_key(self, query: str) -> str:
        """Return the canonical query string used for cache-key generation."""
        return self._executor.get_cache_query(query)
