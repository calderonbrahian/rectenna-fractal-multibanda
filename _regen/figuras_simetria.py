# -*- coding: utf-8 -*-
"""
================================================================================
FIGURAS DE SIMETRÍA ENTRE ESCENARIOS (A · Sierpinski  vs  B · FLPDA Koch)
================================================================================
El documento compara DOS estrategias de captación bajo DOS escenarios. Cada
tipo de análisis debe existir para ambos y verse igual: mismo tipo de eje,
mismos estadísticos, misma tipografía, mismo código de color.

    Escenario A · Sierpinski  →  oro   E.COL["A"]
    Escenario B · FLPDA Koch  →  verde E.COL["B"]

Este módulo define UNA función por tipo de figura y la aplica a los dos
escenarios, de modo que la simetría visual no dependa de que dos generadores
distintos coincidan por casualidad.

Genera en _regen/out/figuras/:
    FigSym_sankey_A.png        Sankey de la cadena RF→DC del Escenario A
                               (cosecha agregada de las 7 bandas urbanas).
                               El par de esta figura es FigS3_sankey_flpda.png,
                               que ya sale de sankey_figures.draw_sankey().
    FigSym_montecarlo_A.png    Monte Carlo del Escenario A
    FigSym_montecarlo_B.png    Monte Carlo del Escenario B (mismo trazo que A)
    FigSym_comparativa_AB.png  Figura comparativa entre escenarios (3 paneles)

Fuente de datos: core/ y _regen/out/efficiency_values.json. Aquí no se fija
ningún valor a mano.

Ejecutar: PYTHONIOENCODING=utf-8 python _regen/figuras_simetria.py
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

import _regen.estilo as E
from _regen.sankey_figures import draw_sankey

plt.rcParams.update(E.RC)

OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)

C_A = E.COL["A"]        # Escenario A · Sierpinski
C_B = E.COL["B"]        # Escenario B · FLPDA Koch
C_ROJO = E.COL["warn"]
C_GRIS = E.COL["grid"]


def _co(x, spec: str) -> str:
    """Formatea con coma decimal y espacio fino de millar (convención es-CO)."""
    s = format(x, spec)
    if "," in s:                       # el spec ya pidió separador de millar
        ent, _, dec = s.partition(".")
        ent = ent.replace(",", " ")
        return ent + ("," + dec if dec else "")
    return s.replace(".", ",")


def _save(fig, name):
    p = os.path.join(OUT_F, name)
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ]", name)


def _load_eff():
    with open(os.path.join(os.path.dirname(__file__), "out", "efficiency_values.json"),
              encoding="utf-8") as fh:
        return json.load(fh)


# ══════════════════════════════════════════════════════════════════════════════
# 1) SANKEY DEL ESCENARIO A  (par simétrico de FigS3_sankey_flpda.png)
# ══════════════════════════════════════════════════════════════════════════════
def sankey_escenario_A(eff):
    """Sankey de la cadena RF→DC del Escenario A, cosecha agregada multibanda.

    Usa la MISMA rutina de dibujo que el Sankey del Escenario B
    (sankey_figures.draw_sankey), que detecta la arquitectura por las claves
    del diccionario: 'eta_cm' → co-diseño conjugado integrado (3 eslabones).
    """
    esc = eff["sierpinski"]["ambiente_urbano_difuso"]
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    draw_sankey(ax, esc, C_A)
    ax.set_title(
        "Sankey RF→DC — Antena Sierpinski (Escenario A)\n"
        "Ambiente urbano difuso, cosecha agregada de 7 bandas (1,8–5,8 GHz)\n"
        f"$\\eta_{{total}}$ = {_co(esc['eta_total'] * 100, '.2f')} %",
        fontsize=11.5, pad=10)
    _save(fig, "FigSym_sankey_A.png")
    return esc


# ══════════════════════════════════════════════════════════════════════════════
# 2) MONTE CARLO — una sola función, los dos escenarios
# ══════════════════════════════════════════════════════════════════════════════
def _montecarlo_panel(samples, canon_uw, color, subtitulo, archivo, fmt_uw=".2f"):
    """Histograma Monte Carlo con eje logarítmico y estadísticos homogéneos.

    Se usa idéntica para A y B: mismo tipo de eje, mismos estadísticos
    (mediana, p5, p95, CV) y misma leyenda. La única diferencia admitida es el
    color del escenario y los valores.
    """
    s = np.asarray([v for v in samples if v > 0], dtype=float)
    med = float(np.median(s))
    p5, p95 = float(np.percentile(s, 5)), float(np.percentile(s, 95))
    cv = float(np.std(s) / np.mean(s) * 100.0)

    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    lo, hi = np.percentile(s, 0.2), np.percentile(s, 99.8)
    bins = np.logspace(np.log10(lo), np.log10(hi), 46)
    ax.hist(s, bins=bins, color=color, alpha=0.82, edgecolor="white", lw=0.3)
    ax.set_xscale("log")

    ax.axvline(med, color=E.INK, lw=1.8,
               label=f"Mediana {_co(med, fmt_uw)} µW")
    ax.axvline(p5, color=E.MUTE, ls=":", lw=1.3,
               label=f"p5 {_co(p5, fmt_uw)} µW")
    ax.axvline(p95, color=E.MUTE, ls="--", lw=1.3,
               label=f"p95 {_co(p95, fmt_uw)} µW")
    ax.axvline(canon_uw, color=C_ROJO, ls="-.", lw=1.5,
               label=f"Caso nominal {_co(canon_uw, fmt_uw)} µW")

    ax.set_xlabel("Potencia DC entregada (µW)")
    ax.set_ylabel("Frecuencia")
    ax.legend(loc="upper right", fontsize=8, framealpha=0.92)
    ax.set_title(f"{subtitulo}\n"
                 f"n = 10 000 realizaciones · CV = {_co(cv, '.0f')} %",
                 fontsize=10.8, pad=8)
    _save(fig, archivo)
    return {"mediana": med, "p5": p5, "p95": p95, "cv_pct": cv, "samples": s}


def montecarlo_ambos(eff):
    """Monte Carlo de los dos escenarios con el mismo trazo."""
    # ── Escenario A: incertidumbre dominante = nivel RF ambiental (±5 dB) ──────
    import core.multiband as mb
    ant, rec, imn = mb.build_default()
    resA = mb.monte_carlo_harvest(ant, rec, imn)
    a = _montecarlo_panel(
        resA["samples"], eff["sierpinski"]["ambiente_urbano_difuso"]["P_dc_uW"],
        C_A, "Escenario A · Sierpinski, cosecha urbana agregada",
        "FigSym_montecarlo_A.png", fmt_uw=".2f")

    # ── Escenario B: incertidumbre dominante = EIRP y distancia al transmisor ─
    from analysis.avanzado import run_monte_carlo
    mc = run_monte_carlo(n_samples=10000)
    b = _montecarlo_panel(
        mc["samples"], eff["flpda"]["tdt_100m_canonico"]["P_dc_uW"],
        C_B, "Escenario B · FLPDA Koch, caso TDT del Cerro Nutibara",
        "FigSym_montecarlo_B.png", fmt_uw=",.0f")
    return a, b


# ══════════════════════════════════════════════════════════════════════════════
# 3) FIGURA COMPARATIVA ENTRE ESCENARIOS
# ══════════════════════════════════════════════════════════════════════════════
def comparativa_AB(eff, mcA, mcB):
    """Comparación gráfica de las dos estrategias en un solo cuadro.

    (a) Cascada de eficiencia sobre eslabones homólogos. Para poder superponer
        las dos cadenas se agrupa el acople del Escenario B (η_mm · η_IMN) en
        un único eslabón «acople antena→diodo», que es exactamente lo que
        η_cm representa en el Escenario A. Quedan tres eslabones comparables.
    (b) Potencia DC entregada frente al consumo medio del nodo de referencia.
    (c) Dispersión relativa del resultado (Monte Carlo normalizado a su
        mediana), que es donde las dos estrategias más se separan.
    """
    A = eff["sierpinski"]["ambiente_urbano_difuso"]
    B = eff["flpda"]["tdt_100m_canonico"]

    # Umbral del nodo de referencia: consumo medio del perfil LoRa SF12 al 1 %
    # de ciclo útil, calculado por el mismo módulo que alimenta la Tabla 2.
    from core.lora_budget import LORA_PROFILES, avg_power_uw
    P_AVG_MIN_UW = avg_power_uw(LORA_PROFILES["LoRa SF12 BW125 (1% DC)"])

    facA = [A["eta_cm"], A["PCE"], A["eta_pmic"]]
    facB = [B["eta_mm"] * B["eta_imn"], B["PCE"], B["eta_pmic"]]
    etapas = ["Puerto de\nantena", "Acople\nantena→diodo", "Rectificación", "Gestión\n(PMIC)"]

    cumA = np.concatenate([[100.0], 100.0 * np.cumprod(facA)])
    cumB = np.concatenate([[100.0], 100.0 * np.cumprod(facB)])

    # Proporción pensada para reproducirse a 14,5 cm de ancho en el documento:
    # el panel ancho a la izquierda y los dos de lectura rápida apilados.
    fig = plt.figure(figsize=(7.5, 4.9))
    # E.RC activa constrained_layout: aquí wspace/hspace son fracción del alto
    # del eje, no pulgadas — valores pequeños o los paneles se comprimen.
    gs = fig.add_gridspec(2, 2, width_ratios=[1.30, 0.80],
                          wspace=0.05, hspace=0.14)

    # ── (a) cascadas superpuestas sobre eslabones homólogos ──────────────────
    ax = fig.add_subplot(gs[:, 0])
    xs = np.arange(len(etapas), dtype=float)
    xs_step = np.append(xs, xs[-1] + 0.62)          # meseta del último eslabón
    for cum, col, lab, dy in ((cumA, C_A, "A · Sierpinski", -13),
                              (cumB, C_B, "B · FLPDA Koch", 8)):
        ax.step(xs_step, np.append(cum, cum[-1]), where="post",
                color=col, lw=2.4, label=lab, zorder=3)
        ax.fill_between(xs_step, np.append(cum, cum[-1]), 1.6, step="post",
                        color=col, alpha=0.10, zorder=1)
        for x, v in zip(xs, cum):
            ax.annotate(f"{_co(v, '.1f')} %", (x + 0.06, v),
                        textcoords="offset points", xytext=(0, dy),
                        ha="left", fontsize=7.2, color=col,
                        fontweight="bold", zorder=4)
    ax.set_xticks(xs)
    ax.set_xticklabels(etapas, fontsize=7.4)
    ax.set_xlim(-0.18, xs[-1] + 0.66)
    ax.set_yscale("log")
    ax.set_ylim(1.6, 420)
    ax.set_yticks([2, 5, 10, 20, 50, 100])
    ax.set_yticklabels(["2", "5", "10", "20", "50", "100"], fontsize=7.6)
    ax.set_ylabel("Energía conservada (%, escala log)", fontsize=8.6)
    ax.set_title("(a) En qué eslabón se pierde la energía", fontsize=9.4, pad=6)
    ax.legend(fontsize=7.8, loc="upper right", framealpha=0.92, handlelength=1.6)
    ax.grid(True, axis="y", ls=":", lw=0.6, color=C_GRIS, alpha=0.55)

    # ── (b) potencia DC entregada frente al consumo del nodo ─────────────────
    ax = fig.add_subplot(gs[0, 1])
    pdc = [A["P_dc_uW"], B["P_dc_uW"]]
    bars = ax.bar(["A", "B"], pdc, color=[C_A, C_B], width=0.55, alpha=0.9)
    ax.set_yscale("log")
    ax.set_ylim(0.8, 2.2e4)
    ax.axhline(P_AVG_MIN_UW, color=C_ROJO, ls="--", lw=1.3, zorder=4)
    # Debajo de la línea: encima chocaría con la etiqueta de la barra del B.
    ax.text(0.5, P_AVG_MIN_UW / 1.7,
            f"consumo del nodo · {_co(P_AVG_MIN_UW, '.1f')} µW",
            ha="center", va="top", fontsize=7.0, color=C_ROJO,
            fontweight="bold", zorder=5)
    for bar, v in zip(bars, pdc):
        veredicto = "cubre" if v >= P_AVG_MIN_UW else "no cubre"
        ax.annotate(f"{_co(v, ',.0f') if v >= 100 else _co(v, '.2f')} µW\n({veredicto})",
                    (bar.get_x() + bar.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 3),
                    ha="center", fontsize=7.4, fontweight="bold", color=E.INK)
    ax.tick_params(labelsize=7.6)
    ax.set_ylabel("P_DC (µW, log)", fontsize=8.2)
    ax.set_title("(b) ¿Alcanza para el nodo?", fontsize=9.4, pad=6)
    ax.grid(True, axis="y", ls=":", lw=0.6, color=C_GRIS, alpha=0.55)

    # ── (c) dispersión relativa del resultado ────────────────────────────────
    ax = fig.add_subplot(gs[1, 1])
    relA = mcA["samples"] / mcA["mediana"]
    relB = mcB["samples"] / mcB["mediana"]
    bp = ax.boxplot([relA, relB], tick_labels=["A", "B"], widths=0.48,
                    showfliers=False, patch_artist=True, whis=(5, 95))
    for patch, col in zip(bp["boxes"], [C_A, C_B]):
        patch.set_facecolor(col); patch.set_alpha(0.65); patch.set_edgecolor(col)
    for elem in ("whiskers", "caps", "medians"):
        for art in bp[elem]:
            art.set_color(E.INK); art.set_linewidth(1.1)
    ax.set_yscale("log")
    ax.set_ylim(4e-3, 3e3)
    ax.axhline(1.0, color=C_GRIS, ls=":", lw=1.0)
    for i, (mc, col) in enumerate(((mcA, C_A), (mcB, C_B)), start=1):
        ax.annotate(f"CV\n{_co(mc['cv_pct'], '.0f')} %", (i, 3e2),
                    ha="center", va="center", fontsize=7.0,
                    color=col, fontweight="bold")
    ax.tick_params(labelsize=7.6)
    ax.set_ylabel("P_DC / mediana", fontsize=8.2)
    ax.set_title("(c) ¿Qué tan predecible es?", fontsize=9.4, pad=6)
    ax.grid(True, axis="y", ls=":", lw=0.6, color=C_GRIS, alpha=0.55)

    _save(fig, "FigSym_comparativa_AB.png")
    return {"cumA": cumA.tolist(), "cumB": cumB.tolist(),
            "P_dc": pdc, "P_avg_min_uW": P_AVG_MIN_UW}


def main():
    eff = _load_eff()
    escA = sankey_escenario_A(eff)
    mcA, mcB = montecarlo_ambos(eff)
    comp = comparativa_AB(eff, mcA, mcB)

    print()
    print("── Valores para las notas de figura (recalculados desde el modelo) ──")
    print(f"  A · P_in agregada     = {escA['P_in_uW']:.2f} µW")
    print(f"  A · eta_cm/PCE/PMIC   = {escA['eta_cm']:.4f} / {escA['PCE']:.4f} / {escA['eta_pmic']:.3f}")
    print(f"  A · P_dc              = {escA['P_dc_uW']:.4f} µW   eta_total = {escA['eta_total']*100:.2f} %")
    print(f"  A · MC mediana/p5/p95 = {mcA['mediana']:.3f} / {mcA['p5']:.3f} / {mcA['p95']:.2f} µW · CV = {mcA['cv_pct']:.0f} %")
    print(f"  B · MC mediana/p5/p95 = {mcB['mediana']:.1f} / {mcB['p5']:.1f} / {mcB['p95']:.1f} µW · CV = {mcB['cv_pct']:.0f} %")
    print(f"  Comparativa cascada A = {[round(v,2) for v in comp['cumA']]}")
    print(f"  Comparativa cascada B = {[round(v,2) for v in comp['cumB']]}")
    print(f"  Umbral del nodo       = {comp['P_avg_min_uW']} µW")


if __name__ == "__main__":
    main()
