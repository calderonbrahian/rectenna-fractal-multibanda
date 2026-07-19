"""
================================================================================
TEST — Parche microcinta × sustratos (capa de estudio comparativo F0)
================================================================================
Verifica el modelo analítico de cavidad (core/patch.py) y el catálogo de
sustratos (core/substrates.py), más una regresión que confirma que el refactor
de sustrato NO alteró los valores canónicos de FractalAntenna/FLPDA_Koch.

Ejecución:
    PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe -m pytest tests/test_patch_substrates.py -v

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import math
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

from core.patch import MicrostripPatchAntenna
from core.substrates import get_substrate, SUBSTRATES
from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from configs.parametros import (
    CANONICAL, fr4_er, FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)

C0 = 3e8
SUBS = ('FR4', 'RT5880', 'RO4003C')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 1 — Dimensión W del parche FR-4 @ 2.45 GHz contra cálculo cerrado
# ═════════════════════════════════════════════════════════════════════════════
def test_patch_W_fr4_closed_form():
    """W = c/(2 f0)·√(2/(εr+1)) con εr dispersivo del FR-4 (≈37,3–37,6 mm)."""
    f0 = 2.45e9
    p = MicrostripPatchAntenna(f0, 'FR4')
    er = fr4_er(f0)                       # εr dispersivo que usa la clase
    W_closed = C0 / (2 * f0) * math.sqrt(2.0 / (er + 1.0))
    assert abs(p.W - W_closed) < 1e-4, f'W={p.W*1e3:.3f} mm vs cerrado {W_closed*1e3:.3f} mm'
    # Rango físico esperado ~37 mm (referencia del pivote de tesis)
    assert 36.0 < p.W * 1e3 < 39.0, f'W={p.W*1e3:.2f} mm fuera de rango físico'
    print(f'  [OK] W_FR4 @2.45GHz = {p.W*1e3:.3f} mm')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 2 — ε_eff dentro de (1, εr) y creciente con εr
# ═════════════════════════════════════════════════════════════════════════════
def test_eps_eff_bounds_and_monotonic():
    """1 < ε_eff < εr para cada sustrato y ε_eff crece con εr (FR4>RO4003C>RT5880)."""
    eps = {}
    for name in SUBS:
        p = MicrostripPatchAntenna(2.45e9, name)
        er = p.er_f0
        assert 1.0 < p.eps_eff < er, f'{name}: ε_eff={p.eps_eff:.3f} no ∈ (1,{er:.2f})'
        eps[name] = p.eps_eff
    assert eps['RT5880'] < eps['RO4003C'] < eps['FR4'], f'orden ε_eff inconsistente: {eps}'
    print(f'  [OK] ε_eff: RT5880={eps["RT5880"]:.3f} < RO4003C={eps["RO4003C"]:.3f} < FR4={eps["FR4"]:.3f}')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 3 — L < W y ambos positivos para los 3 sustratos
# ═════════════════════════════════════════════════════════════════════════════
def test_L_lt_W_positive():
    """El largo resonante L es positivo y menor que el ancho W en los 3 sustratos."""
    for name in SUBS:
        p = MicrostripPatchAntenna(2.45e9, name)
        assert p.W > 0 and p.L > 0, f'{name}: dimensiones no positivas'
        assert p.L < p.W, f'{name}: L={p.L*1e3:.2f} mm no < W={p.W*1e3:.2f} mm'
        print(f'  [OK] {name}: W={p.W*1e3:.2f} > L={p.L*1e3:.2f} mm')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 4 — resonances() ordenadas y TM10 ≈ f0 (±2%)
# ═════════════════════════════════════════════════════════════════════════════
def test_resonances_sorted_tm10():
    """resonances() ordenadas ascendentes y modo dominante TM10 ≈ f0."""
    f0 = 2.45e9
    for name in SUBS:
        p = MicrostripPatchAntenna(f0, name)
        res = p.resonances()
        assert res == sorted(res), f'{name}: resonancias no ordenadas {res}'
        tm10 = dict((m[0], m[3]) for m in p.modes)['TM10']
        err = abs(tm10 - f0) / f0
        assert err < 0.02, f'{name}: TM10={tm10/1e9:.3f} GHz vs f0 (err {err*100:.2f}%)'
    print('  [OK] resonancias ordenadas y TM10≈f0 en los 3 sustratos')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 5 — η_rad(RT5880) > η_rad(FR4) a 2.45 GHz
# ═════════════════════════════════════════════════════════════════════════════
def test_eta_rad_rt5880_gt_fr4():
    """El sustrato de bajas pérdidas radia claramente mejor que el FR-4."""
    f0 = 2.45e9
    eta_fr4 = MicrostripPatchAntenna(f0, 'FR4').eta_rad(f0)
    eta_rt = MicrostripPatchAntenna(f0, 'RT5880').eta_rad(f0)
    assert 0.0 < eta_fr4 < 1.0 and 0.0 < eta_rt < 1.0
    assert eta_rt > eta_fr4 + 0.15, f'η_rad RT5880={eta_rt:.3f} no ≫ FR4={eta_fr4:.3f}'
    print(f'  [OK] η_rad: RT5880={eta_rt:.3f} > FR4={eta_fr4:.3f}')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 6 — gain_dBi coherente (2–9 dBi)
# ═════════════════════════════════════════════════════════════════════════════
def test_gain_range():
    """Ganancia de parche en rango físico 2–9 dBi para los 3 sustratos."""
    f0 = 2.45e9
    for name in SUBS:
        g = float(MicrostripPatchAntenna(f0, name).gain_dBi(f0))
        assert 2.0 <= g <= 9.0, f'{name}: G={g:.2f} dBi fuera de 2–9'
        print(f'  [OK] {name}: G(f0)={g:.2f} dBi')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 7 — S11(f0) < −6 dB (resonancia visible)
# ═════════════════════════════════════════════════════════════════════════════
def test_s11_resonance_visible():
    """El parche presenta un mínimo de reflexión claro en f0 (< −6 dB)."""
    f0 = 2.45e9
    for name in SUBS:
        s11 = float(MicrostripPatchAntenna(f0, name).S11_dB(f0))
        assert s11 < -6.0, f'{name}: S11(f0)={s11:.2f} dB no < −6'
        print(f'  [OK] {name}: S11(f0)={s11:.2f} dB')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 8 — Sustratos: FR4 dispersivo delega en configs; los otros constantes
# ═════════════════════════════════════════════════════════════════════════════
def test_substrate_dispersion():
    """FR-4 dispersivo (εr, tan δ varían con f); RT5880/RO4003C constantes."""
    fr4 = get_substrate('FR4')
    assert fr4.er(1e9) > fr4.er(5.8e9), 'FR-4 εr debe decrecer con f'
    assert abs(fr4.er(1e9) - 4.4) < 1e-9, 'FR-4 εr(1GHz) debe ser 4.4 (SSOT)'
    rt = get_substrate('RT5880')
    assert rt.er(1e9) == rt.er(6e9) == 2.2, 'RT5880 no dispersivo (εr=2.2)'
    assert rt.tan_delta(3e9) == 0.0009
    assert set(SUBSTRATES) == {'FR4', 'RT5880', 'RO4003C'}
    print('  [OK] dispersión de sustratos coherente')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 9 — Regresión: el refactor de sustrato NO alteró los canónicos
# ═════════════════════════════════════════════════════════════════════════════
def test_regression_substrate_refactor():
    """FractalAntenna y FLPDA_Koch con defaults ('FR4') dan los canónicos previos."""
    # FLPDA Koch @ 550 MHz — ganancia canónica 4.97 dBi
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
    g = float(flpda.gain_dBi(550e6))
    assert abs(g - CANONICAL['gain_dBi']) < 0.05, f'FLPDA gain={g:.3f} (canónico {CANONICAL["gain_dBi"]})'

    # Sierpinski: εr y η_rad deben ser idénticos vía delegación al sustrato FR4
    ant = FractalAntenna('sierpinski', iterations=3, base_freq=1.84e9)
    assert abs(ant.get_er(1.84e9) - fr4_er(1.84e9)) < 1e-12
    # η_rad a f0 en rango esperado documentado (~0.61 @1.84 GHz)
    eta = ant.eta_rad(1.84e9)
    assert 0.55 < eta < 0.70, f'η_rad Sierpinski @f0 = {eta:.3f} fuera de rango esperado'
    # explícito: substrate FR4 no cambió tan δ nominal
    assert ant.loss_tan == 0.02 and flpda.loss_tan == 0.02
    print(f'  [OK] regresión: FLPDA gain={g:.3f} dBi, εr/η_rad Sierpinski intactos')


if __name__ == '__main__':
    for fn in [v for k, v in sorted(globals().items()) if k.startswith('test_')]:
        print(f'▸ {fn.__name__}')
        fn()
        print()
    print('OK — tests de parche/sustratos')
