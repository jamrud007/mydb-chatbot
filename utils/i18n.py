"""
Internationalization (i18n) Utility
Supports multiple languages for user-facing messages
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Translation dictionaries
TRANSLATIONS = {
    'id': {
        # Error messages
        'error.rate_limit': 'Terlalu banyak permintaan. Silakan tunggu {seconds} detik.',
        'error.server_unavailable': 'Server tidak tersedia. Silakan coba lagi nanti.',
        'error.sql_unsafe': 'Operasi SQL tidak aman terdeteksi (hanya SELECT diperbolehkan)',
        'error.table_not_found': 'Tabel tidak ditemukan: {tables}',
        'error.unknown_table_suggestion': 'Saran: {suggestions}',
        'error.message_too_long': 'Pesan terlalu panjang ({length} karakter). Maksimal {max_length} karakter.',
        'error.empty_message': 'Pesan tidak boleh kosong.',
        'error.query_timeout': 'Query timeout setelah {seconds} detik. Query terlalu kompleks.',
        'error.database_connection': 'Tidak dapat terhubung ke database: {error}',
        'error.sql_execution': 'Gagal menjalankan query: {error}',
        'error.llm_connection': 'Server AI tidak tersedia. Pastikan Ollama sudah berjalan.',
        'error.llm_timeout': 'Request AI timeout setelah {seconds} detik.',
        'error.model_not_found': 'Model "{model}" tidak ditemukan. Model tersedia: {available}',
        
        # Success messages
        'success.query_executed': 'Query berhasil dijalankan',
        'success.cache_hit': 'Hasil dari cache (lebih cepat)',
        'success.export_complete': 'Export selesai',
        
        # Info messages
        'info.clarification_needed': 'Pertanyaan Anda bisa diartikan beberapa cara. Silakan pilih maksud Anda:',
        'info.generating_query': 'Membuat SQL query...',
        'info.executing_query': 'Menjalankan query...',
        'info.analyzing_results': 'Menganalisis hasil...',
        
        # Validation messages
        'validation.sql_corrected': 'SQL diperbaiki otomatis: {original} → {corrected}',
        'validation.unsafe_operation': 'Operasi tidak aman diblokir: {operation}',
        
        # Export messages
        'export.stats.title': 'Statistik Export',
        'export.stats.total_conversations': 'Total Percakapan: {count}',
        'export.stats.total_queries': 'Total Query Tersimpan: {count}',
        
        # Rate limiting
        'rate_limit.exceeded': 'Batas permintaan tercapai. Tunggu {seconds} detik.',
        'rate_limit.remaining': 'Sisa permintaan: {count}',
        
        # General
        'general.welcome': 'Selamat datang di MyDB Chatbot',
        'general.please_wait': 'Mohon tunggu...',
        'general.processing': 'Memproses...',
    },
    
    'en': {
        # Error messages
        'error.rate_limit': 'Too many requests. Please wait {seconds} seconds.',
        'error.server_unavailable': 'Server unavailable. Please try again later.',
        'error.sql_unsafe': 'Unsafe SQL operation detected (only SELECT allowed)',
        'error.table_not_found': 'Table not found: {tables}',
        'error.unknown_table_suggestion': 'Suggestions: {suggestions}',
        'error.message_too_long': 'Message too long ({length} characters). Maximum {max_length} characters.',
        'error.empty_message': 'Message cannot be empty.',
        'error.query_timeout': 'Query timeout after {seconds} seconds. Query too complex.',
        'error.database_connection': 'Cannot connect to database: {error}',
        'error.sql_execution': 'Failed to execute query: {error}',
        'error.llm_connection': 'AI server unavailable. Make sure Ollama is running.',
        'error.llm_timeout': 'AI request timeout after {seconds} seconds.',
        'error.model_not_found': 'Model "{model}" not found. Available models: {available}',
        
        # Success messages
        'success.query_executed': 'Query executed successfully',
        'success.cache_hit': 'Result from cache (faster)',
        'success.export_complete': 'Export completed',
        
        # Info messages
        'info.clarification_needed': 'Your question can be interpreted in multiple ways. Please choose your intent:',
        'info.generating_query': 'Generating SQL query...',
        'info.executing_query': 'Executing query...',
        'info.analyzing_results': 'Analyzing results...',
        
        # Validation messages
        'validation.sql_corrected': 'SQL auto-corrected: {original} → {corrected}',
        'validation.unsafe_operation': 'Unsafe operation blocked: {operation}',
        
        # Export messages
        'export.stats.title': 'Export Statistics',
        'export.stats.total_conversations': 'Total Conversations: {count}',
        'export.stats.total_queries': 'Total Cached Queries: {count}',
        
        # Rate limiting
        'rate_limit.exceeded': 'Rate limit exceeded. Wait {seconds} seconds.',
        'rate_limit.remaining': 'Remaining requests: {count}',
        
        # General
        'general.welcome': 'Welcome to MyDB Chatbot',
        'general.please_wait': 'Please wait...',
        'general.processing': 'Processing...',
    }
}

class I18n:
    """
    Internationalization handler
    Provides translation functionality with variable substitution
    """
    
    def __init__(self, default_language: str = 'id'):
        """
        Initialize i18n handler
        
        Args:
            default_language: Default language code (id, en)
        """
        self.default_language = default_language
        self.current_language = default_language
        logger.info(f"I18n initialized with default language: {default_language}")
    
    def set_language(self, language: str):
        """
        Set current language
        
        Args:
            language: Language code (id, en)
        """
        if language in TRANSLATIONS:
            self.current_language = language
            logger.info(f"Language changed to: {language}")
        else:
            logger.warning(f"Language '{language}' not supported, using default: {self.default_language}")
    
    def get(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Get translated message
        
        Args:
            key: Translation key (e.g., 'error.rate_limit')
            language: Override current language (optional)
            **kwargs: Variables for substitution
        
        Returns:
            str: Translated message with variables substituted
        """
        lang = language or self.current_language
        
        # Get translation dictionary for language
        translations = TRANSLATIONS.get(lang, TRANSLATIONS[self.default_language])
        
        # Get message
        message = translations.get(key, f"[MISSING: {key}]")
        
        # Substitute variables
        if kwargs:
            try:
                message = message.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing variable in translation {key}: {e}")
        
        return message
    
    def get_available_languages(self) -> list:
        """Get list of available language codes"""
        return list(TRANSLATIONS.keys())
    
    def translate_dict(self, data: dict, language: Optional[str] = None) -> dict:
        """
        Translate all i18n keys in a dictionary
        
        Args:
            data: Dictionary potentially containing i18n keys
            language: Language to use (optional)
        
        Returns:
            dict: Dictionary with translated values
        """
        result = {}
        for key, value in data.items():
            if isinstance(value, str) and value.startswith('i18n:'):
                # Extract i18n key
                i18n_key = value.replace('i18n:', '')
                result[key] = self.get(i18n_key, language)
            elif isinstance(value, dict):
                result[key] = self.translate_dict(value, language)
            else:
                result[key] = value
        return result


# ============================================================================
# GLOBAL I18N INSTANCE (Singleton pattern)
# ============================================================================

_i18n_instance: Optional[I18n] = None

def get_i18n(language: Optional[str] = None) -> I18n:
    """
    Get or create global i18n instance
    
    Args:
        language: Initial language (only used on first call)
    
    Returns:
        I18n instance
    """
    global _i18n_instance
    
    if _i18n_instance is None:
        _i18n_instance = I18n(default_language=language or 'id')
    
    return _i18n_instance


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def t(key: str, language: Optional[str] = None, **kwargs) -> str:
    """
    Shorthand for get_i18n().get()
    
    Usage:
        from utils.i18n import t
        message = t('error.rate_limit', seconds=30)
    
    Args:
        key: Translation key
        language: Override language (optional)
        **kwargs: Variables for substitution
    
    Returns:
        str: Translated message
    """
    return get_i18n().get(key, language, **kwargs)
