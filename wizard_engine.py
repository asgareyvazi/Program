# ============================================================================
# UNIVERSAL PROGRAM & PROCEDURE WIZARD — ENGINE
# ============================================================================
# "I want a drilling program" -> the wizard asks structured inputs ->
# a complete, professional Word document is generated on the spot.
#
# Templates live in wizard_library.py (programs) and wizard_procedures.py
# (procedures). Content is based on worldwide industry practice:
# API RP 5C3/10B/13B/53/59, ISO 10400/10426, NORSOK D-010, IADC guidelines,
# Shell DEP / Saudi Aramco SAES / BP GP style master documents.
# ============================================================================

import re
import html
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QCheckBox, QTextEdit,
    QListWidget, QListWidgetItem, QPushButton, QFileDialog, QProgressBar,
    QScrollArea, QWidget, QFrame, QFormLayout, QMessageBox, QGroupBox,
    QAbstractItemView, QTableWidget, QTableWidgetItem, QHeaderView,
    QApplication, QSpinBox, QSplitter
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QFont, QDesktopServices, QColor, QBrush
from docx.shared import Pt, Cm, RGBColor

# Risk engine integration (lazy import inside methods; RiskLevel used in UI)
from drilling_risk_analyzer import RiskLevel

# ----------------------------------------------------------------------------
# INPUT SPEC + TEMPLATE DEFINITION
# ----------------------------------------------------------------------------

INPUT_TYPES = ("text", "number", "combo", "check", "textarea", "table")


class InputSpec:
    """Definition of one wizard input field."""

    def __init__(self, key: str, label: str, input_type: str = "text",
                 options: Optional[List[str]] = None, unit: str = "",
                 required: bool = False, default: str = "",
                 placeholder: str = "", group: str = "General",
                 columns: Optional[List[str]] = None):
        assert input_type in INPUT_TYPES, f"bad input type {input_type}"
        self.key = key
        self.label = label
        self.type = input_type
        self.options = options or []
        self.unit = unit
        self.required = required
        self.default = default
        self.placeholder = placeholder
        self.group = group
        self.columns = columns or []


class TemplateDef:
    """Definition of one generator template (program or procedure)."""

    def __init__(self, key: str, name: str, icon: str, kind: str,
                 description: str, inputs: Optional[List[InputSpec]] = None,
                 markdown: str = "", source_file: Optional[str] = None,
                 tokens: Optional[Dict[str, str]] = None,
                 meta: Optional[Dict[str, str]] = None):
        self.key = key
        self.name = name
        self.icon = icon
        self.kind = kind              # "Program" | "Procedure"
        self.description = description
        self.inputs = inputs or []
        self.markdown = markdown
        self.source_file = source_file      # path relative to programs dir
        self.tokens = tokens or {}          # token -> input key (for file templates)
        self.meta = meta or {}

    @property
    def full_markdown(self) -> str:
        if self.source_file:
            base = Path(__file__).resolve().parent / "programs"
            p = base / self.source_file
            if p.exists():
                return p.read_text(encoding="utf-8", errors="replace")
            return f"# Template source not found: {self.source_file}"
        return self.markdown


# ----------------------------------------------------------------------------
# FILLING
# ----------------------------------------------------------------------------

PLACEHOLDER_RE = re.compile(r"\{\{([a-zA-Z0-9_]+)\}\}")


# ----------------------------------------------------------------------------
# SECTION EXTRACTION & SELECTION
# ----------------------------------------------------------------------------

def extract_sections(md_text: str):
    """Split markdown into (heading, content) blocks at '##' level."""
    lines = md_text.replace("\r\n", "\n").split("\n")
    heads = []
    for i, l in enumerate(lines):
        m = re.match(r"^##\s+(.+)$", l)
        if m:
            heads.append((m.group(1).strip(), i))
    sections = []
    for idx, (h, start) in enumerate(heads):
        end = heads[idx + 1][1] if idx + 1 < len(heads) else len(lines)
        sections.append((h, "\n".join(lines[start:end])))
    return sections


def render_selected(md_text: str, selected_heads):
    """Return markdown containing only the selected '##' sections.

    The document header (before the first '##') and any section whose
    heading contains 'APPROVAL' are always kept.
    """
    lines = md_text.replace("\r\n", "\n").split("\n")
    first_h2 = next((i for i, l in enumerate(lines) if l.startswith("## ")),
                    None)
    header = "\n".join(lines[:first_h2]) if first_h2 is not None else md_text

    parts = [header.rstrip()]
    for h, content in extract_sections(md_text):
        if h in selected_heads or "APPROVAL" in h.upper():
            parts.append(content.rstrip())
    return "\n\n".join(p for p in parts if p.strip())


# ----------------------------------------------------------------------------
# COMPANY NAME NEUTRALIZATION
# ----------------------------------------------------------------------------
# Company/brand names must never appear in generated output — knowledge
# stays, branding goes. Operator/contractor names are supplied by the user
# as inputs instead.

OPERATOR_NAMES = [
    r"\bNISOC\b", r"\bPECO\b", r"\bOEOC\b", r"\bCNPCI\b", r"\bPEDEC\b",
    r"\bPEDCO\b", r"\bGWDC\b", r"\bNIOC\b", r"\bNIDC\b", r"\bIOOC\b",
    r"\bMSA\b", r"\bNICO\b", r"\bKPE\b", r"\bSK/PECO\b",
    r"\bSaudi Aramco\b", r"\bAramco\b", r"\bADNOC\b", r"\bKOC\b",
    r"\bINOC\b", r"\bNPDC\b", r"\bIOEC\b", r"\bJOGPC\b",
    r"\bPEDEX\b", r"\bMND\b", r"\bNational Iranian Oil Company\b",
    r"\bIranian Offshore Oil Company\b", r"\bCentral Iranian Oil Fields\b",
]
# Well-code / reservoir patterns that must never appear in output.
# The catalog & templates are general; this is a defensive layer for any
# content that may come from internal knowledge documents.
WELL_PATTERNS = [
    (r"\bAZNS\s*[-–]?\s*[A-Z0-9]*\b", ""),
    (r"\bSIAH MAKAN\b", "the field"),
    (r"\bSI-?\d+\b", ""),
    (r"\bAZR[- ]?\d+\b", ""),
    (r"\bMB-W\w+\b", ""),
    (r"\bYAP1\b", ""),
    (r"\bF-?20\b", ""),
    (r"\bS\d{2,3}\b", ""),
    (r"\bW0\d{2,3}\w*\b", ""),
    (r"\bSarvak\b", "main reservoir"),
    (r"\bFahliyan\b", "HPHT reservoir"),
    (r"\bKazhdumi\b", "reservoir"),
    (r"\bGadvan\b", "reservoir"),
]

SERVICE_NAMES = [
    r"\bSchlumberger\b", r"\bSLB\b", r"\bHalliburton\b",
    r"\bBaker Hughes\b", r"\bBaker\b", r"\bBakerlok\b",
    r"\bWeatherford\b",
    r"\bNOV\b", r"\bNational Oilwell\b", r"\bFMC\b", r"\bCameron\b",
    r"\bHydril\b", r"\bTenaris\b", r"\bVallourec\b", r"\bCoreLab\b",
    r"\bSGS\b", r"\bT\u00dcV\b", r"\bExpro\b", r"\bProserv\b",
    r"\bOdfjell\b", r"\bKCA Deutag\b", r"\bParker Drilling\b",
    r"\bEDC\b", r"\bEnsco\b", r"\bTransocean\b", r"\bMaersk Drilling\b",
    r"\bNabors\b", r"\bHelmerich\b", r"\bPatterson-UTI\b",
    r"\bIPM\b", r"\bDowell\b", r"\bSperry Sun\b", r"\bSperry\b",
    r"\bMartin Decker\b", r"\bVarco\b", r"\bVetco\b", r"\bTIW\b",
    r"\bReagan\b", r"\bElmagco\b", r"\bNormar\b", r"\bOmsco\b",
    r"\bBARA-WATE\b", r"\bAnadrill\b", r"\bGeoQuest\b",
    r"\bInTouch\b", r"\bT\.H\. Hill\b", r"\bTotco\b", r"\bWeco\b",
    r"\bModuspec\b", r"\bWestHou\b", r"\bCoilCADE\b", r"\bCoilCade\b",
]


def neutralize_text(md_text: str, operator_name: str = "",
                    contractor_name: str = "") -> str:
    """Remove hard-coded company/brand names from output text.

    The user's own operator / contractor names (entered as inputs) are
    substituted instead of generic placeholders. When not provided, the
    generic roles 'the Operator' / 'the Service Company' are used.

    Temporary sentinels are used so that a user-entered company name which
    itself contains a blacklisted token (e.g. 'PEDEC Oil') is never
    re-replaced.
    """
    op = (operator_name or "").strip() or "the Operator"
    con = (contractor_name or "").strip() or "the Service Company"
    OP_TMP = "\x00OP\x00"
    CON_TMP = "\x00CON\x00"

    out = md_text
    # Protect the user's own names first (whole-word, case-sensitive), so a
    # user name that contains a blacklisted token (e.g. 'PEDEC Oil Co') or
    # is very short is never re-replaced.
    if op.lower() != "the operator" and len(op) >= 2:
        out = re.sub(r"\b" + re.escape(op) + r"\b", OP_TMP, out)
    if con.lower() != "the service company" and len(con) >= 2:
        out = re.sub(r"\b" + re.escape(con) + r"\b", CON_TMP, out)

    # A blacklisted token that appears inside the user's operator name maps
    # to the operator; inside the contractor name maps to the contractor;
    # otherwise operator tokens -> operator, service tokens -> contractor.
    def _target(pat, op, con):
        """Decide which user name a blacklisted token maps to."""
        if re.search(pat, op, re.IGNORECASE):
            return OP_TMP
        if re.search(pat, con, re.IGNORECASE):
            return CON_TMP
        return OP_TMP  # operator tokens default to operator

    for pat in OPERATOR_NAMES:
        out = re.sub(pat, _target(pat, op, con), out, flags=re.IGNORECASE)
    for pat in SERVICE_NAMES:
        if re.search(pat, op, re.IGNORECASE):
            out = re.sub(pat, OP_TMP, out, flags=re.IGNORECASE)
        else:
            out = re.sub(pat, CON_TMP, out, flags=re.IGNORECASE)

    out = out.replace(OP_TMP, op)
    out = out.replace(CON_TMP, con)

    # Defensive: remove well codes / reservoir names (general output)
    for pat, repl in WELL_PATTERNS:
        out = re.sub(pat, repl, out, flags=re.IGNORECASE)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\(\s*\)", "", out)
    out = re.sub(re.escape(op) + r"\s+" + re.escape(op), op, out)
    out = re.sub(re.escape(con) + r"\s+" + re.escape(con), con, out)
    return out


def fill_template(tdef: TemplateDef, values: Dict[str, str]) -> str:
    """Replace {{key}} placeholders (and token literals for file templates)
    with the entered values. Empty values become '[To Be Filled]'."""
    md = tdef.full_markdown

    def repl(m):
        key = m.group(1)
        val = values.get(key, "")
        return val if str(val).strip() else "[To Be Filled]"

    md = PLACEHOLDER_RE.sub(repl, md)

    # Token-based replacement (used by file templates such as ESP master doc)
    if tdef.tokens:
        for token, key in tdef.tokens.items():
            val = values.get(key, "")
            if str(val).strip():
                md = md.replace(token, str(val))

    # Append real reference documents from the operations library
    try:
        from wizard_references import reference_markdown
        ref_section = reference_markdown(tdef.key)
        if ref_section and "REFERENCE DOCUMENTS" not in md:
            md = md.rstrip() + "\n\n---\n\n" + ref_section
    except Exception:
        pass

    return md


# ----------------------------------------------------------------------------
# MARKDOWN -> WORD (.docx)
# ----------------------------------------------------------------------------

ACCENT = RGBColor(0xE9, 0x45, 0x60)
DARK_BLUE = RGBColor(0x0F, 0x34, 0x60)
GOLD = RGBColor(0xC9, 0x9A, 0x2E)
GREY = RGBColor(0x80, 0x80, 0x90)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG = "EDF1F7"
HEAD_BG = "0F3460"

# Active output font settings (set by md_to_docx from user options)
_FONT_NAME = "Calibri"
_FONT_SIZE = 11.0


def _shade_cell(cell, color_hex: str):
    from docx.oxml.ns import nsdecls
    from docx.oxml import parse_xml
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(
        f'<w:shd {nsdecls("w")} w:fill="{color_hex}" w:val="clear"/>'))


def _add_runs(paragraph, text: str, base_size: Optional[float] = None):
    if base_size is None:
        base_size = _FONT_SIZE
    """Add runs to a paragraph, honoring **bold**, *italic*, `code`."""
    # Split by tokens: **...**, *...*, `...`
    pattern = re.compile(r"(\*\*.+?\*\*|\*[^*]+?\*|`[^`]+?`)")
    for part in pattern.split(text):
        if not part:
            continue
        run = paragraph.add_run()
        if part.startswith("**") and part.endswith("**"):
            run.text = part[2:-2]
            run.bold = True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run.text = part[1:-1]
            run.italic = True
        elif part.startswith("`") and part.endswith("`"):
            run.text = part[1:-1]
            run.font.name = "Consolas"
        else:
            run.text = part
        run.font.size = Pt(base_size)


def _heading(doc, text: str, level: int):
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import nsdecls
    from docx.oxml import parse_xml

    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(14 if level == 1 else 8)
    pf.space_after = Pt(6)

    if level == 1:
        pPr = p._p.get_or_add_pPr()
        pPr.append(parse_xml(
            f'<w:shd {nsdecls("w")} w:fill="{HEAD_BG}" w:val="clear"/>'))
        r = p.add_run("  " + text.upper())
        r.bold = True
        r.font.size = Pt(_FONT_SIZE + 4)
        r.font.name = _FONT_NAME
        r.font.color.rgb = WHITE
    elif level == 2:
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(_FONT_SIZE + 1.5)
        r.font.name = _FONT_NAME
        r.font.color.rgb = ACCENT
    else:
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(_FONT_SIZE + 0.5)
        r.font.name = _FONT_NAME
        r.font.color.rgb = DARK_BLUE


def _add_table(doc, header: List[str], rows: List[List[str]],
               col_widths: Optional[List[float]] = None):
    from docx.shared import Cm
    from docx.enum.table import WD_TABLE_ALIGNMENT

    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    hdr = table.rows[0].cells
    for i, h in enumerate(header):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(str(h))
        r.bold = True
        r.font.size = Pt(_FONT_SIZE - 1.5)
        r.font.color.rgb = WHITE
        _shade_cell(hdr[i], HEAD_BG)

    for ridx, row in enumerate(rows):
        cells = table.add_row().cells
        for i in range(len(header)):
            val = row[i] if i < len(row) else ""
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            _add_runs(p, str(val), base_size=_FONT_SIZE - 1.5)
            if ridx % 2 == 1:
                _shade_cell(cells[i], LIGHT_BG)

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def md_to_docx(md_text: str, out_path: str,
               meta: Optional[Dict[str, str]] = None,
               options: Optional[Dict] = None) -> bool:
    """Convert the markdown template (already filled) into a Word document.

    options may contain: font, font_size, page (A4/Letter), orientation,
    margin_left/right/top/bottom (cm), cover, toc, header_text, footer_text.
    """
    from docx import Document
    from docx.shared import Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
    from docx.enum.section import WD_ORIENT
    from docx.oxml.ns import nsdecls, qn
    from docx.oxml import parse_xml

    meta = meta or {}
    options = options or {}

    global _FONT_NAME, _FONT_SIZE
    font_name = options.get("font", "Calibri")
    font_size = float(options.get("font_size", 11))
    _FONT_NAME = font_name
    _FONT_SIZE = font_size
    page = options.get("page", "A4")
    orientation = options.get("orientation", "Portrait")
    ml = options.get("margin_left", 2.5)
    mr = options.get("margin_right", 2.0)
    mt = options.get("margin_top", 2.0)
    mb = options.get("margin_bottom", 2.0)

    doc = Document()
    # Base font on the Normal style (applies to everything by default)
    normal = doc.styles["Normal"]
    normal.font.name = font_name
    normal.font.size = Pt(font_size)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), font_name)
    rfonts.set(qn("w:hAnsi"), font_name)
    rfonts.set(qn("w:cs"), font_name)

    sec = doc.sections[0]
    if page == "Letter":
        sec.page_width = Cm(21.59)
        sec.page_height = Cm(27.94)
    else:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
    if orientation == "Landscape":
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width, sec.page_height = sec.page_height, sec.page_width
    sec.top_margin = Cm(mt)
    sec.bottom_margin = Cm(mb)
    sec.left_margin = Cm(ml)
    sec.right_margin = Cm(mr)

    # Header / footer
    if options.get("header_text"):
        hp = sec.header.paragraphs[0]
        hp.text = options["header_text"]
        for r in hp.runs:
            r.font.size = Pt(8)
            r.font.color.rgb = GREY
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    fld = parse_xml(
        f'<w:fldSimple {nsdecls("w")} w:instr=" PAGE \\* MERGEFORMAT "/>')
    run._r.addnext(fld)
    if options.get("footer_text"):
        r2 = fp.add_run("   " + options["footer_text"])
        r2.font.size = Pt(8)
        r2.font.color.rgb = GREY

    # Cover page
    if options.get("cover", True):
        title = ""
        for line in md_text.replace("\r\n", "\n").split("\n"):
            m = re.match(r"^#\s+(.+)$", line)
            if m:
                title = m.group(1).strip()
                break
        doc.add_paragraph("")
        for _ in range(3):
            doc.add_paragraph("")
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(title or meta.get("title", "DOCUMENT"))
        r.bold = True
        r.font.size = Pt(24)
        r.font.color.rgb = DARK_BLUE

        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r2 = p2.add_run(meta.get("title", ""))
        r2.font.size = Pt(14)
        r2.font.color.rgb = ACCENT

        doc.add_paragraph("")
        for label in ("Operator", "Contractor", "Document Number",
                      "Revision", "Date", "Prepared By", "Reviewed By",
                      "Approved By"):
            val = meta.get({
                "Operator": "operator",
                "Contractor": "contractor",
                "Document Number": "document_number",
                "Revision": "revision",
                "Date": "date",
                "Prepared By": "prepared_by",
                "Reviewed By": "reviewed_by",
                "Approved By": "approved_by",
            }.get(label, ""), "")
            if val:
                p3 = doc.add_paragraph()
                p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r3 = p3.add_run(f"{label}: {val}")
                r3.font.size = Pt(11)
        doc.add_page_break()

    # Table of contents (real Word TOC field — update with F9)
    if options.get("toc", True):
        p = doc.add_paragraph()
        r = p.add_run("TABLE OF CONTENTS")
        r.bold = True
        r.font.size = Pt(14)
        r.font.color.rgb = DARK_BLUE
        doc.add_paragraph()
        fld_p = doc.add_paragraph()
        fld_run = fld_p.add_run()
        fld_xml = parse_xml(
            f'<w:fldSimple {nsdecls("w")} w:instr=" TOC \\o &quot;1-2&quot; \\h \\z \\u "/>')
        fld_run._r.addnext(fld_xml)
        doc.add_page_break()

    lines = md_text.replace("\r\n", "\n").split("\n")
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].rstrip()

        # Fenced code block -> single monospace paragraph
        if line.startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            p = doc.add_paragraph()
            for b in buf:
                r = p.add_run(b + "\n")
                r.font.name = "Consolas"
                r.font.size = Pt(9)
            continue

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            _heading(doc, m.group(2).strip(), len(m.group(1)))
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
            doc.add_paragraph()
            i += 1
            continue

        # Table
        if line.lstrip().startswith("|") and i + 1 < n and \
                re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]) and \
                "-" in lines[i + 1]:
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < n and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            _add_table(doc, header, rows)
            continue

        # Blockquote
        if line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").strip())
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.8)
            r = p.add_run("▸ " + " ".join(buf))
            r.italic = True
            r.font.size = Pt(10)
            r.font.color.rgb = DARK_BLUE
            continue

        # Checklist item
        if re.match(r"^\s*-\s*\[[ xX]\]\s+", line):
            while i < n and re.match(r"^\s*-\s*\[[ xX]\]\s+", lines[i]):
                text = re.sub(r"^\s*-\s*\[[ xX]\]\s+", "", lines[i])
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.8)
                r = p.add_run("☐  ")
                r.font.size = Pt(11)
                _add_runs(p, text)
                i += 1
            continue

        # Unordered list
        if re.match(r"^\s*[-*+]\s+", line):
            while i < n and re.match(r"^\s*[-*+]\s+", lines[i]):
                text = re.sub(r"^\s*[-*+]\s+", "", lines[i])
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.8)
                r = p.add_run("•  ")
                r.font.size = Pt(10)
                _add_runs(p, text)
                i += 1
            continue

        # Ordered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            while i < n and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                text = re.sub(r"^\s*\d+[.)]\s+", "", lines[i])
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Cm(0.8)
                _add_runs(p, text)
                i += 1
            continue

        # Blank
        if not line.strip():
            i += 1
            continue

        # Paragraph — guaranteed progress: unmatched lines are consumed.
        buf = []
        while i < n:
            s = lines[i].strip()
            if not s or s.startswith("#") or s.startswith(">") or \
                    s.startswith("|") or s.startswith("```") or \
                    re.match(r"^\s*[-*+]\s+", lines[i]) or \
                    re.match(r"^\s*\d+[.)]\s+", lines[i]) or \
                    re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", lines[i]) or \
                    re.match(r"^\s*-\s*\[[ xX]\]\s+", lines[i]):
                break
            buf.append(s)
            i += 1
        if buf:
            p = doc.add_paragraph()
            _add_runs(p, " ".join(buf))
        else:
            p = doc.add_paragraph()
            _add_runs(p, lines[i].strip() if i < n else "")
            i += 1

    # Footer meta
    if meta:
        doc.add_paragraph()
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(
            f"Generated by Drilling Program Generator Pro v3.1  •  "
            f"{meta.get('date', datetime.now().strftime('%d-%B-%Y'))}")
        r.font.size = Pt(8)
        r.font.color.rgb = GREY

    doc.save(out_path)
    return True


# ----------------------------------------------------------------------------
# DYNAMIC INPUT WIDGETS
# ----------------------------------------------------------------------------

class TableInputWidget(QWidget):
    """Editable table input (add/remove rows) for table-type InputSpec."""

    def __init__(self, spec: InputSpec, parent=None):
        super().__init__(parent)
        self.columns = spec.columns or ["Item"]
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMinimumHeight(140)
        lay.addWidget(self.table)

        btns = QHBoxLayout()
        btn_add = QPushButton("➕ Add Row")
        btn_add.setMaximumWidth(110)
        btn_add.clicked.connect(self.add_row)
        btn_rm = QPushButton("➖ Remove Row")
        btn_rm.setMaximumWidth(110)
        btn_rm.clicked.connect(self.remove_row)
        btns.addWidget(btn_add)
        btns.addWidget(btn_rm)
        btns.addStretch()
        lay.addLayout(btns)

    def add_row(self, data=None):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for c in range(len(self.columns)):
            val = data[c] if data and c < len(data) else ""
            self.table.setItem(row, c, QTableWidgetItem(str(val)))

    def remove_row(self):
        rows = {i.row() for i in self.table.selectedItems()}
        for r in sorted(rows, reverse=True):
            self.table.removeRow(r)

    def values(self) -> List[List[str]]:
        out = []
        for r in range(self.table.rowCount()):
            row = []
            for c in range(self.table.columnCount()):
                item = self.table.item(r, c)
                row.append(item.text().strip() if item else "")
            if any(row):
                out.append(row)
        return out


def _build_field(spec: InputSpec) -> QWidget:
    if spec.type == "text":
        w = QLineEdit()
        w.setPlaceholderText(spec.placeholder or spec.label)
        if spec.default:
            w.setText(spec.default)
        return w
    if spec.type == "number":
        w = QDoubleSpinBox()
        w.setRange(0, 1e9)
        w.setDecimals(2)
        w.setValue(float(spec.default) if spec.default else 0)
        if spec.unit:
            w.setSuffix(f" {spec.unit}")
        return w
    if spec.type == "combo":
        w = QComboBox()
        w.addItems(spec.options or [])
        if spec.default and w.findText(spec.default) >= 0:
            w.setCurrentText(spec.default)
        w.setEditable(True)
        return w
    if spec.type == "check":
        w = QCheckBox()
        if spec.default.lower() in ("1", "yes", "true"):
            w.setChecked(True)
        return w
    if spec.type == "textarea":
        w = QTextEdit()
        w.setMaximumHeight(90)
        if spec.default:
            w.setPlainText(spec.default)
        return w
    if spec.type == "table":
        return TableInputWidget(spec)
    raise ValueError(spec.type)


def _get_field_value(spec: InputSpec, w: QWidget) -> str:
    if isinstance(w, QLineEdit):
        return w.text().strip()
    if isinstance(w, QDoubleSpinBox):
        return str(w.value())
    if isinstance(w, QComboBox):
        return w.currentText().strip()
    if isinstance(w, QCheckBox):
        return "YES" if w.isChecked() else "NO"
    if isinstance(w, QTextEdit):
        return w.toPlainText().strip()
    if isinstance(w, TableInputWidget):
        rows = w.values()
        if not rows:
            return ""
        return " | ".join(" ; ".join(r) for r in rows)
    return ""


def table_to_md_rows(value: str, columns: List[str]) -> str:
    """Convert a table input value back into markdown table rows."""
    if not value:
        return ""
    out = ["| " + " | ".join(columns) + " |",
           "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in value.split(" | "):
        cells = row.split(" ; ")
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


# ----------------------------------------------------------------------------
# WIZARD DIALOG
# ----------------------------------------------------------------------------

class _TemplatePage(QWizardPage):
    """Page 1: choose what kind of document to generate (friendly view)."""

    def __init__(self, templates: List[TemplateDef], parent=None):
        super().__init__(parent)
        self.setTitle("1. What would you like to generate?")
        self.setSubTitle(
            "Pick the document type. The software will ask which sections "
            "you want, collect the inputs, and produce an editable Word "
            "document.")

        lay = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)

        self.filter = QComboBox()
        self.filter.addItems(["All types", "Programs", "Procedures"])
        self.filter.currentTextChanged.connect(self._apply_filter)
        ll.addWidget(self.filter)

        self.listw = QListWidget()
        for t in templates:
            item = QListWidgetItem(f"{t.icon}  {t.name}")
            item.setData(Qt.UserRole, t.key)
            item.setToolTip(t.description)
            item.setSizeHint(QSize(0, 34))
            self.listw.addItem(item)
        self.listw.currentItemChanged.connect(self._on_select)
        ll.addWidget(self.listw)
        splitter.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(10, 0, 0, 0)
        self.desc = QLabel("Select a document type to see details.")
        self.desc.setWordWrap(True)
        self.desc.setStyleSheet("font-size:12px;color:#c0c0d0;")
        rl.addWidget(self.desc)
        rl.addStretch()
        splitter.addWidget(right)

        splitter.setSizes([420, 500])
        lay.addWidget(splitter)

        self._templates = templates
        if self.listw.count():
            self.listw.setCurrentRow(0)

    def selected_key(self) -> str:
        item = self.listw.currentItem()
        return item.data(Qt.UserRole) if item else ""

    def _apply_filter(self, text):
        for idx in range(self.listw.count()):
            item = self.listw.item(idx)
            t = self._by_key(item.data(Qt.UserRole))
            show = (text == "All types" or
                    (text == "Programs" and t.kind == "Program") or
                    (text == "Procedures" and t.kind == "Procedure"))
            item.setHidden(not show)

    def _by_key(self, key):
        for t in self._templates:
            if t.key == key:
                return t
        return None

    def _on_select(self, cur, _prev):
        if cur is None:
            return
        t = self._by_key(cur.data(Qt.UserRole))
        if t:
            n_sections = len(extract_sections(t.full_markdown))
            self.desc.setText(
                f"<b style='color:#e94560;'>{t.icon} {t.name}</b><br>"
                f"<span style='color:#4fc3f7;'>{t.kind}</span><br><br>"
                f"{t.description}<br><br>"
                f"<span style='color:#8a8a9a;'>Sections available: "
                f"{n_sections}  •  Fields to fill: {len(t.inputs)}</span>")


class _SectionsPage(QWizardPage):
    """Page 2: user picks which sections go into the document."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("2. Choose the sections")
        self.setSubTitle(
            "Tick the sections you want in the document. Unticked sections "
            "are omitted. The header and approval block are always kept.")

        lay = QVBoxLayout(self)
        self.listw = QListWidget()
        self.listw.setSelectionMode(QAbstractItemView.SingleSelection)
        lay.addWidget(self.listw)

        self.lbl = QLabel("")
        self.lbl.setStyleSheet("color:#8a8a9a;font-size:11px;")
        lay.addWidget(self.lbl)

        self._sections: List[str] = []
        self._saved: Dict[str, List[str]] = {}

    def initializePage(self):
        self.listw.clear()
        wiz = self.wizard()
        page0 = wiz.page(0)
        key = page0.selected_key()
        tdef = page0._by_key(key) if hasattr(page0, "_by_key") else None
        if tdef is None:
            return
        sections = extract_sections(tdef.full_markdown)
        self._sections = [h for h, _ in sections]

        prev = self._saved.get(key)
        for h, _ in sections:
            item = QListWidgetItem(h)
            item.setData(Qt.UserRole, h)
            if "APPROVAL" in h.upper():
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked)
                item.setFlags(item.flags() & ~Qt.ItemIsEnabled)
            else:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                if prev is not None:
                    item.setCheckState(Qt.Checked if h in prev else Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
            self.listw.addItem(item)
        self.lbl.setText(
            f"{len(sections)} sections — header + approval are always included")

    def selected_heads(self) -> List[str]:
        out = []
        for i in range(self.listw.count()):
            item = self.listw.item(i)
            if item.flags() & Qt.ItemIsEnabled and item.checkState() == Qt.Checked:
                out.append(item.data(Qt.UserRole))
        return out

    def validatePage(self) -> bool:
        wiz = self.wizard()
        key = wiz.page(0).selected_key()
        self._saved[key] = self.selected_heads()
        return True


class _InputsPage(QWizardPage):
    """Page 2: dynamic input form for the selected template."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("2. Provide the inputs")
        self.setSubTitle("Fill the requested fields. Empty fields will appear "
                         "as [To Be Filled] in the generated document.")

        lay = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        self.form_lay = QVBoxLayout(container)
        self.form_lay.setSpacing(10)
        scroll.setWidget(container)
        lay.addWidget(scroll)

        self.widgets: Dict[str, QWidget] = {}
        self._specs: Dict[str, InputSpec] = {}
        self._groups: Dict[str, QFormLayout] = {}
        self._group_widgets: Dict[str, QGroupBox] = {}
        self.web_notes: str = ""

    def _ensure_group(self, name: str) -> QFormLayout:
        if name in self._groups:
            return self._groups[name]
        gb = QGroupBox(name)
        fl = QFormLayout(gb)
        fl.setSpacing(7)
        self._groups[name] = fl
        self._group_widgets[name] = gb
        self.form_lay.addWidget(gb)
        return fl

    def initializePage(self):
        # clear previous
        for w in list(self.widgets.values()):
            try:
                w.setParent(None)
                w.deleteLater()
            except Exception:
                pass
        self.widgets.clear()
        self._specs.clear()
        self._groups.clear()
        self._group_widgets.clear()
        for gb in list(self._group_widgets.values()):
            gb.deleteLater()
        self._group_widgets.clear()

        tdef = self._selected_template()
        if tdef is None:
            return
        for spec in tdef.inputs:
            fl = self._ensure_group(spec.group)
            w = _build_field(spec)
            label = spec.label
            if spec.required:
                label = "* " + label
            fl.addRow(label, w)
            self.widgets[spec.key] = w
            self._specs[spec.key] = spec

        # Web research tool for field/formation introduction
        web_row = QHBoxLayout()
        self.btn_web = QPushButton("🌐  Web Research — Field / Formation Introduction")
        self.btn_web.setMaximumWidth(360)
        self.btn_web.clicked.connect(self._open_web)
        web_row.addWidget(self.btn_web)
        web_row.addStretch()
        self.form_lay.addLayout(web_row)

        # Field-knowledge enrichment (internal library + ML retrieval)
        kn_group = QGroupBox("📚  Field Knowledge & Intelligence (ML)")
        kn_lay = QVBoxLayout(kn_group)
        self.chk_enrich = QCheckBox(
            "Enrich the output with proven content from the real operations "
            "library (checklists, steps, procedures) — company names removed")
        self.chk_enrich.setChecked(True)
        kn_lay.addWidget(self.chk_enrich)
        krow = QHBoxLayout()
        krow.addWidget(QLabel("Enrichment level:"))
        self.enrich_level = QComboBox()
        self.enrich_level.addItems(["Moderate (recommended)", "Brief", "Detailed"])
        krow.addWidget(self.enrich_level)
        krow.addStretch()
        kn_lay.addLayout(krow)
        knote = QLabel(
            "🧠 Retrieval engine: TF-IDF (built-in ML) ranks the most relevant "
            "field content for this document type; semantic embeddings are "
            "used automatically when 'sentence-transformers' is installed.")
        knote.setWordWrap(True)
        knote.setStyleSheet("color:#8a8a9a;font-size:10px;")
        kn_lay.addWidget(knote)

        self.chk_rope = QCheckBox(
            "Include industry-standard field checklists (Rig Operations "
            "Performance Execution — BHA, bit, casing, cementing, tripping, "
            "well control, stuck pipe, H2S, etc.)")
        self.chk_rope.setChecked(True)
        kn_lay.addWidget(self.chk_rope)

        llm_row = QHBoxLayout()
        self.btn_llm = QPushButton("🤖  LLM Settings (rewrite with AI)")
        self.btn_llm.setMaximumWidth(280)
        self.btn_llm.clicked.connect(self._open_llm)
        llm_row.addWidget(self.btn_llm)
        self.lbl_llm = QLabel("LLM: off")
        self.lbl_llm.setStyleSheet("color:#8a8a9a;font-size:10px;")
        llm_row.addWidget(self.lbl_llm)
        llm_row.addStretch()
        kn_lay.addLayout(llm_row)
        self.form_lay.addWidget(kn_group)
        self.form_lay.addStretch()

    def _open_llm(self):
        try:
            from wizard_llm import LLMSettingsDialog, set_backend
            dlg = LLMSettingsDialog(self)
            if dlg.exec() == QDialog.Accepted:
                backend, key = dlg.get_values()
                set_backend(backend, key)
                self.lbl_llm.setText(
                    f"LLM: {backend if backend != 'none' else 'off'}")
        except Exception as e:
            QMessageBox.warning(self, "LLM Settings", str(e))

    def _open_web(self):
        """Open the web research dialog and store inserted markdown."""
        try:
            from wizard_web import run_web_research
            tdef = self._selected_template()
            key = tdef.key if tdef else ""
            text = run_web_research(key, self)
            if text:
                self.web_notes = text
                QMessageBox.information(
                    self, "Inserted",
                    "The research text will be added to the document as a "
                    "'Field & Formation Introduction (Web Research)' section "
                    "with source links.")
        except Exception as e:
            QMessageBox.warning(self, "Web Research", f"Not available: {e}")

    def _selected_template(self) -> Optional[TemplateDef]:
        wiz = self.wizard()
        page0 = wiz.page(0)
        key = page0.selected_key() if hasattr(page0, "selected_key") else ""
        if hasattr(page0, "_by_key"):
            return page0._by_key(key)
        return None

    def validatePage(self) -> bool:
        missing = []
        for key, spec in self._specs.items():
            if spec.required and not _get_field_value(spec, self.widgets[key]):
                missing.append(spec.label)
        if missing:
            QMessageBox.warning(
                self, "Required Inputs",
                "Please fill the required fields:\n\n• " + "\n• ".join(missing))
            return False
        return True

    def values(self) -> Dict[str, str]:
        out = {}
        for key, spec in self._specs.items():
            val = _get_field_value(spec, self.widgets[key])
            if spec.type == "table" and val:
                val = table_to_md_rows(val, spec.columns)
            out[key] = val
        if self.web_notes:
            out["web_notes"] = self.web_notes
        return out


class _RiskReviewPage(QWizardPage):
    """Page 3: automatic risk review of the document before output."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("3. Risk Review (automatic)")
        self.setSubTitle(
            "The software automatically checks the operations in your "
            "document against the drilling risk knowledge base, shows the "
            "key risks and asks you a few confirmation questions. The "
            "result is added to the document before final output.")

        lay = QVBoxLayout(self)

        # Analyze button + summary
        row = QHBoxLayout()
        self.btn_analyze = QPushButton("🔍  Analyze the Document for Risks")
        self.btn_analyze.setMinimumHeight(38)
        self.btn_analyze.clicked.connect(self._analyze)
        row.addWidget(self.btn_analyze)

        self.summary = QLabel("Not analyzed yet.")
        self.summary.setWordWrap(True)
        self.summary.setStyleSheet("color:#4fc3f7;font-weight:bold;")
        row.addWidget(self.summary, 1)
        lay.addLayout(row)

        # Risks table
        lay.addWidget(QLabel("Key Risks Identified (Critical / High):"))
        self.risk_table = QTableWidget()
        self.risk_table.setColumnCount(5)
        self.risk_table.setHorizontalHeaderLabels(
            ["Risk", "Severity", "Probability", "NPT (hrs)", "Primary Mitigation"])
        self.risk_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.risk_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.risk_table.setAlternatingRowColors(True)
        self.risk_table.setMinimumHeight(150)
        lay.addWidget(self.risk_table)

        # Questions
        self.q_label = QLabel("Confirmation questions — tick the ones already "
                              "addressed in the program:")
        self.q_label.setWordWrap(True)
        lay.addWidget(self.q_label)

        self.q_list = QListWidget()
        self.q_list.setMinimumHeight(120)
        lay.addWidget(self.q_list)

        # Forgotten items
        self.f_label = QLabel("")
        self.f_label.setWordWrap(True)
        lay.addWidget(self.f_label)

        # Include toggle
        self.chk_include = QCheckBox(
            "✅ Include the Risk Assessment & Contingency Plan section in the "
            "generated document")
        self.chk_include.setChecked(True)
        lay.addWidget(self.chk_include)

        self._results: Optional[Dict] = None
        self._questions: List[str] = []

    # -- analysis ----------------------------------------------------------
    def _selected_template(self):
        wiz = self.wizard()
        page0 = wiz.page(0)
        key = page0.selected_key() if hasattr(page0, "selected_key") else ""
        if hasattr(page0, "_by_key"):
            return page0._by_key(key)
        return None

    def _analyze(self):
        try:
            from wizard_risk import (build_sequence_from_document,
                                     run_risk_analysis,
                                     generate_risk_questions)
        except Exception as e:
            QMessageBox.warning(self, "Risk Module", f"Not available: {e}")
            return

        wiz = self.wizard()
        tdef = self._selected_template()
        if tdef is None:
            return
        sec_page = wiz.page(1)
        in_page = wiz.page(2)

        values = dict(in_page.values()) if hasattr(in_page, "values") else {}
        selected = sec_page.selected_heads() if hasattr(sec_page, "selected_heads") else []

        # Build the (filled, section-selected) markdown
        from wizard_engine import fill_template, render_selected
        md = fill_template(tdef, values)
        md = render_selected(md, selected)

        sequence = build_sequence_from_document(md, values)
        results = run_risk_analysis(sequence)

        self._results = results
        self._sequence = sequence
        self._values = values

        sev = results.get("severity_counts", {})
        crit = sev.get(RiskLevel.CRITICAL, 0)
        high = sev.get(RiskLevel.HIGH, 0)
        med = sev.get(RiskLevel.MEDIUM, 0)
        npt = results.get("total_expected_npt", 0)
        self.summary.setText(
            f"✓ {len(results.get('risks', []))} risks identified — "
            f"{crit} critical, {high} high, {med} medium | "
            f"expected NPT {npt:,.0f} hrs")

        # Risk table
        risks = results.get("risks", [])
        top = [r for r in risks
               if r.severity in (RiskLevel.CRITICAL, RiskLevel.HIGH)][:15]
        self.risk_table.setRowCount(len(top))
        for row, r in enumerate(top):
            plan = r.contingency_plans[0].action if r.contingency_plans else "—"
            self.risk_table.setItem(row, 0, QTableWidgetItem(r.problem))
            self.risk_table.setItem(row, 1, QTableWidgetItem(r.severity.value))
            self.risk_table.setItem(row, 2, QTableWidgetItem(f"{r.probability:.0%}"))
            self.risk_table.setItem(row, 3, QTableWidgetItem(f"{r.npt_hours:.0f}"))
            self.risk_table.setItem(row, 4, QTableWidgetItem(plan))
        self.risk_table.resizeRowsToContents()

        # Questions
        self._questions = generate_risk_questions(results, values)
        self.q_list.clear()
        for q in self._questions:
            item = QListWidgetItem(q)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setSizeHint(QSize(0, 40))
            self.q_list.addItem(item)

        # Forgotten items
        forgotten = results.get("forgotten_items", [])
        if forgotten:
            self.f_label.setText(
                f"☑️ {len(forgotten)} best-practice reminders will be added "
                f"to the risk section (first {min(len(forgotten), 12)}).")
        else:
            self.f_label.setText("")

    def answers(self) -> Dict[str, bool]:
        out = {}
        for i in range(self.q_list.count()):
            item = self.q_list.item(i)
            out[item.text()] = (item.checkState() == Qt.Checked)
        return out

    def initializePage(self):
        # auto-analyze once when the page is entered
        if self._results is None:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            try:
                self._analyze()
            finally:
                QApplication.restoreOverrideCursor()

    def validatePage(self) -> bool:
        return True


class _OptionsPage(QWizardPage):
    """Page 4: document metadata, formatting & output location."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("4. Document details, formatting & output")
        self.setSubTitle(
            "Set the document control info, choose the font and page "
            "layout, then pick where to save the Word file.")

        lay = QVBoxLayout(self)

        # -- Document control -------------------------------------------------
        g_doc = QGroupBox("Document Control")
        fl = QFormLayout(g_doc)
        fl.setSpacing(6)
        self.prepared = QLineEdit()
        self.reviewed = QLineEdit()
        self.approved = QLineEdit()
        self.revision = QLineEdit("01")
        self.date = QLineEdit(datetime.now().strftime("%d-%B-%Y"))
        self.doc_number = QLineEdit()
        self.doc_number.setPlaceholderText("e.g. DRL-PRG-2026-001 (optional)")

        fl.addRow("Prepared By:", self.prepared)
        fl.addRow("Reviewed By:", self.reviewed)
        fl.addRow("Approved By:", self.approved)
        fl.addRow("Revision:", self.revision)
        fl.addRow("Date:", self.date)
        fl.addRow("Document Number:", self.doc_number)
        lay.addWidget(g_doc)

        # -- Formatting -------------------------------------------------------
        g_fmt = QGroupBox("Formatting & Page Layout")
        ff = QFormLayout(g_fmt)
        ff.setSpacing(6)

        self.font = QComboBox()
        self.font.addItems(["Calibri", "Arial", "Times New Roman", "Cambria",
                            "Georgia", "Segoe UI", "Consolas"])
        self.font_size = QSpinBox()
        self.font_size.setRange(9, 14)
        self.font_size.setValue(11)
        ff.addRow("Font:", self.font)
        ff.addRow("Font Size:", self.font_size)

        self.page_size = QComboBox()
        self.page_size.addItems(["A4", "Letter"])
        self.orientation = QComboBox()
        self.orientation.addItems(["Portrait", "Landscape"])
        ff.addRow("Page Size:", self.page_size)
        ff.addRow("Orientation:", self.orientation)

        mrow = QHBoxLayout()
        self.m_left = QDoubleSpinBox(); self.m_left.setRange(0.5, 6.0); self.m_left.setValue(2.5)
        self.m_right = QDoubleSpinBox(); self.m_right.setRange(0.5, 6.0); self.m_right.setValue(2.0)
        self.m_top = QDoubleSpinBox(); self.m_top.setRange(0.5, 6.0); self.m_top.setValue(2.0)
        self.m_bottom = QDoubleSpinBox(); self.m_bottom.setRange(0.5, 6.0); self.m_bottom.setValue(2.0)
        for w in (self.m_left, self.m_right, self.m_top, self.m_bottom):
            w.setSuffix(" cm"); w.setDecimals(1)
        mrow.addWidget(QLabel("L:")); mrow.addWidget(self.m_left)
        mrow.addWidget(QLabel("R:")); mrow.addWidget(self.m_right)
        mrow.addWidget(QLabel("T:")); mrow.addWidget(self.m_top)
        mrow.addWidget(QLabel("B:")); mrow.addWidget(self.m_bottom)
        mrow.addStretch()
        ff.addRow("Margins:", mrow)

        self.cover = QCheckBox(); self.cover.setChecked(True)
        self.toc = QCheckBox(); self.toc.setChecked(True)
        ff.addRow("Cover page:", self.cover)
        ff.addRow("Table of contents:", self.toc)

        self.header_text = QLineEdit()
        self.header_text.setPlaceholderText("e.g. DRL-PRG-2026-001 | Rev 01")
        self.footer_text = QLineEdit()
        self.footer_text.setPlaceholderText("e.g. Company Confidential")
        ff.addRow("Header text:", self.header_text)
        ff.addRow("Footer text:", self.footer_text)
        lay.addWidget(g_fmt)

        # -- Cost & Pricing (CBS) ---------------------------------------------
        g_cbs = QGroupBox("💰 Cost & Pricing (CBS)")
        cv = QVBoxLayout(g_cbs)
        row_cbs = QHBoxLayout()
        self.chk_cbs = QCheckBox(
            "Include COST BREAKDOWN STRUCTURE / AFE section")
        self.chk_cbs.setChecked(False)
        self.chk_cbs.toggled.connect(
            lambda on: self.btn_cbs_sel.setEnabled(on))
        row_cbs.addWidget(self.chk_cbs)
        row_cbs.addStretch(1)
        self.btn_cbs_sel = QPushButton("📋 Select Goods & Services…")
        self.btn_cbs_sel.setEnabled(False)
        self.btn_cbs_sel.clicked.connect(self._open_cbs_selection)
        row_cbs.addWidget(self.btn_cbs_sel)
        cv.addLayout(row_cbs)
        self.lbl_cbs_sel = QLabel(
            "No items selected — the full catalog will be used "
            "(with quantities from the '💰 Cost & Pricing' tab).")
        self.lbl_cbs_sel.setWordWrap(True)
        self.lbl_cbs_sel.setStyleSheet("color: #8a8a9a; font-size: 10px;")
        cv.addWidget(self.lbl_cbs_sel)
        self._cbs_selection: Optional[list] = None
        lay.addWidget(g_cbs)

        # -- Drilling Problems (prevention & response) -----------------------
        g_prob = QGroupBox("🛟 Drilling Problems — Prevention & Response")
        pv = QVBoxLayout(g_prob)
        prow = QHBoxLayout()
        self.chk_problems = QCheckBox(
            "Include DRILLING PROBLEM PREVENTION & RESPONSE section")
        self.chk_problems.setChecked(False)
        self.chk_problems.toggled.connect(
            lambda on: self.btn_problems_sel.setEnabled(on))
        prow.addWidget(self.chk_problems)
        prow.addStretch(1)
        self.btn_problems_sel = QPushButton("🛟 Select Problems…")
        self.btn_problems_sel.setEnabled(False)
        self.btn_problems_sel.clicked.connect(self._open_problems_selection)
        prow.addWidget(self.btn_problems_sel)
        pv.addLayout(prow)
        self.lbl_problems_sel = QLabel(
            "No problems selected — the section will be skipped.")
        self.lbl_problems_sel.setWordWrap(True)
        self.lbl_problems_sel.setStyleSheet("color: #8a8a9a; font-size: 10px;")
        pv.addWidget(self.lbl_problems_sel)
        self._problems_selection: Optional[list] = None
        lay.addWidget(g_prob)

        # -- Output -----------------------------------------------------------
        out_group = QGroupBox("Output File")
        ol = QVBoxLayout(out_group)
        row = QHBoxLayout()
        self.path = QLineEdit()
        self.path.setPlaceholderText("Select output folder...")
        btn = QPushButton("📁 Browse...")
        btn.clicked.connect(self._browse)
        row.addWidget(self.path)
        row.addWidget(btn)
        ol.addLayout(row)
        self.fname = QLineEdit()
        self.fname.setPlaceholderText("File name (auto-filled)")
        ol.addWidget(self.fname)
        lay.addWidget(out_group)

        self.registerField("preparedBy", self.prepared)
        self.registerField("reviewedBy", self.reviewed)
        self.registerField("approvedBy", self.approved)
        self.registerField("revision", self.revision)
        self.registerField("docDate", self.date)

    def _open_problems_selection(self):
        """باز کردن دیالوگ انتخاب مشکلات حفاری"""
        try:
            from drilling_problems_ui import ProblemsDialog
            dlg = ProblemsDialog(self)
            if dlg.exec() and dlg.selection:
                self._problems_selection = dlg.selection
                n = len(dlg.selection)
                crit = sum(1 for p in dlg.selection
                           if p.severity in ("Critical", "High"))
                self.lbl_problems_sel.setText(
                    f"✔ {n} problem(s) selected ({crit} Critical/High). "
                    f"Open again to change.")
            else:
                self._problems_selection = None
                self.lbl_problems_sel.setText(
                    "Selection cancelled — the section will be skipped.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Problems Selection", str(e))

    def _open_cbs_selection(self):
        """باز کردن دیالوگ انتخاب کالا/سرویس برای سکشن CBS"""
        try:
            from cbs_ui import CbsSelectionDialog
            dlg = CbsSelectionDialog(self)
            if dlg.exec() and dlg.selection:
                self._cbs_selection = dlg.selection
                n = len(dlg.selection)
                total = sum(s["price"] * s["qty"] for s in dlg.selection)
                self.lbl_cbs_sel.setText(
                    f"✔ {n} item(s) selected — estimated "
                    f"{total:,.2f} (excl. day-rates/contingency). "
                    f"Open again to change.")
            else:
                self._cbs_selection = None
                self.lbl_cbs_sel.setText(
                    "Selection cancelled — the full catalog will be used.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "CBS Selection", str(e))

    def output_options(self) -> dict:
        return {
            "font": self.font.currentText(),
            "font_size": float(self.font_size.value()),
            "page": self.page_size.currentText(),
            "orientation": self.orientation.currentText(),
            "margin_left": self.m_left.value(),
            "margin_right": self.m_right.value(),
            "margin_top": self.m_top.value(),
            "margin_bottom": self.m_bottom.value(),
            "cover": self.cover.isChecked(),
            "toc": self.toc.isChecked(),
            "header_text": self.header_text.text().strip(),
            "footer_text": self.footer_text.text().strip(),
            "document_number": self.doc_number.text().strip(),
            "include_cbs": self.chk_cbs.isChecked(),
            "cbs_selection": self._cbs_selection,
            "include_problems": self.chk_problems.isChecked(),
            "problems_selection": self._problems_selection,
        }

    def initializePage(self):
        tdef = self._selected_template()
        if tdef:
            base = tdef.name.replace(" ", "_").replace("/", "-")
            self.fname.setText(f"{base}.docx")
        default_dir = str(Path.cwd() / "projects" / "exports")
        if not self.path.text():
            self.path.setText(default_dir)

    def _selected_template(self):
        wiz = self.wizard()
        page0 = wiz.page(0)
        key = page0.selected_key() if hasattr(page0, "selected_key") else ""
        if hasattr(page0, "_by_key"):
            return page0._by_key(key)
        return None

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Folder",
                                              self.path.text() or str(Path.cwd()))
        if d:
            self.path.setText(d)

    def output_path(self) -> str:
        folder = self.path.text().strip() or str(Path.cwd())
        fname = self.fname.text().strip() or "Generated_Document.docx"
        if not fname.lower().endswith(".docx"):
            fname += ".docx"
        return str(Path(folder) / fname)


class _GeneratePage(QWizardPage):
    """Page 5: generate the document."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("5. Generate")
        self.setSubTitle("Generate the Word document now.")

        lay = QVBoxLayout(self)
        self.status = QLabel("Ready to generate.")
        self.status.setWordWrap(True)
        lay.addWidget(self.status)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        lay.addWidget(self.progress)

        btns = QHBoxLayout()
        self.btn_gen = QPushButton("⚙️  GENERATE WORD DOCUMENT")
        self.btn_gen.setMinimumHeight(44)
        self.btn_gen.clicked.connect(self._generate)
        btns.addWidget(self.btn_gen)

        self.btn_open = QPushButton("📂 Open Document")
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self._open_doc)
        btns.addWidget(self.btn_open)

        self.btn_folder = QPushButton("🗂️ Open Folder")
        self.btn_folder.setEnabled(False)
        self.btn_folder.clicked.connect(self._open_folder)
        btns.addWidget(self.btn_folder)
        lay.addLayout(btns)
        lay.addStretch()

        self._last_path = ""

    def initializePage(self):
        self._last_path = ""
        self.btn_open.setEnabled(False)
        self.btn_folder.setEnabled(False)
        self.progress.setValue(0)
        tdef = self._selected_template()
        if tdef:
            wiz = self.wizard()
            sec_page = wiz.page(1)
            n_sel = len(sec_page.selected_heads()) if hasattr(sec_page, "selected_heads") else 0
            self.status.setText(
                f"Document: <b>{tdef.icon} {tdef.name}</b><br>"
                f"Sections selected: <b>{n_sel}</b><br>"
                f"Press GENERATE to create the Word document.")

    def _selected_template(self):
        wiz = self.wizard()
        page0 = wiz.page(0)
        key = page0.selected_key() if hasattr(page0, "selected_key") else ""
        if hasattr(page0, "_by_key"):
            return page0._by_key(key)
        return None

    def _generate(self):
        tdef = self._selected_template()
        if tdef is None:
            QMessageBox.warning(self, "No Document Type",
                                "Select a document type first.")
            return

        wiz = self.wizard()
        sec_page = wiz.page(1)      # sections
        in_page = wiz.page(2)       # inputs
        opt_page = wiz.page(4)      # options

        values = dict(in_page.values()) if hasattr(in_page, "values") else {}

        # Document metadata
        values.setdefault("prepared_by", self.field("preparedBy") or "")
        values.setdefault("reviewed_by", self.field("reviewedBy") or "")
        values.setdefault("approved_by", self.field("approvedBy") or "")
        values.setdefault("revision", self.field("revision") or "01")
        values.setdefault("doc_date", self.field("docDate") or "")

        meta = {
            "date": values.get("doc_date", ""),
            "document_number": opt_page.output_options().get("document_number", ""),
            "revision": values.get("revision", ""),
            "prepared_by": values.get("prepared_by", ""),
            "reviewed_by": values.get("reviewed_by", ""),
            "approved_by": values.get("approved_by", ""),
            "title": neutralize_text(tdef.name,
                                     str(values.get("operator", "") or ""),
                                     str(values.get("contractor", "") or "")),
            "operator": str(values.get("operator", "") or
                            values.get("operator_name", "") or ""),
            "contractor": str(values.get("contractor", "") or
                              values.get("contractor_name", "") or ""),
        }

        self.progress.setValue(15)
        QApplication.processEvents()

        try:
            # 1) Fill placeholders with user values
            md = fill_template(tdef, values)
            self.progress.setValue(35)
            QApplication.processEvents()

            # 2) Keep only the user-selected sections
            selected = sec_page.selected_heads() if hasattr(sec_page, "selected_heads") else []
            md = render_selected(md, selected)

            # 3) Web research section (field/formation introduction)
            web_notes = values.get("web_notes", "")
            if web_notes:
                md += ("\n\n## FIELD & FORMATION INTRODUCTION (WEB RESEARCH)\n\n"
                       + web_notes + "\n")
            self.progress.setValue(55)
            QApplication.processEvents()

            # 4) Risk review section (automatic, before final output)
            risk_page = wiz.page(3)
            if (hasattr(risk_page, "_results") and risk_page._results
                    and getattr(risk_page, "chk_include", None)
                    and risk_page.chk_include.isChecked()):
                try:
                    from wizard_risk import build_risk_section_md
                    answers = risk_page.answers()
                    seq = getattr(risk_page, "_sequence", "")
                    risk_md = build_risk_section_md(
                        risk_page._results, answers, seq)
                    if risk_md:
                        md = md.rstrip() + "\n\n---\n\n" + risk_md
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            # 4b) Field-knowledge enrichment (ML retrieval + optional LLM rewrite)
            try:
                if hasattr(in_page, "chk_enrich") and in_page.chk_enrich.isChecked():
                    from wizard_knowledge import (enrich_template,
                                                 get_chunks_for)
                    from wizard_llm import rewrite_chunks
                    level = {
                        "Brief": "brief",
                        "Moderate (recommended)": "moderate",
                        "Detailed": "detailed",
                    }.get(in_page.enrich_level.currentText(), "moderate")
                    op_name = meta.get("operator", "")
                    con_name = meta.get("contractor", "")
                    chunks = get_chunks_for(tdef.key, level)
                    if chunks:
                        kn = rewrite_chunks(
                            chunks, tdef.name,
                            max_input_chars=4000 if level == "brief" else 5500,
                            operator_name=op_name, contractor_name=con_name)
                    else:
                        kn = ""
                    if kn:
                        kn = ("## FIELD KNOWLEDGE ENRICHMENT "
                              "(FROM REAL OPERATIONS LIBRARY)\n\n"
                              "Content below was retrieved by the ML "
                              "engine and rewritten by the AI "
                              "assistant from the internal "
                              "field-document library. Company "
                              "names have been removed.\n\n" + kn)
                    if kn:
                        md = md.rstrip() + "\n\n---\n\n" + kn
            except Exception:
                import traceback
                traceback.print_exc()
            self.progress.setValue(60)
            QApplication.processEvents()

            # 4c) ROPE field checklists
            try:
                if hasattr(in_page, "chk_rope") and in_page.chk_rope.isChecked():
                    from wizard_rope import get_rope_checklists
                    rope_md = get_rope_checklists(
                        tdef.key, level,
                        meta.get("operator", ""),
                        meta.get("contractor", ""))
                    if rope_md:
                        md = md.rstrip() + "\n\n---\n\n" + rope_md
            except Exception:
                import traceback
                traceback.print_exc()
            # 4d0) Drilling problems prevention & response section
            try:
                opts4d0 = opt_page.output_options()
                if opts4d0.get("include_problems") and \
                        opts4d0.get("problems_selection"):
                    from drilling_problems_db import build_problems_markdown
                    prob_md = build_problems_markdown(
                        opts4d0["problems_selection"],
                        meta.get("operator", ""))
                    if prob_md:
                        md = md.rstrip() + "\n\n---\n\n" + prob_md
            except Exception:
                import traceback
                traceback.print_exc()
            # 4d) CBS / AFE cost section (user-selected goods & services)
            try:
                opts4d = opt_page.output_options()
                if opts4d.get("include_cbs"):
                    from cbs_db import (CBSDatabase, CbsItem,
                                        build_cbs_markdown,
                                        get_time_breakdown_summary)
                    cdb = CBSDatabase()
                    sel = opts4d.get("cbs_selection")
                    if sel:
                        cbs_items = [CbsItem(
                            name=s["name"], unit=s["unit"],
                            unit_price=s["price"], qty=s["qty"])
                            for s in sel]
                    else:
                        cbs_items = cdb.get_items()
                    tb = get_time_breakdown_summary()
                    total_days = 0.0
                    try:
                        total_days = float(values.get("total_days") or 0)
                    except (TypeError, ValueError):
                        total_days = 0.0
                    if total_days <= 0:
                        total_days = tb.get("total_days", 0.0)
                    depth_key = ("target_depth" if values.get("target_depth")
                                 else "depth" if values.get("depth")
                                 else "depth_m")
                    try:
                        depth_m = float(values.get(depth_key) or 0)
                    except (TypeError, ValueError):
                        depth_m = 0.0
                    cbs_md = build_cbs_markdown(
                        cbs_items,
                        total_days=total_days,
                        well_depth_m=depth_m,
                        well_name=values.get("well_name", ""),
                        operator=meta.get("operator", ""),
                        currency=cdb.get_currency())
                    if cbs_md:
                        md = md.rstrip() + "\n\n---\n\n" + cbs_md
            except Exception:
                import traceback
                traceback.print_exc()
            self.progress.setValue(65)
            QApplication.processEvents()

            # 5) Neutralize any hard-coded company/brand names
            md = neutralize_text(md, meta.get("operator", ""),
                                  meta.get("contractor", ""))

            # 6) Render to Word with the chosen formatting
            options = opt_page.output_options() if hasattr(opt_page, "output_options") else {}
            out = opt_page.output_path()
            Path(out).parent.mkdir(parents=True, exist_ok=True)
            ok = md_to_docx(md, out, meta, options)
            self.progress.setValue(100)
            self._last_path = out
            if ok:
                self.status.setText(
                    f"✅ <b>Document generated successfully!</b><br>"
                    f"📄 {out}")
                self.btn_open.setEnabled(True)
                self.btn_folder.setEnabled(True)
            else:
                self.status.setText("❌ Generation failed.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.status.setText(f"❌ Error: {e}")
            QMessageBox.critical(self, "Generation Error", str(e))

    def _open_doc(self):
        if self._last_path and Path(self._last_path).exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._last_path))

    def _open_folder(self):
        if self._last_path:
            QDesktopServices.openUrl(
                QUrl.fromLocalFile(str(Path(self._last_path).parent)))


class GeneratorWizard(QWizard):
    """The universal program & procedure generator wizard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧙  Program & Procedure Generator Wizard")
        self.setMinimumSize(1100, 760)
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.NoCancelButtonOnLastPage, False)
        self.setOption(QWizard.HaveHelpButton, False)

        from wizard_library import ALL_TEMPLATES
        from wizard_procedures import PROCEDURE_TEMPLATES
        from wizard_offshore import OFFSHORE_TEMPLATES
        templates: List[TemplateDef] = list(ALL_TEMPLATES) + \
            list(PROCEDURE_TEMPLATES) + list(OFFSHORE_TEMPLATES)

        self.addPage(_TemplatePage(templates))   # 0 type
        self.addPage(_SectionsPage())            # 1 sections
        self.addPage(_InputsPage())              # 2 inputs
        self.addPage(_RiskReviewPage())          # 3 risk review
        self.addPage(_OptionsPage())             # 4 options
        self.addPage(_GeneratePage())            # 5 generate

        self.setStartId(0)


def run_wizard(parent=None) -> Optional[str]:
    """Launch the wizard; returns the generated document path if any."""
    wiz = GeneratorWizard(parent)
    if wiz.exec() == QDialog.Accepted:
        gen_page = wiz.page(5)
        if hasattr(gen_page, "_last_path") and gen_page._last_path:
            return gen_page._last_path
    return None
