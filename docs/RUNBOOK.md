# MyDB Chatbot — Runbook Operasional

Panduan cepat untuk mendiagnosis dan memitigasi incident umum.  
Dibuat: 22 Juni 2026 (Day 20 — Architecture Restructure)

---

## 1. Quick Status Check

Selalu mulai dari dua endpoint ini sebelum melakukan tindakan apapun.

```bash
# Apakah komponen utama hidup?
curl http://localhost:5000/api/health

# Apakah sistem sehat secara performa?
curl http://localhost:5000/api/metrics/summary
```

**Interpretasi `/api/health`**

| `status` | `database` | `llm` | Artinya |
|---|---|---|---|
| `healthy` | `connected` | `connected` | Normal |
| `unhealthy` | `disconnected` | `connected` | DB down → lihat [Playbook 2] |
| `unhealthy` | `connected` | `disconnected` | LLM down → lihat [Playbook 3] |
| `unhealthy` | `disconnected` | `disconnected` | Startup gagal → lihat [Playbook 1] |

**Interpretasi `/api/metrics/summary`**

| `status` | Kondisi | Tindakan |
|---|---|---|
| `ok` | Normal | — |
| `degraded` | Error rate ≥5% atau LLM success rate <90% | Monitor, periksa `top_errors` |
| `critical` | Error rate ≥20% | Eskalasi segera, lihat playbook sesuai `top_errors` |

---

## 2. Playbook: Service Down (503 Everywhere)

**Gejala:** Semua endpoint non-health mengembalikan `503 Service Unavailable` dengan pesan `"Chatbot not initialized"`.

**Penyebab umum:** DB unreachable saat startup, env var hilang, atau crash saat init.

### Langkah Diagnosis

```bash
# 1. Cek log startup
tail -100 logs/chatbot.log | grep -E "(ERROR|CRITICAL|Failed|❌)"

# 2. Cek apakah proses masih jalan
# Windows:
netstat -ano | findstr :5000
# Linux:
ss -tlnp | grep 5000
```

### Langkah Mitigasi

**A. DB unreachable (paling umum)**

```bash
# Cek koneksi ke DB
# MySQL:
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -e "SELECT 1;"
# Oracle:
python -c "import oracledb; oracledb.connect(dsn='$DB_DSN', user='$DB_USER', password='$DB_PASSWORD')"
```

Jika DB memang down: tunggu DB pulih, lalu restart app.  
Jika DB up tapi tidak bisa connect: cek `DB_HOST`, `DB_PORT`, firewall, VPN.

**B. Env var hilang**

```bash
# Cek env var kritis tersedia
python -c "from core.config import Config; Config.validate()"
```

Error akan muncul jika ada yang kurang (e.g. `DB_PASSWORD`, `OPENAI_API_KEY`).

**C. Restart aplikasi**

```bash
# Restart uvicorn
uvicorn main:app --host 0.0.0.0 --port 5000 --reload

# Atau jika pakai Docker:
docker compose restart api
```

**D. Verifikasi setelah restart**

```bash
curl http://localhost:5000/api/health
# Harus: {"status": "healthy", "database": "connected", "llm": "connected"}
```

---

## 3. Playbook: LLM Quota Habis / Provider Error

**Gejala:** `/api/chat` berhasil menerima request tapi balasannya error, atau LLM `success_rate_percent` di `/api/metrics/summary` turun tajam. Log akan menunjukkan `429 Too Many Requests` atau `quota exceeded` dari provider.

**Env var relevan:** `AI_PROVIDER`, `AI_FALLBACK_PROVIDERS`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_BASE_URL`

### Langkah Diagnosis

```bash
# Cek LLM stats
curl http://localhost:5000/api/metrics | python -m json.tool | grep -A 5 '"llm"'

# Cek log error LLM
grep -i "quota\|rate.limit\|429\|llm.*error\|provider.*fail" logs/chatbot.log | tail -20
```

### Langkah Mitigasi

**A. Switch ke fallback provider (tanpa restart)**

Edit `.env` — tambah atau ubah:

```env
# Provider utama gagal, switch ke fallback
AI_PROVIDER=deepseek
AI_FALLBACK_PROVIDERS=ollama

# Atau gunakan Ollama lokal sebagai darurat (tanpa quota):
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1
```

Kemudian restart app (env tidak di-hot-reload):

```bash
uvicorn main:app --host 0.0.0.0 --port 5000
```

**B. Verifikasi Ollama tersedia (fallback lokal)**

```bash
curl http://localhost:11434/api/tags
# Harus tampil list model yang terinstal
```

**C. Cek sisa quota (OpenAI)**

Login ke [platform.openai.com](https://platform.openai.com) → Usage → Billing.  
Untuk DeepSeek: [platform.deepseek.com](https://platform.deepseek.com).

**D. Top-up atau ganti API key**

```env
OPENAI_API_KEY=sk-xxxx-new-key
```

Restart app setelah update `.env`.

**E. Sementara matikan data analysis (kurangi LLM call)**

```env
ENABLE_DATA_ANALYSIS=False
```

Efek: `POST /api/execute/{idx}` tidak lagi trigger background LLM analysis. Query tetap jalan, cuma summary otomatis tidak muncul.

---

## 4. Playbook: Database Unreachable

**Gejala:** `/api/health` menunjukkan `"database": "disconnected"`, query gagal dengan error koneksi.

**Env var relevan:** `DB_ENGINE`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` (MySQL) / `DB_DSN`, `DB_SERVICE_NAME` (Oracle)

### Langkah Diagnosis

```bash
# Cek log koneksi DB
grep -i "database\|connection\|oracle\|mysql\|timeout" logs/chatbot.log | tail -20

# Test koneksi langsung (MySQL)
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p -e "SHOW DATABASES;"

# Test koneksi langsung (Oracle)
python scripts/check_oracle_users.py
```

### Langkah Mitigasi

**A. DB server down**
- Hubungi DBA atau restart DB service.
- Jika Oracle di `192.168.100.81` tidak reachable dari dev: switch sementara ke MySQL lokal.

```env
# Switch ke MySQL lokal (dev only)
DB_ENGINE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=ecommerce_olist
```

**B. Network / VPN**
- Pastikan terhubung ke jaringan yang sama dengan DB server (VPN jika diperlukan).
- Cek firewall: port `3306` (MySQL) atau `1521` (Oracle) harus terbuka dari server app.

**C. Kredensial salah / expired**
- Reset password via `scripts/reset_password.py` atau minta DBA.
- Update `.env` lalu restart app.

**D. Timeout terlalu pendek**
Jika koneksi Oracle lambat tapi berhasil, naikkan timeout query:

```env
QUERY_TIMEOUT_SECONDS=60
```

---

## 5. Playbook: High Error Rate / Status Degraded

**Gejala:** `/api/metrics/summary` menunjukkan `status: degraded` atau `critical`. Field `top_errors` berisi error type yang dominan.

### Langkah Diagnosis

```bash
# Lihat breakdown error
curl http://localhost:5000/api/metrics/summary | python -m json.tool

# Cari error tersebut di log
grep -i "SQL_EXECUTION_ERROR\|RATE_LIMIT\|<error_type>" logs/chatbot.log | tail -30
```

### Tindakan per error type umum

| Error type | Kemungkinan penyebab | Mitigasi |
|---|---|---|
| `SQL_EXECUTION_ERROR` | Query tidak valid / tabel tidak ada | Cek schema, update `SCHEMA_CACHE_TTL`, restart agar schema di-refresh |
| `RATE_LIMIT_EXCEEDED` | User spam request | Turunkan `MAX_REQUESTS_PER_MINUTE` atau block user |
| `LLM_TIMEOUT` | Provider lambat | Naikkan `LLM_TIMEOUT`, atau switch provider |
| `DB_CONNECTION_ERROR` | DB intermittent | Lihat [Playbook 4] |
| `QUERY_TIMEOUT` | Query terlalu berat | Naikkan `QUERY_TIMEOUT_SECONDS`, atau tambah index di DB |

---

## 6. Playbook: Slow Queries

**Gejala:** `p95_duration_ms` di `/api/metrics/summary` tinggi (>5000ms), atau `slow_query_count` >0.

```bash
# Lihat 10 slow query terakhir
curl http://localhost:5000/api/metrics | python -m json.tool | grep -A 20 '"slow_queries"'
```

### Langkah Mitigasi

1. **Identifikasi query** — lihat field `query` di `slow_queries`, jalankan manual di DB client dengan `EXPLAIN`.
2. **Cache hit rate rendah** — jika `cache.hit_rate_percent` <30%, cek apakah cache aktif: `curl http://localhost:5000/api/cache/stats`.
3. **Aktifkan/reset cache**:
   ```bash
   # Reset cache jika korup
   curl -X DELETE http://localhost:5000/api/cache/clear
   ```
4. **Naikkan `MAX_QUERY_ROWS`** — jika user perlu lebih banyak baris dan mau trade-off kecepatan:
   ```env
   MAX_QUERY_ROWS=500
   ```
5. **Naikan `QUERY_TIMEOUT_SECONDS`** — jika query valid tapi lambat karena data besar:
   ```env
   QUERY_TIMEOUT_SECONDS=60
   ```

---

## 7. Quick Reference

### File & Lokasi

| Item | Path |
|---|---|
| Log aplikasi | `logs/chatbot.log` |
| Konfigurasi | `.env` (project root) |
| Cache SQLite | `data/cache.db` (default, lihat `CACHE_SQLITE_PATH`) |

### Perintah Penting

```bash
# Start aplikasi
uvicorn main:app --host 0.0.0.0 --port 5000

# Start dengan reload (dev)
uvicorn main:app --host 0.0.0.0 --port 5000 --reload

# Start via Docker
docker compose up -d

# Lihat log real-time
tail -f logs/chatbot.log

# Cek health
curl http://localhost:5000/api/health

# Cek metrics summary
curl http://localhost:5000/api/metrics/summary

# Clear cache (semua)
curl -X DELETE http://localhost:5000/api/cache/clear

# Clear cache user tertentu
curl -X DELETE "http://localhost:5000/api/cache/clear?user_id=123"
```

### Env Var Kritis

| Var | Default | Keterangan |
|---|---|---|
| `DB_ENGINE` | `mysql` | `mysql` atau `oracle` |
| `DB_HOST` | `localhost` | Hostname DB |
| `DB_PASSWORD` | — | **Wajib** |
| `AI_PROVIDER` | `ollama` | Provider LLM aktif |
| `AI_FALLBACK_PROVIDERS` | — | Comma-separated, e.g. `deepseek,ollama` |
| `ENABLE_DATA_ANALYSIS` | `True` | Matikan jika LLM quota kritis |
| `LLM_TIMEOUT` | `600` | Timeout LLM dalam detik |
| `QUERY_TIMEOUT_SECONDS` | `30` | Timeout query DB |
| `MAX_REQUESTS_PER_MINUTE` | `10` | Rate limit per user |

### Eskalasi

Jika runbook ini tidak menyelesaikan masalah:
1. Ambil dump log: `cp logs/chatbot.log /tmp/incident-$(date +%Y%m%d-%H%M).log`
2. Catat output `/api/health` dan `/api/metrics/summary` saat incident.
3. Laporkan ke tim dengan kedua output tersebut + baris error terakhir dari log.
