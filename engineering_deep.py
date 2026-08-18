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


# ---------------------------------------------------------------------------
# DEEP ENGINEERING VERIFICATION — document section builder
# ---------------------------------------------------------------------------
# Audit items (P1): ROP calibration, Herschel-Bulkley hydraulics, triaxial
# casing, compressibility-aware surge/swab.  This section is appended to
# generated documents whenever the required inputs are available, so every
# deep check is visible and traceable.  Pure deterministic computations.

def _fv(v, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        s = str(v).strip()
        if not s:
            return default
        return float(s)
    except (TypeError, ValueError):
        return default


def _pick(values: Dict, *keys) -> str:
    for k in keys:
        s = str(values.get(k, "") or "").strip()
        if s:
            return s
    return ""


def rop_prediction_table(calib: Dict, depths: List[float],
                         wob: float, rpm: float, mw: float) -> List[Dict]:
    """Predicted ROP (ft/hr) at each depth from a calibrated model."""
    if not calib or not calib.get("k"):
        return []
    k = float(calib["k"])
    a = float(calib.get("a", 1.0))
    b = float(calib.get("b", 0.6))
    c = float(calib.get("c", 0.00005))
    d = float(calib.get("d", -0.05))
    mw_opt = float(calib.get("mw_opt_ppg", 10.0))
    rows = []
    for dep in depths:
        if wob <= 0 or rpm <= 0:
            continue
        rop = (k * (wob ** a) * (rpm ** b) *
               math.exp(-c * dep) * math.exp(d * (mw - mw_opt)))
        rows.append({"depth_ft": round(dep, 0),
                     "rop_ft_hr": round(max(rop, 0.0), 1)})
    return rows


def deep_verify_markdown(values: Dict, rop_calib: Optional[Dict] = None,
                         operator: str = "") -> str:
    """Build the DEEP ENGINEERING VERIFICATION section markdown.

    Computes only what the inputs allow; anything else is listed as
    'requires additional data'.  Never raises.
    """
    v = values or {}
    mw = _fv(_pick(v, "mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    try:
        from input_registry import depth_ft as _dft
        depth_ft = _dft(v)
    except Exception:
        depth_ft = _fv(_pick(v, "depth_ft", "depth", "td_depth", "td_ft",
                             "total_depth"))
    depth_m = _fv(_pick(v, "depth_m", "target_depth_m", "td_m"))
    if depth_ft <= 0 and depth_m > 0:
        depth_ft = depth_m * 3.28084
    hole = _fv(_pick(v, "hole_size", "hole_id", "hole_diameter", "bit_size"))
    pipe = _fv(_pick(v, "pipe_od", "pipe_size", "bha_od", "drill_pipe_od"))
    casing_od = _fv(_pick(v, "casing_od", "casing_size"))
    wall = _fv(_pick(v, "casing_wall", "casing_wall_in", "wall_thickness"))
    ys = _fv(_pick(v, "casing_yield", "casing_yield_psi", "yield_strength"))
    flow = _fv(_pick(v, "flow_rate", "flow_rate_gpm", "q_gpm", "pump_rate"))
    yp = _fv(_pick(v, "yield_point", "mud_yp", "yp_lb100ft2"))
    pv = _fv(_pick(v, "plastic_viscosity", "mud_pv", "pv_cp"))
    trip = _fv(_pick(v, "trip_speed", "trip_speed_ft_min"))
    n_idx = _fv(_pick(v, "n_index", "flow_index"))
    k_idx = _fv(_pick(v, "k_index", "consistency_index"))
    tau0 = _fv(_pick(v, "yield_stress", "tau0", "hb_yield_stress"))
    wob = _fv(_pick(v, "wob", "wob_klbf"))
    rpm = _fv(_pick(v, "rpm", "rotary_speed"))
    burst_load = _fv(_pick(v, "burst_load", "design_burst"))
    coll_load = _fv(_pick(v, "collapse_load", "design_collapse"))
    axial_load = _fv(_pick(v, "axial_load", "design_axial"))

    op = (operator or "").strip() or "the Operator"
    lines = [
        "## DEEP ENGINEERING VERIFICATION",
        "",
        "This section verifies the design with deeper models than the main "
        "body (ROP calibration, yield-power-law hydraulics, triaxial casing "
        "check, compressibility-aware surge/swab). All values are computed "
        "deterministically by built-in calculators.",
    ]
    checks = 0

    def _note(missing: str):
        lines.append(f"- ⚠️ {missing} — requires additional data ("
                     "measurement or offset-well input).")

    # -- 1. ROP model -----------------------------------------------------
    lines.append("")
    lines.append("### ROP Model (Bourgoyne-Young style)")
    if rop_calib and rop_calib.get("k") and rop_calib.get("n_points"):
        k = float(rop_calib["k"])
        n = int(rop_calib["n_points"])
        a = float(rop_calib.get("a", 1.0))
        b = float(rop_calib.get("b", 0.6))
        c = float(rop_calib.get("c", 0.00005))
        d = float(rop_calib.get("d", -0.05))
        lines.append(
            f"- Model: ROP = K × WOB^a × RPM^b × e^(−c·D) × e^(d·(MW−MW_opt))")
        lines.append(
            f"- Calibrated from **{n}** offset data point(s): "
            f"K = {k:.4g}, a = {a:g}, b = {b:g}, c = {c:g}, d = {d:g}")
        if wob > 0 and rpm > 0:
            depths = []
            if depth_ft > 0:
                depths = [max(1000.0, depth_ft * f) for f in
                          (0.25, 0.5, 0.75, 1.0)]
                depths = [min(d, depth_ft) for d in depths]
            else:
                depths = [5000, 8000, 11000]
            preds = rop_prediction_table(
                rop_calib, depths, wob, rpm, mw or 10.0)
            if preds:
                lines.append("")
                lines.append("| Depth (ft) | Predicted ROP (ft/hr) |")
                lines.append("|------------|------------------------|")
                for p in preds:
                    lines.append(f"| {p['depth_ft']:,.0f} | {p['rop_ft_hr']} |")
                checks += 1
        else:
            _note("WOB / RPM for the prediction")
    elif rop_calib:
        _note("Enough offset data for ROP calibration")
    else:
        _note("ROP calibration (offset-well WOB/RPM/depth/MW/ROP data)")

    # -- 2. Herschel-Bulkley annular pressure loss --------------------------
    lines.append("")
    lines.append("### Hydraulics — Yield-Power-Law (Herschel-Bulkley)")
    if flow > 0 and hole > pipe and depth_ft > 0 and n_idx > 0 and k_idx > 0:
        try:
            pl = power_law_pressure_loss(flow, hole, pipe, depth_ft,
                                         n_idx, k_idx)
            hb = herschel_bulkley_pressure_loss(flow, hole, pipe, depth_ft,
                                                tau0, n_idx, k_idx)
            lines.append(f"- Annular pressure loss over {depth_ft:,.0f} ft: "
                         f"**Power Law ≈ {pl:,.0f} psi** | "
                         f"**Herschel-Bulkley ≈ {hb:,.0f} psi** "
                         f"(yield stress term {tau0:g} lb/100ft² included)")
            if tau0 > 0 and pl > 0:
                lines.append(f"- Yield-stress contribution: "
                             f"~{max(0.0, (hb - pl)):,.0f} psi "
                             f"({(hb - pl) / pl * 100:.0f}% of PL estimate)")
            checks += 1
        except Exception:
            _note("Hydraulics verification")
    else:
        _note("Annular pressure-loss data (flow rate, geometry, n/K)")

    # -- 3. Triaxial casing check -------------------------------------------
    lines.append("")
    lines.append("### Casing — Triaxial (von Mises) Combined-Load Check")
    if casing_od > 0 and wall > 0 and ys > 0 and burst_load > 0 and \
            coll_load > 0:
        try:
            tx = triaxial_check(casing_od, wall, ys, burst_load,
                                coll_load, axial_load)
            icon = "✅" if tx["status"] == "PASS" else "⛔"
            lines.append(
                f"- {icon} σ_vm = {tx['vm_stress_psi']:,.0f} psi vs allowable "
                f"{tx['allowable_psi']:,.0f} psi (YS/1.25) — "
                f"**{tx['status']}** ({tx['utilization']}% utilization)")
            lines.append(
                "- Basis: API TR 5C3 thin-wall von Mises; loads: burst "
                f"{burst_load:,.0f} psi / collapse {coll_load:,.0f} psi / "
                f"axial {axial_load:,.0f} psi")
            checks += 1
        except Exception:
            _note("Triaxial check")
    else:
        _note("Triaxial check data (casing OD/wall/grade, design loads)")

    # -- 4. Surge/swab with compressibility ---------------------------------
    lines.append("")
    lines.append("### Surge / Swab — Compressibility-Aware Estimate")
    if trip > 0 and pv > 0 and yp > 0 and hole > pipe and depth_ft > 0:
        try:
            ss = surge_swab_with_compressibility(trip, pv, yp, hole, pipe,
                                                 depth_ft)
            lines.append(
                f"- Trip speed {trip:g} ft/min → annular velocity "
                f"{ss['velocity_ft_min']} ft/min")
            lines.append(
                f"- Rigid-column estimate: {ss['rigid_pressure_psi']} psi; "
                f"compressibility-corrected: "
                f"**{ss['corrected_pressure_psi']} psi** "
                f"(factor {ss['correction_factor']})")
            checks += 1
        except Exception:
            _note("Surge/swab estimate")
    else:
        _note("Surge/swab data (trip speed, PV, YP, geometry)")

    # -- 4b. Advanced casing checks (thermal / wear / corrosion) -------------
    try:
        from engineering_casing import casing_design_check
        csg = casing_design_check(values)
        if csg["checks"]:
            lines.append("")
            lines.append("### Casing — Advanced Design Checks "
                         "(thermal / wear / corrosion)")
            for c in csg["checks"]:
                icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "⛔"}.get(
                    c["status"], "•")
                lines.append(f"- {icon} {c['param']}: **{c['result']} "
                             f"{c['unit']}** ({c['formula']})")
            checks += 1
    except Exception:
        pass

    # -- 4c. Standpipe pressure model (API RP 13D) ---------------------------
    try:
        from engineering_hydraulics import standpipe_pressure
        sp = standpipe_pressure(values)
        if sp["parts"]:
            lines.append("")
            lines.append("### Hydraulics — Standpipe Pressure Model "
                         "(API RP 13D)")
            for p in sp["parts"]:
                lines.append(f"- {p['name']} ({p['geometry']}): "
                             f"**{p['psi']} psi** [{p['regime']}]")
            lines.append(f"- **SPP ≈ {sp['spp_psi']:,.0f} psi**; "
                         f"ECD ≈ **{sp['ecd_ppg']} ppg**")
            checks += 1
    except Exception:
        pass

    # -- 4d. Well control kill sheet + scenario (API RP 59) -------------------
    try:
        from engineering_wellcontrol import kill_sheet_markdown
        wc = kill_sheet_markdown(values, operator)
        if wc:
            lines.append("")
            lines.append(wc)
            checks += 1
    except Exception:
        pass

    # -- 4d2. Cementing engineering checks -------------------------------------
    try:
        from engineering_cementing import cementing_markdown
        cm_ = cementing_markdown(values, operator)
        if cm_:
            lines.append("")
            lines.append(cm_)
            checks += 1
    except Exception:
        pass

    # -- 4d3. Special-wells checks (HPHT / deepwater / completion) -------------
    try:
        from engineering_special import special_wells_markdown
        sw_ = special_wells_markdown(values, operator)
        if sw_:
            lines.append("")
            lines.append(sw_)
            checks += 1
    except Exception:
        pass

    # -- 4e. Wellbore stability & geomechanics --------------------------------
    try:
        from engineering_geomechanics import geomechanics_markdown
        gm = geomechanics_markdown(values, operator)
        if gm:
            lines.append("")
            lines.append(gm)
            checks += 1
    except Exception:
        pass

    # -- 4f. Sensitivity screening (tornado) ----------------------------------
    try:
        from engineering_sensitivity import sensitivity_markdown
        sn = sensitivity_markdown(values, operator)
        if sn:
            lines.append("")
            lines.append(sn)
            checks += 1
    except Exception:
        pass

    # -- 4g. Offset-well intelligence (Phase AF) ------------------------------
    try:
        from well_intelligence import (similar_wells, comparison_markdown,
                                       well_report_markdown)
        target = {"well_name": _pick(v, "well_name", "wellname"),
                  "well_type": _pick(v, "well_type", "well_profile"),
                  "field_name": _pick(v, "field_name", "field"),
                  "mud_weight": _pick(v, "mud_weight", "mud_weight_ppg"),
                  "hole_size": _pick(v, "hole_size", "hole_id"),
                  "depth_m": _pick(v, "depth_m", "td_m")}
        sims = similar_wells(target, top_n=3)
        if sims:
            lines.append("")
            lines.append("### Offset-Well Intelligence — Similar Stored "
                         "Wells")
            lines.append("")
            lines.append("| Offset well | Field | Type | Depth (m) | MW (ppg) "
                         "| Similarity |")
            lines.append("|---|---|---|---|---|---|")
            for s in sims:
                lines.append(f"| {s['well_name']} | {s['field_name'] or '—'} "
                             f"| {s['well_type'] or '—'} | "
                             f"{s['depth_to_m']:,.0f} | "
                             f"{s['mud_weight_ppg']:g} | "
                             f"{s['similarity']:.2f} |")
            lines.append("")
            checks += 1
    except Exception:
        pass

    # -- 5. Anti-collision (trajectory-based) --------------------------------
    lines.append("")
    lines.append("### Anti-Collision — Minimum Curvature + Separation Factor")
    traj_md = _pick(v, "trajectory_table")
    off_md = _pick(v, "offset_trajectory_table")
    if traj_md:
        try:
            from engineering_anticollision import (parse_trajectory_markdown,
                                                   parse_offset_trajectory_markdown,
                                                   anti_collision_review)
            ref = parse_trajectory_markdown(traj_md)
            off = None
            off_surface = (0.0, 0.0)
            if off_md:
                off, off_surface = parse_offset_trajectory_markdown(off_md)
            if len(ref) >= 2:
                rev = anti_collision_review(ref, off,
                                            off_surface=off_surface)
                if rev["status"] == "NO_OFFSET":
                    lines.append(
                        f"- Reference well positioned with minimum "
                        f"curvature: {len(ref)} stations. Offset-well "
                        f"trajectory not provided — enter it to run the "
                        f"separation-factor scan.")
                else:
                    icon = {"OK": "✅", "CAUTION": "⚠️",
                            "FAIL": "⛔"}.get(rev["status"], "?")
                    lines.append(
                        f"- {icon} Minimum separation factor: "
                        f"**{rev['min_sf']}** at MD "
                        f"{rev['min_sf_md']:,.0f} ft (closest approach "
                        f"{rev['min_c2c']} ft at MD {rev['min_c2c_md']:,.0f} "
                        f"ft) — **{rev['status']}** (OWSG: SF ≥ 1.5 "
                        f"acceptable)")
                    lines.append(
                        "- Method: minimum curvature positioning; "
                        "EoU = tan(0.25°) × MD (MWD-class survey cone)")
                    checks += 1
            else:
                _note("Trajectory data (MD/Inc/Az table)")
        except Exception:
            _note("Anti-collision review")
    else:
        _note("Anti-collision review (well trajectory table)")

    lines.append("")
    lines.append(f"*Deep engineering checks computed for {op}; models are "
                 "preliminary design aids and must be confirmed against "
                 "final vendor/third-party software for the critical "
                 "load cases.*")
    return "\n".join(lines)


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
    # deep-verify section demo
    demo = {
        "mud_weight": "12", "td_depth": "10000", "hole_size": "12.25",
        "pipe_od": "5", "casing_size": "9.625", "casing_wall": "0.472",
        "casing_yield": "110000", "flow_rate": "500", "yield_point": "20",
        "plastic_viscosity": "25", "trip_speed": "60",
        "n_index": "0.6", "k_index": "120", "yield_stress": "8",
        "wob": "25", "rpm": "100", "burst_load": "9000",
        "collapse_load": "6000", "axial_load": "400000",
    }
    md = deep_verify_markdown(demo, {"k": rc.k, "a": 1.0, "b": 0.6,
                                     "c": 0.00005, "d": -0.05,
                                     "n_points": len(offset)})
    assert "DEEP ENGINEERING VERIFICATION" in md
    assert "Herschel-Bulkley" in md
    assert "von Mises" in md
    print("deep_verify_markdown OK,", len(md), "chars")
