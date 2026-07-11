"""
================================================================================
CONFIGURACIÓN CENTRALIZADA — Rectenna Fractal Multibanda v3
================================================================================
Constantes físicas, parámetros de diseño y configuración de figuras APA7.

    from configs.parametros import *

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

# ── Constantes físicas ────────────────────────────────────────────────────────
C0    = 3e8           # velocidad de la luz en vacío [m/s]
Q_E   = 1.602e-19     # carga del electrón [C]
K_B   = 1.381e-23     # constante de Boltzmann [J/K]
T_AMB = 300.0         # temperatura ambiente [K]
VT    = K_B * T_AMB / Q_E   # voltaje térmico ≈ 25.85 mV [V]

# ── Sustrato FR-4 (Bahl & Trivedi 1977; Pozar cap. 3; datasheets Isola/Shengyi) ──
FR4_ER_1GHZ  = 4.4    # εr @ 1 GHz
FR4_ER_58GHZ = 4.1    # εr @ 5.8 GHz
FR4_LOSS_TAN = 0.02   # tangente de pérdidas (tan δ) nominal @ 1 GHz
FR4_H_M      = 1.6e-3 # espesor del sustrato [m]

def fr4_er(f_hz: float) -> float:
    """εr(f) del FR-4 (material dispersivo): 4,4 @1 GHz → 4,1 @5,8 GHz.
    Datasheets Isola/Shengyi: εr decrece con la frecuencia en microondas."""
    fghz = f_hz / 1e9
    t = min(max((fghz - 1.0) / (5.8 - 1.0), 0.0), 1.0)
    return FR4_ER_1GHZ + t * (FR4_ER_58GHZ - FR4_ER_1GHZ)

def fr4_tan_delta(f_hz: float) -> float:
    """tan δ(f) del FR-4 (dispersivo): ≈0,015 @1 GHz → ≈0,020 @5,8 GHz → ≈0,025 @10 GHz.
    Las pérdidas dieléctricas del epoxi crecen con la frecuencia (Isola/Shengyi)."""
    fghz = f_hz / 1e9
    return 0.014 + 0.0011 * fghz

# ── Red L de una sección: ancho de banda limitado (límite de Bode-Fano) ───────
IMN_F0_HZ     = 550e6   # frecuencia de diseño de la red L (caso TDT)
IMN_ETA0      = 0.9484  # η_imn en la frecuencia de diseño
IMN_Q_LOADED  = 3.6     # Q cargado ≈ √(R_diodo/Z0 − 1); BW fraccional ≈ 1/Q ≈ 28 %

def eta_imn_freq(f_hz: float, f0_hz: float = IMN_F0_HZ) -> float:
    """
    Eficiencia de la red L de UNA sección en función de la frecuencia.

    Una red L simple es un circuito resonante de banda estrecha: adapta bien solo
    cerca de f0 y su eficiencia decae hacia los extremos según la respuesta
    resonante (límite de Bode-Fano; Pozar cap. 5):
        η_imn(f) = η0 / (1 + [Q·(f/f0 − f0/f)]²)
    Con Q≈3,6 da η_imn ≈ 0,42 @470 MHz, 0,9484 @550 MHz y ≈0,07 @900 MHz.
    En la frecuencia de diseño devuelve exactamente η0 (caso canónico intacto).
    """
    x = f_hz / f0_hz - f0_hz / f_hz
    return IMN_ETA0 / (1.0 + (IMN_Q_LOADED * x) ** 2)

# ── Parámetros SPICE del diodo Skyworks SMS7630 (AN-4003) ────────────────────
SMS7630 = {
    'Is':  5e-6,       # corriente de saturación [A]
    'n':   1.05,       # factor de idealidad
    'Rs':  20.0,       # resistencia serie [Ω]
    'Cj0': 0.14e-12,   # capacitancia de juntura @ 0 V [F]
    'Vj':  0.34,       # potencial de juntura [V]
    'M':   0.4,        # coeficiente de gradación
}

# ── Sistema de referencia ─────────────────────────────────────────────────────
Z0       = 50.0        # impedancia de referencia [Ω]
Q_L_SMD  = 40.0        # factor Q de inductores SMD 0402/0603
Q_C_SMD  = 80.0        # factor Q de capacitores SMD MLCC 0402/0603
R_LOAD   = 1300.0      # resistencia de carga equivalente [Ω] (BQ25504 input)

# ── PMIC Texas Instruments BQ25504 (SLUSCY3) ─────────────────────────────────
BQ25504_ETA_PMIC    = 0.85    # eficiencia del boost converter DC-DC
BQ25504_V_COLDSTART = 0.130  # voltaje mínimo de arranque en frío [V]

# ── Bandas objetivo — Escenario A (Wang et al. 2022, IEEE TAP) ────────────────
BANDS_A = {
    'GSM1800':  1.84e9,   # [Hz]
    'LTE':      2.04e9,
    'WiFi_2.4': 2.45e9,
    '5G_2.6':   2.54e9,
    '5G_3.5':   3.30e9,
    '5G_4.9':   4.76e9,
    'WiFi_5.8': 5.80e9,
}

# ── Escenario B — FLPDA Koch (Carrel 1961) ────────────────────────────────────
FLPDA_TAU       = 0.90
FLPDA_SIGMA     = 0.15
FLPDA_F_LOW_HZ  = 470e6    # [Hz]
FLPDA_F_HIGH_HZ = 900e6    # [Hz]
FLPDA_KOCH_ITER = 2

# ── Fuentes RF UHF 470–900 MHz ────────────────────────────────────────────────
RF_UHF = {
    'TV UHF (DVB-T)':        {'eirp_dbm': 72.15, 'freq_ghz': 0.550, 'color': '#6d28d9'},  # 10 kW ERP + 2.15 dB = EIRP
    'LTE Macro 700 MHz':     {'eirp_dbm': 46.0, 'freq_ghz': 0.700, 'color': '#b45309'},
    'LTE Band 28 (700 MHz)': {'eirp_dbm': 43.0, 'freq_ghz': 0.700, 'color': '#ea580c'},
    'LoRa Gateway (Colombia)':   {'eirp_dbm': 27.0, 'freq_ghz': 0.915, 'color': '#0369a1'},
}

# ── Corrección de propagación urbana (ITU-R P.1546) ──────────────────────────
URBAN_CORRECTION_DB = 6.0

# ── Pérdidas explícitas del enlace (revisión de modelo 2026-07) ──────────────
# Antes embebidas en la corrección urbana; ahora se restan por separado.
POL_LOSS_DB  = 0.5   # desajuste de polarización (Koch it.2, cross-pol ≈ −15 dB)
HARM_LOSS_DB = 0.4   # reflexión de armónicos del doblador sin filtro paso-bajo

# ── Resultados canónicos @ 100 m, TDT DVB-T 550 MHz ─────────────────────────
# ÚNICA fuente de verdad (SSOT) de los valores canónicos del proyecto: el documento,
# las figuras/tablas del pipeline y las pruebas de regresión leen de aquí.
# REVISIÓN DE MODELO 2026-07 (comité): η_rad realista en FR-4 (0.5972, antes 0.9952);
# EIRP = 72.15 dBm (10 kW ERP + 2.15 dB, antes 70.0); pérdidas explícitas de
# polarización (0.5 dB) y armónicos (0.4 dB); Carrel con región activa → N=12 dipolos.
# eta_total = eta_rad * eta_mm * eta_imn * PCE * eta_pmic = 0.4023 (figura de mérito)
# La potencia DC se calcula con cuatro factores sobre P_in (η_rad ya embebida en G):
# P_DC = P_in · η_mm · η_imn · PCE · η_pmic = 1.982 mW · 0.983 · 0.9484 · 0.85 · 0.85 = 1335.0 µW
CANONICAL = {
    'P_dc_uW':    1335.0,   # potencia DC útil [µW]
    'V_dc_mV':    1317.4,   # voltaje DC de salida [mV]
    'T_ciclo_s':  194.2,    # tiempo de ciclo LoRa SF12 [s]
    'E_ciclo_mJ': 259.25,   # energía por ciclo LoRa SF12 [mJ]
    'P_in_dBm':   2.97,     # potencia disponible en antena @ 100m, 550 MHz, EIRP 72.15 dBm
    'P_in_mW':    1.982,    # idem en mW
    'FSPL_dB':    67.25,    # pérdida de espacio libre @ 100m, 550 MHz
    'L_urb_dB':   6.0,      # corrección urbana ITU-R P.1546
    'gain_dBi':   4.97,     # ganancia realizada FLPDA Koch @ 550 MHz [dBi] (η_rad realista)
    'S11_dB':     -17.71,   # coef. reflexión @ 550 MHz (N=12)
    'eta_rad':    0.5972,   # eficiencia de radiación realista FR-4 @ 550 MHz
    'eta_mm':     0.983,    # eficiencia de adaptación (S11 = -17.71 dB)
    'eta_imn':    0.9484,   # eficiencia red L (IL = 0.23 dB nominal, punto de diseño)
    'PCE':        0.85,     # PCE máxima Shockley doubler (cap del modelo)
    'eta_pmic':   0.85,     # eficiencia boost converter BQ25504
    'eta_total':  0.4023,   # FOM de cinco factores (η_rad realista)
    'RMSE_wang':  15.50,    # RMSE validación Wang 2022 [pp] (rectificador, sin cambio)
    'V_cs_mV':    130.0,    # umbral cold-start BQ25504 [mV]
    'R_load_ohm': 1300.0,   # resistencia de carga (BQ25504 input)
}

# ── Referencia Wang et al. (2022) IEEE TAP ───────────────────────────────────
WANG2022_FREQS_GHZ  = [1.84, 2.04, 2.36, 2.54, 3.30, 4.76, 5.80]
WANG2022_PCE_PCT    = [44.4, 43.9, 45.4, 43.4, 36.1, 32.4, 28.3]
WANG2022_S11_DB     = [-14,  -13,  -16,  -12,  -11,  -10,   -9]
WANG2022_GAIN_DBI   = [ 2.1,  2.2,  2.3,  2.2,  2.0,  1.9,  1.8]

# ── Parámetros rcParams — Estilo APA7 para matplotlib ───────────────────────
APA7_RC = {
    'font.family':        'serif',
    'font.serif':         ['Times New Roman', 'Times', 'DejaVu Serif'],
    'font.size':          11,
    'axes.labelsize':     11,
    'axes.titlesize':     12,
    'legend.fontsize':    10,
    'legend.framealpha':  0.85,
    'xtick.labelsize':    10,
    'ytick.labelsize':    10,
    'figure.dpi':         150,
    'savefig.dpi':        300,
    'axes.grid':          True,
    'grid.alpha':         0.25,
    'grid.linestyle':     '--',
    'grid.linewidth':     0.5,
    'lines.linewidth':    1.8,
    'axes.axisbelow':     True,
    'axes.spines.top':    False,
    'axes.spines.right':  False,
    'figure.facecolor':   'white',
    'axes.facecolor':     'white',
    'savefig.facecolor':  'white',
    'savefig.bbox':       'tight',
    'axes.labelpad':      6.0,
    'xtick.direction':    'in',
    'ytick.direction':    'in',
    'xtick.minor.visible': True,
    'ytick.minor.visible': True,
    'figure.constrained_layout.use': True,
}

# Paleta de colores accesible (perceptualmente uniforme, distinguible en B&W)
COLORS = {
    'azul':     '#0077BB',
    'naranja':  '#EE7733',
    'verde':    '#009988',
    'rojo':     '#CC3311',
    'violeta':  '#AA3377',
    'gris':     '#BBBBBB',
    'negro':    '#000000',
    'amarillo': '#DDAA33',
}

LINESTYLES = ['-', '--', '-.', ':', (0,(5,1)), (0,(3,1,1,1))]
MARKERS    = ['o', 's', '^', 'D', 'v', 'P']
