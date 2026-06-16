"""
Análisis avanzado — envueltas cacheadas para core/analysis.py.
Tornado de sensibilidad · Monte Carlo · Supercondensador · Presupuesto de enlace
"""

import numpy as np
import streamlit as st

from core.analysis import (
    sensitivity_tornado, monte_carlo_pdc,
    rectifier_bandwidth, link_budget_table,
    supercap_sizing, get_state_of_art_table,
)
from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.lora_budget import harvested_uw_full
from configs.parametros import FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ, CANONICAL


def _compute_pdc(params: dict) -> float:
    """Función de evaluación para tornado y Monte Carlo."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ)
    rect  = RectifierCircuit('doubler', R_load=params.get('R_load', 1300.0))
    r = harvested_uw_full(
        params['eirp_dbm'], max(params['dist_m'], 1.0), params['freq_ghz'],
        flpda, rect
    )
    return r['P_dc_uW']


@st.cache_data(show_spinner=False)
def run_tornado(eirp_dbm: float = 70.0, dist_m: float = 100.0,
                freq_ghz: float = 0.55, R_load: float = 1300.0) -> dict:
    """Análisis de sensibilidad tipo tornado sobre P_DC."""
    base   = {'eirp_dbm': eirp_dbm, 'dist_m': dist_m, 'freq_ghz': freq_ghz, 'R_load': R_load}
    deltas = {'eirp_dbm': 3.0, 'dist_m': 20.0, 'freq_ghz': 0.05, 'R_load': 300.0}
    return sensitivity_tornado(base, deltas, _compute_pdc, 'P_DC [µW]')


# Semilla fija: el Monte Carlo es la ÚNICA fuente de verdad de sus estadísticos.
# Sin ella, figura, texto del documento y app mostraban realizaciones distintas.
# Determinista y reproducible (figura = documento = aplicación).
MC_SEED = 42


@st.cache_data(show_spinner=False)
def run_monte_carlo(eirp_dbm: float = 70.0, dist_m: float = 100.0,
                    freq_ghz: float = 0.55, R_load: float = 1300.0,
                    n_samples: int = 2000) -> dict:
    """Propagación de incertidumbre Monte Carlo sobre P_DC (determinista, MC_SEED)."""
    base = {'eirp_dbm': eirp_dbm, 'dist_m': dist_m, 'freq_ghz': freq_ghz, 'R_load': R_load}
    uncertainties = {
        'eirp_dbm': {'type': 'normal',  'std': 2.0},
        'dist_m':   {'type': 'uniform', 'half_range': 15.0},
        'freq_ghz': {'type': 'normal',  'std': 0.01},
    }
    np.random.seed(MC_SEED)
    result = monte_carlo_pdc(base, uncertainties, _compute_pdc, n_samples=n_samples)
    # Convert ndarray to list for caching
    result['samples'] = result['samples'].tolist()
    return result


@st.cache_data(show_spinner=False)
def run_rectifier_bw(Pin_dBm: float = -10.0, freq_center_mhz: float = 550.0,
                     freq_span_mhz: float = 1000.0) -> dict:
    """Ancho de banda -3 dB del rectificador doubler SMS7630."""
    rect   = RectifierCircuit('doubler', R_load=1300.0)
    result = rectifier_bandwidth(rect, Pin_dBm=Pin_dBm,
                                 freq_center=freq_center_mhz * 1e6,
                                 freq_span=freq_span_mhz * 1e6)
    result['freqs_hz']  = result['freqs_hz'].tolist()
    result['pce']       = result['pce'].tolist()
    return result


@st.cache_data(show_spinner=False)
def run_link_budget(eirp_dbm: float = 70.0, dist_m: float = 100.0,
                    freq_ghz: float = 0.55) -> list:
    """Tabla de presupuesto de enlace con valores canónicos."""
    return link_budget_table(
        eirp_dbm=eirp_dbm, dist_m=dist_m, freq_ghz=freq_ghz,
        gain_dBi=CANONICAL['gain_dBi'],
        eta_mm=CANONICAL['eta_mm'],
        eta_imn=CANONICAL['eta_imn'],
        IL_dB=10 * np.log10(1.0 / max(CANONICAL['eta_imn'], 1e-10)),
        pce=CANONICAL['PCE'],
        eta_pmic=CANONICAL['eta_pmic'],
    )


@st.cache_data(show_spinner=False)
def run_supercap(P_dc_uW: float = None, E_ciclo_mJ: float = 259.25,
                 C_mF: float = 330.0, V_max: float = 3.3, V_min: float = 1.8,
                 ESR_ohm: float = 50.0, I_leak_uA: float = 1.0) -> dict:
    """Dimensionamiento del supercondensador."""
    if P_dc_uW is None:
        P_dc_uW = CANONICAL['P_dc_uW']
    sc = supercap_sizing(
        P_dc_uW=P_dc_uW,
        E_ciclo_J=E_ciclo_mJ * 1e-3,
        C_F=C_mF * 1e-3,
        V_max=V_max,
        V_min=V_min,
        ESR_ohm=ESR_ohm,
        I_leak_uA=I_leak_uA,
    )
    return {
        'C_mF':          sc.C_F * 1e3,
        'V_max':         sc.V_max,
        'V_min':         sc.V_min,
        'E_stored_mJ':   sc.E_stored_J * 1e3,
        'E_useful_mJ':   sc.E_useful_J * 1e3,
        'E_ciclo_mJ':    sc.E_ciclo_J * 1e3,
        'n_ciclos':      sc.n_ciclos,
        't_charge_s':    sc.t_charge_s,
        't_charge_min':  sc.t_charge_s / 60.0,
        'P_dc_uW':       sc.P_dc_uW,
        'ESR_ohm':       sc.ESR_ohm,
        'P_leak_uW':     sc.P_leak_uW,
        'eta_storage':   sc.eta_storage,
    }


@st.cache_data(show_spinner=False)
def run_state_of_art(pce_max_pct: float = None, pdc_uw: float = None) -> list:
    """Tabla comparativa con el estado del arte."""
    return get_state_of_art_table(
        pce_max=pce_max_pct,
        pin_dbm=-10.0,
        pdc_uw=pdc_uw if pdc_uw is not None else CANONICAL['P_dc_uW'],
    )
