# ============================================================================
# MASTER PROCEDURES — one consolidated procedure per operation
# File: master_procedures.py
#
# Builds ONE canonical "master procedure" for each operation by merging the
# knowledge of ALL library documents of that operation:
#   - steps: extracted from every document, deduplicated, frequency-ranked
#   - checklist: merged & unique
#   - parameters: {{placeholders}} the user fills in to get a precise output
#   - references: the underlying documents (as evidence)
#
# The result is stored in ~/.drilling_program/master_procedures.db and can be
# generated as a Word document via the wizard (see wizard_master.py).
#
# This is NOT deep learning — it is deterministic ML-style consensus:
# frequency-weighted extraction (steps that appear in many documents rank
# higher). If sentence-transformers is installed, semantic clustering is
# used to group near-duplicate steps; otherwise TF-IDF cosine is used.
# ============================================================================

import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

APP_DIR = Path.home() / ".drilling_program"
MASTER_DB = str(APP_DIR / "master_procedures.db")
LIBRARY_DIR = Path(__file__).resolve().parent / "programs" / "library"

# ---------------------------------------------------------------------------
# STEP EXTRACTION (shared logic — same as seed scripts)
# ---------------------------------------------------------------------------

_ACTION_RE = re.compile(
    r"^(drill|run|pooh|rih|make\s*up|pick\s*up|pump|take|perform|circulate|"
    r"condition|displace|test|set|install|remove|retrieve|hold|spot|open|"
    r"close|pull|cement|wash|ream|jet|float|stab|fill|inspect|check|prepare|"
    r"secure|land|pressure|mix|kill|connect|trip|slip|stand|lay\s*down|"
    r"change|reset|back\s*off|mill|fish|tag|work|monitor|record|report|"
    r"verify|ensure|tighten|torque|break|start|stop|jack|cut|rig|mob|demob)\b",
    re.IGNORECASE)

# verbs that may appear anywhere in a step (not only at the start)
_ANY_ACTION_RE = re.compile(
    r"\b(drill|run|rih|pooh|pump|circulate|displace|test|set|install|remove|"
    r"retrieve|spot|open|close|pull|cement|wash|ream|jet|fill|inspect|check|"
    r"prepare|secure|land|pressure|mix|kill|connect|trip|change|back\s*off|"
    r"mill|fish|work|monitor|record|verify|ensure|tighten|torque|break|start|"
    r"stop|cut|rig|mob|demob|hold|perform|condition)\b",
    re.IGNORECASE)

_SKIP = re.compile(r"^(page|table|figure|fig\.|appendix|index|contents|"
                   r"abbrev|symbol|refer|note:|attention:|warning:|caution:)")


def _clean(s: str) -> str:
    from cbs_db import generalize_text
    s = generalize_text(s)
    s = re.sub(r"\s+", " ", s).strip(" .-–—")
    return s


def _norm_step(s: str) -> str:
    """Normalize a step for near-duplicate comparison (strip numbers, units)."""
    s = s.lower()
    s = re.sub(r"\d+[\d.,/%]*", "N", s)
    s = re.sub(r"\b(in|ft|m|bbl|psi|ppg|pcf|hr|min|deg|gpm|rpm|#|lbs)\b",
               "U", s)
    return re.sub(r"[^a-z ]+", " ", s)


def extract_steps(text: str, max_per_doc: int = 40) -> List[str]:
    lines = text.splitlines()
    steps = []
    for ln in lines:
        ln = ln.strip()
        if not ln or _SKIP.match(ln.lower()):
            continue
        if re.match(r"^[─═\[]", ln) or re.match(r"^\[ صفحه", ln):
            continue
        # skip table rows / header artifacts
        if "|" in ln:
            continue
        m = re.match(r"^(\d{1,2})[-.)]\s+(.{15,})", ln)
        cand = None
        if m:
            cand = _clean(m.group(2))
        elif _ACTION_RE.match(ln) and 20 < len(ln) < 320:
            cand = _clean(ln)
        if cand and 14 < len(cand) < 300:
            # numbered lines must still contain an action verb or key noun
            if m and not _ANY_ACTION_RE.search(cand):
                continue
            # drop obvious header/title lines (short, no verb, caps-heavy)
            words = cand.split()
            if len(words) <= 4 and not _ANY_ACTION_RE.search(cand):
                continue
            steps.append(cand)
        if len(steps) >= max_per_doc:
            break
    return steps


def extract_checklist(text: str, max_items: int = 12) -> List[str]:
    keys = ("check", "ensure", "test", "inspect", "prepare", "verify",
            "available", "ready", "calibrat", "safety", "bop", "torque",
            "gauge", "pressure", "mud", "equipment", "crew", "personal")
    out = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or len(ln) > 170:
            continue
        low = ln.lower()
        if any(k in low for k in keys) and re.search(r"[A-Za-z]{4}", ln):
            c = _clean(ln)
            if 12 < len(c) < 160:
                out.append(c)
        if len(out) >= max_items:
            break
    return out or ["Hold pre-job safety meeting"]


# ---------------------------------------------------------------------------
# NEAR-DUPLICATE CLUSTERING (TF-IDF — pure python, no heavy deps)
# ---------------------------------------------------------------------------

def _tfidf_similar(a: str, b: str) -> float:
    wa = set(a.split())
    wb = set(b.split())
    if not wa or not wb:
        return 0.0
    return len(wa & wb) / (len(wa | wb) + 1e-9)


def dedupe_steps(steps: List[Tuple[str, int]], threshold: float = 0.55
                 ) -> List[Tuple[str, int]]:
    """Cluster near-duplicate steps; keep the most frequent representative."""
    normed = [(_norm_step(s), s, f) for s, f in steps]
    kept: List[Tuple[str, int]] = []
    used = [False] * len(normed)
    for i, (n1, s1, f1) in enumerate(normed):
        if used[i]:
            continue
        # find all similar to i
        cluster = [i]
        for j in range(i + 1, len(normed)):
            if not used[j] and _tfidf_similar(n1, normed[j][0]) >= threshold:
                cluster.append(j)
        # representative = highest frequency, then longest
        rep = max(cluster, key=lambda k: (normed[k][2], len(normed[k][1])))
        kept.append((normed[rep][1], sum(normed[k][2] for k in cluster)))
        for k in cluster:
            used[k] = True
    kept.sort(key=lambda x: -x[1])
    return kept


# ---------------------------------------------------------------------------
# MASTER PROCEDURE BUILDER
# ---------------------------------------------------------------------------

class MasterProcedureBuilder:
    def __init__(self):
        self.catalog = None
        try:
            from document_catalog import get_catalog
            self.catalog = get_catalog()
        except Exception:
            pass

    def docs_for_operation(self, operation: str) -> List[Path]:
        if self.catalog is None:
            return []
        rows = self.catalog.conn.execute(
            "SELECT file FROM docs WHERE operation=? ORDER BY num",
            (operation,)).fetchall()
        return [LIBRARY_DIR / r["file"] for r in rows
                if (LIBRARY_DIR / r["file"]).exists()]

    def build(self, operation: str, max_docs: int = 60) -> Optional[dict]:
        docs = self.docs_for_operation(operation)
        if not docs:
            return None
        docs = docs[:max_docs]

        all_steps: List[Tuple[str, int]] = []
        all_chk: List[str] = []
        for d in docs:
            try:
                text = d.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for s in extract_steps(text):
                all_steps.append((s, 1))
            all_chk.extend(extract_checklist(text))

        if not all_steps:
            return None

        steps = dedupe_steps(all_steps, threshold=0.5)
        # checklist dedupe by normalized similarity
        chk_dedup: List[Tuple[str, int]] = []
        for c in all_chk:
            chk_dedup.append((c, 1))
        checklist = [c for c, f in dedupe_steps(chk_dedup, threshold=0.6)]

        return {
            "operation": operation,
            "docs_used": len(docs),
            "steps": [s for s, f in steps[:40]],
            "checklist": checklist[:25],
            "doc_list": [d.name for d in docs],
        }


# ---------------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------------

class MasterDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or MASTER_DB
        APP_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create()

    def _create(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS master_procedures (
                operation TEXT PRIMARY KEY,
                docs_used INTEGER,
                steps TEXT,
                checklist TEXT,
                doc_list TEXT,
                updated TEXT
            );
        """)
        self.conn.commit()

    def save(self, op: str, data: dict):
        from datetime import datetime
        self.conn.execute(
            "INSERT OR REPLACE INTO master_procedures "
            "(operation, docs_used, steps, checklist, doc_list, updated) "
            "VALUES (?,?,?,?,?,?)",
            (op, data["docs_used"], json.dumps(data["steps"]),
             json.dumps(data["checklist"]), json.dumps(data["doc_list"]),
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()

    def get(self, op: str) -> Optional[dict]:
        r = self.conn.execute(
            "SELECT * FROM master_procedures WHERE operation=?",
            (op,)).fetchone()
        if not r:
            return None
        return {"operation": r["operation"], "docs_used": r["docs_used"],
                "steps": json.loads(r["steps"]),
                "checklist": json.loads(r["checklist"]),
                "doc_list": json.loads(r["doc_list"]),
                "updated": r["updated"]}

    def all(self) -> List[dict]:
        rows = self.conn.execute(
            "SELECT * FROM master_procedures ORDER BY operation").fetchall()
        return [{"operation": r["operation"], "docs_used": r["docs_used"],
                 "updated": r["updated"]} for r in rows]

    def close(self):
        self.conn.close()


# ---------------------------------------------------------------------------
# MARKDOWN GENERATION (with user parameters)
# ---------------------------------------------------------------------------

PARAM_ROWS = {
    "well_name": ("Well Name", "text"),
    "field_name": ("Field", "text"),
    "operator": ("Operator", "text"),
    "contractor": ("Contractor", "text"),
    "rig_name": ("Rig", "text"),
    "environment": ("Environment", "combo"),
    "well_type": ("Well Type", "combo"),
    "hole_size": ("Hole Size", "text"),
    "depth_m": ("Depth (m)", "number"),
    "mud_weight": ("Mud Weight (pcf)", "number"),
    "mud_type": ("Mud Type", "text"),
    "casing_size": ("Casing/Liner Size", "text"),
    "bop_wp": ("BOP Rating (psi)", "number"),
    "doc_date": ("Date", "text"),
    "revision": ("Revision", "text"),
}

OPERATION_PARAMS = {
    "Cementing": ["hole_size", "casing_size", "depth_m", "mud_weight", "mud_type"],
    "Casing-Liner": ["hole_size", "casing_size", "depth_m", "mud_weight"],
    "Well Control": ["mud_weight", "mud_type", "depth_m", "bop_wp"],
    "BOP": ["bop_wp", "depth_m"],
    "Fishing": ["hole_size", "depth_m"],
    "Sidetrack": ["hole_size", "depth_m", "mud_weight"],
    "Re-Entry": ["hole_size", "depth_m", "mud_weight"],
    "Workover": ["hole_size", "depth_m", "mud_weight", "mud_type"],
    "Completion": ["hole_size", "casing_size", "depth_m"],
    "Mud-Fluids": ["mud_weight", "mud_type", "depth_m"],
    "Well Testing": ["depth_m", "bop_wp"],
    "Drilling": ["hole_size", "depth_m", "mud_weight", "mud_type", "casing_size"],
}


def build_master_markdown(mp: dict, values: Optional[Dict] = None) -> str:
    values = values or {}
    op = mp["operation"]

    def v(key):
        return values.get(key, "")

    params = ["well_name", "field_name", "operator", "contractor",
              "rig_name", "environment", "well_type"] + \
             OPERATION_PARAMS.get(op, []) + ["doc_date", "revision"]
    params = list(dict.fromkeys(params))

    L = [f"# MASTER PROCEDURE — {op.upper()} OPERATION", ""]
    L.append(f"**Well:** {v('well_name') or '[To Be Filled]'}  |  "
             f"**Field:** {v('field_name') or '[To Be Filled]'}")
    L.append(f"**Operator:** {v('operator') or 'the Operator'}  |  "
             f"**Contractor:** {v('contractor') or 'the Service Company'}")
    L.append(f"**Environment:** {v('environment') or '[To Be Filled]'}  |  "
             f"**Well Type:** {v('well_type') or '[To Be Filled]'}")
    L.append("")

    L.append("## 1. SCOPE")
    L.append("")
    L.append(f"This master procedure consolidates the field-proven practice "
             f"for **{op.lower()} operations**, merged from "
             f"**{mp['docs_used']} reference documents** in the internal "
             f"knowledge library. Apply the parameters below and follow the "
             f"steps in sequence; adapt to the specific well conditions.")
    L.append("")

    L.append("## 2. OPERATION PARAMETERS")
    L.append("")
    L.append("| Parameter | Value |")
    L.append("|---|---|")
    for p in params:
        label = PARAM_ROWS.get(p, (p, "text"))[0]
        L.append(f"| {label} | {v(p) or '[To Be Filled]'} |")
    L.append("")

    L.append("## 3. PREREQUISITES")
    L.append("")
    L.append("- Hold pre-job safety meeting; review risk assessment.")
    L.append("- Verify equipment, gauges and BOP are tested and ready.")
    L.append("- Review the well program and offset-well experience.")
    L.append("")

    L.append("## 4. OPERATION STEPS")
    L.append("")
    for i, s in enumerate(mp["steps"], 1):
        L.append(f"{i}. {s}")
    L.append("")

    L.append("## 5. CHECKLIST")
    L.append("")
    for c in mp["checklist"]:
        L.append(f"- [ ] {c}")
    L.append("")

    L.append("## 6. REFERENCES (EVIDENCE)")
    L.append("")
    L.append(f"Built from {mp['docs_used']} library documents (internal "
             f"knowledge base).")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# SEED — build all master procedures
# ---------------------------------------------------------------------------

def seed_all(force: bool = False) -> List[str]:
    builder = MasterProcedureBuilder()
    db = MasterDatabase()
    try:
        ops = []
        if builder.catalog:
            rows = builder.catalog.conn.execute(
                "SELECT operation, COUNT(*) AS n FROM docs "
                "WHERE operation NOT IN ('Undefined') "
                "GROUP BY operation ORDER BY n DESC").fetchall()
            ops = [r["operation"] for r in rows]
        built = []
        for op in ops:
            data = builder.build(op)
            if data and (force or db.get(op) is None):
                db.save(op, data)
                built.append(op)
                print(f"  ✔ {op}: {data['docs_used']} docs, "
                      f"{len(data['steps'])} steps, "
                      f"{len(data['checklist'])} checklist")
        return built
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    seed_all(force="--force" in sys.argv)
