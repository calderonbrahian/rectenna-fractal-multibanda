"""
================================================================================
MÓDULO: Antena de Parche Microcinta — modelo analítico de cavidad
================================================================================
Parche rectangular alimentado por inset, modelado con las ecuaciones clásicas de
línea de transmisión / cavidad de Balanis (Antenna Theory, 4ª ed., cap. 14) — el
mismo juego de fórmulas que emplean los papers de referencia de la tesis para
dimensionar parches multibanda sobre distintos sustratos.

ALCANCE (§1.2): es un MODELO ANALÍTICO DE CAVIDAD, no un solucionador full-wave.
Reproduce dimensiones, resonancias de los modos TM_mn, eficiencia de radiación y
ganancia con una exactitud típica de ±1,5 dBi frente a simulación electromagnética
(CST/HFSS). Su propósito es el ESTUDIO COMPARATIVO antena × sustrato, no el diseño
de fabricación final.

Ecuaciones (Balanis cap. 14):
    W        = c/(2 f0) · √(2/(εr+1))
    ε_eff    = (εr+1)/2 + (εr−1)/2 · (1 + 12 h/W)^(−1/2)
    ΔL       = 0,412 h (ε_eff+0,3)(W/h+0,264) / [(ε_eff−0,258)(W/h+0,8)]
    L        = c/(2 f0 √ε_eff) − 2 ΔL
    f_mn     = c/(2√ε_eff) · √[(m/L_eff)² + (n/W_eff)²],  L_eff=L+2ΔL, W_eff=W+2ΔL

Eficiencia de radiación por reparto de factores de calidad:
    Q_rad  = c √ε_eff / (4 f h)              (radiación; ∝ 1/h)
    Q_diel = 1/tan δ(f)                       (pérdidas dieléctricas)
    Q_cond = h √(π f μ0 σ_cu)                 (pérdidas de conductor, σ_cu=5,8·10⁷)
    1/Q_t  = 1/Q_rad + 1/Q_diel + 1/Q_cond
    η_rad  = Q_t / Q_rad

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np

from core.substrates import get_substrate

# ── Constantes físicas ────────────────────────────────────────────────────────
_C0       = 3e8            # velocidad de la luz [m/s]
_MU0      = 4e-7 * np.pi   # permeabilidad del vacío [H/m]
_SIGMA_CU = 5.8e7          # conductividad del cobre [S/m]
_Z0       = 50.0           # impedancia de referencia [Ω]
_D0_DBI   = 6.9            # directividad típica de un parche (Balanis) [dBi]

# Factor de inset: fracción de la resistencia de borde vista en el punto de
# alimentación (inset elegido para adaptar ≈50 Ω en el modo dominante TM10).
_INSET_FACTOR = 0.12


class MicrostripPatchAntenna:
    """
    Parche rectangular microcinta alimentado por inset (modelo de cavidad).

    Parámetros
    ----------
    f0_hz     : frecuencia de diseño del modo dominante TM10 [Hz]
    substrate : nombre ('FR4', 'RT5880', 'RO4003C') u objeto Substrate

    Atributos calculados
    --------------------
    W, L                : ancho y largo físicos [m]
    dL                  : extensión de línea por franjas de borde [m]
    eps_eff             : permitividad efectiva [adimensional]
    W_eff, L_eff        : dimensiones efectivas (incluyen 2ΔL) [m]
    modes               : lista [(nombre, m, n, f_mn, dim_radiante)]
    """

    # (nombre, m, n) de los modos de cavidad expuestos como multibanda analítica
    _MODES = (('TM10', 1, 0), ('TM01', 0, 1), ('TM20', 2, 0))

    def __init__(self, f0_hz: float = 2.45e9, substrate: str = 'FR4'):
        self.f0        = float(f0_hz)
        self.substrate = get_substrate(substrate)
        self.h         = self.substrate.h
        self.c0        = _C0

        self._calc_dimensions()
        self._calc_modes()

    # ── Geometría (Balanis cap. 14) ───────────────────────────────────────────

    def _calc_dimensions(self):
        """Dimensiona W, ε_eff, ΔL y L a la frecuencia de diseño f0."""
        er = self.substrate.er(self.f0)
        self.er_f0 = er

        # Ancho: máxima eficiencia de radiación (Balanis 14-6)
        self.W = self.c0 / (2.0 * self.f0) * np.sqrt(2.0 / (er + 1.0))

        # Permitividad efectiva (Balanis 14-1)
        self.eps_eff = (er + 1.0) / 2.0 + (er - 1.0) / 2.0 * \
            (1.0 + 12.0 * self.h / self.W) ** (-0.5)

        # Extensión de longitud por franjas de borde (Balanis 14-2)
        e = self.eps_eff
        Wh = self.W / self.h
        self.dL = 0.412 * self.h * (e + 0.3) * (Wh + 0.264) / \
            ((e - 0.258) * (Wh + 0.8))

        # Longitud resonante (Balanis 14-3)
        self.L = self.c0 / (2.0 * self.f0 * np.sqrt(e)) - 2.0 * self.dL

        # Dimensiones efectivas de la cavidad
        self.L_eff = self.L + 2.0 * self.dL
        self.W_eff = self.W + 2.0 * self.dL

    def _f_mn(self, m: int, n: int) -> float:
        """Frecuencia de resonancia del modo TM_mn de la cavidad [Hz]."""
        return self.c0 / (2.0 * np.sqrt(self.eps_eff)) * \
            np.sqrt((m / self.L_eff) ** 2 + (n / self.W_eff) ** 2)

    def _calc_modes(self):
        """Precalcula frecuencia y dimensión radiante de cada modo expuesto."""
        modos = []
        for name, m, n in self._MODES:
            f = self._f_mn(m, n)
            # Dimensión de los slots que radian el modo: W para modos m-along-L,
            # L para el modo TM01 (radia por el par de bordes de longitud L).
            dim_rad = self.L if (m == 0) else self.W
            modos.append((name, m, n, f, dim_rad))
        self.modes = modos

    def resonances(self) -> list:
        """Frecuencias de resonancia [Hz] de TM10, TM01, TM20, ordenadas."""
        return sorted(f for (_n, _m, _k, f, _d) in self.modes)

    # ── Eficiencia de radiación (reparto de Q) ────────────────────────────────

    def _Q_factors(self, freq: float) -> tuple:
        """Devuelve (Q_rad, Q_diel, Q_cond) a la frecuencia freq [Hz]."""
        f = float(np.asarray(freq, dtype=float).ravel()[0])
        Q_rad  = self.c0 * np.sqrt(self.eps_eff) / (4.0 * f * self.h)
        Q_diel = 1.0 / max(self.substrate.tan_delta(f), 1e-9)
        Q_cond = self.h * np.sqrt(np.pi * f * _MU0 * _SIGMA_CU)
        return Q_rad, Q_diel, Q_cond

    def eta_rad(self, freq: float) -> float:
        """
        Eficiencia de radiación η_rad ∈ (0,1) por reparto de factores de calidad.

        η_rad = Q_total / Q_rad, con 1/Q_total = 1/Q_rad + 1/Q_diel + 1/Q_cond.
        Un sustrato de bajas pérdidas (RT5880, tan δ=0,0009) apenas carga la
        cavidad y radia casi toda la potencia; el FR-4 (tan δ=0,02) disipa una
        fracción notable en el dieléctrico → η_rad(RT5880) ≫ η_rad(FR4).
        """
        Q_rad, Q_diel, Q_cond = self._Q_factors(freq)
        inv_Qt = 1.0 / Q_rad + 1.0 / Q_diel + 1.0 / Q_cond
        Q_total = 1.0 / inv_Qt
        return float(Q_total / Q_rad)

    def _Q_loaded(self, freq: float) -> float:
        """Q cargado total del modo (ancho de banda de la resonancia)."""
        Q_rad, Q_diel, Q_cond = self._Q_factors(freq)
        return 1.0 / (1.0 / Q_rad + 1.0 / Q_diel + 1.0 / Q_cond)

    # ── Resistencia de radiación en el punto de alimentación ──────────────────

    def _edge_resistance(self, dim_rad: float, freq: float) -> float:
        """
        Resistencia de borde del par de slots radiantes (modelo de conductancia
        de ranura, Balanis 14-12): G1 ≈ (1/90)(dim/λ0)² para dim < λ0.
        R_borde = 1/(2 G1). Con inset se ve R_in = R_borde · _INSET_FACTOR.
        """
        f = float(np.asarray(freq, dtype=float).ravel()[0])
        lam0 = self.c0 / f
        G1 = (1.0 / 90.0) * (dim_rad / lam0) ** 2
        G1 = max(G1, 1e-6)
        R_edge = 1.0 / (2.0 * G1)
        return R_edge * _INSET_FACTOR

    # ── Impedancia y reflexión ────────────────────────────────────────────────

    def impedance(self, freq):
        """
        Impedancia de entrada Za(f) [Ω] — superposición de modos RLC en paralelo.

        Cada modo TM_mn se modela como rama RLC serie con resistencia en resonancia
        R_k (resistencia de borde escalada por el inset) y Q cargado del modo:
            L_k = R_k·Q_k/ω_k ,  C_k = 1/(ω_k²·L_k)
        Las ramas se combinan en paralelo (mismo patrón que FractalAntenna).
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        Z = np.zeros(len(freq), dtype=complex)

        for i, f in enumerate(freq):
            omega = 2.0 * np.pi * f
            Y = 0j
            for (_name, _m, _n, f_res, dim_rad) in self.modes:
                omega_r = 2.0 * np.pi * f_res
                Rk = self._edge_resistance(dim_rad, f_res)
                Qk = self._Q_loaded(f_res)
                Lk = Rk * Qk / omega_r
                Ck = 1.0 / (omega_r ** 2 * Lk)
                Zk = Rk + 1j * (omega * Lk - 1.0 / (omega * Ck))
                Y += 1.0 / Zk
            Z[i] = 1.0 / Y if abs(Y) > 1e-15 else complex(1e6, 0.0)

        return Z if len(Z) > 1 else Z[0]

    def S11_dB(self, freq):
        """Coeficiente de reflexión S11 [dB]: Γ=(Za−Z0)/(Za+Z0), Z0=50 Ω."""
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        Za = np.atleast_1d(self.impedance(freq))
        gamma = (Za - _Z0) / (Za + _Z0)
        s11 = 20.0 * np.log10(np.maximum(np.abs(gamma), 1e-6))
        return s11 if len(s11) > 1 else float(s11[0])

    # ── Ganancia ──────────────────────────────────────────────────────────────

    def gain_dBi(self, freq):
        """
        Ganancia realizada [dBi] = directividad de parche (≈6,9 dBi, Balanis) +
        10·log10(η_rad). La pérdida de eficiencia del FR-4 recorta ~2,5 dB frente
        a un sustrato de bajas pérdidas.
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        g = np.array([_D0_DBI + 10.0 * np.log10(max(self.eta_rad(f), 1e-6))
                      for f in freq])
        return g if len(g) > 1 else float(g[0])

    # ── Tablas y figura ───────────────────────────────────────────────────────

    def dimensions(self) -> dict:
        """
        Dimensiones de diseño en mm (ε_eff adimensional) para tablas del documento.
        Orden fijo: W, L, h, dL, eps_eff, W_eff, L_eff.
        """
        return {
            'W_mm':      round(self.W * 1e3, 3),
            'L_mm':      round(self.L * 1e3, 3),
            'h_mm':      round(self.h * 1e3, 3),
            'dL_mm':     round(self.dL * 1e3, 4),
            'eps_eff':   round(self.eps_eff, 4),
            'W_eff_mm':  round(self.W_eff * 1e3, 3),
            'L_eff_mm':  round(self.L_eff * 1e3, 3),
        }

    def geometry_points(self) -> dict:
        """
        Contorno del parche y línea de alimentación inset simple (en mm),
        centrado en el origen, para la figura técnica FigP1.

        Retorna dict con:
            'patch' : polígono cerrado del parche [(x,y),...]
            'feed'  : línea de alimentación [(x,y),(x,y)]
            'inset' : dos muescas del inset [[(x,y),(x,y)], ...]
            'W','L' : dimensiones en mm
        """
        W = self.W * 1e3
        L = self.L * 1e3
        # Rectángulo del parche centrado en el origen (W en x, L en y)
        x0, x1 = -W / 2.0, W / 2.0
        y0, y1 = -L / 2.0, L / 2.0
        patch = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]

        # Línea de alimentación (microcinta ~ inset) entrando por el borde y0
        wf = min(3.0, W * 0.12)          # ancho de la línea de alimentación [mm]
        inset_depth = L * 0.30           # profundidad del inset [mm]
        feed_len = L * 0.35              # tramo externo de la línea
        feed = [(0.0, y0 - feed_len), (0.0, y0 + inset_depth)]

        # Muescas del inset (dos ranuras a ambos lados de la línea)
        gap = wf * 0.9
        inset = [
            [(-gap, y0), (-gap, y0 + inset_depth)],
            [(+gap, y0), (+gap, y0 + inset_depth)],
        ]
        return {'patch': patch, 'feed': feed, 'inset': inset, 'W': W, 'L': L,
                'wf': wf, 'inset_depth': inset_depth}

    # ── Resumen ───────────────────────────────────────────────────────────────

    def summary(self) -> str:
        """Resumen de diseño en texto."""
        d = self.dimensions()
        res = [f'{f/1e9:.3f}' for f in self.resonances()]
        return '\n'.join([
            f'MicrostripPatchAntenna — {self.substrate.name}',
            f'  f0        : {self.f0/1e9:.3f} GHz',
            f'  Sustrato  : {self.substrate.name}  εr(f0)={self.er_f0:.3f}  '
            f'h={self.h*1e3:.3f} mm  tan δ={self.substrate.tan_delta(self.f0):.4f}',
            f'  W×L       : {d["W_mm"]:.2f} × {d["L_mm"]:.2f} mm  (ε_eff={d["eps_eff"]:.3f})',
            f'  Resonancias TM: {res} GHz',
            f'  η_rad(f0) : {self.eta_rad(self.f0):.3f}   G(f0)={float(self.gain_dBi(self.f0)):.2f} dBi',
        ])
