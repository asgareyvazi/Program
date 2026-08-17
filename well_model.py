# ============================================================================
# CANONICAL WELL MODEL — single source of truth for the whole application
# File: well_model.py
# Audit item (P0/P1): Well -> Revision -> Section -> sub-domains with stable
# canonical keys so procedures, risks, calculations, cost and documents all
# attach to the same well/revision/section.
#
# This is the structured backbone that the UI modules and generation
# services should read/write instead of ad-hoc dicts with string matching.
# ============================================================================

import json
import sqlite3
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

APP_DIR = Path.home() / ".drilling_program"
WELL_DB = str(APP_DIR / "wells.db")


# ---------------------------------------------------------------------------
# DOMAIN OBJECTS
# ---------------------------------------------------------------------------

@dataclass
class FormationWindow:
    name: str = ""
    top_md_m: float = 0.0
    top_tvd_m: float = 0.0
    pp_ppg: float = 0.0          # pore pressure
    fg_ppg: float = 0.0          # fracture gradient
    lithology: str = ""
    hazard: str = ""


@dataclass
class HoleSection:
    section_id: str = ""         # stable key, e.g. "SEC-001"
    name: str = ""               # e.g. '12-1/4" Hole Section'
    hole_size_in: float = 0.0
    depth_from_m: float = 0.0
    depth_to_m: float = 0.0
    casing_size_in: float = 0.0
    casing_grade: str = ""
    casing_weight_ppf: float = 0.0
    mud_type: str = ""
    mud_weight_ppg: float = 0.0
    bha_notes: str = ""
    formations: List[FormationWindow] = field(default_factory=list)


@dataclass
class WellRevision:
    revision: str = "01"
    status: str = "Draft"        # Draft/Review/Approved/Released/Superseded
    revision_date: str = ""
    sections: List[HoleSection] = field(default_factory=list)
    well_data: Dict = field(default_factory=dict)   # free-form well data
    notes: str = ""


@dataclass
class Well:
    well_id: str = ""            # stable canonical id (UUID)
    well_name: str = ""
    field_name: str = ""
    operator: str = ""
    contractor: str = ""
    well_type: str = "Vertical"  # Vertical/Deviated/Horizontal/ERD/HPHT/...
    environment: str = "Onshore"
    created_date: str = ""
    modified_date: str = ""
    revisions: List[WellRevision] = field(default_factory=list)


# ---------------------------------------------------------------------------
# DATABASE (canonical store)
# ---------------------------------------------------------------------------

class WellDatabase:
    """Stores wells + revisions + sections with stable IDs."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str = None):
        self.db_path = db_path or WELL_DB
        APP_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create()

    def _create(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY, value TEXT
            );
            CREATE TABLE IF NOT EXISTS wells (
                well_id TEXT PRIMARY KEY,
                well_name TEXT, field_name TEXT, operator TEXT, contractor TEXT,
                well_type TEXT, environment TEXT,
                created_date TEXT, modified_date TEXT
            );
            CREATE TABLE IF NOT EXISTS revisions (
                revision_id INTEGER PRIMARY KEY AUTOINCREMENT,
                well_id TEXT NOT NULL,
                revision TEXT, status TEXT, revision_date TEXT,
                well_data TEXT, notes TEXT,
                FOREIGN KEY (well_id) REFERENCES wells(well_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS sections (
                section_id TEXT PRIMARY KEY,
                revision_id INTEGER NOT NULL,
                name TEXT, hole_size_in REAL, depth_from_m REAL, depth_to_m REAL,
                casing_size_in REAL, casing_grade TEXT, casing_weight_ppf REAL,
                mud_type TEXT, mud_weight_ppg REAL, bha_notes TEXT,
                formations TEXT,
                FOREIGN KEY (revision_id) REFERENCES revisions(revision_id)
                    ON DELETE CASCADE
            );
        """)
        self.conn.execute(
            "INSERT OR REPLACE INTO meta (key, value) VALUES ('schema_version', ?)",
            (self.SCHEMA_VERSION,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    # ---- wells ----

    def save_well(self, well: Well) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not well.well_id:
            well.well_id = uuid.uuid4().hex[:12].upper()
        if not well.created_date:
            well.created_date = now
        well.modified_date = now
        self.conn.execute(
            "INSERT OR REPLACE INTO wells VALUES (?,?,?,?,?,?,?,?,?)",
            (well.well_id, well.well_name, well.field_name, well.operator,
             well.contractor, well.well_type, well.environment,
             well.created_date, well.modified_date))
        # revisions
        self.conn.execute("DELETE FROM revisions WHERE well_id=?", (well.well_id,))
        for rev in well.revisions:
            cur = self.conn.execute(
                "INSERT INTO revisions (well_id, revision, status, revision_date,"
                " well_data, notes) VALUES (?,?,?,?,?,?)",
                (well.well_id, rev.revision, rev.status, rev.revision_date,
                 json.dumps(rev.well_data), rev.notes))
            rid = cur.lastrowid
            for sec in rev.sections:
                self.conn.execute(
                    "INSERT INTO sections (section_id, revision_id, name, "
                    "hole_size_in, depth_from_m, depth_to_m, casing_size_in, "
                    "casing_grade, casing_weight_ppf, mud_type, mud_weight_ppg, "
                    "bha_notes, formations) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (sec.section_id or uuid.uuid4().hex[:8].upper(), rid,
                     sec.name, sec.hole_size_in, sec.depth_from_m,
                     sec.depth_to_m, sec.casing_size_in, sec.casing_grade,
                     sec.casing_weight_ppf, sec.mud_type, sec.mud_weight_ppg,
                     sec.bha_notes, json.dumps([asdict(f) for f in sec.formations])))
        self.conn.commit()
        return well.well_id

    def get_well(self, well_id: str) -> Optional[Well]:
        row = self.conn.execute("SELECT * FROM wells WHERE well_id=?",
                                (well_id,)).fetchone()
        if not row:
            return None
        well = Well(well_id=row["well_id"], well_name=row["well_name"],
                    field_name=row["field_name"], operator=row["operator"],
                    contractor=row["contractor"], well_type=row["well_type"],
                    environment=row["environment"],
                    created_date=row["created_date"],
                    modified_date=row["modified_date"])
        for rr in self.conn.execute(
                "SELECT * FROM revisions WHERE well_id=? ORDER BY revision",
                (well_id,)).fetchall():
            rev = WellRevision(revision=rr["revision"], status=rr["status"],
                               revision_date=rr["revision_date"],
                               notes=rr["notes"])
            try:
                rev.well_data = json.loads(rr["well_data"] or "{}")
            except Exception:
                rev.well_data = {}
            for ss in self.conn.execute(
                    "SELECT * FROM sections WHERE revision_id=? ORDER BY "
                    "depth_from_m", (rr["revision_id"],)).fetchall():
                sec = HoleSection(
                    section_id=ss["section_id"], name=ss["name"],
                    hole_size_in=ss["hole_size_in"],
                    depth_from_m=ss["depth_from_m"],
                    depth_to_m=ss["depth_to_m"],
                    casing_size_in=ss["casing_size_in"],
                    casing_grade=ss["casing_grade"],
                    casing_weight_ppf=ss["casing_weight_ppf"],
                    mud_type=ss["mud_type"], mud_weight_ppg=ss["mud_weight_ppg"],
                    bha_notes=ss["bha_notes"])
                try:
                    sec.formations = [FormationWindow(**d) for d in
                                      json.loads(ss["formations"] or "[]")]
                except Exception:
                    sec.formations = []
                rev.sections.append(sec)
            well.revisions.append(rev)
        return well

    def list_wells(self) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT w.*, (SELECT COUNT(*) FROM revisions r WHERE r.well_id=w.well_id)"
            " AS n_rev FROM wells w ORDER BY w.modified_date DESC").fetchall()
        return [dict(r) for r in rows]

    def delete_well(self, well_id: str):
        self.conn.execute("DELETE FROM wells WHERE well_id=?", (well_id,))
        self.conn.commit()


# ---------------------------------------------------------------------------
# CONVENIENCE — build a Well from wizard input values
# ---------------------------------------------------------------------------

def well_from_values(well_id: str, values: Dict) -> Well:
    """Create/update a Well object from a flat wizard values dict."""
    well = Well(
        well_id=well_id or "",
        well_name=str(values.get("well_name") or values.get("well_name") or ""),
        field_name=str(values.get("field_name") or ""),
        operator=str(values.get("operator") or ""),
        contractor=str(values.get("contractor") or ""),
        well_type=str(values.get("well_type") or "Vertical"),
        environment=str(values.get("environment") or "Onshore"),
    )
    rev = WellRevision(
        revision=str(values.get("revision") or "01"),
        status="Draft",
        revision_date=str(values.get("doc_date") or ""),
    )
    # one section from the key drilling inputs (when present)
    hole = values.get("hole_size") or values.get("hole_size")
    if hole:
        sec = HoleSection(
            name=f'{hole} Hole Section',
            hole_size_in=_parse_size(hole),
            depth_to_m=_fnum(values.get("depth_m") or values.get("target_depth")),
            casing_size_in=_parse_size(values.get("casing_size") or ""),
            casing_grade=str(values.get("casing_grade") or ""),
            mud_type=str(values.get("mud_type") or ""),
            mud_weight_ppg=_fnum(values.get("mud_weight")),
            bha_notes=str(values.get("bha_plan") or ""),
        )
        rev.sections.append(sec)
    well.revisions.append(rev)
    return well


def _fnum(v) -> float:
    try:
        return float(v) if v not in (None, "") else 0.0
    except (TypeError, ValueError):
        return 0.0


def _parse_size(s: str) -> float:
    s = (s or "").strip().replace('"', '').replace('in', '')
    try:
        if "-" in s and "/" in s:
            w, f = s.split("-", 1)
            n, d = f.split("/", 1)
            return float(w) + float(n) / float(d)
        if "/" in s:
            n, d = s.split("/", 1)
            return float(n) / float(d)
        return float(s)
    except (ValueError, ZeroDivisionError):
        return 0.0


if __name__ == "__main__":
    db = WellDatabase()
    w = well_from_values("", {"well_name": "WELL-1", "field_name": "F",
                              "operator": "the Operator", "hole_size": '12-1/4"',
                              "depth_m": "3200", "mud_weight": "12"})
    wid = db.save_well(w)
    loaded = db.get_well(wid)
    print("well_id:", wid, "| name:", loaded.well_name,
          "| sections:", len(loaded.revisions[0].sections),
          "| hole:", loaded.revisions[0].sections[0].hole_size_in)
    print("list:", db.list_wells()[0]["well_name"])
    db.close()
