# ============================================================================
# SPECIAL-WELLS ENGINEERING — HPHT / DEEPWATER / COMPLETION
# File: engineering_special.py
# Audit items (P1):
#   - HPHT: thermal/elastomer/metallurgy
#   - Deepwater: riser margin / subsea BOP
#   - Completion: barrier model (NORSOK D-010 philosophy)
#
# Deterministic, reference-tested engineering checks.
# ============================================================================

import math
from typing import Dict, List, Optional, Tuple

CF = 0.052
SEAWATER_GRADIENT_PSI_FT = 0.445

# ---------------------------------------------------------------------------
# HPHT — elastomer & metallurgy
# ---------------------------------------------------------------------------

ELASTOMER_RATINGS = [
    ("NBR (Nitrile)", 250, "Standard for moderate temperatures"),
    ("HNBR (Hydrogenated Nitrile)", 300, "Sour-service capable"),
    ("FKM / Viton", 400, "High temperature, gas service"),
    ("FFKM (Perfluoroelastomer)", 600, "Extreme HPHT"),
]


def elastomer_rating(max_temp_f: float) -> Dict:
    """Select the elastomer class for the maximum exposure temperature."""
    chosen = ELASTOMER_RATINGS[0]
    for name, rating, note in ELASTOMER_RATINGS:
        if max_temp_f <= rating:
            chosen = (name, rating, note)
            break
    name, rating, note = chosen
    return {"elastomer": name, "max_temp_f": rating,
            "note": note,
            "ok": max_temp_f <= rating,
            "margin_f": round(rating - max_temp_f, 0)}


def trapped_annular_pressure(delta_t_f: float, beta_1f: float = 3.2e-4,
                             kappa_1psi: float = 3.0e-6) -> float:
    """Trapped-annular thermal pressure build-up:

        ΔP = (β / κ) × ΔT
    with β the fluid thermal expansion (1/°F) and κ compressibility
    (1/psi).  For water-based fluids β/κ ≈ 106 psi/°F — the classic
    field rule for a sealed annulus."""
    if kappa_1psi <= 0:
        return 0.0
    return beta_1f / kappa_1psi * delta_t_f


def metallurgy_suggestion(co2_pct: float, h2s: str, temp_f: float,
                          chloride_ppm: float = 0.0) -> Dict:
    """Preliminary tubular metallurgy selection (screening only)."""
    try:
        sour = h2s.lower() in ("yes", "y", "true", "1") or float(
            str(h2s).replace("%", "").strip() or 0) > 0
    except ValueError:
        sour = False
    if sour:
        if temp_f > 300:
            return {"metallurgy": "CRA (e.g. 25Cr / alloy 718) with "
                    "sour-service rating",
                    "note": "H2S + high temperature — full CRA required",
                    "risk": "high"}
        return {"metallurgy": "Low-alloy steel with sour-service "
                "(NACE MR0175/ISO 15156) + inhibitor",
                "note": "H2S present — NACE-compliant materials",
                "risk": "medium"}
    if co2_pct > 2:
        return {"metallurgy": "13Cr / super-13Cr (CO2 corrosion)",
                "note": f"CO2 {co2_pct:g}% — chromium steels",
                "risk": "medium"}
    if co2_pct > 0.5:
        return {"metallurgy": "Carbon steel with corrosion allowance "
                "+ inhibitor",
                "note": f"CO2 {co2_pct:g}% — monitor corrosion",
                "risk": "low"}
    return {"metallurgy": "Carbon steel (L80 / P110 per design)",
            "note": "Mild environment", "risk": "low"}


# ---------------------------------------------------------------------------
# Deepwater — riser margin
# ---------------------------------------------------------------------------

def riser_margin(mw_ppg: float, water_depth_ft: float,
                 total_tvd_ft: float) -> Dict:
    """Riser margin — the mud weight that maintains the same BHP if the
    riser is displaced to seawater:

        MW' = (0.052×MW×TVD − 0.445×WD) / (0.052×(TVD − WD))
    """
    if total_tvd_ft <= water_depth_ft or total_tvd_ft <= 0:
        return {"error": "TVD must exceed water depth"}
    bhp = CF * mw_ppg * total_tvd_ft
    mw_prime = (bhp - SEAWATER_GRADIENT_PSI_FT * water_depth_ft) / \
        (CF * (total_tvd_ft - water_depth_ft))
    return {
        "bhp_psi": round(bhp, 0),
        "riser_margin_mw_ppg": round(mw_prime, 2),
        "margin_over_current_ppg": round(mw_prime - mw_ppg, 2),
        "note": "MW required if riser displaced to seawater to keep BHP "
                "constant",
    }


def subsea_bop_check(bop_wp_psi: float, max_surface_pressure_psi: float,
                     water_depth_ft: float) -> Dict:
    """Subsea BOP working-pressure adequacy (annular + ram stack)."""
    # bottom-hole pressure at mudline governs the subsea stack load
    load = max_surface_pressure_psi + SEAWATER_GRADIENT_PSI_FT * \
        water_depth_ft
    return {"load_psi": round(load, 0), "bop_wp_psi": bop_wp_psi,
            "ok": bop_wp_psi >= load,
            "margin_psi": round(bop_wp_psi - load, 0)}


# ---------------------------------------------------------------------------
# Completion — barrier model (NORSOK D-010 philosophy)
# ---------------------------------------------------------------------------

def completion_barriers(values: Dict) -> Dict:
    """Two-barrier envelope assessment.

    Primary barrier (downhole): cement + casing, or packer + tubing.
    Secondary barrier (surface): wellhead + X-mas tree + TRSV.
    Each element must be present and verified.
    """
    def _pick(*keys) -> str:
        for k in keys:
            s = str(values.get(k, "") or "").strip()
            if s:
                return s
        return ""

    def _yes(*keys) -> bool:
        return _pick(*keys).lower() in ("yes", "y", "true", "1")

    primary = []
    if _yes("cement_verified", "cement_ok", "cbl_ok"):
        primary.append("Cement sheath verified (CBL/VDL)")
    if _yes("casing_tested", "casing_test_ok"):
        primary.append("Casing pressure-tested")
    if _yes("packer_set", "packer_ok"):
        primary.append("Production packer set & tested")
    if _yes("tubing_tested", "tubing_test_ok"):
        primary.append("Tubing pressure-tested")
    secondary = []
    if _yes("wellhead_ok", "wellhead_tested"):
        secondary.append("Wellhead verified")
    if _yes("tree_ok", "xmas_tree_tested"):
        secondary.append("X-mas tree tested")
    if _yes("trsv_ok", "trsv_tested"):
        secondary.append("TRSV function-tested")
    if _yes("bop_ok", "bop_tested"):
        secondary.append("BOP tested")

    primary_ok = len(primary) >= 2
    secondary_ok = len(secondary) >= 1
    status = "TWO BARRIERS OK" if (primary_ok and secondary_ok) else \
        ("INCOMPLETE" if (primary_ok or secondary_ok) else "NO BARRIER")
    return {"primary": primary, "secondary": secondary,
            "primary_ok": primary_ok, "secondary_ok": secondary_ok,
            "status": status}


def special_wells_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready SPECIAL-WELLS ENGINEERING CHECKS section."""
    def _pick(*keys) -> str:
        for k in keys:
            s = str(values.get(k, "") or "").strip()
            if s:
                return s
        return ""

    def _f(x, d=0.0) -> float:
        try:
            return float(str(x).strip()) if str(x).strip() else d
        except (TypeError, ValueError):
            return d

    op = (operator or "").strip() or "the Operator"
    t_max = _f(_pick("max_temperature", "max_temp_f", "reservoir_temperature_f"))
    dT = _f(_pick("temperature_change", "delta_t", "dT_f"))
    co2 = _f(_pick("co2_pct", "co2"), 0.0)
    h2s = _pick("h2s", "h2s_level") or "No"
    wd = _f(_pick("water_depth"))
    mw = _f(_pick("mud_weight", "mud_weight_ppg", "current_mw", "mw"))
    tvd = _f(_pick("depth", "depth_ft", "td_depth", "td_ft", "total_depth"))
    bop_wp = _f(_pick("bop_wp", "bop_working_pressure"))
    masp = _f(_pick("masp", "max_surface_pressure"))

    L = ["## SPECIAL-WELLS ENGINEERING CHECKS (HPHT / Deepwater / "
         "Completion)", ""]
    n = 0

    if t_max > 0:
        er = elastomer_rating(t_max)
        icon = "✅" if er["ok"] else "⛔"
        L.append(f"- {icon} Elastomer for {t_max:g} °F: "
                 f"**{er['elastomer']}** (rated {er['max_temp_f']} °F, "
                 f"margin {er['margin_f']:,.0f} °F)")
        n += 1
    if dT > 0:
        tap = trapped_annular_pressure(dT)
        L.append(f"- Trapped-annular thermal pressure for ΔT {dT:g} °F: "
                 f"**{tap:,.0f} psi** (β/κ ≈ 106 psi/°F, water-based)")
        n += 1
    if co2 > 0 or h2s:
        mt = metallurgy_suggestion(co2, h2s, t_max or 200)
        L.append(f"- Tubular metallurgy screening (CO2 {co2:g}%, "
                 f"H2S {h2s}): **{mt['metallurgy']}** — {mt['note']}")
        n += 1
    if wd > 0 and mw > 0 and tvd > wd:
        rm = riser_margin(mw, wd, tvd)
        L.append(f"- Riser margin @ water depth {wd:,.0f} ft: MW required "
                 f"if riser displaced to seawater = "
                 f"**{rm['riser_margin_mw_ppg']} ppg** "
                 f"({rm['margin_over_current_ppg']:+.2f} ppg vs current)")
        n += 1
    if bop_wp > 0 and wd > 0 and masp > 0:
        sb = subsea_bop_check(bop_wp, masp, wd)
        icon = "✅" if sb["ok"] else "⛔"
        L.append(f"- {icon} Subsea BOP WP check: load "
                 f"{sb['load_psi']:,.0f} psi vs BOP {bop_wp:,.0f} psi "
                 f"(margin {sb['margin_psi']:,.0f} psi)")
        n += 1
    if _pick("packer_set", "packer_ok", "tree_ok", "trsv_ok"):
        bm = completion_barriers(values)
        L.append(f"- Completion barrier envelope: **{bm['status']}**")
        if bm["primary"]:
            L.append(f"  - Primary: {', '.join(bm['primary'])}")
        if bm["secondary"]:
            L.append(f"  - Secondary: {', '.join(bm['secondary'])}")
        n += 1

    if n == 0:
        return ""
    L.append("")
    L.append(f"*Special-wells checks computed deterministically for {op}; "
             "final selection requires the operator's completion/HPHT "
             "philosophy and vendor qualification data.*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # elastomer: 350 °F -> FKM (rated 400)
    er = elastomer_rating(350)
    assert er["elastomer"] == "FKM / Viton", er
    assert er["ok"] is True
    er2 = elastomer_rating(700)
    assert er2["ok"] is False
    # trapped annular: β/κ = 106.7 psi/°F; ΔT=100 °F -> 10,667 psi
    tap = trapped_annular_pressure(100)
    assert abs(tap - 10666.7) < 1.0, tap
    # riser margin: MW 12, WD 3000, TVD 12000
    #   BHP = 0.052×12×12000 = 7488
    #   MW' = (7488 − 0.445×3000)/(0.052×9000) = 6153/468 = 13.15
    rm = riser_margin(12.0, 3000, 12000)
    assert abs(rm["riser_margin_mw_ppg"] - 13.15) < 0.02, rm
    # subsea BOP: 10000 wp vs 5000+0.445×3000 = 6335 -> OK
    sb = subsea_bop_check(10000, 5000, 3000)
    assert sb["ok"] is True and abs(sb["load_psi"] - 6335) < 1
    # metallurgy
    m1 = metallurgy_suggestion(3.0, "No", 200)
    assert "13Cr" in m1["metallurgy"], m1
    m2 = metallurgy_suggestion(0.1, "Yes", 200)
    assert "NACE" in m2["metallurgy"] or "ISO 15156" in m2["metallurgy"], m2
    # barriers
    bm = completion_barriers({"cement_verified": "Yes",
                              "casing_tested": "Yes", "packer_set": "Yes",
                              "tree_ok": "Yes", "trsv_ok": "Yes"})
    assert bm["status"] == "TWO BARRIERS OK", bm
    bm2 = completion_barriers({})
    assert bm2["status"] == "NO BARRIER", bm2
    md = special_wells_markdown({"max_temperature": "350",
                                 "temperature_change": "100",
                                 "co2_pct": "3", "h2s": "No",
                                 "water_depth": "3000", "mud_weight": "12",
                                 "depth": "12000", "bop_wp": "10000",
                                 "masp": "5000", "packer_set": "Yes",
                                 "tree_ok": "Yes"})
    assert "SPECIAL-WELLS" in md
    assert "Elastomer" in md and "Riser margin" in md
    print("  ✔ special selftest: HPHT/deepwater/completion OK")
    return rm


if __name__ == "__main__":
    _selftest()
    print("engineering_special OK")
