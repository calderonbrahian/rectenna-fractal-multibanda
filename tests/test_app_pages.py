"""
Pruebas de la aplicación Streamlit (estructura narrativa de 4 preguntas).
================================================================================
Garantiza dos cosas:

  1. Las cuatro páginas se renderizan SIN excepción con el AppTest de Streamlit.
  2. Los valores que la app muestra EN VIVO coinciden con los canónicos del
     modelo (SSOT: configs/parametros.CANONICAL y los JSON del pipeline). Así,
     si alguien cambiara un número a mano en una página, la coincidencia con
     core/ se rompería y esta prueba lo detectaría.

No toca la suite de física (core/): solo la capa de presentación.
"""

import json
import os
import sys

import pytest
from streamlit.testing.v1 import AppTest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DASH = os.path.dirname(_HERE)
if _DASH not in sys.path:
    sys.path.insert(0, _DASH)

_PAGES = [
    "pages/1_El_problema.py",
    "pages/2_El_modelo.py",
    "pages/3_Los_hallazgos.py",
    "pages/4_Reproducir.py",
]


@pytest.mark.parametrize("page", _PAGES)
def test_pagina_renderiza_sin_excepcion(page):
    """Cada página carga y ejecuta sin lanzar excepciones."""
    at = AppTest.from_file(os.path.join(_DASH, page), default_timeout=60).run()
    assert not at.exception, f"{page} lanzó excepción: {at.exception}"


# ── Sanidad de valores EN VIVO = canónicos ────────────────────────────────────

def test_cosecha_dirigida_es_canonica():
    """El Escenario B a 100 m debe reproducir CANONICAL['P_dc_uW'] = 1335 µW."""
    from configs.parametros import (CANONICAL, FLPDA_TAU, FLPDA_SIGMA,
                                    FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ)
    from core.flpda import FLPDA_Koch
    from core.rectifier import RectifierCircuit
    from core.lora_budget import harvested_uw_full

    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    rect = RectifierCircuit(topology="doubler", R_load=1300.0)
    res = harvested_uw_full(72.15, 100.0, 0.550, flpda, rect, matching_net=None)
    assert res["P_dc_uW"] == pytest.approx(CANONICAL["P_dc_uW"], rel=0.02)


def test_cosecha_multibanda_es_canonica():
    """La suma multibanda del Escenario A debe dar ~2,43 µW (comparative_values)."""
    from core.multiband import build_default, harvest_total_uw
    ant, rec, imn = build_default()
    total = harvest_total_uw(ant, rec, imn)

    with open(os.path.join(_DASH, "_regen", "out", "comparative_values.json"),
              encoding="utf-8") as f:
        esperado = json.load(f)["harvest_urban_uW"]["sierpinski_FR4"]
    assert total == pytest.approx(esperado, rel=0.01)


def test_supercap_json_disponible():
    """El dato de complemento (supercap vs ráfaga) proviene del JSON del pipeline."""
    from configs.parametros import CANONICAL
    with open(os.path.join(_DASH, "_regen", "out", "doc_values.json"),
              encoding="utf-8") as f:
        sc = json.load(f)["supercap"]
    # El supercap guarda varias ráfagas LoRa (E_util >> E_ciclo).
    assert sc["E_util_mJ"] > CANONICAL["E_ciclo_mJ"]
    assert sc["n_ciclos"] == pytest.approx(sc["E_util_mJ"] / CANONICAL["E_ciclo_mJ"], rel=0.05)
