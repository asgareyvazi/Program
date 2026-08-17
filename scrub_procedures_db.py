# ============================================================================
# SCRUB PROCEDURES DATABASE — remove company/well/reservoir names everywhere
# File: scrub_procedures_db.py
# Runs neutralize_text (full blacklist: operators, service companies,
# well codes, reservoirs/formations) over ALL procedures, steps and
# checklist items so the procedures database stays 100% general.
# Run after any seeding.
# ============================================================================

import re
import sys

from wizard_engine import neutralize_text
from procedures_db import ProcedureDatabase


def scrub(db: ProcedureDatabase) -> dict:
    stats = {"procedures": 0, "steps": 0, "checklist": 0}

    # 1) procedures (name, description, tags)
    rows = db.conn.execute(
        "SELECT id, name, description, tags FROM procedures").fetchall()
    for r in rows:
        n_name = neutralize_text(r["name"])
        n_desc = neutralize_text(r["description"] or "")
        n_tags = neutralize_text(r["tags"] or "")
        if (n_name, n_desc, n_tags) != (r["name"], r["description"], r["tags"]):
            db.conn.execute(
                "UPDATE procedures SET name=?, description=?, tags=? WHERE id=?",
                (n_name, n_desc, n_tags, r["id"]))
            stats["procedures"] += 1

    # 2) steps — text plus the structured fields (Batch J/K columns)
    rows = db.conn.execute(
        "SELECT id, text, precondition, acceptance FROM "
        "procedure_steps").fetchall()
    for r in rows:
        nt = neutralize_text(r["text"])
        np_ = neutralize_text(r["precondition"] or "")
        na = neutralize_text(r["acceptance"] or "")
        if (nt, np_, na) != (r["text"], r["precondition"], r["acceptance"]):
            db.conn.execute(
                "UPDATE procedure_steps SET text=?, precondition=?, "
                "acceptance=? WHERE id=?",
                (nt, np_, na, r["id"]))
            stats["steps"] += 1

    # 3) checklist items
    rows = db.conn.execute(
        "SELECT id, text, category FROM checklist_items").fetchall()
    for r in rows:
        nt = neutralize_text(r["text"])
        nc = neutralize_text(r["category"] or "")
        if (nt, nc) != (r["text"], r["category"]):
            db.conn.execute(
                "UPDATE checklist_items SET text=?, category=? WHERE id=?",
                (nt, nc, r["id"]))
            stats["checklist"] += 1

    db.conn.commit()
    return stats


if __name__ == "__main__":
    db = ProcedureDatabase()
    try:
        stats = scrub(db)
        print("scrubbed:", stats)
        total = db.conn.execute("SELECT COUNT(*) AS c FROM procedures").fetchone()["c"]
        print(f"procedures total: {total}")
    finally:
        db.close()
