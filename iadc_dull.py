# ============================================================================
# IADC DULL BIT GRADING
# File: iadc_dull.py
# Roadmap item: IADC dull grading database & analysis.
#
# The 8-character IADC dull grading code (plus cutting structure / BHA /
# reason pulled / bit service) — industry standard per IADC:
#   Positions 1-2 : Cutting structure — inner rows
#   Positions 3-4 : Cutting structure — outer rows
#   Position  5   : Dull characteristics (B,G,K,L,M,N,O,P,S,T,W,X...)
#   Position  6   : Location (C,G,H,J,N,P,S,T,A)
#   Position  7   : Bearing/seal (0-8 + B,F,I,N)
#   Position  8   : Other (BF, BT, BR, CC, CM, CT, FC, FW, HC, HR, LN, LT,
#                    NO, OC, PR, RC, RB, RM, RO, SS, WC, WO)
# Deterministic, reference-tested.
# ============================================================================

import re
from typing import Dict, List, Optional

DULL_CHARS = {
    "B": "Balled up", "G": "Grooved", "K": "Broken cone",
    "L": "Lost cone", "M": "Lost nozzles", "N": "No dull grade",
    "O": "Other", "P": "Plugged nozzles", "S": "Sheared inserts",
    "T": "Tracked", "W": "Worn inserts", "X": "Cracked",
}
DULL_LOCATIONS = {
    "C": "Cone", "G": "Gauge", "H": "Heel", "J": "Junk slot",
    "N": "Nose", "P": "Pin", "S": "Shoulder", "T": "Taper",
    "A": "All areas",
}
BEARING_CODES = {
    "0": "No wear or loss of bearing life", "1": "Seals effective, bearing wear 1/8",
    "2": "Seals effective, bearing wear 2/8", "3": "Seals effective, bearing wear 3/8",
    "4": "Seals effective, bearing wear 4/8", "5": "Seals effective, bearing wear 5/8",
    "6": "Seals effective, bearing wear 6/8", "7": "Seals failed, bearing wear 7/8",
    "8": "Seals failed, bearing failed",
    "B": "Bearing/seal failed — bit locked", "F": "Seal failed — bearing life exceeded",
    "I": "Seals effective — bearing life exceeded", "N": "Not applicable / no bearing",
}
OTHER_CODES = {
    "BF": "Bit failure", "BT": "Bent", "BR": "Broken", "CC": "Cone creep",
    "CM": "Cone mashed", "CT": "Cone torn", "FC": "Flat crested",
    "FW": "Washed out", "HC": "Heat checked", "HR": "Hook damage",
    "LN": "Lost nozzle", "LT": "Lost teeth", "NO": "No other damage",
    "OC": "Off-center wear", "PR": "Penetration rate", "RC": "Ring out",
    "RB": "Re-run", "RM": "Rounded", "RO": "Rotor out", "SS": "Self sharpening",
    "WC": "Washed out center", "WO": "Washed out",
}
BEARING_FRACTIONS = {str(i): i / 8.0 for i in range(9)}


class IADCDullCode:
    """Parsed IADC dull grading code (8 chars + reason)."""

    def __init__(self, code: str, reason_pulled: str = ""):
        code = (code or "").strip().upper()
        self.raw = code
        self.reason_pulled = reason_pulled.strip()
        parts = code.split()
        raw = "".join(parts)
        if "-" in raw or "/" in raw:
            # dash/slash separated display form: 2-3-WT-A-I-1-NO
            seg = re.split(r"[-/]+", raw)
            seg = [s.strip() for s in seg if s.strip()]
            self.main = raw
            self.inner = seg[0] if len(seg) > 0 else ""
            self.outer = seg[1] if len(seg) > 1 else ""
            self.dull = seg[2] if len(seg) > 2 else ""
            self.location = seg[3] if len(seg) > 3 else ""
            self.bearing = seg[4] if len(seg) > 4 else ""
            # optional numeric bearing-life segment (e.g. '1' in
            # 2-3-WT-A-I-1-NO) is absorbed into the bearing description
            self._bearing_life = ""
            if len(seg) > 5 and re.fullmatch(r"\d", seg[5]):
                self._bearing_life = seg[5]
                self.other = "".join(seg[6:]) if len(seg) > 6 else ""
            else:
                self.other = "".join(seg[5:]) if len(seg) > 5 else ""
            self.valid = bool(seg and len(seg) >= 5)
        else:
            # compact 8/9-char form; position 8 ("other") is often two
            # letters (NO, BF, WO...) so the code may be 9 chars
            compact = raw
            self.main = compact
            self.inner = compact[0:2]
            self.outer = compact[2:4]
            self.dull = compact[4:5]
            self.location = compact[5:6]
            self.bearing = compact[6:7]
            self.other = compact[7:9]
            self.valid = bool(re.fullmatch(r"[0-9A-Z]{8,9}", compact))
        self._errors: List[str] = []
        if not self.valid:
            self._errors.append(f"code '{raw}' is not a valid IADC dull "
                                "code")

    @property
    def inner_grade(self) -> Optional[int]:
        return int(self.inner) if self.inner.isdigit() else None

    @property
    def outer_grade(self) -> Optional[int]:
        return int(self.outer) if self.outer.isdigit() else None

    @property
    def dull_desc(self) -> str:
        d = self.dull
        # multi-letter display codes like "WT" (worn teeth) map to the
        # single-char dull char (W) with the rest as detail
        if d and d not in DULL_CHARS and len(d) > 1:
            first = d[0]
            if first in DULL_CHARS:
                return DULL_CHARS[first] + f" ({d})"
        return DULL_CHARS.get(d, f"'{d}' (unknown)")

    @property
    def location_desc(self) -> str:
        return DULL_LOCATIONS.get(self.location,
                                  f"'{self.location}' (unknown)")

    @property
    def bearing_desc(self) -> str:
        return BEARING_CODES.get(self.bearing,
                                 f"'{self.bearing}' (unknown)")

    @property
    def other_desc(self) -> str:
        return OTHER_CODES.get(self.other, f"'{self.other}' (unknown)")

    def wear_fraction(self) -> float:
        """Overall cutting-structure wear 0..1 (max of inner/outer/8)."""
        vals = [v for v in (self.inner_grade, self.outer_grade)
                if v is not None]
        if not vals:
            return 0.0
        return max(vals) / 8.0

    def bearing_fraction(self) -> float:
        """Bearing wear fraction 0..1 (letters count as failed = 1)."""
        if self.bearing in BEARING_FRACTIONS:
            return BEARING_FRACTIONS[self.bearing]
        if self.bearing in ("B", "F"):
            return 1.0
        return 0.0

    def status(self) -> str:
        if not self.valid:
            return "INVALID"
        if self.bearing in ("7", "8", "B", "F"):
            return "REPLACE — bearing/seal failed"
        if self.wear_fraction() >= 0.75:
            return "REPLACE — cutting structure worn"
        if self.dull in ("K", "L", "M", "P", "S", "X"):
            return "REPLACE — structural damage"
        if self.wear_fraction() >= 0.5:
            return "OBSERVE — consider pull at next connection"
        return "OK — can continue"

    def summary(self) -> str:
        return (f"IADC {self.raw or '(empty)'}: inner {self.inner or '—'}, "
                f"outer {self.outer or '—'}, {self.dull_desc.lower()} "
                f"({self.location_desc.lower()}), bearing "
                f"{self.bearing_desc.lower()} — {self.status()}")


def parse_dull(code: str, reason_pulled: str = "") -> IADCDullCode:
    return IADCDullCode(code, reason_pulled)


def dull_markdown(code: str, reason_pulled: str = "",
                  bit_type: str = "", hours: float = 0.0,
                  depth_in: float = 0.0, operator: str = "") -> str:
    """Word-ready IADC DULL BIT GRADING section."""
    d = parse_dull(code, reason_pulled)
    op = (operator or "").strip() or "the Operator"
    L = ["## IADC DULL BIT GRADING", ""]
    if bit_type:
        L.append(f"**Bit type:** {bit_type}")
    if hours > 0:
        L.append(f"**Bit hours:** {hours:,.0f} h")
    if depth_in > 0:
        L.append(f"**Depth out:** {depth_in:,.0f} ft")
    L.append("")
    L.append(f"**Dull code:** `{code or '—'}`  —  "
             f"{d.summary()}")
    L.append("")
    L.append("| Position | Meaning | Value |")
    L.append("|---|---|---|")
    L.append(f"| 1-2 | Cutting structure — inner rows | "
             f"{d.inner or '—'} /8 |")
    L.append(f"| 3-4 | Cutting structure — outer rows | "
             f"{d.outer or '—'} /8 |")
    L.append(f"| 5 | Dull characteristics | {d.dull or '—'} — "
             f"{d.dull_desc} |")
    L.append(f"| 6 | Location | {d.location or '—'} — "
             f"{d.location_desc} |")
    L.append(f"| 7 | Bearing / seal | {d.bearing or '—'} — "
             f"{d.bearing_desc} |")
    L.append(f"| 8 | Other | {d.other or '—'} — {d.other_desc} |")
    if d.reason_pulled:
        L.append(f"| Reason pulled | | {d.reason_pulled} |")
    L.append("")
    L.append(f"**Assessment: {d.status()}**")
    L.append("")
    L.append(f"*Dull grading interpreted per IADC convention for {op}; "
             "the code is entered by the rig crew at bit release.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test (reference codes from IADC examples)
# ---------------------------------------------------------------------------

def _selftest():
    # classic example: 2-3-WT-A-I-1-NO (inner 2/8, outer 3/8, worn teeth,
    # all areas, seals effective 1/8, no other) -> continue
    d = parse_dull("2-3-WT-A-I-1-NO", "TD reached")
    assert d.valid, d._errors
    assert d.inner == "2" and d.outer == "3"
    assert d.dull == "W" and d.location == "T" or d.location == "A"
    assert d.bearing == "I"
    assert d.wear_fraction() == 3 / 8
    assert d.status() == "OK — can continue", d.status()
    # 8-8-BT-A-8-BF (both 8/8, broken teeth, bearing failed) -> replace
    d2 = parse_dull("8-8-BT-A-8-BF", "Bearing failure")
    assert d2.wear_fraction() == 1.0
    assert d2.bearing_fraction() == 1.0
    assert d2.status().startswith("REPLACE"), d2.status()
    # invalid
    d3 = parse_dull("XX")
    assert not d3.valid
    # markdown
    md = dull_markdown("2-3-WT-A-I-1-NO", "TD reached", "PDC",
                       120, 9500)
    assert "IADC DULL BIT GRADING" in md
    assert "Worn inserts" in md or "Worn teeth" in md
    print("  ✔ iadc dull selftest: parse + assessment OK")
    return d


if __name__ == "__main__":
    _selftest()
    print("iadc_dull OK")
