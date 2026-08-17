# ============================================================================
# FULL TEST RUNNER — run every suite in one go
# File: tests/run_all.py
#
# Run:  LD_LIBRARY_PATH=/tmp/glstubs PYTHONPATH=. QT_QPA_PLATFORM=offscreen \
#       python3 tests/run_all.py
#
# Suites:
#   1. Engineering reference tests (69)      — calculation accuracy
#   2. Governance tests (28)                 — backup/encryption/revisions
#   3. Template regression (51 templates)    — end-to-end document generation
#   4. UI smoke tests (17)                   — offscreen UI + wizard E2E
# Exit code 0 = everything passes.
# ============================================================================

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ENV = dict(os.environ)
ENV.setdefault("QT_QPA_PLATFORM", "offscreen")
ENV["PYTHONPATH"] = ROOT + os.pathsep + ENV.get("PYTHONPATH", "")

SUITES = [
    ("Engineering reference tests", "test_engineering_reference.py"),
    ("Governance tests",            "test_governance.py"),
    ("Template regression (51)",    "regression_templates.py"),
    ("UI smoke tests",              "test_ui_smoke.py"),
]


def main():
    failed = []
    for label, script in SUITES:
        print("=" * 64)
        print(f"▶ {label}")
        print("=" * 64)
        r = subprocess.run([sys.executable, os.path.join(HERE, script)],
                           env=ENV, cwd=ROOT)
        if r.returncode != 0:
            failed.append(script)
        print()
    print("#" * 64)
    if failed:
        print(f"FAILED suites: {', '.join(failed)}")
        return 1
    print("ALL SUITES PASSED ✅")
    return 0


if __name__ == "__main__":
    sys.exit(main())
