# -*- coding: utf-8 -*-
"""
Figuras del ESTUDIO COMPARATIVO antena × sustrato (etapa F0 del pivote).
ADITIVO: no toca las figuras existentes. Usa la identidad visual única
(_regen/estilo.py): tipografía, paleta y semántica de color compartidas.

Genera en _regen/out/figuras/ (300 dpi, fondo blanco):
  FigP1_geometria_parche.png     — parche rectangular acotado (W, L, h, inset), FR4.
  FigP2_s11_parche_sustratos.png — S11(f) 1–6 GHz del parche FR4 vs RT5880.
  FigP3_comparativa_antenas.png  — barras: ganancia [dBi] y η_rad [%] por antena.

Ejecutar:
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/comparative_figures.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

import _regen.estilo as E
from core.patch import MicrostripPatchAntenna
from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from configs.parametros import (
    FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)

plt.rcParams.update(E.RC)

# Colores: Sierpinski/A = oro; FLPDA/B = verde; parche = teal (accent) / violeta (aux)
C_A, C_B = E.COL["A"], E.COL["B"]
C_PATCH_FR4, C_PATCH_RT = E.COL["accent"], E.COL["aux"]
C_ROJO, C_INK, C_MUTE = E.COL["warn"], E.INK, E.MUTE

F0_PATCH = 2.45e9
OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)


def _save(fig, name):
    p = os.path.join(OUT_F, name)
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ]", name)


# ── FigP1 — geometría acotada del parche (FR4) ────────────────────────────────
def figP1_geometria():
    p = MicrostripPatchAntenna(F0_PATCH, 'FR4')
    g = p.geometry_points()
    W, L = g['W'], g['L']
    xs = [pt[0] for pt in g['patch']]
    ys = [pt[1] for pt in g['patch']]

    fig, ax = plt.subplots(figsize=(6.2, 5.6))
    ax.set_aspect('equal')

    # Parche (cobre)
    ax.add_patch(Rectangle((-W / 2, -L / 2), W, L, facecolor="#e9c46a",
                           edgecolor=C_INK, lw=1.4, zorder=3, alpha=0.55))
    # Línea de alimentación
    fx = [pt[0] for pt in g['feed']]
    fy = [pt[1] for pt in g['feed']]
    ax.plot(fx, fy, color=C_INK, lw=2.6, zorder=4, solid_capstyle="round")
    # Muescas del inset
    for seg in g['inset']:
        ax.plot([seg[0][0], seg[1][0]], [seg[0][1], seg[1][1]],
                color="white", lw=2.2, zorder=5)

    # Cota de ancho W (abajo)
    yW = -L / 2 - L * 0.16
    ax.add_patch(FancyArrowPatch((-W / 2, yW), (W / 2, yW), arrowstyle="<|-|>",
                 mutation_scale=10, lw=1.0, color=C_MUTE))
    ax.text(0, yW - L * 0.06, f"W = {W:.1f} mm", ha="center", va="top",
            fontsize=9.5, color=C_INK)
    # Cota de largo L (izquierda)
    xL = -W / 2 - W * 0.14
    ax.add_patch(FancyArrowPatch((xL, -L / 2), (xL, L / 2), arrowstyle="<|-|>",
                 mutation_scale=10, lw=1.0, color=C_MUTE))
    ax.text(xL - W * 0.03, 0, f"L = {L:.1f} mm", ha="right", va="center",
            fontsize=9.5, color=C_INK, rotation=90)
    # Anotación del inset y de la línea de alimentación
    ax.annotate(f"inset {g['inset_depth']:.1f} mm", xy=(g['wf'] * 0.9, -L / 2 + g['inset_depth']),
                xytext=(W * 0.30, -L / 2 + g['inset_depth'] + L * 0.10),
                fontsize=8, color=C_MUTE,
                arrowprops=dict(arrowstyle="->", color=C_MUTE, lw=0.8))
    ax.text(0, -L / 2 - L * 0.02, f"línea {g['wf']:.1f} mm", ha="center",
            va="top", fontsize=7.6, color=C_MUTE)
    # Nota del sustrato (h)
    ax.text(W / 2 + W * 0.04, L / 2, "FR-4\nh = 1.6 mm\n$\\varepsilon_r$ = 4.31",
            ha="left", va="top", fontsize=8.5, color=C_INK)

    m = max(W, L) * 0.75
    ax.set_xlim(-W / 2 - m * 0.5, W / 2 + m * 0.7)
    ax.set_ylim(-L / 2 - L * 0.45, L / 2 + L * 0.2)
    ax.axis("off")
    ax.set_title("Parche microcinta 2,45 GHz sobre FR-4 — geometría acotada",
                 fontsize=10.5)
    _save(fig, "FigP1_geometria_parche.png")


# ── FigP2 — S11 del parche: FR4 vs RT5880 ─────────────────────────────────────
def figP2_s11():
    f = np.linspace(1.0e9, 6.0e9, 800)
    p_fr4 = MicrostripPatchAntenna(F0_PATCH, 'FR4')
    p_rt = MicrostripPatchAntenna(F0_PATCH, 'RT5880')
    s_fr4 = p_fr4.S11_dB(f)
    s_rt = p_rt.S11_dB(f)

    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.plot(f / 1e9, s_fr4, color=C_PATCH_FR4, lw=2.2, label="Parche FR-4")
    ax.plot(f / 1e9, s_rt, color=C_PATCH_RT, lw=2.2, ls="--", label="Parche RT/duroid 5880")
    ax.axhline(-10.0, color=C_ROJO, ls=":", lw=1.1, label="Umbral −10 dB")
    ax.axvline(2.45, color=C_MUTE, ls="--", lw=0.9)
    ax.text(2.47, ax.get_ylim()[0] * 0.9 if False else -2.0, "2,45 GHz",
            fontsize=8, color=C_MUTE, rotation=90, va="bottom")
    ax.set_xlabel("Frecuencia (GHz)")
    ax.set_ylabel("S11 (dB)")
    ax.set_xlim(1.0, 6.0)
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title("Reflexión del parche sobre dos sustratos — modo dominante en 2,45 GHz",
                 fontsize=10.5)
    _save(fig, "FigP2_s11_parche_sustratos.png")


# ── FigP3 — comparativa de antenas: ganancia y η_rad ──────────────────────────
def figP3_comparativa():
    sierp = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)
    p_fr4 = MicrostripPatchAntenna(F0_PATCH, 'FR4')
    p_rt = MicrostripPatchAntenna(F0_PATCH, 'RT5880')
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)

    labels = ["Sierpinski\nFR-4", "Parche\nFR-4", "Parche\nRT5880", "FLPDA\nFR-4"]
    colors = [C_A, C_PATCH_FR4, C_PATCH_RT, C_B]
    gains = [float(sierp.gain_dBi(1.84e9)), float(p_fr4.gain_dBi(F0_PATCH)),
             float(p_rt.gain_dBi(F0_PATCH)), float(flpda.gain_dBi(0.550e9))]
    etas = [sierp.eta_rad(1.84e9) * 100, p_fr4.eta_rad(F0_PATCH) * 100,
            p_rt.eta_rad(F0_PATCH) * 100, flpda.eta_rad(0.550e9) * 100]
    x = np.arange(len(labels))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.2))
    b1 = ax1.bar(x, gains, color=colors, edgecolor=C_INK, lw=0.6)
    ax1.set_ylabel("Ganancia (dBi) @ f0")
    ax1.set_title("Ganancia realizada", fontsize=10.5)
    ax1.set_xticks(x); ax1.set_xticklabels(labels, fontsize=8.5)
    for r, v in zip(b1, gains):
        ax1.text(r.get_x() + r.get_width() / 2, v + 0.12, f"{v:.2f}",
                 ha="center", va="bottom", fontsize=8.2, color=C_INK)
    ax1.set_ylim(0, max(gains) * 1.20)

    b2 = ax2.bar(x, etas, color=colors, edgecolor=C_INK, lw=0.6)
    ax2.set_ylabel("η_rad (%) @ f0")
    ax2.set_title("Eficiencia de radiación", fontsize=10.5)
    ax2.set_xticks(x); ax2.set_xticklabels(labels, fontsize=8.5)
    for r, v in zip(b2, etas):
        ax2.text(r.get_x() + r.get_width() / 2, v + 1.0, f"{v:.1f}",
                 ha="center", va="bottom", fontsize=8.2, color=C_INK)
    ax2.set_ylim(0, 105)

    fig.suptitle("Comparativa antena × sustrato — el sustrato de bajas pérdidas "
                 "eleva η_rad y ganancia", fontsize=11)
    _save(fig, "FigP3_comparativa_antenas.png")


if __name__ == "__main__":
    figP1_geometria()
    figP2_s11()
    figP3_comparativa()
    print("\nListo — figuras comparativas antena × sustrato generadas.")
