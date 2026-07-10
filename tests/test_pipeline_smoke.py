"""
Smoke test del pipeline de figuras conceptuales/metodológicas (C1–C5).
================================================================================
Garantiza que el material gráfico del documento (figuras conceptuales) se
regenera sin error desde el pipeline. Cierra la brecha de cobertura de los
artefactos nuevos: si un generador se rompe, la reproducibilidad del documento
deja de estar garantizada y esta prueba lo detecta.
"""

import os
import sys
import importlib

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_DASH = os.path.dirname(_HERE)
_REGEN = os.path.join(_DASH, "_regen")
for _p in (_DASH, _REGEN):
    if _p not in sys.path:
        sys.path.insert(0, _p)

fc = importlib.import_module("figuras_conceptuales")


@pytest.mark.parametrize("fn_name", [
    "figC1_fuentes_a_caso",
    "figC5_maestra",
    "figC3_anatomia_rectena",
    "figC2_flujo_metodologico",
    "figC4_cadena_reproducible",
])
def test_figura_conceptual_se_genera(fn_name):
    """Cada generador conceptual produce un PNG no vacío sin lanzar excepción."""
    fn = getattr(fc, fn_name)
    path, detail = fn()
    assert os.path.isfile(path), f"{fn_name} no produjo archivo: {path}"
    assert os.path.getsize(path) > 1000, f"{fn_name} produjo un archivo vacío o corrupto"
