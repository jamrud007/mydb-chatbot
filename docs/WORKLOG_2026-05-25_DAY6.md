# Worklog Day 6 — 25 Mei 2026

## Tujuan
Tambahkan type hints ke modul-modul kritikal, aktifkan tooling lint+format lokal (ruff + black), dan selesaikan carry-over dari Day 5.

---

## Identifikasi Masalah / Topik Pekerjaan

**Topik:** Modul kritikal tidak punya type hints — IDE tidak bisa inferensi tipe, caller tidak tahu kontrak fungsi tanpa baca isi body.

**Masalah yang ditemukan:**

1. `database/schema_manager.py` masih pakai `cache_ttl=3600` sebagai default — carry-over dari Day 5 yang belum di-wire ke `Config.SCHEMA_CACHE_TTL`.
2. `.env.example` belum punya entry `BACKEND_URL` — inconsistent dengan `Config` yang sudah punya field ini sejak Day 5.
3. Tidak ada `pyproject.toml` — tidak ada konfigurasi ruff/black, sehingga tidak ada standar lint/format yang bisa dijalankan.
4. `ruff` dan `black` belum ada di `requirements.txt` dan belum terinstall di venv.
5. 7 modul kritikal tidak punya type hints sama sekali: `base_client.py`, `db_connection.py`, `schema_manager.py`, `query_executor.py`, `llm_factory.py`, `chatbot_handler.py`, `core/config.py`.
6. `chatbot_handler.py` mengimport `StructuredLogger`, `TimingContext`, dan `format_sql_to_nl_prompt` yang tidak dipakai — F401 warnings.

**Pertanyaan yang dijawab hari ini:**
- Module mana saja yang paling kritikal untuk di-annotate pertama?
- Pattern `None` default atau langsung `Config.X`? (jawaban: `None` + fallback di body, sama seperti Day 5 pada `OllamaClient.timeout`)
- Apakah ada unused imports yang perlu dibersihkan? (jawaban: ya, `ruff --fix` menemukan 12 issues di file-file yang disentuh)

---

## Yang Dikerjakan

### 1. Carry-over: Wire `schema_manager.py` ke `Config.SCHEMA_CACHE_TTL`

Ubah signature `SchemaManager.__init__`:

```python
# Sebelum
def __init__(self, db_connection, cache_ttl=3600):
    self.cache = TTLCache(maxsize=1, ttl=cache_ttl)

# Sesudah
def __init__(self, db_connection: Any, cache_ttl: Optional[int] = None) -> None:
    from config import Config
    effective_ttl = cache_ttl if cache_ttl is not None else Config.SCHEMA_CACHE_TTL
    self.cache: TTLCache = TTLCache(maxsize=1, ttl=effective_ttl)
```

Pola `None` dipakai untuk alasan yang sama seperti `OllamaClient.timeout` di Day 5: default parameter dievaluasi saat import, bukan saat runtime. Dengan `None`, nilai bisa di-override di test dengan patching `Config`.

### 2. Carry-over: Tambah `BACKEND_URL` ke `.env.example`

Tambahkan section baru sebelum checklist akhir:

```
# BACKEND_URL: URL where the FastAPI backend is running
BACKEND_URL=http://localhost:8000
```

### 3. Type Hints — 7 File

Konvensi yang dipakai: `from typing import Any, Dict, List, Optional, Tuple` (kompatibel Python 3.8+, konsisten dengan `user_manager.py` yang sudah pakai pattern ini).

#### `core/config.py`
- Tambah `from typing import Any, Dict`
- `validate(cls) -> bool:`
- `get_db_config(cls) -> Dict[str, Any]:`

#### `llm/base_client.py`
- Semua method abstract dan concrete mendapat return types
- `get_response(self, prompt: str, expect_json: bool = True) -> str:`
- `test_connection(self) -> bool:`
- `reset_chat(self) -> None:`
- `parse_json_response(self, response: str) -> Dict[str, Any]:`
- `_clean_json_response(self, response: str) -> str:`
- `get_provider_info(self) -> Dict[str, str]:`
- Docstrings verbose dihapus, diganti one-liner (informasi sudah ada di signature)

#### `database/db_connection.py`
- `__init__(self, db_config: Dict[str, Any], pool_size: int = 5) -> None:`
- `execute_query(self, query: str, params: Optional[Tuple] = None) -> Tuple[List[str], List[Tuple]]:`
- `test_connection(self) -> bool:`
- `get_connection(self) -> Any:`
- `close(self) -> None:`

#### `database/schema_manager.py`
- Semua method public dan private mendapat signature lengkap
- Return type `Dict[str, Any]` untuk semua `_extract_*` dan `_get_table_info_*`

#### `database/query_executor.py`
- `validate_query(self, query: str) -> Tuple[bool, Optional[str]]:`
- `execute(...) -> Dict[str, Any]:` (multi-line signature)
- `_add_limit(self, query: str) -> str:`
- `format_results_as_table(self, result: Dict[str, Any]) -> str:`

#### `llm/llm_factory.py`
- Import `BaseLLMClient` dari `llm.base_client`
- `create_client(provider: Optional[str] = None) -> BaseLLMClient:`
- `create_with_fallback() -> BaseLLMClient:`
- `get_available_providers() -> List[str]:`
- `test_provider(provider: str) -> Dict[str, Any]:`

#### `chatbot/chatbot_handler.py`
- `handle_user_message(self, user_message: str, user_id: str = 'default') -> Dict[str, Any]:`
- `execute_query_by_index(self, query_index: int, user_id: str = 'default') -> Dict[str, Any]:`
- `get_schema_info(self) -> Dict[str, Any]:`
- `refresh_schema(self) -> Dict[str, Any]:`

### 4. Setup ruff + black

Buat `pyproject.toml` di root project:

```toml
[tool.ruff]
target-version = "py310"
line-length = 120
extend-exclude = ["venv", "backups", "development", "scripts"]

[tool.ruff.lint]
select = ["E", "F", "W", "I"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["config", "core", "database", "llm", "chatbot", ...]

[tool.black]
line-length = 120
target-version = ["py310"]
```

Tambahkan ke `requirements.txt`:
```
ruff>=0.4.0
black>=24.0.0
```

Install ke venv:
```
pip install ruff>=0.4.0 "black>=24.0.0"
→ Installed: ruff-0.15.14, black-26.5.1
```

### 5. Ruff Fix + Smoke Check

Jalankan `ruff check --select F401,I001 --fix` pada 7 file yang diubah:

```
Found 12 errors (12 fixed, 0 remaining).
```

Errors yang diperbaiki:
- **F401** (unused imports): `StructuredLogger`, `TimingContext`, `format_sql_to_nl_prompt` dari `chatbot_handler.py`; `List` dari `query_executor.py` typing import
- **I001** (import ordering): 5 file lainnya — stdlib dipisah dari third-party dan local imports

Final smoke check:
```
python -m py_compile core/config.py database/db_connection.py database/schema_manager.py \
    database/query_executor.py llm/base_client.py llm/llm_factory.py chatbot/chatbot_handler.py
→ OK: semua file compile bersih
```

---

## Hasil

- **7 modul kritikal** sekarang punya type hints lengkap: IDE bisa inferensi return type, mypy/pyright bisa dijalankan, caller tahu kontrak tanpa baca body.
- **`schema_manager.py`** sekarang membaca default TTL dari `Config.SCHEMA_CACHE_TTL` — konsisten dengan pola Day 5.
- **`.env.example`** sudah sinkron dengan semua Config fields termasuk `BACKEND_URL`.
- **Tooling lint/format aktif**: `ruff` dan `black` terinstall, dikonfigurasi di `pyproject.toml`.
- **12 lint issues dibersihkan** di file-file yang disentuh (F401 + I001).

**Baseline ruff statistics sebelum Day 6 (keseluruhan codebase, diluar venv):**

| Rule | Count | Fixable |
|---|---|---|
| W293 (blank-line-whitespace) | 308 | auto |
| I001 (unsorted-imports) | 13 | auto |
| F401 (unused-import) | 9 | auto |
| F841 (unused-variable) | 3 | manual |
| W291 (trailing-whitespace) | 3 | auto |
| E722 (bare-except) | 1 | manual |
| **Total** | **337** | |

Dari 337 issues ini, **337 − 12 = 325** masih tersisa di codebase (mayoritas W293 whitespace pre-existing di file-file yang tidak disentuh hari ini).

---

## Tidak Dilakukan (Scope Batas)

- Belum jalankan `ruff --fix` pada seluruh codebase — 308 W293 (whitespace di blank lines) adalah noise pre-existing yang sebaiknya dibersihkan satu rilis khusus supaya diff tidak mengaburkan perubahan substantif.
- Belum tambahkan `mypy` atau `pyright` ke toolchain — type checking statis bisa ditambahkan setelah annotation coverage lebih tinggi.
- Belum annotate modul-modul non-critical: `utils/`, `api/`, `services/`, `cache/`.

## Next

- Day 7: Audit dan tambahkan type hints ke `utils/` dan `api/` modul; atau jalankan `ruff --fix` full pass untuk bersihkan W293 di seluruh codebase (satu commit khusus "whitespace cleanup").

---

## Penjelasan (Kenapa Day 6 Penting)

**Masalah sebelumnya:**
IDE hanya menampilkan `-> None` atau tidak ada informasi tipe untuk method-method kritikal. Saat `chatbot_handler.execute_query_by_index()` dipanggil dari `api/`, editor tidak bisa suggest bahwa argumen pertama harus `int` dan return value punya key `'rows'`.

**Yang diselesaikan:**
```
Sebelum:
def execute_query_by_index(self, query_index, user_id='default'):
    # IDE tidak tahu query_index harus int
    # Return type tidak diketahui

Sesudah:
def execute_query_by_index(self, query_index: int, user_id: str = 'default') -> Dict[str, Any]:
    # IDE bisa warn jika caller kirim string
    # Caller tahu return adalah dict
```

**Kenapa `from typing import ...` bukan built-in `dict[...]`?**
Python 3.9+ mendukung `dict[str, Any]` langsung tanpa import. Tapi project ini pakai `from typing import Dict, List` di `user_manager.py` (file yang paling mature, sudah production-grade). Konsistensi dengan konvensi yang sudah ada lebih penting dari modernisasi incremental yang akan membuat mixed styles.
