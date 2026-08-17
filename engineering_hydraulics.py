# ============================================================================
# STANDPIPE PRESSURE MODEL — API RP 13D
# File: engineering_hydraulics.py
# Audit item (P1): Hydraulics — full system model (surface equipment +
# inside pipe + bit + annulus) with ECD.
#
# Field units, Bingham plastic.  Constants are analytically verified:
#   - bit drop:     ΔP_bit = MW×Q² / (10858×TFA²)   (Cd = 0.95; derived)
#   - pipe laminar: ΔP = PV×V×L/(90000×d²) + YP×L/(225×d)   (HP + yield;
#                    90000 verified against Hagen-Poiseuille to 0.3%)
#   - ann laminar:  ΔP = PV×V×L/(60000×(D−d)²) + YP×L/(200×(D−d))
#                    (60000 verified against HP to 0.3%)
#   - turbulent:    Darcy-Weisbach + Blasius friction factor
#   - Reynolds:     Re = 928×MW×V×d/PV  (pipe), 928×MW×V×(D−d)/PV (annulus)
#   - ECD:          ECD = MW + ΔP_annulus/(0.052×TVD)
# Surface equipment: API RP 13D equivalent-length table (ft of 3.826-in ID
# pipe): Type 1 = 60, Type 2 = 120, Type 3 = 240, Type 4 = 480.
# ============================================================================

import math
from typing import Dict, List, Optional, Tuple

# API RP 13D surface-equipment equivalent lengths (ft of 3.826-in ID pipe)
SURFACE_EQ_LENGTHS_FT = {"Type 1 (simple)": 60.0, "Type 2 (standard)": 120.0,
                         "Type 3 (long)": 240.0, "Type 4 (extended)": 480.0}
SURFACE_EQ_ID_IN = 3.826
BIT_CONSTANT = 10858.0        # Cd = 0.95 (derived: 12038 × Cd²)
RE_CONSTANT = 928.0           # Re = 928 × MW × V(ft/s) × d / PV
G = 32.174
PIPE_LAM_1 = 90000.0          # PV×V×L/(90000 d²)
PIPE_LAM_2 = 225.0            # YP×L/(225 d)
ANN_LAM_1 = 60000.0
ANN_LAM_2 = 200.0


def _v_ftmin(q_gpm: float, d_in: float) -> float:
    """Velocity inside a pipe: V = 24.5 × Q / d² (ft/min).

    (0.408 × Q/d² gives ft/s; the field formulas use ft/min.)
    """
    return 24.5 * q_gpm / (d_in ** 2)


def _v_ann_ftmin(q_gpm: float, hole_in: float, pipe_in: float) -> float:
    """Annular velocity: V = 24.5 × Q / (D² − d²) (ft/min)."""
    return 24.5 * q_gpm / (hole_in ** 2 - pipe_in ** 2)


def bit_pressure_drop(mw_ppg: float, q_gpm: float, tfa_in2: float) -> float:
    """ΔP_bit = MW×Q²/(10858×TFA²) — API RP 13D (Cd = 0.95)."""
    if tfa_in2 <= 0 or q_gpm <= 0:
        return 0.0
    return mw_ppg * q_gpm ** 2 / (BIT_CONSTANT * tfa_in2 ** 2)


def reynolds_pipe(mw_ppg: float, v_ftmin: float, d_in: float,
                  pv_cp: float) -> float:
    """Pipe Reynolds (V in ft/min internally converted)."""
    if pv_cp <= 0:
        return 1e9
    return RE_CONSTANT * mw_ppg * (v_ftmin / 60.0) * d_in / pv_cp


def reynolds_annulus(mw_ppg: float, v_ftmin: float, hole_in: float,
                     pipe_in: float, pv_cp: float) -> float:
    if pv_cp <= 0:
        return 1e9
    return RE_CONSTANT * mw_ppg * (v_ftmin / 60.0) * (hole_in - pipe_in) \
        / pv_cp


def pressure_loss_pipe(mw_ppg: float, pv_cp: float, yp_lb100ft2: float,
                       v_ftmin: float, d_in: float, length_ft: float,
                       ) -> Dict:
    """Inside-pipe pressure loss with regime selection (Bingham)."""
    if d_in <= 0 or length_ft <= 0:
        return {"psi": 0.0, "regime": "none", "laminar_psi": 0.0,
                "turbulent_psi": 0.0, "reynolds": 0.0}
    lam = (pv_cp * v_ftmin * length_ft / (PIPE_LAM_1 * d_in ** 2) +
           yp_lb100ft2 * length_ft / (PIPE_LAM_2 * d_in))
    re = reynolds_pipe(mw_ppg, v_ftmin, d_in, pv_cp)
    turb = _turbulent_pipe(mw_ppg, v_ftmin, d_in, length_ft, pv_cp, re)
    regime = "laminar" if re < 2100 else "turbulent"
    psi = lam if regime == "laminar" else turb
    return {"psi": round(psi, 1), "regime": regime,
            "laminar_psi": round(lam, 1), "turbulent_psi": round(turb, 1),
            "reynolds": round(re, 0)}


def pressure_loss_annulus(mw_ppg: float, pv_cp: float, yp_lb100ft2: float,
                          v_ftmin: float, hole_in: float, pipe_in: float,
                          length_ft: float) -> Dict:
    """Annular pressure loss with regime selection (Bingham)."""
    dh = hole_in - pipe_in
    if dh <= 0 or length_ft <= 0:
        return {"psi": 0.0, "regime": "none", "laminar_psi": 0.0,
                "turbulent_psi": 0.0, "reynolds": 0.0}
    lam = (pv_cp * v_ftmin * length_ft / (ANN_LAM_1 * dh ** 2) +
           yp_lb100ft2 * length_ft / (ANN_LAM_2 * dh))
    re = reynolds_annulus(mw_ppg, v_ftmin, hole_in, pipe_in, pv_cp)
    turb = _turbulent_annulus(mw_ppg, v_ftmin, hole_in, pipe_in,
                              length_ft, pv_cp, re)
    regime = "laminar" if re < 2100 else "turbulent"
    psi = lam if regime == "laminar" else turb
    return {"psi": round(psi, 1), "regime": regime,
            "laminar_psi": round(lam, 1), "turbulent_psi": round(turb, 1),
            "reynolds": round(re, 0)}


def _turbulent_pipe(mw_ppg: float, v_ftmin: float, d_in: float,
                    length_ft: float, pv_cp: float, re: float) -> float:
    """Darcy-Weisbach + Blasius (smooth pipe, Re < 1e5)."""
    if re <= 0 or d_in <= 0:
        return 0.0
    f = 0.3164 / (re ** 0.25)
    rho = mw_ppg * 7.4805                       # lb/ft³
    v = v_ftmin / 60.0                          # ft/s
    d_ft = d_in / 12.0
    return f * (length_ft / d_ft) * (rho * v ** 2) / (2 * G * 144.0)


def _turbulent_annulus(mw_ppg: float, v_ftmin: float, hole_in: float,
                       pipe_in: float, length_ft: float, pv_cp: float,
                       re: float) -> float:
    """Darcy-Weisbach + Blasius on the hydraulic diameter."""
    dh = hole_in - pipe_in
    if dh <= 0 or re <= 0:
        return 0.0
    f = 0.3164 / (re ** 0.25)
    rho = mw_ppg * 7.4805
    v = v_ftmin / 60.0
    d_ft = dh / 12.0
    return f * (length_ft / d_ft) * (rho * v ** 2) / (2 * G * 144.0)


def ecd(mw_ppg: float, annulus_loss_psi: float, tvd_ft: float) -> float:
    """ECD = MW + ΔP_annulus / (0.052 × TVD)."""
    if tvd_ft <= 0:
        return mw_ppg
    return mw_ppg + annulus_loss_psi / (0.052 * tvd_ft)


# ---------------------------------------------------------------------------
# Full standpipe model
# ---------------------------------------------------------------------------

def standpipe_pressure(values: Dict) -> Dict:
    """Full system pressure loss from wizard-style inputs.

    Expected keys (all optional, missing -> skipped):
      mud_weight, plastic_viscosity, yield_point, flow_rate,
      hole_size, pipe_od, dp_id (drill pipe ID), tfa (total nozzle area),
      depth / td_depth / total_depth (pipe length), casing_depth,
      casing_size (cased annulus), surface_type, bha_od, bha_length
    """
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

    mw = _f(_pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    pv = _f(_pick("plastic_viscosity", "mud_pv", "pv_cp"))
    yp = _f(_pick("yield_point", "mud_yp", "yp_lb100ft2"))
    q = _f(_pick("flow_rate", "flow_rate_gpm", "q_gpm", "pump_rate"))
    hole = _f(_pick("hole_size", "hole_id", "hole_diameter"))
    pipe = _f(_pick("pipe_od", "pipe_size", "drill_pipe_od"))
    dp_id = _f(_pick("dp_id", "dp_inner_id", "pipe_id"))
    tfa = _f(_pick("tfa", "nozzle_area", "tfa_in2"))
    depth = _f(_pick("depth", "depth_ft", "td_depth", "td_ft", "total_depth"))
    depth_m = _f(_pick("depth_m", "td_m"))
    if depth <= 0 and depth_m > 0:
        depth = depth_m * 3.28084
    csg_depth = _f(_pick("casing_depth", "casing_depth_ft", "shoe_depth"))
    csg_id = _f(_pick("casing_id", "casing_size"))
    surf_type = _pick("surface_type", "surface_equipment")
    bha_od = _f(_pick("bha_od"))
    bha_len = _f(_pick("bha_length", "dc_length"))

    parts: List[Dict] = []

    # surface equipment
    eq_len = SURFACE_EQ_LENGTHS_FT.get(surf_type, 120.0) if surf_type else 120.0
    if q > 0:
        v_eq = _v_ftmin(q, SURFACE_EQ_ID_IN)
        parts.append({
            "name": f"Surface equipment ({surf_type or 'Type 2 (standard)'})",
            "geometry": f"{eq_len:g} ft eq. of {SURFACE_EQ_ID_IN:g}-in ID",
            **pressure_loss_pipe(mw, pv, yp, v_eq, SURFACE_EQ_ID_IN, eq_len),
        })

    # inside drill string
    if q > 0 and dp_id > 0 and depth > 0:
        v_dp = _v_ftmin(q, dp_id)
        parts.append({
            "name": "Inside drill pipe",
            "geometry": f"{dp_id:g}-in ID × {depth:,.0f} ft",
            **pressure_loss_pipe(mw, pv, yp, v_dp, dp_id, depth),
        })

    # inside BHA / drill collars
    if q > 0 and bha_od > 0 and bha_len > 0 and dp_id > 0:
        dc_id = max(1.5, dp_id * 0.6)   # typical DC ID ratio
        v_dc = _v_ftmin(q, dc_id)
        parts.append({
            "name": "Inside BHA / drill collars",
            "geometry": f"~{dc_id:g}-in ID × {bha_len:,.0f} ft",
            **pressure_loss_pipe(mw, pv, yp, v_dc, dc_id, bha_len),
        })

    # bit
    if q > 0 and tfa > 0:
        pb = bit_pressure_drop(mw, q, tfa)
        parts.append({"name": "Bit (nozzles)", "geometry": f"TFA {tfa} in²",
                      "psi": round(pb, 1), "regime": "nozzle",
                      "laminar_psi": 0.0, "turbulent_psi": round(pb, 1),
                      "reynolds": 0.0})

    # annulus: cased section + open-hole section
    ann_psi = 0.0
    if q > 0 and hole > pipe and depth > 0:
        if csg_depth > 0 and csg_id > pipe and csg_depth < depth:
            v_a = _v_ann_ftmin(q, csg_id, pipe)
            cased = pressure_loss_annulus(mw, pv, yp, v_a, csg_id, pipe,
                                          csg_depth)
            parts.append({"name": "Annulus — cased section",
                          "geometry": f"{csg_id:g}-in ID × {csg_depth:,.0f} ft",
                          **cased})
            ann_psi += cased["psi"]
            v_a = _v_ann_ftmin(q, hole, pipe)
            open_ = pressure_loss_annulus(mw, pv, yp, v_a, hole, pipe,
                                          depth - csg_depth)
            parts.append({"name": "Annulus — open hole",
                          "geometry": f"{hole:g}-in × {depth - csg_depth:,.0f} ft",
                          **open_})
            ann_psi += open_["psi"]
        else:
            v_a = _v_ann_ftmin(q, hole, pipe)
            open_ = pressure_loss_annulus(mw, pv, yp, v_a, hole, pipe, depth)
            parts.append({"name": "Annulus — open hole",
                          "geometry": f"{hole:g}-in × {depth:,.0f} ft",
                          **open_})
            ann_psi += open_["psi"]
        # BHA annulus (higher ΔP per ft)
        if bha_od > pipe and bha_len > 0 and hole > bha_od:
            v_bha = _v_ann_ftmin(q, hole, bha_od)
            bha_ann = pressure_loss_annulus(mw, pv, yp, v_bha, hole, bha_od,
                                            bha_len)
            parts.append({"name": "Annulus — BHA section",
                          "geometry": f"{hole:g}-in × {bha_od:g}-in "
                                      f"× {bha_len:,.0f} ft",
                          **bha_ann})
            ann_psi += bha_ann["psi"]

    spp = round(sum(p["psi"] for p in parts), 1)
    ecd_ppg = ecd(mw, ann_psi, depth) if depth > 0 else mw
    return {
        "parts": parts, "spp_psi": spp, "annulus_psi": round(ann_psi, 1),
        "ecd_ppg": round(ecd_ppg, 2), "mud_weight_ppg": mw,
        "flow_gpm": q, "tvd_ft": depth,
        "model": "API RP 13D (Bingham) + Darcy-Weisbach/Blasius turbulent",
    }


def hydraulics_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready HYDRAULICS — STANDPIPE PRESSURE MODEL section."""
    res = standpipe_pressure(values)
    op = (operator or "").strip() or "the Operator"
    if not res["parts"]:
        return ""
    L = [
        "## HYDRAULICS — STANDPIPE PRESSURE MODEL (API RP 13D)",
        "",
        f"Model: {res['model']}. Flow = {res['flow_gpm']:g} gpm, "
        f"MW = {res['mud_weight_ppg']:g} ppg.",
        "",
        "| Section | Geometry | ΔP (psi) | Regime |",
        "|---|---|---|---|",
    ]
    for p in res["parts"]:
        L.append(f"| {p['name']} | {p['geometry']} | {p['psi']} | "
                 f"{p['regime']} |")
    L.append("")
    L.append(f"**Standpipe pressure (SPP) ≈ {res['spp_psi']:,.0f} psi**")
    L.append("")
    if res["tvd_ft"] > 0:
        L.append(f"**Equivalent circulating density ≈ "
                 f"{res['ecd_ppg']} ppg** "
                 f"(annulus ΔP {res['annulus_psi']:,.0f} psi over "
                 f"{res['tvd_ft']:,.0f} ft TVD)")
        L.append("")
    L.append(f"*Standpipe model computed deterministically for {op}; "
             "confirm against pump-pressure readings and the "
             "mud-company's hydraulics program before operations.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test (analytic references)
# ---------------------------------------------------------------------------

def _selftest():
    # bit drop: classic example — 12 ppg, 300 gpm, 3×12/32 nozzles
    tfa = 3 * math.pi / 4 * (12 / 32.0) ** 2   # 0.3312 in²
    pb = bit_pressure_drop(12.0, 300.0, tfa)
    expected = 12 * 90000 / (10858 * tfa ** 2)
    assert abs(pb - expected) < 0.01, pb
    assert abs(pb - 906.7) < 10.0, pb
    # laminar pipe vs Hagen-Poiseuille (YP=0): PV=25, V=100 ft/min,
    # d=4.276 in, L=1000 ft -> field 1.519 psi vs HP 1.523 psi (0.3%)
    lam = pressure_loss_pipe(12, 25, 0, 100, 4.276, 1000)
    mu = 25 / 1488.16
    hp = 32 * mu * (100 / 60.0) * 1000 / (G * (4.276 / 12) ** 2 * 144)
    assert abs(lam["laminar_psi"] - hp) < 0.03, (lam, hp)
    # laminar annulus vs HP (narrow-slot): D=8.5, d=5, V=100 ft/min
    la = pressure_loss_annulus(12, 25, 0, 100, 8.5, 5.0, 1000)
    dh = 3.5 / 12.0
    hpa = 48 * mu * (100 / 60.0) * 1000 / (G * dh ** 2 * 144)
    assert abs(la["laminar_psi"] - hpa) < 0.03, (la, hpa)
    # turbulent pipe: DW/Blasius — classic example 5-in DP, 300 gpm
    v = _v_ftmin(300, 4.276)
    res = pressure_loss_pipe(12, 25, 20, v, 4.276, 10000)
    assert res["regime"] == "turbulent", res
    assert abs(res["turbulent_psi"] - 363.3) < 5.0, res
    # ECD: 12 ppg + 70 psi over 8000 ft -> 12.168
    assert abs(ecd(12.0, 70.0, 8000.0) - 12.1683) < 0.01
    # full model
    vals = {"mud_weight": "12", "plastic_viscosity": "25", "yield_point": "20",
            "flow_rate": "300", "hole_size": "8.5", "pipe_od": "5",
            "dp_id": "4.276", "tfa": "0.3312", "depth": "10000",
            "casing_depth": "4000", "casing_id": "8.921", "bha_od": "6.5",
            "bha_length": "600", "surface_type": "Type 2 (standard)"}
    sp = standpipe_pressure(vals)
    assert len(sp["parts"]) >= 6, sp
    assert sp["spp_psi"] > 100, sp
    md = hydraulics_markdown(vals)
    assert "STANDPIPE PRESSURE MODEL" in md
    assert "Equivalent circulating density" in md
    print(f"  ✔ hydraulics selftest: SPP = {sp['spp_psi']} psi, "
          f"ECD = {sp['ecd_ppg']} ppg, {len(sp['parts'])} sections")
    return sp


if __name__ == "__main__":
    _selftest()
    print("engineering_hydraulics OK")
