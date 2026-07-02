# -*- coding: utf-8 -*-
"""
Figuras del PÓSTER de sustentación — regeneradas desde el modelo (SSOT).

Mismos datos que _regen/generate_artifacts.py (Fig03/05/06 + espectro + KPI),
pero con estilo específico para impresión a gran formato (90×110 cm):
  · tipografía sans-serif grande, líneas gruesas, alto contraste;
  · paleta institucional del póster (teal UdeA #007297 + lima #8DC63F);
  · separador decimal en coma (es-CO);
  · sin elementos superfluos.

Salida: _regen/out/poster/P*.png (300 dpi).
Ningún valor se escribe a mano: todo proviene de configs/parametros.py
y de los runners de simulation/ (idéntico a las figuras de la tesis).
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

from configs.parametros import CANONICAL, RF_UHF as RF_SOURCES_UHF

OUT = os.path.join(_HERE, "out", "poster")
os.makedirs(OUT, exist_ok=True)

# ── Estilo póster ────────────────────────────────────────────────────────────
TEAL = "#007297"      # teal institucional del póster
TEAL_D = "#0F3D4C"    # teal oscuro (texto)
LIME = "#8DC63F"      # acento lima de la plantilla
ORANGE = "#E07B39"    # acento cálido (anotaciones)
GRAY = "#9AA5AD"

POSTER_RC = {
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 16,
    "axes.labelsize": 18,
    "axes.titlesize": 20,
    "axes.titleweight": "bold",
    "legend.fontsize": 14,
    "xtick.labelsize": 15,
    "ytick.labelsize": 15,
    "lines.linewidth": 3.0,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.grid": True,
    "grid.alpha": 0.30,
    "grid.linestyle": "--",
    "grid.linewidth": 0.7,
    "axes.axisbelow": True,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#444444",
    "text.color": TEAL_D,
    "axes.labelcolor": TEAL_D,
    "xtick.color": TEAL_D,
    "ytick.color": TEAL_D,
}
plt.rcParams.update(POSTER_RC)


def dc(x, nd=1):
    """Número con coma decimal (es-CO)."""
    s = f"{x:,.{nd}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", " ")


FMT_COMA = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))


def _save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path)
    plt.close(fig)
    print(f"[OK] {name}")


# ── P1 · Cascada de eficiencia RF→DC ────────────────────────────────────────
def p1_cascada():
    etapas = [r"$\eta_{rad}$", r"$\eta_{mm}$", r"$\eta_{IMN}$", "PCE", r"$\eta_{PMIC}$"]
    facs = [CANONICAL["eta_rad"], CANONICAL["eta_mm"], CANONICAL["eta_imn"],
            CANONICAL["PCE"], CANONICAL["eta_pmic"]]
    cum = np.cumprod(facs) * 100.0
    xs = np.arange(len(etapas) + 1)
    ys = np.concatenate([[100.0], cum])

    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    ax.step(xs, ys, where="post", color=TEAL, lw=4)
    ax.fill_between(xs, ys, step="post", color=TEAL, alpha=0.14)
    for i in range(len(etapas)):
        ax.annotate("×" + dc(facs[i], 3), (xs[i + 1] - 0.02, cum[i]),
                    textcoords="offset points", xytext=(4, 10),
                    fontsize=15, fontweight="bold", color=ORANGE)
    # resultado final, grande
    ax.annotate(dc(CANONICAL["eta_total"] * 100, 2) + " %",
                (xs[-1], cum[-1]), textcoords="offset points", xytext=(-8, -46),
                fontsize=26, fontweight="bold", color=TEAL, ha="right")
    ax.set_xticks(xs)
    ax.set_xticklabels(["P captada"] + etapas, fontsize=16)
    ax.set_ylabel("Energía conservada (%)")
    ax.set_title("Cascada de eficiencia RF→DC", pad=14)
    ax.set_ylim(0, 106)
    ax.yaxis.set_major_formatter(FMT_COMA)
    _save(fig, "P1_cascada.png")
    assert abs(cum[-1] - CANONICAL["eta_total"] * 100) < 0.05


# ── P2 · Adaptación S11 FLPDA ────────────────────────────────────────────────
def p2_s11():
    from simulation.escenario_b import run_sweep_freq_b
    sw = run_sweep_freq_b()
    f = np.array(sw["freqs_MHz"]); s11 = np.array(sw["s11_dB"])

    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    ax.axvspan(sw["f_low_MHz"], sw["f_high_MHz"], color=LIME, alpha=0.16,
               label="Banda diseñada 470–900 MHz")
    ax.plot(f, s11, color=TEAL, lw=3.6, label="Modelo FLPDA Koch it.2")
    ax.axhline(-10, color="#333333", ls="--", lw=2.0, label="Umbral −10 dB")
    for fmhz, lab in [(550, "TDT 550"), (700, "LTE 700"), (850, "GSM 850")]:
        ax.axvline(fmhz, color=ORANGE, ls=":", lw=1.8, alpha=0.85)
        ax.text(fmhz, 0.8, lab, rotation=0, fontsize=13, color=ORANGE,
                ha="center", va="bottom", fontweight="bold")
    ax.set_xlabel("Frecuencia (MHz)")
    ax.set_ylabel(r"$S_{11}$ (dB)")
    ax.set_ylim(-25, 4)
    ax.set_title("Adaptación de la antena FLPDA Koch", pad=12)
    ax.legend(loc="lower right", framealpha=0.9)
    ax.yaxis.set_major_formatter(FMT_COMA)
    _save(fig, "P2_s11.png")
    band = (f >= sw["f_low_MHz"]) & (f <= sw["f_high_MHz"])
    assert (s11[band] < -10).all()


# ── P3 · Potencia DC útil vs. distancia ─────────────────────────────────────
def p3_pdc():
    from simulation.escenario_b import run_harvested_vs_dist
    d = run_harvested_vs_dist()
    dist = np.array(d["dist_m"])
    tdt_key = next(k for k in d if "DVB" in k or "UHF" in k)

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    # fuentes secundarias, discretas
    style = {"LTE Macro 700 MHz": (GRAY, "-"), "LTE Band 28 (700 MHz)": (GRAY, "--"),
             "LoRa Gateway (Colombia)": (GRAY, ":")}
    for k, (c, ls) in style.items():
        if k in d:
            ax.plot(dist, d[k], color=c, ls=ls, lw=1.8, label=k)
    # fuente principal
    ax.plot(dist, d[tdt_key], color=TEAL, lw=4.0, label="TV UHF (DVB-T) — fuente elegida")
    # umbral SF12
    sf12 = d["consumos_uw"].get("LoRa SF12 BW125 (1% DC)")
    if sf12:
        ax.axhline(sf12, color=ORANGE, ls="--", lw=2.2)
        ax.text(dist[-1], sf12 * 1.25, "Umbral LoRa SF12 · " + dc(sf12, 1) + " µW",
                fontsize=13, color=ORANGE, ha="right", fontweight="bold")
    # punto canónico @100 m
    i100 = int(np.argmin(np.abs(dist - 100)))
    p100 = d[tdt_key][i100]
    ax.plot([dist[i100]], [p100], "o", ms=13, color=LIME,
            mec=TEAL, mew=2.5, zorder=5)
    ax.annotate(dc(CANONICAL["P_dc_uW"], 1) + " µW @ 100 m",
                (dist[i100], p100), textcoords="offset points", xytext=(20, 16),
                fontsize=16, fontweight="bold", color=TEAL)
    ax.set_yscale("log")
    ax.set_xlabel("Distancia a la torre TDT (m)")
    ax.set_ylabel(r"$P_{DC}$ útil (µW)")
    ax.set_ylim(1e-2, 3e4)
    ax.set_title("Potencia DC útil vs. distancia — Escenario B", pad=12)
    ax.legend(loc="center right", framealpha=0.9, fontsize=12)
    _save(fig, "P3_pdc.png")
    assert abs(p100 - CANONICAL["P_dc_uW"]) / CANONICAL["P_dc_uW"] < 0.03


# ── P4 · Espectro RF del ambiente (fuentes de cosecha) ──────────────────────
def p4_espectro():
    # Fuentes UHF con EIRP del modelo (configs.parametros.RF_SOURCES_UHF)
    srcs = [
        ("TDT (DVB-T)", RF_SOURCES_UHF["TV UHF (DVB-T)"]["eirp_dbm"], 550, TEAL),
        ("LTE 700", RF_SOURCES_UHF["LTE Macro 700 MHz"]["eirp_dbm"], 700, "#3E8FB0"),
        ("LoRa GW", RF_SOURCES_UHF["LoRa Gateway (Colombia)"]["eirp_dbm"], 915, "#7FB4C7"),
    ]
    # Bandas altas: presencia cualitativa (sin EIRP del modelo — no se inventa)
    altas = [("GSM 1800", 1800), ("Wi-Fi 2,4", 2400), ("5G 3,5", 3500), ("Wi-Fi 5,8", 5800)]

    fig, ax = plt.subplots(figsize=(13.6, 3.7))
    ax.set_xscale("log")
    ax.axvspan(470, 900, color=LIME, alpha=0.18)
    ax.text(np.sqrt(470 * 900), 85.5, "Banda de cosecha · UHF 470–900 MHz",
            ha="center", fontsize=15, fontweight="bold", color="#4C7A1F")
    for lab, eirp, f, c in srcs:
        ax.bar(f, eirp - 20, bottom=20, width=f * 0.16, color=c,
               edgecolor=TEAL_D, lw=1.2, zorder=3)
        ax.text(f, eirp + 1.5, f"{lab}\n{dc(eirp,0)} dBm", ha="center",
                fontsize=13, fontweight="bold", color=TEAL_D)
    ax.annotate("fuente elegida", (550, 45), rotation=90, ha="center",
                va="center", fontsize=12.5, color="white", fontweight="bold")
    for lab, f in altas:
        ax.bar(f, 6, bottom=20, width=f * 0.14, color="#D7DDE1",
               edgecolor="#8A9299", hatch="///", lw=1.0, zorder=3)
        ax.text(f, 27.5, lab, ha="center", fontsize=12, color="#5A646B")
    ax.text(2900, 48, "alta frecuencia:\ndensidad baja y variable",
            ha="center", fontsize=12.5, style="italic", color="#5A646B")
    ax.set_ylim(20, 92)
    ax.set_xlim(430, 7200)
    ax.set_xticks([470, 700, 900, 1800, 2400, 3500, 5800])
    ax.set_xticklabels(["470", "700", "900", "1800", "2400", "3500", "5800"])
    ax.set_xlabel("Frecuencia (MHz)")
    ax.set_ylabel("EIRP (dBm)")
    ax.set_title("Espectro RF del ambiente: ¿de dónde se cosecha la energía?", pad=12)
    ax.grid(True, which="major", axis="y")
    ax.grid(False, axis="x")
    _save(fig, "P4_espectro.png")


# ── P5 · Comparación de topologías: PCE Escenario B vs A ────────────────────
def p5_pce_comparacion():
    from simulation.escenario_b import run_pce_uhf_curve
    from simulation.escenario_a import run_pce_vs_pin
    b = run_pce_uhf_curve(f_hz=550e6)
    a = run_pce_vs_pin(f_GHz=3.30, topology="doubler")

    fig, ax = plt.subplots(figsize=(5.0, 5.6))
    ax.text(-24.3, 87.2, "B opera en el tope del modelo (85 %)",
            fontsize=11.5, color="#5A646B")
    ax.plot(b["Pin_dBm"], b["PCE_pct"], color=TEAL, lw=4.0,
            label="FLPDA Koch · 550 MHz (B)")
    ax.plot(a["Pin_dBm"], a["PCE_pct"], color="#8A9299", lw=2.6, ls="--",
            label="Sierpinski · 3,30 GHz (A)")
    ax.axvline(CANONICAL["P_in_dBm"], color=ORANGE, ls=":", lw=2.6,
               label="$P_{in}$ de operación · " + dc(CANONICAL["P_in_dBm"], 2) + " dBm")
    ax.set_xlabel(r"$P_{in}$ (dBm)")
    ax.set_ylabel("PCE (%)")
    ax.set_xlim(-25, 5.5)
    ax.set_ylim(0, 96)
    ax.set_title("¿Por qué la FLPDA Koch?\nPCE de las dos topologías", fontsize=17,
                 pad=12)
    ax.legend(loc="center left", fontsize=11.5, framealpha=0.92)
    ax.yaxis.set_major_formatter(FMT_COMA)
    ax.xaxis.set_major_formatter(FMT_COMA)
    _save(fig, "P5_pce_comparacion.png")
    assert max(b["PCE_pct"]) <= 85.001


if __name__ == "__main__":
    p1_cascada()
    p2_s11()
    p3_pdc()
    p4_espectro()
    p5_pce_comparacion()
    print("Listo:", OUT)
