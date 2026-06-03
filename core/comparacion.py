"""
================================================================================
MÓDULO: Comparación de escenarios y validación vs literatura
================================================================================
Herramientas para contrastar:
    1. Escenario A (Sierpinski) vs Escenario B (FLPDA).
    2. El modelo independiente del rectificador frente a las mediciones
       experimentales de Wang et al. (2022) IEEE TAP.
    3. El diseño de la antena FLPDA Koch frente a la LPDA clásica
       de Carrel (1961).

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np


# ── Datos de referencia experimentales Wang et al. (2022) IEEE TAP ────────────
# Valores medidos en sustrato Duroid 5880 (tanδ = 0.0009), rectificador optimizado.
WANG2022 = {
    'freqs_GHz':   [1.84, 2.04, 2.36, 2.54, 3.30, 4.76, 5.80],
    'pce_percent': [44.4, 43.9, 45.4, 43.4, 36.1, 32.4, 28.3],
    'S11_dB':      [-14,  -13,  -16,  -12,  -11,  -10,   -9],
    'gain_dBi':    [ 2.1,  2.2,  2.3,  2.2,  2.0,  1.9,  1.8],
}

# ── Datos de referencia teóricos Carrel (1961) para LPDA ──────────────────────
CARREL1961 = {
    'tau': 0.90,       # valor de diseño elegido
    'sigma': 0.15,     # valor de diseño elegido
    'gain_dBi': 8.0,   # ganancia típica media
    'BW_ratio': 900.0 / 470.0,
    'S11_max_dB': -10,
}


def compare_scenarios(antenna_a, flpda_b, rectifier_a) -> dict:
    """
    Compara métricas clave globales: Escenario A vs Escenario B.
    """
    freqs_a = np.array(WANG2022['freqs_GHz']) * 1e9
    freqs_b = np.linspace(flpda_b.f_low, flpda_b.f_high, 9)

    s11_a  = np.array([float(antenna_a.S11_dB(f))  for f in freqs_a])
    gain_a = np.array([float(antenna_a.gain_dBi(f)) for f in freqs_a])
    pce_a  = np.array([rectifier_a.PCE(-10.0, f) * 100 for f in freqs_a])

    s11_b  = np.array([float(flpda_b.S11_dB(f))  for f in freqs_b])
    gain_b = np.array([float(flpda_b.gain_dBi(f)) for f in freqs_b])

    return {
        'escenario_A': {
            'freqs_GHz': freqs_a / 1e9,
            'S11_dB': s11_a,
            'gain_dBi': gain_a,
            'PCE_percent': pce_a,
            'mean_PCE': float(np.mean(pce_a)),
            'min_S11': float(np.min(s11_a)),
        },
        'escenario_B': {
            'freqs_GHz': freqs_b / 1e9,
            'S11_dB': s11_b,
            'gain_dBi': gain_b,
            'mean_gain': float(np.mean(gain_b)),
            'min_S11': float(np.min(s11_b)),
            'boom_m': flpda_b.boom_length_m,
            'max_element_cm': flpda_b.max_element_length_m * 100,
            'n_elementos': flpda_b.n_elements,
        },
    }


def validate_wang2022(rectifier, matching_net=None) -> dict:
    """
    Validación de PCE del modelo analítico vs mediciones de Wang et al. (2022).
    La simulación usa FR-4 (tanδ=0.02) vs Duroid 5880 experimental.

    Si matching_net no es None, calcula IL y gamma dinámicamente.
    """
    freqs   = np.array(WANG2022['freqs_GHz']) * 1e9
    pce_ref = np.array(WANG2022['pce_percent'])
    pce_sim = []

    for f in freqs:
        if matching_net:
            Zd  = rectifier.diode.impedance(f)
            res = matching_net.design(f, Z_load=Zd)
            gam = (res.VSWR - 1.0) / (res.VSWR + 1.0)
            pce = rectifier.PCE(-10.0, f, IL_dB=res.insertion_loss_dB, gamma=gam)
        else:
            pce = rectifier.PCE(-10.0, f)
        pce_sim.append(pce * 100)

    pce_sim = np.array(pce_sim)
    err_abs = pce_sim - pce_ref
    err_rel = err_abs / pce_ref * 100

    return {
        'freqs_GHz': WANG2022['freqs_GHz'],
        'pce_referencia': pce_ref.tolist(),
        'pce_simulacion': np.round(pce_sim, 2).tolist(),
        'error_abs_pp': np.round(err_abs, 2).tolist(),
        'error_rel_pct': np.round(err_rel, 1).tolist(),
        'RMSE': float(np.sqrt(np.mean(err_abs ** 2))),
        'max_error_abs': float(np.max(np.abs(err_abs))),
        'mean_error_abs': float(np.mean(err_abs)),
    }


def validate_carrel1961(flpda) -> dict:
    """
    Validación de diseño FLPDA Koch vs LPDA clásica (Carrel 1961).
    """
    test_freqs = np.linspace(flpda.f_low, flpda.f_high, 10)
    gain_avg   = float(np.mean([float(flpda.gain_dBi(f)) for f in test_freqs]))
    s11_min    = float(np.min([float(flpda.S11_dB(f))
                               for f in np.linspace(flpda.f_low, flpda.f_high, 50)]))

    return {
        'tau_disenio': flpda.tau,
        'tau_Carrel': CARREL1961['tau'],
        'sigma_disenio': flpda.sigma,
        'sigma_Carrel': CARREL1961['sigma'],
        'ganancia_media_dBi': round(gain_avg, 2),
        'ganancia_Carrel_dBi': CARREL1961['gain_dBi'],
        'S11_min_dB': round(s11_min, 2),
        'S11_Carrel_dB': CARREL1961['S11_max_dB'],
        'BW_ratio_disenio': round(flpda.f_high / flpda.f_low, 3),
        'BW_ratio_Carrel': round(CARREL1961['BW_ratio'], 3),
        'reduccion_Koch_pct': round((1 - flpda.k_red) * 100, 1),
        'n_elementos': flpda.n_elements,
    }
