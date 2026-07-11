"""
Regeneración de figuras y tablas del trabajo de grado desde el modelo ACTUAL.
================================================================================
Stage 1 (artefactos): lee core/simulation/analysis vigentes (auditados, 51/51
tests) y produce las 11 figuras (matplotlib, estilo APA7) + tablas derivadas +
un reporte de verificación contra CANONICAL.

NO modifica core/, configs/parametros.py ni el documento Word.
Salida en: _regen/out/

Ejecutar:  ./.venv/Scripts/python.exe _regen/generate_artifacts.py
"""

import os
import sys
import json
import traceback

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# Permitir importar el paquete del dashboard (core, simulation, analysis)
_HERE = os.path.dirname(os.path.abspath(__file__))
_DASH = os.path.dirname(_HERE)
for _p in (_DASH, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import estilo as E
from configs.parametros import CANONICAL, BANDS_A, SMS7630

OUT = os.path.join(_HERE, "out")
FIGS = os.path.join(OUT, "figuras")
TABS = os.path.join(OUT, "tablas")
for d in (OUT, FIGS, TABS):
    os.makedirs(d, exist_ok=True)

plt.rcParams.update(E.RC)

# Paleta unificada (estilo.COL) — misma identidad que las figuras conceptuales.
# Convención: A=Sierpinski oro, B=FLPDA verde. Alias por compatibilidad interna.
C_A       = E.COL["A"]        # Escenario A · Sierpinski (oro)
C_VERDE   = E.COL["B"]        # Escenario B · FLPDA (verde)
C_AZUL    = E.COL["accent"]   # serie neutra (teal)
C_NARANJA = E.COL["model"]    # curva de modelo (validación)
C_ROJO    = E.COL["warn"]     # umbrales
C_VIOLETA = E.COL["aux"]      # violeta auxiliar
C_GRIS    = E.COL["grid"]     # gris neutro

status = []   # (figura/tabla, ok/err, detalle)


def _save(fig, name):
    path = os.path.join(FIGS, name)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def _do(label, fn):
    try:
        detail = fn()
        status.append((label, "OK", detail or ""))
        print(f"[OK ] {label}  {detail or ''}")
    except Exception as e:
        status.append((label, "ERR", f"{type(e).__name__}: {e}"))
        print(f"[ERR] {label}  {type(e).__name__}: {e}")
        traceback.print_exc()


# ════════════════════════════════════════════════════════════════════════════
#  FIGURAS
# ════════════════════════════════════════════════════════════════════════════

def fig01_s11_sierpinski():
    from simulation.escenario_a import run_sweep_freq
    sw = run_sweep_freq()
    f = np.array(sw["freqs_GHz"]); s11 = np.array(sw["s11_dB"])
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(f, s11, color=C_A, lw=2, label="Modelo Sierpinski it.3")
    ax.axhline(-10, color="#555", ls="--", lw=1.2, label="Umbral −10 dB")
    for name, fhz in BANDS_A.items():
        ax.axvline(fhz / 1e9, color=C_VIOLETA, ls=":", lw=0.8, alpha=0.7)
    ax.set_xlabel("Frecuencia (GHz)"); ax.set_ylabel(r"$S_{11}$ (dB)")
    ax.set_ylim(-30, 2); ax.legend(loc="lower right")
    _save(fig, "Fig01_S11_Sierpinski.png")
    return f"{len(f)} pts · S11 min={s11.min():.1f} dB"


def fig02_eta_banda_A():
    from simulation.escenario_a import run_bandas
    from core.antenna import FractalAntenna
    bandas = run_bandas(topology="doubler", Pin_dBm=-10.0)
    ant = FractalAntenna("sierpinski", iterations=3)

    def eta_rad_of(f_hz):
        try:
            return float(ant.eta_rad(f_hz))
        except Exception:
            return float(CANONICAL["eta_rad"])

    labels, eta_tot, s11s = [], [], []
    for b in bandas:
        eta_mm = max(1.0 - 10 ** (b["s11_dB"] / 10.0), 0.0)
        eta_imn = 10 ** (-b["IL_dB"] / 10.0)
        er = eta_rad_of(b["f_Hz"])
        eta_tot.append(er * eta_mm * eta_imn * (b["PCE_pct"] / 100.0) * 100.0)
        labels.append(b["banda"])
        s11s.append(b["s11_dB"])
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    x = np.arange(len(labels))
    # oro: banda adaptada (S11 < -10 dB) — Escenario A; gris: el resto
    colors = [C_A if s < -10 else C_GRIS for s in s11s]
    bars = ax.bar(x, eta_tot, color=colors, alpha=0.85)
    for r, v, s in zip(bars, eta_tot, s11s):
        ax.text(r.get_x() + r.get_width() / 2, v + 0.3, f"{v:.1f}\n{s:.0f} dB",
                ha="center", va="bottom", fontsize=7)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel(r"$\eta_{total}$ por banda (%)")
    ax.set_title("Escenario A — eficiencia total por banda (Pin = −10 dBm)", fontsize=11)
    ax.set_ylim(0, max(eta_tot) * 1.25)
    _save(fig, "Fig02_eta_banda_A.png")
    return f"{len(labels)} bandas · η_total max={max(eta_tot):.1f}% · adaptada: 5G-3,5"


def fig03_s11_flpda():
    from simulation.escenario_b import run_sweep_freq_b
    sw = run_sweep_freq_b()
    f = np.array(sw["freqs_MHz"]); s11 = np.array(sw["s11_dB"])
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.axvspan(sw["f_low_MHz"], sw["f_high_MHz"], color=C_VERDE, alpha=0.10,
               label="Banda diseñada 470–900 MHz")
    ax.plot(f, s11, color=C_VERDE, lw=2.2, label="Modelo FLPDA Koch it.2")
    ax.axhline(-10, color="#555", ls="--", lw=1.2, label="Umbral −10 dB")
    for fmhz, lab in [(550, "TDT 550"), (700, "LTE 700"), (850, "GSM 850")]:
        ax.axvline(fmhz, color=C_ROJO, ls=":", lw=0.9, alpha=0.7)
        ax.text(fmhz, -23, lab, rotation=90, fontsize=7, color=C_ROJO,
                ha="right", va="bottom")
    ax.set_xlabel("Frecuencia (MHz)"); ax.set_ylabel(r"$S_{11}$ (dB)")
    ax.set_ylim(-25, 2); ax.legend(loc="lower right", fontsize=8)
    _save(fig, "Fig03_S11_FLPDA.png")
    band = (f >= sw["f_low_MHz"]) & (f <= sw["f_high_MHz"])
    return f"S11 en banda: max={s11[band].max():.1f} dB (todo < -10: {bool((s11[band] < -10).all())})"


def fig04_geom_flpda():
    from simulation.escenario_b import run_geometry_b
    g = run_geometry_b()
    pos = np.array(g["positions_cm"]); Lp = np.array(g["lengths_phys_cm"])
    res = g["res_freqs_MHz"]
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ax.plot([pos[0] - 3, pos[-1] + 3], [0, 0], color="#444", lw=2)  # boom
    for i in range(len(pos)):
        ax.plot([pos[i], pos[i]], [-Lp[i] / 2, Lp[i] / 2], color=C_AZUL, lw=3)
        ax.text(pos[i], -Lp[i] / 2 - 1.5, f"#{i+1}\n{res[i]:.0f}", fontsize=7,
                ha="center", va="top", color="#333")
    ax.set_xlabel("Posición a lo largo del boom (cm)")
    ax.set_ylabel("Extensión del dipolo (cm)")
    ax.set_title(f"FLPDA Koch it.2 — τ=0,90, σ=0,15, N={g['n_elements']} "
                 f"(boom {g['boom_cm']} cm)", fontsize=10)
    ax.set_aspect("equal", adjustable="datalim")
    _save(fig, "Fig04_geometria_FLPDA.png")
    return f"N={g['n_elements']} · boom={g['boom_cm']} cm · red. Koch −{g['reduccion_pct']}%"


def fig05_cascada():
    etapas = ["η_rad", "η_mm", "η_IMN", "PCE", "η_PMIC"]
    facs = [CANONICAL["eta_rad"], CANONICAL["eta_mm"], CANONICAL["eta_imn"],
            CANONICAL["PCE"], CANONICAL["eta_pmic"]]
    cum = np.cumprod(facs) * 100.0
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    xs = np.arange(len(etapas) + 1)
    ys = np.concatenate([[100.0], cum])
    labels = ["P interceptada"] + etapas
    ax.step(xs, ys, where="post", color=C_AZUL, lw=2)
    ax.fill_between(xs, ys, step="post", color=C_AZUL, alpha=0.10)
    for i in range(len(etapas)):
        ax.annotate(f"×{facs[i]:.3f}", (xs[i + 1], cum[i]),
                    textcoords="offset points", xytext=(2, 6), fontsize=8, color=C_ROJO)
    ax.set_xticks(xs); ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
    ax.set_ylabel("Energía conservada (%)")
    ax.set_title(f"Cascada de eficiencia RF→DC — η_total = "
                 f"{CANONICAL['eta_total']*100:.2f}%", fontsize=11)
    ax.set_ylim(0, 105)
    _save(fig, "Fig05_cascada_RFDC.png")
    return f"η_total={CANONICAL['eta_total']:.4f} (esperado 0.6715)"


def fig06_pdc_dist():
    from simulation.escenario_b import run_harvested_vs_dist
    d = run_harvested_vs_dist()
    dist = np.array(d["dist_m"])
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    palette = [C_VIOLETA, C_NARANJA, C_ROJO, C_AZUL]
    srcs = [k for k in d.keys() if k not in ("dist_m", "consumos_uw")]
    for i, s in enumerate(srcs):
        ax.plot(dist, d[s], color=palette[i % len(palette)], lw=2, label=s)
    for prof, p in d.get("consumos_uw", {}).items():
        ax.axhline(p, color="#999", ls=":", lw=1)
        ax.text(dist[-1], p, f" {prof}", fontsize=7, color="#666", va="center")
    ax.set_yscale("log"); ax.set_xlabel("Distancia a la torre TDT (m)")
    ax.set_ylabel("P_DC útil (µW)")
    ax.set_title("Potencia DC disponible vs distancia — Escenario B", fontsize=11)
    ax.legend(fontsize=8)
    _save(fig, "Fig06_PDC_distancia.png")
    return f"{len(srcs)} fuentes · dist {dist[0]:.0f}–{dist[-1]:.0f} m"


def fig07_tciclo_dist():
    from simulation.escenario_b import run_harvested_vs_dist
    d = run_harvested_vs_dist()
    dist = np.array(d["dist_m"])
    tdt_key = next(k for k in d.keys() if "DVB" in k or "UHF" in k)
    p_uw = np.array(d[tdt_key])
    E_mJ = CANONICAL["E_ciclo_mJ"]
    t_ciclo = (E_mJ * 1e3) / np.maximum(p_uw, 1e-6)  # s
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.plot(dist, t_ciclo, color=C_NARANJA, lw=2.2)
    ax.set_yscale("log"); ax.set_xlabel("Distancia a la torre TDT (m)")
    ax.set_ylabel("T_ciclo (s)")
    ax.set_title(f"Intervalo entre transmisiones vs distancia — LoRa SF12 "
                 f"(E_ciclo={E_mJ:.1f} mJ)", fontsize=10)
    ax.grid(True, which="both", alpha=0.25)
    _save(fig, "Fig07_Tciclo_distancia.png")
    # verificación: a 100 m T debe ≈ 158 s
    i100 = int(np.argmin(np.abs(dist - 100)))
    return f"T_ciclo @ {dist[i100]:.0f} m ≈ {t_ciclo[i100]:.0f} s (canónico 158.3 s @100m)"


def fig08_tornado():
    from analysis.avanzado import run_tornado
    s = run_tornado()
    res = s["results"]; base = s["baseline"]
    params = [r["param"] for r in res]
    lows = [r["val_low"] for r in res]; highs = [r["val_high"] for r in res]
    order = np.argsort([abs(hi - lo) for lo, hi in zip(lows, highs)])
    params = [params[i] for i in order]; lows = [lows[i] for i in order]; highs = [highs[i] for i in order]
    fig, ax = plt.subplots(figsize=(6.6, 0.7 * len(params) + 1.5))
    y = np.arange(len(params))
    for i in range(len(params)):
        ax.barh(y[i], highs[i] - lows[i], left=lows[i], color=C_AZUL, alpha=0.8)
    ax.axvline(base, color=C_ROJO, ls="--", lw=1.5, label=f"Base {base:.0f} µW")
    ax.set_yticks(y); ax.set_yticklabels(params)
    ax.set_xlabel("P_DC (µW)"); ax.legend(fontsize=8)
    ax.set_title("Sensibilidad tipo tornado sobre P_DC", fontsize=11)
    _save(fig, "Fig08_tornado.png")
    return f"base={base:.1f} µW · {len(params)} parámetros"


def fig09_montecarlo():
    from analysis.avanzado import run_monte_carlo
    # N=10.000 = el de la narrativa del documento; determinista vía MC_SEED interno.
    mc = run_monte_carlo(n_samples=10000)
    samples = np.array([s for s in mc["samples"] if s > 0])
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.hist(samples, bins=70, color=C_AZUL, alpha=0.78)
    ax.axvline(mc["mean"], color=C_NARANJA, ls="--", lw=2, label=f"Media {mc['mean']:.0f} µW")
    ci = mc.get("ci_95", None)
    if ci:
        ax.axvline(ci[0], color=C_ROJO, ls=":", lw=1.5)
        ax.axvline(ci[1], color=C_ROJO, ls=":", lw=1.5, label="IC 95%")
    ax.set_xlabel("P_DC (µW)"); ax.set_ylabel("Frecuencia")
    ax.set_title(f"Distribución Monte Carlo de P_DC (N={mc.get('n_total', len(samples))})",
                 fontsize=11)
    ax.legend(fontsize=8)
    _save(fig, "Fig09_montecarlo.png")
    return f"media={mc['mean']:.1f} µW · n={len(samples)}"


def fig10_pce_ambos():
    from simulation.escenario_b import run_pce_uhf_curve
    from simulation.escenario_a import run_pce_vs_pin
    b = run_pce_uhf_curve(f_hz=550e6)
    a = run_pce_vs_pin(f_GHz=3.30, topology="doubler")
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.plot(b["Pin_dBm"], b["PCE_pct"], color=C_VERDE, lw=2.2,
            label="Escenario B · 550 MHz")
    ax.plot(a["Pin_dBm"], a["PCE_pct"], color=C_A, lw=2.0, ls="--",
            label="Escenario A · 3,30 GHz")
    ax.axvline(CANONICAL["P_in_dBm"], color=C_ROJO, ls=":", lw=1.4,
               label=f"P_in canónico {CANONICAL['P_in_dBm']:.2f} dBm")
    ax.set_xlabel("P_in (dBm)"); ax.set_ylabel("PCE (%)")
    ax.set_ylim(0, 90); ax.legend(fontsize=8)
    ax.set_title("Eficiencia de conversión RF→DC de ambos escenarios", fontsize=11)
    _save(fig, "Fig10_PCE_ambos.png")
    return f"PCE_B max={max(b['PCE_pct']):.1f}% · PCE_A max={max(a['PCE_pct']):.1f}%"


def fig11_wang():
    # Metodología CANÓNICA del documento (§4.5): adaptación ideal → matching_net=None.
    # (La app usa matching_net=imn y obtiene 22,68 pp; ver informe de auditoría.)
    from core.comparacion import validate_wang2022
    from core.rectifier import RectifierCircuit
    r = validate_wang2022(RectifierCircuit("doubler"), matching_net=None)
    f = np.array(r["freqs_GHz"])
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.plot(f, r["pce_referencia"], "s-", color=C_VERDE, lw=2,
            label="Wang et al. (2022)")
    ax.plot(f, r["pce_simulacion"], "o--", color=C_NARANJA, lw=2,
            label="Modelo (este trabajo)")
    ax.set_xlabel("Frecuencia (GHz)"); ax.set_ylabel("PCE (%)")
    ax.set_title(f"Modelo vs Wang et al. (2022) — RMSE = {r['RMSE']:.2f} pp", fontsize=11)
    ax.legend(fontsize=8)
    _save(fig, "Fig11_validacion_Wang.png")
    return f"RMSE={r['RMSE']:.2f} pp (canónico {CANONICAL['RMSE_wang']} pp)"


# ════════════════════════════════════════════════════════════════════════════
#  TABLAS (derivadas del código → CSV)
# ════════════════════════════════════════════════════════════════════════════

def _csv(name, header, rows):
    import csv
    path = os.path.join(TABS, name)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    return path


def tablas_codigo():
    import pandas as pd
    from simulation.escenario_a import run_bandas
    from simulation.escenario_b import run_geometry_b, run_pce_uhf_curve
    from analysis.avanzado import run_link_budget
    n = 0

    # T2 — bandas Escenario A
    bandas = run_bandas(topology="doubler", Pin_dBm=-10.0)
    pd.DataFrame(bandas).to_csv(os.path.join(TABS, "E12_bandas_escenarioA.csv"),
                                index=False, encoding="utf-8"); n += 1

    # T3 — SPICE SMS7630
    _csv("E13_SPICE_SMS7630.csv", ["Parámetro", "Valor"],
         [["Is [A]", SMS7630["Is"]], ["n", SMS7630["n"]], ["Rs [Ω]", SMS7630["Rs"]],
          ["Cj0 [F]", SMS7630["Cj0"]], ["Vj [V]", SMS7630["Vj"]], ["M", SMS7630["M"]]]); n += 1

    # T6 — geometría dipolos Koch
    g = run_geometry_b()
    rows6 = [[i + 1, round(g["res_freqs_MHz"][i], 1),
              round(g["lengths_elec_cm"][i], 1), round(g["lengths_phys_cm"][i], 1),
              round(g["positions_cm"][i], 1)] for i in range(g["n_elements"])]
    _csv("E15_geometria_dipolos.csv",
         ["Dipolo", "f_res [MHz]", "L_elec [cm]", "L_fis [cm]", "Pos [cm]"], rows6); n += 1

    # T7 — PCE vs Pin (muestreo)
    p = run_pce_uhf_curve(f_hz=550e6)
    idx = np.linspace(0, len(p["Pin_dBm"]) - 1, 12).astype(int)
    rows7 = [[round(p["Pin_dBm"][i], 1), round(p["PCE_pct"][i], 2),
              round(p["Vdc_mV"][i], 1)] for i in idx]
    _csv("E16_PCE_Pin.csv", ["Pin [dBm]", "PCE [%]", "Vdc [mV]"], rows7); n += 1

    # T8 — presupuesto de enlace
    lb = run_link_budget()
    if isinstance(lb, list) and lb and isinstance(lb[0], dict):
        pd.DataFrame(lb).to_csv(os.path.join(TABS, "E17_link_budget.csv"),
                                index=False, encoding="utf-8")
    else:
        _csv("E17_link_budget.csv", ["item"], [[str(x)] for x in lb])
    n += 1

    # T9 — cadena de potencia (CANONICAL)
    facs = [("P_in", CANONICAL["P_in_mW"] * 1000, "µW"),
            ("η_mm", CANONICAL["eta_mm"], "—"), ("η_IMN", CANONICAL["eta_imn"], "—"),
            ("PCE", CANONICAL["PCE"], "—"), ("η_PMIC", CANONICAL["eta_pmic"], "—"),
            ("P_DC", CANONICAL["P_dc_uW"], "µW")]
    _csv("E18_cadena_potencia.csv", ["Etapa", "Valor", "Unidad"],
         [[a, b, c] for a, b, c in facs]); n += 1

    # T11 — banda a banda vs Wang (metodología canónica del documento: matching_net=None)
    from core.comparacion import validate_wang2022
    from core.rectifier import RectifierCircuit
    w = validate_wang2022(RectifierCircuit("doubler"), matching_net=None)
    rows11 = [[round(w["freqs_GHz"][i], 2), round(w["pce_referencia"][i], 1),
               round(w["pce_simulacion"][i], 1), round(w["error_abs_pp"][i], 1)]
              for i in range(len(w["freqs_GHz"]))]
    _csv("E19_vs_Wang.csv", ["f [GHz]", "PCE Wang [%]", "PCE modelo [%]", "Error [pp]"],
         rows11); n += 1

    return f"{n} tablas derivadas del código"


# ════════════════════════════════════════════════════════════════════════════
#  FIGURAS CONCEPTUALES / METODOLÓGICAS (C1–C5) — sistema gráfico unificado
# ════════════════════════════════════════════════════════════════════════════

def figuras_conceptuales():
    """Genera las 5 figuras conceptuales/metodológicas del documento (C1–C5).
    Delega en figuras_conceptuales.py para que un solo comando regenere TODO
    el material del documento (figuras de datos + conceptuales + tablas)."""
    import importlib
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    fc = importlib.import_module("figuras_conceptuales")
    fns = [fc.figC1_fuentes_a_caso, fc.figC5_maestra, fc.figC3_anatomia_rectena,
           fc.figC2_flujo_metodologico, fc.figC4_cadena_reproducible]
    for fn in fns:
        fn()
    return f"{len(fns)} figuras conceptuales (C1–C5)"


# ════════════════════════════════════════════════════════════════════════════
#  VERIFICACIÓN contra CANONICAL
# ════════════════════════════════════════════════════════════════════════════

def verificacion():
    from core.flpda import FLPDA_Koch
    from configs.parametros import FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    checks = {
        "S11_@550MHz_dB": (float(flpda.S11_dB(550e6)), CANONICAL["S11_dB"]),
        "gain_@550MHz_dBi": (float(flpda.gain_dBi(550e6)), CANONICAL["gain_dBi"]),
        "eta_total_FOM": (
            CANONICAL["eta_rad"] * CANONICAL["eta_mm"] * CANONICAL["eta_imn"]
            * CANONICAL["PCE"] * CANONICAL["eta_pmic"], CANONICAL["eta_total"]),
        "P_DC_identidad_uW": (
            CANONICAL["P_in_mW"] * 1000 * CANONICAL["eta_mm"] * CANONICAL["eta_imn"]
            * CANONICAL["PCE"] * CANONICAL["eta_pmic"], CANONICAL["P_dc_uW"]),
    }
    out = {}
    for k, (got, exp) in checks.items():
        out[k] = {"modelo": round(got, 4), "canonico": exp,
                  "delta": round(got - exp, 4)}
    with open(os.path.join(OUT, "verificacion.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
    return " · ".join(f"{k}:Δ{v['delta']:+.3f}" for k, v in out.items())


# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("REGENERACIÓN DE ARTEFACTOS — modelo actual (auditado)")
    print("=" * 70)
    _do("Fig 1 · S11 Sierpinski", fig01_s11_sierpinski)
    _do("Fig 2 · η por banda A", fig02_eta_banda_A)
    _do("Fig 3 · S11 FLPDA", fig03_s11_flpda)
    _do("Fig 4 · Geometría FLPDA", fig04_geom_flpda)
    _do("Fig 5 · Cascada RF→DC", fig05_cascada)
    _do("Fig 6 · P_DC vs distancia", fig06_pdc_dist)
    _do("Fig 7 · T_ciclo vs distancia", fig07_tciclo_dist)
    _do("Fig 8 · Tornado", fig08_tornado)
    _do("Fig 9 · Monte Carlo", fig09_montecarlo)
    _do("Fig 10 · PCE ambos", fig10_pce_ambos)
    _do("Fig 11 · Validación Wang", fig11_wang)
    _do("Figuras conceptuales · C1–C5", figuras_conceptuales)
    _do("Tablas (código)", tablas_codigo)
    _do("Verificación canónica", verificacion)

    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    ok = sum(1 for _, s, _ in status if s == "OK")
    err = sum(1 for _, s, _ in status if s == "ERR")
    for label, s, detail in status:
        print(f"  [{s}] {label}  {detail}")
    print(f"\n  Total: {ok} OK · {err} ERR")
    print(f"  Salida: {OUT}")
