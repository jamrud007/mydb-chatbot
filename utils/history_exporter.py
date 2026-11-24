"""
Query History Export Utility
Exports conversation history and query results in multiple formats
"""
import json
import csv
import io
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class HistoryExporter:
    """
    Export conversation history and query results
    Supports JSON, CSV, and text formats
    """
    
    def __init__(self, conversation_manager, cache_manager=None):
        """
        Initialize history exporter
        
        Args:
            conversation_manager: ConversationManager instance
            cache_manager: CacheManager instance (optional, for query results)
        """
        self.conversation_manager = conversation_manager
        self.cache_manager = cache_manager
        logger.info("HistoryExporter initialized")
    
    def export_conversation_json(self, user_id: str = 'default') -> str:
        """
        Export conversation history as JSON
        
        Args:
            user_id: User identifier
        
        Returns:
            str: JSON string
        """
        history = self.conversation_manager.get_history(user_id)
        session = self.conversation_manager.get_or_create_session(user_id)
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'session_created_at': session['created_at'].isoformat(),
            'total_exchanges': len(history),
            'conversations': history
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def export_conversation_csv(self, user_id: str = 'default') -> str:
        """
        Export conversation history as CSV
        
        Args:
            user_id: User identifier
        
        Returns:
            str: CSV string
        """
        history = self.conversation_manager.get_history(user_id)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Timestamp', 'User Message', 'Bot Response'])
        
        # Write data
        for exchange in history:
            writer.writerow([
                exchange.get('timestamp', ''),
                exchange.get('user_message', ''),
                exchange.get('bot_response', '')
            ])
        
        return output.getvalue()
    
    def export_conversation_text(self, user_id: str = 'default') -> str:
        """
        Export conversation history as readable text
        
        Args:
            user_id: User identifier
        
        Returns:
            str: Formatted text
        """
        history = self.conversation_manager.get_history(user_id)
        session = self.conversation_manager.get_or_create_session(user_id)
        
        lines = []
        lines.append("="*70)
        lines.append("QUERY HISTORY EXPORT")
        lines.append("="*70)
        lines.append(f"User ID: {user_id}")
        lines.append(f"Session Created: {session['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Conversations: {len(history)}")
        lines.append("="*70)
        lines.append("")
        
        for i, exchange in enumerate(history, 1):
            timestamp = exchange.get('timestamp', 'Unknown')
            lines.append(f"[{i}] {timestamp}")
            lines.append(f"User: {exchange.get('user_message', '')}")
            lines.append(f"Bot: {exchange.get('bot_response', '')}")
            lines.append("-"*70)
            lines.append("")
        
        return "\n".join(lines)
    
    def export_query_results_json(self, user_id: str = 'default', limit: int = 50) -> str:
        """
        Export cached query results as JSON
        
        Args:
            user_id: User identifier
            limit: Maximum number of results to export
        
        Returns:
            str: JSON string with query results
        """
        if not self.cache_manager:
            return json.dumps({
                'error': 'Cache manager not available',
                'results': []
            })
        
        # Get all cached results for user
        all_results = self.cache_manager.get_all_results(user_id=user_id, limit=limit)
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'total_results': len(all_results),
            'query_results': all_results
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    def export_full_history_json(self, user_id: str = 'default') -> str:
        """
        Export complete history (conversations + query results) as JSON
        
        Args:
            user_id: User identifier
        
        Returns:
            str: Complete JSON export
        """
        conversation_history = self.conversation_manager.get_history(user_id)
        session = self.conversation_manager.get_or_create_session(user_id)
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'session_created_at': session['created_at'].isoformat(),
            'conversations': {
                'total': len(conversation_history),
                'history': conversation_history
            }
        }
        
        # Add query results if cache manager available
        if self.cache_manager:
            results = self.cache_manager.get_all_results(user_id=user_id, limit=50)
            export_data['query_results'] = {
                'total': len(results),
                'results': results
            }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    def get_export_stats(self, user_id: str = 'default') -> Dict:
        """
        Get statistics about exportable data
        
        Args:
            user_id: User identifier
        
        Returns:
            dict: Export statistics
        """
        history = self.conversation_manager.get_history(user_id)
        session = self.conversation_manager.get_or_create_session(user_id)
        
        stats = {
            'user_id': user_id,
            'total_conversations': len(history),
            'session_created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat(),
            'available_formats': ['json', 'csv', 'text']
        }
        
        if self.cache_manager:
            cached_results = self.cache_manager.get_all_results(user_id=user_id, limit=100)
            stats['total_cached_queries'] = len(cached_results)
        else:
            stats['total_cached_queries'] = 0
        
        return stats
