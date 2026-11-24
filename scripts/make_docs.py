"""
Generate project documentation as Word (.docx)
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Oracle_SQL_Chatbot_Documentation.docx')

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    return p

def add_body(doc, text):
    p = doc.add_paragraph(text)
    p.style.font.size = Pt(11)
    return p

def add_bullet(doc, text, level=0):
    p = doc.add_paragraph(text, style='List Bullet')
    return p

def add_table_header(table, headers, bg='1F4E79'):
    row = table.rows[0]
    for i, h in enumerate(headers):
        cell = row.cells[i]
        cell.text = h
        set_cell_bg(cell, bg)
        run = cell.paragraphs[0].runs[0]
        run.font.bold = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

def main():
    doc = Document()

    # --- Page margins ---
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(3)
    section.right_margin = Cm(2.5)

    # =========================================================
    # COVER PAGE
    # =========================================================
    doc.add_paragraph()
    doc.add_paragraph()
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run('Oracle SQL Chatbot')
    run.bold = True
    run.font.size = Pt(28)
    run.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run('Dokumen Ringkas Proyek')
    r.font.size = Pt(16)
    r.font.color.rgb = RGBColor(0x26, 0x96, 0xC8)

    doc.add_paragraph()
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    info.add_run('Schema: JOINGATEOCR  |  Database: Oracle 19c\nJuni 2026').font.size = Pt(11)

    doc.add_page_break()

    # =========================================================
    # 1. REQUIREMENT SERVER
    # =========================================================
    add_heading(doc, '1. Requirement Server', level=1)

    add_heading(doc, 'Hardware Minimum', level=2)
    hw_min = [
        ('GPU', 'RTX 5090 — 16 GB VRAM'),
        ('CPU', '8 core / 16 thread'),
        ('RAM', '32 GB'),
        ('Storage', 'NVMe SSD 500 GB'),
        ('Network', '1 Gbps LAN'),
    ]
    tbl = doc.add_table(rows=1, cols=2)
    tbl.style = 'Table Grid'
    add_table_header(tbl, ['Komponen', 'Spesifikasi'])
    for comp, spec in hw_min:
        row = tbl.add_row()
        row.cells[0].text = comp
        row.cells[1].text = spec
    doc.add_paragraph()

    add_heading(doc, 'Hardware Ideal', level=2)
    hw_ideal = [
        ('GPU', 'RTX 5090 — 16 GB VRAM'),
        ('CPU', '12 core / 24 thread atau lebih'),
        ('RAM', '64 GB'),
        ('Storage', 'NVMe SSD 1 TB + 1 TB backup'),
    ]
    tbl2 = doc.add_table(rows=1, cols=2)
    tbl2.style = 'Table Grid'
    add_table_header(tbl2, ['Komponen', 'Spesifikasi'])
    for comp, spec in hw_ideal:
        row = tbl2.add_row()
        row.cells[0].text = comp
        row.cells[1].text = spec
    doc.add_paragraph()

    add_heading(doc, 'Software', level=2)
    sw = ['Ubuntu 22.04 LTS', 'Python 3.11+', 'Docker + Docker Compose',
          'Oracle Database 19c', 'Oracle Instant Client / oracledb driver',
          'Redis (opsional, production cache)', 'Ollama (opsional, local inference)']
    for s in sw:
        add_bullet(doc, s)
    doc.add_paragraph()

    # =========================================================
    # 2. TECH STACK
    # =========================================================
    add_heading(doc, '2. Tech Stack', level=1)

    stack = [
        ('LLM Engine', [
            'Ollama — local inference dan mode offline',
            'Google Gemini — text-to-SQL cepat dan biaya efisien',
            'OpenAI-compatible client — fleksibilitas provider',
            'LLM factory pattern — provider bisa diganti lewat konfigurasi',
        ]),
        ('Backend', [
            'FastAPI — REST API utama',
            'Pydantic — validasi request/response',
            'JWT authentication — login dan proteksi endpoint',
            'Service layer + repository pattern',
            'Background task abstraction untuk proses async',
            'SQLite atau Redis untuk cache query dan schema',
        ]),
        ('Frontend', [
            'Streamlit — antarmuka utama',
            'Plotly — visualisasi data interaktif',
            'HTML/CSS template tambahan',
        ]),
    ]
    for layer, items in stack:
        add_heading(doc, layer, level=2)
        for item in items:
            add_bullet(doc, item)
    doc.add_paragraph()

    # =========================================================
    # 3. SYSTEM DESIGN DIAGRAM
    # =========================================================
    add_heading(doc, '3. System Design', level=1)

    diagram_text = (
        "USER\n"
        "  │\n"
        "  ▼\n"
        "┌─────────────────────────┐\n"
        "│   Streamlit Frontend    │\n"
        "│   Chat + Dashboard      │\n"
        "└────────────┬────────────┘\n"
        "             │\n"
        "             ▼\n"
        "┌─────────────────────────┐\n"
        "│   FastAPI Backend       │\n"
        "│   Auth · Chat · API     │\n"
        "└──────┬──────────┬───────┘\n"
        "       │          │\n"
        "       ▼          ▼\n"
        "┌──────────┐  ┌──────────────┐\n"
        "│  Oracle  │  │  LLM Engine  │\n"
        "│  19c DB  │  │ Ollama/Gemini│\n"
        "└──────────┘  └──────────────┘\n"
        "\n"
        "Supporting:\n"
        "  • Cache layer: SQLite / Redis\n"
        "  • Analytics & Logging\n"
        "  • Export CSV & Visualization"
    )
    p = doc.add_paragraph()
    run = p.add_run(diagram_text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    doc.add_paragraph()

    # =========================================================
    # 4. UI MOCKUP
    # =========================================================
    add_heading(doc, '4. User Interface Mockup', level=1)

    ui_text = (
        "┌────────────────────────────────────────────────────┐\n"
        "│  Logo │ Oracle SQL Chatbot │ User Profile │ Logout │\n"
        "├───────────────────┬────────────────────────────────┤\n"
        "│ Sidebar           │ Main Workspace                 │\n"
        "│  ○ Chat           │ ┌──────────────────────────┐  │\n"
        "│  ○ Dashboard      │ │ Input pertanyaan natural  │  │\n"
        "│  ○ Riwayat Query  │ └──────────────────────────┘  │\n"
        "│  ○ Schema         │ ┌──────────────────────────┐  │\n"
        "│  ○ Settings       │ │ Preview SQL               │  │\n"
        "│                   │ │ Hasil Tabel               │  │\n"
        "│                   │ │ Grafik Otomatis           │  │\n"
        "│                   │ │ Insight / Summary         │  │\n"
        "│                   │ └──────────────────────────┘  │\n"
        "└───────────────────┴────────────────────────────────┘"
    )
    p = doc.add_paragraph()
    run = p.add_run(ui_text)
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
    doc.add_paragraph()

    # =========================================================
    # 5. DATABASE SCHEMA
    # =========================================================
    add_heading(doc, '5. Database Schema — JOINGATEOCR', level=1)

    schema_groups = [
        ('Master & Konfigurasi', [
            ('DB_APP_SETTINGS', 'Konfigurasi aplikasi: nama parameter, value, type, timestamp audit'),
            ('USERS', 'Data user: ID, USERNAME, PASSWORD, FULLNAME, ROLE, ACTIVE'),
            ('EFMIGRATIONSHISTORY / __EFMigrationsHistory', 'Riwayat migration Entity Framework'),
        ]),
        ('Device & Monitoring', [
            ('DEVICES', 'Master device: nama, IP, status, response time, lokasi, tipe lokasi'),
            ('Devices', 'Versi PascalCase — perlu dikonfirmasi apakah view atau duplikasi'),
            ('DEVICEHISTORIES', 'Histori status device, relasi ke DEVICES.ID'),
            ('DeviceHistories', 'Versi PascalCase dari histori device'),
        ]),
        ('Gate & Infrastruktur Operasional', [
            ('GATES', 'Master gate: GATE_NAME, TYPE, ACTIVE, timestamp'),
            ('GATE_DEVICES', 'Device per gate: IP, active flag, confidence factor'),
            ('GATE_TRANSACTIONS', 'Transaksi utama gate: status, card/tag, plate, weight, OCR, payment'),
            ('GATE_ACTION_TIMES', 'Timeline aksi tiap transaksi gate'),
            ('GATE_MESSAGE_INFOS', 'Pesan/event terkait transaksi gate'),
        ]),
        ('OCR & Analitik', [
            ('OCR_DATAS', 'Hasil OCR mentah: gate, device, image, tag, axle, container, ISO, seal, DG'),
            ('TRANSACTION_OCR_DATAS', 'OCR dipasangkan ke konteks transaksi operasional'),
            ('OCR_IMAGES', 'Referensi gambar OCR → GATE_TRANSACTION_ID & OCR_DATA_ID'),
            ('OCR_AUTOGATE_ACCURACY', 'Metrik akurasi OCR per field: plate, container, ISO, seal, damage'),
        ]),
        ('Container & Fixed OCR', [
            ('FIXED_OCR_DATAS', 'Data OCR hasil koreksi operator'),
            ('FIXED_FLAT_RACK_BUNDLE', 'Bundle flat rack dari fixed OCR → FIXED_OCR_DATAS.ID'),
            ('FLAT_RACK_BUNDLE', 'Bundle flat rack OCR biasa → OCR_DATA_ID'),
            ('FLAT_RACK_BUNDLE_ASSOC', 'Asosiasi bundle → TRANSACTION_OCR_DATA_ID'),
        ]),
        ('Tiket & Pembayaran', [
            ('ETICKETS', 'E-ticket container: size, type, validity, terminal, ship, voyage, gate tx'),
            ('PAYMENT_INFOS', 'Pembayaran gate: status deduct, nominal, bank code, balance'),
        ]),
    ]

    for group_name, tables in schema_groups:
        add_heading(doc, group_name, level=2)
        tbl = doc.add_table(rows=1, cols=2)
        tbl.style = 'Table Grid'
        add_table_header(tbl, ['Tabel', 'Deskripsi'])
        for tname, tdesc in tables:
            row = tbl.add_row()
            row.cells[0].text = tname
            row.cells[0].paragraphs[0].runs[0].font.bold = True if row.cells[0].paragraphs[0].runs else False
            row.cells[1].text = tdesc
        doc.add_paragraph()

    # Relasi kunci
    add_heading(doc, 'Relasi Kunci Antar Tabel', level=2)
    relasi = [
        'DEVICEHISTORIES.DEVICEID → DEVICES.ID',
        'DeviceHistories.DeviceId → Devices.Id',
        'FIXED_FLAT_RACK_BUNDLE.FIXED_OCR_DATA_ID → FIXED_OCR_DATAS.ID',
        'FLAT_RACK_BUNDLE.OCR_DATA_ID → OCR_DATAS.ID',
        'FLAT_RACK_BUNDLE_ASSOC.TRANSACTION_OCR_DATA_ID → TRANSACTION_OCR_DATAS.ID',
        'OCR_IMAGES.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
        'OCR_IMAGES.OCR_DATA_ID → OCR_DATAS.ID',
        'GATE_ACTION_TIMES.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
        'GATE_MESSAGE_INFOS.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
        'PAYMENT_INFOS.GATE_TRANSACTION_ID → GATE_TRANSACTIONS.ID',
    ]
    for r in relasi:
        add_bullet(doc, r)
    doc.add_paragraph()

    # =========================================================
    # 6. FITUR
    # =========================================================
    add_heading(doc, '6. Fitur', level=1)

    features = [
        ('Fitur Inti', [
            'Natural language ke SQL',
            'Multi-LLM provider (Ollama, Gemini, OpenAI-compatible)',
            'Chat berbasis konteks percakapan',
            'Preview SQL sebelum eksekusi',
            'Eksekusi query ke Oracle',
            'Hasil data dalam bentuk tabel',
            'Auto-visualization chart otomatis',
            'Export CSV',
        ]),
        ('Fitur Keamanan', [
            'JWT login',
            'Password hashing (bcrypt)',
            'Rate limiting',
            'Query validation & read-only protection',
        ]),
        ('Fitur Operasional', [
            'Cache hasil query (SQLite / Redis)',
            'Cache schema database',
            'Logging dan analytics endpoint',
            'Konfigurasi berbasis environment (.env)',
            'Docker support untuk deployment cepat',
        ]),
        ('Fitur Pengembangan Lanjutan', [
            'Approval flow sebelum query sensitif',
            'Role-based access per user/divisi',
            'Saved dashboard dan scheduled report',
            'Audit trail pertanyaan, SQL, dan hasil',
            'Fine-tuning prompt untuk domain bisnis',
        ]),
    ]
    for fname, fitems in features:
        add_heading(doc, fname, level=2)
        for fi in fitems:
            add_bullet(doc, fi)
    doc.add_paragraph()

    # =========================================================
    # 7. TIMELINE
    # =========================================================
    add_heading(doc, '7. Timeline Demo (6 Minggu)', level=1)

    timeline = [
        ('Minggu 1', 'Fondasi Sistem', [
            'Finalisasi requirement',
            'Setup environment server dan database',
            'Validasi koneksi Oracle',
            'Setup FastAPI, Streamlit, dan auth dasar',
        ]),
        ('Minggu 2', 'Integrasi LLM', [
            'Integrasi Ollama atau provider API',
            'Implementasi prompt text-to-SQL',
            'Schema reading Oracle JOINGATEOCR',
            'Uji query sederhana',
        ]),
        ('Minggu 3', 'Query Execution & Security', [
            'Validasi SQL',
            'Query execution pipeline',
            'Row limit, timeout, dan read-only guard',
            'Logging dasar dan error handling',
        ]),
        ('Minggu 4', 'Frontend & Visualisasi', [
            'Chat UI',
            'SQL preview',
            'Tabel hasil query',
            'Auto chart dan export CSV',
        ]),
        ('Minggu 5', 'Hardening Demo', [
            'Cache schema dan hasil query',
            'Penyempurnaan prompt',
            'Perbaikan UX',
            'Test skenario demo utama',
        ]),
        ('Minggu 6', 'Finalisasi Demo', [
            'UAT internal',
            'Sample pertanyaan demo',
            'Dataset dan akun user demo',
            'Dry run presentasi',
            'Freeze versi demo',
        ]),
    ]

    tbl = doc.add_table(rows=1, cols=3)
    tbl.style = 'Table Grid'
    add_table_header(tbl, ['Minggu', 'Tema', 'Deliverable'])
    for week, theme, items in timeline:
        row = tbl.add_row()
        row.cells[0].text = week
        row.cells[1].text = theme
        row.cells[2].text = '\n'.join(f'• {i}' for i in items)
    doc.add_paragraph()

    add_heading(doc, 'Definition of Done untuk Demo', level=2)
    dod = [
        'User bisa login',
        'User bisa bertanya dalam bahasa natural',
        'Sistem menghasilkan SQL yang valid',
        'Sistem menghasilkan Oracle SQL sesuai schema JOINGATEOCR',
        'Sistem menampilkan hasil tabel',
        'Sistem menampilkan visualisasi untuk data yang cocok',
        'Sistem bisa export hasil ke CSV',
        'Sistem stabil untuk 5–10 skenario demo beruntun',
    ]
    for d in dod:
        add_bullet(doc, d)

    # =========================================================
    # SAVE
    # =========================================================
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    doc.save(OUTPUT)
    print(f"Saved: {os.path.abspath(OUTPUT)}")


if __name__ == '__main__':
    main()
