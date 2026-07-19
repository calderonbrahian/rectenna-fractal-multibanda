# -*- coding: utf-8 -*-
"""
================================================================================
TEST — Patrones de radiación, Carta de Smith y datasheet (Etapa G0)
================================================================================
Verifica core/patterns.py (cortes E/H normalizados), la Carta de Smith de
_regen/characterization_figures.py (|Γ|≤1 en los tres barridos), y el
datasheet derivado en _regen/out/datasheet_values.json, más una regresión
que confirma que CANONICAL y la suite completa siguen verdes.

Ejecución:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m pytest tests/test_patterns_datasheet.py -v

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from core.patterns import pattern_cuts
from core.antenna import FractalAntenna
from core.patch import MicrostripPatchAntenna
from core.flpda import FLPDA_Koch
from configs.parametros import (
    CANONICAL, FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)

DATASHEET_JSON = ROOT / '_regen' / 'out' / 'datasheet_values.json'


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 1 — Patrón normalizado: máximo exactamente 0 dB en los 3 tipos
# ═════════════════════════════════════════════════════════════════════════════
def test_patron_normalizado_max_0dB():
    """max(E_plane_dB) y max(H_plane_dB) == 0 dB para parche, Sierpinski y FLPDA."""
    casos = [
        ('patch', 2.45e9, {'substrate': 'FR4', 'f0_hz': 2.45e9}),
        ('sierpinski', 1.84e9, {'base_freq': 1.84e9, 'iterations': 3}),
        ('flpda', 0.55e9, dict(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                               f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)),
    ]
    for kind, f, params in casos:
        r = pattern_cuts(kind, f, **params)
        assert abs(float(np.max(r['E_plane_dB'])) - 0.0) < 1e-6, \
            f'{kind}: max E_plane_dB = {np.max(r["E_plane_dB"]):.4f} (esperado 0)'
        assert abs(float(np.max(r['H_plane_dB'])) - 0.0) < 1e-6, \
            f'{kind}: max H_plane_dB = {np.max(r["H_plane_dB"]):.4f} (esperado 0)'
        assert r['kind'] == kind and abs(r['freq_hz'] - f) < 1.0
        print(f'  [OK] {kind}: max(E)=max(H)=0 dB')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 2 — HPBW del parche en rango físico esperado
# ═════════════════════════════════════════════════════════════════════════════
def test_hpbw_parche_rango():
    """HPBW parche: plano E entre 40° y 120°; plano H entre 40° y 140°."""
    r = pattern_cuts('patch', 2.45e9, substrate='FR4', f0_hz=2.45e9)
    assert 40.0 < r['hpbw_e_deg'] < 120.0, f'HPBW_E parche = {r["hpbw_e_deg"]:.1f}° fuera de (40,120)'
    assert 40.0 < r['hpbw_h_deg'] < 140.0, f'HPBW_H parche = {r["hpbw_h_deg"]:.1f}° fuera de (40,140)'
    print(f'  [OK] HPBW parche: E={r["hpbw_e_deg"]:.1f}°  H={r["hpbw_h_deg"]:.1f}°')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 3 — FLPDA: F/B > 6 dB y máximo en boresight (endfire, θ≈0°)
# ═════════════════════════════════════════════════════════════════════════════
def test_flpda_front_to_back_y_direccion():
    """FLPDA: front_to_back_dB > 6 dB y max_direction_deg ≈ 0°."""
    r = pattern_cuts('flpda', 0.55e9, tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                      f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    assert r['front_to_back_dB'] > 6.0, f'F/B FLPDA = {r["front_to_back_dB"]:.2f} dB (esperado > 6)'
    assert abs(r['max_direction_deg']) < 1.0, \
        f'max_direction FLPDA = {r["max_direction_deg"]:.2f}° (esperado ≈ 0°)'
    print(f'  [OK] FLPDA: F/B={r["front_to_back_dB"]:.1f} dB  dir_max={r["max_direction_deg"]:.2f}°')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 4 — Sierpinski: HPBW ≥ parche (patrón más ancho, aproximación triangular)
# ═════════════════════════════════════════════════════════════════════════════
def test_sierpinski_hpbw_mas_ancho_que_parche():
    """El patrón equivalente de la Sierpinski es más ancho que el del parche."""
    r_sierp = pattern_cuts('sierpinski', 1.84e9, base_freq=1.84e9, iterations=3)
    r_patch = pattern_cuts('patch', 2.45e9, substrate='FR4', f0_hz=2.45e9)
    assert r_sierp['hpbw_e_deg'] >= r_patch['hpbw_e_deg'], \
        f'HPBW_E Sierpinski={r_sierp["hpbw_e_deg"]:.1f}° no >= parche={r_patch["hpbw_e_deg"]:.1f}°'
    assert r_sierp['hpbw_h_deg'] >= r_patch['hpbw_h_deg'], \
        f'HPBW_H Sierpinski={r_sierp["hpbw_h_deg"]:.1f}° no >= parche={r_patch["hpbw_h_deg"]:.1f}°'
    print(f'  [OK] HPBW Sierpinski (E={r_sierp["hpbw_e_deg"]:.1f}°, H={r_sierp["hpbw_h_deg"]:.1f}°) '
          f'>= parche (E={r_patch["hpbw_e_deg"]:.1f}°, H={r_patch["hpbw_h_deg"]:.1f}°)')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 5 — Carta de Smith: |Γ|≤1 en los barridos de las 3 antenas
# ═════════════════════════════════════════════════════════════════════════════
def test_smith_gamma_acotado():
    """|Γ(f)| ≤ 1 (con tolerancia numérica) en los barridos de diseño de las
    tres antenas: Sierpinski y parche 1–6 GHz, FLPDA 0.4–1.0 GHz."""
    sierp = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)
    patch = MicrostripPatchAntenna(2.45e9, 'FR4')
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)

    casos = [
        ('sierpinski', sierp, 1.0e9, 6.0e9),
        ('parche_FR4', patch, 1.0e9, 6.0e9),
        ('flpda', flpda, 0.4e9, 1.0e9),
    ]
    for nombre, obj, f_lo, f_hi in casos:
        fs = np.linspace(f_lo, f_hi, 400)
        Z = np.atleast_1d(obj.impedance(fs))
        gam = (Z - 50.0) / (Z + 50.0)
        max_gam = float(np.max(np.abs(gam)))
        assert max_gam <= 1.0 + 1e-6, f'{nombre}: |Gamma|max={max_gam:.4f} > 1'
        print(f'  [OK] {nombre}: |Gamma|max={max_gam:.4f} <= 1')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 6 — Datasheet: las 4 entradas tienen todas las claves y P_dc coincide
# ═════════════════════════════════════════════════════════════════════════════
def test_datasheet_claves_y_valores_canonicos():
    """El datasheet JSON tiene sierpinski/patch_FR4/patch_RT5880/flpda con las
    claves requeridas, y P_dc_uW coincide con los valores canónicos/JSON
    (1335.0 FLPDA; ≈2.43 µW Sierpinski)."""
    assert DATASHEET_JSON.exists(), (
        f'{DATASHEET_JSON} no existe: ejecuta primero '
        '`PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe _regen/derive_datasheet.py`'
    )
    data = json.loads(DATASHEET_JSON.read_text(encoding='utf-8'))

    claves_esperadas = {
        'tipo', 'geometria_mm', 'sustrato', 'bandas_GHz', 'S11_min_dB_por_banda',
        'Z_in_f0_ohm', 'gain_dBi_f0', 'eta_rad_f0', 'hpbw_e_deg', 'hpbw_h_deg',
        'front_to_back_dB', 'energia',
    }
    assert set(data.keys()) == {'sierpinski', 'patch_FR4', 'patch_RT5880', 'flpda'}
    for nombre, entrada in data.items():
        faltantes = claves_esperadas - set(entrada.keys())
        assert not faltantes, f'{nombre}: faltan claves {faltantes}'
        assert set(entrada['Z_in_f0_ohm'].keys()) == {'R_ohm', 'X_ohm'}
        assert set(entrada['sustrato'].keys()) == {'nombre', 'er', 'tand', 'h_mm'}
        assert 'P_dc_uW' in entrada['energia']

    p_dc_flpda = data['flpda']['energia']['P_dc_uW']
    assert abs(p_dc_flpda - 1335.0) < 0.5, f'P_dc FLPDA = {p_dc_flpda} (esperado 1335.0)'

    p_dc_sierp = data['sierpinski']['energia']['P_dc_uW']
    assert abs(p_dc_sierp - 2.43) < 0.05, f'P_dc Sierpinski = {p_dc_sierp} (esperado ≈2.43)'

    print(f'  [OK] datasheet: claves completas en las 4 entradas; '
          f'P_dc FLPDA={p_dc_flpda} µW, Sierpinski={p_dc_sierp} µW')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 7 — Regresión: CANONICAL intacto tras añadir patterns/datasheet
# ═════════════════════════════════════════════════════════════════════════════
def test_regresion_canonical_intacto():
    """La capa de patrones/datasheet (G0) no altera CANONICAL ni el modelo
    físico de FLPDA_Koch/FractalAntenna (S11_dB, gain_dBi, impedance)."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    g = float(flpda.gain_dBi(550e6))
    assert abs(g - CANONICAL['gain_dBi']) < 0.05, \
        f'FLPDA gain @550MHz = {g:.3f} (canónico {CANONICAL["gain_dBi"]})'

    sierp = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)
    eta = float(sierp.eta_rad(1.84e9))
    assert 0.55 < eta < 0.70, f'eta_rad Sierpinski @f0 = {eta:.3f} fuera de rango esperado'

    # core.patterns no debe requerir tocar impedance()/S11_dB(): verifica que
    # siguen siendo invocables y consistentes tras la importación del módulo.
    s11 = float(flpda.S11_dB(550e6))
    assert abs(s11 - CANONICAL['S11_dB']) < 0.1, f'S11 FLPDA @550MHz = {s11:.2f} (canónico {CANONICAL["S11_dB"]})'

    print(f'  [OK] regresión: FLPDA gain={g:.3f} dBi, S11={s11:.2f} dB, '
          f'eta_rad Sierpinski={eta:.3f} — CANONICAL intacto')


if __name__ == '__main__':
    for fn in [v for k, v in sorted(globals().items()) if k.startswith('test_')]:
        print(f'▸ {fn.__name__}')
        fn()
        print()
    print('OK — tests de patrones/datasheet')
