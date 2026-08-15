# ============================================================================
# SEED PP2 PROCEDURES — extract real procedures from the 321 new documents
# File: seed_pp2_procedures.py
# Builds procedures in the procedures database from the actual documents
# added from the pp2 repo (files 242-562). Steps are extracted from the
# numbered lists inside the source documents (cleaned + generalized),
# checklists are built from safety/equipment notes.
# Includes Caspian Sea / semi-submersible procedures (KEPCO South Caspian,
# Iran Amir Kabir Semi-Submersible, Shah Deniz, 36\" jetting).
# ============================================================================

import re
import sys
from pathlib import Path

from cbs_db import generalize_text
from procedures_db import ProcedureDatabase

LIB = Path(__file__).resolve().parent / "programs" / "library"


def _clean(t: str) -> str:
    t = generalize_text(t)
    t = re.sub(r"\s+", " ", t)
    return t.strip(" .-–—")


def _norm_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", s.lower())


# ---------------------------------------------------------------------------
# PROCEDURE DEFINITIONS — (key, name, category, source file patterns)
# steps: extracted automatically from numbered lists in the source docs
# ---------------------------------------------------------------------------

PROC_DEFS = [
    # --- Hole section procedures ---
    ("pp2_hole_20in", "Drill 20\" Hole Section (Offshore)", "Drilling Operations",
     ["20_inch_Hole_Procedure", "Program_for_20", "When_20"]),
    ("pp2_hole_17in", "Drill 17\" Hole Section", "Drilling Operations",
     ["17_inch_Hole_Procedure", "17_in_PDC_DIRECTIONAL_BHA"]),
    ("pp2_hole_16in", "Drill 16\" Hole Section", "Drilling Operations",
     ["16_inch_HOLE", "Pick_up_16"]),
    ("pp2_hole_1225in", "Drill 12-1/4\" Hole Section", "Drilling Operations",
     ["12.25_section_instruction", "DRILLING_12.25inch_section", "standing_DP_for__12.25inch_section"]),
    ("pp2_hole_10625in", "Drill 10-5/8\" Hole Section", "Drilling Operations",
     ["10.625_inch_Hole_Procedure"]),
    ("pp2_hole_135x17in", "Drill 13.5\" x 17\" Hole Section", "Drilling Operations",
     ["13.5_inch_by_17_inch_hole_section_Procedure"]),
    ("pp2_hole_1475x17in", "Drill 14.75\" x 17\" Hole Section", "Drilling Operations",
     ["14.75_inch_by_17_inch_hole_section_Procedure"]),
    ("pp2_hole_235in", "Drill 23.5\" Hole (Jahrum to TD)", "Drilling Operations",
     ["DRILLING_23.5", "DRILLING_AFTER_S.T_23.5"]),
    ("pp2_hole_24in", "Drill 24\" Hole Section", "Drilling Operations",
     ["Drill_24_in._Hole_Procedure", "DRILLING_24_kick_off"]),
    ("pp2_hole_26in", "Drill 26\" Hole Section", "Drilling Operations",
     ["Drill_26_in._Hole_Procedure"]),
    ("pp2_hole_32in", "Drill 32\" Hole Section", "Drilling Operations",
     ["DRILLING_32", "game_plan_for_32_hole_section"]),
    ("pp2_hole_36in", "Drill 36\" Hole (Conductor)", "Drilling Operations",
     ["Drilling_36", "36inch_Deepwater_Jetting_Procedure"]),
    ("pp2_hole_85in", "Drill 8-1/2\" Hole Section", "Drilling Operations",
     ["8,5_Section_Rec"]),
    # --- Casing running ---
    ("pp2_csg_30in", "Run 30\" Casing", "Casing & Liner",
     ["RUNNING_30_inch_CSG"]),
    ("pp2_csg_20in", "Run 20\" Casing (Offshore)", "Casing & Liner",
     ["Running_20in__Procedure", "RUNNING_20_inch_CSG", "plan_of_run_20_inch_casing"]),
    ("pp2_csg_18625in", "Run 18-5/8\" Casing", "Casing & Liner",
     ["RUN_18_5-8_INCH_CSG"]),
    ("pp2_csg_16in", "Run 16\" Casing", "Casing & Liner",
     ["16_inch_CSG_Procedure"]),
    ("pp2_csg_13375in", "Run 13-3/8\" Casing", "Casing & Liner",
     ["RUNNING_13_3-8_INCH_CSG"]),
    ("pp2_csg_9625in", "Run 9-5/8\" & 10-3/4\" Casing", "Casing & Liner",
     ["RUNNIG_9.625_&_10.75_inch_CASING"]),
    ("pp2_csg_pull", "Pull & Cut 15-5/8\" Casing (Section Recovery)", "Casing & Liner",
     ["24_Section_Rec_Cut_and_Pull_15625_csg"]),
    # --- Cementing ---
    ("pp2_cmt_20in", "Cement 20\" Casing", "Cementing",
     ["Cementing_20in__Procedure", "Procedure_for_Cement_Job_20_casing"]),
    ("pp2_cmt_16in", "Cement 16\" Casing", "Cementing",
     ["16_inch_CMT_Procedure"]),
    ("pp2_cmt_18625in", "Cement 18-5/8\" Casing", "Cementing",
     ["cementing_18_5-8_INCH_CSG", "DRILL_OUT_18_58_SHOE"]),
    ("pp2_cmt_balanced_plug", "Cement Balanced Plug", "Cementing",
     ["Instruction_CMT_balanced_plug", "CMT_Balanced_Plug", "Instruction__CMT_balanced_plug"]),
    ("pp2_cmt_top_job", "Top Cement Job", "Cementing",
     ["SPD18A-09_Top_Cement_Job"]),
    ("pp2_cmt_plug_back", "Cement Plug Back Program", "Cementing",
     ["Cement_Plug_Back_Program", "Final_Cement_Plug_Back_Program", "PLUG_BACK_PROGRAM"]),
    # --- Back-off & fishing ---
    ("pp2_backoff", "Free Point & Back-Off Operation", "Fishing & Remedial",
     ["Back_Off_String_Shot", "BACKOFF_PROCEDURE", "To_Back_off", "3_1-2_pipe_BACKOFF"]),
    ("pp2_fishing", "Fishing Operation (General)", "Fishing & Remedial",
     ["Fishing", "Clean-out_and_mill_running_procedure"]),
    ("pp2_mill_flush", "Mill & Flush Tool Operation", "Fishing & Remedial",
     ["Mill_and_flush_tool", "POLISH_MILL_BHA", "Scraper_and_Polish_Mill"]),
    # --- Liner & whipstock ---
    ("pp2_liner_11875in", "Run 11-7/8\" Liner", "Casing & Liner",
     ["11.875_liner_procedure"]),
    ("pp2_liner_hanger", "Run Liner & Set Liner Hanger", "Casing & Liner",
     ["liner_hanger_running_procedure", "liner_hanger"]),
    ("pp2_liner_top_packer", "Run Liner Top Packer", "Casing & Liner",
     ["Liner_top_packer_running_procedure", "Upper_PBR_and_liner_top_packer"]),
    ("pp2_whipstock", "Hydraulic Whipstock Operation", "Sidetrack Operations",
     ["Hydraulic_Whipstock_Operational_Procedure", "Whipstock_Handling", "Trackmaster"]),
    ("pp2_sidetrack_11875in", "Sidetrack 11-7/8\" Section", "Sidetrack Operations",
     ["11.875_inch_sidetrack_Procedure"]),
    ("pp2_sidetrack_plug", "Sidetrack Cement Plug", "Sidetrack Operations",
     ["Sidetrack_Plug__Procedure"]),
    # --- Shallow gas & well control ---
    ("pp2_shallow_gas", "Shallow Gas — Drilling Without Riser (Semisubmersible)", "Well Control",
     ["IAK_NDCO_shallow_gas_procedure", "shallow_gas_procedure", "RSP_001_Shallow_gas_Suspension"]),
    ("pp2_drillers_method", "Driller's Method (Kill Procedure)", "Well Control",
     ["Drillers_Method_Procedure"]),
    ("pp2_wait_weight", "Wait & Weight Method (Kill Procedure)", "Well Control",
     ["Wait_and_Weight_Method_Procedure"]),
    ("pp2_preflow_check", "Pre-Flow Check List", "Well Control",
     ["Pre-Flow_Check_List"]),
    # --- BOP ---
    ("pp2_bop_run", "Run BOP Stack & Space Out", "BOP Operations",
     ["Run_BOP", "Ver2_BOP_run_procedure"]),
    ("pp2_bop_test_18625in", "Test 18-5/8\" BOP", "BOP Operations",
     ["Test_18.625inch_BOP"]),
    ("pp2_change_rams", "Change BOP Rams", "BOP Operations",
     ["Change_Rams"]),
    # --- Mud ---
    ("pp2_mud_kepco", "Mud Program (Offshore Well)", "Drilling Fluids",
     ["KEPCO_Mud_Program", "Glycol_Project_NISOC__Mud_Program"]),
    ("pp2_mud_fluids_17in", "Drilling Fluids Program 17-1/2\"", "Drilling Fluids",
     ["Drilling_Fluids_Program_for_17_1", "Drilling_Fluids_Program_HD-10D"]),
    # --- Hole cleaning / conditioning ---
    ("pp2_hole_cleaning", "Hole Cleaning Procedure", "Drilling Operations",
     ["hole_cleaning_procedure", "TD_Hole_cleaning"]),
    ("pp2_wash_ream", "Wash & Ream Operation", "Drilling Operations",
     ["Wash_&_Ream"]),
    ("pp2_drillout_cement", "Drill Out Cement & Shoe", "Drilling Operations",
     ["Driil_out_cement_track", "Drill_out_cement", "Drill_out_18_5-8_shoe"]),
    ("pp2_drill_seawater", "Drill 17\" Section with Sea Water", "Drilling Operations",
     ["Instruction_of_drilling_17in_section_by_sea_water"]),
    ("pp2_pilot_hole", "Drill Pilot Hole (100 m)", "Drilling Operations",
     ["100_m_Pilot_hole", "plan_for_start_drilling_pilot_hole"]),
    ("pp2_jet_in", "Jet In — Drill Ahead Procedure", "Drilling Operations",
     ["Jet_In_-Drill_ahead_Procedure"]),
    # --- Completion & testing ---
    ("pp2_completion_kangan", "Completion Running Procedure (Kangan-type)", "Completion",
     ["Kangan_25_COMPLETION_PROCEDURE", "Kangan_23_workover"]),
    ("pp2_completion_esp", "ESP Completion Running", "Completion",
     ["ESP", "SP7,8,9_Main_Compl_Prog"]),
    ("pp2_completion_sefid", "Completion Running (5\" x 7\" x 4-1/2\")", "Completion",
     ["Sefid_Zakhur-02_Completion_Running"]),
    ("pp2_dst_procedure", "DST Procedure (Full Bore / Flex Run)", "Formation Evaluation",
     ["full_bure_DST_program", "RIH_procedure_-String_diagram_Flex_run-DST1", "DST1__POOH_procedure"]),
    ("pp2_well_testing", "Well Testing Program (Yaran-type)", "Formation Evaluation",
     ["Yaran-3_Well_Testing_Programme", "Yaran-2_test_program"]),
    ("pp2_tlc_logging", "TLC Logging Job Procedure", "Formation Evaluation",
     ["TLC_job_procedures"]),
    # --- Semi-submersible ---
    ("pp2_semisub_ops", "Semi-Submersible Drilling Operations", "Special Operations",
     ["Iran_Amir_Kabir__Drilling_Operations_Procedure_Manual"]),
    ("pp2_semisub_dummy", "Subsea Procedure — Dummy Run", "Special Operations",
     ["Subsea_procedure_-_dummy_run"]),
    ("pp2_wash_seabed", "Wash Seabed / Wellhead Preparation", "Special Operations",
     ["wash_seabed"]),
    # --- Tools ---
    ("pp2_tgb_run", "Run TGB (Tubing Hanger / Tie-Back) Tool", "Special Operations",
     ["TGB_RUNNING_PROC", "TGB_running", "plan_of_run_TGB"]),
    ("pp2_isott_run", "Run ISOTT Running Tool", "Special Operations",
     ["ISOTT_running_procedure"]),
    ("pp2_rhino", "RHINO Reamer Operation", "Special Operations",
     ["Rhino_Procedure"]),
    ("pp2_set_packer", "Set Packer BHA", "Completion",
     ["SET_PACKER_BHA"]),
    ("pp2_ssc_valve", "Set SSC (Sub-Surface) Valve", "Well Control",
     ["SETTING_PROCEDURES_FOR_THE_SSC_VALVE"]),
]


def _find_source(patterns):
    """پیدا کردن اولین فایل کتابخانه که با یکی از الگوها مطابقت دارد"""
    files = list(LIB.glob("*.txt"))
    for pat in patterns:
        p = _norm_name(pat)
        for f in files:
            if p in _norm_name(f.name):
                return f
    return None


def _extract_steps(text: str, max_steps: int = 18) -> list:
    """استخراج مراحل از متن سند:
    1) آیتم‌های شماره‌دار (N- / N. / N))
    2) پاراگراف‌های عملیاتی که با افعال کلیدی شروع می‌شوند (سندهای پاراگرافی)
    """
    lines = text.splitlines()
    steps = []
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        if re.match(r"^[─═\[]", ln) or re.match(r"^\[ صفحه", ln):
            continue
        m = re.match(r"^(\d{1,2})[-.)]\s+(.{15,})", ln)
        if m:
            step = _clean(m.group(2))
            if 15 < len(step) < 260:
                steps.append(step)
                continue
        # paragraph-style: starts with an action verb
        if re.match(
            r"^(drill|run|pooh|rih|make\s*up|pick\s*up|pump|take|perform|"
            r"circulate|condition|displace|test|set|install|remove|retrieve|"
            r"hold|spot|open|close|pull|cement|wash|ream|jet|float|stab|"
            r"fill|inspect|check|prepare|secure|land|pressure|mix|kill|"
            r"bop|connect|trip|slip|stand|lay\s*down|change|reset|backoff|"
            r"back\s*off|mill|fish|tag|work|monitor|record|report|verify|"
            r"ensure|tighten|torque|break|start|stop)\b",
            ln, re.IGNORECASE) and 20 < len(ln) < 320:
            step = _clean(ln)
            if step:
                steps.append(step)
    # dedupe
    seen = set()
    out = []
    for s in steps:
        k = s[:60].lower()
        if k not in seen:
            seen.add(k)
            out.append(s)
        if len(out) >= max_steps:
            break
    return out


def _extract_checklist(text: str, max_items: int = 10) -> list:
    """چک‌لیست از جملات ایمنی/تجهیزات (خطوط کلیدی)"""
    keys = ["safety meeting", "safety", "check", "ensure", "test", "inspect",
            "prepare", "verify", "available", "ready", "calibrat", "h2s",
            "fire", "emergency", "bop", "pit", "mud", "radio", "lifeboat",
            "personal protective", "ppe", "torque", "gauge"]
    lines = []
    for ln in text.splitlines():
        ln = ln.strip()
        if not ln or len(ln) > 180:
            continue
        low = ln.lower()
        if any(k in low for k in keys) and re.search(r"[A-Za-z]{4}", ln):
            lines.append(_clean(ln))
    seen, out = set(), []
    for l in lines:
        k = l[:60].lower()
        if k not in seen and 15 < len(l) < 170:
            seen.add(k)
            out.append(l)
        if len(out) >= max_items:
            break
    return out or ["Hold pre-job safety meeting",
                   "Verify all equipment & gauges are calibrated and available"]


def seed(force: bool = False):
    db = ProcedureDatabase()
    try:
        existing = db.conn.execute(
            "SELECT COUNT(*) AS c FROM procedures WHERE proc_key LIKE 'pp2_%'"
        ).fetchone()["c"]
        if existing and not force:
            print(f"✔ pp2 procedures already seeded ({existing}) — "
                  f"use --force to re-seed.")
            return

        # categories
        def cat_id(name):
            for c in db.get_all_categories():
                if c.name == name:
                    return c.id
            return db.add_category(name, icon="📋", sort_order=99)

        added = 0
        skipped = []
        for key, name, cat, patterns in PROC_DEFS:
            src = _find_source(patterns)
            if src is None:
                skipped.append((key, patterns[0]))
                continue
            text = src.read_text(encoding="utf-8", errors="replace")
            steps = _extract_steps(text)
            if len(steps) < 4:
                skipped.append((key, f"{patterns[0]} (only {len(steps)} steps)"))
                continue
            checklist = _extract_checklist(text)
            cid = cat_id(cat)
            desc = (f"Extracted from real field document "
                    f"({src.name.split('_', 1)[-1].rsplit('.', 1)[0]}). "
                    f"Generalized — no well/company names.")
            pid = db.add_procedure(name, cid, description=desc,
                                   has_checklist=True, inputs_json="[]",
                                   tags=f"pp2,{cat.lower()}")
            db.conn.execute("UPDATE procedures SET proc_key=? WHERE id=?",
                            (f"pp2_{key}", pid))
            db.conn.commit()
            for s in steps:
                db.add_step(pid, s)
            for c in checklist:
                db.add_checklist_item(pid, c)
            added += 1
            print(f"  ✔ {name} ({len(steps)} steps, {len(checklist)} chk)")

        print(f"\nadded: {added} | skipped: {len(skipped)}")
        for k, why in skipped[:15]:
            print(f"  - {k}: {why}")
    finally:
        db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
