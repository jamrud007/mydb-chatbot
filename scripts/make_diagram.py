"""
Generate architecture flowchart as PNG for the proposal
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'docs', 'diagram_arsitektur.png')

# ── colours ────────────────────────────────────────────────────
C_USER     = '#2E75B6'
C_FRONT    = '#1F4E79'
C_BACK     = '#1F4E79'
C_LLM      = '#C55A11'
C_DB       = '#375623'
C_SUPPORT  = '#BDD7EE'
C_ARROW    = '#2E75B6'
C_WHITE    = '#FFFFFF'
C_DARK     = '#1A1A1A'
C_SUPPORT_TXT = '#1F4E79'

def box(ax, x, y, w, h, label, sublabel='', bg='#1F4E79', fg='white', fontsize=11, radius=0.03):
    rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f'round,pad=0', linewidth=0,
                          facecolor=bg, zorder=3)
    ax.add_patch(rect)
    if sublabel:
        ax.text(x, y + h*0.12, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=fg, zorder=4)
        ax.text(x, y - h*0.2, sublabel, ha='center', va='center',
                fontsize=fontsize - 2, color=fg, alpha=0.88, zorder=4)
    else:
        ax.text(x, y, label, ha='center', va='center',
                fontsize=fontsize, fontweight='bold', color=fg, zorder=4)

def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=C_ARROW,
                                lw=2.2, connectionstyle='arc3,rad=0'))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx + 0.05, my, label, fontsize=8.5, color=C_ARROW,
                fontstyle='italic', va='center')

fig, ax = plt.subplots(figsize=(10, 12))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.axis('off')
fig.patch.set_facecolor('#F8FAFC')

# ── title ──────────────────────────────────────────────────────
ax.text(5, 12.1, 'Arsitektur Sistem — Oracle SQL Chatbot',
        ha='center', va='center', fontsize=14, fontweight='bold', color='#1F4E79')

# ── boxes ──────────────────────────────────────────────────────
# USER
box(ax, 5, 10.8, 2.8, 0.8, 'USER', bg=C_USER)

# Streamlit Frontend
box(ax, 5, 9.2, 7.5, 1.0,
    'STREAMLIT FRONTEND  (port 8501)',
    'Chat   |   Single Chart   |   Dashboard   |   Data Table',
    bg=C_FRONT)

# FastAPI Backend
box(ax, 5, 7.5, 7.5, 1.0,
    'FASTAPI BACKEND  (port 8000)',
    'Auth   ·   Chat   ·   Cache   ·   Metrics   ·   Export',
    bg=C_BACK)

# LLM Engine
box(ax, 2.5, 5.5, 3.5, 2.2,
    'LLM ENGINE',
    'Ollama  (lokal)\nGoogle Gemini\nOpenAI-compatible',
    bg=C_LLM, fontsize=10)

# Database
box(ax, 7.5, 5.5, 3.5, 2.2,
    'DATABASE',
    'Oracle 19c  (JOINGATEOCR)\nPostgreSQL 15+  (Minggu 7)',
    bg=C_DB, fontsize=10)

# Supporting Layer
box(ax, 5, 3.6, 7.5, 1.0,
    'SUPPORTING LAYER',
    'SQLite / Redis Cache   ·   SMTP Email   ·   Structured Logging',
    bg=C_SUPPORT, fg=C_SUPPORT_TXT, fontsize=10)

# ── arrows ──────────────────────────────────────────────────────
arrow(ax, 5, 10.4, 5, 9.72, 'Browser / HTTP')
arrow(ax, 5, 8.7,  5, 8.02, 'REST API / JSON')
arrow(ax, 3.8, 7.0, 2.9, 6.62)
arrow(ax, 6.2, 7.0, 7.1, 6.62)

# backend to supporting
ax.annotate('', xy=(5, 4.12), xytext=(5, 7.0),
            arrowprops=dict(arrowstyle='->', color='#AAAAAA',
                            lw=1.5, linestyle='dashed',
                            connectionstyle='arc3,rad=0'))
ax.text(5.12, 5.55, 'cache / log', fontsize=8, color='#AAAAAA',
        fontstyle='italic', va='center')

# ── legend ──────────────────────────────────────────────────────
legend_items = [
    mpatches.Patch(color=C_FRONT,   label='Frontend Layer'),
    mpatches.Patch(color=C_LLM,     label='LLM Engine'),
    mpatches.Patch(color=C_DB,      label='Database Layer'),
    mpatches.Patch(color=C_SUPPORT, label='Supporting Layer'),
]
ax.legend(handles=legend_items, loc='lower right',
          bbox_to_anchor=(0.98, 0.01), fontsize=9,
          framealpha=0.9, edgecolor='#CCCCCC')

plt.tight_layout()
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
plt.savefig(OUTPUT, dpi=180, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f'Saved: {os.path.abspath(OUTPUT)}')
plt.close()
