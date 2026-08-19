# ============================================================================
# FINE-GRAINED DOCUMENT COMPOSITION
# File: wizard_compose.py
# Phase AK — the user drives the document at a much finer granularity:
#   For a drilling program:
#     which HOLE SECTIONS?  (size / depth / casing per section)
#       -> include drilling procedure? casing-running? cementing?
#          checklist?  (each pulled from the classified procedures DB)
#   Which PROCEDURES from the 16 classified categories to embed?
#   For a COMPLETION: which TYPE? which TOOLS (packer/TRSV/SSD/ESP/...)?
#     include the completion procedure?
#   Which KNOWLEDGE documents (catalog, 754 docs, 19 operations) to
#     include as selected enrichment?
#
# The composition is a data object + a deterministic renderer; the wizard
# collects it through CompositionDialog and appends compose_markdown() to
# the generated document.
# ============================================================================

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

APP_DIR = Path.home() / ".drilling_program"

COMPLETION_TYPES = [
    "Single (3.5 in)",
    "Dual (4.5 + 2.875 in)",
    "ESP",
    "Coiled Tubing",
    "Cased-hole plug & perf",
    "Open-hole multi-stage",
]
COMPLETION_TOOLS = [
    "Production packer", "TRSV", "SSD", "Gas lift mandrels",
    "ESP assembly", "Nipple profile", "SCSSV control line",
    "Permanent gauge", "Circulating device", "Tubing hanger",
]


@dataclass
class HoleSectionComp:
    size_in: str = "12.25"
    depth_m: str = "3000"
    casing_in: str = "9.625"
    include_drilling: bool = True
    include_casing: bool = True
    include_cementing: bool = True
    include_checklist: bool = True


@dataclass
class CompletionComp:
    completion_type: str = "Single (3.5 in)"
    tools: List[str] = field(default_factory=list)
    include_procedures: bool = True


@dataclass
class Composition:
    hole_sections: List[HoleSectionComp] = field(default_factory=list)
    procedure_ids: List[int] = field(default_factory=list)
    completion: Optional[CompletionComp] = None
    knowledge_ids: List[int] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Data access helpers (classified databases)
# ---------------------------------------------------------------------------

def procedures_by_category() -> List[Dict]:
    """All active procedures grouped by their classified category."""
    import sqlite3
    con = sqlite3.connect(str(APP_DIR / "procedures.db"))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT p.id, p.name, p.description, c.name AS category "
        "FROM procedures p LEFT JOIN categories c ON p.category_id=c.id "
        "WHERE p.is_active=1 ORDER BY c.name, p.name").fetchall()
    con.close()
    return [dict(r) for r in rows]


def procedure_ids_for_category(category: str) -> List[int]:
    import sqlite3
    con = sqlite3.connect(str(APP_DIR / "procedures.db"))
    rows = con.execute(
        "SELECT p.id FROM procedures p LEFT JOIN categories c "
        "ON p.category_id=c.id WHERE c.name=? AND p.is_active=1 "
        "ORDER BY p.name", (category,)).fetchall()
    con.close()
    return [r[0] for r in rows]


def catalog_by_operation() -> List[Dict]:
    """Catalog documents grouped by operation (19 classified ops)."""
    import sqlite3
    con = sqlite3.connect(str(APP_DIR / "catalog.db"))
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT id, num, title, operation, category FROM docs "
        "ORDER BY operation, num").fetchall()
    con.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Renderer — deterministic markdown from a Composition
# ---------------------------------------------------------------------------

def _load_procedure(pid: int) -> Optional[Dict]:
    try:
        from procedures_db import ProcedureDatabase
        db = ProcedureDatabase()
        rec = db.get_procedure(pid)
        if not rec:
            db.close()
            return None
        out = {"name": rec.name, "steps": [s.text for s in rec.steps],
               "checklist": [c.text for c in rec.checklist]}
        db.close()
        return out
    except Exception:
        return None


def _subst_text(t: str, vals: Dict) -> str:
    """Substitute {{x}}/{x} with values (unresolved stay visible)."""
    from wizard_engine import PLACEHOLDER_RE

    def _repl(m):
        key = m.group(1) or m.group(2)
        if key in vals and str(vals[key]).strip():
            return str(vals[key])
        return m.group(0)
    return PLACEHOLDER_RE.sub(_repl, t or "")


def compose_markdown(comp: Composition, values: Dict,
                     operator: str = "") -> str:
    """Render the composition to document markdown (Word-ready)."""
    if not comp:
        return ""
    op = (operator or "").strip() or "the Operator"
    L: List[str] = []
    vals = values or {}

    # ---- 1. Hole sections with per-section procedures ----
    if comp.hole_sections:
        L.append("## FINE-GRAINED HOLE SECTIONS")
        L.append("")
        L.append(f"Selected for {op} — each section with its own "
                 "procedures:")
        L.append("")
        for i, hs in enumerate(comp.hole_sections, 1):
            L.append(f"### Hole Section {i} — {hs.size_in} in hole")
            L.append("")
            L.append("| Parameter | Value |")
            L.append("|---|---|")
            L.append(f"| Hole size | {hs.size_in} in |")
            L.append(f"| Depth | {hs.depth_m} m |")
            L.append(f"| Casing | {hs.casing_in} in |")
            L.append("")
            # per-section procedures
            sub = []
            if hs.include_drilling:
                sub.append(("Drilling procedure", "Drilling Operations"))
            if hs.include_casing:
                sub.append(("Casing running", "Casing & Liner"))
            if hs.include_cementing:
                sub.append(("Cementing", "Cementing"))
            for label, cat in sub:
                ids = procedure_ids_for_category(cat)
                # pick the first matching procedure (best-effort per
                # section size is impossible without a mapping; the user
                # picks specific procedures in tab 2 for full control)
                if ids:
                    proc = _load_procedure(ids[0])
                    if proc:
                        L.append(f"**{label} — {proc['name']}:**")
                        L.append("")
                        for s in proc["steps"][:12]:
                            t = _subst_text(s, vals)
                            if t.strip():
                                L.append(f"- {t}")
                        L.append("")
            if hs.include_checklist:
                L.append(f"**Checklist ({hs.size_in} in section):**")
                L.append("")
                L.append("- [ ] Hole and BHA condition verified")
                L.append("- [ ] Equipment tested and ready")
                L.append("- [ ] Personnel briefed (pre-job meeting)")
                L.append("- [ ] Mud properties per program")
                L.append("- [ ] Well-control equipment checked")
                L.append("")
        L.append("")

    # ---- 2. Explicitly selected procedures ----
    if comp.procedure_ids:
        L.append("## SELECTED PROCEDURES")
        L.append("")
        L.append("The procedures below were explicitly selected by the "
                 "user for this document:")
        L.append("")
        for pid in comp.procedure_ids:
            proc = _load_procedure(pid)
            if not proc:
                continue
            L.append(f"### {proc['name']}")
            L.append("")
            for s in proc["steps"]:
                t = _subst_text(s, vals)
                if t.strip():
                    L.append(f"- {t}")
            if proc["checklist"]:
                L.append("")
                L.append("**Checklist:**")
                L.append("")
                for c in proc["checklist"][:10]:
                    L.append(f"- [ ] {c}")
            L.append("")
        L.append("")

    # ---- 3. Completion design ----
    if comp.completion:
        c = comp.completion
        L.append("## COMPLETION DESIGN")
        L.append("")
        L.append(f"**Type:** {c.completion_type}")
        L.append("")
        if c.tools:
            L.append("**Downhole tools:**")
            L.append("")
            for t in c.tools:
                L.append(f"- {t}")
            L.append("")
        if c.include_procedures:
            ids = procedure_ids_for_category("Completion")
            if ids:
                proc = _load_procedure(ids[0])
                if proc:
                    L.append(f"**Completion procedure — {proc['name']}:**")
                    L.append("")
                    for s in proc["steps"][:15]:
                        t = _subst_text(s, vals)
                        if t.strip():
                            L.append(f"- {t}")
                    L.append("")
        L.append("")

    # ---- 4. Selected knowledge documents ----
    if comp.knowledge_ids:
        L.append("## SELECTED KNOWLEDGE DOCUMENTS")
        L.append("")
        L.append("The following library documents were selected by the "
                 "user (verbatim excerpts; company/well names removed):")
        L.append("")
        import sqlite3
        con = sqlite3.connect(str(APP_DIR / "catalog.db"))
        con.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in comp.knowledge_ids)
        rows = con.execute(
            f"SELECT num, title, operation FROM docs WHERE id IN "
            f"({placeholders}) ORDER BY num",
            comp.knowledge_ids).fetchall()
        con.close()
        for r in rows:
            L.append(f"- **#{r['num']}** {r['title']} "
                     f"({r['operation'] or 'General'})")
        L.append("")
        L.append(f"*Knowledge documents selected for {op}; full texts are "
                 "available in the internal library (programs/library).*")
        L.append("")

    return "\n".join(L)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def _selftest():
    comp = Composition(
        hole_sections=[
            HoleSectionComp(size_in="17.5", depth_m="500",
                            casing_in="13.375",
                            include_drilling=True, include_casing=True,
                            include_cementing=False, include_checklist=True),
            HoleSectionComp(size_in="12.25", depth_m="3000",
                            casing_in="9.625"),
        ],
        procedure_ids=procedure_ids_for_category("Well Control")[:2],
        completion=CompletionComp(completion_type="ESP",
                                  tools=["Production packer", "ESP assembly",
                                         "TRSV"]),
        knowledge_ids=[],
    )
    md = compose_markdown(comp, {"well_name": "Well A"}, "the Operator")
    assert "FINE-GRAINED HOLE SECTIONS" in md
    assert "Hole Section 1 — 17.5 in hole" in md
    assert "Hole Section 2 — 12.25 in hole" in md
    assert "SELECTED PROCEDURES" in md
    assert "COMPLETION DESIGN" in md
    assert "ESP" in md and "ESP assembly" in md
    assert "Checklist" in md
    # placeholder substitution inside embedded procedures
    md2 = compose_markdown(comp, {"well_name": "Well B"},
                           "the Operator")
    assert "{{well_name}}" not in md2
    # empty composition -> empty
    assert compose_markdown(Composition(), {}, "") == ""
    print("  ✔ compose selftest: hole sections + procedures + completion OK")
    return md


if __name__ == "__main__":
    _selftest()
    print("wizard_compose OK")


# ---------------------------------------------------------------------------
# COMPOSITION DIALOG — fine-grained user-driven document composition
# ---------------------------------------------------------------------------

class CompositionDialog:
    """Qt dialog with four fine-grained tabs.  Kept as a thin wrapper so
    the module stays importable headless (the dialog class is defined
    lazily and only instantiates under a Qt event loop)."""

    @staticmethod
    def get_composition(parent=None) -> Optional[Composition]:
        try:
            from PySide6.QtWidgets import (QDialog, QVBoxLayout, QTabWidget,
                                           QWidget, QFormLayout, QLabel,
                                           QComboBox, QLineEdit, QCheckBox,
                                           QPushButton, QHBoxLayout,
                                           QListWidget, QListWidgetItem,
                                           QTableWidget, QTableWidgetItem,
                                           QHeaderView, QGroupBox,
                                           QMessageBox, QAbstractItemView)
            from PySide6.QtCore import Qt
        except Exception:
            return None

        dlg = QDialog(parent)
        dlg.setWindowTitle("⚙️ Fine-Grained Document Composition")
        dlg.setMinimumSize(860, 620)
        lay = QVBoxLayout(dlg)
        head = QLabel(
            "Compose the document at a fine granularity — choose exactly "
            "which hole sections, procedures, completion tools and "
            "knowledge documents to include.")
        head.setWordWrap(True)
        lay.addWidget(head)
        tabs = QTabWidget()

        # ---- Tab 1: hole sections ----
        t1 = QWidget()
        t1l = QVBoxLayout(t1)
        t1t = QTableWidget(0, 7)
        t1t.setHorizontalHeaderLabels(
            ["Hole (in)", "Depth (m)", "Casing (in)", "Drill", "CSG run",
             "Cement", "Checklist"])
        t1t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        t1l.addWidget(t1t)
        b1 = QHBoxLayout()
        def _add_row():
            r = t1t.rowCount()
            t1t.insertRow(r)
            for c, v in enumerate(["12.25", "3000", "9.625", True, True,
                                   True, True]):
                if c < 3:
                    t1t.setItem(r, c, QTableWidgetItem(str(v)))
                else:
                    w = QCheckBox()
                    w.setChecked(bool(v))
                    t1t.setCellWidget(r, c, w)
        btn_add = QPushButton("➕ Add hole section")
        btn_add.clicked.connect(_add_row)
        btn_rm = QPushButton("➖ Remove")
        def _rm_row():
            rows = sorted({i.row() for i in t1t.selectedItems()},
                          reverse=True)
            for r in rows:
                t1t.removeRow(r)
        btn_rm.clicked.connect(_rm_row)
        b1.addWidget(btn_add)
        b1.addWidget(btn_rm)
        b1.addStretch(1)
        t1l.addLayout(b1)
        _add_row()
        tabs.addTab(t1, "🕳️ Hole Sections")

        # ---- Tab 2: procedures by category ----
        t2 = QWidget()
        t2l = QVBoxLayout(t2)
        t2l.addWidget(QLabel("Tick the procedures to embed in this "
                             "document (grouped by category):"))
        proc_list = QListWidget()
        proc_list.setSelectionMode(QAbstractItemView.NoSelection)
        cat_procs: Dict[str, List[QListWidgetItem]] = {}
        for p in procedures_by_category():
            item = QListWidgetItem(f"[{p['category'] or 'Uncategorized'}] "
                                   f"{p['name']}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, p["id"])
            cat_procs.setdefault(p["category"] or "Uncategorized", [])\
                .append(item)
            proc_list.addItem(item)
        t2l.addWidget(proc_list)
        tabs.addTab(t2, "📋 Procedures")

        # ---- Tab 3: completion ----
        t3 = QWidget()
        t3l = QFormLayout(t3)
        cmb_type = QComboBox()
        cmb_type.addItems(COMPLETION_TYPES)
        t3l.addRow("Completion type:", cmb_type)
        tools_widget = QWidget()
        tl = QVBoxLayout(tools_widget)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.addWidget(QLabel("Downhole tools:"))
        tool_checks = []
        for tool in COMPLETION_TOOLS:
            cb = QCheckBox(tool)
            tool_checks.append(cb)
            tl.addWidget(cb)
        t3l.addRow(tools_widget)
        chk_inc = QCheckBox("Include the completion procedure in the "
                            "output")
        chk_inc.setChecked(True)
        t3l.addRow(chk_inc)
        tabs.addTab(t3, "🛢️ Completion")

        # ---- Tab 4: knowledge documents ----
        t4 = QWidget()
        t4l = QVBoxLayout(t4)
        t4l.addWidget(QLabel("Select knowledge documents to include "
                             "(catalog, by operation):"))
        kn_list = QListWidget()
        kn_list.setSelectionMode(QAbstractItemView.NoSelection)
        for d in catalog_by_operation():
            item = QListWidgetItem(f"[{d['operation'] or 'General'}] "
                                   f"#{d['num']} {d['title']}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, d["id"])
            kn_list.addItem(item)
        t4l.addWidget(kn_list)
        tabs.addTab(t4, "📚 Knowledge")

        lay.addWidget(tabs, 1)

        btns = QHBoxLayout()
        btns.addStretch(1)
        b_ok = QPushButton("✅ Apply composition")
        b_cancel = QPushButton("Cancel")
        result = {"comp": None}

        def _apply():
            comp = Composition()
            # hole sections
            for r in range(t1t.rowCount()):
                def _cell(r, c):
                    it = t1t.item(r, c)
                    return it.text().strip() if it else ""
                try:
                    hs = HoleSectionComp(
                        size_in=_cell(r, 0) or "12.25",
                        depth_m=_cell(r, 1) or "3000",
                        casing_in=_cell(r, 2) or "9.625")
                except Exception:
                    continue
                hs.include_drilling = bool(
                    t1t.cellWidget(r, 3) and
                    t1t.cellWidget(r, 3).isChecked())
                hs.include_casing = bool(
                    t1t.cellWidget(r, 4) and
                    t1t.cellWidget(r, 4).isChecked())
                hs.include_cementing = bool(
                    t1t.cellWidget(r, 5) and
                    t1t.cellWidget(r, 5).isChecked())
                hs.include_checklist = bool(
                    t1t.cellWidget(r, 6) and
                    t1t.cellWidget(r, 6).isChecked())
                comp.hole_sections.append(hs)
            # procedures
            for i in range(proc_list.count()):
                it = proc_list.item(i)
                if it.checkState() == Qt.Checked:
                    comp.procedure_ids.append(it.data(Qt.UserRole))
            # completion
            comp.completion = CompletionComp(
                completion_type=cmb_type.currentText(),
                tools=[cb.text() for cb in tool_checks if cb.isChecked()],
                include_procedures=chk_inc.isChecked())
            # knowledge
            for i in range(kn_list.count()):
                it = kn_list.item(i)
                if it.checkState() == Qt.Checked:
                    comp.knowledge_ids.append(it.data(Qt.UserRole))
            result["comp"] = comp
            dlg.accept()

        b_ok.clicked.connect(_apply)
        b_cancel.clicked.connect(dlg.reject)
        btns.addWidget(b_cancel)
        btns.addWidget(b_ok)
        lay.addLayout(btns)

        dlg.exec()
        return result["comp"]


if __name__ == "__main__":
    import sys as _s
    if len(_s.argv) > 1 and _s.argv[1] == "--ui":
        from PySide6.QtWidgets import QApplication
        app = QApplication([])
        c = CompositionDialog.get_composition()
        print("composition:", c)
    else:
        _selftest()
        print("wizard_compose OK")
