# Project Structure

```
mysql-chatbot/
├── api/                      # API route handlers
│   ├── auth.py              # Authentication endpoints
│   └── routes.py            # Main API routes
│
├── backups/                 # Backup files (legacy code)
│
├── cache/                   # Cache implementations
│   ├── cache_manager.py     # Cache manager
│   ├── redis_cache.py       # Redis cache backend
│   └── sqlite_cache.py      # SQLite cache backend
│
├── chatbot/                 # Core chatbot logic
│   ├── chatbot_handler.py   # Main chatbot orchestrator
│   ├── conversation_manager.py  # Conversation history
│   └── query_clarifier.py   # Query disambiguation
│
├── database/                # Database layer
│   ├── db_connection.py     # Connection pooling + timeout
│   ├── query_executor.py    # Query execution + validation
│   └── schema_manager.py    # Schema introspection
│
├── docs/                    # Documentation
│   ├── samples/             # Auto-generated samples
│   │   ├── schema_docs_sample.html
│   │   ├── schema_docs_sample.md
│   │   └── schema_docs_sample.json
│   └── README.md
│
├── exceptions/              # Custom exceptions
│   └── chatbot_exceptions.py
│
├── llm/                     # LLM integrations
│   ├── base_client.py       # Base LLM client
│   ├── gemini_client.py     # Google Gemini
│   ├── ollama_client.py     # Ollama (local)
│   ├── openai_client.py     # OpenAI
│   ├── prompt_templates.py  # Prompt templates
│   └── query_generator.py   # SQL generation
│
├── tests/                   # Test suite
│   ├── test_history_export.py
│   ├── test_i18n.py
│   ├── test_input_sanitization.py
│   ├── test_metrics.py
│   ├── test_query_suggestions.py
│   ├── test_query_timeout.py
│   ├── test_schema_docs.py
│   ├── test_structured_logging.py
│   └── README.md
│
├── utils/                   # Utility modules
│   ├── csv_exporter.py      # CSV export utility
│   ├── history_exporter.py  # Conversation export (NEW)
│   ├── i18n.py              # Internationalization (NEW)
│   ├── logger.py            # Basic logger
│   ├── metrics.py           # Metrics collection (NEW)
│   ├── query_suggestions.py # Autocomplete (NEW)
│   ├── rate_limiter.py      # Rate limiting
│   ├── results_cache.py     # Results caching
│   ├── schema_docs.py       # Doc generator (NEW)
│   ├── sql_validator.py     # SQL validation + safety
│   └── structured_logger.py # Structured logging (NEW)
│
├── config.py                # Configuration
├── main.py                  # FastAPI application
├── streamlit_app.py         # Streamlit frontend
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
└── README.md               # Main documentation
```

## Key Directories

### `/chatbot/`
Core chatbot logic including conversation management and query processing.

### `/database/`
Database connection, query execution, and schema management with connection pooling and timeouts.

### `/llm/`
LLM integrations supporting multiple providers (Ollama, OpenAI, Gemini).

### `/utils/`
Utility modules including **new features**:
- `i18n.py` - Multi-language support (ID/EN)
- `metrics.py` - Performance monitoring
- `history_exporter.py` - Export conversations
- `query_suggestions.py` - Smart autocomplete
- `schema_docs.py` - Auto-generate documentation
- `structured_logger.py` - JSON logging

### `/tests/`
Comprehensive test suite with 100% coverage of new features.

### `/docs/`
Auto-generated documentation and samples.

## Configuration

- `config.py` - Application settings
- `.env` - Environment variables (DB, LLM API keys)
- `requirements.txt` - Python dependencies

## Entry Points

- `main.py` - FastAPI backend server
- `streamlit_app.py` - Streamlit frontend
- `docker-compose.yml` - Full stack deployment
