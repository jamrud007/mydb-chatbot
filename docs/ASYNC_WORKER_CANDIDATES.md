# Async Worker Candidates — Day 8 Analysis

_Prepared: 2026-06-02_

---

## Goal

Identify all heavy synchronous processes in the request path and classify them as
async worker candidates for Week 2 scalability work.

---

## How Requests Flow Today (Synchronous)

```
User browser / Streamlit
    │
    ▼
POST /api/chat                         POST /api/execute/{index}
    │                                      │
    ├─ query_clarifier.analyze_query()     ├─ sql_validator.validate_and_fix()
    │  [LLM call #1 — 5-30s]              │  [fast, ~50ms]
    │                                      │
    ├─ query_generator.generate_queries()  ├─ query_executor.execute()
    │  [LLM call #2 — 10-60s]             │  [DB query — 100ms-5s]
    │                                      │
    └─ return SQL suggestions              ├─ llm_client.get_response(analysis_prompt)
       [user waits entire time]            │  [LLM call #3 — 10-60s]
                                           │  ONLY if ENABLE_DATA_ANALYSIS=True
                                           │  and no cache hit
                                           │
                                           └─ return result + analysis
                                              [user waits for analysis too]
```

---

## Process Inventory

| # | Process | Endpoint | Duration (Ollama local) | Blocks user? |
|---|---|---|---|---|
| 1 | Query clarification (LLM) | `POST /api/chat` | 5–30 s | Yes |
| 2 | NL→SQL generation (LLM) | `POST /api/chat` | 10–60 s | Yes |
| 3 | Auto-analysis insight (LLM) | `POST /api/execute/{i}` | 10–60 s | Yes (but doesn't need to) |
| 4 | DB query execution | `POST /api/execute/{i}` | 100 ms–5 s | Yes (acceptable) |
| 5 | Daily report generation | `POST /api/admin/daily-report` | 1–5 s | Yes (admin only) |
| 6 | History export (JSON/CSV/text) | `GET /api/export/*` | 100 ms–2 s | Yes (usually small) |
| 7 | Schema extraction (first load) | Any first request | 500 ms–3 s | Yes (one-time, cached) |

---

## Candidate Classification

### Priority 1 — Immediate win (low code change, high impact)

**Process #3: Auto-analysis insight**

- The user already has the query results when this starts.
- Analysis is purely additive — the UI can render data first, then stream in the analysis.
- Currently blocks the `/api/execute/` response for 10–60s unnecessarily.
- Fix: Move to FastAPI `BackgroundTasks` or return results immediately with
  `analysis_status: "pending"`, then client polls `/api/execute/{i}/analysis`.

**Process #5: Daily report generation**

- Admin action, no user is waiting for UI feedback.
- Fix: Wrap in FastAPI `BackgroundTasks`. Return `202 Accepted` immediately.

### Priority 2 — Requires frontend coordination (bigger change)

**Processes #1 + #2: Chat LLM calls (clarification + SQL generation)**

- Both are on the critical user path and cannot return a useful partial response.
- Short-term mitigation: add streaming response (`StreamingResponse`) so user
  sees tokens as they arrive rather than waiting for full completion.
- Long-term: move to async job model (POST → job_id → GET /job/{id}) once
  frontend supports it.

### Priority 3 — Low priority (already fast enough)

**Process #4: DB query execution** — 100ms–5s is acceptable for a query tool.

**Process #6: History export** — small payloads, no bottleneck in practice.

**Process #7: Schema extraction** — one-time at startup, TTL-cached after that.

---

## Recommended Async Architecture (to implement Day 9)

```
Option A — FastAPI BackgroundTasks (simplest, no extra infra)
┌─────────────────────────────────────────────────────────┐
│ POST /api/execute/{i}                                    │
│   1. Execute DB query (sync, fast)                       │
│   2. Return results immediately with analysis_pending=True│
│   3. Fire analysis as BackgroundTask (no response wait)  │
│                                                          │
│ GET /api/execute/{i}/analysis                            │
│   Poll: return analysis when ready, or "pending"         │
└─────────────────────────────────────────────────────────┘

Option B — asyncio + async LLM client (if LLM client supports it)
  - Convert route handlers to async def
  - Use await for LLM calls
  - FastAPI runs them on the async event loop
  - No extra infra needed

Option C — Background queue (Redis/Celery) — overkill for now
  - Better for multi-instance horizontal scaling
  - Reserve for Day 14+ when load testing reveals need
```

**Recommendation: Start with Option A (BackgroundTasks) for auto-analysis (Day 9),
then Option B (asyncio) for chat LLM calls (Day 10).**

---

## Files to Change (Day 9 scope)

| File | Change |
|---|---|
| `main.py` | Add `BackgroundTasks` param to `/api/execute/`, fire analysis as background |
| `chatbot/chatbot_handler.py` | Extract `_run_analysis()` as standalone method |
| `main.py` | Add `GET /api/execute/{i}/analysis` polling endpoint |
| `main.py` | Change `/api/admin/daily-report` to return 202 + fire as BackgroundTask |

---

## Files to Change (Day 10 scope — streaming/timeout/retry)

| File | Change |
|---|---|
| `llm/base_client.py` | Add `stream_response()` abstract method |
| `llm/ollama_client.py` | Implement streaming via Ollama `/api/generate` stream=True |
| `main.py` | Add `POST /api/chat/stream` using `StreamingResponse` |
| `llm/ollama_client.py` | Add retry logic with exponential backoff |
| `llm/llm_factory.py` | Add fallback provider switching on timeout |
