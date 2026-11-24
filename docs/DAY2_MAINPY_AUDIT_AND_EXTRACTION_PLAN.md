# Day 2 Audit - main.py Extraction Plan

Tanggal: 13 May 2026  
Checklist Target:
- Audit `main.py` dan tandai blok logic yang harus dipindah.
- Buat service skeleton awal (`services/`).

## 1) Temuan Utama `main.py`

`main.py` saat ini menggabungkan beberapa concern sekaligus:
- App bootstrap + dependency wiring
- Endpoint handlers
- Business logic orchestration (chat/execute/export/cache flow)
- Auth dependency setup
- Health/metrics/admin endpoints

Dampak:
- File besar dan sulit diuji per concern.
- Sulit melakukan perubahan kecil tanpa risiko regresi lintas endpoint.

## 2) Kandidat Ekstraksi (Prioritas)

### A. Bootstrap / Composition Root
- Blok inisialisasi komponen global (`chatbot`, `rate_limiter`, `results_cache`, `metrics_collector`, `user_manager`)
- Target baru: `services/app_services.py` (builder + container dependencies)

### B. Chat & Execution Flow
- Endpoint `/api/chat` dan `/api/execute/{query_index}`
- Target baru: `services/chat_service.py`

### C. Export & History
- Endpoint history export (`json/csv/text/stats`) dan CSV export query
- Target service berikutnya: `services/history_service.py`, `services/export_service.py` (Day 3+)

### D. Cache Operations
- Endpoint cache stats/list/get/clear
- Target service berikutnya: `services/cache_service.py` (Day 3+)

### E. Schema Docs & Suggestions
- Endpoint schema docs dan query suggestion
- Target service berikutnya: `services/schema_service.py`, `services/suggestion_service.py` (Day 3+)

## 3) Skeleton yang Sudah Dibuat (Day 2)

- `services/__init__.py`
- `services/chat_service.py`
- `services/app_services.py`

Catatan:
- Skeleton ini belum mengubah runtime behavior `main.py`.
- Fokus Day 2 adalah menyiapkan boundary layer aman untuk migrasi Day 3.

## 4) Rencana Day 3

1. Integrasikan `ChatService` ke endpoint `/api/chat` tanpa ubah response contract.
2. Integrasikan `ChatService` ke endpoint `/api/execute/{query_index}`.
3. Jalankan smoke test endpoint chat & execute.

