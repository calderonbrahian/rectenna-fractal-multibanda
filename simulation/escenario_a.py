"""
Escenario A — Sierpinski Gasket it.3, 1.8–5.8 GHz.
Todas las funciones retornan dicts serializables para @st.cache_data.
"""

import numpy as np
import streamlit as st

from core.antenna import FractalAntenna
from core.rectifier import RectifierCircuit
from core.matching import LMatchNetwork
from configs.parametros import BANDS_A


@st.cache_data(show_spinner=False)
def run_bandas(topology: str = 'doubler', Pin_dBm: float = -10.0) -> list:
    """Análisis por banda objetivo — retorna lista de dicts."""
    ant = FractalAntenna('sierpinski', iterations=3)
    rec = RectifierCircuit(topology=topology)
    imn = LMatchNetwork(Z_src=50.0)
    resultados = []
    for banda, f in BANDS_A.items():
        za  = ant.impedance(f)
        s11 = float(ant.S11_dB(f))
        zd  = rec.diode.impedance(f)
        res = imn.design(f, Z_load=zd)
        gam = (res.VSWR - 1) / (res.VSWR + 1)
        pce = rec.PCE(Pin_dBm, f, IL_dB=res.insertion_loss_dB, gamma=gam)
        vdc = rec.output_voltage(Pin_dBm, f, IL_dB=res.insertion_loss_dB, gamma=gam) * 1000
        pout_uw = rec.output_power_uw(Pin_dBm, f, IL_dB=res.insertion_loss_dB, gamma=gam)
        resultados.append({
            'banda':   banda,
            'f_GHz':   round(f / 1e9, 3),
            'f_Hz':    f,
            'Za_real': round(za.real, 2),
            'Za_imag': round(za.imag, 2),
            's11_dB':  round(s11, 2),
            'IL_dB':   round(res.insertion_loss_dB, 3),
            'VSWR':    round(res.VSWR, 2),
            'PCE_pct': round(pce * 100, 2),
            'Vdc_mV':  round(vdc, 1),
            'Pout_uW': round(pout_uw, 3),
            'L_nH':    round(res.L * 1e9, 3),
            'C_pF':    round(res.C * 1e12, 3),
            'topo_imn': res.topology,
        })
    return resultados


@st.cache_data(show_spinner=False)
def run_sweep_freq(n_pts: int = 400, topology: str = 'doubler',
                   Pin_dBm: float = -10.0) -> dict:
    """Barrido en frecuencia 1.5–6.2 GHz para S11, ganancia e impedancia."""
    freqs = np.linspace(1.5e9, 6.2e9, n_pts)
    ant   = FractalAntenna('sierpinski', iterations=3)
    s11   = ant.S11_dB(freqs).tolist()
    gain  = ant.gain_dBi(freqs).tolist()
    za    = ant.impedance(freqs)
    return {
        'freqs_GHz': (freqs / 1e9).tolist(),
        's11_dB':    s11,
        'gain_dBi':  gain,
        'Za_real':   za.real.tolist(),
        'Za_imag':   za.imag.tolist(),
    }


@st.cache_data(show_spinner=False)
def run_pce_vs_pin(f_GHz: float = 2.45, topology: str = 'doubler',
                   Pin_range: tuple = (-30.0, 0.0), n_pts: int = 60) -> dict:
    """PCE y Vdc vs Pin para una frecuencia y topología dadas."""
    rec  = RectifierCircuit(topology=topology)
    imn  = LMatchNetwork(Z_src=50.0)
    f    = f_GHz * 1e9
    zd   = rec.diode.impedance(f)
    res  = imn.design(f, Z_load=zd)
    gam  = (res.VSWR - 1) / (res.VSWR + 1)
    pins = np.linspace(Pin_range[0], Pin_range[1], n_pts)
    pce  = [rec.PCE(p, f, IL_dB=res.insertion_loss_dB, gamma=gam) * 100 for p in pins]
    vdc  = [rec.output_voltage(p, f, IL_dB=res.insertion_loss_dB, gamma=gam) * 1000 for p in pins]
    return {
        'Pin_dBm': pins.tolist(),
        'PCE_pct': pce,
        'Vdc_mV':  vdc,
        'IL_dB':   round(res.insertion_loss_dB, 3),
    }


@st.cache_data(show_spinner=False)
def run_geometry(iterations: int = 3) -> list:
    """Puntos de la geometría Sierpinski para visualización."""
    ant = FractalAntenna('sierpinski', iterations=iterations)
    return ant.geometry_points(iterations)
