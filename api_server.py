# ============================================================================
# ENTERPRISE REST API SERVER
# File: api_server.py
# Audit items (P2 / buyer Q14 — "20 engineers at once"):
#   - Local/LAN REST API for the whole desktop engine
#   - API-key authentication (constant-time compare), optional --no-auth
#   - Deterministic document generation through the shared headless pipeline
#   - Read/write endpoints for procedures, problems, CBS, wells, backups
#   - Engineering endpoints: validation, calculation register, anti-collision
#
# Run:   python3 api_server.py --host 0.0.0.0 --port 8000
#        python3 api_server.py --no-auth          (trusted LAN only)
#        python3 launcher.py --server
# Test:  python3 tests/test_api.py
# ============================================================================

import argparse
import base64
import hmac
import json
import os
import secrets
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

APP_DIR = Path.home() / ".drilling_program"
SERVER_CONFIG = APP_DIR / "server_config.json"
VERSION = "3.2"

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_api_key() -> str:
    """Load or generate the server API key (persisted, 0600)."""
    if SERVER_CONFIG.exists():
        try:
            cfg = json.loads(SERVER_CONFIG.read_text(encoding="utf-8"))
            if cfg.get("api_key"):
                return cfg["api_key"]
        except Exception:
            pass
    APP_DIR.mkdir(exist_ok=True)
    key = "drl-" + secrets.token_hex(24)
    SERVER_CONFIG.write_text(json.dumps(
        {"api_key": key, "created": datetime.now().isoformat()},
        indent=1), encoding="utf-8")
    try:
        SERVER_CONFIG.chmod(0o600)
    except Exception:
        pass
    return key


AUTH_ENABLED = True          # set by create_app / main
API_KEY = get_api_key()


def require_key(x_api_key: Optional[str] = Header(default=None)):
    if not AUTH_ENABLED:
        return True
    if not x_api_key or not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401,
                            detail="Invalid or missing X-API-Key header")
    return True


# applied to every endpoint (except /api/health when auth disabled)
AUTH_DEP = [Depends(require_key)]


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    template_key: str
    values: Dict = Field(default_factory=dict)
    operator: str = ""
    contractor: str = ""
    options: Dict = Field(default_factory=dict)


class ValidateRequest(BaseModel):
    values: Dict = Field(default_factory=dict)


class RegisterRequest(BaseModel):
    values: Dict = Field(default_factory=dict)


class AnticollisionRequest(BaseModel):
    ref_trajectory: List[List[float]]
    off_trajectory: Optional[List[List[float]]] = None
    off_surface: Optional[List[float]] = None
    uncertainty_deg: float = 0.25


class ProcedureCreate(BaseModel):
    name: str
    category: str = "General"
    description: str = ""
    tags: str = ""
    steps: List[Dict] = Field(default_factory=list)
    checklist: List[Dict] = Field(default_factory=list)


class ProcedureLink(BaseModel):
    well_id: str = ""
    section: str = ""
    risk_ids: List[int] = Field(default_factory=list)


class BackupRequest(BaseModel):
    password: Optional[str] = None
    tag: str = ""


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app(auth_enabled: bool = True) -> FastAPI:
    global AUTH_ENABLED
    AUTH_ENABLED = auth_enabled
    app = FastAPI(
        title="Drilling Program & Procedure Generator — API",
        version=VERSION,
        description="Enterprise REST API for program/procedure generation, "
                    "engineering checks and knowledge databases.",
    )
    app.add_middleware(
        CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
        allow_headers=["*"])

    # ---------------- system ----------------
    @app.get("/api/health", dependencies=AUTH_DEP)
    def health():
        counts = {}

        def _db_count(fname, table):
            import sqlite3
            try:
                con = sqlite3.connect(str(APP_DIR / fname))
                n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                con.close()
                return n
            except Exception:
                return -1

        try:
            from procedures_db import ProcedureDatabase
            pdb = ProcedureDatabase()
            counts["procedures"] = pdb.get_stats()["total_procedures"]
            pdb.close()
        except Exception:
            counts["procedures"] = -1
        counts["cbs"] = _db_count("cbs.db", "cbs_items")
        counts["problems"] = _db_count("problems.db", "problems")
        counts["catalog"] = _db_count("catalog.db", "docs")
        return {"status": "ok", "version": VERSION,
                "server_time": datetime.now().isoformat(),
                "auth_enabled": AUTH_ENABLED, "databases": counts}

    # ---------------- templates & generation ----------------
    @app.get("/api/templates", dependencies=AUTH_DEP)
    def templates():
        from generation_pipeline import all_templates
        out = []
        for t in all_templates():
            out.append({
                "key": t.key, "name": t.name, "kind": t.kind,
                "icon": t.icon, "description": t.description,
                "inputs": [{"key": s.key, "label": s.label,
                            "type": s.type, "unit": s.unit,
                            "required": s.required, "group": s.group,
                            "options": s.options, "columns": s.columns}
                           for s in t.inputs],
            })
        return {"count": len(out), "templates": out}

    @app.post("/api/generate", dependencies=AUTH_DEP)
    def generate(req: GenerateRequest):
        from generation_pipeline import template_by_key, generate_document
        tdef = template_by_key(req.template_key)
        if tdef is None:
            raise HTTPException(status_code=404,
                                detail=f"template not found: "
                                       f"{req.template_key}")
        values = dict(req.values)
        values.setdefault("operator", req.operator)
        values.setdefault("contractor", req.contractor)
        out_dir = APP_DIR / "exports"
        out_dir.mkdir(parents=True, exist_ok=True)
        fname = (tdef.key + "_" +
                 datetime.now().strftime("%Y%m%d_%H%M%S") + ".docx")
        out_path = str(out_dir / fname)
        meta = {"title": tdef.name, "operator": req.operator,
                "contractor": req.contractor,
                "date": datetime.now().strftime("%d-%B-%Y"),
                "revision": "01", "document_number": ""}
        options = dict(req.options) or {}
        options.setdefault("font", "Calibri")
        options.setdefault("font_size", 11.0)
        options.setdefault("page", "A4")
        report = generate_document(tdef, values, meta, options, out_path)
        if not report["ok"]:
            raise HTTPException(status_code=500, detail="generation failed")
        b64 = base64.b64encode(Path(out_path).read_bytes()).decode()
        return {"report": report, "docx_base64": b64,
                "docx_filename": fname, "docx_size": len(b64)}

    # ---------------- engineering ----------------
    @app.post("/api/validate", dependencies=AUTH_DEP)
    def validate(req: ValidateRequest):
        from validation_engine import validate_well_data
        findings = validate_well_data(req.values)
        return {"findings": [{"level": f.level, "code": f.code,
                              "message": f.message,
                              "blocking": f.is_blocking}
                             for f in findings],
                "critical": sum(1 for f in findings if f.is_blocking)}

    @app.post("/api/register", dependencies=AUTH_DEP)
    def register(req: RegisterRequest):
        from engineering_register import compute_register
        rows = compute_register(req.values)
        return {"rows": rows, "count": len(rows)}

    @app.post("/api/hydraulics", dependencies=AUTH_DEP)
    def hydraulics(req: RegisterRequest):
        from engineering_hydraulics import standpipe_pressure
        return standpipe_pressure(req.values)

    @app.post("/api/wellcontrol", dependencies=AUTH_DEP)
    def wellcontrol(req: RegisterRequest):
        from engineering_wellcontrol import kick_scenario
        from engineering_register import _f
        v = req.values
        out = {"scenario": kick_scenario(v)}
        mw = _f(v.get("mud_weight") or v.get("mud_weight_ppg"))
        sidpp = _f(v.get("sidpp") or v.get("sidpip"))
        tvd = _f(v.get("depth") or v.get("td_depth") or
                 v.get("total_depth"))
        if mw > 0 and sidpp > 0 and tvd > 0:
            from engineering_wellcontrol import kill_mud_weight
            out["kill_mud_weight_ppg"] = round(
                kill_mud_weight(mw, sidpp, tvd), 2)
        return out

    @app.post("/api/geomechanics", dependencies=AUTH_DEP)
    def geomechanics(req: RegisterRequest):
        from engineering_geomechanics import safe_mud_window
        from engineering_register import _f
        v = req.values
        tvd = _f(v.get("depth") or v.get("td_depth") or
                 v.get("total_depth"))
        ucs = _f(v.get("ucs_psi") or v.get("rock_ucs"))
        if tvd <= 0 or ucs <= 0:
            return {"error": "depth and ucs_psi required"}
        sv_grad = _f(v.get("sigma_v_grad"), 1.0)
        sH_r = _f(v.get("sH_sv_ratio"), 0.95)
        sh_r = _f(v.get("sh_sv_ratio"), 0.85)
        pp = _f(v.get("formation_pressure") or v.get("pore_pressure"))
        pp_psi = pp * 0.052 * tvd if 0 < pp <= 5 else pp
        win = safe_mud_window(sv_grad * tvd, sv_grad * tvd * sH_r,
                              sv_grad * tvd * sh_r, pp_psi, ucs,
                              _f(v.get("friction_angle"), 30.0),
                              _f(v.get("tensile_strength")))
        win["tvd_ft"] = tvd
        return win

    @app.post("/api/anticollision", dependencies=AUTH_DEP)
    def anticollision(req: AnticollisionRequest):
        from engineering_anticollision import (min_curvature_positions,
                                               anti_collision_review)
        ref = [(r[0], r[1], r[2]) for r in req.ref_trajectory
               if len(r) >= 3]
        off = None
        if req.off_trajectory:
            off = [(r[0], r[1], r[2]) for r in req.off_trajectory
                   if len(r) >= 3]
        surf = (req.off_surface or [0, 0])
        rev = anti_collision_review(ref, off,
                                    unc_angle_deg=req.uncertainty_deg,
                                    off_surface=(surf[0], surf[1] if
                                                 len(surf) > 1 else 0))
        rev.pop("ref_pos", None)
        rev.pop("off_pos", None)
        return rev

    # ---------------- procedures ----------------
    @app.get("/api/procedures", dependencies=AUTH_DEP)
    def procedures(search: str = Query("", max_length=100)):
        from procedures_db import ProcedureDatabase
        db = ProcedureDatabase()
        try:
            rows = db.search_procedures(search) if search else \
                [{"id": p.id, "name": p.name,
                  "category": p.category_name,
                  "description": p.description, "version": p.version,
                  "builtin": p.is_builtin,
                  "well": p.linked_well_id, "section": p.linked_section}
                 for p in db.get_all_procedures(active_only=True)]
            return {"count": len(rows), "procedures": rows}
        finally:
            db.close()

    @app.get("/api/procedures/{pid}", dependencies=AUTH_DEP)
    def procedure(pid: int):
        from procedures_db import ProcedureDatabase
        db = ProcedureDatabase()
        try:
            rec = db.get_procedure(pid)
            if not rec:
                raise HTTPException(status_code=404,
                                    detail="procedure not found")
            return {
                "id": rec.id, "name": rec.name,
                "category": rec.category_name,
                "description": rec.description, "version": rec.version,
                "status": db.get_lifecycle(pid).get("status", ""),
                "well": rec.linked_well_id, "section": rec.linked_section,
                "risk_ids": json.loads(rec.linked_risk_ids or "[]"),
                "steps": [{"number": s.step_number, "text": s.text,
                           "indent": s.indent_level, "header": s.is_header,
                           "note": s.is_note, "warning": s.is_warning,
                           "precondition": s.precondition,
                           "acceptance": s.acceptance,
                           "hold_point": s.hold_point,
                           "witness_point": s.witness_point,
                           "role": s.role} for s in rec.steps],
                "checklist": [{"number": c.item_number, "text": c.text,
                               "category": c.category}
                              for c in rec.checklist],
            }
        finally:
            db.close()

    @app.post("/api/procedures", dependencies=AUTH_DEP)
    def create_procedure(req: ProcedureCreate):
        from procedures_db import ProcedureDatabase
        db = ProcedureDatabase()
        try:
            cat = db.get_category_id(req.category)
            if not cat:
                cat = db.add_category(req.category)
            pid = db.add_procedure(name=req.name, category_id=cat,
                                   description=req.description,
                                   tags=req.tags)
            db.replace_all_steps(pid, req.steps)
            db.replace_all_checklist(pid, req.checklist)
            return {"id": pid, "name": req.name, "status": "created"}
        finally:
            db.close()

    @app.post("/api/procedures/{pid}/link", dependencies=AUTH_DEP)
    def link_procedure(pid: int, req: ProcedureLink):
        from procedures_db import ProcedureDatabase
        db = ProcedureDatabase()
        try:
            db.link_well(pid, req.well_id, req.section)
            db.link_risks(pid, req.risk_ids)
            return {"id": pid, "ok": True,
                    "links": db.get_links(pid)}
        finally:
            db.close()

    # ---------------- knowledge ----------------
    @app.get("/api/problems", dependencies=AUTH_DEP)
    def problems():
        from drilling_problems_db import ProblemDatabase
        db = ProblemDatabase()
        try:
            probs = db.all()
            return {"count": len(probs),
                    "problems": [{"code": p.code, "name": p.name,
                                  "category": p.category,
                                  "severity": p.severity,
                                  "symptoms": p.symptoms,
                                  "causes": p.causes}
                                 for p in probs]}
        finally:
            db.close()

    @app.get("/api/cbs", dependencies=AUTH_DEP)
    def cbs():
        from cbs_db import CBSDatabase
        db = CBSDatabase()
        try:
            items = db.get_items()
            return {"count": len(items),
                    "items": [{"code": i.code, "name": i.name, "unit": i.unit,
                               "unit_price": i.unit_price,
                               "category": getattr(i, "category", ""),
                               "source": getattr(i, "source", "")}
                              for i in items]}
        finally:
            db.close()

    @app.get("/api/wells", dependencies=AUTH_DEP)
    def wells():
        from well_model import WellDatabase
        db = WellDatabase()
        try:
            return {"count": len(db.list_wells()),
                    "wells": db.list_wells()}
        finally:
            db.close()

    # ---------------- backups ----------------
    @app.get("/api/backups", dependencies=AUTH_DEP)
    def backups():
        from backup_restore import list_backups
        return {"backups": list_backups()}

    @app.post("/api/backup", dependencies=AUTH_DEP)
    def create_backup(req: BackupRequest):
        from backup_restore import create_backup as cb
        b = cb(tag=req.tag, password=req.password)
        if not b:
            raise HTTPException(status_code=500, detail="no data to back up")
        return {"name": b.name, "encrypted": b.suffix == ".enc",
                "path": str(b)}

    # ---------------- reports ----------------
    @app.get("/api/report")
    def report(report_type: str = Query("all", max_length=30)):
        import reporting
        data = {}
        if report_type in ("all", "procedures"):
            data["procedures"] = reporting.procedures_report()
        if report_type in ("all", "problems"):
            data["problems"] = reporting.problems_report()
        if report_type in ("all", "cbs"):
            data["cbs"] = reporting.cbs_report()
        if report_type in ("all", "catalog"):
            data["catalog"] = reporting.catalog_report()
        if report_type in ("all", "operations"):
            data["operations"] = reporting.operations_report()
        if report_type in ("all", "governance"):
            data["governance"] = reporting.catalog_governance()
        data["markdown"] = reporting.report_markdown(report_type)
        return data

    @app.post("/api/witsml")
    def witsml_export(req: RegisterRequest):
        from witsml_export import build_witsml, build_json
        return {"xml": build_witsml(req.values),
                "json": build_json(req.values)}

    @app.post("/api/sensitivity")
    def sensitivity(req: RegisterRequest):
        from engineering_sensitivity import sensitivity_analysis
        return sensitivity_analysis(req.values)

    @app.get("/api/system/ocr")
    def ocr_status():
        import ocr_ingest
        err = ocr_ingest.check_tesseract()
        return {"available": not bool(err), "error": err}

    @app.get("/api/system/pdf")
    def pdf_status():
        import pdf_export
        err = pdf_export.check_libreoffice()
        return {"available": not bool(err), "error": err}

    @app.get("/api/report/excel")
    def report_excel():
        import shutil
        import tempfile
        import reporting
        tmp = tempfile.mkdtemp(prefix="drl_rep_")
        path = os.path.join(tmp, "report.xlsx")
        reporting.export_report_excel(path, "all")
        data = Path(path).read_bytes()
        shutil.rmtree(tmp, ignore_errors=True)
        return {"xlsx_base64": base64.b64encode(data).decode(),
                "size": len(data)}

    # ---------------- stats ----------------
    @app.get("/api/stats", dependencies=AUTH_DEP)
    def stats():
        out = {}
        try:
            from procedures_db import ProcedureDatabase
            db = ProcedureDatabase()
            out["procedures"] = db.get_stats()
            db.close()
        except Exception:
            pass
        try:
            from cbs_db import CBSDatabase
            db = CBSDatabase()
            items = db.get_items()
            out["cbs_items"] = len(items)
            out["cbs_total"] = sum(i.unit_price for i in items)
            db.close()
        except Exception:
            pass
        try:
            from drilling_problems_db import ProblemDatabase
            db = ProblemDatabase()
            probs = db.all()
            out["problems"] = len(probs)
            out["problems_critical"] = sum(
                1 for p in probs if p.severity in ("Critical", "High"))
            db.close()
        except Exception:
            pass
        import sqlite3
        try:
            con = sqlite3.connect(str(APP_DIR / "catalog.db"))
            out["catalog_docs"] = con.execute(
                "SELECT COUNT(*) FROM docs").fetchone()[0]
            con.close()
        except Exception:
            pass
        return out

    return app


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(prog="api_server",
                                 description="Drilling Program REST API")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-auth", action="store_true",
                    help="disable API-key auth (trusted LAN only)")
    ap.add_argument("--key", default=None,
                    help="explicit API key (else auto-generated & saved)")
    args = ap.parse_args()

    global API_KEY, AUTH_ENABLED
    if args.key:
        API_KEY = args.key
    AUTH_ENABLED = not args.no_auth

    app = create_app(auth_enabled=AUTH_ENABLED)
    import uvicorn
    print("=" * 64)
    print("DRILLING PROGRAM GENERATOR — ENTERPRISE API")
    print(f"  http://{args.host}:{args.port}/api/health")
    print(f"  Auth: {'API key (X-API-Key)' if AUTH_ENABLED else 'DISABLED'}")
    if AUTH_ENABLED:
        print(f"  API key: {API_KEY}")
    print("=" * 64)
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    sys.exit(main())
