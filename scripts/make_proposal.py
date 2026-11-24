"""
Generate Oracle SQL Chatbot - Project Proposal (.docx)
Combines: Oracle_SQL_Chatbot_Documentation.docx + converted-document.docx
+ 8-week timeline, screenshots in UI/Mockup section
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os, copy

BASE    = os.path.join(os.path.dirname(__file__), '..')
OUTPUT  = os.path.join(BASE, 'docs', 'Proposal_Oracle_SQL_Chatbot_v3.docx')

# ── colour palette ────────────────────────────────────────────────
PRIMARY = '1F4E79'
ACCENT  = '2E75B6'
LIGHT   = 'DEEAF1'
GREEN   = '375623'
ORANGE  = 'C55A11'
WHITE   = 'FFFFFF'
GRAY    = '595959'

def _rgb(h):
    return RGBColor(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def set_cell_bg(cell, hex6):
    tcPr = cell._tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex6)
    tcPr.append(shd)

def shade_para(p, hex6):
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex6)
    pPr.append(shd)

def h(doc, text, level=1, color=PRIMARY):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.color.rgb = _rgb(color)
    return p

def body(doc, text, size=11):
    p = doc.add_paragraph(text)
    for run in p.runs:
        run.font.size = Pt(size)
    return p

def bullet(doc, text, bold_prefix=''):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        r = p.add_run(bold_prefix + ' '); r.bold = True; r.font.size = Pt(11)
    p.add_run(text).font.size = Pt(11)

def table(doc, headers, rows, hbg=PRIMARY, alt=LIGHT):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    for i, hdr in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = hdr
        set_cell_bg(c, hbg)
        r = c.paragraphs[0].runs[0]
        r.bold = True; r.font.color.rgb = _rgb(WHITE); r.font.size = Pt(10)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for ri, row in enumerate(rows):
        tr = t.add_row()
        if ri % 2 == 1:
            for c in tr.cells: set_cell_bg(c, alt)
        for i, val in enumerate(row):
            tr.cells[i].text = str(val)
            for r in tr.cells[i].paragraphs[0].runs:
                r.font.size = Pt(10)
    doc.add_paragraph()

def screenshot(doc, rel_path, caption, width=Inches(5.8)):
    full = os.path.join(BASE, rel_path)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(full):
        p.add_run().add_picture(full, width=width)
    else:
        r = p.add_run(f'[ Screenshot: {os.path.basename(rel_path)} ]')
        r.font.italic = True; r.font.color.rgb = _rgb('AAAAAA'); r.font.size = Pt(10)
    cap = doc.add_paragraph(caption)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in cap.runs:
        r.font.size = Pt(9); r.font.italic = True; r.font.color.rgb = _rgb(GRAY)
    doc.add_paragraph()

def divider(doc, char='─', n=80, color='CCCCCC'):
    p = doc.add_paragraph(char * n)
    for r in p.runs:
        r.font.size = Pt(8); r.font.color.rgb = _rgb(color)

def week_header(doc, week, theme, color):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run(f'  {week}  —  {theme}  ')
    r.bold = True; r.font.size = Pt(12); r.font.color.rgb = _rgb(WHITE)
    shade_para(p, color)

def merge_docx_body(doc, src_path):
    """Copy all paragraphs and tables from src into doc (best-effort)."""
    if not os.path.exists(src_path):
        doc.add_paragraph(f'[File not found: {src_path}]')
        return
    src = Document(src_path)
    for blk in src.element.body:
        new_blk = copy.deepcopy(blk)
        doc.element.body.append(new_blk)

# ════════════════════════════════════════════════════════════════
def main():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
    sec.left_margin = Cm(3.0); sec.right_margin = Cm(2.5)

    # ── COVER ──────────────────────────────────────────────────
    for _ in range(3): doc.add_paragraph()

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('PROPOSAL PROYEK')
    r.bold = True; r.font.size = Pt(13); r.font.color.rgb = _rgb(ACCENT)

    doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Oracle SQL Chatbot')
    r.bold = True; r.font.size = Pt(34); r.font.color.rgb = _rgb(PRIMARY)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Sistem Tanya-Jawab Database Berbasis Natural Language')
    r.font.size = Pt(14); r.font.color.rgb = _rgb(ACCENT)

    doc.add_paragraph(); divider(doc)

    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(
        'Database Target  :  Oracle 19c — Schema JOINGATEOCR\n'
        'Multi-Database   :  PostgreSQL (Minggu 6–7)\n'
        'Backend          :  FastAPI + Python 3.11\n'
        'Frontend         :  Streamlit + Plotly\n'
        'LLM Provider     :  Ollama / Google Gemini / OpenAI-compatible\n'
        'Timeline         :  8 Minggu\n'
        'Tanggal          :  Juni 2026'
    )
    r.font.size = Pt(11); r.font.name = 'Courier New'
    divider(doc)
    doc.add_page_break()

    # ── 1. LATAR BELAKANG ──────────────────────────────────────
    h(doc, '1.  Latar Belakang')
    body(doc,
        'Sistem operasional gate container di Pelabuhan Joingate menghasilkan data transaksi '
        'besar setiap harinya — mulai dari data OCR kendaraan, pembayaran, hingga histori '
        'perangkat monitoring. Selama ini, pengambilan insight dari data tersebut memerlukan '
        'penulisan query SQL secara manual oleh tim teknis.')
    doc.add_paragraph()
    body(doc,
        'Oracle SQL Chatbot memungkinkan pengguna mengajukan pertanyaan dalam bahasa natural '
        '(Indonesia maupun Inggris), yang secara otomatis dikonversi menjadi query SQL Oracle '
        'yang valid, dieksekusi, dan hasilnya ditampilkan sebagai tabel, grafik interaktif, '
        'serta dapat diekspor ke CSV/Excel.')
    doc.add_paragraph()

    # ── 2. TUJUAN ──────────────────────────────────────────────
    h(doc, '2.  Tujuan Proyek')
    table(doc, ['Tujuan', 'Deskripsi'], [
        ('Aksesibilitas Data',    'Pengguna non-teknis dapat mengakses data Oracle/PostgreSQL tanpa menulis SQL'),
        ('Kecepatan Insight',     'Pertanyaan bisnis terjawab dalam hitungan detik'),
        ('Keamanan Data',         'Akses dibatasi read-only dengan autentikasi JWT + OTP'),
        ('Visualisasi Otomatis',  'Chart ter-generate otomatis sesuai tipe data'),
        ('Multi-Database',        'Platform mendukung Oracle 19c dan PostgreSQL dalam satu antarmuka'),
    ])

    # ── 3. RUANG LINGKUP ───────────────────────────────────────
    h(doc, '3.  Ruang Lingkup')
    h(doc, 'Dalam Scope', level=2, color=GREEN)
    for s in [
        'Query ke Oracle 19c schema JOINGATEOCR',
        'Query ke PostgreSQL (ditambahkan minggu 6–7)',
        'Natural language → SQL via LLM (Ollama, Gemini, OpenAI-compatible)',
        'JWT Authentication + OTP verifikasi email',
        'Auto-visualization: bar, line, pie, scatter, pareto chart',
        'Export CSV dan Excel',
        'Cache query (SQLite / Redis)',
        'Multi-chart dashboard',
        'API docs via Swagger UI (/docs)',
    ]: bullet(doc, s)
    doc.add_paragraph()

    h(doc, 'Luar Scope', level=2, color=ORANGE)
    for s in [
        'Modifikasi data (INSERT/UPDATE/DELETE) — hanya read-only',
        'Fine-tuning model LLM dari awal',
        'Integrasi ke sistem ERP atau billing eksternal',
    ]: bullet(doc, s)
    doc.add_paragraph()

    # ── 4. TECH STACK ──────────────────────────────────────────
    h(doc, '4.  Tech Stack')
    table(doc, ['Layer', 'Teknologi'], [
        ('LLM Engine',   'Ollama (lokal), Google Gemini, OpenAI-compatible API'),
        ('Backend',      'FastAPI, Pydantic, JWT Auth, python-oracledb, psycopg2'),
        ('Frontend',     'Streamlit, Plotly (chart interaktif)'),
        ('Database',     'Oracle 19c (Docker), PostgreSQL 15+ (Docker)'),
        ('Cache',        'SQLite (dev) / Redis (production)'),
        ('Auth',         'JWT + bcrypt + OTP SMTP Gmail'),
        ('Deploy',       'Docker + Docker Compose, Ubuntu 22.04 LTS'),
        ('Monitoring',   '/api/health, /api/metrics, structured logging'),
    ])

    # ── 5. ARSITEKTUR ──────────────────────────────────────────
    h(doc, '5.  Arsitektur Sistem')
    screenshot(doc, 'docs/diagram_arsitektur.png',
               'Diagram 1 — Arsitektur Sistem Oracle SQL Chatbot', width=Inches(5.5))

    doc.add_paragraph()

    # ── 6. TAMPILAN APLIKASI (SCREENSHOTS) ────────────────────
    h(doc, '6.  Tampilan Aplikasi')
    body(doc, 'Berikut tampilan aktual Oracle SQL Chatbot yang sudah berjalan di lingkungan development:')
    doc.add_paragraph()

    screenshot(doc, 'docs/screenshot_login.png',
               'Gambar 1 — Halaman Login: autentikasi dengan username/email dan kata sandi')
    screenshot(doc, 'docs/screenshot_chat.png',
               'Gambar 2 — Tab Chat: input natural language, preview SQL, eksekusi query ke Oracle')
    screenshot(doc, 'docs/screenshot_dashboard.png',
               'Gambar 3 — Multi-Chart Dashboard: key metrics, bar chart, pareto chart, pie chart')
    screenshot(doc, 'docs/screenshot_datatable.png',
               'Gambar 4 — Tab Data Table: raw data dengan filter kolom dan export CSV/Excel')

    # ── 7. FITUR BACKEND ──────────────────────────────────────
    h(doc, '7.  Fitur Backend (FastAPI — port 8000)')

    h(doc, 'Auth  /api/auth/...', level=2, color=ACCENT)
    table(doc, ['Endpoint', 'Method', 'Fungsi'], [
        ('/api/auth/register',     'POST',  'Daftar user baru, kirim OTP verifikasi ke email'),
        ('/api/auth/login',        'POST',  'Login → return JWT token'),
        ('/api/auth/verify-otp',   'POST',  'Verifikasi kode OTP dari email'),
        ('/api/auth/me',           'GET',   'Info user yang sedang login'),
        ('/api/auth/refresh',      'POST',  'Perpanjang masa berlaku JWT token'),
        ('/api/auth/verify-token', 'POST',  'Cek apakah token masih valid'),
    ])

    h(doc, 'Chat & Query', level=2, color=ACCENT)
    table(doc, ['Endpoint', 'Method', 'Fungsi'], [
        ('/api/chat',                  'POST', 'Natural language → SQL → eksekusi Oracle/PG → return hasil'),
        ('/api/execute/{query_index}', 'POST', 'Eksekusi ulang SQL dari index tertentu'),
        ('/api/suggestions',           'GET',  'Saran pertanyaan otomatis berdasarkan schema aktif'),
    ])

    h(doc, 'Hasil & Export', level=2, color=ACCENT)
    table(doc, ['Endpoint', 'Method', 'Fungsi'], [
        ('/api/results',                    'GET',    'List semua hasil query yang di-cache'),
        ('/api/results/{id}',               'GET',    'Detail hasil query spesifik'),
        ('/api/results/{id}/analysis',      'GET',    'Analisis otomatis hasil query'),
        ('/api/export/csv/{query_index}',   'GET',    'Export hasil ke CSV'),
        ('/api/history/export/json|csv|text','GET',   'Export riwayat percakapan'),
    ])

    h(doc, 'Monitoring & Cache', level=2, color=ACCENT)
    table(doc, ['Endpoint', 'Method', 'Fungsi'], [
        ('/api/health',            'GET',    'Status DB, LLM, cache'),
        ('/api/metrics',           'GET',    'Statistik request count, latency, error rate'),
        ('/api/cache/stats',       'GET',    'Info cache: jumlah entry, ukuran, backend'),
        ('/api/cache/clear',       'DELETE', 'Hapus semua cache query'),
        ('/api/admin/daily-report','POST',   'Trigger laporan harian via email'),
    ])

    # ── 8. FITUR FRONTEND ─────────────────────────────────────
    h(doc, '8.  Fitur Frontend (Streamlit — port 8501)')

    h(doc, 'Sidebar', level=2, color=ACCENT)
    table(doc, ['Komponen', 'Fungsi'], [
        ('Info user',     'Username, email, tombol Logout'),
        ('Recent Queries','Riwayat query dari cache — klik untuk load ulang'),
        ('API Status',    '✅ Connected / ⚠️ Degraded / ❌ Offline'),
        ('DB & LLM',      'Status koneksi Oracle/PostgreSQL dan provider LLM'),
        ('Query Cache',   'Ukuran (MB), backend, tombol Clear Cache'),
    ])

    h(doc, 'Tab Chat', level=2, color=ACCENT)
    table(doc, ['Fitur', 'Deskripsi'], [
        ('Input natural language',  'Pertanyaan bahasa Indonesia/Inggris'),
        ('Clarification handler',   'Sistem minta klarifikasi jika pertanyaan ambigu'),
        ('Preview SQL',             'SQL yang di-generate LLM ditampilkan sebelum dieksekusi'),
        ('Hasil tabel',             'Data ditampilkan sebagai tabel interaktif'),
        ('Auto-visualization',      'Chart otomatis: bar, line, pie, scatter, pareto'),
        ('Feedback',                'Rating bintang + komentar per hasil query'),
        ('Export',                  'Download CSV dan Excel langsung dari UI'),
    ])

    h(doc, 'Tab Dashboard & Data Table', level=2, color=ACCENT)
    table(doc, ['Tab', 'Deskripsi'], [
        ('Single Chart',  'Konfigurasi manual jenis chart dan sumbu X/Y'),
        ('Dashboard',     'Multi-chart otomatis dalam satu halaman + key metrics'),
        ('Data Table',    'Raw data lengkap dengan filter kolom dan export'),
    ])

    # ── 9. KEAMANAN ───────────────────────────────────────────
    h(doc, '9.  Keamanan')
    table(doc, ['Mekanisme', 'Keterangan'], [
        ('JWT Authentication',  'Semua endpoint terproteksi token'),
        ('bcrypt hashing',      'Password tidak disimpan plaintext'),
        ('OTP email',           'Registrasi wajib verifikasi email'),
        ('Read-only guard',     'INSERT/UPDATE/DELETE/DROP diblokir'),
        ('Rate limiting',       'Batas request per user per menit'),
        ('Query timeout',       'Default 30 detik per eksekusi'),
        ('Row limit',           'Default 100 baris per hasil query'),
    ], hbg=GREEN)

    # ── 10. DATABASE SCHEMA ───────────────────────────────────
    doc.add_page_break()
    h(doc, '10.  Database Schema — JOINGATEOCR')

    schema_groups = [
        ('Master & Konfigurasi', ACCENT, [
            ('DB_APP_SETTINGS',       'Konfigurasi: parameter, value, type, timestamp'),
            ('USERS',                 'User: ID, USERNAME, PASSWORD, FULLNAME, ROLE, ACTIVE'),
            ('EFMIGRATIONSHISTORY',   'Riwayat migration Entity Framework'),
        ]),
        ('Device & Monitoring', ACCENT, [
            ('DEVICES',               'Master device: nama, IP, status, response time, lokasi'),
            ('DEVICEHISTORIES',       'Histori status dan response time per device'),
        ]),
        ('Gate & Operasional', ACCENT, [
            ('GATES',                 'Master gate: GATE_NAME, TYPE, ACTIVE'),
            ('GATE_DEVICES',          'Device per gate dengan confidence factor'),
            ('GATE_TRANSACTIONS',     'Transaksi utama: status, plate, weight, OCR, payment'),
            ('GATE_ACTION_TIMES',     'Timeline aksi per transaksi gate'),
            ('GATE_MESSAGE_INFOS',    'Pesan/event terkait transaksi'),
        ]),
        ('OCR & Analitik', ACCENT, [
            ('OCR_DATAS',             'Hasil OCR mentah: gate, image, tag, axle, container, ISO'),
            ('TRANSACTION_OCR_DATAS', 'OCR dipasangkan ke konteks transaksi'),
            ('OCR_IMAGES',            'Referensi gambar OCR per transaksi'),
            ('OCR_AUTOGATE_ACCURACY', 'Metrik akurasi OCR per field'),
        ]),
        ('Tiket & Pembayaran', ACCENT, [
            ('ETICKETS',              'E-ticket container: size, type, terminal, ship, voyage'),
            ('PAYMENT_INFOS',         'Pembayaran gate: nominal, bank, balance, status'),
        ]),
    ]
    for gname, gcol, gtables in schema_groups:
        h(doc, gname, level=2, color=gcol)
        table(doc, ['Tabel', 'Deskripsi'], gtables, hbg=gcol)

    h(doc, 'Relasi Kunci', level=2)
    for r in [
        'DEVICEHISTORIES.DEVICEID → DEVICES.ID',
        'OCR_IMAGES.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
        'GATE_ACTION_TIMES.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
        'PAYMENT_INFOS.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
        'FLAT_RACK_BUNDLE.OCR_DATA_ID → OCR_DATAS.ID',
    ]: bullet(doc, r)
    doc.add_paragraph()

    # ── 11. TIMELINE 8 MINGGU ─────────────────────────────────
    doc.add_page_break()
    h(doc, '11.  Timeline Pengerjaan — 8 Minggu')

    weeks = [
        ('Minggu 1', 'Fondasi Sistem',           PRIMARY, [
            'Finalisasi requirement dan scope',
            'Setup environment server & Docker Oracle/PostgreSQL',
            'Validasi koneksi Oracle 19c',
            'Setup FastAPI skeleton + JWT auth dasar',
            'Streamlit halaman login',
        ]),
        ('Minggu 2', 'Integrasi LLM & Schema',   ACCENT, [
            'Integrasi Ollama / Gemini / OpenAI-compatible',
            'Implementasi prompt text-to-SQL Oracle',
            'Schema reader Oracle JOINGATEOCR',
            'Uji query sederhana end-to-end',
        ]),
        ('Minggu 3', 'Query Execution & Security', GREEN, [
            'SQL validator (read-only guard, syntax check)',
            'Query execution pipeline dengan timeout & row limit',
            'JWT + OTP email verifikasi registrasi',
            'Rate limiting & error handling',
        ]),
        ('Minggu 4', 'Frontend & Visualisasi',   ACCENT, [
            'Chat UI dengan preview SQL',
            'Tabel hasil query interaktif',
            'Auto-visualization (bar, line, pie, scatter, pareto)',
            'Export CSV & Excel',
            'Sidebar riwayat query & cache info',
        ]),
        ('Minggu 5', 'Dashboard & Hardening',    PRIMARY, [
            'Multi-chart dashboard + key metrics',
            'Cache schema dan hasil query (SQLite/Redis)',
            'Health check & metrics endpoint',
            'Penyempurnaan prompt LLM',
            'Test performa dan stabilitas',
        ]),
        ('Minggu 6', 'Penyesuaian Oracle DB',    ORANGE, [
            'Audit dan optimasi query Oracle (index, hint, explain plan)',
            'Fix schema reader: tabel duplikasi DEVICES vs Devices',
            'Handling NVARCHAR2, TIMESTAMP(7) WITH TIME ZONE edge case',
            'Pengujian query kompleks multi-tabel Oracle',
            'Perbaikan ORA-xxxxx errors yang ditemukan saat testing',
            'Dokumentasi known issues dan workaround Oracle 19c',
        ]),
        ('Minggu 7', 'Integrasi PostgreSQL',     '7B2D8B', [
            'Tambah adapter koneksi PostgreSQL (psycopg2)',
            'Schema reader untuk PostgreSQL information_schema',
            'Prompt adjustment Oracle vs PostgreSQL syntax',
            'Pengujian query di database PostgreSQL',
            'UI: switch database provider (Oracle / PostgreSQL)',
            'Dokumentasi konfigurasi multi-database',
        ]),
        ('Minggu 8', 'Finalisasi & Demo',        GREEN, [
            'UAT internal end-to-end (Oracle + PostgreSQL)',
            'Siapkan dataset dan akun demo',
            'Dry run 10 skenario demo beruntun tanpa error',
            'Polish UI dan UX',
            'Freeze versi demo',
            'Deployment final ke server demo',
            'Siapkan materi presentasi',
        ]),
    ]

    for week, theme, color, items in weeks:
        week_header(doc, week, theme, color)
        for item in items:
            bullet(doc, item)
        doc.add_paragraph()

    # ── 12. DEFINITION OF DONE ────────────────────────────────
    h(doc, '12.  Definition of Done untuk Demo')
    table(doc, ['Kriteria', 'Deskripsi'], [
        ('Login',          'User dapat login dan logout dengan aman'),
        ('Natural Language','Pertanyaan bahasa Indonesia/Inggris diterima'),
        ('Generate SQL',   'SQL Oracle/PostgreSQL valid ter-generate'),
        ('Eksekusi',       'Query dieksekusi, hasil tampil sebagai tabel'),
        ('Visualisasi',    'Chart otomatis ter-generate sesuai tipe data'),
        ('Export',         'Hasil dapat diunduh CSV dan Excel'),
        ('Multi-DB',       'User dapat switch antara Oracle dan PostgreSQL'),
        ('Stabilitas',     '10 skenario demo beruntun tanpa error'),
        ('Keamanan',       'Query destructive diblokir, rate limit aktif'),
    ], hbg=GREEN)

    # ── 13. REQUIREMENT SERVER ────────────────────────────────
    h(doc, '13.  Requirement Server')

    h(doc, 'Hardware Minimum', level=2, color=ACCENT)
    table(doc, ['Komponen', 'Spesifikasi'], [
        ('GPU',     'RTX 5090 — 16 GB VRAM'),
        ('CPU',     '8 core / 16 thread'),
        ('RAM',     '32 GB'),
        ('Storage', 'NVMe SSD 500 GB'),
        ('Network', '1 Gbps LAN'),
    ])

    h(doc, 'Hardware Ideal', level=2, color=ACCENT)
    table(doc, ['Komponen', 'Spesifikasi'], [
        ('GPU',     'RTX 5090 — 16 GB VRAM'),
        ('CPU',     '12 core / 24 thread atau lebih'),
        ('RAM',     '64 GB'),
        ('Storage', 'NVMe SSD 1 TB + 1 TB backup'),
    ])

    h(doc, 'Software', level=2, color=ACCENT)
    for s in ['Ubuntu 22.04 LTS', 'Python 3.11+', 'Docker + Docker Compose',
              'Oracle Database 19c (Docker)', 'PostgreSQL 15+ (Docker)',
              'Oracle Instant Client / oracledb driver', 'psycopg2 / asyncpg',
              'Redis (opsional, production cache)', 'Ollama (opsional, local inference)']:
        bullet(doc, s)
    doc.add_paragraph()

    # ── PENUTUP ───────────────────────────────────────────────
    doc.add_page_break()
    h(doc, 'Penutup')
    body(doc,
        'Oracle SQL Chatbot dirancang untuk menjembatani kesenjangan antara data operasional '
        'yang kompleks dan kebutuhan pengguna bisnis akan akses informasi yang cepat. Dengan '
        'timeline 8 minggu yang terstruktur — termasuk minggu khusus penyesuaian Oracle (minggu 6) '
        'dan integrasi PostgreSQL (minggu 7) — sistem ini siap untuk demo end-to-end yang stabil '
        'dan meyakinkan.')
    doc.add_paragraph()
    body(doc,
        'Dukungan multi-database memastikan platform tidak terikat pada satu vendor, '
        'sehingga dapat digunakan lintas infrastruktur database yang berbeda.')
    doc.add_paragraph()
    divider(doc)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Oracle SQL Chatbot  ·  Proposal Proyek  ·  Juni 2026')
    r.font.size = Pt(9); r.font.color.rgb = _rgb('888888')

    # ── SAVE ──────────────────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    doc.save(OUTPUT)
    print(f'Saved: {os.path.abspath(OUTPUT)}')

if __name__ == '__main__':
    main()
