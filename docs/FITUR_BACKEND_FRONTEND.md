# Fitur Backend & Frontend — Oracle SQL Chatbot

## Backend (FastAPI — port 8000)

### Auth (`/api/auth/...`)

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/auth/register` | POST | Daftar user baru, kirim OTP verifikasi ke email |
| `/api/auth/login` | POST | Login dengan username/email + password, return JWT token |
| `/api/auth/verify-otp` | POST | Verifikasi kode OTP dari email |
| `/api/auth/me` | GET | Info user yang sedang login |
| `/api/auth/refresh` | POST | Perpanjang masa berlaku JWT token |
| `/api/auth/verify-token` | POST | Cek apakah token masih valid |

### Chat & Query

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/chat` | POST | Terima pertanyaan natural language → generate SQL via LLM → eksekusi ke Oracle → return hasil |
| `/api/execute/{query_index}` | POST | Eksekusi ulang SQL dari index query tertentu |
| `/api/suggestions` | GET | Saran pertanyaan otomatis berdasarkan schema aktif |

### Hasil & Export

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/results` | GET | List semua hasil query yang tersimpan di cache |
| `/api/results/{result_id}` | GET | Ambil detail hasil query spesifik |
| `/api/results/{result_id}/analysis` | GET | Analisis otomatis hasil query (statistik, insight) |
| `/api/export/csv/{query_index}` | GET | Export hasil query ke file CSV |
| `/api/history/export/json` | GET | Export riwayat percakapan format JSON |
| `/api/history/export/csv` | GET | Export riwayat percakapan format CSV |
| `/api/history/export/text` | GET | Export riwayat percakapan format teks |
| `/api/history/export/stats` | GET | Statistik riwayat query |

### Schema Oracle

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/schema/docs/markdown` | GET | Dokumentasi schema JOINGATEOCR format Markdown |
| `/api/schema/docs/html` | GET | Dokumentasi schema format HTML |
| `/api/schema/docs/json` | GET | Dokumentasi schema format JSON |

### Monitoring & Cache

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/health` | GET | Status kesehatan: DB, LLM, cache |
| `/api/metrics` | GET | Statistik penggunaan: request count, latency, error rate |
| `/api/metrics/summary` | GET | Ringkasan metrik (status ok/degraded/critical, uptime, error rate, latency query/LLM, cache hit rate) — versi ringan `/api/metrics` untuk widget status |
| `/api/cache/stats` | GET | Info cache: jumlah entry, ukuran, backend |
| `/api/cache/entries` | GET | List semua entry cache |
| `/api/cache/entry/{cache_key}` | GET | Detail satu entry cache |
| `/api/cache/clear` | DELETE | Hapus semua cache query |

### Admin & Feedback

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/admin/daily-report` | POST | Trigger pengiriman laporan harian via email |
| `/api/feedback` | POST | Kirim rating dan komentar untuk hasil query |

---

## Frontend (Streamlit — port 8501)

### Sidebar

| Komponen | Fungsi |
|---|---|
| Info user | Tampilkan username dan email yang sedang login |
| Tombol Logout | Hapus session dan kembali ke halaman login |
| Recent Queries | Riwayat query dari cache — bisa diklik untuk load ulang |
| API Status | Indikator koneksi backend: ✅ Connected / ⚠️ Degraded / ❌ Offline |
| DB & LLM Status | Status koneksi Oracle dan provider LLM aktif |
| Query Cache | Ukuran cache (MB), backend (SQLite/Redis), tombol Clear Cache |

### Tab 1 — Chat (`💬`)

| Fitur | Deskripsi |
|---|---|
| Input natural language | Kolom teks untuk pertanyaan dalam bahasa Indonesia/Inggris |
| Clarification handler | Jika pertanyaan ambigu, sistem minta klarifikasi sebelum generate SQL |
| Preview SQL | SQL yang di-generate LLM ditampilkan sebelum dieksekusi |
| Hasil tabel | Data hasil query ditampilkan sebagai tabel interaktif |
| Auto-visualization | Chart otomatis di-generate jika data cocok (bar, line, pie, dll.) |
| Feedback | Rating bintang + kolom komentar untuk setiap hasil query |
| Export CSV | Tombol download hasil query langsung ke file CSV |

### Tab 2 — Single Chart (`📊`)

| Fitur | Deskripsi |
|---|---|
| Pilih jenis chart | Bar, Line, Pie, Scatter, dan lainnya |
| Konfigurasi sumbu | Pilih kolom untuk sumbu X dan Y secara manual |
| Render Plotly | Chart interaktif dengan zoom, hover, dan filter |

### Tab 3 — Dashboard (`🎛️`)

| Fitur | Deskripsi |
|---|---|
| Multi-chart | Tampilkan beberapa chart sekaligus dalam satu halaman |
| Monitoring device | Visualisasi status dan response time perangkat |
| Gate analytics | Analisis transaksi gate, OCR accuracy, payment status |

### Tab 4 — Data Table (`📋`)

| Fitur | Deskripsi |
|---|---|
| Raw data | Tampilan tabel penuh tanpa filter chart |
| Sort & filter | Klik header kolom untuk sort, filter per kolom |
| Ekspor langsung | Download data mentah hasil query |

---

## Alur Kerja Utama

```
User ketik pertanyaan
        │
        ▼
Streamlit kirim ke POST /api/chat
        │
        ▼
Backend generate SQL via LLM (Ollama / Gemini / OpenAI-compatible)
        │
        ▼
SQL divalidasi (read-only guard, syntax check, row limit)
        │
        ▼
Query dieksekusi ke Oracle 19c — schema JOINGATEOCR
        │
        ▼
Hasil di-cache (SQLite / Redis)
        │
        ▼
Streamlit tampilkan: tabel + chart otomatis + tombol export CSV
```

---

## Keamanan

| Mekanisme | Keterangan |
|---|---|
| JWT Authentication | Semua endpoint (kecuali login/register) wajib token |
| Password hashing | bcrypt — password tidak disimpan plaintext |
| Rate limiting | Batas request per menit per user |
| Read-only guard | Query non-SELECT (INSERT/UPDATE/DELETE/DROP) diblokir |
| Query timeout | Eksekusi dibatasi waktu (default 30 detik) |
| Row limit | Hasil dibatasi maksimum baris (default 100 rows) |
| OTP email | Registrasi wajib verifikasi email sebelum bisa login |
