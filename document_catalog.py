# ============================================================================
# DOCUMENT CATALOG — fine-grained classification of the whole knowledge library
# File: document_catalog.py
# Classifies every document in programs/library/ along 5 dimensions:
#   - category    (Program / Procedure / Guideline / Checklist / Report / KB)
#   - well_type   (Vertical / Deviated / Horizontal / ERD / HPHT / Deepwater /
#                  Multi-lateral / Undefined)
#   - environment (Onshore / Offshore Jack-up / Semi-submersible /
#                  Fixed Platform / Caspian Sea / Undefined)
#   - operation   (Drilling / Workover / Re-Entry / Sidetrack / Completion /
#                  P&A / Well Testing / Stimulation / Fishing / Cementing /
#                  Well Control / Mud-Fluids / Casing-Liner / BOP / Coring /
#                  Logging / Guidelines / Problems-KB)
#   - hole sections involved (e.g. ["36\"", "26\"", ...])
# Classification = curated rules (filename patterns + content keywords).
# Results are cached in ~/.drilling_program/catalog.db for fast filtering.
# All general — no well/company names stored.
# ============================================================================

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

APP_DIR = Path.home() / ".drilling_program"
CATALOG_DB = str(APP_DIR / "catalog.db")
LIBRARY_DIR = Path(__file__).resolve().parent / "programs" / "library"

# ---------------------------------------------------------------------------
# ENUM LISTS (canonical)
# ---------------------------------------------------------------------------

WELL_TYPES = ["Vertical", "Deviated", "Horizontal", "ERD", "HPHT",
              "Deepwater", "Multi-lateral", "Undefined"]

ENVIRONMENTS = ["Onshore", "Offshore Jack-up", "Semi-submersible",
                "Fixed Platform", "Caspian Sea", "Undefined"]

OPERATIONS = ["Drilling", "Workover", "Re-Entry", "Sidetrack", "Completion",
              "P&A", "Well Testing", "Stimulation", "Fishing", "Cementing",
              "Well Control", "Mud-Fluids", "Casing-Liner", "BOP",
              "Coring", "Logging", "Guidelines", "Problems-KB"]

CATEGORIES = ["Program", "Procedure", "Guideline", "Checklist",
              "Report", "Problem-KB", "Price-Cost", "Manual"]

HOLE_SECTIONS = ["36\"", "30\"", "26\"", "24\"", "23.5\"", "20\"", "17-1/2\"",
                 "16\"", "14.75\"", "13.5\"", "12-1/4\"", "10-5/8\"",
                 "9-5/8\"", "8-1/2\"", "7\"", "6-1/8\"", "6\""]

# ---------------------------------------------------------------------------
# CURATED OVERRIDES: (file-number prefix -> classification dict)
# Applies to known documents where filename alone is not enough.
# ---------------------------------------------------------------------------

CURATED: Dict[str, Dict] = {
    # BP guidelines (files 563+)
    "04": {"category": "Guideline", "operation": "Well Control",
           "environment": "Undefined"},
    "10": {"category": "Guideline", "operation": "Drilling"},
    "11": {"category": "Guideline", "operation": "Drilling"},
    "12": {"category": "Guideline", "operation": "Drilling"},
    "13": {"category": "Guideline", "operation": "Drilling"},
    "14": {"category": "Guideline", "operation": "Drilling"},
    "20": {"category": "Guideline", "operation": "Casing-Liner"},
    "21": {"category": "Guideline", "operation": "Casing-Liner"},
    "22": {"category": "Guideline", "operation": "Casing-Liner"},
    "23": {"category": "Guideline", "operation": "Casing-Liner"},
    "25": {"category": "Guideline", "operation": "Casing-Liner"},
    "30": {"category": "Guideline", "operation": "Cementing"},
    "31": {"category": "Guideline", "operation": "Cementing"},
    "32": {"category": "Guideline", "operation": "Cementing"},
    "33": {"category": "Guideline", "operation": "Cementing"},
    "34": {"category": "Guideline", "operation": "Cementing"},
    "35": {"category": "Guideline", "operation": "Cementing"},
    "40": {"category": "Guideline", "operation": "Mud-Fluids"},
    "41": {"category": "Guideline", "operation": "Mud-Fluids"},
    "42": {"category": "Guideline", "operation": "Mud-Fluids"},
    "43": {"category": "Guideline", "operation": "Mud-Fluids"},
    "44": {"category": "Guideline", "operation": "Mud-Fluids"},
    "45": {"category": "Guideline", "operation": "Mud-Fluids"},
    "46": {"category": "Guideline", "operation": "Mud-Fluids"},
    "49": {"category": "Guideline", "operation": "Mud-Fluids"},
    "50": {"category": "Guideline", "operation": "Casing-Liner"},
    "52": {"category": "Guideline", "operation": "Completion"},
    "54": {"category": "Guideline", "operation": "Completion"},
    "55": {"category": "Guideline", "operation": "Drilling"},
    "60": {"category": "Guideline", "operation": "Fishing"},
    "61": {"category": "Guideline", "operation": "Fishing"},
    "62": {"category": "Guideline", "operation": "Fishing"},
    "64": {"category": "Guideline", "operation": "Fishing"},
    "65": {"category": "Guideline", "operation": "Fishing"},
    "70": {"category": "Guideline", "operation": "Well Testing"},
    "71": {"category": "Guideline", "operation": "Well Testing"},
    "72": {"category": "Guideline", "operation": "Coring"},
    "73": {"category": "Guideline", "operation": "Logging"},
    "74": {"category": "Guideline", "operation": "Logging"},
    "81": {"category": "Guideline", "operation": "Casing-Liner"},
    "82": {"category": "Guideline", "operation": "Drilling"},
    "83": {"category": "Guideline", "operation": "Drilling"},
    # Price table
    "216": {"category": "Price-Cost", "operation": "Drilling"},
    # ROPE manual
    "215": {"category": "Manual", "operation": "Guidelines"},
}

# filename keyword -> operation (checked first, most specific first)
OP_KEYWORDS = [
    (r"workover|wo[_-]?\d", "Workover"),
    (r"re[- ]?entry|re2h|re1h|re3h|re[_-]?en", "Re-Entry"),
    (r"sidetrack|whipstock|window|kick[- ]?off", "Sidetrack"),
    (r"cement|cmt|cementing", "Cementing"),
    (r"completion", "Completion"), (r"esp", "Completion"),
    (r"fishing|back[- ]?off|backoff|mill|washover|free[- ]?point", "Fishing"),
    (r"bop|wellhead|x[- ]?mas", "BOP"),
    (r"kill|kick|blowout|well control|shallow gas|divert", "Well Control"),
    (r"mud|fluid|baryte|barite", "Mud-Fluids"),
    (r"casing|liner|csg", "Casing-Liner"),
    (r"test|dst|lot|formation", "Well Testing"),
    (r"stimulat|acid|nitrogen|n2", "Stimulation"),
    (r"coring|core", "Coring"),
    (r"logg", "Logging"),
    (r"abandon|p&a|pa\b|suspend", "P&A"),
    (r"drill", "Drilling"),
    (r"problem", "Problems-KB"),
]

# environment keywords
ENV_KEYWORDS = [
    (r"semi|semisub|semisubmersible|heave|riserless|subsea", "Semi-submersible"),
    (r"jack[- ]?up|jak|jackup|jack", "Offshore Jack-up"),
    (r"platform|fixed|conductor|template", "Fixed Platform"),
    (r"caspian|shah deniz|amir kabir|kepco|azerbaijan", "Caspian Sea"),
    (r"offshore|sea|marine|deepwater|bop stack", "Offshore Jack-up"),
    (r"onshore|land rig|azadegan|azar|azns|aghajari|zagh", "Onshore"),
]

# well type keywords
WELL_KEYWORDS = [
    (r"horizontal|h\d|re2h|re1h|re3h|deviated", "Horizontal"),
    (r"erd|extended", "ERD"),
    (r"hpht|high pressure", "HPHT"),
    (r"deepwater|dp mode", "Deepwater"),
    (r"vertical", "Vertical"),
    (r"directional|deviated", "Deviated"),
    (r"multilateral|multi-lateral|laterals", "Multi-lateral"),
]

# hole section keywords
HOLE_KEYWORDS = [
    ("36", '36"'), ("30", '30"'), ("26", '26"'), ("24", '24"'),
    ("23.5", '23.5"'), ("20", '20"'), ("17", '17-1/2"'), ("16", '16"'),
    ("14.75", '14.75"'), ("13.5", '13.5"'), ("12.25", '12-1/4"'),
    ("12 1/4", '12-1/4"'), ("10.625", '10-5/8"'), ("10 5/8", '10-5/8"'),
    ("9.625", '9-5/8"'), ("9 5/8", '9-5/8"'), ("8.5", '8-1/2"'),
    ("8 1/2", '8-1/2"'), ("6 1/8", '6-1/8"'), ("6.125", '6-1/8"'),
]

# category keywords
CAT_KEYWORDS = [
    (r"guideline|procedure manual|manual", "Guideline"),
    (r"checklist|check list", "Checklist"),
    (r"report|handover|hand over", "Report"),
    (r"price[- ]?table|price list|cost breakdown|cost ceiling|afe", "Price-Cost"),
    (r"problem", "Problem-KB"),
    (r"procedure|instruction|plan of|plan for|running|drill out",
     "Procedure"),
    (r"program|programme", "Program"),
]


def classify_file(path: Path) -> Dict:
    """Classify a single library file into (category, well_type, env, op, holes)."""
    name = path.stem  # e.g. "242_001_001c_-_SD_A-03_Drilling_Program_..."
    num = int(name.split("_")[0]) if name[:3].isdigit() else 0
    low = name.lower()
    body = ""
    try:
        body = path.read_text(encoding="utf-8", errors="replace")[:6000].lower()
    except Exception:
        pass
    blob = low + " " + body[:3000]

    result = {"category": "Procedure", "well_type": "Undefined",
              "environment": "Undefined", "operation": "Drilling",
              "holes": []}

    # curated override by file-number prefix
    if num >= 563:
        code = name.split("_")[1] if len(name.split("_")) > 1 else ""
        c = CURATED.get(code[:2])
        if c:
            result.update(c)
    elif num in CURATED:
        result.update(CURATED[num])

    # operation keywords (first match wins; more specific first)
    for pat, op in OP_KEYWORDS:
        if re.search(pat, blob):
            result["operation"] = op
            break

    # category keywords
    for pat, cat in CAT_KEYWORDS:
        if re.search(pat, blob):
            result["category"] = cat
            break

    # environment
    for pat, env in ENV_KEYWORDS:
        if re.search(pat, blob):
            result["environment"] = env
            break

    # well type
    for pat, wt in WELL_KEYWORDS:
        if re.search(pat, blob):
            result["well_type"] = wt
            break

    # hole sections
    holes = []
    for pat, hs in HOLE_KEYWORDS:
        if re.search(r"\b" + re.escape(pat) + r"\b", low) or pat in low:
            if hs not in holes:
                holes.append(hs)
    result["holes"] = holes

    # re-entry programs from offshore repo: they are programs
    if num and 217 <= num <= 241 and "program" in low:
        result["category"] = "Program"
        if "workover" in low:
            result["operation"] = "Workover"

    return result


# ---------------------------------------------------------------------------
# DATABASE (cache)
# ---------------------------------------------------------------------------

class DocumentCatalog:
    def __init__(self, rebuild: bool = False):
        APP_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(CATALOG_DB)
        self.conn.row_factory = sqlite3.Row
        self._create()
        if rebuild or self._count() == 0:
            self._build()

    def _create(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS docs (
                id INTEGER PRIMARY KEY,
                file TEXT UNIQUE,
                num INTEGER,
                title TEXT,
                category TEXT,
                well_type TEXT,
                environment TEXT,
                operation TEXT,
                holes TEXT,
                keywords TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_docs_cat ON docs(category);
            CREATE INDEX IF NOT EXISTS idx_docs_op ON docs(operation);
            CREATE INDEX IF NOT EXISTS idx_docs_env ON docs(environment);
            CREATE INDEX IF NOT EXISTS idx_docs_well ON docs(well_type);
        """)
        self.conn.commit()

    def _count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]

    def _build(self):
        self.conn.execute("DELETE FROM docs")
        files = sorted(LIBRARY_DIR.glob("*.txt"))
        for f in files:
            cls = classify_file(f)
            num = int(f.stem.split("_")[0]) if f.stem[:3].isdigit() else 0
            self.conn.execute(
                "INSERT INTO docs (file, num, title, category, well_type, "
                "environment, operation, holes, keywords) VALUES (?,?,?,?,?,?,?,?,?)",
                (f.name, num, f.stem, cls["category"], cls["well_type"],
                 cls["environment"], cls["operation"],
                 ",".join(cls["holes"]), ""))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def count(self) -> int:
        return self._count()

    def stats(self) -> Dict:
        out = {}
        for col in ("category", "well_type", "environment", "operation"):
            rows = self.conn.execute(
                f"SELECT {col} k, COUNT(*) n FROM docs GROUP BY {col} "
                "ORDER BY n DESC").fetchall()
            out[col] = {r["k"]: r["n"] for r in rows}
        return out

    def filter(self, well_type: str = "", environment: str = "",
               operation: str = "", category: str = "",
               limit: int = 200) -> List[Dict]:
        sql = "SELECT * FROM docs WHERE 1=1"
        args = []
        for col, val in (("well_type", well_type), ("environment", environment),
                         ("operation", operation), ("category", category)):
            if val and val != "Undefined":
                sql += f" AND {col}=?"
                args.append(val)
        sql += " ORDER BY num LIMIT ?"
        args.append(limit)
        rows = self.conn.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

    def matched_summary(self, well_type="", environment="", operation="",
                        category="") -> int:
        return len(self.filter(well_type, environment, operation, category,
                               limit=100000))


def get_catalog(rebuild: bool = False) -> DocumentCatalog:
    return DocumentCatalog(rebuild=rebuild)


if __name__ == "__main__":
    cat = DocumentCatalog(rebuild=True)
    try:
        print(f"cataloged: {cat.count()} documents")
        st = cat.stats()
        for k, v in st.items():
            print(f"\n{k}:")
            for name, n in list(v.items())[:15]:
                print(f"  {name}: {n}")
    finally:
        cat.close()
