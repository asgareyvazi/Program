# ============================================================================
# DATABASE MIGRATION FRAMEWORK
# File: db_migrations.py
# Audit item (P0): versioned schema with upgrade path for every SQLite DB.
# Each migration is (version, name, sql). Running `migrate_all()` upgrades
# any DB that is behind. Version is stored in each DB's meta table.
# ============================================================================

import sqlite3
from pathlib import Path

APP_DIR = Path.home() / ".drilling_program"

# ---------------------------------------------------------------------------
# MIGRATIONS per database name (db filename -> list of (version, sql))
# ---------------------------------------------------------------------------

MIGRATIONS = {
    "procedures.db": [
        (2, "ALTER TABLE procedures ADD COLUMN status TEXT DEFAULT 'Draft'"),
        (3, "ALTER TABLE procedures ADD COLUMN owner TEXT DEFAULT ''"),
        (4, "ALTER TABLE procedures ADD COLUMN approved_by TEXT DEFAULT ''"),
        (5, "ALTER TABLE procedures ADD COLUMN effective_date TEXT DEFAULT ''"),
        (6, "ALTER TABLE procedures ADD COLUMN supersedes TEXT DEFAULT ''"),
        (7, "ALTER TABLE procedures ADD COLUMN hold_points TEXT DEFAULT '[]'"),
        (8, "ALTER TABLE procedures ADD COLUMN witness_points TEXT DEFAULT '[]'"),
        # Structured step execution model (audit P1): every step may carry
        # a precondition, acceptance criteria and hold/witness point flags.
        (9, "ALTER TABLE procedure_steps ADD COLUMN precondition TEXT DEFAULT ''"),
        (10, "ALTER TABLE procedure_steps ADD COLUMN acceptance TEXT DEFAULT ''"),
        (11, "ALTER TABLE procedure_steps ADD COLUMN hold_point INTEGER DEFAULT 0"),
        (12, "ALTER TABLE procedure_steps ADD COLUMN witness_point INTEGER DEFAULT 0"),
        (13, "ALTER TABLE procedure_steps ADD COLUMN role TEXT DEFAULT ''"),
        # Procedure <-> Well / Risk linking (audit P1)
        (14, "ALTER TABLE procedures ADD COLUMN linked_well_id TEXT DEFAULT ''"),
        (15, "ALTER TABLE procedures ADD COLUMN linked_section TEXT DEFAULT ''"),
        (16, "ALTER TABLE procedures ADD COLUMN linked_risk_ids TEXT DEFAULT '[]'"),
    ],
    "cbs.db": [
        (2, "ALTER TABLE cbs_items ADD COLUMN vendor TEXT DEFAULT ''"),
        (3, "ALTER TABLE cbs_items ADD COLUMN effective_date TEXT DEFAULT ''"),
    ],
    "problems.db": [
        (2, "ALTER TABLE problems ADD COLUMN decision_tree TEXT DEFAULT '[]'"),
        (3, "ALTER TABLE problems ADD COLUMN escalation TEXT DEFAULT ''"),
    ],
    "wells.db": [],
    "catalog.db": [],
    "time_breakdown.db": [],
    "master_procedures.db": [],
}


def get_version(conn: sqlite3.Connection) -> int:
    try:
        r = conn.execute(
            "SELECT value FROM meta WHERE key='schema_version'").fetchone()
        return int(r[0]) if r else 0
    except sqlite3.Error:
        return 0


def set_version(conn: sqlite3.Connection, version: int):
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES "
                 "('schema_version', ?)", (str(version),))
    conn.commit()


def migrate(db_path: str) -> tuple:
    """Migrate a single DB to the latest schema. Returns (before, after)."""
    name = Path(db_path).name
    steps = MIGRATIONS.get(name, [])
    if not steps:
        return 0, 0
    conn = sqlite3.connect(db_path)
    try:
        cur = get_version(conn)
        applied = 0
        for version, sql in sorted(steps, key=lambda x: x[0]):
            if version > cur:
                try:
                    conn.execute(sql)
                except sqlite3.OperationalError as e:
                    # column may already exist -> skip, don't crash
                    if "duplicate column" in str(e).lower():
                        pass
                    else:
                        raise
                applied += 1
                cur = version
        set_version(conn, cur)
        return (cur - applied, cur)
    finally:
        conn.close()


def migrate_all() -> dict:
    """Migrate every known DB in the app dir. Returns per-db results."""
    results = {}
    for name in MIGRATIONS:
        path = APP_DIR / name
        if path.exists():
            try:
                results[name] = migrate(str(path))
            except Exception as e:
                results[name] = ("error", str(e))
    return results


def status() -> str:
    """Human-readable migration status."""
    out = []
    for name, steps in MIGRATIONS.items():
        path = APP_DIR / name
        latest = max((v for v, _ in steps), default=0)
        if not path.exists():
            out.append(f"{name}: not created yet (latest schema v{latest})")
            continue
        try:
            conn = sqlite3.connect(str(path))
            cur = get_version(conn)
            conn.close()
            state = "OK" if cur >= latest else f"BEHIND (v{cur} -> v{latest})"
            out.append(f"{name}: v{cur} {state}")
        except Exception as e:
            out.append(f"{name}: error {e}")
    return "\n".join(out)


if __name__ == "__main__":
    print(status())
    print("\nRunning migrations...")
    print(migrate_all())
    print("\n" + status())
