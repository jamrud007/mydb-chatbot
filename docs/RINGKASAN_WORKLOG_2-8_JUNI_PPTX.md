# Ringkasan Progress — 2–8 Juni 2026 (Skalabilitas, Day 8–14)

> Sumber: WORKLOG_2026-06-02_DAY8, _DAY9, _DAY12, _DAY14, _DAY13
> Format: tiap `##` = 1 slide. Bullet di bawahnya siap dipakai langsung di pptx.

---

## Slide 1 — Konteks: Kenapa Minggu Ini Fokus ke Skalabilitas?

- Sebelumnya: hampir semua proses di backend berjalan **sinkron** — LLM call, query DB, export, report semua memblokir HTTP response.
- Dengan LLM lokal (Ollama), satu request `/api/chat` bisa makan **10–60 detik**, dan `/api/execute/` bisa sampai **~62 detik** karena auto-analysis ikut diproses sebelum response dikirim.
- Target: pisahkan proses berat dari request path, perkuat caching & query executor, lalu pasang instrumentasi (metrics) supaya semua perbaikan ini bisa **diukur**, bukan cuma "terasa lebih cepat".

---

## Slide 2 — 2 Juni: Audit Proses Berat (Day 8)

**Tujuan:** Identifikasi proses sinkron yang memblokir user, tentukan kandidat untuk dijadikan async/background.

**Temuan kunci — 7 proses berat diinventarisasi:**
| Proses | Endpoint | Durasi | Wajib blokir? |
|---|---|---|---|
| Auto-analysis insight (LLM) | `/api/execute/{i}` | 10–60s | **Tidak** — data sudah ada |
| NL→SQL generation (LLM) | `/api/chat` | 10–60s | Ya |
| Query clarification (LLM) | `/api/chat` | 5–30s | Ya |
| Daily report | `/api/admin/daily-report` | 1–5s | Tidak (admin only) |

**Keputusan:** Auto-analysis = quick win prioritas #1 — bisa dipindah ke background task, berpotensi memangkas response time `/api/execute/` dari **~70 detik → <5 detik**.

**Output:** `docs/ASYNC_WORKER_CANDIDATES.md` — peta jalan untuk Day 9–10.

---

## Slide 3 — 3 Juni: Background Task untuk Auto-Analysis (Day 9)

**Tujuan:** Pisahkan proses berat dari request path tanpa infrastruktur baru.

**Yang dibangun:**
- Abstraksi `TaskQueue` (interface) + `BackgroundTaskQueue` (implementasi via FastAPI `BackgroundTasks`) — agar nanti bisa di-swap ke Celery/Redis tanpa ubah kode endpoint.
- `analysis_status` (`pending` / `ready` / `failed`) ditambahkan ke setiap hasil query.
- Endpoint baru `GET /api/results/{id}/analysis` untuk polling hasil analysis.
- `/api/admin/daily-report` diubah jadi `202 Accepted` instan (fire-and-forget background task).

**Dampak terukur:**
| Endpoint | Sebelum | Sesudah |
|---|---|---|
| `POST /api/execute/{i}` | ~62 detik (DB + LLM analysis) | **~2 detik** (analysis di background) |
| `POST /api/admin/daily-report` | Blokir 1–5 detik | Return 202 instan |

> User langsung lihat data dalam 2 detik; insight analysis menyusul via polling — tanpa menambah server/infra baru.

---

## Slide 4 — 4 Juni: Pagination Konsisten + Optimasi Query Executor (Day 12)

**Tujuan:** Rapikan limit/pagination di semua endpoint daftar, dan bereskan bottleneck di query executor.

**Yang dikerjakan:**
- Validasi & cap pagination konsisten via `Query(ge=, le=)` di 3 endpoint: `/api/suggestions` (maks 50), `/api/results` (maks 200, + `offset`/`total`), `/api/cache/entries` (maks 500).
- **Precompile regex** validasi SQL & row-limiter di `QueryExecutor` — pola yang sebelumnya di-*compile ulang* setiap kali query divalidasi (15 pola), sekarang jadi class-level attribute yang dikompilasi sekali saat load.

**Dampak:** Menghilangkan overhead recompile regex per-request + mencegah client menarik data dalam jumlah tak terbatas dari endpoint manapun — konsisten di seluruh API.

---

## Slide 5 — 5 Juni: MetricsCollector "Hidup" — Wiring + Latency Baseline (Day 14)

**Temuan kritis:** `MetricsCollector` sudah dibangun lengkap (query duration, LLM call, error, cache hit-rate) dan endpoint `/api/metrics` sudah ada — **tapi tidak ada satupun kode produksi yang memanggilnya**. Hasilnya, `/api/metrics` selalu mengembalikan semua angka **0**, walau sistem sudah berjalan.

**Perbaikan:**
- Wire `record_query_duration` + `record_error` ke `QueryExecutor.execute()` (cache HIT, cache MISS, dan exception path).
- Wire `record_llm_call` ke `OpenAIClient.get_response()` — mencakup semua provider OpenAI-compatible (DeepSeek, dll).
- Perbaiki `slow_query_count` agar window-filtered (konsisten dengan metrik lain), sambil tetap menyediakan hitungan all-time.

**Output:** `docs/LATENCY_BASELINE_DAY14.md` — baseline latency per komponen (DB query, LLM inference, end-to-end), referensi untuk mengukur dampak optimasi berikutnya.

> Sebelum: `/api/metrics` → semua 0. Sesudah: terisi data nyata dari setiap request yang masuk.

---

## Slide 6 — 8 Juni: Slow Query Guard + Uji Beban Ringan (Day 13)

**Tujuan:** Pastikan sistem punya visibility ke query lambat, dan ukur perilakunya di bawah beban concurrent.

**Bagian 1 — Slow query guard:** Query > 5 detik otomatis tercatat (`utils/metrics.py`), terhubung ke MetricsCollector sejak Day 14 — sekarang benar-benar menerima data nyata, bukan sekadar terpasang.

**Bagian 2 — Load test lokal (`scripts/load_test_local.py`):**
- Pendekatan **async** (`httpx.AsyncClient` + `asyncio.gather`/`Semaphore`) — concurrency murah tanpa overhead thread OS.
- Hasil pada `/api/health` (concurrency 10 → 50): **avg latency naik ~10x (28.7ms → 310ms)**, throughput justru **turun** (250 → 131 req/s).

**Temuan penting:** Bottleneck-nya bukan di database/cache — endpoint murni baca status in-memory. Penyebabnya: handler `def` (sync) berjalan di thread-pool terbatas, Uvicorn cuma **1 worker**. Di atas ~20 request bersamaan, request mulai antre.

**Implikasi demo Minggu 8:** Target response cache HIT (`< 500ms`) bisa meleset bukan karena cache lambat, tapi karena antrean di lapisan server saat banyak user mengakses bersamaan.

---

## Slide 7 — Ringkasan Dampak Keseluruhan (8–14 = "Scalability Sprint")

| Area | Sebelum | Sesudah |
|---|---|---|
| Response `/api/execute/` (analysis) | ~62 detik | ~2 detik |
| Daily report | Blokir 1–5 detik | 202 instan |
| Pagination API | Tidak konsisten, tanpa cap | Konsisten + tervalidasi (`Query(ge,le)`) |
| Regex validasi SQL | Recompile tiap request | Precompiled sekali di class-load |
| `/api/metrics` | Selalu 0 | Data nyata (query, LLM, cache, error) |
| Visibility performa | Tidak ada | Slow query guard + latency baseline + load test |

**Rekomendasi lanjutan (buffer day berikutnya):**
1. Konversi endpoint baca-saja jadi `async def` agar tidak menyita thread pool.
2. Tambah `workers=N` pada Uvicorn / jalankan via Gunicorn untuk multi-core.
3. Ulangi load test setelah `request_id` middleware (Day 16) aktif untuk trace per-request.
