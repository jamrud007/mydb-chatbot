"""
Main Chatbot Handler - Orchestrates all components
"""
import json
import logging
from typing import Any, Dict, List

from chatbot.conversation_manager import ConversationManager
from config import Config
from database.db_connection import DatabaseConnection
from database.query_executor import QueryExecutor
from database.schema_manager import SchemaManager
from llm.llm_factory import LLMFactory
from llm.prompt_templates import format_data_analysis_prompt, format_error_explanation_prompt
from llm.query_clarifier import QueryClarifier
from llm.query_generator import QueryGenerator
from utils.sql_validator import SQLValidator
from utils.visualization_helper import VisualizationHelper

logger = logging.getLogger(__name__)

class ChatbotHandler:
    """Main chatbot orchestrator"""
    
    def __init__(self, use_fallback: bool = True) -> None:
        logger.info("Initializing ChatbotHandler...")
        
        # Initialize database components
        db_config = Config.get_db_config()
        self.db_connection = DatabaseConnection(db_config)
        self.schema_manager = SchemaManager(self.db_connection, Config.SCHEMA_CACHE_TTL)
        self.query_executor = QueryExecutor(
            self.db_connection,
            read_only=Config.READ_ONLY_MODE,
            max_rows=Config.MAX_QUERY_ROWS
        )
        
        # Initialize LLM client with factory
        try:
            # Direct creation - skip connection testing
            self.llm_client = LLMFactory.create_client()
            
            logger.info(f"Using AI provider: {self.llm_client.provider_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            raise
        
        # Initialize query generator
        self.query_generator = QueryGenerator(self.llm_client, self.schema_manager)
        
        # Initialize query clarifier (NEW)
        self.query_clarifier = QueryClarifier(self.llm_client, self.schema_manager)
        
        # Initialize conversation  manager
        self.conversation_manager = ConversationManager()
        
        # Initialize SQL validator
        self.sql_validator = SQLValidator(self.schema_manager)
        
        logger.info("ChatbotHandler initialized successfully")
    
    def test_connection(self) -> bool:
        """Test database connection"""
        return self.db_connection.test_connection()
    
    def handle_user_message(self, user_message: str, user_id: str = 'default') -> Dict[str, Any]:
        """Handle a user message and generate response."""
        logger.info(f"Handling message from user {user_id}: {user_message[:100]}")
        
        try:
            # NEW: Check for query ambiguity first
            clarification = self.query_clarifier.analyze_query(user_message)
            
            if clarification.get('is_ambiguous'):
                logger.info("Query is ambiguous, returning clarification options")
                return {
                    'success': True,
                    'type': 'clarification_needed',
                    'message': 'Pertanyaan Anda bisa diartikan beberapa cara. Silakan pilih maksud Anda:',
                    'clarification_options': clarification['options'],
                    'original_query': user_message
                }
            
            # EXISTING: Normal SQL generation flow
            # Get conversation context
            context = self.conversation_manager.get_context_string(user_id)
            
            # Generate SQL queries from natural language
            generation_result = self.query_generator.generate_queries(
                user_message,
                context
            )
            
            if not generation_result['success']:
                # If generation failed, create error response
                response = {
                    'success': False,
                    'message': generation_result.get('explanation', 'Failed to understand your question.'),
                    'suggested_queries': [],
                    'error': generation_result.get('error')
                }
            else:
                # Successful generation
                response = {
                    'success': True,
                    'type': 'sql_generated',
                    'message': generation_result.get('explanation', ''),
                    'suggested_queries': generation_result.get('suggested_queries', []),
                    'query_count': len(generation_result.get('suggested_queries', []))
                }
            
            # Add to conversation history
            self.conversation_manager.add_exchange(
                user_id,
                user_message,
                response['message'],
                response.get('suggested_queries', [])
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error handling user message: {e}")
            return {
                'success': False,
                'message': 'Maaf, terjadi kesalahan. Silakan coba lagi.',
                'suggested_queries': [],
                'error': str(e)
            }
    
    def execute_query_by_index(self, query_index: int, user_id: str = 'default') -> Dict[str, Any]:
        """Execute a suggested query by its index (0-based)."""
        logger.info(f"Executing query #{query_index} for user {user_id}")
        
        try:
            # Get suggested queries from conversation
            suggested_queries = self.conversation_manager.get_suggested_queries(user_id)
            
            if not suggested_queries or query_index >= len(suggested_queries):
                return {
                    'success': False,
                    'error': f'Invalid query index: {query_index}',
                    'message': 'Query tidak ditemukan. Silakan ajukan pertanyaan terlebih dahulu.'
                }
            
            # Get the selected query
            selected_query = suggested_queries[query_index]
            sql_query = selected_query['sql']
            cache_query = self.query_executor.get_cache_query(sql_query)
            
            # === VALIDATE SQL FIRST ===
            validation_result = self.sql_validator.validate_and_fix(sql_query)
            
            if not validation_result['valid']:
                error_type = validation_result.get('error_type')
                error_msg = validation_result['error']

                # Auto-retry on hallucinated columns or unknown tables
                if error_type in ('UNKNOWN_COLUMN', 'UNKNOWN_TABLE'):
                    logger.warning(f"Validation failed ({error_type}) — retrying query generation")
                    history = self.conversation_manager.get_history(user_id, num_exchanges=1)
                    user_question = history[0]['user_message'] if history else "Unknown question"
                    schema_text = self.schema_manager.format_schema_for_llm()
                    retry_context = (
                        f"PERHATIAN: query sebelumnya gagal validasi.\n"
                        f"Error: {error_msg}\n"
                        f"WAJIB gunakan HANYA nama tabel dan kolom yang ada di schema berikut:\n{schema_text}"
                    )
                    retry_result = self.query_generator.generate_queries(user_question, retry_context)
                    if retry_result['success'] and retry_result.get('suggested_queries'):
                        sql_query = retry_result['suggested_queries'][0]['sql']
                        self.conversation_manager.update_suggested_queries(user_id, retry_result['suggested_queries'])
                        validation_result = self.sql_validator.validate_and_fix(sql_query)
                        error_type = validation_result.get('error_type')
                        error_msg = validation_result.get('error', '')
                        logger.info(f"Retry validation: valid={validation_result['valid']}, sql={sql_query[:80]}")

                if not validation_result['valid']:
                    if error_type == 'UNSAFE_OPERATION':
                        friendly_msg = "⚠️ **Operasi Tidak Diizinkan**\n\nQuery mengandung operasi berbahaya. Hanya SELECT yang diperbolehkan."
                    elif error_type == 'UNKNOWN_TABLE':
                        friendly_msg = f"⚠️ **Tabel Tidak Ditemukan**\n\n{error_msg}"
                    elif error_type == 'UNKNOWN_COLUMN':
                        friendly_msg = f"⚠️ **Kolom Tidak Ditemukan**\n\n{error_msg}"
                    else:
                        friendly_msg = f"⚠️ **Validasi Gagal**\n\n{error_msg}"

                    logger.warning(f"SQL validation failed after retry: {error_type} - {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg,
                        'error_type': error_type,
                        'message': friendly_msg,
                        'sql_query': sql_query,
                        'validation': validation_result
                    }
            
            # Use fixed SQL if corrections were made
            fixed_sql = validation_result['fixed_sql']
            sql_corrections = validation_result.get('corrections', [])
            
            if sql_corrections:
                corrections_msg = "\n".join([
                    f"✅ Auto-corrected: '{c['original']}' → '{c['corrected']}'"
                    for c in sql_corrections
                ])
                logger.info(f"Applied SQL corrections:\n{corrections_msg}")
                # Update to use fixed SQL
                sql_query = fixed_sql
            
            # Prepare summary for caching
            original_explanation = selected_query.get('explanation', '')
            
            # Get original user question for caching context
            history = self.conversation_manager.get_history(user_id, num_exchanges=1)
            original_question = history[0]['user_message'] if history else "Unknown question"
            
            logger.info(f"Executing SQL: {sql_query[:100]}...")
            
            # Execute the query (passing explanation and question for caching)
            exec_result = self.query_executor.execute(
                sql_query, 
                user_id=user_id, 
                nl_summary=original_explanation,  # Store original explanation in cache
                user_question=original_question
            )
            
            if not exec_result['success']:
                history = self.conversation_manager.get_history(user_id, 1)
                user_question = history[-1]['user_message'] if history else "your question"

                # Auto-retry on ORA-00904 (invalid identifier / hallucinated column)
                if 'ORA-00904' in exec_result.get('error', ''):
                    logger.warning(f"ORA-00904 detected — retrying query generation with stricter prompt")
                    schema_text = self.schema_manager.format_schema_for_llm()
                    retry_context = (
                        f"PERHATIAN: query sebelumnya gagal karena kolom tidak valid.\n"
                        f"Error: {exec_result['error']}\n"
                        f"WAJIB gunakan HANYA nama kolom yang ada di schema berikut:\n{schema_text}"
                    )
                    retry_result = self.query_generator.generate_queries(user_question, retry_context)
                    if retry_result['success'] and retry_result.get('suggested_queries'):
                        retry_sql = retry_result['suggested_queries'][0]['sql']
                        logger.info(f"Retry SQL: {retry_sql[:100]}...")
                        exec_result = self.query_executor.execute(
                            retry_sql,
                            user_id=user_id,
                            nl_summary=retry_result['suggested_queries'][0].get('explanation', ''),
                            user_question=user_question
                        )
                        if exec_result['success']:
                            sql_query = retry_sql
                            original_explanation = retry_result['suggested_queries'][0].get('explanation', '')
                            # Update suggested queries in conversation so index stays valid
                            self.conversation_manager.update_suggested_queries(user_id, retry_result['suggested_queries'])

                if not exec_result['success']:
                    error_prompt = format_error_explanation_prompt(user_question, exec_result['error'])
                    friendly_error = self.llm_client.get_response(error_prompt, expect_json=False)
                    return {
                        'success': False,
                        'error': exec_result['error'],
                        'message': friendly_error,
                        'sql_query': sql_query
                    }
            
            # Format results as table
            table_result = self.query_executor.format_results_as_table(exec_result)
            
            row_count = exec_result['row_count']
            
            # DISPLAY Summary (not cached - for UI only)
            # Use cached summary if available, otherwise use original explanation
            if exec_result.get('nl_summary'):
                # Retrieved from cache - use stored summary
                base_summary = exec_result['nl_summary']
            else:
                # Fresh query - use original explanation
                base_summary = original_explanation

            # Construct FINAL DISPLAY summary with row count
            summary_from_cache = bool(exec_result.get('summary_analysis'))
            if summary_from_cache:
                # Use fully composed summary when already available from cache.
                nl_summary = exec_result.get('summary_analysis', '')
            elif row_count > 0:
                nl_summary = f"{base_summary}\n\n✅ **Hasil:** Ditemukan {row_count} data."
            else:
                nl_summary = f"{base_summary}\n\n⚠️ **Hasil:** Tidak ada data yang ditemukan untuk kriteria ini."
            
            # Get original user question for context (from last exchange)
            history = self.conversation_manager.get_history(user_id, num_exchanges=1)
            original_query = history[0]['user_message'] if history else ''
            
            # Analyze for visualization with user query context
            viz_config = VisualizationHelper.analyze_for_visualization(
                exec_result['rows'],
                exec_result['columns'],
                user_query=original_query
            )
            
            # NOTE: Auto-analysis is intentionally omitted here.
            # It is enqueued as a BackgroundTask by the API layer after this method returns,
            # so the user receives query results without waiting for the LLM analysis call.
            # See: chatbot_handler.generate_analysis() + main.py execute_query endpoint.

            # Use cached analysis if available (cache hit path)
            analysis_text = exec_result.get('analysis', '')
            if analysis_text and not summary_from_cache and "🤖 **Analisis Otomatis:**" not in nl_summary:
                nl_summary += f"\n\n🤖 **Analisis Otomatis:**\n{analysis_text}"

            # --- CACHE VISUALIZATION ---
            # Now that we have the gold-standard visualization config, save it to cache
            # so next time we load from cache, we get this exact same config (preserving dual axis etc)
            if viz_config and viz_config.get('can_visualize'):
                if self.query_executor.cache_manager:
                    self.query_executor.cache_manager.update_visualization(cache_query, viz_config)

            # Store final composed summary text for reliable cache replay.
            if self.query_executor.cache_manager:
                self.query_executor.cache_manager.update_summary_analysis(cache_query, nl_summary)

            return {
                'success': True,
                'sql_query': sql_query,
                'results': exec_result['rows'],
                'columns': exec_result['columns'],
                'row_count': exec_result['row_count'],
                'table_formatted': table_result,
                'nl_summary': nl_summary,
                'limited': exec_result.get('limited', False),
                'visualization': viz_config
            }
        
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Terjadi kesalahan saat menjalankan query. Silakan coba lagi.'
            }
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            schema = self.schema_manager.get_schema()
            return {
                'success': True,
                'schema': schema
            }
        except Exception as e:
            logger.error(f"Error getting schema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_analysis(
        self,
        cache_query: str,
        question: str,
        columns: List[str],
        rows: List[Any],
    ) -> str:
        """Run auto-analysis LLM call and persist result to cache. Designed to run in background.

        Returns the generated analysis text, or "" on failure.
        """
        try:
            logger.info("Background: generating data analysis insight...")
            sample_data = rows[:20]
            data_str = json.dumps(sample_data, indent=2, default=str)
            analysis_prompt = format_data_analysis_prompt(
                question=question,
                columns=columns,
                data=data_str,
            )
            analysis_text = self.llm_client.get_response(analysis_prompt, expect_json=False)
            if self.query_executor.cache_manager:
                self.query_executor.cache_manager.update_analysis(cache_query, analysis_text)
            logger.info("Background: analysis complete.")
            return analysis_text
        except Exception as e:
            logger.error(f"Background: analysis failed: {e}")
            return ""

    def refresh_schema(self) -> Dict[str, Any]:
        """Force refresh of database schema cache"""
        try:
            self.schema_manager.get_schema(force_refresh=True)
            return {
                'success': True,
                'message': 'Schema cache refreshed successfully'
            }
        except Exception as e:
            logger.error(f"Error refreshing schema: {e}")
            return {
                'success': False,
                'error': str(e)
            }
