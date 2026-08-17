# ============================================================================
# SEED BP PROCEDURES — BP UK Operations Guidelines (127 documents)
# File: seed_bp_procedures.py
# Extracts procedures from the 127 BP drilling guidelines (library files
# 563-689) into the procedures database. Steps come from the guideline
# bodies (numbered/action lines), generalized. Master-index files are
# skipped.
# ============================================================================

import re
import sys
from pathlib import Path

from cbs_db import generalize_text
from procedures_db import ProcedureDatabase

LIB = Path(__file__).resolve().parent / "programs" / "library"

# BP category mapping by code prefix
BP_CATEGORY = [
    ("04", "Well Control"),
    ("10", "Drilling Operations"),
    ("11", "Drilling Operations"),
    ("12", "Drilling Operations"),
    ("13", "Drilling Operations"),
    ("14", "Drilling Operations"),
    ("20", "Casing & Liner"),
    ("21", "Casing & Liner"),
    ("22", "Casing & Liner"),
    ("23", "Casing & Liner"),
    ("25", "Casing & Liner"),
    ("30", "Cementing"),
    ("31", "Cementing"),
    ("32", "Cementing"),
    ("33", "Cementing"),
    ("34", "Cementing"),
    ("35", "Cementing"),
    ("40", "Drilling Fluids"),
    ("41", "Drilling Fluids"),
    ("42", "Drilling Fluids"),
    ("43", "Drilling Fluids"),
    ("44", "Drilling Fluids"),
    ("45", "Drilling Fluids"),
    ("46", "Drilling Fluids"),
    ("49", "Drilling Fluids"),
    ("50", "Special Operations"),
    ("52", "Special Operations"),
    ("54", "Special Operations"),
    ("55", "Special Operations"),
    ("60", "Fishing & Remedial"),
    ("61", "Fishing & Remedial"),
    ("62", "Fishing & Remedial"),
    ("64", "Fishing & Remedial"),
    ("65", "Fishing & Remedial"),
    ("70", "Formation Evaluation"),
    ("71", "Formation Evaluation"),
    ("72", "Formation Evaluation"),
    ("73", "Formation Evaluation"),
    ("74", "Formation Evaluation"),
    ("81", "Special Operations"),
    ("82", "Special Operations"),
    ("83", "Special Operations"),
]


def bp_category(code: str) -> str:
    for prefix, cat in BP_CATEGORY:
        if code.startswith(prefix):
            return cat
    return "Special Operations"


def _clean(t: str) -> str:
    t = generalize_text(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip(" .-–—")


def _extract_steps(text: str, max_steps: int = 16) -> list:
    lines = text.splitlines()
    steps = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if re.match(r"^[─═\[]", ln) or re.match(r"^\[ صفحه", ln):
            continue
        m = re.match(r"^(\d{1,2})[-.)]\s+(.{15,})", ln)
        if m:
            step = _clean(m.group(2))
            if 15 < len(step) < 300:
                steps.append(step)
            continue
        if re.match(
            r"^(drill|run|pooh|rih|make\s*up|pick\s*up|pump|take|perform|"
            r"circulate|condition|displace|test|set|install|remove|retrieve|"
            r"hold|spot|open|close|pull|cement|wash|ream|jet|float|stab|"
            r"fill|inspect|check|prepare|secure|land|pressure|mix|kill|"
            r"connect|trip|slip|stand|lay\s*down|change|reset|back\s*off|"
            r"mill|fish|tag|work|monitor|record|report|verify|ensure|"
            r"tighten|torque|break|start|stop|jack|cut)\b",
            ln, re.IGNORECASE) and 20 < len(ln) < 340:
            step = _clean(ln)
            if step:
                steps.append(step)
    seen, out = set(), []
    for s in steps:
        k = s[:60].lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
        if len(out) >= max_steps:
            break
    return out


def _extract_checklist(text: str, max_items: int = 8) -> list:
    keys = ["check", "ensure", "test", "inspect", "prepare", "verify",
            "available", "ready", "calibrat", "safety", "bop", "torque",
            "gauge", "pit", "mud", "pressure"]
    out = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or len(ln) > 170:
            continue
        low = ln.lower()
        if any(k in low for k in keys) and re.search(r"[A-Za-z]{4}", ln):
            c = _clean(ln)
            if 15 < len(c) < 160:
                out.append(c)
        if len(out) >= max_items:
            break
    return out or ["Review the guideline and hold a pre-job safety meeting"]


def seed(force: bool = False):
    db = ProcedureDatabase()
    try:
        existing = db.conn.execute(
            "SELECT COUNT(*) AS c FROM procedures WHERE proc_key LIKE 'bp_%'"
        ).fetchone()["c"]
        if existing and not force:
            print(f"✔ BP procedures already seeded ({existing}) — "
                  f"use --force to re-seed.")
            return
        if force and existing:
            db.conn.execute(
                "DELETE FROM procedures WHERE proc_key LIKE 'bp_%'")
            db.conn.commit()

        def cat_id(name):
            for c in db.get_all_categories():
                if c.name == name:
                    return c.id
            return db.add_category(name, icon="📋", sort_order=99)

        # find BP docs: 563+ with code pattern (NNNN-xxx)
        bp_files = []
        for f in LIB.glob("*.txt"):
            m = re.match(r"^(\d{3})_(\d{4}[a-z]?)", f.name)
            if m and int(m.group(1)) >= 563:
                bp_files.append(f)
        print(f"BP library files: {len(bp_files)}")

        added = skipped = 0
        for f in sorted(bp_files):
            txt = f.read_text(encoding="utf-8", errors="replace")
            # title from filename after code: NNN_CODE_TITLE
            parts = f.name.split("_", 2)
            code = re.sub(r"\.(pdf|docx|doc)$", "", parts[1], flags=re.I)
            code = re.sub(r"^\d{3}_", "", code)
            title = parts[2].rsplit(".", 1)[0].replace("_", " ") if len(parts) > 2 else code
            title = generalize_text(title).strip()
            if "MASTER INDEX" in title.upper() or not re.search(r"[A-Za-z]{4}", title):
                skipped += 1
                continue
            steps = _extract_steps(txt)
            if len(steps) < 4:
                skipped += 1
                continue
            checklist = _extract_checklist(txt)
            cat = bp_category(code[:2])
            cid = cat_id(cat)
            name = f"Guideline {code} — {title.title()}"
            pid = db.add_procedure(name, cid,
                                   description=("Extracted from the international drilling "
                                                "guidelines library (generalized)."),
                                   has_checklist=True, inputs_json="[]",
                                   tags=f"bp,{cat.lower()}")
            db.conn.execute("UPDATE procedures SET proc_key=? WHERE id=?",
                            (f"bp_{code}", pid))
            for s in steps:
                db.add_step(pid, s)
            for c in checklist:
                db.add_checklist_item(pid, c)
            added += 1
        db.conn.commit()
        print(f"added: {added} | skipped (index/too-short): {skipped}")
    finally:
        db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
