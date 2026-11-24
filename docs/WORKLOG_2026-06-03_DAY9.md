# Worklog Day 9 — 3 Juni 2026

## Tujuan
Implement queue interface minimal dan pisahkan task berat dari request path.

---

## Identifikasi Masalah / Topik Pekerjaan

**Topik:** Berdasarkan analisis Day 8, proses paling impactful untuk di-defer adalah:
1. **Auto-analysis insight** di `/api/execute/` — LLM call 10-60s, blokir user padahal data DB sudah tersedia.
2. **Daily report** di `/api/admin/daily-report` — file I/O sync yang tidak perlu blokir admin.

**Target hari ini:**
- Buat abstraksi `TaskQueue` yang bisa di-swap ke Celery/RQ nanti.
- Pindahkan auto-analysis ke background task.
- Tambah polling endpoint sehingga client bisa ambil analysis saat sudah siap.
- Pindahkan daily report ke background task.

---

## Yang Dikerjakan

### 1. Buat `queue/` package — abstraksi task queue

**`queue/task_queue.py`** — abstract base class:
```python
class TaskQueue(ABC):
    @abstractmethod
    def enqueue(self, task_fn, *args, **kwargs) -> None: ...
```

**`queue/background_task_queue.py`** — FastAPI BackgroundTasks implementation:
```python
class BackgroundTaskQueue(TaskQueue):
    def __init__(self, background_tasks: BackgroundTasks):
        self._bg = background_tasks
    def enqueue(self, task_fn, *args, **kwargs) -> None:
        self._bg.add_task(task_fn, *args, **kwargs)
```

Dengan pola ini, jika nanti kita ganti ke Celery/Redis, cukup buat `CeleryTaskQueue(TaskQueue)` — caller di `main.py` tidak perlu diubah.

### 2. Update `utils/results_cache.py`

- Tambah field `analysis_status` ke setiap entry: `'pending' | 'ready' | 'failed' | 'disabled'`
- Tambah method `update_analysis(result_id, analysis_text, status)` — dipanggil oleh background task saat analysis selesai, update `nl_summary` dan ubah status ke `'ready'`.

### 3. Update `chatbot/chatbot_handler.py`

- **Hapus** blok auto-analysis dari `execute_query_by_index()` — method ini sekarang hanya mengeksekusi DB query dan return hasilnya (fast path).
- **Tambah** method `generate_analysis(cache_query, question, columns, rows)` — LLM call + update `cache_manager`. Dirancang untuk dipanggil sebagai background task.

### 4. Update `models/api_models.py`

Tambah field `analysis_status: str = 'ready'` ke `ExecuteResponse`.

### 5. Update `main.py` — execute endpoint

```
Sebelum:
POST /api/execute/{i}
  → execute DB query (~2s)
  → run LLM analysis (~60s)
  → return                      ← user tunggu ~62s

Sesudah:
POST /api/execute/{i}
  → execute DB query (~2s)
  → store result (analysis_status='pending')
  → fire analysis as BackgroundTask
  → return SEGERA               ← user tunggu ~2s
```

Endpoint sekarang:
- Terima `BackgroundTasks` parameter dari FastAPI
- Wrap dengan `BackgroundTaskQueue(background_tasks)`
- Enqueue `_background_analysis(handler, cache_query, question, columns, rows, result_id)`
- Return `ExecuteResponse` dengan `analysis_status='pending'`

### 6. Tambah `GET /api/results/{result_id}/analysis` — polling endpoint

Client memanggil endpoint ini setelah menerima `analysis_status='pending'`:
```json
{
  "result_id": "abc12345",
  "analysis_status": "ready",
  "analysis": "Dari data di atas terlihat bahwa..."
}
```
Jika masih pending, `analysis_status='pending'` dan `analysis=''`.

### 7. Update `/api/admin/daily-report` — return 202

```
Sebelum: POST → generate file sync → return 200 (blokir 1-5s)
Sesudah: POST → fire BackgroundTask → return 202 Accepted (instan)
```

### 8. Smoke check

```
py_compile queue/task_queue.py queue/background_task_queue.py
py_compile utils/results_cache.py models/api_models.py
py_compile chatbot/chatbot_handler.py main.py
→ Semua OK
```

---

## Hasil

| Endpoint | Sebelum | Sesudah |
|---|---|---|
| `POST /api/execute/{i}` | ~62s (DB + LLM analysis) | ~2s (DB only, analysis di background) |
| `POST /api/admin/daily-report` | Blokir 1-5s | Return 202 instan |
| `GET /api/results/{id}/analysis` | (tidak ada) | Polling endpoint baru |

- Tidak ada infra baru yang dibutuhkan — FastAPI `BackgroundTasks` sudah built-in.
- Abstraksi `TaskQueue` memungkinkan swap ke Celery/RQ tanpa ubah `main.py`.

---

## Tidak Dilakukan (Scope Batas)

- Belum implementasi streaming untuk `/api/chat` LLM calls (chat masih sinkron) — ini scope Day 10.
- Belum ada notifikasi push saat analysis selesai — client harus poll aktif. WebSocket/SSE bisa ditambah nanti.
- Belum update Streamlit frontend untuk memanfaatkan `analysis_status` — Streamlit masih tampilkan nl_summary as-is.

---

## Next

- **Day 10:** Timeout + retry policy untuk LLM provider. Tambah fallback provider logic.

---

## Penjelasan (Kenapa Ini Penting)

**Masalah sebelumnya:**
User mengirim query, server sudah punya data dari database dalam 2 detik, tapi response tidak dikirim sampai LLM selesai generate analysis (60 detik). User melihat loading spinner 60 detik meski data sudah ada.

**Sesudah:**
Response dikirim dalam 2 detik. Analysis datang belakangan via polling. User bisa langsung lihat dan interaksi dengan data sambil analysis diproses di background.

**Kenapa `TaskQueue` abstraction penting?**
FastAPI `BackgroundTasks` hanya berjalan dalam satu process — cocok untuk sekarang (single server). Kalau nanti kita scale horizontal (multiple workers), background task dari Worker A tidak akan tereksekusi di Worker B. Dengan abstraksi `TaskQueue`, kita tinggal ganti `BackgroundTaskQueue` dengan `CeleryTaskQueue` tanpa mengubah kode endpoint sama sekali.
