"""
================================================================================
TEST — Métricas de energía-complementaria (marco v7)
================================================================================
Bloquea la derivación de _regen/derive_battery_values.py: frenado de descarga,
autonomía extendida y casos net-positive, sin números a mano.

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    'derive_battery_values', ROOT / '_regen' / 'derive_battery_values.py')
dbv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dbv)

from configs.parametros import CANONICAL
from core.lora_budget import avg_power_uw, LORA_PROFILES


def test_energia_bateria():
    """E = C·3,6·V: 1000 mAh @3,7 V = 13 320 J; supercap 330 mF ≈ 1,26 J."""
    assert abs(dbv.battery_energy_J(1000) - 13320.0) < 1e-6
    assert abs(dbv.supercap_energy_J() - 0.5 * 0.330 * (3.3**2 - 1.8**2)) < 1e-9


def test_net_positive_escenario_b_100m():
    """B @100 m (1 335 µW) supera cualquier perfil: descarga detenida."""
    for prof in LORA_PROFILES.values():
        m = dbv.complementary_metrics(float(CANONICAL['P_dc_uW']),
                                      avg_power_uw(prof),
                                      dbv.battery_energy_J(500))
        assert m['net_positive'] is True
        assert m['visitas_ano_ext'] == 0.0


def test_frenado_consistente():
    """factor = P_load/(P_load−P_harvest) y autonomía extendida = base × factor."""
    p_l, p_h, e = 100.0, 60.0, dbv.battery_energy_J(100)
    m = dbv.complementary_metrics(p_h, p_l, e)
    assert m['net_positive'] is False
    assert abs(m['slowdown_factor'] - 2.5) < 1e-9
    assert abs(m['autonomia_ext_dias'] - m['autonomia_base_dias'] * 2.5) < 0.2


def test_matriz_completa_coherente():
    """La matriz cubre cosechas×perfiles×almacenamientos y B@200m frena SF12 >4×."""
    data = dbv.build_all(p_harvest_a_uw=2.43)   # A fijado para no correr conjugado
    n_esperado = len(data['harvests_uW']) * len(LORA_PROFILES) * len(data['storages_J'])
    assert len(data['matriz']) == n_esperado
    m = data['matriz']['B_dirigida_200m|LoRa SF12 BW125 (1% DC)|liion_500mAh']
    assert m['net_positive'] is False and m['slowdown_factor'] > 4.0


if __name__ == '__main__':
    for fn in (test_energia_bateria, test_net_positive_escenario_b_100m,
               test_frenado_consistente, test_matriz_completa_coherente):
        fn(); print(f'[OK] {fn.__name__}')
