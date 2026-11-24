"""
Query Generator - Orchestrates NL to SQL conversion
"""
import logging
from llm.prompt_templates import format_nl_to_sql_prompt

logger = logging.getLogger(__name__)

# Keyword → table mapping for relevance filtering
# Keeps schema small for low-context models (8K tokens)
# IMPORTANT: Be specific — avoid generic words that match multiple tables
TABLE_KEYWORDS = {
    'gate_transactions':     ['transaksi', 'transaction', 'status', 'gate_name', 'plate', 'plat',
                              'card_id', 'tag_number', 'gate_weight', 'autogate_status',
                              'ocr_completed', 'ocr_corrected', 'ocr_inprogess'],
    'gates':                 ['daftar gate', 'list gate', 'gate aktif', 'active gate',
                              'tipe gate', 'gate type', 'jumlah gate'],
    'gate_devices':          ['gate device', 'perangkat gate', 'kamera gate', 'device gate'],
    'gate_action_times':     ['action time', 'durasi gate', 'waktu aksi'],
    'gate_message_infos':    ['gate message', 'pesan gate'],
    'ocr_datas':             ['ocr data', 'data ocr', 'container', 'kontainer', 'iso_code',
                              'iso code', 'seal', 'chassis', 'axle', 'dg_code', 'flexi'],
    'ocr_images':            ['image', 'gambar', 'foto', 'photo', 'ocr image'],
    'ocr_autogate_accuracy': ['accuracy', 'akurasi', 'autogate accuracy'],
    'transaction_ocr_datas': ['transaction ocr', 'ocr transaksi', 'data ocr transaksi'],
    'etickets':              ['eticket', 'e-ticket', 'tiket', 'ticket', 'vessel', 'kapal',
                              'voyage', 'export', 'import', 'proforma', 'company_code'],
    'payment_infos':         ['payment', 'bayar', 'pembayaran'],
    'users':                 ['user', 'pengguna', 'login', 'username'],
    'fixed_ocr_datas':       ['fixed ocr', 'ocr fixed'],
    'flat_rack_bundle':      ['flat rack', 'bundle'],
}

MAX_TABLES = 5  # Maximum tables to send to LLM at once


def _pick_relevant_tables(question: str, all_table_names: list, max_tables: int = MAX_TABLES) -> list:
    """Score tables by keyword match and return top N."""
    q = question.lower()
    scores = {}
    for table in all_table_names:
        t = table.lower()
        score = 0
        # Direct table name mention
        if t in q or t.replace('_', ' ') in q:
            score += 10
        # Keyword match
        for kw in TABLE_KEYWORDS.get(t, []):
            if kw in q:
                score += 2
        scores[table] = score

    # Sort by score desc, keep tables with score > 0, fallback to top-scored
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    relevant = [t for t, s in ranked if s > 0][:max_tables]

    # If nothing matched, return the highest-scored tables anyway
    if not relevant:
        relevant = [t for t, _ in ranked[:3]]

    logger.info(f"Relevant tables for '{question[:60]}': {relevant}")
    return relevant


class QueryGenerator:
    """Generates SQL queries from natural language using LLM"""

    def __init__(self, llm_client, schema_manager):
        self.llm_client = llm_client
        self.schema_manager = schema_manager
        logger.info(f"QueryGenerator initialized with {llm_client.provider_name}")

    def generate_queries(self, user_question, conversation_context=""):
        """
        Generate SQL queries from natural language question.
        Only sends relevant tables to the LLM to reduce token usage.
        """
        try:
            # Pick only relevant tables based on the question
            schema = self.schema_manager.get_schema()
            all_tables = [t['name'] for t in schema['tables']]
            relevant = _pick_relevant_tables(user_question, all_tables)

            # Build filtered schema text
            schema_text = self.schema_manager.format_schema_for_llm(table_filter=relevant)

            # Create prompt
            prompt = format_nl_to_sql_prompt(
                user_question,
                schema_text,
                conversation_context
            )
            
            # Get response from LLM
            response = self.llm_client.get_response(prompt, expect_json=True)
            
            # Parse JSON response
            result = self.llm_client.parse_json_response(response)
            
            # Validate structure
            if 'error' in result:
                logger.error(f"Error in LLM response: {result['error']}")
                return {
                    'success': False,
                    'error': result['error'],
                    'suggested_queries': [],
                    'explanation': 'Failed to generate queries. Please try rephrasing your question.'
                }
            
            # Ensure suggested_queries exists
            if 'suggested_queries' not in result:
                result['suggested_queries'] = []
            
            # Ensure explanation exists
            if 'explanation' not in result:
                result['explanation'] = ''
            
            result['success'] = True
            
            logger.info(f"Generated {len(result['suggested_queries'])} query suggestions")
            return result
        
        except Exception as e:
            logger.error(f"Query generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'suggested_queries': [],
                'explanation': 'An error occurred while processing your question. Please try again.'
            }
