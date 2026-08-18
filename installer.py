# ============================================================================
# NATIVE INSTALLER — zero-dependency setup for any machine
# File: installer.py
# Phase AI — install / verify / repair the application without PyInstaller:
#   python installer.py            -> full install (deps + databases + launchers)
#   python installer.py --check    -> verify installation only
#   python installer.py --launcher -> create desktop shortcuts only
#
# On Windows the PyInstaller route (packaging/DrillingProgram.spec) remains
# the way to get a standalone .exe; this installer is the fast path for
# engineer machines that already have Python.
# ============================================================================

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_DIR = Path.home() / ".drilling_program"

REQUIRED = [("PySide6", "PySide6"), ("python-docx", "docx"),
            ("openpyxl", "openpyxl"), ("cryptography", "cryptography")]
OPTIONAL = ["fastapi", "uvicorn", "httpx"]

EXPECTED_DB_ROWS = {
    "procedures.db": ("procedures", 100),
    "cbs.db": ("cbs_items", 300),
    "problems.db": ("problems", 20),
    "catalog.db": ("docs", 700),
    "master_procedures.db": ("master_procedures", 10),
}


def check_deps() -> dict:
    out = {}
    for pkg, mod in REQUIRED:
        try:
            __import__(mod)
            out[pkg] = True
        except ImportError:
            out[pkg] = False
    return out


def install_deps() -> bool:
    missing = [m for m, ok in check_deps().items() if not ok]
    if not missing:
        print("  ✔ all required packages present")
        return True
    print(f"  ▶ installing: {', '.join(missing)}")
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--break-system-packages",
         "-q"] + missing, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print(f"  ✘ pip failed: {r.stderr[-300:]}")
        return False
    return True


def check_databases() -> dict:
    import sqlite3
    out = {}
    for fname, (table, min_rows) in EXPECTED_DB_ROWS.items():
        p = APP_DIR / fname
        if not p.exists():
            out[fname] = {"exists": False, "rows": 0, "ok": False}
            continue
        try:
            con = sqlite3.connect(str(p))
            n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            con.close()
            out[fname] = {"exists": True, "rows": n,
                          "ok": n >= min_rows}
        except Exception as e:
            out[fname] = {"exists": True, "rows": -1, "ok": False,
                          "error": str(e)}
    return out


def build_databases() -> bool:
    try:
        import bootstrap
        return bootstrap.seed_all()
    except Exception as e:
        print(f"  ✘ bootstrap failed: {e}")
        return False


def make_launchers() -> list:
    """Create OS-appropriate launch shortcuts."""
    made = []
    if os.name == "nt":
        bat = ROOT / "start_drilling_program.bat"
        bat.write_text(
            f"@echo off\r\n"
            f"cd /d {ROOT}\r\n"
            f"pythonw launcher.py\r\n", encoding="utf-8")
        made.append(str(bat))
    else:
        sh = ROOT / "start_drilling_program.sh"
        sh.write_text(
            f"#!/usr/bin/env bash\n"
            f"cd {ROOT}\n"
            f"python3 launcher.py \"$@\"\n", encoding="utf-8")
        sh.chmod(0o755)
        made.append(str(sh))
        # freedesktop entry
        desktop = Path.home() / ".local/share/applications"
        desktop.mkdir(parents=True, exist_ok=True)
        entry = desktop / "drilling-program.desktop"
        entry.write_text(
            "[Desktop Entry]\n"
            "Type=Application\n"
            "Name=Drilling Program Generator\n"
            f"Exec={ROOT / 'start_drilling_program.sh'}\n"
            "Terminal=false\n"
            "Categories=Science;Engineering;\n", encoding="utf-8")
        made.append(str(entry))
    return made


def install() -> bool:
    print("=" * 60)
    print("DRILLING PROGRAM — INSTALLER")
    print("=" * 60)
    ok = True
    print("[1/3] Python packages")
    ok &= install_deps()
    print("[2/3] Databases")
    db = check_databases()
    missing_db = [f for f, s in db.items() if not s["ok"]]
    if missing_db:
        print(f"  ▶ {len(missing_db)} database(s) need seeding: "
              f"{', '.join(missing_db)}")
        ok &= build_databases()
    else:
        print("  ✔ all databases ready")
    print("[3/3] Launchers")
    launchers = make_launchers()
    for l in launchers:
        print(f"  ✔ {l}")
    print("=" * 60)
    print("INSTALL COMPLETE ✅" if ok else "INSTALL HAD ISSUES ⚠️")
    print("=" * 60)
    return ok


def check() -> bool:
    print("=" * 60)
    print("DRILLING PROGRAM — INSTALLATION CHECK")
    print("=" * 60)
    ok = True
    deps = check_deps()
    for m, present in deps.items():
        print(f"  {'✅' if present else '❌'} package: {m}")
        ok &= present
    db = check_databases()
    for f, s in db.items():
        if s["ok"]:
            print(f"  ✅ db: {f} ({s['rows']} rows)")
        else:
            print(f"  ❌ db: {f} ({s.get('rows', '?')} rows)"
                  + (" — run installer" if not s["exists"] else ""))
            ok &= s["exists"] and s["rows"] >= 0
    lib = ROOT / "programs" / "library"
    n_docs = len(list(lib.glob("*.txt"))) if lib.exists() else 0
    print(f"  {'✅' if n_docs > 700 else '❌'} library: {n_docs} docs")
    ok &= n_docs > 700
    print("=" * 60)
    print("CHECK PASSED ✅" if ok else "ISSUES FOUND — run: python installer.py")
    print("=" * 60)
    return ok


if __name__ == "__main__":
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else "install"
    if arg in ("--check", "-c", "check"):
        sys.exit(0 if check() else 1)
    if arg in ("--launcher", "-l"):
        for p in make_launchers():
            print("✔", p)
        sys.exit(0)
    sys.exit(0 if install() else 1)
