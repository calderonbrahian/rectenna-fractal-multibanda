# -*- coding: utf-8 -*-
"""
================================================================================
TESTS — Eficiencia RF->DC de cadena completa por antena y escenario
================================================================================
Verifica consistencia física del JSON generado por
_regen/derive_efficiency_values.py (_regen/out/efficiency_values.json):
    - eta_cadena y eta_total en (0,1) para las 3 antenas en todos sus escenarios
    - eta_total <= eta_cadena siempre (conjugada: iguales; modular: eta_rad < 1)
    - AUTO-MULTIPLICABILIDAD (corrección K1): en TODOS los escenarios, la potencia
      de referencia × su eficiencia reproduce el P_dc reportado
        · conjugada (Sierpinski/parche): P_dc = P_in · eta_total
        · modular (FLPDA): P_dc = P_incidente · eta_total = P_in · eta_cadena
    - Parche: WiFi cercano entrega más P_dc que el ambiente difuso; Sierpinski:
      el enlace fuerte 3,30 GHz supera el aporte de esa banda en el agregado
    - Regresión exacta: FLPDA @ TDT 100 m reproduce el caso canónico del documento
    - Estructura completa de escenarios/claves presente (incl. P_incidente_uW FLPDA)

Ejecutar:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m pytest tests/test_efficiency_values.py -v
================================================================================
"""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from configs.parametros import CANONICAL

JSON_PATH = os.path.join(ROOT, "_regen", "out", "efficiency_values.json")

COMMON_KEYS = {
    'PCE', 'eta_pmic', 'eta_cadena', 'eta_total',
    'P_in_dBm', 'P_in_uW', 'P_dc_uW', 'descripcion',
}
# Sierpinski/parche: co-diseño conjugado integrado, sin interfaz de 50 Ω
# (eta_cm sustituye a eta_mm/eta_imn; ver decisión de modelado 1 en
# _regen/derive_efficiency_values.py). FLPDA: arquitectura modular de 50 Ω
# ya establecida (eta_mm/eta_imn separados, como en CANONICAL).
REQUIRED_KEYS_CONJUGADO = COMMON_KEYS | {'eta_cm'}
# FLPDA (modular de 50 Ω): además de los 5 factores, expone P_incidente_uW
# (= P_in/eta_rad) para que la terna sea auto-multiplicable (corrección K1:
# eta_total multiplica sobre P_incidente; eta_cadena sobre P_in de puerto).
REQUIRED_KEYS_MODULAR = COMMON_KEYS | {'eta_rad', 'eta_mm', 'eta_imn', 'P_incidente_uW'}

EXPECTED_SCENARIOS = {
    # Sierpinski: el escenario fuerte pasó de "WiFi 2,45 GHz" (anti-resonancia,
    # fuera del dominio de validez del acople) a un emisor intencional EN BANDA
    # a 3,30 GHz — renombrado 'fuente_fuerte_cercana' (corrección K1 #2).
    'sierpinski': {'ambiente_urbano_difuso', 'fuente_fuerte_cercana'},
    # Parche: conserva su escenario WiFi 2,45 GHz (es su banda de diseño f0).
    'parche_FR4': {'ambiente_urbano_difuso', 'fuente_fuerte_wifi'},
    'flpda': {'fuente_cercana_100m', 'fuente_lejana_1000m', 'tdt_100m_canonico'},
}


@pytest.fixture(scope="module", autouse=True)
def _regenerate_efficiency_values():
    """Regenera _regen/out/efficiency_values.json antes de correr los tests,
    para que la suite no dependa de un artefacto stale en disco."""
    script = os.path.join(ROOT, "_regen", "derive_efficiency_values.py")
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run([sys.executable, script], cwd=ROOT, env=env,
                            capture_output=True, text=True)
    assert result.returncode == 0, (
        f"derive_efficiency_values.py fallo:\nSTDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}")
    yield


@pytest.fixture(scope="module")
def data():
    with open(JSON_PATH, encoding="utf-8") as fh:
        return json.load(fh)


class TestEstructura:
    def test_json_existe_y_tiene_las_3_antenas(self, data):
        assert set(data.keys()) == set(EXPECTED_SCENARIOS.keys())

    def test_escenarios_por_antena_completos(self, data):
        for antena, escenarios in EXPECTED_SCENARIOS.items():
            assert set(data[antena].keys()) == escenarios, (
                f"{antena}: escenarios esperados {escenarios}, "
                f"encontrados {set(data[antena].keys())}")

    def test_todas_las_claves_presentes(self, data):
        for antena, escenarios in data.items():
            requeridas = (REQUIRED_KEYS_MODULAR if antena == 'flpda'
                         else REQUIRED_KEYS_CONJUGADO)
            for nombre, d in escenarios.items():
                faltantes = requeridas - set(d.keys())
                assert not faltantes, (
                    f"{antena}/{nombre}: faltan claves {faltantes}")


class TestRangoFisico:
    def test_eta_cadena_y_eta_total_en_0_1(self, data):
        for antena, escenarios in data.items():
            for nombre, d in escenarios.items():
                assert 0.0 < d['eta_cadena'] < 1.0, (
                    f"{antena}/{nombre}: eta_cadena={d['eta_cadena']} fuera de (0,1)")
                assert 0.0 < d['eta_total'] < 1.0, (
                    f"{antena}/{nombre}: eta_total={d['eta_total']} fuera de (0,1)")

    def test_eta_total_menor_o_igual_que_eta_cadena(self, data):
        """eta_total = eta_rad * eta_cadena, con eta_rad < 1 siempre."""
        for antena, escenarios in data.items():
            for nombre, d in escenarios.items():
                assert d['eta_total'] <= d['eta_cadena'] + 1e-9, (
                    f"{antena}/{nombre}: eta_total={d['eta_total']} > "
                    f"eta_cadena={d['eta_cadena']}")


class TestEscenarioFuerteVsDebil:
    def test_sierpinski_fuerte_en_banda_supera_su_aporte_ambiente(self, data):
        """Sierpinski: el escenario fuerte es un enlace de UNA banda (3,30 GHz),
        mientras que el ambiente es una cosecha AGREGADA de 7 bandas. Comparar el
        P_dc total no es apples-to-apples: el agregado de 7 bandas (2,43 µW) puede
        superar al enlace único (0,99 µW) aunque este sea "fuerte". La comparación
        físicamente honesta es POR BANDA: el enlace fuerte a 3,30 GHz debe entregar
        más P_dc que la contribución de ESA MISMA banda (5G_3.5, 3,30 GHz) dentro
        del agregado ambiente."""
        strong = data['sierpinski']['fuente_fuerte_cercana']['P_dc_uW']
        bandas = data['sierpinski']['ambiente_urbano_difuso']['bandas']
        aporte_3_3 = next(b['P_dc_uW'] for b in bandas if abs(b['f_GHz'] - 3.30) < 1e-6)
        assert strong > aporte_3_3, (
            f"Enlace fuerte 3,30 GHz ({strong} uW) deberia superar el aporte de "
            f"esa banda en el ambiente ({aporte_3_3} uW)")

    def test_wifi_cercano_mas_potencia_que_ambiente_parche(self, data):
        amb = data['parche_FR4']['ambiente_urbano_difuso']['P_dc_uW']
        wifi = data['parche_FR4']['fuente_fuerte_wifi']['P_dc_uW']
        assert wifi > amb, (
            f"WiFi cercano ({wifi} uW) deberia superar al ambiente difuso "
            f"({amb} uW) para el parche")

    def test_flpda_cercano_mas_potencia_que_lejano(self, data):
        cerca = data['flpda']['fuente_cercana_100m']['P_dc_uW']
        lejos = data['flpda']['fuente_lejana_1000m']['P_dc_uW']
        assert cerca > lejos


class TestAutoMultiplicabilidad:
    """Corrección K1 — la terna (potencia de referencia, eficiencia, P_dc) debe
    ser auto-multiplicable en TODOS los escenarios: multiplicar la potencia de
    referencia por su eficiencia reproduce el P_dc reportado. Bloquea el doble
    conteo de eta_cm (conjugada) y la mezcla P_in×eta_total (modular FLPDA)."""

    REL_TOL = 1e-3   # residuo relativo admisible (redondeo de factores CANÓNICOS)

    def _close(self, a, b):
        return abs(a - b) <= self.REL_TOL * max(abs(b), 1e-9) + 1e-9

    def test_conjugado_P_dc_igual_P_in_por_eta_total(self, data):
        """Sierpinski y parche (co-diseño conjugado): P_dc = P_in · eta_total,
        con P_in en el puerto de antena (eta_total = eta_cadena = pce·eta_pmic,
        SIN el doble conteo de eta_cm de la primera versión)."""
        for antena in ('sierpinski', 'parche_FR4'):
            for nombre, d in data[antena].items():
                pred = d['P_in_uW'] * d['eta_total']
                assert self._close(pred, d['P_dc_uW']), (
                    f"{antena}/{nombre}: P_in·eta_total={pred} != "
                    f"P_dc={d['P_dc_uW']}")

    def test_flpda_P_dc_igual_P_incidente_por_eta_total(self, data):
        """FLPDA (modular): eta_total (5 factores) multiplica sobre P_incidente
        = P_in/eta_rad, NO sobre P_in de puerto."""
        for nombre, d in data['flpda'].items():
            pred = d['P_incidente_uW'] * d['eta_total']
            assert self._close(pred, d['P_dc_uW']), (
                f"flpda/{nombre}: P_incidente·eta_total={pred} != "
                f"P_dc={d['P_dc_uW']}")

    def test_flpda_P_dc_igual_P_in_por_eta_cadena(self, data):
        """FLPDA (modular): eta_cadena (4 factores post-antena) multiplica sobre
        P_in de puerto."""
        for nombre, d in data['flpda'].items():
            pred = d['P_in_uW'] * d['eta_cadena']
            assert self._close(pred, d['P_dc_uW']), (
                f"flpda/{nombre}: P_in·eta_cadena={pred} != "
                f"P_dc={d['P_dc_uW']}")

    def test_flpda_P_incidente_coherente_con_eta_rad(self, data):
        """P_incidente = P_in / eta_rad (identidad de definición)."""
        for nombre, d in data['flpda'].items():
            pred = d['P_in_uW'] / d['eta_rad']
            assert self._close(pred, d['P_incidente_uW']), (
                f"flpda/{nombre}: P_in/eta_rad={pred} != "
                f"P_incidente={d['P_incidente_uW']}")

    def test_conjugado_franjas_sankey_reproducen_eta_total(self, data):
        """Co-diseño conjugado: eta_cm · PCE(intrínseca) · eta_pmic == eta_total
        (las franjas del Sankey conjugado multiplican exacto)."""
        for antena in ('sierpinski', 'parche_FR4'):
            for nombre, d in data[antena].items():
                prod = d['eta_cm'] * d['PCE'] * d['eta_pmic']
                assert abs(prod - d['eta_total']) < 1e-9, (
                    f"{antena}/{nombre}: eta_cm·PCE·eta_pmic={prod} != "
                    f"eta_total={d['eta_total']}")


class TestRegresionAgregadaMultibanda:
    """Sierpinski y parche, escenario ambiente urbano difuso, deben reproducir
    EXACTAMENTE la cosecha agregada ya publicada y auditada del documento
    (co-diseño conjugado, core.multiband.harvest_total_uw): 2,43 µW
    Sierpinski, 2,32 µW parche. Bloquea la regresión al modelo modular de
    50 Ω (bug detectado y corregido: la primera versión de este script daba
    ~0,21/0,34 µW usando LMatchNetwork.design())."""

    def test_sierpinski_reproduce_ssot(self, data):
        from core.antenna import FractalAntenna
        from core.rectifier import RectifierCircuit
        from core.matching import LMatchNetwork
        from core import multiband as mb
        ssot = mb.harvest_total_uw(
            FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9),
            RectifierCircuit(topology='doubler', R_load=1300.0),
            LMatchNetwork(Z_src=50.0))
        p_dc = data['sierpinski']['ambiente_urbano_difuso']['P_dc_uW']
        assert abs(p_dc - ssot) < 1e-6
        assert 2.3 < p_dc < 2.5

    def test_parche_reproduce_ssot(self, data):
        from core.patch import MicrostripPatchAntenna
        from core.rectifier import RectifierCircuit
        from core.matching import LMatchNetwork
        from core import multiband as mb
        ssot = mb.harvest_total_uw(
            MicrostripPatchAntenna(2.45e9, 'FR4'),
            RectifierCircuit(topology='doubler', R_load=1300.0),
            LMatchNetwork(Z_src=50.0))
        p_dc = data['parche_FR4']['ambiente_urbano_difuso']['P_dc_uW']
        assert abs(p_dc - ssot) < 1e-6
        assert 2.2 < p_dc < 2.4


class TestRegresionCanonicaFLPDA:
    """FLPDA @ TDT 100 m debe reproducir EXACTAMENTE el caso canónico del
    documento (configs.parametros.CANONICAL)."""

    def test_p_dc_uw_exacto(self, data):
        p_dc = data['flpda']['fuente_cercana_100m']['P_dc_uW']
        assert abs(p_dc - CANONICAL['P_dc_uW']) < 0.05, (
            f"P_dc_uW={p_dc} no reproduce CANONICAL={CANONICAL['P_dc_uW']}")

    def test_eta_total_exacto(self, data):
        eta_total = data['flpda']['fuente_cercana_100m']['eta_total']
        assert abs(eta_total - CANONICAL['eta_total']) < 1e-3, (
            f"eta_total={eta_total} no reproduce "
            f"CANONICAL={CANONICAL['eta_total']}")

    def test_escenario_tdt_100m_canonico_es_identico_a_canonical(self, data):
        d = data['flpda']['tdt_100m_canonico']
        assert abs(d['P_dc_uW'] - CANONICAL['P_dc_uW']) < 1e-6
        assert abs(d['eta_total'] - CANONICAL['eta_total']) < 1e-6

    def test_eta_cadena_67_36_pct(self, data):
        """eta_cadena (4 factores post-antena) reproduce el 67.36% publicado."""
        eta_cadena = data['flpda']['fuente_cercana_100m']['eta_cadena']
        assert abs(eta_cadena - 0.6736) < 0.001
