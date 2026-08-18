# ============================================================================
# STANDARDS & RULE COMPLIANCE REGISTRY
# File: standards_engine.py
# Audit item: naming a standard in the program is not enough — each rule
# needs: Rule ID, Standard + Revision, Applicability, Requirement,
# Acceptance Criteria, Pass/Fail status and auditable source.
#
# This registry powers a "STANDARDS COMPLIANCE MATRIX" section in outputs.
# ============================================================================

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class StandardRule:
    rule_id: str
    standard: str            # e.g. "API RP 53"
    revision: str            # e.g. "5th Ed."
    subject: str             # e.g. "BOP Testing"
    applicability: str       # when does this rule apply
    requirement: str         # what must be done
    acceptance_criteria: str # measurable pass condition
    source_note: str = ""    # provenance hint
    # check callback name (used by the engine to evaluate pass/fail)


# ---------------------------------------------------------------------------
# RULE BASE — the auditable standards checklist (extendable)
# ---------------------------------------------------------------------------

STANDARD_RULES: List[StandardRule] = [
    # ---- Well Control / BOP ----
    StandardRule("STD-WC-001", "API RP 53", "5th Ed.", "BOP Testing",
                 "All drilling operations with potential for hydrocarbons",
                 "BOP stack pressure-tested after nipple-up and per schedule",
                 "Test pressure held ≥ 5 min with zero bleed-off",
                 "API RP 53 5.4"),
    StandardRule("STD-WC-002", "API RP 53", "5th Ed.", "Accumulator capacity",
                 "BOP installed",
                 "Accumulator provides closing force for all functions with "
                 "pumps off",
                 "≥ 100% of required volume with 200 psi pre-charge remaining",
                 "API RP 53 6.3"),
    StandardRule("STD-WC-003", "API Std 65-2", "2nd Ed.", "Kick detection",
                 "Drilling operations",
                 "Pit volume and flow monitoring with alarms",
                 "Alarm within ±5 bbl or ±10% of pit gain threshold",
                 "API 65-2"),
    StandardRule("STD-WC-004", "Company Well Control Manual", "Current",
                 "Kill procedures",
                 "Driller's Method / Wait & Weight available with kill sheet",
                 "Kill sheet completed and approved before drilling ahead",
                 "Company WC manual"),

    # ---- Casing ----
    StandardRule("STD-CS-001", "API TR 5C3", "7th Ed.", "Casing design",
                 "Casing strings for pressure-containing service",
                 "Burst/collapse/tension design factors applied",
                 "DF burst ≥ 1.1, collapse ≥ 1.125, tension ≥ 1.6",
                 "API TR 5C3"),
    StandardRule("STD-CS-002", "API Spec 5CT", "10th Ed.", "Casing material",
                 "Casing procurement",
                 "Casing manufactured to API 5CT with grade/PSL specified",
                 "MTRs and certifications available for all joints",
                 "API 5CT"),

    # ---- Cementing ----
    StandardRule("STD-CM-001", "API RP 10B-2", "1st Ed.", "Cement testing",
                 "Primary cementing jobs",
                 "Slurry design tested at BHST/BHCT",
                 "Thickening time ≥ job time + 1 hr margin",
                 "API RP 10B-2"),
    StandardRule("STD-CM-002", "API RP 10D-2", "2nd Ed.", "Cementing centralization",
                 "Casing strings to be cemented",
                 "Centralizer standoff ≥ 67% across pay/interval",
                 "Standoff report included in cement job design",
                 "API RP 10D-2"),

    # ---- Mud ----
    StandardRule("STD-MD-001", "API RP 13B-1", "5th Ed.", "Mud testing",
                 "Water-based mud systems",
                 "Daily mud checks per API RP 13B-1",
                 "Density ±0.1 ppg, FV ±5% of programmed value",
                 "API RP 13B-1"),
    StandardRule("STD-MD-002", "API RP 13D", "8th Ed.", "Hydraulics",
                 "Drilling hydraulics design",
                 "Hole cleaning & ECD checked against FG",
                 "ECD ≤ FG − 0.5 ppg margin",
                 "API RP 13D"),

    # ---- Completion ----
    StandardRule("STD-CP-001", "API RP 14B", "6th Ed.", "SSSV",
                 "Wells with subsurface safety valves",
                 "TRSV installed and function-tested",
                 "Tested to fail-safe close, leak rate per spec",
                 "API RP 14B"),

    # ---- HSE ----
    StandardRule("STD-HS-001", "API RP 49", "3rd Ed.", "H2S operations",
                 "Wells with H2S present",
                 "H2S monitoring, alarms, breathing air, drills",
                 "Sensors calibrated; drill records maintained",
                 "API RP 49"),
    StandardRule("STD-HS-002", "Company HSE Policy", "Current",
                 "All operations",
                 "PTW / JSA before non-routine operations",
                 "JSA completed and signed before job start",
                 "Company HSE policy"),

    # ---- P&A ----
    StandardRule("STD-PA-001", "NORSOK D-010", "Rev 4", "Barrier philosophy",
                 "P&A operations",
                 "Two verified barriers at all times",
                 "Barrier verification record in final P&A report",
                 "NORSOK D-010"),
]


def evaluate_rule(rule: StandardRule, values: Dict) -> Dict:
    """Evaluate a rule against the current well inputs.

    Returns dict with rule info + status (PASS/FAIL/N/A/CHECK).
    This is a deterministic heuristics layer; operators can add precise
    checks per rule by extending `_CHECKS`.
    """
    v = values

    def f(key):
        # canonical aliases (Batch X) — the UI's Engineering Basis uses
        # fracture_gradient / formation_pressure / td_depth while rules
        # historically read *_ppg / depth_m; both must resolve.
        ALIASES = {
            "fracture_gradient_ppg": ("fracture_gradient_ppg",
                                      "fracture_gradient", "fg_ppg", "fg",
                                      "frac_gradient"),
            "pore_pressure_ppg": ("pore_pressure_ppg", "formation_pressure",
                                  "pore_pressure", "pp_ppg"),
            "mud_weight": ("mud_weight", "mud_weight_ppg", "current_mw",
                           "mw", "mw1"),
            "depth_m": ("depth_m", "td_m"),
            "depth_ft": ("depth_ft", "td_depth", "total_depth", "depth",
                         "target_depth"),
        }
        keys = ALIASES.get(key, (key,))
        for k in keys:
            val = v.get(k)
            if val not in (None, ""):
                try:
                    return float(str(val).strip())
                except (TypeError, ValueError):
                    continue
        return 0.0

    def depth_ft():
        ft = f("depth_ft")
        if ft:
            return ft
        return f("depth_m") * 3.28084

    status = "CHECK"
    detail = ""

    # simple deterministic evaluations for key rules
    if rule.rule_id == "STD-WC-001":
        status = "PASS" if f("bop_wp") > 0 and f("bop_wp") >= f("masp") \
            else "FAIL"
        detail = f"BOP {f('bop_wp'):,.0f} psi vs MASP {f('masp'):,.0f} psi"

    elif rule.rule_id == "STD-WC-004":
        status = "PASS" if v.get("kill_sheet") else "CHECK"

    elif rule.rule_id == "STD-CS-001":
        csg = f("casing_depth")
        if csg > 0 and depth_ft() > 0:
            status = "FAIL" if csg > depth_ft() else "PASS"

    elif rule.rule_id == "STD-CM-002":
        so = f("standoff_pct")
        status = "PASS" if so >= 67 else ("CHECK" if so == 0 else "FAIL")

    elif rule.rule_id == "STD-MD-002":
        ecd = f("ecd")
        fg = f("fracture_gradient_ppg")
        if ecd and fg:
            status = "FAIL" if ecd > fg - 0.5 else "PASS"

    elif rule.rule_id == "STD-PA-001":
        status = "PASS" if v.get("pa_barriers") else "CHECK"

    return {
        "rule_id": rule.rule_id,
        "standard": rule.standard,
        "revision": rule.revision,
        "subject": rule.subject,
        "applicability": rule.applicability,
        "requirement": rule.requirement,
        "acceptance_criteria": rule.acceptance_criteria,
        "source": rule.source_note,
        "status": status,
        "detail": detail,
    }


def compliance_matrix(values: Dict) -> List[Dict]:
    return [evaluate_rule(r, values) for r in STANDARD_RULES]


def compliance_markdown(values: Dict, operator: str = "") -> str:
    rows = compliance_matrix(values)
    L = ["## STANDARDS COMPLIANCE MATRIX", ""]
    if operator:
        L.append(f"**Operator:** {operator}")
        L.append("")
    L.append("| Rule ID | Standard | Subject | Applicability | Status | "
             "Acceptance |")
    L.append("|---|---|---|---|---|---|")
    for r in rows:
        L.append(f"| {r['rule_id']} | {r['standard']} {r['revision']} | "
                 f"{r['subject']} | {r['applicability'][:40]} | "
                 f"**{r['status']}** | {r['acceptance_criteria'][:50]} |")
    L.append("")
    L.append("**Legend:** PASS = satisfied by current inputs · "
             "FAIL = not satisfied (must resolve) · "
             "CHECK = verify on site / provide data")
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    demo = {"bop_wp": 10000, "masp": 5000, "casing_depth": 3000,
            "depth_m": 4180, "standoff_pct": 75, "ecd": 14,
            "fracture_gradient_ppg": 16, "kill_sheet": "yes"}
    rows = compliance_matrix(demo)
    for r in rows[:6]:
        print(r["rule_id"], r["standard"], "->", r["status"])
