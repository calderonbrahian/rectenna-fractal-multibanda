"""
================================================================================
MÓDULO: Presupuesto de Potencia LoRa — Escenario B
================================================================================
Cálculo del presupuesto de enlace (Friis) y factibilidad de operación de
un nodo LoRa sin batería alimentado por RF Energy Harvesting (UHF 470–900 MHz).

Modelo PMIC:
    Texas Instruments BQ25504 boost-converter con arranque en frío
    (cold-start) V_in ≥ 130 mV y eficiencia de conversión η_PMIC = 0.85.

Modelos de consumo (LoRa/IoT):
    Basados en Semtech SX1276 datasheet. El consumo promedio se calcula
    ponderando la corriente activa (Tx/Rx) por el duty cycle (típicamente 1%)
    y sumando la corriente de sleep profunda.

──────────────────────────────────────────────────────────────────────────────
 IMPORTANTE — Dualidad PCE en este módulo
──────────────────────────────────────────────────────────────────────────────
Existen DOS funciones distintas para calcular la potencia cosechada:

  1. harvested_uw()        → usa pce_uhf() (aproximación tanh, PCE_max 55%)
                             Es una estimación CONSERVADORA promediada sobre
                             la banda 470–900 MHz. Útil para diseño rápido y
                             para descartar viabilidad en escenarios
                             desfavorables.

  2. harvested_uw_full()   → usa rectifier.PCE() (Shockley iterativo,
                             clipeado físicamente en 85%). Es el método
                             CANÓNICO usado para los resultados oficiales
                             reportados en la tesis (CANONICAL['P_dc_uW']
                             = 1637,6 µW @ 100 m del Cerro Nutibara).

Si los resultados de las dos funciones difieren significativamente, es
esperado: la segunda incluye desglose por eslabón (η_rad, η_mm, η_imn,
PCE_rect, η_PMIC) y refleja la cadena RF→DC completa.

──────────────────────────────────────────────────────────────────────────────
 Default ant_gain_dBi = 7.5 dBi
──────────────────────────────────────────────────────────────────────────────
El default 7.5 dBi corresponde a la ganancia MEDIA de la FLPDA Koch it.2
sobre toda la banda 470–900 MHz (referencia Carrel 1961: 8.0 dBi). Para
cálculos puntuales a una frecuencia específica (p. ej. 7.10 dBi @ 550 MHz),
usar harvested_uw_full() que toma la ganancia desde antenna.gain_dBi(f).
──────────────────────────────────────────────────────────────────────────────

Referencias:
    Pozar, Microwave Engineering 4ed, eq. 2.6 (Ecuación de Friis)
    Texas Instruments BQ25504 datasheet, SLUSCY3
    Semtech SX1276 datasheet

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np

C0 = 3e8  # velocidad de la luz [m/s]

# ── Constantes PMIC (BQ25504 boost-converter) ─────────────────────────────────
ETA_PMIC          = 0.85   # eficiencia del conversor boost DC-DC
V_COLDSTART_MIN_V = 0.130  # voltaje mínimo de arranque en frío [V] = 130 mV
RL_EQUIV          = 1300.0 # resistencia de carga equivalente del rectificador [Ω]


# ── Fuentes RF en banda UHF (470–900 MHz) ─────────────────────────────────────
RF_SOURCES_UHF = {
    'TV UHF (DVB-T)':          {'eirp_dbm': 70.0, 'freq_ghz': 0.550, 'color': '#8b5cf6'},  # ej. Cerro Nutibara 10kW
    'LTE Macro 700 MHz':       {'eirp_dbm': 46.0, 'freq_ghz': 0.700, 'color': '#f59e0b'},
    'LTE Band 28 (700 MHz)':   {'eirp_dbm': 43.0, 'freq_ghz': 0.700, 'color': '#f97316'},
    'LoRa Gateway (Colombia)':     {'eirp_dbm': 27.0, 'freq_ghz': 0.915, 'color': '#06b6d4'},
}


# ── Perfiles LoRa — consumo promedio ponderado por duty cycle ─────────────────
# Semtech SX1276: Tx=120 mA @20 dBm, Rx=11 mA, Sleep=1.5 µA (Vdd=3.3V)
LORA_PROFILES = {
    'LoRa SF12 BW125 (1% DC)': {
        'P_tx_mw': 120.0, 'P_rx_mw': 11.0, 'P_sleep_uw': 1.5,
        'dc_tx': 0.003, 'dc_rx': 0.007, 'color': '#0d9488',
    },
    'LoRa SF9 BW125 (1% DC)': {
        'P_tx_mw': 120.0, 'P_rx_mw': 11.0, 'P_sleep_uw': 1.5,
        'dc_tx': 0.001, 'dc_rx': 0.004, 'color': '#0891b2',
    },
    'LoRa SF7 BW250 (1% DC)': {
        'P_tx_mw': 100.0, 'P_rx_mw': 9.5, 'P_sleep_uw': 1.5,
        'dc_tx': 0.0003, 'dc_rx': 0.002, 'color': '#6366f1',
    },
    'Sensor ADC (solo lectura)': {
        'P_tx_mw': 0.0, 'P_rx_mw': 0.0, 'P_sleep_uw': 1.2,
        'dc_tx': 0.0, 'dc_rx': 0.0, 'color': '#16a34a',
    },
}


def avg_power_uw(profile: dict) -> float:
    """Consumo promedio ponderado [µW] de un perfil IoT basado en duty cycle."""
    return max(
        profile['dc_tx'] * profile['P_tx_mw'] * 1e3
        + profile['dc_rx'] * profile['P_rx_mw'] * 1e3
        + (1 - profile['dc_tx'] - profile['dc_rx']) * profile['P_sleep_uw'],
        0.0,
    )


# ── Presupuesto de enlace y propagación ───────────────────────────────────────

def fspl_dB(dist_m: float, freq_ghz: float) -> float:
    """
    Pérdida de trayecto en espacio libre (FSPL) [dB].
    FSPL = 20·log10(4π·d / λ).

    Raises
    ------
    ValueError : si dist_m ≤ 0 o freq_ghz ≤ 0.
    """
    if dist_m <= 0:
        raise ValueError(f'Distancia debe ser > 0 m, recibido: {dist_m}')
    if freq_ghz <= 0:
        raise ValueError(f'Frecuencia debe ser > 0 GHz, recibido: {freq_ghz}')
    lam = C0 / (freq_ghz * 1e9)
    return 20 * np.log10(4 * np.pi * dist_m / lam)


URBAN_CORRECTION_DB = 6.0  # ITU-R P.1546, entorno urbano denso

def received_power_dBm(eirp_dbm: float, dist_m: float, freq_ghz: float,
                       ant_gain_dBi: float = 7.5) -> float:
    """
    Potencia recibida [dBm] (Friis).
    Incluye corrección de entorno urbano (ITU-R P.1546) sobre espacio libre.
    Ganancia por defecto = 7.5 dBi (FLPDA Koch it.2 media).
    """
    return eirp_dbm - fspl_dB(dist_m, freq_ghz) - URBAN_CORRECTION_DB + ant_gain_dBi


# ── Modelado del cosechador RF-DC ─────────────────────────────────────────────

def pce_uhf(Pin_dBm: float) -> float:
    """
    Eficiencia de conversión PCE [0..1] para el rectificador doubler (SMS7630)
    en banda UHF (470–900 MHz).

    Modelo: tangente hiperbólica calibrada numéricamente contra el modelo
    físico de Shockley (RectifierCircuit.PCE) promediado sobre 470–900 MHz.
    Parámetros: PCE_max = 55%, punto de inflexión = −12 dBm, ancho = 6 dB.

    Calibración: evaluado a Pin ∈ [−30, 0] dBm en la banda UHF con R_load=1300 Ω,
    topología 'doubler', SMS7630. Para Pin >> 0 dBm (fuentes muy cercanas como TDT
    a < 200 m) el modelo Shockley clipa en 85%; la función tanh da estimación más
    conservadora (~55%) apropiada para diseño de sistema.

    Limitación: NO usar fuera de banda UHF. Para otras frecuencias, usar
    directamente RectifierCircuit.PCE(Pin_dBm, freq) del módulo rectifier.
    """
    return 0.55 * (1.0 + np.tanh((Pin_dBm - (-12.0)) / 6.0)) / 2.0


def harvested_uw(eirp_dbm: float, dist_m: float, freq_ghz: float,
                 ant_gain_dBi: float = 7.5,
                 pce_fn=None) -> float:
    """
    Potencia DC útil final [µW] disponible para la carga IoT.

    Cadena de cosechamiento modelada:
        1. Pr(dBm) = Friis (ecuación 2.6, Pozar) + corrección urbana ITU-R P.1546
        2. PCE  = pce_fn(Pr_dBm) si se provee, si no → pce_uhf(Pr_dBm)
        3. P_RF_dc = PCE × Pr_W
        4. V_dc = √(P_RF_dc × R_load)
        5. Cold-start BQ25504: si V_dc < 130 mV → P_útil = 0
        6. Operación normal: P_útil = P_RF_dc × η_PMIC [µW]

    Parámetros
    ----------
    eirp_dbm    : EIRP de la fuente transmisora [dBm]
    dist_m      : distancia fuente–antena [m]
    freq_ghz    : frecuencia de operación [GHz]
    ant_gain_dBi: ganancia de la antena receptora [dBi] (default 7.5 dBi FLPDA)
    pce_fn      : función PCE alternativa callable(Pin_dBm) → PCE [0..1].
                  Si None, usa pce_uhf() calibrada para banda UHF.
                  Ejemplo: pce_fn=lambda p: rectifier.PCE(p, 700e6)
    """
    Pr_dBm  = received_power_dBm(eirp_dbm, dist_m, freq_ghz, ant_gain_dBi)
    Pr_W    = 10.0 ** (Pr_dBm / 10.0) * 1e-3

    pce     = pce_fn(Pr_dBm) if pce_fn is not None else pce_uhf(Pr_dBm)
    P_rf_dc = max(pce * Pr_W, 0.0)

    Vdc_est = np.sqrt(P_rf_dc * RL_EQUIV)

    if Vdc_est < V_COLDSTART_MIN_V:
        return 0.0

    return P_rf_dc * ETA_PMIC * 1e6


def harvested_uw_full(eirp_dbm: float, dist_m: float, freq_ghz: float,
                      antenna, rectifier, matching_net=None,
                      eta_pmic: float = ETA_PMIC) -> dict:
    """
    Potencia DC útil final [µW] con cadena completa desglosada.

    Cadena: EIRP → FSPL + urbano → P_RF → η_mm → η_imn → PCE_rect → η_PMIC → P_DC.

    Todos los factores se calculan desde los modelos físicos, sin función tanh
    aproximada. Esta función es la canónica para resultados de tesis.

    Parámetros
    ----------
    eirp_dbm     : EIRP de la fuente transmisora [dBm]
    dist_m       : distancia fuente–antena [m]
    freq_ghz     : frecuencia de operación [GHz]
    antenna      : instancia FractalAntenna o FLPDA_Koch (con .gain_dBi, .S11_dB, .eta_rad)
    rectifier    : instancia RectifierCircuit (con .PCE, .diode.impedance)
    matching_net : instancia LMatchNetwork (opcional; si None, asume IMN ideal)
    eta_pmic     : eficiencia del PMIC [0..1] (default BQ25504 = 0.85)

    Retorna
    -------
    dict con todos los eslabones de la cadena:
        'P_rf_dBm', 'P_rf_uW', 'gain_dBi', 'eta_rad', 'eta_mm',
        'eta_imn', 'IL_dB', 'PCE', 'eta_pmic', 'P_dc_uW',
        'V_dc_mV', 'eta_total', 'coldstart_ok'
    """
    freq_hz = freq_ghz * 1e9

    # 1. Ganancia realizada de la antena (ya incluye η_rad)
    gain = float(antenna.gain_dBi(freq_hz))
    eta_r = float(antenna.eta_rad(freq_hz))

    # 2. Potencia recibida (Friis + corrección urbana)
    P_rf_dBm = eirp_dbm - fspl_dB(dist_m, freq_ghz) - URBAN_CORRECTION_DB + gain
    P_rf_W   = 10.0 ** (P_rf_dBm / 10.0) * 1e-3

    # 3. η_mm = 1 − |Γ_ant|² desde S11 de la antena
    s11_db  = float(antenna.S11_dB(freq_hz))
    gamma_sq = 10.0 ** (s11_db / 10.0)
    eta_mm  = max(1.0 - gamma_sq, 0.0)

    # 4. η_imn: pérdida de inserción de la red L
    if matching_net is not None:
        try:
            Zd  = rectifier.diode.impedance(freq_hz)
            res = matching_net.design(freq_hz, Z_load=Zd)
            il_dB = res.insertion_loss_dB
            gamma_imn = (res.VSWR - 1.0) / (res.VSWR + 1.0)
        except Exception:
            il_dB = 0.23   # valor típico stub microstrip
            gamma_imn = 0.0
    else:
        il_dB = 0.23       # valor nominal tesis (stub microstrip UHF-FR-4)
        gamma_imn = 0.0
    eta_imn = (1.0 - gamma_imn ** 2) * 10.0 ** (-il_dB / 10.0)

    # 5. Potencia entregada al rectificador
    P_avail_W = P_rf_W * eta_mm * eta_imn
    P_avail_dBm = 10.0 * np.log10(max(P_avail_W, 1e-15) * 1e3)

    # 6. PCE del rectificador (modelo Shockley)
    pce = rectifier.PCE(P_avail_dBm, freq_hz)

    # 7. P_DC bruta y con PMIC
    P_dc_W = P_avail_W * pce * eta_pmic
    P_dc_uW = P_dc_W * 1e6

    # 8. Voltaje DC estimado
    V_dc = np.sqrt(max(P_dc_W * RL_EQUIV, 0.0))
    V_dc_mV = V_dc * 1e3

    # 9. Cold-start check
    coldstart_ok = V_dc >= V_COLDSTART_MIN_V

    # η_total del sistema completo
    eta_total = eta_r * eta_mm * eta_imn * pce * eta_pmic

    return {
        'P_rf_dBm':     float(P_rf_dBm),
        'P_rf_uW':      float(P_rf_W * 1e6),
        'gain_dBi':     gain,
        'eta_rad':      eta_r,
        'eta_mm':       float(eta_mm),
        'eta_imn':      float(eta_imn),
        'IL_dB':        float(il_dB),
        'PCE':          float(pce),
        'eta_pmic':     eta_pmic,
        'P_dc_uW':     float(P_dc_uW),
        'V_dc_mV':     float(V_dc_mV),
        'eta_total':    float(eta_total),
        'coldstart_ok': coldstart_ok,
    }


def supercap_time_s(pout_uw: float, C_F: float = 0.33,
                    V_min: float = 1.8, V_max: float = 3.3) -> float:
    """
    Tiempo de carga [s] de un supercondensador en la ventana operativa V_min→V_max.

    Energía útil entre V_min y V_max (Ec. E.5 del documento):
        E_util = ½·C·(V_max² − V_min²)  →  t = E_util / P_DC.

    Con C = 0,33 F, V_min = 1,8 V, V_max = 3,3 V y P_DC = 1637,6 µW:
        E_util = 1262,2 mJ  →  t ≈ 770,8 s ≈ 12,8 min.
    """
    if pout_uw <= 0:
        return float('inf')
    return 0.5 * C_F * (V_max ** 2 - V_min ** 2) / (pout_uw * 1e-6)
