# Latency Baseline — Day 14 (4 Juni 2026)

Dokumen ini mencatat baseline latency sistem sebelum dan sesudah perbaikan skalabilitas minggu 2 (Day 8–14). Tujuannya sebagai referensi untuk mengukur dampak optimasi di iterasi berikutnya.

---

## Metodologi

Pengukuran dilakukan secara manual di lingkungan development (CPU, tanpa GPU) dengan konfigurasi:
- OS: Ubuntu 22.04 LTS
- Model LLM: Qwen2.5-SQL Q5_K_M via Ollama (target), Mistral 7B NL2SQL (saat ini terukur)
- Database: Oracle 19c Docker, schema JOINGATEOCR
- Cache backend: SQLite

Titik ukur adalah end-to-end dari request masuk hingga response keluar, dibagi per komponen.

---

## Komponen & Latency Terukur

### A. Query DB (tanpa LLM)

| Tipe Query | Sebelum Optimasi | Sesudah (Day 11–12) | Catatan |
|------------|-----------------|---------------------|---------|
| Cache HIT | — | ~0 ms | Dikembalikan dari SQLite tanpa menyentuh DB |
| Query sederhana (1 tabel) | 200–800 ms | 200–800 ms | Tidak berubah — bottleneck di network/DB |
| Query multi-JOIN (3+ tabel) | 1.000–5.000 ms | 1.000–5.000 ms | Timeout guard aktif di 30 detik |
| Query timeout (> 30 detik) | Process hang | Terpotong 30 detik | `max_execution_time` MySQL / `call_timeout` Oracle |

### B. LLM Inference

| Provider | Sebelum | Sesudah (Day 9) | Catatan |
|----------|---------|----------------|---------|
| Mistral 7B (CPU lokal) | Blokir response 15–20 detik | 15–20 detik (background) | Day 9: LLM analysis dipindah ke background task |
| Qwen2.5-SQL (CPU lokal, target) | — | ~20–30 detik | Belum di-deploy, estimasi berdasarkan ukuran model |
| DeepSeek fallback | Tidak ada | 2–5 detik | Aktif sejak Day 10 (fallback provider) |
| Gemini fallback | Tidak ada | 2–4 detik | Aktif sejak Day 10 |

### C. End-to-End Response `/api/execute`

| Kondisi | Sebelum Day 9 | Sesudah Day 9 | Delta |
|---------|--------------|--------------|-------|
| Cache HIT | ~62 detik | ~0.2 detik | **−99%** |
| Cache MISS + analysis | ~62 detik | ~2–5 detik (data) + analysis background | **−95% waktu tunggu user** |
| Cache MISS, Ollama offline | Gagal | 2–5 detik (fallback cloud) | **+availability** |

### D. Overhead Komponen Sistem

| Komponen | Latency Tambahan | Keterangan |
|----------|-----------------|------------|
| JWT validation | < 1 ms | Sinkron, tidak signifikan |
| Rate limiter check | < 1 ms | In-memory dict |
| Schema reader (cached) | ~0 ms | Schema di-cache setelah load pertama |
| Schema reader (cold) | 2.000–4.000 ms | Hanya terjadi saat restart atau cache expired |
| SQL validator | < 5 ms | Regex precompiled (Day 12) |
| Pagination/serialization | < 10 ms | JSON serialization untuk 100 baris |

---

## Perubahan yang Berdampak Langsung pada Latency

| Day | Perubahan | Dampak Terukur |
|-----|-----------|----------------|
| Day 9 | LLM analysis ke background task | Response `/api/execute` turun dari ~62s → ~2–5s |
| Day 10 | Fallback provider (DeepSeek/Gemini) | Zero-downtime jika Ollama offline |
| Day 10 | Retry + exponential backoff | Menghindari hard-fail pada network blip sementara |
| Day 11 | Cache TTL + auto cleanup | Mencegah SQLite cache membesar tak terbatas |
| Day 12 | Regex precompile di QueryExecutor | Eliminasi recompile 15 pattern per request |
| Day 13 | Slow query guard (> 5 detik) | Visibility ke query yang bermasalah |
| Day 14 | Wire MetricsCollector ke execution path | `/api/metrics` sekarang punya data nyata |

---

## Status Metrics Setelah Day 14

Sebelum Day 14, endpoint `/api/metrics` mengembalikan semua angka 0 karena `record_query_duration()` dan `record_llm_call()` tidak pernah dipanggil. Sesudah Day 14:

```
GET /api/metrics
{
  "query_performance": {
    "total_queries": N,          ← sekarang terisi
    "avg_duration_ms": X,        ← sekarang terisi
    "p95_duration_ms": X,        ← sekarang terisi
    "slow_query_count": N,       ← window-filtered (bukan all-time)
    "slow_query_count_all_time": N
  },
  "llm": {
    "total_calls": N,            ← sekarang terisi
    "success_rate_percent": X,   ← sekarang terisi
    "avg_duration_ms": X         ← sekarang terisi
  },
  "cache": {
    "hit_rate_percent": X        ← sekarang terisi
  }
}
```

---

## Target Latency untuk Demo (Minggu 8)

| Metrik | Target | Kondisi |
|--------|--------|---------|
| Response `/api/execute` (cache HIT) | < 500 ms | — |
| Response `/api/execute` (cache MISS, CPU) | < 35 detik | Ollama lokal aktif |
| Response `/api/execute` (cache MISS, GPU) | < 5 detik | Jika GPU tersedia |
| Response `/api/execute` (fallback cloud) | < 8 detik | Ollama offline |
| Cache hit rate (setelah warm-up) | > 30% | Untuk query berulang dalam 7 hari |
| LLM success rate | > 95% | Dengan retry + fallback |
| Slow query rate (> 5 detik DB) | < 10% | Dari total query |

---

## Catatan: Load Test (Day 13 — tidak selesai)

Uji beban ringan concurrent requests direncanakan di Day 13 namun belum dilakukan. Prioritas utama adalah memastikan MetricsCollector menerima data nyata terlebih dahulu (Day 14), sehingga load test berikutnya bisa menghasilkan angka yang valid dan bisa dibandingkan.

Load test dijadwalkan ulang setelah Day 16 (request_id middleware aktif) agar setiap concurrent request bisa di-trace secara individual.
