# -*- coding: utf-8 -*-
"""
Derivación de métricas de operación energía-complementaria (marco v7).

La narrativa del documento pasa de "autonomía total sin batería" a "RFEH como
fuente complementaria que recarga el almacenamiento y extiende la autonomía".
Este script deriva, SIN números a mano, las tres métricas del marco nuevo:

  1. Factor de frenado de la descarga  = P_load / (P_load − P_harvest)
     (idéntico al multiplicador de autonomía: la batería se descarga a la
     potencia neta P_net = P_load − P_harvest en vez de a P_load).
  2. Autonomía base y extendida [días] para almacenamientos concretos:
     Li-ion/LiPo 100/500/1000 mAh @ 3,7 V (E = C·3,6·V julios) y el
     supercondensador 330 mF del caso canónico.
  3. Reducción de visitas de mantenimiento [visitas/año] (recargas o
     reemplazos que el balance neto evita).

Si P_harvest ≥ P_load el balance es net-positive: la batería no se descarga
(autonomía indefinida, el caso "sin batería primaria" del Modo 1).

Entradas (SSOT): CANONICAL['P_dc_uW'] (Escenario B @100 m), la cosecha
multibanda del Escenario A (core.multiband, ambiente urbano nominal) y los
perfiles de consumo LORA_PROFILES (core.lora_budget.avg_power_uw).

Salida: _regen/out/battery_values.json — consumida por los scripts de edición
del documento y por la app (ninguna cifra del texto se escribe a mano).

Ejecutar:  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/derive_battery_values.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.parametros import CANONICAL
from core.lora_budget import avg_power_uw, LORA_PROFILES

# ── Almacenamientos evaluados ─────────────────────────────────────────────────
V_LIION = 3.7          # tensión nominal Li-ion/LiPo [V]
BATTERIES_MAH = (100, 500, 1000)
SUPERCAP_F, SUPERCAP_VMAX, SUPERCAP_VMIN = 0.330, 3.3, 1.8  # caso canónico B.9

SECONDS_PER_DAY = 86400.0
DAYS_PER_YEAR = 365.0


def battery_energy_J(c_mah: float, v_nom: float = V_LIION) -> float:
    """Energía nominal de una batería [J]: E = C[mAh]·3,6·V."""
    return c_mah * 3.6 * v_nom


def supercap_energy_J(c_f: float = SUPERCAP_F, v_max: float = SUPERCAP_VMAX,
                      v_min: float = SUPERCAP_VMIN) -> float:
    """Energía útil del supercondensador [J]: ½C(V_max²−V_min²)."""
    return 0.5 * c_f * (v_max ** 2 - v_min ** 2)


def complementary_metrics(p_harvest_uw: float, p_load_uw: float,
                          e_storage_J: float) -> dict:
    """
    Métricas del régimen energía-complementaria para un (cosecha, carga,
    almacenamiento). Potencias en µW, energía en J, autonomías en días.
    """
    p_net_uw = p_load_uw - p_harvest_uw
    aut_base_d = e_storage_J / (p_load_uw * 1e-6) / SECONDS_PER_DAY
    if p_net_uw <= 0.0:
        return {
            'net_positive': True,
            'slowdown_factor': None,            # descarga detenida
            'autonomia_base_dias': round(aut_base_d, 1),
            'autonomia_ext_dias': None,         # indefinida
            'visitas_ano_base': round(DAYS_PER_YEAR / aut_base_d, 1) if aut_base_d > 0 else None,
            'visitas_ano_ext': 0.0,
        }
    factor = p_load_uw / p_net_uw
    aut_ext_d = e_storage_J / (p_net_uw * 1e-6) / SECONDS_PER_DAY
    return {
        'net_positive': False,
        'slowdown_factor': round(factor, 3),
        'autonomia_base_dias': round(aut_base_d, 1),
        'autonomia_ext_dias': round(aut_ext_d, 1),
        'visitas_ano_base': round(DAYS_PER_YEAR / aut_base_d, 1) if aut_base_d > 0 else None,
        'visitas_ano_ext': round(DAYS_PER_YEAR / aut_ext_d, 1) if aut_ext_d > 0 else None,
    }


def harvest_escenario_a_uw() -> float:
    """Cosecha multibanda del Escenario A a ambiente urbano nominal (SSOT)."""
    from core import multiband as mb
    ant, rec, imn = mb.build_default()
    return mb.harvest_total_uw(ant, rec, imn)


def harvest_escenario_b_uw(dist_m: float) -> float:
    """Cosecha del Escenario B a una distancia dada de la torre TDT (SSOT).

    A 100 m el balance es net-positive y la batería no se descarga; el valor
    del marco complementario aparece MÁS ALLÁ de la frontera continua
    (~175 m), donde la cosecha ya no sostiene sola al nodo pero sí frena la
    descarga del almacenamiento. Por eso se derivan también 200/300/500 m.
    """
    from core.flpda import FLPDA_Koch
    from core.rectifier import RectifierCircuit
    from core.lora_budget import harvested_uw_full
    from configs.parametros import (FLPDA_TAU, FLPDA_SIGMA,
                                    FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ)
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    rec = RectifierCircuit(topology='doubler', R_load=1300.0)
    res = harvested_uw_full(eirp_dbm=72.15, dist_m=dist_m, freq_ghz=0.550,
                            antenna=flpda, rectifier=rec, matching_net=None)
    return float(res['P_dc_uW'])


def build_all(p_harvest_a_uw: float = None) -> dict:
    """Matriz completa cosecha × perfil de carga × almacenamiento."""
    harvests = {
        'B_dirigida_100m': float(CANONICAL['P_dc_uW']),
        'B_dirigida_200m': round(harvest_escenario_b_uw(200.0), 1),
        'B_dirigida_300m': round(harvest_escenario_b_uw(300.0), 1),
        'B_dirigida_500m': round(harvest_escenario_b_uw(500.0), 1),
        'A_multibanda_urbano': (float(p_harvest_a_uw) if p_harvest_a_uw is not None
                                 else round(harvest_escenario_a_uw(), 2)),
    }
    storages = {f'liion_{c}mAh': battery_energy_J(c) for c in BATTERIES_MAH}
    storages['supercap_330mF'] = supercap_energy_J()

    out = {'V_liion': V_LIION, 'harvests_uW': harvests,
           'storages_J': {k: round(v, 1) for k, v in storages.items()},
           'matriz': {}}
    for hname, h_uw in harvests.items():
        for pname, prof in LORA_PROFILES.items():
            p_load = avg_power_uw(prof)
            for sname, e_j in storages.items():
                key = f'{hname}|{pname}|{sname}'
                m = complementary_metrics(h_uw, p_load, e_j)
                m['P_harvest_uW'] = round(h_uw, 2)
                m['P_load_uW'] = round(p_load, 2)
                out['matriz'][key] = m
    return out


if __name__ == '__main__':
    data = build_all()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'battery_values.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print('Cosechas [µW]:', data['harvests_uW'])
    print('Almacenamientos [J]:', data['storages_J'])
    # muestra representativa
    for k in list(data['matriz']):
        m = data['matriz'][k]
        if 'liion_500mAh' in k:
            tag = 'NET+' if m['net_positive'] else f"x{m['slowdown_factor']}"
            print(f"  {k}: base {m['autonomia_base_dias']} d -> "
                  f"{'indefinida' if m['net_positive'] else str(m['autonomia_ext_dias'])+' d'} ({tag})")
    print('Guardado:', path)
