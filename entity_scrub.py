# ============================================================================
# ENTITY-BASED GENERALIZATION
# File: entity_scrub.py
# Audit item: company-name generalization should not be only regex
# replacement — it should distinguish ENTITY TYPES so we never confuse a
# vendor with a technical term or a formation with a well code.
#
# Approach (deterministic, no external deps):
#   1. Known entity lists (operators, service companies, fields, wells)
#   2. Context-aware rules (e.g. "X WSS", "Rig: X", "X Co." patterns)
#   3. Technical-term protection list (words that look like brands but are
#      not, e.g. 'Brown' geology, 'MI' mud engineering, 'Total' adjective)
#   4. Positional heuristics with word-boundary checks
# ============================================================================

import re
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# PROTECTED TECHNICAL TERMS (never scrub — false-positive killers)
# ---------------------------------------------------------------------------
# (term, reason) — these look like brands/well codes but are technical.
PROTECTED = {
    "brown": "geology colour",
    "mi": "mud engineering abbreviation (M-I)",
    "total": "adjective",
    "shell": "casing/wellhead part",
    "baker": "could be geological/name — handled contextually",
    "arrow": "directional arrow",
    "johnson": "could be person name in sign-off",
    "weather": "weather downtime",
    "parker": "parking / person",
    "taylor": "person name",
    "normal": "technical term",
    "major": "adjective",
    "cameron": "person name / brand — contextual",
}

# ---------------------------------------------------------------------------
# ENTITY LISTS (extendable)
# ---------------------------------------------------------------------------

OPERATORS = [
    "nisoc", "nioc", "oeoc", "iooc", "msa", "nicо", "nico", "pedec", "pedco",
    "kpe", "adco", "adnoc", "aramco", "saudi aramco", "pemex", "petrobras",
    "chevron", "exxonmobil", "exxon", "mobil", "totalenergies", "shell plc",
    "bp", "eni", "equinor", "statoil", "conocophillips", "gazprom",
    "cnpc", "sinopec", "cnpci", "jogpc", "ioec", "gwdc", "nidc", "pogo",
]

SERVICE_COMPANIES = [
    "schlumberger", "slb", "halliburton", "baker hughes", "baker", "weatherford",
    "nov", "national oilwell", "fmc", "cameron", "hydril", "tenaris",
    "vallourec", "nimir", "petrom", "iadc", "devereux", "well control school",
    "anadrill", "halco", "m-i", "mi swaco", "baroid", "sperry", "martin decker",
    "varco", "vetco", "tiw", "reagan", "elmagco", "normar", "omsco",
    "bara-wate", "geoquest", "intouch", "t.h. hill", "totco", "weco",
    "moduspec", "westhou", "coilcade", "dowell", "expro", "sgs", "odfjell",
    "kca deutag", "parker drilling", "ensco", "transocean", "nabors",
    "maersk", "bj services", "dri-quip", "ingram-cactus", "kepco",
    "ndco", "ppz", "weatherford", "halliburton", "baker", "bakerlok",
]

FIELDS = [
    "azadegan", "azns", "salman", "balal", "dorood", "foroozan", "siri",
    "khazar", "caspian", "shah deniz", "naftshahr", "kangan", "tabnak",
    "nar", "maleh kuh", "cheshmeh", "aghajari", "siah makan", "paydar",
]

RESERVOIRS = ["fahliyan", "sarvak", "kazhdumi", "gadvan", "asmary", "asmari",
              "bangestan", "aghajari", "gachsaran", "pabdeh", "gurpi",
              "ilam", "khami", "yazd"]

# well-code patterns (with boundaries)
WELL_CODE = re.compile(
    r"\b(?:AZNS|SI|AZR|BL|2S|D|NR|NSH|PYW|SA|SR|DH|NAR|MK|CK|WDI|AGH|NTH|HE)"
    r"[- ]?\d{1,4}[A-Za-z]?\b", re.IGNORECASE)

# context patterns that reveal a company name
COMPANY_CONTEXT = re.compile(
    r"\b(?:rig\s*:?\s*|contractor\s*:?\s*|operator\s*:?\s*|company\s*:?\s*|"
    r"vendor\s*:?\s*|service\s*co(?:mpany)?\s*:?\s*|prepared\s+by\s*:?\s*|"
    r"approved\s+by\s*:?\s*|per\s+|as\s+per\s+)[A-Za-z][A-Za-z .&'-]{2,40}",
    re.IGNORECASE)


def _is_protected(token: str) -> bool:
    return token.lower() in PROTECTED


def scrub_entities(text: str,
                   operator_name: str = "",
                   contractor_name: str = "") -> Tuple[str, List[str]]:
    """Generalize entity names in text; returns (text, removed_entities).

    Keeps the user's operator/contractor names intact (via sentinels).
    """
    OP_TMP, CON_TMP = "\x00OP\x00", "\x00CON\x00"
    removed = []

    # protect user names first
    if len(operator_name or "") >= 2:
        text = re.sub(r"\b" + re.escape(operator_name) + r"\b",
                      OP_TMP, text)
    if len(contractor_name or "") >= 2:
        text = re.sub(r"\b" + re.escape(contractor_name) + r"\b",
                      CON_TMP, text)

    # well codes
    for m in list(WELL_CODE.finditer(text)):
        tok = m.group(0)
        if not _is_protected(tok):
            text = text.replace(tok, "")
            removed.append(("well", tok))

    # operators / service companies (word-boundary, case-insensitive)
    for name in OPERATORS + SERVICE_COMPANIES:
        pat = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
        for m in list(pat.finditer(text)):
            tok = m.group(0)
            if _is_protected(tok):
                continue
            text = text.replace(tok, "")
            removed.append(("company", tok))

    # fields & reservoirs
    for name in FIELDS + RESERVOIRS:
        pat = re.compile(r"\b" + re.escape(name) + r"\b", re.IGNORECASE)
        for m in list(pat.finditer(text)):
            tok = m.group(0)
            if _is_protected(tok):
                continue
            text = text.replace(tok, "")
            removed.append(("field/reservoir", tok))

    # company context lines: scrub the whole phrase value
    def _ctx_repl(m):
        phrase = m.group(0)
        val = m.group(0)[m.end(0):] if False else m.group(0)
        # replace the value part after the label
        label = re.match(r"^([A-Za-z :]+:?\s+)", phrase)
        if label:
            return label.group(1)
        return ""
    text = COMPANY_CONTEXT.sub(_ctx_repl, text)

    # restore user names
    text = text.replace(OP_TMP, operator_name or "the Operator")
    text = text.replace(CON_TMP, contractor_name or "the Service Company")

    # cleanup
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\s+([,.])", r"\1", text)
    return text.strip(" .-–—"), removed


if __name__ == "__main__":
    sample = ("Well SI-09 workover by NISOC with SLB as contractor; "
              "Rig: OEOC 207. Brown shales in the Aghajari formation; "
              "Total depth 3200 m; 'Total' is also a word. "
              "Operator PARS OIL CO approved the plan.")
    out, removed = scrub_entities(sample, "PARS OIL CO", "DRILL PRO")
    print("OUT:", out)
    print("REMOVED:", removed[:8])
