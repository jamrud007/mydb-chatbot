# Migration Mapping - Legacy to Target Structure

Tanggal: 12 April 2026
Tujuan: migrasi bertahap ke struktur `api`, `services`, `repositories`, `core`, `tests` tanpa breaking change.

## Target Structure
- `api/` -> routing, request/response layer
- `services/` -> business logic orchestration
- `repositories/` -> data access (DB/cache/provider wrappers)
- `core/` -> config, constants, shared infra concerns
- `tests/` -> unit/integration/e2e

## Mapping Plan (Phase-by-Phase)

### Phase 1 (Safe, Non-Breaking)
- `config.py` -> `core/config.py`
- `utils/logger.py` -> `core/logging.py`
- `utils/structured_logger.py` -> `core/structured_logging.py`

Catatan:
- Di fase ini boleh pakai adapter/import alias agar import lama tetap jalan.

### Phase 2 (Service Extraction)
- `chatbot/chatbot_handler.py` -> `services/chat_service.py`
- `chatbot/conversation_manager.py` -> `services/conversation_service.py`
- `llm/query_generator.py` -> `services/query_generation_service.py`
- `llm/query_clarifier.py` -> `services/query_clarification_service.py`

Catatan:
- `main.py` nantinya hanya koordinasi dependency + endpoint.

### Phase 3 (Repository Layer)
- `database/db_connection.py` -> `repositories/db/connection_repository.py`
- `database/query_executor.py` -> `repositories/db/query_repository.py`
- `database/schema_manager.py` -> `repositories/db/schema_repository.py`
- `database/user_manager.py` -> `repositories/db/user_repository.py`
- `utils/results_cache.py` -> `repositories/cache/results_cache_repository.py`

### Phase 4 (API Alignment)
- `api/auth.py` -> tetap di `api/auth.py` (refactor internal call ke `services`)
- `api/analytics.py` -> tetap di `api/analytics.py` (refactor internal call ke `services`)
- Endpoint logic di `main.py` -> pindah ke module router per domain bila perlu

### Phase 5 (LLM Provider Organization)
- `llm/base_client.py` -> `repositories/llm/base_client.py`
- `llm/*_client.py` -> `repositories/llm/providers/*`
- `llm/llm_factory.py` -> `repositories/llm/factory.py`
- `llm/prompt_templates.py` -> `core/prompts.py` atau `services/prompts.py` (pilih satu dan konsisten)

## Rules During Migration
- Jangan pindah semua file sekaligus.
- Satu PR/commit = satu area kecil + test hijau.
- Pertahankan backward-compatible imports sementara.
- Update docs setiap phase selesai.

## Definition of Done Day 1
- [x] Folder target dibuat: `services/`, `repositories/`, `core/`
- [x] Dokumen mapping legacy -> target dibuat
- [ ] Tentukan urutan eksekusi Phase 1 (next action Day 2)
