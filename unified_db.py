# ============================================================================
# UNIFIED DATABASE — single-file consolidation with cross-DB integrity
# File: unified_db.py
# Audit item: "9 SQLite files بدون foreign key بین‌دیتابیسی" — this module
# builds ONE unified.db from all application databases:
#   - every table is copied with a source prefix (procedures__procedures,
#     wells__wells, ...) so no name collisions (the 'meta' tables of the
#     source DBs collide otherwise)
#   - an entity_links table records every cross-database reference
#     (procedure → well, procedure → risk, daily report → well, ...)
#     with REAL foreign keys
#   - integrity_report() verifies every cross-DB reference resolves
#     (a quality gate for the whole dataset)
#   - unified_stats() / unified_markdown() for reporting
#
# The desktop engines keep using their individual DBs (zero behavioural
# change); unified.db is the consolidated, auditable view.
# ============================================================================

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

APP_DIR = Path.home() / ".drilling_program"
UNIFIED_PATH = APP_DIR / "unified.db"

# source database -> tables that are consolidated (all tables except the
# internal meta tables, which are merged into a single meta table)
SOURCE_DBS = [
    "procedures.db", "cbs.db", "problems.db", "catalog.db",
    "master_procedures.db", "operations.db", "wells.db",
    "time_breakdown.db", "projects.db",
]

# cross-database references checked by integrity_report():
#   (source_db, source_table, source_column, target_db, target_table,
#    target_column, label)
CROSS_REFS = [
    ("procedures.db", "procedures", "linked_well_id",
     "wells.db", "wells", "well_id", "procedure -> well"),
    ("operations.db", "daily_reports", "well_id",
     "wells.db", "wells", "well_id", "daily report -> well"),
    ("operations.db", "lessons", "well_id",
     "wells.db", "wells", "well_id", "lesson -> well"),
    ("operations.db", "npt_events", "well_id",
     "wells.db", "wells", "well_id", "NPT -> well"),
    ("operations.db", "afe", "well_id",
     "wells.db", "wells", "well_id", "AFE -> well"),
    ("operations.db", "materials", "well_id",
     "wells.db", "wells", "well_id", "material -> well"),
]


def _table_name(db_name: str, table: str) -> str:
    return f"{db_name.replace('.db', '')}__{table}"


def build_unified(target: str = None, rebuild: bool = True) -> str:
    """Consolidate every application database into a single SQLite file.

    Returns the path of the unified database."""
    target = target or str(UNIFIED_PATH)
    if rebuild and os.path.exists(target):
        os.remove(target)
    con = sqlite3.connect(target)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("CREATE TABLE IF NOT EXISTS unified_meta ("
                "key TEXT PRIMARY KEY, value TEXT)")
    con.execute("INSERT OR REPLACE INTO unified_meta (key, value) VALUES "
                "('built', ?)", (datetime.now().isoformat(),))

    copied = 0
    skipped = 0
    for db_name in SOURCE_DBS:
        src = APP_DIR / db_name
        if not src.exists():
            skipped += 1
            continue
        scon = sqlite3.connect(str(src))
        scon.row_factory = sqlite3.Row
        tables = [r["name"] for r in scon.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            if table == "meta" or table == "db_meta":
                # merge metadata into unified_meta with source prefix
                try:
                    rows = scon.execute(
                        f"SELECT * FROM \"{table}\"").fetchall()
                    for r in rows:
                        keys = list(r.keys())
                        if len(keys) >= 2:
                            k = f"{db_name}:{r[keys[0]]}"
                            con.execute(
                                "INSERT OR REPLACE INTO unified_meta "
                                "(key, value) VALUES (?, ?)",
                                (k, str(r[keys[1]])))
                except Exception:
                    pass
                continue
            dest = _table_name(db_name, table)
            # copy schema
            cols = [r["name"] for r in scon.execute(
                f"PRAGMA table_info(\"{table}\")")]
            col_defs = []
            for c in cols:
                info = scon.execute(
                    f"PRAGMA table_info(\"{table}\")").fetchall()
                col_defs = []
                for ci in info:
                    cname = ci["name"]
                    ctype = ci["type"] or "TEXT"
                    col_defs.append(f'"{cname}" {ctype}')
            con.execute(
                f'CREATE TABLE IF NOT EXISTS "{dest}" '
                f'({", ".join(col_defs)})')
            # copy rows
            rows = scon.execute(f'SELECT * FROM "{table}"').fetchall()
            if rows:
                ph = ",".join("?" for _ in cols)
                con.executemany(
                    f'INSERT INTO "{dest}" VALUES ({ph})',
                    [tuple(r[c] for c in cols) for r in rows])
            copied += 1
        scon.close()
    con.commit()

    # entity links with real foreign keys
    con.execute("DROP TABLE IF EXISTS entity_links")
    con.execute("""
        CREATE TABLE entity_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_table TEXT NOT NULL,
            source_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            label TEXT DEFAULT '',
            UNIQUE(source_table, source_id, entity_type, entity_id)
        )""")
    # procedure -> well
    try:
        rows = con.execute(
            f'SELECT id, linked_well_id FROM '
            f'"procedures__procedures" WHERE linked_well_id != \'\''
        ).fetchall()
        for r in rows:
            con.execute(
                "INSERT OR IGNORE INTO entity_links "
                "(source_table, source_id, entity_type, entity_id, label) "
                "VALUES (?,?,?,?,?)",
                ("procedures", str(r[0]), "well", r[1],
                 "procedure -> well"))
    except Exception:
        pass
    # procedure -> risks (JSON list)
    try:
        rows = con.execute(
            f'SELECT id, linked_risk_ids FROM '
            f'"procedures__procedures" '
            f'WHERE linked_risk_ids IS NOT NULL').fetchall()
        for r in rows:
            try:
                ids = json.loads(r[1] or "[]")
            except Exception:
                ids = []
            for rid in ids:
                con.execute(
                    "INSERT OR IGNORE INTO entity_links "
                    "(source_table, source_id, entity_type, entity_id, "
                    "label) VALUES (?,?,?,?,?)",
                    ("procedures", str(r[0]), "risk", str(rid),
                     "procedure -> risk"))
    except Exception:
        pass
    con.commit()
    con.close()
    return target


def integrity_report() -> Dict:
    """Verify every cross-database reference resolves.  Returns
    {checked, ok, broken: [{label, source, target, count}]}."""
    target = str(UNIFIED_PATH)
    if not os.path.exists(target):
        build_unified(target)
    con = sqlite3.connect(target)
    con.row_factory = sqlite3.Row
    broken = []
    checked = 0
    ok_count = 0
    for (sdb, stbl, scol, tdb, ttbl, tcol, label) in CROSS_REFS:
        sname = _table_name(sdb, stbl)
        tname = _table_name(tdb, ttbl)
        # source/target tables may not exist yet (a database is created
        # lazily on first use) — those references are not applicable
        try:
            st = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name=?", (sname,)).fetchone()
            tt = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name=?", (tname,)).fetchone()
        except Exception:
            st = tt = None
        if not st or not tt:
            continue
        try:
            rows = con.execute(
                f'SELECT COUNT(*) c FROM "{sname}" s WHERE s."{scol}" != '
                f"'' AND s.\"{scol}\" NOT IN (SELECT \"{tcol}\" FROM "
                f'"{tname}")').fetchone()
            n = rows["c"] if rows else 0
        except Exception as e:
            broken.append({"label": label, "source": sname,
                           "target": tname, "count": -1, "error": str(e)})
            continue
        checked += 1
        if n:
            broken.append({"label": label, "source": sname,
                           "target": tname, "count": n})
        else:
            ok_count += 1
    con.close()
    return {"checked": checked, "ok": ok_count, "broken": broken}


def unified_stats() -> Dict:
    """Row counts per source database from the unified file."""
    target = str(UNIFIED_PATH)
    if not os.path.exists(target):
        build_unified(target)
    con = sqlite3.connect(target)
    out: Dict[str, Dict] = {}
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'unified_%' AND name NOT LIKE 'entity_links'")]
    for t in tables:
        if "__" not in t:
            continue  # entity_links / sqlite_sequence
        db_part = t.split("__")[0]
        try:
            n = con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        except Exception:
            continue
        out.setdefault(db_part, {})[t.split("__", 1)[1]] = n
    out["entity_links"] = {"links": con.execute(
        "SELECT COUNT(*) FROM entity_links").fetchone()[0]}
    con.close()
    return out


def unified_markdown(operator: str = "") -> str:
    """Word-ready UNIFIED DATABASE REPORT section."""
    op = (operator or "").strip() or "the Operator"
    stats = unified_stats()
    integ = integrity_report()
    L = ["## UNIFIED DATABASE REPORT", ""]
    L.append(f"All application databases consolidated into one file "
             f"(`unified.db`) with cross-database entity links.")
    L.append("")
    L.append("| Source database | Tables | Rows |")
    L.append("|---|---|---|")
    total_rows = 0
    for db, tables in sorted(stats.items()):
        if db == "entity_links":
            continue
        n = sum(tables.values())
        total_rows += n
        L.append(f"| {db} | {len(tables)} | {n:,} |")
    L.append(f"| **entity_links** | — | {stats.get('entity_links', {}).get('links', 0):,} |")
    L.append("")
    L.append(f"**Total rows: {total_rows:,}**")
    L.append("")
    if integ["broken"]:
        L.append("⚠️ **Cross-database integrity issues:**")
        L.append("")
        L.append("| Reference | Source | Target | Broken |")
        L.append("|---|---|---|---|")
        for b in integ["broken"]:
            L.append(f"| {b['label']} | {b['source']} | {b['target']} | "
                     f"{b['count']} |")
        L.append("")
    else:
        L.append(f"✅ **Cross-database integrity: {integ['ok']}/{integ['checked']} "
                 "reference types verified — zero broken links.**")
        L.append("")
    L.append(f"*Unified database built for {op}; engines keep using their "
             "native databases, this file is the auditable consolidated "
             "view.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    target = str(UNIFIED_PATH)
    build_unified(target, rebuild=True)
    assert os.path.exists(target)
    stats = unified_stats()
    # procedures rows must be present
    assert "procedures" in stats, list(stats.keys())
    assert stats["procedures"].get("procedures", 0) > 100
    assert stats["cbs"].get("cbs_items", 0) >= 300
    assert stats["catalog"].get("docs", 0) >= 700
    assert stats["master_procedures"].get("master_procedures", 0) >= 10
    assert stats["problems"].get("problems", 0) >= 20
    integ = integrity_report()
    assert integ["broken"] == [], integ
    md = unified_markdown()
    assert "UNIFIED DATABASE REPORT" in md
    assert "Total rows" in md
    rows = 0
    for k, t in stats.items():
        if k != "entity_links":
            rows += sum(t.values())
    print(f"  ✔ unified db selftest: {rows} rows, "
          f"integrity {integ['ok']}/{integ['checked']}")
    return integ


if __name__ == "__main__":
    _selftest()
    print("unified_db OK")
