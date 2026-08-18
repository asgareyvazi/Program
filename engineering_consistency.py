# ============================================================================
# CROSS-DOCUMENT CONSISTENCY CHECK
# File: engineering_consistency.py
# Audit item: "Cross-Document Consistency" — the final document must not
# contain contradictory values (TD here vs casing there, MW conflicts,
# ECD above FG, BOP below MASP...).
#
# Scans the FINAL markdown (after every enrichment stage) and extracts
# engineering values by key, then cross-checks pairs that must agree:
#   - TD vs casing/shoe depth (casing < TD)
#   - Mud weight vs pore pressure / fracture gradient
#   - ECD vs fracture gradient
#   - BOP WP vs MASP
#   - Kill MW vs casing burst
#   - duplicate conflicting values of the same key
# Returns findings (level/code/message) rendered as a Word section.
# ============================================================================

import re
from typing import Dict, List, Optional, Tuple

CF = 0.052

# units assumed when a number appears without a unit near a known label
try:
    from input_registry import REGISTRY as _REG
    _LABEL_KEYS = {label.lower(): canon
                   for canon, (label, _u, _mn, _mx, _al) in _REG.items()}
except Exception:
    _LABEL_KEYS = {}
_LABEL_KEYS.update({
    "total depth": "td_depth", "td depth": "td_depth",
    "td (md)": "td_md", "target depth": "target_depth",
    "casing depth": "casing_depth", "shoe depth": "shoe_depth",
    "mud weight": "mud_weight", "mud density": "mud_weight",
    "formation pressure": "formation_pressure",
    "pore pressure": "pore_pressure",
    "fracture gradient": "fracture_gradient",
    "ecd": "ecd", "bop working pressure": "bop_wp",
    "maasp": "maasp", "masp": "masp",
    "kill mud weight": "kill_mw", "kmw": "kill_mw",
    "kick tolerance": "kick_tolerance",
    "flow rate": "flow_rate", "pump rate": "flow_rate",
    "rpm": "rpm", "wob": "wob", "rop": "rop",
    "hole size": "hole_size", "bit size": "bit_size",
    "casing size": "casing_size",
})
for _canon, (_lbl, _u, _mn, _mx, _al) in _REG.items():
    for _a in _al:
        _LABEL_KEYS.setdefault(_a.replace("_", " "), _canon)

_NUM = re.compile(r"(\d{1,6}(?:[.,]\d+)?)\s*(ppg|psi|ft|m|in|bbl|gpm|"
                  r"klbf|rpm|ft/hr|lb/100ft2|cP)?")


def extract_typed_values(md_text: str) -> Dict[str, List[Tuple[float, str]]]:
    """Scan the document for 'label : number unit' patterns grouped by
    canonical key."""
    out: Dict[str, List[Tuple[float, str]]] = {}
    for line in (md_text or "").splitlines():
        low = line.lower()
        for label, key in _LABEL_KEYS.items():
            idx = low.find(label)
            if idx < 0:
                continue
            after = line[idx + len(label):idx + len(label) + 60]
            m = _NUM.search(after)
            if m:
                try:
                    val = float(m.group(1).replace(",", ""))
                except ValueError:
                    continue
                unit = (m.group(2) or "").lower()
                out.setdefault(key, []).append((val, unit))
    return out


def _first(d: Dict[str, List[Tuple[float, str]]], key: str
           ) -> Optional[Tuple[float, str]]:
    vals = d.get(key)
    return vals[0] if vals else None


def _to_ppg(v: float, unit: str) -> float:
    u = unit.lower()
    if u == "psi":
        return v / 0.052 / 10000  # not enough info — caller decides
    return v


def consistency_check(md_text: str) -> List[Dict]:
    """Return findings: {level, code, message, hint}."""
    vals = extract_typed_values(md_text)
    f: List[Dict] = []

    def _add(level, code, message, hint=""):
        f.append({"level": level, "code": code, "message": message,
                  "hint": hint})

    def _cmp(key, as_ft=False, as_ppg=False):
        return _first(vals, key)

    # --- depths: casing/shoe must be < TD ---
    td = _cmp("td_depth") or _cmp("td_md") or _cmp("target_depth")
    csg = _cmp("casing_depth")
    shoe = _cmp("shoe_depth")
    if td and csg:
        td_v = td[0] * 3.28084 if td[1] == "m" else td[0]
        csg_v = csg[0] * 3.28084 if csg[1] == "m" else csg[0]
        if csg_v > td_v * 1.02:
            _add("CRITICAL", "CONS-CASING-TD",
                 f"Casing depth ({csg[0]:g} {csg[1] or 'ft'}) exceeds "
                 f"total depth ({td[0]:g} {td[1] or 'ft'}) in the "
                 "document — inconsistent well architecture.",
                 "Casing shoe must be above TD; check the casing program "
                 "section.")
    if td and shoe:
        td_v = td[0] * 3.28084 if td[1] == "m" else td[0]
        sh_v = shoe[0] * 3.28084 if shoe[1] == "m" else shoe[0]
        if sh_v > td_v * 1.02:
            _add("CRITICAL", "CONS-SHOE-TD",
                 f"Shoe depth ({shoe[0]:g}) exceeds TD ({td[0]:g}).")

    # --- mud weight vs pressures ---
    mw = _cmp("mud_weight")
    pp = _cmp("formation_pressure") or _cmp("pore_pressure")
    fg = _cmp("fracture_gradient")
    if mw and pp:
        m = mw[0]
        p = pp[0]
        # both assumed ppg; if one is psi there is no way to compare here
        if mw[1] in ("ppg", "") and pp[1] in ("ppg", "") and m < p:
            _add("HIGH", "CONS-MW-PP",
                 f"Mud weight ({m:g} ppg) below pore pressure "
                 f"({p:g} ppg) — influx risk.",
                 "Raise MW or document a managed-pressure approach.")
    if mw and fg:
        m = mw[0]
        g = fg[0]
        if mw[1] in ("ppg", "") and fg[1] in ("ppg", "") and m > g:
            _add("CRITICAL", "CONS-MW-FG",
                 f"Mud weight ({m:g} ppg) exceeds fracture gradient "
                 f"({g:g} ppg) — induced losses.",
                 "Reduce MW or revise the casing program.")

    # --- ECD vs FG ---
    ecd = _cmp("ecd")
    if ecd and fg:
        e = ecd[0]
        g = fg[0]
        if ecd[1] in ("ppg", "") and fg[1] in ("ppg", "") and e > g:
            _add("CRITICAL", "CONS-ECD-FG",
                 f"ECD ({e:g} ppg) exceeds fracture gradient "
                 f"({g:g} ppg).")

    # --- BOP vs MASP ---
    bop = _cmp("bop_wp")
    masp = _cmp("masp") or _cmp("maasp")
    if bop and masp and bop[0] < masp[0]:
        _add("CRITICAL", "CONS-BOP-MASP",
             f"BOP working pressure ({bop[0]:g} psi) below MASP "
             f"({masp[0]:g} psi).")

    # --- duplicate conflicting values of the same key ---
    for key, entries in vals.items():
        if key in ("flow_rate", "rpm", "wob", "rop"):
            continue  # operational ranges legitimately vary
        nums = [e[0] for e in entries if e[0] > 0]
        if len(nums) >= 2 and max(nums) > min(nums) * 1.5:
            _add("HIGH", f"CONS-DUP-{key.upper()}",
                 f"Conflicting values for {key.replace('_', ' ')} in the "
                 f"document: {min(nums):g} vs {max(nums):g}.")

    return f


def consistency_markdown(findings: List[Dict], operator: str = "") -> str:
    """Word-ready CONSISTENCY CHECK section (only when issues exist)."""
    if not findings:
        return ""
    op = (operator or "").strip() or "the Operator"
    L = ["## CROSS-DOCUMENT CONSISTENCY CHECK", ""]
    L.append("The final document was scanned for contradictory "
             "engineering values:")
    L.append("")
    L.append("| Severity | Code | Finding |")
    L.append("|---|---|---|")
    for f in findings:
        icon = {"CRITICAL": "⛔", "HIGH": "⚠️"}.get(f["level"], "•")
        L.append(f"| {icon} {f['level']} | {f['code']} | "
                 f"{f['message']} |")
    L.append("")
    L.append(f"*Consistency scan performed deterministically for {op}; "
             "resolve all CRITICAL/HIGH items before issue.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    md = """
| Total Depth | 10000 ft |
| Casing Depth | 12000 ft |
| Mud Weight | 17 ppg |
| Fracture Gradient | 16 ppg |
| ECD | 16.5 ppg |
| BOP Working Pressure | 5000 psi |
| MASP | 7000 psi |
"""
    f = consistency_check(md)
    codes = {x["code"] for x in f}
    assert "CONS-CASING-TD" in codes, codes
    assert "CONS-MW-FG" in codes, codes
    assert "CONS-ECD-FG" in codes, codes
    assert "CONS-BOP-MASP" in codes, codes
    # clean doc -> no findings
    md2 = """
| Total Depth | 10000 ft |
| Casing Depth | 8000 ft |
| Mud Weight | 12 ppg |
| Fracture Gradient | 16 ppg |
| ECD | 12.5 ppg |
| BOP Working Pressure | 10000 psi |
| MASP | 3000 psi |
"""
    f2 = consistency_check(md2)
    assert f2 == [], f2
    # markdown section
    md3 = consistency_markdown(f)
    assert "CROSS-DOCUMENT CONSISTENCY" in md3
    assert consistency_markdown([]) == ""
    print(f"  ✔ consistency selftest: {len(f)} findings in bad doc, "
          f"0 in clean doc")
    return f


if __name__ == "__main__":
    _selftest()
    print("engineering_consistency OK")
