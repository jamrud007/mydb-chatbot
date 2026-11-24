# 30-Day Checklist - Restructure Project Architecture (per 12 April 2026)

Parent Epic:
Restructure project architecture to improve maintainability, scalability, and operability.

## A. Maintainability

### Day 1
- [x] Definisikan target struktur folder final (`api`, `services`, `repositories`, `core`, `tests`).
- [x] Buat dokumen mapping file lama -> file baru.

### Day 2
- [x] Audit `main.py` dan tandai blok logic yang harus dipindah.
- [x] Buat service skeleton awal (`services/`).

### Day 3
- [x] Pindahkan 1 flow utama ke service layer (mis. chat flow).
- [x] Pastikan behavior tidak berubah (smoke test).

### Day 4
- [x] Pindahkan akses data jadi repository pattern bertahap.
- [x] Rapikan import agar tidak circular.

### Day 5
- [x] Standarisasi config loading dan fallback env.
- [x] Hapus duplikasi constants/config.

### Day 6
- [x] Tambahkan/rapikan type hints di modul kritikal.
- [x] Aktifkan lint+format lokal (`ruff`/`black`).

### Day 7
- [x] Dokumentasi arsitektur versi baru (`docs/architecture.md`).
- [x] Buffer fix untuk debt minggu 1.

## B. Scalability

### Day 8
- [x] Identifikasi proses berat sinkron (LLM analysis, reports, export).
- [x] Tentukan kandidat async worker.

### Day 9
- [x] Implement queue interface minimal (abstraction dulu, provider belakangan).
- [x] Pisahkan task berat dari request path.

### Day 10
- [x] Tambahkan timeout + retry policy untuk LLM provider. *(llm/openai_client.py — retry dengan exponential backoff)*
- [x] Tambahkan fallback provider logic yang terukur. *(llm/llm_factory.py — create_with_fallback() + AI_FALLBACK_PROVIDERS)*

### Day 11
- [x] Audit caching: result/schema/history. *(cache/sqlite_cache.py + redis_cache.py)*
- [x] Definisikan TTL & invalidation strategy. *(TTL via CACHE_DEFAULT_TTL env, auto cleanup aktif)*

### Day 12
- [x] Terapkan pagination/row limit konsisten di endpoint query. *(main.py — Query(ge,le) caps + offset pada /api/results, /api/cache/entries, /api/suggestions; ResultsListResponse tambah total/offset)*
- [x] Review bottleneck query executor. *(query_executor.py — precompile DANGEROUS_PATTERNS + _add_limit regex sebagai class-level attrs; timeout sudah di-handle di db_connection.execute_query())*

### Day 13
- [x] Tambah guard untuk slow query (warning threshold). *(utils/metrics.py — slow_query_count + threshold 5000ms)*
- [x] Uji beban ringan (local concurrent requests). *(scripts/load_test_local.py — async concurrent GET terhadap /api/health, /api/metrics, /api/cache/stats; lihat docs/WORKLOG_2026-06-06_DAY13.md)*

### Day 14
- [x] Buffer fix skalabilitas minggu 2. *(query_executor.py — wire record_query_duration + record_error; openai_client.py — wire record_llm_call; metrics.py — slow_query_count window-filtered)*
- [x] Catat sebelum/sesudah (latency dasar). *(docs/LATENCY_BASELINE_DAY14.md)*

## C. Operability

### Day 15
- [x] Standarisasi structured logging (json format). *(core/structured_logging.py)*
- [x] Pastikan semua log punya level dan context. *(core/logging.py — JSONFormatter ditambahkan ke setup_logger(); semua 30+ modul yang pakai logging.getLogger() otomatis emit JSON dengan field timestamp/level/logger/message)*

### Day 16
- [x] Tambahkan `request_id` middleware di FastAPI. *(core/middleware.py — RequestIDMiddleware: ambil/generate X-Request-ID, log request_started/request_completed, echo header balik ke client)*
- [x] Propagasi `request_id` ke service/database logs. *(core/request_context.py — contextvar; core/logging.py — RequestIDLogFilter + JSONFormatter sertakan request_id; setup_logger() sekarang konfigurasi root logger jadi semua modul database/llm/utils/api/cache ikut ter-cover, bukan cuma chatbot.*)*

### Day 17
- [x] Tambahkan metrics endpoint latency + error rate. *(/api/metrics — utils/metrics.py)*
- [x] Tambahkan metrik DB duration. *(query_durations tracked di metrics)*

### Day 18
- [x] Tambahkan metrik LLM duration + provider used. *(record_llm_call() di utils/metrics.py)*
- [x] Tambahkan cache hit/miss metric. *(cache_hits / cache_misses di utils/metrics.py)*

### Day 19
- [x] Buat dashboard sederhana (atau endpoint summary). *(main.py — `/api/metrics/summary`; utils/metrics.py — `MetricsCollector.get_summary()` + `_format_uptime()`)*
- [x] Verifikasi metrik mudah dibaca untuk debugging. *(tests/test_metrics_summary.py — status ok/degraded/critical, uptime_human, top_errors)*

### Day 20
- [x] Buat runbook: incident umum + langkah mitigasi. *(docs/RUNBOOK.md)*
- [x] Tambahkan playbook `service down` dan `quota habis`. *(Playbook 2 + 3 di RUNBOOK.md; juga cover DB unreachable, high error rate, slow queries, quick reference env var)*

### Day 21
- [ ] Buffer operability fixes.
- [ ] Pangkas noisy logs dan rapikan error message.

## D. Security & Governance

### Day 22
- [ ] Audit auth flow dan role access saat ini. *(tabel USERS punya kolom ROLE tapi belum di-enforce)*
- [ ] Definisikan RBAC minimal (`admin`, `analyst`, `viewer`).

### Day 23
- [ ] Terapkan role check pada endpoint kritikal. *(belum ada role guard di endpoint)*
- [ ] Tambahkan test negative untuk unauthorized access.

### Day 24
- [ ] Hardening SQL validator (allowlist/denylist tambahan).
- [ ] Tambah query cost/complexity guard sederhana.

### Day 25
- [ ] Review secret handling (hindari hardcoded/sensitif di repo).
- [ ] Perjelas template env untuk production.

### Day 26
- [ ] Aktifkan dependency vulnerability scan di CI.
- [ ] Tambahkan check basic security lint.

### Day 27
- [ ] Tambahkan audit log untuk export/query sensitif. *(belum ada)*
- [ ] Pastikan log tidak bocorkan credential/PII.

### Day 28
- [ ] Buffer hardening security week.
- [ ] Final pass akses dan permission boundary.

## E. Release & Closure

### Day 29
- [ ] Full regression: lint + tests + smoke manual.
- [ ] Final cleanup docs supaya sinkron implementasi.

### Day 30
- [ ] Tulis release notes + changelog.
- [ ] Tulis roadmap next 30 days berdasarkan gap tersisa.

## Definition of Done (Per Hari)
- [ ] Perubahan bisa dijalankan lokal.
- [ ] Test terkait lolos.
- [ ] Tidak menambah regression.
- [ ] Dokumentasi minimum diupdate.

---

## Ringkasan Status (Update: 22 Juni 2026)

| Kategori | Selesai | Belum | Total |
|---|---|---|---|
| A. Maintainability (Day 1–7) | 7 | 0 | 7 |
| B. Scalability (Day 8–14) | 10 | 0 | 10 |
| C. Operability (Day 15–21) | 7 | 2 | 9 |
| D. Security & Governance (Day 22–28) | 0 | 8 | 8 |
| E. Release & Closure (Day 29–30) | 0 | 2 | 2 |
| **Total** | **24** | **12** | **36** |

### Prioritas Selanjutnya (impact tertinggi untuk demo 8 minggu)
1. **Day 21** — Buffer operability + pangkas noisy logs (termasuk fix `RateLimiter` signature di tests)
2. **Day 22–23** — RBAC minimal `admin / analyst / viewer`
3. **Day 27** — Audit log untuk export/query sensitif
