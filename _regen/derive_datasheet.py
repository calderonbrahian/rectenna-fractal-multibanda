# -*- coding: utf-8 -*-
"""
================================================================================
Derivación del DATASHEET por antena — capa de caracterización (Etapa G0)
================================================================================
SIN números escritos a mano: todo se deriva de los modelos de core/ (impedancia,
ganancia, eficiencia de radiación, patrones de core.patterns) y de los valores
CANÓNICOS/JSON existentes para la energía cosechada (core.multiband para
Sierpinski/parche en ambiente urbano A; configs.parametros.CANONICAL para la
FLPDA en el enlace TDT @100 m). Produce _regen/out/datasheet_values.json.

Antenas cubiertas: sierpinski, patch_FR4, patch_RT5880, flpda.

Ejecutar:
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/derive_datasheet.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from core.patch import MicrostripPatchAntenna
from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.matching import LMatchNetwork
from core.substrates import get_substrate
from core.patterns import pattern_cuts
from core import multiband as mb
from configs.parametros import (
    CANONICAL, FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
    FR4_ER_1GHZ, C0,
)

F0_SIERP = 1.84e9
F0_PATCH = 2.45e9
F0_FLPDA = 550e6   # punto de operación canónico (TDT DVB-T, CANONICAL)


# ── Utilidades ─────────────────────────────────────────────────────────────────

def _s11_min_por_banda(obj, freqs_hz, span_frac: float = 0.04, n: int = 121) -> dict:
    """S11 mínimo [dB] en una ventana ±span_frac alrededor de cada frecuencia
    de resonancia dada (barrido fino local)."""
    out = {}
    for f in freqs_hz:
        f_lo = f * (1.0 - span_frac)
        f_hi = f * (1.0 + span_frac)
        fs = np.linspace(f_lo, f_hi, n)
        s11 = np.asarray(obj.S11_dB(fs), dtype=float)
        out[f'{f/1e9:.3f}_GHz'] = round(float(np.min(s11)), 2)
    return out


def _z_in(obj, f0_hz: float) -> dict:
    z = complex(obj.impedance(f0_hz))
    return {'R_ohm': round(z.real, 2), 'X_ohm': round(z.imag, 2)}


# ── Sierpinski ─────────────────────────────────────────────────────────────────

def datasheet_sierpinski() -> dict:
    ant = FractalAntenna('sierpinski', iterations=3, base_freq=F0_SIERP)
    sub = ant.substrate
    bandas = [f for f in ant.fractal_resonances_hz if f < 7e9]

    rec = RectifierCircuit(topology='doubler', R_load=1300.0)
    imn = LMatchNetwork(Z_src=50.0)
    p_dc = mb.harvest_total_uw(ant, rec, imn)

    pat = pattern_cuts('sierpinski', F0_SIERP, base_freq=F0_SIERP, iterations=3)

    # Convención documental (§3.3.2 / Figura 10, misma que derive_comparative_values.py):
    # lado = c/(2 f0 sqrt(er)) con er = FR4_ER_1GHZ (4,4 nominal @1 GHz). NO usar
    # ant.base_dim (dispersivo en f0) para no contradecir la Tabla 3 de diseño.
    lado_base_mm = C0 / (2.0 * F0_SIERP * (FR4_ER_1GHZ ** 0.5)) * 1e3

    return {
        'tipo': 'Sierpinski Gasket it.3 (fractal multibanda)',
        'geometria_mm': {
            'lado_base':        round(lado_base_mm, 3),
            'lado_activo_it3':  round(lado_base_mm / (2 ** 3), 3),
            'escala_por_iteracion': 0.5,
        },
        'sustrato': {
            'nombre': sub.name, 'er': round(sub.er(F0_SIERP), 3),
            'tand': round(sub.tan_delta(F0_SIERP), 4), 'h_mm': round(sub.h * 1e3, 3),
        },
        'bandas_GHz': [round(float(f) / 1e9, 3) for f in bandas],
        'S11_min_dB_por_banda': _s11_min_por_banda(ant, bandas),
        'Z_in_f0_ohm':  _z_in(ant, F0_SIERP),
        'gain_dBi_f0':  round(float(ant.gain_dBi(F0_SIERP)), 3),
        'eta_rad_f0':   round(float(ant.eta_rad(F0_SIERP)), 4),
        'hpbw_e_deg':   round(pat['hpbw_e_deg'], 2),
        'hpbw_h_deg':   round(pat['hpbw_h_deg'], 2),
        'front_to_back_dB': round(pat['front_to_back_dB'], 2),
        'energia': {
            'escenario': 'Ambiente urbano A (multibanda, co-diseño conjugado integrado)',
            'P_incidente_o_ambiente': 'configs.parametros.URBAN_AMBIENT_DBM (−24 a −18 dBm/banda)',
            'P_dc_uW': round(p_dc, 3),
        },
    }


# ── Parche (FR4 / RT5880) ──────────────────────────────────────────────────────

def datasheet_patch(substrate_name: str, incluir_energia: bool) -> dict:
    ant = MicrostripPatchAntenna(F0_PATCH, substrate_name)
    sub = ant.substrate
    bandas = ant.resonances()

    pat = pattern_cuts('patch', F0_PATCH, substrate=substrate_name, f0_hz=F0_PATCH)

    entry = {
        'tipo': f'Parche microcinta rectangular ({sub.name}, alimentación inset)',
        'geometria_mm': ant.dimensions(),
        'sustrato': {
            'nombre': sub.name, 'er': round(ant.er_f0, 3),
            'tand': round(sub.tan_delta(F0_PATCH), 4), 'h_mm': round(sub.h * 1e3, 3),
        },
        'bandas_GHz': [round(float(f) / 1e9, 3) for f in bandas],
        'S11_min_dB_por_banda': _s11_min_por_banda(ant, bandas),
        'Z_in_f0_ohm':  _z_in(ant, F0_PATCH),
        'gain_dBi_f0':  round(float(ant.gain_dBi(F0_PATCH)), 3),
        'eta_rad_f0':   round(float(ant.eta_rad(F0_PATCH)), 4),
        'hpbw_e_deg':   round(pat['hpbw_e_deg'], 2),
        'hpbw_h_deg':   round(pat['hpbw_h_deg'], 2),
        'front_to_back_dB': round(pat['front_to_back_dB'], 2),
    }

    if incluir_energia:
        rec = RectifierCircuit(topology='doubler', R_load=1300.0)
        imn = LMatchNetwork(Z_src=50.0)
        p_dc = mb.harvest_total_uw(ant, rec, imn)
        entry['energia'] = {
            'escenario': 'Ambiente urbano A (multibanda, co-diseño conjugado integrado; '
                         'método homólogo al de la Sierpinski, core.multiband)',
            'P_incidente_o_ambiente': 'configs.parametros.URBAN_AMBIENT_DBM (−24 a −18 dBm/banda)',
            'P_dc_uW': round(p_dc, 3),
        }
    else:
        entry['energia'] = {
            'escenario': 'No evaluado en el estudio comparativo (fuera de alcance F0/G0)',
            'P_incidente_o_ambiente': None,
            'P_dc_uW': None,
        }
    return entry


# ── FLPDA Koch ─────────────────────────────────────────────────────────────────

def datasheet_flpda() -> dict:
    ant = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                      f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    sub = ant.substrate
    bandas = sorted({f for f in ant.resonant_freqs if ant.f_low <= f <= ant.f_high})

    pat = pattern_cuts('flpda', F0_FLPDA, tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                        f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)

    return {
        'tipo': 'FLPDA Koch it.2 (log-periódica de dipolos, endfire)',
        'geometria_mm': {
            'n_elementos':          ant.n_elements,
            'boom_mm':              round(ant.boom_length_m * 1e3, 2),
            'dipolo_max_fisico_mm': round(ant.max_element_length_m * 1e3, 2),
            'k_red_koch':           round(ant.k_red, 4),
        },
        'sustrato': {
            'nombre': sub.name, 'er': round(ant.er, 3),
            'tand': round(ant.loss_tan, 4), 'h_mm': round(sub.h * 1e3, 3),
        },
        'bandas_GHz': [round(float(f) / 1e9, 3) for f in bandas],
        'S11_min_dB_por_banda': _s11_min_por_banda(ant, bandas),
        'Z_in_f0_ohm':  _z_in(ant, F0_FLPDA),
        'gain_dBi_f0':  round(float(ant.gain_dBi(F0_FLPDA)), 3),
        'eta_rad_f0':   round(float(ant.eta_rad(F0_FLPDA)), 4),
        'hpbw_e_deg':   round(pat['hpbw_e_deg'], 2),
        'hpbw_h_deg':   round(pat['hpbw_h_deg'], 2),
        'front_to_back_dB': round(pat['front_to_back_dB'], 2),
        'energia': {
            'escenario': 'TDT DVB-T (Cerro Nutibara, 10 kW ERP) @ 100 m, enlace dirigido (Escenario B)',
            'P_incidente_o_ambiente': f"P_in={CANONICAL['P_in_dBm']} dBm (EIRP 72.15 dBm, FSPL {CANONICAL['FSPL_dB']} dB)",
            'P_dc_uW': CANONICAL['P_dc_uW'],
        },
    }


def build_all() -> dict:
    return {
        'sierpinski':    datasheet_sierpinski(),
        'patch_FR4':     datasheet_patch('FR4', incluir_energia=True),
        'patch_RT5880':  datasheet_patch('RT5880', incluir_energia=True),
        'flpda':         datasheet_flpda(),
    }


if __name__ == '__main__':
    data = build_all()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'datasheet_values.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    print('═══ DATASHEET por antena — resumen ═══\n')
    for key, d in data.items():
        print(f'▸ {key} — {d["tipo"]}')
        print(f'    Bandas [GHz]     : {d["bandas_GHz"]}')
        print(f'    Z_in @f0 [Ω]     : R={d["Z_in_f0_ohm"]["R_ohm"]}  X={d["Z_in_f0_ohm"]["X_ohm"]}')
        print(f'    G(f0)            : {d["gain_dBi_f0"]:.2f} dBi   η_rad={d["eta_rad_f0"]:.3f}')
        print(f'    HPBW E/H         : {d["hpbw_e_deg"]:.1f}° / {d["hpbw_h_deg"]:.1f}°   F/B={d["front_to_back_dB"]:.1f} dB')
        print(f'    Energía          : {d["energia"]["escenario"]} -> P_dc={d["energia"]["P_dc_uW"]} µW')
        print()
    print(f'Guardado: {path}')
