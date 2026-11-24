# Worklog Day 8 — 2 Juni 2026

## Tujuan
Identifikasi proses berat sinkron (LLM analysis, reports, export) dan tentukan kandidat async worker.

---

## Identifikasi Masalah / Topik Pekerjaan

**Topik:** Semua endpoint di `main.py` berjalan secara sinkron — LLM call, DB query, export, report semuanya memblokir HTTP response sampai selesai. Dengan LLM lokal (Ollama), satu `/api/chat` bisa memakan 10–60 detik.

**Pertanyaan yang dijawab hari ini:**
- Proses apa saja yang berat dan ada di request path?
- Mana yang *harus* sinkron (user perlu hasilnya langsung) vs mana yang bisa di-defer?
- Perubahan minimal apa yang bisa kita lakukan di Day 9 untuk efek terbesar?

---

## Yang Dikerjakan

### 1. Audit request flow

Baca: `main.py`, `chatbot/chatbot_handler.py`, `services/chat_service.py`, `llm/query_generator.py`, `utils/daily_reporter.py`, `utils/history_exporter.py`.

**Flow `/api/chat` (sinkron saat ini):**
```
POST /api/chat
  → query_clarifier.analyze_query()    [LLM #1 — 5-30s]
  → query_generator.generate_queries() [LLM #2 — 10-60s]
  → return
```

**Flow `/api/execute/{index}` (sinkron saat ini):**
```
POST /api/execute/{i}
  → sql_validator.validate_and_fix()   [~50ms — OK]
  → query_executor.execute()           [DB — 100ms-5s — OK]
  → llm_client.get_response(analysis)  [LLM #3 — 10-60s] ← tidak perlu blokir
  → return
```

### 2. Inventarisasi 7 proses berat

| # | Proses | Endpoint | Durasi | Blokir user? |
|---|---|---|---|---|
| 1 | Query clarification (LLM) | `/api/chat` | 5-30s | Ya |
| 2 | NL→SQL generation (LLM) | `/api/chat` | 10-60s | Ya |
| 3 | Auto-analysis insight (LLM) | `/api/execute/{i}` | 10-60s | Ya (tidak perlu) |
| 4 | DB query execution | `/api/execute/{i}` | 100ms-5s | Ya (acceptable) |
| 5 | Daily report | `/api/admin/daily-report` | 1-5s | Ya (admin only) |
| 6 | History export | `/api/export/*` | <2s | Ya (kecil) |
| 7 | Schema extraction (cold start) | First request | 500ms-3s | Ya (one-time) |

### 3. Klasifikasi dan rekomendasi

**Priority 1 — Quick win (Day 9):**
- **Auto-analysis (#3):** User sudah punya data query — analysis bisa di-fire sebagai `BackgroundTask`, response langsung dikirim dengan `analysis_pending=True`. Client poll `/api/execute/{i}/analysis` terpisah.
- **Daily report (#5):** Admin tidak perlu tunggu file selesai ditulis — return `202 Accepted`, fire sebagai `BackgroundTask`.

**Priority 2 — Requires streaming (Day 10):**
- **Chat LLM calls (#1, #2):** Tidak bisa di-defer sepenuhnya karena user perlu SQL-nya. Solusi: tambah endpoint `POST /api/chat/stream` dengan `StreamingResponse` — user lihat token realtime, tidak perlu tunggu full completion.

**Priority 3 — OK untuk sekarang:**
- DB query (#4), export (#6), schema (#7) — durasi acceptable, tidak perlu async dulu.

### 4. Buat `docs/ASYNC_WORKER_CANDIDATES.md`

Dokumen referensi untuk Day 9–10 berisi:
- Diagram flow sinkron saat ini
- Inventarisasi 7 proses dengan durasi estimate
- Klasifikasi Priority 1/2/3
- Tiga opsi arsitektur async (BackgroundTasks, asyncio, Redis/Celery)
- Daftar file yang harus diubah di Day 9 dan Day 10

---

## Hasil

- Semua proses berat teridentifikasi dan terdokumentasi.
- Kandidat async yang paling impactful: **auto-analysis insight** (Priority 1) — perubahan kecil, efek besar (response `/api/execute/` bisa dari 70s → <5s).
- Day 9 punya scope yang jelas: `BackgroundTasks` untuk analysis + daily report.
- Day 10 punya scope yang jelas: `StreamingResponse` + timeout/retry untuk chat LLM.

---

## Tidak Dilakukan (Scope Batas)

- Belum implementasi perubahan apapun — Day 8 adalah analisis saja.
- Belum profiling aktual (durasi di atas adalah estimasi berdasarkan code review + Ollama karakteristik).

---

## Next

- **Day 9:** Implement queue interface minimal — `BackgroundTasks` untuk auto-analysis dan daily report. Pisahkan analysis dari request path.

---

## Penjelasan (Kenapa Day 8 Penting)

**Masalah:**
`/api/execute/` saat ini blokir user selama 70+ detik pada query baru dengan `ENABLE_DATA_ANALYSIS=True`:
- DB query: ~2s
- Auto-analysis LLM: ~60s
- Total: user tunggu 62 detik setelah data sudah ada di server

**Solusinya simpel** karena analysis bersifat opsional/additive:
```
Sebelum (sinkron):
  DB query → tunggu → LLM analysis → tunggu → BARU return ke user

Sesudah (async):
  DB query → return ke user segera
  LLM analysis → jalan di background
  User poll /analysis → dapat hasilnya saat selesai
```

Perubahan ini tidak butuh infra baru — FastAPI sudah punya `BackgroundTasks` built-in.
