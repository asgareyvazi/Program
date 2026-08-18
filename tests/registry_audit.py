# ============================================================================
# INPUT REGISTRY AUDIT — verify every engine resolves through one registry
# File: tests/registry_audit.py
#
# Confirms:
#   - every alias in the registry resolves to the same canonical value
#     across validation / standards / register / consistency
#   - units and ranges are consistent
#   - depth is canonical in feet everywhere (no double conversion)
#
# Run:  LD_LIBRARY_PATH=/tmp/glstubs PYTHONPATH=. QT_QPA_PLATFORM=offscreen \
#       python3 tests/registry_audit.py
# ============================================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_PASS = 0
_FAIL = 0


def ok(cond, label, extra=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
    else:
        _FAIL += 1
        print(f"  ✘ {label} {extra}")


def test_registry_resolution():
    print("\n[1] REGISTRY — alias resolution")
    from input_registry import (get, as_float, canonical_key, depth_ft,
                                shoe_ft, range_for, unit_for, all_aliases)
    aliases = all_aliases()
    ok(len(aliases) >= 80, f"alias count >= 80 (got {len(aliases)})")
    # representative resolutions
    ok(get({"fracture_gradient": "16"}, "fracture_gradient_ppg") == "16",
       "fracture_gradient alias")
    ok(get({"formation_pressure": "11"}, "pore_pressure_ppg") == "11",
       "formation_pressure alias")
    ok(as_float({"current_mw": "12.5"}, "mud_weight") == 12.5,
       "current_mw alias")
    ok(as_float({"q_gpm": "500"}, "flow_rate") == 500, "q_gpm alias")
    ok(canonical_key("sidpip") == "sidpp", "sidpip canonical")
    ok(canonical_key("mud_yp") == "yield_point", "mud_yp canonical")
    ok(range_for("mud_weight") == (6.0, 22.0), "MW range")
    ok(unit_for("tfa") == "in2", "TFA unit")
    ok(abs(depth_ft({"depth_m": "3050"}) - 10006.56) < 1,
       "depth_m -> ft canonical")
    ok(shoe_ft({"shoe_depth": "8000"}) == 8000, "shoe ft")


def test_engine_consistency():
    print("\n[2] ENGINES — same value seen by all")
    from validation_engine import validate_well_data
    from standards_engine import compliance_matrix
    from engineering_consistency import consistency_check
    from engineering_register import compute_register
    vals = {"fracture_gradient": "16", "mud_weight": "17",
            "td_depth": "10000", "casing_depth": "8000",
            "bop_wp": "10000", "masp": "2000", "flow_rate_gpm": "500",
            "hole_size": "12.25", "pipe_od": "5", "yield_point": "20",
            "plastic_viscosity": "25", "tfa": "0.3312", "dp_id": "4.276",
            "total_days": "45", "total_cost": "12000000"}
    # validation sees fracture_gradient
    fs = validate_well_data(vals)
    ok("ENG-MW-FG" in [f.code for f in fs], "validation MW>FG via alias")
    # standards sees it
    rows = compliance_matrix(vals)
    md = [r for r in rows if r["rule_id"] == "STD-MD-002"][0]
    ok(md["status"] == "FAIL" or md["status"] == "CHECK",
       "standards ECD/FG via alias", md["status"])
    # register computes with canonical depth
    reg = compute_register(vals)
    hyd = [r for r in reg if "ydrostatic" in r["param"]]
    ok(hyd and hyd[0]["result"] == "8,840", "register hydrostatic 17ppg@10000ft",
       str(hyd[:1]))
    # consistency
    f = consistency_check("| Fracture Gradient | 16 ppg |\n| Mud Weight | "
                          "17 ppg |")
    ok(any(x["code"] == "CONS-MW-FG" for x in f), "consistency via alias")


def test_no_double_conversion():
    print("\n[3] DEPTH — no double ft->m->ft conversion")
    from input_registry import depth_ft
    from validation_engine import validate_well_data
    from engineering_register import compute_register
    ok(depth_ft({"td_depth": "10000"}) == 10000, "td_depth is ft")
    # casing 12000 > TD 10000 in FEET must flag (previously the ft value
    # was sometimes treated as metres -> 39370 ft -> no flag)
    fs = validate_well_data({"td_depth": "10000", "casing_depth": "12000"})
    ok("LOGIC-CASING-TD" in [f.code for f in fs],
       "casing>TD flagged with feet")
    # register: kill mud weight uses canonical feet
    reg = compute_register({"mud_weight": "12", "sidpp": "400",
                            "td_depth": "10000"})
    kmw = [r for r in reg if "kill" in r["param"].lower()]
    ok(kmw and "12.77" in kmw[0]["result"], "KMW uses canonical ft",
       str(kmw[:1]))


if __name__ == "__main__":
    test_registry_resolution()
    test_engine_consistency()
    test_no_double_conversion()
    print("\n" + "=" * 60)
    print(f"RESULT: {_PASS} passed, {_FAIL} failed")
    sys.exit(1 if _FAIL else 0)
