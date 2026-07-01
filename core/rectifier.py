"""
================================================================================
MÓDULO: Rectificador RF-DC — Diodo Schottky SMS7630 + topologías
================================================================================
Modelo analítico del rectificador basado en la ecuación de Shockley con
parámetros SPICE oficiales del diodo Skyworks SMS7630.

La PCE (Power Conversion Efficiency) se calcula por análisis autorreferente:
    1. P_avail → V_oc_pk = √(8·P·Re(Z_d))
    2. Iteración de V_f por ecuación de Shockley (convergencia amortiguada)
    3. V_dc = N·(V_oc_pk − V_f)
    4. PCE = P_dc_net / P_in   (clipeado en [0, 85%])

Topologías disponibles:
    'halfwave' — media onda, 1 diodo
    'doubler'  — doblador de voltaje, 2 diodos (recomendado para IoT)
    'dickson3' — Dickson 3 etapas, 6 diodos (mejor voltaje a baja potencia)

Nota sobre validación:
    El modelo usa Is=5 µA (valor SPICE oficial SMS7630). El error es asimétrico:
    sobrestimación en 1.84–2.04 GHz (+25 y +12 pp) por asunción de adaptación
    perfecta; subestimación en 3.3–5.8 GHz (−4 a −19 pp) por efectos capacitivos
    del diodo a alta frecuencia. RMSE = 15.50 pp @ Pin=−10 dBm vs Wang et al. (2022).
    La diferencia de sustrato (FR-4 tanδ=0.02 vs Duroid 5880 tanδ=0.0009) explica
    parcialmente la subestimación en bandas altas.

    El S11 del rectificador NO se calcula en este módulo (fue eliminado por ser
    un modelo decorativo sin base física). El matching se maneja en matching.py
    mediante la red L con pérdidas reales (Q_L=40, Q_C=80).

Referencias:
    Skyworks SMS7630 datasheet, AN-4003 — parámetros SPICE
    Wang et al. (2022) IEEE TAP — referencia de validación
    Pozar, Microwave Engineering 4ed §2 — análisis de potencia disponible

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np


class SchottkyDiode_SMS7630:
    """
    Modelo SPICE del diodo Schottky Skyworks SMS7630.

    Parámetros extraídos del modelo SPICE oficial (Skyworks, AN-4003):
        Is  = 5 µA      — corriente de saturación
        n   = 1.05      — factor de idealidad
        Rs  = 20 Ω      — resistencia serie
        Cj0 = 0.14 pF   — capacitancia de juntura a 0 V
        Vj  = 0.34 V    — potencial de juntura
        M   = 0.40      — coeficiente de gradación

    Nota: algunos papers citan Is=5 nA (modelo simplificado).
    Se usa el valor oficial Is=5 µA.
    """

    def __init__(self):
        # Parámetros SPICE SMS7630 — SSOT: configs/parametros.py (Skyworks AN-4003)
        from configs.parametros import SMS7630, Q_E, K_B
        self.Is  = SMS7630['Is']    # corriente de saturación [A]
        self.n   = SMS7630['n']     # factor de idealidad
        self.Rs  = SMS7630['Rs']    # resistencia serie [Ω]
        self.Cj0 = SMS7630['Cj0']   # capacitancia de juntura a 0 V [F]
        self.Vj  = SMS7630['Vj']    # potencial de juntura [V]
        self.M   = SMS7630['M']     # coeficiente de gradiente

        # Constantes físicas (SSOT: configs/parametros.py)
        self.q  = Q_E              # carga del electrón [C]
        self.k  = K_B              # constante de Boltzmann [J/K]
        self.T  = 300.0        # temperatura de operación [K]
        self.Vt = self.k * self.T / self.q   # voltaje térmico ≈ 25.85 mV

    # ── Modelos del diodo ─────────────────────────────────────────────────────

    def Cj(self, V: float) -> float:
        """
        Capacitancia de juntura [F] vs voltaje de polarización V [V].
        Modelo estándar SPICE: Cj = Cj0/(1−V/Vj)^M  para V < Vj.
        """
        if V < self.Vj:
            return self.Cj0 / (1 - V / self.Vj) ** self.M
        return self.Cj0 * (1 + self.M * (V - self.Vj) / self.Vj)

    def Id(self, V: float) -> float:
        """Corriente de diodo [A] — ecuación de Shockley: Is·(exp(V/n·Vt)−1)."""
        return self.Is * (np.exp(V / (self.n * self.Vt)) - 1)

    def Rd(self, V: float) -> float:
        """Resistencia dinámica [Ω] = n·Vt / max(Id, 1e-12)."""
        return self.n * self.Vt / max(self.Id(V), 1e-12)

    def impedance(self, freq: float, V_bias: float = 0.0) -> complex:
        """
        Impedancia compleja del diodo [Ω].
        Modelo: Rs en serie con (Rd || Cj) a frecuencia freq [Hz].
        """
        ω  = 2 * np.pi * freq
        Zj = self.Rd(V_bias) / (1 + 1j * ω * self.Rd(V_bias) * self.Cj(V_bias))
        return self.Rs + Zj


class RectifierCircuit:
    """
    Circuito rectificador RF-DC con diodo SMS7630.

    Topologías disponibles
    ----------------------
    'halfwave' : media onda (1 diodo, factor N=1)
    'doubler'  : doblador de voltaje (2 diodos, N=2, recomendado IoT)
    'dickson3' : multiplicador Dickson 3 etapas (6 diodos, N=3, bajo Pin)

    La PCE se calcula por análisis autorreferente de la ecuación de Shockley.
    El voltaje de forward V_f converge iterativamente en ≤80 iteraciones.
    """

    # Eficiencia por topología (pérdidas Rs en etapas adicionales)
    _STAGE_EFF = {'halfwave': 1.00, 'doubler': 0.90, 'dickson3': 0.80}
    _N_STAGES  = {'halfwave': 1,    'doubler': 2,     'dickson3': 3}

    def __init__(self, topology: str = 'doubler', R_load: float = 1300.0):
        """
        Parámetros
        ----------
        topology : 'halfwave', 'doubler', o 'dickson3'
        R_load   : resistencia de carga equivalente [Ω] (BQ25504 input ≈ 1300 Ω)
        """
        valid = list(self._N_STAGES)
        if topology not in valid:
            raise ValueError(f'Topología desconocida: {topology!r}. Opciones: {valid}')
        self.topology = topology
        self.R_load   = R_load
        self.diode    = SchottkyDiode_SMS7630()

    # ── Cálculo de PCE ────────────────────────────────────────────────────────

    def PCE(self, Pin_dBm: float, freq: float = 2.45e9,
            IL_dB: float = 0.0, gamma: float = 0.0) -> float:
        """
        Eficiencia de conversión RF-DC η_rect [0..1].

        Flujo de cálculo:
            P_avail → (corrección IMN: IL + gamma) → V_oc_pk → Shockley → PCE.

        Parámetros
        ----------
        Pin_dBm : potencia de entrada [dBm]
        freq    : frecuencia de operación [Hz]
        IL_dB   : pérdida de inserción de la red de adaptación [dB]
        gamma   : coeficiente de reflexión en la entrada de la IMN [0..1]

        Notas
        -----
        Sin IMN (IL_dB=0, gamma=0) asume adaptación perfecta (best-case).
        PCE clipeado en [0, 0.85] — límite físico para SMS7630.

        Raises
        ------
        ValueError : si freq ≤ 0, gamma fuera de [0,1], o IL_dB < 0.
        """
        # Validación de rango físico
        if freq <= 0:
            raise ValueError(f'Frecuencia debe ser > 0 Hz, recibido: {freq}')
        if not (0.0 <= gamma <= 1.0):
            raise ValueError(f'gamma debe estar en [0, 1], recibido: {gamma}')
        if IL_dB < 0:
            raise ValueError(f'IL_dB debe ser ≥ 0 dB, recibido: {IL_dB}')
        if Pin_dBm > 40.0:
            import warnings
            warnings.warn(f'Pin_dBm={Pin_dBm} dBm excede 10 W — fuera del rango '
                          f'operativo del SMS7630. Resultados no confiables.')

        d     = self.diode
        Pin_W = 10.0 ** ((Pin_dBm - 30.0) / 10.0)
        if Pin_W < 1e-15:
            return 0.0

        # Potencia disponible tras la IMN
        eta_match = (1.0 - gamma ** 2) * 10.0 ** (-IL_dB / 10.0)
        P_avail   = Pin_W * eta_match

        # Resistencia dinámica del diodo a V=0 (Rd0 = n·Vt/Is)
        ω       = 2.0 * np.pi * freq
        Rd0     = d.n * d.Vt / d.Is          # ≈ 5460 Ω para SMS7630
        Cj_val  = d.Cj(0.0)
        Re_Zd   = d.Rs + Rd0 / (1.0 + (ω * Rd0 * Cj_val) ** 2)

        # Amplitud RF circuito abierto: V_oc_pk = √(8·P·Re_Zd)
        Vrf_pk = np.sqrt(8.0 * P_avail * max(Re_Zd, d.Rs))

        N        = self._N_STAGES[self.topology]
        eta_topo = self._STAGE_EFF[self.topology]

        # ── Análisis autorreferente (Shockley) ────────────────────────────────
        V_f = d.n * d.Vt   # voltaje inicial de arranque
        for _ in range(80):
            V_dc = N * (Vrf_pk - V_f)
            if V_dc <= 0.0:
                V_dc = 0.0
                break
            I_dc    = V_dc / self.R_load
            I_diode = max(I_dc, d.Is)
            V_f_new = d.n * d.Vt * np.log(I_diode / d.Is + 1.0)
            V_f_new = min(V_f_new, Vrf_pk * 0.99)   # evitar V_dc negativo
            if abs(V_f_new - V_f) < 1e-10:
                V_f = V_f_new
                break
            V_f = 0.4 * V_f + 0.6 * V_f_new          # convergencia amortiguada

        V_dc = max(N * (Vrf_pk - V_f), 0.0)
        I_dc = V_dc / self.R_load

        # Potencia DC neta (menos pérdidas óhmicas en Rs de los N diodos)
        P_dc_gross = V_dc ** 2 / self.R_load
        P_rs       = N * I_dc ** 2 * d.Rs
        P_dc_net   = max(P_dc_gross - P_rs, 0.0) * eta_topo

        return float(np.clip(P_dc_net / Pin_W, 0.0, 0.85))

    def output_voltage(self, Pin_dBm: float, freq: float = 2.45e9,
                       IL_dB: float = 0.0, gamma: float = 0.0) -> float:
        """
        Voltaje DC de salida [V].
        V_dc = √(PCE · Pin_W · R_load).
        """
        Pin_W = 10.0 ** ((Pin_dBm - 30.0) / 10.0)
        return float(np.sqrt(max(
            self.PCE(Pin_dBm, freq, IL_dB, gamma) * Pin_W * self.R_load, 0.0
        )))

    def output_power_uw(self, Pin_dBm: float, freq: float = 2.45e9,
                        IL_dB: float = 0.0, gamma: float = 0.0) -> float:
        """Potencia DC de salida [µW]."""
        Pin_W = 10.0 ** ((Pin_dBm - 30.0) / 10.0)
        return float(max(self.PCE(Pin_dBm, freq, IL_dB, gamma) * Pin_W * 1e6, 0.0))

    def output_power_dBm(self, Pin_dBm: float, freq: float = 2.45e9,
                         IL_dB: float = 0.0, gamma: float = 0.0) -> float:
        """
        Potencia DC de salida [dBm].
        Retorna -100 dBm si PCE = 0 (sin cosecha útil).
        """
        pce   = self.PCE(Pin_dBm, freq, IL_dB, gamma)
        Pin_W = 10.0 ** ((Pin_dBm - 30.0) / 10.0)
        Pout_W = pce * Pin_W
        if Pout_W < 1e-15:
            return -100.0
        return float(10.0 * np.log10(Pout_W * 1e3))

    # ── Resumen ───────────────────────────────────────────────────────────────

    def summary(self) -> str:
        """Resumen de configuración del rectificador."""
        d = self.diode
        lines = [
            f'RectifierCircuit — {self.topology} (N={self._N_STAGES[self.topology]} etapas)',
            f'  Diodo    : SMS7630  Is={d.Is*1e6:.1f}µA  n={d.n}  Rs={d.Rs}Ω',
            f'             Cj0={d.Cj0*1e12:.2f}pF  Vj={d.Vj}V  Vt={d.Vt*1e3:.2f}mV',
            f'  R_load   : {self.R_load:.0f} Ω',
            f'  η_etapa  : {self._STAGE_EFF[self.topology]*100:.0f}%',
            f'  PCE_max  : 85% (límite físico clipeado)',
        ]
        return '\n'.join(lines)
