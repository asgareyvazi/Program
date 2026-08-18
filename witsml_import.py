# ============================================================================
# WITSML IMPORT
# File: witsml_import.py
# Roadmap item (P3): Telemetry — WITSML import (the app currently exports
# WITSML only).  Parses a WITSML v1.4.1-style XML document and produces
# wizard input values (well identity, trajectory stations, water depth).
#
# Deterministic, stdlib-only, reference-tested.
# ============================================================================

import re
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET

WITSML_NS = "http://www.witsml.org/schemas/1series"


def _local(tag: str) -> str:
    """Strip the namespace from an ElementTree tag."""
    return tag.split("}")[-1] if "}" in tag else tag


def _text(elem, *path) -> str:
    """Find the first descendant (by local name) and return its text."""
    for e in elem.iter():
        if _local(e.tag) in path and e.text and e.text.strip():
            return e.text.strip()
    return ""


def _float(v, d=0.0) -> float:
    try:
        return float(str(v).strip()) if str(v).strip() else d
    except (TypeError, ValueError):
        return d


def parse_witsml(xml_text: str) -> Dict:
    """Parse WITSML XML into a flat dict of wizard input values.

    Returns:
      {well_name, field, operator, country, water_depth_ft,
       trajectory_table (markdown MD|Inc|Az), stations (list), warnings}
    """
    root = ET.fromstring(xml_text)
    out: Dict = {"warnings": []}
    well = None
    for e in root.iter():
        if _local(e.tag) == "well":
            well = e
            break
    if well is None:
        # maybe the root itself is <well>
        if _local(root.tag) == "well":
            well = root
    if well is None:
        raise ValueError("no <well> element found in WITSML document")

    out["well_name"] = _text(well, "name") or ""
    out["field"] = _text(well, "field") or ""
    out["operator"] = _text(well, "operator") or ""
    out["country"] = _text(well, "country") or ""
    wd = _float(_text(well, "waterDepth"))
    out["water_depth"] = wd or 0.0

    # trajectory stations -> markdown table for the wizard input
    stations = []
    for st in well.iter():
        if _local(st.tag) != "trajectoryStation":
            continue
        md = _float(_text(st, "md"))
        inc = _float(_text(st, "inclination"))
        azi = _float(_text(st, "azimuth"))
        if md >= 0:
            stations.append((md, inc, azi))
    stations.sort(key=lambda s: s[0])
    if stations:
        rows = ["| MD (ft) | Inc (°) | Az (°) |", "|---|---|---|"]
        for md, inc, azi in stations:
            rows.append(f"| {md:.1f} | {inc:.2f} | {azi:.2f} |")
        out["trajectory_table"] = "\n".join(rows)
        out["stations"] = stations
    else:
        out["trajectory_table"] = ""
        out["stations"] = []
    return out


def apply_witsml_to_values(xml_text: str, values: Dict) -> Dict:
    """Merge parsed WITSML values into an existing values dict (only fills
    empty keys so user input is never overwritten)."""
    parsed = parse_witsml(xml_text)
    values = dict(values or {})
    for k in ("well_name", "field", "operator", "country",
              "water_depth", "trajectory_table"):
        if k in parsed and parsed[k] and not str(values.get(k, "")).strip():
            values[k] = parsed[k]
    return values


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<wells xmlns="http://www.witsml.org/schemas/1series" version="1.4.1.1">
  <well uid="w1">
    <name>Imported Well</name>
    <field>Imported Field</field>
    <operator>the Operator</operator>
    <wellbore uid="wb1">
      <trajectory uid="t1">
        <trajectoryStation uid="s0">
          <md uom="ft">0.0</md><inclination uom="deg">0.0</inclination>
          <azimuth uom="deg">0.0</azimuth>
        </trajectoryStation>
        <trajectoryStation uid="s1">
          <md uom="ft">5000.0</md><inclination uom="deg">30.0</inclination>
          <azimuth uom="deg">90.0</azimuth>
        </trajectoryStation>
        <trajectoryStation uid="s2">
          <md uom="ft">10000.0</md><inclination uom="deg">30.0</inclination>
          <azimuth uom="deg">90.0</azimuth>
        </trajectoryStation>
      </trajectory>
    </wellbore>
  </well>
</wells>"""
    p = parse_witsml(xml)
    assert p["well_name"] == "Imported Well", p
    assert p["field"] == "Imported Field"
    assert p["operator"] == "the Operator"
    assert len(p["stations"]) == 3, p["stations"]
    assert "trajectory_table" in p and "| 10000.0 | 30.00 | 90.00 |" in \
        p["trajectory_table"]
    # merge only fills empty keys
    v = apply_witsml_to_values(xml, {"well_name": "Keep Me"})
    assert v["well_name"] == "Keep Me", v
    assert v["operator"] == "the Operator"
    print("  ✔ witsml import selftest: parse + merge OK")
    return p


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(parse_witsml(open(sys.argv[1], encoding="utf-8").read()))
    else:
        _selftest()
        print("witsml_import OK")
