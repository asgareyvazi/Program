# ============================================================================
# ROPE FIELD CHECKLISTS — Rig Operations Performance Execution
# ============================================================================
# Industry-standard field checklists (Rig Operations Performance Execution
# manual) integrated into the wizard. The manual text lives in
# programs/library/ROPE_Manual.txt and is parsed lazily into checklists
# that are appended to generated documents (company names removed).
# ============================================================================

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROPE_FILE = Path(__file__).resolve().parent / "programs" / "library" / "ROPE_Manual.txt"

_SECTION_RE = re.compile(
    r"^(\d{1,2}\.\d+(?:\.\d+)?(?:\.\w)?)\s+([A-Z][A-Z0-9 &'()\-/–.,]{2,80})$")
_BULLET_RE = re.compile(r"^\s*(?:•|o|-)\s+(.+)$")
_NUM_ITEM_RE = re.compile(r"^\d{1,3}\s+[A-Z][A-Za-z0-9 &'()/.,\-]{12,}$")
_NUMDOT_ITEM_RE = re.compile(r"^\d{1,3}[.)]\s+[A-Z][A-Za-z0-9 &'()/.,\-]{12,}$")


def _clean_item(line: str) -> Optional[str]:
    s = line.strip()
    if not s or len(s) < 10:
        return None
    if "http" in s.lower() or "|" in s:
        return None
    return s


def _parse() -> Dict[str, Dict]:
    """Parse the manual into {section_id: {title, items}}."""
    if not ROPE_FILE.exists():
        return {}
    sections: Dict[str, Dict] = {}
    cur_id: Optional[str] = None
    for raw in ROPE_FILE.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        m = _SECTION_RE.match(s)
        if m and ("CHECKLIST" in m.group(2).upper()
                  or "GUIDELINE" in m.group(2).upper()
                  or "PROCEDURE" in m.group(2).upper()
                  or "REQUIREMENTS" in m.group(2).upper()
                  or "SYSTEM" in m.group(2).upper()
                  or "GENERAL" in m.group(2).upper()
                  or "SPECIAL" in m.group(2).upper()
                  or "WELL CONTROL" in m.group(2).upper()
                  or "EQUIPMENT" in m.group(2).upper()):
            cur_id = m.group(1)
            sections[cur_id] = {"title": m.group(2).strip(), "items": []}
            continue
        if cur_id is None:
            continue
        item = None
        mb = _BULLET_RE.match(s)
        if mb:
            item = mb.group(1).strip()
        else:
            mn = _NUMDOT_ITEM_RE.match(s) or _NUM_ITEM_RE.match(s)
            if mn:
                item = mn.group(0).strip()
        if item:
            clean = _clean_item(item)
            if clean:
                sections[cur_id]["items"].append(clean)
    return sections


_CACHE: Optional[Dict[str, Dict]] = None


def _sections() -> Dict[str, Dict]:
    global _CACHE
    if _CACHE is None:
        _CACHE = _parse()
    return _CACHE


# ----------------------------------------------------------------------------
# Template -> ROPE section mapping
# ----------------------------------------------------------------------------

TEMPLATE_MAP: Dict[str, List[str]] = {
    "tripping_procedure": ["2.40", "2.13"],
    "running_casing_procedure": ["2.3", "2.13"],
    "casing_running_cementing_procedure": ["2.3", "2.4", "2.27"],
    "cementing_program": ["2.4", "2.21"],
    "cement_plug_procedure": ["2.5", "2.27"],
    "bha_makeup_procedure": ["2.1", "2.2", "2.13"],
    "drilling_program": ["2.11", "2.12", "2.13", "2.41"],
    "advanced_drilling_program": ["2.11", "2.12", "2.13", "2.15", "2.18", "2.41"],
    "workover_program": ["2.6", "2.27", "2.29", "3.13"],
    "esp_workover": ["2.27", "2.36", "3.13"],
    "esp_running_procedure": ["2.27", "2.36"],
    "abandonment_program": ["2.27", "2.42"],
    "well_kill_program": ["2.42", "2.41"],
    "nisoc_kill_procedure": ["2.42", "2.41"],
    "well_testing_program": ["2.28", "2.26", "2.14"],
    "dst_procedure": ["2.14", "2.26"],
    "fishing_program": ["2.16", "2.35"],
    "stimulation_program": ["3.10.2"],
    "coiled_tubing_program": ["2.7", "3.10.1"],
    "hpht_drilling_program": ["2.19", "2.42"],
    "deepwater_drilling_program": ["2.33", "2.37", "2.36"],
    "horizontal_shale_program": ["2.9", "2.15"],
    "perforation_procedure": ["3.10.4", "2.24"],
    "slickline_procedure": ["2.34"],
    "wellhead_installation_procedure": ["2.20", "3.13"],
    "lost_circulation_procedure": ["2.25", "2.15"],
    "rig_move_procedure": ["2.30", "3.9"],
    "h2s_emergency_procedure": ["2.41", "2.42", "3.3"],
    "tubing_pressure_test_procedure": ["2.27"],
    "bop_test_procedure": ["2.37", "2.38", "2.39", "3.3"],
    "reentry_program": ["2.11", "2.12", "2.13", "2.15", "2.42", "3.13"],
    "offshore_workover_program": ["2.6", "2.27", "2.36", "3.13"],
    "offshore_drilling_program": ["2.11", "2.12", "2.13", "2.18", "2.41"],
}


def get_rope_checklists(template_key: str, level: str = "moderate",
                        operator_name: str = "",
                        contractor_name: str = "") -> str:
    """Return a markdown section of ROPE checklists for the template."""
    try:
        from wizard_engine import neutralize_text
    except Exception:
        neutralize_text = lambda s, *a, **k: s  # noqa

    sec_ids = TEMPLATE_MAP.get(template_key, [])
    if not sec_ids:
        return ""
    sections = _sections()
    if not sections:
        return ""

    per_sec = {"brief": 10, "moderate": 20, "detailed": 40}[level]
    total_cap = {"brief": 25, "moderate": 60, "detailed": 180}[level]

    md = ["## FIELD CHECKLISTS (RIG OPERATIONS PERFORMANCE EXECUTION)", "",
          "Industry-standard field checklists adapted for this document "
          "(company names removed).", ""]
    count = 0
    for sid in sec_ids:
        # Aggregate the section and all its sub-sections (e.g. 2.4 -> 2.4.1, 2.4.2)
        parts = []
        for key, sec in sections.items():
            if key == sid or key.startswith(sid + "."):
                parts.append((key, sec))
        if not parts:
            continue
        main = sections.get(sid)
        title = main["title"] if main else parts[0][1]["title"]
        md.append(f"### {title}")
        md.append("")
        for key, sec in parts:
            items = sec["items"][:per_sec]
            if not items:
                continue
            if len(parts) > 1 and key != sid:
                md.append(f"**{sec['title']}**")
            for item in items:
                md.append(f"- [ ] {item}")
                count += 1
                if count >= total_cap:
                    break
            if count >= total_cap:
                break
        if count >= total_cap:
            break
        md.append("")
    if count == 0:
        return ""

    # Detailed level: include a short glossary of key terms
    if level == "detailed":
        gloss = _glossary()
        if gloss:
            md.append("### Glossary of Key Terms")
            md.append("")
            md.extend(gloss)
            md.append("")

    text = "\n".join(md)
    # Neutralize standard references before company-name cleanup
    text = re.sub(r"IPM[-–]?(?:ST|PR|PO|CORP|FO|REF)?[-–][A-Z0-9][A-Z0-9\-]*",
                  "Company Standard", text)
    text = text.replace("OFS-QHSE-S016", "Company Standard")
    text = text.replace("IPM Well Control Manual", "Company Well Control Manual")
    return neutralize_text(text, operator_name, contractor_name)


_GLOSS_RE = re.compile(r"^([A-Z0-9&/\s.\-]{2,40})\s*:\s+(.+)$")


def _glossary() -> List[str]:
    if not ROPE_FILE.exists():
        return []
    out: List[str] = []
    for raw in ROPE_FILE.read_text(encoding="utf-8",
                                   errors="replace").splitlines():
        s = raw.strip()
        m = _GLOSS_RE.match(s)
        if m and len(m.group(2)) > 4 and "REFERENCES" not in m.group(2):
            out.append(f"- **{m.group(1).strip()}** — {m.group(2).strip()}")
        if len(out) >= 40:
            break
    return out
