# ============================================================================
# SEED F-20 TIME BREAKDOWN — AZNS F-20 (PAD-93) Example Project
# File: seed_f20_timebreakdown.py
# Parses the real Time Breakdown table from the F-20 Well Drilling Program
# (programs/library/211_Well Drilling Program-F20-PAD93-Rev-03.pdf.txt) and
# loads it into the Time Breakdown database as an editable example project.
# Column layout of the source table (after Formation):
#   [Depth, ROP?, DurH, DurD, CumD, Time%, cDurH, cDurD, cCumD]
#   Interval appears BEFORE the Formation token.
# PDF text extraction interleaves rows: the head of a row's description may
# be placed on the line(s) before the row number; the row's own line always
# contains the row number + tail of description + IADC + all numeric columns.
# ============================================================================

import re
import sys
from pathlib import Path

from time_breakdown import (
    TimeBreakdownDatabase, TimeBreakdownProject, TimeBreakdownRow,
)

LIB_FILE = Path(__file__).parent / "programs" / "library" / \
    "211_Well Drilling Program-F20-PAD93-Rev-03.pdf.txt"

IADC_CODES = [
    "N/U BOP & BOP Test", "Csg. Running", "Hole Cond/Circ",
    "well Head", "Cut & Slip", "Rig Service", "Slick Line",
    "Drilling", "BOP Test", "Completion", "Trip", "CMT",
    "D/Out", "Survey", "Log", "FIT", "DST", "Perf", "Circ",
]

FORMATION_TOKENS = [
    # combined tokens first (longest match wins on equal position)
    "U-Gu.", "Agh.-Gas.", "Gas.-As.", "Il-La-Sv", "Kz/SV", "Da/Ga.",
    "Ga-FH.", "FH-5b", "Agh.", "Gas.", "FH.", "Kz.", "Da.", "Ga.",
    "As.", "Pb.", "Ja.", "SV", "FH", "KA", "Gd.",
]

SECTION_HEADER_RE = re.compile(
    r"^(26\"|17-1/2\"|12-1/4\"|8-1/2\"|6\") Hole Section\s*/\s*\S+")
SECTION_HEADER_LOOSE_RE = re.compile(
    r"(26\"|17-1/2\"|12-1/4\"|8-1/2\"|6\") Hole Section")


def find_iadc(text: str) -> str:
    """IADC code = the code whose LAST occurrence in the text is latest"""
    best, best_pos = "", -1
    for code in IADC_CODES:
        pos = text.lower().rfind(code.lower())
        if pos > best_pos:
            best, best_pos = code, pos
    return best if best_pos >= 0 else ""


def find_formation_after(text: str) -> str:
    """first formation token at/after a given start — use last occurrence
    of each token; pick the one with the SMALLEST position among tokens
    found after the IADC code (the columns region)"""
    best, best_pos = "", 10 ** 9
    for tok in FORMATION_TOKENS:
        pos = text.rfind(tok)
        if pos >= 0 and pos < best_pos:
            best, best_pos = tok, pos
    return best if best_pos < 10 ** 9 else ""


def parse_numbers(text: str) -> list:
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text)]


def parse_f20() -> list:
    """برمی‌گرداند لیست TimeBreakdownRow های استخراج‌شده"""
    txt = LIB_FILE.read_text(encoding="utf-8", errors="replace")
    start = txt.find("2.3 Time Breakdown")
    end = txt.find("Total Duration of F-20 Well")
    if start < 0 or end < 0:
        raise RuntimeError("Time Breakdown region not found in F-20 file")
    region = txt[start:end]
    lines = region.split("\n")

    row_starts = []  # (line_index, row_number)
    for i, ln in enumerate(lines):
        m = re.match(r"^\s*(\d{1,3})\s+(.*)$", ln)
        if m:
            row_starts.append((i, int(m.group(1))))

    if not row_starts:
        raise RuntimeError("No rows parsed from F-20 file")

    # ---- precompute active section for each line (by position)
    section_by_line = {}
    current_section = ""
    for i, ln in enumerate(lines):
        m = SECTION_HEADER_LOOSE_RE.search(ln)
        if m:
            current_section = m.group(0)
        section_by_line[i] = current_section

    rows_out = []
    for k, (line_idx, num) in enumerate(row_starts):
        current_section = section_by_line.get(line_idx, "")
        # ---- description head: lines between previous row and this row
        head_parts = []
        j = line_idx - 1
        while j >= 0:
            prev = lines[j].strip()
            if not prev:
                break
            if re.match(r"^\d{1,3}\s", prev) or "Total Duration" in prev:
                break
            if SECTION_HEADER_RE.match(prev):
                break
            head_parts.insert(0, prev)
            j -= 1

        # ---- body: the row's own line only (columns + tail of description)
        body = lines[line_idx].strip()

        raw = re.sub(r"\s+", " ", " ".join(head_parts + [body]))

        iadc = find_iadc(raw)
        iadc_pos = raw.lower().rfind(iadc.lower()) if iadc else -1

        # description = everything before the IADC token
        desc = raw
        if iadc_pos > 0:
            desc = raw[:iadc_pos]
        desc = re.sub(r"^\d{1,3}\s*", "", desc).strip(" .-–—")
        if not desc:
            desc = raw

        # numeric columns region: after IADC (and after formation)
        columns_text = raw[iadc_pos + len(iadc):] if iadc_pos >= 0 else raw
        formation = find_formation_after(columns_text)
        fpos = columns_text.rfind(formation) if formation else -1
        if formation and fpos >= 0:
            before = columns_text[:fpos]
            after = columns_text[fpos + len(formation):]
        else:
            before, after = columns_text, ""

        interval = 0.0
        nb = parse_numbers(before)
        if nb:
            interval = nb[-1]  # last number before formation = interval

        nums = parse_numbers(after)
        depth = rop = dur_h = dur_d = cum_d = 0.0
        c_dur_h = c_dur_d = c_cum_d = 0.0
        n = len(nums)
        if n >= 7:
            c_cum_d = nums[-1]
            c_dur_d = nums[-2]
            c_dur_h = nums[-3]
            # nums[-4] = Time %
            cum_d = nums[-5]
            dur_d = nums[-6]
            dur_h = nums[-7]
            if n >= 9:
                depth = nums[-9]
                rop = nums[-8]
            elif n >= 8:
                # no ROP column for trip-type rows: 8th number is Depth
                depth = nums[-8]

        rows_out.append(TimeBreakdownRow(
            row_number=num,
            section_name=current_section,
            operation_description=desc,
            iadc_code=iadc,
            interval_m=interval,
            formation=formation,
            depth_m=depth,
            rop=rop,
            duration_hours=dur_h,
            duration_days=dur_d,
            cumulative_days=cum_d,
            is_section_header=False,
            is_contingency=False,
        ))
    return rows_out


def seed(force: bool = False) -> TimeBreakdownProject:
    db = TimeBreakdownDatabase()
    try:
        existing = [p for p in db.get_all_projects()
                    if "F-20" in (p.get("name") or "")]
        if existing and not force:
            print(f"✔ AZNS F-20 example already exists "
                  f"(project id {existing[0]['id']}) — skipping. "
                  f"Use --force to reload.")
            return None

        rows = parse_f20()

        # insert section header rows before the first row of each section
        headers = ["26\" Hole Section / 20\" Casing",
                   "17-1/2\" Hole Section / 13-3/8\" Casing",
                   "12-1/4\" Hole Section / 9-5/8\" Casing",
                   "8-1/2\" Hole Section / 7\" Liner"]
        for h in reversed(headers):
            sec = h.split(" / ")[0]
            first = next((i for i, r in enumerate(rows)
                          if r.section_name.startswith(sec)), None)
            if first is not None:
                rows.insert(first, TimeBreakdownRow(
                    row_number=0, section_name=h,
                    operation_description=h, is_section_header=True))

        proj = TimeBreakdownProject(
            name="Example — Standard Drilling & Completion Program",
            well_name="Example Well",
            field_name="Example Field",
            operator="the Operator",
            unit_system="Metric",
            notes=("Real Time Breakdown from Well Drilling Program "
                   "F-20 PAD-93 Rev.03 (Oct 2024). Total: 114.0 days "
                   "(125.6 days w/ contingency)."),
            rows=rows,
            created_date="2026-08-11",
            modified_date="2026-08-11",
        )
        db.save_project(proj)

        # section totals for verification
        totals = {}
        for r in rows:
            if r.section_name:
                totals.setdefault(r.section_name, [])
                totals[r.section_name].append(r.cumulative_days)
        print(f"✔ Seeded AZNS F-20 example: {len(rows)} rows")
        for sec, vals in totals.items():
            print(f"   • {sec}: last cumulative = {max(vals):.1f} d")
        last = max((r.cumulative_days for r in rows), default=0)
        print(f"   • TOTAL (w/o contingency): {last:.1f} days "
              f"(reference: 114.0)")
        return proj
    finally:
        db.close()


if __name__ == "__main__":
    seed(force="--force" in sys.argv)
