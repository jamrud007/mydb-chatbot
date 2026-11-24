"""Chat service skeleton for extracting chat flow from main.py endpoints."""
from typing import Any, Dict

from chatbot.chatbot_handler import ChatbotHandler


class ChatService:
    """
    Service facade around ChatbotHandler.

    Day 2 scope:
    - Define a stable service boundary used by API layer.
    - Keep behavior unchanged by delegating to existing handler.
    """

    def __init__(self, chatbot_handler: ChatbotHandler):
        self._chatbot = chatbot_handler

    def generate_queries(self, message: str, user_id: str) -> Dict[str, Any]:
        """Delegate natural-language request handling."""
        return self._chatbot.handle_user_message(message, user_id)

    def execute_suggested_query(self, query_index: int, user_id: str) -> Dict[str, Any]:
        """Delegate query execution by suggestion index."""
        return self._chatbot.execute_query_by_index(query_index, user_id)

    def get_handler(self) -> ChatbotHandler:
        """Temporary escape hatch for endpoints not migrated yet."""
        return self._chatbot

