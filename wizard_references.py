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
    ],
    "advanced_drilling_program": [
        ("152", "Well Drilling Program Rev.02 (2021)"),
        ("214", "Drilling & Completion Programme"),
        ("102", "Drilling program Rev 0.3"),
        ("196", "Drilling Program for"),
        ("200", "Drilling program"),
        ("201", "Drilling program (F02-Area II)"),
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
    ],
    "cementing_program": [
        ("001", "13-3/8\" & 13-5/8\" Casing Running & Cementing Procedure (E001S)"),
        ("021", "SI#09 Cement Program Plug MD850"),
        ("024", "SI#09 Cement Program Plug w150 MD2185"),
        ("186", "Cementing Plug Program @1564m, 118 PCF"),
    ],
    "well_kill_program": [
        ("035", "WELL Killing well procedure No8"),
        ("052", "پس از اطمینان از عدم جریان چاه (kill confirmation)"),
    ],
    "fishing_program": [
        ("085", "Backoff and Colliding Standard procedure"),
        ("106", "E. Back off plan"),
        ("122", "SLD backoff-Colliding procedure"),
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
    ],
    "well_testing_program": [
        ("090", "Clean-up and Well Test Operation Procedure"),
        ("140", "Well testing procedure"),
        ("212", "Well Test Program for South Azadegan"),
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
    ],
    "kick_circulation_procedure": [
        ("035", "WELL Killing well procedure No8"),
    ],
    "stuck_pipe_procedure": [
        ("122", "SLD backoff-Colliding procedure"),
        ("106", "E. Back off plan"),
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
    ],
    "perforation_procedure": [
        ("097", "DST-TCP Procedure, , F18"),
        ("127", "TLC job procedures for company-man"),
    ],
    "dst_procedure": [
        ("097", "DST-TCP Procedure, , F18"),
        ("150", "Sampling with full procedure"),
    ],
    "wellhead_installation_procedure": [
        ("144", "Work instruction to run casing"),
        ("001", "Casing Running & Cementing Procedure (E001S) — wellhead section"),
    ],
    "lost_circulation_procedure": [
        ("044", "در انتهای حفاری و همزمان با کاهش هرزروی"),
        ("017", "KGDS C-Barite Plug Program, Siah Makan"),
        ("086", "Barite Plug Program Rev02"),
    ],
    "rig_move_procedure": [
        ("005", "17.5\" HS Drilling Instruction (rig prep section)"),
    ],
    "h2s_emergency_procedure": [
        ("139", "Well Control Procedure Questions (H2S section)"),
    ],
    "tubing_pressure_test_procedure": [
        ("104", "Dry Test PROCEDURE"),
        ("105", "Dry test procedure"),
    ],
    "bha_makeup_procedure": [
        ("014", "Drilling and handling Tools"),
        ("015", "Handling Equipment Requirements"),
    ],
    "casing_running_cementing_procedure": [
        ("001", "13-3/8\" & 13-5/8\" Casing Running & Cementing Procedure (E001S)"),
        ("002", "13-5/8\" CSG running procedure well SI-09"),
        ("003", "13-5/8\" CSG running procedure well SI-09 (PDF)"),
        ("058", "13-3/8\" Casing Running & Cementing Procedure W014N"),
        ("064", "20\" Casing Running & Cementing Procedure W014N"),
        ("073", "9-5/8\" Casing Running & Cementing Procedure W014N"),
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
