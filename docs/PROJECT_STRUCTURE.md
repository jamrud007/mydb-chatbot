# Project Structure

```
mysql-chatbot/
|
|-- main.py                      # FastAPI application (backend entry point)
|-- streamlit_app.py             # Streamlit dashboard (frontend entry point)
|-- config.py                    # Configuration management
|-- requirements.txt             # Python dependencies
|
|-- api/                         # API route modules
|   |-- auth.py                  # Authentication endpoints
|   |-- analytics.py             # Analytics endpoints
|   `-- __init__.py
|
|-- chatbot/                     # Core chatbot orchestration
|   |-- chatbot_handler.py       # Main flow: NL -> SQL -> execute -> summarize/viz
|   |-- conversation_manager.py  # Session context and history
|   `-- __init__.py
|
|-- database/                    # Database layer
|   |-- db_connection.py         # DB connection and pooling
|   |-- query_executor.py        # Query execution and result formatting
|   |-- schema_manager.py        # Schema introspection and caching
|   |-- user_manager.py          # User/auth data operations
|   `-- __init__.py
|
|-- llm/                         # LLM integrations (Gemini/OpenAI/Ollama/custom)
|   |-- base_client.py
|   |-- llm_factory.py
|   |-- query_generator.py
|   |-- query_clarifier.py
|   |-- prompt_templates.py
|   `-- ...clients
|
|-- utils/                       # Shared utilities
|   |-- sql_validator.py         # SQL safety validation
|   |-- results_cache.py         # Query/result cache
|   |-- metrics.py               # Performance metrics
|   |-- structured_logger.py     # Structured logs
|   |-- visualization_helper.py  # Chart recommendation logic
|   `-- ...
|
|-- models/                      # API request/response models
|   `-- api_models.py
|
|-- tests/                       # Test suite
|-- docs/                        # Documentation
|-- scripts/                     # Operational scripts
|-- docker/                      # Container-related files
|-- sample_db/                   # Sample SQL schema/data
|-- data/                        # Generated reports/metrics
`-- backups/                     # Legacy snapshots
```

## Module Descriptions

### Core Application
- **main.py** - FastAPI server with API routes, middleware, auth integration, and health/metrics/export endpoints.
- **streamlit_app.py** - Streamlit UI that consumes backend APIs for chat, auth, and visualization.
- **config.py** - Centralized settings from environment variables.

### Dependencies (Backend)
- `fastapi` - Web framework/API layer
- `uvicorn` - ASGI server
- `mysql-connector-python` - MySQL driver
- `google-generativeai` / `openai` - Cloud LLM providers
- `requests` - HTTP client (e.g., Ollama)
- `python-dotenv` - Environment management

## Architecture Flow

```
User (Streamlit UI)
    -> FastAPI (main.py)
    -> ChatbotHandler
        -> LLM (generate/clarify SQL)
        -> QueryExecutor (run SQL on MySQL)
        -> VisualizationHelper (chart config)
    -> JSON response back to Streamlit
```
