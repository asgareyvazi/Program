# ============================================================================
# DAILY DRILLING REPORT — first-class Plan vs Actual workflow
# File: daily_report.py
# Phase AG — the daily report / plan-vs-actual structure existed in
# operations.db but had no first-class document workflow.  This module:
#   - builds a Word-ready DAILY DRILLING REPORT (morning-report style)
#   - renders a PLAN vs ACTUAL variance table with KPI flags
#   - aggregates NPT for the day and links to lessons learned
#   - exports the report to .docx via the shared renderer
# Deterministic, reference-tested.
# ============================================================================

from datetime import datetime
from typing import Dict, List, Optional

from operations_engine import LessonsDatabase


def plan_vs_actual_markdown(well_id: str = "", well_name: str = "",
                            operator: str = "", limit: int = 30) -> str:
    """Word-ready PLAN vs ACTUAL variance section from daily reports."""
    db = LessonsDatabase()
    try:
        rows = db.plan_vs_actual(well_id=well_id, limit=limit)
    finally:
        db.close()
    if not rows:
        return ""
    op = (operator or "").strip() or "the Operator"
    L = ["## PLAN vs ACTUAL — DAILY VARIANCE", ""]
    L.append(f"**Well:** {well_name or well_id or '—'}  |  "
             f"**Operator:** {op}  |  **Days reported:** {len(rows)}")
    L.append("")
    L.append("| Date | Depth (m) | Plan (m) | Var (m) | ROP (m/hr) | "
             "Plan ROP | NPT (hr) | Flag |")
    L.append("|---|---|---|---|---|---|---|---|")
    for r in rows:
        dv = r.get("depth_variance_m") or 0
        rv = r.get("rop_variance") or 0
        npt = r.get("npt_hr") or 0
        flags = []
        if abs(dv) >= 50:
            flags.append("⚠️ depth")
        if npt >= 8:
            flags.append("🕘 NPT")
        if rv <= -30:
            flags.append("🐢 ROP")
        L.append(f"| {r.get('date') or '—'} | "
                 f"{r.get('depth_m') or 0:,.0f} | "
                 f"{r.get('plan_depth_m') or 0:,.0f} | "
                 f"{dv:+,.0f} | {r.get('rop_mhr') or 0:g} | "
                 f"{r.get('plan_rop_mhr') or 0:g} | {npt:g} | "
                 f"{' '.join(flags) if flags else '✅'} |")
    # summary
    total_npt = sum(r.get("npt_hr") or 0 for r in rows)
    avg_var = sum(r.get("depth_variance_m") or 0 for r in rows) / len(rows)
    L.append("")
    L.append(f"**Totals:** NPT {total_npt:g} h over {len(rows)} day(s) | "
             f"average depth variance {avg_var:+,.0f} m")
    L.append("")
    L.append(f"*Plan-vs-actual computed deterministically for {op} from "
             "the daily-reports register; flags indicate where the plan "
             "needs revision.*")
    return "\n".join(L)


def daily_report_markdown(values: Dict, operator: str = "") -> str:
    """Full DAILY DRILLING REPORT (morning-report style) from one day of
    operations data."""
    op = (operator or "").strip() or "the Operator"
    well = values.get("well_name") or values.get("wellname") or "WELL"
    date = values.get("date") or values.get("report_date") or \
        datetime.now().strftime("%d-%B-%Y")
    con_name = values.get("contractor") or "the Service Company"
    L = [
        f"# DAILY DRILLING REPORT — {well}",
        "",
        f"**Date:** {date}  |  **Operator:** {op}  |  "
        f"**Contractor:** {con_name}",
        "",
        "## 1. OPERATIONS SUMMARY",
        "",
    ]
    if values.get("summary"):
        L.append(values["summary"])
        L.append("")
    else:
        L.append("_Summary of the day's operations._")
        L.append("")

    # depth / progress
    L.append("## 2. DEPTH & PROGRESS")
    L.append("")
    L.append("| Parameter | Value |")
    L.append("|---|---|")
    depth = values.get("depth_m") or values.get("depth") or ""
    plan = values.get("plan_depth_m") or ""
    rop = values.get("rop_mhr") or values.get("rop") or ""
    plan_rop = values.get("plan_rop_mhr") or ""
    L.append(f"| Depth (m) | {depth or '—'} |")
    L.append(f"| Planned depth (m) | {plan or '—'} |")
    if depth and plan:
        try:
            var = float(depth) - float(plan)
            L.append(f"| Variance (m) | **{var:+,.0f}** |")
        except (TypeError, ValueError):
            pass
    L.append(f"| ROP (m/hr) | {rop or '—'} |")
    L.append(f"| Planned ROP (m/hr) | {plan_rop or '—'} |")
    L.append("")

    # drilling parameters
    L.append("## 3. DRILLING PARAMETERS")
    L.append("")
    L.append("| Parameter | Value |")
    L.append("|---|---|")
    for key, label in (("wob", "WOB (klbf)"), ("rpm", "RPM"),
                       ("flow_gpm", "Flow (gpm)"),
                       ("spp_psi", "SPP (psi)"),
                       ("torque", "Torque (ft-lb)"),
                       ("hookload", "Hookload (klbs)"),
                       ("ecd_ppg", "ECD (ppg)"),
                       ("mud_weight_ppg", "Mud weight (ppg)")):
        if values.get(key) not in (None, ""):
            L.append(f"| {label} | {values[key]} |")
    L.append("")

    # NPT
    npt = values.get("npt_hr") or 0
    L.append("## 4. NPT & EVENTS")
    L.append("")
    try:
        npt = float(npt)
    except (TypeError, ValueError):
        npt = 0
    L.append(f"**NPT today: {npt:g} h**")
    if values.get("npt_cause"):
        L.append("")
        L.append(f"- Cause: {values['npt_cause']}")
    if values.get("remarks"):
        L.append("")
        L.append(f"- Remarks: {values['remarks']}")
    L.append("")

    # plan vs actual history
    pv = plan_vs_actual_markdown(
        well_id=str(values.get("well_id") or ""),
        well_name=well, operator=op)
    if pv:
        L.append(pv)
        L.append("")
    L.append("---")
    L.append("")
    L.append(f"*Daily report compiled for {op}; data from the daily-"
             "reports register (operations.db).*")
    return "\n".join(L)


def generate_daily_report_docx(values: Dict, out_path: str,
                               operator: str = "") -> str:
    """Render the daily report to a Word document."""
    from wizard_engine import md_to_docx
    md = daily_report_markdown(values, operator)
    meta = {"title": f"Daily Drilling Report",
            "operator": operator or "the Operator",
            "contractor": str(values.get("contractor") or ""),
            "date": str(values.get("date") or ""), "revision": "01",
            "document_number": ""}
    md_to_docx(md, out_path, meta, {})
    return out_path


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    import tempfile, os
    db = LessonsDatabase()
    db.add_daily(well_name="DR-WELL", date="2026-08-18", depth_m=3050,
                 rop_mhr=12, wob=20, rpm=100, flow_gpm=500, spp_psi=2500,
                 ecd_ppg=12.4, mud_weight_ppg=12,
                 plan_depth_m=3100, plan_rop_mhr=15, npt_hr=2,
                 remarks="Hard reaming in the 12.25 section")
    db.add_daily(well_name="DR-WELL", date="2026-08-17", depth_m=2950,
                 rop_mhr=14, plan_depth_m=3000, plan_rop_mhr=15, npt_hr=0)
    db.close()
    md = plan_vs_actual_markdown(well_name="DR-WELL")
    assert "PLAN vs ACTUAL" in md
    assert "2026-08-18" in md
    assert "NPT" in md
    full = daily_report_markdown({"well_name": "DR-WELL",
                                  "date": "2026-08-18",
                                  "depth_m": "3050", "plan_depth_m": "3100",
                                  "rop_mhr": "12", "wob": "20",
                                  "rpm": "100", "flow_gpm": "500",
                                  "spp_psi": "2500", "ecd_ppg": "12.4",
                                  "mud_weight_ppg": "12",
                                  "npt_hr": "2",
                                  "npt_cause": "Hard reaming",
                                  "remarks": "Monitor torque"})
    assert "DAILY DRILLING REPORT" in full
    assert "PLAN vs ACTUAL" in full
    assert "Variance (m)" in full
    tmp = tempfile.mkdtemp(prefix="drl_dr_")
    p = os.path.join(tmp, "dr.docx")
    generate_daily_report_docx({"well_name": "DR-WELL"}, p)
    assert os.path.exists(p)
    # cleanup
    db = LessonsDatabase()
    con = db.conn
    con.execute("DELETE FROM daily_reports WHERE well_name='DR-WELL'")
    con.commit()
    db.close()
    print("  ✔ daily report selftest: plan-vs-actual + docx OK")
    return md


if __name__ == "__main__":
    _selftest()
    print("daily_report OK")
