# Proposal Pengembangan — myDB Chatbot
**Sistem Tanya-Jawab Database Berbasis Natural Language**

Pelabuhan Joingate · Versi 2.0 · Juni 2026

---

## Ringkasan Eksekutif

myDB Chatbot adalah sistem yang memungkinkan pengguna — tanpa keahlian SQL sekalipun — mengajukan pertanyaan bisnis dalam bahasa Indonesia atau Inggris dan mendapatkan jawaban langsung dari database operasional perusahaan. Pertanyaan dikonversi secara otomatis menjadi query SQL oleh model **Qwen2.5-SQL** yang berjalan sepenuhnya di server lokal, dieksekusi ke Oracle 19c atau PostgreSQL, lalu hasilnya ditampilkan sebagai tabel interaktif, grafik, dan laporan yang dapat diekspor. Seluruh data tetap berada dalam infrastruktur perusahaan — tidak ada yang dikirim ke layanan cloud pihak ketiga.

---

## 1. Latar Belakang

Sistem operasional gate container di Pelabuhan Joingate menghasilkan volume data transaksi yang besar setiap harinya: data OCR kendaraan, pembayaran tiket, histori status perangkat monitoring, hingga log akurasi sistem autogate. Data ini tersimpan dalam database Oracle 19c schema **JOINGATEOCR** yang mencakup lebih dari 15 tabel saling berelasi.

Selama ini, mengambil insight dari data tersebut hanya bisa dilakukan oleh tim teknis yang memahami struktur database dan mampu menulis query SQL. Akibatnya timbul dua masalah nyata:

- **Ketergantungan teknis.** Manajer operasional atau staf non-teknis yang ingin mengetahui tren transaksi, akurasi OCR, atau status perangkat harus mengajukan permintaan ke tim IT terlebih dahulu — menambah beban kerja IT dan memperlambat pengambilan keputusan.
- **Kecepatan respons.** Pertanyaan bisnis yang seharusnya terjawab dalam hitungan menit bisa membutuhkan waktu berjam-jam jika harus melalui siklus permintaan → penulisan query → eksekusi → laporan.

myDB Chatbot dirancang untuk menutup celah ini. Dengan memanfaatkan **Qwen2.5-SQL** — model AI generasi terbaru yang dioptimalkan khusus untuk tugas teks-ke-SQL — pengguna cukup mengetik pertanyaan seperti *"Berapa total transaksi gate kemarin yang pembayarannya berhasil?"* dan sistem akan menghasilkan query Oracle yang valid, mengeksekusinya, lalu menyajikan hasilnya secara langsung — dalam hitungan detik.

Keputusan untuk menjalankan AI secara lokal bukan semata teknis, melainkan strategis: data transaksi pelabuhan termasuk kategori data operasional sensitif. Menggunakan layanan AI cloud komersial berarti mengirimkan data tersebut ke server pihak ketiga, yang bertentangan dengan prinsip kedaulatan data dan berisiko terhadap kepatuhan regulasi UU PDP. Dengan model lokal, tidak ada satu byte pun data keluar dari infrastruktur perusahaan.

---

## 2. Tujuan Proyek

Proyek ini memiliki lima tujuan utama yang saling melengkapi:

| Tujuan | Deskripsi |
|--------|-----------|
| **Aksesibilitas Data** | Pengguna non-teknis dapat mengakses data Oracle/PostgreSQL tanpa menulis SQL |
| **Kecepatan Insight** | Pertanyaan bisnis terjawab dalam hitungan detik, bukan berjam-jam |
| **Kedaulatan Data** | AI berjalan 100% lokal — tidak ada data yang keluar dari infrastruktur perusahaan |
| **Keamanan Akses** | Akses dibatasi read-only dengan autentikasi JWT + OTP verifikasi email |
| **Visualisasi Otomatis** | Chart ter-generate otomatis sesuai tipe data, tanpa konfigurasi manual |

---

## 3. Ruang Lingkup

### Dalam Scope

- Query ke Oracle 19c schema **JOINGATEOCR** (data operasional pelabuhan)
- Query ke PostgreSQL (data pendukung)
- Konversi natural language → SQL menggunakan model AI lokal (Qwen2.5-SQL Q5_K_M)
- Fallback ke cloud API (DeepSeek, Gemini) jika server lokal tidak tersedia
- Autentikasi JWT + OTP verifikasi email
- Visualisasi otomatis: bar, line, pie, scatter, pareto chart
- Export hasil query ke CSV dan Excel
- Cache query (SQLite untuk development, Redis untuk production)
- Multi-chart dashboard dengan key metrics
- API dokumentasi via Swagger UI (`/docs`)

### Luar Scope

- Modifikasi data (INSERT / UPDATE / DELETE) — sistem bersifat read-only
- Fine-tuning model LLM dari awal (menggunakan model yang sudah di-fine-tune)
- Integrasi ke sistem ERP atau billing eksternal
- Notifikasi real-time / WebSocket push

---

## 4. Bagaimana Sistem Bekerja

Alur kerja myDB Chatbot dari input pengguna hingga hasil dapat divisualisasikan sebagai berikut:

```
Pengguna mengetik pertanyaan
         │
         ▼
[1] Autentikasi & Rate Limiting
    — JWT token divalidasi
    — Request dibatasi N per menit per user
         │
         ▼
[2] Analisis Ambiguitas
    — Sistem cek apakah pertanyaan cukup spesifik
    — Jika ambigu → tampilkan opsi klarifikasi ke user
         │
         ▼
[3] Generasi SQL oleh LLM
    — Schema Oracle/PostgreSQL di-inject ke konteks LLM
    — Model Qwen2.5-SQL menghasilkan query SQL
    — SQL divalidasi (read-only guard, syntax check)
         │
         ▼
[4] Eksekusi Query ke Database
    — Query dikirim ke Oracle 19c atau PostgreSQL
    — Timeout 30 detik, baris dibatasi 100 (default)
    — Hasil di-cache untuk query serupa berikutnya
         │
         ▼
[5] Analisis & Visualisasi (Background)
    — Hasil tabel ditampilkan segera ke user
    — LLM generate insight otomatis di background
    — Chart ter-generate sesuai tipe data hasil
         │
         ▼
Output: Tabel + Chart + Insight + Tombol Export
```

Titik kritis yang menjamin keamanan ada di langkah 1 dan 3: autentikasi mencegah akses tidak sah, sementara SQL validator memastikan tidak ada operasi modifikasi data yang lolos meski pertanyaan pengguna mengandung kata-kata yang bisa diinterpretasi sebagai perintah write.

---

## 5. Model AI — Qwen2.5-SQL

### Model yang Digunakan

| Atribut | Detail |
|---------|--------|
| **Nama Model** | Qwen2.5-SQL |
| **File** | `qwen2.5-sql-q5_k_m.gguf` |
| **Ukuran** | ± 5.4 GB (kuantisasi Q5_K_M) |
| **Arsitektur Dasar** | Qwen2.5 7B (Alibaba Cloud, 2024) |
| **Spesialisasi** | Dioptimalkan untuk tugas Text-to-SQL dan pemahaman struktur database |
| **Runtime** | Ollama (local inference server) |

### Mengapa Qwen2.5-SQL?

Model ini dipilih karena tiga keunggulan utama dibanding generasi model sebelumnya:

1. **Didesain khusus untuk SQL.** Qwen2.5-SQL bukan sekadar model umum yang diberi contoh SQL — arsitekturnya dioptimalkan untuk memahami skema relasional, tipe data, dan sintaks SQL dari berbagai dialek termasuk Oracle. Akurasi query yang dihasilkan lebih tinggi pada kasus multi-JOIN dan subquery dibanding model NL2SQL generasi sebelumnya.

2. **Kuantisasi Q5_K_M — kualitas lebih tinggi, tetap bisa jalan lokal.** Kuantisasi 5-bit (Q5_K_M) mempertahankan akurasi model lebih baik dibanding Q4, dengan ukuran file ± 5.4 GB yang masih bisa dijalankan di CPU server standar dengan RAM 16 GB. Performanya setara kualitas model 8-bit dengan setengah dari biaya komputasi.

3. **Dukungan multilingual yang lebih baik.** Qwen2.5 dilatih dengan data yang jauh lebih kaya untuk bahasa-bahasa Asia, termasuk Indonesia. Artinya pertanyaan dalam Bahasa Indonesia diinterpretasikan lebih akurat dibanding model yang dominan dilatih dengan data Inggris.

### Perbandingan Performa

| Provider | Model | Kecepatan (CPU) | Kecepatan (GPU) | Biaya |
|----------|-------|-----------------|-----------------|-------|
| **Ollama (utama, lokal)** | **Qwen2.5-SQL Q5_K_M** | **20–30 detik** | **< 3 detik** | **Gratis, unlimited** |
| DeepSeek (fallback) | deepseek-chat | — | 2–5 detik | $0.14 / 1M token |
| Gemini (fallback) | gemini-1.5-flash | — | 2–4 detik | Free tier (20 req/hari) |
| OpenAI (fallback) | gpt-4o-mini | — | 3–8 detik | $0.15 / 1M token |

Model lokal menjadi prioritas utama. Sistem otomatis beralih ke fallback cloud (dikonfigurasi via `AI_FALLBACK_PROVIDERS`) jika server Ollama tidak tersedia atau timeout. Ini menjamin ketersediaan layanan tanpa ketergantungan penuh pada infrastruktur lokal.

### Roadmap Peningkatan AI

- **Fase sekarang (CPU):** Model lokal cukup untuk penggunaan internal dengan privasi penuh. Kecepatan 20–30 detik acceptable untuk query analitis yang tidak time-critical.
- **Fase GPU:** Tambah NVIDIA GPU (≥ 8 GB VRAM) → kecepatan turun ke < 3 detik, tanpa perubahan kode apapun. Ini adalah jalur upgrade paling cost-effective.
- **Fase domain adaptation:** Fine-tuning lanjutan menggunakan contoh pertanyaan dan query spesifik skema JOINGATEOCR dengan teknik LoRA. Hasilnya model yang memahami istilah bisnis Joingate secara lebih dalam, dengan biaya training yang jauh lebih hemat dibanding full fine-tuning.

### Kebutuhan Hardware

| Komponen | Minimum | Direkomendasikan |
|----------|---------|-----------------|
| RAM | 12 GB | 16 GB |
| Storage | 15 GB (model + app + cache) | 30 GB |
| CPU | 4 core x86_64 | 8 core |
| GPU | Tidak wajib | NVIDIA ≥ 8 GB VRAM (untuk < 3 detik/query) |
| OS | Ubuntu 22.04 LTS | Ubuntu 22.04 LTS |

---

## 6. Arsitektur Sistem

Sistem terdiri dari tiga layer utama yang terpisah dan berkomunikasi lewat API:

```
┌─────────────────────────────────────────┐
│           FRONTEND (Streamlit)          │
│  Login · Chat UI · Dashboard · Export   │
└──────────────────┬──────────────────────┘
                   │ HTTP / JSON
┌──────────────────▼──────────────────────┐
│           BACKEND (FastAPI)             │
│                                         │
│  Auth (JWT+OTP)  │  Chat Service        │
│  Rate Limiter    │  Query Executor       │
│  Cache Manager   │  Schema Manager      │
│  Metrics         │  Task Queue          │
└────────┬─────────┴──────────┬───────────┘
         │                    │
┌────────▼────────┐  ┌────────▼────────┐
│   AI Engine     │  │   Database      │
│                 │  │                 │
│  Ollama         │  │  Oracle 19c     │
│  Qwen2.5-SQL    │  │  PostgreSQL 15  │
│  (localhost)    │  │  (Docker)       │
└─────────────────┘  └─────────────────┘
```

Pemisahan layer ini memiliki implikasi praktis: backend bisa diganti tanpa mengubah frontend, database bisa ditambah tanpa mengubah logika AI, dan model AI bisa diupgrade tanpa mengubah backend.

---

## 7. Tech Stack

| Layer | Teknologi | Keterangan |
|-------|-----------|------------|
| **Model AI (lokal)** | Qwen2.5-SQL (Q5_K_M) via Ollama | Dioptimalkan Text-to-SQL, berjalan di CPU/GPU lokal |
| **AI Fallback** | DeepSeek / Gemini / OpenAI-compatible | Otomatis jika server lokal tidak tersedia |
| **Backend** | FastAPI + Pydantic | REST API, validasi otomatis, async support |
| **Autentikasi** | JWT + bcrypt + OTP SMTP | Token-based auth + verifikasi email |
| **Frontend** | Streamlit + Plotly | UI chat, dashboard, chart interaktif |
| **Database Utama** | Oracle 19c (Docker) | Schema JOINGATEOCR — data operasional gate |
| **Database Sekunder** | PostgreSQL 15+ (Docker) | Data pendukung |
| **Cache** | SQLite (dev) / Redis (production) | Cache query hasil dan schema |
| **Task Queue** | FastAPI BackgroundTasks (sekarang) / Celery (scale) | Proses berat dijalankan di background |
| **Monitoring** | Structured logging + `/api/metrics` | Latency, error rate, cache hit rate |
| **Deploy** | Docker + Docker Compose | Semua komponen terkontainerisasi |
| **OS** | Ubuntu 22.04 LTS | Server production |

---

## 8. Fitur Utama

### 8.1 Konversi Natural Language ke SQL

Inti dari sistem ini adalah kemampuan mengubah pertanyaan bebas menjadi query SQL yang valid. Model **Qwen2.5-SQL** menerima pertanyaan pengguna beserta konteks skema database aktif (nama tabel, kolom, tipe data, relasi), lalu menghasilkan SQL yang langsung bisa dieksekusi. Sebelum dieksekusi, SQL melewati validator yang memastikan tidak ada operasi berbahaya (DROP, DELETE, UPDATE, INSERT).

Contoh:
- Input: *"Tampilkan 10 transaksi terakhir yang pembayarannya gagal"*
- Output: `SELECT gt.id, gt.plate_number, gt.status, pi.payment_status FROM gate_transactions gt JOIN payment_infos pi ON pi.gate_transaction_id = gt.id WHERE pi.payment_status = 'FAILED' ORDER BY gt.created_at DESC FETCH FIRST 10 ROWS ONLY`

### 8.2 Visualisasi Otomatis

Setelah query dieksekusi, sistem menganalisis struktur data hasil (tipe kolom, jumlah baris, distribusi nilai) untuk menentukan jenis visualisasi yang paling tepat — bar chart untuk perbandingan kategori, line chart untuk data time-series, pie chart untuk distribusi proporsi, pareto untuk analisis 80/20. Pengguna tidak perlu mengkonfigurasi apapun; chart ter-generate otomatis.

### 8.3 Analisis Insight Otomatis

Selain menampilkan data mentah, sistem menjalankan proses analisis kedua di background: LLM membaca hasil query dan menghasilkan ringkasan insight dalam bahasa Indonesia — pola yang menonjol, anomali, atau rekomendasi tindakan. Analisis ini tidak menghalangi tampilnya data; pengguna sudah bisa melihat tabel dan chart sementara analisis diproses.

### 8.4 Cache Query

Query yang pernah dieksekusi disimpan di cache. Jika pertanyaan serupa diajukan lagi (oleh pengguna yang sama atau berbeda), hasil dikembalikan dari cache — tanpa menyentuh database dan tanpa memanggil LLM. Ini mengurangi beban database dan mempercepat respons untuk query berulang.

### 8.5 Export & Laporan

Hasil query dapat diunduh sebagai CSV atau Excel langsung dari UI. Sistem juga menyediakan fitur export riwayat percakapan (JSON/CSV/teks) dan laporan harian yang dikirim via email secara terjadwal.

---

## 9. Keamanan & Privasi Data

Sistem dibangun dengan asumsi bahwa data operasional pelabuhan adalah data sensitif yang harus dilindungi berlapis.

| Mekanisme | Implementasi | Tujuan |
|-----------|-------------|--------|
| **Autentikasi JWT** | Semua endpoint memerlukan token valid | Mencegah akses tanpa identitas |
| **OTP Email** | Registrasi wajib verifikasi kode ke email | Memastikan identitas user nyata |
| **bcrypt hashing** | Password tidak disimpan plaintext | Melindungi jika database bocor |
| **Read-only guard** | INSERT/UPDATE/DELETE/DROP/ALTER diblokir di validator | Tidak ada modifikasi data yang bisa dilakukan, disengaja maupun tidak |
| **Rate limiting** | Batas request per user per menit (default 10 req/menit) | Mencegah penyalahgunaan dan serangan brute force |
| **Query timeout** | 30 detik per eksekusi (MySQL: `max_execution_time`, Oracle: `call_timeout`) | Mencegah query berat menghabiskan resource server |
| **Row limit** | Default 100 baris per hasil query | Mencegah data dump massal |
| **AI lokal** | Model berjalan 100% di server perusahaan | Tidak ada data yang keluar ke internet |

---

## 10. Database Schema — JOINGATEOCR

Schema JOINGATEOCR menyimpan seluruh data operasional gate container Pelabuhan Joingate. Pemahaman terhadap struktur ini adalah kunci kualitas query yang dihasilkan sistem.

### Master & Konfigurasi

| Tabel | Deskripsi Bisnis |
|-------|-----------------|
| `DB_APP_SETTINGS` | Parameter konfigurasi sistem: nilai, tipe, timestamp perubahan |
| `USERS` | Pengguna sistem: ID, username, password (hash), nama lengkap, role, status aktif |

### Perangkat & Monitoring

| Tabel | Deskripsi Bisnis |
|-------|-----------------|
| `DEVICES` | Katalog perangkat fisik: nama, alamat IP, status online/offline, response time, lokasi gate |
| `DEVICEHISTORIES` | Log historis perubahan status setiap perangkat — digunakan untuk analisis keandalan hardware |

### Gate & Transaksi

| Tabel | Deskripsi Bisnis |
|-------|-----------------|
| `GATES` | Daftar gate aktif: nama, tipe (masuk/keluar), status operasional |
| `GATE_DEVICES` | Perangkat yang terpasang di setiap gate beserta confidence factor OCR-nya |
| `GATE_TRANSACTIONS` | **Tabel utama.** Setiap baris adalah satu kendaraan yang melewati gate: nomor plat, berat, status, hasil OCR, status pembayaran |
| `GATE_ACTION_TIMES` | Timeline aksi per transaksi: kapan kamera aktif, kapan barrier naik, dsb. |
| `GATE_MESSAGE_INFOS` | Pesan dan event terkait transaksi — log kejadian tidak normal |

### OCR & Analitik

| Tabel | Deskripsi Bisnis |
|-------|-----------------|
| `OCR_DATAS` | Hasil pembacaan OCR mentah per kamera: gambar, tag, axle count, nomor kontainer, kode ISO |
| `TRANSACTION_OCR_DATAS` | Penghubung antara data OCR dengan konteks transaksi gate |
| `OCR_IMAGES` | Referensi gambar yang diambil saat transaksi |
| `OCR_AUTOGATE_ACCURACY` | Metrik akurasi OCR per field — digunakan untuk laporan kinerja sistem autogate |

### Tiket & Pembayaran

| Tabel | Deskripsi Bisnis |
|-------|-----------------|
| `ETICKETS` | E-ticket container: ukuran, tipe, terminal, nama kapal, voyage number |
| `PAYMENT_INFOS` | Detail pembayaran gate: nominal, bank, saldo, status (berhasil/gagal) |

### Relasi Kunci

```
GATE_TRANSACTIONS (pusat)
  ├── GATE_ACTION_TIMES.gate_transaction_id
  ├── PAYMENT_INFOS.gate_transaction_id
  ├── OCR_IMAGES.gate_transaction_id
  └── TRANSACTION_OCR_DATAS.gate_transaction_id
         └── OCR_DATAS.id

DEVICEHISTORIES.device_id → DEVICES.id
GATE_DEVICES.gate_id      → GATES.id
```

`GATE_TRANSACTIONS` adalah tabel pusat — hampir semua query analitis bisnis akan berpusat di sini, lalu di-JOIN ke tabel lain sesuai kebutuhan.

---

## 11. Timeline Pengerjaan — 8 Minggu

Pengembangan myDB Chatbot direncanakan dalam 8 minggu, dengan urutan yang dibangun dari lapisan terbawah (infrastruktur & database) ke lapisan atas (UI & demo). Setiap minggu menghasilkan deliverable konkret yang bisa diuji sebelum minggu berikutnya dimulai.

| Minggu | Fokus | Deliverable |
|--------|-------|-------------|
| **1** | Infrastruktur & Database | Server siap, Docker Oracle 19c + PostgreSQL jalan, koneksi tervalidasi, schema JOINGATEOCR terbaca |
| **2** | Integrasi AI | Ollama + Qwen2.5-SQL Q5_K_M ter-install, NL → SQL berjalan end-to-end untuk query sederhana |
| **3** | Backend Core | FastAPI lengkap: autentikasi JWT + OTP, SQL validator, query executor dengan timeout & row limit |
| **4** | Frontend & Visualisasi | Streamlit UI: login, chat, preview SQL, tabel hasil, auto-chart (bar/line/pie/pareto), export CSV/Excel |
| **5** | Dashboard & Cache | Multi-chart dashboard, key metrics, cache query (SQLite → Redis), fallback provider (DeepSeek/Gemini) |
| **6** | Hardening Oracle | Prompt tuning untuk schema JOINGATEOCR, penanganan tipe data Oracle spesifik (NVARCHAR2, TIMESTAMP WITH TIME ZONE), pengujian query multi-JOIN |
| **7** | Kualitas & Keamanan | Rate limiting, structured logging, health & metrics endpoint, RBAC dasar (admin/analyst/viewer), uji beban |
| **8** | Finalisasi & Demo | UAT end-to-end, dry run 10 skenario demo, polish UI, freeze versi, deployment ke server demo, siapkan materi presentasi |

### Dependensi Antar Minggu

```
[M1: DB] → [M2: AI] → [M3: Backend] → [M4: Frontend]
                                              │
                              [M5: Dashboard & Cache]
                                              │
                              [M6: Oracle Hardening]
                                              │
                              [M7: Kualitas & Keamanan]
                                              │
                              [M8: Demo & Release]
```

Minggu 1–3 adalah fondasi yang tidak bisa dilewati: AI tidak bisa di-integrate sebelum database terhubung, dan frontend tidak bisa dibangun sebelum backend API siap. Jika terjadi kendala di minggu awal, buffer penyesuaian tersedia di Minggu 6–7.

### Milestone Demo (Akhir Minggu 8)

- Login, OTP, dan autentikasi berjalan tanpa error
- 10 skenario pertanyaan bahasa Indonesia dieksekusi beruntun tanpa crash
- Response time rata-rata < 30 detik (CPU) atau < 5 detik (GPU)
- Export CSV/Excel, dashboard multi-chart, dan fallback AI terkonfirmasi berjalan

---

## 12. Kriteria Sukses untuk Demo

| Kriteria | Indikator Terukur |
|----------|-----------------|
| **Login & Autentikasi** | User dapat login, OTP terkirim ke email, token valid |
| **Natural Language** | Pertanyaan bahasa Indonesia/Inggris diterima dan diproses |
| **Generate SQL** | SQL Oracle yang valid ter-generate dalam < 25 detik |
| **Eksekusi Query** | Query dieksekusi, hasil tampil sebagai tabel interaktif |
| **Visualisasi** | Chart ter-generate otomatis tanpa konfigurasi manual |
| **Multi-tabel** | Query yang melibatkan JOIN ≥ 2 tabel berhasil |
| **Export** | File CSV/Excel bisa diunduh dan isinya sesuai data |
| **Stabilitas** | 10 skenario beruntun tanpa crash atau error kritis |
| **Keamanan** | Percobaan query DELETE/DROP ditolak dengan pesan error jelas |
| **Fallback AI** | Jika Ollama offline, sistem beralih ke cloud provider otomatis |

---

## Lampiran — Tampilan Aplikasi

*(Gambar terlampir dalam versi presentasi)*

- **Gambar 1** — Halaman Login: form username/email + password + OTP
- **Gambar 2** — Tab Chat: input natural language, preview SQL sebelum eksekusi, hasil tabel
- **Gambar 3** — Multi-Chart Dashboard: key metrics, bar chart, pareto chart, pie chart dalam satu halaman
- **Gambar 4** — Tab Data Table: raw data dengan filter kolom dan tombol export CSV/Excel

---

*Dokumen ini merupakan living document. Pembaruan terakhir: 4 Juni 2026.*
