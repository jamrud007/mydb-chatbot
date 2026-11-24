# Worklog Day 7 — 29 Mei 2026

## Tujuan
Dokumentasi arsitektur versi baru dan buffer fix untuk technical debt Week 1.

---

## Identifikasi Masalah / Topik Pekerjaan

**Topik 1:** Belum ada dokumen arsitektur yang menjelaskan struktur folder, dependency graph, dan layer system setelah refactoring Week 1.

**Topik 2 (Buffer Fix):** `.env.example` belum mencantumkan 4 konstanta yang ditambahkan ke `core/config.py` pada Day 5:
- `MAX_REQUESTS_PER_MINUTE`
- `RATE_LIMIT_TIME_WINDOW`
- `RESULTS_CACHE_TTL`
- `METRICS_WINDOW_MINUTES`
- `LLM_TIMEOUT`

Operator yang mau override nilai-nilai ini lewat environment tidak punya referensi apa nama env var-nya.

**Debt lain yang dicek dan sudah beres:**
- `database/schema_manager.py` — sudah pakai `Config.SCHEMA_CACHE_TTL` sejak Day 6, tidak ada hardcode.
- `repositories/query_repository.py` — sudah aktif dan digunakan `services/app_services.py`.

---

## Yang Dikerjakan

### 1. Buat `docs/architecture.md`

Dokumen baru yang mencakup:
- **Overview** — dua runtime process (API server + Streamlit frontend)
- **Layer Diagram** — ASCII diagram 5 layer: Frontend → API → Services → Repositories → Data/Infrastructure → Core
- **Import Dependency Graph** — one-directional, no circular imports
- **Deskripsi setiap layer** — file per file dengan role masing-masing
- **Configuration Reference** — tabel semua `Config` field, env var, default, dan used by
- **Week 1 Refactoring Summary** — tabel ringkasan Day 1–7
- **Running Locally** — quick-start commands

### 2. Update `.env.example` — Buffer Fix

Tambah 5 entry baru di bawah section Rate Limiting:

```ini
MAX_REQUESTS_PER_MINUTE=10
RATE_LIMIT_TIME_WINDOW=60
RESULTS_CACHE_TTL=3600
METRICS_WINDOW_MINUTES=60
LLM_TIMEOUT=600
```

Setiap entry punya komentar penjelasan.

---

## Hasil

- `docs/architecture.md` sekarang jadi single document of truth untuk struktur project.
- `.env.example` sekarang lengkap — semua konstanta yang dikontrol via env sudah terdokumentasi.
- Tidak ada perubahan behavior (pure documentation + env template).

---

## Tidak Dilakukan (Scope Batas)

- Belum migrasi endpoint di `main.py` untuk pakai `QueryRepository` langsung (endpoint masih import `QueryExecutor` via `ChatbotHandler`) — ini debt yang valid tapi skopnya lebih besar, kandidat Day 8+.
- Belum tambah diagram interaktif atau gambar — ASCII diagram cukup untuk dokumentasi text-based.

---

## Status Week 1

| Task | Status |
|---|---|
| Day 1–2: Struktur folder + service skeleton | ✅ Done |
| Day 3: Chat flow ke service layer | ✅ Done |
| Day 4: Repository pattern pilot | ✅ Done |
| Day 5: Centralized config | ✅ Done |
| Day 6: Type hints + ruff/black | ✅ Done |
| Day 7: Architecture docs + buffer fix | ✅ Done |

**Week 1 selesai: 7/7 done.**

---

## Next

- Day 8 (Week 2 — Scalability): Identifikasi proses berat sinkron (LLM analysis, reports, export) dan tentukan kandidat async worker.

---

## Penjelasan (Kenapa Day 7 Penting)

**Masalah sebelumnya:**
Setelah 6 hari refactoring, kode sudah jauh lebih rapi tapi tidak ada satu dokumen yang menjelaskan "ini proyeknya seperti apa sekarang". Onboarding developer baru atau review oleh atasan membutuhkan dokumen ini.

**Yang diselesaikan:**
- Developer baru bisa baca `docs/architecture.md` dan langsung tahu: folder mana berisi apa, dependency mengalir ke arah mana, dan env var mana yang bisa di-tune.
- Operator/sysadmin bisa buka `.env.example` dan langsung tahu semua nilai yang bisa dikustomisasi.

**Kenapa `.env.example` penting sebagai buffer fix?**
`.env.example` adalah kontrak antara developer dan operator. Kalau ada konstanta di `Config` yang tidak ada di `.env.example`, operator tidak akan tahu cara men-tune-nya tanpa baca kode. Ini gap kecil tapi nyata — terutama untuk `LLM_TIMEOUT` (operator perlu tau ini kalau LLM lambat) dan `RESULTS_CACHE_TTL` (mau disable caching? Override ke 0).
