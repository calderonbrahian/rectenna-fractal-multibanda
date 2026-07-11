"""
================================================================================
TESTS UNITARIOS — Modelos de rectenna fractal multibanda
================================================================================
Verifican consistencia fisica y reproducibilidad de los modelos:
    - Rectificador (PCE vs Wang et al. 2022, convergencia Shockley)
    - Antena Sierpinski (frecuencias de resonancia, ganancia)
    - FLPDA Koch (diseno geometrico, impedancia, ganancia)
    - Presupuesto de enlace (FSPL, cadena completa)
    - Red de adaptacion (IL, VSWR)

Uso:
    python -m pytest tests/test_models.py -v
    python -m pytest tests/test_models.py -v --tb=short

Autor: Brahian Calderon Munera . UdeA . 2026
================================================================================
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from core.rectifier import RectifierCircuit, SchottkyDiode_SMS7630
from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from core.lora_budget import fspl_dB, received_power_dBm, harvested_uw, pce_uhf
from core.matching import LMatchNetwork


# ═══════════════════════════════════════════════════════════════════════════
# RECTIFICADOR
# ═══════════════════════════════════════════════════════════════════════════

class TestSchottkyDiode:
    """Tests del modelo del diodo SMS7630."""

    def setup_method(self):
        self.d = SchottkyDiode_SMS7630()

    def test_parametros_spice(self):
        """Verificar parametros SPICE oficiales."""
        assert self.d.Is == 5e-6, "Is debe ser 5 uA"
        assert self.d.n == 1.05, "n debe ser 1.05"
        assert self.d.Rs == 20.0, "Rs debe ser 20 Ohm"
        assert self.d.Cj0 == 0.14e-12, "Cj0 debe ser 0.14 pF"

    def test_voltaje_termico(self):
        """Vt ~ 25.85 mV a 300 K."""
        assert abs(self.d.Vt - 0.02585) < 0.001

    def test_corriente_shockley_V0(self):
        """Id(0) = 0 A."""
        assert self.d.Id(0.0) == 0.0

    def test_corriente_shockley_positiva(self):
        """Id(0.2V) > 0 y crece exponencialmente."""
        I1 = self.d.Id(0.1)
        I2 = self.d.Id(0.2)
        assert I1 > 0
        assert I2 > I1 * 5  # crecimiento exponencial

    def test_capacitancia_juntura_V0(self):
        """Cj(0) = Cj0."""
        assert self.d.Cj(0.0) == self.d.Cj0

    def test_impedancia_compleja(self):
        """Impedancia tiene parte real > 0 y parte imaginaria."""
        Z = self.d.impedance(2.45e9)
        assert Z.real > 0, "Parte real de Z debe ser > 0"
        assert Z.imag != 0, "Parte imaginaria de Z no debe ser 0"


class TestRectifier:
    """Tests del circuito rectificador."""

    def setup_method(self):
        self.rect = RectifierCircuit('doubler', R_load=1300.0)

    def test_pce_rango_valido(self):
        """PCE debe estar en [0, 0.85] para cualquier entrada."""
        for pin in [-30, -20, -10, 0, 10]:
            pce = self.rect.PCE(pin, 550e6)
            assert 0.0 <= pce <= 0.85, f"PCE fuera de rango para Pin={pin} dBm"

    def test_pce_crece_con_potencia(self):
        """PCE debe crecer monotonicamente con Pin (rango razonable)."""
        pce_prev = 0.0
        for pin in range(-25, 5, 5):
            pce = self.rect.PCE(pin, 550e6)
            assert pce >= pce_prev, f"PCE no crece en Pin={pin} dBm"
            pce_prev = pce

    def test_pce_wang2022_rmse(self):
        """RMSE vs Wang et al. (2022) debe ser < 20 pp."""
        wang_freqs = [1.84e9, 2.04e9, 2.36e9, 2.54e9, 3.30e9, 4.76e9, 5.80e9]
        wang_pce = [44.4, 43.9, 45.4, 43.4, 36.1, 32.4, 28.3]

        errors = []
        for f, pce_ref in zip(wang_freqs, wang_pce):
            pce_sim = self.rect.PCE(-10.0, f) * 100
            errors.append(pce_sim - pce_ref)

        rmse = np.sqrt(np.mean(np.array(errors) ** 2))
        assert rmse < 20.0, f"RMSE={rmse:.2f} pp excede 20 pp"

    def test_topologias_validas(self):
        """Todas las topologias deben funcionar."""
        for topo in ['halfwave', 'doubler', 'dickson3']:
            r = RectifierCircuit(topo)
            pce = r.PCE(-10.0, 2.45e9)
            assert pce >= 0

    def test_topologia_invalida(self):
        """Topologia invalida debe lanzar ValueError."""
        with pytest.raises(ValueError):
            RectifierCircuit('invalida')

    def test_validacion_freq_negativa(self):
        """Frecuencia negativa debe lanzar ValueError."""
        with pytest.raises(ValueError):
            self.rect.PCE(-10.0, -1.0)

    def test_validacion_gamma_fuera_rango(self):
        """gamma > 1 debe lanzar ValueError."""
        with pytest.raises(ValueError):
            self.rect.PCE(-10.0, 550e6, gamma=1.5)

    def test_output_voltage_positivo(self):
        """Voltaje de salida debe ser positivo para Pin razonable."""
        V = self.rect.output_voltage(-10.0, 550e6)
        assert V > 0


# ═══════════════════════════════════════════════════════════════════════════
# ANTENA SIERPINSKI
# ═══════════════════════════════════════════════════════════════════════════

class TestFractalAntenna:
    """Tests de la antena fractal Sierpinski."""

    def setup_method(self):
        self.ant = FractalAntenna('sierpinski', 3, 1.84e9)

    def test_frecuencias_resonancia(self):
        """Sierpinski: f_k = f0 * 2^k para k=0,1,2."""
        expected = [1.84e9, 3.68e9, 7.36e9]
        for fk, fe in zip(self.ant.fractal_resonances_hz, expected):
            assert abs(fk - fe) / fe < 0.001

    def test_dimension_base(self):
        """Dimension base ~ lambda_eff/2 a f0."""
        er0 = self.ant.get_er(1.84e9)
        lam_eff = 3e8 / (1.84e9 * np.sqrt(er0))
        assert abs(self.ant.base_dim - lam_eff/2) < 1e-6

    def test_er_dinamico_limites(self):
        """epsilon_r(1 GHz) = 4.4, epsilon_r(5.8 GHz) = 4.1."""
        assert abs(self.ant.get_er(1e9) - 4.4) < 0.01
        assert abs(self.ant.get_er(5.8e9) - 4.1) < 0.01

    def test_s11_tipo(self):
        """S11 debe ser float para escalar y array para array."""
        s = self.ant.S11_dB(1.84e9)
        assert isinstance(s, float)
        s_arr = self.ant.S11_dB([1.84e9, 2.45e9])
        assert hasattr(s_arr, '__len__')

    def test_ganancia_positiva(self):
        """Ganancia en banda debe ser positiva."""
        g = self.ant.gain_dBi(1.84e9)
        assert g > 0

    def test_eta_rad_rango(self):
        """eta_rad debe estar en [0.5, 1.0]."""
        for f in [1.84e9, 2.45e9, 5.8e9]:
            eta = self.ant.eta_rad(f)
            assert 0.5 <= eta <= 1.0


# ═══════════════════════════════════════════════════════════════════════════
# FLPDA KOCH
# ═══════════════════════════════════════════════════════════════════════════

class TestFLPDA:
    """Tests de la antena FLPDA Koch."""

    def setup_method(self):
        self.flpda = FLPDA_Koch(tau=0.90, sigma=0.15,
                                f_low=470e6, f_high=900e6, koch_iter=2)

    def test_n_elements_minimo(self):
        """Debe tener al menos 4 elementos."""
        assert self.flpda.n_elements >= 4

    def test_k_red_koch2(self):
        """k_red = (3/4)^2 = 0.5625 para iteracion 2."""
        assert abs(self.flpda.k_red - 0.5625) < 1e-6

    def test_longitudes_decrecientes(self):
        """Longitudes deben decrecer monotonicamente."""
        L = self.flpda.lengths_phys
        for i in range(1, len(L)):
            assert L[i] < L[i-1]

    def test_frecuencias_resonancia_en_banda(self):
        """Al menos algunas frecuencias de resonancia deben estar en banda."""
        in_band = [f for f in self.flpda.resonant_freqs
                   if self.flpda.f_low <= f <= self.flpda.f_high]
        assert len(in_band) >= 2

    def test_s11_en_banda(self):
        """S11 en banda debe ser < -5 dB (razonablemente acoplado)."""
        freqs = np.linspace(500e6, 850e6, 10)
        s11 = np.array([float(self.flpda.S11_dB(f)) for f in freqs])
        assert np.mean(s11) < -5.0

    def test_ganancia_realizada_vs_directiva(self):
        """Ganancia realizada <= directividad (siempre)."""
        f = 700e6
        g_real = float(self.flpda.gain_dBi(f))
        g_dir = float(self.flpda.directivity_dBi(f))
        assert g_real <= g_dir + 0.01  # tolerancia numerica

    def test_eta_rad_uhf(self):
        """eta_rad realista en FR-4 a 700 MHz: rango 0.50-0.70 (no ~0.99)."""
        eta = self.flpda.eta_rad(700e6)
        assert 0.50 <= eta <= 0.70

    def test_impedancia_en_banda(self):
        """Parte real de Z_in debe ser > 0 en banda."""
        for f in [500e6, 700e6, 850e6]:
            Z = self.flpda.impedance(f)
            assert Z.real > 0


# ═══════════════════════════════════════════════════════════════════════════
# PRESUPUESTO DE ENLACE
# ═══════════════════════════════════════════════════════════════════════════

class TestLinkBudget:
    """Tests del presupuesto de enlace."""

    def test_fspl_espacio_libre(self):
        """FSPL a 100 m, 550 MHz ~ 47.3 dB (verificacion manual)."""
        lam = 3e8 / (0.55e9)
        fspl_manual = 20 * np.log10(4 * np.pi * 100 / lam)
        fspl_calc = fspl_dB(100, 0.55)
        assert abs(fspl_calc - fspl_manual) < 0.1

    def test_fspl_distancia_cero(self):
        """Distancia 0 debe lanzar ValueError."""
        with pytest.raises(ValueError):
            fspl_dB(0, 0.55)

    def test_pce_uhf_rango(self):
        """pce_uhf debe estar en [0, 0.55]."""
        for pin in [-30, -20, -10, 0, 10]:
            pce = pce_uhf(pin)
            assert 0.0 <= pce <= 0.55 + 0.001

    def test_harvested_positivo_cerca(self):
        """A 100 m de TDT DVB-T debe haber cosecha util."""
        p = harvested_uw(70.0, 100, 0.55, 7.5)
        assert p > 0

    def test_harvested_cero_lejos(self):
        """A 10 km de LoRa (27 dBm) no hay cosecha util."""
        p = harvested_uw(27.0, 10000, 0.915, 7.5)
        assert p == 0.0

    def test_received_power_decrece_distancia(self):
        """Potencia recibida decrece con distancia."""
        p1 = received_power_dBm(70.0, 100, 0.55)
        p2 = received_power_dBm(70.0, 200, 0.55)
        assert p2 < p1


# ═══════════════════════════════════════════════════════════════════════════
# RED DE ADAPTACION
# ═══════════════════════════════════════════════════════════════════════════

class TestMatchingNetwork:
    """Tests de la red L de adaptacion."""

    def setup_method(self):
        self.net = LMatchNetwork(Z_src=50.0)

    def test_design_produce_resultado(self):
        """Diseno debe retornar LMatchResult."""
        res = self.net.design(550e6, Z_load=complex(73, -20))
        assert res.L > 0
        assert res.C > 0
        assert res.insertion_loss_dB >= 0
        assert res.VSWR >= 1.0

    def test_il_razonable(self):
        """IL debe ser < 8 dB para carga del diodo (altamente capacitiva)."""
        d = SchottkyDiode_SMS7630()
        Zd = d.impedance(550e6)
        res = self.net.design(550e6, Z_load=Zd)
        assert res.insertion_loss_dB < 8.0

    def test_vswr_razonable(self):
        """VSWR debe ser < 5 para carga razonable."""
        res = self.net.design(550e6, Z_load=complex(73, 0))
        assert res.VSWR < 5.0


# ═══════════════════════════════════════════════════════════════════════════
# VERIFICACION DIMENSIONAL
# ═══════════════════════════════════════════════════════════════════════════

class TestDimensionalConsistency:
    """Verificacion de consistencia dimensional entre modulos."""

    def test_pdc_cadena_positivo(self):
        """La cadena completa debe producir P_DC > 0 a 100 m de TDT."""
        from core.lora_budget import harvested_uw_full
        flpda = FLPDA_Koch(tau=0.90, sigma=0.15, f_low=470e6,
                           f_high=900e6, koch_iter=2)
        rect = RectifierCircuit('doubler', R_load=1300.0)
        result = harvested_uw_full(70.0, 100, 0.55, flpda, rect)
        assert result['P_dc_uW'] > 0
        assert result['eta_total'] > 0
        assert result['eta_total'] < 1.0

    def test_eta_total_producto(self):
        """eta_total = producto de todos los eslabones."""
        from core.lora_budget import harvested_uw_full
        flpda = FLPDA_Koch(tau=0.90, sigma=0.15, f_low=470e6,
                           f_high=900e6, koch_iter=2)
        rect = RectifierCircuit('doubler', R_load=1300.0)
        r = harvested_uw_full(70.0, 100, 0.55, flpda, rect)
        eta_manual = r['eta_rad'] * r['eta_mm'] * r['eta_imn'] * r['PCE'] * r['eta_pmic']
        assert abs(r['eta_total'] - eta_manual) < 0.001

    def test_unidades_potencia(self):
        """P_rf_uW y P_dc_uW deben estar en microvatios."""
        from core.lora_budget import harvested_uw_full
        flpda = FLPDA_Koch(tau=0.90, sigma=0.15, f_low=470e6,
                           f_high=900e6, koch_iter=2)
        rect = RectifierCircuit('doubler', R_load=1300.0)
        r = harvested_uw_full(70.0, 100, 0.55, flpda, rect)
        # A 100 m de TDT 10 kW, P_rf debe ser del orden de mW (miles de uW)
        assert 10 < r['P_rf_uW'] < 1e6
        # P_dc < P_rf siempre
        assert r['P_dc_uW'] < r['P_rf_uW']


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
