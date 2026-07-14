"""Quick verification of canonical values via new models/ namespace."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__) + '/..')

from core.flpda import FLPDA_Koch
from core.rectifier import RectifierCircuit
from core.lora_budget import harvested_uw_full
from configs.parametros import CANONICAL, FLPDA_TAU, FLPDA_SIGMA, FLPDA_F_LOW_HZ, FLPDA_F_HIGH_HZ

flpda = FLPDA_Koch(tau=FLPDA_TAU, sigma=FLPDA_SIGMA,
                   f_low=FLPDA_F_LOW_HZ, f_high=FLPDA_F_HIGH_HZ, koch_iter=2)
rect  = RectifierCircuit('doubler', R_load=1300.0)
r     = harvested_uw_full(72.15, 100, 0.55, flpda, rect)

print(f"P_DC:  {r['P_dc_uW']:.1f} uW  (expected ~{CANONICAL['P_dc_uW']:.0f})")
print(f"gain:  {r['gain_dBi']:.2f} dBi (expected {CANONICAL['gain_dBi']:.2f})")
print(f"PCE:   {r['PCE']*100:.0f}%      (expected {CANONICAL['PCE']*100:.0f}%)")

assert abs(r['P_dc_uW'] - CANONICAL['P_dc_uW']) < 50, \
    f"P_DC mismatch: {r['P_dc_uW']:.1f} vs {CANONICAL['P_dc_uW']:.1f}"
assert abs(r['gain_dBi'] - CANONICAL['gain_dBi']) < 0.1, \
    f"Gain mismatch: {r['gain_dBi']:.2f} vs {CANONICAL['gain_dBi']:.2f}"

# Verify analysis functions accessible
from core.analysis import sensitivity_tornado, monte_carlo_pdc, supercap_sizing
from core.comparacion import validate_wang2022
print("models.analysis OK")
print("All verifications passed.")
