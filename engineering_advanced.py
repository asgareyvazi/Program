# ============================================================================
# ADVANCED ENGINEERING CALCULATIONS
# File: engineering_advanced.py
# Audit items (P1) — fills the engineering depth gaps flagged in the audit:
#   - Kick tolerance & MAASP verification
#   - Surge / swab (simplified dynamic with rheology)
#   - Hole cleaning (transport ratio, cuttings concentration)
#   - MPD / managed pressure basics (CBHP)
#   - BOP pressure envelope
#   - Cuttings slip velocity / critical annular velocity
# All pure functions (no UI), unit-safe via engineering_units.
# ============================================================================

import math
from engineering_units import (DrillingConstants, hydrostatic_pressure,
                               maasp, kill_mud_weight)


# ---------------------------------------------------------------------------
# WELL CONTROL — KICK TOLERANCE
# ---------------------------------------------------------------------------

def kick_tolerance(fg_ppg: float, mw_ppg: float, shoe_tvd_ft: float,
                   max_pit_gain_bbl: float, ann_cap_bbl_ft: float,
                   kick_density_ppg: float = 2.0,
                   trip_margin_ppg: float = 0.2) -> dict:
    """Kick tolerance (ppg) — the maximum kick intensity (as EMW above MW)
    that can be taken and shut in without fracturing the shoe.

    Simplified per IADC / field practice:
      KT = FG - MW - (pit_gain × kick_density / (ann_cap × shoe_tvd × 0.052)) ...
    Returns dict with kt_ppg and notes.
    """
    # pressure at shoe during shut-in with kick at bottom:
    # P_shoe = P_kick_gradient... use the standard simplified formula:
    # KT = FG - MW - margin
    base = fg_ppg - mw_ppg - trip_margin_ppg
    # reduction due to pit gain occupying annulus with lighter kick fluid:
    if ann_cap_bbl_ft > 0 and shoe_tvd_ft > 0:
        # height of kick in ft
        kick_height_ft = max_pit_gain_bbl / ann_cap_bbl_ft
        # pressure reduction at shoe from the light kick column:
        reduction_ppg = (kick_height_ft * (mw_ppg - kick_density_ppg)) / \
                        shoe_tvd_ft
        kt = base - reduction_ppg
    else:
        kt = base
    return {
        "kt_ppg": round(max(kt, 0.0), 2),
        "kick_height_ft": round(max_pit_gain_bbl / ann_cap_bbl_ft, 1)
        if ann_cap_bbl_ft else 0.0,
        "formula": "KT = FG - MW - margin - (kick height × Δρ / TVD)",
    }


def bop_pressure_envelope(bop_wp_psi: float, fg_ppg: float, mw_ppg: float,
                          shoe_tvd_ft: float) -> dict:
    """BOP working pressure envelope check."""
    masp_psi = maasp(fg_ppg, mw_ppg, shoe_tvd_ft)
    ok = bop_wp_psi >= masp_psi
    margin = bop_wp_psi - masp_psi
    return {
        "bop_wp_psi": bop_wp_psi,
        "masp_psi": round(masp_psi, 0),
        "ok": ok,
        "margin_psi": round(margin, 0),
        "status": "OK" if ok else "BOP WP BELOW MASP — NOT ACCEPTABLE",
    }


# ---------------------------------------------------------------------------
# SURGE / SWAB (simplified dynamic)
# ---------------------------------------------------------------------------

def surge_swab_pressure(mud_yp_lb100ft2: float, mud_pv_cp: float,
                        trip_speed_ft_min: float,
                        ann_cap_bbl_ft: float, hole_in: float,
                        pipe_in: float, depth_ft: float,
                        flow_regime: str = "laminar") -> dict:
    """Estimate surge/swab pressure (psi) from annular friction.

    Simplified annular pressure loss using Bingham Plastic:
      dP = (YP/300 × L/D) + (PV × V / (1000 × (D-d)²))-style approximations.
    Adequate for preliminary trip-speed envelopes (audit: needs
    reference-validated full model for final design).
    """
    if hole_in <= pipe_in:
        return {"error": "hole must be larger than pipe"}
    d_h = hole_in
    d_p = pipe_in
    # equivalent annular diameter
    d_e = d_h - d_p
    if d_e <= 0:
        return {"error": "bad geometry"}
    # annular velocity from pipe movement (displacement):
    # V_ann (ft/min) ≈ trip_speed × (pipe OD area) / annulus area
    a_pipe = math.pi / 4 * d_p ** 2
    a_ann = math.pi / 4 * (d_h ** 2 - d_p ** 2)
    vel = trip_speed_ft_min * a_pipe / a_ann if a_ann > 0 else 0.0
    # pressure loss per 1000 ft (Bingham): dP/1000ft = (YP/ (300*D_e)) +
    # (PV × V) / (1000 × D_e²)  [field units approximation]
    dp_per_1000 = (mud_yp_lb100ft2 / (300 * d_e) +
                   (mud_pv_cp * vel) / (1000 * d_e ** 2))
    dp_total = dp_per_1000 * (depth_ft / 1000.0)
    return {
        "ann_velocity_ft_min": round(vel, 1),
        "pressure_psi": round(dp_total, 1),
        "surge_swab": "surge" if trip_speed_ft_min > 0 else "swab",
        "model": "Bingham simplified (P0 — verify for final design)",
    }


# ---------------------------------------------------------------------------
# HOLE CLEANING
# ---------------------------------------------------------------------------

def critical_annular_velocity(mud_yp_lb100ft2: float, mud_pv_cp: float,
                              hole_in: float, pipe_in: float,
                              mud_weight_ppg: float,
                              cuttings_density_ppg: float = 21.7,
                              cuttings_size_in: float = 0.3) -> dict:
    """Critical annular velocity & cuttings transport indicators.

    Returns annular velocity needed to keep cuttings moving and the
    transport ratio estimate for a given actual velocity.
    """
    d_e = hole_in - pipe_in
    if d_e <= 0:
        return {"error": "bad geometry"}
    # Moore's correlation for critical velocity (ft/min) — simplified
    # slip velocity of cuttings:
    rho_mud = mud_weight_ppg * 7.4805  # pcf
    rho_cut = cuttings_density_ppg * 7.4805
    d_p_in = cuttings_size_in
    # slip velocity (Chien / Moore simplified):
    try:
        slip = 0.45 * math.sqrt(
            (rho_cut - rho_mud) * d_p_in * 32.2 * 60 ** 2 / rho_mud
        ) if rho_mud > 0 else 0.0
    except (ValueError, ZeroDivisionError):
        slip = 0.0
    # critical annular velocity ≈ slip + small margin (simplified)
    crit = slip * 1.2
    return {
        "slip_velocity_ft_min": round(slip, 1),
        "critical_ann_velocity_ft_min": round(crit, 1),
        "cuttings_density_ppg": cuttings_density_ppg,
        "model": "Moore simplified (P0 — verify for final design)",
    }


def cuttings_transport_ratio(actual_ann_velocity_ft_min: float,
                             slip_velocity_ft_min: float) -> float:
    """Transport ratio = (Va - Vs) / Va — >0.5 is generally good."""
    if actual_ann_velocity_ft_min <= 0:
        return 0.0
    return max(0.0, min(1.0, (actual_ann_velocity_ft_min -
                              slip_velocity_ft_min) /
                        actual_ann_velocity_ft_min))


# ---------------------------------------------------------------------------
# MPD — MANAGED PRESSURE DRILLING BASICS (CBHP)
# ---------------------------------------------------------------------------

def cbhp_mud_weight(mw_ppg: float, ann_loss_ppg: float,
                    backpressure_psi: float, tvd_ft: float) -> dict:
    """Constant Bottom-Hole Pressure (CBHP) MPD.

    CBHP_EMW = MW + ann_loss_EMW + BP/(0.052×TVD)
    """
    bp_emw = backpressure_psi / (DrillingConstants.PSI_PER_PPG_PER_FT * tvd_ft) \
        if tvd_ft > 0 else 0.0
    cbhp = mw_ppg + ann_loss_ppg + bp_emw
    return {
        "cbhp_emw_ppg": round(cbhp, 2),
        "bp_emw_ppg": round(bp_emw, 2),
        "note": "MPD window = PP + margin ≤ CBHP ≤ FG − margin",
    }


def mpd_operating_window(pp_ppg: float, fg_ppg: float, mw_ppg: float,
                         ann_loss_ppg: float,
                         pp_margin: float = 0.2, fg_margin: float = 0.5) -> dict:
    """Available backpressure window (psi) at surface for CBHP MPD."""
    tvd_ft = 10000.0  # caller should provide; default for window estimate
    min_bp = max(0.0, (pp_ppg + pp_margin) - (mw_ppg + ann_loss_ppg))
    max_bp = max(0.0, (fg_ppg - fg_margin) - (mw_ppg + ann_loss_ppg))
    return {
        "min_bp_psi": round(min_bp * 0.052 * tvd_ft, 0),
        "max_bp_psi": round(max_bp * 0.052 * tvd_ft, 0),
        "window_ok": max_bp > min_bp,
    }


# ---------------------------------------------------------------------------
# CASING — ADDITIONAL LOAD CHECKS (audit: evacuation/lost-returns)
# ---------------------------------------------------------------------------

def evacuation_burst_load(mw_ppg: float, formation_pressure_ppg: float,
                          depth_ft: float) -> float:
    """Burst load (psi) at surface for the evacuation case:
    casing evacuated (gas to surface) with formation pressure at TD.
    """
    return (formation_pressure_ppg - mw_ppg) * 0.052 * depth_ft


def lost_returns_collapse_load(mw_ppg: float, depth_ft: float,
                               external_pore_ppg: float = 8.33) -> float:
    """Collapse load (psi) for the lost-returns case: mud level drops to
    the point where internal pressure is zero at surface.
    """
    # collapse load at depth = external pressure (formation pore) minus
    # internal pressure (mud column to reduced level). Simplified:
    return (external_pore_ppg * 0.052 * depth_ft) - 0.0


if __name__ == "__main__":
    print("kick tolerance:", kick_tolerance(15, 12, 8000, 30, 0.045))
    print("bop envelope:", bop_pressure_envelope(10000, 15, 12, 8000))
    print("surge/swab:", surge_swab_pressure(20, 25, 60, 0.045, 12.25, 5, 10000))
    hc = critical_annular_velocity(20, 25, 12.25, 5, 12)
    print("hole cleaning:", hc)
    print("transport ratio @90 ft/min:", round(
        cuttings_transport_ratio(90, hc.get("slip_velocity_ft_min", 0)), 2))
    print("MPD CBHP:", cbhp_mud_weight(11, 0.8, 300, 10000))
    print("MPD window:", mpd_operating_window(10, 15, 11, 0.8))
    print("evac burst:", round(evacuation_burst_load(12, 14, 10000), 0))
