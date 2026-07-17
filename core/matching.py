"""
================================================================================
MÓDULO: Red L de Adaptación de Impedancias (IMN)
================================================================================
Diseña una red L de dos elementos para adaptar Z_ant (antena, ~50 Ω) a
Z_diodo (diodo Schottky, compleja) a una frecuencia dada.

Optimización con scipy.optimize.minimize (Nelder-Mead) minimizando |Γ|
con modelos de pérdidas reales de componentes SMD:
    Q_L = 40  → R_L(serie) = ω·L / Q_L
    Q_C = 80  → R_C(serie) = 1 / (ω·C·Q_C)

Configuraciones:
    lowpass  — shunt-C en paralelo con (serie-L + Z_load)
    highpass — shunt-L en paralelo con (serie-C + Z_load)
    auto     — elige la que produce menor pérdida de inserción

La pérdida de inserción IL se calcula como ganancia de transductor inversa:
    IL_dB = −10·log10(GT)  con  GT = P_load / P_avs

Referencia: Pozar, Microwave Engineering 4ed §5.1.

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np
from scipy.optimize import minimize
from dataclasses import dataclass


@dataclass
class LMatchResult:
    """
    Resultado del diseño de una red L de adaptación.

    Atributos
    ---------
    freq             : frecuencia de diseño [Hz]
    Z_src            : impedancia fuente [Ω]
    Z_load           : impedancia carga [Ω]
    L                : inductancia óptima [H]
    C                : capacitancia óptima [F]
    topology         : 'lowpass' o 'highpass'
    insertion_loss_dB: pérdida de inserción [dB] (incluye Q finito de L y C)
    VSWR             : relación de onda estacionaria en la entrada
    """
    freq:              float
    Z_src:             complex
    Z_load:            complex
    L:                 float
    C:                 float
    topology:          str
    insertion_loss_dB: float
    VSWR:              float

    def __str__(self) -> str:
        return (f'{self.freq/1e9:.3f} GHz | {self.topology} | '
                f'L={self.L*1e9:.3f} nH  C={self.C*1e12:.3f} pF | '
                f'IL={self.insertion_loss_dB:.2f} dB  VSWR={self.VSWR:.2f} '
                f'| Z_load=({self.Z_load.real:.1f}{self.Z_load.imag:+.1f}j) Ω')


class LMatchNetwork:
    """
    Red L de dos elementos con pérdidas reales de componentes SMD.

    Transforma Z_src (antena, típicamente ~50 Ω real) hacia Z_load
    (impedancia del diodo Schottky, compleja) a una frecuencia dada.

    Parámetros de calidad SMD (valores típicos de mercado):
        Q_L = 40  → inductor SMD 0402/0603
        Q_C = 80  → capacitor SMD MLCC 0402/0603

    Uso típico:
        net = LMatchNetwork(Z_src=50.0)
        res = net.design(freq=2.45e9, Z_load=diode.impedance(2.45e9))
        print(res)
    """

    Q_L = 40.0   # factor Q de inductores SMD
    Q_C = 80.0   # factor Q de capacitores SMD

    def __init__(self, Z_src: complex = 50.0, Z_load: complex = None):
        """
        Parámetros
        ----------
        Z_src  : impedancia fuente [Ω] (típicamente 50+0j)
        Z_load : impedancia carga [Ω] (se puede fijar aquí o en design())
        """
        self.Z_src  = complex(Z_src)
        self.Z_load = complex(Z_load) if Z_load is not None else None

    # ── Funciones auxiliares de Γ y VSWR ─────────────────────────────────────

    @staticmethod
    def _gamma(Zin: complex, Z0: float) -> float:
        """Módulo del coeficiente de reflexión |Γ| = |(Zin−Z0)/(Zin+Z0)|."""
        return abs((Zin - Z0) / (Zin + Z0))

    @staticmethod
    def _vswr(gamma: float) -> float:
        """VSWR = (1+|Γ|)/(1−|Γ|)."""
        return (1 + gamma) / max(1 - gamma, 1e-9)

    # ── Impedancias de componentes con pérdidas ───────────────────────────────

    @classmethod
    def _ZL(cls, L: float, w: float) -> complex:
        """Impedancia de inductor con Q finito: Z_L = ω·L/Q_L + j·ω·L."""
        return complex(w * L / cls.Q_L, w * L)

    @classmethod
    def _ZC(cls, C: float, w: float) -> complex:
        """Impedancia de capacitor con Q finito: Z_C = 1/(ω·C·Q_C) − j/(ω·C)."""
        return complex(1.0 / (w * C * cls.Q_C), -1.0 / (w * C))

    # ── Impedancia de entrada de cada topología ───────────────────────────────

    @classmethod
    def _Zin_lp(cls, Zl: complex, L: float, C: float, w: float) -> complex:
        """Lowpass (LP): shunt-C en paralelo con (serie-L + Zl)."""
        Zs = cls._ZL(L, w) + Zl
        Zp = cls._ZC(C, w)
        return Zs * Zp / (Zs + Zp)

    @classmethod
    def _Zin_hp(cls, Zl: complex, L: float, C: float, w: float) -> complex:
        """Highpass (HP): shunt-L en paralelo con (serie-C + Zl)."""
        Zs = cls._ZC(C, w) + Zl
        Zp = cls._ZL(L, w)
        return Zs * Zp / (Zs + Zp)

    # ── Diseño ────────────────────────────────────────────────────────────────

    def design(self, freq: float, Z_load: complex = None,
               topology: str = 'auto') -> LMatchResult:
        """
        Diseña la red L para adaptar Z_src → Z_load a freq [Hz].

        Parámetros
        ----------
        freq     : frecuencia de diseño [Hz]
        Z_load   : impedancia carga [Ω] (sobreescribe el valor del constructor)
        topology : 'lowpass', 'highpass', o 'auto' (menor IL automáticamente)

        Retorna
        -------
        LMatchResult con L, C óptimos e IL, VSWR calculados.
        """
        if Z_load is not None:
            self.Z_load = complex(Z_load)
        if self.Z_load is None:
            raise ValueError('Z_load no definida. Pásela en design() o en el constructor.')

        if topology == 'auto':
            r_lp = self._optimize(freq, 'lowpass')
            r_hp = self._optimize(freq, 'highpass')
            return r_lp if r_lp.insertion_loss_dB <= r_hp.insertion_loss_dB else r_hp
        return self._optimize(freq, topology)

    # ── Co-diseño conjugado antena → diodo (rectena integrada) ────────────────

    def conjugate_efficiency(self, freq: float, Z_ant: complex,
                             Z_load: complex) -> float:
        """
        Eficiencia de transferencia de potencia de una red L con pérdidas (Q
        finito) que adapta por CONJUGADO una fuente compleja Z_ant (antena) a
        una carga compleja Z_load (diodo), SIN interfaz forzada de 50 Ω.

        Este es el modelo de una rectena INTEGRADA: la antena se conecta
        directamente, vía la red de adaptación, al diodo. No existe una línea de
        50 Ω, por lo que la "reflexión de la antena" (S11 referido a 50 Ω) NO es
        una pérdida; la única pérdida de acople es la de la propia red L por el Q
        finito de sus componentes SMD.

        Se optimizan numéricamente los dos elementos (L, C) en ambas
        orientaciones L para MAXIMIZAR la potencia entregada a Re(Z_load), y se
        devuelve η = P_entregada / P_disponible, con
        P_disponible = |V_s|² / (8·Re(Z_ant)).

        Contraste con design(): design() adapta una fuente de 50 Ω al diodo
        (arquitectura modular con línea de 50 Ω); conjugate_efficiency() adapta
        la impedancia real de la antena al diodo (arquitectura integrada). La
        diferencia entre ambas es justamente la "pérdida por reflexión de la
        antena" que penaliza a una geometría multibanda cuyo puerto no está a
        50 Ω. Referencia: Pozar 4ed §5.1; arquitectura integrada de rectena en
        Valenta & Durgin (2014) IEEE MTT-S.
        """
        w  = 2.0 * np.pi * freq
        Zs = complex(Z_ant)
        Zd = complex(Z_load)
        Rs = max(Zs.real, 1e-3)
        P_avs = 1.0 / (8.0 * Rs)   # con |V_s| = 1

        def eff(orient, x):
            L, C = 10 ** x[0], 10 ** x[1]
            if orient == 'A':
                Zser, Zsh = self._ZL(L, w), self._ZC(C, w)
            else:
                Zser, Zsh = self._ZC(C, w), self._ZL(L, w)
            Zpar = Zsh * Zd / (Zsh + Zd)
            Zin  = Zser + Zpar
            Iin  = 1.0 / (Zs + Zin)
            Vn   = Iin * Zpar
            Id   = Vn / Zd
            P_load = 0.5 * abs(Id) ** 2 * max(Zd.real, 0.0)
            return P_load / P_avs

        best = 0.0
        for orient in ('A', 'B'):
            L0 = 1.0 / (w * max(abs(Zd), 1.0))
            C0 = 1.0 / (w * max(abs(Zs), 1.0))
            x0 = [np.log10(max(L0, 1e-12)), np.log10(max(C0, 1e-15))]
            r = minimize(lambda x: -eff(orient, x), x0, method='Nelder-Mead',
                         options={'xatol': 1e-10, 'fatol': 1e-10, 'maxiter': 12000})
            best = max(best, -r.fun)
        return float(np.clip(best, 0.0, 1.0))

    def _optimize(self, freq: float, topology: str) -> LMatchResult:
        """
        Optimiza L y C minimizando |Γ| con Nelder-Mead.
        La búsqueda se realiza en espacio logarítmico (x = log10(L o C)).
        """
        w       = 2 * np.pi * freq
        Zin_fn  = self._Zin_lp if topology == 'lowpass' else self._Zin_hp
        Z0      = self.Z_src.real

        def cost(x):
            L, C = 10 ** x[0], 10 ** x[1]
            return self._gamma(Zin_fn(self.Z_load, L, C, w), Z0)

        # Punto inicial: L que resuene con |Z_load| y C con |Z_src|
        L0 = 1 / (w * max(abs(self.Z_load), 1.0))
        C0 = 1 / (w * max(abs(self.Z_src),  1.0))
        x0 = [np.log10(max(L0, 1e-12)), np.log10(max(C0, 1e-15))]

        res = minimize(cost, x0, method='Nelder-Mead',
                       options={'xatol': 1e-9, 'fatol': 1e-9, 'maxiter': 8000})

        L_opt, C_opt = 10 ** res.x[0], 10 ** res.x[1]
        Zin_opt      = Zin_fn(self.Z_load, L_opt, C_opt, w)
        gamma        = self._gamma(Zin_opt, Z0)

        # Pérdida de inserción: ganancia de transductor inversa
        I_in   = 1.0 / (Z0 + Zin_opt)
        V_node = I_in * Zin_opt
        Z_ser  = (self._ZL(L_opt, w) + self.Z_load
                  if topology == 'lowpass'
                  else self._ZC(C_opt, w) + self.Z_load)
        I_load = V_node / Z_ser
        P_load = 0.5 * abs(I_load) ** 2 * max(self.Z_load.real, 0.0)
        P_avs  = 1.0 / (8.0 * Z0)
        GT     = max(P_load / P_avs, 1e-10)
        IL_dB  = -10.0 * np.log10(GT)

        return LMatchResult(
            freq=freq, Z_src=self.Z_src, Z_load=self.Z_load,
            L=L_opt, C=C_opt, topology=topology,
            insertion_loss_dB=IL_dB, VSWR=self._vswr(gamma),
        )

