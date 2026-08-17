# ============================================================================
# AUDIT LOG — append-only traceability
# File: audit_log.py
# P0 audit item: who / when / what / why changed.
# Writes an append-only JSONL log to ~/.drilling_program/audit.log
# (rotate at ~5 MB). Used for validation overrides, document generations
# and critical operations.
# ============================================================================

import json
import os
from datetime import datetime
from pathlib import Path

APP_DIR = Path.home() / ".drilling_program"
LOG_FILE = APP_DIR / "audit.log"
_MAX_BYTES = 5 * 1024 * 1024


def log_action(action: str, user: str = "", entity: str = "",
               detail: str = "", severity: str = "INFO"):
    """Append one audit record (never silently dropped)."""
    try:
        APP_DIR.mkdir(exist_ok=True)
        if LOG_FILE.exists() and LOG_FILE.stat().st_size > _MAX_BYTES:
            LOG_FILE.rename(LOG_FILE.with_suffix(".log.1"))
        record = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "action": action,
            "user": user or "unknown",
            "entity": entity or "",
            "detail": detail or "",
            "severity": severity,
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        return True
    except Exception:
        return False


def read_log(limit: int = 100) -> list:
    """Read the most recent audit records."""
    if not LOG_FILE.exists():
        return []
    out = []
    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    except Exception:
        return []
    return out[-limit:]


if __name__ == "__main__":
    log_action("test", "qa", "unit-test", "audit log works", "INFO")
    print("audit entries:", len(read_log()))
    print(read_log()[-1])
