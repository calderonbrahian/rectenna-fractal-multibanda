# -*- coding: utf-8 -*-
"""
================================================================================
FIGURA: Rango de eficiencia total RF->DC por antena y escenario
================================================================================
Gráfico tipo "dumbbell" (dos puntos unidos por una línea) mostrando, por
antena, el eta_total en su escenario de fuente débil/difusa frente a su
escenario de fuente fuerte/cercana. Fuente de datos:
_regen/out/efficiency_values.json (generado por derive_efficiency_values.py;
ningún valor se recalcula aquí).

Nota honesta de lectura: eta_total = eta_rad * eta_mm * eta_imn * PCE * eta_pmic
es una FIGURA DE MÉRITO POR BANDA, no una medida de potencia absoluta. Para
Sierpinski y el parche los dos escenarios comparados están en bandas distintas
(el ambiente urbano difuso es una cosecha AGREGADA de 7 bandas; la fuente fuerte
cercana es un enlace de UNA banda: 3,30 GHz para el Sierpinski —emisor
intencional en banda, se evita la anti-resonancia de 2,45 GHz— y 2,45 GHz para
el parche, su f0). Por eso eta_total puede no ser monótono con la cercanía de la
fuente: para el Sierpinski el escenario "fuerte" cae a 3,55 % (banda de baja
ganancia) frente a 3,68 % del agregado ambiente, mientras que su P_dc por banda
a 3,30 GHz sí es mayor que la contribución de esa misma banda en el ambiente.
Para la FLPDA, eta_total es IDÉNTICO en 100 m y
1000 m porque el rectificador satura en su PCE máxima (85 %) en todo ese
rango de potencia — la diferencia real entre esos dos escenarios está en la
potencia absoluta (1335,0 µW vs 13,4 µW), no en la eficiencia porcentual.
Este gráfico grafica exactamente lo que se le pidió (el rango de eta_total),
y esta nota se imprime también como pie de figura para que no se preste a
una lectura errónea del tipo "cercano siempre es más eficiente en %".

Genera:
    _regen/out/figuras/FigS4_rangos_eficiencia.png   (estilo documento, APA7)
    _regen/out/poster/P6_eficiencia_rangos.png       (estilo póster)

Ejecutar: PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/efficiency_ranges_figure.py
================================================================================
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT_FIG = os.path.join(os.path.dirname(__file__), "out", "figuras")
OUT_POSTER = os.path.join(os.path.dirname(__file__), "out", "poster")
os.makedirs(OUT_FIG, exist_ok=True)
os.makedirs(OUT_POSTER, exist_ok=True)

with open(os.path.join(os.path.dirname(__file__), "out", "efficiency_values.json"),
          encoding="utf-8") as fh:
    DATA = json.load(fh)

# (antena, etiqueta, clave escenario débil, clave escenario fuerte)
ROWS = [
    ("sierpinski", "Sierpinski\n(Escenario A)", "ambiente_urbano_difuso", "fuente_fuerte_cercana"),
    ("parche_FR4", "Parche FR-4\n(microcinta)", "ambiente_urbano_difuso", "fuente_fuerte_wifi"),
    ("flpda", "FLPDA Koch\n(Escenario B)", "fuente_lejana_1000m", "fuente_cercana_100m"),
]

FOOTNOTE = (
    r"$\eta_{total}$ es una figura de mérito por banda, no una medida de potencia absoluta; "
    "no siempre crece con la cercanía de la fuente (ver texto). "
    "FLPDA: mismo $\\eta_{total}$ a 100 y 1000 m porque el PCE satura (85 %); "
    "la diferencia real está en la potencia absoluta (1335,0 vs 13,4 µW)."
)


def _rows_values():
    out = []
    for key, label, k_weak, k_strong in ROWS:
        w = DATA[key][k_weak]["eta_total"] * 100.0
        s = DATA[key][k_strong]["eta_total"] * 100.0
        out.append((label, w, s, DATA[key][k_weak]["descripcion"],
                    DATA[key][k_strong]["descripcion"]))
    return out


# ═══════════════════════════════════════════════════════════════════════════
# Versión documento (APA7 / estilo.py)
# ═══════════════════════════════════════════════════════════════════════════
def _co(x, spec: str) -> str:
    """Formatea `x` con `spec` y coma decimal (convención es-CO del pipeline)."""
    return format(x, spec).replace(".", ",")


def fig_doc():
    import _regen.estilo as E
    plt.rcParams.update(E.RC)

    rows = _rows_values()
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ys = list(range(len(rows)))[::-1]

    c_weak, c_strong, c_line = E.MUTE, E.COL["warn"], E.LINE

    # Umbral de "cercanía visual" relativo al rango del eje (no al valor
    # absoluto): dos puntos separados por pocos puntos porcentuales colisionan
    # igual de mal en un eje de 0-6 % que en uno de 0-56 %, así que el umbral
    # se define como fracción del ancho final del eje, no un valor fijo.
    _xmax_preview = max(s for _, _, s, _, _ in rows) * 1.35 + 5
    _close_thresh = 0.08 * _xmax_preview

    for y, (label, w, s, _, _) in zip(ys, rows):
        close = abs(s - w) < _close_thresh  # puntos visualmente próximos
        ax.plot([w, s], [y, y], color=c_line, lw=2.2, zorder=1, solid_capstyle="round")
        ax.scatter([w], [y], s=70, color=c_weak, zorder=3, label="Débil/difusa" if y == ys[0] else None)
        ax.scatter([s], [y], s=70, color=c_strong, zorder=3, label="Fuerte/cercana" if y == ys[0] else None)
        if close:
            ax.annotate(f"{_co(w, '.2f')} %", (w, y), textcoords="offset points", xytext=(-6, 12),
                        ha="right", fontsize=8.5, color=c_weak, fontweight="bold")
            ax.annotate(f"{_co(s, '.2f')} %", (s, y), textcoords="offset points", xytext=(6, -14),
                        ha="left", fontsize=8.5, color=c_strong, fontweight="bold")
        else:
            ax.annotate(f"{_co(w, '.2f')} %", (w, y), textcoords="offset points", xytext=(0, 10),
                        ha="center", fontsize=8.5, color=c_weak, fontweight="bold")
            ax.annotate(f"{_co(s, '.2f')} %", (s, y), textcoords="offset points", xytext=(0, 10),
                        ha="center", fontsize=8.5, color=c_strong, fontweight="bold")

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=9.5)
    ax.set_xlabel(r"$\eta_{total}$ (%)")
    ax.set_xlim(-2, max(s for _, _, s, _, _ in rows) * 1.35 + 5)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.legend(loc="lower right", fontsize=8.5, framealpha=0.9)
    ax.set_title(r"Rango de $\eta_{total}$ por antena — escenario débil vs. fuerte", fontsize=11)
    fig.text(0.01, -0.04, FOOTNOTE, fontsize=6.6, color=E.MUTE, wrap=True, va="top")

    p = os.path.join(OUT_FIG, "FigS4_rangos_eficiencia.png")
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ] FigS4_rangos_eficiencia.png")


# ═══════════════════════════════════════════════════════════════════════════
# Versión póster (paleta institucional TEAL/LIME/naranja)
# ═══════════════════════════════════════════════════════════════════════════
def fig_poster():
    from _regen.poster_figures import POSTER_RC, TEAL, TEAL_D, LIME, ORANGE, GRAY, dc, FMT_COMA
    plt.rcParams.update(POSTER_RC)

    rows = _rows_values()
    fig, ax = plt.subplots(figsize=(9.0, 5.2))
    ys = list(range(len(rows)))[::-1]

    _xmax_preview = max(s for _, _, s, _, _ in rows) * 1.35 + 5
    _close_thresh = 0.08 * _xmax_preview

    for y, (label, w, s, _, _) in zip(ys, rows):
        close = abs(s - w) < _close_thresh
        ax.plot([w, s], [y, y], color=GRAY, lw=4.0, zorder=1, solid_capstyle="round")
        ax.scatter([w], [y], s=260, color=TEAL, zorder=3, edgecolor="white", linewidth=1.5,
                  label="Débil/difusa" if y == ys[0] else None)
        ax.scatter([s], [y], s=260, color=ORANGE, zorder=3, edgecolor="white", linewidth=1.5,
                  label="Fuerte/cercana" if y == ys[0] else None)
        if close:
            ax.annotate(dc(w, 2) + " %", (w, y), textcoords="offset points", xytext=(-10, 18),
                        ha="right", fontsize=14, color=TEAL, fontweight="bold")
            ax.annotate(dc(s, 2) + " %", (s, y), textcoords="offset points", xytext=(10, -22),
                        ha="left", fontsize=14, color=ORANGE, fontweight="bold")
        else:
            ax.annotate(dc(w, 2) + " %", (w, y), textcoords="offset points", xytext=(0, 16),
                        ha="center", fontsize=14, color=TEAL, fontweight="bold")
            ax.annotate(dc(s, 2) + " %", (s, y), textcoords="offset points", xytext=(0, 16),
                        ha="center", fontsize=14, color=ORANGE, fontweight="bold")

    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows], fontsize=15)
    ax.set_xlabel(r"$\eta_{total}$ (%)")
    ax.set_xlim(-2, max(s for _, _, s, _, _ in rows) * 1.35 + 5)
    ax.set_ylim(-0.7, len(rows) - 0.3)
    ax.legend(loc="upper right", fontsize=13, framealpha=0.9)
    ax.set_title("Rango de eficiencia total RF→DC por antena", pad=14)
    ax.xaxis.set_major_formatter(FMT_COMA)

    p = os.path.join(OUT_POSTER, "P6_eficiencia_rangos.png")
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ] P6_eficiencia_rangos.png")


if __name__ == "__main__":
    fig_doc()
    fig_poster()
