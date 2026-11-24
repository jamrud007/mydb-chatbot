"""
Conversation Manager - Manages chat history and context
"""
import logging
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationManager:
    """Manages conversation history and context for each user session"""
    
    def __init__(self, max_history=10):
        """
        Initialize conversation manager
        
        Args:
            max_history: Maximum number of exchanges to keep in history
        """
        self.max_history = max_history
        self.conversations = {}  # user_id -> conversation data
        logger.info(f"ConversationManager initialized (max_history={max_history})")
    
    def get_or_create_session(self, user_id='default'):
        """
        Get or create a conversation session
        
        Args:
            user_id: User identifier
        
        Returns:
            dict: Conversation session data
        """
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                'history': deque(maxlen=self.max_history),
                'suggested_queries': [],
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
            logger.info(f"Created new conversation session for user: {user_id}")
        
        # Update last activity
        self.conversations[user_id]['last_activity'] = datetime.now()
        
        return self.conversations[user_id]
    
    def add_exchange(self, user_id, user_message, bot_response, suggested_queries=None):
        """
        Add a conversation exchange to history
        
        Args:
            user_id: User identifier
            user_message: User's message
            bot_response: Bot's response
            suggested_queries: List of suggested queries (optional)
        """
        session = self.get_or_create_session(user_id)
        
        exchange = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response
        }
        
        session['history'].append(exchange)
        
        # Store suggested queries for potential execution
        if suggested_queries:
            session['suggested_queries'] = suggested_queries
        
        logger.info(f"Added exchange to conversation history for user: {user_id}")
    
    def get_history(self, user_id='default', num_exchanges=None):
        """
        Get conversation history
        
        Args:
            user_id: User identifier
            num_exchanges: Number of recent exchanges to return (None for all)
        
        Returns:
            list: Conversation history
        """
        session = self.get_or_create_session(user_id)
        history = list(session['history'])
        
        if num_exchanges:
            return history[-num_exchanges:]
        
        return history
    
    def get_context_string(self, user_id='default', num_exchanges=3):
        """
        Get conversation context as formatted string for LLM
        
        Args:
            user_id: User identifier
            num_exchanges: Number of recent exchanges to include
        
        Returns:
            str: Formatted context string
        """
        history = self.get_history(user_id, num_exchanges)
        
        if not history:
            return "No previous conversation"
        
        context_parts = []
        for i, exchange in enumerate(history, 1):
            context_parts.append(f"Exchange {i}:")
            context_parts.append(f"User: {exchange['user_message']}")
            context_parts.append(f"Bot: {exchange['bot_response'][:200]}...")  # Truncate long responses
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_suggested_queries(self, user_id='default'):
        """
        Get stored suggested queries for a user
        
        Args:
            user_id: User identifier
        
        Returns:
            list: Suggested queries
        """
        session = self.get_or_create_session(user_id)
        return session.get('suggested_queries', [])
    
    def update_suggested_queries(self, user_id='default', queries=None):
        """Replace suggested queries for the latest exchange (used after retry)."""
        session = self.get_or_create_session(user_id)
        session['suggested_queries'] = queries or []

    def clear_session(self, user_id='default'):
        """
        Clear conversation session for a user
        
        Args:
            user_id: User identifier
        """
        if user_id in self.conversations:
            del self.conversations[user_id]
            logger.info(f"Cleared conversation session for user: {user_id}")
    
    def get_all_sessions(self):
        """Get all active conversation sessions"""
        return list(self.conversations.keys())
