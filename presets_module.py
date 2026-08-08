# presets_module.py - COMPLETE REWRITE - No circular import
# ============================================================

import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QGroupBox,
    QSplitter, QWidget, QScrollArea, QFrame, QMessageBox,
    QGridLayout, QTabWidget, QApplication
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor


# ============================================================
# STYLES
# ============================================================

PRESET_STYLE = """
QDialog { background-color: #0a0f1a; color: #e0e0e0; }
QWidget { background-color: #0a0f1a; color: #e0e0e0;
          font-family: 'Segoe UI'; font-size: 11px; }
QLabel { color: #c0ccd8; }
QLabel#title { color: #e94560; font-size: 22px; font-weight: bold; }
QLabel#subtitle { color: #8899aa; font-size: 11px; }
QLabel#secTitle { color: #e94560; font-size: 13px; font-weight: bold; }
QLabel#key { color: #8899aa; font-size: 10px; }
QLabel#val { color: #ffffff; font-size: 11px; font-weight: bold; }
QListWidget {
    background-color: #0d1525; border: 2px solid #1a2744;
    border-radius: 8px; color: #d0d8e0; padding: 4px; outline: none;
}
QListWidget::item {
    padding: 10px 12px; border-radius: 5px; margin: 2px;
    border-bottom: 1px solid #1a2744;
}
QListWidget::item:hover { background-color: #152238; border: 1px solid #e94560; }
QListWidget::item:selected {
    background-color: #1a2744; border: 2px solid #e94560; color: #ffffff;
}
QGroupBox {
    border: 2px solid #1a2744; border-radius: 8px;
    margin-top: 12px; padding-top: 18px;
    font-weight: bold; color: #e94560; background: #0d1525;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px;
                   padding: 0 8px; color: #e94560; }
QTextEdit {
    background-color: #0d1525; border: 1px solid #1a2744;
    border-radius: 5px; color: #c0ccd8; padding: 8px; font-size: 10px;
}
QTabWidget::pane { border: 1px solid #1a2744; background: #0d1525; }
QTabBar::tab { background: #0a0f1a; color: #8899aa;
               padding: 7px 14px; border-radius: 4px 4px 0 0; }
QTabBar::tab:selected { background: #1a2744; color: #e94560;
                         border-bottom: 2px solid #e94560; }
QPushButton {
    background-color: #0f3460; color: #fff; border: none;
    border-radius: 6px; padding: 10px 24px; font-weight: bold;
}
QPushButton:hover { background-color: #1a5276; }
QPushButton#loadBtn {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #e94560, stop:1 #c0392b);
    font-size: 14px; padding: 14px 40px; min-height: 44px;
}
QPushButton#loadBtn:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #ff6b81, stop:1 #e74c3c);
}
QPushButton#loadBtn:disabled { background: #2c3e50; color: #7f8c8d; }
QPushButton#cancelBtn {
    background: #1a2744; color: #a0b0c0; border: 1px solid #2c3e50;
    padding: 14px 30px;
}
QPushButton#cancelBtn:hover { background: #2c3e50; color: #fff; }
QScrollArea { border: none; background: transparent; }
"""


# ============================================================
# INFO CARD
# ============================================================

class PresetInfoCard(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(6)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.setWidget(self.container)

    def _clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _sep(self):
        f = QFrame()
        f.setFrameShape(QFrame.HLine)
        f.setStyleSheet("background:#1a2744; max-height:1px; margin:4px 0;")
        self.layout.addWidget(f)

    def _lbl(self, text, obj_name="", wrap=False):
        l = QLabel(text)
        if obj_name:
            l.setObjectName(obj_name)
        if wrap:
            l.setWordWrap(True)
        self.layout.addWidget(l)
        return l

    def show_project(self, project, meta):
        self._clear()

        # Header
        self._lbl(meta.get('name', ''), "secTitle")
        self._lbl(meta.get('description', ''), "subtitle", wrap=True)
        self._sep()

        ci = project.company_info
        wi = project.well_info

        # Key metrics grid
        grid = QGridLayout()
        grid.setSpacing(5)
        items = [
            ("Operator", ci.operator_name),
            ("Well Name", ci.well_name),
            ("Field", ci.field_name),
            ("Country", ci.country),
            ("Rig", ci.rig_name),
            ("Well Type", wi.well_type),
            ("TD (MD)", f"{wi.total_depth_md:,.0f} ft"),
            ("TD (TVD)", f"{wi.total_depth_tvd:,.0f} ft"),
            ("Water Depth", f"{wi.water_depth:,.0f} ft" if wi.water_depth else "Land"),
            ("Target", wi.target_formation or "-"),
            ("BHT", f"{wi.expected_reservoir_temperature:.0f} °F"),
            ("H₂S", f"{wi.expected_h2s_concentration:.1f}%" if wi.expected_h2s_concentration > 0 else "None"),
            ("Res. Pressure", f"{wi.expected_reservoir_pressure:,.0f} psi"),
            ("NACE", "Required" if wi.nace_required else "Not Req."),
        ]
        for i, (k, v) in enumerate(items):
            r, c = i // 2, (i % 2) * 2
            kl = QLabel(k + ":")
            kl.setObjectName("key")
            vl = QLabel(str(v))
            vl.setObjectName("val")
            grid.addWidget(kl, r, c)
            grid.addWidget(vl, r, c + 1)

        gw = QWidget()
        gw.setLayout(grid)
        self.layout.addWidget(gw)
        self._sep()

        # Tabs
        tabs = QTabWidget()
        tabs.setMaximumHeight(320)

        def make_tab(html):
            te = QTextEdit()
            te.setReadOnly(True)
            te.setHtml(html)
            return te

        # Casing tab
        ch = "<table style='width:100%;font-size:10px;color:#c0ccd8'>"
        ch += "<tr style='color:#e94560;font-weight:bold'><td>Section</td><td>Hole</td><td>Casing</td><td>Grade</td><td>Depth MD</td></tr>"
        for cd in project.casing_design:
            ch += f"<tr><td>{cd.section_name}</td><td>{cd.hole_size}\"</td><td>{cd.casing_od}\"</td><td>{cd.casing_grade}</td><td>{cd.setting_depth_md:,.0f} ft</td></tr>"
        ch += "</table>"
        tabs.addTab(make_tab(ch), f"🔧 Casing ({len(project.casing_design)})")

        # Formation tab
        fh = "<table style='width:100%;font-size:9px;color:#c0ccd8'>"
        fh += "<tr style='color:#e94560;font-weight:bold'><td>Formation</td><td>Type</td><td>MD (ft)</td><td>PP (ppg)</td><td>FG (ppg)</td></tr>"
        for ft in project.formation_tops:
            fh += f"<tr><td>{ft.name}</td><td>{ft.formation_type}</td><td>{ft.md_top:,.0f}-{ft.md_bottom:,.0f}</td><td>{ft.pore_pressure_top:.1f}-{ft.pore_pressure_bottom:.1f}</td><td>{ft.fracture_gradient_top:.1f}-{ft.fracture_gradient_bottom:.1f}</td></tr>"
        fh += "</table>"
        tabs.addTab(make_tab(fh), f"🪨 Formations ({len(project.formation_tops)})")

        # Mud tab
        mh = ""
        for mp in project.mud_programs:
            mh += f"<p style='color:#e94560;font-weight:bold'>▸ {mp.section_name} ({mp.hole_size}\")</p>"
            mh += f"<p style='color:#c0ccd8;font-size:10px'>Type: {mp.mud_type}<br>MW: {mp.mud_weight_in:.1f} → {mp.mud_weight_out:.1f} ppg | PV: {mp.plastic_viscosity:.0f} cP | YP: {mp.yield_point:.0f}</p>"
        tabs.addTab(make_tab(mh), f"🧪 Mud ({len(project.mud_programs)})")

        # BHA tab
        bh = ""
        for b in project.bha_designs:
            bh += f"<p style='color:#e94560;font-weight:bold'>▸ BHA #{b.bha_number} - {b.section_name} ({b.hole_size}\")</p>"
            bh += f"<p style='color:#c0ccd8;font-size:10px'>{b.bha_type} | Bit: {b.bit_size}\" {b.bit_type}<br>"
            if b.motor_type:
                bh += f"Motor: {b.motor_type}<br>"
            if b.rss_type:
                bh += f"RSS: {b.rss_type}<br>"
            bh += f"WOB: {b.recommended_wob} | RPM: {b.recommended_rpm}</p>"
        tabs.addTab(make_tab(bh), f"⚙️ BHA ({len(project.bha_designs)})")

        # Hazards tab
        colors = {'Critical': '#e74c3c', 'High': '#e67e22',
                  'Medium': '#f1c40f', 'Low': '#27ae60'}
        hzh = ""
        for h in project.hazards:
            c = colors.get(h.severity, '#fff')
            hzh += f"<p style='color:{c};font-weight:bold'>▸ [{h.severity}] {h.hazard_type} ({h.md_top:,.0f}-{h.md_bottom:,.0f} ft)</p>"
            hzh += f"<p style='color:#c0ccd8;font-size:9px'>{h.description[:120]}...</p>"
        tabs.addTab(make_tab(hzh), f"⚠️ Hazards ({len(project.hazards)})")

        # Time tab
        th = "<table style='width:100%;font-size:10px;color:#c0ccd8'>"
        th += "<tr style='color:#e94560;font-weight:bold'><td>Section</td><td>Operation</td><td>Days</td><td>Cumulative</td></tr>"
        for te in project.time_estimates:
            th += f"<tr><td>{te.section_name}</td><td>{te.operation[:35]}</td><td>{te.total_section_days:.1f}</td><td><b>{te.cumulative_days:.1f}</b></td></tr>"
        th += "</table>"
        if project.time_estimates:
            total = project.time_estimates[-1].cumulative_days
            th += f"<p style='color:#e94560;font-size:13px;font-weight:bold;text-align:center'>Total: {total:.0f} Days</p>"
        tabs.addTab(make_tab(th), "⏱️ Time")

        # BOP tab
        bop = project.bop_stack
        wc = project.well_control
        boph = f"<p style='color:#c0ccd8;font-size:10px'>Type: {bop.bop_type}<br>WP: {bop.working_pressure:,.0f} psi | Bore: {bop.bore_size}\"<br>Manufacturer: {bop.manufacturer}<br>Pipe Rams: {bop.pipe_ram_size}<br>Shear: {'Yes' if bop.shear_ram else 'No'} | Annular: {bop.annular_preventer_size}\"</p>"
        boph += f"<p style='color:#e94560;font-weight:bold'>Well Control:</p><p style='color:#c0ccd8;font-size:10px'>Method: {wc.kill_method}<br>MAASP: {wc.maasp_surface:,.0f} psi | KT: {wc.kick_tolerance:.0f} bbl<br>SPR#1: {wc.slow_pump_rate_1:.0f} SPM @ {wc.slow_pump_pressure_1:,.0f} psi</p>"
        tabs.addTab(make_tab(boph), "🔴 BOP/WC")

        self.layout.addWidget(tabs)
        self._sep()

        # Stats
        stats = QLabel(
            f"📊 {len(project.formation_tops)} Formations | "
            f"{len(project.casing_design)} Casings | "
            f"{len(project.mud_programs)} Mud Systems | "
            f"{len(project.bha_designs)} BHAs | "
            f"{len(project.cement_design)} Cement Jobs | "
            f"{len(project.hazards)} Hazards"
        )
        stats.setObjectName("subtitle")
        stats.setWordWrap(True)
        self.layout.addWidget(stats)
        self.layout.addStretch()


# ============================================================
# PRESET SELECTOR DIALOG
# ============================================================

class PresetSelectorDialog(QDialog):
    presetSelected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🛢️ Professional Well Templates")
        self.setMinimumSize(1150, 780)
        self.setStyleSheet(PRESET_STYLE)
        self.selected_project = None
        self.presets = {}
        self._load_all_presets()
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        t = QLabel("🛢️  SELECT PROFESSIONAL WELL TEMPLATE")
        t.setObjectName("title")
        t.setAlignment(Qt.AlignCenter)
        layout.addWidget(t)

        sub = QLabel("Select a template to load all parameters into the application. You can then review and edit before generating.")
        sub.setObjectName("subtitle")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        layout.addWidget(sub)

        # Splitter
        splitter = QSplitter(Qt.Horizontal)

        # Left: List
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("Available Templates:")
        lbl.setObjectName("secTitle")
        ll.addWidget(lbl)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(320)
        self.list_widget.setMaximumWidth(420)

        for key, meta in self.presets.items():
            item = QListWidgetItem()
            item.setData(Qt.UserRole, key)
            item.setText(
                f"{meta['icon']}  {meta['name']}\n"
                f"     📍 {meta['region']} | 📏 TD: {meta['td']}\n"
                f"     🔹 {meta['well_type']}"
            )
            item.setSizeHint(QSize(0, 72))
            self.list_widget.addItem(item)

        self.list_widget.currentItemChanged.connect(self._on_select)
        ll.addWidget(self.list_widget)
        splitter.addWidget(left)

        # Right: Info
        self.info_card = PresetInfoCard()
        splitter.addWidget(self.info_card)
        splitter.setSizes([370, 780])
        layout.addWidget(splitter)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_cancel = QPushButton("✖  Cancel")
        self.btn_cancel.setObjectName("cancelBtn")
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_load = QPushButton("📥  LOAD TEMPLATE INTO APPLICATION")
        self.btn_load.setObjectName("loadBtn")
        self.btn_load.setEnabled(False)
        self.btn_load.clicked.connect(self._do_load)
        btn_row.addWidget(self.btn_load)

        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _on_select(self, current, previous):
        if not current:
            self.btn_load.setEnabled(False)
            return
        key = current.data(Qt.UserRole)
        try:
            self.selected_project = self.presets[key]['generator']()
            self.info_card.show_project(self.selected_project, self.presets[key])
            self.btn_load.setEnabled(True)
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Error generating preview",
                                 f"{str(e)}\n\n{traceback.format_exc()[-800:]}")

    def _do_load(self):
        if self.selected_project:
            self.presetSelected.emit(self.selected_project)
            self.accept()

    # ============================================================
    # PRESET REGISTRY
    # ============================================================

    def _load_all_presets(self):
        self.presets = {
            'me_dev_h2s': {
                'name': 'Middle East - H₂S Sour Development Well',
                'icon': '🏜️',
                'region': 'Abu Dhabi, UAE (ADNOC Block 4)',
                'td': '14,850 ft MD / 11,200 ft TVD',
                'well_type': 'Directional J-Type | 38° @ 42.5°',
                'description': 'High-pressure sour development well targeting Arab-D. '
                               'H₂S 4.2%, CO₂ 2.8%. NACE compliant. '
                               '4 casing strings. OBM in reservoir.',
                'generator': self._preset_me_h2s,
            },
            'me_dev_sweet': {
                'name': 'Middle East - Sweet Oil Development Well',
                'icon': '🛢️',
                'region': 'Saudi Arabia (Ghawar Field)',
                'td': '11,500 ft MD / 10,200 ft TVD',
                'well_type': 'Directional S-Type | 25°',
                'description': 'Sweet oil development targeting Khuff Formation. '
                               'No H₂S. KCl/Polymer WBM. '
                               '3 casing strings. Saudi Aramco standards.',
                'generator': self._preset_me_sweet,
            },
            'offshore_jackup': {
                'name': 'Offshore - Jack-Up Exploration Well',
                'icon': '🌊',
                'region': 'Persian Gulf, Qatar (180 ft WD)',
                'td': '13,200 ft MD',
                'well_type': 'Vertical | 5 Casing Strings + Liner',
                'description': 'Offshore exploration from Jack-Up in 180 ft water. '
                               'Khuff gas target. H₂S 1.5%. SBM in reservoir. '
                               'Full evaluation + DST.',
                'generator': self._preset_jackup,
            },
            'north_sea_hpht': {
                'name': 'North Sea - HPHT Exploration Well',
                'icon': '🏔️',
                'region': 'Norwegian North Sea (NCS)',
                'td': '18,500 ft MD',
                'well_type': 'Vertical HPHT | 16,000 psi / 380°F',
                'description': 'HPHT exploration well targeting Brent Group. '
                               '15K BOP. 5 casing strings. '
                               'NORSOK D-010 standards.',
                'generator': self._preset_hpht,
            },
            'gom_deepwater': {
                'name': 'Gulf of Mexico - Deepwater Well',
                'icon': '🚢',
                'region': 'GOM Deepwater (5,000 ft WD)',
                'td': '25,000 ft MD',
                'well_type': 'Directional | Subsea BOP | 7 Strings',
                'description': 'Deepwater exploration from drillship. '
                               'Lower Tertiary target. 18,000 psi reservoir. '
                               'Subsea 15K BOP. SBM.',
                'generator': self._preset_deepwater,
            },
            'horizontal_shale': {
                'name': 'Unconventional - Horizontal Shale Well',
                'icon': '↔️',
                'region': 'Permian Basin, Texas, USA',
                'td': '20,500 ft MD (10,000 ft lateral)',
                'well_type': 'Horizontal | Wolfcamp A',
                'description': 'Pad-drilled horizontal well targeting Wolfcamp A. '
                               '10,000 ft lateral. Fast-track 18-day program. '
                               'Modern Permian Basin practices.',
                'generator': self._preset_horizontal,
            },
            'erd_well': {
                'name': 'Extended Reach Drilling (ERD)',
                'icon': '🎯',
                'region': 'Sakhalin Island, Russia',
                'td': '40,000 ft MD (DR > 5:1)',
                'well_type': 'ERD | 82° Inclination',
                'description': 'World-class ERD well from onshore to offshore target. '
                               '82° inclination. 5 casing strings. '
                               'T&D management critical.',
                'generator': self._preset_erd,
            },
            'geothermal': {
                'name': 'Geothermal Energy Well',
                'icon': '🌋',
                'region': 'Iceland / East Africa Rift',
                'td': '9,800 ft MD',
                'well_type': 'Vertical | T > 600°F',
                'description': 'Supercritical geothermal well targeting volcanic reservoir. '
                               'BHT > 600°F. Special HT alloy materials. '
                               'Unique drilling fluids program.',
                'generator': self._preset_geothermal,
            },
        }

    # ============================================================
    # PRESET GENERATORS - imports are INSIDE each function
    # ============================================================

    def _preset_me_h2s(self):
        """Middle East H2S Sour Development Well"""
        from main import (
            WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, HazardEntry, CasingDesign,
            CementDesign, BHADesign, MudProgram,
            DirectionalPlan, BOPStack, WellControlData,
            RigSpecification, DrillingParameters, TimeEstimate
        )

        p = WellProject()

        p.company_info = CompanyInfo(
            operator_name="ARABIAN GULF PETROLEUM COMPANY (AGPC)",
            contractor_name="NATIONAL OILWELL DRILLING COMPANY (NODC)",
            field_name="AL-SHAHEEN FIELD",
            well_name="ASH-0247-H1",
            well_number="0247",
            pad_name="PAD-18 (Cluster E)",
            rig_name="NODC RIG-112 (2000 HP AC/VFD)",
            rig_type="Land Rig",
            country="UNITED ARAB EMIRATES",
            region="Abu Dhabi - ADNOC Block 4",
            block_license="ADNOC Concession Block 4",
            api_number="UAE-ADNOC-ASH-2024-0247",
            spud_date="2024-09-15",
            prepared_by="Eng. Ahmad K. Al-Rashidi, Sr. Drilling Engineer",
            reviewed_by="Eng. Mohammed S. Al-Fahad, Drilling Superintendent",
            approved_by="Eng. Khalid A. Al-Mansouri, Drilling Manager",
            revision="A",
            document_number="AGPC-DRL-ASH0247-PRG-2024-001",
            classification="CONFIDENTIAL - RESTRICTED DISTRIBUTION"
        )

        p.well_info = WellGeneralInfo(
            well_type="Development",
            well_profile="Directional J-Type",
            total_depth_md=14850,
            total_depth_tvd=11200,
            water_depth=0,
            air_gap=0,
            ground_elevation=142.5,
            kb_elevation=32.8,
            magnetic_declination=2.18,
            grid_convergence=0.92,
            surface_latitude="24° 28' 15.34\" N",
            surface_longitude="54° 22' 48.72\" E",
            target_latitude="24° 29' 02.15\" N",
            target_longitude="54° 23' 18.45\" E",
            coordinate_system="WGS 84 / UTM Zone 40N",
            target_formation="Arab-D Reservoir (Upper Unit - Zone 2B)",
            target_zone="Arab-D Zone 2B - Dolomitized Grainstone",
            expected_reservoir_pressure=5120,
            expected_reservoir_temperature=252,
            expected_h2s_concentration=4.2,
            expected_co2_concentration=2.8,
            nace_required=True,
            wellhead_type="Cameron 13-5/8\" x 10M Compact",
            xmas_tree_type="Cameron Conventional Tree 10K"
        )

        p.formation_tops = [
            FormationTop(name="Recent / Quaternary", formation_type="Sand",
                md_top=0, md_bottom=180, tvd_top=0, tvd_bottom=180,
                pore_pressure_top=8.55, pore_pressure_bottom=8.55,
                fracture_gradient_top=13.0, fracture_gradient_bottom=13.5,
                overburden_gradient=15.5, temperature_top=90, temperature_bottom=100,
                drillability="Very Easy", directional_tendency="Neutral",
                remarks="Unconsolidated. Shallow water flow risk. ROP < 60 ft/hr."),
            FormationTop(name="Dibdibba Formation", formation_type="Sandstone",
                md_top=180, md_bottom=680, tvd_top=180, tvd_bottom=680,
                pore_pressure_top=8.55, pore_pressure_bottom=8.60,
                fracture_gradient_top=13.5, fracture_gradient_bottom=14.2,
                overburden_gradient=15.8, temperature_top=100, temperature_bottom=118,
                drillability="Easy", directional_tendency="Neutral",
                remarks="Freshwater aquifer zone. Surface casing seat candidate."),
            FormationTop(name="Fars / Lower Fars", formation_type="Marl",
                md_top=680, md_bottom=1450, tvd_top=680, tvd_bottom=1450,
                pore_pressure_top=8.60, pore_pressure_bottom=8.65,
                fracture_gradient_top=14.2, fracture_gradient_bottom=14.8,
                overburden_gradient=16.2, temperature_top=118, temperature_bottom=140,
                drillability="Easy", directional_tendency="Neutral",
                remarks="Marl and clay interbedded with limestone stringers."),
            FormationTop(name="Dammam Formation", formation_type="Limestone",
                md_top=1450, md_bottom=2850, tvd_top=1450, tvd_bottom=2850,
                pore_pressure_top=8.65, pore_pressure_bottom=8.75,
                fracture_gradient_top=14.8, fracture_gradient_bottom=15.2,
                overburden_gradient=16.5, temperature_top=140, temperature_bottom=168,
                drillability="Medium", directional_tendency="Neutral",
                remarks="⚠ Lost circulation in fractured zones. LCM ready. "
                        "Offset ASH-0198: 15 bbl/hr at 2100-2300 ft."),
            FormationTop(name="Rus Formation", formation_type="Anhydrite",
                md_top=2850, md_bottom=3650, tvd_top=2850, tvd_bottom=3650,
                pore_pressure_top=8.75, pore_pressure_bottom=8.85,
                fracture_gradient_top=15.2, fracture_gradient_bottom=15.6,
                overburden_gradient=17.0, temperature_top=168, temperature_bottom=182,
                drillability="Medium", directional_tendency="Neutral",
                remarks="Anhydrite/marl interbedded. Bit balling in marl."),
            FormationTop(name="Umm Er Radhuma (UER)", formation_type="Limestone",
                md_top=3650, md_bottom=5800, tvd_top=3650, tvd_bottom=5500,
                pore_pressure_top=8.85, pore_pressure_bottom=9.20,
                fracture_gradient_top=15.6, fracture_gradient_bottom=16.0,
                overburden_gradient=17.5, temperature_top=182, temperature_bottom=208,
                drillability="Medium", directional_tendency="Build",
                remarks="KOP at 4200 ft. ⚠ SEVERE LOSSES at 4800-5200 ft. "
                        "ASH-0212: total losses, 200 bbl cement plug required."),
            FormationTop(name="Simsima Formation", formation_type="Limestone",
                md_top=5800, md_bottom=7200, tvd_top=5500, tvd_bottom=6600,
                pore_pressure_top=9.20, pore_pressure_bottom=9.50,
                fracture_gradient_top=16.0, fracture_gradient_bottom=16.5,
                overburden_gradient=18.0, temperature_top=208, temperature_bottom=225,
                drillability="Hard", directional_tendency="Hold",
                remarks="Dense limestone. ROP 8-15 ft/hr. Monitor bit wear."),
            FormationTop(name="Aruma Formation", formation_type="Limestone",
                md_top=7200, md_bottom=8500, tvd_top=6600, tvd_bottom=7500,
                pore_pressure_top=9.50, pore_pressure_bottom=9.80,
                fracture_gradient_top=16.5, fracture_gradient_bottom=16.8,
                overburden_gradient=18.5, temperature_top=225, temperature_bottom=235,
                drillability="Hard", directional_tendency="Hold",
                remarks="Argillaceous limestone with chert nodules."),
            FormationTop(name="Wasia Formation", formation_type="Sandstone",
                md_top=8500, md_bottom=10200, tvd_top=7500, tvd_bottom=8600,
                pore_pressure_top=9.80, pore_pressure_bottom=10.20,
                fracture_gradient_top=16.8, fracture_gradient_bottom=17.0,
                overburden_gradient=18.8, temperature_top=235, temperature_bottom=242,
                drillability="Medium", directional_tendency="Drop",
                remarks="Mauddud/Nahr Umr. Reactive shale. Differential sticking risk."),
            FormationTop(name="Shuaiba Formation", formation_type="Limestone",
                md_top=10200, md_bottom=11400, tvd_top=8600, tvd_bottom=9400,
                pore_pressure_top=10.20, pore_pressure_bottom=10.50,
                fracture_gradient_top=17.0, fracture_gradient_bottom=17.2,
                overburden_gradient=19.0, temperature_top=242, temperature_bottom=245,
                drillability="Hard", directional_tendency="Hold",
                remarks="Dense low-porosity limestone. ROP 5-10 ft/hr."),
            FormationTop(name="Kharaib Formation", formation_type="Limestone",
                md_top=11400, md_bottom=12800, tvd_top=9400, tvd_bottom=10200,
                pore_pressure_top=10.50, pore_pressure_bottom=10.80,
                fracture_gradient_top=17.0, fracture_gradient_bottom=17.2,
                overburden_gradient=19.2, temperature_top=245, temperature_bottom=248,
                drillability="Hard", directional_tendency="Hold",
                remarks="Dense dolomitic limestone. H₂S may appear at top."),
            FormationTop(name="Arab-D Reservoir", formation_type="Dolomite",
                md_top=12800, md_bottom=14850, tvd_top=10200, tvd_bottom=11200,
                pore_pressure_top=10.80, pore_pressure_bottom=10.95,
                fracture_gradient_top=17.0, fracture_gradient_bottom=17.5,
                overburden_gradient=19.5, temperature_top=248, temperature_bottom=255,
                drillability="Medium-Hard", directional_tendency="Hold",
                remarks="🎯 PRIMARY TARGET - Zone 2B. Phi=15-22%. "
                        "H₂S=4.2%, CO₂=2.8%. ALL NACE MR-0175 REQUIRED. "
                        "Offset ASH-0231: IP=4,500 BOPD."),
        ]

        p.hazards = [
            HazardEntry(hazard_type="Shallow Water Flow",
                md_top=0, md_bottom=400, severity="Medium", probability="Possible",
                description="Shallow aquifer in Recent/Dibdibba sands.",
                mitigation="Diverter installed. ROP < 60 ft/hr in top 400 ft.",
                contingency="Activate diverter. Set conductor immediately.",
                reference_well="ASH-0145 (water flow at 280 ft)"),
            HazardEntry(hazard_type="Lost Circulation",
                md_top=1450, md_bottom=2850, severity="Medium", probability="Likely",
                description="Fractured Dammam Fm. ASH-0198: 15 bbl/hr losses.",
                mitigation="Fine CaCO₃ 5 ppb in mud. LCM pill ready.",
                contingency="Spot LCM pill. Cement squeeze if severe.",
                reference_well="ASH-0198"),
            HazardEntry(hazard_type="Lost Circulation",
                md_top=4800, md_bottom=5200, severity="High", probability="Almost Certain",
                description="SEVERE vugular losses in UER. 3/5 offsets had total losses.",
                mitigation="15 ppb LCM pre-treat. Reduce flow 20%. 300 bbl cement ready.",
                contingency="100 bbl LCM pill. Cement plug 100-200 ft. WOC 12 hrs.",
                reference_well="ASH-0212 (total losses, 200 bbl cement plug)"),
            HazardEntry(hazard_type="Stuck Pipe",
                md_top=8500, md_bottom=10200, severity="High", probability="Possible",
                description="Differential sticking in Mauddud sands. Overbalance > 1000 psi.",
                mitigation="Minimize static time < 5 min. Lubricant 3-5%. Keep pipe moving.",
                contingency="Work pipe. Oil pill 100 bbl. Soak 4-8 hrs. Free point if needed.",
                reference_well="ASH-0189 (stuck at 9420 ft, freed with oil pill)"),
            HazardEntry(hazard_type="Sloughing Shale",
                md_top=9600, md_bottom=10200, severity="Medium", probability="Likely",
                description="Nahr Umr reactive shale. Swelling clays. Wellbore enlargement.",
                mitigation="KCl > 5%. Glycol in mud. Hi-vis sweeps every 500 ft.",
                contingency="Increase MW 0.2-0.3 ppg. Increase KCl to 7%. Convert to OBM.",
                reference_well="ASH-0223"),
            HazardEntry(hazard_type="H2S Gas",
                md_top=12800, md_bottom=14850, severity="Critical", probability="Almost Certain",
                description="H₂S 4.2% (42,000 ppm) in Arab-D. CO₂ 2.8%. IDLH condition.",
                mitigation="ALL NACE MR-0175 compliant. H₂S detectors. SCBA. Buddy system. ZnO 10-15 ppb in mud.",
                contingency="10ppm: Alert. 20ppm: Alarm/SCBA. 50ppm: Evacuate. Hospital: 40 min.",
                reference_well="ASH-0231 (H₂S 4.1% during DST, no incidents)"),
            HazardEntry(hazard_type="High Temperature",
                md_top=10200, md_bottom=14850, severity="Medium", probability="Almost Certain",
                description="BHT 255°F. Impact on tools, mud, cement.",
                mitigation="HT-rated tools (>300°F). HT mud additives. HT cement.",
                contingency="POOH if tool failure. Adjust mud chemistry."),
            HazardEntry(hazard_type="Kick / Well Control",
                md_top=12800, md_bottom=14850, severity="Critical", probability="Possible",
                description="Reservoir PP 5120 psi (10.95 ppg). Narrow MW window. H₂S makes kick critical.",
                mitigation="MW 0.3-0.5 ppg above PP. Monitor pit volume. Flow check every connection.",
                contingency="Hard shut-in. W&W method. Kill mud on standby.",
                reference_well="ASH-0178 (2 bbl gas kick at 13200 ft, killed in 4 hrs)"),
            HazardEntry(hazard_type="Anti-Collision Risk",
                md_top=4200, md_bottom=14850, severity="Medium", probability="Unlikely",
                description="ASH-0231, 0235, 0238 on PAD-18. Min 150 ft separation.",
                mitigation="Gyro surveys at all shoes. Compass AC software. SF > 1.5.",
                contingency="Stop if SF < 1.5. Definitive survey. Trajectory correction."),
        ]

        p.casing_design = [
            CasingDesign(section_name="Conductor", section_type="Conductor",
                hole_size=36, casing_od=30, casing_id=28.0, casing_weight=309.72,
                casing_grade="X-56", casing_connection="Welded (AWS D1.1)",
                setting_depth_md=300, setting_depth_tvd=300,
                top_of_cement_md=0, cement_to_surface=True,
                burst_rating=2800, collapse_rating=1100, tensile_rating=550000,
                drift_id=28.0, min_design_factor_burst=1.10,
                min_design_factor_collapse=1.10, min_design_factor_tension=1.60,
                centralizer_type="Rigid", centralizer_spacing=40,
                float_collar_depth=260, float_shoe_type="Guide Shoe",
                number_of_joints=8, remarks="Drive or drill & cement."),
            CasingDesign(section_name="Surface", section_type="Surface",
                hole_size=26, casing_od=20, casing_id=18.73, casing_weight=133.0,
                casing_grade="K-55", casing_connection="BTC",
                setting_depth_md=2900, setting_depth_tvd=2900,
                top_of_cement_md=0, cement_to_surface=True,
                burst_rating=3060, collapse_rating=1490, tensile_rating=1161000,
                drift_id=18.63, min_design_factor_burst=1.10,
                min_design_factor_collapse=1.10, min_design_factor_tension=1.80,
                centralizer_type="Bow-Spring (Weatherford Zip-Set)", centralizer_spacing=60,
                float_collar_depth=2840, float_shoe_type="Float Shoe w/ Circulation Ports",
                number_of_joints=72, scratchers=True,
                remarks="Cement to surface - regulatory requirement."),
            CasingDesign(section_name="Intermediate", section_type="Intermediate",
                hole_size=17.5, casing_od=13.375, casing_id=12.415, casing_weight=72.0,
                casing_grade="N-80 (Type 1)", casing_connection="BTC",
                setting_depth_md=10200, setting_depth_tvd=8600,
                top_of_cement_md=6000,
                burst_rating=5020, collapse_rating=2670, tensile_rating=1556000,
                drift_id=12.259, min_design_factor_burst=1.10,
                min_design_factor_collapse=1.10, min_design_factor_tension=1.80,
                centralizer_type="Bow-Spring + Rigid (deviated)", centralizer_spacing=50,
                float_collar_depth=10140,
                float_shoe_type="Float Shoe w/ PDC Drillable Insert",
                number_of_joints=254, scratchers=True,
                remarks="Critical - isolates loss zones & build section. CBL/VDL required."),
            CasingDesign(section_name="Production", section_type="Production",
                hole_size=12.25, casing_od=9.625, casing_id=8.535, casing_weight=53.5,
                casing_grade="L-80 (13Cr Modified)", casing_connection="VAM TOP HC",
                setting_depth_md=14850, setting_depth_tvd=11200,
                top_of_cement_md=8500,
                burst_rating=8750, collapse_rating=5300, tensile_rating=1310000,
                drift_id=8.379, min_design_factor_burst=1.15,
                min_design_factor_collapse=1.125, min_design_factor_tension=1.80,
                centralizer_type="Bow-Spring Turbulizer", centralizer_spacing=35,
                float_collar_depth=14780,
                float_shoe_type="Auto-Fill Float Shoe (PDC Drillable)",
                number_of_joints=370, scratchers=True,
                remarks="⚠ SOUR SERVICE. NACE MR-0175. VAM TOP HC gas-tight connections. "
                        "CBL/CBIL across full reservoir."),
        ]

        p.cement_design = [
            CementDesign(section_name="Surface",
                casing_od=20, hole_size=26, shoe_depth_md=2900, toc_md=0,
                lead_slurry_type="API Class G + 35% Silica + Perlite",
                lead_slurry_density=12.8, lead_slurry_yield=1.52, lead_slurry_volume=480,
                lead_slurry_thickening_time=10, lead_slurry_compressive_strength=450,
                tail_slurry_type="API Class G + 35% Silica (Neat)",
                tail_slurry_density=15.8, tail_slurry_yield=1.15, tail_slurry_volume=150,
                tail_slurry_thickening_time=6, tail_slurry_compressive_strength=2500,
                spacer_type="Weighted Chemical Spacer", spacer_density=10.0, spacer_volume=40,
                wash_type="FW + Surfactant", wash_volume=25,
                displacement_volume=520, displacement_rate=8, max_ecd=14.8,
                excess_percentage=100, woc_time=12, plug_bump_pressure=500,
                cement_additives="HR-25: 0.3%, Halad-344: 0.5%, CFR-3: 0.3%, Silica: 35%, Perlite: 15%",
                cbl_cbil_required=True, remarks="Cement to surface. Reciprocate ±15 ft."),
            CementDesign(section_name="Intermediate",
                casing_od=13.375, hole_size=17.5, shoe_depth_md=10200, toc_md=6000,
                lead_slurry_type="Class G + 35% Silica + 20% Microspheres",
                lead_slurry_density=12.2, lead_slurry_yield=2.05, lead_slurry_volume=620,
                lead_slurry_thickening_time=12, lead_slurry_compressive_strength=280,
                tail_slurry_type="Class G + 35% Silica + Anti-Gas",
                tail_slurry_density=16.0, tail_slurry_yield=1.12, tail_slurry_volume=200,
                tail_slurry_thickening_time=8, tail_slurry_compressive_strength=2800,
                spacer_type="Engineered Spacer (MudPush II)", spacer_density=11.5, spacer_volume=50,
                wash_type="Chemical Wash Package", wash_volume=30,
                displacement_volume=650, displacement_rate=6, max_ecd=16.2,
                excess_percentage=50, woc_time=18, plug_bump_pressure=800,
                cement_additives="HR-25: 0.5%, Halad-413: 0.8%, Anti-Gas (GasStop HT): 2.0%, Silica: 35%",
                cbl_cbil_required=True,
                remarks="Rotate casing 10-15 RPM. ECD critical. CBL required across 6000-10200 ft."),
            CementDesign(section_name="Production",
                casing_od=9.625, hole_size=12.25, shoe_depth_md=14850, toc_md=8500,
                lead_slurry_type="Class G + 35% Silica + Microspheres + H₂S Resistant",
                lead_slurry_density=11.8, lead_slurry_yield=2.15, lead_slurry_volume=520,
                lead_slurry_thickening_time=14, lead_slurry_compressive_strength=220,
                tail_slurry_type="Class G + 40% Silica + Gas Block + Latex",
                tail_slurry_density=16.5, tail_slurry_yield=1.06, tail_slurry_volume=180,
                tail_slurry_thickening_time=10, tail_slurry_compressive_strength=3500,
                spacer_type="Oil-Based Spacer (OBM compatible)", spacer_density=11.5, spacer_volume=40,
                wash_type="Base Oil + Mutual Solvent + Chemical Wash", wash_volume=35,
                displacement_volume=580, displacement_rate=4.5, max_ecd=17.2,
                excess_percentage=50, woc_time=24, plug_bump_pressure=1200,
                cement_additives="HR-25L: 0.8%, Halad-600: 1.0%, GasStop HT: 3.0%, Latex: 1.5 gal/sk, "
                                 "H₂S Scavenger: 5%, Silica: 35-40%, MicroBond: 0.5%",
                cbl_cbil_required=True,
                remarks="⚠ CRITICAL SOUR SERVICE CEMENT. Rotate+reciprocate. "
                        "CBL/CBIL 8500 ft to TD. Acceptance: CBIL > 80% bonded."),
        ]

        p.bha_designs = [
            BHADesign(section_name="Surface", bha_number=1, hole_size=26,
                bha_type="Rotary Assembly", bit_type="Tricone Insert", bit_size=26,
                bit_manufacturer="Baker Hughes", bit_model="XR+ 517",
                bit_nozzles="3x24 (TFA=1.33 sq.in)", bit_tfa=1.33,
                mwd_type="Gyro MWD",
                stabilizer_sizes='26" Near-bit + 26" String',
                recommended_wob="15-35 klbs", recommended_rpm="80-120",
                recommended_flow_rate="900-1100 GPM", recommended_torque="25,000 ft-lbs",
                remarks="Rotary for vertical surface hole."),
            BHADesign(section_name="Intermediate", bha_number=1, hole_size=17.5,
                bha_type="Motor + MWD/LWD (Build Section)", bit_type="PDC", bit_size=17.5,
                bit_manufacturer="NOV (ReedHycalog)", bit_model="TKC76 - 6 Blade 16mm",
                bit_nozzles="5x16, 2x14 (TFA=0.98 sq.in)", bit_tfa=0.98,
                motor_type="Schlumberger PowerPak 9-5/8\" PDM",
                motor_od=9.625, motor_bend=1.50, motor_lobe="7/8",
                motor_flow_range="400-800 GPM",
                mwd_type="Schlumberger PowerPulse",
                lwd_type="Schlumberger EcoScope",
                lwd_sensors="GR, RES (Phase/Att), NPHI, RHOB, PEF, PWD, Caliper",
                stabilizer_sizes='17-1/2" Adj NB + 17-3/8" String',
                recommended_wob="15-40 klbs (Slide:15-25, Rotate:25-40)",
                recommended_rpm="Slide:0 (motor:80-120). Rotate:100-160",
                recommended_flow_rate="700-850 GPM (Motor ΔP: 400-600 psi)",
                recommended_torque="35,000 ft-lbs",
                remarks="Build 3.0°/100ft from KOP 4200 ft. Slide/Rotate=40/60."),
            BHADesign(section_name="Intermediate", bha_number=2, hole_size=17.5,
                bha_type="Rotary Assembly (Hold Section)", bit_type="PDC", bit_size=17.5,
                bit_manufacturer="Baker Hughes", bit_model="Dynamus HCM 5-Blade 19mm",
                bit_nozzles="4x16, 3x14 (TFA=1.10 sq.in)", bit_tfa=1.10,
                mwd_type="PowerPulse MWD", lwd_sensors="GR, RES, NEU, DEN, PWD",
                stabilizer_sizes='17-1/2" NB + 17-3/8" @30ft + 17-1/4" @60ft',
                recommended_wob="25-45 klbs", recommended_rpm="120-180",
                recommended_flow_rate="750-900 GPM", recommended_torque="38,000 ft-lbs",
                remarks="Triple stab rotary for tangent. Hold 38° ±0.5°."),
            BHADesign(section_name="Production", bha_number=1, hole_size=12.25,
                bha_type="RSS + Full LWD Suite", bit_type="PDC", bit_size=12.25,
                bit_manufacturer="Schlumberger (Smith Bits)", bit_model="SDi616 SHARC 6-Blade 13mm",
                bit_nozzles="4x13, 2x12 (TFA=0.68 sq.in)", bit_tfa=0.68,
                rss_type="Schlumberger PowerDrive X6", rss_model="Push-the-bit RSS",
                mwd_type="TeleScope ICE (HT - 300°F rated)",
                lwd_type="PeriScope 15 + EcoScope + SonicScope",
                lwd_sensors="GR, Deep Azimuthal RES (PeriScope), NPHI, RHOB, PEF, "
                            "Sonic (Comp+Shear), PWD, Ultrasonic Caliper, MSE/Dynamics",
                stabilizer_sizes='12-1/8" integrated RSS + 12-1/8" @90ft',
                recommended_wob="8-25 klbs", recommended_rpm="120-200",
                recommended_flow_rate="550-700 GPM (min 600 for RSS)",
                recommended_torque="28,000 ft-lbs",
                remarks="⚠ H₂S ZONE - ALL NACE COMPLIANT. PeriScope for geo-steering. "
                        "Min 600 GPM for RSS. All tools rated 300°F."),
        ]

        p.mud_programs = [
            MudProgram(section_name="Surface", hole_size=26,
                depth_from=300, depth_to=2900,
                mud_type="WBM - KCl/Polymer (Inhibitive)",
                mud_weight_in=9.0, mud_weight_out=9.5,
                funnel_viscosity=50, plastic_viscosity=18, yield_point=16,
                gel_strength_10s=6, gel_strength_10m=12, gel_strength_30m=18,
                fluid_loss=5.0, hthp_fluid_loss=12.0, ph=10.0,
                chlorides=25000, calcium=200, mbt=12, sand_content=0.25,
                total_volume_required=1800, active_volume=900, reserve_volume=900,
                key_additives="KCl 5-7%, PHPA 1.5-2 ppb, PAC-R 2-3 ppb, PAC-L 1-1.5 ppb, "
                              "Starch 3-4 ppb, Soda Ash, Caustic, Biocide",
                ecd_at_shoe=9.8, ecd_at_td=9.9,
                remarks="Monitor Dammam losses. Pre-treat with Fine CaCO₃ 5 ppb."),
            MudProgram(section_name="Intermediate", hole_size=17.5,
                depth_from=2900, depth_to=10200,
                mud_type="WBM - KCl/Polymer/Glycol (High Performance)",
                mud_weight_in=9.5, mud_weight_out=12.5,
                funnel_viscosity=55, plastic_viscosity=24, yield_point=20,
                gel_strength_10s=8, gel_strength_10m=16, gel_strength_30m=22,
                fluid_loss=3.5, hthp_fluid_loss=8.0, ph=10.5,
                chlorides=45000, calcium=300, mbt=18, sand_content=0.15,
                total_volume_required=3200, active_volume=1600, reserve_volume=1600,
                key_additives="KCl 7-10%, PHPA 2-3 ppb, Glycol (ShaleGuard) 3-5%, "
                              "PAC-R 2.5-3.5 ppb, Barite, Lube-167 3-5%, "
                              "Fine CaCO₃ 5-10 ppb, Gilsonite 5 ppb",
                ecd_at_shoe=12.8, ecd_at_td=13.0,
                remarks="⚠ ECD critical through UER loss zone. Reduce flow 20%. "
                        "Wiper trips at 5000, 7000, 8500 ft. Nahr Umr: increase PHPA+Glycol."),
            MudProgram(section_name="Production", hole_size=12.25,
                depth_from=10200, depth_to=14850,
                mud_type="OBM - Mineral Oil Based (Versadril System)",
                mud_weight_in=11.0, mud_weight_out=13.2,
                funnel_viscosity=55, plastic_viscosity=22, yield_point=14,
                gel_strength_10s=7, gel_strength_10m=12, gel_strength_30m=16,
                hthp_fluid_loss=3.5, oil_water_ratio="75/25",
                electrical_stability=900, sand_content=0.08,
                total_volume_required=3500, active_volume=1800, reserve_volume=1700,
                key_additives="Sarapar 147 oil (base), CaCl₂ 25% brine, VersaMul 8-12 ppb, "
                              "VersaCoat 4-6 ppb, VG-69 4-6 ppb, Lime 5-8 ppb, "
                              "VersaFLC 4-6 ppb, Barite, ZnO 10-15 ppb (H₂S scavenger), "
                              "CaCO₃ Fine 20-30 ppb",
                ecd_at_shoe=13.5, ecd_at_td=13.8,
                remarks="⚠ OBM for reservoir. ZnO for H₂S. ES > 800V. OWR 75/25 ±2%. "
                        "HTHP FL < 4 ml. Closed system - no discharge."),
        ]

        p.directional_plan = DirectionalPlan(
            section_name="All Sections",
            survey_tool="MWD Magnetic (PowerPulse) + Gyro at shoes (ISCWSA Rev.5)",
            survey_frequency=90,
            kickoff_point_md=4200, kickoff_point_tvd=4200,
            build_rate=3.00, turn_rate=0.50,
            hold_inclination=38.0, hold_azimuth=42.5,
            target_inclination=38.0, target_azimuth=42.5,
            max_dls=5.50,
            horizontal_displacement=5850, vertical_section=5850,
            closure_distance=5850, closure_direction=42.5,
            anti_collision_wells="ASH-0231 (180 ft sep @8500 ft), ASH-0235 (220 ft @12000 ft), ASH-0238 (310 ft @14000 ft)",
            wellpath_data=[
                {'md': 0, 'tvd': 0, 'inclination': 0, 'azimuth': 0, 'dls': 0, 'ns': '0', 'ew': '0', 'vs': '0', 'closure_dist': '0', 'closure_dir': '0', 'build_turn': '', 'remarks': 'Surface KB'},
                {'md': 2900, 'tvd': 2900, 'inclination': 0, 'azimuth': 0, 'dls': 0, 'ns': '0', 'ew': '0', 'vs': '0', 'closure_dist': '0', 'closure_dir': '0', 'build_turn': '', 'remarks': '20" Shoe'},
                {'md': 4200, 'tvd': 4200, 'inclination': 0, 'azimuth': 42.5, 'dls': 0, 'ns': '0', 'ew': '0', 'vs': '0', 'closure_dist': '0', 'closure_dir': '42.5', 'build_turn': 'KOP', 'remarks': 'KICKOFF POINT'},
                {'md': 5467, 'tvd': 5100, 'inclination': 38.0, 'azimuth': 42.5, 'dls': 3.0, 'ns': '312', 'ew': '285', 'vs': '420', 'closure_dist': '420', 'closure_dir': '42.5', 'build_turn': 'EOB', 'remarks': 'END OF BUILD'},
                {'md': 7200, 'tvd': 6460, 'inclination': 38.0, 'azimuth': 42.5, 'dls': 0, 'ns': '860', 'ew': '785', 'vs': '1160', 'closure_dist': '1160', 'closure_dir': '42.5', 'build_turn': 'Tangent', 'remarks': ''},
                {'md': 10200, 'tvd': 8600, 'inclination': 38.0, 'azimuth': 42.5, 'dls': 0, 'ns': '1720', 'ew': '1570', 'vs': '2320', 'closure_dist': '2320', 'closure_dir': '42.5', 'build_turn': 'Tangent', 'remarks': '13-3/8" Shoe'},
                {'md': 12800, 'tvd': 10200, 'inclination': 38.0, 'azimuth': 42.5, 'dls': 0, 'ns': '2580', 'ew': '2355', 'vs': '3480', 'closure_dist': '3480', 'closure_dir': '42.5', 'build_turn': 'Tangent', 'remarks': 'Top Arab-D'},
                {'md': 14850, 'tvd': 11200, 'inclination': 38.0, 'azimuth': 42.5, 'dls': 0, 'ns': '3250', 'ew': '2965', 'vs': '4390', 'closure_dist': '4390', 'closure_dir': '42.5', 'build_turn': 'Tangent', 'remarks': 'TD - 9-5/8" Shoe'},
            ]
        )

        p.bop_stack = BOPStack(
            bop_type="Quad Ram (Cameron Type U-II)",
            working_pressure=10000, bore_size=18.75,
            manufacturer="Cameron (SLB)", model="Type U-II Quad Ram",
            serial_number="CAM-U2-2019-1456",
            annular_preventer_size=18.75, annular_preventer_wp=10000,
            pipe_ram_size='5" (upper), 3-1/2" (lower)',
            blind_ram=True, shear_ram=True, variable_bore_ram=True,
            kill_line_size=3.0, choke_line_size=3.0,
            choke_manifold_wp=10000, kill_manifold_wp=10000,
            diverter_size=30, diverter_line_size=12,
            accumulator_capacity=2400, accumulator_precharge=1000,
            function_test_frequency="Weekly",
            pressure_test_frequency="Per Section",
            bop_test_pressure_low=250, bop_test_pressure_high=7000,
            remarks="Stack: Pipe rams 5\", Pipe rams 3-1/2\", Blind/Shear, VBR, Annular. "
                    "Koomey 72-bottle accumulator. All NACE trim from intermediate shoe.")

        p.well_control = WellControlData(
            maasp_surface=2850, kick_tolerance=45,
            kill_method="Wait & Weight (Engineer's Method) - preferred for H₂S",
            slow_pump_rate_1=30, slow_pump_pressure_1=920,
            slow_pump_rate_2=20, slow_pump_pressure_2=650,
            slow_pump_rate_3=40, slow_pump_pressure_3=1180,
            pit_gain_action_level=5, gas_detection_action_level=50,
            h2s_action_levels="10ppm: ALERT | 20ppm: ALARM/SCBA | 50ppm: EVACUATE | 100ppm: IDLH/EMERGENCY",
            emergency_contacts="Company Man: +971-50-XXX-XXXX | AGPC Base: +971-2-XXX-XXXX (24/7)\n"
                               "Al-Ain Hospital: +971-3-XXX-XXXX (40 min) | MEDEVAC: +971-2-XXX-XXXX\n"
                               "Fire: 997 | Police: 999 | Ambulance: 998 | Civil Defense: 996")

        p.rig_spec = RigSpecification(
            rig_name="NODC RIG-112", rig_type="Land Rig",
            rig_contractor="National Oilwell Drilling Company",
            max_hook_load=1000000, max_rotary_torque=37500, max_rotary_speed=250,
            drawworks_power=2000, top_drive=True,
            top_drive_model="NOV TDS-11SA (AC/VFD)", top_drive_torque=37500,
            derrick_height=147, rotary_table_size=37.5,
            mud_pump_1_type="NOV 14-P-220 Triplex", mud_pump_1_hp=1600,
            mud_pump_1_liner=6.5, mud_pump_1_max_pressure=5200, mud_pump_1_max_flow=880,
            mud_pump_2_type="NOV 14-P-220 Triplex", mud_pump_2_hp=1600,
            mud_pump_2_liner=6.5, mud_pump_2_max_pressure=5200, mud_pump_2_max_flow=880,
            mud_pump_3_type="NOV 14-P-220 (Standby/Cement)", mud_pump_3_hp=1600,
            pit_volume_total=2200, pit_volume_active=1400,
            shale_shaker_count=4, degasser_type="Centrifugal + Atmospheric",
            centrifuge="2x Derrick DE-1000 Decanting Centrifuge",
            generators="4x CAT 3512B (1500 kW each) + 1x CAT 3508 standby",
            total_power=6000, crane_capacity=50, accommodation=130,
            remarks="AC/VFD electric rig. NOV NOVOS auto-driller. Pason EDR. "
                    "Certified for H₂S operations (NACE trim BOP).")

        p.time_estimates = [
            TimeEstimate(section_name="Pre-Spud", operation="Rig Move, Setup, Acceptance, Pre-Spud Meeting",
                total_section_days=4.0, cumulative_days=4.0),
            TimeEstimate(section_name="Conductor", operation="Drill 36\" & Set 30\" Conductor @ 300 ft",
                depth_to=300, rop_average=30, total_section_days=2.0, cumulative_days=6.0),
            TimeEstimate(section_name="Surface", operation="Drill 26\" & Run/Cement 20\" Casing @ 2900 ft",
                depth_from=300, depth_to=2900, rop_average=35, total_section_days=8.0, cumulative_days=14.0),
            TimeEstimate(section_name="Intermediate-Build", operation="Drill 17-1/2\" (Build: 2900-5467 ft)",
                depth_from=2900, depth_to=5467, rop_average=18, total_section_days=10.0, cumulative_days=24.0),
            TimeEstimate(section_name="Intermediate-Tangent", operation="Drill 17-1/2\" (Tangent: 5467-10200 ft)",
                depth_from=5467, depth_to=10200, rop_average=15, total_section_days=16.0, cumulative_days=40.0),
            TimeEstimate(section_name="Int. Casing", operation="Run & Cement 13-3/8\" + WOC + CBL @ 10,200 ft",
                total_section_days=5.0, cumulative_days=45.0),
            TimeEstimate(section_name="Production", operation="Drill 12-1/4\" & Run/Cement 9-5/8\" @ 14,850 ft",
                depth_from=10200, depth_to=14850, rop_average=10, total_section_days=28.0, cumulative_days=73.0,
                remarks="Convert to OBM. RSS. H₂S zone. Includes LWD, coring, casing, cement, CBL/CBIL."),
            TimeEstimate(section_name="Completion", operation="Completion, Perforation & Well Testing",
                total_section_days=10.0, cumulative_days=83.0),
            TimeEstimate(section_name="Rig Release", operation="Rig Down & Demobilization",
                total_section_days=2.0, cumulative_days=85.0),
        ]

        p.drilling_parameters = [
            DrillingParameters(section_name="Surface", hole_size=26,
                depth_from=300, depth_to=2900, wob_min=15, wob_max=35,
                rpm_min=80, rpm_max=120, flow_rate_min=900, flow_rate_max=1100,
                rop_min=20, rop_max=60, rop_average=35,
                torque_max=25000, spp_max=2500, overpull_limit=50, max_ecd=14.5),
            DrillingParameters(section_name="Intermediate (Build)", hole_size=17.5,
                depth_from=2900, depth_to=5467, wob_min=15, wob_max=35,
                rpm_min=0, rpm_max=160, flow_rate_min=700, flow_rate_max=850,
                rop_min=10, rop_max=30, rop_average=18,
                torque_max=35000, spp_max=3500, overpull_limit=50, max_ecd=16.0),
            DrillingParameters(section_name="Intermediate (Tangent)", hole_size=17.5,
                depth_from=5467, depth_to=10200, wob_min=25, wob_max=45,
                rpm_min=120, rpm_max=180, flow_rate_min=750, flow_rate_max=900,
                rop_min=8, rop_max=25, rop_average=15,
                torque_max=38000, spp_max=4000, overpull_limit=50, max_ecd=16.5),
            DrillingParameters(section_name="Production", hole_size=12.25,
                depth_from=10200, depth_to=14850, wob_min=8, wob_max=25,
                rpm_min=120, rpm_max=200, flow_rate_min=550, flow_rate_max=700,
                rop_min=5, rop_max=20, rop_average=10,
                torque_max=28000, spp_max=4500, overpull_limit=40, max_ecd=17.2),
        ]

        return p

    def _preset_me_sweet(self):
        """Middle East Sweet Well - simplified version"""
        from main import (
            WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, HazardEntry, CasingDesign,
            CementDesign, BHADesign, MudProgram,
            DirectionalPlan, BOPStack, WellControlData,
            RigSpecification, DrillingParameters, TimeEstimate
        )
        p = WellProject()
        p.company_info = CompanyInfo(
            operator_name="SAUDI ARAMCO",
            contractor_name="ARPD - Arabian Petroleum Drilling Co.",
            field_name="GHAWAR FIELD - AIN DAR AREA",
            well_name="UTMN-1245", rig_name="ARPD Rig 78 (1500 HP)",
            rig_type="Land Rig", country="KINGDOM OF SAUDI ARABIA",
            region="Eastern Province", block_license="Saudi Aramco Concession",
            document_number="SA-DRL-UTMN1245-2024-001",
            prepared_by="Eng. Faisal Al-Otaibi", revision="0",
            classification="COMPANY CONFIDENTIAL")
        p.well_info = WellGeneralInfo(
            well_type="Development", well_profile="Directional S-Type",
            total_depth_md=11500, total_depth_tvd=10200,
            ground_elevation=210, kb_elevation=25.0,
            target_formation="Khuff Formation - Khuff-C Reservoir",
            expected_reservoir_pressure=4200, expected_reservoir_temperature=220,
            nace_required=False, wellhead_type="Cameron CC-4 Compact")
        p.formation_tops = [
            FormationTop(name="Recent/Quaternary", formation_type="Sand",
                md_top=0, md_bottom=500, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=13.5, fracture_gradient_bottom=14.0,
                temperature_top=95, temperature_bottom=110, drillability="Easy"),
            FormationTop(name="Dam Formation", formation_type="Limestone",
                md_top=500, md_bottom=2800, pore_pressure_top=8.6, pore_pressure_bottom=8.8,
                fracture_gradient_top=14.0, fracture_gradient_bottom=15.0,
                temperature_top=110, temperature_bottom=155, drillability="Medium",
                remarks="Possible losses in Dammam Fm"),
            FormationTop(name="Wasia/Aruma", formation_type="Limestone",
                md_top=2800, md_bottom=8000, pore_pressure_top=8.8, pore_pressure_bottom=9.5,
                fracture_gradient_top=15.0, fracture_gradient_bottom=16.5,
                temperature_top=155, temperature_bottom=210, drillability="Hard"),
            FormationTop(name="Shuaiba/Biyadh", formation_type="Limestone",
                md_top=8000, md_bottom=9500, pore_pressure_top=9.5, pore_pressure_bottom=9.8,
                fracture_gradient_top=16.5, fracture_gradient_bottom=16.8,
                temperature_top=210, temperature_bottom=218, drillability="Hard"),
            FormationTop(name="Khuff Formation", formation_type="Dolomite",
                md_top=9500, md_bottom=11500, pore_pressure_top=9.8, pore_pressure_bottom=10.2,
                fracture_gradient_top=16.8, fracture_gradient_bottom=17.0,
                temperature_top=218, temperature_bottom=225, drillability="Medium-Hard",
                remarks="🎯 TARGET - Khuff-C, sweet oil, no H₂S"),
        ]
        p.hazards = [
            HazardEntry(hazard_type="Lost Circulation", md_top=500, md_bottom=2800,
                severity="Medium", probability="Likely",
                description="Fractured Dammam limestone",
                mitigation="LCM in mud"),
            HazardEntry(hazard_type="Stuck Pipe", md_top=8000, md_bottom=9500,
                severity="Medium", probability="Possible",
                description="Differential sticking in Biyadh sands",
                mitigation="Minimize static time, lubricant"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Conductor", hole_size=36, casing_od=30,
                casing_id=28.0, casing_weight=309.72, casing_grade="X-52",
                setting_depth_md=200, setting_depth_tvd=200, top_of_cement_md=0),
            CasingDesign(section_name="Surface", hole_size=26, casing_od=20,
                casing_id=18.73, casing_weight=133, casing_grade="K-55",
                casing_connection="BTC", setting_depth_md=2800,
                setting_depth_tvd=2800, top_of_cement_md=0,
                burst_rating=3060, collapse_rating=1490, drift_id=18.63),
            CasingDesign(section_name="Production", hole_size=17.5, casing_od=13.375,
                casing_id=12.415, casing_weight=72, casing_grade="N-80",
                casing_connection="BTC", setting_depth_md=11500,
                setting_depth_tvd=10200, top_of_cement_md=7000,
                burst_rating=5020, collapse_rating=2670, drift_id=12.259),
        ]
        p.cement_design = [
            CementDesign(section_name="Surface", casing_od=20, hole_size=26,
                shoe_depth_md=2800, toc_md=0, lead_slurry_density=12.5,
                tail_slurry_density=15.8, excess_percentage=100, woc_time=12, cbl_cbil_required=True),
            CementDesign(section_name="Production", casing_od=13.375, hole_size=17.5,
                shoe_depth_md=11500, toc_md=7000, lead_slurry_density=12.0,
                tail_slurry_density=16.0, excess_percentage=50, woc_time=18, cbl_cbil_required=True),
        ]
        p.bha_designs = [
            BHADesign(section_name="Surface", bha_number=1, hole_size=26,
                bha_type="Rotary", bit_type="Tricone Insert", bit_size=26,
                mwd_type="Gyro MWD", recommended_wob="15-30 klbs", recommended_rpm="80-120"),
            BHADesign(section_name="Production", bha_number=1, hole_size=17.5,
                bha_type="Motor + MWD/LWD", bit_type="PDC", bit_size=17.5,
                motor_type="9-5/8\" PDM", motor_od=9.625, motor_bend=1.2,
                mwd_type="PowerPulse", lwd_sensors="GR, RES, DEN, NEU",
                recommended_wob="15-35 klbs", recommended_rpm="100-160"),
        ]
        p.mud_programs = [
            MudProgram(section_name="Surface", hole_size=26, depth_from=200, depth_to=2800,
                mud_type="WBM - Bentonite/Polymer", mud_weight_in=8.8, mud_weight_out=9.2,
                plastic_viscosity=15, yield_point=12, total_volume_required=1200),
            MudProgram(section_name="Production", hole_size=17.5, depth_from=2800, depth_to=11500,
                mud_type="WBM - KCl/Polymer", mud_weight_in=9.2, mud_weight_out=11.5,
                plastic_viscosity=22, yield_point=18, chlorides=40000, total_volume_required=2800),
        ]
        p.directional_plan = DirectionalPlan(
            survey_tool="MWD Magnetic", survey_frequency=90,
            kickoff_point_md=3500, build_rate=2.5,
            hold_inclination=25, target_inclination=25, target_azimuth=135, max_dls=4.0)
        p.bop_stack = BOPStack(working_pressure=10000, bore_size=18.75,
            manufacturer="Cameron", pipe_ram_size='5"', shear_ram=True,
            bop_test_pressure_low=250, bop_test_pressure_high=7000)
        p.well_control = WellControlData(
            maasp_surface=2200, kill_method="Driller's Method",
            kick_tolerance=60, slow_pump_rate_1=30, slow_pump_pressure_1=750)
        p.rig_spec = RigSpecification(rig_name="ARPD Rig 78", rig_type="Land Rig",
            max_hook_load=750000, top_drive=True, mud_pump_1_hp=1300)
        p.time_estimates = [
            TimeEstimate(section_name="Pre-Spud", operation="Setup", total_section_days=3, cumulative_days=3),
            TimeEstimate(section_name="Conductor", operation="Set 30\"", total_section_days=1.5, cumulative_days=4.5),
            TimeEstimate(section_name="Surface", operation="Drill 26\" & Set 20\"", depth_to=2800, total_section_days=6, cumulative_days=10.5),
            TimeEstimate(section_name="Production", operation="Drill 17-1/2\" & Set 13-3/8\"", depth_from=2800, depth_to=11500, total_section_days=30, cumulative_days=40.5),
            TimeEstimate(section_name="Completion", operation="Completion", total_section_days=5, cumulative_days=45.5),
        ]
        return p

    def _preset_jackup(self):
        """Offshore Jack-Up Well"""
        from main import (WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, HazardEntry, CasingDesign, CementDesign,
            BHADesign, MudProgram, DirectionalPlan, BOPStack,
            WellControlData, RigSpecification, TimeEstimate)
        p = WellProject()
        p.company_info = CompanyInfo(
            operator_name="TOTAL ENERGIES E&P",
            contractor_name="Shelf Drilling Ltd.",
            field_name="OFFSHORE BLOCK 12",
            well_name="BLK12-EXP-003",
            rig_name="Shelf Drilling Tenacious (JU-350)",
            rig_type="Jack-Up", country="QATAR",
            region="Persian Gulf Offshore",
            document_number="TE-DRL-BLK12-003-2024",
            classification="CONFIDENTIAL")
        p.well_info = WellGeneralInfo(
            well_type="Exploration", well_profile="Vertical",
            total_depth_md=13200, total_depth_tvd=13200,
            water_depth=180, air_gap=85, kb_elevation=85,
            target_formation="Permian Khuff Gas", expected_reservoir_pressure=7500,
            expected_reservoir_temperature=285, expected_h2s_concentration=1.5,
            nace_required=True)
        p.formation_tops = [
            FormationTop(name="Seabed Sediments", formation_type="Clay",
                md_top=0, md_bottom=500, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=12.5, fracture_gradient_bottom=13.5, remarks="Shallow gas risk"),
            FormationTop(name="UER/Dammam", formation_type="Limestone",
                md_top=500, md_bottom=5500, pore_pressure_top=8.6, pore_pressure_bottom=9.5,
                fracture_gradient_top=13.5, fracture_gradient_bottom=16.0, remarks="Loss zones possible"),
            FormationTop(name="Wasia/Aruma", formation_type="Limestone",
                md_top=5500, md_bottom=8500, pore_pressure_top=9.5, pore_pressure_bottom=11.0,
                fracture_gradient_top=16.0, fracture_gradient_bottom=17.0, remarks="Pressure ramp"),
            FormationTop(name="Khuff Formation", formation_type="Dolomite",
                md_top=8500, md_bottom=13200, pore_pressure_top=11.0, pore_pressure_bottom=12.5,
                fracture_gradient_top=17.0, fracture_gradient_bottom=18.0,
                remarks="🎯 TARGET - Gas, H₂S 1.5%"),
        ]
        p.hazards = [
            HazardEntry(hazard_type="H2S Gas", md_top=8500, md_bottom=13200,
                severity="High", probability="Almost Certain",
                description="H₂S 1.5% in Khuff. NACE required.",
                mitigation="NACE materials, SCBA, H₂S monitors"),
            HazardEntry(hazard_type="Lost Circulation", md_top=500, md_bottom=5500,
                severity="Medium", probability="Likely",
                description="Fractured UER/Dammam", mitigation="LCM in mud"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Conductor", hole_size=36, casing_od=30,
                setting_depth_md=350, top_of_cement_md=0, remarks="Jetted/Driven"),
            CasingDesign(section_name="Surface", hole_size=26, casing_od=20,
                casing_grade="K-55", casing_connection="BTC",
                setting_depth_md=3500, top_of_cement_md=0),
            CasingDesign(section_name="Intermediate", hole_size=17.5, casing_od=13.375,
                casing_grade="N-80", casing_connection="BTC",
                setting_depth_md=8500, top_of_cement_md=5000),
            CasingDesign(section_name="Production", hole_size=12.25, casing_od=9.625,
                casing_grade="C-95", casing_connection="VAM TOP",
                setting_depth_md=12500, top_of_cement_md=7500,
                remarks="NACE C-95 sour service"),
            CasingDesign(section_name="Liner", hole_size=8.5, casing_od=7,
                casing_grade="L-80", casing_connection="VAM TOP",
                setting_depth_md=13200, top_of_cement_md=12000,
                is_liner=True, liner_overlap=500, liner_top_md=12000,
                remarks="NACE L-80 liner"),
        ]
        p.cement_design = [
            CementDesign(section_name="Surface", casing_od=20, hole_size=26,
                shoe_depth_md=3500, toc_md=0, lead_slurry_density=13.0,
                tail_slurry_density=15.8, excess_percentage=100, woc_time=12, cbl_cbil_required=True),
            CementDesign(section_name="Intermediate", casing_od=13.375, hole_size=17.5,
                shoe_depth_md=8500, toc_md=5000, lead_slurry_density=12.5,
                tail_slurry_density=16.0, excess_percentage=50, woc_time=18, cbl_cbil_required=True),
            CementDesign(section_name="Production", casing_od=9.625, hole_size=12.25,
                shoe_depth_md=12500, toc_md=7500, lead_slurry_density=12.0,
                tail_slurry_density=16.5, excess_percentage=50, woc_time=24, cbl_cbil_required=True),
        ]
        p.bha_designs = [
            BHADesign(section_name="Surface", bha_number=1, hole_size=26,
                bha_type="Rotary", bit_type="Tricone", bit_size=26,
                recommended_wob="15-30 klbs"),
            BHADesign(section_name="Production", bha_number=1, hole_size=12.25,
                bha_type="Rotary + Full LWD", bit_type="PDC", bit_size=12.25,
                mwd_type="TeleScope", lwd_sensors="GR, RES, DEN, NEU, SON, FMI, MDT",
                recommended_wob="10-25 klbs"),
        ]
        p.mud_programs = [
            MudProgram(section_name="Surface", hole_size=26, depth_from=350, depth_to=3500,
                mud_type="WBM - Seawater/Polymer", mud_weight_in=8.8, mud_weight_out=9.5,
                plastic_viscosity=18, yield_point=15, total_volume_required=2000),
            MudProgram(section_name="Production", hole_size=12.25, depth_from=8500, depth_to=13200,
                mud_type="SBM - Synthetic Based Mud", mud_weight_in=12.5, mud_weight_out=14.5,
                plastic_viscosity=20, yield_point=12, oil_water_ratio="85/15",
                electrical_stability=1200, total_volume_required=3500),
        ]
        p.directional_plan = DirectionalPlan(
            survey_tool="Gyro MWD", survey_frequency=100, max_dls=3.0,
            remarks="Vertical well - maintain < 2° inclination")
        p.bop_stack = BOPStack(bop_type="Quad Ram", working_pressure=15000, bore_size=18.75,
            manufacturer="Cameron", model="Type TL", shear_ram=True,
            bop_test_pressure_low=300, bop_test_pressure_high=10500)
        p.well_control = WellControlData(maasp_surface=3500, kill_method="Wait & Weight",
            kick_tolerance=35, slow_pump_rate_1=30, slow_pump_pressure_1=1200)
        p.rig_spec = RigSpecification(rig_name="Shelf Drilling Tenacious", rig_type="Jack-Up",
            max_hook_load=1200000, top_drive=True, mud_pump_1_hp=1600,
            pit_volume_total=2500, accommodation=150)
        p.time_estimates = [
            TimeEstimate(section_name="Rig Position", operation="Jack-Up & Position", total_section_days=3, cumulative_days=3),
            TimeEstimate(section_name="Conductor", operation="Jet/Drive Conductor", total_section_days=2, cumulative_days=5),
            TimeEstimate(section_name="Surface", operation="Drill 26\" & Set 20\"", depth_to=3500, total_section_days=8, cumulative_days=13),
            TimeEstimate(section_name="Intermediate", operation="Drill 17-1/2\" & Set 13-3/8\"", depth_to=8500, total_section_days=18, cumulative_days=31),
            TimeEstimate(section_name="Production", operation="Drill 12-1/4\" & Set 9-5/8\"", depth_to=12500, total_section_days=20, cumulative_days=51),
            TimeEstimate(section_name="Liner", operation="Drill 8-1/2\" & Run 7\" Liner", total_section_days=8, cumulative_days=59),
            TimeEstimate(section_name="Evaluation", operation="Logging + DST", total_section_days=10, cumulative_days=69),
            TimeEstimate(section_name="Rig Release", operation="P&A / Suspend + Rig Move", total_section_days=4, cumulative_days=73),
        ]
        return p

    def _preset_hpht(self):
        """North Sea HPHT Well"""
        from main import (WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, HazardEntry, CasingDesign, CementDesign,
            BHADesign, MudProgram, DirectionalPlan, BOPStack,
            WellControlData, RigSpecification, TimeEstimate)
        p = WellProject()
        p.company_info = CompanyInfo(operator_name="EQUINOR ASA",
            contractor_name="Transocean Ltd.", field_name="KVITEBJØRN FIELD",
            well_name="KVB-A-42", rig_name="Transocean Arctic (Semi-Sub)",
            rig_type="Semi-Submersible", country="NORWAY",
            region="Norwegian North Sea", document_number="EQN-DRL-KVB42-2024",
            classification="RESTRICTED")
        p.well_info = WellGeneralInfo(well_type="Exploration", well_profile="Vertical",
            total_depth_md=18500, total_depth_tvd=18500, water_depth=620, kb_elevation=75,
            target_formation="Brent Group Sandstone",
            expected_reservoir_pressure=16000, expected_reservoir_temperature=380, nace_required=True)
        p.formation_tops = [
            FormationTop(name="Nordland Group", formation_type="Clay",
                md_top=0, md_bottom=2500, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=12.0, fracture_gradient_bottom=14.0),
            FormationTop(name="Hordaland Group", formation_type="Shale",
                md_top=2500, md_bottom=7000, pore_pressure_top=8.6, pore_pressure_bottom=10.0,
                fracture_gradient_top=14.0, fracture_gradient_bottom=16.5, remarks="Pressure ramp"),
            FormationTop(name="Rogaland Group", formation_type="Shale",
                md_top=7000, md_bottom=11000, pore_pressure_top=10.0, pore_pressure_bottom=14.0,
                fracture_gradient_top=16.5, fracture_gradient_bottom=18.0, remarks="HPHT zone"),
            FormationTop(name="Shetland Group", formation_type="Chalk",
                md_top=11000, md_bottom=15000, pore_pressure_top=14.0, pore_pressure_bottom=16.0,
                fracture_gradient_top=18.0, fracture_gradient_bottom=19.0, remarks="Narrow window"),
            FormationTop(name="Brent Group", formation_type="Sandstone",
                md_top=15000, md_bottom=18500, pore_pressure_top=16.0, pore_pressure_bottom=17.5,
                fracture_gradient_top=19.0, fracture_gradient_bottom=20.0,
                temperature_top=360, temperature_bottom=380, remarks="🎯 TARGET HPHT reservoir"),
        ]
        p.hazards = [
            HazardEntry(hazard_type="High Pressure", md_top=7000, md_bottom=18500,
                severity="Critical", probability="Almost Certain",
                description="HPHT - 16,000 psi reservoir, 380°F BHT",
                mitigation="15K BOP, HPHT tools, HT cement"),
            HazardEntry(hazard_type="Sloughing Shale", md_top=2500, md_bottom=7000,
                severity="High", probability="Likely",
                description="Reactive Hordaland shales",
                mitigation="High inhibition mud, oil-based preferred"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Conductor", hole_size=36, casing_od=30, setting_depth_md=500),
            CasingDesign(section_name="Surface", hole_size=26, casing_od=20, casing_grade="K-55", setting_depth_md=2500),
            CasingDesign(section_name="Intermediate-1", hole_size=17.5, casing_od=13.625,
                casing_grade="P-110", setting_depth_md=7000),
            CasingDesign(section_name="Intermediate-2", hole_size=12.25, casing_od=10.75,
                casing_grade="Q-125", setting_depth_md=11000),
            CasingDesign(section_name="Production", hole_size=8.5, casing_od=7,
                casing_grade="Q-125", casing_connection="VAM TOP HC",
                setting_depth_md=18500, remarks="15K rated HPHT connections"),
        ]
        p.cement_design = [CementDesign(section_name="Production", casing_od=7, hole_size=8.5,
            shoe_depth_md=18500, toc_md=15000, lead_slurry_density=13.0, tail_slurry_density=17.0,
            excess_percentage=50, woc_time=36, cbl_cbil_required=True,
            cement_additives="HT retarder, HT FL control, Silica 35-40%, HPHT stabilizers")]
        p.bha_designs = [BHADesign(section_name="Production", bha_number=1, hole_size=8.5,
            bha_type="Rotary + MWD", bit_type="PDC", bit_size=8.5,
            mwd_type="HT MWD (rated 400°F)", lwd_sensors="GR, RES, DEN",
            recommended_wob="8-20 klbs", recommended_rpm="100-160")]
        p.mud_programs = [
            MudProgram(section_name="Surface", hole_size=26, depth_from=500, depth_to=2500,
                mud_type="WBM - Seawater Gel", mud_weight_in=8.6, mud_weight_out=9.5, total_volume_required=2000),
            MudProgram(section_name="Production", hole_size=8.5, depth_from=11000, depth_to=18500,
                mud_type="OBM - Mineral Oil (HT Formulation)", mud_weight_in=17.5, mud_weight_out=18.5,
                plastic_viscosity=25, oil_water_ratio="85/15", electrical_stability=1500, total_volume_required=3000),
        ]
        p.directional_plan = DirectionalPlan(survey_tool="MWD + Gyro at shoes",
            survey_frequency=90, max_dls=3.0, remarks="Vertical well, NORSOK D-010")
        p.bop_stack = BOPStack(bop_type="Subsea Stack", working_pressure=15000, bore_size=18.75,
            manufacturer="Cameron", model="18-3/4\" 15K Subsea BOP",
            shear_ram=True, casing_shear_ram=True, accumulator_capacity=5000,
            bop_test_pressure_low=300, bop_test_pressure_high=10500)
        p.well_control = WellControlData(maasp_surface=5000, kill_method="Wait & Weight",
            kick_tolerance=20, slow_pump_rate_1=25, slow_pump_pressure_1=2500)
        p.rig_spec = RigSpecification(rig_name="Transocean Arctic", rig_type="Semi-Submersible",
            max_hook_load=2000000, top_drive=True, mud_pump_1_hp=2200,
            pit_volume_total=4000, accommodation=200)
        p.time_estimates = [
            TimeEstimate(section_name="Total", operation="HPHT Exploration (NORSOK D-010)",
                total_section_days=120, cumulative_days=120),
        ]
        return p

    def _preset_deepwater(self):
        """GOM Deepwater"""
        from main import (WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, CasingDesign, BHADesign, MudProgram,
            DirectionalPlan, BOPStack, WellControlData, RigSpecification, TimeEstimate)
        p = WellProject()
        p.company_info = CompanyInfo(operator_name="SHELL OFFSHORE INC.",
            contractor_name="Transocean Deepwater Inc.",
            field_name="PERDIDO AREA - GOM", well_name="GC-857 #001",
            rig_name="Deepwater Invictus (7th Gen Drillship)",
            rig_type="Drillship", country="UNITED STATES",
            region="Gulf of Mexico Deepwater")
        p.well_info = WellGeneralInfo(well_type="Exploration",
            well_profile="Directional J-Type", total_depth_md=25000, total_depth_tvd=22000,
            water_depth=5000, air_gap=85, target_formation="Lower Tertiary Wilcox",
            expected_reservoir_pressure=18000, expected_reservoir_temperature=290)
        p.formation_tops = [
            FormationTop(name="Recent Sediments", formation_type="Clay",
                md_top=0, md_bottom=2000, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=12.0, fracture_gradient_bottom=13.5),
            FormationTop(name="Pliocene", formation_type="Shale",
                md_top=2000, md_bottom=8000, pore_pressure_top=8.6, pore_pressure_bottom=11.0,
                fracture_gradient_top=13.5, fracture_gradient_bottom=16.0, remarks="Geopressure transition"),
            FormationTop(name="Miocene", formation_type="Sandstone",
                md_top=8000, md_bottom=18000, pore_pressure_top=11.0, pore_pressure_bottom=15.0,
                fracture_gradient_top=16.0, fracture_gradient_bottom=18.0, remarks="Overpressured sands"),
            FormationTop(name="Lower Tertiary Wilcox", formation_type="Sandstone",
                md_top=18000, md_bottom=25000, pore_pressure_top=15.0, pore_pressure_bottom=17.5,
                fracture_gradient_top=18.0, fracture_gradient_bottom=19.5,
                temperature_top=270, temperature_bottom=295, remarks="🎯 TARGET - deepwater reservoir"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Structural", hole_size=42, casing_od=36, setting_depth_md=5200, remarks="Jetted"),
            CasingDesign(section_name="Conductor", hole_size=26, casing_od=22, setting_depth_md=7000),
            CasingDesign(section_name="Surface", hole_size=17.5, casing_od=16, setting_depth_md=10000),
            CasingDesign(section_name="Intermediate-1", hole_size=14.75, casing_od=13.625, setting_depth_md=15000),
            CasingDesign(section_name="Intermediate-2", hole_size=12.25, casing_od=11.75, setting_depth_md=20000),
            CasingDesign(section_name="Production", hole_size=8.75, casing_od=9.625, setting_depth_md=23000),
            CasingDesign(section_name="Liner", hole_size=6.0, casing_od=7.0, setting_depth_md=25000, is_liner=True),
        ]
        p.bha_designs = [BHADesign(section_name="Production", bha_number=1, hole_size=8.75,
            bha_type="RSS + Full LWD", bit_type="PDC", bit_size=8.75,
            rss_type="PowerDrive", mwd_type="TeleScope", lwd_sensors="GR, RES, DEN, NEU, MDT")]
        p.mud_programs = [
            MudProgram(section_name="Riser", hole_size=26, depth_from=0, depth_to=7000,
                mud_type="SBM - Synthetic Base", mud_weight_in=8.6, mud_weight_out=10.0, total_volume_required=5000),
            MudProgram(section_name="Production", hole_size=8.75, depth_from=20000, depth_to=25000,
                mud_type="SBM - Synthetic Base (HT/HP)", mud_weight_in=17.0, mud_weight_out=18.5,
                oil_water_ratio="80/20", electrical_stability=1800, total_volume_required=4000),
        ]
        p.directional_plan = DirectionalPlan(kickoff_point_md=12000, build_rate=2.0,
            hold_inclination=55, target_inclination=55, max_dls=4.0)
        p.bop_stack = BOPStack(bop_type="Subsea Stack", working_pressure=15000, bore_size=18.75,
            manufacturer="Cameron", model="EVO 18-3/4\" 15K",
            shear_ram=True, casing_shear_ram=True, accumulator_capacity=8000)
        p.well_control = WellControlData(maasp_surface=6000, kill_method="Wait & Weight",
            kick_tolerance=15, slow_pump_rate_1=20, slow_pump_pressure_1=3000)
        p.rig_spec = RigSpecification(rig_name="Deepwater Invictus", rig_type="Drillship",
            max_hook_load=2500000, top_drive=True, mud_pump_1_hp=2200,
            pit_volume_total=6000, accommodation=200)
        p.time_estimates = [
            TimeEstimate(section_name="Total", operation="Deepwater Exploration (BSEE/API)",
                total_section_days=180, cumulative_days=180),
        ]
        return p

    def _preset_horizontal(self):
        """Horizontal Shale Well"""
        from main import (WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, CasingDesign, CementDesign, BHADesign, MudProgram,
            DirectionalPlan, BOPStack, WellControlData, RigSpecification, TimeEstimate)
        p = WellProject()
        p.company_info = CompanyInfo(operator_name="PIONEER NATURAL RESOURCES",
            contractor_name="Patterson-UTI Drilling", field_name="MIDLAND BASIN",
            well_name="PIONEER WC-A 1422H", rig_name="PTEN Rig 295 (APEX 1500)",
            rig_type="Land Rig", country="UNITED STATES", region="Permian Basin, TX")
        p.well_info = WellGeneralInfo(well_type="Development", well_profile="Horizontal",
            total_depth_md=20500, total_depth_tvd=8200,
            target_formation="Wolfcamp A Formation",
            expected_reservoir_pressure=3800, expected_reservoir_temperature=180)
        p.formation_tops = [
            FormationTop(name="Clear Fork", formation_type="Limestone",
                md_top=0, md_bottom=2000, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=13.0, fracture_gradient_bottom=14.0),
            FormationTop(name="Spraberry", formation_type="Sandstone",
                md_top=2000, md_bottom=6000, pore_pressure_top=8.6, pore_pressure_bottom=9.0,
                fracture_gradient_top=14.0, fracture_gradient_bottom=15.5),
            FormationTop(name="Wolfcamp A", formation_type="Shale",
                md_top=6000, md_bottom=20500, pore_pressure_top=9.0, pore_pressure_bottom=9.5,
                fracture_gradient_top=15.5, fracture_gradient_bottom=16.0,
                temperature_top=175, temperature_bottom=185,
                remarks="🎯 TARGET - 10,000 ft lateral in Wolfcamp A"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Surface", hole_size=17.5, casing_od=13.375,
                casing_grade="J-55", setting_depth_md=1500, setting_depth_tvd=1500, top_of_cement_md=0),
            CasingDesign(section_name="Intermediate", hole_size=12.25, casing_od=9.625,
                casing_grade="N-80", setting_depth_md=8500, setting_depth_tvd=8200,
                top_of_cement_md=5000, remarks="Curve + landing point for lateral"),
            CasingDesign(section_name="Production", hole_size=8.75, casing_od=5.5,
                casing_grade="P-110", casing_connection="VAM SF",
                setting_depth_md=20500, setting_depth_tvd=8200,
                top_of_cement_md=0, cement_to_surface=True,
                remarks="10,000 ft lateral - frac-ready design"),
        ]
        p.cement_design = [
            CementDesign(section_name="Intermediate", casing_od=9.625, hole_size=12.25,
                shoe_depth_md=8500, toc_md=5000, lead_slurry_density=12.5,
                tail_slurry_density=15.8, excess_percentage=50, woc_time=8),
        ]
        p.bha_designs = [
            BHADesign(section_name="Vertical", bha_number=1, hole_size=12.25,
                bha_type="Rotary + MWD", bit_type="PDC", bit_size=12.25,
                mwd_type="Gyro MWD", recommended_wob="15-35 klbs"),
            BHADesign(section_name="Curve", bha_number=2, hole_size=8.75,
                bha_type="Motor + MWD (Build 8-12°/100ft)", bit_type="PDC", bit_size=8.75,
                motor_type="6-3/4\" PDM", motor_od=6.75, motor_bend=3.0,
                mwd_type="Rotary Steerable MWD", recommended_wob="8-20 klbs"),
            BHADesign(section_name="Lateral", bha_number=3, hole_size=8.75,
                bha_type="RSS + MWD (Lateral Drilling)", bit_type="PDC", bit_size=8.75,
                rss_type="PowerDrive Orbit", mwd_type="TeleScope",
                recommended_wob="8-25 klbs", recommended_rpm="150-220",
                recommended_flow_rate="350-450 GPM"),
        ]
        p.mud_programs = [
            MudProgram(section_name="Surface", hole_size=17.5, depth_from=0, depth_to=1500,
                mud_type="WBM - Gel/Water Spud", mud_weight_in=8.7, mud_weight_out=8.9,
                plastic_viscosity=12, yield_point=10, total_volume_required=600),
            MudProgram(section_name="Lateral", hole_size=8.75, depth_from=8500, depth_to=20500,
                mud_type="WBM - High Performance (Slickwater)", mud_weight_in=8.9, mud_weight_out=9.2,
                plastic_viscosity=8, yield_point=6, total_volume_required=1200),
        ]
        p.directional_plan = DirectionalPlan(
            kickoff_point_md=6500, build_rate=8.0,
            hold_inclination=90, target_inclination=90, target_azimuth=270, max_dls=12.0,
            horizontal_displacement=10000, remarks="Pad drilling - batch mode, 18-day well")
        p.bop_stack = BOPStack(working_pressure=5000, bore_size=13.625,
            bop_type="Double Ram", shear_ram=True, bop_test_pressure_low=200,
            bop_test_pressure_high=3500)
        p.well_control = WellControlData(maasp_surface=1500, kill_method="Driller's Method",
            kick_tolerance=100, slow_pump_rate_1=40, slow_pump_pressure_1=400)
        p.rig_spec = RigSpecification(rig_name="PTEN Rig 295 APEX 1500", rig_type="Land Rig",
            max_hook_load=750000, top_drive=True, mud_pump_1_hp=1500,
            pit_volume_total=800, accommodation=20)
        p.time_estimates = [
            TimeEstimate(section_name="Surface", operation="Drill & Set 13-3/8\"", depth_to=1500, total_section_days=2, cumulative_days=2),
            TimeEstimate(section_name="Vertical+Curve", operation="Drill 12-1/4\" & Set 9-5/8\"", depth_to=8500, total_section_days=5, cumulative_days=7),
            TimeEstimate(section_name="Lateral", operation="Drill 10,000 ft lateral + Run 5-1/2\"", depth_from=8500, depth_to=20500, total_section_days=9, cumulative_days=16),
            TimeEstimate(section_name="Completion", operation="Plug & Perf - 50 stages", total_section_days=2, cumulative_days=18),
        ]
        return p

    def _preset_erd(self):
        """Extended Reach Drilling"""
        from main import (WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, CasingDesign, BHADesign, MudProgram,
            DirectionalPlan, BOPStack, WellControlData, RigSpecification, TimeEstimate)
        p = WellProject()
        p.company_info = CompanyInfo(operator_name="SAKHALIN ENERGY (Shell/Gazprom JV)",
            field_name="CHAYVO FIELD", well_name="OP-11 ERD",
            rig_name="Yastreb Custom ERD Rig (3000 HP)", rig_type="Land Rig",
            country="RUSSIA", region="Sakhalin Island")
        p.well_info = WellGeneralInfo(well_type="Development",
            well_profile="Extended Reach (ERD)", total_depth_md=40000, total_depth_tvd=6200,
            target_formation="Piltun Formation Offshore Reservoir",
            expected_reservoir_pressure=4500, expected_reservoir_temperature=175)
        p.formation_tops = [
            FormationTop(name="Permafrost/Quaternary", formation_type="Clay",
                md_top=0, md_bottom=800, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=12.0, fracture_gradient_bottom=13.0, remarks="Permafrost considerations"),
            FormationTop(name="Nyisky Formation", formation_type="Sandstone",
                md_top=800, md_bottom=4000, pore_pressure_top=8.6, pore_pressure_bottom=9.0,
                fracture_gradient_top=13.0, fracture_gradient_bottom=15.0),
            FormationTop(name="Piltun Formation", formation_type="Sandstone",
                md_top=4000, md_bottom=40000, pore_pressure_top=9.0, pore_pressure_bottom=9.5,
                fracture_gradient_top=15.0, fracture_gradient_bottom=16.0,
                remarks="🎯 TARGET - ERD reservoir, 82° inclination throughout"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Conductor", hole_size=36, casing_od=30, setting_depth_md=500),
            CasingDesign(section_name="Surface", hole_size=26, casing_od=20, setting_depth_md=5000),
            CasingDesign(section_name="Intermediate-1", hole_size=17.5, casing_od=13.375, setting_depth_md=18000),
            CasingDesign(section_name="Intermediate-2", hole_size=12.25, casing_od=10.75, setting_depth_md=30000),
            CasingDesign(section_name="Production", hole_size=8.5, casing_od=7,
                setting_depth_md=40000, remarks="World record ERD - T&D management critical"),
        ]
        p.bha_designs = [BHADesign(section_name="ERD Lateral", bha_number=1, hole_size=8.5,
            bha_type="RSS + Specialized ERD Tools", bit_type="PDC", bit_size=8.5,
            rss_type="PowerDrive Xceed (high torque)", mwd_type="TeleScope ICE",
            lwd_sensors="GR, RES, PWD, Drilling Dynamics",
            recommended_wob="3-15 klbs", recommended_rpm="80-120",
            recommended_flow_rate="300-450 GPM",
            remarks="ERD: Low WOB due to T&D. Torque management critical. "
                    "Shock/vibration monitoring essential.")]
        p.mud_programs = [
            MudProgram(section_name="ERD Section", hole_size=8.5, depth_from=5000, depth_to=40000,
                mud_type="OBM - Low Toxicity (ERD Optimized)", mud_weight_in=9.5, mud_weight_out=10.5,
                plastic_viscosity=15, yield_point=8, oil_water_ratio="80/20",
                electrical_stability=1200, total_volume_required=5000,
                key_additives="Low-friction OBM formulation for ERD torque reduction. "
                              "Anti-settling agents for long horizontal sections.",
                remarks="Friction reduction critical. Monitor ECD throughout 40,000 ft."),
        ]
        p.directional_plan = DirectionalPlan(
            kickoff_point_md=2000, build_rate=2.5, hold_inclination=82,
            target_inclination=82, target_azimuth=90, max_dls=4.0,
            horizontal_displacement=38000,
            remarks="ERD: Departure ratio 38000/6200 = 6.1:1 (world class). "
                    "T&D analysis critical. Real-time torque monitoring required.")
        p.bop_stack = BOPStack(working_pressure=10000, bore_size=21.25,
            bop_type="Quad Ram", shear_ram=True,
            bop_test_pressure_low=250, bop_test_pressure_high=7000)
        p.well_control = WellControlData(maasp_surface=2500, kill_method="Driller's Method",
            kick_tolerance=80, slow_pump_rate_1=30, slow_pump_pressure_1=1800,
            remarks="ERD: Pressure management critical. Monitor ECD vs FG at all times.")
        p.rig_spec = RigSpecification(rig_name="Yastreb Custom ERD", rig_type="Land Rig",
            max_hook_load=1500000, max_rotary_torque=100000, top_drive=True,
            mud_pump_1_hp=2200, mud_pump_2_hp=2200, mud_pump_3_hp=2200,
            pit_volume_total=4000, accommodation=150,
            remarks="Custom 3000 HP rig designed for ERD operations. "
                    "High-torque top drive (100,000 ft-lbs). "
                    "3x 2200 HP pumps for high flow ERD.")
        p.time_estimates = [
            TimeEstimate(section_name="Total", operation="World-Class ERD Well",
                total_section_days=220, cumulative_days=220,
                remarks="Based on Sakhalin Chayvo field experience"),
        ]
        return p

    def _preset_geothermal(self):
        """Geothermal Well"""
        from main import (WellProject, CompanyInfo, WellGeneralInfo,
            FormationTop, CasingDesign, BHADesign, MudProgram,
            DirectionalPlan, BOPStack, WellControlData, RigSpecification, TimeEstimate)
        p = WellProject()
        p.company_info = CompanyInfo(operator_name="ICELAND DEEP DRILLING PROJECT (IDDP)",
            field_name="KRAFLA VOLCANIC FIELD", well_name="IDDP-3",
            rig_name="National Drilling Rig-01 (Custom HT)",
            rig_type="Land Rig", country="ICELAND", region="Northeast Iceland")
        p.well_info = WellGeneralInfo(well_type="Exploration", well_profile="Vertical",
            total_depth_md=9800, total_depth_tvd=9800,
            target_formation="Supercritical Geothermal Reservoir",
            expected_reservoir_pressure=4500, expected_reservoir_temperature=800,
            nace_required=False)
        p.formation_tops = [
            FormationTop(name="Lava Flows (Recent)", formation_type="Basalt",
                md_top=0, md_bottom=600, pore_pressure_top=8.55, pore_pressure_bottom=8.6,
                fracture_gradient_top=14.0, fracture_gradient_bottom=15.0,
                temperature_top=50, temperature_bottom=100, drillability="Hard"),
            FormationTop(name="Hyaloclastite", formation_type="Basalt",
                md_top=600, md_bottom=2000, pore_pressure_top=8.6, pore_pressure_bottom=9.0,
                fracture_gradient_top=15.0, fracture_gradient_bottom=16.0,
                temperature_top=100, temperature_bottom=200, drillability="Medium-Hard"),
            FormationTop(name="Intrusive Basalt", formation_type="Basalt",
                md_top=2000, md_bottom=5000, pore_pressure_top=9.0, pore_pressure_bottom=10.0,
                fracture_gradient_top=16.0, fracture_gradient_bottom=17.0,
                temperature_top=200, temperature_bottom=400, drillability="Very Hard",
                remarks="High temperature zone begins - Air drilling consideration"),
            FormationTop(name="Supercritical Zone", formation_type="Granite",
                md_top=5000, md_bottom=9800, pore_pressure_top=10.0, pore_pressure_bottom=12.0,
                fracture_gradient_top=17.0, fracture_gradient_bottom=18.0,
                temperature_top=400, temperature_bottom=800, drillability="Very Hard",
                remarks="🎯 TARGET - Supercritical geothermal fluids > 400°C"),
        ]
        p.casing_design = [
            CasingDesign(section_name="Surface", hole_size=26, casing_od=20,
                casing_grade="K-55", setting_depth_md=800, top_of_cement_md=0),
            CasingDesign(section_name="Anchor", hole_size=17.5, casing_od=13.375,
                casing_grade="L-80", casing_connection="BTC",
                setting_depth_md=2500, top_of_cement_md=0,
                remarks="Thermal expansion allowance required"),
            CasingDesign(section_name="Production", hole_size=12.25, casing_od=9.625,
                casing_grade="T-95 (HT Alloy)", casing_connection="Hunting Seal",
                setting_depth_md=5000, top_of_cement_md=2000,
                remarks="HT alloy for >400°C. Special cement for geothermal."),
        ]
        p.bha_designs = [
            BHADesign(section_name="Surface-Anchor", bha_number=1, hole_size=17.5,
                bha_type="Rotary + Cooling System", bit_type="Tricone Insert", bit_size=17.5,
                recommended_wob="20-40 klbs", recommended_rpm="60-100",
                remarks="Water cooling of BHA required above 200°C"),
            BHADesign(section_name="Production-Geothermal", bha_number=2, hole_size=12.25,
                bha_type="Rotary (Air/Mist Drilling)", bit_type="Diamond Impreg", bit_size=12.25,
                recommended_wob="5-15 klbs", recommended_rpm="40-80",
                recommended_flow_rate="Air/Mist system",
                remarks="Air/mist drilling for >400°C zone. No MWD - too hot. "
                        "Impregnated diamond bits for hard basalt/granite."),
        ]
        p.mud_programs = [
            MudProgram(section_name="Surface", hole_size=26, depth_from=0, depth_to=2000,
                mud_type="WBM - Fresh Water Gel", mud_weight_in=8.7, mud_weight_out=9.0,
                plastic_viscosity=12, yield_point=8, total_volume_required=800),
            MudProgram(section_name="Production", hole_size=12.25, depth_from=2000, depth_to=5000,
                mud_type="WBM - High Temperature Polymer Mud", mud_weight_in=9.0, mud_weight_out=10.0,
                plastic_viscosity=15, yield_point=10, total_volume_required=1500,
                key_additives="HT polymer, HT fluid loss control, Temperature stabilizer",
                remarks="Transition to air/mist below 200°C BHT"),
            MudProgram(section_name="Geothermal Zone", hole_size=12.25, depth_from=5000, depth_to=9800,
                mud_type="Air / Mist / Aerated Water", mud_weight_in=0, mud_weight_out=0,
                total_volume_required=0,
                remarks="Air drilling for supercritical zone. "
                        "Mud to air conversion at ~5000 ft when BHT > 400°C. "
                        "Aerated water for returns cooling. "
                        "No standard mud properties applicable."),
        ]
        p.directional_plan = DirectionalPlan(survey_tool="Gyro (no MWD in HT zone)",
            survey_frequency=200, max_dls=2.0,
            remarks="Vertical well. Gyro surveys only - MWD not rated for >200°C. "
                    "Wellbore stability critical in fractured volcanic rock.")
        p.bop_stack = BOPStack(bop_type="Double Ram", working_pressure=5000, bore_size=18.75,
            manufacturer="Cameron", shear_ram=True, bop_test_pressure_low=200,
            bop_test_pressure_high=3500,
            remarks="HT rated BOP with thermal protection. Steam handling capability.")
        p.well_control = WellControlData(maasp_surface=1500, kill_method="Driller's Method",
            kick_tolerance=20, slow_pump_rate_1=30, slow_pump_pressure_1=500,
            remarks="Geothermal: steam eruption risk, not gas kick. "
                    "Loss of returns common in fractured rock.")
        p.rig_spec = RigSpecification(rig_name="National Drilling Rig-01 HT Custom",
            rig_type="Land Rig", max_hook_load=500000, top_drive=True,
            mud_pump_1_hp=1000, pit_volume_total=600, accommodation=40,
            remarks="Custom rig for geothermal. Air compressors for air drilling. "
                    "Steam separator. High temperature BOP and wellhead.")
        p.time_estimates = [
            TimeEstimate(section_name="Surface", operation="Drill 26\" & Set 20\"", depth_to=800, total_section_days=4, cumulative_days=4),
            TimeEstimate(section_name="Anchor", operation="Drill 17-1/2\" & Set 13-3/8\"", depth_to=2500, total_section_days=10, cumulative_days=14),
            TimeEstimate(section_name="Production", operation="Drill 12-1/4\" & Set 9-5/8\" (HT)", depth_to=5000, total_section_days=20, cumulative_days=34),
            TimeEstimate(section_name="Geothermal", operation="Air Drill Supercritical Zone 5000-9800 ft", depth_from=5000, depth_to=9800, total_section_days=45, cumulative_days=79,
                remarks="Slow drilling in hard granite. Air/mist system. Multiple bit runs."),
            TimeEstimate(section_name="Testing", operation="Geothermal Well Testing & Logging", total_section_days=11, cumulative_days=90),
        ]
        return p


# ============================================================
# LOAD INTO GUI
# ============================================================

def load_project_into_gui(main_window, project):
    """بارگذاری پروژه در تمام تب‌های GUI"""
    from PySide6.QtWidgets import QMessageBox, QDoubleSpinBox, QSpinBox
    from PySide6.QtCore import QDate

    ci = project.company_info
    wi = project.well_info

    def _set(widget, value):
        if widget is None or value is None:
            return
        try:
            if hasattr(widget, 'setText'):
                widget.setText(str(value))
            elif hasattr(widget, 'setPlainText'):
                widget.setPlainText(str(value))
        except Exception:
            pass

    def _spin(widget, value):
        if widget is None:
            return
        try:
            widget.setValue(float(value) if value else 0)
        except Exception:
            pass

    def _combo(widget, value):
        if widget is None or not value:
            return
        try:
            idx = widget.findText(str(value))
            if idx >= 0:
                widget.setCurrentIndex(idx)
        except Exception:
            pass

    def _check(widget, value):
        if widget is None:
            return
        try:
            widget.setChecked(bool(value))
        except Exception:
            pass

    try:
        # Tab 1: Company & Well
        f = main_window.tab_company.fields
        _set(f.get('operator_name'), ci.operator_name)
        _set(f.get('contractor_name'), ci.contractor_name)
        _set(f.get('field_name'), ci.field_name)
        _set(f.get('well_name'), ci.well_name)
        _set(f.get('well_number'), ci.well_number)
        _set(f.get('pad_name'), ci.pad_name)
        _set(f.get('rig_name'), ci.rig_name)
        _combo(f.get('rig_type'), ci.rig_type)
        _set(f.get('country'), ci.country)
        _set(f.get('region'), ci.region)
        _set(f.get('block_license'), ci.block_license)
        _set(f.get('api_number'), ci.api_number)
        _set(f.get('document_number'), ci.document_number)
        _set(f.get('revision'), ci.revision)
        _combo(f.get('classification'), ci.classification)
        _set(f.get('prepared_by'), ci.prepared_by)
        _set(f.get('reviewed_by'), ci.reviewed_by)
        _set(f.get('approved_by'), ci.approved_by)

        _combo(f.get('well_type'), wi.well_type)
        _combo(f.get('well_profile'), wi.well_profile)
        _spin(f.get('total_depth_md'), wi.total_depth_md)
        _spin(f.get('total_depth_tvd'), wi.total_depth_tvd)
        _spin(f.get('water_depth'), wi.water_depth)
        _spin(f.get('air_gap'), wi.air_gap)
        _spin(f.get('ground_elevation'), wi.ground_elevation)
        _spin(f.get('kb_elevation'), wi.kb_elevation)
        _set(f.get('surface_latitude'), wi.surface_latitude)
        _set(f.get('surface_longitude'), wi.surface_longitude)
        _spin(f.get('magnetic_declination'), wi.magnetic_declination)
        _spin(f.get('grid_convergence'), wi.grid_convergence)
        _set(f.get('target_formation'), wi.target_formation)
        _set(f.get('target_zone'), wi.target_zone)
        _spin(f.get('expected_reservoir_pressure'), wi.expected_reservoir_pressure)
        _spin(f.get('expected_reservoir_temperature'), wi.expected_reservoir_temperature)
        _spin(f.get('expected_h2s'), wi.expected_h2s_concentration)
        _spin(f.get('expected_co2'), wi.expected_co2_concentration)
        _check(f.get('nace_required'), wi.nace_required)

        # Tab 2: Formations
        if project.formation_tops:
            data = []
            for ft in project.formation_tops:
                data.append([ft.name, ft.formation_type,
                    str(ft.md_top), str(ft.md_bottom),
                    str(ft.tvd_top), str(ft.tvd_bottom),
                    str(ft.pore_pressure_top), str(ft.pore_pressure_bottom),
                    str(ft.fracture_gradient_top), str(ft.fracture_gradient_bottom),
                    str(ft.overburden_gradient),
                    str(ft.temperature_top), str(ft.temperature_bottom),
                    ft.drillability, ft.directional_tendency, ft.remarks])
            main_window.tab_formation.formation_table.set_data(data)

        # Hazards
        if project.hazards:
            data = []
            for h in project.hazards:
                data.append([h.hazard_type, str(h.md_top), str(h.md_bottom),
                    h.severity, h.probability, h.description,
                    h.mitigation, h.contingency, h.reference_well])
            main_window.tab_formation.hazard_table.set_data(data)

        # Tab 3: Casing
        if project.casing_design:
            data = []
            for cd in project.casing_design:
                data.append([cd.section_name, cd.section_type, str(cd.hole_size),
                    str(cd.casing_od), str(cd.casing_id), str(cd.casing_weight),
                    cd.casing_grade, cd.casing_connection,
                    str(cd.setting_depth_md), str(cd.setting_depth_tvd),
                    str(cd.top_of_cement_md), str(cd.burst_rating),
                    str(cd.collapse_rating), str(cd.tensile_rating), str(cd.drift_id),
                    str(cd.min_design_factor_burst), str(cd.min_design_factor_collapse),
                    str(cd.min_design_factor_tension), cd.centralizer_type,
                    str(cd.centralizer_spacing), str(cd.float_collar_depth),
                    "Yes" if cd.is_liner else "No", str(cd.liner_overlap), cd.remarks])
            main_window.tab_casing.casing_table.set_data(data)

        # Tab 4: Mud
        if project.mud_programs:
            data = []
            for mp in project.mud_programs:
                data.append([mp.section_name, str(mp.hole_size),
                    str(mp.depth_from), str(mp.depth_to), mp.mud_type,
                    str(mp.mud_weight_in), str(mp.mud_weight_out),
                    str(mp.funnel_viscosity), str(mp.plastic_viscosity),
                    str(mp.yield_point), str(mp.gel_strength_10s),
                    str(mp.gel_strength_10m), str(mp.gel_strength_30m),
                    str(mp.fluid_loss), str(mp.hthp_fluid_loss),
                    str(mp.ph) if mp.ph > 0 else "-",
                    str(mp.chlorides) if mp.chlorides > 0 else "-",
                    str(mp.mbt) if mp.mbt > 0 else "-",
                    str(mp.sand_content), mp.oil_water_ratio or "-",
                    str(mp.electrical_stability) if mp.electrical_stability > 0 else "-",
                    str(mp.total_volume_required), str(mp.active_volume),
                    (mp.key_additives or "")[:100],
                    str(mp.ecd_at_shoe), str(mp.ecd_at_td),
                    (mp.remarks or "")[:80]])
            main_window.tab_mud.mud_table.set_data(data)

        # Tab 5: BHA
        if project.bha_designs:
            data = []
            for b in project.bha_designs:
                data.append([b.section_name, str(b.bha_number), str(b.hole_size),
                    b.bha_type, b.bit_type, str(b.bit_size),
                    b.bit_manufacturer, b.bit_model, b.bit_nozzles,
                    b.motor_type or "-", str(b.motor_od) if b.motor_od else "-",
                    str(b.motor_bend) if b.motor_bend else "-",
                    b.rss_type or "-", b.mwd_type or "-",
                    b.lwd_sensors or "-", b.recommended_wob,
                    b.recommended_rpm, b.recommended_flow_rate,
                    b.recommended_torque or "", (b.remarks or "")[:80]])
            main_window.tab_bha.bha_summary_table.set_data(data)

        # Tab 5: Drilling Parameters
        if project.drilling_parameters:
            data = []
            for dp in project.drilling_parameters:
                data.append([dp.section_name, str(dp.hole_size),
                    str(dp.depth_from), str(dp.depth_to),
                    str(dp.wob_min), str(dp.wob_max),
                    str(dp.rpm_min), str(dp.rpm_max),
                    str(dp.flow_rate_min), str(dp.flow_rate_max),
                    str(dp.torque_max), str(dp.rop_min),
                    str(dp.rop_max), str(dp.rop_average),
                    str(dp.spp_max), str(dp.overpull_limit),
                    str(dp.pickup_weight), str(dp.slackoff_weight),
                    str(dp.rotating_weight), str(dp.max_ecd),
                    str(dp.max_trip_speed_in), str(dp.max_trip_speed_out),
                    dp.remarks or ""])
            main_window.tab_bha.params_table.set_data(data)

        # Tab 6: Cement
        if project.cement_design:
            data = []
            for c in project.cement_design:
                data.append([c.section_name, str(c.casing_od), str(c.hole_size),
                    str(c.shoe_depth_md), str(c.toc_md),
                    c.lead_slurry_type, str(c.lead_slurry_density),
                    str(c.lead_slurry_yield), str(c.lead_slurry_volume),
                    str(c.lead_slurry_thickening_time), str(c.lead_slurry_compressive_strength),
                    c.tail_slurry_type, str(c.tail_slurry_density),
                    str(c.tail_slurry_yield), str(c.tail_slurry_volume),
                    str(c.tail_slurry_thickening_time), str(c.tail_slurry_compressive_strength),
                    c.spacer_type or "", str(c.spacer_density), str(c.spacer_volume),
                    c.wash_type or "", str(c.wash_volume),
                    str(c.displacement_volume), str(c.displacement_rate),
                    str(c.max_ecd), str(c.excess_percentage),
                    str(c.woc_time), str(c.plug_bump_pressure),
                    "Yes" if c.stage_cementing else "No",
                    "Yes" if c.cbl_cbil_required else "No",
                    (c.cement_additives or "")[:80], (c.remarks or "")[:80]])
            main_window.tab_cement.cement_table.set_data(data)

        # Tab 7: Directional
        dp = project.directional_plan
        df = main_window.tab_directional.fields
        _combo(df.get('survey_tool'), dp.survey_tool)
        _spin(df.get('survey_frequency'), dp.survey_frequency)
        _spin(df.get('kop_md'), dp.kickoff_point_md)
        _spin(df.get('kop_tvd'), dp.kickoff_point_tvd)
        _spin(df.get('build_rate'), dp.build_rate)
        _spin(df.get('turn_rate'), dp.turn_rate)
        _spin(df.get('hold_inclination'), dp.hold_inclination)
        _spin(df.get('hold_azimuth'), dp.hold_azimuth)
        _spin(df.get('target_inclination'), dp.target_inclination)
        _spin(df.get('target_azimuth'), dp.target_azimuth)
        _spin(df.get('max_dls'), dp.max_dls)
        _spin(df.get('horizontal_displacement'), dp.horizontal_displacement)
        _spin(df.get('vertical_section'), dp.vertical_section)

        if dp.wellpath_data:
            data = []
            for wp in dp.wellpath_data:
                data.append([str(wp.get('md','')), str(wp.get('tvd','')),
                    str(wp.get('inclination','')), str(wp.get('azimuth','')),
                    str(wp.get('dls','')), str(wp.get('ns','')),
                    str(wp.get('ew','')), str(wp.get('vs','')),
                    str(wp.get('closure_dist','')), str(wp.get('closure_dir','')),
                    str(wp.get('build_turn','')), str(wp.get('remarks',''))])
            main_window.tab_directional.wellpath_table.set_data(data)

        # Tab 8: BOP
        bop = project.bop_stack
        wc = project.well_control
        bf = main_window.tab_bop.fields
        _combo(bf.get('bop_type'), bop.bop_type)
        _spin(bf.get('bop_wp'), bop.working_pressure)
        _spin(bf.get('bop_bore'), bop.bore_size)
        _set(bf.get('bop_manufacturer'), bop.manufacturer)
        _set(bf.get('bop_model'), bop.model)
        _spin(bf.get('annular_size'), bop.annular_preventer_size)
        _spin(bf.get('annular_wp'), bop.annular_preventer_wp)
        _set(bf.get('pipe_ram_size'), bop.pipe_ram_size)
        _check(bf.get('blind_ram'), bop.blind_ram)
        _check(bf.get('shear_ram'), bop.shear_ram)
        _check(bf.get('vbr'), bop.variable_bore_ram)
        _spin(bf.get('kill_line'), bop.kill_line_size)
        _spin(bf.get('choke_line'), bop.choke_line_size)
        _spin(bf.get('choke_manifold_wp'), bop.choke_manifold_wp)
        _spin(bf.get('accumulator_capacity'), bop.accumulator_capacity)
        _spin(bf.get('accumulator_precharge'), bop.accumulator_precharge)
        _spin(bf.get('low_test_pressure'), bop.bop_test_pressure_low)
        _spin(bf.get('high_test_pressure'), bop.bop_test_pressure_high)
        _combo(bf.get('kill_method'), wc.kill_method)
        _spin(bf.get('maasp'), wc.maasp_surface)
        _spin(bf.get('kick_tolerance'), wc.kick_tolerance)
        _spin(bf.get('pit_gain_alarm'), wc.pit_gain_action_level)
        _spin(bf.get('slow_pump_1_spm'), wc.slow_pump_rate_1)
        _spin(bf.get('slow_pump_1_psi'), wc.slow_pump_pressure_1)
        _spin(bf.get('slow_pump_2_spm'), wc.slow_pump_rate_2)
        _spin(bf.get('slow_pump_2_psi'), wc.slow_pump_pressure_2)

        # Tab 9: Rig
        rs = project.rig_spec
        rf = main_window.tab_rig.fields
        _set(rf.get('rig_name'), rs.rig_name)
        _combo(rf.get('rig_type'), rs.rig_type)
        _set(rf.get('rig_contractor'), rs.rig_contractor)
        _spin(rf.get('max_hook_load'), rs.max_hook_load)
        _spin(rf.get('drawworks_hp'), rs.drawworks_power)
        _check(rf.get('top_drive'), rs.top_drive)
        _set(rf.get('top_drive_model'), rs.top_drive_model)
        _spin(rf.get('top_drive_torque'), rs.top_drive_torque)
        _spin(rf.get('max_rpm'), rs.max_rotary_speed)
        _spin(rf.get('derrick_height'), rs.derrick_height)
        _spin(rf.get('rotary_table'), rs.rotary_table_size)
        _set(rf.get('pump1_type'), rs.mud_pump_1_type)
        _spin(rf.get('pump1_hp'), rs.mud_pump_1_hp)
        _spin(rf.get('pump1_liner'), rs.mud_pump_1_liner)
        _spin(rf.get('pump1_max_pressure'), rs.mud_pump_1_max_pressure)
        _spin(rf.get('pump1_max_flow'), rs.mud_pump_1_max_flow)
        _set(rf.get('pump2_type'), rs.mud_pump_2_type)
        _spin(rf.get('pump2_hp'), rs.mud_pump_2_hp)
        _spin(rf.get('pump2_liner'), rs.mud_pump_2_liner)
        _spin(rf.get('pump2_max_pressure'), rs.mud_pump_2_max_pressure)
        _spin(rf.get('pump2_max_flow'), rs.mud_pump_2_max_flow)
        _set(rf.get('pump3_type'), rs.mud_pump_3_type)
        _spin(rf.get('pump3_hp'), rs.mud_pump_3_hp)
        _spin(rf.get('pit_total'), rs.pit_volume_total)
        _spin(rf.get('pit_active'), rs.pit_volume_active)
        _spin(rf.get('shakers'), rs.shale_shaker_count)
        _set(rf.get('degasser'), rs.degasser_type)
        _set(rf.get('centrifuge_detail'), rs.centrifuge)
        _set(rf.get('generators'), rs.generators)
        _spin(rf.get('total_power'), rs.total_power)
        _spin(rf.get('crane'), rs.crane_capacity)
        _spin(rf.get('accommodation'), rs.accommodation)

        # Tab 10: Time
        if project.time_estimates:
            data = []
            for te in project.time_estimates:
                row = [te.section_name, te.operation,
                       str(te.depth_from) if te.depth_from > 0 else "-",
                       str(te.depth_to) if te.depth_to > 0 else "-",
                       str(te.rop_average) if te.rop_average > 0 else "-",
                       "", "", "", "", "", "", "", "",
                       "", "", "",
                       str(te.total_section_days),
                       str(te.cumulative_days),
                       (te.remarks or "")[:80]]
                data.append(row)
            main_window.tab_time.time_table.set_data(data)

        # Success
        total_days = project.time_estimates[-1].cumulative_days if project.time_estimates else 0

        QMessageBox.information(
            main_window, "✅ Template Loaded Successfully",
            f"Well template loaded successfully!\n\n"
            f"🛢️  Well: {ci.well_name}\n"
            f"🏜️  Field: {ci.field_name}\n"
            f"🏢  Operator: {ci.operator_name}\n"
            f"📏  TD: {wi.total_depth_md:,.0f} ft MD / {wi.total_depth_tvd:,.0f} ft TVD\n"
            f"🎯  Target: {wi.target_formation}\n"
            f"⏱️  Est. Duration: {total_days:.0f} days\n\n"
            f"📊  Loaded:\n"
            f"   • {len(project.formation_tops)} Formation Tops\n"
            f"   • {len(project.casing_design)} Casing Strings\n"
            f"   • {len(project.mud_programs)} Mud Systems\n"
            f"   • {len(project.bha_designs)} BHA Designs\n"
            f"   • {len(project.cement_design)} Cement Jobs\n"
            f"   • {len(project.hazards)} Hazard Entries\n\n"
            f"✏️  Review and edit any values, then click Generate!"
        )

        main_window.statusBar().showMessage(
            f"✅ Loaded: {ci.well_name} | {wi.total_depth_md:,.0f} ft MD | "
            f"{total_days:.0f} days | Ready to Generate"
        )

    except Exception as e:
        import traceback
        QMessageBox.warning(
            main_window, "Template Loaded (with warnings)",
            f"Template loaded with some issues:\n\n{str(e)}\n\n"
            f"Some fields may need manual entry.\n"
            f"Check all tabs before generating."
        )