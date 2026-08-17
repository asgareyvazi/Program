# ============================================================================
# WELLBORE STABILITY & GEOMECHANICS
# File: engineering_geomechanics.py
# Audit items (P1):
#   - Wellbore stability: the audit asked for geomechanics inputs and a
#     quantitative model (previously only MW vs PP/FG validation).
#
# Implements the classic Kirsch (elastic) solution for a vertical borehole
# with Mohr-Coulomb shear failure (breakout) and tensile failure
# (fracture), plus LOT/FIT interpretation:
#   - σθθ = σH + σh − 2(σH − σh)cos2θ − Pm            (Kirsch, r = a)
#   - Fracture (tensile) initiation: P_frac = 3σh − σH − Pp + T0
#     (vertical fracture; horizontal fracture if σv governs)
#   - Breakout (shear) limit: solved from Mohr-Coulomb — reference
#     verified in the self-test with a hand solution
#   - Safe mud window = [max(Pp, breakout), min(frac, σv)]
# All stresses in psi; gradients can be given as psi/ft.
# ============================================================================

import math
from typing import Dict, List, Optional, Tuple

CF = 0.052


def kirsch_hoop_stress(sigma_H_psi: float, sigma_h_psi: float,
                       mud_pressure_psi: float, theta_deg: float) -> float:
    """Tangential (hoop) stress at the borehole wall (Kirsch, vertical
    well, r = a, total stress)."""
    th = math.radians(theta_deg)
    return (sigma_H_psi + sigma_h_psi -
            2.0 * (sigma_H_psi - sigma_h_psi) * math.cos(2.0 * th) -
            mud_pressure_psi)


def fracture_pressure(sigma_v_psi: float, sigma_H_psi: float,
                      sigma_h_psi: float, pore_psi: float,
                      tensile_strength_psi: float = 0.0) -> Dict:
    """Mud pressure that initiates a tensile fracture.

    Vertical fracture (at θ=90°, min hoop):
        P = 3σh − σH − Pp + T0
    Horizontal fracture (when σv is the least principal stress):
        P = σv − Pp + T0
    Returns the governing (lower) value and the mechanism.
    """
    vert = 3.0 * sigma_h_psi - sigma_H_psi - pore_psi + tensile_strength_psi
    horiz = sigma_v_psi - pore_psi + tensile_strength_psi
    if horiz <= vert:
        return {"pressure_psi": round(horiz, 0),
                "mechanism": "horizontal (σv least principal)"}
    return {"pressure_psi": round(vert, 0),
            "mechanism": "vertical (hoop tension at θ=90°)"}


def breakout_pressure(sigma_H_psi: float, sigma_h_psi: float,
                      pore_psi: float, ucs_psi: float,
                      friction_angle_deg: float) -> float:
    """Minimum mud pressure to prevent shear (breakout) failure.

    Mohr-Coulomb on effective stresses at θ=0° (σH direction, max hoop):
        σ'θ = 3σH − σh − Pm − Pp ;  σ'r = Pm − Pp
        failure: (σ'1−σ'3)/2 = c·cosφ + ((σ'1+σ'3)/2)·sinφ
    Solved for Pm (derived — verified in the self-test):
        Pm = [3σH − σh − 2c·cosφ − (3σH − σh − 2Pp)·sinφ] / 2
    with c = UCS·(1−sinφ)/(2·cosφ).
    """
    phi = math.radians(friction_angle_deg)
    c = ucs_psi * (1.0 - math.sin(phi)) / (2.0 * math.cos(phi))
    s = math.sin(phi)
    pm = (3.0 * sigma_H_psi - sigma_h_psi - 2.0 * c * math.cos(phi) -
          (3.0 * sigma_H_psi - sigma_h_psi - 2.0 * pore_psi) * s) / 2.0
    return max(0.0, pm)


def safe_mud_window(sigma_v_psi: float, sigma_H_psi: float,
                    sigma_h_psi: float, pore_psi: float,
                    ucs_psi: float, friction_angle_deg: float,
                    tensile_strength_psi: float = 0.0) -> Dict:
    """Safe mud-pressure window [lower, upper] with status."""
    pb = breakout_pressure(sigma_H_psi, sigma_h_psi, pore_psi, ucs_psi,
                           friction_angle_deg)
    pf = fracture_pressure(sigma_v_psi, sigma_H_psi, sigma_h_psi, pore_psi,
                           tensile_strength_psi)["pressure_psi"]
    lower = max(pore_psi, pb)
    upper = min(pf, sigma_v_psi)
    if upper <= lower:
        status = "NO_WINDOW"
    elif upper - lower < 200:
        status = "NARROW"
    else:
        status = "OK"
    return {"lower_psi": round(lower, 0), "upper_psi": round(upper, 0),
            "breakout_pressure_psi": round(pb, 0),
            "fracture_pressure_psi": round(pf, 0),
            "pore_pressure_psi": round(pore_psi, 0),
            "width_psi": round(upper - lower, 0), "status": status}


def mud_window_check(mw_ppg: float, tvd_ft: float, window: Dict) -> Dict:
    """Check the actual mud pressure against the safe window."""
    pm = mw_ppg * CF * tvd_ft
    lower = window["lower_psi"]
    upper = window["upper_psi"]
    if pm < lower:
        status = "BREAKOUT_RISK (mud too light)"
    elif pm > upper:
        status = "FRACTURE_RISK (mud too heavy)"
    else:
        status = "OK — inside safe window"
    return {"mud_pressure_psi": round(pm, 0), "lower_psi": lower,
            "upper_psi": upper, "status": status}


# ---------------------------------------------------------------------------
# LOT / FIT interpretation
# ---------------------------------------------------------------------------

def lot_interpretation(lot_pressure_psi: float, shoe_tvd_ft: float,
                       mw_ppg: float = 0.0,
                       is_fit: bool = False) -> Dict:
    """Leak-off test / formation-integrity test interpretation.

    LOT EMW = LOT pressure / (0.052 × shoe TVD); FIT is a pass/fail
    test at a target pressure (no leak-off to the formation)."""
    if shoe_tvd_ft <= 0:
        return {"error": "shoe TVD required"}
    emw = lot_pressure_psi / (CF * shoe_tvd_ft)
    over_mw = emw - mw_ppg if mw_ppg > 0 else None
    return {
        "test": "FIT" if is_fit else "LOT",
        "pressure_psi": round(lot_pressure_psi, 0),
        "emw_ppg": round(emw, 2),
        "mud_weight_ppg": mw_ppg or None,
        "margin_over_mw_ppg": round(over_mw, 2) if over_mw is not None
        else None,
    }


# ---------------------------------------------------------------------------
# Markdown section
# ---------------------------------------------------------------------------

def geomechanics_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready WELLBORE STABILITY & GEOMECHANICS section."""
    def _pick(*keys) -> str:
        for k in keys:
            s = str(values.get(k, "") or "").strip()
            if s:
                return s
        return ""

    def _f(x, d=0.0) -> float:
        try:
            return float(str(x).strip()) if str(x).strip() else d
        except (TypeError, ValueError):
            return d

    op = (operator or "").strip() or "the Operator"
    tvd = _f(_pick("depth", "depth_ft", "td_depth", "td_ft", "total_depth"))
    depth_m = _f(_pick("depth_m", "td_m"))
    if tvd <= 0 and depth_m > 0:
        tvd = depth_m * 3.28084
    mw = _f(_pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    pore = _f(_pick("formation_pressure", "pore_pressure", "pp_ppg"))
    sv_grad = _f(_pick("sigma_v_grad", "overburden_gradient"), 1.0)
    sH_ratio = _f(_pick("sH_sv_ratio", "sigmaH_sv_ratio"), 0.95)
    sh_ratio = _f(_pick("sh_sv_ratio", "sigmah_sv_ratio"), 0.85)
    ucs = _f(_pick("ucs_psi", "rock_ucs"))
    phi = _f(_pick("friction_angle", "friction_angle_deg"), 30.0)
    t0 = _f(_pick("tensile_strength", "tensile_strength_psi"), 0.0)
    lot_p = _f(_pick("lot_pressure", "lot_psi"))
    shoe = _f(_pick("casing_depth", "casing_depth_ft", "shoe_depth"))
    is_fit = _pick("lot_type", "fit") == "FIT"

    L = [
        "## WELLBORE STABILITY & GEOMECHANICS",
        "",
        "Elastic Kirsch solution for a vertical borehole with "
        "Mohr-Coulomb shear failure (breakout) and tensile failure "
        "(fracture); stresses in psi.",
        "",
    ]

    if tvd <= 0 or ucs <= 0 or mw <= 0:
        L.append("⚠️ Requires depth, rock strength (UCS) and mud weight — "
                 "enter them in the Engineering Basis to run the "
                 "stability window.")
        L.append("")
        return "\n".join(L)

    sv = sv_grad * tvd
    sH = sv * sH_ratio
    sh = sv * sh_ratio
    pp = pore * CF * tvd if pore <= 5 else pore   # pore as ppg EMW or psi
    if pore > 0 and pore <= 5:
        pp = pore * CF * tvd

    win = safe_mud_window(sv, sH, sh, pp, ucs, phi, t0)
    pm = mw * CF * tvd
    chk = mud_window_check(mw, tvd, win)

    L.append(f"| Parameter | Value |")
    L.append("|---|---|")
    L.append(f"| Depth (TVD) | {tvd:,.0f} ft |")
    L.append(f"| Overburden σv | {sv:,.0f} psi ({sv_grad:g} psi/ft) |")
    L.append(f"| Max horizontal σH | {sH:,.0f} psi ({sH_ratio:g}×σv) |")
    L.append(f"| Min horizontal σh | {sh:,.0f} psi ({sh_ratio:g}×σv) |")
    L.append(f"| Pore pressure | {pp:,.0f} psi "
             f"({pp/CF/tvd:.1f} ppg EMW) |")
    L.append(f"| Rock UCS | {ucs:,.0f} psi | φ = {phi:g}° |")
    L.append("")
    L.append(f"**Breakout limit (min Pm):** {win['breakout_pressure_psi']:,.0f} "
             f"psi ({win['breakout_pressure_psi']/CF/tvd:.1f} ppg EMW)")
    L.append(f"**Fracture limit (max Pm):** {win['fracture_pressure_psi']:,.0f} "
             f"psi ({win['fracture_pressure_psi']/CF/tvd:.1f} ppg EMW) — "
             f"{'vertical' if win['fracture_pressure_psi'] < sv else 'horizontal'} "
             f"mechanism")
    L.append(f"**Safe mud window:** {win['lower_psi']:,.0f} – "
             f"{win['upper_psi']:,.0f} psi "
             f"({win['lower_psi']/CF/tvd:.1f} – "
             f"{win['upper_psi']/CF/tvd:.1f} ppg EMW) — **{win['status']}**")
    L.append("")
    L.append(f"**Actual mud pressure ({mw:g} ppg):** {pm:,.0f} psi — "
             f"**{chk['status']}**")
    L.append("")

    if lot_p > 0 and shoe > 0:
        li = lot_interpretation(lot_p, shoe, mw, is_fit)
        L.append(f"**{'FIT' if is_fit else 'LOT'} at shoe "
                 f"({shoe:,.0f} ft):** {li['pressure_psi']:,.0f} psi → "
                 f"**{li['emw_ppg']} ppg EMW**"
                 + (f" (margin +{li['margin_over_mw_ppg']} ppg over MW)"
                    if li.get("margin_over_mw_ppg") is not None else ""))
        L.append("")
    L.append(f"*Geomechanics computed deterministically for {op} with an "
             "elastic vertical-well model; a full 3-D geomechanical "
             "model with rock-property calibration is required for final "
             "design.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test (hand-verified reference)
# ---------------------------------------------------------------------------

def _selftest():
    # Kirsch: σH=12000, σh=10000, Pm=8000:
    #   θ=0  (σH dir): 3σh−σH−Pm = 30000−12000−8000 = 10000
    #   θ=90 (σh dir): 3σH−σh−Pm = 36000−10000−8000 = 18000
    th0 = kirsch_hoop_stress(12000, 10000, 8000, 0)
    assert abs(th0 - 10000) < 0.01, th0
    th90 = kirsch_hoop_stress(12000, 10000, 8000, 90)
    assert abs(th90 - 18000) < 0.01, th90
    # fracture: 3σh−σH−Pp+T0 = 30000−12000−5000+500 = 13500 (vertical)
    fr = fracture_pressure(19000, 12000, 10000, 5000, 500)
    assert fr["mechanism"].startswith("vertical"), fr
    assert abs(fr["pressure_psi"] - 13500) < 1, fr
    # breakout: hand-verified — c = UCS(1−sinφ)/(2cosφ) = 2309;
    # Pm = [26000 − 2c·cosφ − 16000·sinφ]/2 = [26000−4000−8000]/2 = 7000
    pb = breakout_pressure(12000, 10000, 5000, 8000, 30)
    assert abs(pb - 7000) < 3, pb
    # window
    win = safe_mud_window(19000, 12000, 10000, 5000, 8000, 30, 500)
    assert win["lower_psi"] == 7000, win
    assert win["upper_psi"] == 13500, win
    # MW 12 ppg @ 10000 ft = 6240 psi < 7000 -> breakout risk
    chk = mud_window_check(12.0, 10000, win)
    assert "BREAKOUT" in chk["status"], chk
    # MW 16 ppg = 8320 psi -> OK
    chk2 = mud_window_check(16.0, 10000, win)
    assert chk2["status"].startswith("OK"), chk2
    # LOT: 1400 psi @ 4000 ft shoe = 6.73 ppg
    li = lot_interpretation(1400, 4000, 12.0)
    assert abs(li["emw_ppg"] - 6.73) < 0.02, li
    # markdown
    md = geomechanics_markdown({
        "depth": "10000", "mud_weight": "12", "formation_pressure": "9.6",
        "sigma_v_grad": "1.9", "sH_sv_ratio": "0.63", "sh_sv_ratio": "0.53",
        "ucs_psi": "8000", "friction_angle": "30",
        "tensile_strength": "500", "lot_pressure": "1400",
        "casing_depth": "4000"})
    assert "WELLBORE STABILITY" in md
    assert "Safe mud window" in md
    print("  ✔ geomechanics selftest: Kirsch + Mohr-Coulomb + LOT verified")
    return win


if __name__ == "__main__":
    _selftest()
    print("engineering_geomechanics OK")
