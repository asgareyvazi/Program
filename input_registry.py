# ============================================================================
# CANONICAL INPUT REGISTRY — single source of truth for engineering keys
# File: input_registry.py
# Audit item: "canonical input naming هنوز کامل نشده" — the UI,
# validation, standards, register, consistency and deep-engineering
# engines each resolved keys with their own ad-hoc alias lists.  This
# module centralises:
#   - the canonical key for every physical quantity
#   - all accepted aliases (UI / wizard / legacy templates / DB)
#   - the engineering unit and the realistic range for schema checks
#
# Every engine should resolve values through registry.get() / .as_float()
# so a value entered under ANY name is seen by ALL engines.
# ============================================================================

from typing import Dict, List, Optional, Tuple

# canonical key -> (label, unit, min, max, aliases)
REGISTRY: Dict[str, Tuple[str, str, float, float, Tuple[str, ...]]] = {
    # --- depth (canonical storage: feet) ---
    "depth_ft": ("Total depth", "ft", 0.0, 60000.0,
                 ("depth_ft", "td_depth", "td_ft", "total_depth", "depth",
                  "target_depth", "total_depth_md")),
    "depth_m": ("Total depth", "m", 0.0, 20000.0, ("depth_m", "td_m")),
    "casing_depth_ft": ("Casing depth", "ft", 0.0, 60000.0,
                        ("casing_depth_ft", "casing_depth", "shoe_depth",
                         "csg_depth", "shoe_depth_ft")),
    "shoe_depth_ft": ("Shoe depth", "ft", 0.0, 60000.0,
                      ("shoe_depth_ft", "shoe_depth", "csg_depth")),
    # --- mud / pressures (ppg) ---
    "mud_weight": ("Mud weight", "ppg", 6.0, 22.0,
                   ("mud_weight", "mud_weight_ppg", "current_mw", "mw",
                    "mw1")),
    "pore_pressure": ("Pore pressure", "ppg", 6.0, 20.0,
                      ("pore_pressure_ppg", "pore_pressure",
                       "formation_pressure", "pp_ppg",
                       "formation_pressure_ppg")),
    "fracture_gradient": ("Fracture gradient", "ppg", 8.0, 22.0,
                          ("fracture_gradient_ppg", "fracture_gradient",
                           "fg_ppg", "fg", "frac_gradient")),
    "ecd": ("ECD", "ppg", 6.0, 24.0, ("ecd", "ecd_max")),
    "bop_wp": ("BOP working pressure", "psi", 2000.0, 20000.0,
               ("bop_wp", "bop_working_pressure", "bop_wp_psi",
                "bop_rating")),
    "masp": ("MASP / MAASP", "psi", 0.0, 30000.0,
             ("masp", "maasp", "max_surface_pressure_psi")),
    "sidpp": ("SIDPP", "psi", 0.0, 20000.0, ("sidpp", "sidpip")),
    "sicp": ("SICP", "psi", 0.0, 20000.0, ("sicp", "shut_in_casing_pressure")),
    "kill_mw": ("Kill mud weight", "ppg", 6.0, 24.0,
                ("kill_mw", "kill_fluid_weight", "kmw")),
    "kick_tolerance": ("Kick tolerance", "ppg", 0.0, 8.0,
                       ("kick_tolerance",)),
    # --- hydraulics ---
    "flow_rate": ("Flow rate", "gpm", 50.0, 2500.0,
                  ("flow_rate", "flow_rate_gpm", "q_gpm", "pump_rate",
                   "circ_rate", "circulation_rate")),
    "tfa": ("Bit TFA", "in2", 0.05, 5.0, ("tfa", "tfa_in2", "nozzle_area")),
    "trip_speed": ("Trip speed", "ft/min", 0.0, 200.0,
                   ("trip_speed", "trip_speed_ft_min")),
    "ann_velocity": ("Annular velocity", "ft/min", 0.0, 500.0,
                     ("ann_velocity", "annular_velocity")),
    # --- drilling parameters ---
    "rpm": ("Rotary speed", "rpm", 10.0, 400.0,
            ("rpm", "rotary_speed", "rotate_rpm")),
    "wob": ("Weight on bit", "klbf", 0.0, 120.0,
            ("wob", "wob_klbf")),
    "rop": ("ROP", "ft/hr", 0.0, 300.0, ("rop", "rop_target")),
    "torque": ("Torque", "ft-lb", 0.0, 100000.0, ("torque",)),
    # --- geometry (in) ---
    "hole_size": ("Hole size", "in", 3.0, 40.0,
                  ("hole_size", "hole_id", "hole_diameter", "bit_size")),
    "pipe_od": ("Pipe OD", "in", 1.0, 20.0,
                ("pipe_od", "pipe_size", "drill_pipe_od", "bha_od")),
    "casing_size": ("Casing size", "in", 3.0, 40.0,
                    ("casing_size", "casing_od")),
    "casing_wall": ("Casing wall", "in", 0.1, 3.0,
                    ("casing_wall", "casing_wall_in", "wall_thickness")),
    "casing_yield": ("Casing yield", "psi", 40000.0, 150000.0,
                     ("casing_yield", "casing_yield_psi",
                      "yield_strength")),
    # --- fluids ---
    "yield_point": ("Yield point", "lb/100ft2", 0.0, 100.0,
                    ("yield_point", "mud_yp", "yp_lb100ft2")),
    "plastic_viscosity": ("Plastic viscosity", "cP", 0.0, 150.0,
                          ("plastic_viscosity", "mud_pv", "pv_cp")),
    # --- time & cost ---
    "total_days": ("Total days", "days", 0.0, 1000.0,
                   ("total_days", "duration_days", "duration", "days",
                    "time_days")),
    "total_cost": ("Total cost", "USD", 0.0, 1e12,
                   ("total_cost", "estimated_cost", "afe_total")),
    # --- cement ---
    "excess": ("Excess", "%", 0.0, 100.0, ("excess", "excess_pct")),
    "slurry_yield": ("Slurry yield", "ft3/sk", 0.5, 5.0,
                     ("slurry_yield", "lead_yield", "tail_yield")),
    "woc": ("WOC", "h", 0.0, 96.0, ("woc", "woc_time")),
    # --- HPHT / geomechanics ---
    "temperature_change": ("Temperature change", "F", 0.0, 500.0,
                           ("temperature_change", "delta_t", "dT_f")),
    "max_temperature": ("Max temperature", "F", 100.0, 700.0,
                        ("max_temperature", "max_temp_f",
                         "reservoir_temperature_f")),
    "ucs": ("Rock UCS", "psi", 500.0, 30000.0,
            ("ucs_psi", "rock_ucs")),
    "friction_angle": ("Friction angle", "deg", 10.0, 60.0,
                       ("friction_angle", "friction_angle_deg")),
    "lot_pressure": ("LOT/FIT pressure", "psi", 100.0, 30000.0,
                     ("lot_pressure", "lot_psi")),
    # --- water depth ---
    "water_depth": ("Water depth", "ft", 0.0, 12000.0,
                    ("water_depth",)),
}


def canonical_key(key: str) -> str:
    """Map any alias to its canonical key (identity when unknown)."""
    for canon, (_l, _u, _mn, _mx, aliases) in REGISTRY.items():
        if key in aliases:
            return canon
    return key


def get(values: Dict, *keys: str) -> Optional[str]:
    """First non-empty value among the given keys (any alias works)."""
    for k in keys:
        v = values.get(k)
        if v not in (None, ""):
            return v
    # also resolve through the registry: if the caller passes the
    # canonical key, accept any alias
    canon = canonical_key(keys[0]) if keys else ""
    if canon in REGISTRY:
        _, _, _, _, aliases = REGISTRY[canon]
        for a in aliases:
            v = values.get(a)
            if v not in (None, ""):
                return v
    return None


def as_float(values: Dict, *keys: str, default: float = 0.0) -> float:
    v = get(values, *keys)
    if v is None:
        return default
    try:
        return float(str(v).strip())
    except (TypeError, ValueError):
        return default


def depth_ft(values: Dict) -> float:
    """Canonical depth in feet (explicit ft keys as-is, _m converted)."""
    ft = as_float(values, "depth_ft", "td_depth", "td_ft", "total_depth",
                  "depth", "target_depth")
    if ft:
        return ft
    m = as_float(values, "depth_m", "td_m")
    return m * 3.28084 if m else 0.0


def shoe_ft(values: Dict) -> float:
    ft = as_float(values, "casing_depth_ft", "casing_depth", "shoe_depth",
                  "shoe_depth_ft", "csg_depth")
    if ft:
        return ft
    m = as_float(values, "casing_depth_m", "shoe_depth_m")
    return m * 3.28084 if m else 0.0


def range_for(key: str) -> Optional[Tuple[float, float]]:
    canon = canonical_key(key)
    entry = REGISTRY.get(canon)
    if entry:
        return (entry[2], entry[3])
    return None


def unit_for(key: str) -> str:
    canon = canonical_key(key)
    entry = REGISTRY.get(canon)
    return entry[1] if entry else ""


def label_for(key: str) -> str:
    canon = canonical_key(key)
    entry = REGISTRY.get(canon)
    return entry[0] if entry else key.replace("_", " ").title()


def all_aliases() -> Dict[str, str]:
    """alias -> canonical, for audit and documentation."""
    out = {}
    for canon, (_l, _u, _mn, _mx, aliases) in REGISTRY.items():
        for a in aliases:
            out[a] = canon
    return out


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    # alias resolution across engines
    assert get({"fracture_gradient": "16"}, "fracture_gradient_ppg") == "16"
    assert get({"formation_pressure": "11"}, "pore_pressure_ppg") == "11"
    assert as_float({"current_mw": "12.5"}, "mud_weight") == 12.5
    assert as_float({"flow_rate_gpm": "500"}, "flow_rate") == 500
    # canonical depth
    assert depth_ft({"td_depth": "10000"}) == 10000
    assert abs(depth_ft({"depth_m": "3050"}) - 10006.56) < 1
    # range
    lo, hi = range_for("mud_weight")
    assert (lo, hi) == (6.0, 22.0)
    assert unit_for("tfa") == "in2"
    # canonical mapping
    assert canonical_key("sidpip") == "sidpp"
    assert canonical_key("mud_yp") == "yield_point"
    print("  ✔ input registry selftest: aliases + units + ranges OK")
    return dict(all_aliases())


if __name__ == "__main__":
    _selftest()
    print("input_registry OK")
