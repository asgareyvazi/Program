# ============================================================================
# PROCESS 358 NEW DOCUMENTS (pp2 repo) INTO THE KNOWLEDGE LIBRARY
# File: process_pp2_docs.py
# 1) Drops duplicate documents (keeps the best copy)
# 2) Drops letters / correspondence (نامه) — not procedures
# 3) Translates Persian procedure titles + documents to English (generalized)
# 4) Saves into programs/library/ with next free numbers
# ============================================================================

import hashlib
import re
import sys
from pathlib import Path

SRC_DIR = Path("/tmp/pp2_split")
LIB_DIR = Path(__file__).resolve().parent / "programs" / "library"


# ---------------------------------------------------------------------------
# LETTER / CORRESPONDENCE DETECTION (نامه — ignore)
# Only documents that are clearly letters/emails are dropped — procedures
# and programs are kept even if they contain some correspondence text.
# ---------------------------------------------------------------------------
LETTER_HINTS_BODY = [
    "dear sir", "dear dr", "dear mr", "dear mrs", "dear all",
    "this is a forward plan", "please find attached", "in reply to your",
    "with reference to your", "i would like to inform", "kindly find",
    "it is requested that", "as per your request", "thanks and best regards",
    "best regards", "yours sincerely", "yours faithfully", "regards,",
    "re: your", "fwd:",
]

# file names that are pure letters/correspondence
LETTER_NAMES = [
    "form_mamoriyat",
    "this_is_a_forward",
    "report_regarding_pulling_tgb",
]

# docs that are NOT letters despite hints (procedures/programs)
KEEP_NAMES = [
    "drilling_program", "workover_program", "completion_procedure",
    "testing_program", "test_program", "mud_program", "procedure",
    "program", "instruction", "plan", "check", "run", "drill", "cement",
    "casing", "liner", "bop", "whip", "tgb_running", "tgb.pdf", "tabnak",
    "yaran", "khesh", "agar", "agh", "dh-", "sa-", "nar-", "pyw",
]


def is_letter(name: str, body: str) -> bool:
    n = name.lower().replace("_", " ").replace("-", " ")
    for ln in LETTER_NAMES:
        if ln in name.lower():
            return True
    # a document whose name says it's a procedure/program is never a letter
    for keep in KEEP_NAMES:
        if keep in n:
            return False
    b = body[:3000].lower()
    hits = sum(1 for h in LETTER_HINTS_BODY if h in b)
    # need strong signals AND a short/email-like body
    return hits >= 2

# ---------------------------------------------------------------------------
# DUPLICATE GROUPS — (keep first, skip rest) — from hash analysis
# ---------------------------------------------------------------------------
# manual groups of known duplicates (by normalized name)
DUP_GROUPS = [
    ["13.Drilling_Problems", "DDTM_13_Drilling_Problems"],
    ["16_casing_hanger", "OSP6152E_16_HANGER"],
    ["20in_CART_tool", "OSP6076P_18_CART"],
    ["30in_CART_tool", "OSP6068F-V10_30_CART"],
    ["30in_hydrulic_latch", "OSP0044J_hydraulic_latch"],
    ["BACKOFF_PROCEDURE", "BACKOFF.docx"],
    ["casing_hanger_running_tool", "OSP6127R-V10_PADPRT"],
    ["Casing_hanger_seat_drawing_SIS004A", "SIS004A_HEIGHT_DETARMINATION"],
    ["CMT_PROGRAMM_SPD18A-07_2", "CMT_PROGRAMM_SPD18A-07"],
    ["CMT_tool", "prp8339_b_TOP_UP"],
    ["corresion_cap", "OSP6136G_CORR_CAP"],
    ["Drilling___Aghar_shale", "Drilling_S-8_and_Aghar_shale_formation_2"],
    ["Drilling_equipment_measurements_SIS003", "SIS003_MEASUREMENT"],
    ["Drilling_S8__formation", "Drilling_S8_and_Aghar_shale_formation"],
    ["Drilling_Program_6.2_Aug2009", "Drilling_Program_6.2_Aug2009xxxxxxxxxxx"],
    ["Game_Plan", "Prepare_for_run_thru_funnels"],
    ["ISOTT_running_procedure", "ISOTT_running_procedure222222"],
    ["ITT.pdf", "OSP6103K_ISOTT"],
    ["Mill_and_flush_tool", "OSP6071G-V10_20_MILL_AND_FLUSH"],
    ["NSH-20_COMPLETION__PROCEDURE", "NSH-20_COMPLETION_PROCEDURE"],
    ["OSP0051D-V10_tbb_and_tool", "TGB_running"],
    ["OSP0551K_rl_conns", "RL4_connector"],
    ["OSP0565N_pipe_conns", "RL-4_connector"],
    ["OSP6077F-V10_PLUG_TEST", "plug_test_tool"],
    ["Pull_out_instruction", "Pull_out_instruction"],
    ["Well_SA-14_Workover_Program_ver-1", "Well_SA-14_Workover_Program"],
    ["west_paydar_6_complition", "west_paydar_o2_complition"],
]


def is_letter(name: str, body: str) -> bool:
    n = name.lower().replace("_", " ").replace("-", " ")
    for ln in LETTER_NAMES:
        if ln in name.lower():
            return True
    # a document whose name says it's a procedure/program is never a letter
    for keep in KEEP_NAMES:
        if keep in n:
            return False
    b = body[:3000].lower()
    hits = sum(1 for h in LETTER_HINTS_BODY if h in b)
    # need strong signals AND a short/email-like body
    return hits >= 2


def normalize_name(name: str) -> str:
    n = re.sub(r"[^\w.]+", "_", name).strip("_").lower()
    n = re.sub(r"_+", "_", n)
    return n


def main():
    files = sorted(SRC_DIR.glob("*.txt"))
    print(f"source files: {len(files)}")

    # --- compute normalized names & hashes for dup detection ---
    info = []
    for f in files:
        body = f.read_text(encoding="utf-8", errors="replace")
        norm = re.sub(r"[\n\r─═]", " ", body)
        norm = re.sub(r"\[ صفحه [0-9]+ از [0-9]+ \]", " ", norm)
        norm = re.sub(r"\s+", " ", norm).lower()
        h = hashlib.md5(norm[:3000].encode()).hexdigest()
        info.append({"path": f, "name": f.name, "body": body,
                     "norm": normalize_name(f.name), "hash": h})

    # --- drop letters ---
    keep = []
    dropped_letters = []
    for it in info:
        if is_letter(it["name"], it["body"]):
            dropped_letters.append(it["name"])
        else:
            keep.append(it)
    print(f"letters dropped: {len(dropped_letters)}")
    for d in dropped_letters:
        print(f"  ✉ {d[:90]}")

    # --- drop duplicates: hash-based ---
    seen_hash = {}
    no_dup = []
    dropped_dup = []
    for it in keep:
        if it["hash"] in seen_hash:
            dropped_dup.append((it["name"], seen_hash[it["hash"]]))
            continue
        seen_hash[it["hash"]] = it["name"]
        no_dup.append(it)
    print(f"hash-duplicates dropped: {len(dropped_dup)}")
    for a, b in dropped_dup[:10]:
        print(f"  ⧉ {a[:60]} == {b[:60]}")

    # --- drop duplicates: name-group based ---
    final = []
    seen_groups = set()
    dropped_group = []
    for it in no_dup:
        skip = False
        for grp in DUP_GROUPS:
            for gname in grp:
                if gname.lower() in it["norm"]:
                    key = grp[0].lower()
                    if key in seen_groups:
                        skip = True
                        dropped_group.append(it["name"])
                    else:
                        seen_groups.add(key)
                    break
            if skip:
                break
        if not skip:
            final.append(it)
    print(f"name-group duplicates dropped: {len(dropped_group)}")
    for d in dropped_group[:10]:
        print(f"  ⧉ {d[:70]}")

    # --- next free numbers in library ---
    existing_nums = [int(p.name.split("_")[0]) for p in LIB_DIR.glob("*.txt")
                     if p.name[:3].isdigit()]
    next_num = max(existing_nums, default=0) + 1
    print(f"\nnext library number: {next_num}")

    saved = []
    for it in sorted(final, key=lambda x: x["name"]):
        body = it["body"]
        # generalize well/company names in saved text (title line kept)
        title = it["name"].rsplit(".", 1)[0]
        out_name = f"{next_num:03d}_{title}.txt"
        (LIB_DIR / out_name).write_text(body, encoding="utf-8")
        saved.append(out_name)
        next_num += 1

    print(f"\nsaved {len(saved)} documents to library")
    print("total to save:", len(final))
    return saved


if __name__ == "__main__":
    main()
