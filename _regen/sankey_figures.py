# -*- coding: utf-8 -*-
"""
================================================================================
FIGURAS: Diagramas Sankey estáticos de la cadena RF→DC (matplotlib puro)
================================================================================
Visualiza, para cada antena, qué fracción de la potencia RF disponible
sobrevive en cada eslabón de la cadena hasta la salida DC. El nodo de entrada
(100 %) depende de la arquitectura para que las franjas sean auto-consistentes
(franjas × P_entrada = P_DC, corrección K1):

    Conjugada (Sierpinski/parche):   P_in(puerto) → η_cm → PCE → η_pmic → P_DC
    Modular de 50 Ω (FLPDA):  P_incidente → η_rad → η_mm → η_imn → PCE → η_pmic → P_DC
                              (el puerto de antena, 1982 µW, queda tras η_rad)

Implementación 100% matplotlib.patches (Polygon/fill_between) — sin librerías
de terceros de tipo Sankey, consistente con el resto de `_regen/` (sin
kaleido, backend Agg).

Fuente de datos: _regen/out/efficiency_values.json (generado por
_regen/derive_efficiency_values.py — NO se recalculan valores aquí).

Genera en _regen/out/figuras/:
    FigS1_sankey_sierpinski.png  (fuente fuerte cercana, emisor intencional 3,3 GHz)
    FigS2_sankey_parche.png      (fuente fuerte cercana WiFi 2,45 GHz, parche FR-4)
    FigS3_sankey_flpda.png       (escenario TDT canónico @100 m, FLPDA)

Ejecutar: PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/sankey_figures.py
================================================================================
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import _regen.estilo as E

plt.rcParams.update(E.RC)

OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)

def _co(x, spec: str) -> str:
    """Formatea `x` con `spec` y coma decimal (convención es-CO del pipeline)."""
    return format(x, spec).replace(".", ",")


STAGE_LABELS_MODULAR = [r"$\eta_{rad}$", r"$\eta_{mm}$", r"$\eta_{imn}$", "PCE", r"$\eta_{PMIC}$"]
STAGE_KEYS_MODULAR = ["eta_rad", "eta_mm", "eta_imn", "PCE", "eta_pmic"]

# Co-diseño conjugado integrado (Sierpinski, parche): sin interfaz de 50 Ω,
# por eso NO hay eta_mm/eta_imn separados — eta_cm ya es la eficiencia de
# acople antena→diodo completa (ver _regen/derive_efficiency_values.py,
# decisión de modelado 1).
STAGE_LABELS_CONJUGADO = [r"$\eta_{cm}$", "PCE", r"$\eta_{PMIC}$"]
STAGE_KEYS_CONJUGADO = ["eta_cm", "PCE", "eta_pmic"]


def draw_sankey(ax_or_fig, stages: dict, color: str, loss_color: str = None):
    """
    Dibuja un Sankey estático de la cadena RF->DC sobre un Axes de matplotlib.

    Detecta automáticamente la arquitectura por las claves presentes en
    `stages`: si trae 'eta_cm' es co-diseño conjugado integrado (3 etapas,
    Sierpinski/parche); si trae 'eta_mm'/'eta_imn' es arquitectura modular de
    50 Ω (5 etapas, FLPDA/CANONICAL). No se asume una u otra a ciegas.

    Parámetros
    ----------
    ax_or_fig : matplotlib.axes.Axes donde dibujar.
    stages    : dict con los factores multiplicativos en [0,1] de la cadena
                aplicable (ver arriba) y opcionalmente 'P_in_uW'/'P_dc_uW'
                para las anotaciones de potencia absoluta.
    color     : color de la franja principal (flujo que sobrevive).
    loss_color: color de las cuñas de pérdida (default: gris/rojo tenue).

    Retorna el Axes (para encadenar título/leyenda).
    """
    ax = ax_or_fig
    loss_color = loss_color if loss_color is not None else E.COL["warn"]

    if "eta_cm" in stages:
        stage_labels, stage_keys = STAGE_LABELS_CONJUGADO, STAGE_KEYS_CONJUGADO
    else:
        stage_labels, stage_keys = STAGE_LABELS_MODULAR, STAGE_KEYS_MODULAR

    factors = [float(stages[k]) for k in stage_keys]
    n = len(factors)
    xs = np.arange(n + 1, dtype=float)

    # Fracción remanente acumulada (P_in = 100 %)
    cum = np.concatenate([[1.0], np.cumprod(factors)])
    pct = cum * 100.0

    # ── Franja principal (flujo que sobrevive) ────────────────────────────────
    deepest = 0.0
    for i in range(n):
        x0, x1 = xs[i], xs[i + 1]
        h0, h1 = cum[i] / 2.0, cum[i + 1] / 2.0
        poly = Polygon(
            [(x0, h0), (x1, h1), (x1, -h1), (x0, -h0)],
            closed=True, facecolor=color, edgecolor="none", alpha=0.85, zorder=3,
        )
        ax.add_patch(poly)

        # ── Cuña de pérdida (triángulo que se desprende hacia abajo) ─────────
        loss = cum[i] - cum[i + 1]
        if loss > 1e-6:
            wedge = Polygon(
                [(x0, -h0), (x1, -h1), (x1, -h1 - loss)],
                closed=True, facecolor=loss_color, edgecolor="none",
                alpha=0.22, zorder=2,
            )
            ax.add_patch(wedge)
            ax.annotate(
                f"−{_co(loss*100, '.1f')} pp",
                (x1, -(h1 + loss) - 0.02), ha="center", va="top",
                fontsize=7.2, color=loss_color, family=E.FONT,
            )
            deepest = max(deepest, h1 + loss)

        # Etiqueta del factor multiplicativo, encima del segmento
        ax.annotate(
            f"{stage_labels[i]} = {_co(factors[i], '.3f')}",
            (0.5 * (x0 + x1), max(h0, h1) + 0.035), ha="center", va="bottom",
            fontsize=8.3, color=E.INK, fontweight="bold", family=E.FONT,
        )

    # ── Etiquetas de nodo (porcentaje remanente) ──────────────────────────────
    # El nodo de entrada (100 %) es P_incidente en la arquitectura modular
    # (FLPDA, primer eslabón = eta_rad) y P_in de puerto en la conjugada.
    nombre_entrada = "P incidente" if "P_incidente_uW" in stages else "P_in"
    node_names = [nombre_entrada] + [""] * (n - 1) + ["P_DC"]
    for i, x in enumerate(xs):
        h = cum[i] / 2.0
        label = f"{_co(pct[i], '.2f')} %"
        if node_names[i]:
            label = f"{node_names[i]}\n{label}"
        ax.annotate(
            label, (x, h + 0.09), ha="center", va="bottom",
            fontsize=8.6 if node_names[i] else 7.6,
            fontweight="bold" if node_names[i] else "normal",
            color=E.INK, family=E.FONT,
        )
        ax.plot([x, x], [-h, h], color=E.LINE if hasattr(E, "LINE") else "#8a93a0",
                lw=0.9, alpha=0.6, zorder=4)

    # Potencias absolutas en los extremos, si se proveen — bajo TODAS las cuñas
    # de pérdida para no solaparse con sus etiquetas "-x.x pp".
    #
    # Referencia del nodo de entrada (100 %) según arquitectura:
    #  - Conjugada (Sierpinski/parche): P_in_uW = potencia en el PUERTO de
    #    antena (la referencia de eta_total = eta_cadena en esta arquitectura).
    #  - Modular (FLPDA): P_incidente_uW = potencia RF ANTES de la antena; el
    #    puerto de antena queda TRAS el primer eslabón (eta_rad). Se anota
    #    también el nodo intermedio "P puerto" para que las franjas × P_incidente
    #    reproduzcan exactamente el P_DC (auto-consistencia, corrección K1).
    y_power_label = -(deepest + 0.16)
    P_entrada = stages.get("P_incidente_uW", stages.get("P_in_uW"))
    if P_entrada is not None:
        label0 = f"{_co(P_entrada, '.4g')} µW"
        if "P_incidente_uW" in stages:
            label0 = "P incidente\n" + label0
        ax.annotate(label0, (xs[0], y_power_label),
                    ha="center", va="top", fontsize=7.6, color=E.MUTE, family=E.FONT)
    # Nodo intermedio (solo modular): potencia en el puerto de antena tras eta_rad
    if "P_incidente_uW" in stages and "P_in_uW" in stages:
        ax.annotate(f"P puerto de antena\n{_co(stages['P_in_uW'], '.4g')} µW",
                    (xs[1], y_power_label), ha="center", va="top",
                    fontsize=7.2, color=E.MUTE, family=E.FONT)
    if "P_dc_uW" in stages:
        ax.annotate(f"{_co(stages['P_dc_uW'], '.4g')} µW DC", (xs[-1], y_power_label),
                    ha="center", va="top", fontsize=7.6, color=E.MUTE, family=E.FONT)

    ax.set_xlim(-0.35, n + 0.35)
    ymax_top = cum[0] / 2.0 + 0.24
    ymax_bot = deepest + 0.34
    ax.set_ylim(-ymax_bot - 0.05, ymax_top + 0.05)
    ax.axis("off")
    return ax


def _save(fig, name):
    p = os.path.join(OUT_F, name)
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ]", name)


def _figura(escenario: dict, color: str, titulo: str, nombre_archivo: str):
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    draw_sankey(ax, escenario, color)
    eta_total_pct = float(escenario["eta_total"]) * 100.0
    ax.set_title(f"{titulo}\n$\\eta_{{total}}$ = {_co(eta_total_pct, '.2f')} %",
                 fontsize=11.5, pad=10)
    _save(fig, nombre_archivo)


def main():
    with open(os.path.join(os.path.dirname(__file__), "out", "efficiency_values.json"),
              encoding="utf-8") as fh:
        data = json.load(fh)

    # FigS1 — Sierpinski, escenario fuente fuerte cercana (emisor intencional en banda)
    _figura(
        data["sierpinski"]["fuente_fuerte_cercana"], E.COL["A"],
        "Sankey RF→DC — Antena Sierpinski\nFuente fuerte cercana (emisor intencional 3,3 GHz, 20 dBm @ 0,4 m)",
        "FigS1_sankey_sierpinski.png",
    )

    # FigS2 — Parche FR-4, escenario WiFi cercano
    _figura(
        data["parche_FR4"]["fuente_fuerte_wifi"], E.COL["accent"],
        "Sankey RF→DC — Parche microcinta (FR-4)\nFuente fuerte cercana (WiFi/router, 20 dBm @ 0,4 m, 2,45 GHz)",
        "FigS2_sankey_parche.png",
    )

    # FigS3 — FLPDA, escenario TDT canónico @100 m
    _figura(
        data["flpda"]["tdt_100m_canonico"], E.COL["B"],
        "Sankey RF→DC — FLPDA Koch\nFuente firme distante (TDT DVB-T, Cerro Nutibara @ 100 m, 550 MHz)",
        "FigS3_sankey_flpda.png",
    )


if __name__ == "__main__":
    main()
