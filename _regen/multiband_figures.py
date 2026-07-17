# -*- coding: utf-8 -*-
"""
Figuras y tablas del rediseño multibanda (Escenario A · co-diseño conjugado).
ADITIVO: no renumera ni toca las Fig01–Fig15 existentes. Usa la identidad visual
única (estilo.py): Sierpinski = oro, umbrales = rojo, modelo = naranja.

Genera:
  FigM1_acople_recuperado.png   — η de acople por banda: modular 50 Ω (1/7) vs
                                   conjugado integrado (6/7).
  FigM2_cosecha_vs_ambiente.png — cosecha total vs nivel RF ambiental, con
                                   umbrales de sensores y banda de Piñuela (2013).
  FigM3_montecarlo_multibanda.png — histograma Monte Carlo de la cosecha (10⁴).
  BM1_cosecha_por_banda.csv       — desglose por banda (η_cm, PCE, P_dc).
  BM2_matriz_escenarios.csv       — matriz entorno→topología→sensor→modo→viabilidad.

Ejecutar: PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/multiband_figures.py
"""
import os, sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import _regen.estilo as E
from core import multiband as mb
from core.lora_budget import avg_power_uw, LORA_PROFILES
from configs.parametros import BANDS_A, URBAN_AMBIENT_NOMINAL_DBM

plt.rcParams.update(E.RC)
C_A, C_ROJO, C_NAR, C_GRIS = E.COL["A"], E.COL["warn"], E.COL["model"], E.COL["grid"]

OUT_F = os.path.join(os.path.dirname(__file__), "out", "figuras")
OUT_T = os.path.join(os.path.dirname(__file__), "out", "tablas")
os.makedirs(OUT_F, exist_ok=True); os.makedirs(OUT_T, exist_ok=True)


def _save(fig, name):
    p = os.path.join(OUT_F, name)
    fig.savefig(p, dpi=300, bbox_inches="tight"); plt.close(fig)
    print("[OK ]", name)


def figM1_acople(ant, rec, imn):
    """Eficiencia TOTAL de acople antena→diodo por banda, comparación justa:
    - Modular: la señal paga DOS pérdidas — antena→50 Ω (η_mm) y 50 Ω→diodo (η_imn).
    - Integrado: una sola red conjugada antena→diodo (η_cm).
    Ambas barras miden lo mismo (potencia que llega al diodo / disponible)."""
    labels, eta_mod, eta_cm = [], [], []
    for banda, f in BANDS_A.items():
        za = ant.impedance(f); zd = rec.diode.impedance(f)
        s11 = float(ant.S11_dB(f))
        eta_mm = max(1.0 - 10 ** (s11 / 10.0), 0.0)          # antena→50 Ω
        eta_imn = 10 ** (-imn.design(f, Z_load=zd).insertion_loss_dB / 10.0)  # 50 Ω→diodo
        eta_mod.append(eta_mm * eta_imn)                      # total modular
        eta_cm.append(imn.conjugate_efficiency(f, za, zd))   # total integrado
        labels.append(banda)
    x = np.arange(len(labels)); w = 0.38
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    ax.bar(x - w/2, eta_mod, w, color=C_GRIS, label="Modular: η_mm·η_imn (antena→50 Ω→diodo)")
    ax.bar(x + w/2, eta_cm, w, color=C_A, label="Integrado: η conjugado (antena→diodo)")
    ax.axhline(0.5, color=C_ROJO, ls="--", lw=1.1, label="Umbral útil η ≥ 0,5")
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Eficiencia total de acople antena→diodo")
    ax.set_ylim(0, 1.05); ax.legend(loc="upper left", fontsize=7.6)
    n_mod = sum(v >= 0.5 for v in eta_mod); n_cm = sum(v >= 0.5 for v in eta_cm)
    ax.set_title(f"Acople útil por banda: {n_mod}/7 modular  →  {n_cm}/7 integrado conjugado",
                 fontsize=10.5)
    _save(fig, "FigM1_acople_recuperado.png")


def figM2_cosecha(ant, rec, imn):
    """Cosecha total vs ambiente, con umbrales de sensores."""
    curva = mb.harvest_vs_ambient(ant, rec, imn, amb_range_dbm=(-35, -3), n_pts=60)
    x = np.array(curva["P_amb_dBm"]); y = np.array(curva["P_dc_total_uW"])
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.axvspan(-30, -15, color=C_A, alpha=0.08, label="Rango urbano típico (Piñuela 2013)")
    ax.semilogy(x, np.maximum(y, 1e-3), color=C_A, lw=2.3, label="Cosecha multibanda total")
    umbrales = [
        (avg_power_uw(LORA_PROFILES["Sensor ADC (solo lectura)"]), "Sensor ADC (1,2 µW)"),
        (avg_power_uw(LORA_PROFILES["LoRa SF7 BW250 (1% DC)"]), "LoRa SF7 (50 µW)"),
        (avg_power_uw(LORA_PROFILES["LoRa SF12 BW125 (1% DC)"]), "LoRa SF12 (438 µW)"),
    ]
    for val, lab in umbrales:
        ax.axhline(val, ls=":", lw=1.1, color=C_ROJO)
        ax.text(x[-1], val * 1.1, lab, ha="right", va="bottom", fontsize=7, color=C_ROJO)
    ax.axvline(URBAN_AMBIENT_NOMINAL_DBM, color="#555", ls="--", lw=1.0)
    ax.set_xlabel("Nivel RF ambiental por banda (dBm)")
    ax.set_ylabel("Potencia DC cosechada (µW)")
    ax.set_ylim(1e-2, 1e3); ax.legend(loc="upper left", fontsize=8)
    ax.set_title("Cosecha multibanda vs ambiente — el sitio decide la viabilidad", fontsize=10.5)
    _save(fig, "FigM2_cosecha_vs_ambiente.png")


def figM3_montecarlo(ant, rec, imn):
    """Histograma Monte Carlo de la cosecha (ambiente ±5 dB)."""
    res = mb.monte_carlo_harvest(ant, rec, imn)
    s = np.array(res["samples"]); s = s[s > 0]
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    ax.hist(s, bins=np.logspace(-2, 3, 50), color=C_A, alpha=0.8, edgecolor="white", lw=0.3)
    ax.set_xscale("log")
    ax.axvline(res["median"], color=C_ROJO, lw=1.6, label=f"Mediana {res['median']:.1f} µW")
    ax.axvline(res["p5"], color="#555", ls=":", lw=1.1, label=f"p5 {res['p5']:.2f} µW")
    ax.axvline(res["p95"], color="#555", ls="--", lw=1.1, label=f"p95 {res['p95']:.1f} µW")
    ax.set_xlabel("Cosecha total (µW)"); ax.set_ylabel("Frecuencia")
    ax.legend(loc="upper right", fontsize=8)
    ax.set_title(f"Monte Carlo (10⁴, ambiente ±5 dB) · CV≈{res['cv_pct']:.0f}%", fontsize=10.5)
    _save(fig, "FigM3_montecarlo_multibanda.png")


def tablas(ant, rec, imn):
    filas = mb.harvest_per_band(ant, rec, imn)
    pd.DataFrame(filas).to_csv(os.path.join(OUT_T, "BM1_cosecha_por_banda.csv"),
                               index=False, encoding="utf-8")
    print("[OK ] BM1_cosecha_por_banda.csv")
    matriz = [
        {"escenario": "E1 remoto vista a torre TDT (≤100 m)", "topologia": "FLPDA dirigida",
         "sensor": "LoRa SF12 continuo", "modo": "1 sin batería", "resultado": "1.335 µW ≫ 438 µW · viable"},
        {"escenario": "E2 periferia torre (100–175 m)", "topologia": "FLPDA dirigida",
         "sensor": "LoRa esporádico + tampón", "modo": "1→2", "resultado": "cae bajo umbral hacia ~175 m"},
        {"escenario": "E3 urbano denso (techo, WiFi/celular)", "topologia": "Sierpinski multibanda",
         "sensor": "ADC / telemetría muy esporádica", "modo": "2 energía-asistido", "resultado": "≈2,4 µW · sostiene sensor ultra-bajo"},
        {"escenario": "E4 urbano muy denso (−10 dBm/banda)", "topologia": "Sierpinski multibanda",
         "sensor": "telemetría periódica", "modo": "2 energía-asistido", "resultado": "≈83 µW · ciclos moderados"},
        {"escenario": "E5 campo lejos de infraestructura", "topologia": "ninguna capta",
         "sensor": "—", "modo": "—", "resultado": "inviable por RF · requiere otra fuente"},
    ]
    pd.DataFrame(matriz).to_csv(os.path.join(OUT_T, "BM2_matriz_escenarios.csv"),
                               index=False, encoding="utf-8")
    print("[OK ] BM2_matriz_escenarios.csv")


if __name__ == "__main__":
    ant, rec, imn = mb.build_default()
    figM1_acople(ant, rec, imn)
    figM2_cosecha(ant, rec, imn)
    figM3_montecarlo(ant, rec, imn)
    tablas(ant, rec, imn)
    print("\nListo — figuras y tablas del rediseño multibanda generadas.")
