"""Generate refactoring progress PPTX (short version) — May 19, 22, 25 2026"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# ── Palette ──────────────────────────────────────────────────────────────────
DARK_BG   = RGBColor(0x1E, 0x1E, 0x2E)   # dark navy
ACCENT    = RGBColor(0x89, 0xB4, 0xFA)   # catppuccin blue
ACCENT2   = RGBColor(0xA6, 0xE3, 0xA1)   # catppuccin green
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
MUTED     = RGBColor(0xBA, 0xC2, 0xD8)   # subtitle grey
RED_MUTED = RGBColor(0xF3, 0x8B, 0xA8)   # catppuccin red
YELLOW    = RGBColor(0xF9, 0xE2, 0xAF)   # catppuccin yellow

prs = Presentation()
prs.slide_width  = Inches(13.33)
prs.slide_height = Inches(7.5)

BLANK = prs.slide_layouts[6]


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
    shape = slide.shapes.add_shape(1, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=Inches(13.33), height=Inches(0.08))

txbox(s, "Refactoring Progress",
      Inches(0.8), Inches(2.2), Inches(11.5), Inches(1.0),
      size=48, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

txbox(s, "May 19, 22, 25  ·  2026",
      Inches(0.8), Inches(3.3), Inches(11.5), Inches(0.6),
      size=28, color=ACCENT, align=PP_ALIGN.CENTER)

rule(s, Inches(7.3), color=ACCENT2, left=Inches(0), width=Inches(13.33), height=Inches(0.08))


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2 — What We Did
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=Inches(13.33), height=Inches(0.06))

txbox(s, "What We Did", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=32, bold=True, color=WHITE)
rule(s, Inches(0.85), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

# 3-column layout
dates = [
    ("May 19", "Separate Data Layer", [
        "Created QueryRepository",
        "Clean boundary between layers",
        "Easier to refactor database code",
    ], Inches(0.5)),
    ("May 22", "Centralize Config", [
        "All constants in Config",
        "Operators control via .env",
        "7 values tightly managed",
    ], Inches(4.7)),
    ("May 25", "Add Type Hints", [
        "7 critical modules annotated",
        "IDE catches errors early",
        "12 lint issues fixed",
    ], Inches(8.9)),
]

for date, title, items, left in dates:
    txbox(s, date, left, Inches(1.1), Inches(3.8), Inches(0.35),
          size=14, bold=True, color=ACCENT)
    txbox(s, title, left, Inches(1.45), Inches(3.8), Inches(0.4),
          size=16, bold=True, color=WHITE)

    tb = s.shapes.add_textbox(left, Inches(1.95), Inches(3.8), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    first = True
    for item in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        run = p.add_run()
        run.text = "✓  " + item
        run.font.size = Pt(14)
        run.font.color.rgb = ACCENT2

# dividers
for x in [Inches(4.5), Inches(8.7)]:
    div = s.shapes.add_shape(1, x, Inches(1.0), Pt(2), Inches(5.0))
    div.fill.solid()
    div.fill.fore_color.rgb = MUTED
    div.line.fill.background()


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3 — Impact
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=Inches(13.33), height=Inches(0.06))

txbox(s, "Impact", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=32, bold=True, color=WHITE)
rule(s, Inches(0.85), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

impacts = [
    ("Code easier to change", "Database refactoring affects only 1 file, not 5+", ACCENT2),
    ("Config decoupled", "Production settings via .env — zero code changes needed", ACCENT2),
    ("Standards enforced", "IDE catches bugs, code formatted consistently", ACCENT2),
]

row_h = Inches(1.3)
start_top = Inches(1.2)

for i, (title, desc, color) in enumerate(impacts):
    top = start_top + i * row_h
    txbox(s, "✅  " + title, Inches(0.5), top, Inches(12), Inches(0.35),
          size=18, bold=True, color=color)
    txbox(s, desc, Inches(1.0), top + Inches(0.4), Inches(11.5), Inches(0.7),
          size=15, color=MUTED, wrap=True)


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4 — Status & Next
# ─────────────────────────────────────────────────────────────────────────────
s = add_slide()
bg(s)
rule(s, Inches(0), color=ACCENT, left=Inches(0), width=Inches(13.33), height=Inches(0.06))

txbox(s, "Status & Next Step", Inches(0.5), Inches(0.15), Inches(11), Inches(0.65),
      size=32, bold=True, color=WHITE)
rule(s, Inches(0.85), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

# Status table
txbox(s, "Week 1 (Maintainability)", Inches(0.5), Inches(1.15), Inches(6), Inches(0.4),
      size=16, bold=True, color=WHITE)
txbox(s, "6 / 7 done  ✅", Inches(6.6), Inches(1.15), Inches(5.5), Inches(0.4),
      size=16, bold=True, color=ACCENT2, align=PP_ALIGN.RIGHT)

rule(s, Inches(1.65), color=MUTED, left=Inches(0.5), width=Inches(12), height=Pt(1))

txbox(s, "Week 2 (Scalability)", Inches(0.5), Inches(1.8), Inches(6), Inches(0.4),
      size=16, bold=True, color=WHITE)
txbox(s, "Not started", Inches(6.6), Inches(1.8), Inches(5.5), Inches(0.4),
      size=16, color=MUTED, align=PP_ALIGN.RIGHT)

txbox(s, "Week 3 (Operability)", Inches(0.5), Inches(2.3), Inches(6), Inches(0.4),
      size=16, bold=True, color=WHITE)
txbox(s, "Not started", Inches(6.6), Inches(2.3), Inches(5.5), Inches(0.4),
      size=16, color=MUTED, align=PP_ALIGN.RIGHT)

txbox(s, "Week 4 (Security)", Inches(0.5), Inches(2.8), Inches(6), Inches(0.4),
      size=16, bold=True, color=WHITE)
txbox(s, "Not started", Inches(6.6), Inches(2.8), Inches(5.5), Inches(0.4),
      size=16, color=MUTED, align=PP_ALIGN.RIGHT)

rule(s, Inches(3.5), color=ACCENT, left=Inches(0.5), width=Inches(12), height=Pt(2))

txbox(s, "Next: Day 7", Inches(0.5), Inches(4.0), Inches(3), Inches(0.5),
      size=22, bold=True, color=ACCENT)
txbox(s, "Final architecture documentation + Week 1 technical debt buffer",
      Inches(3.6), Inches(4.0), Inches(8.5), Inches(0.5),
      size=18, color=WHITE, wrap=True)

rule(s, Inches(7.3), color=ACCENT2, left=Inches(0), width=Inches(13.33), height=Inches(0.08))


# ─────────────────────────────────────────────────────────────────────────────
out = "docs/refactoring_progress_short.pptx"
prs.save(out)
print(f"Saved: {out}")
