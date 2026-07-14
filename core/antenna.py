"""
================================================================================
MÓDULO: Antena Fractal — Sierpinski Gasket (Escenario A)
================================================================================
Modelo analítico de antena fractal para RF Energy Harvesting multibanda.

Sustrato: FR-4 con permitividad dinámica εr(f): 4.4 @ 1 GHz → 4.1 @ 5.8 GHz.
Modelo de impedancia: resonancias RLC en paralelo + fondo inductivo.
S11 calculado desde Γ = (Za − Z0)/(Za + Z0).

IMPORTANTE — soporte de 'koch' limitado a geometría:
    FractalAntenna admite fractal_type='koch' únicamente para generar la curva
    de Koch con geometry_points() (usada en la figura pedagógica de plegado
    del dipolo, Cap. 3). Los métodos físicos (S11_dB, impedance, eta_rad,
    gain_dBi) NO están calibrados para 'koch' y no deben usarse con ese tipo:
    el modelo físico real del Escenario B (FLPDA Koch) vive en core/flpda.py
    (clase FLPDA_Koch), que sí reproduce los valores canónicos del documento.

IMPORTANTE — Interpretación del S11 calculado:
    S11_dB() retorna el coeficiente de reflexión de la antena SOLA (sin IMN).
    Debido a la inductancia de fondo (Lbg ≈ 45/ω₀), la reactancia de Za a la
    frecuencia fundamental es ~+j45 Ω, lo que limita el S11 a ~−8 dB incluso
    en las bandas de resonancia fractal. Este comportamiento es físicamente
    correcto para una antena sin red de adaptación.

    El sistema completo (antena + IMN + rectificador) se evalúa en los scripts
    de simulación mediante LMatchNetwork.design() y RectifierCircuit.PCE().
    La métrica de sistema relevante para tesis es la PCE final, no el S11 aislado.

    Diferencia con Wang et al. (2022): el Sierpinski puro resuena en f0, 2f0, 4f0.
    Wang usa geometría multi-banda optimizada que logra resonancias en 7 bandas.
    El gap de PCE entre este modelo y Wang refleja esta diferencia estructural.

Referencias:
    Wang et al. (2022) IEEE TAP — geometría y bandas objetivo (referencia de validación)
    Bahl & Trivedi (1977) — εr dinámico FR-4
    Pozar, Microwave Engineering 4ed §2 — análisis de potencia y reflexión

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np

# ── Parámetros de estilo IEEE para matplotlib ─────────────────────────────────
IEEE_RCPARAMS = {
    'font.family':      'serif',
    'font.size':        10,
    'axes.labelsize':   11,
    'axes.titlesize':   12,
    'legend.fontsize':  9,
    'xtick.labelsize':  9,
    'ytick.labelsize':  9,
    'figure.dpi':       150,
    'savefig.dpi':      300,
    'axes.grid':        True,
    'grid.alpha':       0.3,
    'lines.linewidth':  1.5,
    'axes.axisbelow':   True,
}


class FractalAntenna:
    """
    Antena fractal multibanda para RF Energy Harvesting.

    Tipos soportados: 'sierpinski', 'koch'.
    Escenario A: Sierpinski it.3, FR-4 εr dinámico, f0=1.84 GHz, hasta 5.8 GHz.

    Atributos calculados
    --------------------
    base_dim      : longitud base λ_eff/2 en f0 [m]
    resonant_frequencies : lista de frecuencias de resonancia fractal [Hz]
    target_bands  : dict {nombre_banda: frecuencia_Hz}
    """

    _SCALE = {'sierpinski': 2.0, 'koch': 3.0}

    def __init__(self,
                 fractal_type: str = 'sierpinski',
                 iterations:   int = 3,
                 base_freq:    float = 1.84e9,
                 h:            float = 1.6e-3):
        """
        Parámetros
        ----------
        fractal_type : 'sierpinski' o 'koch'
        iterations   : número de iteraciones fractales (3 recomendado)
        base_freq    : frecuencia fundamental de diseño [Hz]
        h            : espesor del sustrato FR-4 [m]
        """
        self.fractal_type = fractal_type
        self.iterations   = iterations
        self.base_freq    = base_freq
        self.h            = h
        self.c0           = 3e8          # velocidad de la luz [m/s]
        self.loss_tan     = 0.02         # tan δ de FR-4
        self.scale_ratio  = self._SCALE.get(fractal_type, 2.0)

        self._calc_dimensions()
        self.resonant_frequencies = self._calc_resonances()

        # Bandas objetivo Escenario A
        self.target_bands = {
            'GSM1800':  1.84e9,
            'LTE':      2.04e9,
            'WiFi_2.4': 2.45e9,
            '5G_2.6':   2.54e9,
            '5G_3.5':   3.30e9,
            '5G_4.9':   4.76e9,
            'WiFi_5.8': 5.80e9,
        }

    # ── Propiedades del sustrato ──────────────────────────────────────────────

    def get_er(self, freq: float) -> float:
        """
        Permitividad relativa dinámica FR-4.
        Interpola linealmente εr=4.4 @ 1 GHz → εr=4.1 @ 5.8 GHz.
        Valores fuera de rango son clipeados al extremo correspondiente.
        Referencia: Bahl & Trivedi (1977); Pozar cap. 3.
        """
        f_GHz  = freq / 1e9
        er_low,  f_low  = 4.4, 1.0
        er_high, f_high = 4.1, 5.8
        t = float(np.clip((f_GHz - f_low) / (f_high - f_low), 0.0, 1.0))
        return er_low + t * (er_high - er_low)

    # ── Geometría y resonancias ───────────────────────────────────────────────

    def _calc_dimensions(self):
        """Calcula dimensiones base λ_eff/2 a f0."""
        er0           = self.get_er(self.base_freq)
        lam_eff       = self.c0 / (self.base_freq * np.sqrt(er0))
        self.base_dim = lam_eff / 2          # [m]
        self.width    = self.base_dim
        self.height   = self.base_dim if self.fractal_type == 'sierpinski' else self.base_dim * 0.4

    def _calc_resonances(self) -> list:
        """
        Calcula frecuencias de resonancia del fractal.
        Sierpinski: f_k = f0 · 2^k  (k=0,1,2)  — escala de similitud 2.
        Koch:       f_k = f0 · (4/3)^k + armónicos.
        """
        freqs = []
        if self.fractal_type == 'sierpinski':
            for k in range(3):
                freqs.append(self.base_freq * (self.scale_ratio ** k))
        elif self.fractal_type == 'koch':
            for i in range(self.iterations + 2):
                f = self.base_freq * (4 / 3) ** i
                if f < 10e9:
                    freqs.append(f)
            for f0 in freqs[:3]:
                for h in [2, 3]:
                    fh = f0 * h
                    if fh < 10e9:
                        freqs.append(fh)
        return sorted(set(freqs))

    # ── Parámetros del resonador ──────────────────────────────────────────────

    def _Q(self, freq: float) -> float:
        """Factor de calidad Q.  FR-4 (εr≥3): Q=8.5 (fijo, dominado por tan δ)."""
        er = self.get_er(freq)
        if er >= 3.0:
            return 8.5
        return max(20 * (self.base_freq / freq) ** 0.3, 5)

    # ── Modelos electromagnéticos ─────────────────────────────────────────────

    def impedance(self, freq):
        """
        Impedancia de entrada Za(f) [Ω] — modelo RLC en paralelo.

        Cada resonancia fr_k se modela como una rama RLC serie:
            R_k = 60 · 0.85^k  [Ω]  (resistencia de radiación)
            Q_k = _Q(fr_k)
            L_k = R_k·Q_k/ω_k · √(εr_k/4.4)
            C_k = 1/(ω_k²·L_k)
        Las ramas se combinan en paralelo. El fondo incluye Rbg e inductancia base.
        """
        if self.fractal_type != 'sierpinski':
            raise NotImplementedError(
                "impedance()/S11_dB() solo están calibrados para fractal_type="
                "'sierpinski'. Para el Escenario B (FLPDA Koch) use core.flpda.FLPDA_Koch."
            )
        freq  = np.atleast_1d(np.asarray(freq, dtype=float))
        Z     = np.zeros(len(freq), dtype=complex)
        ω0    = 2.0 * np.pi * self.base_freq
        L_bg0 = 45.0 / ω0   # inductancia de fondo [H]

        for i, f in enumerate(freq):
            er_f  = self.get_er(f)
            ω     = 2.0 * np.pi * f
            c_eff = self.c0 / np.sqrt(er_f)
            scale = (self.c0 / np.sqrt(self.get_er(self.base_freq))) / c_eff
            L_bg  = L_bg0 * scale
            Z_bg  = complex(8.0, ω * L_bg)   # pérdidas conductor + inductancia base

            Y_modes = 0j
            for k, fr in enumerate(self.resonant_frequencies):
                er_r  = self.get_er(fr)
                Rk    = 60.0 * (0.85 ** k)
                Qk    = self._Q(fr)
                ω_k   = 2.0 * np.pi * fr
                Lk    = Rk * Qk / ω_k * np.sqrt(er_r / 4.4)
                Ck    = 1.0 / (ω_k ** 2 * Lk)
                Zk    = Rk + 1j * (ω * Lk - 1.0 / (ω * Ck))
                Y_modes += 1.0 / Zk

            Z_modes = 1.0 / Y_modes if abs(Y_modes) > 1e-15 else complex(1e6, 0.0)
            Z[i]    = Z_bg + Z_modes

        return Z if len(Z) > 1 else Z[0]

    def S11_dB(self, freq):
        """
        Coeficiente de reflexión S11 [dB].
        Γ = (Za − Z0) / (Za + Z0),  Z0 = 50 Ω.
        """
        freq  = np.atleast_1d(np.asarray(freq, dtype=float))
        Za    = np.atleast_1d(self.impedance(freq))
        Z0    = 50.0
        gamma = (Za - Z0) / (Za + Z0)
        s11   = 20.0 * np.log10(np.maximum(np.abs(gamma), 1e-6))
        return s11 if len(s11) > 1 else float(s11[0])

    def eta_rad(self, freq: float) -> float:
        """
        Eficiencia de radiación η_rad [0–1] — modelo realista para FR-4 dispersivo.

        η_rad = 1 / (1 + L_diel + L_cond), con εr(f) y tan δ(f) dependientes de la
        frecuencia (FR-4 es un material dispersivo: εr decrece y tan δ crece con f):
            L_diel = tan δ(f) · √εr(f) · 8 · (0,3 + f[GHz])
            L_cond = 0,05 · √(f[GHz])
        Resultado: η_rad ≈ 0,61 @1,84 GHz y ≈ 0,32 @5,8 GHz, coherente con las
        altas pérdidas del FR-4 en microondas. Sustituye el modelo previo, que
        daba η≈0,95 @5,8 GHz (físicamente irreal).
        """
        if self.fractal_type != 'sierpinski':
            raise NotImplementedError(
                "eta_rad() solo está calibrado para fractal_type='sierpinski'. "
                "Para el Escenario B (FLPDA Koch) use core.flpda.FLPDA_Koch.eta_rad()."
            )
        from configs.parametros import fr4_tan_delta
        fghz   = float(np.asarray(freq, dtype=float).ravel()[0]) / 1e9
        er_f   = self.get_er(freq)
        td_f   = fr4_tan_delta(freq)
        L_diel = td_f * np.sqrt(er_f) * 8.0 * (0.3 + fghz)
        L_cond = 0.05 * fghz ** 0.5
        eta = 1.0 / (1.0 + L_diel + L_cond)
        return float(np.clip(eta, 0.20, 0.85))

    def gain_dBi(self, freq):
        """
        Ganancia realizada [dBi].
        G = G0 + 0.5·log10(f/f0) + 10·log10(η_rad).
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        G0   = {'sierpinski': 2.5, 'koch': 2.0}.get(self.fractal_type, 2.2)
        g    = np.array([
            G0 + 0.5 * np.log10(f / self.base_freq) + 10 * np.log10(self.eta_rad(f))
            for f in freq
        ])
        return g if len(g) > 1 else float(g[0])

    # ── Geometría fractal ─────────────────────────────────────────────────────

    def geometry_points(self, iterations: int = None):
        """
        Puntos (x,y) normalizados de la geometría fractal (para visualización).
        Sierpinski: lista de triángulos [[p0,p1,p2], ...].
        Koch:       lista de puntos [p0, p1, ...].
        """
        it = iterations if iterations is not None else self.iterations
        if self.fractal_type == 'sierpinski':
            return self._sierpinski(it)
        if self.fractal_type == 'koch':
            return self._koch(it)
        raise ValueError(f"Tipo fractal '{self.fractal_type}' no soportado. Use 'sierpinski' o 'koch'.")

    def _sierpinski(self, depth: int):
        """Genera triángulos del Sierpinski Gasket de forma recursiva."""
        def recurse(v, d):
            if d == 0:
                return [v]
            m01 = [(v[0][0]+v[1][0])/2, (v[0][1]+v[1][1])/2]
            m12 = [(v[1][0]+v[2][0])/2, (v[1][1]+v[2][1])/2]
            m02 = [(v[0][0]+v[2][0])/2, (v[0][1]+v[2][1])/2]
            return (recurse([v[0], m01, m02], d-1) +
                    recurse([m01, v[1], m12], d-1) +
                    recurse([m02, m12, v[2]], d-1))
        h = np.sqrt(3) / 2
        return recurse([[0,0],[1,0],[0.5,h]], depth)

    def _koch(self, depth: int):
        """Genera puntos de la curva de Koch de forma recursiva."""
        def seg(p1, p2, d):
            if d == 0:
                return [p1, p2]
            dx, dy = p2[0]-p1[0], p2[1]-p1[1]
            pa   = [p1[0]+dx/3,   p1[1]+dy/3]
            pb   = [p1[0]+2*dx/3, p1[1]+2*dy/3]
            ang  = np.arctan2(dy, dx) + np.pi/3
            L    = np.hypot(dx, dy) / 3
            pk   = [pa[0]+L*np.cos(ang), pa[1]+L*np.sin(ang)]
            pts  = []
            pts.extend(seg(p1, pa, d-1)[:-1])
            pts.extend(seg(pa, pk, d-1)[:-1])
            pts.extend(seg(pk, pb, d-1)[:-1])
            pts.extend(seg(pb, p2, d-1))
            return pts
        return seg([0,0],[1,0], depth)

    # ── Propiedades adicionales ───────────────────────────────────────────────

    @property
    def fractal_resonances_hz(self) -> list:
        """
        Frecuencias de resonancia FRACTAL puras [Hz] (las que emergen de la
        geometría: f0·ratio^k para Sierpinski, o la serie Koch).
        Distinto de resonant_frequencies que puede incluir modos adicionales.
        """
        if self.fractal_type == 'sierpinski':
            return [self.base_freq * (self.scale_ratio ** k) for k in range(3)]
        return list(self.resonant_frequencies)

    def eta_sys(self, freq: float, IL_imn_dB: float = 0.0,
                gamma_imn: float = 0.0) -> float:
        """
        Eficiencia total de la cadena antena+IMN [0..1].
        η_sys = η_rad · (1 − γ²_IMN) · 10^(−IL_IMN/10).

        Parámetros
        ----------
        freq       : frecuencia de evaluación [Hz]
        IL_imn_dB  : pérdida de inserción de la red L [dB] (de LMatchNetwork)
        gamma_imn  : coeficiente de reflexión residual de la IMN [0..1]
        """
        eta_r     = self.eta_rad(freq)
        eta_match = (1.0 - gamma_imn ** 2) * 10.0 ** (-IL_imn_dB / 10.0)
        return float(np.clip(eta_r * eta_match, 0.0, 1.0))

    # ── Resumen ───────────────────────────────────────────────────────────────

    def summary(self) -> str:
        """Resumen de diseño en texto."""
        er0 = self.get_er(self.base_freq)
        fr_fractal = [f'{f/1e9:.2f}' for f in self.fractal_resonances_hz if f < 7e9]
        lines = [
            f'FractalAntenna -- {self.fractal_type.capitalize()} it.{self.iterations}',
            f'  f0               : {self.base_freq/1e9:.3f} GHz',
            f'  Sustrato         : FR-4  er(f0)={er0:.2f}  h={self.h*1e3:.1f} mm  tand={self.loss_tan}',
            f'  Dimension        : {self.base_dim*1e3:.1f} mm  (lam_eff/2 @ f0)',
            f'  Factor escala    : {self.scale_ratio}',
            f'  Res. fractales   : {fr_fractal} GHz  (f0*ratio^k)',
            f'  Bandas objetivo  : {len(self.target_bands)}  (Wang et al. 2022)',
            f'  NOTA: S11_dB() = antena sin IMN -- ver eta_sys() para sistema completo',
        ]
        return '\n'.join(lines)
