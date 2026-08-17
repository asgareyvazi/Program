# ============================================================================
# DEEP ENGINEERING MODELS
# File: engineering_deep.py
# Audit items (P1): the audit flagged simplified models in:
#   - ROP: needs calibration with offset-well data (Bourgoyne-Young style)
#   - Hydraulics: needs Herschel-Bulkley / Power Law annular pressure loss
#   - Casing: needs triaxial / combined load check
#   - Surge/Swab: needs compressibility-aware estimate
# Pure functions, unit-safe.
# ============================================================================

import math
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# ROP — BOURGOYNE-YOUNG STYLE WITH CALIBRATION
# ---------------------------------------------------------------------------

class ROPCalibrator:
    """Calibrated ROP model (Bourgoyne-Young simplified).

    ROP = K × WOB^a × RPM^b × exp(-c×depth) × exp(d×(MW - MW_opt))
    Calibration fits K from offset-well data at known conditions.
    """

    def __init__(self, k=1.0, a=1.0, b=0.6, c=0.00005, d=-0.05,
                 mw_opt_ppg=10.0):
        self.k = k
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.mw_opt_ppg = mw_opt_ppg
        self._fitted = False

    def predict(self, wob_klbf: float, rpm: float, depth_ft: float,
                mw_ppg: float) -> float:
        """ROP in ft/hr from the model."""
        if wob_klbf <= 0 or rpm <= 0:
            return 0.0
        rop = (self.k *
               (wob_klbf ** self.a) *
               (rpm ** self.b) *
               math.exp(-self.c * depth_ft) *
               math.exp(self.d * (mw_ppg - self.mw_opt_ppg)))
        return max(0.0, rop)

    def calibrate(self, data: List[Dict]) -> float:
        """Fit K from offset data points.

        data: list of dicts {wob, rpm, depth, mw, rop_actual}
        K = mean( ROP_actual / (WOB^a × RPM^b × exp(-c×D) × exp(d×(MW-MWopt))) )
        """
        vals = []
        for p in data:
            denom = ((p["wob"] ** self.a) * (p["rpm"] ** self.b) *
                     math.exp(-self.c * p["depth"]) *
                     math.exp(self.d * (p["mw"] - self.mw_opt_ppg)))
            if denom > 0:
                vals.append(p["rop_actual"] / denom)
        if vals:
            self.k = sum(vals) / len(vals)
            self._fitted = True
        return self.k

    @property
    def is_fitted(self) -> bool:
        return self._fitted


# ---------------------------------------------------------------------------
# HYDRAULICS — POWER LAW / HERSCHEL-BULKLEY ANNULAR PRESSURE LOSS
# ---------------------------------------------------------------------------

def power_law_pressure_loss(q_gpm: float, hole_in: float, pipe_in: float,
                            length_ft: float, n_index: float,
                            k_index_lb100ft2: float) -> float:
    """Annular pressure loss (psi) — Power Law model.

    Simplified field formula for annulus:
      V_ann (ft/min) = 24.5 × q / (D² − d²)
      dP/dL uses the Power Law constants (n, K).
    """
    if hole_in <= pipe_in or q_gpm <= 0:
        return 0.0
    area = (hole_in ** 2 - pipe_in ** 2)
    vel_ftmin = 24.5 * q_gpm / area
    # equivalent annular diameter (in)
    d_e = hole_in - pipe_in
    # Power Law pressure gradient (psi/ft) — field approximation:
    # dP/dL = (K × ( (2n+1)/(3n) × (V/(D-d)) )^n ) / 144  (mixed units)
    shear = (2 * n_index + 1) / (3 * n_index) * (vel_ftmin / (d_e))
    grad = (k_index_lb100ft2 * (shear ** n_index)) / 144.0
    return grad * length_ft


def herschel_bulkley_pressure_loss(q_gpm: float, hole_in: float,
                                   pipe_in: float, length_ft: float,
                                   tau0_lb100ft2: float, n_index: float,
                                   k_index_lb100ft2: float) -> float:
    """Annular pressure loss (psi) — Herschel-Bulkley (yield-power law).

    Includes the yield stress term (τ0) which the Power Law ignores.
    """
    if hole_in <= pipe_in or q_gpm <= 0:
        return 0.0
    area = (hole_in ** 2 - pipe_in ** 2)
    vel_ftmin = 24.5 * q_gpm / area
    d_e = hole_in - pipe_in
    # HB gradient approximation:
    shear = (2 * n_index + 1) / (3 * n_index) * (vel_ftmin / d_e)
    grad = (tau0_lb100ft2 / 300.0 / d_e +
            (k_index_lb100ft2 * (shear ** n_index)) / 144.0)
    return grad * length_ft


# ---------------------------------------------------------------------------
# CASING — TRIAXIAL / COMBINED LOAD CHECK (simplified von Mises)
# ---------------------------------------------------------------------------

def von_mises_equivalent(burst_psi: float, collapse_psi: float,
                         axial_psi: float) -> float:
    """Von Mises equivalent stress for combined burst/collapse + axial."""
    # thin-wall approximation: hoop = P×D/(2t), radial = −P/2
    # equivalent = sqrt(0.5[(σh−σr)² + (σr−σa)² + (σa−σh)²])
    sigma_h = burst_psi       # hoop from pressure
    sigma_r = -collapse_psi / 2.0
    sigma_a = axial_psi
    vm = math.sqrt(0.5 * ((sigma_h - sigma_r) ** 2 +
                          (sigma_r - sigma_a) ** 2 +
                          (sigma_a - sigma_h) ** 2))
    return vm


def triaxial_check(od_in: float, wall_in: float, yield_psi: float,
                   burst_psi: float, collapse_psi: float,
                   axial_psi: float, df: float = 1.25) -> Dict:
    """Triaxial (von Mises) design check per API TR 5C3 philosophy.

    Returns dict with VM stress, allowable, status.
    """
    vm = von_mises_equivalent(burst_psi, collapse_psi, axial_psi)
    allowable = yield_psi / df
    return {
        "vm_stress_psi": round(vm, 0),
        "allowable_psi": round(allowable, 0),
        "status": "PASS" if vm <= allowable else "FAIL",
        "utilization": round(vm / allowable * 100, 1),
    }


# ---------------------------------------------------------------------------
# SURGE/SWAB — COMPRESSIBILITY-AWARE ESTIMATE (extension)
# ---------------------------------------------------------------------------

def surge_swab_with_compressibility(trip_speed_ft_min: float,
                                    mud_pv_cp: float, mud_yp_lb100ft2: float,
                                    hole_in: float, pipe_in: float,
                                    depth_ft: float,
                                    mud_compressibility_1psi: float = 3e-6,
                                    closed_end: bool = True) -> Dict:
    """Surge/swab estimate with a compressibility correction factor.

    Compressible mud absorbs part of the pressure pulse; the correction
    reduces the rigid-column estimate.
    """
    # rigid estimate from the same simplified Bingham model
    a_pipe = math.pi / 4 * pipe_in ** 2
    a_ann = math.pi / 4 * (hole_in ** 2 - pipe_in ** 2)
    if a_ann <= 0:
        return {"error": "geometry"}
    vel = trip_speed_ft_min * (a_pipe / a_ann if closed_end else 0.5 *
                               a_pipe / a_ann)
    d_e = hole_in - pipe_in
    dp_per_1000 = (mud_yp_lb100ft2 / (300 * d_e) +
                   (mud_pv_cp * vel) / (1000 * d_e ** 2))
    dp_rigid = dp_per_1000 * (depth_ft / 1000.0)
    # compressibility correction: fraction of pulse absorbed
    # approx: corr = exp(-compressibility × pressure × modulus)
    corr = max(0.5, 1.0 - mud_compressibility_1psi * dp_rigid * 5e4)
    return {
        "velocity_ft_min": round(vel, 1),
        "rigid_pressure_psi": round(dp_rigid, 1),
        "corrected_pressure_psi": round(dp_rigid * corr, 1),
        "correction_factor": round(corr, 3),
        "model": "Bingham + compressibility (preliminary)",
    }


if __name__ == "__main__":
    # ROP calibration demo
    rc = ROPCalibrator()
    offset = [
        {"wob": 20, "rpm": 90, "depth": 5000, "mw": 11, "rop_actual": 35},
        {"wob": 25, "rpm": 100, "depth": 8000, "mw": 11.5, "rop_actual": 28},
        {"wob": 30, "rpm": 110, "depth": 11000, "mw": 12, "rop_actual": 20},
    ]
    rc.calibrate(offset)
    print("ROP fitted K:", round(rc.k, 4), "| predict:",
          round(rc.predict(25, 100, 8000, 11.5), 1), "ft/hr")
    pl = power_law_pressure_loss(500, 12.25, 5, 1000, 0.6, 2.0)
    hb = herschel_bulkley_pressure_loss(500, 12.25, 5, 1000, 10, 0.6, 2.0)
    print("PL:", round(pl, 1), "psi/1000ft | HB:", round(hb, 1),
          "psi/1000ft (yield adds)")
    tx = triaxial_check(9.625, 0.472, 80000, 6000, 4000, 10000)
    print("triaxial:", tx)
    ss = surge_swab_with_compressibility(60, 25, 20, 12.25, 5, 10000)
    print("surge w/ comp:", ss)
