# ============================================================================
# TEMPLATE & PROCEDURE AUDIT — automatic placeholder/schema QA
# File: tests/template_audit.py
#
# For EVERY wizard template and EVERY database procedure:
#   1. extract placeholders from the body ({{x}} and {x})
#   2. compare against the declared input schema
#   3. find: missing inputs (placeholder without an InputSpec),
#            unused inputs (declared but never referenced),
#            syntax inconsistencies (single-brace in wizard templates,
#            double-brace in DB procedures — both are now supported, so
#            this is informational)
#   4. render with synthetic values and scan for unresolved placeholders
#   5. report PASS / FAIL / WARN per item
#
# Writes: audit_report.md + audit_report.json in the repo root.
# Run:    python3 tests/template_audit.py
# ============================================================================

import json
import os
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wizard_library import ALL_TEMPLATES
from wizard_procedures import PROCEDURE_TEMPLATES
from wizard_offshore import OFFSHORE_TEMPLATES
from wizard_master import build_master_templates
from wizard_engine import scan_unresolved_placeholders, fill_template

DB = Path.home() / ".drilling_program" / "procedures.db"
OUT_MD = Path(__file__).parent.parent / "audit_report.md"
OUT_JSON = Path(__file__).parent.parent / "audit_report.json"

SINGLE = re.compile(r"(?<!\{)\{([a-zA-Z0-9_]{2,})\}(?!\})")
DOUBLE = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")

# placeholders that are intentionally filled by the system (not user
# inputs) — they are resolved by the pipeline
SYSTEM_KEYS = {"prepared_by", "reviewed_by", "approved_by", "revision",
               "doc_date", "document_number", "web_notes", "operator",
               "contractor", "well_name", "field_name", "date"}


def extract_placeholders(text: str):
    singles, doubles = set(), set()
    for m in SINGLE.finditer(text or ""):
        singles.add(m.group(1))
    for m in DOUBLE.finditer(text or ""):
        doubles.add(m.group(1))
    return singles, doubles


def audit_template(td) -> dict:
    singles, doubles = extract_placeholders(td.full_markdown)
    all_ph = singles | doubles
    declared = {s.key for s in td.inputs}
    missing = sorted(all_ph - declared - SYSTEM_KEYS)
    unused = sorted(declared - all_ph)
    # syntax consistency: wizard templates should prefer {{x}}; any
    # single-brace is legacy but supported
    legacy = sorted(singles - doubles)
    # render check with synthetic values
    values = {k: "X" for k in all_ph}
    md = fill_template(td, values)
    unresolved = scan_unresolved_placeholders(md)
    issues = []
    if missing:
        issues.append(f"{len(missing)} missing input(s): {', '.join(missing[:6])}")
    if unused:
        issues.append(f"{len(unused)} unused input(s): {', '.join(unused[:6])}")
    if unresolved:
        issues.append(f"unresolved after render: {', '.join(unresolved[:6])}")
    status = "FAIL" if missing or unresolved else (
        "WARN" if unused or legacy else "PASS")
    return {
        "key": td.key, "name": td.name, "kind": td.kind,
        "placeholders": sorted(all_ph), "declared": sorted(declared),
        "missing": missing, "unused": unused,
        "legacy_single_brace": legacy,
        "unresolved_after_render": unresolved,
        "status": status, "issues": issues,
    }


def audit_db_procedure(con, pid, name) -> dict:
    rows = con.execute(
        "SELECT text, precondition, acceptance FROM procedure_steps "
        "WHERE procedure_id=?", (pid,)).fetchall()
    body = "\n".join((r[0] or "") + "\n" + (r[1] or "") + "\n" +
                     (r[2] or "") for r in rows)
    singles, doubles = extract_placeholders(body)
    all_ph = singles | doubles
    ins = con.execute(
        "SELECT input_key, input_label, input_default, is_required "
        "FROM procedure_inputs WHERE procedure_id=?", (pid,)).fetchall()
    declared = {r[0] for r in ins}
    missing = sorted(all_ph - declared - SYSTEM_KEYS)
    unused = sorted(declared - all_ph)
    # render check: fill with synthetic values
    vals = {k: "X" for k in all_ph}
    md = body
    for k in all_ph:
        md = md.replace("{{" + k + "}}", vals[k]).replace("{" + k + "}",
                                                          vals[k])
    unresolved = scan_unresolved_placeholders(md)
    issues = []
    if missing:
        issues.append(f"{len(missing)} missing input(s): "
                      f"{', '.join(missing[:6])}")
    if unused:
        issues.append(f"{len(unused)} unused input(s): "
                      f"{', '.join(unused[:6])}")
    if unresolved:
        issues.append(f"unresolved after render: "
                      f"{', '.join(unresolved[:6])}")
    status = "FAIL" if missing or unresolved else (
        "WARN" if unused else "PASS")
    return {
        "key": f"db:{pid}", "name": name, "kind": "Procedure (DB)",
        "placeholders": sorted(all_ph), "declared": sorted(declared),
        "missing": missing, "unused": unused,
        "legacy_single_brace": sorted(singles - doubles),
        "unresolved_after_render": unresolved,
        "status": status, "issues": issues,
    }


def run_audit() -> dict:
    results = []
    for td in (list(ALL_TEMPLATES) + list(PROCEDURE_TEMPLATES) +
               list(OFFSHORE_TEMPLATES) + build_master_templates()):
        results.append(audit_template(td))
    if DB.exists():
        con = sqlite3.connect(str(DB))
        for r in con.execute("SELECT id, name FROM procedures "
                             "WHERE is_active=1 ORDER BY name"):
            results.append(audit_db_procedure(con, r[0], r[1]))
        con.close()
    stats = {"total": len(results),
             "pass": sum(1 for r in results if r["status"] == "PASS"),
             "warn": sum(1 for r in results if r["status"] == "WARN"),
             "fail": sum(1 for r in results if r["status"] == "FAIL")}
    return {"stats": stats, "results": results}


def write_reports(report: dict):
    from datetime import datetime
    lines = ["# TEMPLATE & PROCEDURE AUDIT REPORT", "",
             f"Generated: {datetime.now().strftime('%d-%B-%Y %H:%M')}", "",
             f"**Total: {report['stats']['total']}** | "
             f"✅ PASS {report['stats']['pass']} | "
             f"⚠️ WARN {report['stats']['warn']} | "
             f"❌ FAIL {report['stats']['fail']}", "",
             "## Per-item status", "",
             "| # | Key | Name | Kind | Status | Issues |",
             "|---|---|---|---|---|---|"]
    for i, r in enumerate(report["results"], 1):
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(r["status"],
                                                             "•")
        lines.append(f"| {i} | {r['key']} | {r['name'][:50]} | "
                     f"{r['kind']} | {icon} {r['status']} | "
                     f"{'; '.join(r['issues'])[:90]} |")
    lines += ["", "## Failed items detail", ""]
    fails = [r for r in report["results"] if r["status"] == "FAIL"]
    if not fails:
        lines.append("_None — every template and procedure renders "
                     "without unresolved placeholders._")
    for r in fails[:30]:
        lines.append(f"### {r['name']} ({r['key']})")
        lines.append("")
        for i in r["issues"]:
            lines.append(f"- {i}")
        if r["missing"]:
            lines.append(f"- Missing inputs: {', '.join(r['missing'])}")
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(report, indent=1, ensure_ascii=False),
                        encoding="utf-8")


def main():
    print("Running template & procedure audit...")
    report = run_audit()
    write_reports(report)
    s = report["stats"]
    print(f"  total: {s['total']} | PASS {s['pass']} | WARN {s['warn']} "
          f"| FAIL {s['fail']}")
    for r in report["results"]:
        if r["status"] == "FAIL":
            print(f"  ❌ {r['key']}: {r['name'][:50]} — "
                  f"{'; '.join(r['issues'])[:100]}")
    print(f"  reports: {OUT_MD.name} + {OUT_JSON.name}")
    return 0 if s["fail"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
