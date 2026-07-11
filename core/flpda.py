"""
================================================================================
MÓDULO: FLPDA Koch — Escenario B
================================================================================
Antena Log-Periódica de Dipolos Fractal (Koch it.2), 470–900 MHz.
Diseñada para cosechar energía de fuentes UHF (TV DVB-T, LTE 700 MHz)
y alimentar un nodo LoRa sin batería.

La geometría Koch reduce la longitud física de cada dipolo ~43.75%
(iteración 2: k_red = (3/4)^2 = 0.5625) manteniendo la longitud eléctrica
equivalente a λ/2.

Referencias:
    Carrel (1961) "Analysis and Design of the Log-Periodic Dipole Antenna,"
        IRE Trans. on Antennas and Propagation — formulación del diseño LPDA.
    Miniaturización Koch: reducción (3/4)^n por iteración.

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import numpy as np


class FLPDA_Koch:
    """
    Antena Log-Periódica de Dipolos Fractal (FLPDA) con elementos Koch it.2.

    Escenario B: banda 470–900 MHz (UHF), sustrato FR-4.
    Diseño según Carrel (1961) con miniaturización Koch.

    Parámetros de diseño:
        tau   ∈ (0.80, 0.95) — razón de escala log-periódica entre elementos
        sigma ∈ (0.10, 0.20) — espaciado relativo entre elementos

    Atributos calculados
    --------------------
    n_elements       : número de dipolos
    lengths_elec     : longitudes eléctricas [m]
    lengths_phys     : longitudes físicas con reducción Koch [m]
    positions        : posiciones sobre el boom [m]
    resonant_freqs   : frecuencia de resonancia de cada dipolo [Hz]
    k_red            : factor de reducción física Koch = (3/4)^iter
    """

    # Reducción longitud física por iteración Koch: (3/4)^n
    _KOCH_REDUCTION = {0: 1.0, 1: 0.75, 2: 0.5625, 3: 0.421875}

    def __init__(self,
                 tau:       float = 0.90,
                 sigma:     float = 0.15,
                 f_low:     float = 470e6,
                 f_high:    float = 900e6,
                 koch_iter: int   = 2,
                 er:        float = 4.4):
        """
        Parámetros
        ----------
        tau       : razón de escala log-periódica (Carrel 1961)
        sigma     : espaciado relativo entre elementos
        f_low     : frecuencia mínima de la banda [Hz]
        f_high    : frecuencia máxima de la banda [Hz]
        koch_iter : iteraciones de la curva de Koch (0–3)
        er        : permitividad relativa del sustrato (FR-4=4.4)
        """
        self.tau       = tau
        self.sigma     = sigma
        self.f_low     = f_low
        self.f_high    = f_high
        self.koch_iter = min(int(koch_iter), 3)
        self.er        = er
        self.c0        = 3e8
        self.loss_tan  = 0.02   # tan δ FR-4

        self.k_red = self._KOCH_REDUCTION[self.koch_iter]
        self._design()

    # ── Diseño de la red de dipolos ───────────────────────────────────────────

    def _design(self):
        """
        Diseña la red de dipolos según Carrel (1961), incluyendo el ancho de
        banda de la región activa.

        El ancho de banda de diseño B_s no es solo la razón f_high/f_low: la
        región activa (los dipolos que radian a cada frecuencia) exige un margen
        adicional B_ar para que la antena no colapse en los extremos de banda:

            cot(α) = 4·σ / (1 − τ)
            B_ar   = 1.1 + 7.7·(1 − τ)²·cot(α)      (Carrel 1961)
            B_s    = (f_high / f_low) · B_ar
            N      = 1 + ceil( ln(B_s) / ln(1/τ) )

        Con τ=0.90, σ=0.15 esto da B_ar≈1.56 y N≈12 (antes 8 sin el margen),
        lo que asegura adaptación en 470 y 900 MHz.
        """
        f1 = self.f_low
        f2 = self.f_high

        cot_alpha = 4.0 * self.sigma / (1.0 - self.tau)
        self.B_ar = 1.1 + 7.7 * (1.0 - self.tau) ** 2 * cot_alpha
        self.B_s  = (f2 / f1) * self.B_ar

        self.n_elements = max(
            int(np.ceil(1 + np.log(self.B_s) / np.log(1 / self.tau))), 4
        )

        # Dipolo más largo: λ/2 a f1 (longitud eléctrica) reducida por Koch
        lam1              = self.c0 / f1
        self.L_max_elec   = lam1 / 2
        self.L_max_phys   = self.L_max_elec * self.k_red

        # Longitudes de todos los elementos
        self.lengths_elec = np.array([
            self.L_max_elec * self.tau ** i for i in range(self.n_elements)
        ])
        self.lengths_phys = self.lengths_elec * self.k_red

        # Espaciados y posiciones sobre el boom
        self.spacings = 2 * self.sigma * self.lengths_elec[:-1]
        pos = np.zeros(self.n_elements)
        for i in range(1, self.n_elements):
            pos[i] = pos[i-1] + self.spacings[i-1]
        self.positions = pos

        # Frecuencias de resonancia de cada elemento (λ/2)
        self.resonant_freqs = self.c0 / (2 * self.lengths_elec)

    # ── Modelos electromagnéticos ─────────────────────────────────────────────

    def S11_dB(self, freq):
        """
        Coeficiente de reflexión S11 [dB] basado en impedancia de dipolo activo.

        Modelo: calcula Γ = (Z_in − Z0) / (Z_in + Z0) desde la impedancia
        de entrada. La región activa del LPDA define cuál dipolo domina
        a cada frecuencia.  Dentro de banda, el dipolo resonante mantiene
        S11 ≈ −12 a −18 dB; fuera de banda, la impedancia diverge y
        S11 → 0 dB (reflexión total).

        Referencia: Carrel (1961), ecuación de impedancia de dipolos.
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        Za   = np.atleast_1d(self.impedance(freq))
        Z0   = 50.0
        gamma = (Za - Z0) / (Za + Z0)
        s11   = 20.0 * np.log10(np.maximum(np.abs(gamma), 1e-6))
        return s11 if len(s11) > 1 else float(s11[0])

    def gain_dBi(self, freq):
        """
        Ganancia realizada [dBi] — incluye η_rad.

        LPDA clásica: 7–9 dBi directiva en banda (Carrel 1961).
        G_realized = G_directiva + 10·log10(η_rad).
        G0 = 7.5 + corrección por número de elementos.

        Fuera de banda retorna 0 dBi (no hay elemento activo).
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        g    = np.zeros(len(freq))
        G0   = 7.5 + 0.5 * np.log10(self.n_elements / 8)
        for i, f in enumerate(freq):
            if self.f_low <= f <= self.f_high:
                phase  = np.pi * np.log(f / self.f_low) / np.log(self.f_high / self.f_low)
                g_dir  = G0 - 0.5 * abs(np.sin(3 * phase))
                g[i]   = g_dir + 10.0 * np.log10(max(self.eta_rad(f), 1e-6))
        return g if len(g) > 1 else float(g[0])

    def directivity_dBi(self, freq):
        """
        Ganancia directiva [dBi] — sin pérdidas (útil para comparar con Carrel).
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        g    = np.zeros(len(freq))
        G0   = 7.5 + 0.5 * np.log10(self.n_elements / 8)
        for i, f in enumerate(freq):
            if self.f_low <= f <= self.f_high:
                phase  = np.pi * np.log(f / self.f_low) / np.log(self.f_high / self.f_low)
                g[i]   = G0 - 0.5 * abs(np.sin(3 * phase))
        return g if len(g) > 1 else float(g[0])

    def impedance(self, freq):
        """
        Impedancia de entrada compleja [Ω] — modelo de región activa LPDA.

        Cada dipolo se modela como resonador RLC serie con:
            R_dip ≈ 73 Ω (resistencia de radiación de medio dipolo λ/2)
            L_dip = R_dip·Q / ω_res       Q ≈ 4.5 (LPDA, FR-4)
            C_dip = 1/(ω_res²·L_dip)

        La alimentación por línea de transmisión (boom) hace que los
        dipolos aparezcan en paralelo con fase alternante (Carrel 1961).
        Solo el dipolo activo (más cercano en frecuencia) domina, y sus
        vecinos contribuyen con reactancia.

        Fuera de banda: Z → alta impedancia (circuito abierto).
        """
        freq = np.atleast_1d(np.asarray(freq, dtype=float))
        Z    = np.zeros(len(freq), dtype=complex)

        R_dip = 73.0   # resistencia de radiación λ/2 dipolo [Ω]
        Q_dip = 4.5     # factor de calidad efectivo en LPDA FR-4

        for i, f in enumerate(freq):
            omega = 2.0 * np.pi * f

            # Contribución de cada dipolo como rama RLC paralela
            Y_total = 0j
            for k, f_res in enumerate(self.resonant_freqs):
                omega_res = 2.0 * np.pi * f_res
                # Modelo RLC serie del dipolo k
                Rk = R_dip * (0.97 ** k)   # ligera reducción en dipolos cortos
                Lk = Rk * Q_dip / omega_res
                Ck = 1.0 / (omega_res ** 2 * Lk)
                Zk = Rk + 1j * (omega * Lk - 1.0 / (omega * Ck))

                # Peso por proximidad en frecuencia (el dipolo activo domina)
                delta = abs(f - f_res) / f_res
                weight = 1.0 / (1.0 + (delta * 8.0) ** 2)

                Y_total += weight / Zk

            if abs(Y_total) > 1e-15:
                Z[i] = 1.0 / Y_total
            else:
                Z[i] = complex(1e6, 0.0)  # fuera de banda: circuito abierto

        return Z if len(Z) > 1 else Z[0]

    def eta_rad(self, freq: float) -> float:
        """
        Eficiencia de radiación η_rad [0–1] — modelo realista para FR-4.

        η_rad = 1 / (1 + L_diel + L_cond), con las pérdidas expresadas como
        cociente pérdida/radiación:
            L_diel = tan δ · k_d · (0.5 + f[GHz])   (dieléctrico, domina en FR-4)
            L_cond = k_c · √(f[GHz])                 (conductor, efecto pelicular)
        Calibrado a η_rad ≈ 0.60 @ 550 MHz, dentro del rango típico de antenas
        impresas sobre FR-4 en UHF (0.50–0.70). El valor decae con la frecuencia
        por el aumento de las pérdidas dieléctricas y de conductor.

        NOTA (revisión de modelo, 2026-07): sustituye el modelo previo, que
        subestimaba las pérdidas (η≈0.99), físicamente inconsistente con tan δ=0.02.
        """
        fghz = float(np.asarray(freq, dtype=float).ravel()[0]) / 1e9
        L_diel = self.loss_tan * 30.0 * (0.5 + fghz)
        L_cond = 0.06 * fghz ** 0.5
        eta = 1.0 / (1.0 + L_diel + L_cond)
        return float(np.clip(eta, 0.30, 0.85))

    def radiation_pattern_dB(self, freq: float, theta_deg):
        """
        Patrón normalizado [dB] en el plano E — endfire (LPDA).
        Patrón tipo cardioid con componente endfire dominante.
        """
        theta = np.radians(np.asarray(theta_deg, dtype=float))
        p     = np.abs(np.cos(theta)) ** 2 * (1 + 0.5 * np.abs(np.sin(theta)))
        p     = p / np.max(p)
        return 10 * np.log10(p + 1e-10)

    # ── Propiedades de la geometría física ────────────────────────────────────

    @property
    def boom_length_m(self) -> float:
        """Longitud total del boom [m]."""
        return float(np.sum(self.spacings))

    @property
    def max_element_length_m(self) -> float:
        """Longitud física máxima del dipolo (reducida por Koch) [m]."""
        return float(self.lengths_phys[0])

    # ── Resumen ───────────────────────────────────────────────────────────────

    def summary(self) -> str:
        """Resumen de diseño en texto."""
        reduccion_pct = (1 - self.k_red) * 100
        lines = [
            f'FLPDA Koch it.{self.koch_iter} — Escenario B',
            f'  Rango       : {self.f_low/1e6:.0f}–{self.f_high/1e6:.0f} MHz',
            f'  Elementos   : {self.n_elements}',
            f'  tau={self.tau:.3f}  sigma={self.sigma:.3f}',
            f'  Boom        : {self.boom_length_m*100:.1f} cm',
            f'  L_máx físico: {self.max_element_length_m*100:.1f} cm'
            f'  (reducción Koch it.{self.koch_iter}: {reduccion_pct:.1f}%)',
            f'  k_red       : (3/4)^{self.koch_iter} = {self.k_red:.4f}',
        ]
        return '\n'.join(lines)

    def table_elements(self) -> str:
        """Tabla de geometría de dipolos en formato de texto."""
        hdr = (f'  {"#":>3s}  {"f_res(MHz)":>10s}  {"L_elec(mm)":>10s}'
               f'  {"L_phys(mm)":>10s}  {"Pos(mm)":>8s}')
        sep = '  ' + '-' * 50
        rows = [hdr, sep]
        for i in range(self.n_elements):
            rows.append(
                f'  {i+1:>3d}  {self.resonant_freqs[i]/1e6:>10.1f}'
                f'  {self.lengths_elec[i]*1000:>10.1f}'
                f'  {self.lengths_phys[i]*1000:>10.1f}'
                f'  {self.positions[i]*1000:>8.1f}'
            )
        rows.append(sep)
        return '\n'.join(rows)
