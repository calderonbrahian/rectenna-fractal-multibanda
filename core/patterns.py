# -*- coding: utf-8 -*-
"""
================================================================================
MÓDULO: Patrones de radiación — capa de caracterización de antenas (Etapa G0)
================================================================================
API uniforme para los cortes principales (plano E, plano H) de las tres
topologías del proyecto (parche, Sierpinski, FLPDA Koch), en potencia
normalizada [dB] (máximo = 0 dB). ALCANCE: modelo analítico de estimación,
consistente con el resto de la capa `core/` (sin solucionador full-wave),
con la misma tolerancia declarada de ±1,5 dBi frente a EM (CST/HFSS) que
`core/patch.py` (Balanis, Antenna Theory 4ª ed., cap. 14).

── Parche (modelo de cavidad de dos ranuras, Balanis 14-44/14-46) ────────────
Corte E (φ=0°, plano x-z):  F_E(θ) ∝ cos(k·L_eff/2·sinθ) · sinc(k·h/2·sinθ)
    El factor de ranura sinc(k·h/2·sinθ) ≈ 1 porque h ≪ λ (sustratos finos
    de PCB); se omite explícitamente.
Corte H (φ=90°, plano y-z): F_H(θ) ∝ sinc(k·W_eff/2·sinθ) · cosθ

DECISIÓN DE MODELADO — número de onda usado en el factor de arreglo:
    Se usa k = k0·√ε_eff (número de onda "guiado", no k0 puro). Justificación
    física: L_eff se diseña como ≈ λ_g/2 (media longitud de onda GUIADA), de
    modo que el argumento k·L_eff/2 en el plano E es ≈ π/2·sinθ con
    independencia del sustrato — root físico de que L_eff·k_eff ≈ π por
    diseño resonante. Usar k0 puro (número de onda de espacio libre) sobre la
    dimensión FÍSICA (más corta que λ0/2 por el dieléctrico) da patrones
    E-plano irreal/anormalmente anchos (HPBW → 180°, saturando el hemisferio
    frontal) porque subestima el argumento eléctrico. La convención k_eff es
    una aproximación de ingeniería estándar para el modelo de cavidad de dos
    ranuras (equivale a tratar el argumento de arreglo con la "longitud
    eléctrica" de diseño) y reproduce HPBW realistas (~55–70° E-plano) sin
    necesitar un término de difracción de plano de tierra finito.

Radiación solo en el semiespacio superior (plano de tierra ideal, infinito):
el semiespacio trasero (|θ| > 90°) se recorta a un piso de −20 dB, valor
típico de F/B de un parche sobre plano de tierra FINITO real (la difracción
de borde limita, pero no anula, la radiación trasera). Aproximación explícita.

── Sierpinski (aproximación honesta, sin solver full-wave) ───────────────────
Puente-Baliarda et al. reportan que cada banda activa del Sierpinski se
comporta como un radiador tipo parche/monopolo con patrón ESTABLE por banda
(no exactamente igual entre bandas, pero de forma similar). Aquí se reutiliza
el MISMO modelo de cavidad de dos ranuras (arriba) evaluado con la dimensión
activa de la banda k (base_dim/2^k) y la permitividad dispersiva del FR-4 a
esa frecuencia, escalada por un factor de ensanchamiento 0.7 —constante,
documentada— que representa la menor apertura efectiva de un radiador
triangular fractal frente a un parche rectangular equivalente de la misma
dimensión (el triángulo de Sierpinski concentra menos superficie radiante
por unidad de dimensión lineal). Resultado: HPBW sistemáticamente MÁS ANCHO
que el parche equivalente, consistente con la descripción cualitativa de la
literatura (patrones anchos tipo monopolo/parche, Puente-Baliarda 1998-2000).

── FLPDA Koch (endfire, Carrel 1961) ──────────────────────────────────────────
Patrón axialmente simétrico de haz único F(θ) = cos^q(θ/2), con el exponente
q elegido para que la directividad integrada de este patrón coincida con
`FLPDA_Koch.directivity_dBi(f)` del modelo existente:
    Para U(θ) = |F(θ)|² = cos^(2q)(θ/2) (patrón axisimétrico, potencia):
        D0 = ∫∫ 4π U dΩ / ∫∫ U dΩ = (2q + 2) / 2 = q + 1     (derivación cerrada)
    ⇒ q = 10^(D_dBi/10) − 1
No hace falta una búsqueda numérica iterativa: la directividad de este patrón
tiene forma cerrada, así que q se obtiene analíticamente (equivalente a
"calcularlo numéricamente" a partir del valor de directividad del modelo).
El mismo F(θ) se usa para ambos cortes E y H (aproximación de haz único
axisimétrico, razonable para una LPDA endfire). El lóbulo trasero natural de
cos^q(θ/2) diverge a −∞ dB en θ=180°; se aplica un piso de −25 dB (F/B típico
reportado para LPDA reales con reflector/boom finito, Carrel 1961).

Todas las funciones devuelven también `freq_hz` y `kind` para trazabilidad.

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np

from configs.parametros import C0

_N_THETA = 721                 # resolución angular (0.5°) del barrido
_BACK_FLOOR_PATCH_DB = -20.0    # piso F/B parche/Sierpinski (plano de tierra finito)
_BACK_FLOOR_FLPDA_DB = -25.0    # piso F/B FLPDA (LPDA real con boom finito)
_SIERPINSKI_BROADEN = 0.7       # factor de ensanchamiento triángulo vs parche equivalente


# ── Núcleo común: modelo de cavidad de dos ranuras (parche y Sierpinski) ──────

def _cavity_cuts(freq_hz: float, L_eff: float, W_eff: float, eps_eff: float,
                  back_floor_db: float = _BACK_FLOOR_PATCH_DB, n: int = _N_THETA):
    """
    Cortes E/H normalizados [dB] del modelo de cavidad de dos ranuras (Balanis).

    k_eff = k0·√ε_eff (ver nota de diseño en el docstring del módulo).
    """
    theta_deg = np.linspace(-180.0, 180.0, n)
    theta = np.radians(theta_deg)

    k0 = 2.0 * np.pi * freq_hz / C0
    k_eff = k0 * np.sqrt(max(eps_eff, 1.0))

    # Corte E: array factor de dos ranuras separadas L_eff (slot factor ≈ 1)
    F_E = np.cos(k_eff * L_eff / 2.0 * np.sin(theta))

    # Corte H: slot factor sinc(k W_eff/2 sinθ) por el elemento cosθ
    xH = k_eff * W_eff / 2.0 * np.sin(theta)
    with np.errstate(divide='ignore', invalid='ignore'):
        sinc_H = np.where(np.abs(xH) < 1e-9, 1.0, np.sin(xH) / xH)
    F_H = sinc_H * np.cos(theta)

    P_E = F_E ** 2
    P_H = F_H ** 2
    E_dB = 10.0 * np.log10(np.maximum(P_E, 1e-12))
    H_dB = 10.0 * np.log10(np.maximum(P_H, 1e-12))

    # Semiespacio trasero: plano de tierra (finito) -> piso de F/B aproximado
    back = np.abs(theta_deg) > 90.0
    E_dB = np.where(back, back_floor_db, E_dB)
    H_dB = np.where(back, back_floor_db, H_dB)

    # Normalización de seguridad (el máximo teórico ya es 0 dB en boresight)
    E_dB = E_dB - np.max(E_dB)
    H_dB = H_dB - np.max(H_dB)
    return theta_deg, E_dB, H_dB


# ── Métricas comunes ──────────────────────────────────────────────────────────

def _hpbw_deg(theta_deg: np.ndarray, vals_dB: np.ndarray, level: float = -3.0) -> float:
    """
    Ancho de haz a media potencia (HPBW) [°] por interpolación lineal del
    cruce con `level` dB a ambos lados del máximo (asumido en θ=0).
    """
    idx0 = int(np.argmin(np.abs(theta_deg)))

    def _cross(indices):
        prev_t, prev_v = theta_deg[idx0], vals_dB[idx0]
        for i in indices:
            t, v = theta_deg[i], vals_dB[i]
            if prev_v >= level and v < level:
                frac = (level - prev_v) / (v - prev_v)
                return prev_t + frac * (t - prev_t)
            prev_t, prev_v = t, v
        return None

    right = _cross(range(idx0, len(theta_deg)))
    left = _cross(range(idx0, -1, -1))
    if right is None:
        right = float(theta_deg[-1])
    if left is None:
        left = float(theta_deg[0])
    return float(right - left)


def _front_to_back_dB(theta_deg: np.ndarray, vals_dB: np.ndarray) -> float:
    """F/B [dB] = valor en θ=0° − máximo entre θ=+180° y θ=−180°."""
    idx0 = int(np.argmin(np.abs(theta_deg)))
    idx_p180 = int(np.argmin(np.abs(theta_deg - 180.0)))
    idx_m180 = int(np.argmin(np.abs(theta_deg + 180.0)))
    back = max(float(vals_dB[idx_p180]), float(vals_dB[idx_m180]))
    return float(vals_dB[idx0] - back)


def _max_direction_deg(theta_deg: np.ndarray, vals_dB: np.ndarray) -> float:
    """Dirección [°] del máximo de radiación."""
    return float(theta_deg[int(np.argmax(vals_dB))])


def _assemble(kind: str, freq_hz: float, theta_deg, E_dB, H_dB) -> dict:
    return {
        'kind':               kind,
        'freq_hz':            float(freq_hz),
        'theta_deg':          theta_deg,
        'E_plane_dB':         E_dB,
        'H_plane_dB':         H_dB,
        'hpbw_e_deg':         _hpbw_deg(theta_deg, E_dB),
        'hpbw_h_deg':         _hpbw_deg(theta_deg, H_dB),
        'front_to_back_dB':   _front_to_back_dB(theta_deg, E_dB),
        'max_direction_deg':  _max_direction_deg(theta_deg, E_dB),
    }


# ── Parche ─────────────────────────────────────────────────────────────────────

def _pattern_patch(freq_hz: float, substrate: str = 'FR4', f0_hz: float = None,
                    L_eff: float = None, W_eff: float = None,
                    eps_eff: float = None) -> dict:
    """
    Cortes del parche microcinta (modelo de cavidad, `core.patch.MicrostripPatchAntenna`).

    Si no se proveen L_eff/W_eff/eps_eff explícitos, se construye la antena a
    `f0_hz` (frecuencia de diseño; por defecto = freq_hz) sobre `substrate` y
    se toman sus dimensiones efectivas — el patrón se evalúa a `freq_hz`
    (normalmente = f0, el punto de operación).
    """
    if L_eff is None or W_eff is None or eps_eff is None:
        from core.patch import MicrostripPatchAntenna
        f0 = f0_hz if f0_hz is not None else freq_hz
        ant = MicrostripPatchAntenna(f0, substrate)
        L_eff, W_eff, eps_eff = ant.L_eff, ant.W_eff, ant.eps_eff

    theta_deg, E_dB, H_dB = _cavity_cuts(freq_hz, L_eff, W_eff, eps_eff,
                                          back_floor_db=_BACK_FLOOR_PATCH_DB)
    return _assemble('patch', freq_hz, theta_deg, E_dB, H_dB)


# ── Sierpinski ─────────────────────────────────────────────────────────────────

def _pattern_sierpinski(freq_hz: float, base_freq: float = 1.84e9,
                         iterations: int = 3, base_dim: float = None) -> dict:
    """
    Cortes de la Sierpinski (aproximación: parche equivalente por banda activa).

    La banda activa k se identifica por f ≈ base_freq·2^k (autosimilitud del
    Sierpinski, `core.antenna.FractalAntenna`); la dimensión radiante activa
    es base_dim/2^k, ensanchada por `_SIERPINSKI_BROADEN` (ver docstring del
    módulo). ε_eff se aproxima por εr(f) del sustrato FR-4 dispersivo.
    """
    from core.antenna import FractalAntenna
    if base_dim is None:
        ant = FractalAntenna('sierpinski', iterations=iterations, base_freq=base_freq)
        base_dim = ant.base_dim
        er_fn = ant.get_er
    else:
        from core.substrates import get_substrate
        er_fn = get_substrate('FR4').er

    ratio = max(freq_hz / base_freq, 1e-9)
    k_band = max(int(round(np.log2(ratio))), 0)
    dim_active = base_dim / (2.0 ** k_band)
    dim_eff = dim_active * _SIERPINSKI_BROADEN
    eps_eff = er_fn(freq_hz)

    theta_deg, E_dB, H_dB = _cavity_cuts(freq_hz, dim_eff, dim_eff, eps_eff,
                                          back_floor_db=_BACK_FLOOR_PATCH_DB)
    return _assemble('sierpinski', freq_hz, theta_deg, E_dB, H_dB)


# ── FLPDA Koch ──────────────────────────────────────────────────────────────────

def _pattern_flpda(freq_hz: float, directivity_dBi: float = None,
                    tau: float = 0.90, sigma: float = 0.15,
                    f_low: float = 470e6, f_high: float = 900e6,
                    koch_iter: int = 2, n: int = _N_THETA) -> dict:
    """
    Cortes de la FLPDA Koch (endfire, haz único axisimétrico F(θ)=cos^q(θ/2)).

    q se obtiene en forma cerrada de la directividad del modelo existente
    (`FLPDA_Koch.directivity_dBi(f)`): D0 = q+1 ⇒ q = 10^(D_dBi/10) − 1.
    Mismo patrón para ambos cortes E y H (aproximación de haz único).
    """
    if directivity_dBi is None:
        from core.flpda import FLPDA_Koch
        ant = FLPDA_Koch(tau=tau, sigma=sigma, f_low=f_low, f_high=f_high,
                          koch_iter=koch_iter)
        directivity_dBi = float(ant.directivity_dBi(freq_hz))
        if directivity_dBi <= 0.0:
            # Fuera de banda activa: directivity_dBi() devuelve 0; usa la
            # directividad en el centro de banda como referencia razonable.
            f_mid = 0.5 * (f_low + f_high)
            directivity_dBi = float(ant.directivity_dBi(f_mid))

    q = max(10.0 ** (directivity_dBi / 10.0) - 1.0, 0.05)

    theta_deg = np.linspace(-180.0, 180.0, n)
    half = np.radians(theta_deg) / 2.0
    cos_half = np.clip(np.abs(np.cos(half)), 1e-12, 1.0)
    P_dB = 20.0 * q * np.log10(cos_half)          # 10*log10(cos^(2q)) = 20q*log10(cos)
    P_dB = np.maximum(P_dB, _BACK_FLOOR_FLPDA_DB)
    P_dB = P_dB - np.max(P_dB)

    return _assemble('flpda', freq_hz, theta_deg, P_dB, P_dB.copy())


# ── API pública ────────────────────────────────────────────────────────────────

_DISPATCH = {
    'patch':       _pattern_patch,
    'sierpinski':  _pattern_sierpinski,
    'flpda':       _pattern_flpda,
    'flpda_koch':  _pattern_flpda,
}


def pattern_cuts(antenna_kind: str, freq_hz: float, **params) -> dict:
    """
    Cortes E/H de potencia normalizada [dB] (máx = 0 dB) para una antena.

    Parámetros
    ----------
    antenna_kind : 'patch' | 'sierpinski' | 'flpda' (o 'flpda_koch')
    freq_hz      : frecuencia de evaluación [Hz]
    **params     : parámetros específicos de la topología (ver
                   `_pattern_patch`, `_pattern_sierpinski`, `_pattern_flpda`).

    Retorna
    -------
    dict con: kind, freq_hz, theta_deg (ndarray, −180..180°), E_plane_dB,
    H_plane_dB, hpbw_e_deg, hpbw_h_deg, front_to_back_dB, max_direction_deg.
    """
    key = antenna_kind.lower()
    try:
        fn = _DISPATCH[key]
    except KeyError:
        disponibles = ', '.join(sorted(set(_DISPATCH)))
        raise ValueError(f"antenna_kind '{antenna_kind}' no soportado. "
                         f"Disponibles: {disponibles}.")
    return fn(float(freq_hz), **params)
