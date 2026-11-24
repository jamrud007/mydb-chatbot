# Worklog Day 5 — 22 Mei 2026

## Tujuan
Standarisasi config loading dan fallback env, serta hapus duplikasi constants/config yang tersebar di berbagai modul.

---

## Identifikasi Masalah / Topik Pekerjaan

**Topik:** Constants penting di-hardcode di banyak tempat, bukan dibaca dari satu sumber tunggal.

**Masalah yang ditemukan:**

1. `main.py` dan `services/app_services.py` sama-sama hardcode `ttl_seconds=3600`, `time_window=60`, `window_minutes=60` — perubahan di satu tempat tidak otomatis sinkron ke tempat lain.
2. `main.py` dan `services/app_services.py` pakai guard `hasattr(Config, 'MAX_REQUESTS_PER_MINUTE')` — artinya kode tidak yakin Config punya konstanta itu, tanda inkonsistensi.
3. `llm/ollama_client.py` hardcode `timeout=600` sebagai default parameter fungsi — tidak bisa dikontrol via env var tanpa mengubah kode.
4. `streamlit_app.py` memanggil `os.getenv("BACKEND_URL", "http://localhost:8000")` langsung, bypass `Config` yang sudah jadi sumber tunggal.
5. `core/config.py` belum punya field untuk: `RATE_LIMIT_TIME_WINDOW`, `RESULTS_CACHE_TTL`, `LLM_TIMEOUT`, `METRICS_WINDOW_MINUTES`, `BACKEND_URL`.

**Pertanyaan yang dijawab hari ini:**
- Constant apa saja yang perlu ditambahkan ke `core/config.py` supaya semua caller bisa membaca dari satu tempat?
- Bagaimana cara ganti default `timeout` di `OllamaClient` tanpa merusak caller yang sudah melewatkan nilai eksplisit?
- Apakah `streamlit_app.py` bisa import `Config` tanpa side effect?

---

## Yang Dikerjakan

### 1. Tambah 5 field baru ke `core/config.py`

Tambahan di bawah section Rate Limiting dan Cache Behavior:

```python
# Rate Limiting
RATE_LIMIT_TIME_WINDOW = int(os.getenv("RATE_LIMIT_TIME_WINDOW", 60))

# LLM Settings
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 600))
METRICS_WINDOW_MINUTES = int(os.getenv("METRICS_WINDOW_MINUTES", 60))

# Cache Behavior
RESULTS_CACHE_TTL = int(os.getenv("RESULTS_CACHE_TTL", "3600"))

# Frontend / Streamlit Settings
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
```

Semua pakai `os.getenv` dengan fallback — bisa dikontrol via `.env` tanpa mengubah kode.

### 2. Fix `main.py`

- Hapus `hasattr` guard pada inisialisasi `RateLimiter`.
- Ganti `time_window=60` → `time_window=Config.RATE_LIMIT_TIME_WINDOW`.
- Ganti `ttl_seconds=3600` → `ttl_seconds=Config.RESULTS_CACHE_TTL`.
- Ganti `window_minutes=60` → `window_minutes=Config.METRICS_WINDOW_MINUTES`.

### 3. Fix `services/app_services.py`

Perubahan identik dengan `main.py`:
- Hapus `hasattr` guard.
- Ganti 3 magic number dengan referensi ke `Config`.

### 4. Fix `llm/ollama_client.py`

- Import `Config` dari `core.config`.
- Ubah signature: `timeout: int = 600` → `timeout: int = None`.
- Di body `__init__`: `self.timeout = timeout if timeout is not None else Config.LLM_TIMEOUT`.
- Caller yang melewatkan `timeout` eksplisit tidak terpengaruh. Caller yang tidak melewatkan (seperti `llm_factory.py`) otomatis pakai `Config.LLM_TIMEOUT`.

### 5. Fix `streamlit_app.py`

- Tambah `from config import Config`.
- Ganti `API_BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")` → `API_BASE_URL = Config.BACKEND_URL`.
- Ganti `timeout=30.0` di `call_auth_api` → `float(Config.QUERY_TIMEOUT_SECONDS)`.
- Ganti `timeout=600.0` di `call_api` → `float(Config.LLM_TIMEOUT)`.

### 6. Smoke Check

```
python -m py_compile core/config.py main.py services/app_services.py llm/ollama_client.py streamlit_app.py
→ OK: semua file compile bersih
```

---

## Hasil

- `core/config.py` sekarang menjadi **satu sumber tunggal** untuk semua konstanta operasional.
- Semua nilai bisa dikontrol via env var tanpa mengubah kode.
- Tidak ada lagi magic number tersebar di file-file utama untuk konstanta yang sering berubah.
- Duplikasi dihilangkan di 4 file: `main.py`, `services/app_services.py`, `llm/ollama_client.py`, `streamlit_app.py`.

**Daftar constants yang sekarang terpusat:**

| Constant | Env Var | Default | Dipakai di |
|---|---|---|---|
| `MAX_REQUESTS_PER_MINUTE` | `MAX_REQUESTS_PER_MINUTE` | `10` | main, app_services |
| `RATE_LIMIT_TIME_WINDOW` | `RATE_LIMIT_TIME_WINDOW` | `60` | main, app_services |
| `RESULTS_CACHE_TTL` | `RESULTS_CACHE_TTL` | `3600` | main, app_services |
| `METRICS_WINDOW_MINUTES` | `METRICS_WINDOW_MINUTES` | `60` | main, app_services |
| `LLM_TIMEOUT` | `LLM_TIMEOUT` | `600` | ollama_client, streamlit |
| `QUERY_TIMEOUT_SECONDS` | `QUERY_TIMEOUT_SECONDS` | `30` | streamlit (auth API) |
| `BACKEND_URL` | `BACKEND_URL` | `http://localhost:8000` | streamlit |

---

## Tidak Dilakukan (Scope Batas)

- Belum standarisasi constants di file-file script one-off (`check_mistral_duration.py`, `benchmark_ollama.py`, dll) — script tersebut bukan bagian dari production path.
- Belum audit `database/schema_manager.py` yang juga punya `cache_ttl=3600` — nilainya sudah cocok dengan `Config.SCHEMA_CACHE_TTL` yang sudah ada sejak awal, tapi belum di-wire. Ini kandidat Day 6.
- Belum tambahkan `BACKEND_URL` ke `.env.example` — dokumentasi env template.

## Next

- Day 6: Tambahkan/rapikan type hints di modul kritikal, aktifkan lint+format lokal (`ruff`/`black`).

---

## Penjelasan (Kenapa Day 5 Penting)

**Masalah sebelumnya:**
Satu konstanta bisa muncul di 3+ tempat berbeda. Jika operator ingin ubah rate limit window dari 60s ke 120s, mereka harus edit `main.py`, `services/app_services.py`, dan `utils/rate_limiter.py` sekaligus. Satu tempat terlewat = inkonsistensi runtime yang sulit debug.

**Yang diselesaikan:**
```
Sebelum:
main.py          → time_window=60 (hardcoded)
app_services.py  → time_window=60 (hardcoded)

Sesudah:
main.py          → time_window=Config.RATE_LIMIT_TIME_WINDOW
app_services.py  → time_window=Config.RATE_LIMIT_TIME_WINDOW
.env             → RATE_LIMIT_TIME_WINDOW=120  ← satu titik kontrol
```

**Kenapa pola `timeout: int = None` di OllamaClient?**
Python mengevaluasi default parameter saat module di-load, bukan saat fungsi dipanggil. Kalau kita tulis `timeout: int = Config.LLM_TIMEOUT`, nilai ter-freeze saat import dan tidak bisa di-override dengan patching Config di test. Pola `None` + fallback di body `__init__` memungkinkan nilai dibaca saat runtime dan lebih mudah di-test.
