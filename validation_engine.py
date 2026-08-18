# ============================================================================
# VALIDATION ENGINE — four-level engineering validation
# File: validation_engine.py
# P0 audit item (biggest gap): separate four validation levels and block
# Approval/Export on CRITICAL findings.
#
#   Level 1 — Schema        : type / range / unit checks
#   Level 2 — Logical       : structural contradictions
#   Level 3 — Engineering   : engineering consistency (ECD vs FG, BOP vs MASP...)
#   Level 4 — Operational   : execution readiness (acceptance criteria, H2S...)
#
# Severities: CRITICAL (blocks export/approval), HIGH (needs review),
#             MEDIUM (needs completion or risk acceptance),
#             LOW (improvement), INFO (informational)
# ============================================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from engineering_units import (DrillingConstants, hydrostatic_pressure,
                               maasp, kill_mud_weight)


# ---------------------------------------------------------------------------
# Canonical input aliases (Batch X)
# ---------------------------------------------------------------------------
# The UI, the wizard's Engineering Basis and legacy templates use several
# names for the same physical quantity (e.g. fracture_gradient vs
# fracture_gradient_ppg, td_depth vs total_depth).  These helpers read
# the first non-empty alias so validation always sees the user's value.

def _pf(data: Dict, *keys: str, default: float = 0.0) -> float:
    for k in keys:
        v = data.get(k)
        if v not in (None, ""):
            try:
                return float(str(v).strip())
            except (TypeError, ValueError):
                continue
    return default


def _depth_ft(data: Dict) -> float:
    """Canonical depth in feet.  Explicit-ft keys are used as-is;
    _m keys are converted; a bare small 'depth' follows td_depth (ft)."""
    ft = _pf(data, "depth_ft", "td_depth", "total_depth", "depth",
             "target_depth", "td_md")
    if ft:
        return ft
    m = _pf(data, "depth_m", "td_m")
    return m * 3.28084 if m else 0.0


def _shoe_ft(data: Dict) -> float:
    """Casing-shoe / shoe depth in feet (same convention as depth)."""
    return _pf(data, "casing_depth_ft", "shoe_depth_ft", "csg_depth",
               "casing_depth", "shoe_depth")


@dataclass
class Finding:
    level: str            # CRITICAL / HIGH / MEDIUM / LOW / INFO
    module: str
    code: str
    message: str
    hint: str = ""

    @property
    def is_blocking(self) -> bool:
        return self.level == "CRITICAL"

    def __repr__(self):
        return f"[{self.level}] {self.code}: {self.message}"


LEVEL_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


def _f(num, default=0.0):
    """Safely parse a numeric value (str/float/int/None).

    Also handles fractional sizes like '13-3/8"', '12-1/4"' and
    plain fractions '3/8'.
    """
    try:
        if num is None or num == "":
            return default
        if isinstance(num, (int, float)):
            return float(num)
        s = str(num).strip().replace('"', '').replace('in', '').replace('"', '')
        s = s.replace(",", "")
        if "-" in s and "/" in s:
            whole, frac = s.split("-", 1)
            n, d = frac.split("/", 1)
            return float(whole) + float(n) / float(d)
        if "/" in s:
            n, d = s.split("/", 1)
            return float(n) / float(d)
        return float(s)
    except (TypeError, ValueError):
        return default


def _s(val) -> str:
    return str(val or "").strip()


# ---------------------------------------------------------------------------
# LEVEL 1 — SCHEMA VALIDATION
# ---------------------------------------------------------------------------

def validate_schema(data: Dict) -> List[Finding]:
    f = []
    # positive numbers
    for key, label in (("total_depth", "Total Depth"), ("td_depth", "TD"),
                       ("depth", "Depth"), ("depth_m", "Depth (m)"),
                       ("target_depth", "Target Depth"),
                       ("mud_weight", "Mud Weight"), ("mw1", "Mud Weight 1"),
                       ("mw2", "Mud Weight 2"), ("mw3", "Mud Weight 3"),
                       ("bop_wp", "BOP Working Pressure"),
                       ("pump_pressure", "Pump Pressure"),
                       ("flow_rate", "Flow Rate")):
        v = _f(data.get(key), -1)
        if data.get(key) not in (None, "", 0, "0"):
            if v < 0:
                f.append(Finding("CRITICAL", "schema", f"SCHEMA-{key.upper()}",
                                 f"{label} must be a non-negative number.",
                                 f"Entered value: {data.get(key)!r}"))
    # units sanity — depths are handled canonically in ft (Batch X):
    # anything beyond ~60,000 ft (18 km) is suspicious
    depth_ft = _depth_ft(data)
    if depth_ft and depth_ft > 60000:
        f.append(Finding("MEDIUM", "schema", "SCHEMA-DEPTH-UNIT",
                         f"Depth ({depth_ft:,.0f} ft) is unusually large — "
                         "check that feet were not entered as meters.",
                         "If depth is in meters, use the depth_m field."))
    return f


# ---------------------------------------------------------------------------
# LEVEL 2 — LOGICAL VALIDATION
# ---------------------------------------------------------------------------

def validate_logical(data: Dict) -> List[Finding]:
    f = []
    depths = []
    for key, label in (("depth_ft", "Total Depth"),
                       ("td_depth", "Total Depth"),
                       ("total_depth", "Total Depth"),
                       ("depth", "Total Depth"),
                       ("target_depth", "Target Depth"),
                       ("depth_m", "Depth (m)"),
                       ("casing_depth_ft", "Casing Depth"),
                       ("casing_depth", "Casing Depth"),
                       ("shoe_depth", "Shoe Depth"),
                       ("window_depth", "Window Depth")):
        v = _f(data.get(key))
        if v > 0:
            # canonical feet: _m keys are converted, ft keys as-is
            if key in ("depth_m",):
                v = v * 3.28084
            depths.append((label, v))

    if len(depths) >= 2:
        # find any "casing/liner" depth greater than TD
        td = max(v for l, v in depths if l in
                 ("Total Depth", "TD", "Depth", "Target Depth"))
        for label, v in depths:
            if label in ("Casing Depth", "Shoe Depth", "Window Depth") \
                    and v > td * 1.01:
                f.append(Finding("CRITICAL", "logical", "LOGIC-CASING-TD",
                                 f"{label} ({v:,.0f}) exceeds TD "
                                 f"({td:,.0f}).",
                                 "Casing/liner shoe must be above TD."))
    # hole size vs casing size
    hole = _s(data.get("hole_size"))
    csg = _s(data.get("casing_size"))
    if hole and csg:
        h = _f(hole)
        c = _f(csg)
        if h and c and c >= h:
            f.append(Finding("CRITICAL", "logical", "LOGIC-HOLE-CASING",
                             f"Casing size ({csg}) is not smaller than hole "
                             f"size ({hole}).",
                             "Casing OD must be less than hole size."))
    return f


# ---------------------------------------------------------------------------
# LEVEL 3 — ENGINEERING VALIDATION
# ---------------------------------------------------------------------------

def validate_engineering(data: Dict) -> List[Finding]:
    f = []

    mw = _pf(data, "mud_weight", "mud_weight_ppg", "current_mw", "mw",
             "mw1")
    depth_ft = _depth_ft(data)

    # 1) hydrostatic / pressure window (aliases: UI uses
    #    formation_pressure / fracture_gradient — Batch X)
    pp_ppg = _pf(data, "pore_pressure_ppg", "formation_pressure",
                 "pore_pressure", "pp_ppg", "formation_pressure_ppg")
    fg_ppg = _pf(data, "fracture_gradient_ppg", "fracture_gradient",
                 "fg_ppg", "fg", "frac_gradient")
    if mw and pp_ppg and mw < pp_ppg:
        f.append(Finding("HIGH", "mud", "ENG-MW-PP",
                         f"Mud weight ({mw:g} ppg) is below pore pressure "
                         f"({pp_ppg:g} ppg) — influx/kick risk.",
                         "Raise mud weight or document a managed-pressure "
                         "approach."))
    if mw and fg_ppg and mw > fg_ppg:
        f.append(Finding("CRITICAL", "mud", "ENG-MW-FG",
                         f"Mud weight ({mw:g} ppg) exceeds fracture gradient "
                         f"({fg_ppg:g} ppg) — induced lost circulation.",
                         "Reduce mud weight or revise the casing program."))

    # 2) ECD vs FG (if ECD provided or estimable)
    ecd = _f(data.get("ecd"))
    if not ecd and mw:
        ecd = mw * 1.05  # rough estimate flag (not authoritative)
        ecd_est = True
    else:
        ecd_est = False
    if ecd and fg_ppg and ecd > fg_ppg:
        f.append(Finding(
            "CRITICAL", "hydraulics", "ENG-ECD-FG",
            f"ECD ({ecd:g} ppg) exceeds fracture gradient ({fg_ppg:g} ppg) "
            f"at this depth.",
            "Reduce flow rate/ROP, lower MW, or case off the weak zone."))

    # 3) BOP rating vs MASP
    bop = _f(data.get("bop_wp"))
    masp = _f(data.get("masp"))
    if not masp and fg_ppg and mw and depth_ft:
        shoe_ft = _shoe_ft(data)
        if shoe_ft:
            masp = maasp(fg_ppg, mw, shoe_ft)
    if bop and masp and bop < masp:
        f.append(Finding(
            "CRITICAL", "well_control", "ENG-BOP-MASP",
            f"BOP working pressure ({bop:g} psi) is below the maximum "
            f"anticipated surface pressure ({masp:g} psi).",
            "Upgrade BOP rating or revise the well design."))

    # 4) MAASP sanity
    if fg_ppg and mw and depth_ft:
        shoe_ft = _shoe_ft(data)
        if shoe_ft:
            m = maasp(fg_ppg, mw, shoe_ft)
            if m < 0:
                f.append(Finding("HIGH", "well_control", "ENG-MAASP-NEG",
                                 f"MAASP is negative ({m:g} psi) — mud weight "
                                 f"above fracture gradient at shoe.",
                                 "Check MW vs FG at the casing shoe."))

    # 5) Kill mud weight
    sidpp = _f(data.get("sidpp"))
    if sidpp and mw and depth_ft:
        kmw = kill_mud_weight(sidpp, depth_ft, mw)
        if kmw > 19.5:
            f.append(Finding("HIGH", "well_control", "ENG-KMW-HIGH",
                             f"Kill mud weight ({kmw:g} ppg) is very high — "
                             f"verify well design and casing integrity.",
                             "Check casing burst at kill weight."))

    # 6) Casing burst check (if size/weight/grade provided)
    csg = _s(data.get("casing_size"))
    csg_wt = _f(data.get("casing_weight"))
    csg_grade = _s(data.get("casing_grade"))
    if csg and csg_wt:
        from engineering_units import barlow_burst_pressure
        od = _f(csg)
        ys = {"H40": 40000, "J55": 55000, "K55": 55000, "L80": 80000,
              "N80": 80000, "C95": 95000, "T95": 95000,
              "P110": 110000, "Q125": 125000}.get(csg_grade.upper(), 80000)
        # wall thickness from weight (approx): wt = weight/(2.675*od... )
        # use nominal: w = (wt_ppf) / (2.675 * od) is not right; use
        # standard approx wt = ppf / (10.69 * (od - wt))... iterate
        wt = csg_wt / (10.69 * od)  # first-order approximation
        for _ in range(4):
            wt = csg_wt / (10.69 * (od - wt))
        burst = barlow_burst_pressure(od, wt, ys)
        if masp and burst and burst / (masp or 1) < 1.0:
            f.append(Finding(
                "CRITICAL", "casing", "ENG-CASING-BURST",
                f"Casing burst rating ({burst:,.0f} psi) is below the "
                f"maximum surface pressure ({masp:,.0f} psi).",
                "Select a higher grade/weight casing."))

    # 7) Gas migration / kick tolerance (qualitative)
    if not data.get("kick_tolerance") and mw and fg_ppg and depth_ft:
        f.append(Finding("LOW", "well_control", "ENG-KT-NOT-SET",
                         "Kick tolerance not explicitly provided/calculated.",
                         "Compute kick tolerance for the design casing shoe."))
    return f


# ---------------------------------------------------------------------------
# LEVEL 4 — OPERATIONAL READINESS
# ---------------------------------------------------------------------------

def validate_operational(data: Dict) -> List[Finding]:
    f = []
    # acceptance criteria
    if not _s(data.get("acceptance_criteria")):
        f.append(Finding("MEDIUM", "procedure", "OPS-ACCEPTANCE",
                         "No acceptance criteria defined for key operations.",
                         "Define measurable acceptance criteria (pressure "
                         "tests, returns, ROP targets)."))
    # H2S contingency
    if _s(data.get("h2s")) and _s(data.get("h2s")) not in ("0", "None", "none", "No"):
        if not _s(data.get("h2s_plan")):
            f.append(Finding("HIGH", "hse", "OPS-H2S-PLAN",
                             "H2S is present but no H2S contingency plan "
                             "field is set.",
                             "Add H2S monitoring, drills, escape routes and "
                             "breathing-air plan."))
    # BOP test schedule
    if not _s(data.get("bop_test_schedule")):
        f.append(Finding("LOW", "bop", "OPS-BOP-TEST",
                         "BOP test schedule not specified.",
                         "Define test frequency per company policy."))
    # equipment list
    if not _s(data.get("requirements")) and not _s(data.get("equipment_list")):
        f.append(Finding("MEDIUM", "logistics", "OPS-EQUIPMENT",
                         "Equipment/material requirements not listed.",
                         "Add the equipment & materials checklist."))
    # references
    if not _s(data.get("reference_docs")):
        f.append(Finding("LOW", "document", "OPS-REFS",
                         "No reference documents attached to this program.",
                         "Attach the governing standards/procedures."))
    return f


# ---------------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------------

def validate_well_data(data: Dict) -> List[Finding]:
    """Run all four validation levels and return sorted findings."""
    findings = (validate_schema(data) + validate_logical(data) +
                validate_engineering(data) + validate_operational(data))
    findings.sort(key=lambda x: LEVEL_ORDER.get(x.level, 9))
    return findings


def blocking_findings(findings: List[Finding]) -> List[Finding]:
    return [f for f in findings if f.is_blocking]


def findings_markdown(findings: List[Finding], operator: str = "") -> str:
    """Markdown section for the generated document (compliance record)."""
    if not findings:
        return ("## VALIDATION & COMPLIANCE\n\n"
                "No critical findings — the document passed the four-level "
                "engineering validation (schema, logical, engineering, "
                "operational readiness).\n")
    L = ["## VALIDATION & COMPLIANCE", ""]
    if operator:
        L.append(f"**Operator:** {operator}")
        L.append("")
    L.append("| Severity | Module | Finding |")
    L.append("|---|---|---|")
    for f in findings:
        L.append(f"| **{f.level}** | {f.module} | {f.message} |")
    L.append("")
    n_crit = len(blocking_findings(findings))
    if n_crit:
        L.append(f"**{n_crit} CRITICAL finding(s)** — these must be resolved "
                 "or formally accepted before the program is released.")
    else:
        L.append("No CRITICAL findings — document may proceed to "
                 "review/approval.")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    # quick demonstration
    demo = {
        "mud_weight": 12, "depth_m": 3000, "pore_pressure_ppg": 11,
        "fracture_gradient_ppg": 13.5, "bop_wp": 5000,
        "casing_depth": 2500, "shoe_depth": 2500, "h2s": "1%",
        "total_depth": 3200, "hole_size": '12-1/4"', "casing_size": '13-3/8"',
    }
    for f in validate_well_data(demo):
        print(f)
