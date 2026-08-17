# ============================================================================
# REST API TEST SUITE
# File: tests/test_api.py
# Audit items (P2 / buyer Q14): the enterprise API layer.
#
# Starts the FastAPI app in-process (TestClient), exercises auth, template
# listing, document generation (real docx with governance sections),
# validation, register, anti-collision, procedure CRUD/linking, problems,
# CBS, wells, backups and stats.
#
# Run:  LD_LIBRARY_PATH=/tmp/glstubs PYTHONPATH=. QT_QPA_PLATFORM=offscreen \
#       python3 tests/test_api.py
# Exit code 0 = all pass.
# ============================================================================

import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from api_server import create_app, get_api_key

_PASS = 0
_FAIL = 0


def ok(cond, label, extra=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ✔ {label}")
    else:
        _FAIL += 1
        print(f"  ✘ {label} {extra}")


def _gen_values():
    from tests.regression_templates import generic_values
    return generic_values()


def main():
    app = create_app(auth_enabled=True)
    client = TestClient(app)
    key = get_api_key()
    H = {"X-API-Key": key}
    badH = {"X-API-Key": "wrong-key"}

    print("\n[1] AUTH")
    r = client.get("/api/health")
    ok(r.status_code == 401, "no key -> 401")
    r = client.get("/api/health", headers=badH)
    ok(r.status_code == 401, "wrong key -> 401")
    r = client.get("/api/health", headers=H)
    ok(r.status_code == 200 and r.json()["status"] == "ok",
       "correct key -> 200")
    ok(r.json()["auth_enabled"] is True, "auth flag reported")

    print("\n[2] TEMPLATES")
    r = client.get("/api/templates", headers=H)
    ok(r.status_code == 200, "templates 200")
    tpl = r.json()["templates"]
    ok(r.json()["count"] == 51, f"51 templates (got {r.json()['count']})")
    keys = {t["key"] for t in tpl}
    ok("drilling_program" in keys and "master_well_control" in keys,
       "program + master templates present")

    print("\n[3] GENERATE — real Word document via API")
    payload = {"template_key": "drilling_program",
               "values": _gen_values(),
               "operator": "the Operator",
               "contractor": "the Service Company"}
    r = client.post("/api/generate", json=payload, headers=H)
    ok(r.status_code == 200, "generate 200")
    data = r.json()
    rep = data["report"]
    ok(rep["ok"] is True, "report ok")
    for sec in ("VALIDATION & COMPLIANCE", "PROGRAM READINESS SCORE",
                "STANDARDS COMPLIANCE MATRIX", "DOCUMENT COMPLIANCE REPORT",
                "ENGINEERING CALCULATION REGISTER",
                "DEEP ENGINEERING VERIFICATION"):
        ok(any(sec in s for s in rep["sections"]), f"section: {sec}")
    ok(rep["register_rows"] > 0, f"register rows > 0 "
       f"(got {rep['register_rows']})")
    # docx bytes are valid
    docx_bytes = base64.b64decode(data["docx_base64"])
    ok(docx_bytes[:2] == b"PK", "docx is a valid zip (PK header)")
    tmp = os.path.join("/tmp", "api_gen_test.docx")
    with open(tmp, "wb") as f:
        f.write(docx_bytes)
    from docx import Document
    d = Document(tmp)
    text = "\n".join(p.text for p in d.paragraphs).upper()
    ok("VALIDATION & COMPLIANCE" in text and "PROGRAM READINESS" in text,
       "docx contains governance sections")
    # unknown template -> 404
    r = client.post("/api/generate",
                    json={"template_key": "nope", "values": {}},
                    headers=H)
    ok(r.status_code == 404, "unknown template -> 404")

    print("\n[4] ENGINEERING ENDPOINTS")
    r = client.post("/api/validate",
                    json={"values": {"mud_weight": "12", "td_depth": "10000"}},
                    headers=H)
    ok(r.status_code == 200 and "findings" in r.json(), "validate 200")
    r = client.post("/api/register", json={"values": _gen_values()},
                    headers=H)
    ok(r.status_code == 200 and r.json()["count"] > 0,
       f"register rows: {r.json()['count']}")
    r = client.post("/api/anticollision",
                    json={"ref_trajectory": [[0, 0, 90], [1000, 15, 90],
                                             [2000, 30, 90]],
                          "off_trajectory": [[0, 0, 90], [1000, 15, 90],
                                             [2000, 30, 90]]},
                    headers=H)
    ok(r.status_code == 200 and r.json()["status"] == "FAIL",
       "anticollision identical wells -> FAIL")

    print("\n[5] PROCEDURES CRUD + LINKING")
    r = client.post("/api/procedures",
                    json={"name": "API Test Procedure",
                          "category": "API Tests",
                          "steps": [{"text": "Run casing", "hold_point": True,
                                     "role": "Toolpusher"},
                                    {"text": "Circulate"}],
                          "checklist": [{"text": "Verify returns",
                                         "category": "General"}]},
                    headers=H)
    ok(r.status_code == 200, "create procedure 200")
    pid = r.json()["id"]
    r = client.get(f"/api/procedures/{pid}", headers=H)
    ok(r.status_code == 200, "get procedure 200")
    rec = r.json()
    ok(len(rec["steps"]) == 2, "steps round-trip")
    ok(rec["steps"][0]["hold_point"] is True, "hold point round-trip")
    ok(rec["steps"][0]["role"] == "Toolpusher", "role round-trip")
    ok(len(rec["checklist"]) == 1, "checklist round-trip")
    r = client.post(f"/api/procedures/{pid}/link",
                    json={"well_id": "W-API-1", "section": "12.25 in",
                          "risk_ids": [1, 2]},
                    headers=H)
    ok(r.status_code == 200 and r.json()["ok"], "link 200")
    ok(r.json()["links"]["well_id"] == "W-API-1", "well link persisted")
    ok(r.json()["links"]["risk_ids"] == [1, 2], "risk links persisted")
    r = client.get("/api/procedures", headers=H)
    ok(r.status_code == 200 and r.json()["count"] >= 1, "list procedures")
    r = client.get("/api/procedures/999999", headers=H)
    ok(r.status_code == 404, "missing procedure -> 404")

    print("\n[6] KNOWLEDGE + BACKUPS + STATS")
    r = client.get("/api/problems", headers=H)
    ok(r.status_code == 200 and r.json()["count"] >= 20,
       f"problems: {r.json()['count']}")
    r = client.get("/api/cbs", headers=H)
    ok(r.status_code == 200 and r.json()["count"] >= 300,
       f"cbs items: {r.json()['count']}")
    r = client.get("/api/wells", headers=H)
    ok(r.status_code == 200, "wells 200")
    r = client.get("/api/backups", headers=H)
    ok(r.status_code == 200, "backups list 200")
    r = client.post("/api/backup", json={"tag": "api_test"}, headers=H)
    ok(r.status_code == 200 and r.json()["name"], "backup created")
    r = client.get("/api/stats", headers=H)
    ok(r.status_code == 200 and r.json().get("procedures", {}).get(
        "total_procedures", 0) > 0, "stats 200")

    print("\n" + "=" * 60)
    print(f"RESULT: {_PASS} passed, {_FAIL} failed")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
