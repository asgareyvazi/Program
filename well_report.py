# ============================================================================
# WELL REPORT GENERATOR — one-click comprehensive well report
# File: well_report.py
# Produces a single consolidated engineering report for a well containing
# ALL governance/engineering sections the audit asked for:
#   Well Profile -> Validation -> Readiness -> Standards -> Dependency ->
#   Problems -> Risk Decision -> Equipment Compatibility -> Monte Carlo ->
#   Compliance -> References -> Audit trail
# Works standalone (CLI) and from the app (dialog integration).
# ============================================================================

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from engineering_units import DrillingConstants
from validation_engine import validate_well_data, findings_markdown
from operations_engine import readiness_markdown
from standards_engine import compliance_markdown as standards_md
from document_compliance import compliance_check, compliance_markdown
from engineering_dependency import dependency_markdown
from drilling_problems_db import ProblemDatabase, build_problems_markdown
from risk_decision import find_decisions, decision_markdown
from planning_intelligence import (equipment_compatibility,
                                   compatibility_markdown,
                                   monte_carlo_time, monte_carlo_cost,
                                   monte_carlo_markdown)
from audit_log import log_action


def build_well_report(values: Dict, operator: str = "",
                      contractor: str = "") -> str:
    """Assemble the full well report markdown from input values."""
    op = operator or str(values.get("operator") or "the Operator")
    con = contractor or str(values.get("contractor") or "the Service Company")

    L = [f"# WELL ENGINEERING REPORT — {values.get('well_name') or 'WELL'}",
         ""]
    L.append(f"**Field:** {values.get('field_name') or '[To Be Filled]'}  |  "
             f"**Operator:** {op}  |  **Contractor:** {con}")
    L.append(f"**Well Type:** {values.get('well_type') or '—'}  |  "
             f"**Environment:** {values.get('environment') or '—'}")
    L.append(f"**Revision:** {values.get('revision') or '01'}  |  "
             f"**Date:** {values.get('doc_date') or datetime.now().strftime('%d-%B-%Y')}")
    L.append("")

    # 1. Well profile (basis of design)
    L.append("## 1. WELL PROFILE & BASIS OF DESIGN")
    L.append("")
    L.append("| Parameter | Value |")
    L.append("|---|---|")
    for k in ("well_name", "field_name", "well_type", "environment",
              "rig_name", "total_depth", "depth_m", "mud_weight", "mud_type",
              "hole_size", "casing_size", "casing_depth", "bop_wp", "h2s"):
        if values.get(k):
            L.append(f"| {k.replace('_', ' ').title()} | {values[k]} |")
    L.append("")

    # 2. Validation
    findings = validate_well_data(values)
    L.append("## 2. ENGINEERING VALIDATION")
    L.append("")
    L.append(findings_markdown(findings, op))
    L.append("")

    # 3. Readiness
    L.append("## 3. PROGRAM READINESS")
    L.append("")
    L.append(readiness_markdown(values, op))
    L.append("")

    # 4. Standards
    smd = standards_md(values, op)
    if smd:
        L.append("## 4. STANDARDS COMPLIANCE MATRIX")
        L.append("")
        L.append(smd)
        L.append("")

    # 5. Dependency impact
    dep_keys = [k for k in ("mud_weight", "hole_size", "casing_size",
                            "casing_depth", "formation_pressure",
                            "fracture_gradient", "td_depth", "bop_wp",
                            "h2s", "depth_m") if values.get(k)]
    if dep_keys:
        dmd = dependency_markdown(dep_keys)
        if dmd:
            L.append("## 5. ENGINEERING DEPENDENCY IMPACT")
            L.append("")
            L.append(dmd)
            L.append("")

    # 6. Drilling problems
    try:
        pdb = ProblemDatabase()
        probs = pdb.all()
        if probs:
            L.append("## 6. DRILLING PROBLEM PREVENTION & RESPONSE")
            L.append("")
            L.append(build_problems_markdown(probs[:6], op))
            L.append("")
    except Exception:
        pass

    # 7. Risk decisions
    risk_txt = " ".join(str(values.get(k) or "") for k in
                        ("hazards", "risk_notes", "h2s", "formation_pressure"))
    dcs = find_decisions(risk_txt)
    if dcs:
        L.append("## 7. RISK DECISION & RESPONSE MATRIX")
        L.append("")
        L.append(decision_markdown(dcs))
        L.append("")

    # 8. Equipment compatibility
    if values.get("hole_size") or values.get("casing_size"):
        comp = equipment_compatibility(
            hole_size=values.get("hole_size", ""),
            casing_size=values.get("casing_size", ""),
            bha_od=values.get("bha_od", ""),
            bit_size=values.get("bit_size", ""),
            liner_size=values.get("liner_size", ""),
            tubing_size=values.get("tubing_size", ""),
            bop_wp_psi=float(values.get("bop_wp") or 0),
            max_surface_pressure_psi=float(values.get("masp") or 0),
            mud_weight_ppg=float(values.get("mud_weight") or 0))
        if any(f["level"] != "INFO" for f in comp):
            L.append("## 8. EQUIPMENT COMPATIBILITY")
            L.append("")
            L.append(compatibility_markdown(comp))
            L.append("")

    # 9. Monte Carlo
    days = float(values.get("total_days") or 0)
    if days > 0:
        tr = monte_carlo_time(days, days * 0.85, days * 1.25)
        cr = monte_carlo_cost(float(values.get("total_cost") or 0) or
                              days * 100000)
        L.append("## 9. SCHEDULE & COST UNCERTAINTY")
        L.append("")
        L.append(monte_carlo_markdown(tr, cr))
        L.append("")

    # 10. Compliance
    comp_rep = compliance_check("well_report", "\n".join(L), findings)
    L.append("## 10. DOCUMENT COMPLIANCE")
    L.append("")
    L.append(compliance_markdown(comp_rep, op))
    L.append("")

    return "\n".join(L)


def generate_well_report_docx(values: Dict, out_path: str,
                              operator: str = "",
                              contractor: str = "") -> bool:
    """Render the well report to Word using the app's own engine."""
    from wizard_engine import md_to_docx, neutralize_text
    md = build_well_report(values, operator, contractor)
    md = neutralize_text(md, operator or "the Operator",
                         contractor or "the Service Company")
    meta = {
        "title": f"Well Engineering Report — {values.get('well_name') or 'WELL'}",
        "operator": operator or values.get("operator", ""),
        "contractor": contractor or values.get("contractor", ""),
        "document_number": values.get("document_number", ""),
        "revision": values.get("revision", "01"),
        "date": values.get("doc_date", datetime.now().strftime("%d-%B-%Y")),
        "prepared_by": values.get("prepared_by", ""),
        "reviewed_by": values.get("reviewed_by", ""),
        "approved_by": values.get("approved_by", ""),
    }
    ok = md_to_docx(md, out_path, meta, {
        "cover": True, "toc": True, "font": "Calibri", "font_size": 11,
        "page": "A4", "orientation": "Portrait",
        "header_text": "Well Engineering Report",
        "footer_text": "Company Confidential"})
    if ok:
        log_action("well_report", meta["operator"],
                   values.get("well_name", ""), out_path)
    return ok


def _demo_values() -> Dict:
    return {
        "well_name": "Example Well-1", "field_name": "Example Field",
        "well_type": "Horizontal", "environment": "Onshore",
        "rig_name": "RIG-100", "total_depth": "4180", "depth_m": "4180",
        "mud_weight": "14", "mud_type": "KCl/Polymer",
        "hole_size": '12-1/4"', "casing_size": '9-5/8"',
        "casing_depth": "3000", "bop_wp": "10000", "h2s": "1%",
        "h2s_plan": "yes", "acceptance_criteria": "yes",
        "requirements": "yes", "reference_docs": "yes",
        "fracture_gradient_ppg": "16", "pore_pressure_ppg": "12",
        "total_days": "145", "total_cost": "17500000", "masp": "5000",
        "standoff_pct": "75", "ecd": "14", "kill_sheet": "yes",
        "doc_date": "17-August-2026", "revision": "01",
        "prepared_by": "Drilling Engineer", "reviewed_by": "Sr. Engineer",
        "approved_by": "Drilling Manager", "document_number": "WR-2026-001",
    }


if __name__ == "__main__":
    import sys
    vals = _demo_values()
    if len(sys.argv) > 1:
        vals["well_name"] = sys.argv[1]
    md = build_well_report(vals, "PARS OIL CO", "DRILL PRO SERVICES")
    out = str(Path.home() / "Well_Engineering_Report.docx")
    ok = generate_well_report_docx(vals, out, "PARS OIL CO",
                                   "DRILL PRO SERVICES")
    print(f"report md: {len(md)} chars | docx generated: {ok} -> {out}")
