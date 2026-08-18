# ============================================================================
# CROSS-WELL INTELLIGENCE
# File: well_intelligence.py
# Phase AF — now that every generated document persists its well basis in
# wells.db (Phase AE), the application can learn across wells:
#   - similar_wells(): rank stored wells by engineering similarity
#   - lessons_for(): pull lessons learned / NPT for matching wells
#   - suggest_inputs(): prefill a new well from the most similar offset
#   - comparison_markdown(): side-by-side well comparison section
#   - well_database_report(): statistics over the stored well population
# Deterministic, reference-tested.
# ============================================================================

import math
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

APP_DIR = Path.home() / ".drilling_program"
WELL_DB = APP_DIR / "wells.db"
OPS_DB = APP_DIR / "operations.db"


def _f(v, d=0.0) -> float:
    try:
        s = str(v).strip()
        return float(s) if s else d
    except (TypeError, ValueError):
        return d


def _db(fname: str) -> Optional[sqlite3.Connection]:
    p = APP_DIR / fname
    if not p.exists():
        return None
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    return con


def _well_profile(well_id: str) -> Optional[Dict]:
    con = _db("wells.db")
    if con is None:
        return None
    try:
        wrow = con.execute("SELECT * FROM wells WHERE well_id=?",
                           (well_id,)).fetchone()
        if not wrow:
            return None
        rev = con.execute(
            "SELECT * FROM revisions WHERE well_id=? "
            "ORDER BY revision_id DESC LIMIT 1", (well_id,)).fetchone()
        sec = None
        if rev:
            sec = con.execute(
                "SELECT * FROM sections WHERE revision_id=? "
                "ORDER BY depth_to_m DESC LIMIT 1",
                (rev["revision_id"],)).fetchone()
        return {"well_id": wrow["well_id"], "well_name": wrow["well_name"],
                "field_name": wrow["field_name"] or "",
                "operator": wrow["operator"] or "",
                "well_type": wrow["well_type"] or "",
                "environment": wrow["environment"] or "",
                "depth_to_m": _f(sec["depth_to_m"]) if sec else 0.0,
                "hole_size_in": _f(sec["hole_size_in"]) if sec else 0.0,
                "casing_size_in": _f(sec["casing_size_in"]) if sec else 0.0,
                "mud_weight_ppg": _f(sec["mud_weight_ppg"]) if sec else 0.0,
                "mud_type": (sec["mud_type"] or "") if sec else "",
                "n_revisions": _f(rev["revision_id"]) if rev else 1}
    finally:
        con.close()


def all_well_profiles() -> List[Dict]:
    con = _db("wells.db")
    if con is None:
        return []
    try:
        ids = [r["well_id"] for r in
               con.execute("SELECT well_id FROM wells").fetchall()]
    finally:
        con.close()
    return [p for p in (_well_profile(i) for i in ids) if p]


def _similarity(a: Dict, b: Dict) -> float:
    """0..1 similarity between two well profiles."""
    score = 0.0
    weights = 0.0
    a_d = _f(a.get("depth_to_m") or a.get("depth_m"))
    b_d = _f(b.get("depth_to_m") or b.get("depth_m"))
    a_h = _f(a.get("hole_size_in") or a.get("hole_size"))
    b_h = _f(b.get("hole_size_in") or b.get("hole_size"))
    a_m = _f(a.get("mud_weight_ppg") or a.get("mud_weight"))
    b_m = _f(b.get("mud_weight_ppg") or b.get("mud_weight"))
    if a_d and b_d:
        ratio = min(a_d, b_d) / max(a_d, b_d)
        score += ratio * 3
        weights += 3
    if a_h and b_h:
        ratio = min(a_h, b_h) / max(a_h, b_h)
        score += ratio * 2
        weights += 2
    if a_m and b_m:
        ratio = min(a_m, b_m) / max(a_m, b_m)
        score += ratio * 2
        weights += 2
    if a.get("well_type") and a.get("well_type") == b.get("well_type"):
        score += 1.5
        weights += 1.5
    if a.get("field_name") and str(a.get("field_name")).lower() == \
            str(b.get("field_name") or "").lower():
        score += 1.0
        weights += 1.0
    if a.get("mud_type") and str(a.get("mud_type")).lower() == \
            str(b.get("mud_type") or "").lower():
        score += 0.5
        weights += 0.5
    return score / weights if weights else 0.0


def similar_wells(target: Dict, top_n: int = 5) -> List[Dict]:
    """Rank stored wells by similarity to the target profile."""
    profiles = all_well_profiles()
    out = []
    for p in profiles:
        if target.get("well_name") and \
                p["well_name"].lower() == str(target["well_name"]).lower():
            continue  # skip itself
        sim = _similarity(target, p)
        if sim > 0:
            out.append({"well_name": p["well_name"],
                        "well_id": p["well_id"],
                        "field_name": p["field_name"],
                        "well_type": p["well_type"],
                        "depth_to_m": p["depth_to_m"],
                        "mud_weight_ppg": p["mud_weight_ppg"],
                        "similarity": round(sim, 2)})
    out.sort(key=lambda x: x["similarity"], reverse=True)
    return out[:top_n]


def lessons_for(well_name: str = "", field: str = "", operation: str = "",
                limit: int = 10) -> List[Dict]:
    """Lessons learned / NPT for matching wells from operations.db."""
    con = _db("operations.db")
    if con is None:
        return []
    try:
        q = ("SELECT * FROM lessons WHERE 1=1")
        params: list = []
        if well_name:
            q += " AND (well_name LIKE ? OR well_id LIKE ?)"
            params += [f"%{well_name}%", f"%{well_name}%"]
        if field:
            q += " AND (field_name LIKE ?)"
            params.append(f"%{field}%")
        if operation:
            q += " AND (operation LIKE ?)"
            params.append(f"%{operation}%")
        q += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        rows = con.execute(q, params).fetchall()
        return [{"lesson": r["lesson"] if "lesson" in r.keys() else
                 r["details"] if "details" in r.keys() else "",
                 "operation": r["operation"] if "operation" in r.keys()
                 else "",
                 "category": r["category"] if "category" in r.keys()
                 else ""} for r in rows]
    finally:
        con.close()


def suggest_inputs(target: Dict) -> Dict:
    """Prefill a new well from the most similar stored offset well.

    Returns {offset_well, suggestions: {key: value}}."""
    sims = similar_wells(target, top_n=1)
    if not sims:
        return {"offset_well": "", "suggestions": {}}
    off = _well_profile(sims[0]["well_id"])
    if not off:
        return {"offset_well": "", "suggestions": {}}
    sugg = {}
    if off["mud_weight_ppg"] and not _f(target.get("mud_weight")):
        sugg["mud_weight"] = str(off["mud_weight_ppg"])
    if off["hole_size_in"] and not _f(target.get("hole_size")):
        sugg["hole_size"] = str(off["hole_size_in"])
    if off["casing_size_in"] and not _f(target.get("casing_size")):
        sugg["casing_size"] = str(off["casing_size_in"])
    if off["mud_type"] and not str(target.get("mud_type") or "").strip():
        sugg["mud_type"] = off["mud_type"]
    if off["depth_to_m"] and not _f(target.get("depth_m")):
        sugg["depth_m"] = str(round(off["depth_to_m"], 0))
    if off["field_name"] and not str(target.get("field_name") or "").strip():
        sugg["field_name"] = off["field_name"]
    return {"offset_well": off["well_name"], "suggestions": sugg}


def comparison_markdown(well_ids: List[str], operator: str = "") -> str:
    """Word-ready side-by-side comparison of stored wells."""
    if len(well_ids) < 2:
        return ""
    profiles = [p for p in (_well_profile(w) for w in well_ids) if p]
    if len(profiles) < 2:
        return ""
    op = (operator or "").strip() or "the Operator"
    L = ["## OFFSET WELL COMPARISON", ""]
    L.append(f"**Wells compared:** {', '.join(p['well_name'] for p in profiles)}")
    L.append("")
    rows = [
        ("Field", lambda p: p["field_name"]),
        ("Well type", lambda p: p["well_type"]),
        ("Environment", lambda p: p["environment"]),
        ("Depth (m)", lambda p: f"{p['depth_to_m']:,.0f}" if
         p["depth_to_m"] else "—"),
        ("Hole size (in)", lambda p: f"{p['hole_size_in']:g}" if
         p["hole_size_in"] else "—"),
        ("Casing (in)", lambda p: f"{p['casing_size_in']:g}" if
         p["casing_size_in"] else "—"),
        ("Mud weight (ppg)", lambda p: f"{p['mud_weight_ppg']:g}" if
         p["mud_weight_ppg"] else "—"),
        ("Mud type", lambda p: p["mud_type"] or "—"),
        ("Revisions", lambda p: str(p["n_revisions"])),
    ]
    L.append("| Parameter | " + " | ".join(
        p["well_name"][:22] for p in profiles) + " |")
    L.append("|---" * (len(profiles) + 1) + "|")
    for label, fn in rows:
        L.append(f"| {label} | " +
                 " | ".join(fn(p) for p in profiles) + " |")
    L.append("")
    L.append(f"*Well comparison computed for {op} from the local well "
             "database (wells.db); use the closest offsets for "
             "programming and lessons review.*")
    return "\n".join(L)


def well_database_report() -> Dict:
    """Statistics over the stored well population."""
    profiles = all_well_profiles()
    out = {"wells": len(profiles)}
    out["by_type"] = {}
    out["by_field"] = {}
    depths = [p["depth_to_m"] for p in profiles if p["depth_to_m"]]
    out["avg_depth_m"] = round(sum(depths) / len(depths), 0) if depths else 0
    out["max_depth_m"] = max(depths) if depths else 0
    out["total_revisions"] = sum(p["n_revisions"] for p in profiles)
    for p in profiles:
        t = p["well_type"] or "unknown"
        out["by_type"][t] = out["by_type"].get(t, 0) + 1
        f = p["field_name"] or "unknown"
        out["by_field"][f] = out["by_field"].get(f, 0) + 1
    return out


def well_report_markdown(operator: str = "") -> str:
    """Word-ready WELL DATABASE REPORT section."""
    st = well_database_report()
    op = (operator or "").strip() or "the Operator"
    L = ["## WELL DATABASE REPORT", ""]
    L.append(f"**{st['wells']} stored wells** — "
             f"{st['total_revisions']} revisions total, "
             f"avg depth {st['avg_depth_m']:,.0f} m, "
             f"max {st['max_depth_m']:,.0f} m.")
    L.append("")
    L.append("| By well type | Count |")
    L.append("|---|---|")
    for k, v in sorted(st["by_type"].items(), key=lambda x: -x[1]):
        L.append(f"| {k} | {v} |")
    L.append("")
    if st["by_field"]:
        L.append("| By field | Count |")
        L.append("|---|---|")
        for k, v in sorted(st["by_field"].items(), key=lambda x: -x[1]):
            L.append(f"| {k} | {v} |")
        L.append("")
    L.append(f"*Well database report generated for {op} — the basis for "
             "offset-well intelligence and lesson reuse.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    from well_model import WellDatabase, well_from_values
    db = WellDatabase()
    # seed two comparable wells
    w1 = well_from_values("", {"well_name": "SIM-WELL-1", "field_name": "F1",
                               "well_type": "Development",
                               "mud_weight": "12", "td_depth": "10000",
                               "hole_size": "12.25", "casing_size": "9.625",
                               "mud_type": "OBM"})
    w2 = well_from_values("", {"well_name": "SIM-WELL-2", "field_name": "F1",
                               "well_type": "Development",
                               "mud_weight": "12.5", "td_depth": "10100",
                               "hole_size": "12.25", "casing_size": "9.625",
                               "mud_type": "OBM"})
    w3 = well_from_values("", {"well_name": "SIM-WELL-3", "field_name": "F9",
                               "well_type": "Exploration",
                               "mud_weight": "9", "td_depth": "3000",
                               "hole_size": "17.5", "casing_size": "13.375",
                               "mud_type": "WBM"})
    db.save_well(w1)
    db.save_well(w2)
    db.save_well(w3)
    db.close()
    # similarity: SIM-WELL-2 (similar) ranks above SIM-WELL-3 (dissimilar)
    sims = similar_wells({"well_name": "SIM-WELL-1", "well_type":
                          "Development", "mud_weight": "12",
                          "hole_size": "12.25", "depth_m": "3050"},
                         top_n=10)
    names = [s["well_name"] for s in sims]
    assert "SIM-WELL-2" in names, names
    assert names.index("SIM-WELL-2") < names.index("SIM-WELL-3"), names
    # suggestion from the most similar well
    s = suggest_inputs({"well_name": "NEW-WELL", "well_type": "Development"})
    assert s["offset_well"] in ("SIM-WELL-1", "SIM-WELL-2"), s
    assert _f(s["suggestions"].get("mud_weight")) in (12.0, 12.5), s
    # comparison
    md = comparison_markdown([w1.well_id, w2.well_id])
    assert "OFFSET WELL COMPARISON" in md
    assert "SIM-WELL-1" in md and "SIM-WELL-2" in md
    # report
    rep = well_database_report()
    assert rep["wells"] >= 3, rep
    rmd = well_report_markdown()
    assert "WELL DATABASE REPORT" in rmd
    # cleanup
    db = WellDatabase()
    for n in ("SIM-WELL-1", "SIM-WELL-2", "SIM-WELL-3"):
        for w in db.list_wells():
            if w.get("well_name") == n:
                db.delete_well(w["well_id"])
    db.close()
    print("  ✔ well intelligence selftest: similarity + suggestion + "
          "comparison OK")
    return sims


if __name__ == "__main__":
    _selftest()
    print("well_intelligence OK")
