# Worklog Day 4 — 19 Mei 2026

## Tujuan
Pilot repository pattern dari `database/query_executor.py` dan rapikan import agar tidak circular.

---

## Identifikasi Masalah / Topik Pekerjaan

**Topik:** Tidak ada lapisan pemisah antara service layer dan database layer.

**Masalah yang ditemukan:**
1. `services/app_services.py` dan beberapa bagian `main.py` bisa langsung import `database/query_executor.py` — tidak ada boundary yang jelas.
2. `QueryExecutor` tahu terlalu banyak hal sekaligus: validasi query, eksekusi, caching, row limiting — detail ini bocor ke layer atas yang mengimportnya.
3. Folder `repositories/` sudah dibuat sejak Day 1 tapi masih benar-benar kosong.
4. Jika `QueryExecutor` diubah (misalnya ditambah async, atau ganti backend), semua tempat yang mengimportnya harus diupdate.
5. Risiko circular import: jika `services/` import `database/` dan `database/` suatu saat butuh import dari `services/`, terjadi circular.

**Pertanyaan yang dijawab hari ini:**
- Interface minimal apa yang perlu di-expose dari `QueryRepository` ke service layer?
- Bagaimana wire `QueryRepository` ke `AppServices` tanpa merusak inisialisasi yang sudah ada?
- Apakah import graph setelah penambahan ini bebas circular?

---

## Yang Dikerjakan

### 1. Buat `repositories/__init__.py`
- Inisialisasi layer repository sebagai Python package.

### 2. Buat `repositories/query_repository.py`
- Wrap `QueryExecutor` dengan interface repository yang bersih.
- Method yang di-expose ke service layer:
  - `validate(query)` → `(is_valid, error_msg)`
  - `execute(query, ...)` → result dict
  - `get_cache_key(query)` → canonical query string
- Service layer tidak lagi perlu import `database/` langsung.

### 3. Update `services/app_services.py`
- Tambah `QueryRepository` sebagai field di `AppServices` dataclass.
- Wire `QueryExecutor` → `QueryRepository` di `build_app_services()`.
- Import order: `database/` hanya diimport di `app_services.py` dan `repositories/`, tidak dari service lain.

### 4. Smoke Check
- `python -m py_compile repositories/__init__.py repositories/query_repository.py services/app_services.py` → OK

## Hasil
- Layer `repositories/` sekarang aktif (pilot 1 repository).
- Import dependency graph:
  - `api` → `services` → (repositories, chatbot)
  - `repositories` → `database`
  - Tidak ada circular import.

## Tidak Dilakukan (Scope Batas)
- Belum migrasi endpoint `main.py` untuk pakai `QueryRepository` langsung — ini scope Day berikutnya.
- Belum extraction cache/export domain dari `main.py`.

## Next
- Day 5: Standarisasi config loading dan hapus duplikasi constants.

---

## Penjelasan (Kenapa Day 4 Penting)

**Masalah sebelumnya:**
Service layer dan endpoint bisa langsung import `database/query_executor.py`.
Artinya layer atas tahu detail implementasi database — melanggar layered architecture.
Kalau `QueryExecutor` direfactor atau diganti, banyak tempat harus diubah sekaligus.

**Yang diselesaikan:**
`QueryRepository` menjadi satu-satunya pintu masuk ke `QueryExecutor` dari layer atas:

```
Sebelum:
services/ ──────────────────────► database/query_executor.py
main.py  ──────────────────────► database/query_executor.py

Sesudah:
services/ ──► repositories/query_repository.py ──► database/query_executor.py
main.py   ──► (bertahap akan ikut pakai QueryRepository)
```

**Interface yang di-expose (hanya 3 method):**
- `validate(query)` — cek keamanan query
- `execute(query, ...)` — jalankan dan return result
- `get_cache_key(query)` — ambil canonical query untuk cache

**Kenapa ini penting?**
- Kalau besok `QueryExecutor` diganti (misalnya support async), hanya `QueryRepository` yang diubah.
- Service layer tidak perlu tahu soal cache manager, engine type, atau row limit — semua tersembunyi di dalam.
- Import graph jadi satu arah: `services` → `repositories` → `database` (tidak ada circular).
