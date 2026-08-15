# ============================================================================
# SEED OFFSHORE PROCEDURES — from the 25 new offshore documents
# File: seed_offshore_procedures.py
# Extracts general steps & checklists from the offshore re-entry / workover /
# drilling programs (library files 217-241) into the procedures database.
# Everything is generalized (no well/company/reservoir names).
# ============================================================================

import re
import sys
from pathlib import Path

from cbs_db import generalize_text
from procedures_db import ProcedureDatabase

LIB = Path(__file__).parent / "programs" / "library"


def _clean(t: str) -> str:
    t = generalize_text(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def _get_or_create_category(db, name):
    # try to find by name; fall back to first category
    try:
        for c in db.get_all_categories():
            if c.name == name:
                return c.id
    except Exception:
        pass
    try:
        row = db.conn.execute("SELECT id FROM categories ORDER BY id LIMIT 1").fetchone()
        if row:
            return row["id"]
    except Exception:
        pass
    return 1


def seed(force: bool = False):
    db = ProcedureDatabase()
    try:
        # check if already seeded
        existing = db.conn.execute(
            "SELECT COUNT(*) AS c FROM procedures WHERE proc_key LIKE 'offshore_%'"
        ).fetchone()["c"]
        if existing and not force:
            print(f"✔ Offshore procedures already seeded ({existing}) — "
                  f"use --force to re-seed.")
            return

        cat_reentry = _get_or_create_category(db, "Re-Entry / Sidetrack")
        cat_workover = _get_or_create_category(db, "Workover / Completion")
        cat_drilling = _get_or_create_category(db, "Drilling")

        # ----------------------------------------------------------------
        # 1. RE-ENTRY / SIDETRACK (from 217, 219, 231, 232, 236-238)
        # ----------------------------------------------------------------
        reentry_steps = [
            "Record wellhead and tubing annulus pressures; hook up kill lines and pressure-test.",
            "Kill and secure the well (brine/kill fluid as per program).",
            "N/D X-mas tree, N/U BOP stack and pressure-test same.",
            "RIH with bit and directional BHA (MWD/GR/ROP) to top of cement / window.",
            "Perform time drilling / sidetrack from window depth (kick-off).",
            "Drill directional section to section TD; take surveys per plan.",
            "Perform condition trip; take full set of logs (TLC) in open hole as required.",
            "Set balanced plug (e.g. magneset) if required and WOC.",
            "RIH with 6\" BHA, drill out plug and shoe, dress to liner lap.",
            "Run liner, set liner hanger, cement liner, perform lap test.",
            "POOH, change rams, perform BOP test.",
            "RIH with completion string (scraper run first), set packer.",
            "Secure well, N/D BOP, N/U X-mas tree, pressure-test p-seals.",
            "Perform stimulation / clean-up, secure well and release rig.",
        ]
        reentry_checklist = [
            "BHA & bits (roller/PDC) sized for window & hole section",
            "Directional tools: MWD/GR/ROP, motor, survey equipment",
            "Whipstock & window milling assembly (if sidetrack)",
            "Liner with hanger, float shoe/collar, centralizers",
            "Fishing tools & spare parts (overshot, jars, mills)",
            "LCM, weighting material, pipe-free agent",
            "Scraper (tandem if required) & wellhead tools",
            "H2S safety equipment & services (if H2S present)",
            "Kill fluid / brine of required density",
            "BOP test records & choke manifold readiness",
        ]

        # ----------------------------------------------------------------
        # 2. WORKOVER / ESP CHANGE (from 225-227, 233-235, 241)
        # ----------------------------------------------------------------
        workover_steps = [
            "Move/skid rig on location; record wellhead & annulus pressures.",
            "Hook up kill lines on THS & X-mas tree; pressure-test.",
            "Kill and secure well by brine of required density.",
            "N/D X-mas tree, N/U BOP stack and test same.",
            "Retrieve BPV; RIH with R&R tools, latch into hanger, unset packer.",
            "Circulate across wellhead, POOH completion string; lay down ESP.",
            "RIH with bit & casing scraper; clean well to top of perforation.",
            "Pump Hi-Vis pill and CBU to clean the hole.",
            "Run new ESP completion string per completion engineer instructions.",
            "Set packer, install TRSV, pressure-test completion string.",
            "N/D BOP, N/U X-mas tree, test p-seals.",
            "Secure well, release rig.",
        ]
        workover_checklist = [
            "ESP string: pump, motor, seal, cable, penetrator",
            "Completion accessories: packer, TRSV, SSD, nipples, plugs",
            "Scraper (tandem 9-5/8\" x 7\" if required)",
            "Brine / kill fluid (density per program)",
            "Slickline unit & tools (BPV, plugs)",
            "Pump truck for setting packer & pressure-testing",
            "Wellhead specialist & services",
            "Fishing tool set for tubing size",
            "H2S equipment (if H2S in reservoir)",
            "Crane / handling equipment for ESP & completion",
        ]

        # ----------------------------------------------------------------
        # 3. OFFSHORE DRILLING (from 218, 220-224, 228-230)
        # ----------------------------------------------------------------
        drilling_steps = [
            "Move rig to location; set RKB-MSL reference.",
            "Drill 36\" hole, run 30\" conductor; cement.",
            "Drill 26\" hole to surface casing point; run 20\" casing; cement.",
            "N/U BOP stack and test as per policy.",
            "Drill 17-1/2\" hole to intermediate casing point; run 13-3/8\" casing; cement.",
            "Drill 12-1/4\" hole to production casing point; run 9-5/8\" casing; cement.",
            "Drill 8-1/2\" hole to TD; take surveys as per plan.",
            "Run logs (full suite + MDT if required).",
            "Run 7\" liner, set liner hanger, cement; perform liner lap test.",
            "Displace to completion fluid; perforate as per program.",
            "Run completion string; set packer; N/U X-mas tree.",
            "Secure well and release rig.",
        ]
        drilling_checklist = [
            "Bits & BHA for each hole section (with spares)",
            "Mud system & materials (WBM/OBM per section)",
            "Casing & liner with accessories (float, centralizers)",
            "Cementing services & additives",
            "Directional tools: MWD/LWD, motor/RSS, surveys",
            "BOP stack, choke manifold, accumulators",
            "Wellhead & casing hangers",
            "Hydraulics: nozzles, TFA, pump pressure plan per section",
            "Fishing tools & contingency equipment",
            "H2S & safety equipment; HSE plan",
        ]

        def add(name, cat, steps, checklist, desc, tags):
            pid = db.add_procedure(name, cat, description=desc,
                                   has_checklist=True, inputs_json="[]",
                                   tags=tags)
            for s in steps:
                db.add_step(pid, _clean(s))
            for c in checklist:
                db.add_checklist_item(pid, _clean(c))
            print(f"  ✔ {name} ({len(steps)} steps, {len(checklist)} checklist)")

        print("Seeding offshore procedures...")
        add("Offshore Re-Entry & Sidetrack Program", cat_reentry,
            reentry_steps, reentry_checklist,
            "Re-entry / sidetrack sequence: kill, window, directional drilling, "
            "liner, completion — generalized from offshore programs.",
            "offshore,re-entry,sidetrack,whipstock")
        add("Offshore Workover — ESP Change", cat_workover,
            workover_steps, workover_checklist,
            "Workover to change ESP: kill & secure, POOH completion, clean out, "
            "run new ESP completion — generalized.",
            "offshore,workover,esp,completion")
        add("Offshore Drilling Program", cat_drilling,
            drilling_steps, drilling_checklist,
            "Offshore drilling sequence: conductor to completion — generalized "
            "from offshore drilling programs.",
            "offshore,drilling,program")
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
