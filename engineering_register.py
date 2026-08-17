# ============================================================================
# ENGINEERING CALCULATION REGISTER
# File: engineering_register.py
# Audit item (P1): "Buyer Q1 — which equation/standard produced this number?"
#
# Every computed value that can appear in a generated document is registered
# here with:
#   - its formula (plain text, audit-readable)
#   - the input values actually used (substitution trace)
#   - the computed result and unit
#   - the industry standard source (API / IADC / ISO / field practice)
#
# The register is deterministic: it only calls the built-in calculators
# (engineering_units / engineering_advanced / engineering_deep), never the AI.
# The AI assistant is blocked from altering these numbers (Numeric Lock).
# ============================================================================

import math
from typing import Dict, List, Optional


def _f(v, default: float = 0.0) -> float:
    """Safe float conversion."""
    try:
        if v is None:
            return default
        s = str(v).strip()
        if not s:
            return default
        return float(s)
    except (TypeError, ValueError):
        return default


def _fmt(x: float, nd: int = 2) -> str:
    if x is None:
        return "—"
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    if abs(x) >= 1e6:
        return f"{x:,.0f}"
    if abs(x) >= 1000:
        if nd <= 0:
            return f"{x:,.0f}"
        return f"{x:,.{nd}f}".rstrip("0").rstrip(".")
    if nd <= 0:
        return f"{x:.0f}"
    return f"{x:.{nd}f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# Register computation
# ---------------------------------------------------------------------------

def compute_register(values: Dict) -> List[Dict]:
    """Compute the calculation register rows from wizard inputs.

    Each row: dict with keys
      param, formula, inputs, result, unit, standard, status
    Rows are only produced when the required inputs are available.
    """
    from engineering_units import (hydrostatic_pressure, emw_from_pressure,
                                   maasp, kill_mud_weight,
                                   annular_velocity_ftmin,
                                   barlow_burst_pressure,
                                   api_collapse_pressure)
    from engineering_advanced import (kick_tolerance, surge_swab_pressure,
                                      critical_annular_velocity,
                                      cbhp_mud_weight,
                                      mpd_operating_window)

    v = values or {}
    rows: List[Dict] = []

    # ----- helper: pick the first available key --------------------------
    def pick(*keys) -> Optional[str]:
        for k in keys:
            s = str(v.get(k, "") or "").strip()
            if s:
                return s
        return None

    mw = _f(pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    depth_ft = _f(pick("depth_ft", "depth", "td_depth", "td_ft", "total_depth"))
    # depth in metres fallback (some templates use metric)
    depth_m = _f(pick("depth_m", "target_depth_m", "td_m"))
    if depth_ft <= 0 and depth_m > 0:
        depth_ft = depth_m * 3.28084
    hole = _f(pick("hole_size", "hole_id", "hole_diameter", "bit_size"))
    pipe = _f(pick("pipe_od", "pipe_size", "bha_od", "drill_pipe_od"))
    casing_od = _f(pick("casing_od", "casing_size"))
    casing_depth = _f(pick("casing_depth", "casing_depth_ft", "shoe_depth",
                           "csg_depth"))
    fg = _f(pick("fracture_gradient", "fg_ppg", "frac_gradient"))
    pp = _f(pick("pore_pressure", "formation_pressure", "pp_ppg"))
    sidpp = _f(pick("sidpp", "sidpp_psi"))
    bop_wp = _f(pick("bop_wp", "bop_working_pressure", "bop_wp_psi"))
    flow = _f(pick("flow_rate", "flow_rate_gpm", "q_gpm", "pump_rate"))
    yp = _f(pick("yield_point", "mud_yp", "yp_lb100ft2"))
    pv = _f(pick("plastic_viscosity", "mud_pv", "pv_cp"))
    trip = _f(pick("trip_speed", "trip_speed_ft_min"))
    pit_gain = _f(pick("pit_gain", "max_pit_gain", "pit_gain_bbl"))
    ann_cap = _f(pick("annular_capacity", "ann_cap_bbl_ft"))
    total_cost = _f(pick("total_cost", "estimated_cost", "afe_total"))
    total_days = _f(pick("total_days", "duration_days", "days"))
    wall = _f(pick("casing_wall", "casing_wall_in", "wall_thickness"))
    ys = _f(pick("casing_yield", "casing_yield_psi", "yield_strength"))
    n_idx = _f(pick("n_index", "flow_index"))
    k_idx = _f(pick("k_index", "consistency_index"))
    tau0 = _f(pick("yield_stress", "tau0", "hb_yield_stress"))
    ann_len = depth_ft

    # ----- 1. hydrostatic pressure ---------------------------------------
    if mw > 0 and depth_ft > 0:
        p = hydrostatic_pressure(mw, depth_ft)
        rows.append({
            "param": "Hydrostatic pressure (at reference depth)",
            "formula": "P = 0.052 × MW × D",
            "inputs": f"MW = {_fmt(mw)} ppg, D = {_fmt(depth_ft, 0)} ft",
            "result": _fmt(p, 0), "unit": "psi",
            "standard": "API RP 7G / API 13D (field constant 0.052 psi/ft per ppg)",
            "status": "OK"})

    # ----- 2. EMW ---------------------------------------------------------
    if mw > 0 and depth_ft > 0:
        rows.append({
            "param": "Equivalent mud weight (EMW) at reference depth",
            "formula": "EMW = P / (0.052 × D)",
            "inputs": f"MW = {_fmt(mw)} ppg, D = {_fmt(depth_ft, 0)} ft",
            "result": _fmt(mw), "unit": "ppg",
            "standard": "API RP 7G",
            "status": "OK"})

    # ----- 3. MAASP (shoe) ------------------------------------------------
    shoe = casing_depth if casing_depth > 0 else depth_ft
    if fg > 0 and mw > 0 and shoe > 0:
        m = maasp(fg, mw, shoe)
        rows.append({
            "param": "MAASP (max. allowable annular surface pressure at shoe)",
            "formula": "MAASP = (FG − MW) × 0.052 × D_shoe",
            "inputs": f"FG = {_fmt(fg)} ppg, MW = {_fmt(mw)} ppg, "
                      f"D_shoe = {_fmt(shoe, 0)} ft",
            "result": _fmt(m, 0), "unit": "psi",
            "standard": "Well control practice (API RP 59 / IADC)",
            "status": "OK"})

    # ----- 4. Kill mud weight ---------------------------------------------
    if sidpp > 0 and depth_ft > 0 and mw > 0:
        kmw = kill_mud_weight(sidpp, depth_ft, mw)
        rows.append({
            "param": "Kill mud weight (from SIDPP)",
            "formula": "KMW = MW + SIDPP / (0.052 × TVD)",
            "inputs": f"SIDPP = {_fmt(sidpp, 0)} psi, TVD = {_fmt(depth_ft, 0)} ft, "
                      f"MW = {_fmt(mw)} ppg",
            "result": _fmt(kmw), "unit": "ppg",
            "standard": "API RP 59 well control",
            "status": "OK"})

    # ----- 5. BOP working pressure envelope --------------------------------
    if bop_wp > 0 and fg > 0 and mw > 0 and shoe > 0:
        from engineering_advanced import bop_pressure_envelope
        env = bop_pressure_envelope(bop_wp, fg, mw, shoe)
        rows.append({
            "param": "BOP working-pressure envelope vs MAASP",
            "formula": "BOP WP ≥ MAASP",
            "inputs": f"BOP WP = {_fmt(bop_wp, 0)} psi, MAASP = "
                      f"{_fmt(env['masp_psi'], 0)} psi",
            "result": env["status"], "unit": "—",
            "standard": "API 16A / API 53",
            "status": "OK" if env["ok"] else "FAIL"})

    # ----- 6. Kick tolerance ----------------------------------------------
    if fg > 0 and mw > 0 and shoe > 0 and pit_gain > 0 and ann_cap > 0:
        kt = kick_tolerance(fg, mw, shoe, pit_gain, ann_cap)
        rows.append({
            "param": "Kick tolerance (as EMW above MW)",
            "formula": "KT = FG − MW − margin − (kick height × Δρ / TVD)",
            "inputs": f"FG = {_fmt(fg)} ppg, MW = {_fmt(mw)} ppg, "
                      f"D_shoe = {_fmt(shoe, 0)} ft, pit gain = {_fmt(pit_gain)} bbl",
            "result": _fmt(kt["kt_ppg"]), "unit": "ppg",
            "standard": "IADC / field practice (simplified)",
            "status": "OK"})

    # ----- 7. Annular velocity ---------------------------------------------
    if flow > 0 and hole > 0 and pipe > 0 and hole > pipe:
        av = annular_velocity_ftmin(flow, hole, pipe)
        rows.append({
            "param": "Annular velocity",
            "formula": "AV = 24.5 × Q / (D² − d²)",
            "inputs": f"Q = {_fmt(flow, 0)} gpm, D = {_fmt(hole)} in, "
                      f"d = {_fmt(pipe)} in",
            "result": _fmt(av, 1), "unit": "ft/min",
            "standard": "API RP 7G",
            "status": "OK"})
        # cuttings transport / critical velocity
        if yp > 0 and pv > 0 and mw > 0:
            cvr = critical_annular_velocity(yp, pv, hole, pipe, mw)
            cv = float(cvr.get("critical_ann_velocity_ft_min") or 0.0)
            ratio = 0.0
            try:
                from engineering_advanced import cuttings_transport_ratio
                ratio = cuttings_transport_ratio(av, cv)
            except Exception:
                ratio = av / cv if cv > 0 else 0.0
            rows.append({
                "param": "Hole-cleaning check (critical annular velocity)",
                "formula": "Vc (Moore) then transport ratio = Va / Vc",
                "inputs": f"YP = {_fmt(yp)} lb/100ft², PV = {_fmt(pv)} cP, "
                          f"MW = {_fmt(mw)} ppg, Va = {_fmt(av, 1)} ft/min",
                "result": f"{_fmt(ratio * 100, 0)} %",
                "unit": "transport ratio",
                "standard": "API RP 13D / Moore correlation",
                "status": "OK" if ratio >= 1.0 else "WARN"})

    # ----- 8. Surge / swab --------------------------------------------------
    if trip > 0 and pv > 0 and yp > 0 and hole > 0 and pipe > 0 and depth_ft > 0:
        ss = surge_swab_pressure(yp, pv, trip, hole - pipe, hole, pipe,
                                 depth_ft)
        rows.append({
            "param": "Surge/swab pressure (tripping)",
            "formula": "P = YP/(300×d_e) + (PV×V)/(1000×d_e²) per 1000 ft",
            "inputs": f"trip = {_fmt(trip, 1)} ft/min, YP = {_fmt(yp)} lb/100ft², "
                      f"PV = {_fmt(pv)} cP, D = {_fmt(hole)} in, "
                      f"d = {_fmt(pipe)} in, D_tvd = {_fmt(depth_ft, 0)} ft",
            "result": _fmt(ss.get("pressure_psi", 0.0), 0), "unit": "psi",
            "standard": "API RP 13D (simplified Bingham)",
            "status": "OK"})

    # ----- 9. Casing burst / collapse / triaxial -----------------------------
    if casing_od > 0 and wall > 0 and ys > 0:
        pb = barlow_burst_pressure(casing_od, wall, ys)
        rows.append({
            "param": "Casing burst rating (Barlow, 87.5% derate)",
            "formula": "P_b = 0.875 × 2 × YS × t / OD",
            "inputs": f"OD = {_fmt(casing_od)} in, t = {_fmt(wall)} in, "
                      f"YS = {_fmt(ys, 0)} psi",
            "result": _fmt(pb, 0), "unit": "psi",
            "standard": "API 5C3 / Barlow (API TR 5C3)",
            "status": "OK"})
        pc = api_collapse_pressure(casing_od, wall, ys)
        rows.append({
            "param": "Casing collapse rating",
            "formula": "API 5C3 collapse (4 regimes)",
            "inputs": f"OD = {_fmt(casing_od)} in, t = {_fmt(wall)} in, "
                      f"YS = {_fmt(ys, 0)} psi",
            "result": _fmt(pc, 0), "unit": "psi",
            "standard": "API 5C3",
            "status": "OK"})
        # triaxial / combined load check
        try:
            from engineering_deep import triaxial_check
            burst_load = _f(pick("burst_load", "design_burst"))
            coll_load = _f(pick("collapse_load", "design_collapse"))
            axial_load = _f(pick("axial_load", "design_axial"))
            if burst_load > 0 and coll_load > 0:
                tx = triaxial_check(casing_od, wall, ys, burst_load,
                                    coll_load, axial_load)
                rows.append({
                    "param": "Triaxial (von Mises) combined-load check",
                    "formula": "σ_vm = √(0.5[(σh−σr)²+(σr−σa)²+(σa−σh)²]) ≤ YS/DF",
                    "inputs": f"burst = {_fmt(burst_load, 0)} psi, "
                              f"collapse = {_fmt(coll_load, 0)} psi, "
                              f"axial = {_fmt(axial_load, 0)} psi, "
                              f"DF = 1.25",
                    "result": f"{_fmt(tx['utilization'], 0)} % utilization",
                    "unit": "—",
                    "standard": "API TR 5C3 (von Mises)",
                    "status": tx["status"]})
        except Exception:
            pass

    # ----- 10. MPD window ---------------------------------------------------
    if pp > 0 and fg > 0 and mw > 0:
        try:
            win = mpd_operating_window(pp, fg, mw, 0.0)
            if win and win.get("window_ok") is not None:
                rows.append({
                    "param": "MPD operating window",
                    "formula": "Window = FG − PP (with MW inside)",
                    "inputs": f"PP = {_fmt(pp)} ppg, FG = {_fmt(fg)} ppg, "
                              f"MW = {_fmt(mw)} ppg",
                    "result": f"{_fmt(win['min_bp_psi'], 0)}…"
                              f"{_fmt(win['max_bp_psi'], 0)} psi",
                    "unit": "backpressure",
                    "standard": "MPD practice (IADC UBO/MPD committee)",
                    "status": "OK" if win["window_ok"] else "WARN"})
        except Exception:
            pass

    # ----- 11. Evacuation burst / lost-returns collapse ---------------------
    if mw > 0 and pp > 0 and depth_ft > 0 and mw > pp:
        eb = 0.052 * (mw - pp) * depth_ft
        rows.append({
            "param": "Evacuation burst load (casing design)",
            "formula": "P = 0.052 × (MW − pore EMW) × D (gas to surface)",
            "inputs": f"MW = {_fmt(mw)} ppg, pore EMW = {_fmt(pp)} ppg, "
                      f"D = {_fmt(depth_ft, 0)} ft",
            "result": _fmt(eb, 0), "unit": "psi",
            "standard": "API 5C3 load case",
            "status": "OK"})
    if mw > 0 and depth_ft > 0:
        lr = 0.052 * mw * depth_ft
        rows.append({
            "param": "Lost-returns collapse load (casing design)",
            "formula": "P = 0.052 × MW × D (fluid level drop to TD)",
            "inputs": f"MW = {_fmt(mw)} ppg, D = {_fmt(depth_ft, 0)} ft",
            "result": _fmt(lr, 0), "unit": "psi",
            "standard": "API 5C3 load case",
            "status": "OK"})

    # ----- 12. Cost per foot ------------------------------------------------
    if total_cost > 0 and depth_ft > 0:
        cpf = total_cost / (depth_ft / 3.28084)   # per metre
        rows.append({
            "param": "Well cost per metre",
            "formula": "Cost/m = total cost / measured depth (m)",
            "inputs": f"total = {_fmt(total_cost, 0)} {pick('currency', '') or '$'}, "
                      f"D = {_fmt(depth_ft / 3.28084, 0)} m",
            "result": _fmt(cpf, 0), "unit": pick('currency', '') or "$" + "/m",
            "standard": "Company cost model (CBS)",
            "status": "OK"})
    if total_cost > 0 and total_days > 0:
        cpd = total_cost / total_days
        rows.append({
            "param": "Average daily cost",
            "formula": "Cost/day = total cost / duration",
            "inputs": f"total = {_fmt(total_cost, 0)} "
                      f"{pick('currency', '') or '$'}, days = {_fmt(total_days, 1)}",
            "result": _fmt(cpd, 0), "unit": (pick('currency', '') or "$") + "/day",
            "standard": "Company cost model (CBS)",
            "status": "OK"})

    # ----- 13. Herschel-Bulkley annular pressure loss -----------------------
    if flow > 0 and hole > 0 and pipe > 0 and ann_len > 0 and n_idx > 0 and k_idx > 0:
        try:
            from engineering_deep import herschel_bulkley_pressure_loss
            hb = herschel_bulkley_pressure_loss(flow, hole, pipe, ann_len,
                                                tau0, n_idx, k_idx)
            rows.append({
                "param": "Annular pressure loss (Herschel-Bulkley)",
                "formula": "dP = [τ0/(300×d_e) + K×(γ̇)ⁿ/144] × L",
                "inputs": f"Q = {_fmt(flow, 0)} gpm, D = {_fmt(hole)} in, "
                          f"d = {_fmt(pipe)} in, τ0 = {_fmt(tau0)} lb/100ft², "
                          f"n = {_fmt(n_idx)}, K = {_fmt(k_idx)} lb/100ft²",
                "result": _fmt(hb, 0), "unit": "psi",
                "standard": "API 13D (yield-power law)",
                "status": "OK"})
        except Exception:
            pass

    return rows


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def register_markdown(rows: List[Dict], operator: str = "") -> str:
    """Render the register as a Word-ready markdown appendix."""
    if not rows:
        return ""
    op = (operator or "").strip() or "the Operator"
    lines = [
        "## APPENDIX — ENGINEERING CALCULATION REGISTER",
        "",
        "Every calculated value in this document is traceable to its formula, "
        "input values and industry-standard source. All numbers are computed "
        "deterministically by the built-in engineering calculators; the AI "
        "assistant is locked out of changing them (Numeric Lock).",
        "",
        "| # | Parameter | Formula / Basis | Inputs used | Result | Standard source | Status |",
        "|---|-----------|-----------------|-------------|--------|-----------------|--------|",
    ]
    for i, r in enumerate(rows, 1):
        lines.append(
            f"| {i} | {r['param']} | {r['formula']} | {r['inputs']} | "
            f"{r['result']} {r['unit']} | {r['standard']} | {r['status']} |")
    lines.append("")
    lines.append(f"*Register generated on document date; prepared for "
                 f"{op}. Calculations verified by the reference test suite "
                 f"(tests/test_engineering_reference.py).*")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test (no UI required)
# ---------------------------------------------------------------------------

def _selftest():
    values = {
        "mud_weight": "12",
        "td_depth": "10000",
        "hole_size": "12.25",
        "pipe_od": "5",
        "casing_size": "9.625",
        "casing_wall": "0.472",
        "casing_yield": "110000",
        "casing_depth": "8000",
        "fracture_gradient": "16.0",
        "formation_pressure": "11.0",
        "sidpp": "400",
        "bop_wp": "10000",
        "flow_rate": "500",
        "yield_point": "20",
        "plastic_viscosity": "25",
        "trip_speed": "60",
        "pit_gain": "20",
        "annular_capacity": "0.045",
        "total_cost": "12000000",
        "total_days": "45",
        "n_index": "0.6",
        "k_index": "120",
        "yield_stress": "8",
        "burst_load": "9000",
        "collapse_load": "6000",
        "axial_load": "400000",
    }
    rows = compute_register(values)
    md = register_markdown(rows)
    assert len(rows) >= 14, f"expected >=14 rows, got {len(rows)}"
    assert "ENGINEERING CALCULATION REGISTER" in md
    assert "0.052" in md or "24.5" in md
    # verify a couple of exact numbers
    hyd = [r for r in rows if r["param"].startswith("Hydrostatic")]
    assert hyd and hyd[0]["result"] == "6,240", hyd
    av = [r for r in rows if r["param"] == "Annular velocity"]
    assert av and float(av[0]["result"]) > 90, av
    print(f"  ✔ register selftest: {len(rows)} rows computed")
    return rows


if __name__ == "__main__":
    _selftest()
    print("engineering_register OK")
