# ============================================================================
# UI SMOKE TEST SUITE (offscreen)
# File: tests/test_ui_smoke.py
# Audit item (Testing): automated UI smoke — every tab instantiates, the
# wizard walks end-to-end and generates a real Word document with all
# governance sections.
#
# Run:  LD_LIBRARY_PATH=/tmp/glstubs PYTHONPATH=. QT_QPA_PLATFORM=offscreen \
#       python3 tests/test_ui_smoke.py
# Exit code 0 = all pass.
# ============================================================================

import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import (QApplication, QMessageBox, QLineEdit,
                               QComboBox, QDoubleSpinBox, QSpinBox,
                               QCheckBox, QTextEdit, QListWidgetItem)

# Auto-answer modal dialogs so the smoke run never blocks:
#   warning -> Yes (accept CRITICAL overrides), info -> Ok, critical -> Ok
QMessageBox.warning = staticmethod(
    lambda *a, **k: QMessageBox.StandardButton.Yes)
QMessageBox.information = staticmethod(
    lambda *a, **k: QMessageBox.StandardButton.Ok)
QMessageBox.critical = staticmethod(
    lambda *a, **k: QMessageBox.StandardButton.Ok)

_PASS = 0
_FAIL = 0


def ok(cond, label, extra=""):
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ✔ {label}")
    else:
        _FAIL += 1
        print(f"  ✘ {label} {extra}")


def test_main_window(app):
    print("\n[1] MAIN WINDOW — all tabs instantiate")
    from main import DrillingProgramMainWindow
    win = DrillingProgramMainWindow()
    app.processEvents()
    n = win.tabs.count()
    ok(n >= 14, f"tabs >= 14 (got {n})")
    for i in range(n):
        win.tabs.setCurrentIndex(i)
        app.processEvents()
    ok(True, f"switched through all {n} tabs")
    win.close()
    return win


def _fill_widget(widget, key, value_map):
    """Fill a wizard input widget with a generic value."""
    v = value_map.get(key)
    if isinstance(widget, QLineEdit):
        widget.setText(str(v if v is not None else "Generic"))
    elif isinstance(widget, QDoubleSpinBox):
        widget.setValue(float(v if v is not None else 100))
    elif isinstance(widget, QSpinBox):
        widget.setValue(int(v if v is not None else 100))
    elif isinstance(widget, QComboBox):
        if v is not None and v in [widget.itemText(i)
                                   for i in range(widget.count())]:
            widget.setCurrentText(str(v))
        else:
            widget.setCurrentIndex(0)
    elif isinstance(widget, QCheckBox):
        widget.setChecked(True)
    elif isinstance(widget, QTextEdit):
        widget.setPlainText(str(v if v is not None else "Generic text."))
    else:
        # TableInputWidget and others: add a generic row
        if hasattr(widget, "add_row"):
            cols = getattr(widget, "columns", [])
            widget.add_row(["Generic"] * len(cols) if cols else ["Generic"])


def test_wizard_e2e(app):
    print("\n[2] WIZARD END-TO-END — generate a real Word document")
    from wizard_engine import GeneratorWizard
    from regression_templates import generic_values

    wiz = GeneratorWizard()
    wiz.show()
    app.processEvents()

    # page 0: template (row 0 already selected)
    p0 = wiz.page(0)
    ok(p0.listw.count() >= 50, f"template list >= 50 (got {p0.listw.count()})")
    first_key = p0.selected_key()
    ok(bool(first_key), f"template selected: {first_key}")

    vm = generic_values()
    # navigate through pages, initializing each
    for pid in range(1, 7):
        wiz.setCurrentId(pid)
        app.processEvents()

    # page 2: sections — default all checked
    p2 = wiz.page(2)
    heads = p2.selected_heads()
    ok(len(heads) > 3, f"sections selected: {len(heads)}")

    # page 3: inputs — fill every field
    p3 = wiz.page(3)
    filled = 0
    for key, w in p3.widgets.items():
        _fill_widget(w, key, vm)
        filled += 1
    ok(filled > 0, f"filled {filled} input fields")
    vals = p3.values()
    ok(len(vals) > 0, f"values() populated ({len(vals)} keys)")

    # page 5: options — output to temp dir
    tmp = tempfile.mkdtemp(prefix="drl_ui_")
    p5 = wiz.page(5)
    p5.path.setText(tmp)
    p5.fname.setText("smoke_test.docx")
    p5.initializePage()

    # page 6: generate
    p6 = wiz.page(6)
    p6.initializePage()
    p6._generate()
    app.processEvents()
    path = getattr(p6, "_last_path", "")
    ok(bool(path) and os.path.exists(path), f"document generated: {path}")
    if path and os.path.exists(path):
        text = docx_text(path)
        for name in ("VALIDATION & COMPLIANCE", "PROGRAM READINESS SCORE",
                     "STANDARDS COMPLIANCE MATRIX",
                     "DOCUMENT COMPLIANCE REPORT",
                     "ENGINEERING CALCULATION REGISTER",
                     "DEEP ENGINEERING VERIFICATION"):
            ok(name in text, f"section present: {name}")
    wiz.close()


def test_rop_dialog(app):
    print("\n[3] ROP CALIBRATION DIALOG — sample fit")
    from wizard_engine import ROPCalibrationDialog
    dlg = ROPCalibrationDialog()
    dlg._load_sample()
    dlg._fit()
    ok(dlg.result is not None and dlg.result.get("k", 0) > 0,
       f"model fitted from sample: K={dlg.result and dlg.result.get('k'):.4g}")
    ok(dlg.result.get("n_points") == 5, "5 sample points used")
    dlg.deleteLater()


def test_operations_dialog(app):
    print("\n[4] OPERATIONS DIALOG — constructs with tabs")
    from operations_ui import OperationsDialog
    dlg = OperationsDialog(well_data={"mud_weight": "12", "td_depth": "10000"},
                           well_id="smoke")
    dlg.show()
    app.processEvents()
    ok(dlg.isVisible() or not dlg.isHidden(), "operations dialog shown")
    dlg.close()


def test_step_editor(app):
    print("\n[5] STEP EDITOR DIALOG — structured fields + auto-structure")
    from procedures_db import StepEditorDialog
    dlg = StepEditorDialog()
    dlg.txt.setPlainText(
        "Run casing to shoe depth - hold point required before continuing, "
        "verify returns by mud logger")
    dlg._auto_structure()
    data = dlg.get_data()
    ok(data["hold_point"], "hold point auto-detected in editor")
    ok("verify" in data["acceptance"].lower() or "returns" in
       data["acceptance"].lower(), "acceptance auto-filled")
    ok(bool(data["text"]), "step text preserved")
    dlg.deleteLater()
    # procedure editor constructs with a real DB procedure
    from procedures_db import ProcedureDatabase, ProcedureEditorDialog
    import tempfile, os
    tmp = tempfile.mkdtemp(prefix="drl_pe_")
    dbp = os.path.join(tmp, "procedures.db")
    db = ProcedureDatabase(db_path=dbp)
    cat = db.add_category("Smoke")
    pid = db.add_procedure("Smoke Procedure", cat)
    db.add_step(pid, "Test step", precondition="Pre", acceptance="Acc",
                hold_point=True)
    ed = ProcedureEditorDialog(db, proc_id=pid)
    ed.show()
    app.processEvents()
    ok(ed.steps_list.count() == 1, "procedure editor shows the step")
    ed.close()
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


def docx_text(path):
    from docx import Document
    d = Document(path)
    parts = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            for c in row.cells:
                parts.append(c.text)
    return "\n".join(parts)


if __name__ == "__main__":
    app = QApplication([])
    try:
        test_main_window(app)
        test_wizard_e2e(app)
        test_rop_dialog(app)
        test_operations_dialog(app)
        test_step_editor(app)
    finally:
        app.processEvents()
    print("\n" + "=" * 60)
    print(f"RESULT: {_PASS} passed, {_FAIL} failed")
    sys.exit(1 if _FAIL else 0)
