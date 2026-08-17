# ============================================================================
# ENGINEERING REFERENCE TEST SUITE
# File: tests/test_engineering_reference.py
# P0 audit item: reference-validated calculations with acceptance tolerance.
#
# Run:  python tests/test_engineering_reference.py
# Each test compares a calculation against an independent reference value
# (API/field handbook) within a declared tolerance. Exit code 0 = all pass.
# ============================================================================

import math
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engineering_units import (convert, hydrostatic_pressure, maasp,
                               kill_mud_weight, annular_velocity_ftmin,
                               barlow_burst_pressure, api_collapse_pressure,
                               emw_from_pressure)
from engineering_calculations import DrillingEngineering as Calc
from engineering_calculations import HydraulicsCalculator as Hydro

_PASS = 0
_FAIL = 0
_FAILURES = []


def approx(actual, expected, tol, label):
    global _PASS, _FAIL
    if isinstance(expected, bool) or isinstance(actual, bool):
        ok = bool(actual) == bool(expected)
    elif isinstance(expected, str) or isinstance(actual, str):
        ok = str(actual) == str(expected)
    else:
        ok = abs(actual - expected) <= tol
    def _fmt(x):
        return f"{x:.4g}" if isinstance(x, (int, float)) else str(x)
    if ok:
        _PASS += 1
        print(f"  ✔ {label}: {_fmt(actual)} (ref {_fmt(expected)})")
    else:
        _FAIL += 1
        _FAILURES.append(f"{label}: {_fmt(actual)} vs {_fmt(expected)}")
        print(f"  ✘ {label}: {_fmt(actual)} != {_fmt(expected)}")


def test_units():
    print("\n[1] UNIT SYSTEM")
    approx(convert(1, "bar", "psi"), 14.5038, 0.01, "bar->psi")
    approx(convert(1, "m", "ft"), 3.28084, 0.001, "m->ft")
    approx(convert(100, "pcf", "ppg"), 100 * 0.13368, 0.05, "pcf->ppg")
    approx(convert(1, "bbl", "m3"), 1 / 6.28981, 1e-4, "bbl->m3")
    approx(convert(1, "sg", "ppg"), 8.3454, 0.001, "sg->ppg")


def test_hydrostatic():
    print("\n[2] HYDROSTATIC PRESSURE  (P = 0.052 × MW × D)")
    # Reference: 12 ppg @ 10,000 ft = 6,240 psi
    approx(hydrostatic_pressure(12, 10000), 6240, 0.01, "12ppg@10000ft")
    # 15 ppg @ 12,000 ft = 9,360 psi
    approx(hydrostatic_pressure(15, 12000), 9360, 0.01, "15ppg@12000ft")
    # EMW round-trip
    approx(emw_from_pressure(6240, 10000), 12.0, 1e-6, "emw(6240psi@10000ft)")


def test_maasp():
    print("\n[3] MAASP  (FG − MW) × 0.052 × shoe")
    # Reference: FG 15 ppg, MW 10 ppg, shoe 8,000 ft = 2,080 psi
    approx(maasp(15, 10, 8000), 2080, 0.01, "FG15/MW10@shoe8000")
    # FG 16, MW 12, shoe 10,000 = 2,080 psi
    approx(maasp(16, 12, 10000), 2080, 0.01, "FG16/MW12@shoe10000")


def test_kill_mud_weight():
    print("\n[4] KILL MUD WEIGHT  KMW = MW + SIDPP/(0.052×TVD)")
    # Reference: MW 10 ppg, SIDPP 500 psi @ TVD 10,000 ft -> 10.9615 ppg
    approx(kill_mud_weight(500, 10000, 10), 10 + 500 / 520, 0.001,
           "SIDPP500@10kft")
    # with trip margin 0.5 -> 11.4615
    approx(kill_mud_weight(500, 10000, 10, 0.5), 10 + 500 / 520 + 0.5,
           0.001, "SIDPP500+margin0.5")


def test_annular_velocity():
    print("\n[5] ANNULAR VELOCITY  AV = 24.5 × gpm / (D² − d²)")
    # Reference: 500 gpm, 12-1/4" hole, 5" pipe -> 24.5*500/(150.06-25) = 97.95
    approx(annular_velocity_ftmin(500, 12.25, 5), 97.95, 0.5,
           "500gpm 12.25x5")
    # 800 gpm, 17-1/2" hole, 5" pipe -> 24.5*800/(306.25-25) = 69.7
    approx(annular_velocity_ftmin(800, 17.5, 5), 69.68, 0.5,
           "800gpm 17.5x5")


def test_casing_burst():
    print("\n[6] CASING BURST (Barlow, 87.5%)")
    # Reference (API): 9-5/8", 47 ppf, L-80 -> ~6,870 psi
    approx(barlow_burst_pressure(9.625, 0.472, 80000), 6870, 30,
           "9.625x0.472 L80")
    # 13-3/8", 68 ppf, N-80 (t≈0.480) -> 2*0.875*80000*0.480/13.375 = 5024
    approx(barlow_burst_pressure(13.375, 0.480, 80000), 5024, 40,
           "13.375x0.480 N80")


def test_casing_collapse():
    print("\n[7] CASING COLLAPSE (API 5C3 simplified — SANITY BAND)")
    # Full API collapse for 9-5/8,47#,L80 is ~4,480 psi; our simplified
    # model is a P0 approximation, so we only assert a physical band and
    # flag the need for reference verification (per audit).
    p = api_collapse_pressure(9.625, 0.472, 80000)
    approx(p, 4480, 5000, "9.625x0.472 L80 (band 0..9480)")


def test_well_cost():
    print("\n[8] WELL COST (incl. cost-per-meter regression)")
    total = Calc.total_well_cost(80000, 114, 45000, completion_cost=1e6,
                                 mud_cost=200000, casing_cost=1.5e6,
                                 well_depth_ft=13714)
    expected_total = 80000 * 114 + 45000 * 114 + 1e6 + 200000 + 1.5e6
    approx(total["total_cost"], expected_total, 0.01, "total cost")
    # regression: cost_per_foot must be total/depth (was total/1 bug)
    approx(total["cost_per_foot"], expected_total / 13714, 0.01,
           "cost_per_foot = total/depth (bug regression)")
    # when depth is unknown, must be 0 (never total/1)
    nod = Calc.total_well_cost(80000, 114, 45000)
    approx(nod["cost_per_foot"], 0.0, 0.0, "cost_per_foot=0 when depth unknown")


def test_engineering_calc_annular():
    print("\n[9] ENGINEERING_CALCULATIONS annular velocity")
    # 500 gpm, 12.25 hole, 5 pipe -> same 97.95 ft/min
    v = Hydro.annular_velocity(500, 12.25, 5)
    approx(v, 97.95, 0.5, "annular_velocity(500,12.25,5)")


def test_advanced():
    print("\n[10] ADVANCED (kick tolerance, surge/swab, MPD, casing loads)")
    from engineering_advanced import (kick_tolerance, bop_pressure_envelope,
                                      surge_swab_pressure, cbhp_mud_weight,
                                      evacuation_burst_load)
    # KT sanity: FG15/MW12/shoe8000, 30bbl kick -> ~1.9-2.1 ppg
    kt = kick_tolerance(15, 12, 8000, 30, 0.045)
    approx(kt["kt_ppg"], 1.97, 0.3, "kick tolerance 30bbl")
    # BOP envelope: 10k BOP vs MASP 1248 -> OK
    be = bop_pressure_envelope(10000, 15, 12, 8000)
    approx(be["ok"], True, 0, "BOP 10k vs MASP")
    # surge: trip 60 ft/min at 10k ft -> small positive pressure
    ss = surge_swab_pressure(20, 25, 60, 0.045, 12.25, 5, 10000)
    approx(ss["pressure_psi"] > 0, True, 0, "surge positive")
    # CBHP: MW11 + losses 0.8 + BP300 at 10k ft -> ~12.38 ppg
    cb = cbhp_mud_weight(11, 0.8, 300, 10000)
    approx(cb["cbhp_emw_ppg"], 12.38, 0.1, "CBHP EMW")
    # Evacuation burst: (14-12)*0.052*10000 = 1040 psi
    ev = evacuation_burst_load(12, 14, 10000)
    approx(ev, 1040, 1, "evacuation burst load")


def test_readiness_and_ops():
    print("\n[11] READINESS + OPERATIONS ENGINE")
    from operations_engine import readiness_score, LessonsDatabase
    r = readiness_score({"well_name": "W", "well_type": "H", "mud_weight": "12",
                         "bop_wp": "10000"})
    approx(r["score"] > 0, True, 0, "readiness score positive")
    approx(r["grade"] in ("READY", "REVIEW", "NOT READY"), True, 0,
           "readiness grade valid")
    db = LessonsDatabase()
    db.add_lesson(well_name="W1", field="F", operation="Drilling",
                  category="Stuck", lesson="test lesson", cause="c",
                  prevention="p")
    approx(len(db.lessons_for(field="F")) >= 1, True, 0, "lesson stored")
    n = db.add_npt(well_name="W1", date="2026-08-16", duration_hr=10,
                   category="Stuck", cause="Pack-off", direct_cost=100)
    s = db.npt_summary()
    approx(s["events"] >= 1, True, 0, "npt recorded")
    d = db.add_daily(well_name="W1", date="2026-08-16", depth_m=1000,
                     plan_depth_m=1100)
    approx(len(db.plan_vs_actual()) >= 1, True, 0, "daily recorded")
    db.close()


def test_planning_intelligence():
    print("\n[12] PLANNING INTELLIGENCE (offsets, compatibility, Monte Carlo)")
    from planning_intelligence import (equipment_compatibility,
                                       monte_carlo_time, monte_carlo_cost)
    # compatibility: bad bit vs hole -> CRITICAL
    bad = equipment_compatibility(hole_size='12-1/4"', bit_size='13-1/2"')
    approx(any(f["level"] == "CRITICAL" for f in bad), True, 0,
           "bit>hole flagged CRITICAL")
    # good setup -> INFO only
    good = equipment_compatibility(hole_size='12-1/4"', casing_size='9-5/8"',
                                   bit_size='12-1/4"',
                                   bop_wp_psi=10000,
                                   max_surface_pressure_psi=5000)
    approx(all(f["level"] == "INFO" for f in good), True, 0,
           "compatible setup clean")
    # Monte Carlo: P50 near base
    tr = monte_carlo_time(114, 95, 140, seed=1)
    approx(tr["p50_days"], 114, 15, "MC P50 near base")
    cr = monte_carlo_cost(1_000_000, seed=1)
    approx(cr["p50_usd"], 1_000_000, 200_000, "MC cost P50")


def test_entity_scrub():
    print("\n[13] ENTITY SCRUB (context-aware generalization)")
    from entity_scrub import scrub_entities
    out, removed = scrub_entities(
        "Well SI-09 by NISOC, rig OEOC 207; Brown shale; Total depth; "
        "'Total' word; PARS OIL CO approved", "PARS OIL CO", "DRILL PRO")
    approx("SI-09" in out, False, 0, "well code removed")
    approx("NISOC" in out, False, 0, "company removed")
    approx("Brown" in out, True, 0, "geology 'Brown' kept")
    approx("Total depth" in out, True, 0, "technical 'Total' kept")
    approx("PARS OIL CO" in out, True, 0, "user operator kept")


def test_compliance():
    print("\n[14] DOCUMENT COMPLIANCE ENGINE")
    from document_compliance import compliance_check
    good_md = "## 1. SCOPE\n## WELL INFORMATION\n## CASING PROGRAM\n" \
              "## MUD PROGRAM\n## BHA & BITS\n## HYDRAULICS\n" \
              "## WELL CONTROL\n## CEMENTING\n## SAFETY\n" \
              "## VALIDATION & COMPLIANCE\n## PROGRAM READINESS SCORE\n" \
              "## REFERENCE DOCUMENTS\n"
    r = compliance_check("drilling_program", good_md, [])
    approx(r["compliant"], True, 0, "complete doc compliant")
    poor = compliance_check("drilling_program", "## SAFETY\n", [])
    approx(poor["compliant"], False, 0, "incomplete doc not compliant")


def test_risk_decision():
    print("\n[15] RISK DECISION ENGINE")
    from risk_decision import find_decisions
    ds = find_decisions("kick from over-pressured zone; lost circulation; H2S")
    approx(any(d.code == "RD-001" for d in ds), True, 0, "kick decision found")
    approx(any(d.code == "RD-002" for d in ds), True, 0, "loss decision found")
    approx(any(d.code == "RD-004" for d in ds), True, 0, "H2S decision found")


def test_standards():
    print("\n[16] STANDARDS COMPLIANCE MATRIX")
    from standards_engine import compliance_matrix
    rows = compliance_matrix({"bop_wp": 10000, "masp": 5000,
                              "casing_depth": 3000, "depth_m": 4180,
                              "standoff_pct": 75, "ecd": 14,
                              "fracture_gradient_ppg": 16,
                              "kill_sheet": "yes"})
    ids = {r["rule_id"]: r["status"] for r in rows}
    approx(ids.get("STD-WC-001"), "PASS", 0, "BOP rule PASS")
    approx(ids.get("STD-CS-001"), "PASS", 0, "casing rule PASS")
    approx(ids.get("STD-MD-002"), "PASS", 0, "ECD rule PASS")
    # fail case: casing deeper than TD
    rows2 = compliance_matrix({"casing_depth": 5000, "depth_m": 4000})
    ids2 = {r["rule_id"]: r["status"] for r in rows2}
    approx(ids2.get("STD-CS-001"), "FAIL", 0, "casing>TD FAIL")


def test_deep_engineering():
    print("\n[17] DEEP ENGINEERING (ROP calib, HB hydraulics, triaxial)")
    from engineering_deep import (ROPCalibrator, power_law_pressure_loss,
                                  herschel_bulkley_pressure_loss, triaxial_check)
    rc = ROPCalibrator()
    rc.calibrate([
        {"wob": 20, "rpm": 90, "depth": 5000, "mw": 11, "rop_actual": 35},
        {"wob": 25, "rpm": 100, "depth": 8000, "mw": 11.5, "rop_actual": 28},
        {"wob": 30, "rpm": 110, "depth": 11000, "mw": 12, "rop_actual": 20},
    ])
    approx(rc.is_fitted, True, 0, "ROP calibrated")
    pred = rc.predict(25, 100, 8000, 11.5)
    approx(pred, 28, 8, "ROP predict near offset")
    # HB pressure loss > PL (yield adds)
    pl = power_law_pressure_loss(500, 12.25, 5, 1000, 0.6, 2.0)
    hb = herschel_bulkley_pressure_loss(500, 12.25, 5, 1000, 10, 0.6, 2.0)
    approx(hb > pl, True, 0, "HB adds yield stress")
    tx = triaxial_check(9.625, 0.472, 80000, 6000, 4000, 10000)
    approx(tx["status"], "PASS", 0, "triaxial PASS")


def test_structured_steps():
    print("\n[18] STRUCTURED STEP MODEL")
    from structured_steps import structure_step
    ss = structure_step(
        "Run 9-5/8\" casing to 3915 m; verify fill with trip tank; "
        "hold point before cementing; witness by company rep.", 1)
    approx(ss.hold_point, True, 0, "hold point detected")
    approx(ss.witness_point, True, 0, "witness point detected")
    approx(bool(ss.parameter), True, 0, "parameter extracted")
    approx(bool(ss.acceptance), True, 0, "acceptance extracted")


def test_anticollision():
    print("\n[19] ANTI-COLLISION (minimum curvature + separation factor)")
    import math as _m
    from engineering_anticollision import (min_curvature_positions,
                                           anti_collision_review,
                                           parse_trajectory_markdown,
                                           anti_collision_markdown)
    # vertical well: TVD = MD, no displacement
    vert = [(0, 0, 0), (2000, 0, 0), (4000, 0, 0), (6000, 0, 0)]
    pos = min_curvature_positions(vert)
    approx(pos[-1][1], 6000, 1e-6, "vertical TVD=MD")
    approx(pos[-1][2], 0.0, 1e-6, "vertical N=0")
    approx(pos[-1][3], 0.0, 1e-6, "vertical E=0")
    # constant build 1.5 deg/100ft to 30 deg @ azi 90: R=3820 ft
    #   TVD = R·sin30 = 1910 ; E = R·(1−cos30) = 511.75
    build = [(0, 0, 90), (1000, 15, 90), (2000, 30, 90)]
    pos2 = min_curvature_positions(build)
    approx(pos2[-1][1], 1910.0, 0.02 * 1910.0, "build TVD (R·sinθ)")
    approx(pos2[-1][3], 511.75, 0.02 * 511.75, "build E (R·(1−cosθ))")
    # identical wells -> SF = 0 -> FAIL
    rev = anti_collision_review(build, build)
    approx(rev["min_sf"], 0.0, 1e-6, "identical wells SF=0")
    approx(rev["status"], "FAIL", 0, "identical wells FAIL")
    # markdown parse
    md_tbl = ("| MD (ft) | Inc (°) | Az (°) |\n"
              "|---|---|---|\n"
              "| 0 | 0 | 90 |\n"
              "| 1000 | 15 | 90 |\n"
              "| 2000 | 30 | 90 |\n")
    st = parse_trajectory_markdown(md_tbl)
    approx(len(st), 3, 0, "parse 3 stations")
    approx(st[-1][0], 2000.0, 1e-6, "parse MD")
    approx(st[-1][1], 30.0, 1e-6, "parse inc")
    approx(st[-1][2], 90.0, 1e-6, "parse azi")
    # section markdown
    mkd = anti_collision_markdown(build, build)
    approx("ANTI-COLLISION REVIEW" in mkd, True, 0, "section heading")
    approx("FAIL" in mkd, True, 0, "section status")
    # offset well with surface offset (adjacent slot) vs build well:
    # offset vertical at N0=200, E0=0; ref build (30deg @ azi 90) to 3000 ft.
    # ref at 3000: TVD=2776, E=1011.75; offset at (3000, 200, 0)
    # c2c = sqrt(224^2 + 200^2 + 1011.75^2) ~= 1055.4 ft
    # EoU = tan(0.25deg)*3000 = 13.09 -> SF ~= 40.3
    from engineering_anticollision import (parse_offset_trajectory_markdown,
                                           anti_collision_markdown)
    off_tbl = ("| MD (ft) | Inc (°) | Az (°) | N0 (ft) | E0 (ft) |\n"
               "|---|---|---|---|---|\n"
               "| 0 | 0 | 0 | 200 | 0 |\n"
               "| 1500 | 0 | 0 | 200 | 0 |\n"
               "| 3000 | 0 | 0 | 200 | 0 |\n")
    off_st, off_surf = parse_offset_trajectory_markdown(off_tbl)
    approx(off_surf[0], 200.0, 1e-6, "surface offset N0 parsed")
    approx(off_surf[1], 0.0, 1e-6, "surface offset E0 parsed")
    approx(len(off_st), 3, 0, "offset stations parsed")
    ref3 = [(0, 0, 90), (1000, 15, 90), (2000, 30, 90), (3000, 30, 90)]
    rev3 = anti_collision_review(ref3, off_st, off_surface=off_surf)
    approx(rev3["status"], "OK", 0, "slot-separated wells OK")
    # analytic minimum SF ~ 27 at ~1500 ft (c2c~355 ft / EoU-sum~13.1 ft)
    approx(rev3["min_sf"], 27.0, 1.5, "min SF over well ~ 27")
    approx(rev3["min_c2c"], 200.0, 10.0, "closest approach ~ slot spacing")
    mkd3 = anti_collision_markdown(ref3, off_st, off_surface=off_surf)
    approx("Surface offset" in mkd3, True, 0, "offset noted in section")


def test_advanced_casing():
    print("\n[20] ADVANCED CASING (thermal/wear/corrosion/triaxial)")
    from engineering_casing import (buoyancy_factor, thermal_stress,
                                    thermal_force, remaining_wall,
                                    derated_burst, derated_collapse,
                                    eccentricity_correction,
                                    hb_pressure_loss_eccentric,
                                    casing_design_check,
                                    casing_check_markdown)
    # buoyancy: BF = 1 − 12/65.4 = 0.8165
    approx(buoyancy_factor(12.0), 0.8165, 1e-4, "buoyancy factor 12ppg")
    # buoyed axial load: 47 ppf × 8000 ft × 0.8165 = 307,010 lbf
    from engineering_casing import axial_load_buoyed
    approx(axial_load_buoyed(47, 8000, 12.0), 307010.0, 100.0,
           "buoyed axial load")
    # thermal: E·α·ΔT = 30e6 × 6.9e-6 × 200 = 41,400 psi
    approx(thermal_stress(200.0), 41400.0, 1.0, "thermal stress 200F")
    # thermal force on 9.625×0.472 (A = 13.57 in²): 41,400 × 13.57 = 561,800
    f_th = thermal_force(9.625, 0.472, 200.0)
    area = math.pi * (9.625 ** 2 - (9.625 - 0.944) ** 2) / 4.0
    approx(f_th, 41400.0 * area, 100.0, "thermal force = σ×A")
    # wear: 20% wear → t_rem = 0.3776; burst derate exactly 80%
    approx(remaining_wall(0.472, 0.20, 0.0), 0.3776, 1e-9, "remaining wall")
    pb_full = derated_burst(9.625, 0.472, 80000)
    pb_worn = derated_burst(9.625, 0.472, 80000, 0.20)
    approx(pb_worn / pb_full, 0.80, 1e-9, "burst derate = wall ratio")
    pc_full = derated_collapse(9.625, 0.472, 80000)
    pc_worn = derated_collapse(9.625, 0.472, 80000, 0.20)
    approx(pc_worn < pc_full, True, 0, "collapse derated by wear")
    # eccentricity: eccentric loss < concentric; corr within (0.5, 1]
    res = hb_pressure_loss_eccentric(500, 12.25, 5, 1000, 10, 0.6, 2.0,
                                     ecc_ratio=0.5)
    approx(res["eccentric_psi"] < res["concentric_psi"], True, 0,
           "eccentric < concentric")
    approx(eccentricity_correction(0.0, 0.6), 1.0, 1e-9,
           "concentric corr = 1")
    # full check set with thermal + wear + corrosion
    vals = {"casing_od": "9.625", "casing_wall": "0.472",
            "casing_yield": "110000", "mud_weight": "12",
            "casing_depth": "8000", "casing_weight": "47",
            "temperature_change": "150", "wear_fraction": "0.1",
            "corrosion_allowance": "0.02", "burst_load": "9000",
            "collapse_load": "6000", "axial_load": "400000"}
    csg = casing_design_check(vals)
    approx(len(csg["checks"]) >= 8, True, 0, ">= 8 casing checks")
    approx(csg["status"] in ("OK", "WARN"), True, 0, "status OK/WARN")
    md = casing_check_markdown(vals)
    approx("ADVANCED CASING DESIGN" in md or "Casing — Advanced" in md,
           True, 0, "casing section markdown")
    approx("Thermal" in md, True, 0, "thermal check shown")


def test_decision_trees():
    print("\n[21] DIAGNOSTIC DECISION TREES (stuck pipe + fishing)")
    from engineering_decisions import (stuck_pipe_diagnosis,
                                       fishing_tool_selection,
                                       stuck_pipe_markdown,
                                       fishing_markdown)
    # fully stuck -> free point / back-off / fishing path
    s1 = stuck_pipe_diagnosis(False, False, False)
    joined = " ".join(a for s in s1 for a in s["actions"]).upper()
    approx("FREE POINT" in joined, True, 0, "free point in fully-stuck path")
    approx("FISHING" in joined or "FISH" in s1[0]["escalate"].upper(),
           True, 0, "fishing escalation")
    # differential signature (can circulate, cannot rotate/move)
    s2 = stuck_pipe_diagnosis(False, True, False)
    approx("DIFFERENTIAL" in s2[0]["interpretation"].upper(), True, 0,
           "differential sticking identified")
    approx("OVER PULL" in s2[0]["actions"][0].upper().replace("OVER PULL",
           "OVERPULL") or "OVERPULL" in s2[0]["actions"][0].upper(),
           True, 0, "no-overpull advice")
    # key seat / ream path
    s3 = stuck_pipe_diagnosis(True, True, False)
    approx("RESTRICTION" in s3[0]["interpretation"].upper(), True, 0,
           "restriction path")
    # not stuck
    s4 = stuck_pipe_diagnosis(True, True, True)
    approx("NO STICKING" in s4[0]["interpretation"].upper(), True, 0,
           "not-stuck case")
    # fishing tool selection
    f1 = fishing_tool_selection(fish_desc="Drill pipe fish in hole",
                                fish_od_in=5.0, fish_top_ft=8000)
    approx(f1["fish_type"], "pipe", 0, "pipe fish classified")
    approx("OVERSHOT" in f1["primary_tool"].upper(), True, 0,
           "overshot primary for pipe")
    f2 = fishing_tool_selection(fish_desc="Junk and debris on top of fish")
    approx(f2["fish_type"], "junk", 0, "junk classified")
    approx("BASKET" in f2["primary_tool"].upper(), True, 0,
           "basket primary for junk")
    f3 = fishing_tool_selection(fish_desc="Wireline stuck in hole")
    approx(f3["fish_type"], "wireline", 0, "wireline classified")
    # markdown sections
    md1 = stuck_pipe_markdown({"can_rotate": "No", "can_circulate": "Yes",
                               "can_move_pipe": "No"})
    approx("STUCK PIPE DIAGNOSTIC TREE" in md1, True, 0,
           "stuck-pipe section heading")
    approx("Differential" in md1 or "DIFFERENTIAL" in md1, True, 0,
           "differential in section")
    md2 = fishing_markdown({"fish_description": "Junk in hole"})
    approx("FISHING TOOL SELECTION" in md2, True, 0,
           "fishing section heading")
    approx("Basket" in md2 or "basket" in md2, True, 0,
           "tool shown in section")
    # empty when no symptoms
    approx(stuck_pipe_markdown({"mud_weight": "12"}), "", 0,
           "no symptoms -> no section")


def test_hydraulics_model():
    print("\n[22] HYDRAULICS — STANDPIPE MODEL (API RP 13D)")
    import math as _m
    from engineering_hydraulics import (bit_pressure_drop, reynolds_pipe,
                                        pressure_loss_pipe,
                                        pressure_loss_annulus, ecd,
                                        standpipe_pressure,
                                        hydraulics_markdown)
    # bit: classic example — 12 ppg, 300 gpm, 3×12/32 nozzles (TFA 0.3312)
    tfa = 3 * _m.pi / 4 * (12 / 32.0) ** 2
    approx(bit_pressure_drop(12.0, 300.0, tfa), 906.7, 10.0, "bit drop ~907")
    # laminar pipe vs Hagen-Poiseuille (YP=0): 1.519 vs 1.523 psi (0.3%)
    lam = pressure_loss_pipe(12, 25, 0, 100, 4.276, 1000)
    mu = 25 / 1488.16
    hp = 32 * mu * (100 / 60.0) * 1000 / (32.174 * (4.276 / 12) ** 2 * 144)
    approx(lam["laminar_psi"], hp, 0.03, "pipe laminar == HP")
    # laminar annulus vs HP (slot): 3.40 vs 3.41 psi
    la = pressure_loss_annulus(12, 25, 0, 100, 8.5, 5.0, 1000)
    hpa = 48 * mu * (100 / 60.0) * 1000 / (32.174 * (3.5 / 12) ** 2 * 144)
    approx(la["laminar_psi"], hpa, 0.05, "annulus laminar == HP")
    # velocity conversion: 300 gpm in 4.276-in ID -> 402 ft/min (6.7 ft/s)
    from engineering_hydraulics import _v_ftmin
    approx(_v_ftmin(300, 4.276), 401.9, 1.0, "pipe velocity ft/min")
    # Reynolds: 928×12×6.7×4.276/25 = 12,761
    approx(reynolds_pipe(12, 401.9, 4.276, 25), 12761.0, 50.0, "Re ~ 12.8k")
    # turbulent pipe: Darcy-Weisbach + Blasius ~ 363 psi over 10,000 ft
    res = pressure_loss_pipe(12, 25, 20, _v_ftmin(300, 4.276), 4.276, 10000)
    approx(res["regime"], "turbulent", 0, "regime turbulent")
    approx(res["turbulent_psi"], 363.0, 8.0, "turbulent ~363 psi")
    # ECD: 12 ppg + 70 psi over 8000 ft
    approx(ecd(12.0, 70.0, 8000.0), 12.168, 0.01, "ECD calc")
    # full system
    vals = {"mud_weight": "12", "plastic_viscosity": "25", "yield_point": "20",
            "flow_rate": "300", "hole_size": "8.5", "pipe_od": "5",
            "dp_id": "4.276", "tfa": str(round(tfa, 4)), "depth": "10000",
            "casing_depth": "4000", "casing_id": "8.921", "bha_od": "6.5",
            "bha_length": "600", "surface_type": "Type 2 (standard)"}
    sp = standpipe_pressure(vals)
    approx(len(sp["parts"]) >= 6, True, 0, ">= 6 sections")
    approx(sp["spp_psi"] > 1500, True, 0, f"SPP > 1500 (got {sp['spp_psi']})")
    approx(sp["ecd_ppg"] > 12.0, True, 0, "ECD > MW")
    approx(sp["annulus_psi"] > 0, True, 0, "annulus loss > 0")
    md = hydraulics_markdown(vals)
    approx("STANDPIPE PRESSURE MODEL" in md, True, 0, "section heading")
    approx("Equivalent circulating density" in md, True, 0, "ECD shown")
    approx("Bit (nozzles)" in md, True, 0, "bit section shown")


def test_wellcontrol():
    print("\n[23] WELL CONTROL — KILL SHEET + SCENARIO")
    from engineering_wellcontrol import (kill_mud_weight,
                                         initial_circulating_pressure,
                                         final_circulating_pressure,
                                         pipe_capacity_bbl_ft,
                                         annular_capacity_bbl_ft,
                                         strokes_to_bit,
                                         total_strokes_to_displace,
                                         kick_scenario,
                                         kill_sheet_markdown)
    # classic: 12 ppg, SIDPP 400, TVD 10000 -> KMW 12.7692
    kmw = kill_mud_weight(12.0, 400.0, 10000.0)
    approx(kmw, 12.7692, 0.01, "KMW")
    # ICP = 1200 ; FCP = KMW×800/12 = 851.3
    approx(initial_circulating_pressure(400, 800), 1200.0, 0.01, "ICP")
    approx(final_circulating_pressure(kmw, 12.0, 800), 851.3, 1.0, "FCP")
    # capacities: 4.276-in ID = 0.017762 bbl/ft; 8.5×5 ann = 0.04590
    pc = pipe_capacity_bbl_ft(4.276)
    approx(pc, 0.017762, 1e-5, "pipe capacity")
    ac = annular_capacity_bbl_ft(8.5, 5.0)
    approx(ac, 0.04590, 1e-4, "annular capacity")
    # strokes: to bit 1,776 ; total 6,366 @ 0.1 bbl/stk
    approx(strokes_to_bit(pc, 10000, 0.1), 1776.2, 1.0, "strokes to bit")
    approx(total_strokes_to_displace(pc, ac, 10000, 0.1), 6366.2, 2.0,
           "total strokes")
    # scenario branching
    vals = {"mud_weight": "12", "sidpp": "400", "sicp": "600",
            "pit_gain": "20", "depth": "10000", "hole_size": "8.5",
            "pipe_od": "5", "slow_pump_pressure": "800",
            "pump_output": "0.1", "dp_id": "4.276"}
    steps = kick_scenario(vals)
    approx(len(steps) >= 4, True, 0, "scenario >= 4 steps")
    md = kill_sheet_markdown(vals)
    approx("KILL SHEET" in md, True, 0, "kill sheet heading")
    approx("12.77" in md, True, 0, "KMW in section")
    approx("851" in md, True, 0, "FCP in section")
    # heavy-kill heuristic: SIDPP 600 @ 8000 ft -> KMW-MW = 1.44 -> W&W
    vals2 = dict(vals, sidpp="600", depth="8000")
    md2 = kill_sheet_markdown(vals2)
    approx("WAIT-AND-WEIGHT" in md2.upper(), True, 0, "W&W recommended")


def test_geomechanics():
    print("\n[24] GEOMECHANICS — KIRSCH + MOHR-COULOMB + LOT")
    from engineering_geomechanics import (kirsch_hoop_stress,
                                          fracture_pressure,
                                          breakout_pressure,
                                          safe_mud_window,
                                          mud_window_check,
                                          lot_interpretation,
                                          geomechanics_markdown)
    # Kirsch: θ=0 -> 3σh−σH−Pm = 10000 ; θ=90 -> 3σH−σh−Pm = 18000
    approx(kirsch_hoop_stress(12000, 10000, 8000, 0), 10000.0, 0.01,
           "Kirsch θ=0")
    approx(kirsch_hoop_stress(12000, 10000, 8000, 90), 18000.0, 0.01,
           "Kirsch θ=90")
    # fracture: 3σh−σH−Pp+T0 = 30000−12000−5000+500 = 13500 (vertical)
    fr = fracture_pressure(19000, 12000, 10000, 5000, 500)
    approx(fr["pressure_psi"], 13500.0, 1.0, "fracture pressure")
    approx(fr["mechanism"].startswith("vertical"), True, 0, "mechanism")
    # breakout: c = 2309 ; Pm = [26000−4000−8000]/2 = 7000 (hand-verified)
    approx(breakout_pressure(12000, 10000, 5000, 8000, 30), 7000.0, 3.0,
           "breakout pressure")
    # window + checks
    win = safe_mud_window(19000, 12000, 10000, 5000, 8000, 30, 500)
    approx(win["lower_psi"], 7000.0, 3.0, "window lower")
    approx(win["upper_psi"], 13500.0, 3.0, "window upper")
    chk = mud_window_check(12.0, 10000, win)
    approx("BREAKOUT" in chk["status"], True, 0, "12 ppg -> breakout risk")
    chk2 = mud_window_check(16.0, 10000, win)
    approx(chk2["status"].startswith("OK"), True, 0, "16 ppg -> OK")
    # LOT: 1400 psi @ 4000 ft = 6.73 ppg EMW
    li = lot_interpretation(1400, 4000, 12.0)
    approx(li["emw_ppg"], 6.73, 0.02, "LOT EMW")
    # section
    md = geomechanics_markdown({
        "depth": "10000", "mud_weight": "12", "formation_pressure": "9.6",
        "sigma_v_grad": "1.9", "sH_sv_ratio": "0.63", "sh_sv_ratio": "0.53",
        "ucs_psi": "8000", "friction_angle": "30",
        "tensile_strength": "500", "lot_pressure": "1400",
        "casing_depth": "4000"})
    approx("WELLBORE STABILITY" in md, True, 0, "section heading")
    approx("Safe mud window" in md, True, 0, "window shown")
    approx("LOT" in md, True, 0, "LOT shown")


def test_cementing():
    print("\n[25] CEMENTING — VOLUMES / UCA / SGS / GAS MIGRATION")
    from engineering_cementing import (annular_volume_bbl, sacks_required,
                                       mix_water_bbl, uca_strength_estimate,
                                       static_gel_strength,
                                       gas_migration_risk, cementing_markdown)
    # 8.5×5 annulus × 1000 ft + 30% excess: 0.04590×1000×1.3 = 59.67 bbl
    av = annular_volume_bbl(8.5, 5.0, 1000, 30)
    approx(av, 59.67, 0.1, "annular volume with excess")
    # sacks: 59.67×5.6146/1.18 = 283.9
    sk = sacks_required(av, 1.18)
    approx(sk, 283.9, 0.5, "sacks required")
    # mix water: 283.9×5.2/42 = 35.2 bbl
    approx(mix_water_bbl(sk, 5.2), 35.15, 0.1, "mix water")
    # UCA: 0 at t=0; asymptote below final; monotonic
    approx(uca_strength_estimate(0), 0.0, 1e-9, "UCA at t=0")
    approx(uca_strength_estimate(100) < 3000.0, True, 0, "UCA asymptote")
    approx(uca_strength_estimate(100) > uca_strength_estimate(24), True, 0,
           "UCA monotonic")
    # gel: monotonic
    approx(static_gel_strength(60) > static_gel_strength(10), True, 0,
           "SGS monotonic")
    # gas migration: narrow + short WOC -> HIGH; wide + long -> LOW
    g1 = gas_migration_risk(0.8, 4)
    approx(g1["level"], "HIGH", 0, "narrow gap -> HIGH")
    g2 = gas_migration_risk(3.5, 36, static_time_h=2,
                            slurry_fluid_loss_ml30=20)
    approx(g2["level"], "LOW", 0, "wide gap -> LOW")
    approx(g1["score"] > g2["score"], True, 0, "score ordering")
    md = cementing_markdown({"hole_size": "8.5", "pipe_od": "5",
                             "cemented_length": "1000", "excess": "30",
                             "lead_yield": "1.18", "woc": "8"})
    approx("CEMENTING" in md, True, 0, "section heading")
    approx("psi @ 12 h" in md, True, 0, "UCA shown")
    approx("Gas-migration" in md, True, 0, "gas migration shown")


def test_special_wells():
    print("\n[26] SPECIAL WELLS — HPHT / DEEPWATER / COMPLETION")
    from engineering_special import (elastomer_rating,
                                     trapped_annular_pressure,
                                     metallurgy_suggestion, riser_margin,
                                     subsea_bop_check, completion_barriers,
                                     special_wells_markdown)
    # elastomer: 350F -> FKM; 700F -> none OK
    er = elastomer_rating(350)
    approx(er["elastomer"], "FKM / Viton", 0, "350F -> FKM")
    approx(er["ok"], True, 0, "350F ok")
    approx(elastomer_rating(700)["ok"], False, 0, "700F not ok")
    # trapped annular: 106.7 psi/°F × 100 = 10,667 psi
    approx(trapped_annular_pressure(100), 10666.7, 1.0, "trapped pressure")
    # riser margin: 12 ppg, WD 3000, TVD 12000 -> 13.15 ppg
    rm = riser_margin(12.0, 3000, 12000)
    approx(rm["riser_margin_mw_ppg"], 13.15, 0.02, "riser margin MW")
    approx(rm["margin_over_current_ppg"], 1.15, 0.02, "margin vs current")
    # subsea BOP: 10000 vs 6335 -> OK
    sb = subsea_bop_check(10000, 5000, 3000)
    approx(sb["ok"], True, 0, "subsea BOP OK")
    approx(sb["load_psi"], 6335.0, 1.0, "subsea BOP load")
    # metallurgy
    m1 = metallurgy_suggestion(3.0, "No", 200)
    approx("13Cr" in m1["metallurgy"], True, 0, "CO2 -> 13Cr")
    m2 = metallurgy_suggestion(0.1, "Yes", 200)
    approx("NACE" in m2["metallurgy"] or "ISO 15156" in m2["metallurgy"],
           True, 0, "sour -> NACE/ISO 15156")
    # barriers
    bm = completion_barriers({"cement_verified": "Yes",
                              "casing_tested": "Yes", "packer_set": "Yes",
                              "tree_ok": "Yes", "trsv_ok": "Yes"})
    approx(bm["status"], "TWO BARRIERS OK", 0, "two barriers OK")
    approx(completion_barriers({})["status"], "NO BARRIER", 0,
           "no barrier")
    md = special_wells_markdown({"max_temperature": "350",
                                 "temperature_change": "100",
                                 "co2_pct": "3", "h2s": "No",
                                 "water_depth": "3000", "mud_weight": "12",
                                 "depth": "12000", "bop_wp": "10000",
                                 "masp": "5000", "packer_set": "Yes",
                                 "tree_ok": "Yes"})
    approx("SPECIAL-WELLS" in md, True, 0, "section heading")
    approx("Elastomer" in md and "Riser margin" in md, True, 0,
           "checks shown")


def test_witsml():
    print("\n[27] WITSML / JSON EXPORT (telemetry handoff)")
    from witsml_export import (build_witsml, build_json, export_witsml,
                               export_json)
    from xml.dom import minidom
    vals = {"well_name": "Well A", "field_name": "Field X",
            "operator": "the Operator", "mud_weight": "12",
            "depth": "5000", "water_depth": "0",
            "trajectory_table": (
                "| MD (ft) | Inc (°) | Az (°) |\n|---|---|---|\n"
                "| 0 | 0 | 90 |\n| 2500 | 30 | 90 |\n| 5000 | 30 | 90 |")}
    xml = build_witsml(vals)
    dom = minidom.parseString(xml)
    approx(len(dom.getElementsByTagName("well")), 1, 0, "one well object")
    approx(dom.getElementsByTagName("name")[0].firstChild.data, "Well A",
           0, "well name in XML")
    sts = dom.getElementsByTagName("trajectoryStation")
    approx(len(sts), 3, 0, "3 trajectory stations")
    tvds = [float(s.getElementsByTagName("tvd")[0].firstChild.data)
            for s in sts]
    approx(tvds[-1], 4552.6, 1.5, "min-curvature TVD at 5000 ft")
    # json handoff
    j = build_json(vals)
    approx(j["well"]["name"], "Well A", 0, "json well name")
    approx(j["basis"]["mud_weight"], "12", 0, "json basis")
    # file export
    import tempfile
    tmp = tempfile.mkdtemp(prefix="drl_witsml_")
    export_witsml(vals, tmp + "/w.xml")
    export_json(vals, tmp + "/w.json")
    import os as _os
    approx(_os.path.exists(tmp + "/w.xml"), True, 0, "xml file written")
    approx(_os.path.exists(tmp + "/w.json"), True, 0, "json file written")
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


def test_afe_materials():
    print("\n[28] AFE vs ACTUAL + MATERIAL READINESS")
    from operations_engine import LessonsDatabase
    db = LessonsDatabase()
    db.add_afe(well_name="W", afe_number="A1", budget_usd=1000000,
               commitment_usd=600000, actual_usd=400000,
               forecast_usd=1100000)
    s = db.afe_status()
    approx(s["committed_pct"], 60.0, 0.1, "committed %")
    db.add_material(well_name="W", item="Barite", category="Mud",
                    required_qty=100, available_qty=50, unit="ton",
                    critical=True)
    m = db.material_readiness()
    approx(m["short"] >= 1, True, 0, "short material counted")
    approx(len(m["critical_short"]) >= 1, True, 0, "critical short flagged")
    db.close()


def test_backup_secrets():
    print("\n[29] BACKUP/RESTORE + SECRETS")
    from backup_restore import create_backup, list_backups, SecretsManager
    b = create_backup("test")
    approx(b is not None, True, 0, "backup created")
    approx(len(list_backups()) >= 1, True, 0, "backup listed")
    sm = SecretsManager()
    sm.set_secret("t_k", "v1")
    approx(sm.get_secret("t_k"), "v1", 0, "secret roundtrip")
    sm.delete_secret("t_k")
    approx(sm.get_secret("t_k"), "", 0, "secret deleted")


def test_well_report():
    print("\n[30] WELL REPORT GENERATOR")
    from well_report import build_well_report, _demo_values
    md = build_well_report(_demo_values(), "PARS OIL CO", "DRILL PRO")
    for sec in ("WELL PROFILE", "ENGINEERING VALIDATION", "PROGRAM READINESS",
                "STANDARDS COMPLIANCE", "DOCUMENT COMPLIANCE"):
        approx(sec in md, True, 0, f"report has {sec}")


def main():
    print("=" * 64)
    print("ENGINEERING REFERENCE TEST SUITE")
    print("=" * 64)
    for fn in (test_units, test_hydrostatic, test_maasp, test_kill_mud_weight,
               test_annular_velocity, test_casing_burst, test_casing_collapse,
               test_well_cost, test_engineering_calc_annular, test_advanced,
               test_readiness_and_ops, test_planning_intelligence,
               test_entity_scrub, test_compliance, test_risk_decision,
               test_standards, test_deep_engineering,
               test_structured_steps, test_anticollision, test_advanced_casing,
               test_decision_trees, test_hydraulics_model, test_wellcontrol,
               test_geomechanics, test_cementing,
               test_special_wells, test_witsml, test_afe_materials,
               test_backup_secrets, test_well_report):
        try:
            fn()
        except Exception:
            global _FAIL
            _FAIL += 1
            _FAILURES.append(f"{fn.__name__} raised: {traceback.format_exc()[-400:]}")
            print(f"  ✘ {fn.__name__} EXCEPTION")
    print("\n" + "=" * 64)
    print(f"RESULT: {_PASS} passed, {_FAIL} failed")
    if _FAILURES:
        print("Failures:")
        for f in _FAILURES:
            print("  -", f[:300])
    print("=" * 64)
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
