"""
Query Clarification Module
Detects ambiguous queries and generates clarification options
"""
import re
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class QueryClarifier:
    """Analyzes user queries for ambiguity and generates clarification options"""
    
    # Ambiguous patterns that require clarification
    AMBIGUOUS_PATTERNS = {
        'multi_dimension': [
            r'by\s+\w+\s+and\s+\w+\s+(?!by)',  # "by category and city" but NOT "by category and by city"
            r'per\s+\w+\s+dan\s+\w+\s+(?!per)',  # "per kategori dan kota"
        ],
        'vague_metric': [
            # Only match truly vague queries without numbers or specific metrics
            r'\btop\s+(?!(\d+|ten|five|three)\s)',  # "top products" but NOT "top 7" or "top ten"
            r'\bshow\s+\w+\s*$',  # "show sales" (ends abruptly, no details)
            r'^\s*data\s+\w+\s*$',  # "data customer" alone (too vague)
        ],
        'unclear_aggregation': [
            r'total.*and.*per\s+\w+\s+and',  # Multiple aggregations
        ]
    }
    
    def __init__(self, llm_client, schema_manager):
        """
        Initialize query clarifier
        
        Args:
            llm_client: LLM client for generating clarification options
            schema_manager: Database schema for context
        """
        self.llm_client = llm_client
        self.schema_manager = schema_manager
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query for ambiguity
        
        Args:
            query: User's natural language query
            
        Returns:
            {
                'is_ambiguous': bool,
                'reason': str,
                'pattern_type': str,
                'options': List[Dict]
            }
        """
        logger.info(f"Analyzing query for ambiguity: {query}")
        
        # Detect ambiguous patterns
        detected_patterns = self._detect_patterns(query)
        
        if not detected_patterns:
            logger.info("Query is clear, no ambiguity detected")
            return {'is_ambiguous': False}
        
        logger.info(f"Ambiguous patterns detected: {detected_patterns}")
        
        # Generate clarification options using LLM
        try:
            options = self._generate_clarification_options(query, detected_patterns)
            
            return {
                'is_ambiguous': True,
                'reason': f"Query contains {detected_patterns[0]['type']} ambiguity",
                'pattern_type': detected_patterns[0]['type'],
                'options': options
            }
        except Exception as e:
            logger.error(f"Error generating clarification options: {e}")
            # Fallback to pattern-based generic options
            return {
                'is_ambiguous': True,
                'reason': f"Query may be ambiguous ({detected_patterns[0]['type']})",
                'pattern_type': detected_patterns[0]['type'],
                'options': self._get_fallback_options(detected_patterns[0]['type'])
            }
    
    def _detect_patterns(self, query: str) -> List[Dict]:
        """
        Detect ambiguous patterns in query
        
        Returns:
            List of detected patterns with type
        """
        detected = []
        query_lower = query.lower()
        
        for pattern_type, patterns in self.AMBIGUOUS_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    detected.append({
                        'type': pattern_type,
                        'pattern': pattern,
                        'match': re.search(pattern, query_lower).group()
                    })
        
        return detected
    
    def _generate_clarification_options(self, query: str, patterns: List[Dict]) -> List[Dict]:
        """
        Use LLM to generate clarification options
        
        Args:
            query: Original user query
            patterns: Detected ambiguous patterns
            
        Returns:
            List of clarification options
        """
        # Get schema info for context
        schema_info = self._get_schema_context()
        pattern_type = patterns[0]['type']
        
        prompt = self._build_clarification_prompt(query, pattern_type, schema_info)
        
        logger.info("Generating clarification options with LLM")
        
        # Call LLM to generate options
        response = self.llm_client.get_response(prompt)
        
        # Parse LLM response to extract options
        options = self._parse_llm_options(response)
        
        # Ensure we have 2-3 options
        if len(options) < 2:
            options.extend(self._get_fallback_options(pattern_type))
        
        return options[:3]  # Max 3 options
    
    def _build_clarification_prompt(self, query: str, pattern_type: str, schema_info: str) -> str:
        """Build prompt for LLM to generate clarification options"""
        
        if pattern_type == 'multi_dimension':
            instruction = """
The user's query mentions multiple dimensions (e.g., "by category and city").
Generate 3 different interpretations:
1. Aggregate by first dimension only
2. Aggregate by second dimension only  
3. Show breakdown of both dimensions
"""
        elif pattern_type == 'vague_metric':
            instruction = """
The user's query is vague about the metric (e.g., "top products").
Generate 3 interpretations with different metrics:
1. Top by count/quantity
2. Top by revenue/value
3. Top by rating/quality
"""
        else:
            instruction = """
The user's query has unclear aggregation.
Generate 3 interpretations with different aggregation approaches.
"""
        
        return f"""You are a SQL query clarification assistant.

User Query: "{query}"

Database Schema Summary:
{schema_info}

{instruction}

For each interpretation, provide:
1. Clear description of what it means
2. A refined natural language query example
3. Expected chart type (bar/line/pie/table)

Return ONLY valid JSON in this format:
{{
  "options": [
    {{
      "interpretation": "Total sales per category (all cities combined)",
      "example_query": "Show total sales for each product category",
      "chart_type": "bar"
    }}
  ]
}}
"""
    
    def _get_schema_context(self) -> str:
        """Get relevant schema information"""
        try:
            # Get table names and key columns
            schema = self.schema_manager.get_schema()
            
            # Summarize schema
            summary = "Tables: "
            table_names = [table['name'] for table in schema.get('tables', [])]
            summary += ", ".join(table_names[:5])  # First 5 tables
            
            return summary
        except Exception as e:
            logger.warning(f"Could not get schema context: {e}")
            return "E-commerce database with products, orders, customers"
    
    def _parse_llm_options(self, llm_response: str) -> List[Dict]:
        """
        Parse LLM response to extract options
        
        Args:
            llm_response: Raw LLM response text
            
        Returns:
            List of option dicts
        """
        import json
        
        try:
            # Try to find JSON in response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                if 'options' in parsed:
                    return parsed['options']
            
            logger.warning("Could not parse LLM response as JSON")
            return []
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return []
    
    def _get_fallback_options(self, pattern_type: str) -> List[Dict]:
        """
        Get generic fallback options when LLM fails
        
        Args:
            pattern_type: Type of ambiguity detected
            
        Returns:
            List of generic options
        """
        if pattern_type == 'multi_dimension':
            return [
                {
                    'interpretation': 'Aggregate by first dimension',
                    'example_query': 'Show totals grouped by the first category mentioned',
                    'chart_type': 'bar'
                },
                {
                    'interpretation': 'Aggregate by second dimension',
                    'example_query': 'Show totals grouped by the second category mentioned',
                    'chart_type': 'bar'
                }
            ]
        elif pattern_type == 'vague_metric':
            return [
                {
                    'interpretation': 'Top by count/quantity',
                    'example_query': 'Show items with highest number of occurrences',
                    'chart_type': 'bar'
                },
                {
                    'interpretation': 'Top by value/revenue',
                    'example_query': 'Show items with highest total value',
                    'chart_type': 'bar'
                }
            ]
        else:
            return [
                {
                    'interpretation': 'Simple aggregation',
                    'example_query': 'Show summary with single grouping',
                    'chart_type': 'bar'
                },
                {
                    'interpretation': 'Detailed breakdown',
                    'example_query': 'Show detailed data table',
                    'chart_type': 'table'
                }
            ]
