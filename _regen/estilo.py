"""
IDENTIDAD VISUAL ÚNICA DEL PROYECTO — figuras de datos y conceptuales.
================================================================================
Fuente única del lenguaje visual: mismo tipo de letra, misma paleta y misma
semántica de color para TODO el material gráfico (figuras de resultados, de
validación, conceptuales y metodológicas). Lo consumen a la vez:

    _regen/generate_artifacts.py   (figuras de datos, matplotlib)
    _regen/figuras_conceptuales.py (figuras conceptuales/metodológicas)

Convención de color (SSOT): Escenario A · Sierpinski = ORO ; Escenario B · FLPDA = VERDE.

Provee: paleta semántica (COL), rcParams unificados (RC) para las gráficas de
datos, y las primitivas de diagrama (canvas, node, flow, iconos técnicos).
"""

import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc, Circle, Polygon, Rectangle, PathPatch
from matplotlib.path import Path

_DASH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _DASH not in sys.path:
    sys.path.insert(0, _DASH)
from configs.parametros import APA7_RC

# ── Neutros ───────────────────────────────────────────────────────────────────
INK   = "#22262e"   # tinta principal (casi negro)
MUTE  = "#5c6672"   # texto secundario
RAIL  = "#c4cbd4"   # líneas/conectores finos
FILL  = "#f7f8fa"   # relleno de nodo (muy claro)
LINE  = "#8a93a0"   # borde de nodo

# ── Paleta semántica ÚNICA ────────────────────────────────────────────────────
COL = {
    "A":      "#B8860B",   # Escenario A · Sierpinski (oro)
    "B":      "#2F7D4F",   # Escenario B · FLPDA (verde)
    "accent": "#0B6E8F",   # serie neutra / conceptual (teal)
    "model":  "#EE7733",   # curva de modelo (validación, naranja)
    "warn":   "#CC3311",   # umbrales / alertas (rojo)
    "aux":    "#AA3377",   # violeta auxiliar
    "ink":    INK, "mute": MUTE, "rail": RAIL, "grid": "#BBBBBB",
}

# Acentos por familia de diagrama conceptual (matices de la misma paleta)
AC_CONCEPT = COL["accent"]   # conceptual (teal)
AC_METHOD  = "#3a4a86"       # metodológica (índigo)
AC_REPRO   = COL["B"]        # reproducibilidad (verde)
AC_A       = COL["A"]        # topología A (oro)
AC_B       = COL["B"]        # topología B (verde)

FONT = "DejaVu Sans"

# ── rcParams ÚNICOS para las figuras de datos (matplotlib) ────────────────────
# Basados en APA7 pero con la misma tipografía sans y la paleta sobria de los
# diagramas, para que gráficas y diagramas compartan identidad.
RC = dict(APA7_RC)
RC.update({
    "font.family":     "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Arial", "Helvetica"],
    "axes.edgecolor":  LINE,
    "axes.labelcolor": INK,
    "text.color":      INK,
    "xtick.color":     MUTE,
    "ytick.color":     MUTE,
    "grid.color":      RAIL,
    "grid.alpha":      0.35,
})


def canvas(w, h, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal"); ax.axis("off")
    return fig, ax


def node(ax, cx, cy, w, h, title, sub=None, idx=None, accent=INK, icon=None,
         title_fs=9.5, sub_fs=7.4):
    """Nodo rectangular fino con badge numerado opcional e icono opcional."""
    ax.add_patch(FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.01,rounding_size=0.05",
        linewidth=1.1, edgecolor=LINE, facecolor=FILL, zorder=2))
    # franja de acento a la izquierda (fina)
    ax.add_patch(Rectangle((cx - w/2, cy - h/2), 0.055, h,
                           facecolor=accent, edgecolor="none", zorder=3))
    ty = cy
    if icon is not None:
        icon(ax, cx, cy + h*0.20, min(w, h)*0.30, accent)
        ty = cy - h*0.22
    if sub:
        ax.text(cx, ty + (0.0 if icon else h*0.12), title, ha="center", va="center",
                fontsize=title_fs, color=INK, fontweight="bold", family=FONT, zorder=4)
        ax.text(cx, ty - h*0.20, sub, ha="center", va="center",
                fontsize=sub_fs, color=MUTE, family=FONT, zorder=4)
    else:
        ax.text(cx, ty, title, ha="center", va="center", fontsize=title_fs,
                color=INK, fontweight="bold", family=FONT, zorder=4)
    if idx is not None:
        bx, by = cx - w/2 + 0.16, cy + h/2 - 0.16
        ax.add_patch(Circle((bx, by), 0.135, facecolor=accent, edgecolor="none", zorder=5))
        ax.text(bx, by, str(idx), ha="center", va="center", fontsize=7.6,
                color="white", fontweight="bold", family=FONT, zorder=6)


def flow(ax, x0, y0, x1, y1, accent=RAIL, lw=1.6, ms=11, style="-|>"):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style,
                 mutation_scale=ms, linewidth=lw, color=accent, zorder=1,
                 shrinkA=1, shrinkB=1))


def caption(ax, x, y, text, fs=7.8):
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, style="italic",
            color=MUTE, family=FONT)


# ══════════════════════════════════════════════════════════════════════════════
#  PRIMITIVAS "IEEE" — diagrama técnico de artículo, sin tarjetas ni sombras.
#  Rectángulo de esquina recta, borde fino monocromo, tipografía serif académica.
# ══════════════════════════════════════════════════════════════════════════════

FONT_SERIF = "Times New Roman"


def node_ieee(ax, cx, cy, w, h, title, sub=None, icon=None, icon_color=None,
              title_fs=9.3, sub_fs=7.3, step=None, lw=1.0):
    """Bloque rectangular de esquina recta (sin 'rounding', sin relleno de color,
    sin franja de acento, sin sombra). Icono de línea en tinta neutra arriba,
    título en serif debajo, subtítulo opcional en cursiva gris más pequeño."""
    ax.add_patch(Rectangle((cx - w/2, cy - h/2), w, h,
                 linewidth=lw, edgecolor=INK, facecolor="white", zorder=2))
    ic_color = icon_color or INK
    ty = cy
    if icon is not None:
        icon(ax, cx, cy + h * 0.24, min(w, h) * 0.27, ic_color)
        ty = cy - h * 0.16
    if sub:
        ax.text(cx, ty + (0.0 if icon else h * 0.14), title, ha="center", va="center",
                fontsize=title_fs, color=INK, family=FONT_SERIF, zorder=4)
        ax.text(cx, ty - h * 0.24, sub, ha="center", va="center",
                fontsize=sub_fs, color=MUTE, family=FONT_SERIF, style="italic", zorder=4)
    else:
        ax.text(cx, ty, title, ha="center", va="center", fontsize=title_fs,
                color=INK, family=FONT_SERIF, zorder=4)
    if step is not None:
        ax.text(cx - w / 2 + 0.07, cy + h / 2 - 0.07, str(step), ha="left", va="top",
                fontsize=7.2, color=MUTE, family=FONT_SERIF, style="italic", zorder=5)


def flow_ieee(ax, x0, y0, x1, y1, lw=0.9, ms=8.5, color=None):
    """Flecha fina monocroma (estilo diagrama de bloques de artículo técnico)."""
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                 mutation_scale=ms, linewidth=lw, color=color or INK, zorder=1,
                 shrinkA=1, shrinkB=1))


def label_ieee(ax, x, y, text, fs=8.5, weight="normal", ha="center", style="normal",
              color=None):
    ax.text(x, y, text, ha=ha, va="center", fontsize=fs, family=FONT_SERIF,
            fontweight=weight, style=style, color=color or INK)


# ══════════════════════════════════════════════════════════════════════════════
#  ICONOS TÉCNICOS DE LÍNEA  (ax, cx, cy, s, color)  — s = radio aproximado
# ══════════════════════════════════════════════════════════════════════════════

def _ln(ax, xs, ys, c, lw=1.5):
    ax.plot(xs, ys, color=c, lw=lw, solid_capstyle="round", zorder=4)

def ic_city(ax, cx, cy, s, c):
    hs = [0.9, 1.4, 1.1, 1.6, 1.0]
    n = len(hs); bw = 2*s/n
    for i, h in enumerate(hs):
        x = cx - s + i*bw
        ax.add_patch(Rectangle((x, cy - s*0.7), bw*0.78, h*s*0.9,
                     facecolor="none", edgecolor=c, lw=1.3, zorder=4))

def ic_waves(ax, cx, cy, s, c):
    for k, r in enumerate((0.45, 0.8, 1.15)):
        ax.add_patch(Arc((cx - s*0.7, cy - s*0.2), r*s*2, r*s*2, angle=0,
                     theta1=-55, theta2=55, edgecolor=c, lw=1.4, zorder=4))
    ax.add_patch(Circle((cx - s*0.7, cy - s*0.2), s*0.09, facecolor=c, edgecolor="none", zorder=5))

def ic_antenna(ax, cx, cy, s, c):
    _ln(ax, [cx, cx], [cy - s, cy + s*0.2], c)                 # mástil
    _ln(ax, [cx, cx - s*0.6], [cy + s*0.2, cy + s], c)          # brazo izq
    _ln(ax, [cx, cx + s*0.6], [cy + s*0.2, cy + s], c)          # brazo der
    for r in (0.5, 0.85):
        ax.add_patch(Arc((cx, cy + s*0.2), r*s*2, r*s*2, angle=0,
                     theta1=35, theta2=145, edgecolor=c, lw=1.1, zorder=4))

def ic_match(ax, cx, cy, s, c):
    # inductor (3 arcos) + línea
    x0 = cx - s
    for i in range(3):
        ax.add_patch(Arc((x0 + i*s*0.5 + s*0.25, cy), s*0.5, s*0.7, angle=0,
                     theta1=0, theta2=180, edgecolor=c, lw=1.4, zorder=4))
    _ln(ax, [cx + s*0.5, cx + s], [cy, cy], c)
    _ln(ax, [cx + s, cx + s], [cy + s*0.5, cy - s*0.5], c)      # cap placa
    _ln(ax, [cx + s + 0.12, cx + s + 0.12], [cy + s*0.5, cy - s*0.5], c)

def ic_diode(ax, cx, cy, s, c):
    _ln(ax, [cx - s, cx - s*0.4], [cy, cy], c)
    ax.add_patch(Polygon([[cx - s*0.4, cy - s*0.6], [cx - s*0.4, cy + s*0.6],
                 [cx + s*0.4, cy]], closed=True, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    _ln(ax, [cx + s*0.4, cx + s*0.4], [cy - s*0.6, cy + s*0.6], c)   # barra
    _ln(ax, [cx + s*0.4, cx + s], [cy, cy], c)

def ic_chip(ax, cx, cy, s, c):
    ax.add_patch(Rectangle((cx - s*0.6, cy - s*0.6), s*1.2, s*1.2,
                 facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    for i in (-0.3, 0, 0.3):
        _ln(ax, [cx - s*0.6, cx - s*0.85], [cy + i*s*2, cy + i*s*2], c, 1.1)
        _ln(ax, [cx + s*0.6, cx + s*0.85], [cy + i*s*2, cy + i*s*2], c, 1.1)

def ic_battery(ax, cx, cy, s, c):
    ax.add_patch(Rectangle((cx - s*0.9, cy - s*0.5), s*1.7, s, facecolor="none",
                 edgecolor=c, lw=1.4, zorder=4))
    ax.add_patch(Rectangle((cx + s*0.8, cy - s*0.22), s*0.18, s*0.44, facecolor=c,
                 edgecolor="none", zorder=4))
    _ln(ax, [cx - s*0.35, cx - s*0.35], [cy - s*0.28, cy + s*0.28], c)
    _ln(ax, [cx + s*0.1, cx + s*0.1], [cy - s*0.28, cy + s*0.28], c)

def ic_code(ax, cx, cy, s, c):
    _ln(ax, [cx - s*0.2, cx - s*0.8, cx - s*0.2], [cy + s*0.7, cy, cy - s*0.7], c)
    _ln(ax, [cx + s*0.2, cx + s*0.8, cx + s*0.2], [cy + s*0.7, cy, cy - s*0.7], c)

def ic_model(ax, cx, cy, s, c):
    # ejes + curva analítica saturante (modelo de forma cerrada)
    import math
    _ln(ax, [cx - s*0.8, cx - s*0.8, cx + s*0.85], [cy + s*0.85, cy - s*0.7, cy - s*0.7], c, 1.2)
    xs = [cx - s*0.7 + (k/40.0)*s*1.5 for k in range(41)]
    ys = [cy - s*0.55 + s*1.1*(1 - math.exp(-3.0*(k/40.0))) for k in range(41)]
    ax.plot(xs, ys, color=c, lw=1.7, solid_capstyle="round", zorder=4)

def ic_chart(ax, cx, cy, s, c):
    for i, h in enumerate((0.6, 1.1, 0.85)):
        x = cx - s*0.7 + i*s*0.7
        ax.add_patch(Rectangle((x, cy - s*0.7), s*0.42, h*s, facecolor="none",
                     edgecolor=c, lw=1.3, zorder=4))

def ic_check(ax, cx, cy, s, c):
    ax.add_patch(Circle((cx, cy), s*0.95, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    _ln(ax, [cx - s*0.45, cx - s*0.1, cx + s*0.5], [cy, cy - s*0.4, cy + s*0.45], c, 1.8)

def ic_question(ax, cx, cy, s, c):
    ax.add_patch(Circle((cx, cy), s*0.95, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    ax.text(cx, cy, "?", ha="center", va="center", fontsize=s*24, color=c,
            fontweight="bold", family=FONT, zorder=5)

def ic_bulb(ax, cx, cy, s, c):
    ax.add_patch(Circle((cx, cy + s*0.2), s*0.7, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    _ln(ax, [cx - s*0.3, cx + s*0.3], [cy - s*0.55, cy - s*0.55], c)
    _ln(ax, [cx - s*0.22, cx + s*0.22], [cy - s*0.8, cy - s*0.8], c)

def ic_alert(ax, cx, cy, s, c):
    ax.add_patch(Polygon([[cx, cy + s], [cx - s*0.9, cy - s*0.7], [cx + s*0.9, cy - s*0.7]],
                 closed=True, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    _ln(ax, [cx, cx], [cy + s*0.5, cy - s*0.15], c, 1.6)
    ax.add_patch(Circle((cx, cy - s*0.4), s*0.09, facecolor=c, edgecolor="none", zorder=5))

def ic_pin(ax, cx, cy, s, c):
    ax.add_patch(Circle((cx, cy + s*0.25), s*0.7, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    ax.add_patch(Polygon([[cx - s*0.5, cy + s*0.05], [cx + s*0.5, cy + s*0.05], [cx, cy - s]],
                 closed=True, facecolor="none", edgecolor=c, lw=1.4, zorder=4))
    ax.add_patch(Circle((cx, cy + s*0.28), s*0.22, facecolor=c, edgecolor="none", zorder=5))

def ic_branch(ax, cx, cy, s, c):
    # dos formas (A triángulo / B peine) para "dos topologías"
    ax.add_patch(Polygon([[cx - s*0.75, cy - s*0.5], [cx - s*0.15, cy - s*0.5],
                 [cx - s*0.45, cy + s*0.5]], closed=True, facecolor="none",
                 edgecolor=AC_A, lw=1.5, zorder=4))
    _ln(ax, [cx + s*0.5, cx + s*0.5], [cy - s*0.5, cy + s*0.5], AC_B, 1.5)
    for dy in (-0.3, 0, 0.3):
        _ln(ax, [cx + s*0.2, cx + s*0.5], [cy + dy*s*2, cy + dy*s*2], AC_B, 1.3)
