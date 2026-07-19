# -*- coding: utf-8 -*-
"""
Derivación de valores del ESTUDIO COMPARATIVO antena × sustrato (etapa F0).

SIN números escritos a mano: todo se deriva de los modelos de core/. Produce
_regen/out/comparative_values.json, consumido por las figuras comparativas y por
las tablas del documento del pivote de tesis.

Contenido del JSON:
  patch_dimensions   : dimensiones (mm) del parche @2.45 GHz sobre FR4/RT5880/RO4003C.
  sierpinski_dimensions : lado del triángulo mayor (λ_eff/2 @1.84 GHz, it.3) y la
                          serie de lados por iteración (÷2 por iteración, escala
                          de autosimilitud del Sierpinski).
  resonances         : frecuencias de resonancia [GHz] por antena.
  performance        : ganancia [dBi], η_rad y S11 mínimo en banda por antena×sustrato.
  harvest_urban_uW   : cosecha multibanda urbana de la Sierpinski (SSOT: core.multiband,
                       = 2,43 µW) y estimación HOMÓLOGA del parche multibanda,
                       calculada con LAS MISMAS funciones de core.multiband
                       (harvest_total_uw) alimentadas con la impedancia del parche
                       — mismo ambiente URBAN_AMBIENT_DBM, mismo co-diseño conjugado.
  literature         : filas citadas de la literatura (fuente EXTERNA, no de este modelo).

Ejecutar:
  PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/derive_comparative_values.py
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
from core import multiband as mb
from configs.parametros import (
    FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)

F0_PATCH = 2.45e9
F0_SIERP = 1.84e9
PATCH_SUBS = ('FR4', 'RT5880', 'RO4003C')


# ── 1. Dimensiones del parche por sustrato ────────────────────────────────────
def patch_dimensions() -> dict:
    return {s: MicrostripPatchAntenna(F0_PATCH, s).dimensions() for s in PATCH_SUBS}


# ── 2. Dimensiones de la Sierpinski ───────────────────────────────────────────
def sierpinski_dimensions() -> dict:
    # Convención documental (§3.3.2 / Figura 10): lado = c/(2 f0 √εr) con εr = 4,4
    # nominal a 1 GHz — la misma derivación cerrada que muestra el documento y la
    # cota dibujada en Fig12/Figura 10 (38,86 mm). No usar εr dispersivo aquí.
    from configs.parametros import FR4_ER_1GHZ, C0
    lado_base_mm = C0 / (2.0 * F0_SIERP * (FR4_ER_1GHZ ** 0.5)) * 1e3
    lados = {f'it{k}': round(lado_base_mm / (2.0 ** k), 3) for k in range(4)}
    return {
        'lado_base_mm':  round(lado_base_mm, 3),
        'escala_por_iteracion': 0.5,           # ÷2 por iteración (autosimilitud)
        'lados_por_iteracion_mm': lados,
        'f0_GHz': round(F0_SIERP / 1e9, 3),
        'iteraciones': 3,
    }


# ── 3. Resonancias por antena ─────────────────────────────────────────────────
def resonances() -> dict:
    sierp = FractalAntenna('sierpinski', iterations=3, base_freq=F0_SIERP)
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    return {
        'sierpinski':    [round(f / 1e9, 3) for f in sierp.fractal_resonances_hz if f < 7e9],
        'patch_FR4':     [round(f / 1e9, 3) for f in MicrostripPatchAntenna(F0_PATCH, 'FR4').resonances()],
        'patch_RT5880':  [round(f / 1e9, 3) for f in MicrostripPatchAntenna(F0_PATCH, 'RT5880').resonances()],
        # FLPDA: banda continua; se reportan las resonancias λ/2 de sus dipolos dentro de banda
        'flpda':         sorted({round(f / 1e9, 3) for f in flpda.resonant_freqs
                                 if flpda.f_low <= f <= flpda.f_high}),
    }


# ── 4. Desempeño por antena×sustrato ──────────────────────────────────────────
def _s11_min_in_band(obj, f_lo, f_hi, n=400) -> float:
    fs = np.linspace(f_lo, f_hi, n)
    return float(np.min(obj.S11_dB(fs)))


def performance() -> dict:
    out = {}
    # Sierpinski (calibrado solo para FR-4)
    sierp = FractalAntenna('sierpinski', iterations=3, base_freq=F0_SIERP)
    out['sierpinski_FR4'] = {
        'gain_dBi_f0': round(float(sierp.gain_dBi(F0_SIERP)), 3),
        'eta_rad_f0':  round(float(sierp.eta_rad(F0_SIERP)), 4),
        'S11_min_dB':  round(_s11_min_in_band(sierp, 1.6e9, 6.0e9), 2),
    }
    # Parche en los 3 sustratos
    for s in PATCH_SUBS:
        p = MicrostripPatchAntenna(F0_PATCH, s)
        out[f'patch_{s}'] = {
            'gain_dBi_f0': round(float(p.gain_dBi(F0_PATCH)), 3),
            'eta_rad_f0':  round(float(p.eta_rad(F0_PATCH)), 4),
            'S11_min_dB':  round(_s11_min_in_band(p, 1.0e9, 6.0e9), 2),
        }
    # FLPDA (FR-4, banda UHF)
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    out['flpda_FR4'] = {
        'gain_dBi_f0': round(float(flpda.gain_dBi(0.550e9)), 3),
        'eta_rad_f0':  round(float(flpda.eta_rad(0.550e9)), 4),
        'S11_min_dB':  round(_s11_min_in_band(flpda, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ), 2),
    }
    return out


# ── 5. Cosecha urbana multibanda ──────────────────────────────────────────────
def harvest_urban_uW() -> dict:
    """
    Cosecha multibanda (co-diseño conjugado integrado, ambiente URBAN_AMBIENT_DBM).

    Método HOMÓLOGO para ambas antenas: se usan las mismas funciones de
    core.multiband (harvest_total_uw), que suman en DC la potencia de una rama
    antena→red conjugada→diodo por banda. La única diferencia es la impedancia
    Za(f) de la antena: la Sierpinski (multibanda por autosimilitud) frente al
    parche (narrowband, sintonizado a 2,45 GHz). Así la comparación es justa.
    """
    rec = RectifierCircuit(topology='doubler', R_load=1300.0)
    imn = LMatchNetwork(Z_src=50.0)

    sierp = FractalAntenna('sierpinski', iterations=3, base_freq=F0_SIERP)
    h_sierp = mb.harvest_total_uw(sierp, rec, imn)

    patch = MicrostripPatchAntenna(F0_PATCH, 'FR4')
    h_patch = mb.harvest_total_uw(patch, rec, imn)

    return {
        'sierpinski_FR4': round(h_sierp, 3),
        'patch_FR4':      round(h_patch, 3),
        'metodo': 'core.multiband.harvest_total_uw (co-diseño conjugado, '
                  'ambiente URBAN_AMBIENT_DBM); misma cadena para ambas antenas.',
    }


# ── 6. Literatura citada (fuente externa) ─────────────────────────────────────
def literature() -> dict:
    return {
        'Zapata2021': {
            'fuente': 'externa',
            'geometria': 'espiral microcinta', 'sustrato': 'ARLON AD450',
            'er': 4.5, 'tand': 0.0035, 'h_mm': 3.0,
            'bandas_GHz': [1.6, 2.38, 3.38, 4.16], 'ganancia_dBi': [2.48, 7.66],
            'software': 'CST',
        },
        'Elshaekh2025': {
            'fuente': 'externa',
            'geometria': 'monopolo impreso', 'sustrato': 'FR4',
            'bandas_GHz': [0.9, 4.5, 7.0], 'ganancia_dBi': [3.5, 4.0],
            'software': 'CST+medido',
        },
        'Wang2022': {
            'fuente': 'externa',
            'sustrato': 'Duroid 5880',
            'nota': 'ya citado en el documento (referencia de validación del rectificador)',
        },
    }


def build_all() -> dict:
    return {
        'f0_patch_GHz': round(F0_PATCH / 1e9, 3),
        'patch_dimensions':     patch_dimensions(),
        'sierpinski_dimensions': sierpinski_dimensions(),
        'resonances':           resonances(),
        'performance':          performance(),
        'harvest_urban_uW':     harvest_urban_uW(),
        'literature':           literature(),
    }


if __name__ == '__main__':
    data = build_all()
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, 'comparative_values.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # ── Resumen legible ───────────────────────────────────────────────────────
    print('═══ ESTUDIO COMPARATIVO antena × sustrato — resumen ═══\n')
    print('Dimensiones del parche @2.45 GHz [mm]:')
    for s, d in data['patch_dimensions'].items():
        print(f'  {s:8s}: W={d["W_mm"]:.2f}  L={d["L_mm"]:.2f}  ε_eff={d["eps_eff"]:.3f}  ΔL={d["dL_mm"]:.3f}')
    sd = data['sierpinski_dimensions']
    print(f'\nSierpinski: lado base={sd["lado_base_mm"]:.2f} mm, '
          f'lados/it={sd["lados_por_iteracion_mm"]}')
    print('\nResonancias [GHz]:')
    for k, v in data['resonances'].items():
        print(f'  {k:14s}: {v}')
    print('\nDesempeño (@f0):')
    for k, v in data['performance'].items():
        print(f'  {k:16s}: G={v["gain_dBi_f0"]:.2f} dBi  η_rad={v["eta_rad_f0"]:.3f}  '
              f'S11_min={v["S11_min_dB"]:.1f} dB')
    hu = data['harvest_urban_uW']
    print(f'\nCosecha urbana [µW]: Sierpinski={hu["sierpinski_FR4"]:.2f}  '
          f'Parche={hu["patch_FR4"]:.2f}')
    print(f'\nGuardado: {path}')
