"""
================================================================================
TEST — Rediseño multibanda integrado (Escenario A, co-diseño conjugado)
================================================================================
Bloquea el comportamiento del rediseño 2026-07:
  - adaptación conjugada Za→Z_diodo recupera 6/7 bandas (vs 1/7 en 50 Ω),
  - la cosecha multibanda total es positiva y escala con el ambiente,
  - el criterio energía-asistido distingue sensor viable vs no viable.
No debe alterar ningún canónico del Escenario B (ver test_regression_canonical).

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import multiband as mb
from core.lora_budget import avg_power_uw, LORA_PROFILES
from configs.parametros import BANDS_A


def test_conjugado_recupera_6_de_7_bandas():
    """Con co-diseño conjugado integrado, ≥6/7 bandas dan η_match ≥ 0,5
    (vs 1/7 en la arquitectura modular de 50 Ω)."""
    ant, rec, imn = mb.build_default()
    n_ok = 0
    for _, f in BANDS_A.items():
        za = ant.impedance(f)
        zd = rec.diode.impedance(f)
        if imn.conjugate_efficiency(f, za, zd) >= 0.5:
            n_ok += 1
    assert n_ok >= 6, f'solo {n_ok}/7 bandas con η_match≥0,5 (esperado ≥6)'


def test_cosecha_multibanda_positiva_y_creciente():
    """La cosecha total es positiva y crece monótonamente con el ambiente."""
    ant, rec, imn = mb.build_default()
    curva = mb.harvest_vs_ambient(ant, rec, imn, amb_range_dbm=(-30, -5), n_pts=6)
    p = curva['P_dc_total_uW']
    assert p[-1] > p[0] >= 0.0, 'la cosecha debe crecer con el ambiente'
    assert p[-1] > 100.0, f'a −5 dBm/banda se esperan >100 µW, dio {p[-1]:.1f}'


def test_criterio_energia_asistido():
    """Sensor ADC ultra-bajo consumo es viable; LoRa SF12 continuo no,
    a nivel urbano nominal — justamente la distinción de los dos modos."""
    ant, rec, imn = mb.build_default()
    total = mb.harvest_total_uw(ant, rec, imn)
    adc = avg_power_uw(LORA_PROFILES['Sensor ADC (solo lectura)'])
    sf12 = avg_power_uw(LORA_PROFILES['LoRa SF12 BW125 (1% DC)'])
    assert mb.energy_assisted_viability(total, adc)['viable'] is True
    assert mb.energy_assisted_viability(total, sf12)['viable'] is False


def test_no_altera_escenario_b():
    """El módulo multibanda no toca la cadena canónica de la FLPDA."""
    from core.flpda import FLPDA_Koch
    from core.rectifier import RectifierCircuit
    from core.lora_budget import harvested_uw_full
    from configs.parametros import (CANONICAL, FLPDA_TAU, FLPDA_SIGMA,
                                    FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ)
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    rec = RectifierCircuit(topology='doubler', R_load=1300.0)
    res = harvested_uw_full(eirp_dbm=72.15, dist_m=100.0, freq_ghz=0.550,
                            antenna=flpda, rectifier=rec, matching_net=None)
    err = abs(res['P_dc_uW'] - CANONICAL['P_dc_uW']) / CANONICAL['P_dc_uW']
    assert err < 0.01, f'P_DC FLPDA cambió: {res["P_dc_uW"]:.1f} µW'


def test_montecarlo_determinista_y_valido():
    """El Monte Carlo multibanda es reproducible (misma semilla → misma media)
    y produce mayoría de muestras válidas."""
    ant, rec, imn = mb.build_default()
    r1 = mb.monte_carlo_harvest(ant, rec, imn, n_samples=2000)
    r2 = mb.monte_carlo_harvest(ant, rec, imn, n_samples=2000)
    assert abs(r1['mean'] - r2['mean']) < 1e-9, 'MC no determinista'
    assert r1['n_valid'] > 0.8 * r1['n_total'], 'demasiadas muestras nulas'
    assert r1['median'] > 0.0


def test_tornado_ambiente_domina():
    """La sensibilidad de la cosecha está dominada por el nivel ambiental,
    muy por encima de Q de componentes o R_load."""
    ant, rec, imn = mb.build_default()
    tor = mb.tornado_harvest(ant, rec, imn)
    top = tor['results'][0]
    assert top['param'] == 'amb_dbm', f'domina {top["param"]}, esperado amb_dbm'
    assert top['impact'] > 3 * tor['results'][1]['impact']


if __name__ == '__main__':
    for fn in [test_conjugado_recupera_6_de_7_bandas,
               test_cosecha_multibanda_positiva_y_creciente,
               test_criterio_energia_asistido, test_no_altera_escenario_b,
               test_montecarlo_determinista_y_valido, test_tornado_ambiente_domina]:
        fn(); print(f'[OK] {fn.__name__}')
