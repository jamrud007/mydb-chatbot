# Laporan Progress — 2–8 Juni 2026

## 2 Juni — Audit penyebab aplikasi lambat
**Impact:** Ditemukan penyebab utama aplikasi lambat (proses ringkasan AI yang berat), jadi tahu apa yang harus diperbaiki duluan.
**Teknis:** Audit kode di alur `/api/chat` & `/api/execute`, ditemukan 7 proses sinkron yang memblokir response.

## 3 Juni — Bikin pengguna tidak perlu menunggu lama
**Impact:** Waktu tunggu pengguna untuk melihat hasil turun dari **~62 detik → ~2 detik**.
**Teknis:** Proses ringkasan AI dipindah ke background task (`TaskQueue` abstraction berbasis FastAPI `BackgroundTasks`), ditambah endpoint polling `GET /api/results/{id}/analysis`.

## 4 Juni — Rapikan batasan & validasi data di aplikasi
**Impact:** Sistem jadi lebih konsisten dan lebih ringan, fondasi lebih rapi untuk pengembangan berikutnya.
**Teknis:** Standarisasi pagination dengan `Query(ge=, le=)` di 3 endpoint (`/api/suggestions`, `/api/results`, `/api/cache/entries`), dan precompile pola regex validator SQL jadi class-level attribute di `database/query_executor.py` — menghilangkan kompilasi ulang 15 pola di setiap request.

## 5 Juni — Aktifkan sistem pemantau performa
**Impact:** Tim sekarang bisa melihat kondisi sistem secara real-time (kecepatan, error, beban) — sebelumnya alat ini ada tapi tidak terhubung sama sekali.
**Teknis:** `MetricsCollector` (`utils/metrics.py`) sudah lengkap tapi tidak pernah dipanggil dari kode produksi — `/api/metrics` selalu 0. Disambungkan ke `QueryExecutor.execute()` dan `OpenAIClient.get_response()`.

## 8 Juni — Uji coba sistem dengan banyak pengguna sekaligus
**Impact:** Ditemukan risiko: kalau diakses >20 orang bersamaan, respons jadi 10x lebih lambat. Ditemukan dari sekarang (sebelum demo), dan sudah ada rencana perbaikannya.
**Teknis:** Dibuat script load test `scripts/load_test_local.py` (async `httpx` + `asyncio.gather`), uji bertingkat concurrency 10/20/50 ke `/api/health`. Hasil: avg latency naik dari 28.7ms → 310ms — penyebabnya handler sync di thread-pool terbatas + Uvicorn 1 worker.

---

**Highlight utama:** waktu tunggu pengguna turun dari ~1 menit jadi ~2 detik, dan sekarang tim punya alat untuk memantau kesehatan sistem secara langsung.
