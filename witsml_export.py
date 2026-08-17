# ============================================================================
# WITSML EXPORT
# File: witsml_export.py
# Roadmap item (P3): Telemetry / WITSML — export the well basis of design
# as WITSML (Wellsite Information Transfer Standard Markup Language) XML
# and as a flat JSON handoff.
#
# Generates a well-formed WITSML v1.4.1-style document containing the
# well, wellbore and trajectory (minimum-curvature stations) objects.
# Deterministic; validates with the stdlib XML parser.
# ============================================================================

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from xml.dom import minidom
from xml.sax.saxutils import escape


def _f(v, d=0.0) -> float:
    try:
        s = str(v).strip()
        return float(s) if s else d
    except (TypeError, ValueError):
        return d


def _pick(values: Dict, *keys) -> str:
    for k in keys:
        s = str(values.get(k, "") or "").strip()
        if s:
            return s
    return ""


def build_witsml(values: Dict, uid_well: str = "well-001") -> str:
    """Build the WITSML XML string from wizard values."""
    v = values or {}
    well_name = escape(_pick(v, "well_name", "wellname") or "WELL")
    field = escape(_pick(v, "field_name", "field") or "")
    operator = escape(_pick(v, "operator", "operator_name") or "")
    country = escape(_pick(v, "country") or "")
    tvd = _f(_pick(v, "depth", "depth_ft", "td_depth", "td_ft",
                   "total_depth"))
    depth_m = _f(_pick(v, "depth_m", "td_m"))
    if tvd <= 0 and depth_m > 0:
        tvd = depth_m * 3.28084
    tvd_m = round(tvd * 0.3048, 1)
    well_type = escape(_pick(v, "well_type", "well_profile") or "")
    water_depth = _f(_pick(v, "water_depth"))
    traj_md = _pick(v, "trajectory_table")

    # ---- trajectory (minimum curvature) ----
    stations_xml = ""
    n_stations = 0
    if traj_md:
        try:
            from engineering_anticollision import (parse_trajectory_markdown,
                                                   min_curvature_positions)
            st = parse_trajectory_markdown(traj_md)
            if len(st) >= 1:
                pos = min_curvature_positions(st)
                for (md, inc, azi), (m, t, n_, e_) in zip(st, pos):
                    stations_xml += (
                        f'      <trajectoryStation uid="st{int(md)}">\n'
                        f"        <md uom=\"ft\">{md:.1f}</md>\n"
                        f"        <inclination uom=\"deg\">{inc:.2f}"
                        f"</inclination>\n"
                        f"        <azimuth uom=\"deg\">{azi:.2f}</azimuth>\n"
                        f"        <tvd uom=\"ft\">{t:.1f}</tvd>\n"
                        f"        <dispNs uom=\"ft\">{n_:.2f}</dispNs>\n"
                        f"        <dispEw uom=\"ft\">{e_:.2f}</dispEw>\n"
                        f"      </trajectoryStation>\n")
                    n_stations += 1
        except Exception:
            stations_xml = ""

    now = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<wells xmlns="http://www.witsml.org/schemas/1series"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       version="1.4.1.1">
  <well uid="{escape(uid_well)}">
    <name>{well_name}</name>
    <field>{field}</field>
    <operator>{operator}</operator>
    <country>{country}</country>
    <wellDatum uid="KB">
      <name>Kelly bushing</name>
      <elevation uom="ft">0.0</elevation>
    </wellDatum>
    <wellLocation>
      <latitude uom="deg">0.0</latitude>
      <longitude uom="deg">0.0</longitude>
    </wellLocation>
    <wellCommonData>
      <dTimSpud>{now}</dTimSpud>
      <waterDepth uom="ft">{water_depth:.1f}</waterDepth>
    </wellCommonData>
    <wellbore uid="wb-1">
      <name>Main wellbore</name>
      <typeWellbore>initial</typeWellbore>
      <wellBoreCommonData>
        <dTimDrillSpud>{now}</dTimDrillSpud>
      </wellBoreCommonData>
      <trajectory uid="traj-1">
        <name>Planned trajectory (minimum curvature)</name>
        <mdMin uom="ft">0.0</mdMin>
        <mdMax uom="ft">{tvd:.1f}</mdMax>
        <tvdMin uom="ft">0.0</tvdMin>
        <tvdMax uom="ft">{tvd:.1f}</tvdMax>
        <aziVertSect uom="deg">0.0</aziVertSect>
{stations_xml}      </trajectory>
    </wellbore>
  </well>
</wells>
"""
    return xml


def build_json(values: Dict) -> Dict:
    """Flat JSON handoff of the well basis."""
    v = values or {}
    return {
        "schema": "drilling-basis-v1",
        "exported": datetime.now().isoformat(),
        "well": {
            "name": _pick(v, "well_name", "wellname"),
            "field": _pick(v, "field_name", "field"),
            "operator": _pick(v, "operator", "operator_name"),
            "well_type": _pick(v, "well_type", "well_profile"),
            "environment": _pick(v, "environment"),
            "rig": _pick(v, "rig_name", "rig"),
            "water_depth_ft": _f(_pick(v, "water_depth")),
        },
        "basis": {k: v[k] for k in (
            "mud_weight", "mud_type", "hole_size", "casing_size",
            "casing_depth", "formation_pressure", "fracture_gradient",
            "bop_wp", "h2s", "total_days", "total_cost")
            if k in v},
        "units": {"depth": "ft", "pressure": "psi", "mud_weight": "ppg"},
    }


def export_witsml(values: Dict, out_path: str) -> str:
    """Export WITSML XML to a file; returns the path (validates parse)."""
    xml = build_witsml(values)
    minidom.parseString(xml)          # raises if malformed
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(xml, encoding="utf-8")
    return out_path


def export_json(values: Dict, out_path: str) -> str:
    data = build_json(values)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(data, indent=2,
                                         ensure_ascii=False),
                              encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    import tempfile
    vals = {"well_name": "Well A", "field_name": "Field X",
            "operator": "the Operator", "mud_weight": "12",
            "depth": "5000", "water_depth": "0",
            "trajectory_table": (
                "| MD (ft) | Inc (°) | Az (°) |\n|---|---|---|\n"
                "| 0 | 0 | 90 |\n| 2500 | 30 | 90 |\n| 5000 | 30 | 90 |")}
    xml = build_witsml(vals)
    dom = minidom.parseString(xml)
    wells = dom.getElementsByTagName("well")
    assert len(wells) == 1
    assert wells[0].getElementsByTagName("name")[0].firstChild.data == \
        "Well A"
    sts = dom.getElementsByTagName("trajectoryStation")
    assert len(sts) == 3, len(sts)
    # TVD at 5000 ft: build 0->30 deg over 2500 ft (BUR 1.2°/100ft,
    # R = 4775 ft): TVD_build = R·sin30 = 2387.5; hold 2500 ft @ 30°:
    # +2500·cos30 = 2165.1 -> total 4552.6 ft (minimum curvature)
    tvds = [float(s.getElementsByTagName("tvd")[0].firstChild.data)
            for s in sts]
    assert abs(tvds[-1] - 4552.6) < 1.5, tvds
    tmp = tempfile.mkdtemp(prefix="drl_witsml_")
    p = export_witsml(vals, tmp + "/well.xml")
    assert Path(p).exists()
    j = build_json(vals)
    assert j["well"]["name"] == "Well A"
    assert j["basis"]["mud_weight"] == "12"
    pj = export_json(vals, tmp + "/well.json")
    assert Path(pj).exists()
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    print("  ✔ witsml selftest: XML well-formed, trajectory exported")
    return xml


if __name__ == "__main__":
    _selftest()
    print("witsml_export OK")
