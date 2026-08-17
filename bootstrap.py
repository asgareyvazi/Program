# ============================================================================
# ONE-COMMAND BOOTSTRAP — seed every database on any machine
# File: bootstrap.py
#
# Runs every seed/rebuild step idempotently so a fresh checkout works
# immediately:
#   python3 bootstrap.py
#
# Steps: base procedures -> pp2 -> BP -> offshore -> books -> scrub ->
#        CBS + time breakdown -> master procedures -> document catalog ->
#        schema migrations.
# ============================================================================

import os
import shutil
import subprocess
import sys
from pathlib import Path

APP_DIR = Path.home() / ".drilling_program"


def _run(module: str, *args: str) -> bool:
    cmd = [sys.executable, f"{module}.py"] + list(args)
    print(f"  ▶ {module} {' '.join(args)}")
    try:
        r = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)),
                           capture_output=True, text=True, timeout=900)
    except Exception as e:
        print(f"    ✘ {e}")
        return False
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()
        print("    ✘ failed:", " | ".join(tail[-2:])[:200])
        return False
    last = (r.stdout or r.stderr).strip().splitlines()
    if last:
        print(f"    ✔ {last[-1][:160]}")
    return True


def seed_all(verbose: bool = True) -> bool:
    print("=" * 64)
    print("DRILLING PROGRAM — DATABASE BOOTSTRAP")
    print("=" * 64)
    ok = True
    ok &= _run("seed_procedures_v2")
    ok &= _run("seed_pp2_procedures", "--force")
    ok &= _run("seed_bp_procedures", "--force")
    ok &= _run("seed_offshore_procedures", "--force")
    ok &= _run("seed_book_procedures", "--force")
    ok &= _run("scrub_procedures_db")
    ok &= _run("seed_azns_prices", "--force")

    # master procedures rebuild (fresh DB)
    try:
        (APP_DIR / "master_procedures.db").unlink()
    except OSError:
        pass
    ok &= _run("master_procedures", "--force")

    # document catalog rebuild (fresh DB)
    try:
        (APP_DIR / "catalog.db").unlink()
    except OSError:
        pass
    ok &= _run("document_catalog")

    ok &= _run("db_migrations")

    # problems DB seeds itself on first open
    try:
        from drilling_problems_db import ProblemDatabase
        n = len(ProblemDatabase().all())
        print(f"  ✔ problems: {n} seeded")
    except Exception as e:
        print(f"  ⚠ problems: {e}")

    print("=" * 64)
    if ok:
        print("BOOTSTRAP COMPLETE ✅ — run tests/validate_outputs.py now.")
    else:
        print("BOOTSTRAP had failures — see messages above.")
    print("=" * 64)
    return ok


if __name__ == "__main__":
    sys.exit(0 if seed_all() else 1)
