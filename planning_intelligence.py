# ============================================================================
# OFFSET WELL INTELLIGENCE + EQUIPMENT COMPATIBILITY + MONTE CARLO TIME
# File: planning_intelligence.py
# Audit items (P1/P2):
#   - Offset Well Intelligence: similarity search over wells + historical
#     NPT/problems/lessons to inform the new well plan.
#   - Equipment Compatibility: BHA/bit/motor/tubular/BOP compatibility check.
#   - Monte Carlo Time: P10/P50/P90 schedule & cost uncertainty.
# ============================================================================

import random
import statistics
from typing import Dict, List, Optional, Tuple

from engineering_units import DrillingConstants


# ---------------------------------------------------------------------------
# 1) OFFSET WELL INTELLIGENCE
# ---------------------------------------------------------------------------

class OffsetIntelligence:
    """Similarity-based offset well matching.

    Uses the operations DB (lessons + NPT) plus optional wells.db to
    recommend relevant offsets and their historical issues.
    """

    def __init__(self):
        self.ops_db = None
        self.wells_db = None
        try:
            from operations_engine import LessonsDatabase
            self.ops_db = LessonsDatabase()
        except Exception:
            pass
        try:
            from well_model import WellDatabase
            self.wells_db = WellDatabase()
        except Exception:
            pass

    def find_offsets(self, field: str = "", well_type: str = "",
                     depth_m: float = 0.0, operation: str = "",
                     limit: int = 5) -> List[Dict]:
        """Return matching offset wells with their lessons/NPT summaries."""
        offsets = []
        if self.wells_db:
            for w in self.wells_db.list_wells():
                score = 0
                if field and w["field_name"] == field:
                    score += 3
                if well_type and w["well_type"] == well_type:
                    score += 2
                if score > 0:
                    offsets.append({"well": w["well_name"], "field": w["field_name"],
                                    "type": w["well_type"], "score": score})
            offsets.sort(key=lambda x: -x["score"])
            offsets = offsets[:limit]
        # enrich with lessons
        for o in offsets:
            if self.ops_db:
                lessons = self.ops_db.lessons_for(field=o["field"],
                                                  operation=operation or "",
                                                  limit=3)
                o["lessons"] = [l["lesson"] for l in lessons]
                npt = self.ops_db.npt_summary()
                o["npt_hr"] = round(npt["total_hr"], 1)
        return offsets

    def offset_markdown(self, field="", well_type="", operation="") -> str:
        offs = self.find_offsets(field, well_type, operation=operation)
        if not offs:
            return ""
        L = ["## OFFSET WELL INTELLIGENCE", "",
             "Similar wells identified from the project database:"]
        for o in offs:
            L.append(f"- **{o['well']}** ({o['type']}, {o['field']}) — "
                     f"similarity {o['score']}")
            for l in o.get("lessons", [])[:2]:
                L.append(f"  - 💡 {l}")
        L.append("")
        return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# 2) EQUIPMENT COMPATIBILITY
# ---------------------------------------------------------------------------

def _size(s: str) -> float:
    s = (s or "").strip().replace('"', '').replace("in", "")
    try:
        if "-" in s and "/" in s:
            w, f = s.split("-", 1)
            n, d = f.split("/", 1)
            return float(w) + float(n) / float(d)
        if "/" in s:
            n, d = s.split("/", 1)
            return float(n) / float(d)
        return float(s)
    except (ValueError, ZeroDivisionError):
        return 0.0


def equipment_compatibility(hole_size: str = "", casing_size: str = "",
                            bha_od: str = "", motor_size: str = "",
                            bit_size: str = "", tubing_size: str = "",
                            liner_size: str = "", bop_wp_psi: float = 0.0,
                            max_surface_pressure_psi: float = 0.0,
                            mud_weight_ppg: float = 0.0,
                            max_mw_for_bop_ppg: float = 0.0) -> List[Dict]:
    """Check equipment compatibility and return findings."""
    out = []
    h = _size(hole_size)
    c = _size(casing_size)
    b = _size(bha_od)
    m = _size(motor_size)
    bit = _size(bit_size)
    t = _size(tubing_size)
    ln = _size(liner_size)

    # bit vs hole
    if h and bit and bit > h:
        out.append({"level": "CRITICAL", "item": "Bit vs Hole",
                    "message": f"Bit ({bit:g}\") larger than hole ({h:g}\").",
                    "hint": "Bit must pass through the hole size."})
    # BHA vs casing pass-through
    if c and b and b > c:
        out.append({"level": "CRITICAL", "item": "BHA vs Casing",
                    "message": f"BHA OD ({b:g}\") cannot pass through "
                               f"casing ID ({c:g}\").",
                    "hint": "Reduce BHA OD or run before casing."})
    # motor vs hole
    if h and m and m > h:
        out.append({"level": "CRITICAL", "item": "Motor vs Hole",
                    "message": f"Motor OD ({m:g}\") exceeds hole size "
                               f"({h:g}\")."})
    # liner vs casing (liner must pass through casing)
    if c and ln and ln > c:
        out.append({"level": "CRITICAL", "item": "Liner vs Casing",
                    "message": f"Liner ({ln:g}\") cannot pass through casing "
                               f"({c:g}\")."})
    # tubing vs liner/casing
    if c and t and t > c:
        out.append({"level": "HIGH", "item": "Tubing vs Casing",
                    "message": f"Tubing ({t:g}\") exceeds casing ({c:g}\")."})
    # BOP pressure
    if bop_wp_psi and max_surface_pressure_psi and bop_wp_psi < max_surface_pressure_psi:
        out.append({"level": "CRITICAL", "item": "BOP Rating",
                    "message": f"BOP WP ({bop_wp_psi:,.0f} psi) < maximum surface "
                               f"pressure ({max_surface_pressure_psi:,.0f} psi)."})
    # BOP vs mud weight (typical 10k BOP handles heavy mud; check if MW>limit)
    if bop_wp_psi and max_mw_for_bop_ppg and mud_weight_ppg and \
            mud_weight_ppg > max_mw_for_bop_ppg:
        out.append({"level": "HIGH", "item": "BOP vs Mud Weight",
                    "message": f"Mud weight ({mud_weight_ppg:g} ppg) exceeds the "
                               f"BOP-rated maximum ({max_mw_for_bop_ppg:g} ppg)."})
    if not out:
        out.append({"level": "INFO", "item": "Compatibility",
                    "message": "No compatibility conflicts detected.",
                    "hint": ""})
    return out


def compatibility_markdown(findings: List[Dict]) -> str:
    if not findings:
        return ""
    L = ["## EQUIPMENT COMPATIBILITY CHECK", "",
         "| Severity | Item | Finding |", "|---|---|---|"]
    for f in findings:
        L.append(f"| **{f['level']}** | {f['item']} | {f['message']} |")
    L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------
# 3) MONTE CARLO TIME (P10/P50/P90)
# ---------------------------------------------------------------------------

def monte_carlo_time(duration_days: float, p10_days: float, p90_days: float,
                     npt_pct: float = 10.0, n_sims: int = 2000,
                     seed: int = 42) -> Dict:
    """P10/P50/P90 schedule from a triangular distribution.

    duration_days: deterministic base (P50 estimate)
    p10_days / p90_days: optimistic / pessimistic bounds
    npt_pct: expected NPT percentage applied as a shift
    """
    rng = random.Random(seed)
    if p90_days <= p10_days:
        p90_days = duration_days * 1.3
        p10_days = duration_days * 0.8
    sims = []
    for _ in range(n_sims):
        # triangular distribution with mode = duration
        u = rng.random()
        lo, hi, mode = p10_days, p90_days, duration_days
        if u < (mode - lo) / (hi - lo):
            v = lo + (u * (hi - lo) * (mode - lo)) ** 0.5
        else:
            v = hi - ((1 - u) * (hi - lo) * (hi - mode)) ** 0.5
        # NPT shift
        npt = rng.uniform(0, npt_pct * 2) / 100.0
        sims.append(v * (1 + npt))
    sims.sort()
    p10 = sims[int(0.10 * n_sims)]
    p50 = sims[int(0.50 * n_sims)]
    p90 = sims[int(0.90 * n_sims)]
    return {"p10_days": round(p10, 1), "p50_days": round(p50, 1),
            "p90_days": round(p90, 1), "mean_days": round(statistics.mean(sims), 1),
            "n_sims": n_sims}


def monte_carlo_cost(total_cost_usd: float, p10_pct: float = -10,
                     p90_pct: float = 25, n_sims: int = 2000,
                     seed: int = 7) -> Dict:
    """P10/P50/P90 cost from a triangular distribution around the AFE."""
    rng = random.Random(seed)
    sims = []
    for _ in range(n_sims):
        u = rng.random()
        lo = total_cost_usd * (1 + p10_pct / 100)
        hi = total_cost_usd * (1 + p90_pct / 100)
        mode = total_cost_usd
        if u < (mode - lo) / (hi - lo):
            v = lo + (u * (hi - lo) * (mode - lo)) ** 0.5
        else:
            v = hi - ((1 - u) * (hi - lo) * (hi - mode)) ** 0.5
        sims.append(v)
    sims.sort()
    return {"p10_usd": round(sims[int(0.10 * n_sims)], 0),
            "p50_usd": round(sims[int(0.50 * n_sims)], 0),
            "p90_usd": round(sims[int(0.90 * n_sims)], 0),
            "mean_usd": round(statistics.mean(sims), 0)}


def monte_carlo_markdown(time_res: Dict, cost_res: Dict) -> str:
    L = ["## SCHEDULE & COST UNCERTAINTY (MONTE CARLO)", "",
         "| Percentile | Duration (days) | Cost (USD) |", "|---|---:|---:|"]
    L.append(f"| **P10** (optimistic) | {time_res['p10_days']:,.1f} | "
             f"{cost_res['p10_usd']:,.0f} |")
    L.append(f"| **P50** (base) | {time_res['p50_days']:,.1f} | "
             f"{cost_res['p50_usd']:,.0f} |")
    L.append(f"| **P90** (pessimistic) | {time_res['p90_days']:,.1f} | "
             f"{cost_res['p90_usd']:,.0f} |")
    L.append("")
    L.append(f"*{time_res['n_sims']} simulations, triangular distribution.*")
    L.append("")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    t = monte_carlo_time(114, 95, 140, npt_pct=10)
    print("time:", t)
    c = monte_carlo_cost(17_500_000)
    print("cost:", c)
    comp = equipment_compatibility(hole_size='12-1/4"', casing_size='9-5/8"',
                                   bha_od='9-1/2"', bit_size='12-1/4"',
                                   bop_wp_psi=10000,
                                   max_surface_pressure_psi=5000)
    print("compat:", [f["level"] for f in comp])
    oi = OffsetIntelligence()
    print("offsets:", oi.find_offsets(field="F"))
