# BOOTSTRAP (Updated 16 May 2026)

Dokumen ini untuk memulai sesi kerja baru dengan cepat.

## 1) Read First (urut)
1. `HANDOFF.md`
2. `docs/PROJECT_REFERENCE_SUMMARY.md`
3. `docs/TASKLIST_30_DAYS_ARCHITECTURE_RESTRUCTURE.md`
4. `docs/DAY2_MAINPY_AUDIT_AND_EXTRACTION_PLAN.md`

## 2) Current Architecture Direction
- Target: `api` -> `services` -> `repositories` -> `core`
- Sudah berjalan:
  - `core/` (config/logging)
  - `services/chat_service.py` untuk flow chat & execute

## 3) Baseline Runtime Commands
- Backend: `python main.py`
- Frontend: `streamlit run streamlit_app.py`
- Basic compile smoke check:
  - `python -m py_compile main.py services\chat_service.py services\app_services.py`

## 4) Active Next Step
Eksekusi Day 4 dari tasklist:
- Mulai repository extraction pilot dari `database/query_executor.py`
- Pastikan backward compatibility tetap aman
- Commit kecil per area + docs/worklog update

## 5) Commit Discipline
- Karena banyak perubahan non-scope di working tree, selalu:
  - `git status`
  - `git add <file-spesifik>`
  - commit/push per task kecil
