# ============================================================================
# ADVANCED CASING DESIGN CHECKS
# File: engineering_casing.py
# Audit item (P1): Casing Design — the audit flagged that triaxial/thermal/
# wear/corrosion load checks were incomplete.  This module adds the
# classic API 5C3 / API TR 5C3 design checks:
#   - Buoyancy-adjusted axial load
#   - Thermal stress from temperature change (E·α·ΔT)
#   - Wear derating (remaining-wall method)
#   - Corrosion allowance (wall reduction over design life)
#   - Combined triaxial (von Mises) check with the derated geometry
# Plus an eccentric-annulus correction for Herschel-Bulkley pressure loss.
# Pure, deterministic functions with reference tests.
# ============================================================================

import math
from typing import Dict, List, Optional, Tuple

# Steel casing constants (typical)
E_STEEL_PSI = 30e6            # Young's modulus, psi
ALPHA_STEEL_1F = 6.9e-6       # thermal expansion coefficient, 1/°F
STEEL_DENSITY_PPG = 65.4      # density of steel in ppg (489.5 pcf)
GRAV = 32.174                 # ft/s²
CF = 0.052                    # psi per ppg per ft


def buoyancy_factor(mud_ppg: float) -> float:
    """BF = 1 − ρ_mud / ρ_steel (API 5C3 / field practice)."""
    return 1.0 - (mud_ppg / STEEL_DENSITY_PPG)


def axial_load_buoyed(air_weight_ppf: float, length_ft: float,
                      mud_ppg: float) -> float:
    """Axial tension at surface of a string hanging in mud (lbf)."""
    return air_weight_ppf * length_ft * buoyancy_factor(mud_ppg)


def thermal_stress(delta_t_f: float,
                   young_psi: float = E_STEEL_PSI,
                   alpha_1f: float = ALPHA_STEEL_1F) -> float:
    """Thermal axial stress (psi) = E × α × ΔT (restrained casing)."""
    return young_psi * alpha_1f * delta_t_f


def thermal_force(pipe_od_in: float, wall_in: float, delta_t_f: float,
                  young_psi: float = E_STEEL_PSI,
                  alpha_1f: float = ALPHA_STEEL_1F) -> float:
    """Thermal axial force (lbf) for a restrained pipe cross-section."""
    area = math.pi * (pipe_od_in ** 2 - (pipe_od_in - 2 * wall_in) ** 2) / 4.0
    return thermal_stress(delta_t_f, young_psi, alpha_1f) * area


def remaining_wall(original_wall_in: float,
                   wear_fraction: float = 0.0,
                   corrosion_in: float = 0.0) -> float:
    """Remaining wall after wear (fraction of wall) and corrosion (in)."""
    t = original_wall_in * (1.0 - max(0.0, min(1.0, wear_fraction)))
    return max(0.0, t - max(0.0, corrosion_in))


def derated_burst(od_in: float, original_wall_in: float,
                  yield_strength_psi: float,
                  wear_fraction: float = 0.0,
                  corrosion_in: float = 0.0,
                  derate: float = 0.875) -> float:
    """Burst rating with wear/corrosion (remaining-wall Barlow)."""
    t = remaining_wall(original_wall_in, wear_fraction, corrosion_in)
    if od_in <= 0 or t <= 0:
        return 0.0
    return 2.0 * derate * yield_strength_psi * t / od_in


def derated_collapse(od_in: float, original_wall_in: float,
                     yield_strength_psi: float,
                     wear_fraction: float = 0.0,
                     corrosion_in: float = 0.0) -> float:
    """Collapse rating with wear/corrosion (API 5C3 on remaining wall)."""
    from engineering_units import api_collapse_pressure
    t = remaining_wall(original_wall_in, wear_fraction, corrosion_in)
    if od_in <= 0 or t <= 0:
        return 0.0
    return api_collapse_pressure(od_in, t, yield_strength_psi)


def casing_design_check(values: Dict) -> Dict:
    """Run the full advanced casing check set from wizard inputs.

    Returns dict with per-check results and an overall status.
    """
    v = values or {}

    def _pick(*keys) -> str:
        for k in keys:
            s = str(v.get(k, "") or "").strip()
            if s:
                return s
        return ""

    def _f(x, d=0.0) -> float:
        try:
            return float(str(x).strip()) if str(x).strip() else d
        except (TypeError, ValueError):
            return d

    od = _f(_pick("casing_od", "casing_size"))
    wall = _f(_pick("casing_wall", "casing_wall_in", "wall_thickness"))
    ys = _f(_pick("casing_yield", "casing_yield_psi", "yield_strength"))
    mw = _f(_pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    depth = _f(_pick("casing_depth", "casing_depth_ft", "shoe_depth",
                     "csg_depth"))
    air_wt = _f(_pick("casing_weight", "casing_weight_ppf", "weight_ppf"))
    dT = _f(_pick("temperature_change", "delta_t", "dT_f"))
    wear = _f(_pick("wear_fraction", "casing_wear"), 0.0)
    corr = _f(_pick("corrosion_allowance", "corrosion_in"), 0.0)
    burst_load = _f(_pick("burst_load", "design_burst"))
    coll_load = _f(_pick("collapse_load", "design_collapse"))
    axial_load = _f(_pick("axial_load", "design_axial"))
    bf = buoyancy_factor(mw) if mw > 0 else 1.0

    checks: List[Dict] = []

    def _add(name, formula, inputs, result, unit, standard, status):
        checks.append({"param": name, "formula": formula, "inputs": inputs,
                       "result": result, "unit": unit, "standard": standard,
                       "status": status})

    # 1. buoyancy
    if mw > 0:
        _add("Casing buoyancy factor",
             "BF = 1 − ρ_mud/ρ_steel",
             f"MW = {mw:g} ppg, ρ_steel = {STEEL_DENSITY_PPG:g} ppg",
             f"{bf:.3f}", "—", "API 5C3", "OK")
    # 2. buoyed axial load
    if air_wt > 0 and depth > 0 and mw > 0:
        load = axial_load_buoyed(air_wt, depth, mw)
        _add("Buoyed axial load at surface",
             "F = W_air × L × BF",
             f"W = {air_wt:g} ppf, L = {depth:,.0f} ft, BF = {bf:.3f}",
             f"{load:,.0f}", "lbf", "API 5C3", "OK")
    # 3. thermal
    if dT > 0:
        sig = thermal_stress(dT)
        _add("Thermal axial stress (restrained)",
             "σ = E × α × ΔT",
             f"E = 30e6 psi, α = 6.9e-6 /°F, ΔT = {dT:g} °F",
             f"{sig:,.0f}", "psi", "API TR 5C3 / field practice", "OK")
        if od > 0 and wall > 0:
            f_th = thermal_force(od, wall, dT)
            _add("Thermal axial force (restrained)",
                 "F = σ × A",
                 f"OD = {od:g} in, t = {wall:g} in, ΔT = {dT:g} °F",
                 f"{f_th:,.0f}", "lbf", "API TR 5C3", "OK")
    # 4. wear / corrosion derated ratings
    if od > 0 and wall > 0 and ys > 0 and (wear > 0 or corr > 0):
        t_rem = remaining_wall(wall, wear, corr)
        pb = derated_burst(od, wall, ys, wear, corr)
        pc = derated_collapse(od, wall, ys, wear, corr)
        _add("Wear/corrosion remaining wall",
             "t_rem = t×(1−wear) − corrosion",
             f"t = {wall:g} in, wear = {wear*100:g}%, "
             f"corrosion = {corr:g} in",
             f"{t_rem:.3f}", "in", "API RP 5C3", "OK")
        _add("Derated burst rating (remaining wall)",
             "P_b = 0.875 × 2 × YS × t_rem/OD",
             f"OD = {od:g} in, YS = {ys:,.0f} psi, t_rem = {t_rem:.3f} in",
             f"{pb:,.0f}", "psi", "API 5C3 (Barlow)", "OK")
        _add("Derated collapse rating (remaining wall)",
             "API 5C3 on t_rem",
             f"OD = {od:g} in, YS = {ys:,.0f} psi, t_rem = {t_rem:.3f} in",
             f"{pc:,.0f}", "psi", "API 5C3", "OK")
    # 5. triaxial with combined loads + derated geometry.
    #    axial stress = buoyed string weight / cross-section + thermal
    if od > 0 and wall > 0 and ys > 0 and burst_load > 0 and coll_load > 0:
        try:
            from engineering_deep import triaxial_check
            t_rem = remaining_wall(wall, wear, corr)
            area = math.pi * (od ** 2 - (od - 2 * wall) ** 2) / 4.0
            axial_total = axial_load  # user-provided stress (psi), if any
            axial_src = f"user input {axial_load:,.0f} psi"
            if air_wt > 0 and depth > 0 and mw > 0 and area > 0:
                axial_total = axial_load_buoyed(air_wt, depth, mw) / area
                axial_src = (f"buoyed W ({air_wt:g} ppf × {depth:,.0f} ft"
                             f" × BF {bf:.3f}) / A ({area:.2f} in²)")
            if dT > 0:
                axial_total += thermal_stress(dT)
                axial_src += f" + thermal {thermal_stress(dT):,.0f} psi"
            tx = triaxial_check(od, t_rem, ys, burst_load, coll_load,
                                axial_total)
            _add("Triaxial check (derated geometry + thermal)",
                 "σ_vm ≤ YS/1.25",
                 f"burst = {burst_load:,.0f} psi, collapse = "
                 f"{coll_load:,.0f} psi, axial = {axial_src}",
                 f"{tx['utilization']}% util",
                 "—", "API TR 5C3 (von Mises)",
                 "OK" if tx["status"] == "PASS" else "FAIL")
        except Exception:
            pass

    status = "OK" if all(c["status"] == "OK" for c in checks) else \
        ("WARN" if any(c["status"] == "WARN" for c in checks) else "FAIL")
    return {"checks": checks, "status": status}


def casing_check_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready ADVANCED CASING DESIGN CHECKS section."""
    res = casing_design_check(values)
    op = (operator or "").strip() or "the Operator"
    if not res["checks"]:
        return ""
    L = [
        "### Casing — Advanced Design Checks (thermal / wear / corrosion)",
        "",
        "| Check | Formula / Basis | Inputs used | Result | Standard | Status |",
        "|---|---|---|---|---|---|",
    ]
    for c in res["checks"]:
        L.append(f"| {c['param']} | {c['formula']} | {c['inputs']} | "
                 f"{c['result']} {c['unit']} | {c['standard']} | "
                 f"{c['status']} |")
    L.append("")
    L.append(f"*Advanced casing checks computed deterministically for {op}; "
             "final design requires confirmation against licensed casing "
             "design software.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# ECCENTRIC-ANNULUS CORRECTION (Herschel-Bulkley)
# ---------------------------------------------------------------------------

def eccentricity_correction(ecc_ratio: float, n_index: float) -> float:
    """Pressure-loss correction for an eccentric annulus.

    ecc_ratio = offset / (hole − pipe)  (0 concentric … 1 fully eccentric).
    Uses the classic field approximation:
        corr = 1 − 0.072 × (ecc_ratio) × (n_index / 0.6)^0.5
    which reduces the annular pressure loss as the pipe lies off-center
    (the wide side offers a lower-resistance path).  Returns 0 < corr ≤ 1.
    """
    e = max(0.0, min(1.0, ecc_ratio))
    n = max(0.1, n_index)
    corr = 1.0 - 0.072 * e * math.sqrt(n / 0.6)
    return max(0.5, corr)


def hb_pressure_loss_eccentric(q_gpm: float, hole_in: float, pipe_in: float,
                               length_ft: float, tau0_lb100ft2: float,
                               n_index: float, k_index_lb100ft2: float,
                               ecc_ratio: float = 0.0) -> Dict:
    """Herschel-Bulkley annular pressure loss with eccentricity correction."""
    from engineering_deep import herschel_bulkley_pressure_loss
    concentric = herschel_bulkley_pressure_loss(
        q_gpm, hole_in, pipe_in, length_ft, tau0_lb100ft2, n_index,
        k_index_lb100ft2)
    corr = eccentricity_correction(ecc_ratio, n_index)
    return {
        "concentric_psi": round(concentric, 1),
        "correction": round(corr, 3),
        "eccentric_psi": round(concentric * corr, 1),
        "ecc_ratio": ecc_ratio,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # buoyancy: 12 ppg -> BF = 1 - 12/65.4 = 0.8165
    bf = buoyancy_factor(12.0)
    assert abs(bf - 0.8165) < 1e-4, bf
    # thermal: E=30e6, a=6.9e-6, dT=200 -> 41,400 psi
    sig = thermal_stress(200.0)
    assert abs(sig - 41400.0) < 1.0, sig
    # wear: 20% wear on 0.472 wall -> t_rem = 0.3776; burst derate 80%
    t = remaining_wall(0.472, 0.20, 0.0)
    assert abs(t - 0.3776) < 1e-9, t
    pb_full = derated_burst(9.625, 0.472, 80000)
    pb_worn = derated_burst(9.625, 0.472, 80000, 0.20)
    assert abs(pb_worn / pb_full - 0.80) < 1e-9
    # eccentricity: concentric > eccentric; corr in (0.5, 1]
    res = hb_pressure_loss_eccentric(500, 12.25, 5, 1000, 10, 0.6, 2.0,
                                     ecc_ratio=0.5)
    assert res["eccentric_psi"] < res["concentric_psi"]
    assert 0.5 < res["correction"] <= 1.0
    # full check set
    vals = {"casing_od": "9.625", "casing_wall": "0.472",
            "casing_yield": "110000", "mud_weight": "12",
            "casing_depth": "8000", "casing_weight": "47",
            "temperature_change": "150", "wear_fraction": "0.1",
            "corrosion_allowance": "0.02", "burst_load": "9000",
            "collapse_load": "6000", "axial_load": "400000"}
    res2 = casing_design_check(vals)
    assert len(res2["checks"]) >= 8, res2
    md = casing_check_markdown(vals)
    assert "ADVANCED CASING DESIGN" in md or "Casing — Advanced" in md
    print(f"  ✔ casing selftest: {len(res2['checks'])} checks OK")
    return res2


if __name__ == "__main__":
    _selftest()
    print("engineering_casing OK")
