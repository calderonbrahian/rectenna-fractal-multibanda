# -*- coding: utf-8 -*-
"""
Extrae del MODELO (SSOT) todos los valores numéricos que aparecen en el documento.
Salida: _regen/out/doc_values.json  — fuente única para regenerar tablas/figuras/texto.

NO modifica core/ ni configs/. Solo lee el modelo vigente.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import numpy as np
from configs.parametros import (CANONICAL, FLPDA_TAU, FLPDA_SIGMA,
                                FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ)
from simulation.escenario_a import run_bandas
from core.flpda import FLPDA_Koch
from core.lora_budget import (avg_power_uw, LORA_PROFILES, harvested_uw_full,
                              fspl_dB, RL_EQUIV)
from core.antenna import FractalAntenna
from core.rectifier import RectifierCircuit
from core.comparacion import validate_wang2022

out = {}

# ── η_rad por banda (Sierpinski) para construir η_total por banda ─────────────
ant = FractalAntenna('sierpinski', iterations=3)
def eta_rad_band(f_hz):
    try:
        return float(ant.eta_rad(f_hz))
    except Exception:
        return float(CANONICAL['eta_rad'])

# ── TABLA 2 — Escenario A (7 bandas BANDS_A), con η_total por banda ───────────
bandas = run_bandas(topology="doubler", Pin_dBm=-10.0)
t2 = []
for b in bandas:
    eta_mm = max(1.0 - 10 ** (b['s11_dB'] / 10.0), 0.0)
    eta_imn = 10 ** (-b['IL_dB'] / 10.0)
    er = eta_rad_band(b['f_Hz'])
    eta_tot_band = er * eta_mm * eta_imn * (b['PCE_pct'] / 100.0)
    t2.append({
        'banda': b['banda'], 'f_GHz': b['f_GHz'],
        'Za': f"{b['Za_real']:.0f}{'+' if b['Za_imag']>=0 else '-'}j{abs(b['Za_imag']):.0f}",
        's11_dB': round(b['s11_dB'], 1), 'eta_mm': round(eta_mm, 2),
        'IL_dB': round(b['IL_dB'], 2), 'PCE_pct': round(b['PCE_pct'], 1),
        'eta_total_pct': round(eta_tot_band * 100, 1), 'Vdc_mV': round(b['Vdc_mV'], 0),
        's11_ok': b['s11_dB'] < -10,
    })
out['tabla2_bandas'] = t2

# ── TABLA 11 — validación Wang (matching_net=None, canónico) ──────────────────
w = validate_wang2022(RectifierCircuit("doubler"), matching_net=None)
out['tabla11_wang'] = {
    'freqs_GHz': w['freqs_GHz'], 'pce_wang': w['pce_referencia'],
    'pce_modelo': w['pce_simulacion'], 'error_pp': w['error_abs_pp'], 'RMSE': round(w['RMSE'], 2),
}

# ── TABLA 9 / E.8 — cadena de potencia vs distancia (TDT 70 dBm, 550 MHz) ─────
flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA, f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
rect = RectifierCircuit("doubler")
def chain_at(dist_m, eirp_dbm=70.0, f_ghz=0.550):
    r = harvested_uw_full(eirp_dbm, dist_m, f_ghz, flpda, rect, matching_net=None)
    fspl = fspl_dB(dist_m, f_ghz)
    return {'d': dist_m, 'FSPL_dB': round(fspl, 1), 'Pin_dBm': round(r['P_rf_dBm'], 1),
            'PCE_pct': round(r['PCE']*100, 0), 'P_RF_uW': round(r['P_rf_uW'], 1),
            'P_DC_uW': round(r['P_dc_uW'], 1), 'V_dc_mV': round(r['V_dc_mV'], 1)}
out['tabla9_chain'] = [chain_at(d) for d in (50, 100, 200, 400, 500, 1000)]
# E.8 mapa EIRP x dist
src = [('TDT DVB-T (Cerro Nutibara)', 70.0, 0.550), ('LTE Macro 700 MHz', 46.0, 0.700),
       ('LTE Band 28 (700 MHz)', 43.0, 0.700), ('LoRa Gateway (Colombia)', 27.0, 0.915)]
e8 = []
for name, eirp, f in src:
    row = {'fuente': name, 'eirp_dbm': eirp}
    for d in (50, 100, 200, 500):
        rr = harvested_uw_full(eirp, d, f, flpda, rect, matching_net=None)
        row[f'd{d}'] = round(rr['P_dc_uW'], 1)
    e8.append(row)
out['tablaE8_map'] = e8

# ── Umbrales de viabilidad (code-derived) ────────────────────────────────────
p_sf12_cont = avg_power_uw(LORA_PROFILES['LoRa SF12 BW125 (1% DC)'])
out['umbral_sf12_continuo_uW'] = round(p_sf12_cont, 1)             # 438.5
out['umbral_app_10min_uW'] = round(CANONICAL['E_ciclo_mJ'] / 600.0 * 1000, 1)  # 432.1

# ── Supercap (ventana V_min→V_max, Ec. E.5) ──────────────────────────────────
C_sup, Vmin, Vmax = 0.330, 1.8, 3.3
E_util_J = 0.5 * C_sup * (Vmax**2 - Vmin**2)
P_dc_W = CANONICAL['P_dc_uW'] * 1e-6
t_carga_s = E_util_J / P_dc_W
out['supercap'] = {'C_F': C_sup, 'Vmin': Vmin, 'Vmax': Vmax,
                   'E_util_mJ': round(E_util_J*1e3, 1),
                   't_carga_s': round(t_carga_s, 1), 't_carga_min': round(t_carga_s/60, 1),
                   'n_ciclos': round(E_util_J*1e3 / CANONICAL['E_ciclo_mJ'], 1)}

# ── E.7 — relación real V_dc = sqrt(P_DC · R_load) ────────────────────────────
out['E7_vdc'] = {'P_dc_uW': CANONICAL['P_dc_uW'], 'R_load_ohm': RL_EQUIV,
                 'V_dc_mV': round((P_dc_W * RL_EQUIV) ** 0.5 * 1e3, 1)}

# ── Ganancia: @550 (canónica) y media en banda ───────────────────────────────
freqs_band = np.linspace(FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ, 50)
g_mean = float(np.mean([float(flpda.gain_dBi(f)) for f in freqs_band]))
out['ganancia'] = {'G_550_dBi': round(float(flpda.gain_dBi(550e6)), 2),
                   'G_media_banda_dBi': round(g_mean, 2)}

# ── Conteos reales ───────────────────────────────────────────────────────────
out['conteos'] = {'n_canonical_keys': len(CANONICAL),
                  'canonical_keys': list(CANONICAL.keys())}

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "doc_values.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)

# resumen legible
print("== TABLA 2 (7 bandas) ==")
for r in t2:
    print(f"  {r['banda']:9} f={r['f_GHz']:.2f} S11={r['s11_dB']:6} PCE={r['PCE_pct']:5} eta_tot={r['eta_total_pct']:5} Vdc={r['Vdc_mV']:.0f}")
print(f"== TABLA 11 Wang RMSE = {out['tabla11_wang']['RMSE']} pp ==")
print(f"   freqs={out['tabla11_wang']['freqs_GHz']}")
print(f"   modelo={out['tabla11_wang']['pce_modelo']}")
print("== TABLA 9 chain ==")
for r in out['tabla9_chain']:
    print(f"  d={r['d']:5} Pin={r['Pin_dBm']:6} P_RF={r['P_RF_uW']:9} P_DC={r['P_DC_uW']:9} Vdc={r['V_dc_mV']:.0f}")
print("== E.8 50m TDT ==", out['tablaE8_map'][0]['d50'])
print("== umbrales ==", out['umbral_sf12_continuo_uW'], "(continuo) /", out['umbral_app_10min_uW'], "(10min)")
print("== supercap ==", out['supercap'])
print("== E.7 V_dc ==", out['E7_vdc'])
print("== ganancia ==", out['ganancia'])
print("== n_canonical ==", out['conteos']['n_canonical_keys'])
