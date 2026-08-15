# ============================================================================
# INTEGRATED TABS & TOOLS
# ============================================================================
# This module adds the new-generation UI to the Drilling Program Generator:
#   1. DashboardTab        - Home screen with quick actions, stats & recents
#   2. RiskAnalyzerTab     - Embedded Drilling Risk Analysis & Contingency
#                            Planning System (drilling_risk_analyzer.py)
#   3. MasterProgramsTab   - Viewer for Master Execution Documents / Programs
#                            (programs/*.md) with section navigation
#   4. EngineeringToolsTab - Quick engineering calculators (unit converter,
#                            hydraulics, casing verification, cement, well
#                            control, torque & drag)
#   5. DocumentPreviewDialog - Real-time text preview of the generated program
#
# NOTE: No functionality of the original modules is removed or reduced.
# ============================================================================

import re
import html
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QTextBrowser, QSplitter,
    QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox,
    QTextEdit, QDialog, QStackedWidget, QGroupBox, QScrollArea,
    QMessageBox, QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QSize, QUrl
from PySide6.QtGui import QFont, QColor, QDesktopServices, QTextCursor

# ----------------------------------------------------------------------------
# STYLES
# ----------------------------------------------------------------------------

INTEGRATED_STYLE = """
QFrame#card {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    border-radius: 10px;
}
QFrame#card:hover {
    border: 2px solid #e94560;
    background-color: #16213e;
}
QLabel#cardTitle {
    color: #e0e0e0;
    font-size: 13px;
    font-weight: bold;
}
QLabel#cardDesc {
    color: #8a8a9a;
    font-size: 11px;
}
QLabel#cardIcon {
    font-size: 26px;
}
QLabel#dashHeader {
    color: #e94560;
    font-size: 24px;
    font-weight: bold;
    padding: 12px;
}
QLabel#dashSub {
    color: #a0a0b8;
    font-size: 12px;
}
QFrame#banner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0f3460, stop:0.5 #16213e, stop:1 #0f3460);
    border: 2px solid #e94560;
    border-radius: 12px;
}
"""


# ----------------------------------------------------------------------------
# HELPER: MARKDOWN -> HTML (lightweight renderer for program documents)
# ----------------------------------------------------------------------------

def md_to_html(md_text: str) -> str:
    """Convert a practical subset of Markdown to HTML for QTextBrowser.

    Supported: ATX headings (#..#####), bold, italic, inline code, fenced
    code blocks, unordered/ordered lists, tables (| ... |), blockquotes,
    horizontal rules, paragraphs.
    """
    lines = md_text.replace("\r\n", "\n").split("\n")
    out: List[str] = []
    i = 0

    def esc(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
        return s

    def is_table_sep(line: str) -> bool:
        return bool(re.match(r"^\s*\|?[\s:|-]+\|?\s*$", line)) and "-" in line

    while i < len(lines):
        line = lines[i].rstrip()

        # Fenced code block
        if line.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append(
                '<pre style="background:#1a1a2e;color:#e0e0e0;'
                'padding:8px;border-radius:6px;">'
                + "\n".join(buf) + "</pre>")
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            size = max(18 - level * 2, 11)
            color = "#e94560" if level <= 2 else "#d4a24e" if level == 3 else "#9fb8d9"
            out.append(
                f'<h{level} style="color:{color};font-size:{size}px;'
                f'margin:14px 0 6px 0;">{esc(m.group(2))}</h{level}>')
            i += 1
            continue

        # Horizontal rule
        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        # Blockquote
        if line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(esc(lines[i].lstrip("> ")))
                i += 1
            out.append(
                '<blockquote style="border-left:4px solid #e94560;'
                'margin:8px 0;padding:6px 12px;color:#c9c9d8;'
                'background:#1a1a2e;border-radius:4px;">'
                + "<br>".join(buf) + "</blockquote>")
            continue

        # Table
        if line.lstrip().startswith("|") and i + 1 < len(lines) and \
                is_table_sep(lines[i + 1]):
            header_cells = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2  # skip separator
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            t = ['<table border="1" cellspacing="0" cellpadding="5" '
                 'style="border-collapse:collapse;width:100%;'
                 'margin:8px 0;font-size:11px;">']
            t.append('<thead><tr style="background:#0f3460;color:#e94560;">')
            for c in header_cells:
                t.append(f"<th>{esc(c)}</th>")
            t.append("</tr></thead><tbody>")
            for row in rows:
                t.append("<tr>")
                for idx, c in enumerate(row):
                    bg = "#16213e" if idx % 2 == 0 else "#1a1a2e"
                    t.append(f'<td style="background:{bg};">{esc(c)}</td>')
                t.append("</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # Unordered list
        if re.match(r"^\s*[-*+]\s+", line):
            buf = []
            while i < len(lines) and re.match(r"^\s*[-*+]\s+", lines[i]):
                item = re.sub(r"^\s*[-*+]\s+", "", lines[i])
                buf.append(f"<li>{esc(item)}</li>")
                i += 1
            out.append("<ul>" + "".join(buf) + "</ul>")
            continue

        # Ordered list
        if re.match(r"^\s*\d+[.)]\s+", line):
            buf = []
            while i < len(lines) and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                item = re.sub(r"^\s*\d+[.)]\s+", "", lines[i])
                buf.append(f"<li>{esc(item)}</li>")
                i += 1
            out.append("<ol>" + "".join(buf) + "</ol>")
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph (join consecutive plain lines). Guarantees progress:
        # any line that reaches here is consumed, so the loop cannot stall.
        buf = []
        while i < len(lines):
            s = lines[i].strip()
            if not s:
                break
            if s.startswith("#") or s.startswith(">") or \
                    s.startswith("```") or s.startswith("|"):
                break
            if re.match(r"^\s*[-*+]\s+", lines[i]):
                break
            if re.match(r"^\s*\d+[.)]\s+", lines[i]):
                break
            if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", lines[i]):
                break
            buf.append(esc(s))
            i += 1
        if buf:
            out.append("<p style='margin:6px 0;'>" + "<br>".join(buf) + "</p>")
        else:
            # Unmatched line (e.g. bare '*' emphasis or stray table row) -
            # consume it as plain text to keep parsing moving.
            out.append("<p style='margin:6px 0;'>" + esc(line) + "</p>")
            i += 1

    body = "\n".join(out)
    return f"""<html><head><style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px;
               color: #d5d5e0; background: #16213e; padding: 18px; }}
        a {{ color: #4fc3f7; }}
        </style></head><body>{body}</body></html>"""


# ----------------------------------------------------------------------------
# HELPER: FAST RENDERER FOR LARGE EXTRACTED DOCUMENTS
# ----------------------------------------------------------------------------

def md_to_html_fast(md_text: str) -> str:
    """Lightweight renderer for very large extracted documents (PDF text).

    Optimised for speed: headings, paragraphs, hr, blockquote and pre only.
    Table/list markdown parsing is skipped — these documents are mostly
    plain extracted text, and rendering must stay fast (multi-MB files).
    """
    lines = md_text.replace("\r\n", "\n").split("\n")
    out: List[str] = []
    i, n = 0, len(lines)

    def esc(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
        return s

    while i < n:
        line = lines[i].rstrip()

        if line.startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            i += 1
            out.append('<pre style="background:#1a1a2e;color:#e0e0e0;'
                       'padding:8px;border-radius:6px;">'
                       + "\n".join(buf) + "</pre>")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            size = max(17 - level * 2, 11)
            color = "#e94560" if level <= 2 else "#d4a24e"
            out.append(
                f'<h{level} style="color:{color};font-size:{size}px;'
                f'margin:14px 0 6px 0;">{esc(m.group(2))}</h{level}>')
            i += 1
            continue

        if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", line):
            out.append("<hr>")
            i += 1
            continue

        if not line.strip():
            i += 1
            continue

        # paragraph — join consecutive plain lines, guaranteed progress
        buf = []
        while i < n:
            s = lines[i].strip()
            if not s or s.startswith("#") or s.startswith("```"):
                break
            if re.match(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$", lines[i]):
                break
            buf.append(esc(s))
            i += 1
        if buf:
            out.append("<p style='margin:4px 0;'>" + "<br>".join(buf) + "</p>")
        else:
            out.append("<p style='margin:4px 0;'>" + esc(line) + "</p>")
            i += 1

    body = "\n".join(out)
    return f"""<html><head><style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; font-size: 12px;
               color: #d5d5e0; background: #16213e; padding: 14px; }}
        a {{ color: #4fc3f7; }}
        </style></head><body>{body}</body></html>"""


def render_document(md_text: str) -> str:
    """Pick the appropriate renderer based on document size."""
    if len(md_text) > 300_000:
        return md_to_html_fast(md_text)
    return md_to_html(md_text)


# ----------------------------------------------------------------------------
# DASHBOARD TAB
# ----------------------------------------------------------------------------

class ActionCard(QFrame):
    """Clickable card used on the dashboard."""

    def __init__(self, icon: str, title: str, description: str,
                 callback, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(110)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("cardIcon")
        icon_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(icon_lbl)

        txt = QVBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setObjectName("cardTitle")
        desc_lbl = QLabel(description)
        desc_lbl.setObjectName("cardDesc")
        desc_lbl.setWordWrap(True)
        txt.addWidget(title_lbl)
        txt.addWidget(desc_lbl)
        txt.addStretch()
        lay.addLayout(txt, 1)

        self._callback = callback

    def mousePressEvent(self, event):
        if self._callback:
            self._callback()
        super().mousePressEvent(event)


class DashboardTab(QWidget):
    """Home / dashboard tab with quick actions, stats and recent projects."""

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.setStyleSheet(INTEGRATED_STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(14, 10, 14, 10)
        outer.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        container = QWidget()
        lay = QVBoxLayout(container)
        lay.setSpacing(14)

        # Banner
        banner = QFrame()
        banner.setObjectName("banner")
        b_lay = QVBoxLayout(banner)
        b_lay.setContentsMargins(18, 16, 18, 16)
        title = QLabel("🛢️  Drilling Program & Procedure Generator  —  Professional Edition")
        title.setObjectName("dashHeader")
        sub = QLabel(
            "Plan • Design • Generate — Drilling Programs, Workover Procedures, "
            "Risk Analysis, Engineering Calculations & Master Execution Documents "
            "in one integrated workspace.")
        sub.setObjectName("dashSub")
        sub.setWordWrap(True)
        b_lay.addWidget(title)
        b_lay.addWidget(sub)
        lay.addWidget(banner)

        # --- Project actions ---
        sec1 = QLabel("📁  PROJECT")
        sec1.setObjectName("cardTitle")
        lay.addWidget(sec1)

        grid = QGridLayout()
        grid.setSpacing(10)
        cards = [
            ("🆕", "New Project", "Start a blank drilling program project",
             self.main_window.new_project),
            ("📂", "Open Project", "Load a saved project from the database",
             self.main_window.open_project),
            ("💾", "Save Project", "Save the current project to the database",
             self.main_window.save_project),
            ("✅", "Validate Data", "Check data completeness before generation",
             self.main_window.validate_data),
            ("👁️", "Preview Document", "Live text preview of the program",
             self.main_window.preview_document),
            ("📄", "Generate Word Document",
             "Export the full Drilling Program to Microsoft Word (.docx)",
             self.main_window.generate_document),
        ]
        for idx, (icon, t, d, cb) in enumerate(cards):
            grid.addWidget(ActionCard(icon, t, d, cb), idx // 3, idx % 3)
        lay.addLayout(grid)

        # --- Wizard (generator) ---
        wiz_card = ActionCard(
            "🧙", "Program & Procedure Wizard",
            "“I want a drilling program / workover / cementing / procedure...” "
            "— answer the questions and get a complete Word document.",
            self._open_wizard)
        lay.addWidget(wiz_card)

        # --- Tools & analysis ---
        sec2 = QLabel("🧰  TOOLS & ANALYSIS")
        sec2.setObjectName("cardTitle")
        lay.addWidget(sec2)

        grid2 = QGridLayout()
        grid2.setSpacing(10)
        tools = [
            ("⛽", "Risk Analyzer",
             "Drilling risk analysis & contingency planning (expert system + AI)",
             self._open_risk),
            ("🧮", "Engineering Tools",
             "Hydraulics, casing verification, cement, well control, units",
             self._open_engineering),
            ("📋", "Procedure Manager",
             "Step-by-step procedures, checklists & Word export",
             self._open_procedures),
            ("🧬", "Operational Templates",
             "Phase-by-phase operational template library",
             self._open_templates),
            ("⏱️", "Time Breakdown",
             "Phase durations, NPT & AFE time editor",
             self._open_time_breakdown),
        ]
        for idx, (icon, t, d, cb) in enumerate(tools):
            grid2.addWidget(ActionCard(icon, t, d, cb), idx // 3, idx % 3)
        lay.addLayout(grid2)

        # --- Stats + Recents ---
        stats_row = QHBoxLayout()
        stats_row.setSpacing(10)

        stats_card = QFrame()
        stats_card.setObjectName("card")
        s_lay = QVBoxLayout(stats_card)
        s_lay.setContentsMargins(14, 12, 14, 12)
        s_title = QLabel("📊  LIBRARY STATUS")
        s_title.setObjectName("cardTitle")
        s_lay.addWidget(s_title)
        self.stats_text = QLabel("Loading...")
        self.stats_text.setObjectName("cardDesc")
        self.stats_text.setWordWrap(True)
        s_lay.addWidget(self.stats_text)
        stats_row.addWidget(stats_card, 2)

        recents_card = QFrame()
        recents_card.setObjectName("card")
        r_lay = QVBoxLayout(recents_card)
        r_lay.setContentsMargins(14, 12, 14, 12)
        r_title = QLabel("🕘  RECENT PROJECTS")
        r_title.setObjectName("cardTitle")
        r_lay.addWidget(r_title)
        self.recents_list = QListWidget()
        self.recents_list.setMaximumHeight(140)
        self.recents_list.itemDoubleClicked.connect(self._open_recent)
        r_lay.addWidget(self.recents_list)
        stats_row.addWidget(recents_card, 3)

        lay.addLayout(stats_row)

        lay.addStretch()
        scroll.setWidget(container)
        outer.addWidget(scroll)

        self.refresh_stats()

    # -- navigation helpers ------------------------------------------------
    def _open_wizard(self):
        try:
            from wizard_engine import run_wizard
            path = run_wizard(self.main_window)
            if path:
                self.main_window.statusBar().showMessage(
                    f"✅ Generated: {path}")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self.main_window, "Wizard Error", str(e))

    def _open_risk(self):
        self.main_window.open_tab("risk")

    def _open_engineering(self):
        self.main_window.open_tab("engineering")

    def _open_procedures(self):
        self.main_window._show_procedure_manager()

    def _open_templates(self):
        self.main_window._show_operational_templates()

    def _open_time_breakdown(self):
        self.main_window._show_time_breakdown()

    def _open_recent(self, item):
        try:
            proj_id = item.data(Qt.UserRole)
            if proj_id is not None:
                self.main_window._open_project_by_id(proj_id)
        except Exception:
            pass

    def refresh_stats(self):
        """Refresh library statistics and recent projects."""
        try:
            from procedures_db import ProcedureDatabase
            db = ProcedureDatabase()
            stats = db.get_stats()
            db.close()
            txt = (f"<b style='color:#e94560;'>{stats['total_procedures']}</b> "
                   f"procedures in library<br>"
                   f"<b style='color:#e94560;'>{stats['total_steps']}</b> "
                   f"operational steps<br>"
                   f"<b style='color:#e94560;'>{stats['total_checklist_items']}</b> "
                   f"checklist items<br>"
                   f"<b style='color:#e94560;'>{stats['categories']}</b> categories")
        except Exception:
            txt = "Procedure library not available."
        try:
            from operational_templates import get_template_library
            lib = get_template_library()
            txt += (f"<br><b style='color:#e94560;'>"
                    f"{len(getattr(lib, 'well_templates', []))}</b> well templates<br>"
                    f"<b style='color:#e94560;'>"
                    f"{len(getattr(lib, 'phase_templates', []))}</b> phase templates")
        except Exception:
            pass
        self.stats_text.setText(txt)

        self.recents_list.clear()
        try:
            from drilling_database import DrillingProjectDatabase
            db = DrillingProjectDatabase()
            projects = db.get_all_projects() or []
            for p in projects[:8]:
                item = QListWidgetItem(
                    f"📄 {p.get('name', 'Project')}  |  {p.get('well_name', '')}  |  "
                    f"{p.get('operator', '')}  |  {p.get('modified', '')}")
                item.setData(Qt.UserRole, p.get('id'))
                self.recents_list.addItem(item)
            db.close()
        except Exception:
            pass


# ----------------------------------------------------------------------------
# RISK ANALYZER TAB (embedded drilling_risk_analyzer.MainWindow)
# ----------------------------------------------------------------------------

class RiskAnalyzerTab(QWidget):
    """Embeds the full Drilling Risk Analysis & Contingency Planning System.

    The original application (drilling_risk_analyzer.py) is used as-is; its
    own stylesheet and all features (expert risk database, contingency plans,
    forgotten-items checklist, summary, AI backends) remain fully intact.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        from drilling_risk_analyzer import MainWindow as RiskAnalyzerMainWindow
        self.risk_window = RiskAnalyzerMainWindow()
        self.risk_window.setParent(self)
        lay.addWidget(self.risk_window)


# ----------------------------------------------------------------------------
# MASTER PROGRAMS TAB
# ----------------------------------------------------------------------------

class MasterProgramsTab(QWidget):
    """Document Library viewer for Master Execution Documents.

    Two levels:
      - programs/*.md        : curated master documents (ESP workover, real
                               drilling programs S19/AZNS/SPH)
      - programs/library/*.txt : 214 real programs & procedures extracted
                               from the user's combined files, browsable by
                               category with in-document search
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.programs_dir = Path(__file__).resolve().parent / "programs"
        self.library_dir = self.programs_dir / "library"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)

        header = QLabel(
            "📚  MASTER EXECUTION DOCUMENTS  —  complete workover / drilling "
            "programs loaded into the software")
        header.setStyleSheet(
            "color:#e94560;font-size:15px;font-weight:bold;padding:6px;")
        outer.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)

        # Left: navigation (master docs + library by category)
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Documents:")
        lbl.setStyleSheet("color:#a0a0b8;font-weight:bold;")
        ll.addWidget(lbl)

        self.section_combo = QComboBox()
        self.section_combo.addItems(["📘 Master Programs",
                                     "📚 Library — All (214)",
                                     "🏗️ Library — Casing & Cementing",
                                     "🧱 Library — Cementing & Plugs",
                                     "🛢️ Library — Drilling Programs",
                                     "🔧 Library — Workover Programs",
                                     "⚙️ Library — Drilling Procedures",
                                     "🔴 Library — Well Control",
                                     "🔀 Library — Sidetrack / Whipstock",
                                     "🎣 Library — Fishing / Backoff",
                                     "🧪 Library — Testing (LOT/DST/Dry)",
                                     "🔗 Library — Liner & Tie-Back",
                                     "⚡ Library — ESP",
                                     "💥 Library — Stimulation",
                                     "⚠️ Library — HSE & Waste",
                                     "📁 Library — Other"])
        self.section_combo.currentIndexChanged.connect(self._reload_list)
        ll.addWidget(self.section_combo)

        self.program_list = QListWidget()
        self.program_list.currentItemChanged.connect(self._on_select)
        ll.addWidget(self.program_list, 1)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color:#8a8a9a;font-size:11px;")
        ll.addWidget(self.lbl_count)
        splitter.addWidget(left)

        # Right: content browser + search
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        self.doc_title = QLabel("")
        self.doc_title.setStyleSheet(
            "color:#e94560;font-size:14px;font-weight:bold;")
        top_row.addWidget(self.doc_title, 1)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search in document...")
        self.search_box.setMaximumWidth(240)
        self.search_box.returnPressed.connect(self._search_next)
        top_row.addWidget(self.search_box)

        btn_next = QPushButton("▼")
        btn_next.setMaximumWidth(34)
        btn_next.clicked.connect(self._search_next)
        top_row.addWidget(btn_next)
        rl.addLayout(top_row)

        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.anchorClicked.connect(self._on_anchor)
        rl.addWidget(self.browser, 1)
        splitter.addWidget(right)

        splitter.setSizes([340, 900])
        outer.addWidget(splitter, 1)

        self._files: dict = {}
        self._categories: dict = {}
        self._load_catalog()
        self._reload_list()

    # -- catalog -----------------------------------------------------------
    def _load_catalog(self):
        """Build the catalog: master docs + library files with categories."""
        self._files = {}
        self._categories = {}
        if self.programs_dir.exists():
            for f in sorted(self.programs_dir.glob("*.md")):
                self._files[f.stem] = (f, "Master")
            for f in sorted(self.library_dir.glob("*.txt")):
                if f.name == "INDEX.md" or f.stem == "INDEX":
                    continue
                stem = f.stem
                # extract category from INDEX if possible
                cat = self._category_for(stem)
                self._files[stem] = (f, cat)

    def _category_for(self, stem: str) -> str:
        name = stem.lower()
        if 'casing running' in name or ('csg' in name and 'cement' in name):
            return 'Casing & Cementing'
        if 'cement' in name or 'cmt' in name or 'سیمان' in name:
            return 'Cementing & Plugs'
        if 'drilling program' in name or 'drilling programme' in name:
            return 'Drilling Programs'
        if 'workover' in name:
            return 'Workover Programs'
        if 'drilling procedure' in name or 'drilling instruction' in name or \
                'hole section' in name or 'حفاری' in name:
            return 'Drilling Procedures'
        if 'kill' in name or 'control procedure' in name or 'well control' in name:
            return 'Well Control'
        if 'whipstock' in name or 'side track' in name or 'sidetrack' in name:
            return 'Sidetrack / Whipstock'
        if 'backoff' in name or 'colliding' in name or 'fishing' in name:
            return 'Fishing / Backoff'
        if 'test' in name or 'dry test' in name or 'lot' in name:
            return 'Testing (LOT/DST/Dry)'
        if 'esp' in name:
            return 'ESP'
        if 'acid' in name or 'stimul' in name:
            return 'Stimulation'
        if 'liner' in name or 'tie-back' in name:
            return 'Liner & Tie-Back'
        if 'waste' in name or 'management plan' in name:
            return 'HSE & Waste'
        return 'Other'

    def _current_section(self) -> str:
        text = self.section_combo.currentText()
        if "All" in text:
            return "All"
        if "Master" in text:
            return "Master"
        if "— " in text:
            return text.split("— ")[1].strip()
        return "All"

    def _reload_list(self):
        self.program_list.clear()
        section = self._current_section()
        items = []
        for stem, (path, cat) in self._files.items():
            if section == "All":
                ok = True
            elif section == "Master":
                ok = (cat == "Master")
            else:
                ok = (cat == section)
            if ok:
                size_kb = path.stat().st_size // 1024
                icon = "📘" if cat == "Master" else "📄"
                items.append((stem, icon, cat, size_kb))
        items.sort(key=lambda x: x[0].lower())
        for stem, icon, cat, size_kb in items:
            item = QListWidgetItem(f"{icon}  {stem.replace('_', ' ')}")
            item.setToolTip(f"{cat}  •  {size_kb:,} KB")
            item.setData(Qt.UserRole, stem)
            self.program_list.addItem(item)
        self.lbl_count.setText(f"{len(items)} documents")
        if self.program_list.count():
            self.program_list.setCurrentRow(0)

    def _on_select(self, current, _previous):
        if current is None:
            return
        stem = current.data(Qt.UserRole)
        entry = self._files.get(stem)
        if entry is None:
            return
        path, cat = entry
        if path.exists():
            md_text = path.read_text(encoding="utf-8", errors="replace")
            size_kb = path.stat().st_size // 1024
            self.doc_title.setText(
                f"{'📘' if cat == 'Master' else '📄'}  "
                f"{path.stem.replace('_', ' ')}   "
                f"<span style='color:#8a8a9a;font-size:11px;'>"
                f"{cat} • {size_kb:,} KB • {len(md_text):,} chars</span>")
            self.browser.setHtml(render_document(md_text))
            self.browser.verticalScrollBar().setValue(0)

    # -- search ------------------------------------------------------------
    def _search_next(self):
        term = self.search_box.text()
        if not term:
            return
        found = self.browser.find(term)
        if not found:
            self.browser.moveCursor(QTextCursor.Start)
            found = self.browser.find(term)
            if not found:
                self.doc_title.setText(f"🔍 No match for: {term}")

    def _on_anchor(self, url: QUrl):
        target = url.toString()
        if target.startswith("#"):
            self.browser.scrollToAnchor(target[1:])
        elif target.startswith("http"):
            QDesktopServices.openUrl(url)


# ----------------------------------------------------------------------------
# ENGINEERING TOOLS TAB
# ----------------------------------------------------------------------------

class _ToolPage(QWidget):
    """Base page: form fields + Calculate button + result browser."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        t = QLabel(title)
        t.setStyleSheet("color:#e94560;font-size:14px;font-weight:bold;")
        lay.addWidget(t)

        self.form = QFormLayout()
        self.form.setSpacing(8)
        lay.addLayout(self.form)

        self.btn = QPushButton("🧮  Calculate")
        self.btn.clicked.connect(self.calculate)
        lay.addWidget(self.btn)

        self.results = QTextBrowser()
        self.results.setMinimumHeight(160)
        lay.addWidget(self.results, 1)

    # -- helpers ----------------------------------------------------------
    def add_line(self, label: str, placeholder: str = ""):
        w = QLineEdit()
        w.setPlaceholderText(placeholder)
        self.form.addRow(label, w)
        return w

    def add_spin(self, label: str, max_val: float = 1e9, decimals: int = 2,
                 suffix: str = ""):
        w = QDoubleSpinBox()
        w.setRange(0, max_val)
        w.setDecimals(decimals)
        w.setValue(0)
        if suffix:
            w.setSuffix(f" {suffix}")
        self.form.addRow(label, w)
        return w

    def add_combo(self, label: str, items: List[str]):
        w = QComboBox()
        w.addItems(items)
        self.form.addRow(label, w)
        return w

    def show_result(self, text: str):
        self.results.setHtml(
            f"<html><body style='font-family:Consolas,monospace;font-size:12px;"
            f"color:#d5d5e0;'>{text}</body></html>")

    def calculate(self):  # pragma: no cover - overridden
        self.show_result("Not implemented.")


class UnitConverterPage(_ToolPage):
    def __init__(self, parent=None):
        super().__init__("⚖️  Unit Converter", parent)
        self.value = self.add_spin("Value:", 1e12, 4)
        self.from_unit = self.add_combo("From:", [])
        self.to_unit = self.add_combo("To:", [])
        self.category = self.add_combo("Category:", [
            "Length", "Pressure", "Volume", "Mud Weight", "Temperature",
            "Force", "Torque", "Flow Rate", "Mass per Length", "Dimension"])
        self.category.currentIndexChanged.connect(self._update_units)
        self._update_units()

    _UNITS = {
        "Length": [("ft", "ft_to_m", "m"), ("m", "m_to_ft", "ft")],
        "Pressure": [("psi", "psi_to_kpa", "kPa"), ("kPa", "kpa_to_psi", "psi")],
        "Volume": [("bbl", "bbl_to_m3", "m³"), ("m³", "m3_to_bbl", "bbl")],
        "Mud Weight": [("ppg", "ppg_to_sg", "SG"), ("SG", "sg_to_ppg", "ppg"),
                       ("ppg", "ppg_to_psi_per_ft", "psi/ft")],
        "Temperature": [("°F", "fahrenheit_to_celsius", "°C"),
                        ("°C", "celsius_to_fahrenheit", "°F")],
        "Force": [("lbf", "lbf_to_kn", "kN"), ("kN", "lbf_to_kn", "lbf")],
        "Torque": [("ft-lbs", "ftlbs_to_nm", "N·m"), ("N·m", "ftlbs_to_nm", "ft-lbs")],
        "Flow Rate": [("GPM", "gpm_to_lpm", "LPM"), ("LPM", "gpm_to_lpm", "GPM")],
        "Mass per Length": [("ppf", "ppf_to_kg_per_m", "kg/m"),
                            ("kg/m", "ppf_to_kg_per_m", "ppf")],
        "Dimension": [("inch", "inches_to_mm", "mm"), ("mm", "inches_to_mm", "inch")],
    }

    def _update_units(self):
        cat = self.category.currentText()
        units = self._UNITS.get(cat, [])
        names = [u[0] for u in units]
        self.from_unit.clear()
        self.from_unit.addItems(names)
        self.to_unit.clear()
        self.to_unit.addItems(names)
        if len(names) > 1:
            self.to_unit.setCurrentIndex(1)

    def calculate(self):
        try:
            from engineering_calculations import UnitConverter as UC
        except ImportError:
            self.show_result("engineering_calculations module not available.")
            return
        cat = self.category.currentText()
        units = self._UNITS.get(cat, [])
        if not units:
            return
        idx = self.from_unit.currentIndex()
        if idx >= len(units):
            return
        method = units[idx][1]
        func = getattr(UC, method, None)
        if func is None:
            self.show_result(f"Converter <b>{method}</b> not found.")
            return
        val = self.value.value()
        try:
            result = func(val)
            self.show_result(
                f"<p><b>Result:</b> {val:,.4f} "
                f"{self.from_unit.currentText()}  =  "
                f"<span style='color:#4fc3f7;font-size:16px;'>"
                f"{result:,.4f}</span> {self.to_unit.currentText()}</p>")
        except Exception as e:
            self.show_result(f"Error: {e}")


class HydraulicsPage(_ToolPage):
    def __init__(self, parent=None):
        super().__init__("💧  Hydraulics (API RP 13D)", parent)
        self.flow = self.add_spin("Flow Rate (GPM):", 5000, 1)
        self.hole_id = self.add_spin("Hole / Casing ID (in):", 60, 3)
        self.pipe_od = self.add_spin("Drill Pipe OD (in):", 30, 3)
        self.mw = self.add_spin("Mud Weight (ppg):", 25, 2)
        self.pv = self.add_spin("Plastic Viscosity (cP):", 200, 1)
        self.tfa = self.add_spin("Bit TFA (sq.in):", 5, 4)
        self.annular_loss = self.add_spin("Annular Pressure Loss (psi):", 5000, 1)
        self.depth = self.add_spin("Depth (ft):", 50000, 0)

    def calculate(self):
        try:
            from engineering_calculations import HydraulicsCalculator as HC
        except ImportError:
            self.show_result("Module not available.")
            return
        hc = HC()
        try:
            ann_vel = hc.annular_velocity(
                self.flow.value(), self.hole_id.value(), self.pipe_od.value())
            pipe_vel = hc.pipe_velocity(self.flow.value(), self.pipe_od.value() - 0.5)
            bit_drop = hc.bit_pressure_drop(
                self.flow.value(), self.mw.value(), self.tfa.value())
            hhp = hc.hydraulic_horsepower(
                self.flow.value(), bit_drop) if bit_drop else 0
            hsi = hc.hsi(self.flow.value(), bit_drop, self.tfa.value()) \
                if bit_drop and self.tfa.value() else 0
            ecd = hc.ecd(self.mw.value(), self.annular_loss.value(),
                         self.depth.value())
            reynolds = hc.reynolds_number_annular(
                self.mw.value(), ann_vel, self.pv.value(),
                self.hole_id.value(), self.pipe_od.value())
            self.show_result(
                f"<b>Annular Velocity:</b> {ann_vel:,.1f} ft/min<br>"
                f"<b>Pipe Velocity:</b> {pipe_vel:,.1f} ft/min<br>"
                f"<b>Bit Pressure Drop:</b> {bit_drop:,.0f} psi<br>"
                f"<b>Hydraulic HHP:</b> {hhp:,.0f} HP<br>"
                f"<b>HSI:</b> {hsi:,.2f} HP/sq.in<br>"
                f"<b>ECD:</b> {ecd:,.2f} ppg<br>"
                f"<b>Annular Reynolds:</b> {reynolds:,.0f}")
        except Exception as e:
            self.show_result(f"<span style='color:#ff6b6b;'>Error: {e}</span>")


class CasingCheckPage(_ToolPage):
    def __init__(self, parent=None):
        super().__init__("🔩  Casing Design Verification (API RP 5C3)", parent)
        self.od = self.add_spin("Casing OD (in):", 40, 3)
        self.id = self.add_spin("Casing ID (in):", 40, 3)
        self.wt = self.add_spin("Weight (ppf):", 300, 2)
        self.grade = self.add_combo("Grade:", [
            "H-40", "J-55", "K-55", "N-80", "L-80", "C-90", "C-95",
            "T-95", "P-110", "Q-125", "V-150"])
        self.depth = self.add_spin("Setting Depth TVD (ft):", 50000, 0)
        self.mw = self.add_spin("Mud Weight (ppg):", 25, 2)
        self.pore = self.add_spin("Pore Pressure (psi):", 30000, 0)
        self.frac = self.add_spin("Frac Gradient (ppg):", 25, 2)

    def calculate(self):
        try:
            from engineering_calculations import CasingDesignCalculator as CDC
        except ImportError:
            self.show_result("Module not available.")
            return
        grade_map = {
            "H-40": 40000, "J-55": 55000, "K-55": 55000, "N-80": 80000,
            "L-80": 80000, "C-90": 90000, "C-95": 95000, "T-95": 95000,
            "P-110": 110000, "Q-125": 125000, "V-150": 150000}
        try:
            cdc = CDC()
            res = cdc.calculate_casing_design_summary(
                od=self.od.value(), id_inner=self.id.value(),
                weight_ppf=self.wt.value(),
                grade_yield_psi=grade_map.get(self.grade.currentText(), 80000),
                setting_depth_tvd=self.depth.value(),
                mud_weight=self.mw.value(), pore_pressure=self.pore.value(),
                fracture_gradient=self.frac.value())
            if isinstance(res, dict):
                lines = [f"<b>{k.replace('_', ' ').title()}:</b> "
                         f"{v if not isinstance(v, float) else f'{v:,.2f}'}<br>"
                         for k, v in res.items()]
                self.show_result("".join(lines))
            else:
                self.show_result(str(res))
        except Exception as e:
            self.show_result(f"<span style='color:#ff6b6b;'>Error: {e}</span>")


class CementPage(_ToolPage):
    def __init__(self, parent=None):
        super().__init__("🏗️  Cement Job Quick Calculation", parent)
        self.hole = self.add_spin("Hole Size (in):", 40, 3)
        self.casing_od = self.add_spin("Casing OD (in):", 40, 3)
        self.casing_id = self.add_spin("Casing ID (in):", 40, 3)
        self.shoe = self.add_spin("Shoe Depth MD (ft):", 50000, 0)
        self.toc = self.add_spin("TOC MD (ft):", 50000, 0)
        self.excess = self.add_spin("Excess (%):", 300, 0, "%")
        self.lead_den = self.add_spin("Lead Density (ppg):", 20, 2)
        self.tail_den = self.add_spin("Tail Density (ppg):", 25, 2)

    def calculate(self):
        try:
            from engineering_calculations import CementCalculator as CC
        except ImportError:
            self.show_result("Module not available.")
            return
        try:
            cc = CC()
            # Annular volume (open hole section)
            ann_bbl_ft = (self.hole.value() ** 2 - self.casing_od.value() ** 2) / 1029.4
            ann_vol = ann_bbl_ft * (self.shoe.value() - self.toc.value())
            ann_vol *= (1 + self.excess.value() / 100.0)
            # Casing displacement volume
            disp_vol = (self.casing_id.value() ** 2 / 1029.4) * self.shoe.value()
            self.show_result(
                f"<b>Annular Capacity:</b> {ann_bbl_ft:,.4f} bbl/ft<br>"
                f"<b>Annular Volume (with {self.excess.value():.0f}% excess):</b> "
                f"{ann_vol:,.0f} bbl<br>"
                f"<b>Casing Displacement Volume:</b> {disp_vol:,.0f} bbl<br>"
                f"<b>Total Job Volume (approx.):</b> {ann_vol + disp_vol:,.0f} bbl<br>"
                f"<i>Use the full module for lead/tail split, thickening "
                f"time and ECD checks.</i>")
        except Exception as e:
            self.show_result(f"<span style='color:#ff6b6b;'>Error: {e}</span>")


class WellControlPage(_ToolPage):
    def __init__(self, parent=None):
        super().__init__("🔴  Well Control — MAASP & Kick Tolerance", parent)
        self.frac = self.add_spin("Frac Gradient at Shoe (ppg):", 25, 2)
        self.mw = self.add_spin("Current Mud Weight (ppg):", 25, 2)
        self.shoe_tvd = self.add_spin("Shoe TVD (ft):", 50000, 0)
        self.td_tvd = self.add_spin("TD TVD (ft):", 50000, 0)
        self.hole = self.add_spin("Hole Size (in):", 40, 3)
        self.pipe = self.add_spin("Drill Pipe OD (in):", 20, 3)

    def calculate(self):
        try:
            from engineering_calculations import WellControlCalculator as WCC
        except ImportError:
            self.show_result("Module not available.")
            return
        try:
            wcc = WCC()
            maasp = wcc.maasp(self.frac.value(), self.mw.value(),
                              self.shoe_tvd.value())
            kt = wcc.kick_tolerance(
                self.frac.value(), self.mw.value(), self.shoe_tvd.value(),
                self.td_tvd.value(), self.hole.value(), self.pipe.value())
            self.show_result(
                f"<b>MAASP:</b> {maasp:,.0f} psi<br>"
                f"<b>Kick Tolerance:</b> {kt:,.1f} bbl")
        except Exception as e:
            self.show_result(f"<span style='color:#ff6b6b;'>Error: {e}</span>")


class TorqueDragPage(_ToolPage):
    def __init__(self, parent=None):
        super().__init__("⚙️  Torque & Drag Quick Checks", parent)
        self.mw = self.add_spin("Mud Weight (ppg):", 25, 2)
        self.air_wt = self.add_spin("Air Weight (ppf):", 200, 2)
        self.length = self.add_spin("Length (ft):", 50000, 0)
        self.normal = self.add_spin("Normal Force (lbs):", 2e6, 0)
        self.friction = self.add_spin("Friction Coefficient:", 1, 3)

    def calculate(self):
        try:
            from engineering_calculations import TorqueDragCalculator as TDC
        except ImportError:
            self.show_result("Module not available.")
            return
        try:
            tdc = TDC()
            bf = tdc.buoyancy_factor(self.mw.value())
            eff = tdc.effective_weight(self.air_wt.value(), self.length.value(),
                                       bf)
            drag = tdc.drag_force(self.normal.value(), self.friction.value())
            self.show_result(
                f"<b>Buoyancy Factor:</b> {bf:,.3f}<br>"
                f"<b>Effective String Weight:</b> {eff:,.0f} lbs<br>"
                f"<b>Estimated Drag Force:</b> {drag:,.0f} lbs")
        except Exception as e:
            self.show_result(f"<span style='color:#ff6b6b;'>Error: {e}</span>")


class EngineeringToolsTab(QWidget):
    """Tab with a sidebar of quick engineering calculators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Horizontal)

        self.nav = QListWidget()
        self.nav.setMaximumWidth(230)
        self.nav.setMinimumWidth(200)
        tools = [
            ("⚖️  Unit Converter", UnitConverterPage),
            ("💧  Hydraulics", HydraulicsPage),
            ("🔩  Casing Verification", CasingCheckPage),
            ("🏗️  Cement Quick Calc", CementPage),
            ("🔴  Well Control", WellControlPage),
            ("⚙️  Torque & Drag", TorqueDragPage),
        ]
        self.pages = QStackedWidget()
        for name, cls in tools:
            self.nav.addItem(name)
            self.pages.addWidget(cls())

        self.nav.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.nav.setCurrentRow(0)

        splitter.addWidget(self.nav)
        splitter.addWidget(self.pages)
        splitter.setSizes([230, 900])
        lay.addWidget(splitter)


# ----------------------------------------------------------------------------
# DOCUMENT PREVIEW DIALOG
# ----------------------------------------------------------------------------

class DocumentPreviewDialog(QDialog):
    """Shows a live text preview of the generated drilling program."""

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setWindowTitle("👁️  Drilling Program — Preview")
        self.resize(1000, 760)
        self.setStyleSheet(
            "QDialog { background-color: #16213e; }"
            "QLabel { color: #e0e0e0; }")

        lay = QVBoxLayout(self)

        title = QLabel("📄  DRILLING PROGRAM PREVIEW")
        title.setStyleSheet(
            "color:#e94560;font-size:16px;font-weight:bold;padding:6px;")
        lay.addWidget(title)

        self.browser = QTextBrowser()
        lay.addWidget(self.browser, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        lay.addLayout(btn_row)

        self._render(project)

    def _render(self, project):
        ci = project.company_info
        wi = project.well_info

        def row(label, value):
            if value in (None, "", 0, "0"):
                return ""
            return f"<tr><td style='padding:3px 10px;color:#9fb8d9;'>" \
                   f"{label}</td><td style='padding:3px 10px;'>" \
                   f"{value}</td></tr>"

        rows = []
        rows.append(row("Operator", ci.operator_name))
        rows.append(row("Contractor", ci.contractor_name))
        rows.append(row("Field", ci.field_name))
        rows.append(row("Well", f"{ci.well_name} {ci.well_number}"))
        rows.append(row("Rig", ci.rig_name))
        rows.append(row("Document No.", ci.document_number))
        rows.append(row("Revision", ci.revision))
        rows.append(row("Prepared By", ci.prepared_by))
        rows.append(row("Reviewed By", ci.reviewed_by))
        rows.append(row("Approved By", ci.approved_by))
        rows.append(row("Well Type", wi.well_type))
        rows.append(row("Well Profile", wi.well_profile))
        rows.append(row("Total Depth MD", f"{wi.total_depth_md:,.0f} ft"))
        rows.append(row("Total Depth TVD", f"{wi.total_depth_tvd:,.0f} ft"))
        rows.append(row("Target Formation", wi.target_formation))
        rows.append(row("H₂S", f"{wi.expected_h2s_concentration}%"))
        rows.append(row("CO₂", f"{wi.expected_co2_concentration}%"))

        sections = []
        for cd in project.casing_design:
            sections.append(
                f"{cd.section_name} ({cd.hole_size:.1f}\" → {cd.casing_od:.3f}\" "
                f"{cd.casing_grade} {cd.casing_connection}, "
                f"set at {cd.setting_depth_md:,.0f} ft)")
        muds = [f"{m.section_name}: {m.mud_type} @ {m.mud_weight_out:.1f} ppg"
                for m in project.mud_programs]
        bhas = [f"{b.section_name}: {b.bit_type} {b.bit_size:.1f}\" {b.bha_type}"
                for b in project.bha_designs]
        times = [f"{t.section_name}: {t.operation} — {t.total_section_days:.1f} d"
                 for t in project.time_estimates]

        def bullet(items):
            return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

        html_doc = f"""<html><body style="font-family:'Segoe UI',Arial;font-size:13px;
        color:#e0e0e0;padding:10px;">
        <h2 style="color:#e94560;text-align:center;">DRILLING PROGRAM</h2>
        <h3 style="color:#e94560;text-align:center;">{ci.well_name or '—'} — {ci.field_name or ''}</h3>
        <table style="border-collapse:collapse;width:100%;">{''.join(rows)}</table>
        <h3 style="color:#e94560;">Casing Program</h3>{bullet(sections)}
        <h3 style="color:#e94560;">Mud Program</h3>{bullet(muds)}
        <h3 style="color:#e94560;">BHA Plan</h3>{bullet(bhas)}
        <h3 style="color:#e94560;">Time Estimate (AFE)</h3>{bullet(times)}
        <p style="color:#8a8a9a;margin-top:16px;">
        Full document is generated in Microsoft Word format with all sections,
        tables and appendices — use <b>Generate Word Document</b>.</p>
        </body></html>"""
        self.browser.setHtml(html_doc)
