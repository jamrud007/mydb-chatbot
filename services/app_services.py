"""Application service container skeleton for dependency wiring."""
from dataclasses import dataclass
from typing import Optional

from chatbot.chatbot_handler import ChatbotHandler
from database.db_connection import DatabaseConnection
from database.query_executor import QueryExecutor
from database.user_manager import UserManager
from repositories.query_repository import QueryRepository
from services.chat_service import ChatService
from utils.metrics import get_metrics_collector
from utils.rate_limiter import RateLimiter
from utils.results_cache import ResultsCache
from core.config import Config


@dataclass
class AppServices:
    """Centralized service/repository dependencies for API layer."""

    chatbot_handler: ChatbotHandler
    chat_service: ChatService
    rate_limiter: RateLimiter
    results_cache: ResultsCache
    metrics_collector: object
    user_manager: UserManager
    query_repository: QueryRepository


def build_app_services() -> Optional[AppServices]:
    """
    Build application services.

    Returns None if initialization fails to preserve existing startup semantics.
    """
    try:
        chatbot_handler = ChatbotHandler()
        rate_limiter = RateLimiter(
            max_requests=Config.MAX_REQUESTS_PER_MINUTE,
            time_window=Config.RATE_LIMIT_TIME_WINDOW,
        )
        results_cache = ResultsCache(ttl_seconds=Config.RESULTS_CACHE_TTL)
        metrics_collector = get_metrics_collector(window_minutes=Config.METRICS_WINDOW_MINUTES)

        db_conn = DatabaseConnection(Config.get_db_config())
        user_manager = UserManager(db_conn)
        query_executor = QueryExecutor(db_conn)
        query_repository = QueryRepository(query_executor)

        chat_service = ChatService(chatbot_handler)
        return AppServices(
            chatbot_handler=chatbot_handler,
            chat_service=chat_service,
            rate_limiter=rate_limiter,
            results_cache=results_cache,
            metrics_collector=metrics_collector,
            user_manager=user_manager,
            query_repository=query_repository,
        )
    except Exception:
        return None

