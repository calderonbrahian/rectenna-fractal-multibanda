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

# ── Sustrato FR-4 (Bahl & Trivedi 1977; Pozar cap. 3) ────────────────────────
FR4_ER_1GHZ  = 4.4    # εr @ 1 GHz
FR4_ER_58GHZ = 4.1    # εr @ 5.8 GHz
FR4_LOSS_TAN = 0.02   # tangente de pérdidas (tan δ)
FR4_H_M      = 1.6e-3 # espesor del sustrato [m]

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
    'TV UHF (DVB-T)':        {'eirp_dbm': 70.0, 'freq_ghz': 0.550, 'color': '#6d28d9'},
    'LTE Macro 700 MHz':     {'eirp_dbm': 46.0, 'freq_ghz': 0.700, 'color': '#b45309'},
    'LTE Band 28 (700 MHz)': {'eirp_dbm': 43.0, 'freq_ghz': 0.700, 'color': '#ea580c'},
    'LoRa Gateway (Colombia)':   {'eirp_dbm': 27.0, 'freq_ghz': 0.915, 'color': '#0369a1'},
}

# ── Corrección de propagación urbana (ITU-R P.1546) ──────────────────────────
URBAN_CORRECTION_DB = 6.0

# ── Resultados canónicos @ 100 m, TDT DVB-T 550 MHz ─────────────────────────
# Sincronizado con rectenna_platform/config/variables.yaml (auditoría 2026-05-28)
# eta_total = eta_rad * eta_mm * eta_imn * PCE * eta_pmic = 0.6715 (figura de mérito)
# La potencia DC se calcula con cuatro factores sobre P_in: η_rad ya está embebida en G
# P_DC = P_in · η_mm · η_imn · PCE · η_pmic  =  2.427 mW · 0.9847 · 0.9484 · 0.85 · 0.85 = 1637.6 µW
CANONICAL = {
    'P_dc_uW':    1637.6,   # potencia DC útil [µW]
    'V_dc_mV':    1459.1,   # voltaje DC de salida [mV]
    'T_ciclo_s':  158.3,    # tiempo de ciclo LoRa SF12 [s]
    'E_ciclo_mJ': 259.25,   # energía por ciclo LoRa SF12 [mJ]
    'P_in_dBm':   3.85,     # potencia disponible en antena @ 100m, 550 MHz, EIRP 70 dBm
    'P_in_mW':    2.427,    # idem en mW
    'FSPL_dB':    67.25,    # pérdida de espacio libre @ 100m, 550 MHz
    'L_urb_dB':   6.0,      # corrección urbana ITU-R P.1546
    'gain_dBi':   7.10,     # ganancia realizada FLPDA Koch @ 550 MHz [dBi]
    'S11_dB':     -18.16,   # coef. reflexión @ 550 MHz
    'eta_rad':    0.9952,   # eficiencia de radiación (corregido auditoría)
    'eta_mm':     0.9847,   # eficiencia de adaptación (S11 = -18.16 dB)
    'eta_imn':    0.9484,   # eficiencia red L (IL = 0.23 dB nominal)
    'PCE':        0.85,     # PCE máxima Shockley doubler (cap del modelo)
    'eta_pmic':   0.85,     # eficiencia boost converter BQ25504
    'eta_total':  0.6715,   # FOM de cinco factores (corregido auditoría)
    'RMSE_wang':  15.50,    # RMSE validación Wang 2022 [pp]
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
