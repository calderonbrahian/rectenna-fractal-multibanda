"""
Escenario B — FLPDA Koch it.2, 470–900 MHz.
Todas las funciones retornan dicts serializables para @st.cache_data.
"""

import numpy as np
import streamlit as st

from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.lora_budget import (
    harvested_uw_full, harvested_uw, avg_power_uw,
    received_power_dBm, RF_SOURCES_UHF, LORA_PROFILES,
)
from configs.parametros import FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ


@st.cache_data(show_spinner=False)
def run_sweep_freq_b(n_pts: int = 400) -> dict:
    """Barrido en frecuencia 300–1100 MHz para S11, ganancia e impedancia."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    freqs = np.linspace(300e6, 1100e6, n_pts)
    s11   = flpda.S11_dB(freqs).tolist()
    gain  = flpda.gain_dBi(freqs).tolist()
    za    = flpda.impedance(freqs)
    return {
        'freqs_MHz': (freqs / 1e6).tolist(),
        's11_dB':    s11,
        'gain_dBi':  gain,
        'Za_real':   za.real.tolist(),
        'Za_imag':   za.imag.tolist(),
        'f_low_MHz':  FLPDA_F_LOW_HZ / 1e6,
        'f_high_MHz': FLPDA_F_HIGH_HZ / 1e6,
    }


@st.cache_data(show_spinner=False)
def run_geometry_b() -> dict:
    """Tabla de geometría del arreglo FLPDA."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    return {
        'n_elements':    flpda.n_elements,
        'boom_cm':       round(flpda.boom_length_m * 100, 1),
        'L_max_phys_cm': round(flpda.max_element_length_m * 100, 1),
        'k_red':         flpda.k_red,
        'reduccion_pct': round((1 - flpda.k_red) * 100, 1),
        'lengths_phys_cm': (flpda.lengths_phys * 100).tolist(),
        'lengths_elec_cm': (flpda.lengths_elec * 100).tolist(),
        'positions_cm':    (flpda.positions * 100).tolist(),
        'res_freqs_MHz':   (flpda.resonant_freqs / 1e6).tolist(),
    }


@st.cache_data(show_spinner=False)
def run_budget_lora(dist_m: float = 500.0) -> dict:
    """
    Presupuesto de cosechamiento LoRa a distancia dist_m.
    Usa cadena completa Shockley (harvested_uw_full) para coherencia con valores canónicos.
    """
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    rect  = RectifierCircuit('doubler', R_load=1300.0)

    cosecha = {}
    for src_name, src in RF_SOURCES_UHF.items():
        row = {}
        Pr_dBm = received_power_dBm(src['eirp_dbm'], dist_m, src['freq_ghz'])
        result = harvested_uw_full(src['eirp_dbm'], dist_m, src['freq_ghz'], flpda, rect)
        P_uw   = result['P_dc_uW']
        for prof_name, prof in LORA_PROFILES.items():
            P_consumo = avg_power_uw(prof)
            row[prof_name] = {
                'P_cosechada_uW': round(P_uw, 3),
                'P_consumo_uW':   round(P_consumo, 3),
                'margen_uW':      round(P_uw - P_consumo, 3),
                'viable':         P_uw > P_consumo,
                'Pr_dBm':         round(Pr_dBm, 1),
                'Vdc_mV':         round(result.get('V_dc_mV', 0.0), 1),
            }
        cosecha[src_name] = row

    return {'dist_m': dist_m, 'cosecha': cosecha}


@st.cache_data(show_spinner=False)
def run_harvested_vs_dist(dist_range_m: tuple = (50.0, 2000.0), n_pts: int = 80) -> dict:
    """Potencia cosechada DC vs distancia para cada fuente RF (cadena completa)."""
    flpda  = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                        f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    rect   = RectifierCircuit('doubler', R_load=1300.0)
    dists  = np.linspace(dist_range_m[0], dist_range_m[1], n_pts)
    out    = {'dist_m': dists.tolist()}
    for src_name, src in RF_SOURCES_UHF.items():
        out[src_name] = [
            harvested_uw_full(src['eirp_dbm'], float(d), src['freq_ghz'], flpda, rect)['P_dc_uW']
            for d in dists
        ]
    out['consumos_uw'] = {k: avg_power_uw(v) for k, v in LORA_PROFILES.items()}
    return out


@st.cache_data(show_spinner=False)
def run_pce_uhf_curve(f_hz: float = 550e6) -> dict:
    """Curva PCE del modelo Shockley doubler SMS7630 a frecuencia UHF."""
    rect = RectifierCircuit('doubler', R_load=1300.0)
    pins = np.linspace(-35, 5, 100)
    pce  = [rect.PCE(float(p), f_hz) * 100 for p in pins]
    vdc  = [rect.output_voltage(float(p), f_hz) * 1000 for p in pins]
    return {
        'Pin_dBm': pins.tolist(),
        'PCE_pct': pce,
        'Vdc_mV':  vdc,
        'f_MHz':   f_hz / 1e6,
    }


@st.cache_data(show_spinner=False)
def run_radiation_pattern_b(f_MHz: float = 700.0) -> dict:
    """Patrón de radiación FLPDA en el plano E."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    theta = np.linspace(0, 360, 361)
    pat   = flpda.radiation_pattern_dB(f_MHz * 1e6, theta)
    return {'theta_deg': theta.tolist(), 'pattern_dB': pat.tolist()}
