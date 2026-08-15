# ============================================================================
# DRILLING PROBLEMS UI — search & select problems for the output document
# File: drilling_problems_ui.py
# Dialog: search the problems database, preview symptoms/causes/prevention/
# remedies, tick the relevant problems, and add them as a
# 'DRILLING PROBLEM PREVENTION & RESPONSE PLAN' section to the wizard output.
# ============================================================================

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QTextBrowser, QSplitter, QCheckBox,
    QComboBox, QDialogButtonBox, QMessageBox, QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from drilling_problems_db import ProblemDatabase, DrillingProblem, build_problems_markdown


class ProblemsDialog(QDialog):
    """جستجو و انتخاب مشکلات حفاری برای افزودن به سند خروجی"""

    def __init__(self, parent=None, db: ProblemDatabase = None):
        super().__init__(parent)
        self.setWindowTitle("🛟 Drilling Problems — Prevention & Response")
        self.setMinimumSize(980, 620)
        self.db = db or ProblemDatabase()
        self._all: list = self.db.all()
        self.selection: list = []

        lay = QVBoxLayout(self)

        tip = QLabel(
            "Search and tick the drilling problems relevant to this "
            "operation. Their symptoms, prevention measures and response "
            "procedures will be added to the document as a "
            "'Drilling Problem Prevention & Response Plan' section.")
        tip.setWordWrap(True)
        tip.setStyleSheet("color:#8a8a9a;")
        lay.addWidget(tip)

        # search row
        row = QHBoxLayout()
        row.addWidget(QLabel("Search:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText(
            "e.g. stuck pipe, lost circulation, kick, shale, fishing...")
        self.txt_search.textChanged.connect(self._reload)
        row.addWidget(self.txt_search, 1)

        row.addWidget(QLabel("Category:"))
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItem("All", "")
        for c in self.db.categories():
            self.cmb_cat.addItem(c, c)
        self.cmb_cat.currentIndexChanged.connect(self._reload)
        row.addWidget(self.cmb_cat)

        btn_all = QPushButton("✓ Select All")
        btn_all.clicked.connect(lambda: self._set_all(True))
        btn_none = QPushButton("✗ Clear")
        btn_none.clicked.connect(lambda: self._set_all(False))
        row.addWidget(btn_all)
        row.addWidget(btn_none)
        lay.addLayout(row)

        # splitter: list | detail
        sp = QSplitter(Qt.Horizontal)

        self.list_w = QListWidget()
        self.list_w.itemSelectionChanged.connect(self._show_detail)
        self.list_w.itemChanged.connect(self._on_check)
        sp.addWidget(self.list_w)

        self.detail = QTextBrowser()
        self.detail.setOpenExternalLinks(False)
        sp.addWidget(self.detail)

        sp.setSizes([430, 550])
        lay.addWidget(sp, 1)

        self.lbl_count = QLabel("")
        self.lbl_count.setStyleSheet("color:#8a8a9a;")
        lay.addWidget(self.lbl_count)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self._accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

        self._reload()

    # ------------------------------------------------------------------
    def _reload(self):
        q = self.txt_search.text().strip().lower()
        cat = self.cmb_cat.currentData() or ""
        self.list_w.blockSignals(True)
        self.list_w.clear()
        shown = 0
        for p in self._all:
            if cat and p.category != cat:
                continue
            if q:
                blob = " ".join([p.name, p.category] + p.symptoms +
                                p.causes + p.prevention + p.remedies).lower()
                if q not in blob:
                    continue
            item = QListWidgetItem(
                f"[{p.severity}] {p.code} — {p.name}")
            item.setData(Qt.UserRole, p.code)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            if p.severity == "Critical":
                item.setForeground(Qt.red)
            elif p.severity == "High":
                item.setForeground(Qt.yellow)
            self.list_w.addItem(item)
            shown += 1
        self.list_w.blockSignals(False)
        self.lbl_count.setText(
            f"{shown} problem(s) shown of {len(self._all)} in the database")
        if shown:
            self.list_w.setCurrentRow(0)

    def _set_all(self, on: bool):
        for i in range(self.list_w.count()):
            self.list_w.item(i).setCheckState(
                Qt.Checked if on else Qt.Unchecked)

    def _current_problem(self) -> DrillingProblem:
        it = self.list_w.currentItem()
        if not it:
            return None
        return self.db.by_code(it.data(Qt.UserRole))

    def _show_detail(self):
        p = self._current_problem()
        if not p:
            self.detail.setHtml("")
            return
        html = [f"<h2>{p.code} — {p.name}</h2>",
                f"<b>Category:</b> {p.category} &nbsp;|&nbsp; "
                f"<b>Risk:</b> {p.severity}", "<hr>"]
        for title, items in (("⚠️ Symptoms (warning signs)", p.symptoms),
                             ("🔍 Causes", p.causes),
                             ("🛡️ Prevention", p.prevention),
                             ("🛟 Response (in order)", p.remedies)):
            html.append(f"<h3>{title}</h3><ul>")
            html += [f"<li>{x}</li>" for x in items]
            html.append("</ul>")
        if p.related_procedures:
            html.append("<h3>📋 Related procedures</h3><ul>")
            html += [f"<li>{x}</li>" for x in p.related_procedures]
            html.append("</ul>")
        self.detail.setHtml("".join(html))

    def _on_check(self, item):
        pass  # selection read at accept

    def _accept(self):
        sel = []
        for i in range(self.list_w.count()):
            it = self.list_w.item(i)
            if it.checkState() == Qt.Checked:
                p = self.db.by_code(it.data(Qt.UserRole))
                if p:
                    sel.append(p)
        self.selection = sel
        self.accept()

    def selected_markdown(self, operator: str = "") -> str:
        return build_problems_markdown(self.selection, operator)
