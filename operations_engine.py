# ============================================================================
# READINESS SCORE + LESSONS LEARNED + NPT + PLAN vs ACTUAL
# File: operations_engine.py
# Audit items (P1):
#   - Program Readiness Score : completeness dashboard before approval
#   - Lessons Learned engine  : structured lessons applied to similar wells
#   - NPT Root Cause engine   : event -> cause -> cost -> corrective/preventive
#   - Plan vs Actual          : daily variance (depth/ROP/time/cost/events)
# ============================================================================

import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

APP_DIR = Path.home() / ".drilling_program"
OPS_DB = str(APP_DIR / "operations.db")

# ---------------------------------------------------------------------------
# READINESS SCORE
# ---------------------------------------------------------------------------

# (check_key, label, weight 0..3, category)
READINESS_CHECKS = [
    ("well_name", "Well name defined", 1, "Basis"),
    ("well_type", "Well type selected", 1, "Basis"),
    ("field_name", "Field selected", 1, "Basis"),
    ("total_depth", "Total depth defined", 2, "Basis"),
    ("formation_pressure", "Pore pressure defined", 3, "Pressure"),
    ("fracture_gradient", "Fracture gradient defined", 3, "Pressure"),
    ("mud_weight", "Mud weight defined", 3, "Mud"),
    ("mud_type", "Mud type selected", 1, "Mud"),
    ("hole_size", "Hole size defined", 2, "Architecture"),
    ("casing_size", "Casing size defined", 2, "Architecture"),
    ("casing_depth", "Casing depth defined", 2, "Architecture"),
    ("bop_wp", "BOP rating defined", 3, "Well Control"),
    ("h2s", "H2S assessment", 2, "HSE"),
    ("h2s_plan", "H2S contingency plan", 3, "HSE"),
    ("acceptance_criteria", "Acceptance criteria", 3, "Readiness"),
    ("requirements", "Equipment/material list", 2, "Readiness"),
    ("reference_docs", "Reference documents attached", 2, "Governance"),
    ("risk_assessment", "Risk assessment completed", 3, "Governance"),
    ("kick_tolerance", "Kick tolerance calculated", 3, "Well Control"),
    ("lot_fit", "LOT/FIT planned", 2, "Well Control"),
]

READINESS_CRITICAL = {k for k, _, w, _ in READINESS_CHECKS if w == 3}


def readiness_score(values: Dict) -> Dict:
    """Score a well program's completeness 0..100 with a per-category table."""
    total_w = 0
    got_w = 0
    missing = []
    done = []
    for key, label, w, cat in READINESS_CHECKS:
        total_w += w
        v = str(values.get(key) or "").strip()
        ok = bool(v) and v.lower() not in ("0", "none", "n/a", "na")
        if ok:
            got_w += w
            done.append((key, label, cat))
        else:
            missing.append((key, label, cat, w))
    pct = round(100 * got_w / total_w) if total_w else 0
    crit_missing = [label for key, label, cat, w in missing if w == 3]
    grade = ("NOT READY", "CRITICAL") if crit_missing else \
            ("READY" if pct >= 90 else ("REVIEW" if pct >= 70 else "NOT READY"))
    return {
        "score": pct,
        "grade": grade[0],
        "critical_missing": crit_missing,
        "missing": [label for _, label, _, _ in missing],
        "done": [label for _, label, _ in done],
        "total_checks": len(READINESS_CHECKS),
        "done_checks": len(done),
    }


def readiness_markdown(values: Dict, operator: str = "") -> str:
    r = readiness_score(values)
    L = ["## PROGRAM READINESS SCORE", ""]
    if operator:
        L.append(f"**Operator:** {operator}")
        L.append("")
    L.append(f"**Completeness: {r['score']}/100 — {r['grade']}**")
    L.append("")
    if r["critical_missing"]:
        L.append("**Critical missing items (must be completed before "
                 "approval):**")
        L.append("")
        for m in r["critical_missing"]:
            L.append(f"- [ ] {m}")
        L.append("")
    if r["missing"]:
        L.append("**Other missing items:**")
        L.append("")
        for m in r["missing"]:
            L.append(f"- [ ] {m}")
        L.append("")
    L.append(f"**Completed: {len(r['done'])}/{r['total_checks']} checks**")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# LESSONS LEARNED
# ---------------------------------------------------------------------------

class LessonsDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or OPS_DB
        APP_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create()

    def _create(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id TEXT, well_name TEXT, field TEXT,
                operation TEXT, category TEXT,
                lesson TEXT, cause TEXT, prevention TEXT,
                tags TEXT, created TEXT
            );
            CREATE TABLE IF NOT EXISTS npt_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id TEXT, well_name TEXT, date TEXT,
                start TEXT, end TEXT, duration_hr REAL,
                category TEXT, cause TEXT, subcause TEXT,
                direct_cost REAL, indirect_cost REAL,
                corrective TEXT, preventive TEXT, created TEXT
            );
            CREATE TABLE IF NOT EXISTS afe (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id TEXT, well_name TEXT, afe_number TEXT,
                budget_usd REAL, commitment_usd REAL, actual_usd REAL,
                forecast_usd REAL, date TEXT
            );
            CREATE TABLE IF NOT EXISTS materials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id TEXT, well_name TEXT, item TEXT, category TEXT,
                required_qty REAL, available_qty REAL, unit TEXT,
                eta_days REAL, critical INTEGER
            );
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id TEXT, well_name TEXT, date TEXT,
                depth_m REAL, rop_mhr REAL, wob REAL, rpm REAL,
                flow_gpm REAL, spp_psi REAL, torque REAL, hookload REAL,
                ecd_ppg REAL, mud_weight_ppg REAL,
                plan_depth_m REAL, plan_rop_mhr REAL,
                npt_hr REAL, remarks TEXT, created TEXT
            );
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ---- lessons ----

    def add_lesson(self, well_id="", well_name="", field="", operation="",
                   category="", lesson="", cause="", prevention="",
                   tags=""):
        cur = self.conn.execute(
            "INSERT INTO lessons (well_id, well_name, field, operation, "
            "category, lesson, cause, prevention, tags, created) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (well_id, well_name, field, operation, category, lesson,
             cause, prevention, tags, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return cur.lastrowid

    def lessons_for(self, field="", operation="", category="", limit=50):
        sql = "SELECT * FROM lessons WHERE 1=1"
        args = []
        if field:
            sql += " AND field=?"; args.append(field)
        if operation:
            sql += " AND operation=?"; args.append(operation)
        if category:
            sql += " AND category=?"; args.append(category)
        sql += " ORDER BY id DESC LIMIT ?"; args.append(limit)
        return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

    def lessons_markdown(self, field="", operation="") -> str:
        rows = self.lessons_for(field=field, operation=operation, limit=20)
        if not rows:
            return ""
        L = ["## LESSONS LEARNED (FROM SIMILAR OPERATIONS)", ""]
        for r in rows:
            L.append(f"- **{r['operation'] or 'Ops'}** — {r['lesson']}")
            if r["cause"]:
                L.append(f"  - Cause: {r['cause']}")
            if r["prevention"]:
                L.append(f"  - Prevention: {r['prevention']}")
        return "\n".join(L) + "\n"

    # ---- NPT ----

    def add_npt(self, well_id="", well_name="", date="", start="", end="",
                duration_hr=0.0, category="", cause="", subcause="",
                direct_cost=0.0, indirect_cost=0.0, corrective="",
                preventive=""):
        cur = self.conn.execute(
            "INSERT INTO npt_events (well_id, well_name, date, start, end, "
            "duration_hr, category, cause, subcause, direct_cost, "
            "indirect_cost, corrective, preventive, created) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (well_id, well_name, date, start, end, duration_hr, category,
             cause, subcause, direct_cost, indirect_cost, corrective,
             preventive, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return cur.lastrowid

    def npt_summary(self, well_id="") -> Dict:
        sql = "SELECT * FROM npt_events"
        args = []
        if well_id:
            sql += " WHERE well_id=?"; args.append(well_id)
        rows = self.conn.execute(sql, args).fetchall()
        total_hr = sum(r["duration_hr"] or 0 for r in rows)
        total_cost = sum((r["direct_cost"] or 0) + (r["indirect_cost"] or 0)
                         for r in rows)
        by_cause: Dict[str, float] = {}
        for r in rows:
            by_cause[r["cause"] or "Other"] = by_cause.get(
                r["cause"] or "Other", 0) + (r["duration_hr"] or 0)
        return {"events": len(rows), "total_hr": total_hr,
                "total_cost": total_cost,
                "by_cause": dict(sorted(by_cause.items(),
                                        key=lambda x: -x[1]))}

    # ---- daily / plan vs actual ----

    def add_daily(self, well_id="", well_name="", date="", depth_m=0.0,
                  rop_mhr=0.0, wob=0.0, rpm=0.0, flow_gpm=0.0, spp_psi=0.0,
                  torque=0.0, hookload=0.0, ecd_ppg=0.0, mud_weight_ppg=0.0,
                  plan_depth_m=0.0, plan_rop_mhr=0.0, npt_hr=0.0, remarks=""):
        cur = self.conn.execute(
            "INSERT INTO daily_reports (well_id, well_name, date, depth_m, "
            "rop_mhr, wob, rpm, flow_gpm, spp_psi, torque, hookload, ecd_ppg, "
            "mud_weight_ppg, plan_depth_m, plan_rop_mhr, npt_hr, remarks, "
            "created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (well_id, well_name, date, depth_m, rop_mhr, wob, rpm, flow_gpm,
             spp_psi, torque, hookload, ecd_ppg, mud_weight_ppg,
             plan_depth_m, plan_rop_mhr, npt_hr, remarks,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        return cur.lastrowid

    def plan_vs_actual(self, well_id="", limit=30) -> List[Dict]:
        sql = "SELECT * FROM daily_reports"
        args = []
        if well_id:
            sql += " WHERE well_id=?"; args.append(well_id)
        sql += " ORDER BY date LIMIT ?"; args.append(limit)
        out = []
        for r in self.conn.execute(sql, args).fetchall():
            d = dict(r)
            d["depth_variance_m"] = (r["depth_m"] or 0) - (r["plan_depth_m"] or 0)
            d["rop_variance"] = ((r["rop_mhr"] or 0) - (r["plan_rop_mhr"] or 0))
            out.append(d)
        return out

    # ---- AFE vs Actual (budget / commitment / actual / forecast) ----

    def add_afe(self, well_id="", well_name="", afe_number="",
                budget_usd=0.0, commitment_usd=0.0, actual_usd=0.0,
                forecast_usd=0.0, date=""):
        cur = self.conn.execute(
            "INSERT INTO afe (well_id, well_name, afe_number, budget_usd, "
            "commitment_usd, actual_usd, forecast_usd, date) "
            "VALUES (?,?,?,?,?,?,?,?)",
            (well_id, well_name, afe_number, budget_usd, commitment_usd,
             actual_usd, forecast_usd, date or
             datetime.now().strftime("%Y-%m-%d")))
        self.conn.commit()
        return cur.lastrowid

    def afe_status(self, well_id="") -> Dict:
        sql = "SELECT * FROM afe"
        args = []
        if well_id:
            sql += " WHERE well_id=?"; args.append(well_id)
        rows = self.conn.execute(sql, args).fetchall()
        if not rows:
            return {}
        budget = sum(r["budget_usd"] or 0 for r in rows)
        commit = sum(r["commitment_usd"] or 0 for r in rows)
        actual = sum(r["actual_usd"] or 0 for r in rows)
        forecast = sum(r["forecast_usd"] or 0 for r in rows)
        return {
            "budget_usd": budget, "commitment_usd": commit,
            "actual_usd": actual, "forecast_usd": forecast,
            "committed_pct": round(commit / budget * 100, 1) if budget else 0,
            "actual_pct": round(actual / budget * 100, 1) if budget else 0,
            "forecast_vs_budget_pct": round((forecast - budget) / budget * 100, 1)
            if budget else 0,
        }

    def afe_markdown(self, well_id="") -> str:
        a = self.afe_status(well_id)
        if not a:
            return ""
        L = ["## AFE vs ACTUAL — COST STATUS", "",
             "| Item | Amount (USD) | % of Budget |", "|---|---:|---:|",
             f"| AFE Budget | {a['budget_usd']:,.0f} | 100% |",
             f"| Committed | {a['commitment_usd']:,.0f} | "
             f"{a['committed_pct']}% |",
             f"| Actual | {a['actual_usd']:,.0f} | {a['actual_pct']}% |",
             f"| Forecast at Completion | {a['forecast_usd']:,.0f} | "
             f"{a['forecast_vs_budget_pct']:+.1f}% vs budget |"]
        L.append("")
        if a["forecast_vs_budget_pct"] > 5:
            L.append("⚠️ **Forecast exceeds budget — review cost control.**")
        L.append("")
        return "\n".join(L) + "\n"

    # ---- Material & Inventory Readiness ----

    def add_material(self, well_id="", well_name="", item="", category="",
                     required_qty=0.0, available_qty=0.0, unit="",
                     eta_days=0.0, critical=False):
        cur = self.conn.execute(
            "INSERT INTO materials (well_id, well_name, item, category, "
            "required_qty, available_qty, unit, eta_days, critical) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (well_id, well_name, item, category, required_qty, available_qty,
             unit, eta_days, int(critical)))
        self.conn.commit()
        return cur.lastrowid

    def material_readiness(self, well_id="") -> Dict:
        sql = "SELECT * FROM materials"
        args = []
        if well_id:
            sql += " WHERE well_id=?"; args.append(well_id)
        rows = self.conn.execute(sql, args).fetchall()
        if not rows:
            return {"items": [], "ready": 0, "short": 0, "critical_short": []}
        ready, short = [], []
        for r in rows:
            ok = (r["available_qty"] or 0) >= (r["required_qty"] or 0)
            (ready if ok else short).append(dict(r))
        return {
            "items": [dict(r) for r in rows],
            "ready": len(ready), "short": len(short),
            "critical_short": [r["item"] for r in short if r["critical"]],
        }

    def material_markdown(self, well_id="") -> str:
        m = self.material_readiness(well_id)
        if not m["items"]:
            return ""
        L = ["## MATERIAL & INVENTORY READINESS", "",
             "| Item | Category | Required | Available | Unit | Status |",
             "|---|---|---:|---:|---|---|"]
        for it in m["items"]:
            status = "✅" if it["available_qty"] >= it["required_qty"] else \
                     ("⛔" if it["critical"] else "⚠️")
            L.append(f"| {it['item']} | {it['category']} | "
                     f"{it['required_qty']:g} | {it['available_qty']:g} | "
                     f"{it['unit']} | {status} |")
        L.append("")
        if m["critical_short"]:
            L.append("⛔ **Critical items short:** " +
                     ", ".join(m["critical_short"]))
        L.append("")
        return "\n".join(L) + "\n"

    def variance_markdown(self, well_id="") -> str:
        rows = self.plan_vs_actual(well_id)
        if not rows:
            return ""
        L = ["## PLAN vs ACTUAL — DAILY VARIANCE", "",
             "| Date | Actual Depth (m) | Plan Depth (m) | Var (m) | "
             "Actual ROP | Plan ROP | NPT (hr) |", "|---|---:|---:|---:|---:|---:|---:|"]
        for r in rows:
            L.append(f"| {r['date'] or ''} | {r['depth_m'] or 0:,.0f} | "
                     f"{r['plan_depth_m'] or 0:,.0f} | "
                     f"{r['depth_variance_m']:+,.0f} | {r['rop_mhr'] or 0:g} | "
                     f"{r['plan_rop_mhr'] or 0:g} | {r['npt_hr'] or 0:g} |")
        L.append("")
        return "\n".join(L) + "\n"


if __name__ == "__main__":
    db = LessonsDatabase()
    # demo readiness
    demo = {"well_name": "W1", "well_type": "Horizontal", "mud_weight": "12",
            "bop_wp": "10000", "hole_size": '12-1/4"', "casing_size": '9-5/8"'}
    r = readiness_score(demo)
    print("readiness:", r["score"], r["grade"], "| critical missing:",
          len(r["critical_missing"]))
    # demo lessons + npt + daily
    db.add_lesson(well_name="W1", field="F", operation="Drilling",
                  category="Stuck Pipe",
                  lesson="Gumbo shale at 2500m caused pack-off — use "
                         "inhibitive mud and wiper trips",
                  cause="Gumbo / reactive shale",
                  prevention="KCl/Polymer mud, wiper trips each 150m",
                  tags="shale,pack-off")
    db.add_npt(well_name="W1", date="2026-08-16", duration_hr=12,
               category="Stuck Pipe", cause="Pack-off",
               direct_cost=200000, corrective="Pill + jarring",
               preventive="Better hole cleaning")
    db.add_daily(well_name="W1", date="2026-08-16", depth_m=3050,
                 plan_depth_m=3200, rop_mhr=14, plan_rop_mhr=18, npt_hr=12)
    print("lessons:", len(db.lessons_for(field="F")))
    print("npt summary:", db.npt_summary())
    print("plan vs actual rows:", len(db.plan_vs_actual()))
    db.close()
