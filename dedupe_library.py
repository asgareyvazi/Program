# ============================================================================
# DEDUPE LIBRARY — remove exact duplicates + persistent hash manifest
# File: dedupe_library.py
# 1) Scans programs/library/*.txt, groups by MD5 of full content
# 2) For each duplicate group keeps ONE copy (prefers the 7xx range for
#    the operator-handbook sets; otherwise the lowest number)
# 3) Writes programs/library/.hashes.json — a COMMITTED manifest so the
#    ingest pipeline can detect duplicates permanently (survives sandbox/
#    machine restarts, unlike the runtime sqlite DB)
# 4) Prints a mapping old->kept so wizard_references can be remapped
# ============================================================================

import hashlib
import json
import re
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent / "programs" / "library"
MANIFEST = LIB / ".hashes.json"


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def prefer_keep(names: list) -> str:
    """Choose which duplicate copy to keep."""
    # prefer 7xx range (operator handbooks & reference books live there)
    for n in names:
        m = re.match(r"^(\d{3})_", n)
        if m and 700 <= int(m.group(1)) <= 899:
            return n
    # otherwise the lowest number
    def num(n):
        m = re.match(r"^(\d{3})_", n)
        return int(m.group(1)) if m else 9999
    return min(names, key=num)


def main(dry: bool = False):
    files = sorted(p for p in LIB.glob("*.txt") if p.name[:3].isdigit())
    groups = {}
    for f in files:
        h = file_hash(f)
        groups.setdefault(h, []).append(f.name)

    dup_groups = {h: names for h, names in groups.items() if len(names) > 1}
    print(f"files: {len(files)} | unique: {len(groups)} | dup groups: {len(dup_groups)}")

    keep_map = {}      # kept name -> kept name
    removed_map = {}   # removed name -> kept name
    for h, names in sorted(dup_groups.items(),
                           key=lambda kv: min(int(re.match(r'^(\d{3})_', n).group(1))
                                              for n in kv[1])):
        keep = prefer_keep(names)
        keep_map[keep] = keep
        for n in names:
            if n != keep:
                removed_map[n] = keep
        print(f"  KEEP {keep}")
        for n in names:
            if n != keep:
                print(f"    rm  {n}")

    if not dry:
        for n in removed_map:
            (LIB / n).unlink()

    # write manifest of the unique content hashes (survives restarts)
    manifest = {}
    for h, names in groups.items():
        keep = prefer_keep(names)
        manifest[h] = keep
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    print(f"\nmanifest written: {MANIFEST} ({len(manifest)} unique hashes)")

    # also write the remap for wizard_references
    remap = {int(re.match(r'^(\d{3})_', rm).group(1)):
             int(re.match(r'^(\d{3})_', keep).group(1))
             for rm, keep in removed_map.items()}
    (LIB / ".remap.json").write_text(
        json.dumps(remap, indent=1), encoding="utf-8")
    print(f"remap written: {len(remap)} entries")

    after = len(list(LIB.glob("*.txt"))) if not dry else len(files)
    print(f"after: {after} files")


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
