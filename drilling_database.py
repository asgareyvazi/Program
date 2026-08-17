# ============================================================================
# UNIFIED DRILLING DATABASE
# File: drilling_database.py
# SQLite database for drilling projects (save/load/compare)
# ============================================================================

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import asdict


class DrillingProjectDatabase:
    """دیتابیس یکپارچه پروژه‌های حفاری"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            app_dir = Path.home() / ".drilling_program"
            app_dir.mkdir(exist_ok=True)
            db_path = str(app_dir / "projects.db")

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                well_name TEXT DEFAULT '',
                field_name TEXT DEFAULT '',
                operator TEXT DEFAULT '',
                well_type TEXT DEFAULT '',
                status TEXT DEFAULT 'Draft',
                project_data TEXT DEFAULT '{}',
                created_date TEXT,
                modified_date TEXT,
                notes TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS project_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT DEFAULT '',
                FOREIGN KEY (project_id) REFERENCES projects(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS project_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                revision INTEGER NOT NULL,
                snapshot_json TEXT NOT NULL,
                created_date TEXT NOT NULL,
                note TEXT DEFAULT '',
                FOREIGN KEY (project_id) REFERENCES projects(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_proj_name
                ON projects(name);
            CREATE INDEX IF NOT EXISTS idx_proj_well
                ON projects(well_name);
        """)
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

    # ================================================================
    # PROJECT CRUD
    # ================================================================

    def save_project(self, project_obj, name: str = None) -> int:
        """ذخیره پروژه از WellProject object"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ci = project_obj.company_info
        wi = project_obj.well_info

        proj_name = name or ci.well_name or "Untitled Project"
        well_name = ci.well_name or ""
        field_name = ci.field_name or ""
        operator = ci.operator_name or ""
        well_type = wi.well_type or ""

        # Serialize entire project to JSON
        try:
            data_dict = asdict(project_obj)
            project_json = json.dumps(data_dict, ensure_ascii=False)
        except Exception:
            project_json = "{}"

        # Check if project with same name exists
        existing = self.conn.execute(
            "SELECT id FROM projects WHERE name=?",
            (proj_name,)).fetchone()

        if existing:
            # Update
            self.conn.execute(
                "UPDATE projects SET well_name=?, field_name=?, "
                "operator=?, well_type=?, project_data=?, "
                "modified_date=? WHERE id=?",
                (well_name, field_name, operator, well_type,
                 project_json, now, existing['id']))
            proj_id = existing['id']

            self._add_history(proj_id, "Updated", f"Project updated")
        else:
            # Insert
            cur = self.conn.execute(
                "INSERT INTO projects "
                "(name, well_name, field_name, operator, well_type, "
                "status, project_data, created_date, modified_date) "
                "VALUES (?, ?, ?, ?, ?, 'Draft', ?, ?, ?)",
                (proj_name, well_name, field_name, operator, well_type,
                 project_json, now, now))
            proj_id = cur.lastrowid

            self._add_history(proj_id, "Created", f"Project created")

        # Revision snapshot — every save creates a full restorable version
        # (audit buyer Q4: "can we rebuild a previous version?").
        self._snapshot(proj_id, project_json,
                       "Created" if not existing else "Saved")

        self.conn.commit()
        return proj_id

    def load_project(self, project_id: int) -> Optional[Dict]:
        """لود پروژه - برمی‌گردونه dict"""
        row = self.conn.execute(
            "SELECT * FROM projects WHERE id=?",
            (project_id,)).fetchone()
        if not row:
            return None

        try:
            data = json.loads(row['project_data'])
        except json.JSONDecodeError:
            data = {}

        return {
            'id': row['id'],
            'name': row['name'],
            'well_name': row['well_name'],
            'field_name': row['field_name'],
            'operator': row['operator'],
            'status': row['status'],
            'created': row['created_date'],
            'modified': row['modified_date'],
            'notes': row['notes'],
            'data': data
        }

    def get_all_projects(self) -> List[Dict]:
        """لیست تمام پروژه‌ها"""
        rows = self.conn.execute(
            "SELECT id, name, well_name, field_name, operator, "
            "well_type, status, created_date, modified_date "
            "FROM projects ORDER BY modified_date DESC"
        ).fetchall()

        return [{
            'id': r['id'],
            'name': r['name'],
            'well_name': r['well_name'],
            'field_name': r['field_name'],
            'operator': r['operator'],
            'well_type': r['well_type'],
            'status': r['status'],
            'created': r['created_date'],
            'modified': r['modified_date'],
        } for r in rows]

    def delete_project(self, project_id: int):
        self.conn.execute(
            "DELETE FROM projects WHERE id=?", (project_id,))
        self.conn.commit()

    def rename_project(self, project_id: int, new_name: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "UPDATE projects SET name=?, modified_date=? WHERE id=?",
            (new_name, now, project_id))
        self._add_history(project_id, "Renamed", f"Renamed to: {new_name}")
        self.conn.commit()

    def update_status(self, project_id: int, status: str):
        self.conn.execute(
            "UPDATE projects SET status=? WHERE id=?",
            (status, project_id))
        self.conn.commit()

    def update_notes(self, project_id: int, notes: str):
        self.conn.execute(
            "UPDATE projects SET notes=? WHERE id=?",
            (notes, project_id))
        self.conn.commit()

    # ================================================================
    # HISTORY
    # ================================================================

    def _add_history(self, project_id: int, action: str, details: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "INSERT INTO project_history "
            "(project_id, action, timestamp, details) "
            "VALUES (?, ?, ?, ?)",
            (project_id, action, now, details))

    def get_history(self, project_id: int) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT * FROM project_history WHERE project_id=? "
            "ORDER BY timestamp DESC LIMIT 50",
            (project_id,)).fetchall()
        return [{'action': r['action'],
                 'timestamp': r['timestamp'],
                 'details': r['details']} for r in rows]

    # ================================================================
    # REVISION SNAPSHOTS (audit buyer Q4 — rebuild a previous version)
    # ================================================================

    MAX_SNAPSHOTS = 50

    def _snapshot(self, project_id: int, project_json: str,
                  note: str = "Saved"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last = self.conn.execute(
            "SELECT COALESCE(MAX(revision), 0) AS m FROM project_snapshots "
            "WHERE project_id=?", (project_id,)).fetchone()
        revision = (last['m'] if last else 0) + 1
        self.conn.execute(
            "INSERT INTO project_snapshots "
            "(project_id, revision, snapshot_json, created_date, note) "
            "VALUES (?, ?, ?, ?, ?)",
            (project_id, revision, project_json, now, note))
        # keep only the most recent MAX_SNAPSHOTS revisions
        self.conn.execute(
            "DELETE FROM project_snapshots WHERE project_id=? AND id NOT IN "
            "(SELECT id FROM project_snapshots WHERE project_id=? "
            " ORDER BY revision DESC LIMIT ?)",
            (project_id, project_id, self.MAX_SNAPSHOTS))
        self.conn.commit()

    def list_revisions(self, project_id: int) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT id, revision, created_date, note FROM project_snapshots "
            "WHERE project_id=? ORDER BY revision DESC",
            (project_id,)).fetchall()
        return [{'id': r['id'], 'revision': r['revision'],
                 'created_date': r['created_date'], 'note': r['note']}
                for r in rows]

    def restore_revision(self, project_id: int, revision: int) -> bool:
        """Restore project_data from a previous revision snapshot."""
        row = self.conn.execute(
            "SELECT snapshot_json FROM project_snapshots "
            "WHERE project_id=? AND revision=?",
            (project_id, revision)).fetchone()
        if not row:
            return False
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.conn.execute(
            "UPDATE projects SET project_data=?, modified_date=? "
            "WHERE id=?",
            (row['snapshot_json'], now, project_id))
        self._add_history(project_id, "Restored",
                          f"Restored revision {revision}")
        self.conn.commit()
        return True

    def get_revision_data(self, project_id: int, revision: int) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT snapshot_json FROM project_snapshots "
            "WHERE project_id=? AND revision=?",
            (project_id, revision)).fetchone()
        if row:
            try:
                return json.loads(row['snapshot_json'])
            except Exception:
                return None
        return None

    # ================================================================
    # SEARCH
    # ================================================================

    def search_projects(self, query: str) -> List[Dict]:
        q = f"%{query}%"
        rows = self.conn.execute(
            "SELECT id, name, well_name, field_name, operator, "
            "well_type, status, created_date, modified_date "
            "FROM projects WHERE "
            "name LIKE ? OR well_name LIKE ? OR "
            "field_name LIKE ? OR operator LIKE ? "
            "ORDER BY modified_date DESC",
            (q, q, q, q)).fetchall()
        return [dict(r) for r in rows]

    # ================================================================
    # EXPORT / IMPORT
    # ================================================================

    def export_project(self, project_id: int, file_path: str):
        proj = self.load_project(project_id)
        if proj:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(proj, f, indent=2, ensure_ascii=False)

    def import_project(self, file_path: str) -> int:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        name = data.get('name', 'Imported Project')
        project_data = data.get('data', data)

        cur = self.conn.execute(
            "INSERT INTO projects "
            "(name, well_name, field_name, operator, well_type, "
            "status, project_data, created_date, modified_date) "
            "VALUES (?, ?, ?, ?, ?, 'Imported', ?, ?, ?)",
            (f"{name} (Imported)",
             data.get('well_name', ''),
             data.get('field_name', ''),
             data.get('operator', ''),
             data.get('well_type', ''),
             json.dumps(project_data, ensure_ascii=False),
             now, now))
        self.conn.commit()
        return cur.lastrowid

    # ================================================================
    # STATS
    # ================================================================

    def get_stats(self) -> Dict:
        total = self.conn.execute(
            "SELECT COUNT(*) as cnt FROM projects").fetchone()['cnt']
        return {'total_projects': total}