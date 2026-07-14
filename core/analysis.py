"""
================================================================================
MODULO: Analisis avanzado -- Sensibilidad, Monte Carlo, BW, Link Budget
================================================================================
Herramientas complementarias para validacion y cuantificacion de incertidumbre
del sistema de cosecha de energia RF (RFEH) fractal multibanda.

Contenido:
    sensitivity_tornado()   -- Analisis de sensibilidad parametrica (tornado)
    monte_carlo_pdc()       -- Propagacion de incertidumbre (Monte Carlo)
    rectifier_bandwidth()   -- Ancho de banda del rectificador a -3 dB de PCE
    link_budget_table()     -- Tabla formal de presupuesto de enlace
    supercap_sizing()       -- Dimensionamiento del supercondensador
    state_of_art_table()    -- Tabla comparativa con estado del arte

Autor: Brahian Calderon Munera . UdeA . 2026
================================================================================
"""

import numpy as np
from dataclasses import dataclass
from typing import Callable


# ── Analisis de sensibilidad parametrica ────────────────────────────────────

def sensitivity_tornado(base_params: dict,
                        variations: dict,
                        compute_fn: Callable,
                        output_label: str = 'P_dc_uW') -> dict:
    """
    Analisis de sensibilidad tipo tornado.

    Varia cada parametro +-delta mientras los demas se mantienen fijos.
    Retorna el impacto de cada parametro en la metrica de salida.

    Parametros
    ----------
    base_params : dict con parametros base {nombre: valor}
    variations  : dict {nombre: delta_relativo} (e.g. {'eirp_dbm': 3.0} = +-3 dB)
    compute_fn  : funcion(params_dict) -> float que calcula la metrica
    output_label: nombre de la metrica de salida

    Retorna
    -------
    dict con 'baseline', 'results' (lista de dicts con param, low, high, delta)
    """
    baseline = compute_fn(dict(base_params))
    results = []

    for param, delta in variations.items():
        if param not in base_params:
            continue

        # Variacion negativa
        p_low = dict(base_params)
        p_low[param] = base_params[param] - delta
        val_low = compute_fn(p_low)

        # Variacion positiva
        p_high = dict(base_params)
        p_high[param] = base_params[param] + delta
        val_high = compute_fn(p_high)

        results.append({
            'param': param,
            'base': base_params[param],
            'delta': delta,
            'val_low': val_low,
            'val_high': val_high,
            'impact': abs(val_high - val_low),
            'pct_change': abs(val_high - val_low) / max(abs(baseline), 1e-15) * 100,
        })

    # Ordenar por impacto descendente
    results.sort(key=lambda x: x['impact'], reverse=True)

    return {
        'baseline': baseline,
        'output_label': output_label,
        'results': results,
    }


# ── Monte Carlo -- Propagacion de incertidumbre ────────────────────────────

def monte_carlo_pdc(base_params: dict,
                    uncertainties: dict,
                    compute_fn: Callable,
                    n_samples: int = 10000,
                    seed: int = 42) -> dict:
    """
    Propagacion de incertidumbre por Monte Carlo.

    Genera n_samples realizaciones del sistema variando cada parametro
    segun su distribucion de incertidumbre (normal o uniforme).

    Parametros
    ----------
    base_params   : dict {nombre: valor_nominal}
    uncertainties : dict {nombre: {'type': 'normal'|'uniform', 'std'|'half_range': val}}
    compute_fn    : funcion(params_dict) -> float
    n_samples     : numero de muestras Monte Carlo
    seed          : semilla para reproducibilidad

    Retorna
    -------
    dict con 'samples', 'mean', 'std', 'p5', 'p25', 'median', 'p75', 'p95',
             'ci_95' (intervalo de confianza 95%)
    """
    rng = np.random.default_rng(seed)
    samples = np.zeros(n_samples)

    # Generar realizaciones de parametros
    param_samples = {}
    for name, val in base_params.items():
        if name in uncertainties:
            u = uncertainties[name]
            if u['type'] == 'normal':
                param_samples[name] = rng.normal(val, u['std'], n_samples)
            elif u['type'] == 'uniform':
                param_samples[name] = rng.uniform(val - u['half_range'],
                                                   val + u['half_range'],
                                                   n_samples)
            else:
                param_samples[name] = np.full(n_samples, val)
        else:
            param_samples[name] = np.full(n_samples, val)

    # Evaluar cada muestra
    for i in range(n_samples):
        p = {name: float(param_samples[name][i]) for name in base_params}
        try:
            samples[i] = compute_fn(p)
        except Exception:
            samples[i] = 0.0

    # Estadisticas
    valid = samples[samples > 0]
    if len(valid) == 0:
        valid = samples

    return {
        'samples': samples,
        'n_valid': int(np.sum(samples > 0)),
        'n_total': n_samples,
        'mean': float(np.mean(valid)),
        'std': float(np.std(valid)),
        'p5': float(np.percentile(valid, 5)),
        'p25': float(np.percentile(valid, 25)),
        'median': float(np.median(valid)),
        'p75': float(np.percentile(valid, 75)),
        'p95': float(np.percentile(valid, 95)),
        'ci_95': (float(np.percentile(valid, 2.5)), float(np.percentile(valid, 97.5))),
        'cv_pct': float(np.std(valid) / max(np.mean(valid), 1e-15) * 100),
    }


# ── Ancho de banda del rectificador ─────────────────────────────────────────

def rectifier_bandwidth(rectifier, Pin_dBm: float = -10.0,
                        freq_center: float = 550e6,
                        freq_span: float = 500e6,
                        n_points: int = 200) -> dict:
    """
    Calcula el ancho de banda a -3 dB de PCE del rectificador.

    Barre la frecuencia alrededor de freq_center y encuentra donde
    la PCE cae 3 dB (50%) respecto al maximo.

    Retorna
    -------
    dict con 'freqs_hz', 'pce', 'pce_max', 'freq_max_hz', 'bw_3dB_hz',
             'f_low_3dB', 'f_high_3dB', 'fractional_bw'
    """
    freqs = np.linspace(max(freq_center - freq_span/2, 10e6),
                        freq_center + freq_span/2, n_points)
    pce = np.array([rectifier.PCE(Pin_dBm, f) for f in freqs])

    pce_max = np.max(pce)
    idx_max = np.argmax(pce)
    freq_max = freqs[idx_max]
    threshold = pce_max / 2.0   # -3 dB en potencia = 50% en eficiencia

    # Buscar cruce a la izquierda
    f_low = freqs[0]
    for j in range(idx_max, -1, -1):
        if pce[j] < threshold:
            # Interpolar
            if j + 1 < len(freqs):
                frac = (threshold - pce[j]) / max(pce[j+1] - pce[j], 1e-15)
                f_low = freqs[j] + frac * (freqs[j+1] - freqs[j])
            break

    # Buscar cruce a la derecha
    f_high = freqs[-1]
    for j in range(idx_max, len(freqs)):
        if pce[j] < threshold:
            if j - 1 >= 0:
                frac = (threshold - pce[j]) / max(pce[j-1] - pce[j], 1e-15)
                f_high = freqs[j] - frac * (freqs[j] - freqs[j-1])
            break

    bw = f_high - f_low
    fbw = bw / freq_max if freq_max > 0 else 0.0

    return {
        'freqs_hz': freqs,
        'pce': pce,
        'pce_max': float(pce_max),
        'freq_max_hz': float(freq_max),
        'bw_3dB_hz': float(bw),
        'f_low_3dB': float(f_low),
        'f_high_3dB': float(f_high),
        'fractional_bw': float(fbw),
    }


# ── Link Budget formal ─────────────────────────────────────────────────────

def link_budget_table(eirp_dbm: float, dist_m: float, freq_ghz: float,
                      gain_dBi: float, eta_mm: float, eta_imn: float,
                      IL_dB: float, pce: float, eta_pmic: float,
                      urban_correction_dB: float = 6.0) -> list:
    """
    Genera tabla formal de presupuesto de enlace como lista de filas.

    Cada fila: (parametro, valor, unidad, acumulado_dBm)

    Retorna
    -------
    list of dict con 'parameter', 'value', 'unit', 'cumulative_dBm'
    """
    c0 = 3e8
    lam = c0 / (freq_ghz * 1e9)
    fspl = 20 * np.log10(4 * np.pi * dist_m / lam)

    rows = []
    cumul = eirp_dbm

    rows.append({'parameter': 'EIRP transmisor', 'value': f'{eirp_dbm:.1f}',
                 'unit': 'dBm', 'cumulative_dBm': f'{cumul:.1f}'})

    cumul -= fspl
    rows.append({'parameter': f'FSPL ({dist_m:.0f} m, {freq_ghz*1e3:.0f} MHz)',
                 'value': f'-{fspl:.1f}', 'unit': 'dB',
                 'cumulative_dBm': f'{cumul:.1f}'})

    cumul -= urban_correction_dB
    rows.append({'parameter': 'Correccion urbana ITU-R P.1546',
                 'value': f'-{urban_correction_dB:.1f}', 'unit': 'dB',
                 'cumulative_dBm': f'{cumul:.1f}'})

    cumul += gain_dBi
    rows.append({'parameter': 'Ganancia antena Rx (realizada)',
                 'value': f'+{gain_dBi:.2f}', 'unit': 'dBi',
                 'cumulative_dBm': f'{cumul:.1f}'})

    # eta_mm en dB
    mm_dB = -10 * np.log10(max(eta_mm, 1e-10))
    cumul -= mm_dB
    rows.append({'parameter': 'Perdida mismatch (eta_mm)',
                 'value': f'-{mm_dB:.2f}', 'unit': 'dB',
                 'cumulative_dBm': f'{cumul:.1f}'})

    cumul -= IL_dB
    rows.append({'parameter': 'Perdida IMN (eta_imn, IL)',
                 'value': f'-{IL_dB:.2f}', 'unit': 'dB',
                 'cumulative_dBm': f'{cumul:.1f}'})

    P_rect_dBm = cumul
    P_rect_uW = 10.0 ** (P_rect_dBm / 10.0) * 1e3   # uW

    rows.append({'parameter': 'P_RF en rectificador',
                 'value': f'{P_rect_dBm:.1f} dBm = {P_rect_uW:.1f}',
                 'unit': 'uW', 'cumulative_dBm': f'{P_rect_dBm:.1f}'})

    pce_dB = 10 * np.log10(max(pce, 1e-10))
    cumul += pce_dB
    rows.append({'parameter': f'PCE rectificador ({pce*100:.1f}%)',
                 'value': f'{pce_dB:.2f}', 'unit': 'dB',
                 'cumulative_dBm': f'{cumul:.1f}'})

    pmic_dB = 10 * np.log10(max(eta_pmic, 1e-10))
    cumul += pmic_dB
    rows.append({'parameter': f'eta_PMIC BQ25504 ({eta_pmic*100:.0f}%)',
                 'value': f'{pmic_dB:.2f}', 'unit': 'dB',
                 'cumulative_dBm': f'{cumul:.1f}'})

    P_dc_uW = 10.0 ** (cumul / 10.0) * 1e3
    rows.append({'parameter': 'P_DC util final',
                 'value': f'{cumul:.1f} dBm = {P_dc_uW:.1f}',
                 'unit': 'uW', 'cumulative_dBm': f'{cumul:.1f}'})

    return rows


# ── Dimensionamiento del supercondensador ──────────────────────────────────

@dataclass
class SupercapResult:
    """Resultado del dimensionamiento del supercondensador."""
    C_F: float              # capacitancia [F]
    V_max: float            # voltaje maximo [V]
    V_min: float            # voltaje minimo operativo [V]
    E_stored_J: float       # energia almacenada total [J]
    E_useful_J: float       # energia util (entre V_max y V_min) [J]
    E_ciclo_J: float        # energia por ciclo de transmision [J]
    n_ciclos: float         # numero de ciclos por carga completa
    t_charge_s: float       # tiempo de carga desde V_min hasta V_max [s]
    P_dc_uW: float          # potencia DC de entrada [uW]
    ESR_ohm: float          # resistencia serie equivalente [Ohm]
    P_leak_uW: float        # potencia de auto-descarga [uW]
    eta_storage: float      # eficiencia de almacenamiento [0..1]

    def summary(self) -> str:
        lines = [
            f'Supercondensador: C = {self.C_F*1e3:.0f} mF ({self.C_F:.3f} F)',
            f'  V_max = {self.V_max:.2f} V, V_min = {self.V_min:.2f} V',
            f'  E_total = {self.E_stored_J*1e3:.1f} mJ, E_util = {self.E_useful_J*1e3:.1f} mJ',
            f'  E_ciclo = {self.E_ciclo_J*1e3:.2f} mJ',
            f'  Ciclos por carga: {self.n_ciclos:.1f}',
            f'  Tiempo carga V_min->V_max: {self.t_charge_s:.0f} s ({self.t_charge_s/60:.1f} min)',
            f'  ESR = {self.ESR_ohm:.1f} Ohm, P_leak = {self.P_leak_uW:.2f} uW',
            f'  eta_storage = {self.eta_storage*100:.1f}%',
        ]
        return '\n'.join(lines)


def supercap_sizing(P_dc_uW: float, E_ciclo_J: float,
                    C_F: float = 0.33, V_max: float = 3.3,
                    V_min: float = 1.8, ESR_ohm: float = 0.0,
                    I_leak_uA: float = 0.0) -> SupercapResult:
    """
    Dimensionamiento completo del supercondensador.

    Por defecto (ESR_ohm=0, I_leak_uA=0) reproduce exactamente la caracterización
    temporal del Anexo B.9 del documento: t_carga = E_util / P_DC, sin pérdidas
    adicionales. ESR_ohm/I_leak_uA > 0 son un refinamiento opcional (pérdidas
    óhmicas de carga y autodescarga) para exploración fuera del caso canónico,
    no parte del modelo documentado.

    Parametros
    ----------
    P_dc_uW   : potencia DC disponible del cosechador [uW]
    E_ciclo_J  : energia necesaria por ciclo de transmision [J]
    C_F        : capacitancia del supercondensador [F]
    V_max      : voltaje maximo de carga [V]
    V_min      : voltaje minimo operativo [V]
    ESR_ohm    : resistencia serie equivalente [Ohm]
    I_leak_uA  : corriente de fuga del supercondensador [uA]

    Retorna
    -------
    SupercapResult con todos los parametros calculados
    """
    P_dc_W = P_dc_uW * 1e-6
    I_leak_A = I_leak_uA * 1e-6

    # Energia almacenada
    E_total = 0.5 * C_F * V_max ** 2
    E_min = 0.5 * C_F * V_min ** 2
    E_useful = E_total - E_min

    # Ciclos por carga
    n_ciclos = E_useful / E_ciclo_J if E_ciclo_J > 0 else float('inf')

    # Potencia de auto-descarga
    P_leak_W = I_leak_A * (V_max + V_min) / 2.0
    P_leak_uW = P_leak_W * 1e6

    # Potencia neta (descontando auto-descarga y perdidas ESR)
    I_charge = P_dc_W / max(V_min, 0.01)   # corriente de carga a V_min
    P_ESR = I_charge ** 2 * ESR_ohm
    P_net = max(P_dc_W - P_leak_W - P_ESR, 1e-15)

    # Tiempo de carga
    E_charge = E_useful
    t_charge = E_charge / P_net

    # Eficiencia de almacenamiento
    eta_storage = P_net / max(P_dc_W, 1e-15)

    return SupercapResult(
        C_F=C_F, V_max=V_max, V_min=V_min,
        E_stored_J=E_total, E_useful_J=E_useful,
        E_ciclo_J=E_ciclo_J, n_ciclos=n_ciclos,
        t_charge_s=t_charge, P_dc_uW=P_dc_uW,
        ESR_ohm=ESR_ohm, P_leak_uW=P_leak_uW,
        eta_storage=eta_storage,
    )


# ── Tabla comparativa estado del arte ───────────────────────────────────────

STATE_OF_ART = [
    {
        'reference': 'Wang et al. (2022)',
        'journal': 'IEEE TAP',
        'antenna': 'Fractal multi-banda',
        'substrate': 'Duroid 5880',
        'freq_range': '1.84-5.80 GHz',
        'bands': 7,
        'gain_dBi': '1.8-2.3',
        'PCE_max': '45.4%',
        'Pin_dBm': -10,
        'P_dc_uW': 'N/R',
        'rectifier': 'Halfwave',
        'notes': 'Referencia de validacion',
    },
    {
        'reference': 'Sun et al. (2013)',
        'journal': 'IEEE MWCL',
        'antenna': 'Rectenna dual-banda',
        'substrate': 'FR-4',
        'freq_range': '1.8 / 2.45 GHz',
        'bands': 2,
        'gain_dBi': '2.0-3.5',
        'PCE_max': '67%',
        'Pin_dBm': 0,
        'P_dc_uW': 'N/R',
        'rectifier': 'Doubler',
        'notes': 'Dual-band, alta PCE a 0 dBm',
    },
    {
        'reference': 'Hagerty et al. (2004)',
        'journal': 'IEEE TMTT',
        'antenna': 'Array Vivaldi',
        'substrate': 'Duroid 5880',
        'freq_range': '2-18 GHz',
        'bands': 'UWB',
        'gain_dBi': '5-10',
        'PCE_max': '20%',
        'Pin_dBm': -20,
        'P_dc_uW': '~1',
        'rectifier': 'Dickson',
        'notes': 'Broadband, baja PCE por ancho de banda',
    },
    {
        'reference': 'Olgun et al. (2011)',
        'journal': 'IEEE AW&PL',
        'antenna': 'Dipolo plegado',
        'substrate': 'FR-4',
        'freq_range': '2.45 GHz',
        'bands': 1,
        'gain_dBi': '2.2',
        'PCE_max': '40%',
        'Pin_dBm': -10,
        'P_dc_uW': '~10',
        'rectifier': 'Halfwave',
        'notes': 'Bajo costo, single-band',
    },
    {
        'reference': 'Pinuela et al. (2013)',
        'journal': 'IEEE TMTT',
        'antenna': 'Monopolo / LPDA',
        'substrate': 'FR-4',
        'freq_range': '0.3-3 GHz',
        'bands': 'UWB',
        'gain_dBi': '1.5-7.5',
        'PCE_max': '40%',
        'Pin_dBm': -25,
        'P_dc_uW': '~7',
        'rectifier': 'Schottky SMS7630',
        'notes': 'Mediciones en ambiente real (Londres)',
    },
    {
        'reference': 'Shen et al. (2019)',
        'journal': 'IEEE Access',
        'antenna': 'Koch fractal dipolo',
        'substrate': 'FR-4',
        'freq_range': '0.9 / 1.8 / 2.45 GHz',
        'bands': 3,
        'gain_dBi': '2.5-4.0',
        'PCE_max': '52%',
        'Pin_dBm': -5,
        'P_dc_uW': '~100',
        'rectifier': 'Doubler',
        'notes': 'Fractal Koch, triple banda',
    },
    {
        'reference': 'Este trabajo (Esc. B)',
        'journal': 'Tesis UdeA',
        'antenna': 'FLPDA Koch it.2',
        'substrate': 'FR-4',
        'freq_range': '470-900 MHz',
        'bands': 'Continua UHF',
        'gain_dBi': '7.1-7.5',
        'PCE_max': None,      # Se llena con valor calculado
        'Pin_dBm': None,
        'P_dc_uW': None,
        'rectifier': 'Doubler SMS7630',
        'notes': 'Modelo analitico, sin medicion experimental',
    },
]


def get_state_of_art_table(pce_max: float = None,
                           pin_dbm: float = None,
                           pdc_uw: float = None) -> list:
    """
    Retorna la tabla de estado del arte con los valores de este trabajo.

    Parametros
    ----------
    pce_max : PCE maxima calculada del sistema [%]
    pin_dbm : potencia de entrada de referencia [dBm]
    pdc_uw  : potencia DC de salida [uW]
    """
    table = []
    for entry in STATE_OF_ART:
        row = dict(entry)
        if row['reference'] == 'Este trabajo (Esc. B)':
            if pce_max is not None:
                row['PCE_max'] = f'{pce_max:.1f}%'
            if pin_dbm is not None:
                row['Pin_dBm'] = pin_dbm
            if pdc_uw is not None:
                row['P_dc_uW'] = f'{pdc_uw:.1f}'
        table.append(row)
    return table
