# -*- coding: utf-8 -*-
"""
Figuras de recorrido de la investigación (reestructura Cap. 4 + §1.1) — TG RFEH.
===============================================================================
Genera las 5 figuras conceptuales de la reestructura por etapas (E1–E5):

    C1_por_que_rf.png            §1.1  Por qué energía RF (complemento honesto)
    R1_recorrido.png             §4.1  Recorrido de la investigación (E1–E5)
    R2_estrategias.png           §4.3  Estrategias de cosecha evaluadas (A vs. B)
    R3_camino_energia.png        §4.5  El camino de la energía (potencia→energía)
    R4_aporte.png                §4.6  Aporte del proyecto (implementación)

Estilo: identidad visual única del proyecto (_regen/estilo.py) — cajas y
flechas limpias, paleta semántica (A=oro, B=verde, accent=teal), sin símbolos
de circuito. Coma decimal es-CO. Salida 300 dpi en _regen/out/research/.
Cifras ancla verificadas contra CANONICAL/configs (no se inventan valores):
    −20 dBm/banda (referencia difusa) · EIRP 72,15 dBm @ 550 MHz ·
    η_rad = 0,60 · G = 4,97 dBi · PCE ≤ 85 % · η_pmic = 0,85 ·
    E_util = ½·C·(V_max²−V_min²) = 1,26 J · 101 pruebas automatizadas.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

from estilo import COL, INK, MUTE, RAIL, FILL, LINE, FONT

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "research")
os.makedirs(OUT, exist_ok=True)
DPI = 300

AC = COL["accent"]   # teal conceptual
A_GOLD = COL["A"]    # Escenario A · Sierpinski
B_GREEN = COL["B"]   # Escenario B · FLPDA


# ── primitivas locales (cajas con texto envuelto, flechas limpias) ────────────
def box(ax, cx, cy, w, h, lines, accent=AC, fill=FILL, edge=LINE,
        fs=9.0, bold_first=True, sub=None, sub_fs=7.2, lw=1.1, stripe=True):
    """Caja redondeada con franja de acento a la izquierda y texto multilínea.
    Las filas (títulos + sublíneas) se reparten ponderadas por tamaño de fuente,
    de modo que ningún texto desborde la caja."""
    ax.add_patch(FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.07",
        linewidth=lw, edgecolor=edge, facecolor=fill, zorder=2))
    if stripe:
        ax.add_patch(Rectangle((cx - w / 2, cy - h / 2), 0.07, h,
                               facecolor=accent, edgecolor="none", zorder=3))
    rows = []
    for k, ln in enumerate(lines):
        rows.append((ln, fs, "bold" if (bold_first and k == 0) else "normal", INK))
    if sub:
        for s in sub.split("\n"):
            rows.append((s, sub_fs, "normal", MUTE))
    weights = [r[1] for r in rows]
    total = sum(weights)
    pad = 0.16 * h
    usable = h - 2 * pad
    y = cy + h / 2 - pad
    for (txt, size, wgt, col), wg in zip(rows, weights):
        rh = usable * wg / total
        ax.text(cx, y - rh / 2, txt, ha="center", va="center", fontsize=size,
                color=col, family=FONT, zorder=4, fontweight=wgt)
        y -= rh


def arrow(ax, x0, y0, x1, y1, color=None, lw=1.6, ms=12):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                 mutation_scale=ms, linewidth=lw, color=color or RAIL,
                 zorder=1, shrinkA=2, shrinkB=2))


def lienzo(w_in, h_in, xlim, ylim):
    fig, ax = plt.subplots(figsize=(w_in, h_in))
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return fig, ax


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("OK", path)


# ══════════════════════════════════════════════════════════════════════════════
# C1 — Por qué energía RF (§1.1): tres franjas honestas → RF como complemento
# ══════════════════════════════════════════════════════════════════════════════
def fig_c1():
    fig, ax = lienzo(6.2, 2.9, (0, 12.6), (0.2, 6.4))
    bx, bw, bh = 3.55, 6.5, 1.55
    ys = (5.35, 3.25, 1.15)
    box(ax, bx, ys[0], bw, bh, ["Energía solar"],
        sub="entrega mucha potencia,\npero solo con iluminación",
        accent="#C9A227", fs=9.3, sub_fs=7.0)
    box(ax, bx, ys[1], bw, bh, ["RF ambiental"],
        sub="señales débiles pero presentes\ndía y noche (TDT 24/7)",
        accent=AC, fs=9.3, sub_fs=7.0)
    box(ax, bx, ys[2], bw, bh, ["Batería sola"],
        sub="se agota y exige reemplazo\nperiódico en campo",
        accent=COL["warn"], fs=9.3, sub_fs=7.0)
    cx2, cy2, w2, h2 = 10.0, 3.25, 4.5, 2.1
    box(ax, cx2, cy2, w2, h2,
        ["RF como", "complemento", "de la autonomía"],
        accent=AC, fs=9.8, bold_first=True, lw=1.4)
    for y in ys:
        arrow(ax, bx + bw / 2 + 0.1, y, cx2 - w2 / 2 - 0.1, cy2,
              color=RAIL, lw=1.5)
    ax.text(10.0, 1.15, "no reemplaza la fuente principal:\nreduce la dependencia de la batería",
            ha="center", va="center", fontsize=7.2, color=MUTE,
            style="italic", family=FONT)
    save(fig, "C1_por_que_rf.png")


# ══════════════════════════════════════════════════════════════════════════════
# R1 — Recorrido de la investigación (abre Cap. 4): flujo vertical + E1–E5
# ══════════════════════════════════════════════════════════════════════════════
def fig_r1():
    fig, ax = lienzo(6.0, 5.6, (0, 12), (0, 13.4))
    W, H = 9.2, 1.28
    cx = 6.55
    pasos = [
        (["Pregunta de investigación",
          "¿Es viable recuperar energía RF ambiental para complementar",
          "la autonomía de dispositivos de bajo consumo?"], None, INK, 1.75),
        (["Definición del escenario",
          "fuentes RF, estrategias de captación y caso de estudio"], "E1", AC, H),
        (["Modelado electromagnético",
          "antenas: impedancia, S₁₁(f) y ganancia"], "E2", AC, H),
        (["Modelado RF-DC y energético",
          "adaptación, rectificación, gestión y almacenamiento"], "E3", AC, H),
        (["Implementación computacional",
          "Python abierto, pruebas automatizadas y repositorio"], "E4", AC, H),
        (["Comparación y validación",
          "estrategias frente a frente y contraste con la literatura"], "E5", AC, H),
        (["Resultados",
          "viabilidad, criterios de selección y limitaciones"], None, B_GREEN, H),
    ]
    gap = 0.62
    y = 13.4 - 0.15
    centers = []
    for lines, tag, acc, h in pasos:
        cy = y - h / 2
        centers.append((cy, h))
        first = [lines[0]]
        sub = " ".join(lines[1:]) if len(lines) > 1 else None
        if len(lines) == 3:  # pregunta en dos líneas
            box(ax, cx, cy, W, h, [lines[0]], sub=lines[1] + "\n" + lines[2],
                accent=acc, fs=9.4, sub_fs=7.1, lw=1.3)
        else:
            box(ax, cx, cy, W, h, first, sub=sub, accent=acc, fs=9.6, sub_fs=7.4)
        if tag:
            ax.text(cx - W / 2 - 0.55, cy, tag, ha="center", va="center",
                    fontsize=9.5, color=acc, fontweight="bold", family=FONT)
        y = y - h - gap
    for k in range(len(centers) - 1):
        c0, h0 = centers[k]
        c1, h1 = centers[k + 1]
        arrow(ax, cx, c0 - h0 / 2 - 0.04, cx, c1 + h1 / 2 + 0.04, color=RAIL, lw=1.6)
    ax.plot([cx - W / 2 - 0.98, cx - W / 2 - 0.98],
            [centers[1][0] + centers[1][1] / 2, centers[5][0] - centers[5][1] / 2],
            color=RAIL, lw=1.0)
    ax.text(cx - W / 2 - 1.22, (centers[1][0] + centers[5][0]) / 2, "etapas metodológicas",
            ha="center", va="center", rotation=90, fontsize=7.6, color=MUTE,
            style="italic", family=FONT)
    save(fig, "R1_recorrido.png")


# ══════════════════════════════════════════════════════════════════════════════
# R2 — Estrategias de cosecha evaluadas (Etapa 1): A distribuida vs. B dirigida
# ══════════════════════════════════════════════════════════════════════════════
def fig_r2():
    fig, ax = lienzo(6.3, 3.7, (0, 13), (0, 7.6))
    Wc, xA, xB = 5.6, 3.15, 9.85
    # encabezados de columna
    ax.text(xA, 7.25, "Escenario A · captación distribuida", ha="center",
            fontsize=8.8, fontweight="bold", color=A_GOLD, family=FONT)
    ax.text(xB, 7.25, "Escenario B · fuente dominante", ha="center",
            fontsize=8.8, fontweight="bold", color=B_GREEN, family=FONT)
    # fuentes
    box(ax, xA, 5.9, Wc, 1.6, ["Muchas fuentes urbanas débiles"],
        sub="TDT, LTE, WiFi, 5G\nreferencia −20 dBm por banda",
        accent=A_GOLD, fs=8.6, sub_fs=7.0)
    box(ax, xB, 5.9, Wc, 1.6, ["Torre TDT (una fuente potente)"],
        sub="EIRP 72,15 dBm @ 550 MHz\nemisión continua",
        accent=B_GREEN, fs=8.6, sub_fs=7.0)
    # estrategia (protagonista)
    box(ax, xA, 3.65, Wc, 1.85, ["ESTRATEGIA MULTIBANDA"],
        sub="captar poco de muchas bandas a la vez\ny sumar los aportes en DC",
        accent=A_GOLD, fs=9.4, sub_fs=7.2, lw=1.6)
    box(ax, xB, 3.65, Wc, 1.85, ["ESTRATEGIA DIRIGIDA"],
        sub="concentrar la captación sobre la fuente\nconocida, con ganancia y banda ancha",
        accent=B_GREEN, fs=9.4, sub_fs=7.2, lw=1.6)
    # geometría que la materializa (subordinada, pequeña y gris)
    ax.text(xA, 1.95, "se materializa en la geometría:", ha="center",
            fontsize=7.0, color=MUTE, style="italic", family=FONT)
    ax.text(xB, 1.95, "se materializa en la geometría:", ha="center",
            fontsize=7.0, color=MUTE, style="italic", family=FONT)
    ax.text(xA, 1.55, "triángulo de Sierpinski (1,8–5,8 GHz)", ha="center",
            fontsize=8.0, color=MUTE, family=FONT)
    ax.text(xB, 1.55, "FLPDA Koch (470–900 MHz)", ha="center",
            fontsize=8.0, color=MUTE, family=FONT)
    arrow(ax, xA, 5.9 - 0.84, xA, 3.65 + 0.98, color=A_GOLD, lw=1.7)
    arrow(ax, xB, 5.9 - 0.84, xB, 3.65 + 0.98, color=B_GREEN, lw=1.7)
    # separador y mensaje central
    ax.plot([6.5, 6.5], [1.2, 6.9], color=RAIL, lw=1.0, ls=(0, (4, 3)))
    ax.text(6.5, 0.55, "se comparan estrategias de captación bajo idénticas condiciones,\n"
                       "no antenas aisladas", ha="center", va="center",
            fontsize=7.6, color=MUTE, style="italic", family=FONT)
    save(fig, "R2_estrategias.png")


# ══════════════════════════════════════════════════════════════════════════════
# R3 — El camino de la energía (abre Etapa 3): de potencia captada a energía útil
# ══════════════════════════════════════════════════════════════════════════════
def fig_r3():
    fig, ax = lienzo(6.5, 2.0, (0, 14.6), (0.9, 4.35))
    W, H, y = 3.25, 1.5, 2.9
    xs = (1.95, 5.5, 9.05, 12.6)
    titulos = [["Potencia", "captada"], ["Potencia", "aprovechable"],
               ["Energía", "almacenada"], ["Energía disponible", "para el dispositivo"]]
    modelos = ["modelo electromagnético\nη_rad = 0,60 · G = 4,97 dBi",
               "modelo RF-DC\nPCE ≤ 85 %",
               "PMIC + supercondensador\nη_pmic = 0,85",
               "supercondensador\nE_útil = 1,26 J"]
    accs = [AC, AC, AC, B_GREEN]
    for x, t, m, a in zip(xs, titulos, modelos, accs):
        fs_t = 7.2 if len(t[0]) > 12 else 9.0
        box(ax, x, y, W, H, [t[0], t[1]], accent=a, fs=fs_t, bold_first=True)
        ax.text(x, y - H / 2 - 0.58, m, ha="center", va="center",
                fontsize=6.8, color=MUTE, family=FONT)
    for x0, x1 in zip(xs[:-1], xs[1:]):
        arrow(ax, x0 + W / 2 + 0.03, y, x1 - W / 2 - 0.03, y, color=RAIL, lw=1.7)
    ax.text(7.3, 4.05, "lo que se capta como potencia solo sirve al nodo cuando se acumula como energía",
            ha="center", va="center", fontsize=7.4, color=MUTE, style="italic",
            family=FONT)
    save(fig, "R3_camino_energia.png")


# ══════════════════════════════════════════════════════════════════════════════
# R4 — Aporte del proyecto (Etapa 4): del modelo al resultado reproducible
# ══════════════════════════════════════════════════════════════════════════════
def fig_r4():
    fig, ax = lienzo(6.2, 2.6, (0.2, 13), (0.55, 5.45))
    W, H = 3.7, 1.7
    fila1 = [(2.35, 4.4), (6.55, 4.4), (10.75, 4.4)]
    fila2 = [(10.75, 1.65), (6.55, 1.65), (2.35, 1.65)]
    pasos1 = [(["Modelo analítico"], "ecuaciones del Cap. 3\ncon parámetros trazables"),
              (["Implementación", "en Python"], "NumPy/SciPy,\ncódigo abierto"),
              (["Pruebas", "automatizadas"], "101 pruebas bloquean\nlos valores canónicos")]
    pasos2 = [(["Aplicación", "Streamlit"], "recorrido interactivo\ndel modelo completo"),
              (["Repositorio", "abierto"], "código, datos y figuras\nreejecutables"),
              (["Resultados", "reproducibles"], "cada cifra del documento\npuede recalcularse")]
    for (x, y), (t, s) in zip(fila1, pasos1):
        box(ax, x, y, W, H, t, sub=s, accent=AC, fs=8.6, sub_fs=6.6)
    for (x, y), (t, s) in zip(fila2, pasos2):
        acc = B_GREEN if t[0] == "Resultados" else AC
        box(ax, x, y, W, H, t, sub=s, accent=acc, fs=8.6, sub_fs=6.6)
    arrow(ax, fila1[0][0] + W / 2, 4.4, fila1[1][0] - W / 2, 4.4, color=RAIL)
    arrow(ax, fila1[1][0] + W / 2, 4.4, fila1[2][0] - W / 2, 4.4, color=RAIL)
    arrow(ax, fila1[2][0], 4.4 - H / 2 - 0.03, fila2[0][0], 1.65 + H / 2 + 0.03,
          color=RAIL)
    arrow(ax, fila2[0][0] - W / 2, 1.65, fila2[1][0] + W / 2, 1.65, color=RAIL)
    arrow(ax, fila2[1][0] - W / 2, 1.65, fila2[2][0] + W / 2, 1.65, color=RAIL)
    save(fig, "R4_aporte.png")


if __name__ == "__main__":
    fig_c1()
    fig_r1()
    fig_r2()
    fig_r3()
    fig_r4()
