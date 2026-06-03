"""
================================================================================
TEST DE REGRESIÓN — Valores canónicos de la tesis
================================================================================
Bloquea numéricamente los valores reportados en el documento oficial:

    Calderon_Munera_B_TG_UdeA_APA7_FINAL_*.docx

Si algún módulo del proyecto cambia de comportamiento numérico (e.g. ajuste
del modelo RLC, alteración de parámetros SPICE, modificación de la cadena
RF→DC), este test FALLA — lo cual es exactamente lo que queremos para
mantener trazabilidad código ↔ tesis.

Ejecución:
    cd rectenna_dashboard_st
    python -m pytest tests/test_regression_canonical.py -v
    # o sin pytest:
    python tests/test_regression_canonical.py

Autor: Brahian Calderón Múnera · UdeA · 2026
================================================================================
"""

import math
import sys
from pathlib import Path

# Forzar UTF-8 en stdout (Windows console por defecto cp1252)
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# Permitir ejecución directa sin instalar paquete
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.antenna import FractalAntenna
from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit, SchottkyDiode_SMS7630
from core.matching import LMatchNetwork
from core.lora_budget import (
    harvested_uw_full, fspl_dB, received_power_dBm,
    URBAN_CORRECTION_DB,
)
from core.comparacion import validate_wang2022
from configs.parametros import (
    CANONICAL, SMS7630, BANDS_A, FLPDA_TAU, FLPDA_SIGMA,
    FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ,
)


# ─── Tolerancias ──────────────────────────────────────────────────────────────
TOL_REL  = 0.005   # 0,5 % tolerancia relativa para valores principales
TOL_ABS  = 0.05    # tolerancia absoluta para cantidades en dB


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 1 — Diodo SMS7630: parámetros SPICE y frecuencia de corte
# ═════════════════════════════════════════════════════════════════════════════
def test_diodo_sms7630_parametros():
    """Bloquea Is, n, Rs, Cj0 de SMS7630 (datasheet Skyworks AN-4003)."""
    d = SchottkyDiode_SMS7630()
    assert d.Is  == SMS7630['Is']
    assert d.n   == SMS7630['n']
    assert d.Rs  == SMS7630['Rs']
    assert d.Cj0 == SMS7630['Cj0']
    print('  [OK] SMS7630 parámetros SPICE coherentes')


def test_frecuencia_corte_sms7630():
    """Bloquea f_c ≈ 56,8 GHz reportada en §2.6.2."""
    d = SchottkyDiode_SMS7630()
    fc = 1 / (2 * math.pi * d.Rs * d.Cj0)
    fc_GHz = fc / 1e9
    assert abs(fc_GHz - 56.8) < 0.1, f'f_c = {fc_GHz:.2f} GHz (esperado 56,8)'
    print(f'  [OK] f_c SMS7630 = {fc_GHz:.2f} GHz  (§2.6.2)')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 2 — FLPDA Koch: diseño Carrel (1961) + reducción Koch
# ═════════════════════════════════════════════════════════════════════════════
def test_flpda_diseno_carrel():
    """Bloquea n_elementos, boom y reducción Koch reportados en §3.4.2."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ,
                       koch_iter=2)
    assert flpda.n_elements == 8, f'n_elementos = {flpda.n_elements} (esperado 8)'
    boom_cm = flpda.boom_length_m * 100
    assert abs(boom_cm - 50.0) < 5.0, f'boom = {boom_cm:.1f} cm (esperado ~50)'
    red = (1 - flpda.k_red) * 100
    assert abs(red - 43.75) < 0.1, f'reducción Koch = {red:.2f}% (esperado 43,75)'
    print(f'  [OK] FLPDA: n_el={flpda.n_elements}, boom={boom_cm:.1f}cm, red Koch={red:.2f}%')


def test_flpda_ganancia_550mhz():
    """Bloquea ganancia FLPDA Koch @ 550 MHz = 7,10 dBi (CANONICAL)."""
    flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                       f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ,
                       koch_iter=2)
    g = float(flpda.gain_dBi(550e6))
    assert abs(g - CANONICAL['gain_dBi']) < 0.05, \
        f'gain @ 550 MHz = {g:.2f} dBi (esperado {CANONICAL["gain_dBi"]})'
    print(f'  [OK] Ganancia FLPDA @ 550 MHz = {g:.2f} dBi')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 3 — Propagación: Friis + corrección urbana (§2.4 y §4.3.1)
# ═════════════════════════════════════════════════════════════════════════════
def test_fspl_550mhz_100m():
    """Bloquea FSPL(550 MHz, 100 m) = 67,2 dB."""
    fspl = fspl_dB(100.0, 0.550)
    assert abs(fspl - 67.25) < 0.1, f'FSPL = {fspl:.2f} dB (esperado 67,2–67,3)'
    print(f'  [OK] FSPL(550 MHz, 100 m) = {fspl:.2f} dB')


def test_p_in_cerro_nutibara_100m():
    """Bloquea P_in @ 100 m de TDT 10 kW = +3,85 dBm."""
    P_in = received_power_dBm(eirp_dbm=70.0, dist_m=100.0,
                              freq_ghz=0.550, ant_gain_dBi=7.10)
    assert abs(P_in - 3.85) < 0.1, f'P_in = {P_in:.2f} dBm (esperado +3,85)'
    print(f'  [OK] P_in @ 100 m, 10 kW TDT = {P_in:.2f} dBm')


def test_correccion_urbana_itu():
    """Bloquea corrección urbana ITU-R P.1546 = 6 dB."""
    assert URBAN_CORRECTION_DB == 6.0
    print('  [OK] Corrección urbana ITU-R P.1546 = 6 dB')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 4 — Cadena RF→DC canónica (§4.3.1 Tabla 8/9b)
# ═════════════════════════════════════════════════════════════════════════════
def test_cadena_potencia_canonica():
    """
    Bloquea TODA la cadena de potencia @ 100 m del Cerro Nutibara:
      EIRP +70 dBm → FSPL → urbano → η_mm → η_imn → PCE → η_PMIC → P_DC
    Resultado esperado: P_DC = 1.637,6 µW
    """
    flpda     = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                           f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ,
                           koch_iter=2)
    rectifier = RectifierCircuit(topology='doubler', R_load=1300.0)

    res = harvested_uw_full(
        eirp_dbm=70.0, dist_m=100.0, freq_ghz=0.550,
        antenna=flpda, rectifier=rectifier, matching_net=None,
    )

    P_dc_uW = res['P_dc_uW']
    P_canon = CANONICAL['P_dc_uW']
    err_pct = abs(P_dc_uW - P_canon) / P_canon * 100
    assert err_pct < 1.0, \
        f'P_DC = {P_dc_uW:.1f} µW (canónico {P_canon}, error {err_pct:.2f}%)'

    assert res['PCE'] >= 0.84, f'PCE = {res["PCE"]:.3f} (esperado ≥ 0,84)'
    assert bool(res['coldstart_ok']), 'Cold-start False (esperado True)'

    print(f'  [OK] P_DC @ 100 m = {P_dc_uW:.1f} µW  (canónico {P_canon})')
    print(f'  [OK] η_mm={res["eta_mm"]:.4f}  η_imn={res["eta_imn"]:.4f}  '
          f'PCE={res["PCE"]:.3f}  η_total={res["eta_total"]:.4f}')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 5 — Validación cruzada Wang et al. (2022) — RMSE ≈ 15,5 pp
# ═════════════════════════════════════════════════════════════════════════════
def test_validacion_wang2022_rmse():
    """Bloquea RMSE de PCE vs Wang et al. (2022) reportado en §4.5."""
    rectifier = RectifierCircuit(topology='doubler', R_load=1300.0)
    val = validate_wang2022(rectifier, matching_net=None)
    rmse = val['RMSE']
    rmse_canon = CANONICAL['RMSE_wang']
    assert abs(rmse - rmse_canon) < 0.5, \
        f'RMSE = {rmse:.2f} pp (canónico {rmse_canon})'
    print(f'  [OK] RMSE Wang 2022 = {rmse:.2f} pp  (canónico {rmse_canon})')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 6 — Sierpinski: resonancias log-periódicas (Puente-Baliarda 1998)
# ═════════════════════════════════════════════════════════════════════════════
def test_sierpinski_resonancias_log_periodicas():
    """Verifica f_k = f_0 × 2^k con error < 2%."""
    ant = FractalAntenna(fractal_type='sierpinski', iterations=3,
                         base_freq=1.84e9, h=1.6e-3)
    resonancias = ant.resonant_frequencies
    f0 = ant.base_freq
    for k, f in enumerate(resonancias[:3]):
        f_esperada = f0 * (2.0 ** k)
        err = abs(f - f_esperada) / f_esperada * 100
        assert err < 2.0, f'Resonancia k={k}: {f/1e9:.3f} GHz vs esperada {f_esperada/1e9:.3f} GHz (err {err:.1f}%)'
        print(f'  [OK] Resonancia k={k}: {f/1e9:.3f} GHz')


# ═════════════════════════════════════════════════════════════════════════════
#  TEST 7 — PCE clip físico a 85 % (justificado en §2.6.3)
# ═════════════════════════════════════════════════════════════════════════════
def test_pce_clip_85pct():
    """Bloquea PCE_max = 0,85 incluso a P_in muy alto."""
    rectifier = RectifierCircuit(topology='doubler', R_load=1300.0)
    pce_high = rectifier.PCE(20.0, 2.45e9)   # 20 dBm = 100 mW (saturación)
    assert pce_high <= 0.851, f'PCE @ +20 dBm = {pce_high:.4f} (esperado ≤ 0,85)'
    assert pce_high >= 0.84,  f'PCE @ +20 dBm = {pce_high:.4f} (esperado ~0,85)'
    print(f'  [OK] PCE clip @ +20 dBm = {pce_high:.4f}')


# ═════════════════════════════════════════════════════════════════════════════
#  EJECUCIÓN DIRECTA
# ═════════════════════════════════════════════════════════════════════════════
def _run_all():
    tests = [
        test_diodo_sms7630_parametros,
        test_frecuencia_corte_sms7630,
        test_flpda_diseno_carrel,
        test_flpda_ganancia_550mhz,
        test_fspl_550mhz_100m,
        test_p_in_cerro_nutibara_100m,
        test_correccion_urbana_itu,
        test_cadena_potencia_canonica,
        test_validacion_wang2022_rmse,
        test_sierpinski_resonancias_log_periodicas,
        test_pce_clip_85pct,
    ]
    fail = 0
    print('═══════════════════════════════════════════════════════════════')
    print(' TEST DE REGRESIÓN — VALORES CANÓNICOS DE LA TESIS')
    print('═══════════════════════════════════════════════════════════════\n')
    for t in tests:
        try:
            print(f'▸ {t.__name__}')
            t()
            print()
        except AssertionError as e:
            print(f'  [FAIL] {e}')
            fail += 1
            print()
        except Exception as e:
            print(f'  [ERROR] {type(e).__name__}: {e}')
            fail += 1
            print()
    print('═══════════════════════════════════════════════════════════════')
    print(f' {len(tests)-fail}/{len(tests)} OK,  {fail} FALLOS')
    print('═══════════════════════════════════════════════════════════════')
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(_run_all())
