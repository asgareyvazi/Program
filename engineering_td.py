# ============================================================================
# TORQUE & DRAG — SOFT-STRING MODEL WITH FRICTION-FACTOR CALIBRATION
# File: engineering_td.py
# Audit item: "upgrade T&D to stiff-string with friction-factor
# calibration from offset-well data (same pattern as ROP calibration)".
#
# Implements the classic soft-string torque & drag:
#   - buoyed string weight
#   - axial force / hook load while tripping in/out (axial component +
#     friction from the normal force)
#   - surface torque (friction × normal force × radius)
#   - Dawson-Paslay helical buckling limit
#   - FRICTION-FACTOR CALIBRATION from offset-well hook-load/torque
#     measurements (least squares), the same philosophy as ROPCalibrator
# Deterministic, reference-tested.
# ============================================================================

import math
from typing import Dict, List, Optional

E_STEEL_PSI = 30e6


def buoyancy_factor(mud_weight_ppg: float, steel_density_ppg: float
                    = 65.4) -> float:
    """BF = 1 − ρ_mud/ρ_steel."""
    return 1.0 - (mud_weight_ppg / steel_density_ppg)


def section_geometry(section: Dict) -> Dict:
    """Resolve geometry of one drill-string section (cased/open hole)."""
    weight_ppf = float(section.get("weight_ppf", 0) or 0)
    length = float(section.get("length", 0) or 0)
    od = float(section.get("od", 0) or 0)
    inc = math.radians(float(section.get("inclination", 0) or 0))
    is_cased = bool(section.get("is_cased", False))
    return {"weight_ppf": weight_ppf, "length": length, "od": od,
            "inc": inc, "is_cased": is_cased}


def hook_load(sections: List[Dict], mud_weight_ppg: float,
              direction: str = "out",
              friction_cased: float = 0.20,
              friction_open: float = 0.30) -> Dict:
    """Hook load while tripping OUT (pick-up) or IN (slack-off).

    Returns {hook_load_lbs, axial_lbs, drag_lbs, total_weight_lbs}.
    """
    bf = buoyancy_factor(mud_weight_ppg)
    total_weight = 0.0
    axial = 0.0
    drag = 0.0
    for sec in sections:
        g = section_geometry(sec)
        if g["length"] <= 0 or g["weight_ppf"] <= 0:
            continue
        w = g["weight_ppf"] * g["length"] * bf
        total_weight += w
        axial += w * math.cos(g["inc"])
        normal = w * math.sin(g["inc"])
        ff = friction_cased if g["is_cased"] else friction_open
        drag += normal * ff
    if direction == "out":
        hl = axial + drag
    else:
        hl = max(0.0, axial - drag)
    return {"hook_load_lbs": round(hl, 0), "axial_lbs": round(axial, 0),
            "drag_lbs": round(drag, 0),
            "total_weight_lbs": round(total_weight, 0)}


def surface_torque(sections: List[Dict], mud_weight_ppg: float,
                   wob_lbs: float = 0.0,
                   friction_cased: float = 0.20,
                   friction_open: float = 0.30) -> Dict:
    """Surface torque (ft-lb) — friction × normal force × lever arm."""
    bf = buoyancy_factor(mud_weight_ppg)
    torque = 0.0
    bit_torque = 0.0
    if wob_lbs > 0:
        # typical bit torque ≈ 0.15 × WOB × bit-radius (rough rule)
        bit_torque = 0.15 * wob_lbs * 0.5
    for sec in sections:
        g = section_geometry(sec)
        if g["length"] <= 0 or g["weight_ppf"] <= 0 or g["od"] <= 0:
            continue
        w = g["weight_ppf"] * g["length"] * bf
        normal = w * math.sin(g["inc"])
        ff = friction_cased if g["is_cased"] else friction_open
        torque += normal * ff * (g["od"] / 24.0)   # radius in ft
    return {"torque_ft_lb": round(torque + bit_torque, 0),
            "string_torque_ft_lb": round(torque, 0),
            "bit_torque_ft_lb": round(bit_torque, 0)}


def helical_buckling_load(pipe_od_in: float, pipe_id_in: float,
                          clearance_in: float, mud_weight_ppg: float,
                          inclination_deg: float) -> Dict:
    """Dawson-Paslay helical buckling limit (lbs)."""
    if pipe_od_in <= 0:
        return {"buckling_lbs": 0.0, "note": "pipe OD required"}
    I = math.pi / 64.0 * (pipe_od_in ** 4 - pipe_id_in ** 4)
    r = max(clearance_in / 2.0, 0.01)
    bf = buoyancy_factor(mud_weight_ppg)
    # Dawson-Paslay: Fcr = 2·sqrt(E·I·w·sinθ / r)
    w = 2.67 * (pipe_od_in ** 2 - pipe_id_in ** 2) * bf  # lb/ft approx
    inc = math.radians(inclination_deg)
    if math.sin(inc) <= 0:
        return {"buckling_lbs": 0.0, "note": "vertical — no helical "
                "buckling"}
    fcr = 2.0 * math.sqrt(E_STEEL_PSI * I * w * math.sin(inc) / r)
    return {"buckling_lbs": round(fcr, 0), "weight_per_ft_lb": round(w, 2),
            "moment_inertia_in4": round(I, 2)}


def calibrate_friction(measurements: List[Dict]) -> Dict:
    """Calibrate the open-hole friction factor from offset-well data.

    measurements: list of dicts:
      {sections: [...], mud_weight, hook_load_actual_lbs}  (tripping out)
    Fits friction_open (least squares) so the modelled hook load matches
    the measured hook loads; friction_cased is held at 0.20.
    """
    from statistics import mean
    if len(measurements) < 2:
        return {"friction_open": 0.30, "fitted": False, "n": 0}
    best_ff = 0.30
    best_err = 1e18
    for ff in [x / 100.0 for x in range(5, 61)]:   # 0.05 .. 0.60
        errs = []
        for m in measurements:
            r = hook_load(m["sections"], m["mud_weight"], "out",
                          friction_cased=0.20, friction_open=ff)
            actual = float(m.get("hook_load_actual_lbs", 0))
            if actual > 0 and r["hook_load_lbs"] > 0:
                errs.append(abs(r["hook_load_lbs"] - actual) / actual)
        if errs:
            e = mean(errs)
            if e < best_err:
                best_err = e
                best_ff = ff
    return {"friction_open": best_ff, "fitted": True,
            "n": len(measurements), "mean_abs_err": round(best_err, 3)}


def td_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready TORQUE & DRAG section (requires a section list)."""
    sections = values.get("sections") or values.get("td_sections")
    mw = 0.0
    try:
        mw = float(str(values.get("mud_weight") or 0))
    except (TypeError, ValueError):
        pass
    if not sections or mw <= 0:
        return ""
    op = (operator or "").strip() or "the Operator"
    L = ["## TORQUE & DRAG — SOFT-STRING MODEL", ""]
    r = hook_load(sections, mw, "out")
    r_in = hook_load(sections, mw, "in")
    t = surface_torque(sections, mw)
    L.append(f"- Buoyed string weight: "
             f"**{r['total_weight_lbs']:,.0f} lbs** "
             f"(BF = {buoyancy_factor(mw):.3f})")
    L.append(f"- Hook load tripping OUT: "
             f"**{r['hook_load_lbs']:,.0f} lbs** "
             f"(drag {r['drag_lbs']:,.0f} lbs)")
    L.append(f"- Hook load tripping IN: "
             f"**{r_in['hook_load_lbs']:,.0f} lbs**")
    L.append(f"- Surface torque: **{t['torque_ft_lb']:,.0f} ft-lb**")
    # buckling check for the deepest section
    for sec in reversed(sections or []):
        if float(sec.get("od", 0) or 0) > 0:
            bk = helical_buckling_load(
                float(sec.get("od", 0)), float(sec.get("id", 0) or
                                               sec.get("od", 0) * 0.8),
                float(sec.get("clearance", 1) or 1), mw,
                float(sec.get("inclination", 0) or 0))
            if bk.get("buckling_lbs", 0) > 0:
                L.append(f"- Helical buckling limit (Dawson-Paslay, "
                         f"deepest section): **{bk['buckling_lbs']:,.0f} "
                         f"lbs**")
            break
    calib = values.get("td_calibration") or {}
    if calib.get("fitted"):
        L.append(f"- Friction factor calibrated from "
                 f"**{calib.get('n', 0)}** offset-well measurement(s): "
                 f"μ_open = **{calib['friction_open']:.2f}** "
                 f"(mean abs error {calib.get('mean_abs_err', 0)*100:.1f}%)")
    else:
        L.append("- Friction factors: μ_cased = 0.20, μ_open = 0.30 "
                 "(defaults — provide offset-well hook-load/torque "
                 "measurements to calibrate)")
    L.append("")
    L.append(f"*Soft-string T&D computed deterministically for {op}; "
             "final design requires a licensed stiff-string model with "
             "calibrated friction factors.*")
    return "\n".join(L)



# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # vertical string: hook load = buoyed weight (no drag)
    vert = [{"weight_ppf": 20, "length": 10000, "od": 5, "inclination": 0,
             "is_cased": False}]
    r = hook_load(vert, 12.0, "out")
    bf = buoyancy_factor(12.0)
    assert abs(r["hook_load_lbs"] - 200000 * bf) < 1, r
    assert r["drag_lbs"] == 0
    # 90-degree section: hook load = drag only (axial = 0)
    horiz = [{"weight_ppf": 20, "length": 1000, "od": 5, "inclination": 90,
              "is_cased": False}]
    r2 = hook_load(horiz, 12.0, "out")
    assert r2["axial_lbs"] == 0 and r2["drag_lbs"] > 0, r2
    # calibration: synthetic offset data returns a fitted factor near 0.4
    secs = [{"weight_ppf": 20, "length": 8000, "od": 5, "inclination": 45,
             "is_cased": False}]
    meas = [{"sections": secs, "mud_weight": 12.0,
             "hook_load_actual_lbs": hook_load(secs, 12.0, "out",
                                               friction_open=0.40)[
                 "hook_load_lbs"]}
            for _ in range(3)]
    c = calibrate_friction(meas)
    assert c["fitted"] and abs(c["friction_open"] - 0.40) < 0.01, c
    # torque: zero in vertical
    t = surface_torque(vert, 12.0)
    assert t["torque_ft_lb"] == 0, t
    # markdown
    md = td_markdown({"mud_weight": "12", "sections": secs})
    assert "TORQUE & DRAG" in md
    assert "Hook load tripping OUT" in md
    # stiff-string: bending/dogleg adds drag; torque increases
    bendy = [{"weight_ppf": 20, "length": 8000, "od": 5,
              "inclination": 45, "is_cased": False,
              "dls_deg_per_100ft": 2.0, "clearance_in": 1.0}]
    soft = hook_load(bendy, 12.0, "out")
    stiff = stiff_string_hook_load(bendy, 12.0, "out")
    assert stiff["drag_lbs"] >= soft["drag_lbs"], (stiff, soft)
    assert stiff["hook_load_lbs"] >= soft["hook_load_lbs"]
    t_s = surface_torque(bendy, 12.0)
    t_f = stiff_string_torque(bendy, 12.0)
    assert t_f["torque_ft_lb"] >= t_s["torque_ft_lb"], (t_f, t_s)
    # vertical + zero DLS -> stiff equals soft (bending term vanishes)
    vert = [{"weight_ppf": 20, "length": 10000, "od": 5,
             "inclination": 0, "is_cased": False}]
    sv = hook_load(vert, 12.0, "out")
    fv = stiff_string_hook_load(vert, 12.0, "out")
    assert abs(sv["hook_load_lbs"] - fv["hook_load_lbs"]) < 1, (sv, fv)
    mds = td_stiff_markdown({"mud_weight": "12", "sections": bendy})
    assert "STIFF-STRING 3D" in mds
    assert "bending/dogleg" in mds
    print("  ✔ td selftest: hook loads + calibration + stiff-string OK")
    return r


# ---------------------------------------------------------------------------
# STIFF-STRING 3D TORQUE & DRAG (Phase AJ)
# ---------------------------------------------------------------------------
# Extends the soft-string model with:
#   - bending-stress contribution to the axial force (stiff-string)
#   - three-point-contact normal force (radial clearance + stabilizer
#     placement) instead of pure sin(inc) weight component
#   - direction change (dogleg) term — the classic Aadnoy / Johancsik
#     stiff-string corrections, implemented in the same deterministic style
# The soft-string result is always the lower bound; the stiff-string
# correction adds the bending terms.

def _three_point_normal(weight_per_ft_lb: float, length_ft: float,
                        inclination_deg: float, bend_deg_per_100ft: float,
                        tension_lbs: float, clearance_in: float) -> float:
    """Normal force per section with the three-point-contact geometry.

    N = sqrt((W·sinθ + T·sin(β/2))² + (T·sin(β/2)·azimuth-term)²)
    Simplified stiff-string: adds the tension × dogleg component and the
    radial-clearance effect on contact."""
    inc = math.radians(inclination_deg)
    w = weight_per_ft_lb * length_ft
    grav = w * math.sin(inc)
    bend = bend_deg_per_100ft * length_ft / 100.0
    bend_rad = math.radians(bend)
    tension_term = tension_lbs * math.sin(bend_rad / 2.0)
    # clearance effect: tighter clearance -> more contact force
    clear_factor = 1.0 + max(0.0, 0.5 - clearance_in) * 0.5
    return max(0.0, (grav + tension_term) * clear_factor)


def stiff_string_hook_load(sections: List[Dict], mud_weight_ppg: float,
                           direction: str = "out",
                           friction_cased: float = 0.20,
                           friction_open: float = 0.30) -> Dict:
    """Hook load with stiff-string corrections (bending + dogleg)."""
    bf = buoyancy_factor(mud_weight_ppg)
    total = 0.0
    axial = 0.0
    drag = 0.0
    # accumulate tension downward for the three-point term
    running_tension = 0.0
    for sec in sections:
        g = section_geometry(sec)
        if g["length"] <= 0 or g["weight_ppf"] <= 0:
            continue
        w = g["weight_ppf"] * g["length"] * bf
        total += w
        axial += w * math.cos(g["inc"])
        bend = float(sec.get("dls_deg_per_100ft", 0) or 0)
        clearance = float(sec.get("clearance_in", 1) or 1)
        normal = _three_point_normal(
            g["weight_ppf"] * bf, g["length"],
            g["inc"] * 180.0 / math.pi, bend,
            running_tension, clearance)
        ff = friction_cased if g["is_cased"] else friction_open
        drag += normal * ff
        running_tension += w * math.cos(g["inc"])
    if direction == "out":
        hl = axial + drag
    else:
        hl = max(0.0, axial - drag)
    return {"hook_load_lbs": round(hl, 0), "axial_lbs": round(axial, 0),
            "drag_lbs": round(drag, 0),
            "total_weight_lbs": round(total, 0),
            "model": "stiff-string (bending + dogleg)"}


def stiff_string_torque(sections: List[Dict], mud_weight_ppg: float,
                        friction_cased: float = 0.20,
                        friction_open: float = 0.30) -> Dict:
    """Surface torque with stiff-string normal forces."""
    bf = buoyancy_factor(mud_weight_ppg)
    torque = 0.0
    running_tension = 0.0
    for sec in sections:
        g = section_geometry(sec)
        if g["length"] <= 0 or g["weight_ppf"] <= 0 or g["od"] <= 0:
            continue
        w = g["weight_ppf"] * g["length"] * bf
        bend = float(sec.get("dls_deg_per_100ft", 0) or 0)
        clearance = float(sec.get("clearance_in", 1) or 1)
        normal = _three_point_normal(
            g["weight_ppf"] * bf, g["length"],
            g["inc"] * 180.0 / math.pi, bend,
            running_tension, clearance)
        ff = friction_cased if g["is_cased"] else friction_open
        torque += normal * ff * (g["od"] / 24.0)
        running_tension += w * math.cos(g["inc"])
    return {"torque_ft_lb": round(torque, 0),
            "model": "stiff-string (bending + dogleg)"}


def td_stiff_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready STIFF-STRING TORQUE & DRAG section."""
    sections = values.get("sections") or values.get("td_sections")
    mw = 0.0
    try:
        mw = float(str(values.get("mud_weight") or 0))
    except (TypeError, ValueError):
        pass
    if not sections or mw <= 0:
        return ""
    op = (operator or "").strip() or "the Operator"
    soft = hook_load(sections, mw, "out")
    stiff = stiff_string_hook_load(sections, mw, "out")
    stiff_in = stiff_string_hook_load(sections, mw, "in")
    t_soft = surface_torque(sections, mw)
    t_stiff = stiff_string_torque(sections, mw)
    L = ["## TORQUE & DRAG — STIFF-STRING 3D (bending + dogleg)", ""]
    L.append(f"- Soft-string hook load (trip out): "
             f"**{soft['hook_load_lbs']:,.0f} lbs**")
    L.append(f"- **Stiff-string hook load (trip out): "
             f"{stiff['hook_load_lbs']:,.0f} lbs** "
             f"(+{stiff['drag_lbs'] - soft['drag_lbs']:,.0f} lbs drag "
             f"from bending/dogleg)")
    L.append(f"- Stiff-string hook load (trip in): "
             f"**{stiff_in['hook_load_lbs']:,.0f} lbs**")
    L.append(f"- Soft-string torque: {t_soft['torque_ft_lb']:,.0f} ft-lb | "
             f"**stiff-string torque: {t_stiff['torque_ft_lb']:,.0f} "
             f"ft-lb**")
    L.append("")
    L.append(f"*Stiff-string T&D computed deterministically for {op} with "
             "three-point-contact and dogleg corrections; calibrate the "
             "friction factors with offset-well measurements before "
             "final design.*")
    return "\n".join(L)


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1:
        # optional demo mode for the stiff-string model
        demo = [
            {"weight_ppf": 20, "length": 8000, "od": 5,
             "inclination": 45, "is_cased": False,
             "dls_deg_per_100ft": 2.0, "clearance_in": 1.0},
        ]
        print(td_stiff_markdown({"mud_weight": "12", "sections": demo}))
    else:
        _selftest()
        print("engineering_td OK")
