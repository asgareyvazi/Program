# ============================================================================
# DRILLING PROGRAM & PROCEDURE GENERATOR - PROFESSIONAL EDITION
# Version 3.1 (Integrated Edition)
# File: launcher.py
# Final Integration, Config Manager, Setup & Launch
# ============================================================================

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# CONFIG DATA CLASSES
# ============================================================================

@dataclass
class AppConfig:
    name: str = "Drilling Program Generator Pro"
    version: str = "3.1"
    language: str = "en"
    theme: str = "dark"
    auto_save: bool = True
    auto_save_interval: int = 300
    recent_files_max: int = 10
    recent_files: List[str] = field(default_factory=list)


@dataclass
class DocumentConfig:
    paper_size: str = "A4"
    default_format: str = "standard"
    font_family: str = "Calibri"
    font_size: int = 10
    include_appendices: bool = True
    include_kill_sheet: bool = True
    include_ddr_template: bool = True
    include_trip_sheet: bool = True
    include_tally_sheet: bool = True
    include_bit_record: bool = True
    include_survey_sheet: bool = True
    include_cement_report: bool = True
    include_cost_estimate: bool = True


@dataclass
class UnitsConfig:
    depth: str = "ft"
    pressure: str = "psi"
    mud_weight: str = "ppg"
    temperature: str = "F"
    flow_rate: str = "GPM"
    volume: str = "bbl"


@dataclass
class DesignFactorsConfig:
    burst_min: float = 1.10
    collapse_min: float = 1.10
    tension_min: float = 1.60
    triaxial_min: float = 1.25


@dataclass
class FullConfig:
    app: AppConfig = field(default_factory=AppConfig)
    document: DocumentConfig = field(default_factory=DocumentConfig)
    units: UnitsConfig = field(default_factory=UnitsConfig)
    design_factors: DesignFactorsConfig = field(default_factory=DesignFactorsConfig)


# ============================================================================
# CONFIG MANAGER (Singleton)
# ============================================================================

class ConfigManager:
    _instance = None
    _config_path = "config/settings.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
            cls._instance._loaded = False
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None

    @property
    def config(self) -> FullConfig:
        if not self._loaded:
            self._config = self._load()
            self._loaded = True
        return self._config

    def _load(self) -> FullConfig:
        path = Path(self._config_path)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return self._from_dict(data)
            except Exception as e:
                logger.warning(f"Config load failed: {e}")
        return FullConfig()

    def _from_dict(self, data: Dict) -> FullConfig:
        cfg = FullConfig()
        try:
            for section_name in ('app', 'document', 'units', 'design_factors'):
                section_data = data.get(section_name, {})
                section_obj = getattr(cfg, section_name)
                for k, v in section_data.items():
                    if hasattr(section_obj, k):
                        setattr(section_obj, k, v)
        except Exception as e:
            logger.warning(f"Config parse error: {e}")
        return cfg

    def save(self) -> bool:
        try:
            path = Path(self._config_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                'app': asdict(self.config.app),
                'document': asdict(self.config.document),
                'units': asdict(self.config.units),
                'design_factors': asdict(self.config.design_factors),
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Config save failed: {e}")
            return False

    def add_recent_file(self, path: str):
        recent = self.config.app.recent_files
        if path in recent:
            recent.remove(path)
        recent.insert(0, path)
        self.config.app.recent_files = recent[:self.config.app.recent_files_max]
        self.save()

    def initialize(self):
        dirs = [
            "projects", "projects/exports",
            "projects/templates", "projects/backup",
            "logs", "config", "temp"
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        self.save()


# ============================================================================
# DEPENDENCY MANAGER
# ============================================================================

class DependencyManager:
    REQUIRED = {'PySide6': 'PySide6', 'docx': 'python-docx'}
    OPTIONAL = {'openpyxl': 'openpyxl', 'matplotlib': 'matplotlib'}

    @classmethod
    def check(cls) -> dict:
        results = {'required': {}, 'optional': {}, 'all_met': True}
        for module, pkg in cls.REQUIRED.items():
            try:
                __import__(module)
                results['required'][pkg] = True
            except ImportError:
                results['required'][pkg] = False
                results['all_met'] = False
        for module, pkg in cls.OPTIONAL.items():
            try:
                __import__(module)
                results['optional'][pkg] = True
            except ImportError:
                results['optional'][pkg] = False
        return results

    @classmethod
    def install(cls, include_optional=False):
        packages = list(cls.REQUIRED.values())
        if include_optional:
            packages += list(cls.OPTIONAL.values())
        for pkg in packages:
            print(f"Installing {pkg}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip",
                    "install", pkg, "--quiet"])
                print(f"  {pkg}: OK")
            except subprocess.CalledProcessError:
                print(f"  {pkg}: FAILED")

    @classmethod
    def print_status(cls) -> bool:
        results = cls.check()
        print("\n" + "=" * 50)
        print("  DEPENDENCY STATUS")
        print("=" * 50)
        print("\n  Required:")
        for pkg, ok in results['required'].items():
            icon = "OK" if ok else "MISSING"
            print(f"    [{icon}] {pkg}")
        print("\n  Optional:")
        for pkg, ok in results['optional'].items():
            icon = "OK" if ok else "SKIP"
            print(f"    [{icon}] {pkg}")
        if results['all_met']:
            print("\n  All required dependencies met!")
        else:
            print("\n  Run: python launcher.py --install")
        print("=" * 50)
        return results['all_met']


# ============================================================================
# SAMPLE PROJECT
# ============================================================================

def create_sample_project():
    """Quick sample project for testing"""
    from main import (
        WellProject, CompanyInfo, WellGeneralInfo,
        FormationTop, HazardEntry, CasingDesign,
        CementDesign, BHADesign, MudProgram,
        DirectionalPlan, BOPStack, WellControlData,
        RigSpecification, DrillingParameters, TimeEstimate
    )

    p = WellProject()
    p.company_info = CompanyInfo(
        operator_name="Sample Oil Company",
        contractor_name="Sample Drilling Co.",
        field_name="Sample Field",
        well_name="SMP-001",
        rig_name="Sample Rig 1",
        rig_type="Land Rig",
        country="Sample Country",
        spud_date=datetime.now().strftime("%Y-%m-%d"),
        prepared_by="Sample Engineer",
        revision="0",
        document_number="SMP-DRL-001",
        classification="Confidential")

    p.well_info = WellGeneralInfo(
        well_type="Development",
        well_profile="Directional J-Type",
        total_depth_md=10000,
        total_depth_tvd=9000,
        kb_elevation=25.0,
        target_formation="Target Formation",
        expected_reservoir_pressure=4500,
        expected_reservoir_temperature=220)

    p.formation_tops = [
        FormationTop(name="Surface Fm", formation_type="Sand",
            md_top=0, md_bottom=1000, tvd_top=0, tvd_bottom=1000,
            pore_pressure_top=8.6, pore_pressure_bottom=8.7,
            fracture_gradient_top=14.0, fracture_gradient_bottom=14.5,
            temperature_top=80, temperature_bottom=120,
            drillability="Easy"),
        FormationTop(name="Intermediate Fm", formation_type="Limestone",
            md_top=1000, md_bottom=7000, tvd_top=1000, tvd_bottom=6500,
            pore_pressure_top=8.8, pore_pressure_bottom=9.5,
            fracture_gradient_top=14.5, fracture_gradient_bottom=16.0,
            temperature_top=120, temperature_bottom=200,
            drillability="Medium"),
        FormationTop(name="Reservoir", formation_type="Dolomite",
            md_top=7000, md_bottom=10000, tvd_top=6500, tvd_bottom=9000,
            pore_pressure_top=9.5, pore_pressure_bottom=10.2,
            fracture_gradient_top=16.0, fracture_gradient_bottom=17.0,
            temperature_top=200, temperature_bottom=225,
            drillability="Hard"),
    ]

    p.casing_design = [
        CasingDesign(section_name="Surface", section_type="Surface",
            hole_size=26, casing_od=20, casing_id=18.73, casing_weight=133,
            casing_grade="K-55", casing_connection="BTC",
            setting_depth_md=1000, setting_depth_tvd=1000,
            top_of_cement_md=0, cement_to_surface=True,
            burst_rating=3060, collapse_rating=1490,
            drift_id=18.63, centralizer_type="Bow-Spring",
            centralizer_spacing=60, float_collar_depth=950),
        CasingDesign(section_name="Intermediate", section_type="Intermediate",
            hole_size=17.5, casing_od=13.375, casing_id=12.415, casing_weight=72,
            casing_grade="N-80", casing_connection="BTC",
            setting_depth_md=7000, setting_depth_tvd=6500,
            top_of_cement_md=4000,
            burst_rating=5020, collapse_rating=2670,
            drift_id=12.259, centralizer_spacing=60, float_collar_depth=6940),
        CasingDesign(section_name="Production", section_type="Production",
            hole_size=12.25, casing_od=9.625, casing_id=8.535, casing_weight=53.5,
            casing_grade="L-80", casing_connection="VAM TOP",
            setting_depth_md=10000, setting_depth_tvd=9000,
            top_of_cement_md=6000,
            burst_rating=7930, collapse_rating=4750,
            drift_id=8.379, centralizer_spacing=40, float_collar_depth=9940),
    ]

    p.cement_design = [
        CementDesign(section_name="Surface", casing_od=20, hole_size=26,
            shoe_depth_md=1000, toc_md=0, lead_slurry_density=12.8,
            lead_slurry_volume=300, tail_slurry_density=15.8,
            tail_slurry_volume=100, spacer_volume=30,
            displacement_volume=200, displacement_rate=8,
            excess_percentage=100, woc_time=12, plug_bump_pressure=500,
            cbl_cbil_required=True),
        CementDesign(section_name="Production", casing_od=9.625, hole_size=12.25,
            shoe_depth_md=10000, toc_md=6000, lead_slurry_density=12.0,
            lead_slurry_volume=350, tail_slurry_density=16.0,
            tail_slurry_volume=150, spacer_volume=35,
            displacement_volume=400, displacement_rate=5,
            excess_percentage=50, woc_time=24, plug_bump_pressure=1000,
            cbl_cbil_required=True),
    ]

    p.bha_designs = [
        BHADesign(section_name="Surface", bha_number=1, hole_size=26,
            bha_type="Rotary", bit_type="Tricone Insert", bit_size=26,
            bit_manufacturer="Sample Bits", bit_model="Model-X",
            bit_nozzles="3x22", mwd_type="Gyro MWD",
            recommended_wob="15-30 klbs", recommended_rpm="80-120",
            recommended_flow_rate="800-1000 GPM"),
        BHADesign(section_name="Intermediate", bha_number=1, hole_size=17.5,
            bha_type="Motor + MWD/LWD", bit_type="PDC", bit_size=17.5,
            bit_manufacturer="Sample Bits", bit_model="PDC-Model",
            bit_nozzles="5x16", motor_type="9-5/8 PDM",
            motor_od=9.625, motor_bend=1.5, mwd_type="MWD Tool",
            lwd_sensors="GR, RES, DEN, NEU",
            recommended_wob="15-35 klbs", recommended_rpm="100-160",
            recommended_flow_rate="700-850 GPM"),
        BHADesign(section_name="Production", bha_number=1, hole_size=12.25,
            bha_type="RSS + MWD/LWD", bit_type="PDC", bit_size=12.25,
            bit_manufacturer="Sample Bits", bit_model="PDC-Pro",
            bit_nozzles="4x13", rss_type="Push-the-bit RSS",
            mwd_type="HT MWD", lwd_sensors="GR, RES, DEN, NEU, PWD",
            recommended_wob="8-25 klbs", recommended_rpm="120-180",
            recommended_flow_rate="550-700 GPM"),
    ]

    p.mud_programs = [
        MudProgram(section_name="Surface", hole_size=26,
            depth_from=0, depth_to=1000, mud_type="WBM - KCl Polymer",
            mud_weight_in=9.0, mud_weight_out=9.5,
            plastic_viscosity=18, yield_point=16,
            total_volume_required=1500, ecd_at_shoe=9.7, ecd_at_td=9.8),
        MudProgram(section_name="Intermediate", hole_size=17.5,
            depth_from=1000, depth_to=7000, mud_type="WBM - KCl Polymer",
            mud_weight_in=9.5, mud_weight_out=12.0,
            plastic_viscosity=22, yield_point=18,
            total_volume_required=2500, ecd_at_shoe=12.3, ecd_at_td=12.5),
        MudProgram(section_name="Production", hole_size=12.25,
            depth_from=7000, depth_to=10000, mud_type="OBM - Mineral Oil",
            mud_weight_in=10.5, mud_weight_out=12.5,
            plastic_viscosity=20, yield_point=12,
            oil_water_ratio="80/20", electrical_stability=800,
            total_volume_required=3000, ecd_at_shoe=13.0, ecd_at_td=13.2),
    ]

    p.directional_plan = DirectionalPlan(
        survey_tool="MWD + Gyro at shoes", survey_frequency=90,
        kickoff_point_md=2500, kickoff_point_tvd=2500,
        build_rate=3.0, hold_inclination=30, hold_azimuth=45,
        target_inclination=30, target_azimuth=45,
        max_dls=5.0, horizontal_displacement=3000)

    p.bop_stack = BOPStack(
        bop_type="Triple Ram", working_pressure=10000,
        bore_size=18.75, manufacturer="Cameron",
        annular_preventer_size=18.75, annular_preventer_wp=10000,
        pipe_ram_size='5", 3-1/2"',
        blind_ram=True, shear_ram=True,
        kill_line_size=3.0, choke_line_size=3.0,
        accumulator_capacity=1600,
        bop_test_pressure_low=250, bop_test_pressure_high=7000)

    p.well_control = WellControlData(
        maasp_surface=2500, kill_method="Wait & Weight",
        kick_tolerance=50,
        slow_pump_rate_1=30, slow_pump_pressure_1=850,
        slow_pump_rate_2=20, slow_pump_pressure_2=620,
        pit_gain_action_level=5)

    p.rig_spec = RigSpecification(
        rig_name="Sample Rig 1", rig_type="Land Rig",
        rig_contractor="Sample Drilling Co.",
        max_hook_load=1000000, drawworks_power=2000,
        top_drive=True, top_drive_model="NOV TDS-11SA",
        top_drive_torque=37500, derrick_height=147,
        rotary_table_size=37.5,
        mud_pump_1_type="NOV 14-P-220", mud_pump_1_hp=1600,
        mud_pump_1_liner=6.5, mud_pump_1_max_pressure=5000,
        mud_pump_1_max_flow=850,
        mud_pump_2_type="NOV 14-P-220", mud_pump_2_hp=1600,
        pit_volume_total=1800, pit_volume_active=1200,
        shale_shaker_count=4, generators="4x CAT 3512B",
        total_power=6000, accommodation=100)

    p.time_estimates = [
        TimeEstimate(section_name="Pre-Spud", operation="Rig Move & Setup",
            total_section_days=3.0, cumulative_days=3.0),
        TimeEstimate(section_name="Surface", operation="Drill 26\" & Set 20\"",
            depth_from=0, depth_to=1000, rop_average=35,
            total_section_days=5.0, cumulative_days=8.0),
        TimeEstimate(section_name="Intermediate", operation="Drill 17-1/2\" & Set 13-3/8\"",
            depth_from=1000, depth_to=7000, rop_average=20,
            total_section_days=15.0, cumulative_days=23.0),
        TimeEstimate(section_name="Production", operation="Drill 12-1/4\" & Set 9-5/8\"",
            depth_from=7000, depth_to=10000, rop_average=12,
            total_section_days=12.0, cumulative_days=35.0),
        TimeEstimate(section_name="Completion", operation="Completion & Testing",
            total_section_days=5.0, cumulative_days=40.0),
    ]

    p.drilling_parameters = [
        DrillingParameters(section_name="Surface", hole_size=26,
            depth_from=0, depth_to=1000, wob_min=15, wob_max=30,
            rpm_min=80, rpm_max=120, flow_rate_min=800, flow_rate_max=1000,
            torque_max=25000, rop_average=35, spp_max=2500,
            overpull_limit=50, max_ecd=14.5),
        DrillingParameters(section_name="Intermediate", hole_size=17.5,
            depth_from=1000, depth_to=7000, wob_min=15, wob_max=35,
            rpm_min=100, rpm_max=160, flow_rate_min=700, flow_rate_max=850,
            torque_max=35000, rop_average=20, spp_max=3500,
            overpull_limit=50, max_ecd=16.0),
        DrillingParameters(section_name="Production", hole_size=12.25,
            depth_from=7000, depth_to=10000, wob_min=8, wob_max=25,
            rpm_min=120, rpm_max=180, flow_rate_min=550, flow_rate_max=700,
            torque_max=28000, rop_average=12, spp_max=4000,
            overpull_limit=40, max_ecd=17.0),
    ]

    return p


# ============================================================================
# AUTO-SAVE HELPER
# ============================================================================

def auto_save_project(window) -> bool:
    """Silent auto-save for main window"""
    try:
        project = window.collect_all_data()
        if not project.company_info.well_name:
            return False
        from drilling_database import DrillingProjectDatabase
        db = DrillingProjectDatabase()
        db.save_project(project, project.company_info.well_name)
        db.close()
        return True
    except Exception:
        return False


# ============================================================================
# GUI LAUNCHER
# ============================================================================

def launch_gui():
    """Launch main GUI application"""
    from PySide6.QtWidgets import QApplication
    from main import DrillingProgramMainWindow, DARK_STYLE

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setStyleSheet(DARK_STYLE)
    app.setApplicationName("Drilling Program Generator Pro")
    app.setApplicationVersion("3.1")

    window = DrillingProgramMainWindow()
    window.show()
    sys.exit(app.exec())


# ============================================================================
# SAMPLE DOCUMENT GENERATOR
# ============================================================================

def generate_sample():
    """Generate sample document without GUI"""
    print("\nGenerating sample document...")

    project = create_sample_project()
    Path("projects/exports").mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"projects/exports/Sample_Program_{ts}.docx"

    try:
        from word_generator import DrillingProgramWordGenerator
        generator = DrillingProgramWordGenerator(project)
        generator.generate(output_file)
        print(f"\nDocument generated: {output_file}")

        # Try adding appendices
        try:
            from advanced_modules import AppendixGenerator
            from docx import Document
            doc = Document(output_file)
            AppendixGenerator(project).generate_all_appendices(doc)
            doc.save(output_file)
            print("Appendices added")
        except ImportError:
            print("Appendices skipped (module not found)")

        size = Path(output_file).stat().st_size / 1024
        print(f"File size: {size:.0f} KB")

        if sys.platform == 'win32':
            os.startfile(output_file)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


# ============================================================================
# CLI
# ============================================================================

def print_banner():
    print("""
+------------------------------------------------------+
|                                                      |
|   DRILLING PROGRAM GENERATOR PRO v3.1               |
|   Professional Drilling Program & Procedure Generator|
|                                                      |
|   Based on API, IADC, Shell DEP, Aramco Standards   |
|                                                      |
+------------------------------------------------------+
    """)


def print_help():
    print("""
Usage:
  python launcher.py             Launch GUI
  python launcher.py --install   Install packages
  python launcher.py --check     Check packages
  python launcher.py --sample    Generate sample document
  python launcher.py --init      Initialize directories
  python launcher.py --help      Show this help

Required packages: PySide6, python-docx
    """)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    arg = sys.argv[1].lower() if len(sys.argv) > 1 else ""

    print_banner()

    # Create directories
    dirs = ["projects", "projects/exports", "projects/templates",
            "projects/backup", "logs", "config", "temp"]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("Directories: ready")

    if arg in ("--help", "-h"):
        print_help()

    elif arg == "--check":
        DependencyManager.print_status()

    elif arg == "--install":
        include_all = "--all" in sys.argv
        DependencyManager.install(include_all)

    elif arg == "--init":
        cfg = ConfigManager()
        cfg.initialize()
        print("Config initialized")

        try:
            from procedures_db import ProcedureDatabase
            db = ProcedureDatabase()
            stats = db.get_stats()
            print(f"Procedures DB: {stats['total_procedures']} procedures")
            db.close()
        except Exception as e:
            print(f"Procedures DB: {e}")

    elif arg == "--sample":
        if not DependencyManager.check()['all_met']:
            print("Run --install first")
            sys.exit(1)
        generate_sample()

    else:
        # Default: launch GUI
        if not DependencyManager.check()['all_met']:
            print("Missing dependencies!")
            print("Run: python launcher.py --install")
            sys.exit(1)

        # Seed procedures if needed
        try:
            from procedures_db import ProcedureDatabase
            db = ProcedureDatabase()
            stats = db.get_stats()
            if stats['total_procedures'] < 5:
                try:
                    from seed_procedures_v2 import seed_all_v2
                    count = seed_all_v2(db)
                    print(f"Seeded {count} procedures")
                except ImportError:
                    pass
            db.close()
        except Exception:
            pass

        launch_gui()