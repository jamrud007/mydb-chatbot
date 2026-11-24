"""
Query Suggestion Engine
Provides autocomplete suggestions based on schema, history, and common patterns
"""
import logging
import re
from typing import List, Dict, Optional
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

class QuerySuggestionEngine:
    """
    Intelligent query suggestion and autocomplete system
    
    Provides suggestions based on:
    - Schema (tables, columns)
    - User query history
    - Common query patterns
    - Popular queries across all users
    """
    
    # Common query patterns
    COMMON_PATTERNS = [
        "SELECT * FROM {table}",
        "SELECT COUNT(*) FROM {table}",
        "SELECT {column} FROM {table}",
        "SELECT * FROM {table} WHERE {column} = ",
        "SELECT * FROM {table} ORDER BY {column}",
        "SELECT * FROM {table} LIMIT 10",
        "SELECT {column}, COUNT(*) FROM {table} GROUP BY {column}",
        "SELECT AVG({column}) FROM {table}",
        "SELECT SUM({column}) FROM {table}",
        "SELECT MIN({column}), MAX({column}) FROM {table}",
    ]
    
    # Common question patterns (natural language)
    QUESTION_TEMPLATES = {
        'id': [
            "Berapa total {column} di {table}?",
            "Tampilkan semua data dari {table}",
            "Siapa {column} dengan {column2} terbanyak?",
            "Berapa rata-rata {column} di {table}?",
            "Apa {column} tertinggi di {table}?",
            "Tampilkan 10 {table} teratas",
            "Berapa banyak {table} yang ada?",
        ],
        'en': [
            "What is the total {column} in {table}?",
            "Show all data from {table}",
            "Who has the most {column2} in {table}?",
            "What is the average {column} in {table}?",
            "What is the highest {column} in {table}?",
            "Show top 10 {table}",
            "How many {table} are there?",
        ]
    }
    
    def __init__(self, schema_manager, conversation_manager=None):
        """
        Initialize suggestion engine
        
        Args:
            schema_manager: SchemaManager instance for schema info
            conversation_manager: ConversationManager for query history (optional)
        """
        self.schema_manager = schema_manager
        self.conversation_manager = conversation_manager
        self.query_history = defaultdict(list)  # user_id -> [queries]
        self.popular_queries = Counter()  # All queries with frequency
        logger.info("QuerySuggestionEngine initialized")
    
    def get_schema_suggestions(self, partial_query: str, limit: int = 10) -> List[Dict]:
        """
        Get schema-based suggestions (tables, columns)
        
        Args:
            partial_query: Partial user input
            limit: Maximum suggestions
        
        Returns:
            list: Suggestion dictionaries
        """
        suggestions = []
        partial_lower = partial_query.lower()
        schema = self.schema_manager.get_schema()
        
        # Suggest tables
        for table in schema['tables']:
            table_name = table['name']
            if partial_lower in table_name.lower():
                suggestions.append({
                    'type': 'table',
                    'value': table_name,
                    'display': f"📊 {table_name}",
                    'description': f"Table with {len(table['columns'])} columns",
                    'score': 100 - len(partial_query)  # Shorter input = higher score
                })
                
                # Suggest columns from this table
                for col in table['columns'][:5]:  # Top 5 columns
                    col_name = col['name']
                    if partial_lower in col_name.lower():
                        suggestions.append({
                            'type': 'column',
                            'value': col_name,
                            'display': f"  🔹 {table_name}.{col_name}",
                            'description': f"{col['type']} column",
                            'score': 90 - len(partial_query)
                        })
        
        # Sort by score
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:limit]
    
    def get_pattern_suggestions(self, partial_query: str, limit: int = 5) -> List[Dict]:
        """
        Get common SQL pattern suggestions
        
        Args:
            partial_query: Partial user input
            limit: Maximum suggestions
        
        Returns:
            list: Pattern suggestions
        """
        suggestions = []
        schema = self.schema_manager.get_schema()
        
        # Get first table for examples
        if not schema['tables']:
            return []
        
        first_table = schema['tables'][0]
        table_name = first_table['name']
        first_col = first_table['columns'][0]['name'] if first_table['columns'] else 'id'
        
        for pattern in self.COMMON_PATTERNS[:limit]:
            # Fill in placeholders
            filled = pattern.replace('{table}', table_name).replace('{column}', first_col)
            
            suggestions.append({
                'type': 'pattern',
                'value': filled,
                'display': f"💡 {filled}",
                'description': 'Common SQL pattern',
                'score': 80
            })
        
        return suggestions
    
    def get_question_suggestions(self, language: str = 'id', limit: int = 5) -> List[Dict]:
        """
        Get natural language question suggestions
        
        Args:
            language: Language code (id, en)
            limit: Maximum suggestions
        
        Returns:
            list: Question suggestions
        """
        suggestions = []
        schema = self.schema_manager.get_schema()
        
        if not schema['tables']:
            return []
        
        templates = self.QUESTION_TEMPLATES.get(language, self.QUESTION_TEMPLATES['id'])
        first_table = schema['tables'][0]
        table_name = first_table['name']
        
        # Get numeric column for aggregations
        numeric_col = None
        text_col = None
        for col in first_table['columns']:
            if col['type'] in ['int', 'decimal', 'float', 'double']:
                numeric_col = col['name']
            elif col['type'] in ['varchar', 'text']:
                text_col = col['name']
        
        for template in templates[:limit]:
            # Fill in placeholders
            filled = template.replace('{table}', table_name)
            if numeric_col:
                filled = filled.replace('{column}', numeric_col)
            if text_col:
                filled = filled.replace('{column2}', text_col)
            
            suggestions.append({
                'type': 'question',
                'value': filled,
                'display': f"❓ {filled}",
                'description': 'Example question',
                'score': 70
            })
        
        return suggestions
    
    def get_history_suggestions(self, user_id: str = 'default', limit: int = 5) -> List[Dict]:
        """
        Get suggestions from user's query history
        
        Args:
            user_id: User identifier
            limit: Maximum suggestions
        
        Returns:
            list: History-based suggestions
        """
        suggestions = []
        
        if not self.conversation_manager:
            return suggestions
        
        # Get user's conversation history
        history = self.conversation_manager.get_history(user_id)
        
        # Extract questions
        questions = [ex['user_message'] for ex in history[-10:]]  # Last 10
        
        for i, question in enumerate(reversed(questions[:limit])):
            suggestions.append({
                'type': 'history',
                'value': question,
                'display': f"🕐 {question[:60]}...",
                'description': 'From your history',
                'score': 60 - i  # More recent = higher score
            })
        
        return suggestions
    
    def get_popular_suggestions(self, limit: int = 5) -> List[Dict]:
        """
        Get most popular queries across all users
        
        Args:
            limit: Maximum suggestions
        
        Returns:
            list: Popular query suggestions
        """
        suggestions = []
        
        # Get most common queries
        for query, count in self.popular_queries.most_common(limit):
            suggestions.append({
                'type': 'popular',
                'value': query,
                'display': f"🔥 {query[:60]}...",
                'description': f"Used {count} times",
                'score': 50 + count
            })
        
        return suggestions
    
    def get_suggestions(self, partial_query: str, user_id: str = 'default', 
                       language: str = 'id', limit: int = 10) -> List[Dict]:
        """
        Get comprehensive suggestions combining all sources
        
        Args:
            partial_query: Partial user input
            user_id: User identifier
            language: Language code
            limit: Maximum total suggestions
        
        Returns:
            list: Combined suggestions sorted by relevance
        """
        all_suggestions = []
        
        if not partial_query or len(partial_query) < 2:
            # No input - show popular, history, and examples
            all_suggestions.extend(self.get_history_suggestions(user_id, limit=3))
            all_suggestions.extend(self.get_question_suggestions(language, limit=4))
            all_suggestions.extend(self.get_popular_suggestions(limit=3))
        else:
            # Has input - prioritize schema matches
            all_suggestions.extend(self.get_schema_suggestions(partial_query, limit=5))
            all_suggestions.extend(self.get_pattern_suggestions(partial_query, limit=3))
            all_suggestions.extend(self.get_history_suggestions(user_id, limit=2))
        
        # Remove duplicates
        seen = set()
        unique_suggestions = []
        for sug in all_suggestions:
            if sug['value'] not in seen:
                seen.add(sug['value'])
                unique_suggestions.append(sug)
        
        # Sort by score
        unique_suggestions.sort(key=lambda x: x['score'], reverse=True)
        
        return unique_suggestions[:limit]
    
    def record_query(self, query: str, user_id: str = 'default'):
        """
        Record a query for future suggestions
        
        Args:
            query: User's query
            user_id: User identifier
        """
        self.query_history[user_id].append(query)
        self.popular_queries[query] += 1
        
        # Keep only last 100 per user
        if len(self.query_history[user_id]) > 100:
            self.query_history[user_id] = self.query_history[user_id][-100:]
