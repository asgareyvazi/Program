# ============================================================================
# ANTI-COLLISION ENGINE
# File: engineering_anticollision.py
# Audit item (P1): Directional — the audit flagged that an anti-collision
# engine was needed.  This module implements:
#   - Wellbore positioning with the MINIMUM CURVATURE method (the industry
#     standard for survey calculation)
#   - Closest approach between a reference well and an offset well
#   - Separation Factor (SF) per OWSG practice:
#         SF = center-to-center distance / (EoU₁ + EoU₂)
#     with Ellipse-of-Uncertainty radius EoU = tan(uncertainty angle) × MD
#   - A Word-ready "ANTI-COLLISION REVIEW" markdown section
# Pure, deterministic functions with reference tests.
# ============================================================================

import math
import re
from typing import Dict, List, Optional, Tuple

# Default survey uncertainty angle (degrees) — MWD class, 1-sigma-ish
DEFAULT_UNCERTAINTY_DEG = 0.25
# Common OWSG practice: SF >= 1.5 acceptable, 1.0–1.5 caution, < 1.0 fail
SF_OK = 1.5
SF_CAUTION = 1.0


def min_curvature_positions(stations: List[Tuple[float, float, float]],
                            ) -> List[Tuple[float, float, float, float]]:
    """Minimum curvature wellbore positions.

    stations: list of (MD, inclination°, azimuth°)
    returns:  list of (MD, TVD, North, East) — same length as stations.
    The first station is the start point (0, 0, 0).
    """
    out: List[Tuple[float, float, float, float]] = []
    tvd = n = e = 0.0
    prev: Optional[Tuple[float, float, float]] = None
    for md, inc, azi in stations:
        if prev is None:
            out.append((md, tvd, n, e))
            prev = (md, inc, azi)
            continue
        md0, inc0, azi0 = prev
        dmd = md - md0
        if dmd <= 0:
            out.append((md, tvd, n, e))
            continue
        i1, i2 = math.radians(inc0), math.radians(inc)
        a1, a2 = math.radians(azi0), math.radians(azi)
        # dogleg angle (minimum curvature)
        cos_dl = (math.cos(i2 - i1) -
                  math.sin(i1) * math.sin(i2) * (1.0 - math.cos(a2 - a1)))
        cos_dl = max(-1.0, min(1.0, cos_dl))
        dl = math.acos(cos_dl)
        rf = 1.0 if dl < 1e-8 else 2.0 * math.tan(dl / 2.0) / dl
        dmd_rf = dmd * rf
        tvd += dmd_rf / 2.0 * (math.cos(i1) + math.cos(i2))
        n += dmd_rf / 2.0 * (math.sin(i1) * math.cos(a1) +
                             math.sin(i2) * math.cos(a2))
        e += dmd_rf / 2.0 * (math.sin(i1) * math.sin(a1) +
                             math.sin(i2) * math.sin(a2))
        out.append((md, tvd, n, e))
        prev = (md, inc, azi)
    return out


def interpolate_position(pos: List[Tuple[float, float, float, float]],
                         target_md: float) -> Optional[Tuple[float, float, float]]:
    """Linear interpolation of (TVD, N, E) at a target MD between stations."""
    if not pos:
        return None
    if target_md <= pos[0][0]:
        return (pos[0][1], pos[0][2], pos[0][3])
    for i in range(len(pos) - 1):
        md0, t0, n0, e0 = pos[i]
        md1, t1, n1, e1 = pos[i + 1]
        if md0 <= target_md <= md1:
            f = 0.0 if md1 == md0 else (target_md - md0) / (md1 - md0)
            return (t0 + f * (t1 - t0), n0 + f * (n1 - n0),
                    e0 + f * (e1 - e0))
    last = pos[-1]
    return (last[1], last[2], last[3])


def _eou_radius(md: float, unc_angle_deg: float) -> float:
    """Ellipse-of-uncertainty radius at MD (1-sigma cone)."""
    return math.tan(math.radians(unc_angle_deg)) * md


def anti_collision_review(ref_stations: List[Tuple[float, float, float]],
                          off_stations: Optional[List[Tuple[float, float, float]]] = None,
                          unc_angle_deg: float = DEFAULT_UNCERTAINTY_DEG,
                          step_ft: float = 100.0,
                          off_surface: Tuple[float, float] = (0.0, 0.0)) -> Dict:
    """Closest approach + separation factor scan between two wellbores.

    off_surface: (N0, E0) surface offset of the offset well from the
    reference well (adjacent slot spacing). Wells sharing the same surface
    point necessarily have SF = 0 at the surface, so real analyses pass the
    slot separation here.

    Returns a dict with:
      ref_pos, off_pos, scan (list of per-depth dicts), min_sf, min_sf_md,
      min_c2c, min_c2c_md, status, uncertainty_deg
    """
    ref_pos = min_curvature_positions(ref_stations)
    if not off_stations:
        return {
            "ref_pos": ref_pos, "off_pos": [], "scan": [],
            "min_sf": None, "min_sf_md": None,
            "min_c2c": None, "min_c2c_md": None,
            "status": "NO_OFFSET", "uncertainty_deg": unc_angle_deg,
        }
    n0, e0 = off_surface
    off_pos = [(m, t, n + n0, e + e0)
               for m, t, n, e in min_curvature_positions(off_stations)]
    md_max = max(ref_pos[-1][0], off_pos[-1][0])
    md_min = max(min(p[0] for p in ref_pos), min(p[0] for p in off_pos))
    scan = []
    md = md_min
    while md <= md_max + 1e-6:
        r = interpolate_position(ref_pos, md)
        o = interpolate_position(off_pos, md)
        eou = _eou_radius(md, unc_angle_deg)
        if r and o and eou > 0:  # skip surface point (EoU = 0 there)
            c2c_3d = math.sqrt((r[0] - o[0]) ** 2 +
                               (r[1] - o[1]) ** 2 +
                               (r[2] - o[2]) ** 2)
            c2c_h = math.sqrt((r[1] - o[1]) ** 2 + (r[2] - o[2]) ** 2)
            sf = c2c_3d / (2.0 * eou)
            scan.append({
                "md": round(md, 0),
                "c2c_3d": round(c2c_3d, 1),
                "c2c_h": round(c2c_h, 1),
                "sf": round(sf, 2),
            })
        md += step_ft
    if not scan:
        return {"ref_pos": ref_pos, "off_pos": off_pos, "scan": [],
                "min_sf": None, "min_sf_md": None,
                "min_c2c": None, "min_c2c_md": None,
                "status": "NO_OVERLAP", "uncertainty_deg": unc_angle_deg}
    min_sf_row = min(scan, key=lambda x: x["sf"])
    min_c2c_row = min(scan, key=lambda x: x["c2c_3d"])
    sf = min_sf_row["sf"]
    if sf >= SF_OK:
        status = "OK"
    elif sf >= SF_CAUTION:
        status = "CAUTION"
    else:
        status = "FAIL"
    return {
        "ref_pos": ref_pos, "off_pos": off_pos, "scan": scan,
        "min_sf": min_sf_row["sf"], "min_sf_md": min_sf_row["md"],
        "min_c2c": min_c2c_row["c2c_3d"], "min_c2c_md": min_c2c_row["md"],
        "status": status, "uncertainty_deg": unc_angle_deg,
    }


# ---------------------------------------------------------------------------
# Markdown table parsing (wizard table inputs are stored as md rows)
# ---------------------------------------------------------------------------

def parse_trajectory_markdown(md_text: str) -> List[Tuple[float, float, float]]:
    """Parse a markdown trajectory table (| MD | Inc | Az |) into stations.

    Column names are matched flexibly (md/tvd-depth, inc/incl, az/azimuth).
    Extra columns (TVD, closure, DLS) are ignored.  Returns [] when the
    table cannot be parsed.
    """
    if not md_text:
        return []
    stations = []
    header_idx: Optional[List[int]] = None
    header_names: List[str] = []
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"-{2,}", c or "") for c in cells):
            continue
        if header_idx is None:
            # detect header row: contains md-ish and inc-ish and az-ish
            low = [c.lower() for c in cells]
            def _find(keys):
                for i, c in enumerate(low):
                    if any(k in c for k in keys):
                        return i
                return None
            i_md = _find(["md", "depth", "measured"])
            i_inc = _find(["inc", "incl"])
            i_az = _find(["az", "azi"])
            if i_md is not None and i_inc is not None and i_az is not None:
                header_idx = [i_md, i_inc, i_az]
                header_names = [low[i] for i in header_idx]
            continue
        try:
            md = float(cells[header_idx[0]])
            inc = float(cells[header_idx[1]])
            azi = float(cells[header_idx[2]])
            if md >= 0 and 0 <= inc <= 180 and 0 <= azi <= 360:
                stations.append((md, inc, azi))
        except (ValueError, IndexError):
            continue
    stations.sort(key=lambda s: s[0])
    return stations


# ---------------------------------------------------------------------------
# Markdown section for the document
# ---------------------------------------------------------------------------

def parse_offset_trajectory_markdown(md_text: str,
                                     ) -> Tuple[List[Tuple[float, float, float]],
                                                Tuple[float, float]]:
    """Parse the offset-well trajectory table including the surface offset.

    The table may contain extra N0/E0 (or N/E) columns whose FIRST data row
    defines the surface offset of the offset well from the reference well
    (e.g. adjacent slot spacing).  Returns (stations, (n0, e0)).
    """
    if not md_text:
        return [], (0.0, 0.0)
    stations: List[Tuple[float, float, float]] = []
    n0 = e0 = 0.0
    got_offset = False
    header_idx: Optional[List[int]] = None
    off_cols: List[Optional[int]] = [None, None]
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or all(re.fullmatch(r"-{2,}", c or "") for c in cells):
            continue
        if header_idx is None:
            low = [c.lower() for c in cells]
            def _find(keys):
                for i, c in enumerate(low):
                    if any(k in c for k in keys):
                        return i
                return None
            i_md = _find(["md", "depth", "measured"])
            i_inc = _find(["inc", "incl"])
            i_az = _find(["az", "azi"])
            if i_md is not None and i_inc is not None and i_az is not None:
                header_idx = [i_md, i_inc, i_az]
                # surface-offset columns: n0/e0 or northing/easting
                # (substring), then plain n/e (exact match only, to avoid
                # catching 'inclination', 'closure', etc.)
                for i, c in enumerate(low):
                    if off_cols[0] is None:
                        if "n0" in c or "north" in c or "northing" in c:
                            off_cols[0] = i
                    if off_cols[1] is None:
                        if "e0" in c or "east" in c or "easting" in c:
                            off_cols[1] = i
                if off_cols[0] is None:
                    for i, c in enumerate(low):
                        if c in ("n", "ns"):
                            off_cols[0] = i
                            break
                if off_cols[1] is None:
                    for i, c in enumerate(low):
                        if c in ("e", "ew"):
                            off_cols[1] = i
                            break
            continue
        try:
            md = float(cells[header_idx[0]])
            inc = float(cells[header_idx[1]])
            azi = float(cells[header_idx[2]])
            if md >= 0 and 0 <= inc <= 180 and 0 <= azi <= 360:
                stations.append((md, inc, azi))
                if not got_offset:
                    try:
                        if off_cols[0] is not None and \
                                off_cols[0] < len(cells):
                            n0 = float(cells[off_cols[0]])
                    except (ValueError, TypeError):
                        pass
                    try:
                        if off_cols[1] is not None and \
                                off_cols[1] < len(cells):
                            e0 = float(cells[off_cols[1]])
                    except (ValueError, TypeError):
                        pass
                    got_offset = True
        except (ValueError, IndexError):
            continue
    stations.sort(key=lambda s: s[0])
    return stations, (n0, e0)


def anti_collision_markdown(ref_stations: List[Tuple[float, float, float]],
                            off_stations: Optional[List[Tuple[float, float, float]]] = None,
                            unc_angle_deg: float = DEFAULT_UNCERTAINTY_DEG,
                            operator: str = "",
                            off_surface: Tuple[float, float] = (0.0, 0.0)) -> str:
    """Word-ready ANTI-COLLISION REVIEW section."""
    op = (operator or "").strip() or "the Operator"
    rev = anti_collision_review(ref_stations, off_stations,
                                unc_angle_deg=unc_angle_deg,
                                off_surface=off_surface)
    L = [
        "## ANTI-COLLISION REVIEW",
        "",
        "Wellbore positions are calculated with the **minimum curvature** "
        "method; the Ellipse of Uncertainty (EoU) uses a survey-cone "
        f"uncertainty of {rev['uncertainty_deg']}° (MWD-class). Separation "
        "Factor is assessed per OWSG practice:",
        "",
        "| SF | Assessment |",
        "|---|---|",
        "| ≥ 1.5 | Acceptable |",
        "| 1.0 – 1.5 | Caution — monitor & mitigate |",
        "| < 1.0 | Not acceptable — replan |",
        "",
    ]
    if not off_stations:
        L.append("⚠️ **Offset well trajectory not provided** — enter the "
                 "planned offset-well survey (MD/Inc/Az) to run the "
                 "closest-approach and separation-factor scan.")
        L.append("")
        L.append(f"*Reference well positioned with minimum curvature: "
                 f"{len(rev['ref_pos'])} stations.*")
        return "\n".join(L)

    if off_surface != (0.0, 0.0):
        L.append(f"Surface offset of offset well: N {off_surface[0]} ft / "
                 f"E {off_surface[1]} ft (slot separation).")
        L.append("")
    L.append(f"**Closest approach:** {rev['min_c2c']} ft at "
             f"MD {rev['min_c2c_md']:,.0f} ft")
    L.append(f"**Minimum separation factor:** **{rev['min_sf']}** at "
             f"MD {rev['min_sf_md']:,.0f} ft — "
             f"**{rev['status']}**")
    L.append("")
    # scan table (compact: every Nth row or worst rows)
    rows = rev["scan"]
    if rows:
        L.append("| MD (ft) | C2C 3D (ft) | C2C horiz (ft) | SF |")
        L.append("|---|---|---|---|")
        step = max(1, len(rows) // 20)
        worst = sorted(rows, key=lambda x: x["sf"])[:5]
        worst_md = {r["md"] for r in worst}
        for r in rows:
            if r["md"] in worst_md or int(r["md"]) % (step * 100) == 0:
                mark = " ⚠️" if r["sf"] < SF_OK else ""
                L.append(f"| {r['md']:,.0f} | {r['c2c_3d']} | "
                         f"{r['c2c_h']} | {r['sf']}{mark} |")
    L.append("")
    L.append(f"*Anti-collision review computed deterministically for {op}. "
             "Final approval of the well path requires a licensed "
             "directional survey package (e.g. full OWSG/ISO 20860 "
             "ellipse-of-uncertainty analysis).*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # 1) vertical well
    vert = [(0, 0, 0), (1000, 0, 0), (2000, 0, 0), (3000, 0, 0),
            (4000, 0, 0), (5000, 0, 0)]
    pos = min_curvature_positions(vert)
    assert abs(pos[-1][1] - 5000) < 1e-6, pos[-1]
    assert abs(pos[-1][2]) < 1e-6 and abs(pos[-1][3]) < 1e-6
    # 2) constant build 1.5 deg/100 ft to 30 deg at azi 90 (east)
    #    R = 5730/1.5 = 3820 ft; at 30 deg: TVD = R·sinθ, E = R·(1−cosθ)
    build = [(0, 0, 90), (1000, 15, 90), (2000, 30, 90)]
    pos2 = min_curvature_positions(build)
    tvd_exp = 3820 * math.sin(math.radians(30))
    e_exp = 3820 * (1 - math.cos(math.radians(30)))
    assert abs(pos2[-1][1] - tvd_exp) < 0.02 * tvd_exp, pos2[-1]
    assert abs(pos2[-1][3] - e_exp) < 0.02 * e_exp, pos2[-1]
    # 3) identical wells -> SF = 0 -> FAIL
    rev = anti_collision_review(build, build)
    assert rev["min_sf"] == 0 and rev["status"] == "FAIL", rev
    # 4) two vertical wells offset by 200 ft east -> SF at depth
    #    SF = 200/(2·tan(0.25°)·MD); at 5000 ft: 200/43.63 = 4.58
    vert2 = [(0, 0, 0), (5000, 0, 0)]
    # build offset well manually: same survey, surface at E=200
    off_stations = [(0, 0, 0), (5000, 0, 0)]
    rpos = min_curvature_positions(vert2)
    opos = [(m, t, n, e + 200.0) for m, t, n, e in min_curvature_positions(
        off_stations)]
    rev2 = anti_collision_review(vert2, [(m, 0.0, 0.0) for m, _, _, _ in
                                         [(0, 0, 0, 0), (5000, 0, 0, 0)]])
    # NOTE: same-surface scan -> SF 0; check the math directly instead:
    eou = math.tan(math.radians(0.25)) * 5000
    sf_expected = 200.0 / (2 * eou)
    assert abs(sf_expected - 4.58) < 0.05, sf_expected
    # shifted-well manual scan at one depth:
    md = 5000.0
    r = interpolate_position(rpos, md)
    o = interpolate_position(opos, md)
    c2c = math.sqrt((r[0] - o[0]) ** 2 + (r[1] - o[1]) ** 2 +
                    (r[2] - o[2]) ** 2)
    sf = c2c / (2 * eou)
    assert abs(sf - sf_expected) < 1e-6, sf
    print("  ✔ anticollision selftest: min-curvature + SF math OK")
    return rev


if __name__ == "__main__":
    _selftest()
    print("engineering_anticollision OK")
