# ============================================================================
# ENGINEERING SENSITIVITY ANALYSIS (TORNADO)
# File: engineering_sensitivity.py
# Professional add-on: which input parameters drive the design?
#
# For each key input, the value is varied by ±Δ and the effect on the
# derived engineering outputs (SPP, ECD, KMW, MAASP, cost) is recomputed
# with the real calculators.  Parameters are ranked by maximum impact —
# the top drivers are the ones that must be controlled and measured
# accurately on the rig.
#
# Deterministic, reference-tested.
# ============================================================================

from typing import Dict, List, Optional, Tuple

# parameter key -> (label, unit, relative delta)
PARAMETERS = [
    ("mud_weight", "Mud weight", "ppg", 0.10),
    ("flow_rate", "Flow / pump rate", "gpm", 0.10),
    ("depth", "Depth (TVD)", "ft", 0.05),
    ("casing_depth", "Casing depth", "ft", 0.10),
    ("fracture_gradient", "Fracture gradient", "ppg", 0.05),
    ("sidpp", "SIDPP", "psi", 0.20),
    ("total_days", "Duration", "days", 0.10),
    ("total_cost", "Total cost", "USD", 0.10),
]


def _f(v, d=0.0) -> float:
    try:
        s = str(v).strip()
        return float(s) if s else d
    except (TypeError, ValueError):
        return d


def _pick(values: Dict, *keys) -> str:
    for k in keys:
        s = str(values.get(k, "") or "").strip()
        if s:
            return s
    return ""


def _outputs(values: Dict) -> Dict[str, float]:
    """Derived outputs computable from the given values."""
    out: Dict[str, float] = {}
    try:
        from engineering_hydraulics import standpipe_pressure
        sp = standpipe_pressure(values)
        if sp["parts"]:
            out["spp_psi"] = sp["spp_psi"]
            out["ecd_ppg"] = sp["ecd_ppg"]
    except Exception:
        pass
    mw = _f(_pick(values, "mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    sidpp = _f(_pick(values, "sidpp", "sidpip"))
    tvd = _f(_pick(values, "depth", "depth_ft", "td_depth", "td_ft",
                   "total_depth"))
    if tvd <= 0 and _f(_pick(values, "depth_m", "td_m")) > 0:
        tvd = _f(_pick(values, "depth_m", "td_m")) * 3.28084
    if mw > 0 and sidpp > 0 and tvd > 0:
        from engineering_wellcontrol import kill_mud_weight
        out["kmw_ppg"] = kill_mud_weight(mw, sidpp, tvd)
    fg = _f(_pick(values, "fracture_gradient", "fg_ppg", "frac_gradient"))
    shoe = _f(_pick(values, "casing_depth", "casing_depth_ft",
                    "shoe_depth", "csg_depth"))
    if fg > 0 and mw > 0 and shoe > 0:
        from engineering_units import maasp
        out["maasp_psi"] = maasp(fg, mw, shoe)
    cost = _f(_pick(values, "total_cost", "estimated_cost", "afe_total"))
    if cost > 0:
        out["cost_usd"] = cost
    days = _f(_pick(values, "total_days", "duration_days", "days"))
    if cost > 0 and days > 0:
        out["cost_per_day_usd"] = cost / days
    return out


def sensitivity_analysis(values: Dict,
                         parameters: Optional[List[Tuple]] = None) -> Dict:
    """Rank parameters by maximum output impact (tornado)."""
    values = dict(values or {})
    base = _outputs(values)
    if not base:
        return {"outputs": {}, "rows": [], "top_parameters": [],
                "base": {}}
    rows: List[Dict] = []
    for key, label, unit, delta in (parameters or PARAMETERS):
        cur = _pick(values, key)
        if not cur:
            continue
        try:
            base_val = float(str(cur).strip())
        except (TypeError, ValueError):
            continue
        if base_val == 0:
            continue
        lo = dict(values)
        hi = dict(values)
        lo[key] = str(base_val * (1.0 - delta))
        hi[key] = str(base_val * (1.0 + delta))
        out_lo = _outputs(lo)
        out_hi = _outputs(hi)
        impacts = []
        for ok_, bv in base.items():
            if ok_ not in out_lo or ok_ not in out_hi:
                continue
            if bv == 0:
                continue
            d_lo = abs(out_lo[ok_] - bv) / abs(bv)
            d_hi = abs(out_hi[ok_] - bv) / abs(bv)
            impacts.append({"output": ok_, "impact": round(max(d_lo,
                                                               d_hi), 4)})
        if impacts:
            impacts.sort(key=lambda x: x["impact"], reverse=True)
            rows.append({
                "parameter": key, "label": label, "unit": unit,
                "delta": delta, "base_value": base_val,
                "max_impact": impacts[0]["impact"],
                "drives": impacts,
            })
    rows.sort(key=lambda r: r["max_impact"], reverse=True)
    n_crit = max(1, len(rows) // 3)
    for i, r in enumerate(rows):
        r["critical"] = i < n_crit
    return {"base": base, "rows": rows,
            "top_parameters": [r["label"] for r in rows if r["critical"]]}


def sensitivity_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready SENSITIVITY SCREENING (tornado) section."""
    op = (operator or "").strip() or "the Operator"
    res = sensitivity_analysis(values)
    if not res["rows"] or not res["base"]:
        return ""
    L = [
        "## SENSITIVITY SCREENING — INPUT DRIVERS (TORNADO)",
        "",
        "Each key input is varied by ±Δ around the base case and the "
        "effect on the derived outputs is recomputed with the built-in "
        "calculators. Parameters are ranked by maximum impact — the top "
        "drivers must be measured and controlled accurately.",
        "",
        "| Rank | Parameter | Base | ±Δ | Max output impact | Drives |",
        "|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(res["rows"], 1):
        drives = ", ".join(f"{d['output']} ({d['impact']*100:.0f}%)"
                           for d in r["drives"][:3])
        star = " ⭐" if r["critical"] else ""
        L.append(f"| {i} | {r['label']}{star} | {r['base_value']:g} "
                 f"{r['unit']} | ±{r['delta']*100:.0f}% | "
                 f"{r['max_impact']*100:.0f}% | {drives} |")
    L.append("")
    if res["top_parameters"]:
        L.append(f"**Control parameters:** "
                 f"{', '.join(res['top_parameters'])} — prioritize "
                 f"accurate measurement and contingency planning on "
                 f"these.")
        L.append("")
    L.append(f"*Sensitivity screening computed deterministically for {op}; "
             "impacts are first-order (one-at-a-time) and do not replace "
             "a full probabilistic analysis (see Monte-Carlo section).*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test (analytic expectations)
# ---------------------------------------------------------------------------

def _selftest():
    vals = {"mud_weight": "12", "plastic_viscosity": "25", "yield_point": "20",
            "flow_rate": "300", "hole_size": "8.5", "pipe_od": "5",
            "dp_id": "4.276", "tfa": "0.3312", "depth": "10000",
            "casing_depth": "4000", "casing_id": "8.921", "bha_od": "6.5",
            "bha_length": "600", "surface_type": "Type 2 (standard)",
            "sidpp": "400", "fracture_gradient": "16",
            "total_cost": "12000000", "total_days": "45"}
    res = sensitivity_analysis(vals)
    assert "spp_psi" in res["base"], res["base"]
    rows = {r["parameter"]: r for r in res["rows"]}
    # flow ±10% -> SPP impact in the 10..25% band (bit ~Q², pipe ~Q^1.8)
    imp = rows["flow_rate"]["max_impact"]
    assert 0.10 <= imp <= 0.25, imp
    # SIDPP ±20% -> KMW impact = 0.2×(400/520)/12.769 ≈ 1.2%
    kmw_row = [d for d in rows["sidpp"]["drives"] if d["output"] == "kmw_ppg"]
    assert kmw_row and abs(kmw_row[0]["impact"] - 0.012) < 0.002, kmw_row
    # cost ±10% -> cost impact exactly 10%
    cost_row = [d for d in rows["total_cost"]["drives"]
                if d["output"] == "cost_usd"]
    assert cost_row and abs(cost_row[0]["impact"] - 0.10) < 1e-6, cost_row
    # top parameters non-empty
    assert res["top_parameters"], res
    md = sensitivity_markdown(vals)
    assert "SENSITIVITY SCREENING" in md
    assert "Control parameters" in md
    print(f"  ✔ sensitivity selftest: {len(res['rows'])} parameters, "
          f"top = {res['top_parameters'][0]}")
    return res


if __name__ == "__main__":
    _selftest()
    print("engineering_sensitivity OK")
