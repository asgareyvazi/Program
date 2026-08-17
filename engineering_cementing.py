# ============================================================================
# CEMENTING ENGINEERING
# File: engineering_cementing.py
# Audit items (P1):
#   - Cementing: the audit asked for UCA / SGS / gas-migration models
#
# Implements:
#   - Annular & slurry volumes with excess
#   - Sacks & mix-water from slurry yield (API RP 10B / 10A conventions)
#   - UCA-style strength development estimate (exponential approach)
#   - Static gel strength (SGS) development (power-law, 10-min gel)
#   - Gas-migration risk screening (semi-quantitative, API RP 10B-2 /
#     field practice indicators)
# All deterministic and reference-tested.
# ============================================================================

import math
from typing import Dict, List, Optional

BBL_PER_FT3 = 5.6146
GAL_PER_BBL = 42.0


def annular_volume_bbl(hole_in: float, pipe_in: float, length_ft: float,
                       excess_pct: float = 0.0) -> float:
    """Annular volume: (D²−d²)/1029.4 × L, with excess."""
    if hole_in <= pipe_in:
        return 0.0
    v = (hole_in ** 2 - pipe_in ** 2) / 1029.4 * length_ft
    return v * (1.0 + excess_pct / 100.0)


def open_hole_volume_bbl(hole_in: float, length_ft: float,
                         excess_pct: float = 0.0) -> float:
    v = hole_in ** 2 / 1029.4 * length_ft
    return v * (1.0 + excess_pct / 100.0)


def slurry_volume_with_excess(lead_bbl: float = 0.0, tail_bbl: float = 0.0,
                              excess_pct: float = 0.0,
                              displacement_bbl: float = 0.0) -> Dict:
    """Total cement slurry volume: (lead + tail) with excess + optional
    displacement (shoe track / spacer interface)."""
    cem = (lead_bbl + tail_bbl) * (1.0 + excess_pct / 100.0)
    return {"cement_bbl": round(cem, 1),
            "displacement_bbl": round(displacement_bbl, 1),
            "total_bbl": round(cem + displacement_bbl, 1)}


def sacks_required(slurry_bbl: float, yield_ft3_per_sk: float) -> float:
    """Sacks = slurry volume (ft³) / yield (ft³/sk)."""
    if yield_ft3_per_sk <= 0:
        return 0.0
    return slurry_bbl * BBL_PER_FT3 / yield_ft3_per_sk


def mix_water_bbl(sacks: float, water_gal_per_sk: float) -> float:
    """Mix water = sacks × gal/sk (bbl)."""
    return sacks * water_gal_per_sk / GAL_PER_BBL


def displacement_volume_bbl(pipe_cap_bbl_ft: float, shoe_track_ft: float,
                            inner_string_id_in: float = 0.0,
                            string_len_ft: float = 0.0) -> float:
    """Displacement: shoe track + (optionally) inner string volume above
    the shoe to the surface."""
    v = pipe_cap_bbl_ft * shoe_track_ft
    if inner_string_id_in > 0 and string_len_ft > 0:
        v += inner_string_id_in ** 2 / 1029.4 * string_len_ft
    return v


# ---------------------------------------------------------------------------
# Strength & gel development
# ---------------------------------------------------------------------------

def uca_strength_estimate(hours: float, final_strength_psi: float = 3000.0,
                          tau_h: float = 10.0) -> float:
    """UCA-style compressive-strength development (exponential approach):

        S(t) = S_final × (1 − exp(−t/τ))
    with τ the characteristic time (hours).  This is a screening estimate
    of API RP 10B-2 UCA behaviour — the actual test on the job slurry is
    the design basis.
    """
    if hours <= 0:
        return 0.0
    return final_strength_psi * (1.0 - math.exp(-hours / tau_h))


def woc_guidance(strength_psi: float) -> str:
    """Wait-on-cement guidance from the estimated compressive strength
    (API RP 10B-2 / field practice)."""
    if strength_psi >= 2000:
        return "Full operations may resume (≥ 2000 psi estimated)."
    if strength_psi >= 500:
        return "Light operations acceptable (≥ 500 psi); no heavy loads."
    if strength_psi >= 200:
        return ("Wait — strength building (200–500 psi); pressure tests "
                "not yet recommended.")
    return "Continue WOC — strength below 200 psi."


def static_gel_strength(minutes: float, sgs_10min_lb100ft2: float = 100.0,
                        exponent: float = 0.25) -> float:
    """Static gel strength development (power law):

        SGS(t) = SGS(10 min) × (t/10)^n
    Typical n ≈ 0.2–0.3 for field muds (screening estimate)."""
    if minutes <= 0:
        return 0.0
    return sgs_10min_lb100ft2 * (minutes / 10.0) ** exponent


# ---------------------------------------------------------------------------
# Gas migration risk screening
# ---------------------------------------------------------------------------

def gas_migration_risk(annular_gap_in: float, woc_hours: float,
                       static_time_h: float = 4.0,
                       slurry_fluid_loss_ml30: float = 100.0,
                       displacement_efficiency_ok: bool = True) -> Dict:
    """Semi-quantitative gas-migration risk screening.

    Indicators (API RP 10B-2 / field practice):
      - narrow annulus (< 1.5 in) raises risk
      - short WOC (< 12 h) raises risk
      - long static time before gelation raises risk
      - high fluid loss (> 50 ml/30min) raises risk
      - poor displacement raises risk
    Returns score (0..1), level and key factors.
    """
    score = 0.0
    factors = []
    if annular_gap_in < 1.5:
        score += 0.3
        factors.append(f"narrow annulus ({annular_gap_in:g} in)")
    elif annular_gap_in < 2.5:
        score += 0.15
        factors.append(f"moderate annulus ({annular_gap_in:g} in)")
    if woc_hours < 12:
        score += 0.25
        factors.append(f"short WOC ({woc_hours:g} h)")
    elif woc_hours < 24:
        score += 0.1
        factors.append("WOC < 24 h")
    if static_time_h > 8:
        score += 0.2
        factors.append(f"long static time ({static_time_h:g} h)")
    elif static_time_h > 4:
        score += 0.1
    if slurry_fluid_loss_ml30 > 50:
        score += 0.15
        factors.append(f"high fluid loss ({slurry_fluid_loss_ml30:g} "
                       "ml/30min)")
    if not displacement_efficiency_ok:
        score += 0.1
        factors.append("poor displacement / channeling risk")
    score = min(1.0, score)
    level = "LOW" if score < 0.3 else ("MEDIUM" if score < 0.6 else "HIGH")
    return {"score": round(score, 2), "level": level, "factors": factors,
            "annular_gap_in": annular_gap_in, "woc_hours": woc_hours}


# ---------------------------------------------------------------------------
# Markdown section
# ---------------------------------------------------------------------------

def cementing_markdown(values: Dict, operator: str = "") -> str:
    """Word-ready CEMENTING ENGINEERING CHECKS section."""
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
    hole = _f(_pick("hole_size", "hole_id", "hole_diameter"))
    pipe = _f(_pick("pipe_od", "pipe_size", "casing_size"))
    csg_len = _f(_pick("cemented_length", "cement_interval_ft"))
    excess = _f(_pick("excess", "excess_pct"))
    lead_v = _f(_pick("lead_volume"))
    tail_v = _f(_pick("tail_volume"))
    lead_y = _f(_pick("lead_yield", "slurry_yield"))
    tail_y = _f(_pick("tail_yield", "slurry_yield"))
    water_sk = _f(_pick("water_per_sack", "mix_water"))
    woc = _f(_pick("woc", "woc_time"), 8.0)
    fd_loss = _f(_pick("fluid_loss", "fluid_loss_ml30"), 100.0)
    static_h = _f(_pick("static_time", "static_time_h"), 4.0)
    disp_ok = _pick("displacement_efficiency", "displacement_ok") != "No"

    L = ["## CEMENTING ENGINEERING CHECKS", ""]
    checks = 0

    # volumes & sacks
    if hole > pipe and csg_len > 0:
        ann = annular_volume_bbl(hole, pipe, csg_len, excess)
        L.append(f"- Annular volume (D−d = {hole - pipe:g} in, "
                 f"{csg_len:,.0f} ft, +{excess:g}% excess): "
                 f"**{ann:,.0f} bbl**")
        checks += 1
        if lead_y > 0:
            sk = sacks_required(ann, lead_y)
            L.append(f"- Estimated sacks @ yield {lead_y:g} ft³/sk: "
                     f"**{sk:,.0f} sk**")
            if water_sk > 0:
                L.append(f"- Mix water: **{mix_water_bbl(sk, water_sk):,.0f} "
                         f"bbl**")
            checks += 1
    if lead_v > 0 or tail_v > 0:
        sv = slurry_volume_with_excess(lead_v, tail_v, excess)
        L.append(f"- Slurry volume: lead {lead_v:g} + tail {tail_v:g} bbl "
                 f"(+{excess:g}%) = **{sv['cement_bbl']} bbl**")
        checks += 1

    # strength / WOC
    s12 = uca_strength_estimate(12.0)
    s24 = uca_strength_estimate(24.0)
    L.append(f"- UCA-style strength estimate: **{s12:,.0f} psi @ 12 h**, "
             f"**{s24:,.0f} psi @ 24 h** (exponential model, screening)")
    L.append(f"- WOC guidance @ 12 h: {woc_guidance(s12)}")
    checks += 1

    # gas migration
    if hole > pipe:
        gm = gas_migration_risk(hole - pipe, woc, static_h, fd_loss, disp_ok)
        icon = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}.get(gm["level"],
                                                              "•")
        L.append(f"- Gas-migration risk screening: {icon} "
                 f"**{gm['level']}** (score {gm['score']})")
        if gm["factors"]:
            L.append(f"  - Factors: {', '.join(gm['factors'])}")
        checks += 1

    # gel
    sgs = static_gel_strength(static_h * 60.0)
    L.append(f"- Static gel strength estimate after {static_h:g} h: "
             f"**{sgs:,.0f} lb/100ft²** (power-law from 10-min gel)")
    checks += 1

    if checks == 0:
        return ""
    L.append("")
    L.append(f"*Cementing checks computed deterministically for {op}; the "
             "job design must be confirmed by the cementing service "
             "company with UCA/SGS testing of the actual slurry (API RP "
             "10B-2).*")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # annulus 8.5×5 × 1000 ft, 30% excess: 0.04590×1000×1.3 = 59.67 bbl
    av = annular_volume_bbl(8.5, 5.0, 1000, 30)
    assert abs(av - 59.67) < 0.1, av
    # sacks: 59.67 bbl × 5.6146 / 1.18 = 283.9
    sk = sacks_required(av, 1.18)
    assert abs(sk - 283.9) < 0.5, sk
    # mix water: 283.9 × 5.2 gal / 42 = 35.1 bbl
    mw = mix_water_bbl(sk, 5.2)
    assert abs(mw - 35.15) < 0.1, mw
    # UCA: monotonic, asymptote
    assert uca_strength_estimate(0) == 0
    assert uca_strength_estimate(100) < 3000
    assert uca_strength_estimate(100) > uca_strength_estimate(24)
    # SGS monotonic
    assert static_gel_strength(60) > static_gel_strength(10)
    # gas migration: narrow gap + short WOC -> HIGH; wide + long -> LOW
    g1 = gas_migration_risk(0.8, 4)
    g2 = gas_migration_risk(3.5, 36, static_time_h=2,
                            slurry_fluid_loss_ml30=20)
    assert g1["level"] == "HIGH", g1
    assert g2["level"] == "LOW", g2
    md = cementing_markdown({"hole_size": "8.5", "pipe_od": "5",
                             "cemented_length": "1000", "excess": "30",
                             "lead_yield": "1.18", "woc": "8"})
    assert "CEMENTING" in md
    assert "bbl" in md and "psi @ 12 h" in md
    print("  ✔ cementing selftest: volumes/sacks/UCA/SGS/gas-migration OK")
    return av


if __name__ == "__main__":
    _selftest()
    print("engineering_cementing OK")
