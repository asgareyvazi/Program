# ============================================================================
# COST & PRICING TAB — CBS (Cost Breakdown Structure) UI
# File: cbs_ui.py
# Editable price catalog (defaults from AZNS field documents), quantity
# entries, automatic totals, Time Breakdown linkage and AFE export to Word.
# ============================================================================

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QComboBox, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QMessageBox, QFileDialog,
    QDoubleSpinBox, QGroupBox, QScrollArea, QSplitter, QCheckBox,
    QDialog, QDialogButtonBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from cbs_db import (
    CBSDatabase, CbsItem, build_afe, export_afe_docx,
    get_time_breakdown_summary, SEED_CATALOG,
)

CBS_STYLE = """
QFrame#cbsCard {
    background-color: #1a1a2e;
    border: 1px solid #0f3460;
    border-radius: 10px;
}
QLabel#cbsTitle {
    color: #e94560;
    font-size: 15px;
    font-weight: bold;
}
QLabel#cbsSub {
    color: #8a8a9a;
    font-size: 11px;
}
QLabel#cbsBig {
    color: #e0e0e0;
    font-size: 14px;
    font-weight: bold;
}
QLabel#cbsTotal {
    color: #4ecca3;
    font-size: 20px;
    font-weight: bold;
}
QTableWidget {
    background-color: #16213e;
    alternate-background-color: #1a1a2e;
    gridline-color: #0f3460;
    color: #e0e0e0;
    selection-background-color: #e94560;
}
QHeaderView::section {
    background-color: #0f3460;
    color: #ffffff;
    font-weight: bold;
    padding: 4px;
    border: 1px solid #1a1a2e;
}
QComboBox, QLineEdit, QDoubleSpinBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #0f3460;
    border-radius: 4px;
    padding: 3px;
}
QPushButton {
    background-color: #0f3460;
    color: #ffffff;
    border-radius: 5px;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover { background-color: #e94560; }
"""


class CbsSelectionDialog(QDialog):
    """انتخاب کالاها/سرویس‌های موردنیاز + تعداد و قیمت — برای ویزارد

    خروجی: لیست dict ها شامل id, name, unit, price, qty برای اقلام انتخاب‌شده.
    """

    COL_INC, COL_NAME, COL_UNIT, COL_PRICE, COL_QTY = range(5)

    def __init__(self, parent=None, db: CBSDatabase = None):
        super().__init__(parent)
        self.setWindowTitle("📋 Select Goods & Services (CBS)")
        self.setMinimumSize(820, 560)
        self.db = db or CBSDatabase()
        self._updating = False
        self.selection: list = []

        lay = QVBoxLayout(self)
        tip = QLabel(
            "Tick the goods & services required for this job, set "
            "quantities (and adjust unit prices if needed). These will be "
            "used to build the Cost Breakdown / AFE section of the document.")
        tip.setWordWrap(True)
        tip.setStyleSheet("color:#8a8a9a;")
        lay.addWidget(tip)

        # filter
        fr = QHBoxLayout()
        fr.addWidget(QLabel("Category:"))
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItem("All Categories", "")
        for c in self.db.get_categories():
            self.cmb_cat.addItem(c, c)
        self.cmb_cat.currentIndexChanged.connect(self._reload)
        fr.addWidget(self.cmb_cat, 1)
        btn_all = QPushButton("✓ Select All")
        btn_all.clicked.connect(lambda: self._set_all(True))
        btn_none = QPushButton("✗ Clear All")
        btn_none.clicked.connect(lambda: self._set_all(False))
        fr.addWidget(btn_all)
        fr.addWidget(btn_none)
        lay.addLayout(fr)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(
            ["Include", "Item", "Unit", "Unit Price", "Qty"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(self.COL_INC, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        hdr.setSectionResizeMode(self.COL_UNIT, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_PRICE, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_QTY, QHeaderView.ResizeToContents)
        lay.addWidget(self.table, 1)

        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        bb.accepted.connect(self._accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

        self._reload()

    def _reload(self):
        cat = self.cmb_cat.currentData() or ""
        items = [i for i in self.db.get_items()
                 if not cat or i.category == cat]
        self._updating = True
        self.table.setRowCount(0)
        for it in items:
            r = self.table.rowCount()
            self.table.insertRow(r)
            chk = QTableWidgetItem()
            chk.setCheckState(Qt.Checked if it.qty > 0 else Qt.Unchecked)
            self.table.setItem(r, self.COL_INC, chk)
            self.table.setItem(r, self.COL_NAME, QTableWidgetItem(it.name))
            self.table.setItem(r, self.COL_UNIT, QTableWidgetItem(it.unit))
            p = QTableWidgetItem(f"{it.unit_price:,.2f}" if it.unit_price else "")
            self.table.setItem(r, self.COL_PRICE, p)
            q = QTableWidgetItem(f"{it.qty:,.2f}" if it.qty else "1")
            self.table.setItem(r, self.COL_QTY, q)
        self._updating = False

    def _set_all(self, on: bool):
        for r in range(self.table.rowCount()):
            item = self.table.item(r, self.COL_INC)
            if item:
                item.setCheckState(Qt.Checked if on else Qt.Unchecked)

    def _accept(self):
        sel = []
        for r in range(self.table.rowCount()):
            inc = self.table.item(r, self.COL_INC)
            if not inc or inc.checkState() != Qt.Checked:
                continue
            name = self.table.item(r, self.COL_NAME).text().strip()
            unit = self.table.item(r, self.COL_UNIT).text().strip() or "each"
            try:
                price = float(self.table.item(r, self.COL_PRICE).text()
                              .replace(",", "") or 0)
            except ValueError:
                price = 0.0
            try:
                qty = float(self.table.item(r, self.COL_QTY).text()
                            .replace(",", "") or 0)
            except ValueError:
                qty = 0.0
            sel.append({"name": name, "unit": unit,
                        "price": price, "qty": qty})
        self.selection = sel
        self.accept()


class CostPricingTab(QWidget):
    """تب قیمت‌گذاری و ساختار شکست هزینه (CBS) — قیمت‌های پیش‌فرض قابل ویرایش"""

    data_changed = Signal()

    COL_CODE, COL_NAME, COL_UNIT, COL_PRICE, COL_QTY, COL_AMOUNT = range(6)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = CBSDatabase()
        self.items: list = []          # CbsItem list currently shown (filtered)
        self._loaded_all: list = []    # all active items from DB
        self._build_ui()
        self._reload()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)
        self.setStyleSheet(CBS_STYLE)

        # ---- Header ----
        head = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("💰 Cost & Pricing — Cost Breakdown Structure (CBS)")
        title.setObjectName("cbsTitle")
        sub = QLabel(
            "Editable default prices (AZNS field catalog). Unit prices and "
            "quantities are user-editable; totals & AFE are calculated "
            "automatically. Time Breakdown durations link to rig cost.")
        sub.setObjectName("cbsSub")
        sub.setWordWrap(True)
        title_box.addWidget(title)
        title_box.addWidget(sub)
        head.addLayout(title_box, 1)

        self.cmb_currency = QComboBox()
        self.cmb_currency.addItems(["USD", "EUR", "IRR (Million)"])
        self.cmb_currency.setCurrentText(self.db.get_currency())
        self.cmb_currency.currentTextChanged.connect(
            lambda c: self.db.set_currency(c))
        head.addWidget(QLabel("Currency:"))
        head.addWidget(self.cmb_currency)

        btn_save = QPushButton("💾 Save Prices")
        btn_save.clicked.connect(self._save)
        head.addWidget(btn_save)
        btn_reset = QPushButton("↺ Reset Defaults")
        btn_reset.clicked.connect(self._reset_defaults)
        head.addWidget(btn_reset)
        root.addLayout(head)

        # ---- Filter row ----
        filt = QHBoxLayout()
        filt.addWidget(QLabel("Category:"))
        self.cmb_cat = QComboBox()
        self.cmb_cat.addItem("All Categories", "")
        self.cmb_cat.currentIndexChanged.connect(self._apply_filter)
        filt.addWidget(self.cmb_cat, 1)

        btn_add = QPushButton("➕ Add Item")
        btn_add.clicked.connect(self._add_item)
        filt.addWidget(btn_add)
        btn_del = QPushButton("🗑 Delete Item")
        btn_del.clicked.connect(self._delete_item)
        filt.addWidget(btn_del)
        btn_afe = QPushButton("📄 Export AFE (Word)")
        btn_afe.clicked.connect(self._export_afe)
        filt.addWidget(btn_afe)
        root.addLayout(filt)

        # ---- Splitter: table | summary ----
        splitter = QSplitter(Qt.Horizontal)

        # Table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(
            ["Code", "Item / Description", "Unit", "Unit Price",
             "Qty", "Amount"])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.SelectedClicked | QAbstractItemView.AnyKeyPressed)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(self.COL_CODE, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_NAME, QHeaderView.Stretch)
        hdr.setSectionResizeMode(self.COL_UNIT, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_PRICE, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_QTY, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(self.COL_AMOUNT, QHeaderView.ResizeToContents)
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.itemChanged.connect(self._on_item_changed)
        splitter.addWidget(self.table)

        # ---- Right panel: summary + dayrates ----
        right = QWidget()
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)

        # Dayrate card
        card = QFrame()
        card.setObjectName("cbsCard")
        cv = QVBoxLayout(card)
        t = QLabel("⏱️ Rig Cost — linked to Time Breakdown")
        t.setObjectName("cbsTitle")
        cv.addWidget(t)
        self.lbl_tb_info = QLabel("Time Breakdown: not loaded")
        self.lbl_tb_info.setObjectName("cbsSub")
        self.lbl_tb_info.setWordWrap(True)
        cv.addWidget(self.lbl_tb_info)
        gr = QGridLayout()
        gr.addWidget(QLabel("Rig Day Rate:"), 0, 0)
        self.spin_rig_rate = QDoubleSpinBox()
        self.spin_rig_rate.setRange(0, 1e9)
        self.spin_rig_rate.setDecimals(2)
        gr.addWidget(self.spin_rig_rate, 0, 1)
        gr.addWidget(QLabel("Spread Cost/Day:"), 1, 0)
        self.spin_spread = QDoubleSpinBox()
        self.spin_spread.setRange(0, 1e9)
        self.spin_spread.setDecimals(2)
        gr.addWidget(self.spin_spread, 1, 1)
        gr.addWidget(QLabel("Total Days:"), 2, 0)
        self.spin_days = QDoubleSpinBox()
        self.spin_days.setRange(0, 10000)
        self.spin_days.setDecimals(1)
        gr.addWidget(self.spin_days, 2, 1)
        gr.addWidget(QLabel("Well Depth (m):"), 3, 0)
        self.spin_depth = QDoubleSpinBox()
        self.spin_depth.setRange(0, 20000)
        self.spin_depth.setDecimals(0)
        gr.addWidget(self.spin_depth, 3, 1)
        cv.addLayout(gr)
        btn_tb = QPushButton("📥 Load from Time Breakdown")
        btn_tb.clicked.connect(self._load_time_breakdown)
        cv.addWidget(btn_tb)
        rv.addWidget(card)

        # Totals card
        card2 = QFrame()
        card2.setObjectName("cbsCard")
        cv2 = QVBoxLayout(card2)
        t2 = QLabel("🧮 Cost Summary")
        t2.setObjectName("cbsTitle")
        cv2.addWidget(t2)
        self.lbl_totals = QLabel("")
        self.lbl_totals.setObjectName("cbsBig")
        self.lbl_totals.setWordWrap(True)
        cv2.addWidget(self.lbl_totals)
        self.lbl_grand = QLabel("TOTAL: 0.00")
        self.lbl_grand.setObjectName("cbsTotal")
        cv2.addWidget(self.lbl_grand)
        rv.addWidget(card2)
        rv.addStretch(1)

        splitter.addWidget(right)
        splitter.setSizes([900, 380])
        root.addWidget(splitter, 1)

        self._updating = False

    # ------------------------------------------------------------- data
    def _reload(self):
        self._loaded_all = self.db.get_items()
        cats = self.db.get_categories()
        self.cmb_cat.blockSignals(True)
        self.cmb_cat.clear()
        self.cmb_cat.addItem("All Categories", "")
        for c in cats:
            self.cmb_cat.addItem(c, c)
        self.cmb_cat.blockSignals(False)
        self._apply_filter()

    def _apply_filter(self):
        cat = self.cmb_cat.currentData() or ""
        self.items = [i for i in self._loaded_all
                      if not cat or i.category == cat]
        self._fill_table()
        self._refresh_summary()

    def _fill_table(self):
        self._updating = True
        self.table.setRowCount(0)
        for it in self.items:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self._set_item_cell(r, self.COL_CODE, it.code)
            name = it.name
            if it.description:
                name = f"{name}\n{it.description}"
            self._set_item_cell(r, self.COL_NAME, name)
            self._set_item_cell(r, self.COL_UNIT, it.unit)
            self._set_item_cell(r, self.COL_PRICE,
                                f"{it.unit_price:,.2f}" if it.unit_price else "")
            self._set_item_cell(r, self.COL_QTY,
                                f"{it.qty:,.2f}" if it.qty else "")
            self._set_item_cell(r, self.COL_AMOUNT,
                                f"{it.unit_price * it.qty:,.2f}"
                                if it.unit_price and it.qty else "")
        self._updating = False
        self._refresh_summary()

    def _set_item_cell(self, row, col, text):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        if col in (self.COL_PRICE, self.COL_QTY, self.COL_AMOUNT):
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, col, item)

    def _on_cell_changed(self, row, col):
        if self._updating or row >= len(self.items):
            return
        if col in (self.COL_PRICE, self.COL_QTY):
            self._refresh_row_amount(row)

    def _on_item_changed(self, item):
        if self._updating:
            return
        row = item.row()
        if row >= len(self.items):
            return
        col = item.column()
        it = self.items[row]
        try:
            if col == self.COL_CODE:
                it.code = item.text().strip()
            elif col == self.COL_NAME:
                parts = item.text().split("\n")
                it.name = parts[0].strip()
                it.description = "\n".join(parts[1:]).strip()
            elif col == self.COL_UNIT:
                it.unit = item.text().strip() or "each"
            elif col == self.COL_PRICE:
                it.unit_price = float(item.text().replace(",", "").strip() or 0)
            elif col == self.COL_QTY:
                it.qty = float(item.text().replace(",", "").strip() or 0)
        except ValueError:
            pass
        if col in (self.COL_PRICE, self.COL_QTY, self.COL_NAME, self.COL_UNIT):
            self._refresh_row_amount(row)
        self._refresh_summary()

    def _refresh_row_amount(self, row):
        it = self.items[row]
        amt = it.unit_price * it.qty
        self._updating = True
        self.table.item(row, self.COL_AMOUNT).setText(
            f"{amt:,.2f}" if amt else "")
        self._updating = False

    def _refresh_summary(self):
        totals = CBSDatabase.compute_totals(self._loaded_all)
        lines = []
        for cat, amt in sorted(totals["category_totals"].items()):
            lines.append(f"{cat}: {amt:,.2f}")
        self.lbl_totals.setText("\n".join(lines) if lines else "No items yet.")
        self.lbl_grand.setText(
            f"TOTAL: {totals['total']:,.2f} "
            f"(incl. {totals['contingency_pct']:.0f}% contingency)")

    # ------------------------------------------------------------ actions
    def _save(self):
        self.db.save_items(self._loaded_all)
        QMessageBox.information(
            self, "Saved",
            "Prices saved to CBS database.\n"
            "They are used as editable defaults in AFE export.")

    def _reset_defaults(self):
        if QMessageBox.question(
                self, "Reset",
                "Reset catalog to factory defaults (prices become TBD)?") \
                == QMessageBox.Yes:
            self.db.reset_to_defaults()
            self._reload()

    def _add_item(self):
        cat = self.cmb_cat.currentData() or "2. Drilling Services"
        it = CbsItem(code="", category=cat, name="New Item",
                     description="", unit="each", unit_price=0.0, qty=0.0)
        self.db.save_item(it)
        self._reload()
        # scroll to new row
        for i, x in enumerate(self.items):
            if x.id == it.id:
                self.table.selectRow(i)
                break

    def _delete_item(self):
        r = self.table.currentRow()
        if r < 0 or r >= len(self.items):
            QMessageBox.information(self, "Select", "Select an item first.")
            return
        it = self.items[r]
        if QMessageBox.question(
                self, "Delete",
                f"Delete '{it.name}'?") == QMessageBox.Yes:
            self.db.delete_item(it.id)
            self._reload()

    def _load_time_breakdown(self):
        info = get_time_breakdown_summary()
        if info["rows"] == 0:
            QMessageBox.information(
                self, "No Time Breakdown",
                "No Time Breakdown project found.\n"
                "Create one in the '⏱️ Time & Evaluation' tab first "
                "(Time Breakdown button), then load again.")
            return
        self.spin_days.setValue(info["total_days"])
        # auto-fill rig day rate from CBS catalog if available
        for it in self._loaded_all:
            if it.name.strip().lower() == "drilling rig day rate" and it.unit_price:
                self.spin_rig_rate.setValue(it.unit_price)
            if it.name.strip().lower() == "spread cost" and it.unit_price:
                self.spin_spread.setValue(it.unit_price)
        self.lbl_tb_info.setText(
            f"Project: {info['name'] or '—'}  |  Well: "
            f"{info['well_name'] or '—'}\n"
            f"Total: {info['total_days']:.1f} days "
            f"(+ contingency {info['contingency_days']:.1f} days) | "
            f"{info['rows']} operation rows")
        self._refresh_summary()

    def _export_afe(self):
        self._save()
        default = str(Path.home() / "AFE_Cost_Breakdown.docx")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save AFE / CBS", default, "Word Document (*.docx)")
        if not path:
            return
        try:
            export_afe_docx(
                path,
                self._loaded_all,
                total_days=self.spin_days.value(),
                rig_day_rate=self.spin_rig_rate.value(),
                spread_day_rate=self.spin_spread.value(),
                well_depth_m=self.spin_depth.value(),
                currency=self.cmb_currency.currentText())
            QMessageBox.information(
                self, "Exported", f"AFE / CBS saved:\n{path}")
        except Exception as e:
            import traceback
            QMessageBox.critical(
                self, "Export Error",
                f"{e}\n\n{traceback.format_exc()[-400:]}")

    def get_afe_data(self) -> dict:
        """برای استفاده در ویزارد/خروجی‌ها"""
        self._save()
        return build_afe(
            self._loaded_all,
            total_days=self.spin_days.value(),
            rig_day_rate=self.spin_rig_rate.value(),
            spread_day_rate=self.spin_spread.value(),
            well_depth_m=self.spin_depth.value(),
            currency=self.cmb_currency.currentText())
