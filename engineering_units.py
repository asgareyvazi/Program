# ============================================================================
# ENGINEERING UNITS — dimension-safe unit system
# File: engineering_units.py
# P0 audit item: prevent psi/bar, ft/m, ppg/sg mix-ups in core engineering.
# Every engineering module should convert through this registry so values
# are stored in canonical SI/field units and displayed in user units.
# ============================================================================

from typing import Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# DIMENSIONS and base conversion factors (canonical base per dimension)
# ---------------------------------------------------------------------------

# canonical base: pressure=psi, density=ppg, length=ft, volume=bbl,
# flow=gpm, force=lbf, torque=ft-lb, temp=degF, time=hr, rop=ft/hr
_CONV: Dict[str, Dict[str, float]] = {
    "pressure": {"psi": 1.0, "bar": 14.5038, "kpa": 0.145038, "mpa": 145.038,
                 "atm": 14.6959, "kpa*": 0.145038},
    "density": {"ppg": 1.0, "pcf": 0.13368, "sg": 8.3454, "kg/m3": 0.0083454,
                "kg/m³": 0.0083454, "g/cm3": 834.54, "g/cc": 834.54},
    "length": {"ft": 1.0, "m": 3.28084, "in": 0.0833333, "km": 3280.84,
               "mm": 0.00328084, "cm": 0.0328084},
    "volume": {"bbl": 1.0, "m3": 6.28981, "m³": 6.28981, "gal": 0.0238095,
               "l": 0.00628981, "L": 0.00628981},
    "flow": {"gpm": 1.0, "lpm": 0.264172, "m3/hr": 4.40287, "m³/hr": 4.40287,
             "l/s": 15.8503, "bpm": 42.0},
    "force": {"lbf": 1.0, "kn": 224.809, "kN": 224.809, "kgf": 2.20462,
              "tonf": 2240.0, "kip": 1000.0},
    "torque": {"ft-lb": 1.0, "n-m": 0.737562, "N·m": 0.737562,
               "kN-m": 737.562, "kN·m": 737.562},
    "rop": {"ft/hr": 1.0, "m/hr": 3.28084},
    "time": {"hr": 1.0, "min": 0.0166667, "day": 24.0, "s": 0.000277778},
    "rate": {"usd/day": 1.0, "usd/hr": 24.0, "usd/month": 0.032854},
}

# temperature needs special handling (offset)
_TEMP_OFFSET = {"degf": 0.0, "degc": 32.0, "k": -459.67}

# dimension -> canonical display unit
_CANONICAL = {"pressure": "psi", "density": "ppg", "length": "ft",
              "volume": "bbl", "flow": "gpm", "force": "lbf",
              "torque": "ft-lb", "rop": "ft/hr", "time": "hr",
              "rate": "usd/day"}

# unit -> dimension lookup (built once)
_UNIT_DIM: Dict[str, str] = {}
for dim, table in _CONV.items():
    for unit in table:
        _UNIT_DIM[unit.lower()] = dim
for unit in _TEMP_OFFSET:
    _UNIT_DIM[unit.lower()] = "temperature"


def dimension_of(unit: str) -> Optional[str]:
    """Return the dimension of a unit string (case-insensitive)."""
    return _UNIT_DIM.get(str(unit).strip().lower())


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a value between units of the same dimension.

    Raises ValueError on unknown unit or dimension mismatch.
    """
    f = str(from_unit).strip().lower()
    t = str(to_unit).strip().lower()
    if f == t:
        return value
    dim = _UNIT_DIM.get(f)
    if dim is None:
        raise ValueError(f"Unknown unit: {from_unit}")
    if _UNIT_DIM.get(t) != dim:
        raise ValueError(f"Unit mismatch: {from_unit} ({dim}) vs "
                         f"{to_unit} ({_UNIT_DIM.get(t)})")
    if dim == "temperature":
        # both in Fahrenheit-equivalent scale
        return value + (_TEMP_OFFSET[f] - _TEMP_OFFSET[t])
    return value * (_CONV[dim][f] / _CONV[dim][t])


def to_canonical(value: float, unit: str) -> float:
    """Convert to the canonical base unit of the dimension."""
    return convert(value, unit, _CANONICAL[_UNIT_DIM[str(unit).lower()]])


def from_canonical(value: float, unit: str) -> float:
    """Convert from the canonical base unit to the given unit."""
    return convert(value, _CANONICAL[_UNIT_DIM[str(unit).lower()]], unit)


def canonical_unit(dim: str) -> str:
    return _CANONICAL.get(dim, dim)


# ---------------------------------------------------------------------------
# ENGINEERING CONSTANTS (field-standard)
# ---------------------------------------------------------------------------

class DrillingConstants:
    """Standard constants used across calculations (API / field practice)."""
    PSI_PER_PPG_PER_FT = 0.052          # hydrostatic gradient
    PSI_PER_PCF_PER_FT = 0.006944       # 0.052 / 7.4805
    BAR_PER_M_PER_SG = 0.0981           # 0.0981 bar/m per SG
    KPA_PER_M_PER_SG = 9.81
    GPM_PER_FT2_AV = 24.5               # annular velocity factor
    BBL_PER_FT_ANNULAR = 0.0            # depends on geometry
    BBL_PER_BBL_MUD_PER_SACK = 0.0
    GAS_CONSTANT = 10.73                # psi·ft3/lb-mol·R
    STROKE_FACTOR = 0.0

    # design factors (typical minimums — configurable)
    BURST_DF = 1.1
    COLLAPSE_DF = 1.125
    TENSION_DF = 1.6
    KICK_MARGIN_PPG = 0.5               # typical overbalance above pore pressure
    TRIP_MARGIN_PPG = 0.5
    SURGE_SWAB_MARGIN_PPG = 0.5
    FIT_MARGIN_PPG = 0.5                # above max planned MW for next section


def hydrostatic_pressure(mw_ppg: float, depth_ft: float) -> float:
    """Hydrostatic pressure (psi) = 0.052 × MW (ppg) × depth (ft)."""
    return DrillingConstants.PSI_PER_PPG_PER_FT * mw_ppg * depth_ft


def emw_from_pressure(pressure_psi: float, depth_ft: float) -> float:
    """Equivalent mud weight (ppg) from a pressure at a depth."""
    if depth_ft <= 0:
        return 0.0
    return pressure_psi / (DrillingConstants.PSI_PER_PPG_PER_FT * depth_ft)


def maasp(fg_ppg: float, mw_ppg: float, shoe_depth_ft: float) -> float:
    """Maximum Allowable Annular Surface Pressure (psi)."""
    return (fg_ppg - mw_ppg) * DrillingConstants.PSI_PER_PPG_PER_FT * shoe_depth_ft


def kill_mud_weight(sidpp_psi: float, tvd_ft: float, current_mw_ppg: float,
                    trip_margin_ppg: float = 0.0) -> float:
    """Kill mud weight (ppg) from SIDPP."""
    return current_mw_ppg + sidpp_psi / (DrillingConstants.PSI_PER_PPG_PER_FT * tvd_ft) \
        + trip_margin_ppg


def annular_velocity_ftmin(gpm: float, hole_in: float, pipe_in: float) -> float:
    """Annular velocity (ft/min) = 24.5 × gpm / (D² - d²)."""
    area = hole_in ** 2 - pipe_in ** 2
    if area <= 0:
        raise ValueError("Hole ID must be larger than pipe OD")
    return DrillingConstants.GPM_PER_FT2_AV * gpm / area


def barlow_burst_pressure(od_in: float, wall_in: float, yield_strength_psi: float,
                          derate: float = 0.875) -> float:
    """Burst pressure (psi) — Barlow with 87.5% wall derating (API)."""
    if od_in <= 0 or wall_in <= 0:
        return 0.0
    return 2.0 * derate * yield_strength_psi * wall_in / od_in


def _api_collapse_regime(od_in: float, wall_in: float, ys_psi: float,
                         e_psi: float = 30e6) -> Tuple[str, float]:
    """Return (regime, value) per API 5C3 collapse equations.

    Simplified implementation of the four collapse regimes — adequate for
    reference testing and preliminary design (P0 reference suite).
    """
    t = wall_in
    D = od_in
    d = D - 2 * t
    Dt = D / t
    F1, F2, F3, F4 = 1.989, 1.047, 1.779, 1.108  # grade-independent for this impl
    G = F1 if ys_psi <= 80000 else (F2 if ys_psi <= 110000 else (F3 if ys_psi <= 150000 else F4))
    A = 2.8762 + 0.10679e-3 * G * ys_psi + 0.21301e-6 * G * ys_psi ** 2 \
        - 0.53132e-10 * G * ys_psi ** 3
    B = 0.026233 + 0.50609e-6 * G * ys_psi
    C = -465.93 + 0.030867 * G * ys_psi - 0.10483e-7 * G * ys_psi ** 2 \
        + 0.36989e-13 * G * ys_psi ** 3
    # yield collapse
    p_yield = 2 * ys_psi * (t / D)
    # plastic collapse
    p_plast = ys_psi * (A / Dt - B) - C
    # transition
    p_trans = ys_psi * (F1 / Dt - G)
    # elastic
    p_elast = (46.95e6) / (Dt * (Dt - 1) ** 2)
    regime = "yield"
    val = p_yield
    # find the governing regime by the standard's ordering:
    candidates = [
        ("yield", p_yield, Dt <= (A - 2 * B) / (2 * B) if B else True),
        ("plastic", p_plast, True),
        ("transition", p_trans, True),
        ("elastic", p_elast, True),
    ]
    # API logic: take the smallest applicable pressure
    vals = [(r, p) for r, p, _ in candidates if p > 0]
    if vals:
        regime, val = min(vals, key=lambda x: x[1])
    return regime, val


def api_collapse_pressure(od_in: float, wall_in: float,
                          yield_strength_psi: float) -> float:
    """Collapse pressure (psi) per API 5C3 (simplified four regimes)."""
    return _api_collapse_regime(od_in, wall_in, yield_strength_psi)[1]


if __name__ == "__main__":
    # quick self-checks
    assert abs(convert(1, "bar", "psi") - 14.5038) < 1e-3
    assert abs(convert(1, "m", "ft") - 3.28084) < 1e-4
    assert abs(convert(1000, "m", "ft") - 3280.84) < 0.01
    assert abs(hydrostatic_pressure(12, 10000) - 6240) < 1e-9
    assert abs(annular_velocity_ftmin(500, 12.25, 5) - 97.95) < 0.5
    print("engineering_units self-check OK")
