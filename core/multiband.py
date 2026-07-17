"""
================================================================================
MÓDULO: Cosecha multibanda integrada — Escenario A (rectena difusa urbana)
================================================================================
Modelo de una rectena INTEGRADA multibanda: la antena fractal (Sierpinski) se
conecta directamente, vía adaptación conjugada por banda, a un banco de
rectificadores combinados en DC. A diferencia del Escenario B (dirigida,
modular, línea de 50 Ω), aquí NO hay interfaz forzada de 50 Ω: la "reflexión de
la antena" deja de ser pérdida y solo cuenta la pérdida por Q finito de la red
(ver core.matching.LMatchNetwork.conjugate_efficiency y
_regen/FASE0_factibilidad_multibanda.md).

Arquitectura implícita (declarada como limitación): una sola red pasiva no
adapta todas las bandas a la vez (límite de Bode-Fano), por lo que se modela un
RECTIFICADOR MULTIBANDA de varias ramas — una rama antena→red→diodo por banda —
combinadas en DC. Referencias: Valenta & Durgin (2014) IEEE MTT-S (rectenas
integradas); Piñuela et al. (2013) IEEE TMTT (potencia RF ambiental urbana).

Este módulo es el análogo multibanda de core.lora_budget (que cubre el enlace
dirigido del Escenario B). No altera ningún valor canónico del Escenario B.

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np

from core.antenna import FractalAntenna
from core.rectifier import RectifierCircuit
from core.matching import LMatchNetwork
from configs.parametros import (
    BANDS_A, URBAN_AMBIENT_DBM, URBAN_AMBIENT_NOMINAL_DBM,
    BQ25504_ETA_PMIC as ETA_PMIC,
)


def harvest_per_band(antenna, rectifier, matching_net,
                     ambient_dbm: dict = None,
                     eta_pmic: float = ETA_PMIC) -> list:
    """
    Potencia DC cosechada por banda con co-diseño conjugado integrado.

    Cadena por banda: P_amb (puerto antena) → η_conjugado(Za→Zdiodo) → PCE(Shockley)
    → η_PMIC → P_dc. Las ramas se combinan en DC (suma de potencias).

    Parámetros
    ----------
    antenna      : FractalAntenna (Sierpinski) con .impedance(f)
    rectifier    : RectifierCircuit (SMS7630 doblador) con .diode.impedance(f)
    matching_net : LMatchNetwork con .conjugate_efficiency(f, Za, Zd)
    ambient_dbm  : dict {banda: P_amb_dBm}; default configs.URBAN_AMBIENT_DBM
    eta_pmic     : eficiencia del PMIC [0..1]

    Retorna lista de dicts por banda con eta_cm, PCE, P_dc_uW, etc.
    """
    amb = ambient_dbm if ambient_dbm is not None else URBAN_AMBIENT_DBM
    filas = []
    for banda, f in BANDS_A.items():
        p_amb_dbm = float(amb[banda])
        za = antenna.impedance(f)
        zd = rectifier.diode.impedance(f)
        eta_cm = matching_net.conjugate_efficiency(f, za, zd)
        il_cm_db = -10.0 * np.log10(max(eta_cm, 1e-6))
        pce = rectifier.PCE(p_amb_dbm, f, IL_dB=il_cm_db, gamma=0.0)
        p_dc_rect_uw = rectifier.output_power_uw(p_amb_dbm, f, IL_dB=il_cm_db, gamma=0.0)
        p_dc_uw = p_dc_rect_uw * eta_pmic
        filas.append({
            'banda':      banda,
            'f_GHz':      round(f / 1e9, 3),
            'P_amb_dBm':  round(p_amb_dbm, 1),
            'eta_cm':     round(eta_cm, 4),
            'PCE_pct':    round(pce * 100, 2),
            'P_dc_uW':    round(p_dc_uw, 4),
        })
    return filas


def harvest_total_uw(antenna, rectifier, matching_net,
                     ambient_dbm: dict = None,
                     eta_pmic: float = ETA_PMIC) -> float:
    """Potencia DC total [µW] cosechada sumando todas las bandas (combinación DC)."""
    filas = harvest_per_band(antenna, rectifier, matching_net, ambient_dbm, eta_pmic)
    return float(sum(fila['P_dc_uW'] for fila in filas))


def harvest_vs_ambient(antenna, rectifier, matching_net,
                       amb_range_dbm=(-40.0, -5.0), n_pts: int = 40,
                       eta_pmic: float = ETA_PMIC) -> dict:
    """
    Curva de potencia DC total cosechada frente al nivel ambiental UNIFORME por
    banda (todas las bandas al mismo P_amb). Es la métrica honesta de viabilidad:
    en vez de fijar un único valor de ambiente, se muestra cómo escala la cosecha
    con el nivel supuesto, acotado por el rango de Piñuela et al. (2013).
    """
    niveles = np.linspace(amb_range_dbm[0], amb_range_dbm[1], n_pts)
    total = []
    for lvl in niveles:
        amb = {b: float(lvl) for b in BANDS_A}
        total.append(harvest_total_uw(antenna, rectifier, matching_net, amb, eta_pmic))
    return {'P_amb_dBm': niveles.tolist(), 'P_dc_total_uW': total}


def min_ambient_for_load(antenna, rectifier, matching_net,
                         avg_load_uw: float,
                         amb_range_dbm=(-45.0, 0.0), n_pts: int = 90,
                         eta_pmic: float = ETA_PMIC) -> float:
    """
    Nivel ambiental UNIFORME mínimo [dBm/banda] para que la cosecha total iguale
    el consumo medio de un sensor (avg_load_uw). Devuelve np.nan si ni el extremo
    superior del rango alcanza. Es el puente de viabilidad del modo energía-asistido.
    """
    niveles = np.linspace(amb_range_dbm[0], amb_range_dbm[1], n_pts)
    for lvl in niveles:
        amb = {b: float(lvl) for b in BANDS_A}
        if harvest_total_uw(antenna, rectifier, matching_net, amb, eta_pmic) >= avg_load_uw:
            return float(lvl)
    return float('nan')


def energy_assisted_viability(p_harvest_uw: float, avg_load_uw: float) -> dict:
    """
    Criterio de viabilidad del MODO ENERGÍA-ASISTIDO (operación net-positive /
    energy-neutral): a diferencia del modo sin-batería (potencia continua ≥
    umbral), aquí basta con que la potencia MEDIA cosechada supere el consumo
    MEDIO del sensor con ciclo de trabajo bajo. La batería/supercap solo hace de
    tampón para los picos de transmisión; si el balance medio es positivo, nunca
    se descarga por completo.

    Devuelve el margen de energía (razón cosecha/consumo) y si es viable.
    """
    margen = p_harvest_uw / avg_load_uw if avg_load_uw > 0 else float('inf')
    return {
        'P_harvest_uW':  round(p_harvest_uw, 3),
        'P_load_avg_uW': round(avg_load_uw, 3),
        'margen':        round(margen, 2),
        'viable':        bool(p_harvest_uw >= avg_load_uw),
    }


def max_duty_cycle(p_harvest_uw: float, e_ciclo_mj: float) -> float:
    """
    Mensajes/hora máximos que el balance energético sostiene: con energía por
    ciclo E_ciclo [mJ] y cosecha media P_harvest [µW], el número sostenible de
    ciclos por hora es N = P_harvest·3600 / E_ciclo. Traduce la cosecha en una
    frecuencia de operación (el ciclo de trabajo que el sensor puede permitirse).
    """
    p_w = p_harvest_uw * 1e-6
    e_j = e_ciclo_mj * 1e-3
    return float(p_w * 3600.0 / e_j) if e_j > 0 else 0.0


def build_default():
    """Instancias por defecto del Escenario A urbano difuso."""
    ant = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)
    rec = RectifierCircuit(topology='doubler', R_load=1300.0)
    imn = LMatchNetwork(Z_src=50.0)
    return ant, rec, imn


# ── Rigor estadístico (paridad con la FLPDA: Monte Carlo + tornado) ───────────
# La eficiencia de acople conjugado por banda NO depende del ambiente ni de R_load
# (solo de Za(f) y Zd(f)), así que se precalcula una vez para que el Monte Carlo de
# 10.000 muestras sea rápido.

def eta_cm_cache(antenna, rectifier, matching_net) -> list:
    """Precalcula [(banda, f_Hz, η_cm)] una sola vez."""
    out = []
    for banda, f in BANDS_A.items():
        za = antenna.impedance(f)
        zd = rectifier.diode.impedance(f)
        out.append((banda, f, matching_net.conjugate_efficiency(f, za, zd)))
    return out


def harvest_from_cache(eta_list, rectifier, amb_dbm_uniform: float,
                       eta_pmic: float = ETA_PMIC) -> float:
    """Cosecha total [µW] con η_cm precalculado y ambiente uniforme."""
    total = 0.0
    for _, f, eta_cm in eta_list:
        il = -10.0 * np.log10(max(eta_cm, 1e-6))
        total += rectifier.output_power_uw(amb_dbm_uniform, f, IL_dB=il, gamma=0.0) * eta_pmic
    return total


def monte_carlo_harvest(antenna, rectifier, matching_net,
                        amb_nominal_dbm: float = None, amb_std_db: float = 5.0,
                        n_samples: int = 10000, seed: int = 42) -> dict:
    """
    Propagación de incertidumbre Monte Carlo sobre la cosecha multibanda total.
    La incertidumbre DOMINANTE es el nivel RF ambiental (muy variable en ciudad),
    modelado normal en dB (equivale a log-normal en potencia), std=5 dB. Análogo
    al Monte Carlo de la FLPDA (que varía EIRP y distancia). Determinista (seed).
    """
    from core.analysis import monte_carlo_pdc
    from configs.parametros import URBAN_AMBIENT_NOMINAL_DBM
    amb0 = URBAN_AMBIENT_NOMINAL_DBM if amb_nominal_dbm is None else amb_nominal_dbm
    eta_list = eta_cm_cache(antenna, rectifier, matching_net)

    def compute(params):
        return harvest_from_cache(eta_list, rectifier, params['amb_dbm'])

    base = {'amb_dbm': amb0}
    unc = {'amb_dbm': {'type': 'normal', 'std': amb_std_db}}
    res = monte_carlo_pdc(base, unc, compute, n_samples=n_samples, seed=seed)
    res['samples'] = res['samples'].tolist()
    return res


def tornado_harvest(antenna, rectifier, matching_net,
                    amb_nominal_dbm: float = None) -> dict:
    """Sensibilidad tipo tornado de la cosecha total frente a ambiente, Q y R_load."""
    from core.analysis import sensitivity_tornado
    from configs.parametros import URBAN_AMBIENT_NOMINAL_DBM
    amb0 = URBAN_AMBIENT_NOMINAL_DBM if amb_nominal_dbm is None else amb_nominal_dbm

    def compute(params):
        LMatchNetwork.Q_L = params['Q_ind']
        imn = LMatchNetwork(Z_src=50.0)
        rec = RectifierCircuit(topology='doubler', R_load=params['R_load'])
        eta_list = eta_cm_cache(antenna, rec, imn)
        val = harvest_from_cache(eta_list, rec, params['amb_dbm'])
        LMatchNetwork.Q_L = 40.0
        return val

    base = {'amb_dbm': amb0, 'Q_ind': 40.0, 'R_load': 1300.0}
    deltas = {'amb_dbm': 5.0, 'Q_ind': 15.0, 'R_load': 300.0}
    return sensitivity_tornado(base, deltas, compute, 'Cosecha total [µW]')
