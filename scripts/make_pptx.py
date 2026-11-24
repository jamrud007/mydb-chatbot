"""Generate refactoring progress PPTX — May 19, 22, 25 2026"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt
import copy

# ── Palette ──────────────────────────────────────────────────────────────────
DARK_BG   = RGBColor(0x1E, 0x1E, 0x2E)   # dark navy
ACCENT    = RGBColor(0x89, 0xB4, 0xFA)   # catppuccin blue
ACCENT2   = RGBColor(0xA6, 0xE3, 0xA1)   # catppuccin green
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
MUTED     = RGBColor(0xBA, 0xC2, 0xD8)   # subtitle grey
RED_MUTED = RGBColor(0xF3, 0x8B, 0xA8)   # catppuccin red
YELLOW    = RGBColor(0xF9, 0xE2, 0xAF)   # catppuccin yellow

SLIDE_W = Inches(13.33)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H

BLANK = prs.slide_layouts[6]  # completely blank


def add_slide():
    return prs.slides.add_slide(BLANK)


def bg(slide, color=DARK_BG):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def txbox(slide, text, left, top, width, height,
          size=18, bold=False, color=WHITE, align=PP_ALIGN.LEFT,
          wrap=True, italic=False):
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = wrap
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    return tb


def rule(slide, top, color=ACCENT, left=Inches(0.5), width=Inches(12.33), height=Pt(2)):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        left, top, width, height
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def add_bullet(tf, text, size=16, color=WHITE, indent=0, bold=False, color_override=None):
    p = tf.add_paragraph()
    p.level = indent
    c = color_override if color_override else color
    run = p.add_run()
    run.text = ("    " * indent) + text
    run.font.size = Pt(size)
    run.font.color.rgb = c
    run.font.bold = bold
    return p


def section_label(slide, text, top):
    txbox(slide, text, Inches(0.5), top, Inches(4), Inches(0.4),
          size=12, color=ACCENT, bold=True)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)

# decorative top bar
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.08))

# big title
txbox(s, "Architecture Refactoring Progress",
      Inches(0.8), Inches(1.8), Inches(11.5), Inches(1.2),
      size=40, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

txbox(s, "3 Work Sessions  ·  May 19, 22, 25  ·  2026",
      Inches(0.8), Inches(3.0), Inches(11.5), Inches(0.6),
      size=22, color=ACCENT, align=PP_ALIGN.CENTER)

txbox(s, "Part of the 30-day roadmap: Maintainability & Operability Improvements",
      Inches(1.5), Inches(3.8), Inches(10), Inches(0.5),
      size=15, color=MUTED, align=PP_ALIGN.CENTER, italic=True)

# bottom bar
rule(s, Inches(7.3), color=ACCENT2, left=Inches(0), width=SLIDE_W, height=Inches(0.08))


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — Why Refactoring?
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.06))

txbox(s, "Why Refactoring?", Inches(0.5), Inches(0.15), Inches(10), Inches(0.65),
      size=28, bold=True, color=WHITE)
rule(s, Inches(0.85), color=ACCENT, left=Inches(0.5), width=Inches(5.5), height=Pt(2))

# LEFT column — problems
section_label(s, "CONDITIONS FOUND (BEFORE)", Inches(1.0))
tb = s.shapes.add_textbox(Inches(0.5), Inches(1.45), Inches(5.8), Inches(4.5))
tf = tb.text_frame
tf.word_wrap = True
bullets_left = [
    ("Code scattered — changing 1 value required editing 3–4 files", RED_MUTED),
    ("No clear boundary between data, business, and API layers", RED_MUTED),
    ("No coding standard — every developer wrote their own style", RED_MUTED),
    ("IDE couldn't assist due to missing type information", RED_MUTED),
]
first = True
for text, col in bullets_left:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    run = p.add_run()
    run.text = "✗  " + text
    run.font.size = Pt(15)
    run.font.color.rgb = col

# RIGHT column — risks
section_label(s, "REAL RISKS IF LEFT UNADDRESSED", Inches(1.0))
# reposition
tb2 = s.shapes.add_textbox(Inches(7.0), Inches(1.45), Inches(5.8), Inches(4.5))
tf2 = tb2.text_frame
tf2.word_wrap = True
risks = [
    "Hidden bugs from inconsistent values across files",
    "Future refactoring takes 3× longer",
    "Slow onboarding for new developers",
]
first = True
for text in risks:
    p = tf2.paragraphs[0] if first else tf2.add_paragraph()
    first = False
    run = p.add_run()
    run.text = "⚠  " + text
    run.font.size = Pt(15)
    run.font.color.rgb = YELLOW

# vertical divider
div = s.shapes.add_shape(1, Inches(6.6), Inches(1.0), Pt(2), Inches(5.5))
div.fill.solid()
div.fill.fore_color.rgb = MUTED
div.line.fill.background()

# reposition right label
txbox(s, "REAL RISKS IF LEFT UNADDRESSED",
      Inches(7.0), Inches(1.0), Inches(5.8), Inches(0.4),
      size=12, color=ACCENT, bold=True)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — May 19
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.06))

txbox(s, "May 19  ·  Data Layer Separation", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=28, bold=True, color=WHITE)
txbox(s, "Repository Pattern", Inches(0.5), Inches(0.75), Inches(6), Inches(0.4),
      size=16, color=ACCENT, italic=True)
rule(s, Inches(1.1), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

# Before / After diagram
txbox(s, "BEFORE", Inches(0.5), Inches(1.25), Inches(5.5), Inches(0.35), size=12, bold=True, color=RED_MUTED)
txbox(s, "Service Layer  →  database/query_executor.py  (direct)",
      Inches(0.5), Inches(1.6), Inches(5.8), Inches(0.5), size=14, color=RED_MUTED)

txbox(s, "AFTER", Inches(0.5), Inches(2.3), Inches(5.5), Inches(0.35), size=12, bold=True, color=ACCENT2)
txbox(s, "Service Layer  →  QueryRepository  →  database/query_executor.py",
      Inches(0.5), Inches(2.65), Inches(9), Inches(0.5), size=14, color=ACCENT2)

rule(s, Inches(3.35), color=MUTED, left=Inches(0.5), width=Inches(12), height=Pt(1))

# Impact
txbox(s, "IMPACT", Inches(0.5), Inches(3.5), Inches(11), Inches(0.35),
      size=13, bold=True, color=ACCENT)

tb = s.shapes.add_textbox(Inches(0.5), Inches(3.9), Inches(12), Inches(3.0))
tf = tb.text_frame
tf.word_wrap = True
impacts = [
    "If database implementation changes (e.g. switch engine, add async) — only 1 file needs to change",
    "No risk of circular imports between layers",
    "Service layer no longer knows database internals (cache, row limit, engine type)",
]
first = True
for text in impacts:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    run = p.add_run()
    run.text = "✅  " + text
    run.font.size = Pt(16)
    run.font.color.rgb = ACCENT2


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — May 22
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.06))

txbox(s, "May 22  ·  Single Source of Configuration", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=28, bold=True, color=WHITE)
txbox(s, "Config Centralization", Inches(0.5), Inches(0.75), Inches(6), Inches(0.4),
      size=16, color=ACCENT, italic=True)
rule(s, Inches(1.1), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

# Before/After
txbox(s, "BEFORE", Inches(0.5), Inches(1.25), Inches(5.5), Inches(0.35), size=12, bold=True, color=RED_MUTED)
before_lines = [
    'main.py          →  time_window = 60   (hardcoded)',
    'app_services.py  →  time_window = 60   (hardcoded)',
    'ollama_client.py →  timeout = 600       (hardcoded)',
]
tb = s.shapes.add_textbox(Inches(0.5), Inches(1.6), Inches(7), Inches(1.2))
tf = tb.text_frame; tf.word_wrap = False
first = True
for line in before_lines:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    run = p.add_run(); run.text = line
    run.font.size = Pt(13); run.font.color.rgb = RED_MUTED

txbox(s, "AFTER", Inches(0.5), Inches(2.9), Inches(5.5), Inches(0.35), size=12, bold=True, color=ACCENT2)
after_lines = [
    'main.py          →  Config.RATE_LIMIT_TIME_WINDOW',
    'app_services.py  →  Config.RATE_LIMIT_TIME_WINDOW',
    'ollama_client.py →  Config.LLM_TIMEOUT',
    '.env             →  RATE_LIMIT_TIME_WINDOW=120   ← single control point',
]
tb2 = s.shapes.add_textbox(Inches(0.5), Inches(3.25), Inches(9), Inches(1.5))
tf2 = tb2.text_frame; tf2.word_wrap = False
first = True
for line in after_lines:
    p = tf2.paragraphs[0] if first else tf2.add_paragraph()
    first = False
    run = p.add_run(); run.text = line
    run.font.size = Pt(13); run.font.color.rgb = ACCENT2

# Impact
txbox(s, "IMPACT", Inches(0.5), Inches(4.9), Inches(11), Inches(0.35),
      size=13, bold=True, color=ACCENT)
tb3 = s.shapes.add_textbox(Inches(0.5), Inches(5.25), Inches(12), Inches(1.8))
tf3 = tb3.text_frame; tf3.word_wrap = True
impacts = [
    "Single control point for all operational configuration",
    "Production config can differ from development using only .env — no code change needed",
    "7 constants now centralized: rate limit, cache TTL, LLM timeout, query timeout, backend URL, etc.",
]
first = True
for text in impacts:
    p = tf3.paragraphs[0] if first else tf3.add_paragraph()
    first = False
    run = p.add_run(); run.text = "✅  " + text
    run.font.size = Pt(15); run.font.color.rgb = ACCENT2


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5 — May 25
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.06))

txbox(s, "May 25  ·  Type Hints & Code Standards", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=28, bold=True, color=WHITE)
txbox(s, "Ruff + Black activated", Inches(0.5), Inches(0.75), Inches(6), Inches(0.4),
      size=16, color=ACCENT, italic=True)
rule(s, Inches(1.1), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

# Left col — type hints
txbox(s, "TYPE HINTS — IMMEDIATE BENEFITS", Inches(0.5), Inches(1.25), Inches(5.8), Inches(0.35),
      size=12, bold=True, color=ACCENT)
tb = s.shapes.add_textbox(Inches(0.5), Inches(1.65), Inches(5.8), Inches(2.5))
tf = tb.text_frame; tf.word_wrap = True
hints = [
    "IDE catches type errors before code is run",
    "New developers immediately know: what a function accepts, what it returns",
    "execute_query_by_index(query_index: int) → Dict[str, Any]\n    — no need to read the body",
    "7 critical modules annotated",
]
first = True
for h in hints:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    run = p.add_run(); run.text = "•  " + h
    run.font.size = Pt(14); run.font.color.rgb = WHITE

# Right col — tooling
txbox(s, "TOOLING ACTIVATED", Inches(7.0), Inches(1.25), Inches(5.8), Inches(0.35),
      size=12, bold=True, color=ACCENT)
tb2 = s.shapes.add_textbox(Inches(7.0), Inches(1.65), Inches(5.8), Inches(2.5))
tf2 = tb2.text_frame; tf2.word_wrap = True
tools = [
    ("ruff", "Detects bugs & style issues automatically (rules E/F/W/I)"),
    ("black", "Auto-formats code — consistent across the team"),
    ("pyproject.toml", "Standards documented, runnable by anyone"),
]
first = True
for tool, desc in tools:
    p = tf2.paragraphs[0] if first else tf2.add_paragraph()
    first = False
    run = p.add_run(); run.text = tool + "  —  "; run.font.bold = True
    run.font.size = Pt(14); run.font.color.rgb = YELLOW
    run2 = p.add_run(); run2.text = desc
    run2.font.size = Pt(14); run2.font.color.rgb = WHITE

div = s.shapes.add_shape(1, Inches(6.6), Inches(1.2), Pt(2), Inches(3.5))
div.fill.solid(); div.fill.fore_color.rgb = MUTED; div.line.fill.background()

# Impact bar
rule(s, Inches(4.5), color=MUTED, left=Inches(0.5), width=Inches(12), height=Pt(1))
txbox(s, "IMPACT", Inches(0.5), Inches(4.65), Inches(11), Inches(0.35),
      size=13, bold=True, color=ACCENT)
tb3 = s.shapes.add_textbox(Inches(0.5), Inches(5.05), Inches(12), Inches(2.0))
tf3 = tb3.text_frame; tf3.word_wrap = True
impacts = [
    "7 critical modules now compatible with mypy/pyright static type checking",
    "12 unused imports and import-ordering issues cleaned up automatically",
    "Code standards enforced — same output regardless of who runs it",
]
first = True
for text in impacts:
    p = tf3.paragraphs[0] if first else tf3.add_paragraph()
    first = False
    run = p.add_run(); run.text = "✅  " + text
    run.font.size = Pt(15); run.font.color.rgb = ACCENT2


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6 — Overall Progress
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.06))

txbox(s, "Overall Progress", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=28, bold=True, color=WHITE)
rule(s, Inches(0.85), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

rows = [
    ("Week 1", "Maintainability  (Day 1–7)", "6 / 7  done", ACCENT2),
    ("Week 2", "Scalability        (Day 8–14)", "Not started", MUTED),
    ("Week 3", "Operability       (Day 15–21)", "Not started", MUTED),
    ("Week 4", "Security & Governance  (Day 22–28)", "Not started", MUTED),
]

row_h = Inches(0.82)
start_top = Inches(1.1)
col_x = [Inches(0.5), Inches(2.5), Inches(8.0), Inches(11.0)]
col_w = [Inches(1.8), Inches(5.2), Inches(2.7), Inches(2.0)]

# header
header_labels = ["WEEK", "AREA", "STATUS"]
for i, label in enumerate(header_labels):
    txbox(s, label, col_x[i], start_top, col_w[i], Inches(0.4),
          size=12, bold=True, color=ACCENT)

for ri, (week, area, status, col) in enumerate(rows):
    top = start_top + Inches(0.4) + ri * row_h
    # row bg alternating
    if ri % 2 == 0:
        box = s.shapes.add_shape(1, Inches(0.4), top, Inches(12.4), row_h - Inches(0.05))
        box.fill.solid(); box.fill.fore_color.rgb = RGBColor(0x2A, 0x2A, 0x3E)
        box.line.fill.background()
    txbox(s, week, col_x[0], top + Inches(0.18), col_w[0], Inches(0.5), size=15, bold=True, color=WHITE)
    txbox(s, area, col_x[1], top + Inches(0.18), col_w[1], Inches(0.5), size=15, color=WHITE)
    txbox(s, status, col_x[2], top + Inches(0.18), col_w[2], Inches(0.5), size=15, bold=True, color=col)

# next step
txbox(s, "Next:", Inches(0.5), Inches(5.8), Inches(1.2), Inches(0.5),
      size=16, bold=True, color=ACCENT)
txbox(s, "Day 7 — Final architecture documentation + Week 1 technical debt buffer",
      Inches(1.7), Inches(5.8), Inches(10), Inches(0.5),
      size=16, color=WHITE)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7 — Closing
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=SLIDE_W, height=Inches(0.06))

txbox(s, "Closing", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=28, bold=True, color=WHITE)
rule(s, Inches(0.85), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

txbox(s, "Achieved across 3 sessions:", Inches(0.5), Inches(1.1), Inches(10), Inches(0.5),
      size=18, bold=True, color=ACCENT)

tb = s.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(12), Inches(2.5))
tf = tb.text_frame; tf.word_wrap = True
achievements = [
    "Code is easier to change without fear of side effects",
    "Configuration can be controlled by operators without touching code",
    "Coding standards are active and can be enforced automatically",
]
first = True
for text in achievements:
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    first = False
    run = p.add_run(); run.text = "✅  " + text
    run.font.size = Pt(18); run.font.color.rgb = ACCENT2

rule(s, Inches(4.4), color=MUTED, left=Inches(0.5), width=Inches(12), height=Pt(1))

txbox(s, "Remaining effort for Week 1:", Inches(0.5), Inches(4.6), Inches(6), Inches(0.5),
      size=17, bold=True, color=WHITE)
txbox(s, "1 session  (Day 7)", Inches(0.5), Inches(5.15), Inches(6), Inches(0.5),
      size=22, bold=True, color=ACCENT)

# bottom bar
rule(s, Inches(7.3), color=ACCENT2, left=Inches(0), width=SLIDE_W, height=Inches(0.08))


# ─────────────────────────────────────────────────────────────────────────────
out = "docs/refactoring_progress_may2026.pptx"
prs.save(out)
print(f"Saved: {out}")
