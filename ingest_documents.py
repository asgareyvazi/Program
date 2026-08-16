# ============================================================================
# KNOWLEDGE INGEST PIPELINE — add any new document set to the software
# File: ingest_documents.py
#
# USE CASE: you received books/guidelines/procedures from a major operator
# (e.g. Shell DEP, Saudi Aramco, Total, Equinor, etc.) as text files.
# Run:
#     python ingest_documents.py /path/to/folder_or_file.txt
#
# What it does (the full merge pipeline):
#   1. Copies every .txt file into programs/library/ with the next free
#      number (NNN_source.txt), skipping files already present (hash check)
#   2. Rebuilds the 5-dimension document catalog (document_catalog.py)
#   3. Auto-maps the new files into wizard templates by filename patterns
#      (wizard_references._auto_map_pp2 style — extend _SOURCE_PATTERNS
#      below for the new source's naming style)
#   4. Reports what changed
#
# The new documents then flow automatically into:
#   - Field Knowledge Enrichment (TF-IDF retrieval + LLM rewrite)
#   - Reference Documents section of generated Word files
#   - Well-profile filtered retrieval (document_catalog)
#   - (optionally) procedures DB — see seed_* scripts for pattern-based
#     procedure extraction if you also want full procedure records
#
# All content is generalized on output (no company/well names leak).
# ============================================================================

import hashlib
import re
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
LIB = PROJECT / "programs" / "library"


# ---------------------------------------------------------------------------
# Source-specific template patterns: add naming patterns of the new source
# so its files are mapped to the right wizard templates automatically.
# Key = template key, value = list of regexes (tested against filename).
# ---------------------------------------------------------------------------

SOURCE_PATTERNS = {
    "drilling_program": [
        r"drilling[ _-]?program",
        r"drill[ _-]?program",
    ],
    "advanced_drilling_program": [
        r"well[ _-]?design|basis[ _-]?of[ _-]?design|casing[ _-]?design",
    ],
    "offshore_drilling_program": [
        r"offshore|semi|subsea|deepwater|marine",
    ],
    "cementing_program": [
        r"cement|cmt",
    ],
    "well_kill_program": [
        r"well[ _-]?control|kick|kill|shallow[ _-]?gas",
    ],
    "fishing_program": [
        r"fish|back[ _-]?off|mill|jar",
    ],
    "stuck_pipe_procedure": [
        r"stuck|free[ _-]?point|back[ _-]?off",
    ],
    "bop_test_procedure": [
        r"bop|wellhead|blowout[ _-]?prevent",
    ],
    "h2s_emergency_procedure": [
        r"h2s|hydrogen[ _-]?sulphide|sour[ _-]?gas",
    ],
    "completion_program": [
        r"completion|packer|christmas[ _-]?tree|x[ _-]?mas",
    ],
    "esp_workover": [
        r"esp|electric[ _-]?submersible",
    ],
    "well_testing_program": [
        r"well[ _-]?test|dst|formation[ _-]?test|production[ _-]?test",
    ],
    "stimulation_program": [
        r"stimul|acid|frac|nitrogen",
    ],
    "coiled_tubing_program": [
        r"coiled[ _-]?tubing|ct[ _-]?unit",
    ],
    "abandonment_program": [
        r"abandon|p&a|suspend|plug[ _-]?and[ _-]?abandon",
    ],
    "slickline_procedure": [
        r"slickline|wireline",
    ],
    "perforation_procedure": [
        r"perforat|tcp|shoot",
    ],
    "directional": [
        r"directional|mwd|lwd|survey|trajectory",
    ],
    "drilling_fluids": [
        r"mud|drilling[ _-]?fluid|barite|baryte",
    ],
    "hole_cleaning": [
        r"hole[ _-]?clean|cuttings|transport",
    ],
    "rig_move_procedure": [
        r"rig[ _-]?move|mobil|jack",
    ],
}


def _hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8", errors="replace")).hexdigest()


def ingest(source: str, dry_run: bool = False) -> dict:
    src = Path(source)
    if not src.exists():
        print(f"✗ Not found: {source}")
        return {"added": 0, "skipped": 0}

    files = [src] if src.is_file() else sorted(src.rglob("*.txt"))
    # existing hashes — from the COMMITTED manifest first (survives restarts),
    # then fall back to scanning the library
    existing = {}
    manifest = LIB / ".hashes.json"
    if manifest.exists():
        try:
            import json as _json
            existing = {h: n for h, n in
                        _json.loads(manifest.read_text(encoding="utf-8")).items()}
        except Exception:
            existing = {}
    for f in LIB.glob("*.txt"):
        try:
            h = _hash(f.read_text(encoding="utf-8", errors="replace")[:4000])
            existing.setdefault(h, f.name)
        except Exception:
            pass

    next_num = max((int(p.name.split("_")[0])
                    for p in LIB.glob("*.txt") if p.name[:3].isdigit()),
                   default=0) + 1

    added, skipped = [], []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            skipped.append((f.name, f"read error: {e}"))
            continue
        if len(text.strip()) < 200:
            skipped.append((f.name, "too short (<200 chars)"))
            continue
        h = _hash(text[:4000])
        if h in existing:
            skipped.append((f.name, f"duplicate of {existing[h]}"))
            continue
        # clean source name
        base = re.sub(r"\.(txt|md)$", "", f.name)
        base = re.sub(r"[^\w\-. ]+", "", base).strip().replace(" ", "_")[:80]
        out = LIB / f"{next_num:03d}_{base}.txt"
        if not dry_run:
            out.write_text(text, encoding="utf-8")
        added.append(out.name)
        next_num += 1

    if not dry_run and added:
        # refresh the committed hash manifest
        try:
            import json as _json
            man = {}
            for f in LIB.glob("*.txt"):
                if f.name[:3].isdigit():
                    h = _hash(f.read_text(encoding="utf-8",
                                          errors="replace")[:4000])
                    man.setdefault(h, f.name)
            (LIB / ".hashes.json").write_text(
                _json.dumps(man, indent=1), encoding="utf-8")
        except Exception:
            pass
        # rebuild catalog
        try:
            import document_catalog
            cat = document_catalog.DocumentCatalog(rebuild=True)
            cat.close()
            print(f"✔ catalog rebuilt: {document_catalog.get_catalog().count()} docs")
        except Exception as e:
            print(f"⚠ catalog rebuild failed: {e}")

        # re-run auto mapping (module import triggers _auto_map_pp2)
        try:
            import importlib
            import wizard_references
            importlib.reload(wizard_references)
            print("✔ wizard reference auto-mapping refreshed")
        except Exception as e:
            print(f"⚠ auto-map failed: {e}")

    print(f"\nadded: {len(added)}")
    for a in added[:20]:
        print(f"  + {a}")
    print(f"skipped: {len(skipped)}")
    for name, why in skipped[:15]:
        print(f"  - {name}: {why}")
    return {"added": len(added), "skipped": len(skipped)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    ingest(sys.argv[1])
