# ============================================================================
# IMPORT COMPANY PRICE TABLE INTO CBS + TIME BREAKDOWN
# File: seed_azns_prices.py
# Reads the imported price table (22 sheets, saved in the internal
# knowledge library) and:
#   1) imports every priced goods/service item into the CBS database
#      (unit price, unit, qty, source = "Company price table (Rev 07)");
#      existing catalog items are matched by name and their price filled in;
#   2) rebuilds the Time Breakdown example project with the Rev#07 schedule
#      (131.82 days, 145.00 days w/ contingency).
# All prices remain user-editable defaults in the CBS tab.
# ============================================================================

import re
import sys
from pathlib import Path

from cbs_db import CBSDatabase, CbsItem
from time_breakdown import (
    TimeBreakdownDatabase, TimeBreakdownProject, TimeBreakdownRow,
)

PRICE_FILE = Path(__file__).parent / "programs" / "library" / \
    "216_AZNS-F-20_Price_Table_Rev07.txt"
SRC = "Company price table (Rev 07)"

# ---------------------------------------------------------------------------
# SHEET 1 → TIME BREAKDOWN
# ---------------------------------------------------------------------------

IADC_CODES = ["N/U BOP & BOP Test", "Csg. Running", "Hole Cond/Circ",
              "well Head", "Cut & Slip", "Rig Service", "Slick Line",
              "Drilling", "BOP Test", "BOP TEST", "Completion", "Trip",
              "CMT", "D/Out", "Survey", "Log", "FIT", "DST", "Perf", "Cir.",
              "CSG", "WOC", "N/U WH", "N/U BOP", "Testing"]

FORMATION_TOKENS = ["U-Gu.", "Agh.-Gas.", "Gas.-As.", "Il-La-Sv", "Kz/SV",
                    "Da/Ga.", "Ga-FH.", "FH-5b", "AS/Pb.-Ja.", "Pb.-Ja.",
                    "Ja.-Pb.", "Agh.", "Gas.", "FH.", "Kz.", "Da.", "Ga.",
                    "As.", "Pb.", "Ja.", "Tar.", "L-Gurpi", "SV", "FH", "KA"]

SECTION_HEADER_RE = re.compile(
    r'^(26"|17-1/2"|12-1/4"|8-1/2"|6") Hole Section\s*/\s*\S+')


def _dedupe(parts):
    out = []
    for p in parts:
        p = p.strip()
        if out and out[-1] == p:
            continue
        out.append(p)
    return out


def parse_time_breakdown() -> list:
    """پارس شیت ۱ (Time Breakdown) از فایل قیمت Rev#07"""
    txt = PRICE_FILE.read_text(encoding="utf-8", errors="replace")
    start = txt.find('26" Hole Section / 20" Casing')
    end = txt.find("Total Duration of F-20 Well")
    if start < 0 or end < 0:
        raise RuntimeError("Sheet-1 region not found in price table file")
    region = txt[start:end]

    rows = []
    current_section = ""
    for ln in region.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        m = SECTION_HEADER_RE.match(ln)
        if m:
            current_section = m.group(0)
            continue
        if "Total Duration of " in ln and "Hole Section" in ln:
            continue
        if "Total Duration of F-20 Well" in ln:
            continue
        parts = _dedupe(ln.split("|"))
        if len(parts) < 4:
            continue

        iadc, iadc_idx = "", -1
        low = [c.lower() for c in IADC_CODES]
        for i, p in enumerate(parts):
            if p.lower() in low:
                iadc, iadc_idx = p, i
                break
        if iadc_idx < 0:
            continue

        desc = parts[0]
        # clean the two "Total Duration for ..." summary rows
        if desc.lower().startswith("total duration for"):
            desc = re.sub(r"^Total Duration for\s+", "", desc,
                          flags=re.IGNORECASE).strip()
        after = parts[iadc_idx + 1:]

        form, fpos = "", -1
        for i, p in enumerate(after):
            if p in FORMATION_TOKENS:
                form, fpos = p, i
                break
        if not form:
            continue

        nums = [float(p) for p in after[fpos + 1:]
                if re.match(r"^[\d.]+$", p.strip())]
        if not nums:
            continue

        depth = nums[0]
        rest = nums[1:]
        rop = 0.0
        if len(rest) >= 8:
            rop = rest[0]
            rest = rest[1:]
        names = ["ccumd", "cdurd", "cdurh", "cont", "cumd", "durd", "durh"]
        vals = {k: 0.0 for k in names}
        for i, v in enumerate(reversed(rest)):
            if i < len(names):
                vals[names[i]] = v

        # keep descriptions general — no company/well/reservoir names
        from cbs_db import generalize_text
        desc = re.sub(r"as per NIOC policy", "as per Company policy",
                      desc, flags=re.IGNORECASE)
        desc = re.sub(r"per NIOC policy", "per Company policy",
                      desc, flags=re.IGNORECASE)
        desc = re.sub(r"NIOC", "Company", desc, flags=re.IGNORECASE)
        desc = generalize_text(desc)

        rows.append(TimeBreakdownRow(
            row_number=len(rows) + 1,
            section_name=current_section,
            operation_description=desc,
            iadc_code=iadc,
            interval_m=0.0,
            formation=form,
            depth_m=depth,
            rop=rop,
            duration_hours=vals["durh"],
            duration_days=vals["durd"],
            cumulative_days=vals["cumd"],
            is_contingency=False,
        ))
    return rows


def seed_time_breakdown(force: bool = True):
    db = TimeBreakdownDatabase()
    try:
        existing = [p for p in db.get_all_projects()
                    if any(t in (p.get("name") or "") for t in
                           ("F-20", "AZNS", "Example"))]
        for p in existing:
            db.delete_project(p["id"])

        rows = parse_time_breakdown()
        # insert section header rows
        headers = ['26" Hole Section / 20" Casing',
                   '17-1/2" Hole Section / 13-3/8" Casing',
                   '12-1/4" Hole Section / 9-5/8" Casing',
                   '8-1/2" Hole Section / 7" Liner']
        for h in reversed(headers):
            sec = h.split(" / ")[0]
            first = next((i for i, r in enumerate(rows)
                          if r.section_name.startswith(sec)), None)
            if first is not None:
                rows.insert(first, TimeBreakdownRow(
                    row_number=0, section_name=h,
                    operation_description=h, is_section_header=True))

        proj = TimeBreakdownProject(
            name="Example — Standard Drilling & Completion Program (Rev 07)",
            well_name="Example Well",
            field_name="Example Field",
            operator="the Operator",
            unit_system="Metric",
            notes=("Example Time Breakdown: standard drilling & "
                   "completion program with perforation and rig-less "
                   "stimulation. Total: 131.82 days (145.00 days w/ "
                   "contingency). All values are editable."),
            rows=rows,
            created_date="2026-08-11",
            modified_date="2026-08-11",
        )
        db.save_project(proj)
        last = max((r.cumulative_days for r in rows), default=0)
        print(f"✔ Time Breakdown (Rev#07): {len(rows)} rows, "
              f"total = {last:.2f} days (ref 131.82)")
        return proj
    finally:
        db.close()


# ---------------------------------------------------------------------------
# SHEETS 2-22 → CBS PRICES
# ---------------------------------------------------------------------------

UNITS = {"day", "days", "job", "jobs", "m", "hole", "holes", "bbl", "gal",
         "lb", "ea.", "ea", "set", "sets", "run", "runs", "well", "wells",
         "each", "meter", "load", "loads", "sum/hole", "lumpsum", "man-day",
         "person/day", "1 ea", "1 set", "1 lot", "1 pack", "1set", "lump",
         "lump sum", "pad", "joint", "kit", "box", "day ", "set."}

# name -> (category, keep_if_zero)
CATEGORY_MAP = [
    (r"rig servic|rig rental|spread|mob|demob|rig mov|mission cost",
     "1. Rig & Dayrates"),
    (r"mud engineer|mud chemic|drilling fluid|mud logging|communication "
     r"service|real time data",
     "3. Drilling Fluids & Chemicals" if "mud" in "" else "2. Drilling Services"),
    (r"cementing|cement |cmt", "4. Cementing"),
    (r"wire ?line|logging|log |survey|mwd|lwd|directional|multishot|mdt|"
     r"cbl|vdl|cast|usit|sbt|pl\.?t|fsi|flagship|spectral|multifinger|hpht",
     "7. Well Control & Testing"),
    (r"casing runn|tubing runn|liner hanger runn|completion runn",
     "2. Drilling Services"),
    (r"h2s|perforat|depth charge|tcp guns|dry test|slick ?line|memory "
     r"gauge|pvt|dst ",
     "7. Well Control & Testing"),
    (r"waste|cutting fixation|cuttings", "8. Waste Management Equipment"),
    (r"casing,|liner,|tubing,|pup joint|crossover|centralizer|stop collar|"
     r"float shoe|float collar|cement plug|cement basket|drift gauge|"
     r"thread lock|thread seal|stage collar|scratcher|stab-in|duplex shoe",
     "5. Tubulars & Connectors"),
    (r"completion equipment|wellhead|x-mas tree|well head &|liner hanger,|"
     r"liner top packer|bridge plug|whip ?stock|10k completion|section [abcd]",
     "6. Completion Equipment"),
    (r"bit|mill|drill bit", "2. Drilling Services"),
    (r"project management|planning and cost|management|engineering|"
     r"geological forecast|drilling / workover program|operation program|"
     r"completion program|final well|final hse|car rental|ambulance|"
     r"catering|accommodation",
     "9. Overheads & Contingency"),
    (r"hcl|corrosion inhibitor|emulsifier|gelling|iron control|cross linker|"
     r"buffering|anti-sludge|h2s scavenger|suspending|acetic acid|"
     r"surfactant|foaming|clay stabilizer|mutual solvent|sdves|xylene|"
     r"friction reducer|retarding|liquid nitrogen|defoaming|iron "
     r"stabilizer|gel breaker|benzoic|oil soluble|ammonium|caustic soda|"
     r"water|diesel|fractur|twin pump|batch mixer|blender|data acquis|"
     r"acid and chemical|booster pump|acid testing|acid storage|acid "
     r"mixing|water/diesel tank|crane|nitrogen unit|nitrogen tank|"
     r"corrosive fluid|non-corrosive|coiled tubing|cleanout|fishing|"
     r"oil storage|oil pumping|oil transport|choke manifold|data header|"
     r"ssv|esd|separator|gauge tank|surge tank|oil manifold|gas manifold|"
     r"flare|heater|transfer pump|chemical injection|air compressor|"
     r"burner|pipes/hoses|piping|sampler bottle|generator|test kit|"
     r"lubricator|stuff box|string components|tool box|stuff",
     "10. Stimulation & Well Services"),
    (r"supervisor|operator|assistant|helper|engineer|specialist|technician|"
     r"personnel",
     "11. Personnel Rates"),
    (r"design|interpretation|report|labaratory|acid lab",
     "12. Design & Reporting"),
    (r"inspection", "5. Tubulars & Connectors"),
]

CBS_CATEGORY = [
    "1. Rig & Dayrates", "2. Drilling Services",
    "3. Drilling Fluids & Chemicals", "4. Cementing",
    "5. Tubulars & Connectors", "6. Completion Equipment",
    "7. Well Control & Testing", "8. Waste Management Equipment",
    "9. Overheads & Contingency", "10. Stimulation & Well Services",
    "11. Personnel Rates", "12. Design & Reporting",
]


def _categorize(name: str) -> str:
    for pat, cat in CATEGORY_MAP:
        if re.search(pat, name, re.IGNORECASE):
            return cat
    return "2. Drilling Services"


def _is_num(s: str) -> bool:
    return bool(re.match(r"^[\d.]+$", s.strip()))


def parse_price_sheets() -> list:
    """پارس شیت‌های ۲-۲۲ و برگرداندن لیست CbsItem"""
    txt = PRICE_FILE.read_text(encoding="utf-8", errors="replace")
    items = []

    # split into sheets by '# Sheet N' comments
    sheet = 0
    lines = txt.splitlines()
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i].strip()
        m = re.match(r"^#\s*Sheet\s+(\d+)", ln)
        if m:
            sheet = int(m.group(1))
            i += 1
            continue
        if not ln or ln.startswith("#"):
            i += 1
            continue
        # skip until first data line of a priced sheet
        if sheet < 2:
            i += 1
            continue
        # collect the whole line (may be the item)
        parts = _dedupe(ln.split("|"))
        # skip headers / totals / section titles
        joined = " ".join(parts)
        if re.search(r"^(table|total|re-entry|stimulation cost|no\.?$|"
                     r"item|1 \||# )", joined, re.I) and len(parts) <= 3:
            i += 1
            continue
        if "Total" in joined and len(parts) <= 3:
            i += 1
            continue

        # Find unit token (first token after the item name that is a unit)
        unit = ""
        uidx = -1
        for j, p in enumerate(parts):
            if p.lower().strip() in UNITS:
                unit = p
                uidx = j
                break
        if uidx < 0:
            i += 1
            continue

        name = " ".join(parts[:uidx]).strip()
        # strip leading row numbers / section numbers
        name = re.sub(r"^\d+(\.\d+)?\s+", "", name).strip(" .-–—")
        from cbs_db import generalize_text
        name = generalize_text(name)
        if not name:
            i += 1
            continue

        nums = [float(p) for p in parts[uidx + 1:]
                if _is_num(p)]
        if not nums:
            i += 1
            continue

        # Determine price/qty/total by sheet layout
        price = qty = total = 0.0
        if sheet == 5 or sheet == 6:
            # [price, qty, total, ...]
            if len(nums) >= 3:
                price, qty, total = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                price, total = nums[0], nums[1]
                qty = 1
            elif len(nums) == 1:
                total = nums[0]
        elif sheet == 11:
            # [qty, price, total]
            if len(nums) >= 3:
                qty, price, total = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                qty, price = nums[0], nums[1]
                total = qty * price
            elif len(nums) == 1:
                price = nums[0]
        elif sheet in (12, 13, 15, 17, 18, 19):
            # standby/operating day rates — take operating rate as unit price
            # layout varies; last number is usually total, price = max rate
            if len(nums) >= 3:
                total = nums[-1]
                # rates are the two numbers before total (standby, operating)
                rates = nums[-3:-1]
                price = max(rates)
                qty = 1
            elif len(nums) == 2:
                price, total = nums[0], nums[1]
                qty = 1
            else:
                price = nums[0]
        elif sheet == 14:
            # [qty, price, total]
            if len(nums) >= 3:
                qty, price, total = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                qty, price = nums[0], nums[1]
                total = qty * price
        elif sheet == 16:
            # wireline: [standby_days, standby_rate, op_days, op_rate, total]
            if len(nums) >= 4:
                total = nums[-1]
                price = nums[-2] if nums[-2] > 0 else nums[-4]
                qty = 1
            elif len(nums) >= 2:
                price, total = nums[0], nums[1]
        elif sheet == 20:
            # personnel: [qty, std_days, op_days, std_rate, op_rate, total]
            if len(nums) >= 4:
                total = nums[-1]
                price = max(nums[-3:-1])
                qty = nums[0] if len(nums) >= 6 else 1
            elif len(nums) >= 2:
                price, total = nums[0], nums[1]
        elif sheet == 21:
            # [qty, price, total]
            if len(nums) >= 3:
                qty, price, total = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                qty, price = nums[0], nums[1]
                total = qty * price
        elif sheet == 22:
            # [qty, price, total]
            if len(nums) >= 3:
                qty, price, total = nums[0], nums[1], nums[2]
            else:
                price = nums[0]
        elif sheet in (10,):
            # mob/demob: [qty, price, total]
            if len(nums) >= 3:
                qty, price, total = nums[0], nums[1], nums[2]
            elif len(nums) == 2:
                qty, price = nums[0], nums[1]
                total = qty * price
        elif sheet in (2, 3, 4, 7, 9):
            # summary sheets — lump totals, skip (they duplicate detail)
            i += 1
            continue
        else:
            i += 1
            continue

        if not price and not total:
            i += 1
            continue

        unit_clean = unit.strip().lower()
        if unit_clean in ("1 ea", "1 set", "1 lot", "1 pack", "1set"):
            unit_clean = unit_clean[1:].strip() or "each"
        elif unit_clean in ("day", "days", "day "):
            unit_clean = "day"
        elif unit_clean == "person/day":
            unit_clean = "person/day"
        elif unit_clean in ("sum/hole", "hole", "holes"):
            unit_clean = "hole"
        elif unit_clean in ("lump", "lump sum", "lumpsum"):
            unit_clean = "lump sum"
        elif unit_clean in ("ea.", "ea", "each", "kit", "box"):
            unit_clean = "each"

        items.append(CbsItem(
            code="",
            category=_categorize(name),
            name=name[:120],
            description="",
            unit=unit_clean,
            unit_price=round(price, 4) if price else 0.0,
            qty=qty,
            is_service=1 if unit_clean == "day" else 0,
            source=SRC,
            price_source=SRC,
        ))
        i += 1
    return items


# ---------------------------------------------------------------------------
# MERGE INTO CBS DATABASE
# ---------------------------------------------------------------------------

def seed_cbs(force: bool = False) -> int:
    """ادغام آیتم‌های قیمت‌نامه در دیتابیس CBS (idempotent)"""
    db = CBSDatabase()
    try:
        # already imported?
        if db.get_setting("azns_imported", "") and not force:
            print("✔ Prices already imported — skipping (--force to re-import).")
            return 0

        imported = parse_price_sheets()
        existing = db.get_items(active_only=False)
        by_name = {}
        for it in existing:
            key = it.name.strip().lower()
            by_name.setdefault(key, []).append(it)

        added = updated = 0
        # canonical-name aliases so imported items merge into existing catalog
        NAME_ALIASES = {
            "rig service": "drilling rig day rate",
            "rig rental": "drilling rig day rate",
        }
        for az in imported:
            key = az.name.strip().lower()
            key = NAME_ALIASES.get(key, key)
            matched = by_name.get(key) or [
                x for k, xlist in by_name.items()
                for x in xlist
                if (len(k) >= 12 and k in key) or (len(key) >= 12 and key in k)]
            if matched:
                target = matched[0]
                if az.unit_price:
                    target.unit_price = az.unit_price
                    target.price_source = SRC
                    target.source = SRC
                if az.unit:
                    target.unit = az.unit
                if az.qty:
                    target.qty = az.qty
                db.save_item(target)
                updated += 1
            else:
                db.save_item(az)
                by_name.setdefault(key, []).append(az)
                added += 1

        # mark imported
        db.set_setting("azns_imported", "1")
        db.set_setting("azns_source", SRC)
        print(f"✔ CBS: {added} added, {updated} updated (total "
              f"{len(db.get_items())} items)")
        return added
    finally:
        db.close()


if __name__ == "__main__":
    force = "--force" in sys.argv
    if "--tb-only" not in sys.argv:
        seed_cbs(force=force)
    if "--cbs-only" not in sys.argv:
        seed_time_breakdown(force=True)
