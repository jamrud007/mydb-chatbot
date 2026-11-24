"""
Configuration loader for MyDB Chatbot.
"""
import os
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # SMTP Configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_DISPLAY_NAME = os.getenv("SMTP_DISPLAY_NAME", "")

    # Database Configuration
    DB_ENGINE = os.getenv("DB_ENGINE", "mysql").lower()  # mysql | oracle
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "ecommerce_olist")
    DB_SERVICE_NAME = os.getenv("DB_SERVICE_NAME", "ORCLPDB1")
    DB_SCHEMA = os.getenv("DB_SCHEMA", "")
    DB_DSN = os.getenv("DB_DSN", "")

    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")

    # AI Provider Configuration
    AI_PROVIDER = os.getenv("AI_PROVIDER", "ollama")
    AI_FALLBACK_PROVIDERS = (
        os.getenv("AI_FALLBACK_PROVIDERS", "").split(",")
        if os.getenv("AI_FALLBACK_PROVIDERS")
        else []
    )

    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", None)

    # DeepSeek Configuration (OpenAI-compatible)
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # Claude Configuration (future)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-3-haiku-20240307")

    # Application Settings
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    # Cache Settings
    SCHEMA_CACHE_TTL = int(os.getenv("SCHEMA_CACHE_TTL", 3600))

    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE = int(os.getenv("MAX_REQUESTS_PER_MINUTE", 10))
    RATE_LIMIT_TIME_WINDOW = int(os.getenv("RATE_LIMIT_TIME_WINDOW", 60))

    # Query Settings
    MAX_QUERY_ROWS = int(os.getenv("MAX_QUERY_ROWS", 100))
    READ_ONLY_MODE = os.getenv("READ_ONLY_MODE", "False").lower() == "true"
    ENABLE_DATA_ANALYSIS = os.getenv("ENABLE_DATA_ANALYSIS", "True").lower() == "true"
    QUERY_TIMEOUT_SECONDS = int(os.getenv("QUERY_TIMEOUT_SECONDS", 30))

    # LLM Settings
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 600))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.0))
    METRICS_WINDOW_MINUTES = int(os.getenv("METRICS_WINDOW_MINUTES", 60))

    # Query Cache Settings
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
    CACHE_BACKEND = os.getenv("CACHE_BACKEND", "sqlite")

    # SQLite Cache Settings
    CACHE_SQLITE_PATH = os.getenv("CACHE_SQLITE_PATH", "./data/cache.db")
    CACHE_SQLITE_MAX_SIZE_MB = int(os.getenv("CACHE_SQLITE_MAX_SIZE_MB", "500"))

    # Redis Cache Settings (for production)
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS = int(os.getenv("REDIS_MAX_CONNECTIONS", "10"))

    # Cache Behavior
    CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", "604800"))  # 7 days
    CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "10000"))
    CACHE_AUTO_CLEANUP = os.getenv("CACHE_AUTO_CLEANUP", "True").lower() == "true"
    RESULTS_CACHE_TTL = int(os.getenv("RESULTS_CACHE_TTL", "3600"))

    # Frontend / Streamlit Settings
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []

        if not cls.DB_PASSWORD:
            errors.append("DB_PASSWORD is required")

        if cls.DB_ENGINE not in ("mysql", "oracle"):
            errors.append("DB_ENGINE must be either 'mysql' or 'oracle'")

        if cls.DB_ENGINE == "oracle" and not (cls.DB_DSN or cls.DB_SERVICE_NAME):
            errors.append("For Oracle, set DB_DSN or DB_SERVICE_NAME")

        if cls.AI_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required when using Gemini provider")

        if cls.AI_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required when using OpenAI provider")

        if cls.AI_PROVIDER == "claude" and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when using Claude provider")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True

    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """Get database configuration as dict."""
        if cls.DB_ENGINE == "oracle":
            dsn = cls.DB_DSN.strip() if cls.DB_DSN else f"{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_SERVICE_NAME}"
            schema = cls.DB_SCHEMA.strip() if cls.DB_SCHEMA else cls.DB_USER
            return {
                "engine": "oracle",
                "host": cls.DB_HOST,
                "port": cls.DB_PORT,
                "user": cls.DB_USER,
                "password": cls.DB_PASSWORD,
                "service_name": cls.DB_SERVICE_NAME,
                "dsn": dsn,
                "schema": schema,
            }

        return {
            "engine": "mysql",
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD,
            "database": cls.DB_NAME,
        }

