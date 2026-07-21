# -*- coding: utf-8 -*-
"""
Figuras de FUNDAMENTACIÓN TEÓRICA para el marco teórico de la tesis.
ADITIVO: no toca las figuras existentes ni core/. Usa la identidad visual
única del proyecto (_regen/estilo.py: APA7_RC + paleta COL) con la convención
editorial es-CO: coma decimal y signo menos tipográfico (−) en rótulos.

Genera (en _regen/out/figuras/):
  FigT1_sierpinski_iteraciones.png — iteraciones 0→3 del triángulo de
      Sierpinski (geometría real de core.antenna.FractalAntenna), con el
      conteo de triángulos conductores 1, 3, 9, 27.
  FigT2_shockley_diodo.png — (a) curva I-V del SMS7630 desde la ecuación de
      Shockley con los parámetros SPICE reales del pipeline (configs.parametros);
      (b) concepto de rectificación del doblador (ejes normalizados, conceptual).
  FigT3_imn_redL.png — (a) esquema de la red L de adaptación (L serie +
      C paralelo); (b) η_imn(f) real de configs.parametros.eta_imn_freq con el
      punto de diseño (550 MHz, η = 0,9484) marcado.

Ejecutar: PYTHONIOENCODING=utf-8 python _regen/theory_figures.py
"""
import os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle, Circle, Arc
from matplotlib.ticker import FuncFormatter

import _regen.estilo as E
from core.antenna import FractalAntenna
from configs.parametros import SMS7630, VT, eta_imn_freq, IMN_F0_HZ, IMN_ETA0

plt.rcParams.update(E.RC)
C_A, C_TEAL, C_ROJO, C_NAR = E.COL["A"], E.COL["accent"], E.COL["warn"], E.COL["model"]
INK, MUTE = E.INK, E.MUTE

OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
os.makedirs(OUT_F, exist_ok=True)


def _coma(x, spec=".3g"):
    """Número con coma decimal y signo − tipográfico (convención del pipeline)."""
    return format(x, spec).replace(".", ",").replace("-", "−")


FMT_COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",").replace("-", "−"))


def _save(fig, name):
    p = os.path.join(OUT_F, name)
    fig.savefig(p, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("[OK ]", name)


# ══════════════════════════════════════════════════════════════════════════════
# FigT1 — Iteraciones 0→3 del triángulo de Sierpinski
# ══════════════════════════════════════════════════════════════════════════════

def figT1_sierpinski():
    ant = FractalAntenna('sierpinski', iterations=3)
    fig, axes = plt.subplots(1, 4, figsize=(10.0, 3.0))
    for k, ax in enumerate(axes):
        tris = ant.geometry_points(iterations=k)
        for v in tris:
            ax.add_patch(Polygon(v, closed=True, facecolor=C_A,
                                 edgecolor="white", lw=0.3))
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.08, 0.95)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"it. {k}\n{len(tris)} triáng.", fontsize=10.5, color=INK)
    fig.suptitle("Sierpinski: autosimilitud por iteración "
                 "(D$_H$ = log 3 / log 2 ≈ " + _coma(np.log(3)/np.log(2), ".3f") + ")",
                 fontsize=12, color=INK)
    _save(fig, "FigT1_sierpinski_iteraciones.png")


# ══════════════════════════════════════════════════════════════════════════════
# FigT2 — Ecuación de Shockley (SMS7630) + concepto de rectificación
# ══════════════════════════════════════════════════════════════════════════════

def figT2_shockley():
    Is, n = SMS7630['Is'], SMS7630['n']
    nvt = n * VT                                   # ≈ 27,2 mV

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.6))

    # (a) Curva I-V de Shockley con parámetros SPICE reales
    V = np.linspace(-0.2, 0.4, 600)
    I_uA = Is * (np.expm1(V / nvt)) * 1e6          # [µA]
    ax1.plot(V, I_uA, color=C_A, lw=2.0, label="Shockley SMS7630")
    ax1.axhline(0, color=MUTE, lw=0.7)
    ax1.axvline(0, color=MUTE, lw=0.7)
    ax1.axvspan(0.15, 0.20, color=C_ROJO, alpha=0.12,
                label="Zona de umbral (≈0,15–0,2 V)")
    ax1.set_ylim(-60, 2000)
    ax1.set_xlim(-0.2, 0.4)
    ax1.xaxis.set_major_formatter(FMT_COMA)
    ax1.yaxis.set_major_formatter(FMT_COMA)
    ax1.set_xlabel("Voltaje del diodo V (V)")
    ax1.set_ylabel("Corriente I (µA)")
    ax1.set_title("(a) I−V Schottky SMS7630 (Shockley)", fontsize=10.5)
    ax1.annotate("I = I$_s$·(e$^{V/(n·V_t)}$ − 1)\n"
                 f"I$_s$ = {_coma(Is*1e6, '.0f')} µA ; n·V$_t$ ≈ {_coma(nvt*1e3, '.1f')} mV",
                 xy=(0.13, 700), xytext=(-0.185, 1150), fontsize=9, color=INK,
                 arrowprops=dict(arrowstyle="-|>", color=MUTE, lw=0.9))
    ax1.legend(loc="upper left", fontsize=7.6)

    # (b) Concepto de rectificación (doblador) — ejes normalizados, sin números
    t = np.linspace(0, 3, 900)                     # t/T
    vin = np.sin(2 * np.pi * t)
    ax2.plot(t, vin, color=C_TEAL, lw=1.6, label="Entrada RF: v$_{in}$(t)")
    ax2.fill_between(t, 0, vin, where=vin > 0, color=C_TEAL, alpha=0.12)
    # salida del doblador: carga exponencial hacia ≈2·V_pk con rizado pequeño
    vout = 2.0 * (1 - np.exp(-t / 0.8)) - 0.06 * (1 - np.exp(-t / 0.8)) * (1 + np.cos(2 * np.pi * t))
    ax2.plot(t, vout, color=C_A, lw=2.2, label="Salida DC del doblador")
    ax2.axhline(2.0, color=MUTE, ls=":", lw=0.9)
    ax2.text(2.97, 2.04, "≈ 2·V$_{pk}$", ha="right", va="bottom",
             fontsize=8.5, color=MUTE)
    ax2.axhline(0, color=MUTE, lw=0.7)
    ax2.set_xlim(0, 3)
    ax2.set_ylim(-1.3, 2.45)
    ax2.set_xlabel("Tiempo normalizado t/T")
    ax2.set_ylabel("Voltaje normalizado v/V$_{pk}$")
    ax2.xaxis.set_major_formatter(FMT_COMA)
    ax2.yaxis.set_major_formatter(FMT_COMA)
    ax2.set_title("(b) Rectificación: RF → DC (conceptual)", fontsize=10.5)
    ax2.legend(loc="lower right", fontsize=7.6)

    _save(fig, "FigT2_shockley_diodo.png")


# ══════════════════════════════════════════════════════════════════════════════
# FigT3 — Red L de adaptación: esquema + η_imn(f) real
# ══════════════════════════════════════════════════════════════════════════════

def _draw_inductor(ax, x0, x1, y, c=INK, lw=1.5):
    """Inductor serie: 4 semicírculos entre x0 y x1 a altura y."""
    n = 4
    w = (x1 - x0) / n
    for i in range(n):
        ax.add_patch(Arc((x0 + w * (i + 0.5), y), w, w * 1.4, angle=0,
                         theta1=0, theta2=180, edgecolor=c, lw=lw, zorder=4))


def _draw_capacitor(ax, x, y0, y1, c=INK, lw=1.5, plate=0.14):
    """Capacitor vertical entre y0 (arriba) y y1 (abajo), placas en el medio."""
    ym = (y0 + y1) / 2
    gap = 0.05
    ax.plot([x, x], [y0, ym + gap], color=c, lw=lw, zorder=4)
    ax.plot([x - plate, x + plate], [ym + gap, ym + gap], color=c, lw=lw, zorder=4)
    ax.plot([x - plate, x + plate], [ym - gap, ym - gap], color=c, lw=lw, zorder=4)
    ax.plot([x, x], [ym - gap, y1], color=c, lw=lw, zorder=4)


def _draw_ground(ax, x, y, c=INK, lw=1.4):
    for i, w in enumerate((0.16, 0.10, 0.05)):
        ax.plot([x - w, x + w], [y - i * 0.055, y - i * 0.055], color=c, lw=lw, zorder=4)


def figT3_redL():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.4, 3.4),
                                   gridspec_kw={"width_ratios": [1.0, 1.15]})

    # (a) Esquema de la red L (fuente/antena — L serie — C paralelo — carga/diodo)
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 5)
    ax1.set_aspect("equal")
    ax1.axis("off")
    y_top, y_bot = 3.4, 1.1
    # fuente (antena) a la izquierda
    ax1.add_patch(Circle((1.1, (y_top + y_bot) / 2), 0.55, facecolor="white",
                         edgecolor=INK, lw=1.4, zorder=4))
    ax1.text(1.1, (y_top + y_bot) / 2, "~", ha="center", va="center",
             fontsize=14, color=INK, zorder=5)
    ax1.text(1.1, 0.35, "Antena\n(fuente RF)", ha="center", va="center",
             fontsize=8.2, color=MUTE)
    ax1.plot([1.1, 1.1], [(y_top + y_bot) / 2 + 0.55, y_top], color=INK, lw=1.5)
    ax1.plot([1.1, 1.1], [y_bot, (y_top + y_bot) / 2 - 0.55], color=INK, lw=1.5)
    # riel superior con L serie
    ax1.plot([1.1, 3.2], [y_top, y_top], color=INK, lw=1.5)
    _draw_inductor(ax1, 3.2, 5.2, y_top, c=C_A, lw=1.7)
    ax1.text(4.2, y_top + 0.85, "L (serie)", ha="center", va="center",
             fontsize=9.5, color=INK)
    ax1.plot([5.2, 8.6], [y_top, y_top], color=INK, lw=1.5)
    # C paralelo a tierra
    _draw_capacitor(ax1, 6.4, y_top, y_bot, c=C_A, lw=1.7)
    ax1.text(6.15, (y_top + y_bot) / 2, "C (paralelo)", ha="right", va="center",
             fontsize=9.5, color=INK)
    # carga (diodo/rectificador) a la derecha
    ax1.add_patch(Rectangle((8.6, 1.7), 1.0, 1.4, facecolor="white",
                            edgecolor=INK, lw=1.4, zorder=4))
    ax1.text(9.1, 2.4, "Z$_d$", ha="center", va="center", fontsize=9.5,
             color=INK, zorder=5)
    ax1.text(9.1, 0.35, "Diodo\n(carga)", ha="center", va="center",
             fontsize=8.2, color=MUTE)
    ax1.plot([9.1, 9.1], [y_top, 3.1], color=INK, lw=1.5)
    ax1.plot([9.1, 9.1], [y_bot, 1.7], color=INK, lw=1.5)
    ax1.plot([8.6, 9.1], [y_top, y_top], color=INK, lw=1.5)
    ax1.plot([8.6, 9.1], [y_bot, y_bot], color=INK, lw=1.5)
    # riel inferior + tierra
    ax1.plot([1.1, 8.6], [y_bot, y_bot], color=INK, lw=1.5)
    _draw_ground(ax1, 4.85, y_bot - 0.35)
    ax1.plot([4.85, 4.85], [y_bot, y_bot - 0.35], color=INK, lw=1.4)
    ax1.set_title("(a) Red L de adaptación (una sección)", fontsize=10.5)

    # (b) η_imn(f) REAL del pipeline, 0,3–1,0 GHz
    f = np.linspace(0.3e9, 1.0e9, 500)
    eta = np.array([eta_imn_freq(fi) for fi in f])
    ax2.plot(f / 1e9, eta, color=C_A, lw=2.2, label="η$_{imn}$(f) — red L, Q ≈ 3,6")
    f0_ghz = IMN_F0_HZ / 1e9
    ax2.plot([f0_ghz], [IMN_ETA0], "o", ms=7, color=C_ROJO, zorder=5)
    ax2.annotate("Punto de diseño\n550 MHz · η = " + _coma(IMN_ETA0, ".4f"),
                 xy=(f0_ghz, IMN_ETA0), xytext=(0.68, 0.72), fontsize=9,
                 color=INK, arrowprops=dict(arrowstyle="-|>", color=MUTE, lw=0.9))
    ax2.set_xlim(0.3, 1.0)
    ax2.set_ylim(0, 1.05)
    ax2.xaxis.set_major_formatter(FMT_COMA)
    ax2.yaxis.set_major_formatter(FMT_COMA)
    ax2.set_xlabel("Frecuencia (GHz)")
    ax2.set_ylabel("Eficiencia de adaptación η$_{imn}$")
    ax2.set_title("(b) η$_{imn}$(f): banda estrecha (Bode−Fano)", fontsize=10.5)
    ax2.legend(loc="upper right", fontsize=8)

    _save(fig, "FigT3_imn_redL.png")


if __name__ == "__main__":
    figT1_sierpinski()
    figT2_shockley()
    figT3_redL()
    print("Listo:", OUT_F)
