# -*- coding: utf-8 -*-
"""
================================================================================
Figuras de caracterización — Carta de Smith y cortes E/H (Etapa G0)
================================================================================
Retícula de Smith dibujada a mano (círculos de resistencia constante y arcos
de reactancia constante) más el lugar geométrico Γ(f)=(Z−50)/(Z+50) de cada
antena en su banda de barrido, y una figura compuesta de 2 paneles por antena:
    (a) cortes E/H polares @ f0 (de core.patterns.pattern_cuts)
    (b) Carta de Smith con el lugar de Z y las resonancias marcadas

Genera en _regen/out/figuras/ (300 dpi):
    FigD1_caracterizacion_sierpinski.png
    FigD2_caracterizacion_parche.png   (FR4; lugar RT5880 en gris si no satura)
    FigD3_caracterizacion_flpda.png

Ejecutar:
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/characterization_figures.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import _regen.estilo as E
from core.patch import MicrostripPatchAntenna
from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from core.patterns import pattern_cuts
from configs.parametros import FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ

plt.rcParams.update(E.RC)
C_A, C_B, C_MODEL, C_WARN, C_GRIS = E.COL["A"], E.COL["B"], E.COL["model"], E.COL["warn"], E.COL["grid"]

OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)


def _save(fig, name):
    p = os.path.join(OUT_F, name)
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ]", name)


# ═════════════════════════════════════════════════════════════════════════════
#  CARTA DE SMITH — retícula dibujada a mano
# ═════════════════════════════════════════════════════════════════════════════

def smith_grid(ax, r_list=(0.2, 0.5, 1, 2, 5), x_list=(0.2, 0.5, 1, 2, 5)):
    """Retícula de Smith: círculos r=cte y arcos x=cte (gris fino) + círculo
    unitario y eje real."""
    from matplotlib.patches import Circle

    for r in r_list:
        c, rad = r / (r + 1.0), 1.0 / (r + 1.0)
        ax.add_patch(Circle((c, 0.0), rad, fill=False, color=C_GRIS, lw=0.55, zorder=0))
        ax.text(c + rad - 0.015, 0.012, f"{r:g}", fontsize=5.6, color="0.5",
                ha="right", va="bottom", zorder=1)

    r_sweep = np.linspace(0.0, 200.0, 800)
    for x in x_list:
        for xx in (x, -x):
            z = r_sweep + 1j * xx
            gam = (z - 1.0) / (z + 1.0)
            mask = np.abs(gam) <= 1.0 + 1e-9
            ax.plot(gam.real[mask], gam.imag[mask], color=C_GRIS, lw=0.55, zorder=0)

    ax.add_patch(Circle((0.0, 0.0), 1.0, fill=False, color=E.MUTE, lw=1.1, zorder=2))
    ax.plot([-1, 1], [0, 0], color=E.MUTE, lw=0.8, zorder=2)
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    ax.set_aspect("equal")
    ax.axis("off")


def gamma_sweep(obj, f_lo, f_hi, n=400, Z0=50.0, label=""):
    """
    Γ(f) = (Z−Z0)/(Z+Z0) sobre un barrido lineal [f_lo, f_hi].
    Verifica |Γ|≤1; si algún punto lo viola (modelo con Z de parte real
    negativa por combinación de ramas), se clipea a |Γ|=1 conservando la
    fase, y se reporta por consola.
    """
    fs = np.linspace(f_lo, f_hi, n)
    Z = np.atleast_1d(obj.impedance(fs))
    gam = (Z - Z0) / (Z + Z0)
    mag = np.abs(gam)
    over = mag > 1.0 + 1e-9
    if np.any(over):
        print(f"[WARN] {label}: |Gamma|>1 en {int(over.sum())} punto(s) "
              f"(max={mag.max():.4f}) -> clip aplicado a |Gamma|=1")
        gam = gam.copy()
        gam[over] = gam[over] / mag[over]
    return fs, gam, bool(np.any(over))


def _fmt_ghz(f_hz: float, dec: int = 2) -> str:
    """Frecuencia en GHz con coma decimal (convención del pipeline de figuras)."""
    return f"{f_hz/1e9:.{dec}f}".replace(".", ",") + " GHz"


def _mark_resonances(ax, obj, freqs_hz, Z0=50.0, color=E.INK, marker="o", fs=6.6):
    """Marca cada frecuencia con un punto y su etiqueta. La etiqueta se coloca
    HACIA EL INTERIOR de la carta (dirección punto→centro, con alternancia
    vertical para separar puntos próximos), de modo que nunca quede recortada
    en el borde del lienzo aunque el punto caiga junto al círculo unitario."""
    n = len(list(freqs_hz))
    for i, f in enumerate(freqs_hz):
        z = complex(obj.impedance(f))
        g = (z - Z0) / (z + Z0)
        if abs(g) > 1.0:
            g = g / abs(g)
        ax.plot(g.real, g.imag, marker=marker, ms=4.2, color=color,
                mec="white", mew=0.5, zorder=5)
        # Vector unitario punto→centro (si el punto está casi en el centro,
        # empuja hacia arriba-izquierda por defecto).
        mag = abs(g)
        if mag > 0.05:
            ux, uy = -g.real / mag, -g.imag / mag
        else:
            ux, uy = -0.7, 0.7
        # Desplazamiento en puntos: hacia adentro + escalonado vertical por
        # índice, para que etiquetas de resonancias próximas no se pisen
        # aunque sus puntos caigan casi superpuestos en la carta.
        dy_stagger = (i - (n - 1) / 2.0) * 13.0
        off = (ux * 14.0, uy * 14.0 + dy_stagger)
        ha = "left" if ux >= 0 else "right"
        ax.annotate(_fmt_ghz(f), (g.real, g.imag), textcoords="offset points",
                    xytext=off, fontsize=fs, color=color, zorder=6, ha=ha,
                    bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                              edgecolor="none", alpha=0.65))


# ═════════════════════════════════════════════════════════════════════════════
#  CORTES E/H POLARES
# ═════════════════════════════════════════════════════════════════════════════

def panel_polar(ax, pat, color_e, color_h, titulo="(a) Cortes E/H @ f0"):
    theta_rad = np.radians(pat["theta_deg"])
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.plot(theta_rad, pat["E_plane_dB"], color=color_e, lw=1.8,
            label=f"Plano E (HPBW={pat['hpbw_e_deg']:.0f}°)")
    ax.plot(theta_rad, pat["H_plane_dB"], color=color_h, lw=1.6, ls="--",
            label=f"Plano H (HPBW={pat['hpbw_h_deg']:.0f}°)")
    ax.set_rlim(-30, 0)
    ax.set_rticks([-30, -20, -10, 0])
    ax.set_thetagrids(range(0, 360, 30))
    ax.tick_params(labelsize=6.5)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.32), fontsize=7.2, frameon=True)
    ax.set_title(titulo, fontsize=9.5, pad=10)


# ═════════════════════════════════════════════════════════════════════════════
#  FigD1 — Sierpinski
# ═════════════════════════════════════════════════════════════════════════════

def figD1_sierpinski():
    f0 = 1.84e9
    ant = FractalAntenna("sierpinski", iterations=3, base_freq=f0)
    pat = pattern_cuts("sierpinski", f0, base_freq=f0, iterations=3)

    fig = plt.figure(figsize=(14 / 2.54, 7.6 / 2.54))
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)

    panel_polar(ax1, pat, C_A, E.MUTE)

    smith_grid(ax2)
    fs, gam, clipped = gamma_sweep(ant, 1.0e9, 6.0e9, label="Sierpinski")
    ax2.plot(gam.real, gam.imag, color=C_A, lw=1.7, label="Γ(f) 1–6 GHz")
    _mark_resonances(ax2, ant, [f for f in ant.fractal_resonances_hz if f < 6e9], color=C_A)
    ax2.set_title("(b) Carta de Smith", fontsize=10)
    ax2.legend(loc="upper left", fontsize=7.2)

    fig.suptitle("Caracterización — Sierpinski Gasket it.3 (Escenario A)", fontsize=11, y=1.10)
    _save(fig, "FigD1_caracterizacion_sierpinski.png")


# ═════════════════════════════════════════════════════════════════════════════
#  FigD2 — Parche (FR4; RT5880 en gris si no satura)
# ═════════════════════════════════════════════════════════════════════════════

def figD2_parche():
    f0 = 2.45e9
    ant_fr4 = MicrostripPatchAntenna(f0, "FR4")
    pat = pattern_cuts("patch", f0, substrate="FR4", f0_hz=f0)

    fig = plt.figure(figsize=(14 / 2.54, 7.6 / 2.54))
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)

    panel_polar(ax1, pat, C_A, E.MUTE)

    smith_grid(ax2)
    fs, gam, clipped = gamma_sweep(ant_fr4, 1.0e9, 6.0e9, label="Parche FR4")
    ax2.plot(gam.real, gam.imag, color=C_A, lw=1.7, label="Γ(f) FR-4, 1–6 GHz")
    _mark_resonances(ax2, ant_fr4, ant_fr4.resonances(), color=C_A)

    # Lugar RT5880 en gris claro si no satura el gráfico (queda dentro de la retícula)
    ant_rt = MicrostripPatchAntenna(f0, "RT5880")
    fs_rt, gam_rt, clipped_rt = gamma_sweep(ant_rt, 1.0e9, 6.0e9, label="Parche RT5880")
    if np.max(np.abs(gam_rt)) <= 1.0 + 1e-6:
        ax2.plot(gam_rt.real, gam_rt.imag, color="0.72", lw=1.3, ls="--",
                 label="Γ(f) RT5880 (referencia)", zorder=1)

    ax2.set_title("(b) Carta de Smith", fontsize=10)
    ax2.legend(loc="upper left", fontsize=6.8)

    fig.suptitle("Caracterización — Parche microcinta @2,45 GHz (FR-4)", fontsize=11, y=1.10)
    _save(fig, "FigD2_caracterizacion_parche.png")


# ═════════════════════════════════════════════════════════════════════════════
#  FigD3 — FLPDA Koch
# ═════════════════════════════════════════════════════════════════════════════

def figD3_flpda():
    f0 = 550e6
    ant = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                      f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    pat = pattern_cuts("flpda", f0, tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                        f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)

    fig = plt.figure(figsize=(14 / 2.54, 7.6 / 2.54))
    ax1 = fig.add_subplot(1, 2, 1, projection="polar")
    ax2 = fig.add_subplot(1, 2, 2)

    panel_polar(ax1, pat, C_B, E.MUTE)

    smith_grid(ax2)
    fs, gam, clipped = gamma_sweep(ant, 0.4e9, 1.0e9, label="FLPDA")
    ax2.plot(gam.real, gam.imag, color=C_B, lw=1.7, label="Γ(f) 0,4–1,0 GHz")
    bandas_todas = sorted({f for f in ant.resonant_freqs if ant.f_low <= f <= ant.f_high})
    # Solo se anotan extremos y centro de banda: los 7 dipolos activos caen muy
    # próximos entre sí en la carta (banda estrecha en términos de Γ) y anotar
    # los 7 satura la figura sin aportar información adicional.
    idx = sorted({0, len(bandas_todas) // 2, len(bandas_todas) - 1})
    bandas = [bandas_todas[i] for i in idx]
    _mark_resonances(ax2, ant, bandas, color=C_B, fs=6.4)
    ax2.set_title("(b) Carta de Smith", fontsize=10)
    ax2.legend(loc="upper left", fontsize=7.2)

    fig.suptitle("Caracterización — FLPDA Koch it.2 (Escenario B)", fontsize=11, y=1.10)
    _save(fig, "FigD3_caracterizacion_flpda.png")


if __name__ == "__main__":
    figD1_sierpinski()
    figD2_parche()
    figD3_flpda()
    print("\nListo — figuras de caracterización generadas.")
