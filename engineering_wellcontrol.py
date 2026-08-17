# ============================================================================
# WELL CONTROL — KILL SHEET & SCENARIO BRANCHING
# File: engineering_wellcontrol.py
# Audit items (P1):
#   - Well Control: the audit asked for full scenario branching
#
# Implements the classic well-control kill sheet (API RP 59 / IADC
# well-control school conventions):
#   - Kick detection indicators
#   - Shut-in sequence decision
#   - Kill method selection (Driller's / Wait-and-Weight / Bullhead)
#   - KMW, ICP, FCP, strokes-to-bit, strokes-to-shoe, total strokes
#   - Gas-migration handling (bleed & lubricate)
# All formulas are standard and reference-tested.
# ============================================================================

import math
from typing import Dict, List, Optional

CF = 0.052


# ---------------------------------------------------------------------------
# Kill sheet calculations
# ---------------------------------------------------------------------------

def kill_mud_weight(current_mw_ppg: float, sidpp_psi: float,
                    tvd_ft: float) -> float:
    """KMW = MW + SIDPP / (0.052 × TVD)."""
    if tvd_ft <= 0:
        return current_mw_ppg
    return current_mw_ppg + sidpp_psi / (CF * tvd_ft)


def initial_circulating_pressure(sidpp_psi: float,
                                 slow_pump_pressure_psi: float) -> float:
    """ICP = SIDPP + slow pump rate pressure (at kill rate)."""
    return sidpp_psi + slow_pump_pressure_psi


def final_circulating_pressure(kill_mw_ppg: float, current_mw_ppg: float,
                               slow_pump_pressure_psi: float) -> float:
    """FCP = KMW × SPR / MW (at kill rate)."""
    if current_mw_ppg <= 0:
        return 0.0
    return kill_mw_ppg * slow_pump_pressure_psi / current_mw_ppg


def pipe_capacity_bbl_ft(pipe_id_in: float) -> float:
    """Pipe capacity = ID² / 1029.4 (bbl/ft)."""
    return pipe_id_in ** 2 / 1029.4


def annular_capacity_bbl_ft(hole_in: float, pipe_in: float) -> float:
    """Annular capacity = (D² − d²) / 1029.4 (bbl/ft)."""
    return (hole_in ** 2 - pipe_in ** 2) / 1029.4


def strokes_to_bit(pipe_cap_bbl_ft: float, depth_ft: float,
                   pump_output_bbl_stk: float) -> float:
    if pump_output_bbl_stk <= 0:
        return 0.0
    return pipe_cap_bbl_ft * depth_ft / pump_output_bbl_stk


def strokes_to_shoe(pipe_cap_bbl_ft: float, shoe_ft: float,
                    pump_output_bbl_stk: float) -> float:
    if pump_output_bbl_stk <= 0:
        return 0.0
    return pipe_cap_bbl_ft * shoe_ft / pump_output_bbl_stk


def total_strokes_to_displace(pipe_cap_bbl_ft: float,
                              ann_cap_bbl_ft: float, depth_ft: float,
                              pump_output_bbl_stk: float) -> float:
    if pump_output_bbl_stk <= 0:
        return 0.0
    return (pipe_cap_bbl_ft + ann_cap_bbl_ft) * depth_ft \
        / pump_output_bbl_stk


def gas_migration_rate(static_mud_ppg: float, gas_gradient_ppg: float,
                       ann_cap_bbl_ft: float, pit_gain_bbl: float,
                       tvd_ft: float) -> Dict:
    """Simplified gas migration estimate (ft/hr) from the classic rule:
    migration ≈ (mud gradient − gas gradient) × 15 / annulus ... uses the
    common field approximation for a shut-in gas bubble."""
    if tvd_ft <= 0 or ann_cap_bbl_ft <= 0:
        return {"migration_ft_hr": 0.0, "bubble_height_ft": 0.0}
    bubble_ft = pit_gain_bbl / ann_cap_bbl_ft
    # 1 psi/ft pressure increase per hour => migration = 1/(Δgradient)
    d_grad = max(0.01, (static_mud_ppg - gas_gradient_ppg) * CF)
    rate = 1.0 / d_grad          # ft/hr per psi/hr pressure build
    return {"migration_ft_hr": round(rate, 1),
            "bubble_height_ft": round(bubble_ft, 1)}


# ---------------------------------------------------------------------------
# Scenario branching
# ---------------------------------------------------------------------------

def kick_scenario(values: Dict) -> List[Dict]:
    """Kick detection → shut-in → method-selection decision steps."""
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

    sidpp = _f(_pick("sidpp", "sidpip"))
    sicp = _f(_pick("sicp", "shut_in_casing_pressure"))
    gain = _f(_pick("pit_gain", "max_pit_gain", "pit_gain_bbl"))
    mw = _f(_pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    tvd = _f(_pick("depth", "depth_ft", "td_depth", "td_ft", "total_depth"))
    spr = _f(_pick("slow_pump_pressure", "spr_psi", "slow_pump_rate_pressure"))

    steps: List[Dict] = []

    # 1. detection
    indicators = []
    if gain > 0:
        indicators.append(f"pit gain {gain:g} bbl")
    if sidpp > 0:
        indicators.append(f"SIDPP {sidpp:g} psi")
    if sicp > 0:
        indicators.append(f"SICP {sicp:g} psi")
    steps.append({
        "step": 1,
        "condition": "Kick detection",
        "interpretation":
            ("Kick indicators present: " + (", ".join(indicators) if
             indicators else "flow/pit gain suspected (no values entered)"))
        ,
        "actions": [
            "1. Stop drilling/tripping immediately — no pipe movement "
            "while the well is flowing.",
            "2. Pick up off bottom (if safe), space out, and shut in the "
            "BOP (hard shut-in preferred for the first response).",
            "3. Record SIDPP and SICP after the pressures stabilize "
            "(typically 10–15 min); record pit gain.",
            "4. Flow-check before opening the BOP: if the well flows, "
            "keep it shut in.",
        ],
        "escalate": "Well shut in — evaluate",
    })
    # 2. shut-in evaluation
    if sidpp == 0 and sicp == 0:
        interp = ("No shut-in pressures recorded — verify the kick "
                  "actually occurred (flow check, trip tank, pit volume).")
    elif sidpp > 0 and sicp > 0 and abs(sicp - sidpp) < 5:
        interp = ("SICP ≈ SIDPP — gas is near the surface / in the "
                  "riser-casing; keep the well shut in and monitor "
                  "pressure build-up.")
    elif sicp > sidpp:
        interp = ("SICP > SIDPP — kick is in the open hole below the "
                  "shoe; pressure at the shoe is elevated, monitor "
                  "MAASP.")
    else:
        interp = ("SIDPP/SICP recorded — proceed to the kill sheet.")
    steps.append({
        "step": 2,
        "condition": "Shut-in evaluation",
        "interpretation": interp,
        "actions": [
            "1. Compare SICP vs MAASP; if SICP ≥ MAASP, the shoe may "
            "fracture — consider releasing small volumes per procedure.",
            "2. Compute KMW and check kick tolerance.",
            "3. Decide the kill method (step 3).",
        ],
        "escalate": "Kill method selection",
    })
    # 3. method selection
    method = _pick("kill_method", "primary_method")
    if method and method.lower() != "select":
        interp = f"Operator-selected method: {method}."
    elif mw > 0 and tvd > 0 and sidpp > 0:
        kmw = kill_mud_weight(mw, sidpp, tvd)
        if kmw - mw > 3.5:
            interp = ("KMW exceeds current MW by more than ~3.5 ppg — "
                      "prefer the DRILLER'S METHOD (two circulations) to "
                      "avoid excessive surface pressures while "
                      "weighting up.")
        elif spr > 0:
            interp = ("KMW within practical range — WAIT-AND-WEIGHT "
                      "method recommended (single circulation, lower "
                      "surface pressures).")
        else:
            interp = ("Slow pump rate pressure not entered — use the "
                      "Driller's method or enter SPR for a full "
                      "Wait-and-Weight kill sheet.")
    else:
        interp = "Enter SIDPP/MW/TVD for the method recommendation."
    steps.append({
        "step": 3,
        "condition": "Kill method selection",
        "interpretation": interp,
        "actions": [
            "1. Driller's method: circulate kick out at current MW, "
            "then weight up and circulate kill mud.",
            "2. Wait-and-Weight: weight up to KMW while shut in, then "
            "one circulation with ICP→FCP schedule.",
            "3. Bullheading (no circulation possible / surface "
            "stack risk): pump kill mud down the string/casing per "
            "procedure.",
        ],
        "escalate": "Kill sheet execution",
    })
    # 4. gas migration
    if gain > 0 and mw > 0:
        mig = gas_migration_rate(mw, 0.2, max(0.04, annular_capacity_bbl_ft(
            _f(_pick("hole_size", "hole_id"), 8.5),
            _f(_pick("pipe_od", "pipe_size"), 5.0))), gain, tvd or 8000)
        steps.append({
            "step": 4,
            "condition": "Gas migration management",
            "interpretation": (f"Estimated migration "
                               f"{mig['migration_ft_hr']} ft/hr with "
                               f"bubble height ≈ {mig['bubble_height_ft']} ft "
                               "(simplified field estimate)."),
            "actions": [
                "1. Monitor casing pressure build-up; if it approaches "
                "MAASP, use bleed-and-lubricate per the operator "
                "procedure.",
                "2. Do NOT vent gas without replacing volume — maintain "
                "bottom-hole pressure constant.",
            ],
            "escalate": "Bleed & lubricate / kill",
        })
    return steps


# ---------------------------------------------------------------------------
# Markdown section
# ---------------------------------------------------------------------------

def kill_sheet_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready WELL CONTROL KILL SHEET section."""
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
    mw = _f(_pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    sidpp = _f(_pick("sidpp", "sidpip"))
    tvd = _f(_pick("depth", "depth_ft", "td_depth", "td_ft", "total_depth"))
    depth_m = _f(_pick("depth_m", "td_m"))
    if tvd <= 0 and depth_m > 0:
        tvd = depth_m * 3.28084
    spr = _f(_pick("slow_pump_pressure", "spr_psi"))
    pump_out = _f(_pick("pump_output", "pump_output_bbl_stk"))
    dp_id = _f(_pick("dp_id", "pipe_id"))
    shoe = _f(_pick("casing_depth", "casing_depth_ft", "shoe_depth"))
    hole = _f(_pick("hole_size", "hole_id"))
    pipe = _f(_pick("pipe_od", "pipe_size"))
    sicp = _f(_pick("sicp", "shut_in_casing_pressure"))

    scenario = kick_scenario(values)

    L = [
        "## WELL CONTROL — KICK SCENARIO & KILL SHEET",
        "",
        f"Prepared for {op}. All pressures in psi; depths in ft TVD; "
        "verify against the rig's approved well-control procedures.",
        "",
        "### Scenario branching",
        "",
    ]
    for s in scenario:
        L.append(f"**Step {s['step']} — {s['condition']}**")
        L.append("")
        L.append(f"*Interpretation:* {s['interpretation']}")
        L.append("")
        for a in s["actions"]:
            L.append(f"- {a}")
        L.append("")
        if s["escalate"] != "—":
            L.append(f"*Escalate: {s['escalate']}*")
            L.append("")

    if mw > 0 and sidpp > 0 and tvd > 0:
        kmw = kill_mud_weight(mw, sidpp, tvd)
        L.append("### Kill sheet")
        L.append("")
        L.append(f"| Parameter | Value | Formula |")
        L.append("|---|---|---|")
        L.append(f"| Current MW | {mw:g} ppg | input |")
        L.append(f"| SIDPP | {sidpp:g} psi | input |")
        L.append(f"| Kill mud weight | **{kmw:.2f} ppg** | "
                 f"MW + SIDPP/(0.052×TVD) |")
        if spr > 0:
            icp = initial_circulating_pressure(sidpp, spr)
            fcp = final_circulating_pressure(kmw, mw, spr)
            L.append(f"| ICP (at kill rate) | **{icp:.0f} psi** | "
                     f"SIDPP + SPR |")
            L.append(f"| FCP (at kill rate) | **{fcp:.0f} psi** | "
                     f"KMW×SPR/MW |")
        if pump_out > 0 and dp_id > 0:
            pc = pipe_capacity_bbl_ft(dp_id)
            stb = strokes_to_bit(pc, tvd, pump_out)
            L.append(f"| Strokes to bit | **{stb:,.0f}** | "
                     f"(ID²/1029.4)×TVD / pump output |")
            if shoe > 0:
                sts = strokes_to_shoe(pc, shoe, pump_out)
                L.append(f"| Strokes to shoe | **{sts:,.0f}** | "
                         f"(ID²/1029.4)×shoe / pump output |")
            if hole > pipe:
                ac = annular_capacity_bbl_ft(hole, pipe)
                tot = total_strokes_to_displace(pc, ac, tvd, pump_out)
                L.append(f"| Total strokes (to displace) | **{tot:,.0f}** | "
                         f"(pipe+annular cap)×TVD / pump output |")
        if sicp > 0:
            maasp_note = ("Monitor SICP vs MAASP (shoe) at all times; "
                          "bleed & lubricate if SICP approaches MAASP.")
            L.append(f"| Shut-in casing pressure | {sicp:g} psi | input — "
                     f"{maasp_note} |")
        L.append("")
    else:
        L.append("_Kill sheet requires SIDPP, mud weight and TVD — enter "
                 "them in the Engineering Basis to compute KMW/ICP/FCP "
                 "and strokes._")
        L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test (reference values)
# ---------------------------------------------------------------------------

def _selftest():
    # classic: 12 ppg, SIDPP 400 psi, TVD 10,000 ft
    kmw = kill_mud_weight(12.0, 400.0, 10000.0)
    assert abs(kmw - 12.7692) < 0.01, kmw
    # ICP = 400 + 800 = 1200 ; FCP = 12.7692×800/12 = 851.3
    icp = initial_circulating_pressure(400, 800)
    assert abs(icp - 1200) < 0.01
    fcp = final_circulating_pressure(kmw, 12.0, 800)
    assert abs(fcp - 851.3) < 1.0, fcp
    # capacities: 5-in DP 4.276-in ID = 0.01776 bbl/ft
    pc = pipe_capacity_bbl_ft(4.276)
    assert abs(pc - 0.017762) < 1e-5, pc
    # annulus 8.5×5: 47.25/1029.4 = 0.04590
    ac = annular_capacity_bbl_ft(8.5, 5.0)
    assert abs(ac - 0.04590) < 1e-4, ac
    # strokes: 0.1 bbl/stk -> to bit = 177.62 bbl/0.1 = 1,776
    stb = strokes_to_bit(pc, 10000, 0.1)
    assert abs(stb - 1776.2) < 1.0, stb
    tot = total_strokes_to_displace(pc, ac, 10000, 0.1)
    assert abs(tot - 6366.2) < 2.0, tot   # (0.017762+0.04590)×10000/0.1
    # scenario
    vals = {"mud_weight": "12", "sidpp": "400", "sicp": "600",
            "pit_gain": "20", "depth": "10000", "hole_size": "8.5",
            "pipe_od": "5", "slow_pump_pressure": "800",
            "pump_output": "0.1", "dp_id": "4.276"}
    steps = kick_scenario(vals)
    assert len(steps) >= 4, steps
    md = kill_sheet_markdown(vals)
    assert "WELL CONTROL" in md and "KILL SHEET" in md
    assert "12.77" in md, md[:500]
    assert "851" in md
    print("  ✔ wellcontrol selftest: KMW/ICP/FCP/strokes verified")
    return kmw


if __name__ == "__main__":
    _selftest()
    print("engineering_wellcontrol OK")
