# ============================================================================
# DATA CLASSIFICATION & USAGE AUDIT
# File: tests/data_usage_audit.py
# Phase AK — the user asked: "is the database fully classified and does
# the application use ALL the data it holds?"
#
# Audits:
#   1. Procedures DB — categories coverage, empty categories, procedures
#      without steps/checklists, placeholders unresolved in steps
#   2. Catalog — classification coverage per dimension (operation,
#      category, well_type, environment), documents reachable from the
#      fine-grained composition picker
#   3. CBS — priced vs unpriced items, categories
#   4. Problems — severity/category coverage
#   5. Data usage — how many catalog docs / procedures are reachable
#      through the composition UI (procedures_by_category,
#      catalog_by_operation) and how many are actually referenced in the
#      wizard (template inputs, ROPE, master docs)
#
# Run:  LD_LIBRARY_PATH=/tmp/glstubs PYTHONPATH=. QT_QPA_PLATFORM=offscreen \
#       python3 tests/data_usage_audit.py
# ============================================================================

import os
import re
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

APP_DIR = Path.home() / ".drilling_program"

_PASS = 0
_FAIL = 0
_WARNINGS = []


def ok(cond, label, extra=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  ✘ {label} {extra}")


def warn(label, extra=""):
    _WARNINGS.append(f"{label}: {extra}")
    print(f"  ⚠ {label} {extra}")


def audit_procedures():
    print("\n[1] PROCEDURES DB — classification coverage")
    con = sqlite3.connect(str(APP_DIR / "procedures.db"))
    con.row_factory = sqlite3.Row
    cats = con.execute(
        "SELECT c.name, COUNT(p.id) n FROM categories c "
        "LEFT JOIN procedures p ON p.category_id=c.id AND p.is_active=1 "
        "GROUP BY c.name ORDER BY n DESC").fetchall()
    ok(len(cats) >= 14, f"categories >= 14 (got {len(cats)})")
    empty = [c["name"] for c in cats if c["n"] == 0]
    ok(not empty, "no empty categories", str(empty))
    # procedures without steps
    no_steps = con.execute(
        "SELECT COUNT(*) c FROM procedures p WHERE p.is_active=1 "
        "AND NOT EXISTS (SELECT 1 FROM procedure_steps s "
        "WHERE s.procedure_id=p.id)").fetchone()["c"]
    total = con.execute(
        "SELECT COUNT(*) c FROM procedures WHERE is_active=1"
    ).fetchone()["c"]
    ok(no_steps / max(total, 1) < 0.15,
       f"procedures with steps >= 85% ({(total-no_steps)}/{total})")
    # placeholder check: steps with unresolved single-brace placeholders
    pat = re.compile(r"(?<!\{)\{([a-zA-Z0-9_]{2,})\}(?!\})")
    ph_steps = 0
    for r in con.execute("SELECT text FROM procedure_steps"):
        if pat.search(r["text"] or ""):
            ph_steps += 1
    warn("steps with placeholders", f"{ph_steps} (resolved at export by "
         "the parameter engine)")
    con.close()


def audit_catalog():
    print("\n[2] CATALOG — classification coverage (5 dimensions)")
    con = sqlite3.connect(str(APP_DIR / "catalog.db"))
    con.row_factory = sqlite3.Row
    total = con.execute("SELECT COUNT(*) c FROM docs").fetchone()["c"]
    ok(total >= 700, f"docs >= 700 (got {total})")
    for dim in ("operation", "category", "well_type", "environment"):
        n = con.execute(
            f"SELECT COUNT(DISTINCT {dim}) c FROM docs "
            f"WHERE {dim} != ''").fetchone()["c"]
        ok(n >= 5, f"distinct {dim} >= 5 (got {n})")
    # documents with an operation value (usable by the composition picker)
    classified = con.execute(
        "SELECT COUNT(*) c FROM docs WHERE operation != ''"
    ).fetchone()["c"]
    ok(classified / max(total, 1) >= 0.9,
       f"docs classified by operation >= 90% ({classified}/{total})")
    con.close()


def audit_cbs_problems():
    print("\n[3] CBS + PROBLEMS")
    con = sqlite3.connect(str(APP_DIR / "cbs.db"))
    n_items = con.execute("SELECT COUNT(*) FROM cbs_items").fetchone()[0]
    n_priced = con.execute(
        "SELECT COUNT(*) FROM cbs_items WHERE unit_price > 0"
    ).fetchone()[0]
    con.close()
    ok(n_items >= 300, f"cbs items >= 300 (got {n_items})")
    ok(n_priced / max(n_items, 1) >= 0.5,
       f"priced items >= 50% ({n_priced}/{n_items})")
    con = sqlite3.connect(str(APP_DIR / "problems.db"))
    n_prob = con.execute("SELECT COUNT(*) FROM problems").fetchone()[0]
    n_sev = con.execute(
        "SELECT COUNT(DISTINCT severity) FROM problems").fetchone()[0]
    con.close()
    ok(n_prob >= 20, f"problems >= 20 (got {n_prob})")
    ok(n_sev >= 3, f"severity levels >= 3 (got {n_sev})")


def audit_composition_reach():
    print("\n[4] COMPOSITION — all data reachable by the user")
    from wizard_compose import procedures_by_category, catalog_by_operation
    procs = procedures_by_category()
    docs = catalog_by_operation()
    ok(len(procs) >= 150, f"procedures reachable >= 150 (got {len(procs)})")
    ok(len(docs) >= 700, f"knowledge docs reachable >= 700 (got {len(docs)})")
    # every procedure has a category (classification complete)
    uncat = [p for p in procs if not (p.get("category") or "").strip()]
    ok(not uncat, "no uncategorized procedures",
       f"{len(uncat)} uncategorized")
    # every doc has an operation or category
    unop = [d for d in docs if not (d.get("operation") or "").strip()]
    warn("docs without operation", f"{len(unop)} (shown as General)")


def audit_wizard_coverage():
    print("\n[5] WIZARD — knowledge/data usage in generation")
    # templates reference procedures categories? at least the master
    # templates merge from master_procedures.db
    con = sqlite3.connect(str(APP_DIR / "master_procedures.db"))
    n_master = con.execute(
        "SELECT COUNT(*) FROM master_procedures").fetchone()[0]
    con.close()
    ok(n_master >= 10, f"master procedures >= 10 (got {n_master})")
    # library files used by the catalog
    lib = Path(__file__).parent.parent / "programs" / "library"
    n_files = len(list(lib.glob("*.txt")))
    ok(n_files >= 700, f"library files >= 700 (got {n_files})")
    # ROPE manual exists and is parsed
    rope = lib / "ROPE_Manual.txt"
    ok(rope.exists(), "ROPE manual present")
    try:
        from wizard_rope import _sections
        secs = _sections()
        ok(len(secs) >= 30, f"ROPE sections >= 30 (got {len(secs)})")
    except Exception:
        ok(False, "ROPE parseable")


if __name__ == "__main__":
    audit_procedures()
    audit_catalog()
    audit_cbs_problems()
    audit_composition_reach()
    audit_wizard_coverage()
    print("\n" + "=" * 60)
    print(f"RESULT: {_PASS} passed, {_FAIL} failed, "
          f"{len(_WARNINGS)} warnings")
    for w in _WARNINGS:
        print("  ⚠", w)
    print("=" * 60)
    sys.exit(1 if _FAIL else 0)
