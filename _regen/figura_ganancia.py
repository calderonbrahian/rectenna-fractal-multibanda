# -*- coding: utf-8 -*-
"""
================================================================================
FIGURA: Ganancia realizada frente a la frecuencia — los dos escenarios
================================================================================
El objetivo específico 1 del trabajo compromete la caracterización de la
ganancia realizada de ambas geometrías. Hasta ahora esa magnitud solo existía
como cifra suelta en la prosa y en las tablas; esta figura la muestra.

Un solo panel por escenario, trazados con la misma función para que la
comparación sea legítima: mismo tipo de eje, misma banda de incertidumbre
(±1,5 dBi, la declarada en § 1.4) y mismo código de color.

    Escenario A · Sierpinski  →  oro   E.COL["A"]
    Escenario B · FLPDA Koch  →  verde E.COL["B"]

La ganancia realizada incluye la eficiencia de radiación: G = η_rad · D, de
modo que el castigo del FR-4 a alta frecuencia se ve directamente en la curva.

Genera en _regen/out/figuras/:
    FigSym_ganancia_AB.png

Ejecutar: PYTHONIOENCODING=utf-8 python _regen/figura_ganancia.py
================================================================================
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import _regen.estilo as E
import core.multiband as mb
from core.flpda import FLPDA_Koch

plt.rcParams.update(E.RC)

OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)

C_A, C_B = E.COL["A"], E.COL["B"]
C_GRIS = E.COL["grid"]
INCERT_DBI = 1.5          # incertidumbre declarada del modelo analítico (§ 1.4)


def _co(x, spec=".2f"):
    return format(x, spec).replace(".", ",")


def _panel(ax, fs_hz, antena, color, titulo, marcas, xlabel):
    """Traza ganancia realizada con su banda de incertidumbre. Idéntica para A y B."""
    g = np.array([antena.gain_dBi(f) for f in fs_hz])
    x = fs_hz / 1e9
    ax.fill_between(x, g - INCERT_DBI, g + INCERT_DBI,
                    color=color, alpha=0.16, lw=0,
                    label=f"±{_co(INCERT_DBI, '.1f')} dBi (incertidumbre del modelo)")
    ax.plot(x, g, color=color, lw=2.3, label="Ganancia realizada G = η_rad · D")
    ax.axhline(0.0, color=C_GRIS, ls=":", lw=0.9)

    for etiqueta, f_hz in marcas.items():
        gm = antena.gain_dBi(f_hz)
        ax.plot(f_hz / 1e9, gm, "o", color=color, ms=4.5, zorder=5,
                markeredgecolor="white", markeredgewidth=0.8)
        ax.annotate(f"{etiqueta}\n{_co(gm)} dBi", (f_hz / 1e9, gm),
                    textcoords="offset points", xytext=(0, 9), ha="center",
                    fontsize=6.6, color=E.INK)

    ax.set_title(titulo, fontsize=9.6, pad=7)
    ax.set_xlabel(xlabel, fontsize=8.6)
    ax.set_ylabel("Ganancia realizada (dBi)", fontsize=8.6)
    ax.tick_params(labelsize=7.8)
    ax.grid(True, ls=":", lw=0.6, color=C_GRIS, alpha=0.55)
    ax.legend(fontsize=7.0, loc="lower left", framealpha=0.92)
    return g


def main():
    ant_a, _, _ = mb.build_default()
    ant_b = FLPDA_Koch()

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.5))

    # ── (a) Escenario A: las siete bandas urbanas objetivo ────────────────────
    fs_a = np.linspace(1.70e9, 6.10e9, 900)
    marcas_a = {"GSM1800": 1.84e9, "5G-3,5": 3.30e9, "WiFi 5,8": 5.80e9}
    g_a = _panel(axes[0], fs_a, ant_a, C_A,
                 "(a) Escenario A · Sierpinski it. 3", marcas_a,
                 "Frecuencia (GHz)")
    axes[0].set_ylim(-5.0, 4.2)

    # ── (b) Escenario B: la banda de diseño de la FLPDA ───────────────────────
    # Solo la banda de diseño: fuera de ella el modelo de Carrel no aplica y
    # devolvería cero, lo que dibujaría un acantilado sin sentido físico.
    fs_b = np.linspace(0.47e9, 0.90e9, 900)
    marcas_b = {"TDT 550": 0.550e9, "LTE 700": 0.700e9, "GSM 850": 0.850e9}
    g_b = _panel(axes[1], fs_b, ant_b, C_B,
                 "(b) Escenario B · FLPDA Koch it. 2", marcas_b,
                 "Frecuencia (GHz)")
    axes[1].set_ylim(2.4, 7.6)

    _p = os.path.join(OUT_F, "FigSym_ganancia_AB.png")
    fig.savefig(_p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ] FigSym_ganancia_AB.png")

    print()
    print("── Cifras para la nota de figura (desde el modelo) ──")
    print(f"  A · G(1,84 GHz) = {ant_a.gain_dBi(1.84e9):.2f} dBi   "
          f"G(5,80 GHz) = {ant_a.gain_dBi(5.80e9):.2f} dBi")
    print(f"  A · rango en 1,7–6,1 GHz: {g_a.min():.2f} a {g_a.max():.2f} dBi")
    print(f"  A · η_rad: {ant_a.eta_rad(1.84e9):.3f} (1,84 GHz) → "
          f"{ant_a.eta_rad(5.80e9):.3f} (5,80 GHz)")
    fs_band = np.linspace(0.47e9, 0.90e9, 600)
    gb = np.array([ant_b.gain_dBi(f) for f in fs_band])
    print(f"  B · G(550 MHz) = {ant_b.gain_dBi(0.55e9):.2f} dBi   "
          f"media en 470–900 MHz = {gb.mean():.2f} dBi   "
          f"rango {gb.min():.2f}–{gb.max():.2f} dBi")
    print(f"  B · η_rad: {ant_b.eta_rad(0.47e9):.3f} (470 MHz) → "
          f"{ant_b.eta_rad(0.90e9):.3f} (900 MHz)")


if __name__ == "__main__":
    main()
