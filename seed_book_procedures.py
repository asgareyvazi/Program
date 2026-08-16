# ============================================================================
# SEED REFERENCE-BOOK PROCEDURES — from major-operator manuals (690-702)
# File: seed_book_procedures.py
# Extracts high-quality procedures from the 13 reference books added to the
# library (ADCO, Saudi Aramco, Nimir, Halliburton, PETROM, ExxonMobil,
# HPHT Aberdeen, IADC Drilling Manual, IADC Well Control, Devereux,
# Stuck Pipe Prevention). Everything is generalized.
# ============================================================================

import re
import sys
from pathlib import Path

from cbs_db import generalize_text
from procedures_db import ProcedureDatabase

LIB = Path(__file__).resolve().parent / "programs" / "library"


def _clean(t: str) -> str:
    t = generalize_text(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip(" .-–—")


# ---------------------------------------------------------------------------
# Curated procedures with steps extracted from the actual books
# ---------------------------------------------------------------------------

BOOK_PROCEDURES = [
    # --- from 702 Stuck Pipe Prevention (Well Control School) ---
    ("book_stuck_pipe_prevention",
     "Stuck Pipe Prevention — Program & Practices",
     "Fishing & Remedial",
     "702",
     "Stuck pipe prevention: causes (differential, formation-related, "
     "mechanical), warning signs, prevention program, freeing methods.",
     ["Differential sticking: caused by overbalance + thick filter cake "
      "across permeable formations",
      "Formation-related sticking: swelling/gumbo shales, mobile formations, "
      "unconsolidated sands, key seats, ledges, junk",
      "Mechanical sticking: junk in hole, collapsed casing, undergauge hole, "
      "cement / hard bridges",
      "Identify the mechanism from the warning signs before attempting to free",
      "Differential sticking signs: no rotation, no circulation, static pipe, "
      "stuck across permeable zone",
      "Formation-related signs: pack-off, loss of circulation, cavings at "
      "surface, torque/drag increase",
      "Mechanical signs: stuck on trips at a known depth, rotation/circulation "
      "partially available",
      "Plan a stuck-pipe prevention program before spud: offset-well review, "
      "mud plan, jar placement, contingency equipment",
      "Good drilling practices: keep hole clean, avoid long static periods, "
      "monitor torque/drag/ECD trends",
      "Good tripping practices: fill hole, controlled speeds, ream tight spots, "
      "check fill on bottom",
      "Differential prevention: minimize overbalance, thin filter cake, "
      "pipe-free agents, keep pipe moving",
      "Formation prevention: inhibitive mud, adequate MW for stability, "
      "minimize exposure time",
      "Mechanical prevention: catch junk early, gauge trips, avoid ledges",
      "Freeing differentially stuck pipe: spot pipe-free agent, reduce MW if "
      "safe, jar with accelerator",
      "Freeing mechanically stuck pipe: work pipe, circulate, wash/ream, "
      "fishing if needed",
      "If all fails: free point indicator, back-off, sidetrack"]),

    # --- from 699 IADC Well Control Equipment & Procedures ---
    ("book_iadc_well_control",
     "Well Control Equipment & Procedures (IADC)",
     "Well Control",
     "699",
     "Well control equipment (BOP stack, accumulators, choke manifold) and "
     "procedures per IADC Drilling Manual 12th edition.",
     ["Well control barriers: primary (mud hydrostatic), secondary (BOP stack)",
      "BOP stack components: annular, pipe rams, blind/shear rams, "
      "choke & kill lines",
      "Accumulator unit: bottles pre-charged with nitrogen, operating pressure "
      "per API 16D",
      "Choke manifold: adjustable choke, remote panels, gauges",
      "BOP testing: low-pressure and high-pressure tests after nipple-up and "
      "per schedule",
      "Kick detection: pit volume gain, flow check, trip tank monitoring",
      "Shut-in procedure: close BOP, shut down pump, record SIDPP/SICP",
      "Kill methods: Driller's Method, Wait & Weight, Volumetric",
      "Drillers Method: circulate kick out at original MW, then weight up and "
      "circulate",
      "Wait & Weight: weight up in one circulation, maintain constant BHP",
      "Slow pump rates: measured and recorded for kill operations",
      "Trip procedures: fill hole, flow checks, trip tank discipline",
      "Gas handling: divert if shallow, strip if required, MGS for gas cut mud",
      "Equipment inspection: BOP stack, accumulators, choke line per schedule"]),

    # --- from 697 HPHT Course ---
    ("book_hpht_course",
     "HPHT Well Operations (Course)",
     "Well Control",
     "697",
     "HPHT well operations: design philosophy, well control, mud, casing, "
     "equipment selection per Aberdeen HPHT course.",
     ["HPHT definition: reservoir temperature >300°F and/or pressure >10,000 psi",
      "Design philosophy: two verified barriers at all times",
      "Mud selection: high-density, thermally stable, gas-tight",
      "Casing design: account for thermal expansion, trapped pressure, "
      "gas migration",
      "Wellhead & BOP: high-pressure rated, tested to maximum anticipated "
      "surface pressure",
      "Kick tolerance: calculated for worst-case kick; limited kick tolerance "
      "requires contingency",
      "Gas behavior: deep hot gas expands rapidly — early detection critical",
      "Mud gas separation: MGS sized for HPHT gas flow rates",
      "Temperature effects: mud rheology, cement slurry design, tool "
      "electronics rating",
      "Well control drills: practiced with HPHT scenarios",
      "Leak-off / formation integrity: verify each casing shoe",
      "Contingency: relief well planning for HPHT exploration"]),
]


def _find_source(pattern):
    for f in LIB.glob("*.txt"):
        if f.name.startswith(pattern + "_"):
            return f
    return None


def seed(force: bool = False):
    db = ProcedureDatabase()
    try:
        existing = db.conn.execute(
            "SELECT COUNT(*) AS c FROM procedures WHERE proc_key LIKE 'book_%'"
        ).fetchone()["c"]
        if existing and not force:
            print(f"✔ book procedures already seeded ({existing}) — "
                  f"use --force to re-seed.")
            return

        def cat_id(name):
            for c in db.get_all_categories():
                if c.name == name:
                    return c.id
            return db.add_category(name, icon="📚", sort_order=99)

        for key, name, cat, src_prefix, desc, steps in BOOK_PROCEDURES:
            src = _find_source(src_prefix)
            src_name = src.name.split("_", 1)[1].rsplit(".", 1)[0] if src else src_prefix
            cid = cat_id(cat)
            pid = db.add_procedure(
                name, cid,
                description=f"{desc} Source: {src_name} (generalized).",
                has_checklist=True, inputs_json="[]",
                tags=f"book,{cat.lower()}")
            db.conn.execute("UPDATE procedures SET proc_key=? WHERE id=?",
                            (key, pid))
            for s in steps:
                db.add_step(pid, _clean(s))
            # checklist: key practices
            for c in steps[-5:]:
                db.add_checklist_item(pid, _clean(c))
            print(f"  ✔ {name} ({len(steps)} steps)")

        db.conn.commit()
        print("done")
    finally:
        db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
