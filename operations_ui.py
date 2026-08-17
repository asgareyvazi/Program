# ============================================================================
# OPERATIONS UI — Readiness / Lessons Learned / NPT / Plan vs Actual
# File: operations_ui.py
# Audit items (P1): gives the desktop app the operational layer —
#   - Program Readiness Score dialog (completeness before approval)
#   - Lessons Learned entry & viewer
#   - NPT event entry & summary
#   - Daily report / Plan vs Actual variance
# ============================================================================

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QMessageBox, QHeaderView, QDoubleSpinBox, QFormLayout, QSplitter,
    QWidget,
)
from PySide6.QtCore import Qt

from operations_engine import (LessonsDatabase, readiness_score,
                               readiness_markdown)
from audit_log import log_action


class OperationsDialog(QDialog):
    """Readiness / Lessons / NPT / Plan-vs-Actual in one dialog."""

    def __init__(self, parent=None, well_data: dict = None,
                 well_id: str = ""):
        super().__init__(parent)
        self.setWindowTitle("📊 Operations — Readiness, Lessons, NPT, Plan vs Actual")
        self.setMinimumSize(1000, 680)
        self.well_data = well_data or {}
        self.well_id = well_id
        self.db = LessonsDatabase()

        lay = QVBoxLayout(self)
        tabs = QTabWidget()

        tabs.addTab(self._build_readiness(), "✅ Readiness Score")
        tabs.addTab(self._build_lessons(), "💡 Lessons Learned")
        tabs.addTab(self._build_npt(), "⏱️ NPT Events")
        tabs.addTab(self._build_daily(), "📅 Daily / Plan vs Actual")
        tabs.addTab(self._build_afe(), "💰 AFE vs Actual")
        tabs.addTab(self._build_materials(), "📦 Materials")
        lay.addWidget(tabs)

        btns = QHBoxLayout()
        btns.addStretch()
        b_close = QPushButton("Close")
        b_close.clicked.connect(self.accept)
        btns.addWidget(b_close)
        lay.addLayout(btns)

    # ------------------------------------------------------------------
    def _build_readiness(self):
        w = QWidget()
        l = QVBoxLayout(w)
        r = readiness_score(self.well_data)
        head = QLabel(f"<h2>Completeness: {r['score']}/100 — "
                      f"<span style='color:{'#27ae60' if r['grade']=='READY' else '#e94560'}'>"
                      f"{r['grade']}</span></h2>")
        l.addWidget(head)
        if r["critical_missing"]:
            cm = QLabel("⚠️ <b>Critical missing (blocks approval):</b><br>• " +
                        "<br>• ".join(r["critical_missing"]))
            cm.setStyleSheet("color:#e94560;")
            l.addWidget(cm)
        if r["missing"]:
            mm = QLabel("📋 Other missing:<br>• " + "<br>• ".join(r["missing"]))
            mm.setStyleSheet("color:#8a8a9a;")
            l.addWidget(mm)
        done = QLabel(f"✅ Completed: {len(r['done'])}/{r['total_checks']} checks")
        l.addWidget(done)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(readiness_markdown(self.well_data))
        txt.setMaximumHeight(220)
        l.addWidget(txt)
        l.addStretch()
        return w

    def _build_lessons(self):
        w = QWidget()
        l = QVBoxLayout(w)
        form = QFormLayout()
        self.l_field = QLineEdit(self.well_data.get("field_name", ""))
        self.l_operation = QComboBox()
        self.l_operation.addItems(["Drilling", "Workover", "Cementing",
                                   "Well Control", "Stuck Pipe", "Fishing",
                                   "Completion", "Other"])
        self.l_category = QLineEdit()
        self.l_lesson = QLineEdit()
        self.l_cause = QLineEdit()
        self.l_prevention = QLineEdit()
        form.addRow("Field:", self.l_field)
        form.addRow("Operation:", self.l_operation)
        form.addRow("Category:", self.l_category)
        form.addRow("Lesson:", self.l_lesson)
        form.addRow("Cause:", self.l_cause)
        form.addRow("Prevention:", self.l_prevention)
        l.addLayout(form)
        btn = QPushButton("➕ Add Lesson")
        btn.clicked.connect(self._add_lesson)
        l.addWidget(btn)
        self.lessons_table = QTableWidget(0, 4)
        self.lessons_table.setHorizontalHeaderLabels(
            ["Operation", "Category", "Lesson", "Prevention"])
        hdr = self.lessons_table.horizontalHeader()
        hdr.setSectionResizeMode(2, QHeaderView.Stretch)
        hdr.setSectionResizeMode(3, QHeaderView.Stretch)
        l.addWidget(self.lessons_table, 1)
        self._refresh_lessons()
        return w

    def _add_lesson(self):
        self.db.add_lesson(
            well_id=self.well_id,
            well_name=self.well_data.get("well_name", ""),
            field=self.l_field.text().strip(),
            operation=self.l_operation.currentText(),
            category=self.l_category.text().strip(),
            lesson=self.l_lesson.text().strip(),
            cause=self.l_cause.text().strip(),
            prevention=self.l_prevention.text().strip())
        log_action("lesson_added", "", self.l_field.text(),
                   self.l_lesson.text()[:60])
        self.l_lesson.clear(); self.l_cause.clear(); self.l_prevention.clear()
        self._refresh_lessons()

    def _refresh_lessons(self):
        rows = self.db.lessons_for(limit=100)
        self.lessons_table.setRowCount(0)
        for r in rows:
            i = self.lessons_table.rowCount()
            self.lessons_table.insertRow(i)
            for j, v in enumerate((r["operation"], r["category"],
                                   r["lesson"], r["prevention"])):
                self.lessons_table.setItem(i, j, QTableWidgetItem(str(v or "")))

    # ------------------------------------------------------------------
    def _build_npt(self):
        w = QWidget()
        l = QVBoxLayout(w)
        form = QFormLayout()
        self.n_date = QLineEdit("2026-08-17")
        self.n_duration = QDoubleSpinBox(); self.n_duration.setRange(0, 720); self.n_duration.setDecimals(1)
        self.n_category = QComboBox()
        self.n_category.addItems(["Stuck Pipe", "Lost Circulation", "Kick",
                                  "Equipment Failure", "Weather", "Fishing",
                                  "Cementing", "Other"])
        self.n_cause = QLineEdit()
        self.n_subcause = QLineEdit()
        self.n_direct = QDoubleSpinBox(); self.n_direct.setRange(0, 1e9); self.n_direct.setDecimals(0)
        self.n_indirect = QDoubleSpinBox(); self.n_indirect.setRange(0, 1e9); self.n_indirect.setDecimals(0)
        self.n_corrective = QLineEdit()
        self.n_preventive = QLineEdit()
        form.addRow("Date:", self.n_date)
        form.addRow("Duration (hr):", self.n_duration)
        form.addRow("Category:", self.n_category)
        form.addRow("Cause:", self.n_cause)
        form.addRow("Sub-cause:", self.n_subcause)
        form.addRow("Direct cost ($):", self.n_direct)
        form.addRow("Indirect cost ($):", self.n_indirect)
        form.addRow("Corrective:", self.n_corrective)
        form.addRow("Preventive:", self.n_preventive)
        l.addLayout(form)
        btn = QPushButton("➕ Add NPT Event")
        btn.clicked.connect(self._add_npt)
        l.addWidget(btn)
        self.npt_summary_lbl = QLabel("")
        l.addWidget(self.npt_summary_lbl)
        self.npt_table = QTableWidget(0, 5)
        self.npt_table.setHorizontalHeaderLabels(
            ["Date", "Category", "Cause", "Dur (hr)", "Cost ($)"])
        l.addWidget(self.npt_table, 1)
        self._refresh_npt()
        return w

    def _add_npt(self):
        self.db.add_npt(
            well_id=self.well_id,
            well_name=self.well_data.get("well_name", ""),
            date=self.n_date.text().strip(), duration_hr=self.n_duration.value(),
            category=self.n_category.currentText(), cause=self.n_cause.text().strip(),
            subcause=self.n_subcause.text().strip(),
            direct_cost=self.n_direct.value(), indirect_cost=self.n_indirect.value(),
            corrective=self.n_corrective.text().strip(),
            preventive=self.n_preventive.text().strip())
        log_action("npt_added", "", self.well_data.get("well_name", ""),
                   f"{self.n_category.currentText()} {self.n_duration.value()}hr")
        self.n_cause.clear(); self.n_subcause.clear()
        self.n_corrective.clear(); self.n_preventive.clear()
        self._refresh_npt()

    def _refresh_npt(self):
        s = self.db.npt_summary(self.well_id)
        self.npt_summary_lbl.setText(
            f"Total: {s['events']} events | {s['total_hr']:.0f} hr | "
            f"${s['total_cost']:,.0f}")
        rows = self.db.conn.execute(
            "SELECT * FROM npt_events ORDER BY id DESC LIMIT 100").fetchall()
        self.npt_table.setRowCount(0)
        for r in rows:
            i = self.npt_table.rowCount()
            self.npt_table.insertRow(i)
            vals = (r["date"], r["category"], r["cause"], r["duration_hr"],
                    (r["direct_cost"] or 0) + (r["indirect_cost"] or 0))
            for j, v in enumerate(vals):
                self.npt_table.setItem(i, j, QTableWidgetItem(str(v or "")))

    # ------------------------------------------------------------------
    def _build_daily(self):
        w = QWidget()
        l = QVBoxLayout(w)
        form = QFormLayout()
        self.d_date = QLineEdit("2026-08-17")
        self.d_depth = QDoubleSpinBox(); self.d_depth.setRange(0, 20000); self.d_depth.setDecimals(0)
        self.d_rop = QDoubleSpinBox(); self.d_rop.setRange(0, 500); self.d_rop.setDecimals(1)
        self.d_plan_depth = QDoubleSpinBox(); self.d_plan_depth.setRange(0, 20000); self.d_plan_depth.setDecimals(0)
        self.d_plan_rop = QDoubleSpinBox(); self.d_plan_rop.setRange(0, 500); self.d_plan_rop.setDecimals(1)
        self.d_npt = QDoubleSpinBox(); self.d_npt.setRange(0, 24); self.d_npt.setDecimals(1)
        self.d_remarks = QLineEdit()
        form.addRow("Date:", self.d_date)
        form.addRow("Actual Depth (m):", self.d_depth)
        form.addRow("Actual ROP (m/hr):", self.d_rop)
        form.addRow("Plan Depth (m):", self.d_plan_depth)
        form.addRow("Plan ROP (m/hr):", self.d_plan_rop)
        form.addRow("NPT (hr):", self.d_npt)
        form.addRow("Remarks:", self.d_remarks)
        l.addLayout(form)
        btn = QPushButton("➕ Record Daily Report")
        btn.clicked.connect(self._add_daily)
        l.addWidget(btn)
        self.daily_table = QTableWidget(0, 6)
        self.daily_table.setHorizontalHeaderLabels(
            ["Date", "Actual (m)", "Plan (m)", "Var (m)", "NPT (hr)", "Remarks"])
        hdr = self.daily_table.horizontalHeader()
        hdr.setSectionResizeMode(5, QHeaderView.Stretch)
        l.addWidget(self.daily_table, 1)
        self._refresh_daily()
        return w

    def _add_daily(self):
        self.db.add_daily(
            well_id=self.well_id,
            well_name=self.well_data.get("well_name", ""),
            date=self.d_date.text().strip(), depth_m=self.d_depth.value(),
            rop_mhr=self.d_rop.value(), plan_depth_m=self.d_plan_depth.value(),
            plan_rop_mhr=self.d_plan_rop.value(), npt_hr=self.d_npt.value(),
            remarks=self.d_remarks.text().strip())
        log_action("daily_added", "", self.well_data.get("well_name", ""),
                   self.d_date.text())
        self.d_remarks.clear()
        self._refresh_daily()

    def _refresh_daily(self):
        rows = self.db.plan_vs_actual(self.well_id)
        self.daily_table.setRowCount(0)
        for r in rows:
            i = self.daily_table.rowCount()
            self.daily_table.insertRow(i)
            vals = (r["date"], f"{r['depth_m'] or 0:,.0f}",
                    f"{r['plan_depth_m'] or 0:,.0f}",
                    f"{r['depth_variance_m']:+,.0f}", r["npt_hr"], r["remarks"])
            for j, v in enumerate(vals):
                self.daily_table.setItem(i, j, QTableWidgetItem(str(v or "")))

    # ------------------------------------------------------------------
    def _build_afe(self):
        w = QWidget()
        l = QVBoxLayout(w)
        form = QFormLayout()
        self.afe_number = QLineEdit("AFE-001")
        self.afe_budget = QDoubleSpinBox(); self.afe_budget.setRange(0, 1e12); self.afe_budget.setDecimals(0)
        self.afe_commit = QDoubleSpinBox(); self.afe_commit.setRange(0, 1e12); self.afe_commit.setDecimals(0)
        self.afe_actual = QDoubleSpinBox(); self.afe_actual.setRange(0, 1e12); self.afe_actual.setDecimals(0)
        self.afe_forecast = QDoubleSpinBox(); self.afe_forecast.setRange(0, 1e12); self.afe_forecast.setDecimals(0)
        form.addRow("AFE Number:", self.afe_number)
        form.addRow("Budget ($):", self.afe_budget)
        form.addRow("Committed ($):", self.afe_commit)
        form.addRow("Actual ($):", self.afe_actual)
        form.addRow("Forecast ($):", self.afe_forecast)
        l.addLayout(form)
        btn = QPushButton("➕ Record AFE")
        btn.clicked.connect(self._add_afe)
        l.addWidget(btn)
        self.afe_lbl = QLabel("")
        l.addWidget(self.afe_lbl)
        self.afe_table = QTableWidget(0, 6)
        self.afe_table.setHorizontalHeaderLabels(
            ["AFE #", "Budget", "Committed", "Actual", "Forecast", "Δ%"])
        l.addWidget(self.afe_table, 1)
        self._refresh_afe()
        return w

    def _add_afe(self):
        self.db.add_afe(well_id=self.well_id,
                        well_name=self.well_data.get("well_name", ""),
                        afe_number=self.afe_number.text().strip(),
                        budget_usd=self.afe_budget.value(),
                        commitment_usd=self.afe_commit.value(),
                        actual_usd=self.afe_actual.value(),
                        forecast_usd=self.afe_forecast.value())
        log_action("afe_added", "", self.afe_number.text(), "budget updated")
        self._refresh_afe()

    def _refresh_afe(self):
        s = self.db.afe_status(self.well_id)
        if s:
            self.afe_lbl.setText(
                f"Budget ${s['budget_usd']:,.0f} | Actual {s['actual_pct']}% | "
                f"Forecast {s['forecast_vs_budget_pct']:+.1f}% vs budget")
        rows = self.db.conn.execute(
            "SELECT * FROM afe ORDER BY id DESC LIMIT 50").fetchall()
        self.afe_table.setRowCount(0)
        for r in rows:
            i = self.afe_table.rowCount()
            self.afe_table.insertRow(i)
            vals = (r["afe_number"], f"{r['budget_usd'] or 0:,.0f}",
                    f"{r['commitment_usd'] or 0:,.0f}",
                    f"{r['actual_usd'] or 0:,.0f}",
                    f"{r['forecast_usd'] or 0:,.0f}", "")
            for j, v in enumerate(vals):
                self.afe_table.setItem(i, j, QTableWidgetItem(str(v)))

    # ------------------------------------------------------------------
    def _build_materials(self):
        w = QWidget()
        l = QVBoxLayout(w)
        form = QFormLayout()
        self.mat_item = QLineEdit()
        self.mat_cat = QComboBox()
        self.mat_cat.addItems(["Tubulars", "Mud", "Cement", "Bits", "BOP",
                               "Chemicals", "Spares", "Other"])
        self.mat_req = QDoubleSpinBox(); self.mat_req.setRange(0, 1e6); self.mat_req.setDecimals(1)
        self.mat_avail = QDoubleSpinBox(); self.mat_avail.setRange(0, 1e6); self.mat_avail.setDecimals(1)
        self.mat_unit = QLineEdit("m")
        self.mat_critical = QComboBox(); self.mat_critical.addItems(["No", "Yes"])
        form.addRow("Item:", self.mat_item)
        form.addRow("Category:", self.mat_cat)
        form.addRow("Required qty:", self.mat_req)
        form.addRow("Available qty:", self.mat_avail)
        form.addRow("Unit:", self.mat_unit)
        form.addRow("Critical:", self.mat_critical)
        l.addLayout(form)
        btn = QPushButton("➕ Add Material")
        btn.clicked.connect(self._add_material)
        l.addWidget(btn)
        self.mat_lbl = QLabel("")
        l.addWidget(self.mat_lbl)
        self.mat_table = QTableWidget(0, 6)
        self.mat_table.setHorizontalHeaderLabels(
            ["Item", "Category", "Required", "Available", "Unit", "Status"])
        l.addWidget(self.mat_table, 1)
        self._refresh_materials()
        return w

    def _add_material(self):
        self.db.add_material(
            well_id=self.well_id, well_name=self.well_data.get("well_name", ""),
            item=self.mat_item.text().strip(),
            category=self.mat_cat.currentText(),
            required_qty=self.mat_req.value(),
            available_qty=self.mat_avail.value(),
            unit=self.mat_unit.text().strip(),
            critical=self.mat_critical.currentText() == "Yes")
        self.mat_item.clear()
        self._refresh_materials()

    def _refresh_materials(self):
        m = self.db.material_readiness(self.well_id)
        if m["items"]:
            self.mat_lbl.setText(
                f"Ready {m['ready']} | Short {m['short']}" +
                (f" | ⛔ {len(m['critical_short'])} critical short"
                 if m["critical_short"] else ""))
        rows = m["items"][-50:]
        self.mat_table.setRowCount(0)
        for r in rows:
            i = self.mat_table.rowCount()
            self.mat_table.insertRow(i)
            status = "✅" if r["available_qty"] >= r["required_qty"] else \
                     ("⛔" if r["critical"] else "⚠️")
            vals = (r["item"], r["category"], f"{r['required_qty']:g}",
                    f"{r['available_qty']:g}", r["unit"], status)
            for j, v in enumerate(vals):
                self.mat_table.setItem(i, j, QTableWidgetItem(str(v)))
