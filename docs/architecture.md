# Architecture — MySQL Chatbot (Week 1 Refactored State)

_Last updated: 2026-05-29 (after Day 7)_

---

## Overview

MySQL Chatbot is a text-to-SQL assistant that accepts natural-language questions,
generates a SQL query via an LLM, executes it against a MySQL/Oracle database,
and returns structured results with optional visualizations.

The system is composed of two runtime processes:

| Process | Entry point | Purpose |
|---|---|---|
| **API server** | `main.py` (FastAPI) | Handles HTTP requests, auth, business logic |
| **Frontend** | `streamlit_app.py` | Browser UI that calls the API server |

---

## Layer Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Frontend (Streamlit)  streamlit_app.py                         │
│  Reads: Config.BACKEND_URL, Config.LLM_TIMEOUT                  │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP (REST)
┌──────────────────────────────▼──────────────────────────────────┐
│  API Layer  main.py + api/auth.py + api/analytics.py            │
│  • FastAPI routes + CORS middleware                              │
│  • Auth endpoints (JWT)                                          │
│  • Rate limiting via RateLimiter                                 │
│  • Results caching via ResultsCache                              │
└───────────┬──────────────────────────┬──────────────────────────┘
            │                          │
┌───────────▼──────────┐  ┌────────────▼──────────────────────────┐
│  Services Layer      │  │  Services Layer (continued)           │
│  services/           │  │                                        │
│  • AppServices       │  │  chatbot/chatbot_handler.py            │
│    (DI container)    │  │  • Orchestrates LLM + DB pipeline      │
│  • ChatService       │  │  • Owns db_connection, schema_manager  │
└───────────┬──────────┘  │    query_executor, llm_client          │
            │             └────────────┬──────────────────────────┘
┌───────────▼──────────┐               │
│  Repository Layer    │               │
│  repositories/       │               │
│  • QueryRepository   │               │
│    wraps QueryExecutor               │
└───────────┬──────────┘               │
            │                          │
┌───────────▼──────────────────────────▼──────────────────────────┐
│  Data / Infrastructure Layer                                     │
│  database/                  llm/                 cache/          │
│  • DatabaseConnection       • LLMFactory         • CacheManager  │
│  • SchemaManager            • BaseLLMClient      • SQLiteCache   │
│  • QueryExecutor            • OllamaClient       • RedisCache    │
│  • UserManager              • OpenAIClient                       │
│                             • GeminiClient                       │
└──────────────────────────────────────────────────────────────────┘
            ▲                          ▲
            │                          │
┌───────────┴──────────────────────────┴──────────────────────────┐
│  Core / Config Layer                                             │
│  core/config.py — single source of truth for all constants      │
│  All values readable from environment variables (.env)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Import Dependency Graph

One-directional, no circular imports:

```
api (main.py)
  └─► services/app_services.py
        ├─► repositories/query_repository.py
        │     └─► database/query_executor.py
        │               └─► database/db_connection.py
        ├─► chatbot/chatbot_handler.py
        │     ├─► llm/llm_factory.py → llm/ollama_client.py (etc.)
        │     ├─► database/schema_manager.py
        │     └─► database/query_executor.py
        └─► utils/* (rate_limiter, metrics, results_cache)
              └─► core/config.py
```

---

## Layers

### 1. Core (`core/`)

| File | Role |
|---|---|
| `core/config.py` | Single class `Config` with all constants; reads from `.env` via `os.getenv()` with sane defaults |

`Config` covers: database, LLM provider, cache TTL, rate limiting, query limits, timeouts, and frontend URL.
No other layer hard-codes operational values.

### 2. Data / Infrastructure (`database/`, `llm/`, `cache/`)

**`database/`**

| File | Role |
|---|---|
| `db_connection.py` | Manages MySQL/Oracle connections, engine abstraction |
| `schema_manager.py` | Extracts + caches DB schema (TTL from `Config.SCHEMA_CACHE_TTL`) |
| `query_executor.py` | Validates, executes, caches SQL queries; enforces row limits |
| `user_manager.py` | User CRUD + JWT-related DB operations |

**`llm/`**

| File | Role |
|---|---|
| `base_client.py` | Abstract `BaseLLMClient` interface |
| `llm_factory.py` | Creates concrete client from `Config.AI_PROVIDER` |
| `ollama_client.py` | Ollama (local) implementation; `timeout` defaults to `Config.LLM_TIMEOUT` |
| `openai_client.py` | OpenAI-compatible implementation |
| `gemini_client.py` | Google Gemini implementation |
| `query_generator.py` | Turns natural language + schema into SQL |
| `prompt_templates.py` | Prompt string builders |
| `query_clarifier.py` | Asks follow-up questions for ambiguous inputs |

**`cache/`**

| File | Role |
|---|---|
| `cache_interface.py` | `CacheInterface` ABC |
| `sqlite_cache.py` | Default local cache (file-based SQLite) |
| `redis_cache.py` | Production cache (Redis) |
| `cache_manager.py` | Routes to correct backend based on `Config.CACHE_BACKEND` |

### 3. Repository (`repositories/`)

| File | Role |
|---|---|
| `query_repository.py` | `QueryRepository` — the only gateway from service layer to `QueryExecutor` |

Exposes exactly 3 methods: `validate()`, `execute()`, `get_cache_key()`.
Hides all database internals from the service layer.

### 4. Services (`services/`, `chatbot/`)

| File | Role |
|---|---|
| `services/app_services.py` | `AppServices` dataclass (DI container) + `build_app_services()` factory |
| `services/chat_service.py` | Thin orchestration between API layer and `ChatbotHandler` |
| `chatbot/chatbot_handler.py` | Main orchestrator: NL → SQL → execute → visualize pipeline |
| `chatbot/conversation_manager.py` | Conversation history per session |

### 5. API (`main.py`, `api/`, `streamlit_app.py`)

| File | Role |
|---|---|
| `main.py` | FastAPI app; HTTP routes for chat, execute, export, metrics |
| `api/auth.py` | Login, register, JWT token endpoints |
| `api/analytics.py` | Analytics and reporting endpoints |
| `streamlit_app.py` | Streamlit browser UI; calls `Config.BACKEND_URL` |

---

## Configuration Reference

All values come from `core/config.py` which reads environment variables.
Set any of these in `.env` to override the default.

| Config field | Env var | Default | Used by |
|---|---|---|---|
| `DB_ENGINE` | `DB_ENGINE` | `mysql` | DatabaseConnection |
| `DB_HOST/PORT/USER/PASSWORD/NAME` | matching vars | see `.env.example` | DatabaseConnection |
| `AI_PROVIDER` | `AI_PROVIDER` | `ollama` | LLMFactory |
| `OLLAMA_MODEL` | `OLLAMA_MODEL` | `llama3.1` | OllamaClient |
| `LLM_TIMEOUT` | `LLM_TIMEOUT` | `600` | OllamaClient, Streamlit |
| `MAX_REQUESTS_PER_MINUTE` | `MAX_REQUESTS_PER_MINUTE` | `10` | RateLimiter |
| `RATE_LIMIT_TIME_WINDOW` | `RATE_LIMIT_TIME_WINDOW` | `60` | RateLimiter |
| `RESULTS_CACHE_TTL` | `RESULTS_CACHE_TTL` | `3600` | ResultsCache |
| `SCHEMA_CACHE_TTL` | `SCHEMA_CACHE_TTL` | `3600` | SchemaManager |
| `METRICS_WINDOW_MINUTES` | `METRICS_WINDOW_MINUTES` | `60` | MetricsCollector |
| `MAX_QUERY_ROWS` | `MAX_QUERY_ROWS` | `100` | QueryExecutor |
| `QUERY_TIMEOUT_SECONDS` | `QUERY_TIMEOUT_SECONDS` | `30` | Streamlit auth API |
| `CACHE_BACKEND` | `CACHE_BACKEND` | `sqlite` | CacheManager |
| `BACKEND_URL` | `BACKEND_URL` | `http://localhost:8000` | streamlit_app.py |

---

## Week 1 Refactoring Summary (Days 1–7)

| Day | Change | Files affected |
|---|---|---|
| 1–2 | Defined target folder structure; service skeleton | `services/`, `api/` |
| 3 | Moved chat flow to `ChatService` | `services/chat_service.py` |
| 4 | Repository pattern: `QueryRepository` | `repositories/query_repository.py`, `services/app_services.py` |
| 5 | Centralized constants in `Config`; removed magic numbers | `core/config.py`, `main.py`, `app_services.py`, `ollama_client.py`, `streamlit_app.py` |
| 6 | Type hints on 7 critical modules; `ruff`+`black` activated | `core/`, `llm/base_client.py`, `database/` (3 files), `chatbot/chatbot_handler.py` |
| 7 | Architecture documentation; `.env.example` updated | `docs/architecture.md`, `.env.example` |

---

## Running Locally

```bash
# 1. Copy and fill env
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start API server
uvicorn main:app --reload --port 8000

# 4. Start Streamlit (separate terminal)
streamlit run streamlit_app.py
```

See [QUICKSTART.md](QUICKSTART.md) for full setup including database and Ollama.
