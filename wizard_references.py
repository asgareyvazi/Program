# ============================================================================
# WIZARD REFERENCE LIBRARY
# ============================================================================
# Maps wizard templates to the real documents in programs/library/ (214
# documents extracted from the user's combined files). When a document is
# generated, the matched reference documents are listed (and optionally
# appended) so the output is enriched with real, field-proven content.
# ============================================================================

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

LIBRARY_DIR = Path(__file__).resolve().parent / "programs" / "library"

# ----------------------------------------------------------------------------
# Category keywords used to match template -> library documents
# ----------------------------------------------------------------------------

# template_key -> list of (library file number prefix, label)
TEMPLATE_REFERENCES: Dict[str, List[Tuple[str, str]]] = {
    "drilling_program": [
        ("152", "Well Drilling Program Rev.02 (2021)"),
        ("196", "Drilling Program for"),
        ("200", "Drilling program"),
        ("197", "Drilling Program for"),
            ("587", 'Guideline 1100 — Drilling 36" Hole'),
        ("592", 'Guideline 1200sem — Drilling 26" Hole (Semi-submersibles)'),
        ("594", 'Guideline 1300 — Drilling Vertical 17-1/2" Hole'),
        ("597", 'Guideline 1350 — Drilling 12-1/4" Hole'),
        ("598", 'Guideline 1400 — Drilling 8-1/2" Hole'),
        ("583", 'Guideline 1020 — Pipe Tally Procedure'),
        ("582", 'Guideline 1010 — Depth Referencing'),
        ("646", 'Guideline 4900 — Drilling Hydraulics'),
],
    "advanced_drilling_program": [
        ("152", "Well Drilling Program Rev.02 (2021)"),
        ("214", "Drilling & Completion Programme"),
        ("102", "Drilling program Rev 0.3"),
        ("196", "Drilling Program for"),
        ("200", "Drilling program"),
        ("201", "Drilling program (F02-Area II)"),
            ("600", 'Guideline 2005 — Casing Design'),
        ("601", 'Guideline 2010 — Casing Centralisation'),
        ("591", 'Guideline 1200fix — Drilling Surface Hole (Multi-well)'),
        ("593", 'Guideline 1280 — Underreaming in Top Hole'),
        ("595", 'Guideline 1310 — Drilling Deviated 17-1/2" Hole'),
        ("646", 'Guideline 4900 — Drilling Hydraulics'),
],
    "workover_program": [
        ("173", "Workover Program Rev04"),
        ("174", "Workover Program Rev02"),
        ("177", "Workover-1 Program Rev.05"),
        ("185", "Workover Program Rev.00"),
    ],
    "esp_workover": [
        ("163", "25 Wells ESP Running Program"),
        ("75", "Completion pull out procedure"),
        ("76", "POOH Completion String Operation Procedure"),
        ("92", "Completion Program 127 Workover #2 Rev.02"),
    ],
    "reentry_program": [
        ("217", "Amendment 3 — Re-entry program"),
        ("219", "Re-entry #1 Program"),
        ("231", "Re-entry #4"),
        ("232", "Re-entry program Final"),
        ("236", "Re1-H program"),
        ("237", "Re1-H final program"),
        ("238", "Re3H Program"),
            ("585", 'Guideline 1060sem — Running TGB'),
        ("586", 'Guideline 1070sem — 12-1/4" Pilot Hole'),
        ("672", 'Guideline 6150 — Free Point & Back-Off'),
        ("675", 'Guideline 6410 — Casing Milling'),
],
    "offshore_workover_program": [
        ("225", "Workover Program FINAL"),
        ("226", "Program Final"),
        ("227", "Workover Program"),
        ("233", "Workover 3"),
        ("234", "Workover"),
        ("235", "Workover 4"),
        ("241", "Workover program"),
    ],
    "offshore_drilling_program": [
        ("218", "Drilling program rev 00"),
        ("220", "Drilling Program ver2"),
        ("221", "Drilling Program Rev-1"),
        ("222", "Drilling program Final"),
        ("223", "Drilling Program PLDR-4002"),
        ("224", "Drilling Program PLDR-5002"),
        ("228", "Continue Drilling Program"),
        ("229", "Program Final"),
        ("230", "Drilling Program"),
            ("588", 'Guideline 1100sem — Drilling 36" Hole (Semi)'),
        ("592", 'Guideline 1200sem — Drilling 26" Hole (Semi-submersibles)'),
        ("585", 'Guideline 1060sem — Well Establishment: Running TGB'),
        ("586", 'Guideline 1070sem — Well Establishment: 12-1/4" Pilot Hole'),
        ("589", 'Guideline 1110fix — Conductor Installation'),
        ("590", 'Guideline 1130fix — Conductor Drill/Drive'),
        ("665", 'Guideline 5500sem — Heave Compensation Systems'),
        ("689", 'Guideline 8300sem — Heavy Weather Policy'),
],
    "cementing_program": [
        ("001", "13-3/8\" & 13-5/8\" Casing Running & Cementing Procedure (E001S)"),
        ("021", "SI#09 Cement Program Plug MD850"),
        ("024", "SI#09 Cement Program Plug w150 MD2185"),
        ("186", "Cementing Plug Program @1564m, 118 PCF"),
            ("616", 'Guideline 3010 — Cementing: Responsibilities'),
        ("617", 'Guideline 3020 — Cementing: Pre-Job Checklist'),
        ("618", 'Guideline 3030 — Cementing: Operations Checklist'),
        ("619", 'Guideline 3040 — Cementing: Programme Checklist'),
        ("620", 'Guideline 3050 — Cement and Additives'),
        ("627", 'Guideline 3350 — 9-5/8" Cementation'),
        ("628", 'Guideline 3450 — 7" Liner Cementation & Clean-out'),
],
    "well_kill_program": [
        ("035", "WELL Killing well procedure No8"),
        ("052", "پس از اطمینان از عدم جریان چاه (kill confirmation)"),
            ("570", 'Guideline 0400 — Well Control Procedures'),
        ("571", 'Guideline 0402 — Well Control in High Angle/Horizontal Wells'),
        ("573", 'Guideline 0405 — Limited Kick Tolerance'),
        ("574", 'Guideline 0410 — Shallow Gas Procedures'),
],
    "fishing_program": [
        ("085", "Backoff and Colliding Standard procedure"),
        ("106", "E. Back off plan"),
        ("122", "SLD backoff-Colliding procedure"),
            ("667", 'Guideline 6005 — Calculation of Optimum Fishing Time'),
        ("670", 'Guideline 6050 — Jar Placement and Jarring Practices'),
        ("672", 'Guideline 6150 — Free Point Determination & Back-Off'),
        ("673", 'Guideline 6200 — Fishing: Procedures and Tools'),
        ("675", 'Guideline 6410 — Casing Milling'),
        ("676", 'Guideline 6420 — Section Milling'),
],
    "coiled_tubing_program": [
        ("093", "D Instruction — 3-1/2\" LNR clean-out & displace by CT"),
        ("094", "D Instruction — RIH W2.125\" nozzle on CT & displace"),
    ],
    "stimulation_program": [
        ("083", "Azar-05 acidizing"),
        ("171", "AZN-10 Well Stimulation Program + Lab report Rev.01"),
    ],
    "abandonment_program": [
        ("026", "TEMPORARY ABANDONMENT PROCEDURE No11"),
        ("010", "Cement Plug & Continue drilling Procedure No3"),
            ("678", 'Guideline 6500 — Bit Nozzle Removal'),
],
    "well_testing_program": [
        ("090", "Clean-up and Well Test Operation Procedure"),
        ("140", "Well testing procedure"),
        ("212", "Well Test Program for South Azadegan"),
            ("680", 'Guideline 7100 — Leak-Off Testing'),
        ("573", 'Guideline 0405 — Limited Kick Tolerance'),
],
    "hpht_drilling_program": [
        ("197", "Drilling Program for (ISHPS)"),
        ("199", "Drilling Program ISHPS"),
    ],
    "horizontal_shale_program": [
        ("102", "Drilling program (F03-Area II)"),
        ("201", "Drilling program (F02-Area II)"),
    ],
    "tripping_procedure": [
        ("103", "Drilling to Shoe, Displace"),
        ("012", "Condition the well to 2300m"),
    ],
    "running_casing_procedure": [
        ("001", "13-3/8\" & 13-5/8\" Casing Running & Cementing Procedure (E001S)"),
        ("002", "13-5/8\" CSG running procedure well SI-09"),
        ("144", "Work instruction to run casing"),
        ("143", "Work instruction for running fishing 24"),
    ],
    "bop_test_procedure": [
        ("139", "Well Control Procedure Questions"),
        ("151", "Well controll procedure tests"),
            ("577", 'Guideline 0420f — Surface BOP Testing'),
        ("578", 'Guideline 0420s — Subsea BOP Testing'),
        ("579", 'Guideline 0440j — Pressure Testing 21-1/4" BOP'),
        ("580", 'Guideline 0441j — Pressure Testing 13-5/8" BOP'),
        ("576", 'Guideline 0415 — Cold Weather Effect on BOP Stacks'),
],
    "kick_circulation_procedure": [
        ("035", "WELL Killing well procedure No8"),
            ("570", 'Guideline 0400 — Well Control Procedures'),
        ("572", 'Guideline 0403 — Well Control Whilst Logging'),
        ("573", 'Guideline 0405 — Limited Kick Tolerance'),
],
    "stuck_pipe_procedure": [
        ("122", "SLD backoff-Colliding procedure"),
        ("106", "E. Back off plan"),
            ("668", 'Guideline 6010 — Freeing Differentially Stuck Pipe (U-Tube)'),
        ("669", 'Guideline 6020 — Freeing Stuck Pipe Riserless/Fixed'),
        ("670", 'Guideline 6050 — Jar Placement and Jarring Practices'),
        ("671", 'Guideline 6100 — Effective Pull on Stuck Pipe'),
        ("674", 'Guideline 6250 — Stuck Logging Tools'),
],
    "slickline_procedure": [
        ("126", "SlickLine Azar Job Procedure"),
    ],
    "esp_running_procedure": [
        ("163", "25 Wells ESP Running Program"),
        ("203", "ESP 2"),
    ],
    "packer_setting_procedure": [
        ("119", "S.N Packer procedure"),
            ("650", 'Guideline 5200 — Packer: Tie-back (Compression Set)'),
        ("653", 'Guideline 5215 — Bridge Plug Setting'),
        ("654", 'Guideline 5220 — EZ Drill-SV Squeeze Packers'),
],
    "perforation_procedure": [
        ("097", "DST-TCP Procedure, , F18"),
        ("127", "TLC job procedures for company-man"),
    ],
    "dst_procedure": [
        ("097", "DST-TCP Procedure, , F18"),
        ("150", "Sampling with full procedure"),
            ("573", 'Guideline 0405 — Limited Kick Tolerance (DST-related)'),
],
    "wellhead_installation_procedure": [
        ("144", "Work instruction to run casing"),
        ("001", "Casing Running & Cementing Procedure (E001S) — wellhead section"),
            ("604", 'Guideline 2105fix — Cutting Casing to Accept Wellhead'),
        ("605", 'Guideline 2200fix — Running 20/18-5/8" Casing'),
        ("607", 'Guideline 2300fix — Running 13-3/8" Casing'),
],
    "lost_circulation_procedure": [
        ("044", "در انتهای حفاری و همزمان با کاهش هرزروی"),
        ("017", "KGDS C-Barite Plug Program, Siah Makan"),
        ("086", "Barite Plug Program Rev02"),
            ("642", 'Guideline 4300 — Lost Circulation'),
        ("640", 'Guideline 4200 — Barytes Plug (Water-Based Mud)'),
        ("641", 'Guideline 4250 — Barytes Plug (Oil-Based Mud)'),
],
    "rig_move_procedure": [
        ("005", "17.5\" HS Drilling Instruction (rig prep section)"),
            ("688", 'Guideline 8200jak — Jacking Procedures'),
        ("687", 'Guideline 8160jak — Pulling Away from Fixed Structures'),
],
    "h2s_emergency_procedure": [
        ("139", "Well Control Procedure Questions (H2S section)"),
            ("564", 'Guideline 0120g2 — H2S (Hydrogen Sulphide) Procedures'),
        ("565", 'Guideline 0120g3 — H2S (Hydrogen Sulphide) Procedures'),
],
    "tubing_pressure_test_procedure": [
        ("104", "Dry Test PROCEDURE"),
        ("105", "Dry test procedure"),
    ],
    "bha_makeup_procedure": [
        ("014", "Drilling and handling Tools"),
        ("015", "Handling Equipment Requirements"),
            ("583", 'Guideline 1020 — Pipe Tally Procedure'),
        ("664", 'Guideline 5460 — Drill String Lifting & Handling'),
],
    "casing_running_cementing_procedure": [
        ("001", "13-3/8\" & 13-5/8\" Casing Running & Cementing Procedure (E001S)"),
        ("002", "13-5/8\" CSG running procedure well SI-09"),
        ("003", "13-5/8\" CSG running procedure well SI-09 (PDF)"),
        ("058", "13-3/8\" Casing Running & Cementing Procedure W014N"),
        ("064", "20\" Casing Running & Cementing Procedure W014N"),
        ("073", "9-5/8\" Casing Running & Cementing Procedure W014N"),
            ("602", 'Guideline 2100jak — 30" Conductor Stab-in Cement'),
        ("605", 'Guideline 2200fix — 20/18-5/8" Casing Running'),
        ("607", 'Guideline 2300fix — 13-3/8" Casing Running'),
        ("609", 'Guideline 2500fix — 7" Casing Running'),
        ("601", 'Guideline 2010 — Casing Centralisation'),
],
    "cement_plug_procedure": [
        ("021", "SI#09 Cement Program Plug MD850"),
        ("022", "SI#09 Cement Program Plug MD2146"),
        ("023", "SI#09 Cement Program Plug MD2347"),
        ("024", "SI#09 Cement Program Plug w150 MD2185"),
        ("025", "SI#09 Cement Program Plug w150 MD2150"),
        ("186", "Cementing Plug Program @1564m 118 PCF"),
        ("188", "Cementing Plug Program @4100m 118 PCF Rig201"),
    ],
    "nisoc_kill_procedure": [
        ("035", "WELL Killing well procedure No8"),
        ("052", "پس از اطمینان از عدم جریان چاه (kill confirmation)"),
        ("032", "Secure well Procedure SI#09"),
    ],
}

# ----------------------------------------------------------------------------
# Category -> representative docs (for the library browser quick view)
# ----------------------------------------------------------------------------

CATEGORY_EXAMPLES: Dict[str, List[str]] = {
    "Casing Running & Cementing": ["001", "002", "003", "058", "064", "073"],
    "Cementing & Plugs": ["021", "022", "023", "024", "025", "186", "187"],
    "Drilling Programs": ["152", "196", "197", "200", "201", "207", "214"],
    "Workover Programs": ["173", "174", "177", "185"],
    "Drilling Procedures": ["004", "031", "050", "057", "061", "066", "068"],
    "Well Control": ["032", "035", "036"],
    "Sidetrack / Whipstock": ["053", "107", "112", "141"],
    "Fishing / Backoff": ["085", "106", "122"],
    "Testing (LOT/DST/Dry)": ["087", "097", "104", "148"],
    "Liner & Tie-Back": ["060", "069", "070", "071", "072"],
    "ESP": ["163", "203"],
    "Stimulation": ["083", "171"],
    "HSE & Waste": ["169", "175"],
}

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def list_library_files() -> List[Tuple[str, Path]]:
    """Return (stem, path) for all library text files."""
    if not LIBRARY_DIR.exists():
        return []
    out = []
    for f in sorted(LIBRARY_DIR.glob("*.txt")):
        if f.stem == "INDEX":
            continue
        out.append((f.stem, f))
    return out


def get_reference_docs(template_key: str) -> List[Tuple[str, str]]:
    """Return [(file_stem, label)] for a template key."""
    return TEMPLATE_REFERENCES.get(template_key, [])


def reference_markdown(template_key: str) -> str:
    """Build a 'Reference Documents' markdown section for the output doc."""
    refs = get_reference_docs(template_key)
    if not refs:
        return ""
    lines = ["## REFERENCE DOCUMENTS (REAL OPERATIONS LIBRARY)", ""]
    lines.append("The following field documents from the operations library "
                 "were used to enrich this document:")
    lines.append("")
    lines.append("| # | Reference Document |")
    lines.append("|---|---|")
    for stem, label in refs:
        lines.append(f"| | {label} `[{stem}]` |")
    lines.append("")
    return "\n".join(lines)
