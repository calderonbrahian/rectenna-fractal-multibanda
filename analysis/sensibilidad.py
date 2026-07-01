"""
Análisis de sensibilidad paramétrica.
Barridos sobre parámetros clave del sistema.
"""

import numpy as np
import streamlit as st

from core.rectifier import RectifierCircuit
from core.matching import LMatchNetwork
from core.flpda import FLPDA_Koch
from core.comparacion import validate_wang2022


@st.cache_data(show_spinner=False)
def sweep_Q_L(Q_L_range: tuple = (10.0, 100.0), n_pts: int = 40,
              f_GHz: float = 2.45, topology: str = 'doubler',
              Pin_dBm: float = -10.0) -> dict:
    """Barrido de PCE vs factor Q del inductor SMD."""
    qs   = np.linspace(Q_L_range[0], Q_L_range[1], n_pts)
    pces = []
    ils  = []
    f    = f_GHz * 1e9
    for q in qs:
        LMatchNetwork.Q_L = q
        imn  = LMatchNetwork(Z_src=50.0)
        rec  = RectifierCircuit(topology=topology)
        zd   = rec.diode.impedance(f)
        res  = imn.design(f, Z_load=zd)
        gam  = (res.VSWR - 1) / (res.VSWR + 1)
        pces.append(rec.PCE(Pin_dBm, f, IL_dB=res.insertion_loss_dB, gamma=gam) * 100)
        ils.append(res.insertion_loss_dB)
    LMatchNetwork.Q_L = 40.0  # restaurar default
    return {'Q_L': qs.tolist(), 'PCE_pct': pces, 'IL_dB': ils}


@st.cache_data(show_spinner=False)
def sweep_R_load(R_range: tuple = (200.0, 5000.0), n_pts: int = 50,
                 f_GHz: float = 2.45, topology: str = 'doubler',
                 Pin_dBm: float = -10.0) -> dict:
    """Barrido de PCE y Vdc vs resistencia de carga."""
    rs   = np.linspace(R_range[0], R_range[1], n_pts)
    pces = []
    vdcs = []
    f    = f_GHz * 1e9
    imn  = LMatchNetwork(Z_src=50.0)
    for r in rs:
        rec  = RectifierCircuit(topology=topology, R_load=r)
        zd   = rec.diode.impedance(f)
        res  = imn.design(f, Z_load=zd)
        gam  = (res.VSWR - 1) / (res.VSWR + 1)
        pces.append(rec.PCE(Pin_dBm, f, IL_dB=res.insertion_loss_dB, gamma=gam) * 100)
        vdcs.append(rec.output_voltage(Pin_dBm, f, IL_dB=res.insertion_loss_dB, gamma=gam) * 1000)
    return {'R_load_ohm': rs.tolist(), 'PCE_pct': pces, 'Vdc_mV': vdcs}


@st.cache_data(show_spinner=False)
def sweep_tau_sigma(tau_range: tuple = (0.80, 0.95), sigma_range: tuple = (0.10, 0.22),
                    n_pts: int = 15) -> dict:
    """Mapa de color: ganancia media FLPDA vs tau y sigma."""
    taus   = np.linspace(tau_range[0], tau_range[1], n_pts)
    sigmas = np.linspace(sigma_range[0], sigma_range[1], n_pts)
    freqs  = np.linspace(470e6, 900e6, 20)
    gain_map   = np.zeros((n_pts, n_pts))
    n_elem_map = np.zeros((n_pts, n_pts), dtype=int)
    for i, tau in enumerate(taus):
        for j, sig in enumerate(sigmas):
            try:
                flpda = FLPDA_Koch(tau=tau, sigma=sig)
                gains = [float(flpda.gain_dBi(f)) for f in freqs]
                gain_map[i, j]   = float(np.mean(gains))
                n_elem_map[i, j] = flpda.n_elements
            except Exception:
                gain_map[i, j] = 0.0
    return {
        'taus':      taus.tolist(),
        'sigmas':    sigmas.tolist(),
        'gain_map':  gain_map.tolist(),
        'n_elem_map': n_elem_map.tolist(),
    }


@st.cache_data(show_spinner=False)
def run_validacion_wang(topology: str = 'doubler') -> dict:
    """Validación PCE modelo vs Wang et al. (2022) IEEE TAP.

    Metodología canónica del documento (§4.5): comparación en régimen de
    **adaptación ideal** (matching_net=None) → RMSE = 15,50 pp, consistente con
    CANONICAL['RMSE_wang'], la Tabla 11, la Figura 11 y el test de regresión.
    (Antes pasaba una red L real, lo que daba 22,68 pp y contradecía el texto
    de la propia página.)
    """
    rec = RectifierCircuit(topology=topology)
    return validate_wang2022(rec, matching_net=None)
