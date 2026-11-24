"""
Custom Exceptions for MyDB Chatbot
Provides user-friendly error handling with actionable messages
"""

class ChatbotException(Exception):
    """Base exception for all chatbot errors"""
    def __init__(self, message, error_code=None, details=None):
        super().__init__(message)
        self.error_code = error_code or 'CHATBOT_ERROR'
        self.details = details or {}


# ============================================================================
# LLM EXCEPTIONS
# ============================================================================

class LLMException(ChatbotException):
    """Base exception for LLM-related errors"""
    pass


class OllamaConnectionError(LLMException):
    """Ollama server connection failed"""
    def __init__(self, base_url):
        super().__init__(
            f"Cannot connect to Ollama server at {base_url}",
            error_code="OLLAMA_CONNECTION_ERROR",
            details={'base_url': base_url}
        )


class OllamaTimeoutError(LLMException):
    """Ollama request timeout"""
    def __init__(self, timeout):
        super().__init__(
            f"Ollama request timeout after {timeout} seconds",
            error_code="OLLAMA_TIMEOUT",
            details={'timeout': timeout}
        )


class ModelNotFoundError(LLMException):
    """Requested model not found"""
    def __init__(self, model_name, available_models=None):
        super().__init__(
            f"Model '{model_name}' not found",
            error_code="MODEL_NOT_FOUND",
            details={
                'requested_model': model_name,
                'available_models': available_models or []
            }
        )


class JSONParseError(LLMException):
    """Failed to parse LLM JSON response"""
    def __init__(self, raw_response, parse_error):
        super().__init__(
            "Failed to parse LLM response as JSON",
            error_code="JSON_PARSE_ERROR",
            details={
                'raw_response': raw_response[:500] if raw_response else '',
                'parse_error': str(parse_error)
            }
        )


# ============================================================================
# DATABASE EXCEPTIONS
# ============================================================================

class DatabaseException(ChatbotException):
    """Base exception for database errors"""
    pass


class DatabaseConnectionError(DatabaseException):
    """Database connection failed"""
    def __init__(self, host, database, original_error):
        super().__init__(
            f"Cannot connect to database '{database}' at '{host}': {original_error}",
            error_code="DB_CONNECTION_ERROR",
            details={
                'host': host,
                'database': database,
                'error': str(original_error)
            }
        )


class SQLExecutionError(DatabaseException):
    """SQL query execution failed"""
    def __init__(self, sql, original_error):
        super().__init__(
            f"SQL execution failed: {original_error}",
            error_code="SQL_EXECUTION_ERROR",
            details={
                'sql': sql[:500] if sql else '',
                'error': str(original_error)
            }
        )


class SQLValidationError(DatabaseException):
    """SQL validation failed"""
    def __init__(self, sql, validation_error):
        super().__init__(
            f"SQL validation failed: {validation_error}",
            error_code="SQL_VALIDATION_ERROR",
            details={
                'sql': sql,
                'validation_error': validation_error
            }
        )


class SchemaException(DatabaseException):
    """Schema-related errors"""
    pass


class SchemaExtractionError(SchemaException):
    """Failed to extract database schema"""
    def __init__(self, original_error):
        super().__init__(
            f"Failed to extract schema: {original_error}",
            error_code="SCHEMA_EXTRACTION_ERROR",
            details={'error': str(original_error)}
        )


# ============================================================================
# ERROR FORMATTER - User-Friendly Messages
# ============================================================================

def format_error_response(error: Exception) -> dict:
    """
    Format exception into user-friendly response
    
    Args:
        error: Exception instance
    
    Returns:
        dict: Formatted error response
    """
    if isinstance(error, OllamaConnectionError):
        return {
            'success': False,
            'error_code': error.error_code,
            'message': '🔴 **Server AI Tidak Tersedia**\n\nServer Ollama tidak berjalan. Pastikan Ollama sudah dijalankan dengan: `ollama serve`',
            'technical_details': str(error),
            'user_action': 'Jalankan Ollama server atau hubungi administrator'
        }
    
    elif isinstance(error, OllamaTimeoutError):
        return {
            'success': False,
            'error_code': error.error_code,
            'message': '⏱️ **Request Timeout**\n\nQuery terlalu kompleks atau server sedang sibuk. Coba pertanyaan yang lebih sederhana.',
            'technical_details': str(error),
            'user_action': 'Sederhanakan pertanyaan atau coba lagi nanti'
        }
    
    elif isinstance(error, ModelNotFoundError):
        available = ', '.join(error.details['available_models'][:5])
        return {
            'success': False,
            'error_code': error.error_code,
            'message': f'🤖 **Model Tidak Ditemukan**\n\nModel `{error.details["requested_model"]}` tidak tersedia.\n\n**Model tersedia:** {available}',
            'technical_details': str(error),
            'user_action': f'Pull model dengan: ollama pull {error.details["requested_model"]}'
        }
    
    elif isinstance(error, DatabaseConnectionError):
        return {
            'success': False,
            'error_code': error.error_code,
            'message': '🔴 **Koneksi Database Gagal**\n\nTidak dapat terhubung ke database. Periksa konfigurasi database Anda.',
            'technical_details': str(error),
            'user_action': 'Hubungi administrator database'
        }
    
    elif isinstance(error, SQLExecutionError):
        return {
            'success': False,
            'error_code': error.error_code,
            'message': '⚠️ **Error Menjalankan Query**\n\nQuery SQL tidak dapat dijalankan. Mungkin ada kesalahan di struktur query.',
            'technical_details': str(error),
            'sql': error.details.get('sql', '')[:200],
            'user_action': 'Coba pertanyaan dengan cara berbeda'
        }
    
    elif isinstance(error, SQLValidationError):
        return {
            'success': False,
            'error_code': error.error_code,
            'message': f'⚠️ **Query Tidak Valid**\n\n{error.details.get("validation_error", "Unknown error")}',
            'technical_details': str(error),
            'user_action': 'Periksa nama tabel dan kolom dalam pertanyaan Anda'
        }
    
    elif isinstance(error, SchemaExtractionError):
        return {
            'success': False,
            'error_code': error.error_code,
            'message': '⚠️ **Gagal Membaca Schema Database**\n\nTidak dapat membaca struktur database.',
            'technical_details': str(error),
            'user_action': 'Hubungi administrator'
        }
    
    elif isinstance(error, ChatbotException):
        # Generic chatbot exception
        return {
            'success': False,
            'error_code': error.error_code,
            'message': f'⚠️ **Error:** {str(error)}',
            'technical_details': str(error),
            'details': error.details
        }
    
    else:
        # Unknown error
        return {
            'success': False,
            'error_code': 'UNEXPECTED_ERROR',
            'message': '⚠️ **Terjadi Kesalahan**\n\nMaaf, terjadi kesalahan yang tidak terduga. Silakan coba lagi.',
            'technical_details': str(error),
            'user_action': 'Coba lagi atau hubungi administrator'
        }
